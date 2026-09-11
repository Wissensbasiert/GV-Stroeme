"""Begrenzter Gesprächskontext und ausgewiesene Standards aus geprüften Daten."""
import copy
import json
import re
import duckdb
from .contracts import FUNCTIONS, directed_pairs, question_supports, token_present, validate

LATEST = re.compile(r'\b(?:aktuell\w*|neuest\w*|letzt\w*\s+verfügbar\w*)\s*(?:verfügbar\w*\s*)?(?:jahr\w*|daten\w*|stand)\b', re.I)
YEAR = re.compile(r'(?<!\w)(?:19|20)\d{2}(?!\w)')


def validate_history(history):
    if history is None:
        return []
    if not isinstance(history, list) or len(history)>6 or any(not isinstance(x,str) or not x.strip() or len(x)>4000 for x in history) or sum(map(len,history))>6000:
        raise ValueError('Gesprächsverlauf zu umfangreich')
    return history


def conversation_question(question, history, names):
    """Nur Nutzereingaben, keine alten KI-Zahlen als neue Faktenquelle."""
    active=''
    for text in [*validate_history(history),question]:
        named=any(question_supports(text,code,names) for code in names)
        independent=named and (bool(directed_pairs(text,names,[])) or (bool(re.search(r'\b(welche|wie|zeige|vergleiche)\b',text,re.I)) and not re.match(r'\s*(und|aber)\b',text,re.I)))
        if independent:
            active=text
            continue
        if YEAR.search(text) or LATEST.search(text):
            active=YEAR.sub('',active)
            active=LATEST.sub('',active)
        if any(question_supports(text,m,{}) for m in ['tonnes','tkm']):
            active=re.sub(r'\b(Tonnenkilometer|tkm|Tonnen)\b','',active,flags=re.I)
        active=(active+'\n'+text).strip()
    return active


def route_hint(question,names):
    pairs=directed_pairs(question,names,[])
    if len(pairs)!=1 or not re.search(r'\b(güter|güterarten|gütergruppen)\b',question,re.I) or re.search(r'\b(vergleiche|verändert|entwicklung|prognose)\b',question,re.I):
        return None
    modes=[m for m in ['rail','road','iww'] if question_supports(question,m,{})]
    return {'rail':'rail_goods','road':'road_relation_goods_limit'}.get(modes[0]) if len(modes)==1 else None


def direct_route(question, names):
    """Eng begrenzte Standardfrage; komplexere Anliegen bleiben bei der Modellplanung."""
    if not re.fullmatch(r'\s*Welche Güter (?:gehen|gingen|werden transportiert)\s+(?:(?:19|20)\d{2}\s+)?(?:per|auf der)\s+(?:Schiene|Straße)\s+von\s+[^?\n]+\s+nach\s+[^?\n]+\??\s*', question, re.I):
        return None
    if re.search(r'\b(und|aber|warum|weil|prognose|vergleich|mehr|weniger|nur)\b', question, re.I):
        return None
    return route_hint(question,names)


def available_years(datasets,function,parameters):
    """Jahrgänge des passenden Datenprodukts, ohne Ersatz für fehlende Werte."""
    if function=='rail_goods':
        path=datasets.paths['b03']/'rail_monthly_details.parquet'
        with duckdb.connect(config={'threads':2,'memory_limit':'128MB'}) as con:
            return [r[0] for r in con.execute('SELECT year_ref FROM read_parquet(?) GROUP BY year_ref HAVING count(DISTINCT month)=12 ORDER BY year_ref',[str(path)]).fetchall()]
    if function in {'relation','road_relation_goods_limit','partner_ranking','relation_matrix'}:
        mode=parameters.get('mode','road' if function=='road_relation_goods_limit' else None)
        years=datasets.manifests['b01']['years_by_mode']
        if mode:return sorted(int(y) for y in years.get(mode,[]))
        return sorted(set.intersection(*(set(int(y) for y in value) for value in years.values())))
    if function in {'region_profile','regional_modal_split','compare_regions','balance','goods_structure','intermodal_markets'}:
        path=datasets.paths['b0406']/'regional_profiles.parquet'
        regions=parameters.get('regions') or ([parameters['region']] if parameters.get('region') else [])
        if not regions:return []
        with duckdb.connect(config={'threads':2,'memory_limit':'128MB'}) as con:
            sets=[{r[0] for r in con.execute('SELECT year FROM read_parquet(?) WHERE id=?',[str(path),region]).fetchall()} for region in regions]
        coverage=json.loads((datasets.paths['b0406']/'source_coverage.json').read_text(encoding='utf-8'))
        modes=parameters.get('modes') or ([parameters['mode']] if parameters.get('mode') else ['road','rail','iww'])
        sets.extend({row['year'] for row in coverage if row['mode']==mode} for mode in modes)
        return sorted(set.intersection(*sets))
    return []


