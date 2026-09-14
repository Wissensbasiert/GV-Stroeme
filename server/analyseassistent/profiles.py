"""Zusammengesetzte Profile ausschließlich aus dem geprüften B04–B06-Bestand."""
import json
import math
from pathlib import Path
from scripts.analysis.b0406 import regions_checked, rows, compare_regions as original_compare_regions

MODES = {'road': 'Straße', 'rail': 'Schiene', 'iww': 'Binnenschiff'}
DIRECTIONS = {'all': 'Versand plus Empfang', 'outbound': 'Versand', 'inbound': 'Empfang'}


def complete_sum(values):
    if not values or any(type(v) not in {int, float} or not math.isfinite(v) or v < 0 for v in values):
        return None
    return math.fsum(values)


def read_profile(con, dataset, region, year):
    names = regions_checked(dataset, [region], year)
    data = con.execute('SELECT profile FROM read_parquet(?) WHERE id=? AND year=?',
                       [str(Path(dataset)/'regional_profiles.parquet'), region, year]).fetchall()
    if len(data) > 1:
        raise ValueError('Regionalprofil ist mehrdeutig')
    profile=json.loads(data[0][0]) if data else None
    if profile is not None:
        coverage=json.loads((Path(dataset)/'source_coverage.json').read_text(encoding='utf-8'))
        unavailable=[mode for mode in MODES if not any(r['mode']==mode and r['year']==year for r in coverage)]
        # D01 can carry a display zero for a source year that does not exist.
        # Never expose it as observed freight or a valid modal denominator.
        for metric in ['tonnes','tkm']:
            for mode in unavailable:
                profile.setdefault('modes_'+metric,{})[mode]=None
                profile.setdefault('modes_direction_'+metric,{})[mode]={d:None for d in ['outbound','inbound']}
            if unavailable:
                profile['total_'+metric]=None
                profile['directions_'+metric]={d:None for d in ['outbound','inbound']}
                profile['groups_7_'+metric]={d:{g:None for g in '1234567'} for d in DIRECTIONS}
        profile['unavailable_modes']=unavailable
    return names[region], profile


def compare_regions(con,dataset,*,regions,year,metric,direction):
    result=original_compare_regions(con,dataset,regions=regions,year=year,metric=metric,direction=direction)
    for row in result['rows']:
        _,profile=read_profile(con,dataset,row['id'],year)
        if profile is None: continue
        row['value']=profile.get('total_'+metric) if direction=='all' else profile.get('directions_'+metric,{}).get(direction)
        row['modes']=profile.get('modes_'+metric,{}) if direction=='all' else {
            mode:profile.get('modes_direction_'+metric,{}).get(mode,{}).get(direction) for mode in MODES}
        row['groups']=profile.get('groups_7_'+metric,{}).get(direction,{})
        if profile['unavailable_modes']: row['status']='partial'
    if any(r['value'] is None for r in result['rows']): result['status']='partial'
    result['note']='Fehlende Quellenjahre bleiben unbekannt, auch wenn das Dashboardprofil technische Nullen enthält.'
    return result


def common(dataset, region, metric):
    return {'snapshot_id': json.loads((Path(dataset)/'manifest.json').read_text(encoding='utf-8'))['snapshot_id'],
            'region': region, 'metric': metric, 'unit': 't' if metric == 'tonnes' else 'tkm',
            'scope': 'D01: bestehende Regionalprofile aller drei Landverkehrsträger; alle Güter.',
            'counting': 'Ist-Profil: Versand plus Empfang enthält Binnenverkehr zweimal. Keine Verbundsumme.',
            'quality_note': 'D01-Profilgrenzen gelten fort: numerische Nullen sind kein neuer Rohquellen-Nullnachweis; Quellenkennzeichen der regionalen Straßen-Güterrandsummen wurden nicht nacherschlossen.',
            'comparability': 'not_confirmed', 'observations': [], 'status': 'available'}


def regional_history(con,dataset,*,region,start,end,mode,metric,direction):
    if end-start>20:
        raise ValueError('Höchstens 21 veröffentlichte Jahresscheiben auswählen')
    observations=[]
    for year in range(start,end+1):
        name,profile=read_profile(con,dataset,region,year)
        value=None if profile is None else (profile.get('modes_'+metric,{}).get(mode) if direction=='all' else
              profile.get('modes_direction_'+metric,{}).get(mode,{}).get(direction))
        observations.append({'label':name+' / '+str(year),'value':value,'year':year,'mode':mode,
                             'direction':direction,'basis':'observed_profile'})
    return {**common(dataset,region,metric),'observations':observations,
            'status':'available' if all(o['value'] is not None for o in observations) else 'partial',
            'note':'Die prozentuale Veränderung wird aus den veröffentlichten Anfangs- und Endwerten berechnet. Sie ist nicht um Gebiets-, Erfassungs- oder Revisionsbrüche bereinigt. SGV: Konflikt zwischen NUTS-Dateikopf und Beschreibung in älteren Quellen; aus Sprüngen folgt keine belegte Ursache.'}


