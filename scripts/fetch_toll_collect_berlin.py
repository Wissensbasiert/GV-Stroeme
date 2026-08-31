#!/usr/bin/env python3
"""Lädt monatliche Toll-Collect-Relationen für Berlin vollständig und prüfbar.

Die erzeugten GeoJSON-Dateien bleiben unverändert auf Relationsebene. Es findet
keine Aggregation oder Auswahl einzelner Kennwerte statt.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import date
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


LAYER_URL = (
    "https://webgis.toll-collect.de/server/rest/services/verkehrsportal/"
    "mautdaten_bund_monat_sz/FeatureServer/0"
)
QUERY_URL = f"{LAYER_URL}/query"
BERLIN_AGS = "11000000"
PAGE_SIZE = 2_000
TIMEOUT_SECONDS = 90
RETRIES = 3

EXPECTED_FIELDS = {
    "objectid",
    "monat",
    "richtung",
    "ags_start",
    "ags_ziel",
    "name_start",
    "name_ziel",
    "name",
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
}

DIRECTIONS = {
    "Quelle": {"direction": 0, "ags_field": "ags_start"},
    "Ziel": {"direction": 1, "ags_field": "ags_ziel"},
}


def month_starts(first: date, last: date) -> list[date]:
    """Return inclusive first days of all months from first through last."""
    result: list[date] = []
    current = first.replace(day=1)
    end = last.replace(day=1)
    while current <= end:
        result.append(current)
        current = (
            date(current.year + 1, 1, 1)
            if current.month == 12
            else date(current.year, current.month + 1, 1)
        )
    return result


def fetch_json(params: dict[str, str]) -> dict[str, Any]:
    url = f"{QUERY_URL}?{urlencode(params)}"
    last_error: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        try:
            with urlopen(url, timeout=TIMEOUT_SECONDS) as response:
                payload = json.load(response)
            if "error" in payload:
                raise RuntimeError(f"API-Fehler: {payload['error']}")
            return payload
        except (HTTPError, URLError, TimeoutError, RuntimeError) as error:
            last_error = error
            if attempt == RETRIES:
                break
            time.sleep(attempt * 2)
    raise RuntimeError(f"Abruf nach {RETRIES} Versuchen fehlgeschlagen: {last_error}")


def fetch_relation_set(
    month: date,
    label: str,
    *,
    return_geometry: bool = False,
) -> dict[str, Any]:
    definition = DIRECTIONS[label]
    where = (
        f"{definition['ags_field']} = '{BERLIN_AGS}' "
        f"AND monat = DATE '{month.isoformat()}' "
        f"AND richtung = {definition['direction']}"
    )
    features: list[dict[str, Any]] = []
    offset = 0

    while True:
        payload = fetch_json(
            {
                "where": where,
                "outFields": "*",
                "returnGeometry": "true" if return_geometry else "false",
                "orderByFields": "objectid ASC",
                "resultOffset": str(offset),
                "resultRecordCount": str(PAGE_SIZE),
                "f": "geojson",
            }
        )
        page = payload.get("features")
        if not isinstance(page, list):
            raise RuntimeError("Die API-Antwort enthält keine GeoJSON-Features.")
        features.extend(page)
        if not payload.get("exceededTransferLimit"):
            break
        if not page:
            raise RuntimeError("Leere Seite trotz exceededTransferLimit.")
        offset += len(page)

    for feature in features:
        properties = feature.get("properties", {})
        missing = EXPECTED_FIELDS.difference(properties)
        if missing:
            raise RuntimeError(f"Unvollständiger Feldsatz: {sorted(missing)}")
        if properties.get("richtung") != definition["direction"]:
            raise RuntimeError("Richtung in der Antwort weicht vom Filter ab.")
        if properties.get(definition["ags_field"]) != BERLIN_AGS:
            raise RuntimeError("Berlin-AGS in der Antwort weicht vom Filter ab.")

    return {
        "type": "FeatureCollection",
        "name": f"Berlin_{label}_{month:%Y-%m}",
        "features": features,
    }


def write_json(path: Path, content: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(content, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw/Straße/Lkw-Portal/Berlin"),
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    months = month_starts(date(2025, 8, 1), date(2026, 7, 1))
    manifest: dict[str, Any] = {
        "source": LAYER_URL,
        "area": "Berlin (AGS 11000000)",
        "period": "2025-08 bis 2026-07",
        "directions": {
            "Quelle": "ags_start = 11000000 und richtung = 0",
            "Ziel": "ags_ziel = 11000000 und richtung = 1",
        },
        "geometry": "nicht abgerufen (returnGeometry=false)",
        "fields": sorted(EXPECTED_FIELDS),
        "files": [],
    }

    for month in months:
        for label in DIRECTIONS:
            filename = f"Berlin_{label}_{month:%Y-%m}.geojson"
            output_path = output_dir / label / filename
            if output_path.exists() and not args.overwrite:
                raise FileExistsError(
                    f"{output_path} existiert bereits. Mit --overwrite bewusst ersetzen."
                )
            collection = fetch_relation_set(month, label)
            write_json(output_path, collection)
            relation_count = len(collection["features"])
            manifest["files"].append(
                {
                    "file": str(output_path.relative_to(output_dir)).replace("\\", "/"),
                    "month": month.isoformat(),
                    "role": label,
                    "relation_count": relation_count,
                }
            )
            print(f"{filename}: {relation_count} Relationen")

    write_json(output_dir / "README.json", manifest)
    print(f"Fertig: {len(manifest['files'])} Dateien in {output_dir}")


if __name__ == "__main__":
    main()
