# Analyseassistent: Aufbereitungsplan für alle 45 Testfälle

**Stand: 09.09.2026 · Fortschreibung nach Gemini-B01–B03-Zweitprüfung: B01 (159), B02 (178), B03 (201) sowie B04–B06 (199 Hauptprüfungen und zehn zusätzliche Kontrollen) erneut lokal mit Quellen-/Vergleichsgrenzen bestätigt. Aktuelle Kennungen: Roadmap Abschnitt 23. Der Terminalfall mit offenen Raumbezügen ist eine zusätzliche Anforderung in Abschnitt 22, keine Erweiterung der 45 festgelegten Modellfälle. B07 bleibt offen. T22-Sollannahme nach Quellenprüfung korrigiert.**

Aktuelle Schritte, Dateien und Datenstand stehen zentral in der Roadmap: B01 in Abschnitt 17, B02 in Abschnitt 19, B03 in Abschnitt 20 und B04–B06 einschließlich Quellenbefunden in Abschnitt 21. Die folgenden Abschnitte dokumentieren die ursprüngliche Planung; die damaligen Aussagen zur noch nicht begonnenen Umsetzung sind historisch. Die T22-Kontrollannahme wurde unten ausdrücklich anhand der Rohquelle berichtigt.

Die Arbeit wird auf dem vollständig erhaltenen Terra-Prüflauf und dem vorbereiteten Regelpaket fortgesetzt. Diese Datei ordnet alle 45 vorhandenen Testfälle einer Quelle, dem benötigten Aufbereitungsschritt und einer fachlichen Kontrollrechnung zu. Die [strukturierte Fassung](ANALYSEASSISTENT_AUFBEREITUNGSPLAN.json) enthält zusätzlich die Fragen und Parameter des bestehenden Katalogs.

## 1. Wiederaufgenommener Arbeitsstand

- Alle 23 mit Prüfsummen protokollierten Artefakte des Terra-Laufs wurden erneut gelesen und unverändert vorgefunden. Die 45 Erstantworten, 16 Kontrollantworten und Einzelbewertungen sind vorhanden. Die Teilagenten sind abgeschlossen.
- Das Regelpaket enthält alle fünf Dateien, 26 Regeln und 15 Funktionsverträge. Es ist weiterhin deaktiviert; die auf Nutzerrückmeldung zurückgenommenen festen Zeitgrenzen sind nicht wieder eingesetzt.
- Eine Pipeline- oder Serverumsetzung wurde zuvor nicht begonnen. Offen geblieben war der Übergang von der Besprechung zur konkreten Aufbereitungsplanung.
- Ein Datenverlust oder unvollständiger gespeicherter Terra-Lauf ist damit nicht festzustellen. Die Ursache eines wahrgenommenen App-/Sprachabbruchs lässt sich aus diesen Dateiprüfungen nicht bestimmen.

## 2. Bedeutung für das heutige Dashboard

Die Bewertungen des Terra-Berichts betreffen Modellantworten, nicht automatisch die entsprechenden Dashboardberechnungen. Im bestehenden Quellcode wird der Deutschlandwert aus der nationalen Datenbasis geladen; der Steckbrief nennt Versand/Empfang einschließlich Binnenverkehr. Terras gemischte Regionssumme und seine falsche Beschreibung als reiner Außenverkehr sind deshalb keine Nachweise derselben Fehler in diesen Anzeigen. Es wurde keine erneute vollständige Dashboardabnahme durchgeführt.

Eine konkrete Aufbereitungslücke sind dagegen die KBA-Quellenkennzeichen: Die aktuelle OD-Aufbereitung übernimmt Mengen, Leistung und Fahrten, aber nicht die zugehörigen ZS-Felder. Fehlende Kennzeichen machen die Zahl nicht automatisch falsch, verbergen jedoch ihre Einschränkung. B01 muss diese Information erhalten. Ob und wie sie in bestehenden Ansichten zusätzlich sichtbar werden muss, wird anhand der betroffenen Werte gesondert geprüft. Diese Planung verändert die Anzeige nicht.

Gekürzte Weblisten sind für die schnelle Anzeige vorgesehen. Sie sind keine vollständige Grundlage für beliebige neue Assistentenfragen. Ebenso enthält der Regionalbestand unterschiedliche Gebietsebenen, die eine neue Abfrage ausdrücklich filtern muss. Solche Grenzen sind bei einer Serverabfrage zu behandeln; eine bloße Summierung aller verfügbaren Einträge ist keine geeignete Ersatzlogik.

