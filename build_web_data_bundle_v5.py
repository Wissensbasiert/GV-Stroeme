"""
High-Speed Data Bundler v5:
- Fast DuckDB-based ingestion for KBA Road, SGV Rail, IWW Waterway, and MRTM Seeverkehr.
- Precomputes regional summaries and choropleth lookups.
- Partitions relations per region into data/processed/relations/{REGION_ID}.json (< 250 KB per file).
- Eliminates the 512MB monolith for instant browser loading (< 50ms).
"""

import os
import glob
import json
import duckdb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
RELATIONS_DIR = os.path.join(PROCESSED_DIR, "relations")
os.makedirs(RELATIONS_DIR, exist_ok=True)

con = duckdb.connect()

# Amtliche NST-2007-Zusammenfassung C1–C7 (Destatis NST-2007, S. 7–8).
# Diese ist identisch mit Gueterposition_7 im KBA-Produkt VE12/VE13.
# Eine branchenlogische, aber abweichende Siebener-Zusammenfassung ist hier
# unzulässig: C1 umfasst beispielsweise die Abteilungen 01, 02 und 03.
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

# ----------------------------------------------------
# 1. Load Centroids & Seaports
# ----------------------------------------------------
print(">>> 1. Loading Centroids & Seaport Coordinates...")
with open(os.path.join(PROCESSED_DIR, "nuts_centroids_full.json"), "r", encoding="utf-8") as f:
    centroids = json.load(f)

seaports_coords = {
    "DEHAM": {"name": "Hamburg", "lat": 53.535, "lng": 9.975, "country": "DE", "hub_type": "Universal- & Container-Megahub (Elbe)"},
    "DEBRV": {"name": "Bremerhaven", "lat": 53.570, "lng": 8.545, "country": "DE", "hub_type": "Container- & Automobil-Hub (Weser)"},
    "DEWVN": {"name": "Wilhelmshaven", "lat": 53.585, "lng": 8.140, "country": "DE", "hub_type": "Tiefwasser- & Energiehafen (Jade)"},
    "DERSK": {"name": "Rostock", "lat": 54.150, "lng": 12.115, "country": "DE", "hub_type": "Fähr- & Massenguthub Ostsee"},
    "DELBC": {"name": "Lübeck", "lat": 53.895, "lng": 10.705, "country": "DE", "hub_type": "Größter deutscher Ostsee-Fährhafen"},
    "DEBRB": {"name": "Brunsbüttel", "lat": 53.890, "lng": 9.155, "country": "DE", "hub_type": "Chemie-, Massengut- & LNG-Hafen (NOK)"},
    "DEBRE": {"name": "Bremen", "lat": 53.115, "lng": 8.765, "country": "DE", "hub_type": "Industrie- & Stückguthäfen"},
    "DEBKE": {"name": "Brake (Unterweser)", "lat": 53.330, "lng": 8.490, "country": "DE", "hub_type": "Agrar-, Futter- & Holz-Hub"},
    "DESTA": {"name": "Stade (Bützfleth)", "lat": 53.645, "lng": 9.505, "country": "DE", "hub_type": "Industrie-, Chemie- & LNG-Standort"},
    "DEKEL": {"name": "Kiel", "lat": 54.335, "lng": 10.150, "country": "DE", "hub_type": "Skandinavien-Fähren & Passagierhub"},
    "DEEME": {"name": "Emden", "lat": 53.345, "lng": 7.195, "country": "DE", "hub_type": "Führender Automobilumschlagshafen"},
    "DECUX": {"name": "Cuxhaven", "lat": 53.875, "lng": 8.710, "country": "DE", "hub_type": "Offshore-Wind- & RoRo-Hub"},
    "DESAS": {"name": "Sassnitz / Mukran", "lat": 54.495, "lng": 13.630, "country": "DE", "hub_type": "Östlichster Tiefwasserhafen (Rügen)"},
    "DEWIS": {"name": "Wismar", "lat": 53.895, "lng": 11.455, "country": "DE", "hub_type": "Holz-, Agrar- & Baustoffumschlag"},
    "DENOH": {"name": "Nordenham", "lat": 53.500, "lng": 8.495, "country": "DE", "hub_type": "Kohle-, Erz- & Kabelumschlag (Weser)"},
    "DENHA": {"name": "Nordenham", "lat": 53.4833, "lng": 8.4833, "country": "DE", "hub_type": "Kohle-, Erz- & Kabelumschlag (Weser)"},
    "DESTL": {"name": "Stralsund", "lat": 54.3000, "lng": 13.1000, "country": "DE", "hub_type": "Fähr- & Stückguthafen Ostsee"},
    "DEVIW": {"name": "Vierow", "lat": 54.1303, "lng": 13.5724, "country": "DE", "hub_type": "Massengut- & Agrarhafen"},
    "DEBSK": {"name": "Puttgarden", "lat": 54.5008, "lng": 11.2260, "country": "DE", "hub_type": "Fährhafen Fehmarn"},
    "DEPAP": {"name": "Papenburg", "lat": 53.1004, "lng": 7.3652, "country": "DE", "hub_type": "Werft- & Industriehafen"},
    "DELBM": {"name": "Industriehafen Lubmin", "lat": 54.1550, "lng": 13.6433, "country": "DE", "hub_type": "Energie- & Industriehafen"}
}

for k, v in seaports_coords.items():
    if k not in centroids:
        centroids[k] = {"id": k, "name": v["name"], "level": 3, "country": "DE", "lat": v["lat"], "lng": v["lng"]}

de_regions = {k: {"id": k, "name": v.get("name", k), "lng": v.get("lng"), "lat": v.get("lat")}
              for k, v in centroids.items() if k.startswith("DE") and v.get("level") == 3}

with open(os.path.join(PROCESSED_DIR, "web_regions.json"), "w", encoding="utf-8") as f:
    json.dump(de_regions, f, ensure_ascii=False, indent=2)
print(f"    Saved web_regions.json ({len(de_regions)} German regions)")

# ----------------------------------------------------
# 2. Road Commodity Data (KBA VE12 / VE13)
# ----------------------------------------------------
raw_subdirs = os.listdir(RAW_DIR)
stra_name = [d for d in raw_subdirs if "Stra" in d][0]
kba_dir = os.path.join(RAW_DIR, stra_name, "KBA")

kba_subdirs = os.listdir(kba_dir)
ve12_sub = [d for d in kba_subdirs if "VE12" in d][0]
ve13_sub = [d for d in kba_subdirs if "VE13" in d][0]

ve12_file = os.path.join(kba_dir, ve12_sub, "ve12_2010_2024.csv").replace("\\", "/")
ve13_file = os.path.join(kba_dir, ve13_sub, "ve13_2010_2024.csv").replace("\\", "/")

