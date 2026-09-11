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

Lokaler Analyseassistent: `analysis/run_assistant.py` führt bestätigte Einzelabfragen oder die Bereitschaftsprüfung des 45-Fälle-Katalogs aus. `analysis/prepare_assistant_cases.py` trennt Eingaben und Referenzen; `analysis/prepare_b07_local.py` prüft ausschließlich vorhandene Berliner Mautauszüge. `analysis/configure_requesty.ps1` speichert den Nutzerschlüssel lokal DPAPI-verschlüsselt; `analysis/serve_assistant.py` ist ein nur an Loopback gebundener API-Pilot mit künstlichem Konto. `validation/validate_assistant_runtime.py` führt lokale Tests ohne externe KI aus; benötigt Schreibzugriff auf `C:\tmp`. `analysis/build_assistant_release.py` erstellt dort ein neues Übergabepaket, ohne Serverumschaltung. Anleitung und Freigabegrenzen: [Lokaler Pilot](../docs/betrieb/ANALYSEASSISTENT_LOKALER_PILOT.md), Roadmap Abschnitt 24 und Qualitätssicherungsplan.

`analysis/run_assistant_catalog.py` ist der gebündelte Testtreiber: standardmäßig Vorprüfung ohne KI; ein echter Modelllauf erfordert `--requesty --gate <aktuelle Freigabedatei>`. `analysis/prepare_assistant_gate.py` bindet bestandene lokale Tests, Eingaben, Referenzen und Datenstand. Nach Code-/Promptänderungen frühere Nachweise nicht als aktuelle Freigabe verwenden. Jeder Fall erhält ein eigenes Ergebnis; keine Sollantworten im Modellprozess. Der erste 45er-Lauf und zwei gezielte Nachprüfungen sind erfolgt, noch keine vollständige fachliche Abnahme.

`analysis/review_assistant_catalog.py --live <Laufordner> --baseline <lokaler Vergleich> --output <neue JSON-Datei>` prüft anschließend Ergebnisprüfsummen, Routing, unveränderte Fakten und erlaubte Aussageauswahl ohne externe Aufrufe. Der Bericht unterscheidet erfassten Verbrauch von Aufrufen ohne Verbrauchsdaten. Identische lokale Ergebnisse belegen keine vollständige fachliche Sollantwort. Aktueller Nachweis im Qualitätssicherungsplan unter „echter 45-Fälle-Modelllauf und Nachprüfung“.

`analysis/build_assistant_test_report.py --output <Berichtsordner>` erstellt eine durchsuchbare HTML-Übersicht und eine Markdown-Lesefassung der gespeicherten 45 Antworten einschließlich der beiden gezielten Nachprüfungen. Keine API-Aufrufe; Ergebnisprüfsummen werden vor Darstellung geprüft. `--update` ersetzt ausschließlich die drei erzeugten Lesedateien. Der aktuelle Bericht liegt unter `outputs/analyseassistent_runtime_20260910/lesebericht01/`.

`validation/validate_assistant_portal.py --portal <Plattformordner> --output <neuer Bericht>` prüft die tatsächlichen Portalrouten, Verwaltung, Migrationen und Release-Anforderungen mit den gezielten Plattformtests; keine Liveportal- oder Modellverbindung. Aktuell 47 bestandene Prüfungen. Temporäre Testdateien unter `C:\tmp`.

`validation/validate_assistant_postgres.py` startet eine eigene temporäre PostgreSQL-Instanz unter `C:\tmp`, nur auf Loopback und mit künstlichen Konten. Parameter: `--postgres-bin`, `--driver-dir`, `--portal`, `--output`. Es werden die aktuellen neun Portal-Migrationen einschließlich KI-Kontingentschema eingespielt; 14 echte Transaktions-/Zugriffs- und Verwaltungsprüfungen folgen. Die eigene Instanz wird abschließend gestoppt und der eigene Cluster entfernt. Keine Portal-Zugangsdaten oder bestehende Datenbankdienste verwenden. Der Treiber muss wie andere temporäre Abhängigkeiten unter `C:\tmp` liegen. Geprüfte Versionen und Nachweis stehen im Qualitätssicherungsplan.

`analysis/prepare_assistant_support.py` baut das zusätzliche private Güter-/KV-Abbild aus dem an B04 gebundenen D01-Originalprofil und den an B01 gebundenen Schienen-/IWW-Rohdateien. Quellhashes, Zeilenzahlen, C-Güterprojektion, KV-Jahres-/Richtungswerte und Unterschiede bei unbekanntem Gegenraum werden geprüft. Aktivierung nur nach vollständigem Aufbau; bestehende Datenstände nicht überschreiben. Kein Netzabruf, keine Veränderung der Dashboarddateien und keine automatische Modellfreigabe. Aktueller Nachweis im Qualitätssicherungsplan unter „D01-Güterfelder, KV und Quellenhinweise“.

