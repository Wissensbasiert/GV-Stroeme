"""Validate that published relation candidates cover both dashboard measures.

The dashboard applies its Top-X selection only after the user chooses tonnes
or tonne-kilometres.  This check therefore verifies that every retained
NST-7-specific relation file contains the top 25 candidates for *both*
measures.  It also guards the separate intermodal path, which intentionally
has no NST filter but must retain every qualified relation with a German side.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[2]
FACT_PATH = ROOT / "data" / "processed" / "fact_od_flows.parquet"
RELATIONS_DIR = ROOT / "data" / "processed" / "relations"
INTERMODAL_PATH = ROOT / "data" / "processed" / "web_intermodal.json"
RAW_DIR = ROOT / "data" / "raw"
TOP_LIMIT = 25


def top_partner_ids(rows: list[tuple[str, float, float]]) -> set[str]:
    # Match the deterministic tie-breaker used in build_web_data_bundle_v5.py.
    by_tonnes = sorted(rows, key=lambda row: (-row[1], row[0]))[:TOP_LIMIT]
    by_tkm = sorted(rows, key=lambda row: (-row[2], row[0]))[:TOP_LIMIT]
    return {partner_id for partner_id, _, _ in [*by_tonnes, *by_tkm]}


def validate_grouped_historical_relations(failures: list[str]) -> int:
    con = duckdb.connect()
    rows = con.execute(
        f"""
        SELECT year_ref, mode_transport, group_7_id, origin_nuts, dest_nuts,
               SUM(tonnes) AS tonnes, SUM(tkm) AS tkm
        FROM read_parquet('{FACT_PATH.as_posix()}')
        WHERE mode_transport IN ('rail', 'iww')
          AND (
            (origin_nuts LIKE 'DE%' AND dest_nuts IS NOT NULL AND dest_nuts <> '')
            OR (dest_nuts LIKE 'DE%' AND origin_nuts IS NOT NULL AND origin_nuts <> '')
          )
        GROUP BY 1, 2, 3, 4, 5
        """
    ).fetchall()
    con.close()

    source: dict[tuple[str, int, str, str, str], list[tuple[str, float, float]]] = defaultdict(list)
    for year, mode, group, origin, destination, tonnes, tkm in rows:
        # A German origin is a published outbound relation; a German
        # destination is a published inbound relation.  Do not create
        # fictitious regional files for the foreign partner side.
        if str(origin).startswith("DE"):
            source[(str(origin), int(year), str(mode), "outbound", str(group))].append(
                (str(destination), float(tonnes or 0), float(tkm or 0))
            )
        if str(destination).startswith("DE"):
            source[(str(destination), int(year), str(mode), "inbound", str(group))].append(
                (str(origin), float(tonnes or 0), float(tkm or 0))
            )

    cache: dict[str, dict] = {}

    def published_partner_ids(region: str, year: int, mode: str, direction: str, group: str) -> set[str]:
        relation_path = RELATIONS_DIR / f"{region}.json"
        if region not in cache:
            cache[region] = json.loads(relation_path.read_text(encoding="utf-8")) if relation_path.exists() else {}
        published = (
            cache[region]
            .get(str(year), {})
            .get("by_mode", {})
            .get(mode, {})
            .get("by_group", {})
            .get(group, {})
            .get(direction, [])
        )
        return {
            str(row.get("dest_id") if direction == "outbound" else row.get("origin_id"))
            for row in published
        }

    checked = 0
    for (region, year, mode, direction, group), candidates in source.items():
        published_ids = published_partner_ids(region, year, mode, direction, group)
        expected_ids = top_partner_ids(candidates)
        missing = expected_ids - published_ids
        if missing:
            failures.append(
                f"{region}/{year}/{mode}/{direction}/NST-{group}: "
                f"{len(missing)} Top-Relation(en) fehlen ({', '.join(sorted(missing)[:5])})."
            )
        checked += 1

        # A currently visible relation needs its matching raw value from the
        # preceding year to compute a valid Vorjahresvergleich.  The prior
        # value can be outside that older year's own Top-X, so the build must
        # deliberately retain it as a comparison candidate.
        if year > 2016:
            previous_rows = source.get((region, year - 1, mode, direction, group), [])
            previous_positive_ids = {
                partner_id
                for partner_id, tonnes, tkm in previous_rows
                if tonnes > 0 or tkm > 0
            }
            expected_previous = expected_ids & previous_positive_ids
            prior_published_ids = published_partner_ids(region, year - 1, mode, direction, group)
            missing_prior = expected_previous - prior_published_ids
            if missing_prior:
                failures.append(
                    f"{region}/{year}/{mode}/{direction}/NST-{group}: "
                    f"{len(missing_prior)} Vorjahreswert(e) für aktuelle Top-Relation(en) fehlen "
                    f"({', '.join(sorted(missing_prior)[:5])})."
                )
    return checked


def validate_nuernberg_international_regression(failures: list[str]) -> int:
    """Keep the reported Nuremberg waterway exports in the published bundle.

    The values are deliberately read from the fact table instead of being
    hard-coded, so a legitimate future data revision remains possible while
    the two foreign partners stay a non-negotiable coverage case.
    """
    expected_partners = {"BE211", "NL366"}
    con = duckdb.connect()
    rows = con.execute(
        f"""
        SELECT dest_nuts, SUM(tonnes) AS tonnes, SUM(tkm) AS tkm
        FROM read_parquet('{FACT_PATH.as_posix()}')
        WHERE year_ref = 2025
          AND mode_transport = 'iww'
          AND group_7_id = '4'
          AND origin_nuts = 'DE254'
          AND dest_nuts IN ('BE211', 'NL366')
        GROUP BY dest_nuts
        """
    ).fetchall()
    con.close()
    raw = {str(partner): (float(tonnes or 0), float(tkm or 0)) for partner, tonnes, tkm in rows}
    if set(raw) != expected_partners:
        failures.append("Nürnberg/2025/IWW/NST-4: erwartete Auslandspartner BE211 und NL366 fehlen bereits in der Faktentabelle.")
        return 0

    relation_path = RELATIONS_DIR / "DE254.json"
    bundle = json.loads(relation_path.read_text(encoding="utf-8")) if relation_path.exists() else {}
    published = (
        bundle.get("2025", {})
        .get("by_mode", {})
        .get("iww", {})
        .get("by_group", {})
        .get("4", {})
        .get("outbound", [])
    )
    by_partner = {str(row.get("dest_id")): row for row in published}
    for partner, (expected_tonnes, expected_tkm) in raw.items():
        row = by_partner.get(partner)
        if row is None:
            failures.append(f"Nürnberg/2025/IWW/NST-4: Auslandspartner {partner} fehlt in der veröffentlichten Versandliste.")
            continue
        if abs(float(row.get("tonnes", 0)) - expected_tonnes) > 0.05 or abs(float(row.get("tkm", 0)) - expected_tkm) > 0.05:
            failures.append(f"Nürnberg/2025/IWW/NST-4: Wert für {partner} stimmt nicht mit der Faktentabelle überein.")
    return len(raw)


def validate_intermodal_completeness(failures: list[str]) -> int:
    con = duckdb.connect()
    rail_pattern = str(RAW_DIR / "SGV OpenData" / "eb_opendata_*.csv").replace("\\", "/")
    iww_pattern = str(RAW_DIR / "IWW OpenData" / "IWW_OpenData_*.csv").replace("\\", "/")
    rows = con.execute(
        f"""
        WITH rail AS (
            SELECT CAST(Referenzzeitraum_Jahr AS INTEGER) AS year,
                   CAST(Versandregion_NUTS2024 AS VARCHAR) AS origin,
                   CAST(Empfangsregion_NUTS2024 AS VARCHAR) AS destination
            FROM read_csv('{rail_pattern}', delim=';', header=true, encoding='latin-1', union_by_name=true)
            WHERE CAST(Referenzzeitraum_Jahr AS INTEGER) BETWEEN 2016 AND 2025
              AND Ladeeinheit IS NOT NULL AND Ladeeinheit <> 'Keine'
              AND (
                (Versandregion_NUTS2024 LIKE 'DE%' AND Empfangsregion_NUTS2024 IS NOT NULL AND Empfangsregion_NUTS2024 <> '')
                OR (Empfangsregion_NUTS2024 LIKE 'DE%' AND Versandregion_NUTS2024 IS NOT NULL AND Versandregion_NUTS2024 <> '')
              )
        ), iww AS (
            SELECT CAST(Referenzzeitraum_Jahr AS INTEGER) AS year,
                   CAST(Einladeregion_NUTS3 AS VARCHAR) AS origin,
                   CAST(Ausladeregion_NUTS3 AS VARCHAR) AS destination
            FROM read_csv('{iww_pattern}', delim=';', header=true, encoding='utf-8', union_by_name=true)
            WHERE CAST(Referenzzeitraum_Jahr AS INTEGER) BETWEEN 2016 AND 2025
              AND Container_Groesse IS NOT NULL
              AND (
                (Einladeregion_NUTS3 LIKE 'DE%' AND Ausladeregion_NUTS3 IS NOT NULL AND Ausladeregion_NUTS3 <> '')
                OR (Ausladeregion_NUTS3 LIKE 'DE%' AND Einladeregion_NUTS3 IS NOT NULL AND Einladeregion_NUTS3 <> '')
              )
        )
        SELECT 'rail' AS mode, year, origin, destination FROM rail GROUP BY ALL
        UNION ALL
        SELECT 'iww' AS mode, year, origin, destination FROM iww GROUP BY ALL
        """
    ).fetchall()
    con.close()

    expected: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    for mode, year, origin, destination in rows:
        expected[(str(year), str(mode))].add((str(origin), str(destination)))

    bundle = json.loads(INTERMODAL_PATH.read_text(encoding="utf-8"))
    checked = 0
    for key, expected_pairs in expected.items():
        year, mode = key
        published_pairs = {
            (str(row["origin_id"]), str(row["destination_id"]))
            for row in bundle.get("relations_by_year", {}).get(year, {}).get(mode, [])
        }
        missing = expected_pairs - published_pairs
        if missing:
            failures.append(f"Intermodal {year}/{mode}: {len(missing)} qualifizierte Relation(en) mit deutschem Bezug fehlen.")
        checked += 1
    return checked


def main() -> None:
    failures: list[str] = []
    grouped_cases = validate_grouped_historical_relations(failures)
    regression_cases = validate_nuernberg_international_regression(failures)
    intermodal_cases = validate_intermodal_completeness(failures)
    if failures:
        raise SystemExit("RELATIONS-VALIDIERUNG FEHLGESCHLAGEN:\n- " + "\n- ".join(failures[:100]))
    print(
        "BESTANDEN: "
        f"{grouped_cases} NST-7-Relationsgruppen enthalten die Top-{TOP_LIMIT}-Kandidaten "
        "für Tonnen und Tonnenkilometer sowie ihre vorhandenen Vorjahreswerte; "
        f"{regression_cases} Nürnberg-Auslandsrelation(en) stimmen; "
        f"{intermodal_cases} Intermodal-Jahr/Teilmärkte sind vollständig."
    )


if __name__ == "__main__":
    main()
