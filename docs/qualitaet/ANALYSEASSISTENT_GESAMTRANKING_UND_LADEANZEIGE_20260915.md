# Analyseassistent: Gesamtzuwachs und Ladeanzeige

Stand: 15.09.2026

Regelpaket: 0.8.0

Status: im Testportal bereitgestellt und abschließend geprüft

## Anlass und Befund

Die Frage „Welche Region gewinnt absolut gesehen am meisten an Güterverkehr bis 2040 zu?“ wurde als Rangliste des Straßengüterverkehrs beantwortet. Auch die anschließende Klarstellung, dass der Gesamtzuwachs gemeint war, änderte die Auswahl nicht. Die genannten Werte waren innerhalb der Straße rechnerisch richtig, beantworteten aber nicht den gewünschten Gesamtumfang.

Ursache war eine Lücke zwischen Sprachverständnis und Datenvertrag: Die Modellanweisung sah ohne genannten Verkehrsträger alle drei Landverkehrsträger vor, die Ranglistenfunktion erlaubte technisch jedoch nur genau einen Verkehrsträger. Der gespeicherte Straßenkontext konnte deshalb fortgeschrieben werden. Die nachgelagerte Antwortprüfung bestätigte die Zahlen gegen diese technisch ausgewählten Straßenfakten, nicht gegen die ursprüngliche Bedeutung der Frage.

## Umsetzung

- Die Prognoserangliste akzeptiert eine geprüfte Liste aus Straße, Schiene und Binnenschiff.
- Mehrere ausgewählte Verkehrsträger werden je Region vollständig summiert, bevor absolute und relative Änderung sowie Rangfolge berechnet werden.
- Gesamtformulierungen wie „Gesamtzuwachs“, „gesamter Güterverkehr“, „insgesamt“ und „alle Verkehrsträger“ werden zusätzlich serverseitig auf alle drei Landverkehrsträger gebunden. Damit kann ein alter Einzelmodus die ausdrückliche Klarstellung nicht überschreiben.
- Bei einer neuen Rangfrage ohne erkennbaren Gesamt- oder Einzelverkehrsträger und einer dennoch vom Modell vorgeschlagenen Einzelauswahl fragt der Assistent gezielt nach Gesamtverkehr oder Einzelverkehrsträger.
- Auswahlhinweis, Antwortbelege und Tabellenhinweise nennen den tatsächlich verwendeten Verkehrsträgerumfang und die Summierung je Region.
- Im Antwortbereich bleibt während einer laufenden Anfrage ein kleiner, zurückhaltender Ladekreis sichtbar. Fortschrittsmeldungen und absatzweiser Livestream bleiben unverändert. Bei reduzierter Bewegung im Betriebssystem wird die Drehbewegung abgeschaltet.

Die serverseitige Absicherung ersetzt nicht das Sprachmodell. Sie kontrolliert eine fachlich besonders folgenreiche Auswahl, nachdem das Modell die Nutzerfrage semantisch ausgewertet hat.

## Fachliche Referenzwerte

Für Menge, beide Richtungen und Straße + Schiene + Binnenschiff ergeben sich aus dem gebundenen VP2040-Bestand folgende fünf größten absoluten Zuwächse:

| Rang | Region | Prognosebasis 2019 | Prognose 2040 | Absolute Änderung |
|---:|---|---:|---:|---:|
| 1 | Hamburg | 177.916.293 t | 216.712.093 t | +38.795.800 t |
| 2 | Nürnberg, Kreisfreie Stadt | 45.803.154 t | 67.027.814 t | +21.224.660 t |
| 3 | Köln, Kreisfreie Stadt | 69.558.212 t | 86.793.748 t | +17.235.536 t |
| 4 | München, Kreisfreie Stadt | 55.924.406 t | 72.451.637 t | +16.527.231 t |
| 5 | Ludwigsburg | 38.967.768 t | 52.930.996 t | +13.963.228 t |

