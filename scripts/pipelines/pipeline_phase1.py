"""
ETL & Aggregation Pipeline for German Freight Flows
Processes Destatis, KBA, NUTS Geodata and prepares optimized relational tables & web JSONs.
"""

import os
import glob
import json
import sqlite3
import pandas as pd
import duckdb
import geopandas as gpd
from shapely.geometry import mapping

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
OUT_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(OUT_DIR, exist_ok=True)

# ----------------------------------------------------
# 1. Geometries & Centroids from NUTS GeoPackages
# ----------------------------------------------------
def process_nuts_geometries():
    print(">>> 1. Processing NUTS Geometries & Centroids...")
    nuts_files = {
        "2024": os.path.join(RAW_DIR, "NUTS", "NUTS_RG_01M_2024_3035.gpkg"),
        "2021": os.path.join(RAW_DIR, "NUTS", "NUTS_RG_01M_2021_3035.gpkg"),
        "2016": os.path.join(RAW_DIR, "NUTS", "NUTS_RG_01M_2016_3035.gpkg"),
    }
    
    centroids = {}
    regions_meta = {}

    for year_tag, gpkg_file in nuts_files.items():
        if not os.path.exists(gpkg_file):
            continue
        gdf = gpd.read_file(gpkg_file)
        # Convert to WGS84 for web mapping
        gdf_wgs84 = gdf.to_crs(epsg=4326)
        
        # Calculate centroids in EPSG:3035 then convert to 4326 for accurate center
        centroids_3035 = gdf.geometry.centroid
        centroids_wgs84 = gpd.GeoSeries(centroids_3035, crs=3035).to_crs(epsg=4326)

        centroids[year_tag] = {}
        for idx, row in gdf.iterrows():
            nuts_id = row['NUTS_ID']
            c_pt = centroids_wgs84.iloc[idx]
            centroids[year_tag][nuts_id] = {
                "id": nuts_id,
                "name": row.get('NUTS_NAME', row.get('NAME_LATN', '')),
                "level": int(row.get('LEVL_CODE', 3)),
                "country": row.get('CNTR_CODE', ''),
                "lng": round(c_pt.x, 5),
                "lat": round(c_pt.y, 5)
            }
            if nuts_id not in regions_meta:
                regions_meta[nuts_id] = centroids[year_tag][nuts_id]
        
        # Save simplified GeoJSON for DE NUTS-3 (for fast web loading)
        gdf_de = gdf_wgs84[(gdf_wgs84['CNTR_CODE'] == 'DE') & (gdf_wgs84['LEVL_CODE'] == 3)]
        # Simplify geometry slightly to keep payload minimal (<1.5MB)
        gdf_de_simple = gdf_de.copy()
        gdf_de_simple['geometry'] = gdf_de.geometry.simplify(0.005, preserve_topology=True)
        geojson_path = os.path.join(OUT_DIR, f"nuts3_de_{year_tag}.geojson")
        gdf_de_simple[['NUTS_ID', 'NUTS_NAME', 'geometry']].to_file(geojson_path, driver="GeoJSON")
        print(f"    Saved {geojson_path} ({os.path.getsize(geojson_path)//1024} KB)")

    with open(os.path.join(OUT_DIR, "nuts_centroids.json"), "w", encoding="utf-8") as f:
        json.dump(centroids, f, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, "regions_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(regions_meta, f, ensure_ascii=False, indent=2)
    print(f"    Metadata saved: {len(regions_meta)} regions indexed.")

# ----------------------------------------------------
# 2. NST-2007 Taxonomy Master Table
# ----------------------------------------------------
def build_nst_taxonomy():
    print(">>> 2. Building NST-2007 Taxonomy Tables...")
    NST2007_HIERARCHY = {
        "groups_7": {
            "1": {"name": "Erzeugnisse der Land- und Forstwirtschaft, Rohstoffe", "divisions": ["01", "02", "03"]},
            "2": {"name": "Konsumgüter zum kurzfristigen Verbrauch, Holzwaren", "divisions": ["04", "05", "06"]},
            "3": {"name": "Mineralische, chemische und Mineralölerzeugnisse", "divisions": ["07", "08", "09"]},
            "4": {"name": "Metalle und Metallerzeugnisse", "divisions": ["10"]},
            "5": {"name": "Maschinen und Ausrüstungen, langlebige Konsumgüter", "divisions": ["11", "12", "13"]},
            "6": {"name": "Sekundärrohstoffe, Abfälle", "divisions": ["14"]},
            "7": {"name": "Sonstige Produkte", "divisions": ["15", "16", "17", "18", "19", "20"]}
        },
        "divisions_20": {
            "01": {"name": "Erzeugnisse der Landwirtschaft, Jagd und Forstwirtschaft; Fische", "group_7": "1"},
            "02": {"name": "Kohle, rohes Erdöl und Erdgas", "group_7": "1"},
            "03": {"name": "Erze, Steine und Erden; sonstige Bergbauerzeugnisse", "group_7": "1"},
            "04": {"name": "Nahrungs- und Genussmittel, Tabakerzeugnisse", "group_7": "2"},
            "05": {"name": "Textilien, Bekleidung, Lederwaren", "group_7": "2"},
            "06": {"name": "Holz, Holzwaren, Papier, Pappe, Druckerzeugnisse", "group_7": "2"},
            "07": {"name": "Kokerei- und Mineralölerzeugnisse", "group_7": "3"},
            "08": {"name": "Chemische Erzeugnisse, synthetische Fasern, Gummi- und Kunststoffwaren", "group_7": "3"},
            "09": {"name": "Glas, Keramik, bearbeitete Steine und Erden", "group_7": "3"},
            "10": {"name": "Metalle und Metallerzeugnisse", "group_7": "4"},
            "11": {"name": "Maschinen, Ausrüstungen, Haushaltsgeräte", "group_7": "5"},
            "12": {"name": "Fahrzeuge", "group_7": "5"},
            "13": {"name": "Möbel, sonstige Industriewaren", "group_7": "5"},
            "14": {"name": "Sekundärrohstoffe, Abfälle", "group_7": "6"},
            "15": {"name": "Post, Pakete", "group_7": "7"},
            "16": {"name": "Geräte und Material für die Güterbeförderung", "group_7": "7"},
            "17": {"name": "Im Rahmen von Umzügen beförderte Güter", "group_7": "7"},
            "18": {"name": "Zusammengesetzte Güter (Containerladung)", "group_7": "7"},
            "19": {"name": "Nicht identifizierbare Güter", "group_7": "7"},
            "20": {"name": "Sonstige Güter a.n.g.", "group_7": "7"}
        }
    }
    with open(os.path.join(OUT_DIR, "dim_nst2007.json"), "w", encoding="utf-8") as f:
        json.dump(NST2007_HIERARCHY, f, ensure_ascii=False, indent=2)
    print("    dim_nst2007.json created.")

if __name__ == "__main__":
    process_nuts_geometries()
    build_nst_taxonomy()
    print("Phase 1 complete.")
