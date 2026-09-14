# Analyseassistent: natürlicher Chat mit Datenwerkzeugen

## Auftrag und Änderung

Am 14.09.2026 beauftragt: Gesprächsablauf umbauen, mit einigen echten Modellaufrufen prüfen, ausschließlich im Testportal bereitstellen und auf GitHub sichern. Echte Requesty-Aufrufe sind ausdrücklich freigegeben. Keine Produktionsbereitstellung.

Version 0.3.0 verwendet native Requesty-Tools statt des separaten JSON-Planformats. Die vorhandenen Datenadapter und strengen Datenschemas bleiben erhalten; je Nutzereingabe wird höchstens eine zusammengehörige Datenfunktion ausgeführt. Zusammengesetzte Funktionen liefern mehrere Kennzahlen oder Verkehrsträger. Maximal zwei Modellaufrufe pro Eingabe; eine freie Rückfrage benötigt nur einen. Kein automatischer Reparaturaufruf.

Der signierte Zustand enthält höchstens acht begrenzte Gesprächsnachrichten, die bestätigte Auswahl und den Datenstand. Signatur und Ablaufzeit bleiben erhalten. Gesprächsverlauf unterstützt das Verständnis; konkrete Verkehrswerte werden erneut abgefragt. Neueste Jahrgänge werden anhand der tatsächlich gewählten Verkehrsträger bestimmt. Richtung und Bezugsjahr bleiben bei Anschlussfragen erhalten; neue Routen erben kein altes Jahr.

Das Modell formuliert frei mit deutschen Zahlen und internen Belegverweisen. Die Prüfung bezieht sich auf die jeweils zitierten Belege und kontrolliert Zahlen, Jahreszuordnung, Einheiten, Richtung sowie ausgewählte widersprüchliche Aussagen. Allgemeine Methodikerklärungen mit „weil“ und „deshalb“ sind zulässig. Die konkrete Ursache einer fehlenden Relationszeile darf nicht aus einer allgemeinen Stichprobenmethodik behauptet werden. Vollständige automatische semantische Faktensicherheit wird ausdrücklich nicht behauptet.

Die ursprünglichen Tabellen, Quellenzustände und notwendigen Qualitätshinweise bleiben serverseitig. Bei ungültiger Formulierung oder Modellfehler erscheint die geprüfte feste Antwort. Hinweise auf fehlende Zeilen und fehlende Jahrgänge werden im neuen Ablauf aus den einzelnen Fakten abgeleitet. Der neue Systemprompt ersetzt den langen Platzhaltervertrag im echten Modellbetrieb; die bisherige Implementierung bleibt für Offline-Regressionen erhalten.

## Oberfläche und Abschluss

Die vorhandene geschützte POST-Schnittstelle bietet SSE zusätzlich zum kompatiblen JSON-Ablauf. Fortschrittsmeldungen werden während des Frageverständnisses, Datenabrufs und der Antwortprüfung angezeigt. Erst geprüfte Absätze werden freigegeben; Modelltoken werden nicht ungeprüft durchgereicht. Der abschließende Ergebnisdatensatz folgt erst nach Kontingentabschluss. Ein Verbindungsabbruch löst keinen automatischen Neuaufruf aus. Die begrenzte Serverarbeit schließt ihre Reservierung auch bei getrenntem Browser ab.

Freitext unterstützt sichere Hervorhebungen und einfache Listen über DOM-Textknoten, ohne HTML-Ausführung oder externe Markdown-Bibliothek. Umfangreiche Tabellen sind aufklappbar. Im nativen Antwortmodus entfällt die zusätzliche formularartige Überschrift. Rückfragen und reine Datenlücken buchen keine fertige numerische Analyse.

## Prüfungen und Grenzen

