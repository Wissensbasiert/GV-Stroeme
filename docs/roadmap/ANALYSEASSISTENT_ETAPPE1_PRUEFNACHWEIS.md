# Analyseassistent Etappe 1 – Prüfnachweis

**Datum:** 08.09.2026 · **Art:** lesende Bestandsprüfung und Dokumentkontrolle, keine Pipelineausführung oder Assistentenabnahme.

## 1. Umfang und Status

Aus acht Akteursperspektiven wurden 160 Kandidatfragen formuliert. Nach der fachlichen Abgrenzung auf vorhandene Dashboard- und Rohdaten sind 84 Fragen den 15 Fragetypen zugeordnet; darunter ausdrücklich begrenzte Teilfragen und Grenzfälle. 76 Fragen bleiben als Bedarf außerhalb des vorgesehenen Umfangs sichtbar. 45 Testfälle konkretisieren die Ergebnislogik. Sie sind keine 45 bereits ausgeführten Assistententests.

Die Dokumente wurden zweimal an die Rückmeldung zum Umfang angepasst: zuerst Bedarfsermittlung unabhängig vom vorhandenen Datenbestand, danach Begrenzung des geplanten Antwortumfangs auf diesen Bestand. Es werden keine externen Datenprodukte oder neuen Umwelt-, Kapazitäts-, Kosten- oder Transportkettenanalysen vorbereitet. Es bleibt bei sieben möglichen Prüfpaketen für vorhandene Rohdaten, ohne Dashboarderweiterung.

Gelesen wurden README, Dokumentationsindex, Roadmap, Fachkonzept, Qualitätssicherungsplan, Datenkatalog, Crosswalk-Dokumentation sowie einschlägige aktive Aufbereitungsskripte. Ausführung erfolgte nur für kurzlebige lesende Abfragen und die Erstellung dieser Markdown-Dokumente. Keine Daten-/Frontend-Builds, keine neuen Abhängigkeiten, keine Veröffentlichung, kein externer Modellaufruf, keine externe Quellenverfügbarkeitsprüfung und keine Live-Mautabfrage.

## 2. Arbeitsstand

Git-HEAD bei Erstellung: `5285fc90abd2fe5810d27cecbb9b0d8ee9e4e11a`. Der Arbeitsbaum war bereits verändert; insbesondere die verlinkte Roadmap war vor Beginn modifiziert. Vorhandene Änderungen und unversionierte Dateien wurden erhalten. HEAD allein beschreibt deshalb nicht den vollständigen Daten-/Dokumentstand; für die gelesenen Zahlenquellen gelten zusätzlich die unten aufgeführten SHA-256-Werte.

Der aktuelle Qualitätssicherungsplan, Abschnitt 10.9, dokumentiert alle zehn manuellen Nutzerfälle als bestanden. Eine eigene neue fachliche Freigabe des Analyseassistentenkatalogs wird daraus nicht abgeleitet. Frühere interne Hinweise wurden nur zur Orientierung verwendet; maßgebliche Aussagen wurden im aktuellen lokalen Bestand nachgesehen.

## 3. Tatsächlich kontrollierte Schemas

