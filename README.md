# Güterverkehrsströme Deutschland

Interaktives Fach-Dashboard von Wissensbasierte Planung zur Analyse räumlicher Güterverkehrsströme in Deutschland.

## Orientierung

- [`docs/README.md`](docs/README.md) ist das zentrale Inhaltsverzeichnis und ordnet Fachkonzept, Betrieb, Qualitätssicherung und Roadmaps ein.
- [`scripts/README.md`](scripts/README.md) erklärt die aktiven Skripte und trennt sie von historischen Ständen.
- [`AGENTS.md`](AGENTS.md) enthält die projektbezogene Lese- und Arbeitsreihenfolge für KI-Assistenten.

## Lokal ansehen

Die Anwendung ist statisch und muss wegen der geladenen Datendateien über einen lokalen Webserver geöffnet werden. Danach ist sie unter der vom Server genannten lokalen Adresse erreichbar.

Die ausgelieferten Browserdateien werden aus den modularen Quellen erzeugt:

```powershell
python scripts/frontend/build_frontend.py all
```

Direkte Änderungen an `index.html`, `css/style.css` oder `js/app.js` sind zu vermeiden; maßgeblich sind die Quellen unter `html/`, `css/source/` und `js/source/` beziehungsweise `js/modules/`.

## Projektstruktur

| Bereich | Inhalt |
|---|---|
| `docs/` | Fachliche und technische Dokumentation, Qualitätssicherung und Roadmaps |
| `scripts/` | Datenaufbereitung, Frontend-Build, Prüfungen und Hilfsskripte |
| `data/raw/` | amtliche und weitere Ausgangsdaten |
| `data/processed/` | aufbereitete Daten für das Dashboard |
| `html/`, `css/source/`, `js/source/`, `js/modules/` | bearbeitbare Frontend-Quellen |
| `index.html`, `css/style.css`, `js/app.js` | generierte Browserdateien |
| `data_catalog.json` | maschinenlesbarer Datenkatalog |

Umfangreiche Rohdaten, lokale Sicherungen und Arbeitsergebnisse sind bewusst nicht Bestandteil der Git-Historie. Die große Prognosedatei `data/processed/web_forecast_2040.json` wird über Git Large File Storage (Git LFS) verwaltet.