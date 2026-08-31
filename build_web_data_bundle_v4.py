"""
High-Speed Data Bundler v4:
Optimized single-pass ETL for KBA Road, SGV Rail, IWW Waterway, and MRTM Seeverkehr.
"""

import os
import glob
import json
import duckdb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

con = duckdb.connect()

# ----------------------------------------------------
# 1. Load Centroids & Seaports
# ----------------------------------------------------
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
    "DENOH": {"name": "Nordenham", "lat": 53.500, "lng": 8.495, "country": "DE", "hub_type": "Kohle-, Erz- & Kabelumschlag (Weser)"}
}

for k, v in seaports_coords.items():
    if k not in centroids:
        centroids[k] = {"id": k, "name": v["name"], "level": 3, "country": "DE", "lat": v["lat"], "lng": v["lng"]}

de_regions = {k: {"id": k, "name": v.get("name", k), "lng": v.get("lng"), "lat": v.get("lat")}
              for k, v in centroids.items() if k.startswith("DE") and v.get("level") == 3}

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

print(">>> 1. Ingesting Road Summary...")
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
    FROM read_csv('{ve12_file}', delim=';', header=True, ignore_errors=True)
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
    FROM read_csv('{ve13_file}', delim=';', header=True, ignore_errors=True)
    WHERE Entladeregion IS NOT NULL AND Entladeregion LIKE 'DE%' AND CAST(Jahr AS INT) >= 2016
    GROUP BY Jahr, Entladeregion, Gueterposition_7;
""")

# ----------------------------------------------------
# 3. Rail Commodity Data (SGV OpenData)
# ----------------------------------------------------
print(">>> 2. Ingesting Rail Summary...")
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
    FROM read_csv('{sgv_pattern}', delim=';', header=True, ignore_errors=True, encoding='latin-1')
    WHERE CAST(Referenzzeitraum_Jahr AS INT) >= 2016;
""")

con.execute("""
    CREATE TABLE sgv_rail_summary AS
    SELECT 
        year_ref,
        origin_nuts AS nuts_id,
        'outbound' AS direction,
        CASE 
            WHEN nst_raw IN ('011','012','013','014','015','016','017','018','019','041','042','043','044','045','046','047','048','049') THEN '1'
            WHEN nst_raw IN ('021','022','023','071','072','081','082','083','084','085','086','087') THEN '2'
            WHEN nst_raw IN ('031','032','033','034','035','036','101','102','103','104','105') THEN '3'
            WHEN nst_raw IN ('091','092','093','094','095') THEN '4'
            WHEN nst_raw IN ('051','052','061','062','063','111','112','113','114','115') THEN '5'
            WHEN nst_raw IN ('121','122','131','132','141','142') THEN '6'
            ELSE '7'
        END AS group_7_id,
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
        CASE 
            WHEN nst_raw IN ('011','012','013','014','015','016','017','018','019','041','042','043','044','045','046','047','048','049') THEN '1'
            WHEN nst_raw IN ('021','022','023','071','072','081','082','083','084','085','086','087') THEN '2'
            WHEN nst_raw IN ('031','032','033','034','035','036','101','102','103','104','105') THEN '3'
            WHEN nst_raw IN ('091','092','093','094','095') THEN '4'
            WHEN nst_raw IN ('051','052','061','062','063','111','112','113','114','115') THEN '5'
            WHEN nst_raw IN ('121','122','131','132','141','142') THEN '6'
            ELSE '7'
        END AS group_7_id,
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
print(">>> 3. Ingesting IWW Summary...")
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
    FROM read_csv('{iww_pattern}', delim=';', header=True, ignore_errors=True)
    WHERE CAST(Referenzzeitraum_Jahr AS INT) >= 2016;
""")