Erster vollständiger isolierter Offline-Lauf: 104 Tests bestanden (`offline01.json`). Nachfolgende Änderungen erfordern einen neuen vollständigen Lauf. Neun gezielte Prüfungen einschließlich tatsächlicher Datenabfragen bestätigen inzwischen Jahresrückfrage, neuestes Schienenjahr 2025, Gegenrichtung und Jahreswechsel sowie Abwehr falscher Jahre/Einheiten/Richtungen, erfundener Zahlen, fremder Belege und unbelegter Datenlückenursachen. Der SSE-Test bestätigt Ergebnisfreigabe nach Buchung und Schutz vor doppelter Anfrage.

Eine Offline-Payloadprüfung bestätigte öffentliche KBA-/Destatis-Auszüge, Testfragen, Gebietsnamen, Verfügbarkeitskatalog und Fachregeln; keine lokalen Pfade, persönlichen E-Mail-Adressen oder Zugangsdaten im Modellinhalt. Übermittlung erfolgt über den bestehenden EU-Endpunkt `https://router.eu.requesty.ai/v1/chat/completions`, Modell `vertex/gemini-3.7-flash@eu`. Anbieteraufbewahrung wurde nicht neu geprüft.

Die echten Entwicklungsläufe und verworfenen Zwischenstände bleiben unter `outputs/analyseassistent_chat_20260914/` nachvollziehbar. `smoke01.json` zeigte eine fehlende Zustandsübernahme nach freier Rückfrage. `dialogue02.json` zeigte einen zu eng bestimmten neuesten Jahrgang, eine zusätzliche Jahresrückfrage und überstrenge Textprüfungen. Diese Fehler wurden korrigiert. `dialogue03.json` bestätigt 2025 Berlin → Hamburg mit 240.297 Tonnen, Gegenrichtung mit 585.052 Tonnen und Gegenrichtung 2024 mit 554.806 Tonnen; alle als Summe veröffentlichter Güterangaben. Die nachfolgende Lesekontrolle erkannte eine unbelegte Datenlückenursache. `focus04.json` bestätigt deren Korrektur für Dortmund → Bielefeld einschließlich Warum-Rückfrage sowie die richtige Erklärung einer fehlenden Binnenschiffsrelation. Die verbleibende unnötige Ablehnung einer belegten Jahresalternative wurde anschließend korrigiert.

Dies sind gezielte Stichproben, keine vollständige fachliche Abnahme aller freien Gespräche. Die bestehende Daten- und Fachgrenze des 45-Fälle-Katalogs bleibt erhalten.

## Abschluss am 14.09.2026

Der abschließende isolierte Lauf besteht mit **107 Tests, null Fehlern und null Fehlschlägen** (`offline_final.json`). Die gebundenen Quellprüfsummen stimmen mit dem bereitgestellten Laufzeitstand überein. JavaScript-Syntax und Diff-Format wurden geprüft. Die vier echten Entwicklungsläufe umfassen insgesamt 23 Eingaben, 42 Modellaufrufe und 186.789 gemeldete Tokens; gemeldete Kosten zusammen 0,180869865 USD. Darin sind verworfene Zwischenstände enthalten, spätere Portalaufrufe nicht. Es wurden keine Entwicklungsaufrufe auf Kundenkontingente gebucht.

Nach ausdrücklicher Anmeldung des Nutzers wurden vier Eingaben im echten Testportal durchgeführt:

| Eingabe | Beobachtetes Ergebnis | Kontingent |
|---|---|---|
| Welche Güter gehen per Schiene von Berlin nach Hamburg? | Natürliche Rückfrage nach dem Jahr | unverändert 12 von 50 |
| Das aktuellste Jahr | 2025; 240.297 Tonnen aus veröffentlichten Güterangaben, aufklappbare Gütertabelle | 13 von 50 |
| Und andersherum? | Hamburg → Berlin, 2025; 585.052 Tonnen; feste geprüfte Rückfallantwort | 14 von 50 |
| Und 2026? | Jahrgang nicht abgedeckt; keine Nullbehauptung; Alternative 2025 erst nach Bestätigung | unverändert 14 von 50 |