def modal_history(con,dataset,*,region,years,metric,direction):
    observations=[]
    status='available'
    for year in years:
        _,profile=read_profile(con,dataset,region,year)
        values,state=modal_rows(profile,year=year,direction=direction,metric=metric)
        observations.extend(values)
        if state!='available': status='partial'
    return {**common(dataset,region,metric),'observations':observations,'status':status,
            'note':'Anteile nur bei drei verfügbaren Verkehrsträgern im gleichen Quellenjahr. Fehlende Straßenjahre sind keine Nullwerte. Kein Verlagerungsnachweis aus Anteilen.'}


def modal_rows(profile, *, year, direction, metric):
    if profile is None:
        return [], 'missing_year'
    values = (profile.get('modes_'+metric, {}) if direction == 'all' else
              {mode: profile.get('modes_direction_'+metric, {}).get(mode, {}).get(direction) for mode in MODES})
    denominator = complete_sum([values.get(mode) for mode in MODES])
    total = (profile.get('total_'+metric) if direction == 'all' else profile.get('directions_'+metric, {}).get(direction))
    # Totals in the existing profile are rounded to tenths; only floating-point
    # noise within that precision is tolerated. An absent/conflicting total blocks shares.
    consistent = denominator is not None and total is not None and math.isclose(denominator,total,rel_tol=1e-12,abs_tol=0.051)
    if not consistent:
        denominator = None
    result = []
    for mode, label in MODES.items():
        value = values.get(mode)
        base = {'year': year, 'mode': mode, 'direction': direction, 'basis': 'observed_profile'}
        result.append({**base, 'label': label+' / '+DIRECTIONS[direction]+' '+str(year), 'value': value})
        result.append({**base, 'label': label+' / Anteil '+str(year), 'value': value/denominator*100 if denominator else None,
                       'unit': '%', 'denominator': denominator,
                       'denominator_scope': 'Alle drei Landverkehrsträger im selben D01-Profil, Jahr und Richtungsbezug',
                       'formula': 'mode_value / compatible_modal_sum * 100'})
    return result, 'available' if denominator and consistent else 'partial'


def regional_modal_split(con, dataset, *, region, year, metric, direction):
    name, profile = read_profile(con,dataset,region,year)
    observations, status = modal_rows(profile,year=year,direction=direction,metric=metric)
    return {**common(dataset,region,metric),'name':name,'year':year,'direction':direction,
            'observations':observations,'status':status,
            'note':'Keine Anteile aus Salden oder aus einem unvollständigen Drei-Modi-Nenner.'}


def forecast_rows(con,dataset,region,metric,direction):
    regions_checked(dataset,[region])
    data=rows(con.execute('SELECT mode,base,target FROM read_parquet(?) WHERE id=? AND metric=? AND direction=? ORDER BY mode',
                          [str(Path(dataset)/'forecast.parquet'),region,metric,direction]))
    by_mode={r['mode']:r for r in data}
    if len(by_mode)!=len(data):
        raise ValueError('Prognosewerte sind mehrdeutig')
    result=[]
    for mode,label in MODES.items():
        row=by_mode.get(mode,{})
        base,target=row.get('base'),row.get('target')
        meta={'mode':mode,'direction':direction,'basis':'VP2019_BASE_to_2040_P1',
              'counting':'VP all: Binnen einmal; Versand/Empfang ohne Binnen.'}
        for scenario,value in [('2019_BASE',base),('2040_P1',target)]:
            result.append({**meta,'label':label+' / VP '+scenario,'value':value,'scenario':scenario})
        result.append({**meta,'label':label+' / VP absolute Änderung','value':target-base if base is not None and target is not None else None,
                       'formula':'VP2040_P1 - VP2019_BASE'})
        result.append({**meta,'label':label+' / VP relative Änderung',
                       'value':(target-base)/base*100 if base is not None and base>0 and target is not None else None,
                       'unit':'%','denominator':base,'denominator_scope':'Gleicher Verkehrsträger und Richtungsbezug im VP-Basisfall',
                       'formula':'(VP2040_P1 - VP2019_BASE) / VP2019_BASE * 100'})
    base=complete_sum([by_mode.get(mode,{}).get('base') for mode in MODES])
    target=complete_sum([by_mode.get(mode,{}).get('target') for mode in MODES])
    meta={'direction':direction,'basis':'VP2019_BASE_to_2040_P1',
          'counting':'VP all: Binnen einmal; Versand/Empfang ohne Binnen.'}
    for scenario,value in [('2019_BASE',base),('2040_P1',target)]:
        result.append({**meta,'label':'Alle Landverkehrsträger / VP '+scenario,'value':value,'scenario':scenario})
    result.append({**meta,'label':'Alle Landverkehrsträger / VP relative Änderung',
                   'value':(target-base)/base*100 if base is not None and base>0 and target is not None else None,
                   'unit':'%','denominator':base,'denominator_scope':'Alle drei Landverkehrsträger im gleichen VP-Richtungsbezug',
                   'formula':'(VP2040_P1 - VP2019_BASE) / VP2019_BASE * 100'})
    return result, 'available' if len(data)==3 and all(r['base'] is not None and r['target'] is not None for r in data) else 'partial'


