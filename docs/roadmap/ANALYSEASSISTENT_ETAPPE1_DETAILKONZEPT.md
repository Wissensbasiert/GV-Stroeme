# Analyseassistent – Etappe 1: Detailkonzept und Abgleich mit vorhandenen Daten

**Stand:** 08.09.2026 · **Status:** prüfbarer Entwurf; fachliche Bestätigung ausstehend.

## 1. Ziel, Umfang und Lesereihenfolge

Ausgangspunkt sind Akteursfragen, nicht Datenfelder. Die [160 Kandidatfragen aus acht Perspektiven](ANALYSEASSISTENT_ETAPPE1_KANDIDATFRAGEN.md) bleiben deshalb als breiter Bedarfspool erhalten. Danach werden die Fragen mit dem vorhandenen Bestand abgeglichen. Die Auswahl ist eine Nutzungshypothese, keine dokumentierte Akteursbefragung.

**Verbindliche Abgrenzung nach Rückmeldung des Projektverantwortlichen:** Es werden ausschließlich vorhandene Dashboardbestände und bereits vorhandene Rohdaten berücksichtigt. Das Dashboard erhält durch diesen Auftrag keine weiteren Daten oder Funktionen. Zusätzliche Aufbereitungen bestehender Rohdaten für den Assistenten dürfen als fachlicher Prüfbedarf vorgeschlagen werden. Externe Datenbeschaffung, neue Umweltbilanzen, Kapazitätsanalysen, betriebliche Transportketten, Kosten-/Servicebewertungen und zusätzliche Szenariomodelle gehören nicht zum geplanten Ausbau. Auch ein vorhandener Transportkettenordner begründet hier keinen Auftrag zur Erweiterung um Transportkettenanalysen.

Damit unterscheiden wir eine **Datenaufbereitungslücke innerhalb des Bestands** von einer **bewussten Leistungsgrenze**. Fragen außerhalb des Umfangs bleiben im Bedarfspool sichtbar, werden aber weder als künftige Funktion zugesagt noch in ein Beschaffungsprogramm übersetzt.

Die Ergebnisse umfassen dieses Detailkonzept, die Kandidatfragen, den [45 Fälle umfassenden Testkatalog](ANALYSEASSISTENT_ETAPPE1_TESTKATALOG.md) und den [Prüfnachweis](ANALYSEASSISTENT_ETAPPE1_PRUEFNACHWEIS.md). Es wurden nur Dokumente erstellt und Daten lesend geprüft. Keine Modell-, Portal-, Pipeline- oder Codeumsetzung.

Der maßgebliche [Qualitätssicherungsplan](../qualitaet/QUALITÄTSSICHERUNGSPLAN.md), Abschnitt 10.9, dokumentiert am 01.09.2026 alle zehn manuellen Fälle als bestanden. Ältere Angaben der Roadmap zu acht offenen Fällen sind überholt. Die fachliche Bestätigung dieses neuen Katalogs und die Festlegung eines freigegebenen Datenstands für einen späteren Modellvergleich bleiben gesonderte Schritte. Die bereits bearbeitete Roadmap wurde erhalten.

## 2. Datenvertrag vor jeder Zahlenantwort

| Dimension | Festzulegende Bedeutung |
|---|---|
| Raum | eindeutige Region, Hafen, Flughafen, Gemeinde oder Quelle-Ziel-Paar; ID als Text; Gebietsstand; bei Regionsverbünden Liste ganzer Quellgebiete |
| Zeit | explizites Jahr/Monat, gemeinsames vollständiges Vergleichsjahr, Ist oder vorhandenes Prognoseszenario; Quellenstand und Vollständigkeit |
| Güter | alle Güter, C1–C7, NST-Abteilung oder belegte Feinposition; zulässige Tiefe je Quelle; geprüfter Umstiegsschlüssel |
| Richtung | Versand, Empfang, Binnen, nationale Verkehrsbeziehung/Transit oder beide Richtungen; interne Zählung explizit |
| Verkehrsträger | Straße, Schiene, Binnenschiff; See/Luft als eigenständige Knotenstatistik; keine neue vollständige Transportkettenbilanz |
| Kennzahl | t, tkm, TEU, Mautfahrten, quellenbezogene Fahrten/Ladeeinheiten/Flüge; Zähler, Nenner, Sortierung und Skalierung |
| Qualität | gültige Null, fehlend, nicht veröffentlicht, eingeschränkt belastbar, beobachtet oder prognostiziert; Quellenkennzeichen erhalten |

„Aktuell“ muss auf ein konkret genanntes vollständiges gemeinsames Jahr aufgelöst werden. Ausdrücklich gewünschte fehlende Jahre werden nicht still ersetzt. „Wichtigste“ oder „stärkste“ benötigt eine bestätigte Kennzahl und absolute/relative Sortierung. Ein offener Regionsbezug führt zur Rückfrage.

