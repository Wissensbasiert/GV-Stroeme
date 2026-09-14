"""Native Datenwerkzeuge und begrenzter signierter Dialog mit belegtem Freitext."""
import copy
import json
import re
import time

from .contracts import FUNCTIONS, fields, validate, explicit_conflict, directed_pairs, question_supports
from .conversation import pack, unpack
from .dialogue import previous_calendar_year, complete_plan, available_years, LATEST, PREVIOUS_YEAR
from .narrative import evidence
from .presentation import present
from .requesty import ModelError
from .results import limited

RESPONSE = fields(paragraphs={'type': 'array', 'minItems': 1, 'maxItems': 4, 'items': fields(
    text={'type': 'string', 'minLength': 1, 'maxLength': 800},
    evidence_ids={'type': 'array', 'minItems': 1, 'maxItems': 6, 'uniqueItems': True,
                  'items': {'type': 'string'}})})
NUMBER = re.compile(r'(?<![\w])[-+]?\d+(?:\.\d{3})*(?:,\d+)?(?![\w])')
YEAR = re.compile(r'\b(?:19|20)\d{2}\b')


def numbers(text):
    return {round(float(m.group().replace('.', '').replace(',', '.')), 6) for m in NUMBER.finditer(text)}


def tool_specs():
    # Partial arguments are allowed by the transport; the server decides what is
    # missing before any query. Dataset schemas themselves remain strict.
    return [{'type': 'function', 'function': {'name': name, 'description': entry[1],
            'parameters': {**entry[3], 'required': []}}} for name, entry in FUNCTIONS.items()]


def packet(result, datasets):
    answer = result['answer']
    records = evidence(result, answer)
    # Unlike the legacy narrative, row facts remain available for a free account
    # of the requested years. They are never substituted for a missing endpoint.
    facts = {f['fact_id']: f for f in result.get('facts', [])}
    for table in answer['tables']:
        for row in table['rows'][:30]:
            for key in row.get('fact_ids', []):
                records[key] = row['label'] + ': ' + row['value'] + ' ' + row['unit'] + '. ' + row.get('note', '')
    structured = {}
    for key, text in records.items():
        item = {'text': text}
        if key in facts:
            item.update({k: facts[key][k] for k in ['value', 'unit', 'year', 'mode', 'origin', 'destination',
                        'source_status', 'quality_status', 'source'] if k in facts[key]})
        structured[key] = item
    params = result.get('parameters', {})
    scope = {k: params[k] for k in params}
    for key in ['origin', 'destination', 'region', 'partner']:
        if scope.get(key) in datasets.names:
            scope[key] = {'code': scope[key], 'name': min(datasets.names[scope[key]], key=len)}
    return {'status': result['status'], 'scope': scope, 'evidence': structured,
            'questions': answer.get('questions', []),
            'instructions': 'Antworte frei mit eigenen Sätzen und exakten Zahlen aus den Belegen. '
            'Jeder Absatz nennt nur seine verwendeten evidence_ids. Werte gehören zu ihrem Jahr, '
            'ihrer Richtung und Einheit. Keine Platzhalter. Keine selbst berechneten Zahlen. '
            'Die Tabelle und nötigen Qualitätsgrenzen werden zusätzlich angezeigt; wiederhole sie nicht vollständig.'}