def defaults_for(function,question,datasets,parameters):
    props=FUNCTIONS[function][3]['properties']; context={}; notes=[]
    modes=[m for m in ['road','rail','iww'] if question_supports(question,m,{})]
    if 'mode' in props and len(modes)==1:context['mode']=modes[0]
    pair=directed_pairs(question,datasets.names,[])
    if len(pair)==1:
        origin,destination=next(iter(pair))
        if 'origin' in props and 'destination' in props:context.update(origin=origin,destination=destination)
        elif 'region' in props and 'partner' in props and 'direction' in props:
            context.update(region=origin,partner=destination,direction='outbound')
    choices={'metric':'tonnes','group':'ALL','nst':None,'top':10,'include_forecast':False,
             'granularity':'NST20' if re.search(r'\bNST\s*20\b',question,re.I) else 'C7'}
    mentioned_metrics=[m for m in ['tonnes','tkm','trips','load_units','teu','flights'] if question_supports(question,m,{})]
    if mentioned_metrics:
        choices['metric']=mentioned_metrics[0] if len(mentioned_metrics)==1 else None
    if 'metrics' in props:choices['metrics']=mentioned_metrics or ['tonnes']
    if 'directions' in props:
        choices['directions']=[d for d in ['outbound','inbound'] if question_supports(question,d,{})] or ['all']
    if re.search(r'\bC[1-7]\b',question,re.I): choices.pop('group',None)
    if re.search(r'\bNST\s*\d',question,re.I):choices.pop('nst',None)
    if re.search(r'\btop\s+\d+\b',question,re.I):choices.pop('top',None)
    if re.search(r'\b(prognose|2040)\b',question,re.I):choices.pop('include_forecast',None)
    for key,value in choices.items():
        if key not in props:continue
        try:validate(props[key],value)
        except ValueError:continue
        context[key]=value
        if key=='metric' and not mentioned_metrics:notes.append('Die Gütermengen werden in Tonnen dargestellt.')
        if key=='group' and value=='ALL':notes.append('Berücksichtigt werden alle verfügbaren Güterarten.')
        if key=='top' and not token_present(question,'10'):notes.append('Die Übersicht zeigt die zehn größten veröffentlichten Werte.')
    # Regional summaries may use both directions, but never erase an OD direction.
    if 'direction' in props and 'direction' not in context:
        directions=[d for d in ['outbound','inbound'] if question_supports(question,d,{})]
        value=directions[0] if len(directions)==1 else ('total' if 'total' in props['direction'].get('enum',[]) else 'all')
        try:validate(props['direction'],value)
        except ValueError:pass
        else:
            context['direction']=value
            if not directions:notes.append('Die Auswertung umfasst Versand und Empfang.')
    if 'partner' in props and 'partner' not in context and len(pair)==0:
        named={code for code in datasets.names if question_supports(question,code,datasets.names)}
        if len(named)<=1:context['partner']=None
    years=available_years(datasets,function,{**parameters,**context}) if 'year' in props else []
    explicit_years={int(x) for x in YEAR.findall(question)}
    if 'year' in props and len(explicit_years)==1:context['year']=next(iter(explicit_years))
    elif 'year' in props and not explicit_years and LATEST.search(question) and years:
        context['year']=max(years);notes.append(f'Verwendet wird das neueste vollständig verfügbare Datenjahr {max(years)} dieses Datenprodukts.')
    return context,notes,years


def complete_plan(plan,question,confirmed,datasets):
    """Modellvorschläge durch unabhängige Belege vervollständigen, nicht vertrauen."""
    plan=copy.deepcopy(plan)
    function=plan.get('function_id')
    if function not in FUNCTIONS or plan.get('status') not in {'ready','needs_clarification'}:
        return plan,confirmed,[],[]
    defaults,notes,years=defaults_for(function,question,datasets,plan.get('parameters',{}))
    parameters=plan['parameters']; origins=plan['parameter_origins']; approved=dict(confirmed)
    for key,value in defaults.items():
        if key in confirmed:continue
        # A differing model guess remains untrusted; directly evidenced routes/year
        # may replace guesses but explicit user values are checked again downstream.
        direct=key in {'origin','destination','region','partner','direction','year','mode'}
        if key not in parameters or parameters[key]==value or direct:
            parameters[key]=value;origins[key]='context';approved[key]=value
    missing=[k for k in FUNCTIONS[function][3]['required'] if k not in parameters]
    unresolved=[k for k in plan.get('unresolved_fields',[]) if k not in approved and k in FUNCTIONS[function][3]['properties']]
    plan['unresolved_fields']=list(dict.fromkeys([*missing,*unresolved]))
    if not plan['unresolved_fields']:plan['status']='ready'
    note_fields={'Die Gütermengen':'metric','Berücksichtigt':'group','Die Übersicht':'top','Die Auswertung':'direction','Verwendet':'year'}
    notes=[note for note in notes if all(not note.startswith(prefix) or (key in approved and approved[key]==defaults.get(key)) for prefix,key in note_fields.items())]
    return plan,approved,notes,years
