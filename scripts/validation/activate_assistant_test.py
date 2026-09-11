"""Aktiviert ausschließlich den geprüften ui05-Testeinstieg, ohne Kontorechte.

Der bestehende Serverprüfer übernimmt Manifestprüfung und temporäre Prüfmittel.
Die Kontofreigabe erfolgt anschließend über die angemeldete Portalverwaltung.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--portal', type=Path, required=True)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    assert args.release.name == 'portal-test-20260910-gueterstroeme-ui05'
    assert not args.output.exists()
    sys.path.insert(0, str(args.portal/'deployment/automation'))
    from deploy_alwaysdata_test import Api
    api = Api(os.environ['ALWAYSDATA_API_TOKEN'])
    site = api.request('GET', '/site/1067000/')
    production = api.request('GET', '/site/1069350/')
    assert {str(a).rstrip('/') for a in site['addresses']} == {'test.portal.wissensbasiert.de'}
    assert site['path'] == 'portal_test/releases/'+args.release.name+'/alwaysdata_portal/wsgi.py'
    assert site['virtualenv_directory'] == 'portal_test/.venv'
    environment = site['environment']
    lines = environment.splitlines()
    variables = dict(line.split('=',1) for line in lines if '=' in line)
    assert variables['WBP_PORTAL_ENVIRONMENT'] == 'test'
    assert variables['WBP_GUETERSTROEME_ENABLED'] == '0'
    assert variables['REQUESTY_API_KEY']
    assert sum(line.startswith('WBP_GUETERSTROEME_ENABLED=') for line in lines) == 1
    production_variables = dict(line.split('=',1) for line in production['environment'].splitlines() if '=' in line)
    # Actual DB variable names come from the portal configuration, not guesses.
    assert variables.get('WBP_PORTAL_DB_NAME')
    assert production_variables.get('WBP_PORTAL_DB_NAME')
    assert variables['WBP_PORTAL_DB_NAME'] != production_variables['WBP_PORTAL_DB_NAME']
    if not args.apply:
        print(json.dumps({'plan':True,'site_id':1067000,'tool':'gueterstroeme',
                          'activation_flag':'0 -> 1','account_changes':0,'production_changes':0}))
        return 0
    spec = importlib.util.spec_from_file_location('freight_probe', Path(__file__).with_name('validate_assistant_alwaysdata.py'))
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    probe.REMOTE = probe.REMOTE.replace("cursor.execute('SET TRANSACTION READ ONLY')", """
            cursor.execute("SET LOCAL statement_timeout = '10s'")
            cursor.execute("LOCK TABLE portal_tools, portal_tool_entitlements IN SHARE ROW EXCLUSIVE MODE")
            cursor.execute("SELECT count(*) FROM portal_tool_entitlements WHERE tool_slug='gueterstroeme'")
            assert cursor.fetchone()[0] == 0, 'Existing tool grants require separate review'
            cursor.execute("SELECT count(*) FROM portal_tool_ai_grants WHERE tool_slug='gueterstroeme'")
            assert cursor.fetchone()[0] == 0
            cursor.execute("UPDATE portal_tools SET is_active=TRUE WHERE slug='gueterstroeme' RETURNING slug")
            assert cursor.fetchone()[0] == 'gueterstroeme'
            report['database_writes']=1
            report['account_changes']=0
""")
    sys.argv = [str(spec.origin),'--portal',str(args.portal),'--release',str(args.release),'--output',str(args.output)]
    assert probe.main() == 0
    # Re-read immediately before patching to preserve concurrent manual changes.
    fresh = api.request('GET','/site/1067000/')
    assert fresh['environment'] == environment and fresh['path'] == site['path']
    updated = '\n'.join('WBP_GUETERSTROEME_ENABLED=1' if line.startswith('WBP_GUETERSTROEME_ENABLED=') else line for line in lines)
    api.request('PATCH','/site/1067000/',{'environment':updated})
    api.request('POST','/site/1067000/restart/')
    checked = api.request('GET','/site/1067000/')
    assert checked['environment'] == updated
    assert api.request('GET','/site/1069350/') == production
    report = json.loads(args.output.read_text(encoding='utf-8'))
    report.update(activation_flag_enabled=True,production_unchanged=True,account_changes=0)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Testeinstieg aktiviert; Kontofreigabe ausstehend. Produktion unverändert.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
