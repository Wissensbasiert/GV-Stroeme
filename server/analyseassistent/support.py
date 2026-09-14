"""Zusätzliche Güter- und KV-Abfragen aus dem separat gebundenen Support-Abbild."""
import json
import math
from pathlib import Path
from scripts.analysis.b0406 import rank


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def dependency(dataset,package):
    snapshot=read(Path(dataset)/'manifest.json')['dependencies'][package]['snapshot_id']
    return Path(dataset).parents[2]/package/'releases'/snapshot


def scoped_goods(con,dataset,*,region,year,mode,metric,directions,granularity,partner_scope):
    from .transport import scoped_rows, SCOPES
    base={'observations':[],'unit':'t' if metric=='tonnes' else 'tkm',
          'scope':'Gerichtete veröffentlichte Güterverkehre; Gegenraum: '+SCOPES[partner_scope]+'.',
          'counting':'Bei beiden Richtungen wird innerregionaler Verkehr einmal gezählt.',
          'note':'Anteile beziehen sich auf die bekannten veröffentlichten Güterangaben im ausgewählten Gegenraum. Fehlende Gütergruppen bleiben unbekannt.'}
    if mode=='road' or granularity!='C7':
        return {**base,'status':'not_available','note':'Die gewählte Gütergliederung mit Inland-/Auslandsfilter ist hier nur für Schiene und Binnenschiff auf C7 verfügbar. Straßen-OD enthält Gesamtmengen, keine Güteraufteilung.'}
    labels=read(dependency(dataset,'b03')/'classification.json')['groups']
    observations=[]; complete=True
    for direction in directions:
        rows=scoped_rows(con,dependency(dataset,'b01'),region=region,year=year,mode=mode,metric=metric,direction=direction,partner_scope=partner_scope)
        by_group={r['goods']:r for r in rows}
        total=math.fsum(r['value'] or 0 for r in rows) if rows and not any(r['missing_count'] for r in rows) else None
        values={g:(by_group[g]['value'] if g in by_group and not by_group[g]['missing_count'] else None) for g in '1234567'}
        ranks={r['id']:r['rank'] for r in rank([{'id':g,'value':v} for g,v in values.items()])}
        if total is None or any(v is None for v in values.values()):complete=False
        for g,value in sorted(values.items(),key=lambda r:(ranks.get(r[0],999),r[0])):
            source=by_group.get(g,{})
            meta={'group':g,'direction':direction,'mode':mode,'year':year,'region':region,'partner_scope':partner_scope,'rank':ranks.get(g),
                  'restricted_count':source.get('restricted_count',0),
                  'quality':'restricted' if source.get('restricted_count') else 'unknown' if source.get('unknown_quality_count') or not source else 'unflagged'}
            label={'all':'Versand und Empfang','outbound':'Versand','inbound':'Empfang'}[direction]+' / C'+g+' '+labels[g]
            observations.extend([{**meta,'label':label,'value':value},
                {**meta,'label':label+' / Anteil','value':value/total*100 if value is not None and total else None,'unit':'%',
                 'denominator':total,'denominator_scope':SCOPES[partner_scope]+', derselbe Verkehrsträger und dieselbe Richtung',
                 'formula':'group_value / published_scope_total * 100'}])
        observations.append({'label':direction+' / Gesamt','value':total,'direction':direction,'mode':mode,'year':year,'region':region,'partner_scope':partner_scope,
            'restricted_count':sum(r['restricted_count'] for r in rows),
            'quality':'restricted' if any(r['restricted_count'] for r in rows) else 'unknown' if not rows or any(r['unknown_quality_count'] for r in rows) else 'unflagged'})
    return {**base,'observations':observations,'status':'available' if complete else 'partial'}