- `fact_od_flows.parquet`: 498.143 Zeilen; Jahr, Quelle, Ziel, Verkehrsträger, C-Gruppe, Tonnen, Tonnenkilometer, trips. Straße 2010–2024 mit `ALL`; Schiene 2016–2025 und Binnenschiff 2011–2025 mit C1–C7. 101.742 fehlende trips-Werte. Keine Qualitätsspalten. Keine Nullwerte in den gelesenen Tonnen-/tkm-Spalten; dies beweist keine vollständige Quellenqualität oder Nullsemantik.
- `fact_regional_summary.parquet`: 96.950 Zeilen; Straße nur `ALL`, daher kein Ersatz für regionale VE12-/VE13-Gütergliederung in `web_summary_by_region.json`.
- Nationaldaten 2025 enthalten nur Schiene/Binnenschiff, keine Straße.
- Intermodalbestand Schema 3 enthält nationale, regionale, richtungsbezogene und Relationswerte; `not_additive=true`. Das ältere Fachkonzept beschreibt diese regionale Verfügbarkeit noch nicht.
- Luftfracht-Metadaten: nationale und Flughafen-Tonnage 2016–2025; belastbare Flughafen-Flugzahlen und veröffentlichte Relationsjahre nur bis 2024. Gespeicherte Top-Relationen maximal 25.
- Ist-Regionalzusammenfassung addiert Versand und Empfang inklusive Binnen in beiden Richtungen. Die VP-Aufbereitung bildet externen Versand + externen Empfang + Binnen einmal. Diese Zählweisen wurden in den aktiven Quellen nachgesehen.
- `dim_nst2007.json` enthält eine alte, abweichende Gruppierung. Für den Katalog gilt der aktuelle C1–C7-Vertrag im Crosswalk-README und den aktiven Zuordnungsregeln; keine Korrektur an der Datendatei vorgenommen.

## 4. Lesend nachgerechnete Kontrollwerte

### Regionalvergleich 2024, t, Versand plus Empfang

| Region | Gesamt | Straße | Schiene | Binnenschiff | Versand | Empfang | Saldo |
|---|---:|---:|---:|---:|---:|---:|---:|
| Duisburg DEA12 | 108.215.313,5 | 48.505.812 | 18.055.930 | 41.653.571,5 | 45.332.657,8 | 62.882.655,7 | −17.549.997,9 |
| Magdeburg DEE03 | 23.180.902,5 | 15.934.549 | 4.368.137 | 2.878.216,5 | 11.109.259,2 | 12.071.643,3 | −962.384,1 |

Modalanteile aus diesen ungerundeten Ausgangswerten: Duisburg 44,8 / 16,7 / 38,5 %, Magdeburg 68,7 / 18,8 / 12,4 % für Straße/Schiene/Binnenschiff. Führende Gesamtgütergruppen C1 in Duisburg (35.972.424,2 t), C7 in Magdeburg (6.065.189,9 t). Die regionale Straßen-Rohkontrolle für Duisburg ergibt VE12-Versand 26.371.111 t und VE13-Empfang 22.134.701 t; jeweils sieben Güterzeilen ohne Tonnen-ZS-Markierung in der Stichprobe.

### Vollständige Relationen mit Rohkontrolle

Köln DEA23 → Hamburg DE600, Schiene 2024: 199.851 t, davon C7 199.620 und C1 231 t. Die Original-SGV-Datei bestätigt NST 031=231, NST 161=12.817 und NST 191=186.803 t. Der Test T19 verwendet die bestätigte Richtung und diese Zuordnung.

Hamburg DE600, Straße 2024, beide Richtungen, nur externe Partner: DE933 5.126.813; DEF0D 4.628.663; DEF0F 3.374.382; DEF06 2.687.481; DE929 2.289.981 t. Reihenfolge und Mengen stimmen zwischen vollständigem Parquet und VE7-Rohdatei. Interne Relation DE600→DE600: 23.607.440 t, im externen Ranking ausgeschlossen.

Im berührenden Hamburger Rohbestand waren 169 von 207 Zeilen für Tonnen mit `( )` markiert. Die zehn Richtungszeilen der fünf führenden Außenpartner waren unmarkiert. Die Flagbedeutung wurde nicht aus eigener Interpretation festgelegt; B01 verlangt Quellendefinition und Erhalt. Somit keine pauschale Freigabe aller Hamburger Relationswerte oder Prozentnenner als uneingeschränkt belastbar.

### Nationaler Modal Split 2024 nach tkm

