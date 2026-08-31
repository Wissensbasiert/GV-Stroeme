"""
Phase 2 ETL: Aggregating freight flows into high-performance cubes using DuckDB & Pandas.
"""

import os
import glob
import json
import duckdb
import pandas as pd

BASE_DIR = r"d:\HiDrive\01_Projekte\WBP-Solutions\Tools\Güterströme"
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
OUT_DIR = os.path.join(BASE_DIR, "data", "processed")

con = duckdb.connect()

# Amtliche NST-2007-Zusammenfassung C1–C7 (siehe nsz-2007.pdf, S. 7–8).
# Sie entspricht den Codes der KBA-Variablen Gueterposition_7.
con.execute("""
    CREATE MACRO nst_c1c7(nst_raw) AS (
        CASE
            WHEN LPAD(SUBSTRING(CAST(nst_raw AS VARCHAR), 1,
                 CASE WHEN LENGTH(CAST(nst_raw AS VARCHAR)) = 3 THEN 2 ELSE 1 END), 2, '0')
                 IN ('01', '02', '03') THEN '1'
            WHEN LPAD(SUBSTRING(CAST(nst_raw AS VARCHAR), 1,
                 CASE WHEN LENGTH(CAST(nst_raw AS VARCHAR)) = 3 THEN 2 ELSE 1 END), 2, '0')
                 IN ('04', '05', '06') THEN '2'
            WHEN LPAD(SUBSTRING(CAST(nst_raw AS VARCHAR), 1,
                 CASE WHEN LENGTH(CAST(nst_raw AS VARCHAR)) = 3 THEN 2 ELSE 1 END), 2, '0')
                 IN ('07', '08', '09') THEN '3'
            WHEN LPAD(SUBSTRING(CAST(nst_raw AS VARCHAR), 1,
                 CASE WHEN LENGTH(CAST(nst_raw AS VARCHAR)) = 3 THEN 2 ELSE 1 END), 2, '0') = '10' THEN '4'
            WHEN LPAD(SUBSTRING(CAST(nst_raw AS VARCHAR), 1,
                 CASE WHEN LENGTH(CAST(nst_raw AS VARCHAR)) = 3 THEN 2 ELSE 1 END), 2, '0')
                 IN ('11', '12', '13') THEN '5'
            WHEN LPAD(SUBSTRING(CAST(nst_raw AS VARCHAR), 1,
                 CASE WHEN LENGTH(CAST(nst_raw AS VARCHAR)) = 3 THEN 2 ELSE 1 END), 2, '0') = '14' THEN '6'
            ELSE '7'
        END
    );
""")

print(">>> 1. Processing KBA VE7 (Road O-D Matrix 2010-2024)...")
ve7_file = os.path.join(RAW_DIR, "Straße", "KBA", "VE7_Verflechtung_NUTS3", "ve7_2010_2024.csv")
con.execute(f"""
    CREATE TABLE road_od AS
    SELECT 
        CAST(Jahr AS INT) AS year_ref,
        Beladeregion AS origin_nuts,
        Entladeregion AS dest_nuts,
        'road' AS mode_transport,
        'ALL' AS group_7_id,
        TRY_CAST(Tonnen AS DOUBLE) AS tonnes,
        TRY_CAST(Tkm AS DOUBLE) AS tkm,
        TRY_CAST(Fahrten AS BIGINT) AS trips
    FROM read_csv('{ve7_file}', delim=';', header=True, all_varchar=True, quote='"', sample_size=-1)
    WHERE Beladeregion IS NOT NULL AND Entladeregion IS NOT NULL;
""")
print(f"    Road O-D rows: {con.execute('SELECT count(*) FROM road_od').fetchone()[0]:,}")

# Nationale Straßen-Verkehrsleistung: Für den Deutschlandwert wird die in der
# VE7 separat ausgewiesene Leistung auf deutschen Straßen verwendet. Die
# regionalen VE12/VE13-Dateien enthalten diese Inlandskomponente nicht.
con.execute(f"""
    CREATE TABLE road_national AS
    SELECT
        CAST(Jahr AS INT) AS year_ref,
        SUM(TRY_CAST(Tonnen AS DOUBLE)) AS tonnes,
        SUM(TRY_CAST(Inlands_tkm AS DOUBLE)) AS tkm
    FROM read_csv('{ve7_file}', delim=';', header=True, all_varchar=True, quote='"', sample_size=-1)
    GROUP BY Jahr;
""")

