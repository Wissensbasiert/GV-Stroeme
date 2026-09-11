# Roadmap: Analyseassistent, Premiumzugang und Portalbetrieb

**Ausbau vom 11.09.2026:** Verfügbarkeitskatalog, signierter Gesprächsstand, geprüfte kurze Anschlussfragen und belegte Erläuterungen sind implementiert; Beta-Kennzeichnung, kundenorientierter Hover und Entfernung der technischen Antwortdetails gehören dazu. 83 lokale Prüfungen, der begrenzte echte Sechs-Eingaben-Vergleich und die gezielte Beta04-Linux-Prüfung bestehen. Einzelheiten und aktueller Bereitstellungsabschluss: [Beta-Prüfbericht](../qualitaet/ANALYSEASSISTENT_BETA_20260911.md). Die früheren Abschnitte bleiben historische beziehungsweise geplante Stände; keine zusätzliche fachliche Gesamtfreigabe.

**Stand:** 11.09.2026

**Status:** Analyseassistent auf AlwaysData-Testsite 1067000 bereitgestellt; eigenes Administratorkonto mit Premium freigeschaltet. Beta04 ist aktiv und einschließlich der beleggebundenen Mehrjahresauswertung und rechnerischen Veränderungen in der Linux-Laufzeit geprüft. Keine Produktionsfreigabe und keine fachliche Gesamtabnahme aller 45 Antworten.

**Bezug:** Güterverkehrsströme Deutschland und WBP-Solutions-Portal auf AlwaysData

**Aktueller Überblick:** B01–B06 sind geprüft und über begrenzte Adapter angebunden. B07 enthält die geprüften Berliner Monatsauszüge; ein gleichmonatiger Vorjahresvergleich fehlt. Der echte 45-Fälle-Lauf mit geladenem Systemprompt und getrennten Referenzen ist durchgeführt, T30/T44 anschließend gezielt nachgeprüft. Basic 5/Premium 50 je Kalendermonat werden serverseitig je Benutzer und Werkzeug geführt. Version 0.2.1 ergänzt den aktiven Beta04-Stand um Mehrjahresrelation, belegte Kernaussagen und transparente rechnerische Veränderungen. Maßgeblich sind die neuesten Nachträge in Abschnitt 24 und der Qualitätssicherungsplan. Quellen- und Vergleichsgrenzen, insbesondere T13 und der fehlende B07-Vorjahresmonat, bleiben offen.

## 1. Zweck des Dokuments

Dieses Dokument beschreibt die nächsten Schritte, um das bestehende Güterströme-Dashboard in das WBP-Solutions-Portal zu übernehmen und den derzeitigen Interface-Prototyp des Analyseassistenten zu einer belastbaren Produktfunktion auszubauen. Es dient als gemeinsame Roadmap für weitere Arbeitschats und als Ausgangspunkt für die spätere technische Umsetzung.

Ziel ist eine gemeinsame Anwendung mit zwei Nutzungsstufen:

- **Basispaket:** Zugriff auf das Güterströme-Dashboard und fünf erfolgreiche numerische KI-Auswertungen je Kalendermonat.
- **Premiumpaket:** Zugriff auf das Dashboard und 50 erfolgreiche numerische KI-Auswertungen je Kalendermonat. Rückfragen und fehlgeschlagene Analysen belasten das Kontingent nicht.

Die Benutzeroberfläche bleibt grundsätzlich für beide Pakete gleich. Die Berechtigung für den Analyseassistenten wird jedoch serverseitig geprüft und durchgesetzt.

## 2. Historischer Ausgangsstand vor der Umsetzung

- Das Dashboard liegt als statische Browseranwendung mit modular aufgebauten HTML-, CSS- und JavaScript-Quellen vor.
- Ein gestalteter Interface-Prototyp des Analyseassistenten ist lokal integriert. Er besitzt noch keine Verbindung zu einem KI-Modell oder einer serverseitigen Datenschnittstelle.
- Der Prototyp verwendet die Bezeichnung **Analyseassistent** und das Datenkorridor-Symbol `assets/icons/gueterstrom-ki-variante-c-datenkorridor.svg`.
- Ein Informations-Hover im Kopf des Analyseassistenten erläutert die vorgesehene EU-Verarbeitung, die Nutzung der geprüften Datenbasis, den Ausschluss eines Modelltrainings mit Kundenanfragen und die verbleibende Möglichkeit fehlerhafter KI-Erläuterungen.
- Der Entwicklungsstand ist im GitHub-Zweig `ki-interface-prototype` versioniert. Der Hauptzweig bleibt davon getrennt.
- Die automatisierte und browserseitige Korrekturregression des Dashboards ist bestanden.
- In der manuellen Prüftabelle sind H-01 und H-02 bestanden. H-03 bis H-10 bleiben als acht nutzerseitige Freigabefälle offen.

Die fachliche Datenfreigabe ist damit noch nicht abgeschlossen. Maßgeblich ist der jeweils aktuelle Stand in [`QUALITÄTSSICHERUNGSPLAN.md`](../qualitaet/QUALITÄTSSICHERUNGSPLAN.md) und der zugehörigen manuellen Prüftabelle.

## 3. Verbindliches Eingangstor: fachliche Datenfreigabe

Vor Beginn der produktiven Portal- und KI-Anbindung sind folgende Punkte abzuschließen:

1. H-03 bis H-10 werden mit dem aktuellen Daten- und Anwendungsstand durchgeführt.
2. Abweichungen werden dokumentiert, fachlich bewertet und bei Bedarf korrigiert.
3. Nach Korrekturen werden die betroffenen automatisierten und browserseitigen Prüfungen wiederholt.
4. Der geprüfte Daten- und Anwendungsstand wird ausdrücklich als Ausgangsbasis für die Portal- und KI-Umsetzung freigegeben.
5. Der freigegebene Stand erhält eine eindeutige Versionsbezeichnung beziehungsweise einen Git-Tag.

Erst danach wird die technische Umsetzung auf einer stabilen fachlichen Grundlage fortgeführt. Neue Produktfunktionen dürfen die fachlich geprüften Berechnungen nicht verändern.

## 4. Zielbild

Der Analyseassistent soll Fragen zu den Güterverkehrsdaten verstehen, in geprüfte Datenabfragen übersetzen und die Ergebnisse verständlich einordnen. Die KI berechnet oder erfindet keine Mengenwerte. Zahlen werden ausschließlich aus kontrollierten Abfragen der freigegebenen Datenbasis übernommen.

Vereinfachter Ablauf:

```text
Frage im Dashboard
  → Portal prüft Anmeldung und Premiumberechtigung
  → Analyse-API erkennt den Fragetyp
  → geprüfte Datenfunktion liefert das Ergebnis
  → KI formuliert eine nachvollziehbare Einordnung
  → Antwort mit Zeitraum, Einheit, Quelle und Einschränkungen
```

Die Anwendung soll zunächst eine begrenzte, fachlich beherrschbare Auswahl von Fragen zuverlässig beantworten. Ein völlig freier Zugriff der KI auf Datenbank oder Dateisystem ist nicht vorgesehen.

## 5. Fachlicher MVP des Analyseassistenten

Für eine erste produktive Fassung werden etwa zehn bis fünfzehn Fragetypen definiert. Geeignete Startfälle sind:

1. wichtigste Verkehrsrelationen von und nach einer Region,
2. Vergleich zweier Regionen,
3. Entwicklung eines Verkehrsträgers zwischen zwei Zeitpunkten,
4. dominante Gütergruppen einer Region,
5. Modal Split einer Region oder Deutschlands,
6. Vergleich von Versand, Empfang und Saldo,
7. stärkste Zu- oder Abnahmen,
8. Vergleich von Ist-Daten und Verkehrsprognose,
9. Einordnung einer auffälligen Relation,
10. Erläuterung von Datenquelle, Einheit und methodischer Abgrenzung.

Für jeden Fragetyp wird vor der Programmierung festgelegt:

- zulässige Parameter und Filterkombinationen,
- verwendete Datenquelle und fachliche Grundgesamtheit,
- Kennzahl und Einheit,
- Berechnungs- und Sortierlogik,
- erwartetes Antwortformat,
- bekannte Einschränkungen und Nichtvergleichbarkeiten,
- Prüffragen mit fachlich erwarteten Ergebnissen.

Nach Abschluss der Datenfreigabe wird hierfür in einem separaten Arbeitschat ein fachlich geprüfter Testkatalog vorbereitet. Aus zuvor festgelegten Nutzenden-Perspektiven werden 100 bis 200 Kandidatfragen erzeugt, nach Fragetypen gebündelt und zu einer repräsentativen, fachlich prüfbaren Auswahl verdichtet. KI-gestützte Erzeugung darf Vielfalt und Formulierung der Kandidatfragen beschleunigen, ersetzt aber weder die fachliche Auswahl noch die Prüfung der erwarteten Ergebnisse. Für jede tatsächlich genutzte Testfrage sind zulässige Datenbasis, erwartete Kennzahl und Einheit, Quellenhinweis, Einschränkungen und erwartete Ergebnislogik festzulegen.

## 6. Kontrollierte Daten- und Abfrageschicht

Zwischen KI und Datenbasis wird eine fachlich definierte Abfrageschicht eingerichtet. Das Modell darf keine freien Datenbankabfragen erzeugen. Stattdessen wählt es aus geprüften Funktionen, beispielsweise:

- `get_top_relations(...)`
- `compare_regions(...)`
- `get_modal_split(...)`
- `get_goods_structure(...)`
- `get_time_change(...)`
- `get_forecast_comparison(...)`

Jede Funktion prüft die übergebenen Parameter und liefert ein strukturiertes Ergebnis. Dieses enthält mindestens:

- Ergebniswerte,
- Einheit und Skalierung,
- Raum- und Zeitbezug,
- Verkehrsrichtung und Verkehrsträger,
- Gütergruppe,
- Datenquelle,
- methodische Hinweise,
- Kennzeichnung fehlender oder nicht vergleichbarer Werte.

Die vorhandenen verarbeiteten Webdaten können als Ausgangspunkt dienen. Vor der technischen Festlegung ist zu entscheiden, ob sie serverseitig direkt gelesen oder in eine geeignete Datenbankstruktur überführt werden. Diese Entscheidung richtet sich nach Datenmenge, Antwortzeit, Aktualisierungsprozess und Wartbarkeit.

## 7. Analyse-API und KI-Anbindung auf AlwaysData

Auf AlwaysData wird eine serverseitige Schnittstelle eingerichtet, beispielsweise:

```text
POST /api/analyseassistent
```

Die Schnittstelle übernimmt folgende Aufgaben:

1. angemeldete Sitzung serverseitig validieren,
2. Premiumberechtigung prüfen,
3. Frage und Parameter auf zulässigen Umfang begrenzen,
4. passenden Fragetyp und geprüfte Datenfunktion auswählen,
5. Ergebnis aus der freigegebenen Datenbasis abrufen,
6. strukturierte Fakten an das KI-Modell übergeben,
7. Antwort auf Zahlenkonsistenz und Pflichtangaben prüfen,
8. Ergebnis an die Benutzeroberfläche zurückgeben.

Der Zugangsschlüssel zum KI-Anbieter liegt ausschließlich in einer geschützten Serverkonfiguration. Er wird weder im Browsercode noch im GitHub-Repository gespeichert. Der konkrete KI-Anbieter und das Modell werden erst nach einem Vergleich von Qualität, Datenschutz, Kosten und technischer Eignung festgelegt.

Für die erste Plattformstufe ist eine Einbindung in dieselbe AlwaysData-Anwendung wie Portal und `/api/...` sinnvoll. Dadurch bleiben Anmeldung, Berechtigungsprüfung und Schnittstelle unter derselben Herkunft und unnötige technische Komplexität wird vermieden.

## 8. Basis- und Premiumberechtigung

Es wird nur eine gemeinsame Version des Dashboards gepflegt. Die Pakete unterscheiden sich durch serverseitig verwaltete Funktionsrechte.

Vorgesehene Berechtigungen:

- `gueterstroeme`: Zugriff auf das Dashboard,
- `gueterstroeme_ai`: Zugriff auf den Analyseassistenten.

Falls die bestehende Portalstruktur bisher nur ganze Werkzeuge freischaltet, wird sie um ein eindeutig benanntes Merkmal für einzelne Premiumfunktionen ergänzt. Ob dies als Paket, Feature-Berechtigung oder gesonderter Eintrag umgesetzt wird, ist vor der Datenbankänderung anhand des aktuellen Portalschemas zu entscheiden.

### Verhalten im Basispaket

- Der Button **KI fragen** bleibt sichtbar.
- Beim Anklicken öffnet sich ein reduziertes Informationsfenster.
- Das Eingabefeld und die eigentliche Analysefunktion stehen nicht zur Verfügung.
- Der Hinweis erläutert den Nutzen und verweist auf das Premiumpaket.

Vorgesehener Text:

> **Analyseassistent – Premium-Funktion**  
> Stellen Sie individuelle Fragen zu Regionen, Verkehrsrelationen, Verkehrsträgern und Entwicklungen. Der Analyseassistent ist im Premiumpaket enthalten.

### Verhalten im Premiumpaket

- Das vollständige Eingabefenster wird geöffnet.
- Fragen werden an die geschützte Analyse-API übermittelt.
- Nutzungsgrenzen und Fehlermeldungen werden verständlich angezeigt.

Die Berechtigung darf nicht nur im Browser geprüft werden. Jeder Aufruf der Analyse-API muss die serverseitig validierte Identität und das zugehörige Funktionsrecht erneut prüfen. Ein nicht berechtigter Aufruf wird unabhängig von der sichtbaren Oberfläche abgewiesen.