con.execute("""
    CREATE TABLE iww_summary AS
    SELECT 
        year_ref,
        origin_nuts AS nuts_id,
        'outbound' AS direction,
        CASE 
            WHEN nst_raw LIKE '1%' OR nst_raw LIKE '4%' THEN '1'
            WHEN nst_raw LIKE '2%' OR nst_raw LIKE '7%' OR nst_raw LIKE '8%' THEN '2'
            WHEN nst_raw LIKE '3%' OR nst_raw LIKE '10%' THEN '3'
            WHEN nst_raw LIKE '9%' THEN '4'
            WHEN nst_raw LIKE '5%' OR nst_raw LIKE '6%' OR nst_raw LIKE '11%' THEN '5'
            WHEN nst_raw LIKE '12%' OR nst_raw LIKE '13%' OR nst_raw LIKE '14%' THEN '6'
            ELSE '7'
        END AS group_7_id,
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
        CASE 
            WHEN nst_raw LIKE '1%' OR nst_raw LIKE '4%' THEN '1'
            WHEN nst_raw LIKE '2%' OR nst_raw LIKE '7%' OR nst_raw LIKE '8%' THEN '2'
            WHEN nst_raw LIKE '3%' OR nst_raw LIKE '10%' THEN '3'
            WHEN nst_raw LIKE '9%' THEN '4'
            WHEN nst_raw LIKE '5%' OR nst_raw LIKE '6%' OR nst_raw LIKE '11%' THEN '5'
            WHEN nst_raw LIKE '12%' OR nst_raw LIKE '13%' OR nst_raw LIKE '14%' THEN '6'
            ELSE '7'
        END AS group_7_id,
        LPAD(SUBSTRING(nst_raw, 1, CASE WHEN LENGTH(nst_raw) = 3 THEN 2 ELSE 1 END), 2, '0') AS division_20_id,
        SUM(tonnes) AS tonnes,
        SUM(tkm) AS tkm,
        SUM(trips) AS trips
    FROM iww_raw
    WHERE dest_nuts IS NOT NULL AND dest_nuts LIKE 'DE%'
    GROUP BY year_ref, nuts_id, group_7_id, division_20_id;
""")

# ----------------------------------------------------
# 5. Maritime Seeverkehr Data (2016-2025 single-pass load)
# ----------------------------------------------------
print(">>> 4. Ingesting Maritime Seeverkehr...")
mrtm_files = glob.glob(os.path.join(RAW_DIR, "MRTM OpenData", "MRTM_OpenData_201[6-9].csv")) + \
             glob.glob(os.path.join(RAW_DIR, "MRTM OpenData", "MRTM_OpenData_202[0-5].csv"))
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
    FROM read_csv({mrtm_files_clean}, delim=';', header=True, ignore_errors=True)
    WHERE Ausladeregion_ISO = 'DE' OR Einladeregion_ISO = 'DE';
""")

# Seaports Aggregation
seaports_agg = con.execute("""
    SELECT 
        year_ref,
        CASE WHEN Ausladeregion_ISO = 'DE' THEN Ausladeregion_UNLOCODE ELSE Einladeregion_UNLOCODE END AS unlocode,
        CASE WHEN Ausladeregion_ISO = 'DE' THEN Ausladeregion_HafenID_Label ELSE Einladeregion_HafenID_Label END AS hafen_name,
        SUM(tonnes) AS tonnes,
        SUM(teu) AS teu,
        SUM(units) AS units
    FROM mrtm_cached
    GROUP BY year_ref, unlocode, hafen_name
    HAVING tonnes > 400000;
