"""Gemeldeten Gesprächsablauf reproduzieren; echte Modellaufrufe nur mit --requesty."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from server.analyseassistent.datasets import Datasets,digest
from server.analyseassistent.service import Service
from server.analyseassistent.dialogue import previous_calendar_year
from scripts.analysis.prepare_assistant_gate import required_files

QUESTIONS=[
    'Was für Güter wurden letztes Jahr von Köln nach Düsseldorf transportiert und wie viele?',
    'Kannst du mir auch die Verkehrsleistung nennen? Und was ist mit der Güterart?',
    'Ich meine weiterhin Köln nach Düsseldorf im letzten Jahr',
    '2024',
]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--requesty',action='store_true')
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Neuer Bericht erforderlich')
    root=Path(__file__).resolve().parents[2]
    model=None
    if args.requesty:
        from server.analyseassistent.credentials import load_local_requesty
        model=load_local_requesty()
    service=Service(Datasets(root),model=model)
    token=None
    report={'passed':False,'external_model_calls':0,'customer_quota_writes':0,'turns':[],
        'files_sha256':{p.relative_to(root).as_posix():digest(p) for p in required_files()}}
    try:
        for index,question in enumerate(QUESTIONS):
            result,audit=service.analyze(question,conversation=token)
            report['external_model_calls']+=audit['attempted_model_calls']
            report['turns'].append({'question':question,'result':result,'audit':audit})
            token=result['conversation']
            assert result['status'] in {'ok','partial'}
            p=result['parameters']
            assert p['origin']=='DEA23' and p['destination']=='DEA11'
            assert p['year']==(2024 if index==3 else previous_calendar_year())
            assert p['include_goods'] and p['metrics']==(['tonnes'] if index==0 else ['tonnes','tkm'])
            assert all(row['label'] and row['value'] and row['unit'] for table in result['answer']['tables'] for row in table['rows'])
            if args.requesty:
                assert result['answer_mode']=='grounded_narrative',audit.get('narrative_error')
            print(f'Gesprächsschritt {index+1}: {result["status"]}, Jahr {p["year"]}, Kennzahlen {p["metrics"]}',flush=True)
        report['passed']=True
    except Exception as error:
        report['error_type']=type(error).__name__
        report['error']=str(error)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in {'turns','files_sha256'}}))
    return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
