"""Zusätzliche D01-Güterfelder und quellgeprüfte KV-Kennwerte, ohne B01–B07 zu ändern."""
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts.analysis.b01 import parse_measure
from server.analyseassistent.datasets import Datasets, digest, read

ROOT=Path(__file__).resolve().parents[2]
KEEP=['by_mode_groups','by_mode_groups_tkm','modes_tonnes','modes_tkm',
      'modes_direction_tonnes','modes_direction_tkm','data_quality']


def build():
    datasets=Datasets(ROOT,include_support=False)
    original=ROOT/'data/processed/web_summary_by_region.json'
    if digest(original)!=datasets.manifests['b0406']['input_sha256'][original.relative_to(ROOT).as_posix()]:
        raise ValueError('D01-Originalprofil weicht vom geprüften B04-Eingang ab')
    registry=read(datasets.paths['b0406']/'regions.json')
    profiles=read(original)
    goods={region:{year:{key:value for key,value in profile.items() if key in KEEP}
                   for year,profile in years.items()
                   if region in registry['2024' if int(year)>=2024 else '2021' if int(year)>=2021 else '2016']}
           for region,years in profiles.items()}
    goods={region:years for region,years in goods.items() if years}
    web_path=ROOT/'data/processed/web_intermodal.json'
    web=read(web_path)
    if web.get('not_additive') is not True:
        raise ValueError('KV-Quelle muss Nichtadditivität ausdrücklich festhalten')
    hashes={original.relative_to(ROOT).as_posix():digest(original),web_path.relative_to(ROOT).as_posix():digest(web_path)}
    aggregates={}
    checked_sources=[]
    for source in datasets.manifests['b01']['sources']:
        mode=source['mode']
        if mode not in {'rail','iww'}: continue
        path=ROOT/source['path']
        if digest(path)!=source['sha256']: raise ValueError('Gebundene KV-Rohquelle verändert')
        hashes[source['path']]=source['sha256']
        print('KV-Quellenprüfung: '+path.name,flush=True)
        count=0
        with path.open(encoding=source['encoding'],newline='') as handle:
            for raw in csv.DictReader(handle,delimiter=';'):
                count+=1
                year=int(raw['Referenzzeitraum_Jahr'])
                if year<2016: continue
                month=int(raw['Referenzzeitraum_Monat'])
                if month not in range(1,13): raise ValueError('Ungültiger Quellmonat')
                names=registry['2024' if year>=2024 else '2021' if year>=2021 else '2016']
                if mode=='rail':
                    origin,target=raw['Versandregion_NUTS2024'],raw['Empfangsregion_NUTS2024']
                    load=raw['Ladeeinheit'].strip()
                    qualified=None if not load else load!='Keine'
                    values=[raw['Befoerderungsmenge_in_Tonnen'],raw['Befoerderungsleistung_in_TKM']]
                else:
                    origin,target=raw['Einladeregion_NUTS3'],raw['Ausladeregion_NUTS3']
                    container=raw['Container_Groesse'].strip()
                    if container and container not in {'1','2','3','4'}: raise ValueError('Unbekannte Containerklasse')
                    qualified=bool(container)
                    values=[raw['Tonnen'],raw['Tonnen_km']]
                scopes={('DE','all')}
                if origin in names:
                    if target: scopes.add((origin,'internal' if origin==target else 'outbound'))
                    else: scopes.add((origin,'unassigned_outbound'))
                    scopes.add((origin,'all'))
                if target in names:
                    if origin: scopes.add((target,'internal' if origin==target else 'inbound'))
                    else: scopes.add((target,'unassigned_inbound'))
                    scopes.add((target,'all'))
                for metric,text in zip(['tonnes','tkm'],values):
                    value,_,_=parse_measure(text)
                    for region,direction in scopes:
                        key=(year,region,mode,direction,metric)
                        row=aggregates.setdefault(key,{'total_known':0.0,'total_missing':0,'qualified_known':0.0,
                            'qualified_missing':0,'qualification_unknown':0,'unknown_endpoint_count':0,'source_rows':0,'months':set(),'source_ids':set()})
                        row['source_rows']+=1; row['months'].add(month); row['source_ids'].add(source['id'])
                        if not origin or not target: row['unknown_endpoint_count']+=1
                        if value is None: row['total_missing']+=1
                        else: row['total_known']+=value
                        if qualified is None: row['qualification_unknown']+=1
                        if qualified is True:
                            if value is None: row['qualified_missing']+=1
                            else: row['qualified_known']+=value
        if count!=source['records'] or digest(path)!=source['sha256']:
            raise ValueError('Quellzeilenzahl oder nachträgliche Prüfsumme widerspricht B01')
        checked_sources.append({'id':source['id'],'records':count,'sha256':source['sha256']})
    records=[]
    comparisons=0
    explained_differences=[]
    for (year,region,mode,direction,metric),row in sorted(aggregates.items()):
        row={**row,'months':sorted(row['months']),'source_ids':sorted(row['source_ids'])}
        complete=row['months']==list(range(1,13))
        row['total_value']=row['total_known'] if not row['total_missing'] and complete else None
        row['qualified_value']=row['qualified_known'] if not row['qualified_missing'] and not row['qualification_unknown'] and complete else None
        row.update(year=year,region=region,mode=mode,direction=direction,metric=metric)
        source_scope=web.get('scoped_metrics_by_year',{}).get(str(year),{}).get(region,{}).get(mode,{})
        source_direction='binnen' if direction=='internal' else direction
        market='intermodal_load_units' if mode=='rail' else 'containerised_transport'
        for field,section in [('total_value','total'),('qualified_value',market)]:
            expected=source_scope.get(section,{}).get(source_direction,{}).get(metric)
            if row[field] is not None and expected is not None:
                if not math.isclose(row[field],expected,rel_tol=1e-9,abs_tol=0.001):
                    # The dashboard SQL classifies an unknown destination as
                    # outbound via CASE/ELSE, whereas unknown origins are excluded
                    # from inbound by SQL NULL comparison. Keep our external
                    # directions strictly assigned and explain the exact difference.
                    unknown=aggregates.get((year,region,mode,'unassigned_outbound',metric),{}) if direction=='outbound' else {}
                    difference=unknown.get('total_known' if field=='total_value' else 'qualified_known',0)
                    if not math.isclose(row[field]+difference,expected,rel_tol=1e-9,abs_tol=0.001):
                        raise ValueError('KV-Rohquellvergleich widerspricht Dashboardwert: '+str((year,region,mode,direction,metric,field)))
                    explained_differences.append({'year':year,'region':region,'mode':mode,'direction':direction,
                        'metric':metric,'field':field,'difference':difference,'reason':'Dashboard enthält unbekannten Gegenraum im Versand; hier separat unassigned_outbound'})
                comparisons+=1
        records.append(row)
    identity={'dependencies':{p:{'snapshot_id':datasets.pointers[p]['snapshot_id'],
                              'manifest_sha256':datasets.pointers[p]['manifest_sha256']} for p in ['b01','b03','b0406']},
              'input_sha256':hashes,'code_sha256':{'scripts/analysis/prepare_assistant_support.py':digest(Path(__file__))},
              'scope':'D01-Güterfelder mit unveränderter Quellenqualität; KV getrennt nach Statistik, Jahr, Raum, Richtung und Kennzahl.'}
    snapshot=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()[:24]
    dest=ROOT/'data/analysis/assistant_support/releases'/snapshot
    if dest.exists(): raise ValueError('Support-Datenstand existiert bereits; nicht überschreiben')
    dest.mkdir(parents=True)
    def save(name,value):
        (dest/name).write_text(json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n',encoding='utf-8')
    save('goods.json',goods); save('intermodal.json',records)
    # Independent projection check against the full immutable D01 source.
    reloaded=read(dest/'goods.json')
    if any(p!={k:v for k,v in profiles[r][y].items() if k in KEEP} for r,ys in reloaded.items() for y,p in ys.items()):
        raise ValueError('D01-Güterprojektion weicht vom Original ab')
    manifest={**identity,'snapshot_id':snapshot,'output_sha256':{f:digest(dest/f) for f in ['goods.json','intermodal.json']}}
    report={'passed':True,'snapshot_id':snapshot,'sources':checked_sources,'raw_source_comparisons':comparisons,
            'explained_scope_differences':explained_differences,
            'goods_profiles':sum(len(ys) for ys in goods.values()),'kv_records':len(records),
            'limits':['D01-Straßenkennzeichen nicht nacherschlossen; keine NST-20-Aufteilung auf NUTS-3.',
                      'KV: zwölf beobachtete Monate erforderlich; fehlende Werte und Ladeeinheitenkennung bleiben unbekannt.',
                      'Keine harmonisierte Gebietszeitreihe und keine eindeutige KV-Gesamtsumme.']}
    save('manifest.json',manifest);save('validation.json',report)
    pointer={'snapshot_id':snapshot,'manifest_sha256':digest(dest/'manifest.json'),'validation_sha256':digest(dest/'validation.json')}
    target=dest.parent.parent/'current.json'; pending=target.with_suffix('.pending.json')
    pending.write_text(json.dumps(pointer,indent=2)+'\n',encoding='utf-8');pending.replace(target)
    return {**pointer,'kv_records':len(records),'goods_profiles':report['goods_profiles'],'comparisons':comparisons}


if __name__=='__main__': print(json.dumps(build(),ensure_ascii=False))
