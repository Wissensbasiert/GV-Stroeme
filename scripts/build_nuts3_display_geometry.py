#!/usr/bin/env python3
"""Build topology-preserving NUTS-3 GeoJSON layers used only for map display."""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
from shapely import make_valid
from shapely.geometry import mapping
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "raw" / "NUTS"
TARGET_DIR = ROOT / "data" / "processed"
VERSIONS = ("2016", "2021", "2024")


def build(version: str) -> None:
    source = SOURCE_DIR / f"NUTS_RG_01M_{version}_3035.gpkg"
    target = TARGET_DIR / f"nuts3_de_{version}_display.geojson"
    regions = gpd.read_file(source)
    regions = regions[(regions["CNTR_CODE"] == "DE") & (regions["LEVL_CODE"] == 3)].copy()
    if regions.empty or not regions["NUTS_ID"].is_unique:
        raise ValueError(f"{version}: keine eindeutigen deutschen NUTS-3-Regionen.")

    # Repair only the few formal ring errors in the copied map geometry. The
    # original GPKG, regional IDs and all traffic calculations remain untouched.
    regions.geometry = regions.geometry.map(lambda geometry: make_valid(geometry) if not geometry.is_valid else geometry)
    if not regions.geometry.is_valid.all():
        raise ValueError(f"{version}: nicht reparierbare NUTS-Geometrie.")

    # Transform each shared source edge identically into the browser CRS.
    display = regions.to_crs(4326)
    union = unary_union(list(display.geometry))
    overlap = sum(geometry.area for geometry in display.geometry) - union.area
    if abs(overlap) > 1e-10:
        raise ValueError(f"{version}: unerwartete Flächenüberlappungen in der Anzeigegeometrie.")

    features = [
        {
            "type": "Feature",
            "properties": {"NUTS_ID": str(row.NUTS_ID), "NUTS_NAME": str(row.NUTS_NAME)},
            "geometry": mapping(row.geometry),
        }
        for row in display.itertuples()
    ]
    target.write_text(json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{target.relative_to(ROOT)}: {len(features)} topologisch geprüfte Regionen")


def main() -> None:
    for version in VERSIONS:
        build(version)


if __name__ == "__main__":
    main()