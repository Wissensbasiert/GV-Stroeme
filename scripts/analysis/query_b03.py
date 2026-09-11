"""Gezielte lokale B03-Abfrage ohne KI oder Serverzugriff."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import duckdb
from scripts.analysis.b01 import resolve_dataset
from scripts.analysis.b03 import STORE, query_rail, query_road


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=STORE)
    parser.add_argument('--product', choices=['rail', 'VD2', 'VD3c'], required=True)
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--direction', choices=['outbound','inbound','total'], default='outbound')
    parser.add_argument('--partner')
    parser.add_argument('--nst')
    parser.add_argument('--group', default='ALL')
    parser.add_argument('--population', choices=['I','G'], default='I')
    parser.add_argument('--metric', default='tonnes')
    args = parser.parse_args()
    if args.product != 'rail' and args.direction == 'total':
        parser.error('Bei VD2/VD3c bitte Versand (outbound) oder Empfang (inbound) wählen; beide Richtungen werden nicht addiert.')
    dataset = resolve_dataset(args.dataset)
    validation = json.loads((dataset / 'validation.json').read_text(encoding='utf-8'))
    manifest = json.loads((dataset / 'manifest.json').read_text(encoding='utf-8'))
    if not validation['passed'] or validation['snapshot_id'] != manifest['snapshot_id']:
        raise ValueError('Datenstand nicht geprüft')
    with duckdb.connect() as con:
        common = dict(year=args.year, region=args.region, direction=args.direction, metric=args.metric, partner=args.partner)
        if args.product == 'rail':
            if args.population != 'I': parser.error('I/G gilt nur für KBA-Produkte')
            result = query_rail(con, dataset, **common, nst=args.nst, group=args.group)
        else:
            if args.nst is not None or args.group != 'ALL': parser.error('Keine zusätzliche Güterfilterung der Straßenprodukte; Klassen werden vollständig ausgegeben')
            result = query_road(con, dataset, **common, product=args.product, population=args.population)
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
