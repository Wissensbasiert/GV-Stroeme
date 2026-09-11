"""Lesbare lokale Ergebnisübersicht aus gespeicherten Modellläufen; kein API-Aufruf."""
import argparse
import hashlib
from html import escape
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
BASE=ROOT/'outputs/analyseassistent_runtime_20260910'
STATUS={'ok':'Antwort vorhanden','partial':'Antwort mit Datenlücken','needs_clarification':'Rückfrage',
        'not_available':'Funktion noch nicht verfügbar','out_of_scope':'Außerhalb des Datenumfangs','error':'Technischer Fehler'}
REVIEW_NOTES={
    'T13':'Das gewünschte Ranking der tatsächlichen Veränderung ist noch nicht implementiert. Der Fall bleibt offen.',
    'T30':'Die erste Modellantwort war unvollständig. Bei der gezielten Nachprüfung wurde eine Rückfrage ausgegeben. Alternative Prognoseszenarien sind damit noch nicht bereitgestellt.',
    'T35':'Der Ablauf stimmt mit dem lokalen Vergleich überein. Die Ausgabe benötigt noch ausgeschriebene Ländernamen bei den Partnern.',
    'T43':'Der Ablauf stimmt mit dem lokalen Vergleich überein. Die konkrete Erklärung der 422/400/22 Gebiete fehlt noch.',
    'T44':'Zunächst wurde ein allgemeiner Quellenhinweis falsch zugeordnet. Die gezielte Nachprüfung lieferte die konkrete Schienenrelation mit identischen Werten und Quellen wie im lokalen Vergleich.'}

def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def items(values): return '<ul>'+''.join('<li>'+escape(str(v))+'</li>' for v in values)+'</ul>'


def render_result(result):
    if result.get('answer'):
        a=result['answer']
        content='<h3>'+escape(a['title'])+'</h3>'
        content+=''.join('<p>'+escape(t)+'</p>' for t in a['paragraphs'])
        if a['questions']: content+=items(a['questions'])
        if a.get('suggestions'): content+='<h3>Diese Fragen kann ich mit vorhandenen Daten weiterverfolgen</h3>'+items(a['suggestions'])
        if a['notes']: content+='<div class="notice"><h3>Was Sie bei der Einordnung beachten sollten</h3>'+items(a['notes'])+'</div>'
        for table in a['tables']:
            content+='<details class="data"><summary>'+escape(table['title'])+'</summary><div class="scroll"><table><thead><tr>'+''.join('<th>'+escape(c)+'</th>' for c in table['columns'])+'</tr></thead><tbody>'
            for row in table['rows']:
                content+='<tr>'+''.join('<td>'+escape(row[k])+'</td>' for k in ['label','value','unit','note'])+'</tr>'
            content+='</tbody></table></div></details>'
        content+='<details class="original"><summary>Quellen und ursprüngliches technisches Ergebnis</summary>'
        content+=render_result({k:v for k,v in result.items() if k!='answer'})+'</details>'
        return content
    content='<h3>Ausgegebene Kurzantwort</h3>'
    content+=items(result['summary']) if result.get('summary') else '<p>Keine numerische Kurzantwort ausgegeben. Die Rückfrage oder Einschränkung steht unten.</p>'
    if result.get('notices'): content+='<div class="notice"><h3>Rückfrage und Hinweise der Anwendung</h3>'+items(result['notices'])+'</div>'
    if result.get('tables'):
        content+='<details class="data"><summary>Tabellen und Belege anzeigen</summary>'
        for table in result['tables']:
            rows=table.get('rows',[])
            content+='<div class="scroll"><table><thead><tr><th>Beleg / Kennwert</th><th>Wert</th><th>Einheit</th><th>Datenhinweis</th></tr></thead><tbody>'
            for row in rows:
                label=row.get('label') or row.get('text') or row.get('name') or row.get('fact_id') or ''
                value=row.get('display_value','–' if row.get('value') is None else str(row['value']))
                value_states={'missing_row':'Keine veröffentlichte Zeile','missing_value':'Wert fehlt',
                              'observed':'Veröffentlichter Wert','reported_zero':'Veröffentlichte Null',
                              'suppressed':'Wert unterdrückt','not_applicable':'Nicht anwendbar'}
                state=value_states.get(row.get('value_status'),'')
                if row.get('quality_status')=='restricted': state+=' · eingeschränkt belastbar'
                content+='<tr>'+''.join('<td>'+escape(str(v))+'</td>' for v in [label,value,row.get('unit',''),state])+'</tr>'
            content+='</tbody></table></div>'
        content+='</details>'
    if result.get('sources'): content+='<h3>Quellen</h3>'+items(result['sources'])
    content+='<details class="data"><summary>Vollständiges Ergebnis für die technische Prüfung</summary><pre>'+escape(json.dumps(result,ensure_ascii=False,indent=2))+'</pre></details>'
    return content


