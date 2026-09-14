# Analyseassistent: Flughafenverbindungen und Vorschaufragen

Stand: 14.09.2026, Regelversion 0.7.0. Testrelease `portal-test-20260914-gueterstroeme-nodes02` aktiv, lokale und abschließende Linux-Prüfung bestanden. Keine allgemeine fachliche Gesamtabnahme beliebiger Modellfragen.

## Umfang und fachliche Grenzen

- Konkrete Flughafenverbindungen aus dem vorhandenen AVIA_GOR_DE-Bestand, IATA-/ICAO-Auswahl und kataloggebundene London-Gruppe; keine Umformung der großen Bestandsdaten.
- LEJ–LHR bezeichnet ausschließlich Leipzig/Halle–Heathrow. London umfasst im vorhandenen Katalog Luton, Gatwick, Heathrow, Southend und Stansted; keine Zusage vollständiger Stadtabdeckung.
- Gegenräume auch für Knotenstatistik, Profile, Ranglisten und Verbindungen. Unbekannte Länder, fehlende Zeilen und fehlende Werte werden nicht zu Ausland oder Nullverkehr umgedeutet.
- Flughafen-Gesamtstatistik und veröffentlichte Relationsauswahl bleiben getrennt. Die bisherige GOOA-Flugsperre 2025 bleibt bis zu einer gesonderten Quellenprüfung erhalten.
- Fünf statt sechs Vorschaufragen. Die Verwaltungsvorlagenfrage wurde entfernt. Eindeutige Fragen mit fehlendem Jahr führen zur Jahresrückfrage, nicht zur allgemeinen Nichtzuordnung.
- Vorherige NST-/VP-Zugriffe, Inland/Ausland, Modalgesamtsummen, KV-Grenzen und strukturierte Antworten bleiben Bestandteil der Regressionen.

## Nachweise

Die direkte Prüfung der jährlichen Original-TSV-Zeilen und des bestehenden Analysepakets ergibt für reine Fracht- und Postflüge 2024 von Leipzig/Halle: Luton 438, Heathrow 66, Stansted 490. Southend besitzt keinen Zahlenwert, Gatwick keine Zeile. Bekannte London-Teilsumme: 994; vollständige Gesamtsumme unbekannt. In Gegenrichtung beträgt die bekannte Teilsumme 634. IATA-Aliasse stammen aus dem vorhandenen OurAirports-Abbild vom 03.09.2026; die kleine Referenzdatei bindet dessen SHA-256.

`outputs/analyseassistent_nodes_20260914/offline02.json`: 215 lokale Tests, keine Fehler, keine externen Modellaufrufe. Neue Regressionen sichern insbesondere Gruppenauflösung, exakte IATA-Auswahl, fehlende Werte, Gegenrichtung, 2025-Grenze, Filterwechsel, Mehrkennwerterhalt und Vorschaufragen ab.

Die ausdrücklich freigegebenen acht Modellfragen wurden über Requesty-EU ausgeführt: acht Antworten, keine technischen Fehler, keine Ersatzantwort. Sie decken London, Gegenrichtung, Heathrow, ausländische und inländische Flughafenpartner, Hamburg/China/Metalle, Duisburg/Ausland und Berlin/Gesamtverkehr ab. Nachweis: `live01.json`, 16 Modellaufrufe, ausgewiesene Kosten 0,3908883 USD; keine Kundenbuchung.

Die zusätzlich freigegebenen fünf sichtbaren Vorschaufragen wurden je einmal geprüft: drei gezielte Jahresrückfragen, eine direkte Magdeburger Zeitreihe, eine fachlich richtige Prognose-Ersatzantwort. Bei letzterer reichte die bisherige Belegzahl für fünf Ränge mit jeweils vier Zahlen nicht aus. Ein gemeinsames, serverseitig begrenztes Prognose-Rangbelegpaket behebt dies. Der gespeicherte Modelltext wurde mit dieser Belegzuordnung offline erfolgreich erneut geprüft; kein zusätzlicher bezahlter Modelllauf nach dieser Änderung. Nachweis: `examples01.json`, sieben Modellaufrufe, 0,16179075 USD, keine technischen Fehler, eine sichere Ersatzantwort.

## Gemini-Zweitprüfung und eigene Bewertung

Zwei abgeschlossene lesende Gemini-Prüfungen wurden unabhängig nachbewertet; ein vorheriger breiterer Versuch lief in ein Zeitlimit und zählt nicht als bestandene Prüfung. Bestätigte Befunde zu Gegenraumvalidierung, Quellenkennzeichnung, explizitem Zurücksetzen des Auslandsfilters und dem Erhalt mehrerer Kennwerte wurden korrigiert und durch Regressionen abgesichert. Hinweise auf eine angeblich unzulässige GOOA-Flugsperre wurden nicht übernommen: GOR-Verbindungen ersetzen keine gesperrte Gesamtstatistik. Die Gruppenauflösung verwendet denselben validierten Namenskatalog; Ranglistenanteile beziehen sich ausdrücklich auf veröffentlichte nutzbare Partnerwerte, nicht die gesamte Flughafenmenge. Gemini hatte ausschließlich lesenden Zugriff; seine Befunde sind keine pauschale Freigabe.