print(">>> 2. Ingesting Road Summary (KBA)...")
con.execute(f"""
    CREATE TABLE kba_road_summary AS
    SELECT 
        CAST(Jahr AS INT) AS year_ref,
        Beladeregion AS nuts_id,
        'outbound' AS direction,
        CAST(Gueterposition_7 AS VARCHAR) AS group_7_id,
        SUM(TRY_CAST(REPLACE(CAST(Tonnen AS VARCHAR), ',', '.') AS DOUBLE)) AS tonnes,
        SUM(TRY_CAST(REPLACE(CAST(Tkm AS VARCHAR), ',', '.') AS DOUBLE)) AS tkm,
        SUM(TRY_CAST(CAST(Fahrten AS VARCHAR) AS BIGINT)) AS trips
    FROM read_csv('{ve12_file}', delim=';', header=True, all_varchar=True, quote='"', sample_size=-1)
    WHERE Beladeregion IS NOT NULL AND Beladeregion LIKE 'DE%' AND CAST(Jahr AS INT) >= 2016
    GROUP BY Jahr, Beladeregion, Gueterposition_7
    UNION ALL
    SELECT 
        CAST(Jahr AS INT) AS year_ref,
        Entladeregion AS nuts_id,
        'inbound' AS direction,
        CAST(Gueterposition_7 AS VARCHAR) AS group_7_id,
        SUM(TRY_CAST(REPLACE(CAST(Tonnen AS VARCHAR), ',', '.') AS DOUBLE)) AS tonnes,
        SUM(TRY_CAST(REPLACE(CAST(Tkm AS VARCHAR), ',', '.') AS DOUBLE)) AS tkm,
        SUM(TRY_CAST(CAST(Fahrten AS VARCHAR) AS BIGINT)) AS trips
    FROM read_csv('{ve13_file}', delim=';', header=True, all_varchar=True, quote='"', sample_size=-1)
    WHERE Entladeregion IS NOT NULL AND Entladeregion LIKE 'DE%' AND CAST(Jahr AS INT) >= 2016
    GROUP BY Jahr, Entladeregion, Gueterposition_7;
""")

# ----------------------------------------------------
# 3. Rail Commodity Data (SGV OpenData)
# ----------------------------------------------------
print(">>> 3. Ingesting Rail Summary (SGV)...")
sgv_pattern = os.path.join(RAW_DIR, "SGV OpenData", "eb_opendata_*.csv").replace('\\', '/')
con.execute(f"""
    CREATE TABLE sgv_rail_raw AS
    SELECT 
        CAST(Referenzzeitraum_Jahr AS INT) AS year_ref,
        Versandregion_NUTS2024 AS origin_nuts,
        Empfangsregion_NUTS2024 AS dest_nuts,
        CAST(Guetergruppe_NST2007 AS VARCHAR) AS nst_raw,
        TRY_CAST(REPLACE(CAST(Befoerderungsmenge_in_Tonnen AS VARCHAR), ',', '.') AS DOUBLE) AS tonnes,
        TRY_CAST(REPLACE(CAST(Befoerderungsleistung_in_TKM AS VARCHAR), ',', '.') AS DOUBLE) AS tkm,
        TRY_CAST(CAST(Anzahl_Ladeeinheiten AS VARCHAR) AS BIGINT) AS trips
    FROM read_csv('{sgv_pattern}', delim=';', header=True, all_varchar=True, quote='"', sample_size=-1, union_by_name=True, encoding='latin-1')
    WHERE CAST(Referenzzeitraum_Jahr AS INT) >= 2016;
""")

con.execute("""
    CREATE TABLE sgv_rail_summary AS
    SELECT 
        year_ref,
        origin_nuts AS nuts_id,
        'outbound' AS direction,
        nst_c1c7(nst_raw) AS group_7_id,
        SUBSTRING(nst_raw, 1, 2) AS division_20_id,
        SUM(tonnes) AS tonnes,
        SUM(tkm) AS tkm,
        SUM(trips) AS trips
    FROM sgv_rail_raw
    WHERE origin_nuts IS NOT NULL AND origin_nuts LIKE 'DE%'
    GROUP BY year_ref, nuts_id, group_7_id, division_20_id
    UNION ALL
    SELECT 
        year_ref,
        dest_nuts AS nuts_id,
        'inbound' AS direction,
        nst_c1c7(nst_raw) AS group_7_id,
        SUBSTRING(nst_raw, 1, 2) AS division_20_id,
        SUM(tonnes) AS tonnes,
        SUM(tkm) AS tkm,
        SUM(trips) AS trips
    FROM sgv_rail_raw
    WHERE dest_nuts IS NOT NULL AND dest_nuts LIKE 'DE%'
    GROUP BY year_ref, nuts_id, group_7_id, division_20_id;
""")

# ----------------------------------------------------
# 4. IWW Commodity Data
# ----------------------------------------------------
print(">>> 4. Ingesting IWW Summary (Binnenschifffahrt)...")
iww_pattern = os.path.join(RAW_DIR, "IWW OpenData", "IWW_OpenData_*.csv").replace('\\', '/')
con.execute(f"""
    CREATE TABLE iww_raw AS
    SELECT 
        CAST(Referenzzeitraum_Jahr AS INT) AS year_ref,
        Einladeregion_NUTS3 AS origin_nuts,
        Ausladeregion_NUTS3 AS dest_nuts,
        CAST(NST2007 AS VARCHAR) AS nst_raw,
        TRY_CAST(REPLACE(CAST(Tonnen AS VARCHAR), ',', '.') AS DOUBLE) AS tonnes,
        TRY_CAST(REPLACE(CAST(Tonnen_km AS VARCHAR), ',', '.') AS DOUBLE) AS tkm,
        TRY_CAST(CAST(Anzahl_Ladungstraeger AS VARCHAR) AS BIGINT) AS trips
    FROM read_csv('{iww_pattern}', delim=';', header=True, all_varchar=True, quote='"', sample_size=-1, union_by_name=True)
    WHERE CAST(Referenzzeitraum_Jahr AS INT) >= 2016;
""")

con.execute("""
    CREATE TABLE iww_summary AS
    SELECT 
        year_ref,
        origin_nuts AS nuts_id,
        'outbound' AS direction,
        nst_c1c7(nst_raw) AS group_7_id,
        LPAD(SUBSTRING(nst_raw, 1, CASE WHEN LENGTH(nst_raw) = 3 THEN 2 ELSE 1 END), 2, '0') AS division_20_id,
        SUM(tonnes) AS tonnes,
        SUM(tkm) AS tkm,
        SUM(trips) AS trips
    FROM iww_raw
    WHERE origin_nuts IS NOT NULL AND origin_nuts LIKE 'DE%'
    GROUP BY year_ref, nuts_id, group_7_id, division_20_id
    UNION ALL
    SELECT 
        year_ref,
        dest_nuts AS nuts_id,
        'inbound' AS direction,
        nst_c1c7(nst_raw) AS group_7_id,
        LPAD(SUBSTRING(nst_raw, 1, CASE WHEN LENGTH(nst_raw) = 3 THEN 2 ELSE 1 END), 2, '0') AS division_20_id,
        SUM(tonnes) AS tonnes,
        SUM(tkm) AS tkm,
        SUM(trips) AS trips
    FROM iww_raw
    WHERE dest_nuts IS NOT NULL AND dest_nuts LIKE 'DE%'
    GROUP BY year_ref, nuts_id, group_7_id, division_20_id;
""")

