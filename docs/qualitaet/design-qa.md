# Design-QA: minimalistisches Güterstrom-KI-Fenster

## Vergleichsgrundlage

- Visuelle Referenz: `D:/HiDrive/01_Projekte/WBP-Solutions/Tools/Güterströme/.codex-remote-attachments/01a057c2-1143-7883-97c1-3ecbde508182/12b186b0-12bd-4fc3-8b9c-68ea245a42e6/1-Photo-1.jpg`
- Browsergerenderte Umsetzung, mobile Startansicht: `outputs/ki-minimal-ui/implementation-mobile.png`
- Browsergerenderte Umsetzung, Desktop-Startansicht: `outputs/ki-minimal-ui/implementation-desktop.png`
- Weitere Zustände: `outputs/ki-minimal-ui/implementation-desktop-examples.png` und `outputs/ki-minimal-ui/implementation-desktop-conversation.png`
- Gemeinsames Vergleichsbild: `outputs/ki-minimal-ui/comparison-mobile.png`
- Referenz: 570 × 1272 Pixel; mobile Umsetzung: 800 × 900 Pixel bei 800 × 900 CSS-Pixeln und Device-Scale-Faktor 1; Desktop-Umsetzung: 1838 × 1272 Pixel bei 1838 × 1272 CSS-Pixeln und Device-Scale-Faktor 1.
- Für das gemeinsame Vergleichsbild wurden beide Aufnahmen proportional auf 900 Pixel Höhe normalisiert. Browserrahmen und dunkles ChatGPT-Thema der Referenz sind nicht Teil des zu übertragenden Produktdesigns.
- Geprüfter Zustand: leere Startansicht sowie geöffnete Beispielfragen und Prototyp-Gespräch nach dem Absenden.

## Vergleichsergebnis

Die Referenz dient als Hierarchie- und Dichtevorgabe, nicht als pixelgenaue Farb- oder Gerätevorlage. Die Umsetzung übernimmt die zentralen Merkmale: viel ruhige Fläche, eine einzige Leitfrage, ein dominantes Eingabefeld, einen sekundären Hilfeknopf und erst bei Bedarf eingeblendete Beispiele. WBP-Branding und der zurückhaltende Prototyphinweis bleiben erhalten; eine sichtbare Bindung an die aktuelle Dashboard-Auswahl wurde entfernt, weil alle Filterkombinationen abfragbar sein sollen.

### Geprüfte Qualitätsflächen

- **Typografie:** Inter bleibt konsistent mit dem Tool. Überschrift, Eingabe, Hilfeknopf und Kleinhinweis bilden eine klare, ruhige Hierarchie; keine ungewollten Umbrüche im Desktop- oder Mobilzustand.
- **Abstände und Rhythmus:** großzügige zentrale Freifläche, 660-Pixel-Eingabebreite auf Desktop, gleichmäßige vertikale Staffelung und ausreichend Randabstand auf 800 Pixel Breite.
- **Farben und Tokens:** helle WBP-Oberflächen, Primärgrün `#63B472`, Akzent `#4C7F83`, zurückhaltende Schatten und feine Grenzen. Die dunkle Referenz wurde bewusst nicht kopiert.
- **Bild- und Assetqualität:** Das vorhandene SVG-Zeichen `gueterstrom-ki-mark.svg` wird unverändert und scharf ausschließlich im Kopf verwendet. Das zusätzliche Zeichen in der Startfläche wurde zugunsten der Ruhe entfernt.
- **Text und Inhalt:** Die Leitfrage ist fachlich auf Güterverkehrsströme zugeschnitten. Beispielfragen bleiben vollständig verborgen, bis „Was kann ich fragen?“ geöffnet wird. Die Überschrift lautet nur noch „Beispielfragen“, und die Verkehrsrelationsfrage verwendet Berlin als konkretes Beispiel. Der Prototyphinweis ist sichtbar, aber visuell nachgeordnet.

## Interaktionsprüfung

- KI-Fenster öffnen und Eingabefokus: bestanden.
- „Was kann ich fragen?“ öffnen und schließen: bestanden.
- Beispielfrage auswählen: bestanden; die Frage wird nur in die Eingabe übernommen und nicht automatisch abgesendet.
- Frage mit dem Senden-Knopf absenden: bestanden; die Startfläche wechselt in die bestehende Prototyp-Gesprächsansicht.
- Klassischer Rechtspfeil im Senden-Knopf: bestanden.
- Desktop- und Mobilansicht: bestanden.
- Browserkonsole nach den geprüften Interaktionen: keine Fehler.

## Findings

Keine offenen P0-, P1- oder P2-Abweichungen. Die verbleibende Kopfzeile ordnet den Dialog eindeutig dem Güterströme-Tool zu, ohne die minimalistische Kernhierarchie zu beeinträchtigen.

## Vergleichshistorie

- Erster vollständiger Vergleich: keine P0-/P1-/P2-Befunde; daher war keine visuelle Korrekturschleife erforderlich.
- Zweiter Vergleich nach den Browseranmerkungen: Badge, Startlogo, Kontextzeile und Unterzeile entfernt; Hilfetext und Pfeil konkretisiert. Desktop-, Mobil- und Gesprächszustand erneut ohne P0-/P1-/P2-Befund geprüft.

## Follow-up-Polish

- P3: Sobald eine echte Datenabfrage angeschlossen wird, kann der derzeitige Prototyphinweis durch eine reguläre Quellen- und Datenschutzhilfe ersetzt werden.

final result: passed