## 3. Fünfzehn fachliche Fragetypen innerhalb des vorgesehenen Umfangs

Die Typen wurden nach der Akteurssammlung gebildet. Sie bündeln beantwortbare Auskünfte, sinnvolle Rohdatenprüfungen und zugehörige fachliche Grenzfälle. Sie sind noch keine implementierten Funktionen.

| Typ | Parameter und Erkenntnisinteresse | Ergebnislogik / Kennzahl / Einheit | Antwortformat und Grenze |
|---|---|---|---|
| F01 Regionsprofil und Kurzfassung | Region, gemeinsames Jahr, Landverkehr, Güter, vereinbarter Profilumfang | Mengen t, Güter-/Modalanteile %, Saldo t; Prognose getrennt | Kurzfazit und Tabelle; keine Wirkungs- oder Standortqualität aus Mengen ableiten |
| F02 Konkrete Verbindungen und Partner | Quelle/Ziel oder Fokusregion, Jahr, Modus, Richtung, Güter soweit verfügbar, Top-N, Binnenfilter | vollständige OD-Grundgesamtheit je Partner aggregieren, dann nach t/tkm sortieren; Anteile mit passendem Nenner | Verbindungstabelle/Rangliste; kein Wegverlauf oder buchbares Angebot |
| F03 Regionsvergleich | mindestens zwei gleich abgegrenzte Regionen, gemeinsames Jahr, gleiche Filter; ganze Regionsverbünde gesondert | Werte/Differenzen t/tkm; Strukturanteile %, Differenz Prozentpunkte | Vergleichstabelle; keine Mischung Stadt/Terminal oder ungleicher Jahre |
| F04 Zeitverlauf und Vergleichbarkeit | Region/Relation, Zeitraum, Modus, Richtung, Güter, Gebietsstand | Jahresreihe, Δt/Δtkm/Δ%; Lücken und Brüche markieren | Zeitreihe plus Einordnung; keine unbelegte Ursache |
| F05 Änderungsranking und Anteilszerlegung | vergleichbare Regionen/Güter, Basis/Ziel, absolutes/relatives Rangmaß, Mindestbasis | Änderung vor Rundung sortieren; Basiswerte mitliefern; Anteilseffekt von Mengenentwicklung unterscheiden | Rangliste mit beiden Werten; kleine Basen nicht verdecken |
| F06 Regionale Güterstruktur | Region, Jahr, Modus, Richtung, C-Gruppen oder verfügbare NST-Tiefe | Gütersummen und Anteil an passender Grundgesamtheit, t/tkm/% | Gütertabelle; Straße NUTS-3 nur sieben Gruppen |
| F07 Güter auf einer Verbindung | konkrete OD, Jahr, Modus, Richtung, belegte Gütertiefe | je Gütergruppe summieren, Anteil am OD-Gesamtwert | Tabelle; Straßen-OD nur Gesamt, feinere Schienen-/IWW-Rohgliederung ggf. prüfen |
| F08 Modal Split | Region/Deutschland, vollständiges Jahr, t oder tkm, kompatible Güter/Richtung | Teilwert durch vollständige Summe der drei Landverkehrsträger, % | Mengen plus Nenner/Anteile; kein vollständiger Modal Split bei fehlender Straße |
| F09 Versand, Empfang, Binnen und Transit | Gebiet/OD, Jahr, Modus, Richtung und Zählweise | Saldo=Versand−Empfang, t/tkm; Binnen separat; nationaler Transit aus Verkehrsbeziehung | Richtungstabelle; örtlicher Transit benötigt Wege und bleibt unbelegt |
| F10 Vorhandene Verkehrsprognose | 2019_BASE/2040_P1, gleiche Raumgrundlage, Modus, Güter, Richtung | Basis/Ziel und Δt/Δtkm/Δ%; Ist getrennt daneben | Prognosetabelle; keine weiteren Szenarien, keine erfundene Zwischenprognose |
| F11 Statistische intermodale Teilmärkte | Schiene/Binnenschiff, Jahr, nationale/regionale Abgrenzung, Richtung, t/tkm | qualifizierte Menge durch jeweiligen Gesamtmodus, % | getrennte Teilmarkttabelle; kein KV-Kettengesamtwert und kein Verlagerungspotenzial |
| F12 Hafen- und Flughafenstatistik | identifizierter Knoten, Jahr, Richtung, verfügbare Güter/Maße/Partner | t, TEU oder reine Fracht-/Postflüge; Vergleich mit passender Quelle | Knotenprofil/Partnerliste; Veröffentlichungsschwellen und unterschiedliche Nenner |
| F13 Monatsdaten und Mautvergleich | Region/Knoten/Gemeinde, Monat, Richtung, Maß und Vergleichsmonat | t/Monat aus amtlichen Rohdaten oder Mautfahrten, absolute/relative Änderung | Monatsreihe; keine Wochen-/Betriebs- oder Personalplanung aus Jahreswerten |
| F14 Zusätzliche vorhandene Straßendetails | VD2-/VD3c-Regionsebene, Jahr, deutsche Lkw, Richtung, Inland/Gesamt | Fahrten/t/tkm nach amtlichen Entfernungsstufen bzw. NST-20 | Tabelle; andere Grundgesamtheit als VE, keine künstliche Verfeinerung |
| F15 Quelle, Machbarkeit und Grenzen | konkrete Frage/Zahl, alle Dimensionen und Datenversion | Quellen-/Einheiten-/Vollständigkeitsprüfung; zulässige Teilantwort oder begründete Grenze | Erklärung mit Quellen und Rechenweg; keine externe Datenergänzung als automatischer Folgeauftrag |