Aus D03: Straße 455.156.638.190; Schiene 126.319.807.860; Binnenschiff 43.443.314.381; Summe 624.919.760.431 tkm. Rechnerische Anteile vor Anzeige: rund 72,8344 / 20,2138 / 6,9518 %. Diese nationalen Werte wurden in dieser Etappe aus dem vorhandenen Benchmark gelesen, nicht erneut über alle nationalen Rohdateien aggregiert.

### Magdeburger Schienenreihe

D01, DEE03, Gesamt-t, 2016 bis 2025: 391.082; 376.529; 413.339; 3.350.578; 3.563.715; 3.712.362; 3.775.110; 4.466.662; 4.368.137; 1.265.439. Die auffälligen Sprünge sind Bestandstatsachen, ihre Ursache und die Vergleichbarkeit wurden nicht neu geklärt. Der Test verlangt deshalb Transparenz statt einer unbelegten Wachstumserklärung.

### Prognose 2019_BASE gegenüber 2040_P1

Duisburg, Landverkehr insgesamt: 115.374.997 → 103.871.423 t; rund −10,0 %. Keine Mischung mit dem anders gezählten Ist-Regionalwert.

Schienen-Zuwachsrang unter den 400 IDs des vorhandenen deutschen NUTS-2024-Geometriebestands, die in beiden Szenarien vorhanden sind:

| ID | Basis 2019, t | Ziel 2040, t | Zuwachs, t |
|---|---:|---:|---:|
| DE600 | 56.947.238 | 74.766.845 | 17.819.607 |
| DEA23 | 9.969.301 | 18.669.000 | 8.699.699 |
| DEB34 | 10.057.073 | 15.929.876 | 5.872.803 |
| DE502 | 11.818.574 | 16.602.420 | 4.783.846 |
| DE212 | 11.901.451 | 16.324.703 | 4.423.252 |

Die Rangfolge wurde aus allen 400 gefilterten Regionen berechnet, nicht aus einer Top-Auslieferung übernommen. Keine vollständige erneute Prüfung sämtlicher Prognosematrizen.

### Statistische intermodale Teilmärkte

National 2024: Schiene mit Ladeeinheiten 99.853.065 t / gesamte Schiene 337.515.115 t; Binnenschiff mit Containern 16.738.676,4 t / gesamtes Binnenschiff 173.778.020,4 t. Jeweilige Quote separat. Duisburg Schiene externer Versand: 4.422.816 / 9.194.861 t = rund 48,1 %. Die regionalen Richtungswerte wurden aus `scoped_metrics_by_year` gelesen. Keine betriebliche Transportkettenauswertung.

## 5. Noch nicht numerisch abgenommene Fälle

Insbesondere zusätzliche Monatswürfel, nationale Transitaufteilung, VD2-/VD3c-Auswertungen, weitere Detailjahre auf einzelnen Relationen, freie Regionsverbünde und feste Maut-Teststände benötigen vor einem Modellvergleich noch ihren eigenen freigegebenen Zahlenstand. Die Dokumente benennen den vorhandenen Quellenansatz, die benötigten Dimensionen und die erwartete Rechnung. Sie behaupten keinen bereits umgesetzten vollständigen Analysebestand.

Alle 45 Testfälle enthalten überprüfbare Ergebnislogik; nicht jeder Fall enthält eine bereits aus Rohdaten berechnete reale Sollzahl. Das entspricht dem Status eines fachlich prüfbaren Detailkonzepts. Fachliche Bestätigung, zusätzliche Rohdatenaufbereitung und spätere Assistententests sind getrennte Arbeitsschritte.

## 6. Eingefrorene Prüfsummen der gelesenen Datenquellen

Die Prüfsummen identifizieren den tatsächlich gelesenen lokalen Stand; sie sind kein Release-Tag und keine Freigabe. Pfade relativ zum Projektstamm.

