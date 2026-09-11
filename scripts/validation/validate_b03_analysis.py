"""B03: Originalbelege, Aggregation und fachliche Abfragegrenzen prüfen."""
import argparse
import csv
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import duckdb
from scripts.analysis.b01 import ROOT, DEFAULT_STORE, resolve_dataset, sha256, save_json, literal
from scripts.analysis.b02 import STORE as B02_STORE, summarize_months
from scripts.analysis.b03 import STORE, query_rail, query_road, road_measure
from scripts.pipelines.build_b03_analysis import checked_dependency


def raw_number(raw, flag):
    """Unabhängige Kontrollauslegung der KBA-Zeichen aus Handbuch, Seite 8."""
    flag = ''.join(flag.split())
    if flag in {'/', '.', 'X', '__', '|'}: return None
    if flag == '-': return 0.0 if not raw.strip() or float(raw.replace(',', '.')) == 0 else None
    if not raw.strip(): return None
    number = float(raw.replace(',', '.'))
    if not math.isfinite(number) or number < 0 or (flag == '0' and number != 0): return None
    return number


def close(a, b):
    return a is None and b is None or a is not None and b is not None and math.isclose(a, b, abs_tol=1e-5, rel_tol=1e-12)


def validate(dataset, activate=False):
    dataset = Path(dataset).resolve()
    m = json.loads((dataset / 'manifest.json').read_text(encoding='utf-8'))
    b01, bm = checked_dependency(DEFAULT_STORE)
    b02, tm = checked_dependency(B02_STORE)
    checks = []
    def check(name, passed, detail=None):
        checks.append({'name': name, 'passed': bool(passed), 'detail': detail})
        print(('OK ' if passed else 'FEHLER ') + name, flush=True)
    for name, path, manifest in [('b01', b01, bm), ('b02', b02, tm)]:
        check('Passender geprüfter Stand ' + name, m[name]['snapshot_id'] == manifest['snapshot_id'] and
              m[name]['manifest_sha256'] == sha256(path / 'manifest.json'))
    check('B01/B02 gemeinsam zugehörig', tm['b01']['snapshot_id'] == bm['snapshot_id'])
    for name, digest in m['output_sha256'].items(): check('B03-Ausgabe ' + name, sha256(dataset / name) == digest)
    for name, digest in m['code_sha256'].items(): check('Buildcode ' + name, sha256(ROOT / name) == digest)
    for name, digest in {**tm['document_sha256'], **m['document_sha256']}.items():
        check('Beschreibung/Register ' + name, sha256(ROOT / name) == digest)
    for source in bm['sources'] + m['sources']:
        check('Rohquelle ' + source['id'], sha256(ROOT / source['path']) == source['sha256'])
    baseline = sha256(ROOT / 'data/processed/fact_od_flows.parquet')
    registry = json.loads((dataset / 'classification.json').read_text(encoding='utf-8'))
    check('T18 alle sieben C-Gruppen und 20 Abteilungen', set(registry['groups']) == set('1234567') and len(registry['divisions']) == 20)
    check('T18 031 und NST14/VP140 richtig zugeordnet', registry['divisions']['03']['group_7_id'] == '1' and
          registry['divisions']['14']['group_7_id'] == '6' and registry['vp_to_group']['140'] == '6')
    with duckdb.connect() as c:
        c.execute("SET memory_limit='1GB'"); c.execute('SET threads=1')
        c.execute('CREATE VIEW fine AS SELECT * FROM read_parquet(' + literal(dataset / 'rail_monthly_details.parquet') + ')')
        c.execute('CREATE VIEW road AS SELECT * FROM read_parquet(' + literal(dataset / 'road_details.parquet') + ')')
        c.execute('CREATE VIEW monthly AS SELECT * FROM read_parquet(' + literal(b02 / 'monthly_od.parquet') + ')')
        check('Zeilenzahlen stimmen', c.execute('SELECT count(*) FROM fine').fetchone()[0] == m['row_counts']['rail_monthly_details'] and
              c.execute('SELECT count(*) FROM road').fetchone()[0] == m['row_counts']['road_details'])
        check('Eindeutige Straßenklassenzellen', c.execute('''SELECT count(*) FROM (SELECT product,year_ref,region_id,direction,class_id,population,metric
              FROM road GROUP BY ALL HAVING count(*)<>1)''').fetchone()[0] == 0)
        check('Originalcodes als Text, keine unbekannte Zuordnung', c.execute("SELECT count(*) FROM fine WHERE length(nst_raw)<>3 OR group_7_id IS NULL OR month NOT BETWEEN 1 AND 12").fetchone()[0] == 0)
        # Every fine cell must reconstruct the already validated B02 cell, including all counters.
        keys = 'year_ref,origin_id,dest_id,group_7_id,metric,source_id,legacy_scope,month'
        counters = ['source_rows', 'missing_count', 'restricted_count', 'unknown_quality_count']
        c.execute('CREATE TEMP TABLE regrouped AS SELECT ' + keys + ',sum(known_sum) AS known_sum,' +
                  ','.join('sum('+k+') AS '+k for k in counters) + ' FROM fine GROUP BY ALL')
        mismatch = c.execute('''SELECT count(*) FROM regrouped a FULL OUTER JOIN
            (SELECT * FROM monthly WHERE mode='rail') b USING (''' + keys + ''') WHERE
            a.source_id IS NULL OR b.source_id IS NULL OR
            (a.known_sum IS NULL)<>(b.known_sum IS NULL) OR
            abs(a.known_sum-b.known_sum)>greatest(0.00001,abs(b.known_sum)*1e-12) OR ''' +
            ' OR '.join('a.'+k+' IS DISTINCT FROM b.'+k for k in counters)).fetchone()[0]
        check('Sämtliche Feinpositionen ergeben B02-Mengen und Qualitätszähler', mismatch == 0, mismatch)
        # Independent CSV totals for each SGV year, exact direction, raw NST, month and metric.
        for source in [s for s in bm['sources'] if s['mode'] == 'rail']:
            c.execute('CREATE OR REPLACE VIEW raw AS SELECT * FROM read_csv(' + literal(ROOT / source['path']) +
                      ",delim=';',header=true,all_varchar=true,encoding='latin-1')")
            for field, metric in [('Befoerderungsmenge_in_Tonnen','tonnes'), ('Befoerderungsleistung_in_TKM','tkm'), ('Anzahl_Ladeeinheiten','load_units')]:
                raw = c.execute('''SELECT CAST(Referenzzeitraum_Jahr AS INTEGER),CAST(Referenzzeitraum_Monat AS INTEGER),
                    Versandregion_NUTS2024,Empfangsregion_NUTS2024,Guetergruppe_NST2007,count(*),
                    sum(TRY_CAST(REPLACE("''' + field + '''",',','.') AS DOUBLE)) FROM raw GROUP BY 1,2,3,4,5 ORDER BY 1,2,3,4,5''').fetchall()
                saved = c.execute('''SELECT year_ref,month,origin_id,dest_id,nst_raw,sum(source_rows),sum(known_sum)
                    FROM fine WHERE source_id=? AND metric=? GROUP BY 1,2,3,4,5 ORDER BY 1,2,3,4,5''', [source['id'], metric]).fetchall()
                check('SGV-Original Monat/Richtung/NST ' + source['id'] + ' ' + metric,
                      len(raw) == len(saved) and all(a[:6] == b[:6] and close(a[6], b[6]) for a,b in zip(raw,saved)))
        # Verify every saved road measure against its original CSV field and flag.
        for source in m['sources']:
            with (ROOT / source['path']).open(encoding=source['encoding'], newline='') as handle:
                rows = list(csv.DictReader(handle, delimiter=';'))
            saved = c.execute('''SELECT source_record,year_ref,region_id,satzart1,satzart2,class_raw,class_id,
                source_field,raw_value,raw_flag,value,quality_status,product,direction,population,metric,unit,region_level,group_7_id
                FROM road WHERE source_id=?''', [source['id']]).fetchall()
            good = len(saved) == len(rows)*6 and len(rows) == source['records']
            for record in saved:
                idx, year, region, s1, s2, raw_class, cls, field, raw, flag, value, quality, product, direction, population, metric, unit, level, group = record
                row = rows[idx-1]
                code = row['FT_ENTF3'] if source['product'] == 'VD2' else row['GUART']
                expected_class = code if source['product'] == 'VD2' else code.zfill(2)
                expected_field = {'tonnes':'TON','tkm':'TKM','trips':'FT'}[metric] + '_' + population
                expected_group = None if product == 'VD2' else registry['divisions'][expected_class]['group_7_id']
                good = good and (year,region,s1,s2,raw_class,cls,raw,flag,product,direction,field,unit,level,group) == (
                    int(row['JAHR']),row[source['region_field']],row['SATZART1'],row['SATZART2'],code,expected_class,row[field],row[field+'_ZS'],
                    source['product'],source['direction'],expected_field,{'tonnes':'t','tkm':'tkm','trips':'Fahrten'}[metric],source['region_level'],expected_group)
                good = good and close(value,raw_number(row[field],row[field+'_ZS']))
                if ''.join(flag.split()) == '()': good = good and quality == 'restricted'
            check('Alle KBA-Felder, Richtungen, I/G und Originalzeichen ' + source['id'], good)
        q = lambda **kw: query_rail(c,dataset,region='DEA23',partner='DE600',**kw)
        r24, r23 = q(year=2024), q(year=2023)
        check('T19/T21 Köln → Hamburg 2023/2024', r24['published_sum'] == 199851 and r23['published_sum'] == 227456)
        check('T19 C1 und C7, fehlende C2 ohne Nullnachweis', q(year=2024,group='1')['published_sum'] == 231 and
              q(year=2024,group='7')['published_sum'] == 199620 and q(year=2024,group='2')['status'] == 'missing_row')
        reverse = q(year=2024,direction='inbound')
        direct = c.execute("SELECT sum(known_sum) FROM fine WHERE year_ref=2024 AND origin_id='DE600' AND dest_id='DEA23' AND metric='tonnes'").fetchone()[0]
        check('T21 Empfang ist Gegenrichtung', close(reverse['published_sum'], direct) and direct != r24['published_sum'])
        check('T21 keine ungeprüfte Änderungsrate', r23['change_pct'] is None and r24['comparability'] == 'not_confirmed')
        nst = r24['details'][0]['nst_raw']
        selected = q(year=2024,nst=nst)
        check('Feincode gezielt abgefragt', len(selected['details']) == 1 and selected['details'][0]['nst_raw'] == nst)
        total = query_rail(c,dataset,year=2024,region='DEE03',direction='total')
        exact = c.execute("SELECT sum(known_sum) FROM fine WHERE year_ref=2024 AND (origin_id='DEE03' OR dest_id='DEE03') AND metric='tonnes'").fetchone()[0]
        check('Binnenverkehr bei total einmal', close(total['published_sum'], exact))
        gap = query_rail(c,dataset,year=2016,region='DEE06',partner='DEA23',group='4')
        check('Reale Monatslücke bleibt unbekannt', {1,5} <= set(gap['missing_months']) and gap['annual_value'] is None and gap['peak_month_share_pct'] is None)
        check('Gebiets-/Revisionsgrenzen übernommen', any(s['territory_status'] == 'header_documentation_conflict' for s in r23['sources']))
        distance = query_road(c,dataset,product='VD2',year=2024,region='DE254',metric='trips')
        check('T40 Nürnberg 698880,8 / 400300,5 / 476759,4 Fahrten', [r['value'] for r in distance['rows']] == [698880.8,400300.5,476759.4])
        for direction in ['outbound','inbound']:
            for population in ['I','G']:
                for metric in ['tonnes','tkm','trips']:
                    detail = query_road(c,dataset,product='VD3c',year=2024,region='DEA2',direction=direction,population=population,metric=metric)
                    check('T41 DEA2 20 Originalpositionen '+direction+' '+population+' '+metric,
                          len(detail['rows']) == 20 and not detail['missing_classes'] and detail['status']=='partial' and detail['value'] is None and
                          any(r['raw_flag']=='/' and r['value'] is None for r in detail['rows']))
        check('T17 NUTS3 nicht als NUTS2 umgedeutet', query_road(c,dataset,product='VD3c',year=2024,region='DEA23')['status']=='unsupported_region_level')
        check('T20 keine Straßen-OD erzeugt', query_road(c,dataset,product='VD3c',year=2024,region='DEA2',partner='DE60')['status']=='unsupported_relation')
        check('Nicht vorhandenes Jahr bleibt not_available', query_road(c,dataset,product='VD2',year=1900,region='DE254')['status']=='not_available')
        check('Fehlende Region bleibt missing_row', query_road(c,dataset,product='VD2',year=2024,region='DE999')['status']=='missing_row')
        for name, kwargs in [('SQL-artiger Feincode',{'nst':"031' OR 1=1"}), ('Numerischer Feincode',{'nst':31}), ('Unbekannte Kennzahl',{'metric':'profit'})]:
            try: q(year=2024,**kwargs)
            except ValueError: passed=True
            else: passed=False
            check('Eingabeprüfung '+name,passed)
        from scripts.validation.check_b0103_regressions import b03_checks
        b03_checks(c,dataset,check)
    cases = [('0','',(0.0,'reported_zero','unflagged')),('0','0',(0.0,'rounded_zero','unflagged')),
             ('','-',(0.0,'confirmed_zero','unflagged')),('','/',(None,'suppressed','unknown')),
             ('','.',(None,'suppressed','unknown')),('12,5','()',(12.5,'observed','restricted')),
             ('','',(None,'missing_value','unflagged')),('2','0',(None,'conflicting_source','unknown')),
             ('12','X',(None,'not_comparable','unknown')),('nan','',(None,'invalid_numeric','unflagged'))]
    for raw,flag,expected in cases: check('T42 Zeichenfall '+repr((raw,flag)),road_measure(raw,flag)==expected)
    months = [{'month':i,'value':200 if i==12 else 100,'known_sum':200 if i==12 else 100,'missing_count':0} for i in range(1,13)]
    synthetic = summarize_months(months)
    check('T39 synthetischer Spitzenanteil',synthetic['annual_value']==1300 and close(synthetic['peak_month_share_pct'],200/1300*100))
    check('T39 fehlender Monat verhindert Jahresbewertung',summarize_months(months[:-1])['annual_value'] is None)
    check('Bestehender Dashboard-OD unverändert',baseline==sha256(ROOT / 'data/processed/fact_od_flows.parquet'))
    report = {'snapshot_id':m['snapshot_id'],'passed':all(x['passed'] for x in checks),'checks':checks,
              'manifest_sha256':sha256(dataset/'manifest.json'),
              'checked_at':datetime.now(timezone.utc).isoformat(),'validator_sha256':sha256(Path(__file__)),
              'scope':'Lokale B03-Daten und Abfragegrenzen; kein Modelltest, keine Server-/Dashboardfreigabe.'}
    save_json(dataset / 'validation.json', report)
    if report['passed'] and activate:
        if dataset.parent.name != 'releases' or dataset.name != m['snapshot_id']:
            raise ValueError('Nur unveränderten Releasepfad aktivieren')
        pointer = dataset.parent.parent / 'current.json'
        temporary = pointer.with_suffix('.new.json')
        save_json(temporary,{'snapshot_id':m['snapshot_id'],'validation_sha256':sha256(dataset/'validation.json'),
                             'manifest_sha256':sha256(dataset/'manifest.json')})
        os.replace(temporary,pointer)
    print(f"B03: {sum(x['passed'] for x in checks)}/{len(checks)} Prüfungen bestanden",flush=True)
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,required=True)
    parser.add_argument('--activate',action='store_true')
    args = parser.parse_args()
    raise SystemExit(0 if validate(args.dataset,args.activate) else 1)
