"""Begrenzte Relationsauswertungen auf dem unveränderten geprüften B01-Abbild."""
from pathlib import Path
import json
from scripts.analysis.b01 import query_relation
from scripts.analysis.b0406 import rank, rows
from scripts.analysis.b03 import query_rail


def relation_matrix(con, dataset, *, origin, destination, year, metric):
    observations=[]
    for mode in ['road','rail','iww']:
        for source,target in [(origin,destination),(destination,origin)]:
            result=query_relation(con,dataset,year=year,origin=source,destination=target,
                                  mode=mode,metric=metric,group='ALL')
            observations.append({'label':source+' → '+target+' / '+mode,'value':result['value'],
                                 'mode':mode,'origin':source,'destination':target,
                                 'source_status':result['status'],'quality':result.get('quality','unknown'),
                                 'source_ids':result.get('source_ids',[]),
                                 'missing_count':result.get('missing_count'),
                                 'restricted_count':result.get('restricted_count')})
    return {'status':'available' if all(r['value'] is not None for r in observations) else 'partial',
            'unit':'t' if metric=='tonnes' else 'tkm','observations':observations,
            'scope':'Summe vorhandener veröffentlichter Zeilen je Verkehrsträger und gerichteter Relation.',
            'counting':'Jede Richtung separat; keine gemeinsame Summe über Verkehrsträger.',
             'note':'Eine nicht veröffentlichte Relation ist kein Nullnachweis. Keine Aussage zu Route, Hafennutzung oder Terminalpotenzial.'}


def relation_overview(con,dataset,*,origin,destination,year,modes,metrics,include_goods):
    # One scan for the selected route; totals and disjoint groups share the
    # same source-flag rules as B01.query_relation.
    records=rows(con.execute('''SELECT mode,metric,group_7_id,sum(source_rows) AS source_rows,
        sum(known_sum) AS known_sum,sum(missing_count) AS missing_count,
        sum(restricted_count) AS restricted_count,sum(unknown_quality_count) AS unknown_quality_count,
        list(DISTINCT source_id) AS source_ids FROM read_parquet(?)
        WHERE origin_id=? AND dest_id=? AND year_ref=? GROUP BY mode,metric,group_7_id''',
        [str(Path(dataset)/'annual_od.parquet'),origin,destination,year]))
    coverage=json.loads((Path(dataset)/'manifest.json').read_text(encoding='utf-8'))['years_by_mode']
    observations=[]
    for mode in modes:
        for metric in metrics:
            for group in (['ALL',*[str(n) for n in range(1,8)]] if include_goods and mode!='road' else ['ALL']):
                selected=[r for r in records if r['mode']==mode and r['metric']==metric and (group=='ALL' or r['group_7_id']==group)]
                missing=sum(r['missing_count'] or 0 for r in selected)
                restricted=sum(r['restricted_count'] or 0 for r in selected)
                raw={'value':sum(r['known_sum'] or 0 for r in selected) if selected and not missing else None,
                    'unit':'t' if metric=='tonnes' else 'tkm',
                    'status':('not_available' if year not in coverage[mode] else 'missing_row') if not selected else 'partial' if missing else 'available',
                    'quality':'unknown' if not selected or any(r['unknown_quality_count'] for r in selected) else 'restricted' if restricted else 'unflagged',
                    'missing_count':missing,'restricted_count':restricted,
                    'source_ids':sorted({s for r in selected for s in r['source_ids']})}
                observations.append({'label':mode+' / '+('Alle veröffentlichten Güterangaben' if group=='ALL' else 'C'+group),
                    'value':raw['value'],'unit':raw['unit'],'mode':mode,'metric':metric,'group':group,'year':year,
                    'source_status':raw['status'],'quality':raw.get('quality','unknown'),
                    'missing_count':raw.get('missing_count'),'restricted_count':raw.get('restricted_count'),
                    'source_ids':raw.get('source_ids',[])})
    return {'status':'partial' if (include_goods and 'road' in modes) or any(r['value'] is None for r in observations) else 'available',
        'observations':observations,'scope':'Gerichtete Jahresrelation; Verkehrsträger und Kennzahlen getrennt.',
        'note':'Straßenrelationen enthalten keine Güteraufteilung. Gruppen und Gesamtwerte überlappen und dürfen nicht addiert werden. Fehlende Angaben bleiben unbekannt.'}


