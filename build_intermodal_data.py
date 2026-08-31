"""Erzeugt die nationale Zeitreihe für das Modul "Intermodale Verkehre & KV".

Die Auswertung verwendet ausschließlich die mitgelieferten Destatis-Open-Data-
Jahresdateien. Sie erzeugt bewusst keine addierte "KV-Gesamtsumme": Eine
Transportkette kann sowohl in der Eisenbahn- als auch in der
Binnenschifffahrtsstatistik auftreten. Die beiden Teilmärkte bleiben deshalb
getrennt auswertbar.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import duckdb


BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "web_intermodal.json"
MIN_YEAR = 2016


def to_float(value: object) -> float:
    """Serialisiert DuckDB-Zahlen zuverlässig als JSON-Zahl."""
    number = float(value or 0.0)
    return number if math.isfinite(number) else 0.0


def metric_pair(row: dict[str, object], prefix: str) -> dict[str, float]:
    return {
        "tonnes": to_float(row[f"{prefix}_tonnes"]),
        "tkm": to_float(row[f"{prefix}_tkm"]),
    }


def build_dataset() -> dict[str, object]:
    con = duckdb.connect()
    rail_pattern = str(RAW_DIR / "SGV OpenData" / "eb_opendata_*.csv").replace("\\", "/")
    iww_pattern = str(RAW_DIR / "IWW OpenData" / "IWW_OpenData_*.csv").replace("\\", "/")

    rail_rows = con.execute(
        f"""
        WITH source AS (
            SELECT
                CAST(Referenzzeitraum_Jahr AS INTEGER) AS year,
                CAST(Ladeeinheit AS VARCHAR) AS load_unit,
                TRY_CAST(REPLACE(CAST(Befoerderungsmenge_in_Tonnen AS VARCHAR), ',', '.') AS DOUBLE) AS tonnes,
                TRY_CAST(REPLACE(CAST(Befoerderungsleistung_in_TKM AS VARCHAR), ',', '.') AS DOUBLE) AS tkm
            FROM read_csv('{rail_pattern}', delim=';', header=true, encoding='latin-1', union_by_name=true)
            WHERE CAST(Referenzzeitraum_Jahr AS INTEGER) >= {MIN_YEAR}
        )
        SELECT
            year,
            SUM(tonnes) AS total_tonnes,
            SUM(tkm) AS total_tkm,
            SUM(CASE WHEN load_unit IS NOT NULL AND load_unit <> 'Keine' THEN tonnes ELSE 0 END) AS intermodal_tonnes,
            SUM(CASE WHEN load_unit IS NOT NULL AND load_unit <> 'Keine' THEN tkm ELSE 0 END) AS intermodal_tkm,
            SUM(CASE WHEN load_unit LIKE 'Container%' THEN tonnes ELSE 0 END) AS container_tonnes,
            SUM(CASE WHEN load_unit LIKE 'Container%' THEN tkm ELSE 0 END) AS container_tkm,
            SUM(CASE WHEN load_unit LIKE 'Sattelzuganhaenger%' THEN tonnes ELSE 0 END) AS semitrailer_tonnes,
            SUM(CASE WHEN load_unit LIKE 'Sattelzuganhaenger%' THEN tkm ELSE 0 END) AS semitrailer_tkm,
            SUM(CASE WHEN load_unit LIKE 'Lastkraftwagen%' OR load_unit LIKE 'Lastzug%' THEN tonnes ELSE 0 END) AS accompanied_tonnes,
            SUM(CASE WHEN load_unit LIKE 'Lastkraftwagen%' OR load_unit LIKE 'Lastzug%' THEN tkm ELSE 0 END) AS accompanied_tkm
        FROM source
        GROUP BY year
        ORDER BY year
        """
    ).fetchdf().to_dict("records")

    iww_rows = con.execute(
        f"""
        WITH source AS (
            SELECT
                CAST(Referenzzeitraum_Jahr AS INTEGER) AS year,
                TRY_CAST(Container_Groesse AS INTEGER) AS container_size,
                TRY_CAST(REPLACE(CAST(Tonnen AS VARCHAR), ',', '.') AS DOUBLE) AS tonnes,
                TRY_CAST(REPLACE(CAST(Tonnen_km AS VARCHAR), ',', '.') AS DOUBLE) AS tkm
            FROM read_csv('{iww_pattern}', delim=';', header=true, encoding='utf-8', union_by_name=true)
            WHERE CAST(Referenzzeitraum_Jahr AS INTEGER) >= {MIN_YEAR}
        )
        SELECT
            year,
            SUM(tonnes) AS total_tonnes,
            SUM(tkm) AS total_tkm,
            SUM(CASE WHEN container_size IS NOT NULL THEN tonnes ELSE 0 END) AS containerised_tonnes,
            SUM(CASE WHEN container_size IS NOT NULL THEN tkm ELSE 0 END) AS containerised_tkm,
            SUM(CASE WHEN container_size = 1 THEN tonnes ELSE 0 END) AS c20_tonnes,
            SUM(CASE WHEN container_size = 1 THEN tkm ELSE 0 END) AS c20_tkm,
            SUM(CASE WHEN container_size = 3 THEN tonnes ELSE 0 END) AS c40_tonnes,
            SUM(CASE WHEN container_size = 3 THEN tkm ELSE 0 END) AS c40_tkm,
            SUM(CASE WHEN container_size IN (2, 4) THEN tonnes ELSE 0 END) AS other_tonnes,
            SUM(CASE WHEN container_size IN (2, 4) THEN tkm ELSE 0 END) AS other_tkm
        FROM source
        GROUP BY year
        ORDER BY year
        """
    ).fetchdf().to_dict("records")

    # Inländische NUTS-3-Relationen für Karte und Rangtabelle. Die beiden
    # Teilmärkte werden auch hier getrennt geführt; eine Addition wäre wegen
    # möglicher Kettenüberschneidungen fachlich nicht belastbar.
    rail_relation_rows = con.execute(
        f"""
        WITH source AS (
            SELECT
                CAST(Referenzzeitraum_Jahr AS INTEGER) AS year_ref,
                CAST(Versandregion_NUTS2024 AS VARCHAR) AS origin_id,
                CAST(Empfangsregion_NUTS2024 AS VARCHAR) AS destination_id,
                TRY_CAST(REPLACE(CAST(Befoerderungsmenge_in_Tonnen AS VARCHAR), ',', '.') AS DOUBLE) AS tonnes,
                TRY_CAST(REPLACE(CAST(Befoerderungsleistung_in_TKM AS VARCHAR), ',', '.') AS DOUBLE) AS tkm,
                TRY_CAST(REPLACE(CAST(Anzahl_Ladeeinheiten AS VARCHAR), ',', '.') AS DOUBLE) AS load_units,
                TRY_CAST(REPLACE(CAST(TEU AS VARCHAR), ',', '.') AS DOUBLE) AS teu
            FROM read_csv('{rail_pattern}', delim=';', header=true, encoding='latin-1', union_by_name=true)
            WHERE CAST(Referenzzeitraum_Jahr AS INTEGER) >= {MIN_YEAR}
              AND Ladeeinheit IS NOT NULL AND Ladeeinheit <> 'Keine'
              AND Versandregion_NUTS2024 LIKE 'DE%'
              AND Empfangsregion_NUTS2024 LIKE 'DE%'
        )
        SELECT year_ref, origin_id, destination_id,
            SUM(tonnes) AS tonnes, SUM(tkm) AS tkm,
            SUM(load_units) AS load_units, SUM(teu) AS teu
        FROM source
        GROUP BY year_ref, origin_id, destination_id
        ORDER BY year_ref, tonnes DESC
        """
    ).fetchdf().to_dict("records")

    iww_relation_rows = con.execute(
        f"""
        WITH source AS (
            SELECT
                CAST(Referenzzeitraum_Jahr AS INTEGER) AS year_ref,
                CAST(Einladeregion_NUTS3 AS VARCHAR) AS origin_id,
                CAST(Ausladeregion_NUTS3 AS VARCHAR) AS destination_id,
                TRY_CAST(REPLACE(CAST(Tonnen AS VARCHAR), ',', '.') AS DOUBLE) AS tonnes,
                TRY_CAST(REPLACE(CAST(Tonnen_km AS VARCHAR), ',', '.') AS DOUBLE) AS tkm,
                TRY_CAST(REPLACE(CAST(Anzahl_Ladungstraeger AS VARCHAR), ',', '.') AS DOUBLE) AS load_carriers,
                TRY_CAST(REPLACE(CAST(TEU AS VARCHAR), ',', '.') AS DOUBLE) AS teu
            FROM read_csv('{iww_pattern}', delim=';', header=true, encoding='utf-8', union_by_name=true)
            WHERE CAST(Referenzzeitraum_Jahr AS INTEGER) >= {MIN_YEAR}
              AND Container_Groesse IS NOT NULL
              AND Einladeregion_NUTS3 LIKE 'DE%'
              AND Ausladeregion_NUTS3 LIKE 'DE%'
        )
        SELECT year_ref, origin_id, destination_id,
            SUM(tonnes) AS tonnes, SUM(tkm) AS tkm,
            SUM(load_carriers) AS load_carriers, SUM(teu) AS teu
        FROM source
        GROUP BY year_ref, origin_id, destination_id
        ORDER BY year_ref, tonnes DESC
        """
    ).fetchdf().to_dict("records")

    # Richtungsbezogene Kennzahlen für Deutschland und einzelne NUTS-3-Regionen.
    # Anders als die Kartenrelationen berücksichtigen sie auch grenzüberschreitende
    # Verkehre der gewählten Region. Binnenverkehre werden separat geführt, damit
    # der Schalter in der Oberfläche ihren Einbezug nachvollziehbar steuern kann.
    rail_scoped_rows = con.execute(
        f"""
        WITH source AS (
            SELECT
                CAST(Referenzzeitraum_Jahr AS INTEGER) AS year_ref,
                CAST(Versandregion_NUTS2024 AS VARCHAR) AS origin_id,
                CAST(Empfangsregion_NUTS2024 AS VARCHAR) AS destination_id,
                TRY_CAST(REPLACE(CAST(Befoerderungsmenge_in_Tonnen AS VARCHAR), ',', '.') AS DOUBLE) AS tonnes,
                TRY_CAST(REPLACE(CAST(Befoerderungsleistung_in_TKM AS VARCHAR), ',', '.') AS DOUBLE) AS tkm,
                CASE WHEN Ladeeinheit IS NOT NULL AND Ladeeinheit <> 'Keine' THEN 1 ELSE 0 END AS is_qualified
            FROM read_csv('{rail_pattern}', delim=';', header=true, encoding='latin-1', union_by_name=true)
            WHERE CAST(Referenzzeitraum_Jahr AS INTEGER) >= {MIN_YEAR}
        ), scoped AS (
            -- Nationaler Gesamtwert: der unveränderte Statistikumfang, damit
            -- die Gesamtansicht keine innerdeutschen Relationen doppelt zählt.
            SELECT year_ref, 'DE' AS region_id, 'all' AS direction,
                tonnes, tkm, is_qualified
            FROM source
            UNION ALL
            -- Deutschland: jede inländische oder grenzüberschreitende Bewegung genau einmal.
            SELECT year_ref, 'DE' AS region_id,
                CASE WHEN origin_id = destination_id THEN 'binnen' ELSE 'outbound' END AS direction,
                tonnes, tkm, is_qualified
            FROM source WHERE origin_id LIKE 'DE%'
            UNION ALL
            SELECT year_ref, 'DE' AS region_id, 'inbound' AS direction,
                tonnes, tkm, is_qualified
            FROM source WHERE destination_id LIKE 'DE%' AND origin_id <> destination_id
            UNION ALL
            -- Region: Versand (einschließlich grenzüberschreitend) und Binnenverkehr.
            SELECT year_ref, origin_id AS region_id,
                CASE WHEN origin_id = destination_id THEN 'binnen' ELSE 'outbound' END AS direction,
                tonnes, tkm, is_qualified
            FROM source WHERE origin_id LIKE 'DE%'
            UNION ALL
            -- Region: Empfang; Binnenverkehr wurde oben bereits genau einmal erfasst.
            SELECT year_ref, destination_id AS region_id, 'inbound' AS direction,
                tonnes, tkm, is_qualified
            FROM source WHERE destination_id LIKE 'DE%' AND origin_id <> destination_id
        )
        SELECT year_ref, region_id, direction,
            SUM(tonnes) AS total_tonnes,
            SUM(tkm) AS total_tkm,
            SUM(CASE WHEN is_qualified = 1 THEN tonnes ELSE 0 END) AS qualified_tonnes,
            SUM(CASE WHEN is_qualified = 1 THEN tkm ELSE 0 END) AS qualified_tkm
        FROM scoped
        GROUP BY year_ref, region_id, direction
        ORDER BY year_ref, region_id, direction
        """
    ).fetchdf().to_dict("records")

    iww_scoped_rows = con.execute(
        f"""
        WITH source AS (
            SELECT
                CAST(Referenzzeitraum_Jahr AS INTEGER) AS year_ref,
                CAST(Einladeregion_NUTS3 AS VARCHAR) AS origin_id,
                CAST(Ausladeregion_NUTS3 AS VARCHAR) AS destination_id,
                TRY_CAST(REPLACE(CAST(Tonnen AS VARCHAR), ',', '.') AS DOUBLE) AS tonnes,
                TRY_CAST(REPLACE(CAST(Tonnen_km AS VARCHAR), ',', '.') AS DOUBLE) AS tkm,
                CASE WHEN TRY_CAST(Container_Groesse AS INTEGER) IS NOT NULL THEN 1 ELSE 0 END AS is_qualified
            FROM read_csv('{iww_pattern}', delim=';', header=true, encoding='utf-8', union_by_name=true)
            WHERE CAST(Referenzzeitraum_Jahr AS INTEGER) >= {MIN_YEAR}
        ), scoped AS (
            SELECT year_ref, 'DE' AS region_id, 'all' AS direction,
                tonnes, tkm, is_qualified
            FROM source
            UNION ALL
            SELECT year_ref, 'DE' AS region_id,
                CASE WHEN origin_id = destination_id THEN 'binnen' ELSE 'outbound' END AS direction,
                tonnes, tkm, is_qualified
            FROM source WHERE origin_id LIKE 'DE%'
            UNION ALL
            SELECT year_ref, 'DE' AS region_id, 'inbound' AS direction,
                tonnes, tkm, is_qualified
            FROM source WHERE destination_id LIKE 'DE%' AND origin_id <> destination_id
            UNION ALL
            SELECT year_ref, origin_id AS region_id,
                CASE WHEN origin_id = destination_id THEN 'binnen' ELSE 'outbound' END AS direction,
                tonnes, tkm, is_qualified
            FROM source WHERE origin_id LIKE 'DE%'
            UNION ALL
            SELECT year_ref, destination_id AS region_id, 'inbound' AS direction,
                tonnes, tkm, is_qualified
            FROM source WHERE destination_id LIKE 'DE%' AND origin_id <> destination_id
        )
        SELECT year_ref, region_id, direction,
            SUM(tonnes) AS total_tonnes,
            SUM(tkm) AS total_tkm,
            SUM(CASE WHEN is_qualified = 1 THEN tonnes ELSE 0 END) AS qualified_tonnes,
            SUM(CASE WHEN is_qualified = 1 THEN tkm ELSE 0 END) AS qualified_tkm
        FROM scoped
        GROUP BY year_ref, region_id, direction
        ORDER BY year_ref, region_id, direction
        """
    ).fetchdf().to_dict("records")

    coverage = con.execute(
        f"""
        SELECT 'rail' AS source, CAST(Referenzzeitraum_Jahr AS INTEGER) AS year,
            COUNT(DISTINCT Referenzzeitraum_Monat) AS month_count
        FROM read_csv('{rail_pattern}', delim=';', header=true, encoding='latin-1', union_by_name=true)
        WHERE CAST(Referenzzeitraum_Jahr AS INTEGER) >= {MIN_YEAR}
        GROUP BY 1, 2
        UNION ALL
        SELECT 'iww' AS source, CAST(Referenzzeitraum_Jahr AS INTEGER) AS year,
            COUNT(DISTINCT Referenzzeitraum_Monat) AS month_count
        FROM read_csv('{iww_pattern}', delim=';', header=true, encoding='utf-8', union_by_name=true)
        WHERE CAST(Referenzzeitraum_Jahr AS INTEGER) >= {MIN_YEAR}
        GROUP BY 1, 2
        ORDER BY source, year
        """
    ).fetchdf().to_dict("records")
    con.close()

    rail_by_year = {int(row["year"]): row for row in rail_rows}
    iww_by_year = {int(row["year"]): row for row in iww_rows}
    years = sorted(set(rail_by_year) & set(iww_by_year))
    if not years:
        raise ValueError("Keine gemeinsamen Berichtsjahre ab 2016 für Schiene und Binnenschiff gefunden.")
    relation_rows = {"rail": rail_relation_rows, "iww": iww_relation_rows}
    scoped_rows = {"rail": rail_scoped_rows, "iww": iww_scoped_rows}
    coverage_by_source = {"rail": {}, "iww": {}}
    for row in coverage:
        coverage_by_source[str(row["source"])][str(int(row["year"]))] = int(row["month_count"])

    data_by_year: dict[str, object] = {}
    relations_by_year: dict[str, object] = {}
    scoped_metrics_by_year: dict[str, object] = {}
    for year in years:
        rail = rail_by_year[year]
        iww = iww_by_year[year]
        rail_intermodal = metric_pair(rail, "intermodal")
        rail_structure = {
            "containers_and_swap_bodies": metric_pair(rail, "container"),
            "unaccompanied_semitrailers": metric_pair(rail, "semitrailer"),
            "accompanied_road_vehicles": metric_pair(rail, "accompanied"),
        }
        rail_structure["other_identified_load_units"] = {
            metric: max(
                0.0,
                rail_intermodal[metric]
                - sum(component[metric] for component in rail_structure.values()),
            )
            for metric in ("tonnes", "tkm")
        }

        data_by_year[str(year)] = {
            "rail": {
                "total": metric_pair(rail, "total"),
                "intermodal_load_units": rail_intermodal,
                "load_unit_structure": rail_structure,
            },
            "iww": {
                "total": metric_pair(iww, "total"),
                "containerised_transport": metric_pair(iww, "containerised"),
                "container_size_structure": {
                    "c20": metric_pair(iww, "c20"),
                    "c40": metric_pair(iww, "c40"),
                    "other_sizes": metric_pair(iww, "other"),
                },
            },
        }

        relations_by_year[str(year)] = {}
        for mode, rows in relation_rows.items():
            relations_by_year[str(year)][mode] = [
                {
                    "origin_id": str(row["origin_id"]),
                    "destination_id": str(row["destination_id"]),
                    "tonnes": round(to_float(row["tonnes"]), 1),
                    "tkm": round(to_float(row["tkm"]), 1),
                    "load_units": round(to_float(row["load_units"]), 1) if mode == "rail" else None,
                    "load_carriers": round(to_float(row["load_carriers"]), 1) if mode == "iww" else None,
                    "teu": round(to_float(row["teu"]), 2),
                }
                for row in rows if int(row["year_ref"]) == year
            ]

        scoped_metrics_by_year[str(year)] = {}
        for mode, rows in scoped_rows.items():
            qualified_key = "intermodal_load_units" if mode == "rail" else "containerised_transport"
            for row in rows:
                if int(row["year_ref"]) != year:
                    continue
                region_id = str(row["region_id"])
                direction = str(row["direction"])
                region_pack = scoped_metrics_by_year[str(year)].setdefault(region_id, {})
                mode_pack = region_pack.setdefault(mode, {"total": {}, qualified_key: {}})
                mode_pack["total"][direction] = metric_pair(row, "total")
                mode_pack[qualified_key][direction] = metric_pair(row, "qualified")

    return {
        "schema_version": 3,
        "years": years,
        "not_additive": True,
        "relation_scope": "Inländische NUTS-3-Relationen mit ausgewiesener Ladeeinheit (Schiene) bzw. Containergrößenklasse (Binnenschiff).",
        "sources": {
            "rail": f"Statistisches Bundesamt (Destatis), Güterverkehrsstatistik der Eisenbahn, EVAS 46131, gemeinsame Jahresdateien {years[0]}–{years[-1]}.",
            "iww": f"Statistisches Bundesamt (Destatis), Binnenschifffahrt, EVAS 46321, gemeinsame Jahresdateien {years[0]}–{years[-1]}.",
        },
        "definitions": {
            "rail_intermodal_load_units": "Eisenbahngüterverkehr mit einer ausgewiesenen Ladeeinheit ungleich 'Keine'.",
            "iww_containerised_transport": "Binnenschifffahrt mit einer ausgewiesenen Containergrößenklasse.",
            "comparison": "Die Anteile beziehen sich jeweils auf den gesamten Verkehrsträger desselben Jahres und derselben Kennzahl.",
            "directional_scope": "Richtungswerte werden für Deutschland und ausgewählte NUTS-3-Regionen aus Versand, Empfang und separat ausgewiesenem Binnenverkehr berechnet. Bei Regionalfiltern sind grenzüberschreitende Bewegungen der gewählten Region einbezogen.",
            "non_additivity": "Die Teilmärkte dürfen nicht zu einer KV-Gesamtsumme addiert werden, weil einzelne Transportketten in beiden Statistiken auftreten können.",
        },
        "coverage_months": coverage_by_source,
        "data_by_year": data_by_year,
        "relations_by_year": relations_by_year,
        "scoped_metrics_by_year": scoped_metrics_by_year,
    }


def main() -> None:
    dataset = build_dataset()
    OUTPUT_PATH.write_text(json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {OUTPUT_PATH.relative_to(BASE_DIR)} for {len(dataset['years'])} complete annual periods.")


if __name__ == "__main__":
    main()
