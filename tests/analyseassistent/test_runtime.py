"""Vertrags-, Fehler-, Kontingent- und reale Abfragetests ohne externe KI."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch, MagicMock
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from wsgiref.simple_server import make_server, WSGIRequestHandler

from server.analyseassistent.contracts import verify_plan
from server.analyseassistent.datasets import Datasets
from server.analyseassistent.results import apply_selection
from server.analyseassistent.service import Service
from server.analyseassistent.quota import LocalQuota, QuotaError, month_key
from server.analyseassistent.api import Application
from server.analyseassistent.requesty import Requesty, ModelError
from server.analyseassistent.profiles import modal_rows
from server.analyseassistent.relations import partner_ranking
from scripts.analysis.b01 import literal
import duckdb

ROOT = Path(__file__).resolve().parents[2]
PARAMETERS = {'region': 'DEA12', 'year': 2024, 'mode': 'road', 'metric': 'tonnes'}


def plan(**changes):
    record = {'phase': 'plan', 'function_id': 'balance', 'parameters': PARAMETERS.copy(),
              'parameter_origins': {k: 'context' for k in PARAMETERS}, 'unresolved_fields': [], 'status': 'ready'}
    record.update(changes)
    return record


class Contracts(unittest.TestCase):
    def test_portal_resolver_uses_validated_issuer_and_uuid(self):
        from server.analyseassistent.portal import resolve_portal_identity
        connect=MagicMock()
        cursor=connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value=(17,)
        user='00000000-0000-0000-0000-000000000001'
        self.assertEqual(resolve_portal_identity(connect,user,'https://synthetic.hanko.io'),17)
        self.assertEqual(cursor.execute.call_args.args[1],('https://synthetic.hanko.io',user))
        connect.reset_mock()
        self.assertIsNone(resolve_portal_identity(connect,'browser-forged-id','https://synthetic.hanko.io'))
        connect.assert_not_called()

    def test_portal_auth_and_csrf_reject_before_database_or_model(self):
        from server.analyseassistent.portal import PortalEndpoint,ANALYSIS_PATH,QUOTA_PATH
        connect,quota,service=MagicMock(),MagicMock(),MagicMock()
        auth=MagicMock(return_value=None)
        endpoint=PortalEndpoint(connect=connect,quota=quota,service=service,validate_session=auth,
            issuer=lambda:'https://synthetic.hanko.io',session_token=lambda _:'synthetic-cookie',
            csrf_token=lambda *a:'csrf',valid_csrf_token=lambda *a:False,allowed_origin='https://test.invalid')
        statuses=[]
        env={'PATH_INFO':ANALYSIS_PATH,'REQUEST_METHOD':'POST','HTTP_ORIGIN':'https://test.invalid'}
        endpoint(env,lambda status,headers:statuses.append(status))
        self.assertTrue(statuses[-1].startswith('401'))
        auth.return_value='00000000-0000-0000-0000-000000000001'
        endpoint(env,lambda status,headers:statuses.append(status))
        self.assertTrue(statuses[-1].startswith('403'))
        endpoint({**env,'PATH_INFO':QUOTA_PATH},lambda status,headers:statuses.append(status))
        self.assertTrue(statuses[-1].startswith('405'))
        connect.assert_not_called(); service.analyze.assert_not_called(); quota.reserve.assert_not_called()

    def test_lazy_service_initializes_once_under_parallel_requests(self):
        from server.analyseassistent.portal import LazyService
        factory=MagicMock(); factory.return_value.analyze.return_value=('synthetic',{})
        lazy=LazyService(factory)
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(lambda _:lazy.analyze('test'),range(8)))
        factory.assert_called_once()
        self.assertEqual(factory.return_value.analyze.call_count,8)

    def test_customer_clarification_is_specific_and_hides_unknown_fields(self):
        from server.analyseassistent.presentation import present
        from server.analyseassistent.results import limited
        result=limited('needs_clarification','internal technical notice',missing_fields=['region','year','secret/path'])
        answer=present(result,None)
        self.assertIn('Bitte ergänzen Sie',answer['paragraphs'][0])
        self.assertEqual(answer['questions'],['Welche Stadt oder Region möchten Sie betrachten?','Auf welches Jahr bezieht sich Ihre Frage?'])
        visible=json.dumps({k:v for k,v in answer.items() if k!='technical_details'},ensure_ascii=False)
        self.assertNotIn('secret/path',visible); self.assertNotIn('internal technical',visible)

    def test_related_data_distinguishes_missing_unchecked_and_known_zero(self):
        from server.analyseassistent.alternatives import related_data
        from server.analyseassistent.presentation import present
        datasets=MagicMock(snapshot_id='synthetic',paths={},names={})
        result={'function_id':'road_relation_goods_limit','data_snapshot_id':'synthetic',
                'status':'partial','parameters':{'origin':'A','destination':'B','year':2024,'metric':'tonnes'}}
        datasets.query.side_effect=[{'status':'available','grouped_details':[{'value':0}]},
            {'status':'missing_row','value':None}, OSError('private failure'),
            {'status':'partial','observations':[{'group':'1','value':None},{'value':100}]}]
        result['related_data']=related_data(result,datasets)
        checks=result['related_data']['checks']
        self.assertTrue(checks['rail']['available'])
        self.assertEqual(checks['iww']['status'],'missing_row')
        self.assertEqual(checks['origin_goods']['status'],'not_checked')
        self.assertFalse(checks['destination_goods']['available'])
        answer=present(result,datasets)
        self.assertEqual(len(answer['suggestions']),1)
        self.assertTrue(any('Ob tatsächlich kein Verkehr' in text for text in answer['paragraphs']))
        self.assertTrue(any('nicht vollständig' in text for text in answer['notes']))
        self.assertNotIn('private failure',json.dumps(answer))
        self.assertEqual(datasets.query.call_count,4)

    def test_related_data_respects_deadline_and_dataset_binding(self):
        from server.analyseassistent.alternatives import related_data
        datasets=MagicMock(snapshot_id='synthetic')
        result={'function_id':'road_relation_goods_limit','data_snapshot_id':'synthetic',
                'parameters':{'origin':'A','destination':'B','year':2024,'metric':'tonnes'}}
        evidence=related_data(result,datasets,deadline=time.monotonic()-1)
        self.assertTrue(all(c['status']=='not_checked' for c in evidence['checks'].values()))
        self.assertIsNone(related_data({**result,'data_snapshot_id':'stale'},datasets))
        datasets.query.assert_not_called()

    def test_model_gate_requires_prompt_and_detects_changed_prompt(self):
        from scripts.analysis.prepare_assistant_gate import required_files, verify_bound_files
        from server.analyseassistent.datasets import digest
        hashes={p.relative_to(ROOT).as_posix():digest(p) for p in required_files()}
        verify_bound_files(hashes)
        missing=dict(hashes)
        del missing['config/analyseassistent/SYSTEM_PROMPT.md']
        with self.assertRaises(ValueError): verify_bound_files(missing)
        changed={**hashes, 'config/analyseassistent/SYSTEM_PROMPT.md':'0'*64}
        with self.assertRaises(ValueError): verify_bound_files(changed)

    def test_incomplete_model_answer_records_usage_without_echo_or_retry(self):
        model = Requesty(model='synthetic', base_url='https://router.eu.requesty.ai/v1',
                         api_key='synthetic-test-key', timeout_seconds=180)
        response = {'choices': [{'finish_reason': 'length', 'message': {'content': 'private incomplete text'}}],
                    'usage': {'prompt_tokens': 12, 'completion_tokens': 1500, 'total_tokens': 1512,
                              'cost': 0.01, 'private_field': 'do not echo'}}
        with patch.object(model.opener, 'open', return_value=io.BytesIO(json.dumps(response).encode())) as opened:
            with self.assertRaises(ModelError) as raised:
                model.complete('prompt', {'phase': 'plan'}, {}, deadline=time.monotonic()+10)
        opened.assert_called_once()
        self.assertEqual(raised.exception.diagnostics['finish_reason'], 'length')
        self.assertEqual(raised.exception.diagnostics['usage']['total_tokens'], 1512)
        self.assertNotIn('private', json.dumps(raised.exception.diagnostics))
        self.assertNotIn('private', str(raised.exception))

    def test_incomplete_diagnostics_rejects_untrusted_reason_and_usage(self):
        from server.analyseassistent.requesty import incomplete_diagnostics
        output = incomplete_diagnostics({'usage': {'cost': 'secret', 'prompt_tokens': True,
                                                    'total_tokens': float('inf')}},
                                        {'finish_reason': ['untrusted']}, 5)
        self.assertEqual(output, {'finish_reason': 'other', 'elapsed_ms': 5, 'usage': {}})

    def test_synthetic_change_and_month_controls_are_not_live_data(self):
        from scripts.analysis.b02 import change, summarize_months
        from scripts.analysis.b0406 import change_ranking
        self.assertEqual(change(0,10,comparable=True)['absolute_change'],10)
        self.assertIsNone(change(0,10,comparable=True)['relative_change_pct'])
        self.assertEqual(change(10,0,comparable=True)['relative_change_pct'],-100)
        self.assertIsNone(change(None,10,comparable=True)['absolute_change'])
        records=[{'id':'small','base':1,'target':10},{'id':'large','base':1000,'target':1500},{'id':'missing','base':None,'target':40}]
        ranked=change_ranking(records,comparable=True,measure='relative')
        self.assertEqual([r['id'] for r in ranked['rows']],['small','large'])
        self.assertEqual([r['relative_change_pct'] for r in ranked['rows']],[900,50])
        self.assertEqual(ranked['excluded'],[{'id':'missing','reason':'missing_value'}])
        self.assertEqual(change_ranking(records,comparable=False)['rows'],[])
        months=[{'month':m,'value':200 if m==12 else 100,'known_sum':200 if m==12 else 100,'missing_count':0} for m in range(1,13)]
        summary=summarize_months(months)
        self.assertEqual(summary['annual_value'],1300)
        self.assertEqual(round(summary['peak_month_share_pct'],2),15.38)
        self.assertIsNone(summarize_months(months[:-1])['annual_value'])

    def test_intermodal_unknown_value_blocks_share(self):
        from server.analyseassistent.support import intermodal_markets
        fixture={'region':'DEA12','year':2024,'mode':'rail','metric':'tonnes','direction':'outbound',
                 'qualified_value':None,'total_value':100,'qualified_missing':1,'total_missing':0,
                 'qualification_unknown':0,'months':list(range(1,13))}
        with patch('server.analyseassistent.support.read',return_value=[fixture]):
            result=intermodal_markets(None,Path('.'),region='DEA12',year=2024,modes=['rail'],metrics=['tonnes'],direction='outbound')
        self.assertEqual(result['status'],'partial')
        self.assertIsNone(result['observations'][2]['value'])

    def test_observed_year_and_named_scenarios_do_not_conflict(self):
        parameters={'region':'DEA12','year':2024,'metric':'tonnes','include_forecast':True}
        record=plan(function_id='region_profile',parameters=parameters,parameter_origins={k:'context' for k in parameters})
        self.assertTrue(verify_plan(record,'Duisburg Ist 2024; VP 2019_BASE und 2040_P1',parameters,{}))
        with self.assertRaises(ValueError):
            verify_plan(record,'Duisburg Ist 2023; VP 2019_BASE und 2040_P1',parameters,{})

    def test_year_list_cannot_override_question_year(self):
        parameters={'region':'DEA12','years':[2016,2025],'metric':'tonnes','direction':'all'}
        record=plan(function_id='modal_history',parameters=parameters,parameter_origins={k:'context' for k in parameters})
        with self.assertRaises(ValueError):
            verify_plan(record,'Duisburg 2024',parameters,{})
    def test_modal_denominator_missing_conflicting_or_zero(self):
        for values,total in [({'road':10,'rail':None,'iww':20},30),
                             ({'road':10,'rail':10,'iww':20},100),
                             ({'road':0,'rail':0,'iww':0},0)]:
            rows,status=modal_rows({'modes_tonnes':values,'total_tonnes':total},year=2024,direction='all',metric='tonnes')
            self.assertEqual(status,'partial')
            self.assertTrue(all(r['value'] is None for r in rows if r.get('unit')=='%'))

    def test_forecast_year_list_must_be_explicit_unique_and_bounded(self):
        from server.analyseassistent.contracts import FUNCTIONS, validate
        for years in [[],[True],[2024,2024],[2019,2020,2021,2024]]:
            with self.assertRaises(ValueError):
                validate(FUNCTIONS['forecast_comparison'][3],{'region':'DEA12','metric':'tonnes','direction':'all','observed_years':years})

    def test_relation_partner_is_not_conflicting_region(self):
        parameters={'region':'DEA23','partner':'DE600','year':2024,'direction':'outbound','classification':'C7','group':'ALL','metric':'tonnes'}
        record=plan(function_id='rail_goods',parameters=parameters,parameter_origins={k:'context' for k in parameters})
        self.assertTrue(verify_plan(record,'Welche Güter werden von Köln nach Hamburg versandt?',parameters,{'DEA23':['Köln'],'DE600':['Hamburg']}))
    def test_explicit_conflicting_year(self):
        with self.assertRaises(ValueError):
            verify_plan(plan(), 'Duisburg 2025 Straße', PARAMETERS, {})

    def test_swapped_endpoints(self):
        params={'origin':'DE600','destination':'DEA23','year':2024,'mode':'rail','metric':'tonnes','group':'ALL'}
        record=plan(function_id='relation',parameters=params,parameter_origins={k:'context' for k in params})
        with self.assertRaises(ValueError):
            verify_plan(record,'DEA23 → DE600, 2024, Schiene',params,{})

    def test_natural_directed_relation_and_ambiguous_or_swapped_routes(self):
        names={'DEA23':['Köln'],'DE600':['Hamburg'],'DEA12':['Duisburg']}
        parameters={'origin':'DEA23','destination':'DE600','year':2024,'metric':'tonnes'}
        record=plan(function_id='road_relation_goods_limit',parameters=parameters,
                    parameter_origins={key:'question' for key in parameters})
        for question in ['Tonnen 2024 von Köln nach Hamburg','Tonnen 2024 Köln → Hamburg']:
            self.assertTrue(verify_plan(record,question,{},names))
        for question in ['Tonnen 2024 von Hamburg nach Köln',
                         'Tonnen 2024 zwischen Köln und Hamburg',
                         'Tonnen 2024 von Köln nach Hamburg und von Köln nach Duisburg',
                         'Tonnen 2024 Köln → Hamburg und Hamburg → Köln']:
            with self.assertRaises(ValueError):
                verify_plan(record,question,{},names)
        with self.assertRaises(ValueError):
            verify_plan(record,'Tonnen 2024 von Köln nach Hamburg',{}, {**names,'OTHER':['Köln']})

    def test_default_tonnes_for_goods_question_is_explicit_and_verified(self):
        from server.analyseassistent.dialogue import complete_plan
        parameters={'origin':'DEA23','destination':'DE600','year':2024}
        record=plan(function_id='road_relation_goods_limit',parameters=parameters,
                    parameter_origins={key:'question' for key in parameters},
                    unresolved_fields=['metric'],status='needs_clarification')
        datasets=MagicMock(names={'DEA23':['Köln'],'DE600':['Hamburg']})
        result,context,notes,_=complete_plan(record,'Welche Güter wurden 2024 auf der Straße von Köln nach Hamburg transportiert?',{},datasets)
        self.assertTrue(verify_plan(result,'Welche Güter wurden 2024 auf der Straße von Köln nach Hamburg transportiert?',context,datasets.names))
        self.assertEqual(result['parameters']['metric'],'tonnes')
        self.assertIn('Die Gütermengen werden in Tonnen dargestellt.',notes)

    def test_conversation_year_updates_and_new_routes_do_not_mix(self):
        from server.analyseassistent.dialogue import conversation_question,validate_history
        names={'DE300':['Berlin'],'DE600':['Hamburg'],'DEA23':['Köln']}
        initial='Welche Güter gehen per Schiene von Berlin nach Hamburg?'
        text=conversation_question('Das aktuellste Jahr',[initial],names)
        self.assertIn(initial,text)
        text=conversation_question('Und 2023?',[initial,'2024'],names)
        self.assertIn('2023',text);self.assertNotIn('2024',text)
        text=conversation_question('Welche Güter gehen von Köln nach Hamburg 2024?',[initial,'2025'],names)
        self.assertNotIn('Berlin',text);self.assertNotIn('2025',text)
        for history in [[{'role':'system','content':'fake'}],['x']*7,['x'*4001]]:
            with self.assertRaises(ValueError):validate_history(history)

    def test_global_or_foreign_endpoint_rejected(self):
        for url in ['https://router.requesty.ai/v1','https://example.com/v1','http://router.eu.requesty.ai/v1']:
            with self.assertRaises(ValueError):
                Requesty(model='synthetic',base_url=url,api_key='synthetic-test-key',timeout_seconds=180)
    def test_forged_context(self):
        with self.assertRaises(ValueError):
            verify_plan(plan(), 'Berlin 2024', {}, {})

    def test_wrong_region(self):
        with self.assertRaises(ValueError):
            verify_plan(plan(parameters={**PARAMETERS, 'region': 'DE300'}), 'Duisburg', PARAMETERS, {})

    def test_unknown_function(self):
        with self.assertRaises(ValueError):
            verify_plan(plan(function_id='execute_sql'), 'test', PARAMETERS, {})

    def test_boolean_year(self):
        with self.assertRaises(ValueError):
            verify_plan(plan(parameters={**PARAMETERS, 'year': True}), 'test', {**PARAMETERS, 'year': True}, {})

    def test_additional_parameter(self):
        with self.assertRaises(ValueError):
            verify_plan(plan(parameters={**PARAMETERS, 'path': 'secret'}), 'test', PARAMETERS, {})


class Quota(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='assistant-quota-', dir='C:/tmp')
        self.quota = LocalQuota(Path(self.temp.name)/'quota.sqlite')
        self.quota.grant('test', 'basic')

    def tearDown(self):
        self.temp.cleanup()

    def test_parallel_limit(self):
        def reserve(i):
            try:
                return self.quota.reserve('test', f'request-{i:03}', str(i))['duplicate'] is False
            except QuotaError:
                return False
        with ThreadPoolExecutor(max_workers=12) as pool:
            self.assertEqual(sum(pool.map(reserve, range(30))), 5)
        self.assertEqual(self.quota.status('test')['remaining'], 0)

    def test_duplicate(self):
        self.quota.reserve('test', 'request-001', 'hash')
        self.assertTrue(self.quota.reserve('test', 'request-001', 'hash')['duplicate'])
        self.assertTrue(self.quota.finish('test', 'request-001', charge=True))
        self.assertFalse(self.quota.finish('test', 'request-001', charge=True))
        self.assertEqual(self.quota.status('test')['used'], 1)
        with self.assertRaises(QuotaError):
            self.quota.reserve('test', 'request-001', 'other')

    def test_release_and_upgrade(self):
        self.quota.reserve('test', 'request-001', 'hash')
        self.quota.finish('test', 'request-001', charge=False)
        self.assertEqual(self.quota.status('test')['remaining'], 5)
        self.quota.grant('test', 'premium')
        self.assertEqual(self.quota.status('test')['remaining'], 50)

    def test_month_boundary(self):
        self.assertEqual(month_key(datetime(2026, 8, 31, 22, 1, tzinfo=timezone.utc)), '2026-09')
        self.quota.reserve('test', 'request-001', 'hash', now=datetime(2026,8,31,21,59,tzinfo=timezone.utc))
        self.assertEqual(self.quota.status('test',now=datetime(2026,8,31,22,1,tzinfo=timezone.utc))['remaining'], 5)

    def test_revoked(self):
        self.quota.grant('test', 'premium', active=False)
        with self.assertRaises(QuotaError):
            self.quota.reserve('test', 'request-001', 'hash')

    def test_api_rejects_browser_identity_and_cross_origin(self):
        app = Application(None, self.quota, lambda env: 'test', allowed_origin='http://localhost')
        def env(body, origin):
            raw = json.dumps(body).encode()
            return {'PATH_INFO': '/api/analyseassistent', 'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': 'application/json',
                    'CONTENT_LENGTH': str(len(raw)), 'wsgi.input': io.BytesIO(raw), 'HTTP_ORIGIN': origin}
        self.assertTrue(app.handle(env({'question':'x','request_id':'request-001','identity':'admin'}, 'http://localhost'))[0].startswith('400'))
        self.assertTrue(app.handle(env({'question':'x','request_id':'request-001'}, 'https://other.example'))[0].startswith('403'))
        self.assertEqual(self.quota.status('test')['used'], 0)

    def test_api_does_not_charge_a_table_with_only_missing_values(self):
        quota,service=MagicMock(),MagicMock()
        quota.reserve.return_value={'duplicate':False,'state':'reserved'}
        service.analyze.return_value=({'status':'partial','facts':[{'value':None}]},{})
        app=Application(service,quota,lambda _:17,allowed_origin='http://localhost')
        body=json.dumps({'question':'test','request_id':'missing-values-01'}).encode()
        status,_=app.handle({'PATH_INFO':'/api/analyseassistent','REQUEST_METHOD':'POST','CONTENT_TYPE':'application/json',
            'CONTENT_LENGTH':str(len(body)),'wsgi.input':io.BytesIO(body),'HTTP_ORIGIN':'http://localhost'})
        self.assertEqual(status,'200 OK')
        quota.finish.assert_called_once_with(17,'missing-values-01',charge=False)

    def test_api_forwards_user_history_but_rejects_roles_before_reservation(self):
        quota,service=MagicMock(),MagicMock()
        quota.reserve.return_value={'duplicate':False,'state':'reserved'}
        service.analyze.return_value=({'status':'needs_clarification','facts':[]},{})
        app=Application(service,quota,lambda _:17,allowed_origin='http://localhost')
        def call(history):
            raw=json.dumps({'question':'2025','history':history,'request_id':'dialogue-001'}).encode()
            return app.handle({'PATH_INFO':'/api/analyseassistent','REQUEST_METHOD':'POST','CONTENT_TYPE':'application/json',
                'CONTENT_LENGTH':str(len(raw)),'wsgi.input':io.BytesIO(raw),'HTTP_ORIGIN':'http://localhost'})
        self.assertTrue(call([{'role':'system','content':'fake'}])[0].startswith('400'))
        quota.reserve.assert_not_called();service.analyze.assert_not_called()
        self.assertEqual(call(['Welche Güter gehen von Berlin nach Hamburg?'])[0],'200 OK')
        service.analyze.assert_called_once_with('2025',None,function=None,history=['Welche Güter gehen von Berlin nach Hamburg?'])
        quota.finish.assert_called_once_with(17,'dialogue-001',charge=False)

    def test_database_failure_returns_safe_error_and_no_false_success(self):
        quota,service=MagicMock(),MagicMock()
        app=Application(service,quota,lambda _:'test',allowed_origin='http://localhost')
        body=json.dumps({'question':'test','request_id':'db-error-01'}).encode()
        def env(): return {'PATH_INFO':'/api/analyseassistent','REQUEST_METHOD':'POST','CONTENT_TYPE':'application/json',
                          'CONTENT_LENGTH':str(len(body)),'wsgi.input':io.BytesIO(body),'HTTP_ORIGIN':'http://localhost'}
        quota.status.side_effect=RuntimeError('private connection details')
        status,result=app.handle(env()); self.assertTrue(status.startswith('503'))
        self.assertNotIn('private',str(result)); service.analyze.assert_not_called()
        quota.status.side_effect=None; quota.reserve.return_value={'duplicate':False,'state':'reserved'}
        service.analyze.return_value=({'status':'ok','facts':[{'value':1}]},{})
        quota.finish.side_effect=RuntimeError('private database error')
        status,result=app.handle(env()); self.assertTrue(status.startswith('503'))
        self.assertEqual(result['request_id'],'db-error-01'); self.assertNotIn('private',str(result))


class SyntheticRelations(unittest.TestCase):
    def test_ties_full_denominator_and_unknown_partner(self):
        # Deliberately synthetic A-D values exercise ranking behavior, never a
        # real geography or evidence of live-source coverage.
        with tempfile.TemporaryDirectory(prefix='assistant-ranks-',dir='C:/tmp') as folder:
            with duckdb.connect() as con:
                con.execute('''CREATE TABLE fixture(origin_id VARCHAR,dest_id VARCHAR,known_sum DOUBLE,
                    year_ref INTEGER DEFAULT 2024,mode VARCHAR DEFAULT 'road',metric VARCHAR DEFAULT 'tonnes',
                    group_7_id VARCHAR DEFAULT 'ALL',source_rows INTEGER DEFAULT 1,missing_count INTEGER DEFAULT 0,
                    restricted_count INTEGER DEFAULT 0,unknown_quality_count INTEGER DEFAULT 0,
                    rounded_zero_count INTEGER DEFAULT 0,source_id VARCHAR DEFAULT 'synthetic')''')
                con.executemany('INSERT INTO fixture(origin_id,dest_id,known_sum) VALUES (?,?,?)',
                                [('FOCUS','A',300),('FOCUS','B',200),('FOCUS','C',200),('FOCUS','D',10)])
                path=Path(folder)/'annual_od.parquet'
                con.execute('COPY fixture TO '+literal(path)+' (FORMAT PARQUET)')
                params={'region':'FOCUS','year':2024,'mode':'road','metric':'tonnes','direction':'all','group':'ALL','top':2,'external':True}
                result=partner_ranking(con,Path(folder),**params)
                self.assertEqual(result['denominator'],710)
                self.assertEqual([r['id'] for r in result['observations'] if r.get('unit')!='%'],['A','B','C'])
                self.assertEqual([r['rank'] for r in result['observations'] if r.get('unit')!='%'],[1,2,2])
                con.execute("INSERT INTO fixture(origin_id,dest_id,known_sum,missing_count) VALUES ('FOCUS','UNKNOWN',NULL,1)")
                con.execute('COPY fixture TO '+literal(path)+' (FORMAT PARQUET)')
                result=partner_ranking(con,Path(folder),**params)
                self.assertIsNone(result['denominator'])
                self.assertEqual(result['unknown_partner_count'],1)
                self.assertTrue(all(r['value'] is None for r in result['observations'] if r.get('unit')=='%'))


class RealData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.datasets = Datasets(ROOT)
        cls.service = Service(cls.datasets)

    def test_rail_dialogue_year_reply_latest_and_direction(self):
        def model():
            result=MagicMock()
            result.complete.return_value=(plan(function_id='rail_goods',parameters={'region':'DE300','partner':'DE600'},
                parameter_origins={'region':'question','partner':'question'},
                unresolved_fields=['year','direction','group','metric','classification'],status='needs_clarification'),{})
            return result
        initial='Welche Güter gehen per Schiene von Berlin nach Hamburg?'
        service=Service(self.datasets,model=model())
        first,_=service.analyze(initial,select_answer=False)
        self.assertEqual(first['status'],'needs_clarification')
        self.assertEqual(first['missing_fields'],['year'])
        self.assertIn('2025',first['answer']['questions'][0])
        self.assertEqual(first['answer']['replies'][0]['question'],'2025')
        for reply,year in [('Das aktuellste Jahr',2025),('2024',2024)]:
            result,audit=service.analyze(reply,history=[initial],select_answer=False)
            self.assertIn(result['status'],['ok','partial'])
            self.assertEqual(result['parameters'],{'region':'DE300','partner':'DE600','year':year,'direction':'outbound','group':'ALL','classification':'C7','metric':'tonnes'})
            direct,_=self.service.analyze(f'Berlin nach Hamburg {year}',result['parameters'],function='rail_goods')
            self.assertEqual(result['facts'],direct['facts'])
        complete,_=service.analyze(initial+' Das Jahr 2024',select_answer=False)
        self.assertIn(complete['status'],['ok','partial'])

    def test_recent_relation_is_answered_as_five_year_series_without_plan_model(self):
        question='Wie viel Güter sind in den letzten Jahren von Rosenheim nach Augsburg transportiert worden?'
        result,audit=self.service.analyze(question,select_answer=False)
        self.assertIn(result['status'],['ok','partial'])
        self.assertEqual(audit['attempted_model_calls'],0)
        self.assertEqual(result['function_id'],'relation_history')
        self.assertEqual(result['parameters'],{'origin':'DE213','destination':'DE271','start':2020,'end':2024,
                                               'modes':['road','rail','iww'],'metric':'tonnes'})
        self.assertEqual(len([f for f in result['facts'] if not f.get('aggregate')]),15)
        self.assertTrue(result['answer']['tables'][0]['collapsed'])
        self.assertIn('kein vollständiger Verkehrsträgervergleich',result['answer']['paragraphs'][0])
        self.assertIn('kein nutzbarer Güterverkehrswert erfasst beziehungsweise veröffentlicht',result['answer']['paragraphs'][0])
        self.assertTrue(any('rechnerischen Rückgang um 50,99 %' in paragraph for paragraph in result['answer']['paragraphs']))
        self.assertTrue(any('kreisfreie Städte' in note for note in result['answer']['notes']))
        evidence=next(statement for statement in result['statements'] if 'rechnerischen Rückgang' in statement['text'])
        inverted={'result_id':result['result_id'],'data_snapshot_id':result['data_snapshot_id'],
                  'paragraphs':[{'text':evidence['text'].replace('Rückgang','Wachstum'),
                                 'statement_ids':[evidence['id']]}],
                  'table_ids':[],'wording_variant':'compact'}
        with self.assertRaises(ValueError):
            apply_selection(result,inverted)

    def test_recent_relation_followup_keeps_multi_year_intent_without_model(self):
        initial='Wie viel Güter sind in den letzten Jahren von Rosenheim nach Augsburg transportiert worden?'
        result,audit=self.service.analyze('ich möchte mehrere Jahrgänge verwenden',history=[initial],select_answer=False)
        self.assertEqual(result['function_id'],'relation_history')
        self.assertEqual((result['parameters']['start'],result['parameters']['end']),(2020,2024))
        self.assertEqual(audit['attempted_model_calls'],0)

    def test_data_failure_has_safe_stage_and_diagnostic_code(self):
        with patch.object(self.datasets,'query',side_effect=OSError('private path')):
            result,audit=self.service.analyze('Duisburg',PARAMETERS,function='balance',select_answer=False)
        self.assertEqual(result['status'],'error')
        self.assertEqual(audit['failure_stage'],'data_lookup')
        self.assertEqual(audit['error_kind'],'OSError')
        self.assertIn('AA-D02',result['answer']['paragraphs'][0])
        self.assertNotIn('private path',json.dumps(result,ensure_ascii=False))

    def test_goods_structure_leads_with_relations_between_values(self):
        params={'region':'DEA12','year':2024,'mode':'road','metric':'tonnes',
                'directions':['outbound','inbound'],'granularity':'C7'}
        result,_=self.service.analyze('Welche Güter prägen Duisburg?',params,function='goods_structure',select_answer=False)
        self.assertIn('versandt und',result['answer']['paragraphs'][0])
        self.assertTrue(any('größte Gütergruppe' in paragraph for paragraph in result['answer']['paragraphs']))
        self.assertTrue(result['answer']['tables'][0]['collapsed'])

    def test_region_profile_fallback_explains_modal_distribution(self):
        params={'region':'DEA12','year':2024,'metric':'tonnes','include_forecast':False}
        result,_=self.service.analyze('Wie ist Duisburgs Güterverkehrsprofil?',params,function='region_profile',select_answer=False)
        self.assertTrue(any('Verteilung lautet' in paragraph and '44,82 %' in paragraph for paragraph in result['answer']['paragraphs']))
        self.assertTrue(result['answer']['tables'][0]['collapsed'])

    def test_display_references_reproduce_original_sources(self):
        from scripts.analysis.build_assistant_references import build, TARGET
        self.assertEqual(json.loads((ROOT/TARGET).read_text(encoding='utf-8')), build(ROOT))

    def test_airport_names_preserve_statistical_values_and_countries(self):
        parameters = {'kind':'air','node':'EDDP','year':2024,'metric':'tonnes',
                      'direction':'outbound','international':True,'top':100}
        raw = self.datasets.query('node_partners', parameters)
        result, _ = self.service.analyze('Internationale Luftfracht ab Leipzig/Halle 2024', parameters, function='node_partners')
        values = [f for f in result['facts'] if f['unit'] != '%']
        self.assertEqual([(f['partner_id'], f['value'], f['partner_country']) for f in values],
                         [(r['id'],r['value'],r['partner_country']) for r in raw['rows']])
        self.assertAlmostEqual(raw['denominator'],662332,places=7)
        self.assertEqual(values[0]['label'],'East Midlands Airport')
        self.assertEqual(next(f for f in values if f['partner_id']=='LFSB')['partner_country'],'CH')
        self.assertIn('Leipzig/Halle', result['answer']['title'])
        shares = [f for f in result['facts'] if f['unit']=='%']
        self.assertTrue(all(abs(f['denominator']-662332)<1e-7 for f in shares))

    def test_regional_scope_example_is_year_bound_and_not_a_billed_analysis(self):
        result, _ = self.service.analyze('Warum unterscheiden sich Gebietssumme und Deutschlandwert?',
                                        {'topic':'regional_vs_national'}, function='explain_scope')
        example = next(f for f in result['text_facts'] if f.get('evidence'))
        self.assertEqual(example['evidence']['year'],2024)
        self.assertEqual(example['evidence']['entry_count'],422)
        self.assertEqual(example['evidence']['district_count'],400)
        self.assertEqual(len(example['evidence']['other_codes']),22)
        self.assertIn('2024',example['text'])
        self.assertIn(example['source'],result['sources'])
        self.assertEqual(result['facts'],[])
        self.assertIn(example['text'],result['answer']['paragraphs'])

    def test_duisburg_balance(self):
        result, audit = self.service.analyze('Duisburg 2024 Straße Tonnen', PARAMETERS, function='balance')
        self.assertEqual(result['status'], 'ok')
        self.assertEqual([f['value'] for f in result['facts']], [26371111,22134701,4236410])
        self.assertEqual(audit['model_calls'], [])

    def test_t20_customer_answer_preserves_value_and_relevant_limits(self):
        parameters={'origin':'DEA23','destination':'DE600','year':2024,'metric':'tonnes'}
        result,_=self.service.analyze('Köln → Hamburg 2024',parameters,function='road_relation_goods_limit')
        answer=result['answer']
        visible=json.dumps({k:v for k,v in answer.items() if k not in {'technical_details','tables','sources','followups'}},ensure_ascii=False)
        for text in ['Köln','Hamburg','67.757 Tonnen','nicht aufschlüsseln','eingeschränkt belastbar']:
            self.assertIn(text,visible)
        for text in [self.datasets.snapshot_id,'DEA23','DE600','C1–C7','OD']:
            self.assertNotIn(text,visible)
        self.assertEqual(answer['tables'][0]['rows'][0]['value'],'67.757')
        self.assertEqual(answer['technical_details']['data_snapshot_id'],self.datasets.snapshot_id)
        self.assertEqual(result['facts'][0]['value'],67757)
        checks=result['related_data']['checks']
        self.assertEqual(checks['rail']['evidence']['published_sum'],199851)
        self.assertTrue(checks['rail']['available'])
        self.assertEqual(checks['iww']['status'],'missing_row')
        self.assertIsNone(checks['iww']['evidence']['value'])
        self.assertEqual(checks['rail']['parameters']['partner'],'DE600')
        self.assertEqual(checks['rail']['parameters']['direction'],'outbound')
        self.assertEqual(len(answer['suggestions']),3)
        self.assertEqual(answer['followups'][0]['parameters'],checks['rail']['parameters'])
        self.assertEqual(answer['followups'][0]['question'],answer['suggestions'][0])
        for key,direction,expected in [('origin_goods','outbound',25225748),('destination_goods','inbound',57257443)]:
            self.assertTrue(checks[key]['available'])
            self.assertEqual(checks[key]['parameters']['directions'],[direction])
            observations=checks[key]['evidence']['observations']
            self.assertEqual(next(r['value'] for r in observations if not r.get('group')),expected)
        self.assertTrue(any('innerregionaler' in n for n in answer['notes']))
        self.assertTrue(any('Ob tatsächlich kein Verkehr' in n for n in answer['paragraphs']))

    def test_road_relation_has_total_but_no_goods_breakdown(self):
        params={'origin':'DEA23','destination':'DE600','year':2024,'metric':'tonnes'}
        result,_=self.service.analyze('Köln → Hamburg',params,function='road_relation_goods_limit')
        self.assertEqual(result['status'],'partial')
        self.assertEqual([f['value'] for f in result['facts']],[67757])
        self.assertEqual(result['facts'][0]['quality_status'],'restricted')
        self.assertTrue(any('Güterstruktur dieser Straßenrelation ist nicht verfügbar' in n for n in result['notices']))

    def test_rail_goods_two_years_preserve_published_sums(self):
        params={'region':'DEA23','partner':'DE600','years':[2023,2024],'direction':'outbound','metric':'tonnes','classification':'C7'}
        result,_=self.service.analyze('Köln → Hamburg',params,function='rail_goods_history')
        totals=[f['value'] for f in result['facts'] if f.get('sum_scope')]
        self.assertEqual(totals,[227456,199851])
        self.assertTrue(any(f['unit']=='%' for f in result['facts']))
        self.assertTrue(any('Dreistellige NST-Feinpositionen bleiben intern' in n for n in result['notices']))

    def test_rail_relation_goods_followup_compares_named_groups_and_never_exposes_triples(self):
        initial,_=self.service.analyze(
            'Wie entwickelte sich der Schienengüterverkehr von Berlin nach Hamburg von 2021 bis 2025?',
            {'origin':'DE300','destination':'DE600','start':2021,'end':2025,
             'modes':['rail'],'metric':'tonnes'},function='relation_history',select_answer=False)
        self.assertEqual(initial['function_id'],'relation_history')
        followup,audit=self.service.analyze(
            'Gab es Gütergruppen, die auf dieser Verbindung besonders verloren?',
            conversation=initial['conversation'],select_answer=False)
        self.assertEqual(audit['attempted_model_calls'],0)
        self.assertEqual(followup['function_id'],'rail_goods_history')
        self.assertEqual(followup['parameters']['years'],[2021,2025])
        self.assertEqual(followup['parameters']['classification'],'C7')
        decline=next(f for f in followup['facts'] if f.get('change')=='absolute' and f.get('group')=='7')
        self.assertEqual(decline['value'],-159621)
        self.assertEqual(decline['group_name'],'Sonstige Produkte')
        public=json.dumps({'result':followup,'answer':followup['answer']},ensure_ascii=False)
        self.assertNotRegex(public,r'NST\s+[0-9]{3}')
        self.assertFalse(any('nst_raw' in f for f in followup['facts']))

        nst,_=self.service.analyze(
            'Und wie haben sich die NST-Gütergruppen entwickelt?',
            conversation=followup['conversation'],select_answer=False)
        self.assertEqual(nst['parameters']['classification'],'NST20')
        self.assertTrue(any(f.get('group_name') for f in nst['facts']))
        self.assertNotRegex(json.dumps(nst,ensure_ascii=False),r'NST\s+[0-9]{3}')

    def test_model_clarification_uses_only_known_field_labels(self):
        class Missing:
            def complete(self,*args,**kwargs):
                return {'phase':'plan','function_id':None,'parameters':{},'parameter_origins':{},
                        'unresolved_fields':['region','year','private/path'],'status':'needs_clarification'},{}
        result,audit=Service(self.datasets,Missing()).analyze('Unsere Stadt')
        self.assertEqual(result['status'],'needs_clarification')
        self.assertIn('Region, Jahr',result['notices'][0])
        self.assertNotIn('private/path',result['notices'][0])
        self.assertEqual(audit['attempted_model_calls'],1)

    def test_goods_structure_directions_and_group_rankings(self):
        params={'region':'DEA12','year':2024,'mode':'road','metric':'tonnes','directions':['outbound','inbound'],'granularity':'C7'}
        result,_=self.service.analyze('Duisburg',params,function='goods_structure')
        self.assertEqual(result['status'],'ok')
        for direction,total,expected in [('outbound',26371111,['3','7','4','1','2','6','5']),('inbound',22134701,['3','7','1','4','6','2','5'])]:
            rows=[f for f in result['facts'] if f.get('direction')==direction and f['unit']=='t' and 'group' in f]
            self.assertEqual(sum(f['value'] for f in rows),total)
            self.assertEqual([f['group'] for f in rows],expected)
            shares=[f for f in result['facts'] if f.get('direction')==direction and f['unit']=='%']
            self.assertAlmostEqual(sum(f['value'] for f in shares),100)
        params['granularity']='NST20'
        result,_=self.service.analyze('Duisburg',params,function='goods_structure')
        self.assertEqual(result['status'],'not_available')
        self.assertEqual(result['facts'],[])

    def test_goods_missing_road_year_is_not_zero(self):
        params={'region':'DEA12','year':2025,'mode':'road','metric':'tonnes','directions':['outbound'],'granularity':'C7'}
        result,_=self.service.analyze('Duisburg',params,function='goods_structure')
        self.assertEqual(result['status'],'not_available')
        self.assertEqual(result['facts'],[])

    def test_national_intermodal_markets_remain_separate(self):
        params={'region':'DE','year':2024,'modes':['rail','iww'],'metrics':['tonnes','tkm'],'direction':'all'}
        result,_=self.service.analyze('Deutschland',params,function='intermodal_markets')
        self.assertEqual(result['status'],'ok')
        self.assertEqual(len(result['facts']),12)
        self.assertEqual(result['facts'][0]['value'],99853065)
        self.assertAlmostEqual(result['facts'][6]['value'],16738676.4,places=4)
        self.assertTrue(all(f['mode'] in ['rail','iww'] for f in result['facts']))
        self.assertTrue(any('nicht additiv' in n for n in result['notices']))
        self.assertLessEqual(len(result['answer']['paragraphs']),3)
        self.assertTrue(result['answer']['tables'][0]['collapsed'])

    def test_duisburg_intermodal_external_outbound(self):
        params={'region':'DEA12','year':2024,'modes':['rail'],'metrics':['tonnes'],'direction':'outbound'}
        result,_=self.service.analyze('Duisburg',params,function='intermodal_markets')
        self.assertEqual([f['value'] for f in result['facts'][:2]],[4422816,9194861])
        self.assertEqual(round(result['facts'][2]['value'],2),48.10)
        self.assertEqual(result['facts'][2]['denominator'],9194861)

    def test_intermodal_unknown_destination_is_not_external_outbound(self):
        params={'region':'DE712','year':2016,'modes':['iww'],'metrics':['tkm'],'direction':'outbound'}
        result,_=self.service.analyze('Frankfurt',params,function='intermodal_markets')
        self.assertAlmostEqual(result['facts'][1]['value'],377969860.8,places=3)
        self.assertTrue(any('bekanntem Gegenraum' in n for n in result['notices']))

    def test_classification_preserves_codes_and_text_tables(self):
        result,_=self.service.analyze('Gütergruppen',{'topic':'classification'},function='explain_scope')
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['facts'],[])
        self.assertEqual(next(f['group'] for f in result['text_facts'] if f.get('division')=='03'),'1')
        self.assertEqual(next(f['group'] for f in result['text_facts'] if f.get('division')=='14'),'6')
        self.assertFalse(any(f.get('nst') for f in result['text_facts']))
        self.assertEqual(result['tables'][0]['kind'],'text')

    def test_outside_scope_has_no_invented_numbers(self):
        result,_=self.service.analyze('Kosten und Umweltbilanz',{'topic':'outside_scope'},function='explain_scope')
        self.assertEqual(result['status'],'out_of_scope')
        self.assertEqual(result['facts'],[])
        self.assertTrue(any('nicht bestimmen' in f['text'] for f in result['text_facts']))

    def test_airport_2025_weight_and_corrected_flights_available(self):
        params={'kind':'air','node':'EDDP','year':2025,'direction':'all','metrics':['tonnes','flights']}
        result,_=self.service.analyze('Leipzig/Halle 2025',params,function='node_profile')
        self.assertEqual(result['status'],'ok')
        self.assertEqual([(f['value'],f['unit']) for f in result['facts']],[(1390729.8,'t'),(48657,'Flüge')])
        self.assertFalse(any('Quellenwiderspruch' in n for n in result['notices']))

    def test_road_distance_units_and_population_are_visible(self):
        params={'product':'VD2','year':2024,'region':'DE254','direction':'outbound','population':'I','metric':'trips','partner':None}
        result,_=self.service.analyze('Nürnberg 2024',params,function='road_details')
        self.assertEqual(result['status'],'ok')
        self.assertEqual([f['value'] for f in result['facts']],[698880.8,400300.5,476759.4])
        self.assertTrue(all(f['unit']=='Fahrten' for f in result['facts']))
        self.assertTrue(any('In Deutschland zugelassene' in n for n in result['notices']))

    def test_hamburg_partner_ranking_full_denominator_and_flags(self):
        params={'region':'DE600','year':2024,'mode':'road','metric':'tonnes','direction':'all','group':'ALL','top':5,'external':True}
        raw=self.datasets.query('partner_ranking',params)
        self.assertEqual(raw['denominator'],55473138)
        self.assertEqual(raw['restricted_denominator_value'],21167732)
        self.assertEqual([r['id'] for r in raw['observations'] if r.get('unit')!='%'],['DE933','DEF0D','DEF0F','DEF06','DE929'])
        result,_=self.service.analyze('Hamburg',params,function='partner_ranking')
        self.assertEqual(result['status'],'ok')
        self.assertTrue(all(f['denominator']==55473138 for f in result['facts'] if f['unit']=='%'))
        self.assertTrue(any(f['quality_status']=='restricted' and f['value']==21167732 for f in result['facts']))

    def test_exact_relation_missing_is_not_zero(self):
        params={'origin':'DEA12','destination':'DEE03','year':2024,'metric':'tonnes'}
        result,_=self.service.analyze('DEA12 → DEE03',params,function='relation_matrix')
        self.assertEqual(result['status'],'partial')
        self.assertEqual([r['value'] for r in result['facts'] if not r.get('aggregate')],[None,None,None,None,1947,1189])
        self.assertTrue(all(r['value'] is None for r in result['facts'] if r.get('aggregate')=='modal_sum'))
        self.assertTrue(all(r['source_status']=='missing_row' for r in result['facts'][:4]))
        self.assertTrue(any('1.947' in s for s in result['summary']))

    def test_national_transit_is_rendered_with_its_modal_denominator(self):
        params={'year':2024,'metric':'tkm','mode':'rail'}
        result,_=self.service.analyze('Deutschland 2024 Schiene',params,function='national')
        transit=[f for f in result['facts'] if f.get('relationship')=='4']
        self.assertEqual(transit[0]['value'],13622343988)
        self.assertEqual(transit[1]['denominator'],126319807860)
        self.assertEqual(round(transit[1]['value'],3),10.784)
        self.assertEqual(transit[0]['label'],'Transitverkehr')
        self.assertTrue(any(transit[0]['fact_id'] in s['fact_ids'] for s in result['statements']))
        self.assertLessEqual(len(result['summary']),3)

    def test_rail_goods_groups_total_and_missing_positions_survive(self):
        params={'year':2024,'region':'DEA23','partner':'DE600','direction':'outbound','metric':'tonnes','group':'ALL','classification':'C7'}
        result,_=self.service.analyze('Köln → Hamburg',params,function='rail_goods')
        groups=[f for f in result['facts'] if f.get('group')]
        self.assertEqual([f['value'] for f in groups],[231,None,None,None,None,None,199620])
        self.assertTrue(all(f['value_status']=='missing_row' for f in groups[1:6]))
        self.assertEqual(result['facts'][-1]['value'],199851)

    def test_rail_goods_answer_uses_named_public_classifications_only(self):
        from server.analyseassistent.presentation import present, number
        from server.analyseassistent.narrative import evidence
        params={'year':2025,'region':'DE300','partner':'DE600','direction':'outbound','metric':'tonnes','group':'ALL','classification':'C7'}
        result,_=self.service.analyze('Berlin → Hamburg',params,function='rail_goods')
        answer=present(result,self.datasets)
        rows=answer['tables'][0]['rows']
        self.assertEqual(len(rows),8)
        grouped=[f for f in result['facts'] if f.get('group')]
        self.assertEqual([r['value'] for r in rows[:7]],[number(f['value']) for f in grouped])
        self.assertEqual(rows[-1]['value'],'240.297')
        serialized=json.dumps({'result':result,'answer':answer,'evidence':evidence(result,answer)},ensure_ascii=False)
        self.assertNotRegex(serialized,r'NST\s+[0-9]{3}')
        self.assertFalse(any('nst_raw' in f for f in result['facts']))
        # An explicit NST request uses named two-digit divisions, never fine positions.
        params['classification']='NST20'
        detail,_=self.service.analyze('NST-Gruppen',params,function='rail_goods')
        detail_rows=present(detail,self.datasets)['tables'][0]['rows']
        self.assertEqual(len(detail_rows),21)
        self.assertTrue(any('Nahrungs- und Genussmittel' in r['label'] for r in detail_rows))
        self.assertNotRegex(json.dumps(detail,ensure_ascii=False),r'NST\s+[0-9]{3}')
        # A selected aggregate must not imply six other groups have missing data.
        params.update(classification='C7',group='5')
        filtered,_=self.service.analyze('Güterart 5',params,function='rail_goods')
        self.assertEqual(len(present(filtered,self.datasets)['tables'][0]['rows']),2)

    def test_compare_regions_retains_all_groups(self):
        params={'regions':['DEA12','DEE03'],'year':2024,'metric':'tonnes','direction':'all'}
        result,_=self.service.analyze('Duisburg und Magdeburg',params,function='compare_regions')
        self.assertEqual(len([f for f in result['facts'] if 'group' in f and f['unit']=='t']),14)
        self.assertEqual(len([f for f in result['facts'] if 'group' in f and f['unit']=='%']),14)
        for region in params['regions']:
            self.assertAlmostEqual(sum(f['value'] for f in result['facts'] if f.get('region')==region and 'group' in f and f['unit']=='%'),100)
        self.assertAlmostEqual(result['facts'][-1]['value'],108215313.5-23180902.5)

    def test_2025_missing_road_source_blocks_modal_share(self):
        params={'region':'DEA12','years':[2016,2025],'metric':'tonnes','direction':'all'}
        result,_=self.service.analyze('Duisburg',params,function='modal_history')
        self.assertEqual(result['status'],'partial')
        rows2025=[f for f in result['facts'] if f['year']==2025]
        self.assertTrue(all(f['value'] is None for f in rows2025 if f['unit']=='%'))
        self.assertTrue(all(f['value'] is None for f in rows2025 if f['mode']=='road'))
        self.assertEqual(next(f['value'] for f in rows2025 if f['mode']=='rail' and f['unit']=='t'),18410000)
        params={'regions':['DEA12','DEE03'],'year':2025,'metric':'tonnes','direction':'all'}
        result,_=self.service.analyze('Duisburg und Magdeburg',params,function='compare_regions')
        self.assertEqual(result['status'],'partial')
        self.assertTrue(all(f['value'] is None for f in result['facts'] if f['unit']=='%'))

    def test_magdeburg_ten_years_preserved_with_transparent_endpoint_change(self):
        params={'region':'DEE03','start':2016,'end':2025,'mode':'rail','metric':'tonnes','direction':'all'}
        result,_=self.service.analyze('Magdeburg',params,function='regional_history')
        self.assertEqual(result['status'],'ok')
        self.assertEqual([f['value'] for f in result['facts']],
                         [391082,376529,413339,3350578,3563715,3712362,3775110,4466662,4368137,1265439])
        self.assertFalse(any(f['unit']=='%' for f in result['facts']))
        self.assertTrue(any('rechnerischen Wachstum von 223,57 %' in paragraph for paragraph in result['answer']['paragraphs']))
        self.assertTrue(any('nicht um Gebiets-, Erfassungs- oder Revisionsbrüche bereinigt' in note for note in result['answer']['notes']))

    def test_duisburg_full_profile_separates_forecast(self):
        params={'region':'DEA12','year':2024,'metric':'tonnes','include_forecast':True}
        result,audit=self.service.analyze('Duisburg',params,function='region_profile')
        self.assertEqual(result['status'],'ok')
        self.assertAlmostEqual(result['facts'][0]['value'],108215313.5)
        self.assertAlmostEqual(result['facts'][3]['value'],-17549997.9)
        totals=[f for f in result['facts'] if f['label'].startswith('Alle Landverkehrsträger / VP')]
        self.assertEqual([f['value'] for f in totals[:2]],[115374997,103871423])
        self.assertEqual(round(totals[2]['value'],1),-10.0)
        self.assertTrue(all('Verkehrsprognose' in f['source'] for f in totals))
        self.assertTrue(any('Binnen' in s and 'zweimal' in s for s in result['notices']))
        self.assertEqual(audit['model_calls'],[])

    def test_regional_modal_shares_and_direction_denominator(self):
        for direction,denominator,expected in [('all',108215313.5,[44.8,16.7,38.5]),('inbound',62882655.7,None)]:
            params={'region':'DEA12','year':2024,'metric':'tonnes','direction':direction}
            result,_=self.service.analyze('Duisburg',params,function='regional_modal_split')
            self.assertEqual(result['status'],'ok')
            shares=[f for f in result['facts'] if f['unit']=='%']
            self.assertAlmostEqual(sum(f['value'] for f in shares),100)
            self.assertTrue(all(abs(f['denominator']-denominator)<0.01 for f in shares))
            if expected: self.assertEqual([round(f['value'],1) for f in shares],expected)

    def test_forecast_comparison_does_not_mix_observed_and_scenario(self):
        params={'region':'DEA12','observed_years':[2019,2024],'metric':'tonnes','direction':'all'}
        result,_=self.service.analyze('Duisburg',params,function='forecast_comparison')
        self.assertEqual(result['status'],'ok')
        observed=[f for f in result['facts'] if f.get('basis')=='observed_profile']
        self.assertEqual(len(observed),6)
        self.assertEqual({f['year'] for f in observed},{2019,2024})
        formulas=[f for f in result['facts'] if 'formula' in f]
        self.assertTrue(formulas)
        self.assertTrue(all(f['basis']=='VP2019_BASE_to_2040_P1' for f in formulas))

    def test_missing_profile_year_does_not_become_zero(self):
        params={'region':'DEA12','year':2099,'metric':'tonnes','include_forecast':False}
        result,_=self.service.analyze('Duisburg',params,function='region_profile')
        self.assertEqual(result['status'],'not_available')
        self.assertEqual(result['facts'],[])

    def test_real_http_and_one_charge(self):
        class Quiet(WSGIRequestHandler):
            def log_message(self,*args): pass
        with tempfile.TemporaryDirectory(prefix='assistant-http-',dir='C:/tmp') as folder:
            quota=LocalQuota(Path(folder)/'quota.sqlite')
            quota.grant('http-test','basic')
            app=Application(self.service,quota,lambda env:'http-test' if env.get('HTTP_AUTHORIZATION')=='Bearer synthetic-test-token' else None,
                            allowed_origin='pending')
            server=make_server('127.0.0.1',0,app,handler_class=Quiet)
            origin=f'http://127.0.0.1:{server.server_port}'
            app.allowed_origin=origin
            thread=threading.Thread(target=server.serve_forever,daemon=True)
            thread.start()
            try:
                body=json.dumps({'question':'Duisburg','confirmed':PARAMETERS,'function':'balance','request_id':'http-test-001'}).encode()
                def request(token):
                    req=Request(origin+'/api/analyseassistent',data=body,headers={'Content-Type':'application/json','Origin':origin,'Authorization':token})
                    try:
                        with urlopen(req,timeout=30) as response: return response.status,json.load(response)
                    except HTTPError as exc: return exc.code,json.load(exc)
                self.assertEqual(request('')[0],401)
                status,result=request('Bearer synthetic-test-token')
                self.assertEqual(status,200)
                self.assertEqual(result['status'],'ok')
                self.assertEqual(quota.status('http-test')['used'],1)
                self.assertEqual(request('Bearer synthetic-test-token')[0],409)
                self.assertEqual(quota.status('http-test')['used'],1)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_national_incomplete_denominator(self):
        result, _ = self.service.analyze('Deutschland 2024 tkm', {'year':2024,'metric':'tkm','mode':None}, function='national')
        self.assertEqual(result['status'], 'partial')
        self.assertTrue(all(f['value'] is None for f in result['facts'] if f['unit']=='%'))

    def test_b07_prior_year_missing(self):
        result, _ = self.service.analyze('Berlin Juli 2026', {'ags':'11000000','month':'2026-07','comparison_month':'2025-07'}, function='toll_month')
        self.assertEqual(result['status'], 'partial')
        self.assertTrue(any('Vorjahresmonatspaar' in s for s in result['notices']))

    def test_invalid_answer_cannot_replace_facts(self):
        result, _ = self.service.analyze('Duisburg', PARAMETERS, function='balance')
        selection={'result_id':result['result_id'],'data_snapshot_id':result['data_snapshot_id'],
                   'paragraphs':[{'text':'Unbelegte Aussage.','statement_ids':['invented']}],
                   'table_ids':[],'wording_variant':'compact'}
        with self.assertRaises(ValueError):
            apply_selection(result, selection)
        evidence=result['statements'][0]
        selection['paragraphs']=[{'text':evidence['text'],'statement_ids':[evidence['id']]}]
        selected=apply_selection(result, selection)
        self.assertEqual(selected['tables'], result['tables'])
        self.assertEqual(selected['notices'], result['notices'])
        selection['paragraphs']=[{'text':'Zusätzlich 999 Tonnen.','statement_ids':[evidence['id']]}]
        with self.assertRaises(ValueError):
            apply_selection(result, selection)
        selection['paragraphs']=[{'text':evidence['text'].replace('Mio. Tonnen','Tonnen'),'statement_ids':[evidence['id']]}]
        with self.assertRaises(ValueError):
            apply_selection(result, selection)
        selection['paragraphs']=[{'text':'Die Werte belegen eine hervorragende wirtschaftliche Anbindung.','statement_ids':[evidence['id']]}]
        with self.assertRaises(ValueError):
            apply_selection(result, selection)

    def test_model_two_phases_load_prompt_and_no_references(self):
        class Fake:
            def __init__(self): self.calls=[]
            def complete(self, prompt, payload, schema, *, deadline):
                self.calls.append((prompt,payload))
                if payload['phase']=='plan': return plan(), {'model':'synthetic-test'}
                return {'result_id':payload['result_id'],'data_snapshot_id':payload['data_snapshot_id'],
                        'paragraphs':[{'text':'Der aktuelle Beleg lautet: {{f1}}.', 'evidence_ids':['f1']}]}, {'model':'synthetic-test'}
        model=Fake()
        result,_=Service(self.datasets,model).analyze('Duisburg',PARAMETERS)
        self.assertEqual(len(model.calls),2)
        self.assertEqual(model.calls[1][1]['question'],'Duisburg')
        self.assertIn('f1',model.calls[1][1]['evidence'])
        self.assertIn('relation_years_by_mode',model.calls[0][1]['availability'])
        self.assertTrue(all(prompt==self.service.prompt for prompt,_ in model.calls))
        self.assertEqual(result['answer_mode'],'grounded_narrative')
        self.assertFalse(any(key in json.dumps(model.calls) for key in ['control','last_terra_assessment','references.json']))

    def test_failed_optional_model_preserves_result(self):
        class Broken:
            def complete(self,*args,**kwargs): raise ModelError('synthetic failure')
        result,audit=Service(self.datasets,Broken()).analyze('Duisburg',PARAMETERS,function='balance')
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['answer_mode'],'fixed_verified')
        self.assertEqual(audit['attempted_model_calls'],1)
        self.assertEqual([f['value'] for f in result['facts']],[26371111,22134701,4236410])


class GuidedDialogue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.datasets=Datasets(ROOT)

    def initial(self):
        fake=MagicMock()
        fake.complete.return_value=(plan(function_id='rail_goods', parameters={'region':'DE300','partner':'DE600'},
            parameter_origins={'region':'question','partner':'question'}, unresolved_fields=['year'], status='needs_clarification'),{})
        service=Service(self.datasets,fake)
        first,_=service.analyze('Welche Güter gehen per Schiene von Berlin nach Hamburg?',select_answer=False)
        return service,first

    def test_signed_year_reverse_and_new_year_requery_real_data(self):
        service,first=self.initial()
        self.assertEqual(first['missing_fields'],['year'])
        latest,audit=service.analyze('Das aktuellste Jahr',conversation=first['conversation'],select_answer=False)
        self.assertEqual(latest['parameters']['year'],2025)
        self.assertEqual(audit['attempted_model_calls'],0)
        reverse,audit=service.analyze('Und in Gegenrichtung?',conversation=latest['conversation'],select_answer=False)
        self.assertEqual(reverse['parameters']['direction'],'inbound')
        self.assertEqual(audit['attempted_model_calls'],0)
        raw=self.datasets.query('rail_goods',reverse['parameters'])
        self.assertEqual(reverse['facts'][-1]['value'],raw['published_sum'])
        changed,_=service.analyze('Und 2024?',conversation=reverse['conversation'],select_answer=False)
        self.assertEqual(changed['parameters']['year'],2024)
        self.assertEqual(changed['parameters']['direction'],'inbound')
        self.assertEqual(changed['conversation_state']['initial_question'],first['conversation_state']['initial_question'])

    def test_forged_state_and_snapshot_are_rejected(self):
        from server.analyseassistent.conversation import unpack,pack
        service,first=self.initial()
        with self.assertRaises(ValueError):service.analyze('2024',conversation=first['conversation']+'x')
        state=unpack(first['conversation'],service.conversation_key,self.datasets.snapshot_id)
        state['snapshot']='forged'
        with self.assertRaises(ValueError): service.analyze('2024',conversation=pack(state,service.conversation_key))
        self.assertNotIn('facts',state['last_result'])

    def test_independent_topic_does_not_inherit_old_places_or_year(self):
        from server.analyseassistent.conversation import resume,unpack
        service,first=self.initial()
        state=unpack(first['conversation'],service.conversation_key,self.datasets.snapshot_id)
        for text in ['Wie entwickelt sich die Luftfracht?', 'Wie hoch sind die nationalen Mengen 2024?', 'Welche Güter gehen von Köln nach Hamburg?']:
            effective,confirmed,function,transition=resume(text,state,self.datasets)
            self.assertEqual((effective,confirmed,function,transition),(text,{},None,'new_topic'))

    def test_gap_and_alternative_are_queried_and_not_zero(self):
        service=Service(self.datasets)
        params={'year':2024,'origin':'DEA23','destination':'DE600','mode':'iww','group':'ALL','metric':'tonnes'}
        result,_=service.analyze('Köln Hamburg',params,function='relation')
        self.assertEqual(result['source_status'],'missing_row')
        self.assertIsNone(result['facts'][0]['value'])
        self.assertIn('keinen veröffentlichten Eintrag',result['answer']['paragraphs'][0])
        self.assertTrue(result['answer']['followups'])
        for item in result['answer']['followups']:
            self.assertIsNotNone(self.datasets.query(item['function_id'],item['parameters'])['value'])

    def test_narrative_cannot_insert_numbers_causes_or_foreign_evidence(self):
        from server.analyseassistent.narrative import apply_narrative,evidence
        service=Service(self.datasets)
        result,_=service.analyze('Duisburg',PARAMETERS,function='balance')
        records=evidence(result,result['answer'])
        for text,ids in [('Ergebnis: 999 Tonnen {{f1}}',['f1']),('Aufgrund guter Kapazität: {{f1}}',['f1']),('{{f999}}',['f999'])]:
            payload={'result_id':result['result_id'],'data_snapshot_id':result['data_snapshot_id'],'paragraphs':[{'text':text,'evidence_ids':ids}]}
            with self.assertRaises(ValueError):apply_narrative(result,result['answer'],payload,records)


if __name__=='__main__': unittest.main()
