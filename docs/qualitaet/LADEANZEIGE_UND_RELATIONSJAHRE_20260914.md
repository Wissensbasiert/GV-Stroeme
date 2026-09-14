# Ladeanzeige und Relationsjahrgänge: Testrelease vom 14.09.2026

Aktiv auf Testsite 1067000: `portal-test-20260914-gueterstroeme-loading01`. Ausgangspunkt war der frisch inventarisierte, vollständig rekonstruierte `air01`-Release. Unbeteiligte Portaldateien wurden unverändert übernommen. Die anderen lokalen Portaländerungen sind nicht Teil dieser Bereitstellung.

- GitHub-Implementierung: `3fccf37b22c0eeda7b588bc7323f54c3bd8ede53`, regulär auf `main` übertragen und entfernt bestätigt.
- Manifest: `70a74cfe9f1be4771316a3d1932fb5d346e132692450d700b027d4ec85da93f9`.
- Datenkennung unverändert: `039b9381b0645bb93f0dbd23`.
- 1.741 Dateien unabhängig serverseitig kopiert; acht geänderte Nutzdateien plus Manifest übertragen, insgesamt 1.266.256 Bytes. Alle 1.749 Zieldateien geprüft.
- API und Datenbank bereit; bestehende monatliche KitaNavigator-Aufgabe 30833 auf den neuen Release gebunden.

## Änderungen und Prüfung

Der Assistent erkennt vollständig fehlende Relationsjahrgänge anhand der vorhandenen Jahrgänge derselben Kennzahl. Für 2025 nennt er 2024 als neuesten verfügbaren Relationsjahrgang. Er ersetzt weder das angefragte Jahr noch fehlende Werte. Die bekannte London-Teilsumme von 994 Flügen bleibt gesondert erhalten. Flughafen-Infobox und Quellenfenster unterscheiden Gesamtwerte bis 2025 und Relationen bis 2024.

Die gemeinsame Ladeanzeige liegt mittig über der Karte und fügt keine Layoutzeile ein. 218 lokale Laufzeittests bestanden. Lokale Chrome-Prüfung bestätigt unveränderte Kartenposition und -größe sowie die Fehler-/Wiederholungsanzeige. Im angemeldeten Testportal wurden die korrigierte Flughafen-Infobox, das Laden der Prognose und der Ladehinweis bei Auswahl von Hamburg beobachtet.

Die abschließende Linux-Prüfung bestätigt sämtliche Release-Dateien, den neuen Jahrgangshinweis für Tonnen und Flüge, London-Summen und freigegebene Flughafen-Gesamtflugzahlen 2025 sowie bestehende Dialog-/Prognose-/Datenzugriffsregressionen. Keine externen Modellaufrufe und keine Kundenbuchung. Temporäre Serverprüfaufgabe, FTPS-Zugang und Statusdateien entfernt. Produktionsportal unverändert.

Lokale Nachweise: `outputs/loading_release_20260914_inventory.json`, `outputs/loading_release_20260914_base.json`, `outputs/loading_release_20260914_assembly.json`, `outputs/loading_release_20260914_deployment.log`, `outputs/loading_release_20260914_linux.json`.

## Aufbewahrung

Frische Inventur bestätigt `loading01` aktiv sowie `air01`, `nodes02` und `scope01` als vorhandene Rückfallstände. Der gebundene Plan sieht das Entfernen ausschließlich von `scope01` vor. Die automatische Freigabeprüfung lehnte die dauerhafte Löschung ab, weil der aktuelle Auftrag Push und Bereitstellung, aber keine Löschung autorisiert. Der Plan wurde nicht ausgeführt; es wurde kein Release entfernt. Bereitstellung und Server-/Browserabnahme sind abgeschlossen, die Reduktion auf zwei Rückfallstände bleibt bis zur ausdrücklichen Löschfreigabe offen. Nachweis: `outputs/loading_release_20260914_retention_plan.json`.
