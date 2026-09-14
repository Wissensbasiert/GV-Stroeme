"""Native Datenwerkzeuge und begrenzter signierter Dialog mit belegtem Freitext."""
import copy
import json
import re
import time
import duckdb

from .contracts import FUNCTIONS, fields, validate, explicit_conflict, question_supports, qualified_region_mentions, directed_pairs
from .conversation import pack, unpack
from .dialogue import previous_calendar_year
from .narrative import evidence
from .presentation import present, number
from .requesty import ModelError
from .results import limited, make_result, compact_value
from .alternatives import related_data
from .selection import tools, resolve, validate_selection, SelectionError

RESPONSE = fields(paragraphs={'type': 'array', 'minItems': 1, 'maxItems': 4, 'items': fields(
    text={'type': 'string', 'minLength': 1, 'maxLength': 800},
    evidence_ids={'type': 'array', 'minItems': 1, 'maxItems': 6, 'uniqueItems': True,
                  'items': {'type': 'string'}})})
NUMBER = re.compile(r'(?<![\w])[-+]?\d+(?:\.\d{3})*(?:,\d+)?(?![\w])')
YEAR = re.compile(r'\b(?:19|20)\d{2}\b')


def numbers(text):
    return {round(float(m.group().replace('.', '').replace(',', '.')), 6) for m in NUMBER.finditer(text)}


def tool_specs():
    return tools()


