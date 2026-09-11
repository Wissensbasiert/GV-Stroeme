"""Begrenzte B04–B06-Abfrage mit expliziten JSON-Parametern."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import duckdb
from scripts.analysis import b0406 as b
from scripts.analysis.b01 import resolve_dataset

FUNCTIONS={'union':b.query_union,'compare':b.compare_regions,'balance':b.direction_balance,'forecast':b.forecast_ranking,
           'national':b.national,'partners':b.node_partners,'node':b.node_statistics}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('function',choices=FUNCTIONS)
    parser.add_argument('--parameters',required=True,help='JSON-Objekt mit expliziten Parametern')
    parser.add_argument('--dataset',type=Path,default=b.STORE)
    args=parser.parse_args()
    with duckdb.connect() as con:
        result=FUNCTIONS[args.function](con,resolve_dataset(args.dataset),**json.loads(args.parameters))
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
