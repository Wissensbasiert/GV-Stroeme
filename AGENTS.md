# Projektbezogene Arbeitsanweisung

## Verbindlicher Einstieg

1. Zuerst `README.md` und `docs/README.md` lesen.
2. Anschließend die dort für die Aufgabe genannte Leitdatei lesen.
3. Bei Skriptarbeiten zusätzlich `scripts/README.md` beachten.

## Autorität und Status

- Für den aktuellen Prüf- und Freigabestand ist `docs/qualitaet/QUALITÄTSSICHERUNGSPLAN.md` maßgeblich.
- Dateien unter `docs/roadmap/` beschreiben geplante Weiterentwicklungen; sie sind kein Nachweis einer erfolgten Umsetzung.
- Dateien unter `scripts/legacy/` sind historische Stände und dürfen nicht für aktuelle Daten- oder Frontend-Builds verwendet werden.
- Bei Widersprüchen zwischen Dokumentation und Daten zuerst die tatsächlichen Schemas, Metadaten und Quellwerte prüfen und den Widerspruch offen benennen.

## Änderungen

- Vor jeder Änderung den aktuellen Arbeitsstand prüfen und nicht zugehörige Änderungen erhalten.
- `index.html`, `css/style.css` und `js/app.js` werden generiert. Bearbeitbare Quellen liegen unter `html/`, `css/source/`, `js/source/` und `js/modules/`.
- Änderungen an Datenlogik, Bedienoberfläche oder Prüfverfahren in der zuständigen Dokumentation nachführen.
- Deutsche Texte, Umlaute, Sonderzeichen sowie Codes mit führenden Nullen UTF-8- und typensicher behandeln.
- Abhängigkeiten, Paket-Caches und große temporäre Dateien ausschließlich außerhalb des synchronisierten Projektordners unter `C:\tmp` anlegen.