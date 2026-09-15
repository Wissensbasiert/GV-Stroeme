# Diagrammkopfzeilen, regionale KV-Struktur und Ladeanzeige

## Stand und Umfang

Lokal umgesetzt und geprüft am 15.09.2026. Noch keine Bereitstellung im Test- oder Produktivportal. Anlass sind die acht Browserkommentare vom 15.09.2026.

## Kopfzeilen nach Diagramm

Die große Ansicht und ihr PNG verwenden denselben beim Öffnen erfassten Diagrammkontext. Die pauschale Einstellungszeile und „Diagrammwerte“ entfallen. Einheiten bleiben an den Achsen bzw. in Legende und Tooltip. Der allgemeine Export behält den vollständigen Auswahlstand als zusätzlichen Kontext.

| Diagramm | Angaben in der Kopfzeile |
|---|---|
| Übersicht: Modal Split | Region, Jahr bzw. tatsächlicher Zeitreihenbereich, Richtung, Verkehrsaufkommen oder Verkehrsleistung; eine wirksame einzelne Güterauswahl |
| Übersicht: Güterstruktur | Region, Jahr bzw. Zeitreihenbereich, Richtung, Verkehrsaufkommen oder Verkehrsleistung |
| Straße, Schiene, Binnenschiff: Güterstruktur | Region, Jahr bzw. Zeitreihenbereich, Richtung, Verkehrsaufkommen oder Verkehrsleistung; kein globaler Güterfilter, da die Struktur ihre eigenen Kategorien zeigt |
| Seeverkehr: Güterstruktur | Hafen bzw. alle Häfen, Jahr bzw. Zeitreihenbereich, Richtung, Seegüterumschlag |
| Luftverkehr: Flughafenvergleich | Deutschland, Jahr bzw. Zeitreihenbereich, Richtung; bei Dynamik zusätzlich Bezugsjahr für die Auswahl führender Flughäfen. Ein in der Dynamik ergänzter ausgewählter Flughafen bleibt im Diagrammtitel bezeichnet. |
| KV: Ladeeinheiten Schiene / Containergrößen Binnenschiff | Region, Jahr bzw. Zeitreihenbereich, Richtung, Bezugskennzahl; Status als Anteile, Dynamik als Mengen/Leistungen, Saldo als vorzeichenbehaftete Werte |
| Prognose: Modal Split | Region, Szenario, Richtung, Verkehrsaufkommen oder Verkehrsleistung; wirksame einzelne Güterauswahl |
| Prognose: Güterstruktur | Region, Szenario, Richtung, Verkehrsaufkommen oder Verkehrsleistung; kein globaler Güterfilter |
| Prognose: Ladeeinheiten | Region, Szenario, Verkehrsaufkommen nach Ladeeinheitentyp, Gesamtverkehr. Die Daten sind unabhängig von globaler Kennzahl, Richtung und Güterauswahl stets Tonnen; die Achse nennt Mio. Tonnen. |
| Maut: Distanzklassen | Gemeinde, Monat, Richtung, Anteil der Mautfahrten nach mittlerer Distanz, wirksamer Binnenverkehrsfilter. Keine Top-X- oder Kartenkennzahl: Das Diagramm verwendet alle verfügbaren Relationen. |

In den vier KPI-Titeln von See- und Luftverkehr entfallen Ortszusätze. „Containerumschlag“ trägt bei Gesamtrichtung keinen Zusatz „Gesamt“. Fachlich unterschiedliche Kennzahlen und Richtungszusätze bleiben erhalten.

## KV-Daten und Filter

Die beiden Strukturdiagramme lasen vorher ausschließlich `data_by_year`, also nationale Werte. Die vorhandenen Destatis-Jahresdateien enthalten regionale Ladeeinheiten und Containergrößen. Die Pipeline ergänzt diese Kategorien unter `scoped_metrics_by_year` für Deutschland und NUTS-3, getrennt nach Versand, Empfang und Binnenverkehr sowie Tonnen und Tonnenkilometern.

Status und Dynamik verwenden diese Werte für die aktuelle Region und Richtung. Binnenverkehre zählen bei Versand und Empfang mit, bei der kombinierten Richtung einmal und beim Saldo nicht. Top-X und der reine Relationsfilter für Binnenverkehr verändern die Struktur nicht. Ein Anteil bei Nenner null bleibt fehlend. Salden werden nicht als Prozentanteile dargestellt. Schiene und Binnenschiff bleiben getrennte Teilmärkte.

