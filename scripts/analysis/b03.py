"""B03: vorhandene Güter- und Entfernungsdetails, ausschließlich lokal."""
import json
import re
from pathlib import Path
from scripts.analysis.b01 import ROOT, resolve_dataset, parse_measure
from scripts.analysis.b02 import summarize_months

STORE = ROOT / 'data/analysis/b03'
CROSSWALK = 'data/crosswalks/crosswalk_nst_vp2040.json'
METRICS = {'tonnes': ('TON', 't'), 'tkm': ('TKM', 'tkm'), 'trips': ('FT', 'Fahrten')}
DISTANCES = {'1': 'Nahbereich (bis 50 km)', '2': 'Regionalbereich (51–150 km)',
             '3': 'Fernbereich (mehr als 150 km)'}
FOLDERS = [('VD2', 'outbound', 'Versand_VD2V_NUTS3', 'BE_NUTS3'),
           ('VD2', 'inbound', 'Empfang_VD2E_NUTS3', 'EN_NUTS3'),
           ('VD3c', 'outbound', 'Versand_VD3cV_NUTS2_20Gueter', 'BE_NUTS2'),
           ('VD3c', 'inbound', 'Empfang_VD3cE_NUTS2_20Gueter', 'EN_NUTS2')]


def classification_registry():
    rows = json.loads((ROOT / CROSSWALK).read_text(encoding='utf-8'))
    divisions, groups, vp = {}, {}, {}
    for row in rows:
        code = row['nst2007_division']
        item = {'name': row['nst2007_division_name'], 'group_7_id': row['nst2007_group7']}
        if code in divisions and divisions[code] != item:
            raise ValueError('Widersprüchlicher Crosswalk: ' + code)
        divisions[code] = item
        groups[row['nst2007_group7']] = row['nst2007_group7_name']
        vp[str(row['vp40_code'])] = row['nst2007_group7']
    if set(divisions) != {f'{i:02}' for i in range(1, 21)} or set(groups) != set('1234567'):
        raise ValueError('Unvollständiger Crosswalk')
    return {'source': CROSSWALK, 'divisions': divisions, 'groups': groups, 'vp_to_group': vp,
            'distance_classes': DISTANCES,
            'fine_position_note': 'Originalcode erhalten; Abteilung aus den ersten zwei Zeichen des dreistelligen Codes. Keine erfundenen Feinpositionsnamen.'}


def road_measure(raw, flag):
    # B01-Semantik wiederverwenden; zusätzliche nicht vergleichbare Zeichen sperren.
    if ''.join(flag.split()) in {'X', '__', '|'}:
        return None, 'not_comparable', 'unknown'
    return parse_measure(raw, flag, kba=True)