## 3. Aufbau der zusätzlichen Analysebestände

Die schlanken Browserpakete können erhalten bleiben. Zusätzlich werden aus denselben vorhandenen Rohquellen serverinterne Bestände vorbereitet. Die Formate sind noch nicht entschieden; maßgeblich sind schnelle gezielte Abfragen, nachvollziehbare Quellenstände und eine wartbare Aktualisierung. Neue Umwelt-, Kosten-, Kapazitäts- oder betriebliche Transportkettenprodukte werden nicht aufgebaut.

| Reihenfolge | Arbeitsblock | Konkretes Ergebnis | Abnahme |
|---|---|---|---|
| 1 | B01 und notwendige Jahresprüfung aus B02 | Vollständige OD mit Verfügbarkeit, Qualitätskennzeichen, Quellenfassung, Raum-/Zeit-/Richtungsbezug; verfügbare Jahresabdeckung | Gleiche Mengen bei gleicher Abgrenzung; fehlend/Null/eingeschränkt bleiben verschieden; Fälle T04–T06, T19–T21 und T42/T44 |
| 2 | B03 vorhandene Güter-/Straßendetails | SGV-Feinpositionen; KBA VD2-Klassen und VD3c-NST-20 auf amtlicher Raumebene | Kontrollwerte T19/T21/T40/T41; keine Verfeinerung einer Straßen-OD oder einer NUTS-3-C-Gruppe |
| 2 | B06 veröffentlichte Knotenrelationen | Vollständige publizierte Flughafen-/Hafenpartner mit Länderfilter und passenden Nennern | T35 internationaler Nenner 662.332,0 t; Hafenvergleich T36 erst nach Hafenauswahl |
| 3 | B02 Monatsdaten und Vergleichbarkeit | Monatstabellen mit Abdeckung, Quellen-/Gebietsstand und geprüften Jahressummen | T10/T39: reale Monate vollständig prüfen; synthetische Beispiele allein reichen nicht |
| Nach Fallbedarf | B04/B05 | Ganze Regionsverbünde und nationale Verkehrsbeziehungen mit korrekter Zählung | T08/T26 innen/außen/eindeutig; T27 nationale Randsumme; T43 gleichrangige Räume |
| Nach geklärtem Teststand | B07 | Vorhandenes passendes Gemeinde-Monatsabbild oder gesondert autorisierter gezielter Abruf | T37/T38: bestätigter AGS, Richtung und Monatspaar; keine bundesweite Komplettabfrage |

Reihenfolge bezeichnet Abhängigkeiten und Nutzen, keine Reduktion des Testumfangs: Alle 45 Fälle bleiben zugeordnet. B04/B05 sind früher einzubeziehen, sobald eine Abfrage ihre Raum- oder nationale Abgrenzung braucht. Die bereits vorhandenen Datenprodukte D01/D03/D05/D06 werden nicht allein wegen der neuen Schnittstelle fachlich neu erfunden.

## 4. Quellen und technische Leitplanken

Quellen-IDs entsprechen dem [Detailkonzept](ANALYSEASSISTENT_ETAPPE1_DETAILKONZEPT.md). Die folgenden Pfade wurden bei der Wiederaufnahme als vorhanden geprüft. Verfügbarkeit eines Ordners belegt noch nicht die Vollständigkeit jeder denkbaren Kombination.

