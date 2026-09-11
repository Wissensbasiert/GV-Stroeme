"""KI-Paketpflege im geschützten Verwaltungsbereich des Testportals."""
import os
import uuid
from html import escape


def enabled():
    return os.environ.get('WBP_PORTAL_ENVIRONMENT') == 'test' and os.environ.get('WBP_GUETERSTROEME_ENABLED') == '1'


def connection():
    from db import database_connection_parameters
    import psycopg
    parameters = database_connection_parameters()
    if parameters is None:
        raise RuntimeError('Portaldatenbank nicht verfügbar')
    return psycopg.connect(connect_timeout=5, **parameters)


def overview(issuer, *, connect=None):
    """Nur nach Administratorprüfung aufrufen; Fehler ist nicht Nullverbrauch."""
    if not enabled():
        return {}
    try:
        with (connect or connection)() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SET LOCAL statement_timeout = '5s'")
                cursor.execute("""SELECT identity.external_user_id::text,
                    grant_row.plan_code, grant_row.is_active, plan.monthly_limit,
                    COUNT(request.request_id) FILTER (WHERE request.status='charged'),
                    COUNT(request.request_id) FILTER (WHERE request.status='reserved'),
                    to_char(CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Berlin','YYYY-MM')
                    FROM portal_external_identities identity
                    JOIN portal_tool_entitlements entitlement ON entitlement.identity_id=identity.id
                    JOIN portal_tools tool ON tool.slug=entitlement.tool_slug
                    LEFT JOIN portal_tool_ai_grants grant_row
                      ON (grant_row.identity_id,grant_row.tool_slug)=(identity.id,tool.slug)
                    LEFT JOIN portal_tool_ai_plans plan
                      ON (plan.tool_slug,plan.plan_code)=(grant_row.tool_slug,grant_row.plan_code)
                    LEFT JOIN portal_tool_ai_requests request
                      ON (request.identity_id,request.tool_slug)=(identity.id,tool.slug)
                      AND request.period_start=date_trunc('month',CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Berlin')::date
                    WHERE identity.provider='hanko' AND identity.issuer=%s
                      AND tool.slug='gueterstroeme' AND tool.is_active=TRUE
                    GROUP BY identity.id,grant_row.plan_code,grant_row.is_active,plan.monthly_limit""", (issuer,))
                return {str(user): {'plan': plan, 'active': bool(active), 'limit': limit,
                                   'used': used, 'reserved': reserved, 'month': month}
                        for user,plan,active,limit,used,reserved,month in cursor.fetchall()}
    except Exception:
        return None


def save_plan(issuer, external_user_id, plan, *, connect=None):
    """Nur aus dem authentifizierten, CSRF-geprüften Administrator-POST aufrufen."""
    if not enabled():
        return 'ai_unavailable'
    if plan not in {'none','basic','premium'} or not issuer:
        return 'invalid_ai_plan'
    try:
        user = str(uuid.UUID(external_user_id))
    except (ValueError, TypeError, AttributeError):
        return 'invalid_id'
    try:
        with (connect or connection)() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SET LOCAL statement_timeout = '8s'")
                cursor.execute("SET LOCAL lock_timeout = '5s'")
                cursor.execute("""SELECT identity.id FROM portal_external_identities identity
                    JOIN portal_tool_entitlements entitlement ON entitlement.identity_id=identity.id
                    JOIN portal_tools tool ON tool.slug=entitlement.tool_slug
                    WHERE identity.provider='hanko' AND identity.issuer=%s AND identity.external_user_id=%s
                      AND tool.slug='gueterstroeme' AND tool.is_active=TRUE
                    FOR UPDATE OF identity""", (issuer,user))
                row = cursor.fetchone()
                if row is None:
                    return 'ai_requires_tool'
                identity = row[0]
                if plan == 'none':
                    cursor.execute("""UPDATE portal_tool_ai_grants SET is_active=FALSE
                        WHERE identity_id=%s AND tool_slug='gueterstroeme'""", (identity,))
                else:
                    cursor.execute("""INSERT INTO portal_tool_ai_grants(identity_id,tool_slug,plan_code,is_active)
                        VALUES (%s,'gueterstroeme',%s,TRUE)
                        ON CONFLICT (identity_id,tool_slug) DO UPDATE
                        SET plan_code=EXCLUDED.plan_code,is_active=TRUE""", (identity,plan))
        return 'ai_saved'
    except Exception:
        return 'failed'


def account_controls(record, external_user_id, csrf):
    if not record:
        return ''
    selected = record['plan'] if record['active'] else 'none'
    options = ''.join('<option value="'+code+'"'+(' selected' if code==selected else '')+'>'+label+'</option>'
                      for code,label in [('none','KI-Zugang gesperrt'),('basic','Basic · 5 Fragen pro Monat'),
                                         ('premium','Premium · 50 Fragen pro Monat')])
    used, reserved = int(record['used']), int(record['reserved'])
    limit = int(record['limit']) if record['limit'] is not None else 0
    if record['active']:
        usage = f'{used} von {limit} Fragen genutzt · {reserved} in Bearbeitung · {max(0,limit-used-reserved)} verfügbar'
    else:
        usage = f'KI-Zugang gesperrt · {used} Fragen genutzt · {reserved} in Bearbeitung'
    return f"""<form method="post" action="/admin/ai-access" class="admin-form" style="grid-column:1/-1;width:100%">
      <input type="hidden" name="csrf_token" value="{escape(csrf or '',quote=True)}">
      <input type="hidden" name="external_user_id" value="{escape(external_user_id,quote=True)}">
      <label><span>Güterströme · KI-Paket</span><select name="ai_plan">{options}</select></label>
      <p>{escape(usage)} · Monat {escape(str(record['month']))}</p>
      <small>Gezählt werden erfolgreiche numerische Auswertungen je Kalendermonat. Rückfragen zählen nicht. Ein Paketwechsel setzt den Verbrauch nicht zurück.</small>
      <div class="admin-form-actions"><button type="submit" {'disabled' if not csrf else ''}>KI-Paket speichern</button></div>
    </form>"""
