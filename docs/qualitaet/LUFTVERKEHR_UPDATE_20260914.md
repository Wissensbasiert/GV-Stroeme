# Eurostat-Luftverkehr: korrigierter Quellenstand vom 14.09.2026

## Anlass und Quellenabgrenzung

Die vom Nutzer aktualisierten Originaldateien `estat_avia_gooa.tsv` und `estat_avia_gooc.tsv` wurden vollständig neu eingelesen. Die annualen Dimensionen, Einheiten und Verkehrsabgrenzungen bleiben erhalten; Monats- und Quartalszeilen werden nicht zu Jahreswerten addiert. AVIA_GOR_DE wurde nicht aktualisiert und reicht weiterhin nur bis 2024.

Die frühere GOOA-Flughafensumme 2025 von 1.573.111 reinen Fracht- und Postflügen ist korrigiert. Die 22 veröffentlichten deutschen Flughafenwerte ergeben jetzt 119.237, die nationale GOOC-Reihe weiterhin 116.671. Zum Vergleich: 2024 sind es 120.846 beziehungsweise 117.931. Die beiden Zählungen bleiben getrennt; weder Flughafensummen noch Richtungssummen ersetzen die nationale Originalreihe. CAF_FRM umfasst keine Passagierflüge mit Beiladefracht.

| Quelle | SHA-256 |
| --- | --- |
| AVIA_GOOA | `f4b188782619f9f453c58ab0d5ba162da2660cba8c5f7c7c5fd73dabce85d565` |
| AVIA_GOOC | `3d8a5b29108a948c4c9f3b9f542a42eb2ad5b0c2e65cbbb79e971f02bec9f5ab` |
| AVIA_GOR_DE, unverändert | `45695ac2c11c94c5fbf335a443730b1497f35b8b7ca7ec3ed2af527f431c4b6a` |

Die Freigabe ist in `config/analyseassistent/LUFTVERKEHR_FREIGABE.json` an beide aktualisierten Dateien gebunden. Der Web-Build stoppt bei einer anderen Quellenfassung. Die Analyseabfrage prüft die Quellenhashes ihres unveränderlichen B04–B06-Manifests: Alte oder ungeprüfte Bestände bleiben für Flughafen-Flugzahlen 2025 gesperrt. Bei weiteren Updates sind die fachlichen Prüfungen erneut erforderlich; eine bloße Änderung der Freigabehashes genügt nicht.

## Aufbereitung und Prüfung

- `web_airfreight.json`: 1.38 MiB, 281/281 Flughafenkoordinaten, 1.391 veröffentlichte Jahres-/Richtungswerte unabhängig mit Originalzellen abgeglichen. Die Flughafensummen je Richtung werden zusätzlich geprüft; nationale Angaben bleiben eigenständige Originalwerte.
- Gegenüber der gesicherten Vorgängerdatei ausschließlich 66 zusätzliche Flugwerte 2025: Gesamtzahl, Abflug und Ankunft für 22 Flughäfen. Sämtliche übrigen Flughafenwerte 2016–2025, nationalen Werte, Relationen, Relationsnenner und Koordinaten sind exakt unverändert. Veröffentlichte Nullen bleiben Nullen; fehlende Angaben werden nicht ergänzt.
- Die Kennzahlenfunktionen und der echte lokale Chrome-Browser bestätigen Leipzig/Halle 2025 mit 48.657 Flügen und −2,6 % gegenüber 2024 sowie Frankfurt/Main mit 24.210 Flügen 2025 und 23.743 im Jahr 2024. Die Oberfläche weist weiterhin ausdrücklich auf fehlende Relationen 2025 hin. Keine JavaScript-Laufzeitfehler.
- Neuer B04–B06-Stand `468a94ac196b551486b1`: 10/10 unabhängige Partnerprüfungen und 202/202 Hauptprüfungen bestanden; erst danach lokal aktiviert. Originalwerte, Qualitätszeichen, Fehlzellen und Länder-/Partnerzuordnungen bleiben im privaten Analysebestand erhalten. GOOC ist zusätzlich als geprüfte Freigabequelle im Manifest gebunden; nationale Luftverkehrswerte werden weiterhin im Dashboardpaket geführt.
- Abhängiger KI-Unterstützungsbestand `1f110797e41ffb2b399507c7`: 32.296 Quellenvergleiche, 34.270 KV-Datensätze und 3.984 Güterprofile; nach Neuaufbau erfolgreich geladen.
- Der unabhängige Dashboardzugriff `474ef7b4cebe7468b85f` hat unveränderte Eingangs-/Codeidentität. Der Builder verweigert bestimmungsgemäß ein Überschreiben dieses vorhandenen Stands. Manifest, Prüfbericht und sämtliche Ausgabedateien wurden anhand ihrer Prüfsummen bestätigt; der Bestand wurde erhalten.