KV-Terminalebene: `python -B scripts/frontend/build_terminal_data.py` erzeugt die minimale Standortdatei aus dem lokalen GeoJSON. Anschließend Frontend neu bauen. `node scripts/validation/validate_terminals_quota.cjs` prüft Quelltreue, erlaubte Felder und die Grenzen des lokalen Fragenkontingents. Abgrenzung und Browserprüfung stehen in der Betriebsdokumentation und im Qualitätssicherungsplan unter der Ergänzung vom 10.09.2026.

Nachprüfung B01–B03: `validation/check_b0103_regressions.py` wird von den jeweiligen Hauptprüfern eingebunden. Es ergänzt unabhängige Originalzellkontrollen, Eingabe-/Fehlwertfälle, IWW-Abfragen und lokale Aufruftests. Prüfer- und Aufrufcode werden mit den neuen Releases versioniert. Die komplette lokale Datenkette ist nach betroffenen Codeänderungen in Abhängigkeitsreihenfolge zu erneuern; aktueller Nachweis in Roadmap Abschnitt 23 und im Qualitätssicherungsplan.

### Separater Analysebestand B01

`pipelines/build_b01_analysis.py` erzeugt den zusätzlichen OD-Bestand; `analysis/b01.py` enthält Quellenzustände und die gezielte Relationsabfrage. `analysis/query_b01.py` ist der lokale Abfrageaufruf. `validation/validate_b01_analysis.py` prüft Quellen, Mengen und Fehlwertfälle und aktiviert einen Datenstand nur nach bestandener Prüfung. Diese Skripte sind kein Bestandteil des Browser-Builds.

