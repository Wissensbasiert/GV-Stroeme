"""B01: vollständige Quellbelege und jährliche OD mit Qualitätszuständen.

Schreibt ausschließlich data/analysis/b01. DuckDB-/Stagingdateien liegen in C:/tmp.
Die Veröffentlichung eines lokalen Datenstands erfolgt über current.json zuletzt.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import uuid
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import duckdb
from scripts.analysis.b01 import ROOT, DEFAULT_STORE, VERSION, literal, save_json, sha256


def source_list(root):
    road = root / 'data/raw/Straße/KBA/VE7_Verflechtung_NUTS3/ve7_2010_2024.csv'
    sources = [('road', road, 'utf-8')]
    for mode, folder, pattern, encoding in [
        ('rail', 'SGV OpenData', 'eb_opendata_*.csv', 'latin-1'),
        ('iww', 'IWW OpenData', 'IWW_OpenData_*.csv', 'utf-8')]:
        files = sorted((root / 'data/raw' / folder).glob(pattern))
        if not files:
            raise ValueError(f'Keine Rohquellen für {mode}')
        sources.extend((mode, path, encoding) for path in files)
    return sources


def normalized_select(mode, source_id):
    q = lambda name: 'CAST(NULL AS VARCHAR)' if name is None else 'NULLIF(TRIM("' + name + '"), \'\')'
    if mode == 'road':
        names = ['Jahr', None, 'Beladeregion', 'Entladeregion', None, None,
                 None, 'Hauptverkehrsbeziehung', 'Tonnen', 'Tkm', 'Fahrten',
                 'ZS_Tonnen', 'ZS_Tkm', 'ZS_Fahrten']
        count_metric = 'trips'
    elif mode == 'rail':
        names = ['Referenzzeitraum_Jahr', 'Referenzzeitraum_Monat',
                 'Versandregion_NUTS2024', 'Empfangsregion_NUTS2024', None, None,
                 'Guetergruppe_NST2007', 'Verkehrsbeziehung',
                 'Befoerderungsmenge_in_Tonnen', 'Befoerderungsleistung_in_TKM',
                 'Anzahl_Ladeeinheiten', None, None, None]
        count_metric = 'load_units'
    else:
        names = ['Referenzzeitraum_Jahr', 'Referenzzeitraum_Monat',
                 'Einladeregion_NUTS3', 'Ausladeregion_NUTS3',
                 'Einladeregion_ISO', 'Ausladeregion_ISO', 'NST2007',
                 'Verkehrsbeziehung', 'Tonnen', 'Tonnen_km',
                 'Anzahl_Ladungstraeger', None, None, None]
        count_metric = 'load_carriers'
    fields = ['year_text', 'month_text', 'origin_nuts', 'dest_nuts',
              'origin_country', 'dest_country', 'nst_raw', 'traffic_relationship',
              'raw_tonnes', 'raw_tkm', 'raw_count', 'flag_tonnes', 'flag_tkm', 'flag_count']
    return ('SELECT ' + literal(source_id) + ' AS source_id, row_number() OVER () AS source_record, '
            + literal(mode) + ' AS mode, ' + literal(count_metric) + ' AS count_metric, '
            + ', '.join(q(name) + ' AS ' + alias for name, alias in zip(names, fields)) + ' FROM incoming')


# Long form retains each metric's original spelling and flag independently.
LONG_SQL = '''
WITH long AS (
 SELECT *, 'tonnes' AS metric, raw_tonnes AS raw_value, flag_tonnes AS raw_flag FROM normalized
 UNION ALL SELECT *, 'tkm', raw_tkm, flag_tkm FROM normalized
 UNION ALL SELECT *, count_metric, raw_count, flag_count FROM normalized
), parsed AS (
 SELECT *, TRY_CAST(REPLACE(raw_value, ',', '.') AS DOUBLE) AS parsed_value,
 REPLACE(COALESCE(raw_flag,''),' ','') AS flag FROM long
), classified AS (
 SELECT *, CASE
 WHEN mode='road' AND flag IN ('/','.') THEN 'suppressed'
 WHEN mode='road' AND flag='-' AND (raw_value IS NULL OR parsed_value=0) THEN 'confirmed_zero'
 WHEN mode='road' AND flag='-' THEN 'conflicting_source'
 WHEN raw_value IS NULL THEN 'missing_value'
 WHEN parsed_value IS NULL OR NOT isfinite(parsed_value) OR parsed_value<0 THEN 'invalid_numeric'
 WHEN mode='road' AND flag='0' AND parsed_value<>0 THEN 'conflicting_source'
 WHEN mode='road' AND flag='0' THEN 'rounded_zero'
 WHEN parsed_value=0 THEN 'reported_zero'
 ELSE 'observed' END AS value_status,
 CASE WHEN mode='road' AND flag='()' THEN 'restricted'
 WHEN flag NOT IN ('','-','0') THEN 'unknown' ELSE 'unflagged' END AS quality_status
 FROM parsed
)
SELECT source_id, source_record, mode, year_ref, month_text, origin_nuts, dest_nuts,
 origin_country, dest_country, origin_id, dest_id, legacy_scope,
 nst_raw, group_7_id, traffic_relationship, metric, raw_value, raw_flag,
 value_status, CASE WHEN value_status='conflicting_source' THEN 'unknown' ELSE quality_status END AS quality_status,
 CASE WHEN value_status='confirmed_zero' THEN 0
 WHEN value_status IN ('suppressed','conflicting_source','missing_value','invalid_numeric') THEN NULL
 ELSE parsed_value END AS value
FROM classified
'''

ANNUAL_SQL = '''SELECT year_ref, origin_id, dest_id, mode, group_7_id, metric, source_id,
 legacy_scope, count(*) AS source_rows, sum(value) AS known_sum,
 count(*) FILTER (WHERE value IS NULL) AS missing_count,
 count(*) FILTER (WHERE quality_status='restricted') AS restricted_count,
 count(*) FILTER (WHERE quality_status='unknown') AS unknown_quality_count,
 count(*) FILTER (WHERE value_status='reported_zero') AS reported_zero_count,
 count(*) FILTER (WHERE value_status='rounded_zero') AS rounded_zero_count,
 list(DISTINCT raw_flag) FILTER (WHERE raw_flag IS NOT NULL) AS source_flags,
 list(DISTINCT value_status) AS source_value_states,
 CASE WHEN count(*) FILTER (WHERE value IS NULL)>0 THEN NULL ELSE sum(value) END AS value,
 CASE WHEN count(*) FILTER (WHERE value IS NULL)>0 THEN 'partial' ELSE 'available' END AS status
 FROM read_parquet(?) GROUP BY ALL'''


def build(root=ROOT, store=DEFAULT_STORE):
    root, store = Path(root), Path(store)
    # Explicit probe avoids lengthy tempfile retries in restricted Windows environments.
    temp_root = Path('C:/tmp')
    temp_root.mkdir(parents=True, exist_ok=True)
    probe = temp_root / ('wbp-b01-writecheck-' + uuid.uuid4().hex)
    probe.mkdir()
    probe.rmdir()
    sources = []
    for mode, path, encoding in source_list(root):
        print(f'Prüfe Quellenstand: {path.name}', flush=True)
        sources.append({'id': f'S{len(sources)+1:03}', 'mode': mode,
                        'path': path.relative_to(root).as_posix(), 'encoding': encoding,
                        'sha256': sha256(path), 'bytes': path.stat().st_size})
    code_hashes = {name: sha256(ROOT / name) for name in
                   ['scripts/pipelines/build_b01_analysis.py', 'scripts/analysis/b01.py',
                    'scripts/analysis/query_b01.py','scripts/validation/validate_b01_analysis.py',
                    'scripts/validation/check_b0103_regressions.py']}
    identity = json.dumps([VERSION, sources, code_hashes], sort_keys=True).encode()
    snapshot = hashlib.sha256(identity).hexdigest()[:20]
    destination = store / 'releases' / snapshot
    if destination.exists():
        raise FileExistsError(f'Datenstand existiert bereits: {destination}; zuerst validieren, nicht überschreiben.')
    Path('C:/tmp').mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='wbp-b01-', dir='C:/tmp') as tmp:
        stage = Path(tmp) / 'release'
        stage.mkdir()
        con = duckdb.connect(str(Path(tmp) / 'work.duckdb'))
        try:
            con.execute("SET memory_limit='1GB'")
            con.execute('SET threads=1')
            con.execute('SET preserve_insertion_order=true')
            for source in sources:
                print(f"Lese {source['id']} {source['path']}", flush=True)
                con.execute('CREATE OR REPLACE VIEW incoming AS SELECT * FROM read_csv('
                            + literal((root / source['path']).as_posix())
                            + ", delim=';', header=true, all_varchar=true, sample_size=-1, encoding="
                            + literal(source['encoding']) + ')')
                sql = normalized_select(source['mode'], source['id'])
                con.execute(('CREATE TABLE staged_rows AS ' if source == sources[0]
                             else 'INSERT INTO staged_rows ') + sql)
                source['records'] = con.execute('SELECT count(*) FROM incoming').fetchone()[0]
            con.execute('''CREATE TABLE normalized AS SELECT *, CAST(year_text AS INTEGER) AS year_ref,
                COALESCE(origin_nuts,origin_country) AS origin_id,
                COALESCE(dest_nuts,dest_country) AS dest_id,
                origin_nuts IS NOT NULL AND dest_nuts IS NOT NULL AS legacy_scope,
                CASE WHEN mode='road' THEN 'ALL'
                  WHEN substr(lpad(nst_raw,3,'0'),1,2) IN ('01','02','03') THEN '1'
                  WHEN substr(lpad(nst_raw,3,'0'),1,2) IN ('04','05','06') THEN '2'
                  WHEN substr(lpad(nst_raw,3,'0'),1,2) IN ('07','08','09') THEN '3'
                  WHEN substr(lpad(nst_raw,3,'0'),1,2)='10' THEN '4'
                  WHEN substr(lpad(nst_raw,3,'0'),1,2) IN ('11','12','13') THEN '5'
                  WHEN substr(lpad(nst_raw,3,'0'),1,2)='14' THEN '6'
                  WHEN substr(lpad(nst_raw,3,'0'),1,2) IN ('15','16','17','18','19','20') THEN '7'
                  ELSE NULL END AS group_7_id FROM staged_rows''')
            # The actual sources use three-digit NST positions. Reject drift instead of misclassifying.
            unknown = con.execute("SELECT count(*) FROM normalized WHERE mode<>'road' AND group_7_id IS NULL").fetchone()[0]
            if unknown:
                raise ValueError(f'{unknown} unbekannte NST-Zuordnungen; Quellenvertrag prüfen')
            raw = stage / 'source_values.parquet'
            con.execute('COPY (' + LONG_SQL + ') TO ' + literal(raw.as_posix())
                        + ' (FORMAT PARQUET, COMPRESSION ZSTD)')
            con.execute('CREATE TABLE annual AS ' + ANNUAL_SQL, [str(raw)])
            con.execute('COPY annual TO ' + literal((stage / 'annual_od.parquet').as_posix())
                        + ' (FORMAT PARQUET, COMPRESSION ZSTD)')
            manifest = {'schema_version': VERSION, 'snapshot_id': snapshot,
                        'created_at': datetime.now(timezone.utc).isoformat(),
                        'scope': 'Alle vorhandenen VE7-/SGV-/IWW-Quellzeilen, keine Top-Kürzung; kein vollständiger Realverkehrsnachweis.',
                        'sources': sources, 'code_sha256': code_hashes,
                        'years_by_mode': {}, 'row_counts': {},
                        'coverage': 'published_rows_only',
                        'missing_row_policy': 'Kein Nullnachweis; durch Abfrage als missing_row ausgeben.',
                        'zero_policy': 'reported_zero ist eine veröffentlichte numerische Null, kein unabhängiger Nachweis exakter Verkehrsfreiheit.',
                        'source_record': '1-basierte logische CSV-Datenzeile je Quelle, ohne Kopfzeile.',
                        'validation': 'Separater Prüfbericht validation.json erforderlich.'}
            for mode in ['road','rail','iww']:
                manifest['years_by_mode'][mode] = [x[0] for x in con.execute(
                    'SELECT DISTINCT year_ref FROM normalized WHERE mode=? ORDER BY 1', [mode]).fetchall()]
            manifest['row_counts']['raw_records'] = con.execute('SELECT count(*) FROM normalized').fetchone()[0]
            manifest['row_counts']['source_values'] = con.execute('SELECT count(*) FROM read_parquet(?)', [str(raw)]).fetchone()[0]
            manifest['row_counts']['annual_records'] = con.execute('SELECT count(*) FROM annual').fetchone()[0]
            manifest['row_counts']['outside_legacy_scope'] = con.execute('SELECT count(*) FROM normalized WHERE NOT legacy_scope').fetchone()[0]
            manifest['value_states'] = dict(con.execute('SELECT value_status,count(*) FROM read_parquet(?) GROUP BY 1', [str(raw)]).fetchall())
            manifest['quality_states'] = dict(con.execute('SELECT quality_status,count(*) FROM read_parquet(?) GROUP BY 1', [str(raw)]).fetchall())
            manifest['output_sha256'] = {p.name: sha256(p) for p in stage.glob('*.parquet')}
            save_json(stage / 'manifest.json', manifest)
        finally:
            con.close()
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(stage, destination)
    print(f'B01 aufgebaut: {destination}', flush=True)
    print('Noch nicht als current aktiviert. Prüfskript mit --dataset und --activate ausführen.', flush=True)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--store', type=Path, default=DEFAULT_STORE)
    args = parser.parse_args()
    build(args.root, args.store)
