# Prognosevergleich mehrerer Regionen und Kennwerte

## Anlass und bestätigte Ursache

Der gemeldete Dialog „Wie entwickelt sich bis 2040 die Schienengüterverkehre in Magdeburg und Duisburg?“ → „Bitte stelle beide Regionen und beide Kennwerte dar“ → „na 2040“ ist mit Version 0.4.0 nicht vollständig abbildbar. Das einzige passende Vergleichswerkzeug `forecast_comparison` verlangte eine einzelne Region, eine einzelne Kennzahl und mindestens ein beobachtetes Jahr. Die erste Rückfrage und die anschließende Aufforderung zur Auswahl beobachteter Jahre wurden mit drei echten Eingaben reproduziert. Der dritte Modellschritt wich vom Nutzerbericht ab: Er setzte ungefragt 2019 ein und lieferte nur Magdeburg in Tonnen, einschließlich nicht verlangter Verkehrsträger. Auch dies beantwortete den Auftrag nicht. Nachweis: `outputs/analyseassistent_forecast_20260914/before.json`.

## Version 0.4.1

`forecast_regions` vergleicht die feste Prognosebasis 2019_BASE mit dem Szenario 2040_P1 für bis zu fünf Kreise oder kreisfreie Städte, einen bis drei Landverkehrsträger sowie Tonnen und/oder Tonnenkilometer. Beobachtete Jahre sind keine Voraussetzung. Vorhandene geprüfte `forecast.parquet`-Werte und die Berechnungen von `forecast_rows` werden wiederverwendet. Es werden keine Zwischenjahre interpoliert und keine Summen über die ausgewählten Regionen gebildet. Nicht gewählte Verkehrsträger und deren Gesamtsummen werden nicht ausgegeben.

Der Werkzeugkatalog benennt diese Fähigkeit ausdrücklich. Prompt und Gesprächsvererbung unterscheiden reine Prognose, zusätzliche Ist-Vergleiche und neue Themen. „Beide Kennwerte“ erweitert die Auswahl; Regionen und Verkehrsträger bleiben bestehen. Der vollständige Zahlenvergleich und seine methodischen Grenzen bleiben auch bei Ausfall der freien Formulierung als feste Antwort erhalten. Quellen, Region, Kennzahl, Einheit, Modus und Szenario werden an jedem Zahlenbeleg mitgeführt. Bei der Prozentänderung wird eine Nullbasis als mathematische Nichtberechenbarkeit erläutert und nicht als fehlender Quellwert behandelt.

Die Antwortprüfung kontrolliert zusätzlich einzelne Regionsverwechslungen und bezieht Szenariojahre in die bestehende Jahresprüfung ein. Sie ist weiterhin kein vollständiger semantischer Beweis: Komplexe Sätze mit mehreren Orten oder Jahren können missverstanden werden. Deshalb bleiben die geprüften Tabellen und die sichtbare Auswahl maßgeblich.

## Prüfung und Gemini-Bewertung

Zwei ausschließlich lesende Gemini-3.8-Flash-Prüfungen mit Thinking High über den benannten Skill: zunächst Ursache und Entwurf, anschließend Implementierung. Bestätigte Hinweise wurden selbst nachgeprüft und korrigiert: explizite Einheit am Ausgangswert, Jahresmetadaten, Fremdregionenprüfung, Nullbasisstatus und Kennzeichnung von Prognose-/Rechenwerten. Die fehlende Einbindung in die alte `analytical_statements`-Funktion ist kein Ausfall der Kundenzusammenfassung: Die neue Präsentation erzeugt bereits vollständige Vergleiche je Region und Modus und stellt sie als Belege bereit. Der synthetische Dialogtest allein beweist kein Sprachverständnis; ergänzend wurden echte Modellläufe ausgeführt. Ungeprüfte pauschale Sicherheits- oder Freigabeaussagen aus Gemini wurden nicht übernommen. Kein vollständiger Gemini-Befund als Datei gespeichert.

Zehn neue Regressionen prüfen reale Quellwerte und Änderungsraten, Nullbasis und Fehlwerte, Mehrfachauswahl und Grenzen, Fortsetzung und Altkontext, Jahres-/Regionszuordnung, vollständige Belegabdeckung für fünf Regionen mit beiden Kennwerten und allen Modi sowie den speicherbaren Linux-Prüfbericht. Abschließend bestanden **129 Tests**, ohne Fehler oder Fehlschläge (`offline_complete.json`). Alle gebundenen Quellprüfsummen stimmen mit dem endgültigen Arbeitsstand überein. Der zunächst falsch gewählte Python-Modulaufruf der Einzelprüfung wurde auf die bestehende Test-Discovery korrigiert.

`after01.json`: sieben echte Eingaben, keine technischen Fehler. Der Dreischritt-Dialog, ein vollständiger Vergleich, Wechsel zu Empfang und beobachteten Daten sowie die korrekte Rückfrage zum nicht verfügbaren Prognosejahr 2035 wurden geprüft. Zwei freie Texte nannten vorhandene Zahlen ohne alle nötigen Belegkennungen; die vollständige feste Datenausgabe blieb verfügbar. Daraufhin wurden Basis, Ziel und Veränderungen je Region/Modus/Kennzahl in einem gemeinsamen Beleg zusammengefasst.

