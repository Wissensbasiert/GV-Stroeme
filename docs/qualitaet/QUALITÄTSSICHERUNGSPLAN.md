# Qualitätssicherungsplan für das Güterströme-Dashboard

**Lokal, 15.09.2026:** Diagrammspezifische Kopfzeilen, regionale KV-Struktur und verzögerte Ladeanzeige umgesetzt. 228 Quellenkontrollen, 25 Browseransichten und bestehende Export-/Lade-/Luft-KPI-Prüfungen bestanden. Noch nicht bereitgestellt. [Prüfbericht und Grenzen](DIAGRAMMKONTEXT_UND_KV_20260915.md).

**Testportal, 14.09.2026 – `loading01`:** Relationsanfragen für 2025 nennen den verfügbaren Jahrgang 2024; Flughafenhinweise aktualisiert und Ladeanzeige ohne Layoutverschiebung über der Karte. 218 lokale Tests, vollständige Linux-Prüfung und Browserstichprobe bestanden. [Bereitstellung und Nachweis](LADEANZEIGE_UND_RELATIONSJAHRE_20260914.md). Nachfolgend frühere Prüfstände.

## Lokale Antwort- und Ladehinweise vom 14.09.2026

Konkrete Knotenverbindungen unterscheiden jetzt fehlende Relationsjahrgänge von fehlenden Einzelwerten. Bei der 2025-Anfrage wird 2024 als neuester vorhandener Relationsjahrgang genannt; bekannte London-Teilsummen bleiben erhalten. Flughafen-Infobox und Quellenfenster nennen Gesamtwerte bis 2025 und Relationen bis 2024. Die gemeinsame Ladeanzeige liegt ohne zusätzliche Layoutzeile über der Karte.

Prüfung: Abschließend 218/218 lokale Laufzeittests bestanden (214 Sekunden, keine externen Modellaufrufe). Darin 24 gezielte Knoten-/Flughafentests bestanden, darunter Originalquellen, 994-Flüge-Teilsumme, neuer Jahrgangshinweis, Nullwerte und fehlende TEU. Die Prüfung mit temporären Dateien musste wegen des eingeschränkten Zugriffs auf C:\tmp separat mit freigegebenem Zugriff wiederholt werden und bestand in drei Sekunden. Gemeinsame Lade-/Fehlerprüfungen, Frontendbuild, JavaScript-Syntax und UTF-8-Prüfung bestanden. Chrome bestätigt identische Kartenposition/-größe beim Ladewechsel in der Übersicht sowie stabile, mittig platzierte Anzeige im Prognosemodul; Fehler-/Wiederholungsanzeige geprüft. Keine neue externe Modellstichprobe. Dieser Nachtrag beschreibt ausschließlich lokale Änderungen, keine neue Bereitstellung im Test- oder Produktivportal.

## Luftverkehr: korrigiertes Eurostat-Update vom 14.09.2026

Die aktualisierten GOOA-/GOOC-Dateien wurden lokal neu aufgebaut und unabhängig geprüft: 1.391 Originalzellen, 66 neue Flugwerte 2025, 281/281 Koordinaten, 10 Partner- und 202 Hauptprüfungen des neuen B04–B06-Stands. Die korrigierte Flughafensumme beträgt 119.237 reine Fracht-/Postflüge. Der Quellenhash entscheidet über die Freigabe; ältere Datenstände bleiben gesperrt. Relationen bleiben auf 2024 begrenzt. Der abhängige KI-Bestand wurde mit 32.296 Quellenvergleichen erneuert. 217/217 lokale Laufzeittests und die Prüfung des vollständig kopierten Übergabepakets bestanden. Der [Prüfbericht](LUFTVERKEHR_UPDATE_20260914.md) dokumentiert Datenstände und Grenzen. Testrelease `portal-test-20260914-gueterstroeme-air01` aktiv: sämtliche 1.749 Dateien auf Linux bestätigt, korrigierte 2025-Abfragen und bestehende Funktionen geprüft; Browser bestätigt Leipzig/Halle mit 48.657 Flügen und −2,6 %. API und Datenbank bereit. Keine externen Modellaufrufe; Produktion unverändert. Die folgenden Abschnitte enthalten weitere aktuelle beziehungsweise historische Prüfstände.

**14.09.2026, Version 0.7.0 – Flughafenverbindungen und Vorschaufragen:** Testrelease `nodes02` aktiv. IATA-/ICAO-Einzelauswahl, kataloggebundene London-Gruppe mit sichtbaren Fehlstellen und bekannten Teilsummen, Gegenräume und geschützte Folgefragen. Verwaltungsvorlagenfrage entfernt; fünf verbleibende Vorschaufragen mit dem echten Modell geprüft. 215 lokale Tests und abschließende Linux-Prüfung aller 1.732 Dateien samt früheren Fachregressionen bestanden. 13 freigegebene Modellfragen, zwei abgeschlossene lesende Gemini-Prüfungen und eigene Befundbewertung. Ein während paralleler Datenarbeit entstandener Mischstand `nodes01` wurde erkannt und zurückgerollt; Paket-Builder prüfen künftig zusätzlich die fertig kopierte Laufzeit. `nodes01` ist kein Rückfallstand. [Verbindlicher Abschluss und Grenzen](ANALYSEASSISTENT_KNOTEN_VORSCHAU_20260914.md). Nachfolgend historische Stände.

**14.09.2026, Version 0.6.0 – Gegenräume, Gesamtsummen und lesbare Antworten:** Testrelease scope01 aktiv, 189 lokale Tests und Linux-Prüfung aller 1.731 Dateien bestanden. Originaldialoge Duisburg/Ausland/Inland und Berlin/Gesamtverkehr mit tatsächlichem Modell geprüft; kurze Ersatzantwort schützt bei unvollständigen oder zu ausführlichen Modelltexten. Zwei lesende Gemini-Prüfungen mit eigener Bewertung. Originaldaten nicht umgebaut; KV bleibt getrennt, fehlende Straße 2025 erzeugt keine erfundene Gesamtsumme. Browserdarstellung lokal geprüft, frischer Portalchat erreichbar, keine Kundenbuchung. Produktion und sieben ältere Releases unverändert. [Verbindlicher Abschluss und Grenzen](ANALYSEASSISTENT_RAUM_SUMMEN_20260914.md). Nachfolgend historische Stände.

**14.09.2026, Version 0.5.0 – vorhandene Daten erschlossen:** Testrelease access04 aktiv. Originalfrage Berlin/Metalle/Schienenversand im Browser korrekt: 277 → 1.531 Tonnen (+452,71 %). Güterprognosen, vollständige gerichtete Prognoseverbindungen, regionale NST20, Hafen- und KV-Details angebunden. 176 lokale Tests, 291.300 Quellenabgleiche, Feldinventar mit Aufbausperre für unbekannte Hauptfelder und Linux-Prüfung aller 1.730 Dateien bestanden. Sieben freigegebene echte Modellfragen; zwei ursprüngliche NST-Fallbacks nach Belegkorrektur anhand gespeicherter Modelltexte erneut geprüft. Keine neue unabhängige Gemini-Prüfung und keine Garantie beliebiger freier Modelltexte. Produktionsportal und Benutzerrechte unverändert; alte Serverreleases erhalten. [Aktueller Prüfbericht und Grenzen](ANALYSEASSISTENT_DATENZUGRIFF_20260914.md). Nachfolgend historische Stände.

**14.09.2026, Version 0.4.2 – Güterzeitreihe und echte Antwortstichprobe:** Originaldialog Leipzig einschließlich Folgefragen und acht dokumentierte Fragetypen frei über Requesty-EU geprüft; Antworten tatsächlich gelesen und gegen Verständnis, Zuordnung, Zahlen, Verständlichkeit und Vollständigkeit bewertet. Drei lesende Gemini-Prüfungen; 147 lokale Tests bestanden. Testrelease goods03 aktiv; Linuxprüfung aller 1.710 Dateien und angemeldete Browserabnahme bestanden. Prognose-Crosswalks ergänzt; nationale und regionale Prognoseansicht lädt wieder. Leipzig 2020–2024 vollständig mit drei Verkehrsträgern, Datenlücke und Tabellenhinweis; im Browser vollständige geprüfte Ersatzantwort. [Aktueller Prüfbericht](ANALYSEASSISTENT_GÜTER_UND_STICHPROBE_20260914.md). Keine pauschale 45-Fälle-Abnahme, Produktion unverändert.

**14.09.2026, Version 0.4.1:** Der gemeldete Prognosedialog Magdeburg/Duisburg wird über einen gemeinsamen Mehrregionen- und Mehrkennzahlenvergleich ohne Pflicht-Istjahre ausgeführt. Zwei lesende Gemini-Prüfungen, 129 lokale Tests, abschließende Linuxprüfung und der angemeldete Originaldialog sind dokumentiert; Testrelease forecast01 aktiv. Maßgeblicher Abschluss: [Prognose-Prüfbericht](ANALYSEASSISTENT_PROGNOSE_20260914.md). Keine Produktionsfreigabe und keine vollständige erneute 45-Fälle-Abnahme.

**Neuester Nachtrag 14.09.2026 – semantische Auswahl:** Version 0.4.0 ist als `portal-test-20260914-gueterstroeme-semantic01` auf Testsite 1067000 aktiv. Die KI ordnet freie Formulierungen mit Orts-/Datenkatalog zu; der native Datenzugriff prüft strukturierte Auswahl ohne zweite sprachliche Musterprüfung. Teilkontext bleibt bei Rückfragen gespeichert, Kalenderjahre und verfügbare Jahre werden getrennt aufgelöst. Ladekreis entfernt, Fortschritt im Antwortbereich. 119 Offline-Tests und die Linux-Prüfung aller 1.708 Dateien einschließlich des gemeldeten semantischen Dialogs bestanden. Zwei lesende Gemini-Prüfungen wurden selbst bewertet und bestätigte Fehler nachgebessert. [Prüfbericht und aktuelle Liveabnahme](ANALYSEASSISTENT_SEMANTIK_20260914.md). Keine Produktionsbereitstellung und keine pauschale fachliche Gesamtabnahme beliebiger Fragen.

**Aktueller Nachtrag 14.09.2026 – natürlicher Chat:** Version 0.3.0 ist als `portal-test-20260914-gueterstroeme-chat01` auf Testsite 1067000 aktiv. Native Datenwerkzeuge, signierter Gesprächsverlauf, freie beleggeprüfte Absätze und Fortschrittsausgabe sind umgesetzt. 107 Offline-Tests und die Linux-Prüfung aller 1.707 Release-Dateien bestanden. Echte Modellstichproben und vier angemeldete Browsereingaben bestätigen Jahresrückfrage, neuestes Schienenjahr 2025, Gegenrichtung und die Grenze für 2026. Zwei numerische Antworten wurden korrekt gebucht; Rückfrage und Datenlücke nicht. Die Gegenrichtung nutzte im Browser die feste geprüfte Rückfallantwort. Kein Nachweis vollständig fehlerfreier freier Modelltexte und keine fachliche Gesamtabnahme des 45-Fälle-Katalogs. Produktion unverändert. [Vollständiger Abschlussnachweis](ANALYSEASSISTENT_CHAT_20260914.md). Die folgenden datierten Abschnitte dokumentieren Vorgängerstände.

**Nachtrag 11.09.2026 – Mehrjahresauswertung und rechnerische Veränderung:** `portal-test-20260911-gueterstroeme-beta04` ist auf Testsite 1067000 aktiv. 83 lokale Prüfungen und die Linux-Prüfung aller 1.706 Serverdateien bestehen. Der Rosenheim–Augsburg-Fall wird ohne Einzeljahres-Rückfrage für 2020–2024 ausgewertet: Schiene 2.175 zu 1.066 Tonnen, rechnerischer Rückgang 50,99 %. Fehlende Straßen- und Binnenschiffswerte werden als in der zugrunde liegenden Statistik nicht nutzbar erfasst beziehungsweise veröffentlicht bezeichnet, nicht als tatsächlich ausgebliebener Verkehr. Beta04 enthält weiterhin die korrigierte Trennung von Güterarten und NST-Einzelpositionen aus Beta03. Manifest `4d2cc83bb1e65b491486cdff58f887186e49e570e4387f86377e266276f5f6d6`; API und Datenbank gesund. Kein neuer Modellaufruf, keine Kundenbuchung und keine Produktionsänderung. [Vollständiger begrenzter Nachweis](ANALYSEASSISTENT_BETA_20260911.md). Keine fachliche Gesamtabnahme beliebiger Fragen.

**Stand:** 14.09.2026

Ergänzungen zum Analyseassistenten vom 09.–11.09.2026 stehen am Dokumentende. Das eigene Testkonto ist freigeschaltet; der Beta03-Browser-/Kontingenttest und die Beta04-Linux-Prüfung bestehen. Version 0.2.1 mit Mehrjahresrelation, analytischen Kernaussagen und rechnerischen Veränderungen ist bereitgestellt. Für B01–B06 ist der letzte Nachprüfungsabschnitt maßgeblich; frühere Paketabschnitte dokumentieren die jeweiligen Vorgängerstände.

**Status:** Automatisierte, browserseitige und manuelle Korrekturregression sowie unabhängige externe Zweitprüfung mit anschließender Nachprüfung bestanden

**Zweck:** Dieser Plan dient zugleich als Arbeitsplan der aktuellen Gesamtprüfung und als verbindliche Vorlage für spätere Datenaktualisierungen.

## 1. Prüfziel und Freigabegrenze

Vor einer Weitergabe an Kunden muss nachvollziehbar belegt sein, dass:

1. die vorgesehenen amtlichen Rohdaten vollständig und mit der richtigen fachlichen Abgrenzung eingelesen werden,
2. räumliche, zeitliche und gütersystematische Zuordnungen stimmen,
3. Transformationen, Aggregationen, Anteile, Salden und Veränderungsraten rechnerisch korrekt sind,
4. Filter und Darstellungsoptionen im Dashboard genau die dafür vorgesehenen Daten verwenden,
5. Randsummen und Komponenten innerhalb der fachlich zulässigen Grenzen übereinstimmen,
6. ausgewählte Ergebnisse durch unabhängige amtliche Veröffentlichungen plausibilisiert werden können und
7. bekannte methodische Grenzen sichtbar dokumentiert sind und
8. die fachlich geprüften Werte bei identischen Einstellungen tatsächlich im Browser angezeigt werden.

Die Prüfung ist bis zur gemeinsamen Sichtung der Befunde **ausschließlich lesend**. Festgestellte Fehler werden gesammelt und zunächst im Chat vorgelegt. Daten, Skripte und Anwendung werden erst nach ausdrücklicher Freigabe korrigiert.

## 2. Geltungsbereich

Geprüft werden die sieben veröffentlichten Analysemodule:

1. Übersicht
2. Straßengüterverkehr
3. Schienengüterverkehr
4. Binnenschifffahrt
5. Seeverkehr und Häfen
6. Intermodaler Verkehr und Kombinierter Verkehr
7. Verkehrsprognose 2040

Die Mautdaten-Relationen sind derzeit kein veröffentlichtes Analysemodul und werden deshalb nur auf korrekte Abgrenzung vom Produktivumfang geprüft, nicht in die fachlichen Ergebnisstichproben aufgenommen.

## 3. Prüfebenen

### 3.1 Quellen- und Schemaprüfung

Je Datenquelle werden mindestens folgende sechs Punkte geprüft:

- Dateibestand und erwartete Berichtsjahre
- Zeichencodierung, Trennzeichen und Spaltennamen
- fachlicher Datensatzumfang und Erhebungsgrenze
- räumliche Ebene und verwendeter Gebietsstand
- Kennzahl, Einheit und Skalierung
- Schlüssel, Duplikate, fehlende Werte und zulässige Merkmalsausprägungen

**Planumfang:** 7 Module × 6 Prüfungen = **42 Strukturprüfungen**.

### 3.2 Prüfung der Verarbeitung und Formeln

Für jede Pipeline wird der Weg von der Rohdatei bis zum im Browser gelesenen JSON- oder Parquet-Datensatz nachvollzogen. Zu prüfen sind insbesondere:

- Filterbedingungen und Ausschlüsse
- Umstiegsschlüssel für Räume und Gütergruppen
- Aggregationsniveau vor und nach Verknüpfungen
- Versand, Empfang, Binnenverkehr und Saldo
- Gesamtwert = fachlich zulässige Summe der Komponenten
- Anteil = Teilmenge / passende Grundgesamtheit
- Veränderung = `(neuer Wert − Basiswert) / |Basiswert| × 100`
- Umgang mit Nullwerten und fehlenden Basiswerten
- Umrechnung von Tonnen in Mio. t sowie Tonnenkilometern in Mio. oder Mrd. tkm
- Rundung erst in der Ausgabe, nicht vor der Aggregation

### 3.3 Rohdaten-gegen-Dashboard-Stichproben

Je Modul werden mindestens zwölf unterschiedliche Filter- und Darstellungskombinationen unabhängig aus den Rohdaten rekonstruiert. Ein Prüffall kann mehrere Einzelwerte enthalten, zählt aber nur dann als bestanden, wenn alle zugehörigen Werte, Einheiten und Beschriftungen stimmen.

| Modul | Mindestzahl | Schwerpunkte |
|---|---:|---|
| Übersicht | 12 | Deutschland/Region, Tonnen/tkm, Verkehrsträger, Richtung, Modal Split, Güterstruktur |
| Straße | 12 | Versand/Empfang/Binnen, NUTS-3/NUTS-2-Abgrenzung, sieben/20 Gütergruppen, Relation |
| Schiene | 12 | Region, Richtung, Tonnen/tkm, Gütergruppe, Relation, Ladeeinheit |
| Binnenschifffahrt | 12 | Hafen/Region, Richtung, Tonnen/tkm, Gütergruppe, Relation, Container |
| Seeverkehr | 12 | deutscher Hafen, Partnerland, Empfang/Versand/Saldo, Gütergruppe, TEU |
| Intermodal/KV | 12 | Schiene/Binnenschiff getrennt, Tonnen/tkm, Jahr, Ladeeinheit/Containergröße, Inlandrelation |
| Verkehrsprognose 2040 | 12 | 2019/2040, Region/Deutschland, Verkehrsträger, Richtung, Gütergruppe, Relation, Wachstum |
| **Summe** | **84** | |

Die automatisierten Stichproben verwenden mindestens Deutschland und mehrere unterschiedlich geprägte Regionen beziehungsweise Städte. Die zehn manuellen Stichproben aus Abschnitt 8 werden von den automatisierten Agents nicht vorweggenommen.

### 3.4 Browser-Sichtprüfung

Für jeden der 84 Rohdaten-Prüffälle wird – soweit die Kombination in der Benutzeroberfläche auswählbar ist – zusätzlich im Browser kontrolliert:

- aktives Analysemodul,
- ausgewähltes Jahr und Kennzahl,
- Raumbezug beziehungsweise ausgewählte Region oder Hafen,
- Verkehrsrichtung,
- Verkehrsträger und Gütergruppe,
- sichtbarer Wert einschließlich Einheit und Rundung,
- Übereinstimmung von Kennzahlenkarte, Karte, Diagramm, Tabelle und Tooltip, sofern mehrere Darstellungen denselben Sachverhalt zeigen,
- nachvollziehbare Leer- oder Hinweiszustände bei fachlich nicht anwendbaren Filtern.

Mindestens drei Fälle je Modul werden als vollständige Browser-Prüfung mit den konkreten Einstellungen und dem abgelesenen Wert protokolliert. Damit entstehen mindestens **21 dokumentierte Browser-Prüffälle**; weitere Browserkontrollen können mit den Rohdatenprüfungen verbunden werden.

### 3.5 Randsummen- und Konsistenzprüfungen

Pro Modul werden mindestens vier Randsummen oder Identitäten geprüft:

1. Komponenten gegen Gesamtwert,
2. Versand/Empfang/Binnen beziehungsweise deren fachlich korrekte Beziehung,
3. Gütergruppen oder Verkehrsträger gegen die passende Grundgesamtheit,
4. Anteile, Salden oder Zeitveränderungen durch unabhängige Neuberechnung.

**Planumfang:** 7 Module × 4 Prüfungen = **28 Randsummenprüfungen**.

Nicht addierbare Reihen werden ausdrücklich nicht summiert. Dies gilt insbesondere für die getrennten KV-Teilmärkte Schiene und Binnenschifffahrt, da dieselbe Transportkette in beiden Statistiken vorkommen kann.

### 3.6 Externer Quellenabgleich

Mindestens zehn Dashboardwerte werden mit Veröffentlichungen der jeweils zuständigen amtlichen oder fachlich verantwortlichen Stelle verglichen:

- mindestens vier Deutschlandwerte,
- mindestens sechs Werte für ausgewählte Städte, Regionen oder Häfen,
- nach Möglichkeit unterschiedliche Verkehrsträger und Jahre.

Jeder Vergleich dokumentiert Quelle, Veröffentlichungsdatum, Bezugsjahr, Einheit, räumliche und fachliche Abgrenzung sowie mögliche Rundungs- oder Revisionsunterschiede. Ein externer Wert gilt nur dann als echte Bestätigung, wenn Definition und Grundgesamtheit übereinstimmen. Reine Größenordnungsplausibilität wird gesondert gekennzeichnet.

### 3.7 Unabhängige Zweitprüfung

Gemini erhält ausschließlich lesenden Zugriff auf den freigegebenen Projektordner. Die Zweitprüfung darf keine Dateien verändern, keine Befehle ausführen und keine externen Werkzeuge verwenden. Gemini prüft den Datenfluss, Formeln, Abgrenzungen, vorhandene Prüflücken und die konsolidierten Befunde. Jeder konkrete Gemini-Hinweis wird anschließend unabhängig nachgeprüft; ungeprüfte Hinweise werden nicht als Fehler übernommen.

## 4. Geplanter Mindestumfang

| Prüfblock | Zahl |
|---|---:|
| Strukturprüfungen | 42 |
| Rohdaten-gegen-Dashboard-Prüffälle | 84 |
| dokumentierte Browser-Sichtprüfungen | 21 |
| Randsummenprüfungen | 28 |
| externe Referenzvergleiche | 10 |
| manuelle Nutzerstichproben | 10 |
| **Gesamt** | **195** |

Die Gemini-Zweitprüfung ist eine zusätzliche unabhängige Prüfinstanz und wird nicht auf diese 195 Primärprüfungen angerechnet. Neben der Zahl der Prüffälle wird am Ende auch die größere Zahl der tatsächlich verglichenen Einzelwerte ausgewiesen. Wenn eine Browser-Sichtprüfung zugleich einen Rohdaten-Prüffall abschließt, bleiben beide Prüfebenen im Protokoll getrennt erkennbar.

## 5. Auswahl der Stichproben

Die Stichproben werden geschichtet ausgewählt, damit nicht nur große und leicht prüfbare Werte vorkommen:

- Deutschland und mindestens drei unterschiedliche Regionen oder Städte,
- hoher, mittlerer und niedriger Güterverkehrsumfang,
- Binnen-, Versand-, Empfangs- und Saldoansichten,
- Tonnen und Tonnenkilometer,
- mindestens zwei Berichtsjahre je Zeitreihenmodul,
- häufige und seltenere Gütergruppen,
- große und kleine Relationen,
- positive, negative und – sofern vorhanden – nicht berechenbare Veränderungsraten,
- nationale, regionale, Hafen- und Partnerbezüge.

Die Zufallsauswahl wird reproduzierbar mit einem dokumentierten Startwert erzeugt. Ungeeignete Zufallstreffer, etwa nicht vorhandene Kombinationen, dürfen nur mit Begründung neu gezogen werden.

## 6. Toleranzen und Bewertung

Grundsätzlich werden Roh- und Zwischenwerte vor der Anzeige-Rundung verglichen.

| Fall | Toleranz |
|---|---|
| ganzzahlige Zählwerte und Schlüssel | exakt |
| intern gespeicherte Tonnen/tkm | höchstens die dokumentierte ETL-Rundung |
| angezeigte Werte | höchstens eine halbe Einheit der sichtbaren letzten Nachkommastelle |
| Anteile und Wachstumsraten | höchstens 0,1 Prozentpunkte, sofern nur auf eine Nachkommastelle gerundet wird |
| externe Veröffentlichungen | nur nach Definition; Rundungs- und Revisionsdifferenzen werden einzeln erklärt |

Bewertung der Befunde:

- **Kritisch:** zentrale Kennzahlen, Grundgesamtheiten oder Kernfilter sind falsch; eine Kundennutzung ist nicht vertretbar.
- **Hoch:** wesentliche Teilbereiche oder häufig genutzte Auswertungen sind materiell verfälscht.
- **Mittel:** lokalisierter Fehler oder unklare Methodik mit erkennbarer Auswirkung.
- **Niedrig:** Beschriftungs-, Rundungs- oder Dokumentationsproblem ohne wesentliche Ergebnisverzerrung.

Zusätzlich wird die Sicherheit jedes Befunds als hoch, mittel oder niedrig angegeben.

## 7. Protokollierung je Prüffall

Jeder Prüffall erhält mindestens:

- eindeutige Prüf-ID,
- Modul und Prüfer,
- Rohdatenquelle und betroffene Datei,
- Filter: Jahr, Kennzahl, Raum, Richtung, Verkehrsträger und Gütergruppe,
- eigenständiger Rechenweg,
- erwarteter Rohdatenwert,
- Wert im verarbeiteten Datensatz,
- sichtbarer Dashboardwert und Einheit,
- Differenz und Toleranz,
- Ergebnis: bestanden, Hinweis, Fehler oder nicht prüfbar,
- Belegpfade und gegebenenfalls externe Quelle.

## 8. Zehn manuelle Stichproben durch den Nutzer

Diese zehn Fälle werden nach Abschluss der automatisierten Stichproben zufällig aus noch nicht geprüften, gültigen Kombinationen gezogen und in einer gesonderten Excel-Prüftabelle bereitgestellt. Für jeden Fall werden konkrete Klick-/Filterangaben, die zu öffnende Rohdatei, die benötigten Zeilen beziehungsweise Filter, der aus den Rohdaten ermittelte Vergleichswert und ein Rechenblatt-Schema angegeben. Der Nutzer trägt den im Dashboard abgelesenen Wert und seinen Prüfstatus selbst ein.

Vorgesehene Streuung:

1. zwei regionale Straßenrelationen,
2. zwei Schienenrelationen,
3. zwei Binnenschiffsrelationen,
4. zwei Seehafenfälle mit Partnerland und Richtung,
5. eine getrennte KV-Teilmarktkennzahl,
6. eine VP2040-Verbindung mit Basis- und Prognosewert.

**Zufallsstartwert der Erstprüfung:** `20260824`.  
**Konkrete Fälle und Rohwerte:** `outputs/01a0346f-9c94-7c73-9e36-4338961574a1/Manuelle_Prüffälle_Güterströme.xlsx`. Die Datei enthält Anleitung, zehn Prüffälle mit Sollwert und Eingabefeldern sowie die Rohdatenbelege. Die Kombinationen wurden mit dem dokumentierten Zufallsstartwert gezogen und nicht als automatisierte Einzelfälle vorweggenommen.

## 9. Wiederholung bei zukünftigen Datenständen

Bei jeder Datenaktualisierung sind mindestens folgende Schritte verpflichtend:

1. bisherigen Datenstand und erzeugte Dateien sichern,
2. Schema- und Jahresvergleich vor der Verarbeitung,
3. nur die betroffene Pipeline ausführen,
4. alle stabilen Struktur- und Randsummentests wiederholen,
5. mindestens zwölf Rohdatenstichproben je betroffenem Modul neu ziehen,
6. mindestens drei bisherige Referenzfälle als Regressionstest wiederholen,
7. mindestens zwei neue manuelle Fälle auswählen und die zehn Referenzfälle rotierend fortführen,
8. Browserdarstellung für mindestens drei Fälle je betroffenem Modul sowie alle geänderten Filter und Einheiten prüfen,
9. Abweichungen dokumentieren und fachlich freigeben,
10. erst danach den neuen Datenstand übernehmen.

## 10. Ergebnisstatus der Erstprüfung

Die Erstprüfung wurde mit drei parallelen fachlichen Prüfsträngen, einer zusätzlichen Quellenprüfung und einer eigenständigen Browserkontrolle durchgeführt. Die Mindestzahl von 84 Rohdatenfällen wurde überschritten. In den maschinellen Vergleichen wurden mindestens 4.752 Einzelwerte kontrolliert; allein für die Prognose kamen zusätzlich 3.904 Tooltip-gegen-Datenpaket-Vergleiche hinzu. Wo ein Prüffall mehrere Werte umfasst, wird deshalb neben der Fallzahl auch die Zahl der Einzelvergleiche ausgewiesen.

| Prüfblock | Geplant | Ausgeführt | Ergebnis |
|---|---:|---:|---|
| Struktur | 42 | 42 | abgeschlossen; mehrere relevante Schema- und Zuordnungsbefunde |
| Rohdaten gegen Dashboard | 84 Fälle | mindestens 4.752 Einzelwerte | Mindestumfang deutlich überschritten; überwiegend korrekt, aber materielle Teilfehler |
| Browser-Sichtprüfung | 21 | 24 Filterzustände | 16 ohne Auffälligkeit; 8 bestätigten oder konkretisierten Fehler |
| Randsummen | 28 | mehr als 28 | regionale Grundidentitäten überwiegend exakt; nationale Abgrenzungen teilweise unvollständig |
| externe Referenzen | 10 | 12 | vier exakte Bestätigungen, eine Größenordnungsplausibilität, sieben materielle Abweichungen im Seeverkehr |
| manuelle Nutzerstichproben | 10 | 10 durch den Nutzer ausgeführt | nach der Korrektur mit denselben Referenzfällen erneut auszuführen |
| Gemini-Zweitprüfung | zusätzlich | abgeschlossen | Projektzugriff interaktiv bestätigt; unabhängige Prüfung im Plan-/Sandboxmodus ohne zusätzliche Befunde und ohne Dateiänderungen |

### 10.1 Konsolidierte Befundliste vor jeder Korrektur

| ID | Priorität | Modul | Befund und nachgeprüfter Beleg |
|---|---|---|---|
| QS-01 | **Kritisch** | Seeverkehr | Der CSV-Import mit Fehlertoleranz verwirft 42.071 von 420.173 Datensätzen (10,01 %), weil korrekt zitierte Bezeichnungen Semikolons enthalten. Die fachlich vollständige Rohsumme 2025 beträgt 279,595 Mio. t; im erzeugten Datenpaket verbleiben 256,327 Mio. t (−23,269 Mio. t bzw. −8,32 %). |
| QS-02 | **Hoch** | Seeverkehr | NST-Schlüssel verlieren beim Einlesen führende Nullen. Beispielsweise wird `011` als `11` interpretiert. Dadurch ist die Güterstruktur erheblich falsch zugeordnet. |
| QS-03 | **Hoch** | Seeverkehr | Richtungsbezogene TEU werden nur innerhalb der Bedingung „Gütergewicht > 0“ summiert. Leere Container fehlen deshalb: Deutschland 2025 Empfang 8,478 Mio. TEU roh gegenüber 6,257 Mio. im Dashboard; Versand 8,758 gegenüber 5,777 Mio. TEU. |
| QS-04 | **Hoch** | Verkehrsprognose 2040 | Der Richtungsfilter ändert bei Deutschland Beschriftungen, aber nicht Kennzahlen, Modal Split oder Güterstruktur. Browserbeleg: 2040 Gesamt und Versand zeigen jeweils 5.110,74 Mio. t. |
| QS-05 | **zurückgezogen** | Verkehrsprognose 2040 | Die erneute fachliche Prüfung bestätigt die vom Nutzer beschriebene Soll-Logik: „Binnenverkehr ausblenden“ ist ein reiner Darstellungsfilter für Selbstrelationen in Linien und Tabellen. Von KPI, Flächenwerten und Randsummen darf nichts abgezogen werden. |
| QS-06 | **Hoch** | Übersicht | Die Deutschland-Verkehrsleistung der Schiene und Binnenschifffahrt verwendet nur Datensätze mit vollständigem NUTS-3-Ursprungs- und Zielschlüssel. Dadurch zeigt die Übersicht 2024 nur 88,08 Mrd. Schienen-tkm und 22,23 Mrd. Binnenschiffs-tkm; die vollständigen amtlichen Reihen betragen 126,320 beziehungsweise 43,443 Mrd. tkm. |
| QS-07 | **Hoch** | Schiene/Binnenschiff | Für die Relationstabellen wird eine ältere beziehungsweise reihenfolgeabhängige NST-7-Zuordnung verwendet. Daher können Karte/Kennzahl und Relationstabelle unter demselben Güterfilter unterschiedliche Gruppen abbilden. Die manuellen Fälle H-03, H-05 und H-06 machen dies direkt prüfbar. |
| QS-08 | **Mittel** | Binnenschifffahrt | Der nationale Wert 2025 ist wegen der NUTS-3-Vollständigkeitsbedingung um 343.292 t beziehungsweise 0,20 % niedriger als die vollständige Rohsumme. |
| QS-09 | **zurückgezogen** | Binnenschifffahrt | Dass der Darstellungsfilter nur Selbstrelationen ausblendet, ist beabsichtigt. Die regionale Kennzahl bleibt unverändert. Empfang und Versand sind getrennte regionale Bezüge; ihre gemeinsame Darstellung als Aufkommen ist in der Methodik kenntlich zu machen, aber kein durch den Schalter verursachter Rechenfehler. |
| QS-10 | **methodisch präzisiert** | Intermodal/KV | Die Karte darf Schiene und Binnenschiff als räumliches Intensitätsmaß addieren, sofern sie ausdrücklich als „Summe erfasster KV-Teilmärkte“ bezeichnet wird und keine eindeutige Sendungs- oder nationale KV-Gesamtmenge behauptet. Kennzahlen und Anteilsberechnungen bleiben getrennt. |
| QS-11 | **Mittel** | Übersicht/Regionen | 22 der 434 als Region geführten Schlüssel sind keine fünfstelligen NUTS-3-Codes. Ursache ist eine zu breite Auswahl nach dem Muster `DE%`; Sonder- und Sammelzellen müssen getrennt gekennzeichnet werden. |
| QS-12 | **Mittel** | Verkehrsprognose 2040 | Im Saldo-Tooltip wird auf nicht definierte Modalvariablen verwiesen; beim Überfahren ist deshalb ein JavaScript-Fehler zu erwarten. |
| QS-13 | **Mittel** | Verkehrsprognose 2040 | Das KV-Containerdiagramm reagiert nicht auf Richtung und Gütergruppe und bleibt mengenbezogen, obwohl andere Filter beziehungsweise Kennzahlen gewählt sind. |
| QS-14 | **Hoch** | Verkehrsprognose 2040 | Die nationale Matrix enthält die Sonderzellen vollständig; es geht national keine Menge verloren. In den sechs Landmatrizen werden 40 deutsche Flughafen-/Seehafen-Sonderzellen verwendet. Die bisherige regionale Zuordnung war jedoch unvollständig und teils falsch (unter anderem Papenburg und Emden). Erforderlich ist eine eindeutige Zuordnung jeder verwendeten deutschen Sonderzelle zu genau einem Standortkreis vor der regionalen Aggregation. |
| QS-15 | **Mittel** | Straße/Übersicht | Der nationale Straßenwert stammt aus VE7, regionale Summen aus VE12/13. Für 2024 liegt die halbierte Regionalsumme mit 2.973,169 Mio. t rund 10,7 % unter dem nationalen VE7-Wert 3.327,945 Mio. t. Diese verschiedenen Erhebungsumfänge dürfen nicht als identische Randsumme behandelt werden und benötigen eine sichtbare Erläuterung. |
| QS-16 | **Hoch** | VP2040/Gütersystematik | Der frühere VP2040-Crosswalk ordnete die 25 VP-Positionen wirtschaftslogisch neu, statt sie über die NST-2007-Abteilung auf die amtlichen C1–C7-Gruppen abzubilden. Dadurch konnten Kohle, Erze und Steine/Erden in abweichenden Gruppen erscheinen. Die bisherigen Summenprüfungen erkannten dies nicht zuverlässig, weil Berechnung und Prüfung dieselbe fehlerhafte Zuordnung verwendeten. |

### 10.2 Bestandene Kernprüfungen

- Für 4.136 Region-Jahr-Kombinationen stimmen die internen Grundidentitäten der Übersicht exakt: Gesamt = Verkehrsträgersumme, Verkehrsträger = Versand + Empfang und Gütergruppensumme = Gesamt.
- Die vollständigen amtlichen Deutschlandwerte 2024 im Intermodal-Modul stimmen für Schiene und Binnenschiff sowohl bei Tonnen als auch bei Tonnenkilometern mit Destatis überein.
- Die sechs VP2040-Matrizen enthalten keine negativen oder fehlenden Mengen; Summen, Wachstumsraten und der verwendete Crosswalk stimmen in den maschinellen Prüfungen mit dem erzeugten Datenpaket überein.
- Die KV-Teilmarktwerte, Strukturen und Anteile stimmen innerhalb ihrer getrennten Grundgesamtheiten rechnerisch mit den Rohdaten überein.
- Die Stichproben der Straßenrelationen und mehrere Schienen-, Binnenschiffs-, Seehafen- und Prognoserelationen stimmen außerhalb der oben genannten Fehlerbilder.

### 10.3 Externe Referenzen der Erstprüfung

- Destatis, Seeverkehr 2025: <https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/03/PD26_077_463.html>
- GENESIS, Statistik 46331 Seeverkehr: <https://genesis.destatis.de/datenbank/online/statistic/46331/details>
- Destatis, Eisenbahn-Grundzahlen: <https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Transport-Verkehr/Gueterverkehr/Tabellen/eisenbahn-grundzahlen.html>
- Destatis, Hauptverkehrsrelationen nach Verkehrsträger: <https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Transport-Verkehr/Gueterverkehr/Tabellen/verkehrstraeger-hauptverkehrs-relation-b.html>
- Destatis, Güterbeförderung im Ländervergleich: <https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Transport-Verkehr/Gueterverkehr/Tabellen/gueterbefoerderung-lr.html>

### 10.4 Freigabestatus

Eine Freigabeempfehlung wird nicht ausgesprochen. Vor einer Kundenvorführung sollten mindestens QS-01 bis QS-07 korrigiert und danach vollständig regressionsgeprüft werden. Anschließend sind die zehn manuellen Stichproben auszuwerten. Die mittleren Befunde sollten entweder behoben oder in Oberfläche und Methodik so klar erläutert werden, dass keine falsche Interpretation naheliegt.

Der Stand dieser Aussage ist die Erstprüfung vor der Korrektur. Die Freigabebewertung wird erst nach Abschluss der in Abschnitt 10.6 beschriebenen Regressionsprüfung aktualisiert.

### 10.5 Verbindliche methodische Hinweise in der Oberfläche

Jedes Informationsfenster einer Relationstabelle muss modulbezogen mindestens die folgenden Punkte benennen:

- fachliche Grundgesamtheit der Relationstabelle und der zugehörigen Kennzahlen,
- Gründe, warum die Summe sichtbarer Relationen von einer regionalen oder nationalen Randsumme abweichen kann,
- räumliche Auflösung und nicht oder nur gröber zuordenbare Datensätze,
- Wirkung der Top-X-Auswahl,
- ausschließliche Darstellungswirkung von „Binnenverkehr ausblenden“,
- bei der Verkehrsprognose: Einbezug der Sonderzellen in die nationale Matrix und genau einmalige Zuordnung deutscher Hafen- und Flughafenzellen zum Standortkreis,
- beim Intermodalmodul: getrennte Kennzahlen und Anteile für die Teilmärkte Schiene und Binnenschiff sowie die eindeutige Kennzeichnung der gemeinsamen Karte als Summe erfasster Teilmarktvolumina ohne Anspruch auf überschneidungsfreie Sendungen.

Diese Hinweise sind nach jeder Datenaktualisierung in mindestens einem Browserfall je Modul zusammen mit den dazugehörigen Kennzahlen und Relationstabellen zu prüfen.

### 10.6 Korrekturstand und verpflichtende Regression

Nach der kritischen Neubewertung gelten folgende Festlegungen und Korrekturen:

- QS-05 und QS-09 sind keine Fehler. Der Binnenverkehrsschalter ist ausschließlich ein Darstellungsfilter für Selbstrelationen in Verbindungslinien und Relationstabellen.
- QS-01 bis QS-03: Der Seeverkehr wird mit expliziter CSV-Zitierlogik und als Text eingelesenen Schlüsseln verarbeitet. Innerdeutsche Seeverkehre werden am deutschen Ladehafen als Versand und am deutschen Löschhafen als Empfang gezählt. Die automatisierte Prüfung `scripts/validation/validate_maritime_bundle.py` muss für alle Berichtsjahre bestehen.
- Ergänzend muss `scripts/validation/validate_maritime_port_profiles.py` alle veröffentlichten Seeverkehrs-Hafenprofile gegen die MRTM-Rohdaten prüfen: Tonnen, Empfang, Versand, TEU, NST-7-/NST-20-Struktur und internationale Partnerrelationen. Fehlende Richtungsfelder in Hafen-, Gütergruppen- oder NST-Objekten lassen den Test fehlschlagen; eine 58/42-Schätzung darf im veröffentlichten Datenpaket nicht erforderlich sein.
- QS-04: Die Richtungsauswahl bleibt auch in der nationalen VP2040-Ansicht aktiv. Bei „Gesamt“ werden die vollständigen nationalen Matrizen einschließlich Transit und Sonderzellen verwendet. Bei Versand, Empfang und Saldo werden Karte und KPI aus den räumlich zuordenbaren NUTS-3-Werten gebildet; Transit und nicht regional zuordenbare Sonderzellen sind in diesem Richtungsumfang ausdrücklich ausgeschlossen.
- QS-06 und QS-08: Nationale Tonnen- und Tonnenkilometerwerte werden aus der vollständigen nationalen Rohgrundgesamtheit berechnet, nicht aus der Summe vollständig NUTS-zuordenbarer Relationen.
- QS-07: Die NST-2007-Zuordnung der Relationstabellen entspricht derselben sieben Hauptgruppen umfassenden Zuordnung wie Karten und Diagramme. Bei den dreistelligen Schlüsseln handelt es sich nicht um eine alte NST-Systematik, sondern um die feinere NST-2007-Untergliederung; führende Nullen sind Bestandteil des Schlüssels.
- Feinpositions-Regression: `scripts/validation/validate_nst_fine_codes.py` muss alle tatsächlich vorkommenden NST-2007-Feinpositionen von Schiene und Binnenschiff einer Abteilung 01–20 zuordnen und deren C1–C7-Summen unabhängig gegen `fact_od_flows.parquet` nachrechnen. Unbekannte Formate, fehlende Abteilungen, abweichende Summen oder abweichende sichtbare NST-20-/C1–C7-Bezeichnungen verhindern die Freigabe.
- VP2040-Güterschlüssel: `scripts/validation/validate_vp2040_bundle.py` prüft beide gelieferten Dateien `nst2007.csv`, die Begriffe der VP-Positionen gegen `nsz-2007.pdf` sowie den Crosswalk. Erwartet werden genau 25 Originalcodes und die amtliche C1–C7-Gliederung des KBA-Produkts VE13: C1 = Abteilungen 01–03, C2 = 04–06, C3 = 07–09, C4 = 10, C5 = 11–13, C6 = 14, C7 = 15–20. Die VP2040-Zellen-Exceldateien sind keine Quelle für Güterschlüssel.
- Crosswalk-Vertrag: Die CSV- und JSON-Fassung müssen jeweils genau 25 eindeutige VP-Codes enthalten und in allen fachlichen Feldern identisch sein: Code, VP-Begriff, NST-Abteilung mit Bezeichnung sowie C-Gruppe mit Bezeichnung. Der Validator prüft diese Gleichheit unabhängig von der Verarbeitung und prüft zusätzlich die C-Gruppe aus der NST-Abteilung. Abweichungen, doppelte Codes oder abweichende Gruppenbezeichnungen verhindern die Freigabe.
- Ranglisten-Regression: `scripts/validation/validate_relation_coverage.py` muss für jede veröffentlichte NST-7-Relation von Schiene und Binnenschiff die Top-25-Kandidaten nach Tonnen **und** Tonnenkilometern abdecken. Der Test prüft außerdem, dass vorhandene Vorjahreswerte für alle aktuell sichtbaren Gütergruppenrelationen bereitstehen; eine erst im aktuellen Jahr sichtbare Relation darf daher nicht fälschlich `--` erhalten.
- Auslandsrelationen: Für regionale Relationstabellen werden alle Datensätze mit deutscher Quelle oder deutschem Ziel veröffentlicht; nur reiner Auslandstransit bleibt ausgeschlossen. `scripts/validation/validate_relation_coverage.py` prüft diese Regel auch für das Intermodalmodul und enthält Nürnberg (DE254), Binnenschiff, Versand, NST-4, 2025 mit Antwerpen (BE211) und Groot-Rijnmond/Rotterdam (NL366) als festen Regressionsfall. Partner ohne belastbare Koordinate bleiben als Ranglisteneintrag sichtbar und werden in der Oberfläche mit **„ohne Kartenpunkt“** gekennzeichnet.
- QS-10: Die Intermodalkarte zeigt ohne Teilmarkt-Umschalter die Summe der erfassten KV-Teilmärkte als räumliches Intensitätsmaß. Der Tooltip schlüsselt Schiene und Binnenschiff getrennt auf; KPI und Anteile bleiben getrennt. Die Kartensumme wird nicht als eindeutige nationale KV-Gesamtmenge oder Zahl unterschiedlicher Sendungen interpretiert.
- QS-12: Der Saldo-Tooltip verwendet die tatsächlich berechneten Modalwerte und keine undefinierten Variablen.
- QS-14: Alle 40 in den sechs Landmatrizen verwendeten deutschen Flughafen- und Seehafen-Sonderzellen sind in `data/crosswalks/vp2040_special_cells_nuts3.json` genau einem Standortkreis zugeordnet. Die nationale Matrix bleibt unverändert vollständig.
- QS-15: Die abweichenden KBA-Produkte VE7 und VE12/VE13 werden im Informationsfenster ausdrücklich als nicht identische Randsummen erläutert.
- VP2040-Relationen: Aufbau, nachträgliche 2019-Vergleichswerte und Validator verwenden dieselbe versionierte Sonderzellen-Zuordnung. Der Regressionstest umfasst den Fall Hamburg, Empfang, Dithmarschen (DEF05), Gütergruppe 3; abweichende Basiswerte lassen die Freigabe fehlschlagen.
- Übersicht-Hover: Für mindestens eine straßen-dominierte und eine nicht straßen-dominierte Gütergruppe ist im gemeinsamen Basisjahr 2019 zu prüfen, ob amtliche Istreihe und VP2040-Reihe dieselbe fachliche Abgrenzung besitzen. Dieser Test ist **kein Gleichheitstest der Werte**: Die amtliche Istreihe und die VP-Basis können wegen Quelle, Erhebungsumfang und Modellabgrenzung abweichen. Ein Vergleich ist nur bei gleicher Region, Richtung, Kennzahl, Verkehrsträger und C-Gruppe aussagekräftig. Jede verbleibende Abweichung ist mit Quelle, Grundgesamtheit und Einheit im Datenkatalog bzw. der Methodik zu dokumentieren; das Diagramm darf keine Fortschreibung behaupten.
- Ausländische VP2040-Partnerzellen sind in der Relationstabelle mit dem im Crosswalk vorhandenen Namen statt nur mit der numerischen Zell-ID auszuweisen.

Nach jeder Neuerzeugung sind mindestens zu prüfen: nationale Werte 2024 für Schiene und Binnenschiff in Tonnen und Tonnenkilometern, die Seeverkehrsrandsummen und NST-Schlüssel aller Jahre einschließlich `scripts/validation/validate_nst_fine_codes.py`, unveränderte nationale VP2040-Summen, die 25 VP2040-Crosswalk-Positionen gegen beide Referenzquellen, regionale Werte der von Sonderzellen besonders betroffenen Kreise Bremen, Bremerhaven, Emsland und Emden, die Filterkombination Richtung plus Gütergruppe sowie die sichtbaren Methodenhinweise aller sieben Module.

### 10.7 Ergebnis der Korrekturregression vom 24./25.08.2026

- Die Seeverkehrsvalidierung bestand für alle zehn Berichtsjahre 2016 bis 2025: nationale Empfangs-, Versand- und Gesamtrandsummen für Tonnen und TEU stimmen mit der vollständig neu gelesenen Rohgrundgesamtheit; die NST-Schlüssel sind zweistellig auf Abteilungsebene und die sieben Gütergruppen ergeben die Randsumme.
- Ergänzende Hafenprofilprüfung vom 25.08.2026: 189 veröffentlichte Hafenprofile und 6.784 internationale Partnerrelationen stimmen für Tonnen, Empfang, Versand, TEU sowie NST-7-/NST-20-Struktur mit den MRTM-Rohdaten überein. Alle erforderlichen Richtungsfelder liegen vor; die 58/42-Schätzlogik wird im aktuellen Datenpaket nicht benötigt.
- Die VP2040-Validierung bestand für beide Szenarien. Nationale Randsummen: 2019 = 4.356,972 Mio. t und 689,305 Mrd. tkm; 2040 P1 = 5.110,741 Mio. t und 904,539 Mrd. tkm. Zusätzlich wurden DE600, DE300, DE501, DE502, DE949 und DE942 direkt gegen die sechs Rohmatrizen geprüft.
- Die Crosswalk-Regression bestand: CSV und JSON enthalten jeweils dieselben 25 eindeutigen Positionen und dieselben fachlichen Felder. Die Zuordnung wurde gegen beide VP-`nst2007.csv` und die NST-2007-PDF geprüft; C1–C7 folgt ausschließlich der NST-Abteilung.
- Die Browserprüfung bestätigte für Deutschland 2024: 624,92 Mrd. tkm insgesamt, davon 455,16 Mrd. Inlandstonnenkilometer Straße, 126,32 Mrd. tkm Schiene und 43,44 Mrd. tkm Binnenschiff.
- Die Browserprüfung bestätigte für den Seeverkehr 2025: 284,4 Mio. t Hafenumschlag, 15,0 Mio. TEU, 175,9 Mio. t Empfang und 108,5 Mio. t Versand.
- In der nationalen Verkehrsprognose blieb die Richtungsauswahl sichtbar aktiv. Bei „Gesamt“ zeigte sie die vollständige nationale Matrix; bei Versand wechselten Karte und KPI auf den räumlich zuordenbaren Umfang und wiesen den Ausschluss von Transit und nicht regional zuordenbaren Sonderzellen aus. In der regionalen Probe Bremen waren Versand, Gütergruppe 5 und Tonnenkilometer gleichzeitig wirksam; ausländische Partner wurden mit Namen angezeigt, beispielsweise „Wien/Österreich Ost (AT)“ statt nur mit Zell-ID.
- Im Intermodalmodul blieben die KPI beim Umschalten von „Binnenverkehr einbeziehen“ auf „ausblenden“ unverändert. Die erneute Browserprüfung bestätigte die gemeinsame blaue Intensitätskarte ohne Teilmarkt-Umschalter, die getrennten KPI für Schiene und Binnenschiff sowie die übereinstimmende Beschriftung von Karte und Legende als „Summe erfasster KV-Teilmärkte“.
- In der Verkehrsprognose zeigte die Browserprüfung bei ausgewähltem Görlitz sowohl in der Relationstabelle als auch im Routen-Popup „Warschau (PL)“ statt der numerischen Partner-ID. Der Steckbrief enthielt außerdem einen gesonderten Prognoseblock mit den stärksten Beziehungen 2040 und benannten ausländischen Partnern, darunter „Breslau (PL)“.
- Im abschließenden Browserlauf wurden für den aktuellen Build keine JavaScript-Fehler protokolliert.
- Für die Gemini-Zweitprüfung wurde die Projektvertrauensabfrage einmal interaktiv bestätigt. Der eigentliche Lauf erfolgte weiterhin ausschließlich lesend im Plan-/Sandboxmodus; ein Zugriff außerhalb des Projektordners wurde abgelehnt. Gemini fand in den gezielt geprüften Berechnungs-, Anzeige- und Dokumentationsstellen keine zusätzlichen Widersprüche und änderte keine Datei. Die Browser- und Laufzeitprüfung blieb davon getrennt und wurde durch Codex durchgeführt.

Automatisierte und browserseitige Korrekturregression sind damit bestanden. Vor einer externen Kundenvorführung sollten die zehn manuellen Nutzerfälle mit dem korrigierten Datenstand noch einmal wiederholt und in der bestehenden Prüftabelle als bestanden oder abweichend dokumentiert werden.

### 10.8 UI-Nachprüfung und Browserregression vom 25.08.2026

Nach weiteren Korrekturen an Datenverfügbarkeit und Modulzuständen wurde die ausgelieferte Oberfläche erneut geprüft:

- Für 2025 wird in der Übersicht kein vollständiger Modal Split mehr ausgewiesen, solange die Straßengüterverkehrsdaten fehlen. Das Diagramm zeigt stattdessen einen ausdrücklichen Nichtverfügbarkeitshinweis; Schiene und Binnenschiff werden nicht auf 100 Prozent einer unvollständigen Grundgesamtheit normiert.
- Im Straßengüterverkehr ist 2025 deaktiviert. Beim Wechsel aus einer 2025er Ansicht wird konsistent auf 2024 umgestellt; Auswahl, Einstellungsanzeige, Kartenüberschrift und Kartenskala verwenden dasselbe Jahr.
- Nicht anwendbare Einstellungen werden beim Modulwechsel nicht mehr als wirksame Filter dargestellt. Der Seeverkehr zeigt Tonnen und eine modulinterne Hafenauswahl; das Intermodalmodul kennzeichnet den globalen Güterfilter als nicht anwendbar.
- Die modularen Quellen und die ausgelieferten Dateien `index.html`, `js/app.js` und `css/style.css` stimmen nach dem Frontend-Build bytegenau überein. `index.html` und `html/shell-tail.html` verwenden dieselbe Cache-Version `20260825-qa-regression`.
- Alle sieben Module wurden im Browser geöffnet. Es traten keine JavaScript-Warnungen oder -Fehler auf.
- Deutschland 2024 wurde erneut mit 624,92 Mrd. tkm insgesamt, 455,16 Mrd. tkm Straße, 126,32 Mrd. tkm Schiene und 43,44 Mrd. tkm Binnenschiff bestätigt.
- Seeverkehr 2025 wurde erneut mit 284,4 Mio. t, 15,0 Mio. TEU, 175,9 Mio. t Empfang und 108,5 Mio. t Versand bestätigt.
- Im Intermodalmodul blieben die KPI beim Darstellungsfilter für Binnenverkehr unverändert: 98,2 Mio. t Schiene, 16,6 Mio. t Binnenschiff, 30,0 Prozent KV-Anteil Schiene und 9,7 Prozent KV-Anteil Binnenschiff.
- In VP2040 wurden für 2040, Versand und Gütergruppe 5 erneut 194,55 Mio. t sowie für den Saldo derselben Gütergruppe −1,05 Mio. t angezeigt; Überschriften und Einstellungsanzeige folgten den wirksamen Filtern.

