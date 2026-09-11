"""Gezielte Nachprüfungen aus Gemini B01–B03; keine Modellaufrufe."""
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
from scripts.analysis.b01 import ROOT,literal,query_relation


def raw_b01(con,dataset,manifest,check):
    """Jede Quellzelle aller drei Kennzahlen, auch außerhalb alter Raumfilter."""
    for source in manifest['sources']:
        con.execute('CREATE OR REPLACE TEMP TABLE independent_raw AS SELECT row_number() OVER () nr,* FROM read_csv('
                    +literal(ROOT/source['path'])+",delim=';',all_varchar=true,encoding="+literal(source['encoding'])+')')
        mode=source['mode']
        fields=({'tonnes':'Tonnen','tkm':'Tkm','trips':'Fahrten'} if mode=='road' else
                {'tonnes':'Befoerderungsmenge_in_Tonnen','tkm':'Befoerderungsleistung_in_TKM','load_units':'Anzahl_Ladeeinheiten'} if mode=='rail' else
                {'tonnes':'Tonnen','tkm':'Tonnen_km','load_carriers':'Anzahl_Ladungstraeger'})
        for metric,field in fields.items():
            value='NULLIF(trim("'+field+'"),\'\')'
            flag='replace(coalesce(trim("ZS_'+field+'"),\'\'),\' \',\'\')' if mode=='road' else "''"
            sql='''WITH raw AS (SELECT nr,'''+value+' raw_text,'+flag+''' flag,
                 TRY_CAST(replace('''+value+''',',','.') AS DOUBLE) number FROM independent_raw),
                 expected AS (SELECT *,CASE WHEN flag IN ('/','.') THEN NULL
                 WHEN flag='-' THEN CASE WHEN raw_text IS NULL OR number=0 THEN 0 ELSE NULL END
                 WHEN number IS NULL OR NOT isfinite(number) OR number<0 OR (flag='0' AND number<>0) THEN NULL
                 ELSE number END AS value FROM raw),
                 saved AS (SELECT * FROM read_parquet(?) WHERE source_id=? AND metric=?)
                 SELECT count(*) FILTER(WHERE a.nr IS NULL OR b.source_record IS NULL
                   OR a.raw_text IS DISTINCT FROM b.raw_value
                   OR (a.value IS NULL)<>(b.value IS NULL)
                   OR abs(a.value-b.value)>greatest(0.00001,abs(a.value)*1e-12)),
                   count(*) FILTER(WHERE NOT b.legacy_scope)
                 FROM expected a FULL JOIN saved b ON a.nr=b.source_record'''
            failures,outside=con.execute(sql,[str(Path(dataset)/'source_values.parquet'),source['id'],metric]).fetchone()
            check('Originalzellen alle Räume '+source['id']+' '+metric,failures==0,{'outside_legacy_cells':outside})
    check('Jede Belegzelle eindeutig',con.execute('SELECT count(*) FROM (SELECT source_id,source_record,metric FROM read_parquet(?) GROUP BY ALL HAVING count(*)<>1)',[str(Path(dataset)/'source_values.parquet')]).fetchone()[0]==0)
    check('Belege außerhalb bisheriger Raumfilter geprüft',con.execute('SELECT count(*) FROM read_parquet(?) WHERE NOT legacy_scope',[str(Path(dataset)/'source_values.parquet')]).fetchone()[0]==3*manifest['row_counts']['outside_legacy_scope'])


