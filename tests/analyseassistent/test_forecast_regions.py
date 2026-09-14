"""Prognosevergleich: Dimensionen, echte Quellwerte und Gesprächsfortsetzung."""
import json
import ast
from pathlib import Path
import unittest
from unittest.mock import patch
from server.analyseassistent.datasets import Datasets
from server.analyseassistent.service import Service
from server.analyseassistent.selection import resolve, SelectionError
from server.analyseassistent.results import make_result
from server.analyseassistent.presentation import present
from server.analyseassistent.chat import packet, check_prose
from server.analyseassistent.profiles import forecast_regions


def intent(context='new', kind='explicit'):
    return {'context': context, 'clarification': '', 'time': {'kind': kind, 'count': 0}}


class ForecastRegions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = Datasets(Path(__file__).resolve().parents[2])

    def setUp(self):
        self.args = {'regions': ['DEE03', 'DEA12'], 'modes': ['rail'],
                     'metrics': ['tonnes', 'tkm'], 'direction': 'all'}

    def result(self):
        raw = self.data.query('forecast_regions', self.args)
        result = make_result('forecast_regions', self.args, raw, self.data, '0.4.1')
        result['answer'] = present(result, self.data)
        return result

    def test_actual_source_values_and_changes_stay_separate(self):
        result = self.result()
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['facts']), 16)
        expected = {('DEE03', 'tonnes'): (2037023, 2751683), ('DEE03', 'tkm'): (218995582, 319228696),
                    ('DEA12', 'tonnes'): (22506890, 26407912), ('DEA12', 'tkm'): (6410552330, 9373443044)}
        for key, (base, target) in expected.items():
            group = [f for f in result['facts'] if (f['region'], f['metric']) == key]
            self.assertEqual(next(f['value'] for f in group if f.get('scenario') == '2019_BASE'), base)
            self.assertEqual(next(f['value'] for f in group if f.get('scenario') == '2040_P1'), target)
            self.assertAlmostEqual(next(f['value'] for f in group if f['unit'] == '%'), (target-base)/base*100)
            self.assertTrue(all(f['mode'] == 'rail' and f['basis'] == 'VP2019_BASE_to_2040_P1' for f in group))
        self.assertEqual(len(set(f['label'] for f in result['facts'])), 16)
        self.assertEqual(len(result['answer']['paragraphs']), 2)
        self.assertEqual(len(result['answer']['tables']), 2)
        self.assertTrue(all(f['value_status'] in {'forecast', 'calculated'} for f in result['facts']))
        self.assertIn('Szenariovergleich', ' '.join(result['answer']['notes']))

    def test_relative_changes_missing_and_zero_do_not_become_observations(self):
        # Isolated fixture: missing unrelated modes must not mark rail as partial.
        with patch('server.analyseassistent.profiles.regions_checked', return_value={'DEE03': 'Magdeburg'}), \
             patch('server.analyseassistent.profiles.forecast_rows', return_value=([
                 {'mode': 'rail', 'label': 'rail base', 'value': 0},
                 {'mode': 'rail', 'label': 'rail change', 'value': None, 'unit': '%'},
                 {'mode': 'road', 'label': 'road base', 'value': None}], 'partial')):
            raw = forecast_regions(None, None, regions=['DEE03'], modes=['rail'], metrics=['tonnes'], direction='all')
        self.assertEqual(len(raw['observations']), 2)
        self.assertEqual(raw['observations'][0]['value'], 0)
        self.assertIsNone(raw['observations'][1]['value'])
        self.assertEqual(raw['status'], 'partial')

    def test_limits_invalid_dimensions_and_no_observed_years(self):
        for extra in [{'metrics': ['teu']}, {'modes': ['air']}, {'regions': ['DEE03', 'DEE03']},
                      {'observed_years': [2040]}, {'year': 2040}, {'regions': ['XX999']}]:
            with self.subTest(extra=extra), self.assertRaises(SelectionError):
                resolve('forecast_regions', {**self.args, **extra, '_dialogue': intent()}, {}, self.data)
        _, args, _, _ = resolve('forecast_regions', {**self.args, '_dialogue': intent()}, {}, self.data)
        self.assertEqual(args, self.args)

    def test_zero_base_is_not_a_missing_source_value(self):
        with patch('server.analyseassistent.profiles.regions_checked', return_value={'DEE03': 'Magdeburg'}), \
             patch('server.analyseassistent.profiles.forecast_rows', return_value=([
                 {'mode': 'rail', 'label': 'base', 'value': 0, 'scenario': '2019_BASE'},
                 {'mode': 'rail', 'label': 'target', 'value': 10, 'scenario': '2040_P1'},
                 {'mode': 'rail', 'label': 'absolute', 'value': 10},
                 {'mode': 'rail', 'label': 'relative', 'value': None, 'unit': '%', 'denominator': 0}], 'available')):
            raw = forecast_regions(None, None, regions=['DEE03'], modes=['rail'], metrics=['tonnes'], direction='all')
        self.assertEqual(raw['status'], 'available')
        self.assertEqual(raw['observations'][-1]['value_status'], 'not_computable')
        result = make_result('forecast_regions', {**self.args, 'regions': ['DEE03'], 'metrics': ['tonnes']}, raw, self.data, '0.4.1')
        answer = present(result, self.data)
        self.assertEqual(result['status'], 'ok')
        self.assertIn('nicht berechenbar', answer['tables'][0]['rows'][-1]['note'])

    def test_linux_forecast_check_preserves_serializable_manifest_reference(self):
        from scripts.validation.validate_assistant_alwaysdata import REMOTE
        tree = ast.parse(REMOTE)
        block = next(node for node in ast.walk(tree) if isinstance(node, ast.If)
                     and ast.unparse(node.test) == "'forecast_regions' in FUNCTIONS")
        context = {'expected': 'manifest-sha256', 'report': {}, 'datasets': self.data,
                   'FUNCTIONS': {'forecast_regions': True}}
        exec(compile(ast.Module(body=[block], type_ignores=[]), '<linux-forecast-check>', 'exec'), context)
        self.assertEqual(context['expected'], 'manifest-sha256')
        json.dumps({**context['report'], 'manifest_sha256': context['expected']})

    def test_five_regions_all_modes_and_units_have_complete_evidence(self):
        self.args.update(regions=['DEE03', 'DEA12', 'DE300', 'DE600', 'DEA52'], modes=['road', 'rail', 'iww'])
        result = self.result()
        self.assertEqual(len(result['facts']), 120)
        payload = packet(result, self.data)
        self.assertTrue(all(f['fact_id'] in payload['evidence'] for f in result['facts']))
        with self.assertRaises(SelectionError):
            resolve('forecast_regions', {**self.args, 'regions': [*self.args['regions'], 'DEA41'], '_dialogue': intent()}, {}, self.data)

    def test_followup_both_metrics_keeps_regions_and_mode(self):
        old = {'function_id': 'forecast_regions', 'confirmed': {**self.args, 'metrics': ['tonnes']}}
        _, args, _, _ = resolve('forecast_regions', {'metrics': ['tonnes', 'tkm'], '_dialogue': intent('continue', 'unspecified')}, old, self.data)
        self.assertEqual(args, self.args)
        _, args, _, _ = resolve('forecast_regions', {'_dialogue': intent('continue')}, old, self.data)
        self.assertNotIn('observed_years', args)
        self.assertEqual(args['regions'], self.args['regions'])

    def test_legacy_forecast_context_and_new_topic(self):
        old = {'function_id': 'forecast_comparison', 'confirmed': {'region': 'DEE03', 'metric': 'tkm', 'direction': 'inbound', 'observed_years': [2024]}}
        _, args, _, _ = resolve('forecast_regions', {'regions': ['DEE03', 'DEA12'], 'modes': ['rail'], '_dialogue': intent('continue')}, old, self.data)
        self.assertEqual(args['metrics'], ['tkm'])
        self.assertEqual(args['direction'], 'inbound')
        self.assertNotIn('observed_years', args)
        _, args, _, _ = resolve('relation_overview', {'origin': 'DE300', 'destination': 'DE600', '_dialogue': intent()}, old, self.data)
        self.assertNotIn('year', args)
        self.assertNotIn('regions', args)

    def test_evidence_keeps_region_metric_scenario_and_rejects_swap(self):
        result = self.result()
        payload = packet(result, self.data)
        bundles = [entry for key, entry in payload['evidence'].items() if key.startswith('forecast_group_')]
        self.assertEqual(len(bundles), 4)
        self.assertTrue(all(len(entry['fact_ids']) == 4 for entry in bundles))
        for fact in result['facts']:
            evidence = payload['evidence'][fact['fact_id']]
            for field in ['region', 'metric', 'mode', 'basis', 'unit']:
                self.assertEqual(evidence[field], fact[field])
        paragraphs = [{'text': p, 'evidence_ids': ['p'+str(i+1)]} for i,p in enumerate(result['answer']['paragraphs'])]
        self.assertEqual(len(check_prose({'paragraphs': paragraphs}, payload, result, self.data)), 2)
        with self.assertRaises(ValueError):
            check_prose({'paragraphs': [{'text': 'In Duisburg sind es 2040 2.751.683 Tonnen.', 'evidence_ids': ['p1', 'p2']}]}, payload, result, self.data)
        for text in ['In Magdeburg sind es 2019 2.751.683 Tonnen.', 'In Berlin sind es 2040 2.751.683 Tonnen.']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                check_prose({'paragraphs': [{'text': text, 'evidence_ids': ['p1']}]}, payload, result, self.data)

    def test_reported_three_turn_dialogue_executes_complete_queries(self):
        choices = [{**self.args, 'metrics': ['tonnes'], '_dialogue': intent()},
                   {'metrics': ['tonnes', 'tkm'], '_dialogue': intent('continue', 'unspecified')},
                   {'_dialogue': intent('continue')}]
        class Model:
            native_tools = True
            def chat(model, messages, **options):
                if options.get('tools'):
                    return {'role':'assistant','tool_calls':[{'id':'forecast','type':'function','function':{
                        'name':'forecast_regions','arguments':json.dumps(choices.pop(0))}}]}, {}
                payload = json.loads(messages[-1]['content'])
                keys = [k for k in payload['evidence'] if k.startswith('p')]
                return {'role':'assistant','content':json.dumps({'paragraphs':[
                    {'text':payload['evidence'][k]['text'],'evidence_ids':[k]} for k in keys]})}, {}
        service = Service(self.data, Model())
        conversation = None
        for question in ['Wie entwickelt sich bis 2040 die Schienengüterverkehre in Magdeburg und Duisburg?',
                         'Bitte stelle beide Regionen und beide Kennwerte dar', 'na 2040']:
            result, audit = service.analyze(question, conversation=conversation)
            conversation = result['conversation']
            self.assertEqual(result['status'], 'ok')
            self.assertEqual(result['parameters']['regions'], self.args['regions'])
            self.assertEqual(result['answer_mode'], 'native_grounded_chat')
            self.assertNotIn('observed_years', result['parameters'])
        self.assertEqual(result['parameters']['metrics'], ['tonnes', 'tkm'])


if __name__ == '__main__': unittest.main()
