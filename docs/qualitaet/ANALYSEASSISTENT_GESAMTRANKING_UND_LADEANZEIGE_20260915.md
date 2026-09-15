# Analyseassistent: Gesamtzuwachs und Ladeanzeige

Stand: 15.09.2026

Regelpaket: 0.8.0

Status: lokal umgesetzt; Abschlussprüfung und Testportalbereitstellung laufen

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

Die vollständige Laufzeit-, Frontend-, Release-, Linux- und Browserprüfung sowie der endgültige Testportalstand werden nach Abschluss hier ergänzt. Das Produktionsportal bleibt unverändert.
