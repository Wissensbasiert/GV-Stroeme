"""Lokale B04–B06-Abfragen; keine Modell- oder Portalverbindung."""
import json
import math
from pathlib import Path
from scripts.analysis.b01 import ROOT, resolve_dataset

STORE = ROOT / 'data/analysis/b0406'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def rows(cursor):
    return [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]


def rank(records, key='value', top=None, descending=True):
    if top is not None and (type(top) is not int or not 1 <= top <= 1000):
        raise ValueError('Top muss eine ganze Zahl zwischen 1 und 1000 sein')
    valid = [dict(r) for r in records if r.get(key) is not None and math.isfinite(r[key])]
    valid.sort(key=lambda r: ((-1 if descending else 1)*r[key], str(r.get('id', ''))))
    previous, place = None, 0
    for i, item in enumerate(valid, 1):
        if i == 1 or item[key] != previous:
            place = i
        previous = item[key]
        item['rank'] = place
    return [r for r in valid if top is None or r['rank'] <= top]


def change_ranking(records, *, comparable=False, measure='absolute', top=None,
                   minimum_base=None, descending=True):
    if measure not in {'absolute', 'relative'}:
        raise ValueError('Rangmaß muss absolute oder relative sein')
    if minimum_base is not None and (not math.isfinite(minimum_base) or minimum_base < 0):
        raise ValueError('Mindestbasis muss endlich und nicht negativ sein')
    if not comparable:
        return {'status': 'comparability_not_confirmed', 'rows': []}
    result, excluded = [], []
    for row in records:
        a, b = row.get('base'), row.get('target')
        if a is None or b is None or not math.isfinite(a) or not math.isfinite(b):
            excluded.append({'id': row['id'], 'reason': 'missing_value'}); continue
        if minimum_base is not None and a < minimum_base:
            excluded.append({'id': row['id'], 'reason': 'minimum_base'}); continue
        rate = (b-a)/a*100 if a else None
        if measure == 'relative' and rate is None:
            excluded.append({'id': row['id'], 'reason': 'zero_base'}); continue
        result.append({**row, 'absolute_change': b-a, 'relative_change_pct': rate,
                       'value': b-a if measure == 'absolute' else rate})
    return {'status': 'available', 'rows': rank(result, top=top, descending=descending),
            'excluded': excluded, 'minimum_base': minimum_base, 'measure': measure}


def context(dataset, function, **parameters):
    dataset = Path(dataset)
    m = read(dataset/'manifest.json')
    return {'snapshot_id': m['snapshot_id'], 'function': function, 'parameters': parameters,
            'scope': 'Veröffentlichte Quellenwerte; keine Aussage über nicht erfasste Verkehre',
            'comparability': 'not_confirmed', 'revision_status': 'not_documented',
            'source_registry':'manifest.json / source_contracts.json',
            'territory_note':'B02-Grenzen gelten fort: SGV 2016–2023 Dateikopf NUTS2024 widerspricht Beschreibung; ältere Jahresvergleiche nicht harmonisiert.'}


def direction_balance(con,dataset,*,region,year,mode='road',metric='tonnes'):
    regions_checked(dataset,[region],year)
    if mode not in {'road','rail','iww'} or metric not in {'tonnes','tkm'}:
        raise ValueError('Ungültige Richtungsauswahl')
    data=rows(con.execute('SELECT profile FROM read_parquet(?) WHERE id=? AND year=?',
                         [str(Path(dataset)/'regional_profiles.parquet'),region,year]))
    p=json.loads(data[0]['profile']) if data else {}
    directions=p.get('modes_direction_'+metric,{}).get(mode,{})
    a,z=directions.get('outbound'),directions.get('inbound')
    return {**context(dataset,'direction_balance',region=region,year=year,mode=mode,metric=metric),
            'outbound':a,'inbound':z,'balance':a-z if a is not None and z is not None else None,
            'status':'available' if a is not None and z is not None else 'missing_value',
            'unit':'t' if metric=='tonnes' else 'tkm',
            'counting':'Versand minus Empfang; Binnen in beiden Richtungen enthalten, im Saldo aufgehoben.',
            'empty_trips':None,'local_transit':None,
            'note':'Bestehende D01-Profilwerte; daraus keine Leerfahrten oder örtlichen Durchfahrten ableiten.'}


