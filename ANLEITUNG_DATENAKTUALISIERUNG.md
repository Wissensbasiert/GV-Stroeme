# Datenaktualisierung und Reproduktion des Güterströme-Dashboards

Stand: 24.08.2026  
Zweck dieses Dokuments: Es beschreibt verbindlich, welche Rohdaten in die aktive Anwendung eingehen, wie sie verarbeitet werden und welche Prüfungen vor einer Übernahme eines neuen Datenstands erforderlich sind. Es ist die Arbeitsanleitung für künftige Datenreleases; die Skripte und die Rohdaten bleiben dabei die technische Referenz.

## 1. Grundregeln für jedes Datenrelease

1. **Rohdaten unverändert ablegen.** Neue Originaldateien werden zusätzlich in den jeweils benannten Ordner kopiert. Bestehende Jahrgänge, Szenarien und die Datensatzbeschreibung werden nicht überschrieben oder umbenannt.
2. **Vor jedem Neuaufbau sichern.** Die aktuell ausgelieferten Dateien aus `data/processed/` werden in einen eindeutig datierten Unterordner von `backups/` kopiert, zum Beispiel `backups/before-data-update-YYYYMMDD/`.
3. **Schema zuerst prüfen.** Vor der Verarbeitung sind Dateiname, Zeichencodierung, Trennzeichen, Spaltennamen, Jahrgang, räumliche Ebene und fachliche Abgrenzung mit dem bisherigen Release zu vergleichen. Ein gleiches Dateiformat bedeutet nicht automatisch einen vergleichbaren Inhalt.
4. **Nur die betroffene Pipeline ausführen.** Ein neues VP2040-Szenario aktualisiert nicht automatisch die Ist-Daten; ein neues Destatis-Jahresrelease aktualisiert nicht die VP2040. Die Zuordnung steht in Abschnitt 3.
5. **Ergebnis gegen die Rohdaten prüfen.** Nach jedem Aufbau sind mindestens nationale Summen, ein Verkehrsträger, drei Regionen und – soweit vorhanden – eine Relation nachzurechnen. Für VP2040 existiert dafür ein eigenes Prüfsystem.
6. **Erst nach erfolgreicher Prüfung übernehmen.** Fehlerhafte oder nicht nachvollziehbare Ergebnisse werden nicht durch manuelle Werte im Dashboard ersetzt.

Alle Web-JSON-Dateien werden UTF-8-kodiert geschrieben. Umlaute und Sonderzeichen dürfen weder in Rohdaten noch in Dokumentation oder Ausgaben durch Ersatzschreibweisen ersetzt werden.

## 2. Welche Quellen aktuell wofür verwendet werden

| Fachbereich | Rohdatenordner und Muster | Aktive Verarbeitung | Ergebnis im Dashboard |
| --- | --- | --- | --- |
| Straßengüterverkehr | `data/raw/Straße/KBA/`; VE12 und VE13 für regionale Kennzahlen, VE7 für O-D-Relationen | `pipeline_phase2_aggregations.py` und `build_web_data_bundle_v5.py` | regionale Ist-Werte, Güterstruktur, Versand/Empfang, Modal Split und Straßenrelationen |
| Schienengüterverkehr | `data/raw/SGV OpenData/eb_opendata_YYYY.csv` | `build_web_data_bundle_v5.py` und `build_intermodal_data.py` | regionale Ist-Werte sowie getrennte KV-Teilmarktanalyse Schiene |
| Binnenschifffahrt | `data/raw/IWW OpenData/IWW_OpenData_YYYY.csv` | `build_web_data_bundle_v5.py` und `build_intermodal_data.py` | regionale Ist-Werte sowie getrennte KV-Teilmarktanalyse Binnenschiff |
| Seeverkehr | `data/raw/MRTM OpenData/MRTM_OpenData_YYYY.csv` | `build_web_data_bundle_v5.py`, danach `build_maritime_port_profiles.py` | Seeverkehr, deutsche Seehäfen, Empfang/Versand, Güter und Partner |
| Verkehrsprognose 2040 | `data/raw/VP2040/VP2040_2019_GV_NUTS3/` und `data/raw/VP2040/VP2040_2040P1BP_GV_NUTS3/` | `pipeline_vp2040.py` | Szenarien 2019 und 2040 P1, Karten, Regionalwerte, Relationen und Veränderung |
| Räumliche und fachliche Umstiegsschlüssel | `data/crosswalks/crosswalk_spatial_vp2040.json`, `data/crosswalks/vp2040_special_cells_nuts3.json` und `data/crosswalks/crosswalk_nst_vp2040.json` | von `pipeline_vp2040.py` und der VP2040-Prüfung gelesen | NUTS-3-Zuordnung einschließlich Sonderzellen sowie Gütergruppen-Umstieg |

Die Mautdaten und die VP2040-Dateien zu Seeverkehr, Luftfracht und intermodalen Transportketten liegen zwar im Projekt, werden jedoch **nicht** in die derzeit ausgelieferte VP2040-Analyse eingerechnet. Ihre spätere Verwendung setzt eine eigene fachliche Entscheidung und dokumentierte Erweiterung voraus.

## 3. Ausführung nach Art des Datenupdates