# ----------------------------------------------------
# 5. Maritime Seeverkehr Data (all available annual files from 2016)
# ----------------------------------------------------
print(">>> 5. Ingesting Maritime Seeverkehr (MRTM)...")
mrtm_files = sorted(glob.glob(os.path.join(RAW_DIR, "MRTM OpenData", "MRTM_OpenData_*.csv")))
mrtm_files_clean = [f.replace('\\', '/') for f in mrtm_files]

con.execute(f"""
    CREATE TABLE mrtm_cached AS
    SELECT 
        CAST(Referenzzeitraum_Jahr AS INT) AS year_ref,
        Einladeregion_ISO,
        Einladeregion_ISO_Label,
        Einladeregion_UNLOCODE,
        Einladeregion_HafenID_Label,
        Ausladeregion_ISO,
        Ausladeregion_ISO_Label,
        Ausladeregion_UNLOCODE,
        Ausladeregion_HafenID_Label,
        CAST(NST2007 AS VARCHAR) AS nst_raw,
        TRY_CAST(REPLACE(CAST(Guetergewicht AS VARCHAR), ',', '.') AS DOUBLE) AS tonnes,
        TRY_CAST(REPLACE(CAST(TEU AS VARCHAR), ',', '.') AS DOUBLE) AS teu,
        TRY_CAST(CAST(Anzahl_Ladungstraeger AS VARCHAR) AS BIGINT) AS units
    FROM read_csv({mrtm_files_clean}, delim=';', header=True, all_varchar=True, quote='"', sample_size=-1, union_by_name=True)
    WHERE CAST(Referenzzeitraum_Jahr AS INT) >= 2016
      AND (Ausladeregion_ISO = 'DE' OR Einladeregion_ISO = 'DE');
""")

# Seaports Aggregation
seaports_agg = con.execute("""
    WITH port_calls AS (
        SELECT year_ref, Ausladeregion_UNLOCODE AS unlocode,
               Ausladeregion_HafenID_Label AS hafen_name, tonnes, teu, units
        FROM mrtm_cached WHERE Ausladeregion_ISO = 'DE'
        UNION ALL
        SELECT year_ref, Einladeregion_UNLOCODE AS unlocode,
               Einladeregion_HafenID_Label AS hafen_name, tonnes, teu, units
        FROM mrtm_cached WHERE Einladeregion_ISO = 'DE'
    )
    SELECT year_ref, unlocode, hafen_name,
           SUM(tonnes) AS tonnes, SUM(teu) AS teu, SUM(units) AS units
    FROM port_calls
    GROUP BY year_ref, unlocode, hafen_name
    HAVING tonnes > 400000;
""").fetchall()

seaports_web = {}
for r in seaports_agg:
    yr, code, name, t, teu, units = r
    if yr not in seaports_web:
        seaports_web[yr] = {}
    
    clean_code = code if code in seaports_coords else ("DEHAM" if "Hamburg" in (name or "") else ("DEBRV" if "Bremerhaven" in (name or "") else ("DERSK" if "Rostock" in (name or "") else code)))
    coord = seaports_coords.get(clean_code)
    if not coord:
        print(f"    Skipping seaport without verified coordinate: {clean_code} ({name})")
        continue
    
    seaports_web[yr][clean_code] = {
        "unlocode": clean_code,
        "name": name or coord.get("name", clean_code),
        "lat": coord["lat"],
        "lng": coord["lng"],
        "hub_type": coord.get("hub_type", "Seehafen"),
        "tonnes": round(float(t or 0), 1),
        "teu": round(float(teu or 0), 1) if teu else 0.0,
        "units": int(units or 0)
    }

# Partners Aggregation
partners_agg = con.execute("""
    SELECT 
        year_ref,
        CASE WHEN Ausladeregion_ISO = 'DE' THEN Einladeregion_ISO_Label ELSE Ausladeregion_ISO_Label END AS partner_name,
        CASE WHEN Ausladeregion_ISO = 'DE' THEN Einladeregion_ISO ELSE Ausladeregion_ISO END AS iso,
        SUM(tonnes) AS tonnes,
        SUM(teu) AS teu
    FROM mrtm_cached
    WHERE Einladeregion_ISO != Ausladeregion_ISO
    GROUP BY year_ref, partner_name, iso
    ORDER BY year_ref, tonnes DESC;
""").fetchall()

partners_web = {}
for r in partners_agg:
    yr, name, iso, t, teu = r
    if yr not in partners_web:
        partners_web[yr] = []
    if len(partners_web[yr]) < 15 and name:
        main_goods_map = {
            "US": "Container, Fahrzeuge, Chemie & Energie",
            "SE": "RoRo, Forstprodukte, Papier & Holz",
            "CN": "Container, Elektronik, Konsumgüter",
            "NO": "Rohöl, Gas, Erze & NE-Metalle",
            "GB": "RoRo-Fährverkehr, Mineralöl, Chemie",
            "FI": "Papier, Zellstoff, RoRo-Verkehre",
            "DK": "Fährverkehre, Baustoffe, Agrar",
            "NL": "Feeder-Container, Mineralölprodukte",
            "CA": "Erze, Getreide, Holzpellets",
            "BR": "Eisenerz, Soja & Agrarprodukte",
            "PL": "Massengüter, Fährverkehr, Kohle",
            "SG": "Transshipment Container, Fernost-Route",
            "RU": "Historisch: Rohöl, Kohle (rückläufig)"
        }
        partners_web[yr].append({
            "iso": iso,
            "name": name,
            "tonnes": round(float(t or 0), 1),
            "teu": round(float(teu or 0), 1) if teu else 0.0,
            "main_goods": main_goods_map.get(iso, "Container, Massengüter & Stückgut")
        })

# Commodity breakdown for Seeverkehr
mrtm_nst_agg = con.execute("""
    SELECT 
        year_ref,
        nst_raw,
        SUM(tonnes) AS tonnes
    FROM mrtm_cached
    GROUP BY year_ref, nst_raw;
""").fetchall()

