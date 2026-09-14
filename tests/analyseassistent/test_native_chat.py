"""Native Tools, gebundene freie Zahlen und abschließende Streaming-Buchung."""
import copy
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from server.analyseassistent.chat import check_prose, packet, validate_arguments, tool_specs
from server.analyseassistent.api import Application


class NativeGuards(unittest.TestCase):
    def setUp(self):
        self.data = SimpleNamespace(names={'DEA52': ['Dortmund'], 'DEA41': ['Bielefeld']})
        self.result = {'parameters': {'origin': 'DEA52', 'destination': 'DEA41', 'start': 2020, 'end': 2024},
                       'facts': [{'value': 110050, 'year': 2020, 'unit': 't'}]}
        self.payload = {'evidence': {'f1': {'text': '2020: 110.050 Tonnen', 'value': 110050, 'year': 2020, 'unit': 't'},
                                     'n1': {'text': 'Für 2024 fehlt die Relationszeile; eine Veränderung ist nicht berechenbar.'}}}

    def check(self, text, ids=None):
        return check_prose({'paragraphs': [{'text': text, 'evidence_ids': ids or ['f1']}]}, self.payload, self.result, self.data)

    def test_free_number_and_natural_causal_word(self):
        self.assertEqual(self.check('**2020** waren es 110.050 Tonnen.'), ['**2020** waren es 110.050 Tonnen.'])
        self.check('Ein Vergleich ist nicht möglich, weil für 2024 die Relationszeile fehlt.', ['n1'])

    def test_existing_number_with_wrong_year_rejected(self):
        with self.assertRaises(ValueError): self.check('2024 waren es 110.050 Tonnen.', ['f1', 'n1'])

    def test_million_abbreviation_does_not_split_a_year_comparison(self):
        self.result['facts']=[{'fact_id':'f1','value':797506,'year':2020,'unit':'t'},
                              {'fact_id':'f2','value':1490000,'year':2024,'unit':'t'}]
        self.payload['evidence']['p1']={'text':'2020: 797.506 Tonnen. 2024: 1,49 Mio. Tonnen.',
                                        'fact_ids':['f1','f2']}
        self.check('Die Werte betrugen 797.506 Tonnen im Jahr 2020 und 1,49 Mio. Tonnen im Jahr 2024.', ['p1'])
        self.check('Von 2020 bis 2024 sanken die Werte auf 1,49 Mio. Tonnen, ausgehend von 797.506 Tonnen.', ['p1'])
        with self.assertRaises(ValueError): self.check('2024 betrug der Wert 797.506 Tonnen.', ['p1'])

    def test_wrong_unit_direction_and_invented_numbers_rejected(self):
        for text in ['2020 waren es 110.050 Tonnenkilometer.', 'Von Bielefeld nach Dortmund waren es 110.050 Tonnen.',
                     '2020 waren es 72.000 Tonnen.', 'Es waren 2020 Tonnen.', 'Die Region ist verkehrsfrei.', '<img src=x onerror=alert(1)>']:
            with self.subTest(text=text), self.assertRaises(ValueError): self.check(text)

    def test_foreign_evidence_rejected(self):
        with self.assertRaises(ValueError): self.check('Ein Wert.', ['f999'])

    def test_checked_alternative_can_be_named_but_cannot_take_road_quantity(self):
        self.result['function_id']='road_relation_goods_limit'
        self.result['related_data']={'checks':{'rail':{'status':'partial','available':True,'parameters':{}}}}
        self.payload['evidence']['n2']={'text':'Alternativ sind auf der Schiene veröffentlichte Güterangaben verfügbar.'}
        self.check('Alternativ sind auf der Schiene veröffentlichte Güterangaben verfügbar.', ['n2'])
        with self.assertRaises(ValueError): self.check('Auf der Schiene waren es 2020 110.050 Tonnen.', ['f1','n2'])

    def test_mode_percentage_and_swapped_quantity_units(self):
        self.result['parameters']['modes'] = ['road']
        for text in ['2020 waren es auf der Schiene 110.050 Tonnen.', 'Der Anteil beträgt 110.050 %.']:
            with self.assertRaises(ValueError): self.check(text)
        self.payload['evidence']['f2'] = {'text': '2020: 7.500 Tonnenkilometer', 'unit': 'tkm', 'value': 7500}
        with self.assertRaises(ValueError): self.check('2020 waren es 7.500 Tonnen.', ['f2'])

    def test_possible_method_is_not_a_proven_cause(self):
        self.result['facts'].append({'value': None, 'year': 2024, 'source_status': 'missing_row'})
        self.payload['evidence']['n2'] = {'text': 'Die Stichprobenmethodik kann fehlende Relationen erklären. Die konkrete Ursache ist unbekannt.'}
        with self.assertRaises(ValueError): self.check('Die fehlende Angabe liegt an der Stichprobenmethodik.', ['n2'])
        self.check('Die Stichprobenmethodik kann eine Rolle spielen. Die konkrete Ursache ist unbekannt.', ['n2'])

    def test_tools_use_real_schemas_and_no_sql(self):
        tools = tool_specs()
        self.assertGreaterEqual(len(tools), 25)
        self.assertTrue(all(t['function']['parameters']['additionalProperties'] is False for t in tools))
        with self.assertRaises(ValueError): validate_arguments('run_sql', {}, 'test', {}, self.data)

    def test_structured_selection_does_not_require_sentence_patterns(self):
        args = {'origin': 'DEA52', 'destination': 'DEA41', 'year': 2024}
        validate_arguments('relation_overview', args, 'Von Dortmund nach Bielefeld 2024', {}, self.data)
        validate_arguments('relation_overview', args, 'Was schicken wir Richtung Bielefeld?', {}, self.data)
        with self.assertRaises(ValueError): validate_arguments('relation_overview', {**args, 'origin': 'UNKNOWN'}, 'Eine Frage', {}, self.data)
        validate_arguments('relation_overview', {**args, 'origin': 'DEA41', 'destination': 'DEA52'},
                           'Und umgekehrt?', {'confirmed': args}, self.data)

    def test_stream_result_follows_quota_finish_and_duplicate_does_not_query(self):
        quota = Mock()
        quota.status.return_value = {'remaining': 10}
        quota.reserve.return_value = {'duplicate': False}
        order = []
        def analyze(*args, **kwargs):
            kwargs['progress']({'stage': 'data', 'text': 'Daten werden gelesen …'})
            order.append('analyze')
            return {'status': 'ok', 'facts': [{'value': 1}], 'answer': {}}, {}
        service = SimpleNamespace(analyze=analyze)
        quota.finish.side_effect = lambda *a, **kw: order.append('booked')
        app = Application(service, quota, lambda _: 7, allowed_origin='https://test.invalid')
        body = json.dumps({'question': 'Test', 'request_id': '00000000-0000-0000-0000-000000000001'}).encode()
        env = {'PATH_INFO': '/api/analyseassistent', 'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': 'application/json',
               'CONTENT_LENGTH': str(len(body)), 'wsgi.input': io.BytesIO(body), 'HTTP_ORIGIN': 'https://test.invalid',
               'HTTP_ACCEPT': 'text/event-stream'}
        stream = app(env, lambda *a: None)
        frames = []
        for chunk in stream:
            if b'event: result' in chunk: self.assertEqual(order, ['analyze', 'booked'])
            frames.append(chunk)
        self.assertIn(b'event: status', b''.join(frames))
        self.assertIn(b'event: result', b''.join(frames))
        quota.reserve.return_value = {'duplicate': True, 'state': 'done'}
        env['wsgi.input'] = io.BytesIO(body)
        self.assertIn(b'event: error', b''.join(app(env, lambda *a: None)))
        self.assertEqual(order, ['analyze', 'booked'])


