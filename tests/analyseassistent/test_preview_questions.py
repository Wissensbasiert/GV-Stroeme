"""Editable UI examples and executable contracts; not a live model-routing proof."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from server.analyseassistent.contracts import FUNCTIONS


ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = [
    ('Wie unterscheiden sich Duisburg und Magdeburg beim Güteraufkommen, Modal Split und bei der Güterstruktur?',
     'compare_regions', {'regions': ['DEA12', 'DEE03'], 'year': 2024, 'metric': 'tonnes', 'direction': 'all'}),
    ('Welche Gütergruppen werden auf der Schiene von Köln nach Hamburg transportiert?',
     'relation_overview', {'origin': 'DEA23', 'destination': 'DE600', 'year': 2024,
                           'modes': ['rail'], 'metrics': ['tonnes'], 'include_goods': True}),
    ('Welche Regionen sind Hamburgs wichtigste Partner im Straßengüterverkehr?',
     'partner_ranking', {'region': 'DE600', 'year': 2024, 'mode': 'road', 'metric': 'tonnes',
                         'direction': 'all', 'group': 'ALL', 'top': 10, 'external': True,
                         'partner_scope': 'all'}),
    ('Wie hat sich der Schienengüterverkehr in Magdeburg seit 2016 entwickelt?',
     'transport_history', {'region': 'DEE03', 'start': 2016, 'end': 2025, 'modes': ['rail'],
                           'metric': 'tonnes', 'direction': 'all', 'partner_scope': 'all'}),
    ('Wo wächst das Schienengüteraufkommen laut Prognose von 2019 bis 2040 am stärksten?',
     'forecast_ranking', {'modes': ['rail'], 'metric': 'tonnes', 'direction': 'all',
                          'measure': 'absolute', 'top': 10, 'descending': True}),
]


class ExampleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.examples = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'button' and 'data-ai-question' in attributes:
            self.current = {'question': attributes['data-ai-question'], 'label': ''}

    def handle_data(self, data):
        if self.current is not None:
            self.current['label'] += data

    def handle_endtag(self, tag):
        if tag == 'button' and self.current is not None:
            self.examples.append(self.current)
            self.current = None


class PreviewQuestions(unittest.TestCase):
    def setUp(self):
        self.parser = ExampleParser()
        self.parser.feed((ROOT / 'html/shell-tail.html').read_text(encoding='utf-8'))

    def test_five_supported_topics_without_administrative_template(self):
        self.assertEqual([row['question'] for row in self.parser.examples], [row[0] for row in EXAMPLES])
        self.assertFalse(any('Verwaltungsvorlage' in row['question'] for row in self.parser.examples))

    def test_click_text_matches_visible_question_and_preserves_unicode(self):
        self.assertEqual(len({row['question'] for row in self.parser.examples}), 5)
        for row in self.parser.examples:
            with self.subTest(question=row['question']):
                self.assertEqual(row['label'], row['question'])
                self.assertTrue(row['question'].endswith('?'))
                self.assertNotIn('\ufffd', row['question'])

    def test_each_topic_has_a_valid_completed_data_contract(self):
        # These are explicit test completions, not inferred user years/defaults.
        # Missing years and absolute/relative growth still require dialogue handling.
        for question, function, arguments in EXAMPLES:
            with self.subTest(question=question, function=function):
                self.assertIn(function, FUNCTIONS)
                Draft202012Validator(FUNCTIONS[function][3]).validate(arguments)


if __name__ == '__main__':
    unittest.main()
