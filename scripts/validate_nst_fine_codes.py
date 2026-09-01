#!/usr/bin/env python3
"""Validate NST-2007 fine codes from rail and inland-waterway source data.

Rail and inland-waterway source files contain three-character NST-2007 fine
positions (for example ``011``, ``01A`` and ``192``), not merely the 20
divisions shown in the dashboard.  This regression test rejects an unknown
fine-code shape and independently reconciles the official C1–C7 aggregation
with the generated O-D fact table.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
FACT_PATH = ROOT / "data" / "processed" / "fact_od_flows.parquet"
CORE_HEAD = ROOT / "js" / "source" / "core-head.js"

DIVISION_TO_GROUP = {
    "01": "1", "02": "1", "03": "1",
    "04": "2", "05": "2", "06": "2",
    "07": "3", "08": "3", "09": "3", "10": "4",
    "11": "5", "12": "5", "13": "5", "14": "6",
    "15": "7", "16": "7", "17": "7", "18": "7", "19": "7", "20": "7",
}

GROUP_NAMES = {
    "1": "Erzeugnisse der Land- und Forstwirtschaft, Rohstoffe",
    "2": "Konsumgüter zum kurzfristigen Verbrauch, Holzwaren",
    "3": "Mineralische, chemische und Mineralölerzeugnisse",
    "4": "Metalle und Metallerzeugnisse",
    "5": "Maschinen und Ausrüstungen, langlebige Konsumgüter",
    "6": "Sekundärrohstoffe, Abfälle",
    "7": "Sonstige Produkte",
}

DIVISION_SHORT_NAMES = {
    "01": "Erzeugnisse der Land- und Forstwirtschaft sowie der Fischerei",
    "02": "Kohle, rohes Erdöl und Erdgas",
    "03": "Erze, Steine und Erden, sonstige Bergbauerzeugnisse",
    "04": "Nahrungs- und Genussmittel",
    "05": "Textilien, Bekleidung, Leder und Lederwaren",
    "06": "Holzwaren, Papier, Pappe, Druckerzeugnisse",
    "07": "Kokerei- und Mineralölerzeugnisse",
    "08": "Chemische Erzeugnisse etc.",
    "09": "Sonstige Mineralerzeugnisse (Glas, Zement, Gips etc.)",
    "10": "Metalle und Metallerzeugnisse",
    "11": "Maschinen und Ausrüstungen, Haushaltsgeräte etc.",
    "12": "Fahrzeuge",
    "13": "Möbel, Schmuck, Musikinstrumente, Sportgeräte etc.",
    "14": "Sekundärrohstoffe, Abfälle",
    "15": "Post, Pakete",
    "16": "Geräte und Material für die Güterbeförderung",
    "17": "Umzugsgut und sonstige nichtmarktbestimmte Güter",
    "18": "Sammelgut",
    "19": "Gutart unbekannt",
    "20": "Sonstige Güter a.n.g.",
}

SOURCES = {
    "rail": {
        "label": "Schiene",
        "pattern": RAW_DIR / "SGV OpenData" / "eb_opendata_*.csv",
        "encoding": "latin-1",
        "code": "Guetergruppe_NST2007",
        "year": "Referenzzeitraum_Jahr",
        "origin": "Versandregion_NUTS2024",
        "destination": "Empfangsregion_NUTS2024",
        "tonnes": "Befoerderungsmenge_in_Tonnen",
        "tkm": "Befoerderungsleistung_in_TKM",
    },
    "iww": {
        "label": "Binnenschiff",
        "pattern": RAW_DIR / "IWW OpenData" / "IWW_OpenData_*.csv",
        "encoding": "utf-8",
        "code": "NST2007",
        "year": "Referenzzeitraum_Jahr",
        "origin": "Einladeregion_NUTS3",
        "destination": "Ausladeregion_NUTS3",
        "tonnes": "Tonnen",
        "tkm": "Tonnen_km",
    },
}


def code_to_division(code: str) -> str | None:
    """Return the NST-2007 division for a valid three-character fine code."""
    normalized = str(code).strip().upper()
    if len(normalized) != 3 or not normalized[:2].isdigit() or not normalized[2].isalnum():
        return None
    return normalized[:2] if normalized[:2] in DIVISION_TO_GROUP else None


def raw_aggregates(con: duckdb.DuckDBPyConnection, spec: dict[str, object]) -> tuple[dict[str, int], dict[tuple[int, str], tuple[float, float]]]:
    pattern = str(spec["pattern"]).replace("\\", "/")
    code = str(spec["code"])
    year = str(spec["year"])
    origin = str(spec["origin"])
    destination = str(spec["destination"])
    tonnes = str(spec["tonnes"])
    tkm = str(spec["tkm"])
    encoding = str(spec["encoding"])
    rows = con.execute(
        f"""
        WITH raw AS (
            SELECT
                CAST({year} AS INTEGER) AS year_ref,
                TRIM(CAST({code} AS VARCHAR)) AS raw_code,
                CAST({origin} AS VARCHAR) AS origin,
                CAST({destination} AS VARCHAR) AS destination,
                TRY_CAST(REPLACE(CAST({tonnes} AS VARCHAR), ',', '.') AS DOUBLE) AS tonnes,
                TRY_CAST(REPLACE(CAST({tkm} AS VARCHAR), ',', '.') AS DOUBLE) AS tkm
            FROM read_csv('{pattern}', delim=';', header=true, all_varchar=true,
                          union_by_name=true, encoding='{encoding}')
        )
        SELECT year_ref, raw_code, SUM(tonnes) AS tonnes, SUM(tkm) AS tkm
        FROM raw
        WHERE origin IS NOT NULL AND destination IS NOT NULL
        GROUP BY 1, 2
        """
    ).fetchall()

    code_counts: dict[str, int] = defaultdict(int)
    aggregates: dict[tuple[int, str], list[float]] = defaultdict(lambda: [0.0, 0.0])
    invalid: list[str] = []
    for year_ref, raw_code, tonnes_value, tkm_value in rows:
        division = code_to_division(str(raw_code))
        if division is None:
            invalid.append(str(raw_code))
            continue
        code_counts[str(raw_code)] += 1
        group = DIVISION_TO_GROUP[division]
        aggregate = aggregates[(int(year_ref), group)]
        aggregate[0] += float(tonnes_value or 0.0)
        aggregate[1] += float(tkm_value or 0.0)
    if invalid:
        raise AssertionError("Ungültige NST-2007-Feinposition(en): " + ", ".join(sorted(set(invalid))))
    missing_divisions = sorted(set(DIVISION_TO_GROUP) - {code_to_division(code) for code in code_counts})
    if missing_divisions:
        raise AssertionError("In den vollständigen Quelldateien fehlen NST-Abteilungen: " + ", ".join(missing_divisions))
    return dict(code_counts), {key: tuple(value) for key, value in aggregates.items()}


def validate_fact_reconciliation(con: duckdb.DuckDBPyConnection, mode: str, expected: dict[tuple[int, str], tuple[float, float]]) -> int:
    actual = {
        (int(year_ref), str(group)): (float(tonnes or 0.0), float(tkm or 0.0))
        for year_ref, group, tonnes, tkm in con.execute(
            f"""
            SELECT year_ref, CAST(group_7_id AS VARCHAR), SUM(tonnes), SUM(tkm)
            FROM read_parquet('{FACT_PATH.as_posix()}')
            WHERE mode_transport = '{mode}'
            GROUP BY 1, 2
            """
        ).fetchall()
    }
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        unexpected = sorted(set(actual) - set(expected))
        raise AssertionError(f"{mode}: abweichende Jahr/C-Gruppe-Schlüssel; fehlen={missing}, zusätzlich={unexpected}")
    for key, (expected_tonnes, expected_tkm) in expected.items():
        actual_tonnes, actual_tkm = actual[key]
        if abs(actual_tonnes - expected_tonnes) > 0.1 or abs(actual_tkm - expected_tkm) > 0.1:
            raise AssertionError(
                f"{mode} {key[0]}/C{key[1]}: Faktendatei stimmt nicht mit den NST-Feinpositionen überein "
                f"(t {actual_tonnes} statt {expected_tonnes}; tkm {actual_tkm} statt {expected_tkm})."
            )
    return len(expected)


def validate_dashboard_taxonomy() -> None:
    source = CORE_HEAD.read_text(encoding="utf-8")
    missing_labels = [
        f'"{division}": "{division} {label}"'
        for division, label in DIVISION_SHORT_NAMES.items()
        if f'"{division}": "{division} {label}"' not in source
    ]
    missing_groups = [
        f'"{group}": "{label}"'
        for group, label in GROUP_NAMES.items()
        if f'"{group}": "{label}"' not in source
    ]
    if missing_labels or missing_groups:
        details = [*missing_labels, *missing_groups]
        raise AssertionError("Dashboard-Taxonomie weicht von der NST-2007-Referenz ab: " + "; ".join(details))


def main() -> None:
    if not FACT_PATH.exists():
        raise SystemExit(f"Faktendatei fehlt: {FACT_PATH}")
    con = duckdb.connect()
    results: list[str] = []
    try:
        for mode, spec in SOURCES.items():
            codes, expected = raw_aggregates(con, spec)
            cases = validate_fact_reconciliation(con, mode, expected)
            results.append(f"{spec['label']}: {len(codes)} Feinpositionen, {cases} Jahr/C-Gruppen-Summen")
    finally:
        con.close()
    validate_dashboard_taxonomy()
    print("BESTANDEN: " + "; ".join(results) + "; NST-20-Kurzbezeichnungen und C1–C7-Texte stimmen mit der Referenz überein.")


if __name__ == "__main__":
    main()
