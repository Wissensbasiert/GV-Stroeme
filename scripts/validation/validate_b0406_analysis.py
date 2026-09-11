"""Quellenabgleich, reale Referenzen und fachliche Grenzfälle für B04–B06."""
import argparse
import csv
import json
import math
import sys
import uuid
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import duckdb
from scripts.analysis import b0406 as b
from scripts.analysis.b01 import ROOT,save_json,sha256,resolve_dataset
from scripts.pipelines.build_b0406_analysis import check_dependency_chain


def partner_report_valid(dataset,manifest):
    try:
        r=b.read(Path(dataset)/'partner_mapping_validation.json')
        checks=r.get('checks',[])
        return (r.get('passed') is True and r.get('snapshot_id')==manifest['snapshot_id']
                and r.get('manifest_sha256')==sha256(Path(dataset)/'manifest.json')
                and r.get('validator_sha256')==sha256(Path(__file__).with_name('validate_b0406_partner_mapping.py'))
                and len(checks)==r.get('count') and len(checks)>=10
                and all(c.get('passed') is True for c in checks))
    except (OSError,ValueError,KeyError,TypeError):
        return False


def activate_dataset(dataset,manifest,report,store=b.STORE):
    if report.get('passed') is not True or not partner_report_valid(dataset,manifest):
        raise ValueError('Aktivierung benötigt beide bestandenen Prüfungen desselben Datenstands')
    pointer={'snapshot_id':manifest['snapshot_id'],'manifest_sha256':sha256(dataset/'manifest.json'),
             'validation_sha256':sha256(dataset/'validation.json'),
             'partner_mapping_validation_sha256':sha256(dataset/'partner_mapping_validation.json')}
    temporary=Path(store)/('current.'+uuid.uuid4().hex+'.tmp')
    try:
        save_json(temporary,pointer)
        temporary.replace(Path(store)/'current.json')
    finally:
        temporary.unlink(missing_ok=True)


