# Analyseassistent: benannte Schienen-Gütergruppen und Randjahresvergleich

**Stand:** 15.09.2026, Version 0.8.1, im AlwaysData-Testportal bereitgestellt und geprüft.

## Anlass

In einem Nutzerdialog zur Schienenrelation Berlin → Hamburg wurden dreistellige NST-Feinpositionen ohne Bezeichnung ausgegeben. Eine Anschlussfrage nach besonders verlorenen Gütergruppen blieb zudem zunächst in einem Einzeljahr, obwohl zuvor bereits der Zeitraum 2021–2025 bestätigt war. Damit entsprach die Antwort weder der verständlichen Dashboardgliederung noch der zeitlichen Fragestellung.

## Fachliche Festlegung

- Standard ist die im Dashboard verwendete Gliederung in sieben benannte C7-Gütergruppen.
- Eine ausdrücklich gewünschte NST-Gliederung verwendet die 20 benannten zweistelligen NST-2007-Abteilungen.
- Dreistellige NST-Feinpositionen bleiben interne Quellenmerkmale und werden weder in Fakten, Tabellen, Belegen noch Klassifikationshinweisen ausgegeben.
- Fragen nach Entwicklung, Zunahme, Abnahme, Gewinn oder Verlust übernehmen die bereits bestätigte Schienenrelation, Richtung, Kennzahl und beide Randjahre.
- Nur Werte, die in beiden Randjahren veröffentlicht vorliegen, werden rechnerisch verglichen. Ein fehlender Gruppenwert ist keine Null und kein Rückgang um 100 Prozent.

## Reproduzierter Fall Berlin → Hamburg

Für 2021–2025 weist die C7-Darstellung den größten bezifferbaren Rückgang bei **Sonstige Produkte** aus: 397.908 Tonnen auf 238.287 Tonnen, also 159.621 Tonnen beziehungsweise 40,12 Prozent weniger. Andere nur in einem Randjahr veröffentlichte Gruppen bleiben sichtbar, werden aber ausdrücklich als nicht vergleichbar gekennzeichnet.

Auf die Anschlussfrage nach NST-Gütergruppen wechselt dieselbe Auswahl auf NST-20. Der größte bezifferbare Rückgang liegt dort bei **Nicht identifizierbare Güter**: 394.933 Tonnen auf 230.254 Tonnen, also 164.679 Tonnen beziehungsweise 41,70 Prozent weniger. Die Abteilung **Geräte und Material für die Güterbeförderung** steigt von 2.975 auf 8.033 Tonnen. Keine Antwort enthält einen dreistelligen NST-Code.

## Umsetzung und Prüfung

Die Aggregation liegt in der Assistentenschicht; `scripts/analysis/b03.py` und der geprüfte B03-Datenbestand wurden nicht verändert. Verträge, Standardauswahl, Gesprächsfortsetzung, Ergebnisbildung, Belegpaket und Tabellen verwenden gemeinsam die beiden freigegebenen Gliederungen.

Ohne externen Modellaufruf bestanden:

- 27 Vertrags-, Sicherheits- und Grenztests,
- 12 Tests der semantischen Auswahl und Gesprächsfortsetzung,
- 41 Realdatentests ohne die gesonderte HTTP-Serverprüfung, darunter Einzeljahr, Zweijahresvergleich, C7, NST-20 und der vollständige Berlin–Hamburg-Anschlussdialog,
- 12 Prüfungen des nativen Chatablaufs sowie eine gezielte Prüfung des serverseitigen C7-/NST-20-Schutzes,
- Python-Syntaxprüfung der geänderten Assistentenmodule.

Ein vollständiger Lauf mit der lokalen HTTP-Serverprüfung wurde wegen deren langer Wartezeit nicht als Gesamtfreigabe gewertet. Das betrifft nicht die oben genannten bestandenen Fachtests. Die nachfolgende vollständige Release- und Linux-Prüfung bindet den tatsächlich aktiven Serverbestand.

## Bereitstellung und Serverprüfung

Der Release `portal-test-20260915-gueterstroeme-groups01` wurde aus dem vollständig geprüften Vorgänger `total01` zusammengesetzt. 1.767 unveränderte Dateien wurden serverseitig übernommen, 17 geänderte Nutzdateien plus Manifest übertragen. Sämtliche 1.784 Dateien und Prüfsummen stimmen mit dem lokalen Release überein. Manifest-SHA-256: `ca1e72289efa2c8b7e75ba6b6c72c65fc2dcee6be3114ff96dfea0854be31484`; Datenkennung: `24a4c8cee90c6f866fdba5a7`.

Die abschließende Linux-Prüfung bestätigte zusätzlich:

- C7-Standardausgabe Berlin → Hamburg 2021–2025 mit −159.621 Tonnen bei **Sonstige Produkte**,
- NST-20-Anschlussfrage mit −164.679 Tonnen bei **Nicht identifizierbare Güter**,
- keine Ausgabe dreistelliger NST-Codes,
- keine externen Modellaufrufe und keine Datenbankschreibvorgänge,
- bereite API und Datenbank sowie vollständige Entfernung der temporären Prüfaufgabe, des FTPS-Zugangs und der Statusdateien.

Das angemeldete Dashboard und das vorhandene KI-Fenster wurden im Browser sichtbar bestätigt. Eine weitere Frage wurde dabei bewusst nicht abgesendet, um kein Kundenkontingent und keinen Modellaufruf auszulösen. Der alte Release `loading01` wurde nach erneuter Bestandsaufnahme und manifestgebundenem Plan entfernt. Aktiv bleiben `groups01` sowie genau zwei vollständig geprüfte Rückfallstände: `total01` und `mdc-license01`. Das Produktionsportal blieb unverändert.

## Grenzen

Die Veränderungen sind rechnerische Vergleiche veröffentlichter Werte und belegen keine Ursache. Fehlende oder nicht veröffentlichte Gruppen dürfen nicht als tatsächlich verkehrsfrei interpretiert werden. Die Bereitstellung betrifft ausschließlich das Testportal; das Produktionsportal blieb unverändert.
