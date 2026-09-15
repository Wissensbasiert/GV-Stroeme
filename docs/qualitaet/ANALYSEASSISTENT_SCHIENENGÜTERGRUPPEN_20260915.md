# Analyseassistent: benannte Schienen-Gütergruppen und Randjahresvergleich

**Stand:** 15.09.2026, Version 0.8.1, lokal geprüft, noch nicht bereitgestellt.

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

Ein vollständiger Lauf mit der bestehenden HTTP-Serverprüfung wurde wegen deren langer Wartezeit nicht als Gesamtfreigabe gewertet. Das betrifft nicht die oben genannten bestandenen Fachtests. Vor einer Bereitstellung sind das Releasepaket, die Linux-Laufzeit und der angemeldete Browserdialog erneut zu prüfen.

## Grenzen

Die Veränderungen sind rechnerische Vergleiche veröffentlichter Werte und belegen keine Ursache. Fehlende oder nicht veröffentlichte Gruppen dürfen nicht als tatsächlich verkehrsfrei interpretiert werden. Testportal und Produktion blieben in diesem Schritt unverändert.
