# Roadmap: Fachliche Weiterentwicklung des Güterströme-Dashboards

**Stand:** 03.09.2026  
**Status:** Fachliches Konzept; Umsetzung nach Prüfung und Ergänzung der Datenquellen  
**Bezug:** Güterverkehrsströme Deutschland

## 1. Zweck des Dokuments

Dieses Dokument hält fachliche und gestalterische Entscheidungen für die weitere Entwicklung des Güterströme-Dashboards fest. Im Mittelpunkt stehen die Ergänzung eines Moduls zu Luftfracht und Flughäfen sowie eine übersichtlichere Navigation auf Desktop- und Mobilgeräten.

Die Roadmap ist von der Datei [`ROADMAP_ANALYSEASSISTENT_PORTAL.md`](ROADMAP_ANALYSEASSISTENT_PORTAL.md) getrennt. Dort werden Analyseassistent, Premiumzugang und Portalbetrieb behandelt. Die vorliegende Roadmap betrifft dagegen die fachliche Erweiterung und Benutzerführung des Dashboards selbst.

## 2. Grundentscheidung zum Luftverkehr

Der Luftverkehr wird als eigenes, bewusst schlankes Analysemodul **Luftfracht & Flughäfen** ergänzt. Das Modul erweitert die Verkehrsträgerperspektive um hoch spezialisierte internationale Logistikknoten. Seine Bedeutung wird nicht allein über die im Vergleich zu Straße, Schiene und Binnenschifffahrt geringe Beförderungsmenge begründet, sondern über die räumliche Konzentration, die internationalen Beziehungen und die Bedeutung für zeitkritische, hochwertige oder verderbliche Güter.

Das Modul wird nicht in den bestehenden Modal Split der drei landseitigen Verkehrsträger einbezogen. Die verfügbaren Luftverkehrsdaten weisen andere räumliche Einheiten, Erfassungslogiken und Kennzahlen auf. Insbesondere ist in den vorgesehenen Quellen keine mit den vorhandenen Verkehrsträgern unmittelbar vergleichbare Tonnenkilometerreihe enthalten.

## 3. Vorgesehene Datenquellen und ihre Rollen

Für das Modul werden drei Eurostat-Tabellen mit klar getrennten Aufgaben verwendet:

| Tabelle | Aufgabe im Modul | Begründung |
| :--- | :--- | :--- |
| **AVIA_GOOC** | Nationale Gesamtwerte und Entwicklung der Luftfracht und Post in Deutschland | Die Tabelle liefert die belastbare nationale Randsumme und vermeidet, dass nationale Werte aus Flughafen- oder Relationsdaten selbst gebildet werden müssen. Sie ist die maßgebliche Quelle für nationale Kennzahlen. |
| **AVIA_GOOA** | Reihenfolge, Aufkommen und zeitliche Entwicklung der deutschen Flughäfen | Die Tabelle liefert vollständige aggregierte Werte je Flughafen. Sie ist erforderlich, um den Status quo und die Dynamik der Flughafenstandorte darzustellen. |
| **AVIA_GOR_DE** | Wichtigste veröffentlichte Beziehungen zwischen deutschen Berichtsflughäfen und Partnerflughäfen | Die Tabelle ermöglicht die Relationskarte und die Tabelle der stärksten Verbindungen. Sie wird nicht für nationale oder flughafenbezogene Gesamtwerte verwendet. |

### 3.1 Warum AVIA_GOOC allein nicht ausreicht

AVIA_GOOC wäre ausreichend, wenn ausschließlich das nationale Luftfrachtaufkommen und dessen Entwicklung gezeigt werden sollten. Das geplante Modul soll jedoch auch beantworten, welche Flughäfen das Aufkommen prägen und wie sich ihre Position im Zeitverlauf verändert. Dafür wird AVIA_GOOA benötigt.

AVIA_GOOA ersetzt umgekehrt nicht die nationale Randsumme aus AVIA_GOOC. Eine eigene Addition von Flughafenwerten kann insbesondere bei innerdeutschen Verkehren zu einer anderen Zähllogik führen. Nationale Kennzahlen und Flughafenwerte bleiben deshalb als getrennte, jeweils direkt aus der zuständigen Aggregation übernommene Datenebenen erhalten.

