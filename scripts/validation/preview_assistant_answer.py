"""Lokale Browserprüfung des echten Antwort-Renderers, ohne Modell/Kundenbuchung."""
import argparse
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT=Path(__file__).resolve().parents[2]
HTML='''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="wbp-gueterstroeme-assistant" content="/api/tools/gueterstroeme">
<title>Lokale Antwortprüfung</title><link rel="stylesheet" href="/style.css">
<style>body{background:#f4f5f6;margin:24px}.ki-modal-body{max-width:960px;margin:auto;display:block;max-height:none}#aiConversation{max-height:none;overflow:visible}.ki-message{margin:20px 0}textarea{width:80%;height:70px}button{padding:10px}</style>
<main class="ki-modal-body"><h2>Lokale Antwortprüfung – keine Modellanfrage</h2>
<div id="aiQuotaLabel"></div><progress id="aiQuotaProgress"></progress><div id="aiQuotaHint"></div><div id="aiStatusNotice"></div>
<div id="aiConversation"></div><form id="aiQuestionForm"><textarea id="aiQuestionInput" aria-label="Testfrage">Gespeicherte Antwort anzeigen</textarea><button type="submit">Antwort anzeigen</button></form><button id="aiNewChat">Neuer Chat</button></main>
<script src="/client.js"></script><script>const client=createAiClient();document.getElementById('aiQuestionForm').addEventListener('submit',e=>{e.preventDefault();client.submit()});client.open();</script></html>'''

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--turn',type=int,default=1)
    parser.add_argument('--port',type=int,default=8798)
    args=parser.parse_args()
    result=json.loads(args.report.read_text(encoding='utf-8'))['turns'][args.turn]['result']
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def send(self,data,kind):
            self.send_response(200);self.send_header('Content-Type',kind);self.end_headers();self.wfile.write(data)
        def do_GET(self):
            if self.path=='/':self.send(HTML.encode(),'text/html; charset=utf-8')
            elif self.path=='/client.js':self.send((ROOT/'js/shared/ai-client.js').read_bytes(),'text/javascript')
            elif self.path=='/style.css':self.send((ROOT/'css/style.css').read_bytes(),'text/css')
            elif self.path=='/api/tools/gueterstroeme/quota':self.send(json.dumps(dict(plan='basic',limit=100,used=0,reserved=0,remaining=100,csrf_token='local-preview-only',month='Lokale Prüfung')).encode(),'application/json')
            else:self.send_error(404)
        def do_POST(self):
            if self.path!='/api/tools/gueterstroeme/analysis':self.send_error(404);return
            self.rfile.read(int(self.headers.get('Content-Length',0)))
            self.send(json.dumps(result,ensure_ascii=False).encode(),'application/json')
    print('Local-only preview on 127.0.0.1:'+str(args.port),flush=True)
    HTTPServer(('127.0.0.1',args.port),Handler).serve_forever()

if __name__=='__main__':main()
