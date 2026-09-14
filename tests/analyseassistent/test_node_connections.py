"""Knoten, IATA/Stadtgruppe, Quellen, Folgefragen und gemeinsame Raumfilter."""
import csv
import json
from pathlib import Path
import tempfile
import unittest
import duckdb
from server.analyseassistent.datasets import Datasets
from server.analyseassistent.selection import resolve, SelectionError
from server.analyseassistent.results import make_result
from server.analyseassistent.presentation import present
from server.analyseassistent.chat import packet, check_prose
from server.analyseassistent.availability import catalog
from server.analyseassistent.contracts import FUNCTIONS
from server.analyseassistent.dialogue import available_years
from server.analyseassistent import nodes
from scripts.analysis import b0406

ROOT=Path(__file__).resolve().parents[2]


def intent(scope='inherit',context='new',kind='explicit'):
    return {'context':context,'clarification':'','geographic_scope':scope,'time':{'kind':kind,'count':0}}


class NodeConnections(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.data=Datasets(ROOT)

    def selection(self,**changes):
        args=dict(kind='air',node='LEJ',year=2024,direction='outbound',metric='flights',partner_group='london',_dialogue=intent('international'))
        args.update(changes)
        return resolve('node_connections',args,{},self.data)[1]

    def result(self,parameters=None,function='node_connections'):
        p=parameters or self.selection()
        result=make_result(function,p,self.data.query(function,p),self.data,'0.7.0')
        result['answer']=present(result,self.data)
        return result

    def test_unavailable_relation_year_explains_latest_without_zero_rows(self):
        for metric in ['tonnes', 'flights']:
            result = self.result(self.selection(year=2025, metric=metric))
            self.assertEqual(result['status'], 'not_available')
            self.assertEqual(result['facts'], [])
            text = ' '.join(result['answer']['paragraphs'])
            self.assertIn('2025', text)
            self.assertIn('2024', text)
            self.assertIn('keine Relationsdaten', text)
            payload = packet(result, self.data)
            checked = check_prose({'paragraphs': [{'text': 'Keine Angaben.', 'evidence_ids': ['q1']}]}, payload, result, self.data)
            self.assertEqual(checked, result['answer']['paragraphs'])

    def test_iata_aliases_are_from_original_reference(self):
        from scripts.analysis.build_assistant_references import build
        built=build(ROOT)
        self.assertEqual(built['airport_iata']['LEJ'],'EDDP')
        self.assertEqual(built['airport_iata']['LHR'],'EGLL')
        self.assertEqual(built['airport_iata']['BER'],'EDDB')
        self.assertEqual(built['airport_iata'],self.data.airport_iata)

    def test_london_group_and_missing_values(self):
        p=self.selection(); result=self.result(p)
        self.assertEqual(p['partners'],['EGGW','EGKK','EGLL','EGMC','EGSS'])
        values={f.get('partner_id'):f for f in result['facts'] if f.get('partner_id')}
        self.assertEqual(values['EGLL']['value'],66)
        self.assertEqual(values['EGKK']['value_status'],'missing_row')
        self.assertEqual(values['EGMC']['value_status'],'missing_value')
        self.assertIsNone(next(f['value'] for f in result['facts'] if f.get('aggregate_role')=='total'))
        self.assertEqual(next(f['value'] for f in result['facts'] if f.get('aggregate_role')=='subtotal'),994)
        self.assertTrue(any('Heathrow' in n and 'Gatwick' in n and 'Southend' in n for n in result['answer']['notes']))
        self.assertTrue(any('CAF_FRM' in n for n in result['answer']['notes']))
        self.assertEqual(result['status'],'partial')

    def test_single_iata_does_not_expand_city(self):
        args=dict(kind='air',node='LEJ',partners=['LHR'],year=2024,direction='outbound',metric='flights',_dialogue=intent('international'))
        p=resolve('node_connections',args,{},self.data)[1]
        self.assertEqual(p['partners'],['EGLL']);self.assertNotIn('partner_group',p)
        result=self.result(p)
        self.assertEqual([f['value'] for f in result['facts']],[66])
        self.assertIn('Heathrow',result['answer']['title'])
        self.assertNotIn('Zusammengefasst',' '.join(result['answer']['paragraphs']))

    def test_original_eurostat_cells(self):
        found={}
        with (ROOT/'data/raw/Luftverkehr/estat_avia_gor_de.tsv').open(encoding='utf-8-sig',newline='') as handle:
            rows=csv.reader(handle,delimiter='\t');header=next(rows)
            position=next(i for i,k in enumerate(header) if k.strip()=='2024')
            for row in rows:
                key=row[0]
                if key.startswith('A,FLIGHT,CAF_FRM_DEP,DE_EDDP_'):
                    for code in ['EGGW','EGLL','EGSS','EGMC']:
                        if key.endswith(code):found[code]=row[position].strip()
        self.assertEqual(found,{'EGGW':'438','EGLL':'66','EGSS':'490','EGMC':':'})

    def test_reverse_and_direct_followups(self):
        p=self.selection();state={'function_id':'node_connections','confirmed':p}
        reverse=resolve('node_connections',{'direction':'inbound','_dialogue':intent(context='continue',kind='unspecified')},state,self.data)[1]
        self.assertEqual(reverse['partners'],p['partners']);self.assertEqual(reverse['year'],2024)
        self.assertEqual(next(f['value'] for f in self.result(reverse)['facts'] if f.get('aggregate_role')=='subtotal'),634)
        direct=resolve('node_connections',{'_dialogue':intent(context='continue',kind='unspecified')},state,self.data)[1]
        self.assertEqual(direct,p)

    def test_single_partner_clears_inherited_group(self):
        p=resolve('node_connections',{'partners':['LHR'],'_dialogue':intent(context='continue',kind='unspecified')},
            {'function_id':'node_connections','confirmed':self.selection()},self.data)[1]
        self.assertNotIn('partner_group',p);self.assertEqual(p['partners'],['EGLL'])
        self.assertEqual(self.result(p)['facts'][0]['value'],66)

    def test_year_clarification_preserves_group(self):
        args=dict(kind='air',node='LEJ',partner_group='london',metric='flights',direction='outbound',_dialogue=intent('international',kind='unspecified'))
        p=resolve('node_connections',args,{},self.data)[1];self.assertNotIn('year',p)
        p=resolve('node_connections',{'year':2024,'_dialogue':intent(context='continue')},
            {'function_id':'node_connections','confirmed':p},self.data)[1]
        self.assertEqual(len(p['partners']),5);self.assertEqual(p['partner_scope'],'international')

    def test_no_silent_connection_loss(self):
        with self.assertRaises(SelectionError):
            resolve('node_statistics',{'_dialogue':intent(context='continue',kind='unspecified')},
                {'function_id':'node_connections','confirmed':self.selection()},self.data)

    def test_unknown_codes_wrong_unit_and_scope(self):
        for changes in [{'node':'ZZZZ'},{'partners':['ZZZZ'],'partner_group':None},{'metric':'teu'}, {'partner_scope':'domestic'}]:
            with self.subTest(changes=changes),self.assertRaises(SelectionError):self.selection(**changes)
        with self.assertRaises(SelectionError):self.selection(partners=['EGLL'])

    def test_catalog_matches_declared_filter_capabilities(self):
        expected={name for name,e in FUNCTIONS.items() if 'partner_scope' in e[3]['properties']}
        self.assertEqual(set(catalog(self.data)['geographic_scope']['tools']),expected)
        self.assertIn('node_connections',expected)

    def test_hamburg_preview_needs_only_the_year(self):
        p=resolve('partner_ranking',{'region':'DE600','mode':'road','_dialogue':intent(kind='unspecified')},{},self.data)[1]
        self.assertEqual([k for k in FUNCTIONS['partner_ranking'][3]['required'] if k not in p],['year'])
        self.assertEqual(p['direction'],'all');self.assertTrue(p['external']);self.assertEqual(p['top'],5)

    def test_preview_forecast_summary_respects_absolute_ranking(self):
        p=dict(mode='rail',metric='tonnes',direction='all',measure='absolute',top=5,descending=True)
        result=self.result(p,'forecast_ranking')
        first=min((f for f in result['facts'] if f['label'].endswith('/ Absolute Änderung')),key=lambda f:f['rank'])
        self.assertIn(first['fact_id'],result['statements'][0]['fact_ids'])
        self.assertIn('absoluter Mengenänderung',result['answer']['paragraphs'][0])
        self.assertEqual(len(packet(result,self.data)['evidence']['forecast_ranking_group']['fact_ids']),20)

    def test_air_rankings_preserve_legacy_values(self):
        p=dict(kind='air',node='EDDP',year=2024,metric='tonnes',direction='outbound',international=True,top=100)
        raw=self.data.query('node_partners',p)
        with duckdb.connect() as con:old=b0406.node_partners(con,self.data.paths['b0406'],**p)
        self.assertEqual([(r['id'],r['value']) for r in raw['rows']],[(r['id'],r['value']) for r in old['rows']])
        self.assertAlmostEqual(raw['denominator'],662332)

    def test_air_and_sea_scopes_and_followup(self):
        for kind,node in [('air','EDDP'),('sea','DEHAM')]:
            p=dict(kind=kind,node=node,year=2024,metric='tonnes',direction='outbound',top=5,international=True,_dialogue=intent('international'))
            p=resolve('node_partners',p,{},self.data)[1]
            self.assertEqual(p['partner_scope'],'international')
            self.assertTrue(all(r['partner_country']!='DE' for r in self.data.query('node_partners',p)['rows']))
            p=resolve('node_partners',{'_dialogue':intent('domestic','continue','unspecified')},
                {'function_id':'node_partners','confirmed':p},self.data)[1]
            self.assertFalse(p['international'])
            self.assertTrue(all(r['partner_country']=='DE' for r in self.data.query('node_partners',p)['rows']))

    def test_legacy_false_resets_foreign_filter(self):
        old={'function_id':'node_partners','confirmed':dict(kind='air',node='EDDP',year=2024,direction='outbound',metric='tonnes',top=5,international=True,partner_scope='international')}
        p=resolve('node_partners',{'international':False,'_dialogue':intent(context='continue',kind='unspecified')},old,self.data)[1]
        self.assertEqual(p['partner_scope'],'all');self.assertFalse(p['international'])

    def test_multiple_node_metrics_are_not_silently_reduced(self):
        old={'function_id':'node_profile','confirmed':dict(kind='air',node='EDDP',year=2024,direction='outbound',metrics=['tonnes','flights'])}
        with self.assertRaisesRegex(SelectionError,'mehrere Kennzahlen'):
            resolve('node_connections',{'partners':['EGLL'],'_dialogue':intent(context='continue',kind='unspecified')},old,self.data)
        p=resolve('node_connections',{'partners':['EGLL'],'metric':'flights','_dialogue':intent(context='continue',kind='unspecified')},old,self.data)[1]
        self.assertEqual(p['metric'],'flights')

    def test_leipzig_berlin_is_a_domestic_airport_connection(self):
        args=dict(kind='air',node='LEJ',partners=['BER'],year=2024,direction='outbound',metric='flights',_dialogue=intent('domestic'))
        p=resolve('node_connections',args,{},self.data)[1]
        self.assertEqual(p['node'],'EDDP');self.assertEqual(p['partners'],['EDDB'])
        self.assertNotIn('partner_group',p)

    def test_exact_sea_country_filter_is_not_rejected(self):
        p=dict(product='sea_partners',entity='DEHAM',year=2024,mode='sea',metric='tonnes',direction='outbound',classification='C7',group='4',partner='CN',top=10,_dialogue=intent('international'))
        selected=resolve('dashboard_detail',p,{},self.data)[1]
        self.assertEqual(selected['partner'],'CN')
        state={'function_id':'dashboard_detail','confirmed':selected}
        selected=resolve('dashboard_detail',{'direction':'inbound','_dialogue':intent('international','continue','unspecified')},state,self.data)[1]
        self.assertEqual(selected['partner'],'CN')

    def test_source_labels_do_not_become_b01(self):
        for function in ['node_connections','node_profile','node_statistics','node_partners']:
            p=self.selection() if function=='node_connections' else dict(kind='air',node='EDDP',year=2024,direction='outbound',partner_scope='international')
            p.update({'metrics':['tonnes']} if function=='node_profile' else {'metric':'tonnes'})
            if function=='node_partners':p['top']=5
            result=self.result(p,function)
            self.assertTrue(all('AVIA_GOR_DE' in f['source'] and 'B01' not in f['source'] for f in result['facts']))
        p=dict(kind='sea',node='DEHAM',year=2024,direction='outbound',partner_scope='domestic',metric='teu')
        self.assertIn('Destatis Seeverkehr',self.result(p,'node_statistics')['sources'][0])

    def test_2025_statistics_use_corrected_source_without_inventing_relations(self):
        raw=self.data.query('node_statistics',dict(kind='air',node='EDDP',year=2025,direction='all',metric='flights',partner_scope='all'))
        self.assertEqual(raw['value'],48657)
        for scope in ['domestic','international']:
            raw=self.data.query('node_statistics',dict(kind='air',node='EDDP',year=2025,direction='all',metric='flights',partner_scope=scope))
            self.assertIsNone(raw['value']);self.assertEqual(raw['status'],'missing_row')
        years=available_years(self.data,'node_statistics',dict(kind='air',node='EDDP',metric='flights'))
        self.assertIn(2024,years);self.assertIn(2025,years)
        filtered=available_years(self.data,'node_statistics',dict(kind='air',node='EDDP',metric='flights',partner_scope='international'))
        self.assertNotIn(2025,filtered)
        result=self.result(dict(kind='air',node='EDDP',year=2025,direction='all',metric='flights',partner_scope='all'),'node_statistics')
        self.assertTrue(all('gesperrt' not in fact['source'] for fact in result['facts']))

    def test_partial_total_and_units_are_verified(self):
        result=self.result();payload=packet(result,self.data)
        good={'paragraphs':[{'text':'2024 beträgt die bekannte Teilsumme 994 Frachtflüge. Eine vollständige Summe fehlt.','evidence_ids':['connection_group']}]}
        self.assertEqual(len(check_prose(good,payload,result,self.data)),1)
        for text in ['2024 gab es insgesamt 994 Frachtflüge.','2024 beträgt die bekannte Teilsumme 994 Tonnen.']:
            with self.assertRaises(ValueError):check_prose({'paragraphs':[{'text':text,'evidence_ids':['connection_group']}]},payload,result,self.data)

    def test_all_direction_air_is_not_double_counted(self):
        p=self.selection(direction='all');raw=self.data.query('node_connections',p)
        values={r.get('partner_id'):r['value'] for r in raw['observations'] if r.get('partner_id')}
        self.assertEqual(values['EGLL'],360);self.assertEqual(values['EGGW'],462);self.assertEqual(values['EGSS'],806)

    def test_fixture_zero_missing_teu_and_unknown_country(self):
        with tempfile.TemporaryDirectory(prefix='node-test-',dir='C:/tmp') as directory,duckdb.connect() as con:
            con.execute('CREATE TABLE records(node VARCHAR,partner VARCHAR,partner_country VARCHAR,year INTEGER,direction VARCHAR,metric VARCHAR,known_sum DOUBLE,missing_count INTEGER,restricted_count INTEGER,source_rows INTEGER,source_id VARCHAR,not_applicable_count INTEGER)')
            data=[('DETEST','DEONE','DE',2024,'outbound','teu',0,0,0,1,'test',0),
                  ('DETEST','NLONE','NL',2024,'outbound','teu',None,0,0,1,'test',1),
                  ('DETEST','NLTWO','NL',2024,'outbound','teu',5,1,1,2,'test',0),
                  ('DETEST','ZZONE','ZZ',2024,'outbound','teu',100,0,0,1,'test',0)]
            con.executemany('INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',data)
            path=Path(directory)/'sea_partners.parquet'
            con.execute("COPY records TO '"+path.as_posix()+"' (FORMAT PARQUET)")
            p=dict(kind='sea',node='DETEST',year=2024,direction='outbound',metric='teu')
            domestic=nodes.node_connections(con,Path(directory),**p,partners=['DEONE'])
            self.assertEqual(domestic['observations'][0]['value'],0)
            foreign=nodes.node_statistics(con,Path(directory),**p,partner_scope='international')
            self.assertIsNone(foreign['value']);self.assertEqual(foreign['known_sum'],5)
            missing=nodes.node_connections(con,Path(directory),**p,partners=['NOPE'])
            self.assertIsNone(missing['observations'][0]['value'])
            self.assertEqual(missing['observations'][0]['source_status'],'missing_row')


if __name__=='__main__':unittest.main()
