"""Independent source checks for regional KV categories and existing denominators."""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
data = json.loads((ROOT / 'data/processed/web_intermodal.json').read_text(encoding='utf-8'))
regions = {'DE501', 'DEA12', 'DE300'}
checks = 0
for mode, folder, pattern, encoding, origin, destination, category, tonnes, tkm in [
    ('rail', 'SGV OpenData', 'eb_opendata_2024.csv', 'latin-1', 'Versandregion_NUTS2024', 'Empfangsregion_NUTS2024', 'Ladeeinheit', 'Befoerderungsmenge_in_Tonnen', 'Befoerderungsleistung_in_TKM'),
    ('iww', 'IWW OpenData', 'IWW_OpenData_2024.csv', 'utf-8-sig', 'Einladeregion_NUTS3', 'Ausladeregion_NUTS3', 'Container_Groesse', 'Tonnen', 'Tonnen_km'),
]:
    totals = defaultdict(float)
    with (ROOT / 'data/raw' / folder / pattern).open(encoding=encoding, newline='') as handle:
        for row in csv.DictReader(handle, delimiter=';'):
            start, end, code = row[origin], row[destination], row[category]
            if start not in regions and end not in regions:
                continue
            if mode == 'rail':
                key = ('containers_and_swap_bodies' if code.startswith('Container') else
                       'unaccompanied_semitrailers' if code.startswith('Sattelzuganhaenger') else
                       'accompanied_road_vehicles' if code.startswith(('Lastkraftwagen', 'Lastzug')) else None)
            else:
                key = {'1':'c20', '3':'c40', '2':'other_sizes', '4':'other_sizes'}.get(code)
            if key is None:
                continue
            for region in regions:
                if start == end == region:
                    direction = 'binnen'
                elif start == region:
                    direction = 'outbound'
                elif end == region and start:
                    direction = 'inbound'
                else:
                    continue
                for metric, field in [('tonnes',tonnes),('tkm',tkm)]:
                    try:
                        amount = float(row[field].replace(',','.'))
                    except ValueError:
                        amount = 0
                    totals[region,key,direction,metric] += amount
    keys = ['containers_and_swap_bodies','unaccompanied_semitrailers','accompanied_road_vehicles'] if mode == 'rail' else ['c20','c40','other_sizes']
    for region in regions:
        for key in keys:
            for direction in ['outbound','inbound','binnen']:
                for metric in ['tonnes','tkm']:
                    actual = data['scoped_metrics_by_year']['2024'][region][mode][key].get(direction,{}).get(metric,0)
                    expected = totals[region,key,direction,metric]
                    assert math.isclose(actual,expected,rel_tol=1e-12,abs_tol=.001), (mode,region,key,direction,metric,actual,expected)
                    checks += 1

# Every year's national categories must match the previous independent national series.
for year, pack in data['data_by_year'].items():
    for mode, field in [('rail','load_unit_structure'),('iww','container_size_structure')]:
        for key, metrics in pack[mode][field].items():
            if key == 'other_identified_load_units':
                assert all(v == 0 for v in metrics.values())
                continue
            for metric, expected in metrics.items():
                actual = data['scoped_metrics_by_year'][year]['DE'][mode][key]['all'][metric]
                assert math.isclose(actual,expected,rel_tol=1e-12,abs_tol=.001), (year,mode,key,metric)
                checks += 1
print(f'PASS: {checks} KV source checks, Bremen/Duisburg/Berlin, both metrics, three directions, all national years.')