### 3.1 Neue jährliche Ist-Daten für Straße, Schiene, Binnenschiff oder See

1. Originaldatei im passenden Quellordner ablegen und den bisherigen Dateinamen bzw. das dort verwendete Jahresmuster beibehalten.
2. Vor dem Lauf kontrollieren, ob die neue Datei dieselben Schlüsselspalten und dieselbe räumliche Ebene enthält.
3. **Technische Release-Grenzen prüfen:** Ein neues Datenrelease wird nicht in jedem Fall allein durch Kopieren einer Datei sichtbar. Die aktuell fest hinterlegten Grenzen und Dateinamen stehen in Abschnitt 3.1.1. Vor dem ersten abweichenden Release muss das betroffene Skript fachlich und technisch erweitert und diese Anleitung fortgeschrieben werden.
4. Wenn VE7, SGV oder IWW aktualisiert wurden, zuerst die O-D-Fakten neu erzeugen:

   `python pipeline_phase2_aggregations.py`

   Dieser Schritt schreibt `fact_od_flows.parquet`. Ohne ihn würden die Top-Relationen aus dem bisherigen Datenstand weiterverwendet.

5. Neuaufbau der Ist-Daten ausführen:

   `python build_web_data_bundle_v5.py`

6. Bei neuem Schienen- oder Binnenschiffsrelease zusätzlich ausführen:

   `python build_intermodal_data.py`

7. Bei neuem Seeverkehrsrelease anschließend ausführen, da das Skript die vorher erzeugte Datei `web_maritime.json` ergänzt:

   `python build_maritime_port_profiles.py`

8. Bei einem Neuaufbau des Seeverkehrs anschließend zwingend die Rohdatengegenprüfung ausführen:

   `python scripts/validate_maritime_bundle.py`

9. Danach den neuen Zeitstand, nationale Summen, ausgewählte Regionen und die Darstellung im Browser prüfen.

#### 3.1.1 Aktuelle technische Release-Grenzen

- **KBA Straße:** Die laufenden Skripte lesen gegenwärtig die zusammengefassten Dateien `ve7_2010_2024.csv`, `ve12_2010_2024.csv` und `ve13_2010_2024.csv`. Ein neuer KBA-Jahrgang darf nicht durch ein stilles manuelles Anhängen in die Produktivdatei übernommen werden. Zuerst ist festzulegen, ob eine neue, vollständig konsolidierte Datei erzeugt oder die Skriptlogik auf einzelne Jahresdateien umgestellt wird. Anschließend müssen sowohl die Dateireferenz als auch die Dokumentation angepasst werden.
- **SGV und IWW:** Die O-D-, Regional- und intermodale Pipeline lesen alle Jahresdateien ab 2016 mit den Mustern `eb_opendata_*.csv` beziehungsweise `IWW_OpenData_*.csv`. Das Intermodalmodul veröffentlicht nur Berichtsjahre, die in beiden Quellen vorhanden sind. Nach einem neuen Jahrgang ist deshalb zu prüfen, ob Schiene und Binnenschiff für dieses Jahr vollständig vorliegen.
- **MRTM Seeverkehr:** Die aktive Ist-, Hafenprofil- und Validierungspipeline liest alle Jahresdateien ab 2016 mit dem Muster `MRTM_OpenData_*.csv`. Nach einem neuen Jahrgang ist die vollständige Rohdatenprüfung weiterhin zwingend auszuführen.
- **NUTS-Geometrien:** Neue Geometrien sind kein regulärer Jahresdatenimport. `pipeline_phase1.py` dient nur der vorbereitenden Erzeugung von NUTS-Geometrien, Zentroiden und der NST-Systematik. Vor einer NUTS-Aktualisierung ist der Gebietsstand fachlich festzulegen und die Kompatibilität von `nuts_centroids_full.json` mit dem Dashboard gesondert zu prüfen.

### 3.2 Neues VP2040-Release oder neues VP2040-Szenario

Die VP2040-Pipeline ist eigenständig. Sie verwendet für die aktive Landverkehrsanalyse nur drei Matrizen je Szenario:

| Verkehrsträger | Erwartete Datei je Szenario |
| --- | --- |
| Straße | `VP2040_<Präfix>_GV_Strasse_NUTS3_Matrix_V01.csv` |
| Schiene | `VP2040_<Präfix>_GV_Bahn_NUTS3_Matrix_V01.csv` |
| Binnenschiff | `VP2040_<Präfix>_GV_Bischi_NUTS3_Matrix_V01.csv` |

Der aktuelle, im Skript fest hinterlegte Datenstand besteht aus:

| Szenario-ID | Ordner | Präfix | Fachliche Rolle |
| --- | --- | --- | --- |
| `2019_BASE` | `data/raw/VP2040/VP2040_2019_GV_NUTS3/` | `2019` | Basisjahr 2019 |
| `2040_P1` | `data/raw/VP2040/VP2040_2040P1BP_GV_NUTS3/` | `2040P1BP` | Basisprognose 2040, Prognosefall P1 |

Vor einem neuen Szenario ist zu entscheiden, ob es einen der beiden bestehenden Ordner **ersetzt** oder als zusätzlich auswählbares Szenario ergänzt werden soll. Ohne diese Entscheidung wird keine Datei überschrieben und kein Skript angepasst.