mrtm_nst_web = {}
for r in mrtm_nst_agg:
    yr, nst_raw, t = r
    if yr not in mrtm_nst_web:
        mrtm_nst_web[yr] = {"groups_7": {}, "divisions_20": {}}
    
    nst_str = str(nst_raw or "").strip()
    if not nst_str:
        continue
    div = nst_str.zfill(3)[:2] if len(nst_str) == 3 else nst_str.zfill(2)
    div_num = int(div) if div.isdigit() else 20
    div_key = f"{div_num:02d}"

    if div_num in [1, 2, 3]: g7 = "1"
    elif div_num in [4, 5, 6]: g7 = "2"
    elif div_num in [7, 8, 9]: g7 = "3"
    elif div_num == 10: g7 = "4"
    elif div_num in [11, 12, 13]: g7 = "5"
    elif div_num == 14: g7 = "6"
    else: g7 = "7"

    t_val = float(t or 0)
    mrtm_nst_web[yr]["groups_7"][g7] = mrtm_nst_web[yr]["groups_7"].get(g7, 0.0) + t_val
    mrtm_nst_web[yr]["divisions_20"][div_key] = mrtm_nst_web[yr]["divisions_20"].get(div_key, 0.0) + t_val

for yr in mrtm_nst_web:
    mrtm_nst_web[yr]["groups_7"] = {k: round(v, 1) for k, v in mrtm_nst_web[yr]["groups_7"].items()}
    mrtm_nst_web[yr]["divisions_20"] = {k: round(v, 1) for k, v in mrtm_nst_web[yr]["divisions_20"].items()}

maritime_bundle = {
    "seaports": seaports_web,
    "partner_countries": partners_web,
    "commodities": mrtm_nst_web
}
with open(os.path.join(PROCESSED_DIR, "web_maritime.json"), "w", encoding="utf-8") as f:
    json.dump(maritime_bundle, f, ensure_ascii=False, indent=2)
print("    Saved web_maritime.json")

# ----------------------------------------------------
# 6. Combined Regional Summaries & Fact Cubes
# ----------------------------------------------------
print(">>> 6. Building Regional Fact Cubes...")
con.execute("""
    CREATE TABLE all_regional_modes AS
    SELECT year_ref, nuts_id, 'road' AS mode_transport, direction, group_7_id, '00' AS division_20_id, tonnes, tkm, trips
    FROM kba_road_summary
    UNION ALL
    SELECT year_ref, nuts_id, 'rail' AS mode_transport, direction, group_7_id, division_20_id, tonnes, tkm, trips
    FROM sgv_rail_summary
    UNION ALL
    SELECT year_ref, nuts_id, 'iww' AS mode_transport, direction, group_7_id, division_20_id, tonnes, tkm, trips
    FROM iww_summary;
""")

reg_summary_agg = con.execute("""
    SELECT 
        nuts_id,
        year_ref,
        mode_transport,
        direction,
        group_7_id,
        division_20_id,
        SUM(tonnes) AS tonnes,
        SUM(tkm) AS tkm,
        SUM(trips) AS trips
    FROM all_regional_modes
    GROUP BY nuts_id, year_ref, mode_transport, direction, group_7_id, division_20_id;
""").fetchall()

divisions_to_group7 = {
    "01": "1", "02": "1", "03": "1",
    "04": "2", "05": "2", "06": "2",
    "07": "3", "08": "3", "09": "3",
    "10": "4", "11": "5", "12": "5", "13": "5", "14": "6",
    "15": "7", "16": "7", "17": "7", "18": "7", "19": "7", "20": "7"
}
# Die KBA-Dateien VE12/VE13 liefern auf NUTS-3-Ebene ausschließlich die
# amtlichen zusammengefassten Güterpositionen 1–7. Eine Verteilung auf die
# 20 NST-Abteilungen wäre eine nicht belegte Modellannahme und wird daher
# nicht erzeugt.
group7_to_div_shares = {str(i): {} for i in range(1, 8)}

