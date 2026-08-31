# Technisches Handbuch & Systemdokumentation: Güterströme Deutschland

## 1. Projektübersicht & Fachkonzept

Das **WBP Güterströme-Dashboard** ist eine interaktive, webbasierte Business-Intelligence- und Geodaten-Anwendung zur Visualisierung und multimodalen Analyse der Güterverkehrsströme in Deutschland.

### Fachlicher Erfassungsbereich
* **Räumliche Ebene**: Deutsche Landkreise und kreisfreie Städte auf NUTS-3-Ebene sowie aggregierte Bundes- und Auslandsverflechtungen. Die VP2040 verwendet für ihr Basisjahr 2019 einen NUTS-2016-bezogenen Verkehrs-zellenstand mit 401 deutschen Flächenzellen und zusätzlichen Hafen-, Flughafen- und Inselzellen.
* **Verkehrsträger**: 
  1. Straßengüterverkehr (KBA / Eurostat)
  2. Schienengüterverkehr (Destatis EVAS 46131)
  3. Binnenschifffahrt (Destatis EVAS 46321)
  4. Seeverkehr (Destatis EVAS 46331)
  5. Kombinierter / Intermodaler Verkehr (SGKV / Destatis)
  6. Bundesverkehrsprognose 2040 (BMDV / Intraplan / Trimode)
* **Zeithorizonte**:
  * **Ist-Daten (fachlicher Bestand)**: 2010 – 2025 (16 Kalenderjahre); die vergleichbare, im Dashboard auswählbare multimodale Ansicht reicht derzeit von 2016 bis 2024.
  * **Prognose-Daten**: Basisjahr 2019 vs. Prognosehorizont 2040 (Basisfall P1)
* **Güterklassifikation**: Amtliche Systematik **NST-2007** (7 Hauptgruppen und 20 Abteilungen).

---

### 1.1 Aktuelle Analyse-Module

| Modul | Zweck und zentrale Funktionen | Datenquellen / räumliche Ebene |
|---|---|---|
| **Übersicht** | Vergleich der drei landseitigen Verkehrsträger, Karte regionaler Kennwerte, Top-Relationen, Modal Split und Güterstruktur für eine ausgewählte Region. | KBA, Destatis; überwiegend NUTS-3, im Ausland abhängig von der Quelle. |
| **Straßengüterverkehr** | Regionale Straßenverkehrskennwerte, Versand-/Empfangsbeziehungen und Güterstruktur nach sieben NST-2007-Hauptgruppen. | KBA VE 7, VE 12/VE 13, VD 2 und VD 3c; NUTS-3 bzw. NUTS-2 nach Tabelle. |
| **Schienengüterverkehr** | Regionale Kennwerte, Quell- und Zielrelationen sowie Güterstruktur des Eisenbahnverkehrs. | Destatis EVAS 46131; Inland NUTS-3, Ausland NUTS-2. |
| **Binnenschifffahrt** | Hafen- und regionale Kennwerte, Relationen und Güterstruktur. | Destatis EVAS 46321; Hafen- und NUTS-Ebenen. |
| **Seeverkehr & Häfen** | Profile deutscher Seehäfen mit Empfang, Versand, Güterstruktur und internationalen Partnerbeziehungen. | Destatis EVAS 46331; deutsche Häfen und internationale Partner. |
| **Intermodaler Verkehr & KV** | Getrennte Betrachtung der abgrenzbaren KV-Teilbereiche auf Schiene und Binnenschiff, einschließlich Ladeeinheiten bzw. Containergrößen und inländischer Relationen. | Destatis EVAS 46131 und 46321. Die Teilmärkte werden nicht zu einer Gesamtsumme addiert. |
| **Verkehrsprognose 2040** | Karten- und Relationsanalyse der Bundesverkehrsprognose für den Prognosefall 2040 (P1). | Bundesverkehrsprognose 2040; Verkehrszellen und NUTS-3-Bezüge. |

Die Quellen, Zeitbezüge, räumlichen Ebenen und Kennzahlen sind im maschinenlesbaren Katalog `data_catalog.json` detailliert dokumentiert. Die Module verwenden nur Daten, deren räumliche und fachliche Abgrenzung zur jeweils dargestellten Kennzahl passt; ein unmittelbarer Vergleich verschieden abgegrenzter Quellen ist entsprechend kenntlich zu machen.