Nach vollständiger Ablage und Schema-Prüfung beider benötigten Matrizensätze wird ausgeführt:

`python pipeline_vp2040.py`

Der Lauf schreibt `data/processed/web_forecast_2040.json` zunächst in einen lokalen temporären Bereich und kopiert die fertige Datei erst anschließend in den Projektordner. Das verhindert eine teilweise geschriebene Ausgabedatei.

Anschließend ist zwingend auszuführen:

`python scripts/validate_vp2040_bundle.py`

Ein erfolgreicher Lauf endet mit `VP2040 validation passed`. Erst dann wird die Ausgabe im Browser geprüft.

## 4. Berechnungslogik der laufenden Ist-Daten

### 4.1 Straße (KBA)

Die regionale Ist-Ansicht verwendet die sieben direkt gelieferten Güterhauptgruppen aus VE12 (Versand) und VE13 (Empfang). Diese Dateien werden nach Jahr und deutscher NUTS-3-Region summiert. Eine künstliche Überleitung auf die 20 NST-Abteilungen findet auf dieser räumlichen Ebene nicht statt.

Die O-D-Relationen der Straße beruhen getrennt darauf auf VE7: `pipeline_phase2_aggregations.py` erzeugt daraus die Faktendatei `fact_od_flows.parquet` mit Jahr, Quelle, Ziel, Tonnen, Tonnenkilometern und Fahrten. `build_web_data_bundle_v5.py` bereitet daraus die angezeigten Spitzenrelationen je Region vor. VE12/VE13 und VE7 erfüllen damit unterschiedliche Funktionen und dürfen nicht gegeneinander ausgetauscht werden.

**Ranglisten, Gütergruppen und Vorjahr:** Für Schiene und Binnenschiff werden die Kandidaten der Relationstabellen je Region, Richtung, Verkehrsträger und NST-7-Hauptgruppe getrennt ermittelt. Für jede Gruppe müssen die Top-25-Kandidaten sowohl nach Tonnen als auch nach Tonnenkilometern verfügbar sein. Wird eine Relation erst im aktuellen Jahr sichtbar, muss ihr Rohwert des Vorjahres dennoch als Vergleichskandidat bereitgestellt werden. Der Browser darf für den Vorjahresvergleich einer gefilterten Gütergruppe ausschließlich die gruppenspezifische Relationsliste verwenden, nicht die allgemeine Rangliste. Nach jedem Neuaufbau muss `python scripts/validate_relation_coverage.py` bestehen.

### 4.2 Schiene und Binnenschifffahrt (Destatis)

Für die regionale Ist-Ansicht werden die vorhandenen Jahresdateien jeweils nach Jahr, Quell- bzw. Zielregion, Verkehrsträger und den im Tool verwendeten sieben NST-2007-Hauptgruppen aggregiert. Bei der Schiene stammen Quelle und Ziel aus den bereitgestellten NUTS-2024-Feldern; bei der Binnenschifffahrt aus den NUTS-3-Feldern. Die Güterzuordnung erfolgt aus den gelieferten NST-Codes und wird nicht geschätzt.

Für die O-D-Faktendatei werden nur Datensätze mit belegter Quell- und Zielregion verarbeitet. Die drei Verkehrsträger Straße, Schiene und Binnenschiff werden dort technisch als getrennte Reihen zusammengeführt; die Auswertung kann sie im Dashboard getrennt filtern.

Die NST-2007-Schlüssel werden bereits beim Einlesen als Zeichenfolgen behandelt. Eine führende Null ist Bestandteil des fachlichen Schlüssels und darf weder durch automatische Typumwandlung noch durch eine Tabellenkalkulation entfernt werden. Die Zuordnung zu den sieben Hauptgruppen muss in allen betroffenen Pipelines aus derselben kanonischen Zuordnung stammen. Vor einem Release sind die vorkommenden Originalcodes, nicht zugeordnete Codes und die Mengen je Hauptgruppe zu vergleichen.

Nationale Randsummen und regionale O-D-Summen haben unterschiedliche Abdeckungen: Nationale Vergleichswerte werden aus allen dafür vorgesehenen nationalen Rohdatensätzen gebildet. Relationstabellen können dagegen nur Datensätze mit verwertbarer Quell- und Zielregion enthalten und zeigen zusätzlich nur die stärksten Verbindungen. Deshalb darf eine nationale Kennzahl niemals aus den sichtbaren oder räumlich zuordenbaren Relationen zurückgerechnet werden. Eine verbleibende Differenz ist als methodische Abgrenzung zu dokumentieren, nicht stillschweigend zu verteilen.

### 4.3 Seeverkehr (MRTM)

Die Seeverkehrsverarbeitung berücksichtigt nur Datensätze mit Deutschland-Bezug, also Empfang oder Versand über einen deutschen Hafen. Sie berechnet nationale und regionale Summen, Güterstruktur und Hafenbezüge. `build_maritime_port_profiles.py` ergänzt anschließend die bereits erzeugte Datei `web_maritime.json` um hafenbezogene Empfangs- und Versandwerte sowie internationale Partner.