web_summaries = {}
for r in reg_summary_agg:
    n_id, yr_val, mode, direct, g7, div20, t, tkm, tr = r
    try:
        yr = int(yr_val)
    except:
        continue
    if yr < 2016:
        continue
    
    if n_id not in web_summaries:
        web_summaries[n_id] = {}
    if yr not in web_summaries[n_id]:
        web_summaries[n_id][yr] = {
            "total_tonnes": 0.0, "total_tkm": 0.0, "total_trips": 0,
            "modes_tonnes": {"road": 0.0, "rail": 0.0, "iww": 0.0},
            "modes_tkm": {"road": 0.0, "rail": 0.0, "iww": 0.0},
            "modes_direction_tonnes": {
                "road": {"inbound": 0.0, "outbound": 0.0},
                "rail": {"inbound": 0.0, "outbound": 0.0},
                "iww": {"inbound": 0.0, "outbound": 0.0}
            },
            "modes_direction_tkm": {
                "road": {"inbound": 0.0, "outbound": 0.0},
                "rail": {"inbound": 0.0, "outbound": 0.0},
                "iww": {"inbound": 0.0, "outbound": 0.0}
            },
            "directions_tonnes": {"inbound": 0.0, "outbound": 0.0},
            "directions_tkm": {"inbound": 0.0, "outbound": 0.0},
            "groups_7_tonnes": {"all": {}, "inbound": {}, "outbound": {}},
            "groups_7_tkm": {"all": {}, "inbound": {}, "outbound": {}},
            "divisions_20_tonnes": {"all": {}, "inbound": {}, "outbound": {}},
            "divisions_20_tkm": {"all": {}, "inbound": {}, "outbound": {}},
            "by_mode_groups": {
                "road": {"all": {}, "inbound": {}, "outbound": {}},
                "rail": {"all": {}, "inbound": {}, "outbound": {}},
                "iww": {"all": {}, "inbound": {}, "outbound": {}}
            },
            "by_mode_groups_tkm": {
                "road": {"all": {}, "inbound": {}, "outbound": {}},
                "rail": {"all": {}, "inbound": {}, "outbound": {}},
                "iww": {"all": {}, "inbound": {}, "outbound": {}}
            },
            "by_mode_divisions": {
                "road": {"all": {}, "inbound": {}, "outbound": {}},
                "rail": {"all": {}, "inbound": {}, "outbound": {}},
                "iww": {"all": {}, "inbound": {}, "outbound": {}}
            },
            "by_mode_divisions_tkm": {
                "road": {"all": {}, "inbound": {}, "outbound": {}},
                "rail": {"all": {}, "inbound": {}, "outbound": {}},
                "iww": {"all": {}, "inbound": {}, "outbound": {}}
            },
            "data_quality": {
                "road_divisions_20": "nicht verfügbar: KBA VE12/VE13 stellt auf NUTS-3-Ebene nur die amtlichen Güterpositionen 1–7 bereit"
            }
        }
    
    t_val = float(t or 0)
    tkm_val = float(tkm or 0)
    tr_val = int(tr or 0)

    p = web_summaries[n_id][yr]
    p["total_tonnes"] += t_val
    p["total_tkm"] += tkm_val
    p["total_trips"] += tr_val

    p["modes_tonnes"][mode] = p["modes_tonnes"].get(mode, 0.0) + t_val
    p["modes_tkm"][mode] = p["modes_tkm"].get(mode, 0.0) + tkm_val

    if direct in ["inbound", "outbound"]:
        p["modes_direction_tonnes"][mode][direct] += t_val
        p["modes_direction_tkm"][mode][direct] += tkm_val
        p["directions_tonnes"][direct] += t_val
        p["directions_tkm"][direct] += tkm_val

    clean_g7 = str(g7).strip()
    if clean_g7 in ["1", "2", "3", "4", "5", "6", "7"]:
        p["groups_7_tonnes"]["all"][clean_g7] = p["groups_7_tonnes"]["all"].get(clean_g7, 0.0) + t_val
        p["groups_7_tkm"]["all"][clean_g7] = p["groups_7_tkm"]["all"].get(clean_g7, 0.0) + tkm_val
        if direct in ["inbound", "outbound"]:
            p["groups_7_tonnes"][direct][clean_g7] = p["groups_7_tonnes"][direct].get(clean_g7, 0.0) + t_val
            p["groups_7_tkm"][direct][clean_g7] = p["groups_7_tkm"][direct].get(clean_g7, 0.0) + tkm_val

        p["by_mode_groups"][mode]["all"][clean_g7] = p["by_mode_groups"][mode]["all"].get(clean_g7, 0.0) + t_val
        p["by_mode_groups_tkm"][mode]["all"][clean_g7] = p["by_mode_groups_tkm"][mode]["all"].get(clean_g7, 0.0) + tkm_val
        if direct in ["inbound", "outbound"]:
            p["by_mode_groups"][mode][direct][clean_g7] = p["by_mode_groups"][mode][direct].get(clean_g7, 0.0) + t_val
            p["by_mode_groups_tkm"][mode][direct][clean_g7] = p["by_mode_groups_tkm"][mode][direct].get(clean_g7, 0.0) + tkm_val

        if mode == "road":
            shares = group7_to_div_shares.get(clean_g7, {})
            for div_k, share_v in shares.items():
                d_t = t_val * share_v
                d_tkm = tkm_val * share_v
                p["divisions_20_tonnes"]["all"][div_k] = p["divisions_20_tonnes"]["all"].get(div_k, 0.0) + d_t
                p["divisions_20_tkm"]["all"][div_k] = p["divisions_20_tkm"]["all"].get(div_k, 0.0) + d_tkm
                p["by_mode_divisions"][mode]["all"][div_k] = p["by_mode_divisions"][mode]["all"].get(div_k, 0.0) + d_t
                p["by_mode_divisions_tkm"][mode]["all"][div_k] = p["by_mode_divisions_tkm"][mode]["all"].get(div_k, 0.0) + d_tkm

                if direct in ["inbound", "outbound"]:
                    p["divisions_20_tonnes"][direct][div_k] = p["divisions_20_tonnes"][direct].get(div_k, 0.0) + d_t
                    p["divisions_20_tkm"][direct][div_k] = p["divisions_20_tkm"][direct].get(div_k, 0.0) + d_tkm
                    p["by_mode_divisions"][mode][direct][div_k] = p["by_mode_divisions"][mode][direct].get(div_k, 0.0) + d_t
                    p["by_mode_divisions_tkm"][mode][direct][div_k] = p["by_mode_divisions_tkm"][mode][direct].get(div_k, 0.0) + d_tkm

    if mode in ["rail", "iww"]:
        clean_div = str(div20).strip().zfill(2)
        if clean_div in divisions_to_group7:
            p["divisions_20_tonnes"]["all"][clean_div] = p["divisions_20_tonnes"]["all"].get(clean_div, 0.0) + t_val
            p["divisions_20_tkm"]["all"][clean_div] = p["divisions_20_tkm"]["all"].get(clean_div, 0.0) + tkm_val
            p["by_mode_divisions"][mode]["all"][clean_div] = p["by_mode_divisions"][mode]["all"].get(clean_div, 0.0) + t_val
            p["by_mode_divisions_tkm"][mode]["all"][clean_div] = p["by_mode_divisions_tkm"][mode]["all"].get(clean_div, 0.0) + tkm_val

            if direct in ["inbound", "outbound"]:
                p["divisions_20_tonnes"][direct][clean_div] = p["divisions_20_tonnes"][direct].get(clean_div, 0.0) + t_val
                p["divisions_20_tkm"][direct][clean_div] = p["divisions_20_tkm"][direct].get(clean_div, 0.0) + tkm_val
                p["by_mode_divisions"][mode][direct][clean_div] = p["by_mode_divisions"][mode][direct].get(clean_div, 0.0) + t_val
                p["by_mode_divisions_tkm"][mode][direct][clean_div] = p["by_mode_divisions_tkm"][mode][direct].get(clean_div, 0.0) + tkm_val

# Clean & Round
for n_id in web_summaries:
    for yr in web_summaries[n_id]:
        p = web_summaries[n_id][yr]
        p["total_tonnes"] = round(p["total_tonnes"], 1)
        p["total_tkm"] = round(p["total_tkm"], 1)
        p["balance_tonnes"] = round(p["directions_tonnes"].get("outbound", 0) - p["directions_tonnes"].get("inbound", 0), 1)
        p["balance_tkm"] = round(p["directions_tkm"].get("outbound", 0) - p["directions_tkm"].get("inbound", 0), 1)
        
        p["modes_tonnes"] = {k: round(v, 1) for k, v in p["modes_tonnes"].items()}
        p["modes_tkm"] = {k: round(v, 1) for k, v in p["modes_tkm"].items()}
        for m in p["modes_direction_tonnes"]:
            p["modes_direction_tonnes"][m] = {k: round(v, 1) for k, v in p["modes_direction_tonnes"][m].items()}
        for m in p["modes_direction_tkm"]:
            p["modes_direction_tkm"][m] = {k: round(v, 1) for k, v in p["modes_direction_tkm"][m].items()}
        p["directions_tonnes"] = {k: round(v, 1) for k, v in p["directions_tonnes"].items()}
        p["directions_tkm"] = {k: round(v, 1) for k, v in p["directions_tkm"].items()}

        for d in ["all", "inbound", "outbound"]:
            p["groups_7_tonnes"][d] = {k: round(v, 1) for k, v in p["groups_7_tonnes"][d].items()}
            p["groups_7_tkm"][d] = {k: round(v, 1) for k, v in p["groups_7_tkm"][d].items()}
            p["divisions_20_tonnes"][d] = {k: round(v, 1) for k, v in p["divisions_20_tonnes"][d].items()}
            p["divisions_20_tkm"][d] = {k: round(v, 1) for k, v in p["divisions_20_tkm"][d].items()}

        for m in p["by_mode_groups"]:
            for d in ["all", "inbound", "outbound"]:
                p["by_mode_groups"][m][d] = {k: round(v, 1) for k, v in p["by_mode_groups"][m][d].items()}
                p["by_mode_groups_tkm"][m][d] = {k: round(v, 1) for k, v in p["by_mode_groups_tkm"][m][d].items()}
        for m in p["by_mode_divisions"]:
            for d in ["all", "inbound", "outbound"]:
                p["by_mode_divisions"][m][d] = {k: round(v, 1) for k, v in p["by_mode_divisions"][m][d].items()}
                p["by_mode_divisions_tkm"][m][d] = {k: round(v, 1) for k, v in p["by_mode_divisions_tkm"][m][d].items()}

