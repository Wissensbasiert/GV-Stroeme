"""Portalanschluss: geprüfte Hanko-Sitzung, Issuer und bestehende Werkzeugrechte."""
import json
import threading
import uuid
from .api import Application
from .quota import QuotaError

ANALYSIS_PATH='/api/tools/gueterstroeme/analysis'
QUOTA_PATH='/api/tools/gueterstroeme/quota'


def resolve_portal_identity(connect, external_user_id, issuer):
    if not issuer or not external_user_id:
        return None
    try:
        external_user_id=str(uuid.UUID(external_user_id))
    except (ValueError, AttributeError, TypeError):
        return None
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL statement_timeout = '5s'")
            cursor.execute('''SELECT id FROM portal_external_identities
                WHERE provider='hanko' AND issuer=%s AND external_user_id=%s''',
                           (issuer,external_user_id))
            row=cursor.fetchone()
            return int(row[0]) if row else None


class LazyService:
    """Initialisiert Daten und Modell erst bei einer zugelassenen Analyse."""
    def __init__(self, factory):
        self.factory=factory
        self.service=None
        self.lock=threading.Lock()

    def analyze(self,*args,**kwargs):
        with self.lock:
            if self.service is None:
                self.service=self.factory()
        return self.service.analyze(*args,**kwargs)


class PortalEndpoint:
    def __init__(self,*,connect,quota,service,validate_session,issuer,session_token,
                 csrf_token,valid_csrf_token,allowed_origin):
        self.connect,self.quota,self.service=connect,quota,service
        self.validate_session,self.issuer=validate_session,issuer
        self.session_token,self.csrf_token,self.valid_csrf_token=session_token,csrf_token,valid_csrf_token
        self.allowed_origin=allowed_origin

    @staticmethod
    def respond(start_response,status,payload):
        body=json.dumps(payload,ensure_ascii=False).encode('utf-8')
        start_response(status,[('Content-Type','application/json; charset=utf-8'),
                              ('Content-Length',str(len(body))),('Cache-Control','no-store'),
                              ('X-Content-Type-Options','nosniff')])
        return [body]

    def __call__(self,environ,start_response):
        path=environ.get('PATH_INFO')
        method=environ.get('REQUEST_METHOD')
        if path not in {ANALYSIS_PATH,QUOTA_PATH}:
            return self.respond(start_response,'404 Not Found',{'error':'Unbekannte Schnittstelle'})
        if method!=('GET' if path==QUOTA_PATH else 'POST'):
            return self.respond(start_response,'405 Method Not Allowed',{'error':'Methode nicht zulässig'})
        try:
            user=self.validate_session(environ)
            issuer=self.issuer()
        except Exception:
            user,issuer=None,None
        if not user or not issuer:
            return self.respond(start_response,'401 Unauthorized',{'error':'Anmeldung erforderlich'})
        token=self.session_token(environ)
        if method=='POST' and (environ.get('HTTP_ORIGIN')!=self.allowed_origin or
                not self.valid_csrf_token(user,token,environ.get('HTTP_X_WBP_CSRF_TOKEN',''))):
            return self.respond(start_response,'403 Forbidden',{'error':'Sitzung oder Anfrageherkunft ungültig; Seite neu laden'})
        try:
            identity=resolve_portal_identity(self.connect,user,issuer)
            if identity is None:
                return self.respond(start_response,'403 Forbidden',{'error':'Werkzeugzugriff nicht freigegeben'})
            if path==QUOTA_PATH:
                status=self.quota.status(identity)
                return self.respond(start_response,'200 OK',{**status,'csrf_token':self.csrf_token(user,token) or ''})
        except QuotaError:
            return self.respond(start_response,'403 Forbidden',{'error':'Werkzeugzugriff nicht freigegeben'})
        except Exception:
            return self.respond(start_response,'503 Service Unavailable',{'error':'Kontingentprüfung vorübergehend nicht verfügbar'})
        # A new local callback closes over the verified identity; no HTTP field
        # can substitute a user ID, package, issuer or count.
        translated=dict(environ,PATH_INFO='/api/analyseassistent')
        application=Application(self.service,self.quota,lambda _:identity,allowed_origin=self.allowed_origin)
        return application(translated,start_response)
