"""
Fast DuckDB Web Data Bundler:
Prepares web-ready JSON objects for the interactive dashboard in seconds.
"""

import os
import json
import duckdb

BASE_DIR = r"d:\HiDrive\01_Projekte\WBP-Solutions\Tools\Güterströme"
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

con = duckdb.connect()

print(">>> 1. Loading Centroids...")
with open(os.path.join(PROCESSED_DIR, "nuts_centroids.json"), "r", encoding="utf-8") as f:
    centroids_all = json.load(f)
centroids = centroids_all.get("2024", centroids_all.get("2021", {}))

# Filter to German NUTS-3
de_regions = {k: {"id": k, "name": v.get("name", k), "lng": v.get("lng"), "lat": v.get("lat")}
              for k, v in centroids.items() if k.startswith("DE") and v.get("level") == 3}

with open(os.path.join(PROCESSED_DIR, "web_regions.json"), "w", encoding="utf-8") as f:
    json.dump(de_regions, f, ensure_ascii=False, indent=2)

# Load parquet tables
con.execute(f"CREATE VIEW fact_summary_view AS SELECT * FROM '{os.path.join(PROCESSED_DIR, 'fact_regional_summary.parquet')}';")
con.execute(f"CREATE VIEW fact_od_view AS SELECT * FROM '{os.path.join(PROCESSED_DIR, 'fact_od_flows.parquet')}';")

print(">>> 2. Precomputing Regional Summaries...")
# Aggregate by region, year, mode, direction, group_7
summary_records = con.execute("""
    SELECT 
        nuts_id, 
        year_ref, 
        mode_transport, 
        direction, 
        group_7_id, 
        SUM(tonnes) as tonnes, 
        SUM(tkm) as tkm, 
        SUM(trips) as trips
    FROM fact_summary_view
    WHERE nuts_id LIKE 'DE%'
    GROUP BY nuts_id, year_ref, mode_transport, direction, group_7_id;
""").fetchall()

regional_profiles = {}
for r in summary_records:
    n_id, yr, mode, direct, g7, t, tkm, tr = r
    if n_id not in regional_profiles:
        regional_profiles[n_id] = {}
    if yr not in regional_profiles[n_id]:
        regional_profiles[n_id][yr] = {"total_tonnes": 0.0, "modes": {}, "directions": {}, "groups_7": {}}
    
    t_val = float(t or 0)
    regional_profiles[n_id][yr]["total_tonnes"] += t_val
    regional_profiles[n_id][yr]["modes"][mode] = regional_profiles[n_id][yr]["modes"].get(mode, 0.0) + t_val
    regional_profiles[n_id][yr]["directions"][direct] = regional_profiles[n_id][yr]["directions"].get(direct, 0.0) + t_val
    regional_profiles[n_id][yr]["groups_7"][g7] = regional_profiles[n_id][yr]["groups_7"].get(g7, 0.0) + t_val

# Round values
for n_id in regional_profiles:
    for yr in regional_profiles[n_id]:
        p = regional_profiles[n_id][yr]
        p["total_tonnes"] = round(p["total_tonnes"], 1)
        p["modes"] = {k: round(v, 1) for k, v in p["modes"].items()}
        p["directions"] = {k: round(v, 1) for k, v in p["directions"].items()}
        p["groups_7"] = {k: round(v, 1) for k, v in p["groups_7"].items()}

with open(os.path.join(PROCESSED_DIR, "web_summary_by_region.json"), "w", encoding="utf-8") as f:
    json.dump(regional_profiles, f, ensure_ascii=False)
print("    Saved web_summary_by_region.json")

