"""Verständliche Kundenausgabe aus belegten Fakten; technische Belege separat."""
import json
import re

FIELD_LABELS={
    'region':'Welche Stadt oder Region möchten Sie betrachten?',
    'regions':'Welche Regionen möchten Sie miteinander vergleichen?',
    'origin':'Wo beginnt die Verbindung?', 'destination':'Wo endet die Verbindung?',
    'partner':'Welche zweite Region gehört zu der Verbindung?',
    'year':'Auf welches Jahr bezieht sich Ihre Frage?',
    'years':'Welche Jahre möchten Sie vergleichen?', 'observed_years':'Welche beobachteten Jahre möchten Sie betrachten?',
    'start':'Mit welchem Jahr soll der Vergleich beginnen?', 'end':'Mit welchem Jahr soll der Vergleich enden?',
    'mode':'Welchen Verkehrsträger meinen Sie: Straße, Schiene oder Binnenschiff?',
    'modes':'Welche Verkehrsträger möchten Sie betrachten?',
    'metric':'Welche Kennzahl interessiert Sie, zum Beispiel Gütermenge oder Verkehrsleistung?',
    'metrics':'Welche Kennzahlen möchten Sie vergleichen?',
    'direction':'Geht es um Versand, Empfang oder beide Richtungen?',
    'directions':'Welche Verkehrsrichtungen möchten Sie vergleichen?',
    'group':'Welche Gütergruppe möchten Sie betrachten?', 'top':'Wie viele Spitzenwerte möchten Sie sehen?',
    'node':'Welchen Hafen oder Flughafen meinen Sie?', 'ags':'Welche Gemeinde möchten Sie betrachten?',
    'month':'Welchen Monat möchten Sie betrachten?', 'comparison_month':'Mit welchem Monat soll verglichen werden?',
    'minimum_base':'Ab welcher Ausgangsmenge sollen Verbindungen berücksichtigt werden?',
    'measure':'Interessiert Sie die Veränderung als Menge oder in Prozent?'}
MODES={'road':'Straße','rail':'Schiene','iww':'Binnenschiff','total':'alle Verkehrsträger'}
DIRECTIONS={'outbound':'Versand','inbound':'Empfang','all':'beide Richtungen','internal':'Binnenverkehr','total':'beide Richtungen'}
UNITS={'t':'Tonnen','tonnes':'Tonnen','tkm':'Tonnenkilometer','trips':'Fahrten','flights':'Flüge','load_units':'Ladeeinheiten','%':'%','teu':'TEU'}


def number(value):
    if value is None: return 'Keine Angabe'
    decimals=0 if float(value).is_integer() else 2
    return f'{value:,.{decimals}f}'.replace(',','\x00').replace('.',',').replace('\x00','.')


def name(code,datasets):
    names=datasets.names.get(str(code),[])
    if names:
        return min(names,key=len)
    return {'11000000':'Berlin','DE':'Deutschland'}.get(str(code),str(code))


def friendly_label(row,datasets,groups):
    text=row.get('label','Kennwert')
    text=re.sub(r'\bDE[A-Z0-9]{1,4}\b',lambda match:name(match.group(),datasets),text)
    words={**MODES,**DIRECTIONS,'Ist':'Beobachteter Wert','2019_BASE':'Prognosebasis 2019','2040_P1':'Prognose 2040'}
    for before,after in words.items():
        text=re.sub(r'(?<!\w)'+re.escape(before)+r'(?!\w)',after,text)
    for code,label in groups.items():
        text=text.replace('C'+code+' '+label,label)
        text=re.sub(r'\bC'+re.escape(code)+r'\b',label,text)
    return (text.replace('veröffentlichte Zeilensumme','veröffentlichte Gütermenge')
                .replace('Summe bekannter veröffentlichter Feinpositionen','Summe der verfügbaren Güterangaben')
                .replace('Regionalgesamt','Güteraufkommen').replace(' / ',' · '))


