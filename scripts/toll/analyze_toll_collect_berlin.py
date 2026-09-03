#!/usr/bin/env python3
"""Erzeugt prüfbare Kennzahlen für die Berliner Toll-Collect-Relationen."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


INPUT = Path("data/raw/Straße/Lkw-Portal/Berlin/Berlin_Relationen_2025-08_bis_2026-07.csv")
OUTPUT = Path("outputs/mautdaten_berlin_auswertung/analysis_data.json")


def as_int(row: dict[str, str], field: str) -> int:
    return int(row[field])


def weighted_mean(rows: Iterable[dict[str, str]], field: str) -> float | None:
    values = list(rows)
    denominator = sum(as_int(row, "anzahl_befahrungen") for row in values)
    if denominator == 0:
        return None
    return round(
        sum(as_int(row, "anzahl_befahrungen") * float(row[field]) for row in values)
        / denominator,
        1,
    )


def period_key(row: dict[str, str]) -> tuple[int, int]:
    return as_int(row, "jahr"), as_int(row, "monat")


def summarize_period(rows: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "befahrungen": sum(as_int(row, "anzahl_befahrungen") for row in rows),
        "relationen": len(rows),
        "gewichtete_fahrzeit_min": weighted_mean(rows, "zeit_min_mittelw"),
        "gewichtete_distanz_km": weighted_mean(rows, "distanz_km_mittelw"),
    }


def top_relations(
    rows: list[dict[str, str]],
    key_ags: str,
    key_name: str,
    limit: int = 10,
    exclude_ags: set[str] | None = None,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], int] = defaultdict(int)
    for row in rows:
        if exclude_ags and row[key_ags] in exclude_ags:
            continue
        grouped[(row[key_ags], row[key_name])] += as_int(row, "anzahl_befahrungen")
    total = sum(grouped.values())
    ordered = sorted(grouped.items(), key=lambda item: (-item[1], item[0][1]))[:limit]
    return [
        {
            "rang": index,
            "ags": ags,
            "gebiet": name,
            "befahrungen": count,
            "anteil_prozent": round(count / total * 100, 2) if total else None,
        }
        for index, ((ags, name), count) in enumerate(ordered, start=1)
    ]


def top_relations_with_route_metrics(
    rows: list[dict[str, str]],
    key_ags: str,
    key_name: str,
    limit: int = 10,
    exclude_ags: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Aggregiert die häufigsten Gemeinde-Relationen mit Zeit und Distanz.

    Die Zeit- und Distanzwerte sind mit der Zahl der Befahrungen gewichtete
    Mittelwerte der bereits aggregierten Relationen.
    """
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if exclude_ags and row[key_ags] in exclude_ags:
            continue
        grouped[(row[key_ags], row[key_name])].append(row)

    ordered = sorted(
        grouped.items(),
        key=lambda item: (-sum(as_int(row, "anzahl_befahrungen") for row in item[1]), item[0][1]),
    )[:limit]
    total = sum(
        as_int(row, "anzahl_befahrungen")
        for relation_rows in grouped.values()
        for row in relation_rows
    )
    return [
        {
            "rang": index,
            "ags": ags,
            "gebiet": name,
            "befahrungen": sum(as_int(row, "anzahl_befahrungen") for row in relation_rows),
            "anteil_prozent": round(
                sum(as_int(row, "anzahl_befahrungen") for row in relation_rows) / total * 100,
                2,
            ) if total else None,
            "gewichtete_fahrzeit_min": weighted_mean(relation_rows, "zeit_min_mittelw"),
            "gewichtete_distanz_km": weighted_mean(relation_rows, "distanz_km_mittelw"),
            "relationen": len(relation_rows),
        }
        for index, ((ags, name), relation_rows) in enumerate(ordered, start=1)
    ]


DISTANCE_CLASSES = (
    ("unter 50 km", 0, 50),
    ("50 bis unter 100 km", 50, 100),
    ("100 bis unter 200 km", 100, 200),
    ("200 bis unter 300 km", 200, 300),
    ("300 km und mehr", 300, None),
)

MONTH_LABELS = (
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
)


def format_period(year: int, month: int) -> str:
    return f"{MONTH_LABELS[month - 1]} {year}"