def goods_structure(con,dataset,*,region,year,mode,metric,directions,granularity,partner_scope='all'):
    if partner_scope!='all':
        return scoped_goods(con,dataset,region=region,year=year,mode=mode,metric=metric,directions=directions,granularity=granularity,partner_scope=partner_scope)
    base={'unit':'t' if metric=='tonnes' else 'tkm','observations':[],
          'scope':'Bestehende D01-Güterstruktur einer NUTS-3-Region; keine Güteraufteilung auf einzelne Straßenrelationen.',
          'counting':'Versand und Empfang separat; all summiert beide Richtungen und zählt Binnen doppelt.',
          'quality_note':'D01-Profilwerte: Straßen-Quellenkennzeichen der Güterrandsummen nicht nacherschlossen. Keine zusätzliche Rohquellenfreigabe.'}
    if granularity!='C7':
        return {**base,'status':'not_available','note':'Für diese Profilabfrage sind nur C1–C7 freigegeben. Keine künstliche NST-20-Aufteilung; VD3c auf NUTS-2 betrifft deutsche Lkw und eine andere Abgrenzung.'}
    profile=read(Path(dataset)/'goods.json').get(region,{}).get(str(year))
    coverage=read(dependency(dataset,'b0406')/'source_coverage.json')
    if profile is None or not any(r['mode']==mode and r['year']==year for r in coverage):
        return {**base,'status':'missing_year','note':'Für Region, Verkehrsträger und Jahr liegt keine freigegebene Profilbasis vor.'}
    labels=read(dependency(dataset,'b03')/'classification.json')['groups']
    observations=[]
    status='available'
    for direction in directions:
        groups=profile.get('by_mode_groups' if metric=='tonnes' else 'by_mode_groups_tkm',{}).get(mode,{}).get(direction,{})
        total=profile.get('modes_'+metric,{}).get(mode) if direction=='all' else profile.get('modes_direction_'+metric,{}).get(mode,{}).get(direction)
        records=[{'id':g,'value':groups.get(g)} for g in '1234567']
        complete=all(r['value'] is not None for r in records) and total is not None
        compatible=complete and math.isclose(sum(r['value'] for r in records),total,rel_tol=1e-12,abs_tol=0.051)
        denominator=total if compatible else None
        if not compatible: status='partial'
        ranks={r['id']:r['rank'] for r in rank(records)}
        for row in sorted(records,key=lambda r:(ranks.get(r['id'],999),r['id'])):
            group,value=row['id'],row['value']
            label={'outbound':'Versand','inbound':'Empfang','all':'Versand plus Empfang'}[direction]+' / C'+group+' '+labels[group]
            metadata={'group':group,'direction':direction,'rank':ranks.get(group),'mode':mode,'year':year,'region':region}
            observations.append({**metadata,'label':label,'value':value})
            observations.append({**metadata,'label':label+' / Anteil','value':value/denominator*100 if denominator and value is not None else None,
                                 'unit':'%','denominator':denominator,'denominator_scope':'Gleicher Verkehrsträger, Jahr, Richtung und vollständige C1–C7',
                                 'formula':'group_value / compatible_modal_direction_total * 100'})
        observations.append({'label':direction+' / Gesamt','value':total,'direction':direction,'year':year,'mode':mode})
    return {**base,'status':status,'observations':observations,
            'note':'Aktueller C1–C7-Crosswalk; fehlende Gruppen bleiben unbekannt. Ranggleichstände vor Rundung, keine Standort- oder Produktionsursache.'}


def goods_history(con,dataset,*,region,start,end,modes,metric,directions,partner_scope='all'):
    """Published profiles by year/mode; unknown groups never become zero."""
    if start > end or end-start > 9:
        raise ValueError('Güterzeitraum muss ein bis zehn Jahre umfassen')
    if (15*(end-start+1)+16)*len(modes)*len(directions) > 600:
        raise ValueError('Güterauswertung überschreitet den Ergebnisumfang')
    labels=read(dependency(dataset,'b03')/'classification.json')['groups']
    unit='t' if metric=='tonnes' else 'tkm'
    observations=[]
    complete=True
    for year in range(start,end+1):
        for mode in modes:
            raw=goods_structure(con,dataset,region=region,year=year,mode=mode,metric=metric,
                                directions=directions,granularity='C7',partner_scope=partner_scope)
            if raw['status']!='available': complete=False
            rows=raw['observations']
            if not rows:
                rows=[]
                for direction in directions:
                    for group in '1234567':
                        meta={'group':group,'direction':direction,'region':region,'mode':mode,'year':year}
                        rows.extend([{**meta,'label':direction+' / C'+group+' '+labels[group],'value':None},
                                     {**meta,'label':direction+' / C'+group+' '+labels[group]+' / Anteil','value':None,'unit':'%'}])
                    rows.append({'label':direction+' / Gesamt','direction':direction,'value':None,'region':region,'mode':mode,'year':year})
            for row in rows:
                observations.append({**row,'label':str(year)+' / '+mode+' / '+row['label'],
                                     'source_status':'not_available' if raw['status']=='missing_year' else raw['status'],
                                     'region':region,'metric':metric,'unit':row.get('unit',unit)})
    # Calculate differences only from the requested endpoints of the same series.
    for mode in modes:
        for direction in directions:
            for group in [None,*'1234567']:
                endpoints=[next(r for r in observations if r.get('year')==y and r['mode']==mode
                                and r['direction']==direction and r.get('group')==group and r['unit']==unit)
                           for y in [start,end]]
                first,last=endpoints
                valid=first['value'] is not None and last['value'] is not None
                absolute=last['value']-first['value'] if valid else None
                relative=absolute/first['value']*100 if valid and first['value']!=0 else None
                meta={'mode':mode,'direction':direction,'region':region,'metric':metric,
                      'group':group,'start_year':start,'end_year':end,'basis':'published_profile_change' if partner_scope=='all' else 'published_od_change',
                      'endpoint_values':[first['value'],last['value']]}
                label=f'{start}–{end} / {mode} / {direction} / '+('C'+group+' '+labels[group] if group else 'Gesamt')
                observations.extend([{**meta,'label':label+' / Veränderung','value':absolute,'unit':unit,
                                      'change':'absolute','formula':'end_value - start_value',
                                      'value_status':'calculated' if valid else 'missing_value'},
                                     {**meta,'label':label+' / Veränderung in Prozent','value':relative,'unit':'%',
                                      'change':'relative','formula':'(end_value - start_value) / start_value * 100',
                                      'value_status':'calculated' if relative is not None else 'not_computable' if valid else 'missing_value'}])
    return {'status':'available_with_comparability_limits' if complete else 'partial','unit':unit,'observations':observations,
            'scope':raw['scope'],
            'counting':raw['counting'],
            'quality_note':('Veränderungen der veröffentlichten D01-Profilwerte; Straßen-Quellenkennzeichen der Güterrandsummen sind nicht nacherschlossen. ' if partner_scope=='all' else 'Veränderungen veröffentlichter B01-Relationen im ausgewählten Gegenraum. ')+'Keine harmonisierte Gebietszeitreihe und kein Nachweis von Ursachen.',
            'note':'Fehlende Gütergruppen bleiben unbekannt, auch bei einem veröffentlichten Verkehrsträger-Gesamtwert null. Fehlende Randjahre werden nicht durch andere Jahre ersetzt.'}


