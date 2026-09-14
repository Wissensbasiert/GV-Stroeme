"""Prüft den aktiven Testrelease über eine kurzlebige AlwaysData-Aufgabe.

Fach- und Datenbankzugriffe sind lesend; temporäre Aufgabe, FTPS-Zugang und
Statusdatei werden wieder entfernt. Modellaufrufe nur mit --requesty;
keine Rechteänderung und keine Buchung auf einem Kundenkonto.
"""
import argparse
import ftplib
import hashlib
import io
import json
import os
from pathlib import Path
import secrets
import shlex
import ssl
import sys
import time


REMOTE = r'''
import hashlib,json,sys,platform,importlib.metadata,os
from pathlib import Path
root=Path(sys.argv[1]); status=Path(sys.argv[2]); expected=sys.argv[3]
# Scheduled tasks can overlap on a slow provider response. Only the first
# invocation may inspect data or make a paid model call.
try:
    with status.with_suffix('.started').open('x',encoding='utf-8') as marker:
        marker.write('started\n')
except FileExistsError:
    raise SystemExit(0)
report={'passed':False,'external_model_calls':0,'database_writes':0}
try:
    report['stage']='manifest'
    manifest=root/'MANIFEST.sha256.json'
    assert hashlib.sha256(manifest.read_bytes()).hexdigest()==expected
    files=json.loads(manifest.read_text(encoding='utf-8'))
    for name,entry in files.items():
        target=(root/name).resolve()
        assert target.is_relative_to(root.resolve())
        assert target.stat().st_size==entry['bytes']
        assert hashlib.sha256(target.read_bytes()).hexdigest()==entry['sha256']
    report['stage']='private_runtime'
    private=root/'private/gueterstroeme'
    sys.path.insert(0,str(private))
    sys.path.insert(0,str(root/'alwaysdata_portal'))
    from server.analyseassistent.datasets import Datasets
    from server.analyseassistent.service import Service
    datasets=Datasets(private)
    result,audit=Service(datasets).analyze('Welche Güter werden von Köln nach Hamburg auf der Straße transportiert?',{'origin':'DEA23','destination':'DE600','year':2024,'metric':'tonnes'},function='road_relation_goods_limit')
    assert result['facts'][0]['value']==67757
    assert len(result['answer']['followups'])==3
    assert audit['attempted_model_calls']==0
    if (private/'config/analyseassistent/DARSTELLUNGSREFERENZEN.json').exists():
        from server.analyseassistent.contracts import verify_plan
        parameters={'origin':'DEA23','destination':'DE600','year':2024,'metric':'tonnes'}
        plan={'phase':'plan','function_id':'road_relation_goods_limit','parameters':parameters,
              'parameter_origins':{k:'question' for k in parameters},'unresolved_fields':[],'status':'ready'}
        assert verify_plan(plan,'Wie viele Tonnen wurden 2024 von Köln nach Hamburg transportiert?',{},datasets.names)
        airport,_=Service(datasets).analyze('Flughafenpartner',
            {'kind':'air','node':'EDDP','year':2024,'direction':'outbound','metric':'tonnes','international':True,'top':5},function='node_partners')
        assert airport['facts'][0]['label']=='East Midlands Airport' and airport['facts'][0]['value']==50109
        assert abs(airport['facts'][1]['denominator']-662332)<1e-7
        explanation,_=Service(datasets).analyze('Gebietssumme',{'topic':'regional_vs_national'},function='explain_scope')
        scope_example=next(f['evidence'] for f in explanation['text_facts'] if f.get('evidence'))
        assert scope_example['year']==2024 and scope_example['entry_count']==422
        assert scope_example['district_count']==400 and len(scope_example['other_codes'])==22
        assert not explanation['facts']
        report['response_corrections']={'natural_direction_verified':True,'airport_names_and_values_verified':True,
            'regional_scope_2024_verified':True,'external_model_calls':0}
    if (private/'server/analyseassistent/dialogue.py').exists():
        class DialogueModel:
            def complete(self,*args,**kwargs):
                return {'phase':'plan','function_id':'rail_goods','parameters':{'region':'DE300','partner':'DE600'},
                    'parameter_origins':{'region':'question','partner':'question'},'unresolved_fields':['year','direction','metric','group','nst'],
                    'status':'needs_clarification'},{}
        dialogue_service=Service(datasets,model=DialogueModel())
        initial='Welche Güter gehen per Schiene von Berlin nach Hamburg?'
        first,_=dialogue_service.analyze(initial,select_answer=False)
        assert first['missing_fields']==['year'] and first['answer']['replies'][0]['question']=='2025'
        followup,_=dialogue_service.analyze('Das aktuellste Jahr',history=[initial],select_answer=False)
        assert followup['status']=='ok' and followup['parameters']['year']==2025
        assert followup['parameters']['direction']=='outbound' and followup['parameters']['partner']=='DE600'
        assert followup['facts'][-1]['value']==240297
        report['dialogue_verified']={'year_only_clarification':True,'latest_year':2025,'short_reply_uses_history':True,
            'published_rail_tonnes':240297,'model':'synthetic_plan_with_actual_data','external_model_calls':0}
        if (private/'server/analyseassistent/conversation.py').exists():
            latest,_=dialogue_service.analyze('Das aktuellste Jahr',conversation=first['conversation'],select_answer=False)
            reverse,reverse_audit=dialogue_service.analyze('Und in Gegenrichtung?',conversation=latest['conversation'],select_answer=False)
            assert reverse['parameters']['direction']=='inbound' and reverse['facts'][-1]['value']==585052
            assert reverse_audit['attempted_model_calls']==0
            gap,_=dialogue_service.analyze('Welche Güter gehen 2026 per Schiene von Berlin nach Hamburg?',select_answer=False)
            assert gap['status']=='not_available' and gap['answer']['followups'][0]['parameters']['year']==2025
            report['guided_dialogue_verified']={'signed_context':True,'reverse_2025_tonnes':585052,'gap_2026_alternative_2025':True}
            report['configured_model']=os.environ.get('REQUESTY_MODEL')
            assert report['configured_model']=='vertex/gemini-3.7-flash@eu'
            relation_question='Wie viel Güter sind in den letzten Jahren von Rosenheim nach Augsburg transportiert worden?'
            report['stage']='published_growth'
            relation,relation_audit=Service(datasets).analyze(relation_question,select_answer=False)
            assert relation['function_id']=='relation_history'
            assert relation['parameters']=={'origin':'DE213','destination':'DE271','metric':'tonnes',
                'modes':['road','rail','iww'],'start':2020,'end':2024}
            assert relation_audit['attempted_model_calls']==0
            assert any('rechnerischen Rückgang um 50,99 %' in paragraph for paragraph in relation['answer']['paragraphs'])
            assert any('kein nutzbarer Güterverkehrswert erfasst beziehungsweise veröffentlicht' in paragraph
                for paragraph in relation['answer']['paragraphs'])
            # The customer correction removed a duplicated generic note. Verify
            # the underlying missing values and endpoint calculation directly.
            assert all(f['value'] is None for f in relation['facts'] if f.get('mode') in {'road','iww'})
            rail_values={f['year']:f['value'] for f in relation['facts'] if f.get('mode')=='rail'}
            assert rail_values[2020]==2175 and rail_values[2024]==1066
            assert round((rail_values[2020]-rail_values[2024])/rail_values[2020]*100,2)==50.99
            report['published_growth_verified']={'question':relation_question,'start_year':2020,'end_year':2024,
                'rail_start_tonnes':2175,'rail_end_tonnes':1066,'calculated_decline_percent':50.99,
                'missing_values_not_treated_as_zero':True,'external_model_calls':0}
            from server.analyseassistent.dialogue import previous_calendar_year
            followup_service=Service(datasets)
            token=None
            turns=[]
            questions=['Was für Güter wurden letztes Jahr von Köln nach Düsseldorf transportiert und wie viele?',
                'Kannst du mir auch die Verkehrsleistung nennen? Und was ist mit der Güterart?',
                'Ich meine weiterhin Köln nach Düsseldorf im letzten Jahr','2024']
            for index,question in enumerate(questions):
                checked,checked_audit=followup_service.analyze(question,conversation=token,select_answer=False)
                token=checked['conversation']
                p=checked['parameters']
                assert checked['status'] in {'ok','partial'} and checked['function_id']=='relation_overview'
                assert (p['origin'],p['destination'])==('DEA23','DEA11')
                assert p['year']==(2024 if index==3 else previous_calendar_year())
                assert p['metrics']==(['tonnes'] if index==0 else ['tonnes','tkm']) and p['include_goods']
                assert checked_audit['attempted_model_calls']==0
                turns.append({'parameters':p,'status':checked['status'],'transition':checked_audit['conversation_transition']})
            report['calendar_and_followups_verified']={'turns':turns,'external_model_calls':0}
    if (private/'server/analyseassistent/selection.py').exists():
        report['stage']='semantic_dialogue'
        class NativeModel:
            native_tools=True
            first=True
            def chat(self,messages,**options):
                if options.get('tools'):
                    parameters=({'origin':'DE136','destination':'DE600','_dialogue':{'context':'new',
                        'clarification':'Welchen Zeitraum möchten Sie betrachten?','time':{'kind':'unspecified','count':0}}}
                        if self.first else {'_dialogue':{'context':'continue','clarification':'',
                        'time':{'kind':'last_calendar_years','count':5}}})
                    name='relation_overview' if self.first else 'relation_history'
                    self.first=False
                    return {'role':'assistant','tool_calls':[{'id':'qa','type':'function','function':{
                        'name':name,'arguments':json.dumps(parameters)}}]},{}
                payload=json.loads(messages[-1]['content']); key=next(iter(payload['evidence']))
                return {'role':'assistant','content':json.dumps({'paragraphs':[{
                    'text':payload['evidence'][key]['text'],'evidence_ids':[key]}]})},{}
        semantic=Service(datasets,NativeModel())
        first,_=semantic.analyze('Welche Güter fließen vom Schwarzwald-Baar-Kreis Richtung Hamburg?')
        assert first['status']=='needs_clarification' and first['conversation_state']['confirmed']['origin']=='DE136'
        second,_=semantic.analyze('die letzten fünf Jahre',conversation=first['conversation'])
        assert second['status']=='not_available' and second['parameters']['start']==2021 and second['parameters']['end']==2025
        assert len(second['facts'])==15 and all(f['value'] is None for f in second['facts'])
        report['semantic_dialogue_verified']={'partial_selection_saved':True,'start':2021,'end':2025,
            'missing_values_remain_unknown':True,'external_model_calls':0}
    if sys.argv[4]=='requesty':
        report['stage']='requesty'
        from server.analyseassistent.requesty import Requesty
        question='Welche Güter wurden 2024 auf der Straße von Köln nach Hamburg transportiert? Bitte nach Güterarten aufschlüsseln.'
        confirmed={'origin':'DEA23','destination':'DE600','year':2024,'metric':'tonnes'}
        live,live_audit=Service(datasets,model=Requesty.from_environment()).analyze(question,confirmed)
        report['external_model_calls']=live_audit['attempted_model_calls']
        visible=['title','paragraphs','questions','tables','notes','sources','suggestions','followups']
        report['live_requesty']={'question':question,'confirmed':confirmed,
            'status':live['status'],'function_id':live.get('function_id'),
            'total_ms':live_audit['total_ms'],'prompt_sha256':live_audit['prompt_sha256'],
            'calls':[{**{k:call.get(k) for k in ['requested_model','model','elapsed_ms']},
                'usage':{k:v for k,v in (call.get('usage') or {}).items()
                         if k in ['prompt_tokens','completion_tokens','total_tokens','cost'] and type(v) in [int,float]}}
                for call in live_audit['model_calls']],
            'customer_answer':{k:live['answer'].get(k) for k in visible},
            'matches_local_t20':all(live['answer'].get(k)==result['answer'].get(k) for k in visible)}
        for key in ['model_error','model_error_diagnostics','answer_selection_error']:
            if key in live_audit:report['live_requesty'][key]=live_audit[key]
        assert live.get('function_id')=='road_relation_goods_limit'
        assert live.get('parameters')==confirmed and live['facts'][0]['value']==67757
        assert report['live_requesty']['matches_local_t20']
    report['stage']='database_read_only'
    from db import database_connection_parameters
    from auth import hanko_api_url
    import psycopg
    with psycopg.connect(connect_timeout=10,**database_connection_parameters()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SET TRANSACTION READ ONLY')
            cursor.execute("SELECT plan_code,monthly_limit FROM portal_tool_ai_plans WHERE tool_slug='gueterstroeme' ORDER BY plan_code")
            plans=dict(cursor.fetchall())
            assert plans=={'basic':5,'premium':50}
            cursor.execute("SELECT checksum FROM schema_migrations WHERE version='009_tool_ai_quotas.sql'")
            applied=cursor.fetchone()
            sql=root/'alwaysdata_portal/migrations/009_tool_ai_quotas.sql'
            assert applied and applied[0]==hashlib.sha256(sql.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
            cursor.execute("SELECT is_active FROM portal_tools WHERE slug='gueterstroeme'")
            tool_active=cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM portal_external_identities WHERE provider='hanko' AND issuer=%s",(hanko_api_url(),))
            report['matching_hanko_identities']=cursor.fetchone()[0]
    report.update(passed=True,stage='complete',manifest_sha256=expected,files_verified=len(files),python=platform.python_version(),system=platform.system(),versions={p:importlib.metadata.version(p) for p in ['duckdb','jsonschema','psycopg']},data_snapshot=datasets.snapshot_id,t20_road_tonnes=67757,followups=3,plans=plans,migration_009_verified=True,tool_active=tool_active)
except Exception as error:
    report['error_type']=type(error).__name__
temporary=status.with_suffix('.tmp')
temporary.write_text(json.dumps(report,ensure_ascii=False)+'\n',encoding='utf-8')
temporary.replace(status)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--portal', type=Path, required=True)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--requesty', action='store_true', help='Echter Modelltest mit bereits auf der Testsite hinterlegter Konfiguration')
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Neuer Prüfbericht erforderlich')
    sys.path.insert(0, str(args.portal.resolve()/'deployment/automation'))
    from deploy_alwaysdata_test import Api, collection_items, resource_id, job_resource_id
    release = args.release.resolve()
    if not release.name.startswith('portal-test-'):
        raise ValueError('Nur eindeutig benannter Testrelease zulässig')
    digest = hashlib.sha256((release/'MANIFEST.sha256.json').read_bytes()).hexdigest()
    api = Api(os.environ['ALWAYSDATA_API_TOKEN'])
    site = api.request('GET', '/site/1067000/')
    relative = 'portal_test/releases/'+release.name
    if ({str(address).rstrip('/') for address in site.get('addresses',[])} != {'test.portal.wissensbasiert.de'}
            or site.get('path') != relative+'/alwaysdata_portal/wsgi.py'
            or site.get('virtualenv_directory') != 'portal_test/.venv'):
        raise ValueError('Aktive Site entspricht nicht dem bestätigten Testrelease')
    marker = 'private/gueterstroeme/validation_'+secrets.token_hex(8)+'.json'
    remote = '/home/wbp-solutions/'+relative
    ftp_name = 'wbp-solutions_fqa_'+secrets.token_hex(4)
    ftp_password = secrets.token_urlsafe(32)
    annotation = 'temporary freight runtime QA '+release.name+' '+secrets.token_hex(4)
    ftp_id = job_id = None
    ftp = None
    result = None
    cleanup = {'job_removed':False,'ftp_removed':False,'status_removed':False,'lock_removed':False}
    try:
        created = api.request('POST','/ftp/',{'name':ftp_name,'password':ftp_password,'path':relative})
        ftp_id = resource_id(created,api.request('GET','/ftp/'),ftp_name)
        if ftp_id is None: raise RuntimeError('Temporärer FTPS-Zugang nicht auflösbar')
        ftp = ftplib.FTP_TLS(context=ssl.create_default_context())
        ftp.connect('ftp-wbp-solutions.alwaysdata.net',21,timeout=30)
        ftp.auth(); ftp.login(ftp_name,ftp_password); ftp.prot_p()
        users = collection_items(api.request('GET','/ssh/'))
        ssh_user = next(u['id'] for u in users if u.get('name')=='wbp-solutions')
        command = ' '.join(shlex.quote(p) for p in ['/home/wbp-solutions/portal_test/.venv/bin/python','-B','-c',REMOTE,remote,remote+'/'+marker,digest,'requesty' if args.requesty else 'no_model'])
        created = api.request('POST','/job/',{'type':'TYPE_COMMAND','date_type':'CRONTAB','crontab_syntax':'* * * * *','argument':command,'working_directory':relative,'environment':site['environment'],'ssh_user':ssh_user,'annotation':annotation})
        job_id = job_resource_id(created,api.request('GET','/job/'),annotation)
        if job_id is None: raise RuntimeError('Temporäre Prüfaufgabe nicht auflösbar')
        print('Temporäre Test-Laufzeitprüfung gestartet.',flush=True)
        for attempt in range(60):
            buffer=io.BytesIO()
            try:
                ftp.retrbinary('RETR '+marker,buffer.write)
                result=json.loads(buffer.getvalue().decode('utf-8'))
                break
            except ftplib.error_perm as error:
                if not str(error).startswith('550'): raise
            if attempt<59: time.sleep(5)
        if result is None: raise RuntimeError('Prüfaufgabe hat noch keinen Abschlussstatus geliefert')
    except Exception as error:
        result={'passed':False,'error_type':type(error).__name__,'external_model_calls':0,
                'temporary_job_id':job_id,'temporary_ftp_id':ftp_id}
    finally:
        if job_id is not None:
            try:
                api.request('DELETE',f'/job/{job_id}/')
                cleanup['job_removed']=all(j.get('id')!=job_id for j in collection_items(api.request('GET','/job/')))
            except Exception:
                cleanup['job_removed']=False
        if ftp is not None:
            try:
                if result is not None and 'temporary_job_id' not in result:
                    ftp.delete(marker)
                    cleanup['status_removed']=True
                    ftp.delete(str(Path(marker).with_suffix('.started')).replace('\\','/'))
                    cleanup['lock_removed']=True
                ftp.quit()
            except ftplib.all_errors: ftp.close()
        if ftp_id is not None:
            try:
                api.request('DELETE',f'/ftp/{ftp_id}/')
                cleanup['ftp_removed']=all(f.get('id')!=ftp_id for f in collection_items(api.request('GET','/ftp/')))
            except Exception:
                cleanup['ftp_removed']=False
    result.update(cleanup=cleanup,release=release.name,site_id=1067000,
                  verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    result['passed']=result.get('passed') is True and all(cleanup.values())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