### Nachgelagerte Zuordnung aller 160 Fragen

**A:** vorhandener Auswertungsbestand grundsätzlich geeignet, genaue Filter prüfen. **B:** zusätzliche Prüfung/Aufbereitung vorhandener Rohdaten nötig. **T:** nur fachlich eingegrenzte Teilantwort. **G:** bewusste Datengrenze innerhalb eines Typs. **X:** außerhalb des vorgesehenen Umfangs, keine Ausbauzusage. Diese Einstufung ersetzt keine Prüfung aller Kombinationen.

| Frage | Perspektive | Typ / Status | Abdeckungsentscheidung |
|---|---|---|---|
| Q001 | P1 | F01 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q002 | P1 | F01 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q003 | P1 | F03 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q004 | P1 | F02 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q005 | P1 | F04 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q006 | P1 | F06 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q007 | P1 | F09 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q008 | P1 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q009 | P1 | F13 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q010 | P1 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q011 | P1 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q012 | P1 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q013 | P1 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q014 | P1 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q015 | P1 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q016 | P1 | F15 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q017 | P1 | F03 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q018 | P1 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q019 | P1 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q020 | P1 | F04 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q021 | P2 | F08 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q022 | P2 | F10 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q023 | P2 | F05 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q024 | P2 | F02 / T | OD-Beziehungen beschreibbar; tatsächliche Verkehrswege/Korridorbelastung nicht belegt. |
| Q025 | P2 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q026 | P2 | F09 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q027 | P2 | F03 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q028 | P2 | F10 / G | Alternativer Kohlebedarf ist kein vorhandenes Szenario; nur veröffentlichte VP-Güterentwicklung beschreibbar. |
| Q029 | P2 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q030 | P2 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q031 | P2 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q032 | P2 | F10 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q033 | P2 | F10 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q034 | P2 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q035 | P2 | F10 / G | Nur vorhandenes P1 und Basisjahr; keine neue Szenariomodellierung. |
| Q036 | P2 | F06 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q037 | P2 | F03 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q038 | P2 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q039 | P2 | F14 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q040 | P2 | F15 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q041 | P3 | F06 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q042 | P3 | F03 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q043 | P3 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q044 | P3 | F02 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q045 | P3 | F05 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q046 | P3 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q047 | P3 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q048 | P3 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q049 | P3 | F02 / T | Partnerkonzentration beschreibbar; betriebliche Versorgungsabhängigkeit nicht belegt. |
| Q050 | P3 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q051 | P3 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q052 | P3 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q053 | P3 | F01 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q054 | P3 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q055 | P3 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q056 | P3 | F04 / T | Vorher/Nachher beschreibbar; Werkswirkung nicht nachgewiesen. |
| Q057 | P3 | F02 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q058 | P3 | F12 / T | Flughafenprofil möglich; kein vollständiges regionales Luftfracht-Wirtschaftsprofil. |
| Q059 | P3 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q060 | P3 | F15 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q061 | P4 | F02 / T | Statistische Partner je Knoten-/Regionsquelle; vollständige Hinterlandketten nicht belegt. |
| Q062 | P4 | F07 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q063 | P4 | F02 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q064 | P4 | F12 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q065 | P4 | F12 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q066 | P4 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q067 | P4 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q068 | P4 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q069 | P4 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q070 | P4 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q071 | P4 | F11 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q072 | P4 | F13 / T | Amtliche Monate prüfbar; Personalbedarf und Terminalspitzen nicht ableitbar. |
| Q073 | P4 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q074 | P4 | F12 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q075 | P4 | F12 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q076 | P4 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q077 | P4 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q078 | P4 | F10 / T | VP-Gebiet oder Sonderzelle klären; kein betrieblicher Terminalforecast. |
| Q079 | P4 | F13 / T | Monatsdaten ggf. Rohaufbereitung; Wochenverlauf nicht nachgewiesen. |
| Q080 | P4 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q081 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q082 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q083 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q084 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q085 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q086 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q087 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q088 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q089 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q090 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q091 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q092 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q093 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q094 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q095 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q096 | P5 | F07 / G | Straßen-OD enthält keine Güterstruktur; regionale Güteranteile ersetzen sie nicht. |
| Q097 | P5 | F02 / T | Statistisches Relationsaufkommen als Kontext; keine gesicherte betriebliche Nachfrage. |
| Q098 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q099 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q100 | P5 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q101 | P6 | F02 / T | Mengenvergleich möglich; Tragfähigkeit eines Linienangebots nicht belegt. |
| Q102 | P6 | F09 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q103 | P6 | F07 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q104 | P6 | F05 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q105 | P6 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q106 | P6 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q107 | P6 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q108 | P6 | F13 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q109 | P6 | F13 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q110 | P6 | F13 / T | Nur tatsächlich vorhandene Maut-Distanz-/Fahrzeitmerkmale nach Quellenprüfung; keine betriebliche Routenrekonstruktion. |
| Q111 | P6 | F14 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q112 | P6 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q113 | P6 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q114 | P6 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q115 | P6 | F10 / T | VP-Marktentwicklung als Kontext; kein unternehmensbezogener Nachfrageforecast. |
| Q116 | P6 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q117 | P6 | F11 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q118 | P6 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q119 | P6 | F15 / T | Quellabgrenzungen beschreiben; nicht beobachtete Mengen nicht schätzen. |
| Q120 | P6 | F13 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q121 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q122 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q123 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q124 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q125 | P7 | F08 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q126 | P7 | F05 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q127 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q128 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q129 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q130 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q131 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q132 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q133 | P7 | F10 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q134 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q135 | P7 | F15 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q136 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q137 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q138 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q139 | P7 | F15 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q140 | P7 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q141 | P8 | F15 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q142 | P8 | F15 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q143 | P8 | F04 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q144 | P8 | F15 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q145 | P8 | F15 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q146 | P8 | F02 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q147 | P8 | F06 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q148 | P8 | F10 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q149 | P8 | F04 / T | Auffälligkeit und Prüfbedarf darstellbar; Ursache ohne Zusatzbeleg offen. |
| Q150 | P8 | X | Außerhalb: erfordert zusätzliche externe/betriebliche Daten oder ein neues Wirkungs-, Kosten-, Umwelt-, Kapazitäts- oder Standortmodell. |
| Q151 | P8 | F03 / T | Ganze Quellgebiete aggregierbar; geschnittene Teilgebiete nicht ohne Modell. |
| Q152 | P8 | F05 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q153 | P8 | F11 / G | Keine Addition beider Teilmärkte zu eindeutigen KV-Ketten. |
| Q154 | P8 | F10 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q155 | P8 | F01 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q156 | P8 | F15 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q157 | P8 | F15 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q158 | P8 | F15 / B | Vorhandene Rohdaten/Geometrien bzw. bestehende Anbindung prüfen und bei Nutzen zusätzlich aufbereiten. |
| Q159 | P8 | F15 / A | Statistische oder methodische Auskunft aus dem Bestand; Dimensionen und Quellenvertrag des Typs gelten. |
| Q160 | P8 | F04 / T | Revision nur bei tatsächlich vorhandenen Vergleichsständen; keine historische Serie erfinden. |