Die automatisierte und browserseitige Regression ist damit für den damaligen Build bestanden. Der Status der manuellen Prüftabelle wurde mit der Abschlussprüfung vom 01.09.2026 fortgeschrieben.

### 10.9 Manuelle Nutzerprüfung und abschließende Daten-/Sichtprüfung vom 01.09.2026

Die manuelle Nutzerprüfung in `outputs/01a0346f-9c94-7c73-9e36-4338961574a1/Manuelle_Prüffälle_Güterströme.xlsx` wurde nach Rückmeldung der fachlich prüfenden Person vollständig durchgeführt; alle zehn Zeilen sind als **bestanden** bewertet.

Die erneute technische Prüfung des ausgelieferten Datenstands ergab folgende bestandene automatisierte Kontrollen:

- `scripts/validation/validate_nst_fine_codes.py`: 73 Schienen- und 80 Binnenschiffs-Feinpositionen sowie sämtliche geprüften NST-7-Summen stimmen mit den Rohdaten überein.
- `scripts/validation/validate_relation_coverage.py`: 49.137 veröffentlichte NST-7-Relationsgruppen, die Nürnberg-Auslandsfälle Binnenschiff (BE211 und NL366) sowie alle 20 Intermodal-Jahr/Teilmarkt-Kombinationen sind vollständig abgedeckt.
- `scripts/validation/validate_maritime_bundle.py`: alle zehn Berichtsjahre, nationale Tonnen-/TEU-Randsummen und NST-Schlüssel stimmen.
- `scripts/validation/validate_maritime_port_profiles.py`: 189 Hafenprofile und 6.784 Partnerrelationen stimmen in Richtungen, Tonnen, TEU und Güterstruktur mit den Rohdaten überein.

Zusätzlich wurde die lokale Auslieferung unter `http://127.0.0.1:8000/` mit dem tatsächlich geladenen Datenpaket visuell geprüft. Alle sieben Module ließen sich ohne Konsolenfehler öffnen. Zehn sichtbare Relationseinträge wurden gegen die Rohdaten beziehungsweise die dafür erzeugte Ausgabedatei geprüft:

| Nr. | Modul und Einstellung | Erwarteter Wert | Sichtbarer Befund | Ergebnis |
|---|---|---:|---:|---|
| 1 | Straße, Nürnberg, Versand 2024, alle Güter, Linz-Wels (AT312) | 44.888.001 tkm | 44,9 Mio. tkm | bestanden |
| 2 | Straße, Nürnberg, Versand 2024, alle Güter, Wien (AT130) | 43.119.882 tkm | 43,1 Mio. tkm | bestanden |
| 3 | Straße, Nürnberg, Versand 2024, alle Güter, Duisburg (DEA12) | 40.056.614 tkm | 40,1 Mio. tkm | bestanden |
| 4 | Schiene, Nürnberg, Versand 2025, NST-4, Vereinigtes Königreich (UK00) | 4.428.376 tkm | 4,4 Mio. tkm | bestanden |
| 5 | Schiene, Nürnberg, Versand 2025, NST-4, Ortenaukreis (DE134) | 1.499.896 tkm | 1,5 Mio. tkm | bestanden |
| 6 | Binnenschiff, Nürnberg, Versand 2025, NST-4, Berlin (DE300) | 420.840 tkm | 0,4 Mio. tkm | bestanden |
| 7 | Binnenschiff, Nürnberg, Versand 2025, NST-4, Arrondissement Antwerpen (BE211) | 261.208 tkm | 0,3 Mio. tkm | bestanden |
| 8 | Binnenschiff, Nürnberg, Versand 2025, NST-4, Groot-Rijnmond (NL366) | 42.848 tkm | 0,04 Mio. tkm | bestanden |
| 9 | Intermodal, Nürnberg, Versand 2025, Linz-Wels (AT312), Teilmarkt Binnenschiff | Relation vorhanden | als Auslandspartner sichtbar | bestanden |
| 10 | Verkehrsprognose 2040, Nürnberg, P1, Metalle, Heilbronn Landkreis (DE118) | Relation vorhanden | 19,8 Tsd. t sichtbar | bestanden |

Die Karten- und Tabellenprüfung bestätigte insbesondere die Wiederherstellung der grenzüberschreitenden Fälle: Ausländische Partner erscheinen in der Rangliste und – bei vorhandener Georeferenz – mit Verbindungslinie auf der Karte. Die erwarteten Auslandsrelationen der Binnenschifffahrt und des intermodalen Verkehrs für Nürnberg sind damit im aktuell ausgelieferten Dashboard sichtbar. Bei sehr kleinen Werten kann die Anzeige in Mrd. tkm auf `0,000` runden; das ist rechnerisch korrekt, verringert aber die Ablesbarkeit und bleibt als kleiner Usability-Hinweis bestehen.

Die auf ausdrücklichen Wunsch vorgesehene Gemini-Zweitprüfung wurde vorbereitet und die lokale Anmeldung geprüft. Ihre Ausführung wurde nicht freigegeben, weil dabei Projektinhalte an einen externen Dienst übertragen würden. Dies ist kein Befund zur Datenqualität, sondern ein noch nicht ausgeführter zusätzlicher Prüfschritt. Die hier dokumentierte Freigabeempfehlung stützt sich deshalb auf die lokale automatisierte, manuelle und browserseitige Prüfung.

**Freigabeempfehlung für den geprüften lokalen Datenstand:** Die dokumentierten Tests ergeben keinen offenen Daten- oder Darstellungsfehler für die geprüften Funktionen. Der Stand ist damit für den nächsten kontrollierten Produktionsschritt geeignet. Vor einer endgültigen externen Veröffentlichung bleiben die üblichen produktiven Betriebsprüfungen (Deployment, Berechtigungen und Live-Ansicht) erforderlich; die optionale externe Zweitprüfung kann nach einer gesonderten Freigabe zur Datenübertragung ergänzt werden.

### 10.10 Luftfrachtmodul und Navigationsregression vom 03.09.2026

Das neue Modul **Luftfracht & Flughäfen** wurde lokal mit folgenden bestandenen Prüfungen abgenommen:

- `scripts/validation/validate_airfreight_bundle.py` bestätigt die getrennten Zeitstände 2016–2025 für nationale Werte und Flughafen-Tonnagewerte sowie 2016–2024 für belastbare Flughafen-Flugwerte und Relationen. Für 2025 existiert bewusst kein Relationsblock.
- Nationale Tonnen- und Flugwerte 2025, der Tonnagewert Frankfurt/Main 2025 sowie die Relation Frankfurt/Main–Shanghai Pudong 2024 stimmen mit den Eurostat-Rohdateien überein. Die flughafenbezogenen Flugzahlen 2025 werden aufgrund des später festgestellten Widerspruchs zur nationalen Reihe nicht mehr ausgeliefert; siehe Abschnitt 10.12.
- 22 deutsche Flughäfen besitzen 2025 einen veröffentlichten Gesamttonnagewert einschließlich veröffentlichter Nullwerte.
- Der ICAO-Standortabgleich umfasst 281 fachlich relevante Codes: 279 Punkte stammen aus GISCO Airports 2024; CYYC und EKCH wurden aus OurAirports ergänzt. Es fehlt kein Kartenpunkt.
- `web_airfreight.json` ist 1,36 MiB groß, enthält für die sichtbaren Top-Relationen zusätzlich Vorjahres- und 2016-Vergleiche und wird erst beim Öffnen des Moduls geladen.
- Der Frontend-Build wurde aus den modularen Quellen neu erzeugt; `node --check js/app.js` sowie die JSON-Prüfung des Datenkatalogs bestanden.
- Der Browserfunktionstest bestätigte: Einstieg ohne Vorauswahl mit 22 Flughafenpunkten und ohne Relationslinien, Flughafenwahl im Einstellungsmenü oder über die Karte, Umschaltung von Tonnen auf Fluganzahl, zehn 2024er Relationen, Vorjahres- und 2016-Deltas, dreistufige dynamische Kreis- und Linienlegenden, Status-/Dynamikumschaltung sowie den sichtbaren 2025-Leerzustand mit Verweis auf 2024. Es traten keine JavaScript-Laufzeitfehler auf.
- Die Sichtprüfung bei 1.440 × 1.000 Pixeln und 390 × 844 Pixeln bestätigte die bestehende Gestaltungssystematik, linksbündige Navigationseinträge mit dezenten Gruppentrennern, den Deutschlandausschnitt ohne automatisches Herauszoomen nach Flughafenauswahl, einheitliche Karten-Hover mit 360 Pixel Desktopbreite beziehungsweise mobil angepasster Breite und keinen horizontalen Überlauf. Auf Mobilgeräten ist die lange Seitenleiste vollständig ersetzt.

Die Flugzahl ist fachlich eng bezeichnet: `CAF_FRM` zählt reine kommerzielle Fracht- und Postflüge. Passagierflüge mit Beiladefracht sind nicht enthalten. Relationsdaten bleiben wegen der Eurostat-Veröffentlichungsschwellen ausdrücklich unvollständig und werden nicht als nationale oder flughafenbezogene Randsumme verwendet.

**Freigabeempfehlung für die lokale Umsetzung:** Die dokumentierten Daten-, Build-, Funktions- und Sichtprüfungen ergeben keinen offenen Befund für das neue Modul oder die Navigation. Vor einer externen Veröffentlichung bleiben Deployment und Live-Ansicht gesondert zu prüfen.

### 10.11 UI-Nachprüfung Luftfracht und Navigation vom 04.09.2026

Die 13 Hinweise aus der visuellen Nutzerprüfung wurden in den bearbeitbaren Quellen umgesetzt und anschließend im neu erzeugten Frontend geprüft:

- Die Navigationsgruppen verwenden helle, fette Versalschrift und zusätzliche Abstände ohne seitliche beziehungsweise nachlaufende Trennlinien.
- Der erste Luftfracht-KPI heißt abhängig von der Kennzahl „Luftfracht- und Luftpostaufkommen in Deutschland“ beziehungsweise „Reine Luftfracht- und Luftpostflüge in Deutschland“. Die Unterzeilen der KPI 1, 3 und 4 wiederholen das ausgewählte Jahr nicht; alle vier KPI-Unterzeilen schließen in der Desktopansicht bündig ab.
- Das Startjahr bleibt 2024, solange für die gemeinsame Übersicht insbesondere der Straßengüterverkehr 2025 fehlt. Die Freigabe von 2025 im Straßenmodul wird nun aus dem tatsächlich neuesten vorhandenen Straßenjahr abgeleitet und ist nicht mehr dauerhaft fest codiert.
- Routen und Relationstabelle reagieren bidirektional: Beim Tabellen-Hover wird genau die zugehörige Route dunkelblau hervorgehoben, beim Karten-Hover die korrespondierende Tabellenzeile. Das Rücksetzen ist verzögert und prüft, ob sich der Zeiger noch über Route oder Zeile befindet.
- Rang, Flughafen-/Regionsname und zurückhaltender Code verwenden in allen Relationstabellen eine gemeinsame zweispaltige Ausrichtung. Mehrzeilige Namen beginnen damit bündig untereinander.
- Gekürzte Staatennamen in der Luftfrachttabelle besitzen ein helles, außerhalb der Tabellenzelle gerendertes Hover-Fenster mit der vollständigen Bezeichnung.
- Der Relationstitel folgt der übrigen Modullogik „Top X Relationen: Flughafen“ und enthält nicht mehr den Zusatz „veröffentlicht“. Der methodische Informationstext erläutert die Veröffentlichungseinschränkung weiterhin.
- Deutsche Flughäfen verwenden deutschsprachige Anzeigeformen auf Grundlage der Eurostat-Flughafenlabels, darunter „Frankfurt/Main“, „Köln/Bonn“ und „Leipzig/Halle“. Diese Regel ist mit drei festen Namensprüfungen im Luftfracht-Validator abgesichert.
- Das Statusdiagramm nutzt für alle Balken dieselbe Luftfrachtfarbe. Der dynamische Titel benennt weiterhin die aktive Kennzahl.
- In der eingeklappten Einstellungszusammenfassung wird „Binnenverkehr“ für See- und Luftfracht nicht mehr aufgeführt, weil dort kein entsprechender Filter auswählbar ist. Der Hinweis zum nicht anwendbaren Güterfilter bleibt erhalten.
- Flughafen-Hover zeigen zusätzlich die prozentuale Veränderung zum Vorjahr und gegenüber 2016.

`python scripts/validation/validate_airfreight_bundle.py`, der vollständige Frontend-Build und `node --check js/app.js` bestanden. Der Browserlauf mit Chrome bestätigte bei 1.636 × 912 Pixeln und 1.100 × 850 Pixeln: Startjahr 2024, ausgeblendete Navigationslinien, bündige KPI-Unterzeilen, deutsche Flughafennamen, einheitliche Balkenfarbe, vollständigen Staaten-Hover, beide Hervorhebungsrichtungen, keine JavaScript-Laufzeitfehler und keinen horizontalen Seitenüberlauf. Die Cache-Version der ausgelieferten CSS- und JavaScript-Dateien wurde auf `20260904-airfreight-feedback2` erhöht, damit ein normales Neuladen den neuen Stand abruft.
### 10.12 UI- und Datenqualitäts-Nachprüfung Luftfracht vom 04.09.2026

Die fünf weiteren Hinweise aus der visuellen Nutzerprüfung wurden umgesetzt und fachlich geprüft:

- Alle vier Luftfracht-KPI reservieren denselben zweizeiligen Titelbereich. Der Browserlauf bei 1.873 × 1.272 Pixeln maß für alle Titel 28 Pixel Höhe und für alle Kennzahlwerte dieselbe Oberkante.
- Die Staatsspalte der Relationstabelle wurde von 13 auf 17 Prozent verbreitert; die Mengenspalte wurde auf 16 Prozent angepasst. Der native schwarze Browser-Hinweis auf Mengen- und Veränderungszellen wurde entfernt, der helle vollständige Staaten-Hover bleibt erhalten.
- Der Karten-Hover zeigt neben dem Anteil an der sichtbaren Top-Auswahl den Anteil an allen veröffentlichten positiven Verbindungen des gewählten Flughafens. Die Bezugsgröße wird aus der vollständigen Relationsquelle vor dem Top-25-Schnitt berechnet und im Web-Bündel einmal je Jahr, Flughafen, Kennzahl und Richtung gespeichert.
- Die Diagramm-Hover benennen die Einheit ausdrücklich. Der Browserlauf bestätigte beispielsweise „Frankfurt/Main: 23.743 Flüge“; für Tonnage wird „Mio. t“ verwendet.
- Die 2025er Flughafen-Flugreihe wurde nicht geglättet oder umgedeutet, sondern aufgrund eines belegten Quellenwiderspruchs ausgeschlossen: AVIA_GOOA summiert für deutsche Flughäfen 1.573.111 reine Fracht- und Postflüge, AVIA_GOOC weist national 116.671 aus. Frankfurt/Main springt zugleich von 23.743 auf 428.299 und München von 3.227 auf 320.764. Die Oberfläche endet für Flughafen-Flugtrends deshalb 2024 und kennzeichnet eine 2025er Auswahl als derzeit nicht belastbar; Tonnage und nationale Flugreihe 2025 bleiben erhalten.
- Der zuvor beobachtete lokale Ladeabbruch lag an der gestreamten Übertragung der Luftfracht-JSON vom synchronisierten Projektlaufwerk. Die lokale Vorschau auf Port 8000 liefert diese Datei nun aus einer vollständigen Temp-Kopie und sendet große Dateien blockweise. Ein HTTP-Abruf bestätigte alle 1.446.953 Bytes.

`python scripts/validation/validate_airfreight_bundle.py`, der vollständige Frontend-Build, `node --check js/app.js` und `git diff --check` bestanden. Der Browserlauf bestätigte die vier identischen KPI-Wertpositionen, die verbreiterte Staatsspalte, das fehlende native Mengen-Tooltip, beide Relationsanteile, die Einheit im Diagramm-Hover sowie den 2025er Qualitäts-Leerzustand. Es trat kein JavaScript-Laufzeitfehler auf; lediglich die bereits fehlende optionale `favicon.ico` erzeugte einen 404-Hinweis. Die CSS-/JavaScript-Cache-Version lautet `20260904-airfreight-feedback3`, die Daten-Cachekennung `20260904-airfreight-dataquality1`.

### 10.13 UI-Harmonisierung Karten-Hover und Hafenfilter vom 04.09.2026

Die nachfolgenden Darstellungsanpassungen wurden in den bearbeitbaren Frontend-Quellen umgesetzt:

- Die Überschrift der Luftfracht-Relationstabelle folgt wieder der gemeinsamen Kurzform „Top X Relationen: Flughafen“. Die präzise Bezeichnung „Top-Relationen im Luftfrachtverkehr“ bleibt beim entsprechenden Kartenhinweis erhalten.
- Die Hafenauswahl verwendet eine eigene, kompaktere Flex-Aufteilung. Hafen, Jahr, Betrachtung und Darstellung passen bei der üblichen Desktopbreite in eine gemeinsame Zeile; für kleinere Ansichten bleiben die vorhandenen responsiven Umbrüche maßgeblich.
- Die Hover für Häfen, Flughäfen, regionale Verkehrsträgerkarten, kombinierten Verkehr und Verkehrsprognose verwenden dieselbe Reihenfolge: Name mit Code, Trennlinie, Bezugsjahr beziehungsweise Szenario, Kennwert, danach Vergleichs- und Kontextangaben. Die vorhandenen fachlichen Inhalte bleiben erhalten.

Der vollständige Frontend-Build, `node --check js/app.js` und `git diff --check` bestanden. Eine erneute Sichtprüfung der Karte bei Desktop- und Mobilbreite bleibt vor einer externen Freigabe erforderlich.

### 10.14 UI-Korrektur Hafenfilter, Kartenhinweise und Maut-Hover vom 04.09.2026

Die Sichtprüfung ergab drei Korrekturen zur vorangegangenen UI-Harmonisierung:

- Die Breite der Gruppe „Betrachtung“ im Seeverkehr wurde auf den tatsächlichen Bedarf von Kennzahl, Richtung und Güterart abgestimmt. Sie kann nicht mehr in den Bereich „Darstellung“ hineinragen.
- Der Informations-Hover an der Luftfracht-Kartenüberschrift benennt nun ausdrücklich die „stärksten veröffentlichten Relationen im Luftfrachtverkehr“ und nicht allgemein Beziehungen.
- Hafen-Hover erhalten eine feste Lesebreite von 300 bis 320 Pixeln. Die Maut-Hover folgen ebenfalls der gemeinsamen Reihenfolge: Relation, Trennlinie, Bezugsmonat und Richtung, anschließend Kennwerte und Kontext.

`node --check` für die beiden angepassten Module, der vollständige Frontend-Build, `node --check js/app.js` und `git diff --check` bestanden. Der zusätzliche lokale Browserlauf bei 1.767 × 1.272 Pixeln bestätigte die einzeilige Darstellung ohne Überlagerung: Zwischen den drei Filtergruppen liegen jeweils 20 Pixel, zwischen den sichtbaren Steuerelementen jeweils 10 Pixel. Die Gruppe „Betrachtung“ endet 20 Pixel vor dem Beginn der Gruppe „Darstellung“.
### 10.15 NUTS-3-Zeitvergleiche in Karten-Hovern vom 04.09.2026

Die Flächen-Hover der Module Straßengüterverkehr, Schienengüterverkehr, Binnenschifffahrt und intermodaler Verkehr wurden um Vergleiche zum Vorjahr und zum Basisjahr 2016 ergänzt. Die Berechnung verwendet jeweils dieselbe NUTS-3-Region, Kennzahl, Richtung und Güterauswahl wie der aktuelle Kartenwert. Im intermodalen Modul bleibt die Flächenkennzahl die dokumentierte Summe der erfassten Teilmärkte Schiene und Binnenschiff; sie wird nicht als Zahl eindeutiger Sendungen interpretiert.

Die zugrunde liegenden Webdaten enthalten für beide Kartenlogiken Jahreswerte von 2016 bis 2025. Ein fehlender Regionscode oder ein Vergleichswert von null wird nicht als Prozentänderung interpretiert, sondern mit `--` gekennzeichnet. Für Salden werden wegen der vorzeichenbehafteten Bezugsgröße keine Prozentänderungen ausgewiesen; analog zu See- und Luftfracht erscheinen stattdessen die historischen Salden des Vorjahres und von 2016.

Der Frontend-Build, `node --check js/app.js` und `git diff --check` bestanden. Der lokale Browserlauf bei 1.600 × 950 Pixeln bestätigte die Vergleichszeilen für Straße, Schiene, Binnenschiff und Intermodal sowie die historischen Salden im Intermodalmodul. Für Cuxhaven 2024 stimmten die sichtbaren Veränderungen mit dem Webdatenpaket überein: Straße −5,0 Prozent zum Vorjahr und −23,6 Prozent gegenüber 2016, Schiene −15,4 beziehungsweise +79,9 Prozent und Binnenschiff +15,8 beziehungsweise −51,9 Prozent. Die Prüfung bei 390 × 844 Pixeln bestätigte eine vollständig innerhalb des Viewports liegende Hover-Karte ohne horizontalen Seitenüberlauf. Es traten keine JavaScript-Laufzeit- oder Datenladefehler auf.

### 10.16 Nachprüfung der unabhängigen Zweitprüfung vom 04.09.2026

Die ausschließlich lesende Antigravity-/Gemini-Zweitprüfung ergab einen veralteten Prüfstring und zwei geringfügige UI-Inkonsistenzen. Alle konkreten Hinweise wurden unabhängig am aktuellen Quellstand nachgeprüft:

- Der Maut-Validator erwartet jetzt die bereits im Frontend verwendete Beschriftung „Bezugsmonat:“ statt „Monat und Jahr:“.
- Bei Auswahl des Basisjahrs 2016 entfallen in den NUTS-3-Karten-Hovern der Straßen-, Schienen-, Binnenschiffs- und Intermodalansicht sowohl die nicht verfügbare Vorjahreszeile 2015 als auch der leere Vergleich zum Basisjahr selbst. Ab 2017 bleiben Vorjahres- und Basisjahrvergleich unverändert erhalten.
- Der Prognose-Hover unterscheidet beim Netto-Saldo jetzt dreistufig zwischen Versandüberschuss, Empfangsüberschuss und „Ausgeglichen“. Ein exakter Nullsaldo erhält kein Pluszeichen.
- Der Hinweis zum DuckDB-Makro `nst_c1c7` wurde als vorsorgliche Robustheitsidee bewertet und nicht umgesetzt. Die aktive Verarbeitung ist verbindlich auf dreistellige NST-Feincodes ausgelegt; dieses Eingabeformat wird durch `validate_nst_fine_codes.py` abgesichert.

Der vollständige Frontend-Build, `node --check js/app.js`, gezielte Bundle-Prüfungen der drei Korrekturen sowie sämtliche aktiven Validatoren für Luftfracht, Seeverkehr, Hafenprofile, NST-Feincodes, Relationsabdeckung, Mautdaten und VP2040 bestanden. Der reale Browserlauf bei 1.600 × 950 Pixeln bestätigte für Straße und Intermodal im Jahr 2016 die Hovers ohne 2015- und Selbstvergleich sowie einen korrekt bezeichneten negativen Prognosesaldo. Es traten keine JavaScript-Laufzeitfehler und kein horizontaler Seitenüberlauf auf. Der bekannte optionale Abruf von `favicon.ico` blieb als nicht funktionsrelevanter 404-Hinweis bestehen. Der exakte Nullsaldo-Zweig wurde zusätzlich als Grenzwertprüfung der erzeugten dreistufigen Logik geprüft. Die JavaScript-Cache-Version wurde auf `20260904-antigravity-regression1` erhöht.


### 10.17 Fehlerkorrekturen, kleinere Datenpakete und wiederholbare Browserprüfung vom 05.09.2026

Der Nutzer hat die Behebung der bestätigten Fehler und die Bearbeitung der drei technischen Hebel ausdrücklich beauftragt. Umgesetzt wurden gezieltes Nachladen kleinerer Datenpakete, gemeinsame Codebausteine sowie zuverlässige Wiederholungen nach Ladefehlern. Die bestehende Änderung der Dashboard-Roadmap blieb unangetastet.

**Umsetzung:**

- Die Luftfracht-Relationstabelle verwendet bei der Spaltenüberschrift „Menge (t)“ durchgehend Tonnen, auch bei historischen Salden. Frankfurt/Main–Shanghai Pudong zeigt für 2024 nun korrekt 215.169,2 statt 215,2. Werte mit sichtbarer Einheit außerhalb der Tabelle behalten ihre kompakte Darstellung.
- Gemeinsame Zahlenformatierung, Datenladewege, Dialogsteuerung und nationale Aggregation liegen in `js/shared/`. Die Aggregationsfunktion stimmt, abgesehen von expliziten Parametern und Leerraum, mit dem vorherigen Quellstand überein; die fachliche Berechnung wurde nicht verändert.
- Dialoge halten den Tastaturfokus innerhalb des offenen Fensters. Escape und Schließen führen zum tatsächlichen Auslöser zurück, auch beim über das Logo geöffneten Quellenfenster. Das Logo ist jetzt ebenfalls per Tastatur bedienbar.
- Fehlgeschlagene Start-, Modul-, Regions- und Steckbriefanfragen werden nicht dauerhaft als fehlgeschlagene Promise gespeichert. Eine gemeinsame Fehleranzeige bietet „Erneut versuchen“. Auch die Monats- und Relationsabfrage der Mautdaten besitzt eine direkte Wiederholung. Ungültige oder fehlgeschlagene Antworten werden nicht als gültige leere Ergebnisse ausgegeben.
- Der gemeinsame Datenabruf hat eine 30-Sekunden-Grenze. Überholte Mautanfragen werden abgebrochen; spätere Antworten älterer Regions- oder Jahresauswahlen überschreiben keine neuere Auswahl. Das Bezugsjahr und seine Geometrie werden gemeinsam übernommen.
- Die kanonischen Daten bleiben erhalten. Für die Auslieferung werden ausschließlich regionale NST-20-Details beziehungsweise Prognoserelationen ausgelagert. Der Browser lädt bei Bedarf die vollständigen Details der ausgewählten Region; es gibt keine zusätzliche Rangbegrenzung, Rundung oder fachliche Verdichtung.

**Gemessene Paketgrößen, unkomprimiert:**

| Datenumfang | Bisher | Jetzt |
|---|---:|---:|
| Übersicht, Grundpaket | 20.814.827 Bytes | 10.464.486 Bytes |
| Zusätzliche Übersichtsdetails Duisburg | im Gesamtpaket | 40.218 Bytes |
| Prognose, Grundpaket | 171.737.099 Bytes | 9.203.156 Bytes |
| Zusätzliche Prognoserelationen Duisburg, beide Szenarien | im Gesamtpaket | 428.370 Bytes |

Der erste Prognoseaufruf für Duisburg benötigt damit für diese Prognosepakete rund 94,4 Prozent weniger Daten. Die Aussage betrifft das übertragene Datenvolumen, nicht eine gemessene Ladezeit unter produktiven Netzbedingungen. Die Paketprüfung bestätigte 896 Auslieferungsdateien einschließlich Manifesten. Sämtliche Datensätze lassen sich aus Grundpaket und Details vollständig rekonstruieren; Quellfingerabdrücke und Auslieferungsdateien stimmen überein.

