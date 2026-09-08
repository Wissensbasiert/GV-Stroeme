# Analyseassistent – fachlicher Testkatalog für Etappe 1

**Stand:** 08.09.2026 · **Umfang:** 45 Fälle, drei je Fragetyp · **Status:** fachliche Bestätigung ausstehend.

## Anwendung

Der Katalog verdichtet die [160 Akteursfragen](ANALYSEASSISTENT_ETAPPE1_KANDIDATFRAGEN.md) auf den bestätigten Umfang: vorhandene Dashboard- und Rohdaten, gegebenenfalls sinnvolle zusätzliche Aufbereitung dieses Bestands. Externe Beschaffung, Umweltbilanzen, Kapazitäten, Kosten-/Servicemodelle und betriebliche Transportketten werden nicht als Zielprodukte vorbereitet. Die Typen F01–F15, Quellen D01–D10, Prüfpakete B01–B07 und Regeln R1–R10 sind im [Detailkonzept](ANALYSEASSISTENT_ETAPPE1_DETAILKONZEPT.md) definiert und gehören zu jedem Fall.

**Heute/Ziel:** Bei vorhandenen Auswertungen gilt die konkrete Quell- und Rechenerwartung. Bei noch nicht aufbereiteten Rohdaten ist die Ergebnislogik festgelegt; die numerische Sollantwort wird erst nach gesonderter Rohdatenprüfung fixiert. Eine korrekt begrenzte Antwort besteht als Grenzfall, belegt aber keine volle Abdeckung der ursprünglichen Akteursfrage.

**Kontrollwerte:** Bestandswerte wurden lokal gelesen/nachgerechnet; Einzelheiten im [Prüfnachweis](ANALYSEASSISTENT_ETAPPE1_PRUEFNACHWEIS.md). Synthetische Minibeispiele sind ausdrücklich erfundene Prüfwerte ausschließlich für Aggregation, Rangfolge und Fehlwertlogik. Sie sind keine tatsächlichen Verkehrsmengen. Es gibt keine synthetischen Umwelt-, Kosten- oder Kapazitätsprodukte.

**Bestehenskriterien:** richtige Parameter, Datenbasis, Zahlen/Rechnung, Einheit, Quelle, Zeit-/Raumbezug, Nenner und Einschränkung. Keine Zahl bei einer entscheidenden ungeklärten Dimension. Fehlende Daten bleiben fehlend; nachvollziehbare Datenbegrenzung statt erfundener Werte. Quellenname ohne nachvollziehbaren Rechenweg genügt nicht.

**Toleranzen:** ganzzahlige D02-Kontrollmengen exakt; aus D01 gerundete Summen höchstens 0,1 t je addiertem Quellwert; auf eine Nachkommastelle ausgegebene Anteile/Änderungen höchstens 0,05 Prozentpunkte Abweichung vom ungerundeten Kontrollwert. Synthetische Werte exakt bzw. wie angegeben gerundet. Falscher Nenner, Rang, Gebietsbezug oder Fehlstatus fällt unabhängig von Zahlentoleranzen durch.

**Prüfstatus:** Alle 45 Fälle sind als spätere Assistententests nicht ausgeführt. Einige Quellwerte wurden lesend kontrolliert. Bei fachlicher Abnahme je T-ID Prüfer, Datum, Datenversion, erhaltene Antwort, Abweichung und Bewertung festhalten. Numerisch noch offene Rohdatenfälle sind vor ihrer Aufnahme in einen Modellvergleich mit freigegebenen Sollwerten zu ergänzen.


## F01 – Regionsprofil und Kurzfassung

### T01 – Kernbefunde für eine Verwaltungsvorlage

- **Herkunft/Frage:** P1, Q001; „Welche zentralen Befunde zur ausgewählten Region gehören in eine Verwaltungsvorlage?“ UI-Beispiel.
- **Parameter:** bestätigte Auswahl Duisburg `DEA12`; Ist 2024, t, alle Güter, alle drei Landverkehrsträger; VP separat 2019_BASE/2040_P1. Vollprofil ausdrücklich vereinbart, abweichende Modulfilter offengelegt.
- **Datenbasis/Quelle:** D01, D03, D05 und aktuelle C-Gruppen aus D04; KBA, Destatis, VP2040.
- **Kennzahl/Einheit:** regionales Versand-/Empfangsaufkommen in t/Mio. t, Modalanteile in %, Güteranteile in %, Prognoseänderung in %.
- **Erwartung heute:** kurzes Fazit plus Tabelle. Bestandswert 108.215.313,5 t; Binnenschiff 38,5 %; Saldo −17.549.997,9 t. Führende Gesamtgruppe C1 mit 35.972.424,2 t. VP: 103.871.423 gegenüber 115.374.997 t, rund −10,0 %.
- **Grenze/Ziel:** Ist-Aufkommen als Versand plus Empfang benennen; VP-Zählweise separat. Keine Aussage über Beschäftigung, freie Kapazität oder Maßnahmenwirkung. Quelle/Jahre jeder Teilanalyse nennen. Prüfbedarf gemäß Detailkonzept gelten bei späteren Datenständen.


### T02 – Fehlende Regionsauswahl

- **Herkunft/Frage:** P1, Q002; „Wie viel Güterverkehr erzeugt und empfängt unsere Stadt?“
- **Parameter:** kein bestätigter Stadtbezug; Jahr und gemeinte Verkehrsträger offen.
- **Datenbasis/Quelle:** D01/D10 nach Klärung; KBA/Destatis, amtliche Gebietszuordnung.
- **Kennzahl/Einheit:** Versand und Empfang in t; keine Zahl vor Raumklärung.
- **Erwartung heute:** Stadt/Gebiet erfragen, danach vollständiges Bezugsjahr und Verkehrsbereich sichtbar festlegen. Kein Rückgriff auf eine beliebige zuletzt geladene Region oder Deutschland.
- **Grenze/Ziel:** „erzeugt“ umfasst in der Statistik Versand, nicht automatisch lokal produzierte Güter. Keine Umdeutung zur Produktionsmenge. Nach Klärung separate Versand-/Empfangstabelle gemäß R2.


### T03 – Belegtes Profil statt Standortversprechen

- **Herkunft/Frage:** P3, Q053: Wie sieht eine belastbare Kurzbeschreibung des Standorts für ein Investorengespräch aus?
- **Parameter:** Duisburg, 2024, alle Landverkehrsträger, t; gewünschte kurze Zusammenfassung.
- **Datenbasis/Quelle:** D01/D04; KBA VE12/13, Destatis 46131/46321.
- **Kennzahl/Einheit:** Aufkommen t/Mio. t und Strukturanteile %.
- **Erwartete Ergebnislogik:** Die Kontrollwerte von T01 in höchstens fünf belegte Aussagen übersetzen. Quellen und Binnenzählung erhalten.
- **Einschränkung/Status:** Keine Ansiedlungsnachfrage, Beschäftigung, freie Kapazität oder Logistikkosten behaupten. Solche Bewertungen bleiben außerhalb; regionale Verkehrsmengen sind der zulässige Kontext.


## F02 – Konkrete Verbindungen und Partner

### T04 – Hamburgs wichtigste Straßenpartner

