"""Positivlisten und überprüfbare Parameterherkunft ohne Modellvertrauen."""
import re
from jsonschema import Draft202012Validator


def enum(*values):
    return {'enum': list(values)}


YEAR = {'type': 'integer', 'minimum': 1900, 'maximum': 2100}
CODE = {'type': 'string', 'pattern': '^[A-Za-z0-9_ -]{2,80}$'}
REGIONS = {'type': 'array', 'items': CODE, 'minItems': 1, 'maxItems': 20, 'uniqueItems': True}
MODE = enum('road', 'rail', 'iww')
METRIC = enum('tonnes', 'tkm', 'trips', 'load_units', 'load_carriers', 'teu', 'flights')
GROUP = enum('ALL', '1', '2', '3', '4', '5', '6', '7')
DIRECTION = enum('outbound', 'inbound', 'all', 'total')
TOP = {'type': 'integer', 'minimum': 1, 'maximum': 100}


def fields(**properties):
    return {'type': 'object', 'properties': properties,
            'required': list(properties), 'additionalProperties': False}


# All parameters are explicit. Defaults in the underlying local functions cannot
# silently replace a missing user selection.
FUNCTIONS = {
    'relation_overview': ('F07', 'Gerichtete Jahresrelation: Menge und/oder Verkehrsleistung sowie verfügbare C1–C7-Güterarten je Verkehrsträger; Straße nur Gesamtwerte', 'b01', fields(
        origin=CODE,destination=CODE,year=YEAR,
        modes={'type':'array','items':MODE,'minItems':1,'maxItems':3,'uniqueItems':True},
        metrics={'type':'array','items':enum('tonnes','tkm'),'minItems':1,'maxItems':2,'uniqueItems':True},
        include_goods={'type':'boolean'})),
    'road_relation_goods_limit': ('F07', 'Verfügbare Straßen-OD-Gesamtmenge mit ausdrücklicher Grenze fehlender Güterstruktur', 'b01', fields(
        origin=CODE,destination=CODE,year=YEAR,metric=enum('tonnes','tkm'))),
    'rail_goods_history': ('F07', 'Schienen-Feinpositionen derselben Relation in zwei bestätigten Jahren, keine ungeprüften Raten', 'b03', fields(
        region=CODE,partner=CODE,years={'type':'array','items':YEAR,'minItems':2,'maxItems':2,'uniqueItems':True},
        direction=enum('outbound','inbound'),metric=enum('tonnes','tkm'))),
    'explain_scope': ('F15', 'Quellen-, Klassifikations- und Machbarkeitsgrenzen als belegte Hinweise', 'b03', fields(
        topic=enum('classification','source_flags','regional_vs_national','outside_scope','road_goods_depth'))),
    'goods_structure': ('F06', 'Regionale C1–C7-Güterstruktur je Verkehrsträger; keine künstliche NST-20-Aufteilung', 'assistant_support', fields(
        region=CODE,year=YEAR,mode=MODE,metric=enum('tonnes','tkm'),
        directions={'type':'array','items':enum('all','outbound','inbound'),'minItems':1,'maxItems':3,'uniqueItems':True},
        granularity=enum('C7','NST20'))),
    'goods_history': ('F06', 'Regionale C1–C7-Güterstruktur und Entwicklung über bis zu zehn Jahre für mehrere Verkehrsträger, getrennte Mengen, Anteile und berechnete Randjahresveränderungen; keine Relationsgüter und keine harmonisierte Zeitreihe', 'assistant_support', fields(
        region=CODE,start=YEAR,end=YEAR,
        modes={'type':'array','items':MODE,'minItems':1,'maxItems':3,'uniqueItems':True},
        metric=enum('tonnes','tkm'),
        directions={'type':'array','items':enum('all','outbound','inbound'),'minItems':1,'maxItems':3,'uniqueItems':True})),
    'intermodal_markets': ('F11', 'Getrennte KV-Teilmärkte mit jeweils passendem Modalnenner, ohne Verlagerungspotenzial', 'assistant_support', fields(
        region=CODE,year=YEAR,modes={'type':'array','items':enum('rail','iww'),'minItems':1,'maxItems':2,'uniqueItems':True},
        metrics={'type':'array','items':enum('tonnes','tkm'),'minItems':1,'maxItems':2,'uniqueItems':True},
        direction=enum('all','outbound','inbound','internal'))),
    'node_profile': ('F12', 'Knotenprofil mit getrennten Kennzahlen und sichtbaren Jahrgangslücken', 'b0406', fields(
        kind=enum('air','sea'),node=CODE,year=YEAR,direction=enum('all','outbound','inbound'),
        metrics={'type':'array','items':enum('tonnes','teu','flights'),'minItems':1,'maxItems':2,'uniqueItems':True})),
    'regional_history': ('F04', 'Regionale Ist-Jahresscheiben mit Quellenjahresprüfung und Vergleichbarkeitsgrenzen', 'b0406', fields(
        region=CODE,start=YEAR,end=YEAR,mode=MODE,metric=enum('tonnes','tkm'),direction=enum('all','outbound','inbound'))),
    'modal_history': ('F08', 'Regionale Modalanteile für ausdrücklich gewählte Jahre; fehlende Modi bleiben unbekannt', 'b0406', fields(
        region=CODE,years={'type':'array','items':YEAR,'minItems':1,'maxItems':3,'uniqueItems':True},
        metric=enum('tonnes','tkm'),direction=enum('all','outbound','inbound'))),
    'relation_matrix': ('F02', 'Konkrete Verbindung in beiden Richtungen, drei Verkehrsträger getrennt', 'b01', fields(
        origin=CODE, destination=CODE, year=YEAR, metric=enum('tonnes', 'tkm'))),
    'relation_history': ('F04', 'Gerichtete Verbindung über mehrere Jahre; verfügbare Verkehrsträger getrennt und ohne künstliche Gesamtsumme', 'b01', fields(
        origin=CODE, destination=CODE, start=YEAR, end=YEAR,
        modes={'type':'array','items':MODE,'minItems':1,'maxItems':3,'uniqueItems':True},
        metric=enum('tonnes','tkm'))),
    'partner_ranking': ('F02', 'Alle veröffentlichten Partner vor Top-Begrenzung, Gleichstände und Quellenflags', 'b01', fields(
        region=CODE, year=YEAR, mode=MODE, metric=enum('tonnes','tkm'), direction=enum('all','outbound','inbound'),
        group=GROUP, top=TOP, external={'type':'boolean'})),
    'region_profile': ('F01', 'Vollständiges D01-Regionalprofil, optional getrennte VP-Werte', 'b0406', fields(
        region=CODE, year=YEAR, metric=enum('tonnes', 'tkm'), include_forecast={'type': 'boolean'})),
    'regional_modal_split': ('F08', 'Regionale Verkehrsanteile bei vollständigem passendem Nenner', 'b0406', fields(
        region=CODE, year=YEAR, metric=enum('tonnes', 'tkm'), direction=enum('all', 'outbound', 'inbound'))),
    'forecast_regions': ('F10', 'Reine Prognoseentwicklung 2019_BASE zu 2040_P1 für eine bis fünf Regionen, mehrere Kennzahlen und Verkehrsträger; keine beobachteten Jahre erforderlich, keine Verbindung zwischen den Regionen', 'b0406', fields(
        regions={**REGIONS, 'maxItems': 5},
        modes={'type': 'array', 'items': MODE, 'minItems': 1, 'maxItems': 3, 'uniqueItems': True},
        metrics={'type': 'array', 'items': enum('tonnes', 'tkm'), 'minItems': 1, 'maxItems': 2, 'uniqueItems': True},
        direction=enum('all', 'outbound', 'inbound'))),
    'forecast_comparison': ('F10', 'Zusätzlich ausdrücklich gewünschte beobachtete Ist-Jahre neben VP2019_BASE/2040_P1 für eine Region; reine Prognosefragen und mehrere Regionen über forecast_regions', 'b0406', fields(
        region=CODE, metric=enum('tonnes', 'tkm'), direction=enum('all', 'outbound', 'inbound'),
        observed_years={'type': 'array', 'items': YEAR, 'minItems': 1, 'maxItems': 3, 'uniqueItems': True})),
    'toll_month': ('F13', 'Gespeicherte Berliner Mautfahrten; fehlender Vorjahresmonat bleibt offen', 'b07', fields(
        ags={'type': 'string', 'pattern': '^\\d{8}$'}, month={'type': 'string', 'pattern': '^20\\d{2}-(0[1-9]|1[0-2])$'},
        comparison_month={'anyOf': [{'type': 'string', 'pattern': '^20\\d{2}-(0[1-9]|1[0-2])$'}, {'type': 'null'}]})),
    'relation': ('F02', 'Exakte Quelle-Ziel-Verbindung, keine Rangliste', 'b01', fields(
        year=YEAR, origin=CODE, destination=CODE, mode=MODE, group=GROUP, metric=METRIC)),
    'compare_regions': ('F03', 'Vergleich ganzer Kreise mit D01-Profilgrenzen', 'b0406', fields(
        regions=REGIONS, year=YEAR, metric=enum('tonnes', 'tkm'), direction=enum('all', 'outbound', 'inbound'))),
    'union': ('F03', 'Innen-/Außenverkehr eines bestätigten Verbunds ganzer Kreise', 'b0406', fields(
        regions=REGIONS, year=YEAR, mode=MODE, metric=enum('tonnes', 'tkm'), group=GROUP)),
    'time_series': ('F04', 'Veröffentlichte Monatsreihen, keine ungeprüfte harmonisierte Änderungsrate', 'b02', fields(
        region=CODE, mode=MODE, direction=enum('outbound', 'inbound', 'total'), start=YEAR, end=YEAR,
        group=GROUP, metric=METRIC, partner={'anyOf': [CODE, {'type': 'null'}]})),
    'rail_goods': ('F07', 'Veröffentlichte Schienen-Feinpositionen', 'b03', fields(
        year=YEAR, region=CODE, direction=enum('outbound', 'inbound', 'total'),
        partner={'anyOf': [CODE, {'type': 'null'}]}, nst={'anyOf': [{'type': 'string', 'pattern': '^[0-9]{2}[0-9A-Z]$'}, {'type': 'null'}]},
        group=GROUP, metric=enum('tonnes', 'tkm', 'load_units'))),
    'national': ('F08', 'Nationale Verkehrsbeziehungen und nur bei vollständigem Nenner Anteile', 'b0406', fields(
        year=YEAR, metric=enum('tonnes', 'tkm'), mode={'anyOf': [MODE, {'type': 'null'}]})),
    'balance': ('F09', 'Versand, Empfang und Saldo eines Kreises', 'b0406', fields(
        region=CODE, year=YEAR, mode=MODE, metric=enum('tonnes', 'tkm'))),
    'forecast_ranking': ('F10', 'Ranking VP2019_BASE zu 2040_P1, keine Ist-Entwicklung', 'b0406', fields(
        mode=MODE, metric=enum('tonnes', 'tkm'), direction=enum('all', 'outbound', 'inbound'),
        measure=enum('absolute', 'relative'), top=TOP, descending={'type': 'boolean'})),
    'node_partners': ('F12', 'Veröffentlichte Hafen-/Flughafenpartner mit passendem Teilmengennenner', 'b0406', fields(
        kind=enum('air', 'sea'), node=CODE, year=YEAR, direction=enum('all', 'outbound', 'inbound'),
        metric=enum('tonnes', 'teu', 'flights'), international={'type': 'boolean'}, top=TOP)),
    'node_statistics': ('F12', 'Hafen-/Flughafenkennzahl mit ausdrücklicher Einheit', 'b0406', fields(
        kind=enum('air', 'sea'), node=CODE, year=YEAR, direction=enum('all', 'outbound', 'inbound'), metric=enum('tonnes', 'teu', 'flights'))),
    'road_details': ('F14', 'VD2-Entfernungen oder VD3c-Güter in amtlicher Raum-/Fahrzeugabgrenzung', 'b03', fields(
        product=enum('VD2', 'VD3c'), year=YEAR, region=CODE, direction=enum('outbound', 'inbound'),
        population=enum('I', 'G'), metric=enum('tonnes', 'tkm', 'trips'), partner={'type': 'null'})),
}