### 1.2 Vorgemerktes Erweiterungsmodul: Mautdaten-Relationen

**Status:** fachlich und technisch vorgeprüft, noch nicht in die Anwendung integriert.

Das Modul soll eine ergänzende, gemeindebezogene Monatsanalyse auf Basis des Lkw-Maut-Portals von Toll Collect / BALM ermöglichen. Es ist bewusst von den bestehenden, jahresbezogenen NUTS-3-Analysen getrennt zu halten: Die Daten beschreiben Mautfahrten auf dem mautpflichtigen Netz, nicht den vollständigen Straßengüterverkehr und auch keine Gütermengen.

**Vorgesehene Nutzung:**

1. Auswahl einer Gemeinde auf der Karte sowie eines Berichtsmonats.
2. Wahl der Perspektive: ausgehende Verbindungen (`ags_start`, `richtung = 0`) oder eingehende Verbindungen (`ags_ziel`, `richtung = 1`).
3. Anzeige der Gegenkommunen als Rangtabelle und, sofern geeignete Gemeinde-Zentroide bereitstehen, als Relationendarstellung auf der Karte.
4. Ausweisung von Top-Relationen und Monatskennwerten, insbesondere `anzahl_befahrungen`, Fahrleistung sowie Distanz- und Fahrzeitkennwerten.
5. Optionale Zeitreihe für die ausgewählte Gemeinde oder eine konkret gewählte Start-Ziel-Relation. Für die Zeitreihe sind die Monatsabfragen einzeln auszuführen und die Ergebnisse nachvollziehbar zu aggregieren.

**Bekannte Daten- und API-Grenzen:**

* Die API verlangt zwingend eine Gemeinde als Start oder Ziel zusammen mit der Richtung. Eine bundesweite Komplettabfrage aller Gemeinde-zu-Gemeinde-Relationen ist nicht zulässig.
* Testabfragen für Berlin bestätigen Daten für Juni und Dezember 2025; für Mai 2025 wurden keine Berliner ausgehenden Relationen geliefert. Der in der Portalanwendung sichtbare Beginn ab Juni 2025 ist vor einer Produktivschaltung noch einmal quellenbezogen zu prüfen.
* Der Downloadbereich des Portals stellt nach bisherigem Kenntnisstand nur den aktuellsten Monatsbestand als CSV bereit. Historische bundesweite Monatsbestände wären daher nicht automatisch als vollständiges Archiv verfügbar.
* `anzahl_befahrungen` kann für einen definierten Zeitraum summiert werden. Distanz- und Zeitkennwerte sind Verteilungs- bzw. Lagekennwerte und dürfen nicht über Monate addiert werden; bei einer Zeitraumauswertung wären sie getrennt monatlich oder als fachlich begründete gewichtete Kennwerte auszuweisen.
* Vor einer Umsetzung sind Ergebnislimits, Seitennavigation, zulässige Abruffrequenz, CORS bzw. eine sichere Serveranbindung und die Lizenzangabe produktiv zu prüfen. Eine lokale Abschaltung der Zertifikatsprüfung ist ausschließlich ein Diagnoseschritt und keine zulässige Produktionslösung.

---

## 2. Systemarchitektur & Technologie-Stack

Die Anwendung ist als performante **Client-Side Single-Page Application (SPA)** ohne Backend-Laufzeitabhängigkeit konzipiert. Alle Daten werden in optimierten JSON-Datenbündeln vorgehalten und im Browser per JavaScript in Echtzeit aggregiert, gefiltert und visualisiert.

```mermaid
graph TD
    subgraph ETL_Data_Pipeline [Data Pipelines - Python]
        RAW[Rohdaten: Destatis, KBA, GISCO, VP2040] --> P1[build_web_data_bundle_v5.py]
        RAW --> P2[pipeline_vp2040.py]
        P1 --> JSON1[(web_summary_by_region.json / web_choropleth.json / relations/*.json)]
        P1 --> JSON2[(nuts3_de_2016/2021/2024.geojson)]
        P2 --> JSON3[(data/processed/web_forecast_2040.json)]
    end

    subgraph Frontend_Application [Web Application]
        JSON1 & JSON2 & JSON3 --> APP[js/app.js - State Engine & Renderers]
        CSS[css/style.css - WBP Design System] --> UI[index.html - 7 Analyse-Module]
        APP --> UI
        APP --> MAPS[Leaflet.js - Choropleth & Spider Maps]
        APP --> CHARTS[Chart.js - Modal Split & NST-7 Charts]
    end
```

