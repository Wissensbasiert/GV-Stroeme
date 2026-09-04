# Qualitätssicherungsplan für das Güterströme-Dashboard

**Stand:** 04.09.2026

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
