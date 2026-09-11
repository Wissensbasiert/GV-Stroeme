"""Begrenzte Verfügbarkeitsprüfung passender Folgeauswertungen, ohne Modellaufruf."""
import time

import duckdb


def related_data(result, datasets, *, deadline=None):
    if result.get('function_id') != 'road_relation_goods_limit':
        return None
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
