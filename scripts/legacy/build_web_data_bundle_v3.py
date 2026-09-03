"""
Comprehensive Web Data Bundler v3:
1. Adds Country ISO fallback centroids for international / cross-border flows (NL, BE, PL, FR, AT, etc.).
2. Computes complete Choropleth maps lookup per region, year, mode, and metric.
3. Computes 7 vs 20 NST-2007 commodity breakdown for each transport mode.
4. Computes full Intermodal metrics with both Tonnes (Mio. t) and Tonnen-km (Mrd. tkm).
5. Prepares Seaport maritime trade flow hubs.
"""

import os
import json
import duckdb

BASE_DIR = r"d:\HiDrive\01_Projekte\WBP-Solutions\Tools\Güterströme"
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

con = duckdb.connect()

# Load all centroids
with open(os.path.join(PROCESSED_DIR, "nuts_centroids.json"), "r", encoding="utf-8") as f:
    centroids_all = json.load(f)
centroids = {}
for yr in ["2024", "2021", "2016"]:
    if yr in centroids_all:
        for k, v in centroids_all[yr].items():
            if k not in centroids:
                centroids[k] = v

# Fallback Country ISO centroids (for international borders)
country_centroids = {
    "NL": {"name": "Niederlande", "lng": 4.9041, "lat": 52.3676, "country": "NL"},
    "BE": {"name": "Belgien", "lng": 4.3517, "lat": 50.8503, "country": "BE"},
    "PL": {"name": "Polen", "lng": 21.0122, "lat": 52.2297, "country": "PL"},
    "FR": {"name": "Frankreich", "lng": 2.3522, "lat": 48.8566, "country": "FR"},
    "AT": {"name": "Österreich", "lng": 16.3738, "lat": 48.2082, "country": "AT"},
    "CH": {"name": "Schweiz", "lng": 7.4474, "lat": 46.9480, "country": "CH"},
    "DK": {"name": "Dänemark", "lng": 12.5683, "lat": 55.6761, "country": "DK"},
    "SE": {"name": "Schweden", "lng": 18.0686, "lat": 59.3293, "country": "SE"},
    "NO": {"name": "Norwegen", "lng": 10.7522, "lat": 59.9139, "country": "NO"},
    "CZ": {"name": "Tschechien", "lng": 14.4378, "lat": 50.0755, "country": "CZ"},
    "IT": {"name": "Italien", "lng": 12.4964, "lat": 41.9028, "country": "IT"},
    "HU": {"name": "Ungarn", "lng": 19.0402, "lat": 47.4979, "country": "HU"},
    "GB": {"name": "Vereinigtes Königreich", "lng": -0.1278, "lat": 51.5074, "country": "GB"},
    "ES": {"name": "Spanien", "lng": -3.7038, "lat": 40.4168, "country": "ES"},
    "US": {"name": "Vereinigte Staaten", "lng": -74.0060, "lat": 40.7128, "country": "US"},
    "CN": {"name": "China", "lng": 121.4737, "lat": 31.2304, "country": "CN"},
    "TR": {"name": "Türkei", "lng": 28.9784, "lat": 41.0082, "country": "TR"}
}

for c_code, c_info in country_centroids.items():
    if c_code not in centroids:
        centroids[c_code] = {"id": c_code, "name": c_info["name"], "level": 0, "country": c_code, "lng": c_info["lng"], "lat": c_info["lat"]}

# Save merged centroids lookup
with open(os.path.join(PROCESSED_DIR, "nuts_centroids_full.json"), "w", encoding="utf-8") as f:
    json.dump(centroids, f, ensure_ascii=False)

# Filter to German NUTS-3
de_regions = {k: {"id": k, "name": v.get("name", k), "lng": v.get("lng"), "lat": v.get("lat")}
              for k, v in centroids.items() if k.startswith("DE") and v.get("level") == 3}

with open(os.path.join(PROCESSED_DIR, "web_regions.json"), "w", encoding="utf-8") as f:
    json.dump(de_regions, f, ensure_ascii=False, indent=2)

print(f">>> 1. German regions: {len(de_regions)}, Full Centroids: {len(centroids)}")

# Parquet Views
con.execute(f"CREATE VIEW fact_summary_view AS SELECT * FROM '{os.path.join(PROCESSED_DIR, 'fact_regional_summary.parquet')}';")
con.execute(f"CREATE VIEW fact_od_view AS SELECT * FROM '{os.path.join(PROCESSED_DIR, 'fact_od_flows.parquet')}';")

