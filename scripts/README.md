# Skriptübersicht

Alle Befehle werden aus dem Projektstamm ausgeführt. Die Unterordner zeigen Zweck und Status der Skripte.

| Ordner | Zweck | Status |
|---|---|---|
| `pipelines/` | zentrale Aufbereitung der Ist-Daten, Prognose, Seeverkehrs- und Intermodaldaten | aktiv |
| `frontend/` | erzeugt die ausgelieferten HTML-, CSS- und JavaScript-Dateien aus den modularen Quellen | aktiv |
| `validation/` | automatisierte fachliche und technische Prüfungen | aktiv |
| `geodata/` | Aufbau und Aufbereitung räumlicher Grundlagen | aktiv bei Geodatenänderungen |
| `toll/` | Aufbereitung des Mautdatenmoduls | aktiv für dieses Modul |
| `utilities/` | gezielte Ergänzungs- und Wartungsschritte | nur nach Anleitung einsetzen |
| `examples/` | nachvollziehbare Abfragebeispiele, keine Produktionspipeline | Beispiel |
| `legacy/` | abgelöste Bundler und frühere Varianten | historisch, nicht für aktuelle Builds verwenden |

## Zentrale Aufrufe

```powershell
python scripts/pipelines/pipeline_phase2_aggregations.py
python scripts/pipelines/build_web_data_bundle_v5.py
python scripts/pipelines/build_intermodal_data.py
python scripts/pipelines/build_maritime_port_profiles.py
python scripts/pipelines/pipeline_vp2040.py
python scripts/frontend/build_frontend.py all
```

Welche Reihenfolge und welche Prüfungen für eine konkrete Datenaktualisierung gelten, steht verbindlich in [`../docs/betrieb/ANLEITUNG_DATENAKTUALISIERUNG.md`](../docs/betrieb/ANLEITUNG_DATENAKTUALISIERUNG.md). Der dokumentierte Prüfstand steht in [`../docs/qualitaet/QUALITÄTSSICHERUNGSPLAN.md`](../docs/qualitaet/QUALITÄTSSICHERUNGSPLAN.md).

## Regeln für die Verwendung

- Aktuelle Datenpakete ausschließlich mit den dokumentierten Skripten unter `pipelines/` erzeugen.
- Vor einer Freigabe die passenden Prüfungen unter `validation/` ausführen.
- Dateien unter `legacy/` nicht in automatisierte Abläufe aufnehmen. Sie bleiben nur zur Nachvollziehbarkeit früherer Entwicklungsstände erhalten.
- Generierte Browserdateien nicht direkt pflegen; Änderungen erfolgen in den modularen Frontend-Quellen und werden anschließend mit dem Frontend-Build zusammengesetzt.
- Keine Paketumgebungen, Caches oder großen temporären Dateien im Projektordner anlegen.