Alle 127.519 vorhandenen Zahlenwerte wurden mit dem vollständigen Neuaufbau verglichen (maximale zugelassene absolute Rundungsabweichung 0,001, relative Toleranz 1e-12); anschließend wurden die vorhandenen Werte und Relationsreihenfolgen unverändert bewahrt und ausschließlich die neuen Strukturkategorien ergänzt. Sicherung: `backups/before-chart-feedback-20260915/web_intermodal.json`.

## Ladeanzeige

Der technische Ladezustand gilt weiterhin sofort. Die sichtbare Anzeige erscheint erst nach 1.500 ms. Fertigstellung oder eine neue Anfrage hebt den alten Timer auf. Nach Fehlern darf ein alter Timer keine Anzeige mehr einblenden. Die Anzeige bleibt über der Karte ohne zusätzliche Layoutzeile.

## Prüfungen

- `validate_intermodal_structure.py`: 228 unabhängige Kontrollen gegen die CSV-Originalzeilen für Bremen, Duisburg und Berlin (2024), beide Kennzahlen und drei Richtungen sowie nationale Strukturwerte aller zehn Jahre.
- `validate_chart_context.cjs`: 25 Diagrammansichten in Status und Dynamik, regionale KV-Veränderungen und rechnerischer Bremen-Anteil, Saldo, Prognose-KV sowie 1.100 ms unsichtbar, abgebrochener Timer unsichtbar, 2.700 ms sichtbar und sofortiges Ausblenden nach Abschluss. Keine unbehandelten Browserfehler.
- `validate_frontend_exports.cjs`: große Ansichten aller Module einschließlich Maut, identische Diagrammdaten, Fokusführung, PNG/Excel/GeoPackage, Laptop/Mobil und simulierte Maut-Grenzfälle bestanden. Mautfälle nutzen reproduzierbare Testantworten; dies ist kein neuer Nachweis der Verfügbarkeit der externen Maut-API.
- Bestehende Lade-/Fehler- und Luftfracht-KPI-Prüfungen, Frontendaufbau und JavaScript-Syntax bestanden.
- Visuelle Kontrolle der gespeicherten großen Ansichten für Modal Split, Bremen-KV, Prognose-KV sowie der verzögerten Ladeanzeige: lesbare Texte und keine abgeschnittenen Kopfzeilen.

Browsernachweise liegen unter `outputs/chart-feedback-20260915/` und `outputs/chart-feedback-exports-20260915/`. Die Änderung erweitert den öffentlichen KV-Bestand; vor einer späteren Portalbereitstellung sind die dort erforderlichen Paket- und Assistentenprüfungen erneut auszuführen. Eine lokale Frontendprüfung ist keine Portal-Freigabe.


## Nachprüfung: KV-Achsen und KPI-Rundung (15.09.2026)

Die erneuten Browserkommentare zu Köln 2025 zeigten einen Fehler der früheren Prüfung: Region und Werte stimmten, aber die Dynamikachse rundete auf ganze Zahlen. Die neue gemeinsame Achsenformatierung bestimmt die Dezimalstellen aus dem tatsächlichen Abstand der Skalenstriche. Dies gilt für die KV-Dynamik und die Saldo-Statusansicht, einschließlich Vergrößerung und PNG. Die Einheit bleibt je Diagramm einheitlich.

Mengen-/Leistungs-KPI in Übersicht, Prognose, KV, See- und Luftverkehr erhalten eine eigene Anzeigeformatierung: ab einem Betrag von 100 in der angezeigten Einheit keine Nachkommastelle, von 1 bis unter 100 höchstens eine, darunter etwa zwei signifikante Stellen. Unnötige Endnullen entfallen. Sehr kleine Werte werden erforderlichenfalls wissenschaftlich dargestellt; fehlende Werte bleiben fehlend. Beispiele: 3.839,24 → 3.839; 42,56 → 42,6; 0,021 → 0,021. Prozentwerte, Fluganzahlen, Tabellen, Quelldaten und Berechnungen bleiben bei ihren bisherigen Regeln. Die bisherige Einheitenauswahl bei Luftfracht bleibt erhalten.

