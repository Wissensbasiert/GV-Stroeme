"""B04–B06 gemeinsam reproduzierbar aufbauen; Aktivierung erst im Prüfskript."""
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
import uuid
from contextlib import ExitStack
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import duckdb
from scripts.analysis.b01 import ROOT, save_json, sha256, literal, parse_measure
from scripts.analysis.b0406 import STORE, read
from scripts.pipelines.build_b03_analysis import checked_dependency

CODE=['scripts/pipelines/build_b0406_analysis.py','scripts/analysis/b0406.py',
      'scripts/validation/validate_b0406_analysis.py','scripts/analysis/query_b0406.py',
      'scripts/validation/validate_b0406_partner_mapping.py']
CODE.append('scripts/validation/check_b0406_regressions.py')


def check_dependency_chain(dependencies):
    manifests={key:read(ROOT/dep['path']/'manifest.json') for key,dep in dependencies.items()}
    for child,parent in [('b02','b01'),('b03','b01'),('b03','b02')]:
        link=manifests[child][parent]
        expected=dependencies[parent]
        if any(link.get(field)!=expected[field] for field in ['snapshot_id','manifest_sha256']):
            raise ValueError(f'Abhängigkeiten passen nicht zusammen: {child} → {parent}')


def eurostat(path,statistics=False):
    """Alle Jahreszellen 2016 ff. einschließlich Fehlzellen und Originalzeichen."""
    with path.open(encoding='utf-8-sig',newline='') as handle:
        reader=csv.reader(handle,delimiter='\t'); header=next(reader)
        years=[(i,int(h.strip())) for i,h in enumerate(header) if re.fullmatch(r'20\d\d',h.strip()) and int(h.strip())>=2016]
        for number,row in enumerate(reader,1):
            d=row[0].strip().split(',')
            if statistics:
                if len(d)!=6 or d[0]!='A' or d[3:5]!=['TOTAL','TOTAL']: continue
                pair=d[5].split('_')
                if len(pair)!=2 or pair[0]!='DE': continue
                node=pair[1]; partner=country=None
            else:
                if len(d)!=4 or d[0]!='A': continue
                pair=d[3].split('_')
                if len(pair)!=4 or pair[0]!='DE': continue
                node,country,partner=pair[1:]
            mappings={'T':('tonnes',{'FRM_LD_NLD':'all','FRM_LD':'outbound','FRM_NLD':'inbound'}),
                      'FLIGHT':('flights',{'CAF_FRM':'all','CAF_FRM_DEP':'outbound','CAF_FRM_ARR':'inbound'})}
            if d[1] not in mappings: continue
            metric,directions=mappings[d[1]]
            if d[2] not in directions: continue
            for index,year in years:
                raw=row[index].strip() if index<len(row) else ''
                match=re.fullmatch(r'([0-9]+(?:\.[0-9]+)?)\s*([a-z ]*)',raw)
                value=float(match[1]) if match else None
                flag=match[2].strip() if match else raw
                yield {'node':node,'partner':partner,'partner_country':country,'year':year,
                       'direction':directions[d[2]],'metric':metric,'source_record':number,
                       'raw_value':raw,'raw_flag':flag,'known_sum':value,'missing_count':int(value is None),
                       'restricted_count':int(bool(flag)),'source_rows':1,
                       'source_id':'AVIA_GOOA' if statistics else 'AVIA_GOR_DE'}


def write_records(con,stage,name,records,schema,tmp):
    intermediate=tmp/(name+'.jsonl')
    with intermediate.open('w',encoding='utf-8') as handle:
        for record in records:
            handle.write(json.dumps(record,ensure_ascii=False,allow_nan=False)+'\n')
    columns='{'+','.join(literal(k)+':'+literal(v) for k,v in schema.items())+'}'
    con.execute('COPY (SELECT * FROM read_json('+literal(intermediate)+", format='newline_delimited',columns="+columns+')) TO '+literal(stage/(name+'.parquet'))+' (FORMAT PARQUET, COMPRESSION ZSTD)')
    return con.execute('SELECT count(*) FROM read_parquet(?)',[str(stage/(name+'.parquet'))]).fetchone()[0]