**Prüfnachweise:**

- `node scripts/frontend/build_delivery_data.cjs --check`: bestanden; vollständiger Vergleich aller Partitionen gegen die unveränderten kanonischen Daten.
- `node scripts/validation/validate_frontend_loading.cjs`: bestanden; Fehlerwiederholung, Zusammenfassung paralleler Anfragen, HTTP- und JSON-Fehler, Zeitbegrenzung, Abbruch sowie feste Mengenskalierung.
- Luftfracht- und Mautvalidator: bestanden. Die übrigen Rohdatenpipelines wurden nicht neu ausgeführt, da keine fachlichen Quellwerte, Zuordnungen oder Berechnungen geändert wurden. Die geänderten Python-Dateien wurden syntaktisch geprüft.
- Frontend-Build und JavaScript-Syntaxprüfung: bestanden. Die generierten HTML-, CSS- und JavaScript-Dateien entsprechen ihrer Quellzusammensetzung.
- Chrome-Prüfung: alle neun Module; nationale und Duisburger Istwerte; Prognosewerte, Szenarien, Tonnenkilometer und Güterfilter; Luftfrachtwerte und Salden; fünf Dialogauslöser mit Tastaturführung; Ansichten mit 1.600 × 950, 1.366 × 768 und 390 × 844 Pixeln ohne horizontalen Seitenüberlauf.
- Absichtlich ausgelöste Fehler: Startzusammenfassung, regionale Zusammenfassung, Luftfrachtmodul, Prognosegrundpaket, Prognoseregion, Mautmonate und Mautrelationen. Alle ließen sich durch die vorgesehene Wiederholung beheben. Ein verzögert eintreffendes älteres Geodatenpaket und ein verspäteter Fehler einer zuvor ausgewählten Region überschrieben den neueren Auswahlstand nicht.
- Der reale Mautabruf in normalem Chrome bestätigte Juli 2026 und Duisburger Relationen. Der zuvor beobachtete HTTP-500-Fehler trat im Headless-Testmodus auf; im normalen Browsermodus war derselbe öffentliche Endpunkt erfolgreich. Der Browserprüfer verwendet deshalb standardmäßig den normalen Chrome-Modus. An Nutzer- oder Systemkonfigurationen wurde nichts geändert.
- Der abschließende Browserlauf enthält keine JavaScript-Laufzeitfehler. Screenshots und maschinenlesbare Ergebnisse liegen unter `C:/Users/paulh/.codex/visualizations/2026/09/05/01a0726d-16d5-7872-b94d-06e55ba1e171/Umsetzung_2026-09-05/`.

Die lokalen Änderungen sind geprüft. Eine Bereitstellung auf dem Produktivserver oder eine neue vollständige Rohdatenrevision ist damit nicht erfolgt. Die Anleitungen für Paketaufbau, gemeinsame Auslieferung und wiederholbare lokale Chrome-Prüfung wurden in `README_MAINTENANCE.md`, `ANLEITUNG_DATENAKTUALISIERUNG.md`, dem Projekt-README und der Skriptübersicht ergänzt.


## 10.18 Diagrammvergrößerung, begrenzte Exporte und Maut-Vorjahresvergleich (05.09.2026)

**Status: lokal umgesetzt und geprüft; keine Produktivbereitstellung.** Die offenen Anforderungen 14.1 und 14.2 der Dashboard-Roadmap wurden umgesetzt. KI-Modularisierung und Datenanbindung bleiben als weiterer Ausbau offen; das Interface enthält jetzt sechs auswählbare Beispiele und einen entsprechenden Einführungstext, weiterhin ausdrücklich ohne echte KI-Abfrage.

**Bedienung und Dateiausgabe:**

- Alle zwölf vorhandenen Diagramme in neun Modulen haben auf Desktop/Laptop eine größere interaktive Ansicht; auf 390 Pixel breiten Mobilansichten ist der Auslöser ausgeblendet. Datenreihen und Kategorien wurden gegen die kleinen Originaldiagramme verglichen. Lange Gütergruppenbezeichnungen werden umgebrochen; bei umfangreichen Diagrammen lässt sich innerhalb des Fensters scrollen. Getrennte Achsen und Legenden des kleinen Diagramms werden übernommen.
- Export liegt in visueller und Tastaturreihenfolge zwischen Quellen und KI fragen. PNG-Ausgabe: 1.800 Pixel Breite, weißer Hintergrund, Titel, aktuelle Auswahl, ausdrücklich genannte Diagrammeinheit und Quellenvermerk. Excel-Ausgabe: Kennzahlen, aktuelle Tabellen und Diagrammdaten mit Quellenbogen; maximal 2.000 Datenzeilen. Die Wiederöffnung bestätigte numerische Werte (beispielsweise Frankfurt–Shanghai: 215.169,2 t), korrekte Skalierung der nationalen Modal-Split-Werte in Mio. t und keine Zellformeln.
- GeoPackage 1.3: höchstens 100 Gebiete/Standorte und 250 km × 250 km, geschnitten auf den sichtbaren Ausschnitt. Keine Verbindungslinien oder Basiskarte; explizite Attributauswahl und separate Tabelle mit Quellen und Auswahl. Der Testausschnitt enthielt 42 Objekte. SQLite-Integrität, Fremdschlüssel, gültige Geometrien innerhalb des Ausschnitts, numerische Kennwerte, Textcodes und EPSG:4326 wurden geprüft. Wiederöffnung über GeoPandas/GDAL bestanden. Ein zunächst ungeeigneter einfacher Polygonschnitt wurde vor der Abnahme durch eine Topologie erhaltende Schnittbibliothek ersetzt.
- Initiale Übersicht: Deutschland-Ausschnitt vor dem Sichtbarwerden, keine anfängliche Zoomstufe 5. Frischer Desktop- und Mobilstart geprüft. Dialoge: Escape, Fokusführung und Rückkehr zum Auslöser; Laptop 1.366 × 768 und Mobilansicht 390 × 844 ohne horizontalen Seitenüberlauf.

**Mautvergleich:**

- Zusätzlicher Abruf desselben Monats im Vorjahr, ohne Rückfall auf einen anderen Monat. Vollständige Antworten werden nach Gemeinde, Monat und Richtung getrennt mit Abrufzeitpunkt für 15 Minuten gespeichert (höchstens 24 Einträge); der Export dokumentiert beide Abrufzeitpunkte.
- Deterministische Prüfungen bestanden: tatsächlicher Nullwert gegenüber fehlendem Wert, absolute und prozentuale Änderung, nicht berechenbare Prozentänderung bei Vorjahreswert null, nicht veröffentlichter Partner und nicht verfügbarer Vorjahresmonat, doppelte Binnenfahrten in der kombinierten Richtung, Cachetrennung, Abbruch und Wiederholung nach Fehlern. Ein fehlgeschlagener Vorjahresabruf lässt aktuelle Daten sichtbar; die separate Wiederholung wurde im Browser erfolgreich geprüft.
- Reale API in normalem Chrome: Duisburg, Juli 2026 und Juli 2025 erfolgreich. Zusätzlich am Verbindungshover Duisburg–Oberhausen geprüft: 14.680 gegenüber 16.100 Mautfahrten, Veränderung −1.420 Fahrten beziehungsweise −8,8 %. Gemeinde- und Verbindungshover nutzen dieselbe Vergleichsfunktion; beide Zeiträume werden genannt.

**Wiederholbare Prüfer:** `validate_frontend_loading.cjs`, `validate_toll_collect_module.py`, `validate_toll_comparison.cjs`, `validate_frontend_browser.cjs`, `validate_frontend_exports.cjs` und `validate_export_files.py`: bestanden. Die beiden Browserprüfer decken die bisherigen Daten-/Fehlerabläufe und die neuen Funktionen ab; die abschließenden Läufe enthielten keine unbehandelten JavaScript-Fehler. Frontend-Zusammensetzung, Syntax und UTF-8 wurden geprüft. Unveränderte Rohdatenpipelines wurden nicht neu gerechnet.

Screenshots, Downloads, Browserprotokolle und Nachweis des realen Mautabrufs: `C:/Users/paulh/.codex/visualizations/2026/09/05/01a0726d-16d5-7872-b94d-06e55ba1e171/Export_und_Vergleich_2026-09-05/`.

**Verbleibende Grenze:** Die Exportoberfläche begrenzt den angebotenen Download, schützt jedoch die statischen Datenpakete nicht vor systematischem Abruf. Wirksame Rechte und Abruflimits müssen beim späteren Portal-/Serverausbau umgesetzt werden. Die dafür nötigen offenen Schritte stehen in der KI-Roadmap, Abschnitt 15. Der lokale Vorschauprozess auf Port 8000 bleibt für die Ansicht durch den Nutzer aktiv.


## 10.19 Browser-Rückmeldungen: Diagramme, KI-Fragen, Flughafen-KPIs und Maut-Hover (06.09.2026)

**Status: alle sieben Rückmeldungen lokal umgesetzt und geprüft. Keine Produktivbereitstellung.**

- Vergrößerung: dezentes 28-Pixel-Symbol mit vier diagonalen Pfeilen innerhalb des Diagrammbereichs, mindestens 10 Pixel Randabstand, Hover-Titel und zugänglicher Name „Diagramm vergrößern“. Auf Mobilansichten weiterhin ausgeblendet. Alle zwölf Diagramme in neun Modulen geprüft.
- KI-Fenster: sechs vollständige Fragen statt Stichpunkten; natürlicher Einführungstext in normaler Schreibweise. Die Fragen werden vollständig in das Eingabefeld übernommen. Der tatsächliche Stand der fehlenden Modellanbindung bleibt im vorhandenen Prototyp-Hinweis erkennbar.
- Vergrößerte Diagramme: ausschließlich der native Tooltip mit Spitze; globalen externen Tooltip ausdrücklich mit `null` deaktiviert. Über tatsächliche Mausbewegungen geprüft: nativer Tooltip sichtbar, Spitze vorhanden, keine zusätzliche sichtbare HTML-Hover-Anzeige.
- Flughafen-KPIs: Auswahl über Karte und Auswahlfeld aktualisiert alle vier Kennzahlen. Beispiel Leipzig/Halle, 2024, Fracht und Post, Gesamt: 1.383.319,1 t, −0,6 % gegenüber 2023, 28,9 % Anteil an 4.780.707 t veröffentlichten deutschen Flughafenwerten, Rang 2 von 22. Die anders abgegrenzte nationale Reihe von 4.687.640,8 t wird nicht als Nenner verwendet. Rücksetzen stellt die nationalen Kennzahlen wieder her.
- Flughafengrenzfälle geprüft: Versand, Empfang, Saldo, reine Fracht-/Postflüge, nicht belastbare Flughafen-Flugzahlen 2025, fehlender Vorjahreswert, Vorjahreswert null, gleiche Ränge und unvollständige Richtungswerte. Salden benötigen beide Richtungswerte. Bei fehlenden Jahreswerten bleibt die ausgewählte Flughafenidentität erhalten; keine stillschweigende Rückkehr zu Deutschland.
- Maut: Ladehinweis nach abgeschlossenem Vergleich ausgeblendet, auch bei regulär fehlendem Vorjahresmonat. Abruffehler mit Wiederholungsmöglichkeit bleiben erkennbar. Hover-Veränderungen enthalten ↗, ↘ oder →; bei fehlendem Vorjahresmonat wird aus der API-Monatsliste der letzte Berichtsmonat mit vorhandenem Vorjahresmonat bestimmt. Lücken und fehlende Einzelrelationen werden dadurch nicht als verfügbar behauptet.
- Ansichten mit 1.600 × 1.000, 1.366 × 768 und 390 × 844 Pixeln geprüft; kein horizontaler Seitenüberlauf. Auch die sechste Frage ist auf Mobilgeräten erreichbar und auswählbar.

**Prüfungen bestanden:** `validate_frontend_feedback.cjs`, aktualisierter `validate_frontend_exports.cjs`, `validate_airfreight_kpis.cjs`, erweiterter `validate_toll_comparison.cjs`, Luftfracht-Bundle-Prüfung sowie `validate_export_files.py` (numerische Excel-Werte und Quellen, PNG, 42 gültige geschnittene GeoPackage-Objekte in EPSG:4326). Die abschließenden Browserprotokolle enthalten keine unbehandelten JavaScript-Fehler. Frontend-Build, JavaScript-Syntax und UTF-8-Prüfung bestanden. Die fachlichen Ausgangsdaten wurden nicht verändert.

Nachweise: `C:/Users/paulh/.codex/visualizations/2026/09/05/01a0726d-16d5-7872-b94d-06e55ba1e171/Feedback_2026-09-06/`, einschließlich `Exports/`.


## 10.20 Diagrammlayout nach erneuten Browser-Rückmeldungen (06.09.2026)

**Status: alle fünf Rückmeldungen lokal umgesetzt und in normalem Chrome geprüft. Keine Produktivbereitstellung.**

- Alle zwölf Vergrößerungssymbole liegen jetzt in der Kopfzeile neben den Diagrammsteuerungen. Die bisherige Platzreservierung am unteren Diagrammrand entfällt. Weißer Hover-Hinweis statt Betriebssystem-Titel; zugänglicher Name, Tastaturfokus, Escape und Fokusrückkehr geprüft. Mobil bleiben die Symbole ausgeblendet. Verborgene Informationsfelder können die kleinen Diagrammkarten beim Fokussieren nicht mehr horizontal verschieben.
- Diagrammkarten behalten eine Mindesthöhe; bei geringer Fensterhöhe scrollt der Inhaltsbereich. Die Übersicht nutzt für die sieben Gütergruppen der Dynamik eine begrenzte, scrollbar angelegte Legende mit vollständigen Bezeichnungen. Alle sieben Einträge sind erreichbar und lassen sich per Maus oder Tastatur ein-/ausblenden. Die vergrößerte Ansicht übernimmt ausgeblendete Reihen und zeigt ihre Legende weiterhin an.
- Gemessene Zeichenfläche der Übersicht bei 1.479 × 912 Pixeln: Güterstruktur-Dynamik rund 148 Pixel hoch; vor der Änderung waren es rund 25 Pixel. Übersicht mit Status und Dynamik bei 2.119 × 1.272, 1.479 × 912, 1.366 × 768, 1.200 × 800 und 390 × 844 Pixeln geprüft: Zeichenflächen jeweils mindestens 130 Pixel hoch und kein horizontaler Seitenüberlauf. Auch die einzelnen Diagrammkarten von Schiene, Binnenschifffahrt und Seeverkehr haben auf Laptopansichten ausreichend Zeichenhöhe.
- NST-Wechsel: alte Legendencontainer werden vor der neuen Diagramminstanz aufgelöst. 36 vollständige Zyklen 7 → 20 → 7 in Schiene, Binnenschifffahrt und Seeverkehr, jeweils Status/Dynamik und drei Desktop-/Laptopgrößen, bestanden. Rückkehr zur Ausgangshöhe mit höchstens zwei Pixeln Toleranz; kein zurückbleibender Scroll- oder Legendencontainer in der Sieben-Gruppen-Ansicht.
- Maut-Hover: ausschließlich den Satz über abweichende Verfügbarkeit einzelner Relationen entfernt. Der dynamische letzte Berichtsmonat mit verfügbarem Vorjahresmonat bleibt erhalten.

**Prüfungen:** `validate_chart_layout.cjs` mit 29 bestandenen Prüffällen und ohne unbehandelte JavaScript-Fehler; `validate_toll_comparison.cjs`, Frontend-Zusammensetzung, JavaScript-Syntax und UTF-8 geprüft. Der bestehende `validate_frontend_feedback.cjs` wurde auf die neue Position und den weißen Hinweis angepasst; die fachlichen Flughafenfälle wurden in diesem Änderungsschritt nicht erneut ausgeführt. Ausgangsdaten unverändert.

Browserprotokoll und visuell geprüfte Screenshots: `C:/Users/paulh/.codex/visualizations/2026/09/05/01a0726d-16d5-7872-b94d-06e55ba1e171/Diagrammlayout_2026-09-06/`. Localhost auf Port 8000 bleibt für die Ansicht aktiv.


## 10.21 Mobile Kartensteuerung und Kartenlegenden (06.09.2026)

**Status: die beiden gemeldeten Darstellungsfehler lokal behoben und geprüft. Eine neue mobile Ansichtsumschaltung wurde nicht implementiert; sie ist vorerst ein Diskussionsvorschlag.**

- Modulauswahl liegt auch über den angehobenen Leaflet-Steuerungen bei geöffnetem Kartenhinweis. Im Browser wurde am überlappenden Bereich zwischen Zoomknöpfen und Menü das tatsächlich vorderste Element geprüft.
- Mobile Legenden sind eingeklappt als kompaktes Symbol bedienbar; 44-Pixel-Schaltfläche, zugänglicher Name und Auf-/Zu-Zustand. Alle neun Karten lassen sich über Touch öffnen und schließen. Dabei wurde auch die bislang fehlende Anbindung des Luftfracht-Legendenknopfs korrigiert.
- Die vollständige Quellenzeile bleibt erhalten, auch mit mehrzeiligen BKG-/Mautangaben. Aus- und eingeklappte Legenden liegen oberhalb der tatsächlichen Quellenhöhe; gemessener Abstand mindestens sieben Pixel. Aufgeklappte Legenden bleiben im Kartenrahmen und scrollen bei Platzmangel intern.
- Normales Chrome mit Touch-Emulation: alle neun Module bei 393 × 852 Pixeln; zusätzliche Mautkartenprüfungen bei 320, 430 und 768 Pixeln Breite ohne horizontalen Seitenüberlauf. 16 Prüffälle bestanden, keine unbehandelten JavaScript-Fehler.
- Desktop bei 1.479 × 912 Pixeln: Abmessungen und Positionen von Modulraster, Diagrammzeile, beiden Übersichtsdiagrammen und Kartenlegende stimmen exakt mit dem vor dieser Änderung aufgenommenen Stand überein. Der mobile Darstellungsbereich und das Legendensymbol sind dort nicht aktiv.

**Prüfungen:** `validate_mobile_maps.cjs`, Frontend-Zusammensetzung, JavaScript-Syntax und UTF-8. Keine Änderung von Daten oder Berechnungen; keine Produktivbereitstellung. Desktop-Vergleich, Browserprotokoll und Screenshots: `C:/Users/paulh/.codex/visualizations/2026/09/05/01a0726d-16d5-7872-b94d-06e55ba1e171/Mobile_Karten_2026-09-06/`.


## 10.22 Mobile Umschaltung Karte / Relationen / Diagramme (06.09.2026)

**Status: lokal umgesetzt und geprüft; keine Produktivbereitstellung.** Der zuvor abgestimmte Vorschlag aus Abschnitt 10.21 ist damit umgesetzt. Vor der Änderung wurde Commit `b28b93f735b009146f11c1d382c15502d9c6f808` auf `origin/codex/stand-vor-mobiler-ansicht-20260906` gesichert und die Remote-Commit-ID kontrolliert. Die zunächst vom automatischen Freigabesystem abgelehnten abgeleiteten Datenpakete wurden aus dem Push entfernt. Ihre Ausgangsdaten waren bereits auf `origin/main` vorhanden; 896 daraus vollständig reproduzierbare Ausgaben wurden geprüft. Die Wiederherstellung ist im Projekt-README beschrieben.

- Alle neun Module besitzen mobil eine gemeinsame Orientierung und drei Ergebnisansichten. Kennzahlen bleiben erhalten. Hinweise und Verknüpfungen verwenden die tatsächlich sichtbare Bezeichnung „Aktuell → Raum & Zeit“; das richtige Regions-, Gemeinde-, Hafen- oder Flughafenfeld wird geöffnet und fokussiert.
- Die Auswahl bleibt beim Umschalten erhalten. Beispiel Duisburg: Relationstabelle und Diagramme, anschließend Jahreswechsel auf 2023 aus der Diagrammansicht, ohne Verlust von Region oder aktiver Ansicht. Ein echter Kartentipp auf Berlin aktualisiert die Auswahl, ohne automatisch zu den Relationen zu wechseln. Zurücksetzen auf Deutschland stellt den Auswahlhinweis wieder her.
- Kartenausschnitt und Zoom stimmen vor und nach dem Wechsel über Relationen und Diagramme exakt überein. Die von Leaflet sonst erzeugte Pixelrundung beim Wiedereinblenden wurde berücksichtigt. Diagramme werden nach dem Einblenden korrekt vermessen.
- Mobile Ansichten bei 393 × 852 Pixeln in allen neun Modulen, zusätzlich 320, 430, 768 und 900 Pixel Breite: genau ein Ergebnisbereich sichtbar, verborgene Bereiche nicht fokussierbar, kein horizontaler Seitenüberlauf. Pfeiltasten sowie Home/End funktionieren in der Registerleiste. Beim Vergrößern zum Desktop erscheinen alle Ergebnisbereiche wieder.
- Desktop: alle neun Module bei 1.479 × 912 und 2.119 × 1.272 Pixeln mit dem Stand vor der Änderung verglichen. Positionen und Abmessungen von Modulraster, Karten und Diagrammen bleiben innerhalb eines Pixels identisch. Die neue Navigationsleiste bleibt dort unsichtbar.
- Export aus der mobilen Kartenansicht: beide Diagramme bleiben auswählbar. Zusätzlich Excel heruntergeladen und mit openpyxl geöffnet: Kennzahlen, Quellenbogen, zehn Duisburger Relationen und beide Diagrammblätter vorhanden. Groot-Rijnmond: numerischer Wert 30.252,2 in 1.000 Tonnen bei Berichtsjahr 2024; die visuell verborgene Relationstabelle wurde vollständig übernommen.

**Prüfungen:** `validate_mobile_views.cjs`: 36 bestandene Fälle, keine unbehandelten JavaScript-Fehler. Zusätzliche Excel-Wiederöffnung, Frontend-Zusammensetzung, JavaScript-Syntax und UTF-8 geprüft. Die vorhandenen Karten- und Diagrammlayout-Prüfer wurden an die Register angepasst; die fachlichen Datenpipelines wurden nicht verändert.

Nachweise einschließlich Desktop-Ausgangsmaßen, Screenshots, Browserprotokoll und Excel-Datei: `C:/Users/paulh/.codex/visualizations/2026/09/05/01a0726d-16d5-7872-b94d-06e55ba1e171/Mobile_Ansichten_2026-09-06/`. Localhost auf Port 8000 bleibt aktiv.

## 10.23 Steckbrief: erweiterter Einstieg und Top 5 (07.09.2026)

**Status: lokal umgesetzt und geprüft; keine Veröffentlichung.** Die Nutzeranforderung umfasst eine strukturierte Zusammenfassung mit Güterstruktur, Bundesvergleich und Verkehrsprognose sowie fünf statt drei Beziehungen bei weiterhin funktionsfähigem PDF-Export.

- Kurzfazit mit acht Sätzen in drei Absätzen bei vollständiger Datenbasis. Nenner und Bezugsjahre entsprechen den Profilabschnitten. Gütergruppen insgesamt sowie die jeweils wichtigste Versand-/Empfangsgruppe werden genannt; nationale Anteile werden im selben Profiljahr verglichen. Beim Deutschlandprofil entfällt der Selbstvergleich. KV-Anteile bleiben nach Verkehrsträger getrennt.
- Zwei Relationslisten mit je fünf positiven Einträgen; Ist-Partner werden vor der Begrenzung über beide Richtungen zusammengeführt. Die separate Gütergruppenliste bleibt unverändert bei drei Gruppen.
- Prognose: P1 2040 gegenüber 2019, ausschließlich Landverkehr. Grenzfälle für Wachstum, Rückgang, unverändertes Niveau, Zielwert null sowie fehlenden/undefinierten/nullwertigen Basis- oder Zielwert geprüft. Ein gültiger Zielwert null ergibt −100 Prozent; fehlende Vergleichsbasis erzeugt keine Änderungsrate.
- Normales Chrome: Deutschland, Duisburg, Berlin und Bottrop mit echten lokalen Daten geprüft. Sichtbare Modal- und Güteranteile sowie Prognoseraten wurden gegen die JSON-Werte gerechnet. Duisburg: 108,2 Mio. t im Profiljahr 2024, 38,5 Prozent Binnenschiffsanteil, Prognose −10 Prozent gegenüber 2019. Berlin: Prognose +19,5 Prozent; Bottrop: −31,9 Prozent. Keine unbehandelten JavaScript-Fehler.
- Modulfilter für Tonnenkilometer, Versand und eine einzelne Gütergruppe verändern das vollständige Profil nicht. Druckknopf ruft weiterhin den Browserdruck auf. Mobile Kopfzeile bei 320 und 390 Pixeln ohne Überschneidung des langen Titels mit dem Druckknopf; scrollbare Zusammenfassung, beide Top-5-Listen und Quellen erreichbar. Rückkehr zum Desktop geprüft.
- Fünf PDFs (vier Profile und ein Export aus der mobilen Ansicht) erneut geöffnet: jeweils drei A4-Seiten, vollständiges Kurzfazit, alle Tabellenzeilen und Quellen, Text innerhalb der Seitenränder, keine beschädigten Unicode-Zeichen. Gerenderte Seiten und mobile Screenshots visuell geprüft; keine abgeschnittenen Inhalte oder Tabellenzeilen.

**Prüfungen:** `validate_steckbrief.cjs` (10 bestandene Prüfpunkte), `validate_steckbrief_pdf.py`, `validate_frontend_loading.cjs`, Frontend-Build, JavaScript-Syntax und UTF-8. Fachliche Rohdatenpipelines wurden nicht verändert oder neu gerechnet. Vorhandene nicht zugehörige unversionierte Dateien bleiben erhalten.

Nachweise: `C:/Users/paulh/.codex/visualizations/2026/09/07/01a07b4d-7ef3-7300-af07-a2f8e9283af2/Steckbrief/` (Browserprotokoll, PDFs, PDF-Prüfbericht und Seitenbilder). Vorschau auf Port 8000 bleibt verfügbar.


### Sprachliche Nachbearbeitung des Kurzfazits mit WBP Writing (07.09.2026)

Die Satzbausteine aus Abschnitt 10.23 wurden nach dem WBP-Stil für Web-/Produkttexte überarbeitet. Drei Absätze bleiben erhalten; zugunsten kürzerer Sätze sind es je nach Datenlage etwa acht bis zehn Sätze. Anteile stehen im Fließtext ohne Klammern. Artikel bei Verkehrsträgern, natürliche Anteilsbezeichnungen, die Unterscheidung von Binnenverkehr und externer Verbindung sowie gemeinsame Nennung identischer führender Gütergruppen verbessern den Lesefluss. Salden werden als „mehr Güter empfangen als versandt“ beziehungsweise umgekehrt beschrieben; Prognosen als höheres/geringeres Aufkommen gegenüber 2019. Datenbasis, Nenner und Rangfolge bleiben unverändert.

**Prüfung:** `validate_steckbrief.cjs` ergänzt sieben Formulierungsfälle (gleiche/verschiedene Gütergruppen, Ranggleichheit, nur Versand/nur Empfang, nullwertige und fehlende Richtungsdaten), prüft Klammerfreiheit sowie Berlin mit Binnenverkehr und Duisburg mit externer Verbindung. Erneuter Browservergleich für vier Profile und die mobile Darstellung; insgesamt elf bestandene Prüfpunkte ohne unbehandelte JavaScript-Fehler. `validate_steckbrief_pdf.py` prüft erneut fünf vollständige PDF-Exporte; jeweils drei A4-Seiten. UTF-8, Syntax und Frontend-Build geprüft. Lokale Umsetzung.