def regions_checked(dataset, regions, year=2024):
    if not isinstance(regions, list) or not regions or any(not isinstance(r, str) for r in regions):
        raise ValueError('Liste bestätigter ganzer NUTS-3-Gebiete erforderlich')
    if len(set(regions)) != len(regions):
        raise ValueError('Doppelte Gebiete sind nicht zulässig')
    version = '2024' if year >= 2024 else '2021' if year >= 2021 else '2016'
    registry = read(Path(dataset)/'regions.json')[version]
    if any(r not in registry for r in regions):
        raise ValueError('Unbekanntes Gebiet oder andere Raumebene; keine Kreisanteile/Knoten')
    return registry


def compare_regions(con, dataset, *, regions, year, metric='tonnes', direction='all'):
    registry = regions_checked(dataset, regions, year)
    if len(regions) < 2 or metric not in {'tonnes','tkm'} or direction not in {'all','outbound','inbound'}:
        raise ValueError('Mindestens zwei Gebiete und gültige Kennzahl/Richtung erforderlich')
    data = rows(con.execute('SELECT * FROM read_parquet(?) WHERE year=? AND id IN (SELECT unnest(?))',
                           [str(Path(dataset)/'regional_profiles.parquet'), year, regions]))
    by_id = {r['id']: read_json_record(r['profile']) for r in data}
    result = []
    for region in regions:
        p = by_id.get(region, {})
        modes = p.get('modes_'+metric, {}) if direction == 'all' else {
            k: v.get(direction) for k,v in p.get('modes_direction_'+metric, {}).items()}
        value = p.get('total_'+metric) if direction == 'all' else p.get('directions_'+metric,{}).get(direction)
        result.append({'id':region,'name':registry[region],'value':value,'modes':modes,
                       'groups':p.get('groups_7_'+metric,{}).get(direction,{}),
                       'status':'available_in_existing_profile' if p else 'missing_year'})
    return {**context(dataset,'compare_regions',regions=regions,year=year,metric=metric,direction=direction),
            'status':'available' if all(r['value'] is not None for r in result) else 'partial',
            'unit':'t' if metric=='tonnes' else 'tkm', 'rows':result,
            'counting':'Versand plus Empfang zählt Binnenverkehr zweimal; keine Verbundsumme.',
            'quality_note':'Bestehendes D01-Profil; dortige Nullen sind kein neuer Rohquellen-Nullnachweis. Quellenkennzeichen für VE12/13 hier nicht nacherschlossen.'}


def read_json_record(value):
    return json.loads(value)


