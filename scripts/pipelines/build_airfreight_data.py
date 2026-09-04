#!/usr/bin/env python3
"""Build the compact Eurostat air-freight bundle used by the dashboard.

The source tables are Eurostat TSV bulk downloads.  Only annual observations
from 2016 onward and the documented freight-and-mail measures are retained.
Airport coordinates come from GISCO first and from OurAirports only when a
code is missing in GISCO.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sqlite3
import tempfile
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "Luftverkehr"
LOCATIONS = RAW / "Flughafenstandorte"
OUTPUT = ROOT / "data" / "processed" / "web_airfreight.json"

GOOC = RAW / "estat_avia_gooc.tsv"
GOOA = RAW / "estat_avia_gooa.tsv"
GOR = RAW / "estat_avia_gor_de.tsv"
GISCO_ZIP = LOCATIONS / "GISCO_AIRP_PT_2024_GPKG.zip"
OURAIRPORTS = LOCATIONS / "ourairports_airports_2026-09-03.csv"

# Deutschsprachige Anzeigeformen der amtlichen Eurostat-Flughafenlabels. Die
# Statistik-API liefert für deutsche Flughäfen beispielsweise FRANKFURT/MAIN,
# KOELN/BONN und LEIPZIG/HALLE; die Schreibweise wird hier ausschließlich
# orthografisch (Umlaute/Großschreibung) für die Oberfläche aufbereitet.
GERMAN_AIRPORT_DISPLAY_NAMES = {
    "EDDB": "Berlin Brandenburg",
    "EDDC": "Dresden",
    "EDDE": "Erfurt-Weimar",
    "EDDF": "Frankfurt/Main",
    "EDDG": "Münster/Osnabrück",
    "EDDH": "Hamburg",
    "EDDK": "Köln/Bonn",
    "EDDL": "Düsseldorf",
    "EDDM": "München",
    "EDDN": "Nürnberg",
    "EDDP": "Leipzig/Halle",
    "EDDR": "Saarbrücken",
    "EDDS": "Stuttgart",
    "EDDT": "Berlin-Tegel",
    "EDDV": "Hannover",
    "EDDW": "Bremen",
    "EDFH": "Frankfurt-Hahn",
    "EDJA": "Memmingen",
    "EDLP": "Paderborn/Lippstadt",
    "EDLV": "Niederrhein (Weeze)",
    "EDLW": "Dortmund",
    "EDNY": "Friedrichshafen",
    "EDSB": "Karlsruhe/Baden-Baden",
    "EDXW": "Sylt",
    "ETNL": "Rostock-Laage",
}

START_YEAR = 2016
END_YEAR = 2025
YEARS = [str(year) for year in range(START_YEAR, END_YEAR + 1)]
TONNAGE_MEASURES = {
    "FRM_LD_NLD": "all",
    "FRM_LD": "outbound",
    "FRM_NLD": "inbound",
}
FLIGHT_MEASURES = {
    "CAF_FRM": "all",
    "CAF_FRM_DEP": "outbound",
    "CAF_FRM_ARR": "inbound",
}
TOP_RELATIONS_STORED = 25
EXCLUDED_AIRPORT_FLIGHT_YEARS = {"2025"}
NUMBER_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_value(raw: str) -> float | None:
    text = raw.strip()
    if not text or text.startswith(":"):
        return None
    match = NUMBER_RE.match(text.replace(",", "."))
    return float(match.group(0)) if match else None


def read_eurostat_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        columns = {name.strip(): index for index, name in enumerate(header)}
        year_columns = {year: columns[year] for year in YEARS if year in columns}
        for row in reader:
            if not row:
                continue
            dimensions = [part.strip() for part in row[0].split(",")]
            values = {
                year: parse_value(row[index]) if index < len(row) else None
                for year, index in year_columns.items()
            }
            yield dimensions, values


def read_gisco_locations() -> dict[str, dict]:
    Path("C:/tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="wbp-airfreight-gisco-", dir="C:/tmp") as tmp:
        with zipfile.ZipFile(GISCO_ZIP) as archive:
            gpkg_member = next(name for name in archive.namelist() if name.lower().endswith(".gpkg"))
            archive.extract(gpkg_member, tmp)
        gpkg = Path(tmp) / gpkg_member
        connection = sqlite3.connect(gpkg)
        try:
            rows = connection.execute(
                "SELECT ICAO_CODE, CNTR_CODE, LAT, LONG_, NAME FROM AIRP_PT_2024"
            ).fetchall()
        finally:
            connection.close()

    locations: dict[str, dict] = {}
    for code, country, lat, lng, name in rows:
        code = str(code or "").strip().upper()
        if len(code) != 4 or not lat or not lng:
            continue
        locations[code] = {
            "code": code,
            "name": str(name or code).strip(),
            "country": str(country or "").strip().upper(),
            "lat": round(float(lat), 6),
            "lng": round(float(lng), 6),
            "coordinateSource": "GISCO Airports 2024",
            "coordinateSourceDate": "2024",
        }
    return locations


def supplement_ourairports(locations: dict[str, dict], needed_codes: set[str]) -> None:
    missing = needed_codes.difference(locations)
    if not missing:
        return
    with OURAIRPORTS.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            code = str(row.get("ident") or "").strip().upper()
            if code not in missing:
                continue
            try:
                lat = float(row["latitude_deg"])
                lng = float(row["longitude_deg"])
            except (KeyError, TypeError, ValueError):
                continue
            locations[code] = {
                "code": code,
                "name": str(row.get("name") or code).strip(),
                "country": str(row.get("iso_country") or "").strip().upper(),
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "coordinateSource": "OurAirports",
                "coordinateSourceDate": "2026-09-03",
            }


def airport_code(geo: str) -> str | None:
    parts = geo.split("_")
    return parts[1].upper() if len(parts) == 2 and parts[0] == "DE" and len(parts[1]) == 4 else None


def relation_codes(pair: str) -> tuple[str, str] | None:
    parts = pair.split("_")
    if len(parts) != 4 or parts[0] != "DE" or len(parts[1]) != 4 or len(parts[3]) != 4:
        return None
    return parts[1].upper(), parts[3].upper()


def is_physical_airport(location: dict | None) -> bool:
    if not location:
        return False
    name = str(location.get("name") or "").casefold()
    return "unknown airport" not in name and "unkown airport" not in name


def collect_needed_codes() -> set[str]:
    codes: set[str] = set()
    for dimensions, values in read_eurostat_rows(GOOA):
        if len(dimensions) != 6 or dimensions[:5] != ["A", "T", "FRM_LD_NLD", "TOTAL", "TOTAL"]:
            continue
        code = airport_code(dimensions[5])
        if code and any(value is not None for value in values.values()):
            codes.add(code)
    for dimensions, values in read_eurostat_rows(GOR):
        if len(dimensions) != 4 or dimensions[:3] != ["A", "T", "FRM_LD_NLD"]:
            continue
        pair = relation_codes(dimensions[3])
        if pair and any(value is not None for value in values.values()):
            codes.update(pair)
    return codes


def build_bundle() -> dict:
    needed_codes = collect_needed_codes()
    locations = read_gisco_locations()
    supplement_ourairports(locations, needed_codes)
    for code, display_name in GERMAN_AIRPORT_DISPLAY_NAMES.items():
        if code in locations:
            locations[code]["name"] = display_name
            locations[code]["nameSource"] = "Eurostat-Flughafenlabel, deutschsprachige Anzeigeform"

    national: dict[str, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    for dimensions, values in read_eurostat_rows(GOOC):
        if len(dimensions) != 6:
            continue
        freq, unit, measure, schedule, coverage, geo = dimensions
        if (freq, schedule, coverage, geo) != ("A", "TOTAL", "TOTAL", "DE"):
            continue
        metric = "tonnes" if unit == "T" else "flights" if unit == "FLIGHT" else None
        direction = (TONNAGE_MEASURES if metric == "tonnes" else FLIGHT_MEASURES if metric == "flights" else {}).get(measure)
        if not metric or not direction:
            continue
        for year, value in values.items():
            if value is not None:
                national[year][metric][direction] = value

    airports: dict[str, dict[str, dict]] = defaultdict(dict)
    valid_airport_codes: set[str] = set()
    published_airport_codes: set[str] = set()
    for dimensions, values in read_eurostat_rows(GOOA):
        if len(dimensions) != 6:
            continue
        freq, unit, measure, schedule, coverage, geo = dimensions
        if (freq, schedule, coverage) != ("A", "TOTAL", "TOTAL"):
            continue
        metric = "tonnes" if unit == "T" else "flights" if unit == "FLIGHT" else None
        direction = (TONNAGE_MEASURES if metric == "tonnes" else FLIGHT_MEASURES if metric == "flights" else {}).get(measure)
        code = airport_code(geo)
        if not metric or not direction or not code or not is_physical_airport(locations.get(code)):
            continue
        for year, value in values.items():
            if value is None:
                continue
            # The 2025 AVIA_GOOA CAF_FRM airport values are internally
            # inconsistent with AVIA_GOOC: German airport values sum to
            # 1,573,111 flights, while the national total is 116,671. Several
            # airports also jump to values resembling all commercial aircraft
            # movements. Keep the raw files unchanged, but do not publish this
            # airport-level slice until Eurostat corrects or explains it.
            if metric == "flights" and year in EXCLUDED_AIRPORT_FLIGHT_YEARS:
                continue
            record = airports[year].setdefault(code, {"code": code})
            record.setdefault(metric, {})[direction] = value
            if metric == "tonnes" and direction == "all":
                published_airport_codes.add(code)
            if metric == "tonnes" and value > 0:
                valid_airport_codes.add(code)

    relations_raw: dict[str, dict[str, dict[str, list[dict]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    for dimensions, values in read_eurostat_rows(GOR):
        if len(dimensions) != 4:
            continue
        freq, unit, measure, pair_key = dimensions
        metric = "tonnes" if unit == "T" else "flights" if unit == "FLIGHT" else None
        direction = (TONNAGE_MEASURES if metric == "tonnes" else FLIGHT_MEASURES if metric == "flights" else {}).get(measure)
        pair = relation_codes(pair_key)
        if freq != "A" or not metric or not direction or not pair:
            continue
        reporting, partner = pair
        if reporting not in valid_airport_codes or reporting == partner:
            continue
        for year, value in values.items():
            if value is None or value <= 0:
                continue
            relations_raw[year][reporting][f"{metric}:{direction}"].append({
                "partner": partner,
                "value": value,
            })

    relation_lookup = {
        year: {
            reporting: {
                metric_direction: {item["partner"]: item["value"] for item in records}
                for metric_direction, records in directions.items()
            }
            for reporting, directions in reporting_airports.items()
        }
        for year, reporting_airports in relations_raw.items()
    }

    relations: dict[str, dict[str, dict[str, dict[str, list[dict]]]]] = {}
    relation_totals: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    for year, reporting_airports in relations_raw.items():
        relations[year] = {}
        relation_totals[year] = {}
        previous_year = str(int(year) - 1)
        baseline_year = str(START_YEAR)
        for reporting, directions in reporting_airports.items():
            relations[year][reporting] = {}
            relation_totals[year][reporting] = {}
            for metric_direction, records in directions.items():
                metric, direction = metric_direction.split(":", 1)
                records.sort(key=lambda item: (-item["value"], item["partner"]))
                all_published_sum = sum(max(0, item["value"]) for item in records)
                relation_totals[year][reporting].setdefault(metric, {})[direction] = all_published_sum
                enriched_records = []
                for record in records[:TOP_RELATIONS_STORED]:
                    partner = record["partner"]
                    current_value = record["value"]
                    previous_value = relation_lookup.get(previous_year, {}).get(reporting, {}).get(metric_direction, {}).get(partner)
                    baseline_value = relation_lookup.get(baseline_year, {}).get(reporting, {}).get(metric_direction, {}).get(partner)
                    enriched_records.append({
                        **record,
                        "previous_value": previous_value,
                        "baseline_value": baseline_value,
                        "yoy_pct": ((current_value - previous_value) / previous_value * 100) if previous_value else None,
                        "trend_pct": ((current_value - baseline_value) / baseline_value * 100) if baseline_value else None,
                    })
                relations[year][reporting].setdefault(metric, {})[direction] = enriched_records

    national_years = sorted(year for year, record in national.items() if record.get("tonnes", {}).get("all") is not None)
    airport_years = sorted(
        year for year, records in airports.items()
        if any(record.get("tonnes", {}).get("all", 0) > 0 for record in records.values())
    )
    relation_years = sorted(
        year for year, records in relations.items()
        if any(record.get("tonnes") for record in records.values())
    )

    # The location audit covers all German airports with published annual
    # values plus every partner in the fachlich filtered relation source. It is
    # deliberately wider than the Top-25 relations retained for the browser.
    visible_codes = set(published_airport_codes)
    for reporting_airports in relations_raw.values():
        visible_codes.update(reporting_airports)
        for metric_directions in reporting_airports.values():
            visible_codes.update(
                item["partner"] for item in metric_directions.get("tonnes:all", [])
            )

    airport_master = {}
    for code in sorted(visible_codes):
        location = locations.get(code)
        airport_master[code] = location or {
            "code": code,
            "name": code,
            "country": "",
            "lat": None,
            "lng": None,
            "coordinateSource": None,
            "coordinateSourceDate": None,
        }

    missing_coordinates = sorted(code for code, item in airport_master.items() if item["lat"] is None)
    source_counts = {
        source: sum(1 for item in airport_master.values() if item["coordinateSource"] == source)
        for source in ("GISCO Airports 2024", "OurAirports")
    }

    bundle = {
        "metadata": {
            "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "sourceDownloadDate": "2026-09-03",
            "yearStart": START_YEAR,
            "availableNationalYears": [int(year) for year in national_years],
            "availableAirportYears": [int(year) for year in airport_years],
            "availableAirportFlightYears": [
                int(year) for year in airport_years
                if year not in EXCLUDED_AIRPORT_FLIGHT_YEARS
            ],
            "availableRelationYears": [int(year) for year in relation_years],
            "latestNationalYear": int(national_years[-1]),
            "latestAirportYear": int(airport_years[-1]),
            "latestRelationYear": int(relation_years[-1]),
            "measures": {
                "tonnes": {
                    "label": "Fracht und Post",
                    "unit": "t",
                    "codes": TONNAGE_MEASURES,
                },
                "flights": {
                    "label": "Reine Fracht- und Postflüge",
                    "unit": "Anzahl",
                    "codes": FLIGHT_MEASURES,
                    "scope": "All-freight and mail commercial air flights; Passagierflüge mit Beiladefracht sind nicht enthalten.",
                },
            },
            "schedule": "TOTAL",
            "trafficCoverage": "TOTAL",
            "topRelationsStored": TOP_RELATIONS_STORED,
            "sourceTables": {
                "national": "Eurostat AVIA_GOOC",
                "airports": "Eurostat AVIA_GOOA",
                "relations": "Eurostat AVIA_GOR_DE",
                "coordinatesPrimary": "Eurostat/GISCO Airports 2024",
                "coordinatesSupplement": "OurAirports 2026-09-03",
                "germanAirportNames": "Eurostat Statistics API, deutschsprachige Flughafenlabels, geprüft 2026-09-04",
            },
            "sourceFiles": {
                path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)}
                for path in (GOOC, GOOA, GOR, GISCO_ZIP, OURAIRPORTS)
            },
            "coordinateCoverage": {
                "codesInWebBundle": len(airport_master),
                "withCoordinates": len(airport_master) - len(missing_coordinates),
                "missingCodes": missing_coordinates,
                "sourceCounts": source_counts,
            },
            "limitations": [
                "Relationsdaten enthalten nur von Eurostat veröffentlichte Verbindungen oberhalb der Veröffentlichungsschwellen.",
                "Relationssummen entsprechen weder zwingend dem Flughafenaufkommen noch der nationalen Gesamtmenge.",
                "Nationale Werte und Flughafenwerte werden wegen unterschiedlicher Zähllogiken nicht gegeneinander ausgetauscht.",
                "CAF_FRM zählt reine Fracht- und Postflüge; Passagierflüge mit Beiladefracht sind nicht enthalten.",
                "Flughafenbezogene Flugzahlen 2025 werden wegen eines Widerspruchs zwischen AVIA_GOOA und der nationalen AVIA_GOOC-Reihe nicht ausgeliefert; Tonnenwerte und nationale Flugzahlen 2025 bleiben erhalten.",
            ],
        },
        "airports": airport_master,
        "national": {year: national[year] for year in national_years},
        "airportValues": {
            year: {code: record for code, record in sorted(airports[year].items())}
            for year in airport_years
        },
        "relations": relations,
        "relationTotals": relation_totals,
    }

    assert bundle["metadata"]["latestNationalYear"] == 2025
    assert bundle["metadata"]["latestAirportYear"] == 2025
    assert bundle["metadata"]["latestRelationYear"] == 2024
    assert len([
        record for record in bundle["airportValues"]["2025"].values()
        if record.get("tonnes", {}).get("all") is not None
    ]) == 22
    assert bundle["metadata"]["coordinateCoverage"]["missingCodes"] == []
    return bundle

def main() -> None:
    bundle = build_bundle()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(bundle, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    size_mib = OUTPUT.stat().st_size / (1024 * 1024)
    metadata = bundle["metadata"]
    print(
        f"{OUTPUT.relative_to(ROOT)}: {size_mib:.2f} MiB; "
        f"Jahre national {metadata['availableNationalYears'][0]}–{metadata['latestNationalYear']}, "
        f"Flughäfen {metadata['availableAirportYears'][0]}–{metadata['latestAirportYear']}, "
        f"Relationen {metadata['availableRelationYears'][0]}–{metadata['latestRelationYear']}"
    )
    print(
        "Koordinatenabdeckung: "
        f"{metadata['coordinateCoverage']['withCoordinates']}/"
        f"{metadata['coordinateCoverage']['codesInWebBundle']}"
    )


if __name__ == "__main__":
    main()
