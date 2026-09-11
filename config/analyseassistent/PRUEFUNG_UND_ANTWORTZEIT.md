# Antwortprüfung und kurze Wartezeiten

**Version 0.1.0 · 09.09.2026 · Entwurf für die spätere Implementierung.** Die beschriebenen Prüfschritte sind noch nicht programmiert; Antwortzeiten und passende Fristen sind noch nicht mit Requesty ermittelt.

## Was automatisch geprüft werden kann

Eine schnelle Prüfung gleicht bekannte Größen und zulässige Aussagen ab. Sie ist keine allgemeine Beurteilung, ob beliebiger KI-Text wahr oder sinnvoll ist. Der Standardablauf nutzt deshalb feste Datenfunktionen und vorgeprüfte Aussagebausteine.

| Stufe | Konkrete Prüfung | Reaktion bei Abweichung |
|---|---|---|
| Vor der Abfrage | Erlaubte Funktion, zugelassene Parameter, tatsächlicher Bezug zur Frage und zu bestätigten Filtern | Ungültigen Plan nicht ausführen; gezielte Rückfrage oder strukturierte Auswahl |
| Datenfunktion | Quelle, Raumebene, gemeinsames Jahr, Population, Richtung, Einheit, Güter, Binnenzählung und Verfügbarkeit | Betroffene Zahl sperren oder Antwort als Teilantwort mit Grenze kennzeichnen |
| Berechnung | Formel, vollständiger kompatibler Nenner, Status der Eingabewerte, Vorzeichen, Rang und Rundung | Keine Freigabe der abgeleiteten Zahl; Fehler dokumentieren |
| Aussageangebot | Jede Aussage verweist auf aktuelle Fakten und besitzt erfüllte Voraussetzungen | Nicht belegte Aussage gar nicht zur Auswahl anbieten |
| Modellrückgabe | Zulässiges Format, gleiche Ergebnis-/Datenstandskennung, nur vorhandene Aussage- und Tabellenkennungen, keine Zusatzfelder | Gesamte ungültige Auswahl verwerfen; feste Zusammenfassung verwenden |
| Ausgabe | Werte/Namen direkt vom Server einsetzen; erforderliche Tabellen, Jahr, Quellen und Methodikhinweise vollständig ergänzen | Unvollständige Ausgabe nicht als reguläres Ergebnis zeigen |

Ein reiner Zahlenabgleich reicht nicht: „Hamburg ist kleiner“ könnte trotz richtig kopierter Zahlen falsch sein. Deshalb werden im Standardmodus die Vergleichsoperatoren bereits auf dem Server geprüft. Ebenso muss die Zuordnung der Frage geprüft werden: Eine gültige Datenbankkennung für den falschen Ort wäre weiterhin eine falsche Antwort. Unklare Ortsnamen oder die Unterscheidung international/extern führen zur Rückfrage. Eindeutig aufgelöste Fragen benötigen keinen zusätzlichen Bestätigungsklick; die verwendeten Filter werden mit dem Ergebnis sichtbar.

## Konkrete Fehler aus dem Terra-Lauf und ihre Absicherung

| Befund | Verbindliche Korrektur im Serverablauf | Bestehende Tests |
|---|---|---|
| Fehlende Güterzeilen als 0 und daraus −100 % ausgegeben | Fehlstatus erhalten; ohne Nullnachweis keine Nullfüllung und keine gruppenbezogene Änderungsrate | T19, T21, T42, T44 |
| Richtige Regionalmenge als reinen Außenverkehr beschrieben | Zählweise als Pflichtmetadatum und zwingenden Textbaustein binden | T01, T07, T24, T26, T29 |
| Internationale Luftfracht mit inländischen Partnern im Nenner | Auslandspartner vor Aggregation über vollständige publizierte Rohrelationen filtern; Nennerumfang mitgeben | T35 |
| Flughafenname aus Gedächtnis falsch benannt | Name über den aktuellen Metadatenschlüssel einsetzen | T35 |
| Textliche Güterrangfolge passt nicht zur Versandtabelle | Rangfolge je Richtung berechnen; nur daraus erzeugte Aussage anbieten | T16 |
| 422 gemischte Gebietseinträge als Regionalgesamtvergleich verwendet | Gebietsebene über Register prüfen; 400 NUTS-3 und zusätzliche Ebenen unterscheiden; Mehrfachberührung erhalten | T43 |
| Qualitätsflags oder Klassenbedeutungen fehlen | KBA-Zeichen je Quelle und Version auswerten; VD2-Klassengrenzen aus vorhandenem Handbuch übernehmen | T04, T20, T40, T41, T42 |
| Zahlenangaben oder Bezug im Testeingang beeinflussen die Bewertung | Erwartete Antworten von Modelleingaben trennen; jeden isolierten Fall mit vollständigen Eingaben versehen | T19, T32, T44 |

