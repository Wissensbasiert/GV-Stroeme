"""Begrenzte Verfügbarkeitsprüfung passender Folgeauswertungen, ohne Modellaufruf."""
import time

import duckdb
from .dialogue import available_years


def missing_alternatives(result, datasets, deadline):
    function = result.get('function_id')
    p = result.get('parameters', {})
    if function not in {'relation', 'rail_goods','relation_overview'} or (result['status'] != 'not_available' and function!='relation_overview'):
        return None
    candidates = []
    years = available_years(datasets, function, p)
    if years and p.get('year') not in years:
        candidates.append(('latest_year', function, {**p, 'year': max(years)}))
    if function == 'relation' and p.get('metric') in {'tonnes', 'tkm'}:
        for mode in ['rail', 'road', 'iww']:
            if mode != p['mode'] and p['year'] in datasets.manifests['b01']['years_by_mode'][mode]:
                candidates.append((mode, 'relation', {**p, 'mode': mode}))
    checks = {}
    until = min(deadline or float('inf'), time.monotonic() + 5)
    for key, fn, parameters in candidates[:3]:
        if time.monotonic() >= until: break
        record = {'function_id': fn, 'parameters': parameters, 'available': False, 'status': 'not_checked'}
        checks[key] = record
        try:
            raw = datasets.query(fn, parameters, timeout_seconds=until-time.monotonic())
        except (ValueError, KeyError, OSError, duckdb.Error):
            continue
        record.update(status=raw['status'], available=(raw.get('value') is not None if fn == 'relation' else any(r.get('value') is not None for r in raw.get('observations' if fn=='relation_overview' else 'details', []))))
    return {'data_snapshot_id': datasets.snapshot_id, 'checks': checks}


def related_data(result, datasets, *, deadline=None):
    if result.get('function_id') != 'road_relation_goods_limit':
        return missing_alternatives(result, datasets, deadline)
    if result.get('data_snapshot_id') != datasets.snapshot_id:
        return None
    p = result['parameters']
    common = {'year': p['year'], 'metric': 'tonnes'}
    requests = [
        ('rail', 'rail_goods', {**common, 'region': p['origin'], 'partner': p['destination'],
                              'direction': 'outbound', 'group': 'ALL', 'nst': None}),
        ('iww', 'relation', {**common, 'origin': p['origin'], 'destination': p['destination'],
                            'mode': 'iww', 'group': 'ALL'}),
        ('origin_goods', 'goods_structure', {**common, 'region': p['origin'], 'mode': 'road',
                                           'directions': ['outbound'], 'granularity': 'C7'}),
        ('destination_goods', 'goods_structure', {**common, 'region': p['destination'], 'mode': 'road',
                                                'directions': ['inbound'], 'granularity': 'C7'})]
    deadline = min(deadline if deadline is not None else float('inf'), time.monotonic() + 5)
    evidence = {'data_snapshot_id': datasets.snapshot_id, 'checks': {}}
    for key, function, parameters in requests:
        record = {'function_id': function, 'parameters': parameters, 'status': 'not_checked', 'available': False}
        evidence['checks'][key] = record
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            continue
        try:
            raw = datasets.query(function, parameters, timeout_seconds=remaining)
        except (ValueError, KeyError, OSError, duckdb.Error):
            # A failed optional check is neither evidence of absence nor an
            # error in the already verified primary answer.
            continue
        record.update(status=raw.get('status', 'unknown'), evidence=raw)
        if key == 'rail':
            record['available'] = any(row.get('value') is not None for row in raw.get('details', []))
        elif key == 'iww':
            record['available'] = raw.get('value') is not None
        else:
            record['available'] = any(row.get('group') and row.get('value') is not None
                                      and row.get('unit') != '%' for row in raw.get('observations', []))
    return evidence