Nachweise: `C:/Users/paulh/.codex/visualizations/2026/09/07/01a07b4d-7ef3-7300-af07-a2f8e9283af2/Steckbrief_WBP_Text/`.


## 10.24 Analyseassistent: Terra-Probelauf und vorbereitetes Regelpaket (09.09.2026)

**Status: lokaler Erkundungslauf ausgewertet und Regeldateien vorbereitet; keine technische Server-, Modell- oder Portalimplementierung und keine Produktfreigabe.** Die Bearbeitung der 45 vorhandenen Testfälle erfolgte auf Nutzerauftrag mit GPT-5.6 Terra. Alle Erstantworten wurden geprüft. Für T19 und T31–T45 liegt zusätzlich ein frischer Kontrolllauf vor.

Der Erstlauf ergab 28 unauffällige Antworten, 13 Fälle mit Nacharbeit, drei mit fachlichem Fehler und eine unvollständige Testeingabe. Der 16-Fälle-Kontrolllauf ergab elf unauffällige Antworten, zwei mit Nacharbeit und drei mit fachlichem Fehler. Der aktuelle vollständige Lesesatz verwendet 29 Erst- und 16 Kontrollantworten: 29 unauffällig, elf mit Nacharbeit und fünf mit fachlichem Fehler. Dies ist keine einheitliche Benchmark-Erfolgsquote. „Unauffällig“ ist keine automatische fachliche Freigabe.

Im ersten Versuchsaufbau waren T19/T32 durch Zahlvorgaben beeinflusst; im dritten Paket wurden versehentlich Ausschnitte des ausgeschlossenen Katalogs sichtbar. Zudem nutzten Erstagenten teilweise Projekt-Memory. Diese Grenzen und die unvollständige Eingabe von T44 sind dokumentiert; die Erstantworten blieben erhalten. Der Kontrolllauf erhielt bereinigte Eingaben und begrenzten Quellenzugriff. Mengen, Klassifikationen, Quellenzeichen und Nenner wurden durch die Hauptinstanz nachgeprüft. Alle 15 eingefrorenen Referenzquellen blieben unverändert, sieben zusätzliche lokale Rohdateien/Handbücher wurden mit Prüfsummen dokumentiert.

Lokale Nachweise: [Ergebnisbericht](../../outputs/analyseassistent_terra_probelauf_20260909/ERGEBNIS_TERRA_PROBELAUF.md), [45 Antworten mit Prüfung](../../outputs/analyseassistent_terra_probelauf_20260909/ALLE_45_ANTWORTEN_MIT_PRUEFUNG.md) und [Abschlusskontrolle](../../outputs/analyseassistent_terra_probelauf_20260909/ABSCHLUSSKONTROLLE.json). Dateien unter outputs sind lokale Arbeitsergebnisse und nicht durch Git gesichert.

**Vorbereitetes Regelpaket:** [config/analyseassistent](../../config/analyseassistent/README.md), Version 0.1.0. Fünf Dateien enthalten Modellregeln, 26 deklarative Fachregeln, Verträge für alle 15 Fragetypen und Vorgaben zur Antwortprüfung und Laufzeitmessung. Alle 45 Testfälle sind zugeordnet. Die wesentlichen Fehler werden durch getrennte Fehlwertzustände, passende Nenner, verbindliche Binnenzählung, Quellenmetadaten und vorgeprüfte Aussagebausteine adressiert. Der Modellprompt benennt fehlende Daten, Aufbereitungslücken und Abruffehler getrennt; eine plausible Ersatzschätzung ist nicht zulässig.

**Strukturprüfungen:** JSON lesbar, UTF-8 und interne Verknüpfungen geprüft; 15 eindeutige Funktionsverträge mit vollständiger Zuordnung der 45 Testfälle; Abdeckung aller Fälle durch 26 eindeutige Fachregeln; Funktionsnamen zwischen Dokumentation und Konfiguration konsistent. Laufzeitstatus und alle Funktionen sind deaktiviert. Es wurden keine ausführbaren fachlichen Validatoren oder Datenfunktionen getestet, weil sie noch nicht implementiert sind.

**Nutzerpräzisierung zur Antwortzeit:** Die zunächst vorgeschlagenen fünf und zehn Sekunden wurden als feste Ziel-/Abbruchwerte zurückgenommen. In der Konfiguration bleiben Laufzeitwerte ausdrücklich offen. Zuerst reale Requesty-Laufzeiten einschließlich langsamer und gleichzeitiger Anfragen messen; danach Zielzeit, Wartehinweis und Höchstfrist getrennt festlegen. Vor späterer Aktivierung ist eine begründete technische Frist erforderlich. Keine Geschwindigkeitsmessung oder externe Modellabfrage in diesem Arbeitsschritt.

Dokumentationsverzeichnis und Roadmap verweisen auf das Paket. Der vollständige 45-Fälle-Umfang und die Beschränkung auf vorhandene Dashboard-/Rohdaten sind nachgeführt. Daten, Frontend und Pipelines bleiben unverändert; keine Bereitstellung auf dem Server.


### Wiederaufnahme und Aufbereitungsplanung (09.09.2026)

Nach gemeldetem Abbruch den gespeicherten Stand erneut geprüft: alle 23 im Artefaktmanifest erfassten Dateien stimmen mit ihren SHA-256-Prüfsummen überein; alle 45 Bewertungen und der 16-Fälle-Kontrolllauf sind vorhanden. Die Teilagenten sind abgeschlossen. Das fünfteilige Regelpaket enthält weiterhin 26 Regeln/15 Funktionsverträge, bleibt deaktiviert und enthält keine feste Fünf-/Zehnsekundenfrist. Ein beschädigter gespeicherter Terra-Lauf ist nicht nachgewiesen; die technische Ursache des gemeldeten Abbruchs wurde damit nicht ermittelt.

Neu angelegt: [Aufbereitungsplan für alle 45 Testfälle](../roadmap/ANALYSEASSISTENT_AUFBEREITUNGSPLAN.md) und [strukturierte Zuordnung](../roadmap/ANALYSEASSISTENT_AUFBEREITUNGSPLAN.json). Quellen-IDs, vorhandene Pfade, benötigte Aufbereitung, Regel-/Eingabegrenzen und Kontrollrechnungen sind je Fall dokumentiert. Quellpfade und Kopfzeilen ausgewählter SGV-/IWW-/MRTM-Dateien lesend geprüft; Monatsfelder vorhanden, Vollständigkeit konkreter Monatsreihen noch nicht freigegeben. SGV-Zeichensatz entsprechend aktiver Pipeline ausdrücklich berücksichtigen; Rohdateien nicht geändert.

Die Zuordnung ist Arbeitsplanung, keine umgesetzte Pipeline und kein bestandener Funktionstest. Bestehende Daten, Browserpakete, Programmquellen und Server wurden nicht verändert. Dokumentationsübersicht und Roadmap verweisen auf den neuen Plan.


### B01: separater lokaler Analysebestand umgesetzt (09.09.2026)

Datenstand `19ffa80c84ef939f75ed` ist nach 71 bestandenen Prüfungen über `data/analysis/b01/current.json` lokal aktiviert. 26 vorhandene Rohdateien, 2.615.459 Quellzeilen, 7.846.377 Kennzahlbelege, 1.495.344 Jahresrelations-/Kennzahlzeilen. Alle vergleichbaren OD-Mengen und tkm stimmen mit dem bisherigen Bestand überein; Quellen- und Ausgabeprüfsummen bestätigt. Alle 145.707 markierten VE7-Tonnenzeilen erhalten. Reale Referenzen T04/T05/T19/T20 sowie Fehlwert-, Null-, Quellenkonflikt- und Teilsummengrenzen geprüft. Führende Nullen und alphanumerische NST-Schlüssel geprüft. Lokale CLI-Abfrage Köln → Hamburg 2024 Straße erfolgreich: 67.757 t mit eingeschränkter Qualität.

Prüfskript: `scripts/validation/validate_b01_analysis.py`. Vollständiger Bericht: `data/analysis/b01/releases/19ffa80c84ef939f75ed/validation.json`; Quellenbeleg: `manifest.json` im selben Ordner. Der frühere Stand `5796b803720672575554` bestand einen synthetischen Qualitätskonflikt nicht und wurde nie aktiviert; die Korrektur ist im neuen Stand geprüft.