| Quelle | Vorhandene Grundlage |
|---|---|
| D01 | [data/processed/web_summary_by_region.json](../../data/processed/web_summary_by_region.json); [data/raw/Straße/KBA/Versand_VE12_NUTS3_7Gueter/ve12_2010_2024.csv](../../data/raw/Straße/KBA/Versand_VE12_NUTS3_7Gueter/ve12_2010_2024.csv); [data/raw/Straße/KBA/Empfang_VE13_NUTS3_7Gueter/ve13_2010_2024.csv](../../data/raw/Straße/KBA/Empfang_VE13_NUTS3_7Gueter/ve13_2010_2024.csv) |
| D02 | [data/processed/fact_od_flows.parquet](../../data/processed/fact_od_flows.parquet); [data/raw/Straße/KBA/VE7_Verflechtung_NUTS3/ve7_2010_2024.csv](../../data/raw/Straße/KBA/VE7_Verflechtung_NUTS3/ve7_2010_2024.csv) |
| D03 | [data/processed/national_benchmarks.json](../../data/processed/national_benchmarks.json) |
| D04 | [data/raw/SGV OpenData](../../data/raw/SGV OpenData); [data/raw/IWW OpenData](../../data/raw/IWW OpenData); [data/raw/Straße/KBA](../../data/raw/Straße/KBA); [data/crosswalks/crosswalk_nst_vp2040.json](../../data/crosswalks/crosswalk_nst_vp2040.json) |
| D05 | [data/processed/web_forecast_2040.json](../../data/processed/web_forecast_2040.json); [data/processed/web_forecast_core.json](../../data/processed/web_forecast_core.json); [data/raw/VP2040](../../data/raw/VP2040) |
| D06 | [data/processed/web_intermodal.json](../../data/processed/web_intermodal.json) |
| D07 | [data/processed/web_maritime.json](../../data/processed/web_maritime.json); [data/raw/MRTM OpenData](../../data/raw/MRTM OpenData) |
| D08 | [data/processed/web_airfreight.json](../../data/processed/web_airfreight.json); [data/raw/Luftverkehr/estat_avia_gor_de.tsv](../../data/raw/Luftverkehr/estat_avia_gor_de.tsv) |
| D09 | [js/modules/toll.js](../../js/modules/toll.js); [scripts/toll](../../scripts/toll) |
| D10 | [data/processed/nuts3_de_2024.geojson](../../data/processed/nuts3_de_2024.geojson); [data/raw/NUTS](../../data/raw/NUTS); [data/crosswalks](../../data/crosswalks) |

D09 bezeichnet den bestehenden Zugang und lokale Aufbereitungshilfen. Ein passendes eingefrorenes Abbild für die noch unbestimmten Testgemeinden und Monate ist damit nicht nachgewiesen. Bestehende Auszüge zuerst auf ihre Eignung prüfen; in dieser Wiederaufnahme wurde nichts live abgerufen.

Die Kopfzeilen der lokalen SGV-, IWW- und MRTM-Dateien 2024 enthalten Monatsfelder. Das bestätigt die grundsätzlich vorhandene Dimension, noch nicht zwölf vollständige Monate für eine konkrete Güter-/Raumauswahl. Die aktive SGV-Aufbereitung liest Latin-1; eine vollständige UTF-8-Lesung der betreffenden Rohdatei schlägt fehl. Ein ASCII-kompatibler Dateikopf beweist keine UTF-8-Kodierung des Inhalts. Rohquellen unverändert erhalten und den Zeichensatz ausdrücklich behandeln; neue Texte und Exporte UTF-8-sicher erzeugen.

Für jedes neue Analyseprodukt mitführen: Originalquelle und Datenfassung, Rohcode als Text, Regionsebene/Gebietsstand, Jahr/Monat, Richtung, Modus, Güterklassifikation, Einheit/Skalierung, Population/Inland-Gesamt, Zählweise, numerischer Verfügbarkeitsstatus und Qualitätsflag. Bei Prozentwerten gehören Nenner und dessen veröffentlichte bzw. vollständige Grundgesamtheit zum Ergebnis. Keine fehlenden Komponenten durch Default-Null ersetzen.

## 5. Zuordnung aller 45 Testfälle

„Bestand nutzen“ bedeutet: keine neue externe Quelle und kein zwingender neuer fachlicher Rohdatenwürfel; die kontrollierte Serverabfrage muss dennoch entwickelt werden. „Synthetisch“ bezeichnet einen Regeltest, keinen Nachweis einer realen Datenreihe. „Leistungsgrenze“ wird durch eine korrekte begrenzte Antwort erfüllt. Ein Paketverweis ist Arbeitsbedarf, kein Nachweis seiner Umsetzung.