## 9. Portal- und Testsystemintegration

Die Integration erfolgt zuerst ausschließlich im getrennten Testportal. Der vorgesehene Ablauf ist:

1. freigegebenen Güterströme-Stand als Portalwerkzeug paketieren,
2. Werkzeug im Testportal registrieren und mit künstlichen Testkonten absichern,
3. Basis- und Premiumkonto mit unterschiedlichen Rechten anlegen,
4. Dashboardzugriff, Premiumhinweis und Analyse-API getrennt prüfen,
5. Gesundheitsprüfung, Berechtigungsprüfung und Browser-QA dokumentieren,
6. Rückfall auf den vorherigen Teststand erproben,
7. erst nach fachlicher und technischer Abnahme eine Produktivfreigabe vorbereiten.

Test- und Produktivsystem bleiben vollständig getrennt. Testaufträge dürfen nicht auf die Produktivdatenbank oder produktive Geheimnisse zugreifen.

## 10. Qualitätssicherung des Analyseassistenten

Für den Assistenten wird ein eigener Abnahmekatalog aufgebaut. Er umfasst mindestens:

- fachlich erwartete Antworten für alle freigegebenen Fragetypen,
- korrekte Zahlen, Einheiten, Zeit- und Raumbezüge,
- Übereinstimmung mit den sichtbaren Dashboardwerten,
- transparente Hinweise bei fehlenden oder nicht vergleichbaren Daten,
- Ablehnung nicht unterstützter Fragen ohne erfundene Antworten,
- Schutz vor manipulierten Eingaben und unzulässigen Datenzugriffen,
- serverseitige Ablehnung von Basiskonten,
- verständliche Fehlerzustände bei nicht erreichbarer Daten- oder KI-Schnittstelle,
- Prüfung von Antwortzeit und laufenden Kosten,
- Browserprüfung auf Desktop und Mobilgeräten.

Eine Antwort gilt nur dann als bestanden, wenn Datenwert und fachliche Einordnung korrekt sind. Sprachlich überzeugende, aber fachlich falsche Antworten dürfen nicht freigegeben werden.
Der Testkatalog aus Abschnitt 5 ist hierfür die fachliche Grundlage; seine repräsentative Auswahl ist vor einem Modellvergleich auf Vollständigkeit der erwarteten Ergebnisse zu prüfen.

## 11. Datenschutz, Sicherheit und Betrieb

Vor der produktiven Freigabe sind mindestens folgende Regeln umzusetzen:

- keine API-Schlüssel, Passwörter oder Tokens im Browser oder Repository,
- serverseitige Validierung der Hanko-Sitzung,
- serverseitige Prüfung der Portal- und Premiumberechtigung,
- Begrenzung von Fragenlänge, Aufrufhäufigkeit und Antwortumfang,
- protokollierte technische Fehler ohne unnötige personenbezogene Inhalte,
- definierte Aufbewahrungs- und Löschregeln für eventuell gespeicherte Fragen,
- Aktualisierung von Datenschutz- und Nutzungshinweisen, falls Fragen, Nutzungsereignisse oder KI-Anfragen gespeichert werden,
- Kostenobergrenzen und Warnschwellen für die KI-Nutzung,
- kontrollierter Ausfallmodus, in dem das Dashboard ohne KI weiter nutzbar bleibt.

Standardmäßig sollten Fragen nicht dauerhaft gespeichert werden. Falls eine Gesprächshistorie oder gespeicherte Analysen später gewünscht sind, ist dies als eigener Funktions- und Datenschutzbaustein zu planen.

## 12. Umsetzungsetappen und Freigabepunkte

### Etappe 0 – Datenfreigabe

**Ergebnis:** H-03 bis H-10 abgeschlossen, Abweichungen geklärt und Ausgangsstand versioniert.  
**Freigabepunkt:** ausdrückliche fachliche Freigabe durch den Projektverantwortlichen.

### Etappe 1 – Fachliches Detailkonzept

**Ergebnis:** zehn bis fünfzehn Fragetypen mit Datenquelle, Parametern, Antwortformat und Prüferwartung sowie ein aus 100 bis 200 Kandidatfragen verdichteter, fachlich geprüfter Testkatalog.
**Freigabepunkt:** fachliche Bestätigung des Fragen- und Antwortkatalogs einschließlich zulässiger Datenbasis und erwarteter Ergebnislogik je Testfrage.

Erst nach diesem Freigabepunkt wird ein lokaler, nicht produktiver Pilot mit einem zu vergleichenden Modellkandidaten und einem freigegebenen Datenumfang vorbereitet. Anbieter, Modell und konkrete technische Ausgestaltung sind damit noch nicht festgelegt.

### Etappe 2 – Datenfunktionen und Analyse-API

**Ergebnis:** kontrollierte Datenfunktionen, API-Grundgerüst und automatisierte Tests ohne produktive Nutzer- oder KI-Daten.  
**Freigabepunkt:** Zahlenvergleich gegen Dashboard und Rohdaten bestanden.

### Etappe 3 – KI-Orchestrierung

**Ergebnis:** Zuordnung freier Fragen zu geprüften Funktionen und nachvollziehbare Antworterzeugung.  
**Freigabepunkt:** definierter Abnahmekatalog ohne erfundene Zahlen bestanden.

### Etappe 4 – Premiumberechtigung und Portal

**Ergebnis:** Basis- und Premiumverhalten im Testportal, serverseitige Rechteprüfung und verständliche Zustände.  
**Freigabepunkt:** Tests mit anonymem, Basis-, Premium- und Administratorkonto bestanden.

### Etappe 5 – Pilot und Produktivfreigabe

**Ergebnis:** begrenzter Pilotbetrieb mit Kosten-, Fehler- und Qualitätsbeobachtung.  
**Freigabepunkt:** dokumentierte fachliche, technische und datenschutzbezogene Abnahme sowie geprüfter Rückfallweg.

## 13. Noch zu treffende Entscheidungen

Vor beziehungsweise während der Umsetzung sind folgende Punkte ausdrücklich zu entscheiden:

1. Welche zehn bis fünfzehn Fragetypen bilden den ersten Produktumfang?
2. Welche Datenbasis und welches serverseitige Speicherformat werden verwendet?
3. Welcher KI-Anbieter und welches Modell erfüllen Qualitäts-, Datenschutz- und Kostenanforderungen?
4. Welche Nutzung ist je Premiumpaket enthalten und welche Grenzen gelten?
5. Werden Fragen oder Gesprächsverläufe gespeichert?
6. Wie wird ein Wechsel vom Basis- zum Premiumpaket organisatorisch ausgelöst?
7. Welche Quellen- und Methodikhinweise müssen in jeder Antwort erscheinen?
8. Welche Kriterien müssen vor einem Pilot- beziehungsweise Produktivstart bestanden sein?

## 14. Unmittelbar nächster Arbeitsschritt

Nach der vorgesehenen letzten Datenprüfung wird zunächst Etappe 0 abgeschlossen. Anschließend wird in einem separaten Arbeitschat für Etappe 1 ein fachlich geprüfter Testkatalog erarbeitet: 100 bis 200 Kandidatfragen aus vorab festgelegten Nutzenden-Perspektiven werden nach Fragetypen gebündelt und zu einer repräsentativen, fachlich prüfbaren Auswahl verdichtet. Für jede tatsächlich genutzte Testfrage werden zulässige Datenbasis, erwartete Kennzahl und Einheit, Quellenhinweis, Einschränkungen und erwartete Ergebnislogik festgelegt.

KI kann die Vielfalt und Formulierung der Kandidatfragen unterstützen, darf aber weder die fachliche Auswahl noch die Prüfung der erwarteten Ergebnisse ersetzen. Erst mit diesem Katalog wird der nächste lokale, nicht produktive Pilot mit einem zu vergleichenden Modellkandidaten und freigegebenem Datenumfang vorbereitet. Die verbindliche Zielarchitektur bleibt dabei die kontrollierte serverseitige Datenfunktion mit Analyse-API; freier Zugriff auf Datenbank, Dateisystem oder Modell ist nicht vorgesehen.



## 15. Offener Ausbau: gemeinsamer Analyseunterbau und flexible Ergebnisdarstellung

**Ergänzung vom 05.09.2026; Datenfunktionen und KI-Anbindung weiterhin offen.** Die sechs beispielhaften Fragen im Interface dienen als Zielbild und spätere Abnahmefälle. Der Prototyp erhält dadurch noch keine Modell- oder Datenverbindung.

Dashboard und Assistent sollen auf denselben geprüften Kennzahlen aufbauen. Standardkennwerte, Karten, Filter, Datenstände und der regionale Steckbrief bleiben direkt zugänglich. Individuelle Regionsvergleiche, Kombinationen mehrerer Auswertungen und zielgruppengerechte Zusammenfassungen werden vorrangig über den Assistenten angeboten. Häufig verwendete Auswertungen können später als eigene Bedienfunktion ergänzt werden.

Ergänzend zu den Abschnitten 5 und 6 bleiben folgende Arbeiten offen:

- [ ] Die vollständigen vorhandenen Analysebestände serverseitig erschließen. Die auf Top-Relationen gekürzten Webdateien sind keine ausreichende Grundlage für beliebige Quelle-Ziel-Abfragen. `fact_od_flows.parquet` ist als vorhandener Ausgangsbestand zu prüfen; regionale Kennwerte und Prognosewerte behalten ihre jeweiligen Quellenabgrenzungen.
- [ ] Geprüfte Funktionen für Regionsvergleich, konkrete Verbindung, Güterstruktur, Zeitvergleich und Prognosevergleich einschließlich eindeutiger Parameter, Einheiten, Gebietsstände und Bezugsjahre definieren. Ein gemeinsames vollständiges Bezugsjahr wird ausdrücklich genannt; fehlende Jahre werden nicht still ersetzt.
- [ ] Verfügbarkeit und Datenqualität je Kombination aus Raum, Jahr, Richtung, Verkehrsträger und Güterart mitliefern. Null, fehlend, nicht veröffentlicht und eingeschränkt belastbar müssen unterschieden werden; entsprechende Quellkennzeichnungen sind bei der Verarbeitung zu erhalten.
- [ ] Wiederverwendbare Antwortbausteine für Vergleichstabellen, Diagramme, kurze Texte, Quellen und Export erstellen. Die KI erhält geprüfte Ergebnisse und erläutert sie; die Zahlenberechnung liegt in den kontrollierten Datenfunktionen.
- [ ] Den vollständigen Katalog mit 45 Testfällen als Grundlage der späteren Funktions- und Modellabnahme verwenden. Die sechs sichtbaren Beispielfragen sind darin enthalten; der Abnahmeumfang wird nicht auf diese sechs beschränkt.
- [ ] Zusätzliche Auswertungen ausschließlich aus vorhandenen Dashboard- und Rohdaten nach bestätigtem Nutzen vorbereiten. Neue Kosten-, Umwelt-, Kapazitäts- und betriebliche Transportkettenquellen sind gemäß späterer Umfangsentscheidung nicht vorgesehen.
- [ ] Serverseitige Rechte, Mengen- und Abrufbegrenzungen für Analyse und Export im späteren Portal vorsehen. Eine Beschränkung der Exportoberfläche allein schützt statisch ausgelieferte Daten nicht vor systematischem Abruf.

**Bestätigte Datengrenze:** Die vorhandenen Straßen-Verflechtungsdaten enthalten Gesamtmengen je Quelle-Ziel-Paar, aber keine Gütergliederung dieser einzelnen Verbindung. Regionale Güterstrukturen dürfen nicht als belegte Güterstruktur einer bestimmten Straßenrelation ausgegeben werden. Für Schiene und Binnenschiff enthält der vorhandene Relationsbestand Güterhauptgruppen. Eine darüber hinausgehende Modellierung benötigt eine gesonderte fachliche Entscheidung und sichtbare Kennzeichnung.

## 16. Vorbereitetes Server-Regelpaket (09.09.2026)

Auf Nutzerauftrag liegt unter [`config/analyseassistent/`](../../config/analyseassistent/README.md) ein lokales Regelpaket vor: Modellprompt, 26 maschinenlesbar dokumentierte Fachregeln, Funktionsverträge für alle 15 Fragetypen und eine Beschreibung der Antwortprüfung und Laufzeitmessung. Die vorhandenen 45 Testfälle sind vollständig zugeordnet. Grundlage sind das Etappe-1-Konzept und die Erkenntnisse des lokalen Terra-Probelaufs.

**Status:** Dateien angelegt und strukturell geprüft; Datenfunktionen, Validator, Requesty-Adapter und Servereinbindung noch nicht implementiert. Keine Bereitstellung im Test- oder Produktivportal. Das Speichern einer Markdown- oder JSON-Datei führt ihre Regeln nicht aus. Der spätere Server muss Prompt und Konfiguration ausdrücklich laden und die beschriebenen Prüfungen umsetzen.

Der Promptinhalt soll jedem Modellaufruf als Anweisungstext zugeordnet werden. Testkatalog und Referenzantworten bleiben interne Prüfunterlagen. In der ersten vorgesehenen Antwortform wählt das Modell aus serverseitig belegten Aussagebausteinen; Zahlen, Namen, Quellen und Pflichtangaben setzt der Server ein. Eine zweite KI zur Bewertung und automatische Reparaturschleifen sind nicht vorgesehen.

