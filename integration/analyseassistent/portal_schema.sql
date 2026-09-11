-- ENTWURF für die getrennte Testportal-Integration, hier NICHT angewendet.
-- Voraussetzungen: Portal-Identitäten und portal_tools sind vorhanden.
-- Tabellen gehören in dieselbe PostgreSQL-Datenbank wie das jeweilige Portal.
-- Paketpflege/Abfragen sind nur nach serverseitiger Portalrechteprüfung zulässig.
CREATE TABLE IF NOT EXISTS portal_tool_ai_plans (
    tool_slug TEXT NOT NULL REFERENCES portal_tools(slug) ON DELETE CASCADE,
    plan_code TEXT NOT NULL CHECK (plan_code IN ('basic', 'premium')),
    monthly_limit INTEGER NOT NULL CHECK (monthly_limit > 0),
    PRIMARY KEY (tool_slug, plan_code)
);
CREATE TABLE IF NOT EXISTS portal_tool_ai_grants (
    identity_id BIGINT NOT NULL REFERENCES portal_external_identities(id) ON DELETE CASCADE,
    tool_slug TEXT NOT NULL,
    plan_code TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (identity_id, tool_slug),
    FOREIGN KEY (tool_slug, plan_code) REFERENCES portal_tool_ai_plans(tool_slug, plan_code) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS portal_tool_ai_requests (
    identity_id BIGINT NOT NULL,
    tool_slug TEXT NOT NULL,
    request_id TEXT NOT NULL CHECK (request_id ~ '^[!-~]{8,100}$'),
    period_start DATE NOT NULL CHECK (EXTRACT(DAY FROM period_start) = 1),
    request_hash CHAR(64) NOT NULL CHECK (request_hash ~ '^[0-9a-f]{64}$'),
    status TEXT NOT NULL CHECK (status IN ('reserved', 'charged', 'released')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMPTZ,
    PRIMARY KEY (identity_id, tool_slug, request_id),
    FOREIGN KEY (identity_id, tool_slug) REFERENCES portal_tool_ai_grants(identity_id, tool_slug) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS portal_tool_ai_requests_period
    ON portal_tool_ai_requests(identity_id, tool_slug, period_start, status);
CREATE INDEX IF NOT EXISTS portal_tool_ai_requests_recent
    ON portal_tool_ai_requests(identity_id, tool_slug, created_at);
-- Erst nach vorhandener Werkzeuganlage in einer eigenen Testmigration ausführen:
INSERT INTO portal_tool_ai_plans(tool_slug, plan_code, monthly_limit)
SELECT slug, 'basic', 5 FROM portal_tools WHERE slug = 'gueterstroeme'
ON CONFLICT (tool_slug, plan_code) DO NOTHING;
INSERT INTO portal_tool_ai_plans(tool_slug, plan_code, monthly_limit)
SELECT slug, 'premium', 50 FROM portal_tools WHERE slug = 'gueterstroeme'
ON CONFLICT (tool_slug, plan_code) DO NOTHING;
-- Vor jeder Reservierung die passende Zeile in portal_tool_ai_grants mit
-- SELECT ... FOR UPDATE sperren; danach aktuelle Werkzeugberechtigung,
-- Monat (Europe/Berlin), Limit und Idempotenz prüfen. Alle Schritte in EINER
-- Transaktion. Keine SELECT-count-then-INSERT-Folge ohne diese Sperre.
-- Keine fremden/produktiven Rechte verändern oder vorhandene Tableau-Notizen umdeuten.
