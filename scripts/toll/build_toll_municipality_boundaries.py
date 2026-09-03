#!/usr/bin/env python3
"""Create local, unchanged BKG municipality display geometries for the toll map.

The dashboard never fetches individual municipal borders from the BKG WFS at
runtime.  This one-off build downloads the authoritative VG250 geometries,
keeps all current German municipality borders, and writes a
small index plus one GeoJSON file per Bundesland.  Splitting by Bundesland
lets the browser load only the files that overlap the current map view while
retaining the source's shared edges unchanged.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "processed" / "toll_municipalities.json"
TARGET_DIR = ROOT / "data" / "processed" / "toll_municipality_boundaries"
WFS_URL = "https://sgx.geodatenzentrum.de/wfs_vg250"
PAGE_SIZE = 2000


def request_json(params: dict[str, str]) -> dict:
    url = f"{WFS_URL}?{urlencode(params)}"
    with urlopen(url, timeout=120) as response:  # nosec B310: fixed public BKG endpoint
        return json.load(response)


def get_features(layer: str, extra: dict[str, str] | None = None) -> list[dict]:
    """Fetch all WFS pages and reject an incomplete or malformed response."""
    features: list[dict] = []
    expected_total: int | None = None
    offset = 0
    while True:
        params = {
            "SERVICE": "WFS",
            "VERSION": "2.0.0",
            "REQUEST": "GetFeature",
            "TYPENAMES": layer,
            "SRSNAME": "urn:ogc:def:crs:OGC::CRS84",
            "OUTPUTFORMAT": "application/json",
            "COUNT": str(PAGE_SIZE),
            "STARTINDEX": str(offset),
        }
        params.update(extra or {})
        payload = request_json(params)
        page = payload.get("features")
        if not isinstance(page, list):
            raise RuntimeError(f"{layer}: BKG-Antwort enthält keine Featureliste.")
        reported_total = payload.get("numberMatched")
        if isinstance(reported_total, int):
            if expected_total is None:
                expected_total = reported_total
            elif expected_total != reported_total:
                raise RuntimeError(f"{layer}: wechselnde numberMatched-Angabe.")
        features.extend(page)
        if not page or len(page) < PAGE_SIZE:
            break
        offset += len(page)
    if expected_total is not None and len(features) != expected_total:
        raise RuntimeError(
            f"{layer}: unvollständiger WFS-Abruf ({len(features)} von {expected_total})."
        )
    return features


def coordinates(geometry: dict) -> list[tuple[float, float]]:
    """Return all coordinate pairs without modifying the source geometry."""
    result: list[tuple[float, float]] = []

    def visit(value: object) -> None:
        if not isinstance(value, list) or not value:
            return
        if isinstance(value[0], (int, float)):
            if len(value) < 2:
                raise ValueError("Unvollständiges Koordinatenpaar.")
            result.append((float(value[0]), float(value[1])))
            return
        for child in value:
            visit(child)

    visit(geometry.get("coordinates"))
    return result


def bbox(features: list[dict]) -> list[float]:
    points = [point for feature in features for point in coordinates(feature["geometry"])]
    if not points:
        raise ValueError("Geometrien enthalten keine Koordinaten.")
    longitudes, latitudes = zip(*points)
    return [min(longitudes), min(latitudes), max(longitudes), max(latitudes)]


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    names_by_ags = {
        str(item["ags"]): str(item["name"])
        for item in registry.get("municipalities", [])
        if isinstance(item, dict) and str(item.get("ags", "")).isdigit()
    }
    if not names_by_ags:
        raise RuntimeError("Das Toll-Collect-Gemeinderegister ist leer.")

    # The public layer also carries historical/non-Germany geometries with the
    # same AGS. ``gf=4`` is the source's Germany scope. Keep every resulting
    # municipality, not just the smaller Toll-Collect search register: this is
    # what prevents visible gaps between neighbouring municipality borders.
    source_features = get_features("vg250:vg250_gem", {"CQL_FILTER": "gf=4"})
    selected: dict[str, dict] = {}
    for source_feature in source_features:
        properties = source_feature.get("properties") or {}
        ags = str(properties.get("ags", ""))
        if len(ags) != 8 or not ags.isdigit():
            raise RuntimeError(f"Ungültiger amtlicher Gemeindeschlüssel: {ags!r}.")
        geometry = source_feature.get("geometry")
        if not isinstance(geometry, dict) or geometry.get("type") not in {"Polygon", "MultiPolygon"}:
            raise RuntimeError(f"AGS {ags}: keine verwendbare Flächengeometrie.")
        if ags in selected:
            raise RuntimeError(f"AGS {ags}: doppelte BKG-Gemeindegeometrie.")
        source_name = ", ".join(
            value for value in (str(properties.get("bez", "")).strip(), str(properties.get("gen", "")).strip()) if value
        )
        # Preserve each source geometry in structure; only retain the display
        # properties the browser needs. The Traffic register's name wins where
        # it exists so selected relations and map labels use one spelling.
        selected[ags] = {
            "type": "Feature",
            "properties": {"ags": ags, "name": names_by_ags.get(ags, source_name or ags)},
            "geometry": geometry,
        }

    missing = sorted(set(names_by_ags).difference(selected))
    if missing:
        raise RuntimeError(
            "Für die folgenden Gemeinden fehlt eine amtliche BKG-Geometrie: "
            + ", ".join(missing[:12])
            + (" …" if len(missing) > 12 else "")
        )

    by_state: dict[str, list[dict]] = defaultdict(list)
    for ags, feature in selected.items():
        by_state[ags[:2]].append(feature)
    if len(by_state) != 16:
        raise RuntimeError(f"Unerwartete Anzahl Länderdateien: {len(by_state)}.")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    states = []
    for state_code, features in sorted(by_state.items()):
        features.sort(key=lambda feature: feature["properties"]["ags"])
        file_name = f"{state_code}.geojson"
        write_json(TARGET_DIR / file_name, {"type": "FeatureCollection", "features": features})
        states.append(
            {
                "code": state_code,
                "file": file_name,
                "bbox": bbox(features),
                "feature_count": len(features),
            }
        )

    country_features = get_features("vg250:vg250_sta", {"CQL_FILTER": "gf=4"})
    if len(country_features) != 1 or not isinstance(country_features[0].get("geometry"), dict):
        raise RuntimeError("Die BKG-Antwort enthält nicht genau eine Deutschland-Geometrie.")
    country = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Deutschland"},
                "geometry": country_features[0]["geometry"],
            }
        ],
    }
    write_json(TARGET_DIR / "deutschland.geojson", country)

    write_json(
        TARGET_DIR / "index.json",
        {
            "metadata": {
                "provider": "Bundesamt für Kartographie und Geodäsie (BKG)",
                "dataset": "VG250, Gemeinden und Staatsgrenze Deutschland",
                "license": "Datenlizenz Deutschland – Namensnennung – Version 2.0",
                "crs": "CRS84 / WGS84",
                "download_date": date.today().isoformat(),
                "processing": "Unveränderte BKG-Geometrien, nach Bundesland für die bedarfsgesteuerte Kartendarstellung aufgeteilt.",
                "municipality_count": len(selected),
                "toll_collect_selectable_count": len(names_by_ags),
            },
            "country_outline_file": "deutschland.geojson",
            "states": states,
        },
    )
    print(
        f"{TARGET_DIR.relative_to(ROOT)}: {len(selected)} Gemeinden in {len(states)} "
        "Länderdateien und eine Deutschlandgrenze"
    )


if __name__ == "__main__":
    main()
