"""Angefragte Randjahre und originale KBA-Zustände bleiben in der Kundenausgabe erhalten."""
import copy
import csv
from pathlib import Path
from types import SimpleNamespace
import unittest

from server.analyseassistent.datasets import Datasets
from server.analyseassistent.service import Service
from server.analyseassistent.results import make_result
from server.analyseassistent.presentation import present
from server.analyseassistent.narrative import evidence, apply_narrative

ROOT=Path(__file__).resolve().parents[2]
QUESTION='Wie viele Güter wurden auf der Straße von Dortmund nach Bielefeld bewegt, im jahr 2024 und 2020 und wie war die Entwicklung?'


def synthetic(values,states=None):
    datasets=SimpleNamespace(names={'A':['Alpha'],'B':['Beta']},paths={},snapshot_id='synthetic')
    params={'origin':'A','destination':'B','start':2020,'end':2020+len(values)-1,'modes':['road'],'metric':'tonnes'}
    observations=[{'label':str(2020+i)+' / road','year':2020+i,'mode':'road','value':value,
                   'source_status':states[i] if states else ('missing_row' if value is None else 'available')}
                  for i,value in enumerate(values)]
    result=make_result('relation_history',params,{'status':'partial' if None in values else 'available',
                       'unit':'t','observations':observations},datasets,'test')
    result['answer']=present(result,datasets)
    return result


class CustomerHistory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result,cls.audit=Service(Datasets(ROOT)).analyze(QUESTION,select_answer=False)

    def test_reported_question_matches_original_rows_without_substitute_period(self):
        path=ROOT/'data/raw/Straße/KBA/VE7_Verflechtung_NUTS3/ve7_2010_2024.csv'
        with path.open(encoding='utf-8',newline='') as handle:
            records=[r for r in csv.DictReader(handle,delimiter=';') if
                     r['Beladeregion']=='DEA52' and r['Entladeregion']=='DEA41' and
                     2020<=int(r['Jahr'])<=2024]
        self.assertEqual({int(r['Jahr']):int(r['Tonnen']) for r in records},{2020:110050,2022:55106})
        self.assertTrue(all(''.join(r['ZS_Tonnen'].split())=='()' for r in records))
        facts={f['year']:f for f in self.result['facts']}
        for record in records:
            self.assertEqual(facts[int(record['Jahr'])]['value'],int(record['Tonnen']))
            self.assertEqual(facts[int(record['Jahr'])]['quality_status'],'restricted')
        for year in [2021,2023,2024]:
            self.assertIsNone(facts[year]['value'])
            self.assertEqual(facts[year]['value_status'],'missing_row')
        prose=' '.join(self.result['answer']['paragraphs'])
        self.assertIn('110.050 Tonnen',prose)
        self.assertIn('Für 2024 fehlt ein eigener Eintrag',prose)
        self.assertIn('2020 bis 2024',prose)
        for forbidden in ['49,93','2022','größten','jüngsten gemeinsamen']:
            self.assertNotIn(forbidden,prose)
        self.assertEqual(self.audit['attempted_model_calls'],0)

    def test_customer_structure_keeps_details_and_concrete_source_explanation(self):
        answer=self.result['answer']
        self.assertEqual(len(answer['paragraphs']),2)
        self.assertIn('Stichproben',answer['paragraphs'][1])
        self.assertIn('allein nicht feststellen',answer['paragraphs'][1])
        self.assertTrue(answer['tables'][0]['collapsed'])
        self.assertEqual(answer['tables'][0]['row_count'],5)
        self.assertEqual(len(answer['notes']),2)  # precision and city interpretation
        self.assertTrue(any('kaum hinreichend genau' in n for n in answer['notes']))

    def test_missing_either_endpoint_never_uses_inner_years(self):
        for values in [[None,100,50],[100,50,None],[None,100,None],[None,None,None]]:
            with self.subTest(values=values):
                result=synthetic(values)
                prose=' '.join(result['answer']['paragraphs'])
                self.assertIn('2020 bis 2022 lässt sich damit nicht beziffern',prose)
                self.assertNotIn('%',prose)
                self.assertNotIn('2021',prose)

    def test_available_endpoints_allow_arithmetic_despite_missing_middle(self):
        result=synthetic([100,None,50])
        self.assertIn('rechnerischen Rückgang um 50 %',' '.join(result['summary']))
        self.assertEqual([f['value'] for f in result['facts']],[100,None,50])
        for values in [[0,100],[0,0]]:
            self.assertIn('keine prozentuale Veränderung',' '.join(synthetic(values)['summary']))
        self.assertIn('Rückgang um 100 %',' '.join(synthetic([100,0])['summary']))

    def test_missing_states_are_not_collapsed_into_unknown_value(self):
        result=synthetic([None,None,None],['missing_row','not_available','suppressed'])
        self.assertEqual([f['value_status'] for f in result['facts']],['missing_row','not_available','suppressed'])
        notes=[row['note'] for row in result['answer']['tables'][0]['rows']]
        self.assertIn('Kein eigener Eintrag',notes[0])
        self.assertIn('Jahrgang',notes[1])
        self.assertIn('unterdrückter',notes[2])

    def test_model_must_keep_endpoint_answer_and_explanation_in_order(self):
        result=copy.deepcopy(self.result)
        records=evidence(result,result['answer'])
        self.assertFalse(any(key.startswith('f') for key in records))
        for tokens in [['p2'],['p2','p1'],['p1','p1','p2']]:
            selection={'result_id':result['result_id'],'data_snapshot_id':result['data_snapshot_id'],
                       'paragraphs':[{'text':' '.join('{{'+t+'}}' for t in tokens),'evidence_ids':list(set(tokens))}]}
            with self.assertRaises(ValueError):
                apply_narrative(result,copy.deepcopy(result['answer']),selection,records)
        selection={'result_id':result['result_id'],'data_snapshot_id':result['data_snapshot_id'],
                   'paragraphs':[{'text':'{{'+key+'}}','evidence_ids':[key]} for key in ['p1','p2']]}
        answer=apply_narrative(result,copy.deepcopy(result['answer']),selection,records)
        self.assertEqual(answer['paragraphs'],self.result['answer']['paragraphs'])

    def test_single_year_is_not_presented_as_growth(self):
        prose=' '.join(synthetic([100])['summary'])
        self.assertNotIn('Veränderung',prose)
        self.assertNotIn('%',prose)


if __name__=='__main__':unittest.main()