def region_profile(con,dataset,*,region,year,metric,include_forecast):
    name,profile=read_profile(con,dataset,region,year)
    result={**common(dataset,region,metric),'name':name,'year':year,
            'note':'Vollprofil unabhängig von einzelnen Modulfiltern; keine Standortbewertung oder Ursachenbehauptung.'}
    if profile is None:
        return {**result,'status':'missing_year'}
    observations=[]
    outbound=profile.get('directions_'+metric,{}).get('outbound')
    inbound=profile.get('directions_'+metric,{}).get('inbound')
    for label,value in [('Regionalgesamt',profile.get('total_'+metric)),('Versand',outbound),('Empfang',inbound),
                        ('Saldo: Versand minus Empfang',outbound-inbound if outbound is not None and inbound is not None else None)]:
        observations.append({'label':name+' / '+label+' '+str(year),'value':value,'year':year,'basis':'observed_profile'})
    modal,status=modal_rows(profile,year=year,direction='all',metric=metric)
    observations.extend(modal)
    for direction in DIRECTIONS:
        groups=profile.get('groups_7_'+metric,{}).get(direction,{})
        for group in '1234567':
            observations.append({'label':'C'+group+' / '+DIRECTIONS[direction],'value':groups.get(group),
                                 'year':year,'group':group,'direction':direction,'basis':'observed_profile'})
    if include_forecast:
        forecast,forecast_status=forecast_rows(con,dataset,region,metric,'all')
        observations.extend(forecast)
        if forecast_status!='available': status='partial'
        result['note']+=' Prognose 2019_BASE/2040_P1 separat: Binnen bei VP all einmal. Keine Änderungsrate zwischen Ist und Prognose.'
    if any(o['value'] is None for o in observations): status='partial'
    return {**result,'status':status,'observations':observations}


def forecast_regions(con, dataset, *, regions, modes, metrics, direction):
    names = regions_checked(dataset, regions)
    observations = []
    for region in regions:
        for metric in metrics:
            forecast, _ = forecast_rows(con, dataset, region, metric, direction)
            for row in forecast:
                # No all-mode total and no sum across overlapping regional flows.
                if row.get('mode') not in modes:
                    continue
                extra = {'year': 2019 if row['scenario'] == '2019_BASE' else 2040} if row.get('scenario') else {}
                extra['value_status'] = ('forecast' if row.get('scenario') else 'calculated') if row['value'] is not None else (
                    'not_computable' if row.get('unit') == '%' and row.get('denominator') == 0 else 'missing_value')
                observations.append({**row, **extra, 'region': region, 'region_name': names[region], 'metric': metric,
                    'unit': row.get('unit', 't' if metric == 'tonnes' else 'tkm'),
                    'label': names[region] + ' / ' + ('Gütermenge' if metric == 'tonnes' else 'Verkehrsleistung') + ' / ' + row['label']})
    return {'status': 'partial' if any(row['value'] is None and row['value_status'] != 'not_computable' for row in observations) else 'available',
            'observations': observations,
            'note': 'Szenariovergleich der VP: Prognosebasis 2019 zu Prognose 2040. Keine beobachtete Entwicklung und keine Zwischenprognosen. Regionen und Kennzahlen bleiben getrennt; keine regionsübergreifende Summe.',
            'counting': 'VP all: Versand und Empfang ohne Binnenverkehr plus Binnenverkehr einmal; einzelne Versand-/Empfangswerte ohne Binnenverkehr.'}


def forecast_comparison(con,dataset,*,region,metric,direction,observed_years):
    result=common(dataset,region,metric)
    observations=[]
    for year in observed_years:
        name,profile=read_profile(con,dataset,region,year)
        for mode,label in MODES.items():
            value=None if profile is None else (profile.get('modes_'+metric,{}).get(mode) if direction=='all'
                  else profile.get('modes_direction_'+metric,{}).get(mode,{}).get(direction))
            observations.append({'label':label+' / Ist '+str(year),'value':value,'year':year,'mode':mode,
                                 'direction':direction,'basis':'observed_profile'})
    forecast,status=forecast_rows(con,dataset,region,metric,direction)
    observations.extend(forecast)
    if any(o['value'] is None for o in observations): status='partial'
    return {**result,'observations':observations,'status':status,
            'note':'Ist-Jahresscheiben und VP2019_BASE/2040_P1 separat. VP all zählt Binnen einmal, Ist all zweimal; keine Ist-zu-VP-Änderungsrate. Keine weiteren Szenarien.'}