| Fall / Thema | Quellen | Pakete | Arbeitsart |
|---|---|---|---|
| T01 – Kernbefunde für eine Verwaltungsvorlage | D01, D03, D04, D05 | B01, B02 | Bestand nutzen |
| T02 – Fehlende Regionsauswahl | D01 | — | Eingabe klären |
| T03 – Belegtes Profil statt Standortversprechen | D01, D05 | B01 | Bestand nutzen |
| T04 – Hamburgs wichtigste Straßenpartner | D02, D04 | B01 | Aufbereitung ergänzen |
| T05 – Konkrete Verbindung statt Treffer in der Top-Liste | D02, D04 | B01 | Aufbereitung ergänzen |
| T06 – Fehlender Top-Treffer und Gleichstand | D02, D04 | B01 | Synthetische Regelprüfung |
| T07 – Duisburg und Magdeburg im gemeinsamen Jahr | D01, D04, D10 | B01, B04 | Bestand nutzen |
| T08 – Frei abgegrenzter Wirtschaftsraum | D02, D10 | B01, B04 | Synthetisch und Eingabe klären |
| T09 – Ungeeignete Vergleichsräume und Ranggleichheit | D01, D10 | B04 | Synthetisch und Eingabe klären |
| T10 – Magdeburger Schienenentwicklung seit 2016 | D01, D04, D10 | B02 | Aufbereitung ergänzen |
| T11 – Zeitvergleich mit Null und fehlendem Basiswert | D01, D02, D04 | B02 | Synthetische Regelprüfung |
| T12 – Entwicklung erklären ohne unbelegte Ursache | D04, D10 | B02 | Eingabe klären |
| T13 – Absolutes und relatives Änderungsranking | D01, D02, D04, D10 | B02, B04 | Synthetische Regelprüfung |
| T14 – Kleine Ausgangswerte im Ranking | D01, D02 | B01, B02 | Synthetische Regelprüfung |
| T15 – Mehr Schienenanteil trotz weniger Schienenmenge | D01, D03 | B02 | Synthetische Regelprüfung |
| T16 – Regionale Straßen-Güterstruktur | D01, D04 | B01, B03 | Bestand nutzen |
| T17 – NST-20 auf NUTS-3 im Straßenmodul | D01, D04 | B03 | Begrenzte Alternative |
| T18 – Aktuelle Güterzuordnung statt veralteter Labels | D04, D05 | B03 | Bestand nutzen |
| T19 – Schienengütergruppen Köln → Hamburg | D02, D04 | B01, B03 | Aufbereitung ergänzen |
| T20 – Güter auf einer Straßenverbindung | D02, D04 | B01 | Begrenzte Alternative |
| T21 – Feinere Schienengüter auf der richtigen Richtung | D04 | B01, B02, B03 | Aufbereitung ergänzen |
| T22 – Nationaler Modal Split nach Verkehrsleistung | D03, D04 | B05 | Bestand nutzen |
| T23 – Unvollständiges Modal-Split-Jahr | D03 | — | Datenlücke ausgeben |
| T24 – Regionaler Modal Split mit passendem Nenner | D01 | B01 | Bestand nutzen |
| T25 – Versand und Empfang sind keine Leerfahrten | D01, D02, D04 | B01, B05 | Bestand nutzen |
| T26 – Binnenverkehr und örtlicher Transit | D02, D10 | B01, B04 | Synthetische Regelprüfung |
| T27 – Nationaler Transit aus vorhandenen Rohquellen | D03, D04 | B05 | Aufbereitung ergänzen |
| T28 – Größter prognostizierter Schienenzuwachs | D05, D10 | B04 | Bestand nutzen |
| T29 – Ist-Entwicklung neben der Prognose | D01, D05, D10 | B02 | Bestand nutzen |
| T30 – Vorhandene Prognose mit Nullwerten und Szenariogrenze | D05 | — | Synthetisch und Leistungsgrenze |
| T31 – Intermodale Teilmärkte getrennt | D06 | — | Bestand nutzen |
| T32 – Regionaler intermodaler Anteil im Versand | D06 | — | Bestand nutzen |
| T33 – Statistischer KV ist kein Verlagerungspotenzial | D06 | — | Leistungsgrenze |
| T34 – Flughafenprofil mit unterschiedlichen verfügbaren Jahren | D08 | — | Datenlücke ausgeben |
| T35 – Veröffentlichte Luftfrachtpartner und richtiger Nenner | D08 | B01, B06 | Aufbereitung ergänzen |
| T36 – Seehafenumschlag, TEU und Vergleichsjahre | D07 | B06 | Eingabe klären |
| T37 – Mautfahrten nach Richtung | D09 | B07 | Synthetisch; realer Stand offen |
| T38 – Vorjahresmonat und fehlende Angaben | D09 | B07 | Synthetisch; realer Stand offen |
| T39 – Monatliche Güterspitzen | D04 | B02, B03 | Synthetisch; Aufbereitung ergänzen |
| T40 – Entfernungsstufen aus vorhandenen Rohdaten | D04 | B03 | Aufbereitung ergänzen |
| T41 – Vorhandene VD3c-Details auf NUTS-2 | D04 | B01, B03 | Aufbereitung ergänzen |
| T42 – Null, fehlend und Quellenkennzeichen | D02, D04 | B01, B03 | Synthetische Regelprüfung |
| T43 – Regional- und Deutschlandwerte widersprechen sich scheinbar | D01, D02, D03, D04, D10 | B01, B04, B05 | Bestand nutzen |
| T44 – Reproduzierbare Analyse und belegte Kurzfassung | D01, D02, D04, D10 | B01 | Bestand nutzen |
| T45 – Fragen außerhalb des bestätigten Umfangs | D01, D02, D06 | — | Leistungsgrenze |

