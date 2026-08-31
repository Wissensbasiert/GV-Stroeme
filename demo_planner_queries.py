"""
Test script to demonstrate Top-X relations & automated profile generator for planners.
"""

import duckdb
import json

con = duckdb.connect()

summary_parquet = "data/processed/fact_regional_summary.parquet"
od_parquet = "data/processed/fact_od_flows.parquet"
centroids_file = "data/processed/nuts_centroids.json"

with open(centroids_file, "r", encoding="utf-8") as f:
    centroids = json.load(f)["2024"]

def get_region_profile(nuts_id="DE300", year=2024, top_x=5):
    name = centroids.get(nuts_id, {}).get("name", nuts_id)
    
    # 1. Total Volume & Modal Split
    df_modal = con.execute(f"""
        SELECT mode_transport, direction, SUM(tonnes) as tonnes, SUM(tkm) as tkm
        FROM '{summary_parquet}'
        WHERE nuts_id = '{nuts_id}' AND year_ref = {year}
        GROUP BY mode_transport, direction;
    """).df()
    
    tot_tonnes = df_modal['tonnes'].sum()
    
    # 2. Top-X Relations Outbound
    df_top_out = con.execute(f"""
        SELECT dest_nuts, mode_transport, SUM(tonnes) as tonnes
        FROM '{od_parquet}'
        WHERE origin_nuts = '{nuts_id}' AND year_ref = {year}
        GROUP BY dest_nuts, mode_transport
        ORDER BY tonnes DESC
        LIMIT {top_x};
    """).df()
    
    # 3. Top-X Relations Inbound
    df_top_in = con.execute(f"""
        SELECT origin_nuts, mode_transport, SUM(tonnes) as tonnes
        FROM '{od_parquet}'
        WHERE dest_nuts = '{nuts_id}' AND year_ref = {year}
        GROUP BY origin_nuts, mode_transport
        ORDER BY tonnes DESC
        LIMIT {top_x};
    """).df()

    print(f"==================================================")
    print(f"STECKBRIEF: {name} ({nuts_id}) - Bezugsjahr {year}")
    print(f"==================================================")
    print(f"Gesamtaufkommen (Empfang & Versand): {tot_tonnes/1e6:.2f} Mio. Tonnen")
    print("\nModal Split:")
    by_mode = df_modal.groupby('mode_transport')['tonnes'].sum()
    for m, t in by_mode.items():
        print(f"  - {m.upper()}: {t/1e6:.2f} Mio. t ({t/tot_tonnes*100:.1f}%)")
        
    print(f"\nTop {top_x} Versand-Relationen (Wohin gehen die Güter?):")
    for _, r in df_top_out.iterrows():
        dest_name = centroids.get(r['dest_nuts'], {}).get('name', r['dest_nuts'])
        print(f"  -> {dest_name} ({r['dest_nuts']}) [{r['mode_transport']}]: {r['tonnes']/1e3:,.1f} tsd. t")

    print(f"\nTop {top_x} Empfangs-Relationen (Woher kommen die Güter?):")
    for _, r in df_top_in.iterrows():
        orig_name = centroids.get(r['origin_nuts'], {}).get('name', r['origin_nuts'])
        print(f"  <- {orig_name} ({r['origin_nuts']}) [{r['mode_transport']}]: {r['tonnes']/1e3:,.1f} tsd. t")

if __name__ == "__main__":
    get_region_profile("DE300", 2024, top_x=5) # Berlin
    print("\n")
    get_region_profile("DE111", 2024, top_x=5) # Stuttgart