Antwortzeiten werden zunächst mit Requesty gemessen, einschließlich langsamer Anfragen und paralleler Nutzung. Die zunächst vorgeschlagenen fünf und zehn Sekunden wurden auf Nutzerrückmeldung nicht als feste Ziel- oder Abbruchgrenzen übernommen. Zielzeit, Wartehinweis und technische Höchstfrist bleiben bis zur Messung getrennt festzulegen. Bei bereits geprüftem Datenergebnis können Tabelle und feste Kurzfassung vor der optionalen Modellantwort erscheinen; eine Laufzeitüberschreitung darf keine ungeprüften Zahlen freigeben.

Die Beschränkung auf vorhandene Daten und der vollständige 45-Fälle-Umfang gelten für die weitere Vorbereitung. Frühere offene Vorschläge zur externen Datenbeschaffung sind damit nicht mehr Teil dieses Auftrags. Der aktuelle Prüf- und Freigabestand wird weiterhin im Qualitätssicherungsplan dokumentiert; dieses Paket ist keine Produktfreigabe.


### Fortsetzung: Aufbereitungsplan für den vollständigen Testkatalog (09.09.2026)

Der [Aufbereitungsplan](ANALYSEASSISTENT_AUFBEREITUNGSPLAN.md) und seine [strukturierte Fassung](ANALYSEASSISTENT_AUFBEREITUNGSPLAN.json) ordnen alle 45 Testfälle vorhandenen Quellen, Aufbereitungspaketen und Kontrollrechnungen zu. Die Wiederaufnahme hat die gespeicherten Terra-Artefakte ohne Prüfsummenabweichung vorgefunden. Offen war die konkrete Aufbereitungsplanung; sie liegt damit vor. Die Ursache eines wahrgenommenen App-Abbruchs ist dadurch nicht bestimmt.

Als erster Umsetzungsblock ist B01 mit vollständigen OD, Quellenkennzeichen und getrennten Fehlwertzuständen vorgeschlagen; die nötige Jahres-/Quellenprüfung aus B02 gehört dazu. Danach folgen vorhandene Güter-/Straßendetails und vollständige veröffentlichte Knotenrelationen sowie Monatsdaten nach Bedarf. Die Reihenfolge reduziert den Katalog nicht auf die sechs sichtbaren Fragen. Datenaufbereitung, Serverfunktionen und externe Modellaufrufe wurden bei dieser Fortsetzung nicht ausgeführt.


## 17. B01 – Umsetzung und zentraler Arbeitsstand (09.09.2026)

Historische erste Umsetzung; die aktuelle Nachprüfung und die jetzt gültigen Kennungen stehen in Abschnitt 23.

**Ergebnis: B01 lokal umgesetzt, vollständig aufgebaut und geprüft.** Der aktive Datenstand ist `19ffa80c84ef939f75ed`. Alle 71 automatisierten Prüfungen sind bestanden. Dies ist die Freigabe des lokalen B01-Bestands, keine Abnahme aller 45 Assistentenfunktionen und keine Serverbereitstellung.

### Erledigte Schritte und Dateien

Alle Pfade beziehen sich auf den Projektstamm; diese Übersicht ist der zentrale Einstieg für die Fortsetzung.

| Schritt | Status | Datei / Ergebnis |
|---|---|---|
| Vorhandene Quellen und Mengenlogik abgleichen | abgeschlossen | 26 Rohdateien: VE7, SGV 2016–2025, IWW 2011–2025; Quellenliste samt Prüfsummen im Manifest |
| Vollständigen separaten Bestand aufbauen | abgeschlossen | [`scripts/pipelines/build_b01_analysis.py`](../../scripts/pipelines/build_b01_analysis.py) |
| Fehlwertzustände und exakte Relationsabfrage festlegen | abgeschlossen | [`scripts/analysis/b01.py`](../../scripts/analysis/b01.py) |
| Lokalen Abfrageaufruf bereitstellen und ausführen | abgeschlossen | [`scripts/analysis/query_b01.py`](../../scripts/analysis/query_b01.py) |
| Rohquellen, alle vergleichbaren Mengen und Grenzfälle prüfen | 71/71 bestanden | [`scripts/validation/validate_b01_analysis.py`](../../scripts/validation/validate_b01_analysis.py) |
| Geprüften Stand lokal aktivieren | abgeschlossen | [`data/analysis/b01/current.json`](../../data/analysis/b01/current.json) verweist auf den geprüften Stand |
| Wiederholung und Nachweise dokumentieren | abgeschlossen | [Betriebsanleitung, Abschnitt 12](../betrieb/ANLEITUNG_DATENAKTUALISIERUNG.md), [Skriptübersicht](../../scripts/README.md), [Qualitätssicherungsplan](../qualitaet/QUALITÄTSSICHERUNGSPLAN.md), Aufbereitungsplan MD/JSON und diese Roadmap |
| Große reproduzierbare Bestände aus Git ausschließen | abgeschlossen | [`.gitignore`](../../.gitignore); Daten bleiben lokal erhalten |

### Erzeugter Bestand

Basisordner: `data/analysis/b01/releases/19ffa80c84ef939f75ed/`.

| Datei | Inhalt |
|---|---|
| `source_values.parquet` | 7.846.377 einzelne Kennzahlbelege aus 2.615.459 Rohzeilen; Originalwert und Quellenzeichen, Quellzeile, Raum, Jahr, Monat soweit vorhanden, Richtung und NST-Schlüssel |
| `annual_od.parquet` | 1.495.344 jährliche Relations-/Kennzahlzeilen mit getrennten Mengen, bekannten Teilsummen, Fehlwert- und Qualitätszuständen; keine Top-Kürzung |
| `manifest.json` | Originalquellen, Zeichensätze, SHA-256-Prüfsummen, Buildcode-Prüfsummen, Datenstände, Jahresabdeckung und Zeilenzahlen |
| `validation.json` | Tatsächliche Ergebnisse aller 71 Prüfungen |

Jahre mit vorhandenen Quellzeilen: Straße 2010–2024, Schiene 2016–2025, Binnenschiff 2011–2025. Dies bestätigt noch keine vollständigen Monatsreihen oder Vergleichbarkeit aller Jahre; das bleibt B02. 3.397 Rohzeilen außerhalb der bisherigen räumlichen Auswahl bleiben nachvollziehbar erhalten. Die vollständigen Rohdateien bleiben die Originalbelege; zusätzliche, hier nicht ausgewertete Spalten werden in späteren Paketen erschlossen.

### Fachliche Prüfergebnisse

- **Keine Mengenabweichung** für sämtliche vergleichbaren Quelle-Ziel-/Jahr-/Verkehrsträger-/Gütergruppen-Schlüssel bei Tonnen und Tonnenkilometern gegenüber `fact_od_flows.parquet`. Verglichen wurden alle Schlüssel, nicht nur Beispiele oder Top-Listen. Numerische Toleranz: maximal aus 0,00001 und dem 10⁻¹²-fachen Vergleichswert für Gleitkommaarithmetik.
- Alle **145.707 mit Klammern markierten VE7-Tonnenzeilen** sind als eingeschränkt belastbar erhalten. Beispiel Köln → Hamburg, Straße 2024: **67.757 t, eingeschränkte Qualität**. Die bestehende Dashboardanzeige wurde dadurch noch nicht ergänzt.
- Referenzen T04, T05, T19 und T20 nachgerechnet: unter anderem Schiene Köln → Hamburg 199.851 t; Binnenschiff Duisburg → Magdeburg 1.947 t und Gegenrichtung 1.189 t; Hamburger Straßenpartner und vollständiger Nenner bestätigt.
- Fehlende Zeilen werden nicht zu Null. Veröffentlichte numerische Null, gerundete Null, bestätigte Quellnull, fehlender Wert, unterdrückter Wert und widersprüchliche Quellangabe bleiben getrennt. 100 plus unbekannt ergibt eine bekannte Teilsumme 100, aber keinen vollständigen Gesamtwert.
- Führende Nullen und alphanumerische NST-Schlüssel wie `01A` bleiben erhalten. Fahrten, Ladeeinheiten und Ladungsträger sind verschiedene Kennzahlen.
- Rohquellenprüfsummen stimmen; der bestehende Dashboard-OD-Bestand blieb unverändert. Keine Änderungen an Browserpaketen, keine externe Modellabfrage und keine Serverübertragung.

Der erste Prüfstand `5796b803720672575554` wurde wegen eines synthetischen Quellenkonflikts nicht aktiviert. Die Qualitätsklassifikation wurde korrigiert und der komplette Bestand neu aufgebaut. Dieser verworfene Stand bleibt mit fehlgeschlagenem Prüfbericht nachvollziehbar, ist aber nicht der über `current.json` verwendete Bestand.

### Wiederholen und nutzen

Aufbau: `python scripts/pipelines/build_b01_analysis.py`. Danach den ausgegebenen Datenstand mit `python scripts/validation/validate_b01_analysis.py --dataset <Pfad> --activate` prüfen und aktivieren. Ein vorhandener identischer Stand wird nicht überschrieben. Temporäre Arbeitsdaten liegen ausschließlich unter `C:\tmp`.

Beispiel der erfolgreich ausgeführten lokalen Abfrage:

```powershell
python scripts/analysis/query_b01.py --year 2024 --origin DEA23 --destination DE600 --mode road
```

Die Abfrage liefert Wert, Einheit, Richtung, Jahr, Datenstand, Quellen-ID und Qualitätszustand. Quellen-IDs werden über das Manifest zur Originaldatei aufgelöst. `available` bedeutet vorhandene veröffentlichte Zeilen; unbekannte Komponenten führen zu `partial`. Ortskennungen müssen derzeit exakt angegeben werden; Namensauflösung und Prüfung gleichrangiger Räume sind keine fertige Portalbedienung.

### Was als Nächstes offen bleibt

| Paket / Schritt | Status und nächster Gegenstand |
|---|---|
| B02 – zeitliche Abdeckung | Monatsbestand und Abdeckungsprüfung lokal umgesetzt, 112 Prüfungen bestanden; Gebiets-/Revisionsvergleichbarkeit nicht pauschal bestätigt. Details in Abschnitt 19 |
| B03 – vorhandene Details | Inzwischen lokal geprüft: feinere Schienengüter sowie VD2-/VD3c-Details; 193/193 Prüfungen, Dateien und Grenzen in Abschnitt 20 |
| B04/B05 – Raum und nationale Abgrenzung | Lokal geprüft, siehe Abschnitt 21; T22-Nenner wegen sieben unbekannter Straßen-Inlandswerte begrenzt |
| B06 – Knotenrelationen | Lokal geprüft, siehe Abschnitt 21; vollständige veröffentlichte Partner, TEU-Anwendbarkeit und Gewichtsgrenzen erhalten |
| B07 – Maut | Bestätigten Raum, Richtung und Monatspaar vorbereiten; kein bundesweiter Komplettabruf |
| Kontrollierte Serverfunktionen und Requesty | Noch nicht implementiert; Regelpaket bleibt deaktiviert. B01 ist eine lokale Datengrundlage, kein öffentlich erreichbarer Assistent |

Alle **45 Testfälle** bleiben im [Aufbereitungsplan](ANALYSEASSISTENT_AUFBEREITUNGSPLAN.md) zugeordnet. B01 allein beantwortet nicht alle Fälle. Neue Umwelt-, Kosten-, Kapazitäts- oder betriebliche Transportkettenquellen bleiben ausgeschlossen.


## 18. Nächste Schritte und erneuter KI-Test

**Aktualisierte Vereinbarung auf Nutzerwunsch:** Zuerst die übrigen Datenpakete B02–B07 vorbereiten, anschließend den Modell-Nachtest mit Systemprompt und den überarbeiteten Basisdaten bündeln. Einzelne KI-Nachtests nach B01 oder nach jedem weiteren Paket entfallen, um Aufwand und Tokenverbrauch zu begrenzen. Ziel ist nachzuweisen, ob die beobachteten Fehler seltener auftreten und die Antworten Zahlen, Datenlücken und Einschränkungen korrekt wiedergeben. Der erneute Modelllauf ist geplant, noch nicht ausgeführt. Die 71 bestandenen B01-Prüfungen sind Datenprüfungen und ersetzen ihn nicht.

### Eine Roadmap als zentraler Einstieg

Für den Arbeitsüberblick genügt diese Datei: Abschnitt 17 zeigt den erledigten B01-Stand, Abschnitt 18 die nächsten Schritte. Nach jedem abgeschlossenen Schritt hier Status, Ergebnis und Verweis auf die zugehörigen Dateien ergänzen. Keine zusätzliche parallele Fortschrittsliste anlegen. Der Qualitätssicherungsplan bleibt der verbindliche Nachweis tatsächlich bestandener Prüfungen; die übrigen Dokumente sind Detailunterlagen und müssen für den Überblick nicht laufend gelesen werden.

### Reihenfolge der nächsten Arbeiten

| Reihenfolge | Arbeit | Konkretes Ergebnis | Status |
|---|---|---|---|
| 1 | B02 – Zeitliche Vergleichbarkeit | Monatsdaten und Quellenabdeckung aufgebaut; Gebiets-/Revisionsgrenzen dokumentiert, keine ungeprüften Änderungsraten | lokal geprüft – Details Abschnitt 19 |
| 2 | B03 – Fachliche Details | Feinere Schienengüter sowie VD2-/VD3c-Details auf Originalraumebene aufbereitet | lokal geprüft – 193/193, Details Abschnitt 20 |
| 3 | B04/B05 – Räumliche und nationale Auswertungen | Regionsverbünde und nationale Verkehrsbeziehungen mit korrekter Zählung; T22-Quellenlücke dokumentiert | lokal geprüft – Abschnitt 21 |
| 4 | B06 – Knotenrelationen | Vollständige veröffentlichte Hafen-/Flughafenpartner, passende Nenner und Anwendbarkeits-/Fehlwertzustände | lokal geprüft mit Quellenlimits – Abschnitt 21 |
| 5 | B07 – Maut | Benötigte vorhandene Daten nach bestätigtem Raum, Richtung und Monatspaar vorbereiten | offen – konkrete Auswahl erforderlich |
| 6 | Gebündelten Modell-Nachtest vorbereiten und durchführen | Gemeinsamer Prompt-/Datenstand, geprüfte Sollantworten, unveränderte Modellantworten und ein zusammenfassender Vorher-/Nachher-Bericht | offen – nach den Datenpaketen |
| 7 | Ergebnisse bewerten und weitere Freigabe vorbereiten | Verbleibende Fehler und Einschränkungen festhalten; gezielte Korrekturen vor kontrollierter Server-/Portalintegration | offen |