AVIA_GOR_DE ergänzt diese beiden Ebenen um veröffentlichte Flughafenbeziehungen. Die drei Tabellen sind damit nicht redundant, sondern bilden eine abgestufte Quellenarchitektur:

```text
Deutschland insgesamt: AVIA_GOOC
  → Flughäfen: AVIA_GOOA
    → veröffentlichte Flughafenbeziehungen: AVIA_GOR_DE
```

### 3.2 Geprüfte Datenstände und Umgang mit abweichenden Bezugsjahren

Die am 3. September 2026 lokal abgelegten Eurostat-Dateien weisen für das geplante Modul unterschiedliche letzte vollständige Jahresstände auf:

| Datenebene | Datei | Letztes vorhandenes Jahresfeld | Verwendung |
| :--- | :--- | :--- | :--- |
| Deutschland insgesamt | `estat_avia_gooc.tsv` | 2025 | nationale Kennzahlen und nationale Entwicklung |
| einzelne Flughäfen | `estat_avia_gooa.tsv` | 2025 | Flughafenrangfolge, Standortwerte und Dynamik |
| Flughafenbeziehungen | `estat_avia_gor_de.tsv` | 2024 | Karte und Top-10-Relationen |

Für die maßgebliche Kennzahl **Fracht und Post, geladen und entladen** (`FRM_LD_NLD`, Einheit Tonnen, Linienverkehr und Nichtlinienverkehr zusammen, Verkehrsabdeckung insgesamt) sind 2025 in AVIA_GOOA Werte für 22 deutsche Flughäfen ausgewiesen. Das Vorhandensein eines Jahresfeldes allein genügt künftig nicht als Freigabekriterium; zusätzlich müssen die benötigten Reihen tatsächlich mit Werten belegt sein.

Das Modul verwendet deshalb keinen scheinbar einheitlichen Datenstand. Jede Datenebene wird für das tatsächlich ausgewählte Jahr ausgewertet. Bei Auswahl von 2025 gilt nach dem derzeitigen Datenstand:

- **Deutschland: 2025**,
- **Flughäfen: 2025**,
- **Relationen: für 2025 nicht verfügbar; letzter verfügbarer Stand 2024**.

Die Anwendung mischt **keine älteren Relationsdaten automatisch unter ein neueres Auswahljahr**. Für 2025 dürfen die Flughafenstandorte und Flughafensummen aus AVIA_GOOA weiterhin sichtbar sein; Relationslinien und Top-10-Relationstabelle bleiben jedoch leer. Der Leerzustand wird aus den tatsächlich verfügbaren Jahren der Relationsdatei erzeugt und nicht fest auf 2024 programmiert. Vorgesehener Hinweis:

> Für das ausgewählte Jahr {Auswahljahr} liegen keine Relationsdaten vor. Das letzte verfügbare Relationsjahr ist {letztes Relationsjahr}. Bitte wählen Sie dieses Jahr in den aktuellen Einstellungen aus.

Optional kann der Hinweis einen Schalter **„{letztes Relationsjahr} auswählen“** enthalten. Das Auswahljahr darf sich nur nach bewusster Betätigung ändern, nicht automatisch. Titel, Filter und Datenstand bleiben damit jederzeit konsistent.

In der Dynamikansicht endet jede Zeitreihe an ihrem tatsächlich verfügbaren letzten Jahr. Linien werden nicht künstlich bis 2025 fortgeschrieben. Die Metadaten der späteren Webdatei führen `latestNationalYear`, `latestAirportYear` und `latestRelationYear` getrennt. Bei jeder Aktualisierung wird automatisiert geprüft, ob neue Jahresfelder vorhanden **und** für die vorgesehenen Messgrößen befüllt sind.