## 6. Aufbereitung und Kontrollrechnung je Fall

### T01 – Kernbefunde für eine Verwaltungsvorlage

**Aufbereitung:** Profil aus vorhandenen Teilkennzahlen mit Quellen-, Binnen- und Prognosevertrag bereitstellen.

**Kontrolle:** 108.215.313,5 t; Saldo −17.549.997,9 t; VP 115.374.997→103.871.423 t separat.

### T02 – Fehlende Regionsauswahl

**Aufbereitung:** Keine zusätzliche Datenaufbereitung; Region und dann Jahr/Umfang eindeutig bestimmen.

**Kontrolle:** Keine beliebige Regionszahl; Versand nicht als lokale Produktion auslegen.

### T03 – Belegtes Profil statt Standortversprechen

**Aufbereitung:** Belegte Profilkennzahlen als Aussagen mit Quellen und Zählweise bereitstellen.

**Kontrolle:** Keine unbewertete Standortwertung; Zahlen wie T01 und Binnenhinweis erhalten.

### T04 – Hamburgs wichtigste Straßenpartner

**Aufbereitung:** Vollständige Hamburger Außenrelationen mit ZS je Kennzahl verarbeiten; Partner vor Rangbildung aggregieren.

**Kontrolle:** Top 5 unverändert; Nenner 55.473.138 t; Kennzeichen bei 21.167.732 t Nenneranteil erhalten.

### T05 – Konkrete Verbindung statt Treffer in der Top-Liste

**Aufbereitung:** Genaues OD-Paar und Gegenrichtung statt Top-Datei; Zeilenverfügbarkeit pro Modus erhalten.

**Kontrolle:** IWW 1.947/1.189 t; fehlende Straßen-/Schienenzeilen nicht 0.

### T06 – Fehlender Top-Treffer und Gleichstand

**Aufbereitung:** Vollständige OD-Auswahl und Ranggleichstand als allgemeine Abfragelogik.

**Kontrolle:** A/B/C bei Top 2; Nenner 710 t; D mit 10 t trotz fehlendem Top-Treffer abfragbar.

### T07 – Duisburg und Magdeburg im gemeinsamen Jahr

**Aufbereitung:** Zwei gleichrangige Einzelregionen mit gemeinsamem Jahr; alle sieben Gütergruppen und gleiche Zählweise.

**Kontrolle:** Duisburg 108.215.313,5 t, Magdeburg 23.180.902,5 t; Strukturanteile gegen Regionalwerte.

### T08 – Frei abgegrenzter Wirtschaftsraum

**Aufbereitung:** Liste ganzer Regionen bestätigen; Innen- und Außenrelationen aus OD getrennt bilden.

**Kontrolle:** A+B: intern 100, externer Versand 40, Empfang 60, eindeutig 200 t; keine Kreisanteilsverteilung.

### T09 – Ungeeignete Vergleichsräume und Ranggleichheit

**Aufbereitung:** Raumtyp und Vergleichszweck prüfen; ungleiche Einheiten getrennt behandeln.

**Kontrolle:** 200/100/100 ergibt 1/2/2; Stadt und Knoten nicht gemeinsam ranken.

### T10 – Magdeburger Schienenentwicklung seit 2016

**Aufbereitung:** Jahresreihe vorhanden; Monatsabdeckung, Gebietsstand und Revision je Jahr ergänzen.

**Kontrolle:** Zehn Magdeburger Jahreswerte erhalten; Sprünge 2018/19 und 2024/25 markieren, Ursachen offenlassen.

### T11 – Zeitvergleich mit Null und fehlendem Basiswert

**Aufbereitung:** Fehlwert- und Nullbasisregeln für Zeitvergleich.

**Kontrolle:** 0→10 absolut +10, Rate undefiniert; 10→0 −100 %; fehlend ohne Rate.

### T12 – Entwicklung erklären ohne unbelegte Ursache

**Aufbereitung:** Konkrete Reihe bestätigen, dann Abdeckungs-/Gebiets-/Klassifikationsnachweise aus vorhandenem Material.

**Kontrolle:** Befund und belegte Erfassungsänderung trennen; unbekannte Ursache bleibt unbekannt.

### T13 – Absolutes und relatives Änderungsranking

**Aufbereitung:** Vergleichbare Auswahl beider Jahre und getrennte absolute/relative Rankings.

