# Pflege der Weboberfläche

> **Pflichtlektüre vor jeder Datenänderung – auch für KI-Systeme:**
> [`ANLEITUNG_DATENAKTUALISIERUNG.md`](ANLEITUNG_DATENAKTUALISIERUNG.md) und
> [`QUALITÄTSSICHERUNGSPLAN.md`](../qualitaet/QUALITÄTSSICHERUNGSPLAN.md). Beide Dokumente
> müssen vor Änderungen an Rohdaten, Berechnungen, Umstiegsschlüsseln oder
> Dashboard-Ausgaben gelesen und gemeinsam fortgeschrieben werden.

Die fachliche Aktualisierung der Rohdaten und die dazugehörigen Prüfungen sind
getrennt von der Weboberfläche in
[`ANLEITUNG_DATENAKTUALISIERUNG.md`](ANLEITUNG_DATENAKTUALISIERUNG.md)
dokumentiert.

Die ausgelieferten Dateien `index.html`, `css/style.css` und `js/app.js` werden
aus kleineren Quell-Dateien erzeugt. Bitte Änderungen in diesen Quellen
vornehmen und danach den folgenden Befehl ausführen:

`python scripts/frontend/build_frontend.py all`

Wichtige Zuordnung:

- `js/modules/maritime.js`: Seeverkehr und Häfen
- `js/modules/forecast.js`: Verkehrsprognose 2040
- `js/shared/`: gemeinsame Zahlenformatierung, Datenladewege, Dialogsteuerung und unveränderte nationale Aggregation
- `html/modules/`: sichtbare Analysebereiche
- `css/source/`: Basis, Komponenten, Fachmodule und responsive Darstellung

`js/app.js`, `index.html` und `css/style.css` bleiben die Dateien, die der
Webserver ausliefert. Sie werden nicht direkt gepflegt.

Die Sicherung vor dieser Umstellung liegt unter
`backups/before-modular-refactor-20260819-0100/`. Sie enthält die damals
ausgelieferten Fassungen von Oberfläche, Styles, Logik und den drei nun
nachgeladenen Fachdaten-Dateien.


## Datenpakete und lokale Browserprüfung seit 05.09.2026

Die fachlichen Gesamtdateien bleiben als kanonischer Prüfbestand erhalten. Der Browser lädt für Übersicht und Prognose kleinere Grundpakete und nur die Details der ausgewählten Region:

| Auslieferung | Inhalt |
|---|---|
| `data/processed/web_summary_core.json` | Karten- und Zeitreihenwerte aller Regionen sowie vorberechnete nationale Kennwerte |
| `data/processed/delivery/summary/{Region}.json` | regionale NST-20-Details aller vorhandenen Jahre |
| `data/processed/web_forecast_core.json` | Prognosekennwerte, Karten und Strukturwerte für beide Szenarien |
| `data/processed/delivery/forecast/{Region}.json` | sämtliche bisherigen Relationen dieser Region, beide Szenarien und alle Gütergruppen |
| `data/processed/delivery/*-manifest.json` | Quellfingerabdrücke, Dateigrößen und Prüfsummen |

Erzeugen und gegen den aktuellen kanonischen Bestand prüfen:

```powershell
node scripts/frontend/build_delivery_data.cjs
node scripts/frontend/build_delivery_data.cjs --check
python scripts/frontend/build_frontend.py all
node scripts/validation/validate_frontend_loading.cjs
node scripts/frontend/serve_preview.cjs 8000
```

Der Datenpaket-Build verwendet Node.js ohne zusätzliche Pakete. Der reine Frontend-Build erzeugt HTML, CSS und JavaScript; er ersetzt keinen Datenpaket-Build. Für eine Veröffentlichung müssen die beiden Grundpakete, der vollständige Ordner `delivery/` und die generierten Browserdateien gemeinsam aus einem bestandenen Prüfstand übernommen werden. Die bestehenden übrigen Fachdaten bleiben erforderlich.

