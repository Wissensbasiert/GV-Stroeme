"""Mehrere ausdrücklich gewählte Kennzahlen desselben Hafen-/Flughafenjahrs."""
from scripts.analysis.b0406 import node_statistics


def node_profile(con,dataset,*,kind,node,year,direction,metrics):
    observations=[]
    notes=[]
    for metric in metrics:
        raw=node_statistics(con,dataset,kind=kind,node=node,year=year,direction=direction,metric=metric)
        observations.append({'label':node+' / '+str(year)+' / '+{'tonnes':'Frachtgewicht','flights':'Flüge','teu':'TEU'}[metric],
                             'value':raw['value'],'unit':{'tonnes':'t','flights':'Flüge','teu':'TEU'}[metric],
                             'year':year,'node':node,'direction':direction,'metric':metric,
                             'source_status':raw['status'],'source_ids':raw.get('source_ids',[]),
                             'restricted_count':raw.get('restricted_count',0)})
        notes.extend(raw[k] for k in ['note','counting'] if raw.get(k))
    return {'observations':observations,'status':'available' if all(r['value'] is not None for r in observations) else 'partial',
            'scope':'Veröffentlichte Randsumme des ausdrücklich gewählten Knotens, Jahres und Richtungsbezugs.',
            'note':' '.join(dict.fromkeys(notes))+ ' Unterschiedliche Einheiten bleiben getrennt. Kein stiller Wechsel in ein anderes Bezugsjahr.'}
