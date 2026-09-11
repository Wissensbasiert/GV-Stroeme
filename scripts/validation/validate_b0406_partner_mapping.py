"""Zusätzlicher unabhängiger Feldabgleich: Luftzellen, Seehafenpaare 2024, reale Verbünde."""
import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import duckdb
from scripts.analysis import b0406 as b
from scripts.analysis.b01 import ROOT,sha256,save_json


def validate(dataset):
    dataset=Path(dataset);m=b.read(dataset/'manifest.json');checks=[]
    def check(name,passed):checks.append({'name':name,'passed':bool(passed)})
    def close(a,z):return a is not None and z is not None and math.isclose(a,z,rel_tol=1e-12,abs_tol=1e-5)
    con=duckdb.connect();con.execute('SET threads=1')
    for file,table,stat in [('estat_avia_gor_de.tsv','air_partners',False),('estat_avia_gooa.tsv','air_statistics',True)]:
        originals={}
        with (ROOT/'data/raw/Luftverkehr'/file).open(encoding='utf-8-sig',newline='') as handle:
            reader=csv.reader(handle,delimiter='\t');header=next(reader)
            years=[(i,int(x.strip())) for i,x in enumerate(header) if x.strip().isdigit() and int(x.strip())>=2016]
            for nr,r in enumerate(reader,1):
                dimensions=r[0].split(',')
                if dimensions[0]!='A':continue
                for i,year in years:
                    originals[(nr,year)]=(dimensions,r[i].strip() if i<len(r) else '')
        failures=0
        for r in b.rows(con.execute('SELECT * FROM read_parquet(?)',[str(dataset/(table+'.parquet'))])):
            d,raw=originals[(r['source_record'],r['year'])];parts=d[-1].split('_');tokens=raw.split()
            try:value=float(tokens[0]);flag=' '.join(tokens[1:])
            except (ValueError,IndexError):value=None;flag=raw
            failures+=int(r['node']!=parts[1] or (not stat and (r['partner_country']!=parts[2] or r['partner']!=parts[3]))
                          or r['known_sum']!=value or r['missing_count']!=int(value is None)
                          or r['raw_flag']!=flag)
        check(table+' Werte, Zeichen und Länder aus Originalzellen',failures==0)
    expected=defaultdict(lambda:[0.0,0,0,0])
    with (ROOT/'data/raw/MRTM OpenData/MRTM_OpenData_2024.csv').open(encoding='utf-8-sig',newline='') as handle:
        for r in csv.DictReader(handle,delimiter=';'):
            for own,other,direction in [('Einladeregion','Ausladeregion','outbound'),('Ausladeregion','Einladeregion','inbound')]:
                if r[own+'_ISO']!='DE':continue
                node=r[own+'_UNLOCODE'] or None
                partner=r[other+'_UNLOCODE'] or ('HAFENID:'+r[other+'_HafenID'] if r[other+'_HafenID'] else None)
                country=r[other+'_ISO'] or None
                for metric,field in [('tonnes','Guetergewicht'),('teu','TEU')]:
                    slot=expected[(node,partner,country,direction,metric)];raw=r[field].strip()
                    na=not raw and metric=='teu' and not r['Container_Groesse']
                    slot[0]+=float(raw.replace(',','.')) if raw else 0;slot[1]+=1
                    slot[2]+=int(not raw and not na);slot[3]+=int(na)
    data=b.rows(con.execute('SELECT * FROM read_parquet(?) WHERE year=2024',[str(dataset/'sea_partners.parquet')]))
    check('See 2024 vollständige Partnerschlüssel',set(expected)=={(r['node'],r['partner'],r['partner_country'],r['direction'],r['metric']) for r in data})
    failures=0
    for r in data:
        z=expected[(r['node'],r['partner'],r['partner_country'],r['direction'],r['metric'])]
        failures+=int((not close(r['known_sum'],z[0]) if z[1]!=z[2]+z[3] else r['known_sum'] is not None)
                      or [r['source_rows'],r['missing_count'],r['not_applicable_count']]!=z[1:])
    check('See 2024 alle Partnerwerte und Fehlzellen',failures==0)
    annual=ROOT/m['dependencies']['b01']['path']/'annual_od.parquet'
    for mode in ['road','rail','iww']:
        result=b.query_union(con,dataset,regions=['DEA12','DEA13'],year=2024,mode=mode)
        source=b.rows(con.execute('SELECT * FROM read_parquet(?) WHERE year_ref=2024 AND mode=? AND metric=?',[str(annual),mode,'tonnes']))
        selected=[r for r in source if r['origin_id'] in {'DEA12','DEA13'} or r['dest_id'] in {'DEA12','DEA13'}]
        known=sum(r['known_sum'] or 0 for r in selected)
        check('Realer Verbund '+mode,close(result['known_sum'],known) and (result['unique_value'] is None)==any(r['missing_count'] for r in selected))
        check('Qualitätszeichen Verbund '+mode,sum(r['restricted_count'] for r in selected)==sum(r['restricted_count'] for r in result['parts'].values()))
    con.close()
    report={'snapshot_id':m['snapshot_id'],'passed':all(r['passed'] for r in checks),'count':len(checks),
            'checks':checks,'validator_sha256':sha256(Path(__file__)),
            'manifest_sha256':sha256(dataset/'manifest.json'),
            'scope':'Zusätzliche Originalfeldprüfung; ergänzt validation.json'}
    save_json(dataset/'partner_mapping_validation.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2));return report['passed']


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True)
    sys.exit(0 if validate(p.parse_args().dataset) else 1)
