"""B03 aus geprüftem B01/B02 und vorhandenen VD2-/VD3c-Dateien aufbauen."""
import argparse
import csv
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
from scripts.analysis.b01 import ROOT, DEFAULT_STORE, resolve_dataset, save_json, sha256, literal
from scripts.analysis.b02 import STORE as B02_STORE
from scripts.analysis.b03 import STORE, FOLDERS, METRICS, CROSSWALK, classification_registry, road_measure

CODE = ['scripts/pipelines/build_b03_analysis.py', 'scripts/analysis/b03.py',
        'scripts/analysis/b01.py', 'scripts/analysis/b02.py','scripts/analysis/query_b03.py',
        'scripts/validation/validate_b03_analysis.py','scripts/validation/check_b0103_regressions.py']


def checked_dependency(store):
    path = resolve_dataset(store)
    manifest = json.loads((path / 'manifest.json').read_text(encoding='utf-8'))
    validation = json.loads((path / 'validation.json').read_text(encoding='utf-8'))
    if validation['snapshot_id'] != manifest['snapshot_id'] or not validation['passed']:
        raise ValueError('Abhängigkeit nicht geprüft: ' + str(path))
    for name, digest in manifest['output_sha256'].items():
        if sha256(path / name) != digest:
            raise ValueError('Veränderte Abhängigkeit: ' + name)
    for name, digest in manifest['code_sha256'].items():
        if sha256(ROOT / name) != digest:
            raise ValueError('Veränderter Code der Abhängigkeit: ' + name)
    return path, manifest


def road_sources():
    sources = []
    for product, direction, folder, field in FOLDERS:
        parent = ROOT / 'data/raw/Straße/KBA' / folder
        paths = sorted(parent.glob('puf_*.csv'))
        if not paths:
            raise ValueError('Keine Dateien: ' + str(parent))
        document = next(parent.glob('referenz*.pdf')).relative_to(ROOT).as_posix()
        for path in paths:
            sources.append({'id': f'K{len(sources)+1:03}', 'path': path.relative_to(ROOT).as_posix(),
                'sha256': sha256(path), 'encoding': 'utf-8-sig', 'product': product,
                'direction': direction, 'region_field': field,
                'region_level': 'NUTS3' if product == 'VD2' else 'NUTS2',
                'documentation': document, 'publisher': 'KBA',
                'territory_status': 'year_specific_reference_not_individually_harmonized',
                'revision_status': 'not_documented', 'comparability': 'not_confirmed'})
    return sources