def aggregate_union(con, annual_path, *, regions, year, mode, metric='tonnes', group='ALL'):
    if mode not in {'road','rail','iww'} or metric not in {'tonnes','tkm'} or group not in {'ALL',*'1234567'}:
        raise ValueError('Ungültiger Verkehrsträger, Kennzahl oder Gütergruppe')
    if mode == 'road' and group != 'ALL':
        raise ValueError('Keine Güteraufteilung für Straßenrelationen')
    query = '''WITH selected AS (SELECT *,origin_id IN (SELECT unnest(?)) AS inside_o,
        dest_id IN (SELECT unnest(?)) AS inside_d FROM read_parquet(?)
        WHERE year_ref=? AND mode=? AND metric=?'''
    args = [regions,regions,str(annual_path),year,mode,metric]
    if group != 'ALL':
        query += ' AND group_7_id=?'; args.append(group)
    query += ''') SELECT CASE WHEN inside_o AND inside_d THEN 'internal'
        WHEN inside_o THEN 'external_outbound' ELSE 'external_inbound' END AS category,
        sum(source_rows) AS source_rows,sum(known_sum) AS known_sum,
        sum(missing_count) AS missing_count,sum(restricted_count) AS restricted_count,
        sum(unknown_quality_count) AS unknown_quality_count,list(DISTINCT source_id) AS source_ids
        FROM selected WHERE inside_o OR inside_d GROUP BY 1'''
    data = rows(con.execute(query,args)); parts = {r['category']:r for r in data}
    for key in ['internal','external_outbound','external_inbound']:
        r = parts.setdefault(key, {'category':key,'source_rows':0,'known_sum':None,'missing_count':0,
                                  'restricted_count':0,'unknown_quality_count':0,'source_ids':[]})
        r['value'] = r['known_sum'] if r['source_rows'] and not r['missing_count'] else None
        r['status'] = 'missing_row' if not r['source_rows'] else 'partial' if r['missing_count'] else 'available'
    known = [r['known_sum'] for r in data if r['known_sum'] is not None]
    complete = bool(data) and not any(r['missing_count'] for r in data)
    unique = sum(known) if known else None
    # Summation over observed rows is valid even if an entire category has no published rows.
    internal = parts['internal']['known_sum']
    return {'parts':parts,'known_sum':unique,'unique_value':unique if complete else None,
            'touch_value':unique+(internal or 0) if complete else None,
            'status':'available' if complete else 'partial' if data else 'missing_row',
            'local_transit':None,'counting':'Eindeutig: Innen + Außenversand + Außenempfang, jede belegte OD einmal. Berührungen: Innen zweimal.',
            'note':'Fehlende Kategorien sind kein Nullnachweis. Werte beziehen sich nur auf vorhandene veröffentlichte Zeilen; örtlicher Transit aus OD nicht bestimmbar.'}


def query_union(con,dataset,*,regions,year,mode,metric='tonnes',group='ALL'):
    regions_checked(dataset,regions,year)
    m = read(Path(dataset)/'manifest.json')
    annual = ROOT/m['dependencies']['b01']['path']/'annual_od.parquet'
    return {**context(dataset,'region_union',regions=regions,year=year,mode=mode,metric=metric,group=group),
            'unit':'t' if metric=='tonnes' else 'tkm',
            **aggregate_union(con,annual,regions=regions,year=year,mode=mode,metric=metric,group=group)}


def forecast_ranking(con,dataset,*,modes=None,metric='tonnes',direction='all',measure='absolute',top=5,descending=True):
    # Direkte historische Prüfaufrufe bleiben bei Schiene; der Chat setzt seinen
    # fachlichen Standard für uneingeschränkte Fragen ausdrücklich auf alle drei Modi.
    modes = ['rail'] if modes is None else modes
    if (not isinstance(modes,list) or not modes or len(modes)>3 or len(set(modes))!=len(modes)
            or any(mode not in {'road','rail','iww'} for mode in modes)
            or metric not in {'tonnes','tkm'} or direction not in {'all','outbound','inbound','binnen'}):
        raise ValueError('Ungültige Prognoseauswahl')
    selected_count=len(modes)
    data = rows(con.execute('''SELECT id,any_value(name) AS name,
        CASE WHEN count(*)=? AND count(base)=? THEN sum(base) END AS base,
        CASE WHEN count(*)=? AND count(target)=? THEN sum(target) END AS target
        FROM read_parquet(?) WHERE mode IN (SELECT unnest(?)) AND metric=? AND direction=?
        GROUP BY id''',[selected_count,selected_count,selected_count,selected_count,
            str(Path(dataset)/'forecast.parquet'),modes,metric,direction]))
    labels={'road':'Straße','rail':'Schiene','iww':'Binnenschiff'}
    selection_label=('alle drei Landverkehrsträger' if set(modes)=={'road','rail','iww'} else
        ' und '.join(labels[mode] for mode in modes))
    return {**context(dataset,'forecast_ranking',modes=modes,metric=metric,direction=direction,measure=measure,top=top),
            **change_ranking(data,comparable=True,measure=measure,top=top,descending=descending),
            'descending':descending,
            'population_count':len(data),'comparability':'VP2019_BASE_to_2040_P1_only',
            'modes':modes,'mode_selection_label':selection_label,
            'counting':'Ausgewählte Verkehrsträger werden je Region vollständig addiert; all enthält Binnenverkehr je Verkehrsträger einmal, Versand/Empfang ohne Binnenverkehr.',
            'unit':'t' if metric=='tonnes' else 'tkm','note':'Modellvergleich 2019/2040, keine Ist-Zeitreihe oder zusätzliche Szenariorechnung.'}