**Kontrolle:** A führt absolut, D relativ mit −100 %; fehlende Basis ausschließen und benennen.

### T14 – Kleine Ausgangswerte im Ranking

**Aufbereitung:** Basiswerte und explizite Mindestbasis als Abfrageparameter erhalten.

**Kontrolle:** 1→10 = +900 %/+9 t; 1.000→1.500 = +50 %/+500 t; kein versteckter Ausschluss.

### T15 – Mehr Schienenanteil trotz weniger Schienenmenge

**Aufbereitung:** Anteile und Mengen je Zeitstand getrennt berechnen.

**Kontrolle:** 20→18 t Schiene, Anteil 20→30 %, +10 Prozentpunkte; kein Verlagerungsnachweis.

### T16 – Regionale Straßen-Güterstruktur

**Aufbereitung:** Regionale C-Gruppen aus VE12/13, nicht aus Straße ALL im Regional-Parquet.

**Kontrolle:** Versand 26.371.111 t, Empfang 22.134.701 t; Rangfolge je Richtung korrekt.

### T17 – NST-20 auf NUTS-3 im Straßenmodul

**Aufbereitung:** NST-20 auf Straße NUTS-3 bleibt unbelegt; C-Gruppen anbieten, VD3c auf NUTS-2 nur ausdrücklich separat.

**Kontrolle:** Keine künstliche 20er-Aufteilung; andere Raumebene/Population sichtbar.

### T18 – Aktuelle Güterzuordnung statt veralteter Labels

**Aufbereitung:** Verbindliches Klassifikationsregister aus aktuellem Crosswalk; alte Dimensionsdatei nicht als Autorität.

**Kontrolle:** 031→C1; NST14/VP140→C6; alle sieben Gruppen richtig zugeordnet.

### T19 – Schienengütergruppen Köln → Hamburg

**Aufbereitung:** C-Gruppen-OD mit Fehlstatus; vorhandene SGV-Feinpositionen für Rohkontrolle erhalten.

**Kontrolle:** C1 231, C7 199.620 t; Summe belegter Gruppen 199.851 t; C2–C6 ohne Nullnachweis.

### T20 – Güter auf einer Straßenverbindung

**Aufbereitung:** Straßen-OD mit Gesamtmenge und ZS aus VE7; keine Güteraufteilung auf dieser Verbindung.

**Kontrolle:** 67.757 t mit eingeschränktem Aussagewert; kein abgeleitetes Straßen-OD-Güterdetail.

### T21 – Feinere Schienengüter auf der richtigen Richtung

**Aufbereitung:** SGV-Feinpositionen je Richtung und Jahr einschließlich Monats-/Fehlwertstatus erhalten.

**Kontrolle:** 2023 227.456, 2024 199.851 t belegte Zeilensummen; fehlende Feinpositionen ohne −100-%-Rate.

### T22 – Nationaler Modal Split nach Verkehrsleistung

**Aufbereitung:** Nationale Nenner und Inlands-tkm mit Quellenvertrag aus bestehendem Bestand bereitstellen.

**Kontrolle, nach Rohquellenprüfung B05 korrigiert (09.09.2026):** 2024 ergeben die bekannten Werte 624.919.760.431 tkm. Sieben VE7-Zellen `Inlands_tkm` mit `ZS_Inlands_tkm=.` sind jedoch unbekannt. Der Betrag ist deshalb kein bestätigter vollständiger Nenner; die neue Abfrage gibt keinen vollständigen Modal Split aus. Die ursprüngliche Sollannahme eines vollständigen Drei-Modi-Nenners ist nicht freigegeben.

### T23 – Unvollständiges Modal-Split-Jahr

**Aufbereitung:** Fehlende Straßenwerte des gewünschten Jahres offenhalten; vorhandenes gemeinsames Jahr nur als Alternative.

**Kontrolle:** Kein vollständiger 2025-Split nur aus Schiene/IWW.

### T24 – Regionaler Modal Split mit passendem Nenner

**Aufbereitung:** Regionaler Modal Split mit D01-Zählweise als festem Metadatum.

**Kontrolle:** Duisburg 44,8/16,7/38,5 %; Binnen in beiden Richtungen enthalten.

### T25 – Versand und Empfang sind keine Leerfahrten

**Aufbereitung:** Versand/Empfang/Saldo getrennt; Transit-/Leerfahrtenbedeutung nicht hineininterpretieren.

**Kontrolle:** Duisburger Straße Saldo +4.236.410 t; keine Zahl für Leerfahrten.

### T26 – Binnenverkehr und örtlicher Transit