Die Werte vergleichen ausschließlich die Modellstände `2019_BASE` und `2040_P1`. Sie sind keine beobachtete Entwicklung und keine sichere Vorhersage. Innerregionale Verkehre werden bei der hier verwendeten Richtungsangabe gemäß VP-Zählweise einmal berücksichtigt.

## Daten- und Prüfstand

- B04–B06 neu aufgebaut: `c204d6eb8902125a2f55`; Partnerprüfung 10/10, Hauptprüfung 202/202 bestanden.
- Abhängiger Assistenten-Unterstützungsbestand neu aufgebaut: `109e02e6eee8f8489d6dde97`; 34.270 KV-Datensätze, 3.984 Güterprofile und 32.296 Quellenvergleiche.
- Dashboard-Zugriffsbestand nach dem gemeinsamen Ausgangscommit neu aufgebaut: `f57cb170ea43c579e6b6`; 291.300 Zellen geprüft, keine unbekannten Hauptfelder.
- Keine externen Modellaufrufe und keine Kontingentbuchung. Die Prüfung bewertet Datenfunktion, Auswahlregeln, Antwortbelege und Oberfläche deterministisch.

## Abschlussprüfung und Bereitstellung

- 221/221 lokale Laufzeittests bestanden; keine Fehler, keine externen Modellaufrufe.
- Frontend-Build, JavaScript-/JSON-Syntax, UTF-8-Inhalte, Änderungsprüfung, 896 Auslieferungsdateien sowie Lade-, Fehler-, Zeitbegrenzungs- und Abbruchfälle bestanden.
- Die synthetische Chrome-Prüfung am vollständigen Release bestätigt genau einen Ladekreis und `aria-busy` während der gehaltenen Anfrage, die vorhandenen Fortschritts-/Antwortzustände sowie das vollständige Entfernen des Ladekreises nach dem Ergebnis. Zwölf Oberflächen- und Dialogprüfungen bestanden; keine Portalbuchung.
- GitHub `main`: Implementierung `5ef96df`, aufbauend auf dem zuvor abgeglichenen Commit `e41ff90`.
- Aktiver Testrelease: `portal-test-20260915-gueterstroeme-total01`, aus dem zuvor aktiven und bytegenau rekonstruierten `portal-test-20260915-mdc-license01` erstellt. 1.732 unveränderte Dateien wurden serverseitig unabhängig kopiert; 52 geänderte Nutzdateien plus Manifest wurden übertragen. Alle 1.784 Dateien mit insgesamt 888.940.241 Bytes bestanden den Abgleich. Manifest: `3b66223972ae62e8ff7652aa298a0dce9dc0cb187bc5db45a7066c6cf6ed220e`.
- Die Linux-Nachprüfung bestätigt die private Laufzeit, Prognose-/Güter-/Knoten-/Gesamtsummenregressionen, 291.300 Dashboard-Zellen und eine lesende Datenbanktransaktion. Datenkennung: `24a4c8cee90c6f866fdba5a7`. API, Datenbank und monatliche KitaNavigator-Aufgabe 30833 sind bereit; temporäre Prüfmittel wurden entfernt.
- Eine abschließende Inventur bestätigt `total01` als aktiven Testrelease, unveränderte Produktion und einen gesunden Portalzustand.

Ein echter Modelllauf wurde bewusst nicht ausgeführt, weil hierfür kein gesonderter Kosten-/Datenauftrag vorlag. Die Korrektur ist durch Daten-, Auswahl-, Ergebnis-, Linux- und Browserprüfungen abgedeckt; beliebige freie Modellformulierungen sind damit nicht vollständig garantiert.

Auf dem Testserver sind neben dem aktiven Release derzeit fünf ältere Releases vorhanden. Ein geprüfter, nicht ausgeführter Aufbewahrungsplan würde `mdc-license01` und `loading01` als zwei Rückfallstände behalten und `air01`, `nodes02` sowie `scope01` entfernen. Eine Löschung war nicht Teil dieses Auftrags und wurde daher nicht ausgeführt.

Das Produktionsportal blieb unverändert.