def relation_history(con, dataset, *, origin, destination, start, end, modes, metric):
    """Mehrjährige gerichtete Relation, Verkehrsträger bewusst getrennt."""
    if end-start>20:
        raise ValueError('Höchstens 21 veröffentlichte Jahresscheiben auswählen')
    observations=[]
    for year in range(start,end+1):
        for mode in modes:
            result=query_relation(con,dataset,year=year,origin=origin,destination=destination,
                                  mode=mode,metric=metric,group='ALL')
            observations.append({'label':str(year)+' / '+mode,'value':result['value'],
                                 'year':year,'mode':mode,'origin':origin,'destination':destination,
                                 'source_status':result['status'],'quality':result.get('quality','unknown'),
                                 'source_ids':result.get('source_ids',[]),
                                 'missing_count':result.get('missing_count'),
                                 'restricted_count':result.get('restricted_count')})
    return {'status':'available' if observations and all(r['value'] is not None for r in observations) else 'partial',
            'unit':'t' if metric=='tonnes' else 'tkm','observations':observations,
            'scope':'Veröffentlichte Jahreswerte der gerichteten Relation, je Verkehrsträger getrennt.',
            'counting':'Jahr und Verkehrsträger werden separat ausgewiesen; keine gemeinsame Summe über Verkehrsträger.',
            'note':'Eine prozentuale Veränderung setzt Zahlen für das angefragte Anfangs- und Endjahr voraus. Fehlende Randjahre werden nicht durch Zwischenjahre ersetzt. Die Rate ist nicht um methodische Brüche bereinigt und belegt keine Ursache. Eine fehlende Relation ist kein Nachweis, dass tatsächlich kein Verkehr stattfand.'}


def road_relation_goods_limit(con,dataset,*,origin,destination,year,metric):
    raw=query_relation(con,dataset,origin=origin,destination=destination,year=year,mode='road',metric=metric,group='ALL')
    return {**raw,'status':'partial' if raw['value'] is not None else raw['status'],
            'observations':[{'label':'Straßenrelation / alle Güter','value':raw['value'],
                             'origin':origin,'destination':destination,'year':year,'mode':'road',
                             'quality':raw.get('quality','unknown'),'restricted_count':raw.get('restricted_count'),
                             'source_ids':raw.get('source_ids',[])}],
            'note':raw['note']+' Die Güterstruktur dieser Straßenrelation ist nicht verfügbar. Weder C1–C7 noch NST-20 aus regionalen Randsummen auf die OD übertragen.'}


def rail_goods_history(con,dataset,*,region,partner,years,direction,metric):
    observations=[]
    for year in years:
        raw=query_rail(con,dataset,region=region,partner=partner,year=year,direction=direction,metric=metric,group='ALL',nst=None)
        for row in raw['details']:
            observations.append({'label':str(year)+' / NST '+row['nst_raw'],'value':row['value'],'year':year,
                                 'nst_raw':row['nst_raw'],'group':row['group_7_id'],'missing_count':row['missing_count'],
                                 'restricted_count':row['restricted_count']})
        observations.append({'label':str(year)+' / Summe bekannter veröffentlichter Feinpositionen',
                             'value':raw['published_sum'],'year':year,'sum_scope':'Nur bekannte veröffentlichte Zeilen'})
    return {'status':'available' if observations and all(r['value'] is not None for r in observations) else 'partial',
            'observations':observations,'unit':'t' if metric=='tonnes' else 'tkm',
            'scope':'Schienen-Feinpositionen der identischen bestätigten Relation, Kennzahl und Richtung, je Quelljahr.',
            'note':'Fehlende Feinpositionen sind kein Nullnachweis; kein Rückgang um −100 % aus einer fehlenden Zeile. Quellenjahre nicht harmonisiert, keine bestätigte Änderungsrate und keine Ursache. Zeilensummen sind keine Garantie vollständigen realen Verkehrs.'}