Die Browserprüfung wird in einem zweiten Terminal gestartet. Playwright und etwaige Abhängigkeiten liegen ausschließlich außerhalb des Projektordners unter `C:\tmp`; der angegebene Modulpfad muss auf die tatsächlich vorhandene Installation zeigen:

```powershell
$env:PLAYWRIGHT_MODULE_PATH = 'C:\tmp\kita_playwright_qa\node_modules\playwright'
node scripts/validation/validate_frontend_browser.cjs http://127.0.0.1:8000 C:\tmp\gueterstroeme-browser-qa
```

Der Prüflauf verwendet das installierte Chrome im normalen Browsermodus und schließt seinen Browser anschließend. Im Durchgang vom 05.09.2026 lieferte die öffentliche Maut-API im Headless-Modus HTTP 500, im normalen Chrome dagegen HTTP 200 und echte Relationen. `QA_HEADLESS=1` ist deshalb nur eine optionale technische Variante und kein Ersatz für die Prüfung des Live-Mautmoduls. Eine externe Nichtverfügbarkeit wird im JSON-Prüfprotokoll ausdrücklich als solche ausgewiesen.

Fehlgeschlagene Datenanfragen bleiben erneut ausführbar. Start-, Modul-, Regions- und Steckbrieffehler zeigen eine Wiederholungsmöglichkeit statt scheinbar gültiger Leerwerte. Datenanfragen enden nach spätestens 30 Sekunden; veraltete Regions- und Jahresantworten überschreiben keine neuere Auswahl. Die gemeinsame Dialogsteuerung hält den Tastaturfokus im offenen Dialog und gibt ihn beim Schließen an dessen tatsächlichen Auslöser zurück.


## Diagrammvergrößerung, Exporte und Mautvergleich (05.09.2026)

`js/modules/export.js` erfasst beim Öffnen einen unveränderlichen Stand des aktiven Moduls. PNG und Excel übernehmen dessen Auswahl. Diagramme werden aus ihrer tatsächlichen Chart.js-Konfiguration neu gezeichnet; lokale Legenden und fixierte Achsen erhalten in der großen Ansicht eine eigenständige Darstellung. Das Schließen erfolgt über die gemeinsame Dialogsteuerung, einschließlich Fokusführung.

Excel: maximal 2.000 Datenzeilen; numerische Diagrammwerte mit ausdrücklicher Skalierung, unskalierte rechtsbündige Tabellenwerte als Zahlen, sonst angezeigter Text. Keine Formeln werden erzeugt. Der Quellenbogen enthält fachliche Hinweise und Filter. GeoPackage: höchstens 100 Gebiete/Standorte und 250 km Seitenlänge; EPSG:4326; Topologie erhaltender Polygonschnitt; Kennwerte bleiben Werte der vollständigen Gebiete. Keine Relationslinien oder Basiskarten. Die Felder sind ausdrücklich freigegeben (`code`, `name`, `wert`, `einheit`, `information`); vollständige Rohattribute werden nicht übernommen.

Die dafür benötigten Bibliotheken liegen mit Lizenzen unter `assets/vendor/` und werden erst bei Bedarf geladen. Bei der gemeinsamen Auslieferung muss dieser Ordner einschließlich `sqljs/sql-wasm.wasm` vollständig enthalten sein. Pflege und feste Paketversionen: `assets/vendor/README.md`. Paketinstallation und Bündelung ausschließlich unter `C:\tmp`, anschließend dort aufräumen. Eine Bibliotheksaktualisierung verlangt eine erneute Browser- und Dateiprüfung.

`js/shared/toll-comparison.js` lädt denselben Vorjahresmonat anhand der von der API gemeldeten Monatsverfügbarkeit. Der Sitzungscache ist nach Gemeinde, Monat und Richtung getrennt, auf 24 vollständige Antworten und 15 Minuten Gültigkeit begrenzt. Aktueller und vorheriger Abrufzeitpunkt stehen im Export. Fehlende Relationen, fehlende Werte und ein Vorjahreswert von null erzeugen keine vermeintliche Prozentänderung. Anfragen übernehmen einen festen Auswahlstand und werden bei neuen Auswahlen abgebrochen; verspätete Antworten überschreiben diesen nicht.

