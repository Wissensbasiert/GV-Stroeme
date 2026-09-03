#!/usr/bin/env python3
"""Führt die monatlichen Toll-Collect-Relationen für Berlin in eine CSV zusammen."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


INPUT_DIR = Path("data/raw/Straße/Lkw-Portal/Berlin")
OUTPUT_PATH = INPUT_DIR / "Berlin_Relationen_2025-08_bis_2026-07.csv"

FIELDNAMES = [
    "jahr",
    "monat",
    "perspektive_berlin",
    "richtung_api",
    "quelle_ags",
    "quelle_name",
    "ziel_ags",
    "ziel_name",
    "name_api",
    "anzahl_befahrungen",
    "fahrleistung_km",
    "land",
    "zeit_min_min",
    "zeit_min_max",
    "zeit_min_median_approx",
    "zeit_min_mittelw",
    "zeit_min_stdw",
    "distanz_km_min",
    "distanz_km_max",
    "distanz_km_median_approx",
    "distanz_km_mittelw",
    "distanz_km_stdw",
    "monat_api_unix_ms",
    "objectid_api",
]


def to_row(properties: dict[str, object], perspective: str) -> dict[str, object]:
    date_value = datetime.fromtimestamp(
        int(properties["monat"]) / 1_000, tz=timezone.utc
    )
    return {
        "jahr": date_value.year,
        "monat": date_value.month,
        "perspektive_berlin": f"Berlin als {perspective}",
        "richtung_api": properties["richtung"],
        "quelle_ags": properties["ags_start"],
        "quelle_name": properties["name_start"],
        "ziel_ags": properties["ags_ziel"],
        "ziel_name": properties["name_ziel"],
        "name_api": properties["name"],
        "anzahl_befahrungen": properties["anzahl_befahrungen"],
        "fahrleistung_km": properties["fahrleistung_km"],
        "land": properties["land"],
        "zeit_min_min": properties["zeit_min_min"],
        "zeit_min_max": properties["zeit_min_max"],
        "zeit_min_median_approx": properties["zeit_min_median_approx"],
        "zeit_min_mittelw": properties["zeit_min_mittelw"],
        "zeit_min_stdw": properties["zeit_min_stdw"],
        "distanz_km_min": properties["distanz_km_min"],
        "distanz_km_max": properties["distanz_km_max"],
        "distanz_km_median_approx": properties["distanz_km_median_approx"],
        "distanz_km_mittelw": properties["distanz_km_mittelw"],
        "distanz_km_stdw": properties["distanz_km_stdw"],
        "monat_api_unix_ms": properties["monat"],
        "objectid_api": properties["objectid"],
    }


def main() -> None:
    rows: list[dict[str, object]] = []
    for perspective in ("Quelle", "Ziel"):
        for path in sorted((INPUT_DIR / perspective).glob("*.geojson")):
            collection = json.loads(path.read_text(encoding="utf-8"))
            for feature in collection["features"]:
                rows.append(to_row(feature["properties"], perspective))

    rows.sort(
        key=lambda row: (
            row["jahr"],
            row["monat"],
            row["quelle_ags"],
            row["ziel_ags"],
            row["richtung_api"],
        )
    )

    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print(f"{OUTPUT_PATH}: {len(rows)} Zeilen, {len(FIELDNAMES)} Spalten")


if __name__ == "__main__":
    main()
