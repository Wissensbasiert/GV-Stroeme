#!/usr/bin/env python3
"""Derive a single, interior Bundesland-border layer from shipped NUTS-3 geometry."""

from __future__ import annotations

import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "processed" / "nuts3_de_2024_display.geojson"
TARGET = ROOT / "data" / "processed" / "nuts1_de_boundaries.geojson"


def line_parts(geometry):
    """Yield only positive-length lines from an arbitrary Shapely geometry."""
    if geometry.is_empty:
        return
    if geometry.geom_type == "LineString":
        if geometry.length > 0:
            yield geometry
        return
    if geometry.geom_type in {"MultiLineString", "GeometryCollection"}:
        for part in geometry.geoms:
            yield from line_parts(part)


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    by_state: dict[str, list] = defaultdict(list)
    for feature in source.get("features", []):
        nuts_id = str(feature.get("properties", {}).get("NUTS_ID", ""))
        geometry = feature.get("geometry")
        if len(nuts_id) < 3 or not geometry:
            continue
        by_state[nuts_id[:3]].append(shape(geometry))

    states = {nuts1_id: unary_union(geometries) for nuts1_id, geometries in by_state.items()}
    if len(states) != 16 or not all(geometry.is_valid for geometry in states.values()):
        raise ValueError("NUTS-3-Geometrien ergeben keine 16 gültigen Bundesländer.")

    # Draw every state border exactly once: shared interior lines only, no outer outline.
    # This prevents doubled SVG strokes where two dissolved state polygons touch.
    shared_lines = []
    for left, right in combinations(states.values(), 2):
        shared_lines.extend(line_parts(left.boundary.intersection(right.boundary)))
    borders = unary_union(shared_lines)
    if borders.is_empty:
        raise ValueError("Keine gemeinsamen Bundeslandgrenzen abgeleitet.")

    result = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"layer": "Bundeslandgrenzen"},
            "geometry": mapping(borders),
        }],
    }
    TARGET.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{TARGET.relative_to(ROOT)}: eine Ebene mit inneren Bundeslandgrenzen")


if __name__ == "__main__":
    main()