Für T35 gilt in diesem Paket die natürliche Frage nach **internationalen Verbindungen**: Partnerland ungleich Deutschland. Die allgemeinere alte Parameterformulierung „externe Partner“ darf nicht als gleichbedeutend behandelt werden. Bei der nächsten Fassung des Prüfkatalogs ist diese Eingabe ausdrücklich zu präzisieren; der archivierte Versuch wird nicht umgeschrieben.

Die Regelzuordnung zu allen 45 Fällen steht maschinenlesbar in `FACHREGELN.json`. Die bekannten Fehler ersetzen nicht die übrigen Fälle. Jede Änderung an Modell, Prompt, Funktionsvertrag, Datenstand oder Regeln benötigt eine passende erneute Prüfung; für einen Modellvergleich wird der vollständige bereinigte 45-Fälle-Satz verwendet.

## Antwortzeiten zuerst messen, Fristen danach festlegen

**Nutzerpräzisierung vom 09.09.2026:** Die zunächst genannten fünf und zehn Sekunden sind keine bestätigten Leistungswerte und werden nicht als feste Ziel- oder Abbruchgrenzen übernommen. Eine fachlich richtige, noch laufende Antwort soll nicht an einer ungeprüften knappen Frist scheitern. Die Zeitwerte in der Konfiguration bleiben bis zur Messung ausdrücklich offen.

| Anteil | Zuerst ermitteln | Vorgesehener Umgang |
|---|---|---|
| Frage zuordnen, nur falls nötig | Dauer der Zuordnung und Anteil nötiger Rückfragen | Bei strukturierten Filtern ohne Modell; sonst höchstens ein Aufruf |
| Vorbereitete Daten abrufen und berechnen | Laufzeit mit warmem und leerem Cache | Indizierte/vorgeladene Bestände oder geprüfter Ergebniscache |
| Optionale Auswahl der Kurzfassung | Modelllaufzeit einschließlich langsamer Antworten | Geprüfte Tabelle mit fester Kurzfassung kann bereits erscheinen |
| Rückgabe prüfen und einsetzen | Tatsächliche lokale Prüfzeit | Format-, Kennungs- und Vollständigkeitsprüfung ohne weitere KI |
| Gesamter interaktiver Ablauf | Median, 95. Perzentil und Ausreißer unter paralleler Nutzung | Nutzbare Antwort früh zeigen; Gesamthöchstfrist erst anhand der Messungen festlegen |

Nach dem Pilotlauf werden eine realistische Zielzeit, ein Zeitpunkt für einen verständlichen Wartehinweis und eine technische Höchstfrist getrennt festgelegt. Dabei sind auch Zeitlimits von Server und Anbieter zu prüfen. Ein Wartehinweis beendet die Anfrage nicht. Bereits geprüfte Ergebnisse bleiben sichtbar; Nutzende sollen eine laufende Anfrage selbst abbrechen können.

Offene Konfigurationswerte bedeuten keine unbegrenzte Wartezeit im späteren Betrieb. Vor Aktivierung muss eine begründete Frist gesetzt sein. Sie gilt für den gesamten Ablauf einschließlich Warteschlange und Netzwerk und wird nicht bei jedem Schritt neu gestartet. Es gibt höchstens zwei Modellaufrufe insgesamt und keine automatische Reparatur- oder Bewertungsrunde. Bei bereits bekannten Filtern reicht ein optionaler Antwortaufruf; ohne ihn ist eine feste Zusammenfassung möglich.

Für den häufigen Regionsvergleich sollen benötigte Werte vorab verfügbar sein. Neue Rohdatenaufbereitung gehört in den Aktualisierungsprozess. Wenn eine gewünschte Datenfunktion noch nicht vorbereitet ist, meldet die Anfrage diese konkrete Grenze. Sie startet keine minutenlange Datenaufbereitung im Hintergrund.

