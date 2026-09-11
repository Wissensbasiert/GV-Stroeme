# Analyseassistent: lokaler Pilot und Übergabe an das Testportal

**Nachtrag 11.09.2026:** Der neue Gesprächsablauf, der echte begrenzte Vergleich und die Browserabnahme sind im [Beta-Prüfbericht](../qualitaet/ANALYSEASSISTENT_BETA_20260911.md) dokumentiert. Der Client verwendet künftig `conversation` als serverseitig signierten Stand; `history` bleibt für ältere Clients verfügbar. Ausgangsfrage, bestätigte Auswahl und offene Rückfrage sind getrennt; frühere Zahlen werden erneut abgefragt. Gültigkeit zwei Stunden und Bindung an den Datenstand. Bei Schlüsselwechsel oder Neustart einer rein lokalen Laufzeit kann ein neuer Chat erforderlich sein. Die folgenden ui10-Abschnitte dokumentieren den Vorgänger.

Stand: 11.09.2026. Release `portal-test-20260911-gueterstroeme-beta03` ist auf AlwaysData-Testsite 1067000 aktiv und gemäß Beta-Prüfbericht geprüft. Die lokale Version 0.2.1 ergänzt darauf aufbauend die Mehrjahresrelation, analytische Kernaussagen und rechnerische Veränderungen der veröffentlichten Werte; sie ist noch nicht neu bereitgestellt. Keine Produktionsfreigabe oder fachliche Gesamtabnahme aller freien Fragen.

## Im Testportal verwenden

1. Im Testportal anmelden und unter „Meine Tools“ das Werkzeug „Güterströme“ öffnen.
2. Oben „KI fragen“ wählen. Das Fragefeld zeigt das verfügbare Monatskontingent.
3. Die Frage frei eingeben; Kartenfilter werden nicht übernommen. Seit Update ui10 reichen bei Rückfragen kurze Ergänzungen im selben Chat, etwa „2024“ oder „das aktuellste Jahr“. Die Jahresrückfrage bietet einen belegten neuesten Jahrgang an. Bei allgemeinen Güterfragen werden Richtung aus „von … nach …“, verfügbare Güterarten und Mengen in Tonnen abgeleitet. Das Eingabefeld wird beim Absenden geleert; eine Arbeitsanzeige zeigt die laufende Auswertung.
4. Eine erfolgreiche numerische Auswertung zählt einmal; Rückfragen und Fehler zählen nicht. Folgefragen und Jahresvorschläge werden erst nach ausdrücklichem Absenden ausgeführt. „Neuer Chat“ beginnt ohne bisherigen Verlauf; Neuladen der Seite ebenfalls. Das Kontingent bleibt erhalten.

Der erste gemeinsame Browsertest ergab 67.757 Tonnen für die Straßenverbindung Köln → Hamburg 2024 und änderte den Zähler von 0/50 auf 1/50. Der Wert ist laut Quelle eingeschränkt belastbar. Das ist ein Nachweis des konkreten Ablaufs, keine Freigabe beliebiger Fragen. Nachstehende Fortschrittsabschnitte dokumentieren zum Teil frühere Stände; für den aktuellen Release und die Restpunkte gilt der neueste Nachtrag im Qualitätssicherungsplan.

## Was bereits ausführbar ist

`server/analyseassistent/` verbindet 25 ausdrücklich begrenzte Funktionen mit den aktivierten B01–B06-Beständen und dem neuen Berliner B07-Abbild. Die vorhandenen B01–B06-Programme wurden nicht verändert. Beim Start werden Datenartefakte, Prüfberichte, Abhängigkeiten und die im jeweiligen Manifest gebundenen Programme anhand ihrer Prüfsummen geprüft. Der Prozess hält diese Versionen fest; ein geänderter Aktivierungsverweis erfordert einen neuen Start.

Die Funktionen umfassen exakte Relationen, Regionsvergleich, Regionsverbünde, Monatsreihen, Schienen-Feinpositionen, nationale Verkehrsbeziehungen, Saldo, VP-Ranking, Knotenpartner, Knotenkennzahlen, KBA-Details und gespeicherte Mautmonate. Zusammengesetzte Profile, regionale Güter-/KV-Auswertungen und die 45 Eingabeverträge sind ergänzt. Ein Ist-Änderungsranking mit belastbar bestätigter Quellenvergleichbarkeit (T13) bleibt offen; die bloße Vorbereitung einer Testfrage belegt keine verfügbare Fachfunktion.

Bei strukturiert bestätigten Filtern ist keine Modellzuordnung nötig. Freie Fragen verwenden einen begrenzten Planaufruf. Der Server prüft erlaubte Parameter, deren Herkunft und ausdrücklich erkennbare Widersprüche. Unbelegte oder widersprüchliche Zuordnungen führen zur Rückfrage. Die konservative Namenserkennung kann zusätzliche Bestätigungen benötigen; sie ist noch keine vollständige deutschsprachige Ortsauflösung.

Tabellen und analytische Rückfallfassungen werden aus den Abfragewerten erzeugt. Lokal formuliert ein optionaler zweiter Modellaufruf aus belegten Einzelwerten und geprüften Vergleichsaussagen einen kurzen Antworttext. Jeder Absatz nennt seine Aussagekennungen; neue Zahlen werden verworfen. Ungültige Formulierungen oder ein Modellfehler ersetzen keine Fakten, Pflichtangaben oder Tabellen. Tabellen mit mehr als acht Werten sind in der Oberfläche zunächst eingeklappt. `FACHREGELN.json` liegt lokal in Version 0.2.0 vor; der aktive Testrelease verwendet noch 0.1.0.

## Requesty und sichere lokale Schlüsselablage