PLAN = fields(phase=enum('plan'), function_id={'anyOf': [enum(*FUNCTIONS), {'type': 'null'}]},
              parameters={'type': 'object'}, parameter_origins={'type': 'object', 'additionalProperties': enum('context', 'question')},
              unresolved_fields={'type': 'array', 'items': {'type': 'string', 'maxLength': 60}, 'maxItems': 20},
              status=enum('ready', 'needs_clarification', 'not_available', 'out_of_scope'))
ANSWER_PARAGRAPH = fields(
    text={'type':'string','minLength':1,'maxLength':900},
    statement_ids={'type':'array','items':{'type':'string'},'minItems':1,'maxItems':6,'uniqueItems':True})
ANSWER = fields(result_id={'type': 'string'}, data_snapshot_id={'type': 'string'},
                paragraphs={'type':'array','items':ANSWER_PARAGRAPH,'minItems':1,'maxItems':3},
                table_ids={'type': 'array', 'items': {'type': 'string'}, 'maxItems': 20, 'uniqueItems': True},
                wording_variant=enum('compact', 'neutral'))

ALIASES = {
    'classification': ['Güterzuordnung','Gütergruppen','NST','Crosswalk'],
    'source_flags': ['Quellenkennzeichen','Quellenzeichen','Nullwerte'],
    'regional_vs_national': ['Deutschlandwert','Deutschlandwerte','Regionalwerte'],
    'outside_scope': ['CO₂','CO₂e','Kosten','Auslastung','Verlagerungspotenzial'],
    'road': ['straße', 'straßenverkehr'], 'rail': ['schiene', 'schienenverkehr'],
    'iww': ['binnenschiff', 'binnenschifffahrt'], 'tonnes': ['tonnen', 't'],
    'tkm': ['tonnenkilometer', 'tkm', 'verkehrsleistung', 'transportleistung'], 'outbound': ['versand'], 'inbound': ['empfang'],
    'teu': ['teu'], 'flights': ['flüge'], 'VD2': ['vd2'], 'VD3c': ['vd3c'],
}