- **Herkunft/Frage:** P1, Q004; „Welche Regionen sind Hamburgs wichtigste Partner im Straßengüterverkehr?“ UI-Beispiel.
- **Parameter:** `DE600`, 2024, Straße, alle Güter, t, externe Partner, beide Richtungen; bestätigtes Ranking nach Tonnen, Top 5.
- **Datenbasis/Quelle:** D02 mit D04-Kontrolle; KBA VE7. Alle berührenden OD-Zeilen verwenden, vor Sortierung je Gegenregion aggregieren.
- **Kennzahl/Einheit:** Menge je Partner in t; Anteil nur mit vollständigem gleich abgegrenztem Nenner.
- **Erwartung heute:** Rangfolge `DE933` 5.126.813; `DEF0D` 4.628.663; `DEF0F` 3.374.382; `DEF06` 2.687.481; `DE929` 2.289.981 t. Beide Richtungen zählen, interne 23.607.440 t ausschließen und Ausschluss nennen.
- **Grenze/Ziel:** zehn zugrunde liegende Richtungszeilen der Top 5 ohne Tonnen-ZS-Markierung geprüft; übrige Grundgesamtheit enthält Flags. Prüfbedarf gemäß Detailkonzept muss diese erhalten. Keine Gütergliederung der Straßenpartner und keine Gleichsetzung mit befahrenen Routen.


### T05 – Konkrete Verbindung statt Treffer in der Top-Liste

- **Herkunft/Frage:** P4, Q063; „Wie viel Ladung wird zwischen Duisburg und Magdeburg in jeder Richtung transportiert?“
- **Parameter:** `DEA12` ↔ `DEE03`, 2024, Straße/Schiene/Binnenschiff getrennt, alle Güter, t.
- **Datenbasis/Quelle:** D02; KBA VE7 und Destatis 46131/46321, bei ungeklärten Leerstellen D04.
- **Kennzahl/Einheit:** je Verkehrsträger Summe Duisburg → Magdeburg und Gegenrichtung in t; bei Straße nur `ALL`, bei Schiene/Binnenschiff Summe C1–C7.
- **Erwartung heute:** sechs eindeutig beschriftete Felder aus dem vollständigen OD-Bestand. Nicht in Top-Datei enthalten bedeutet nicht null. Fehlender Quellnachweis erzeugt „nicht nachgewiesen/Verfügbarkeit zu prüfen“.
- **Grenze/Ziel:** Binnenschiff/Schiene haben andere Erfassungsbereiche als Straße; keine Fahrzeit, Route oder buchbare Bedienung ableiten. Prüfbedarf gemäß Detailkonzept für belastbare Null-/Qualitätssemantik.


### T06 – Fehlender Top-Treffer und Gleichstand

- **Herkunft/Frage:** P8, Q146: Welche Beziehungen fehlen in der Top-Liste, obwohl Verkehr vorhanden ist?
- **Parameter:** Fokusregion, 2024, Modus, Richtung, t, Top 2.
- **Datenbasis/Quelle:** D02/D04; vollständiger amtlicher Relationsbestand gegenüber gekürzter Auslieferung.
- **Kennzahl/Einheit:** t und Rang; keine Menge allein aus Listenmitgliedschaft.
- **Erwartete Ergebnislogik:** Synthetisch: A 300, B 200, C 200, D 10 t. Top 2 enthält A/B/C mit Rängen 1/2/2. D bleibt als vorhandene Verbindung mit 10 t abfragbar.
- **Einschränkung/Status:** B01. Fehlender Eintrag in der Webliste ist kein Nullnachweis; Anteil nur mit vollständigem Nenner 710 t. Keine Zahl für in der Rohquelle ungeklärte Verbindungen.


## F03 – Regionsvergleich

### T07 – Duisburg und Magdeburg im gemeinsamen Jahr

- **Herkunft/Frage:** P1, Q003; „Wie unterscheiden sich Duisburg und Magdeburg beim Güteraufkommen, Modal Split und bei der Güterstruktur?“ UI-Beispiel.
- **Parameter:** `DEA12`/`DEE03`, gemeinsames vollständiges Jahr 2024 explizit bestätigt; t; alle Landverkehrsträger; C1–C7; Versand plus Empfang.
- **Datenbasis/Quelle:** D01/D04/D10; KBA VE12/13, Destatis 46131/46321, NUTS.
- **Kennzahl/Einheit:** Aufkommen t; Anteile %; Anteilsdifferenzen Prozentpunkte.
- **Erwartung heute:** Duisburg 108.215.313,5 t, Magdeburg 23.180.902,5 t. Modalanteile Straße/Schiene/Binnenschiff: Duisburg 44,8/16,7/38,5 %, Magdeburg 68,7/18,8/12,4 %. Führende Gesamtgütergruppe C1 in Duisburg, C7 in Magdeburg; sieben Gruppen jeweils am Regionsgesamtwert messen.
- **Grenze/Ziel:** kein Vergleich mit Magdeburg 2025 als „aktuellstem Wert“ neben Duisburg 2024. Größenunterschied nicht als Logistikeffizienz interpretieren; gleiche Binnenzählung. Prüfbedarf gemäß Detailkonzept bei anderen Gebietsständen.


### T08 – Frei abgegrenzter Wirtschaftsraum

- **Herkunft/Frage:** P8, Q151; „Können wir dieselbe Analyse für einen frei abgegrenzten Wirtschaftsraum wiederholen?“
- **Parameter:** zunächst klären: Vereinigung ganzer Quellgebiete oder ein Polygon, das Kreise schneidet; 2024, t, Straße, Richtung extern/intern.
- **Datenbasis/Quelle:** D02/D10; KBA VE7 und Geometrien. Für geschnittene Teilgebiete zusätzliche räumliche Evidenz.
- **Kennzahl/Einheit:** externer Versand, externer Empfang, interner Verkehr in t.
- **Erwartung heute:** Prüfbedarf gemäß Detailkonzept benennen. Keine flächenproportionale Verteilung als beobachtete Gütermenge ausgeben.
- **Zielprüfung, synthetisch:** Raum = A+B; A→B 100 t, A→C 40 t, C→B 60 t. Intern 100, externer Versand 40, Empfang 60, raumberührende eindeutige Menge 200 t. A→B weder extern noch doppelt zählen. Eine neue Pipeline muss diese Regel belegen.


### T09 – Ungeeignete Vergleichsräume und Ranggleichheit

- **Herkunft/Frage:** P3/P8, Q042/Q152; „Wie unterscheidet sich unser Güterprofil von drei vergleichbaren Wirtschaftsstandorten?“
- **Parameter:** vorgegeben sind eine Stadt, ein Bundesland und ein Terminal; Vergleichskriterium offen.
- **Datenbasis/Quelle:** D01/D10 beziehungsweise knotenspezifische Quelle nach Klärung.
- **Kennzahl/Einheit:** t oder klar definierte Strukturanteile in %; keine ungeklärte Standortwertung.
- **Erwartung heute:** einheitliche Raum-/Knotenebene, gemeinsames Jahr und Vergleichszweck klären. Keine ungekennzeichnete gemeinsame Rangliste ungleicher Grundgesamtheiten.
- **Zielprüfung, synthetisch:** bei drei vergleichbaren Regionen mit 200, 100, 100 t ergeben sich Ränge 1, 2, 2. Top 2 enthält wegen Gleichstand drei Zeilen; Gleichstand und sekundäre ID-Sortierung erklären, R6.


## F04 – Zeitverlauf und Vergleichbarkeit

### T10 – Magdeburger Schienenentwicklung seit 2016