class NativeRealDialogue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from server.analyseassistent.datasets import Datasets
        cls.datasets = Datasets(Path(__file__).resolve().parents[2])

    def test_native_year_reverse_followup_and_missing_source_state(self):
        from server.analyseassistent.service import Service
        class Scripted:
            native_tools = True
            initial = True
            parameters = {}
            time = {'kind': 'unspecified', 'count': 0}
            def chat(self, messages, **kwargs):
                if kwargs.get('tools'):
                    if self.initial:
                        self.initial = False
                        return {'role': 'assistant', 'tool_calls': [{'id': 'initial', 'type': 'function', 'function': {
                            'name': 'relation_overview', 'arguments': json.dumps({'origin': 'DE300', 'destination': 'DE600',
                            'modes': ['rail'], '_dialogue': {'context': 'new', 'clarification': 'Welches Jahr möchten Sie auswerten?',
                            'time': {'kind': 'unspecified', 'count': 0}}})}}]}, {}
                    return {'role': 'assistant', 'tool_calls': [{'id': 'test', 'type': 'function', 'function': {
                        'name': 'relation_overview', 'arguments': json.dumps({**self.parameters, '_dialogue': {
                            'context': 'continue', 'clarification': '', 'time': self.time}})}}]}, {}
                payload = json.loads(messages[-1]['content'])
                key = next(k for k in payload['evidence'] if k.startswith('p'))
                return {'role': 'assistant', 'content': json.dumps({'paragraphs': [{
                    'text': payload['evidence'][key]['text'], 'evidence_ids': [key]}]})}, {}
        model = Scripted()
        service = Service(self.datasets, model)
        result, _ = service.analyze('Welche Güter gehen per Schiene von Berlin nach Hamburg?')
        self.assertEqual(result['status'], 'needs_clarification')
        model.parameters = {'origin': 'DE300', 'destination': 'DE600', 'modes': ['rail'], 'include_goods': True}
        model.time = {'kind': 'latest_available', 'count': 0}
        result, _ = service.analyze('Das aktuellste Jahr', conversation=result['conversation'])
        self.assertEqual(result['parameters']['year'], 2025)
        self.assertEqual(result['facts'][0]['value'], 240297)
        model.parameters = {'origin': 'DE600', 'destination': 'DE300'}
        model.time = {'kind': 'unspecified', 'count': 0}
        result, _ = service.analyze('Und andersherum?', conversation=result['conversation'])
        self.assertEqual(result['parameters']['year'], 2025)
        self.assertEqual(result['parameters']['modes'], ['rail'])
        self.assertEqual(result['facts'][0]['value'], 585052)
        model.parameters['year'] = 2024
        result, _ = service.analyze('Und 2024?', conversation=result['conversation'])
        self.assertEqual(result['facts'][0]['value'], 554806)
        model.parameters = {'origin': 'DEA23', 'destination': 'DE600', 'year': 2024, 'modes': ['iww'], 'include_goods': False}
        result, _ = service.analyze('Wie viele Tonnen gingen 2024 per Binnenschiff von Köln nach Hamburg?')
        self.assertEqual(result['source_status'], 'missing_row')


if __name__ == '__main__': unittest.main()
