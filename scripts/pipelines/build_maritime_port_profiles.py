"""Ergänzt die Webdaten um fachliche Profile je deutschem Seehafen.

Die bestehende Webdatei enthält bereits Lage, Umschlag und TEU der kartierten
Häfen. Dieses Skript ergänzt daraus ableitbare Güterstrukturen, Empfang/Versand
und internationale Partnerländer aus den vorhandenen Destatis-Rohdateien
(EVAS 46331). Es verändert keine anderen Webartefakte.
"""

from __future__ import annotations

import glob
import json
from collections import defaultdict
from pathlib import Path

import duckdb


BASE_DIR = Path(__file__).resolve().parents[2]
RAW_PATTERN = str(BASE_DIR / "data" / "raw" / "MRTM OpenData" / "MRTM_OpenData_*.csv").replace("\\", "/")
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "web_maritime.json"
NATIONAL_KEY = "__NATIONAL__"
MIN_YEAR = 2016


def group_7(nst_raw: object) -> tuple[str, str]:
    """Ordnet NST-2007-Code der amtlichen C1-C7- und 20er-Ebene zu."""
    nst_str = str(nst_raw or "").strip()
    if not nst_str:
        return "7", "20"
    division = nst_str.zfill(3)[:2] if len(nst_str) == 3 else nst_str.zfill(2)
    division_number = int(division) if division.isdigit() else 20
    division_key = f"{division_number:02d}"
    if division_number in [1, 2, 3]:
        return "1", division_key
    if division_number in [4, 5, 6]:
        return "2", division_key
    if division_number in [7, 8, 9]:
        return "3", division_key
    if division_number == 10:
        return "4", division_key
    if division_number in [11, 12, 13]:
        return "5", division_key
    if division_number == 14:
        return "6", division_key
    return "7", division_key


def add_value(target: dict[str, float], key: str, value: float) -> None:
    target[key] = target.get(key, 0.0) + value