def validate(schema, value):
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors:
        # Do not echo user/model content or internal paths in error messages.
        raise ValueError('Eingabe entspricht nicht dem erlaubten Format')


def token_present(question, token):
    return bool(re.search(r'(?<!\w)' + re.escape(str(token).casefold()) + r'(?!\w)', question.casefold()))


def question_supports(question, value, names):
    if isinstance(value, list):
        return all(question_supports(question, v, names) for v in value)
    if value is None or type(value) is bool:
        return False
    alternatives = [str(value), *ALIASES.get(str(value), []), *names.get(str(value), [])]
    return any(token_present(question, token) for token in alternatives)


class ParameterEvidenceError(ValueError):
    """Fehlende Angaben für eine gezielte Kundennachfrage, ohne interne Details."""
    def __init__(self, fields):
        self.fields = list(dict.fromkeys(fields))
        super().__init__('Auswahl nicht belegt: ' + ', '.join(self.fields))


def directed_pairs(question, names, endpoints):
    """Nur ausdrücklich gerichtete Ortsangaben; Mehrdeutigkeit bleibt erhalten."""
    aliases = {}
    for code in set(names) | set(endpoints):
        for label in [code, *names.get(code, [])]:
            if token_present(question, label):
                aliases.setdefault(label.casefold(), set()).add(code)
    if not aliases:
        return set()
    alternatives = '|'.join(re.escape(label) for label in sorted(aliases, key=len, reverse=True))
    patterns = [rf'(?<!\w)(?P<source>{alternatives})\s*→\s*(?P<target>{alternatives})(?!\w)',
                rf'(?<!\w)(?P<source>{alternatives})\s+nach\s+(?P<target>{alternatives})(?!\w)',
                rf'\bvon\s+(?P<source>{alternatives})\s+nach\s+(?P<target>{alternatives})(?!\w)']
    pairs = set()
    for pattern in patterns:
        for match in re.finditer(pattern, question.casefold()):
            pairs.update((source, target) for source in aliases[match['source']]
                         for target in aliases[match['target']])
    return pairs


