"""
High Precision Web Data Bundler v2:
- Computes complete YoY and 10-Year trends for all relations.
- Includes tonnes, tkm (Verkehrsleistung), and trips.
- Prepares mode-specific flow geometries and clean null handling for 2025.
"""

import os
import json
import duckdb

BASE_DIR = r"d:\HiDrive\01_Projekte\WBP-Solutions\Tools\Güterströme"
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

con = duckdb.connect()

print(">>> 1. Loading NUTS Centroids & Regions...")
with open(os.path.join(PROCESSED_DIR, "nuts_centroids.json"), "r", encoding="utf-8") as f:
    centroids_all = json.load(f)
centroids = centroids_all.get("2024", centroids_all.get("2021", {}))

# German NUTS-3
de_regions = {}
for k, v in centroids.items():
    if k.startswith("DE") and v.get("level") == 3:
        de_regions[k] = {
            "id": k,
            "name": v.get("name", k),
            "lng": v.get("lng"),
            "lat": v.get("lat")
        }

with open(os.path.join(PROCESSED_DIR, "web_regions.json"), "w", encoding="utf-8") as f:
    json.dump(de_regions, f, ensure_ascii=False, indent=2)

# Load parquet views
con.execute(f"CREATE VIEW fact_summary_view AS SELECT * FROM '{os.path.join(PROCESSED_DIR, 'fact_regional_summary.parquet')}';")
con.execute(f"CREATE VIEW fact_od_view AS SELECT * FROM '{os.path.join(PROCESSED_DIR, 'fact_od_flows.parquet')}';")

print(">>> 2. Precomputing Regional Summaries (Tonnes & Tkm)...")
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
        regional_profiles[n_id][yr] = {
            "total_tonnes": 0.0, "total_tkm": 0.0, "total_trips": 0,
            "modes_tonnes": {}, "modes_tkm": {},
            "directions_tonnes": {}, "directions_tkm": {},
            "groups_7_tonnes": {}, "groups_7_tkm": {}
        }
    
    t_val = float(t or 0)
    tkm_val = float(tkm or 0)
    tr_val = int(tr or 0)
    
    p = regional_profiles[n_id][yr]
    p["total_tonnes"] += t_val
    p["total_tkm"] += tkm_val
    p["total_trips"] += tr_val
    p["modes_tonnes"][mode] = p["modes_tonnes"].get(mode, 0.0) + t_val
    p["modes_tkm"][mode] = p["modes_tkm"].get(mode, 0.0) + tkm_val
    p["directions_tonnes"][direct] = p["directions_tonnes"].get(direct, 0.0) + t_val
    p["directions_tkm"][direct] = p["directions_tkm"].get(direct, 0.0) + tkm_val
    p["groups_7_tonnes"][g7] = p["groups_7_tonnes"].get(g7, 0.0) + t_val
    p["groups_7_tkm"][g7] = p["groups_7_tkm"].get(g7, 0.0) + tkm_val

# Clean & Round
for n_id in regional_profiles:
    for yr in regional_profiles[n_id]:
        p = regional_profiles[n_id][yr]
        p["total_tonnes"] = round(p["total_tonnes"], 1)
        p["total_tkm"] = round(p["total_tkm"], 1)
        p["modes_tonnes"] = {k: round(v, 1) for k, v in p["modes_tonnes"].items()}
        p["modes_tkm"] = {k: round(v, 1) for k, v in p["modes_tkm"].items()}
        p["directions_tonnes"] = {k: round(v, 1) for k, v in p["directions_tonnes"].items()}
        p["directions_tkm"] = {k: round(v, 1) for k, v in p["directions_tkm"].items()}
        p["groups_7_tonnes"] = {k: round(v, 1) for k, v in p["groups_7_tonnes"].items()}
        p["groups_7_tkm"] = {k: round(v, 1) for k, v in p["groups_7_tkm"].items()}

with open(os.path.join(PROCESSED_DIR, "web_summary_by_region.json"), "w", encoding="utf-8") as f:
    json.dump(regional_profiles, f, ensure_ascii=False)
print("    Saved web_summary_by_region.json")