def present(result,datasets):
    """A separate display contract leaves the original result available for audit."""
    status=result['status']; function=result.get('function_id'); p=result.get('parameters',{})
    answer={'title':'Ihre Auswertung','paragraphs':[],'questions':[],'tables':[],'notes':[],
            'sources':result.get('sources',[]),
            'technical_details':{'data_snapshot_id':result.get('data_snapshot_id'),
                                 'result_id':result.get('result_id'),'parameters':p,
                                 'original_notices':result.get('notices',[]),
                                 'original_sources':result.get('sources',[])}}
    if status=='needs_clarification':
        answer['title']='Noch eine kurze Rückfrage'
        answer['paragraphs']=['Für eine passende Antwort fehlen mir noch wichtige Angaben. Bitte ergänzen Sie:']
        answer['questions']=list(dict.fromkeys(FIELD_LABELS[k] for k in result.get('missing_fields',[]) if k in FIELD_LABELS))
        if not answer['questions']:
            answer['paragraphs']=['Ich konnte Ihre Frage noch nicht eindeutig zuordnen. Bitte beschreiben Sie kurz, welche Auswertung Sie benötigen.']
        if result.get('available_years'):
            latest=max(result['available_years'])
            answer['questions']=[f'Für dieses Datenprodukt ist {latest} das neueste vollständig verfügbare Jahr. Möchten Sie dieses Jahr oder einen früheren Jahrgang verwenden?' if q==FIELD_LABELS['year'] else q for q in answer['questions']]
            answer['replies']=[{'label':f'Neuestes Jahr ({latest}) verwenden','question':str(latest)}]
        return answer
    if status=='error':
        answer['title']='Die Auswertung hat gerade nicht geklappt'
        code=result.get('diagnostic_code')
        answer['paragraphs']=['Ihre Frage konnte wegen eines technischen Problems nicht beantwortet werden. Bitte versuchen Sie es später noch einmal. Diese fehlgeschlagene Auswertung zählt nicht zu Ihrem Monatskontingent.'+((' Fehlerkennung: '+code+'.') if code else '')]
        return answer
    if status=='not_available':
        answer['title']='Für diese Auswahl fehlt eine belastbare Zahlenangabe'
        source_status = result.get('source_status')
        reason = {'missing_row':'Im vorhandenen Datenbestand gibt es für diese Verbindung oder Auswahl keinen veröffentlichten Eintrag.',
                  'not_available':'Die angefragte Auswahl ist durch dieses Datenprodukt nicht abgedeckt.',
                  'suppressed':'Der Wert ist in der Quelle unterdrückt und kann nicht beziffert werden.',
                  'partial':'Die vorhandenen Quellzeilen enthalten unbekannte Werte; eine vollständige Menge lässt sich deshalb nicht angeben.'}.get(source_status,
                  'Die gewünschte Auswertung kann ich mit dem derzeit vorbereiteten Datenangebot noch nicht liefern.')
        answer['paragraphs']=[reason+' Daraus lässt sich nicht schließen, dass kein Verkehr stattfindet.']
        if p.get('year'): answer['notes'].append('Angefragtes Bezugsjahr: '+str(p['year'])+'.')
        answer['suggestions']=[]; answer['followups']=[]
        for check in result.get('related_data',{}).get('checks',{}).values():
            if not check.get('available'): continue
            alt=check['parameters']; mode=MODES.get(alt.get('mode'),'Schiene')
            origin=alt.get('origin') or alt.get('region'); destination=alt.get('destination') or alt.get('partner')
            text=f"Für {mode} im Jahr {alt['year']} ist eine Zahlenangabe für diese Auswahl vorhanden."
            answer['paragraphs'].append(text)
            question=f"Zeige die verfügbare Auswertung von {name(origin,datasets)} nach {name(destination,datasets)} für {mode} {alt['year']}."
            answer['suggestions'].append(question)
            answer['followups'].append({'question':question,'function_id':check['function_id'],'parameters':alt})
        answer['notes'].append('Eine vorgeschlagene Alternative ändert die genannte Auswahl und wird erst auf Ihre nächste Frage hin ausgewertet.') if answer['suggestions'] else None
        return answer
    if status=='out_of_scope':
        answer['title']='Das lässt sich mit diesen Daten nicht beantworten'
        answer['paragraphs']=['Die vorhandenen Verkehrsstatistiken enthalten keine Angaben zu Transportkosten, Umweltbilanzen oder zur Auslastung einzelner Terminals. Dafür sind zusätzliche Daten nötig; aus den Gütermengen allein lassen sich diese Fragen nicht beantworten.']
        return answer
    groups={}
    if 'b03' in datasets.paths:
        groups=json.loads((datasets.paths['b03']/'classification.json').read_text(encoding='utf-8'))['groups']
    facts=result.get('facts',[])
    labels={f['fact_id']:friendly_label(f,datasets,groups) for f in facts}
    # The audit result retains every fact. Display only one classification level:
    # grouped goods by default, or fine positions when explicitly selected.
    display_facts=facts
    if function=='rail_goods':
        display_facts=[f for f in facts if f.get('sum_scope') or (
            bool(f.get('nst_raw')) if p.get('nst') else
            not f.get('nst_raw') and (p.get('group','ALL')=='ALL' or f.get('group')==p['group']))]
        for f in display_facts:
            if f.get('group') and not f.get('nst_raw'):
                labels[f['fact_id']]=groups.get(f['group'],labels[f['fact_id']])
    if display_facts:
        rows=[]
        for f in display_facts:
            notes=[]
            if function=='rail_goods' and f.get('sum_scope'):
                notes.append('Summe der bekannten veröffentlichten Einzelmengen; fehlende Werte sind nicht als null enthalten.')
            if f['value'] is None:
                notes.append({'missing_row':'In dieser Statistik ist für diese Auswahl kein nutzbarer Wert erfasst beziehungsweise veröffentlicht.',
                              'suppressed':'In der Quelle unterdrückter Wert.',
                              'missing_value':'Quellwert unbekannt oder nicht veröffentlicht.'}.get(f.get('value_status'), 'In dieser Statistik ist kein nutzbarer Wert erfasst beziehungsweise veröffentlicht.'))
            if f.get('quality_status')=='restricted': notes.append('Laut Quelle eingeschränkt belastbar.')
            if f['value']==0: notes.append('Veröffentlichte Null; möglicherweise gerundet.')
            rows.append({'label':labels[f['fact_id']],'value':number(f['value']),
                         'unit':UNITS.get(f.get('unit'),f.get('unit','')),
                         'note':' '.join(notes),'fact_ids':[f['fact_id']]})
        answer['tables']=[{'title':'Ergebnisse im Überblick','columns':['Kennwert','Wert','Einheit','Hinweis'],'rows':rows,
                           'collapsed':len(rows)>8,'row_count':len(rows)}]
        if function=='rail_goods':
            answer['tables'][0].update(title='Güterpositionen im Überblick' if p.get('nst') else 'Güterarten im Überblick',
                                      columns=['Güterposition' if p.get('nst') else 'Güterart','Menge','Einheit','Hinweis'])
    selected={s['text']:s for s in result.get('statements',[])}
    by_id={f['fact_id']:f for f in display_facts}
    for text in result.get('summary',[]):
        statement=selected.get(text)
        ids=statement.get('fact_ids',[]) if statement else []
        if function=='rail_goods' and (not ids or any(fid not in by_id for fid in ids)):
            continue
        if statement and statement.get('role')=='fact' and len(ids)==1 and ids[0] in by_id:
            f=by_id[ids[0]]
            if f['value'] is not None:
                answer['paragraphs'].append('Für '+labels[ids[0]]+' weist die Statistik '+number(f['value'])+' '+UNITS.get(f.get('unit'),f.get('unit',''))+' aus.')
        else:
            answer['paragraphs'].append(text)
    region=name(p.get('region'),datasets) if p.get('region') else None
    if region:
        answer['title']='Ihre Auswertung für '+region+(f" ({p['year']})" if p.get('year') else '')
        if function=='rail_goods' and p.get('partner'):
            other=name(p['partner'],datasets)
            route=(other+' nach '+region) if p.get('direction')=='inbound' else (region+' nach '+other)
            answer['title']=('Güterverkehr auf der Schiene zwischen '+region+' und '+other if p.get('direction')=='total' else 'Güterverkehr auf der Schiene von '+route)+f" ({p['year']})"
    elif p.get('node'):
        node_name = datasets.airport_names.get(p['node'],p['node']) if p.get('kind')=='air' else name(p['node'],datasets)
        answer['title']='Ihre Auswertung für '+node_name+(f" ({p['year']})" if p.get('year') else '')
    elif function in {'relation_matrix','relation_history'} and p.get('origin') and p.get('destination'):
        origin,destination=name(p['origin'],datasets),name(p['destination'],datasets)
        period=(f" ({p['start']}–{p['end']})" if function=='relation_history' else f" ({p['year']})")
        answer['title']=f'Güterverkehr von {origin} nach {destination}'+period
    introductions={
        'region_profile':'Die folgenden Kennwerte beschreiben das Güterverkehrsprofil Ihrer Region.',
        'regional_modal_split':'Die Auswertung zeigt, wie sich der Verkehr auf Straße, Schiene und Binnenschiff verteilt.',
        'compare_regions':'Die Gegenüberstellung zeigt die Kennwerte der ausgewählten Regionen. Die vollständigen Ergebnisse finden Sie in der Tabelle.',
        'relation_history':'Die Auswertung stellt die veröffentlichten Jahreswerte der Verbindung nach Verkehrsträgern getrennt gegenüber.',
        'rail_goods':'Für die gewählte Schienenverbindung sind die folgenden Güterangaben veröffentlicht.',
        'rail_goods_history':'Die Tabelle stellt die veröffentlichten Güterangaben der gewählten Jahre nebeneinander.',
        'regional_history':'Die Jahreswerte zeigen den veröffentlichten Verlauf. Bitte beachten Sie die Hinweise zur Vergleichbarkeit.',
        'modal_history':'Hier sehen Sie die verfügbaren Verkehrsanteile der gewählten Jahre im Vergleich.',
        'node_partners':'Die Tabelle zeigt die größten veröffentlichten Partnerverbindungen Ihrer Auswahl.',
        'partner_ranking':'Diese Partner gehören nach den veröffentlichten Mengen zur Spitzengruppe Ihrer Auswahl.',
        'goods_structure':'Die Auswertung zeigt, welche Gütergruppen den Versand beziehungsweise Empfang der Region prägen.',
        'forecast_ranking':'Die Tabelle zeigt die größten Veränderungen innerhalb des gewählten Prognoseszenarios.',
        'forecast_comparison':'Hier werden die beobachteten Kennwerte und die Prognose getrennt gegenübergestellt.',
        'intermodal_markets':'Die Ergebnisse zeigen die ausgewählten intermodalen Teilmärkte jeweils getrennt.',
        'balance':'Die Auswertung stellt Versand und Empfang gegenüber. Der Saldo ist die Differenz zwischen beiden Mengen.',
        'toll_month':'Die folgenden Angaben zeigen die veröffentlichten mautpflichtigen Fahrten für den gewählten Monat.'}
    # Analytical statements already explain the result in a question-specific
    # way. The generic introduction is only a last-resort bridge for functions
    # that could not produce such a statement; otherwise it interrupts the
    # answer between its main finding and its supporting interpretation.
    if function in introductions and not answer['paragraphs']:
        answer['paragraphs'].append(introductions[function])
    if function=='road_relation_goods_limit':
        origin,destination=name(p['origin'],datasets),name(p['destination'],datasets)
        answer['title']=f'Straßengüterverkehr von {origin} nach {destination}'
        value=facts[0]['value'] if facts else None
        answer['paragraphs']=[f'Welche Güter im Straßenverkehr von {origin} nach {destination} transportiert werden, lässt sich mit diesen Daten nicht aufschlüsseln: Die zugrunde liegende Statistik enthält für einzelne Straßenverbindungen nur Gesamtmengen über alle Güterarten.']
        if value is not None:
            answer['paragraphs'].append(f"Für {p['year']} sind insgesamt {number(value)} {UNITS.get(facts[0]['unit'],facts[0]['unit'])} über alle Güterarten veröffentlicht. Dieser Wert ist laut Quelle nur eingeschränkt belastbar." if facts[0].get('quality_status')=='restricted' else
                f"Für {p['year']} sind insgesamt {number(value)} {UNITS.get(facts[0]['unit'],facts[0]['unit'])} über alle Güterarten veröffentlicht.")
        answer['notes']=['Die Güterverteilung der beteiligten Regionen lässt sich nicht auf diese einzelne Verbindung übertragen. Die Daten zeigen außerdem nicht, welche Straßen tatsächlich befahren wurden.']
        related=result.get('related_data') or {}
        if related.get('data_snapshot_id')==datasets.snapshot_id:
            answer['technical_details']['related_data']=related
            checks=related.get('checks',{})
            suggestions=[]
            followups=[]
            if checks.get('rail',{}).get('available'):
                answer['paragraphs'].append(f'Für dieselbe Verbindung auf der Schiene liegen für {p["year"]} dagegen veröffentlichte Güterangaben vor. Die Einschränkung betrifft hier also die Straßenstatistik, nicht sämtliche Verkehrsträger.')
                suggestions.append(f'Welche Güter wurden {p["year"]} auf der Schiene von {origin} nach {destination} transportiert?')
                followups.append({'question':suggestions[-1],'function_id':checks['rail']['function_id'],'parameters':checks['rail']['parameters']})
            iww=checks.get('iww',{})
            if iww.get('status')=='missing_row':
                answer['paragraphs'].append(f'Für das Binnenschiff fehlt für diese Richtung und das Jahr {p["year"]} eine veröffentlichte Datenzeile. Ob tatsächlich kein Verkehr stattfand oder warum die Angabe fehlt, lässt sich daraus nicht feststellen.')
            elif iww.get('available'):
                answer['paragraphs'].append(f'Für das Binnenschiff liegt für diese Verbindung und das Jahr {p["year"]} ebenfalls eine veröffentlichte Mengenangabe vor.')
            for key,place,direction in [('origin_goods',origin,'Versand'),('destination_goods',destination,'Empfang')]:
                if checks.get(key,{}).get('available'):
                    suggestions.append(f'Welche Güter prägen {p["year"]} den gesamten {direction} im Straßenverkehr von {place}?')
                    followups.append({'question':suggestions[-1],'function_id':checks[key]['function_id'],'parameters':checks[key]['parameters']})
            if suggestions:
                answer['suggestions']=suggestions
                answer['followups']=followups
            if any(checks.get(key,{}).get('available') for key in ['origin_goods','destination_goods']):
                answer['notes'].append('Die vorgeschlagenen regionalen Güterprofile umfassen den gesamten Straßenversand beziehungsweise Straßenempfang einschließlich innerregionaler Transporte. Sie zeigen keine Güteraufteilung dieser einzelnen Verbindung.')
            if any(c.get('status')=='not_checked' for c in checks.values()):
                answer['notes'].append('Weitere passende Auswertungen konnten gerade nicht vollständig auf Verfügbarkeit geprüft werden.')
        if answer['tables']: answer['tables'][0]['rows'][0]['label']=f'{origin} → {destination} · {p["year"]} · alle Güterarten'
    elif function in {'region_profile','regional_modal_split','compare_regions','modal_history','regional_history'}:
        answer['notes'].append('Verkehr innerhalb einer Region zählt bei Versand und Empfang jeweils mit. Die Summe beider Richtungen ist deshalb nicht die Menge eindeutig verschiedener Transporte.')
        if function in {'regional_history','modal_history'}:
            answer['notes'].append('Eine ausgewiesene Veränderungsrate ist aus den veröffentlichten Werten berechnet. Sie ist nicht um Gebiets-, Erfassungs- oder Revisionsbrüche bereinigt und erklärt keine Ursache.')
    elif function in {'relation','relation_matrix','relation_history','rail_goods','rail_goods_history','time_series'}:
        answer['notes'].append('Wo kein Wert vorliegt, ist in der zugrunde liegenden Statistik kein nutzbarer Verkehrswert erfasst beziehungsweise veröffentlicht. Das beweist nicht, dass tatsächlich kein Verkehr stattfand.')
        if function in {'relation_history','rail_goods_history','time_series'}:
            answer['notes'].append('Eine ausgewiesene Veränderungsrate wird transparent aus vorhandenen veröffentlichten Werten berechnet. Sie ist nicht methodisch bereinigt und belegt keine Ursache.')
    elif function=='node_partners':
        if p['kind']=='air':
            answer['notes'].append('Die Anteile beziehen sich auf alle veröffentlichten Partnerverbindungen der Auswahl, nicht auf das gesamte Luftfrachtaufkommen des Flughafens. Kleinere Verbindungen können wegen Veröffentlichungsschwellen fehlen.')
        else:
            answer['notes'].append('Die Anteile beziehen sich auf die veröffentlichten Verbindungen der Auswahl. Ein- und Ausladung werden bei beiden Richtungen zusammengezählt; TEU beschreiben ausschließlich Containerverkehre.')
    elif function=='partner_ranking':
        answer['notes'].append('Die Anteile beziehen sich auf alle veröffentlichten Partner der Auswahl. Die Tabelle zeigt nur die ausgewählte Spitzengruppe; gleich hohe Werte teilen sich einen Rang.')
    elif function=='intermodal_markets':
        answer['notes'].append('Schiene und Binnenschiff beschreiben getrennte Teilmärkte. Ihre Mengen lassen sich nicht zu einer eindeutigen Gesamtmenge addieren. Auch ein mögliches Verlagerungspotenzial ist damit nicht nachgewiesen.')
    elif function=='toll_month':
        answer['title']='Mautpflichtige Fahrten in '+name(p.get('ags'),datasets)
        answer['notes'].append('Fahrten innerhalb Berlins erscheinen sowohl bei Start als auch bei Ziel. Bei den eindeutig gezählten Fahrten werden sie nur einmal berücksichtigt.')
        if p.get('comparison_month') and status=='partial':
            answer['notes'].append('Für den gewählten Vergleichsmonat liegen im lokalen Bestand keine passenden Daten vor. Deshalb kann ich die Veränderung gegenüber diesem Monat noch nicht berechnen.')
    elif function=='road_details':
        answer['notes'].append('Diese Auswertung bezieht sich auf deutsche Güterkraftfahrzeuge und die räumliche Abgrenzung der zugrunde liegenden Straßenverkehrsstatistik. Sie ist keine vollständige Aufteilung einzelner Straßenverbindungen.')
        answer['notes'].append('Ausgewählt sind '+('Fahrten innerhalb Deutschlands.' if p.get('population')=='I' else 'die Gesamtverkehre der genannten Fahrzeuggruppe.'))
    if function in {'forecast_comparison','forecast_ranking'} or p.get('include_forecast'):
        answer['notes'].append('Die Prognose vergleicht das Basisszenario 2019 mit dem Szenario für 2040. Das sind Modellannahmen, keine beobachtete Entwicklung und keine sichere Vorhersage. Beobachtete Werte bleiben davon getrennt.')
    if function=='goods_structure':
        answer['notes'].append('Die Gütergruppen beschreiben die ausgewählte Region. Ihre Anteile lassen sich nicht als Güterverteilung einer einzelnen Verbindung lesen.')
    if status=='partial' and function!='road_relation_goods_limit':
        answer['notes'].append('Ein Teil der gewünschten Angaben fehlt oder ist nur eingeschränkt nutzbar. Fehlende Werte werden in der Tabelle ausdrücklich angezeigt und nicht durch null ersetzt.')
    if any(f.get('quality_status')=='restricted' for f in facts) and function!='road_relation_goods_limit':
        answer['notes'].append('Die Quelle kennzeichnet einzelne Werte als eingeschränkt belastbar. Bitte beachten Sie die Hinweise in der Tabelle.')
    answer['notes']=list(dict.fromkeys(answer['notes']))
    return answer
