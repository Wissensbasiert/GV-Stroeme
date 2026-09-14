"""Originalfall Leipzig: vollständiger Auftrag, echte Werte und Fehlergrenzen."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from server.analyseassistent.datasets import Datasets
from server.analyseassistent.selection import resolve, SelectionError
from server.analyseassistent.results import make_result
from server.analyseassistent.presentation import present
from server.analyseassistent.chat import packet, check_prose
from server.analyseassistent.service import Service
from server.analyseassistent.support import goods_history


def intent(context='new',kind='unspecified',clarification='',**extra):
    return {'context':context,'clarification':clarification,'time':{'kind':kind,'count':0,**extra}}


class GoodsHistory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=Datasets(Path(__file__).resolve().parents[2])
        cls.params={'region':'DED52','start':2020,'end':2024,'modes':['road','rail','iww'],
                    'metric':'tonnes','directions':['outbound']}
        cls.raw=cls.data.query('goods_history',cls.params)

    def result(self):
        r=make_result('goods_history',self.params,self.raw,self.data,'0.4.2')
        r['answer']=present(r,self.data)
        return r

    def row(self,mode,year,group=None,unit='t'):
        return next(r for r in self.raw['observations'] if r['mode']==mode and r.get('year')==year and r.get('group')==group and r['unit']==unit)

    def test_real_endpoints_ranks_and_changes(self):
        self.assertEqual(self.row('road',2020,'1')['value'],5408617)
        self.assertEqual(self.row('road',2024,'1')['value'],6144747)
        self.assertEqual(self.row('rail',2024,'1')['value'],772173)
        self.assertEqual(self.row('road',2024,'1')['rank'],1)
        self.assertAlmostEqual(self.row('road',2024,'1','%')['value'],6144747/13295272*100)
        change=next(r for r in self.raw['observations'] if r['mode']=='road' and r.get('change')=='relative' and r.get('group') is None)
        self.assertAlmostEqual(change['value'],(13295272-13899892)/13899892*100)
        self.assertEqual({r['year'] for r in self.raw['observations'] if 'year' in r},set(range(2020,2025)))
        self.assertEqual({r['mode'] for r in self.raw['observations']},{'road','rail','iww'})

    def test_iww_groups_unknown_despite_zero_total(self):
        self.assertIsNone(self.row('iww',2024,'1')['value'])
        self.assertIsNone(self.row('iww',2024,'1','%')['value'])
        self.assertEqual(self.row('iww',2024)['value'],0)
        change=next(r for r in self.raw['observations'] if r['mode']=='iww' and r.get('change')=='relative' and r.get('group') is None)
        self.assertEqual(change['value_status'],'not_computable')
        self.assertEqual(self.raw['status'],'partial')

    def test_since_resolution_partial_region_and_new_topic(self):
        _,first,d,notes=resolve('goods_history',{'directions':['outbound'],'_dialogue':intent(kind='since_available',start_year=2020,clarification='Welches Leipzig?')},{},self.data)
        self.assertEqual(first['start'],2020)
        self.assertNotIn('end',first)
        old={'function_id':'goods_history','confirmed':first,'time_intent':d['time']}
        _,second,_,notes=resolve('goods_history',{'region':'DED52','modes':['road','rail','iww'],'_dialogue':intent('continue')},old,self.data)
        self.assertEqual((second['start'],second['end']),(2020,2024))
        self.assertEqual(second['directions'],['outbound'])
        self.assertIn('gemeinsamen Datenjahr',notes[0])
        _,new,_,_=resolve('goods_structure',{'region':'DE300','mode':'rail','_dialogue':intent()},old,self.data)
        self.assertNotIn('year',new)

    def test_explicit_year_replaces_since(self):
        old={'function_id':'goods_history','confirmed':self.params,'time_intent':{'kind':'since_available','count':0,'start_year':2020}}
        _,new,d,_=resolve('goods_structure',{'mode':'road','year':2022,'_dialogue':intent('continue','explicit')},old,self.data)
        self.assertEqual(new['year'],2022)
        self.assertEqual(new['region'],'DED52')
        self.assertEqual(d['time']['kind'],'explicit')

    def test_missing_end_year_not_replaced(self):
        p={**self.params,'end':2025,'modes':['road']}
        raw=self.data.query('goods_history',p)
        end=[r for r in raw['observations'] if r.get('year')==2025]
        self.assertTrue(all(r['value'] is None for r in end))
        self.assertTrue(all(r['value'] is None for r in raw['observations'] if r.get('change')))
        r=make_result('goods_history',p,raw,self.data,'0.4.2')
        self.assertIn('fehlender Randjahreswerte',' '.join(present(r,self.data)['paragraphs']))

    def test_invalid_since_period_and_dimensions(self):
        for args in [{'_dialogue':intent(kind='since_available')},
                     {'start':2020,'_dialogue':intent(kind='since_available',start_year=2020)},
                     {'start':2024,'end':2020},{'start':2010},{'modes':['air']},
                     {'directions':['all','outbound','inbound'],'start':2016}]:
            with self.subTest(args=args),self.assertRaises(SelectionError):
                resolve('goods_history',{**self.params,'_dialogue':intent(kind='explicit'),**args},{},self.data)

    def test_fallback_covers_all_modes_and_both_question_parts(self):
        r=self.result()
        self.assertEqual(len(r['answer']['paragraphs']),2)
        self.assertEqual(len([f for f in r['facts'] if not f.get('aggregate')]),273)
        self.assertIn('2020–2024',r['answer']['title'])
        self.assertIn('46,22 %',r['answer']['paragraphs'][1])
        self.assertIn('-4,35 %',r['answer']['paragraphs'][1])
        self.assertIn('772.173 Tonnen',r['answer']['paragraphs'][1])
        self.assertIn('Rangfolge ist nicht möglich',r['answer']['paragraphs'][1])
        self.assertTrue(r['answer']['paragraphs'][1].startswith('- '))
        self.assertTrue(r['answer']['tables'][0]['collapsed'])
        payload=packet(r,self.data)
        prose={'paragraphs':[{'text':text,'evidence_ids':['p'+str(i+1)]} for i,text in enumerate(r['answer']['paragraphs'])]}
        self.assertEqual(check_prose(prose,payload,r,self.data),r['answer']['paragraphs'])
        for short in [{'paragraphs':prose['paragraphs'][:1]},
                      {'paragraphs':[{'text':'Straße, Schiene und Binnenschiff: Die Tabelle enthält 2020 und 2024.','evidence_ids':['p1']}]}]:
            with self.assertRaises(ValueError): check_prose(short,payload,r,self.data)

    def test_missing_intermediate_year_stays_unknown(self):
        from server.analyseassistent.support import goods_structure
        def interrupted(con,dataset,**p):
            return {'status':'missing_year','observations':[]} if p['year']==2022 else goods_structure(con,dataset,**p)
        with patch('server.analyseassistent.support.goods_structure',side_effect=interrupted):
            raw=goods_history(None,self.data.paths['assistant_support'],**{**self.params,'modes':['rail']})
        self.assertTrue(all(r['value'] is None for r in raw['observations'] if r.get('year')==2022))
        self.assertEqual(raw['status'],'partial')
        self.assertTrue(any(r['value'] is not None for r in raw['observations'] if r.get('change')))

    def test_signed_dialogue_and_brief_model_answer_fall_back(self):
        class Model:
            native_tools=True
            first=True
            def chat(model,messages,**options):
                if options.get('tools'):
                    args={'directions':['outbound'],'_dialogue':intent(kind='since_available',start_year=2020,clarification='Stadt Leipzig oder Landkreis Leipzig?')} if model.first else {'region':'DED52','modes':['road','rail','iww'],'_dialogue':intent('continue')}
                    model.first=False
                    return {'role':'assistant','tool_calls':[{'id':'a','type':'function','function':{'name':'goods_history','arguments':json.dumps(args)}}]},{}
                return {'role':'assistant','content':json.dumps({'paragraphs':[{'text':'Die Ergebnisse stehen in der Tabelle.','evidence_ids':['p1']}]})},{}
        service=Service(self.data,Model())
        first,_=service.analyze('Welche Güter werden in meinem Kreis Leipzig am meisten versandt? Wie hat sich das seit 2020 entwickelt?')
        self.assertEqual(first['status'],'needs_clarification')
        with patch.object(self.data,'query',wraps=self.data.query) as query:
            second,audit=service.analyze('Landkreis Leipzig und alle Verkehrsträger',conversation=first['conversation'])
        query.assert_called_once()
        self.assertEqual(second['parameters'],{**self.params,'partner_scope':'all'})
        self.assertEqual(second['answer_mode'],'verified_fallback')
        self.assertEqual(len(second['answer']['paragraphs']),2)
        self.assertIn('narrative_error',audit)

    def test_confirmed_district_is_not_confused_with_shared_city_alias(self):
        from server.analyseassistent.contracts import explicit_conflict
        for text in ['Im Landkreis Leipzig','Für Leipzig','Im Kreis Leipzig']:
            self.assertFalse(explicit_conflict(text,self.params,self.data.names))
        for text in ['In der kreisfreien Stadt Leipzig','In der Stadt Leipzig','Leipzig, Kreisfreie Stadt','DED51']:
            self.assertTrue(explicit_conflict(text,self.params,self.data.names))

    def test_concise_bullets_remain_valid_for_district_alias(self):
        r=self.result()
        prose={'paragraphs':[{'text':'Für den Landkreis Leipzig: '+r['answer']['paragraphs'][0], 'evidence_ids':['p1']},
                              {'text':r['answer']['paragraphs'][1],'evidence_ids':['p2']}]}
        self.assertEqual(len(check_prose(prose,packet(r,self.data),r,self.data)),2)


if __name__=='__main__': unittest.main()