def build():
    probe=Path('C:/tmp')/('wbp-b0406-probe-'+uuid.uuid4().hex)
    probe.mkdir();probe.rmdir()
    print('Prüfe zusammengehörige B01–B03-Stände',flush=True)
    dependencies={}
    for key in ['b01','b02','b03']:
        path,m=checked_dependency(ROOT/'data/analysis'/key)
        dependencies[key]={'path':path.relative_to(ROOT).as_posix(),'snapshot_id':m['snapshot_id'],
                           'manifest_sha256':sha256(path/'manifest.json')}
    b01=ROOT/dependencies['b01']['path']; bm=read(b01/'manifest.json')
    check_dependency_chain(dependencies)
    inputs=['data/processed/nuts3_de_'+v+'.geojson' for v in ['2016','2021','2024']]
    inputs+=['data/processed/web_summary_by_region.json','data/processed/web_forecast_core.json',
             'data/processed/national_benchmarks.json','data/raw/Luftverkehr/estat_avia_gor_de.tsv',
             'data/raw/Luftverkehr/estat_avia_gooa.tsv',
             'data/raw/Straße/KBA/VE7_Verflechtung_NUTS3/ve7_2010_2024.csv']
    inputs += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'data/raw/MRTM OpenData').glob('MRTM_OpenData_*.csv'))]
    inputs += [s['path'] for s in bm['sources'] if s['mode']!='road']
    inputs += [p.relative_to(ROOT).as_posix() for p in (ROOT/'data/raw/MRTM OpenData').glob('*.pdf')]
    digests={}
    for p in inputs:
        print('Quellenfassung: '+p,flush=True)
        digests[p]=sha256(ROOT/p)
    identity={'dependencies':dependencies,'input_sha256':digests,
              'code_sha256':{p:sha256(ROOT/p) for p in CODE}}
    for source in bm['sources']:
        if sha256(ROOT/source['path'])!=source['sha256']:
            raise ValueError('B01-Rohdaten verändert')
    snapshot=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()[:20]
    destination=STORE/'releases'/snapshot
    if destination.exists():
        print(destination);return destination
    with tempfile.TemporaryDirectory(prefix='wbp-b0406-',dir='C:/tmp') as temp, ExitStack() as resources:
        tmp=Path(temp);stage=tmp/'release';stage.mkdir()
        con=resources.enter_context(duckdb.connect(str(tmp/'work.duckdb')))
        con.execute("SET threads=2");con.execute("SET memory_limit='1GB'")
        counts={}
        registries={v:{f['properties']['NUTS_ID']:f['properties']['NUTS_NAME'] for f in read(ROOT/('data/processed/nuts3_de_'+v+'.geojson'))['features']} for v in ['2016','2021','2024']}
        save_json(stage/'regions.json',registries)
        shutil.copyfile(ROOT/dependencies['b02']['path']/'source_coverage.json',stage/'source_coverage.json')
        print('B04: Regionsprofile und Prognose',flush=True)
        profiles=read(ROOT/'data/processed/web_summary_by_region.json')
        keep=['total_tonnes','total_tkm','modes_tonnes','modes_tkm','modes_direction_tonnes','modes_direction_tkm',
              'directions_tonnes','directions_tkm','groups_7_tonnes','groups_7_tkm']
        records=({'id':r,'year':int(y),'profile':json.dumps({k:p[k] for k in keep if k in p},ensure_ascii=False)}
                 for r,ys in profiles.items() for y,p in ys.items() if r in registries['2024' if int(y)>=2024 else '2021' if int(y)>=2021 else '2016'])
        counts['regional_profiles']=write_records(con,stage,'regional_profiles',records,{'id':'VARCHAR','year':'INTEGER','profile':'VARCHAR'},tmp)
        vp=read(ROOT/'data/processed/web_forecast_core.json')['scenarios'];forecast=[]
        for region,name in registries['2024'].items():
            for mode in ['road','rail','iww']:
                for metric in ['tonnes','tkm']:
                    for direction in ['all','outbound','inbound','binnen']:
                        values=[vp[s]['regions'].get(region,{}).get('modes_direction_'+metric,{}).get(mode,{}).get(direction) for s in ['2019_BASE','2040_P1']]
                        forecast.append(dict(id=region,name=name,mode=mode,metric=metric,direction=direction,base=values[0],target=values[1]))
        counts['forecast']=write_records(con,stage,'forecast',forecast,{k:('DOUBLE' if k in {'base','target'} else 'VARCHAR') for k in forecast[0]},tmp)
        print('B05: Nationale Verkehrsbeziehungen und Inlandsleistung',flush=True)
        con.execute('''CREATE TABLE national AS SELECT year_ref AS year,mode,metric,traffic_relationship AS relationship,
            sum(value) AS known_sum,count(*) AS source_rows,count(*) FILTER(WHERE value IS NULL) AS missing_count,
            count(*) FILTER(WHERE quality_status='restricted') AS restricted_count,
            CASE WHEN count(*) FILTER(WHERE value IS NULL)>0 THEN NULL ELSE sum(value) END AS value
            FROM read_parquet(?) WHERE mode IN ('rail','iww') AND metric IN ('tonnes','tkm') GROUP BY ALL''',[str(b01/'source_values.parquet')])
        road=[]
        with (ROOT/'data/raw/Straße/KBA/VE7_Verflechtung_NUTS3/ve7_2010_2024.csv').open(encoding='utf-8-sig',newline='') as handle:
            for r in csv.DictReader(handle,delimiter=';'):
                for metric,field in [('tonnes','Tonnen'),('tkm','Inlands_tkm')]:
                    value,status,quality=parse_measure(r[field],r['ZS_'+field],True)
                    road.append({'year':int(r['Jahr']),'mode':'road','metric':metric,'relationship':r['Hauptverkehrsbeziehung'],
                                 'value':value,'restricted':int(quality=='restricted')})
        write_records(con,stage,'road_national_evidence',road,{'year':'INTEGER','mode':'VARCHAR','metric':'VARCHAR','relationship':'VARCHAR','value':'DOUBLE','restricted':'INTEGER'},tmp)
        con.execute('''INSERT INTO national SELECT year,mode,metric,relationship,sum(value),count(*),
            count(*) FILTER(WHERE value IS NULL),sum(restricted),
            CASE WHEN count(*) FILTER(WHERE value IS NULL)>0 THEN NULL ELSE sum(value) END
            FROM read_parquet(?) GROUP BY ALL''',[str(stage/'road_national_evidence.parquet')])
        con.execute('COPY national TO '+literal(stage/'national.parquet')+' (FORMAT PARQUET,COMPRESSION ZSTD)')
        counts['national']=con.execute('SELECT count(*) FROM national').fetchone()[0]
        print('B06: Vollständige veröffentlichte Flughafenrelationen',flush=True)
        air_schema={k:('DOUBLE' if k=='known_sum' else 'INTEGER' if k in {'year','source_record','missing_count','restricted_count','source_rows'} else 'VARCHAR') for k in next(eurostat(ROOT/'data/raw/Luftverkehr/estat_avia_gor_de.tsv'))}
        for name,source,stat in [('air_partners','estat_avia_gor_de.tsv',False),('air_statistics','estat_avia_gooa.tsv',True)]:
            counts[name]=write_records(con,stage,name,eurostat(ROOT/'data/raw/Luftverkehr'/source,stat),air_schema,tmp)
        print('B06: Seehafenpartner aus allen vorhandenen Jahrgängen',flush=True)
        # TEU applies only to containers (source documentation p. 10). Non-container blanks
        # retain a separate not-applicable counter; unknown applicable cells remain unknown.
        con.execute('''CREATE TABLE sea_raw AS SELECT Referenzzeitraum_Jahr,
            Ausladeregion_UNLOCODE,Einladeregion_UNLOCODE,Ausladeregion_HafenID,Einladeregion_HafenID,
            Ausladeregion_ISO,Einladeregion_ISO,Guetergewicht,TEU,Container_Groesse,
            filename AS source_id FROM read_csv(?,delim=';',
            header=true,all_varchar=true,union_by_name=true,filename=true,quote='"')''',
            [[str(ROOT/p) for p in inputs if '/MRTM_OpenData_' in p]])
        con.execute('''CREATE TABLE sea_sides AS SELECT Referenzzeitraum_Jahr AS year,Ausladeregion_UNLOCODE AS node,
            coalesce(Einladeregion_UNLOCODE,'HAFENID:'||Einladeregion_HafenID) AS partner,Einladeregion_ISO AS partner_country,'inbound' AS direction,
            Guetergewicht,TEU,Container_Groesse,source_id FROM sea_raw WHERE Ausladeregion_ISO='DE'
            UNION ALL SELECT Referenzzeitraum_Jahr,Einladeregion_UNLOCODE,coalesce(Ausladeregion_UNLOCODE,'HAFENID:'||Ausladeregion_HafenID),Ausladeregion_ISO,
            'outbound',Guetergewicht,TEU,Container_Groesse,source_id FROM sea_raw WHERE Einladeregion_ISO='DE' ''')
        con.execute('''CREATE TABLE sea_long AS SELECT *, 'tonnes' AS metric,TRY_CAST(replace(Guetergewicht,',','.') AS DOUBLE) AS value FROM sea_sides
            UNION ALL SELECT *, 'teu',TRY_CAST(replace(TEU,',','.') AS DOUBLE) FROM sea_sides''')
        con.execute('''COPY (SELECT CAST(year AS INTEGER) AS year,node,partner,partner_country,direction,metric,
            regexp_extract(source_id,'[^/\\\\]+$') AS source_id,
            sum(value) AS known_sum,count(*) AS source_rows,
            count(*) FILTER(WHERE value IS NULL AND NOT(metric='teu' AND Container_Groesse IS NULL)) AS missing_count,
            count(*) FILTER(WHERE value IS NULL AND metric='teu' AND Container_Groesse IS NULL) AS not_applicable_count,
            count(*) FILTER(WHERE value IS NULL) AS blank_count,
            CAST(0 AS BIGINT) AS restricted_count
            FROM sea_long GROUP BY ALL) TO '''+literal(stage/'sea_partners.parquet')+' (FORMAT PARQUET,COMPRESSION ZSTD)')
        counts['sea_partners']=con.execute('SELECT count(*) FROM read_parquet(?)',[str(stage/'sea_partners.parquet')]).fetchone()[0]
        save_json(stage/'source_contracts.json',{
            'national':'SGV/IWW alle B01-Quellzeilen; VE7 Tonnen und Inlands_tkm mit eigenem ZS. Keine Summe gemischter Regionsebenen.',
            'relationships':{'1':'Binnenverkehr Deutschland','2':'Versand in das Ausland','3':'Empfang aus dem Ausland','4':'Transitverkehr','XX':'Quellenangabe unzugeordnet'},
            'air':'AVIA_GOR_DE Jahreswerte ab 2016, Partnerland aus Quellschlüssel; fehlende und gekennzeichnete Zellen erhalten. Keine Top-Kürzung. AVIA_GOOA getrennte Knotenrandsumme.',
            'sea':'Alle MRTM-Jahrgänge, Ein-/Ausladeseiten deutscher Häfen. Original-UNLOCODE als Text; fehlende Partner erhalten. Leere Gewichte bleiben unbekannt. Leere TEU ohne Containergröße sind nicht anwendbar, nach Beschreibung S. 10; separate Zähler statt Nullfüllung.',
            'sea_documentation_conflict':'Datensatzbeschreibung 22.05.2025 S. 5/10 nennt Tonnen und Brutto-Brutto-Gewicht; tatsächliches Feld heißt Guetergewicht. Leere Gewichte bei Leercontainern bleiben ungeklärt. TEU laut Beschreibung nur bei Containertransport.',
            'regional':'D01 unveränderte Profilwerte, Binnen bei Versand+Empfang doppelt. B04-Verbünde ausschließlich B01-OD; B02-Gebietsgrenzen bleiben wirksam.',
            'forecast':'400 deutsche NUTS-3-Gebiete aus Geometrie 2024; ungerundete D05-Ausgangswerte; 2019_BASE und 2040_P1.'})
        con.close()
        save_json(stage/'manifest.json',{**identity,'snapshot_id':snapshot,'row_counts':counts,
                  'schema_version':'1.0.0','output_sha256':{p.name:sha256(p) for p in stage.iterdir()},
                  'scope':'B04–B06 lokal; keine Server-/Modellanbindung; fachliche Grenzen im Quellenvertrag'})
        destination.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(stage,destination)
    print(destination,flush=True);return destination


if __name__=='__main__':
    build()