| Datei | Bytes | SHA-256 |
|---|---:|---|
| `data/processed/web_summary_by_region.json` | 20814827 | `70947162eadf116609315f0cef849b89043c4ee2ca5604eb424de16a2fb1e774` |
| `data/processed/fact_od_flows.parquet` | 5266948 | `700bb5369cd912e368cbd23875d2824b0e7260d6bd3b40dd11604e06af97a4f6` |
| `data/processed/fact_regional_summary.parquet` | 1208661 | `d48621f0b66ab3cb264d85d8b0a26856c87e6f416fe840822634e952c6d90703` |
| `data/processed/national_benchmarks.json` | 6623 | `8d84dd126723a1cc1d60090763a96bee5347412f840cf8a184c53ba46b1cad30` |
| `data/processed/web_forecast_2040.json` | 171737099 | `e3e4d9a3d0d1e00662f2d78a7655eed81e133f913df56374ff3fbf2b5b7ffb1c` |
| `data/processed/web_forecast_core.json` | 9203156 | `802b6f1f3d4f0aa32c3fe3a6d7c5fe1914a1146d81e48e5172277f911352e062` |
| `data/processed/web_intermodal.json` | 8053422 | `a50642f48e5e3ef4a3f6560a3331aecddbbe76e55552fc914a799aa26a5af138` |
| `data/processed/web_airfreight.json` | 1446953 | `3a646626448860dd11aaf765710abfd19d363da8d9100673110cd2d9a8aa0999` |
| `data/processed/web_maritime.json` | 5812951 | `9ae3763b1507d33cc27e2a8afd6bf3114b47ed3576792b995ec5032cb4179179` |
| `data/processed/nuts3_de_2024.geojson` | 1420201 | `7ee20278f6a019cb2142810dff13c234196ebb7d5132554838dcbfbe1d88ccf8` |
| `data/crosswalks/crosswalk_nst_vp2040.json` | 8654 | `a81606dcae69717549efd38738e01612f17d27a319c26148418ea4dd01cfe915` |
| `data/raw/Straße/KBA/VE7_Verflechtung_NUTS3/ve7_2010_2024.csv` | 16865581 | `4db91e27ba70f352b8689a5df23a48fb22b6378884d3eb5fd217b29af2b68bd9` |
| `data/raw/Straße/KBA/Versand_VE12_NUTS3_7Gueter/ve12_2010_2024.csv` | 2809339 | `76f2af1329c51988ac62a6c995b185f06627518dc7896779dd5efa56c1519f38` |
| `data/raw/Straße/KBA/Empfang_VE13_NUTS3_7Gueter/ve13_2010_2024.csv` | 2924763 | `bf94d6d52c06a27887977b08f7ec83db6cb835df883c4151d4af1f4ba1dd9b2e` |
| `data/raw/SGV OpenData/eb_opendata_2024.csv` | 19482936 | `51f64b87384eb6480eceedd8b768793a430d879cfaedf66c96546785149bb190` |

## 7. Dokumentkontrolle

Ergebnis der abschließenden Struktur-, Verweis- und UTF-8-Prüfung wird unten dokumentiert. Bestehende Dateien außerhalb der vier neuen Etappe-1-Dokumente wurden nicht bearbeitet.

**Bestanden:** vier Markdown-Dokumente strikt als UTF-8 wieder eingelesen; keine Ersatzzeichen oder geprüften typischen Umlautbeschädigungen. Alle lokalen Dokumentverweise existieren. Genau 160 eindeutige Kandidaten in acht Gruppen zu je 20; 160 eindeutige nachgelagerte Abdeckungszuordnungen, davon 84 mit Fragetyp und 76 außerhalb. Genau 15 Typen und 45 eindeutige Test-IDs mit je drei Fällen. Alle Fälle enthalten Herkunft, Parameter, Datenbasis/Quelle, Kennzahl/Einheit, Ergebnislogik und Grenze. Alle sechs UI-Beispielfragen sind einem konkreten Testfall zugeordnet. Kein Modell- oder Browserfunktionstest ausgeführt.
