"""WSGI-Endpunkt mit injizierter serverseitiger Identität und Kontingentprüfung."""
import json
import io
from .quota import fingerprint, QuotaError
from .dialogue import validate_history


class Application:
    def __init__(self, service, quota, resolve_identity, *, allowed_origin):
        self.service, self.quota = service, quota
        # The portal must supply its Hanko/session + tool-entitlement resolver.
        # Never implement this callback by trusting a browser identity/plan field.
        self.resolve_identity, self.allowed_origin = resolve_identity, allowed_origin

    def __call__(self, environ, start_response):
        # A small, framed body must be consumed before an early 401/403 response.
        # Otherwise a Windows HTTP/1.0 loopback server can reset the connection
        # while unread request bytes remain. Oversized/unframed bodies stay bounded.
        if environ.get('REQUEST_METHOD') == 'POST' and environ.get('PATH_INFO') == '/api/analyseassistent':
            try:
                size = int(environ.get('CONTENT_LENGTH', '0'))
            except (ValueError, TypeError):
                size = 0
            if 1 <= size <= 60000:
                environ = dict(environ)
                environ['wsgi.input'] = io.BytesIO(environ['wsgi.input'].read(size))
        status, result = self.handle(environ)
        data = json.dumps(result, ensure_ascii=False, allow_nan=False).encode('utf-8')
        start_response(status, [('Content-Type', 'application/json; charset=utf-8'),
                                ('Content-Length', str(len(data))), ('Cache-Control', 'no-store'),
                                ('X-Content-Type-Options', 'nosniff')])
        return [data]

    def handle(self, environ):
        if environ.get('PATH_INFO') not in {'/api/analyseassistent', '/api/analyseassistent/quota'}:
            return '404 Not Found', {'error': 'Unbekannte Schnittstelle'}
        try:
            identity = self.resolve_identity(environ)
        except Exception:
            identity = None
        if not identity:
            return '401 Unauthorized', {'error': 'Anmeldung erforderlich'}
        try:
            quota_status = self.quota.status(identity)
        except QuotaError:
            return '403 Forbidden', {'error': 'Werkzeugzugriff nicht freigegeben'}
        except Exception:
            return '503 Service Unavailable', {'error': 'Kontingentprüfung vorübergehend nicht verfügbar'}
        if environ['PATH_INFO'].endswith('/quota'):
            if environ.get('REQUEST_METHOD') == 'GET':
                return '200 OK', quota_status
            return '405 Method Not Allowed', {'error': 'GET erforderlich'}
        if environ.get('REQUEST_METHOD') != 'POST':
            return '405 Method Not Allowed', {'error': 'POST erforderlich'}
        if environ.get('HTTP_ORIGIN') != self.allowed_origin:
            return '403 Forbidden', {'error': 'Anfrageherkunft nicht zulässig'}
        if environ.get('CONTENT_TYPE', '').split(';')[0] != 'application/json':
            return '415 Unsupported Media Type', {'error': 'JSON erforderlich'}
        try:
            size = int(environ.get('CONTENT_LENGTH', '0'))
            if not 1 <= size <= 60000:
                raise ValueError()
            body = json.loads(environ['wsgi.input'].read(size))
            if not isinstance(body, dict) or set(body) - {'question', 'confirmed', 'function', 'request_id', 'history', 'conversation'}:
                raise ValueError()
            question = body['question']
            if not isinstance(question, str) or not question.strip() or len(question) > 4000:
                raise ValueError()
            validate_history(body.get('history'))
            if 'conversation' in body and (not isinstance(body['conversation'], str) or len(body['conversation']) > 24000):
                raise ValueError()
            request_id = body['request_id']
            reservation = self.quota.reserve(identity, request_id, fingerprint(body))
        except (ValueError, KeyError, TypeError):
            return '400 Bad Request', {'error': 'Ungültige oder zu umfangreiche Anfrage'}
        except QuotaError as exc:
            return '429 Too Many Requests', {'error': str(exc)}
        except Exception:
            return '503 Service Unavailable', {'error': 'Anfrage konnte nicht reserviert werden; bitte später erneut versuchen'}
        if reservation['duplicate']:
            return '409 Conflict', {'error': 'Diese Anfrage wurde bereits angenommen; kein erneuter Modellaufruf.', 'state': reservation['state']}
        charge = False
        try:
            options={'function':body.get('function')}
            if body.get('history'):options['history']=body['history']
            if body.get('conversation'):options['conversation']=body['conversation']
            result, _audit = self.service.analyze(question, body.get('confirmed'), **options)
            charge = result['status'] in {'ok', 'partial'} and any(f.get('value') is not None for f in result.get('facts', []))
            response = ('200 OK', {**result, 'request_id': request_id})
        except Exception:
            response = ('500 Internal Server Error', {'error': 'Analyse konnte nicht abgeschlossen werden',
                                                       'request_id':request_id,'diagnostic_code':'AA-X01'})
        try:
            self.quota.finish(identity, request_id, charge=charge)
        except Exception:
            return '503 Service Unavailable', {'error': 'Abschluss der Anfrage konnte nicht bestätigt werden; nicht mit neuer Kennung wiederholen',
                                               'request_id': request_id}
        return response