## Sichtprüfung und Bereitstellung

Die gespeicherte echte London-Antwort wurde lokal ohne weiteren Modellaufruf im Browser angezeigt: bekannte Teilsumme 994, drei lesbare Aufzählungspunkte, vollständige Gruppenbenennung und sichtbare Fehlstellenhinweise. Die geöffnete Tabelle zeigt sieben Werte einschließlich unbekannter vollständiger Summe und bekannter Teilsumme.

Der erste Release `nodes01` bestand die Dateiprüfung, scheiterte aber bei der abschließenden privaten Dateninitialisierung. Während des Paketkopierens waren parallel zwei manifestgebundene Aufbereitungsdateien geändert worden: `scripts/pipelines/build_b0406_analysis.py` und `scripts/analysis/b0406.py`. Die Laufzeit blockierte den Mischstand korrekt. Testsite und ihre monatliche KitaNavigator-Aufgabe wurden auf den zuvor geprüften `scope01` zurückgestellt; API und Datenbank waren anschließend bereit. Keine Datenbankänderung oder Modellbuchung durch den fehlgeschlagenen Prüflauf; sämtliche temporären Prüfmittel wurden entfernt (`linux01.json`).

Die Korrektur erfolgt ausschließlich in einer neuen Paketkopie. Beide Dateien wurden aus dem geprüften beta06-Rückfallpaket übernommen, und zwar nur nach Gleichheit mit den jeweils erwarteten Datenmanifest-Hashes. Der parallele Arbeitsstand blieb unangetastet. Die komplette kopierte Laufzeit wurde erfolgreich neu geladen und ihr Snapshot `cb3de04eb6e3444e2435b8c1` bestätigt (`repair01.json`). Sowohl Fachpaket-Builder als auch Release-Zusammenstellung führen diesen abschließenden Ladetest künftig in einem frischen Prozess aus. Eine frühere reine Prüfung des Ausgangsbestands genügt nicht als Freeze-Nachweis.

Der korrigierte Release `nodes02` ist auf Testsite 1067000 aktiv. Manifest: `276b4533498132122bf895fa92d4e9586bcbd027e58013f97bdf414324f4bacf`. Alle 1.732 Dateien bestanden die erneute Linux-Prüfung; 1.715 Dateien wurden unabhängig kopiert, 17 geänderte Nutzdateien plus Manifest übertragen (787.411 Bytes). Gegenüber dem geprüften beta06-Ausgangsportal sind unbeteiligte Portaldateien identisch. API und Datenbank sind bereit; die bestehende monatliche KitaNavigator-Testaufgabe 30833 zeigt auf den neuen Testrelease.

`linux02.json` bestätigt neben London 994/634, Heathrow 66, unbekannter vollständiger London-Summe und fünf Vorschaufragen auch die früheren Dialog-, Kalenderjahr-, Prognose-, NST-, Hafen-, KV-, Gegenraum- und Gesamtverkehrsprüfungen. 291.300 Quellenzellen im Dashboard-Zugriff wurden erneut abgeglichen. Keine externen Modellaufrufe, keine Datenbank-Schreibzugriffe. Temporäre Prüfaufgabe, FTPS-Zugang, Status-, Fortschritts- und Sperrdateien sind nachweislich entfernt.

Im frisch geladenen angemeldeten Testportal wurden KI-Fenster und die fünf Vorschaufragen visuell geprüft. Die Verwaltungsvorlagenfrage fehlt; keine Frage wurde im Kundenkonto abgesendet, das angezeigte Kontingent blieb während der Sichtprüfung unverändert. Der lokale Vorschauprozess ist beendet. Parallel laufende Luftverkehrsdatenaktualisierungen sind nicht Bestandteil dieses eingefrorenen Releases. `nodes01` ist ein fehlgeschlagener Zwischenstand und **kein geeigneter Rückfallrelease**; `scope01` bleibt der zuvor bestätigte fachliche Rückfallstand.

Die abschließende Serverinventur bestätigt `nodes02` als aktiven Release, gesunde Anwendung, unveränderte Produktion und Entfernung des temporären Inventurzugangs. Alle acht vor Beginn vorhandenen Releases sind einschließlich Manifest, Dateizahl, Größe und Bereitschaftsstatus identisch (`server_inventory_before.json`/`server_inventory_after.json`). Alte Releases wurden nicht gelöscht. Der Dateibereitschaftsmarker allein ist kein fachlicher Laufzeitnachweis: Dies zeigt ausdrücklich der erhaltene, aber nicht freigegebene Zwischenstand `nodes01`.
