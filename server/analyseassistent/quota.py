"""Lokaler Kontingent-Prototyp mit atomarer Reservierung und Wiederholschutz.

SQLite ist ausschließlich die lokale Testablage. Das Portal verwendet seine
eigene PostgreSQL-Datenbank und einen separat abzunehmenden Adapter.
"""
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

LIMITS = {'basic': 5, 'premium': 50}
TOOL = 'gueterstroeme'


class QuotaError(RuntimeError):
    pass


def month_key(now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('Zeitpunkt benötigt eine Zeitzone')
    return now.astimezone(ZoneInfo('Europe/Berlin')).strftime('%Y-%m')


def fingerprint(request):
    return hashlib.sha256(json.dumps(request, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()


class LocalQuota:
    def __init__(self, path):
        self.path = Path(path).resolve()
        if not self.path.is_relative_to(Path('C:/tmp').resolve()):
            raise ValueError('Lokale Kontingentdatei muss unter C:\\tmp liegen')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.transaction() as con:
            con.executescript('''
                CREATE TABLE IF NOT EXISTS grants (
                    identity TEXT NOT NULL, tool TEXT NOT NULL, plan TEXT NOT NULL CHECK(plan IN ('basic','premium')),
                    active INTEGER NOT NULL CHECK(active IN (0,1)), PRIMARY KEY(identity,tool));
                CREATE TABLE IF NOT EXISTS requests (
                    identity TEXT NOT NULL, tool TEXT NOT NULL, request_id TEXT NOT NULL,
                    month TEXT NOT NULL, request_hash TEXT NOT NULL,
                    state TEXT NOT NULL CHECK(state IN ('reserved','charged','released')),
                    created REAL NOT NULL, PRIMARY KEY(identity,tool,request_id));
            ''')

    @contextmanager
    def transaction(self):
        con = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        try:
            con.execute('BEGIN IMMEDIATE')
            yield con
            con.commit()
        except BaseException:
            con.rollback()
            raise
        finally:
            con.close()

    def grant(self, identity, plan, *, active=True):
        if not identity or plan not in LIMITS:
            raise ValueError('Ungültiges lokales Testkonto')
        with self.transaction() as con:
            con.execute('INSERT INTO grants VALUES (?,?,?,?) ON CONFLICT(identity,tool) DO UPDATE SET plan=excluded.plan,active=excluded.active',
                        (identity, TOOL, plan, int(active)))

    def _grant(self, con, identity):
        row = con.execute('SELECT plan,active FROM grants WHERE identity=? AND tool=?', (identity, TOOL)).fetchone()
        if not row or not row[1]:
            raise QuotaError('Werkzeugzugriff nicht freigegeben')
        return row[0]

    def status(self, identity, *, now=None):
        month = month_key(now)
        with self.transaction() as con:
            plan = self._grant(con, identity)
            rows = dict(con.execute('SELECT state,count(*) FROM requests WHERE identity=? AND tool=? AND month=? GROUP BY state',
                                    (identity, TOOL, month)))
            used, reserved = rows.get('charged', 0), rows.get('reserved', 0)
            return {'plan': plan, 'limit': LIMITS[plan], 'used': used, 'reserved': reserved,
                    'remaining': max(0, LIMITS[plan]-used-reserved), 'month': month}

    def reserve(self, identity, request_id, request_hash, *, now=None):
        if not isinstance(request_id, str) or not 8 <= len(request_id) <= 100 or not request_id.isascii():
            raise ValueError('Gültige Anfragekennung erforderlich')
        month = month_key(now)
        with self.transaction() as con:
            plan = self._grant(con, identity)
            old = con.execute('SELECT request_hash,state FROM requests WHERE identity=? AND tool=? AND request_id=?',
                              (identity, TOOL, request_id)).fetchone()
            if old:
                if old[0] != request_hash:
                    raise QuotaError('Anfragekennung wurde bereits für eine andere Anfrage verwendet')
                return {'duplicate': True, 'state': old[1]}
            timestamp = (now or datetime.now(timezone.utc)).timestamp()
            attempts = con.execute('SELECT count(*) FROM requests WHERE identity=? AND tool=? AND created>?',
                                   (identity, TOOL, timestamp-60)).fetchone()[0]
            if attempts >= 20:
                raise QuotaError('Zu viele Anfragen in kurzer Zeit; bitte kurz warten')
            amount = con.execute("SELECT count(*) FROM requests WHERE identity=? AND tool=? AND month=? AND state IN ('reserved','charged')",
                                 (identity, TOOL, month)).fetchone()[0]
            if amount >= LIMITS[plan]:
                raise QuotaError('Monatskontingent ausgeschöpft')
            con.execute('INSERT INTO requests VALUES (?,?,?,?,?,?,?)',
                        (identity, TOOL, request_id, month, request_hash, 'reserved', timestamp))
            return {'duplicate': False, 'state': 'reserved'}

    def finish(self, identity, request_id, *, charge):
        with self.transaction() as con:
            updated = con.execute("UPDATE requests SET state=? WHERE identity=? AND tool=? AND request_id=? AND state='reserved'",
                                  ('charged' if charge else 'released', identity, TOOL, request_id))
            return updated.rowcount == 1

    def release_expired(self, *, before):
        # Only after the worker has terminated; never release a running request's
        # reservation merely because a browser disconnected.
        with self.transaction() as con:
            return con.execute("UPDATE requests SET state='released' WHERE state='reserved' AND created<?", (before,)).rowcount