**Aufbereitung:** OD-Innen/Außen/Eindeutig mit Berührungszählung vergleichen.

**Kontrolle:** 60 t eindeutig gegen 70 t Versand+Empfang; örtlicher Transit unbekannt.

### T27 – Nationaler Transit aus vorhandenen Rohquellen

**Aufbereitung:** Nationale Verkehrsbeziehungen aus vollständiger SGV-Rohquelle aufbereiten; unzugeordnete Räume erhalten.

**Kontrolle:** Schienentransit 2024 13.622.343.988 tkm, Anteil 10,784 % am nationalen Schienennenner.

### T28 – Größter prognostizierter Schienenzuwachs

**Aufbereitung:** VP-Ranking auf bestätigter NUTS-3-Grundgesamtheit, ungerundete Änderungen.

**Kontrolle:** Top absolut: Hamburg, Köln, Ludwigshafen, Bremerhaven, München; 400 passende Gebiete.

### T29 – Ist-Entwicklung neben der Prognose

**Aufbereitung:** Ist- und VP-Reihen mit verschiedenen Quellen-/Binnenverträgen getrennt bereitstellen.

**Kontrolle:** Keine Rate aus D01 2024 zu VP2040 als gleichartige Zeitreihe; VP-intern −10,0 %.

### T30 – Vorhandene Prognose mit Nullwerten und Szenariogrenze

**Aufbereitung:** Null-/Fehlwertlogik innerhalb bestehendem P1; keine weitere Szenarioaufbereitung.

**Kontrolle:** 100→0 −100 t/−100 %; 0→100 +100 t/undefinierte Rate; Beispiele synthetisch.

### T31 – Intermodale Teilmärkte getrennt

**Aufbereitung:** Vorhandene nationale Teilmärkte mit jeweiligem Nenner getrennt ausgeben.

**Kontrolle:** Schiene 99.853.065 t, IWW 16.738.676,4 t; keine eindeutige KV-Gesamtsumme.

### T32 – Regionaler intermodaler Anteil im Versand

**Aufbereitung:** Vorhandenen regionalen externen Versand mit Binnenabgrenzung verwenden.

**Kontrolle:** 4.422.816 / 9.194.861 t = 48,10 %; Binnen nicht im Nenner.

### T33 – Statistischer KV ist kein Verlagerungspotenzial

**Aufbereitung:** Statistische Teilmärkte als begrenzte Alternative; keine Potenzialpipeline.

**Kontrolle:** Keine realistisch verlagerbare Menge aus beobachteten KV-Mengen.

### T34 – Flughafenprofil mit unterschiedlichen verfügbaren Jahren

**Aufbereitung:** Kennzahlspezifische Zeitabdeckung erhalten; keine Flugzahl 2025 aus Tonnen ableiten.

**Kontrolle:** EDDP2025 1.390.729,8 t; Flughafenflüge 2025 nicht verfügbar, 2024 ggf. separate Alternative.

### T35 – Veröffentlichte Luftfrachtpartner und richtiger Nenner

**Aufbereitung:** Vollständige veröffentlichte Flughafen-OD mit Partnerland/Jahr/Richtung; international explizit definieren.

**Kontrolle:** EDDP2024 Auslandspartner 662.332,0 t in 59 positiven Relationen; OBBI=Bahrain; Top-25 kein Nenner.

**Präzisierung:** Für internationale Verbindungen Partnerland ungleich Deutschland; extern ist keine gleichbedeutende Abgrenzung.

### T36 – Seehafenumschlag, TEU und Vergleichsjahre

**Aufbereitung:** Hafen auswählen; dann passende Umschläge/TEU 2023/24 und gegebenenfalls vollständige Partner aus MRTM.

**Kontrolle:** Ohne Hafen keine Sollzahl; t/TEU und Ein-/Ausladung getrennt.

### T37 – Mautfahrten nach Richtung

**Aufbereitung:** Bestehende lokale Mautauszüge auf Eignung für bestätigte Gemeinde/Monat prüfen; kein automatischer Liveabruf.

**Kontrolle:** Synthetisch Start 15, Ziel 25, Binnen 5; reales Abbild und Filter müssen separat belegt sein.

### T38 – Vorjahresmonat und fehlende Angaben

**Aufbereitung:** Gleichgerichtete Gemeinde-OD im bestätigten Monat und Vorjahresmonat als feste Stände.

**Kontrolle:** 120/100 +20/+20 %; 120/fehlend ohne Vergleich; 120/0 +120, Rate undefiniert.

### T39 – Monatliche Güterspitzen

