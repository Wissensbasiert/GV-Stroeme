# Analyseassistent 0.6.0: Gegenräume, Gesamtsummen und lesbare Antworten

Stand: 14.09.2026. Version 0.6.0 als `portal-test-20260914-gueterstroeme-scope01` auf Testsite 1067000 aktiv. 189 lokale Tests, Linux-Nachprüfung und Browserprüfung bestanden. Produktion unverändert und nicht für diesen Umbau freigegeben.

## Ergebnis und Datenabgrenzung

- `Inland` bedeutet Deutschland, `Ausland` außerhalb Deutschlands. Eine Jahresrückfrage und anschließendes „Und ins Inland?“ erhalten bzw. ändern genau diesen Filter. „Externe Partner“ ist weiterhin nicht gleichbedeutend mit Ausland.
- Gesamtverkehr und Güterstruktur sind unterschiedliche Fragen. `transport_history` beantwortet die Entwicklung des gesamten regionalen Güterverkehrs mit fünf sichtbaren Jahreswerten und ausklappbaren Verkehrsträgerdetails, statt eine unbestellte Gütergruppenliste mit 273 Werten auszugeben.
- Tonnen-Gesamtwerte gleicher Auswahl werden serverseitig über Verkehrsträger summiert. Fehlende Werte bleiben unbekannt; vorhandene Teilmengen heißen ausdrücklich Teilsumme. Kombinierte Transportketten können mehrfach erfasst sein; der Hinweis verbietet nicht die statistische Summe. KV-Teilmärkte und Tonnenkilometer werden weiterhin nicht vermischt oder addiert.
- Kurze Kernaussage, Aufzählungen und Detailtabelle sind getrennt. Der sichere Renderer unterstützt auch einen Einleitungssatz mit anschließender Liste im selben Absatz. Die Ersatzantwort zu einer Güterstruktur zeigt maximal drei führende Gruppen.

Keine Datenmigration, keine neue Datenaufbereitung und keine neuen Abhängigkeiten. Die Abfragen filtern die vorhandenen gerichteten B01-Daten und nutzen die bestehenden Regionalprofile. Datenstand `ee6a63245684af9920c961a3` unverändert. Güterprognosen/NST/Hafen/KV-Zugriffe aus Version 0.5.0 bleiben angebunden.

### Nachgerechnete Originalfälle

| Auswahl | Ergebnis |
|---|---:|
| Duisburg, Binnenschiff, Versand 2025, alle Ziele | 8.288.992,40 t |
| Davon Ausland | 5.915.781,20 t |
| Davon Inland | 2.373.211,20 t |
| Berlin, Versand plus Empfang, drei Landverkehrsträger, 2020 | 83.255.517,40 t |
| Dieselbe Auswahl, 2024 | 71.741.627 t |
| Veränderung 2020–2024 | −11.513.890,40 t / −13,83 % |

Duisburg unabhängig gegen das ISO-Länderfeld des amtlichen IWW-CSV 2025 geprüft, einschließlich aller sieben Gütergruppen. Im Ausland führt **Sonstige Produkte**, nicht Metalle: 2.217.138,20 t gegenüber 2.062.879 t Metallen. Die ursprüngliche Antwort hatte ungefilterte Regionalwerte als Auslandsverkehr ausgegeben. Berliner Jahressummen 2021/2022/2023: 81.891.720 / 80.390.334 / 73.057.305 t. Für 2025 fehlt Straße; die vollständige Dreimodalsumme und ihre Fünfjahresveränderung bleiben unbekannt. Der Assistent ersetzt 2025 nicht heimlich durch 2024.

Wichtige Grenze: Ungefilterte Regionalprofile zählen bei Versand plus Empfang innerregionale Verkehre zweimal. Die gerichtete B01-Auswahl mit beiden Richtungen zählt jede Relation einmal. Beide Zählweisen werden im Ergebnis offengelegt; keine pauschale Additivitätsbehauptung zwischen diesen Auswahlen. Gefilterte C7-Strukturen liegen für Schiene und Binnenschiff vor, nicht für Straßen-OD. Unbekannte Partnercodes sind kein Ausland. Quellenkennzeichen werden weitergegeben, fehlende Randjahre und unterdrückte Werte nicht durch null ersetzt.

## Prüfungen und eigene Bewertung