def qualified_region_mentions(question, names):
    """A shared short name alone cannot contradict a confirmed district."""
    owners={}
    for code,labels in names.items():
        for label in labels: owners.setdefault(label.casefold(),set()).add(code)
    unique={code:[label for label in labels if len(owners[label.casefold()])==1] for code,labels in names.items()}
    for alias,codes in owners.items():
        if len(codes)!=2: continue
        city=[code for code in codes if any(label.casefold() in {alias+', kreisfreie stadt',alias+', stadtkreis'} for label in names[code])]
        if len(city)==1:
            unique[city[0]].extend(['Stadt '+alias,'kreisfreie Stadt '+alias])
            district=next(code for code in codes if code!=city[0])
            unique[district].extend(['Landkreis '+alias,'Kreis '+alias,alias+', Landkreis'])
    return {code for code in names if question_supports(question,code,unique)}


def explicit_conflict(question, parameters, names):
    # Named VP scenarios are not observed-year selections. They can accompany
    # a separately confirmed Ist year in a combined profile.
    year_question = re.sub(r'\b(?:2019_BASE|2040_P1)\b', '', question)
    years = {int(x) for x in re.findall(r'(?<!\w)(?:19|20)\d{2}(?!\w)', year_question)}
    if 'year' in parameters and years and years != {parameters['year']}:
        return True
    for field in ['years','observed_years']:
        if field in parameters and not years <= set(parameters[field]):
            return True
    if 'start' in parameters and 'end' in parameters and any(not parameters['start']<=y<=parameters['end'] for y in years):
        return True
    mentioned_modes = {mode for mode in ['road', 'rail', 'iww'] if question_supports(question, mode, {})}
    if parameters.get('mode') and mentioned_modes and mentioned_modes != {parameters['mode']}:
        return True
    if 'region' in parameters:
        mentioned = qualified_region_mentions(question,names)
        allowed_regions = {parameters['region']}
        if parameters.get('partner'):
            allowed_regions.add(parameters['partner'])
        if mentioned and not mentioned <= allowed_regions:
            return True
    if 'origin' in parameters and 'destination' in parameters:
        pairs = directed_pairs(question, names, [parameters['origin'],parameters['destination']])
        if pairs and pairs != {(parameters['origin'],parameters['destination'])}:
            return True
    return False


