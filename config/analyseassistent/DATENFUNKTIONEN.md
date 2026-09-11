# Fachlicher Vertrag der Datenfunktionen

**Version 0.1.0 · 09.09.2026 · Spezifikation, keine ausführbare Implementierung.** Alle Funktionen sind zunächst deaktiviert. Freigabe und Verfügbarkeit gelten je Filterkombination, nicht pauschal je Funktionsname.

## Gemeinsame Eingaben

| Angabe | Verbindliche Behandlung |
|---|---|
| Gebiet | Gebietstyp und bestätigte ID als Text; Namen über freigegebene Metadaten auflösen. Gleichnamige oder unterschiedlich abgegrenzte Treffer erfragen. |
| Zeit | Explizites Jahr/Jahrespaar oder Monatspaar. Ein erlaubter Standard „letztes gemeinsames vollständiges Jahr“ benötigt einen zuvor festgelegten Produktstandard und einen Verfügbarkeitsnachweis; Standardannahme sichtbar ausgeben. |
| Modus und Einheit | Fachlich erlaubte Kombination; t, tkm, Fahrten, Ladeeinheiten, TEU, Flüge getrennt. |
| Richtung und Binnen | Versand, Empfang, beide Richtungen oder Saldo; Binnenbehandlung zusätzlich ausdrücklich festlegen. |
| Güter | ALL, C1–C7 oder belegte NST-Tiefe; keine Aufteilung aus gröberen Gruppen erfinden. |
| Partnerauswahl | Konkrete OD oder Fokusregion; extern und international getrennt. International bedeutet bestätigter Länderfilter, nicht bloß anderer Flughafen. |
| Ranking | Rangmaß, Top-N, Gleichstandsregel und gegebenenfalls ausdrücklich vereinbarte Mindestbasis. |
| Kontext | Bestätigte Auswahl versus Modellvorschlag getrennt; widersprüchliche aktive Filter nicht still übernehmen. |

Der Server validiert alle Eingaben gegen eine Positivliste. Ein Modellvorschlag kann keine Datenquelle, Quelldatei, freie Abfrage oder unbekannte Funktion freischalten. Bei mehreren unabhängigen Fragen in einem Satz zunächst einen angebotenen kombinierten Vertrag nutzen oder den Umfang klären; keine unbeschränkte Agentenschleife.

## Fünfzehn Funktionen und die vorhandenen Testfälle

Die Funktionsnamen sind vorgeschlagene interne Namen. Datenquellen D01–D10 entsprechen dem Etappe-1-Detailkonzept.