print(">>> 2. Processing SGV Eisenbahn (Rail 2016-2025)...")
sgv_pattern = os.path.join(RAW_DIR, "SGV OpenData", "eb_opendata_*.csv").replace('\\', '/')
con.execute(f"""
    CREATE TABLE rail_raw AS
    SELECT
        CAST(Referenzzeitraum_Jahr AS INT) AS year_ref,
        Versandregion_NUTS2024 AS origin_nuts,
        Empfangsregion_NUTS2024 AS dest_nuts,
        Guetergruppe_NST2007 AS nst_raw,
        TRY_CAST(REPLACE(Befoerderungsmenge_in_Tonnen, ',', '.') AS DOUBLE) AS tonnes,
        TRY_CAST(REPLACE(Befoerderungsleistung_in_TKM, ',', '.') AS DOUBLE) AS tkm,
        TRY_CAST(Anzahl_Ladeeinheiten AS BIGINT) AS trips
    FROM read_csv('{sgv_pattern}', delim=';', header=True, all_varchar=True,
                  quote='"', sample_size=-1, union_by_name=True, encoding='latin-1');

    CREATE TABLE rail_od AS
    SELECT
        Referenzzeitraum_Jahr AS year_ref,
        Versandregion_NUTS2024 AS origin_nuts,
        Empfangsregion_NUTS2024 AS dest_nuts,
        'rail' AS mode_transport,
        nst_c1c7(Guetergruppe_NST2007) AS group_7_id,
        SUM(TRY_CAST(CAST(Befoerderungsmenge_in_Tonnen AS VARCHAR) AS DOUBLE)) AS tonnes,
        SUM(TRY_CAST(CAST(Befoerderungsleistung_in_TKM AS VARCHAR) AS DOUBLE)) AS tkm,
        SUM(TRY_CAST(Anzahl_Ladeeinheiten AS BIGINT)) AS trips
    FROM (
        SELECT year_ref AS Referenzzeitraum_Jahr,
               origin_nuts AS Versandregion_NUTS2024,
               dest_nuts AS Empfangsregion_NUTS2024,
               nst_raw AS Guetergruppe_NST2007,
               tonnes AS Befoerderungsmenge_in_Tonnen,
               tkm AS Befoerderungsleistung_in_TKM,
               trips AS Anzahl_Ladeeinheiten
        FROM rail_raw
    )
    WHERE Versandregion_NUTS2024 IS NOT NULL AND Empfangsregion_NUTS2024 IS NOT NULL
    GROUP BY year_ref, origin_nuts, dest_nuts, group_7_id;
""")
print(f"    Rail aggregated O-D rows: {con.execute('SELECT count(*) FROM rail_od').fetchone()[0]:,}")

print(">>> 3. Processing IWW Binnenschifffahrt (Inland Waterways 2011-2025)...")
iww_pattern = os.path.join(RAW_DIR, "IWW OpenData", "IWW_OpenData_*.csv").replace('\\', '/')
con.execute(f"""
    CREATE TABLE iww_raw AS
    SELECT
        CAST(Referenzzeitraum_Jahr AS INT) AS year_ref,
        Einladeregion_NUTS3 AS origin_nuts,
        Ausladeregion_NUTS3 AS dest_nuts,
        Einladeregion_ISO AS origin_iso,
        Ausladeregion_ISO AS dest_iso,
        NST2007 AS nst_raw,
        TRY_CAST(REPLACE(Tonnen, ',', '.') AS DOUBLE) AS tonnes,
        TRY_CAST(REPLACE(Tonnen_km, ',', '.') AS DOUBLE) AS tkm,
        TRY_CAST(Anzahl_Ladungstraeger AS BIGINT) AS trips
    FROM read_csv('{iww_pattern}', delim=';', header=True, all_varchar=True,
                  quote='"', sample_size=-1, union_by_name=True);

    CREATE TABLE iww_od AS
    SELECT
        Referenzzeitraum_Jahr AS year_ref,
        COALESCE(Einladeregion_NUTS3, Einladeregion_ISO) AS origin_nuts,
        COALESCE(Ausladeregion_NUTS3, Ausladeregion_ISO) AS dest_nuts,
        'iww' AS mode_transport,
        nst_c1c7(NST2007) AS group_7_id,
        SUM(TRY_CAST(REPLACE(CAST(Tonnen AS VARCHAR), ',', '.') AS DOUBLE)) AS tonnes,
        SUM(TRY_CAST(REPLACE(CAST(Tonnen_km AS VARCHAR), ',', '.') AS DOUBLE)) AS tkm,
        SUM(TRY_CAST(Anzahl_Ladungstraeger AS BIGINT)) AS trips
    FROM (
        SELECT year_ref AS Referenzzeitraum_Jahr,
               origin_nuts AS Einladeregion_NUTS3,
               dest_nuts AS Ausladeregion_NUTS3,
               origin_iso AS Einladeregion_ISO,
               dest_iso AS Ausladeregion_ISO,
               nst_raw AS NST2007,
               tonnes AS Tonnen,
               tkm AS Tonnen_km,
               trips AS Anzahl_Ladungstraeger
        FROM iww_raw
    )
    WHERE Einladeregion_NUTS3 IS NOT NULL AND Ausladeregion_NUTS3 IS NOT NULL
    GROUP BY year_ref, origin_nuts, dest_nuts, group_7_id;
""")
print(f"    IWW aggregated O-D rows: {con.execute('SELECT count(*) FROM iww_od').fetchone()[0]:,}")

