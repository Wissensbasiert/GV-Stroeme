"""Signierter, begrenzter Gesprächsstand; Ergebniswerte werden stets neu abgefragt."""
import base64
import copy
import hashlib
import hmac
import json
import re
import time
from .contracts import FUNCTIONS, question_supports, directed_pairs
from .dialogue import YEAR, LATEST, PREVIOUS_YEAR, MULTI_YEAR


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
    # Subject-preserving refinements can be full sentences, not just canned replies.
    pairs=directed_pairs(text,datasets.names,[])
    route_origin=old.get('origin') or old.get('region')
    route_destination=old.get('destination') or old.get('partner')
    if old.get('direction')=='inbound':route_origin,route_destination=route_destination,route_origin
    named={code for code in datasets.names if question_supports(text,code,datasets.names)}
    same_route=pairs=={(route_origin,route_destination)}
    refers_back=bool(re.search(r'\b(?:auch|weiterhin|dazu|dabei|dieselbe|dieser|diese|noch|stattdessen|zusätzlich)\b|^\s*(?:und|was ist mit)\b',text,re.I))
    requested_metrics=[m for m in ['tonnes','tkm'] if question_supports(text,m,{})]
    requested_modes=[m for m in ['road','rail','iww'] if question_supports(text,m,{})]
    goods=bool(re.search(r'\bgüter(?:art\w*|grupp\w*)\b',text,re.I))
    goods_change=bool(re.search(r'\b(?:entwickel\w*|veränder\w*|verlor\w*|verlust\w*|gewinn\w*|zunahm\w*|abnahm\w*|anstieg\w*|rückgang\w*)\b',text,re.I))
    classification='NST20' if re.search(r'\bNST(?:[- ]?20)?\b|\b20\s+(?:NST[- ]?)?(?:Gruppen|Abteilungen)\b',text,re.I) else 'C7'
    # A metric-only question without another place is itself a contextual
    # refinement, even if the user omits words such as "auch" or "dazu".
    refers_back=refers_back or bool((requested_metrics or goods) and not named)
    relation_functions={'relation','relation_matrix','relation_history','relation_overview','road_relation_goods_limit','rail_goods','rail_goods_history'}
    refinement=(refers_back and (requested_metrics or requested_modes or goods or same_route or YEAR.search(text))
        and (not named or named<={route_origin,route_destination}) and (not pairs or same_route)
        and not re.search(r'\b(?:national\w*|luftfracht|prognose|kosten|emission\w*)\b',text,re.I))
    if refinement and (requested_metrics or requested_modes or goods or same_route) and function in relation_functions and route_origin and route_destination:
        modes=old.get('modes') or ([old['mode']] if old.get('mode') else ['rail'] if function.startswith('rail_goods') else ['road'] if function=='road_relation_goods_limit' else ['road','rail','iww'])
        metrics=old.get('metrics') or [old.get('metric','tonnes')]
        metrics=list(dict.fromkeys([*metrics,*requested_metrics])) if re.search(r'\b(?:auch|zusätzlich)\b',text,re.I) else requested_metrics or metrics
        comparison_years=old.get('years') or ([old['start'],old['end']] if old.get('start') is not None and old.get('end') is not None else None)
        if goods and goods_change and modes==['rail'] and comparison_years:
            parameters={'region':route_origin,'partner':route_destination,'years':comparison_years,
                        'direction':'outbound','metric':metrics[0],'classification':classification}
            return state['effective_question']+'\n'+text,parameters,'rail_goods_history','refinement'
        parameters={'origin':route_origin,'destination':route_destination,'modes':requested_modes or modes,'metrics':metrics,
            'include_goods':old.get('include_goods',function in {'rail_goods','rail_goods_history','road_relation_goods_limit'}) or goods}
        if old.get('year'):parameters['year']=old['year']
        # Old time wording must not override an explicit correction.
        effective=state['effective_question']
        if YEAR.search(text) or PREVIOUS_YEAR.search(text) or LATEST.search(text):
            parameters.pop('year',None)
            effective=PREVIOUS_YEAR.sub('',LATEST.sub('',YEAR.sub('',effective)))
        if function=='relation_history':effective=MULTI_YEAR.sub('',effective)
        return effective+'\n'+text,parameters,'relation_overview','refinement'
    if refinement and function not in relation_functions and not named and not goods:
        properties=FUNCTIONS[function][3]['properties']
        parameters=copy.deepcopy(old)
        if len(requested_metrics)==1 and 'metric' in properties:parameters['metric']=requested_metrics[0]
        elif requested_metrics:return question,{},None,'new_topic'
        if len(requested_modes)==1 and 'mode' in properties:parameters['mode']=requested_modes[0]
        elif requested_modes:return question,{},None,'new_topic'
        effective=state['effective_question']
        if YEAR.search(text) or PREVIOUS_YEAR.search(text) or LATEST.search(text):
            parameters.pop('year',None)
            effective=PREVIOUS_YEAR.sub('',LATEST.sub('',YEAR.sub('',effective)))
        # Remove the previous selected mode/metric wording before replacing it.
        from .contracts import ALIASES
        for key,values in [('mode',requested_modes),('metric',requested_metrics)]:
            if values and old.get(key)!=parameters.get(key):
                for word in [old.get(key,''),*ALIASES.get(old.get(key),[])]:
                    if word:effective=re.sub(r'(?<!\w)'+re.escape(word)+r'(?!\w)','',effective,flags=re.I)
        return effective+'\n'+text,parameters,function,'refinement'
    reverse = bool(re.fullmatch(r'(?:und\s+)?(?:in\s+)?(?:der\s+)?(?:gegenrichtung|umgekehrt)[?!. ]*', text, re.I))
    year_reply = bool(re.fullmatch(r'(?:und\s+|für\s+|im\s+)?(?:19|20)\d{2}[?!. ]*', text, re.I) or
                      ((LATEST.search(text) or PREVIOUS_YEAR.search(text)) and len(text) < 70 and not pairs))
    if reverse or year_reply:
        parameters = copy.deepcopy(old)
        effective = state['effective_question']
        if year_reply:
            parameters.pop('year', None)
            effective = PREVIOUS_YEAR.sub('', LATEST.sub('', YEAR.sub('', effective))) + '\n' + text
            if function=='relation_history':
                function='relation_overview'
                parameters={'origin':route_origin,'destination':route_destination,'modes':old['modes'],
                    'metrics':[old['metric']],'include_goods':bool(re.search(r'\bgüter\w*',effective,re.I))}
                effective=MULTI_YEAR.sub('',effective)
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
        return state['effective_question'] + '\n' + text, copy.deepcopy(old), function, 'clarification_reply'
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