| Typ / Funktion | Fachliche Verarbeitung und Datenbasis | Besondere Grenze | Tests |
|---|---|---|---|
| F01 `get_region_profile` | D01/D03/D05/D04; Profil aus Menge, Modal-/Güterstruktur, Richtungen und getrenntem VP-Pfad zusammensetzen | Profilumfang und abweichende Modulfilter offenlegen; keine Standortbewertung ohne Vergleich | T01–T03 |
| F02 `get_relations` | D02/D04; vollständige OD filtern, Partner aggregieren, dann Rangfolge und passende Anteile berechnen | Konkrete Verbindung auch außerhalb Top-Liste; Binnen und Qualitätsflags erhalten; kein Straßen-OD-Güterdetail | T04–T06 |
| F03 `compare_regions` | D01/D02/D04/D10; mindestens zwei vergleichbare Gebiete, gleiche Filter und gemeinsames Jahr; absolute Unterschiede und Strukturvergleich | Ganze Regionsverbünde gesondert nach OD bilden; keine Flächenverteilung auf geschnittene Teilgebiete | T07–T09 |
| F04 `get_time_series` | D01/D02/D04; gleiche Filter über bestätigte Zeitabdeckung, Lücken und Brüche mitführen | Vorhandene Jahreszeile allein belegt keine Vergleichbarkeit oder Ursache | T10–T12 |
| F05 `get_change_ranking` | Vergleichbare vollständige Auswahl, Änderungen vor Rundung sortieren; Basiswerte, absolute und relative Änderung ausgeben | Kleine Basis, Nullbasis und fehlende Basis getrennt; Anteilsanstieg ist kein Mengenanstieg | T13–T15 |
| F06 `get_goods_structure` | D01/D04; regionale Güter je Richtung aggregieren; aktueller C-Crosswalk | Straße NUTS-3 sieben Gruppen; ALL im Regional-Parquet ist keine fein gegliederte Straßenquelle | T16–T18 |
| F07 `get_relation_goods` | D02/D04; genaue OD und Richtung, C-Gruppen oder tatsächlich vorhandene Schienen-/IWW-Details | Straße konkrete OD nur ALL; fehlende Güterzeilen nicht nullsetzen | T19–T21 |
| F08 `get_modal_split` | Regional D01 oder national D03; passende drei Landverkehrsträger und Einheit; Nenner vollständig prüfen | Kein vollständiger Split aus nur zwei Modi; Salden ohne Modal Split | T22–T24 |
| F09 `get_direction_balance` | D01/D02/D04; Versand, Empfang, Saldo und Binnen explizit; nationalen Transit aus belegter Verkehrsbeziehung | Keine örtliche Durchfahrt aus außerhalb liegenden Endpunkten ableiten | T25–T27 |
| F10 `get_forecast_comparison` | D05; 2019_BASE und 2040_P1; ggf. D01-Ist getrennt daneben | VP-Binnen einmal, D01 in beiden Richtungen; keine weiteren Szenarien oder Zwischenprognosen | T28–T30 |
| F11 `get_intermodal_markets` | D06; jeweiliger Teilmarkt/Zähler und kompatibler modaler Nenner, national oder richtungsbezogen regional | Schiene und Binnenschiff nicht additiv; kein Verlagerungspotenzial | T31–T33 |
| F12 `get_node_statistics` | D07/D08/D04; eindeutig benannter Hafen/Flughafen, Profil oder Partnerliste; Kennzahl und Richtung getrennt | t, TEU, Flüge mit eigener Zeitabdeckung; internationale Nenner aus vollständigen publizierten Rohrelationen | T34–T36 |
| F13 `get_monthly_comparison` | D04 oder festes D09-Abbild; vollständige Monatsfolge bzw. bestätigtes Vorjahresmonatspaar | Keine Live-Massenabfrage; keine Personalplanung aus statistischen Monatswerten | T37–T39 |
| F14 `get_road_details` | Vorhandenes KBA VD2 oder VD3c; amtliche Klassen, NUTS-Ebene, deutsche Lkw, Inland/Gesamt und ZS-Felder | Andere Fahrzeugpopulation als VE; keine Übertragung auf nicht belegte Raum- oder OD-Ebene | T40–T42 |
| F15 `explain_data_scope` | Quellenregister und konkrete Ergebnisbelege; Herkunft, Zählweise, Machbarkeit, Grenzen und Reproduzierbarkeit | Keine externe Datenerweiterung als Folgeauftrag; fehlende Daten nicht mit allgemeinem Modellwissen ersetzen | T43–T45 |

## Gemeinsamer Ergebnisvertrag

Jedes Ergebnis besitzt `result_id`, `data_snapshot_id`, `rules_version`, `function_id`, normalisierte Eingaben mit Herkunft und einen Status: `ok`, `partial`, `needs_clarification`, `not_available`, `out_of_scope` oder `error`. `ok` bezeichnet eine bestandene Ergebnisprüfung, keine allein aus der Funktionsausführung abgeleitete Freigabe.

Eine Zahl wird nicht als nackter Wert weitergereicht. Jeder Fakteneintrag enthält mindestens:

- `fact_id`, ungerundeter `value` oder `null`, `unit`, `scale` und serverseitig erzeugtes `display_value`;
- Gebietstyp und -kennung, Bezugszeit, Verkehrsträger, Richtung, Güter und Binnen-/Zählweise;
- Population und Erfassungsbereich, insbesondere Inland/Gesamt und deutsche/europäische Lkw;
- `value_status`, numerischer Verfügbarkeitsstatus und Qualitätsstatus gemäß Fachregeldatei; originales Quellenzeichen mit dessen geprüfter Definition;
- Datenquelle und Originalherausgeber, Quelldatei-/Datenstandskennung, tatsächlich berechnete Prüfsumme und Datum der Quellenfassung;
- bei Ableitungen Formelkennung und Referenzen auf die Eingabefakten; bei Anteilen zusätzlich Nennerkennung, Nennerwert und dessen exakt beschriebene Grundgesamtheit;
- zeitliche und räumliche Vergleichbarkeit, Vollständigkeit und zwingende methodische Hinweise.