- **Herkunft/Frage:** P1, Q005; „Wie hat sich der Schienengüterverkehr in Magdeburg seit 2016 entwickelt?“ UI-Beispiel.
- **Parameter:** `DEE03`, 2016–2025, Schiene, t, alle Güter, Versand plus Empfang; Endjahr und Erfassungsprüfung offenlegen.
- **Datenbasis/Quelle:** D01; Destatis EVAS 46131; D04/D10 für Monatsvollständigkeit und Gebiets-/Erfassungsbrüche.
- **Kennzahl/Einheit:** Jahresmenge t, absolute Änderung t, Rate % bei positiver Basis.
- **Erwartung heute:** Bestandsreihe 391.082; 376.529; 413.339; 3.350.578; 3.563.715; 3.712.362; 3.775.110; 4.466.662; 4.368.137; 1.265.439 t in Jahresreihenfolge. Die Sprünge 2018/2019 und 2024/2025 nennen, ihre Ursache nicht behaupten.
- **Grenze/Ziel:** Quellen-/Gebietsstand je Jahresscheibe und Vollständigkeit prüfen; ohne geklärte Brüche keine homogene reale Wachstumsgeschichte formulieren. Prüfbedarf gemäß Detailkonzept; eine vorhandene Jahreszeile allein beweist keine Vergleichbarkeit.


### T11 – Zeitvergleich mit Null und fehlendem Basiswert

- **Herkunft/Frage:** P1/P8, Q020/Q143: Welche Zeitvergleiche lassen sich belastbar fortschreiben?
- **Parameter:** Identisches Gebiet, Gütergruppe, Modus, Richtung und zwei bestätigte Jahre.
- **Datenbasis/Quelle:** D01/D04/D10; amtliche Jahresdaten und Gebietsstände.
- **Kennzahl/Einheit:** Δt und Δ%; Quellenstatus.
- **Erwartete Ergebnislogik:** Synthetisch: 0→10 t: +10 t, Rate undefiniert; 10→0: −10 t/−100 %; 0→0: Δ0, Rate undefiniert; fehlend→10: keine Änderung.
- **Einschränkung/Status:** B02. Kein stilles Ersatzjahr, keine Nullfüllung und keine als harmonisiert bezeichnete Zeitreihe allein durch neue Kartenpolygone.


### T12 – Entwicklung erklären ohne unbelegte Ursache

- **Herkunft/Frage:** P8, Q149; „Warum steigt eine Gütergruppe stark an: reale Entwicklung, Erfassungsänderung oder räumliche Umgliederung?“
- **Parameter:** Region, Gütergruppe, Richtung, zwei Jahre und Verkehrsträger zunächst bestätigen.
- **Datenbasis/Quelle:** D01/D04/D10 plus tatsächlich vorhandene Änderungsprotokolle.
- **Kennzahl/Einheit:** beobachtete Veränderung t/%; Ursachenanteile ohne Zusatznachweis nicht beziffern.
- **Erwartung heute:** Befund von möglichen Erklärungen trennen; Monatsvollständigkeit, Güterzuordnung, Gebietsstand und Revision als konkrete Prüfungen nennen.
- **Grenze/Ziel:** Prüfbedarf gemäß Detailkonzept. Eine einzelne Zeitreihe beweist keine Werkserweiterung oder politische Wirkung. Nur belegte Erfassungs-/Gebietsänderungen aus vorhandenem Material erklären; sonst Ursache offenlassen. Keine externe Ursachenstudie vorbereiten.


## F05 – Änderungsranking und Anteilszerlegung

### T13 – Absolutes und relatives Änderungsranking

- **Herkunft/Frage:** P2, Q023; „Welche Regionen verzeichnen seit 2019 die stärksten absoluten und relativen Rückgänge?“
- **Parameter:** bestätigte vergleichbare Regionen, 2019/2024, Schiene, t, gleicher Richtungsbezug; Mindestbasis für prozentuale Rangfolge explizit.
- **Datenbasis/Quelle:** D01/D10, Destatis; synthetische Grenzwertkontrolle als Ergänzung.
- **Kennzahl/Einheit:** Δt und Δ%; zwei getrennte Ranglisten mit Basis-/Endwert, keine Mischung.
- **Erwartung heute:** Datensatz auf beide Jahre und vergleichbare Gebiete beschränken, ausgeschlossene Fälle nennen; keine still ersetzten Werte.
- **Zielprüfung, synthetisch:** A 1.000→900: −100 t/−10 %; B 100→50: −50 t/−50 %. A führt absolut, B relativ. C 0→5: +5 t/Rate undefiniert; D 10→0: −100 %; E fehlend→10: keine Änderung. Prüfbedarf gemäß Detailkonzept, R5/R6.


### T14 – Kleine Ausgangswerte im Ranking

- **Herkunft/Frage:** P6/P8, Q104/Q152: Welche bisher kleinen Partner wachsen schnell, und wie robust ist das Ranking?
- **Parameter:** 2019/2024, identische Richtung/Güter, Rangmaß relativ; Mindestbasis noch nicht vereinbart.
- **Datenbasis/Quelle:** D02/D04, KBA bzw. Destatis nach gewähltem Verkehrsträger.
- **Kennzahl/Einheit:** Basis/Endwert t, Δt, Δ%.
- **Erwartete Ergebnislogik:** Synthetisch: A 1→10 t: +900 %/+9 t; B 1.000→1.500 t: +50 %/+500 t. Relative und absolute Bedeutung getrennt nennen. Mindestbasis erfragen oder ungekürztes Ranking mit sichtbaren Basen liefern.
- **Einschränkung/Status:** Keine unsichtbare Mindestmenge festlegen. Falls ausdrücklich Basis ≥100 t vereinbart, A ausschließen und Zahl der Ausschlüsse nennen. B01/B02.


### T15 – Mehr Schienenanteil trotz weniger Schienenmenge

- **Herkunft/Frage:** P7, Q126: Entsteht ein höherer Schienenanteil durch mehr Schiene oder weniger Straße?
- **Parameter:** Zwei vollständige gemeinsame Jahre, dieselbe Region, alle Landverkehrsträger, t.
- **Datenbasis/Quelle:** D01; KBA/Destatis.
- **Kennzahl/Einheit:** Mengen t, Anteile %, Anteilsdifferenz Prozentpunkte.
- **Erwartete Ergebnislogik:** Synthetisch: Schiene 20→18 t, Straße 70→32 t, Binnenschiff 10→10 t. Gesamt 100→60, Schienenanteil 20→30 %, +10 Prozentpunkte trotz −2 t Schienenmenge.
- **Einschränkung/Status:** Anteilseffekt beschreiben, keinen nachgewiesenen Wechsel einzelner Sendungen zur Bahn behaupten. Nenner jedes Jahres vollständig; R4/R5.


## F06 – Regionale Güterstruktur

### T16 – Regionale Straßen-Güterstruktur

- **Herkunft/Frage:** P1/P3, Q006/Q041: Welche Güter prägen Versand und Empfang unserer Region?
- **Parameter:** Duisburg, 2024, Straße, C1–C7, Versand/Empfang getrennt, t.
- **Datenbasis/Quelle:** D01 by_mode_groups.road; D04 VE12/VE13 als Rohkontrolle.
- **Kennzahl/Einheit:** t je Gruppe, Anteil an jeweiliger Richtung %.
- **Erwartete Ergebnislogik:** Je sieben Gruppen ausweisen; Gruppensumme im Versand 26.371.111 t, im Empfang 22.134.701 t. Anteil immer am passenden Richtungsnenner.
- **Einschränkung/Status:** Nicht fact_regional_summary.parquet mit Straße ALL als Güterbasis verwenden. Nicht auf einzelne Straßenpartner übertragen. Führende Gruppe erst aus den ungerundeten Gruppenwerten bestimmen.


