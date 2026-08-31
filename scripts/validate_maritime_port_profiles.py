"""Validiert alle veröffentlichten MRTM-Hafenprofile gegen die Rohdaten.

Neben Tonnen und TEU werden Empfang, Versand, NST-7-/NST-20-Strukturen und
internationale Partnerrelationen verglichen. Fehlende Richtungsfelder werden
als Fehler behandelt, damit die Anzeige nicht auf eine Schätzlogik zurückfallen
kann.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import duckdb

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from build_maritime_port_profiles import group_7


RAW_PATTERN = str(BASE_DIR / "data" / "raw" / "MRTM OpenData" / "MRTM_OpenData_*.csv").replace("\\", "/")
BUNDLE_PATH = BASE_DIR / "data" / "processed" / "web_maritime.json"
TOLERANCE = 0.11
MIN_YEAR = 2016


def add_value(target: dict[str, float], key: str, value: float) -> None:
    target[key] = target.get(key, 0.0) + value


def assert_close(failures: list[str], label: str, actual: object, expected: float) -> None:
    if actual is None:
        failures.append(f"{label}: Richtungs- oder Kennzahlenfeld fehlt")
        return
    if abs(float(actual) - expected) > TOLERANCE:
        failures.append(f"{label}: Paket={actual}, Rohdaten={expected}")


def main() -> None:
    bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
    published_ports = {
        (str(year), port_code): record
        for year, ports in bundle.get("seaports", {}).items()
        for port_code, record in ports.items()
    }
    if not published_ports:
        raise AssertionError("Keine veröffentlichten Hafenprofile im Datenpaket gefunden.")

    connection = duckdb.connect()
    rows = connection.execute(
        f"""
        WITH raw AS MATERIALIZED (
            SELECT *
            FROM read_csv('{RAW_PATTERN}', delim=';', header=true, all_varchar=true,
                          quote='"', sample_size=-1, union_by_name=true)
            WHERE CAST(Referenzzeitraum_Jahr AS INTEGER) >= {MIN_YEAR}
              AND (Ausladeregion_ISO = 'DE' OR Einladeregion_ISO = 'DE')
        ), movements AS (
            SELECT CAST(Referenzzeitraum_Jahr AS INTEGER) AS year,
                   Ausladeregion_UNLOCODE AS port_code,
                   Einladeregion_ISO AS partner_iso,
                   Einladeregion_ISO_Label AS partner_name,
                   NST2007 AS nst_raw,
                   TRY_CAST(REPLACE(Guetergewicht, ',', '.') AS DOUBLE) AS tonnes,
                   TRY_CAST(REPLACE(TEU, ',', '.') AS DOUBLE) AS teu,
                   'inbound' AS direction
            FROM raw WHERE Ausladeregion_ISO = 'DE'
            UNION ALL
            SELECT CAST(Referenzzeitraum_Jahr AS INTEGER) AS year,
                   Einladeregion_UNLOCODE AS port_code,
                   Ausladeregion_ISO AS partner_iso,
                   Ausladeregion_ISO_Label AS partner_name,
                   NST2007 AS nst_raw,
                   TRY_CAST(REPLACE(Guetergewicht, ',', '.') AS DOUBLE) AS tonnes,
                   TRY_CAST(REPLACE(TEU, ',', '.') AS DOUBLE) AS teu,
                   'outbound' AS direction
            FROM raw WHERE Einladeregion_ISO = 'DE'
        )
        SELECT year, port_code, partner_iso, partner_name, nst_raw, direction,
               SUM(COALESCE(tonnes, 0)) AS tonnes,
               SUM(COALESCE(teu, 0)) AS teu
        FROM movements
        GROUP BY ALL
        """
    ).fetchall()
    connection.close()

    profiles = defaultdict(lambda: {
        "tonnes": 0.0,
        "inbound_tonnes": 0.0,
        "outbound_tonnes": 0.0,
        "teu": 0.0,
        "inbound_teu": 0.0,
        "outbound_teu": 0.0,
        "groups": defaultdict(lambda: defaultdict(float)),
        "divisions": defaultdict(lambda: defaultdict(float)),
    })
    partners = defaultdict(
        lambda: defaultdict(
            lambda: {
                "tonnes": 0.0,
                "inbound_tonnes": 0.0,
                "outbound_tonnes": 0.0,
                "groups_7": defaultdict(float),
                "groups_7_inbound": defaultdict(float),
                "groups_7_outbound": defaultdict(float),
            }
        )
    )

    for year, port_code, partner_iso, partner_name, nst_raw, direction, tonnes, teu in rows:
        key = (str(year), port_code)
        if key not in published_ports:
            continue
        value = float(tonnes or 0.0)
        teu_value = float(teu or 0.0)
        group, division = group_7(nst_raw)
        profile = profiles[key]
        profile["tonnes"] += value
        profile["teu"] += teu_value
        profile[f"{direction}_tonnes"] += value
        profile[f"{direction}_teu"] += teu_value
        profile["groups"][group]["tonnes"] += value
        profile["groups"][group][direction] += value
        profile["groups"][group]["teu"] += teu_value
        profile["groups"][group][f"{direction}_teu"] += teu_value
        profile["divisions"][division]["tonnes"] += value
        profile["divisions"][division][direction] += value
        profile["divisions"][division]["teu"] += teu_value
        profile["divisions"][division][f"{direction}_teu"] += teu_value

        if partner_iso and partner_iso != "DE" and partner_name:
            partner = partners[key][(partner_iso, partner_name)]
            partner["tonnes"] += value
            partner[f"{direction}_tonnes"] += value
            partner["groups_7"][group] += value
            partner[f"groups_7_{direction}"][group] += value

    # Der Erzeuger schreibt für jede vorhandene Gütergruppe beide
    # Richtungsfelder aus. Fehlt in einer Richtung ein Wert, muss er daher
    # explizit als 0 vorliegen und nicht als fehlender Schlüssel.
    for port_partners in partners.values():
        for partner in port_partners.values():
            for group in partner["groups_7"]:
                partner["groups_7_inbound"].setdefault(group, 0.0)
                partner["groups_7_outbound"].setdefault(group, 0.0)

    failures: list[str] = []
    compared_profiles = 0
    compared_partners = 0
    for key, actual in published_ports.items():
        expected = profiles.get(key)
        label = f"{key[0]} {key[1]}"
        if expected is None:
            failures.append(f"{label}: veröffentlichter Hafen kommt in den Rohdaten nicht vor")
            continue
        compared_profiles += 1
        for field in ("tonnes", "inbound_tonnes", "outbound_tonnes", "teu", "inbound_teu", "outbound_teu"):
            assert_close(failures, f"{label} {field}", actual.get(field), expected[field])

        for level, field, required_fields in (
            ("NST-7", "by_group", ("tonnes", "inbound", "outbound", "teu", "inbound_teu", "outbound_teu")),
            ("NST-20", "by_division", ("tonnes", "inbound", "outbound", "teu", "inbound_teu", "outbound_teu")),
        ):
            actual_buckets = actual.get(field, {})
            expected_buckets = expected["groups" if field == "by_group" else "divisions"]
            if set(actual_buckets) != set(expected_buckets):
                failures.append(f"{label} {level}: Schlüssel unterscheiden sich zwischen Paket und Rohdaten")
            for bucket_key, expected_values in expected_buckets.items():
                actual_values = actual_buckets.get(bucket_key, {})
                for value_field in required_fields:
                    assert_close(
                        failures,
                        f"{label} {level} {bucket_key} {value_field}",
                        actual_values.get(value_field),
                        expected_values[value_field],
                    )

        actual_partners = {
            (entry.get("iso"), entry.get("name")): entry
            for entry in actual.get("partner_countries", [])
        }
        expected_partners = partners.get(key, {})
        if set(actual_partners) != set(expected_partners):
            failures.append(f"{label} Partner: Schlüssel unterscheiden sich zwischen Paket und Rohdaten")
        for partner_key, expected_values in expected_partners.items():
            actual_values = actual_partners.get(partner_key, {})
            compared_partners += 1
            partner_label = f"{label} Partner {partner_key[0]} {partner_key[1]}"
            for field in ("tonnes", "inbound_tonnes", "outbound_tonnes"):
                assert_close(failures, f"{partner_label} {field}", actual_values.get(field), expected_values[field])
            for field in ("groups_7", "groups_7_inbound", "groups_7_outbound"):
                if set(actual_values.get(field, {})) != set(expected_values[field]):
                    failures.append(f"{partner_label} {field}: Gütergruppenschlüssel unterscheiden sich")
                for group, expected_value in expected_values[field].items():
                    assert_close(failures, f"{partner_label} {field} {group}", actual_values.get(field, {}).get(group), expected_value)

    if failures:
        raise AssertionError("\n".join(failures))
    print(
        "BESTANDEN: "
        f"{compared_profiles} Hafenprofile, {compared_partners} Partnerrelationen sowie "
        "alle Richtungs-, TEU- und NST-Felder stimmen mit den Rohdaten; "
        "keine 58/42-Schätzung wäre erforderlich."
    )


if __name__ == "__main__":
    main()
