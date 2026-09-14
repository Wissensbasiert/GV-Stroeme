# Allgemeine Gesprächskorrekturen vom 11.09.2026

## Fehlerursachen und Regeln

Die bisherige Mehrjahreserkennung traf wegen zu breiter Wortmuster sowohl „letztes Jahr“ als auch „letzte Jahre“. Der signierte Gesprächsstand wurde zwar übertragen, aber die Fortsetzung erkannte im Wesentlichen nur Jahreszahlen und die Gegenrichtung. Andere Nachfragen wurden als neues Thema behandelt. Eine freie Jahreskorrektur konnte dadurch auf einen unvollständigen Plan treffen und erneut bereits genannte Angaben verlangen.

Version 0.2.2 unterscheidet Kalenderjahr, neuesten Datenjahrgang und mehrjährige Reihe. Das vorige Kalenderjahr wird aus der Serverzeit in Europe/Berlin ermittelt. Ein fehlendes Datenjahr wird nicht still ersetzt. Die bestätigten Parameter werden bei einer erkennbaren Anschlussfrage weitergeführt; neue Kennzahlen ergänzen oder ersetzen nur die ausdrücklich angesprochene Auswahl. Jahreskorrekturen und Gegenrichtung erhalten die übrige Auswahl. Ein eigenständiges neues Thema oder eine neue Verbindung übernimmt den alten Kontext nicht.

Die allgemeine Funktion `relation_overview` beantwortet gerichtete Jahresfragen nach Gütermenge, Verkehrsleistung und Güterarten. Ein begrenzter Scan des vorhandenen B01-Bestands liefert die Werte je Verkehrsträger, Kennzahl und C1–C7-Gruppe. Qualität und Fehlwertbehandlung werden gegen die vorhandene B01-Einzelabfrage geprüft. Straßenrelationen haben keine Güteraufteilung. Gesamtwerte und Gruppen erscheinen in getrennten Tabellen, damit überlappende Mengen nicht als additive Zeilen erscheinen. Bei einer Datenjahreslücke wird eine passende Jahresalternative tatsächlich abgefragt, bevor sie angeboten wird.

Die beiden vom Nutzer benannten technischen Sätze wurden aus dem KI-Infofenster entfernt. Die Beschreibung der Datengrundlage bleibt erhalten.

## Wiederholbare Prüfung

`tests/analyseassistent/test_conversation_regression.py` prüft den gemeldeten Vier-Schritte-Dialog sowie Varianten für Hamburg → Berlin, Duisburg → Köln und Rosenheim → Augsburg. Hinzu kommen regionale Kennzahlwechsel, neue Themen ohne Kontextübernahme, Singular/Plural der Jahresbegriffe und der Abgleich von Werten und Qualitätskennzeichen mit der bestehenden Datenfunktion. Die Laufzeitprüfung bindet alle Testmodule mit Prüfsummen.

`scripts/validation/validate_assistant_followups.py --output <neuer Bericht>` führt den vollständigen gemeldeten Dialog mit realen Daten aus. `--requesty` erlaubt ausdrücklich vier echte Antwortaufrufe ohne Kundenbuchung. Referenzen werden erst nach der Antwort geprüft und nicht an das Modell gegeben. Der Browserprüfer akzeptiert diesen Bericht als optionales viertes Argument; er prüft den signierten Kontext im HTTP-Dialog sowie befüllte Mengen-, Leistungs- und Gütertabellen auf Desktop und Mobilgeräten.

Diese Prüfungen belegen allgemeine Regeln und mehrere Varianten. Sie sind keine Zusicherung, dass jede denkbare freie Formulierung oder jede fachliche Frage durch den vorhandenen Datenumfang beantwortbar ist.

## Prüfergebnis

Der abschließende Lauf `dialogue_beta06_validation01.json` besteht mit 90/90 lokalen Prüfungen. Zusätzlich bestehen neun gezielte Portalprüfungen. `followups_requesty_beta06_01.json` bestätigt alle vier Schritte mit dem tatsächlich konfigurierten Modell: Verbindung und Güterarten bleiben erhalten, die zweite Frage ergänzt Tonnenkilometer, die dritte behält das Kalenderjahr 2025 und die vierte wechselt ausschließlich auf 2024. Alle Antworten nutzen die geprüfte Sprachsynthese; keine Rückfrage und keine Kundenbuchung. Vier Modellaufrufe, 14.525 Tokens, laut Anbieter 0,014124825 USD; einschließlich eines vorangegangenen erfolgreichen Kandidatenlaufs acht Aufrufe und 0,02824965 USD.

13 Browserprüfungen am vollständigen Release bestehen. Die gespeicherten echten Modellantworten werden als lokale HTTP-Antworten eingesetzt, damit derselbe Wortlaut reproduzierbar bleibt. Bestätigt sind die Weitergabe des signierten Gesprächsstands, befüllte Mengen-/Leistungs-/Gütertabellen, Desktop- und Mobilansicht sowie das verkürzte Infofenster. Diese Browserprüfung verursacht keine weiteren Modellaufrufe und verwendet keine angemeldete Kundensitzung. Nachweise: `outputs/analyseassistent_runtime_20260911/` und `outputs/analyseassistent_dialogregeln_20260911/`.
