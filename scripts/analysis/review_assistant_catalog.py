"""Nachgelagerter Vergleich: Modellrouting, unveränderte Fakten und offene Fachgrenzen.

Dieser Prozess liest Referenzen erst nach dem Modelllauf. Kein Providerzugriff.
Eine identische lokale Ausgabe beweist Transport-/Routingtreue, nicht automatisch
die Vollständigkeit jeder fachlichen Sollantwort.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def review(live,baseline,output):
    run=read(live/'report.json'); local=read(baseline/'report.json')
    references={c['id']:c for c in read(ROOT/'tests/analyseassistent/references.json')}
    inputs={c['id']:c for c in read(ROOT/'tests/analyseassistent/inputs.json')}
    if not run.get('finished_at') or len(run['cases'])!=45:
        raise ValueError('Erst abgeschlossenen vollständigen Lauf bewerten')
    local_by_id={c['id']:c for c in local['cases']}
    rows=[]; times=[]; usage=[]; calls_with_usage=0
    for case in run['cases']:
        id=case['id']; checks={}
        if case.get('execution')!='completed':
            rows.append({'id':id,'status':'not_executed','checks':{}});continue
        result_path=live/case['result_file']
        if sha(result_path)!=case['result_sha256']: raise ValueError('Modellergebnis nach Lauf verändert')
        response=read(result_path);result=response['result'];audit=response['audit']
        times.append(audit['total_ms'])
        calls = list(audit['model_calls'])
        calls.extend(audit[k] for k in ('model_error_diagnostics', 'answer_error_diagnostics') if audit.get(k))
        for call in calls:
            values = call.get('usage')
            if isinstance(values, dict) and type(values.get('total_tokens')) in (int, float):
                calls_with_usage += 1
                usage.append(values)
        checks['no_transport_or_selection_error']=not audit.get('model_error') and not audit.get('answer_selection_error')
        checks['summary_at_most_four']=len(result['summary'])<=4
        checks['no_reference_markers_in_model_output']=all('last_terra_assessment' not in c.get('raw_content','') for c in audit['model_calls'])
        if references[id]['model_test_kind']=='missing_context':
            checks['requests_missing_selection']=result['status']=='needs_clarification'
            checks['no_invented_numbers']=not result.get('facts')
        else:
            expected=local_by_id[id]
            expected_path=baseline/expected['result_file']
            if sha(expected_path)!=expected['result_sha256']: raise ValueError('Lokales Vergleichsergebnis verändert')
            reference=read(expected_path)['result']
            checks['function_matches_prepared_route']=result.get('function_id')==inputs[id]['structured_function']
            for field in ['parameters','facts','tables','sources','notices','source_status']:
                checks['unchanged_'+field]=result.get(field)==reference.get(field)
            valid={s['id']:s for s in result['statements']}
            texts={s['text'] for s in valid.values()}
            checks['summary_only_server_statements']=all(s in texts for s in result['summary'])
        rows.append({'id':id,'result_status':result['status'],'model_function':audit.get('plan',{}).get('function_id'),
                     'status':'route_and_data_checks_passed' if all(checks.values()) else 'needs_review',
                     'checks':checks,'elapsed_ms':audit['total_ms']})
    counts=Counter(r['status'] for r in rows)
    report={'mode':'post_run_offline_review','live_report_sha256':sha(live/'report.json'),
            'baseline_report_sha256':sha(baseline/'report.json'),'reference_sha256':sha(ROOT/'tests/analyseassistent/references.json'),
            'cases':rows,'counts':dict(counts),'total_model_calls':run['model_calls'],
            'sum_case_time_ms':sum(times),'median_case_ms':sorted(times)[len(times)//2] if times else None,
            'max_case_ms':max(times) if times else None,
            'usage_totals':{k:sum(u.get(k,0) or 0 for u in usage) for k in ['prompt_tokens','completion_tokens','total_tokens']},
            'calls_with_usage':calls_with_usage,
            'calls_without_usage':run['model_calls']-calls_with_usage,
            'usage_complete':calls_with_usage==run['model_calls'],
            'full_factual_acceptance':False,
            'known_remaining_reviews':[
                'T13: tatsächliches Änderungsranking ist noch nicht als ausführbare Funktion angeboten; eine Nichtverfügbarkeit ersetzt nicht die gewünschte Rückfrage.',
                'T35: Quellenland ist im Rohbestand vorhanden, Partnerausgabe und ausgeschriebene Ländernamen noch vervollständigen.',
                'T43: Erklärung der Nichtadditivität vorhanden; konkreten 422/400/22-Nachweis in gebundene Ausgabe aufnehmen.',
                'Synthetische Kontrollen sind keine Freigabe einer realen harmonisierten Änderungsreihe oder unbekannter Gebiete.',
                'Prüfung der fachlichen Kurzfassung und verständlicher Orts-/Verkehrsträgernamen vor Portalabnahme.']}
    if output.exists(): raise ValueError('Neuer Bewertungsbericht erforderlich')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {k:report[k] for k in ['counts','total_model_calls','median_case_ms','max_case_ms','usage_totals','full_factual_acceptance']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--live',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(review(a.live,a.baseline,a.output),ensure_ascii=False))
