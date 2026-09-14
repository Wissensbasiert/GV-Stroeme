"""Begrenzter Zugriff auf bislang nicht erschlossene veröffentlichte Dashboarddaten."""
import json
import math
from pathlib import Path
from functools import lru_cache

MODES = {'road': 'Straße', 'rail': 'Schiene', 'iww': 'Binnenschiff'}
DIRECTIONS = {'outbound': 'Versand', 'inbound': 'Empfang', 'all': 'Gesamtaufkommen', 'binnen': 'Binnenverkehr'}
VP_CODES = ['10','21','22','23','31','32','33','40','50','60','71','72','80','90','100','110','120','130','140','150','160','170','180','190','200']


def field_access_inventory(forecast, regional, sea, intermodal):
    """New published semantic fields require an explicit access or metadata mapping."""
    regional_fields={k:('dashboard_detail' if k in {'by_mode_divisions','by_mode_divisions_tkm','total_trips'} else 'region_profile / goods_structure / goods_history / balance') for k in
        ['balance_tkm','balance_tonnes','by_mode_divisions','by_mode_divisions_tkm','by_mode_groups','by_mode_groups_tkm','data_quality','directions_tkm','directions_tonnes','divisions_20_tkm','divisions_20_tonnes','groups_7_tkm','groups_7_tonnes','modes_direction_tkm','modes_direction_tonnes','modes_tkm','modes_tonnes','total_tkm','total_tonnes','total_trips']}
    forecast_fields={k:'forecast_regions / forecast_relation / dashboard_detail' for k in
        ['behtyp','directions_tkm','directions_tonnes','groups_7_tkm','groups_7_tonnes','growth_2019','id','kv','modal_split_tkm','modal_split_tonnes','modes_by_group_tkm','modes_by_group_tonnes','modes_direction_tkm','modes_direction_tonnes','modes_tkm','modes_tonnes','name','nst_7','tkm','tonnes','vp2040_groups_tkm','vp2040_groups_tonnes']}
    sea_fields={k:('reference_metadata' if k in {'hub_type','lat','lng','name','unlocode'} else 'node_profile / dashboard_detail') for k in
        ['by_division','by_group','commodities','hub_type','inbound_teu','inbound_tonnes','lat','lng','name','outbound_teu','outbound_tonnes','partner_countries','teu','tonnes','units','unlocode']}
    intermodal_fields={k:('reference_metadata' if k in {'schema_version','years','not_additive','relation_scope','sources','definitions','coverage_months'} else 'intermodal_markets / dashboard_detail') for k in
        ['schema_version','years','not_additive','relation_scope','sources','definitions','coverage_months','data_by_year','relations_by_year','scoped_metrics_by_year']}
    families=[('regional', [p for ys in regional.values() for p in ys.values()],regional_fields),
              ('forecast', [p for s in forecast['scenarios'].values() for p in s['regions'].values()],forecast_fields),
              ('sea',[p for ys in sea['seaports'].values() for p in ys.values()],sea_fields),('intermodal',[intermodal],intermodal_fields)]
    unmapped=[]; mappings={}
    for family,records,known in families:
        observed=set().union(*(set(r) for r in records))
        unmapped.extend(family+'.'+k for k in sorted(observed-set(known)))
        mappings[family]={k:known.get(k,'UNMAPPED') for k in sorted(observed)}
    return {'passed':not unmapped,'unmapped_fields':unmapped,'field_access':mappings,
            'limit':'Schema-/Zugriffsabgleich des veröffentlichten Dashboardbestands; kein Beweis jeder freien KI-Formulierung oder sämtlicher nicht veröffentlichter Rohfelder.'}


@lru_cache(maxsize=24)
def read(dataset, name):
    return json.loads((Path(dataset)/name).read_text(encoding='utf-8'))


def files(dataset):
    return [str(Path(dataset)/(s+'_'+m+'.parquet')) for s in ['2019_BASE', '2040_P1'] for m in MODES]


def goods_filter(goods):
    if goods == 'ALL': return '', []
    if goods in '1234567' and len(goods) == 1: return ' AND c7=?', [goods]
    if goods.startswith('VP') and goods[2:] in VP_CODES: return ' AND vp=?', [goods[2:]]
    raise ValueError('Unbekannte Prognosegütergruppe')