### T17 – NST-20 auf NUTS-3 im Straßenmodul

- **Herkunft/Frage:** P8, Q145: Welche Gütergliederung erlaubt einen fairen Vergleich?
- **Parameter:** Duisburg/Magdeburg 2024, Straße, gewünschte 20 Abteilungen, NUTS-3.
- **Datenbasis/Quelle:** D01/D04, KBA VE12/VE13; VD3c hat andere Ebene/Population.
- **Kennzahl/Einheit:** Gewünschte t je NST-20; zulässige Alternative t je C1–C7.
- **Erwartete Ergebnislogik:** 20er-Ergebnis auf dieser Grundlage nicht verfügbar. C1–C7 als transparente Alternative anbieten; kein künstliches Aufteilen der sieben Gruppen.
- **Einschränkung/Status:** B03 kann vorhandenes VD3c auf NUTS-2 für deutsche Lkw gesondert erschließen. Kein stiller Wechsel der Regionsebene oder Fahrzeugpopulation.


### T18 – Aktuelle Güterzuordnung statt veralteter Labels

- **Herkunft/Frage:** P8, Q147: Sind sieben Güterhauptgruppen zwischen Ist und Prognose inhaltlich identisch?
- **Parameter:** Aktueller C1–C7-Vertrag und VP-Crosswalk; Codes als Text.
- **Datenbasis/Quelle:** D04, data/crosswalks/README_UMSTIEGSSCHLUESSEL.md und CSV/JSON-Crosswalk; aktive NST-Zuordnung.
- **Kennzahl/Einheit:** Klassifikationszuordnung; Mengen t nur aus jeweils gültiger Quelle.
- **Erwartete Ergebnislogik:** C1=01–03, C2=04–06, C3=07–09, C4=10, C5=11–13, C6=14, C7=15–20. Rohcode 031 gehört zu C1; VP 140 zu NST14/C6.
- **Einschränkung/Status:** dim_nst2007.json enthält abweichende alte Zuordnungen und ist hier keine Begriffsautorität. Gemeinsame Klassifikation macht Erfassungsbereiche und Binnenzählung noch nicht identisch.


## F07 – Güter auf einer Verbindung

### T19 – Schienengütergruppen Köln → Hamburg

- **Herkunft/Frage:** P4, Q062; „Welche Gütergruppen werden auf der Schiene von Köln nach Hamburg transportiert?“ UI-Beispiel.
- **Parameter:** `DEA23` → `DE600`, 2024, Schiene, t, Versand, C1–C7; Jahr explizit vereinbart.
- **Datenbasis/Quelle:** D02/D04; Destatis EVAS 46131, vollständige Relation und amtliche C-Zuordnung.
- **Kennzahl/Einheit:** t je Gruppe; Anteil an 199.851 t dieser Richtung in %.
- **Erwartung heute:** C7 „Sonstige Produkte“ 199.620 t; C1 „Erzeugnisse der Land- und Forstwirtschaft, Rohstoffe“ 231 t. Rohkontrolle: NST 031=231, 161=12.817, 191=186.803 t. Anteile ungerundet rechnen, dann rund 99,9/0,1 %.
- **Grenze/Ziel:** nicht Hamburg → Köln und nicht regionale Kölner Gesamtgüterstruktur verwenden. Nicht beobachtete Gruppen nicht ohne Quellenregel als veröffentlichte Null ausgeben. D04-Detailauswertung ist mögliches Zusatzprodukt von Prüfbedarf gemäß Detailkonzept.


### T20 – Güter auf einer Straßenverbindung

- **Herkunft/Frage:** P5, Q096; „Welche Güter werden auf unserer geplanten Straßenverbindung bereits transportiert?“
- **Parameter:** Köln → Hamburg, 2024, Straße, NST-20 gewünscht.
- **Datenbasis/Quelle:** D02 KBA VE7 hat nur `ALL`; D01 VE12/13 enthält regionale C-Gruppen, keine Straßen-OD-Güterstruktur.
- **Kennzahl/Einheit:** gewünschte Menge t je OD-Gütergruppe; heute nur Gesamtmenge der Verbindung belegbar.
- **Erwartung heute:** Datengrenze erklären; Gesamtmenge als Teilantwort anbieten. Kölner Versandanteile weder auf die OD-Gesamtmenge übertragen noch als beobachtete Relation ausgeben.
- **Grenze:** Keine externe OD-Güterquelle und keine Modellierung vorgesehen. Die Güterfrage ist mit dem vorhandenen Bestand nicht beantwortbar; regionale oder VD3c-Anteile ersetzen keine beobachtete OD-Güterstruktur.


### T21 – Feinere Schienengüter auf der richtigen Richtung

- **Herkunft/Frage:** P6, Q103: Welche Gütergruppen gewinnen auf einer Schienenrelation an Bedeutung?
- **Parameter:** Köln DEA23 → Hamburg DE600, 2023/2024, Schiene, NST-Feinpositionen, t.
- **Datenbasis/Quelle:** D04 SGV-Rohdateien: Jahr, Quell-/Zielregion, Guetergruppe_NST2007, Befoerderungsmenge_in_Tonnen.
- **Kennzahl/Einheit:** t je Feinposition/Jahr, Δt/Δ% bei positiver Basis.
- **Erwartete Ergebnislogik:** B03: je Jahr exakt dieselbe Richtung filtern, Monate prüfen und Feinpositionen aggregieren. Kontrolljahr 2024: 031=231, 161=12.817, 191=186.803 t; Summe 199.851 t.
- **Einschränkung/Status:** 2023-Werte müssen noch gegen Quelle ermittelt werden; keine Rate aus unermitteltem Basiswert. Gegenrichtung ist ein anderer Fall. Keine feinere Aufteilung aus C-Gruppen zurückrechnen.


## F08 – Modal Split

### T22 – Nationaler Modal Split nach Verkehrsleistung

- **Herkunft/Frage:** P2, Q021; „Wie verteilt sich die deutsche Güterverkehrsleistung auf Straße, Schiene und Binnenschiff?“
- **Parameter:** Deutschland, 2024, tkm, alle Güter, nationale Gesamtabgrenzung.
- **Datenbasis/Quelle:** D03; KBA VE7 `Inlands_tkm`, Destatis 46131/46321.
- **Kennzahl/Einheit:** tkm bzw. Mrd. tkm und Anteile in %.
- **Erwartung heute:** insgesamt 624.919.760.431 tkm; Straße 455.156.638.190; Schiene 126.319.807.860; Binnenschiff 43.443.314.381. Anteile rund 72,8/20,2/7,0 %.
- **Grenze/Ziel:** keine Summe D01-Regionen als Deutschland-Nenner; keine See-/Luftmenge hinzufügen; keine gespeicherten Tonnenanteile für tkm verwenden. Antwort nennt den nationalen Leistungsbezug.


### T23 – Unvollständiges Modal-Split-Jahr