```powershell
node scripts/validation/validate_toll_comparison.cjs
node scripts/validation/validate_frontend_exports.cjs http://127.0.0.1:8000/ C:\tmp\gueterstroeme-export-pruefung
python -B scripts/validation/validate_export_files.py C:\tmp\gueterstroeme-export-pruefung
```

Die Browserprüfung verwendet den oben dokumentierten externen Playwright-Pfad und normales Chrome. Sie lädt echte lokale Dashboarddaten und verwendet für wiederholbare Maut-Grenzfälle gekennzeichnete API-Testantworten. Der reale Vorjahresabruf ist zusätzlich im Browser zu prüfen. Die Dateiprüfung benötigt die vorhandene Datenanalyseumgebung mit openpyxl, Pillow, Shapely und GeoPandas samt GIS-Lesetreiber. Exportgrenzen im Browser sind keine Zugriffskontrolle; deren spätere Durchsetzung auf dem Server bleibt Roadmap-Arbeit.


### Anpassungen nach Browser-Rückmeldungen vom 06.09.2026

- Diagramme öffnen sich über ein 24-Pixel-Symbol mit vier diagonalen Pfeilen in der Kopfzeile, neben den vorhandenen Diagrammsteuerungen. Es belegt keine Zeichenfläche. Der weiße Hinweis „Diagramm vergrößern“ erscheint bei Maus und Tastaturfokus; der zugängliche Name bleibt erhalten. Mobil bleibt das Symbol ausgeblendet.
- Die Übersicht und die einzelnen Diagrammkarten der Analyse-Module schützen die Diagrammhöhe durch Mindestgrößen; bei geringer Fensterhöhe scrollt der Inhaltsbereich. Die Güterstruktur-Dynamik besitzt eine begrenzte, scrollbar angelegte Legende mit vollständigen Bezeichnungen. Datenreihen lassen sich per Maus oder Tastatur ein-/ausblenden; die größere Ansicht übernimmt diesen Zustand.
- Beim Wechsel der NST-Ebene werden alte Legendencontainer vor der neuen Diagramminstanz entfernt. Damit misst und beobachtet das neue Diagramm wieder seinen tatsächlichen Elterncontainer. Dies gilt gemeinsam für Schiene, Binnenschifffahrt und Seeverkehr.
- Der Maut-Hover nennt weiterhin den letzten Berichtsmonat mit verfügbarem Vorjahresvergleich; der Zusatz über möglicherweise abweichende Einzelrelationen wurde entfernt.
- Vergrößerte Diagramme verwenden ausschließlich den nativen Chart.js-Tooltip mit Spitze. `external: null` verhindert die Übernahme der globalen HTML-Tooltip-Funktion; `undefined` würde auf diese globale Voreinstellung zurückfallen und zwei Anzeigen erzeugen.
- Die KI-Beispiele sind vollständige Fragen; Einführungstext in normaler Schreibweise. Der vorhandene Hinweis auf die fehlende Modellanbindung bleibt korrekt erhalten.
- Luftfracht-KPIs folgen der Flughafenauswahl: Flughafenwert, Vorjahresänderung, Anteil an der Summe veröffentlichter deutscher Flughafenwerte, Rang. Ohne Auswahl gilt die bisherige nationale Darstellung. Nationalreihe und Flughafenreihe werden nicht miteinander verrechnet. Salden: historischer Saldo statt Prozentänderung; Anteil und Rang nach absolutem Saldo. Ranggleichheit bei gleichen Werten; fehlende oder nicht belastbare Flughafenwerte bleiben fehlend und löschen die Flughafenauswahl nicht. Ein Saldo benötigt beide Richtungswerte.
- Der Maut-Vergleichshinweis verschwindet nach erfolgreichem Laden und bei regulär fehlendem Vergleichsmonat. Ladezustand und wiederholbare Abruffehler bleiben sichtbar. Hover-Inhalte zeigen Richtungspfeile und nennen bei fehlendem Vorjahresmonat den letzten Berichtsmonat, für den beide Monate in der API-Verfügbarkeitsliste enthalten sind. Daraus wird keine lückenlose Zeitreihe und keine Verfügbarkeit jeder einzelnen Relation abgeleitet.

