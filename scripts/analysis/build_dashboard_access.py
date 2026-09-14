"""Separater, hashgebundener Dashboardzugriff; Zwischenstände nur unter C:/tmp."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
from contextlib import ExitStack
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import duckdb
from server.analyseassistent.datasets import digest, read

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ['data/processed/web_forecast_core.json', 'data/processed/web_summary_by_region.json',
           'data/processed/web_maritime.json', 'data/processed/web_intermodal.json',
           'data/crosswalks/crosswalk_spatial_vp2040.json', 'data/crosswalks/crosswalk_nst_vp2040.json',
           'data/crosswalks/vp2040_special_cells_nuts3.json', 'data/processed/dim_nst2007.json']


def build():
    from server.analyseassistent.access import validate_package, field_access_inventory
    matrices = [(s, m, f'data/raw/VP2040/{directory}/VP2040_{prefix}_GV_{label}_NUTS3_Matrix_V01.csv')
                for s, directory, prefix in [('2019_BASE', 'VP2040_2019_GV_NUTS3', '2019'),
                                              ('2040_P1', 'VP2040_2040P1BP_GV_NUTS3', '2040P1BP')]
                for m, label in [('road', 'Strasse'), ('rail', 'Bahn'), ('iww', 'Bischi')]]
    inputs = {p: digest(ROOT/p) for p in [*SOURCES, *(p for _, _, p in matrices)]}
    code = {p: digest(ROOT/p) for p in ['scripts/analysis/build_dashboard_access.py', 'server/analyseassistent/access.py']}
    snapshot = __import__('hashlib').sha256(json.dumps([inputs, code], sort_keys=True).encode()).hexdigest()[:20]
    store = ROOT/'data/analysis/dashboard_access'
    target = store/'releases'/snapshot
    if target.exists():
        raise ValueError('Vorhandenen Datenstand nicht überschreiben')
    with tempfile.TemporaryDirectory(prefix='gv-dashboard-access-', dir='C:/tmp') as temporary, ExitStack() as cleanup:
        stage = Path(temporary)
        con = duckdb.connect(config={'threads': 2, 'memory_limit': '768MB', 'temp_directory': str(stage/'spill')})
        cleanup.callback(con.close)
        spatial = read(ROOT/SOURCES[4])
        special = read(ROOT/SOURCES[6])['cells']
        mapping = []
        for item in spatial:
            cell = item['cell_id']
            region = item.get('nuts3_2024') or item.get('nuts3_2016')
            if item.get('country_iso2') == 'DE' and not region:
                region = special.get(str(cell), {}).get('nuts3_2024')
                if not region and str(cell).endswith('00'):
                    region = next((x.get('nuts3_2024') or x.get('nuts3_2016') for x in spatial
                                   if str(x.get('ags_5stellig', x.get('ags_5digit', ''))) == str(cell)[:5]), None)
            # Foreign cells retain their original VP zone codes, just as in the dashboard.
            mapping.append((cell, region if item.get('country_iso2') == 'DE' and region else str(cell)))
        con.execute('CREATE TABLE cells(cell BIGINT, region VARCHAR)')
        con.executemany('INSERT INTO cells VALUES (?,?)', mapping)
        groups = read(ROOT/SOURCES[5])
        con.execute('CREATE TABLE groups(vp VARCHAR, c7 VARCHAR)')
        con.executemany('INSERT INTO groups VALUES (?,?)', [(str(x['vp40_code']), str(x['nst2007_group7'])) for x in groups])
        counts = []
        for scenario, mode, source in matrices:
            print('Prognosematrix: '+scenario+' / '+mode, flush=True)
            con.execute("CREATE OR REPLACE TABLE raw AS SELECT * FROM read_csv(?, delim=';', header=true, all_varchar=true)", [str(ROOT/source)])
            invalid = con.execute('''SELECT count(*) FROM raw WHERE try_cast(Quellzelle AS BIGINT) IS NULL
                OR try_cast(Zielzelle AS BIGINT) IS NULL OR try_cast(Tonnen AS DOUBLE) IS NULL
                OR try_cast(Tkm AS DOUBLE) IS NULL OR NOT isfinite(try_cast(Tonnen AS DOUBLE))
                OR NOT isfinite(try_cast(Tkm AS DOUBLE)) OR try_cast(Tonnen AS DOUBLE)<0
                OR try_cast(Tkm AS DOUBLE)<0 OR Guetergruppe NOT IN (SELECT vp FROM groups)
                OR try_cast(TEU AS DOUBLE) IS NULL OR NOT isfinite(try_cast(TEU AS DOUBLE)) OR try_cast(TEU AS DOUBLE)<0
                OR try_cast(Ladeeinheiten AS DOUBLE) IS NULL OR NOT isfinite(try_cast(Ladeeinheiten AS DOUBLE)) OR try_cast(Ladeeinheiten AS DOUBLE)<0
                OR try_cast(VerkArt AS INTEGER) IS NULL OR BehTyp IS NULL''').fetchone()[0]
            if invalid: raise ValueError('Ungültige Prognosezellen')
            counts.append({'scenario': scenario, 'mode': mode, 'rows': con.execute('SELECT count(*) FROM raw').fetchone()[0]})
            if counts[-1]['rows'] == 0: raise ValueError('Leere Prognosematrix')
            con.execute('''CREATE OR REPLACE TABLE aggregate AS SELECT ?::VARCHAR AS scenario, ?::VARCHAR AS "mode",
                coalesce(a.region, r.Quellzelle) origin, coalesce(b.region,r.Zielzelle) destination,
                r.Guetergruppe vp, g.c7, r.BehTyp beh,
                sum(cast(Tonnen AS DOUBLE)) tonnes, sum(cast(Tkm AS DOUBLE)) tkm,
                sum(cast(TEU AS DOUBLE)) teu, sum(cast(Ladeeinheiten AS DOUBLE)) load_units,
                sum(CASE WHEN cast(VerkArt AS INTEGER)=2 THEN cast(Tonnen AS DOUBLE) ELSE 0 END) kv_tonnes,
                sum(CASE WHEN cast(VerkArt AS INTEGER)=2 THEN cast(TEU AS DOUBLE) ELSE 0 END) kv_teu,
                sum(CASE WHEN cast(VerkArt AS INTEGER)=2 THEN cast(Ladeeinheiten AS DOUBLE) ELSE 0 END) kv_load_units
                FROM raw r LEFT JOIN cells a ON cast(r.Quellzelle AS BIGINT)=a.cell
                LEFT JOIN cells b ON cast(r.Zielzelle AS BIGINT)=b.cell JOIN groups g ON r.Guetergruppe=g.vp
                GROUP BY ALL''', [scenario, mode])
            out = stage/(scenario+'_'+mode+'.parquet')
            con.execute("COPY aggregate TO '"+str(out).replace("'", "''")+"' (FORMAT PARQUET, COMPRESSION ZSTD)")
        con.close()
        shutil.copyfile(ROOT/SOURCES[0], stage/'forecast_core.json')
        regional = read(ROOT/SOURCES[1])
        compact = {r: {y: {k: v for k, v in p.items() if k in {'by_mode_divisions', 'by_mode_divisions_tkm', 'total_trips'}}
                       for y, p in ys.items()} for r, ys in regional.items()}
        (stage/'regional.json').write_text(json.dumps(compact, ensure_ascii=False), encoding='utf-8')
        for source, name in [(SOURCES[2], 'sea.json'), (SOURCES[3], 'intermodal.json')]:
            shutil.copyfile(ROOT/source, stage/name)
        # The historical dim_nst2007 C7 names disagree with the current VP and
        # frontend classification. Use the actual crosswalk names, not that legacy label set.
        taxonomy=read(ROOT/SOURCES[7])
        taxonomy={'groups_7':{str(x['nst2007_group7']):{'name':x['nst2007_group7_name']} for x in groups},
                  'divisions_20':{k:{'name':v['name']} for k,v in taxonomy['divisions_20'].items()}}
        (stage/'taxonomy.json').write_text(json.dumps(taxonomy,ensure_ascii=False),encoding='utf-8')
        (stage/'vp_groups.json').write_text(json.dumps(groups, ensure_ascii=False), encoding='utf-8')
        (stage/'forecast_cells.json').write_text(json.dumps({str(x['cell_id']):x['cell_name'] for x in spatial if x['country_iso2']!='DE'},ensure_ascii=False),encoding='utf-8')
        (stage/'forecast_cells.json').write_text(json.dumps({str(x['cell_id']):x['cell_name'] for x in spatial if x['country_iso2']!='DE'},ensure_ascii=False),encoding='utf-8')
        coverage = {
            'forecast': {'tool': 'forecast_regions', 'dimensions': ['region', 'mode', 'direction', 'metric', 'C7', 'VP25'], 'years': [2019, 2040]},
            'forecast_relations': {'tool': 'forecast_relation', 'dimensions': ['origin', 'destination', 'mode', 'metric', 'C7', 'VP25'], 'complete_matrices': True},
            'regional_NST20': {'tool': 'dashboard_detail', 'product': 'regional_goods', 'modes': ['rail', 'iww'], 'limit': 'Straße NUTS-3 nur C7; VD3c auf NUTS-2 über road_details.'},
            'sea_goods': {'tool': 'dashboard_detail', 'product': 'sea_goods', 'dimensions': ['port', 'year', 'direction', 'C7', 'NST20', 'tonnes', 'teu']},
            'sea_goods_partners': {'tool': 'dashboard_detail', 'product': 'sea_partners', 'limit': 'Veröffentlichte Dashboard-Partnerliste; keine vollständige Topliste aller Originalpartner.'},
            'intermodal_structure': {'tool': 'dashboard_detail', 'product': 'kv_structure', 'limit': 'Nationale Ladeeinheiten- bzw. Containergrößenstruktur, getrennte Teilmärkte.'},
            'intermodal_relations': {'tool': 'dashboard_detail', 'product': 'kv_relations', 'limit': 'Vorhandene Dashboard-Relationsauswahl, keine Vollständigkeitsbehauptung.'},
            'regional_trips': {'tool': 'dashboard_detail', 'product': 'regional_trips', 'limit': 'Straßenfahrten aus dem veröffentlichten Regionalprofil, ohne Richtung/Güteraufteilung.'},
            'forecast_kv': {'tool': 'dashboard_detail', 'product': 'forecast_kv', 'limit': 'Modellierter KV laut VerkArt=2; keine Auslastung oder Verlagerungspotenziale.'},
            'forecast_container_types': {'tool':'dashboard_detail','product':'forecast_container_types','limit':'Behältertypen gemäß Originalmatrix, keine künstliche KV-Filterung.'},
            'forecast_load_units': {'tool':'dashboard_detail','product':'forecast_load_units','limit':'TEU und Ladeeinheiten laut Matrix ohne Zusatzfilter; KV-Abgrenzung ausdrücklich über forecast_kv.'},
            'existing_access': {'tools': ['relation_overview', 'rail_goods', 'goods_history', 'road_details', 'national', 'node_profile', 'node_partners', 'intermodal_markets', 'toll_month', 'union']},
            'true_limits': ['Keine Straßen-OD-Güterstruktur in den Ist-Daten.', 'Keine künstliche NST20-Aufteilung der Straße auf NUTS-3.',
                            'Keine Prognosehorizonte außer 2040 P1.', 'B07 nur importierte lokale Monatsauszüge.',
                            'Keine Kosten-, Umwelt-, Kapazitäts- oder kausalen Standortaussagen.']}
        (stage/'coverage.json').write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding='utf-8')
        inventory=field_access_inventory(read(ROOT/SOURCES[0]),regional,read(ROOT/SOURCES[2]),read(ROOT/SOURCES[3]))
        (stage/'field_access.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
        report = validate_package(stage)
        report['field_access_passed']=inventory['passed']
        report['unmapped_fields']=inventory['unmapped_fields']
        report['passed']=report['passed'] and inventory['passed']
        report.update(snapshot_id=snapshot, input_sha256=inputs, code_sha256=code, matrices=counts)
        (stage/'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        if not report['passed']: raise ValueError('Dashboardabgleich fehlgeschlagen')
        if any(digest(ROOT/p) != sha for p, sha in {**inputs, **code}.items()):
            raise ValueError('Quellen oder Code während der Prüfung geändert')
        outputs = {p.name: digest(p) for p in stage.iterdir() if p.is_file() and p.name != 'validation.json'}
        manifest = {'snapshot_id': snapshot, 'input_sha256': inputs, 'code_sha256': code, 'output_sha256': outputs}
        (stage/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        target.mkdir(parents=True)
        for p in stage.iterdir():
            if p.is_file():
                shutil.copyfile(p, target/p.name)
                if digest(p) != digest(target/p.name): raise ValueError('Kopierfehler')
        pointer = {'snapshot_id': snapshot, 'manifest_sha256': digest(target/'manifest.json'), 'validation_sha256': digest(target/'validation.json')}
        (store/'current.json').write_text(json.dumps(pointer, indent=2)+'\n', encoding='utf-8')
        return {'snapshot_id': snapshot, **{k: v for k, v in report.items() if k not in {'input_sha256', 'code_sha256', 'matrices'}}}


if __name__ == '__main__':
    print(json.dumps(build(), ensure_ascii=False))
