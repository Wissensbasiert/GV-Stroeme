"""Lokale B01-Abfrage einer vollständigen Relation, keine Modellanbindung."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import duckdb
from scripts.analysis.b01 import DEFAULT_STORE, query_relation, resolve_dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=DEFAULT_STORE)
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--origin', required=True)
    parser.add_argument('--destination', required=True)
    parser.add_argument('--mode', choices=['road', 'rail', 'iww'], required=True)
    parser.add_argument('--group', default='ALL')
    parser.add_argument('--metric', default='tonnes')
    args = parser.parse_args()
    with duckdb.connect() as con:
        result = query_relation(con, resolve_dataset(args.dataset), year=args.year,
                                origin=args.origin, destination=args.destination,
                                mode=args.mode, group=args.group, metric=args.metric)
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
