"""Vergleicht das Seeverkehrs-Webpaket mit der vollständig gelesenen Rohdatei."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb


BASE_DIR = Path(__file__).resolve().parents[2]
RAW_PATTERN = str(BASE_DIR / "data" / "raw" / "MRTM OpenData" / "MRTM_OpenData_*.csv").replace("\\", "/")
BUNDLE_PATH = BASE_DIR / "data" / "processed" / "web_maritime.json"
MIN_YEAR = 2016


def main() -> None:
    bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
    connection = duckdb.connect()
    rows = connection.execute(
        f"""
        SELECT CAST(Referenzzeitraum_Jahr AS INTEGER) AS year,
               SUM(TRY_CAST(REPLACE(Guetergewicht, ',', '.') AS DOUBLE))
                   FILTER (WHERE Ausladeregion_ISO = 'DE') AS inbound_tonnes,
               SUM(TRY_CAST(REPLACE(Guetergewicht, ',', '.') AS DOUBLE))
                   FILTER (WHERE Einladeregion_ISO = 'DE') AS outbound_tonnes,
               SUM(TRY_CAST(REPLACE(TEU, ',', '.') AS DOUBLE))
                   FILTER (WHERE Ausladeregion_ISO = 'DE') AS inbound_teu,
               SUM(TRY_CAST(REPLACE(TEU, ',', '.') AS DOUBLE))
                   FILTER (WHERE Einladeregion_ISO = 'DE') AS outbound_teu
        FROM read_csv('{RAW_PATTERN}', delim=';', header=true, all_varchar=true,
                      quote='"', sample_size=-1, union_by_name=true)
        WHERE CAST(Referenzzeitraum_Jahr AS INTEGER) >= {MIN_YEAR}
        GROUP BY year ORDER BY year
        """
    ).fetchall()
    connection.close()

    failures: list[str] = []
    for year, inbound_tonnes, outbound_tonnes, inbound_teu, outbound_teu in rows:
        actual = bundle["national"][str(year)]
        expected = {
            "inbound_tonnes": float(inbound_tonnes or 0),
            "outbound_tonnes": float(outbound_tonnes or 0),
            "tonnes": float((inbound_tonnes or 0) + (outbound_tonnes or 0)),
            "inbound_teu": float(inbound_teu or 0),
            "outbound_teu": float(outbound_teu or 0),
            "teu": float((inbound_teu or 0) + (outbound_teu or 0)),
        }
        for key, expected_value in expected.items():
            if abs(float(actual[key]) - expected_value) > 0.11:
                failures.append(f"{year} {key}: Paket={actual[key]}, Rohdaten={expected_value}")

        division_keys = set(actual.get("by_division", {}))
        if any(len(key) != 2 or not key.isdigit() for key in division_keys):
            failures.append(f"{year}: ungültige NST-2007-Abteilungsschlüssel {sorted(division_keys)}")
        group_sum = sum(float(values.get("tonnes", 0)) for values in actual.get("by_group", {}).values())
        # Sieben auf eine Nachkommastelle gerundete Gruppen können zusammen
        # um wenige Zehnteltonnen von der ungerundeten Randsumme abweichen.
        if abs(group_sum - expected["tonnes"]) > 0.5:
            failures.append(f"{year}: Gütergruppensumme={group_sum}, Gesamt={expected['tonnes']}")

    if failures:
        raise AssertionError("\n".join(failures))
    print(f"BESTANDEN: {len(rows)} Berichtsjahre, nationale Tonnen-/TEU-Randsummen und NST-Schlüssel stimmen.")


if __name__ == "__main__":
    main()