**Aufbereitung:** SGV-Monate mit bestätigter Gütergruppe/Richtung erschließen; Personalplanung bleibt außerhalb.

**Kontrolle:** Elfmal 100 plus 200 = 1.300 t; Spitzenanteil 15,38 %; fehlender Monat verhindert vollständige Jahresbewertung.

### T40 – Entfernungsstufen aus vorhandenen Rohdaten

**Aufbereitung:** KBA VD2-V: FT_ENTF3, FT_I, ZS, Region und Population; Klassen aus Handbuch.

**Kontrolle:** Nürnberg Nah/Regional/Fern 698.880,8 / 400.300,5 / 476.759,4 Fahrten; Grenzen 50/150 km.

### T41 – Vorhandene VD3c-Details auf NUTS-2

**Aufbereitung:** KBA VD3c-V/E NST-20 auf NUTS-2; TON/TKM/FT und Inland/Gesamt sowie ZS getrennt.

**Kontrolle:** DEA2: 20 Positionen mit Feld-/Flagvergleich; unterdrückte Gruppen nicht null; keine vollständige Summe behaupten.

### T42 – Null, fehlend und Quellenkennzeichen

**Aufbereitung:** Quellenspezifische ZS-Definitionen und separate Verfügbarkeits-/Qualitätszustände.

**Kontrolle:** Exakte synthetische 0 von KBA-Zeichen 0 trennen; / unsicher, - nichts vorhanden, () eingeschränkt.

### T43 – Regional- und Deutschlandwerte widersprechen sich scheinbar

**Aufbereitung:** Metadaten für Gebietsgrundgesamtheit, Berührungszählung und nationale Leistung bereitstellen.

**Kontrolle:** 422 Einträge=400 NUTS-3 plus22 andere; nicht als Deutschlandwert verwenden.

### T44 – Reproduzierbare Analyse und belegte Kurzfassung

**Aufbereitung:** Wiederholbare Ergebnisbelege mit tatsächlichen Quellenhashes/Filtern/Formeln/Rundung.

**Kontrolle:** Konkreter T19-Bezug; unabhängige Reproduktion von 199.851 t; keine erfundenen Nullen.

**Präzisierung:** Vollständiger Bezug: Köln DEA23 → Hamburg DE600, 2024, Schiene, Versand, belegte C-Gruppen, t und Anteil an belegter Relationssumme.

### T45 – Fragen außerhalb des bestätigten Umfangs

**Aufbereitung:** Keine Kosten-/Umwelt-/Kapazitätsaufbereitung; nur belegte Verkehrskennwerte als Alternative.

**Kontrolle:** Keine Euro-, CO₂e- oder Auslastungszahl; kein externer Folgeauftrag.

## 7. Konkreter nächster Umsetzungsschritt

Als erstes begrenztes Implementierungspaket wird B01 vorgeschlagen: eine zusätzliche vollständige OD-Auswertung mit Quellenkennzeichen und getrennten Datenzuständen, beginnend mit den vorhandenen VE7-Jahren sowie den dazu passenden SGV-/IWW-Relationsbeständen. Die Quelle-Ziel-, Jahres- und Güterkennungen bleiben typensicher. Die neuen Analysedaten werden getrennt von den bestehenden Browserpaketen ausgegeben.

Vor Freigabe werden die vorhandenen Referenzmengen, markierten Werte, nicht vorhandenen Zeilen und passenden Nenner nachgerechnet. Mengenänderungen bei eigentlich identischem Umfang werden erklärt, nicht durch Toleranzen verdeckt. Erst danach werden VD2/VD3c, feinere Schienengüter, vollständige Knotenrelationen und Monatsauswertungen auf dieser gemeinsamen Grundlage ergänzt.

Dieser Arbeitsschritt hat den Stand geprüft und die Planung vervollständigt. Er hat noch keinen neuen Datenbestand berechnet, keine Datenpipeline geändert, kein Requesty-Modell aufgerufen und nichts auf einem Server bereitgestellt.

## Nachweise

[Regelpaket und spätere Serverrolle](../../config/analyseassistent/README.md) · [Terra-Ergebnisbericht](../../outputs/analyseassistent_terra_probelauf_20260909/ERGEBNIS_TERRA_PROBELAUF.md) · [Einzelbewertungen](../../outputs/analyseassistent_terra_probelauf_20260909/BEWERTUNG_GESAMT.json) · [Korrigierte Referenzangaben](../../outputs/analyseassistent_terra_probelauf_20260909/FACHLICHE_KORREKTUREN.md)