- **Herkunft/Frage:** P7, Q125, Variante mit ausdrücklichem Endjahr 2025; „Wie verändert sich der Modal Split unserer Region bis 2025?“
- **Parameter:** Duisburg, 2016/2025, alle drei Landverkehrsträger, t.
- **Datenbasis/Quelle:** D01/D03-Verfügbarkeit; KBA/Destatis.
- **Kennzahl/Einheit:** gewünschte Anteile %, Anteilsänderung Prozentpunkte.
- **Erwartung heute:** vollständiger 2025-Vergleich nicht verfügbar, weil Straße fehlt. Weder Straße=0 noch Normierung von Schiene/Binnenschiff auf 100 % der drei Verkehrsträger.
- **Ziel:** vollständiges gemeinsames Jahr 2024 als ausdrücklich benannte Alternative anbieten; keine stille Änderung des Endjahrs. Vollständige 2025-Antwort erst nach geprüftem Straßenjahr. Prüfbedarf gemäß Detailkonzept und R4.


### T24 – Regionaler Modal Split mit passendem Nenner

- **Herkunft/Frage:** P1/P7, Q003/Q125: Wie verteilt sich Duisburgs Güteraufkommen auf die Verkehrsträger?
- **Parameter:** DEA12, 2024, t, Versand plus Empfang, alle Güter.
- **Datenbasis/Quelle:** D01, KBA VE12/VE13 und Destatis 46131/46321.
- **Kennzahl/Einheit:** t und Anteil %.
- **Erwartete Ergebnislogik:** 48.505.812 t Straße, 18.055.930 t Schiene, 41.653.571,5 t Binnenschiff; Nenner 108.215.313,5 t. Anteile 44,8/16,7/38,5 %.
- **Einschränkung/Status:** Keinen D03-Nationalnenner oder D06-Richtungsnenner einsetzen. Bei tkm-Anfrage andere Quellfelder und Anteile neu rechnen. D01-Binnenzählung nennen.


## F09 – Versand, Empfang, Binnen und Transit

### T25 – Versand und Empfang sind keine Leerfahrten

- **Herkunft/Frage:** P6/P3, Q102/Q050; „Auf welchen Relationen oder in welchen Regionen sind die Richtungen besonders unausgeglichen?“
- **Parameter:** Kontrollfall Duisburg, Straße, 2024, alle Güter; regionale Richtungswerte in t.
- **Datenbasis/Quelle:** D01/D04; KBA VE12/VE13.
- **Kennzahl/Einheit:** Versand, Empfang, Saldo = Versand − Empfang in t.
- **Erwartung heute:** 26.371.111 t Versand, 22.134.701 t Empfang, +4.236.410 t Saldo. Rohsummen wurden bestätigt; positiver Saldo bedeutet mehr Versand.
- **Grenze/Ziel:** daraus keine Leerfahrtenquote und keine freien Rückladungen ableiten. Leerfahrten-/Rückladungsaussagen bleiben mangels entsprechender Belege außerhalb. Für Relationssaldo D02 statt regionaler Summen verwenden; keine Prozentwachstumsrate eines Saldos.


### T26 – Binnenverkehr und örtlicher Transit

- **Herkunft/Frage:** P1, Q007; „Wie groß sind Binnenverkehr, ein- und ausgehender Verkehr sowie Durchgangsverkehr in unserer Stadt?“
- **Parameter:** Stadtgebiet, 2024, Straße, t; Binnen = Quelle und Ziel im Gebiet; Transit = Weg durch Gebiet bei beiden Endpunkten außerhalb.
- **Datenbasis/Quelle:** D02/D10 für OD-Anteile; tatsächliche Wege/Netzzuordnung zusätzlich erforderlich.
- **Kennzahl/Einheit:** Binnen, externer Versand, externer Empfang, Transit in t jeweils separat.
- **Erwartung heute:** OD-Anteile möglich; örtlicher Transit ohne Wegeinformation nicht belegbar. Beide Endpunkte außerhalb beweisen keinen Durchgang durch die Stadt, Prüfbedarf gemäß Detailkonzept.
- **Zielprüfung, synthetisch:** A→A 10, A→B 20, B→A 30 t: eindeutig berührende Menge 60 t; Versand inkl. Binnen 30, Empfang inkl. Binnen 40, D01-artige Summe 70. Unterschied erklären, keine still gleiche Gesamtabgrenzung.


### T27 – Nationaler Transit aus vorhandenen Rohquellen

- **Herkunft/Frage:** P2, Q026: Welchen Anteil hat Transit an der Verkehrsleistung in Deutschland?
- **Parameter:** Deutschland, 2024, Schiene, tkm, amtliche Verkehrsbeziehung.
- **Datenbasis/Quelle:** D04 SGV-Rohdatei 2024, Verkehrsbeziehung=4 laut Quelllabel; Befoerderungsleistung_in_TKM; D03 als Randsummenkontrolle.
- **Kennzahl/Einheit:** Transit-tkm / vollständige nationale Schienen-tkm ×100.
- **Erwartete Ergebnislogik:** B05: alle Rohzeilen der Transitkategorie summieren, nicht nur regional kartierbare OD-Zeilen. Nenner gesamte passende Rohreihe einschließlich übriger Verkehrsbeziehungen; gegen 126.319.807.860 tkm prüfen.
- **Einschränkung/Status:** Transitwert/Quote hier noch nicht numerisch erhoben; Ergebnislogik ist vollständig festgelegt. Nicht als Transitanteil einer Stadt interpretieren. Für Straße wäre Inlands_tkm und deren Verkehrsbeziehungsdefinition separat erforderlich.


## F10 – Vorhandene Verkehrsprognose

### T28 – Größter prognostizierter Schienenzuwachs

- **Herkunft/Frage:** P2, Q022; „Wo wächst das Schienengüteraufkommen laut Prognose von 2019 bis 2040 am stärksten?“ UI-Beispiel.
- **Parameter:** Deutschland, 400 im aktuellen NUTS-2024-Geometriebestand enthaltene Regionen, gemeinsame VP-IDs, 2019_BASE/2040_P1, Schiene, t, Gesamt inkl. Binnen einmal; „stärksten“ hier bestätigt als absoluter Zuwachs, Top 5.
- **Datenbasis/Quelle:** D05/D10; VP2040 V01, `regions[id].modes_tonnes.rail`; Menge der 400 IDs explizit begrenzen, Sonderzellen ausschließen.
- **Kennzahl/Einheit:** Basis, Ziel, Δt und ergänzend Δ%; Ranking nach Δt.
- **Erwartung heute:** Hamburg `DE600` +17.819.607; Köln `DEA23` +8.699.699; `DEB34` +5.872.803; `DE502` +4.783.846; `DE212` +4.423.252 t. Namen aus D10 ergänzen.
- **Grenze/Ziel:** relative Rangfolge ist eine andere Frage; keine gemessenen 2040-Werte, kein Abgleich gegen amtliche Ist-2019 als Ersatzbasis. Raumgrundgesamtheit nennen.


### T29 – Ist-Entwicklung neben der Prognose

- **Herkunft/Frage:** P2, Q032; „Passt die beobachtete Entwicklung seit 2019 noch zur Verkehrsprognose?“
- **Parameter:** Duisburg, alle Landverkehrsträger, t; Ist 2019/2024 versus VP 2019_BASE/2040_P1.
- **Datenbasis/Quelle:** D01, D05, D10; KBA/Destatis neben VP2040.
- **Kennzahl/Einheit:** jeweils eigene Basis-/Endwerte, eigene Änderung t/%; keine ungeprüfte gemeinsame Wachstumsrate.
- **Erwartung heute:** Ist-Reihe und Prognosepfad getrennt präsentieren; D01 zählt Binnen doppelt, D05 einmal. Bestandskontrolle VP 115.374.997→103.871.423 t ergibt rund −10,0 %.
- **Grenze/Ziel:** aus Ist 108.215.313,5 t für 2024 gegenüber VP2040 keine „verbleibende Wachstumsrate“ als vergleichbare Statistik ausgeben. Keine lineare VP-Zwischenprognose 2024 erfinden. Harmonisierung vorhandener Quellabgrenzungen gesondert prüfen; ein neuer Verlauf wird nicht modelliert.


