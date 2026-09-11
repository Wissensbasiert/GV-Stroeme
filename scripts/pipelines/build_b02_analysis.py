"""B02 aus geprüftem B01; Monatsdaten und Quellenabdeckung, keine Webausgabe."""
import argparse
import csv
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import uuid
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import duckdb
from scripts.analysis.b01 import ROOT,DEFAULT_STORE,literal,resolve_dataset,save_json,sha256
from scripts.analysis.b02 import STORE,MONTHLY_SQL

DOCS=['data/raw/SGV OpenData/SGV_OpenData_Datensatzbeschreibung_2026.pdf',
      'data/raw/IWW OpenData/IWW OpenData Datensatzbeschreibung_Binnenschiff.pdf']


def source_contract(source,year,header):
    mode=source['mode']
    documented=(2016 if year<=2020 else 2021 if year<=2023 else 2024) if mode=='rail' else None
    region_fields=[h for h in header if 'NUTS' in h or h in {'Beladeregion','Entladeregion'}]
    conflict=mode=='rail' and documented!=2024 and any('2024' in h for h in region_fields)
    return {'publisher':'KBA' if mode=='road' else 'Destatis',
        'region_fields':region_fields,'documented_nuts_version':documented,
        'territory_status':'header_documentation_conflict' if conflict else
            'documented_not_individually_harmonized' if mode=='rail' else 'not_documented_in_checked_source',
        'territory_evidence':DOCS[0]+' Seite 1' if mode=='rail' else DOCS[1]+' Seiten 4, 7–8' if mode=='iww' else source['path'],
        'revision_status':'not_documented','comparability':'not_confirmed',
        'note':'Gleicher Regionscode beweist keine unveränderte Abgrenzung. Keine Ursachenbehauptung aus einem Mengensprung.'}


def build(b01_store=DEFAULT_STORE,store=STORE):
    temp=Path('C:/tmp');temp.mkdir(exist_ok=True,parents=True)
    probe=temp/('wbp-b02-writecheck-'+uuid.uuid4().hex);probe.mkdir();probe.rmdir()
    b01=resolve_dataset(b01_store).resolve()
    bm=json.loads((b01/'manifest.json').read_text(encoding='utf-8'))
    validation=json.loads((b01/'validation.json').read_text(encoding='utf-8'))
    if not validation['passed'] or validation['snapshot_id']!=bm['snapshot_id']:
        raise ValueError('B01 muss zuvor bestanden haben')
    for name,digest in bm['output_sha256'].items():
        if sha256(b01/name)!=digest: raise ValueError('B01-Ausgabe verändert: '+name)
    for source in bm['sources']:
        if sha256(ROOT/source['path'])!=source['sha256']:
            raise ValueError('Rohquelle verändert; zuerst B01 erneuern: '+source['path'])
    for name,digest in bm['code_sha256'].items():
        if sha256(ROOT/name)!=digest: raise ValueError('B01-Code verändert; zuerst B01 erneuern')
    code={p:sha256(ROOT/p) for p in ['scripts/pipelines/build_b02_analysis.py','scripts/analysis/b02.py','scripts/analysis/b01.py',
          'scripts/analysis/query_b02.py','scripts/validation/validate_b02_analysis.py','scripts/validation/check_b0103_regressions.py']}
    documents={p:sha256(ROOT/p) for p in DOCS}
    dependency={'snapshot_id':bm['snapshot_id'],'manifest_sha256':sha256(b01/'manifest.json'),
                'output_sha256':bm['output_sha256']}
    identity={'b01':dependency,'code_sha256':code,'document_sha256':documents}
    snapshot=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()[:20]
    destination=Path(store)/'releases'/snapshot
    if destination.exists():
        print('B02-Stand existiert; Prüfung wiederholen: '+str(destination),flush=True)
        return destination
    coverage=[]
    with tempfile.TemporaryDirectory(prefix='wbp-b02-',dir=temp) as tmp:
        stage=Path(tmp)/'release';stage.mkdir()
        with duckdb.connect(str(Path(tmp)/'work.duckdb')) as con:
            con.execute("SET memory_limit='1GB'");con.execute('SET threads=1')
            con.execute('CREATE VIEW evidence AS SELECT * FROM read_parquet('+literal(b01/'source_values.parquet')+')')
            invalid=con.execute("SELECT count(*) FROM evidence WHERE mode<>'road' AND (month_text IS NULL OR NOT regexp_full_match(month_text,'(0?[1-9]|1[0-2])'))").fetchone()[0]
            if invalid: raise ValueError(f'{invalid} ungültige Monatswerte')
            print('Erzeuge vollständige monatliche Relationen aus B01',flush=True)
            con.execute('CREATE TABLE monthly AS '+MONTHLY_SQL)
            con.execute('COPY monthly TO '+literal(stage/'monthly_od.parquet')+' (FORMAT PARQUET,COMPRESSION ZSTD)')
            for source in bm['sources']:
                with (ROOT/source['path']).open(encoding=source['encoding'],newline='') as f:
                    header=next(csv.reader(f,delimiter=';'))
                years=con.execute("SELECT year_ref,list(DISTINCT TRY_CAST(month_text AS INTEGER) ORDER BY TRY_CAST(month_text AS INTEGER)),count(*) FROM evidence WHERE source_id=? AND metric='tonnes' GROUP BY 1 ORDER BY 1",[source['id']]).fetchall()
                for year,months,count in years:
                    months=[m for m in months if m is not None]
                    coverage.append({'source_id':source['id'],'mode':source['mode'],'year':year,
                        'path':source['path'],'sha256':source['sha256'],'encoding':source['encoding'],
                        'source_records':count,'observed_months':months,
                        'missing_months':[m for m in range(1,13) if m not in months] if source['mode']!='road' else None,
                        'monthly_status':'not_available' if source['mode']=='road' else 'all_12_present' if len(months)==12 else 'incomplete',
                        **source_contract(source,year,header)})
            save_json(stage/'source_coverage.json',coverage)
            manifest={'schema_version':'1.0.0','snapshot_id':snapshot,
                'created_at':datetime.now(timezone.utc).isoformat(),**identity,
                'rows':con.execute('SELECT count(*) FROM monthly').fetchone()[0],
                'source_years':len(coverage),
                'scope':'Monatliche veröffentlichte Schienen-/IWW-OD. VE7 nur Jahresabdeckung; keine erfundenen Monate.',
                'comparison_policy':'Gebiets-/Revisionsvergleichbarkeit nicht automatisch bestätigt; Jahreswerte als veröffentlichte Jahresscheiben.',
                'output_sha256':{p.name:sha256(p) for p in stage.iterdir()}}
            save_json(stage/'manifest.json',manifest)
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(stage,destination)
    print('B02 aufgebaut, noch nicht aktiviert: '+str(destination),flush=True)
    return destination


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--b01',type=Path,default=DEFAULT_STORE)
    p.add_argument('--store',type=Path,default=STORE)
    a=p.parse_args();build(a.b01,a.store)
