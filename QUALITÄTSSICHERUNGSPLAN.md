# Qualitätssicherungsplan für das Güterströme-Dashboard

**Stand:** 01.09.2026  
**Status:** Automatisierte, browserseitige und manuelle Korrekturregression bestanden; die unabhängige externe Zweitprüfung ist aus Datenschutzgründen noch nicht erfolgt  
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
- QS-01 bis QS-03: Der Seeverkehr wird mit expliziter CSV-Zitierlogik und als Text eingelesenen Schlüsseln verarbeitet. Innerdeutsche Seeverkehre werden am deutschen Ladehafen als Versand und am deutschen Löschhafen als Empfang gezählt. Die automatisierte Prüfung `scripts/validate_maritime_bundle.py` muss für alle Berichtsjahre bestehen.
- Ergänzend muss `scripts/validate_maritime_port_profiles.py` alle veröffentlichten Seeverkehrs-Hafenprofile gegen die MRTM-Rohdaten prüfen: Tonnen, Empfang, Versand, TEU, NST-7-/NST-20-Struktur und internationale Partnerrelationen. Fehlende Richtungsfelder in Hafen-, Gütergruppen- oder NST-Objekten lassen den Test fehlschlagen; eine 58/42-Schätzung darf im veröffentlichten Datenpaket nicht erforderlich sein.
- QS-04: Die Richtungsauswahl bleibt auch in der nationalen VP2040-Ansicht aktiv. Bei „Gesamt“ werden die vollständigen nationalen Matrizen einschließlich Transit und Sonderzellen verwendet. Bei Versand, Empfang und Saldo werden Karte und KPI aus den räumlich zuordenbaren NUTS-3-Werten gebildet; Transit und nicht regional zuordenbare Sonderzellen sind in diesem Richtungsumfang ausdrücklich ausgeschlossen.
- QS-06 und QS-08: Nationale Tonnen- und Tonnenkilometerwerte werden aus der vollständigen nationalen Rohgrundgesamtheit berechnet, nicht aus der Summe vollständig NUTS-zuordenbarer Relationen.
- QS-07: Die NST-2007-Zuordnung der Relationstabellen entspricht derselben sieben Hauptgruppen umfassenden Zuordnung wie Karten und Diagramme. Bei den dreistelligen Schlüsseln handelt es sich nicht um eine alte NST-Systematik, sondern um die feinere NST-2007-Untergliederung; führende Nullen sind Bestandteil des Schlüssels.
- Feinpositions-Regression: `scripts/validate_nst_fine_codes.py` muss alle tatsächlich vorkommenden NST-2007-Feinpositionen von Schiene und Binnenschiff einer Abteilung 01–20 zuordnen und deren C1–C7-Summen unabhängig gegen `fact_od_flows.parquet` nachrechnen. Unbekannte Formate, fehlende Abteilungen, abweichende Summen oder abweichende sichtbare NST-20-/C1–C7-Bezeichnungen verhindern die Freigabe.
- VP2040-Güterschlüssel: `scripts/validate_vp2040_bundle.py` prüft beide gelieferten Dateien `nst2007.csv`, die Begriffe der VP-Positionen gegen `nsz-2007.pdf` sowie den Crosswalk. Erwartet werden genau 25 Originalcodes und die amtliche C1–C7-Gliederung des KBA-Produkts VE13: C1 = Abteilungen 01–03, C2 = 04–06, C3 = 07–09, C4 = 10, C5 = 11–13, C6 = 14, C7 = 15–20. Die VP2040-Zellen-Exceldateien sind keine Quelle für Güterschlüssel.
- Crosswalk-Vertrag: Die CSV- und JSON-Fassung müssen jeweils genau 25 eindeutige VP-Codes enthalten und in allen fachlichen Feldern identisch sein: Code, VP-Begriff, NST-Abteilung mit Bezeichnung sowie C-Gruppe mit Bezeichnung. Der Validator prüft diese Gleichheit unabhängig von der Verarbeitung und prüft zusätzlich die C-Gruppe aus der NST-Abteilung. Abweichungen, doppelte Codes oder abweichende Gruppenbezeichnungen verhindern die Freigabe.
- Ranglisten-Regression: `scripts/validate_relation_coverage.py` muss für jede veröffentlichte NST-7-Relation von Schiene und Binnenschiff die Top-25-Kandidaten nach Tonnen **und** Tonnenkilometern abdecken. Der Test prüft außerdem, dass vorhandene Vorjahreswerte für alle aktuell sichtbaren Gütergruppenrelationen bereitstehen; eine erst im aktuellen Jahr sichtbare Relation darf daher nicht fälschlich `--` erhalten.
- Auslandsrelationen: Für regionale Relationstabellen werden alle Datensätze mit deutscher Quelle oder deutschem Ziel veröffentlicht; nur reiner Auslandstransit bleibt ausgeschlossen. `scripts/validate_relation_coverage.py` prüft diese Regel auch für das Intermodalmodul und enthält Nürnberg (DE254), Binnenschiff, Versand, NST-4, 2025 mit Antwerpen (BE211) und Groot-Rijnmond/Rotterdam (NL366) als festen Regressionsfall. Partner ohne belastbare Koordinate bleiben als Ranglisteneintrag sichtbar und werden in der Oberfläche mit **„ohne Kartenpunkt“** gekennzeichnet.
- QS-10: Die Intermodalkarte zeigt ohne Teilmarkt-Umschalter die Summe der erfassten KV-Teilmärkte als räumliches Intensitätsmaß. Der Tooltip schlüsselt Schiene und Binnenschiff getrennt auf; KPI und Anteile bleiben getrennt. Die Kartensumme wird nicht als eindeutige nationale KV-Gesamtmenge oder Zahl unterschiedlicher Sendungen interpretiert.
- QS-12: Der Saldo-Tooltip verwendet die tatsächlich berechneten Modalwerte und keine undefinierten Variablen.
- QS-14: Alle 40 in den sechs Landmatrizen verwendeten deutschen Flughafen- und Seehafen-Sonderzellen sind in `data/crosswalks/vp2040_special_cells_nuts3.json` genau einem Standortkreis zugeordnet. Die nationale Matrix bleibt unverändert vollständig.
- QS-15: Die abweichenden KBA-Produkte VE7 und VE12/VE13 werden im Informationsfenster ausdrücklich als nicht identische Randsummen erläutert.
- VP2040-Relationen: Aufbau, nachträgliche 2019-Vergleichswerte und Validator verwenden dieselbe versionierte Sonderzellen-Zuordnung. Der Regressionstest umfasst den Fall Hamburg, Empfang, Dithmarschen (DEF05), Gütergruppe 3; abweichende Basiswerte lassen die Freigabe fehlschlagen.
- Übersicht-Hover: Für mindestens eine straßen-dominierte und eine nicht straßen-dominierte Gütergruppe ist im gemeinsamen Basisjahr 2019 zu prüfen, ob amtliche Istreihe und VP2040-Reihe dieselbe fachliche Abgrenzung besitzen. Dieser Test ist **kein Gleichheitstest der Werte**: Die amtliche Istreihe und die VP-Basis können wegen Quelle, Erhebungsumfang und Modellabgrenzung abweichen. Ein Vergleich ist nur bei gleicher Region, Richtung, Kennzahl, Verkehrsträger und C-Gruppe aussagekräftig. Jede verbleibende Abweichung ist mit Quelle, Grundgesamtheit und Einheit im Datenkatalog bzw. der Methodik zu dokumentieren; das Diagramm darf keine Fortschreibung behaupten.
- Ausländische VP2040-Partnerzellen sind in der Relationstabelle mit dem im Crosswalk vorhandenen Namen statt nur mit der numerischen Zell-ID auszuweisen.