def distance_class_summary(rows: list[dict[str, str]], perspective: str) -> list[dict[str, Any]]:
    """Klassen nach mittlerer Distanz der Gemeinde-Relation, nicht je Einzelfahrt."""
    total = sum(as_int(row, "anzahl_befahrungen") for row in rows)
    result = []
    for label, lower, upper in DISTANCE_CLASSES:
        relation_rows = [
            row
            for row in rows
            if float(row["distanz_km_mittelw"]) >= lower
            and (upper is None or float(row["distanz_km_mittelw"]) < upper)
        ]
        count = sum(as_int(row, "anzahl_befahrungen") for row in relation_rows)
        result.append(
            {
                "perspektive": perspective,
                "distanzklasse": label,
                "untere_grenze_km": lower,
                "obere_grenze_km": upper,
                "befahrungen": count,
                "anteil_prozent": round(count / total * 100, 2) if total else None,
                "relationen": len(relation_rows),
            }
        )
    return result


def cumulative_distance_class_summary(rows: list[dict[str, str]], perspective: str) -> list[dict[str, Any]]:
    """Kumulierte Anteile für die nach mittlerer Relationsdistanz sortierten Klassen."""
    summary = distance_class_summary(rows, perspective)
    cumulative = 0.0
    result = []
    for row in summary:
        cumulative += row["anteil_prozent"] or 0.0
        result.append(
            {
                **row,
                "kumulativer_anteil": round(cumulative / 100, 4),
                "kumulativer_anteil_prozent": round(cumulative, 2),
            }
        )
    return result


def threshold_300_summary(rows: list[dict[str, str]], perspective: str) -> dict[str, Any]:
    """Zeigt die Unsicherheit der 300-km-Schwelle innerhalb aggregierter Relationen."""
    def count_if(field: str) -> int:
        return sum(
            as_int(row, "anzahl_befahrungen")
            for row in rows
            if float(row[field]) >= 300
        )

    return {
        "perspektive": perspective,
        "befahrungen_insgesamt": sum(as_int(row, "anzahl_befahrungen") for row in rows),
        "befahrungen_relation_mittelwert_ab_300_km": count_if("distanz_km_mittelw"),
        "befahrungen_sicher_ab_300_km": count_if("distanz_km_min"),
        "befahrungen_potenziell_ab_300_km": count_if("distanz_km_max"),
    }


