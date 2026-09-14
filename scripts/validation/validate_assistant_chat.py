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
                    'start': 2020, 'end': 2024, 'modes': ['road'], 'metric': 'tonnes'})}}]}, {}
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
    elif args.focus: conversations = conversations[1:4]
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
