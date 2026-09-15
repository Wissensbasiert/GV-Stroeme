"""Verständliche Kundenausgabe aus belegten Fakten; technische Belege separat."""
import json
import re

FIELD_LABELS={
    'region':'Welche Stadt oder Region möchten Sie betrachten?',
    'regions':'Welche Regionen möchten Sie miteinander vergleichen?',
    'origin':'Wo beginnt die Verbindung?', 'destination':'Wo endet die Verbindung?',
    'partner':'Welche zweite Region gehört zu der Verbindung?',
    'partners':'Welche konkreten Flughäfen oder Häfen gehören zu der Verbindung?',
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
MODES={'road':'Straße','rail':'Schiene','iww':'Binnenschiff','sea':'Seeverkehr','total':'Summe der ausgewählten Verkehrsträger','subtotal':'Bekannte Teilsumme'}
DIRECTIONS={'outbound':'Versand','inbound':'Empfang','all':'beide Richtungen','internal':'Binnenverkehr','total':'beide Richtungen'}
UNITS={'t':'Tonnen','tonnes':'Tonnen','tkm':'Tonnenkilometer','trips':'Fahrten','flights':'Flüge','load_units':'Ladeeinheiten','Ladeeinheiten':'Ladeeinheiten','Fahrten':'Fahrten','%':'%','teu':'TEU','TEU':'TEU'}


def number(value):
    if value is None: return 'Keine Angabe'
    decimals=0 if float(value).is_integer() else 2
    return f'{value:,.{decimals}f}'.replace(',','\x00').replace('.',',').replace('\x00','.')


def name(code,datasets):
    names=datasets.names.get(str(code),[])
    if names:
        return min(names,key=len)
    return getattr(datasets,'forecast_cell_names',{}).get(str(code),{'11000000':'Berlin','DE':'Deutschland'}.get(str(code),str(code)))


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
        reason = {'AA-M01': 'Der KI-Dienst hat gerade keine vollständige Antwort geliefert.',
                  'AA-D02': 'Die Datenabfrage konnte gerade nicht abgeschlossen werden.',
                  'AA-R01': 'Die Datenantwort konnte gerade nicht aufbereitet werden.',
                  'AA-F01': 'Die Antwort des KI-Dienstes konnte nicht verarbeitet werden.'}.get(code,
                  'Ihre Frage konnte wegen eines technischen Problems nicht beantwortet werden.')
        answer['paragraphs']=[reason+' Bitte versuchen Sie es später noch einmal. Diese fehlgeschlagene Auswertung zählt nicht zu Ihrem Monatskontingent.'+((' Fehlerkennung: '+code+'.') if code else '')]
        return answer
    if status=='not_available' and not (function in {'relation_history','node_connections'} and result.get('facts')):
        answer['title']='Für diese Auswahl fehlt eine belastbare Zahlenangabe'
        source_status = result.get('source_status')
        reason = {'missing_row':'Im vorhandenen Datenbestand gibt es für diese Verbindung oder Auswahl keinen veröffentlichten Eintrag.',
                  'not_available':'Die angefragte Auswahl ist durch dieses Datenprodukt nicht abgedeckt.',
                  'suppressed':'Der Wert ist in der Quelle unterdrückt und kann nicht beziffert werden.',
                  'partial':'Die vorhandenen Quellzeilen enthalten unbekannte Werte; eine vollständige Menge lässt sich deshalb nicht angeben.'}.get(source_status,
                  'Die gewünschte Auswertung kann ich mit dem derzeit vorbereiteten Datenangebot noch nicht liefern.')
        answer['paragraphs']=[reason+' Daraus lässt sich nicht schließen, dass kein Verkehr stattfindet.']
        coverage = next((n for n in result.get('notices', []) if n.startswith('Für das angefragte Jahr ')), None)
        if coverage:
            answer['paragraphs'] = [coverage]
        if p.get('year'): answer['notes'].append('Angefragtes Bezugsjahr: '+str(p['year'])+'.')
        if function in {'node_statistics','node_profile','node_partners'}:
            answer['notes'].extend(n for n in result.get('notices',[]) if not n.startswith('Datenstand:'))
        answer['suggestions']=[]; answer['followups']=[]
        for check in result.get('related_data',{}).get('checks',{}).values():
            if not check.get('available'): continue
            alt=check['parameters']; mode=MODES.get(alt.get('mode'),'die gewählten Verkehrsträger' if check['function_id']=='relation_overview' else 'Schiene')
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
    groups={}; divisions={}
    if 'b03' in datasets.paths:
        classification=json.loads((datasets.paths['b03']/'classification.json').read_text(encoding='utf-8'))
        groups=classification['groups']
        divisions={code:item['name'] for code,item in classification['divisions'].items()}
    facts=result.get('facts',[])
    labels={f['fact_id']:friendly_label(f,datasets,groups) for f in facts}
    # The audit result retains every fact. Display only one classification level:
    # grouped goods by default, or fine positions when explicitly selected.
    display_facts=facts
    if function=='rail_goods':
        display_facts=[f for f in facts if f.get('sum_scope') or p.get('group','ALL')=='ALL' or f.get('group')==p['group']]
        for f in display_facts:
            if f.get('group_name'): labels[f['fact_id']]=f['group_name']
    if display_facts:
        rows=[]
        for f in display_facts:
            notes=[]
            if function=='rail_goods' and f.get('sum_scope'):
                notes.append('Summe der bekannten veröffentlichten Einzelmengen; fehlende Werte sind nicht als null enthalten.')
            if f['value'] is None:
                notes.append({'missing_row':'Kein eigener Eintrag für diese Verbindung.',
                              'not_available':'Jahrgang für diese Auswahl nicht verfügbar.',
                              'suppressed':'In der Quelle unterdrückter Wert.',
                              'not_applicable':'Für diesen Verkehr ist die Kennzahl nicht anwendbar; keine veröffentlichte Null.',
                              'not_computable':'Prozentuale Veränderung bei Ausgangswert null nicht berechenbar.',
                              'missing_value':'Quellwert unbekannt oder nicht veröffentlicht.'}.get(f.get('value_status'), 'In dieser Statistik ist kein nutzbarer Wert erfasst beziehungsweise veröffentlicht.'))
            if f.get('quality_status')=='restricted': notes.append('Laut Quelle eingeschränkt belastbar.')
            if f['value']==0: notes.append('Veröffentlichte Null; möglicherweise gerundet.')
            rows.append({'label':labels[f['fact_id']],'value':number(f['value']),
                         'unit':UNITS.get(f.get('unit'),f.get('unit','')),
                         'note':' '.join(notes),'fact_ids':[f['fact_id']]})
        answer['tables']=[{'title':'Ergebnisse im Überblick','columns':['Kennwert','Wert','Einheit','Hinweis'],'rows':rows,
                           'collapsed':len(rows)>8,'row_count':len(rows)}]
        if function=='relation_history':
            answer['tables'][0].update(title='Jahreswerte im Detail',collapsed=len(rows)>2,
                                      columns=['Jahr · Verkehrsträger','Wert','Einheit','Einordnung'])
        if function=='rail_goods':
            answer['tables'][0].update(title=('C7-Gütergruppen' if p.get('classification')=='C7' else 'NST-2007-Abteilungen')+' im Überblick',
                                      columns=['Gütergruppe','Menge','Einheit','Hinweis'])
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
    if function=='rail_goods_history':
        start,end=p['years']
        comparison_rows=[]
        group_codes=list(groups) if p['classification']=='C7' else list(divisions)
        for code in group_codes:
            first=next((f for f in facts if f.get('group')==code and f.get('year')==start),None)
            last=next((f for f in facts if f.get('group')==code and f.get('year')==end),None)
            if not first or not last or (first['value'] is None and last['value'] is None): continue
            absolute=next((f for f in facts if f.get('group')==code and f.get('change')=='absolute'),None)
            relative=next((f for f in facts if f.get('group')==code and f.get('change')=='relative'),None)
            values=number(first['value'])+' → '+number(last['value'])
            if absolute:
                sign='+' if absolute['value']>0 else '−' if absolute['value']<0 else '±'
                change=sign+number(abs(absolute['value']))+' '+UNITS.get(absolute['unit'],absolute['unit'])
                if relative and relative['value'] is not None:
                    change+=' ('+('+' if relative['value']>0 else '−' if relative['value']<0 else '±')+number(abs(relative['value']))+' %)'
            else: change='Nicht vergleichbar, weil mindestens ein Randjahreswert fehlt.'
            comparison_rows.append({'label':first.get('group_name') or labels[first['fact_id']],
                'value':values,'unit':UNITS.get(first['unit'],first['unit']),'note':change,
                'fact_ids':[f['fact_id'] for f in [first,last,absolute,relative] if f]})
        answer['tables']=[{'title':('C7-Gütergruppen' if p['classification']=='C7' else 'NST-2007-Abteilungen')+' im Vergleich',
            'columns':['Gütergruppe',str(start)+' → '+str(end),'Einheit','Veränderung'],
            'rows':comparison_rows,'collapsed':len(comparison_rows)>8,'row_count':len(comparison_rows)}]
    region=name(p.get('region'),datasets) if p.get('region') else None
    if region:
        answer['title']='Ihre Auswertung für '+region+(f" ({p['year']})" if p.get('year') else '')
        if function in {'rail_goods','rail_goods_history'} and p.get('partner'):
            other=name(p['partner'],datasets)
            route=(other+' nach '+region) if p.get('direction')=='inbound' else (region+' nach '+other)
            period=str(p['year']) if p.get('year') else str(p['years'][0])+'–'+str(p['years'][1])
            answer['title']=('Güterverkehr auf der Schiene zwischen '+region+' und '+other if p.get('direction')=='total' else 'Güterverkehr auf der Schiene von '+route)+f" ({period})"
    elif p.get('node'):
        node_name = datasets.airport_names.get(p['node'],p['node']) if p.get('kind')=='air' else name(p['node'],datasets)
        answer['title']='Ihre Auswertung für '+node_name+(f" ({p['year']})" if p.get('year') else '')
        if function=='node_connections':
            partner_name=(datasets.airport_groups[p['partner_group']]['name'] if p.get('partner_group') else
                          ', '.join(datasets.airport_names.get(c,c) if p['kind']=='air' else c for c in p['partners']))
            endpoints=(partner_name,node_name) if p['direction']=='inbound' else (node_name,partner_name)
            answer['title']=(' ↔ ' if p['direction']=='all' else ' → ').join(endpoints)+f" ({p['year']})"
    elif function in {'relation_matrix','relation_history','relation_overview'} and p.get('origin') and p.get('destination'):
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
    if function=='relation_overview':
        totals=[f for f in facts if f.get('group')=='ALL']
        answer['paragraphs']=[]
        for metric in p['metrics']:
            selected=[f for f in totals if f.get('metric')==metric and f['value'] is not None]
            missing=[f for f in totals if f.get('metric')==metric and f['value'] is None]
            label='Gütermenge' if metric=='tonnes' else 'Verkehrsleistung'
            if selected:
                answer['paragraphs'].append(f'{label} {p["year"]} von {name(p["origin"],datasets)} nach {name(p["destination"],datasets)}: '+
                    '; '.join(MODES[f['mode']]+' '+number(f['value'])+' '+UNITS[f['unit']] for f in selected)+'.')
            if missing:
                answer['paragraphs'].append('Für '+', '.join(MODES[f['mode']] for f in missing)+f' ist für {p["year"]} keine nutzbare {label} dieser Verbindung verfügbar.')
        if p['include_goods']:
            for mode in p['modes']:
                if mode=='road':
                    answer['paragraphs'].append('Die Güterarten der Straßenverbindung lassen sich mit dieser Statistik nicht aufschlüsseln; sie enthält hier ausschließlich Gesamtwerte.')
                    continue
                metric='tonnes' if 'tonnes' in p['metrics'] else p['metrics'][0]
                known=[f for f in facts if f.get('mode')==mode and f.get('metric')==metric and f.get('group')!='ALL' and f['value'] is not None]
                ranked=sorted(known,key=lambda f:f['value'],reverse=True)
                if ranked:
                    answer['paragraphs'].append('Bei '+MODES[mode]+' sind folgende Gütergruppen mit den größten veröffentlichten Werten erfasst: '+
                        '; '.join(groups.get(f['group'],'C'+f['group'])+' ('+number(f['value'])+' '+UNITS[f['unit']]+')' for f in ranked[:3])+'.')
                else:answer['paragraphs'].append('Für '+MODES[mode]+' liegen für diese Auswahl keine nutzbaren Gütergruppenwerte vor.')
        # Totals stay visible; breakdowns use separate tables to avoid double counting.
        all_rows=answer['tables'][0]['rows'] if answer['tables'] else []
        by_fact={f['fact_id']:f for f in facts}
        answer['tables']=[]
        for mode in [None,*p['modes']]:
            selected=[row for row in all_rows if (by_fact[row['fact_ids'][0]]['group']=='ALL' if mode is None else
                by_fact[row['fact_ids'][0]]['mode']==mode and by_fact[row['fact_ids'][0]]['group']!='ALL')]
            if selected:answer['tables'].append({'title':'Gesamtwerte der Verbindung' if mode is None else 'Güterarten · '+MODES[mode],
                'columns':['Kennwert','Wert','Einheit','Hinweis'],'rows':selected,'collapsed':mode is not None,'row_count':len(selected)})
        answer['notes'].append('Gesamtwerte und Gütergruppen beschreiben dieselben Transporte und werden nicht addiert. Fehlende Angaben sind keine Nullwerte.')
        for check in result.get('related_data',{}).get('checks',{}).values():
            if not check.get('available'):continue
            alt=check['parameters']
            prompt=f'Zeige dieselbe Verbindung und Auswahl für {alt["year"]}.'
            answer['suggestions']=[prompt]
            answer['followups']=[{'question':prompt,'function_id':'relation_overview','parameters':alt}]
            answer['notes'].append(f'Für den gemeinsamen Datenjahrgang {alt["year"]} wurden verfügbare Werte dieser Verbindung geprüft. Er kann als alternative Auswertung gewählt werden.')
        if 'tkm' in p['metrics']:answer['notes'].append('Verkehrsleistung wird in Tonnenkilometern angegeben: transportierte Tonnen × Transportentfernung im jeweiligen Quellenumfang.')
    elif function=='road_relation_goods_limit':
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
    elif function=='relation_history':
        road=[f for f in facts if f.get('mode')=='road']
        missing_road=any(f.get('source_status')=='missing_row' for f in road)
        restricted_road=any(f.get('quality_status')=='restricted' for f in road)
        if missing_road:
            answer['paragraphs'].append('Die fehlende Angabe bedeutet nicht, dass auf dieser Verbindung keine Lkw unterwegs waren. Die KBA-Statistik beruht auf hochgerechneten Stichproben. Bei zu wenigen Fällen werden Verbindungen zu größeren Gebieten zusammengefasst. Warum diese Verbindung im betreffenden Jahr keinen eigenen Eintrag hat, lässt sich aus der Datei allein nicht feststellen.')
        elif any(f['value'] is None for f in facts):
            answer['notes'].append('Fehlende Angaben sind kein Nachweis, dass kein Verkehr stattfand. Die Tabelle unterscheidet fehlende Einträge von nicht verfügbaren Jahrgängen und unvollständigen Zahlenangaben.')
        if restricted_road:
            answer['notes'].append('Die gekennzeichneten KBA-Werte beruhen auf kleinen Stichproben. Laut KBA sind daraus berechnete Veränderungsraten kaum hinreichend genau.')
        elif any(f.get('quality_status')=='restricted' for f in facts):
            answer['notes'].append('Die gekennzeichneten Werte sind laut Quelle eingeschränkt belastbar.')
        if any('rechnerischen' in text for text in result.get('summary',[])):
            answer['notes'].append('Die Rate vergleicht veröffentlichte Werte; methodische Änderungen und Ursachen sind damit nicht geklärt.')
        if missing_road or restricted_road:
            answer['sources'].append('KBA: Referenzhandbuch VE 7, Stand Dezember 2025, Abschnitt 2.1–2.2, Seiten 6–7 (Stichprobe und statistische Genauigkeit).')
    elif function in {'relation','relation_matrix','rail_goods','rail_goods_history','time_series'}:
        answer['notes'].append('Wo kein Wert vorliegt, ist in der zugrunde liegenden Statistik kein nutzbarer Verkehrswert erfasst beziehungsweise veröffentlicht. Das beweist nicht, dass tatsächlich kein Verkehr stattfand.')
        if function in {'relation_history','rail_goods_history','time_series'}:
            answer['notes'].append('Eine ausgewiesene Veränderungsrate wird transparent aus vorhandenen veröffentlichten Werten berechnet. Sie ist nicht methodisch bereinigt und belegt keine Ursache.')
        if function=='rail_goods_history':
            answer['notes'].append('Die Darstellung verwendet '+('die sieben C7-Gütergruppen.' if p['classification']=='C7' else 'die 20 benannten NST-2007-Abteilungen.')+' Dreistellige Feinpositionen werden nicht ausgegeben.')
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
    if function == 'forecast_regions' and not p.get('goods'):
        answer['title'] = 'Prognose 2040: ' + ', '.join(name(region, datasets) for region in p['regions'])
        original_rows = {row['fact_ids'][0]: row for table in answer['tables'] for row in table['rows']}
        answer['tables'], answer['paragraphs'] = [], []
        for region in p['regions']:
            for mode in p['modes']:
                selected = [f for f in facts if f.get('region') == region and f.get('mode') == mode]
                rows = [original_rows[f['fact_id']] for f in selected]
                answer['tables'].append({'title': name(region, datasets) + ' · ' + MODES[mode],
                    'columns': ['Kennwert', 'Wert', 'Einheit', 'Hinweis'], 'rows': rows,
                    'collapsed': len(rows) > 4, 'row_count': len(rows)})
                parts = []
                for metric in p['metrics']:
                    group = [f for f in selected if f.get('metric') == metric]
                    base = next(f for f in group if f.get('scenario') == '2019_BASE')
                    target = next(f for f in group if f.get('scenario') == '2040_P1')
                    change = next(f for f in group if f['unit'] == '%')
                    label = 'Gütermenge' if metric == 'tonnes' else 'Verkehrsleistung'
                    if base['value'] is None or target['value'] is None:
                        parts.append(label + ': Für den Szenariovergleich fehlt ein nutzbarer Wert.')
                    else:
                        text = label + ': von ' + number(base['value']) + ' ' + UNITS[base['unit']] + ' auf ' + number(target['value']) + ' ' + UNITS[base['unit']]
                        if change['value'] is not None:
                            text += ' (Veränderung ' + number(change['value']) + ' %)'
                        else:
                            text += ' (keine prozentuale Veränderung bei Ausgangswert null)'
                        parts.append(text + '.')
                answer['paragraphs'].append(name(region, datasets) + ', ' + MODES[mode] + ': Prognosebasis 2019 → Prognose 2040. ' + ' '.join(parts))
        answer['notes'].extend(['Szenariovergleich, keine beobachtete Entwicklung. Regionen und Kennzahlen werden getrennt ausgewiesen und nicht addiert.',
            'Gesamtverkehr in der VP: Versand und Empfang ohne Binnenverkehr plus Binnenverkehr einmal. Einzelne Versand-/Empfangswerte enthalten keinen Binnenverkehr.'])
    if (function == 'forecast_regions' and p.get('goods')) or function == 'forecast_relation':
        answer['title']='Prognose nach Gütergruppen: '+(', '.join(name(r,datasets) for r in p['regions']) if function=='forecast_regions' else name(p['origin'],datasets)+' → '+name(p['destination'],datasets))
        original_rows={row['fact_ids'][0]:row for table in answer['tables'] for row in table['rows']}
        answer['tables'],answer['paragraphs']=[],[]
        selections={}
        for f in facts:
            selections.setdefault((f.get('region'),f.get('mode'),f.get('group')),[]).append(f)
        for (region_code,mode,goods),selected in selections.items():
            goods_name=selected[0].get('group_name',goods)
            place=name(region_code,datasets) if region_code else name(p['origin'],datasets)+' → '+name(p['destination'],datasets)
            title=place+' · '+MODES[mode]+' · '+goods_name
            rows=[original_rows[f['fact_id']] for f in selected]
            answer['tables'].append({'title':title,'columns':['Kennwert','Wert','Einheit','Hinweis'],'rows':rows,'collapsed':len(rows)>4,'row_count':len(rows)})
            parts=[]
            for metric in p['metrics']:
                group_facts=[f for f in selected if f.get('metric')==metric]
                base=next(f for f in group_facts if f.get('scenario')=='2019_BASE')
                target=next(f for f in group_facts if f.get('scenario')=='2040_P1')
                delta=next(f for f in group_facts if 'absolute Änderung' in f['label'])
                pct=next(f for f in group_facts if f['unit']=='%')
                if base['value'] is None or target['value'] is None:
                    parts.append('Für diesen Szenariovergleich fehlt ein eigener nutzbarer Relationswert; fehlende Werte sind nicht null.')
                    continue
                text=('Gütermenge' if metric=='tonnes' else 'Verkehrsleistung')+': von '+number(base['value'])+' '+UNITS[base['unit']]+' in der Prognosebasis 2019 auf '+number(target['value'])+' '+UNITS[target['unit']]+' im Jahr 2040'
                text+='; absolute Veränderung '+number(delta['value'])+' '+UNITS[delta['unit']]
                text+=' und relative Veränderung '+number(pct['value'])+' %.' if pct['value'] is not None else '. Bei Ausgangswert null ist keine prozentuale Veränderung berechenbar.'
                parts.append(text)
            answer['paragraphs'].append(title+': '+ ' '.join(parts))
        answer['notes'].extend(['Szenariovergleich, keine beobachtete Entwicklung oder sichere Vorhersage. Versand/Empfang ohne Binnenverkehr; Gesamtaufkommen zählt Binnen einmal.',
                               'C7 und VP25 sind verschiedene überlappende Gliederungen, keine zusätzlichen Mengen.'])
    if function=='dashboard_detail':
        titles={'regional_goods':'Regionale NST-Güterstruktur','sea_goods':'Hafengüterstruktur','sea_partners':'Hafenpartner nach Güterauswahl','kv_structure':'Ladeeinheiten- und Containergrößenstruktur','kv_relations':'Vorhandene KV-Relationen','regional_trips':'Straßenfahrten im Regionalprofil','forecast_kv':'Prognostizierter KV','forecast_load_units':'Prognose-Ladeeinheiten'}
        titles['forecast_container_types']='Prognose-Behältertypen'
        answer['title']=titles[p['product']]+' ('+str(p['year'])+')'
        if p['product'] in {'regional_goods','sea_goods','sea_partners'} and p['group']!='ALL':
            designation=('NST-20 Abteilung ' if p['classification']=='NST20' else 'C7 Gruppe ')+p['group']
            answer['paragraphs']=[designation+': '+text for text in answer['paragraphs']]
        answer['notes'].extend(n for n in result.get('notices',[]) if not n.startswith('Datenstand:'))
    if function=='forecast_ranking':
        selected_modes=('alle drei Landverkehrsträger zusammen' if set(p['modes'])=={'road','rail','iww'} else
                        ' und '.join(MODES[mode] for mode in p['modes']))
        answer['notes'].append('Die Rangliste bezieht sich auf '+selected_modes+'. Die ausgewählten Verkehrsträger werden je Region vor der Rangbildung addiert.')
    if function in {'forecast_relation','forecast_regions','forecast_comparison','forecast_ranking'} or p.get('include_forecast'):
        answer['notes'].append('Die Prognose vergleicht das Basisszenario 2019 mit dem Szenario für 2040. Das sind Modellannahmen, keine beobachtete Entwicklung und keine sichere Vorhersage. Beobachtete Werte bleiben davon getrennt.')
    if function=='goods_structure' and len(p['directions'])==1:
        from .results import compact_value
        totals=[f for f in facts if not f.get('group') and f['value'] is not None]
        ranked=sorted([f for f in facts if f.get('group') and f['unit']!='%' and f['value'] is not None],key=lambda f:f['value'],reverse=True)
        if totals and ranked:
            answer['paragraphs']=['; '.join(DIRECTIONS[f['direction']]+': '+compact_value(f['value'],f['unit']) for f in totals)+' erfasste Gütermenge ('+str(p['year'])+').',
                '\n'.join('- '+re.sub(r'^.*?/ C\d+\s*','',f['label'])+': '+compact_value(f['value'],f['unit']) for f in ranked[:3])]
    if function=='goods_history':
        answer['title']='Güterstruktur für '+region+f' ({p["start"]}–{p["end"]})'
        answer['paragraphs']=['Die wichtigsten Güter und ihre Entwicklung im gewählten Zeitraum:', '\n'.join('- '+s['text'] for s in result['statements'] if s.get('role')=='analysis')]
        if answer['tables']:
            answer['tables'][0].update(title='Gütergruppen und Jahresentwicklung im Detail',columns=['Jahr · Verkehrsträger · Gütergruppe','Wert','Einheit','Hinweis'])
        from .transport import SUM_NOTE
        answer['notes'].extend([SUM_NOTE,
            ('Dargestellt sind Veränderungen der veröffentlichten Profilwerte; Straßen-Quellenkennzeichen der Güterrandsummen sind nicht nacherschlossen. ' if p.get('partner_scope','all')=='all' else 'Dargestellt sind veröffentlichte Relationen im ausgewählten Gegenraum. ')+'Keine harmonisierte Gebietszeitreihe und kein Nachweis von Ursachen.',
            'Fehlende Gütergruppen bleiben unbekannt, auch wenn der Gesamtwert eines Verkehrsträgers null beträgt. Daraus folgt kein Nachweis von Nullverkehr.'])
    if function in {'goods_structure','goods_history'} and p.get('partner_scope','all')=='all':
        answer['notes'].append('Die Gütergruppen beschreiben die ausgewählte Region. Ihre Anteile lassen sich nicht als Güterverteilung einer einzelnen Verbindung lesen.')
    if status=='partial' and function not in {'road_relation_goods_limit','relation_history'}:
        answer['notes'].append('Ein Teil der gewünschten Angaben fehlt oder ist nur eingeschränkt nutzbar. Fehlende Werte werden in der Tabelle ausdrücklich angezeigt und nicht durch null ersetzt.')
    if any(f.get('quality_status')=='restricted' for f in facts) and function not in {'road_relation_goods_limit','relation_history'}:
        answer['notes'].append('Die Quelle kennzeichnet einzelne Werte als eingeschränkt belastbar. Bitte beachten Sie die Hinweise in der Tabelle.')
    if function=='transport_history':
        from .transport import SCOPES, SUM_NOTE
        answer['title']='Güterverkehr in '+region+f' ({p["start"]}–{p["end"]})'
        insights=[s['text'] for s in result['statements'] if s.get('role')=='analysis']
        answer['paragraphs']=[insights[0], '\n'.join('- '+s for s in insights[1:])] if len(insights)>1 else insights
        answer['notes']=[SCOPES[p['partner_scope']]+'. '+('Versand und Empfang.' if p['direction']=='all' else DIRECTIONS[p['direction']]+'.'),
                         next((n for n in result['notices'] if n.startswith('Versand plus Empfang') or n.startswith('Gerichtete veröffentlichte Relationen;')),''),
                         SUM_NOTE if p['metric']=='tonnes' else 'Verkehrsleistungen bleiben wegen unterschiedlicher Erfassungsräume nach Verkehrsträger getrennt.']
        if answer['tables']:
            all_rows=answer['tables'][0]['rows']; by_fact={f['fact_id']:f for f in facts}
            primary='total' if len(p['modes'])>1 and p['metric']=='tonnes' else p['modes'][0]
            main=[]; details=[]
            for row in all_rows:
                f=by_fact[row['fact_ids'][0]]
                if f.get('mode')==primary and f.get('year'):
                    missing=f.get('missing_modes',[])
                    main.append({**row,'label':str(f['year']),'note':'Fehlt: '+', '.join(MODES[m] for m in missing) if missing else row['note']})
                else:details.append(row)
            answer['tables']=[{'title':'Jahreswerte · '+MODES[primary],'columns':['Jahr','Wert','Einheit','Hinweis'],
                               'rows':main,'row_count':len(main),'collapsed':False,'compact_summary':True},
                              {'title':'Verkehrsträger und Veränderungen im Detail','columns':['Kennwert','Wert','Einheit','Hinweis'],
                               'rows':details,'row_count':len(details),'collapsed':True}]
    if function in {'node_connections','node_profile','node_statistics','node_partners'}:
        answer['notes'].extend(n for n in result.get('notices',[]) if not n.startswith('Datenstand:'))
    if p.get('partner_scope','all')!='all':
        from .transport import SCOPES
        answer['title']+=' · '+SCOPES[p['partner_scope']]
        answer['notes']=[n for n in answer['notes'] if not n.startswith('Die Gütergruppen beschreiben')]
        answer['notes'].insert(0,'Ausgewählter Gegenraum: '+SCOPES[p['partner_scope']]+'.')
    if function in {'relation_overview','relation_history','relation_matrix'} and any(f.get('aggregate') for f in facts):
        from .transport import SUM_NOTE
        answer['notes'].append(SUM_NOTE)
    answer['notes']=list(dict.fromkeys(n for n in answer['notes'] if n))
    return answer