### Frontend-Kerntechnologien:
* **HTML5**: Semantische Struktur mit responsivem Container-Layout.
* **Vanilla CSS3**: Modernes WBP-Designsystem mit zentralen Fachfarben, CSS Grid & Flexbox sowie Mobil-Breakpoints.
* **Vanilla JavaScript (ES6+)**: Zentrales reaktives `state`-Objekt, Geometrieverarbeitung und DOM-Aktualisierung.
* **Leaflet.js (v1.9.4)**: Karten-Rendering (Choroplethen, interaktive Tooltips, gerade O-D-Verbindungslinien, Legenden).
* **Chart.js (v4.4.1)**: Donut-Diagramme (Modal Split), horizontale/vertikale Balkendiagramme (Güterstrukturen, KV-Ladeeinheiten, Zeitreihen).

---

## 3. Dateistruktur & Speicherorte

```
Güterströme/
│
├── index.html                           # Hauptanwendung (7 Analyse-Module)
├── DATA_STRUCTURE_AND_CONCEPT.md        # Fachkonzept & Metadatenübersicht
├── HANDBUCH_SYSTEMDOKUMENTATION.md      # Diese Dokumentation
├── data_catalog.json                    # Maschinenlesbarer Datenkatalog
├── schema_mysql_postgres.sql            # SQL-Schema für relationale Datenbank-Backends
│
├── css/
│   └── style.css                        # Komplettes UI-Designsystem & Responsive Styles
│
├── js/
│   └── app.js                           # Vollständige Client-Logik, Map- & Chart-Renderer
│
├── data/
│   ├── raw/                             # Amtliche Rohdaten (CSV, Excel, GeoPackages)
│   │   ├── binnenschiff/                # Destatis EVAS 46321
│   │   ├── seeverkehr/                  # Destatis EVAS 46331
│   │   ├── schiene/                     # Destatis EVAS 46131
│   │   ├── strasse/                     # KBA VE7, VE12, VE13, VD2, VD3c
│   │   ├── vp2040/                      # VP 2040 Rohmatrizen & Zentroide
│   │   └── geodaten/                    # Eurostat GISCO NUTS Grenzpolygone
│   │
│   ├── crosswalks/                      # NUTS-Konkordanzen & Gebietsstandsänderungen
│   │   ├── nuts_mapping_2016_2024.csv
│   │   └── vz_nuts3_vp2040_mapping.csv
│   │
│   └── processed/                       # Bereinigte, optimierte Web-JSON-Dateien
│       ├── web_summary_by_region.json   # Ist-Daten: regionale Summaries und Güterwürfel
│       ├── web_choropleth.json          # Vorberechnete Kartenwerte
│       ├── relations/                   # Regionsweise partitionierte O-D-Relationen
│       ├── web_forecast_2040.json       # Prognose-Daten 2040: Mehrdimensionaler Daten-Würfel
│       ├── nuts3_de_2016/2021/2024.geojson # NUTS-Geometrien je Gebietsstand
│       ├── nuts_centroids_full.json     # Zentroide für Kreis- und Spinnennetz-Darstellung
│       ├── web_maritime.json            # Seeverkehrskennzahlen und Hafenbeziehungen
│       └── web_intermodal.json          # Zeitreihe, Teilmarktstrukturen und Inlandrelationen für intermodale Verkehre
│
├── build_web_data_bundle_v5.py          # Python ETL-Pipeline für Ist-Daten
├── build_maritime_port_profiles.py       # Hafen-, Güter- und Partnerprofile aus EVAS 46331
├── build_intermodal_data.py              # reproduzierbare Auswertung der KV-Teilmarktzeitreihe
└── pipeline_vp2040.py                   # Python ETL-Pipeline für Verkehrsprognose 2040
```

---

## 4. Daten-Pipelines & ETL-Prozesse

