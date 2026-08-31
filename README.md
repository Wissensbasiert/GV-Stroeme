# Güterverkehrsströme Deutschland

Interaktives Fach-Dashboard von Wissensbasierte Planung zur Analyse räumlicher Güterverkehrsströme in Deutschland.

## Repository-Inhalt

Das Repository enthält die Browseranwendung, die Datenaufbereitung, Dokumentation sowie die für die lokale Darstellung benötigten verarbeiteten Webdaten. Umfangreiche Rohdaten, lokale Sicherungen und Arbeitsergebnisse sind bewusst nicht Bestandteil der Git-Historie.

Die große Prognosedatei `data/processed/web_forecast_2040.json` wird über Git Large File Storage (Git LFS) verwaltet.

## Lokal ansehen

Die Anwendung ist statisch. Sie muss wegen der geladenen Datendateien über einen lokalen Webserver geöffnet werden. Nach dem Start ist die Anwendung im Browser unter der vom Server genannten lokalen Adresse erreichbar.

Die erzeugten Browserdateien werden aus den modularen Quellen aufgebaut:

```powershell
python scripts/build_frontend.py all
```

Weitere Hinweise stehen in `HANDBUCH_SYSTEMDOKUMENTATION.md`, `README_MAINTENANCE.md` und `ANLEITUNG_DATENAKTUALISIERUNG.md`.