def records(cursor):
    names = [c[0] for c in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def query_road(connection, dataset, *, product, year, region, direction='outbound',
               population='I', metric='tonnes', partner=None):
    if type(year) is not int or not 1900 <= year <= 2100:
        raise ValueError('Jahr muss eine ganze Zahl zwischen 1900 und 2100 sein')
    if product not in {'VD2', 'VD3c'} or direction not in {'outbound', 'inbound'}:
        raise ValueError('Produkt oder Richtung nicht unterstützt')
    if population not in {'I', 'G'} or metric not in METRICS:
        raise ValueError('Population muss I/G sein; Kennzahl tonnes/tkm/trips')
    dataset = Path(dataset)
    manifest = json.loads((dataset / 'manifest.json').read_text(encoding='utf-8'))
    level = 'NUTS3' if product == 'VD2' else 'NUTS2'
    result = {'snapshot_id': manifest['snapshot_id'], 'product': product, 'year': year,
              'region': region, 'region_level': level, 'direction': direction,
              'metric': metric, 'unit': METRICS[metric][1], 'population': population,
              'vehicle_population': 'In Deutschland zugelassene Güterkraftfahrzeuge, Lastfahrten',
              'population_note': 'Fahrten mit erfassten Inlandskilometern; tkm nur im Inland' if population == 'I'
              else 'Fahrten beziehungsweise Transportwerte insgesamt einschließlich ausländischer Strecken',
              'comparability': 'not_confirmed', 'rows': [], 'value': None, 'known_sum': None,
              'note': 'Keine Straßen-OD, keine Leerfahrten, kein Saldo als Leerfahrtenersatz; I und G nicht addieren.'}
    if partner is not None:
        return {**result, 'status': 'unsupported_relation'}
    pattern = r'DE[A-Z0-9]{3}|XX000' if level == 'NUTS3' else r'DE[A-Z0-9]{2}|XX00'
    if not isinstance(region, str) or not re.fullmatch(pattern, region):
        return {**result, 'status': 'unsupported_region_level'}
    sources = [s for s in manifest['sources'] if s['product'] == product and
               s['direction'] == direction and year in s['years']]
    if not sources:
        return {**result, 'status': 'not_available'}
    rows = records(connection.execute('''SELECT * FROM read_parquet(?) WHERE product=?
        AND year_ref=? AND region_id=? AND direction=? AND population=? AND metric=? ORDER BY class_id''',
        [str(dataset / 'road_details.parquet'), product, year, region, direction, population, metric]))
    expected = set(DISTANCES) if product == 'VD2' else {f'{i:02}' for i in range(1, 21)}
    if len({r['class_id'] for r in rows}) != len(rows):
        raise ValueError('Mehrdeutige Quellzeilen; keine Doppelzählung zulässig')
    registry = json.loads((dataset / 'classification.json').read_text(encoding='utf-8'))
    for row in rows:
        row['label'] = DISTANCES[row['class_id']] if product == 'VD2' else registry['divisions'][row['class_id']]['name']
    missing = sorted(expected - {r['class_id'] for r in rows})
    known = [r['value'] for r in rows if r['value'] is not None]
    complete = bool(rows) and not missing and len(known) == len(rows)
    return {**result, 'status': 'available' if complete else 'partial' if rows else 'missing_row',
            'rows': rows, 'missing_classes': missing, 'sources': sources,
            'quality': 'unknown' if any(r['quality_status'] == 'unknown' for r in rows) else
            'restricted' if any(r['quality_status'] == 'restricted' for r in rows) else 'unflagged',
            'known_sum': sum(known) if known else None, 'value': sum(known) if complete else None,
            'sum_scope': 'Summe veröffentlichter Klassenwerte; unterdrückte Werte bleiben unbekannt.'}


def query_rail(connection, dataset, *, year, region, direction='outbound', partner=None,
               nst=None, group='ALL', metric='tonnes'):
    if type(year) is not int or not 1900 <= year <= 2100:
        raise ValueError('Jahr muss eine ganze Zahl zwischen 1900 und 2100 sein')
    if direction not in {'outbound', 'inbound', 'total'} or metric not in {'tonnes', 'tkm', 'load_units'}:
        raise ValueError('Richtung oder Kennzahl nicht unterstützt')
    if group not in {'ALL', *'1234567'}:
        raise ValueError('C-Gruppe muss ALL oder 1–7 sein')
    if not isinstance(region, str) or not region or (partner is not None and (not isinstance(partner, str) or not partner)):
        raise ValueError('Regionskennungen als nichtleere Texte erforderlich')
    if nst is not None and (not isinstance(nst, str) or not re.fullmatch(r'[0-9]{2}[0-9A-Z]', nst)):
        raise ValueError('NST-Feincode muss als dreistelliger Originalcode übergeben werden')
    dataset = Path(dataset)
    manifest = json.loads((dataset / 'manifest.json').read_text(encoding='utf-8'))
    result = {'snapshot_id': manifest['snapshot_id'], 'year': year, 'region': region,
              'partner': partner, 'direction': direction, 'nst_raw': nst, 'group_7_id': group,
              'metric': metric, 'unit': 't' if metric == 'tonnes' else 'tkm' if metric == 'tkm' else 'Anzahl',
              'comparability': 'not_confirmed', 'change_pct': None,
              'note': 'Summe veröffentlichter Belege. Fehlende Feinpositionen sind kein Nullnachweis; keine harmonisierte Änderungsrate. Binnenrelation bei total einmal gezählt.'}
    clauses, args = ['year_ref=?', 'metric=?'], [year, metric]
    if direction == 'total':
        clauses.append('(origin_id=? OR dest_id=?)' if partner is None else
                       '((origin_id=? AND dest_id=?) OR (dest_id=? AND origin_id=?))')
        args.extend([region, region] if partner is None else [region, partner, region, partner])
    else:
        side, other = ('origin_id', 'dest_id') if direction == 'outbound' else ('dest_id', 'origin_id')
        clauses.append(side + '=?'); args.append(region)
        if partner is not None:
            clauses.append(other + '=?'); args.append(partner)
    if nst is not None:
        clauses.append('nst_raw=?'); args.append(nst)
    if group != 'ALL':
        clauses.append('group_7_id=?'); args.append(group)
    where = ' AND '.join(clauses)
    common = '''sum(source_rows) AS source_rows,sum(known_sum) AS known_sum,
        sum(missing_count) AS missing_count,sum(restricted_count) AS restricted_count,
        sum(unknown_quality_count) AS unknown_quality_count,
        CASE WHEN sum(missing_count)>0 THEN NULL ELSE sum(known_sum) END AS value'''
    params = [str(dataset / 'rail_monthly_details.parquet'), *args]
    months = records(connection.execute('SELECT month,' + common +
        ' FROM read_parquet(?) WHERE ' + where + ' GROUP BY month ORDER BY month', params))
    details = records(connection.execute('SELECT nst_raw,group_7_id,' + common +
        ' FROM read_parquet(?) WHERE ' + where + ' GROUP BY nst_raw,group_7_id ORDER BY nst_raw', params))
    coverage = json.loads((dataset / 'source_coverage.json').read_text(encoding='utf-8'))
    sources = [s for s in coverage if s['mode'] == 'rail' and s['year'] == year]
    known=[r['known_sum'] for r in details if r['known_sum'] is not None]
    return {**result, **summarize_months(months), 'months': months, 'details': details,
            'sources': sources, 'published_sum': sum(known) if known else None,
            'status': summarize_months(months)['status'] if sources else 'not_available'}
