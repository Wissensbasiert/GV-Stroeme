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


def goods_structure(con,dataset,*,region,year,mode,metric,directions,granularity):
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