Die vollständige, releasefähige Zuordnung von Rohdaten, Berechnungsschritten,
Ausgabedateien und Prüfschritten steht in
[`ANLEITUNG_DATENAKTUALISIERUNG.md`](ANLEITUNG_DATENAKTUALISIERUNG.md). Dieses
Kapitel gibt die fachlich-technische Übersicht; die Anleitung ist für die
Durchführung eines neuen Datenupdates maßgeblich.

### 4.1 ETL für Ist-Daten (`build_web_data_bundle_v5.py`)
1. **Jahresscheiben mit amtlichem Gebietsstand**: Die Anwendung nutzt je Berichtsjahr die passende NUTS-Geometrie (2016, 2021 oder 2024). Sie erzeugt ausdrücklich keine künstlich harmonisierte Zeitreihe auf NUTS 2024.
2. **Taxonomie-Mapping**: Normalisierung auf die amtlichen sieben zusammengefassten NST-2007-Güterpositionen. Die 20 Abteilungen werden nur dort ausgegeben, wo der Quellbestand sie räumlich passend liefert; KBA VE12/VE13 ist auf NUTS-3 auf sieben Gruppen begrenzt.
3. **Bilaterale Verflechtungs-Matrizen**: Aggregation der Top-O-D-Beziehungen je Landkreis mit Ausweisung von Transportmenge (Tonnen), Verkehrsleistung (tkm), Verkehrsträgern und Modal Split.
4. **Export**: Generiert die getrennten Webartefakte `web_summary_by_region.json`, `web_choropleth.json`, `web_maritime.json`, `web_regions.json` sowie nach Regionen partitionierte O-D-Dateien unter `relations/`.

### 4.2 ETL für intermodale Verkehre und KV (`build_intermodal_data.py`)
1. **Quellen und Zeitraum:** Liest die jährlichen Destatis-Dateien EVAS 46131 (Schiene) und EVAS 46321 (Binnenschifffahrt) für 2016 bis 2025 ein und prüft die Monatsabdeckung.
2. **Fachliche Abgrenzung:** Schiene umfasst die ausgewiesenen Ladeeinheiten, Binnenschiff den Verkehr mit einer ausgewiesenen Containergrößenklasse. Die Ergebnisse werden nicht addiert.
3. **Relationen:** Ermittelt für beide Teilmärkte zusätzlich die inländischen NUTS-3-Relationen. Schiene wird über eine ausgewiesene Ladeeinheit ungleich „Keine“, Binnenschiff über eine ausgewiesene Containergrößenklasse abgegrenzt.
4. **Export:** Erzeugt `web_intermodal.json` mit Jahreswerten für Tonnen und Tonnenkilometer, Strukturen der Ladeeinheiten und Containergrößen sowie den getrennten Relationen für Karte und Rangtabelle. Der zentrale Top-Filter greift je Teilmarkt, damit beide Teilmärkte sichtbar bleiben.

### 4.3 Hafenprofile im Seeverkehr (`build_maritime_port_profiles.py`)
1. **Quelle und Zeitraum:** Liest die bereits im Projekt abgelegten jährlichen Destatis-Dateien EVAS 46331 für 2016 bis 2025.
2. **Abgrenzung:** Ergänzt die kartierten deutschen Seehäfen um Empfang, Versand, NST-2007-Güterstruktur und internationale Partnerländer. Die Partnerbeziehungen werden nur nach Auswahl eines Hafens gezeigt.
3. **Ausführung:** Nach einem vollständigen Neuaufbau von `web_maritime.json` dieses Skript ebenfalls ausführen, damit die hafenbezogenen Profile erhalten bleiben.

### 4.4 ETL für Verkehrsprognose 2040 (`pipeline_vp2040.py`)
1. **Multidimensionaler Aggregationswürfel**:
   * Vorberechnung sämtlicher Filterdimensionen je NUTS-3 Landkreis:
     * **Metrik**: Beförderungsmenge (`tonnes`) & Verkehrsleistung (`tkm`)
     * **Richtung**: `all` (Gesamt), `outbound` (Versand), `inbound` (Empfang), `balance` (Netto-Saldo), `binnen` (Binnenverkehr)
     * **Güterart**: Gesamt (`ALL`) sowie NST-2007 Gruppen `1` bis `7`
     * **Verkehrsträger**: Straße (`road`), Schiene (`rail`), Binnenschiff (`iww`)
     * **KV-Ladeeinheiten**: Behältertypen 1 bis 8 (20ft, 40ft, Wechselbehälter, Sattelauflieger, RoLa, Leerbehälter)