def build(store=STORE):
    probe = Path('C:/tmp') / ('wbp-b03-probe-' + uuid.uuid4().hex)
    probe.mkdir()
    probe.rmdir()
    print('Prüfe B01/B02 und Quellenprüfsummen', flush=True)
    b01, bm = checked_dependency(DEFAULT_STORE)
    b02, tm = checked_dependency(B02_STORE)
    if tm['b01']['snapshot_id'] != bm['snapshot_id'] or tm['b01']['manifest_sha256'] != sha256(b01 / 'manifest.json'):
        raise ValueError('B01/B02 passen nicht zusammen')
    for source in bm['sources']:
        if sha256(ROOT / source['path']) != source['sha256']:
            raise ValueError('Rohdaten verändert; zuerst B01/B02 erneuern')
    for name, digest in tm['document_sha256'].items():
        if sha256(ROOT / name) != digest:
            raise ValueError('B02-Quellbeschreibung verändert')
    sources = road_sources()
    documents = {s['documentation']: sha256(ROOT / s['documentation']) for s in sources}
    documents[CROSSWALK] = sha256(ROOT / CROSSWALK)
    identity = {'b01': {'snapshot_id': bm['snapshot_id'], 'manifest_sha256': sha256(b01 / 'manifest.json')},
                'b02': {'snapshot_id': tm['snapshot_id'], 'manifest_sha256': sha256(b02 / 'manifest.json')},
                'sources': sources, 'document_sha256': documents,
                'code_sha256': {p: sha256(ROOT / p) for p in CODE}}
    snapshot = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:20]
    destination = Path(store) / 'releases' / snapshot
    if destination.exists():
        print('B03 bereits vorhanden; erneut prüfen: ' + str(destination), flush=True)
        return destination
    registry = classification_registry()
    with tempfile.TemporaryDirectory(prefix='wbp-b03-', dir='C:/tmp') as tmp:
        stage = Path(tmp) / 'release'; stage.mkdir()
        with duckdb.connect(str(Path(tmp) / 'work.duckdb')) as con:
            con.execute("SET memory_limit='1GB'"); con.execute('SET threads=1')
            print('Erzeuge monatliche Schienen-Feinpositionen', flush=True)
            con.execute('''CREATE TABLE rail AS SELECT source_id,year_ref,CAST(month_text AS INTEGER) AS month,
                origin_id,dest_id,nst_raw,group_7_id,traffic_relationship,legacy_scope,metric,
                count(*) AS source_rows,sum(value) AS known_sum,
                count(*) FILTER(WHERE value IS NULL) AS missing_count,
                count(*) FILTER(WHERE quality_status='restricted') AS restricted_count,
                count(*) FILTER(WHERE quality_status='unknown') AS unknown_quality_count,
                list(DISTINCT value_status) AS source_value_states,
                CASE WHEN count(*) FILTER(WHERE value IS NULL)>0 THEN NULL ELSE sum(value) END AS value
                FROM read_parquet(?) WHERE mode='rail' GROUP BY ALL''', [str(b01 / 'source_values.parquet')])
            codes = con.execute('SELECT DISTINCT nst_raw,group_7_id FROM rail').fetchall()
            for code, group in codes:
                if len(code) != 3 or registry['divisions'].get(code[:2], {}).get('group_7_id') != group:
                    raise ValueError('Unbekannte oder abweichende NST-Zuordnung: ' + str(code))
            registry['observed_rail_positions'] = sorted(code for code, group in codes)
            con.execute('COPY rail TO ' + literal(stage / 'rail_monthly_details.parquet') + ' (FORMAT PARQUET, COMPRESSION ZSTD)')
            # Small road sources are parsed with the reference semantics; raw spelling remains intact.
            columns = ['source_id','source_record','product','year_ref','region_id','region_level','direction',
                       'satzart1','satzart2','class_raw','class_id','group_7_id','population','metric',
                       'source_field','unit','raw_value','raw_flag','value','value_status','quality_status']
            intermediate = Path(tmp) / 'road.jsonl'
            with intermediate.open('w', encoding='utf-8') as out:
                for source in sources:
                    years, seen, count = set(), set(), 0
                    with (ROOT / source['path']).open(encoding=source['encoding'], newline='') as handle:
                        for count, row in enumerate(csv.DictReader(handle, delimiter=';'), 1):
                            year = int(row['JAHR']); years.add(year)
                            region = row[source['region_field']]
                            code = row['FT_ENTF3'] if source['product'] == 'VD2' else row['GUART']
                            if row['SATZART1'] != ('3' if source['direction'] == 'outbound' else '2') or row['SATZART2'] != '1':
                                raise ValueError('Unerwartete Satzart: ' + source['path'])
                            class_id = code if source['product'] == 'VD2' else f'{int(code):02}'
                            if (source['product'] == 'VD2' and code not in {'1','2','3'}) or (source['product'] == 'VD3c' and class_id not in registry['divisions']):
                                raise ValueError('Unbekannte Klasse')
                            key = (year, region, class_id)
                            if key in seen:
                                raise ValueError('Doppelte Klasse in Rohquelle')
                            seen.add(key)
                            for population in ['I', 'G']:
                                for metric, (prefix, unit) in METRICS.items():
                                    field = prefix + '_' + population
                                    raw, flag = row[field], row[field + '_ZS']
                                    value, status, quality = road_measure(raw, flag)
                                    values = [source['id'],count,source['product'],year,region,source['region_level'],
                                        source['direction'],row['SATZART1'],row['SATZART2'],code,class_id,
                                        registry['divisions'][class_id]['group_7_id'] if source['product']=='VD3c' else None,
                                        population,metric,field,unit,raw,flag,value,status,quality]
                                    out.write(json.dumps(dict(zip(columns, values)), ensure_ascii=False) + '\n')
                    if not count or len(years) != 1:
                        raise ValueError('Leere oder mehrjährige PUF-Datei')
                    source.update(years=sorted(years), records=count)
                    print('Erschlossen: ' + source['path'], flush=True)
            # Explicit schema protects numeric-looking codes and empty/raw strings.
            schema = {name: 'BIGINT' if name in {'source_record','year_ref'} else 'DOUBLE' if name == 'value' else 'VARCHAR' for name in columns}
            sql_schema = '{' + ','.join(literal(k)+':'+literal(v) for k,v in schema.items()) + '}'
            con.execute('CREATE TABLE road AS SELECT * FROM read_json(' + literal(intermediate) + ', columns=' + sql_schema + ', format=\'newline_delimited\')')
            con.execute('COPY road TO ' + literal(stage / 'road_details.parquet') + ' (FORMAT PARQUET, COMPRESSION ZSTD)')
            save_json(stage / 'classification.json', registry)
            shutil.copyfile(b02 / 'source_coverage.json', stage / 'source_coverage.json')
            manifest = {**identity, 'snapshot_id': snapshot, 'schema_version': '1.0.0',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'row_counts': {'rail_monthly_details': con.execute('SELECT count(*) FROM rail').fetchone()[0],
                               'road_details': con.execute('SELECT count(*) FROM road').fetchone()[0]},
                'scope': 'Vorhandene SGV-Feinpositionen und VD2/VD3c, beide Richtungen, TON/TKM/FT mit I/G. Keine Straßen-OD-Güteraufteilung.',
                'source_record': '1-basierte logische CSV-Datenzeile ohne Kopfzeile; SGV-Einzelbelege in zugehörigem B01.',
                'road_units': 'TON=t, TKM=tkm, FT=Fahrten; keine Skalierung. KM-Felder nicht erschlossen.',
                'output_sha256': {p.name: sha256(p) for p in stage.iterdir()}}
            save_json(stage / 'manifest.json', manifest)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(stage, destination)
    print('B03 aufgebaut, noch nicht aktiviert: ' + str(destination), flush=True)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store', type=Path, default=STORE)
    build(parser.parse_args().store)
