"""Gegenräume und Modalgesamtsummen auf bestehenden, unveränderten Daten."""
import json
import math
from pathlib import Path
from .profiles import read_profile

MODES = {'road': 'Straße', 'rail': 'Schiene', 'iww': 'Binnenschiff'}
SCOPES = {'all': 'alle Ziele und Herkunftsorte', 'domestic': 'Inland (Deutschland)',
          'international': 'Ausland (außerhalb Deutschlands)'}
SUM_NOTE = ('Die Summe addiert die erfassten Mengen der ausgewählten Verkehrsträger. '
            'Bei kombinierten Transportketten können Güter in mehreren Verkehrsträgerstatistiken vorkommen; '
            'die Summe ist deshalb keine bereinigte Menge eindeutig verschiedener Güter.')


def scope_filter(direction, partner_scope, region):
    if direction not in {'outbound', 'inbound', 'all'} or partner_scope not in SCOPES:
        raise ValueError('Unzulässige Richtung oder Gegenraum')
    clauses=[]; args=[]
    for side,other in [('origin_id','dest_id'),('dest_id','origin_id')]:
        if (direction=='outbound' and side!='origin_id') or (direction=='inbound' and side!='dest_id'):
            continue
        clause=side+'=?'; args.append(region)
        if partner_scope=='domestic': clause += " AND starts_with("+other+", 'DE')"
        elif partner_scope=='international':
            # Valid country/NUTS identifiers only; null or unknown IDs are not foreign countries.
            clause += " AND regexp_full_match("+other+", '[A-Z]{2}[A-Z0-9]{0,3}') AND NOT starts_with("+other+", 'DE') AND substr("+other+",1,2) NOT IN ('ZZ','XX','QU','QV','QW','QX','QY','QZ')"
        clauses.append('('+clause+')')
    return ' OR '.join(clauses),args


def scoped_rows(con, dataset, *, region, year, mode, metric, direction, partner_scope):
    where,args=scope_filter(direction,partner_scope,region)
    cursor=con.execute('''SELECT group_7_id AS goods, sum(known_sum) AS value,
        sum(missing_count) AS missing_count, sum(restricted_count) AS restricted_count,
        sum(unknown_quality_count) AS unknown_quality_count, sum(source_rows) AS source_rows
        FROM read_parquet(?) WHERE year_ref=? AND mode=? AND metric=? AND ('''+where+''')
        GROUP BY group_7_id ORDER BY group_7_id''',
        [str(Path(dataset)/'annual_od.parquet'),year,mode,metric,*args])
    return [dict(zip([x[0] for x in cursor.description],row)) for row in cursor.fetchall()]


def add_modal_sums(observations, modes, dimensions):
    """Add only disjoint modal tonnage facts; no KV, percentages or goods subtotals."""
    if len(modes)<2: return
    groups={}
    for row in list(observations):
        if row.get('mode') not in modes or row.get('unit','t') not in {'t','tonnes'} or row.get('change'):
            continue
        if row.get('group') not in {None,'ALL'}: continue
        groups.setdefault(tuple(row.get(k) for k in dimensions),[]).append(row)
    for key,rows in groups.items():
        by_mode={r['mode']:r for r in rows}
        if len(by_mode)!=len(rows): raise ValueError('Überlappende Modalwerte dürfen nicht summiert werden')
        missing=[m for m in modes if m not in by_mode or by_mode[m]['value'] is None]
        known=[by_mode[m] for m in modes if m not in missing]
        meta=dict(zip(dimensions,key))
        prefix=' / '.join(str(v) for v in key if v is not None and v!='ALL')
        total={'label':prefix+' / Summe der ausgewählten Verkehrsträger', 'value':None if missing else math.fsum(r['value'] for r in known),
               'mode':'total','unit':'t','aggregate':'modal_sum','components':modes,'missing_modes':missing,
               'source_status':'partial' if missing else 'available',
               'quality':'restricted' if any(r.get('restricted_count',0) or r.get('quality')=='restricted' for r in known) else 'unknown' if any(r.get('quality','unknown')=='unknown' for r in known) else 'unflagged',
               'formula':'sum(selected_modal_tonnes_same_scope)',**meta}
        observations.append(total)
        if missing and known:
            observations.append({**total,'label':prefix+' / Bekannte Teilsumme ('+', '.join(MODES[r['mode']] for r in known)+')',
                                 'value':math.fsum(r['value'] for r in known),'mode':'subtotal','aggregate':'known_modal_subtotal',
                                 'components':[r['mode'] for r in known]})


