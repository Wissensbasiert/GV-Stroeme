"""Portal-, Release- und Migrationsprüfungen für den Analyseassistenten, ohne Livezugriff."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--portal',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise ValueError('Neuer Prüfbericht erforderlich')
    portal=args.portal.resolve()
    sys.path.insert(0,str(portal/'tests'))
    names=['test_alwaysdata_kita_deployment','test_gueterstroeme_portal','test_build_alwaysdata_release','test_migrate']
    loader=unittest.TestLoader()
    suite=unittest.TestSuite(loader.loadTestsFromName(name) for name in names)
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    files=[portal/'alwaysdata_portal'/name for name in ['wsgi.py','admin.py','ai_access.py','analyseassistent.py','portal_existing.py','migrations/009_tool_ai_quotas.sql']]
    files.extend(portal/'tests'/(name+'.py') for name in names)
    files.extend([portal/'scripts/build_alwaysdata_release.py',portal/'scripts/gueterstroeme_release.py',Path(__file__)])
    report={'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),
            'errors':len(result.errors),'external_model_calls':0,'portal_connections':0,
            'details':stream.getvalue(),'files_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['details','files_sha256']}))
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':
    raise SystemExit(main())