Fortschrittsmeldungen und gut lesbare Absätze wurden im Browser sichtbar geprüft. Zusätzlich wurde eine gespeicherte Dortmund–Bielefeld-Antwort mit dem tatsächlichen Client lokal dargestellt und die aufgeklappte Fünfjahrestabelle geprüft. Dies ist keine neue Prüfung sämtlicher Bildschirmgrößen. Der Rückfall bei der Gegenrichtung zeigt zugleich, dass freie Antworten weiterhin an der Prüfung scheitern können; die sachlich richtige Auswertung bleibt dann verfügbar.

Aktiver Testrelease: **`portal-test-20260914-gueterstroeme-chat01`**, Site **1067000**. Manifest SHA-256: `d456e81831af3b7c7509ce235ae2d07db93472d77f4b15292c8c69b7b49b8075`. Vollbestand: 1.707 Dateien, 668.188.576 Bytes. Gegenüber dem vollständig verifizierten beta06-Ausgangsrelease wurden 14 Nutzdateien plus Manifest mit 1.177.182 Bytes hochgeladen und 1.693 unveränderte Dateien unabhängig kopiert. Keine Hardlinks oder Überschreibung des vorherigen Release. API und Datenbank bereit; die monatliche KitaNavigator-Aufgabe zeigt auf den neuen Testrelease. Unbeteiligte Portaldateien sind nachweislich identisch zum Ausgangsrelease; vorhandene lokale Portaländerungen wurden nicht übernommen.

Die Linux-Nachprüfung (`linux_final02.json`) besteht: alle Manifestdateien, Datenabfragen, Migration 009, Kontingentpläne und Anmeldungskopplung geprüft. Keine externen Modellaufrufe oder Datenbankschreibvorgänge in dieser Prüfung. Eine erste Ausführung (`linux_final.json`) scheiterte an einer veralteten Textassertion zum Rosenheim–Augsburg-Hinweis. Der Prüfer kontrolliert nun die fachlichen Werte direkt: 2.175 und 1.066 Tonnen, 50,99 Prozent Rückgang, fehlende Straßen-/Binnenschiffswerte bleiben leer. Die Laufzeit musste dafür nicht verändert werden. Temporäre Serveraufgabe, FTPS-Zugang, Status- und Sperrdateien wurden entfernt.

Unauthentifizierte Zugriffsprüfung: Health 200, Kontingent 401, geschütztes JavaScript 403, privater Systemprompt 404 (`public_access.json`). Produktionsportal unverändert.

Nach zusätzlicher ausdrücklicher Nutzerfreigabe wurden ausschließlich `portal-test-20260910-gueterstroeme-ui10` und `portal-test-20260911-gueterstroeme-beta03` entfernt. Die Aufbewahrungsprüfung bestätigt genau drei Releases: chat01 aktiv, beta06 und beta04 als Rückfallstände. Alle 5.119 Dateien dieser drei Bestände wurden gegen ihre Manifeste geprüft; aktive Site und Produktion unverändert, Health bestanden und temporärer FTPS-Zugang entfernt (`retention_result.json`).

Implementierung auf GitHub `main` verifiziert: `4c8ae3340f2067bc6b17574287b8c95dc1ddd6ee`, regulär als direkte Fortsetzung von `15654bf` übertragen. Der bestehende lokale Arbeitszweig heißt `codex/steckbrief-20260907`; der lokale Zweig `main` war veraltet und wurde nicht verwendet. Nachfolgende reine Dokumentationscommits können darüber liegen. Keine Portal-Quelländerung oder Veröffentlichung fremder lokaler Portaländerungen. Ausführliche Berichte und Release-Manifest liegen lokal unter `outputs/analyseassistent_chat_20260914/`; die wesentlichen Ergebnisse sind in diesem Git-Dokument festgehalten.