def national(con,dataset,*,year,metric='tkm',mode=None):
    if metric not in {'tonnes','tkm'} or mode not in {None,'road','rail','iww'}:
        raise ValueError('Ungültige nationale Auswahl')
    data = rows(con.execute('SELECT * FROM read_parquet(?) WHERE year=? AND metric=? ORDER BY mode,relationship',
                           [str(Path(dataset)/'national.parquet'),year,metric]))
    totals=[]
    for item in ['road','rail','iww']:
        subset=[r for r in data if r['mode']==item]
        known=[r['known_sum'] for r in subset if r['known_sum'] is not None]
        val=sum(known) if known else None
        complete=bool(subset) and not any(r['missing_count'] for r in subset)
        totals.append({'mode':item,'value':val if complete else None,'known_sum':val,
                       'status':'available' if complete else 'partial' if subset else 'missing_year',
                       'restricted_count':sum(r['restricted_count'] for r in subset)})
    full=all(r['value'] is not None for r in totals)
    denominator=sum(r['value'] for r in totals) if full else None
    for r in totals:
        r['share_pct']=r['value']/denominator*100 if denominator and r['value'] is not None else None
    if mode:
        modal=next(r for r in totals if r['mode']==mode)
        data=[r for r in data if r['mode']==mode]
        for r in data:
            r['share_pct']=r['value']/modal['value']*100 if modal['value'] and r['value'] is not None else None
    return {**context(dataset,'national',year=year,metric=metric,mode=mode),
            'status':modal['status'] if mode else ('missing_year' if not data else 'available' if full else 'partial'),
            'unit':'t' if metric=='tonnes' else 'tkm','denominator':denominator,'modes':totals,'relationships':data,
            'counting':'Nationale Quellzeilen einmal einschließlich unzugeordneter Räume. Straße: europäische Lkw, tkm ausschließlich Inlands_tkm.',
            'note':'Keine Ableitung örtlichen Transits oder von Leerfahrten. Relationsanteile beziehen sich auf den jeweiligen Verkehrsträger.'}


def node_partners(con,dataset,*,kind,node,year,direction='outbound',metric='tonnes',international=False,top=10):
    if kind not in {'air','sea'} or direction not in {'all','outbound','inbound'}:
        raise ValueError('Knotentyp oder Richtung ungültig')
    if metric not in ({'tonnes','flights'} if kind=='air' else {'tonnes','teu'}):
        raise ValueError('Kennzahl passt nicht zum Knoten')
    base=context(dataset,'node_partners',kind=kind,node=node,year=year,direction=direction,metric=metric,international=international,top=top)
    if not node:
        return {**base,'status':'needs_clarification','note':'Bitte konkreten Flughafen oder Seehafen auswählen.'}
    where='node=? AND year=? AND metric=?'; args=[node,year,metric]
    if kind=='air' or direction!='all':
        where+=' AND direction=?';args.append(direction)
    if international:
        where+=" AND partner_country IS NOT NULL AND partner_country<>'' AND partner_country<>'DE'"
    applicability='sum(not_applicable_count)' if kind=='sea' else '0'
    data=rows(con.execute('SELECT '+applicability+''' AS not_applicable_count,
        partner AS id,partner_country,sum(known_sum) AS known_sum,
        sum(missing_count) AS missing_count,sum(source_rows) AS source_rows,
        sum(restricted_count) AS restricted_count,list(DISTINCT source_id) AS source_ids
        FROM read_parquet(?) WHERE '''+where+' GROUP BY partner,partner_country',
        [str(Path(dataset)/(kind+'_partners.parquet')),*args]))
    for r in data:
        r['value']=r['known_sum'] if not r['missing_count'] else None
    positive=[r for r in data if r['value'] is not None and r['value']>0]
    denominator=sum(r['value'] for r in positive) if positive else None
    # For air, publication thresholds permit only a denominator over published numeric relations.
    # For sea, unknown metric cells prevent a complete denominator.
    if kind=='sea' and any(r['missing_count'] for r in data):
        denominator=None
    for r in positive:
        r['share_pct']=r['value']/denominator*100 if denominator else None
    unknown=sum(r['missing_count']>0 for r in data)
    not_applicable=sum(r['known_sum'] is None and not r['missing_count'] and r['not_applicable_count']>0 for r in data)
    return {**base,'status':'missing_row' if not data else 'partial' if unknown else 'not_applicable' if not_applicable==len(data) else 'available',
            'unit':{'tonnes':'t','teu':'TEU','flights':'Flüge'}[metric],
            'denominator':denominator,'positive_relations':len(positive),
            'unknown_relations':unknown,'not_applicable_relations':not_applicable,
            'not_applicable_count':sum(r['not_applicable_count'] for r in data),'rows':rank(positive,top=top),
            'denominator_scope':'Summe aller veröffentlichten positiven numerischen Partnerrelationen der Auswahl, vor Top-Begrenzung',
            'note':'Veröffentlichungsschwellen bei Luftfracht: kein gesamtes Flughafenaufkommen. Seehäfen: all zählt Ein- und Ausladung; TEU nur bei Containertransporten. Nicht anwendbare TEU-Leerfelder sind separat gezählt, fehlende anwendbare Werte bleiben unbekannt.'}