Eine veröffentlichte Teilmenge kann einen explizit so bezeichneten Bezugsrahmen bilden. Sie darf nicht zum gesamten realen Verkehr umbenannt werden. Sind benötigte Komponenten innerhalb des behaupteten Bezugsrahmens unbekannt, ist dessen vollständiger Gesamtwert nicht belegt. Die Summe vorhandener Zeilen darf dann nur als solche erscheinen.

Öffentliche Quellenhinweise werden aus einem geprüften Register erzeugt; interne Pfade und Prüfsummen bleiben bei Bedarf im Prüfprotokoll. Knoten- und Gebietsnamen stammen aus Metadaten, nicht aus dem Gedächtnis des Modells. Die Tabellen werden aus dem Serverergebnis erzeugt, nicht aus einem vom Modell nachgebauten Zahlenblock.

## Vertrag zwischen Server und Modell

**Planphase:** `phase`, `function_id`, `parameters`, `parameter_origins`, `unresolved_fields`, `status`. Jedes Parameterfeld stammt aus einer expliziten Nutzerangabe, bestätigtem Kontext oder einem benannten erlaubten Standard. Der Server darf keine allein vom Modell behauptete Parameterherkunft als Bestätigung werten. Er gleicht sie mit der Anfrage und dem gespeicherten Kontext ab. Eine syntaktisch gültige Ortskennung allein beweist noch nicht die richtige Ortsauswahl.

**Antwortphase:** Eingabe sind das aktuelle Ergebnis, erlaubte Tabellen und serverseitig vorgeprüfte Aussagen. Jede Aussage besitzt eine ID, eine Aussageart, Faktenbelege, einen festen Satzbaustein und geprüfte Voraussetzungen. Ein Satz „A hat mehr als B“ wird nur angeboten, wenn beide Werte verfügbar, kompatibel und A > B sind. Gleichstände und methodisch nicht vergleichbare Werte erhalten eigene Bausteine.

Modellausgabe: `result_id`, `data_snapshot_id`, geordnete `statement_ids` (höchstens vier), `table_ids` und `wording_variant` (`compact` oder `neutral`). Keine weiteren Felder, Zahlen, HTML oder freien Tatsachensätze. Der Server prüft Kennungen gegen genau dieses Ergebnis, entfernt nichts von den zwingenden Quellen-/Methodikhinweisen und setzt die freigegebenen Zahlen und Namen in die Satzbausteine ein. Die erforderlichen Tabellen legt der Server fest; eine Modellauswahl darf sie nicht unterdrücken.

Die Syntax dieses Vertrags ist beim späteren Adapter als Schema umzusetzen. Diese Dokumentation ist selbst noch kein Validator. Modellunterstützung und konkrete Übertragungsform bei Requesty werden in der Integration geprüft. Eine fehlgeschlagene Auswahl führt zur festen Serverzusammenfassung, nicht zu einer automatischen Reparaturschleife.

## Beispiel: Magdeburg und Hamburg

Bei bestätigter Auswahl „Magdeburg und Hamburg, 2024, Tonnen, alle drei Landverkehrsträger, Versand plus Empfang“ löst der Server die Gebiete über seine Metadaten auf. `compare_regions` prüft das gemeinsame Jahr und die Zählweise, liest die vorbereiteten Regionalwerte und berechnet Unterschiede sowie Modal-/Güteranteile. Das Ergebnis enthält beide Regionen, sieben Gütergruppen soweit belegt, Quelle und Binnenhinweis.

Danach können die Tabelle und eine feste Kurzfassung ausgegeben werden. Für die Auswahl weniger Kernaussagen ist optional ein Modellaufruf möglich. Ohne bestätigtes Jahr greift nur eine vorher definierte und sichtbar genannte Standardregel; andernfalls wird gezielt nachgefragt. Dieses Beispiel beschreibt den Vertrag und enthält bewusst keine ungeprüften Hamburg-Vergleichszahlen.
