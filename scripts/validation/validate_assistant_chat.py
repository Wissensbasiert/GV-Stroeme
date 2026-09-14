"""Begrenzte echte Dialogprüfung ohne Portalbuchung; keine automatische Wiederholung."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from server.analyseassistent.datasets import Datasets
from server.analyseassistent.service import Service
from server.analyseassistent.credentials import load_local_requesty


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--requesty', action='store_true')
    parser.add_argument('--payload-review', action='store_true')
    parser.add_argument('--limit', type=int, default=8, choices=range(1, 10))
    parser.add_argument('--focus', action='store_true', help='Nur zwei Datenlücken und die konkrete Warum-Rückfrage')
    parser.add_argument('--semantic', action='store_true', help='Offene Formulierungen, Zahlwörter, Gegenrichtung und Themenwechsel')
    parser.add_argument('--forecast', action='store_true', help='Mehrregionenprognose, beide Kennwerte und Anschlussfragen')
    parser.add_argument('--goods', action='store_true', help='Originaldialog Leipzig: Gütergruppen, alle Verkehrsträger, seit 2020')
    parser.add_argument('--access', action='store_true', help='Neue Prognose-/NST-/Hafen-/KV-Zugriffe ohne vorgegebene Funktion')
    parser.add_argument('--scope-totals', action='store_true', help='Originaldialoge Duisburg Ausland/Inland und Berlin Gesamtentwicklung')
    parser.add_argument('--scope-recheck', action='store_true', help='Drei gezielte Nachprüfungen der Belegpakete und benannten Inlandsrelation')
    parser.add_argument('--nodes', action='store_true', help='Acht freigegebene Flughafen-, Hafen- und Bestandsregressionen')
    parser.add_argument('--examples', action='store_true', help='Die fünf tatsächlich sichtbaren Vorschaufragen einmal, ohne erfundene Jahresauswahl')
    parser.add_argument('--sample', action='store_true', help='Freie Auswahl aus T02/T04/T05/T07/T16/T20/T22/T35; keine vorgegebene Funktion')
    parser.add_argument('--cases', help='Einbasierte Auswahl der unabhängigen sample-Fragen, durch Komma getrennt')
    args = parser.parse_args()
    if args.output.exists(): raise SystemExit('Neue Ergebnisdatei erforderlich; Wiederholung gesperrt.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('{}\n', encoding='utf-8')
    if args.requesty == args.payload_review:
        raise SystemExit('Genau --requesty oder --payload-review wählen.')
    class ReviewModel:
        native_tools = True
        model = 'offline_payload_review'
        def __init__(self): self.requests = []
        def chat(self, messages, **kwargs):
            self.requests.append({'messages': json.loads(json.dumps(messages)),
                                  'tools': kwargs.get('tools'), 'schema': kwargs.get('schema')})
            if kwargs.get('tools'):
                return {'role': 'assistant', 'tool_calls': [{'id': 'review', 'type': 'function', 'function': {
                    'name': 'relation_history', 'arguments': json.dumps({'origin': 'DEA52', 'destination': 'DEA41',
                    'start': 2020, 'end': 2024, 'modes': ['road'], 'metric': 'tonnes', '_dialogue': {
                    'context': 'new', 'clarification': '', 'time': {'kind': 'explicit', 'count': 0}}})}}]}, {}
            return {'role': 'assistant', 'content': json.dumps({'paragraphs': [
                {'text': 'Für 2024 fehlt der Eintrag.', 'evidence_ids': ['p1']}]})}, {}
    model = ReviewModel() if args.payload_review else load_local_requesty()
    service = Service(Datasets(args.root), model)
    conversations = [
        ['Welche Güter gehen per Schiene von Berlin nach Hamburg?', 'Das aktuellste Jahr', 'Und andersherum?', 'Und wie sieht es dort 2024 aus?'],
        ['Wie viele Tonnen gingen 2020 und 2024 auf der Straße von Dortmund nach Bielefeld? Wie war die Entwicklung?',
         'Warum fehlen denn für 2024 die Angaben?'],
        ['Welche Güter gehen 2026 per Schiene von Berlin nach Hamburg?'],
        ['Wie viele Tonnen gingen 2024 per Binnenschiff von Köln nach Hamburg?'],
        ['Wie hoch waren 2024 die Emissionen von Dortmund nach Bielefeld?'],
    ]
    if args.payload_review: conversations = [conversations[1][:1]]
    elif args.examples:
        from html.parser import HTMLParser
        class ExampleParser(HTMLParser):
            def __init__(self):super().__init__();self.questions=[]
            def handle_starttag(self,tag,attributes):
                attrs=dict(attributes)
                if tag=='button' and 'data-ai-question' in attrs:self.questions.append(attrs['data-ai-question'])
        examples=ExampleParser();examples.feed((args.root/'html/shell-tail.html').read_text(encoding='utf-8'))
        if len(examples.questions)!=5:raise ValueError('Genau fünf aktuelle Vorschaufragen erwartet')
        conversations=[[question] for question in examples.questions]
    elif args.nodes:
        conversations=[['Wie viele Frachtflüge gab es 2024 von Leipzig nach London?', 'Und in Gegenrichtung?', 'Und nur von LEJ nach LHR?'],
            ['Welche fünf internationalen Luftfrachtverbindungen waren 2024 ab Leipzig/Halle nach Tonnen am wichtigsten?', 'Und nur im Inland?'],
            ['Wie viele Tonnen Metalle wurden 2024 aus dem Hamburger Seehafen nach China versandt?'],
            ['Welche Güter flossen 2025 auf dem Binnenschiff von Duisburg ins Ausland?'],
            ['Wie entwickelte sich der gesamte Güterverkehr in Berlin von 2020 bis 2024?']]
    elif args.scope_recheck:
        conversations=[['Welche Güter flossen 2025 auf dem Binnenschiff von Duisburg ins Ausland?'],
            ['Wie entwickelte sich der gesamte Güterverkehr in Berlin von 2020 bis 2024?'],
            ['Wie viel Güterverkehr gab es 2024 von Duisburg nach Magdeburg insgesamt über Straße, Schiene und Binnenschiff?']]
    elif args.scope_totals:
        conversations=[['Welche Güter flossen auf dem Binnenschiff von Duisburg ins Ausland?', '2025', 'Und ins Inland?'],
            ['Wie entwickelte sich der gesamte Güterverkehr in Berlin in den letzten fünf Jahren?', 'Und was ist mit einem Vergleich 2020-2024?'],
            ['Wie viel Güterverkehr gab es 2024 von Duisburg nach Magdeburg insgesamt über Straße, Schiene und Binnenschiff?']]
    elif args.sample:
        conversations = [[question] for question in [
            'Wie viel Güterverkehr erzeugt und empfängt unsere Stadt?',
            'Welche fünf Regionen sind Hamburgs wichtigste Partner im Straßengüterverkehr 2024? Bitte Versand und Empfang zusammen in Tonnen, externe Partner ohne Binnenverkehr.',
            'Wie viel Ladung wurde 2024 zwischen Duisburg und Magdeburg in jeder Richtung transportiert? Bitte Straße, Schiene und Binnenschiff getrennt in Tonnen.',
            'Wie unterscheiden sich Duisburg und Magdeburg 2024 beim Güteraufkommen, Modal Split und bei der Güterstruktur? Alle drei Landverkehrsträger, Versand plus Empfang, in Tonnen.',
            'Welche Gütergruppen wurden 2024 aus Duisburg auf der Straße am meisten versandt? Bitte mit Mengen in Tonnen und Anteilen.',
            'Welche Güter wurden 2024 auf der Straße von Köln nach Hamburg transportiert? Bitte nach Güterarten in Tonnen aufschlüsseln.',
            'Wie hoch war 2024 deutschlandweit der Modal Split der Güterverkehrsleistung auf Straße, Schiene und Binnenschiff in Tonnenkilometern?',
            'Welche fünf internationalen Luftfrachtverbindungen waren 2024 vom Flughafen Leipzig/Halle im Versand am bedeutendsten? Bitte nach Tonnen sortieren.',
        ]]
    elif args.access:
        conversations = [
            ['Wie entwickeln sich in Berlin laut Prognose Metalle und Metallerzeugnisse, die per Schiene versandt werden?', 'Und im Empfang?'],
            ['Wie viele Tonnen Metalle und Metallerzeugnisse wurden 2024 aus Berlin per Schiene versandt? Bitte die NST-Gütergruppe ausweisen.'],
            ['Wie viele Tonnen Metalle und Metallerzeugnisse wurden 2024 im Hamburger Seehafen im Versand umgeschlagen? Bitte nach NST-Gütergruppe.'],
            ['Wie viele Tonnen Metalle wurden 2024 aus dem Hamburger Seehafen nach China versandt?'],
            ['Wie verteilen sich 2024 deutschlandweit die Tonnen im Schienen-KV auf Ladeeinheitentypen?'],
            ['Wie entwickelt sich laut Prognose der Schienenverkehr von Berlin nach Hamburg in Tonnen zwischen 2019 und 2040?'],
        ]
    elif args.goods:
        conversations = [
            ['Welche Güter werden in meinem Kreis (Leipzig) am meisten versandt? Wie hat sich das seit 2020 entwickelt?',
             'Landkreis Leipzig und alle Verkehrsträger'],
            ['Welche Güter werden im Landkreis Leipzig über alle Verkehrsträger am meisten versandt? Wie hat sich das seit 2020 entwickelt?',
             'Und nur die Schiene?', 'Jetzt nur 2022 auf der Straße.'],
        ]
    elif args.forecast:
        conversations = [
            ['Wie entwickelt sich bis 2040 die Schienengüterverkehre in Magdeburg und Duisburg?',
             'Bitte stelle beide Regionen und beide Kennwerte dar', 'na 2040'],
            ['Vergleiche die Prognose 2040 für Duisburg und Magdeburg auf der Schiene in Tonnen und Tonnenkilometern.',
             'Und nur den Empfang?', 'Jetzt die beobachtete Gütermenge 2024 in Berlin auf der Schiene.'],
            ['Zeige die Prognose für Magdeburg für 2035.'],
        ]
    elif args.semantic:
        conversations = [
            ['Welche Güter fließen von meinem Schwarzwald-Baar-Kreis Richtung Hamburg?', 'die letzten fünf Jahre',
             'Und was kommt von dort zu uns zurück?'],
            ['Mich interessieren die Bahntransporte aus Berlin in die Hansestadt Hamburg.', 'Nimm bitte die neuesten verfügbaren fünf Jahre.',
             'Jetzt eine andere Frage: Welche Güter gehen von Köln nach Düsseldorf?'],
            ['Was wurde im letzten Kalenderjahr auf der Straße von Dortmund nach Bielefeld befördert?'],
            ['Wie viele Tonnen gingen 2024 auf der Schiene von Berlin nach Hamburg?'],
        ]
    elif args.focus: conversations = conversations[1:4]
    if args.cases:
        if not args.sample: raise SystemExit('--cases erfordert --sample')
        conversations=[conversations[int(i)-1] for i in args.cases.split(',')]
    report = {'model': service.model.model, 'portal_bookings': 0, 'turns': [], 'full_acceptance': False}
    for questions in conversations:
        conversation = None
        for question in questions:
            if len(report['turns']) >= args.limit: break
            progress = []
            result, audit = service.analyze(question, conversation=conversation, progress=progress.append)
            conversation = result.pop('conversation', None)
            report['turns'].append({'question': question, 'result': result, 'audit': audit, 'progress': progress})
            if args.payload_review: report['outgoing_payloads'] = model.requests
            calls = [c for t in report['turns'] for c in t['audit']['model_calls']]
            report['summary'] = {'turns': len(report['turns']),
                'calls': sum(t['audit']['attempted_model_calls'] for t in report['turns']),
                'tokens': sum((c.get('usage') or {}).get('total_tokens', 0) for c in calls),
                'cost_usd': sum((c.get('usage') or {}).get('cost', 0) for c in calls),
                'errors': sum(t['result']['status'] == 'error' for t in report['turns']),
                'fallbacks': sum(t['result'].get('answer_mode') == 'verified_fallback' for t in report['turns'])}
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
            print(json.dumps({'question': question, 'status': result['status'], 'mode': result.get('answer_mode'),
                              'ms': audit['total_ms'], 'error': audit.get('chat_error') or audit.get('narrative_error')}, ensure_ascii=False), flush=True)
    print(json.dumps(report['summary']), flush=True)


if __name__ == '__main__': main()