print(">>> 3. Computing Precise Top Relations with Multi-Period YoY and 10-Yr Trends...")
# Create index table for fast historical lookups
con.execute("""
    CREATE TABLE od_history AS
    SELECT 
        origin_nuts, 
        dest_nuts, 
        year_ref, 
        mode_transport,
        group_7_id,
        SUM(tonnes) as tonnes, 
        SUM(tkm) as tkm, 
        SUM(trips) as trips
    FROM fact_od_view
    GROUP BY origin_nuts, dest_nuts, year_ref, mode_transport, group_7_id;
""")

# Top Outbound Overall with YoY and 10-Yr
top_out_query = con.execute("""
    WITH yearly_agg AS (
        SELECT origin_nuts, dest_nuts, year_ref, 
               SUM(tonnes) as tonnes, SUM(tkm) as tkm, SUM(trips) as trips
        FROM od_history
        WHERE origin_nuts LIKE 'DE%'
        GROUP BY origin_nuts, dest_nuts, year_ref
    ),
    ranked AS (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY origin_nuts, year_ref ORDER BY tonnes DESC) as rnk
        FROM yearly_agg
    )
    SELECT 
        curr.origin_nuts,
        curr.year_ref,
        curr.dest_nuts,
        curr.tonnes,
        curr.tkm,
        curr.trips,
        prev.tonnes as tonnes_prev,
        past10.tonnes as tonnes_10yr
    FROM ranked curr
    LEFT JOIN yearly_agg prev ON curr.origin_nuts = prev.origin_nuts AND curr.dest_nuts = prev.dest_nuts AND prev.year_ref = curr.year_ref - 1
    LEFT JOIN yearly_agg past10 ON curr.origin_nuts = past10.origin_nuts AND curr.dest_nuts = past10.dest_nuts AND past10.year_ref = curr.year_ref - 10
    WHERE curr.rnk <= 25;
""").fetchall()

# Top Inbound Overall with YoY and 10-Yr
top_in_query = con.execute("""
    WITH yearly_agg AS (
        SELECT dest_nuts, origin_nuts, year_ref, 
               SUM(tonnes) as tonnes, SUM(tkm) as tkm, SUM(trips) as trips
        FROM od_history
        WHERE dest_nuts LIKE 'DE%'
        GROUP BY dest_nuts, origin_nuts, year_ref
    ),
    ranked AS (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY dest_nuts, year_ref ORDER BY tonnes DESC) as rnk
        FROM yearly_agg
    )
    SELECT 
        curr.dest_nuts,
        curr.year_ref,
        curr.origin_nuts,
        curr.tonnes,
        curr.tkm,
        curr.trips,
        prev.tonnes as tonnes_prev,
        past10.tonnes as tonnes_10yr
    FROM ranked curr
    LEFT JOIN yearly_agg prev ON curr.dest_nuts = prev.dest_nuts AND curr.origin_nuts = prev.origin_nuts AND prev.year_ref = curr.year_ref - 1
    LEFT JOIN yearly_agg past10 ON curr.dest_nuts = past10.dest_nuts AND curr.origin_nuts = past10.origin_nuts AND past10.year_ref = curr.year_ref - 10
    WHERE curr.rnk <= 25;
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
            SUM(tkm) as tkm,
            ROW_NUMBER() OVER (PARTITION BY origin_nuts, year_ref, mode_transport ORDER BY SUM(tonnes) DESC) as rnk_out,
            ROW_NUMBER() OVER (PARTITION BY dest_nuts, year_ref, mode_transport ORDER BY SUM(tonnes) DESC) as rnk_in
        FROM od_history
        GROUP BY origin_nuts, dest_nuts, year_ref, mode_transport, group_7_id
    )
    SELECT origin_nuts, dest_nuts, year_ref, mode_transport, group_7_id, tonnes, tkm, rnk_out, rnk_in
    FROM ranked
    WHERE rnk_out <= 15 OR rnk_in <= 15;
""").fetchall()

top_bundle = {}