def label(dataset, goods):
    if goods == 'ALL': return 'Alle Güter'
    if goods.startswith('VP'):
        return next(x['vp40_name'] for x in read(dataset, 'vp_groups.json') if str(x['vp40_code']) == goods[2:])
    return read(dataset, 'taxonomy.json')['groups_7'][goods]['name']


def forecast_value(con, dataset, region, scenario, mode, metric, direction, goods='ALL'):
    if metric not in {'tonnes','tkm','teu','load_units','kv_tonnes','kv_teu','kv_load_units'}: raise ValueError('Ungültige Kennzahl')
    predicate = {'outbound': 'origin=? AND destination<>origin', 'inbound': 'destination=? AND destination<>origin',
                 'binnen': 'origin=? AND destination=origin', 'all': '(origin=? OR destination=?)'}[direction]
    args = [region, region] if direction == 'all' else [region]
    if region == 'DE':
        if direction != 'all': return None
        predicate, args = 'true', []
    extra, ga = goods_filter(goods)
    result = con.execute(f'SELECT sum({metric}) FROM read_parquet(?) WHERE scenario=? AND mode=? AND {predicate}{extra}',
                         [files(dataset), scenario, mode, *args, *ga]).fetchone()[0]
    # The exhaustive, validated VP matrices are a sparse model cube. Regional
    # structural zero is allowed only after checking source-covered region/scenario.
    core = read(dataset, 'forecast_core.json')
    if region != 'DE' and region not in core['scenarios'][scenario]['regions']: return None
    return 0.0 if result is None else result


def forecast_regions(con, dataset, *, regions, modes, metrics, direction, goods):
    core = read(dataset, 'forecast_core.json')
    observations = []
    for region in regions:
        if region!='DE' and region not in core['scenarios']['2019_BASE']['regions']: raise ValueError('Unbekannte Prognoseregion')
        for mode in modes:
            for metric in metrics:
                for g in goods:
                    values = [forecast_value(con,dataset,region,s,mode,metric,direction,g) for s in ['2019_BASE','2040_P1']]
                    meta = {'region': region, 'region_name': 'Deutschland' if region=='DE' else core['scenarios']['2019_BASE']['regions'][region]['name'],
                            'mode': mode, 'metric': metric, 'direction': direction, 'group': g,
                            'group_name': label(dataset,g), 'basis': 'VP2019_BASE_to_2040_P1'}
                    unit = 't' if metric == 'tonnes' else 'tkm'
                    prefix = meta['region_name']+' / '+MODES[mode]+' / '+DIRECTIONS[direction]+' / '+meta['group_name']+' / '
                    for s, year, value in zip(['2019_BASE','2040_P1'],[2019,2040],values):
                        observations.append({**meta,'label':prefix+s,'value':value,'scenario':s,'year':year,'unit':unit,'value_status':'forecast'})
                    delta = values[1]-values[0] if all(v is not None for v in values) else None
                    observations.append({**meta,'label':prefix+'absolute Änderung','value':delta,'unit':unit,'value_status':'calculated','formula':'VP2040_P1 - VP2019_BASE'})
                    pct = delta/values[0]*100 if delta is not None and values[0]>0 else None
                    observations.append({**meta,'label':prefix+'relative Änderung','value':pct,'unit':'%','value_status':'calculated' if pct is not None else 'not_computable' if values[0]==0 else 'missing_value',
                                         'denominator':values[0],'formula':'(VP2040_P1 - VP2019_BASE) / VP2019_BASE * 100'})
    return {'status':'available' if all(x['value'] is not None or x['value_status']=='not_computable' for x in observations) else 'partial',
            'observations':observations,'counting':'VP: Versand/Empfang ohne Binnen; Gesamtaufkommen zählt Binnen einmal.',
            'note':'Vollständige Originalmatrizen mit Verkehrsträger- und Güterauswahl. Prognosebasis 2019 und Szenario 2040 P1, keine beobachtete Entwicklung. VP25 und C7 sind überlappende Gliederungen und werden nicht addiert. Nationale Werte einschließlich Transit; regionale Werte mit deutscher Quelle oder Ziel.'}


