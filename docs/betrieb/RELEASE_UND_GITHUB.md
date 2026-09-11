# GitHub-Sicherung und AlwaysData-Testreleases

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

Aktiver Stand zu Beginn: `portal-test-20260910-gueterstroeme-ui10`. Vorgesehene Rückfallstände: `portal-test-20260910-gueterstroeme-ui09` und `portal-test-20260910-gueterstroeme-ui07`. Abschlusszahlen, Git-IDs und geprüfte Serverbereinigung werden nach erfolgreicher Ausführung hier ergänzt. Lokale ausführliche Prüfberichte: `outputs/release_work_20260911/`.
