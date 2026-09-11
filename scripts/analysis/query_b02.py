"""Lokale B02-Zeitreihe; keine Modell- oder Serveranbindung."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import duckdb
from scripts.analysis.b02 import STORE,query_series,resolve_dataset

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset',type=Path,default=STORE)
    p.add_argument('--region',required=True)
    p.add_argument('--mode',required=True,choices=['road','rail','iww'])
    p.add_argument('--direction',default='outbound',choices=['outbound','inbound','total'])
    p.add_argument('--start',type=int,default=2016)
    p.add_argument('--end',type=int,default=2025)
    p.add_argument('--group',default='ALL')
    p.add_argument('--metric',default='tonnes')
    p.add_argument('--partner')
    a=p.parse_args()
    with duckdb.connect() as c:
        result=query_series(c,resolve_dataset(a.dataset),region=a.region,mode=a.mode,
            direction=a.direction,start=a.start,end=a.end,group=a.group,metric=a.metric,partner=a.partner)
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