def verify_plan(plan, question, confirmed, names):
    validate(PLAN, plan)
    if plan['status'] != 'ready':
        return False
    function = plan['function_id']
    if function not in FUNCTIONS or plan['unresolved_fields']:
        raise ValueError('Unvollständige Funktionsauswahl')
    parameters = plan['parameters']
    validate(FUNCTIONS[function][3], parameters)
    fixed_mode = 'rail' if function in {'rail_goods','rail_goods_history'} else 'road' if function in {'road_relation_goods_limit','road_details'} else None
    mentioned_modes = {mode for mode in ['road','rail','iww'] if question_supports(question,mode,{})}
    if fixed_mode and mentioned_modes and mentioned_modes != {fixed_mode}:
        raise ValueError('Verkehrsträger passt nicht zur Funktion')
    if explicit_conflict(question, parameters, names):
        raise ValueError('Frage widerspricht der vorgeschlagenen Auswahl')
    if set(plan['parameter_origins']) != set(parameters):
        raise ValueError('Parameterherkunft fehlt')
    unresolved = []
    for key, value in parameters.items():
        origin = plan['parameter_origins'][key]
        if origin == 'context':
            supported = key in confirmed and type(value) is type(confirmed[key]) and value == confirmed[key]
        else:
            supported = question_supports(question, value, names)
            if key in {'origin', 'destination'}:
                endpoints = [parameters.get('origin'), parameters.get('destination')]
                supported = all(endpoints) and directed_pairs(question, names, endpoints) == {tuple(endpoints)}
            if key == 'group':
                supported = (token_present(question, 'alle Güter') if value == 'ALL'
                             else token_present(question, 'C' + str(value)))
            if key == 'top':
                supported = bool(re.search(r'\btop\s+' + re.escape(str(value)) + r'\b', question, re.I))
        # A question cannot silently overwrite a differing explicit selection.
        if key in confirmed and value != confirmed[key]:
            supported = False
        if not supported:
            unresolved.append(key)
    if unresolved:
        raise ParameterEvidenceError(unresolved)
    return True


def model_functions():
    return [{'function_id': key, 'type': val[0], 'description': val[1], 'parameters': val[3]}
            for key, val in FUNCTIONS.items()]