Freigabeumfang: separater lokaler B01-Bestand und exakte lokale Relationsabfrage. Keine vollständige Abnahme der 45 Assistentenfälle, keine Monatsvollständigkeits- oder Gebietsvergleichbarkeitsfreigabe, keine neue Dashboardabnahme, keine Server-/Requesty-Einbindung. Bestehende Dashboarddaten wurden nicht geschrieben. Die Qualitätskennzeichen werden im neuen Analysebestand erhalten; ihre Darstellung im bestehenden Dashboard bleibt gesondert zu prüfen. Schritte, Dateien, Reproduktion und offene Pakete sind zentral in [Roadmap Abschnitt 17](../roadmap/ROADMAP_ANALYSEASSISTENT_PORTAL.md#17-b01--umsetzung-und-zentraler-arbeitsstand-09092026) dokumentiert.


### Geplanter gebündelter Modelltest nach den Datenpaketen

Aktualisierte Nutzerentscheidung: B02–B07 zunächst vorbereiten, anschließend einen gebündelten Modell-Nachtest mit Systemprompt und überarbeiteten Daten über die 45 festgelegten Fälle durchführen. B01-Teillauf und paketweise KI-Nachtests entfallen. Fachliche Datenprüfungen bleiben Bestandteil jedes Pakets und benötigen keinen Modellaufruf. Verbleibende Voraussetzungen oder Datenlücken vor dem gemeinsamen Lauf ausdrücklich dokumentieren und ihren Umgang klären; nicht prüfbare Fälle sind nicht bestanden. Die Referenzen bleiben vom Modellkontext ausgeschlossen; Promptfassung, Datenstand und Modell werden dokumentiert. Reihenfolge und Bedingungen stehen zentral in [Roadmap Abschnitt 18](../roadmap/ROADMAP_ANALYSEASSISTENT_PORTAL.md#18-nächste-schritte-und-erneuter-ki-test). Status: geplant, keine neue Modellprüfung ausgeführt und keine zusätzliche Freigabe erteilt.


### B02: Monatsbestand und Quellenabdeckung lokal geprüft (09.09.2026)

Stand `027b7422159248cf7dd0`, abhängig von B01 `19ffa80c84ef939f75ed`, mit 112 bestandenen Prüfungen lokal aktiviert. 4.561.071 Monats-/Relations-/Kennzahlzeilen; 40 Quellen-Jahreskombinationen. Alle 25 Schienen-/IWW-Jahresdateien enthalten zwölf Monate; VE7 hat ausschließlich Jahreswerte. Sämtliche Monatssummen und Qualitätszähler gegen B01 geprüft; Zeilenzahlen und Tonnen je Quellmonat unabhängig aus allen Original-CSV bestätigt. Quellen-, Code-, Ausgabe- und Beschreibungsprüfsummen stimmen. Reale Magdeburger Reihe, unvollständige Einzelrelation und synthetische Fehlwert-/Nullbasis-/Spitzenanteilsfälle geprüft. Lokale CLI über den aktiven Stand erfolgreich getestet. Dashboard-OD unverändert.

Nachweise: `data/analysis/b02/releases/027b7422159248cf7dd0/validation.json`, `manifest.json` und `source_coverage.json`. Prüfer: `scripts/validation/validate_b02_analysis.py`. Quellenbefund: SGV-Beschreibung Seite 1 nennt ältere NUTS-Stände für 2016–2023, während die acht Dateiköpfe NUTS2024 ausweisen. Revisions-/Endgültigkeitsnachweis bleibt offen. Diese Grenzen sind maschinenlesbar dokumentiert; keine pauschale Freigabe harmonisierter Vergleiche und keine ungeprüfte Änderungsrate. Monatsabdeckung ist auf der konkreten Auswahl zu prüfen; fehlende Zeilen bleiben fehlend.

Freigabeumfang: lokale B02-Aufbereitung und begrenzte Zeitreihenabfrage mit sichtbaren Quellen-/Vergleichsgrenzen. Keine Freigabe aller 45 Modellfälle, kein KI-Aufruf, keine Veröffentlichung. Aktualisierung B01 → B02 und spätere serverinterne Bereitstellung in Datenaktualisierungsanleitung Abschnitt 13 dokumentiert; zentraler Arbeitsstand in Roadmap Abschnitt 19. Offene Gebiets-/Revisionsfragen bleiben bei der späteren fachlichen Fallabnahme zu berücksichtigen.


### B03: Schienen-Feinpositionen und KBA-Details lokal geprüft (09.09.2026)

Datenstand `421123fa003af03e5929` nach **193/193 bestandenen Prüfungen** lokal aktiviert; gehört unverändert zu B01 `19ffa80c84ef939f75ed` und B02 `027b7422159248cf7dd0`. Bestand: 3.495.186 monatliche Schienen-Detailzeilen (2016–2025) und 214.452 KBA-Kennzahlbelege aus 36 VD2-/VD3c-Dateien (2016–2024). Vier Referenzhandbücher und aktueller NST-/VP-Crosswalk gegen die tatsächlichen Felder geprüft. Quellen-, Code-, Beschreibungs- und Ausgabeprüfsummen bestätigt.

**Datenprüfung:** Sämtliche Schienen-Feinpositionen rekonstruieren B02-Monatsmengen und Qualitätszähler. Alle zehn SGV-Jahresquellen je Monat, Richtung, NST-Originalcode und allen drei Kennzahlen zusätzlich unabhängig aus CSV abgeglichen. Alle KBA-Belege auf Originalfeld, Originalzeichen, Richtung, Region, Klasse, Einheit sowie I/G geprüft; keine doppelten Klassenzellen. Numerische Aggregationstoleranz: maximal aus 0,00001 und 10⁻¹² des Vergleichswerts. Klassifikation 031→C1 sowie NST14/VP140→C6 und vollständiges Abteilungs-/C-Gruppenregister bestätigt.

**Fachliche Fälle:** Köln → Hamburg 2023/2024 mit 227.456/199.851 t, C1/C7 2024 mit 231/199.620 t; Gegenrichtung und Binnenzählung geprüft. Reale Monatslücke verhindert Jahresbewertung/Spitzenanteil. Nürnberg 2024 VD2-V, FT_I: 698.880,8 / 400.300,5 / 476.759,4 Fahrten; Entfernungsklassen bis 50 km, 51–150 km, mehr als 150 km. DEA2 in VD3c für beide Richtungen, beide Populationen und alle drei Kennzahlen mit jeweils 20 Positionen und unterdrückten Werten geprüft; keine vollständige Summe ausgegeben. Synthetische Fehl-/Null-/Qualitätsfälle, falsche Raumebene, unzulässige Straßenrelation, fehlende Regionen/Jahre und ungültige Parameter geprüft.

**Nachweise:** `scripts/validation/validate_b03_analysis.py`; vollständiger Bericht `data/analysis/b03/releases/421123fa003af03e5929/validation.json`, zugehöriges `manifest.json` und `data/analysis/b03/current.json`. Drei dokumentierte CLI-Beispiele über den aktiven Stand erfolgreich ausgeführt: Schienenrelation, Nürnberger Entfernungsklassen, DEA2-Empfang NST-20/G. Der bekannte DEA2-Teilwert wird ausdrücklich als `partial` ausgegeben. Aufbau mit temporärem Schreibzugriff unter `C:/tmp`; Zwischenverzeichnis nach Abschluss entfernt.

**Freigabeumfang:** ausschließlich lokaler B03-Bestand und begrenzte Datenabfragen. Keine harmonisierten Änderungsraten, kein Straßen-OD-Güterdetail, keine NST-20-Verfeinerung auf NUTS-3 und keine Leerfahrtenableitung. I/G betreffen deutsche Güterkraftfahrzeuge und dürfen nicht addiert werden. TON/TKM/FT ohne Skalierung; KM-Felder nicht erschlossen. VE12/VE13 bleiben die bestehende Grundlage für T16. Die Gebiets-/Revisionsgrenzen aus B02 bleiben wirksam. Keine neue Dashboard-, Modell-, Portal- oder Produktfreigabe. Bestehender Dashboard-OD blieb unverändert; kein Browser-Build und kein KI-Aufruf. Wiederholung in Datenaktualisierungsanleitung Abschnitt 14, zentraler Arbeitsstand in Roadmap Abschnitt 20; als Nächstes B04/B05.

### B04–B06: räumliche, nationale und Knotenabfragen lokal geprüft (09.09.2026)

**Freigabe nach Nachbesserung: lokaler Datenstand `ac45c399570d4ef97445` mit ausdrücklich begrenzter fachlicher Abdeckung; 199/199 Hauptprüfungen und 10/10 zusätzliche Kontrollen bestanden.** Aktiviert über `data/analysis/b0406/current.json`. Zusammengehörige B01-/B02-/B03-Stände, deren Ausgabedateien sowie die neuen Eingangs-/Ausgabeprüfsummen und alle sechs aktuellen Codefassungen bestätigt. Datenumfang und Dateien stehen zentral in Roadmap Abschnitt 21; Wiederholung in Betriebsanleitung Abschnitt 15. Vorgänger `c36ed9b0929ac02c25e2` bleibt erhalten.

**Geprüft:** Regionsverbünde innen/außen/eindeutig, Berührungszählung, unbekannte Werte, gleichrangige Räume, Duplikat-/Knotenabwehr, Ranggleichstände, kleine/fehlende/Nullbasis und Vergleichbarkeit. Duisburg/Magdeburg 2024: 108.215.313,5 / 23.180.902,5 t aus unverändertem D01; Straßensaldo Duisburg +4.236.410 t ohne Leerfahrtenableitung. Sämtliche übernommenen Regional-/Prognosefelder unverändert; VP-Ranking über 400 Gebiete: Hamburg, Köln, Ludwigshafen, Bremerhaven, München. Nationale Quellsummen nach Jahr, Verkehrsträger und Verkehrsbeziehung vollständig aus Original-CSV nachgerechnet. Schienentransit 2024: 13.622.343.988 tkm, rund 10,784 % des nationalen Schienennenners.

**Knotenprüfung:** Alle gespeicherten Luft-Jahreszellen auf Originalwert, Quellenzeichen, Partner und Land geprüft; Leipzig/Halle 2024, Versand ins Ausland: 59 positive veröffentlichte Relationen, Nenner 662.332,0 t unabhängig von Top-Begrenzung, OBBI mit Bahrain/BH. Alle Seehafen-Jahrgänge 2011–2025 je Quelle, Richtung und Kennzahl auf Summe, Zeilenanzahl, fehlende und nicht anwendbare Werte unabhängig aus CSV bestätigt; sämtliche Partnerpaare 2024 zusätzlich vollständig kontrolliert. Reale Duisburg-/Essen-Verbünde für alle drei Modi und ihre Qualitätszähler stimmen mit B01 überein. Hamburg 2024: 7.828.362,9 Container-TEU, 3.115 nicht anwendbare TEU-Leerfelder separat; keine unbekannten anwendbaren TEU-Felder dieser Auswahl.

**Neue Quellenbefunde:** T22 kann nicht wie ursprünglich angenommen als vollständiger nationaler tkm-Modal-Split freigegeben werden: sieben Straßen-Inlandsleistungsfelder 2024 sind mit `.` unbekannt gekennzeichnet. Die bekannten Werte ergeben 624.919.760.431 tkm, aber keinen vollständig belegten Nenner. Die Abfrage sperrt den vollständigen Split; Aufbereitungsplan MD/JSON berichtigt. Bei Seehafen-Gewichten bleiben leere Werte und der Widerspruch zwischen Feld `Guetergewicht` und der Beschreibung (`Tonnen`, Brutto-Brutto-Gewicht) ungeklärt. Bekannte Gewichtsteilsummen sind keine freigegebenen vollständigen Gesamtwerte. TEU ohne Containergröße sind dagegen laut Beschreibung S. 10 nicht anwendbar und werden gesondert gezählt.

**Nachweise:** `data/analysis/b0406/releases/ac45c399570d4ef97445/validation.json`, `partner_mapping_validation.json`, `manifest.json` und `source_contracts.json`; Prüfer unter `scripts/validation/validate_b0406_analysis.py` und `validate_b0406_partner_mapping.py`, zusätzliche Fälle in `check_b0406_regressions.py`. Die ausgeführte Prüferfassung steht jeweils als SHA-256 im Bericht. UTF-8/Syntax geprüft. Temporäre Arbeitsdateien bereinigt. Die Vorstufe `23cef5ddd65226c28dd7` wurde nicht aktiviert.

**Nachprüfung der Verbesserungen:** 49 zusätzliche Regressionstests innerhalb der Hauptprüfung bestanden. Fehlende, fehlgeschlagene, veraltete und widersprüchliche Partnerberichte verhindern eine Freigabe und lassen den vorherigen Verweis unverändert. Eine fehlgeschlagene Hauptprüfung sperrt ebenfalls. Erfolgreiche und wiederholte Aktivierung behalten die Prüfsummen beider Berichte und des Manifests. Alle drei Abhängigkeitsverknüpfungen werden einschließlich absichtlicher ID-/Hashkonflikte getestet. Hamburg, Versand 2024: 190 ausschließlich nicht anwendbare TEU-Partner statt 190 fälschlich unbekannter Relationen; gemeldete Null, fehlende Zeile und unbekannte Werte separat geprüft. Weitere reale Abfragen decken Regionsvergleiche und Salden in t/tkm, reguläre Flughafenwerte, Seehafenpartner, fehlende nationale Jahrgänge, Prognoserückgänge und lokale Parameterübergabe ab. Quellen und Zeilenanzahlen unverändert. Gemini prüfte den Vorgänger lesend; die korrigierte Fassung wurde lokal vollständig gegen Quellen und Funktionsregeln geprüft, nicht erneut durch Gemini.

**Grenzen der Freigabe:** Lokale Aufbereitung und begrenzte Abfragen, keine vollständige Abnahme aller 45 Modellfälle. B02-Gebiets-/Revisionsgrenzen, D01-Profilgrenzen, Luft-Veröffentlichungsschwellen und die Sperre der Flughafen-Flugzahlen 2025 gelten fort. T36 benötigt weiterhin einen bestätigten Hafen; B07 bleibt offen. Keine Änderung bestehender Dashboarddaten oder der Bedienoberfläche, keine Modell-/Requesty-Abfrage und keine Serverbereitstellung.

### B01–B03-Zweitprüfung und erneuerte Gesamtkette (09.09.2026)

**Aktueller, maßgeblicher lokaler Freigabestand:** B01 `dea0378af6f4f6dea076` mit 159/159 Prüfungen, B02 `cc36b3f63ef24d526897` mit 178/178, B03 `7deae62d547a876417ef` mit 201/201 sowie B04–B06 `603097102c408e95a15e` mit 199/199 Hauptprüfungen und 10/10 zusätzlichen Partnerkontrollen. Alle vier aktiven Verweise sind gesetzt; Vorgänger bleiben erhalten. Die Paketabschnitte darüber sind historische Prüfstände, keine zusätzlichen aktuellen Versionen.

**Unabhängige Zweitprüfung:** Gemini 3.8 Flash (High), `gemini-3.8-flash-high`, über den Skill `gemini-zweitpruefung` ausschließlich lesend im Plan-/Sandboxmodus. Prüfmaterial waren benannte B01–B03-Programme, Prüfer, Manifeste, Berichte und Dokumentation. Originalbefund: `outputs/gemini_b0103_20260909/BEFUND_ORIGINAL.md`; eigene Belegprüfung und vollständige Behandlung aller Hinweise: `AUSWERTUNG.md` im selben Ordner. Gemini prüfte statisch die Vorgänger; die korrigierte Fassung wurde anschließend lokal gegen Quellen und Funktionsregeln geprüft, nicht erneut durch Gemini.

**Belegte Korrekturen:** B02-Gesamtstatus bei fehlenden/teilweise vorhandenen Reihen; verständliche Eingabeablehnung statt Programmabbruch für Straßenprodukte mit `total`; strikte Jahresparameter; B03-Teilsumme bei ausschließlich unbekannten Schienenwerten bleibt unbekannt statt 0. Der letzte Fehler wurde durch die eigene ergänzende Gegenprobe gefunden. Keine automatische Auflösung des amtlichen NUTS-Widerspruchs und kein Wechsel vom durch AGENTS.md vorgegebenen temporären Arbeitsordner.

**Erweiterte Kontrollen:** B01 prüft jede Originalzelle aller drei modalspezifischen Kennzahlen einschließlich der 3.397 Rohzeilen außerhalb früherer Raumfilter und eindeutiger Belegschlüssel. B02 prüft Tonnenkilometer sowie Ladeeinheiten/Ladungsträger unabhängig je Quellmonat und enthält neun IWW-Abfragevarianten. B01/B02-Aufrufe wurden als echte Prozesse getestet; B03 zusätzlich für Schiene, VD2 und VD3c nach der tatsächlichen Aktivierung erfolgreich aufgerufen. Der vorgelagerte B03-Parser-/Abfragetest simuliert nur die noch nicht vorhandene Freigabedatei; diese Simulation ist kein Freigabenachweis. Neue Prüfungen sind in `scripts/validation/check_b0103_regressions.py` eingebunden.

**Integrität und Wiederholung:** B01/B02/B03-Datenartefakte sind bytegleich zu ihren Vorgängern, bestätigt anhand sämtlicher Ausgabeprüfsummen. Geändert sind Abfrage-/Prüfcode und dessen Versionsbindung. B01/B02/B03-Manifeste binden jetzt auch Prüfer und lokale Aufrufe; die Verweise enthalten Manifest- und Prüfberichtprüfsummen. Der neue B04–B06-Stand bindet exakt die oben genannten Vorstufen; seine Quellen-/Funktionsprüfung wurde vollständig wiederholt. Keine Rohdaten-, Dashboard- oder Serveränderung. Syntax, UTF-8 und abschließende Manifest-/Verweisbindung werden vor Übergabe kontrolliert; temporäre Aufbaubestände bleiben außerhalb des Projekts und werden bereinigt.

**Grenzen:** Freigabe gilt für lokale Daten und Abfragefunktionen, nicht für den gebündelten 45-Fälle-Modelltest. B07 und Server-/Modellanbindung bleiben offen. Der Terminalfall „Kreis plus Nachbarkreise → Hamburg/Nordseeküste mit Gütern“ ist in Roadmap Abschnitt 22 als zusätzliche Anforderung dokumentiert. Noch keine geprüfte Nachbarschafts-/Küstenliste, Listen-zu-Listen-Schnittstelle oder automatische Rückfragefunktion. Relationsgüter für Schiene/Binnenschiff sind vorhanden; Güter der konkreten Straßenrelationen und Terminalpotenzial sind damit nicht belegt.


### Lokale KV-Terminalebene und Fragenkontingent-Vorschau (10.09.2026)

**Prüfumfang:** zusätzliche Standortebene und lokale Kontingentanzeige. Keine neue Freigabe statistischer Daten, der B01–B07-Kette oder einer Server-/KI-Anbindung.

**Daten:** `validate_terminals_quota.cjs` gleicht alle 1.468 ausgegebenen Standorte vollständig mit der Rohdatei ab: identische Namen und Koordinaten, Funktion nach dem Quellfeld `kategorie`, ausschließlich `name` und `function` als Ausgabeattribute und passender Quell-SHA-256. 756 Schiene/Straße, 285 Wasserstraße/Straße, 427 trimodal. 140 Containerdepots und 15 stillgelegte Anlagen ausgeschlossen. Rohdatei unverändert. Kein Abgleich der gegenwärtigen Betriebsbereitschaft mit externen Terminalbetreibern.

**Kontingent:** 0 → 50, Sperre des 51. Versuchs, Monatsgrenze Europe/Berlin einschließlich UTC-Abweichung, Monatsrücksetzung, Erhalt gültiger gespeicherter Zähler, fehlerhafte/ungültige Speicherwerte und blockierter Browserspeicher bestanden. Die Oberfläche zählt nur lokale Testfragen, keine echten Lizenzverbräuche. Eine leere Eingabe erhöht den Zähler nicht; in der Browserprüfung blieb er bei 1 von 50. Neuladen erhielt den Teststand.

**Browser:** Lokale Ansicht im Codex-Browser bei Desktopbreite und 390 × 844 Pixeln geprüft. Terminalschalter zunächst aus; 1.468 Marker nach Einschalten, 0 nach Ausschalten. Zustand bleibt beim Modulwechsel erhalten. Hamburg 2024: 20 Verbindungselemente bei ausgeschalteten Terminals; 1.468 Terminalmarker bei ausgeschalteten Verbindungen; KV-Schienenkennzahl bleibt jeweils 26,6 Mio. t. Per Klick geöffnetes bimodales KLV-Terminal Salzgitter und per Enter geöffnetes trimodales Hafen Braunschweig Containerterminal mit korrektem Inhalt geprüft. Linkziel, neues Fenster und rel-Absicherung kontrolliert. Intermodal-Map-Adresse über die offizielle SGKV-Seite bestätigt. Vollständiger Popup-Rahmen nach Korrektur der Abstände am Desktop bestätigt; auf der niedrigen mobilen Karte wird der Inhalt begrenzt und scrollbar, Rahmen innerhalb der Karte. KI-Zähler und Balken am Desktop und mobil visuell geprüft. Hover ist implementiert; der automatisierte Browsernachweis betrifft die angeklickte beziehungsweise per Tastatur geöffnete Information.

**Technik:** Frontend-Build, `node --check js/app.js`, `validate_terminals_quota.cjs` und bestehender Prüfer `validate_frontend_loading.cjs` bestanden. Quellen-/Dokumenttexte UTF-8 eingelesen; bestehende, nicht zugehörige Änderungen erhalten. Ergänzte Betriebs-/Build-Anweisungen dokumentieren die neue Ausgabedatei. Die abschließende Nutzer-Sichtprüfung am Localhost steht aus.


### Nachprüfung des Nutzerfeedbacks: Terminals und Kontingent (10.09.2026)

Aktuelle Terminalebene: 213 ausschließlich deutsche Standorte nach `iso2 == DE`; vollständiger Quellvergleich mit `validate_terminals_quota.cjs` bestanden (109 Schiene/Straße, 13 Wasserstraße/Straße, 91 trimodal). Quellenwerte und Koordinaten unverändert, minimale Ausgabeattribute erhalten. Vorgängerausgabe gesichert. Frontend-Build, JavaScript-Syntax und vorhandene Kontingent-Grenzprüfungen bestanden.

Browserkontrolle: 213 kleine blaue Rechtecke und passender Legendeneintrag nach Einschalten, jeweils 0 nach Ausschalten. Schalterhinweise wechseln korrekt zwischen „Terminals anzeigen“ und „Terminals ausblenden“; weißer Hinweis sichtbar, Hover-Regeln für beide Zustände vorhanden. Popup ElbePort Wittenberge zeigt Titeltrennlinie, Funktion und durch eine zweite Linie getrennten kleineren/kursiven SGKV-Verweis. Der Fragenzähler steht mit 58 × 3 Pixel Balken direkt unter dem Eingabefeld; keine dauerhaft sichtbare Kontingent-Vorschauzeile. Fragezeichen-Hinweis am Desktop und bei 390 × 844 Pixeln geprüft, mobile Sichtprüfung bestanden. Daten-/Lizenzlogik unverändert; weiterhin keine Server- oder KI-Freigabe.


### Nachprüfung: abgeschnittene Hinweise und überlappende Kopfzeilen (10.09.2026)

**Befunde behoben:** Kontingenthinweis konnte am unteren Dialogrand abgeschnitten werden; der Terminal-Hinweis blieb nach Mausbedienung durch Fokus geöffnet; Informationssymbole konnten bei schmalen Diagrammkarten in Status-/Dynamikschalter ragen.

**Browsernachweis:** 63 Kopfzeilenkontrollen ohne Überschneidung und ohne über den Kopfzeilenrahmen hinausragende Titelteile/Bedienelemente. Breiten 1.366, 1.537, 1.767 und 2.119 Pixel; Übersicht, Straße, Schiene, Binnenschiff, See, Luft und KV, zusätzlich Status-/Dynamikvarianten bei 1.366/1.537/2.119. Prognose ebenfalls aufgerufen, dort keine passende Umschaltkopfzeile. KV-Dynamik separat bei 390 × 844 ohne Überschneidung oder Randüberlauf bestätigt.

**Hinweise:** Nach tatsächlicher Zeigerbedienung und Verlassen des Terminalknopfes bleibt dieser fokussiert, der Hinweis ist aber verborgen (`hover=false`, `pointerFocus=true`, `visibility=hidden`). Anschließende Tastatureingabe entfernt die Zeigermarkierung und zeigt den Hinweis wieder (`focus-visible=true`). Der Kontingenthinweis liegt bei 1.537 × 1.272 sowie 390 × 844 vollständig innerhalb des Dialogrechtecks und oberhalb des Zählers; beide Darstellungen visuell geprüft.

**Technik/Grenzen:** Frontend neu erzeugt, JavaScript-Syntax geprüft; bestehende Terminal-/Kontingentgrenzprüfung bestanden. Reine Oberflächenkorrektur, keine Änderung an Quelldaten, Statistiken, Lizenz- oder Modellanbindung. Temporäre Browsergrößen nach Prüfung zurückgesetzt.

### Analyseassistent: erste lokale Anwendungsschicht und B07 (10.09.2026)

**Prüfstand:** 22/22 automatisierte Laufzeittests bestanden. Nachweis: `outputs/analyseassistent_runtime_20260910/validation.json`, gebunden an die dort bezeichneten Programmprüfsummen. Keine externe KI in diesen Prüfungen und keine 45-Fälle-Fachabnahme. Der einzelne Duisburg-Aufruf ist zusätzlich unter `outputs/analyseassistent_runtime_20260910/balance.json` gespeichert. Der zusätzliche echte HTTP-Test bestätigt anonym 401, berechtigt 200 mit Datenantwort und genau einer Kontingentbelastung sowie 409 bei wiederholter Anfragekennung ohne erneute Belastung; temporärer Loopback-Server anschließend beendet. Ein weiterer Test verhindert, dass ein ausdrücklich genannter Relationspartner fälschlich als widersprüchliche Fokusregion abgelehnt wird.

Geprüft sind insbesondere zusätzliche/unerlaubte Parameter, boolesches Jahr, gefälschte Kontextangaben, falscher Raum, widersprüchliches Jahr, vertauschte Quelle/Ziel bei Pfeilangabe, unzulässiger Modellendpunkt, parallele Basic-Reservierungen, doppelte Anfragekennung, Freigabe nach Fehler, Paketwechsel, Europe/Berlin-Monatsgrenze, entzogenes Testrecht und Ablehnung browserseitiger Identitätsfelder/fremder Anfrageherkunft. Reale Datenfälle: Duisburger Straßenversand 26.371.111 t, Empfang 22.134.701 t und Saldo +4.236.410 t; gesperrte nationale Anteile bei unvollständigem T22-Nenner; B07 mit fehlendem Vorjahresmonat. Simulierte Modellphasen belegen das tatsächliche Laden des Systemprompts und den Erhalt von Tabellen/Quellenhinweisen bei ungültiger oder ausgefallener Modellauswahl. Simulationen sind keine Requesty-Qualitäts- oder Geschwindigkeitsmessung.

**B07-Datenprüfung:** 23.685 Zeilen aus den 24 vorhandenen Berliner Monats-/Richtungsdateien, August 2025 bis Juli 2026. AGS als achtstelliger Text, tatsächlicher Quellmonat, Richtung, Fokusgemeinde, Relationszahl, eindeutige gerichtete Relationen und nichtnegative ganzzahlige Fahrtenwerte geprüft. Zwölf Binnenwerte zwischen Quelle/Ziel identisch. Manifest und Bericht unter `data/analysis/b07/releases/93390e3aeb43d8f8b08845c8/`; Aktivierung über `current.json`. Kein Vorjahresmonatspaar vorhanden. T38 daher nicht numerisch bestanden. Kein externer Abruf und keine behauptete neue Vollständigkeitsprüfung beim Anbieter.

**Zugangstest:** Nutzerschlüssel lokal DPAPI-verschlüsselt abgelegt. Einlesen und `GET /models` über `https://router.eu.requesty.ai/v1` erfolgreich; konfigurierte Kennung `vertex/gemini-3.7-flash@eu` vorhanden. Keine Fachfrage und kein Projektbeleg versendet. Key-Inhalt nicht ausgegeben. Der erfolgreiche Zugriff ist keine Bestätigung aller Requesty-Datenschutz-/Aufbewahrungseinstellungen oder der strukturierten Fachantworten.

**Grenzen:** Zwölf begrenzte Adapter sind implementiert, nicht sämtliche fünfzehn fachlichen Fragetypen samt Kombinationen abgenommen. Der 45-Fälle-Katalog ist getrennt vorbereitet, die vollständige Ausführung noch gesperrt. SQLite-Kontingent ausschließlich lokaler Prototyp; PostgreSQL-Schema nicht angewendet, Hanko-/Portalanschluss und Benutzerverwaltung offen. Kein Browseranschluss an die neue API, keine Portalumschaltung, keine Produktionsänderung. Betriebsanleitung: `docs/betrieb/ANALYSEASSISTENT_LOKALER_PILOT.md`.

**Vorbereitender Kataloglauf:** `outputs/analyseassistent_runtime_20260910/preflight01/report.json` führt alle 45 Fälle; sieben strukturierte Adapteraufrufe ausgeführt, 38 Fallverträge noch nicht ausgeführt, null Modellaufrufe, keine fachliche Gesamtfreigabe. T19 zeigte eine unnötige Rückfrage durch die Partner-/Fokusverwechslung. Nach Korrektur gezielt erneut ausgeführt: `T19_corrected.json`; der historische Vorbericht bleibt unverändert. Technische Ausführung ist nicht gleich vollständige fachliche Abnahme des jeweiligen Falls.

### Analyseassistent: zusätzliche Profilfunktionen und HTTP-Korrektur (10.09.2026)

**Aktueller Nachweis:** `outputs/analyseassistent_runtime_20260910/profiles_validation_httpfix.json`, 28/28 Prüfungen bestanden, null externe Modellaufrufe, Programmprüfsummen im Bericht. Drei zusätzliche Adapter für Regionsprofil, regionalen Modal Split und getrennten Ist-/VP-Vergleich. Bestehende B01–B06-Programme und Datenstände unverändert.

Reale Referenzen: Duisburg 2024 insgesamt 108.215.313,5 t, Saldo −17.549.997,9 t, modale Anteile gerundet 44,8/16,7/38,5 %. Empfangsnenner separat 62.882.655,7 t. VP-Gesamtsummen 115.374.997 t im Basisfall und 103.871.423 t im Zielbild, Änderung gerundet −10,0 %. Ist-Jahre 2019 und 2024 werden mit eigener Quellenkennung und ohne Ist-zu-VP-Rate ausgegeben. Fehlendes Jahr liefert keine Null; unvollständiger, widersprüchlicher oder nullwertiger Modalnenner liefert keine Anteile. Leere, doppelte und zu umfangreiche Jahreslisten sowie boolesche Jahre werden zurückgewiesen.

Die Vorprüfungen `profiles_validation.json`, `profiles_validation_final.json` und `profiles_validation_confirmed.json` bleiben als Fehlernachweise erhalten: zuerst eine unnötig genaue falsch angesetzte Testreferenz, danach wiederholter Verbindungsabbruch beim unangemeldeten lokalen HTTP-Aufruf. Nach Korrektur konsumiert die WSGI-Anwendung kleine deklarierte Anfragekörper vor einer frühen Ablehnung. Die vollständige abschließende Prüfung bestätigt wieder 401 für anonymen Zugriff, 200 mit einmaliger Belastung für berechtigten Zugriff und 409 ohne Doppelbelastung bei Wiederholung.

**Katalog:** `outputs/analyseassistent_runtime_20260910/preflight03/report.json`: alle 45 Fälle verzeichnet, elf strukturierte Aufrufe abgeschlossen, neun `ok`, T22 und T35 `partial`, 34 nicht ausgeführt. Der frühere `preflight02` hatte zusätzlich einen Windows-Zeichencodierungsfehler bei der Erfassung der Unterprozessausgabe; der Runner setzt nun ausdrücklich UTF-8. Keine automatische fachliche Abnahme aus den Ausführungsstatus ableiten. Vollständiger Modelltest, verbleibende Fallverträge, PostgreSQL-/Portalanschluss und Testdeployment offen. Das vorherige lokale Übergabepaket enthält die neuen Programme noch nicht.

### Analyseassistent: Relations- und Quellenjahresprüfung (10.09.2026)

**Abschließender Lauf:** `outputs/analyseassistent_runtime_20260910/relations_validation_verified.json`, 40/40 lokale Prüfungen, null externe Modellaufrufe; Programme und Tests per SHA-256 gebunden. Der Zwischenlauf `relations_validation02.json` enthält einen Fehler im synthetischen Testaufbau (DuckDB-COPY-Ziel lässt sich dort nicht als Parameter übergeben); nach korrekt maskiertem SQL-Literal wurde auch dieser Test ausgeführt. Keine Fehlernachweise überschrieben.

**Reale Befunde:** Hamburg 2024 externe Straßenpartner: vollständiger veröffentlichter Nenner 55.473.138 t, davon 21.167.732 t in OD-Aggregaten mit eingeschränktem Aussagewert; Top fünf IDs DE933, DEF0D, DEF0F, DEF06, DE929. Duisburg → Magdeburg Binnenschiff 1.947 t, Gegenrichtung 1.189 t; fehlende Straße/Schiene bleiben `missing_row`, nicht null. Köln → Hamburg Schiene 2024: C1 231 t, C7 199.620 t, C2–C6 ohne Nullnachweis; bekannte veröffentlichte Feinpositionen 199.851 t. Nationaler Schienentransit 13.622.343.988 tkm, Nenner 126.319.807.860 tkm, gerundet 10,784 %. Diese Werte und Quellenkennzeichen sind jetzt in der Antwortausgabe nachgewiesen.

**Quellenjahre:** Alle zehn Magdeburger Schienenwerte 2016–2025 gegen die festgehaltenen D01-Referenzen geprüft. Keine harmonisierte Änderungsrate oder Ursachenbehauptung. Duisburger Straße 2025 hat kein Quellenjahr: technische Dashboard-Null wird in der Anwendungsschicht zu unbekannt; sämtliche 2025-Modalanteile bleiben gesperrt. Dasselbe gilt im Regionsvergleich. Vorhandene Schienen-/IWW-Werte bleiben sichtbar. D01-Dashboarddaten selbst unverändert.

**Weitere Grenzen:** Leipzig/Halle 2025 1.390.729,8 t verfügbar, Flugzahl wegen dokumentiertem Quellenwiderspruch nicht verfügbar. Nürnberger VD2-Lastfahrten 698.880,8 / 400.300,5 / 476.759,4, Population I und Fahrzeugabgrenzung erhalten. Synthetischer Partnerfall A/B/C/D (300/200/200/10) bestätigt Top 2 mit Ranggleichheit 1/2/2 und Nenner 710; zusätzlicher unbekannter Partner sperrt Anteile. Synthetische Werte sind keine neuen realen Datenbelege.

**Fragen-/Auswahlprüfung:** Benannte VP-Szenarien widersprechen nicht dem separat bestätigten Ist-Jahr; abweichende Ist-Jahre und abweichende Jahreslisten werden abgelehnt. Die optionale Antwortphase erhält Frage und geprüfte Parameter sowie alle belegten numerischen Aussagen. Auswahl weiterhin maximal vier Aussagen, unveränderte Quellen, Tabellen und Einschränkungen. Kein Zugriff auf Sollantworten.

**Katalogvorlauf:** `preflight04/report.json` enthält alle 45 Fälle, davon 21 technisch abgeschlossen (14 `ok`, sieben `partial`), 24 nicht ausgeführt, null Modellaufrufe. Noch keine fachliche Gesamtfreigabe und kein echter Requesty-Test. Die abschließend ergänzten Güteranteile und vollständigen Aussagekandidaten sind im Laufzeitbericht geprüft; historische Katalogausgaben wurden nicht neu beschriftet oder überschrieben. Portal-/PostgreSQL-Anschluss, Benutzerverwaltung, Browseranbindung und Testdeployment bleiben offen. Das vorhandene Übergabepaket ist veraltet.

### Analyseassistent: D01-Güterfelder, KV und Quellenhinweise (10.09.2026)

**Datenbindung:** Separater Stand `data/analysis/assistant_support/releases/f8f8949c0654f9a42d4e5e94/`, aktiviert über `current.json`; Manifest, Prüfbericht und beide Datendateien per SHA-256 verbunden. Abhängigkeiten auf B01, B03 und B04–B06 geprüft. 3.984 vollständige Projektionen der benötigten D01-Originalprofilfelder; Originaldatei muss dem bereits in B04 gebundenen Hash entsprechen. 34.270 KV-Kennwertdatensätze aus 25 B01-Quellfassungen, jeweils Zeilenzahl und Quellhash geprüft. Die 27 Eingänge (D01, bestehendes KV-Dashboardpaket, 25 Rohdateien) wurden nach dem Aufbau erneut geprüft, keine Änderung. Zwei zusätzliche Datendateien zusammen 19.355.187 Bytes; keine Rohdatenkopie im Browserbereich.

**KV-Prüfung:** 32.296 Kontrollen gegen bestehende Dashboardkennwerte. 140 enthalten dokumentierte, betragsgenau belegte Differenzen durch die geänderte Behandlung unbekannter Zielräume. Beispiel Frankfurt am Main, IWW-Versand 2016: bekannte Gegenräume 377.969.860,8 tkm; bisheriger Dashboardwert 378.290.660,8 tkm enthält weitere 320.800 tkm mit unbekanntem Zielraum. Unabhängige lokale SQL- und CSV-Auswertung bestätigten den Wert für bekannte Gegenräume. Die früheren fehlgeschlagenen Aufbauversuche wurden vor Anlage/Aktivierung eines Support-Stands beendet. Die freigegebene Fassung bewahrt unbekannte Gegenräume separat auf und beschreibt die Unterschiede; Dashboarddateien unverändert.

**Kennwertregeln:** Vollständige Kennzahlen erfordern zwölf beobachtete Monate und keine unbekannten maßgeblichen Werte. Fehlende Ladeeinheitenkennung wird nicht als sicherer Nicht-KV-Verkehr interpretiert. Regionaler externer Versand/Empfang ohne Binnen und nur mit bekanntem Gegenraum; regional all zählt berührende Quellzeilen einmal einschließlich unbekanntem Gegenraum. National all zählt jede Quellzeile einmal. Schiene und Binnenschiff bleiben nicht additiv. Keine Harmonisierung von Gebietszeitreihen und kein Nachweis von Terminalauslastung oder Verlagerungspotenzial.

**Laufzeit:** `outputs/analyseassistent_runtime_20260910/support_validation01.json`, 48/48 Prüfungen bestanden, null externe Modellaufrufe. Duisburg Straße 2024: sieben Gruppen je Richtung; Summe Versand 26.371.111 t und Empfang 22.134.701 t, Rangfolgen und Anteile geprüft. Straße 2025 und gewünschte NST-20-Profilaufteilung liefern keine Ersatznullen. KV Deutschland 2024: Schiene 99.853.065 t, Binnenschiff 16.738.676,4 t getrennt; Duisburg externer Schienenversand 4.422.816/9.194.861 t = 48,10 %. Ein synthetischer unbekannter KV-Zähler sperrt den Anteil. Klassifikation 031→C1, NST14/VP140→C6 mit Textcodes aus gebundenem Crosswalk geprüft; außerfachliche Kosten-/Umwelt-/Kapazitätsfrage enthält keine erfundenen Zahlen.

**Grenzen:** D01-Straßen-Güterkennzeichen weiterhin nicht aus Rohquellen nacherschlossen; keine zusätzliche Quellenqualitätsfreigabe. Feste Methodikantworten ersetzen keine konkrete Datenabfrage. 30 von 45 Fällen sind als prüfbare Ausgangspunkte zugeordnet; 15 Fallverträge beziehungsweise Kombinationen offen. Katalogvorlauf `preflight05/report.json`; technische Ausführung ist keine fachliche Abnahme. Kein echter Modelltest, Portalanschluss oder Testdeployment. Neuerstellung des veralteten Übergabepakets vor späterer Übergabe erforderlich.

### Analyseassistent: echter 45-Fälle-Modelllauf und Nachprüfung (10.09.2026)

**Vorbereitung:** 25 begrenzte Adapter; 32 konkrete Datenabfragen und 13 bewusst unvollständige Eingaben. 52/52 lokale Tests vor Modelllauf (`outputs/analyseassistent_runtime_20260910/catalog_contract_validation_final.json`); Freigabe für Evaluation mit `model_gate01.json`, getrennte Sollreferenzen. `preflight06/report.json` ist der lokale Vergleich für die 32 konkreten Fälle. Synthetische Rechenkontrollen ersetzen keine reale Gebiets-/Revisionsvergleichbarkeit.

**Modelllauf:** `requesty45_run01/report.json` im selben Ausgabeordner: 45 ausgeführte Fälle, 75 Aufrufe, Modell `vertex/gemini-3.7-flash@eu`, EU-Endpunkt. Ablauf 10:26:22–10:34:24 UTC. Verwendeter Systemprompt und Datenstand je Ergebnis per SHA-256 beziehungsweise Kennung dokumentiert. Nur Fragen, bestätigter Kontext, Funktionsschemata und öffentliche Verkehrsbelege wurden übertragen; keine Sollantworten, Portalidentitäten oder Zugangsschlüssel in Modellnachrichten. Die anfängliche automatische Ablehnung wurde nach Prüfung der konkreten Nachrichten und der bestehenden Nutzerautorisierung aufgehoben; der erneute identische Laufantrag wurde genehmigt.

**Ergebnisabgleich:** `requesty45_review02.json`: 42 Fälle bestehen Routing-/Datenkontrollen, drei benötigen Nacharbeit. T13: `not_available`, fehlende Ist-Änderungsranking-Funktion. T30: unvollständige Modellantwort; damaliger Transport speicherte weder genauen Abbruchgrund noch Verbrauch dieses Aufrufs. T44: `explain_scope/source_flags` statt konkreter Schienenabfrage, von der Parameterprüfung abgefangen. Zahlen, Tabellen, Quellen und Hinweise der erfolgreich zugeordneten konkreten Fälle stimmen mit dem lokalen Vergleich überein; dies ist keine unabhängige Vollständigkeitsprüfung aller fachlichen Antworten. Verbrauchssumme 408.047 Tokens nur für die 74 protokollierten Aufrufe mit Verbrauch; ein Aufruf fehlt. Median der Fallzeiten 8,765 Sekunden, Maximum 13,094 Sekunden; diese Messung umfasst nicht die vorgelagerte Dateninitialisierung je Prozess.

**Korrektur und Nachprüfung:** Präzisierter allgemeiner Reproduktions-/Rückfragehinweis im Systemprompt; begrenzte Fehlerdiagnose für nicht abgeschlossene Modellantworten ohne freie fremde Fehlertexte. `post_requesty_validation01.json`: 54/54 lokale Tests, keine externen Aufrufe. Neue Tests prüfen einen simulierten Tokenabbruch einschließlich Verbrauch, keine Wiederholung sowie Ausschluss fremder Inhalte und nichtnumerischer Diagnosedaten. Anschließend ausschließlich T30 und T44 mit Originaleingaben erneut über Requesty ausgeführt: drei Modellaufrufe. `requesty_targeted02/review.json` bestätigt Rückfrage ohne erfundene Zahlen für T30 und vollständige Übereinstimmung der T44-Fakten, Tabellen, Quellen, Parameter und Hinweise mit dem lokalen Vergleich. T44: C1 231 t, C7 199.620 t, veröffentlichte Feinpositionen 199.851 t. Der ursprünglich unvollständige T30-Aufruf bleibt als Befund erhalten; seine Ursache ist rückwirkend nicht nachgewiesen.

**Freigabegrenze:** Keine vollständige fachliche 45-Fälle-Abnahme. T13, T35-Ländernamen, T43-Gebietszahlen sowie Fachprüfung aller Kurzfassungen bleiben offen. Die zwei Nachprüfungen belegen keine erneute Evaluation der anderen 43 Fälle mit dem geänderten Prompt. T30s Rückfrage bietet noch kein alternatives Prognoseszenario. B07 ohne Vorjahresmonatspaar. PostgreSQL-Adapter und Schema sind lokale Entwürfe ohne echte Datenbankprüfung; Hanko-/Portalanschluss, Administration, Dashboard, Browserprüfung und Testdeployment offen. Keine Produktionsänderung. Altes Übergabepaket weiter veraltet.

**Abschließende Freigabeprüfung:** `outputs/analyseassistent_runtime_20260910/post_requesty_validation02.json`, 55/55 lokale Tests bestanden. Die gebundene Dateiliste umfasst jetzt ausdrücklich Systemprompt, Fachregeln, Laufzeitprogramme, Testtreiber und Freigabeprüfer. Fehlende Promptbindung und geänderter Prompthash werden abgelehnt; der Runner prüft zusätzlich den Referenzhash. Bereits vorhandene Gate-Ausgabedateien werden vor einer Änderung der Eingaben abgelehnt. Diese Nachprüfung erzeugt keinen weiteren Modellaufruf und keine neue fachliche Freigabe. Ältere Gate-Dateien bleiben historische Nachweise.

### Analyseassistent: lesbare Testantworten und PostgreSQL-Kontingente (10.09.2026)

**Ergebnisübersicht:** `outputs/analyseassistent_runtime_20260910/lesebericht01/index.html` enthält 45 eindeutige Testkarten mit originalen Fragen, Testauswahl, ausgegebenen Kurzantworten, Hinweisen und Tabellen. T30/T44 zeigen die Nachprüfung und behalten die ursprüngliche Ausgabe aufklappbar. Vor Erstellung 47 Ergebnisprüfsummen gegen Lauf- beziehungsweise Nachprüfungsberichte kontrolliert. Zusätzlich Markdown-Lesefassung und Manifest. Suche nach T44, Antwort und Tabelle im Browser geprüft; Umlaute sichtbar korrekt. Die Anzeige übersetzt Datenzustände, die unveränderte vollständige Ausgabe bleibt separat einsehbar. Keine neue Modellanfrage und keine Änderung der ursprünglichen Prüfergebnisse.

**Kostenhinweis des Nutzers:** Requesty-Dashboard zeigt 78 Requests und insgesamt 0,51 USD. Dies stimmt zahlenmäßig mit 75 Aufrufen im ersten Lauf plus drei gezielten Nachprüfungen überein. Kosten aus Nutzerangabe, nicht durch eigenen Dashboardzugriff verifiziert. Lokale Tokensumme wegen eines früheren Abbruchs weiter unvollständig; keine Hochrechnung als Tarif- oder Monatskostenfreigabe.

**Echte lokale Datenbankprüfung:** `postgres_validation02.json` im selben Ausgabeordner, 9/9 Tests bestanden. Eigene PostgreSQL-13.3-Instanz ausschließlich auf 127.0.0.1, zufälligem Port, zufälligem Testpasswort und eigenem C:\tmp-Cluster. Treiber psycopg 3.2.10 gemäß Portal-Requirements. Alle acht tatsächlichen Portal-Migrationen 001–008 und das zusätzliche Schema geladen; Dateien per SHA-256 festgehalten. Ausschließlich künstliche Identitäten, keine Portalverbindung und keine Modellaufrufe.

**Nachweise:** Zwölf gleichzeitige Basic-Reservierungen lassen genau fünf zu; acht gleichzeitige identische Kennungen reservieren einmal. Abweichender Inhalt unter derselben Kennung wird abgelehnt. Belastung und Freigabe erfolgen einmal; Freigabe erzeugt keinen erneuten Modellversuch unter derselben Kennung. Wechsel Basic→Premium→Basic erhält den Verbrauch. Gesperrte/abgelaufene/zukünftige Rechte, deaktiviertes Paket oder Werkzeug und fehlendes Werkzeugrecht werden abgewiesen. Ein im Vormonat reservierter Auftrag bleibt dort belastet und verbraucht kein neues Monatskontingent. 20 Versuche einschließlich Freigaben begrenzen weitere kurzfristige Anfragen. Erzwungener Transaktionsfehler hinterlässt keine Reservierung. Wiederholtes Schema erhält Basic 5/Premium 50; ungültige Limits und Identitäten werden abgefangen.

**Windows-Startbefund:** `postgres_validation01.json` dokumentiert einen fehlgeschlagenen Start-Wrapper: PostgreSQL war bereit, aber ein geerbtes Ausgaberohr hielt den Aufruf offen. Die konkrete eigene Instanz wurde kontrolliert beendet und der Cluster entfernt; keine parallele Neuinitialisierung. Das Prüfprogramm verwendet danach eigene Logdateien statt geerbter Ausgaberohre. Der zweite Lauf besteht einschließlich kontrolliertem Stopp und vollständiger Clusterentfernung.

**Grenze:** Diese neun Tests prüfen die lokale PostgreSQL-Transaktionslogik, nicht Hanko, die administrative Oberfläche oder AlwaysData. Kein aktueller Test-/Produktivdatenbankzugang gelesen, keine Servermigration, kein Deployment. Liveversion und Testkonfiguration vor der späteren Umschaltung prüfen. Fachliche Restpunkte des Modelltests bleiben bestehen.

### Analyseassistent: verständliche Antworten und belegte Alternativen (10.09.2026)

**Umsetzung:** Eigener Kundenbereich `answer` mit freundlichen, feldbezogenen Rückfragen, ausgeschriebenen Regionen, formatierten Werten, relevanten Einschränkungen und Tabellen. Ursprüngliche Fakten, Quellen, Parameter und technische Hinweise bleiben getrennt erhalten. Allgemeine Methodiktexte verständlicher formuliert. Keine frei erfundenen Zahlen oder freien Tatsachenbehauptungen aus einer zusätzlichen Modellphase.

**T20:** Die fehlende Gütergliederung betrifft die Straßenrelation, nicht alle Verkehrsträger. Vier begrenzte lokale Folgeprüfungen am selben Datenstand prüfen Schienengüter, Binnenschiffs-Gesamtmenge sowie Straßenversand der Quelle und Straßenempfang des Ziels. Vorschläge nur bei tatsächlich vorhandenen nutzbaren Güterwerten; Gesamtmengen allein belegen kein regionales Güterprofil. Fehlende Zeile, fehlender Wert und nicht erfolgte Prüfung bleiben unterscheidbar. Höchstens fünf Sekunden zusätzlich innerhalb der gesamten Anfragefrist; Fehler einer optionalen Prüfung lassen die belegte Hauptantwort bestehen. Abfrageparameter und vollständige Befunde werden unter `related_data` nachvollziehbar gespeichert. Noch keine anklickbare Folgeabfrage im Portal.

**Konkreter Befund:** Köln → Hamburg 2024: Straßen-Gesamtmenge 67.757 t, laut Quelle eingeschränkt belastbar; keine Gütergliederung dieser Straßenrelation. Schiene: veröffentlichte Feinpositionen summieren sich auf 199.851 t. Binnenschiff: `missing_row`, kein Nachweis fehlenden Verkehrs und keine belegte Erklärung für die fehlende Veröffentlichung. Regionale Straßenprofile vorhanden: Köln Versand insgesamt 25.225.748 t, Hamburg Empfang insgesamt 57.257.443 t. Beide einschließlich innerregionaler Transporte; keine Übertragung ihrer Güteranteile auf Köln → Hamburg. Kundenhinweise und Vorschläge werden aus geprüfter Verfügbarkeit abgeleitet, nicht aus der Testkennung.

**Prüfung:** `outputs/analyseassistent_runtime_20260910/customer_portal_validation02.json`: 63/63 lokale Tests bestanden, keine externen Modellaufrufe. Enthält reale T20-Werte und Richtungsauswahl, fehlende IWW-Zeile, simulierten Abfragefehler, bekannte Null, unzureichende Profildaten, abgelaufene Frist und falschen Datenstand. Der vorherige Lauf `customer_portal_validation01.json` hatte einen veralteten Wortlautvergleich (61 Tests, ein Fehler); dieser wurde auf die tatsächlich gleichbedeutende Formulierung aktualisiert. Die Browser-Lesefassung wird aus unveränderten historischen Modellantworten neu dargestellt und prüft Alternativen zusätzlich lokal. Das ersetzt keinen neuen 45-Fälle-Modelllauf; Originalantworten bleiben einsehbar. Weiterhin insgesamt 78 historische Requesty-Aufrufe.

**Portalvorbereitung im selben Prüfstand:** Lokaler Adapter zur Auflösung validierter Hanko-Identitäten über Issuer und UUID, Prüfung von Herkunft und CSRF, einmalige Initialisierung sowie begrenzte Fehlerantworten bei Datenbankausfällen vorbereitet und getestet. Eine fehlgeschlagene Verbrauchsbuchung meldet keinen falschen Erfolg. Test-only-Einstieg unter `integration/analyseassistent/portal_entrypoint.py`; Übergabebuilder und Freigabebindung berücksichtigen Integrationsdateien. Noch nicht in das Plattform-Repository übernommen oder deployed. Aktuelles Übergabepaket und Modellfreigabe müssen nach den Codeänderungen neu erstellt werden. Administrative Oberfläche, Dashboardanschluss, Testdeployment und fachliche Restpunkte bleiben offen; keine Produktionsänderung.

### Analyseassistent: tatsächlicher Portalanschluss und Paketverwaltung lokal geprüft (10.09.2026)

**Umsetzung im maßgeblichen Plattform-Repository:** `alwaysdata_portal/wsgi.py` leitet die beiden Güterströme-API-Pfade an den geschützten Adapter weiter. `analyseassistent.py` und `ai_access.py` übernommen. API und Paketpflege nur bei `WBP_PORTAL_ENVIRONMENT=test` und `WBP_GUETERSTROEME_ENABLED=1`; keine Aktivierung durch ein Browserfeld. `/admin/ai-access` verlangt die bestehende Administratorprüfung und den Sitzungsschutz. Doppelte oder zusätzliche Formularfelder werden abgelehnt. Die normale Kundenübersicht ist jetzt ebenfalls auf den validierten Hanko-Aussteller begrenzt.

**Benutzerverwaltung:** Direkt am Güterströme-Konto lassen sich Basic 5, Premium 50 oder gesperrter KI-Zugang auswählen. Angezeigt werden Monat, genutzt, in Bearbeitung und verfügbar. Nur bestehende Güterströme-Werkzeugrechte erlauben eine Paketzuordnung. Planwechsel und Sperren löschen weder Freigabezeile noch Anfragehistorie. Fehlgeschlagene Verbrauchsabfragen erscheinen als Fehler, nicht als null. Normale Werkzeugrechte bleiben Voraussetzung für jede Analyse.

**Migration und Release:** Additive Migration `009_tool_ai_quotas.sql` ergänzt das Werkzeug zunächst inaktiv sowie die drei Kontingenttabellen mit Basic/Premium. Migrationen 001–008 unverändert. Release-Vollständigkeitsprüfung um beide neuen Module und Migration 009 ergänzt. Private fachliche Daten verbleiben im Güterströme-Repository; keine Zugangsdaten kopiert.

**Nachweise:** `outputs/analyseassistent_runtime_20260910/portal_integration_validation02.json`: 47/47 Portal-, Release- und Migrationsprüfungen bestanden. Der erste kombinierte Lauf `portal_integration_validation01.json` scheiterte an der noch nicht ergänzten Soll-Liste der Laufzeitmodule; zwei neue Pflichtmodule wurden in der Liste nachgeführt. `postgres_portal_validation04.json`: 14/14 Tests gegen eine eigene PostgreSQL-13.3-Instanz, alle neun tatsächlichen Plattformmigrationen geladen. Zusätzlich zum Kontingentschutz sind echte administrative Paketwechsel, Sperre mit anschließendem Abschluss einer laufenden Anfrage, Wiedereinschaltung, fehlendes Paket, falscher Aussteller, fehlendes Werkzeugrecht, absichtlicher Datenbankfehler mit Rücknahme sowie Bearbeitung im bisherigen Rechteeditor geprüft. Dessen Änderung erhält den KI-Verbrauch. Prüfdateien enthalten SHA-256 der relevanten Quelldateien. Testinstanz gestoppt und Cluster entfernt. Keine Liveportal- oder Modellverbindung.

**Qualitätsmaßstab:** Nutzer bestätigt T20 als passende Referenz für Tonalität und Struktur der Startphase. Diese Zustimmung betrifft die lokal formulierte Kundendarstellung mit geprüften Alternativen; sie ist keine erneute Gemini-Prüfung und keine fachliche Abnahme aller 45 Antworten. Das Modell ordnet Fragen zu und wählt belegte Aussagen, die Darstellung folgt dem Programmvertrag. Weitere Fragetypen hieran prüfen.

**Offen:** Dashboard und bedienbare Folgefragen anschließen, privaten Datenbestand in einen vollständigen aktuellen Portalrelease aufnehmen, Browserprüfung der Verwaltung, aktuelle AlwaysData-Testkonfiguration und Abhängigkeiten prüfen, Planmodus und Testdeployment einschließlich Rechte-/Rückfallprüfung durchführen. Migration 009 bisher nur in temporären lokalen Datenbanken angewendet. Kein Testportal umgeschaltet und keine Produktion geändert. Goal bleibt aktiv.

### Analyseassistent: bedienbare Kundenoberfläche und zusammengesetzter Testrelease (10.09.2026)

Der Dashboarddialog verwendet jetzt die geschützte Portal-API. Kontingente stammen ausschließlich vom Server; der frühere Browserzähler ist nicht mehr eingebunden. Antworten zeigen verständliche Einordnung, Tabellen mit Einheiten und geprüfte Folgefragen; technische Angaben bleiben eingeklappt. Folgefragen werden vorbereitet und erst nach erneutem Absenden ausgeführt. Tabellen sind auf Mobilgeräten horizontal scrollbar. Rückfragen erhalten die ursprüngliche Frage. Verbindungsabbrüche lösen keine automatische Wiederholung aus; bei unklarem Abschluss ist erneutes Senden bis zum Neuladen gesperrt. Eine Wiederherstellung verlorener Antworten nach dem Neuladen ist noch nicht implementiert.

Der Kontext berücksichtigt nur die jeweilige Modulauswahl: Maut mit AGS und Monat, Flughäfen und Seehäfen mit Knoten und passender Einheit, Prognose ohne verborgenes Ist-Jahr. Fehlende Angaben werden nicht ergänzt. Erfolgreiche Antworten ohne einen einzigen bekannten Zahlenwert verbrauchen keine Kontingentfrage; bekannte Nullwerte bleiben echte Zahlenwerte.

Der Plattformbuilder übernimmt mit `--gueterstroeme-package` ein geprüftes Fachpaket ausschließlich in einen Testrelease. Öffentliche Dashboarddateien liegen hinter der Werkzeugberechtigung; Programme, Systemprompt und Analysebestand unter `private/gueterstroeme`. Leaflet und Chart.js werden lokal mitgeliefert. Linux-Laufzeit muss DuckDB 1.2.1 und jsonschema 4.25.1 unterstützen. Unveränderter Datenstand: `3652bb8234800abbd4327ef4`.

Nachweise unter `outputs/analyseassistent_runtime_20260910/`: `ui_runtime_validation05.json` (64 lokale Laufzeittests), `portal_ui_validation04.json` (49 Portal-/Releaseprüfungen), `postgres_portal_validation04.json` (14 echte lokale Datenbanktests). `browser_ui03/report.json` besteht neun Browserprüfungen des vollständigen ui03-Releases mit synthetischen HTTP-Antworten aus dem geprüften T20-Ergebnis; Desktop- und Mobilansicht gesichtet. Die spätere modulbezogene Kontextkorrektur besteht zehn separate Prüfungen in `validate_assistant_context.cjs`; deshalb ist ui03 kein aktueller Deploymentkandidat mehr. Für den abschließenden ui04-Release sind Manifest- und Browserprüfung erneut auszuführen.

AlwaysData wurde ausschließlich lesend geprüft. Bestätigt: Testsite 1067000, bestehende Portal-Datenbank und Hanko-Konfiguration, Python 3.13, separate Testlaufzeit `portal_test/.venv`, keine direkten statischen Sitepfade. Die ausdrückliche Testkennzeichnung und Requesty-Konfiguration fehlen noch. Maßgeblich ist `alwaysdata_readiness02.json`; die Datenbank-/Virtualenv-Felder in `alwaysdata_readiness01.json` wurden mit unpassenden Feldnamen geprüft und sind überholt. Planmodus des ui03-Releases erfolgreich; keine Dateien hochgeladen, keine Live-Migration, keine Rechteänderung und keine Umschaltung.

Offen bleiben aktuelle Paketprüfung, Linux-Laufzeitprüfung, geschützte Testkonfiguration, Auswahl des Testkontos, tatsächliche Testbereitstellung und Abnahme mit echten Modellantworten. Die neun Browserprüfungen ersetzen keinen Hanko-/PostgreSQL-/Requesty-Gesamttest. Unverändert 78 historische Requesty-Aufrufe; keine neuen Kostenmessungen. Fachliche Restpunkte T13, T35, T43 und fehlender B07-Vorjahresmonat bleiben offen. T20 ist der bestätigte Darstellungsmaßstab, keine Freigabe aller 45 Fälle. Das Goal bleibt aktiv.

**Abschließender Prüfstand dieses Schritts:** `C:/tmp/portal-test-20260910-gueterstroeme-ui04` ist das aktuelle vollständige lokale Testpaket: 1.700 Dateien, 667.757.997 Bytes, Manifest-SHA-256 `25150e3c8e4fdad5aef10cf6bf8429fc5de949357e049b4769cbadc50d78f972`. `release_ui04_validation.json` bestätigt alle Dateiprüfsummen sowie die tatsächliche Initialisierung und T20-Abfrage direkt aus dem privaten Releasebestand. `browser_ui04/report.json` bestätigt erneut alle neun Browserprüfungen für genau dieses Manifest. Der AlwaysData-Planmodus bestätigt die Testsite und den Zielrelease; ohne `-Apply`, weiterhin keine Serveränderung. Fünf überholte eigene ui01–ui03-Pakete wurden nach Pfadkontrolle entfernt; die beiden abschließenden ui04-Pakete bleiben vorhanden.

**Echter T20-Nachtest:** `requesty_t20_ui04/result.json` und `review.json`: neuer Ablauf mit `vertex/gemini-3.7-flash@eu`, passende Funktionszuordnung, 67.757 t und drei belegte Folgefragen. Alle sichtbaren Antwortfelder stimmen mit dem bestätigten lokalen T20-Muster überein. Zwei erfolgreiche Modellaufrufe, 9.635 Tokens, laut API 0,010506375 USD, Ablaufzeit 11,25 Sekunden. Damit insgesamt 80 historische Requesty-Aufrufe. Dies belegt T20 im aktuellen Modell-/Programmlauf, nicht die Qualität aller 45 Fälle. Gemini ordnet zu und wählt belegte Aussagen; das Programm erzeugt weiterhin die Kundendarstellung.

**Testumgebung:** `alwaysdata_isolation01.json` bestätigt unterschiedliche Test-/Produktivdatenbanken und Laufzeitordner, allerdings denselben Datenbankbenutzer; keine Behauptung vollständig getrennter Zugangsdaten. `linux_wheels01.json` bestätigt veröffentlichte passende CPython-3.13-Linux-Pakete für die beiden neuen Abhängigkeiten, noch keine erfolgreiche Linux-Ausführung. Für die tatsächliche Freischaltung wurde die Auswahl eines bereits bestehenden Testkontos angefragt. Testkonfiguration, Live-Laufzeit, Deployment und gemeinsame Liveabnahme bleiben offen. Produktionssystem unverändert.

### Analyseassistent: Testrelease auf AlwaysData bereitgestellt (10.09.2026)

**Aktiv auf Testsite 1067000:** `portal_test/releases/portal-test-20260910-gueterstroeme-ui05/alwaysdata_portal/wsgi.py`, Arbeitsverzeichnis entsprechend. Das vollständige Paket ist bytegleich zum lokal und im Browser geprüften ui04-Stand, Manifest-SHA-256 `25150e3c8e4fdad5aef10cf6bf8429fc5de949357e049b4769cbadc50d78f972`. Der bestätigte Planmodus ging dem Apply-Lauf voraus. Testportal und Datenbank melden bereit; die vorhandene Test-Kita-Aufgabe 30833 wurde auf denselben Release umgestellt. Der bisherige funktionsfähige Testrelease `portal-test-20260904-bkg-basemap-v3` bleibt als Rückfallstand erhalten. Produktionssite und Produktionsaufgabe wurden nicht umgeschaltet.

**Upload und Wiederherstellung:** Der erste ui04-Upload brach nach 77 Dateien und 14.073.451 Bytes vor jeder Migration ab. Der bisherige Testrelease wurde anschließend mit gesundem Portalstatus bestätigt (`deployment_failed01.json`, `upload_diagnostic01.json`). Die Übertragung wurde auf weniger Verzeichniswechsel und maximal drei Versuche je betroffener Datei umgestellt; Wiederaufnahme beginnt bei Byte null ausschließlich innerhalb des neu angelegten, inaktiven Release. Vorhandene Releases und dauerhafte Zugriffsfehler werden nicht überschrieben oder endlos wiederholt. Sechs Automatisierungsprüfungen bestehen (`deployment_retry_validation01.json`). Der zweite Lauf mit neuem Namen ui05 übertrug alle 1.701 Dateien einschließlich Manifest, installierte die Laufzeit und führte die Testmigration erfolgreich aus. `partial_upload_cleanup01.json` bestätigt anschließend die Entfernung des eigenen unvollständigen ui04-Serverordners. Ein bereits vor dem zweiten Versuch vorhandener, nicht eindeutig dieser Arbeit zugeordneter FTPS-Zugang 567638 wurde nicht verändert.

**Direkte Linux-Prüfung:** `linux_runtime_validation01.json` verifiziert auf dem aktiven Server alle 1.700 Manifestdateien, Python 3.13.15, DuckDB 1.2.1, jsonschema 4.25.1 und psycopg 3.2.10. Der private Analysebestand initialisiert korrekt; T20 ergibt ohne Modell 67.757 Tonnen und drei belegte Folgefragen. Eine ausdrücklich lesende Datenbanktransaktion bestätigt Migration 009 samt Prüfsumme, Basic 5/Premium 50 und den weiterhin inaktiven Werkzeugeintrag. Vier Identitäten passen zum konfigurierten Hanko-Aussteller; es wurden keine Konten oder Rechte verändert. Temporäre Prüfaufgabe, FTPS-Zugang und Statusdatei wurden entfernt und die Bereinigung bestätigt.

**Öffentlicher Zugriffsschutz:** `live_access_validation02.json` bestätigt gesunde Portal-API und Loginseite. Der Werkzeugpfad liefert ohne Sitzung exakt dieselbe Loginseite; die deaktivierte Analyse-API gibt den vorgesehenen Hinweis mit HTTP 503 zurück. Private Dateien, Dashboardressourcen ohne Aktivierung und getestete Pfadüberschreitungen werden nicht ausgeliefert. `live_access_validation01.json` hatte hierfür zu enge Statuscode-Annahmen; der zweite Prüflauf prüft zusätzlich den tatsächlichen Antwortinhalt. Dies ist keine Abnahme eines angemeldeten Nutzers oder der Verwaltungsoberfläche.

**Requesty-Konfiguration und offene Freigabe:** Die automatische Freigabeprüfung hat die Übertragung des lokal verschlüsselten Requesty-Schlüssels in die geschützte AlwaysData-Testkonfiguration abgelehnt, weil die Zustimmung zur dortigen Speicherung nicht ausdrücklich vorlag. Dieser Auftrag wurde nicht ausgeführt. Der Nutzer möchte den Schlüssel selbst unter Web → Sites → Testsite 1067000 → Environment eintragen; die sechs erforderlichen Variablen wurden im Chat genannt, mit `WBP_GUETERSTROEME_ENABLED=0`. Erfolgreiches Speichern und passende Konfiguration sind noch zu bestätigen. Keine neuen Modellaufrufe in dieser Bereitstellung; weiterhin 80 historische Requesty-Aufrufe. Auswahl des Testkontos, gezielte Werkzeug-/Paketfreigabe und vollständige Prüfung mit Anmeldung und Requesty bleiben offen. Goal bleibt aktiv.

**Weitere fachliche Vorbereitung:** `t35_name_readiness01.json` bestätigt Namen für alle 59 positiven T35-Partnerrelationen 2024. Statistik-Länderkennungen dürfen nicht durch teilweise abweichende geografische Länderzuordnungen überschrieben werden; die Namensausgabe ist noch nicht im Assistenten ergänzt. `t43_scope_readiness01.json` bestätigt aus an B04–B06 gebundenen Originaldateien für 2024 die 422 Einträge, davon 400 NUTS-3 und 22 andere Raumebenen, ohne fehlenden Kreis. Die jahresübergreifende Datei umfasst dagegen 434 verschiedene Kennungen; der konkrete 422/400/22-Nachweis gehört ausdrücklich zum Jahr 2024. Noch nicht in die Kundenantwort eingebunden. T13 und B07-Vorjahresvergleich bleiben offen.

**Nachtrag: manuelle Requesty-Konfiguration und echter Serveraufruf bestätigt (10.09.2026):** Nach der vom Nutzer bestätigten Eingabe bestehen alle sechs Konfigurationsprüfungen; die Testsite wurde neu gestartet und meldet gesund. `alwaysdata_requesty_manual_config01.json` enthält ausschließlich Statusprüfungen, keinen Schlüssel. Umgebungsvariablen wurden nicht verändert. Der Nutzerzugang bleibt mit Aktivierungsflag `0` und inaktivem Werkzeugeintrag gesperrt.

`linux_requesty_validation01.json` bestätigt anschließend einen echten Ablauf direkt aus der Linux-Testlaufzeit über `vertex/gemini-3.7-flash@eu`: natürlich formulierte Frage nach Güterarten der Straßenverbindung Köln → Hamburg 2024, passende Funktionszuordnung, 67.757 Tonnen und dieselbe sichtbare Kundendarstellung wie beim bestätigten T20-Muster einschließlich drei Folgefragen. Zwei Modellanfragen, 9.809 Tokens, laut API 0,011382525 USD, Analysezeit 10,264 Sekunden. Zusammenfassung: `requesty_server_summary01.json`. Damit 82 protokollierte Modellanfragen insgesamt. Kein Kundenkontingent belastet; keine neue fachliche 45-Fälle-Abnahme. Datenbank-/Manifestprüfung bestanden, temporäre Aufgabe, FTPS-Zugang und Statusdatei entfernt. Noch kein Test einer angemeldeten Browser-Sitzung oder Kontofreigabe.

Der Serverprüfer führt bezahlte Aufrufe nur mit `--requesty` aus. Anschließend wurde sein Wiederholungsschutz ergänzt: Eine atomar angelegte Startdatei verhindert zusätzliche Ausführungen derselben geplanten Prüfaufgabe bei langsamen Modellantworten. `remote_probe_once_validation01.json` prüft den tatsächlichen Startabschnitt mit acht konkurrierenden lokalen Prozessen: genau eine Ausführung, keine externen Aufrufe, temporärer Ordner entfernt. Der neu ergänzte Startschutz ist separat lokal geprüft; der vorherige erfolgreiche Linuxbericht bindet seinen damaligen Prüferstand. Auswahl des bestehenden Testkontos, gezielte Paket-/Werkzeugfreigabe und gemeinsame Browser-/Requesty-Abnahme bleiben offen. Produktionssystem unverändert; Goal aktiv.

### Analyseassistent: Testeinstieg aktiviert, Kontofreigabe noch offen (10.09.2026)

Nach Benennung des eigenen Administratorkontos durch den Nutzer wurde ausschließlich auf Testsite 1067000 der Werkzeugeintrag `gueterstroeme` aktiviert und `WBP_GUETERSTROEME_ENABLED` von `0` auf `1` gesetzt. Die übrigen bestehenden Umgebungswerte bleiben erhalten. Der Planlauf prüfte den exakten ui05-Testrelease, die separate Testdatenbank und die Testkennung. Der Ausführungslauf prüfte erneut alle 1.700 Manifestdateien, die Linux-Laufzeit, Migration 009 und T20 ohne Modell. Vor Aktivierung waren keine Güterströme-Werkzeugrechte oder KI-Paketfreigaben vorhanden; keine Kontorechte wurden geändert. Produktionssite unverändert. Nachweis: `outputs/analyseassistent_runtime_20260910/test_activation01.json`; temporäre Aufgabe, FTPS-Zugang, Statusdatei und Startschutz entfernt.

Nach Neustart bestehen fünf öffentliche Zugriffsprüfungen: Portal gesund, Werkzeug ohne Sitzung nur Loginseite, Kontingent-API 401, Dashboarddatei 403 und privater Systemprompt 404 (`activated_access_validation01.json`). Keine neuen Requesty-Aufrufe; weiterhin 82 protokollierte Modellanfragen. Das benannte Administratorkonto soll Premium mit 50 Fragen je Kalendermonat erhalten. Seine konkrete Anmeldekennung wird über die angemeldete Portalverwaltung bestätigt; die persönliche Werkzeug-/Paketfreigabe und gemeinsame Browserabnahme sind noch offen. Die Anmeldung wurde im geöffneten Chrome-Testportal angefragt. Keine fachliche Gesamtfreigabe; T13 sowie die vorbereiteten T35-/T43-Verbesserungen bleiben offen. Goal aktiv.

### Analyseassistent: Flughafennamen und konkrete Gebietserklärung lokal geprüft (10.09.2026)

Die neue private Darstellungsreferenz wird reproduzierbar aus `web_airfreight.json`, `web_summary_by_region.json` und `nuts3_de_2024.geojson` abgeleitet. Flughafenantworten nennen nun beispielsweise East Midlands Airport und Leipzig/Halle. ICAO-Kennung, Mengen, vollständiger Anteilsnenner und statistische Partner-Länderkennung bleiben erhalten. Geografische Länderzuordnungen werden bewusst nicht zur internationalen Abgrenzung verwendet. Flughafennamen bleiben außerhalb des Regionsnamensregisters, damit Stadt-/Flughafenüberschneidungen keine bestehenden Kreisabfragen verändern.

Die Methodikantwort T43 erklärt nun anhand des ausdrücklich bezeichneten Beispiels 2024: 422 Einträge bestehen aus 400 Kreisen und kreisfreien Städten sowie 22 weiteren Gebietseinträgen; eine Summe über alle Einträge vermischt überlappende Räume. Die abweichende Zählweise regionaler und nationaler Statistiken sowie die Unterscheidung von Tonnen und Tonnenkilometern bleiben erklärt. Der Nachweis erhält eine eigene Quellenangabe. Keine numerischen Analysefakten und damit keine Buchung gemäß unveränderter Kontingentregel.

`ui_runtime_validation06.json` dokumentiert den ersten Fehlversuch: Namensüberschneidungen durch ein gemeinsames Register und ein falsch benannter Testparameter. Nach Korrektur bestehen alle 67 Prüfungen (`ui_runtime_validation07.json`). Die neuen Tests vergleichen die gesamte Referenz mit den Originalpaketen, alle veröffentlichten Partnerwerte und Länderkennungen einschließlich LFSB/CH, den vollständigen Nenner 662.332 Tonnen sowie den jahresgebundenen 422/400/22-Nachweis. `gate_ui06.json` bestätigt die technische Bereitschaft aller 45 Eingaben; keine neue fachliche Modellabnahme. `customer_examples_ui06.json` enthält lokale T20-/T35-/T43-Antworten ohne Modellaufrufe.

Die Referenzprüfsumme ist Bestandteil der Laufzeitkennung: lokal `205f56cd7dca3225c3b4f120`; die Verkehrsquellpakete selbst sind unverändert. Der aktive ui05-Testrelease verwendet weiterhin `3652bb8234800abbd4327ef4` und enthält diese lokalen Ergänzungen noch nicht. Nutzeranmeldung, persönliche Premium-Freigabe und gemeinsame Browserabnahme bleiben offen. Produktion unverändert; weiterhin 82 protokollierte Requesty-Aufrufe.

**Paketnachweis:** `C:/tmp/gueterstroeme-handoff-20260910-ui06` enthält 1.614 geprüfte Dateien mit 648.581.738 Bytes. `handoff_ui06_validation.json` bestätigt alle Dateiprüfsummen sowie die tatsächliche Ausführung von T35 und T43 ausschließlich aus der privaten Paketlaufzeit. Die Referenzdatei ist enthalten; keine zusätzlichen lokalen Originalpakete für die Laufzeit erforderlich. Noch kein Upload oder Wechsel des aktiven ui05-Testrelease.

### Analyseassistent: eigenes Administratorkonto freigeschaltet und Browserablauf geprüft (10.09.2026)

Nach bestätigter Anmeldung wurde das benannte eigene Konto über die tatsächliche Testportalverwaltung als WBP Administration zugeordnet. Güterströme wurde zu den fünf vorhandenen Werkzeugfreigaben ergänzt; bestehende Tableau-Zuordnung und Stufen blieben erhalten. Anschließend wurde das Premium-Paket mit 50 Fragen je Kalendermonat gespeichert. Die Portalübersicht zeigte zunächst 0 genutzt und 50 verfügbar.

`authenticated_browser_ui05.json` dokumentiert die tatsächlichen DOM- und Sichtprüfungen in Chrome, keine synthetischen Antworten: Eine erste freie Frage nach den Gütern von Köln nach Hamburg führte zu einer zu allgemeinen Rückfrage. Der Zähler blieb dabei korrekt bei 0. Die anschließend ausdrücklich gerichtete Frage mit Köln → Hamburg und der Einheit Tonnen lieferte die akzeptierte Kundendarstellung: 67.757 Tonnen, Einschränkung der Straßen-Gütergliederung, belegte Schienenalternative, fehlende Binnenschiffszeile ohne Nullannahme und drei Folgefragen. Danach zeigte das Portal 1 von 50 genutzt und 49 verfügbar. Die Darstellung wurde zusätzlich als Screenshot visuell geprüft. Dieser Nachweis bestätigt den angemeldeten Requesty-/Daten-/Kontingentweg, nicht die zuverlässige Zuordnung aller freien Fragen. Die beiden Browserfragen verursachen zusätzliche Modellaufrufe; deren genaue Anzahl, Tokens und Kosten wurden nicht aus dem Provider-Audit gelesen. Die vorherigen 82 protokollierten Aufrufe sind deshalb kein aktueller Gesamtzähler.

Die konkrete Codeprüfung erklärt eine Hürde der ersten Frage: Ohne bestätigte Endpunkte erlaubte die Parameterprüfung zuvor nur gerichtete Pfeile. Lokal werden nun auch eindeutige Formulierungen `von <Ort> nach <Ort>` anhand des vorhandenen Namensregisters geprüft. Vertauschte Endpunkte, mehrere unterschiedliche Verbindungen oder mehrdeutige Ortsnamen bleiben unzulässig. Nicht belegte Parameter werden als benannte fehlende Felder an die Kundendarstellung gegeben; bei fehlender Einheit folgt beispielsweise eine konkrete Nachfrage nach Gütermenge oder Verkehrsleistung. Es wird keine Einheit still ergänzt.

69 lokale Prüfungen bestehen (`ui_runtime_validation08.json`), ebenso die technische Bereitschaft aller 45 Eingaben (`gate_ui07.json`). Der aktuelle Testserver bleibt vorerst ui05; die lokal geprüften Korrekturen sind für den nächsten Release gebündelt. Der zwischenzeitlich vollständig vorbereitete ui06-Release enthält ausschließlich private Antwortänderungen und interne Übergabemetadaten, die öffentlichen Dashboard- und Portaldateien sind unverändert (`release_ui06_validation.json`). Für die zusätzliche Fragekorrektur wird ui07 vorbereitet. Keine Produktionsänderung. Persönliche Freigabe und erster gemeinsamer Browser-/Buchungstest sind erledigt; Veröffentlichung und erneuter Browsernachweis der lokalen Korrekturen sowie fachliche Gesamtfreigabe bleiben offen.

**Nächster Testrelease:** `portal-test-20260910-gueterstroeme-ui07` ist vollständig geprüft: 1.701 Dateien, 667.778.641 Bytes, Manifest `4de95744d27645bce4bf31cc71e53a1c28d401b15b3e5c816becdeb68f0b045d`. `release_ui07_validation.json` bestätigt alle Dateiprüfsummen, unveränderte öffentliche Portal-/Dashboarddateien und die natürliche Richtungserkennung mit echten Fachdaten und synthetischem Modellplan direkt aus der privaten Release-Laufzeit. Der lesende AlwaysData-Planmodus bestätigt ui05 als bisherigen und ui07 als Zielrelease. Die Übertragung wurde anschließend gestartet; erfolgreicher Abschluss, aktive Pfade und Linux-/Browsernachprüfung sind noch zu bestätigen. Kein vorzeitiger Freigabenachweis aus dem laufenden Upload.


### UI-Rückmeldung und Testrelease ui09 – 10.09.2026

ui07 ist inzwischen erfolgreich bereitgestellt: `deployment_ui07.json` bestätigt aktive Testpfade, unveränderte Serverumgebung und Produktion sowie bereinigte temporäre Zugänge. `linux_runtime_validation02.json` bestätigt sämtliche Manifestdateien, Linux-Laufzeit, Kontingentmigration und die Antwortkorrekturen einschließlich natürlicher Richtungsangaben; ohne neue Modellaufrufe.

Auf ausdrücklichen Nutzerwunsch zeigt der Portal-Link ein Haus-Symbol und „Portal“ ohne Unterstreichung. Die Kartenfilter-Auswahl und ihre Zusammenfassung sind aus dem Assistenten entfernt; freie Fragen senden leere bestätigte Parameter. Nur ausdrücklich gewählte Folgefragen behalten ihre belegten Parameter und verlangen weiterhin das Absenden. Die permanente Fußzeile entfällt; notwendige Verbindungs- und Kontingentmeldungen erscheinen nur bei entsprechendem Zustand. Bei geöffneten Beispielfragen bleiben Titel und Eingabe bei 1440 × 1000, 900 × 600 und 390 × 844 Pixeln getrennt.

Das echte Dashboard-Vorschaubild liegt unter `assets/previews/gueterstroeme.png` und ist über den geschützten Werkzeugpfad in der Portalübersicht verknüpft. `browser_ui09/report.json` bestätigt elf Browserprüfungen mit künstlichen API-Antworten, ohne Modellaufrufe. `portal_ui_validation07.json` bestätigt 49 Portalprüfungen; eine bestehende Bildprüfung wurde an den externen Fachpaketpfad angepasst. `release_ui09_validation.json` bestätigt 1.702 Dateien, 668.082.821 Bytes und das enthaltene, verknüpfte Vorschaubild; Manifest `63a38d98fe57a45bb5e235b83d8e9eb154e6ee7e24ef70ec13c258445c0f6b66`.

Der lesende Planlauf bestätigt Testsite 1067000, ui07 als vorherigen und ui09 als Zielrelease. Upload gestartet; Abschluss und abschließende Liveprüfung stehen noch aus. Keine vorzeitige Freigabe aus dem laufenden Upload.


**Abschluss ui09:** `deployment_ui09.json` bestätigt die erfolgreiche Umschaltung auf ui09, unveränderte Serverumgebung und Produktion sowie entfernte temporäre Upload-/Migrationszugänge. `linux_runtime_validation03.json` bestätigt alle 1.702 Manifestdateien, Linux-Laufzeit, Migration 009 und T20/T35/T43 ohne zusätzliche Modellaufrufe oder Datenbankänderungen. `activated_access_validation02.json` bestätigt fünf öffentliche Zugriffsprüfungen einschließlich des geschützten Vorschaubilds.

`authenticated_browser_ui09.json` dokumentiert die echte angemeldete Chrome-Prüfung: Werkzeug-Vorschaubild geladen (1.040 × 585 Pixel), Haus-Symbol und „Portal“ ohne Unterstreichung, entfernte Filterkontrollen und Fußzeile sowie geöffnete Beispielfragen ohne Überlagerung. Die vollständig frei eingegebene Frage „Welche Güter wurden 2024 auf der Straße von Köln nach Hamburg transportiert? Bitte die Gütermenge in Tonnen und die verfügbaren Güterarten angeben.“ wurde über die echte Modell-/Datenstrecke beantwortet: 67.757 Tonnen, Quellenbeschränkung, belegte Schienenalternative, fehlende Binnenschiffszeile ohne Nullannahme und drei Folgefragen. Zähler vor/nach dieser Analyse: 1/50 → 2/50, danach 48 verfügbar. Provider-Aufrufzahl, Tokens und Kosten dieser Browseranalyse wurden nicht gesondert ausgelesen; eine Browseranalyse ist nicht mit einem einzelnen Modellaufruf gleichzusetzen.

Vier eigene überholte lokale Zwischenpakete ui06/ui08 wurden entfernt; aktueller Release, Rückfallversion und gemeinsame Browserlaufzeit bleiben erhalten (`temp_cleanup_ui09.json`). Das beauftragte Goal bis zum nutzbaren Testdeployment einschließlich der nachträglichen UI-Wünsche ist damit erledigt. Fachliche Gesamtabnahme aller 45 Antworten, T13 mit bestätigter Quellenvergleichbarkeit und ein B07-Monatspaar zum Vorjahr bleiben ausdrücklich weitere Schritte; sie werden nicht als bereits gelöst ausgewiesen.


### Dialogkorrekturen nach Nutzersichtung – ui10, 10.09.2026

Die Nutzersichtung zeigte drei Darstellungsfehler und eine grundlegende Dialoglücke: Logo öffnete Quellen, Informationstext sprach von einer Filterauswahl, Arbeitszustand war nicht zuverlässig sichtbar, Listenmarker lagen außerhalb der Antwortblase; kurze Antworten auf Rückfragen hatten keinen Bezug zur vorherigen Frage. Außerdem mussten selbst technisch ableitbare Standardparameter ausdrücklich genannt werden.

Die Logo-Grafik ist jetzt ein normaler Homepage-Link nach `https://wissensbasiert.de/` in einem neuen Tab; die bisherige Quellen-Dialogbindung ist entfernt. Der Informationstext benennt die letzten Chatnachrichten, die ausschließliche Datengrundlage des Tools und den Verzicht auf Kartenfilter. Eine Arbeitsanzeige mit rotierendem Kreis bleibt während der Anfrage direkt über dem Eingabefeld sichtbar; bei reduzierter Bewegung bleibt der Text sichtbar. Das Feld wird beim Absenden geleert, auch vor einer Rückfrage. Listen besitzen eigene innere Einrückung.

Der Browser hält ausschließlich Nutzernachrichten dieses geöffneten Chats (höchstens sechs Nachrichten, insgesamt 6.000 Zeichen); keine dauerhafte Gesprächsdatenbank und keine alten KI-Zahlen als Faktengrundlage. Der Server begrenzt und prüft das Eingabeformat vor der Reservierung. Kurze Ergänzungen werden mit dem bisherigen Anliegen zusammengeführt; ein neues ausdrücklich genanntes Jahr ersetzt die alte Einzeljahresangabe, eine neue selbständige Frage mit Ortsbezug beginnt eine neue Fragestellung. „Neuer Chat“ und Neuladen verwerfen den lokalen Verlauf, ohne Kontingente zu verändern. Das ist kein unbegrenztes Langzeitgedächtnis und keine vollständige Auflösung beliebiger Gesprächswechsel.

`dialogue.py` ergänzt unabhängig vom Modell benannte Standards und eindeutig aus dem Text belegte Parameter. „Von Berlin nach Hamburg“ bedeutet Versand von Berlin mit Partner Hamburg. Allgemeine Güterfragen verwenden alle verfügbaren Güterarten und Tonnen; entsprechende Annahmen erscheinen in den Hinweisen. Ein konkreter abweichender Zahlen-/Filterwunsch bleibt zu prüfen. Bei einer fehlenden Jahresangabe wird der tatsächlich vorhandene neueste Jahrgang als Antwortknopf angeboten. „Das aktuellste Jahr“ wird anhand des passenden geprüften Datenprodukts aufgelöst; regionale Profile werden zusätzlich mit der Quellenjahresabdeckung der benötigten Verkehrsträger abgeglichen. Fehlende Werte werden nicht durch frühere Jahrgänge oder Null ersetzt.

`dialogue_runtime05.json` bestätigt 72 lokale Prüfungen einschließlich Verlauf, Jahreswechsel, neuer Verbindung, ungültiger Rollen im HTTP-Verlauf und Berlin–Hamburg mit echter lokaler Datenabfrage. Eine bestehende Flughafensummenprüfung erhielt eine Toleranz von 0,0000001 Tonnen für schwankende binäre Summenreihenfolge; keine Datenwerte oder Berechnungslogik geändert. `gate_ui10.json` bestätigt die technische Bereitschaft der 45 bestehenden Eingaben, keine erneute fachliche Gesamtabnahme. `browser_ui10b/report.json` und die visuell geprüften Bilder `arbeitsanzeige.png`/`rueckfrage-mobil.png` belegen Arbeitsanzeige, geleertes Feld, Verlaufspayload, neuen Chat, enthaltene Listen und den unveränderten Zugriff auf Kontingente; diese Browserantworten sind künstliche Testantworten.

Der zusätzliche echte lokale Requesty-Dialog besteht: „Welche Güter gehen per Schiene von Berlin nach Hamburg?“ führt nur zur Jahresfrage mit Vorschlag 2025. „Das aktuellste Jahr“ unter Mitgabe der ersten Nutzernachricht liefert die Schienen-Güterauswertung für Berlin → Hamburg 2025: 240.297 Tonnen Summe verfügbarer veröffentlichter Feinpositionen. Das ist kein uneingeschränkter Vollständigkeitsnachweis aller tatsächlich transportierten Güter. Drei Modellaufrufe über zwei Dialogschritte, 19.507 Tokens und 0,024864675 USD laut API; kein Portal-Kontingent belastet. Nachweise: `dialogue_requesty_first01.json`, `dialogue_requesty_latest01.json`, `dialogue_requesty_summary01.json`.

`release_ui10_validation.json` bestätigt den vollständigen Kandidaten mit 1.703 Dateien und 668.098.489 Bytes; Manifest `1e1c571d610469b859a02ba5c3c61dc06e647f9e82d595cf719b430b943344e2`. Zwölf Dateien unterscheiden sich vom Vorgänger, davon eine neu. Der AlwaysData-Planlauf bestätigt ui09 als aktiven und ui10 als Zielrelease der Testsite 1067000. Upload gestartet; erfolgreiche Umschaltung und angemeldeter Live-Dialog bleiben bis zum Abschluss zu bestätigen. Produktion unverändert.


**Liveabschluss ui10:** `deployment_ui10.json` bestätigt erfolgreiche Bereitstellung auf Testsite 1067000, unveränderte Serverumgebung und Produktion sowie entfernte temporäre Upload-/Migrationszugänge. `linux_runtime_validation04.json` bestätigt alle 1.703 Manifestdateien und zusätzlich den zweistufigen Jahresdialog mit synthetischem Plan und echten Daten direkt in der Linux-Laufzeit. Keine neuen Modellaufrufe oder Datenbankänderungen in dieser Serverprüfung; alle temporären Prüfmittel entfernt. `activated_access_validation03.json` bestätigt fünf öffentliche Zugriffsschutzprüfungen, darunter die nicht öffentliche Dialogdatei.

`authenticated_browser_ui10.json` belegt anschließend den echten angemeldeten Portalablauf: Homepage-Link statt Quellenbindung, überarbeiteter Informationstext, geleertes Eingabefeld, sichtbare rotierende Arbeitsanzeige und Listen innerhalb der Antwortblase. Auf „Welche Güter gehen per Schiene von Berlin nach Hamburg?“ kam ausschließlich die Jahresfrage mit Vorschlag 2025. Die kurze Antwort „Das aktuellste Jahr“ lieferte unmittelbar „Güterverkehr auf der Schiene von Berlin nach Hamburg (2025)“ mit 240.297 Tonnen Summe verfügbarer veröffentlichter Güterangaben. Richtung, Gütergruppe und Kennzahl wurden nicht erneut abgefragt. Verbrauch: vor der Frage 2/50, nach der Rückfrage weiterhin 2/50, nach der Auswertung 3/50 und 47 verfügbar. Die genaue zusätzliche Provider-Aufrufzahl, Tokens und Kosten dieser beiden Browserübermittlungen wurden nicht separat ausgelesen.

Die angeforderten Darstellungs- und Dialogkorrekturen sind damit auf dem Testportal umgesetzt und anhand des gemeldeten Beispiels abgenommen. Der begrenzte Verlauf ersetzt kein unbegrenztes Gesprächsgedächtnis. Eine fachliche Gesamtabnahme aller freien Formulierungen oder aller 45 Antworten wird daraus nicht abgeleitet.


### GitHub-Sicherung und Testreleasepflege (11.09.2026)

Der operative Ablauf steht in [RELEASE_UND_GITHUB.md](../betrieb/RELEASE_UND_GITHUB.md). Beide zugehörigen Quellstände sind auf GitHub `main` gesichert. Die standardmäßige Delta-Übertragung wurde an einem separaten, nicht aktivierten Serverpaket geprüft: 332.416 Bytes Upload statt rund 668 MB, 1.704 Zielprüfsummen bestätigt. 28 gezielte Prüfungen des ausgewählten Portal-/Deploymentstands sowie Frontend-Lade-/Syntaxprüfung bestanden. Für die isolierte Builderprüfung wurde der tatsächliche externe Kita-Eingabeordner ausdrücklich zugeordnet.

57 alte/temporäre Testordner wurden nach aktueller Verweisprüfung entfernt. Erhalten: ui10 aktiv, ui09 und ui07 als Rückfallstände; alle 5.106 Manifestdateien geprüft. API und Datenbank gesund, Produktionskonfiguration unverändert, temporäre Prüfmittel entfernt. Keine neue Modellanfrage, Änderung der fachlichen Daten oder Gesamtabnahme der KI-Antworten. Ergebnisse: `outputs/release_work_20260911/`.

### Analyseassistent: beleggebundene Antwortsynthese und Mehrjahresrelation (11.09.2026)

**Anlass und Prüfmaßstab:** Die Nutzersichtung zeigte zwei systematische Schwächen: Ein ausdrücklicher Mehrjahreswunsch wurde in eine Einzeljahres-Rückfrage umgedeutet und konnte anschließend technisch abbrechen; umfangreiche Ergebnisse wurden weitgehend als Tabelle wiederholt, statt die Werte zu gewichten und miteinander in Beziehung zu setzen. Drei ausdrücklich beauftragte Subagenten mit `gpt-5.6-terra` prüften unabhängig Stichproben und Leitplanken. Betrachtet wurden insbesondere T01, T04, T05, T07, T10, T13, T19, T22, T26, T28, T31, T35, T39, T43 und T45. Der gemeinsame Erwartungshorizont lautet: direkte Antwort zuerst, mindestens eine rechnerisch belegte Einordnung soweit möglich, keine zeilenweise Tabellenwiederholung, klare Daten-/Vergleichsgrenze und keine unbelegten Ursachen oder Empfehlungen.

**Umsetzung:** Die neue Funktion `relation_history` erkennt gerichtete Fragen nach den letzten Jahren deterministisch. Ohne Modellaufruf verwendet sie die fünf neuesten gemeinsam abfragbaren Jahre und weist diese Annahme sichtbar aus; die Antwort auf eine vorherige Rückfrage mit „mehrere Jahrgänge“ behält denselben Mehrjahreswunsch. Kurze Ortsnamen werden nur bei einer eindeutigen Stadt-/Landkreis-Konstellation sichtbar als kreisfreie Stadt aufgelöst. Die Ergebnisschicht erzeugt für die wesentlichen numerischen Funktionen geprüfte Analyseaussagen zu Größenverhältnissen, Rangfolgen, Salden, Anteilen oder Zeitpunkten. Das Modell darf daraus höchstens drei kurze Absätze formulieren und muss je Absatz die verwendeten Aussagekennungen nennen. Kennungen, Zahlen, Größenordnung, Einheit und riskante Einordnungen werden serverseitig geprüft; eine unzulässige oder abgebrochene Modellantwort fällt auf die bereits analytische Serverfassung zurück. Lange Tabellen werden vollständig erhalten, aber ab neun Zeilen zunächst eingeklappt. Technische Fehler erhalten eine Stufe und eine kurze Fehlerkennung, ohne interne Fehlermeldungen offenzulegen.

**Prüfung:** `outputs/analyseassistent_runtime_20260911/growth_validation01.json` bestätigt 83/83 lokale Laufzeit-, Daten-, Sicherheits- und Dialogprüfungen, null externe Modellaufrufe. Darin enthalten sind beide Rosenheim–Augsburg-Abläufe, die rechnerische Veränderung, der analytische Duisburg-Güter- und Regionsprofil-Einstieg, sicherer Datenfehler sowie Ablehnung fremder Kennungen, neuer Zahlen, geänderter Einheiten und unbelegter wirtschaftlicher Deutungen. Python- und JavaScript-Syntax sowie der vollständige Frontend-Neubau bestehen. Die Datenbestände wurden nicht geändert.

**Bereitstellung und Freigabegrenze:** Beta04 ist auf Testsite 1067000 aktiv. `linux_growth_validation02.json` bestätigt alle 1.706 Dateien, die unveränderte Linux-Laufzeit, die Daten- und Datenbankprüfungen sowie den konkreten Rosenheim–Augsburg-Fall mit 50,99 % rechnerischem Rückgang. Die Prüfung erzeugte keine Modellanfrage, keine Datenbankänderung und keine Kundenbuchung; ihre temporäre Aufgabe und der FTPS-Zugang wurden entfernt. Dies ist kein neuer Requesty-45-Fälle-Lauf und keine erneute angemeldete Browserabnahme. Produktion bleibt unverändert.


### Analyseassistent: Kundenantwort Dortmund → Bielefeld (11.09.2026, lokal)

Die Originalquellenprüfung bestätigt 110.050 Tonnen für 2020 und 55.106 Tonnen für 2022, jeweils eingeschränkt belastbar; die eigene Straßenrelationszeile fehlt für 2024 bereits in der vorhandenen KBA-Datei. Die Antwort darf daraus weder Nullverkehr noch eine Entwicklung bis 2024 ableiten. Die Randjahreslogik, verständliche Stichprobenerklärung, präzisen Fehlwertzustände und Absatzabstände sind lokal korrigiert. Ausführlicher Nachweis: [Kundenantwort-Prüfbericht](ANALYSEASSISTENT_KUNDENANTWORT_20260911.md).

`outputs/analyseassistent_kundenantwort_20260911/targeted_validation.json` bestätigt 13/13 gezielte Prüfungen. Ein ausdrücklich erlaubter echter Requesty-Antwortaufruf besteht mit 3.024 Tokens und 0,0029502 USD, ohne Kundenbuchung. Die gespeicherte echte Antwort ist mit dem vorhandenen Chatclient und aktuellem CSS auf Desktop und Mobilgerät geprüft; Jahresdetails bleiben vollständig zugänglich. CSS-Build und Syntax-/Diffprüfung bestanden.

Der breite Gesamtprüflauf wurde nach mehr als zwölf Minuten ohne Abschluss beendet und zählt nicht als bestanden. Keine aktuelle Gesamtfreigabe, kein Testportal-Deployment und keine Produktionsänderung aus dieser Korrektur. Vor Releasefreigabe ist der vollständige Laufzeitnachweis abzuschließen.


### Nachprüfung 15.09.2026: Achsenpräzision und KPI

KV-Achsen passen ihre Dezimalstellen an den Skalenabstand an. Mengen-/Leistungs-KPI runden ab 100 auf ganze Werte, kleinere Werte abgestuft ohne Scheinnullen. Ladeanzeige nun ab 1.500 ms. 32 Achsenkonfigurationen für Köln 2025, 25 Kontextansichten, Zahlen- und Luft-KPI-Prüfungen bestanden. Details im Prüfbericht DIAGRAMMKONTEXT_UND_KV_20260915.md, Abschnitt Nachprüfung. Weiterhin lokal, nicht im Testportal.


### Flughafenzählung und Hover, 15.09.2026

Flughafenzählung auf positive Verkehrs-/Flugwerte begrenzt (2024 Gesamtfracht: 18). Kategorienzuordnung und zeilenweiser Hover im Flughafenranking korrigiert; Achsen- und Datenhinweise abgestimmt. Prognosekarten-Hover gekürzt und mit dynamischem Vergleich 2019–2040 ergänzt. 48 Filter-/Szenariofälle, Fehlwertgrenzen, Luft-KPI sowie Maus-/Kartenvergleich lokal bestanden. Details und Grenzen im Prüfbericht DIAGRAMMKONTEXT_UND_KV_20260915.md, letzter Nachprüfungsabschnitt. Nicht bereitgestellt.


Prognose-Nachtrag 15.09.2026: Δ und Grün/Rot/Grau für Flächen- und Verbindungsvergleiche harmonisiert. Verbindungen vergleichen 2019–2040 mit identischer Richtung, Kennzahl und Güterauswahl; fehlende Ranglisteneinträge sind keine Nullwerte. Lokale Fach- und Browserprüfung im letzten Abschnitt von DIAGRAMMKONTEXT_UND_KV_20260915.md dokumentiert.
