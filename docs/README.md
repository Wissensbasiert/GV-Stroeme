# Dokumentationsübersicht

Diese Seite ist der zentrale Einstieg in die Projektdokumentation. Sie trennt verbindliche Betriebs- und Qualitätshinweise von fachlichen Konzepten und noch nicht umgesetzten Planungen.

## Welche Datei ist wofür maßgeblich?

| Fragestellung | Zuerst lesen | Ergänzend |
|---|---|---|
| Daten aktualisieren oder neu aufbereiten | [`betrieb/ANLEITUNG_DATENAKTUALISIERUNG.md`](betrieb/ANLEITUNG_DATENAKTUALISIERUNG.md) | [`qualitaet/QUALITÄTSSICHERUNGSPLAN.md`](qualitaet/QUALITÄTSSICHERUNGSPLAN.md) |
| Aufbau, Technik, Datenfluss oder Betrieb verstehen | [`betrieb/HANDBUCH_SYSTEMDOKUMENTATION.md`](betrieb/HANDBUCH_SYSTEMDOKUMENTATION.md) | [`betrieb/README_MAINTENANCE.md`](betrieb/README_MAINTENANCE.md) |
| Frontend ändern und neu zusammensetzen | [`betrieb/README_MAINTENANCE.md`](betrieb/README_MAINTENANCE.md) | [`../scripts/README.md`](../scripts/README.md) |
| GitHub sichern, Testrelease übertragen oder alte Serverstände bereinigen | [`betrieb/RELEASE_UND_GITHUB.md`](betrieb/RELEASE_UND_GITHUB.md) | Portalprojekt: `deployment/automation/`, aktiver Stand plus zwei Rückfallstände |
| Datenmodell, Begriffe und fachliche Struktur klären | [`fachkonzept/DATA_STRUCTURE_AND_CONCEPT.md`](fachkonzept/DATA_STRUCTURE_AND_CONCEPT.md) | `data_catalog.json` im Projektstamm und Metadaten der jeweiligen Rohquelle |
| Aktuellen Prüf- oder Freigabestand beurteilen | [`qualitaet/QUALITÄTSSICHERUNGSPLAN.md`](qualitaet/QUALITÄTSSICHERUNGSPLAN.md) | [`qualitaet/design-qa.md`](qualitaet/design-qa.md) nur für den dokumentierten Design-Prüfstand |
| Dashboard, Navigation oder Flugverkehr weiterentwickeln | [`roadmap/ROADMAP_DASHBOARD_WEITERENTWICKLUNG.md`](roadmap/ROADMAP_DASHBOARD_WEITERENTWICKLUNG.md) | Fachkonzept und Qualitätssicherungsplan |
| Analyseassistent, Portal oder Basis-/Premiumlogik planen | [`roadmap/ROADMAP_ANALYSEASSISTENT_PORTAL.md`](roadmap/ROADMAP_ANALYSEASSISTENT_PORTAL.md) | Dashboard-Roadmap bei Berührungspunkten zur Oberfläche |
| Vorbereitete Modellregeln, Datenfunktionen und Antwortprüfung verstehen | [`../config/analyseassistent/README.md`](../config/analyseassistent/README.md) | Im lokalen Assistenten und aktiven Testrelease eingebunden; eigenes Testkonto freigeschaltet und erster Browser-/Buchungstest bestanden; weitere Fachabnahme offen |
| Lokalen Analyseassistenten, Requesty-Schlüssel und Portalübergabe prüfen | [`betrieb/ANALYSEASSISTENT_LOKALER_PILOT.md`](betrieb/ANALYSEASSISTENT_LOKALER_PILOT.md) | Lokaler Pilot, echter Modelllauf, serverseitige Kontingente und aktivierter AlwaysData-Testeinstieg; eigenes Testkonto freigeschaltet und erster gemeinsamer Browser-/Buchungstest bestanden; weitere Antwortkorrekturen lokal geprüft, fachliche Gesamtfreigabe offen; neuester Nachtrag in Roadmap und Qualitätssicherungsplan |
| Zusätzliche Aufbereitung vorhandener Daten für den Assistenten planen | [`roadmap/ANALYSEASSISTENT_AUFBEREITUNGSPLAN.md`](roadmap/ANALYSEASSISTENT_AUFBEREITUNGSPLAN.md) | Alle 45 Testfälle zugeordnet; B01–B06 lokal mit Quellen-/Vergleichsgrenzen geprüft, B07 offen; aktueller Bestand und korrigierte T22-Sollannahme in Roadmap Abschnitt 21, nächste Schritte in Abschnitt 18 |

## Status der Dokumenttypen

- **Betrieb:** beschreibt den aktuellen technischen Umgang mit Anwendung und Daten.
- **Fachkonzept:** beschreibt Datenmodell, Begriffe und fachliche Logik.
- **Qualitätssicherung:** enthält Prüfkriterien und den jeweils dokumentierten Freigabestand. Bei Aussagen zum aktuellen Stand ist der Qualitätssicherungsplan maßgeblich.
- **Roadmap:** enthält Entscheidungen, Empfehlungen und offene Umsetzungsschritte. Eine Roadmap belegt nicht, dass eine Funktion bereits umgesetzt ist.

## Arbeitsreihenfolge für KI-Assistenten

1. Dieses Inhaltsverzeichnis lesen und die passende Leitdatei auswählen.
2. Bei Datenfragen zusätzlich die tatsächlichen Rohdaten, Schemas und Metadaten prüfen; keine Feldbedeutung allein aus Dateinamen ableiten.
3. Vor Änderungen den aktuellen Arbeitsstand prüfen und fremde oder nicht zugehörige Änderungen erhalten.
4. Nur aktive Skripte aus den in [`../scripts/README.md`](../scripts/README.md) genannten Bereichen verwenden. Dateien unter `scripts/legacy/` sind historische Stände.
5. Änderungen an Datenlogik, Bedienoberfläche oder Prüfverfahren in der jeweils zuständigen Dokumentation nachführen.
6. Deutsche Texte und Schlüssel mit führenden Nullen konsequent UTF-8- und typensicher behandeln.

## Weitere Markdown-Dateien

- [`../data/crosswalks/README_UMSTIEGSSCHLUESSEL.md`](../data/crosswalks/README_UMSTIEGSSCHLUESSEL.md) dokumentiert gezielt den fachlichen Umstiegsschlüssel für VP2040 und bleibt deshalb direkt bei den Crosswalk-Dateien.
- [`../data/raw/Luftverkehr/Flughafenstandorte/README_FLUGHAFENSTANDORTE.md`](../data/raw/Luftverkehr/Flughafenstandorte/README_FLUGHAFENSTANDORTE.md) dokumentiert die Originalquellen, Prüfsummen, Quellenrollen und Aktualisierung der Flughafenstandorte und bleibt deshalb unmittelbar bei diesen Rohdaten.
- Markdown-Dateien unter `backups/` sind Sicherungsstände und keine aktuelle Dokumentation.
- Dateien unter `outputs/` dokumentieren einzelne Arbeitsergebnisse; sie sind ebenfalls keine allgemeine Projektanleitung.
