"""B02-Datenprüfung ohne Modellaufruf; aktiviert nur einen bestandenen Stand."""
import argparse
import json
import math
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import duckdb
from scripts.analysis.b01 import ROOT,DEFAULT_STORE,literal,resolve_dataset,sha256,save_json
from scripts.analysis.b02 import query_series,summarize_months,change


def validate(dataset,activate=False,b01_store=DEFAULT_STORE):
    dataset=Path(dataset).resolve();b01=resolve_dataset(b01_store)
    m=json.loads((dataset/'manifest.json').read_text(encoding='utf-8'))
    bm=json.loads((b01/'manifest.json').read_text(encoding='utf-8'))
    checks=[]
    def check(name,passed,detail=None):
        checks.append({'name':name,'passed':bool(passed),'detail':detail})
        print(('OK ' if passed else 'FEHLER ')+name,flush=True)
    check('Passender aktiver B01-Stand',bm['snapshot_id']==m['b01']['snapshot_id'])
    check('B01-Manifest unverändert',sha256(b01/'manifest.json')==m['b01']['manifest_sha256'])
    for name,digest in m['b01']['output_sha256'].items():check('B01 '+name,sha256(b01/name)==digest)
    for name,digest in m['output_sha256'].items():check('B02 '+name,sha256(dataset/name)==digest)
    for name,digest in m['code_sha256'].items():check('Buildcode '+name,sha256(ROOT/name)==digest)
    for name,digest in m['document_sha256'].items():check('Quellbeschreibung '+name,sha256(ROOT/name)==digest)
    for source in bm['sources']:check('Rohquelle '+source['id'],sha256(ROOT/source['path'])==source['sha256'])
    coverage=json.loads((dataset/'source_coverage.json').read_text(encoding='utf-8'))
    before=sha256(ROOT/'data/processed/fact_od_flows.parquet')
    with duckdb.connect() as c:
        c.execute('CREATE VIEW monthly AS SELECT * FROM read_parquet('+literal(dataset/'monthly_od.parquet')+')')
        c.execute('CREATE VIEW annual AS SELECT * FROM read_parquet('+literal(b01/'annual_od.parquet')+')')
        keys=['year_ref','origin_id','dest_id','mode','group_7_id','metric','source_id','legacy_scope']
        keytext=','.join(keys)
        check('Monatsschlüssel eindeutig',c.execute('SELECT count(*) FROM (SELECT '+keytext+',month,count(*) n FROM monthly GROUP BY ALL HAVING n>1)').fetchone()[0]==0)
        check('Monate gültig, keine Straßenmonate erfunden',c.execute("SELECT count(*) FROM monthly WHERE month NOT BETWEEN 1 AND 12 OR month IS NULL OR mode NOT IN ('rail','iww')").fetchone()[0]==0)
        check('Zeilenzahl entspricht Manifest',c.execute('SELECT count(*) FROM monthly').fetchone()[0]==m['rows'])
        joined=' AND '.join('a.'+k+' IS NOT DISTINCT FROM b.'+k for k in keys)
        sql='''WITH a AS (SELECT * FROM annual WHERE mode IN ('rail','iww')),
            b AS (SELECT '''+keytext+''',sum(source_rows) source_rows,sum(known_sum) known_sum,
              sum(missing_count) missing_count,sum(restricted_count) restricted_count,
              sum(unknown_quality_count) unknown_quality_count FROM monthly GROUP BY ALL)
            SELECT count(*) FROM a FULL JOIN b ON '''+joined+'''
            WHERE a.source_rows IS DISTINCT FROM b.source_rows
              OR a.missing_count IS DISTINCT FROM b.missing_count
              OR a.restricted_count IS DISTINCT FROM b.restricted_count
              OR a.unknown_quality_count IS DISTINCT FROM b.unknown_quality_count
              OR (a.known_sum IS NULL)<>(b.known_sum IS NULL)
              OR abs(a.known_sum-b.known_sum)>greatest(0.00001,abs(a.known_sum)*1e-12)'''
        diff=c.execute(sql).fetchone()[0]
        check('Alle Monatssummen und Qualitätszähler stimmen mit B01-Jahreswerten überein',diff==0,diff)
        check('Unbekannte Komponenten sperren Monatsgesamtwert',c.execute('SELECT count(*) FROM monthly WHERE missing_count>0 AND value IS NOT NULL').fetchone()[0]==0)
        # Independently re-read each original CSV, without using the B01 parser.
        for source in bm['sources']:
            c.execute('CREATE OR REPLACE VIEW raw AS SELECT * FROM read_csv('+literal(ROOT/source['path'])+",delim=';',header=true,all_varchar=true,encoding="+literal(source['encoding'])+')')
            mode=source['mode']
            if mode=='road':
                actual=c.execute('SELECT CAST(Jahr AS INTEGER),count(*) FROM raw GROUP BY 1 ORDER BY 1').fetchall()
                saved=sorted((r['year'],r['source_records']) for r in coverage if r['source_id']==source['id'])
                check('VE7-Jahresabdeckung unabhängig aus CSV',actual==saved)
                continue
            value='Befoerderungsmenge_in_Tonnen' if mode=='rail' else 'Tonnen'
            raw=c.execute('SELECT CAST(Referenzzeitraum_Jahr AS INTEGER),CAST(Referenzzeitraum_Monat AS INTEGER),count(*),sum(CAST(REPLACE("'+value+'",\',\',\'.\') AS DOUBLE)) FROM raw GROUP BY 1,2 ORDER BY 1,2').fetchall()
            saved=c.execute("SELECT year_ref,month,sum(source_rows),sum(known_sum) FROM monthly WHERE source_id=? AND metric='tonnes' GROUP BY 1,2 ORDER BY 1,2",[source['id']]).fetchall()
            same=len(raw)==len(saved) and all(a[:3]==b[:3] and ((a[3] is None and b[3] is None) or (a[3] is not None and b[3] is not None and math.isclose(a[3],b[3],rel_tol=1e-12,abs_tol=1e-5))) for a,b in zip(raw,saved))
            check('Monate und Tonnen unabhängig aus CSV '+source['id'],same)
            for item in [r for r in coverage if r['source_id']==source['id']]:
                check('Quellenabdeckung '+source['id'],item['observed_months']==[r[1] for r in raw if r[0]==item['year']] and item['source_records']==sum(r[2] for r in raw if r[0]==item['year']))
            extra=[('Befoerderungsleistung_in_TKM','tkm'),('Anzahl_Ladeeinheiten','load_units')] if mode=='rail' else [('Tonnen_km','tkm'),('Anzahl_Ladungstraeger','load_carriers')]
            for field,metric in extra:
                original=c.execute('SELECT CAST(Referenzzeitraum_Jahr AS INTEGER),CAST(Referenzzeitraum_Monat AS INTEGER),count(*),sum(CAST(REPLACE("'+field+'",\',\',\'.\') AS DOUBLE)) FROM raw GROUP BY 1,2 ORDER BY 1,2').fetchall()
                stored=c.execute('SELECT year_ref,month,sum(source_rows),sum(known_sum) FROM monthly WHERE source_id=? AND metric=? GROUP BY 1,2 ORDER BY 1,2',[source['id'],metric]).fetchall()
                match=len(original)==len(stored) and all(a[:3]==b[:3] and ((a[3] is None and b[3] is None) or (a[3] is not None and b[3] is not None and math.isclose(a[3],b[3],rel_tol=1e-12,abs_tol=1e-5))) for a,b in zip(original,stored))
                check('Unabhängige CSV-Monate '+source['id']+' '+metric,match)
        series=query_series(c,dataset,region='DEE03',mode='rail',start=2016,end=2025)
        expected=[61204,82328,76144,1485941,1389350,1395002,1567349,1975339,1873054,448780]
        check('T10 zehn Magdeburger Versandjahre erhalten',[y['annual_value'] for y in series['years']]==expected)
        check('T10 zwölf belegte Monate in jedem Jahr',all(len(y['observed_months'])==12 for y in series['years']))
        check('Keine unbelegte Vergleichsrate trotz Mengenreihe',series['comparison']['status']=='comparability_not_confirmed')
        total=query_series(c,dataset,region='DEE03',mode='rail',direction='total',start=2024,end=2024)
        direct=c.execute("SELECT sum(known_sum) FROM annual WHERE mode='rail' AND metric='tonnes' AND year_ref=2024 AND (origin_id='DEE03' OR dest_id='DEE03')").fetchone()[0]
        check('Regionalgesamt zählt Binnenrelation einmal',total['years'][0]['annual_value']==direct,direct)
        missing=query_series(c,dataset,region='UNKNOWN',mode='rail',start=2024,end=2024)
        check('Unbelegte Region erhält zwölf Fehlmonate statt Nullen',missing['years'][0]['annual_value'] is None and len(missing['years'][0]['missing_months'])==12)
        road=query_series(c,dataset,region='DEE03',mode='road')
        check('VE7 wird nicht auf Monate verteilt',road['status']=='monthly_not_available')
        noyear=query_series(c,dataset,region='DEE03',mode='rail',start=2015,end=2015)
        check('Fehlender Jahrgang ist separat gekennzeichnet',noyear['years'][0]['status']=='year_not_available')
        thin=c.execute("SELECT origin_id,dest_id,mode,year_ref,group_7_id FROM monthly WHERE metric='tonnes' AND origin_id IS NOT NULL AND dest_id IS NOT NULL GROUP BY ALL HAVING count(DISTINCT month)<12 LIMIT 1").fetchone()
        if thin:
            origin,dest,mode,year,group=thin
            result=query_series(c,dataset,region=origin,partner=dest,mode=mode,start=year,end=year,group=group)['years'][0]
            check('Reale lückenhafte Einzelrelation sperrt Jahresanteil',result['annual_value'] is None and result['peak_month_share_pct'] is None,{'origin':origin,'destination':dest,'mode':mode,'year':year,'group':group,'missing_months':result['missing_months']})
        else:check('Realer Fall mit fehlenden Monatszeilen vorhanden',False)
        cases=[{'month':i,'known_sum':200 if i==12 else 100,'value':200 if i==12 else 100,'missing_count':0} for i in range(1,13)]
        result=summarize_months(cases)
        check('T39 Jahressumme 1300 und Spitzenanteil 15,38 Prozent',result['annual_value']==1300 and math.isclose(result['peak_month_share_pct'],200/1300*100))
        check('T39 elf Monate sind kein vollständiges Jahr',summarize_months(cases[:-1])['annual_value'] is None)
        unknown=[dict(r) for r in cases];unknown[0].update(value=None,missing_count=1)
        check('T39 Teilmonat sperrt Jahreswert',summarize_months(unknown)['annual_value'] is None)
        zeros=[dict(r,value=0,known_sum=0) for r in cases]
        check('Zwölf veröffentlichte Nullmonate: Summe 0, kein Anteil',summarize_months(zeros)['annual_value']==0 and summarize_months(zeros)['peak_month_share_pct'] is None)
        check('T11 Nullbasis erlaubt keine Prozentänderung',change(0,10,comparable=True)=={'absolute_change':10,'relative_change_pct':None,'status':'zero_base'})
        check('T11 Rückgang auf Null ergibt minus 100 Prozent',change(10,0,comparable=True)['relative_change_pct']==-100)
        check('T11 fehlende Basis erlaubt keine Rate',change(None,10,comparable=True)['relative_change_pct'] is None)
        check('T14 kleine Basis wird nicht still ausgeschlossen',change(1,10,comparable=True)['relative_change_pct']==900)
        conflict=[r for r in coverage if r['mode']=='rail' and r['year']<2024]
        check('Historischer NUTS-Konflikt ist sichtbar',all(r['territory_status']=='header_documentation_conflict' for r in conflict) and len(conflict)==8)
        check('Revisionsstand wird nicht erfunden',all(r['revision_status']=='not_documented' for r in coverage))
        from scripts.validation.check_b0103_regressions import b02_checks
        b02_checks(c,dataset,check)
    check('Bestehender Dashboard-OD unverändert',sha256(ROOT/'data/processed/fact_od_flows.parquet')==before)
    passed=all(r['passed'] for r in checks)
    report={'snapshot_id':m['snapshot_id'],'passed':passed,'checks':checks,
        'manifest_sha256':sha256(dataset/'manifest.json'),
        'validation_code_sha256':sha256(Path(__file__)),
        'limits':'Lokale Aufbereitung geprüft; keine harmonisierte Zeitreihe, keine bestätigte Revision, kein KI-Test.'}
    save_json(dataset/'validation.json',report)
    if not passed:raise AssertionError('B02-Prüfung fehlgeschlagen; keine Aktivierung')
    if activate:
        if dataset.parent.name!='releases' or dataset.name!=m['snapshot_id']:raise ValueError('Datenstand muss unter passendem Releasepfad liegen')
        pending=dataset.parent.parent/'current.pending.json'
        save_json(pending,{'snapshot_id':m['snapshot_id'],'b01_snapshot_id':bm['snapshot_id'],'validation':'passed',
                          'manifest_sha256':sha256(dataset/'manifest.json'),'validation_sha256':sha256(dataset/'validation.json')})
        os.replace(pending,dataset.parent.parent/'current.json')
    print(f'{len(checks)} Prüfungen bestanden',flush=True)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset',type=Path,required=True)
    p.add_argument('--b01',type=Path,default=DEFAULT_STORE)
    p.add_argument('--activate',action='store_true')
    a=p.parse_args();validate(a.dataset,a.activate,a.b01)
