"""The corrected airport series must never unlock an older source snapshot."""
import json
from pathlib import Path
import tempfile
import unittest
from scripts.analysis import b0406
from server.analyseassistent import nodes


class AirfreightRevisionTests(unittest.TestCase):
    def test_2025_requires_both_reviewed_sources(self):
        approval = b0406.read(b0406.ROOT/'config/analyseassistent/LUFTVERKEHR_FREIGABE.json')
        sources = approval['airport_flights_2025']['source_sha256']
        with tempfile.TemporaryDirectory(prefix='wbp-air-revision-', dir='C:/tmp') as directory:
            manifest = Path(directory)/'manifest.json'
            for candidate, blocked in [({}, True), (sources, False),
                                       ({**sources, 'data/raw/Luftverkehr/estat_avia_gooa.tsv': 'old'}, True),
                                       ({**sources, 'data/raw/Luftverkehr/estat_avia_gooc.tsv': 'unreviewed'}, True)]:
                manifest.write_text(json.dumps({'input_sha256': candidate}), encoding='utf-8')
                self.assertEqual(b0406.airport_flights_blocked(directory, 2025), blocked)
                self.assertFalse(b0406.airport_flights_blocked(directory, 2024))

    def test_old_airport_snapshot_does_not_fall_back_to_relations(self):
        with tempfile.TemporaryDirectory(prefix='wbp-air-old-', dir='C:/tmp') as directory:
            (Path(directory)/'manifest.json').write_text('{"input_sha256": {}}', encoding='utf-8')
            for scope in ['all', 'domestic', 'international']:
                result = nodes.node_statistics(None, directory, kind='air', node='EDDP', year=2025,
                                               direction='all', metric='flights', partner_scope=scope)
                self.assertEqual(result['status'], 'not_available')
                self.assertIsNone(result['value'])


if __name__ == '__main__':
    unittest.main()
