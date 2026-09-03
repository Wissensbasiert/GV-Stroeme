#!/usr/bin/env python3
"""Statische Integritätsprüfung des Live-Mautdatenmoduls."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key == "id" and value:
                self.ids.append(value)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "js" / "app.js").read_text(encoding="utf-8")
    styles = (ROOT / "css" / "style.css").read_text(encoding="utf-8")
    registry = json.loads(
        (ROOT / "data" / "processed" / "toll_municipalities.json").read_text(encoding="utf-8")
    )
    boundary_dir = ROOT / "data" / "processed" / "toll_municipality_boundaries"
    boundary_index = json.loads((boundary_dir / "index.json").read_text(encoding="utf-8"))

    parser = IdCollector()
    parser.feed(index)
    duplicates = sorted(key for key, count in Counter(parser.ids).items() if count > 1)
    require(not duplicates, f"Doppelte HTML-IDs: {duplicates}")

    for identifier in (
        "tab-overview", "tab-road", "tab-toll", "tab-rail", "tab-iww",
        "tab-maritime", "tab-intermodal", "tab-forecast",
        "controlGroupTollMunicipality", "controlGroupTollMonth",
        "controlGroupTollMetric", "controlGroupTollDirection",
        "tollLeafletMap", "tableTollRelationsBody", "chartTollDistanceClasses",
        "tollChartEmpty",
        "tollConnectionLegendThin", "tollConnectionLegendMedium", "tollConnectionLegendThick",
    ):
        require(f'id="{identifier}"' in index, f"HTML-ID fehlt: {identifier}")

    require(
        "webgis.toll-collect.de/arcgis/rest/services/lkw-verkehrsportal/" in app
        and "mautdaten_bund_monat_sz/FeatureServer/0/query" in app,
        "Dokumentierter Live-API-Endpunkt fehlt im Bundle.",
    )
    require(
        "returnDistinctValues" in app and "outFields: 'monat'" in app,
        "Die Monatsauswahl wird nicht aus den tatsächlich verfügbaren API-Monaten aufgebaut.",
    )
    require(
        "Die Mautdaten-API ist derzeit nicht erreichbar." in app,
        "Verbindlicher API-Fehlerhinweis fehlt.",
    )
    require(
        "tollMunicipality: null" in app and "tollMunicipality: '11000000'" not in app,
        "Das Modul muss ohne still voreingestellte Gemeinde starten.",
    )
    require(
        "TOLL_MUNICIPALITY_BOUNDARY_BASE_URL" in app
        and "toll_municipality_boundaries" in app
        and "index.json" in app
        and "fetchTollMunicipalityBoundaryFile" in app
        and "TOLL_MUNICIPALITY_MIN_ZOOM = 7" in app
        and "datenquellen_vg_nuts.pdf" in app
        and "https://sgx.geodatenzentrum.de/wfs_vg250" not in app,
        "Die lokale, amtliche BKG-Gemeindegeometrie für die Kartenauswahl fehlt.",
    )
    require(
        "Zoomen Sie in die Karte" in app
        and "Daten werden nach Auswahl einer Gemeinde angezeigt." in index,
        "Einheitliche Nutzerführung für den leeren Startzustand fehlt.",
    )
    require(
        "getTollConnectionClassification" in app
        and "getTollGeometryRepresentativePoint" in app
        and "toll-binnen-badge" in app
        and "Anteil der Mautfahrten" in index,
        "Harmonisierte Tabelle, Linienklassierung oder Mautfahrten-Bezeichnung fehlt.",
    )
    require(
        "toll-relation-leaflet-tooltip" in app
        and "Monat und Jahr:" in app
        and "Richtung:" in app
        and "toll-map-tooltip-route-arrow" in app
        and ".toll-map-tooltip-route-arrow" in styles
        and "color: #64748b" in styles
        and "font-size: inherit" in styles
        and ".leaflet-tooltip.toll-relation-leaflet-tooltip" in styles,
        "Das Mautdaten-Tooltip enthält keine lesbare Relationsdarstellung.",
    )
    require(
        "radius: 6" in app
        and "markerRadius" in app
        and "L.circleMarker([destination.lat, destination.lng]" in app
        and "weight: 1.15" in app
        and "opacity: 0.64" in app
        and "3.8 : 5.6" in app,
        "Mautdaten-Verbindungsendpunkte, angemessene Linienbreiten oder dezente Deutschlandgrenze fehlen.",
    )
    require(
        "fetchTollRelationsForDirection('outbound')" in app
        and "fetchTollRelationsForDirection('inbound')" in app
        and "state.tollDirection === 'both'" in app
        and "distanceWeighted" in app
        and "one relation, not one outbound and one inbound trip" in app,
        "Die kombinierte Darstellung beider Richtungen ist nicht nachvollziehbar implementiert.",
    )
    require(
        "Von Gemeinde" in index
        and "Zu Gemeinde" in index
        and "Beide Richtungen" in index
        and "Im Grenzraum können die zugrunde liegenden Fahrten über Deutschland hinausführen" in index
        and "formatTollTripShare" in app
        and "kombinierte Ansicht" in index
        and "fertige Kennzahl aus den Rohdaten" in index,
        "Neutrale Richtungsbegriffe, Grenzraumhinweis oder präzise Anteilsanzeige fehlen.",
    )
    require(
        "bindTollHoverTooltip" in app
        and "closeTollHoverTooltip" in app
        and "delay = 400" in app
        and "{ delay: 0 }" in app
        and "toll-partner-cell" in app
        and "originalColor: TOLL_CONNECTION_COLOR" in app
        and "originalWeight: lineWeight" in app
        and "originalRadius: markerRadius" in app
        and "originalOpacity: 0.75" in app
        and "item.originalRadius ??" in app
        and "tollHoverSequence" in app
        and "resetTollPartnerHighlight" in app
        and "getTollDistanceChartKey" in app
        and "TOLL_DISTANCE_CLASS_COLORS" in app,
        "Zentrale Mauthover-Steuerung oder stabile Wiederherstellung der Verbindungen fehlt.",
    )
    require(
        "return formatDeNum(number, 0, 0);" in app
        and "&lt; 50 km</span><span>≥ 300 km" in app,
        "Kompakte Legendenwerte für Verbindungen oder Distanzklassen fehlen.",
    )
    require(
        "tollConnectionLegendTitle" in index
        and "setText('tollConnectionLegendTitle', 'Verbindungen');" in app
        and "unit: 'Fahrten'" in app
        and ".analysis-panel-body.is-toll-mode #controlGroupTollDirection" in styles,
        "Maut-Linienlegende oder modulspezifische Filterbreite fehlt.",
    )
    require(
        "data/raw/Straße/Lkw-Portal/Berlin" not in app
        and "outputs/mautdaten_berlin_auswertung" not in app,
        "Das Frontend darf keine lokalen Berliner Relationsdaten als Fallback laden.",
    )
    require(".toll-status-banner" in styles, "Mautdaten-Statusgestaltung fehlt.")
    require(
        ".analysis-panel-body .control-group[hidden]" in styles,
        "Ausgeblendete modulabhängige Filter bleiben im Layout sichtbar.",
    )

    municipalities = registry.get("municipalities")
    require(isinstance(municipalities, list) and municipalities, "Gemeinderegister ist leer.")
    require(
        registry.get("metadata", {}).get("purpose") == "Gemeinde-Suchliste; keine Relationswerte",
        "Zweck des Gemeinderegisters ist nicht eindeutig dokumentiert.",
    )
    require(
        all(set(item) == {"ags", "name"} for item in municipalities),
        "Gemeinderegister enthält unerwartete Relations- oder Kennwertfelder.",
    )
    require(
        any(item == {"ags": "11000000", "name": "Stadt, Berlin"} for item in municipalities),
        "Geprüfter Berliner Standardwert fehlt im Gemeinderegister.",
    )

    states = boundary_index.get("states")
    require(isinstance(states, list) and len(states) == 16, "Lokaler BKG-Grenzindex enthält nicht 16 Länderdateien.")
    registry_by_ags = {item["ags"]: item["name"] for item in municipalities}
    geometry_items: list[dict] = []
    for state in states:
        file_name = state.get("file") if isinstance(state, dict) else None
        require(isinstance(file_name, str) and file_name.endswith(".geojson"), "Ungültige Länderdatei im BKG-Grenzindex.")
        payload = json.loads((boundary_dir / file_name).read_text(encoding="utf-8"))
        features = payload.get("features")
        require(isinstance(features, list) and len(features) == state.get("feature_count"), f"{file_name}: falsche Featureanzahl.")
        geometry_items.extend(features)
    boundary_by_ags = {str(feature.get("properties", {}).get("ags")): feature for feature in geometry_items}
    require(len(boundary_by_ags) == len(geometry_items), "Lokale BKG-Geometrie enthält doppelte AGS.")
    require(
        boundary_index.get("metadata", {}).get("municipality_count") == len(boundary_by_ags)
        and boundary_index.get("metadata", {}).get("toll_collect_selectable_count") == len(registry_by_ags),
        "Lokaler BKG-Grenzindex dokumentiert den Umfang nicht korrekt.",
    )
    require(set(registry_by_ags).issubset(boundary_by_ags), "Für auswählbare Gemeinden fehlt eine lokale BKG-Geometrie.")
    require(
        all(feature.get("geometry", {}).get("type") in {"Polygon", "MultiPolygon"}
            for feature in boundary_by_ags.values())
        and all(boundary_by_ags[ags].get("properties", {}).get("name") == name
            for ags, name in registry_by_ags.items()),
        "Lokale BKG-Geometrie enthält unpassende Namen oder Geometrietypen.",
    )
    country_file = boundary_index.get("country_outline_file")
    country = json.loads((boundary_dir / str(country_file)).read_text(encoding="utf-8"))
    require(len(country.get("features", [])) == 1, "Lokale Deutschlandgrenze fehlt.")

    subprocess.run(["node", "--check", str(ROOT / "js" / "app.js")], check=True)
    print(
        "Mautdatenmodul geprüft: "
        f"{len(municipalities)} auswählbare Gemeinden, "
        f"{len(boundary_by_ags)} lokale amtliche Gemeindegrenzen, "
        "Live-API ohne Datenfallback."
    )
if __name__ == "__main__":
    main()
