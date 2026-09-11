"""Gleicher fachlicher Ablauf für lokalen Test und späteren Portalaufruf."""
import hashlib
import json
import time
import duckdb
from pathlib import Path
from .contracts import PLAN, ANSWER, verify_plan, model_functions, FUNCTIONS, ParameterEvidenceError, validate
from .dialogue import conversation_question, complete_plan, route_hint
from .results import make_result, apply_selection, limited
from .requesty import ModelError
from .presentation import present
from .alternatives import related_data


class Service:
    def __init__(self, datasets, model=None, timeout_seconds=180):
        self.datasets, self.model = datasets, model
        if not 1 <= timeout_seconds <= 600:
            raise ValueError('Begrenzte technische Testfrist erforderlich')
        self.timeout_seconds = timeout_seconds
        config = Path(datasets.root) / 'config/analyseassistent'
        self.prompt = (config / 'SYSTEM_PROMPT.md').read_text(encoding='utf-8')
        self.rules = json.loads((config / 'FACHREGELN.json').read_text(encoding='utf-8'))
        if self.rules['response_mode'] != 'verified_statement_selection' or self.rules['free_factual_prose_enabled']:
            raise ValueError('Nicht unterstützter Regelmodus')
        self.prompt_sha256 = hashlib.sha256(self.prompt.encode()).hexdigest()
        self.rules_sha256 = hashlib.sha256((config / 'FACHREGELN.json').read_bytes()).hexdigest()

    def analyze(self, question, confirmed=None, *, function=None, select_answer=True, history=None):
        if not isinstance(question, str) or not question.strip() or len(question) > 4000:
            raise ValueError('Frage muss zwischen 1 und 4.000 Zeichen enthalten')
        question = conversation_question(question, history, self.datasets.names) if history else question
        confirmed = {} if confirmed is None else confirmed
        if not isinstance(confirmed, dict) or len(json.dumps(confirmed, ensure_ascii=False)) > 12000:
            raise ValueError('Filterumfang ungültig')
        started = time.monotonic()
        deadline = started + self.timeout_seconds
        audit = {'prompt_sha256': self.prompt_sha256, 'rules_sha256': self.rules_sha256,
                 'data_snapshot_id': self.datasets.snapshot_id, 'model_calls': [], 'attempted_model_calls': 0}
        assumptions, years = [], []
        def finish(result):
            if result['status']=='needs_clarification' and 'year' in result.get('missing_fields',[]) and years:
                result['available_years']=years
            related = related_data(result, self.datasets, deadline=deadline)
            if related is not None:
                result['related_data'] = related
            result['answer']=present(result,self.datasets)
            if result['status'] in {'ok','partial'}:
                result['answer']['notes']=list(dict.fromkeys([*result['answer']['notes'],*assumptions]))
            audit['total_ms'] = round((time.monotonic()-started)*1000)
            return result, audit
        if function is not None:
            plan = {'phase': 'plan', 'function_id': function, 'parameters': confirmed,
                    'parameter_origins': {k: 'context' for k in confirmed}, 'unresolved_fields': [], 'status': 'ready'}
        elif self.model is None:
            return finish(limited('not_available', 'Für freie Fragen ist noch kein Modell verbunden.'))
        else:
            # Only relevant metadata names; no test references or source paths.
            relevant = {code: names for code, names in self.datasets.names.items()
                        if code.casefold() in question.casefold() or any(n.casefold() in question.casefold() for n in names)}
            payload = {'phase': 'plan', 'question': question, 'confirmed_context': confirmed,
                       'functions': model_functions(), 'region_candidates': relevant, 'output_schema': PLAN}
            payload['suggested_function']=route_hint(question,self.datasets.names)
            payload['allowed_defaults']={'metric':'tonnes','group':'ALL','nst':None,'top':10,
                'direction':'Bei von A nach B: Versand von A nach B; bei regionalem Profil ohne Richtung: beide Richtungen.',
                'year':'Ein genanntes Jahr übernehmen. Bei aktuellstem Jahr prüft der Server den neuesten verfügbaren Jahrgang. Ohne Jahresangabe nur nach dem Jahr fragen.',
                'history':'Die Frage enthält gegebenenfalls die letzten Nutzereingaben einschließlich Ergänzungen. Keine erneute Nachfrage nach bereits genannten Angaben.'}
            try:
                audit['attempted_model_calls'] += 1
                plan, call = self.model.complete(self.prompt, payload, PLAN, deadline=deadline)
                audit['model_calls'].append(call)
            except ModelError as exc:
                audit['model_error']=str(exc)
                if exc.diagnostics:
                    audit['model_error_diagnostics'] = exc.diagnostics
                return finish(limited('error', 'Die Frage konnte wegen eines Modellfehlers nicht zugeordnet werden.'))
        audit['plan'] = plan
        try:
            validate(PLAN,plan)
            if function is None:
                plan,confirmed,assumptions,years=complete_plan(plan,question,confirmed,self.datasets)
                audit['resolved_plan']=plan
            ready = verify_plan(plan, question, confirmed, self.datasets.names)
        except ParameterEvidenceError as error:
            return finish(limited('needs_clarification', 'Bitte die fehlenden Angaben ergänzen.', missing_fields=error.fields))
        except ValueError:
            return finish(limited('needs_clarification', 'Bitte Funktion, Raum, Zeitraum und Filter eindeutig bestätigen; die vorgeschlagene Auswahl ist nicht ausreichend belegt.'))
        if not ready:
            notices = {'needs_clarification': 'Bitte fehlenden Raum, Zeitraum oder Filter ergänzen.',
                       'not_available': 'Die benötigte Auswertung ist in diesem lokalen Stand noch nicht angebunden.',
                       'out_of_scope': 'Diese Frage liegt außerhalb der verfügbaren Güterverkehrsdaten.'}
            if plan['status']=='needs_clarification':
                labels={'region':'Region','regions':'vergleichbare Regionen','origin':'Quellregion','destination':'Zielregion',
                        'year':'Jahr','years':'Bezugsjahre','start':'Anfangsjahr','end':'Endjahr','mode':'Verkehrsträger',
                        'modes':'Verkehrsträger','metric':'Kennzahl','metrics':'Kennzahlen','direction':'Richtung',
                        'directions':'Richtungen','group':'Gütergruppe','top':'Top-Anzahl','node':'Hafen oder Flughafen',
                        'minimum_base':'Mindestbasis','partner':'Relationspartner','observed_years':'Ist-Jahre',
                        'ags':'Gemeinde','month':'Monat','comparison_month':'Vergleichsmonat','measure':'Rangmaß'}
                missing=list(dict.fromkeys(labels[k] for k in plan['unresolved_fields'] if k in labels))
                if missing: notices['needs_clarification']='Bitte folgende Auswahl ergänzen: '+', '.join(missing)+'.'
            return finish(limited(plan['status'], notices[plan['status']],missing_fields=plan.get('unresolved_fields',[])))
        try:
            lookup_started = time.monotonic()
            raw = self.datasets.query(plan['function_id'], plan['parameters'], timeout_seconds=max(0.001, deadline-time.monotonic()))
            audit['lookup_ms'] = round((time.monotonic()-lookup_started)*1000)
            if time.monotonic() > deadline:
                return finish(limited('error', 'Die Datenabfrage hat die technische Testfrist überschritten.'))
            result = make_result(plan['function_id'], plan['parameters'], raw, self.datasets, self.rules['version'])
        except (ValueError, KeyError, OSError, duckdb.Error):
            return finish(limited('error', 'Die geprüfte Datenabfrage konnte nicht ausgeführt werden.'))
        if result['status'] in {'ok', 'partial'} and result.get('statements') and self.model and select_answer:
            payload = {'phase': 'answer', 'question': question, 'confirmed_parameters': plan['parameters'],
                       'result_id': result['result_id'],
                       'data_snapshot_id': result['data_snapshot_id'], 'statements': result['statements'],
                       'table_ids': [t['id'] for t in result['tables']], 'mandatory_notices': result['notices']}
            try:
                audit['attempted_model_calls'] += 1
                selection, call = self.model.complete(self.prompt, payload, ANSWER, deadline=deadline)
                audit['model_calls'].append(call)
                result = apply_selection(result, selection)
            except (ModelError, ValueError) as exc:
                audit['answer_selection_error']=str(exc)
                if isinstance(exc, ModelError) and exc.diagnostics:
                    audit['answer_error_diagnostics'] = exc.diagnostics
                result['notices'].append('Die feste geprüfte Kurzfassung wird angezeigt; die optionale Modellauswahl war nicht verwendbar.')
        return finish(result)