Die nationalen und die Flughafenwerte dürfen auch bei gleichem Jahr nicht gegeneinander ausgetauscht werden. Für 2025 ergibt die Addition von geladenen und entladenen Mengen über die Flughäfen rund 4,859 Mio. Tonnen, während AVIA_GOOC für die nationale Randsumme `FRM_LD_NLD` rund 4,767 Mio. Tonnen ausweist. Die Differenz ist fachlich plausibel, weil innerdeutsche Verkehre in der Summe der Flughafenaktivitäten an Lade- und Entladeflughafen erscheinen, in der nationalen Gesamtmenge jedoch nicht doppelt gezählt werden sollen. Die nationale Kennzahl wird daher stets direkt aus AVIA_GOOC übernommen.

### 3.3 Zeitlicher Beginn und Verfügbarkeitslogik

Das Luftfrachtmodul beginnt grundsätzlich im Jahr **2016**, weil die geprüften Reihen der drei vorgesehenen Tabellen ab diesem Jahr für die benötigten Auswertungen verfügbar sind. Die geprüfte Abdeckung lautet:

- nationale Kennwerte aus AVIA_GOOC: 2016 bis 2025,
- Flughafensummen und Flughafenentwicklung aus AVIA_GOOA: 2016 bis 2025,
- veröffentlichte Flughafenrelationen aus AVIA_GOR_DE: 2016 bis 2024.

Die Jahresauswahl kann damit 2016 bis zum jeweils neuesten nationalen beziehungsweise flughafenbezogenen Jahr anbieten. Für jede Datenebene werden separate Listen der tatsächlich verfügbaren Jahre aus den befüllten Reihen erzeugt. Die Oberfläche entscheidet anhand dieser Listen, ob ein Wert oder der beschriebene Leerzustand gezeigt wird. Eine bloße Jahresspalte ohne verwertbare Werte gilt nicht als verfügbares Jahr.

In der Dynamikansicht beginnt eine Reihe frühestens 2016 und endet an ihrem tatsächlich letzten verfügbaren Jahr. Fehlende Zwischenjahre werden als Datenlücke behandelt und nicht interpoliert.

## 4. Methodische Grenzen der Relationsdaten

Eurostat veröffentlicht in den Tabellen `avia_gor_*` nur Routen, die festgelegte Veröffentlichungsschwellen überschreiten. Die Schwellen werden für Personenverkehr sowie Fracht und Post getrennt bestimmt. Werte unterhalb der Schwelle werden mit `:` gekennzeichnet. Dieses Zeichen kann sowohl für einen nicht veröffentlichten Wert unterhalb der Schwelle als auch für keinen Verkehr auf der betreffenden Route stehen.

Die Relationsdaten bilden daher nur einen veröffentlichten Ausschnitt des tatsächlichen Verkehrs ab. Die Summe der dargestellten Beziehungen entspricht weder zwingend dem vollständigen Aufkommen eines Flughafens noch der nationalen Gesamtmenge. Zudem beschreiben Flughafenbeziehungen nicht in jedem Fall den tatsächlichen ursprünglichen Versand- und endgültigen Empfangsort einer Sendung.

Diese Einschränkungen werden im Modul an der Relationstabelle und in den allgemeinen Quelleninformationen erläutert.

### 4.1 Vorgesehener Informationstext für die Top-10-Relationen

> Die Tabelle zeigt die zehn stärksten veröffentlichten Fracht- und Postrelationen des ausgewählten Flughafens. Eurostat veröffentlicht in AVIA_GOR_DE nur Routen oberhalb festgelegter Schwellen. Mit `:` gekennzeichnete Angaben können entweder unterhalb der Veröffentlichungsschwelle liegen oder keinen Verkehr aufweisen. Die Relationsdaten sind daher nicht vollständig; ihre Summe entspricht nicht dem gesamten Fracht- und Postaufkommen des Flughafens. Die vollständigen Flughafenwerte stammen aus AVIA_GOOA, der nationale Gesamtwert aus AVIA_GOOC. Die dargestellten Flughafenbeziehungen entsprechen außerdem nicht zwingend dem ursprünglichen Versand- und endgültigen Empfangsort einer Sendung.

## 5. Inhalt und Aufbau des Moduls

Das Modul orientiert sich gestalterisch an den bestehenden Analysemodulen, übernimmt deren Aufbau jedoch nur dort, wo die Daten fachlich vergleichbar sind.