def validate(dataset,activate=False):
    dataset=Path(dataset);m=b.read(dataset/'manifest.json');checks=[]
    def check(name,condition,detail=None):
        checks.append({'name':name,'passed':bool(condition),'detail':detail})
        if not condition: print('FAIL '+name+': '+str(detail),flush=True)
    def close(a,z):
        return a is not None and z is not None and math.isclose(a,z,rel_tol=1e-12,abs_tol=1e-5)
    for category in ['input_sha256','code_sha256','output_sha256']:
        for file,digest in m[category].items():
            check(category+': '+file,sha256((dataset if category=='output_sha256' else ROOT)/file)==digest)
    try:
        check_dependency_chain(m['dependencies']);chain_ok=True
    except (ValueError,KeyError):
        chain_ok=False
    check('Vollständige Abhängigkeitskette B01 B02 B03',chain_ok)
    check('Partnerprüfung bestanden und an Manifest sowie Prüfer gebunden',partner_report_valid(dataset,m))
    for key,dep in m['dependencies'].items():
        p=ROOT/dep['path'];dm=b.read(p/'manifest.json');v=b.read(p/'validation.json')
        check('dependency '+key,v['passed'] and v['snapshot_id']==dep['snapshot_id'] and sha256(p/'manifest.json')==dep['manifest_sha256'])
        check('active '+key,resolve_dataset(ROOT/'data/analysis'/key)==p)
        for name,digest in dm['output_sha256'].items():check(key+' output '+name,sha256(p/name)==digest)
    con=duckdb.connect();con.execute('SET threads=1')
    # Compact synthetic OD: the union logic is checked against hand-calculated totals.
    con.execute('''CREATE TABLE fixture AS SELECT * FROM (VALUES
        ('A','B',100.0,0),('A','C',40.0,0),('C','B',60.0,0),('C','D',999.0,0))
        v(origin_id,dest_id,known_sum,missing_count)''')
    con.execute('''CREATE VIEW synthetic AS SELECT *,2024 AS year_ref,'rail' AS mode,'tonnes' AS metric,
        '1' AS group_7_id,1 AS source_rows,0 AS restricted_count,0 AS unknown_quality_count,'test' AS source_id FROM fixture''')
    # aggregate_union accepts read_parquet; replacement SQL uses a transient in-memory adapter only in tests.
    class Fixture:
        def execute(self,sql,args):
            sql=sql.replace('read_parquet(?)','synthetic');args=args[:2]+args[3:]
            return con.execute(sql,args)
    union=b.aggregate_union(Fixture(),'unused',regions=['A','B'],year=2024,mode='rail')
    check('T08 innen außen eindeutig',union['unique_value']==200 and union['touch_value']==300 and union['parts']['internal']['value']==100)
    con.execute('DELETE FROM fixture');con.execute("INSERT INTO fixture VALUES ('A','A',10,0),('A','B',20,0),('B','A',30,0)")
    union=b.aggregate_union(Fixture(),'unused',regions=['A'],year=2024,mode='rail')
    check('T26 Binnen einmal und Berührungen',union['unique_value']==60 and union['touch_value']==70 and union['local_transit'] is None)
    con.execute("INSERT INTO fixture VALUES ('A','C',NULL,1)")
    union=b.aggregate_union(Fixture(),'unused',regions=['A'],year=2024,mode='rail')
    check('Fehlwert keine vollständige Summe',union['unique_value'] is None and union['known_sum']==60)
    check('Ranggleichstand 1 2 2',[r['rank'] for r in b.rank([{'value':200},{'value':100},{'value':100}],top=2)]==[1,2,2])
    for sample in [['DE','DE600'],['EDDP','DE600'],['DE600','DE600'],['Teil Hamburg']]:
        try:b.regions_checked(dataset,sample);ok=False
        except ValueError:ok=True
        check('Unzulässige Raumliste '+str(sample),ok)
    changes=[{'id':'A','base':1000,'target':1500},{'id':'B','base':1,'target':10},
             {'id':'C','base':0,'target':10},{'id':'D','base':10,'target':0},{'id':'E','base':None,'target':1}]
    check('Zeitvergleich gesperrt',b.change_ranking(changes)['status']=='comparability_not_confirmed')
    absolute=b.change_ranking(changes,comparable=True)
    relative=b.change_ranking(changes,comparable=True,measure='relative')
    check('Absolute Änderung A führt',absolute['rows'][0]['id']=='A')
    check('Kleine Basis sichtbar',relative['rows'][0]['id']=='B' and relative['rows'][0]['value']==900)
    check('Nullbasis absolute Änderung',next(r for r in absolute['rows'] if r['id']=='C')['relative_change_pct'] is None)
    check('Rückgang auf Null',next(r for r in relative['rows'] if r['id']=='D')['value']==-100)
    profiles=b.compare_regions(con,dataset,regions=['DEA12','DEE03'],year=2024)
    check('T07 Duisburg Magdeburg',all(close(r['value'],v) for r,v in zip(profiles['rows'],[108215313.5,23180902.5])))
    balance=b.direction_balance(con,dataset,region='DEA12',year=2024)
    check('T25 Saldo und keine Leerfahrten',close(balance['balance'],4236410) and balance['empty_trips'] is None,balance)
    source=b.read(ROOT/'data/processed/web_summary_by_region.json')
    records=b.rows(con.execute('SELECT * FROM read_parquet(?)',[str(dataset/'regional_profiles.parquet')]))
    check('Alle gespeicherten Regionalfelder unverändert',all(all(source[r['id']][str(r['year'])][k]==v for k,v in json.loads(r['profile']).items()) for r in records))
    for direction in ['outbound','inbound','all']:
        check('Sieben Strukturgruppen '+direction,all(len(r['groups'])==7 for r in b.compare_regions(con,dataset,regions=['DEA12','DEE03'],year=2024,direction=direction)['rows']))
    forecast=b.forecast_ranking(con,dataset)
    check('T28 400 passende Räume',forecast['population_count']==400)
    check('T28 Rangfolge', [r['id'] for r in forecast['rows'][:5]]==['DE600','DEA23','DEB34','DE502','DE212'],forecast['rows'])
    # Independent field comparison over every stored forecast row, including zero and missing values.
    vp=b.read(ROOT/'data/processed/web_forecast_core.json')['scenarios']
    fr=b.rows(con.execute('SELECT * FROM read_parquet(?)',[str(dataset/'forecast.parquet')]))
    check('Alle Prognoseausgangswerte',all(r[k]==vp[s]['regions'].get(r['id'],{}).get('modes_direction_'+r['metric'],{}).get(r['mode'],{}).get(r['direction']) for r in fr for k,s in [('base','2019_BASE'),('target','2040_P1')]))
    national=b.national(con,dataset,year=2024)
    check('T22 bisheriger Betrag als bekannte Teilsumme',close(sum(r['known_sum'] for r in national['modes']),624919760431))
    check('T22 vollständiger Split bei sieben fehlenden Inlandswerten gesperrt',
          national['denominator'] is None and all(r['share_pct'] is None for r in national['modes'])
          and sum(r['missing_count'] for r in national['relationships'] if r['mode']=='road')==7)
    rail=b.national(con,dataset,year=2024,mode='rail')
    transit=next(r for r in rail['relationships'] if r['relationship']=='4')
    check('T27 Schienentransit',close(transit['value'],13622343988))
    check('T27 Transitanteil',abs(transit['share_pct']-10.784)<0.001)
    check('Unvollständiges Jahr kein Split',b.national(con,dataset,year=2025)['denominator'] is None)
    # Independently accumulate original CSV by national relationship, including all unassigned rows.
    bm=b.read(ROOT/m['dependencies']['b01']['path']/'manifest.json')
    expected=defaultdict(lambda:[0.0,0,0])
    for source_info in bm['sources']:
        mode=source_info['mode']
        if mode=='road': fields=[('tonnes','Tonnen'),('tkm','Inlands_tkm')];yf='Jahr';rf='Hauptverkehrsbeziehung'
        elif mode=='rail':fields=[('tonnes','Befoerderungsmenge_in_Tonnen'),('tkm','Befoerderungsleistung_in_TKM')];yf='Referenzzeitraum_Jahr';rf='Verkehrsbeziehung'
        else:fields=[('tonnes','Tonnen'),('tkm','Tonnen_km')];yf='Referenzzeitraum_Jahr';rf='Verkehrsbeziehung'
        with (ROOT/source_info['path']).open(encoding=source_info['encoding'],newline='') as handle:
            for r in csv.DictReader(handle,delimiter=';'):
                for metric,field in fields:
                    raw=r[field].strip();flag=r.get('ZS_'+field,'').strip()
                    missing=not raw or flag in {'/','.'}
                    value=None if missing else float(raw.replace(',','.'))
                    if flag=='-':value=0;missing=False
                    slot=expected[(int(r[yf]),mode,metric,r[rf])];slot[0]+=value or 0;slot[1]+=1;slot[2]+=int(missing)
    actual=b.rows(con.execute('SELECT * FROM read_parquet(?)',[str(dataset/'national.parquet')]))
    check('Nationale Schlüssel vollständig',set(expected)=={(r['year'],r['mode'],r['metric'],r['relationship']) for r in actual})
    for mode in ['road','rail','iww']:
        check('Alle nationalen Originalwerte '+mode,all(close(r['known_sum'],expected[(r['year'],mode,r['metric'],r['relationship'])][0]) and [r['source_rows'],r['missing_count']]==expected[(r['year'],mode,r['metric'],r['relationship'])][1:] for r in actual if r['mode']==mode))
    # Read annual air cells independently and compare raw spelling/value/missingness, not the builder generator.
    for product,filename,stat in [('air_partners','estat_avia_gor_de.tsv',False),('air_statistics','estat_avia_gooa.tsv',True)]:
        lookup={};total=0
        with (ROOT/'data/raw/Luftverkehr'/filename).open(encoding='utf-8-sig',newline='') as handle:
            reader=csv.reader(handle,delimiter='\t');head=next(reader)
            annual={int(h.strip()):i for i,h in enumerate(head) if h.strip().isdigit() and int(h.strip())>=2016}
            for nr,row in enumerate(reader,1):
                d=row[0].split(',')
                if d[0]!='A' or d[1] not in {'T','FLIGHT'}:continue
                if d[2] not in ({'FRM_LD_NLD','FRM_LD','FRM_NLD'} if d[1]=='T' else {'CAF_FRM','CAF_FRM_DEP','CAF_FRM_ARR'}):continue
                if stat and (len(d)!=6 or d[3:5]!=['TOTAL','TOTAL']):continue
                pair=d[-1].split('_')
                if len(pair)!=(2 if stat else 4) or pair[0]!='DE':continue
                for yr,i in annual.items():lookup[(nr,yr)]=row[i].strip() if i<len(row) else ''
        cells=b.rows(con.execute('SELECT * FROM read_parquet(?)',[str(dataset/(product+'.parquet'))]))
        check(product+' alle Jahreszellen erhalten',len(cells)==len(lookup) and all(r['raw_value']==lookup[(r['source_record'],r['year'])] for r in cells))
        check(product+' eindeutige Schlüssel',len({(r['node'],r['partner'],r['partner_country'],r['year'],r['metric'],r['direction']) for r in cells})==len(cells))
    air=b.node_partners(con,dataset,kind='air',node='EDDP',year=2024,international=True,top=1000)
    check('T35 internationaler Nenner',close(air['denominator'],662332),air['denominator'])
    check('T35 59 positive Partner',air['positive_relations']==59,air['positive_relations'])
    check('T35 OBBI Bahrain',any(r['id']=='OBBI' and r['partner_country']=='BH' for r in air['rows']))
    check('Top 5 verändert Nenner nicht',b.node_partners(con,dataset,kind='air',node='EDDP',year=2024,international=True,top=5)['denominator']==air['denominator'])
    check('Kein Hafen gewählt',b.node_statistics(con,dataset,kind='sea',node=None,year=2024)['status']=='needs_clarification')
    check('Luftflugzahlen 2025 gesperrt',b.node_statistics(con,dataset,kind='air',node='EDDP',year=2025,metric='flights')['status']=='not_available')
    # Independent streaming sea totals for each source, year, side and metric (including null-cell counts).
    sea_expected=defaultdict(lambda:[0.0,0,0,0])
    for path in sorted((ROOT/'data/raw/MRTM OpenData').glob('MRTM_OpenData_*.csv')):
        with path.open(encoding='utf-8-sig',newline='') as handle:
            reader=csv.reader(handle,delimiter=';');header=next(reader);ix={v:i for i,v in enumerate(header)}
            for r in reader:
                for side,prefix in [('outbound','Einladeregion'),('inbound','Ausladeregion')]:
                    if r[ix[prefix+'_ISO']]!='DE':continue
                    for metric,field in [('tonnes','Guetergewicht'),('teu','TEU')]:
                        raw=r[ix[field]].strip();slot=sea_expected[(path.name,int(r[ix['Referenzzeitraum_Jahr']]),side,metric)]
                        na=not raw and metric=='teu' and not r[ix['Container_Groesse']]
                        slot[0]+=float(raw.replace(',','.')) if raw else 0;slot[1]+=1
                        slot[2]+=int(not raw and not na);slot[3]+=int(na)
        print('Quellenprüfung '+path.name,flush=True)
    actual=b.rows(con.execute('''SELECT source_id,year,direction,metric,sum(known_sum) AS known_sum,
        sum(source_rows) AS source_rows,sum(missing_count) AS missing_count,
        sum(not_applicable_count) AS not_applicable_count FROM read_parquet(?) GROUP BY ALL''',[str(dataset/'sea_partners.parquet')]))
    check('Alle Seequellen erfasst',len(actual)==len(sea_expected))
    for year in sorted({r['year'] for r in actual}):
        check('See Originalsummen, Fehlzellen und Anwendbarkeit '+str(year),all(close(r['known_sum'],sea_expected[(r['source_id'],year,r['direction'],r['metric'])][0]) and [r['source_rows'],r['missing_count'],r['not_applicable_count']]==sea_expected[(r['source_id'],year,r['direction'],r['metric'])][1:] for r in actual if r['year']==year))
    for metric in ['tonnes','teu']:
        sea=b.node_statistics(con,dataset,kind='sea',node='DEHAM',year=2024,metric=metric)
        check('Hamburg '+metric+' ohne Nullfüllung',sea['known_sum'] is not None and (sea['value'] is None if sea['missing_count'] else sea['value']==sea['known_sum']))
    check('Hamburg TEU 2024 Containerabgrenzung',close(b.node_statistics(con,dataset,kind='sea',node='DEHAM',year=2024,metric='teu')['value'],7828362.9))
    from scripts.validation.check_b0406_regressions import run_checks
    run_checks(con,dataset,check)
    for path in [dataset/'regions.json',dataset/'source_contracts.json',*[ROOT/p for p in m['code_sha256']]]:
        text=path.read_text(encoding='utf-8');check('UTF-8 '+path.name,'\ufffd' not in text)
    report={'snapshot_id':m['snapshot_id'],'passed':all(c['passed'] for c in checks),'checks':checks,
            'validation_code_sha256':sha256(Path(__file__)),
            'build_time_validation_code_sha256':m['code_sha256']['scripts/validation/validate_b0406_analysis.py'],
            'reference_divergence':{'T22':'624.919.760.431 tkm ist die bekannte Summe, kein vollständig belegter Nenner: sieben Inlands_tkm-Zellen 2024 mit ZS=. sind unbekannt. Alte Sollannahme nicht freigegeben.'},
            'count':len(checks),'scope':'Lokale Daten-/Funktionsprüfung B04–B06; keine 45-Fälle-Modellabnahme.'}
    save_json(dataset/'validation.json',report)
    if activate and report['passed']:
        activate_dataset(dataset,m,report)
    print(json.dumps({'passed':report['passed'],'checks':len(checks),'dataset':str(dataset)},ensure_ascii=False),flush=True)
    con.close();return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dataset',type=Path,required=True);p.add_argument('--activate',action='store_true')
    args=p.parse_args();sys.exit(0 if validate(args.dataset,args.activate)['passed'] else 1)
