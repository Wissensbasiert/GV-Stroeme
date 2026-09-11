"""B01: reale Quellen-/Mengenprüfung und synthetische Fehlwertgrenzen.

--activate setzt erst nach vollständig bestandener Prüfung den lokalen current-Verweis.
"""
import argparse
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import duckdb
from scripts.analysis.b01 import ROOT, literal, parse_measure, query_relation, save_json, sha256
from scripts.pipelines.build_b01_analysis import LONG_SQL, ANNUAL_SQL


def validate(dataset, activate=False, root=ROOT):
    dataset, root = Path(dataset).resolve(), Path(root)
    manifest = json.loads((dataset / 'manifest.json').read_text(encoding='utf-8'))
    checks = []

    def check(name, condition, detail=None):
        checks.append({'name': name, 'passed': bool(condition), 'detail': detail})
        print(('OK ' if condition else 'FEHLER ') + name, flush=True)

    for name, digest in manifest['output_sha256'].items():
        check('Ausgabedatei ' + name, sha256(dataset / name) == digest)
    for source in manifest['sources']:
        check('Rohquelle ' + source['id'], sha256(root / source['path']) == source['sha256'])
    for name, digest in manifest['code_sha256'].items():
        check('Buildcode ' + name, sha256(ROOT / name) == digest)
    with duckdb.connect() as con:
        con.execute('SET threads=1')
        con.execute('SET preserve_insertion_order=true')
        con.execute('CREATE VIEW facts AS SELECT * FROM read_parquet(' + literal(dataset / 'annual_od.parquet') + ')')
        con.execute('CREATE VIEW evidence AS SELECT * FROM read_parquet(' + literal(dataset / 'source_values.parquet') + ')')
        count = con.execute('SELECT count(*) FROM evidence').fetchone()[0]
        check('Jede Rohzeile mit drei getrennten Kennzahlen erhalten',
              count == 3 * sum(s['records'] for s in manifest['sources']))
        actual_sources = dict(con.execute('SELECT source_id,count(DISTINCT source_record) FROM evidence GROUP BY 1').fetchall())
        check('Zeilenzahl je Quelle erhalten', all(actual_sources[s['id']] == s['records'] for s in manifest['sources']))
        check('Kennzahlen nicht als gemeinsame Fahrtenzahl vermischt', con.execute("""
            SELECT count(*) FROM evidence WHERE
            (mode='road' AND metric NOT IN ('tonnes','tkm','trips')) OR
            (mode='rail' AND metric NOT IN ('tonnes','tkm','load_units')) OR
            (mode='iww' AND metric NOT IN ('tonnes','tkm','load_carriers'))""").fetchone()[0] == 0)
        check('Unbekannte numerische Werte nicht durch Null ersetzt', con.execute("""
            SELECT count(*) FROM evidence WHERE value_status IN
            ('missing_value','suppressed','invalid_numeric','conflicting_source') AND value IS NOT NULL""").fetchone()[0] == 0)
        invalid = con.execute("SELECT value_status,count(*) FROM evidence WHERE value_status IN ('invalid_numeric','conflicting_source') GROUP BY 1").fetchall()
        check('Keine ungeklärten Parse-/Quellkonflikte', not invalid, invalid)
        check('Teilsumme nicht als vollständiger Wert ausgegeben',
              con.execute('SELECT count(*) FROM facts WHERE missing_count>0 AND value IS NOT NULL').fetchone()[0] == 0)
        # Comparison covers every legacy-scoped key, not just the visible Top list.
        old = root / 'data/processed/fact_od_flows.parquet'
        before = sha256(old)
        con.execute('CREATE VIEW old_fact AS SELECT * FROM read_parquet(' + literal(old) + ')')
        differences = con.execute('''WITH old_long AS (
            SELECT year_ref,origin_nuts AS origin_id,dest_nuts AS dest_id,mode_transport AS mode,
                   group_7_id,'tonnes' AS metric,tonnes AS value FROM old_fact
            UNION ALL SELECT year_ref,origin_nuts,dest_nuts,mode_transport,group_7_id,'tkm',tkm FROM old_fact
          ), a AS (SELECT year_ref,origin_id,dest_id,mode,group_7_id,metric,
                          sum(value) AS v,count(*) AS n FROM old_long GROUP BY ALL),
          b AS (SELECT year_ref,origin_id,dest_id,mode,group_7_id,metric,
                          sum(known_sum) AS v,count(*) AS n FROM facts
                 WHERE legacy_scope AND metric IN ('tonnes','tkm') GROUP BY ALL)
          SELECT count(*) FROM a FULL OUTER JOIN b
          USING(year_ref,origin_id,dest_id,mode,group_7_id,metric)
          WHERE a.n IS NULL OR b.n IS NULL OR (a.v IS NULL)<>(b.v IS NULL)
             OR abs(a.v-b.v)>greatest(0.00001,abs(a.v)*1e-12)''').fetchone()[0]
        check('Alle vergleichbaren OD-Mengen und tkm stimmen mit bisherigem Bestand überein', differences == 0, differences)
        for name, origin, dest, mode, expected in [
            ('T19 Köln–Hamburg Schiene', 'DEA23','DE600','rail',199851),
            ('T20 Köln–Hamburg Straße', 'DEA23','DE600','road',67757),
            ('T05 Duisburg–Magdeburg IWW', 'DEA12','DEE03','iww',1947),
            ('T05 Magdeburg–Duisburg IWW', 'DEE03','DEA12','iww',1189)]:
            result = query_relation(con,dataset,year=2024,origin=origin,destination=dest,mode=mode)
            check(name, result['status']=='available' and abs(result['value']-expected)<1e-6, result['value'])
        result = query_relation(con,dataset,year=2024,origin='DEA23',destination='DE600',mode='road')
        check('T20 Qualität der Straßenmenge eingeschränkt', result['quality']=='restricted')
        result = query_relation(con,dataset,year=2024,origin='DEA23',destination='DE600',mode='rail',group='2')
        check('T19 nicht vorhandene C-Gruppe ist missing_row, nicht 0',result['status']=='missing_row' and result['value'] is None)
        result = query_relation(con,dataset,year=2024,origin='DEA23',destination='DE600',mode='road',group='1')
        check('Keine Güterstruktur auf Straßen-OD erfunden',result['status']=='not_available')
        result = query_relation(con,dataset,year=2025,origin='DEA23',destination='DE600',mode='road')
        check('Straße 2025 nicht als fehlende Einzelrelation verkannt',result['status']=='not_available')
        result = query_relation(con,dataset,year=2024,origin='UNKNOWN',destination='DE600',mode='road')
        check('Unbelegte Kennung erzeugt keine Nullzahl',result['value'] is None)
        # Independent CSV read for flag totals and Hamburg ranking.
        road = root / 'data/raw/Straße/KBA/VE7_Verflechtung_NUTS3/ve7_2010_2024.csv'
        con.execute('CREATE VIEW ve7 AS SELECT * FROM read_csv(' + literal(road)
                    + ",delim=';',all_varchar=true)")
        raw_flag_count = con.execute("SELECT count(*) FROM ve7 WHERE replace(coalesce(ZS_Tonnen,''),' ','')='()'").fetchone()[0]
        saved_flag_count = con.execute("SELECT count(*) FROM evidence WHERE mode='road' AND metric='tonnes' AND quality_status='restricted'").fetchone()[0]
        check('Alle eingeschränkten VE7-Tonnenzeilen erhalten', raw_flag_count==saved_flag_count, saved_flag_count)
        top = con.execute("""SELECT CASE WHEN origin_id='DE600' THEN dest_id ELSE origin_id END AS partner,
              sum(value) AS tonnes FROM facts WHERE mode='road' AND metric='tonnes' AND year_ref=2024
              AND (origin_id='DE600' OR dest_id='DE600') AND origin_id<>dest_id
              GROUP BY partner ORDER BY tonnes DESC,partner LIMIT 5""").fetchall()
        check('T04 Hamburger Top 5 aus vollständigem Bestand',top==[
            ('DE933',5126813.0),('DEF0D',4628663.0),('DEF0F',3374382.0),
            ('DEF06',2687481.0),('DE929',2289981.0)],top)
        totals=con.execute("""SELECT sum(value),sum(value) FILTER (WHERE quality_status='restricted')
              FROM evidence WHERE mode='road' AND metric='tonnes' AND year_ref=2024
              AND (origin_id='DE600' OR dest_id='DE600') AND origin_id<>dest_id""").fetchone()
        check('T04 vollständiger Nenner samt markierter Teilmenge', totals==(55473138.0,21167732.0), totals)
        # Test the actual SQL parser, including states absent in today's sample.
        cases=[('12,5','',False,(12.5,'observed','unflagged')),
               ('100','( )',True,(100.0,'observed','restricted')),
               ('','/',True,(None,'suppressed','unknown')),
               ('','',True,(None,'missing_value','unflagged')),
               ('','-',True,(0.0,'confirmed_zero','unflagged')),
               ('0','',True,(0.0,'reported_zero','unflagged')),
               ('0','0',True,(0.0,'rounded_zero','unflagged')),
               ('9','-',True,(None,'conflicting_source','unknown')),
               ('bad','',True,(None,'invalid_numeric','unflagged'))]
        for i,(raw,flag,kba,expected) in enumerate(cases):
            mode='road' if kba else 'rail'
            con.execute(f'''CREATE OR REPLACE TABLE normalized AS SELECT 'test' AS source_id,
                1 AS source_record,{literal(mode)} AS mode,'trips' AS count_metric,2024 AS year_ref,
                '01' AS month_text,'00123' AS origin_nuts,'DE600' AS dest_nuts,
                NULL AS origin_country,NULL AS dest_country,'00123' AS origin_id,'DE600' AS dest_id,
                true AS legacy_scope,'031' AS nst_raw,'1' AS group_7_id,'1' AS traffic_relationship,
                NULLIF({literal(raw)},'') AS raw_tonnes,NULL AS raw_tkm,NULL AS raw_count,
                {literal(flag)} AS flag_tonnes,NULL AS flag_tkm,NULL AS flag_count''')
            result=con.execute('SELECT value,value_status,quality_status FROM ('+LONG_SQL+") WHERE metric='tonnes'").fetchone()
            check(f'Synthetischer Quellenzustand {i+1}',result==expected, result)
            check(f'Python-Referenzsemantik {i+1}',parse_measure(raw,flag,kba)==expected)
        con.execute("UPDATE normalized SET raw_tonnes='100',flag_tonnes='( )'")
        con.execute('CREATE TABLE synthetic_values AS '+LONG_SQL)
        con.execute("UPDATE normalized SET source_record=2,raw_tonnes=NULL,flag_tonnes='/'")
        con.execute('INSERT INTO synthetic_values '+LONG_SQL)
        aggregate = ANNUAL_SQL.replace('FROM read_parquet(?)','FROM synthetic_values')
        mixed = con.execute("SELECT known_sum,value,missing_count,restricted_count,status FROM ("+aggregate+") WHERE metric='tonnes'").fetchone()
        check('Gemischte Summe: 100 plus unbekannt bleibt unvollständig', mixed==(100.0,None,1,1,'partial'),mixed)
        check('Führende Nullen bleiben in Ortskennungen erhalten',con.execute("SELECT min(origin_id) FROM synthetic_values").fetchone()[0]=='00123')
        check('Alphanumerische NST-Schlüssel bleiben erhalten',con.execute("SELECT count(*) FROM evidence WHERE nst_raw='01A'").fetchone()[0]>0)
        check('Bestehende Dashboard-OD unverändert', sha256(old)==before)
        from scripts.validation.check_b0103_regressions import raw_b01,b01_checks
        raw_b01(con,dataset,manifest,check)
        b01_checks(con,dataset,check)
    passed = all(c['passed'] for c in checks)
    report={'snapshot_id':manifest['snapshot_id'],'passed':passed,'checks':checks,
            'manifest_sha256':sha256(dataset/'manifest.json'),'validation_code_sha256':sha256(Path(__file__)),
            'limits':'Lokale B01-Datenprüfung, keine Portal-/Modellfreigabe; fehlende Zeilen und reale Vollständigkeit bleiben getrennt.'}
    save_json(dataset/'validation.json',report)
    if not passed:
        raise AssertionError('B01-Prüfung fehlgeschlagen; current nicht aktiviert')
    if activate:
        if dataset.parent.name!='releases' or dataset.name!=manifest['snapshot_id']:
            raise ValueError('--activate benötigt einen Datenstand unter releases')
        pointer=dataset.parent.parent/'current.json'
        pending=pointer.with_suffix('.pending.json')
        save_json(pending,{'snapshot_id':manifest['snapshot_id'],'validation':'passed',
                          'manifest_sha256':sha256(dataset/'manifest.json'),'validation_sha256':sha256(dataset/'validation.json')})
        os.replace(pending,pointer)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,required=True)
    parser.add_argument('--activate',action='store_true')
    args=parser.parse_args()
    validate(args.dataset,args.activate)
