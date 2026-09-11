# GitHub-Sicherung und AlwaysData-Testreleases

**Aktueller Abschluss vom 11.09.2026:** Aktiv ist `portal-test-20260911-gueterstroeme-beta03`. Die Korrektur trennt die sieben Güterarten von ihren NST-Einzelpositionen in der sichtbaren Antwort. Gegenüber beta02 wurden drei geänderte Dateien plus Manifest (363.061 Bytes) übertragen und 1.703 Dateien serverseitig unabhängig kopiert; alle 1.706 Zieldateien geprüft. 78 lokale Prüfungen, Linux-Prüfung und angemeldeter Antwort-/Kontingenttest bestanden. Geprüfte Rückfallstände bleiben ui10 und ui09; sie enthalten noch die frühere Darstellungsgrenze. Produktion unverändert; temporäre Serverprüfmittel entfernt. [Prüfbericht einschließlich Aufbewahrungsnachweis](../qualitaet/ANALYSEASSISTENT_BETA_20260911.md). Die unten stehenden ui10-Angaben dokumentieren den vorherigen Abschluss am selben Tag.

Verbindlicher Arbeitsablauf auf Nutzerauftrag vom 11.09.2026. Für fachliche Freigaben bleibt der Qualitätssicherungsplan maßgeblich.

## Zuständigkeit und GitHub

- Güterströme: `https://github.com/Wissensbasiert/GV-Stroeme`, maßgeblicher gemeinsamer Stand auf `main`.
- Portal, Anmeldung, Kontingente und Bereitstellung: `https://github.com/Wissensbasiert/wbp-solutions-portal`, lokaler Ordner `D:/HiDrive/01_Projekte/WBP-Solutions/Plattform/Overhaul`.
- Nach abgeschlossenen, geprüften Änderungen die zugehörigen Quellen, Prompts, Tests und Betriebsunterlagen committen und regulär nach `main` übertragen. Vorher Remoteänderungen abgleichen. Kein Force-Push; fremde lokale Änderungen erhalten und nicht ungeprüft mitveröffentlichen.
- Geheimnisse, lokale Anhänge, personenbezogene Testdaten, große private Analysebestände und reproduzierbare Browserpakete bleiben außerhalb von Git. Die Aufbereitungsskripte, Abhängigkeiten und Wiederherstellungsanleitung gehören hinein. Bereits verwaltete Git-LFS-Dateien behalten ihre Behandlung.
- Ein Push ist keine Serverbereitstellung. Beide Schritte getrennt prüfen und mit Commit-IDs sowie Release-Manifest dokumentieren. `main` ist nicht gleichbedeutend mit fachlicher Produktionsfreigabe.

## Nur Änderungen übertragen

Der Standard-Testdeployer im Portalprojekt (`deployment/automation/run_alwaysdata_deploy.ps1`) verwendet einen neuen, unabhängigen Releaseordner. Er vergleicht dessen vollständiges Dateimanifest mit dem aktiven Testrelease. Nur neue oder geänderte Dateien und das Manifest werden hochgeladen. Unveränderte Dateien werden auf dem Server kopiert, anschließend werden sämtliche Zielprüfsummen kontrolliert. Im neuen Stand entfernte Dateien werden nicht übernommen. Keine Hardlinks und keine Überschreibung des aktiven Release.

Fehlt ein kompatibles Ausgangsmanifest, wird abgebrochen. Nur dann begründet den vollständigen Upload mit `-FullUpload` verwenden. Bestehende Releaseordner bleiben unveränderlich. Temporäre Pakete und Abhängigkeiten liegen unter `C:/tmp`.

Die Änderung gilt für die Testsite 1067000. Die Produktionsbereitstellung bleibt unverändert und benötigt einen gesonderten Auftrag.

## Aufbewahrung auf AlwaysData

