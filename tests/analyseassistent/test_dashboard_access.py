"""Quelltreuer Zusatz-Zugriff und Grenzen statt pauschaler Nichtverfügbarkeit."""
import json
from pathlib import Path
import unittest
from server.analyseassistent.datasets import Datasets, digest
from server.analyseassistent.contracts import FUNCTIONS, validate
from server.analyseassistent.selection import resolve, SelectionError
from server.analyseassistent.results import make_result
from server.analyseassistent.presentation import present
from server.analyseassistent.chat import packet, check_prose
from server.analyseassistent.access import read, field_access_inventory

ROOT=Path(__file__).resolve().parents[2]


def intent(context='new',kind='unspecified'):
    return {'context':context,'clarification':'','time':{'kind':kind,'count':0}}


class DashboardAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=Datasets(ROOT)

    def forecast(self,goods=['4'],**extra):
        p={'regions':['DE300'],'modes':['rail'],'metrics':['tonnes'],'direction':'outbound','goods':goods,**extra}
        r=make_result('forecast_regions',p,self.data.query('forecast_regions',p),self.data,'0.5.0')
        r['answer']=present(r,self.data)
        return r

    def detail(self,product,**extra):
        p={'product':product,'entity':'DE300','year':2024,'mode':'rail','metric':'tonnes','direction':'outbound',
           'classification':'NST20','group':'10','partner':None,'top':20,**extra}
        return self.data.query('dashboard_detail',p)

    def test_berlin_metals_actual_values_and_relative_change(self):
        r=self.forecast()
        self.assertEqual([f['value'] for f in r['facts'][:3]],[277,1531,1254])
        self.assertAlmostEqual(r['facts'][3]['value'],452.7075812274369)
        self.assertIn('Metalle',r['answer']['title']+' '.join(r['answer']['paragraphs']))
        self.assertIn('1.531',' '.join(r['answer']['paragraphs']))
        self.assertEqual(len(r['answer']['tables']),1)

    def test_vp100_and_c4_have_same_values_in_every_direction_and_mode(self):
        for direction in ['all','outbound','inbound']:
            for mode in ['road','rail','iww']:
                a=self.forecast(['4'],direction=direction,modes=[mode],metrics=['tonnes','tkm'])
                b=self.forecast(['VP100'],direction=direction,modes=[mode],metrics=['tonnes','tkm'])
                self.assertEqual([f['value'] for f in a['facts']],[f['value'] for f in b['facts']])

    def test_legacy_total_is_unchanged(self):
        p={'regions':['DE300'],'modes':['rail'],'metrics':['tonnes'],'direction':'outbound'}
        r=self.data.query('forecast_regions',p)
        self.assertEqual([f['value'] for f in r['observations'][:3]],[970375,1265924,295549])

    def test_groups_have_separate_bundles_and_tables(self):
        r=self.forecast(['3','4'],metrics=['tonnes','tkm'])
        self.assertEqual(len(r['facts']),16)
        bundles=[v for k,v in packet(r,self.data)['evidence'].items() if k.startswith('forecast_group_')]
        self.assertEqual(len(bundles),4)
        self.assertTrue(all(len(v['fact_ids'])==4 for v in bundles))
        self.assertEqual(len(r['answer']['tables']),2)

    def test_followup_keeps_goods_mode_and_region(self):
        state={'function_id':'forecast_regions','confirmed':self.forecast()['parameters']}
        _,p,_,_=resolve('forecast_regions',{'direction':'inbound','_dialogue':intent('continue')},state,self.data)
        self.assertEqual(p['goods'],['4'])
        self.assertEqual(p['regions'],['DE300'])
        self.assertEqual(p['direction'],'inbound')
        _,new,_,_=resolve('forecast_regions',{'regions':['DEA12'],'_dialogue':intent()},state,self.data)
        self.assertNotIn('goods',new)

    def test_overlap_unknown_groups_and_size_are_rejected(self):
        for goods in [['ALL','4'],['4','VP100'],['VP999'],['4','4']]:
            with self.subTest(goods=goods),self.assertRaises(SelectionError):
                resolve('forecast_regions',{'regions':['DE300'],'goods':goods,'_dialogue':intent()},{},self.data)

    def test_false_missing_goods_claim_is_rejected(self):
        r=self.forecast();p=packet(r,self.data)
        with self.assertRaises(ValueError):
            check_prose({'paragraphs':[{'text':'Für die Prognose liegt keine Aufteilung nach Gütergruppen vor.','evidence_ids':['f1']}]},p,r,self.data)

    def test_rail_and_iww_nst20_profiles(self):
        self.assertEqual(self.detail('regional_goods')['observations'][0]['value'],557)
        self.assertEqual(self.detail('regional_goods',mode='iww')['observations'][0]['value'],355)

    def test_missing_nst_group_is_unknown_not_zero(self):
        raw=self.detail('regional_goods',group='20')
        self.assertIsNone(raw['observations'][0]['value'])
        self.assertEqual(raw['status'],'partial')

    def test_road_nst3_does_not_get_artificial_nst20(self):
        raw=self.detail('regional_goods',mode='road')
        self.assertEqual(raw['status'],'not_available')
        self.assertEqual(raw['observations'],[])

    def test_leading_zero_codes_remain_text(self):
        raw=self.detail('regional_goods',group='01')
        self.assertEqual(raw['observations'][0]['group'],'01')
        self.assertEqual(raw['observations'][0]['value'],116)

    def test_hamburg_sea_metals_nst20(self):
        raw=self.detail('sea_goods',entity='DEHAM',mode='sea')
        self.assertAlmostEqual(raw['observations'][0]['value'],2485916.2)

    def test_hamburg_sea_partner_goods_filter(self):
        raw=self.detail('sea_partners',entity='DEHAM',mode='sea',classification='C7',group='4',partner='CN')
        self.assertEqual(raw['observations'][0]['value'],291435)
        self.assertIn('keine vollständige',raw['note'])

    def test_national_kv_container_structure(self):
        raw=self.detail('kv_structure',entity='DE',classification='C7',group='ALL',direction='all')
        self.assertEqual(raw['observations'][0]['value'],68294220)
        raw=self.detail('kv_structure',entity='DE',mode='iww',classification='C7',group='ALL',direction='all')
        self.assertAlmostEqual(raw['observations'][0]['value'],5544856.9)
        self.assertIn('nicht addieren',raw['note'])

    def test_kv_relations_are_bounded_and_directed(self):
        raw=self.detail('kv_relations',classification='C7',group='ALL',partner='DE600')
        self.assertTrue(all(r['origin']=='DE300' and r['destination']=='DE600' for r in raw['observations']))
        self.assertIn('keine Vollständigkeitsbehauptung',raw['note'])

    def test_forecast_relation_uses_complete_matrix_not_top25(self):
        p={'origin':'DE300','destination':'DE600','modes':['rail'],'metrics':['tonnes','tkm'],'goods':['ALL']}
        raw=self.data.query('forecast_relation',p)
        self.assertEqual(len(raw['observations']),8)
        self.assertTrue(all(r['origin']=='DE300' and r['destination']=='DE600' for r in raw['observations']))
        self.assertIn('keine Toplistenbegrenzung',raw['note'])
        r=make_result('forecast_relation',p,raw,self.data,'0.5.0');r['answer']=present(r,self.data)
        self.assertTrue(r['answer']['tables'])

    def test_forecast_missing_relation_does_not_become_zero(self):
        p={'origin':'DE300','destination':'DE600','modes':['iww'],'metrics':['tonnes'],'goods':['VP100']}
        raw=self.data.query('forecast_relation',p)
        for r in raw['observations']:
            if r['value'] is None:self.assertIn(r['value_status'],{'missing_row','missing_value','not_computable'})

    def test_road_trips_profile(self):
        raw=self.detail('regional_trips',mode='road',metric='trips',direction='all',group='ALL')
        self.assertEqual(raw['observations'][0]['value'],6729604)

    def test_forecast_kv_and_container_types_are_available(self):
        for product in ['forecast_kv','forecast_container_types']:
            raw=self.detail(product,year=2040,classification='C7',group='ALL',direction='all')
            self.assertTrue(raw['observations'])
            self.assertTrue(all(r['value_status']=='forecast' for r in raw['observations']))

    def test_source_package_and_coverage_bind_every_tool(self):
        path=self.data.paths['dashboard_access']
        report=read(path,'validation.json')
        self.assertTrue(report['passed'])
        self.assertGreater(report['checked_cells'],150000)
        coverage=read(path,'coverage.json')
        for entry in coverage.values():
            if 'tool' in entry:self.assertIn(entry['tool'],FUNCTIONS)
            if 'product' in entry:self.assertIn(entry['product'],FUNCTIONS[entry['tool']][3]['properties']['product']['enum'])
        for name,source in [('sea.json','web_maritime.json'),('intermodal.json','web_intermodal.json')]:
            self.assertEqual(digest(path/name),digest(ROOT/'data/processed'/source))

    def test_latest_year_from_real_port_source(self):
        _,p,_,_=resolve('dashboard_detail',{'product':'sea_goods','entity':'DEHAM','mode':'sea','_dialogue':intent(kind='latest_available')},{},self.data)
        self.assertEqual(p['year'],2025)
        self.assertEqual(p['classification'],'C7')

    def test_field_access_inventory_fails_on_new_unmapped_field(self):
        source=read(ROOT/'data/processed','web_forecast_core.json')
        regional=read(ROOT/'data/processed','web_summary_by_region.json')
        sea=read(ROOT/'data/processed','web_maritime.json')
        kv=read(ROOT/'data/processed','web_intermodal.json')
        self.assertTrue(field_access_inventory(source,regional,sea,kv)['passed'])
        next(iter(regional.values()))[next(iter(next(iter(regional.values()))))]['new_unknown_metric']=1
        inventory=field_access_inventory(source,regional,sea,kv)
        self.assertFalse(inventory['passed'])
        self.assertIn('regional.new_unknown_metric',inventory['unmapped_fields'])

    def test_original_vp_all_includes_inbound(self):
        p=read(self.data.paths['dashboard_access'],'forecast_core.json')['scenarios']['2040_P1']['regions']['DE300']
        self.assertEqual(p['vp2040_groups_tonnes']['all']['100'],p['groups_7_tonnes']['all']['4'])
        self.assertEqual(p['vp2040_groups_tonnes']['all']['100'],2291943)

    def test_national_forecast_and_regional_nst_limits(self):
        r=self.forecast(['VP100'],regions=['DE'],direction='all')
        self.assertTrue(all(f['value'] is not None for f in r['facts']))
        with self.assertRaises(SelectionError):
            resolve('forecast_regions',{'regions':['DE'],'direction':'outbound','_dialogue':intent()},{},self.data)
        raw=self.detail('regional_goods',entity='DE',direction='all')
        self.assertTrue(raw['observations'][0]['value']>0)
        self.assertIn('Keine amtliche vollständige nationale Randsumme',raw['note'])

    def test_forecast_load_units_and_explicit_kv_filter(self):
        raw=self.detail('forecast_load_units',year=2040,metric='teu',classification='C7',group='ALL')
        self.assertIsNotNone(raw['observations'][0]['value'])
        self.assertIn('ohne zusätzlichen VerkArt-Filter',raw['note'])
        kv=self.detail('forecast_kv',year=2040,metric='teu',classification='C7',group='ALL')
        self.assertEqual(kv['status'],'available')
        self.assertTrue(kv['observations'][0]['value']<=raw['observations'][0]['value'])

    def test_sea_country_filter_resolves_actual_iso_code(self):
        _,p,_,_=resolve('dashboard_detail',{'product':'sea_partners','entity':'DEHAM','mode':'sea','year':2024,'group':'4','partner':'CN','direction':'outbound','_dialogue':intent()},{},self.data)
        self.assertEqual(self.data.query('dashboard_detail',p)['observations'][0]['value'],291435)

    def test_unavailable_partner_detail_is_not_silently_ignored(self):
        with self.assertRaises(SelectionError):
            resolve('dashboard_detail',{'product':'regional_goods','entity':'DE300','mode':'rail','year':2024,'group':'10','partner':'DE600','_dialogue':intent()},{},self.data)

    def test_original_forecast_foreign_cells_are_registered(self):
        self.assertEqual(self.data.forecast_cell_names['2100011'],'Kopenhagen')
        _,p,_,_=resolve('forecast_relation',{'origin':'DE300','destination':'2100011','modes':['rail'],'_dialogue':intent()},{},self.data)
        self.assertEqual(p['destination'],'2100011')
        with self.assertRaises(SelectionError):
            resolve('forecast_relation',{'origin':'DE','destination':'DE600','_dialogue':intent()},{},self.data)

    def test_nst_designation_is_evidence_not_an_invented_quantity(self):
        p={'product':'regional_goods','entity':'DE300','year':2024,'mode':'rail','metric':'tonnes','direction':'outbound','classification':'NST20','group':'10','partner':None,'top':10}
        r=make_result('dashboard_detail',p,self.data.query('dashboard_detail',p),self.data,'0.5.0');r['answer']=present(r,self.data)
        payload=packet(r,self.data)
        text='Im Jahr 2024 wurden in Berlin im Schienenversand in der NST-2007-Abteilung 10 (Metalle und Metallerzeugnisse) 557 Tonnen erfasst.'
        self.assertEqual(check_prose({'paragraphs':[{'text':text,'evidence_ids':['f1']}]},payload,r,self.data),[text])
        self.assertIn('NST-20 Abteilung 10',r['answer']['paragraphs'][0])
        with self.assertRaises(ValueError):
            check_prose({'paragraphs':[{'text':'Berlin versandte 2024 10 Tonnen.','evidence_ids':['f1']}]},payload,r,self.data)
        with self.assertRaises(ValueError):
            check_prose({'paragraphs':[{'text':'Im Jahr 2007 versandte Berlin 557 Tonnen.','evidence_ids':['f1']}]},payload,r,self.data)


if __name__=='__main__':unittest.main()