### T30 – Vorhandene Prognose mit Nullwerten und Szenariogrenze

- **Herkunft/Frage:** P8/P2, Q154/Q035: Wie wird die Prognose ohne Scheinsicherheit dargestellt?
- **Parameter:** 2019_BASE/2040_P1, gleiche Region und Kennzahl; alternative Szenarien ausdrücklich angefragt.
- **Datenbasis/Quelle:** D05, VP2040 V01; ausschließlich vorhandene Szenarien.
- **Kennzahl/Einheit:** Basis/Ziel t, Δt/Δ%; Status Prognose.
- **Erwartete Ergebnislogik:** Synthetischer Rechenrandfall: Basis100/Ziel0 ergibt −100 t/−100 %; Basis0/Ziel100 ergibt +100 t und undefinierte Rate; fehlendes Ziel keine Änderung.
- **Einschränkung/Status:** Kein P2, Energieszenario oder jährlicher Zwischenpfad erfinden. Zusätzliche Szenariomodelle sind außerhalb des Umfangs. VP-P1-Werte als bedingte Prognose benennen.


## F11 – Statistische intermodale Teilmärkte

### T31 – Intermodale Teilmärkte getrennt

- **Herkunft/Frage:** P6/P8, Q117/Q153; „Wie unterscheiden sich die intermodalen Teilmärkte, und lassen sie sich zu einem KV-Gesamtwert addieren?“
- **Parameter:** Deutschland, 2024, t und tkm jeweils getrennt, keine regionalen Filter.
- **Datenbasis/Quelle:** D06 `data_by_year`; Destatis EVAS 46131/46321.
- **Kennzahl/Einheit:** Teilmarktmenge t, Leistung tkm, Anteil am jeweiligen Verkehrsträger %.
- **Erwartung heute:** Schiene 99.853.065 t von 337.515.115 t; Binnenschiff 16.738.676,4 t von 173.778.020,4 t. Jeweilige Quote aus diesen Nennern; bei tkm die dazugehörigen tkm-Werte verwenden.
- **Grenze/Ziel:** ausdrücklich kein nationaler eindeutiger KV-Gesamtwert aus der Summe; `not_additive=true`. Eine neue Ketten-Deduplizierung ist nicht vorgesehen und kann nicht aus Teilmarktanteilen rekonstruiert werden.


### T32 – Regionaler intermodaler Anteil im Versand

- **Herkunft/Frage:** P4, Q071; „Wie groß ist der Anteil intermodaler Verkehre an der Schiene im Einzugsgebiet?“
- **Parameter:** Einzugsgebiet hier ausdrücklich Duisburg `DEA12`, 2024, Schiene, t, externer Versand ohne Binnen.
- **Datenbasis/Quelle:** D06 `scoped_metrics_by_year.2024.DEA12.rail`; Destatis 46131.
- **Kennzahl/Einheit:** 4.422.816 t mit Ladeeinheit / 9.194.861 t externer Schienenversand ×100, rund 48,1 %.
- **Erwartung heute:** regionalen Richtungsnenner verwenden; nicht nationale Quote oder D01-Versand inklusive Binnen. Aktuelle regionale D06-Verfügbarkeit anerkennen.
- **Grenze/Ziel:** administratives Gebiet ist nicht automatisch betriebliches Einzugsgebiet. Bei anderem Gebiet Prüfbedarf gemäß Detailkonzept, keine Behauptung über freie Terminalkapazitäten oder bedienbare Mengen.


### T33 – Statistischer KV ist kein Verlagerungspotenzial

- **Herkunft/Frage:** P8/P1, Q153/Q011: Ist aus den vorhandenen KV-Mengen das Verlagerungspotenzial erkennbar?
- **Parameter:** National oder genau bestätigte Region, 2024, Schiene/Binnenschiff getrennt, t.
- **Datenbasis/Quelle:** D06, Destatis 46131/46321.
- **Kennzahl/Einheit:** Zulässig: beobachtete Teilmarktmengen t und jeweilige Anteile %. Nicht verfügbar: realistisch verlagerbare Menge.
- **Erwartete Ergebnislogik:** Getrennte Teilmarktwerte als Kontext liefern. Keine Addition zu eindeutigen Ketten und keine verbleibende Straßenmenge als Potenzial ausgeben.
- **Einschränkung/Status:** Kapazitäten, Kosten, Gütereignung und betriebliche Transportketten werden nicht ergänzt. Q011 bleibt außerhalb; das ist eine bewusste Grenze, kein Pipelineauftrag.


## F12 – Hafen- und Flughafenstatistik

### T34 – Flughafenprofil mit unterschiedlichen verfügbaren Jahren

- **Herkunft/Frage:** P4, Q074; „Wie unterscheiden sich Luftfrachtmenge und Zahl reiner Fracht- und Postflüge an unserem Flughafen?“
- **Parameter:** Leipzig/Halle `EDDP`, ausdrücklich 2025, Fracht und Post, beide Richtungen.
- **Datenbasis/Quelle:** D08; Eurostat AVIA_GOOA, `airportValues` und `metadata.availableAirportFlightYears`.
- **Kennzahl/Einheit:** Fracht/Post in t; reine Fracht-/Postflüge in Anzahl.
- **Erwartung heute:** vorhandenen Tonnenwert 2025 mit Quelle ausweisen, Flughafen-Flugzahl 2025 als nicht belastbar/nicht verfügbar kennzeichnen. 2024 nur als ausdrücklich benannte Alternative anbieten; nationale Flugzahl nicht einsetzen.
- **Grenze/Ziel:** Passagierflüge mit Beiladefracht nicht als reine Frachtflüge zählen. Gemeinsamen Vergleich auf das vorhandene vollständige Jahr 2024 beschränken, wenn dies bestätigt wird. Keine neue externe Quelle beschaffen; keine Beladungskennzahl aus fehlenden Flügen.


### T35 – Veröffentlichte Luftfrachtpartner und richtiger Nenner

- **Herkunft/Frage:** P4, Q075; „Welche internationalen Flugverbindungen tragen den größten Teil unserer Luftfracht?“
- **Parameter:** `EDDP`, 2024, t, Versand, externe Flughafenpartner, Top 5.
- **Datenbasis/Quelle:** D08; Eurostat AVIA_GOR_DE, `relations` und passend gefilterte `relationTotals`.
- **Kennzahl/Einheit:** veröffentlichte Relationsmenge in t und Anteil an der passenden veröffentlichten Relationssumme in %.
- **Erwartung heute:** positive Verbindungen sortieren; Nenner nicht aus den angezeigten fünf Zeilen bilden. Veröffentlichungsschwelle und Top-25-Speichergrenze benennen. Ohne passenden internationalen Nenner nur Mengen/Ränge oder Datenbedarf ausgeben, keinen Ersatzanteil.
- **Grenze/Ziel:** kein Anteil am vollständigen Flughafenaufkommen aus einer inkompatiblen Relationssumme. Für beliebige internationale Unterauswahlen vollständige publizierte Rohrelationen aus D08 zusätzlich aufbereiten, Prüfbedarf gemäß Detailkonzept.


