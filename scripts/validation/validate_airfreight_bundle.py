#!/usr/bin/env python3
"""Validate the compact air-freight web bundle against selected raw values."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "pipelines"))

import build_airfreight_data as pipeline  # noqa: E402


OUTPUT = ROOT / "data" / "processed" / "web_airfreight.json"


def raw_value(path: Path, expected_dimensions: list[str], year: str) -> float:
    for dimensions, values in pipeline.read_eurostat_rows(path):
        if dimensions == expected_dimensions:
            value = values.get(year)
            if value is None:
                raise AssertionError(f"Rohwert fehlt: {path.name} {expected_dimensions} {year}")
            return value
    raise AssertionError(f"Rohdatenzeile fehlt: {path.name} {expected_dimensions}")


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: erwartet {expected!r}, erhalten {actual!r}")


def assert_close(actual: float, expected: float, label: str, tolerance: float = 1e-6) -> None:
    if abs(actual - expected) > tolerance:
        raise AssertionError(f"{label}: erwartet {expected!r}, erhalten {actual!r}")


def raw_relation_sum(reporting: str, measure: str, year: str) -> float:
    total = 0.0
    for dimensions, values in pipeline.read_eurostat_rows(pipeline.GOR):
        if len(dimensions) != 4 or dimensions[:3] != ["A", "T", measure]:
            continue
        pair = pipeline.relation_codes(dimensions[3])
        value = values.get(year)
        if pair and pair[0] == reporting and value is not None and value > 0:
            total += value
    return total


def main() -> None:
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    metadata = data["metadata"]

    assert_equal(metadata["availableNationalYears"], list(range(2016, 2026)), "Nationale Jahre")
    assert_equal(metadata["availableAirportYears"], list(range(2016, 2026)), "Flughafenjahre")
    assert_equal(metadata["availableAirportFlightYears"], list(range(2016, 2025)), "Belastbare Flughafen-Flugjahre")
    assert_equal(metadata["availableRelationYears"], list(range(2016, 2025)), "Relationsjahre")
    assert_equal(metadata["latestNationalYear"], 2025, "Letztes nationales Jahr")
    assert_equal(metadata["latestAirportYear"], 2025, "Letztes Flughafenjahr")
    assert_equal(metadata["latestRelationYear"], 2024, "Letztes Relationsjahr")
    assert "2025" not in data["relations"], "2025 darf nicht als Relationsjahr vorgetäuscht werden"

    published_2025 = [
        record for record in data["airportValues"]["2025"].values()
        if record.get("tonnes", {}).get("all") is not None
    ]
    assert_equal(len(published_2025), 22, "Flughäfen mit veröffentlichtem 2025-Wert")

    coverage = metadata["coordinateCoverage"]
    assert_equal(coverage["codesInWebBundle"], 281, "Koordinatenaudit: relevante Codes")
    assert_equal(coverage["withCoordinates"], 281, "Koordinatenaudit: Codes mit Punkt")
    assert_equal(coverage["missingCodes"], [], "Koordinatenaudit: fehlende Codes")
    assert_equal(coverage["sourceCounts"]["GISCO Airports 2024"], 279, "GISCO-Koordinaten")
    assert_equal(coverage["sourceCounts"]["OurAirports"], 2, "OurAirports-Ergänzungen")
    assert_equal(data["airports"]["CYYC"]["coordinateSource"], "OurAirports", "CYYC-Quelle")
    assert_equal(data["airports"]["EKCH"]["coordinateSource"], "OurAirports", "EKCH-Quelle")
    assert_equal(data["airports"]["EDDF"]["name"], "Frankfurt/Main", "Deutscher Anzeigename EDDF")
    assert_equal(data["airports"]["EDDP"]["name"], "Leipzig/Halle", "Deutscher Anzeigename EDDP")
    assert_equal(data["airports"]["EDDK"]["name"], "Köln/Bonn", "Deutscher Anzeigename EDDK")

    raw_national_tonnes = raw_value(
        pipeline.GOOC, ["A", "T", "FRM_LD_NLD", "TOTAL", "TOTAL", "DE"], "2025"
    )
    raw_national_flights = raw_value(
        pipeline.GOOC, ["A", "FLIGHT", "CAF_FRM", "TOTAL", "TOTAL", "DE"], "2025"
    )
    assert_equal(data["national"]["2025"]["tonnes"]["all"], raw_national_tonnes, "National Tonnen 2025")
    assert_equal(data["national"]["2025"]["flights"]["all"], raw_national_flights, "National Flüge 2025")

    raw_eddf_tonnes = raw_value(
        pipeline.GOOA, ["A", "T", "FRM_LD_NLD", "TOTAL", "TOTAL", "DE_EDDF"], "2025"
    )
    assert_equal(data["airportValues"]["2025"]["EDDF"]["tonnes"]["all"], raw_eddf_tonnes, "EDDF Tonnen 2025")
    assert "flights" not in data["airportValues"]["2025"]["EDDF"], "Unplausible EDDF-Flugzahl 2025 darf nicht ausgeliefert werden"

    raw_relation_tonnes = raw_value(
        pipeline.GOR, ["A", "T", "FRM_LD_NLD", "DE_EDDF_CN_ZSPD"], "2024"
    )
    raw_relation_flights = raw_value(
        pipeline.GOR, ["A", "FLIGHT", "CAF_FRM", "DE_EDDF_CN_ZSPD"], "2024"
    )
    raw_relation_tonnes_previous = raw_value(
        pipeline.GOR, ["A", "T", "FRM_LD_NLD", "DE_EDDF_CN_ZSPD"], "2023"
    )
    raw_relation_tonnes_baseline = raw_value(
        pipeline.GOR, ["A", "T", "FRM_LD_NLD", "DE_EDDF_CN_ZSPD"], "2016"
    )
    eddf_relations = data["relations"]["2024"]["EDDF"]
    tonnes_by_partner = {item["partner"]: item for item in eddf_relations["tonnes"]["all"]}
    flights_by_partner = {item["partner"]: item["value"] for item in eddf_relations["flights"]["all"]}
    zspd_tonnes = tonnes_by_partner["ZSPD"]
    assert_equal(zspd_tonnes["value"], raw_relation_tonnes, "EDDF–ZSPD Tonnen 2024")
    assert_equal(zspd_tonnes["previous_value"], raw_relation_tonnes_previous, "EDDF–ZSPD Tonnen 2023")
    assert_equal(zspd_tonnes["baseline_value"], raw_relation_tonnes_baseline, "EDDF–ZSPD Tonnen 2016")
    assert_equal(
        zspd_tonnes["yoy_pct"],
        (raw_relation_tonnes - raw_relation_tonnes_previous) / raw_relation_tonnes_previous * 100,
        "EDDF–ZSPD Veränderung zum Vorjahr",
    )
    assert_equal(
        zspd_tonnes["trend_pct"],
        (raw_relation_tonnes - raw_relation_tonnes_baseline) / raw_relation_tonnes_baseline * 100,
        "EDDF–ZSPD Veränderung gegenüber 2016",
    )
    all_published_eddf_tonnes = raw_relation_sum("EDDF", "FRM_LD_NLD", "2024")
    assert_close(
        data["relationTotals"]["2024"]["EDDF"]["tonnes"]["all"],
        all_published_eddf_tonnes,
        "EDDF Summe aller veröffentlichten Tonnen-Verbindungen",
    )
    assert_equal(flights_by_partner["ZSPD"], raw_relation_flights, "EDDF–ZSPD Flüge 2024")

    assert "Passagierflüge mit Beiladefracht sind nicht enthalten" in metadata["measures"]["flights"]["scope"]
    assert OUTPUT.stat().st_size < 2 * 1024 * 1024, "Web-Bündel überschreitet 2 MiB"
    print("Luftfracht-Bündel geprüft: Rohwerte, Relationsanteile, 2025-Plausibilitätsgrenze, Jahre, Flugdefinition und 281/281 Koordinaten stimmen.")


if __name__ == "__main__":
    main()