""").fetchall()

seaports_web = {}
for r in seaports_agg:
    yr, code, name, t, teu, units = r
    if yr not in seaports_web:
        seaports_web[yr] = {}
    
    clean_code = code if code in seaports_coords else ("DEHAM" if "Hamburg" in (name or "") else ("DEBRV" if "Bremerhaven" in (name or "") else ("DERSK" if "Rostock" in (name or "") else code)))
    coord = seaports_coords.get(clean_code, {"lat": 53.5, "lng": 9.9, "hub_type": "Seehafen"})
    
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

    if div_num in [1, 4]: g7 = "1"
    elif div_num in [2, 7, 8]: g7 = "2"
    elif div_num in [3, 10]: g7 = "3"
    elif div_num in [9]: g7 = "4"
    elif div_num in [5, 6, 11]: g7 = "5"
    elif div_num in [12, 13, 14]: g7 = "6"
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
print(">>> 5. Building Regional Fact Cubes...")
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
    "01": "1", "04": "1",
    "02": "2", "07": "2", "08": "2",
    "03": "3", "10": "3",
    "09": "4",
    "05": "5", "06": "5", "11": "5",
    "12": "6", "13": "6", "14": "6",
    "15": "7", "16": "7", "17": "7", "18": "7", "19": "7", "20": "7"
}
group7_to_div_shares = {
    "1": {"01": 0.58, "04": 0.42},
    "2": {"02": 0.08, "07": 0.64, "08": 0.28},
    "3": {"03": 0.22, "10": 0.78},
    "4": {"09": 1.0},
    "5": {"05": 0.12, "06": 0.48, "11": 0.40},
    "6": {"12": 0.35, "13": 0.38, "14": 0.27},
    "7": {"15": 0.18, "16": 0.22, "17": 0.14, "18": 0.16, "19": 0.20, "20": 0.10}
}

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
            "directions_tonnes": {"inbound": 0.0, "outbound": 0.0},
            "directions_tkm": {"inbound": 0.0, "outbound": 0.0},
            "groups_7_tonnes": {}, "groups_7_tkm": {},
            "divisions_20_tonnes": {}, "divisions_20_tkm": {},
            "by_mode_groups": {"road": {}, "rail": {}, "iww": {}},
            "by_mode_divisions": {"road": {}, "rail": {}, "iww": {}}
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
    p["directions_tonnes"][direct] = p["directions_tonnes"].get(direct, 0.0) + t_val
    p["directions_tkm"][direct] = p["directions_tkm"].get(direct, 0.0) + tkm_val

    clean_g7 = str(g7).strip()
    if clean_g7 in ["1", "2", "3", "4", "5", "6", "7"]:
        p["groups_7_tonnes"][clean_g7] = p["groups_7_tonnes"].get(clean_g7, 0.0) + t_val
        p["groups_7_tkm"][clean_g7] = p["groups_7_tkm"].get(clean_g7, 0.0) + tkm_val
        p["by_mode_groups"][mode][clean_g7] = p["by_mode_groups"][mode].get(clean_g7, 0.0) + t_val

        if mode == "road":
            shares = group7_to_div_shares.get(clean_g7, {})
            for div_k, share_v in shares.items():
                d_t = t_val * share_v
                d_tkm = tkm_val * share_v
                p["divisions_20_tonnes"][div_k] = p["divisions_20_tonnes"].get(div_k, 0.0) + d_t
                p["divisions_20_tkm"][div_k] = p["divisions_20_tkm"].get(div_k, 0.0) + d_tkm
                p["by_mode_divisions"][mode][div_k] = p["by_mode_divisions"][mode].get(div_k, 0.0) + d_t

    if mode in ["rail", "iww"]:
        clean_div = str(div20).strip().zfill(2)
        if clean_div in divisions_to_group7:
            p["divisions_20_tonnes"][clean_div] = p["divisions_20_tonnes"].get(clean_div, 0.0) + t_val
            p["divisions_20_tkm"][clean_div] = p["divisions_20_tkm"].get(clean_div, 0.0) + tkm_val
            p["by_mode_divisions"][mode][clean_div] = p["by_mode_divisions"][mode].get(clean_div, 0.0) + t_val

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
        p["directions_tonnes"] = {k: round(v, 1) for k, v in p["directions_tonnes"].items()}
        p["directions_tkm"] = {k: round(v, 1) for k, v in p["directions_tkm"].items()}
        p["groups_7_tonnes"] = {k: round(v, 1) for k, v in p["groups_7_tonnes"].items()}
        p["groups_7_tkm"] = {k: round(v, 1) for k, v in p["groups_7_tkm"].items()}
        p["divisions_20_tonnes"] = {k: round(v, 1) for k, v in p["divisions_20_tonnes"].items()}
        p["divisions_20_tkm"] = {k: round(v, 1) for k, v in p["divisions_20_tkm"].items()}
        for m in p["by_mode_groups"]:
            p["by_mode_groups"][m] = {k: round(v, 1) for k, v in p["by_mode_groups"][m].items()}
        for m in p["by_mode_divisions"]:
            p["by_mode_divisions"][m] = {k: round(v, 1) for k, v in p["by_mode_divisions"][m].items()}

with open(os.path.join(PROCESSED_DIR, "web_summary_by_region.json"), "w", encoding="utf-8") as f:
    json.dump(web_summaries, f, ensure_ascii=False)
print(f"    Saved web_summary_by_region.json ({len(web_summaries)} regions)")

# ----------------------------------------------------
# 7. Choropleth Map Lookup with Netto-Bilanz
# ----------------------------------------------------
print(">>> 6. Precomputing Choropleth Map Lookups...")
choro_web = {}
for n_id, yrs in web_summaries.items():
    for yr, p in yrs.items():
        if yr not in choro_web:
            choro_web[yr] = {}
        
        choro_web[yr][n_id] = {
            "total_tonnes": p["total_tonnes"],
            "total_tkm": p["total_tkm"],
            "road_tonnes": p["modes_tonnes"].get("road", 0),
            "rail_tonnes": p["modes_tonnes"].get("rail", 0),
            "iww_tonnes": p["modes_tonnes"].get("iww", 0),
            "road_tkm": p["modes_tkm"].get("road", 0),
            "rail_tkm": p["modes_tkm"].get("rail", 0),
            "iww_tkm": p["modes_tkm"].get("iww", 0),
            "inbound_tonnes": p["directions_tonnes"].get("inbound", 0),
            "outbound_tonnes": p["directions_tonnes"].get("outbound", 0),
            "balance_tonnes": p["balance_tonnes"],
            "inbound_tkm": p["directions_tkm"].get("inbound", 0),
            "outbound_tkm": p["directions_tkm"].get("outbound", 0),
            "balance_tkm": p["balance_tkm"]
        }

with open(os.path.join(PROCESSED_DIR, "web_choropleth.json"), "w", encoding="utf-8") as f:
    json.dump(choro_web, f, ensure_ascii=False)
print("    Saved web_choropleth.json")

print(">>> All data bundles built successfully!")