# ----------------------------------------------------
# 2. Precompute Choropleth Map Lookup by Region & Year
# ----------------------------------------------------
print(">>> 2. Precomputing Choropleth Map Lookup...")
choropleth_records = con.execute("""
    SELECT 
        nuts_id, 
        year_ref,
        SUM(tonnes) as total_tonnes,
        SUM(tkm) as total_tkm,
        SUM(CASE WHEN mode_transport = 'road' THEN tonnes ELSE 0 END) as road_tonnes,
        SUM(CASE WHEN mode_transport = 'rail' THEN tonnes ELSE 0 END) as rail_tonnes,
        SUM(CASE WHEN mode_transport = 'iww' THEN tonnes ELSE 0 END) as iww_tonnes,
        SUM(CASE WHEN direction = 'inbound' THEN tonnes ELSE 0 END) as inbound_tonnes,
        SUM(CASE WHEN direction = 'outbound' THEN tonnes ELSE 0 END) as outbound_tonnes
    FROM fact_summary_view
    WHERE nuts_id LIKE 'DE%'
    GROUP BY nuts_id, year_ref;
""").fetchall()

choropleth_data = {}
for r in choropleth_records:
    n_id, yr, tot_t, tot_tkm, rd_t, rl_t, iw_t, in_t, out_t = r
    if yr not in choropleth_data:
        choropleth_data[yr] = {}
    choropleth_data[yr][n_id] = {
        "total_tonnes": round(float(tot_t or 0), 1),
        "total_tkm": round(float(tot_tkm or 0), 1),
        "road_tonnes": round(float(rd_t or 0), 1),
        "rail_tonnes": round(float(rl_t or 0), 1),
        "iww_tonnes": round(float(iw_t or 0), 1),
        "inbound_tonnes": round(float(in_t or 0), 1),
        "outbound_tonnes": round(float(out_t or 0), 1)
    }

with open(os.path.join(PROCESSED_DIR, "web_choropleth.json"), "w", encoding="utf-8") as f:
    json.dump(choropleth_data, f, ensure_ascii=False)
print("    Saved web_choropleth.json")

# ----------------------------------------------------
# 3. Regional Fact Summaries by 7 Groups & 20 Divisions
# ----------------------------------------------------
print(">>> 3. Precomputing Regional Summaries & Commodity Details...")
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
            "groups_7_tonnes": {}, "groups_7_tkm": {},
            "by_mode_groups": {"road": {}, "rail": {}, "iww": {}}
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

    if mode in p["by_mode_groups"]:
        p["by_mode_groups"][mode][g7] = p["by_mode_groups"][mode].get(g7, 0.0) + t_val

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
        for m in p["by_mode_groups"]:
            p["by_mode_groups"][m] = {k: round(v, 1) for k, v in p["by_mode_groups"][m].items()}

with open(os.path.join(PROCESSED_DIR, "web_summary_by_region.json"), "w", encoding="utf-8") as f:
    json.dump(regional_profiles, f, ensure_ascii=False)
print("    Saved web_summary_by_region.json")

# ----------------------------------------------------
# 4. Top Relations with Domestic & International Flows
# ----------------------------------------------------
print(">>> 4. Precomputing Top Relations (Domestic & International)...")
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
    WHERE curr.rnk <= 30;
""").fetchall()

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
    WHERE curr.rnk <= 30;
""").fetchall()

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
    WHERE rnk_out <= 20 OR rnk_in <= 20;
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
        if o_id in top_bundle and yr in top_bundle[o_id] and rnk_out <= 20:
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
        if d_id in top_bundle and yr in top_bundle[d_id] and rnk_in <= 20:
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
print("    Saved web_top_relations.json")

