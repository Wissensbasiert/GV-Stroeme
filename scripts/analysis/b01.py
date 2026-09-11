"""Gemeinsamer B01-Vertrag; keine Änderung der Dashboarddaten."""
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STORE = ROOT / 'data/analysis/b01'
VERSION = '1.0.0'


def sha256(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def save_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                    allow_nan=False) + '\n', encoding='utf-8')


def parse_measure(raw, flag='', kba=False):
    """Referenzsemantik für Tests und kleine Einzelauszüge, keine Nullfüllung."""
    raw = '' if raw is None else str(raw).strip()
    symbol = '' if flag is None else ''.join(str(flag).split())
    if kba and symbol in {'/', '.'}:
        return None, 'suppressed', 'unknown'
    if kba and symbol == '-':
        if raw:
            try:
                if float(raw.replace(',', '.')) != 0:
                    return None, 'conflicting_source', 'unknown'
            except ValueError:
                return None, 'conflicting_source', 'unknown'
        return 0.0, 'confirmed_zero', 'unflagged'
    quality = 'restricted' if kba and symbol == '()' else 'unknown' if symbol not in {'', '-', '0'} else 'unflagged'
    if not raw:
        return None, 'missing_value', quality
    try:
        value = float(raw.replace(',', '.'))
    except ValueError:
        return None, 'invalid_numeric', quality
    if not math.isfinite(value) or value < 0:
        return None, 'invalid_numeric', quality
    if kba and symbol == '0':
        return (0.0, 'rounded_zero', quality) if value == 0 else (None, 'conflicting_source', 'unknown')
    return value, 'reported_zero' if value == 0 else 'observed', quality


def resolve_dataset(store=DEFAULT_STORE):
    store = Path(store)
    if (store / 'manifest.json').exists():
        return store
    pointer = json.loads((store / 'current.json').read_text(encoding='utf-8'))
    path = (store / 'releases' / pointer['snapshot_id']).resolve()
    if path.parent != (store / 'releases').resolve():
        raise ValueError('Ungültiger Datenstandsverweis')
    return path


def query_relation(connection, dataset, *, year, origin, destination, mode,
                   group='ALL', metric='tonnes'):
    """Exakte Relation. ALL summiert belegte C-Gruppen, keine fehlenden Gruppen."""
    dataset = Path(dataset)
    if type(year) is not int or not 1900 <= year <= 2100:
        raise ValueError('Jahr muss eine ganze Zahl zwischen 1900 und 2100 sein')
    manifest = json.loads((dataset / 'manifest.json').read_text(encoding='utf-8'))
    allowed = {'road': {'tonnes', 'tkm', 'trips'},
               'rail': {'tonnes', 'tkm', 'load_units'},
               'iww': {'tonnes', 'tkm', 'load_carriers'}}
    if mode not in allowed or metric not in allowed[mode]:
        raise ValueError('Kennzahl und Verkehrsträger nicht kompatibel')
    if group not in {'ALL', '1', '2', '3', '4', '5', '6', '7'}:
        raise ValueError('Gütergruppe muss ALL oder 1–7 sein')
    if not isinstance(origin, str) or not isinstance(destination, str) or not origin or not destination:
        raise ValueError('Quelle und Ziel müssen nichtleere Textkennungen sein')
    result = {'snapshot_id': manifest['snapshot_id'], 'year': year,
              'origin': origin, 'destination': destination, 'mode': mode,
              'group': group, 'metric': metric,
              'unit': 't' if metric == 'tonnes' else 'tkm' if metric == 'tkm' else 'Anzahl',
              'scope': 'Summe vorhandener veröffentlichter Quellzeilen dieser Relation',
              'value': None, 'known_sum': None,
              'note': 'Fehlende Zeilen sind kein Nullnachweis; keine Aussage zu Route oder vollständigem realem Verkehr.'}
    if (mode == 'road' and group != 'ALL') or year not in manifest['years_by_mode'][mode]:
        return {**result, 'status': 'not_available', 'rows': 0}
    where = 'year_ref=? AND origin_id=? AND dest_id=? AND mode=? AND metric=?'
    args = [str(dataset / 'annual_od.parquet'), year, origin, destination, mode, metric]
    if group != 'ALL':
        where += ' AND group_7_id=?'
        args.append(group)
    cursor = connection.execute(f'''SELECT sum(source_rows) AS rows,
        sum(known_sum) AS known_sum, sum(missing_count) AS missing_count,
        sum(restricted_count) AS restricted_count, sum(unknown_quality_count) AS unknown_quality_count,
        sum(reported_zero_count) AS reported_zero_count,
        sum(rounded_zero_count) AS rounded_zero_count,
        list(DISTINCT group_7_id) AS observed_groups,
        list(DISTINCT source_id) AS source_ids
        FROM read_parquet(?) WHERE {where}''', args)
    record = dict(zip([x[0] for x in cursor.description], cursor.fetchone()))
    if not record['rows']:
        return {**result, 'status': 'missing_row', 'rows': 0}
    result.update(record)
    result['status'] = 'partial' if record['missing_count'] else 'available'
    result['quality'] = ('unknown' if record['unknown_quality_count'] else
                         'restricted' if record['restricted_count'] else 'unflagged')
    result['value'] = None if record['missing_count'] else record['known_sum']
    return result
