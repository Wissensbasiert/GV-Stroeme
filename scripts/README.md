# Skriptübersicht

Alle Befehle werden aus dem Projektstamm ausgeführt. Die Unterordner zeigen Zweck und Status der Skripte.

| Ordner | Zweck | Status |
|---|---|---|
| `pipelines/` | zentrale Aufbereitung der Ist-Daten, Prognose, Seeverkehrs- und Intermodaldaten | aktiv |
| `frontend/` | erzeugt die ausgelieferten HTML-, CSS- und JavaScript-Dateien aus den modularen Quellen | aktiv |
| `validation/` | automatisierte fachliche und technische Prüfungen | aktiv |
| `geodata/` | Aufbau und Aufbereitung räumlicher Grundlagen | aktiv bei Geodatenänderungen |
| `toll/` | Aufbereitung des Mautdatenmoduls | aktiv für dieses Modul |
| `utilities/` | gezielte Ergänzungs- und Wartungsschritte | nur nach Anleitung einsetzen |
| `examples/` | nachvollziehbare Abfragebeispiele, keine Produktionspipeline | Beispiel |
| `legacy/` | abgelöste Bundler und frühere Varianten | historisch, nicht für aktuelle Builds verwenden |

## Zentrale Aufrufe

```powershell
python scripts/pipelines/pipeline_phase2_aggregations.py
python scripts/pipelines/build_web_data_bundle_v5.py
python scripts/pipelines/build_intermodal_data.py
python scripts/pipelines/build_maritime_port_profiles.py
python scripts/pipelines/build_airfreight_data.py
python scripts/validation/validate_airfreight_bundle.py
python scripts/pipelines/pipeline_vp2040.py
python scripts/frontend/build_frontend.py all
```

Welche Reihenfolge und welche Prüfungen für eine konkrete Datenaktualisierung gelten, steht verbindlich in [`../docs/betrieb/ANLEITUNG_DATENAKTUALISIERUNG.md`](../docs/betrieb/ANLEITUNG_DATENAKTUALISIERUNG.md). Der dokumentierte Prüfstand steht in [`../docs/qualitaet/QUALITÄTSSICHERUNGSPLAN.md`](../docs/qualitaet/QUALITÄTSSICHERUNGSPLAN.md).

## Regeln für die Verwendung

- Aktuelle Datenpakete ausschließlich mit den dokumentierten Skripten unter `pipelines/` erzeugen.
- Vor einer Freigabe die passenden Prüfungen unter `validation/` ausführen.
- Dateien unter `legacy/` nicht in automatisierte Abläufe aufnehmen. Sie bleiben nur zur Nachvollziehbarkeit früherer Entwicklungsstände erhalten.
- Generierte Browserdateien nicht direkt pflegen; Änderungen erfolgen in den modularen Frontend-Quellen und werden anschließend mit dem Frontend-Build zusammengesetzt.
- Keine Paketumgebungen, Caches oder großen temporären Dateien im Projektordner anlegen.

## Browserpakete und wiederholbare Oberflächenprüfung

- `frontend/build_delivery_data.cjs`: erstellt kompakte Übersicht und Prognose sowie regionale Detailpakete; `--check` prüft den gesamten Auslieferungsbestand ohne Änderung.
- `frontend/serve_preview.cjs`: lokaler Testserver mit vollständigem Einlesen synchronisierter Dateien; ausschließlich auf `127.0.0.1`, Standardport 8000.
- `validation/validate_frontend_loading.cjs`: prüft erneute Anfragen nach Fehlern, gemeinsame parallele Anfragen, HTTP-/JSON-Fehler, Zeitbegrenzung, Abbruch und feste Tabelleneinheiten.
- `validation/validate_frontend_browser.cjs`: tatsächliche Chrome-Prüfung aller neun Module, ausgewählter Kennwerte, Filter, Dialoge, responsiver Darstellung sowie absichtlich ausgelöster Fehler und schneller Auswahlwechsel. Aufruf und externe Playwright-Abhängigkeit sind in `docs/betrieb/README_MAINTENANCE.md` dokumentiert.