Die MRTM-Dateien enthalten in Anführungszeichen gesetzte Bezeichnungen, in denen selbst Semikolons vorkommen können. Sie müssen deshalb mit ausdrücklich gesetztem Semikolon-Trennzeichen und Anführungszeichen, vollständig als Zeichenfolgen und ohne stilles Überspringen fehlerhafter Zeilen eingelesen werden. Eine Stichprobenerkennung der Datentypen ist unzulässig. Ändert sich die Zahl der eingelesenen Zeilen oder treten unlesbare Zeilen auf, bricht die Freigabe ab, bis Ursache und Umfang geklärt sind.

Innerdeutscher Seeverkehr wird hafenbezogen gezählt: Der deutsche Löschhafen erhält die Empfangsmenge, der deutsche Ladehafen die Versandmenge. Dadurch können beide deutschen Hafenanläufe desselben Transports in Hafenprofilen erscheinen; dies ist keine versehentliche Dublette. TEU werden unmittelbar nach ihrer Verkehrsrichtung zugeordnet und nicht davon abhängig gemacht, ob zugleich ein positives Gütergewicht vorliegt, da auch leere Container gezählt werden. Die fertige Ausgabe ist mit `scripts/validate_maritime_bundle.py` gegen die Rohdaten zu prüfen.

### 4.4 Kombinierter Verkehr

Die intermodale Auswertung ist absichtlich keine nationale KV-Gesamtsumme. Auf der Schiene werden nur Datensätze mit einer Ladeeinheit ungleich `Keine` ausgewertet. In der Binnenschifffahrt werden nur Datensätze mit angegebener Containergröße einbezogen. Beide Teilmärkte bleiben getrennt, weil eine Transportkette in beiden amtlichen Statistiken enthalten sein kann.

Schiene und Binnenschiff bleiben in den Kennzahlen und Anteilsberechnungen getrennte Teilmärkte. Ihre Addition darf nicht als eindeutige nationale KV-Gesamtmenge oder als Zahl unterschiedlicher Sendungen bezeichnet werden. Für die räumliche Intensitätskarte werden die beiden amtlich erfassten Teilmarktvolumina dagegen addiert. Diese Kartensumme ist ausdrücklich als **„Summe erfasster KV-Teilmärkte“** zu kennzeichnen und im Tooltip in Schiene und Binnenschiff aufzuschlüsseln. Dadurch wird keine Überschneidungsfreiheit behauptet.

Die Auswahl **„Binnenverkehr ausblenden“** ist eine reine Darstellungsoption für Relationslinien und Relationstabellen. Sie darf keine KPI, Flächenfärbung, Güterstruktur, nationale Randsumme oder fachliche Ausgangsdatei verändern. Diese Regel gilt in allen Analysemodulen einschließlich Verkehrsprognose und kombiniertem Verkehr.

## 5. Berechnungslogik der VP2040 im Detail

### 5.1 Eingangsprüfung und Harmonisierung

Für jede der drei Matrizen eines Szenarios liest die Pipeline die Spalten `Quellzelle`, `Zielzelle`, `Guetergruppe`, `VerkArt`, `BehTyp`, `Tonnen`, `Tkm`, `Ladeeinheiten`, `TEU` und `Transportwert`. Die Dateien werden als Semikolon-CSV in Latin-1 gelesen, weil dies dem gelieferten Originalformat entspricht. Fehlende Schlüssel- oder Kennzahlwerte sowie leere oder fehlende Matrizen brechen den Lauf ab.

Die Zuordnung erfolgt ausschließlich mit den abgelegten Umstiegsschlüsseln:

- `crosswalk_spatial_vp2040.json` ordnet reguläre deutsche Verkehrszellen den im Tool verwendeten NUTS-3-Regionen zu. Ausland bleibt als VP2040-Zelle mit seiner dokumentierten Partnerbezeichnung erhalten.
- `vp2040_special_cells_nuts3.json` ordnet die in den aktiven Landverkehrsmatrizen vorkommenden deutschen Hafen- und Flughafenzellen genau einmal ihrer räumlichen NUTS-3-Gastregion zu.
- `crosswalk_nst_vp2040.json` ordnet die 25 VP2040-Gütergruppen sowohl den 20 NST-2007-Abteilungen als auch den sieben NST-2007-Hauptgruppen zu.

Die verbindlichen Originalquellen sind die mit der VP-Matrix gelieferte Datei `nst2007.csv`, die NST-2007-Referenz `nsz-2007.pdf` und das KBA-Referenzhandbuch VE13. Die Excel-Dateien der VP2040 dokumentieren ausschließlich Verkehrszellen, nicht Gütergruppen. Beide Szenarien müssen genau dieselben 25 Originalcodes enthalten. Für den Dashboardfilter gilt die amtliche, im VE13 verwendete NST-Zusammenfassung C1 bis C7: C1 umfasst die Abteilungen 01 bis 03, C2 die Abteilungen 04 bis 06, C3 die Abteilungen 07 bis 09, C4 die Abteilung 10, C5 die Abteilungen 11 bis 13, C6 die Abteilung 14 und C7 die Abteilungen 15 bis 20. Codeform, amtliche Abteilungsbezeichnung und VP-Bezeichnung sind gemeinsam zu prüfen; führende Nullen sind Teil der Originalschlüssel. Eine branchenlogische Neuordnung der sieben Gruppen ist unzulässig.