def packet(result, datasets):
    answer = result['answer']
    records = evidence(result, answer)
    # Unlike the legacy narrative, row facts remain available for a free account
    # of the requested years. They are never substituted for a missing endpoint.
    facts = {f['fact_id']: f for f in result.get('facts', [])}
    for table in answer['tables']:
        for row in (table['rows'] if result.get('function_id') in {'dashboard_detail','forecast_relation','compare_regions','forecast_regions','partner_ranking','node_partners'} else table['rows'][:30]):
            for key in row.get('fact_ids', []):
                records[key] = row['label'] + ': ' + row['value'] + ' ' + row['unit'] + '. ' + row.get('note', '')
    if result.get('function_id') == 'relation_history':
        labels = {'missing_row': 'kein eigener veröffentlichter Eintrag für diese Verbindung',
                  'not_available': 'Jahrgang für diese Auswahl nicht verfügbar', 'suppressed': 'Wert unterdrückt'}
        modes = {'road': 'Straße', 'rail': 'Schiene', 'iww': 'Binnenschiff'}
        for mode, label in modes.items():
            for status, description in labels.items():
                years = sorted({f['year'] for f in facts.values() if f.get('mode') == mode
                                and f.get('source_status') == status and f.get('year')})
                if years:
                    records['coverage_' + mode + '_' + status] = label + ', Jahre ' + ', '.join(map(str, years)) + ': ' + description + '.'
    structured = {}
    for key, text in records.items():
        if key in facts and result.get('function_id')=='dashboard_detail' and facts[key].get('group') not in {None,'ALL'}:
            classification=result['parameters']['classification']
            text=('NST 2007, NST-20 Abteilung ' if classification=='NST20' else 'NST 2007, C7 Gruppe ')+facts[key]['group']+': '+text
        item = {'text': text}
        if key.startswith('p') and key[1:].isdigit():
            statement=next((s for s in result.get('statements',[]) if s['text']==text),None)
            if statement: item['fact_ids']=statement['fact_ids']
        if key in facts:
            item.update({k: facts[key][k] for k in ['value', 'unit', 'year', 'mode', 'origin', 'destination',
                        'region', 'region_name', 'metric', 'scenario', 'direction', 'basis',
                        'source_status', 'quality_status', 'source','group','group_name'] if k in facts[key]})
        structured[key] = item
    if result.get('function_id') in {'forecast_regions','compare_regions'}:
        groups = {}
        for fact in facts.values():
            if not fact.get('region'): continue
            groups.setdefault((fact['region'], fact.get('mode'), fact.get('metric'),fact.get('group')), []).append(fact)
        for i, ((region, mode, metric, goods), group) in enumerate(groups.items(), 1):
            structured[('forecast_group_' if result['function_id']=='forecast_regions' else 'profile_group_') + str(i)] = {
                'text': ' '.join(structured[f['fact_id']]['text'] for f in group),
                'region': region, 'mode': mode, 'metric': metric, 'group':goods,
                'basis': 'VP2019_BASE_to_2040_P1' if result['function_id']=='forecast_regions' else 'observed_profile',
                'fact_ids': [f['fact_id'] for f in group]}
    if result.get('function_id') in {'partner_ranking','node_partners'}:
        ranked=[f for f in facts.values() if f.get('partner_id')]
        structured['partner_group']={'text':' '.join(structured[f['fact_id']]['text'] for f in ranked),
                                     'fact_ids':[f['fact_id'] for f in ranked]}
    params = result.get('parameters', {})
    scope = {k: params[k] for k in params}
    for key in ['origin', 'destination', 'region', 'partner']:
        if scope.get(key) in datasets.names:
            scope[key] = {'code': scope[key], 'name': min(datasets.names[scope[key]], key=len)}
    if params.get('regions'):
        scope['regions'] = [{'code': code, 'name': min(datasets.names[code], key=len)} for code in params['regions']]
    return {'status': result['status'], 'scope': scope, 'evidence': structured,
            'questions': answer.get('questions', []),
            'instructions': 'Antworte frei mit eigenen Sätzen und exakten Zahlen aus den Belegen. '
            'Jeder Absatz nennt nur seine verwendeten evidence_ids. Werte gehören zu ihrem Jahr, '
            'ihrer Richtung und Einheit. Keine Platzhalter. Keine selbst berechneten Zahlen. '
            'Bei Prognosevergleichen nutze die forecast_group-Belege: Sie enthalten jeweils Basis, Ziel und beide Veränderungen einer Region, eines Verkehrsträgers und einer Kennzahl. '
            'Bei Partner-Ranglisten nutze partner_group für mehrere Mengen und Anteile im selben Absatz. '
            'Bei regionalen Güterzeitreihen beantworte beide Teile: führende Gütergruppen im Endjahr mit Mengen/Anteilen und die Entwicklung seit dem Startjahr. Behandle jeden ausgewählten Verkehrsträger, auch konkrete Datenlücken. '
            'Ordne die Ergebnisse in verständlichen Absätzen ein. Ein kurzer Satz genügt bei mehrteiligen Fragen nicht. '
            'Die Tabelle und nötigen Qualitätsgrenzen werden zusätzlich angezeigt; wiederhole sie nicht vollständig.'}