Einrichtung durch `scripts/analysis/configure_requesty.ps1`. Das Windows-Eingabefenster nimmt den Schlüssel verdeckt entgegen. Die Datei `key.dpapi` wird mit Windows DPAPI für das aktuelle Benutzerkonto verschlüsselt. Die nicht geheime `config.json` enthält Modellkennung und technische Einstellungen. Beide liegen unter `%LOCALAPPDATA%\WBP-Solutions\Gueterstroeme\Requesty`; die Ordnerrechte werden auf das aktuelle Windows-Konto und SYSTEM begrenzt. Keine Kopie im Projekt oder Übergabepaket, kein Schlüssel in Modellkontext oder Prüfbericht.

Am 10.09.2026 wurden das Einlesen der verschlüsselten Konfiguration und die Modellverfügbarkeit durch `GET /models` am EU-Endpunkt bestätigt. Eingetragen ist `vertex/gemini-3.7-flash@eu`. Es wurden dabei keine Fachfragen versendet. Auf dem späteren AlwaysData-Server ist eine eigene geschützte Serverkonfiguration erforderlich; die Windows-DPAPI-Datei ist kein Servergeheimnisformat.

Die Implementierung verwendet `https://router.eu.requesty.ai/v1`, folgt dem dokumentierten [Requesty-EU-Routing](https://docs.requesty.ai/features/eu-routing) und den [strukturierten Ausgaben](https://docs.requesty.ai/features/structured-outputs). Planantworten werden als JSON-Objekt angefordert und lokal streng geprüft, weil ihre Parameter je Funktion variieren. Die beleggebundene Antwortsynthese verwendet ein festes JSON-Schema. Ihre tatsächliche Kompatibilität und Laufzeit mit dem eingetragenen Modell muss nach Abschluss der lokalen Prüfungen erneut gebündelt getestet werden. Die in Requesty eingerichteten Datenschutz-/Aufbewahrungseinstellungen wurden nicht unabhängig geprüft.

Die anfängliche technische Testfrist von 180 Sekunden ist eine vorläufige Schutzgrenze, kein Leistungsversprechen. Sie umfasst beide Modellphasen und die Datenabfrage. Kein automatischer Wiederholungs- oder Reparaturaufruf. Die Zielantwortzeit wird erst nach echten Messungen festgelegt. Eine clientseitige Frist garantiert keinen Kostenstopp beim Anbieter.

## Ausführen und prüfen

Vorhandene lokale Laufzeit: Python 3.11, DuckDB 1.2.1 und jsonschema. Keine Installation von Abhängigkeiten im Projekt. Schreibzugriff auf `C:\tmp` ist für die kleinen temporären Testdatenbanken erforderlich. Bei verweigertem Zugriff die Tests nicht wiederholt im selben gesperrten Kontext starten.

```powershell
python -B scripts/validation/validate_assistant_runtime.py --output outputs/analyseassistent_runtime_20260910/validation.json
python -B scripts/analysis/prepare_assistant_cases.py
python -B scripts/analysis/run_assistant.py --catalog-check --output outputs/analyseassistent_runtime_20260910/catalog_readiness.json
python -B scripts/analysis/run_assistant_catalog.py --output outputs/analyseassistent_runtime_20260910/NEUER-VORLAUF
```

Eine lokale Einzelabfrage liest eine JSON-Datei mit `question`, `confirmed` und optional `function`. `function` kennzeichnet eine ausdrückliche strukturierte Funktionsauswahl. Ohne Modell steht für eine freie Frage keine automatische Zuordnung zur Verfügung.

```powershell
python -B scripts/analysis/run_assistant.py --input scripts/examples/assistant_balance.json --output outputs/analyseassistent_runtime_20260910/balance.json
```

Der optionale Schalter `--requesty` liest die verschlüsselte lokale Konfiguration und sendet tatsächlich Modellanfragen. Er gehört nicht zu den Offlineprüfungen. Gemäß Roadmap wird der nächste fachliche Modelllauf gebündelt über die 45 Fälle vorbereitet; keine routinemäßigen Einzel-Modelltests ausführen.

`tests/analyseassistent/inputs.json` enthält alle 45 Fragen und die notwendigen Eingabehinweise. Die getrennte `references.json` enthält interne Prüferwartungen und wird vom Laufzeitprogramm nicht geladen. Sie ist kein vollständig neu freigegebener Referenzsatz. T22, T35 und T44 enthalten die bereits dokumentierten Korrekturen. 30 Adapterzuordnungen sind als prüfbare Ausgangspunkte vorbereitet, nicht als vollständig bestandene Fachfälle. Die Bereitschaftsprüfung blockiert einen als vollständig behaupteten Modelllauf, solange Fallverträge offen sind.

`run_assistant_catalog.py` führt ohne `--requesty` nur die bereits zugeordneten strukturierten Datenabläufe aus und weist alle übrigen Fälle als nicht bereit aus. Mit `--requesty` ist der vollständige Lauf erst zulässig, wenn alle 45 Fallverträge ausdrücklich `ready` sind. Jeder Modellfall läuft in einem eigenen Prozess mit einer getrennten Eingabedatei; Ergebnis und verfügbare Verbrauchsdaten werden unverändert gesichert. Technisch abgeschlossene Antworten bleiben bis zur unabhängigen fachlichen Bewertung `pending_independent_review`. Der Runner kann keine fachliche Freigabe allein aus einem erfolgreichen HTTP-Aufruf ableiten.

Für echte lokale HTTP-Prüfungen steht `scripts/analysis/serve_assistant.py` bereit. Es bindet ausschließlich an `127.0.0.1`, verwendet ein künstliches Testkonto, legt einen zufälligen lokalen Zugangstoken unter dem ausdrücklich angegebenen `--state-dir` in `C:\tmp` ab und entfernt diesen beim regulären Beenden. Es ist kein Portalserver. Das Dashboard ist noch nicht mit diesem Endpunkt verbunden.

## B07: vorhandene Berliner Mautauszüge

`scripts/analysis/prepare_b07_local.py` prüft die vorhandenen 24 Dateien unter `data/raw/Straße/Lkw-Portal/Berlin`, ohne Netzwerkabruf. Monat, Richtung, Fokusgemeinde, AGS-Typ, Relationszahl, Eindeutigkeit und Fahrtenwerte werden geprüft. Die zwölf Binnenwerte stimmen jeweils zwischen Quelle und Ziel überein. Der aufbereitete Bestand enthält 23.685 Zeilen für August 2025 bis Juli 2026, AGS `11000000`.

Damit können veröffentlichte Start-/Ziel-/Binnenwerte und die eindeutige Zählung für T37 real geprüft werden. Kein Monat besitzt im lokalen Bestand denselben Vorjahresmonat. T38 erhält deshalb eine ausdrückliche Datenlücke; eine reale Vorjahresrate ist nicht abgenommen. Es wurden keine neuen externen Daten beschafft. Prüfumfang ist der vorhandene lokale Auszug, keine erneute Bestätigung der Vollständigkeit des externen Dienstes.

## Basic, Premium und Verbrauch

Neue Nutzervorgabe: Basic fünf, Premium 50 KI-Fragen je Kalendermonat. Basic besitzt damit einen KI-Zugang. Zuordnung und Zählung gelten je Portalidentität **und Werkzeug**, Monat nach Europe/Berlin. Ein Paketwechsel verändert das Limit, nicht rückwirkend die bereits gezählten Anfragen.

Der lokale SQLite-Prototyp `quota.py` reserviert vor der Verarbeitung atomar einen Platz. Eine abgeschlossene zahlenhaltige Analyse mit Status `ok` oder `partial` zählt einmal. Rückfragen, abgewiesene Fragen, reine Nichtverfügbarkeit und technische Fehler werden freigegeben. Eine wiederholte Anfragekennung löst keinen zweiten Modellaufruf aus; andere Inhalte unter derselben Kennung werden abgelehnt. Als technische Begrenzung werden höchstens 20 angenommene Anfragen je Minute und Testkonto zugelassen, einschließlich später freigegebener Versuche. Monatskontingent und technische Abrufbegrenzung sind getrennt.

Nach einem Prozessabsturz dürfen verbliebene Reservierungen erst nach Ende des betreffenden Workers freigegeben werden; die lokale Hilfsfunktion darf nicht laufende Anfragen entsperren. Die Produktentscheidung für abgeschlossene Antworten, die ausschließlich eine fachliche Grenze erläutern, ist bei der Erweiterung des Funktionsumfangs nachzuführen.

## Portalübergabe und offene Arbeiten

`integration/analyseassistent/portal_schema.sql` ist ein **nicht angewendeter** PostgreSQL-Entwurf. Identitäten, Werkzeuge, Pakete und Verbrauch sollen in der bestehenden Datenbank der jeweiligen Portalumgebung liegen. Fachliche Analysebestände bleiben in einem privaten Werkzeugverzeichnis. Eine zusätzliche AlwaysData-Datenbank wurde weder angelegt noch als erforderlich nachgewiesen.

`api.py` enthält den WSGI-Endpunkt mit einer injizierten serverseitigen Identitätsprüfung, Herkunftsprüfung, Eingabegrenzen und Kontingentbehandlung. Der echte Hanko-/Portalresolver, PostgreSQL-Transaktionen, Verwaltungsoberfläche und Frontendanschluss sind noch einzubinden und zu prüfen. Browserseitig übermittelte Benutzer- oder Paketfelder sind unzulässig. Die vorhandene Tableau-Lizenznotiz wird nicht umgedeutet.

```powershell
python -B scripts/analysis/build_assistant_release.py --output C:\tmp\gueterstroeme-assistant-NEUE-KENNUNG
```

Der Builder verlangt einen neuen Zielordner und prüft die Kopien per SHA-256. `public/` enthält die erlaubten Browserressourcen, `private/` Programme und gebundene Analysebestände. Kein Schlüssel, keine Nutzerdatei, keine Testreferenz und kein Rohdatenordner werden übernommen. Das Paket ist eine lokale Übergabe, kein vollständiger Portalrelease. Die Portalintegration erfolgt später über das maßgebliche Plattform-Repository `Plattform/Overhaul`, dessen Testbereitstellung bereits Planmodus, Healthcheck und Rückfall vorsieht.

Offen bleiben insbesondere die vollständigen Fallverträge/Funktionskombinationen, ein gebündelter echter 45-Fälle-Modelllauf, die fachliche Ergebnisabnahme, PostgreSQL-/Portalrechte, die sichtbare Benutzerverwaltung, die Dashboardverbindung sowie Browser- und Rückfallprüfung im Testportal. Kein Testdeployment und keine Produktionsänderung durchgeführt.

## Ergänzung: geprüfte Profilfunktionen (10.09.2026)

Der folgende Absatz dokumentiert die erste Erweiterung; maßgeblich für den jüngsten Stand ist der anschließende Abschnitt.

Regionsprofil, regionaler Modal Split und getrennter Ist-/VP-Vergleich sind jetzt ausführbar. Anteile setzen vollständige passende Nenner voraus; keine Rate verbindet Ist und Prognose. Aktueller Laufzeitnachweis: outputs/analyseassistent_runtime_20260910/profiles_validation_httpfix.json, 28/28 bestanden. Katalogvorlauf: preflight03/report.json, elf ausgeführte strukturierte Fälle und 34 offene Fallverträge, ohne Modellaufrufe. Die Windows-Unterprozesse des Runners starten ausdrücklich im UTF-8-Modus. Das vorherige Übergabepaket C:\tmp\gueterstroeme-assistant-20260910-pilot03 ist damit veraltet und muss vor einer späteren Übergabe neu gebaut werden.

## Ergänzung: Relations- und Jahresfunktionen (10.09.2026)

20 begrenzte Adapter, 21 zugeordnete Testfälle und 40/40 bestandene lokale Laufzeittests. Nachweis: `outputs/analyseassistent_runtime_20260910/relations_validation_verified.json`; Katalogvorlauf: `preflight04/report.json` mit 21 ausgeführten und 24 noch offenen Fällen, ohne Modellaufrufe. Adapterzuordnung und technische Ausführung sind weiterhin keine vollständige fachliche Fallfreigabe.

Partner-Ranking verwendet alle veröffentlichten Partner vor Top-Begrenzung, behält Ranggleichstände und Qualitätskennzeichen. Konkrete Relationen werden in beiden Richtungen je Verkehrsträger ausgegeben; fehlende Zeilen bleiben unbekannt. Die Profilfunktionen prüfen die Quellenjahresabdeckung: fehlende Straßenwerte 2025 ergeben keine Null und keinen vollständigen Modal Split. Knotenprofile wechseln bei fehlender Kennzahl nicht automatisch das Jahr. Die Ausgabe enthält jetzt Gütergruppen, nationale Verkehrsbeziehungen einschließlich Transit sowie vollständige Aussagekandidaten; eine optionale Modellauswahl bleibt auf vier belegte Aussagen begrenzt und erhält die ursprüngliche Frage samt geprüften Parametern.

Für die lokalen Testeingaben sind B07 Berlin Juli 2026 beziehungsweise der angefragte Vorjahresmonat Juli 2025 und die Inlandspopulation I für T40/T41 ausdrücklich gesetzt. Das sind Testauswahlen, keine automatischen Produktstandards. T38 bleibt ohne verfügbares Vorjahresmonatspaar; der vollständige gewünschte Relationsvergleich ist damit nicht abgenommen.

Vor dem gebündelten Modelltest fehlen weitere Fallverträge und Funktionen, insbesondere regionale Güterstruktur je Verkehrsträger, KV-Teilmärkte und Quellen-/Machbarkeitserklärungen. Die ergänzenden modebezogenen D01-Güterfelder liegen im Originalprofil, aber noch nicht im gebundenen privaten Datenabbild. Weiterhin kein Portal-/PostgreSQL-Anschluss und kein Testdeployment; vorhandenes Übergabepaket vor einer Übergabe neu bauen.

## Ergänzung: Güter-/KV-Abbild und Quellenhinweise (10.09.2026)

Der vorherige Absatz beschreibt den inzwischen überholten Zwischenstand dieser drei Funktionen. Jetzt sind 23 begrenzte Adapter und 30 Katalogzuordnungen vorbereitet; 48/48 lokale Laufzeittests bestehen (`outputs/analyseassistent_runtime_20260910/support_validation01.json`). Der Katalogvorlauf `preflight05/report.json` führt 30 Fälle aus und lässt 15 offen, ohne Modellaufrufe oder fachliche Gesamtfreigabe.

Das zusätzliche private Paket unter `data/analysis/assistant_support/` enthält modebezogene D01-Güterprofile und neu aus gebundenen Rohquellen berechnete KV-Kennwerte. Aufbau mit `python -X utf8 -B scripts/analysis/prepare_assistant_support.py`. Der Builder verlangt unveränderte Quellen und legt einen neuen unveränderlichen Datenstand an; vorhandene Releases werden nicht überschrieben. Aktiver Stand: `f8f8949c0654f9a42d4e5e94`, 3.984 Güterprofile und 34.270 KV-Kennwertdatensätze. Die Anwendung prüft das Paket wie die anderen Datenstände, einschließlich seiner Abhängigkeiten.

Externer KV-Versand und -Empfang erfordern bekannte Gegenräume. Unterschiede zur bisherigen Dashboardbehandlung unbekannter Zielräume sind betragsgenau im Paketprüfbericht dokumentiert. Schiene und Binnenschiff bleiben getrennt, fehlende Werte beziehungsweise Monate sperren vollständige Nenner. Regionale Straßen-Güterstruktur bleibt C1–C7 mit den bisherigen D01-Qualitätsgrenzen. Quellen-/Klassifikationshinweise besitzen belegte Texttabellen; solche Antworten erfinden keine numerischen Verkehrsangaben und ändern die vereinbarte Zählregel für zahlenhaltige Analysen nicht.

Die verbliebenen Fälle sind vor dem gebündelten Requesty-Test als kombinierte Abfrage, notwendige Rückfrage oder konkrete Datengrenze festzulegen und gegen ihre getrennten Referenzen zu prüfen. Portal-/PostgreSQL-Anschluss, Benutzerverwaltung, Browserintegration und Testbereitstellung bleiben offen. Das alte lokale Übergabepaket enthält das neue Support-Paket nicht; vor einer späteren Übergabe neu bauen.

## Ergänzung: echter Requesty-Test und aktueller Arbeitsstand (10.09.2026)

Die vorherigen Abschnitte dokumentieren Zwischenstände. Jetzt sind 25 begrenzte Adapter und alle 45 Modelleingaben vorbereitet: 32 konkrete Datenfälle, 13 Rückfragefälle. Der vereinbarte vollständige Requesty-Lauf ist erfolgt, mit geladenem Systemprompt und getrennten Sollreferenzen. Bericht: `outputs/analyseassistent_runtime_20260910/requesty45_run01/report.json`; nachgelagerter Vergleich: `requesty45_review02.json`. 75 Modellaufrufe, 42 bestandene Ablauf-/Datenkontrollen und drei Befunde. Keine vollständige fachliche Abnahme.

T30 und T44 wurden nach Präzisierung des Prompts gezielt erneut geprüft; drei zusätzliche Aufrufe und beide Kontrollen bestanden (`requesty_targeted02/review.json`). Die erste Ausgabe bleibt unverändert. Aktuelle lokale Laufzeitprüfung: 54/54 Tests (`post_requesty_validation01.json`). T13-Funktion, Ländernamen in T35, Gebietsnachweis in T43 und Prüfung aller Kurzfassungen bleiben offen. Eine erfolgreiche Rückfrage ist noch keine vollständige Antwort auf einen zuvor unvollständigen Fall.

Der Schlüssel liegt weiterhin außerhalb des Projekts verschlüsselt unter dem lokalen Windows-Benutzerprofil; er wird nicht in Ausgaben, Git oder Übergabepakete kopiert. Die vorhandene Konfiguration wurde erfolgreich verwendet. Für diesen Stand wurden keine Modellkennungen oder Schlüssel erneut angefordert. Der echte Lauf lädt die Konfiguration nur im Arbeitsspeicher.

Vor einem zukünftigen vollständigen Modelllauf muss `prepare_assistant_gate.py` eine neue Freigabedatei aus aktuellen bestandenen Tests, Eingaben, Referenzen und Datenstand erzeugen. Der vorhandene `model_gate01.json` bindet den Stand vor der letzten Korrektur und ist daher kein Freibrief für spätere Änderungen. `run_assistant_catalog.py --requesty --gate <Datei> --output <neuer Ordner>` prüft die Bindung. `review_assistant_catalog.py --live <Laufordner> --baseline <lokaler Vergleich> --output <neue JSON-Datei>` bewertet erst danach und hat keinen Providerzugriff. Ein neuer vollständiger Lauf ist nach den gezielten Nachprüfungen nicht allein zur Wiederholung erforderlich.

`integration/analyseassistent/postgres_quota.py` ergänzt den Schemaentwurf um den vorgesehenen Adapter für Basic 5/Premium 50, Transaktionen und Reservierungen. Noch keine echte PostgreSQL-Prüfung oder Einbindung in das Portal. Als Nächstes folgen Datenbankprüfung und Hanko-/Werkzeugrechte im maßgeblichen Plattform-Repository, Administration und Dashboardverbindung, danach Paketierung und Prüfung des vollständigen Testreleases. Das alte lokale Übergabepaket ist weiterhin veraltet; es wurde weder auf Test noch Produktion installiert.

**Abschließende Freigabeprüfung:** `outputs/analyseassistent_runtime_20260910/post_requesty_validation02.json`, 55/55 lokale Tests bestanden. Die gebundene Dateiliste umfasst jetzt ausdrücklich Systemprompt, Fachregeln, Laufzeitprogramme, Testtreiber und Freigabeprüfer. Fehlende Promptbindung und geänderter Prompthash werden abgelehnt; der Runner prüft zusätzlich den Referenzhash. Bereits vorhandene Gate-Ausgabedateien werden vor einer Änderung der Eingaben abgelehnt. Diese Nachprüfung erzeugt keinen weiteren Modellaufruf und keine neue fachliche Freigabe. Ältere Gate-Dateien bleiben historische Nachweise.

## Antworten lesen und Stand der Kontingentprüfung (10.09.2026)

Die vollständige lesbare Übersicht liegt unter `outputs/analyseassistent_runtime_20260910/lesebericht01/index.html`. Sie kann direkt als lokale HTML-Datei geöffnet werden; Suche, Aufklappen und Druckknopf benötigen keine KI. `ANTWORTEN_TESTFRAGEN.md` daneben ist die zusätzliche Textfassung. T30 und T44 enthalten im HTML auch ihre ursprünglichen Antworten. 78 Modellaufrufe sind protokolliert; die vom Nutzer aus Requesty gemeldeten Gesamtkosten betragen 0,51 USD. Diese Anzeige ist keine erneute fachliche Freigabe.

Der PostgreSQL-Adapter wurde inzwischen gegen eine eigene kurzlebige lokale PostgreSQL-13.3-Instanz geprüft. Neun Tests bestanden (`postgres_validation02.json`); aktueller Portal-Migrationssatz, künstliche Konten und Treiber psycopg 3.2.10. Instanz und Daten danach entfernt. Keine tatsächliche Portal-Datenbank angesprochen. Die noch offene Arbeit ist der Anschluss an Hanko, Werkzeugrouting, Administration und Dashboard sowie die Abnahme im tatsächlichen Testportal.

### Verständliche Antworten und Folgefragen (10.09.2026)

Die Laufzeitausgabe enthält unter `answer` Titel, Absätze, konkrete Rückfragen, Tabellen und fachliche Hinweise. Technische Nachweise bleiben separat verfügbar. Bei fehlender Güteraufteilung einer Straßenverbindung werden passende Alternativen mit höchstens vier lokalen Datenabfragen und fünf Sekunden innerhalb der Anfragefrist geprüft. Vorgeschlagene Fragen erscheinen unter `answer.suggestions`, ihre Abfrageparameter und Belege unter `related_data`. Eine Verfügbarkeitsprüfung löst keinen Requesty-Aufruf aus und führt keine neue kostenpflichtige Analyse im Namen des Nutzers aus. Folgefragen sind in der Lesefassung Hinweise; die Portalbedienung ist noch nicht angeschlossen.

T20 in der bestehenden Lesefassung zeigt die überarbeitete Darstellung einschließlich geprüfter Schienen- und Regionalalternativen. Die Originalantworten des Modelltests bleiben unverändert erhalten. Anzeige aktualisieren: `python -X utf8 -B scripts/analysis/build_assistant_test_report.py --output outputs/analyseassistent_runtime_20260910/lesebericht01 --update`. Danach die lokale Browserseite neu laden. Neue Prüfung: `customer_portal_validation02.json`, 63 lokale Tests bestanden. Kein neuer Modelllauf oder Testdeployment.

### Paketverwaltung im tatsächlichen Portalcode (10.09.2026)

Im Plattform-Repository sind die API-Routen, die administrative Paketpflege und Migration 009 jetzt lokal integriert. Aktivierung erfordert ausdrücklich Testumgebung und `WBP_GUETERSTROEME_ENABLED=1`. Die Migration erzeugt den Werkzeugeintrag zunächst inaktiv. Im Verwaltungsbereich wird nach bestehender Werkzeugfreigabe das KI-Paket separat am Kundenkonto gewählt. Verbrauch und laufende Anfragen bleiben bei Paketwechseln erhalten. Keine neue Benutzerdatenbank und keine Kopie der Hanko-Identitäten.

Nachweise: `portal_integration_validation02.json` (47 Tests) und `postgres_portal_validation04.json` (14 echte lokale Datenbanktests). Reproduzierbarer Portalprüfer: `scripts/validation/validate_assistant_portal.py --portal <Plattformordner> --output <neuer Bericht>`. Noch keine echte Portalverbindung, Servermigration oder Umschaltung; private Datenpaketierung, Dashboardanschluss und Browserabnahme folgen.

### Analyseassistent: bedienbare Kundenoberfläche und zusammengesetzter Testrelease (10.09.2026)

Der Dashboarddialog verwendet jetzt die geschützte Portal-API. Kontingente stammen ausschließlich vom Server; der frühere Browserzähler ist nicht mehr eingebunden. Antworten zeigen verständliche Einordnung, Tabellen mit Einheiten und geprüfte Folgefragen; technische Angaben bleiben eingeklappt. Folgefragen werden vorbereitet und erst nach erneutem Absenden ausgeführt. Tabellen sind auf Mobilgeräten horizontal scrollbar. Rückfragen erhalten die ursprüngliche Frage. Verbindungsabbrüche lösen keine automatische Wiederholung aus; bei unklarem Abschluss ist erneutes Senden bis zum Neuladen gesperrt. Eine Wiederherstellung verlorener Antworten nach dem Neuladen ist noch nicht implementiert.

Der Kontext berücksichtigt nur die jeweilige Modulauswahl: Maut mit AGS und Monat, Flughäfen und Seehäfen mit Knoten und passender Einheit, Prognose ohne verborgenes Ist-Jahr. Fehlende Angaben werden nicht ergänzt. Erfolgreiche Antworten ohne einen einzigen bekannten Zahlenwert verbrauchen keine Kontingentfrage; bekannte Nullwerte bleiben echte Zahlenwerte.

Der Plattformbuilder übernimmt mit `--gueterstroeme-package` ein geprüftes Fachpaket ausschließlich in einen Testrelease. Öffentliche Dashboarddateien liegen hinter der Werkzeugberechtigung; Programme, Systemprompt und Analysebestand unter `private/gueterstroeme`. Leaflet und Chart.js werden lokal mitgeliefert. Linux-Laufzeit muss DuckDB 1.2.1 und jsonschema 4.25.1 unterstützen. Unveränderter Datenstand: `3652bb8234800abbd4327ef4`.

Nachweise unter `outputs/analyseassistent_runtime_20260910/`: `ui_runtime_validation05.json` (64 lokale Laufzeittests), `portal_ui_validation04.json` (49 Portal-/Releaseprüfungen), `postgres_portal_validation04.json` (14 echte lokale Datenbanktests). `browser_ui03/report.json` besteht neun Browserprüfungen des vollständigen ui03-Releases mit synthetischen HTTP-Antworten aus dem geprüften T20-Ergebnis; Desktop- und Mobilansicht gesichtet. Die spätere modulbezogene Kontextkorrektur besteht zehn separate Prüfungen in `validate_assistant_context.cjs`; deshalb ist ui03 kein aktueller Deploymentkandidat mehr. Für den abschließenden ui04-Release sind Manifest- und Browserprüfung erneut auszuführen.

AlwaysData wurde ausschließlich lesend geprüft. Bestätigt: Testsite 1067000, bestehende Portal-Datenbank und Hanko-Konfiguration, Python 3.13, separate Testlaufzeit `portal_test/.venv`, keine direkten statischen Sitepfade. Die ausdrückliche Testkennzeichnung und Requesty-Konfiguration fehlen noch. Maßgeblich ist `alwaysdata_readiness02.json`; die Datenbank-/Virtualenv-Felder in `alwaysdata_readiness01.json` wurden mit unpassenden Feldnamen geprüft und sind überholt. Planmodus des ui03-Releases erfolgreich; keine Dateien hochgeladen, keine Live-Migration, keine Rechteänderung und keine Umschaltung.

Offen bleiben aktuelle Paketprüfung, Linux-Laufzeitprüfung, geschützte Testkonfiguration, Auswahl des Testkontos, tatsächliche Testbereitstellung und Abnahme mit echten Modellantworten. Die neun Browserprüfungen ersetzen keinen Hanko-/PostgreSQL-/Requesty-Gesamttest. Unverändert 78 historische Requesty-Aufrufe; keine neuen Kostenmessungen. Fachliche Restpunkte T13, T35, T43 und fehlender B07-Vorjahresmonat bleiben offen. T20 ist der bestätigte Darstellungsmaßstab, keine Freigabe aller 45 Fälle. Das Goal bleibt aktiv.

**Abschließender Prüfstand dieses Schritts:** `C:/tmp/portal-test-20260910-gueterstroeme-ui04` ist das aktuelle vollständige lokale Testpaket: 1.700 Dateien, 667.757.997 Bytes, Manifest-SHA-256 `25150e3c8e4fdad5aef10cf6bf8429fc5de949357e049b4769cbadc50d78f972`. `release_ui04_validation.json` bestätigt alle Dateiprüfsummen sowie die tatsächliche Initialisierung und T20-Abfrage direkt aus dem privaten Releasebestand. `browser_ui04/report.json` bestätigt erneut alle neun Browserprüfungen für genau dieses Manifest. Der AlwaysData-Planmodus bestätigt die Testsite und den Zielrelease; ohne `-Apply`, weiterhin keine Serveränderung. Fünf überholte eigene ui01–ui03-Pakete wurden nach Pfadkontrolle entfernt; die beiden abschließenden ui04-Pakete bleiben vorhanden.

**Echter T20-Nachtest:** `requesty_t20_ui04/result.json` und `review.json`: neuer Ablauf mit `vertex/gemini-3.7-flash@eu`, passende Funktionszuordnung, 67.757 t und drei belegte Folgefragen. Alle sichtbaren Antwortfelder stimmen mit dem bestätigten lokalen T20-Muster überein. Zwei erfolgreiche Modellaufrufe, 9.635 Tokens, laut API 0,010506375 USD, Ablaufzeit 11,25 Sekunden. Damit insgesamt 80 historische Requesty-Aufrufe. Dies belegt T20 im aktuellen Modell-/Programmlauf, nicht die Qualität aller 45 Fälle. Gemini ordnet zu und wählt belegte Aussagen; das Programm erzeugt weiterhin die Kundendarstellung.

**Testumgebung:** `alwaysdata_isolation01.json` bestätigt unterschiedliche Test-/Produktivdatenbanken und Laufzeitordner, allerdings denselben Datenbankbenutzer; keine Behauptung vollständig getrennter Zugangsdaten. `linux_wheels01.json` bestätigt veröffentlichte passende CPython-3.13-Linux-Pakete für die beiden neuen Abhängigkeiten, noch keine erfolgreiche Linux-Ausführung. Für die tatsächliche Freischaltung wurde die Auswahl eines bereits bestehenden Testkontos angefragt. Testkonfiguration, Live-Laufzeit, Deployment und gemeinsame Liveabnahme bleiben offen. Produktionssystem unverändert.

### Analyseassistent: Testrelease auf AlwaysData bereitgestellt (10.09.2026)

**Aktiv auf Testsite 1067000:** `portal_test/releases/portal-test-20260910-gueterstroeme-ui05/alwaysdata_portal/wsgi.py`, Arbeitsverzeichnis entsprechend. Das vollständige Paket ist bytegleich zum lokal und im Browser geprüften ui04-Stand, Manifest-SHA-256 `25150e3c8e4fdad5aef10cf6bf8429fc5de949357e049b4769cbadc50d78f972`. Der bestätigte Planmodus ging dem Apply-Lauf voraus. Testportal und Datenbank melden bereit; die vorhandene Test-Kita-Aufgabe 30833 wurde auf denselben Release umgestellt. Der bisherige funktionsfähige Testrelease `portal-test-20260904-bkg-basemap-v3` bleibt als Rückfallstand erhalten. Produktionssite und Produktionsaufgabe wurden nicht umgeschaltet.

**Upload und Wiederherstellung:** Der erste ui04-Upload brach nach 77 Dateien und 14.073.451 Bytes vor jeder Migration ab. Der bisherige Testrelease wurde anschließend mit gesundem Portalstatus bestätigt (`deployment_failed01.json`, `upload_diagnostic01.json`). Die Übertragung wurde auf weniger Verzeichniswechsel und maximal drei Versuche je betroffener Datei umgestellt; Wiederaufnahme beginnt bei Byte null ausschließlich innerhalb des neu angelegten, inaktiven Release. Vorhandene Releases und dauerhafte Zugriffsfehler werden nicht überschrieben oder endlos wiederholt. Sechs Automatisierungsprüfungen bestehen (`deployment_retry_validation01.json`). Der zweite Lauf mit neuem Namen ui05 übertrug alle 1.701 Dateien einschließlich Manifest, installierte die Laufzeit und führte die Testmigration erfolgreich aus. `partial_upload_cleanup01.json` bestätigt anschließend die Entfernung des eigenen unvollständigen ui04-Serverordners. Ein bereits vor dem zweiten Versuch vorhandener, nicht eindeutig dieser Arbeit zugeordneter FTPS-Zugang 567638 wurde nicht verändert.

**Direkte Linux-Prüfung:** `linux_runtime_validation01.json` verifiziert auf dem aktiven Server alle 1.700 Manifestdateien, Python 3.13.15, DuckDB 1.2.1, jsonschema 4.25.1 und psycopg 3.2.10. Der private Analysebestand initialisiert korrekt; T20 ergibt ohne Modell 67.757 Tonnen und drei belegte Folgefragen. Eine ausdrücklich lesende Datenbanktransaktion bestätigt Migration 009 samt Prüfsumme, Basic 5/Premium 50 und den weiterhin inaktiven Werkzeugeintrag. Vier Identitäten passen zum konfigurierten Hanko-Aussteller; es wurden keine Konten oder Rechte verändert. Temporäre Prüfaufgabe, FTPS-Zugang und Statusdatei wurden entfernt und die Bereinigung bestätigt.

**Öffentlicher Zugriffsschutz:** `live_access_validation02.json` bestätigt gesunde Portal-API und Loginseite. Der Werkzeugpfad liefert ohne Sitzung exakt dieselbe Loginseite; die deaktivierte Analyse-API gibt den vorgesehenen Hinweis mit HTTP 503 zurück. Private Dateien, Dashboardressourcen ohne Aktivierung und getestete Pfadüberschreitungen werden nicht ausgeliefert. `live_access_validation01.json` hatte hierfür zu enge Statuscode-Annahmen; der zweite Prüflauf prüft zusätzlich den tatsächlichen Antwortinhalt. Dies ist keine Abnahme eines angemeldeten Nutzers oder der Verwaltungsoberfläche.

**Requesty-Konfiguration und offene Freigabe:** Die automatische Freigabeprüfung hat die Übertragung des lokal verschlüsselten Requesty-Schlüssels in die geschützte AlwaysData-Testkonfiguration abgelehnt, weil die Zustimmung zur dortigen Speicherung nicht ausdrücklich vorlag. Dieser Auftrag wurde nicht ausgeführt. Der Nutzer möchte den Schlüssel selbst unter Web → Sites → Testsite 1067000 → Environment eintragen; die sechs erforderlichen Variablen wurden im Chat genannt, mit `WBP_GUETERSTROEME_ENABLED=0`. Erfolgreiches Speichern und passende Konfiguration sind noch zu bestätigen. Keine neuen Modellaufrufe in dieser Bereitstellung; weiterhin 80 historische Requesty-Aufrufe. Auswahl des Testkontos, gezielte Werkzeug-/Paketfreigabe und vollständige Prüfung mit Anmeldung und Requesty bleiben offen. Goal bleibt aktiv.

**Weitere fachliche Vorbereitung:** `t35_name_readiness01.json` bestätigt Namen für alle 59 positiven T35-Partnerrelationen 2024. Statistik-Länderkennungen dürfen nicht durch teilweise abweichende geografische Länderzuordnungen überschrieben werden; die Namensausgabe ist noch nicht im Assistenten ergänzt. `t43_scope_readiness01.json` bestätigt aus an B04–B06 gebundenen Originaldateien für 2024 die 422 Einträge, davon 400 NUTS-3 und 22 andere Raumebenen, ohne fehlenden Kreis. Die jahresübergreifende Datei umfasst dagegen 434 verschiedene Kennungen; der konkrete 422/400/22-Nachweis gehört ausdrücklich zum Jahr 2024. Noch nicht in die Kundenantwort eingebunden. T13 und B07-Vorjahresvergleich bleiben offen.

**Nachtrag: manuelle Requesty-Konfiguration und echter Serveraufruf bestätigt (10.09.2026):** Nach der vom Nutzer bestätigten Eingabe bestehen alle sechs Konfigurationsprüfungen; die Testsite wurde neu gestartet und meldet gesund. `alwaysdata_requesty_manual_config01.json` enthält ausschließlich Statusprüfungen, keinen Schlüssel. Umgebungsvariablen wurden nicht verändert. Der Nutzerzugang bleibt mit Aktivierungsflag `0` und inaktivem Werkzeugeintrag gesperrt.

`linux_requesty_validation01.json` bestätigt anschließend einen echten Ablauf direkt aus der Linux-Testlaufzeit über `vertex/gemini-3.7-flash@eu`: natürlich formulierte Frage nach Güterarten der Straßenverbindung Köln → Hamburg 2024, passende Funktionszuordnung, 67.757 Tonnen und dieselbe sichtbare Kundendarstellung wie beim bestätigten T20-Muster einschließlich drei Folgefragen. Zwei Modellanfragen, 9.809 Tokens, laut API 0,011382525 USD, Analysezeit 10,264 Sekunden. Zusammenfassung: `requesty_server_summary01.json`. Damit 82 protokollierte Modellanfragen insgesamt. Kein Kundenkontingent belastet; keine neue fachliche 45-Fälle-Abnahme. Datenbank-/Manifestprüfung bestanden, temporäre Aufgabe, FTPS-Zugang und Statusdatei entfernt. Noch kein Test einer angemeldeten Browser-Sitzung oder Kontofreigabe.

Der Serverprüfer führt bezahlte Aufrufe nur mit `--requesty` aus. Anschließend wurde sein Wiederholungsschutz ergänzt: Eine atomar angelegte Startdatei verhindert zusätzliche Ausführungen derselben geplanten Prüfaufgabe bei langsamen Modellantworten. `remote_probe_once_validation01.json` prüft den tatsächlichen Startabschnitt mit acht konkurrierenden lokalen Prozessen: genau eine Ausführung, keine externen Aufrufe, temporärer Ordner entfernt. Der neu ergänzte Startschutz ist separat lokal geprüft; der vorherige erfolgreiche Linuxbericht bindet seinen damaligen Prüferstand. Auswahl des bestehenden Testkontos, gezielte Paket-/Werkzeugfreigabe und gemeinsame Browser-/Requesty-Abnahme bleiben offen. Produktionssystem unverändert; Goal aktiv.


Aktiver, live geprüfter Dialogstand ui10: siehe „Dialogkorrekturen nach Nutzersichtung“ im Qualitätssicherungsplan. Der lokale Verlauf ist auf sechs Nutzernachrichten und 6.000 Zeichen begrenzt; die aktuelle Eingabe darf zusätzlich bis zu 4.000 Zeichen enthalten. Frühere Antwortwerte werden dem Modell nicht als neue Datenquelle vorgelegt.


Dialogkorrekturen ui10 sind bereitgestellt. Nachweise: `dialogue_runtime05.json` (72 lokale Prüfungen), `browser_ui10b/report.json`, `deployment_ui10.json`, `linux_runtime_validation04.json`, `activated_access_validation03.json` und `authenticated_browser_ui10.json`. Die letzten sechs Nutzernachrichten (höchstens 6.000 Zeichen) unterstützen kurze Rückfrageantworten innerhalb der geöffneten Seite; „Neuer Chat“ und Neuladen verwerfen diesen lokalen Verlauf. Zahlen werden weiterhin aktuell aus den geprüften Daten gelesen.

### Lokale Antwortlogik 0.2.0 (11.09.2026)

Die lokal geprüfte, noch nicht bereitgestellte Version erkennt gerichtete Mehrjahresfragen wie Rosenheim → Augsburg ohne Einzeljahres-Rückfrage und verwendet sichtbar die fünf neuesten gemeinsam abfragbaren Jahre. Numerische Ergebnisse enthalten zuerst bis zu drei serverseitig belegte Kernaussagen; die vollständige Tabelle bleibt erhalten und ist ab neun Zeilen zunächst eingeklappt. Der optionale Modellaufruf darf diese Belege sprachlich verbinden, aber keine neuen Zahlen, Einheiten, Ursachen, Bewertungen oder Empfehlungen einführen. Ungültige oder unvollständige Modellantworten werden durch die analytische Serverfassung ersetzt. Fehlerstufe und Fehlerkennung werden intern beziehungsweise kundenlesbar getrennt erfasst.

Nachweis: `outputs/analyseassistent_runtime_20260911/narrative_validation01.json`, 77/77 lokale Prüfungen, keine externen Modellaufrufe. Drei beauftragte Terra-Subagenten prüften Katalogstichproben, Promptgrenzen und den gemeldeten Mehrjahresablauf. Der aktive Testrelease ui10 bleibt unverändert; für Version 0.2.0 sind Testrelease, echter Modell-Stichprobenlauf und Browserabnahme noch offen.
