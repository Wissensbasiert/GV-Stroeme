"""Structured model intent -> bounded data selection; no natural-language parser."""
import copy
import json
from .contracts import FUNCTIONS, fields, validate, YEAR
from .dialogue import available_years, previous_calendar_year

TIME_KEYS = {'year', 'years', 'start', 'end', 'observed_years'}
DIALOGUE = fields(
    context={'enum': ['new', 'continue']},
    clarification={'type': 'string', 'maxLength': 600},
    time=fields(kind={'enum': ['unspecified', 'explicit', 'latest_available', 'previous_calendar_year',
                              'last_calendar_years', 'last_available_years', 'since_available']},
                count={'type': 'integer', 'minimum': 0, 'maximum': 10}))
DIALOGUE['properties']['time']['properties']['start_year'] = YEAR
DIALOGUE['properties']['geographic_scope'] = {'enum':['all','domestic','international','inherit']}


class SelectionError(ValueError):
    def __init__(self, code, message, fields=None):
        super().__init__(message)
        self.code, self.fields = code, fields or []


def tools():
    result = []
    for name, entry in FUNCTIONS.items():
        schema = copy.deepcopy(entry[3])
        schema['properties']['_dialogue'] = DIALOGUE
        schema['properties']['_dialogue'] = copy.deepcopy(DIALOGUE)
        schema['properties']['_dialogue']['required'] = [*DIALOGUE['required'],'geographic_scope']
        schema['required'] = ['_dialogue']
        result.append({'type': 'function', 'function': {'name': name,
            'description': entry[1] + '. Auch unvollständig aufrufen: Auswahl wird gespeichert; _dialogue.clarification stellt die Rückfrage.',
            'parameters': schema}})
    result.append({'type': 'function', 'function': {'name': 'clarify_request',
        'description': 'Nur wenn noch keine Datenfunktion zugeordnet werden kann. Bei bekannter Funktion diese mit Teilauswahl und Rückfrage verwenden.',
        'parameters': fields(_dialogue=DIALOGUE)}})
    return result


def validate_selection(name, args, datasets):
    if name not in FUNCTIONS or not isinstance(args, dict):
        raise SelectionError('unknown_tool', 'Welche Auswertung möchten Sie mit den vorhandenen Güterverkehrsdaten durchführen?')
    try:
        validate({**FUNCTIONS[name][3], 'required': []}, args)
    except ValueError:
        raise SelectionError('invalid_parameters', 'Die Auswahl passt noch nicht zur möglichen Auswertung. Bitte präzisieren Sie Raum, Zeitraum oder Kennzahl.') from None
    for key in ['origin', 'destination', 'region', 'regions', 'partner']:
        value = args.get(key)
        for code in value if isinstance(value, list) else [value] if value else []:
            if name=='dashboard_detail' and key=='partner' and args.get('product')=='sea_partners':
                from .access import read
                sea=read(datasets.paths['dashboard_access'],'sea.json') if 'dashboard_access' in datasets.paths else {'seaports':{}}
                countries={r['iso'] for ports in sea['seaports'].values() for p in ports.values() for r in p.get('partner_countries',[])}
                if code not in countries:
                    raise SelectionError('unknown_sea_country','Welches Partnerland des Hafens möchten Sie betrachten?', ['partner'])
                continue
            if name=='forecast_relation' and key in {'origin','destination'} and code in getattr(datasets,'forecast_cell_names',{}): continue
            if code not in datasets.names:
                raise SelectionError('unknown_region', 'Welche Stadt oder welchen Kreis meinen Sie genau?', [key])
    if name=='forecast_relation' and any(args.get(k)=='DE' for k in ['origin','destination']):
        raise SelectionError('national_forecast_endpoint','Bitte wählen Sie konkrete Prognoseregionen statt Deutschland als Relationsendpunkt.', ['origin','destination'])
    if name=='dashboard_detail' and args.get('partner') and args.get('product') not in {'sea_partners','kv_relations'}:
        raise SelectionError('unsupported_partner_filter','Dieses Datenprodukt enthält kein Partnerdetail. Möchten Sie das gesamte Regional-/Hafengüterprofil oder eine Relation betrachten?', ['partner'])
    if name == 'forecast_regions' and args.get('regions'):
        registry = json.loads((datasets.paths['b0406'] / 'regions.json').read_text(encoding='utf-8'))['2024']
        if any(code not in registry and code!='DE' for code in args['regions']):
            raise SelectionError('unsupported_forecast_region', 'Die regionale Prognose liegt für Kreise und kreisfreie Städte vor. Welche dieser Regionen möchten Sie betrachten?', ['regions'])
        if 'DE' in args['regions'] and args.get('direction','all')!='all':
            raise SelectionError('national_forecast_direction','Die nationale Prognose aus vollständigen Matrizen ist nur für Gesamtverkehr einschließlich Transit definiert. Möchten Sie direction=all betrachten?', ['direction'])
    if name in {'forecast_regions','forecast_relation'} and args.get('goods'):
        goods=args['goods']
        if ('ALL' in goods and len(goods)>1) or (any(g.startswith('VP') for g in goods) and any(g in '1234567' for g in goods)):
            raise SelectionError('overlapping_goods', 'Bitte wählen Sie entweder VP-Gütergruppen oder Hauptgruppen, ohne überlappende Gesamtwerte.', ['goods'])
        if len(goods)*len(args.get('regions',[1]))*len(args.get('modes',[1]))*len(args.get('metrics',[1]))*4 > 600:
            raise SelectionError('too_many_forecast_values','Bitte grenzen Sie Regionen, Gütergruppen oder Kennzahlen etwas ein.', ['goods'])
    if name == 'goods_history' and all(k in args for k in ['start','end','modes','directions']):
        if (15*(args['end']-args['start']+1)+16)*len(args['modes'])*len(args['directions']) > 600:
            raise SelectionError('too_many_goods_values', 'Bitte grenzen Sie Zeitraum oder Verkehrsrichtungen für die Güterauswertung etwas ein.', ['start','end','directions'])
    if 'start' in args and 'end' in args and (args['start'] > args['end'] or args['end'] - args['start'] > 9):
        raise SelectionError('invalid_period', 'Bitte wählen Sie einen zusammenhängenden Zeitraum von höchstens zehn Jahren.', ['start', 'end'])
    return args


