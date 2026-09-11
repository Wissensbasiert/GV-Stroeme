"""Lokaler API-Pilot mit künstlichem Testkonto; kein Portal-/Produktivserver."""
import argparse
import json
from pathlib import Path
import secrets
import sys
from wsgiref.simple_server import make_server, WSGIRequestHandler
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from server.analyseassistent.api import Application
from server.analyseassistent.datasets import Datasets
from server.analyseassistent.quota import LocalQuota
from server.analyseassistent.service import Service

ROOT = Path(__file__).resolve().parents[2]


class QuietHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        pass


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8011)
    parser.add_argument('--plan',choices=['basic','premium'],default='basic')
    parser.add_argument('--state-dir',type=Path,required=True)
    parser.add_argument('--requesty',action='store_true')
    args=parser.parse_args()
    if not 1024<=args.port<=65535:
        parser.error('Port muss zwischen 1024 und 65535 liegen')
    state=args.state_dir.resolve()
    if state==Path('C:/tmp').resolve() or not state.is_relative_to(Path('C:/tmp').resolve()):
        parser.error('Eigener Zustandsordner unter C:\\tmp erforderlich')
    # A random local bearer protects the synthetic account against unrelated
    # localhost clients. This is explicitly not Hanko authentication.
    state.mkdir(parents=True,exist_ok=True)
    token=secrets.token_urlsafe(32)
    (state/'local-token.txt').write_text(token,encoding='utf-8')
    quota=LocalQuota(state/'quota.sqlite')
    quota.grant('local-test',args.plan)
    model=None
    if args.requesty:
        from server.analyseassistent.credentials import load_local_requesty
        model=load_local_requesty()
    service=Service(Datasets(ROOT),model=model)
    origin=f'http://127.0.0.1:{args.port}'
    def identity(env):
        supplied=env.get('HTTP_AUTHORIZATION','')
        return 'local-test' if secrets.compare_digest(supplied,'Bearer '+token) else None
    app=Application(service,quota,identity,allowed_origin=origin)
    print(json.dumps({'local_api':origin+'/api/analyseassistent','model_enabled':bool(model),
                      'plan':args.plan,'token_file':str(state/'local-token.txt')},ensure_ascii=False),flush=True)
    try:
        with make_server('127.0.0.1',args.port,app,handler_class=QuietHandler) as httpd:
            httpd.serve_forever()
    finally:
        (state/'local-token.txt').unlink(missing_ok=True)


if __name__=='__main__': main()
