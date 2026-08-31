#!/usr/bin/env python3
"""Erzeugt kartierbare, über zwölf Monate aggregierte Berliner Mautrelationen.

Für die räumliche Darstellung werden Gemeinde-Polygone aus der Toll-Collect-API
abgerufen. Die Kennzahlen stammen weiterhin aus der zusammengeführten CSV.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from fetch_toll_collect_berlin import fetch_relation_set, month_starts


INPUT = Path("data/raw/Straße/Lkw-Portal/Berlin/Berlin_Relationen_2025-08_bis_2026-07.csv")
OUTPUT_DIR = Path("outputs/mautdaten_berlin_auswertung/karten")
BERLIN_AGS = "11000000"

MAPS = {
    "von_berlin": {
        "perspektive": "Berlin als Quelle",
        "api_label": "Quelle",
        "csv_ags": "ziel_ags",
        "csv_name": "ziel_name",
        "api_ags": "ags_ziel",
        "name": "Relationen von Berlin",
    },
    "nach_berlin": {
        "perspektive": "Berlin als Ziel",
        "api_label": "Ziel",
        "csv_ags": "quelle_ags",
        "csv_name": "quelle_name",
        "api_ags": "ags_start",
        "name": "Relationen nach Berlin",
    },
}


def read_rows() -> list[dict[str, str]]:
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def aggregate(rows: list[dict[str, str]], definition: dict[str, str]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row["perspektive_berlin"] != definition["perspektive"]:
            continue
        ags = row[definition["csv_ags"]]
        if ags == BERLIN_AGS:
            continue
        if ags not in grouped:
            grouped[ags] = {
                "ags": ags,
                "gebiet": row[definition["csv_name"]],
                "befahrungen": 0,
                "fahrleistung_km_summe": 0,
                "gewichtete_fahrzeit_summe": 0.0,
                "gewichtete_distanz_summe": 0.0,
                "relationen_monate": 0,
            }
        entry = grouped[ags]
        trips = int(row["anzahl_befahrungen"])
        entry["befahrungen"] += trips
        entry["fahrleistung_km_summe"] += int(row["fahrleistung_km"])
        entry["gewichtete_fahrzeit_summe"] += trips * float(row["zeit_min_mittelw"])
        entry["gewichtete_distanz_summe"] += trips * float(row["distanz_km_mittelw"])
        entry["relationen_monate"] += 1

    ordered = sorted(grouped.values(), key=lambda item: (-item["befahrungen"], item["gebiet"]))
    for rank, entry in enumerate(ordered, start=1):
        trips = entry["befahrungen"]
        entry["rang_nach_befahrungen"] = rank
        entry["top_10"] = rank <= 10
        entry["gewichtete_fahrzeit_min"] = round(entry.pop("gewichtete_fahrzeit_summe") / trips, 1)
        entry["gewichtete_distanz_km"] = round(entry.pop("gewichtete_distanz_summe") / trips, 1)
    return grouped


def build_map(definition: dict[str, str], rows: list[dict[str, str]]) -> dict[str, Any]:
    aggregates = aggregate(rows, definition)
    geometries: dict[str, tuple[dict[str, Any], str]] = {}
    for month in month_starts(date(2025, 8, 1), date(2026, 7, 1)):
        collection = fetch_relation_set(month, definition["api_label"], return_geometry=True)
        for feature in collection["features"]:
            properties = feature.get("properties", {})
            ags = properties.get(definition["api_ags"])
            if ags in aggregates and ags not in geometries and feature.get("geometry"):
                geometries[ags] = (feature["geometry"], month.isoformat())

    features = []
    for ags, entry in aggregates.items():
        geometry_info = geometries.get(ags)
        if geometry_info is None:
            continue
        geometry, geometry_month = geometry_info
        features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    **entry,
                    "perspektive": definition["perspektive"],
                    "geometrie_monat": geometry_month,
                },
            }
        )

    total_trips = sum(entry["befahrungen"] for entry in aggregates.values())
    mapped_trips = sum(feature["properties"]["befahrungen"] for feature in features)
    return {
        "type": "FeatureCollection",
        "name": definition["name"],
        "metadata": {
            "zeitraum": "2025-08 bis 2026-07",
            "perspektive": definition["perspektive"],
            "ausgeschlossen": "Berlin–Berlin",
            "gemeinden_gesamt": len(aggregates),
            "gemeinden_mit_geometrie": len(features),
            "befahrungen_gesamt": total_trips,
            "befahrungen_mit_geometrie": mapped_trips,
            "volumenabdeckung_prozent": round(mapped_trips / total_trips * 100, 2) if total_trips else None,
            "hinweis": (
                "Quelle und Ziel bezeichnen das Verwaltungsgebiet des Eintritts bzw. "
                "Austritts aus dem mautpflichtigen Netz, nicht zwingend den tatsächlichen "
                "Start- oder Zielort der gesamten Fahrt."
            ),
        },
        "features": sorted(features, key=lambda feature: feature["properties"]["rang_nach_befahrungen"]),
    }


def main() -> None:
    rows = read_rows()
    for file_stem, definition in MAPS.items():
        collection = build_map(definition, rows)
        output = OUTPUT_DIR / f"berlin_{file_stem}_2025-08_bis_2026-07.geojson"
        write_json(output, collection)
        metadata = collection["metadata"]
        print(
            f"{output.name}: {metadata['gemeinden_mit_geometrie']}/"
            f"{metadata['gemeinden_gesamt']} Gemeinden, "
            f"{metadata['volumenabdeckung_prozent']} % Volumenabdeckung"
        )


if __name__ == "__main__":
    main()
