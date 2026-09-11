"""B02: Monatsabdeckung und ausdrücklich begrenzte Zeitvergleiche."""
import json
from pathlib import Path
from scripts.analysis.b01 import ROOT, literal

STORE = ROOT / 'data/analysis/b02'
MONTHLY_SQL = '''SELECT year_ref,origin_id,dest_id,mode,group_7_id,metric,source_id,
 legacy_scope,CAST(month_text AS INTEGER) AS month,
 count(*) AS source_rows,sum(value) AS known_sum,
 count(*) FILTER(WHERE value IS NULL) AS missing_count,
 count(*) FILTER(WHERE quality_status='restricted') AS restricted_count,
 count(*) FILTER(WHERE quality_status='unknown') AS unknown_quality_count,
 list(DISTINCT value_status) AS source_value_states,
 CASE WHEN count(*) FILTER(WHERE value IS NULL)>0 THEN NULL ELSE sum(value) END AS value
 FROM evidence WHERE mode IN ('rail','iww') GROUP BY ALL'''


def resolve_dataset(store=STORE):
    store = Path(store).resolve()
    if (store/'manifest.json').exists():
        return store
    pointer = json.loads((store/'current.json').read_text(encoding='utf-8'))
    result = (store/'releases'/pointer['snapshot_id']).resolve()
    if result.parent != store/'releases':
        raise ValueError('Ungültiger B02-Datenstandsverweis')
    return result


def summarize_months(rows):
    """Keine Quellzeile ist kein Nullmonat; Ranggleichheit bleibt erhalten."""
    by_month = {r['month']: r for r in rows}
    if len(by_month) != len(rows) or any(m not in range(1,13) for m in by_month):
        raise ValueError('Monate müssen eindeutig und zwischen 1 und 12 liegen')
    missing = [m for m in range(1,13) if m not in by_month]
    unknown = [m for m,r in by_month.items() if r['missing_count'] or r['value'] is None]
    known = [r['known_sum'] for r in rows if r['known_sum'] is not None]
    full = not missing and not unknown
    total = sum(known) if known else None
    maximum = max((r['value'] for r in rows),default=None) if full else None
    return {'status':'available' if full else 'missing_row' if not rows else 'incomplete',
            'observed_months':sorted(by_month),'missing_months':missing,
            'months_with_unknown_values':sorted(unknown),
            'known_sum':total,'annual_value':total if full else None,
            'peak_months':[m for m,r in by_month.items() if r['value']==maximum] if full else [],
            'peak_month_share_pct':maximum/total*100 if full and total else None,
            'coverage_scope':'published_rows_only'}


def change(base, target, *, comparable=False):
    result={'absolute_change':None,'relative_change_pct':None}
    if base is None or target is None:
        return {**result,'status':'missing_value'}
    if not comparable:
        return {**result,'status':'comparability_not_confirmed'}
    return {'absolute_change':target-base,
            'relative_change_pct':(target-base)/base*100 if base else None,
            'status':'zero_base' if base==0 else 'available'}


def query_series(con,dataset,*,region,mode,direction='outbound',start=2016,end=2025,
                 group='ALL',metric='tonnes',partner=None):
    allowed={'road':{'tonnes','tkm','trips'},'rail':{'tonnes','tkm','load_units'},
             'iww':{'tonnes','tkm','load_carriers'}}
    if mode not in allowed or metric not in allowed[mode] or direction not in {'outbound','inbound','total'}:
        raise ValueError('Unzulässige Kennzahl, Richtung oder Verkehrsträger')
    if group not in {'ALL','1','2','3','4','5','6','7'} or not isinstance(region,str) or not region:
        raise ValueError('Region und Gütergruppe prüfen')
    if type(start) is not int or type(end) is not int or not 1900<=start<=end<=2100:
        raise ValueError('Ungültiger Zeitraum')
    if partner is not None and (not isinstance(partner,str) or not partner.strip()):
        raise ValueError('Partner muss eine nichtleere Textkennung sein')
    dataset=Path(dataset)
    manifest=json.loads((dataset/'manifest.json').read_text(encoding='utf-8'))
    coverage=json.loads((dataset/'source_coverage.json').read_text(encoding='utf-8'))
    result={'snapshot_id':manifest['snapshot_id'],'region':region,'partner':partner,
            'mode':mode,'direction':direction,'group':group,'metric':metric,
            'unit':'t' if metric=='tonnes' else 'tkm' if metric=='tkm' else 'Anzahl',
            'counting':'total zählt jede ausgewählte OD-Zeile einmal, Binnenverkehr einmal',
            'scope':'Veröffentlichte Quellzeilen; keine harmonisierte Gebietszeitreihe',
            'years':[], 'note':'Fehlende Monate sind kein Nullnachweis. Sprünge erklären keine Ursache.'}
    if mode=='road':
        return {**result,'status':'monthly_not_available','note':'VE7 enthält Jahreswerte, keine Monatswerte. Jahresabfrage über B01; keine Monatsverteilung schätzen.'}
    spatial={'outbound':'origin_id=?','inbound':'dest_id=?','total':'(origin_id=? OR dest_id=?)'}[direction]
    args=[region,region] if direction=='total' else [region]
    if partner is not None:
        if direction=='total':
            spatial='((origin_id=? AND dest_id=?) OR (dest_id=? AND origin_id=?))'
            args=[region,partner,region,partner]
        else:
            spatial+=' AND '+('dest_id=?' if direction=='outbound' else 'origin_id=?')
            args.append(partner)
    spatial+=' AND mode=? AND metric=? AND year_ref BETWEEN ? AND ?'
    args.extend([mode,metric,start,end])
    if group!='ALL':
        spatial+=' AND group_7_id=?';args.append(group)
    sql='''SELECT year_ref,month,sum(known_sum) AS known_sum,sum(missing_count) AS missing_count,
        sum(restricted_count) AS restricted_count,sum(unknown_quality_count) AS unknown_quality_count,
        CASE WHEN sum(missing_count)>0 THEN NULL ELSE sum(known_sum) END AS value,
        list(DISTINCT source_id) AS source_ids
        FROM read_parquet(?) WHERE '''+spatial+' GROUP BY 1,2 ORDER BY 1,2'
    cur=con.execute(sql,[str(dataset/'monthly_od.parquet'),*args])
    names=[c[0] for c in cur.description]; records=[dict(zip(names,r)) for r in cur.fetchall()]
    for year in range(start,end+1):
        sources=[r for r in coverage if r['mode']==mode and r['year']==year]
        months=[r for r in records if r['year_ref']==year]
        summary=summarize_months(months)
        if not sources: summary['status']='year_not_available'
        result['years'].append({'year':year,**summary,'months':months,'sources':sources,
            'comparability':'not_confirmed','revision_status':'not_documented'})
    states=[y['status'] for y in result['years']]
    result['status']=('year_not_available' if all(s=='year_not_available' for s in states) else
                      'missing_row' if not records else
                      'available_with_comparability_limits' if all(s=='available' for s in states) else 'incomplete')
    result['comparison']=change(result['years'][0]['annual_value'],result['years'][-1]['annual_value'])
    return result