for r in top_out_query:
    o_id, yr, d_id, t, tkm, tr, t_prev, t_10 = r
    if o_id not in top_bundle:
        top_bundle[o_id] = {}
    if yr not in top_bundle[o_id]:
        top_bundle[o_id][yr] = {"outbound_overall": [], "inbound_overall": [], "by_mode": {"road":{"outbound":[],"inbound":[]},"rail":{"outbound":[],"inbound":[]},"iww":{"outbound":[],"inbound":[]}}}
    
    d_info = centroids.get(d_id, {})
    yoy_pct = round(((float(t) - float(t_prev)) / float(t_prev)) * 100, 1) if t_prev and float(t_prev) > 0 else None
    trend_10yr_pct = round(((float(t) - float(t_10)) / float(t_10)) * 100, 1) if t_10 and float(t_10) > 0 else None

    top_bundle[o_id][yr]["outbound_overall"].append({
        "dest_id": d_id,
        "dest_name": d_info.get("name", d_id),
        "dest_lng": d_info.get("lng"),
        "dest_lat": d_info.get("lat"),
        "tonnes": round(float(t or 0), 1),
        "tkm": round(float(tkm or 0), 1),
        "trips": int(tr or 0),
        "yoy_pct": yoy_pct,
        "trend_10yr_pct": trend_10yr_pct
    })

for r in top_in_query:
    d_id, yr, o_id, t, tkm, tr, t_prev, t_10 = r
    if d_id not in top_bundle:
        top_bundle[d_id] = {}
    if yr not in top_bundle[d_id]:
        top_bundle[d_id][yr] = {"outbound_overall": [], "inbound_overall": [], "by_mode": {"road":{"outbound":[],"inbound":[]},"rail":{"outbound":[],"inbound":[]},"iww":{"outbound":[],"inbound":[]}}}
    
    o_info = centroids.get(o_id, {})
    yoy_pct = round(((float(t) - float(t_prev)) / float(t_prev)) * 100, 1) if t_prev and float(t_prev) > 0 else None
    trend_10yr_pct = round(((float(t) - float(t_10)) / float(t_10)) * 100, 1) if t_10 and float(t_10) > 0 else None

    top_bundle[d_id][yr]["inbound_overall"].append({
        "origin_id": o_id,
        "origin_name": o_info.get("name", o_id),
        "origin_lng": o_info.get("lng"),
        "origin_lat": o_info.get("lat"),
        "tonnes": round(float(t or 0), 1),
        "tkm": round(float(tkm or 0), 1),
        "trips": int(tr or 0),
        "yoy_pct": yoy_pct,
        "trend_10yr_pct": trend_10yr_pct
    })

for r in by_mode_records:
    o_id, d_id, yr, mode, g7, t, tkm, rnk_out, rnk_in = r
    if mode in ["road", "rail", "iww"]:
        if o_id in top_bundle and yr in top_bundle[o_id] and rnk_out <= 15:
            d_info = centroids.get(d_id, {})
            top_bundle[o_id][yr]["by_mode"][mode]["outbound"].append({
                "dest_id": d_id,
                "dest_name": d_info.get("name", d_id),
                "dest_lng": d_info.get("lng"),
                "dest_lat": d_info.get("lat"),
                "group_7": g7,
                "tonnes": round(float(t or 0), 1),
                "tkm": round(float(tkm or 0), 1)
            })
        if d_id in top_bundle and yr in top_bundle[d_id] and rnk_in <= 15:
            o_info = centroids.get(o_id, {})
            top_bundle[d_id][yr]["by_mode"][mode]["inbound"].append({
                "origin_id": o_id,
                "origin_name": o_info.get("name", o_id),
                "origin_lng": o_info.get("lng"),
                "origin_lat": o_info.get("lat"),
                "group_7": g7,
                "tonnes": round(float(t or 0), 1),
                "tkm": round(float(tkm or 0), 1)
            })

with open(os.path.join(PROCESSED_DIR, "web_top_relations.json"), "w", encoding="utf-8") as f:
    json.dump(top_bundle, f, ensure_ascii=False)
print("    Saved web_top_relations.json with complete YoY & 10-Yr trends.")

print(">>> Finished Data Bundler v2!")