## Zeitüberschreitung und Ausfall

- **Zuordnung unklar oder zu langsam:** Keine beliebige Region oder Jahreswahl übernehmen. Eine passende strukturierte Auswahl beziehungsweise gezielte Rückfrage ausgeben.
- **Datenabruf fehlgeschlagen:** Ohne geprüftes Ergebnis keine Zahl aus Modellwissen und keine unmarkierten alten Cachewerte ausgeben. Technischen Fehler von fachlich fehlenden Daten unterscheiden.
- **Ergebnis vollständig, Modell zu langsam oder ungültig:** Die geprüfte Tabelle und feste Kurzfassung bleiben die Antwort. Pflichtangaben stammen weiterhin aus dem Ergebnis.
- **Verspätete Rückgabe:** Nach Abschluss oder neuer Nutzerfrage nicht mehr in eine andere Antwort einsetzen. Ergebniskennung und Datenstand müssen exakt passen. Abbruch nach Möglichkeit weiterreichen; ein lokales Zeitlimit garantiert allein noch keinen Abbruch oder Kostenstopp beim Anbieter.

## Vorbereiten und zwischenspeichern

Prompt, Metadaten und Regeln beim Start einer Serverversion laden. Häufige, rein fachliche Datenabfragen dürfen mit vollständigem Schlüssel zwischengespeichert werden: Datenstand, Funktionsvertrag, alle Filter, Einheit, Skalierung, Zählweise, Population, Güterklassifikation, Regelversion und Zugriffsbereich. Vor jeder Cacheausgabe trotzdem die Berechtigung prüfen. Eine Quellen- oder Regeländerung macht alte Ergebnisse für diesen Stand ungültig.

Rohfragen werden standardmäßig nicht dauerhaft gespeichert. Für Messungen genügen Fallkennung, pseudonyme technische Anfragekennung, Paket-/Modell-/Datenversion, Phasenzeiten, Ergebnisstatus, Cachetreffer, Abbruch und gegebenenfalls tatsächlich gemeldeter Verbrauch. Schlüssel und personenbezogene Portalangaben gehören weder in Protokolle noch in Modellanfragen.

## Messung und spätere Abnahme

Die 45 fachlichen Fälle bilden die Grundlage. Synthetische Rechenfälle prüfen Regeln, nicht den Zugriff auf reale Monats- oder Mautdaten. Zusätzlich werden folgende technische Situationen separat geprüft:

1. Bekannter Regionsvergleich mit warmem sowie leerem Cache; gleiche Antwort und Pflichtangaben.
2. Freie Formulierung desselben Vergleichs; korrekte Zuordnung und sichtbare Filter.
3. Eine große oder noch nicht vorbereitete Anfrage; Einhaltung der später festgelegten Frist und wahrheitsgemäßer Status.
4. Ungültige Modellkennung, zusätzliche Textfelder oder Bezug auf einen alten Datenstand; feste Antwort statt ungeprüfter Ausgabe.
5. Verzögerter Modellaufruf, Netzfehler und verspätete Rückgabe; keine zweite automatische KI-Runde.
6. Mehrere gleichzeitige Anfragen einschließlich Warteschlange; Antwortzeit und Fehlerquote erfassen.
7. Unberechtigter Zugriff auch bei Cachetreffer; keine Ergebnisfreigabe.
8. Neue Daten-/Regelversion; keine Wiederverwendung unpassender alter Ergebnisse.

Je Versuch getrennt messen: Zeit bis zur nutzbaren Tabelle einschließlich Kurzfassung und Quellen, Zeit bis zur optionalen Modellauswahl sowie gesamte Antwortzeit. Median, 95. Perzentil, Anzahl der Zeitüberschreitungen und der festen Rückfallantworten berichten. Ein schneller falscher Wert besteht nicht. Rückfragen bei tatsächlich unklaren Angaben sind erwartetes Verhalten, aber keine beantworteten Zahlenvergleiche.

Für einen belastbaren Geschwindigkeitstest sind wiederholte typische Anfragen und gleichzeitige Nutzung erforderlich. Ein einzelner schneller Aufruf oder der Mittelwert aller 45 unterschiedlichen Fälle reicht nicht. Requesty-Messungen und die Umsetzung der hier beschriebenen Kontrollen stehen noch aus.
