"""Wiederholbarer Bericht der lokalen Laufzeitprüfung, ohne externe Modellaufrufe."""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts.analysis.prepare_assistant_gate import required_files

ROOT=Path(__file__).resolve().parents[2]


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests/analyseassistent'),pattern='test_*.py')
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    files=required_files()
    report={'tested_at':datetime.now(timezone.utc).isoformat(),'passed':result.wasSuccessful(),
            'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
            'external_model_calls':0,'full_45_case_acceptance':False,
            'files_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            'details':stream.getvalue()}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in {'files_sha256','details'}},ensure_ascii=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