Die genaue Frage steht unter derselben Q-ID im Kandidatenpool. T-/G-/X-Fragen werden nicht gelöscht. Für T wird nur der genannte Teil unterstützt, für G/X ist die begründete Grenze das erwartete Antwortverhalten. Etwa Q096 ist keine Aufforderung, Straßen-Güteranteile zu modellieren.

## 4. Tatsächlich geprüfter Bestand und Quellenverträge

Quellen-IDs D01–D10 gelten auch im Testkatalog. Sie umfassen den Herausgeber und den konkreten lokalen Bestand. Ein Quellenhinweis muss zusätzlich das tatsächlich verwendete Jahr und die Filter enthalten. Die Rohquellen wurden hinsichtlich Schema und ausgewählter Werte gelesen; keine vollständige erneute Datenfreigabe und keine externe Datenbeschaffung.

| ID | Vorhandene Datenbasis und Originalquelle | Verwendbare Felder/Dimensionen | Bestätigte Grenze |
|---|---|---|---|
| D01 | `data/processed/web_summary_by_region.json`; KBA VE12/VE13, Destatis EVAS 46131 und 46321 | Region → Jahr; `modes_tonnes`, `modes_tkm`, `modes_direction_*`, `groups_7_*`, `by_mode_groups`, `by_mode_divisions`; t/tkm; Webzeitraum ab 2016, Straße bis 2024 | Regionaler Gesamtwert summiert Versand und Empfang einschließlich interner Bewegungen in beiden Richtungen. Straße: C1–C7, keine 20er-Gliederung auf NUTS-3. Zusammengefasste 20er-Felder enthalten nicht den Straßenanteil. |
| D02 | `data/processed/fact_od_flows.parquet`; KBA VE7, Destatis EVAS 46131/46321; zugehörige Rohdateien | `year_ref`, `origin_nuts`, `dest_nuts`, `mode_transport`, `group_7_id`, `tonnes`, `tkm`, `trips`; Straße 2010–2024, Schiene 2016–2025, Binnenschiff 2011–2025 | 498.143 Zeilen; Straße nur `ALL`, Schiene/Binnenschiff C1–C7. Vollständig gegenüber der Top-Auslieferung, aber kein Nachweis vollständiger Erfassung aller realen Transporte. Rohzeilen ohne räumliche Zuordnung können fehlen. Qualitätsflags nicht im Schema. `trips` ist verkehrsträgerübergreifend keine einheitliche Fahrtenkennzahl. |
| D03 | `data/processed/national_benchmarks.json`; KBA VE7 und vollständige Destatis-Rohreihen | Jahr, `total_tonnes`, `total_tkm`, `modes` | Nationaler Straßen-tkm-Wert nutzt `Inlands_tkm`; regionale Straßenwerte haben einen anderen Leistungsbezug. Transit/Rohzeilen ohne regionale Zuordnung können in nationalen Werten enthalten sein. 2025 fehlt Straße. Keine Summe regionaler Umschlagwerte als Ersatz. |
| D04 | KBA-Rohdaten unter `data/raw/Straße/KBA/`; SGV-/IWW-Rohdateien; Klassifikation unter `data/crosswalks/` | VE7: `ZS_Tonnen`, `ZS_Tkm`, Verkehrsbeziehung; VE12/13: regionale C-Gruppen; VD2: Entfernungsstufen; VD3c: 20 Abteilungen auf NUTS-2; SGV/IWW: Monate, feinere Gütercodes und Ladeeinheiten | VD-Reihen betreffen deutsche Lkw; Wechsel von VE auf VD ist ein Wechsel der Grundgesamtheit. Vor jeder Ergänzung Feldsemantik, Quellenkennzeichen und Monatsvollständigkeit prüfen. C-Gruppen nach aktuellem Crosswalk-README: C1=01–03, C2=04–06, C3=07–09, C4=10, C5=11–13, C6=14, C7=15–20. |
| D05 | `web_forecast_2040.json`, `web_forecast_core.json`; VP2040, BMDV/Intraplan/Trimode/ETR/MWP; Originalmatrizen und Transportketten unter `data/raw/VP2040/` | `scenarios.2019_BASE`, `scenarios.2040_P1`, `national`, `regions`; t/tkm, Verkehrsträger, C-Gruppen/VP-Gruppen, Richtungen | Regionaler Gesamtwert = externer Versand + externer Empfang + Binnenverkehr einmal. Gleiche Prognosebasis für 2019/2040; kein gemessener Ist-Verlauf bis 2040. Sonderzellen und Crosswalk beachten. Transportkettenordner vorhanden; daraus wird in diesem Auftrag keine zusätzliche Transportkettenanalyse abgeleitet. |
| D06 | `data/processed/web_intermodal.json`, Schema 3; Destatis EVAS 46131/46321 | `data_by_year`, `scoped_metrics_by_year`, `relations_by_year`; 2016–2025; Schiene mit Ladeeinheiten, Binnenschiff mit Containern; regional/Richtung im aktuellen Bestand vorhanden | `not_additive=true`; beide Teilmärkte nicht zu einer nationalen eindeutigen Transportkettenmenge addieren. Regionale und nationale Nenner nicht tauschen. Keine Terminals, Tarife oder freien Kapazitäten. |
| D07 | `data/processed/web_maritime.json` und Hafenprofile aus der aktiven Hafenaufbereitung; Destatis EVAS 46331, Rohdaten `data/raw/MRTM OpenData/` | nationale und Hafen-Umschläge, t, TEU, Güter, Partner; ausgelieferte Jahre 2016–2025 | Seeseitiger Hafenumschlag ist keine vollständige Hinterlandkette; TEU sind kein Gewicht, Mengen nicht mit Landverkehr zu eindeutigen Lieferketten addieren. Monats-/Leercontainerbedarf gegen Rohfelder prüfen. |
| D08 | `data/processed/web_airfreight.json`; Eurostat AVIA_GOOC, AVIA_GOOA, AVIA_GOR_DE | `national`, `airportValues`, `relations`, `relationTotals`, `metadata`; t und reine Fracht-/Postflüge | 2016–2025 für nationale/Flughafen-Tonnage; Flughafen-Flüge nur bis 2024; Relationen nur bis 2024, Top 25 gespeichert, Veröffentlichungsschwellen. Nationalwert und Summe der Flughafenwerte sind unterschiedlich abgegrenzt. |
| D09 | Mautmodul und Datenkatalog; BALM/Toll Collect, gemeindebezogene Start-Ziel-Abfragen | AGS als Text, Monat, Richtung, `anzahl_befahrungen`, dokumentierte Fahrleistungs-/Distanz-/Fahrzeitmerkmale | Live-Verfügbarkeit in dieser Etappe nicht erneut abgerufen. Keine Tonnen oder Güterarten. Keine bundesweite Komplettabfrage der Relationsdaten. Ein festes, zulässig abgefragtes Testabbild fehlt noch. |
| D10 | NUTS-Geometrien 2016/2021/2024, regionale Metadaten, VP-Raumcrosswalk, Sonderzellen-Zuordnung; Eurostat/GISCO und projektbezogene Aufbereitung | Gebiets- und Knoten-IDs, Namen, Geometrien, räumliche Umstiege | Geometrie ist kein Verkehrsnetz. Ein neuer Kartengebietsstand harmonisiert keine Zeitreihe. Frei geschnittene Kreisanteile liefern keine beobachtete kleinräumige Güterverteilung. |