Die Pipeline erzeugt keine künstlich feinere Güterklassifikation: Die 25 Originalgruppen bleiben separat verfügbar; für die gemeinsame Darstellung mit den Ist-Daten werden nur die hinterlegten sieben Hauptgruppen verwendet.

Das zugrunde liegende VP2040-Zellsystem umfasst reguläre deutsche und ausländische Gebietszellen sowie zusätzliche Sonderzellen für Seehäfen, Flughäfen und Inseln. Diese Sonderzellen sind eigenständige Modellzellen und nicht bloß alternative Namen einer Gebietszelle. In den sechs aktuell verwendeten Landverkehrsmatrizen treten 40 deutsche Hafen- und Flughafenzellen auf. Ihre Mengen dürfen bei der NUTS-3-Aggregation weder verloren gehen noch doppelt gezählt werden.

Vor der räumlichen Aggregation wird deshalb geprüft, dass jede verwendete deutsche Sonderzelle genau eine Zuordnung besitzt. Die nationale Randsumme wird direkt aus den vollständigen Rohmatrizen gebildet und muss vor und nach der räumlichen Zuordnung unverändert bleiben. Erst nach der Zuordnung wird bestimmt, ob Quelle und Ziel zur selben NUTS-3-Region gehören und damit als Binnenrelation gelten. Eine fehlende oder mehrdeutige Sonderzellenzuordnung ist ein Abbruchgrund; sie darf nicht durch eine Schätzung oder den Ausschluss der Zeile kaschiert werden.

### 5.2 Nationale und regionale Kennzahlen

Die nationalen Kennzahlen sind die Summe der drei vollständigen verwendeten Landverkehrsmatrizen. Ausgegeben werden Tonnen, Tonnenkilometer, Ladeeinheiten, TEU und Transportwert sowie die drei Verkehrsträger getrennt. Auf der Ebene Deutschland ist eine Richtung fachlich nicht definiert; die Auswahl von Versand oder Empfang wird dort im Dashboard deaktiviert. Erst eine ausgewählte Region erzeugt durch ihre Rolle als Quelle oder Ziel eine Verkehrsrichtung.

Für jede deutsche NUTS-3-Region berechnet die Pipeline die folgenden Fachwerte. Sie bestehen unabhängig von der Darstellungsoption **„Binnenverkehr ausblenden“** unverändert fort:

- **Versand (`outbound`)**: Quelle liegt in der ausgewählten Region und das Ziel außerhalb dieser Region;
- **Empfang (`inbound`)**: Ziel liegt in der ausgewählten Region, ohne Binnenverkehr;
- **Binnenverkehr (`binnen`)**: Quelle und Ziel liegen in derselben Region;
- **Gesamt (`all`)**: Versand + Empfang + Binnenverkehr;
- **Saldo (`balance`)**: Versand – Empfang.

Diese Kennzahlen werden jeweils für Tonnen und Tonnenkilometer, für die drei Verkehrsträger sowie für die sieben Hauptgruppen und die 25 Originalgruppen berechnet. Für die sieben Hauptgruppen liegt die Kreuzung mit Straße, Schiene und Binnenschiff zusätzlich national und je NUTS-3-Region vor. Dadurch reagieren die Verkehrsträger-KPI und der Modal Split auf die ausgewählte Gütergruppe. KV-Werte werden ausschließlich mit `VerkArt = 2` abgegrenzt; sie sind keine Schätzung.

### 5.3 Relationen und Vergleich 2019–2040

Für jede Region werden die stärksten Relationen getrennt nach Gesamt, Versand und Empfang vorbereitet. Dasselbe geschieht je NST-2007-Hauptgruppe. Der Browser erhält nur diese angezeigten Spitzenrelationen; er berechnet keine Werte aus Rohdaten nach.

Die Veränderung 2040 gegenüber 2019 wird jeweils nach folgender Regel berechnet:

`(Wert_2040 – Wert_2019) / Wert_2019 × 100`

Sie wird für nationale Werte, Verkehrsträger, Gütergruppen, Regionen und die angezeigten Relationen aus den beiden Originalmatrizensätzen berechnet. Ist der Wert von 2019 null oder nicht vorhanden, wird keine Prozentveränderung ausgegeben. Das Dashboard zeigt dann `--`, nicht einen Ersatzwert.

Die relationsspezifischen Vergleichswerte werden zusätzlich in einem speicherschonenden Durchlauf direkt aus den drei 2019er Rohmatrizen ergänzt. Dadurch bleiben auch die Vergleichswerte bei Gütergruppen nachvollziehbar, ohne eine sehr große vollständige Relationsmatrix im Browser abzulegen.

Für die nachträgliche Ergänzung dieser 2019er Vergleichswerte gelten derselbe räumliche Crosswalk und dieselbe Sonderzellen-Datei wie im Szenarioaufbau. Eine zweite, im Skript hinterlegte Sonderzellenliste ist unzulässig. Nach jeder Änderung an Crosswalk, Matrix oder Relationslogik muss `python scripts/validate_vp2040_bundle.py` bestehen; der Test umfasst ausdrücklich den Richtungs- und Gütergruppenfall Hamburg–Dithmarschen (DEF05).