def inherited_selection(name, state):
    old = copy.deepcopy(state.get('confirmed', {}))
    props = FUNCTIONS[name][3]['properties']
    old_function = state.get('function_id') or ''
    if name == 'forecast_regions' and old_function in {'forecast_comparison', 'region_profile', 'compare_regions'} and old.get('region'):
        old['regions'] = [old['region']]
    if old_function == 'forecast_regions' and 'region' in props and len(old.get('regions', [])) == 1:
        old['region'] = old['regions'][0]
    # Translate equivalent parameter names when the model switches data products.
    if 'origin' in props and old.get('region') and old.get('partner'):
        # A total across both directions cannot become a directed pair.
        if old.get('direction') in {'inbound', 'outbound'}:
            origin, destination = old['region'], old['partner']
            if old['direction'] == 'inbound': origin, destination = destination, origin
            old.update(origin=origin, destination=destination)
    elif 'partner' in props and old.get('origin') and old.get('destination'):
        old.update(region=old['origin'], partner=old['destination'], direction='outbound')
    modes = old.get('modes') or ([old['mode']] if old.get('mode') else
            ['rail'] if old_function.startswith('rail_goods') else ['road'] if old_function == 'road_relation_goods_limit' else [])
    if modes:
        if 'modes' in props: old['modes'] = modes
        if 'mode' in props and len(modes) == 1: old['mode'] = modes[0]
    metrics = old.get('metrics') or ([old['metric']] if old.get('metric') else [])
    if metrics:
        if 'metrics' in props: old['metrics'] = metrics
        if 'metric' in props and len(metrics) == 1: old['metric'] = metrics[0]
    if 'directions' in props and old.get('direction') in {'outbound','inbound','all'}:
        old['directions'] = [old['direction']]
    if 'direction' in props and len(old.get('directions',[])) == 1:
        old['direction'] = old['directions'][0]
    if name == 'goods_history' and old_function == 'goods_structure' and old.get('year'):
        old.update(start=old['year'],end=old['year'])
    if name == 'goods_structure' and old_function == 'goods_history' and old.get('end'):
        old['year'] = old['end']
    if 'entity' in props and old.get('region'): old['entity']=old['region']
    if 'region' in props and old.get('entity') and old.get('mode')!='sea': old['region']=old['entity']
    return {k: v for k, v in old.items() if k in props}


