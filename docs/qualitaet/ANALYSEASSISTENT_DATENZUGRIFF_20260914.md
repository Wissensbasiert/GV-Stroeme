# KI-Chat: vorhandene Daten systematisch erschließen

Stand: 14.09.2026, Version 0.5.0. Im Testportal bereitgestellt; lokale Prüfung, Linux-Nachprüfung und angemeldete Browserabnahme bestanden. Produktion bleibt unverändert.

## Anlass und bestätigte Ursache

Die Antwort zur Prognose von Metallen im Berliner Schienenversand war fachlich falsch abgegrenzt: Die alte Chatfunktion las nur Verkehrsträgersummen ohne Güterdimension, obwohl Originalmatrizen und Dashboard die Güterauswahl enthalten. Der gesamte Schienenversand steigt von 970.375 auf 1.265.924 Tonnen; angefragte Metalle (VP100/NST10/C4) dagegen von 277 auf 1.531 Tonnen, +1.254 Tonnen bzw. +452,71 %. Prognosebasis 2019 zu Prognosefall 2040 P1, kein beobachteter Verlauf.

## Umgesetzte zusätzliche Zugriffe

| Datenbereich | Chatwerkzeug und Umfang | Grenze |
|---|---|---|
| Prognose-Güter | `forecast_regions.goods`, C7 oder 25 Original-VP-Gruppen, Verkehrsträger, Richtung, t/tkm | Keine Addition überlappender Gliederungen; Deutschland nur all einschließlich Transit |
| Prognose-Verbindungen | `forecast_relation`, vollständige gerichtete Matrix, Modi, Güter, t/tkm | Fehlende Zeilen bleiben unbekannt, kein weiterer Horizont |
| Regionale NST20 | `dashboard_detail/regional_goods`, Schiene/IWW, t/tkm | Straße NUTS-3 nur C7; nationale Dashboardaggregation keine vollständige Randsumme |
| Hafengüter | `sea_goods`, Hafen und Deutschland, C7/NST20, t/TEU, Richtungen | Hafenbezug nicht mit Stadtprofil gleichsetzen |
| Hafenpartner-Güter | `sea_partners`, C7/Tonnen, Richtung/Partner | Nur veröffentlichte Dashboard-Partnerauswahl |
| KV | `kv_structure`, nationale Ladeeinheiten-/Containergrößenstruktur; `kv_relations` | Getrennte Teilmärkte nicht addieren; Relationsauswahl nicht vollständig |
| Weitere veröffentlichte Kennzahlen | Straßenfahrten im Regionalprofil; VP-KV, gesamte VP-Ladeeinheiten/TEU und Behältertypen | Fahrten nicht eindeutige Fahrzeuge; VP-TEU nicht ausschließlich KV |

## Schutz vor weiteren stillen Datenlücken

Ein Feldzugriffsinventar ordnet die tatsächlich veröffentlichten Regional-, Prognose-, Hafen- und Intermodalfelder Chatwerkzeugen oder Referenzmetadaten zu. Ein neuer nicht zugeordneter semantischer Dashboard-Schlüssel sperrt den Paketaufbau. Der KI-Katalog nennt zusätzliche Daten und echte Grenzen; ein fehlendes privates Paket wird ausdrücklich als fehlende Chat-Anbindung bezeichnet, nicht als fehlende Quelle. Quellen-, Code- und Ausgabeprüfsummen binden jeden Datenstand.

Der Rohmatrix-Abgleich deckt jede regionale C7/VP25-Kombination in beiden Szenarien, Richtungen und Kennzahlen sowie nationale Modussummen ab. Dabei fiel zusätzlich ein bestehender Pipelinefehler auf: Die regionalen Original-VP-Gruppen unter all enthielten bisher keinen Empfangsanteil. Die Pipeline wurde korrigiert. Beispiel Berlin/VP100/2040/all/alle Modi: 2.291.943 Tonnen statt 1.263.379 Tonnen. Die älteren C7-Namen der Dimensionstabelle weichen von der kanonischen Crosswalk-Klassifikation ab; das neue Paket übernimmt die korrekten Crosswalk-Namen.

Regressionstests prüfen Originalfrage, Gütererhalt in Folgefragen, getrennte Gruppen-/Kennwertbelege, Gliederungsüberlappung, führende Nullen, unbekannte Werte, Hafen-/KV-Zuordnung und neue unzugeordnete Felder. Freie unbelegte Behauptungen fehlender Gütergliederung werden bei vorhandenen angefragten Daten abgelehnt; dann bleibt die serverseitig geprüfte Ersatzantwort erhalten.

Keine absolute Garantie beliebiger KI-Formulierungen oder Zugriff auf sämtliche nicht veröffentlichten Rohfelder. Tatsächliche Grenzen bleiben: Straßen-OD-Ist-Güterstruktur, künstliche Straßen-NST20 auf NUTS-3, weitere Prognosehorizonte, nicht importierte Mautauszüge sowie Kosten-/Umwelt-/Kapazitäts-/Ursachenaussagen.

## Prüf- und Bereitstellungsnachweise

Der Nutzer hat ausschließlich das Testportal 1067000 einschließlich benötigter amtlicher privater Analyseauszüge und sieben Modellfragen freigegeben. Produktionsportal und Benutzerrechte bleiben unverändert. Bestehende Serverreleases werden nicht gelöscht oder überschrieben.

