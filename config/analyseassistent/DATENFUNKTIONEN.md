# Fachlicher Vertrag der Datenfunktionen

## Ergänzung 0.6.0: Gegenräume und Gesamtverkehr

`transport_history(region,start,end,modes,metric,direction,partner_scope)` liefert bis zu zehn Jahre. `all` nutzt die bestehende Regionalprofil-Zählweise; Versand plus Empfang zählt innerregional zweimal. `domestic` und `international` filtern vorhandene B01-Relationen nach Deutschland bzw. ausländischen Partnerkennungen; bei Richtung `all` zählt jede gerichtete Relation einmal. Diese unterschiedlichen Zählweisen werden ausdrücklich ausgewiesen. Unbekannte Partnercodes werden nicht als Ausland behandelt. Deshalb sind gefilterte und ungefilterte Werte bei beiden Richtungen nicht pauschal additiv vergleichbar.

`goods_structure`, `goods_history` und `partner_ranking` akzeptieren optional denselben Gegenraum. Gefilterte C7-Güteraufteilungen sind für Schiene/Binnenschiff verfügbar; Straßen-OD besitzt nur Gesamtwerte. Ein Filter darf bei einem Werkzeugwechsel nicht still verloren gehen. Bei einer neu ausdrücklich benannten Relation sind kompatible Ländereinschränkungen bereits durch beide Endpunkte erfüllt.

Modalgesamtsummen entstehen nur aus disjunkten Tonnen-Gesamtwerten bei gleichem Jahr, Raum, Richtung und Kennzahl. Keine Addition mit Güteruntergruppen, Prozentwerten, Tonnenkilometern oder KV-Teilmärkten. Fehlt ein Verkehrsträger, bleibt die vollständige Summe unbekannt; eine bekannte Teilsumme trägt ihre Komponenten. Regionale Zeitreihen berechnen Veränderungen ausschließlich aus den gewünschten Randjahren. 2025 ohne Straßenwert darf nicht durch 2024 ersetzt werden. Die kurze Haupttabelle zeigt Jahreswerte, die Detailtabelle ist ausklappbar.

## Ergänzung 0.5.0: bislang fehlende Datenzugriffe

`forecast_regions` akzeptiert zusätzlich `goods`: `ALL`, C7 als Textcode 1–7 oder Originalgruppen `VP10` bis `VP200` gemäß Katalog (25 Codes). Keine Mischung überlappender Gliederungen; keine Addition von `ALL` und Einzelgruppen. Region, Modus, Richtung, Gruppe und Kennzahl bleiben als gemeinsamer Faktenbezug erhalten. Deutschland nur `direction=all`, einschließlich Transit. Regional Versand/Empfang ohne Binnen, all mit Binnen einmal. Nullbasis erzeugt keine Prozentveränderung.

`forecast_relation` liest gerichtete Quelle/Ziel-Verbindungen aus vollständigen Originalmatrizen statt Dashboard-Toplisten, mit Modi, t/tkm und C7/VP25. Fehlende Relationszeilen bleiben unbekannt. Beide Funktionen vergleichen ausschließlich 2019_BASE und 2040_P1; keine Ist-Fortschreibung.

`dashboard_detail` erschließt veröffentlichte Regional-NST20-Profile (Schiene/IWW t/tkm), Hafen-NST20/C7 (t/TEU), Hafenpartner mit C7-Filter (t), nationale getrennte KV-Strukturen, veröffentlichte KV-Relationen, Regionalprofil-Straßenfahrten und modellierte VP-KV-/Behälter-/Ladeeinheitenkennzahlen. NST20-Codes bleiben zweistelliger Text. Straße NUTS-3 erhält keine künstliche NST20-Aufteilung. Hafenpartner und KV-Relationen bleiben explizit begrenzte veröffentlichte Auswahlen. Nationale Regional-NST20-Dashboardaggregation ist keine vollständige amtliche Randsumme. VP-TEU/Ladeeinheiten umfassen alle Matrixverkehre, nicht nur KV.

Privates Paket `dashboard_access`: Quellen-/Code-/Ausgabehashes, vollständiger regionaler C7/VP25-Abgleich, nationale t/tkm-Summen und Feldzugriffsinventar. Neue nicht zugeordnete semantische Dashboardfelder sperren den Build. Der Inventarabgleich prüft den veröffentlichten Bestand, nicht alle nicht veröffentlichten Rohfelder oder jede freie KI-Frage. Weitere Details und tatsächlicher Freigabestand im [Prüfbericht](../../docs/qualitaet/ANALYSEASSISTENT_DATENZUGRIFF_20260914.md).

**Version 0.2.1 · 11.09.2026 · Spezifikation und lokal implementierter Antwortvertrag; keine Produktfreigabe.** Freigabe und Verfügbarkeit gelten je Filterkombination, nicht pauschal je Funktionsname.

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
| F04 `get_time_series` | D01/D02/D04; gleiche Filter über bestätigte Zeitabdeckung, Lücken und Brüche mitführen; prozentuale Veränderung aus vorhandenem Anfangs- und Endwert berechnen | Rechnerische Veränderung als solche kennzeichnen; fehlende Werte nicht als null einsetzen; keine Ursache oder methodisch bereinigte Entwicklung behaupten | T10–T12 |
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

Modellausgabe: `result_id`, `data_snapshot_id`, ein bis drei Absätze mit `text` und jeweils verwendeten `statement_ids`, `table_ids` und `wording_variant` (`compact` oder `neutral`). Das Modell formuliert die Antwort selbst, darf aber nur bereitgestellte Einzelwerte und serverseitig geprüfte Vergleichsaussagen verwenden. Der Server prüft jede Kennung und jede Zahl gegen die Belege des Absatzes; neue Zahlen, HTML oder fremde Kennungen machen die Formulierung ungültig. Die erforderlichen Tabellen, Quellen und Hinweise bleiben unabhängig vom Modell erhalten.

Die Syntax dieses Vertrags ist beim späteren Adapter als Schema umzusetzen. Diese Dokumentation ist selbst noch kein Validator. Modellunterstützung und konkrete Übertragungsform bei Requesty werden in der Integration geprüft. Eine fehlgeschlagene Auswahl führt zur festen Serverzusammenfassung, nicht zu einer automatischen Reparaturschleife.

## Beispiel: Magdeburg und Hamburg

Bei bestätigter Auswahl „Magdeburg und Hamburg, 2024, Tonnen, alle drei Landverkehrsträger, Versand plus Empfang“ löst der Server die Gebiete über seine Metadaten auf. `compare_regions` prüft das gemeinsame Jahr und die Zählweise, liest die vorbereiteten Regionalwerte und berechnet Unterschiede sowie Modal-/Güteranteile. Das Ergebnis enthält beide Regionen, sieben Gütergruppen soweit belegt, Quelle und Binnenhinweis.

Danach können die Tabelle und eine analytische feste Kurzfassung ausgegeben werden. Optional verbindet das Modell die belegten Kernaussagen zu einem kurzen Antworttext. Ohne bestätigtes Jahr greift nur eine vorher definierte und sichtbar genannte Standardregel; bei einem ausdrücklichen Mehrjahreswunsch wird dagegen ein begrenzter, sichtbarer Zeitraum verwendet. Dieses Beispiel beschreibt den Vertrag und enthält bewusst keine ungeprüften Hamburg-Vergleichszahlen.
