"""Begrenzter echter Vorher-/Nachherdialog; keine Portalbuchung, keine Wiederholungen."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--requesty', action='store_true')
    parser.add_argument('--baseline', action='store_true')
    args=parser.parse_args()
    if args.output.exists(): raise SystemExit('Neuen Ausgabepfad verwenden; keine unbeabsichtigte Wiederholung.')
    sys.path.insert(0,str(args.root))
    from server.analyseassistent.datasets import Datasets
    from server.analyseassistent.service import Service
    from server.analyseassistent.credentials import load_local_requesty
    model=load_local_requesty() if args.requesty else None
    service=Service(Datasets(args.root),model=model)
    conversations=[
        ['Welche Güter gehen per Schiene von Berlin nach Hamburg?', 'Das aktuellste Jahr', 'Und in Gegenrichtung?', 'Und 2024?'],
        ['Wie viele Tonnen gingen 2024 per Binnenschiff von Köln nach Hamburg?'],
        ['Welche Güter gehen 2026 per Schiene von Berlin nach Hamburg?'],
    ]
    report={'mode':'baseline' if args.baseline else 'candidate','model':getattr(model,'model',None),'conversations':[], 'full_acceptance':False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    def save(): args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    save()
    for questions in conversations:
        turns=[]; history=[]; conversation=None
        report['conversations'].append(turns)
        for question in questions:
            options={}
            if args.baseline: options['history']=history
            elif conversation: options['conversation']=conversation
            result,audit=service.analyze(question,**options)
            conversation=result.pop('conversation',None)
            turns.append({'question':question,'result':result,'audit':audit})
            history.append(question)
            save()
            print(json.dumps({'question':question,'status':result['status'],'calls':audit['attempted_model_calls'],'ms':audit['total_ms']},ensure_ascii=False),flush=True)
    all_turns=[t for c in report['conversations'] for t in c]
    calls=[call for t in all_turns for call in t['audit']['model_calls']]
    diagnostics=[t['audit'][key] for t in all_turns for key in ['model_error_diagnostics','answer_error_diagnostics','narrative_error_diagnostics'] if key in t['audit']]
    usages=[c.get('usage') or {} for c in [*calls,*diagnostics]]
    report['summary']={'turns':len(all_turns),'clarifications':sum(t['result']['status']=='needs_clarification' for t in all_turns),
                       'calls':sum(t['audit']['attempted_model_calls'] for t in all_turns),'completed_calls':len(calls),'total_ms':sum(t['audit']['total_ms'] for t in all_turns),
                       'tokens':sum(u.get('total_tokens',0) for u in usages),
                       'cost_usd':sum(u.get('cost',0) for u in usages)}
    save()
    print(json.dumps(report['summary']))

if __name__=='__main__': main()