def partner_ranking(con,dataset,*,region,year,mode,metric,direction,group,top,external):
    if mode=='road' and group!='ALL':
        return {'status':'not_available','observations':[],
                'note':'Straßenrelationen liegen nur für alle Güter vor; keine Güteraufteilung aus regionalen Randsummen.'}
    # Each directed OD enters once. For both directions an internal OD also
    # enters once; external=True excludes it before aggregation and denominator.
    where={'outbound':'origin_id=?','inbound':'dest_id=?','all':'(origin_id=? OR dest_id=?)'}[direction]
    args=[region,region] if direction=='all' else [region]
    if external:
        where+=' AND origin_id<>dest_id'
    if group!='ALL':
        where+=' AND group_7_id=?';args.append(group)
    data=rows(con.execute('''SELECT CASE WHEN origin_id=? THEN dest_id ELSE origin_id END AS id,
        sum(known_sum) AS known_sum,sum(source_rows) AS source_rows,
        sum(missing_count) AS missing_count,sum(restricted_count) AS restricted_count,
        sum(CASE WHEN restricted_count>0 THEN known_sum ELSE 0 END) AS restricted_value,
        sum(unknown_quality_count) AS unknown_quality_count,
        sum(rounded_zero_count) AS rounded_zero_count,
        list(DISTINCT source_id) AS source_ids
        FROM read_parquet(?) WHERE year_ref=? AND mode=? AND metric=? AND '''+where+' GROUP BY 1',
        [region,str(Path(dataset)/'annual_od.parquet'),year,mode,metric,*args]))
    for row in data:
        row['value']=row['known_sum'] if not row['missing_count'] else None
        row['quality']='unknown' if row['unknown_quality_count'] else 'restricted' if row['restricted_count'] else 'unflagged'
    denominator=sum(r['value'] for r in data) if data and all(r['value'] is not None for r in data) else None
    ranked=rank(data,top=top)
    observations=[]
    for row in ranked:
        metadata={k:v for k,v in row.items() if k not in {'value','known_sum'}}
        observations.append({**metadata,'label':row['id'],'value':row['value']})
        observations.append({**metadata,'label':row['id']+' / Anteil',
                             'value':row['value']/denominator*100 if denominator else None,'unit':'%',
                             'denominator':denominator,'denominator_scope':'Alle veröffentlichten Partner der bestätigten Auswahl vor Top-Begrenzung',
                             'formula':'partner_value / all_published_partner_values * 100'})
    return {'status':'available' if data and denominator is not None else 'partial' if data else 'missing_row',
            'observations':observations,'unit':'t' if metric=='tonnes' else 'tkm',
            'denominator':denominator,'partner_count':len(data),'ranked_count':len(ranked),
            'unknown_partner_count':sum(r['value'] is None for r in data),
            'restricted_denominator_value':sum(r['restricted_value'] for r in data if r['restricted_value'] is not None),
            'scope':'Vollständige Auswahl veröffentlichter B01-Partnerzeilen; kein Nachweis des gesamten realen Verkehrs.',
            'counting':'Beide Richtungen zusammen bei all; Binnen einmal, bei externen Partnern ausgeschlossen.',
            'note':'Nenner vor Top-Begrenzung. Ranggleichstände bleiben vollständig erhalten; unbekannte Partnerwerte sind nicht rangfähig. Fehlende Partner sind kein Nullnachweis.'}