def check_prose(selection, payload, result, datasets):
    """Bounded checks, explicitly not a complete semantic proof of free language."""
    validate(RESPONSE, selection)
    rendered = []
    params = result.get('parameters', {})
    facts = payload['evidence']
    for paragraph in selection['paragraphs']:
        text, ids = paragraph['text'], paragraph['evidence_ids']
        if (result.get('parameters',{}).get('goods') or result.get('function_id')=='dashboard_detail') and any(f.get('value') is not None for f in result.get('facts',[])):
            if re.search(r'(?:keine|nicht)\s+(?:\w+\s+){0,5}(?:Aufteilung|Güteraufteilung|Gütergruppenwerte|Gütergliederung)|(?:Gütergruppen|Güterarten).{0,50}(?:nicht verfügbar|liegen nicht vor)',text,re.I):
                raise ValueError('Vorhandene Güterdaten dürfen nicht pauschal als fehlend bezeichnet werden')
        if any(key not in facts for key in ids) or re.search(r'[<>]|\{\{|https?://', text):
            raise ValueError('Ungültiger Beleg oder Ausgabeformat')
        cited = [facts[key] for key in ids]
        allowed_text = ' '.join(f['text'] for f in cited)
        allowed_numbers = numbers(allowed_text)
        # Scope years may be named, but never used to relabel another year's value.
        allowed_numbers |= {float(y) for y in YEAR.findall(json.dumps(params))}
        if not numbers(text) <= allowed_numbers:
            raise ValueError('Zahl fehlt in den zugeordneten Belegen')
        quantity = re.compile(r'([-+]?\d+(?:\.\d{3})*(?:,\d+)?)\s*(Mio\.|Tsd\.)?\s*(Tonnenkilometer|Tonnen|tkm|TEU|%|t)(?!\w)', re.I)
        unit_names = {'tonnen': 't', 'tonnenkilometer': 'tkm', 'teu': 'teu', 'tkm': 'tkm', 't': 't', '%': '%'}
        def quantities(value):
            return {(round(next(iter(numbers(m.group(1)))) * (1000000 if m.group(2)=='Mio.' else 1000 if m.group(2)=='Tsd.' else 1),6), unit_names[m.group(3).lower()]) for m in quantity.finditer(value.replace('**', '').replace('*', ''))}
        if not quantities(text) <= quantities(allowed_text):
            raise ValueError('Zahl und Einheit sind nicht gemeinsam belegt')
        for sentence in re.split(r'(?<=[!?])\s+|(?<!\d)(?<!Mio)(?<!Tsd)\.\s+(?=[A-ZÄÖÜ])', text):
            if result.get('function_id')=='road_relation_goods_limit' and quantities(sentence):
                if any(question_supports(sentence,mode,{}) for mode in ['rail','iww']):
                    raise ValueError('Alternative Verkehrsträger dürfen keine Straßenmenge übernehmen')
            if result.get('function_id') in {'forecast_regions','compare_regions'}:
                mentioned = qualified_region_mentions(sentence,datasets.names)
                if not mentioned <= set(params['regions']):
                    raise ValueError('Region fehlt in der abgefragten Auswahl')
                if len(mentioned) == 1:
                    region_facts = [f for f in result['facts'] if f.get('region') in mentioned]
                    allowed_region_quantities = {(round(float(f['value']), 6), unit_names.get(f['unit'].lower(), f['unit'].lower()))
                                                 for f in region_facts if f['value'] is not None}
                    # Match the same rounding used by the customer presentation.
                    allowed_region_quantities |= {(next(iter(numbers(number(f['value'])))), unit_names.get(f['unit'].lower(), f['unit'].lower()))
                                                  for f in region_facts if f['value'] is not None}
                    allowed_region_quantities |= {q for f in region_facts if f['value'] is not None for q in quantities(compact_value(f['value'],f['unit']))}
                    if not quantities(sentence) <= allowed_region_quantities:
                        raise ValueError('Zahl und Region sind nicht gemeinsam belegt')
                elif len(mentioned)>1:
                    regional_quantities={q for f in result['facts'] if f.get('region') in mentioned and f['value'] is not None for q in quantities(compact_value(f['value'],f['unit'])) | quantities(number(f['value'])+' '+f['unit'])}
                    if quantities(sentence) & regional_quantities:
                        raise ValueError('Mehrere Regionen mit Mengen bitte in getrennten Sätzen zuordnen')
            if result.get('function_id')=='relation_matrix':
                pairs=directed_pairs(sentence,datasets.names,[params['origin'],params['destination']])
                if quantities(sentence):
                    if len(pairs)!=1: raise ValueError('Relationsmenge ohne eindeutige Richtung')
                    pair=next(iter(pairs))
                    matching=[f for f in result['facts'] if (f.get('origin'),f.get('destination'))==pair and f['value'] is not None]
                    allowed={q for f in matching for q in quantities(number(f['value'])+' '+f['unit']) | quantities(compact_value(f['value'],f['unit']))}
                    if not quantities(sentence)<=allowed: raise ValueError('Menge und Relationsrichtung widersprechen sich')
            years = {int(y) for y in YEAR.findall(re.sub(r'\bNST[-\s]*2007\b','NST',sentence,flags=re.I))}
            numeric = numbers(sentence)
            cited_fact_ids=set(ids) | {fid for item in cited for fid in item.get('fact_ids',[])}
            year_facts=[f for f in result.get('facts',[]) if f.get('fact_id') in cited_fact_ids]
            # Compatibility payloads without IDs still have structured row metadata.
            year_facts += [f for f in cited if f.get('year') and 'value' in f]
            for f in result.get('facts', []):
                if f.get('value') is None or not f.get('year'):
                    continue
                values = {round(float(f['value']), 6)}
                if numeric & values and years and f['year'] not in years:
                    if not any(other.get('year') in years and other.get('value')==f['value'] and other.get('unit')==f['unit'] for other in year_facts):
                        raise ValueError('Zahl und Bezugsjahr widersprechen sich')
            if re.search(r'\b(?:Tonnenkilometer|tkm)\b', sentence, re.I):
                if not any(f.get('unit') == 'tkm' or re.search(r'Tonnenkilometer|tkm', f['text'], re.I) for f in cited):
                    raise ValueError('Einheit widerspricht den Belegen')
            affirmative_zero = re.search(r'\b(?:ist|war|bleibt)\s+(?:vollständig\s+)?verkehrsfrei\b|\b(?:gab|gibt)\s+es\s+keinen?\s+Verkehr\b', sentence, re.I)
            if affirmative_zero and not re.search(r'\b(?:nicht|keineswegs|beweist|bedeutet|schließen)\b', sentence, re.I):
                raise ValueError('Fehlwert darf keinen Nullverkehr begründen')
        # NST-2007 is the classification edition, not the observation year.
        # Actual year statements (including 2007) retain the existing scope gate.
        checked_text = re.sub(r'\bNST[-\s]*2007\b','NST',text,flags=re.I)
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
        if result.get('function_id') == 'road_relation_goods_limit':
            allowed_modes |= {c.get('parameters',{}).get('mode',key) for key,c in result.get('related_data',{}).get('checks',{}).items()
                              if key in {'rail','iww'} and c.get('status')!='not_checked'}
        mentioned_modes = {m for m in ['road', 'rail', 'iww'] if question_supports(checked_text, m, {})}
        if allowed_modes and not mentioned_modes <= allowed_modes:
            raise ValueError('Verkehrsträger widerspricht den Belegen')
        # Mode restrictions above also account for verified alternative-data notices.
        answer_scope.pop('mode',None)
        if result.get('function_id') == 'partner_ranking':
            allowed_regions={params['region']} | {f.get('partner_id') for f in result.get('facts',[]) if f.get('fact_id') in cited_fact_ids}
            if not qualified_region_mentions(checked_text,datasets.names) <= allowed_regions:
                raise ValueError('Partnername fehlt in den zugeordneten Belegen')
            answer_scope.pop('region',None)
        if result.get('function_id') == 'relation_matrix':
            pair=(params['origin'],params['destination'])
            if not directed_pairs(checked_text,datasets.names,list(pair)) <= {pair,pair[::-1]}:
                raise ValueError('Richtung fehlt in der abgefragten Auswahl')
            answer_scope.pop('origin',None)
            answer_scope.pop('destination',None)
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
    if result.get('function_id')=='goods_history':
        text=' '.join(rendered)
        used={key for paragraph in selection['paragraphs'] for key in paragraph['evidence_ids']}
        covered=used | {fid for key in used for fid in facts[key].get('fact_ids',[])}
        for mode in params['modes']:
            if not question_supports(text,mode,{}):
                raise ValueError('Güterantwort lässt einen ausgewählten Verkehrsträger aus')
            for direction in params['directions']:
                series=[f for f in result['facts'] if f.get('mode')==mode and f.get('direction')==direction]
                required=[f for f in series if not f.get('group') and f.get('year') in {params['start'],params['end']} and f['unit']!='%']
                latest=[f for f in series if f.get('year')==params['end'] and f.get('group') and f['unit']!='%']
                known=[f for f in latest if f['value'] is not None]
                required+= [max(known,key=lambda f:f['value'])] if known else latest
                required+=[f for f in series if not f.get('group') and f.get('change')=='relative']
                if any(f['fact_id'] not in covered for f in required):
                    raise ValueError('Güterantwort belegt Rangfolge, Randjahre oder Vergleichsgrenze nicht vollständig')
                for f in required:
                    if f['value'] is not None:
                        variants=[numbers(number(f['value'])),numbers(compact_value(f['value'],f['unit']))]
                        if not any(value <= numbers(text) for value in variants):
                            raise ValueError('Güterantwort lässt führende Menge oder Jahresentwicklung aus')
        if not {params['start'],params['end']} <= {int(y) for y in YEAR.findall(text)}:
            raise ValueError('Güterantwort lässt den Vergleichszeitraum aus')
    if result.get('function_id')=='compare_regions':
        text=' '.join(rendered)
        used={key for paragraph in selection['paragraphs'] for key in paragraph['evidence_ids']}
        covered=used | {fid for key in used for fid in facts[key].get('fact_ids',[])}
        for region in params['regions']:
            selected=[f for f in result['facts'] if f.get('region')==region]
            required=[f for f in selected if not f.get('group') and f['unit']!='%']
            groups=[f for f in selected if f.get('group') and f['unit']!='%' and f['value'] is not None]
            if groups: required.append(max(groups,key=lambda f:f['value']))
            if any(f['fact_id'] not in covered for f in required):
                raise ValueError('Regionsvergleich belegt Güteraufkommen, Verkehrsträger oder führende Gütergruppe nicht vollständig')
            for f in required:
                options=[f]
                if f.get('mode'): options += [s for s in selected if s.get('mode')==f['mode'] and s['unit']=='%']
                if f['value'] is not None and not any(value <= numbers(text) for option in options if option['value'] is not None for value in [numbers(number(option['value'])),numbers(compact_value(option['value'],option['unit']))]):
                    raise ValueError('Regionsvergleich lässt einen angefragten Ergebnisbereich aus')
    if result.get('function_id')=='relation_matrix':
        used={key for paragraph in selection['paragraphs'] for key in paragraph['evidence_ids']}
        covered=used | {fid for key in used for fid in facts[key].get('fact_ids',[])}
        if any(f['fact_id'] not in covered for f in result['facts']):
            raise ValueError('Relationsantwort belegt beide Richtungen und Verkehrsträger nicht vollständig')
    return rendered