def forecast_relation(con,dataset,*,origin,destination,modes,metrics,goods):
    observations=[]
    for mode in modes:
        for metric in metrics:
            for g in goods:
                extra, ga=goods_filter(g)
                rows=con.execute(f'SELECT scenario,sum({metric}) FROM read_parquet(?) WHERE origin=? AND destination=? AND mode=?{extra} GROUP BY scenario',
                                 [files(dataset),origin,destination,mode,*ga]).fetchall()
                vals=dict(rows)
                meta={'origin':origin,'destination':destination,'mode':mode,'metric':metric,'group':g,'group_name':label(dataset,g),'basis':'VP2019_BASE_to_2040_P1','direction':'outbound'}
                unit='t' if metric=='tonnes' else 'tkm'
                prefix=origin+' → '+destination+' / '+MODES[mode]+' / '+label(dataset,g)+' / '
                for s,y in [('2019_BASE',2019),('2040_P1',2040)]:
                    observations.append({**meta,'label':prefix+s,'scenario':s,'year':y,'value':vals.get(s),'unit':unit,'value_status':'forecast' if s in vals else 'missing_row'})
                b,t=vals.get('2019_BASE'),vals.get('2040_P1')
                delta=t-b if b is not None and t is not None else None
                observations.append({**meta,'label':prefix+'absolute Änderung','value':delta,'unit':unit,'value_status':'calculated' if delta is not None else 'missing_value'})
                observations.append({**meta,'label':prefix+'relative Änderung','value':delta/b*100 if delta is not None and b>0 else None,'unit':'%',
                                     'denominator':b,'value_status':'not_computable' if b==0 else 'calculated' if delta is not None else 'missing_value'})
    return {'status':'available' if all(x['value'] is not None or x['value_status']=='not_computable' for x in observations) else 'partial',
            'observations':observations,'note':'Gerichtete Prognoserelation aus vollständigen VP-Matrizen, keine Toplistenbegrenzung. Fehlende Relationszeile bleibt unbekannt, nicht null. Basis 2019 zu Prognose 2040 P1.'}