Die Ladeverzögerung wurde auf Nutzerwunsch von ursprünglich 2.500 auf 1.500 ms verkürzt. Die ursprünglichen Export-/Quellenprüfungen oben beziehen sich auf den ersten Stand. Neu bestanden: `validate_number_precision.cjs`, Luftfracht-KPI-Prüfung, Syntax-/Buildprüfung, `validate_kv_axes.cjs` mit 32 Achsenkonfigurationen für Köln 2025 (Tonnen/tkm, Versand/Empfang/Summe/Saldo, Status/Dynamik), große Ansichten und nationale KPI. Sichtprüfung der Screenshots bestätigt lesbare Dezimalachsen und die gerundeten nationalen KPI. Die 25 Kontextansichten und Ladeprüfung wurden mit 1.500 ms erneut bestanden: bei 1.100 ms unsichtbar, nach Abbruch weiterhin unsichtbar, bei 1.700 ms sichtbar, nach Abschluss verborgen.

Neue Nachweise: `outputs/kv-axes-20260915/` und `outputs/chart-context-1500ms-20260915/`. Weiterhin ausschließlich lokaler Prüfstand.


## Nachprüfung: Flughafenzählung, Diagramm-Hover und Prognosekarte

Die dritte nationale Luftverkehrs-KPI zählt jetzt nur veröffentlichte Werte größer null für das ausgewählte Jahr, die Kennzahl und die Richtung. Im Gesamtverkehr 2024 sind dies 18 statt 22 Flughäfen; Memmingen, Niederrhein/Weeze, Dortmund und Friedrichshafen haben veröffentlichte Nullwerte. Bei Saldo wird für diese Zählung der Gesamtverkehr verwendet, weil ein ausgeglichener Saldo keine Verkehrslosigkeit bedeutet; der Untertitel benennt diese Abgrenzung. Die Nullwerte bleiben im Datenbestand sowie in Karte und Ranking erhalten. Die Flughafen-Einzelauswahl zeigt weiterhin ihren Anteil statt einer Flughafenanzahl.

Die Flughafenachse verwendete die Position innerhalb der ausgedünnten Tickliste als Index der vollständigen Datenliste. Dadurch passten Namen und Zeilen nicht zusammen. Die Beschriftung verwendet jetzt den tatsächlichen Kategorienwert. Der gemeinsame Achsen-Hover bestimmt seine Position ebenfalls aus Kategorienwerten statt aus Tickpositionen; Achsen- und Daten-Hover überschreiben einander nicht mehr. In der Flughafen-Statusansicht ist jede Datenzeile unabhängig von der Balkenlänge erreichbar. Der Tooltip nutzt dieselbe Wertformatierung wie die Karte, einschließlich Tonnen/Tausend Tonnen/Millionen Tonnen und Flugzahlen.

Der Prognosekarten-Hover enthält Region, Szenario, gewählte Richtung/Kennzahl, gegebenenfalls Güterart und den Vergleich 2019–2040. In der Gesamtrichtung erläutert eine kurze Zeile Versand + Empfang + Binnenverkehr. Die zusätzlichen Modal-Split- und Saldo-Detailblöcke entfallen. Der zunächst ebenfalls entfernte KV-Block wurde auf Nutzerwunsch wiederhergestellt (siehe Nachprüfung unten). Ist Saldo ausdrücklich gewählt, bleibt er der Hauptwert; der Vergleich zeigt dann eine absolute Differenz ohne Prozentrechnung. Bei 2019 lautet der Vergleich „Erwartete Veränderung bis 2040“, bei 2040 „Veränderung gegenüber 2019“. Beide berechnen dieselbe vorwärts gerichtete Entwicklung auf Basis 2019. Fehlende Vergleichswerte bleiben fehlend; ein Nullbasiswert erzeugt keine unendliche Prozentzahl.

Bestanden: 48 Kombinationen aus Kennzahl, Richtung, Güterfilter und Szenario sowie Fehlwert-/Nullbasisfälle (`validate_forecast_hover.cjs`), erweiterte Luft-KPI-Prüfung, Browserprüfung mit tatsächlichen Mausbewegungen auf Bremen, Paderborn/Lippstadt, Erfurt-Weimar und Hamburg einschließlich Achsenlabels, identischen Kartenwerten und großer Ansicht (`validate_air_forecast_hover.cjs`). Beispiel: Bremen 267 t, Paderborn/Lippstadt 45 t, Erfurt-Weimar 14 t (2024, Gesamtverkehr). Teltow-Fläming: Verkehrsleistung 2019 4,7 Mrd. tkm, 2040 8,7 Mrd. tkm; aus ungerundeten Daten +85,4 %. Keine unbehandelten Browserfehler. Nachweise: `outputs/air-forecast-hover-20260915/`. Noch keine Portalbereitstellung.