def resolve(name, arguments, state, datasets, explicit=None):
    args = copy.deepcopy(arguments)
    dialogue = args.pop('_dialogue', None)
    try:
        validate(DIALOGUE, dialogue)
    except ValueError:
        raise SelectionError('invalid_intent', 'Bitte beschreiben Sie noch einmal kurz, welche Auswertung Sie benötigen.') from None
    if name == 'clarify_request':
        if args or not dialogue['clarification'].strip():
            raise SelectionError('invalid_clarification', 'Was möchten Sie über die Güterverkehrsdaten wissen?')
        return None, {}, dialogue, []
    validate_selection(name, args, datasets)
    inherited = inherited_selection(name, state) if dialogue['context'] == 'continue' else {}
    if dialogue['context'] == 'continue' and dialogue['time']['kind'] == 'unspecified' and not any(k in args for k in TIME_KEYS):
        if state.get('time_intent',{}).get('kind') == 'since_available':
            dialogue['time'] = copy.deepcopy(state['time_intent'])
    kind = dialogue['time']['kind']
    if kind != 'unspecified':
        inherited = {k: v for k, v in inherited.items() if k not in TIME_KEYS}
    args = {**inherited, **args}
    notes = []
    props = FUNCTIONS[name][3]['properties']
    selected_scope = dialogue.get('geographic_scope', 'inherit')
    if selected_scope == 'inherit':
        selected_scope = state.get('confirmed',{}).get('partner_scope','all') if dialogue['context']=='continue' else args.get('partner_scope','all')
    if selected_scope != 'all' and 'partner_scope' not in props:
        pair=[args.get('origin',''),args.get('destination','')]
        # A fully specified new relation already fixes both countries. It needs no
        # additional aggregate filter, but must agree with the model's scope.
        fixed_pair=(dialogue['context']=='new' and all(pair) and
            ((selected_scope=='domestic' and all(c.startswith('DE') for c in pair)) or
             (selected_scope=='international' and sum(c.startswith('DE') for c in pair)==1)))
        if not fixed_pair:
            raise SelectionError('unsupported_geographic_scope','Für diese Auswertung kann der gewünschte Inland-/Auslandsfilter nicht angewendet werden. Bitte wählen Sie eine regionale Verkehrs- oder Güterauswertung.', ['partner_scope'])
    if 'partner_scope' in props:
        if 'partner_scope' in arguments and dialogue.get('geographic_scope') not in {None,'inherit',arguments['partner_scope']}:
            raise SelectionError('conflicting_geographic_scope','Die Angaben zum Inland-/Auslandsbezug widersprechen sich.', ['partner_scope'])
        args['partner_scope'] = arguments.get('partner_scope',selected_scope)
    for key, value in (explicit or {}).items():
        if key not in props or (key in args and args[key] != value):
            raise SelectionError('explicit_filter_conflict', 'Die verstandene Auswahl widerspricht Ihrer ausdrücklich gewählten Einstellung. Bitte bestätigen Sie die gewünschte Auswahl.')
        args[key] = value
    # Data defaults have no dependency on wording; no implicit year or place.
    defaults = {'metric': 'tonnes', 'metrics': ['tonnes'], 'group': 'ALL', 'nst': None,
                'top': 10, 'include_forecast': False, 'include_goods': True, 'granularity': 'C7'}
    if name == 'forecast_relation': defaults.update(goods=['ALL'], modes=['road','rail','iww'])
    if name == 'dashboard_detail': defaults.update(direction='all',classification='NST20' if args.get('product')=='regional_goods' else 'C7',partner=None)
    if name in {'relation_history', 'relation_overview'}: defaults['modes'] = ['road', 'rail', 'iww']
    if name == 'forecast_regions':
        defaults.update(modes=['road', 'rail', 'iww'], direction='all')
    if name == 'goods_history': defaults['modes'] = ['road','rail','iww']
    if name == 'transport_history': defaults.update(modes=['road','rail','iww'],direction='all',partner_scope='all')
    for key, value in defaults.items():
        if key in props and key not in args: args[key] = copy.deepcopy(value)
    if kind == 'since_available':
        start = dialogue['time'].get('start_year')
        if start is None or not {'start','end'} <= props.keys() or dialogue['time']['count'] != 0:
            raise SelectionError('invalid_since', 'Mit welchem Jahr soll die Zeitreihe beginnen?', ['start'])
        if any(k in arguments for k in TIME_KEYS):
            raise SelectionError('conflicting_time', 'Bitte geben Sie entweder einen festen Zeitraum oder ein Startjahr bis zum neuesten verfügbaren Jahr an.', ['start','end'])
        args['start'] = start
        # Resolve only after the region is known; preserve intent across clarification.
        if args.get('region') or (args.get('origin') and args.get('destination')):
            coverage_function = {'regional_history':'region_profile'}.get(name,name)
            years = available_years(datasets,coverage_function,args)
            if not years or max(years) < start:
                raise SelectionError('unresolved_since', 'Ab dem gewünschten Startjahr ist kein gemeinsamer Jahrgang verfügbar. Welchen Zeitraum möchten Sie betrachten?', ['start','end'])
            args['end'] = max(years)
            notes.append(f'Zeitraum: {start}–{max(years)}; bis zum neuesten gemeinsamen Datenjahr der ausgewählten Verkehrsträger. Jahrgangsabdeckung garantiert keine vollständigen Einzelwerte.')
    elif kind not in {'unspecified', 'explicit'}:
        if any(k in arguments for k in TIME_KEYS):
            raise SelectionError('conflicting_time', 'Meinen Sie bestimmte Kalenderjahre oder die neuesten verfügbaren Daten?', list(TIME_KEYS & props.keys()))
        count = dialogue['time']['count']
        previous = previous_calendar_year()
        if kind in {'last_calendar_years', 'last_available_years'} and not 1 <= count <= 10:
            raise SelectionError('invalid_count', 'Wie viele Jahre möchten Sie betrachten?')
        if kind == 'previous_calendar_year': years = [previous]
        elif kind == 'last_calendar_years': years = list(range(previous-count+1, previous+1))
        else:
            coverage_function = {'rail_goods_history': 'rail_goods', 'regional_history': 'region_profile',
                                 'modal_history': 'region_profile', 'forecast_comparison': 'region_profile'}.get(name, name)
            available = available_years(datasets, coverage_function, args)
            if not available:
                raise SelectionError('unresolved_availability', 'Für welchen konkreten Zeitraum möchten Sie diese Auswertung?', list(TIME_KEYS & props.keys()))
            years = available[-1:] if kind == 'latest_available' else available[-count:]
            if kind == 'last_available_years' and len(years) != count:
                raise SelectionError('insufficient_years', f'Es sind weniger als {count} gemeinsame Jahrgänge verfügbar. Welchen kürzeren Zeitraum möchten Sie betrachten?')
        if 'year' in props and len(years) == 1: args['year'] = years[0]
        elif 'start' in props and 'end' in props:
            if years != list(range(min(years), max(years)+1)):
                raise SelectionError('noncontiguous_years', 'Die verfügbaren Jahre bilden keinen durchgehenden Zeitraum. Welche Jahre möchten Sie vergleichen?')
            args.update(start=min(years), end=max(years))
        elif 'years' in props: args['years'] = years
        elif 'observed_years' in props: args['observed_years'] = years
        else:
            raise SelectionError('wrong_time_product', 'Für diesen Zeitraum ist eine andere Auswertung nötig. Möchten Sie eine Zeitreihe betrachten?')
        wording = 'abgeschlossene Kalenderjahre' if kind == 'last_calendar_years' else 'verfügbare Datenjahre'
        notes.append(('Zeitraum: ' + str(min(years)) + '–' + str(max(years)) + ' (' + wording + ').') if len(years) > 1
                     else 'Bezugsjahr: ' + str(years[0]) + (' (vorheriges Kalenderjahr).' if kind in {'previous_calendar_year', 'last_calendar_years'} else ' (neuester verfügbarer Jahrgang).'))
    validate_selection(name, args, datasets)
    for key, value in (explicit or {}).items():
        if key not in props or (key in args and args[key] != value):
            raise SelectionError('explicit_filter_conflict', 'Die verstandene Auswahl widerspricht Ihrer ausdrücklich gewählten Einstellung. Bitte bestätigen Sie die gewünschte Auswahl.')
        args[key] = value
    validate_selection(name, args, datasets)
    return name, args, dialogue, notes
