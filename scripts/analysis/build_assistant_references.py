"""Kleine Namens- und Methodikreferenz aus vorhandenen Originalpaketen ableiten."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = 'config/analyseassistent/DARSTELLUNGSREFERENZEN.json'


def build(root=ROOT):
    sources = ['data/processed/web_airfreight.json',
               'data/processed/web_summary_by_region.json',
               'data/processed/nuts3_de_2024.geojson']
    contents = {name: (root/name).read_bytes() for name in sources}
    air, summary, boundaries = [json.loads(contents[name]) for name in sources]
    districts = {feature['properties']['NUTS_ID'] for feature in boundaries['features']}
    selected = {code for code, years in summary.items() if '2024' in years}
    assert districts <= selected
    return {'schema_version': 1,
            'source_sha256': {name: hashlib.sha256(content).hexdigest() for name, content in contents.items()},
            # Geographic countries are deliberately excluded: statistical countries differ.
            'airport_names': {code: row['name'] for code, row in sorted(air['airports'].items())},
            'regional_scope': {'year': 2024, 'entry_count': len(selected),
                               'district_count': len(selected & districts),
                               'other_codes': sorted(selected-districts)}}


def serialized(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)+'\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    content = serialized(build())
    if args.check:
        assert (ROOT/TARGET).read_text(encoding='utf-8') == content
        print('Darstellungsreferenzen entsprechen den Originalpaketen.')
    else:
        (ROOT/TARGET).write_text(content, encoding='utf-8')
        print('Darstellungsreferenzen erzeugt.')