def dashboard_detail(con,dataset,*,product,entity,year,mode,metric,direction,classification,group,partner,top):
    observations=[]
    unit={'tonnes':'t','tkm':'tkm','teu':'TEU','load_units':'Ladeeinheiten','trips':'Fahrten'}[metric]
    note='Veröffentlichter Dashboardbestand; keine Ursachen-, Kapazitäts- oder Transportkettenaussagen.'
    def add(text,value,**meta):
        observations.append({'label':text,'value':value,'unit':unit,'year':year,'mode':mode,'direction':direction,**meta})
    taxonomy=read(dataset,'taxonomy.json')
    groups=taxonomy['groups_7' if classification=='C7' else 'divisions_20']
    def selected(data):
        keys=sorted(groups,key=lambda x:int(x)) if group=='ALL' else [group]
        if any(k not in groups for k in keys): raise ValueError('Gütercode passt nicht zur Gliederung')
        return keys
    if product=='regional_goods':
        if mode not in {'rail','iww'} or metric not in {'tonnes','tkm'} or classification!='NST20':
            return {'status':'not_available','observations':[],'note':'Regionale NST20-Dashboarddetails liegen für Schiene/Binnenschiff in t/tkm vor. C7 über goods_structure; Straße NUTS-3 nur C7, NST20 auf NUTS-2 über road_details.'}
        if entity=='DE':
            if direction!='all': return {'status':'not_available','observations':[],'note':'Nationale NST20-Dashboardaggregation nur all; keine vollständige nationale Güterrandsumme.'}
            data={}
            for code,ys in read(dataset,'regional.json').items():
                if len(code)!=5: continue
                for g,v in ys.get(str(year),{}).get('by_mode_divisions' if metric=='tonnes' else 'by_mode_divisions_tkm',{}).get(mode,{}).get('all',{}).items():
                    if v is not None: data[g]=data.get(g,0)+v/2
            for g in selected(data): add('Deutschland / '+MODES[mode]+' / NST20 Dashboardaggregation / '+groups[g]['name'],data.get(g),group=g)
            return {'status':'available' if observations and all(r['value'] is not None for r in observations) else 'partial','observations':observations,
                    'note':'Nationale Dashboard-Güterstruktur: Summe regionaler all-Profile geteilt durch zwei, wie im Dashboard. Keine amtliche vollständige nationale Randsumme; reiner Auslandstransit fehlt und Auslandsverkehre sind nicht vollständig repräsentiert. Nicht mit nationalen Gesamtmengen einschließlich Transit gleichsetzen.'}
        profile=read(dataset,'regional.json').get(entity,{}).get(str(year))
        if profile is None: return {'status':'missing_year','observations':[],'note':'Region oder Jahrgang im Profil nicht verfügbar.'}
        data=profile.get('by_mode_divisions' if metric=='tonnes' else 'by_mode_divisions_tkm',{}).get(mode,{}).get(direction,{})
        for g in selected(data): add(entity+' / '+MODES[mode]+' / '+DIRECTIONS[direction]+' / '+groups[g]['name'],data.get(g),group=g,region=entity)
        note='Regionale NST20-Gliederung aus dem Dashboard, kein Güterdetail einer einzelnen Relation. Fehlende Gruppen bleiben unbekannt. all zählt Versand plus Empfang wie das Ist-Profil; Binnenverkehr damit doppelt.'
    elif product in {'sea_goods','sea_partners'}:
        if mode!='sea' or metric not in {'tonnes','teu'}: return {'status':'not_available','observations':[],'note':'Seeverkehrsdetails: Tonnen oder TEU, Verkehrsträger sea.'}
        sea=read(dataset,'sea.json')
        p=sea.get('national',{}).get(str(year)) if entity=='DE' else sea.get('seaports',{}).get(str(year),{}).get(entity)
        if not p: return {'status':'missing_year','observations':[],'note':'Hafen oder Jahrgang nicht verfügbar.'}
        field=metric if direction=='all' else direction if metric=='tonnes' else direction+'_teu'
        if product=='sea_goods':
            data=p.get('by_group' if classification=='C7' else 'by_division',{})
            for g in selected(data): add(p['name']+' / '+DIRECTIONS[direction]+' / '+groups[g]['name'],data.get(g,{}).get(field),group=g)
        else:
            if metric!='tonnes' or classification!='C7': return {'status':'not_available','observations':[],'note':'Hafenpartner-Güterauswahl im Dashboard: C7 und Tonnen; keine NST20/TEU-Partnerdetails.'}
            key='groups_7' if direction=='all' else 'groups_7_'+direction
            records=[r for r in p.get('partner_countries',[]) if partner is None or r['iso']==partner]
            value_key='tonnes' if direction=='all' else direction+'_tonnes'
            records=[(r, r.get(value_key) if group=='ALL' else r.get(key,{}).get(group)) for r in records]
            records.sort(key=lambda pair:-(pair[1] if pair[1] is not None else -1))
            for r,v in records[:top]: add(p['name']+' / '+r['name']+' / '+DIRECTIONS[direction],v,partner_id=r['iso'],group=group)
            note='Vorhandene veröffentlichte Dashboard-Partnerauswahl; keine vollständige Rangliste aller Originalpartner. Fehlende Einträge beweisen keinen Nullverkehr.'
    elif product=='kv_structure':
        if entity!='DE' or mode not in {'rail','iww'} or metric not in {'tonnes','tkm'} or direction!='all' or group!='ALL':
            return {'status':'not_available','observations':[],'note':'Ladeeinheiten-/Containergrößenstruktur nur national, alle Richtungen und Güter, t/tkm, getrennt nach Schiene/Binnenschiff.'}
        p=read(dataset,'intermodal.json').get('data_by_year',{}).get(str(year),{}).get(mode,{})
        structure=p.get('load_unit_structure' if mode=='rail' else 'container_size_structure',{})
        names={'containers_and_swap_bodies':'Container und Wechselbehälter','unaccompanied_semitrailers':'Unbegleitete Sattelanhänger','accompanied_road_vehicles':'Begleitete Straßenfahrzeuge','other_identified_load_units':'Weitere Ladeeinheiten','c20':'20-Fuß-Container','c40':'40-Fuß-Container','other_sizes':'Weitere Containergrößen'}
        for k,v in structure.items(): add(MODES[mode]+' / '+names[k],v.get(metric))
        note='Nationale Struktur des getrennten intermodalen Teilmarkts. Schiene und Binnenschiff nicht addieren; nationale Werte einschließlich Transit.'
    elif product=='kv_relations':
        if mode not in {'rail','iww'} or group!='ALL': return {'status':'not_available','observations':[],'note':'KV-Relationsbestand getrennt nach Schiene/Binnenschiff, ohne Güterfilter.'}
        data=read(dataset,'intermodal.json')
        records=data.get('relations_by_year',{}).get(str(year),{}).get(mode,[])
        picked=[]
        for r in records:
            involved = (r['origin_id']==entity if direction=='outbound' else r['destination_id']==entity if direction=='inbound' else entity in {r['origin_id'],r['destination_id']})
            other=r['destination_id'] if r['origin_id']==entity else r['origin_id']
            if involved and (partner is None or other==partner): picked.append(r)
        picked.sort(key=lambda r:-(r.get(metric) if r.get(metric) is not None else -1))
        for r in picked[:top]: add(r['origin_id']+' → '+r['destination_id']+' / '+MODES[mode],r.get(metric),origin=r['origin_id'],destination=r['destination_id'])
        note=data['relation_scope']+'. Vorhandene Dashboard-Relationsauswahl, keine Vollständigkeitsbehauptung. Fehlende Einträge sind nicht null.'
    elif product=='regional_trips':
        if mode!='road' or metric!='trips' or direction!='all' or group!='ALL': return {'status':'not_available','observations':[],'note':'Regionalprofil-Fahrten nur Straße, all, ohne Güterfilter.'}
        p=read(dataset,'regional.json').get(entity,{}).get(str(year),{})
        add(entity+' / Straßenfahrten im Regionalprofil',p.get('total_trips'),region=entity)
        note='Straßenfahrten aus dem veröffentlichten Regionalprofil; keine Richtung oder Güteraufteilung, kein Nachweis eindeutiger Fahrzeugzahlen.'
    elif product=='forecast_kv':
        if year not in {2019,2040} or mode not in MODES or metric not in {'tonnes','teu','load_units'} or group!='ALL':
            return {'status':'not_available','observations':[],'note':'VP-KV: 2019 oder 2040, Landverkehrsträger, alle Güter, t/TEU/Ladeeinheiten.'}
        scenario='2019_BASE' if year==2019 else '2040_P1'
        add(entity+' / '+MODES[mode]+' / VP KV / '+DIRECTIONS[direction],forecast_value(con,dataset,entity,scenario,mode,'kv_'+metric,direction),basis='VP2019_BASE_to_2040_P1',scenario=scenario,value_status='forecast',region=entity)
        note='Modellierter KV nach VerkArt=2 aus vollständigen Originalmatrizen. Keine Auslastungs- oder Verlagerungspotenziale; Binnen bei all einmal.'
    elif product=='forecast_container_types':
        if year not in {2019,2040} or mode not in MODES or metric!='tonnes' or direction!='all' or group!='ALL':
            return {'status':'not_available','observations':[],'note':'VP-Behältertypen: 2019/2040, Landverkehrsträger, alle Güter, all, Tonnen.'}
        scenario='2019_BASE' if year==2019 else '2040_P1'
        if entity!='DE' and entity not in read(dataset,'forecast_core.json')['scenarios'][scenario]['regions']:
            return {'status':'not_available','observations':[],'note':'Unbekannte Prognoseregion.'}
        predicate='true' if entity=='DE' else '(origin=? OR destination=?)'
        args=[] if entity=='DE' else [entity,entity]
        rows=con.execute('SELECT beh,sum(tonnes) FROM read_parquet(?) WHERE scenario=? AND mode=? AND '+predicate+' GROUP BY beh ORDER BY beh',
                         [files(dataset),scenario,mode,*args]).fetchall()
        for b,v in rows: add(entity+' / '+MODES[mode]+' / VP Behältertyp '+b,v,scenario=scenario,basis='VP2019_BASE_to_2040_P1',value_status='forecast')
        note='Behältertypen nach Originalcode BehTyp der VP-Matrizen, nicht ausschließlich KV. Gesamtaufkommen zählt Binnen einmal; nationale Werte einschließlich Transit.'
    elif product=='forecast_load_units':
        if year not in {2019,2040} or mode not in MODES or metric not in {'teu','load_units'} or group!='ALL': return {'status':'not_available','observations':[],'note':'VP-Ladeeinheiten: 2019/2040, Landverkehrsträger, alle Güter, TEU/Ladeeinheiten.'}
        scenario='2019_BASE' if year==2019 else '2040_P1'
        add(entity+' / '+MODES[mode]+' / VP / '+DIRECTIONS[direction],forecast_value(con,dataset,entity,scenario,mode,metric,direction),basis='VP2019_BASE_to_2040_P1',scenario=scenario,value_status='forecast',region=entity)
        note='Ladeeinheiten/TEU laut VP-Matrix ohne zusätzlichen VerkArt-Filter. Die Datensatzbeschreibung definiert sie als KV-Aufkommen; forecast_kv setzt VerkArt=2 ausdrücklich. Binnen bei all einmal.'
    else: raise ValueError('Unbekanntes Dashboardprodukt')
    return {'status':'available' if observations and all(r['value'] is not None for r in observations) else 'partial', 'observations':observations,'note':note}