2. **Basisjahr-Vergleich und Modalstruktur**: Die originalen NUTS-3-Matrizen für das Basisjahr 2019 und die Basisprognose 2040 (P1) werden mit demselben Verfahren aggregiert. Nationale, regionale und relationsspezifische Veränderungen werden ausschließlich aus diesen beiden Matrizensätzen berechnet; bei einem Nullwert im Basisjahr wird kein Prozentwert ausgewiesen. Da jede Rohmatrix Gütergruppe und Verkehrsträger gleichzeitig führt, werden die drei Landverkehrsträger auch für jede der sieben NST-2007-Hauptgruppen getrennt ausgegeben.
3. **Export**: Generiert `web_forecast_2040.json` mit den auswählbaren Szenarien `2019_BASE` und `2040_P1`.

---

## 5. Visualisierungs- & Interaktionskonzept

### 5.1 Farbkonzept & Barrierefreiheit
* **Verkehrsträger-Kennfarben**:
  * Straße (Lkw): Amber / Orange (`#f59e0b`)
  * Schiene (Bahn): Royal Blue (`#2563eb`)
  * Binnenschiff: Teal (`#0f766e`)
  * Seeverkehr: Deep Indigo (`#4f46e5`)
  * Gesamt/Übersicht: Emerald Green (`#059669`)
* **Verkehrsprognose 2040**:
  * **Verbindungslinien (Spinnennetz)**: Distinktes Royal Violett (`#7c3aed`) mit weißen Endpunkten (`#ffffff`), um jede Verwechslung mit Straßenfarben auszuschließen.
  * **Choroplethen-Hintergrund**: Elegante, dezente Sky-Slate-Palette (`#f8fafc` bis `#2563eb`).
  * **Verkehrssaldo (Divergierend)**: Sanfte Pastelltöne (Grün `#f0fdf4`–`#22c55e` für Versandüberschuss; Blau `#f0f9ff`–`#38bdf8` für Empfangsüberschuss).
* **KPI-Karten**: Jede Modulübersicht besitzt einen farbigen oberen Akzent. In den fachlich gemischten Prognose-KPIs entspricht er jeweils dem Verkehrsträger; sonst folgt er der Modulfarbe.

### 5.2 Interaktivität & Reaktivität
1. **Zentraler State Manager**: Jede Filteränderung (Region, Jahr, Szenario, Metrik, Richtung, Güterart, Top-X, Binnenverkehr) triggert eine synchrone Aktualisierung von:
   * 4 KPI-Karten (Hauptkore, Verkehrsträger-Volumen, Vorjahres-/Prognose-Trend)
   * Leaflet-Choroplethenkarte & Legende
   * O-D Spinnennetz-Linien (Spider Lines)
   * Verflechtungstabelle mit relationalen Badges
   * Modal-Split-Donut und Güterstruktur-/KV-Balkendiagrammen
2. **Kreuz-Interaktivität**:
   * Mausklick auf einen Landkreis setzt diesen als aktiven Regionsfilter.
   * Hover auf eine Tabellenzeile hebt die zugehörige Verbindungslinie und den Zielpunkt auf der Karte visuell hervor (`setHighlight`).
   * Detailreiche Tooltips zeigen exakte Mengengerüste, Verkehrsbilanzen, Modal Split und KV-Anteile kontextsensitiv an.
3. **Modale Steckbriefe**: Button "Regions-Steckbrief öffnen" generiert eine druck- und exportoptimierte Gesamtanalyse des aktiven Kreises.

---

## 6. Gültigkeit & Qualitätsprüfung

* **Syntax & Linting**: Alle JavaScript-Dateien wurden mit Node.js (`node -c js/app.js`) fehlerfrei validiert (Exit Code 0).
* **Code-Integrität**: Keine externen Framework-Build-Schritte nötig; sofortige Ausführbarkeit in jedem modernen Standard-Webbrowser über lokalen Webserver oder statisches Hosting.