with open(os.path.join(PROCESSED_DIR, "web_summary_by_region.json"), "w", encoding="utf-8") as f:
    json.dump(web_summaries, f, ensure_ascii=False)
print(f"    Saved web_summary_by_region.json ({len(web_summaries)} regions)")

# ----------------------------------------------------
# 7. Choropleth Map Lookup with Mode & Direction Precomputations
# ----------------------------------------------------
print(">>> 7. Precomputing Choropleth Map Lookups with Mode & Direction...")
choro_web = {}
for n_id, yrs in web_summaries.items():
    for yr, p in yrs.items():
        if yr not in choro_web:
            choro_web[yr] = {}
        
        rd_in_t = p["modes_direction_tonnes"]["road"]["inbound"]
        rd_out_t = p["modes_direction_tonnes"]["road"]["outbound"]
        rl_in_t = p["modes_direction_tonnes"]["rail"]["inbound"]
        rl_out_t = p["modes_direction_tonnes"]["rail"]["outbound"]
        iw_in_t = p["modes_direction_tonnes"]["iww"]["inbound"]
        iw_out_t = p["modes_direction_tonnes"]["iww"]["outbound"]

        rd_in_tkm = p["modes_direction_tkm"]["road"]["inbound"]
        rd_out_tkm = p["modes_direction_tkm"]["road"]["outbound"]
        rl_in_tkm = p["modes_direction_tkm"]["rail"]["inbound"]
        rl_out_tkm = p["modes_direction_tkm"]["rail"]["outbound"]
        iw_in_tkm = p["modes_direction_tkm"]["iww"]["inbound"]
        iw_out_tkm = p["modes_direction_tkm"]["iww"]["outbound"]

        choro_web[yr][n_id] = {
            "total_tonnes": p["total_tonnes"],
            "total_tkm": p["total_tkm"],
            "inbound_tonnes": p["directions_tonnes"].get("inbound", 0),
            "outbound_tonnes": p["directions_tonnes"].get("outbound", 0),
            "balance_tonnes": p["balance_tonnes"],
            "inbound_tkm": p["directions_tkm"].get("inbound", 0),
            "outbound_tkm": p["directions_tkm"].get("outbound", 0),
            "balance_tkm": p["balance_tkm"],

            "road_tonnes": p["modes_tonnes"].get("road", 0),
            "road_tkm": p["modes_tkm"].get("road", 0),
            "road_inbound_tonnes": rd_in_t,
            "road_outbound_tonnes": rd_out_t,
            "road_balance_tonnes": round(rd_out_t - rd_in_t, 1),
            "road_inbound_tkm": rd_in_tkm,
            "road_outbound_tkm": rd_out_tkm,
            "road_balance_tkm": round(rd_out_tkm - rd_in_tkm, 1),

            "rail_tonnes": p["modes_tonnes"].get("rail", 0),
            "rail_tkm": p["modes_tkm"].get("rail", 0),
            "rail_inbound_tonnes": rl_in_t,
            "rail_outbound_tonnes": rl_out_t,
            "rail_balance_tonnes": round(rl_out_t - rl_in_t, 1),
            "rail_inbound_tkm": rl_in_tkm,
            "rail_outbound_tkm": rl_out_tkm,
            "rail_balance_tkm": round(rl_out_tkm - rl_in_tkm, 1),

            "iww_tonnes": p["modes_tonnes"].get("iww", 0),
            "iww_tkm": p["modes_tkm"].get("iww", 0),
            "iww_inbound_tonnes": iw_in_t,
            "iww_outbound_tonnes": iw_out_t,
            "iww_balance_tonnes": round(iw_out_t - iw_in_t, 1),
            "iww_inbound_tkm": iw_in_tkm,
            "iww_outbound_tkm": iw_out_tkm,
            "iww_balance_tkm": round(iw_out_tkm - iw_in_tkm, 1)
        }

with open(os.path.join(PROCESSED_DIR, "web_choropleth.json"), "w", encoding="utf-8") as f:
    json.dump(choro_web, f, ensure_ascii=False)
print("    Saved web_choropleth.json")

# ----------------------------------------------------
# 8. Partitioned Regional Top Relations (Sub-JSONs per Region)
# ----------------------------------------------------
print(">>> 8. Precomputing Partitioned Regional Top Relations...")
fact_od_path = os.path.join(PROCESSED_DIR, 'fact_od_flows.parquet').replace('\\', '/')
con.execute(f"CREATE VIEW fact_od_view AS SELECT * FROM '{fact_od_path}';")

# Top relations for the overview.  Both selectable measures must be represented:
# the browser sorts these retained candidates after the user chooses tonnes or
# tonne-kilometres.  Keeping only a tonnes ranking would hide valid top-tkm
# relations before the UI can apply that choice.
top_out = con.execute("""
    WITH yearly AS (
        SELECT origin_nuts, dest_nuts, year_ref, SUM(tonnes) as tonnes, SUM(tkm) as tkm, SUM(trips) as trips
        FROM fact_od_view
        -- A regional relation needs a German origin, but its partner may be
        -- domestic or foreign.  Pure foreign transit is not a regional
        -- German relation and is therefore still outside this view.
        WHERE origin_nuts LIKE 'DE%'
          AND dest_nuts IS NOT NULL AND dest_nuts <> ''
        GROUP BY origin_nuts, dest_nuts, year_ref
    ),
    ranked AS (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY origin_nuts, year_ref ORDER BY tonnes DESC, dest_nuts) as rnk_tonnes,
               ROW_NUMBER() OVER (PARTITION BY origin_nuts, year_ref ORDER BY tkm DESC, dest_nuts) as rnk_tkm
        FROM yearly
    )
    SELECT curr.origin_nuts, curr.year_ref, curr.dest_nuts, curr.tonnes, curr.tkm, curr.trips,
           prev.tonnes as tonnes_prev, past10.tonnes as tonnes_10yr
    FROM ranked curr
    LEFT JOIN yearly prev ON curr.origin_nuts = prev.origin_nuts AND curr.dest_nuts = prev.dest_nuts AND prev.year_ref = curr.year_ref - 1
    LEFT JOIN yearly past10 ON curr.origin_nuts = past10.origin_nuts AND curr.dest_nuts = past10.dest_nuts AND past10.year_ref = curr.year_ref - 10
    WHERE curr.rnk_tonnes <= 25 OR curr.rnk_tkm <= 25;
""").fetchall()