def transport_history(con,dataset,*,region,start,end,modes,metric,direction,partner_scope='all'):
    if region=='DE':
        return {'status':'not_available','observations':[], 'note':'Bitte für diese Regionalzeitreihe eine Stadt oder einen Kreis wählen; nationale Werte haben eine andere Zählweise.'}
    if start>end or end-start>9: raise ValueError('Zeitraum maximal zehn Jahre')
    observations=[]
    b01=Path(dataset).parents[2]/'b01'/'releases'/json.loads((Path(dataset)/'manifest.json').read_text(encoding='utf-8'))['dependencies']['b01']['snapshot_id']
    for year in range(start,end+1):
        _,profile=read_profile(con,dataset,region,year)
        for mode in modes:
            if partner_scope=='all':
                value=None if profile is None else (profile.get('modes_'+metric,{}).get(mode) if direction=='all' else profile.get('modes_direction_'+metric,{}).get(mode,{}).get(direction))
                quality='unknown'; missing=0
            else:
                rows=scoped_rows(con,b01,region=region,year=year,mode=mode,metric=metric,direction=direction,partner_scope=partner_scope)
                missing=sum(r['missing_count'] for r in rows)
                value=math.fsum(r['value'] or 0 for r in rows) if rows and not missing else None
                quality='restricted' if any(r['restricted_count'] for r in rows) else 'unknown' if any(r['unknown_quality_count'] for r in rows) else 'unflagged'
            observations.append({'label':str(year)+' / '+MODES[mode], 'year':year,'region':region,'direction':direction,
                'partner_scope':partner_scope,'mode':mode,'metric':metric,'unit':'t' if metric=='tonnes' else 'tkm',
                'value':value,'quality':quality,'source_status':'available' if value is not None else 'not_available'})
    if metric=='tonnes':add_modal_sums(observations,modes,['year','region','direction','partner_scope','metric'])
    for mode in [*modes,*(['total'] if len(modes)>1 and metric=='tonnes' else [])]:
        ends=[next((r for r in observations if r.get('mode')==mode and r.get('year')==y),None) for y in [start,end]]
        first,last=ends
        valid=first and last and first['value'] is not None and last['value'] is not None
        change=last['value']-first['value'] if valid else None
        for kind,value,unit in [('absolute',change,'t' if metric=='tonnes' else 'tkm'),('relative',change/first['value']*100 if valid and first['value'] else None,'%')]:
            observations.append({'label':f'{start}–{end} / '+MODES.get(mode,'Summe')+' / Veränderung'+(' in Prozent' if kind=='relative' else ''),
                'value':value,'unit':unit,'change':kind,'mode':mode,'region':region,'direction':direction,'partner_scope':partner_scope,
                'start_year':start,'end_year':end,'endpoint_values':[r['value'] if r else None for r in ends],
                'formula':'end - start' if kind=='absolute' else '(end - start) / start * 100'})
    return {'status':'available' if all(r['value'] is not None for r in observations if not r.get('change')) else 'partial',
        'observations':observations,'scope':'Güterverkehr der Region; Gegenraum: '+SCOPES[partner_scope]+'.',
        'counting':('Versand plus Empfang zählt innerregionale Verkehre zweimal, wie im Regionalprofil.' if partner_scope=='all' else 'Gerichtete veröffentlichte Relationen; bei beiden Richtungen wird innerregionaler Verkehr einmal gezählt.'),
        'note':SUM_NOTE if metric=='tonnes' else 'Verkehrsleistungen werden wegen unterschiedlicher Erfassungsräume je Verkehrsträger ausgewiesen.'}
