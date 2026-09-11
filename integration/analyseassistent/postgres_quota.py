"""PostgreSQL-Adapter zur Portalabnahme; Schema und Echtbetrieb noch nicht angewendet.

Die Verbindung wird vom Portal injiziert. Keine eigene Konfigurationsdatei,
keine Zugangsdaten in Ausgaben, keine browserseitigen Benutzer-/Paketangaben.
"""
from contextlib import contextmanager
import re
from server.analyseassistent.quota import QuotaError


class PostgresQuota:
    TOOL='gueterstroeme'

    def __init__(self,connect):
        self.connect=connect

    @contextmanager
    def transaction(self):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL statement_timeout = '8s'")
                cursor.execute("SET LOCAL lock_timeout = '5s'")
                yield cursor

    def grant_and_period(self,cursor,identity):
        if type(identity) is not int or identity<=0:
            raise QuotaError('Gültige serverseitige Portalidentität erforderlich')
        cursor.execute('''SELECT grant_row.plan_code,plan.monthly_limit,
                   date_trunc('month',CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Berlin')::date
            FROM portal_tool_ai_grants grant_row
            JOIN portal_tool_ai_plans plan ON (plan.tool_slug,plan.plan_code)=(grant_row.tool_slug,grant_row.plan_code)
            JOIN portal_external_identities identity ON identity.id=grant_row.identity_id
            JOIN portal_tool_entitlements entitlement ON (entitlement.identity_id,entitlement.tool_slug)=(grant_row.identity_id,grant_row.tool_slug)
            JOIN portal_tools tool ON tool.slug=grant_row.tool_slug
            WHERE grant_row.identity_id=%s AND grant_row.tool_slug=%s
              AND grant_row.is_active=TRUE AND tool.is_active=TRUE AND identity.provider='hanko'
              AND entitlement.status='active'
              AND (entitlement.valid_from IS NULL OR entitlement.valid_from <= (CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Berlin')::date)
              AND (entitlement.valid_until IS NULL OR entitlement.valid_until >= (CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Berlin')::date)
            FOR UPDATE OF grant_row,entitlement''',(identity,self.TOOL))
        row=cursor.fetchone()
        if row is None:
            raise QuotaError('Werkzeugzugriff oder KI-Paket nicht freigegeben')
        return row

    def status(self,identity):
        with self.transaction() as cursor:
            plan,limit,period=self.grant_and_period(cursor,identity)
            cursor.execute('''SELECT status,count(*) FROM portal_tool_ai_requests
                WHERE identity_id=%s AND tool_slug=%s AND period_start=%s GROUP BY status''',(identity,self.TOOL,period))
            counts=dict(cursor.fetchall())
            used,reserved=counts.get('charged',0),counts.get('reserved',0)
            return {'plan':plan,'limit':limit,'used':used,'reserved':reserved,
                    'remaining':max(0,limit-used-reserved),'month':period.strftime('%Y-%m')}

    def reserve(self,identity,request_id,request_hash):
        if not isinstance(request_id,str) or not re.fullmatch(r'[!-~]{8,100}',request_id):
            raise ValueError('Gültige Anfragekennung erforderlich')
        if not isinstance(request_hash,str) or not re.fullmatch(r'[0-9a-f]{64}',request_hash):
            raise ValueError('Gültiger Anfragefingerabdruck erforderlich')
        with self.transaction() as cursor:
            _plan,limit,period=self.grant_and_period(cursor,identity)
            cursor.execute('''SELECT request_hash,status FROM portal_tool_ai_requests
                WHERE identity_id=%s AND tool_slug=%s AND request_id=%s''',(identity,self.TOOL,request_id))
            previous=cursor.fetchone()
            if previous:
                if previous[0]!=request_hash:
                    raise QuotaError('Anfragekennung wurde bereits für eine andere Anfrage verwendet')
                return {'duplicate':True,'state':previous[1]}
            cursor.execute('''SELECT count(*) FROM portal_tool_ai_requests
                WHERE identity_id=%s AND tool_slug=%s AND created_at > CURRENT_TIMESTAMP - INTERVAL '60 seconds' ''',(identity,self.TOOL))
            if cursor.fetchone()[0]>=20:
                raise QuotaError('Zu viele Anfragen in kurzer Zeit; bitte kurz warten')
            cursor.execute('''SELECT count(*) FROM portal_tool_ai_requests
                WHERE identity_id=%s AND tool_slug=%s AND period_start=%s AND status IN ('reserved','charged')''',
                           (identity,self.TOOL,period))
            if cursor.fetchone()[0]>=limit:
                raise QuotaError('Monatskontingent ausgeschöpft')
            cursor.execute('''INSERT INTO portal_tool_ai_requests(identity_id,tool_slug,request_id,period_start,request_hash,status)
                VALUES (%s,%s,%s,%s,%s,'reserved')''',(identity,self.TOOL,request_id,period,request_hash))
            return {'duplicate':False,'state':'reserved'}

    def finish(self,identity,request_id,*,charge):
        with self.transaction() as cursor:
            cursor.execute('''UPDATE portal_tool_ai_requests SET status=%s,finished_at=CURRENT_TIMESTAMP
                WHERE identity_id=%s AND tool_slug=%s AND request_id=%s AND status='reserved' ''',
                           ('charged' if charge else 'released',identity,self.TOOL,request_id))
            return cursor.rowcount==1
