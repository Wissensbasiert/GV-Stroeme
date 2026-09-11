# Analyseassistent: begrenzte Beta-Abnahme vom 11.09.2026

## Umsetzung und Grenzen

Der Ausbau umfasst Gesprächsführung, Beta-Kennzeichnung, Informationshover und Entfernung der sichtbaren Rubrik „Quellen und Nachweise“. Keine fachliche Gesamtfreigabe aller freien Fragen oder des gesamten 45-Fälle-Katalogs; Produktion bleibt unverändert.

- `availability.py` erstellt aus gebundenen Manifesten, Quellenjahresabdeckung und Klassifikationsregister einen kompakten Katalog: Verkehrsträger/Jahrgänge, regionale Abdeckung, Gütergruppen, VD2-/VD3c-Raumebenen und Jahre, Berliner Mautmonate und fachliche Grenzen. Die vorhandene gezielte Jahresprüfung ergänzt die Auswahl. Keine vollständigen Datenbestände, privaten Pfade oder Testreferenzen im Modellkontext. Ein Jahrgang belegt noch keinen Wert für jede Verbindung.
- `conversation.py` führt Ausgangsfrage, wirksame Frage, unabhängig belegte Parameter, offene Rückfrage und letzten Ergebnisbezug. Der Server signiert den auf zwei Stunden begrenzten Stand; der Browser hält ihn bis „Neuer Chat“ oder Neuladen. Keine alten Ergebniszahlen als neue Fachdaten. Jahreswechsel und Gegenrichtung werden daraus abgeleitet und neu abgefragt. Selbständige neue Anliegen erben die alte Auswahl nicht. Beliebige implizite Themenwechsel bleiben eine Grenze.
- Eng gefasste Standardfragen „Welche Güter gehen … per Schiene/Straße von … nach …?“ verwenden direkt die geprüfte Orts-, Richtungs- und Parameterprüfung. Andere freie Fragen verwenden die Modellplanung mit Verfügbarkeitskatalog.
- Die zweite Modellphase kann aktuelle belegte Erläuterungen frei verbinden. Fakten erscheinen über geprüfte Platzhalter; eigene numerische Angaben, fremde Belegkennungen und erkannte Ursachenbehauptungen werden verworfen. Tabellen, Einheiten und Pflichtgrenzen bleiben serverseitig. Keine vollständige semantische Garantie für beliebige Formulierungen; bei Modell-/Formatfehlern bleibt die feste Datenausgabe erhalten.
- Fehlender Eintrag, fehlende Abdeckung, unbekannter beziehungsweise explizit unterdrückter Quellwert und veröffentlichte Null bleiben getrennt. Bei passenden Datenlücken werden höchstens drei Alternativen abgefragt. Nur tatsächlich verfügbare Auswertungen werden angeboten; Ausführung erst nach Absenden.
- Im Hauptmenü steht „Beta“. Der Hover nennt Zweck, Gemini 3.7 Flash über Requesty, Datengrundlage und kritische Prüfung. Keine ungeprüfte Datenschutzbehauptung. Kartenfilter werden nicht übernommen. Interne Quellen-/Prüfinformationen bleiben erhalten, die technische Rubrik in den sichtbaren Antworten entfällt.

## Lokale Prüfung und echte Modellläufe

77 Laufzeitprüfungen bestehen: bisherige Fachregressionen, HTTP-/Portalzugriff, Kontingente und zusätzliche Tests für signierten Stand, Manipulation, neues Thema, Jahreswechsel, Gegenrichtung mit echten Daten, belegte Alternativen und unzulässige Erläuterungen. Rückfragen und reine Datenlücken buchen weiterhin keine fertige Analyse.

Daten aus dem bestehenden ui10-Fachpaket; benötigte Originalreferenzen ausschließlich lesend übernommen. Temporäre Bestände unter `C:/tmp`. Im Zwischenvergleich änderte allein die Zeilenumbruchform der Darstellungsreferenz die technische Datenkennung von `205f56cd7dca3225c3b4f120` auf `58d780a273b23b4cb7e64848`; JSON-Inhalt und alle sechs Datenstandsverweise sind gleich. Der endgültige Kandidat übernimmt unveränderte Originalbytes.

Requesty-Konfiguration unverändert: `vertex/gemini-3.7-flash@eu`, 1.500 maximale Ausgabetokens, bestehender EU-Endpunkt. Sechs identische Eingaben je Vergleich, keine Portalkontingentbuchung und keine automatische Wiederholung.

| Messwert | ui10 | Abschließend geprüfter Ausbau |
|---|---:|---:|
| Nutzereingaben | 6 | 6 |
| Rückfragen | 1 | 1 |
| Technische Fehler | 1 | 0 |
| Modellaufrufe einschließlich Fehler | 8 | 6 |
| Tokens einschließlich vorhandener Fehlerdiagnostik | 54.903 | 24.311 |
| API-Kosten in USD | 0,067451175 | 0,032137875 |
| Gesamte Analysezeit | 63,297 s | 39,923 s |