def validate_package(dataset):
    import duckdb
    core=read(dataset,'forecast_core.json')
    failures=[]
    checked=0
    with duckdb.connect(config={'threads':2,'memory_limit':'512MB'}) as con:
        # A complete grouped cube is independently reconciled with every source-covered
        # region, both scenarios, modes, directions, metrics and C7 (including zeros).
        rows=con.execute('''WITH movement AS (
            SELECT scenario,mode,origin region,vp,c7,'outbound' direction,tonnes,tkm FROM read_parquet(?) WHERE origin<>destination
            UNION ALL SELECT scenario,mode,destination,vp,c7,'inbound',tonnes,tkm FROM read_parquet(?) WHERE origin<>destination
            UNION ALL SELECT scenario,mode,origin,vp,c7,'binnen',tonnes,tkm FROM read_parquet(?) WHERE origin=destination)
            SELECT scenario,mode,region,c7,direction,sum(tonnes),sum(tkm) FROM movement GROUP BY ALL''', [files(dataset)]*3).fetchall()
        cube={(s,m,r,g,d):(t,k) for s,m,r,g,d,t,k in rows}
        for s,sc in core['scenarios'].items():
            for r,p in sc['regions'].items():
                for m in MODES:
                    for g in '1234567':
                        for direction in ['outbound','inbound','binnen','all']:
                            actual=tuple(sum(cube.get((s,m,r,g,d),(0,0))[i] for d in (['outbound','inbound','binnen'] if direction=='all' else [direction])) for i in [0,1])
                            for metric,value in zip(['tonnes','tkm'],actual):
                                expected=p['modes_by_group_'+metric][g][m][direction]
                                checked+=1
                                if not math.isclose(value,expected,abs_tol=.051,rel_tol=1e-12): failures.append([s,r,m,g,direction,metric,value,expected])
        for s,sc in core['scenarios'].items():
            for m in MODES:
                sums=con.execute('SELECT sum(tonnes),sum(tkm) FROM read_parquet(?)',[str(Path(dataset)/(s+'_'+m+'.parquet'))]).fetchone()
                for metric,value in zip(['tonnes','tkm'],sums):
                    checked+=1
                    expected=sc['national']['modes'][m][metric]
                    if not math.isclose(value,expected,abs_tol=.051,rel_tol=1e-12): failures.append([s,'DE',m,metric,value,expected])
        vp_rows=con.execute('''WITH movement AS (
            SELECT scenario,origin region,vp,'outbound' direction,tonnes,tkm FROM read_parquet(?) WHERE origin<>destination
            UNION ALL SELECT scenario,destination,vp,'inbound',tonnes,tkm FROM read_parquet(?) WHERE origin<>destination
            UNION ALL SELECT scenario,origin,vp,'binnen',tonnes,tkm FROM read_parquet(?) WHERE origin=destination)
            SELECT scenario,region,vp,direction,sum(tonnes),sum(tkm) FROM movement GROUP BY ALL''',[files(dataset)]*3).fetchall()
        vp_cube={(s,r,g,d):(t,k) for s,r,g,d,t,k in vp_rows}
        for s,sc in core['scenarios'].items():
            for r,p in sc['regions'].items():
                for g in VP_CODES:
                    for direction in ['outbound','inbound','all']:
                        actual=tuple(sum(vp_cube.get((s,r,g,d),(0,0))[i] for d in (['outbound','inbound','binnen'] if direction=='all' else [direction])) for i in [0,1])
                        for metric,value in zip(['tonnes','tkm'],actual):
                            expected=p['vp2040_groups_'+metric][direction][g]
                            checked+=1
                            if not math.isclose(value,expected,abs_tol=.051,rel_tol=1e-12): failures.append([s,r,'VP'+g,direction,metric,value,expected])
        berlin=[forecast_value(con,dataset,'DE300',s,'rail','tonnes','outbound','VP100') for s in ['2019_BASE','2040_P1']]
        if berlin!=[277,1531]: failures.append(['Berlin metal',berlin])
    return {'passed':not failures,'checked_cells':checked,'berlin_rail_metals':berlin,'failures':failures[:30], 'failure_count':len(failures), 'external_model_calls':0}
