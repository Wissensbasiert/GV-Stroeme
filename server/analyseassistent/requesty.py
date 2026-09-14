"""Begrenzter Requesty-Transport; keine Schlüssel in Ausgaben oder Dateien."""
import json
import math
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler


class ModelError(RuntimeError):
    def __init__(self, message, *, diagnostics=None):
        super().__init__(message)
        self.diagnostics = diagnostics or {}


def incomplete_diagnostics(record, choice, elapsed_ms):
    """Only bounded status and numeric usage; never echo provider error content."""
    reason = choice.get('finish_reason')
    known = {'length', 'content_filter', 'tool_calls', 'function_call'}
    usage = record.get('usage')
    safe_usage = {}
    if isinstance(usage, dict):
        for key in ('prompt_tokens', 'completion_tokens', 'total_tokens', 'cost'):
            value = usage.get(key)
            if type(value) in (int, float) and math.isfinite(value) and value >= 0:
                safe_usage[key] = value
    return {'finish_reason': reason if isinstance(reason, str) and reason in known else 'other',
            'elapsed_ms': elapsed_ms, 'usage': safe_usage}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ModelError('Unerwartete Weiterleitung des Modellaufrufs')


class Requesty:
    native_tools = True

    def chat(self, messages, *, deadline, tools=None, schema=None):
        """Native tool messages, including provider signatures, stay in one dialogue."""
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ModelError('Gesamtfrist erreicht')
        body = {'model': self.model, 'messages': messages, 'max_tokens': max(self.max_tokens, 2500), 'stream': False}
        if tools:
            body.update(tools=tools, tool_choice='auto', parallel_tool_calls=False)
        if schema:
            body['response_format'] = {'type': 'json_schema', 'json_schema': {
                'name': 'grounded_chat', 'strict': True, 'schema': schema}}
        request = Request(self.base_url + '/chat/completions',
                          data=json.dumps(body, ensure_ascii=False, allow_nan=False).encode('utf-8'),
                          headers={'Authorization': 'Bearer ' + self.api_key, 'Content-Type': 'application/json'})
        started = time.monotonic()
        try:
            with self.opener.open(request, timeout=min(remaining, self.timeout_seconds)) as response:
                raw = response.read(1_000_001)
            if len(raw) > 1_000_000 or time.monotonic() > deadline:
                raise ModelError('Modellantwort überschreitet Umfang oder Gesamtfrist')
            record = json.loads(raw)
            choice = record['choices'][0]
            if choice.get('finish_reason') not in {'stop', 'tool_calls'}:
                raise ModelError('Modellantwort nicht vollständig', diagnostics=incomplete_diagnostics(
                    record, choice, round((time.monotonic()-started)*1000)))
            message = choice['message']
            if message.get('role') != 'assistant':
                raise ValueError()
        except HTTPError as exc:
            raise ModelError('Modellschnittstelle meldet HTTP ' + str(exc.code)) from None
        except (URLError, TimeoutError, OSError, KeyError, IndexError, TypeError, ValueError):
            raise ModelError('Modellschnittstelle nicht erreichbar oder Antwortformat ungültig') from None
        return message, {'model': record.get('model', self.model), 'requested_model': self.model,
                         'elapsed_ms': round((time.monotonic()-started)*1000), 'usage': record.get('usage')}

    def __init__(self, *, model, base_url, api_key, timeout_seconds, max_tokens=1500):
        parsed = urlparse(base_url)
        if (parsed.scheme != 'https' or parsed.hostname != 'router.eu.requesty.ai'
                or parsed.path.rstrip('/') != '/v1' or parsed.port not in {None, 443}
                or parsed.username or parsed.password or parsed.query or parsed.fragment):
            raise ValueError('Requesty-Adresse nicht freigegeben')
        if not model or not api_key or not 1 <= timeout_seconds <= 600 or not 128 <= max_tokens <= 8000:
            raise ValueError('Modell, Schlüssel und begrenzte Laufzeitkonfiguration erforderlich')
        self.model, self.base_url, self.api_key = model, base_url.rstrip('/'), api_key
        self.timeout_seconds, self.max_tokens = timeout_seconds, max_tokens
        self.opener = build_opener(NoRedirect())

    @classmethod
    def from_environment(cls):
        required = ['REQUESTY_MODEL', 'REQUESTY_BASE_URL', 'REQUESTY_API_KEY', 'REQUESTY_TIMEOUT_SECONDS']
        if any(not os.environ.get(key) for key in required):
            raise ModelError('Requesty-Konfiguration unvollständig; kein externer Aufruf ausgeführt')
        return cls(model=os.environ['REQUESTY_MODEL'], base_url=os.environ['REQUESTY_BASE_URL'],
                   api_key=os.environ['REQUESTY_API_KEY'], timeout_seconds=float(os.environ['REQUESTY_TIMEOUT_SECONDS']))

    def complete(self, prompt, payload, schema, *, deadline):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ModelError('Gesamtfrist erreicht')
        body = {'model': self.model, 'messages': [
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False, allow_nan=False)}],
            'response_format': ({'type': 'json_object'} if payload['phase'] == 'plan' else
                                {'type': 'json_schema', 'json_schema': {
                                    'name': 'analysis_answer', 'strict': True, 'schema': schema}}),
            'max_tokens': self.max_tokens, 'stream': False}
        request = Request(self.base_url + '/chat/completions',
                          data=json.dumps(body, ensure_ascii=False).encode('utf-8'),
                          headers={'Authorization': 'Bearer ' + self.api_key, 'Content-Type': 'application/json'})
        started = time.monotonic()
        try:
            with self.opener.open(request, timeout=min(remaining, self.timeout_seconds)) as response:
                raw = response.read(1_000_001)
            if len(raw) > 1_000_000 or time.monotonic() > deadline:
                raise ModelError('Modellantwort überschreitet Umfang oder Gesamtfrist')
            record = json.loads(raw)
            choice = record['choices'][0]
            if choice.get('finish_reason') != 'stop':
                raise ModelError('Modellantwort nicht vollständig', diagnostics=incomplete_diagnostics(
                    record, choice, round((time.monotonic()-started)*1000)))
            content = choice['message']['content']
            parsed = json.loads(content)
        except HTTPError as exc:
            raise ModelError('Modellschnittstelle meldet HTTP ' + str(exc.code)) from None
        except (URLError, TimeoutError, OSError, KeyError, IndexError, TypeError, ValueError):
            raise ModelError('Modellschnittstelle nicht erreichbar oder Antwortformat ungültig') from None
        return parsed, {'model': record.get('model', self.model), 'requested_model': self.model,
                        'elapsed_ms': round((time.monotonic()-started)*1000),
                        'usage': record.get('usage'), 'raw_content': content}
