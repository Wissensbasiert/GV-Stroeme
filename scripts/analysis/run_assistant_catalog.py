"""Gebündelter 45-Fälle-Lauf; strikte Bereitschaftssperre vor Modellaufrufen.

Der steuernde Prozess lädt Eingaben, der eigentliche Modellprozess bekommt pro
Fall nur die ausdrücklich ausgewählte Eingabedatei. Referenzen werden ihm nie
übergeben. Fachliche Bewertung bleibt von technischer Ausführung getrennt.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from server.analyseassistent.datasets import digest,Datasets
from scripts.analysis.prepare_assistant_gate import verify_bound_files

ROOT=Path(__file__).resolve().parents[2]


def run(output, *, live=False, gate=None):
    cases_path=ROOT/'tests/analyseassistent/inputs.json'
    cases=json.loads(cases_path.read_text(encoding='utf-8'))
    if len(cases)!=45 or {c['id'] for c in cases}!={f'T{i:02}' for i in range(1,46)}:
        raise ValueError('Vollständiger 45-Fälle-Katalog erforderlich')
    pending=[c['id'] for c in cases if c['preparation_status']!='ready']
    if live and pending:
        raise ValueError('Modelllauf gesperrt: vollständige Fallfreigabe fehlt für '+', '.join(pending))
    if live:
        if gate is None: raise ValueError('Gebundener Bericht zur technischen Testbereitschaft erforderlich')
        proof=json.loads(gate.read_text(encoding='utf-8'))
        verify_bound_files(proof['runtime_sha256'])
        if (proof.get('ready_for_model_evaluation') is not True or proof['input_sha256']!=digest(cases_path)
                or proof['reference_sha256']!=digest(ROOT/'tests/analyseassistent/references.json')
                or proof['data_snapshot_id']!=Datasets(ROOT).snapshot_id
                ):
            raise ValueError('Testbereitschaft passt nicht zu aktuellem Programm, Datenstand oder Eingaben')
    output=output.resolve()
    if output.exists():
        raise ValueError('Neuer Berichtsordner erforderlich; alte Ergebnisse bleiben unverändert')
    output.mkdir(parents=True)
    report={'started_at':datetime.now(timezone.utc).isoformat(),'mode':'requesty' if live else 'preflight_no_model',
            'input_sha256':digest(cases_path),'cases':[],'model_calls':0,'full_model_run_ready':not pending,
            'full_factual_acceptance':False}
    systemic_errors=0
    for case in cases:
        if not live and not case.get('structured_function'):
            report['cases'].append({'id':case['id'],'execution':'not_run','assessment':'not_ready',
                                    'reason':case['blocking_note']})
            continue
        request={'question':case['question'],'confirmed':case['confirmed']}
        if not live:
            request['function']=case['structured_function']
        else:
            # No expected function or solution enters the question-understanding test.
            request['question']+='\nBestätigter Eingabekontext: '+case['parameter_guidance']
        input_path=output/(case['id']+'_input.json')
        result_path=output/(case['id']+'_result.json')
        input_path.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        command=[sys.executable,'-X','utf8','-B',str(ROOT/'scripts/analysis/run_assistant.py'),'--input',str(input_path),'--output',str(result_path)]
        if live: command.append('--requesty')
        try:
            completed=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=240)
            if completed.returncode!=0 or not result_path.exists():
                row={'id':case['id'],'execution':'error','assessment':'not_passed','reason':'Laufzeitprozess fehlgeschlagen; keine ungeprüfte Fehlerausgabe übernommen.'}
            else:
                result=json.loads(result_path.read_text(encoding='utf-8'))
                calls=result['audit']['attempted_model_calls']
                report['model_calls']+=calls
                row={'id':case['id'],'execution':'completed','result_status':result['result']['status'],
                     'assessment':'pending_independent_review','result_file':result_path.name,'result_sha256':digest(result_path),
                     'model_calls':calls,'total_ms':result['audit']['total_ms']}
                error=result['audit'].get('model_error') or result['audit'].get('answer_selection_error')
                if live and error and str(error).startswith(('Modell','Gesamtfrist','Unerwartete Weiterleitung')):
                    row['model_error']=error
                    systemic_errors+=1
                else:
                    systemic_errors=0
        except subprocess.TimeoutExpired:
            row={'id':case['id'],'execution':'timeout','assessment':'not_passed','reason':'Technische Gesamtfrist des Testprozesses überschritten.'}
        report['cases'].append(row)
        # Checkpoint after each case; an interrupted run is never a passed run.
        (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if live and systemic_errors>=2:
            report['halted_reason']='Zwei aufeinanderfolgende technische Modellfehler; Konfiguration vor weiteren kostenpflichtigen Aufrufen prüfen.'
            break
    completed_ids={c['id'] for c in report['cases']}
    for case in cases:
        if case['id'] not in completed_ids:
            report['cases'].append({'id':case['id'],'execution':'not_run','assessment':'not_passed',
                                    'reason':'Gebündelter Lauf wegen technischer Modellfehler angehalten.'})
    report['finished_at']=datetime.now(timezone.utc).isoformat()
    (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'mode':report['mode'],'cases':len(report['cases']),'model_calls':report['model_calls'],
            'completed':sum(c['execution']=='completed' for c in report['cases']),
            'full_factual_acceptance':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--requesty',action='store_true')
    parser.add_argument('--gate',type=Path)
    args=parser.parse_args()
    print(json.dumps(run(args.output,live=args.requesty,gate=args.gate),ensure_ascii=False))
