# Güterzeitreihe, Antwortqualität und Prognose-Datenladung

Stand: 14.09.2026, Fachregeln 0.4.2. Die folgenden Nachweise betreffen eine gezielte echte Modellstichprobe und lokale Regressionen. Sie ersetzen keine erneute Gesamtabnahme aller 45 Testfälle.

## Warum die bisherigen Tests den Fehler nicht verhinderten

Die bisherigen Prüfungen bestätigten technische Datenabfragen, ausgewählte Dialoge und einzelne Zahlenbindungen. Die Frage nach führenden regionalen Gütern **und** ihrer Entwicklung war im nativen Dialog nicht vollständig abgedeckt: Die Güterfunktion nahm nur ein Jahr und einen Verkehrsträger an; „seit 2020“ wurde zum Einzeljahr. Eine bestandene Funktionsprüfung belegt weder vollständiges Frageverständnis noch eine verständliche Antwort auf alle Teile. Die frühere Prüfung war dafür zu schmal.

## Änderungen und belegte Ergebnisse

`goods_history` beantwortet regionale Güterfragen für mehrere Jahre und Verkehrsträger. „Seit 2020“ bleibt durch eine Ortsrückfrage gespeichert und wird bis zum neuesten gemeinsamen Jahr aufgelöst. Für den Landkreis Leipzig und alle drei Landverkehrsträger ist das 2024. Verkehrsträger bleiben getrennt; unbekannte Gütergruppen werden auch bei veröffentlichtem Gesamtwert null nicht aufgefüllt.

| Landkreis Leipzig, Versand | 2020 | 2024 | Veränderung veröffentlichter Werte |
|---|---:|---:|---:|
| Straße, Gesamtaufkommen | 13.899.892 t | 13.295.272 t | −4,35 % |
| Straße, führende C1-Gruppe | 5.408.617 t | 6.144.747 t | +13,61 % |
| Schiene, Gesamtaufkommen | 1.565.140 t | 1.491.266 t | −4,72 % |
| Schiene, führende C1-Gruppe | 797.506 t | 772.173 t | −3,18 % |
| Binnenschiff, veröffentlichter Gesamtwert | 0 t | 0 t | keine Rate bei Ausgangswert null |

C1: Erzeugnisse der Land- und Forstwirtschaft, Rohstoffe. Anteile 2024: Straße 46,22 %, Schiene 51,78 %. Binnenschiff: keine aufgeschlüsselten Gütergruppenwerte; keine Rangfolge und keine verkehrsträgerübergreifende Gesamtrangliste. D01-Profilgrenzen gelten: keine harmonisierte Gebietszeitreihe, keine belegten Ursachen, Straßen-Quellenkennzeichen der Güterrandsummen nicht nacherschlossen.

Die freie Antwort muss alle angefragten Verkehrsträger, führende Mengen und Randjahre berücksichtigen. Eine kurze unvollständige Antwort wird durch eine vollständige geprüfte Ersatzantwort ersetzt. Die Oberfläche kündigt eine tatsächlich vorhandene Ergebnistabelle verständlich an.

Die Prognoseansicht scheiterte an zwei HTTP-404-Dateien: `crosswalk_spatial_vp2040.json` und `crosswalk_nst_vp2040.json`. Der Paketbuilder kopiert beide ausdrücklich und prüft statische Browser-Datenabhängigkeiten. Ein zusätzlicher ausführender Test verwendet den realen Prognose-Lader ausschließlich gegen den öffentlichen Paketbestand; einschließlich dynamischer regionaler Detaildatei DEA1D. Ausgangspaket: Fehler reproduziert. Quellbestand und neues Fachpaket: alle fünf Datenanforderungen erfolgreich.

## Tatsächlich gelesene Modellantworten

Keine feste Funktion oder bestätigte Filter wurden den Stichproben vorgegeben. Die KI musste die natürlich formulierten Fragen selbst zuordnen. User-Freigabe: Requesty-EU; lokal ohne Portalbuchungen. Bewertet wurden Verständnis, Funktions-/Datenzuordnung, Zahlen und Bezüge, verständliche Sprache sowie Vollständigkeit einschließlich Datenlücken.