def build(output, *, update=False):
    if output.exists() and not update: raise ValueError('Neuer Berichtsordner oder ausdrückliches --update erforderlich')
    run_dir=BASE/'requesty45_run01'
    run=read(run_dir/'report.json')
    review=read(BASE/'requesty45_review02.json')
    assert review['live_report_sha256']==sha(run_dir/'report.json')
    reviews={x['id']:x for x in review['cases']}
    targeted=BASE/'requesty_targeted02'
    targeted_review={x['id']:x for x in read(targeted/'review.json')['cases']}
    from server.analyseassistent.datasets import Datasets
    from server.analyseassistent.presentation import present
    from server.analyseassistent.alternatives import related_data
    datasets=Datasets(ROOT)
    cards=[]; hashes={}; md=['# Antworten auf die 45 Testfragen', '', 'Stand: 10.09.2026. Erster vollständiger Lauf plus gezielte Nachprüfung von T30 und T44.',
        '', '78 Requesty-Aufrufe. Gesamtkosten laut Nutzerangabe aus dem Requesty-Dashboard: 0,51 USD. Keine vollständige fachliche Abnahme.', '']
    for case in run['cases']:
        id=case['id']; path=run_dir/case['result_file']
        assert sha(path)==case['result_sha256']
        original=read(path); current=original
        hashes[path.relative_to(ROOT).as_posix()]=sha(path)
        rechecked=id in targeted_review
        if rechecked:
            path=targeted/f'{id}_result.json'
            assert sha(path)==targeted_review[id]['result_sha256']
            current=read(path); hashes[path.relative_to(ROOT).as_posix()]=sha(path)
        request=read(run_dir/f'{id}_input.json')
        question,sep,context=request['question'].partition('\nBestätigter Eingabekontext: ')
        result=dict(current['result']); status=result['status']
        assert current['audit']['data_snapshot_id']==datasets.snapshot_id
        result['missing_fields']=current['audit'].get('plan',{}).get('unresolved_fields',[])
        related=related_data(result,datasets)
        if related is not None: result['related_data']=related
        result['answer']=present(result,datasets)
        open_review=id in REVIEW_NOTES and id not in ('T30','T44')
        label=('Gezielt nachgeprüft' if rechecked else 'Ablauf geprüft' if reviews[id]['status']=='route_and_data_checks_passed' else 'Nacharbeit erforderlich')
        search=' '.join([id,question,context,*result.get('summary',[])])
        content=f'<details class="case" id="{id}" data-search="{escape(search.lower(),quote=True)}" data-state="{status}" data-open-review="{str(open_review).lower()}"><summary><span class="case-id">{id}</span><span class="question">{escape(question)}</span><span class="badge">{escape(STATUS[status])}</span></summary><div class="answer">'
        content+=f'<p class="review"><strong>{label}</strong> · '+('Gezielte Nachprüfung; ursprüngliches Ergebnis unten erhalten.' if rechecked else 'Erster vollständiger Lauf.')+'</p>'
        if context: content+='<p class="context"><strong>Testauswahl:</strong> '+escape(context)+'</p>'
        if id in REVIEW_NOTES: content+='<p class="editor"><strong>Prüfhinweis:</strong> '+escape(REVIEW_NOTES[id])+'</p>'
        content+=render_result(result)
        if rechecked: content+='<details class="original"><summary>Ursprüngliches Ergebnis vor der Korrektur</summary>'+render_result(original['result'])+'</details>'
        content+='</div></details>'
        cards.append(content)
        md.extend([f'## {id} – {question}','',f'**Status:** {STATUS[status]} · {label}', '', '**Testauswahl:** '+context,''])
        if id in REVIEW_NOTES: md.extend(['**Prüfhinweis:** '+REVIEW_NOTES[id],''])
        md.extend(['### Ausgegebene Kurzantwort','',*['- '+x for x in result.get('summary',[])], '', '### Rückfrage und Hinweise','',*['- '+x for x in result.get('notices',[])], ''])
        for table in result.get('tables',[]):
            md.extend(['| Beleg / Kennwert | Wert | Einheit |','|---|---:|---|'])
            for row in table.get('rows',[]):
                fields=[row.get('label') or row.get('text') or '',row.get('display_value','–'),row.get('unit','')]
                md.append('| '+' | '.join(str(v).replace('|','\\|').replace('\n',' ') for v in fields)+' |')
            md.append('')
        md.extend(['**Quellen:** '+ '; '.join(result.get('sources',[])), ''])
    template='''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Güterströme – Antworten auf 45 Testfragen</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#F8FAFC;color:#0F172A;font:16px/1.6 Inter,ui-sans-serif,system-ui,sans-serif}header,main,footer{max-width:1140px;margin:auto;padding:32px}header{padding-top:48px}.eyebrow{color:#4C7F83;font-weight:700;letter-spacing:.06em;font-size:13px}h1{font-size:clamp(30px,4vw,44px);line-height:1.15;margin:12px 0 18px;letter-spacing:-.035em}h2{font-size:22px}h3{font-size:16px;margin:24px 0 8px}.intro{max-width:850px;color:#334155}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:30px 0}.stat{background:white;border:1px solid #CBD5E1;border-radius:16px;padding:20px}.stat strong{display:block;font-size:30px;color:#4C7F83}.stat span{font-size:14px}.fine{font-size:14px;color:#475569}.toolbar{position:sticky;top:0;z-index:1;display:flex;flex-wrap:wrap;gap:10px;padding:16px;background:#F8FAFCf5;border:1px solid #CBD5E1;border-radius:14px;margin-bottom:22px}input,select,button,.download{font:inherit;border:1px solid #CBD5E1;background:white;border-radius:8px;padding:9px 12px;color:#0F172A}input{flex:1;min-width:220px}button,.download{cursor:pointer;font-weight:600}button.primary{background:#63B472;color:#0F172A;border-color:#63B472}button:hover,.download:hover{border-color:#4C7F83}a{color:#36676b}.case{background:white;border:1px solid #CBD5E1;border-radius:14px;margin:12px 0;overflow:hidden;scroll-margin-top:110px}.case>summary{display:flex;align-items:center;gap:16px;cursor:pointer;padding:22px;list-style:none}.case>summary:before{content:'+';font-size:24px;color:#4C7F83}.case[open]>summary:before{content:'−'}.case-id{font-weight:800;color:#4C7F83}.question{flex:1;font-weight:600}.badge{font-size:12px;border-radius:20px;background:#edf4f4;padding:5px 10px;white-space:nowrap}.answer{padding:0 24px 24px;border-top:1px solid #e2e8f0}.review{font-size:14px;color:#4C7F83}.context{background:#F8FAFC;padding:14px;border-radius:8px}.editor{border-left:4px solid #A4B3CF;padding:12px 16px;background:#F8FAFC}.notice{border-left:3px solid #BAD267;padding:1px 18px 8px;background:#fafcf5}.data,.original{margin:18px 0}.data>summary,.original>summary{cursor:pointer;font-weight:600;color:#36676b;padding:8px 0}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:10px;border-bottom:1px solid #e2e8f0;vertical-align:top}th{background:#F8FAFC}td:nth-child(2){white-space:nowrap;font-variant-numeric:tabular-nums}pre{max-height:450px;overflow:auto;background:#F8FAFC;padding:15px;font-size:12px}li{margin:6px 0}footer{font-size:13px;color:#475569}.hidden{display:none}#count{margin:0 0 12px;color:#475569;font-size:14px}summary:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #4C7F83;outline-offset:3px}
@media(max-width:700px){header,main,footer{padding:20px}.stats{gap:8px}.stat{padding:12px}.stat strong{font-size:24px}.case>summary{padding:16px;gap:10px;flex-wrap:wrap}.badge{margin-left:45px}.question{min-width:70%}.toolbar{position:static}.answer{padding:0 16px 16px}}
@media print{body{background:white;font-size:10pt}.toolbar,.download,.original,pre{display:none}.case{break-inside:auto}.case>summary{break-after:avoid}.stats{margin:10px 0}header,main,footer{padding:10px}h1{font-size:25pt}.data>summary{display:none}.hidden{display:none!important}}
</style>
<header><div class="eyebrow">WISSENSBASIERTE PLANUNG · GÜTERSTRÖME</div><h1>Die Antworten auf unsere<br>45 Testfragen</h1><p class="intro">Hier stehen die tatsächlich ausgegebenen Kurzantworten, Rückfragen, Tabellen und Quellen. T30 und T44 zeigen zunächst die gezielte Nachprüfung; ihre ursprünglichen Ergebnisse bleiben aufklappbar.</p><div class="stats"><div class="stat"><strong>45</strong><span>Testfragen</span></div><div class="stat"><strong>78</strong><span>Requesty-Aufrufe · 75 + 3</span></div><div class="stat"><strong>0,51 USD</strong><span>Gesamtkosten laut deinem Dashboard</span></div></div><p class="fine">Stand: 10.09.2026 · Kosten von dir aus dem Requesty-Dashboard mitgeteilt. Der erste Lauf bestand bei 42 Fällen die automatische Ablauf- und Datenprüfung; zwei weitere Fälle wurden gezielt erfolgreich nachgeprüft. Eine vollständige fachliche Abnahme steht noch aus. Die Kurzantworten bestehen aus belegten, vom Server formulierten Aussagen, die das Modell auswählt.</p></header>
<main><div class="toolbar"><input id="search" type="search" aria-label="Testfragen durchsuchen" placeholder="Frage, Ort oder Testnummer suchen …"><select id="filter" aria-label="Ergebnisse filtern"><option value="all">Alle Ergebnisse</option><option value="review">Offene fachliche Hinweise</option><option value="needs_clarification">Rückfragen</option><option value="partial">Antworten mit Datenlücken</option></select><button id="expand" class="primary">Alle öffnen</button><button id="print">Drucken / PDF</button></div><p id="count" aria-live="polite">45 Testfragen</p>__CARDS__<p><a class="download" href="ANTWORTEN_TESTFRAGEN.md" download>Alle Antworten als Textdatei herunterladen</a></p></main><footer>Lokale Auswertung gespeicherter Ergebnisse. Beim Öffnen, Suchen und Drucken erfolgen keine KI-Aufrufe. Dieser Bericht verändert das Portal nicht.</footer>
<script>
const cards=[...document.querySelectorAll('.case')],search=document.querySelector('#search'),filter=document.querySelector('#filter');
function apply(){let n=0;for(const c of cards){const visible=c.dataset.search.includes(search.value.toLowerCase())&&(filter.value==='all'||(filter.value==='review'?c.dataset.openReview==='true':c.dataset.state===filter.value));c.classList.toggle('hidden',!visible);if(visible)n++}document.querySelector('#count').textContent=n+' von 45 Testfragen';}
search.addEventListener('input',apply);filter.addEventListener('change',apply);
document.querySelector('#expand').addEventListener('click',()=>{const visible=cards.filter(c=>!c.classList.contains('hidden'));const open=visible.some(c=>!c.open);visible.forEach(c=>c.open=open);document.querySelector('#expand').textContent=open?'Alle schließen':'Alle öffnen'});
document.querySelector('#print').addEventListener('click',()=>{for(const c of cards.filter(c=>!c.classList.contains('hidden'))){c.open=true;c.querySelectorAll('.data').forEach(d=>d.open=true)}window.print()});
if(location.hash){const selected=document.getElementById(location.hash.slice(1));if(selected)selected.open=true;}
</script></html>'''
    output.mkdir(parents=True,exist_ok=update)
    template=template.replace('Hier stehen die tatsächlich ausgegebenen Kurzantworten, Rückfragen, Tabellen und Quellen.',
        'Die Kundendarstellung wird hier mit den überarbeiteten Textbausteinen aus den gespeicherten Ergebnissen gezeigt. Passende Alternativen werden zusätzlich am selben lokalen Datenstand geprüft. Dafür wurde kein neuer Modelllauf ausgeführt. Die ursprünglichen Antworten bleiben unter den Quelldetails erhalten.')
    template=template.replace('Alle Antworten als Textdatei herunterladen','Ursprüngliche Antworten als Textdatei herunterladen')
    (output/'index.html').write_text(template.replace('__CARDS__','\n'.join(cards)),encoding='utf-8')
    (output/'ANTWORTEN_TESTFRAGEN.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    (output/'manifest.json').write_text(json.dumps({'cases':len(cards),'requesty_calls':78,'reported_cost_usd':0.51,
        'cost_source':'Nutzerangabe aus Requesty-Dashboard am 10.09.2026; keine eigene Dashboardabfrage',
        'source_hashes':hashes,'full_factual_acceptance':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return output/'index.html'


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--update',action='store_true',help='Nur die drei erzeugten Lesedateien ersetzen; Modellprotokolle unverändert')
    args=p.parse_args(); print(build(args.output,update=args.update))