### Festgestellte Dokumentations- und Bestandsunterschiede

- Das Fachkonzept beschreibt Intermodalität noch als rein national ohne Richtungsfilter. D06 enthält inzwischen regionale und richtungsbezogene Werte. Für neue Testfälle ist das tatsächlich gelesene Schema maßgeblich.
- `fact_regional_summary.parquet` enthält Straßenwerte nur unter `ALL`; die regionale Straßen-Güterstruktur stammt aus VE12/VE13 beziehungsweise D01. Beide Dateien sind kein austauschbarer Regionalwürfel.
- `dim_nst2007.json` enthält eine von der aktuellen C1–C7-Zuordnung abweichende Gliederung. Im Katalog wird der dokumentierte aktuelle Crosswalk mit den aktiven Zuordnungsregeln verwendet. Diese Datei wird nicht korrigiert oder als Begriffsautorität herangezogen.
- Die Ist-Zusammenfassung und die VP-Prognose behandeln Binnenbewegungen unterschiedlich. Auch bei identischen Gebiets-IDs ist ein unmittelbares prozentuales Mischen beider Gesamtwerte nicht freigegeben.
- KBA-Quellkennzeichen sind in D02 nicht erhalten. Bei der Stichprobe Hamburg 2024 enthielten 169 von 207 berührenden VE7-Zeilen das Kennzeichen `( )` für Tonnen. Die zehn Richtungszeilen der ermittelten Top-5-Außenpartner hatten kein solches Kennzeichen. Die Bedeutung und Weitergabe der Kennzeichen bleibt Bestandteil von B01; eine fehlende Kennzeichnung im Webbestand beweist keine uneingeschränkte Belastbarkeit.