def cli(function,dataset,arguments):
    return subprocess.run([sys.executable,str(ROOT/'scripts/analysis'/('query_'+function+'.py')),
                           '--dataset',str(dataset),*arguments],capture_output=True,text=True,encoding='utf-8',
                          env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1'},timeout=90)


def b01_checks(con,dataset,check):
    for bad in ['2024',2024.5,True,None]:
        try:query_relation(con,dataset,year=bad,origin='DEA23',destination='DE600',mode='rail');ok=False
        except ValueError:ok=True
        check('B01 falscher Jahrestyp '+repr(bad),ok)
    p=cli('b01',dataset,['--year','2024','--origin','DEA23','--destination','DE600','--mode','road'])
    r=json.loads(p.stdout) if p.returncode==0 else {}
    check('B01 lokaler Aufruf samt Umlautausgabe',p.returncode==0 and r.get('value')==67757 and r.get('quality')=='restricted')


def b02_checks(con,dataset,check):
    from scripts.analysis.b02 import query_series
    absent=query_series(con,dataset,region='UNKNOWN',mode='rail',start=2024,end=2024)
    check('B02 leere Reihe kein Erfolgsstatus',absent['status']=='missing_row')
    absent=query_series(con,dataset,region='DEE03',mode='rail',start=1900,end=1901)
    check('B02 fehlender Zeitraum eindeutig',absent['status']=='year_not_available')
    thin=query_series(con,dataset,region='DEE06',partner='DEA23',mode='rail',group='4',start=2016,end=2016)
    check('B02 lückenhafte Reihe oben unvollständig',thin['status']=='incomplete')
    for metric in ['tonnes','tkm','load_carriers']:
        for direction in ['outbound','inbound','total']:
            r=query_series(con,dataset,region='DEA12',partner='DEE03',mode='iww',metric=metric,direction=direction,start=2024,end=2024)
            spatial={'outbound':"origin_id='DEA12' AND dest_id='DEE03'",'inbound':"origin_id='DEE03' AND dest_id='DEA12'",
                     'total':"(origin_id='DEA12' AND dest_id='DEE03') OR (origin_id='DEE03' AND dest_id='DEA12')"}[direction]
            expected=con.execute('SELECT sum(known_sum) FROM read_parquet(?) WHERE year_ref=2024 AND mode=\'iww\' AND metric=? AND ('+spatial+')',[str(Path(dataset)/'monthly_od.parquet'),metric]).fetchone()[0]
            actual=r['years'][0]['known_sum']
            check('B02 IWW '+metric+' '+direction,actual==expected)
    p=cli('b02',dataset,['--region','DEA12','--partner','DEE03','--mode','iww','--start','2024','--end','2024'])
    r=json.loads(p.stdout) if p.returncode==0 else {}
    check('B02 lokaler IWW-Aufruf',p.returncode==0 and r.get('mode')=='iww' and r['years'][0]['known_sum']==1947)


def b03_checks(con,dataset,check):
    from scripts.analysis.b03 import query_rail
    con.execute("CREATE OR REPLACE TEMP VIEW unknown_fixture AS SELECT 1 AS month,'031' AS nst_raw,'1' AS group_7_id,1 AS source_rows,NULL::DOUBLE AS known_sum,1 AS missing_count,0 AS restricted_count,0 AS unknown_quality_count,2024 AS year_ref,'tonnes' AS metric,'DEA23' AS origin_id,'DE600' AS dest_id")
    class Fixture:
        def execute(self,sql,args):return con.execute(sql.replace('read_parquet(?)','unknown_fixture'),args[1:])
    r=query_rail(Fixture(),dataset,year=2024,region='DEA23',partner='DE600')
    check('B03 nur unbekannte Werte ergeben keine Nullsumme',r['published_sum'] is None and r['known_sum'] is None)
    p=cli('b03',dataset,['--product','VD2','--year','2024','--region','DE254','--direction','total'])
    check('B03 unzulässige Straßenrichtung verständlich abgewiesen',p.returncode==2 and 'Versand' in p.stderr and 'Traceback' not in p.stderr)
    # Test the real CLI parser/dispatcher in-process against the real data. The
    # release report is deliberately mocked because this test precedes validation.
    from scripts.analysis import query_b03
    import contextlib,io
    original=json.loads
    for product,region in [('rail','DEA23'),('VD2','DE254'),('VD3c','DEA2')]:
        output=io.StringIO()
        class Output(io.StringIO):
            def reconfigure(self,**kwargs):pass
        output=Output()
        original_read=Path.read_text
        def read(path,*args,**kwargs):
            if path==Path(dataset)/'validation.json':
                manifest=original(original_read(Path(dataset)/'manifest.json',encoding='utf-8'))
                return json.dumps({'passed':True,'snapshot_id':manifest['snapshot_id']})
            return original_read(path,*args,**kwargs)
        with patch.object(sys,'argv',['query_b03','--dataset',str(dataset),'--product',product,'--year','2024','--region',region]),patch.object(Path,'read_text',read),contextlib.redirect_stdout(output):
            query_b03.main()
        r=json.loads(output.getvalue())
        check('B03 Argumente und Abfrage '+product,r['year']==2024 and r['region']==region and (bool(r.get('details')) or bool(r.get('rows'))))