## Harmonisierung: Delta und Prognoseverbindungen

Flächen- und Verbindungshinweise der Prognose verwenden nun dieselbe Vergleichsformatierung: Δ, Pfeil, Grün für Zunahme, Rot für Abnahme und Grau für unveränderte bzw. nicht berechenbare Werte. Szenario 2040 zeigt die Veränderung gegenüber 2019; Szenario 2019 die erwartete Entwicklung bis 2040. Bezug bleibt jeweils 2019, auch wenn die Ansicht wechselt.

Verbindungen vergleichen denselben Partner, dieselbe Richtung, Kennzahl und Güterauswahl in beiden Szenarien. Sind beide Mengen vorhanden, wird aus den ungerundeten Mengen gerechnet. Bei fehlendem Basiseintrag kann der bereits aus den Originalmatrizen geprüfte Prognose-Prozentwert verwendet werden. Die Browser-Ranglisten sind begrenzt: Ein darin fehlender Eintrag wird nicht als null interpretiert. Für Salden werden nur bei vollständiger belegter Versand-/Empfangspaarung beider Szenarien absolute Veränderungen ausgewiesen. Fehlende Vergleiche bleiben ausdrücklich nicht verfügbar.

Prüfung: 48 Regions-/Filter-/Szenariofälle plus Routenvergleich Rhein-Kreis Neuss–Rotterdam für Tonnen und tkm in beiden Szenarien, Vorzeichenfarben, unveränderte Werte, Nullbasis, Fehlwerte und Salden. Browserprüfung mit tatsächlichem Maus-Hover auf der Verbindung: +6,2 % bei Tonnen in beiden Szenarien, jeweils passend bezeichnet. Δ und Farben auf Flächen und allen angezeigten Verbindungen bestätigt; keine unbehandelten Browserfehler. Prüfer: `validate_forecast_hover.cjs` und `validate_forecast_route_hover.cjs`. Nachweise: `outputs/forecast-route-hover-20260915/`. Lokal, noch keine Portalbereitstellung.


## Nachprüfung: KV-Hinweise wiederhergestellt und Kartenrand

Der regionale KV-Block aus dem vorherigen Git-Stand ist wieder enthalten: richtungsbezogene Menge in Mio. t, Anteil an der Beförderungsmenge (außer bei Saldo) und Tsd. TEU. Bei Auswahl von Verkehrsleistung bleibt diese Zusatzinformation in ausdrücklich bezeichneten Mengen-Einheiten sichtbar; die Anteilsberechnung verwendet stets Tonnen. Bei einer einzelnen Gütergruppe wird kein nicht verfügbarer regionaler KV-Anteil behauptet. Die neuen farbigen Vergleichshinweise bleiben erhalten.

Auf Verbindungen wird die vorhandene positive TEU-Angabe ausdrücklich als „Kombinierter Verkehr · Containerladung“ bezeichnet. Die zuvor daneben stehende gesamte Transportmenge entfällt aus diesem Zusatz: Das Relationsschema enthält keine gesonderte KV-Tonnenmenge, daher wäre diese Zuordnung irreführend. Fehlende TEU werden nicht als Null ergänzt; Saldo-Routen enthalten weiterhin keine abgeleitete TEU-Angabe.

Die Positionskorrektur des regionalen Hovers läuft jetzt nach Leaflets eigener Mausbewegungs-Verarbeitung. Sie berücksichtigt den sichtbaren Schnitt von Karte und Browserfenster. Reale Mausbewegungen am Eifelkreis Bitburg-Prüm sowie gezielt angesteuerte Positionen an allen vier Kartenecken wurden geprüft: Der vollständige Hover bleibt mit Innenabstand innerhalb der Karte. Sichtprüfung des Screenshots bestätigt die Lesbarkeit einschließlich KV-Block.

Bestanden: Frontend-Build, JavaScript-Syntax, 48 Prognosevergleichsfälle und Routenvergleiche, Browserprüfung der Verbindung Rhein-Kreis Neuss–Rotterdam für 2019/2040 einschließlich KV und Delta sowie Kartenrandprüfung. Nachweise: `outputs/forecast-kv-edge-20260915/`. Weiterhin lokaler Stand, nicht bereitgestellt.


