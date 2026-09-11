"""Brücke im Plattform-Repository; Aktivierung nur im konfigurierten Testportal."""
import json
import os
from pathlib import Path
import sys
import threading

_endpoint=None
_lock=threading.Lock()


def _create_endpoint():
    from auth import validate_session,hanko_api_url,session_token
    from admin import csrf_token,valid_csrf_token
    from db import database_connection_parameters
    root=Path(__file__).resolve().parents[1]/'private/gueterstroeme'
    if not (root/'server/analyseassistent/portal.py').is_file():
        raise RuntimeError('Privates Werkzeugpaket fehlt')
    if str(root) not in sys.path:
        sys.path.insert(0,str(root))
    from server.analyseassistent.portal import PortalEndpoint,LazyService
    from integration.analyseassistent.postgres_quota import PostgresQuota
    def connect():
        import psycopg
        parameters=database_connection_parameters()
        if parameters is None:
            raise RuntimeError('Portaldatenbank nicht konfiguriert')
        return psycopg.connect(connect_timeout=5,**parameters)
    def service():
        from server.analyseassistent.datasets import Datasets
        from server.analyseassistent.service import Service
        from server.analyseassistent.requesty import Requesty
        return Service(Datasets(root),model=Requesty.from_environment())
    return PortalEndpoint(connect=connect,quota=PostgresQuota(connect),service=LazyService(service),
                          validate_session=validate_session,issuer=hanko_api_url,session_token=session_token,
                          csrf_token=csrf_token,valid_csrf_token=valid_csrf_token,
                          allowed_origin='https://test.portal.wissensbasiert.de')


def application(environ,start_response):
    global _endpoint
    # Explicit activation prevents an accidental production/API exposure when
    # the common portal source is later included in an unrelated release.
    if os.environ.get('WBP_PORTAL_ENVIRONMENT')!='test' or os.environ.get('WBP_GUETERSTROEME_ENABLED')!='1':
        status,message='503 Service Unavailable','Analyseassistent im Testportal noch nicht aktiviert'
    else:
        try:
            with _lock:
                if _endpoint is None:
                    _endpoint=_create_endpoint()
            return _endpoint(environ,start_response)
        except Exception:
            status,message='503 Service Unavailable','Analyseassistent vorübergehend nicht verfügbar'
    body=json.dumps({'error':message},ensure_ascii=False).encode('utf-8')
    start_response(status,[('Content-Type','application/json; charset=utf-8'),('Content-Length',str(len(body))),
                           ('Cache-Control','no-store'),('X-Content-Type-Options','nosniff')])
    return [body]