| Fall / Eingabe | Tatsächlich geprüfte Antwort und Bewertung |
|---|---|
| Original Leipzig, erste Frage | Sachgerechte Rückfrage Stadt/Landkreis; Zeitabsicht und Versand bleiben gespeichert. Keine ungeprüften Kennzahlen. |
| Leipzig, „Landkreis Leipzig und alle Verkehrsträger“ | Drei verständliche Absätze, Rangfolge/Mengen/Anteile 2024 und Entwicklung seit 2020 für Straße/Schiene; Binnenschiffsgrenze ausdrücklich. Werte stimmen mit obiger Tabelle überein. |
| Leipzig, vollständige Ausgangsfrage | Selbstständige richtige Zuordnung, derselbe vollständige Zeitraum. Sprachliches „Rückgang um −x %“ im ersten Nachtest war unnötig holprig; Formulierungsregel ergänzt. |
| „Und nur die Schiene?“ | Richtungs-/Zeitabsicht bleibt; jetzt neuestes verfügbares Schienenjahr 2025 ausdrücklich genannt. Führende C1-Menge 642.407 t; Gesamtentwicklung seit 2020 −7,04 %. |
| „Jetzt nur 2022 auf der Straße.“ | Richtiger Wechsel zur Einzeljahresstruktur; C1 5.655.670 t / 41,15 %, veröffentlichte Gesamtsumme 13.744.140 t. Keine alte Zeitreihe weitergeführt. |
| T02, „unsere Stadt“ ohne Ortsangabe | Verständliche Orts-/Jahresrückfrage statt erfundener Region. Bestanden als Rückfragefall. |
| T04, Hamburg, fünf externe Straßenpartner 2024 | Harburg, Segeberg, Stormarn, Herzogtum Lauenburg, Region Hannover mit richtigen Mengen/Anteilen. Nenner aller veröffentlichten Partner 55.473.138 t, eingeschränkte Teilmenge 21.167.732 t. Nachtest frei beantwortet. |
| T05, Duisburg ↔ Magdeburg 2024 | Beide Richtungen: Binnenschiff 1.947 t / 1.189 t. Straße/Schiene ohne eigene Zeile; kein Nullverkehr behauptet. Nachtest frei beantwortet und verständlich. |
| T07, Duisburg/Magdeburg, Aufkommen + Modal Split + Güterstruktur | Nach Korrektur vollständige freie Antwort für beide Regionen. Aufkommen 108.215.313,50 t / 23.180.902,50 t; alle drei Modalmengen/-anteile; führende Gruppen. Magdeburg C7 6.065.189,90 t / 26,16 %. Hinweis auf Binnen-Doppelzählung vorhanden. |
| T16, Duisburg, Straßenversand 2024 | C3 7.154.062 t / 27,13 %, C7 5.225.211 t / 19,81 %, C4 4.629.340 t / 17,55 %. Freie Antwort sachlich, richtige Richtung; etwas ausführlich mit weiteren Gruppen. |
| T20, Köln → Hamburg, Straßen-Güterarten 2024 | Güterarten auf Straßenrelationen nicht verfügbar; 67.757 t als eingeschränkter Gesamtwert korrekt. Nachtest erklärt die Grenze in zwei klaren Absätzen. Geprüfte Alternativen dürfen erwähnt werden; keine fremden Zahlen übernommen. |
| T22, nationaler Modal Split der Verkehrsleistung 2024 | Kein vollständiger Drei-Modi-Anteil bei fehlender Straßenleistung. Schiene 126.319.807.860 tkm und Binnenschiff 43.443.314.381 tkm korrekt; keine Teilmenge zum Gesamtverkehr erklärt. |
| T35, Leipzig/Halle, internationale Luftfrachtpartner 2024 | ICAO EDDP anhand Katalog erkannt. East Midlands 50.109 t, Cincinnati 39.586 t, Bahrain 30.075 t, Brüssel 28.973 t, Incheon 26.848,80 t. Verständliche drei Absätze; Veröffentlichungsumfang korrekt vom gesamten Flughafenaufkommen unterschieden. |

Zusätzliche Fehler der ersten Stichprobe wurden offen festgehalten: eigene Textprüfung verbot veröffentlichte Partnernamen, Gegenrichtung und geprüfte Alternativmodi; feste Ersatzantwort für Regionsvergleich zu kurz; Flughafen-Katalog fehlte. Anschließend trat bei neu gruppierten Belegen der 30-Zeilen-Grenzfehler auf. Alle bestätigten Fehler wurden korrigiert; betroffene Fragen gezielt erneut gestellt. Die tatsächlichen Endantworten wurden gegen frisch abgefragte Daten und die endgültige Textprüfung nochmals geprüft, ohne weitere Modellaufrufe.

Lokale Nachweise: `outputs/analyseassistent_goods_20260914/`. `revalidated_final.json` enthält 13 abschließende Eingaben/Antworten. Einschließlich verworfener Versuche: 23 Eingaben, 40 Modellaufrufe, 659.192 gemeldete Tokens, 0,482036115 USD gemeldete Kosten. Kein Portal-Fragenkontingent belastet. Browserabnahmen sind darin nicht enthalten.

## Unabhängige Prüfung und Grenzen

