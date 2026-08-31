# Pflege der Weboberfläche

> **Pflichtlektüre vor jeder Datenänderung – auch für KI-Systeme:**
> [`ANLEITUNG_DATENAKTUALISIERUNG.md`](ANLEITUNG_DATENAKTUALISIERUNG.md) und
> [`QUALITÄTSSICHERUNGSPLAN.md`](QUALITÄTSSICHERUNGSPLAN.md). Beide Dokumente
> müssen vor Änderungen an Rohdaten, Berechnungen, Umstiegsschlüsseln oder
> Dashboard-Ausgaben gelesen und gemeinsam fortgeschrieben werden.

Die fachliche Aktualisierung der Rohdaten und die dazugehörigen Prüfungen sind
getrennt von der Weboberfläche in
[`ANLEITUNG_DATENAKTUALISIERUNG.md`](ANLEITUNG_DATENAKTUALISIERUNG.md)
dokumentiert.

Die ausgelieferten Dateien `index.html`, `css/style.css` und `js/app.js` werden
aus kleineren Quell-Dateien erzeugt. Bitte Änderungen in diesen Quellen
vornehmen und danach den folgenden Befehl ausführen:

`python scripts/build_frontend.py all`

Wichtige Zuordnung:

- `js/modules/maritime.js`: Seeverkehr und Häfen
- `js/modules/forecast.js`: Verkehrsprognose 2040
- `html/modules/`: sichtbare Analysebereiche
- `css/source/`: Basis, Komponenten, Fachmodule und responsive Darstellung

`js/app.js`, `index.html` und `css/style.css` bleiben die Dateien, die der
Webserver ausliefert. Sie werden nicht direkt gepflegt.

Die Sicherung vor dieser Umstellung liegt unter
`backups/before-modular-refactor-20260819-0100/`. Sie enthält die damals
ausgelieferten Fassungen von Oberfläche, Styles, Logik und den drei nun
nachgeladenen Fachdaten-Dateien.