def check_prose(selection, payload, result, datasets):
    """Bounded checks, explicitly not a complete semantic proof of free language."""
    validate(RESPONSE, selection)
    rendered = []
    params = result.get('parameters', {})
    facts = payload['evidence']
    for paragraph in selection['paragraphs']:
        text, ids = paragraph['text'], paragraph['evidence_ids']
        if any(key not in facts for key in ids) or re.search(r'[<>]|\{\{|https?://', text):
            raise ValueError('Ungültiger Beleg oder Ausgabeformat')
        cited = [facts[key] for key in ids]
        allowed_text = ' '.join(f['text'] for f in cited)
        allowed_numbers = numbers(allowed_text)
        # Scope years may be named, but never used to relabel another year's value.
        allowed_numbers |= {float(y) for y in YEAR.findall(json.dumps(params))}
        if not numbers(text) <= allowed_numbers:
            raise ValueError('Zahl fehlt in den zugeordneten Belegen')
        quantity = re.compile(r'([-+]?\d+(?:\.\d{3})*(?:,\d+)?)\s*(Tonnenkilometer|Tonnen|tkm|TEU|%|t)(?!\w)', re.I)
        unit_names = {'tonnen': 't', 'tonnenkilometer': 'tkm', 'teu': 'teu', 'tkm': 'tkm', 't': 't', '%': '%'}
        def quantities(value):
            return {(next(iter(numbers(m.group(1)))), unit_names[m.group(2).lower()]) for m in quantity.finditer(value.replace('**', '').replace('*', ''))}
        if not quantities(text) <= quantities(allowed_text):
            raise ValueError('Zahl und Einheit sind nicht gemeinsam belegt')
        for sentence in re.split(r'(?<=[!?])\s+|(?<!\d)\.\s+(?=[A-ZÄÖÜ])', text):
            years = {int(y) for y in YEAR.findall(sentence)}
            numeric = numbers(sentence)
            for f in result.get('facts', []):
                if f.get('value') is None or not f.get('year'):
                    continue
                values = {round(float(f['value']), 6)}
                if numeric & values and years and f['year'] not in years:
                    raise ValueError('Zahl und Bezugsjahr widersprechen sich')
            if re.search(r'\b(?:Tonnenkilometer|tkm)\b', sentence, re.I):
                if not any(f.get('unit') == 'tkm' or re.search(r'Tonnenkilometer|tkm', f['text'], re.I) for f in cited):
                    raise ValueError('Einheit widerspricht den Belegen')
            affirmative_zero = re.search(r'\b(?:ist|war|bleibt)\s+(?:vollständig\s+)?verkehrsfrei\b|\b(?:gab|gibt)\s+es\s+keinen?\s+Verkehr\b', sentence, re.I)
            if affirmative_zero and not re.search(r'\b(?:nicht|keineswegs|beweist|bedeutet|schließen)\b', sentence, re.I):
                raise ValueError('Fehlwert darf keinen Nullverkehr begründen')
        checked_text = text
        if not any(f.get('value') is not None for f in result.get('facts', [])):
            # Describing a verified available year is not a substituted analysis.
            for year in YEAR.findall(allowed_text):
                checked_text = re.sub(r'\b' + year + r'\b', '', checked_text)
        if re.search(r'\bAlternativ\w*\b', text, re.I):
            alternative_years = {str(c['parameters']['year']) for c in result.get('related_data', {}).get('checks', {}).values()
                                 if c.get('available') and c.get('parameters', {}).get('year')}
            for year in alternative_years:
                checked_text = re.sub(r'\b' + year + r'\b', '', checked_text)
        answer_scope = dict(params)
        if params.get('region') and params.get('partner'):
            pair = (params['region'], params['partner'])
            if params.get('direction') == 'inbound': pair = pair[::-1]
            answer_scope.update(origin=pair[0], destination=pair[1])
        allowed_modes = set(params.get('modes', []) or ([params['mode']] if params.get('mode') else []))
        if result.get('function_id') in {'rail_goods', 'rail_goods_history'}: allowed_modes = {'rail'}
        if result.get('function_id') in {'road_relation_goods_limit', 'road_details'}: allowed_modes = {'road'}
        mentioned_modes = {m for m in ['road', 'rail', 'iww'] if question_supports(checked_text, m, {})}
        if allowed_modes and not mentioned_modes <= allowed_modes:
            raise ValueError('Verkehrsträger widerspricht den Belegen')
        if explicit_conflict(checked_text, answer_scope, datasets.names):
            raise ValueError('Antwort widerspricht der abgefragten Auswahl')
        if any(f.get('source_status') == 'missing_row' for f in result.get('facts', [])):
            if re.search(r'\b(?:liegt|liegen)\b[^.!?]{0,35}\b(?:an|daran)\b|\b(?:ist|sind)\b[^.!?]{0,55}\bzurückzuführen\b', text, re.I):
                raise ValueError('Konkrete Ursache der fehlenden Relationszeile ist nicht belegt')
        # Do not ban causal conjunctions: methodological explanations need them.
        unsupported = r'\b(?:Standortvorteil|Verlagerungspotenzial|freie Kapazität|Werksschließung|Betriebsschließung)\w*'
        if re.search(unsupported, text, re.I) and not re.search(unsupported, allowed_text, re.I):
            raise ValueError('Unbelegte fachliche Zusatzbehauptung')
        rendered.append(text)
    return rendered


