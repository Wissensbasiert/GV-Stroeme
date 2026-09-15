# Dokumentationsübersicht

**Lokal geprüft, 15.09.2026 – Analyseassistent 0.8.1:** Schienen-Gütergruppen erscheinen standardmäßig als sieben benannte C7-Gruppen, bei ausdrücklicher NST-Frage als 20 benannte NST-2007-Abteilungen. Dreistellige Feinpositionen bleiben intern; Entwicklungsfragen übernehmen die bestätigten Randjahre. [Prüfbericht](qualitaet/ANALYSEASSISTENT_SCHIENENGÜTERGRUPPEN_20260915.md). Noch nicht im Testportal bereitgestellt.

**Testportal, 15.09.2026 – Analyseassistent 0.8.0 (`total01`):** Prognoseranglisten bilden den ausdrücklich oder standardmäßig gewünschten Gesamtzuwachs aus Straße, Schiene und Binnenschiff je Region; bei echter Unklarheit erfolgt eine Rückfrage. Ein dezenter Ladekreis ergänzt den unveränderten Livestream. 221 lokale Laufzeittests und die vollständige Release-/Linux-/Browserprüfung ohne externen Modellaufruf bestanden. [Prüfbericht](qualitaet/ANALYSEASSISTENT_GESAMTRANKING_UND_LADEANZEIGE_20260915.md).

**Testportal, 15.09.2026:** Diagrammkopfzeilen, regionale KV-Struktur und verzögerte Ladeanzeige sind im gemeinsamen Release `total01` bereitgestellt. [Prüfbericht](qualitaet/DIAGRAMMKONTEXT_UND_KV_20260915.md).

**Testportal, 14.09.2026 – `loading01`:** Relationsanfragen für 2025 nennen den verfügbaren Jahrgang 2024; Flughafenhinweise aktualisiert und Ladeanzeige ohne Layoutverschiebung über der Karte. 218 lokale Tests, vollständige Linux-Prüfung und Browserstichprobe bestanden. [Bereitstellung und Nachweis](qualitaet/LADEANZEIGE_UND_RELATIONSJAHRE_20260914.md). Nachfolgend frühere Prüfstände.

**Luftverkehr, 14.09.2026:** Die korrigierten Eurostat-Dateien sind im Testrelease `air01` bereitgestellt und auf dem Server sowie im Browser geprüft. Flughafen-Flugzahlen 2025 sind für den freigegebenen Quellenstand wieder verfügbar; Relationen weiterhin bis 2024. Die Funktionen aus `nodes02` sind enthalten. [Datenprüfung und Bereitstellung](qualitaet/LUFTVERKEHR_UPDATE_20260914.md). Nachfolgend Vorgängerstände.

**Aktuell: Version 0.7.0 im Testportal (`nodes02`).** Konkrete Flughafenverbindungen, IATA-Auswahl, London-Gruppe mit Abdeckungshinweis und fünf geprüfte Vorschaufragen. 215 lokale Tests, 13 freigegebene Modellfragen, lesende Gemini-Zweitprüfung und abschließende Linux-/Browserprüfung dokumentiert. Ein erkannter Paketierungs-Mischstand wurde zurückgerollt und durch einen konsistenten, erneut geladenen Release ersetzt. [Prüfbericht](qualitaet/ANALYSEASSISTENT_KNOTEN_VORSCHAU_20260914.md). Nachfolgend Vorgängerstände.

**Aktuell: Version 0.6.0 im Testportal.** Inland-/Auslandsfilter, passende Gesamtverkehrszeitreihe, serverseitige Modalgesamtsummen und lesbare Listen. 189 lokale Tests, zwei lesende Gemini-Prüfungen und Linux-/Browsernachprüfung dokumentiert. [Prüfbericht](qualitaet/ANALYSEASSISTENT_RAUM_SUMMEN_20260914.md). Produktion unverändert; nachfolgend Vorgängerstände.

Aktueller Stand 14.09.2026: Version 0.5.0 erschließt vorhandene Prognose-Gütergruppen, gerichtete Prognoseverbindungen, regionale NST20 sowie Hafen- und KV-Details für den KI-Chat. 176 lokale Tests, 291.300 Quellenabgleiche und Linux-/Browserabnahme bestanden; Testrelease access04 aktiv. [Prüfbericht zum Datenzugriff](qualitaet/ANALYSEASSISTENT_DATENZUGRIFF_20260914.md). Produktion unverändert. Die folgenden datierten Abschnitte dokumentieren Vorgängerstände.

Neueste Prüfung: Version 0.4.2 mit regionaler Güterzeitreihe, vollständigerem Antworttext und korrigierter Prognose-Datenladung. Der [Prüfbericht zur echten Antwortstichprobe](qualitaet/ANALYSEASSISTENT_GÜTER_UND_STICHPROBE_20260914.md) enthält die gelesenen Antworten aus acht dokumentierten Fragetypen und dem Leipzig-Dialog, Bewertung sowie aktuellen Bereitstellungsstand.

Vorgängerstand: Version 0.4.1 mit gemeinsamem Prognosevergleich mehrerer Regionen und Kennwerte, ohne Pflicht-Istjahre. [Prognose-Prüfbericht](qualitaet/ANALYSEASSISTENT_PROGNOSE_20260914.md). Die folgenden Abschnitte dokumentieren Vorgängerstände.

Seit 14.09.2026 ist Version 0.4.0 mit semantischer Auswahl, strukturierten Rückfragen und Zeitwünschen im Testportal aktiv. Aktueller Stand: [Semantik-Prüfbericht](qualitaet/ANALYSEASSISTENT_SEMANTIK_20260914.md). Den vorausgehenden Chatumbau dokumentiert der [Chat-Prüfbericht](qualitaet/ANALYSEASSISTENT_CHAT_20260914.md); die Dortmund–Bielefeld-Korrektur ist im [Prüfbericht zur Kundenantwort](qualitaet/ANALYSEASSISTENT_KUNDENANTWORT_20260911.md) hergeleitet. Produktion bleibt unverändert.

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

Der begrenzte Dialogausbau ist in [`qualitaet/ANALYSEASSISTENT_BETA_20260911.md`](qualitaet/ANALYSEASSISTENT_BETA_20260911.md) mit echtem Vorher-/Nachhervergleich dokumentiert. Für den verbindlichen Freigabestand weiterhin den Qualitätssicherungsplan beachten.

Die allgemeinen Kalenderjahr- und Anschlussregeln ab Version 0.2.2 sowie ihre Regressionen stehen in [`qualitaet/ANALYSEASSISTENT_DIALOGREGELN_20260911.md`](qualitaet/ANALYSEASSISTENT_DIALOGREGELN_20260911.md).

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
