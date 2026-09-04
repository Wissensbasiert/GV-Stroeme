# Flughafenstandorte für das Luftfrachtmodul

Stand: 4. September 2026

## Zweck und Quellenrollen

Die Dateien in diesem Ordner dienen ausschließlich als räumliche Referenz für die im geplanten Luftfrachtmodul verwendeten ICAO-Flughafencodes. Die Eurostat-Luftverkehrstabellen bleiben die fachliche Quelle für Flüge, Frachtmengen und Relationen.

- **GISCO** ist die vorrangige Quelle für Koordinaten und für die Bezeichnungen ausländischer Flughäfen.
- **Die deutschsprachige Eurostat Statistics API** ist die Anzeigeautorität für deutsche Flughafenbezeichnungen. Die dort in Versalschrift und teils ohne Umlaute gelieferten Labels werden ausschließlich orthografisch aufbereitet, beispielsweise zu „Frankfurt/Main“, „Köln/Bonn“ und „Leipzig/Halle“.
- **OurAirports** wird nur ergänzend verwendet, wenn ein in den Eurostat-Daten vorkommender ICAO-Code in der GISCO-Datei fehlt.
- Ein Flughafen ohne Treffer in beiden Quellen bleibt in Tabellen erhalten und wird als „ohne Kartenpunkt“ gekennzeichnet. Er darf nicht stillschweigend entfallen.

## Abgelegte Originaldateien

| Datei | Quelle und Abruf | Format / Stand | Größe | SHA-256 | Hinweise zur Nachnutzung |
|---|---|---|---:|---|---|
| `GISCO_AIRP_PT_2024_GPKG.zip` | [Eurostat/GISCO – Transport networks](https://ec.europa.eu/eurostat/en/web/gisco/geodata/transport-networks), Direktabruf: `https://ec.europa.eu/eurostat/documents/d/gisco/airp-pt-2024-gpkg`, abgerufen am 03.09.2026 | GeoPackage im ZIP, Flughafenstand 2024 | 2.152.642 Byte | `7D85F81A167E3492831715E009948A45BE51FFAAF48F8EB0D26786DB19AD96D6` | Quelle Eurostat/GISCO nennen; maßgeblich sind die jeweils aktuellen Eurostat-Hinweise zu Copyright und Weiterverwendung. |
| `ourairports_airports_2026-09-03.csv` | [OurAirports Data](https://ourairports.com/data/), Direktabruf: `https://davidmegginson.github.io/ourairports-data/airports.csv`, abgerufen am 03.09.2026 | CSV-Tagesstand 03.09.2026 | 12.716.717 Byte | `81EB4259EA42834DDE3EE8EB407E6184A32C59AAE9D8F33563BD4F804946FFB9` | OurAirports stellt die Daten als Public Domain ohne Gewähr bereit. Quelle und Abrufstand dennoch nennen. |

Die Originaldateien bleiben unverändert. Abgeleitete, für das Dashboard optimierte Dateien müssen getrennt gespeichert und über ihre Erzeugungsschritte nachvollziehbar dokumentiert werden.

## Geprüfte Abdeckung für die vorhandenen Luftverkehrsdaten

Für die in den vorhandenen Eurostat-Dateien der Jahre 2016 bis 2024 vorkommenden Flughafenbeziehungen wurden 281 unterschiedliche ICAO-Codes ermittelt.

- GISCO deckt 279 von 281 Codes ab.
- In GISCO fehlen für diesen Bestand `CYYC` (Calgary) und `EKCH` (Kopenhagen).
- OurAirports ergänzt beide Codes.
- Beide Quellen zusammen decken damit den derzeitigen Bestand vollständig ab: 281 von 281 Codes.

Die Abdeckung ist bei jeder Datenaktualisierung erneut zu prüfen. Das Ergebnis ist kein dauerhafter Qualitätsnachweis für spätere Eurostat-Stände.

## Aktualisierungsablauf

1. Neue Quelldateien zunächst in einem temporären Arbeitsordner unter `C:\tmp` herunterladen; keine Paket-Caches oder großen Zwischenstände im synchronisierten Projektordner anlegen.
2. GISCO-Version, OurAirports-Abrufdatum, Dateigröße, Struktur und SHA-256-Prüfsumme kontrollieren.
3. Neue Originaldateien mit eindeutigem Versions- beziehungsweise Datumsbezug ablegen. Vorherige Stände erst entfernen, wenn Verarbeitung und Qualitätssicherung abgeschlossen sind.
4. Alle in den aktuellen Eurostat-Luftverkehrsdaten enthaltenen ICAO-Codes gegen GISCO und anschließend gegen OurAirports prüfen. Nicht auflösbare Codes protokollieren und im Tool als „ohne Kartenpunkt“ sichtbar machen.
5. Verarbeitungsmetadaten und Datenkatalog aktualisieren. Erst wenn die Quellen tatsächlich im produktiven Modul verwendet werden, außerdem die sichtbaren Bereiche „Quellen“ und „Hinweise“ gemäß der Roadmap synchron ergänzen.
6. Abgeleitete Geodaten fachlich und kartografisch prüfen: Koordinatenbereich, vertauschte Längen-/Breitengrade, Dubletten, falsche Code-Zuordnung und auffällige Lagepunkte.

## Quellen- und Lizenzhinweise

- [Eurostat – Copyright und freie Weiterverwendung](https://ec.europa.eu/eurostat/help/copyright-notice)
- [Europäische Kommission – rechtlicher Hinweis](https://commission.europa.eu/legal-notice_en)
- [OurAirports – Datenbeschreibung](https://ourairports.com/help/data-dictionary.html)