Zusätzliche Prüfungen: `validation/validate_frontend_feedback.cjs` (gleiche Parameter wie beim Export-Browserprüfer), `validation/validate_airfreight_kpis.cjs` und die ergänzten Monatsverfügbarkeitsfälle in `validation/validate_toll_comparison.cjs`.

Diagrammlayout separat prüfen: `node scripts/validation/validate_chart_layout.cjs http://127.0.0.1:8000/ C:\tmp\gueterstroeme-layout-pruefung` (externer Playwright-Pfad wie oben). Geprüft werden tatsächliche Zeichenflächen auf fünf Fenstergrößen, alle zwölf Kopfzeilensymbole, helle Hinweise, Legendenbedienung und wiederholtes Umschalten 7 → 20 → 7 in drei Modulen.


### Mobile Karten: Menüebene und kompakte Legende (06.09.2026)

- Bis 900 Pixel Fensterbreite hält ein eigener Darstellungsbereich die Kartensteuerung unterhalb der mobilen Modulauswahl. Die Desktop-Regeln bleiben unverändert.
- Eingeklappte mobile Legenden zeigen nur ein antippbares Legendensymbol. Aufgeklappt bleiben Titel und Erklärung erhalten. Beide Zustände haben einen zugänglichen Namen und `aria-expanded`; die Luftfrachtlegende ist jetzt ebenfalls an die gemeinsame Umschaltung angeschlossen.
- Die Höhe der Quellenzeile wird je Karte beobachtet. Die mobile Legende sitzt acht Pixel oberhalb der Quellenzeile; lange Quellenangaben umbrechen innerhalb der Karte. Umfangreiche Legenden können innerhalb des Kartenrahmens scrollen. Quellen und Lizenzen bleiben vollständig erhalten.
- Prüfung: `node scripts/validation/validate_mobile_maps.cjs http://127.0.0.1:8000/ C:\tmp\gueterstroeme-mobile-pruefung`. Optional als viertes Argument eine vor der Änderung gespeicherte Desktop-Geometrie-JSON übergeben; Playwright bleibt außerhalb des Projekts wie oben beschrieben.


### Mobile Analyseansichten (06.09.2026)

- `js/shared/mobile-views.js` ergänzt bis 900 Pixel Fensterbreite die Ansichten „Karte“, „Relationen“ und „Diagramme“ in allen neun Modulen. Kennzahlen und Auswahlhinweis bleiben oberhalb der Umschaltung. Die vorhandenen Karten und Auswertungen werden weder kopiert noch im Desktop-DOM verschoben.
- Pro Modul bleibt die gewählte Ansicht erhalten. Ansichtswechsel verändern keine Filter und führen nicht zu neuen Datenabfragen. Verborgene Ansichtsbereiche sind mobil auch für Fokus und Hilfstechniken ausgeblendet; beim Wechsel zum Desktop werden alle Bereiche wieder freigegeben.
- Die mobile Anleitung benennt „Aktuell → Raum & Zeit“. Ihre Schaltfläche öffnet das bestehende Einstellungsfeld und fokussiert je nach Modul die Regions-, Gemeinde-, Hafen- oder Flughafenauswahl. Nach einer Auswahl bleibt die Ansicht erhalten; „Relationen ansehen“ ist ein freiwilliger nächster Schritt.
- Karten und Diagramme werden nach dem Einblenden neu vermessen. Kartenausschnitt und Zoom werden beim Ansichtswechsel wiederhergestellt, einschließlich der sonst von Leaflet verursachten Rundung auf ganze Pixel.
- Der Export bleibt eine Auswertung des gesamten aktiven Moduls. Die lediglich durch mobile Ansichtsregister verborgenen Tabellen und Diagramme bleiben enthalten; alle bisherigen Filter und Exportgrenzen gelten weiter.
- Prüfung: `node scripts/validation/validate_mobile_views.cjs http://127.0.0.1:8000/ C:\tmp\gueterstroeme-mobile-views-pruefung [Desktop-Geometrie-JSON]`. Externe Playwright-Installation wie oben. Die bestehenden Diagrammlayout- und Kartenprüfer berücksichtigen die neuen Register.