print(">>> 4. Combining into Fact O-D Table...")
con.execute("""
    CREATE TABLE fact_od AS
    SELECT * FROM road_od
    UNION ALL
    SELECT * FROM rail_od
    UNION ALL
    SELECT * FROM iww_od;
""")
od_count = con.execute("SELECT count(*) FROM fact_od").fetchone()[0]
print(f"    Total Combined Fact O-D rows: {od_count:,}")

# Export Fact OD as compressed parquet
fact_od_path = os.path.join(OUT_DIR, "fact_od_flows.parquet")
con.execute(f"COPY fact_od TO '{fact_od_path}' (FORMAT PARQUET, COMPRESSION ZSTD);")
print(f"    Saved {fact_od_path} ({os.path.getsize(fact_od_path)//(1024*1024)} MB)")

# ----------------------------------------------------
# 5. Build Regional Summary & Benchmarks
# ----------------------------------------------------
print(">>> 5. Building Regional Fact Summary & Benchmarks...")
con.execute("""
    CREATE TABLE fact_summary AS
    WITH outbound AS (
        SELECT year_ref, origin_nuts AS nuts_id, mode_transport, group_7_id, 'outbound' AS direction,
               SUM(tonnes) AS tonnes, SUM(tkm) AS tkm, SUM(trips) AS trips
        FROM fact_od GROUP BY year_ref, origin_nuts, mode_transport, group_7_id
    ),
    inbound AS (
        SELECT year_ref, dest_nuts AS nuts_id, mode_transport, group_7_id, 'inbound' AS direction,
               SUM(tonnes) AS tonnes, SUM(tkm) AS tkm, SUM(trips) AS trips
        FROM fact_od GROUP BY year_ref, dest_nuts, mode_transport, group_7_id
    )
    SELECT * FROM outbound
    UNION ALL
    SELECT * FROM inbound;
""")

summary_path = os.path.join(OUT_DIR, "fact_regional_summary.parquet")
con.execute(f"COPY fact_summary TO '{summary_path}' (FORMAT PARQUET, COMPRESSION ZSTD);")
print(f"    Saved {summary_path} ({os.path.getsize(summary_path)//1024} KB)")

# Save national benchmark stats as JSON
benchmarks = con.execute("""
    SELECT year_ref, 'road' AS mode_transport, tonnes AS total_tonnes, tkm AS total_tkm
    FROM road_national
    UNION ALL
    SELECT year_ref, 'rail' AS mode_transport, SUM(tonnes) AS total_tonnes, SUM(tkm) AS total_tkm
    FROM rail_raw GROUP BY year_ref
    UNION ALL
    SELECT year_ref, 'iww' AS mode_transport, SUM(tonnes) AS total_tonnes, SUM(tkm) AS total_tkm
    FROM iww_raw GROUP BY year_ref
    ORDER BY year_ref, mode_transport;
""").df()

benchmark_dict = {}
for yr, grp in benchmarks.groupby('year_ref'):
    tot_t = grp['total_tonnes'].sum()
    tot_tkm = grp['total_tkm'].sum()
    benchmark_dict[int(yr)] = {
        "total_tonnes": float(tot_t),
        "total_tkm": float(tot_tkm),
        "modes": {
            row['mode_transport']: {
                "tonnes": float(row['total_tonnes']),
                "tkm": float(row['total_tkm']),
                "share": round(float(row['total_tonnes']) / tot_t, 4)
            }
            for _, row in grp.iterrows()
        }
    }

with open(os.path.join(OUT_DIR, "national_benchmarks.json"), "w", encoding="utf-8") as f:
    json.dump(benchmark_dict, f, ensure_ascii=False, indent=2)
print("    Saved national_benchmarks.json")

print("\n>>> Pipeline Phase 2 completed successfully!")
