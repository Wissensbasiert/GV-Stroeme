"""Conversation state and temporal meaning, independent of phrasing heuristics."""
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock
from server.analyseassistent.selection import resolve, SelectionError
from server.analyseassistent.api import log_diagnostic


def intent(context='new', kind='unspecified', count=0, clarification=''):
    return {'context': context, 'clarification': clarification, 'time': {'kind': kind, 'count': count}}


class SelectionRules(unittest.TestCase):
    def setUp(self):
        self.data = SimpleNamespace(names={'DE136': ['Schwarzwald-Baar-Kreis'], 'DE600': ['Hamburg'], 'DE300': ['Berlin']},
                                    manifests={'b01': {'years_by_mode': {'road': list(range(2020, 2025)),
                                                                     'rail': list(range(2020, 2026)), 'iww': list(range(2020, 2025))}}})
        self.old = {'function_id': 'relation_overview', 'confirmed': {'origin': 'DE136', 'destination': 'DE600',
                    'year': 2024, 'modes': ['rail'], 'metrics': ['tkm'], 'include_goods': True}}

    def test_calendar_window_keeps_unavailable_years(self):
        with patch('server.analyseassistent.selection.previous_calendar_year', return_value=2025):
            _, args, _, notes = resolve('relation_history', {'_dialogue': intent('continue', 'last_calendar_years', 5)}, self.old, self.data)
        self.assertEqual((args['start'], args['end'], args['metric']), (2021, 2025, 'tkm'))
        self.assertIn('Kalenderjahre', notes[0])

    def test_available_window_uses_chosen_modes(self):
        _, args, _, _ = resolve('relation_history', {'origin': 'DE136', 'destination': 'DE600',
                         '_dialogue': intent('new', 'last_available_years', 5)}, {}, self.data)
        self.assertEqual((args['start'], args['end']), (2020, 2024))
        _, rail, _, _ = resolve('relation_history', {'_dialogue': intent('continue', 'last_available_years', 5)}, self.old, self.data)
        self.assertEqual((rail['start'], rail['end']), (2021, 2025))

    def test_new_topic_does_not_inherit_old_year_or_metrics(self):
        _, args, _, _ = resolve('relation_overview', {'origin': 'DE300', 'destination': 'DE600',
                               '_dialogue': intent()}, self.old, self.data)
        self.assertNotIn('year', args)
        self.assertEqual(args['metrics'], ['tonnes'])
        self.assertEqual(args['modes'], ['road', 'rail', 'iww'])

    def test_explicit_period_does_not_keep_other_endpoint(self):
        old = {'function_id': 'relation_history', 'confirmed': {'origin': 'DE136', 'destination': 'DE600', 'start': 2020, 'end': 2024}}
        _, args, _, _ = resolve('relation_history', {'start': 2022, '_dialogue': intent('continue', 'explicit')}, old, self.data)
        self.assertNotIn('end', args)

    def test_total_and_inbound_are_preserved_in_same_coordinate_system(self):
        for direction in ['total', 'inbound']:
            old = {'function_id': 'rail_goods', 'confirmed': {'region': 'DE136', 'partner': 'DE600',
                   'year': 2024, 'direction': direction, 'metric': 'tonnes'}}
            _, args, _, _ = resolve('rail_goods', {'_dialogue': intent('continue')}, old, self.data)
            self.assertEqual((args['region'], args['partner'], args['direction']), ('DE136', 'DE600', direction))
            _, directed, _, _ = resolve('relation_overview', {'_dialogue': intent('continue')}, old, self.data)
            if direction == 'total': self.assertNotIn('origin', directed)
            else: self.assertEqual((directed['origin'], directed['destination']), ('DE600', 'DE136'))

    def test_one_calendar_year_is_not_labeled_latest_available(self):
        with patch('server.analyseassistent.selection.previous_calendar_year', return_value=2025):
            _, args, _, notes = resolve('relation_overview', {'_dialogue': intent('continue', 'last_calendar_years', 1)}, self.old, self.data)
        self.assertEqual(args['year'], 2025)
        self.assertIn('vorheriges Kalenderjahr', notes[0])
        self.assertNotIn('verfügbar', notes[0])

    def test_explicit_metric_is_not_overridden_by_default(self):
        _, args, _, _ = resolve('relation_history', {'origin': 'DE136', 'destination': 'DE600',
                              'start': 2020, 'end': 2024, '_dialogue': intent()}, {}, self.data, explicit={'metric': 'tkm'})
        self.assertEqual(args['metric'], 'tkm')

    def test_region_relation_transition_does_not_guess_endpoint(self):
        old = {'function_id': 'region_profile', 'confirmed': {'region': 'DE136', 'year': 2024}}
        _, args, _, _ = resolve('relation_overview', {'_dialogue': intent('continue')}, old, self.data)
        self.assertNotIn('origin', args)
        self.assertNotIn('destination', args)

    def test_bad_codes_schemas_periods_and_ui_conflicts(self):
        cases = [{'origin': 'invented'}, {'metric': 'euros'}, {'start': 2025, 'end': 2020},
                 {'start': 1900, 'end': 2025}, {'_dialogue': intent('new', 'last_calendar_years', 0)},
                 {'start': 2020, '_dialogue': intent('new', 'last_calendar_years', 5)}]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(SelectionError):
                resolve('relation_history', {'_dialogue': intent(), **case}, {}, self.data)
        with self.assertRaises(SelectionError):
            resolve('relation_overview', {'origin': 'DE136', '_dialogue': intent()}, {}, self.data, explicit={'origin': 'DE300'})

    def test_diagnostics_never_log_model_text_or_user_data(self):
        with patch('server.analyseassistent.api.logging.getLogger') as logger:
            log_diagnostic('private identifier', {'status': 'error', 'diagnostic_code': 'AA-M01'},
                           {'failure_stage': 'understanding', 'chat_error': 'secret question and provider response',
                            'parameters': {'private': 'secret'}, 'total_ms': 17})
        text = str(logger.return_value.warning.call_args)
        self.assertNotIn('secret', text)
        self.assertNotIn('private', text)
        self.assertIn('AA-M01', text)