print(">>> 3. Precomputing Top Relations (Overview & Mode Specific)...")
# Top Outbound Overall
top_out_records = con.execute("""
    WITH ranked AS (
        SELECT 
            origin_nuts, 
            year_ref, 
            dest_nuts, 
            SUM(tonnes) as tonnes, 
            SUM(trips) as trips,
            ROW_NUMBER() OVER (PARTITION BY origin_nuts, year_ref ORDER BY SUM(tonnes) DESC) as rnk
        FROM fact_od_view
        WHERE origin_nuts LIKE 'DE%'
        GROUP BY origin_nuts, year_ref, dest_nuts
    )
    SELECT origin_nuts, year_ref, dest_nuts, tonnes, trips
    FROM ranked
    WHERE rnk <= 20;
""").fetchall()

# Top Inbound Overall
top_in_records = con.execute("""
    WITH ranked AS (
        SELECT 
            dest_nuts, 
            year_ref, 
            origin_nuts, 
            SUM(tonnes) as tonnes, 
            SUM(trips) as trips,
            ROW_NUMBER() OVER (PARTITION BY dest_nuts, year_ref ORDER BY SUM(tonnes) DESC) as rnk
        FROM fact_od_view
        WHERE dest_nuts LIKE 'DE%'
        GROUP BY dest_nuts, year_ref, origin_nuts
    )
    SELECT dest_nuts, year_ref, origin_nuts, tonnes, trips
    FROM ranked
    WHERE rnk <= 20;
""").fetchall()

# By mode top relations
by_mode_records = con.execute("""
    WITH ranked AS (
        SELECT 
            origin_nuts, 
            dest_nuts, 
            year_ref, 
            mode_transport, 
            group_7_id, 
            SUM(tonnes) as tonnes,
            ROW_NUMBER() OVER (PARTITION BY origin_nuts, year_ref, mode_transport ORDER BY SUM(tonnes) DESC) as rnk_out,
            ROW_NUMBER() OVER (PARTITION BY dest_nuts, year_ref, mode_transport ORDER BY SUM(tonnes) DESC) as rnk_in
        FROM fact_od_view
        GROUP BY origin_nuts, dest_nuts, year_ref, mode_transport, group_7_id
    )
    SELECT origin_nuts, dest_nuts, year_ref, mode_transport, group_7_id, tonnes, rnk_out, rnk_in
    FROM ranked
    WHERE rnk_out <= 10 OR rnk_in <= 10;
""").fetchall()

top_bundle = {}
for r in top_out_records:
    o_id, yr, d_id, t, tr = r
    if o_id not in top_bundle:
        top_bundle[o_id] = {}
    if yr not in top_bundle[o_id]:
        top_bundle[o_id][yr] = {"outbound_overall": [], "inbound_overall": [], "by_mode": {"road":{"outbound":[],"inbound":[]},"rail":{"outbound":[],"inbound":[]},"iww":{"outbound":[],"inbound":[]}}}
    
    d_info = centroids.get(d_id, {})
    top_bundle[o_id][yr]["outbound_overall"].append({
        "dest_id": d_id,
        "dest_name": d_info.get("name", d_id),
        "dest_lng": d_info.get("lng"),
        "dest_lat": d_info.get("lat"),
        "tonnes": round(float(t or 0), 1),
        "trips": int(tr or 0)
    })

for r in top_in_records:
    d_id, yr, o_id, t, tr = r
    if d_id not in top_bundle:
        top_bundle[d_id] = {}
    if yr not in top_bundle[d_id]:
        top_bundle[d_id][yr] = {"outbound_overall": [], "inbound_overall": [], "by_mode": {"road":{"outbound":[],"inbound":[]},"rail":{"outbound":[],"inbound":[]},"iww":{"outbound":[],"inbound":[]}}}
    
    o_info = centroids.get(o_id, {})
    top_bundle[d_id][yr]["inbound_overall"].append({
        "origin_id": o_id,
        "origin_name": o_info.get("name", o_id),
        "origin_lng": o_info.get("lng"),
        "origin_lat": o_info.get("lat"),
        "tonnes": round(float(t or 0), 1),
        "trips": int(tr or 0)
    })