Drei ausschließlich lesende Prüfungen mit Gemini 3.8 Flash High; keine Dateiänderungen durch Gemini. Konkrete Hinweise wurden am Code und durch eigene Tests überprüft. Bestätigt und korrigiert: Gruppierung jenseits 30 Zeilen, Mengenbindung für Gegenrichtungen, Einheitenbindung von Millionenangaben und unqualifizierte gemeinsame Ortsnamen. Beim Modal Split werden belegte Anteilsangaben als Alternative zu absoluten Einzelmengen akzeptiert. Mehrere Regionen mit einzelnen regionalen Mengen sollen in getrennten Sätzen stehen; dadurch werden unklare Vertauschungen abgefangen. Ein belegter Vergleichsabstand darf beide Regionen nennen.

Die Textprüfung bleibt heuristisch; sie ist kein allgemeiner semantischer Beweis. Ein durchgefallener freier Text führt zur vollständigen geprüften Ersatzantwort. Die acht dokumentierten Fragetypen und fünf Leipzig-Eingaben belegen diese gezielte Auswahl, keine Fehlerfreiheit beliebiger Formulierungen und keine erneute 45-Fälle-Abnahme.

## Bereitstellung

Aktiv auf Testsite 1067000: `portal-test-20260914-gueterstroeme-goods03`, Fachregeln 0.4.2. Manifest SHA-256 `bb3829e6b0f796f900f4ec681cb6abfc4871d218075df9493c49ebe47d633039`; 1.710 Dateien, 668.537.761 Bytes. Der Stand wurde unabhängig aus dem vollständig geprüften lokalen beta06-Bestand zusammengesetzt; fremde lokale Portaländerungen wurden nicht übernommen. Nach einem ersten erfolgreichen Teststand goods02 ergänzte goods03 nur die zusätzliche Zuordnungsprüfung: zwei geänderte Nutzdateien plus Manifest, 365.063 Bytes übertragen; 1.708 Dateien unabhängig serverseitig kopiert und alle Zieldateien geprüft. Öffentliche Browserdateien gegenüber goods02 unverändert. API und Datenbank bereit; monatliche KitaNavigator-Testaufgabe auf den neuen Release umgestellt. Produktion unverändert.

147 lokale Tests bestanden. Zusätzlich eine große Prognosematrix mit 48 Fakten und zwölf Beleggruppen sowie eine größere Partnerliste gegen die frühere 30-Zeilen-Lücke geprüft. Die Linuxprüfung des aktiven goods03 bestand: alle 1.710 Manifestdateien, 273 Güterfakten, Zeitabsicht durch Ortsrückfrage, vollständige Ersatzantwort, unbekannte Binnenschiffsgruppen, beide Prognose-Crosswalks sowie bestehende Prognose-/Dialog-/Kontingentregressionen. Null externe Modellaufrufe und null Datenbankschreibvorgänge; alle temporären Prüfaufgaben, FTPS-Zugänge und Status-/Sperr-/Fortschrittsdateien entfernt (`linux_final.json`).

Angemeldeter Browser: Prognosekennzahlen, Karte und beide Diagramme national geladen; Duisburg anschließend mit regionalen Kennzahlen, zehn Partnerverbindungen und Diagrammen vollständig geladen. Diese Datenabnahme erfolgte in goods02; dessen öffentliche Dateien sind mit goods03 identisch. Originalfrage Leipzig sachgerecht mit Ortsrückfrage; Antwort „Landkreis Leipzig und alle Verkehrsträger“ im aktiven goods03 liefert vollständig 2020–2024, drei Verkehrsträger und Tabellenankündigung. Hier wurde die vollständige geprüfte Ersatzantwort verwendet; sie ist verständlich gegliedert, aber technischer formuliert als die freien lokalen Antworten. Kein Nachweis, dass jeder neue freie Modelltext die Prüfung besteht. Tabelle geöffnet: 273 Zeilen, erster Wert 5.408.617 t für C1/Straße/Versand 2020. Kontingent: 20 → 20 nach Rückfrage → 21 nach numerischer Antwort, genau eine Buchung (`browser_final.json`).

Unauthentifizierte Zugriffe am endgültigen Stand: Health 200, Kontingent 401, geschütztes JavaScript 403, privater Systemprompt 404 (`public_access_final.json`).

Eigene überholte lokale Fachpakete und nicht aktivierte lokale Vorbereitungen unter `C:\tmp` entfernt; fremder Basisbestand erhalten. Der aktive lokale Release bleibt bis zum Abschluss der Nachweissicherung verfügbar. Auf dem Server bleiben ältere Testreleases bis zur noch offenen Löschfreigabe erhalten; insbesondere ist die frühere beta06-Löschung nicht als freigegeben behandelt. Keine stillschweigende Löschung und keine Produktionsänderung.

Quellen, Prompts, Tests und Betriebsunterlagen werden regulär auf GitHub `main` gesichert. Remoteabgleich, Commit-ID und abschließende lokale Bereinigung stehen in `outputs/analyseassistent_goods_20260914/completion.json`.