Nach erfolgreicher Releaseabnahme: **aktiver Testrelease plus zwei geprüfte Rückfallstände**. Ältere vollständige und unvollständige Testreleases werden anhand eines gespeicherten Bereinigungsplans entfernt. Vorher aktive Site und alle geplanten Aufgaben auf Pfadverweise prüfen; die drei erhaltenen Releasebestände vollständig anhand ihrer Manifeste prüfen. Bei anderen Verweisen, beschädigtem Rückfallstand oder zwischenzeitlicher Änderung abbrechen und klären. Datenbank, `portal_test/private_data`, gemeinsame virtuelle Umgebung und Produktion bleiben unangetastet.

Werkzeug im Portalprojekt: `deployment/automation/release_maintenance.py`. Ohne `--apply` inventarisieren; mit `--keep <Rückfall1> <Rückfall2> --output <Plan.json>` einen Plan schreiben. Anschließend `--plan <Plan.json> --apply --output <Ergebnis.json>`. Aufruf über den DPAPI-Wrapper `run_release_maintenance.ps1`; keine Schlüssel in Befehle, Dateien oder Chat eintragen. Temporäre Prüfaufgaben und FTPS-Zugänge werden entfernt. Keine dauerhaft laufende neue Automation.

## Wiederherstellung

Für Quellcode den passenden Git-Commit verwenden; öffentliche Ausgangspakete gegebenenfalls mit Git LFS wiederherstellen. Browserpakete gemäß Projekt-README erzeugen. Private Analysebestände werden aus den lokal gesicherten Quellen nach `ANLEITUNG_DATENAKTUALISIERUNG.md` aufgebaut; GitHub ersetzt diese Datensicherung nicht. Die zwei Server-Rückfallstände enthalten jeweils ihren vollständigen damaligen Laufzeitbestand. Ein Rückfall muss Sitepfad und monatliche Kita-Aufgabe gemeinsam berücksichtigen; Datenbankmigrationen werden nicht automatisch zurückgenommen.

## Nachweis vom 11.09.2026

Bestätigt aktiv: `portal-test-20260910-gueterstroeme-ui10`. Erhaltene Rückfallstände: `portal-test-20260910-gueterstroeme-ui09` und `portal-test-20260910-gueterstroeme-ui07`. Alle 5.106 Manifestdateien dieser drei Stände vollständig auf dem Server geprüft. 57 ältere beziehungsweise temporäre Testordner mit 2.292.385.809 Bytes erfassten Dateien entfernt; danach genau drei Releases vorhanden. API/Datenbank gesund, aktive Site und Produktion unverändert. Temporäre Prüfaufgaben, Prüfdateien und FTPS-Zugänge entfernt.

Echter Delta-Test an einem nicht aktivierten Paket: 1.703 unveränderte Dateien serverseitig kopiert, eine neue Prüfdatei plus Manifest hochgeladen (332.416 Bytes), alle 1.704 Zieldateien geprüft. Das Prüfpaket anschließend mit entfernt. Der Standard-Testdeployer nutzt jetzt diesen Ablauf. Migration/Umschaltung wurden in diesem Infrastrukturtest nicht erneut ausgeführt; ui10 bleibt aktiv. 28 gezielte Portal-/Bereitstellungsprüfungen aus dem ausgewählten Git-Kandidaten bestanden, zusätzlich Frontend-Lade- und Syntaxprüfung. Keine Modellaufrufe.

Auf GitHub `main` verifiziert: Güterströme-Implementierung `c553be2574c2c926d00ac4d734a527bc29fa9fdc`, Portal-Anbindung und Delta-Verfahren `b8dbd0787ed5d255ec2a9ccbdd2eddfb15677176`. Spätere Dokumentationscommits können darüber liegen. Andere lokale Portaländerungen (unter anderem Micro-Depot/weitere Darstellungsanpassungen und Produktionsstatusbrücke) wurden erhalten und nicht mitveröffentlicht. Deshalb sind diese Git-Commits keine Behauptung einer vollständigen Bytegleichheit sämtlicher Portaldateien mit ui10; maßgeblich für den Server sind die geprüften Release-Manifeste.

Lokale ausführliche Nachweise: `outputs/release_work_20260911/delta_live01.json`, `prune_plan01.json`, `prune_result01.json`, `local_validation01.json`. Die wesentlichen Ergebnisse stehen bewusst hier in Git, damit der Betrieb nicht vom lokalen Ausgabeordner abhängt.