class SemanticConversation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from server.analyseassistent.datasets import Datasets
        cls.data = Datasets(Path(__file__).resolve().parents[2])

    def test_reported_dialogue_uses_persisted_partial_selection(self):
        from server.analyseassistent.service import Service
        from server.analyseassistent.conversation import unpack
        class Model:
            native_tools = True
            first = True
            def chat(self, messages, **options):
                if options.get('tools'):
                    args = {'origin': 'DE136', 'destination': 'DE600', '_dialogue': intent(clarification='Welchen Zeitraum möchten Sie betrachten?')} if self.first else {
                        '_dialogue': intent('continue', 'last_calendar_years', 5)}
                    name = 'relation_overview' if self.first else 'relation_history'
                    self.first = False
                    return {'role': 'assistant', 'tool_calls': [{'id': 'a', 'type': 'function', 'function': {
                        'name': name, 'arguments': json.dumps(args)}}]}, {}
                payload = json.loads(messages[-1]['content'])
                key = next(iter(payload['evidence']))
                return {'role': 'assistant', 'content': json.dumps({'paragraphs': [{'text': payload['evidence'][key]['text'], 'evidence_ids': [key]}]})}, {}
        service = Service(self.data, Model())
        with patch.object(self.data, 'query', wraps=self.data.query) as query:
            first, audit = service.analyze('Welche Güter fließen von meinem Schwarzwald-Baar-Kreis Richtung Hamburg?')
            self.assertEqual(first['status'], 'needs_clarification')
            query.assert_not_called()
            state = unpack(first['conversation'], service.conversation_key, self.data.snapshot_id)
            self.assertEqual(state['confirmed']['origin'], 'DE136')
            self.assertEqual(state['function_id'], 'relation_overview')
            with patch('server.analyseassistent.selection.previous_calendar_year', return_value=2025), \
                 patch('server.analyseassistent.dialogue.complete_plan', side_effect=AssertionError('Old parser must not run')):
                second, audit = service.analyze('die letzten fünf Jahre', conversation=first['conversation'])
            self.assertEqual(second['status'], 'not_available')
            self.assertEqual((second['parameters']['start'], second['parameters']['end']), (2021, 2025))
            self.assertEqual(second['parameters']['destination'], 'DE600')
            self.assertEqual(len(second['facts']), 15)
            self.assertTrue(all(f.get('value') is None for f in second['facts']))
            self.assertTrue(any(f.get('source_status') == 'missing_row' for f in second['facts']))

    def test_model_failure_is_not_a_selection_error(self):
        from server.analyseassistent.service import Service
        from server.analyseassistent.requesty import ModelError
        model = SimpleNamespace(native_tools=True, chat=Mock(side_effect=ModelError('provider failed')))
        result, _ = Service(self.data, model).analyze('Testfrage')
        self.assertEqual(result['diagnostic_code'], 'AA-M01')
        self.assertIn('KI-Dienst', result['answer']['paragraphs'][0])


if __name__ == '__main__': unittest.main()