## KI-Abfragen und Übergabepaket

Die feste Jahresausnahme in Chat-Jahresauswahl und Knotenabfragen wurde durch die Freigabeprüfung des tatsächlichen Datenmanifests ersetzt. Leipzig/Halle (48.657), Frankfurt/Main (24.210) und Köln/Bonn (34.193) liefern für 2025 ihre korrigierten reinen Fracht-/Postflugzahlen. Gesamtprofile können Tonnen und Flüge gemeinsam ausgeben. Quellenbeschriftungen kennzeichnen verfügbare Werte nicht mehr als gesperrt. Gefilterte Partnerauswertungen bleiben an AVIA_GOR_DE gebunden und erhalten für 2025 keine erfundenen Werte.

Ein temporäres vollständiges Übergabepaket mit 1.645 Dateien und 731.383.293 Bytes wurde aus dem neuen Stand erstellt. Die kopierte private Laufzeit wurde in einem frischen Prozess geladen; Datenkennung `039b9381b0645bb93f0dbd23`. Auch direkt in dieser Kopie liefert Leipzig/Halle 2025 genau 48.657 Flüge. Alle erforderlichen Browserdateien sind enthalten. Nachweis: `package_validation.json`; keine Serverübertragung. Die temporäre Paketkopie wurde nach Prüfung entfernt, der reproduzierbare lokale Datenbestand bleibt erhalten.

**Abschließender Laufzeitnachweis:** 217/217 lokale Tests bestanden, null Fehler, null externe Modellaufrufe (`runtime_validation_final.json`). Im ersten Lauf bestand noch eine historische Testerwartung auf die frühere 2025-Sperre; diese wurde auf das nun verfügbare gemeinsame Tonnen-/Flugprofil umgestellt. Die neuen Regressionen halten dagegen die Sperre alter oder ungeprüfter Quellenstände ausdrücklich aufrecht. Direkte Chat-Datenabfragen für drei Flughäfen und die Jahresauswahl sind in `assistant_2025.json` dokumentiert. Kein neuer 45-Fälle-Modelltest und keine Onlinebereitstellung der neuen Daten.

## Reproduktion und Nachweise

Reihenfolge: Luftfracht-Build → `validate_airfreight_bundle.py` → B04–B06-Build → Partnerprüfung → Hauptprüfung mit `--activate` → `prepare_assistant_support.py` → Darstellungsreferenzen → Laufzeit- und Browserprüfung. Den Dashboardzugriff nur bei veränderter eigener Eingangs-/Codeidentität neu erstellen. Die übrigen Rohdatenpipelines werden durch dieses Luftverkehrsupdate nicht verändert.

Zusätzliche Prüfungen: `node scripts/validation/validate_airfreight_kpis.cjs` und `validate_airfreight_revision.cjs <lokale URL> <Ausgabeordner>`. Temporäre Datenbanken und Testdateien liegen unter `C:/tmp`; Rohdaten und private Analysepakete bleiben außerhalb von Git.

Lokale Nachweise: `outputs/airfreight_update_20260914/`, insbesondere `raw_audit.json`, `bundle_delta.json`, `web_validation.json`, `dashboard_access.json` und `browser/validation.json`. Gesicherter Vorgängerstand unter `backups/before-airfreight-update-20260914/`.

Die Datenaktualisierung ist von der parallelen Erweiterung der Flughafenabfragen getrennt. Deren Serverrelease ist kein Nachweis einer Bereitstellung dieser neuen Daten. In dieser Aufgabe wurden keine externen KI-Modellaufrufe oder Produktionsänderungen vorgenommen.