Diese Punkte sind Arbeitsaufträge für die spätere Datenvorbereitung, keine in dieser Etappe erledigten Korrekturen.

## 5. Sinnvoll zu prüfende Aufbereitungen bereits vorhandener Daten

Die folgenden sieben Prüfpakete sind ausschließlich fachliche Vorschläge, keine Implementierung und keine Dashboarderweiterung. Quelle, Aufwand, Abdeckung und Nutzen sind vor einer Umsetzung zu bestätigen. Externe Datenquellen und neue Modellbilanzen werden nicht vorbereitet.

| Paket | Fragebezug | Vorhandene Grundlage / fehlender Schritt | Abnahme und Nutzen |
|---|---|---|---|
| B01 Vollständige OD und Quellenkennzeichen | Q004, Q062, Q141, Q144, Q146 | D02/D04; vollständige Abfragen statt Top-Dateien, ZS-/Fehlstatus je Kennzahl aus der Originalquelle mitführen | OD gegen Rohquelle; nicht angezeigte Verbindung auffindbar; Null/fehlend/markiert bleiben verschieden; keine erfundenen Straßen-OD-Güter |
| B02 Monats- und Zeitvergleich | Q005, Q020, Q072, Q079, Q143, Q160 | SGV/IWW-Monate in D04, vorhandene Jahres-/Gebietsstände; Monatswürfel und Vergleichbarkeitskennzeichnung prüfen | zwölf vollständige Monate stimmen zur Jahressumme; Gebietsbruch sichtbar; historische Revision nur bei vorhandenem früherem Stand. Wochen-/Tagesbetriebswerte nicht ergänzen |
| B03 Vorhandene Güter- und Straßendetails | Q039, Q062, Q065, Q103, Q111 | D04: NST-Feinpositionen, Ladezustand; VD2/VD3c; getrennte Aufbereitung auf amtlich verfügbarer Raumebene | C-Summen stimmen; VD-Population deutscher Lkw und NST-20 auf NUTS-2 benannt; keine VE-NUTS-3-Verfeinerung oder technische Sendungseignung behaupten |
| B04 Ganze Regionsverbünde und Raumvergleich | Q017, Q027, Q151 | D02/D10; Liste ganzer Regionen, intern/extern sowie Geometrie-/Gebietsstand | interne OD einmal, externe Richtungen korrekt; keine proportionale Kreiszerlegung, Route oder lokale Transitmodellierung. Für regionale Güter zusätzlich deren jeweilige Quellabgrenzung beachten |
| B05 Nationale Verkehrsbeziehungen | Q007, Q026, Q037 | D04: Hauptverkehrsbeziehung/Verkehrsbeziehung, nationale Vollquellen | Binnen, grenzüberschreitender Versand/Empfang und Transit nach Originaldefinition; Nationalrandsumme rekonstruierbar; örtlicher Durchgangsverkehr bleibt außerhalb |
| B06 Vollständige veröffentlichte Knotenrelationen | Q061, Q064, Q075 | D07/D08 plus bereits vorhandene See-/Luft-Rohdateien; Publikationsgrenzen und passende Nenner über die gespeicherten Top-Einträge hinaus prüfen | nur publizierte Grundgesamtheit behaupten; t/TEU/Flüge getrennt; keine Hinterland-Transportkette aus Hafenumständen ableiten |
| B07 Prüfbare Maut-Monatsstände | Q009, Q108, Q109, Q110, Q120 | bestehende D09-Anbindung für zulässige gezielte Gemeindeabfragen; festes Abbild je Prüfmonat und Richtungsfilter fehlt | AGS als Text, gleiche Monate/Richtungen, Binnenzählung; keine bundesweite Komplettabfrage, keine Umrechnung zu Gütertonnen. In dieser Etappe keine Live-Abfrage ausgeführt |