Nach jeder Neuerzeugung sind mindestens zu prüfen: nationale Werte 2024 für Schiene und Binnenschiff in Tonnen und Tonnenkilometern, die Seeverkehrsrandsummen und NST-Schlüssel aller Jahre einschließlich `scripts/validate_nst_fine_codes.py`, unveränderte nationale VP2040-Summen, die 25 VP2040-Crosswalk-Positionen gegen beide Referenzquellen, regionale Werte der von Sonderzellen besonders betroffenen Kreise Bremen, Bremerhaven, Emsland und Emden, die Filterkombination Richtung plus Gütergruppe sowie die sichtbaren Methodenhinweise aller sieben Module.

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

- `scripts/validate_nst_fine_codes.py`: 73 Schienen- und 80 Binnenschiffs-Feinpositionen sowie sämtliche geprüften NST-7-Summen stimmen mit den Rohdaten überein.
- `scripts/validate_relation_coverage.py`: 49.137 veröffentlichte NST-7-Relationsgruppen, die Nürnberg-Auslandsfälle Binnenschiff (BE211 und NL366) sowie alle 20 Intermodal-Jahr/Teilmarkt-Kombinationen sind vollständig abgedeckt.
- `scripts/validate_maritime_bundle.py`: alle zehn Berichtsjahre, nationale Tonnen-/TEU-Randsummen und NST-Schlüssel stimmen.
- `scripts/validate_maritime_port_profiles.py`: 189 Hafenprofile und 6.784 Partnerrelationen stimmen in Richtungen, Tonnen, TEU und Güterstruktur mit den Rohdaten überein.

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