def airport_flights_blocked(dataset, year):
    """Retain the 2025 safeguard for old or unreviewed immutable snapshots."""
    if year != 2025:
        return False
    approval = read(ROOT/'config/analyseassistent/LUFTVERKEHR_FREIGABE.json')
    actual = read(Path(dataset)/'manifest.json').get('input_sha256', {})
    return any(actual.get(source) != expected for source, expected in
               approval['airport_flights_2025']['source_sha256'].items())


def node_statistics(con,dataset,*,kind,node,year,direction='all',metric='tonnes'):
    if kind not in {'air','sea'} or direction not in {'all','outbound','inbound'} or metric not in ({'tonnes','flights'} if kind=='air' else {'tonnes','teu'}):
        raise ValueError('Ungültige Knotenauswahl')
    result=context(dataset,'node_statistics',kind=kind,node=node,year=year,direction=direction,metric=metric)
    if not node:
        return {**result,'status':'needs_clarification','value':None}
    if kind=='air':
        if metric=='flights' and airport_flights_blocked(dataset, year):
            return {**result,'status':'not_available','value':None,'note':'Flughafen-Flugzahlen 2025 wegen dokumentiertem Quellenwiderspruch gesperrt.'}
        data=rows(con.execute('SELECT * FROM read_parquet(?) WHERE node=? AND year=? AND direction=? AND metric=?',
            [str(Path(dataset)/'air_statistics.parquet'),node,year,direction,metric]))
    else:
        clause='' if direction=='all' else ' AND direction=?'
        data=rows(con.execute('''SELECT sum(known_sum) AS known_sum,sum(missing_count) AS missing_count,
            sum(not_applicable_count) AS not_applicable_count,
            sum(restricted_count) AS restricted_count,list(DISTINCT source_id) AS source_ids,
            sum(source_rows) AS source_rows FROM read_parquet(?) WHERE node=? AND year=? AND metric=?'''+clause,
            [str(Path(dataset)/'sea_partners.parquet'),node,year,metric,*([direction] if clause else [])]))
        data=[r for r in data if r['source_rows']]
    if not data:
        return {**result,'status':'missing_row','value':None}
    if len(data)!=1:
        raise ValueError('Mehrdeutiger Knotenwert')
    r=data[0]
    return {**result,**r,'value':r['known_sum'] if not r['missing_count'] else None,
            'unit':{'tonnes':'t','teu':'TEU','flights':'Flüge'}[metric],
            'status':'partial' if r['missing_count'] else 'available' if r['known_sum'] is not None else 'not_applicable',
            'counting':'See: Ein- plus Ausladung bei all, TEU nur bei Containertransporten. Luft: publizierte Flughafen-Randsumme aus AVIA_GOOA.'}
