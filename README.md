# Güterverkehrsströme Deutschland

Interaktives Fach-Dashboard von Wissensbasierte Planung zur Analyse räumlicher Güterverkehrsströme in Deutschland.

## Orientierung

- [`docs/README.md`](docs/README.md) ist das zentrale Inhaltsverzeichnis und ordnet Fachkonzept, Betrieb, Qualitätssicherung und Roadmaps ein.
- [`docs/betrieb/RELEASE_UND_GITHUB.md`](docs/betrieb/RELEASE_UND_GITHUB.md) beschreibt die GitHub-Sicherung auf `main`, die Übertragung geänderter Dateien und die Aufbewahrung von zwei Rückfallständen auf AlwaysData.
- [`scripts/README.md`](scripts/README.md) erklärt die aktiven Skripte und trennt sie von historischen Ständen.
- [`AGENTS.md`](AGENTS.md) enthält die projektbezogene Lese- und Arbeitsreihenfolge für KI-Assistenten.

## Lokal ansehen

Die Anwendung ist statisch und muss wegen der geladenen Datendateien über einen lokalen Webserver geöffnet werden. Danach ist sie unter der vom Server genannten lokalen Adresse erreichbar.

Die ausgelieferten Browserdateien werden aus den modularen Quellen erzeugt:

```powershell
node scripts/frontend/build_delivery_data.cjs
python scripts/frontend/build_frontend.py all
node scripts/frontend/serve_preview.cjs 8000
```

Die Vorschau ist unter `http://127.0.0.1:8000` erreichbar und wird mit Strg+C beendet. Der Server liest Dateien vom synchronisierten Laufwerk vor der Übertragung vollständig ein. Falls der Port belegt ist, einen anderen freien Port verwenden.

Die Terminalebene verwendet die versionierte Datei `data/processed/web_intermodal_terminals.geojson`. Nur bei einer Aktualisierung der lokal vorhandenen Terminal-Rohdatei ist zusätzlich `python -B scripts/frontend/build_terminal_data.py` auszuführen; für eine unveränderte Vorschau ist dieser Schritt nicht erforderlich.

Direkte Änderungen an `index.html`, `css/style.css` oder `js/app.js` sind zu vermeiden; maßgeblich sind die Quellen unter `html/`, `css/source/` und `js/source/` beziehungsweise `js/modules/` und `js/shared/`.

## Projektstruktur

| Bereich | Inhalt |
|---|---|
| `docs/` | Fachliche und technische Dokumentation, Qualitätssicherung und Roadmaps |
| `scripts/` | Datenaufbereitung, Frontend-Build, Prüfungen und Hilfsskripte |
| `data/raw/` | amtliche und weitere Ausgangsdaten |
| `data/processed/` | aufbereitete Daten für das Dashboard |
| `html/`, `css/source/`, `js/source/`, `js/modules/`, `js/shared/` | bearbeitbare Frontend-Quellen |
| `index.html`, `css/style.css`, `js/app.js` | generierte Browserdateien |
| `data_catalog.json` | maschinenlesbarer Datenkatalog |

Umfangreiche Rohdaten, lokale Sicherungen und Arbeitsergebnisse sind bewusst nicht Bestandteil der Git-Historie. Die große Prognosedatei `data/processed/web_forecast_2040.json` wird über Git Large File Storage (Git LFS) verwaltet.
Die abgeleiteten Browserpakete unter `data/processed/delivery/` sowie `web_summary_core.json` und `web_forecast_core.json` können vollständig aus den versionierten Ausgangspaketen erzeugt werden. Nach einer Wiederherstellung aus Git zuerst den oben genannten Datenpaket-Build ausführen; für die Prognose muss die Git-LFS-Datei lokal verfügbar sein.
