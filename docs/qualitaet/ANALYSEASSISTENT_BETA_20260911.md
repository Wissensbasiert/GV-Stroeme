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

Lokale Chrome-Prüfung mit echten Daten und künstlichem Kontingent: Beta-Knopf, Eingabe, Arbeitsanzeige, Jahresrückfrage ohne Zähleranstieg und entfernter technischer Nachweisbereich. Hover bei normaler Größe und 390 × 844 Pixeln visuell geprüft. Ein zunächst links abgeschnittener mobiler Hover wurde korrigiert und danach vollständig innerhalb des Dialogs bestätigt. Modellqualität stammt aus den getrennten echten Requesty-Läufen; die lokale Vorschau verwendet kein Modell.

Der unabhängige Testkandidat entsteht aus dem vollständig hashgeprüften aktiven ui10-Paket und dem neuen Fachpaket. Unbeteiligte Portaldateien bleiben bytegleich zu ui10; fremde lokale Portaländerungen werden nicht vermischt. Upload, Linux-/Liveabnahme und Aufbewahrung werden nach Abschluss ergänzt.

Ausführliche lokale Berichte: `C:/tmp/gueterstroeme-dialogue-20260911/` mit `baseline01.json`, `candidate01.json`, `candidate02.json`, `runtime01.json` bis `runtime04.json` und `release_validation.json`. Wesentliche Ergebnisse stehen hier dauerhaft in Git.
