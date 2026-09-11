"""Technische Testbereitschaft aller Eingaben; ausdrücklich keine Fachabnahme."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from server.analyseassistent.datasets import Datasets,digest
from server.analyseassistent.contracts import FUNCTIONS,verify_plan
from scripts.analysis.prepare_assistant_cases import CLARIFICATION_CASES

ROOT=Path(__file__).resolve().parents[2]


def required_files():
    return [*sorted((ROOT/'server/analyseassistent').glob('*.py')),
            *sorted((ROOT/'integration/analyseassistent').glob('*.py')),
            ROOT/'tests/analyseassistent/test_runtime.py',
            ROOT/'scripts/validation/validate_assistant_runtime.py',
            ROOT/'scripts/analysis/prepare_assistant_gate.py',
            ROOT/'scripts/analysis/prepare_assistant_cases.py',
            ROOT/'scripts/analysis/run_assistant_catalog.py',
            ROOT/'scripts/analysis/run_assistant.py',
            ROOT/'scripts/analysis/build_assistant_references.py',
            ROOT/'config/analyseassistent/DARSTELLUNGSREFERENZEN.json',
            ROOT/'config/analyseassistent/SYSTEM_PROMPT.md',
            ROOT/'config/analyseassistent/FACHREGELN.json',
            ROOT/'config/analyseassistent/requirements.txt']


def verify_bound_files(hashes):
    required = {p.relative_to(ROOT).as_posix() for p in required_files()}
    if not required <= set(hashes):
        raise ValueError('Prüfbericht bindet nicht alle Programme, Systemprompt und Fachregeln')
    if any(digest(ROOT/p) != expected for p, expected in hashes.items()):
        raise ValueError('Programme oder Modellregeln seit der lokalen Prüfung verändert')


def prepare(validation,output):
    if output.exists(): raise ValueError('Neuer Gate-Bericht erforderlich')
    validation=validation.resolve()
    report=json.loads(validation.read_text(encoding='utf-8'))
    if report.get('passed') is not True or report.get('external_model_calls')!=0:
        raise ValueError('Bestandene lokale Prüfung erforderlich')
    verify_bound_files(report['files_sha256'])
    datasets=Datasets(ROOT)
    path=ROOT/'tests/analyseassistent/inputs.json'
    cases=json.loads(path.read_text(encoding='utf-8'))
    checks=[]
    for case in cases:
        function=case['structured_function']
        if function:
            parameters=case['confirmed']
            plan={'phase':'plan','function_id':function,'parameters':parameters,
                  'parameter_origins':{k:'context' for k in parameters},'unresolved_fields':[],'status':'ready'}
            verify_plan(plan,case['question']+'\n'+case['parameter_guidance'],parameters,datasets.names)
            if FUNCTIONS[function][2] not in datasets.paths:
                raise ValueError('Benötigtes Datenpaket nicht bereit')
            kind='concrete_query'
        else:
            if case['id'] not in CLARIFICATION_CASES or case['confirmed']:
                raise ValueError('Ungeklärter Fall ist kein definierter Rückfragetest')
            kind='missing_context'
        case['preparation_status']='ready'
        case['blocking_note']=None
        checks.append({'id':case['id'],'kind':kind,'input_contract_checked':True})
    if len(checks)!=45 or {c['id'] for c in checks}!={f'T{i:02}' for i in range(1,46)}:
        raise ValueError('Alle 45 Fälle erforderlich')
    path.write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    gate={'ready_for_model_evaluation':True,'full_factual_acceptance':False,
          'input_sha256':digest(path),'reference_sha256':digest(ROOT/'tests/analyseassistent/references.json'),
          'validation_sha256':digest(validation),'data_snapshot_id':datasets.snapshot_id,
          'runtime_sha256':report['files_sha256'],'cases':checks,
          'limitation':'32 konkrete Eingaben und 13 absichtlich fehlende Auswahlen; synthetische Kontrollen sind keine realen Verkehrsantworten. Fachliche Bewertung bleibt offen.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists(): raise ValueError('Neuer Gate-Bericht erforderlich')
    output.write_text(json.dumps(gate,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {k:gate[k] for k in ['ready_for_model_evaluation','full_factual_acceptance','data_snapshot_id']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--validation',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();print(json.dumps(prepare(args.validation,args.output)))
