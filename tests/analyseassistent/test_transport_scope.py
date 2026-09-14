"""Originaldialoge: Gegenraum erhalten, Modalgesamtsumme und knappe Antwort."""
import csv
import math
from pathlib import Path
import unittest
from unittest.mock import patch
from server.analyseassistent.datasets import Datasets
from server.analyseassistent.results import make_result
from server.analyseassistent.presentation import present
from server.analyseassistent.selection import resolve, SelectionError
from server.analyseassistent.chat import packet, check_prose
from server.analyseassistent.transport import add_modal_sums

ROOT=Path(__file__).resolve().parents[2]


def intent(scope='inherit', context='new', kind='unspecified', count=0):
    return {'context':context,'clarification':'','geographic_scope':scope,'time':{'kind':kind,'count':count}}


class TransportScope(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.data=Datasets(ROOT)

    def query(self,**extra):
        p=dict(region='DE300',start=2020,end=2024,modes=['road','rail','iww'],metric='tonnes',direction='all',partner_scope='all')
        p.update(extra)
        r=make_result('transport_history',p,self.data.query('transport_history',p),self.data,'0.6.0')
        r['answer']=present(r,self.data)
        return r

    def goods(self,scope,direction='outbound',mode='iww'):
        return self.data.query('goods_structure',dict(region='DEA12',year=2025,mode=mode,metric='tonnes',directions=[direction],granularity='C7',partner_scope=scope))

    def test_duisburg_against_original_country_field(self):
        total=0.; groups={str(g):0. for g in range(1,8)}
        mapping={n:('1' if n<=3 else '2' if n<=6 else '3' if n<=9 else '4' if n==10 else '5' if n<=13 else '6' if n==14 else '7') for n in range(1,21)}
        with (ROOT/'data/raw/IWW OpenData/IWW_OpenData_2025.csv').open(encoding='utf-8',newline='') as handle:
            for row in csv.DictReader(handle,delimiter=';'):
                if row['Einladeregion_NUTS3']=='DEA12' and row['Ausladeregion_ISO'] and row['Ausladeregion_ISO']!='DE':
                    value=float(row['Tonnen'].replace(',','.')); total+=value
                    groups[mapping[int(row['NST2007'].zfill(3)[:2])]]+=value
        raw=self.goods('international')
        self.assertAlmostEqual(total,5915781.2,places=5)
        self.assertAlmostEqual(raw['observations'][-1]['value'],total,places=5)
        for row in raw['observations']:
            if row.get('group') and row.get('unit')!='%':self.assertAlmostEqual(row['value'],groups[row['group']],places=5)
        self.assertEqual(raw['observations'][0]['group'],'7')

    def test_domestic_foreign_partition_outbound(self):
        total=lambda scope:self.goods(scope)['observations'][-1]['value']
        self.assertAlmostEqual(total('domestic'),2373211.2,places=5)
        self.assertAlmostEqual(total('domestic')+total('international'),total('all'),places=5)

    def test_inbound_foreign_and_road_goods_limit(self):
        raw=self.goods('international','inbound')
        self.assertGreater(raw['observations'][-1]['value'],0)
        self.assertEqual(self.goods('international',mode='road')['status'],'not_available')

    def test_clarification_and_domestic_followup(self):
        _,p,_,_=resolve('goods_structure',{'region':'DEA12','mode':'iww','directions':['outbound'],'_dialogue':intent('international')},{},self.data)
        self.assertNotIn('year',p); self.assertEqual(p['partner_scope'],'international')
        state={'function_id':'goods_structure','confirmed':p}
        _,p,_,_=resolve('goods_structure',{'year':2025,'_dialogue':intent(context='continue',kind='explicit')},state,self.data)
        self.assertEqual(p['partner_scope'],'international')
        _,p,_,_=resolve('goods_structure',{'_dialogue':intent('domestic',context='continue')},{'function_id':'goods_structure','confirmed':p},self.data)
        self.assertEqual(p['partner_scope'],'domestic');self.assertEqual(p['year'],2025)

    def test_scope_cannot_disappear_on_tool_switch(self):
        old={'function_id':'goods_structure','confirmed':{'region':'DEA12','partner_scope':'international'}}
        with self.assertRaises(SelectionError):resolve('region_profile',{'year':2025,'_dialogue':intent(context='continue')},old,self.data)
        with self.assertRaises(SelectionError):resolve('region_profile',{'_dialogue':intent('international')},{},self.data)

    def test_five_calendar_years_and_explicit_followup(self):
        with patch('server.analyseassistent.selection.previous_calendar_year',return_value=2025):
            _,p,_,_=resolve('transport_history',{'region':'DE300','_dialogue':intent('all',kind='last_calendar_years',count=5)},{},self.data)
        self.assertEqual((p['start'],p['end']),(2021,2025))
        _,p,_,_=resolve('transport_history',{'start':2020,'end':2024,'_dialogue':intent(context='continue',kind='explicit')},{'function_id':'transport_history','confirmed':p},self.data)
        self.assertEqual((p['start'],p['end']),(2020,2024));self.assertEqual(p['modes'],['road','rail','iww'])

    def test_named_domestic_pair_is_already_filtered(self):
        args=dict(origin='DEA12',destination='DEE03',year=2024,_dialogue=intent('domestic'))
        name,p,_,_=resolve('relation_overview',args,{},self.data)
        self.assertEqual(name,'relation_overview');self.assertEqual(p['destination'],'DEE03')
        args['_dialogue']=intent('international')
        with self.assertRaises(SelectionError):resolve('relation_overview',args,{},self.data)

    def test_grouped_evidence_and_unicode_minus(self):
        r=self.query(); payload=packet(r,self.data)
        prose={'paragraphs':[{'text':'2020–2024: Die erfasste Gütermenge sank von 83,26 Mio. Tonnen auf 71,74 Mio. Tonnen (−13,83 %).','evidence_ids':['mode_group_total']},
            {'text':'- Straße: −13,88 %.\n- Schiene: −9,50 %.\n- Binnenschiff: −23,76 %.','evidence_ids':['mode_group_road','mode_group_rail','mode_group_iww']}]}
        self.assertEqual(len(check_prose(prose,payload,r,self.data)),2)
        prose['paragraphs'][0]['text']=prose['paragraphs'][0]['text'].replace('83,26','83,27')
        with self.assertRaises(ValueError):check_prose(prose,payload,r,self.data)

    def test_berlin_sum_change_and_short_visible_table(self):
        r=self.query(); totals=[f for f in r['facts'] if f.get('mode')=='total']
        self.assertEqual([f['value'] for f in totals if f.get('year')],[83255517.4,81891720.,80390334.,73057305.,71741627.])
        self.assertAlmostEqual(next(f['value'] for f in totals if f.get('change')=='relative'),-13.829582422365686)
        self.assertEqual(len(r['answer']['tables'][0]['rows']),5)
        self.assertFalse(r['answer']['tables'][0]['collapsed'])
        self.assertTrue(r['answer']['paragraphs'][1].startswith('- '))
        self.assertLess(len(r['facts']),35)
        payload=packet(r,self.data)
        check_prose({'paragraphs':[{'text':r['answer']['paragraphs'][0],'evidence_ids':['p1']},
                                   {'text':r['answer']['paragraphs'][1],'evidence_ids':['p2']}]},payload,r,self.data)

    def test_2025_partial_not_full_and_no_endpoint_substitution(self):
        r=self.query(start=2021,end=2025)
        total=next(f for f in r['facts'] if f.get('mode')=='total' and f.get('year')==2025)
        self.assertIsNone(total['value']);self.assertEqual(total['missing_modes'],['road'])
        self.assertIsNone(next(f['value'] for f in r['facts'] if f.get('mode')=='total' and f.get('change')=='relative'))
        subtotal=next(f for f in r['facts'] if f.get('aggregate')=='known_modal_subtotal')
        self.assertEqual(subtotal['components'],['rail','iww'])
        self.assertIn('Fehlt: Straße',r['answer']['tables'][0]['rows'][-1]['note'])

    def test_only_tonnes_aggregate_and_no_zero_invention(self):
        rows=[{'mode':'rail','value':2,'unit':'t','year':2024},{'mode':'iww','value':None,'unit':'t','year':2024}]
        add_modal_sums(rows,['rail','iww'],['year']);self.assertIsNone(rows[-2]['value']);self.assertEqual(rows[-1]['value'],2)
        r=self.query(metric='tkm');self.assertFalse(any(f.get('aggregate') for f in r['facts']))

    def test_overlapping_groups_not_added(self):
        rows=[{'mode':'rail','value':100,'unit':'t','group':'ALL'}, {'mode':'rail','value':70,'unit':'t','group':'4'}, {'mode':'iww','value':50,'unit':'t','group':'ALL'}]
        add_modal_sums(rows,['rail','iww'],['group']);self.assertEqual(rows[-1]['value'],150)

    def test_partner_ranking_foreign_excludes_domestic(self):
        p=dict(region='DEA12',year=2025,mode='iww',metric='tonnes',direction='outbound',group='ALL',top=100,external=False,partner_scope='international')
        r=self.data.query('partner_ranking',p)
        self.assertAlmostEqual(r['denominator'],5915781.2,places=5)
        self.assertTrue(all(not x['id'].startswith('DE') for x in r['observations']))


if __name__=='__main__':unittest.main()