Die einzige Rückfrage betrifft das fehlende Jahr. Der alte Gegenrichtungsaufruf wurde wegen Ausgabelänge abgebrochen. Auch ein erster Ausbauversuch scheiterte bei der Jahreslücke daran; `candidate01.json` bleibt als Fehlversuch erhalten. Nach Ergänzung der direkten Standardzuordnung besteht der abschließende Vergleich. Dies sind Stichproben, keine zugesicherten Laufzeiten, Kosten oder allgemeinen Erfolgsquoten.

| Verlauf | Belegtes Ergebnis des endgültigen Laufs |
|---|---|
| Berlin → Hamburg, Güter per Schiene, ohne Jahr | Nur Jahresfrage; neuester vollständiger Jahrgang 2025 |
| „Das aktuellste Jahr“ | 2025, Berlin → Hamburg; 240.297 Tonnen Summe verfügbarer veröffentlichter Feinpositionen |
| „Und in Gegenrichtung?“ | 2025, Hamburg → Berlin; 585.052 Tonnen derselben Teilmengenabgrenzung |
| „Und 2024?“ | Gegenrichtung bleibt erhalten; 554.806 Tonnen für 2024 |
| Köln → Hamburg per Binnenschiff 2024 | Fehlender Eintrag, kein Nullnachweis; Schiene und Straße separat als vorhandene Alternativen geprüft |
| Berlin → Hamburg per Schiene 2026 | Nicht abgedeckter Jahrgang; 2025 für dieselbe Auswahl tatsächlich abgefragt und angeboten |

## Browser und Testrelease

**Nachträglicher Nutzerbefund:** Die nachfolgend dokumentierte Sichtprüfung von beta02 übersah eine fehlerhafte Gliederung: Die Antwort zeigte sieben aggregierte Güterarten und anschließend deren NST-Einzelpositionen in derselben Tabelle. Es handelte sich um überlappende Mengen, nicht zusätzliche Güter. Die Mengenberechnung war unverändert; die damalige Sichtprüfung war in diesem Punkt unzureichend. Die Korrektur für beta03 beschränkt Standardtabelle und Sprachbelege auf sieben Güterarten plus gekennzeichnete Summe. Interne Einzelfakten und Nachweise bleiben vollständig. Bei ausdrücklicher NST-Auswahl erscheinen nur die ausgewählte Feinposition und die Summe, bei einer Güterartenauswahl nur diese Güterart und die Summe. 78 lokale Prüfungen bestehen einschließlich dieser Abgrenzungen; abschließender echter Modelllauf und Liveprüfung folgen.

Lokale Chrome-Prüfung mit echten Daten und künstlichem Kontingent: Beta-Knopf, Eingabe, Arbeitsanzeige, Jahresrückfrage ohne Zähleranstieg und entfernter technischer Nachweisbereich. Hover bei normaler Größe und 390 × 844 Pixeln visuell geprüft. Ein zunächst links abgeschnittener mobiler Hover wurde korrigiert und danach vollständig innerhalb des Dialogs bestätigt. Modellqualität stammt aus den getrennten echten Requesty-Läufen; die lokale Vorschau verwendet kein Modell.

Der unabhängige Testrelease `portal-test-20260911-gueterstroeme-beta02` ist auf Testsite **1067000** aktiv. Er entstand aus dem vollständig hashgeprüften ui10-Paket und dem neuen Fachpaket. Unbeteiligte Portaldateien bleiben bytegleich zu ui10; fremde lokale Portaländerungen wurden nicht vermischt. Manifest: `259672b8e611a9b5a551114444e2a68370862de8124a8081e15b1ce3e2bd47e9`, 1.706 Dateien, 668.100.601 Bytes. Delta: 16 geänderte Dateien plus Manifest hochgeladen (1.246.055 Bytes), 1.690 unveränderte Dateien serverseitig unabhängig kopiert. Alle Zieldateien geprüft. API/Datenbank gesund; bestehende monatliche Kita-Aufgabe 30833 zeigt auf denselben neuen Release.

Die zusätzliche Linux-Prüfung bestätigt erneut alle 1.706 Dateien, Python 3.13.15, DuckDB 1.2.1, jsonschema 4.25.1, psycopg 3.2.10, Migration 009, Basic 5/Premium 50 sowie die konfigurierte Modellkennung. Jahresdialog, signierte Gegenrichtung mit 585.052 Tonnen und die tatsächliche Alternative 2025 zur Jahreslücke 2026 bestehen direkt auf dem Server. Diese Prüfung verwendet synthetische Modellpläne mit echten Daten und verursacht keine Modellaufrufe oder Datenbankänderungen. Temporäre Aufgabe, FTPS-Zugang, Ergebnisdatei und Startsperre vollständig entfernt.