def validate_arguments(name, args, question, state, datasets):
    # Compatibility entry point: language interpretation belongs to the model.
    return validate_selection(name, args, datasets)


def analyze_chat(service, question, confirmed=None, *, function=None, history=None, conversation=None, progress=None):
    if not isinstance(question, str) or not question.strip() or len(question) > 4000:
        raise ValueError('Frage muss zwischen 1 und 4.000 Zeichen enthalten')
    if confirmed is not None and (not isinstance(confirmed, dict) or len(json.dumps(confirmed)) > 12000):
        raise ValueError('Ungültige Filter')
    started = time.monotonic()
    deadline = started + service.timeout_seconds
    try:
        state = unpack(conversation, service.conversation_key, service.datasets.snapshot_id) if conversation else {}
    except ValueError:
        result = limited('needs_clarification', 'Der bisherige Gesprächsstand ist abgelaufen. Bitte nennen Sie Ihre gewünschte Auswertung noch einmal.')
        result['answer'] = present(result, service.datasets)
        result['answer']['paragraphs'] = result['notices']
        return result, {'failure_stage': 'conversation', 'error_kind': 'expired_context', 'model_calls': [], 'attempted_model_calls': 0}
    turns = state.get('messages', [])
    if not turns and history:
        turns = [{'role': 'user', 'content': q} for q in history[-6:]]
    audit = {'prompt_sha256': service.prompt_sha256, 'rules_sha256': service.rules_sha256,
             'data_snapshot_id': service.datasets.snapshot_id, 'model_calls': [],
             'attempted_model_calls': 0, 'planning_mode': 'native_tools', 'tool_calls': []}
    emit = progress or (lambda event: None)
    emit({'stage': 'understanding', 'text': 'Ich ordne Ihre Frage und den Gesprächsverlauf ein …'})
    # The compact complete registry permits synonyms, spelling variants and
    # indirect place references; no exact-name gate before model understanding.
    names = service.datasets.names
    context = {'available_data': service.catalog, 'region_names': names,
               'airport_names': service.datasets.airport_names,
               'confirmed_selection': state.get('confirmed', {}), 'previous_function': state.get('function_id'),
               'previous_time_intent': state.get('time_intent', {}),
               'previous_calendar_year': previous_calendar_year(),
               'explicit_filters': confirmed or {}}
    messages = [{'role': 'system', 'content': service.prompt},
                {'role': 'system', 'content': 'Aktueller geprüfter Kontext: ' + json.dumps(context, ensure_ascii=False)},
                *turns, {'role': 'user', 'content': question}]
    result = None
    selected = {}
    stage = 'understanding'
    selected_function = None
    new_topic = False
    time_intent = {}

    def call(**kwargs):
        audit['attempted_model_calls'] += 1
        message, usage = service.model.chat(messages, deadline=deadline, **kwargs)
        audit['model_calls'].append(usage)
        return message

    def finish():
        if 'answer' not in result: result['answer'] = present(result, service.datasets)
        short = '\n\n'.join(result['answer'].get('paragraphs', []) + result['answer'].get('questions', []))
        new_turns = [*turns, {'role': 'user', 'content': question}, {'role': 'assistant', 'content': short[:2200]}][-8:]
        while sum(len(m['content']) for m in new_turns) > 8000 and len(new_turns) > 2:
            new_turns = new_turns[2:]
        next_state = {'version': 3, 'snapshot': service.datasets.snapshot_id, 'issued': time.time(),
                      'messages': new_turns, 'confirmed': selected, 'function_id': result.get('function_id'),
                      'time_intent': time_intent,
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
                     'function': {'name': function, 'arguments': json.dumps({**(confirmed or {}), '_dialogue': {
                         'context': 'new', 'clarification': '', 'time': {'kind': 'explicit', 'count': 0}}})}}]}
        else:
            first = call(tools=tool_specs())
        calls = first.get('tool_calls', [])
        if len(calls) != 1:
            raise SelectionError('invalid_tool_count', 'Welche zusammengehörige Auswertung möchten Sie zuerst betrachten?')
        messages.append(first)
        tool = calls[0]
        name = tool['function']['name']
        args = json.loads(tool['function']['arguments'])
        stage = 'selection'
        if not isinstance(args, dict):
            raise SelectionError('invalid_parameters', 'Bitte beschreiben Sie die gewünschte Auswertung noch einmal kurz.')
        audit['proposed_tool'] = {'name': name, 'parameters': copy.deepcopy(args)}
        new_topic = isinstance(args.get('_dialogue'), dict) and args['_dialogue'].get('context') == 'new'
        name, args, dialogue, notes = resolve(name, args, state, service.datasets, explicit=confirmed)
        time_intent = copy.deepcopy(dialogue['time'])
        selected, selected_function = args, name
        audit['conversation_transition'] = dialogue['context']
        if name is None and dialogue['context'] == 'continue':
            selected, selected_function = state.get('confirmed', {}), state.get('function_id')
            if time_intent.get('kind')=='unspecified': time_intent=state.get('time_intent',{})
        missing = [k for k in FUNCTIONS[name][3]['required'] if k not in args] if name else []
        if missing or dialogue['clarification'] or name is None:
            result = limited('needs_clarification', 'Bitte ergänzen Sie die fehlende Auswahl.', missing_fields=missing)
            result.update(function_id=selected_function, parameters=selected)
            result['answer'] = present(result, service.datasets)
            if not dialogue['clarification'] and missing and set(missing) <= {'year', 'years', 'start', 'end'}:
                route = ''
                if selected.get('origin') and selected.get('destination'):
                    labels = [min(service.datasets.names[c], key=len) for c in [selected['origin'], selected['destination']]]
                    route = ' für die Verbindung von ' + labels[0] + ' nach ' + labels[1]
                result['answer']['paragraphs'] = ['Welches Jahr oder welchen Zeitraum möchten Sie' + route + ' betrachten?']
                result['answer']['questions'] = []
            if dialogue['clarification']:
                text = dialogue['clarification'].strip()
                if re.search(r'[<>]|\d[\d.,]*\s*(?:Tonnen|tkm|%|TEU)\b', text, re.I):
                    raise SelectionError('invalid_clarification', 'Bitte ergänzen Sie die noch fehlende Auswahl.', missing)
                result['answer']['paragraphs'] = [text]
                result['answer']['questions'] = []
            result['answer_mode'] = 'native_grounded_chat'
            return finish()
        emit({'stage': 'data', 'text': 'Ich lese die passenden Güterverkehrsdaten …'})
        stage = 'data_lookup'
        lookup_started = time.monotonic()
        raw = service.datasets.query(name, args, timeout_seconds=max(0.001, deadline-time.monotonic()))
        audit['lookup_ms'] = round((time.monotonic()-lookup_started)*1000)
        if time.monotonic() > deadline: raise TimeoutError('Datenfrist erreicht')
        stage = 'result_build'
        result = make_result(name, args, raw, service.datasets, service.rules['version'])
        states = {f.get('source_status') for f in result.get('facts', [])}
        if len(states) == 1 and states <= {'not_available', 'missing_row', 'suppressed'}:
            result['status'], result['source_status'] = 'not_available', next(iter(states))
        related = related_data(result, service.datasets, deadline=deadline)
        if related is not None: result['related_data'] = related
        result['answer'] = present(result, service.datasets)
        result['answer']['notes'] = list(dict.fromkeys([*notes, *result['answer']['notes']]))
        if name == 'relation_history':
            result['answer']['notes'].append('Diese Zeitreihe enthält Gesamtmengen je Verkehrsträger; keine jährliche Güterartenaufteilung.')
        audit['tool_calls'].append({'name': name, 'parameters': args, 'status': result['status']})
        payload = packet(result, service.datasets)
        if not payload['evidence']:
            payload['evidence'] = {'q1': {'text': ' '.join(result['answer'].get('questions', []) or result['answer']['paragraphs'])}}
        messages.append({'role': 'tool', 'tool_call_id': tool['id'], 'content': json.dumps(payload, ensure_ascii=False)})
        emit({'stage': 'answer', 'text': 'Die Daten liegen vor. Ich formuliere und prüfe die Antwort …'})
        stage = 'answer'
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
    except SelectionError as exc:
        audit.update(failure_stage='selection', error_kind=exc.code)
        result = limited('needs_clarification', str(exc), missing_fields=exc.fields)
        result.update(function_id=selected_function or (None if new_topic else state.get('function_id')))
        result['answer'] = present(result, service.datasets)
        result['answer']['paragraphs'], result['answer']['questions'] = [str(exc)], []
        selected = selected or ({} if new_topic else state.get('confirmed', {}))
        return finish()
    except (ModelError, ValueError, TypeError, KeyError, OSError, duckdb.Error) as exc:
        audit['chat_error'] = str(exc)
        audit.update(failure_stage=stage, error_kind=type(exc).__name__)
        if isinstance(exc, ModelError):
            audit['model_error_diagnostics'] = exc.diagnostics
        result = limited('error', 'Die Auswertung konnte technisch nicht abgeschlossen werden.')
        result['diagnostic_code'] = 'AA-M01' if isinstance(exc, ModelError) else {
            'data_lookup': 'AA-D02', 'result_build': 'AA-R01'}.get(stage, 'AA-F01')
        result['function_id'] = state.get('function_id')
        selected = state.get('confirmed', {})
        return finish()
