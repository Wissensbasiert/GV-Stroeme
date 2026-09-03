#!/usr/bin/env python3
"""Recalculate selected VP2040 browser values directly from the raw matrices.

The script deliberately reads the source CSV files again instead of reusing the
ETL result.  It verifies national totals, three NUTS-3 examples and selected
relation values for both published VP2040 scenarios.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import pandas as pd
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = ROOT / "data" / "raw" / "VP2040"
OUTPUT = ROOT / "data" / "processed" / "web_forecast_2040.json"
NST_REFERENCE_PDF = ROOT / "data" / "raw" / "Straße" / "KBA" / "Empfang_VD3cE_NUTS2_20Gueter" / "nsz-2007.pdf"
CROSSWALK_CSV = ROOT / "data" / "crosswalks" / "crosswalk_nst_vp2040.csv"
# Neben zwei allgemeinen Beispielen werden die durch die korrigierte
# Sonderzellenzuordnung besonders betroffenen Kreise dauerhaft geprüft.
CHECK_REGIONS = ("DE600", "DE300", "DE501", "DE502", "DE949", "DE942")
CHECK_GROUP = "1"
# Regression: Brunsbüttel (DEF05) is a VP2040 special cell.  The 2019
# relation comparison must use the same special-cell-to-NUTS mapping as the
# scenario aggregation; otherwise its growth for Hamburg is overstated.
REGRESSION_RELATION_CHECKS = (("DE600", "inbound", "DEF05", "3"),)
MODES = {
    "road": "Strasse",
    "rail": "Bahn",
    "iww": "Bischi",
}
SCENARIOS = {
    "2019_BASE": ("VP2040_2019_GV_NUTS3", "2019"),
    "2040_P1": ("VP2040_2040P1BP_GV_NUTS3", "2040P1BP"),
}

# Die VP2040-Dateien haben 25 Original-Gütergruppen. Die Tabelle ist der
# fachliche Vertrag für ihre Zusammenfassung auf die sieben amtlichen
# NST-2007-C-Gruppen (C1–C7), die das KBA als Gueterposition_7 verwendet.
# Entscheidend ist die Abteilung, nicht eine branchenlogische Neuordnung:
# C1 umfasst die Abteilungen 01 bis 03 einschließlich Kohle sowie Erze und
# Steine/Erden.
EXPECTED_VP2040_GROUP7 = {
    10: "1", 21: "1", 22: "1", 23: "1", 31: "1", 32: "3", 33: "1",
    40: "2", 50: "2", 60: "2", 71: "3", 72: "3", 80: "3", 90: "3",
    100: "4", 110: "5", 120: "5", 130: "5", 140: "6", 150: "7",
    160: "7", 170: "7", 180: "7", 190: "7", 200: "7",
}
EXPECTED_VP2040_DIVISION = {
    10: "01", 21: "02", 22: "02", 23: "02", 31: "03", 32: "08", 33: "03",
    40: "04", 50: "05", 60: "06", 71: "07", 72: "07", 80: "08", 90: "09",
    100: "10", 110: "11", 120: "12", 130: "13", 140: "14", 150: "15",
    160: "16", 170: "17", 180: "18", 190: "19", 200: "20",
}
EXPECTED_GROUP_BY_DIVISION = {
    **{f"{division:02d}": "1" for division in range(1, 4)},
    **{f"{division:02d}": "2" for division in range(4, 7)},
    **{f"{division:02d}": "3" for division in range(7, 10)},
    "10": "4",
    **{f"{division:02d}": "5" for division in range(11, 14)},
    "14": "6",
    **{f"{division:02d}": "7" for division in range(15, 21)},
}
EXPECTED_GROUP7_NAMES = {
    "1": "Erzeugnisse der Land- und Forstwirtschaft, Rohstoffe",
    "2": "Konsumgüter zum kurzfristigen Verbrauch, Holzwaren",
    "3": "Mineralische, chemische und Mineralölerzeugnisse",
    "4": "Metalle und Metallerzeugnisse",
    "5": "Maschinen und Ausrüstungen, langlebige Konsumgüter",
    "6": "Sekundärrohstoffe, Abfälle",
    "7": "Sonstige Produkte",
}
VP2040_LABEL_TOKENS = {
    10: "land", 21: "steinkohle", 22: "braunkohle", 23: "erdol", 31: "erz",
    32: "dungemittel", 33: "steine", 40: "nahrungs", 50: "textilien", 60: "holz",
    71: "koks", 72: "mineralol", 80: "chemische", 90: "mineralerzeugnisse",
    100: "metalle", 110: "maschinen", 120: "fahrzeuge", 130: "mobel",
    140: "sekundarrohstoffe", 150: "post", 160: "material", 170: "umzugsgut",
    180: "sammelgut", 190: "unbekannt", 200: "sonstige",
}


def normalized_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]", "", value)


def assert_close(label: str, actual: float, expected: float, tolerance: float = 0.11) -> None:
    if abs(actual - expected) > tolerance:
        raise AssertionError(f"{label}: dashboard={actual}, raw={expected}")


def percentage_change(value: float, base_value: float | None) -> float | None:
    if base_value is None or abs(base_value) < 1e-9:
        return None
    return round((value - base_value) / abs(base_value) * 100, 1)


def load_cell_targets() -> dict[int, str]:
    with (ROOT / "data" / "crosswalks" / "crosswalk_spatial_vp2040.json").open(encoding="utf-8") as handle:
        crosswalk = json.load(handle)

    ags_to_nuts = {
        str(item["ags_5stellig"]): item.get("nuts3_2024") or item.get("nuts3_2016")
        for item in crosswalk
        if item.get("ags_5stellig") and (item.get("nuts3_2024") or item.get("nuts3_2016"))
    }
    with (ROOT / "data" / "crosswalks" / "vp2040_special_cells_nuts3.json").open(encoding="utf-8") as handle:
        special_cells = {
            int(cell_id): metadata["nuts3_2024"]
            for cell_id, metadata in json.load(handle)["cells"].items()
        }
    result: dict[int, str] = {}
    for item in crosswalk:
        cell_id = int(item["cell_id"])
        if item["country_iso2"] != "DE":
            result[cell_id] = str(cell_id)
            continue

        nuts_id = item.get("nuts3_2024") or item.get("nuts3_2016")
        if not nuts_id:
            nuts_id = special_cells.get(cell_id)
        if not nuts_id:
            cell_text = str(cell_id)
            if len(cell_text) == 7 and cell_text.endswith("00"):
                nuts_id = ags_to_nuts.get(cell_text[:5])
        result[cell_id] = nuts_id or str(cell_id)
    return result


def load_group_lookup() -> dict[int, str]:
    with (ROOT / "data" / "crosswalks" / "crosswalk_nst_vp2040.json").open(encoding="utf-8") as handle:
        crosswalk = json.load(handle)
    codes = [int(item["vp40_code"]) for item in crosswalk]
    if len(crosswalk) != 25 or len(set(codes)) != len(codes):
        raise AssertionError("Der VP2040-JSON-Crosswalk muss genau 25 eindeutige Originalcodes enthalten.")
    lookup = {int(item["vp40_code"]): str(item["nst2007_group7"]) for item in crosswalk}
    if lookup != EXPECTED_VP2040_GROUP7:
        raise AssertionError(
            "Der VP2040-Güterschlüssel weicht von der verbindlichen NST-7-Zuordnung ab."
        )
    divisions = {int(item["vp40_code"]): str(item["nst2007_division"]) for item in crosswalk}
    if divisions != EXPECTED_VP2040_DIVISION:
        raise AssertionError(
            "Der VP2040-Güterschlüssel weicht bei den NST-2007-Abteilungen von der amtlichen C1-C7-Zuordnung ab."
        )
    if any(lookup[code] != EXPECTED_GROUP_BY_DIVISION[divisions[code]] for code in lookup):
        raise AssertionError(
            "Mindestens eine VP2040-Position ist nicht gemäß ihrer NST-2007-Abteilung auf C1–C7 abgebildet."
        )
    group_names = {
        str(item["nst2007_group7"]): str(item["nst2007_group7_name"])
        for item in crosswalk
    }
    if group_names != EXPECTED_GROUP7_NAMES:
        raise AssertionError("Die Bezeichnungen der sieben amtlichen NST-2007-C-Gruppen weichen ab.")
    with CROSSWALK_CSV.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle, delimiter=";"))
    csv_codes = [int(item["vp40_code"]) for item in csv_rows]
    if len(csv_rows) != 25 or len(set(csv_codes)) != len(csv_codes):
        raise AssertionError("Der VP2040-CSV-Crosswalk muss genau 25 eindeutige Originalcodes enthalten.")
    csv_lookup = {int(item["vp40_code"]): str(item["nst2007_group7"]) for item in csv_rows}
    csv_divisions = {int(item["vp40_code"]): str(item["nst2007_division"]) for item in csv_rows}
    if csv_lookup != lookup or csv_divisions != divisions:
        raise AssertionError(
            "Die CSV- und JSON-Fassung des VP2040-Güterschlüssels sind nicht identisch."
        )
    semantic_fields = (
        "vp40_code", "vp40_name", "nst2007_division", "nst2007_division_name",
        "nst2007_group7", "nst2007_group7_name",
    )
    json_by_code = {int(item["vp40_code"]): item for item in crosswalk}
    csv_by_code = {int(item["vp40_code"]): item for item in csv_rows}
    differing_fields = [
        f"{code}:{field}"
        for code in sorted(json_by_code)
        for field in semantic_fields
        if str(json_by_code[code][field]) != str(csv_by_code[code][field])
    ]
    if differing_fields:
        raise AssertionError(
            "CSV- und JSON-Crosswalk weichen in fachlichen Feldern ab: "
            + ", ".join(differing_fields)
        )

    for folder, _prefix in SCENARIOS.values():
        source_list = RAW_ROOT / folder / "nst2007.csv"
        source = pd.read_csv(source_list, sep=";", encoding="latin1")
        source_codes = set(source["NST 2007"].astype(int))
        if source_codes != set(lookup):
            raise AssertionError(
                f"{source_list.name} in {folder} enthält nicht genau die 25 Crosswalk-Codes."
            )
        source_labels = dict(zip(source["NST 2007"].astype(int), source["Bezeichnung"].astype(str)))
        crosswalk_labels = {int(item["vp40_code"]): str(item["vp40_name"]) for item in crosswalk}
        for code, token in VP2040_LABEL_TOKENS.items():
            if token not in normalized_text(source_labels[code]) or token not in normalized_text(crosswalk_labels[code]):
                raise AssertionError(
                    f"VP2040-Güterbegriff für Code {code} stimmt zwischen nst2007.csv und Crosswalk nicht überein."
                )
    pdf_text = normalized_text(" ".join(page.extract_text() or "" for page in PdfReader(NST_REFERENCE_PDF).pages))
    missing_pdf_terms = [token for token in VP2040_LABEL_TOKENS.values() if token not in pdf_text]
    if missing_pdf_terms:
        raise AssertionError(
            "Die NST-2007-Referenz-PDF enthält nicht alle erwarteten Güterbegriffe: "
            + ", ".join(sorted(missing_pdf_terms))
        )
    return lookup


def find_relation_checks(bundle: dict) -> list[tuple[str, str, str, str]]:
    """Choose tonnes and tonne-kilometre relation candidates dynamically.

    The bundle retains the union of both Top-X rankings.  Selecting one row
    for each measure guards against a regression to tonnes-only preselection.
    """
    rows: list[tuple[str, str, str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    regions = bundle["scenarios"]["2040_P1"]["regions"]
    for group in ("ALL", *map(str, range(1, 8))):
        for direction in ("all", "outbound", "inbound"):
            for region_id in CHECK_REGIONS:
                relation_rows = (
                    regions[region_id]["relations_overall"][direction]
                    if group == "ALL"
                    else regions[region_id]["by_group_relations"][group][direction]
                )
                if not relation_rows:
                    continue
                for metric in ("tonnes", "tkm"):
                    row = max(relation_rows, key=lambda item: float(item.get(metric, 0) or 0))
                    item = (region_id, direction, row["partner_id"], group)
                    if item not in seen:
                        seen.add(item)
                        rows.append(item)
                break
    if rows:
        forecast_regions = bundle["scenarios"]["2040_P1"]["regions"]
        for region_id, direction, partner_id, group in REGRESSION_RELATION_CHECKS:
            relation_rows = forecast_regions[region_id]["by_group_relations"][group][direction]
            if any(item["partner_id"] == partner_id for item in relation_rows):
                item = (region_id, direction, partner_id, group)
                if item not in seen:
                    rows.append(item)
        return rows
    raise AssertionError("Keine geeigneten Relationseinträge im 2040-Dashboard gefunden.")


def empty_region_values() -> dict:
    return {
        "directions": {"tonnes": defaultdict(float), "tkm": defaultdict(float)},
        "modes": {
            metric: {mode: defaultdict(float) for mode in MODES}
            for metric in ("tonnes", "tkm")
        },
        "group_modes": {
            metric: {mode: defaultdict(float) for mode in MODES}
            for metric in ("tonnes", "tkm")
        },
    }


def collect_raw_values(
    cell_targets: dict[int, str],
    group_lookup: dict[int, str],
    relation_checks: list[tuple[str, str, str, str]],
) -> dict:
    result = {}
    for scenario_id, (folder, prefix) in SCENARIOS.items():
        national = {"tonnes": 0.0, "tkm": 0.0}
        national_modes = {
            metric: {mode: 0.0 for mode in MODES}
            for metric in ("tonnes", "tkm")
        }
        national_group_modes = {
            metric: {mode: 0.0 for mode in MODES}
            for metric in ("tonnes", "tkm")
        }
        regional = {region_id: empty_region_values() for region_id in CHECK_REGIONS}
        relations = {
            (region_id, direction, partner_id, group): {"tonnes": 0.0, "tkm": 0.0}
            for region_id, direction, partner_id, group in relation_checks
        }

        for mode, suffix in MODES.items():
            matrix = RAW_ROOT / folder / f"VP2040_{prefix}_GV_{suffix}_NUTS3_Matrix_V01.csv"
            for chunk in pd.read_csv(
                matrix,
                sep=";",
                encoding="latin1",
                usecols=["Quellzelle", "Zielzelle", "Guetergruppe", "Tonnen", "Tkm"],
                chunksize=100_000,
            ):
                chunk["origin"] = chunk["Quellzelle"].map(cell_targets).fillna(chunk["Quellzelle"].astype(str))
                chunk["destination"] = chunk["Zielzelle"].map(cell_targets).fillna(chunk["Zielzelle"].astype(str))
                chunk["g7"] = chunk["Guetergruppe"].map(group_lookup).fillna("7")
                chunk["is_binnen"] = chunk["origin"] == chunk["destination"]
                for metric, source_column in (("tonnes", "Tonnen"), ("tkm", "Tkm")):
                    national[metric] += float(chunk[source_column].sum())
                    national_modes[metric][mode] += float(chunk[source_column].sum())
                    national_group_modes[metric][mode] += float(
                        chunk.loc[chunk["g7"].eq(CHECK_GROUP), source_column].sum()
                    )

                    for region_id, region_values in regional.items():
                        outbound = chunk["origin"].eq(region_id) & ~chunk["is_binnen"]
                        inbound = chunk["destination"].eq(region_id) & ~chunk["is_binnen"]
                        binnen = chunk["origin"].eq(region_id) & chunk["is_binnen"]
                        region_values["directions"][metric]["outbound"] += float(chunk.loc[outbound, source_column].sum())
                        region_values["directions"][metric]["inbound"] += float(chunk.loc[inbound, source_column].sum())
                        region_values["directions"][metric]["binnen"] += float(chunk.loc[binnen, source_column].sum())
                        region_values["modes"][metric][mode]["all"] += float(chunk.loc[outbound | inbound | binnen, source_column].sum())
                        group_mask = chunk["g7"].eq(CHECK_GROUP)
                        region_values["group_modes"][metric][mode]["outbound"] += float(
                            chunk.loc[outbound & group_mask, source_column].sum()
                        )
                        region_values["group_modes"][metric][mode]["inbound"] += float(
                            chunk.loc[inbound & group_mask, source_column].sum()
                        )
                        region_values["group_modes"][metric][mode]["binnen"] += float(
                            chunk.loc[binnen & group_mask, source_column].sum()
                        )

                    for region_id, direction, partner_id, group in relation_checks:
                        if direction == "all":
                            relation_mask = (
                                (chunk["origin"].eq(region_id) & chunk["destination"].eq(partner_id))
                                | (chunk["origin"].eq(partner_id) & chunk["destination"].eq(region_id))
                            )
                        elif direction == "outbound":
                            relation_mask = chunk["origin"].eq(region_id) & chunk["destination"].eq(partner_id)
                        else:
                            relation_mask = chunk["destination"].eq(region_id) & chunk["origin"].eq(partner_id)
                        if group != "ALL":
                            relation_mask &= chunk["g7"].eq(group)
                        relations[(region_id, direction, partner_id, group)][metric] += float(
                            chunk.loc[relation_mask, source_column].sum()
                        )

        for region_values in regional.values():
            for metric in ("tonnes", "tkm"):
                directions = region_values["directions"][metric]
                directions["all"] = directions["outbound"] + directions["inbound"] + directions["binnen"]
                directions["balance"] = directions["outbound"] - directions["inbound"]
                for mode in MODES:
                    group_modes = region_values["group_modes"][metric][mode]
                    group_modes["all"] = group_modes["outbound"] + group_modes["inbound"] + group_modes["binnen"]
                    group_modes["balance"] = group_modes["outbound"] - group_modes["inbound"]
        result[scenario_id] = {
            "national": national,
            "national_modes": national_modes,
            "national_group_modes": national_group_modes,
            "regional": regional,
            "relations": relations,
        }
    return result


def validate() -> None:
    bundle = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert bundle["metadata"]["available_scenarios"][1]["available"] is True
    assert {"2019_BASE", "2040_P1"} == set(bundle["scenarios"])

    relation_checks = find_relation_checks(bundle)
    raw = collect_raw_values(load_cell_targets(), load_group_lookup(), relation_checks)
    for scenario_id in SCENARIOS:
        dashboard = bundle["scenarios"][scenario_id]
        for metric in ("tonnes", "tkm"):
            assert_close(
                f"{scenario_id} national {metric}",
                dashboard["national"][f"total_{metric}"],
                raw[scenario_id]["national"][metric],
            )
            for mode in MODES:
                assert_close(
                    f"{scenario_id} national {mode} {metric}",
                    dashboard["national"]["modes"][mode][metric],
                    raw[scenario_id]["national_modes"][metric][mode],
                )
                assert_close(
                    f"{scenario_id} national group {CHECK_GROUP} {mode} {metric}",
                    dashboard["national"]["modes_by_group"][CHECK_GROUP][mode][metric],
                    raw[scenario_id]["national_group_modes"][metric][mode],
                )
        for region_id in CHECK_REGIONS:
            dashboard_region = dashboard["regions"][region_id]
            for metric in ("tonnes", "tkm"):
                for direction in ("all", "outbound", "inbound", "binnen"):
                    assert_close(
                        f"{scenario_id} {region_id} {metric} {direction}",
                        dashboard_region[f"directions_{metric}"][direction],
                        raw[scenario_id]["regional"][region_id]["directions"][metric][direction],
                    )
                for mode in MODES:
                    assert_close(
                        f"{scenario_id} {region_id} {mode} {metric}",
                        dashboard_region[f"modes_direction_{metric}"][mode]["all"],
                        raw[scenario_id]["regional"][region_id]["modes"][metric][mode]["all"],
                    )
                    for direction in ("all", "outbound", "inbound", "binnen", "balance"):
                        assert_close(
                            f"{scenario_id} {region_id} group {CHECK_GROUP} {mode} {metric} {direction}",
                            dashboard_region[f"modes_by_group_{metric}"][CHECK_GROUP][mode][direction],
                            raw[scenario_id]["regional"][region_id]["group_modes"][metric][mode][direction],
                        )

    forecast_regions = bundle["scenarios"]["2040_P1"]["regions"]
    for region_id, direction, partner_id, group in relation_checks:
        relation_rows = (
            forecast_regions[region_id]["relations_overall"][direction]
            if group == "ALL"
            else forecast_regions[region_id]["by_group_relations"][group][direction]
        )
        row = next(item for item in relation_rows if item["partner_id"] == partner_id)
        for metric in ("tonnes", "tkm"):
            assert_close(
                f"2040 relation {region_id} {direction} {partner_id} group {group} {metric}",
                row[metric],
                raw["2040_P1"]["relations"][(region_id, direction, partner_id, group)][metric],
            )
            expected_growth = percentage_change(
                row[metric],
                raw["2019_BASE"]["relations"][(region_id, direction, partner_id, group)][metric],
            )
            actual_growth = row["growth_2019"][metric]
            growth_mismatch = (
                (actual_growth is None) != (expected_growth is None)
                or (
                    actual_growth is not None
                    and expected_growth is not None
                    and abs(actual_growth - expected_growth) > 0.11
                )
            )
            if growth_mismatch:
                raise AssertionError(
                    f"2040 relation growth {region_id} {direction} {partner_id} group {group} {metric}: "
                    f"dashboard={row['growth_2019'][metric]}, raw={expected_growth}"
                )

    expected_growth = percentage_change(
        raw["2040_P1"]["national"]["tonnes"], raw["2019_BASE"]["national"]["tonnes"]
    )
    if bundle["scenarios"]["2040_P1"]["national"]["growth_2019_tonnes_pct"] != expected_growth:
        raise AssertionError("Nationaler 2019-zu-2040-Vergleich stimmt nicht mit den Rohmatrizen überein.")

    print("VP2040 validation passed")
    for scenario_id in SCENARIOS:
        national = raw[scenario_id]["national"]
        print(f"{scenario_id}: {national['tonnes'] / 1e6:.3f} Mio. t, {national['tkm'] / 1e9:.3f} Mrd. tkm")
    print("Checked NUTS-3 regions: " + ", ".join(CHECK_REGIONS))
    print(f"Checked modal values for NST-7 group {CHECK_GROUP}.")
    print("Checked relations: " + ", ".join(f"{a}/{b}/{c}/group-{d}" for a, b, c, d in relation_checks))


if __name__ == "__main__":
    validate()