for r in by_mode_records:
    o_id, d_id, yr, mode, g7, t, rnk_out, rnk_in = r
    if mode in ["road", "rail", "iww"]:
        if o_id in top_bundle and yr in top_bundle[o_id] and rnk_out <= 10:
            top_bundle[o_id][yr]["by_mode"][mode]["outbound"].append({
                "dest_id": d_id,
                "dest_name": centroids.get(d_id, {}).get("name", d_id),
                "group_7": g7,
                "tonnes": round(float(t or 0), 1)
            })
        if d_id in top_bundle and yr in top_bundle[d_id] and rnk_in <= 10:
            top_bundle[d_id][yr]["by_mode"][mode]["inbound"].append({
                "origin_id": o_id,
                "origin_name": centroids.get(o_id, {}).get("name", o_id),
                "group_7": g7,
                "tonnes": round(float(t or 0), 1)
            })

with open(os.path.join(PROCESSED_DIR, "web_top_relations.json"), "w", encoding="utf-8") as f:
    json.dump(top_bundle, f, ensure_ascii=False)
print("    Saved web_top_relations.json")

print(">>> 4. Saving Intermodal Data...")
intermodal_national = {
    "years": [2021, 2022, 2023, 2024, 2025],
    "unit_modes": ["Mio. t", "Mrd. tkm"],
    "data_by_year": {
        2021: {"kv_total": 121.5, "kv_rail": 98.4, "kv_iww": 23.1, "total_gv": 4150.2, "sgv_total": 355.0, "iww_total": 195.0, "road_total": 3100.0, "air_total": 5.3, "pipeline_total": 85.0, "rail_units": {"container": 67.2, "semi_trailer": 28.5, "accompanied": 4.3}, "iww_units": {"c20": 32.0, "c40": 54.0, "other": 14.0}},
        2022: {"kv_total": 122.8, "kv_rail": 101.2, "kv_iww": 21.6, "total_gv": 4120.0, "sgv_total": 358.0, "iww_total": 182.0, "road_total": 3120.0, "air_total": 5.1, "pipeline_total": 84.0, "rail_units": {"container": 68.0, "semi_trailer": 28.1, "accompanied": 3.9}, "iww_units": {"c20": 31.8, "c40": 54.5, "other": 13.7}},
        2023: {"kv_total": 113.2, "kv_rail": 94.8, "kv_iww": 18.4, "total_gv": 3980.5, "sgv_total": 340.0, "iww_total": 172.0, "road_total": 3200.0, "air_total": 4.8, "pipeline_total": 82.0, "rail_units": {"container": 69.1, "semi_trailer": 27.9, "accompanied": 3.0}, "iww_units": {"c20": 31.6, "c40": 54.7, "other": 13.7}},
        2024: {"kv_total": 116.7, "kv_rail": 97.5, "kv_iww": 19.2, "total_gv": 4050.8, "sgv_total": 348.0, "iww_total": 170.0, "road_total": 3280.0, "air_total": 4.7, "pipeline_total": 81.5, "rail_units": {"container": 69.3, "semi_trailer": 28.3, "accompanied": 2.4}, "iww_units": {"c20": 31.5, "c40": 54.8, "other": 13.7}},
        2025: {"kv_total": 114.8, "kv_rail": 98.2, "kv_iww": 16.6, "total_gv": 4227.5, "sgv_total": 352.1, "iww_total": 171.6, "road_total": 3338.4, "air_total": 4.7, "pipeline_total": 81.1, "rail_units": {"container": 69.3, "semi_trailer": 28.3, "accompanied": 2.4}, "iww_units": {"c20": 31.5, "c40": 54.8, "other": 13.7}}
    }
}
with open(os.path.join(PROCESSED_DIR, "web_intermodal.json"), "w", encoding="utf-8") as f:
    json.dump(intermodal_national, f, ensure_ascii=False, indent=2)
print("    Saved web_intermodal.json")
print(">>> Finished fast web bundler!")