Schritte, Dateien und aktueller Prüfstand stehen zentral in [Roadmap, Abschnitt 17](../docs/roadmap/ROADMAP_ANALYSEASSISTENT_PORTAL.md#17-b01--umsetzung-und-zentraler-arbeitsstand-09092026). Die Wiederholung ist in der [Datenaktualisierungsanleitung](../docs/betrieb/ANLEITUNG_DATENAKTUALISIERUNG.md) beschrieben. Benötigt werden Python ab 3.11, DuckDB mit CSV-Zeichensatzunterstützung und Schreibrechte unter `C:\tmp`; keine Abhängigkeiten im Projekt installieren.

### Separater Analysebestand B02

`pipelines/build_b02_analysis.py` liest einen geprüften B01-Stand und erzeugt monatliche Schienen-/IWW-Relationen sowie Quellen-/Jahresabdeckung. `analysis/b02.py` enthält die Monats- und Zeitvergleichsregeln; `analysis/query_b02.py` fragt lokale Zeitreihen ab. `validation/validate_b02_analysis.py` gleicht alle Monatssummen mit B01 und die Tonnen je Quellmonat unabhängig mit den Original-CSV ab. Aufbau und Prüfung benötigen keinen Modellaufruf. Update-Reihenfolge und spätere serverinterne Bereitstellung: Datenaktualisierungsanleitung, Abschnitt 13. Aktueller Status: Analyseassistenten-Roadmap.

### Separater Analysebestand B03

`pipelines/build_b03_analysis.py` ergänzt aus zusammengehörigem, geprüftem B01/B02 die monatlichen SGV-Feinpositionen sowie vorhandene VD2-/VD3c-Jahresdateien für Versand und Empfang. `analysis/b03.py` enthält Klassifikationsregister und begrenzte Abfragen; `analysis/query_b03.py` ist der lokale Aufruf. `validation/validate_b03_analysis.py` prüft alle Schienen-Feinsummen gegen B02 und Original-CSV sowie sämtliche erschlossenen KBA-Wert-/Zeichenfelder. TON/TKM/FT werden in Originaleinheiten und getrennt nach I/G geführt; KM-Felder werden nicht erschlossen. Aufbau und Prüfung benötigen keinen Modellaufruf. Befehle und Grenzen: Datenaktualisierungsanleitung Abschnitt 14; tatsächlicher Prüfstand: Qualitätssicherungsplan und Roadmap Abschnitt 20.

### Gemeinsamer lokaler Analysebestand B04–B06

`pipelines/build_b0406_analysis.py` erzeugt einen zusammengehörigen Stand für Regionsvergleiche und VP-Rankings (B04), nationale Verkehrsbeziehungen mit Straßen-Inlandsleistung (B05) sowie vollständige veröffentlichte Flughafen- und Seehafenpartner (B06). Regionsverbünde greifen auf den bereits geprüften B01-Relationsbestand zu; dieser wird nicht kopiert. `analysis/b0406.py` enthält die begrenzten Abfragen, `analysis/query_b0406.py` den lokalen Aufruf. `validation/validate_b0406_analysis.py` prüft Quellenfassungen, Originalwerte und fachliche Grenzfälle und aktiviert nur einen bestandenen Stand. Wiederholung: Datenaktualisierungsanleitung Abschnitt 15. Tatsächliche Freigabe: Qualitätssicherungsplan und Roadmap Abschnitt 21.

Die B04–B06-Hauptprüfung enthält zusätzlich `validation/check_b0406_regressions.py`: reale Abfragevarianten, nicht anwendbare/fehlende TEU, fehlende Jahrgänge, Prognoserückgänge, Versionskonflikte und verweigerte beziehungsweise wiederholte Freigaben. Die kleinen Testdateien entstehen ausschließlich unter `C:\tmp` und werden automatisch entfernt. Die Partnerprüfung muss vor jeder Hauptprüfung mit Aktivierung vorliegen und zum Manifest sowie zum aktuellen Prüfer passen.

### Bestehende Daten- und Frontendaufbereitung

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

### Portalgebundener Analyseassistent: Oberflächenprüfung

- Die frühere Modulauswahl-Prüfung `validate_assistant_context.cjs` entfällt nach dem Nutzerentscheid für offene Fragen. `validate_assistant_browser.cjs` prüft stattdessen, dass freie Fragen keine Kartenfilter übertragen, bestätigte Folgefragen ihren belegten Kontext behalten und die Beispielsammlung ohne Überlagerung bedienbar bleibt.
- `validation/validate_assistant_browser.cjs <vollständiger Portalrelease> <Ausgabeordner>`: neun Chrome-Prüfungen mit synthetischen HTTP-Antworten aus dem lokalen T20-Nachweis. Testet unter anderem Kontingentanzeige, Rückfragen, Folgeaktionen, Doppelklick, mobilen Tabellenüberlauf und unklaren Verbindungsabbruch. Keine echten Modellaufrufe; kein vollständiger Authentifizierungs-/Datenbanktest. Playwright bleibt außerhalb des Projekts unter `C:/tmp`.
- `validation/validate_assistant_portal.py --portal <Plattform-Repository> --output <Bericht.json>`: aktuell 49 Portal-/Releaseprüfungen.
- Der Frontendbuild bindet `js/shared/ai-client.js` ein. Der historische Browserzähler `ai-quota.js` wird nicht mehr ausgeliefert. Die Kontingentfunktion wird serverseitig sowie gegen PostgreSQL geprüft.

- `validation/validate_assistant_alwaysdata.py --portal <Plattform-Repository> --release <lokaler Testrelease> --output <neuer Bericht.json>`: prüft ausschließlich den exakt passenden aktiven Testrelease über eine kurzlebige AlwaysData-Aufgabe. Benötigt den bestehenden AlwaysData-Testtoken nur im Prozess. Verifiziert Serverdateien, private Linux-Laufzeit und T20 ohne Modell sowie Migration/Kontingente in einer lesenden Transaktion. Temporäre Aufgabe, FTPS-Zugang und Statusdatei werden entfernt. Der Prüfer liest oder überträgt keinen lokalen Requesty-Schlüssel. Mit dem ausdrücklichen Zusatz `--requesty` führt er einen echten kostenpflichtigen Modelltest aus der vorhandenen Serverkonfiguration aus; eine Startdatei verhindert parallele beziehungsweise wiederholte Ausführung derselben Prüfaufgabe. Diese Startdatei wird ebenfalls bereinigt. Ohne Zusatz entstehen keine Modellaufrufe.

- `validation/activate_assistant_test.py`: einmalige, ausdrücklich autorisierte Aktivierung des geprüften ui05-Testeinstiegs. Ohne `--apply` nur Konfigurationsplan; mit `--apply` Manifest-/Linux-/Migrationsprüfung, Prüfung auf fehlende bestehende Werkzeugrechte, Aktivierung des Werkzeugeintrags und des Testflags, Neustart sowie Prüfung unveränderter Produktionssite. Keine Kontofreigabe oder Modellaufrufe. Bestehende Servergeheimnisse werden nicht ausgegeben. Die anschließende Kontofreigabe erfolgt in der angemeldeten Portalverwaltung.

- `analysis/build_assistant_references.py`: erzeugt die private Namens-/Methodikreferenz aus vorhandenen Dashboardquellen; `--check` bestätigt ohne Änderung die vollständige Übereinstimmung. Keine neuen Quellen, Länderzuordnungen oder Modellaufrufe. Die Referenz wird vom Übergabebuilder automatisch privat übernommen und durch das Laufzeit-Prüfgate gebunden.