### T36 – Seehafenumschlag, TEU und Vergleichsjahre

- **Herkunft/Frage:** P4, Q064: Wie hoch sind Umschlag und Containeraufkommen unseres Seehafens im Zeitvergleich?
- **Parameter:** Eindeutig benannter Seehafen, 2023/2024, Ein-/Ausladung, t und TEU getrennt.
- **Datenbasis/Quelle:** D07 und vorhandene Hafenprofile; Destatis EVAS 46331, MRTM-Rohdaten.
- **Kennzahl/Einheit:** Umschlag t, Containermaß TEU; jeweilige absolute/relative Änderung.
- **Erwartete Ergebnislogik:** Gleichen Hafen und Richtungsbezug pro Jahr verwenden. t und TEU nebeneinander, keine Umrechnung mit unterstelltem Durchschnittsgewicht. Fehlender Richtungswert verhindert vollständigen Saldo.
- **Einschränkung/Status:** B06 bei zusätzlichen veröffentlichten Partnerauswahlen. Keine Terminalkapazität, Hinterlandkette oder eindeutige gesamtwirtschaftliche Warenmenge aus Umschlag ableiten.


## F13 – Monatsdaten und Mautvergleich

### T37 – Mautfahrten nach Richtung

- **Herkunft/Frage:** P6, Q109; „Wie viele mautpflichtige Fahrten entfallen auf unsere Zielgemeinde, getrennt nach Start und Ziel?“
- **Parameter:** bestätigter achtstelliger AGS als Text, einzelner verfügbarer Monat, Start/Ziel und Binnenzählung.
- **Datenbasis/Quelle:** D09; BALM/Toll Collect; Prüfbedarf gemäß Detailkonzept für festes, gezielt abgefragtes Datenabbild. Hier kein Live-Abruf.
- **Kennzahl/Einheit:** `anzahl_befahrungen`, Anzahl Mautfahrten; keine t.
- **Erwartung heute:** numerische Abnahme erst mit gespeichertem zulässigem Gemeindeauszug; Abrufstatus und fehlende Werte benennen.
- **Zielprüfung, synthetisch:** A→A 5, A→B 10, B→A 20: Start 15, Ziel 25, eindeutige A-berührende Fahrten 35. Keine Summe 40 ohne Doppelzählungshinweis. Führende Null eines AGS bleibt erhalten; keine deutschlandweite Komplettabfrage auslösen.


### T38 – Vorjahresmonat und fehlende Angaben

- **Herkunft/Frage:** P6, Q108; „Welche mautpflichtigen Gemeindeverbindungen haben zuletzt besonders stark zugelegt?“
- **Parameter:** fokussierte Gemeinde, Richtung, konkret bestätigter Monat/Vorjahresmonat, absolutes Ranking; einzelne Relation eindeutig.
- **Datenbasis/Quelle:** D09 und festes Abbild Prüfbedarf gemäß Detailkonzept, BALM/Toll Collect.
- **Kennzahl/Einheit:** ΔMautfahrten und Δ%; gleicher Monat des Vorjahres.
- **Erwartung heute:** Verfügbarkeit von Monat und Relation getrennt prüfen; keine bundesweite Rangliste aus einem Gemeindeauszug. Explizit gewünschten Monat nicht ersetzen.
- **Zielprüfung, synthetisch:** 120 gegenüber 100: +20/+20 %. Vorjahr fehlt: beide Änderungen nicht berechenbar. Vorjahr 0: +120, Prozent undefiniert. Fehlt angefragter Vorjahresmonat, Alternative nur ausdrücklich benannt; existierender Monat macht nicht jede Relation vollständig.


### T39 – Monatliche Güterspitzen

- **Herkunft/Frage:** P4, Q072; „Welche saisonalen Güterspitzen sollten bei der Personalplanung berücksichtigt werden?“
- **Parameter:** Magdeburg, Schiene, Gütergruppe und Richtung, vollständige Monatsjahre; Terminalbezug separat.
- **Datenbasis/Quelle:** D04, SGV-Rohfeld `Referenzzeitraum_Monat`; vorhandene Quelle, zusätzliche Aufbereitung Prüfbedarf gemäß Detailkonzept. Die Personalplanung selbst liegt außerhalb.
- **Kennzahl/Einheit:** t/Monat, Monatsanteile %, gegebenenfalls Schwankungskennzahl mit Definition.
- **Erwartung heute:** jährliches D01-Aufkommen nicht in zwölf erfundene Monatsmengen aufteilen; NUTS-Region nicht automatisch Terminaldurchsatz.
- **Zielprüfung, synthetisch:** elf Monate je 100 t, ein Monat 200 t: 1.300 t/Jahr; Spitzenmonat 15,4 %, Mittel 108,3 t. Fehlender Monat verhindert Volljahresanteile. Kein Personalbedarf aus der statistischen Monatsreihe ableiten.


## F14 – Zusätzliche vorhandene Straßendetails

### T40 – Entfernungsstufen aus vorhandenen Rohdaten

- **Herkunft/Frage:** P6, Q111; „Wie verteilen sich Lkw-Fahrten unserer Region auf Nah-, Regional- und Fernverkehr?“
- **Parameter:** Nürnberg, 2024, Versand; amtliche Entfernungsstufen und Fahrzeugpopulation vorab bestätigen.
- **Datenbasis/Quelle:** D04, KBA VD2-V, vorhandener Rohordner `Versand_VD2V_NUTS3`; zusätzliche Aufbereitung Prüfbedarf gemäß Detailkonzept.
- **Kennzahl/Einheit:** Fahrten je Entfernungsstufe in Anzahl und Anteil %; t nur als getrennte Kennzahl.
- **Erwartung heute:** Rohbestand als Ansatz benennen, Ergebnis nicht aus tkm/t einer Region rekonstruieren. VD2 betrifft deutsche Lkw; nicht als vollständige europäische VE7-Population bezeichnen.
- **Ziel:** Quellfelder, Inland/Gesamt-Abgrenzung und Stufengrenzen prüfen, dann Klassen summieren und gegen passende Rohsumme kontrollieren. Keine frei erfundenen Kilometergrenzen; fehlende Klassen nicht nullsetzen.


### T41 – Vorhandene VD3c-Details auf NUTS-2

- **Herkunft/Frage:** P2/P8, Q039/Q145: Welche zusätzlichen Straßengüterdetails sind aus vorhandenen Daten nutzbar?
- **Parameter:** NUTS-2-Gebiet DEA2, 2024, Versand, deutsche Lkw, 20 NST-Abteilungen; Gesamt/Inland explizit festlegen.
- **Datenbasis/Quelle:** D04, vorhandene KBA-Ordner Versand_VD3cV_NUTS2_20Gueter und Empfang_VD3cE_NUTS2_20Gueter.
- **Kennzahl/Einheit:** Tonnen bzw. tkm je NST-Abteilung; Fahrten nur getrennt.
- **Erwartete Ergebnislogik:** B03: tatsächliche Felder TON_G/TKM_G versus Inlandskomponente und Quellkennzeichen prüfen; je Abteilung aggregieren und passende Rohsumme kontrollieren.
- **Einschränkung/Status:** Keine ausländischen Lkw ergänzen oder VE7-Vollpopulation behaupten. Kein NUTS-3- oder konkretes OD-Ergebnis. Numerische Sollwerte erst nach der separaten Rohdatenprüfung fixieren.