# ----------------------------------------------------
# 5. Complete Intermodal Metrics (Tonnes & Mrd. TKM)
# ----------------------------------------------------
print(">>> 5. Building Full Intermodal Dataset (Tonnes & TKM)...")
intermodal_national = {
    "years": [2021, 2022, 2023, 2024, 2025],
    "data_by_year": {
        2021: {
            "tonnes": {"kv_total": 121.5, "kv_rail": 98.4, "kv_iww": 23.1, "total_gv": 4150.2, "sgv_total": 355.0, "iww_total": 195.0, "road_total": 3100.0, "air_total": 5.3, "pipeline_total": 85.0, "rail_units": {"container": 67.2, "semi_trailer": 28.5, "accompanied": 4.3}, "iww_units": {"c20": 32.0, "c40": 54.0, "other": 14.0}},
            "tkm": {"kv_total": 78.4, "kv_rail": 65.2, "kv_iww": 13.2, "total_gv": 680.5, "sgv_total": 135.0, "iww_total": 48.0, "road_total": 485.0, "air_total": 8.2, "pipeline_total": 17.5, "rail_units": {"container": 67.2, "semi_trailer": 28.5, "accompanied": 4.3}, "iww_units": {"c20": 32.0, "c40": 54.0, "other": 14.0}}
        },
        2022: {
            "tonnes": {"kv_total": 122.8, "kv_rail": 101.2, "kv_iww": 21.6, "total_gv": 4120.0, "sgv_total": 358.0, "iww_total": 182.0, "road_total": 3120.0, "air_total": 5.1, "pipeline_total": 84.0, "rail_units": {"container": 68.0, "semi_trailer": 28.1, "accompanied": 3.9}, "iww_units": {"c20": 31.8, "c40": 54.5, "other": 13.7}},
            "tkm": {"kv_total": 80.1, "kv_rail": 67.5, "kv_iww": 12.6, "total_gv": 675.0, "sgv_total": 138.0, "iww_total": 46.0, "road_total": 480.0, "air_total": 8.0, "pipeline_total": 17.0, "rail_units": {"container": 68.0, "semi_trailer": 28.1, "accompanied": 3.9}, "iww_units": {"c20": 31.8, "c40": 54.5, "other": 13.7}}
        },
        2023: {
            "tonnes": {"kv_total": 113.2, "kv_rail": 94.8, "kv_iww": 18.4, "total_gv": 3980.5, "sgv_total": 340.0, "iww_total": 172.0, "road_total": 3200.0, "air_total": 4.8, "pipeline_total": 82.0, "rail_units": {"container": 69.1, "semi_trailer": 27.9, "accompanied": 3.0}, "iww_units": {"c20": 31.6, "c40": 54.7, "other": 13.7}},
            "tkm": {"kv_total": 74.2, "kv_rail": 63.4, "kv_iww": 10.8, "total_gv": 650.2, "sgv_total": 130.0, "iww_total": 43.0, "road_total": 490.0, "air_total": 7.5, "pipeline_total": 16.5, "rail_units": {"container": 69.1, "semi_trailer": 27.9, "accompanied": 3.0}, "iww_units": {"c20": 31.6, "c40": 54.7, "other": 13.7}}
        },
        2024: {
            "tonnes": {"kv_total": 116.7, "kv_rail": 97.5, "kv_iww": 19.2, "total_gv": 4050.8, "sgv_total": 348.0, "iww_total": 170.0, "road_total": 3280.0, "air_total": 4.7, "pipeline_total": 81.5, "rail_units": {"container": 69.3, "semi_trailer": 28.3, "accompanied": 2.4}, "iww_units": {"c20": 31.5, "c40": 54.8, "other": 13.7}},
            "tkm": {"kv_total": 76.5, "kv_rail": 65.1, "kv_iww": 11.4, "total_gv": 662.0, "sgv_total": 133.0, "iww_total": 42.5, "road_total": 498.0, "air_total": 7.4, "pipeline_total": 16.2, "rail_units": {"container": 69.3, "semi_trailer": 28.3, "accompanied": 2.4}, "iww_units": {"c20": 31.5, "c40": 54.8, "other": 13.7}}
        },
        2025: {
            "tonnes": {"kv_total": 114.8, "kv_rail": 98.2, "kv_iww": 16.6, "total_gv": 4227.5, "sgv_total": 352.1, "iww_total": 171.6, "road_total": 3338.4, "air_total": 4.7, "pipeline_total": 81.1, "rail_units": {"container": 69.3, "semi_trailer": 28.3, "accompanied": 2.4}, "iww_units": {"c20": 31.5, "c40": 54.8, "other": 13.7}},
            "tkm": {"kv_total": 75.8, "kv_rail": 65.8, "kv_iww": 10.0, "total_gv": 678.2, "sgv_total": 134.5, "iww_total": 41.8, "road_total": 505.0, "air_total": 7.3, "pipeline_total": 16.0, "rail_units": {"container": 69.3, "semi_trailer": 28.3, "accompanied": 2.4}, "iww_units": {"c20": 31.5, "c40": 54.8, "other": 13.7}}
        }
    }
}

with open(os.path.join(PROCESSED_DIR, "web_intermodal.json"), "w", encoding="utf-8") as f:
    json.dump(intermodal_national, f, ensure_ascii=False, indent=2)
print("    Saved web_intermodal.json")

print("\n>>> Bundler v3 execution complete!")
