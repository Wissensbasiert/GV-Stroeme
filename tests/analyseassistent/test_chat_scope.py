"""Mehrteilige reale Aufträge und Kontextgrenzen der freien Antwort."""
import copy
from pathlib import Path
import unittest
from server.analyseassistent.datasets import Datasets
from server.analyseassistent.results import make_result
from server.analyseassistent.presentation import present
from server.analyseassistent.chat import packet, check_prose


class ChatScope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=Datasets(Path(__file__).resolve().parents[2])

    def result(self,fn,p):
        r=make_result(fn,p,self.data.query(fn,p),self.data,'0.4.2')
        r['answer']=present(r,self.data)
        return r,packet(r,self.data)

    def test_published_partner_names_and_grouped_shares(self):
        r,p=self.result('partner_ranking',dict(region='DE600',year=2024,mode='road',metric='tonnes',direction='all',external=True,group='ALL',top=5))
        prose={'paragraphs':[{'text':'Harburg: 5.126.813 Tonnen (9,24 %). Segeberg: 4.628.663 Tonnen (8,34 %). Stormarn: 3.374.382 Tonnen (6,08 %). Herzogtum Lauenburg: 2.687.481 Tonnen (4,84 %). Region Hannover: 2.289.981 Tonnen (4,13 %).','evidence_ids':['partner_group']}]}
        check_prose(prose,p,r,self.data)
        wrong=copy.deepcopy(prose)
        wrong['paragraphs'][0]['text']=wrong['paragraphs'][0]['text'].replace('Harburg','Duisburg')
        with self.assertRaises(ValueError): check_prose(wrong,p,r,self.data)

    def test_bidirectional_relation_and_missing_modes(self):
        r,p=self.result('relation_matrix',dict(origin='DEA12',destination='DEE03',year=2024,metric='tonnes'))
        prose={'paragraphs':[{'text':s,'evidence_ids':['p'+str(i+1)]} for i,s in enumerate(r['summary'])]}
        self.assertEqual(len(check_prose(prose,p,r,self.data)),2)
        self.assertIn('1.947',prose['paragraphs'][0]['text'])
        self.assertIn('1.189',prose['paragraphs'][1]['text'])
        self.assertIn('kein eigener veröffentlichter',prose['paragraphs'][0]['text'])
        wrong=copy.deepcopy(prose)
        wrong['paragraphs'][0]['text']=wrong['paragraphs'][0]['text'].replace('1.947','1.189')
        wrong['paragraphs'][0]['evidence_ids']=['p1','p2']
        with self.assertRaises(ValueError): check_prose(wrong,p,r,self.data)
        with self.assertRaises(ValueError): check_prose({'paragraphs':prose['paragraphs'][:1]},p,r,self.data)

    def test_comparison_covers_both_regions_modes_and_goods(self):
        r,p=self.result('compare_regions',dict(regions=['DEA12','DEE03'],year=2024,metric='tonnes',direction='all'))
        prose={'paragraphs':[{'text':s,'evidence_ids':['p'+str(i+1)]} for i,s in enumerate(r['summary'])]}
        self.assertEqual(len(check_prose(prose,p,r,self.data)),2)
        self.assertIn('Sonstige Produkte',prose['paragraphs'][1]['text'])
        with self.assertRaises(ValueError): check_prose({'paragraphs':prose['paragraphs'][:1]},p,r,self.data)
        self.assertTrue(any(k.startswith('profile_group_') for k in p['evidence']))
        wrong=copy.deepcopy(prose)
        wrong['paragraphs'][0]['text']=wrong['paragraphs'][0]['text'].replace('108,22 Mio. Tonnen','108,22 Mio. Tonnenkilometer')
        with self.assertRaises(ValueError): check_prose(wrong,p,r,self.data)

    def test_large_partner_and_forecast_groups_have_all_row_evidence(self):
        r,p=self.result('partner_ranking',dict(region='DE600',year=2024,mode='road',metric='tonnes',direction='all',external=True,group='ALL',top=30))
        self.assertGreater(len(p['evidence']['partner_group']['fact_ids']),30)
        self.assertTrue(all(key in p['evidence'] for key in p['evidence']['partner_group']['fact_ids']))
        r,p=self.result('forecast_regions',dict(regions=['DEA12','DEE03'],modes=['road','rail','iww'],metrics=['tonnes','tkm'],direction='all'))
        self.assertEqual(len(r['facts']),48)
        self.assertEqual(len([key for key in p['evidence'] if key.startswith('forecast_group_')]),12)
        self.assertTrue(all(f['fact_id'] in p['evidence'] for f in r['facts']))


if __name__=='__main__': unittest.main()
