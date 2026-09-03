# Dokumentationsübersicht

Diese Seite ist der zentrale Einstieg in die Projektdokumentation. Sie trennt verbindliche Betriebs- und Qualitätshinweise von fachlichen Konzepten und noch nicht umgesetzten Planungen.

## Welche Datei ist wofür maßgeblich?

| Fragestellung | Zuerst lesen | Ergänzend |
|---|---|---|
| Daten aktualisieren oder neu aufbereiten | [`betrieb/ANLEITUNG_DATENAKTUALISIERUNG.md`](betrieb/ANLEITUNG_DATENAKTUALISIERUNG.md) | [`qualitaet/QUALITÄTSSICHERUNGSPLAN.md`](qualitaet/QUALITÄTSSICHERUNGSPLAN.md) |
| Aufbau, Technik, Datenfluss oder Betrieb verstehen | [`betrieb/HANDBUCH_SYSTEMDOKUMENTATION.md`](betrieb/HANDBUCH_SYSTEMDOKUMENTATION.md) | [`betrieb/README_MAINTENANCE.md`](betrieb/README_MAINTENANCE.md) |
| Frontend ändern und neu zusammensetzen | [`betrieb/README_MAINTENANCE.md`](betrieb/README_MAINTENANCE.md) | [`../scripts/README.md`](../scripts/README.md) |
| Datenmodell, Begriffe und fachliche Struktur klären | [`fachkonzept/DATA_STRUCTURE_AND_CONCEPT.md`](fachkonzept/DATA_STRUCTURE_AND_CONCEPT.md) | `data_catalog.json` im Projektstamm und Metadaten der jeweiligen Rohquelle |
| Aktuellen Prüf- oder Freigabestand beurteilen | [`qualitaet/QUALITÄTSSICHERUNGSPLAN.md`](qualitaet/QUALITÄTSSICHERUNGSPLAN.md) | [`qualitaet/design-qa.md`](qualitaet/design-qa.md) nur für den dokumentierten Design-Prüfstand |
| Dashboard, Navigation oder Flugverkehr weiterentwickeln | [`roadmap/ROADMAP_DASHBOARD_WEITERENTWICKLUNG.md`](roadmap/ROADMAP_DASHBOARD_WEITERENTWICKLUNG.md) | Fachkonzept und Qualitätssicherungsplan |
| Analyseassistent, Portal oder Basis-/Premiumlogik planen | [`roadmap/ROADMAP_ANALYSEASSISTENT_PORTAL.md`](roadmap/ROADMAP_ANALYSEASSISTENT_PORTAL.md) | Dashboard-Roadmap bei Berührungspunkten zur Oberfläche |

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