def directional_synchrony(monthly_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Beschreibt die Nähe der Richtungswerte ohne daraus Warenmengen abzuleiten."""
    source = sorted(
        (row for row in monthly_rows if row["perspektive"] == "Berlin als Quelle"),
        key=lambda row: (row["jahr"], row["monat"]),
    )
    target = sorted(
        (row for row in monthly_rows if row["perspektive"] == "Berlin als Ziel"),
        key=lambda row: (row["jahr"], row["monat"]),
    )
    source_values = [row["befahrungen"] for row in source]
    target_values = [row["befahrungen"] for row in target]
    source_mean = sum(source_values) / len(source_values)
    target_mean = sum(target_values) / len(target_values)
    numerator = sum(
        (source_value - source_mean) * (target_value - target_mean)
        for source_value, target_value in zip(source_values, target_values)
    )
    denominator = math.sqrt(
        sum((value - source_mean) ** 2 for value in source_values)
        * sum((value - target_mean) ** 2 for value in target_values)
    )
    differences = [target_value - source_value for source_value, target_value in zip(source_values, target_values)]
    relative_differences = [
        abs(target_value - source_value) / ((target_value + source_value) / 2) * 100
        for source_value, target_value in zip(source_values, target_values)
    ]
    return {
        "monatliche_korrelation": round(numerator / denominator, 6) if denominator else None,
        "durchschnittliche_absolute_monatsabweichung_prozent": round(
            sum(relative_differences) / len(relative_differences), 3
        ),
        "monatsdifferenz_min": min(differences),
        "monatsdifferenz_max": max(differences),
        "befahrungen_von_berlin_gesamt": sum(source_values),
        "befahrungen_nach_berlin_gesamt": sum(target_values),
        "differenz_gesamt": sum(target_values) - sum(source_values),
        "hinweis": (
            "Die Kennzahl vergleicht Fahrtenzahlen, nicht Warenmengen, Tonnage oder Güterarten."
        ),
    }


def top_for_period(
    rows: list[dict[str, str]],
    key_ags: str,
    key_name: str,
    exclude_ags: set[str] | None = None,
) -> dict[str, Any] | None:
    top = top_relations(rows, key_ags, key_name, limit=1, exclude_ags=exclude_ags)
    return top[0] if top else None


def main() -> None:
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
        fieldnames = handle.seek(0) or next(csv.reader(handle, delimiter=";"))

    perspectives = {
        "Berlin als Quelle": [row for row in rows if row["perspektive_berlin"] == "Berlin als Quelle"],
        "Berlin als Ziel": [row for row in rows if row["perspektive_berlin"] == "Berlin als Ziel"],
    }
    periods = sorted({period_key(row) for row in rows})
    monthly: list[dict[str, Any]] = []
    monthly_external: list[dict[str, Any]] = []
    for year, month in periods:
        for perspective, perspective_rows in perspectives.items():
            subset = [row for row in perspective_rows if period_key(row) == (year, month)]
            monthly.append(
                {
                    "periode": f"{year}-{month:02d}",
                    "zeitraum": format_period(year, month),
                    "jahr": year,
                    "monat": month,
                    "perspektive": perspective,
                    **summarize_period(subset),
                }
            )
            external_subset = [
                row
                for row in subset
                if not (
                    row["quelle_ags"] == "11000000"
                    and row["ziel_ags"] == "11000000"
                )
            ]
            monthly_external.append(
                {
                    "periode": f"{year}-{month:02d}",
                    "zeitraum": format_period(year, month),
                    "jahr": year,
                    "monat": month,
                    "perspektive": perspective,
                    **summarize_period(external_subset),
                }
            )

    first_period = periods[0]
    last_period = periods[-1]
    comparisons: list[dict[str, Any]] = []
    external_comparisons: list[dict[str, Any]] = []
    for perspective, perspective_rows in perspectives.items():
        first = [row for row in perspective_rows if period_key(row) == first_period]
        last = [row for row in perspective_rows if period_key(row) == last_period]
        first_summary = summarize_period(first)
        last_summary = summarize_period(last)
        comparisons.append(
            {
                "perspektive": perspective,
                "von": f"{first_period[0]}-{first_period[1]:02d}",
                "bis": f"{last_period[0]}-{last_period[1]:02d}",
                "befahrungen_von": first_summary["befahrungen"],
                "befahrungen_bis": last_summary["befahrungen"],
                "befahrungen_veraenderung_prozent": round(
                    (last_summary["befahrungen"] / first_summary["befahrungen"] - 1) * 100,
                    1,
                ),
                "fahrzeit_von_min": first_summary["gewichtete_fahrzeit_min"],
                "fahrzeit_bis_min": last_summary["gewichtete_fahrzeit_min"],
                "fahrzeit_veraenderung_min": round(
                    last_summary["gewichtete_fahrzeit_min"]
                    - first_summary["gewichtete_fahrzeit_min"],
                    1,
                ),
                "distanz_von_km": first_summary["gewichtete_distanz_km"],
                "distanz_bis_km": last_summary["gewichtete_distanz_km"],
                "distanz_veraenderung_km": round(
                    last_summary["gewichtete_distanz_km"]
                    - first_summary["gewichtete_distanz_km"],
                    1,
                ),
            }
        )
        first_external = [
            row
            for row in first
            if not (
                row["quelle_ags"] == "11000000"
                and row["ziel_ags"] == "11000000"
            )
        ]
        last_external = [
            row
            for row in last
            if not (
                row["quelle_ags"] == "11000000"
                and row["ziel_ags"] == "11000000"
            )
        ]
        first_external_summary = summarize_period(first_external)
        last_external_summary = summarize_period(last_external)
        external_comparisons.append(
            {
                "perspektive": perspective,
                "von": f"{first_period[0]}-{first_period[1]:02d}",
                "bis": f"{last_period[0]}-{last_period[1]:02d}",
                "befahrungen_von": first_external_summary["befahrungen"],
                "befahrungen_bis": last_external_summary["befahrungen"],
                "befahrungen_veraenderung_prozent": round(
                    (
                        last_external_summary["befahrungen"]
                        / first_external_summary["befahrungen"]
                        - 1
                    )
                    * 100,
                    1,
                ),
                "fahrzeit_von_min": first_external_summary["gewichtete_fahrzeit_min"],
                "fahrzeit_bis_min": last_external_summary["gewichtete_fahrzeit_min"],
                "fahrzeit_veraenderung_min": round(
                    last_external_summary["gewichtete_fahrzeit_min"]
                    - first_external_summary["gewichtete_fahrzeit_min"],
                    1,
                ),
                "distanz_von_km": first_external_summary["gewichtete_distanz_km"],
                "distanz_bis_km": last_external_summary["gewichtete_distanz_km"],
                "distanz_veraenderung_km": round(
                    last_external_summary["gewichtete_distanz_km"]
                    - first_external_summary["gewichtete_distanz_km"],
                    1,
                ),
            }
        )

    source_rows = perspectives["Berlin als Ziel"]
    target_rows = perspectives["Berlin als Quelle"]
    external_source_rows = [row for row in source_rows if row["quelle_ags"] != "11000000"]
    external_target_rows = [row for row in target_rows if row["ziel_ags"] != "11000000"]
    top_source_per_period = []
    top_target_per_period = []
    for year, month in periods:
        source_top = top_for_period(
            [row for row in source_rows if period_key(row) == (year, month)],
            "quelle_ags",
            "quelle_name",
            exclude_ags={"11000000"},
        )
        target_top = top_for_period(
            [row for row in target_rows if period_key(row) == (year, month)],
            "ziel_ags",
            "ziel_name",
            exclude_ags={"11000000"},
        )
        top_source_per_period.append({"periode": f"{year}-{month:02d}", **(source_top or {})})
        top_target_per_period.append({"periode": f"{year}-{month:02d}", **(target_top or {})})

    empty_values = sum(
        value in (None, "") for row in rows for value in row.values()
    )
    objectids = [row["objectid_api"] for row in rows]
    composites = [
        (row["jahr"], row["monat"], row["richtung_api"], row["quelle_ags"], row["ziel_ags"])
        for row in rows
    ]
    numeric_fields = [
        "anzahl_befahrungen",
        "fahrleistung_km",
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
    ]
    invalid_measures = sum(
        float(row[field]) < 0 for row in rows for field in numeric_fields
    )

    output = {
        "source": str(INPUT).replace("\\", "/"),
        "scope": "Berlin als Quelle oder Ziel, August 2025 bis Juli 2026",
        "quality": {
            "rows": len(rows),
            "columns": len(fieldnames),
            "periods": [f"{year}-{month:02d}" for year, month in periods],
            "empty_values": empty_values,
            "duplicate_objectids": len(objectids) - len(set(objectids)),
            "duplicate_month_direction_relations": len(composites) - len(set(composites)),
            "invalid_negative_measures": invalid_measures,
            "land_values": sorted({row["land"] for row in rows}),
        },
        "monthly": monthly,
        "monthly_external": monthly_external,
        "top_sources_to_berlin": top_relations(source_rows, "quelle_ags", "quelle_name"),
        "top_targets_from_berlin": top_relations(target_rows, "ziel_ags", "ziel_name"),
        "top_external_sources_to_berlin": top_relations(
            source_rows, "quelle_ags", "quelle_name", exclude_ags={"11000000"}
        ),
        "top_external_targets_from_berlin": top_relations(
            target_rows, "ziel_ags", "ziel_name", exclude_ags={"11000000"}
        ),
        "top_external_sources_to_berlin_mit_zeiten_distanzen": top_relations_with_route_metrics(
            source_rows, "quelle_ags", "quelle_name", exclude_ags={"11000000"}
        ),
        "top_external_targets_from_berlin_mit_zeiten_distanzen": top_relations_with_route_metrics(
            target_rows, "ziel_ags", "ziel_name", exclude_ags={"11000000"}
        ),
        "distanzklassen_extern": (
            distance_class_summary(external_target_rows, "Berlin als Quelle")
            + distance_class_summary(external_source_rows, "Berlin als Ziel")
        ),
        "kumulierte_distanzklassen_extern": (
            cumulative_distance_class_summary(external_target_rows, "Berlin als Quelle")
            + cumulative_distance_class_summary(external_source_rows, "Berlin als Ziel")
        ),
        "schwelle_300_km_extern": [
            threshold_300_summary(external_target_rows, "Berlin als Quelle"),
            threshold_300_summary(external_source_rows, "Berlin als Ziel"),
        ],
        "richtungsvergleich": {
            "alle_relationen": directional_synchrony(monthly),
            "ohne_berlin_berlin": directional_synchrony(monthly_external),
        },
        "top_source_per_period": top_source_per_period,
        "top_target_per_period": top_target_per_period,
        "start_end_comparison": comparisons,
        "start_end_comparison_external": external_comparisons,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{OUTPUT}: {len(rows)} Zeilen ausgewertet")


if __name__ == "__main__":
    main()