def validate_arguments(name, args, question, state, datasets):
    if name not in FUNCTIONS or not isinstance(args, dict):
        raise ValueError('Datenwerkzeug nicht zugelassen')
    schema = FUNCTIONS[name][3]
    validate({**schema, 'required': []}, args)
    if explicit_conflict(question, args, datasets.names):
        raise ValueError('Werkzeugauswahl widerspricht der Frage')
    # Names and route endpoints must be grounded in current input or signed
    # conversation. A new pair must not inherit an old endpoint.
    current = directed_pairs(question, datasets.names, [])
    old = state.get('confirmed', {}) if state else {}
    if args.get('year') and not YEAR.search(question):
        relative = re.search(r'aktuell|neueste|letzte[srn]? Jahr|Vorjahr', question, re.I)
        if not relative and (args['year'] != old.get('year') or current):
            raise ValueError('Bitte das gewünschte Jahr ergänzen')
    if args.get('origin') and args.get('destination'):
        pair = (args['origin'], args['destination'])
        oldpair = (old.get('origin') or old.get('region'), old.get('destination') or old.get('partner'))
        if old.get('direction') == 'inbound':
            oldpair = oldpair[::-1]
        if current and current != {pair}:
            raise ValueError('Verkehrsrichtung widerspricht der Frage')
        if not current and pair != oldpair:
            reverse = re.search(r'gegenrichtung|umgekehrt|andersherum|zurück|rückrichtung', question, re.I)
            if not (reverse and pair == oldpair[::-1]):
                raise ValueError('Verbindung nicht im Gespräch belegt')
    history_text = '\n'.join(m['content'] for m in (state or {}).get('messages', []) if m['role'] == 'user')
    for key in ['region', 'regions', 'origin', 'destination', 'partner', 'node', 'ags']:
        value = args.get(key)
        for code in value if isinstance(value, list) else [value] if value else []:
            if not question_supports(question + '\n' + history_text, code, datasets.names):
                if code not in [old.get(k) for k in ['region', 'origin', 'destination', 'partner', 'node', 'ags']]:
                    raise ValueError('Raumauswahl nicht im Gespräch belegt')
    return args


