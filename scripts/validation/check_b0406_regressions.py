"""Regressionen aus der Zweitprüfung: reale Abfragen und gezielte Fehlerfälle."""
import copy
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
from scripts.analysis import b0406 as b
from scripts.analysis.b01 import ROOT,save_json,sha256


def run_checks(con,dataset,check):
    dataset=Path(dataset)
    source=b.read(ROOT/'data/processed/web_summary_by_region.json')
    for metric in ['tonnes','tkm']:
        for direction in ['all','outbound','inbound']:
            r=b.compare_regions(con,dataset,regions=['DEA12','DEE03'],year=2024,metric=metric,direction=direction)
            expected=[source[k]['2024']['total_'+metric] if direction=='all' else
                      source[k]['2024']['directions_'+metric][direction] for k in ['DEA12','DEE03']]
            check(f'Vergleich {metric} {direction}',[x['value'] for x in r['rows']]==expected)
        for mode in ['road','rail','iww']:
            r=b.direction_balance(con,dataset,region='DEA12',year=2024,mode=mode,metric=metric)
            p=source['DEA12']['2024']['modes_direction_'+metric][mode]
            expected=p['outbound']-p['inbound'] if p['outbound'] is not None and p['inbound'] is not None else None
            check(f'Saldo {mode} {metric}',r['balance']==expected and r['empty_trips'] is None)
    for direction in ['all','outbound','inbound']:
        for metric in ['tonnes','flights']:
            r=b.node_statistics(con,dataset,kind='air',node='EDDP',year=2024,metric=metric,direction=direction)
            raw=b.rows(con.execute('SELECT * FROM read_parquet(?) WHERE node=? AND year=2024 AND metric=? AND direction=?',
                [str(dataset/'air_statistics.parquet'),'EDDP',metric,direction]))[0]
            check(f'Flughafen verfügbar {metric} {direction}',r['value']==raw['known_sum'] and r['status']=='available' and r['restricted_count']==raw['restricted_count'])
    sea=b.node_partners(con,dataset,kind='sea',node='DEHAM',year=2024,metric='teu',top=5)
    check('Hamburg 190 nicht anwendbare statt unbekannte TEU-Partner',sea['unknown_relations']==0 and sea['not_applicable_relations']==190 and sea['status']=='available')
    all_sea=b.node_partners(con,dataset,kind='sea',node='DEHAM',year=2024,metric='teu',top=1000)
    check('See Nenner vor Top-Begrenzung',math.isclose(sea['denominator'],all_sea['denominator'],rel_tol=1e-12) and abs(sum(x['share_pct'] for x in all_sea['rows'])-100)<1e-8)
    weight=b.node_partners(con,dataset,kind='sea',node='DEHAM',year=2024,metric='tonnes')
    check('See fehlende Gewichte sperren Nenner',weight['status']=='partial' and weight['unknown_relations']>0 and weight['denominator'] is None and all(x['share_pct'] is None for x in weight['rows']))
    total=b.node_statistics(con,dataset,kind='sea',node='DEHAM',year=2024,metric='teu')
    check('See Qualitätszähler und Quellen',total['restricted_count']==0 and bool(total['source_ids']))
    check('National fehlender Jahrgang',b.national(con,dataset,year=1900)['status']=='missing_year' and b.national(con,dataset,year=2025,mode='road')['status']=='missing_year')
    down=b.forecast_ranking(con,dataset,descending=False)
    check('Prognose stärkste Rückgänge',down['descending'] is False and [x['value'] for x in down['rows']]==sorted(x['value'] for x in down['rows']) and down['rows'][0]['value']<0)

    # A controlled in-memory source exercises NA-only, zero, unknown and absent partners.
    con.execute('''CREATE OR REPLACE TEMP TABLE partner_fixture AS SELECT * FROM (VALUES
        ('NA',NULL::DOUBLE,0,2),('ZERO',0.0,0,0),('UNKNOWN',NULL::DOUBLE,1,0),('KNOWN',10.0,0,0))
        v(partner,known_sum,missing_count,not_applicable_count)''')
    con.execute('''CREATE OR REPLACE TEMP VIEW partner_source AS SELECT *,partner AS node,'FR' AS partner_country,
        2024 AS year,'teu' AS metric,'outbound' AS direction,2 AS source_rows,0 AS restricted_count,'fixture' AS source_id FROM partner_fixture''')
    class Fixture:
        def execute(self,sql,args):
            return con.execute(sql.replace('read_parquet(?)','partner_source'),args[1:])
    for node,status,unknown,na in [('NA','not_applicable',0,1),('ZERO','available',0,0),('UNKNOWN','partial',1,0),('ABSENT','missing_row',0,0)]:
        r=b.node_partners(Fixture(),dataset,kind='sea',node=node,year=2024,metric='teu')
        check('Partnerzustand '+node,r['status']==status and r['unknown_relations']==unknown and r['not_applicable_relations']==na and r['denominator'] is None)

    from scripts.pipelines import build_b0406_analysis as builder
    deps={k:{'path':k,'snapshot_id':k,'manifest_sha256':k+'hash'} for k in ['b01','b02','b03']}
    manifests={'b01':{},'b02':{'b01':deps['b01']},'b03':{'b01':deps['b01'],'b02':deps['b02']}}
    for child,parent in [('b02','b01'),('b03','b01'),('b03','b02')]:
        for field in ['snapshot_id','manifest_sha256']:
            broken=copy.deepcopy(manifests);broken[child][parent][field]='wrong'
            with patch.object(builder,'read',side_effect=lambda p:broken[p.parent.name]):
                try:builder.check_dependency_chain(deps);blocked=False
                except ValueError:blocked=True
            check(f'Abhängigkeitskonflikt {child} {parent} {field}',blocked)

    from scripts.validation import validate_b0406_analysis as validator
    with tempfile.TemporaryDirectory(prefix='wbp-b0406-gate-',dir='C:/tmp') as tmp:
        folder=Path(tmp);manifest={'snapshot_id':'fixture'}
        save_json(folder/'manifest.json',manifest);save_json(folder/'validation.json',{'passed':True})
        report={'snapshot_id':'fixture','passed':True,'count':10,'checks':[{'passed':True}]*10,
                'manifest_sha256':sha256(folder/'manifest.json'),
                'validator_sha256':sha256(Path(validator.__file__).with_name('validate_b0406_partner_mapping.py'))}
        save_json(folder/'current.json',{'old':'preserve'})
        original=(folder/'current.json').read_bytes()
        variants=[None,{**report,'passed':False},{**report,'snapshot_id':'other'},
                  {**report,'manifest_sha256':'wrong'},{**report,'validator_sha256':'wrong'},
                  {**report,'checks':[{'passed':False}]*10},{**report,'count':9}]
        for i,bad in enumerate(variants):
            if bad is not None:save_json(folder/'partner_mapping_validation.json',bad)
            try:validator.activate_dataset(folder,manifest,{'passed':True},store=folder);blocked=False
            except ValueError:blocked=True
            check(f'Freigabe verweigert bei ungültiger Partnerprüfung {i}',blocked and (folder/'current.json').read_bytes()==original)
        save_json(folder/'partner_mapping_validation.json',report)
        try:validator.activate_dataset(folder,manifest,{'passed':False},store=folder);blocked=False
        except ValueError:blocked=True
        check('Fehlgeschlagene Hauptprüfung sperrt Freigabe',blocked and (folder/'current.json').read_bytes()==original)
        for i in range(2):
            validator.activate_dataset(folder,manifest,{'passed':True},store=folder)
            pointer=b.read(folder/'current.json')
            check('Freigabe und erneute Freigabe vollständig '+str(i),set(pointer)=={'snapshot_id','manifest_sha256','validation_sha256','partner_mapping_validation_sha256'} and all(pointer[k]==sha256(folder/f) for k,f in [('manifest_sha256','manifest.json'),('validation_sha256','validation.json'),('partner_mapping_validation_sha256','partner_mapping_validation.json')]))
        check('Keine temporären Freigabedateien',not list(folder.glob('*.tmp')))

    env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1'}
    for function,parameters in [('compare',{'regions':['DEA12','DEE03'],'year':2024,'metric':'tkm'}),
          ('partners',{'kind':'sea','node':'DEHAM','year':2024,'metric':'teu'}),
          ('node',{'kind':'air','node':'EDDP','year':2024}),('forecast',{'descending':False})]:
        proc=subprocess.run([sys.executable,str(ROOT/'scripts/analysis/query_b0406.py'),function,'--dataset',str(dataset),
                             '--parameters',json.dumps(parameters)],capture_output=True,text=True,encoding='utf-8',env=env,timeout=60)
        value=json.loads(proc.stdout) if proc.returncode==0 else {}
        check('Lokaler Aufruf '+function,proc.returncode==0 and value.get('snapshot_id')==b.read(dataset/'manifest.json')['snapshot_id'])


if __name__=='__main__':
    import duckdb
    results=[]
    with duckdb.connect() as con:
        run_checks(con,Path(sys.argv[1]),lambda name,ok:results.append({'name':name,'passed':bool(ok)}))
    print(json.dumps(results,ensure_ascii=False,indent=2))
    sys.exit(0 if all(x['passed'] for x in results) else 1)
