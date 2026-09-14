"""Nutzerverlauf Köln–Düsseldorf mit echten Daten und ohne Planmodell."""
import unittest
from pathlib import Path
from unittest.mock import patch
from server.analyseassistent.datasets import Datasets
from server.analyseassistent.service import Service
from server.analyseassistent.dialogue import MULTI_YEAR, PREVIOUS_YEAR

ROOT=Path(__file__).resolve().parents[2]
QUESTIONS=[
    'Was für Güter wurden letztes Jahr von Köln nach Düsseldorf transportiert und wie viele?',
    'Kannst du mir auch die Verkehrsleistung nennen? Und was ist mit der Güterart?',
    'Ich meine weiterhin Köln nach Düsseldorf im letzten Jahr',
    '2024',
]

class ConversationRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.datasets=Datasets(ROOT)

    def test_singular_and_plural_years_are_distinct(self):
        for text in ['letztes Jahr','im letzten Jahr','vergangenes Jahr','Vorjahr']:
            self.assertTrue(PREVIOUS_YEAR.search(text))
            self.assertFalse(MULTI_YEAR.search(text))
        for text in ['in den letzten Jahren','letzte Jahre','mehrere Jahrgänge','seit 2020']:
            self.assertTrue(MULTI_YEAR.search(text))
            self.assertFalse(PREVIOUS_YEAR.search(text))

    @patch('server.analyseassistent.dialogue.previous_calendar_year',return_value=2025)
    def test_complete_reported_conversation_retains_route_year_goods_and_metrics(self,_):
        service=Service(self.datasets)
        token=None
        for index,question in enumerate(QUESTIONS):
            result,audit=service.analyze(question,conversation=token,select_answer=False)
            token=result['conversation']
            self.assertIn(result['status'],{'ok','partial'},(question,result['answer']))
            self.assertEqual(result['function_id'],'relation_overview')
            p=result['parameters']
            self.assertEqual((p['origin'],p['destination']),('DEA23','DEA11'))
            self.assertEqual(p['year'],2024 if index==3 else 2025)
            self.assertEqual(p['metrics'],['tonnes'] if index==0 else ['tonnes','tkm'])
            self.assertTrue(p['include_goods'])
            self.assertEqual(audit['attempted_model_calls'],0)
            self.assertNotIn('2020–2024',result['answer']['title'])
            self.assertTrue(any('Güterarten der Straßenverbindung' in x for x in result['answer']['paragraphs']))
            self.assertTrue(all(row['label'] and row['value'] and row['unit'] for table in result['answer']['tables'] for row in table['rows']))
        for mode,expected in [('road',624632),('rail',4045),('iww',1372.7)]:
            value=next(f['value'] for f in result['facts'] if f['mode']==mode and f['metric']=='tonnes' and f['group']=='ALL')
            self.assertEqual(value,expected)
        self.assertTrue(any(f['unit']=='tkm' and f['value'] is not None for f in result['facts']))

    def test_other_routes_refinements_and_reverse_match_fresh_queries(self):
        for origin,destination in [('Hamburg','Berlin'),('Duisburg','Köln'),('Rosenheim','Augsburg')]:
            with self.subTest(route=(origin,destination)):
                service=Service(self.datasets)
                initial,_=service.analyze(f'Welche Güter wurden 2024 von {origin} nach {destination} transportiert?',select_answer=False)
                for followup in ['Und die Güterarten?', 'Zeige dazu die Transportleistung.', 'Wie hoch ist die Verkehrsleistung?', 'Und in Gegenrichtung?', 'Und 2023?']:
                    current,audit=service.analyze(followup,conversation=initial['conversation'],select_answer=False)
                    self.assertIn(current['status'],{'ok','partial','not_available'})
                    self.assertEqual(audit['attempted_model_calls'],0)
                    self.assertEqual(current['function_id'],'relation_overview')
                    raw=self.datasets.query('relation_overview',current['parameters'])
                    self.assertEqual([r['value'] for r in current['facts'] if not r.get('aggregate')],[r['value'] for r in raw['observations']])
                    self.assertEqual(current['parameters']['include_goods'],True)
                    if 'Transportleistung' in followup:self.assertEqual(current['parameters']['metrics'],['tkm'])
                    if 'Gegenrichtung' in followup:
                        self.assertEqual(current['parameters']['origin'],initial['parameters']['destination'])
                    if '2023' in followup:self.assertEqual(current['parameters']['year'],2023)

    def test_regional_metric_followup_preserves_region_and_year(self):
        service=Service(self.datasets)
        initial,_=service.analyze('Duisburg 2024',{'region':'DEA12','year':2024,'mode':'road','metric':'tonnes'},function='balance')
        result,audit=service.analyze('Und die Verkehrsleistung?',conversation=initial['conversation'],select_answer=False)
        self.assertEqual(result['parameters'],{'region':'DEA12','year':2024,'mode':'road','metric':'tkm'})
        self.assertEqual(result['function_id'],'balance')
        self.assertEqual(audit['attempted_model_calls'],0)

    def test_overview_matches_existing_b01_source_values_and_flags(self):
        p={'origin':'DEA23','destination':'DEA11','year':2024,'modes':['road','rail','iww'],'metrics':['tonnes','tkm'],'include_goods':True}
        raw=self.datasets.query('relation_overview',p)
        for mode,metric,group in [('road','tonnes','ALL'),('rail','tonnes','6'),('iww','tkm','ALL'),('iww','tonnes','7')]:
            expected=self.datasets.query('relation',{'origin':p['origin'],'destination':p['destination'],'year':p['year'],
                'mode':mode,'metric':metric,'group':group})
            row=next(r for r in raw['observations'] if (r['mode'],r['metric'],r['group'])==(mode,metric,group))
            self.assertEqual(row['value'],expected['value'])
            self.assertEqual(row['source_status'],expected['status'])
            self.assertEqual(row['quality'],expected.get('quality','unknown'))

    def test_year_clarification_retains_function_and_other_fields(self):
        service=Service(self.datasets)
        first,_=service.analyze('Was für Güter wurden von Köln nach Düsseldorf transportiert?',select_answer=False)
        self.assertEqual(first['missing_fields'],['year'])
        second,_=service.analyze('2024',conversation=first['conversation'],select_answer=False)
        self.assertEqual(second['parameters']['year'],2024)
        self.assertIn(second['status'],{'ok','partial'})

    def test_new_route_does_not_inherit_old_year_or_metrics(self):
        service=Service(self.datasets)
        first,_=service.analyze('Was für Güter wurden 2024 von Köln nach Düsseldorf transportiert?',select_answer=False)
        next_result,audit=service.analyze('Welche Güter gehen von Berlin nach Hamburg?',conversation=first['conversation'],select_answer=False)
        self.assertEqual(audit['conversation_transition'],'new_topic')
        self.assertEqual(next_result['missing_fields'],['year'])
        self.assertEqual(next_result['conversation_state']['confirmed']['origin'],'DE300')

if __name__=='__main__':unittest.main()