def intermodal_markets(con,dataset,*,region,year,modes,metrics,direction):
    records=read(Path(dataset)/'intermodal.json')
    observations=[]
    complete=True
    for mode in modes:
        for metric in metrics:
            matches=[r for r in records if (r['region'],r['year'],r['mode'],r['metric'],r['direction'])==(region,year,mode,metric,direction)]
            if len(matches)>1: raise ValueError('Mehrdeutiger KV-Kennwert')
            row=matches[0] if matches else {}
            numerator,denominator=row.get('qualified_value'),row.get('total_value')
            valid=numerator is not None and denominator is not None and numerator<=denominator+0.001
            if not valid: complete=False
            metadata={'region':region,'year':year,'mode':mode,'metric':metric,'direction':direction,
                      'unit':'t' if metric=='tonnes' else 'tkm','months':row.get('months',[]),
                      'source_ids':row.get('source_ids',[]),'total_missing':row.get('total_missing'),
                      'qualified_missing':row.get('qualified_missing'),'qualification_unknown':row.get('qualification_unknown')}
            metadata['unknown_endpoint_count']=row.get('unknown_endpoint_count')
            label=('Schiene: ausgewiesene Ladeeinheiten' if mode=='rail' else 'Binnenschiff: ausgewiesene Containerklasse')
            observations.append({**metadata,'label':label,'value':numerator})
            observations.append({**metadata,'label':mode+' / Verkehrsträger insgesamt','value':denominator})
            observations.append({**metadata,'label':label+' / Anteil','value':numerator/denominator*100 if valid and denominator else None,
                                 'unit':'%','denominator':denominator if valid else None,
                                 'denominator_scope':'Derselbe Verkehrsträger, dieselbe Kennzahl, Region, Richtung und vollständige zwölf Quellmonate',
                                 'formula':'qualified_modal_value / same_modal_total * 100'})
    return {'status':'available' if complete else 'partial','observations':observations,
            'scope':'Nationale Gesamtabgrenzung bei DE/all; regionale veröffentlichte OD-Zeilen bei NUTS-3, einschließlich grenzüberschreitender Partner.',
            'counting':'Regional outbound/inbound ohne Binnen und nur mit bekanntem Gegenraum; internal separat; regional all jede ausgewählte Quellzeile einmal, auch bei unbekanntem Gegenraum. National all jede Quellzeile einmal.',
            'note':'Schiene und Binnenschiff sind nicht additiv: dieselbe Transportkette kann in beiden Statistiken auftreten. Keine eindeutige KV-Gesamtsumme, kein Verlagerungspotenzial und keine Terminalauslastung. Fehlende Monate oder Werte sperren vollständige Kennzahlen; keine harmonisierte Gebietszeitreihe.'}