### 5.1 Kennzahlen

Vorgesehen sind kompakte Kennzahlen zu:

- Fracht- und Postaufkommen in Deutschland,
- Veränderung gegenüber dem Vorjahr,
- Zahl der Flughäfen mit ausgewiesenem Aufkommen,
- Konzentration auf die größten Frachtflughäfen.

Die nationale Gesamtmenge stammt aus AVIA_GOOC. Flughafenbezogene Kennzahlen werden direkt aus AVIA_GOOA übernommen.

### 5.2 Karte und Relationsdarstellung

Die Karte zeigt die deutschen Flughäfen als Punktsymbole. Größe beziehungsweise visuelles Gewicht der Symbole richten sich nach dem Fracht- und Postaufkommen des ausgewählten Jahres. Nach Auswahl eines Flughafens werden dessen stärkste veröffentlichte Beziehungen aus AVIA_GOR_DE dargestellt.

Die Karte wird nicht als NUTS-3-Flächenkarte umgesetzt. Ein Flughafen ist ein Verkehrsknoten; sein Umschlag darf nicht ohne weitere Annahmen als Güterverkehrsmenge des umgebenden Kreises interpretiert werden.

Für die Standortkoordinaten gilt folgende Quellenhierarchie:

1. **GISCO als Hauptquelle:** Das amtliche Punktnetz [**GISCO Airports 2024**](https://ec.europa.eu/eurostat/en/web/gisco/geodata/transport-networks) von Eurostat wird für alle passenden ICAO-Codes verwendet, nicht nur für deutsche und europäische Flughäfen. Es passt institutionell zur Verkehrsquelle und wird über den vierstelligen ICAO-Code mit `rep_airp` beziehungsweise den Teilen von `airp_pr` verknüpft.
2. **OurAirports als Ergänzungsquelle:** Die weltweite, gemeinfreie Datei `airports.csv` von [**OurAirports**](https://ourairports.com/data/) ergänzt ausschließlich Codes, die in GISCO fehlen. Die jeweilige Koordinatenquelle wird in der Flughafenstammtabelle festgehalten. Sichtbare Ergänzungen aus OurAirports werden wegen des offenen Gemeinschaftscharakters der Quelle stichprobenartig gegen eine offizielle Flughafen- oder Luftfahrtquelle geprüft.
3. **Nicht eindeutig zuordenbare Codes:** bleiben in der Relationstabelle sichtbar, werden aber mit **„ohne Kartenpunkt“** gekennzeichnet. Es werden keine Koordinaten aus Ortsnamen geschätzt.

Die am 3. September 2026 durchgeführte Bestandsprüfung ergab 281 unterschiedliche ICAO-Codes in den relevanten Flughafen- und Relationsdaten ab 2016. GISCO deckt davon 279 ab; `CYYC` und `EKCH` werden durch OurAirports ergänzt. Die kombinierte Abdeckung beträgt für den derzeitigen Bestand 281 von 281 Codes. Dieser Befund wird bei jeder Datenaktualisierung neu geprüft. Originaldateien, Abrufstände, Prüfsummen und Aktualisierungsablauf sind in [`README_FLUGHAFENSTANDORTE.md`](../../data/raw/Luftverkehr/Flughafenstandorte/README_FLUGHAFENSTANDORTE.md) dokumentiert.

Die später erzeugte Flughafenstammtabelle speichert je Standort ICAO-Code, Anzeigename, Staat, Längen- und Breitengrad, Koordinatenquelle und Stand der Quelle. Historische oder geschlossene Flughäfen werden nicht allein aufgrund eines aktuellen Geodatensatzes entfernt, wenn sie für frühere Berichtsjahre in den Eurostat-Daten benötigt werden.

### 5.3 Top-10-Relationen

Die Relationstabelle zeigt die zehn stärksten veröffentlichten Partnerflughäfen der aktuellen Auswahl. Sie reagiert auf Jahr und Richtung. Gesamt, Versand und Empfang werden aus den jeweils passenden Messgrößen der Relationsquelle abgeleitet.

Die Eurostat-Begriffe werden nicht inhaltlich umgedeutet, sondern für die konsistente Bedienlogik des Dashboards transparent übersetzt:

- **Versand (am ausgewählten Flughafen geladen):** `FRM_LD`,
- **Empfang (am ausgewählten Flughafen entladen):** `FRM_NLD`,
- **Gesamt (geladen und entladen):** `FRM_LD_NLD`.

Für eine Relation bedeutet Versand eine am ausgewählten deutschen Flughafen geladene Menge mit dem Partnerflughafen als nächstem gemeldeten Ziel; Empfang bedeutet eine am ausgewählten Flughafen entladene Menge vom gemeldeten Partnerflughafen. Die Begriffe bezeichnen damit die Flughafenperspektive und nicht zwingend den ursprünglichen Versandort oder endgültigen Empfangsort der Sendung. In Überschrift, Filterhilfe und Methodentext werden die amtlichen Begriffe in Klammern mitgeführt, damit die Übersetzung überprüfbar bleibt.

Der Informationstext aus Abschnitt 4.1 steht unmittelbar an der Tabelle. Die Tabelle wird nicht als vollständige Rangfolge aller tatsächlichen Beziehungen bezeichnet.

### 5.4 Diagrammfläche: Status quo und Dynamik

In der rechten unteren Diagrammfläche wird – entsprechend der Logik anderer Analysebereiche – ein Umschalter **Status quo / Dynamik** vorgesehen.

- **Status quo:** Rangfolge der deutschen Flughäfen nach Fracht- und Postaufkommen im ausgewählten Jahr. Grundlage ist AVIA_GOOA.
- **Dynamik:** Entwicklung der führenden Flughäfen über die verfügbaren Jahre. Die im ausgewählten Jahr führenden Standorte werden als Linien gezeigt; der aktuell ausgewählte Flughafen wird visuell hervorgehoben.

Die Zahl gleichzeitig dargestellter Linien wird begrenzt, damit Unterschiede und Rangverschiebungen lesbar bleiben. Weitere Flughäfen können über die Flughafenwahl gezielt betrachtet werden.

## 6. Filter- und Bedienlogik

Folgende Steuerungen sind fachlich vorgesehen:

- **Jahr:** zentrale Jahresauswahl, begrenzt auf die für das Modul verfügbaren Jahre,
- **Richtung:** Gesamt, Versand (geladen) und Empfang (entladen),
- **Flughafen:** eigene Auswahl innerhalb des Moduls oder Auswahl direkt über die Karte,
- **Kennzahl:** Fracht und Post in Tonnen sowie Fracht- und Postflüge in Anzahl.

Der Kennzahlenschalter wird ähnlich wie im Mautdatenmodul angeordnet, aber fachlich eindeutig beschriftet:

- **Fracht und Post (t):** primäre Kennzahl für Aufkommen, Rangfolge, Dynamik und Relationen;
- **Fracht- und Postflüge (Anzahl):** ergänzende Betriebskennzahl auf Basis von `CAF_FRM`.

Die Flugzahl darf nicht als Menge von Gütern bezeichnet werden. Außerdem ist sie kein Maß für die durchschnittliche Auslastung: Die [Eurostat-Metadaten](https://ec.europa.eu/eurostat/cache/metadata/en/avia_pa_esms.htm) führen `CAF_FRM` als „Freight and mail commercial air flights“, während die Tonnage nach dem Konzept der geladenen und entladenen Fracht und Post abgegrenzt wird. Vor der Umsetzung wird anhand der Eurostat-Metadaten und ausgewählter Flughäfen abschließend dokumentiert, welche Passagierflüge mit Beiladefracht in der Flugzahl enthalten sind. Bis zu dieser Prüfung bleibt die Tonnage die voreingestellte und fachlich führende Kennzahl; eine Division Tonnen je Flug wird nicht angeboten.

Die regionale NUTS-Auswahl, NST-2007-Gütergruppen und Tonnenkilometer sind für das Luftfrachtmodul nicht anwendbar. Nicht passende globale Filter werden im Modul klar als nicht verfügbar gekennzeichnet oder ausgeblendet, ohne ihre Werte für andere Module zu verändern.

## 7. Neustrukturierung der Desktop-Navigation

Mit dem Luftfrachtmodul umfasst die Navigation neun fachlich unterschiedliche Bereiche. Zur besseren Orientierung werden sichtbare Gruppenüberschriften und zusätzliche Abstände eingeführt. Auf- und zuklappbare Untermenüs sind bei diesem Umfang zunächst nicht erforderlich.

Vorgesehene Gliederung:

### Einstieg

- Übersicht

### Verkehrsträger und Knoten

- Straßengüterverkehr
- Schienengüterverkehr
- Binnenschifffahrt
- Seeverkehr & Häfen
- Luftfracht & Flughäfen

### Vertiefungen

- Mautdaten
- Intermodaler Verkehr & KV

### Zukunft

- Verkehrsprognose 2040

Die Verkehrsprognose erhält eine eigene Gruppe **Zukunft**. Sie ist keine bloße fachliche Vertiefung der Ist-Daten, sondern beruht auf einer eigenständigen modellbasierten Datengrundlage und beantwortet eine andere zeitliche Fragestellung. Die eigene Gruppe macht diesen Perspektivwechsel sichtbar, ohne die Navigation durch eine weitere Hierarchieebene zu verkomplizieren.

## 8. Mobile Navigation

Auf kleinen Bildschirmen wird die bisherige lange horizontale Modulleiste perspektivisch durch einen kompakten Button beziehungsweise Modulwahlschalter ersetzt.

Der geschlossene Schalter zeigt:

- das Symbol des aktuell gewählten Moduls,
- dessen festgelegte Akzentfarbe,
- die vollständige Modulbezeichnung,
- einen eindeutigen Hinweis zum Öffnen der Auswahl.

Nach dem Öffnen erscheint eine gruppierte Modulliste entsprechend der Desktop-Struktur. Symbole und Akzentfarben bleiben in der Liste erhalten. Das aktuell aktive Modul wird zusätzlich durch Hintergrund, Textkennzeichnung oder Häkchen markiert, sodass die Orientierung nicht allein von der Farbe abhängt.

Die mobile Auswahl muss per Berührung und Tastatur bedienbar sein. Nach einer Auswahl schließt sie sich und setzt den Fokus nachvollziehbar auf den Modulwahlschalter beziehungsweise den Beginn des neu geöffneten Moduls zurück.

## 9. Farb- und Symbolsystem

Das Luftfrachtmodul erhält ein eigenes Flugzeug- beziehungsweise Luftfracht-Symbol und eine feste Akzentfarbe, die sich ausreichend von Schiene, Binnenschifffahrt, Seeverkehr und Prognose unterscheidet. Die Farbe wird konsistent in Navigation, Kennzahlen, Karte, Diagrammen und aktiven Zuständen verwendet.

Symbole und Farben bleiben auf Desktop und Mobilgeräten erhalten. Bezeichnungen, aktive Zustände und gegebenenfalls Muster oder Linienformen stellen sicher, dass Informationen nicht ausschließlich über Farbe vermittelt werden.

## 10. Technische Umsetzung

Das Luftfrachtmodul wird entsprechend der bestehenden Modulstruktur getrennt aufgebaut:

- eigenes HTML-Modul,
- eigenes JavaScript-Modul,
- eigene Vorverarbeitung der Eurostat-Daten,
- kompakte Webdatei für nationale Werte, Flughafenwerte und ausgewählte Relationen,
- verzögertes Laden der Fachdaten erst beim Öffnen des Moduls.

Die rund 47 MB große Rohdatei AVIA_GOR_DE wird nicht direkt im Browser verarbeitet. Die Vorverarbeitung beschränkt die Webdaten auf benötigte Jahre, Messgrößen, deutsche Berichtsflughäfen und veröffentlichte Relationen. Quelltabellen, Messkonzepte und Aktualisierungszeitpunkte bleiben in den Metadaten der Ausgabedatei dokumentiert.

### 10.1 Verbindliche Synchronisierung von Daten, „Quellen“ und „Hinweise“

Neue Quellen oder Funktionen gelten erst dann als vollständig integriert, wenn Datenmetadaten, sichtbare Quellenangaben und Nutzungshinweise gemeinsam aktualisiert und geprüft wurden. Für das Luftfrachtmodul gilt folgender Ablauf:

1. **Daten und Metadaten:** Rohquelle, Tabelle, Messgröße, räumliche Ebene, verfügbare Jahre, Abrufdatum, Lizenz-/Nachnutzungshinweis und Verarbeitungsschritt im Datenkatalog und in den Metadaten der Webdatei ergänzen.
2. **Bereich „Quellen“:** In `html/shell-tail.html` im Dialog „Quellen, Bearbeitungsstand & Rechtliches“ einen eigenen Eintrag für Luftfracht ergänzen. Er nennt AVIA_GOOC, AVIA_GOOA und AVIA_GOR_DE einschließlich ihrer Rollen sowie GISCO und den ergänzenden OurAirports-Bestand für die Flughafenstandorte. Daten- und Abrufstände werden getrennt angegeben.
3. **Bereich „Hinweise“:** Im Dialog „Nutzungshinweise zum Dashboard“ das neue Modul in „Was Sie auswerten können“ aufnehmen. Unter „Datenstand und Vergleichbarkeit“ werden die getrennten Verfügbarkeiten für nationale Werte, Flughäfen und Relationen dynamisch aus den Metadaten ausgegeben. Zusätzlich wird erläutert, dass bei einem Jahr ohne Relationsdaten keine älteren Relationen automatisch eingeblendet werden.
4. **Funktionshinweise:** Neue Filter, Kennzahlen oder Interaktionen werden gleichzeitig in den Nutzungshinweisen ergänzt, sofern ihre Bedeutung nicht unmittelbar aus der Oberfläche hervorgeht. Für Luftfracht sind mindestens Richtung, Kennzahl, Status quo/Dynamik und der Leerzustand der Relationen zu erläutern.
5. **Generierte Oberfläche:** Änderungen erfolgen in den bearbeitbaren Quellen unter `html/`, `css/source/`, `js/source/` und `js/modules/`. Danach wird das Frontend mit `python scripts/frontend/build_frontend.py all` neu erzeugt; die generierten Dateien werden nicht direkt bearbeitet.
6. **Qualitätssicherung:** Datenkatalog, sichtbare Quellen, Hinweise, Komponentenüberschriften und tatsächliche Datenstände werden gegeneinander geprüft. Der Qualitätssicherungsplan und – soweit der reale Betriebsablauf betroffen ist – die Anleitung zur Datenaktualisierung werden nachgeführt.

Vorgesehene Kurzfassung im Bereich **„Quellen“**:

> **Luftfracht und Flughäfen:** Eurostat AVIA_GOOC (Deutschland), AVIA_GOOA (Flughäfen) und AVIA_GOR_DE (veröffentlichte Flughafenrelationen), Auswertung ab 2016. Flughafenstandorte: Eurostat/GISCO Airports 2024; fehlende ICAO-Codes ergänzend aus OurAirports. Die konkreten letzten Datenjahre werden je Datenebene ausgewiesen.

Vorgesehene Kurzfassung im Bereich **„Hinweise“**:

> **Luftfracht & Flughäfen:** Nationale Entwicklung, Flughafenrangfolge und veröffentlichte Top-Relationen können getrennt ausgewertet werden. Liegen für das gewählte Jahr keine Relationsdaten vor, werden keine älteren Relationen automatisch eingesetzt. Der Hinweis an der Relationstabelle nennt das letzte verfügbare Relationsjahr und verweist auf die Jahresauswahl.

Die sichtbaren Quellenangaben werden **erst mit der tatsächlichen Freischaltung des Moduls** ergänzt. Eine vorzeitige Aufnahme würde fälschlich den Eindruck erwecken, die neuen Quellen würden bereits im aktuellen Dashboard verwendet.

## 11. Vorgesehene Umsetzungsschritte

### Schritt 1 – Quellenbasis vervollständigen

- die vorhandenen Dateien AVIA_GOOC, AVIA_GOOA und AVIA_GOR_DE als Eingangsquellen registrieren,
- Codes und Messgrößen dokumentieren,
- verfügbare Jahre, tatsächlich befüllte Reihen und Aktualisierungsstände getrennt prüfen,
- die bereits abgelegten Standortquellen GISCO Airports 2024 und OurAirports gemäß der Quellenbeschreibung registrieren,
- Flughafenbezeichnungen und Koordinaten über ICAO-Codes belastbar zuordnen und die Abdeckung bei jeder Aktualisierung neu prüfen.

### Schritt 2 – Fachliche Vorverarbeitung

- nationale Zeitreihe aus AVIA_GOOC aufbauen,
- Flughafenrangfolge und Zeitreihen aus AVIA_GOOA aufbauen,
- veröffentlichte Beziehungen aus AVIA_GOR_DE ableiten,
- getrennte Listen der tatsächlich verfügbaren Jahre sowie letzte verfügbare Jahre für jede Datenebene erzeugen,
- die Auswertung ab 2016 aufbauen,
- Summen-, Richtungs-, Datenstands- und Schwellenlogik automatisiert prüfen.

### Schritt 3 – Modul und Navigation umsetzen

- Luftfrachtmodul mit Karte, Kennzahlen, Relationstabelle und Diagramm erstellen,
- Desktop-Navigation gruppieren,
- mobile Modulwahl mit Symbolen und Farben einführen,
- für Jahre ohne Relationsdaten den dynamischen Leerzustand mit Verweis auf das letzte verfügbare Relationsjahr umsetzen,
- nicht anwendbare globale Filter eindeutig behandeln,
- die Dialoge „Quellen“ und „Hinweise“ sowie Datenkatalog und Dokumentation synchron ergänzen.

### Schritt 4 – Qualitätssicherung

- nationale Werte gegen AVIA_GOOC prüfen,
- Flughafenwerte gegen AVIA_GOOA prüfen,
- Relationswerte stichprobenartig gegen AVIA_GOR_DE prüfen,
- für die Auswahl 2025 prüfen, dass Deutschland- und Flughafenwerte 2025 zeigen, während Relationslinien und -tabelle leer bleiben und auf 2024 verweisen,
- Zuordnung geladen/Versand und entladen/Empfang in beiden Richtungen kontrollieren,
- ICAO-Verknüpfung und Koordinatenabdeckung aller sichtbaren Top-Relationen prüfen,
- Hinweise zu Veröffentlichungsschwellen und Datenlücken kontrollieren,
- Status- und Dynamikdarstellung auf Lesbarkeit prüfen,
- Desktop- und Mobilnavigation mit Maus, Tastatur und Berührung testen,
- Ladezeit und Größe der erzeugten Webdatei dokumentieren.

## 12. Noch zu treffende Detailentscheidungen

1. Welche Akzentfarbe wird für Luftfracht festgelegt?
2. Welche Zahl von Flughäfen wird in der Statusansicht standardmäßig gezeigt?
3. Welche Flughäfen erscheinen gleichzeitig in der Dynamikansicht?
4. Soll die Flughafenwahl dauerhaft im Modul sichtbar sein oder erst nach Auswahl auf der Karte erscheinen?
5. Soll die ergänzende Flugzahl bereits in der ersten Ausbaustufe angeboten werden oder erst nach der vertieften Prüfung ihrer Abgrenzung?

## 13. Unmittelbar nächster Arbeitsschritt

Als nächster Schritt wird die fachliche Vorverarbeitung für den Zeitraum ab 2016 spezifiziert und anschließend umgesetzt. Dabei entstehen getrennte Jahresverfügbarkeiten für nationale Werte, Flughafensummen und Relationen sowie eine ICAO-basierte Flughafenstammtabelle mit dokumentierter Koordinatenquelle. Vor der Freischaltung des Moduls werden der dynamische Relations-Leerzustand und die synchrone Aktualisierung von „Quellen“ und „Hinweise“ in die Qualitätssicherung aufgenommen.
