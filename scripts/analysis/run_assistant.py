"""Lokale Einzelabfrage oder Bereitschaftsprüfung des vollständigen Testkatalogs."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from server.analyseassistent.datasets import Datasets
from server.analyseassistent.service import Service

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, help='JSON mit question, confirmed und optional function')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--catalog-check', action='store_true')
    parser.add_argument('--requesty', action='store_true', help='Expliziter echter Modellaufruf mit lokal verschlüsselter Konfiguration')
    args = parser.parse_args()
    if args.catalog_check:
        cases = json.loads((ROOT/'tests/analyseassistent/inputs.json').read_text(encoding='utf-8'))
        # Do not load the reference file into the runtime or provider context.
        report = {'mode': 'readiness_only_no_model_calls', 'cases': len(cases),
                  'full_model_run_ready': all(c['preparation_status'] == 'ready' for c in cases),
                  'pending': [{'id': c['id'], 'status': c['preparation_status'], 'note': c['blocking_note']} for c in cases
                              if c['preparation_status'] != 'ready']}
        if args.requesty:
            raise SystemExit('Kein Modelllauf: Vollständige Fallfreigabe steht noch aus.')
    else:
        if args.input is None:
            parser.error('--input oder --catalog-check erforderlich')
        request = json.loads(args.input.read_text(encoding='utf-8'))
        if set(request) - {'question', 'confirmed', 'function', 'history'}:
            raise SystemExit('Unzulässige Eingabefelder; Referenzen nicht als Modelleingabe verwenden')
        model = None
        if args.requesty:
            from server.analyseassistent.credentials import load_local_requesty
            model = load_local_requesty()
        service = Service(Datasets(ROOT), model=model)
        result, audit = service.analyze(request['question'], request.get('confirmed'), function=request.get('function'), history=request.get('history'))
        report = {'mode': 'requesty' if model else 'local_no_model', 'result': result, 'audit': audit}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'output': str(args.output), 'mode': report['mode']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
