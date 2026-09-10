"""Create the minimal terminal overlay; keep source contact details out of delivery."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'data/raw/Intermodal/intermodal_terminals_europe.geojson'
TARGET = ROOT / 'data/processed/web_intermodal_terminals.geojson'
FUNCTIONS = {
    'Schiene / Straße': 'Bimodales Terminal · Schiene / Straße',
    'Wasserstraße / Straße': 'Bimodales Terminal · Wasserstraße / Straße',
    'Trimodal': 'Trimodales Terminal · Schiene / Wasserstraße / Straße',
}


def build():
    raw = SOURCE.read_bytes()
    source = json.loads(raw.decode('utf-8-sig'))
    assert source['type'] == 'FeatureCollection'
    features, excluded, counts = [], Counter(), Counter()
    for feature in source['features']:
        props = feature['properties']
        if props.get('iso2') != 'DE':
            excluded['Außerhalb Deutschlands'] += 1
            continue
        category = props['kategorie']
        if category in ('Containerdepot', 'Anlage stillgelegt'):
            excluded[category] += 1
            continue
        if category not in FUNCTIONS:
            raise ValueError(f'Unknown terminal category: {category}')
        geometry = feature['geometry']
        coords = geometry['coordinates']
        assert geometry['type'] == 'Point' and len(coords) == 2
        assert all(type(value) in (float, int) for value in coords)
        assert -180 <= coords[0] <= 180 and -90 <= coords[1] <= 90
        assert isinstance(props['name'], str) and props['name'].strip()
        features.append({'type': 'Feature', 'geometry': geometry,
                         'properties': {'name': props['name'], 'function': FUNCTIONS[category]}})
        counts[category] += 1
    output = {'type': 'FeatureCollection', 'metadata': {
        'source': SOURCE.relative_to(ROOT).as_posix(),
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'source_url': 'https://www.intermodal-map.com/',
        'classification_field': 'kategorie', 'counts': dict(counts),
        'excluded': dict(excluded),
        'country_filter': {'field': 'iso2', 'value': 'DE'},
        'scope': 'Terminalstandorte in Deutschland laut iso2=DE; unabhängig von Berichtsjahr und Mengenfiltern.'
    }, 'features': features}
    TARGET.write_text(json.dumps(output, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(f'{len(features)} terminals; categories={dict(counts)}; excluded={dict(excluded)}')


if __name__ == '__main__':
    build()