# Top 25 Inbound
top_in = con.execute("""
    WITH yearly AS (
        SELECT dest_nuts, origin_nuts, year_ref, SUM(tonnes) as tonnes, SUM(tkm) as tkm, SUM(trips) as trips
        FROM fact_od_view
        -- Mirror the outbound scope: German destinations retain domestic and
        -- foreign origins.  Map rendering handles partners without a usable
        -- coordinate separately, but they remain visible in the ranking.
        WHERE dest_nuts LIKE 'DE%'
          AND origin_nuts IS NOT NULL AND origin_nuts <> ''
        GROUP BY dest_nuts, origin_nuts, year_ref
    ),
    ranked AS (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY dest_nuts, year_ref ORDER BY tonnes DESC, origin_nuts) as rnk_tonnes,
               ROW_NUMBER() OVER (PARTITION BY dest_nuts, year_ref ORDER BY tkm DESC, origin_nuts) as rnk_tkm
        FROM yearly
    )
    SELECT curr.dest_nuts, curr.year_ref, curr.origin_nuts, curr.tonnes, curr.tkm, curr.trips,
           prev.tonnes as tonnes_prev, past10.tonnes as tonnes_10yr
    FROM ranked curr
    LEFT JOIN yearly prev ON curr.dest_nuts = prev.dest_nuts AND curr.origin_nuts = prev.origin_nuts AND prev.year_ref = curr.year_ref - 1
    LEFT JOIN yearly past10 ON curr.dest_nuts = past10.dest_nuts AND curr.origin_nuts = past10.origin_nuts AND past10.year_ref = curr.year_ref - 10
    WHERE curr.rnk_tonnes <= 25 OR curr.rnk_tkm <= 25;
""").fetchall()

# Mode-specific relations are retained in two complementary views:
# - an all-goods candidate list for the unfiltered view;
# - a separate candidate list for each NST-7 group.
#
# Ranking a mixed-goods list first and filtering it later was the cause of
# valid small goods groups appearing as if no relations had been recorded.
# Both views retain the top 25 by tonnes *and* top 25 by tonne-kilometres.
by_mode = con.execute("""
    WITH yearly_mode AS (
        SELECT origin_nuts, dest_nuts, year_ref, mode_transport, group_7_id, SUM(tonnes) as tonnes, SUM(tkm) as tkm
        FROM fact_od_view
        -- Keep every relation with a German side.  This includes imports and
        -- exports, while excluding pure foreign transit.  Partners without a
        -- usable coordinate stay in the table with an explicit map note.
        WHERE (origin_nuts LIKE 'DE%' AND dest_nuts IS NOT NULL AND dest_nuts <> '')
           OR (dest_nuts LIKE 'DE%' AND origin_nuts IS NOT NULL AND origin_nuts <> '')
        GROUP BY origin_nuts, dest_nuts, year_ref, mode_transport, group_7_id
    ),
    ranked_out AS (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY origin_nuts, year_ref, mode_transport ORDER BY tonnes DESC, dest_nuts) as rnk_all_tonnes,
               ROW_NUMBER() OVER (PARTITION BY origin_nuts, year_ref, mode_transport ORDER BY tkm DESC, dest_nuts) as rnk_all_tkm,
               ROW_NUMBER() OVER (PARTITION BY origin_nuts, year_ref, mode_transport, group_7_id ORDER BY tonnes DESC, dest_nuts) as rnk_group_tonnes,
               ROW_NUMBER() OVER (PARTITION BY origin_nuts, year_ref, mode_transport, group_7_id ORDER BY tkm DESC, dest_nuts) as rnk_group_tkm
        FROM yearly_mode
        WHERE origin_nuts LIKE 'DE%'
    ),
    ranked_in AS (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY dest_nuts, year_ref, mode_transport ORDER BY tonnes DESC, origin_nuts) as rnk_all_tonnes,
               ROW_NUMBER() OVER (PARTITION BY dest_nuts, year_ref, mode_transport ORDER BY tkm DESC, origin_nuts) as rnk_all_tkm,
               ROW_NUMBER() OVER (PARTITION BY dest_nuts, year_ref, mode_transport, group_7_id ORDER BY tonnes DESC, origin_nuts) as rnk_group_tonnes,
               ROW_NUMBER() OVER (PARTITION BY dest_nuts, year_ref, mode_transport, group_7_id ORDER BY tkm DESC, origin_nuts) as rnk_group_tkm
        FROM yearly_mode
        WHERE dest_nuts LIKE 'DE%'
    )
    SELECT curr.origin_nuts, curr.dest_nuts, curr.year_ref, curr.mode_transport, curr.group_7_id, curr.tonnes, curr.tkm,
           curr.rnk_all_tonnes, curr.rnk_all_tkm, curr.rnk_group_tonnes, curr.rnk_group_tkm,
           (
               curr.rnk_all_tonnes <= 25 OR curr.rnk_all_tkm <= 25
               OR next.rnk_all_tonnes <= 25 OR next.rnk_all_tkm <= 25
           ) AS keep_all,
           (
               curr.rnk_group_tonnes <= 25 OR curr.rnk_group_tkm <= 25
               OR next.rnk_group_tonnes <= 25 OR next.rnk_group_tkm <= 25
           ) AS keep_group,
           'outbound' AS relation_direction
    FROM ranked_out curr
    LEFT JOIN ranked_out next
      ON curr.origin_nuts = next.origin_nuts
     AND curr.dest_nuts = next.dest_nuts
     AND curr.mode_transport = next.mode_transport
     AND curr.group_7_id = next.group_7_id
     AND curr.year_ref = next.year_ref - 1
    WHERE curr.rnk_all_tonnes <= 25 OR curr.rnk_all_tkm <= 25
       OR curr.rnk_group_tonnes <= 25 OR curr.rnk_group_tkm <= 25
       OR next.rnk_all_tonnes <= 25 OR next.rnk_all_tkm <= 25
       OR next.rnk_group_tonnes <= 25 OR next.rnk_group_tkm <= 25
    UNION ALL
    SELECT curr.origin_nuts, curr.dest_nuts, curr.year_ref, curr.mode_transport, curr.group_7_id, curr.tonnes, curr.tkm,
           curr.rnk_all_tonnes, curr.rnk_all_tkm, curr.rnk_group_tonnes, curr.rnk_group_tkm,
           (
               curr.rnk_all_tonnes <= 25 OR curr.rnk_all_tkm <= 25
               OR next.rnk_all_tonnes <= 25 OR next.rnk_all_tkm <= 25
           ) AS keep_all,
           (
               curr.rnk_group_tonnes <= 25 OR curr.rnk_group_tkm <= 25
               OR next.rnk_group_tonnes <= 25 OR next.rnk_group_tkm <= 25
           ) AS keep_group,
           'inbound' AS relation_direction
    FROM ranked_in curr
    LEFT JOIN ranked_in next
      ON curr.origin_nuts = next.origin_nuts
     AND curr.dest_nuts = next.dest_nuts
     AND curr.mode_transport = next.mode_transport
     AND curr.group_7_id = next.group_7_id
     AND curr.year_ref = next.year_ref - 1
    WHERE curr.rnk_all_tonnes <= 25 OR curr.rnk_all_tkm <= 25
       OR curr.rnk_group_tonnes <= 25 OR curr.rnk_group_tkm <= 25
       OR next.rnk_all_tonnes <= 25 OR next.rnk_all_tkm <= 25
       OR next.rnk_group_tonnes <= 25 OR next.rnk_group_tkm <= 25;
""").fetchall()