1. Lokale Originaldaten- und Dialogregression: Summen, Anteile, führende Gruppe, Versand/Empfang, Filtervererbung, widersprüchlicher Funktionswechsel, explizite Jahre, fehlende Straße 2025, überlappende Gruppen, KV-Abgrenzung, Kurzbelege und Unicode-Minus.
2. Erste echte Modellserie: sechs Fragen, zehn Modellaufrufe, 0,24754785 USD, keine Kundenbuchung. Duisburg und Berlin wählten die richtige Funktion und Auswahl; vier Zahlenantworten nutzten die abgesicherte Ersatzformulierung wegen unvollständiger Belegzuordnung. Die benannte Inlandsrelation benötigte zunächst unnötig eine Rückfrage. Alle Ausgaben wurden gelesen.
3. Daraufhin Belegpakete pro Verkehrsträger, zulässige Kurzformen und Unicode-Minus ergänzt; konsistente Länderangaben bei vollständig benannten neuen Relationen erlaubt. Drei gezielte echte Nachprüfungen: sechs Modellaufrufe, 0,11470107 USD, drei beleggeprüfte freie Antworten, keine Kundenbuchung. Zahlen und Richtung stimmen. Der Duisburg-Text wiederholte noch alle sieben Gruppen; die anschließende Längenregel leitet solche Antworten zur knappen, geprüften Top-3-Ersatzantwort um. Dieser letzte Darstellungsfilter wurde ohne weitere kostenpflichtige Wiederholung geprüft. Keine Behauptung, dass jede Modellantwort automatisch knapp ausfällt.
4. Zwei unabhängige, ausschließlich lesende Gemini-Prüfungen mit Antigravity/Gemini 3.8 Flash High: erste Prüfung bestätigte fehlende Raumsemantik, falsche Gesamtverkehrszuordnung und unnötigen Textzwang; zweite meldete keine belegten Codefehler. Rohdaten und Laufzeit waren für Gemini nicht zugänglich. Eigene Nachprüfung ergänzte danach insbesondere Quellen-/Qualitätsweitergabe, kompatible benannte Relationen und gemischte Einleitungs-/Listenblöcke. Geminis Urteil ist keine Laufzeitfreigabe und keine Garantie fehlerfreier Antworten.
5. Lokale Browserprüfung mit tatsächlich gespeicherter Berliner Modellantwort, echtem Antwort-Renderer und Projekt-CSS, ohne externe Anfrage: drei echte Listenpunkte, fünf sichtbare Jahreswerte, 23 ausklappbare Detailwerte und klarer Summenhinweis. Der lokale Prüfraum ist keine vollständige Portalabnahme.

Lokale ausführliche Nachweise: `outputs/analyseassistent_scope_20260914/`. Dort verbleiben Modellberichte lokal; keine Zugangsdaten oder Rohantwortprotokolle im öffentlichen Portal/Git. Der wiederholbare Prüfeinstieg ist `scripts/validation/validate_assistant_runtime.py`; die Originalfälle stehen in `tests/analyseassistent/test_transport_scope.py`.

## Was verhindert weitere ähnliche Fehler?

Kein einzelner Prompt garantiert korrekte beliebige Freitexte. Deshalb mehrere überprüfbare Schutzschichten: quellgebundenes Feldinventar aus 0.5.0, explizite Datenfunktionen und Verfügbarkeitskatalog, gespeicherte Auswahl einschließlich Gegenraum/Zeit, serverseitige Summen und Qualitätskennzeichen, beleggebundene Textprüfung mit sicherer Ersatzantwort sowie dauerhafte Regression der gemeldeten Dialoge. Neue Datenfelder ohne Zuordnung sperren den entsprechenden Datenaufbau. Noch nicht unterstützte Kombinationen müssen als konkrete Grenze erscheinen, nicht als pauschal fehlende Daten.

Nicht beansprucht: vollständige Fachabnahme aller beliebigen Formulierungen oder des gesamten 45-Fragen-Katalogs, Harmonisierung der historischen Gebietsstände, eindeutige Transportkettenmengen oder Produktionsfreigabe.

## Abschluss der Testbereitstellung

- Aktiver Testrelease: `portal-test-20260914-gueterstroeme-scope01`, 1.731 Dateien, 750.534.456 Bytes. Manifest `5adde8a92e25c8941a5a2fbe335a525cfa84595a05bfbeff1707f624a2d34be2`.
- Eigenständiger Delta-Release aus access04: 17 geänderte Nutzdateien plus Manifest hochgeladen (1.184.555 Bytes), 1.714 unveränderte Dateien unabhängig serverseitig kopiert; alle Prüfsummen bestätigt. Kein Überschreiben oder Hardlink des aktiven Ausgangsreleases.
- `offline04.json`: 189 Tests, null Fehler/Ausfälle. `linux02.json`: sämtliche 1.731 Dateiprüfsummen, alte Prognose-/NST-/Hafen-/KV-Zugriffe, Leipzig- und Mehrjahresdialoge sowie neue Berlin-/Duisburg-Fälle bestanden. Python 3.13.15 unter Linux, DuckDB 1.2.1. Keine Modellaufrufe und keine Datenbank-Schreibzugriffe in dieser Nachprüfung. Die erste Linuxprüfung brach an der alten Erwartung von 15 statt 15 Einzel- plus 5 Summenwerten ab; der Prüfer prüft nun beides ausdrücklich. Keine nachträgliche Anwendungsänderung am aktivierten Release.
- Frisch geladene angemeldete Portalansicht und KI-Dialog geöffnet. Kontingent blieb bei 28 von 50 Fragen; keine Kundenbuchung durch diese Arbeit. Die konkrete Listen-/Tabellendarstellung wurde lokal mit gespeicherter echter Antwort geprüft, nicht durch einen weiteren bezahlten Portalchat. Der vorhandene alte Nutzerchat blieb in seiner Registerkarte erhalten.
- Serverinventuren vor/nach Übertragung verglichen: alle sieben bisherigen Releases mit unveränderten Dateizahlen, Größen und Manifesten erhalten. Produktion unverändert, API und Datenbank bereit. Alle temporären Serverjobs, FTPS-Zugänge und Prüfdateien entfernt. Lokalen Vorschauprozess beendet und die eigene Vorschau geschlossen.
- Ausführliche Nachweise bleiben lokal unter `outputs/analyseassistent_scope_20260914/`; die Dokumentation und Regressionstests gehören zur regulären Git-Sicherung, nicht die Modellprotokolle oder Datenbestände.