**Priorität als Vorschlag:** zuerst B01 und die nötigen Teile von B02 für die sechs UI-Beispiele; danach B03/B05/B06 dort, wo ein konkreter Akteursfall zusätzliche fachliche Tiefe braucht. B04 erfordert eine bestätigte Regionsdefinition; B07 einen festen zulässigen Teststand. Keine automatische Umsetzung aller Pakete.

**Bewusste Grenzen:** Kosten, Bedienangebote, Zuverlässigkeit, Kapazität, technische Gütereignung, Umwelt-/Wirkungsbilanzen, Standortoptimierung und vollständige betriebliche Transportketten bleiben außerhalb. Der Assistent erklärt dies sachlich und kann passende beobachtete Verkehrskennzahlen als ausdrücklich begrenzten Kontext anbieten. Er verspricht weder externe Beschaffung noch Modellierung. Vorhandene nationale/regionale intermodale Statistiken und vorhandene VP-P1-Werte bleiben nutzbar; sie sind keine neuen Ketten- oder Kapazitätsanalysen.

## 6. Gemeinsame Ergebnis- und Prüfregeln

**R1 – Zahlenherkunft:** Jede Zahl stammt aus einer benannten Quelle oder einer offengelegten Rechenoperation. Synthetische Prüfwerte bleiben als solche bezeichnet. Beobachtung, Schätzung und Prognose werden getrennt.

**R2 – Summen und Binnenverkehr:** D01 entspricht der Summe von Versand und Empfang; eine Binnenbewegung kann dabei zweimal enthalten sein. Für eindeutige OD-Mengen wird D02 mit jeder Zeile einmal ausgewertet. Für eine Regionsvereinigung gilt Quelle/Ziel innerhalb der Menge = intern einmal, genau eine Seite innerhalb = extern. D05 und die regionalen D06-Werte zählen Binnenverkehr separat einmal. Quellen mit unterschiedlichen Zählweisen werden nicht unmittelbar verrechnet.

**R3 – Nationale Abgrenzung:** Deutschlandwerte werden aus nationaler Datenbasis gelesen. D03 enthält bei Straße die Inlandsverkehrsleistung; regionale D01/D02-tkm sind keine streckengenaue Verkehrsleistung innerhalb der betreffenden Region. See-/Luftumschlag und Landverkehr nicht zu einer eindeutigen Gütergesamtmenge addieren.