Angemeldete Chrome-Liveabnahme: Startverbrauch 3/50; Jahresrückfrage unverändert 3/50; „Das aktuellste Jahr“ liefert 240.297 Tonnen und 4/50; „Und in Gegenrichtung?“ liefert Hamburg → Berlin 2025 mit 585.052 Tonnen und 5/50, anschließend 45 verfügbar. Richtung und Güterauswahl wurden nicht erneut erfragt. Beta-Kennzeichnung und Modellhover sichtbar; keine aufklappbaren technischen Nachweisbereiche in den Antworten. Quellen-/Gültigkeitsgrenzen stehen direkt in der Ausgabe. Die zusätzlichen Browser-Modellkosten wurden nicht separat aus Provider-Audits ausgelesen und sind nicht Bestandteil des lokalen Vergleichs.

Öffentlicher Zugriffsschutz: Health 200, Kontingent ohne Anmeldung 401, Dashboard-JavaScript ohne Werkzeugzugriff 403, private Gesprächsdatei 404. Keine Produktionsbereitstellung. Implementierung auf GitHub `main`: `5831a06b3f32ed44fd25622567f70b4f4026fbd6`; spätere Abschlussdokumentation liegt darüber.

**Aufbewahrung abgeschlossen:** aktiver Beta-Release plus ui10 und ui09. Alle 5.111 Manifestdateien der drei erhaltenen Releases geprüft. Ausschließlich ui07 nach erneuter Verweisprüfung entfernt; anschließend genau drei Testreleases vorhanden. Aktiver Pfad, Produktionssite und Gesundheitsstatus unverändert; temporärer FTPS-Zugang entfernt. Eigene lokale Vorschau beendet; temporäre Pakete werden nach hashgeprüfter Archivierung der Berichte entfernt.

Ausführliche Berichte werden nach Bereinigung unter `outputs/analyseassistent_beta_20260911/` aufbewahrt: Vorher-/Nachherläufe einschließlich Fehlversuch, lokale Prüfungen, Gate, Release-Manifest, Linux-/Zugriffsprüfung und Aufbewahrungsnachweise. Wesentliche Ergebnisse stehen hier dauerhaft in Git. Der temporäre erste Beta-Paketentwurf wurde nicht veröffentlicht.

## Abschluss der Gütergliederungskorrektur: beta03

Die obigen beta02-Angaben sind der historische Zwischenstand. Maßgeblicher aktiver Testrelease ist jetzt `portal-test-20260911-gueterstroeme-beta03` (Testsite 1067000). 78 lokale Prüfungen bestehen; die neue Prüfung bestätigt sieben aggregierte Güterarten plus Summe, unveränderte Mengen, erhaltene interne NST-Fakten, keine NST-Positionen im Sprachbelegpaket sowie gesonderte Ausgaben für ausdrücklich ausgewählte Feinpositionen oder Güterarten.

Ein zusätzlicher echter Requesty-Lauf zur Frage „Welche Güter gehen 2025 per Schiene von Berlin nach Hamburg?“ bestätigt genau acht Tabellenzeilen und ausschließlich aggregierte Güterangaben im Text: Maschinen und Ausrüstungen, langlebige Konsumgüter 2.010 Tonnen; sonstige Produkte 238.287 Tonnen; Summe der verfügbaren Güterangaben 240.297 Tonnen. Fehlende Angaben bleiben unbekannt. Ein Modellaufruf, 3.171 Tokens, 0,004995375 USD, 9,016 Sekunden gesamte Analysezeit; keine Portalkontingentbuchung. Modellkonfiguration unverändert.

Neues Manifest `830ebbad5b6c570817b2c2a56ad067004c655f0f3d90e660dbf726cc2a3e0818`: 1.706 Dateien, 668.102.272 Bytes. Gegenüber dem aktiven beta02 wurden drei Nutzdateien plus Manifest übertragen (363.061 Bytes); 1.703 unveränderte Dateien wurden serverseitig unabhängig kopiert. Alle Hashes stimmen. API und Datenbank gesund; Kita-Aufgabe 30833 auf demselben neuen Release. Linux-Prüfung bestätigt zusätzlich alle Dateien, die unveränderte Umgebung, den Jahresdialog, die Gegenrichtung und die geprüfte Datenalternative. Temporäre Serverprüfmittel entfernt. Öffentlicher Zugriffsschutz erneut mit erwarteten Statuscodes 200/401/403/404 bestanden.