### 5.4 Vergleich von Ist-Reihe und VP2040-Reihe in der Übersicht

Der Karten-Hover kann für dieselbe Region, Richtung, Kennzahl und NST-7-Hauptgruppe sowohl die amtliche Ist-Reihe als auch VP2040 anzeigen. Beide Reihen müssen denselben im Dashboard gewählten Filter anwenden. Ihre absoluten Werte dürfen jedoch nur als Vergleich dargestellt werden, wenn ihre Quellenabgrenzung gleich ist. Insbesondere ist für Berlin zu prüfen, ob Straßenwerte der amtlichen KBA-Reihe und der VP2040-Matrix dieselbe Verkehrsabgrenzung besitzen. Bei einer dokumentierten Abgrenzungsdifferenz darf die Darstellung keine lückenlose Fortschreibung suggerieren; der VP2040-Basiswert 2019 ist sichtbar auszuweisen. Diese Prüfung ist bei Änderungen an Datenkatalog, Crosswalk oder Tooltip-Logik im Browser mit mindestens einer straßen-dominierten und einer nicht straßen-dominierten Gütergruppe durchzuführen.

## 6. Ergebnisdateien und Abhängigkeiten

| Skript | Schreibt bzw. ergänzt | Abhängigkeit |
| --- | --- | --- |
| `pipeline_phase2_aggregations.py` | `fact_od_flows.parquet`, `fact_regional_summary.parquet`, `national_benchmarks.json` | KBA VE7, SGV und IWW; Grundlage für die Ist-Daten-Relationen |
| `build_web_data_bundle_v5.py` | `web_regions.json`, `web_summary_by_region.json`, `web_choropleth.json`, `web_maritime.json` und regionale Relationsdateien | NUTS-Zentroide, KBA, SGV, IWW, MRTM sowie für die Relationen `fact_od_flows.parquet` |
| `build_intermodal_data.py` | `web_intermodal.json` | SGV und IWW; die Teilmärkte bleiben getrennt und werden nicht zu einem nationalen KV-Gesamtwert addiert |
| `build_maritime_port_profiles.py` | ergänzt `web_maritime.json` | zuvor erzeugtes `web_maritime.json` und MRTM |
| `pipeline_vp2040.py` | `web_forecast_2040.json` | VP2040-Matrizen 2019 und 2040 P1, räumlicher und fachlicher Umstiegsschlüssel, `web_regions.json` |
| `scripts/validate_maritime_bundle.py` | keine Produktivdatei | prüft `web_maritime.json` unabhängig gegen alle aktiven MRTM-Jahresdateien |
| `scripts/validate_vp2040_bundle.py` | keine Produktivdatei | prüft `web_forecast_2040.json` unabhängig gegen die VP2040-Rohmatrizen einschließlich Sonderzellenzuordnung |

Ein Neuaufbau der Daten erfordert keinen Neuaufbau der Weboberfläche. `python scripts/build_frontend.py all` wird nur ausgeführt, wenn Dateien unter `html/`, `css/source/` oder `js/source/` beziehungsweise `js/modules/` geändert wurden.

## 7. Mindestprüfung und Freigabeprotokoll

Für jedes übernommene Release sind folgende Punkte kurz zu protokollieren:

| Prüfschritt | Nachweis |
| --- | --- |
| Datenlieferung | Quelle, Abrufdatum, Dateiname, Berichtsjahr bzw. Szenario, Datensatzbeschreibung |
| Vollständigkeit | erwartete Dateien vorhanden; bei Monatsdaten vollständige Monate; bei VP2040 alle drei Landverkehrsmatrizen |
| Vergleichbarkeit | räumliche Ebene, Gütersystematik, Einheit und fachliche Abgrenzung unverändert oder Abweichung dokumentiert |
| Neuaufbau | ausgeführtes Skript und erfolgreicher Abschluss |
| Rohdatenstichprobe | nationale Summe, ein Verkehrsträger, mindestens drei Regionen und eine Relation bzw. Gütergruppe |
| Browserprüfung | ausgewähltes Jahr/Szenario, Kennzahl, Einheit, Überschrift und mindestens eine Karte oder Tabelle plausibilisiert |
| Sicherung | Pfad der Sicherung des vorherigen produktiven Datenstands |

Für VP2040 deckt `scripts/validate_vp2040_bundle.py` bereits nationale Summen, Verkehrsträger, die Regionen DE600, DE300, DE501, DE502, DE949 und DE942 sowie Gesamt- und Gütergruppenrelationen ab. Die Browserprüfung ergänzt die technische Prüfung um die tatsächlich sichtbare Darstellung.

## 8. Verbindliche Fehlervermeidung für künftige Bearbeitungen und KI-Systeme

### 8.1 Pflichtlektüre und Arbeitsreihenfolge

Vor jeder Änderung an Rohdaten, Umstiegsschlüsseln, Pipelines, Berechnungsregeln oder Dashboard-Ausgaben sind mindestens diese Unterlagen zu lesen:

1. diese Aktualisierungsanleitung;
2. `QUALITÄTSSICHERUNGSPLAN.md`;
3. die zur betroffenen Quelle gehörende Datensatzbeschreibung im Rohdatenordner;
4. die betroffenen Umstiegsschlüssel und Prüfscripte;
5. bei einer Oberflächenänderung zusätzlich `README_MAINTENANCE.md`.

Die Reihenfolge ist verbindlich: fachliche Abgrenzung klären, Rohdatenprofil und Schema prüfen, Verarbeitung ausführen, maschinell gegen Rohdaten validieren, anschließend die sichtbare Darstellung mit denselben Filtern im Browser prüfen. Annahmen aus Dateinamen, scheinbar ähnlichen Spalten oder früheren Releases ersetzen keine Quellenprüfung.

### 8.2 Wiederkehrende Fehlerrisiken und verbindliche Gegenmaßnahmen

| Risiko | Verbindliche Regel | Mindestnachweis vor Freigabe |
| --- | --- | --- |
| CSV wird wegen eingebetteter Trennzeichen falsch zerlegt | Trennzeichen, Anführungszeichen, Zeichencodierung und Spaltentypen ausdrücklich setzen; keine fehlerhaften Zeilen still überspringen | Zeilenzahl, Spaltenzahl und mindestens drei Originalzeilen gegen den Import spiegeln |
| Führende Null in NST- oder Gebietscodes geht verloren | Schlüssel bereits beim Import als Zeichenfolge behandeln; Rohcode unverändert mitführen | vorkommende und nicht zugeordnete Codes vor und nach Verarbeitung vergleichen |
| VP2040-Crosswalk wird nach fachlicher Ähnlichkeit statt nach NST-Abteilung geändert | Die amtliche C1–C7-Zuordnung ausschließlich aus der NST-2007-Abteilung ableiten; VP-Begriff als unabhängigen Textabgleich verwenden | `scripts/validate_vp2040_bundle.py` besteht: 25 eindeutige Codes, CSV = JSON, Begriffstest gegen beide `nst2007.csv` und NST-2007-PDF |
| Nationale Kennzahl wird aus unvollständigen Relationen gebildet | Nationale Randsumme aus dem vollständigen dafür vorgesehenen Rohdatenbestand berechnen; Relationstabellen nie aufsummieren | Rohsumme und Dashboard-KPI mit identischer Einheit und Abgrenzung vergleichen |
| Top-X-Tabelle wird als vollständige Summe missverstanden | Relationstabellen als Ranglisten kennzeichnen; methodischen Hinweis im jeweiligen Informationsfenster mitführen | Browserprüfung von Ranggrenze, Richtung und Hinweistext |
| Binnenverkehrsfilter verändert Fachwerte | Filter ausschließlich auf Relationslinien und Relationstabellen anwenden | KPI und Flächenkarte müssen beim Umschalten unverändert bleiben; Binnenrelation muss sichtbar verschwinden bzw. erscheinen |
| Innerdeutscher Seeverkehr oder leere Container werden unterzählt | Deutsche Lade- und Löschhäfen richtungsbezogen zählen; TEU unabhängig von positivem Gewicht verarbeiten | Seeverkehrsvalidator sowie mindestens ein innerdeutscher Fall und ein TEU-Fall |
| VP2040-Sonderzellen gehen verloren oder werden doppelt gezählt | ausschließlich den versionierten Sonderzellen-Crosswalk verwenden; jede verwendete Sonderzelle genau einmal zuordnen | Rohmatrixsumme vor und nach NUTS-3-Zuordnung identisch; keine ungemappte deutsche Zelle |
| Ausländische VP2040-Partner erscheinen nur als Nummer | Partnerbezeichnung aus dem räumlichen Crosswalk erhalten | mindestens eine grenzüberschreitende Relation im Browser prüfen |
| Kartensumme der KV-Teilmärkte wird als eindeutige Gesamtmenge missverstanden | Kennzahlen und Anteile getrennt ausweisen; die gemeinsame Karte ausschließlich als „Summe erfasster KV-Teilmärkte“ und nicht als eindeutige Sendungs- oder Gesamtmenge bezeichnen | getrennte KPI sowie gemeinsame Kartenlegende und Aufschlüsselung im Tooltip prüfen |
| Unterschiedliche KBA-Produkte werden gleichgesetzt | VE7 ausschließlich für O-D-Relationen, VE12/VE13 für regionale Versand-/Empfangskennzahlen verwenden | Quelle und fachliche Rolle im Freigabeprotokoll nennen |
| Generierte Webdateien werden direkt geändert | nur Dateien unter `html/`, `css/source/`, `js/source/` oder `js/modules/` bearbeiten und danach den Frontend-Build ausführen | generierte Dateien stammen aus einem erfolgreichen `python scripts/build_frontend.py all` |

Zusätzlich sind bei jedem betroffenen Release folgende maschinenlesbare oder tabellarische Prüfnachweise zu erzeugen und mit dem Freigabeprotokoll abzulegen:

- **NST-Schlüssel:** mindestens die tatsächlich vorkommenden Codes `01` und `07` vom Rohwert über die kanonische Zuordnung und die Zwischendatei bis zur entsprechenden Hauptgruppensumme in der Webausgabe verfolgen. Fehlt einer dieser Codes im neuen Jahrgang, wird stattdessen ein anderer tatsächlich vorkommender Code mit führender Null dokumentiert. Die Rohcodes müssen dabei zweistellig erhalten bleiben.
- **VP2040-Güterschlüssel:** vor jedem Neuaufbau die 25 VP-Codes, VP-Begriffe, NST-Abteilungen und C1–C7-Gruppen prüfen. Die CSV ist die lesbare Prüftabelle, JSON die Laufzeitfassung; beide müssen in allen fachlichen Feldern exakt übereinstimmen. Die Referenz sind ausschließlich `data/raw/VP2040/.../nst2007.csv`, `data/raw/Straße/KBA/Empfang_VD3cE_NUTS2_20Gueter/nsz-2007.pdf` und das VE13-Referenzhandbuch – nicht Codebreite, Ziffernlänge oder eine eigene Branchenlogik.
- **Randsummen:** je Jahr, Verkehrsträger und Kennzahl eine Prüftabelle mit Rohsumme, Ausgabesumme, Einheit, Differenz und fachlicher Abgrenzung erzeugen. Für Tonnen und Tonnenkilometer sind zusätzlich die sieben Güterhauptgruppen zu prüfen. Auf regionaler Ebene muss `Gesamt = Versand + Empfang + Binnen` und `Saldo = Versand − Empfang` gelten.
- **Ist–VP-Basisvergleich:** Im gemeinsamen Jahr 2019 für zwei Gütergruppen den Vergleich Istreihe/VP-Basis als Abgrenzungsprüfung dokumentieren: Region, Richtung, Kennzahl, Verkehrsträger, C-Gruppe, Quelle, Grundgesamtheit und Einheit. Unterschiedliche Werte sind zulässig, aber nur mit schriftlich belegter Abgrenzung; sie sind kein Anlass, den Crosswalk nachträglich passend zu machen.
- **MRTM-Import:** für jede erwartete Jahresdatei Dateiname, Vorhandensein, Zeilen- und Spaltenzahl, Schemaabweichungen sowie Summen nach Empfang und Versand ausweisen. Ein fehlendes Jahr, eine verringerte Zeilenzahl oder eine unerklärte Summenabweichung verhindert die Freigabe.
- **VP2040-Sonderzellen:** für jede der 40 in den aktiven Matrizen vorkommenden deutschen Hafen- und Flughafenzellen und für jede der sechs Matrizen einen Status ausgeben: `einmalig zugeordnet`, `nicht vorhanden`, `nicht zugeordnet` oder `mehrfach zugeordnet`. Jede tatsächlich vorkommende Zelle muss `einmalig zugeordnet` sein; die nationale Summengleichheit allein genügt nicht als Nachweis.

### 8.3 Abbruch- und Dokumentationsregel

Eine Verarbeitung wird nicht freigegeben, wenn eine Quelldatei stillschweigend Zeilen verliert, Schlüssel nicht eindeutig zugeordnet sind, CSV- und JSON-Crosswalk fachlich voneinander abweichen, nationale Summen ohne geklärte methodische Ursache abweichen oder eine Browserdarstellung nicht mit dem auf Rohdatenbasis errechneten Prüffall übereinstimmt. Es werden weder Werte von Hand in erzeugten JSON-Dateien korrigiert noch unbekannte Fälle geschätzt oder Restmengen proportional verteilt.

Jede fachliche Besonderheit, die die Interpretation einer Relationstabelle oder ihre Vergleichbarkeit mit der nationalen Kennzahl betrifft, wird zusätzlich im Informationsfenster des betroffenen Analysemoduls erläutert. Ändert sich eine Methode, werden Pipeline, Validator, diese Anleitung, Qualitätssicherungsplan und sichtbarer Hinweis gemeinsam fortgeschrieben.

### 8.4 Definition „freigabefähig“

Ein Datenstand ist erst freigabefähig, wenn:

- alle betroffenen Verarbeitungsschritte ohne Warnung über verworfene Datensätze abgeschlossen sind;
- die zugehörigen Validatoren bestanden wurden;
- nationale Randsumme, mindestens drei Regionen sowie Relations-, Richtungs- und Gütergruppenfälle gegen die Rohdaten geprüft wurden;
- der Binnenverkehrsfilter nachweislich nur die Relationsdarstellung verändert;
- die methodischen Informationsfenster zur aktuellen Datenlogik passen;
- dieselben Prüffälle mit ihren exakten Filtern und Einheiten im Browser bestätigt wurden;
- Abweichungen, Quellenstand, ausgeführte Befehle und Sicherungspfad im Freigabeprotokoll festgehalten sind.

## 9. Verantwortliche Fortschreibung dieser Anleitung

Diese Anleitung wird gemeinsam mit der Pipeline aktualisiert, wenn sich mindestens einer der folgenden Punkte ändert: Quelle oder Dateiformat, Zeitfenster, räumlicher Gebietsstand, Gütersystematik, Berechnungsregel, Szenarioliste, Ausgabedatei oder Prüfschritt. Ein neues Datenrelease ohne solche methodische Änderung wird ausschließlich als Release im Freigabeprotokoll ergänzt.