## Korrektur nach erneuter Rückmeldung: Quellen und sämtliche Prognose-Hover

Die vorherige Kartenrandprüfung war zu eng: Sie bestätigte regionale Beispiele, erfasste aber nicht jede interne Neupositionierung der Routenfenster. Die separate regionale Korrektur wurde ersetzt. Regionen, Routenlinien und Endpunktmarker öffnen ihre Fenster nun zur Kartenmitte und verwenden nach jeder Leaflet-Positionsaktualisierung die gemeinsame Begrenzung einschließlich Legendenvermeidung. Damit hängt die Begrenzung nicht davon ab, ob Mausereignisse bis zur Karte weitergereicht werden. Die Anpassung überschreibt gezielt die Positionsmethode der jeweiligen Prognose-Tooltipinstanz; bei einem Leaflet-Update muss diese Integration erneut geprüft werden.

Vor dem regionalen KV-Block steht ein Absatzabstand. Routenwerte und ihre Einheiten sind gemeinsam umbrechende Einheiten; Beschriftungen dürfen separat umbrechen.

Im Quellen-Dialog entfallen der Beraterzusatz, der abschließende Punkt bei der Konzeption sowie die Zeile zur technischen Lizenzübersicht. Zwischen Konzeption und Bearbeitungsstand steht ein eigener Absatzabstand. Die Lizenzdateien selbst bleiben erhalten. Ein neuer Hinweis erläutert Rechte am Tool und verweist auf die bestehenden Portal-Nutzungsbedingungen, ohne gesonderte Daten- und Drittkomponentenlizenzen oder gesetzliche Erlaubnisse aufzuheben. Grundlage: live abgerufene Nutzungsbedingungen vom 20.08.2026, Ziffern 5, 6 und 13, unter https://wissensbasiert.de/nutzungsbedingungen-wbp-solutions/ (PDF), sowie §§ 69a und 69d UrhG. Dies ist ein zusammenfassender Hinweis zu bestehenden Bedingungen, keine neu formulierte Vertragsregelung oder anwaltliche Freigabe.

Erweiterte Browserprüfung: tatsächlicher Routenhover Rhein-Kreis Neuss–Rotterdam in beiden Szenarien, Mausbewegung am Eifelkreis Bitburg-Prüm und alle Regions-/Routenfenster an vier Kartenrändern bei 1.906 und 1.440 Pixeln Fensterbreite. Innere Inhalte separat auf horizontalen Überlauf geprüft (der äußere Tooltip enthält einen absichtlich herausragenden Richtungspfeil). Nachweise und Screenshots: `outputs/forecast-hover-all-20260915/`. Build, Syntax und bestehende Prognosevergleichsprüfungen bestanden. Ausschließlich lokal.

Zusätzlich bestanden: tatsächlicher Maus-Hover auf der Verbindung Ortenaukreis–Rotterdam bei eingeklappten Einstellungen; Screenshot `ortenau-route.png`. Absatzabstand zwischen Konzeption und Bearbeitungsstand im Browser bestätigt.


## Nutzungshinweise und Steckbrief

Die feste Kontextzeile am Anfang des Steckbriefs entfällt in der gemeinsamen Berichtsvorlage. Sie war keine Anzeige aktiver Filter. Die Berechnung bleibt unverändert: Gesamtprofil des gewählten Raums anhand der Beförderungsmenge, unabhängig von Güterart-, Richtungs- und Kennzahlfilter. Diese Abgrenzung steht nun knapp in den Nutzungshinweisen; das Bezugsjahr bleibt im Berichtstitel.

Die Nutzungshinweise wurden vollständig redaktionell überarbeitet. Die neun Module stehen einzeln und mit ihren Navigationsbezeichnungen in der Reihenfolge der linken Menüleiste. Anschließend folgen Raumauswahl und Darstellung, Steckbrief und Export, ergänzende Fragen mit dem freigeschalteten KI-Analyseassistenten im Beta-Modus sowie Datenstand und Vergleichbarkeit. Der KI-Hinweis erklärt Anschlussfragen, fehlende automatische Übernahme der Kartenfilter und die Prüfung wichtiger Aussagen. Technische Ladehinweise entfallen; die dynamische Datenabdeckung sowie fachlich relevante Exportgrenzen bleiben erhalten.

Frontend-Build und Syntaxprüfung bestanden. Lokaler Stand, keine Portalbereitstellung.