**Datenprüfung und Modelltest bleiben getrennt:** Jedes Paket erhält seine erforderlichen fachlichen Kontrollrechnungen ohne Modellaufruf. Die KI-Testfragen werden anschließend gemeinsam durchlaufen. Falls ein Paket mangels vorhandener Daten oder notwendiger Auswahl nicht fertiggestellt werden kann, die konkrete Lücke und betroffenen Fälle hier dokumentieren; vor dem gebündelten Lauf muss ihr Umgang geklärt sein. Keine stillschweigende Auslassung und keine externe Datenbeschaffung über den vereinbarten Umfang hinaus.

### Umfang und Bedingungen des erneuten Tests

- **Ein gebündelter Durchlauf über alle 45 festgelegten Testfälle**, sobald die Datenpakete vorbereitet beziehungsweise verbleibende Grenzen ausdrücklich geklärt sind. Die zuvor vorgeschlagene B01-Teilauswahl und paketweise Modellwiederholungen entfallen.
- Die fünf zuvor fachlich fehlerhaften und elf ergänzungsbedürftigen Fälle im gemeinsamen Ergebnisbericht besonders ausweisen. Pro Fall festhalten: behoben, weiterhin fehlerhaft, neu auffällig oder wegen konkret dokumentierter Voraussetzungen noch nicht prüfbar. Nicht prüfbar bedeutet nicht bestanden.
- Wo die fachlich richtige Antwort eine Rückfrage oder eine begründete Grenze ist, genau dieses Verhalten prüfen. Fehlende Rohdaten, noch nicht vorbereitete Auswertung und technischer Abruffehler bleiben getrennt.
- Keine routinemäßigen weiteren Komplettläufe oder zusätzlichen Modellvergleiche. Nach dem gebündelten Lauf notwendige Korrekturen begründen und eine erforderliche Wiederholungsprüfung auf die betroffenen Fälle begrenzen.
- Den vorhandenen [`SYSTEM_PROMPT.md`](../../config/analyseassistent/SYSTEM_PROMPT.md) ausdrücklich als Systemanweisung laden. Er sieht eine Phase zur Fragezuordnung und eine Phase zur Auswahl geprüfter Aussagen vor. Vor dem Test dafür einen begrenzten lokalen Ablauf mit erlaubten Funktionen, geprüften Ergebnissen, Aussagebausteinen und Prüfung des Ausgabeformats vorbereiten. Ein bloßer Dateiverweis lädt den Prompt nicht; B01 allein stellt diese Verarbeitung noch nicht bereit.
- Das getestete Modell erhält nur die vorgesehenen Eingaben und Datenbelege. **Keine Sollantworten, alten Bewertungen oder Ergebnisberichte als Modellkontext.** Die Referenzen dienen ausschließlich der anschließenden unabhängigen Prüfung.
- Ein Modell der vereinbarten Leistungsklasse verwenden. Ein Terra-Subagentenlauf ist als solcher zu kennzeichnen; ein Requesty-Lauf muss den tatsächlich verwendeten Anbieter, Modellbezeichner und Einstellungen dokumentieren. Subagenten-Ergebnisse belegen keine Requesty-Antwortzeiten. Keine Portalbereitstellung für diesen Test erforderlich.
- Pro Lauf Promptfassung, Datenstand, Modell, Eingaben und unveränderte Ausgaben festhalten. Zahlen, Einheit, Raum, Zeit, Richtung, Nenner, Qualitäts- und Fehlwerthinweise sowie notwendige Rückfragen prüfen. Bei Requesty zusätzlich Laufzeiten und verfügbare Verbrauchsdaten messen; keine ungeprüfte Fünf-/Zehnsekundengrenze einführen.
- Der frühere Terra-Lauf bleibt eine dokumentierte Ausgangsbeobachtung mit seinen bekannten Zugriffsgrenzen. Ein besseres Ergebnis nach gleichzeitiger Änderung von Prompt und Daten belegt die Verbesserung des Gesamtverfahrens, nicht den isolierten Effekt einer einzelnen Änderung. Bei verbleibenden Fehlern gezielt zwischen Daten, Berechnung, Prompt, Modellauswahl und Ausgabeprüfung unterscheiden.

### Wo die Unterlagen liegen

| Unterlage | Zweck |
|---|---|
| Diese Roadmap, Abschnitte 17–18 | Überblick, nächste Arbeit, Status und Ergebnisverweise |
| [`ANALYSEASSISTENT_AUFBEREITUNGSPLAN.md`](ANALYSEASSISTENT_AUFBEREITUNGSPLAN.md) und JSON-Fassung | Detailzuordnung aller 45 Fragen zu Quellen und Datenpaketen |
| [`config/analyseassistent/`](../../config/analyseassistent/README.md) | Systemprompt und fachliche Verträge für den Test und die spätere Anwendung |
| `data/analysis/b01/current.json` und der dort bezeichnete Datenstand | Geprüfte lokale Basisdaten einschließlich Quellenbelegen |
| `outputs/analyseassistent_terra_probelauf_20260909/` | Vorhandene Ausgangsantworten und Bewertungen; ausschließlich für den Vergleich, nicht als Modellkontext |
| [`QUALITÄTSSICHERUNGSPLAN.md`](../qualitaet/QUALITÄTSSICHERUNGSPLAN.md) | Verbindlicher Prüf- und Freigabenachweis |

Die Dateien des neuen Testlaufs werden erst bei dessen Durchführung angelegt und hier mit ihrem tatsächlichen Speicherort ergänzt. In diesem Schritt werden nur Vereinbarung und Reihenfolge dokumentiert; kein Modellaufruf, keine neue Datenaufbereitung und keine Serveränderung.


## 19. B02 – Monatsdaten, Quellenstände und Updateablauf

Historische erste Umsetzung; die aktuelle Nachprüfung und die jetzt gültigen Kennungen stehen in Abschnitt 23.

**Stand 09.09.2026:** B02 lokal aufgebaut und mit **112 bestandenen Datenprüfungen** aktiviert. Datenstand `027b7422159248cf7dd0` verwendet unverändert B01 `19ffa80c84ef939f75ed`. Die Quellenabdeckung und die Berechnungen sind geprüft; eine allgemeine Freigabe harmonisierter Zeitvergleiche ist damit nicht verbunden. Kein KI-Nachtest und keine Serverbereitstellung durchgeführt.

### Schritte und Dateien

| Schritt | Status | Datei / Ergebnis |
|---|---|---|
| Monatsfelder und Quellbeschreibungen prüfen | abgeschlossen | Original-CSV und lokale Datensatzbeschreibungen für SGV und IWW; Gebietsangaben und Widersprüche mitgeführt |
| Monatliche Relationen aufbauen | abgeschlossen | [`scripts/pipelines/build_b02_analysis.py`](../../scripts/pipelines/build_b02_analysis.py) |
| Monatsabdeckung, Jahreswerte und sichere Rechenregeln bereitstellen | abgeschlossen | [`scripts/analysis/b02.py`](../../scripts/analysis/b02.py) |
| Lokale Zeitreihenabfrage ausführen | abgeschlossen | [`scripts/analysis/query_b02.py`](../../scripts/analysis/query_b02.py); Magdeburg, Schienenversand 2016–2025 erfolgreich abgefragt |
| Gesamten Bestand gegen B01 und Originalquellen prüfen | 112/112 bestanden | [`scripts/validation/validate_b02_analysis.py`](../../scripts/validation/validate_b02_analysis.py) |
| Geprüften Stand aktivieren | lokal erfolgt | [`data/analysis/b02/current.json`](../../data/analysis/b02/current.json) |
| Update- und spätere Bereitstellungsreihenfolge dokumentieren | abgeschlossen | [Datenaufbereitungsanleitung, Abschnitt 13](../betrieb/ANLEITUNG_DATENAKTUALISIERUNG.md), Skriptübersicht und Qualitätssicherungsplan |

Bestand unter `data/analysis/b02/releases/027b7422159248cf7dd0/`:

| Datei | Inhalt |
|---|---|
| `monthly_od.parquet` | 4.561.071 Monats-/Relations-/Kennzahlzeilen für Schiene und Binnenschiff, einschließlich Güterhauptgruppe, Richtung und Fehlwert-/Qualitätszählern |
| `source_coverage.json` | 40 Quellen-Jahreskombinationen: beobachtete Monate, Quellpfad und Prüfsumme, Zeichensatz, dokumentierte Gebietsangaben und offene Revisionsstände |
| `manifest.json` | Zugehöriger B01-Stand, Ausgabe-, Code- und Quellbeschreibungsprüfsummen |
| `validation.json` | Vollständige Ergebnisse der 112 Prüfungen |

### Befunde und fachliche Grenzen

- Alle 25 SGV-/IWW-Jahresdateien enthalten die Monate 1–12. Für die 15 VE7-Jahre liegen ausschließlich Jahreswerte vor; B02 erzeugt dafür keine geschätzten Monatswerte.
- Sämtliche monatlich aggregierten Mengen und Qualitätszähler stimmen mit B01 überein. Zusätzlich wurden Monatszeilenzahlen und Tonnen für jede SGV-/IWW-Quelle direkt aus den Original-CSV abgeglichen. Technische Aggregationstoleranz: maximal aus 0,00001 und 10⁻¹² des Vergleichswerts.
- Eine konkrete Auswahl kann dennoch lückenhaft sein: Schiene DEE06 → DEA23, C-Gruppe 4, 2016 enthält keine Zeilen für Januar und Mai. Die Abfrage kennzeichnet diese Monate als fehlend und liefert keinen vollständigen Jahreswert oder Spitzenanteil. Dies belegt keine Verkehrsfreiheit in diesen Monaten.
- Magdeburgs zehn Schienenversand-Jahreswerte 2016–2025 bleiben erhalten, jeweils mit zwölf belegten Monaten. Die Sprünge von 76.144 t (2018) auf 1.485.941 t (2019) und von 1.873.054 t (2024) auf 448.780 t (2025) sind Mengenbefunde, keine belegten Ursachen. Die Abfrage behauptet keine Erklärung oder harmonisierte Entwicklung.
- **Hohe fachliche Relevanz, belegter Metadatenwiderspruch:** Die acht Schienenjahrgänge 2016–2023 führen NUTS2024 im Spaltenkopf; die lokale SGV-Datensatzbeschreibung, Seite 1, nennt für diese Jahre NUTS2016 beziehungsweise NUTS2021. B02 erhält beides und setzt `header_documentation_conflict`. Die Ursache ist im geprüften Material nicht geklärt; vor entsprechenden harmonisierten Vergleichen ist die tatsächliche räumliche Abgrenzung zu bestätigen.
- Revisions-/Endgültigkeitsstände sind in den geprüften Unterlagen nicht hinreichend belegt und bleiben `not_documented`. Für IWW und VE7 wird kein ungeprüfter NUTS-Versionsjahrgang ergänzt. Deshalb bleibt die allgemeine Vergleichbarkeit `not_confirmed`; die lokale Abfrage zeigt Jahresscheiben und gibt keine freigegebene Änderungsrate aus. Das ist eine sichtbare Grenze, kein durch Null ersetzter Wert.
- Nullbasis, fehlende Basis, unvollständiger Monat, vollständige Nullreihe und kleine Ausgangswerte sind als Rechenfälle geprüft. Eine Veränderungsrate darf erst nach bestätigter fachlicher Vergleichbarkeit verwendet werden. Feinere NST-Auswertungen und weitere Details sind inzwischen durch B03 ergänzt (Abschnitt 20).

### Aktualisierung und spätere Servernutzung

**Fester Ablauf:** Rohdaten aktualisieren → passenden B01-Stand aufbauen und prüfen → B02 daraus aufbauen und prüfen → gemeinsam zugehörige Stände dokumentieren. Bei unverändertem B02-Eingangs-/Codestand wird der vorhandene Datenstand wiederverwendet. Befehle und Vorgehen bei neuen VE7-Dateinamen stehen in der [Datenaufbereitungsanleitung](../betrieb/ANLEITUNG_DATENAKTUALISIERUNG.md), Abschnitt 13. Temporäre Dateien bleiben unter `C:\tmp`.

Die zusätzlichen Analysebestände sollen später **serverintern auf AlwaysData** neben dem Tool betrieben werden, außerhalb öffentlicher Browserdateien. Kontrollierte Datenfunktionen lesen die benötigten Werte; das Modell erhält nur das passende geprüfte Ergebnis samt Quellen und Grenzen sowie den Systemprompt. Es erhält nicht sämtliche Dateien bei jeder Anfrage. Serverpfade, Berechtigungen und die technische Einbindung bleiben noch umzusetzen. Der spätere Updateablauf sieht vollständige Übertragung, Prüfung zusammengehöriger Versionen und gemeinsames Umschalten mit Rücknahmemöglichkeit vor; heute wurde nichts veröffentlicht.

