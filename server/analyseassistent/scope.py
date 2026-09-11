"""Feste, quellengebundene Methodikhinweise; keine frei erzeugten Modellfakten."""
import json
from pathlib import Path


def explain_scope(con,dataset,*,topic,regional_scope=None):
    classification=json.loads((Path(dataset)/'classification.json').read_text(encoding='utf-8'))
    texts=[]
    if topic=='classification':
        texts=[{'label':'C'+group,'text':'C'+group+': '+label,'group':group}
               for group,label in sorted(classification['groups'].items())]
        for code in ['031','14']:
            division=code[:2]
            group=classification['divisions'][division]['group_7_id']
            texts.append({'label':'NST '+code,'text':'NST '+code+' gehört zu C'+group+'.','nst':code,'group':group})
        group=classification['vp_to_group']['140']
        texts.append({'label':'VP 140','text':'VP 140 gehört zu C'+group+'.','vp':'140','group':group})
    elif topic=='road_goods_depth':
        texts=[{'label':'Regionale Güterstruktur','text':'Für die Kreise liegen Angaben zu sieben Güterhauptgruppen vor. Eine feinere Aufteilung auf 20 Güterabteilungen lässt sich daraus nicht ableiten.'},
               {'label':'Zusätzliche Straßendaten','text':'Die zusätzliche KBA-Statistik VD3c unterscheidet 20 Güterabteilungen für deutsche Güterkraftfahrzeuge auf einer anderen regionalen Ebene. Diese Angaben lassen sich nicht als Aufteilung einzelner Kreisprofile oder Straßenverbindungen verwenden.'}]
    elif topic=='source_flags':
        texts=[{'label':'Nullwerte','text':'Eine veröffentlichte Null kann durch Rundung entstehen. In den verwendeten KBA-Tabellen steht das Zeichen 0 für eine gerundete Null; es belegt deshalb nicht, dass tatsächlich kein Verkehr stattgefunden hat.'},
               {'label':'Quellenzeichen','text':'In den verwendeten KBA-Produkten liefern / und . keinen belastbaren Zahlenwert. Das Zeichen - bedeutet nichts vorhanden; Klammern kennzeichnen einen eingeschränkt belastbaren Wert. Die Bedeutung ist immer anhand der jeweiligen Quelle zu prüfen.'},
               {'label':'Fehlende Angaben','text':'Wenn eine Verbindung oder Gütergruppe in der Veröffentlichung fehlt, ist in dieser Statistik kein nutzbarer Wert erfasst beziehungsweise veröffentlicht. Das wird nicht als numerische Null behandelt und beweist nicht, dass tatsächlich kein Verkehr stattfand.'}]
    elif topic=='regional_vs_national':
        texts=[{'label':'Regionen und Deutschland','text':'Der Regionalbestand enthält neben Kreisprofilen zusätzliche Gebietseinträge. Seine Summe entspricht daher nicht dem Deutschlandwert. Für Deutschland wird eine eigene nationale Statistik verwendet.'},
               {'label':'Unterschiedliche Zählweise','text':'Verkehr innerhalb einer Region wird sowohl beim Versand als auch beim Empfang gezählt. Nationale Statistiken und Prognosen verwenden eigene Zählweisen. Die Summen sind deshalb nicht unmittelbar vergleichbar.'},
               {'label':'Gütermenge und Verkehrsleistung','text':'Tonnen messen die Gütermenge. Tonnenkilometer berücksichtigen zusätzlich die Transportentfernung. Ein regionaler Wert zeigt dabei nicht automatisch die ausschließlich innerhalb Deutschlands erbrachte Verkehrsleistung.'}]
        if regional_scope:
            year = regional_scope['year']
            count = regional_scope['entry_count']
            districts = regional_scope['district_count']
            others = len(regional_scope['other_codes'])
            assert count == districts + others
            texts.insert(1, {'label': f'Beispiel {year}',
                            'text': f'Für {year} enthält der Regionalbestand {count} Gebietseinträge: {districts} Kreise und kreisfreie Städte sowie {others} zusätzliche Einträge anderer Gebietsebenen, darunter Deutschland insgesamt. Wer alle Einträge addiert, zählt damit überlappende Gebiete mehrfach. Auch die Summe der Kreiswerte ersetzt wegen der unterschiedlichen Zählweise nicht automatisch die nationale Statistik.',
                            'source': 'D01-Regionalbestand und NUTS-3-Gebietsstand 2024',
                            'evidence': regional_scope})
    else:
        texts=[{'label':'Zusätzliche Daten erforderlich','text':'Transportkosten, Umweltbilanzen, freie Kapazitäten und die Auslastung einzelner Terminals lassen sich aus diesen Verkehrsstatistiken nicht bestimmen. Auch die betrieblich gewinnbare Transportmenge ist damit nicht belegt. Dafür sind zusätzliche Daten erforderlich.'}]
    return {'status':'out_of_scope' if topic=='outside_scope' else 'available','text_facts':texts,
            'scope':'Gebundener C-Crosswalk und feste fachliche Grenzen der vorhandenen Statistikprodukte.',
            'note':'Keine externe Datenergänzung; Aussagen zu konkreten Werten erfordern eine eigene bestätigte Datenabfrage. Eine gemeinsame Güterklassifikation belegt noch keine Vergleichbarkeit von Ist und Prognose oder verschiedenen Fahrzeugpopulationen.'}
