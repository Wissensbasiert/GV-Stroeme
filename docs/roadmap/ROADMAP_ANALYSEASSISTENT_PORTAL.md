# Roadmap: Analyseassistent, Premiumzugang und Portalbetrieb

**Stand:** 31.08.2026  
**Status:** Technisches Grobkonzept; Umsetzung nach fachlicher Datenfreigabe  
**Bezug:** Güterverkehrsströme Deutschland und WBP-Solutions-Portal auf AlwaysData

## 1. Zweck des Dokuments

Dieses Dokument beschreibt die nächsten Schritte, um das bestehende Güterströme-Dashboard in das WBP-Solutions-Portal zu übernehmen und den derzeitigen Interface-Prototyp des Analyseassistenten zu einer belastbaren Produktfunktion auszubauen. Es dient als gemeinsame Roadmap für weitere Arbeitschats und als Ausgangspunkt für die spätere technische Umsetzung.

Ziel ist eine gemeinsame Anwendung mit zwei Nutzungsstufen:

- **Basispaket:** Zugriff auf das Güterströme-Dashboard ohne KI-Auswertung.
- **Premiumpaket:** zusätzlicher Zugriff auf den Analyseassistenten.

Die Benutzeroberfläche bleibt grundsätzlich für beide Pakete gleich. Die Berechtigung für den Analyseassistenten wird jedoch serverseitig geprüft und durchgesetzt.

## 2. Aktueller Ausgangsstand

- Das Dashboard liegt als statische Browseranwendung mit modular aufgebauten HTML-, CSS- und JavaScript-Quellen vor.
- Ein gestalteter Interface-Prototyp des Analyseassistenten ist lokal integriert. Er besitzt noch keine Verbindung zu einem KI-Modell oder einer serverseitigen Datenschnittstelle.
- Der Prototyp verwendet die Bezeichnung **Analyseassistent** und das Datenkorridor-Symbol `assets/icons/gueterstrom-ki-variante-c-datenkorridor.svg`.
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

**Ergebnis:** zehn bis fünfzehn Fragetypen mit Datenquelle, Parametern, Antwortformat und Prüferwartung.  
**Freigabepunkt:** fachliche Bestätigung des Fragen- und Antwortkatalogs.

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

Nach der vorgesehenen letzten Datenprüfung wird zunächst Etappe 0 abgeschlossen. Anschließend wird für Etappe 1 eine kompakte Arbeitstabelle mit zehn bis fünfzehn typischen Nutzerfragen erstellt. Für jede Frage werden die benötigten Filter, Datenfelder, Berechnungen, Quellenhinweise und erwarteten Antwortbestandteile festgelegt.

Diese Tabelle bildet die verbindliche Brücke zwischen fachlicher Datenprüfung und technischer Entwicklung. Erst auf dieser Grundlage werden Datenfunktionen, API und KI-Anbindung programmiert.