- Lokal: 176 Tests bestanden, keine Fehler (`outputs/analyseassistent_access_20260914/offline06.json`); technische Bereitschaftsprüfung bestanden. Bestehende VP2040-Bündelprüfung, öffentlicher Datenlader und Rekonstruktion aller 460 Prognosepartitionen bestanden.
- Quellenabgleich: 291.300 Kennwertzellen bestanden; Feldzugriffsinventar ohne unbekannte semantische Schlüssel. Privater Zugriffssnapshot `474ef7b4cebe7468b85f`, Gesamtdatenstand `ee6a63245684af9920c961a3`. Die Datenqualitätsprüfung verwendet gleiche räumliche, zeitliche, Güter-, Richtungs- und Kennwertabgrenzungen; sie vergleicht nicht bloß unpassende Gesamtsummen.
- Sechs echte lokale Modellfragen: Berlin-Metallprognose und Empfang-Folgefrage, regionale NST20, Hamburger Hafengüter, China als Hafenpartner und nationale KV-Ladeeinheitenstruktur. Zwölf Modellaufrufe, 304.443 Tokens, ausgewiesene Modellkosten 0,202422825 US-Dollar; keine Kundenbuchung. Zwei ursprüngliche freie NST-Texte wurden zunächst zugunsten der korrekten Ersatzantwort abgelehnt: Die Klassifikationsbezeichnung „NST 2007“ und ihr Abteilungscode waren nicht eindeutig im Textbeleg abgebildet. Nach Korrektur bestehen alle sechs gespeicherten echten Modelltexte in der erneuten Belegprüfung, ohne weitere Modellkosten (`live_access01.json`, `replay01.json`). Dies ist eine Wiederprüfung gespeicherter Antworten, kein erneuter Providerlauf.
- Siebte Modellfrage im angemeldeten Browser: Originalfrage Berlin/Metalle/Schienenversand. Absatz und Tabelle zeigen 277 → 1.531 Tonnen, +1.254 Tonnen und +452,71 %, mit Szenariovorbehalt. Tabelle visuell lesbar. Genau eine Frage auf dem eigenen Testkonto gebucht (23 → 24 von 50), kein Kundenkonto (`browser01.json`).
- Linux: sämtliche 1.730 Manifestdateien geprüft; Berlin 277/1.531, regionale Schiene/NST20 557 Tonnen, Hamburger Hafengüter 2.485.916,2 Tonnen, China/Hamburg/C4 291.435 Tonnen und Schienen-KV/Container 68.294.220 Tonnen bestätigt. Bestehende Dialog-, Gegenrichtungs-, Zeitreihen- und Rechteprüfungen bestanden. Keine externen Modellaufrufe und keine Datenbankschreibvorgänge durch den Prüfjob (`linux01.json`).
- Bereitstellung: `portal-test-20260914-gueterstroeme-access04`, unabhängiger Delta-Release. 1.694 unveränderte Dateien kopiert, 36 geänderte Nutzdateien plus Manifest hochgeladen (93.004.762 Bytes). Alle 1.730 Zieldateien geprüft. Manifest-SHA256 `5dbf0299feeda0e503c05027d89e4dc6b8ab593ee01c4bc13c10ebf2b0a2fbcc`. API und Datenbank bereit; vorhandene monatliche KitaNavigator-Aufgabe zeigt auf den neuen Testrelease. Unbeteiligte Portaldateien gegenüber dem verifizierten Ausgangspaket unverändert (`assembly04.json`, `deploy_delta01.json`).
- Temporärer Linux-Prüfjob, FTPS-Zugang, Status-, Sperr- und Fortschrittsdatei nachweislich entfernt; alle fünf Bereinigungsfelder erfolgreich.
- Abschließendes Serverinventar bestanden: access04 aktiv und gesund, Produktion unverändert, alle sechs vorherigen Releases mit identischen Manifestprüfsummen weiterhin vorhanden. Temporärer Inventar-FTPS-Zugang entfernt (`server_inventory_final.json`). Die bestehende Aufbewahrungsbereinigung wird nicht ohne separate Löschfreigabe ausgeführt.

Die maschinenlesbaren Prüfprotokolle und privaten amtlichen Auszüge bleiben lokal beziehungsweise im geschützten Testrelease und außerhalb von Git. Die reproduzierbaren Quellen, Tests, Prompts und Betriebsunterlagen werden regulär auf GitHub `main` gesichert; dies ist keine Produktionsfreigabe. Keine neue unabhängige Gemini-Zweitprüfung in diesem Abschluss und keine pauschale fachliche Abnahme aller denkbaren Fragen.

## Quellen und Körnung

Der Zugriff liest die sechs Original-VP-Matrizen für Straße, Schiene und Binnenschiff in 2019 BASE und 2040 P1, einschließlich gerichteter Quell-/Zielzelle und Original-VP-Gütergruppe. C7-Zuordnung und Namen stammen aus dem kanonischen VP-Crosswalk; NST20-Bezeichnungen aus der NST-Dimension werden nicht als Beobachtungsjahr verstanden. Regionale Ist-, Hafen- und KV-Werte stammen aus den tatsächlich veröffentlichten Dashboardauszügen. Quellenprüfsummen und fachliche Abgrenzungen stehen im Snapshot; die Zuordnung sämtlicher beobachteter semantischer Hauptfelder steht im Feldinventar. Unterfelder und beliebige zusätzliche Rohquellen sind damit nicht pauschal erschlossen.

Die ursprüngliche Berliner Gesamtverkehrszahl war korrekt, beantwortete aber eine andere Güterpopulation. Prognose-KV wird explizit auf `VA=2` begrenzt; fehlende Relationszeilen werden nicht zu Nullverkehr erklärt. Veröffentlichte Hafenpartner- und KV-Relationstabellen bleiben Teilbestände und dürfen nicht als vollständige Verkehrsmatrix ausgegeben werden.
