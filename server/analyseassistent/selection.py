"""Structured model intent -> bounded data selection; no natural-language parser."""
import copy
from .contracts import FUNCTIONS, fields, validate
from .dialogue import available_years, previous_calendar_year

TIME_KEYS = {'year', 'years', 'start', 'end', 'observed_years'}
DIALOGUE = fields(
    context={'enum': ['new', 'continue']},
    clarification={'type': 'string', 'maxLength': 600},
    time=fields(kind={'enum': ['unspecified', 'explicit', 'latest_available', 'previous_calendar_year',
                              'last_calendar_years', 'last_available_years']},
                count={'type': 'integer', 'minimum': 0, 'maximum': 10}))


class SelectionError(ValueError):
    def __init__(self, code, message, fields=None):
        super().__init__(message)
        self.code, self.fields = code, fields or []


def tools():
    result = []
    for name, entry in FUNCTIONS.items():
        schema = copy.deepcopy(entry[3])
        schema['properties']['_dialogue'] = DIALOGUE
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
            if code not in datasets.names:
                raise SelectionError('unknown_region', 'Welche Stadt oder welchen Kreis meinen Sie genau?', [key])
    if 'start' in args and 'end' in args and (args['start'] > args['end'] or args['end'] - args['start'] > 9):
        raise SelectionError('invalid_period', 'Bitte wählen Sie einen zusammenhängenden Zeitraum von höchstens zehn Jahren.', ['start', 'end'])
    return args


def inherited_selection(name, state):
    old = copy.deepcopy(state.get('confirmed', {}))
    props = FUNCTIONS[name][3]['properties']
    old_function = state.get('function_id') or ''
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
    kind = dialogue['time']['kind']
    if kind != 'unspecified':
        inherited = {k: v for k, v in inherited.items() if k not in TIME_KEYS}
    args = {**inherited, **args}
    notes = []
    props = FUNCTIONS[name][3]['properties']
    for key, value in (explicit or {}).items():
        if key not in props or (key in args and args[key] != value):
            raise SelectionError('explicit_filter_conflict', 'Die verstandene Auswahl widerspricht Ihrer ausdrücklich gewählten Einstellung. Bitte bestätigen Sie die gewünschte Auswahl.')
        args[key] = value
    # Data defaults have no dependency on wording; no implicit year or place.
    defaults = {'metric': 'tonnes', 'metrics': ['tonnes'], 'group': 'ALL', 'nst': None,
                'top': 10, 'include_forecast': False, 'include_goods': True, 'granularity': 'C7'}
    if name in {'relation_history', 'relation_overview'}: defaults['modes'] = ['road', 'rail', 'iww']
    for key, value in defaults.items():
        if key in props and key not in args: args[key] = copy.deepcopy(value)
    if kind not in {'unspecified', 'explicit'}:
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
