"""Echte kurzlebige PostgreSQL-Prüfung mit ausschließlich künstlichen Konten.

Startet eine eigene Instanz nur auf Loopback unter C:\\tmp, stoppt diese im
finally-Block und entfernt ausschließlich ihren eigenen temporären Ordner.
Keine Verbindungskonfiguration oder Zugangsdaten eines Portals werden gelesen.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date
import hashlib
import io
import json
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from integration.analyseassistent.postgres_quota import PostgresQuota
from server.analyseassistent.quota import QuotaError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--postgres-bin', type=Path, required=True)
    parser.add_argument('--driver-dir', type=Path, required=True)
    parser.add_argument('--portal', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Neuer Prüfbericht erforderlich')
    sys.path.insert(0, str(args.driver_dir))
    import psycopg
    from psycopg.errors import CheckViolation
    binaries = args.postgres_bin.resolve()
    scratch = Path(tempfile.mkdtemp(prefix='gueterstroeme-pg-', dir='C:/tmp')).resolve()
    cluster = scratch/'data'
    password = secrets.token_urlsafe(36)
    password_file = scratch/'init-password.txt'
    password_file.write_text(password+'\n', encoding='utf-8')
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    hidden = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    def command(name, *values, timeout=40):
        # A detached postgres child can inherit a captured pipe on Windows and
        # prevent communicate() from reaching EOF after pg_ctl already exited.
        # Dedicated files keep startup bounded and preserve local diagnostics.
        log=scratch/(name+'-command.log')
        with log.open('ab') as stream:
            return subprocess.run([str(binaries/(name+'.exe')), *map(str, values)],
                                  stdout=stream, stderr=stream, timeout=timeout, creationflags=hidden)
    def connect():
        return psycopg.connect(host='127.0.0.1', port=port, dbname='postgres', user='assistant_test',
                               password=password, connect_timeout=3)
    def execute(sql, params=None):
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall() if cursor.description else None
    started = False
    report = {'passed': False, 'external_model_calls': 0, 'portal_connections': 0,
              'synthetic_accounts_only': True, 'temporary_cluster_removed': False}
    try:
        initialized = command('initdb', '-D', cluster, '-U', 'assistant_test', '-A', 'scram-sha-256',
                              '--pwfile', password_file, '--encoding=UTF8', '--no-locale')
        password_file.unlink()
        if initialized.returncode:
            raise RuntimeError('Lokales PostgreSQL-initdb fehlgeschlagen (keine Portalverbindung)')
        with (cluster/'postgresql.conf').open('a', encoding='utf-8') as f:
            f.write(f"\nlisten_addresses = '127.0.0.1'\nport = {port}\nmax_connections = 30\nshared_buffers = '32MB'\n")
        start = command('pg_ctl', '-D', cluster, '-l', scratch/'postgres.log', '-w', '-t', '25', 'start')
        started = (cluster/'postmaster.pid').exists()
        if start.returncode:
            raise RuntimeError('Lokaler PostgreSQL-Start fehlgeschlagen')
        report['postgres_version'] = execute('SHOW server_version')[0][0]
        files = sorted((args.portal/'alwaysdata_portal/migrations').glob('*.sql'))
        if len(files) != 9 or files[-1].name != '009_tool_ai_quotas.sql':
            raise ValueError('Portal-Migrationsstand neu prüfen; erwartet 001 bis 009')
        for migration in files:
            execute(migration.read_text(encoding='utf-8'))
        execute("UPDATE portal_tools SET is_active=TRUE WHERE slug='gueterstroeme'")
        schema = ROOT/'integration/analyseassistent/portal_schema.sql'
        execute(schema.read_text(encoding='utf-8'))
        quota = PostgresQuota(connect)
        sys.path.insert(0,str(args.portal/'alwaysdata_portal'))
        import ai_access
        import admin

        class QuotaTests(unittest.TestCase):
            def setUp(self):
                execute('TRUNCATE portal_external_identities RESTART IDENTITY CASCADE')
                execute("UPDATE portal_tools SET is_active=TRUE WHERE slug='gueterstroeme'")
                self.identity = execute("INSERT INTO portal_external_identities(provider,issuer,external_user_id,label) VALUES ('hanko','https://synthetic.invalid','00000000-0000-0000-0000-000000000001','Künstliches Prüfkonto') RETURNING id")[0][0]
                execute("INSERT INTO portal_tool_entitlements(identity_id,tool_slug,status) VALUES (%s,'gueterstroeme','active')", (self.identity,))
                execute("INSERT INTO portal_tool_ai_grants(identity_id,tool_slug,plan_code) VALUES (%s,'gueterstroeme','basic')", (self.identity,))

            def test_basic_concurrency_cannot_overdraw(self):
                barrier = threading.Barrier(12)
                def reserve(i):
                    barrier.wait()
                    try:
                        quota.reserve(self.identity, f'parallel-{i:03}', 'a'*64)
                        return 'accepted'
                    except QuotaError:
                        return 'limited'
                with ThreadPoolExecutor(max_workers=12) as pool:
                    results = list(pool.map(reserve, range(12)))
                self.assertEqual(results.count('accepted'), 5)
                self.assertEqual(quota.status(self.identity)['reserved'], 5)
                self.assertEqual(quota.status(self.identity)['remaining'], 0)

            def test_duplicate_concurrency_and_payload_conflict(self):
                with ThreadPoolExecutor(max_workers=8) as pool:
                    outcomes = list(pool.map(lambda _:quota.reserve(self.identity, 'same-request', 'b'*64), range(8)))
                self.assertEqual(sum(not row['duplicate'] for row in outcomes), 1)
                with self.assertRaises(QuotaError): quota.reserve(self.identity, 'same-request', 'c'*64)
                self.assertEqual(quota.status(self.identity)['reserved'], 1)

            def test_release_charge_and_retry_are_idempotent(self):
                quota.reserve(self.identity, 'charge-001', 'a'*64)
                self.assertTrue(quota.finish(self.identity, 'charge-001', charge=True))
                self.assertFalse(quota.finish(self.identity, 'charge-001', charge=False))
                quota.reserve(self.identity, 'release-01', 'b'*64)
                self.assertTrue(quota.finish(self.identity, 'release-01', charge=False))
                self.assertTrue(quota.reserve(self.identity, 'release-01', 'b'*64)['duplicate'])
                status = quota.status(self.identity)
                self.assertEqual((status['used'],status['reserved'],status['remaining']), (1,0,4))

            def test_upgrade_and_downgrade_preserve_usage(self):
                quota.reserve(self.identity, 'count-001', 'a'*64)
                quota.finish(self.identity, 'count-001', charge=True)
                execute("UPDATE portal_tool_ai_grants SET plan_code='premium' WHERE identity_id=%s",(self.identity,))
                self.assertEqual((quota.status(self.identity)['limit'],quota.status(self.identity)['remaining']), (50,49))
                execute("UPDATE portal_tool_ai_grants SET plan_code='basic' WHERE identity_id=%s",(self.identity,))
                self.assertEqual((quota.status(self.identity)['used'],quota.status(self.identity)['remaining']), (1,4))

            def test_revoked_expired_or_inactive_rights_reject(self):
                for sql,reset in [
                    ("UPDATE portal_tool_entitlements SET status='suspended'", "UPDATE portal_tool_entitlements SET status='active'"),
                    ("UPDATE portal_tool_entitlements SET valid_until=CURRENT_DATE-1", "UPDATE portal_tool_entitlements SET valid_until=NULL"),
                    ("UPDATE portal_tool_entitlements SET valid_from=CURRENT_DATE+1", "UPDATE portal_tool_entitlements SET valid_from=NULL"),
                    ("UPDATE portal_tool_ai_grants SET is_active=FALSE", "UPDATE portal_tool_ai_grants SET is_active=TRUE"),
                    ("UPDATE portal_tools SET is_active=FALSE WHERE slug='gueterstroeme'", "UPDATE portal_tools SET is_active=TRUE WHERE slug='gueterstroeme'")]:
                    execute(sql)
                    with self.assertRaises(QuotaError): quota.reserve(self.identity,'blocked-01','a'*64)
                    execute(reset)
                execute('DELETE FROM portal_tool_entitlements WHERE identity_id=%s',(self.identity,))
                with self.assertRaises(QuotaError): quota.status(self.identity)

            def test_month_and_old_reservation_stay_in_original_period(self):
                current = execute("SELECT date_trunc('month',CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Berlin')::date")[0][0]
                prior = execute("SELECT (date_trunc('month',CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Berlin')-INTERVAL '1 month')::date")[0][0]
                quota.reserve(self.identity,'old-month-01','a'*64)
                execute('UPDATE portal_tool_ai_requests SET period_start=%s WHERE identity_id=%s',(prior,self.identity))
                quota.finish(self.identity,'old-month-01',charge=True)
                status=quota.status(self.identity)
                self.assertEqual((status['month'],status['used'],status['remaining']), (current.strftime('%Y-%m'),0,5))
                self.assertEqual(execute('SELECT period_start,status FROM portal_tool_ai_requests')[0],(prior,'charged'))

            def test_twenty_attempts_including_releases_throttle(self):
                for i in range(20):
                    key=f'throttle-{i:03}'
                    quota.reserve(self.identity,key,'a'*64)
                    quota.finish(self.identity,key,charge=False)
                with self.assertRaises(QuotaError): quota.reserve(self.identity,'throttle-last','b'*64)
                self.assertEqual(quota.status(self.identity)['used'],0)

            def test_failed_transaction_rolls_back_reservation(self):
                with self.assertRaises(RuntimeError):
                    with quota.transaction() as cursor:
                        _plan,_limit,period=quota.grant_and_period(cursor,self.identity)
                        cursor.execute("INSERT INTO portal_tool_ai_requests(identity_id,tool_slug,request_id,period_start,request_hash,status) VALUES (%s,'gueterstroeme','rollback-01',%s,%s,'reserved')",(self.identity,period,'a'*64))
                        raise RuntimeError('synthetic rollback')
                self.assertEqual(quota.status(self.identity)['reserved'],0)

            def test_admin_plan_changes_preserve_usage_and_inflight_reservations(self):
                user='00000000-0000-0000-0000-000000000001'
                quota.reserve(self.identity,'admin-used-01','a'*64)
                quota.finish(self.identity,'admin-used-01',charge=True)
                quota.reserve(self.identity,'admin-pending-01','b'*64)
                with patch.dict('os.environ',{'WBP_PORTAL_ENVIRONMENT':'test','WBP_GUETERSTROEME_ENABLED':'1'}):
                    for plan,limit in [('premium',50),('basic',5)]:
                        self.assertEqual(ai_access.save_plan('https://synthetic.invalid',user,plan,connect=connect),'ai_saved')
                        record=ai_access.overview('https://synthetic.invalid',connect=connect)[user]
                        self.assertEqual((record['limit'],record['used'],record['reserved']),(limit,1,1))
                    self.assertEqual(ai_access.save_plan('https://synthetic.invalid',user,'none',connect=connect),'ai_saved')
                    with self.assertRaises(QuotaError): quota.reserve(self.identity,'must-fail-01','c'*64)
                    self.assertTrue(quota.finish(self.identity,'admin-pending-01',charge=True))
                    self.assertEqual(ai_access.save_plan('https://synthetic.invalid',user,'basic',connect=connect),'ai_saved')
                    self.assertEqual(quota.status(self.identity)['used'],2)

            def test_admin_is_scoped_to_issuer_and_existing_tool_right(self):
                user='00000000-0000-0000-0000-000000000001'
                with patch.dict('os.environ',{'WBP_PORTAL_ENVIRONMENT':'test','WBP_GUETERSTROEME_ENABLED':'1'}):
                    self.assertEqual(ai_access.save_plan('https://wrong.invalid',user,'premium',connect=connect),'ai_requires_tool')
                    self.assertEqual(ai_access.overview('https://wrong.invalid',connect=connect),{})
                    self.assertEqual(ai_access.save_plan('https://synthetic.invalid',user,'unlimited',connect=connect),'invalid_ai_plan')
                    execute('DELETE FROM portal_tool_entitlements WHERE identity_id=%s',(self.identity,))
                    self.assertEqual(ai_access.save_plan('https://synthetic.invalid',user,'premium',connect=connect),'ai_requires_tool')
                    self.assertEqual(execute('SELECT plan_code FROM portal_tool_ai_grants'),[('basic',)])
                with patch.dict('os.environ',{'WBP_PORTAL_ENVIRONMENT':'production','WBP_GUETERSTROEME_ENABLED':'1'}):
                    self.assertEqual(ai_access.save_plan('https://synthetic.invalid',user,'premium',connect=connect),'ai_unavailable')

            def test_admin_overview_distinguishes_missing_plan_from_zero_usage(self):
                user='00000000-0000-0000-0000-000000000001'
                execute('DELETE FROM portal_tool_ai_grants WHERE identity_id=%s',(self.identity,))
                with patch.dict('os.environ',{'WBP_PORTAL_ENVIRONMENT':'test','WBP_GUETERSTROEME_ENABLED':'1'}):
                    record=ai_access.overview('https://synthetic.invalid',connect=connect)[user]
                    self.assertIsNone(record['plan']); self.assertIsNone(record['limit'])
                    self.assertFalse(record['active'])
                    self.assertEqual(ai_access.save_plan('https://synthetic.invalid',user,'premium',connect=connect),'ai_saved')
                    self.assertEqual(quota.status(self.identity)['remaining'],50)

            def test_existing_access_editor_preserves_ai_usage_and_issuer_scope(self):
                user='00000000-0000-0000-0000-000000000001'
                quota.reserve(self.identity,'existing-editor-01','a'*64)
                quota.finish(self.identity,'existing-editor-01',charge=True)
                other=execute("INSERT INTO portal_external_identities(provider,issuer,external_user_id,label) VALUES ('hanko','https://other.invalid',%s,'Anderer Aussteller') RETURNING id",(user,))[0][0]
                execute("INSERT INTO portal_tool_entitlements(identity_id,tool_slug,status) VALUES (%s,'gueterstroeme','active')",(other,))
                parameters={'host':'127.0.0.1','port':port,'dbname':'postgres','user':'assistant_test','password':password}
                with patch.object(admin,'database_connection_parameters',return_value=parameters):
                    self.assertEqual(admin.replace_manual_grants(issuer='https://synthetic.invalid',external_user_id=user,label='Aktualisiertes Prüfkonto',tableau_username='',tool_slugs=['gueterstroeme'],tableau_license_notes={},status='active',valid_from='',valid_until=''),'saved')
                    tools,grants=admin.admin_overview(issuer='https://synthetic.invalid')
                self.assertEqual(len(grants),1)
                self.assertEqual(grants[0]['label'],'Aktualisiertes Prüfkonto')
                self.assertEqual(quota.status(self.identity)['used'],1)

            def test_admin_failed_update_rolls_back(self):
                execute("CREATE FUNCTION reject_ai_change() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic failure'; END $$")
                execute('CREATE TRIGGER reject_ai_change BEFORE UPDATE ON portal_tool_ai_grants FOR EACH ROW EXECUTE FUNCTION reject_ai_change()')
                try:
                    with patch.dict('os.environ',{'WBP_PORTAL_ENVIRONMENT':'test','WBP_GUETERSTROEME_ENABLED':'1'}):
                        self.assertEqual(ai_access.save_plan('https://synthetic.invalid','00000000-0000-0000-0000-000000000001','premium',connect=connect),'failed')
                    self.assertEqual(execute('SELECT plan_code FROM portal_tool_ai_grants'),[('basic',)])
                finally:
                    execute('DROP TRIGGER reject_ai_change ON portal_tool_ai_grants')
                    execute('DROP FUNCTION reject_ai_change()')

            def test_schema_repeat_and_validation(self):
                execute(schema.read_text(encoding='utf-8'))
                self.assertEqual(execute("SELECT plan_code,monthly_limit FROM portal_tool_ai_plans ORDER BY plan_code"),[('basic',5),('premium',50)])
                with self.assertRaises(CheckViolation):
                    execute("UPDATE portal_tool_ai_plans SET monthly_limit=0")
                for identity in ('1',True,-1):
                    with self.assertRaises(QuotaError): quota.status(identity)

        stream=io.StringIO()
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(QuotaTests))
        report.update(passed=result.wasSuccessful(), tests=result.testsRun, failures=len(result.failures),
                      errors=len(result.errors), details=stream.getvalue(),
                      files_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*files,schema,ROOT/'integration/analyseassistent/postgres_quota.py',args.portal/'alwaysdata_portal/ai_access.py',args.portal/'alwaysdata_portal/admin.py',Path(__file__)]})
    except Exception as error:
        report['setup_error_type']=type(error).__name__
        report['setup_error']=str(error)[:400]
    finally:
        # A failed startup may still leave a live server. Always check its own PID file.
        if started or (cluster/'postmaster.pid').exists():
            stopped=command('pg_ctl','-D',cluster,'-m','fast','-w','-t','25','stop')
            report['server_stopped']=stopped.returncode==0 and not (cluster/'postmaster.pid').exists()
        else:
            report['server_stopped']=True
        if report['server_stopped']:
            if scratch.parent != Path('C:/tmp').resolve() or not scratch.name.startswith('gueterstroeme-pg-'):
                raise RuntimeError('Temporärer Pfad außerhalb des erlaubten Testbereichs')
            shutil.rmtree(scratch)
            report['temporary_cluster_removed']=not scratch.exists()
        report['passed']=report['passed'] and report['server_stopped'] and report['temporary_cluster_removed']
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k not in ('details','files_sha256')},ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