- `validation/validate_toll_comparison.cjs`: fachliche Grenzfälle des Monatsvergleichs, fehlende und Nullwerte, Binnenverkehr in beiden Richtungen sowie vollständiger, nach Auswahl getrennter Cache mit Wiederholung und Abbruch.
- `validation/validate_frontend_exports.cjs`: größere Diagramme und ihre tatsächlichen Daten in allen Modulen, sechs KI-Beispiele, Exportdownloads, Mengenbegrenzung, Tastatur/Mobilansicht sowie wiederholbare Vorjahresfälle der Maut-API.
- `validation/validate_export_files.py`: öffnet die Browserdownloads erneut mit Excel- und GIS-Lesern; prüft Zahlen, Einheiten, Formelfreiheit, PNG-Auflösung sowie GeoPackage-Struktur, gültige geschnittene Geometrien und EPSG:4326. Aufruf mit dem Ausgabeordner des Export-Browserprüfers.

- `validation/validate_frontend_feedback.cjs`: Diagrammsymbole in der Kopfzeile mit hellem Hover-Hinweis, genau ein Tooltip mit Spitze in allen Modulen, sechs Fragen, Flughafen-KPIs nach Karte/Filter, Richtungen und fehlende Jahreswerte, Laptop-/Mobilansicht. Parameter: lokale URL mit abschließendem `/` und externer Ausgabeordner.
- `validation/validate_airfreight_kpis.cjs`: Anteil mit passendem Flughafen-Nenner, Ranggleichheit, Vorjahreswert null, unvollständiger Saldo und beibehaltene Auswahl bei fehlendem Jahr.

- `validation/validate_chart_layout.cjs`: Mindestzeichenflächen bei fünf Bildschirmgrößen, zwölf Kopfzeilensymbole, weißer Hinweis und Fokusführung, scrollbare Legende mit Tastaturbedienung sowie Größenrückkehr nach NST-Wechseln in Schiene, Binnenschiff und Seeverkehr. Parameter: lokale URL und externer Ausgabeordner.

- `validation/validate_mobile_maps.cjs`: echte Touch-Bedienung der neun Kartenlegenden, Menü vor Kartensteuerung per Trefferprüfung, Abstand zu vollständigen Quellenangaben und schmale Mobilansichten. Optionaler Vergleich mit zuvor gespeicherten Desktop-Abmessungen. Parameter: lokale URL, externer Ausgabeordner, optional Desktop-Geometrie-JSON.

- `validation/validate_mobile_views.cjs`: Desktop-Vergleich aller neun Module bei zwei Größen; mobile Register, passende Einstellungsfelder, Regions-/Jahreswechsel, echter Kartentipp, unveränderter Kartenausschnitt, Zurücksetzen, Tastatur und 320–900 Pixel breite Ansichten. Parameter: lokale URL, externer Ausgabeordner und optional vorher gespeicherte Desktop-Geometrie-JSON.
- `validation/validate_steckbrief.cjs`: Kurzfazit gegen echte Übersicht-/Prognosepakete, Top 5 und Richtungsaggregation, Prognose-Grenzfälle, Deutschland/Duisburg/Berlin/Bottrop, Modulfilter-Unabhängigkeit, Druckknopf, mobile Kopfzeile und PDF-Ausgaben. Parameter: lokale URL und externer Ausgabeordner; Playwright wie im Betriebshandbuch.
- `validation/validate_steckbrief_pdf.py`: Wiederöffnung der fünf Steckbrief-PDFs mit PyMuPDF; vollständiger Einstieg, alle Relationszeilen und Quellen sowie Textränder geprüft; Seiten-PNGs für die Sichtprüfung. Parameter: Ausgabeordner des Steckbrief-Browserprüfers.