def main() -> None:
    bundle = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    seaports = bundle.get("seaports", {})

    con = duckdb.connect()
    con.execute(
        f"""
        CREATE TEMP TABLE mrtm_profile_raw AS
        SELECT *
        FROM read_csv('{RAW_PATTERN}', delim=';', header=true, all_varchar=true,
                      quote='"', sample_size=-1, union_by_name=true)
        WHERE CAST(Referenzzeitraum_Jahr AS INTEGER) >= {MIN_YEAR}
          AND (Ausladeregion_ISO = 'DE' OR Einladeregion_ISO = 'DE')
        """
    )
    rows = con.execute(
        """
        SELECT CAST(Referenzzeitraum_Jahr AS INTEGER) AS year,
               Ausladeregion_UNLOCODE AS port_code,
               Einladeregion_ISO AS partner_iso,
               Einladeregion_ISO_Label AS partner_name,
               NST2007 AS nst_raw,
               TRY_CAST(REPLACE(Guetergewicht, ',', '.') AS DOUBLE) AS tonnes,
               TRY_CAST(REPLACE(TEU, ',', '.') AS DOUBLE) AS teu,
               TRY_CAST(Anzahl_Ladungstraeger AS BIGINT) AS units,
               'inbound' AS port_direction
        FROM mrtm_profile_raw WHERE Ausladeregion_ISO = 'DE'
        UNION ALL
        SELECT CAST(Referenzzeitraum_Jahr AS INTEGER) AS year,
               Einladeregion_UNLOCODE AS port_code,
               Ausladeregion_ISO AS partner_iso,
               Ausladeregion_ISO_Label AS partner_name,
               NST2007 AS nst_raw,
               TRY_CAST(REPLACE(Guetergewicht, ',', '.') AS DOUBLE) AS tonnes,
               TRY_CAST(REPLACE(TEU, ',', '.') AS DOUBLE) AS teu,
               TRY_CAST(Anzahl_Ladungstraeger AS BIGINT) AS units,
               'outbound' AS port_direction
        FROM mrtm_profile_raw WHERE Einladeregion_ISO = 'DE'
        """
    ).fetchall()
    con.close()

    profile = defaultdict(lambda: {
        "tonnes": 0.0,
        "inbound_tonnes": 0.0,
        "outbound_tonnes": 0.0,
        "teu": 0.0,
        "inbound_teu": 0.0,
        "outbound_teu": 0.0,
        "units": 0,
        "groups": defaultdict(lambda: {
            "tonnes": 0.0, "inbound": 0.0, "outbound": 0.0,
            "teu": 0.0, "inbound_teu": 0.0, "outbound_teu": 0.0,
        }),
        "divisions": defaultdict(lambda: {
            "tonnes": 0.0, "inbound": 0.0, "outbound": 0.0,
            "teu": 0.0, "inbound_teu": 0.0, "outbound_teu": 0.0,
        }),
    })
    partners = defaultdict(lambda: defaultdict(lambda: {
        "tonnes": 0.0,
        "inbound_tonnes": 0.0,
        "outbound_tonnes": 0.0,
        "groups": defaultdict(float),
        "groups_inbound": defaultdict(float),
        "groups_outbound": defaultdict(float),
    }))

    for year, port_code, partner_iso, partner_name, nst_raw, tonnes, teu, units, port_direction in rows:
        year_key = str(year)
        value = float(tonnes or 0.0)
        teu_value = float(teu or 0.0)
        units_value = int(units or 0)
        inbound_value = value if port_direction == "inbound" else 0.0
        outbound_value = value if port_direction == "outbound" else 0.0
        group, division = group_7(nst_raw)
        targets = [(year_key, NATIONAL_KEY)]
        if port_code in seaports.get(year_key, {}):
            targets.append((year_key, port_code))

        for profile_key in targets:
            port = profile[profile_key]
            port["tonnes"] += value
            port["inbound_tonnes"] += inbound_value
            port["outbound_tonnes"] += outbound_value
            port["teu"] += teu_value
            # TEU are stored on the same directional raw-data row as the
            # tonnage.  Preserve the separation rather than applying a
            # proportional split in the browser.
            if port_direction == "inbound":
                port["inbound_teu"] += teu_value
            if port_direction == "outbound":
                port["outbound_teu"] += teu_value
            port["units"] += units_value
            port["groups"][group]["tonnes"] += value
            port["groups"][group]["inbound"] += inbound_value
            port["groups"][group]["outbound"] += outbound_value
            port["groups"][group]["teu"] += teu_value
            if port_direction == "inbound":
                port["groups"][group]["inbound_teu"] += teu_value
            if port_direction == "outbound":
                port["groups"][group]["outbound_teu"] += teu_value
            port["divisions"][division]["tonnes"] += value
            port["divisions"][division]["inbound"] += inbound_value
            port["divisions"][division]["outbound"] += outbound_value
            port["divisions"][division]["teu"] += teu_value
            if port_direction == "inbound":
                port["divisions"][division]["inbound_teu"] += teu_value
            if port_direction == "outbound":
                port["divisions"][division]["outbound_teu"] += teu_value

            if partner_iso and partner_iso != "DE" and partner_name:
                partner = partners[profile_key][(partner_iso, partner_name)]
                partner["tonnes"] += value
                partner["inbound_tonnes"] += inbound_value
                partner["outbound_tonnes"] += outbound_value
                partner["groups"][group] += value
                partner["groups_inbound"][group] += inbound_value
                partner["groups_outbound"][group] += outbound_value

    def build_profile_record(values: dict, *, name: str, include_location: bool = False) -> dict:
        record = {
            "name": name,
            "tonnes": round(values["tonnes"], 1),
            "inbound_tonnes": round(values["inbound_tonnes"], 1),
            "outbound_tonnes": round(values["outbound_tonnes"], 1),
            "teu": round(values["teu"], 1),
            "inbound_teu": round(values["inbound_teu"], 1),
            "outbound_teu": round(values["outbound_teu"], 1),
            "units": values["units"],
            "by_group": {
                group: {key: round(amount, 1) for key, amount in group_values.items()}
                for group, group_values in values["groups"].items()
            },
            "by_division": {
                division: {key: round(amount, 1) for key, amount in division_values.items()}
                for division, division_values in values["divisions"].items()
            },
            "commodities": {
                "groups_7": {group: round(group_values["tonnes"], 1) for group, group_values in values["groups"].items()},
                "divisions_20": {division: round(division_values["tonnes"], 1) for division, division_values in values["divisions"].items()},
            },
            "partner_countries": [],
        }
        return record

    national = {}
    for (year_key, port_code), values in profile.items():
        if port_code == NATIONAL_KEY:
            national[year_key] = build_profile_record(values, name="Deutschland Gesamt")
            target = national[year_key]
        else:
            port = seaports[year_key][port_code]
            target = build_profile_record(values, name=port.get("name", port_code))
            port.update({key: value for key, value in target.items() if key not in {"name", "teu", "units"}})

        for (iso, name), partner_values in partners[(year_key, port_code)].items():
            target["partner_countries"].append({
                "iso": iso,
                "name": name,
                "tonnes": round(partner_values["tonnes"], 1),
                "inbound_tonnes": round(partner_values["inbound_tonnes"], 1),
                "outbound_tonnes": round(partner_values["outbound_tonnes"], 1),
                "groups_7": {group: round(amount, 1) for group, amount in partner_values["groups"].items()},
                "groups_7_inbound": {group: round(amount, 1) for group, amount in partner_values["groups_inbound"].items()},
                "groups_7_outbound": {group: round(amount, 1) for group, amount in partner_values["groups_outbound"].items()},
            })
        target["partner_countries"].sort(key=lambda item: item["tonnes"], reverse=True)

    bundle["national"] = national

    OUTPUT_PATH.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated port profiles in {OUTPUT_PATH.relative_to(BASE_DIR)}.")


if __name__ == "__main__":
    main()