def analyze_chat(service, question, confirmed=None, *, function=None, history=None, conversation=None, progress=None):
    if not isinstance(question, str) or not question.strip() or len(question) > 4000:
        raise ValueError('Frage muss zwischen 1 und 4.000 Zeichen enthalten')
    if confirmed is not None and (not isinstance(confirmed, dict) or len(json.dumps(confirmed)) > 12000):
        raise ValueError('Ungültige Filter')
    from .service import Service
    started = time.monotonic()
    deadline = started + service.timeout_seconds
    state = unpack(conversation, service.conversation_key, service.datasets.snapshot_id) if conversation else {}
    turns = state.get('messages', [])
    if not turns and history:
        turns = [{'role': 'user', 'content': q} for q in history[-6:]]
    audit = {'prompt_sha256': service.prompt_sha256, 'rules_sha256': service.rules_sha256,
             'data_snapshot_id': service.datasets.snapshot_id, 'model_calls': [],
             'attempted_model_calls': 0, 'planning_mode': 'native_tools', 'tool_calls': []}
    emit = progress or (lambda event: None)
    emit({'stage': 'understanding', 'text': 'Ich ordne Ihre Frage und den Gesprächsverlauf ein …'})
    name_context = question + ' ' + ' '.join(m['content'] for m in turns if m['role'] == 'user') + ' ' + json.dumps(state.get('confirmed', {}), ensure_ascii=False)
    names = {code: aliases for code, aliases in service.datasets.names.items()
             if any(n.casefold() in name_context.casefold()
                    for n in [code, *aliases])}
    context = {'available_data': service.catalog, 'region_names': names,
               'confirmed_selection': state.get('confirmed', {}), 'previous_calendar_year': previous_calendar_year(),
               'explicit_filters': confirmed or {}}
    messages = [{'role': 'system', 'content': service.prompt},
                {'role': 'system', 'content': 'Aktueller geprüfter Kontext: ' + json.dumps(context, ensure_ascii=False)},
                *turns, {'role': 'user', 'content': question}]
    result = None
    selected = {}

    def call(**kwargs):
        audit['attempted_model_calls'] += 1
        message, usage = service.model.chat(messages, deadline=deadline, **kwargs)
        audit['model_calls'].append(usage)
        return message

    def finish():
        result.setdefault('answer', present(result, service.datasets))
        short = '\n\n'.join(result['answer'].get('paragraphs', []) + result['answer'].get('questions', []))
        new_turns = [*turns, {'role': 'user', 'content': question}, {'role': 'assistant', 'content': short[:2200]}][-8:]
        while sum(len(m['content']) for m in new_turns) > 8000 and len(new_turns) > 2:
            new_turns = new_turns[2:]
        next_state = {'version': 2, 'snapshot': service.datasets.snapshot_id, 'issued': time.time(),
                      'messages': new_turns, 'confirmed': selected, 'function_id': result.get('function_id'),
                      'initial_question': question[:1000], 'effective_question': question[:1000],
                      'missing_fields': result.get('missing_fields', []), 'open_question': result['answer'].get('questions', []),
                      'last_result': {'status': result['status'], 'result_id': result.get('result_id')}}
        result['conversation'] = pack(next_state, service.conversation_key)
        result['conversation_state'] = {k: next_state[k] for k in ['confirmed', 'function_id', 'missing_fields']}
        audit['total_ms'] = round((time.monotonic()-started)*1000)
        return result, audit

    try:
        if function:
            first = {'role': 'assistant', 'content': None, 'tool_calls': [{'id': 'explicit_selection', 'type': 'function',
                     'function': {'name': function, 'arguments': json.dumps(confirmed or {})}}]}
        else:
            first = call(tools=tool_specs())
        calls = first.get('tool_calls', [])
        if not calls:
            text = (first.get('content') or '').strip()
            # A no-tool turn can clarify, never publish unqueried traffic facts.
            if not text or len(text) > 1000 or numbers(text) - {float(y) for y in YEAR.findall(json.dumps(context))}:
                raise ValueError('Unbelegte Antwort ohne Datenabfrage')
            if re.search(r'Tonnen|transportiert|beträgt|Prozent|\d\s*%', text, re.I):
                raise ValueError('Ergebnisbehauptung ohne Datenabfrage')
            result = limited('needs_clarification', text)
            result['answer'] = present(result, service.datasets)
            result['answer']['paragraphs'] = [text]
            result['answer']['questions'] = []
            selected = dict(state.get('confirmed', {}))
            pairs = directed_pairs(question, service.datasets.names, [])
            if len(pairs) == 1:
                origin, destination = next(iter(pairs))
                selected = {'origin': origin, 'destination': destination}
                modes = [m for m in ['road', 'rail', 'iww'] if question_supports(question, m, {})]
                if modes: selected['modes'] = modes
            return finish()
        if len(calls) != 1:
            raise ValueError('Bitte eine zusammengehörige Auswertung je Frage wählen')
        messages.append(first)
        tool = calls[0]
        name = tool['function']['name']
        args = json.loads(tool['function']['arguments'])
        if name not in FUNCTIONS or not isinstance(args, dict):
            raise ValueError('Ungültiger Werkzeugaufruf')
        audit['proposed_tool'] = {'name': name, 'parameters': copy.deepcopy(args)}
        old = state.get('confirmed', {})
        pair = (args.get('origin') or args.get('region'), args.get('destination') or args.get('partner'))
        oldpair = (old.get('origin') or old.get('region'), old.get('destination') or old.get('partner'))
        if not function and all(pair) and pair in {oldpair, oldpair[::-1]}:
            for key in ['year', 'modes', 'metrics', 'metric', 'include_goods', 'group']:
                if key not in args and key in old and key in FUNCTIONS.get(name, (None, None, None, {'properties': {}}))[3]['properties']:
                    if key == 'year' and (YEAR.search(question) or LATEST.search(question) or PREVIOUS_YEAR.search(question)):
                        continue
                    args[key] = copy.deepcopy(old[key])
        if not function:
            validate_arguments(name, args, question, state, service.datasets)
        else:
            validate({**FUNCTIONS[name][3], 'required': []}, args)
        # Keep data defaults and availability resolution in the existing server.
        plan = {'phase': 'plan', 'function_id': name, 'parameters': args,
                'parameter_origins': {k: 'context' for k in args}, 'unresolved_fields': [], 'status': 'ready'}
        plan, _, _, _ = complete_plan(plan, question, args.copy(), service.datasets)
        args = plan['parameters']
        if 'year' in FUNCTIONS[name][3]['properties']:
            if LATEST.search(question):
                years = available_years(service.datasets, name, args)
                if years: args['year'] = max(years)
            elif PREVIOUS_YEAR.search(question) and not YEAR.search(question):
                args['year'] = previous_calendar_year()
        selected = args
        missing = [k for k in FUNCTIONS[name][3]['required'] if k not in args]
        if missing:
            result = limited('needs_clarification', 'Bitte ergänzen Sie die fehlende Auswahl.', missing_fields=missing)
            result['function_id'] = name
            result['answer'] = present(result, service.datasets)
        else:
            emit({'stage': 'data', 'text': 'Ich lese die passenden Güterverkehrsdaten …'})
            data_service = Service(service.datasets, timeout_seconds=max(1, min(600, deadline-time.monotonic())))
            result, data_audit = data_service.analyze(question, args, function=name, select_answer=False)
            states = {f.get('source_status') for f in result.get('facts', [])}
            if len(states) == 1 and states <= {'not_available', 'missing_row', 'suppressed'}:
                result['status'], result['source_status'] = 'not_available', next(iter(states))
                result['answer'] = present(result, service.datasets)
            audit['lookup_ms'] = data_audit.get('lookup_ms', 0)
            audit['tool_calls'].append({'name': name, 'parameters': args, 'status': result['status']})
        payload = packet(result, service.datasets)
        if not payload['evidence']:
            payload['evidence'] = {'q1': {'text': ' '.join(result['answer'].get('questions', []) or result['answer']['paragraphs'])}}
        messages.append({'role': 'tool', 'tool_call_id': tool['id'], 'content': json.dumps(payload, ensure_ascii=False)})
        emit({'stage': 'answer', 'text': 'Die Daten liegen vor. Ich formuliere und prüfe die Antwort …'})
        try:
            final = call(schema=RESPONSE)
            selection = json.loads(final.get('content') or '')
            audit['answer_evidence'] = selection
            result['answer']['paragraphs'] = check_prose(selection, payload, result, service.datasets)
            result['answer']['questions'] = []
            result['answer_mode'] = 'native_grounded_chat'
            for text in result['answer']['paragraphs']:
                emit({'stage': 'paragraph', 'text': text})
        except (ModelError, ValueError, TypeError, KeyError) as exc:
            audit['narrative_error'] = str(exc)
            if isinstance(exc, ModelError): audit['narrative_error_diagnostics'] = exc.diagnostics
            result['answer_mode'] = 'verified_fallback'
        # Tables are rendered from the original facts, never from model Markdown.
        for table in result['answer']['tables']:
            table['collapsed'] = len(table['rows']) > 4
        return finish()
    except (ModelError, ValueError, TypeError, KeyError) as exc:
        audit['chat_error'] = str(exc)
        if isinstance(exc, ModelError):
            audit['model_error_diagnostics'] = exc.diagnostics
        result = limited('error', 'Die Frage konnte noch nicht sicher ausgewertet werden. Bitte nennen Sie Verbindung, Jahr und Verkehrsträger möglichst konkret.')
        result['diagnostic_code'] = 'AA-C01'
        selected = state.get('confirmed', {})
        return finish()