**R4 – Anteile:** Anteil = 100 × Teilwert / kompatibler Gesamtwert. Nenner positiv und vollständig; aus Schiene und Binnenschiff allein entsteht kein vollständiger Landverkehrs-Modal-Split für 2025. Teilmarktanteile des KV bleiben getrennt. Salden erhalten keinen Modal Split.

**R5 – Änderungen:** Δ = Zielwert − Basiswert; Rate = 100 × Δ / Basiswert nur bei Basis > 0. Basis 0/Ziel > 0: absoluter Zuwachs, Rate nicht definiert. Basis > 0/Ziel 0: −100 %. Beide 0: Δ=0, Rate nicht definiert. Fehlend bleibt fehlend. Salden werden absolut verglichen, nicht mit Wachstumsraten.

**R6 – Rankings:** Grundgesamtheit zuerst vollständig filtern und je Partner/Region/Gut aggregieren; danach nach ungerundetem Wert sortieren. Gleichstände behalten gleichen Rang (1, 2, 2, 4), sekundär ID aufsteigend. Ein Gleichstand am Top-N-Rand wird vollständig angezeigt und die Überschreitung erläutert. Prozent-Rankings benötigen eine bestätigte Mindestbasis oder einen deutlichen Hinweis auf kleine Basen; kein stiller Schwellenwert.

**R7 – Fehlende und eingeschränkte Daten:** Nicht vorhandene Zeilen sind ohne Quellenbeleg keine gemessene Null. Veröffentlichungsschwellen, Geheimhaltung/Qualitätskennzeichen und nicht verfügbare Kombinationen bleiben unterscheidbar. Ein allgemeines Default-Null darf keine Datenlücke verdecken. Ungeprüfte Flagbedeutungen werden nicht erfunden.

**R8 – Güter und Einheiten:** Codes bleiben Text, etwa `01`, `DEA12` oder ein achtstelliger AGS. C1–C7 nach D04; keine rückwärtige Aufteilung einer C-Gruppe auf Detailgüter. t, tkm, Fahrten, Ladeeinheiten, TEU und Flüge nicht austauschen. Kosten-, Umwelt- und Kapazitätskennzahlen gehören nicht zum vorgesehenen Antwortumfang.

**R9 – Zahlenformat:** intern mit den verfügbaren ungerundeten Werten rechnen, am Ende skalieren. Nachkommastellen orientieren sich an Quellpräzision; Standarddarstellung 0,1 Mio. t bzw. 0,1 Prozent/Prozentpunkte, kleine Werte in t statt scheinbarer Null. Quellenwerte im Prüfnachweis bleiben genauer. Keine Toleranz rechtfertigt einen falschen Nenner oder eine fehlende Dimension.

**R10 – Antwortumfang:** zuerst Befund, anschließend kompakte Tabelle, abschließend Quelle und wesentliche Einschränkung. Bei unklarer Eingabe gezielte Rückfrage. Bei fehlenden Daten: vorhandene Rohquelle und gegebenenfalls sinnvolle Aufbereitung nennen oder die bewusste Leistungsgrenze erklären; kein externer Datenauftrag und kein erfundener Zahlenersatz. Unpassende aktive Filter werden offengelegt und nicht still als angewendet ausgegeben.

## 7. Auswahl und fachliche Bestätigung

45 Fälle decken alle 15 Typen ab, einschließlich der sechs unveränderten UI-Beispielfragen. Aus dem breiten Pool werden beantwortbare Fragen, relevante Rohdatenlücken und notwendige Grenzfälle ausgewählt. Die Anzahl der Nennungen in der Sammlung belegt keine Nachfragehäufigkeit. Synthetische Beispiele dienen ausschließlich der Prüfung allgemeiner Rechen-, Aggregations- und Fehlwertregeln; es werden keine hypothetischen Umwelt-, Kosten- oder Kapazitätsprodukte mehr als Zielantwort definiert.

Je Testfall müssen Frage, Parameter, zulässige Datenbasis, Kennzahl, Einheit, Originalquelle, Einschränkung und erwartete Ergebnislogik bestätigt werden. „Rohdaten vorhanden“ reicht nicht als Freigabe einer neuen Aufbereitung. Vor einem Modellvergleich sind die tatsächlich verwendeten Zahlenfälle an einen freigegebenen Datenstand zu binden.

**Offen für die fachliche Bestätigung:** Akteursbreite; Auswahl der 15 Typen; Binnen-/National-/Prognosezählung; Qualitätshinweise; Nutzen und Reihenfolge B01–B07. Kein fehlender externer Datensatz blockiert den definierten Umfang: entsprechende Fragen sind bewusst begrenzte Fälle. Erstellung und lesende Kontrollrechnung sind abgeschlossen, die Bestätigung durch den Projektverantwortlichen ist nicht vorweggenommen.
