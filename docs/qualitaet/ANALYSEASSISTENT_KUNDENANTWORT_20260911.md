# Kundenantwort und Quellenprüfung Dortmund → Bielefeld

## Befund

Die gemeldete Frage verlangt Straßen-Gütermengen für 2020 und 2024 sowie deren Entwicklung. Der lokale Vorherlauf reproduziert die beanstandete Antwort genau: Rangbehauptung bei nur einem Verkehrsträger, Ausweichen auf das letzte vorhandene Jahr 2022 und eine Veränderung von 2020 bis 2022 statt bis 2024. Mehrere allgemeine Hinweise wiederholen dieselbe Datenlücke. In der Oberfläche hatten aufeinanderfolgende Absätze keinen Abstand.

Die Originaldatei `data/raw/Straße/KBA/VE7_Verflechtung_NUTS3/ve7_2010_2024.csv` enthält für Beladeregion `DEA52` und Entladeregion `DEA41` im untersuchten Zeitraum ausschließlich 2020 und 2022. Der unabhängige CSV-Abgleich prüft sämtliche Hauptverkehrsbeziehungen und Satzarten für genau diese Endpunkte. Ergebnis: 110.050 Tonnen 2020 und 55.106 Tonnen 2022, jeweils Quellenzeichen `( )`; zugrunde liegen 21 beziehungsweise 13 Fahrzeugdatensätze. Für 2021, 2023 und 2024 fehlt die eigene Relationszeile bereits in der Rohquelle, nicht erst im Assistenten. Dies ist eine Prüfung des vorhandenen Originalbestands, keine erneute Beschaffung sämtlicher KBA-Daten.

Das zugehörige `referenzhandbuch_VE7.pdf`, Stand Dezember 2025, erklärt auf Seiten 6–7 die hochgerechnete Stichprobenerhebung und die räumliche Verdichtung bei weniger als zehn Fällen. Für zehn bis 50 Fälle kennzeichnet das KBA eingeschränkte Genauigkeit und warnt vor kaum hinreichend genauen Veränderungsraten. Das erklärt die methodische Möglichkeit fehlender einzelner Relationen; es beweist nicht die konkrete Ursache der Dortmunder Datenlücke. Eine fehlende Zeile darf deshalb weder als Nullverkehr noch als nachgewiesene Unterdrückung ausgegeben werden.

## Allgemeine Korrektur

- `relation_history` vergleicht ausschließlich das angefragte Anfangs- und Endjahr. Ein fehlendes Randjahr wird nicht durch ein Zwischenjahr ersetzt. Bei vorhandenen Randwerten bleibt ein ausdrücklich rechnerischer Vergleich zulässig; eingeschränkte Qualität wird unmittelbar eingeordnet.
- Der Verkehrsträgervergleich betrachtet das angefragte Endjahr und entsteht nur bei mehreren Verkehrsträgern. Ein einzelner Verkehrsträger wird nicht als Rangführer ausgegeben.
- Fehlende Relationszeile, nicht verfügbarer Jahrgang und unterdrückter Wert bleiben in den Ergebnisfakten und Tabellen getrennt erhalten.
- Die Kundenantwort nennt zuerst die angefragten Werte und die mögliche oder unmögliche Veränderung. Bei fehlenden Straßenrelationen folgt die belegte Erklärung zur Stichprobe, einschließlich der unbekannten konkreten Ursache.
- Jahresreihen mit mehr als zwei Werten sind als Details aufklappbar. Doppelte allgemeine Warnungen und der redundante Einheitenhinweis entfallen bei dieser Funktion. Die Gebietsannahme und die konkrete Qualitätseinschränkung bleiben erhalten.
- Die Modellformulierung muss bei Jahresvergleichen sämtliche vorbereiteten Antwortabsätze einmal in Reihenfolge erhalten. Einzelne Tabellenzellen werden hierfür nicht als Ersatzantwort angeboten. Bei Verletzung bleibt die geprüfte Serverantwort bestehen.
- Die bearbeitbare CSS-Quelle setzt Abstände unter der Antwortüberschrift und zwischen Absätzen. Das CSS-Auslieferungsartefakt wurde daraus neu erzeugt.

## Nachweise und Grenze

`outputs/analyseassistent_kundenantwort_20260911/before.json` enthält die reproduzierte Ausgangsantwort, die passenden Originalzeilen und die CSV-Prüfsumme. `after_local.json` enthält die korrigierte lokale Antwort.

Sieben gezielte Regressionen in `tests/analyseassistent/test_customer_history.py` bestehen: unabhängiger Originalabgleich, Antwortstruktur, fehlende Randjahre einschließlich vollständig fehlender Reihen, berechenbare Randwerte trotz innerer Lücke, Null-Ausgangswerte, Erhalt unterschiedlicher Fehlzustände, Einjahresauswahl und verpflichtende Reihenfolge der Modellbelege. Der Prüfer gruppiert diese Kontrollen in sieben Testmethoden.

Nach ausdrücklicher Zustimmung wurde genau ein echter Requesty-Antwortaufruf ausgeführt: `after_requesty.json` bestätigt `grounded_narrative`, keine verworfene Formulierung, 3.024 Tokens, 0,0029502 USD laut Anbieter und keine Kundenbuchung. Die Zuordnung der Frage erfolgte ohne Planmodell. Die Prüfung verwendet keine Sollantwort im Modellkontext.

`scripts/validation/validate_assistant_customer.cjs <lokaler Portalrelease> <gespeicherte Antwort.json> <Ausgabeordner>` zeigt diese gespeicherte echte Modellantwort über den tatsächlichen Chatclient. `browser_final/report.json` und die visuell geprüften Desktop-/Mobilbilder belegen sichtbare Randwerte, fehlende Ersatzrate, Absatzabstände, zunächst geschlossene und vollständig aufklappbare fünf Jahreswerte sowie fehlenden horizontalen Seitenüberlauf. Der lokale Portalrelease beta06 stellt den bestehenden Client bereit; das aktuelle neu gebaute CSS wird eigens zugeladen und per Prüfsumme dokumentiert. Die Browserprüfung erzeugt keine Modellaufrufe und keine Portalbuchung.

`targeted_validation.json` bestätigt abschließend 13/13 Prüfungen am aktuellen Stand: die sieben neuen Kontrollen und sechs bestehende Regressionen für Mehrjahresdialog, belegte Modellantwort, fehlende Relation und Abwehr unbelegter Aussagen. Laufzeit rund 13,5 Sekunden, keine externen Aufrufe. Der zuvor gestartete breite Gesamtprüflauf wurde nach mehr als zwölf Minuten ohne Abschluss beendet. Er ist kein bestandener Gesamtnachweis und erzeugt keine aktuelle Freigabedatei.

Die Änderungen sind lokal. Dieser Nachweis belegt keine Bereitstellung im Testportal und keine vollständige fachliche Abnahme aller freien Chatfragen. Vor einer Releasefreigabe bleibt ein abgeschlossener vollständiger Laufzeitnachweis erforderlich.