top_bundle = {reg: {} for reg in de_regions}

for r in top_out:
    o_id, yr, d_id, t, tkm, tr, t_prev, t_10 = r
    yr_s = str(yr)
    if o_id not in top_bundle:
        top_bundle[o_id] = {}
    if yr_s not in top_bundle[o_id]:
        top_bundle[o_id][yr_s] = {
            "outbound_overall": [], "inbound_overall": [],
            "by_mode": {"road": {"outbound": [], "inbound": [], "by_group": {}}, "rail": {"outbound": [], "inbound": [], "by_group": {}}, "iww": {"outbound": [], "inbound": [], "by_group": {}}}
        }
    yoy_pct = round(((float(t) - float(t_prev)) / float(t_prev)) * 100, 1) if t_prev and float(t_prev) > 0 else None
    trend_10yr_pct = round(((float(t) - float(t_10)) / float(t_10)) * 100, 1) if t_10 and float(t_10) > 0 else None
    d_info = centroids.get(d_id, {})
    top_bundle[o_id][yr_s]["outbound_overall"].append({
        "dest_id": d_id,
        "dest_name": d_info.get("name", d_id),
        "dest_lng": d_info.get("lng"),
        "dest_lat": d_info.get("lat"),
        "tonnes": round(float(t or 0), 1),
        "tkm": round(float(tkm or 0), 1),
        "is_binnen": (o_id == d_id),
        "yoy_pct": yoy_pct,
        "trend_10yr_pct": trend_10yr_pct
    })

for r in top_in:
    d_id, yr, o_id, t, tkm, tr, t_prev, t_10 = r
    yr_s = str(yr)
    if d_id not in top_bundle:
        top_bundle[d_id] = {}
    if yr_s not in top_bundle[d_id]:
        top_bundle[d_id][yr_s] = {
            "outbound_overall": [], "inbound_overall": [],
            "by_mode": {"road": {"outbound": [], "inbound": [], "by_group": {}}, "rail": {"outbound": [], "inbound": [], "by_group": {}}, "iww": {"outbound": [], "inbound": [], "by_group": {}}}
        }
    yoy_pct = round(((float(t) - float(t_prev)) / float(t_prev)) * 100, 1) if t_prev and float(t_prev) > 0 else None
    trend_10yr_pct = round(((float(t) - float(t_10)) / float(t_10)) * 100, 1) if t_10 and float(t_10) > 0 else None
    o_info = centroids.get(o_id, {})
    top_bundle[d_id][yr_s]["inbound_overall"].append({
        "origin_id": o_id,
        "origin_name": o_info.get("name", o_id),
        "origin_lng": o_info.get("lng"),
        "origin_lat": o_info.get("lat"),
        "tonnes": round(float(t or 0), 1),
        "tkm": round(float(tkm or 0), 1),
        "is_binnen": (o_id == d_id),
        "yoy_pct": yoy_pct,
        "trend_10yr_pct": trend_10yr_pct
    })

for r in by_mode:
    o_id, d_id, yr, mode, g7, t, tkm, rnk_all_tonnes, rnk_all_tkm, rnk_group_tonnes, rnk_group_tkm, keep_all, keep_group, relation_direction = r
    yr_s = str(yr)
    if mode in ["road", "rail", "iww"]:
        # Keep the same relation in the preceding year when it becomes visible
        # in the following year's Top-X.  The browser can then calculate an
        # exact Vorjahresvergleich even when that older value is not itself a
        # top-ranked relation.
        is_top_all = bool(keep_all)
        is_top_group = g7 != "ALL" and bool(keep_group)
        if relation_direction == "outbound" and o_id in top_bundle and yr_s in top_bundle[o_id]:
            d_info = centroids.get(d_id, {})
            relation = {
                "dest_id": d_id,
                "dest_name": d_info.get("name", d_id),
                "dest_lng": d_info.get("lng"),
                "dest_lat": d_info.get("lat"),
                "group_7": str(g7),
                "tonnes": round(float(t or 0), 1),
                "tkm": round(float(tkm or 0), 1),
                "is_binnen": (o_id == d_id)
            }
            if is_top_all:
                top_bundle[o_id][yr_s]["by_mode"][mode]["outbound"].append(relation)
            if is_top_group:
                by_group = top_bundle[o_id][yr_s]["by_mode"][mode].setdefault("by_group", {})
                by_group.setdefault(str(g7), {"outbound": [], "inbound": []})["outbound"].append(relation)
        if relation_direction == "inbound" and d_id in top_bundle and yr_s in top_bundle[d_id]:
            o_info = centroids.get(o_id, {})
            relation = {
                "origin_id": o_id,
                "origin_name": o_info.get("name", o_id),
                "origin_lng": o_info.get("lng"),
                "origin_lat": o_info.get("lat"),
                "group_7": str(g7),
                "tonnes": round(float(t or 0), 1),
                "tkm": round(float(tkm or 0), 1),
                "is_binnen": (o_id == d_id)
            }
            if is_top_all:
                top_bundle[d_id][yr_s]["by_mode"][mode]["inbound"].append(relation)
            if is_top_group:
                by_group = top_bundle[d_id][yr_s]["by_mode"][mode].setdefault("by_group", {})
                by_group.setdefault(str(g7), {"outbound": [], "inbound": []})["inbound"].append(relation)

for reg, rdata in top_bundle.items():
    rfp = os.path.join(RELATIONS_DIR, f"{reg}.json")
    with open(rfp, "w", encoding="utf-8") as f:
        json.dump(rdata, f, ensure_ascii=False)

print(f"    Saved {len(top_bundle)} partitioned relation files in {RELATIONS_DIR}")

# Remove or truncate the 512MB monolith file to prevent browser hanging
old_monolith = os.path.join(PROCESSED_DIR, "web_top_relations.json")
if os.path.exists(old_monolith):
    # Overwrite with empty object or lightweight fallback
    with open(old_monolith, "w", encoding="utf-8") as f:
        json.dump({}, f)
    print("    Cleared old 512MB web_top_relations.json")

print("\n>>> Pipeline v5 completed successfully!")