`after02.json`: vier weitere echte Eingaben, acht Modellaufrufe, alle Antworten frei und ohne Rückfall. Alle vier Texte wurden nach den abschließenden Gemini-Korrekturen erneut gegen frisch abgefragte Daten und die endgültigen Prüfregeln geprüft; bestanden ohne weitere Modellaufrufe (`revalidated_after02.json`). Lokale Modelltests führen keine Portalbuchungen aus. Der gesamte 45-Fälle-Katalog und eine vollständige Mobilabnahme sind damit nicht erneut ausgeführt.

Vorher-/Nachher-Modellläufe zusammen: 14 Eingaben, 25 Modellaufrufe, 357.342 gemeldete Tokens und 0,31283505 USD gemeldete Kosten (`model_usage.json`). Spätere Browseraufrufe im Portal sind darin nicht enthalten.

## Verifizierte Ausgangswerte

| Region | Kennwert | Prognosebasis 2019 | Prognose 2040 |
|---|---|---:|---:|
| Magdeburg | Schiene, Tonnen | 2.037.023 | 2.751.683 |
| Magdeburg | Schiene, Tonnenkilometer | 218.995.582 | 319.228.696 |
| Duisburg | Schiene, Tonnen | 22.506.890 | 26.407.912 |
| Duisburg | Schiene, Tonnenkilometer | 6.410.552.330 | 9.373.443.044 |

Richtungsbezug: VP-Gesamtverkehr, Binnenverkehr einmal. Keine beobachtete Entwicklung von 2019 bis 2040.

## Bereitstellung

Aktiv auf Testsite 1067000 ist `portal-test-20260914-gueterstroeme-forecast01`. Manifest SHA-256: `303d911316cc830432d56e879038b76c2b4dc674aeff610e471588e0b82c62dc`; 1.708 Dateien, 668.211.326 Bytes. Gegenüber semantic01 wurden elf Nutzdateien plus Manifest mit zusammen 506.692 Bytes übertragen, 1.697 Dateien unabhängig serverseitig kopiert und alle Zieldateien geprüft. API und Datenbank sind bereit; die monatliche KitaNavigator-Testaufgabe zeigt auf den neuen Release. Das Paket wurde aus dem vollständig verifizierten lokalen beta06-Bestand aufgebaut. Andere lokale Portaländerungen wurden nicht übernommen. Produktion unverändert.

Angemeldeter Chrome-Test im aktiven Release: Der exakte Dreischritt-Dialog wurde vollständig beantwortet. Schon die erste Frage lieferte beide Städte in Tonnen; die zweite ergänzte beide Verkehrsleistungen; „na 2040“ behielt beide Regionen und Kennzahlen bei. Alle drei Antworten wurden frei formuliert und stimmten mit den oben genannten Quellwerten überein, ohne Rückfrage oder technischen Fehler. Das Monatskontingent stieg je erfolgreicher numerischer Antwort genau einmal: 15 → 16 → 17 → 18. Fortschritt im Antwortbereich und Abschlussdarstellung visuell geprüft (`browser_final.json`).

Unauthentifizierte Zugriffe: Health 200, Kontingent 401, geschütztes JavaScript 403, privater Systemprompt 404; alle erwarteten Zustände bestätigt (`public_access.json`).

Die Linux-Prüfung bestand vollständig (`linux_corrected.json`): 1.708 Manifestdateien, 16 Prognosefakten, bestehende Dialog- und Datenregressionen, Migration 009, Kontingentpläne und bestehende Identitätszuordnung. Keine externen Modellaufrufe und keine Datenbankschreibvorgänge. Temporäre Prüfaufgabe, FTPS-Zugang sowie Status-, Sperr- und Fortschrittsdatei dieses erfolgreichen Laufs wurden entfernt.

Zwei vorausgehende Prüfversuche konnten ihren Bericht nicht speichern: Im hinzugefügten Prognose-Prüfblock überschrieb `expected` die Manifestkennung mit einem Wörterbuch mit Tupelschlüsseln; dessen spätere JSON-Ausgabe scheiterte außerhalb der Fehlerbehandlung. Die Wartefrist war deshalb nicht die eigentliche Ursache. Die Variable heißt nun `forecast_expected`; eine ausführende Regression prüft, dass Manifestkennung und Gesamtbericht serialisierbar bleiben. Die zusätzliche Fortschrittsanzeige und begrenzte längere Wartefrist erleichtern künftige Diagnosen. Der Portal-Laufzeitcode war davon nicht betroffen; eine weitere Bereitstellung war nicht nötig.

## Aufbewahrung und GitHub

Der geprüfte Bereinigungsplan behält forecast01 als aktiven Stand sowie semantic01 und chat01 als Rückfallstände. Die zusätzliche dauerhafte Löschung von beta06 ist angefragt, aber noch nicht freigegeben; deshalb bleiben vorerst vier Testreleases erhalten. `retention_plan.json` liegt bei den lokalen Nachweisen. Vor einer späteren Anwendung müssen aktive Site und Plan weiterhin übereinstimmen. Produktionsportal und Datenbank bleiben unberührt.

Quellen, Regressionen und Betriebsnachweise werden gemeinsam auf GitHub `main` gesichert. Commit-ID, Remoteabgleich und abschließende Bereinigungsnachweise stehen im lokalen `completion.json` und in der Übergabe. Andere lokale Portaländerungen bleiben erhalten und sind nicht Bestandteil dieses Commits.