### T42 – Null, fehlend und Quellenkennzeichen

- **Herkunft/Frage:** P8, Q144; „Wie lassen sich veröffentlichte Nullwerte, fehlende Angaben und eingeschränkt belastbare Schätzwerte unterscheiden?“
- **Parameter:** konkrete Quelle, Jahr, Region/Relation und Kennzahl.
- **Datenbasis/Quelle:** D04-KBA inklusive ZS; D08-Veröffentlichungshinweise; D02 allein verliert Flags. Prüfbedarf gemäß Detailkonzept.
- **Kennzahl/Einheit:** Status je Wert, Menge t nur bei gültiger Zahl.
- **Erwartung heute:** fehlende Flagfelder im Auswertungsbestand offenlegen. `( )` nicht ohne geprüfte Quellendefinition als Geheimhaltung oder Null interpretieren.
- **Zielprüfung, synthetisch:** belegte 0 → 0 t; nicht veröffentlichter Wert → keine Zahl, Status erhalten; Zahl 100 mit Einschränkungsflag → 100 t plus belegte Einschränkung; fehlende Zeile → ungeklärte Verfügbarkeit. Summe mit fehlender Komponente nicht als vollständig ausgeben. Vier Zustände müssen unterscheidbar bleiben.


## F15 – Quelle, Machbarkeit und Grenzen

### T43 – Regional- und Deutschlandwerte widersprechen sich scheinbar

- **Herkunft/Frage:** P8, Q142; „Warum weichen die Summe der Regionalwerte und der Deutschlandwert voneinander ab?“
- **Parameter:** 2024, Landverkehr, t bzw. tkm explizit unterscheiden; D01 gegenüber D03.
- **Datenbasis/Quelle:** D01/D02/D03/D04; KBA VE12/13 versus VE7-Inlandsleistung, Destatis-Nationalwerte mit Transit/weiteren Quellzeilen.
- **Kennzahl/Einheit:** gleiche Einheiten, aber dokumentiert verschiedene Zähl-/Erfassungsbereiche.
- **Erwartung heute:** regionale Versand-/Empfangsberührung und Mehrfachzählung sowie nationale Leistungsabgrenzung erklären. Keine „Korrektur“ der Deutschlandzahl durch Regionssumme.
- **Grenze/Ziel:** `trips` aus D02 ist bei Straße Fahrten, bei anderen Modi aus Ladeeinheiten/Ladungsträgern abgeleitet; verkehrsträgerübergreifende Fahrzeugsumme unzulässig. Einheiten- und Populationsvertrag gehört in Prüfbedarf gemäß Detailkonzept.


### T44 – Reproduzierbare Analyse und belegte Kurzfassung

- **Herkunft/Frage:** P8, Q157; „Wie kann ein zweiter Prüfer einen Regions- oder Relationsvergleich vollständig reproduzieren?“
- **Parameter:** Beispiel T07 oder T19, identischer Datenstand, alle Filter und Sortierregeln.
- **Datenbasis/Quelle:** D01/D02/D04/D10 und [Prüfnachweis](ANALYSEASSISTENT_ETAPPE1_PRUEFNACHWEIS.md).
- **Kennzahl/Einheit:** Übereinstimmung von Quellwerten, Rechenergebnis und Antwort; t/%/Prozentpunkte gemäß gewähltem Fall.
- **Erwartung heute:** Quellenpfad/Herausgeber, Datenstand/Prüfsumme, Gebietscodes, Jahr, Richtung, Güter, Verkehrsträger, Nenner, Rundung und Einschränkungen vollständig nennen. Prüfer muss Ergebnis ohne freie Interpretationsentscheidung nachrechnen können.
- **Grenze/Ziel:** Quellenangabe allein reicht nicht; Datenrevision muss als neuer Stand erkennbar sein. Methodische Grenzen auch in einer kurzen Verwaltungszusammenfassung erhalten. Keine Vertraulichkeits- oder Veröffentlichungsfreigabe aus der bloßen lokalen Dateiverfügbarkeit ableiten.


### T45 – Fragen außerhalb des bestätigten Umfangs

- **Herkunft/Frage:** P5/P7/P4, Q082/Q121/Q066: Was kosten Transporte, welche Umweltbilanz haben sie und wie ausgelastet ist ein Terminal?
- **Parameter:** Vom Nutzenden benannte Region/Relation/Knoten; gewünschte Kennzahl erkennen.
- **Datenbasis/Quelle:** Im vorgesehenen Güterdatenbestand keine geeignete Kosten-, Emissions- oder Kapazitätsdatenbasis. Originalquelle für diese Zahlen daher nicht vorhanden.
- **Kennzahl/Einheit:** Gewünscht: Euro, CO₂e oder Auslastung %. Heute keine solche Zahl; gegebenenfalls klar bezeichnete Verkehrsmenge t aus D01/D02/D06.
- **Erwartete Ergebnislogik:** Knapp erklären, dass die verlangte Aussage mit dem vorgesehenen Datenumfang nicht belegbar ist. Passende statistische Verkehrskennwerte als begrenzte Alternative anbieten.
- **Einschränkung/Status:** Keine externen Quellen, Umweltbilanzen, Kapazitäts- oder Transportkettenmodelle vorbereiten oder versprechen. Auch eine plausible Schätzung oder synthetische Rechenzahl darf nicht als reale Antwort erscheinen.


## Abdeckung und Freigabe

| Anforderung | Nachweis |
|---|---|
| 15 Typen | je drei Fälle T01–T45 in der angegebenen Reihenfolge |
| Sechs UI-Beispiele | Q001/T01, Q003/T07, Q004/T04, Q005/T10, Q022/T28, Q062/T19 |
| Perspektiven | P1 T01/T02/T07/T10/T16/T24/T26; P2 T13/T22/T27/T28/T29/T41; P3 T03/T09/T16; P4 T05/T19/T32/T34–T36/T39; P5 T20/T45; P6 T14/T21/T25/T31/T37/T38/T40; P7 T15/T23/T24/T45; P8 T06/T08/T11/T12/T17/T18/T30/T33/T42–T44 |
| Raum | NUTS-3/NUTS-2, Deutschland, ganze Regionsverbünde, OD, Knoten und AGS; örtliche Routen/Teilgebiete als Grenze |
| Zeit | Jahresverlauf, Gebietsbruch, Monatsvergleich, VP2019/2040; fehlende Jahre und Nullbasis |
| Güter/Richtung | C1–C7, NST-20/Feinpositionen, fehlende Straßen-OD-Güter, Versand/Empfang/Binnen/nationaler Transit |
| Rohdatenlücken | B01 vollständige Relationen/Flags; B02 Monate/Zeit; B03 Detailgliederung; B04 Regionsverbünde; B05 nationale Verkehrsbeziehungen; B06 Knotenrelationen; B07 gezielte Mautstände |
| Bewusste Grenzen | T12 Ursachen, T20 Straßen-OD-Güter, T26 örtlicher Transit, T30 neue Szenarien, T33 Potenzial/Ketten, T45 Umwelt/Kapazität/Kosten |

**Offen:** fachliche Bestätigung von Auswahl und Definitionen; Entscheidung über sinnvolle Rohdatenaufbereitungen; konkrete Sollwerte für die noch nicht numerisch geprüften Rohdatenfälle. Der Katalog ist prüfbar vorbereitet, aber weder als vollständig numerisch abgenommener Datensatz noch als bestandener Modelltest ausgewiesen.