**Fortgeschrieben durch Abschnitt 20:** B03 ist inzwischen lokal geprüft. B02-Vergleichsgrenzen bleiben für die davon betroffenen Testfragen sichtbar. Der Modell-Nachtest bleibt nach Vorbereitung der übrigen Pakete gebündelt; es erfolgt kein zusätzlicher KI-Lauf für B02.

## 20. B03 – Schienen-Feinpositionen und Straßendetails

Historische erste Umsetzung; die aktuelle Nachprüfung und die jetzt gültigen Kennungen stehen in Abschnitt 23.

**Stand 09.09.2026:** Datenstand `421123fa003af03e5929` nach **193/193 bestandenen Prüfungen** lokal aktiviert. Er gehört zu B01 `19ffa80c84ef939f75ed` und B02 `027b7422159248cf7dd0`. Vorhandene Dashboarddaten und Frontend wurden nicht geändert; kein Modellaufruf und keine Serverbereitstellung.

| Schritt | Ergebnis / Datei |
|---|---|
| Quellen und Klassifikation | Vier KBA-Referenzhandbücher gegen CSV-Felder geprüft; aktueller Crosswalk statt veralteter Labels |
| Aufbau | [`build_b03_analysis.py`](../../scripts/pipelines/build_b03_analysis.py): SGV aus B01, Quellen-/Vergleichsgrenzen aus B02, 36 VD2-/VD3c-Jahresdateien |
| Lokale Datenfunktionen | [`b03.py`](../../scripts/analysis/b03.py): Schienen-Feinpositionen/Monate sowie KBA-Klassen mit festen Raum-, Richtungs- und Populationsgrenzen |
| Lokale Abfrage | [`query_b03.py`](../../scripts/analysis/query_b03.py): Schienenrelation, Entfernungsklassen oder 20 NST-Abteilungen gezielt abfragen |
| Vollständige Datenprüfung | [`validate_b03_analysis.py`](../../scripts/validation/validate_b03_analysis.py): 193/193 bestanden |
| Aktivierung | [`data/analysis/b03/current.json`](../../data/analysis/b03/current.json), ausschließlich lokal |
| Wiederholung / spätere Bereitstellung | [Datenaktualisierungsanleitung, Abschnitt 14](../betrieb/ANLEITUNG_DATENAKTUALISIERUNG.md#14-b03-schienen-feinpositionen-und-kba-details-erneuern) |

Dateien unter `data/analysis/b03/releases/421123fa003af03e5929/`:

| Datei | Inhalt |
|---|---|
| `rail_monthly_details.parquet` | 3.495.186 monatliche Relations-/Feinpositions-/Kennzahlzeilen, 2016–2025; Richtung, Verkehrsbeziehung und Qualitätszähler |
| `road_details.parquet` | 214.452 Kennzahlbelege aus 36 Dateien, 2016–2024: VD2 und VD3c, jeweils Versand/Empfang, TON/TKM/FT sowie I/G getrennt; Originalwert und ZS-Zeichen erhalten |
| `classification.json` | 20 NST-Abteilungen, sieben C-Gruppen, VP-Zuordnung, beobachtete Schienen-Originalcodes und drei Entfernungsklassen |
| `source_coverage.json` | Unveränderte B02-Quellen-/Monatsabdeckung einschließlich Gebiets- und Revisionsgrenzen |
| `manifest.json`, `validation.json` | Quellen-/Code-/Dateiprüfsummen, Abhängigkeiten und vollständiger Prüfbericht |

**Bestätigte Kontrollen:** Alle Schienen-Feinpositionen ergeben exakt die B02-Monatsmengen und Qualitätszähler innerhalb der dokumentierten numerischen Toleranz (maximal aus 0,00001 und 10⁻¹² des Vergleichswerts). Alle zehn Schienenjahre wurden zusätzlich je Monat, Richtung, NST-Originalcode und drei Kennzahlen mit den Original-CSV verglichen. Sämtliche 214.452 KBA-Belege sind auf Originalfeld, Richtung, Raumcode, I/G, Einheit und ZS geprüft.

- **T18/T19/T21:** 031 gehört zu C1, NST14 und VP140 zu C6. Köln → Hamburg Schiene: 227.456 t (2023) und 199.851 t (2024), davon 2024 C1 231 t und C7 199.620 t. Fehlende C2–C6 bleiben ohne Nullnachweis; keine ungeprüfte Änderungsrate. Gegenrichtung gesondert geprüft.
- **T39:** Reale Monatslücke DEE06 → DEA23, C4, 2016 verhindert vollständigen Jahreswert und Spitzenanteil. Synthetische Rechnung 1.300 t und 200/1.300 als Spitzenanteil bestätigt.
- **T40:** Nürnberg 2024, Versand, Inlandsfahrten: 698.880,8 / 400.300,5 / 476.759,4 Fahrten in Nah-/Regional-/Fernbereich. Grenzen bis 50 km, 51–150 km, mehr als 150 km.
- **T41/T42:** DEA2 hat je Richtung, I/G und Kennzahl 20 veröffentlichte Positionen, darunter unterdrückte Werte; deshalb keine vollständige Gesamtsumme. Originalzeichen und bekannte Teilsummen bleiben sichtbar. Fehlend, gemeldete Null, gerundete Null, bestätigte Null und eingeschränkter Wert sind geprüft.

**Fortbestehende Grenzen:** VD2/VD3c beziehen sich auf deutsche Güterkraftfahrzeuge und Lastfahrten. I umfasst auch Fahrten mit einem deutschen Teilstück; G schließt Auslandsteile ein. Kein Straßen-OD-Güterdetail, keine künstliche NUTS-3-Aufteilung der 20 NST-Abteilungen, keine Leerfahrtenableitung. TON=t, TKM=tkm, FT=Fahrten ohne Skalierung; KM-Felder nicht erschlossen. T16 nutzt weiterhin vorhandene VE12/VE13-C-Gruppen. Feinpositionsnamen werden nicht erfunden. Gebiets-/Revisionsgrenzen von B02 bleiben wirksam; der gemeinsame Modelltest und die vollständige Fallabnahme stehen aus.

**Fortgeschrieben durch Abschnitt 21:** B04–B06 sind inzwischen lokal geprüft. B07 sowie die Klärung verbleibender Fallgrenzen stehen vor dem gebündelten KI-Nachtest aus.

## 21. B04–B06 – räumliche Auswertungen, nationale Verkehrsbeziehungen und Knoten

Bisherige Umsetzung und Nachbesserung; die erneuerte Abhängigkeitskette nach B01–B03-Zweitprüfung steht in Abschnitt 23.

**Stand 09.09.2026, nach Zweitprüfung verbessert: lokal nach 199/199 Hauptprüfungen sowie 10/10 zusätzlichen Kontrollen aktiviert.** Gemeinsamer Datenstand: `ac45c399570d4ef97445`, Verweis `data/analysis/b0406/current.json`. B01 `19ffa80c84ef939f75ed`, B02 `027b7422159248cf7dd0` und B03 `421123fa003af03e5929` bleiben die zusammengehörigen Abhängigkeiten. Freigabeumfang sind die lokalen Datenfunktionen mit den nachstehend genannten Grenzen; keine Freigabe sämtlicher Modellfälle oder Serverbereitstellung. Der vorherige Stand `c36ed9b0929ac02c25e2` bleibt erhalten.

Bestand unter `data/analysis/b0406/releases/ac45c399570d4ef97445/`: 3.984 Regional-/Jahresprofile, 9.600 Prognose-/Kennzahl-/Richtungszeilen, 350 nationale Verkehrsbeziehungswerte, 70.263 Flughafenrelations-Jahreszellen, 4.830 Flughafenrandsummen-Jahreszellen und 124.762 Seehafenpartner-/Kennzahlzeilen. Insgesamt rund 4,2 MiB einschließlich Metadaten und Prüfberichten. Die lokale Leipziger Top-5-Beispielabfrage des vorherigen Stands ergab rund 2,3 KB JSON mit Quellen-/Methodikhinweisen; dies ist keine Messung einer Server- oder Modellantwortzeit.

**Prüfnachweise:** `validation.json` und `partner_mapping_validation.json` im Release. Alle Input-/Outputprüfsummen und aktuellen Codefassungen bestätigt, Abhängigkeiten stimmen überein. Nationale Werte vollständig gegen Original-CSV kontrolliert; sämtliche Luft-Jahreszellen einschließlich Originalzeichen/Länder gegengeprüft; Seejahre 2011–2025 nach Quelle, Richtung, Kennzahl und fehlenden/nicht anwendbaren Zellen nachgerechnet. Zusätzlich sämtliche Seehafen-Partnerpaare 2024 direkt gegen CSV geprüft. Reale Verbünde für alle drei Verkehrsträger, D01-Vergleich Duisburg/Magdeburg, Richtungssaldo, 400er-VP-Ranking, Transitwert und internationale Leipziger Partner bestätigt. Temporäre Arbeitsdateien unter `C:\tmp` sind entfernt. Die frühere lokale Vorstufe `23cef5ddd65226c28dd7` wurde nicht aktiviert und bleibt als überholter Aufbau erhalten.

| Paket | Ergebnis | Dateien / lokale Funktionen |
|---|---|---|
| B04 | Ganze Regionsverbünde mit Innen-/Außen- und Berührungszählung; Vergleich gleichrangiger Einzelregionen, Richtungssaldo, Ranggleichstände und VP-Ranking über 400 deutsche NUTS-3-Gebiete | `scripts/analysis/b0406.py`: `query_union`, `compare_regions`, `direction_balance`, `change_ranking`, `forecast_ranking`; `regional_profiles.parquet`, `forecast.parquet`, `regions.json` |
| B05 | Nationale Verkehrsbeziehungen aus sämtlichen SGV-/IWW-Quellzeilen; Straße mit eigener Inlandsleistung und deren Qualitätszeichen | `national`; `national.parquet`, `road_national_evidence.parquet` |
| B06 | Vollständige veröffentlichte Flughafen-Jahreszellen und Seehafenpartner; Länderfilter vor Nenner/Rangbildung, getrennte Flughafenrandsummen sowie t/TEU | `node_partners`, `node_statistics`; `air_partners.parquet`, `air_statistics.parquet`, `sea_partners.parquet` |

Aufbau: [`build_b0406_analysis.py`](../../scripts/pipelines/build_b0406_analysis.py). Lokale Abfragen: [`query_b0406.py`](../../scripts/analysis/query_b0406.py). Hauptprüfung: [`validate_b0406_analysis.py`](../../scripts/validation/validate_b0406_analysis.py). Zusätzlicher unabhängiger Abgleich von Partnern, Ländern, Originalwerten und realen Verbünden: [`validate_b0406_partner_mapping.py`](../../scripts/validation/validate_b0406_partner_mapping.py). Wiederholung und Beispiele stehen in der Datenaktualisierungsanleitung, Abschnitt 15.

### Quellenbefunde und verbleibende Grenzen

- **T22, neue relevante Grenze:** Sieben `Inlands_tkm`-Felder der VE7-Quelle 2024 sind leer und mit `ZS_Inlands_tkm=.` unbekannt gekennzeichnet. Die bekannten Werte ergeben zwar den bisherigen Referenzbetrag 624.919.760.431 tkm, aber keinen vollständig belegten Drei-Modi-Nenner. B05 gibt daher keinen vollständigen nationalen tkm-Modal-Split aus. Die ursprüngliche Sollannahme im Aufbereitungsplan wurde berichtigt; vor dem gebündelten Modelltest ist diese Korrektur maßgeblich. Die alten Terra-Antworten und ihre Bewertungen bleiben historische Nachweise.
- **T36, Seehafen-Gewicht:** Die lokale Beschreibung vom 22.05.2025 nennt auf S. 5/10 `Tonnen` und Brutto-Brutto-Gewicht. Die CSV-Dateien enthalten `Guetergewicht`; zahlreiche Leerfelder betreffen unter anderem Leercontainer. Diese Felder bleiben unbekannt. Die Abfrage nennt bekannte Teilsummen und gibt ohne vollständige Komponenten keine freigegebene Gewichtssumme aus. Eine konkrete Hafenauswahl ist weiterhin erforderlich.
- **TEU-Anwendbarkeit:** Laut Beschreibung gelten TEU nur für Containertransporte. Leere TEU ohne Containergröße erhalten `not_applicable_count`; sie sind weder gemeldete Null noch unbekannte Container-TEU. Leere TEU mit Containergröße bleiben fehlend. `blank_count` erhält daneben die Zahl sämtlicher numerisch leerer Originalfelder.
- **B04/B02:** Frühere Gebiets-/Revisionsgrenzen bleiben wirksam. Einzelprofile nutzen den bestehenden D01-Bestand mit dessen Quellen-/Nullgrenzen. Regionsverbünde benutzen die vollständige B01-OD-Auswahl; deren große Einzelbelege werden nicht kopiert. Örtlicher Transit und Leerfahrten werden nicht aus Salden oder außen liegenden Endpunkten abgeleitet.
- **Luftfracht:** Der Nenner ist die Summe aller veröffentlichten positiven numerischen Verbindungen der Auswahl. Er bezeichnet nicht das gesamte Flughafenaufkommen. Fehlende Jahreszellen bleiben erhalten; flughafenbezogene Flugzahlen 2025 bleiben wegen des bekannten Quellenwiderspruchs gesperrt.

### Nachbesserung aus der Zweitprüfung

Die lesende Gemini-3.8-Flash-Prüfung des Vorgängers und die eigene Gegenkontrolle führten zu folgenden Korrekturen, anschließend durch lokale Tests bestätigt:

- Freigaben benötigen beide bestandenen Prüfungen desselben Manifests und die passende Prüferfassung. Wiederholte Aktivierung erhält alle vier Verweisfelder; die Umschaltung erfolgt atomar. Alle sechs Skriptfassungen werden ohne Ausnahme gegen das Manifest geprüft.
- B02 → B01, B03 → B01 und B03 → B02 werden jeweils anhand Datenstands-ID und Manifestprüfsumme abgeglichen. Falsche Kombinationen werden abgewiesen.
- Nicht anwendbare TEU-Partner werden nicht mehr als unbekannt ausgegeben. Hamburg, Versand 2024: 190 ausschließlich nicht anwendbare Partnerrelationen, keine unbekannten anwendbaren TEU-Relationen. Ein ausschließlich nicht anwendbarer Bestand erhält einen eigenen Status; gemeldete Null, fehlende Zeile und unbekannter Wert bleiben unterscheidbar.
- Vollständig fehlende nationale Jahrgänge werden als fehlend bezeichnet; Seehafenrandsummen enthalten Qualitätszähler und Quellen. Prognoserankings erlauben mit `descending: false` auch die stärksten Rückgänge.
- 49 neue Regressionstests decken reale t-/tkm-Vergleiche und Salden aller drei Verkehrsträger, reguläre Flughafenwerte, Seehafenpartner, vier lokale Aufrufvarianten, Grenzfälle und absichtlich ungültige beziehungsweise wiederholte Freigaben ab. Sie sind Bestandteil der 199 Hauptprüfungen. Kleine Testdateien werden unter `C:\tmp` automatisch entfernt.

Rohquellen, Vorstufen und Zeilenanzahlen sind gegenüber dem Vorgänger unverändert. Keine erneute Gemini-Prüfung der Korrektur behauptet: Der Nachweis für diesen Stand ist die vollständig bestandene lokale Quellen- und Funktionsprüfung. B07, Modell-/Serveranbindung und bestehende fachliche Quellengrenzen bleiben unberührt.

### Umfang der späteren Verwendung (unverändert)

Dies sind lokale Datenbestände und gezielte Datenfunktionen. Server-/Requesty-Adapter, Portalberechtigungen, Modellübersetzung und Antwortprüfung sind weiterhin gesonderte Implementierungsschritte. Der gebündelte 45-Fälle-Modelltest wird hier nicht vorweggenommen. B07 und die dafür erforderliche Gemeinde-/Monatsauswahl bleiben offen. Vor dem gemeinsamen Modelltest sind die Grenzen aus T22/T36 und B02 ausdrücklich in den Sollantworten zu berücksichtigen.

## 22. Terminal-Anwendungsfall: Kreisumfeld → Hamburg oder Nordseeküste

**Anforderung vom 09.09.2026, noch keine implementierte Dialogfunktion.** Ein Terminalbetreiber möchte erkennen, welche veröffentlichten Verkehrsmengen aus seinem Kreis und dessen Nachbarkreisen in einen nördlichen Zielraum gehen und welche Güter dabei transportiert werden. Dies unterstützt die Markterkundung; eine statistische Relation belegt weder verfügbares Kundenpotenzial noch tatsächlich gewinnbare Terminalmengen.

### Gewünschter Dialog

Bereits bestätigte Angaben aus der Kartenauswahl oder dem Gespräch werden übernommen. Rückfragen betreffen nur die noch offenen, ergebnisrelevanten Punkte; sinnvolle Gebietsvorschläge sollen die Auswahl erleichtern, nicht durch wiederholte vollständige Fragebögen ersetzen.

1. **Ausgangspunkt klären:** Welcher Kreis beziehungsweise welche kreisfreie Stadt ist gemeint? Einen Ort über geprüfte Gebietsmetadaten auflösen; gleichnamige Orte und Stadt/Landkreis unterscheiden.
2. **Umland vorschlagen:** Den ausgewählten Kreis und seine unmittelbar angrenzenden Kreise als prüfbaren Vorschlag mit Namen und Karte anbieten. „Angrenzend“ muss fachlich festgelegt sein, beispielsweise gemeinsame Grenzlinie statt bloßer Punktberührung. Ganze Kreise verwenden, keine anteiligen Verkehrsmengen aus geometrischen Überschneidungen schätzen. Der Nutzer bestätigt oder verändert die Liste.
3. **Zielraum konkretisieren:** „Hamburg“ als Stadtgebiet, Hafengebiet oder Metropolregion unterscheiden. Bei „Nordseeküste“ beispielsweise die Optionen „Küstenkreise“ und „Kreise mit ausgewählten Nordseehäfen“ anbieten. „Norddeutschland“ benötigt eine ausdrücklich vorgeschlagene Länder-/Kreisliste. Solche Begriffe werden nicht still durch Modellwissen in feste Kreislisten übersetzt. Die genaue Liste stammt aus einem geprüften, versionierten Gebietsregister und wird bestätigt.
4. **Zeit und Kennzahl klären:** Jahr, Verkehrsträger und Versandrichtung festlegen. „Wie viel Verkehr?“ zunächst etwa als Tonnen pro Jahr vorschlagen; Fahrten und Ladeeinheiten separat behandeln. Ein voreingestelltes gemeinsames Jahr benötigt belegte Verfügbarkeit und bleibt sichtbar.
5. **Gezielt auswerten:** Nur Verbindungen mit Ursprung in der bestätigten Quellliste UND Ziel in der bestätigten Zielliste auswählen. Gütergruppen und Zielgebiete aggregieren, Herkunfts- und Zielkreislisten mit ausgeben. Jede gerichtete Verbindung einmal zählen; bei überlappenden Listen Binnenfälle ausdrücklich kennzeichnen. Fehlende Zeilen und unbekannte Komponenten nicht in Nullen umdeuten.

Die KI kann Formulierungen zuordnen und Optionen erläutern. Ein noch zu schreibendes Programm muss die Ortsnamen auflösen, Nachbarschaften und Zielraumlisten liefern, Auswahlbestätigungen speichern und die zulässige Datenabfrage ausführen. Die Bestätigung stammt vom Nutzer, nicht aus einer Behauptung des Modells.

### Was die Daten bereits tragen

| Verkehrsträger | Vorhandener Relationsbestand | Aussage zu Gütern |
|---|---|---|
| Schiene | B01 jährlich, B02 monatlich, B03 mit feineren Güterpositionen; konkrete Quell-/Zielkennungen | Sieben C-Gruppen; feinere dreistellige NST-Originalcodes über B03, Benennungen nur soweit belegt |
| Binnenschiff | B01 jährlich und B02 monatlich | Sieben C-Gruppen auf konkreten Verbindungen; vorhandene Roh-Feincodes sind noch keine fertige B03-IWW-Detailabfrage |
| Straße | B01 mit jährlichen Verbindungsmengen, Verkehrsleistung, Fahrten und Qualitätszeichen | Keine Güteraufteilung genau dieser Verbindungen. Regionale Güterrandsummen aus D01 oder B03/VD3c lassen sich nicht auf Hamburg- oder Küstenrelationen übertragen |

Eine lesende Bereitschaftsprobe für Nürnberg → Hamburg, 2024, zeigt gespeicherte Schienenrelationen in C1/C6/C7 und eine Straßenrelation mit ALL. Sie belegt die grundsätzliche Datenstruktur, nicht die Vollständigkeit des realen Verkehrs. Der noch nicht vom Nutzer bestimmte Ausgangskreis wurde dadurch nicht festgelegt.

### Was noch entwickelt werden muss

- Versioniertes Register für Namen, Nachbarschaften und bestätigbare Zielraumvarianten. Kreisgeometrien und Gebietsnamen liegen lokal vor; eine geprüfte Nachbarschafts- oder Nordseeküstenliste fehlt.
- Begrenzte Listen-zu-Listen-Abfrage für Quellraum → Zielraum einschließlich Güterstruktur, Qualitätszuständen und verständlichen Quellenangaben. Die heutigen B01–B03-Abfragen nehmen einzelne Gebietskennungen entgegen. B04s implementiertes `query_union` zählt dagegen Innen-/Außenverkehre eines Verbunds und ersetzt keinen ausgewählten Zielraumfilter.
- Bestätigungsdialog und Ergebnisprüfung in der späteren Modell-/Serverintegration. Vor dieser Umsetzung verspricht der Assistent noch keine automatische Bearbeitung solcher offenen Raumformulierungen.
- Zusätzliche Tests für mehrdeutige Räume, Stadt versus Landkreis, Küstenkreis versus Hafen, doppelte/überlappende Kreislisten, fehlende Daten und verweigerte Straßen-Güteraufteilung. Diese Anforderung ist zusätzlich zu den bisherigen 45 Fällen zu planen; deren Anzahl wird nicht still geändert.

Verkehr **nach Hamburg** oder in einen Küstenkreis ist nicht automatisch Hafenhinterlandverkehr. Hafen-, Terminal- oder KV-Nutzung sowie Routen, Umschlagketten und gewinnbare Transportmengen sind damit nicht nachgewiesen. Unterschiedliche Verkehrsstatistiken dürfen auch nicht ohne Weiteres als Zahl eindeutig verschiedener Sendungen addiert werden.

## 23. B01–B03: Gemini-Zweitprüfung, Korrekturen und erneute Freigabe

**Stand 09.09.2026:** Gemini 3.8 Flash (High) prüfte die bisherigen B01–B03-Programme, Prüfer und dokumentierten Stände ausschließlich lesend. Die bestätigten Befunde wurden selbst überprüft und korrigiert. Die Korrekturen wurden anschließend durch lokale Quellen-/Funktionstests geprüft, nicht durch einen behaupteten weiteren Gemini-Lauf. Originalbefund und vollständige Einordnung: [Befund](../../outputs/gemini_b0103_20260909/BEFUND_ORIGINAL.md), [Bewertung und Behandlung](../../outputs/gemini_b0103_20260909/AUSWERTUNG.md).

| Paket | Neuer Datenstand | Tatsächlicher Prüfstand |
|---|---|---|
| B01 | `dea0378af6f4f6dea076` | 159/159 bestanden, lokal aktiviert |
| B02 | `cc36b3f63ef24d526897` | 178/178 bestanden, lokal aktiviert |
| B03 | `7deae62d547a876417ef` | 201/201 bestanden, lokal aktiviert; zusätzlich drei echte lokale Aufrufe für Schiene, VD2 und VD3c nach Aktivierung erfolgreich |
| B04–B06 | `603097102c408e95a15e` | 199/199 Hauptprüfungen und 10/10 Partnerkontrollen bestanden, lokal aktiviert |

Jeder Bestand liegt unter `data/analysis/<Paket>/releases/<Datenstand>/`; bei B04–B06 lautet der Paketordner `b0406`. `manifest.json` und `validation.json` sind die konkreten Nachweise, bei B04–B06 zusätzlich `partner_mapping_validation.json`. Aktivierte Stände sind über die jeweiligen `current.json` bezeichnet. Die erneuerte Kette ist nach bestandener B04–B06-Nachprüfung gemeinsam lokal freigegeben, mit unveränderten fachlichen Grenzen.

**Korrigiert:** Gesamtstatus leerer/unvollständiger B02-Reihen; verständliche Ablehnung von `total` für B03-Straßenprodukte; ganzzahlige Jahresparameter; keine fälschliche Null-Teilsumme bei ausschließlich unbekannten B03-Schienenwerten. Prüfer-/Aufrufcode ist in den jeweiligen Manifesten gebunden; B01/B02/B03-Verweise enthalten nun jeweils Manifest- und Prüfberichtprüfsummen.

**Zusätzlich geprüft:** In B01 sämtliche Originalzellen für alle drei verkehrsträgerspezifischen Kennzahlen, einschließlich 3.397 Rohzeilen außerhalb der früheren räumlichen Auswahl und eindeutiger Belegschlüssel. In B02 alle SGV-/IWW-Monate auch für tkm und Ladeeinheiten/Ladungsträger unabhängig gegen CSV, außerdem IWW-Abfragen für drei Kennzahlen und drei Richtungen. Neue Fehlerfall-/Aufruftests sind in `scripts/validation/check_b0103_regressions.py` in die Hauptprüfer eingebunden. B03-Parser-/Abfragetests simulieren vor Freigabe nur die Freigabedatei; die drei zusätzlichen echten Prozessaufrufe nach Aktivierung verwendeten den tatsächlich geprüften Stand.

**Unverändert und weiter begrenzt:** Die Datenartefakte von B01, B02 und B03 sind jeweils bytegleich zum vorherigen Stand; neue Versionen binden die korrigierten Programme und die erweiterten Prüfer. Amtliche Quellen wurden nicht geändert. NUTS-Metadatenkonflikte und ungeklärte Vergleichbarkeit bleiben sichtbar. Der feste Arbeitsordner `C:\tmp` bleibt gemäß AGENTS.md bestehen. Keine Straßen-Güterstruktur auf Relationen, keine Ableitung von Terminalpotenzialen oder Hafennutzung aus Kreisverkehren. Keine Änderung des Dashboards, kein Server-/Requesty-Aufruf und keine B07-Umsetzung.

Vorgänger bleiben erhalten. Die neue, nicht aktivierte B01-Vorstufe `a16f9675e09cb1042821` enthält den ersten Aufbau vor Korrektur eines Kontroll-SQL-Syntaxfehlers. Die nachfolgende separate Originalzellprüfung bestand; der endgültige Stand wurde vollständig neu aufgebaut und erneut geprüft. Der neue Terminalfall in Abschnitt 22 ist als Anforderung dokumentiert, nicht als zusätzliche bereits getestete Modellfunktion oder Änderung der 45 bisherigen Testfälle.


## Ergänzung: sichtbares Fragenkontingent (10.09.2026)

Die lokale KI-Oberfläche enthält jetzt die Kontingent-Vorschau „x von 50 Fragen gestellt“ mit Fortschrittsbalken. 50 Fragen pro Kalendermonat sind ein Demonstrationswert aus der Nutzeranforderung, keine abschließend festgelegte Lizenz. Testfragen erhöhen den Zähler; bei 50 wird weiteres Absenden gesperrt. Monat und Zähler werden innerhalb der Browsersitzung gespeichert, ohne Fragetexte. Monatswechsel nach Europe/Berlin; keine echte KI-Abfrage und keine Änderung an B01–B07.

Bei der Testportal-Anbindung sind Limit, Verbrauch und Zeitraum aus dem angemeldeten Lizenzkonto zu beziehen und auf dem Server durchzusetzen. Die lokale Vorschau ist keine Zugriffskontrolle. Vor Aktivierung festlegen, welche erfolgreichen, abgewiesenen oder fehlgeschlagenen Anfragen das Kontingent belasten; parallele Anfragen, Wiederholungen und mehrere Sitzungen müssen konsistent behandelt werden. Die sichtbare Vorschau ist umgesetzt; Portal-, Abrechnungs- und Modellanbindung bleiben offen.


### Kontingentanzeige nach Nutzerfeedback (10.09.2026)

Die zuvor beschriebene prominente Kontingentanzeige wurde durch einen kleinen Balken mit „x von 50 Fragen“ links unter dem Eingabefeld ersetzt. Die dauerhaft sichtbare Kontingent-Vorschauzeile entfällt; ein Fragezeichen erläutert im hellen Hinweis das Monatskontingent und dessen Rücksetzung. Dies ändert nur die Oberfläche: 50 bleibt der lokale Demonstrationswert, serverseitige Lizenzzählung und Modellanbindung bleiben offen.

## 24. Goal: lokale Verbindung und Vorbereitung des Testdeployments (10.09.2026)

**Neue Nutzervorgabe:** Basic erhält fünf, Premium 50 KI-Fragen je Kalendermonat. Damit ist die ältere Vorgabe „Basic ohne KI“ in den Abschnitten 1/8 überholt. Die Zählung wird je Benutzer und Werkzeug in der bestehenden Portal-Datenbank der jeweiligen Umgebung vorgesehen; umfangreiche Fachdaten bleiben im privaten Werkzeugbereich. Keine zusätzliche AlwaysData-Datenbank angelegt.

**Einordnung der 45 Fälle:** Der Terra-Erkundungslauf vom 09.09. wurde bereits durchgeführt. Offen ist der gebündelte Nachtest über die neue ausführbare Anwendung mit dem geladenen Systemprompt. Ein Quellen-/Datentest, eine simulierte Modellauswahl und ein `GET /models` sind kein solcher Fachfragenlauf. Die alte Angabe offener H-03 bis H-10 am Dokumentanfang ist ebenfalls überholt: QS-Plan Abschnitt 10.9 dokumentiert alle zehn als bestanden.

**Umgesetzt:** Neue getrennte Anwendung unter `server/analyseassistent/`, ohne Änderung der geprüften B01–B06-Programme. Zwölf begrenzte Adapter, Prüfbindung der aktiven Bestände, strikte Parameterformate und konservative Herkunftsprüfung, Laden des Systemprompts, begrenzter Requesty-Transport, serverseitige Tabellen/Kurzfassungen und Prüfung der optionalen Aussageauswahl. Keine freie SQL-/Dateiauswahl des Modells und keine automatische Reparaturschleife. Ein WSGI-Endpunkt und ein ausschließlich lokaler HTTP-Server mit künstlichem Testkonto sind vorbereitet.

**Kontingent:** Lokaler SQLite-Prototyp mit atomarer Reservierung, Basic 5/Premium 50, Europe/Berlin-Monat, Erhalt des Verbrauchs beim Paketwechsel und Wiederholschutz. Zahlenhaltige abgeschlossene Analysen zählen einmal; technische Fehler/Rückfragen belasten das Monatskontingent nicht. Zusätzliche technische Abrufbegrenzung. PostgreSQL-Schema als nicht angewendeter Entwurf unter `integration/analyseassistent/portal_schema.sql`; echter Portal-/Hankoresolver, PostgreSQL-Adapter und Benutzerverwaltungsansicht noch offen. Bestehende Tableau-Lizenznotizen unverändert.

**B07:** Auf Nutzerwunsch vorhandene Berliner Auszüge zuerst geprüft, kein neuer Netzabruf. Aktivierter Stand `93390e3aeb43d8f8b08845c8`, 23.685 Zeilen, 24 Monats-/Richtungsdateien, August 2025 bis Juli 2026. Typ-/Monats-/Richtungs-/Eindeutigkeitskontrollen und zwölf Binnenabgleiche bestanden. T37 kann damit reale Monatswerte prüfen. T38 hat weiterhin kein reales Vorjahresmonatspaar; diese Lücke wird ausgegeben, keine Rate erfunden. Keine neue externe Vollständigkeitsbestätigung.

**Requesty:** Schlüssel vom Nutzer über ein lokales Windows-Eingabefenster hinterlegt, DPAPI-verschlüsselt außerhalb des Projekts. Einlesen und Modellverfügbarkeit von `vertex/gemini-3.7-flash@eu` am EU-Endpunkt bestätigt. Keine Fachfrage versendet. Die vorläufige technische Testfrist von 180 Sekunden ist kein Leistungsziel; Antwortzeiten und Anbieterkompatibilität des vollständigen Ablaufs bleiben zu messen.

**45-Fälle-Vorbereitung:** Alle 45 Fragen als getrennte Modelleingaben/Referenzen unter `tests/analyseassistent/` vorbereitet. Sieben Adapterzuordnungen sind prüfbare Ausgangspunkte; noch keine vollständige Fallfreigabe. Zusammengesetzte Profile, weitere Rankings, regionale Güter-/Modal-/KV-Auswertungen, Quellenklärungen und einige konkrete Testauswahlen müssen vor dem vollständigen Lauf ergänzt werden. Die Bereitschaftsprüfung weist diese Voraussetzungen aus und bezeichnet sie nicht als bestanden.

**Nächster Schritt:** Fallverträge und fehlende Funktionskombinationen vervollständigen, danach ein gebündelter Modelltest mit getrennten Sollantworten. Anschließend PostgreSQL-/Portaladapter und Dashboardanschluss im lokalen Zusammenspiel prüfen, vollständigen Portal-Testrelease bauen, Planmodus prüfen und erst dann Testumschaltung samt Rechte-, Browser- und Rückfallprüfung. Vorhandene Website/Portalproduktion bleibt unverändert.

Ausführung, Grenzen und Paketierung: [Lokaler Pilot](../betrieb/ANALYSEASSISTENT_LOKALER_PILOT.md). Tatsächliche Prüfergebnisse: Qualitätssicherungsplan und `outputs/analyseassistent_runtime_20260910/validation.json`. Das Goal ist weiter aktiv; der erste lokale Pilot ist kein abgeschlossenes Testdeployment.

### Fortschritt: Regionsprofil, Modal Split und Prognosevergleich

**10.09.2026, nach dem ersten Pilotstand:** Drei zusätzliche Adapter sind eingebunden: `region_profile`, `regional_modal_split` und `forecast_comparison`. Damit bestehen 15 begrenzte ausführbare Adapter; dies ist nicht gleichbedeutend mit der vollständigen Abdeckung der 15 fachlichen Fragetypen. Sie verwenden ausschließlich den unveränderten geprüften B04–B06-Bestand. Regionalprofil einschließlich sieben Gütergruppen, Richtungen und Saldo; regionale Anteile nur mit vollständigem, zum Profilgesamt passenden Nenner; Ist-Jahre und VP2019_BASE/2040_P1 getrennt. Veränderungsraten werden ausschließlich innerhalb der VP berechnet, bei positivem Basiswert. Keine Standortbewertung und keine Ursache aus Verkehrsvolumen abgeleitet.

**Nachweis:** 28/28 lokale Laufzeittests in `outputs/analyseassistent_runtime_20260910/profiles_validation_httpfix.json`. Der neue Katalogvorlauf `preflight03/report.json` führt elf strukturierte Fälle aus, darunter T01, T03, T24 und T29; 34 Fallverträge bleiben offen. Keine Modellaufrufe, weiterhin keine fachliche 45-Fälle-Abnahme. T22 und T35 behalten ihre Teilverfügbarkeit. Zusätzlich behoben: lokaler HTTP-Verbindungsabbruch bei frühzeitig abgewiesenen Anfragen mit noch ungelesenem kleinem Requestbody; UTF-8 für die Windows-Unterprozesse des Kataloglaufs ausdrücklich aktiviert.

Das ältere Übergabepaket `C:\tmp\gueterstroeme-assistant-20260910-pilot03` enthält diese Ergänzungen noch nicht und ist kein aktueller Deploymentkandidat. Neu paketieren erst nach den weiteren Funktions- und Portalergänzungen. Nächste offene Funktionsbereiche bleiben weitere Ranglisten, regionale Güter-/KV-Auswertungen und Quellenklärungen; anschließend gebündelter Requesty-Test und Portalanschluss. Das Goal bleibt aktiv.

### Fortschritt: Relationspartner, Jahresabdeckung und vollständige Befunde

**10.09.2026, zweite Erweiterung:** 20 ausführbare, weiterhin begrenzte Adapter. Neu: Partner-Ranking aus sämtlichen veröffentlichten B01-Relationen mit Nenner vor Top-Begrenzung und Ranggleichständen; konkrete Relation in beiden Richtungen und drei getrennten Verkehrsträgern; regionale Jahresfolge; mehrere regionale Modal-Split-Jahre; Knotenprofil mit getrennten Einheiten. B01–B06-Programme und Datenbestände unverändert.

**Fachliche Korrektur:** D01 enthält für Straße 2025 technische Nullen, obwohl der Quellenjahrgang fehlt. Die neuen Profilfunktionen prüfen deshalb zusätzlich die gebundene B02-Jahresabdeckung. Für fehlende Modi werden keine Nullwerte und keine vollständigen Modalanteile ausgegeben; Gesamt-/Güterprofile bleiben dann unvollständig. Die unveränderten Dashboarddaten sind hierdurch nicht korrigiert oder neu freigegeben.

**Antwortausgabe vervollständigt:** Regionsvergleich mit sieben Gütergruppen, passenden Strukturanteilen und absoluter Differenz; Schienenrelation mit C1–C7, Original-Feinpositionen und bekannter Zeilensumme; nationaler Transit mit eigenem Modalnenner; Jahres-/Monatswerte und Spitzenanteil bei vollständigen zwölf Monaten; VP-Ranking mit Rang, Basis-/Zielwert, absoluter und relativer Änderung. Fehlende Positionen bleiben unbekannt. Alle numerisch belegten Aussagen stehen der Auswahlphase zur Verfügung, höchstens vier erscheinen in der Kurzfassung. Die Auswahlphase bekommt die ursprüngliche Frage und die geprüften Parameter; Sollantworten bleiben getrennt.

**Prüfstand:** 40 lokale Tests; abschließender Nachweis `outputs/analyseassistent_runtime_20260910/relations_validation_verified.json`. `preflight04/report.json`: 21 strukturierte Fälle ausgeführt (14 `ok`, sieben `partial`), 24 Fallverträge noch offen, null Modellaufrufe. Die später ergänzte vollständige Aussageauswahl ist im abschließenden Laufzeittest geprüft; historische Katalogdateien bleiben unverändert. T37/T38 konkret auf Berlin Juli 2026 und angefragten Juli 2025 vorbereitet, T40/T41 für den lokalen Test ausdrücklich Population I; diese Auswahl ist kein stiller Produktstandard. T38 bleibt wegen fehlendem Vorjahresmonat ohne Vergleichsrate und ist noch kein vollständiger Relations-Ranking-Vertrag.

**Weiter offen:** Unter anderem regionale Güterstruktur je Verkehrsträger, KV-Teilmärkte, Quellen-/Machbarkeitserklärungen, weitere zusammengesetzte Fälle sowie vollständige Fallabnahme. Die nötigen modebezogenen Güterfelder sind im bestehenden D01-Originalprofil vorhanden, aber im bisherigen B04-Profilabbild nicht enthalten. Für eine Erweiterung diese Felder mit Quellenbindung separat paketieren; die geprüften B01–B06-Bestände nicht still verändern. Erst nach der Fallvorbereitung folgt der gebündelte Requesty-Test, anschließend Portal-/PostgreSQL-Anschluss und Testbereitstellung. Das Goal bleibt aktiv.

### Fortschritt: gebundene Güter-/KV-Daten und Methodikantworten

**10.09.2026, dritte Erweiterung:** Zusätzliches privates Datenpaket `assistant_support`, Stand `f8f8949c0654f9a42d4e5e94`. 3.984 vorhandene D01-Güterprofile quellidentisch projiziert und 34.270 KV-Kennwertdatensätze aus 25 an B01 gebundenen Schienen-/IWW-Rohdateien gebildet. 32.296 Vergleiche mit dem bestehenden Dashboardbestand; darunter 140 rechnerisch vollständig erklärte Abgrenzungsdifferenzen. Alle 27 Eingangsdateien nach Aufbau nochmals mit den gespeicherten Prüfsummen abgeglichen, unverändert. Keine Änderung der B01–B07-Daten oder der Dashboarddateien.

**Abgrenzungsbefund:** Das bisherige Dashboard-SQL zählt einen unbekannten Zielraum über CASE/ELSE zum Versand, während ein unbekannter Quellraum beim Empfang durch SQL-NULL-Vergleich ausgeschlossen wird. Im neuen Assistentenbestand verlangen externer Versand und Empfang einen bekannten Gegenraum. Unbekannte Gegenräume werden separat als `unassigned_outbound`/`unassigned_inbound` aufbewahrt; die jeweilige all-Abgrenzung bleibt ausdrücklich beschrieben. Die 140 Differenzen sind im Prüfbericht des Support-Pakets mit Jahr, Region, Richtung, Kennzahl und Betrag einzeln dokumentiert. Keine stillschweigende Gleichsetzung mit der alten Dashboardabgrenzung.

**Neu ausführbar:** Regionale C1–C7-Güterstruktur nach Modus und Richtung; getrennte KV-Teilmärkte mit jeweils eigenem Modalnenner; feste Methodik-/Klassifikationshinweise und Machbarkeitsgrenzen. Fehlende Quellenjahre, unvollständige Monate, unbekannte Werte und Ladeeinheitenkennungen sperren vollständige Kennzahlen. Keine künstliche Straßen-NST-20-Aufteilung auf NUTS-3, keine addierte KV-Gesamtsumme und kein Verlagerungspotenzial. Methodikantworten besitzen eigene Textbelege und Tabellen; sie erfinden keine numerischen Verkehrsangaben.

**Nachweis:** 48/48 lokale Laufzeittests in `outputs/analyseassistent_runtime_20260910/support_validation01.json`; 23 begrenzte Adapter, 30 zugeordnete Fachfälle. Katalogvorlauf unter `preflight05/report.json`, ohne Modellaufrufe und ohne automatische fachliche Abnahme. B07-Berlin und die bestehenden Kontingentprüfungen bleiben Bestandteil des lokalen Laufzeittests. Der Paketbuilder berücksichtigt das zusätzliche private Datenpaket über dessen Manifest; das frühere Übergabepaket bleibt veraltet.

**Nächster Schritt:** Die 15 verbleibenden Fälle konkret als ausführbare kombinierte Abfrage, absichtliche Rückfrage oder belegte Grenze festlegen. Synthetische Rechenbeispiele bleiben getrennte Prüfbelege und werden nicht als reale Datenabdeckung ausgegeben. Insbesondere Straßenrelation mit expliziter Gütergrenze und Schienen-Feinpositionen über zwei Jahre noch zusammensetzen; vorbereitete Antworten fachlich gegen die getrennten Referenzen prüfen. Danach der vereinbarte gebündelte Requesty-Test mit echtem Systemprompt; Portal-/PostgreSQL- und Dashboardanschluss bleiben weiter offen. Das Goal bleibt aktiv.

### Fortschritt: erster vollständiger Requesty-Lauf und gezielte Nachprüfung

**10.09.2026:** Der hinterlegte Windows-DPAPI-Schlüssel wurde erfolgreich für den vereinbarten EU-Zugang verwendet. 25 begrenzte Datenadapter; 32 konkrete Datenfälle und 13 Fälle mit fehlender Auswahl vorbereitet. Die Freigabedatei `outputs/analyseassistent_runtime_20260910/model_gate01.json` bindet den damaligen Programmstand, Eingaben, Referenzen und Datenstand an 52 bestandene lokale Tests. Diese Freigabe erlaubt die Modellevaluation, ist keine fachliche Gesamtabnahme.

**Echter Lauf:** `outputs/analyseassistent_runtime_20260910/requesty45_run01/report.json`, alle 45 Fälle bearbeitet, 75 Modellaufrufe an `vertex/gemini-3.7-flash@eu`. Geladener Systemprompt, bestätigte Filter und angebotene Datenfunktionen; danach gegebenenfalls Auswahl aus serverseitig belegten Aussagen. Sollantworten bleiben außerhalb des Modellprozesses. Laufdauer einschließlich Prozessstart und Datenprüfung rund acht Minuten; mittlere Fallzeit als Median 8,765 Sekunden. Keine automatische Wiederholung fehlgeschlagener Modellaufrufe.

**Nachprüfung:** `requesty45_review02.json` meldet 42 bestandene Ablauf-/Datenvergleiche und drei Befunde: T13 ohne implementiertes Ist-Änderungsranking, T30 mit unvollständiger Modellantwort, T44 mit ungeeignetem allgemeinem Quellenhinweis. Die 408.047 erfassten Tokens betreffen 74 von 75 Aufrufen; zum unvollständigen T30-Aufruf wurde im damaligen Programmstand kein Verbrauch gespeichert. Das ist keine vollständige Verbrauchs- oder Kostenabrechnung.

**Gezielt korrigiert:** Der Systemprompt verlangt bei konkreter Reproduktionsauswahl die passende Datenfunktion. Bei unvollständigen Antworten kann der Transport nun begrenzten Abbruchstatus und numerische Verbrauchsangaben festhalten, ohne fremden Fehlertext auszugeben. 54/54 lokale Tests bestanden (`post_requesty_validation01.json`). T30 und T44 mit unveränderten Eingaben anschließend gezielt erneut geprüft: drei zusätzliche Modellaufrufe, richtige Rückfrage bei T30, richtige Schienenrelation bei T44. Ergebnis und Vergleich: `requesty_targeted02/review.json`. Kein neuer vollständiger 45er-Lauf; die frühere Freigabedatei gilt nicht für den geänderten Programmstand.

**Weiter offen:** T13-Funktion und Quellenvergleichbarkeit, T35-Ländernamen, T43 konkreter Nachweis der 422/400/22 Gebiete sowie die Vollständigkeit und Verständlichkeit aller Kurzfassungen. T30s Rückfrage belegt noch keine Bereitstellung alternativer Prognoseszenarien. B07 besitzt weiterhin keinen gleichmonatigen Vorjahresvergleich. Für das Portal sind PostgreSQL-Schema und Kontingentadapter unter `integration/analyseassistent/` vorbereitet, aber noch nicht angewendet oder gegen PostgreSQL geprüft. Nächster Integrationsschritt: echte Transaktionsprüfung, Hanko-/Werkzeugrechte und Benutzerverwaltung im Plattform-Repository anschließen, danach Dashboard und vollständigen Testrelease bauen. Kein Testdeployment und keine Produktionsänderung. Das Goal bleibt aktiv.

Abschließend 55/55 lokale Tests bestanden (`post_requesty_validation02.json`); Freigabe bindet jetzt ausdrücklich auch Systemprompt, Fachregeln und Testtreiber. Kein weiterer Modelllauf oder Deployment.

### Fortschritt: Testantworten lesbar und Kontingentlogik gegen PostgreSQL geprüft

**10.09.2026:** Alle 45 Testfragen sind jetzt mit ausgegebenen Antworten, Tabellen, Quellen und Rückfragen in `outputs/analyseassistent_runtime_20260910/lesebericht01/index.html` lesbar; Markdown-Datei daneben. Die beiden Nachprüfungen ersetzen die ursprünglichen Modellprotokolle nicht. Nutzer meldet aus Requesty 78 Requests für insgesamt 0,51 USD, passend zu 75 plus drei dokumentierten Aufrufen. Kein neuer Modelllauf für diese Übersicht.

**Portalvorbereitung:** Das KI-Schema und der Kontingentadapter bestehen neun echte Tests auf einer eigenen lokalen PostgreSQL-13.3-Instanz mit dem aktuellen Portal-Migrationssatz und künstlichen Konten. Nachweis `postgres_validation02.json`; Begrenzung bei parallelen Anfragen, Idempotenz, Paketwechsel, Rechte, Monatszuordnung und Transaktionsrücknahme geprüft. Instanz beendet und temporärer Cluster entfernt. Test-/Produktivportal nicht angesprochen; lokale Prüfung ersetzt keine Liveabnahme.

**Nächster Schritt:** Hanko-Identität mit Issuer in die interne Portalidentität auflösen, PostgreSQL-Adapter in das tatsächliche Werkzeugrouting einbinden und Basic/Premium samt Verbrauch in der administrativen Oberfläche ergänzen. Danach Dashboardanschluss und vollständiger Testrelease; fachliche Restpunkte T13/T35/T43 und Kurzfassungsprüfung weiter bearbeiten. Goal aktiv, Produktionssystem unverändert.

### Fortschritt: verständliche Antworten mit begründeten Alternativen

**10.09.2026:** Kundenantworten besitzen jetzt freundliche konkrete Rückfragen, lesbare Tabellen und fachlich passende Einschränkungen. Technische Belege stehen getrennt. Bei einer nicht verfügbaren Gütergliederung einer Straßenverbindung prüft der Ablauf am selben Datenstand passende Schienen- und Regionalauswertungen und erläutert den Veröffentlichungsstand beim Binnenschiff. T20 belegt Schienengüter Köln → Hamburg und regionale Straßenprofile; die fehlende Binnenschiffszeile wird ausdrücklich nicht als fehlender Verkehr interpretiert. Regionalprofile einschließlich Binnenverkehr sind keine Güteraufteilung der einzelnen Verbindung.

**Prüfstand:** 63/63 lokale Tests in `customer_portal_validation02.json`; bestehende Lesefassung aktualisiert, ursprüngliche Modellantworten erhalten. Keine neuen Requesty-Aufrufe. Lokaler Portaladapter mit Hanko-/Issuer-Zuordnung, CSRF und sicherer Behandlung fehlgeschlagener Verbrauchsbuchungen vorbereitet. Noch keine Übernahme in das echte Portalrouting, keine administrativen Paketfelder und kein Testdeployment. Der nächste Integrationsschritt bleibt der tatsächliche Plattformanschluss; fachliche Antwortprüfung und T13/T35/T43 bleiben offen. Goal aktiv.

### Fortschritt: Portalrouting und Basic/Premium in der Kundenverwaltung

**10.09.2026:** Der lokale Anschluss ist nun im tatsächlichen Plattform-Repository umgesetzt: geschützte Güterströme-Anfragewege, testweise Aktivierung, Paketauswahl am Kundenkonto und Monatsverbrauch. Sperren und Paketwechsel erhalten die Anfragehistorie; auch der bestehende Rechteeditor setzt den Verbrauch nicht zurück. Migration 009 ergänzt Kontingenttabellen und einen zunächst inaktiven Werkzeugeintrag. Normale Werkzeugrechte bleiben zusätzlich erforderlich.

**Nachweis:** 47 bestandene Portal-/Releaseprüfungen (`portal_integration_validation02.json`) und 14 bestandene echte PostgreSQL-Tests (`postgres_portal_validation04.json`). Eigene lokale Datenbank mit künstlichen Konten wieder entfernt; keine Liveverbindung. T20 ist vom Nutzer als Referenz für Ton und Aufbau der Startphase bestätigt, noch kein Beleg gleichbleibender Qualität aller Modellfälle.

**Nächster Schritt:** Dashboard-/Antwortoberfläche und Folgefragen mit den geschützten API-Pfaden verbinden, vollständigen aktuellen Testrelease mit privatem Analysebestand erstellen und lokal im Browser prüfen. Anschließend tatsächliche Testkonfiguration, Planmodus und Testdeployment prüfen. Aktuelle Portaldateien sind lokal geändert, noch nicht ausgerollt; Produktionssystem unverändert. Goal aktiv.

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

### Beleggebundene Antwortsynthese und Mehrjahresrelation – beta04 (11.09.2026)

Version 0.2.1 setzt die Ergebnisse nicht mehr nur in Tabellen um. Für die numerischen Fragetypen berechnet der Server Kernaussagen, die Werte miteinander in Beziehung setzen. Anfangs- und Endwerte derselben veröffentlichten Reihe werden als rechnerisches Wachstum beziehungsweise rechnerischer Rückgang ausgewiesen. Ein optionaler Antwortaufruf formuliert daraus höchstens drei Absätze und verweist je Absatz auf die verwendeten Belege. Der Server lehnt fremde Kennungen, neue Zahlen, veränderte Einheiten sowie unbelegte Ursachen, Bewertungen und Empfehlungen ab. Die analytische Serverfassung bleibt als Rückfall erhalten; lange Tabellen werden zunächst eingeklappt.

Der konkrete Rosenheim–Augsburg-Fall wird als `relation_history` für 2020–2024 erkannt, einschließlich der kurzen Folgeantwort „mehrere Jahrgänge“. Die Schienenwerte 2.175 Tonnen (2020) und 1.066 Tonnen (2024) werden als rechnerischer Rückgang von 50,99 % eingeordnet. Für Straße und Binnenschiff wird eine statistische Datenlücke benannt, nicht tatsächlich ausgebliebener Verkehr behauptet. Drei `gpt-5.6-terra`-Subagenten prüften ausgewählte Fälle, Promptgrenzen und technische Robustheit. 83/83 lokale Prüfungen und die gezielte Linux-Prüfung des aktiven Release bestehen.

`portal-test-20260911-gueterstroeme-beta04` ist auf Testsite 1067000 aktiv. Manifest `4d2cc83bb1e65b491486cdff58f887186e49e570e4387f86377e266276f5f6d6`, 1.706 Dateien. 64 geänderte Nutzdateien plus Manifest wurden übertragen, 1.642 Dateien serverseitig unabhängig kopiert und anschließend vollständig geprüft. Keine Produktionsänderung, kein neuer Modellaufruf und keine Kundenbuchung. Eine erneute angemeldete Browserprüfung und eine neue 45-Fälle-Gesamtabnahme bleiben offen.
