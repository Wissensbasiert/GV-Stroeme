"""Signierter, begrenzter Gesprächsstand; Ergebniswerte werden stets neu abgefragt."""
import base64
import copy
import hashlib
import hmac
import json
import re
import time
from .contracts import FUNCTIONS, question_supports, directed_pairs
from .dialogue import YEAR, LATEST


def pack(state, key):
    body = base64.urlsafe_b64encode(json.dumps(state, ensure_ascii=False, separators=(',', ':')).encode()).decode()
    return body + '.' + hmac.new(key, body.encode(), hashlib.sha256).hexdigest()


def unpack(token, key, snapshot):
    if not isinstance(token, str) or len(token) > 24000:
        raise ValueError('Ungültiger Gesprächsstand')
    try:
        body, signature = token.rsplit('.', 1)
        if not hmac.compare_digest(signature, hmac.new(key, body.encode(), hashlib.sha256).hexdigest()):
            raise ValueError()
        state = json.loads(base64.urlsafe_b64decode(body))
        if state['snapshot'] != snapshot or time.time() - state['issued'] > 7200:
            raise ValueError()
        return state
    except (ValueError, KeyError, TypeError):
        raise ValueError('Gesprächsstand ist abgelaufen oder nicht mehr gültig') from None


def resume(question, state, datasets):
    """Nur eindeutige Ergänzungen erben Angaben; selbständige Anliegen beginnen neu."""
    if not state:
        return question, {}, None, 'new_topic'
    old = state.get('confirmed', {})
    function = state.get('function_id')
    if function not in FUNCTIONS:
        return question, {}, None, 'new_topic'
    text = question.strip()
    reverse = bool(re.fullmatch(r'(?:und\s+)?(?:in\s+)?(?:der\s+)?(?:gegenrichtung|umgekehrt)[?!. ]*', text, re.I))
    year_reply = bool(re.fullmatch(r'(?:und\s+|für\s+|im\s+)?(?:19|20)\d{2}[?!. ]*', text, re.I) or
                      (LATEST.search(text) and len(text) < 70 and not directed_pairs(text, datasets.names, [])))
    if reverse or year_reply:
        parameters = copy.deepcopy(old)
        effective = state['effective_question']
        if year_reply:
            parameters.pop('year', None)
            effective = LATEST.sub('', YEAR.sub('', effective)) + '\n' + text
        else:
            if parameters.get('origin') and parameters.get('destination'):
                parameters['origin'], parameters['destination'] = parameters['destination'], parameters['origin']
            elif parameters.get('partner') and parameters.get('direction') in {'outbound', 'inbound'}:
                parameters['direction'] = 'inbound' if parameters['direction'] == 'outbound' else 'outbound'
            else:
                return question, {}, None, 'ambiguous_followup'
            # Reconstruct only the changed route; old directional wording must not survive.
            origin = parameters.get('origin') or parameters.get('region')
            destination = parameters.get('destination') or parameters.get('partner')
            if parameters.get('direction') == 'inbound': origin, destination = destination, origin
            mode = parameters.get('mode', 'rail' if function == 'rail_goods' else 'road')
            effective = f'Welche Güter von {origin} nach {destination} per {mode}?'
            if parameters.get('year'): effective += ' ' + str(parameters['year'])
        return effective, parameters, function, 'reverse' if reverse else 'year'
    # An answer to an actual open field may be short; a named new route always resets.
    missing = state.get('missing_fields', [])
    if missing and len(text) < 100 and not re.search(r'\b(welche|wie|zeige|vergleiche|warum)\b', text, re.I) and not directed_pairs(text, datasets.names, []):
        return state['effective_question'] + '\n' + text, copy.deepcopy(old), None, 'clarification_reply'
    return question, {}, None, 'new_topic'


def confirmed_parameters(plan, approved, question, names):
    if not plan or plan.get('function_id') not in FUNCTIONS:
        return {}
    # Only independently evidenced fields enter the signed state, even on a clarification.
    result = {}
    for key, value in plan.get('parameters', {}).items():
        if key in approved and type(value) is type(approved[key]) and value == approved[key]:
            result[key] = value
        elif plan.get('parameter_origins', {}).get(key) == 'question' and question_supports(question, value, names):
            if key not in {'origin', 'destination'} or directed_pairs(question, names, []) == {(plan['parameters'].get('origin'), plan['parameters'].get('destination'))}:
                result[key] = value
    return result