Angemeldete Chrome-Liveprüfung derselben Frage nach Neuladen: genau sieben Güterarten plus Summe, keine NST-Zeilen oder NST-Angaben im Fließtext, identische Mengen. Tabellenanfang und -abschluss visuell geprüft. Verbrauch 5/50 → 6/50, 44 verfügbar. Die zusätzliche Provider-Nutzung dieses Browseraufrufs wurde nicht separat ausgelesen. Die vorherige Sichtprüfung hatte diesen Gliederungsfehler übersehen; daraus wird keine vollständige fachliche Abnahme anderer Antworten abgeleitet. Produktion unverändert.

Aufbewahrung abschließend geprüft: beta03 aktiv, ui10 und ui09 als zwei technisch geprüfte Rückfallstände; alle 5.111 erhaltenen Manifestdateien bestätigt. Diese Rückfallstände enthalten noch die frühere Darstellungsgrenze. Ausschließlich beta02 wurde nach erneuter Verweisprüfung entfernt. Genau drei Testreleases verbleiben; aktive Konfiguration, Produktion und Gesundheitsstatus unverändert, temporärer FTPS-Zugang entfernt.

Die Berichte einschließlich der früheren Fehlversuche sind unter `outputs/analyseassistent_beta_20260911/` hashgeprüft archiviert. Sieben eigene temporäre Paket-/Arbeitsordner unter `C:/tmp` und sämtliche neun Hilfsdateien dieser Arbeit entfernt; vorbestehende Arbeitsbestände erhalten. Keine Vorschau oder temporäre Serveraufgabe bleibt aktiv. Die Korrektur und dieser Abschluss werden gemeinsam im nachfolgenden Git-Commit auf `main` gesichert; der Commit ist über diese Datei auffindbar.

## Mehrjahresauswertung und rechnerische Veränderung: beta04

Der Nutzerhinweis zur zu vorsichtigen Einordnung wurde umgesetzt. Wenn Anfangs- und Endwert derselben veröffentlichten Reihe vorliegen, berechnet der Server die prozentuale Veränderung und bezeichnet sie als rechnerisches Wachstum beziehungsweise rechnerischen Rückgang der veröffentlichten Werte. Daraus werden keine Ursache und keine methodisch bereinigte Entwicklung abgeleitet. Fehlende Einträge werden nicht als null behandelt: Die Antwort sagt, dass in der zugrunde liegenden Statistik kein nutzbarer Güterverkehrswert erfasst beziehungsweise veröffentlicht ist, und ergänzt, dass dies tatsächlich stattgefundenen Verkehr nicht ausschließt.

Der gemeldete Fall „Wie viel Güter sind in den letzten Jahren von Rosenheim nach Augsburg transportiert worden?“ wird ohne Einzeljahres-Rückfrage als gerichtete Mehrjahresrelation 2020–2024 beantwortet. Für die Schiene stehen 2.175 Tonnen im Jahr 2020 und 1.066 Tonnen im Jahr 2024 gegenüber; daraus ergibt sich ein rechnerischer Rückgang um 50,99 %. Straße und Binnenschiff werden wegen fehlender nutzbarer Werte nicht in einen scheinbar vollständigen Verkehrsträgervergleich einbezogen.

`growth_validation01.json` bestätigt 83/83 lokale Prüfungen. Der neue Testrelease `portal-test-20260911-gueterstroeme-beta04` ist auf Testsite 1067000 aktiv. Manifest `4d2cc83bb1e65b491486cdff58f887186e49e570e4387f86377e266276f5f6d6`: 1.706 Dateien, 668.142.171 Bytes. Gegenüber beta03 wurden 64 geänderte Nutzdateien plus Manifest übertragen (2.068.216 Bytes), 1.642 unveränderte Dateien serverseitig unabhängig kopiert und danach alle Zieldateien geprüft. API und Datenbank sind gesund; Kita-Aufgabe 30833 zeigt auf denselben Release.

`linux_growth_validation02.json` bestätigt direkt in der aktiven Linux-Laufzeit alle 1.706 Dateien, Python 3.13.15, DuckDB 1.2.1, jsonschema 4.25.1, psycopg 3.2.10, Migration 009, Basic 5/Premium 50, den signierten Dialogzustand und den konkreten Rosenheim–Augsburg-Fall einschließlich 50,99 % Rückgang. Keine Modellanfrage, Kundenbuchung oder Datenbankänderung. Temporäre Aufgabe, Ergebnisdatei, Startsperre und FTPS-Zugang wurden entfernt.

Aufbewahrung abschließend geprüft: beta04 aktiv, beta03 und ui10 als zwei vollständig geprüfte Rückfallstände. ui09 wurde ausschließlich nach dem gespeicherten und erneut abgeglichenen Plan entfernt. Es verbleiben genau drei Testreleases; Produktion und Gesundheitsstatus sind unverändert. Eine neue angemeldete Browserprüfung oder 45-Fälle-Gesamtabnahme wurde nicht durchgeführt.