Der Stand vor dieser Änderung ist unter `codex/stand-vor-mobiler-ansicht-20260906`, Commit `b28b93f735b009146f11c1d382c15502d9c6f808`, auf dem bestehenden GitHub-Remote gesichert. Abgeleitete Browserpakete werden nach Wiederherstellung gemäß Projekt-README aus den bereits versionierten Ausgangspaketen erzeugt; die Reproduzierbarkeit aller 896 Ausgabedateien wurde vor der Sicherung geprüft.

### Steckbrief: Kurzfazit, Top 5 und PDF (07.09.2026)

Der Einstieg im Steckbrief besteht bei vollständiger Datenbasis aus etwa acht bis zehn Sätzen in drei Absätzen: Aufkommen und historische Entwicklung; Verkehrsträger mit Bundesvergleich sowie wichtigste Gütergruppen insgesamt und je Richtung; Saldo und stärkste Beziehung, getrennte KV-Anteile sowie Ausblick bis 2040. Die Formulierungen entstehen in `renderSteckbriefModal()` in `js/source/core-head.js` aus denselben Profildaten wie die folgenden Abschnitte.

- Das Profil bleibt eine Auswertung aller Güter und beider Richtungen in Tonnen. Modulfilter zu Gütergruppe, Richtung und Verkehrsleistung verändern es nicht. Der bestehende Profiljahr-Mechanismus bleibt maßgeblich.
- Modalanteile verwenden die Summe der drei Verkehrsträgermengen im Profiljahr. Der Vergleich nennt den Verkehrsträger mit der größten absoluten Anteilsabweichung zum bundesweiten Modal Split. Er ist kein ungewichteter Durchschnitt der Regionen; beim Deutschlandprofil entfällt der Selbstvergleich.
- Die beiden größten NST-7-Gruppen werden mit ihren Anteilen an der aufgeschlüsselten Gütermenge genannt, zusätzlich der Bundesanteil der führenden Gruppe. Versand und Empfang nennen jeweils ihre größte Gruppe mit dem Anteil innerhalb der betreffenden Richtung. Fehlende Richtungsaufschlüsselungen werden nicht aus der Gesamtstruktur geschätzt.
- Gegenwärtige und prognostizierte Beziehungen zeigen jeweils höchstens fünf positive Einträge, absteigend nach Menge. Die Ist-Richtungen werden wie bisher zuerst je Partner zusammengeführt. Die Gütergruppenliste bleibt bei drei Einträgen.
- Die Prognose bleibt P1, gesamter Landverkehr, Vergleich 2019–2040. Wachstum, Rückgang und auf eine Nachkommastelle unveränderte Entwicklung werden sprachlich unterschieden. Ein tatsächlicher Prognosewert null ist ein Rückgang um 100 Prozent; fehlender oder nullwertiger Basiswert bleibt nicht vergleichbar.
- PDF verwendet weiterhin den vorhandenen Browser-Druckknopf und dieselben Inhalte. Absatzabstände, ungeteilte Abschnitte und Tabellenzeilen bleiben erhalten. Lange mobile Titel umbrechen vor dem Druckknopf, ohne ihn zu überlagern.

Prüfung mit externer Playwright-Installation wie oben:

```powershell
node scripts/validation/validate_steckbrief.cjs http://127.0.0.1:8000/ C:/tmp/gueterstroeme-steckbrief
python -B scripts/validation/validate_steckbrief_pdf.py C:/tmp/gueterstroeme-steckbrief
```

Der PDF-Prüfer benötigt PyMuPDF (`fitz`), liest die fünf Browserexporte erneut und rendert alle Seiten zur anschließenden Sichtprüfung.


Die sprachliche Überarbeitung nach `wbp-writing` vom 07.09.2026 integriert Mengenanteile in den Satz statt in Klammern. Verkehrsträger erhalten passende Artikel und Anteilsbezeichnungen. Gleiche führende Gütergruppen werden für Versand und Empfang gemeinsam genannt; unterschiedliche Gruppen, Ranggleichheit und fehlende Richtungsdaten haben eigene Formulierungen. Binnenverkehr wird als „der Binnenverkehr in …“ bezeichnet, eine externe Verbindung als „Verkehrsbeziehung … mit …“. Die Prognose nennt weiterhin explizit P1, Landverkehr und den Vergleich 2019–2040. Die ausführlichen Gütergruppenbezeichnungen bleiben unverändert.


### KV-Terminals und Kontingent-Vorschau (10.09.2026)

Die Kartenkopfzeile des KV-Moduls enthält den Schalter „Terminals“. Er ist zunächst ausgeschaltet und steuert eine eigene Standortebene unabhängig von Verbindungen, Region, Jahr, Kennzahl und Richtung. Der Zustand bleibt beim Modulwechsel erhalten. Die Punktinformation zeigt ausschließlich Terminalname, bi-/trimodale Funktion und den Hinweis mit direktem Link zur Intermodal Map der SGKV (https://www.intermodal-map.com/). Maus-Hover ist interaktiv; ein Klick beziehungsweise Antippen öffnet dieselbe Information dauerhaft. Tastaturbedienung erfolgt über die Terminalmarker und Enter. Fehler beim Nachladen werden sichtbar angezeigt; erneutes Einschalten wiederholt den Abruf.

Bearbeitbare Quellen: `js/modules/intermodal-terminals.js`, `html/modules/intermodal.html`, `css/source/modules.css`; Einbindung über `scripts/frontend/build_frontend.py`. `python -B scripts/frontend/build_terminal_data.py` erzeugt `data/processed/web_intermodal_terminals.geojson`. Diese Datei muss mit dem Frontend ausgeliefert werden. Die vollständige Rohdatei mit Betreiber- und Kontaktdaten wird vom Browser nicht angefordert. Details zur Klassifikation stehen in der Datenaktualisierungsanleitung.

Im Analyseassistenten steht oberhalb des Eingabefelds „x von 50 Fragen gestellt“ mit Fortschrittsbalken. Die Anzeige ist ausdrücklich eine lokale Kontingent-Vorschau; nichtleere Testfragen werden gezählt, leere Eingaben und weitere Versuche nach 50 Fragen nicht. Der Teststand bleibt innerhalb derselben Browsersitzung auch beim Neuladen erhalten; gespeichert werden nur Monat und Zahl, keine Fragen. Monatswechsel richtet sich nach Europe/Berlin und wird beim Öffnen sowie Absenden geprüft. Ist Browserspeicher gesperrt, funktioniert die Anzeige für die laufende Seite. Ein neuer Browserkontext beginnt bei null. `js/shared/ai-quota.js` kapselt die Vorschau; echte Lizenzwerte und serverseitige Durchsetzung sind noch nicht angebunden.

Prüfung: `node scripts/validation/validate_terminals_quota.cjs`, `node scripts/validation/validate_frontend_loading.cjs`, Frontend-Build und `node --check js/app.js`. Zusätzlich lokale Browserkontrolle von Schaltern, Punktinformation/Link, KI-Testfrage und schmaler Ansicht. Keine neue Gesamtfreigabe des Dashboards oder der KI.


### Nachtrag zur Terminal- und Kontingentdarstellung (10.09.2026, Nutzerfeedback)

Diese Ergänzung ersetzt die Darstellungsbeschreibung des vorangehenden Abschnitts: Die Terminalebene enthält ausschließlich Deutschland (`iso2 == DE`, 213 Standorte). Marker sind 12 × 9 Pixel große blaue Rechtecke mit weißem Rand und leichtem Schatten. Nur bei tatsächlich eingeblendeter Ebene erscheint derselbe Marker in der KV-Legende mit „KV-Terminals · Deutschland“; Filter-/Modulwechsel erhalten den Eintrag ohne Duplikate. Der Schalter besitzt einen hellen Hinweis „Terminals anzeigen“ beziehungsweise „Terminals ausblenden“ sowie Hover-Hervorhebung und Tastaturfokus. Titel und Terminalfunktion sind durch eine feine Linie getrennt; SGKV-Hinweis und Link stehen kleiner und kursiv hinter einer zweiten Linie.

Das Fragenkontingent steht nun links direkt unter dem Eingabefeld: 58 × 3 Pixel kleiner Balken, „x von 50 Fragen“ und ein fokussierbares Fragezeichen. Die zuvor dauerhaft sichtbare Kontingent-Vorschauzeile und die zusätzliche Monatsüberschrift entfallen. Der weiße Hinweis am Fragezeichen erklärt Monatskontingent und Rücksetzung; die lokale Zählweise und der allgemeine Hinweis auf den Interface-Prototyp bleiben unverändert.


### Nachtrag: Hinweisposition, Mausfokus und Diagrammkopfzeilen (10.09.2026)

Der Kontingenthinweis ist über `data-tooltip-placement="above"` ausdrücklich oberhalb der Zählerzeile verankert. Die gemeinsame Hinweisausrichtung erhält diese Vorgabe; Bezugspunkt ist die Zählerzeile, nicht das Fragezeichen oder der größere Browserrahmen. Dadurch bleibt der Hinweis innerhalb des begrenzten KI-Dialogs.

Der Terminalknopf unterscheidet Zeigerbedienung und Tastaturfokus: Nach `pointerdown` darf zurückbleibender Fokus den Hinweis außerhalb des Knopfes nicht offen halten. Tastatureingabe und Fokusverlust löschen die Zeigermarkierung. Der Hinweis selbst fängt keine Zeigerereignisse ab; Hover und Tastaturzugang bleiben erhalten.

Kopfzeilen mit Umschaltgruppen nutzen modulübergreifend automatischen Zeilenumbruch nach tatsächlich verfügbarem Platz. Titelbereich und Schalter dürfen in getrennte Zeilen wechseln, Titeltexte bleiben innerhalb ihres Bereichs umbrechbar, Informationssymbole behalten ihre Breite. Diese Regel gilt auch oberhalb früherer Bildschirm- und Containergrenzen. Quellen: `css/source/components.css`, `css/source/modules.css`, `js/source/core-head.js` und `html/shell-tail.html`.


### Dialogbedienung im Testrelease ui10 (10.09.2026)

Der Header verweist mit einem normalen Link auf `https://wissensbasiert.de/`; das Logo ist kein Quellen-Dialogauslöser mehr. `js/shared/ai-client.js` verwaltet den begrenzten Nutzernachrichtenverlauf, leert das Feld beim Absenden und steuert `#aiWorking`. „Neuer Chat“ verwirft ausschließlich den lokalen Verlauf. `css/source/modules.css` setzt innere Listenabstände und die bei reduzierter Bewegung statische Arbeitsanzeige. Fachliche Vervollständigung und Jahrgangsprüfung liegen ausschließlich in `server/analyseassistent/dialogue.py`, nicht in Kartenfiltern oder Browserwerten. Aktueller Prüf-/Deploymentstand: neuester Nachtrag im Qualitätssicherungsplan.
