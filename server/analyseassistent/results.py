"""Tabellen und Aussagen aus geprüften Werten, ohne frei erzeugte Fakten."""
import hashlib
import json
import math
import re
from .contracts import ANSWER, validate


def format_value(value):
    if value is None:
        return 'nicht verfügbar'
    if type(value) not in {int, float} or not math.isfinite(value):
        raise ValueError('Ungültiger Ergebniswert')
    return f'{value:,.2f}'.replace(',', '\x00').replace('.', ',').replace('\x00', '.')


MODE_LABELS={'road':'Straße','rail':'Schiene','iww':'Binnenschiff','total':'Summe der ausgewählten Verkehrsträger','subtotal':'Bekannte Teilsumme'}
DIRECTION_LABELS={'outbound':'Versand','inbound':'Empfang','all':'Versand und Empfang'}


def compact_value(value,unit):
    """Gerundete Lesefassung; die Tabelle behält den vollständigen Wert."""
    absolute=abs(value)
    if absolute>=1_000_000:
        shown=f'{value/1_000_000:.2f}'.replace('.',',')+' Mio.'
    elif absolute>=1_000:
        shown=f'{value:,.0f}'.replace(',','.')
    else:
        shown=format_value(value).removesuffix(',00')
    return shown+' '+{'t':'Tonnen','tkm':'Tonnenkilometer','%':'%'}.get(unit,unit)


def display_name(code,datasets):
    names=datasets.names.get(str(code),[])
    return min(names,key=len) if names else str(code)


def analytical_statements(function,parameters,rows,datasets):
    """Belegte Kernaussagen aus Ergebnisfakten; keine freie Zahlenerzeugung."""
    findings=[]
    def add(text,*facts):
        ids=list(dict.fromkeys(f['fact_id'] for f in facts if f))
        if text and ids:
            findings.append({'id':'a'+str(len(findings)+1),'text':text,'fact_ids':ids,'role':'analysis'})
    available=[row for row in rows if row.get('value') is not None]
    unit=next((row.get('unit') for row in available if row.get('unit')!='%'),None)
    if function=='transport_history':
        period=f'{parameters["start"]}–{parameters["end"]}'
        for mode in (['total'] if len(parameters['modes'])>1 and parameters['metric']=='tonnes' else [])+parameters['modes']:
            series=[r for r in rows if r.get('mode')==mode]
            first=next((r for r in series if r.get('year')==parameters['start']),None)
            last=next((r for r in series if r.get('year')==parameters['end']),None)
            delta=next((r for r in series if r.get('change')=='relative'),None)
            label=MODE_LABELS[mode]
            if first and last and first['value'] is not None and last['value'] is not None:
                text=f'{label} {period}: '+compact_value(first['value'],first['unit'])+' → '+compact_value(last['value'],last['unit'])
                if delta and delta['value'] is not None:text+=' ('+compact_value(delta['value'],'%')+').'
                else:text+='; eine prozentuale Veränderung ist bei Ausgangswert null nicht berechenbar.'
                add(text,first,last,delta)
            else:
                missing=sorted({r['year'] for r in series if r.get('year') and r['value'] is None})
                add(label+': Für '+', '.join(map(str,missing))+' fehlen vollständige Werte. Die Veränderung '+period+' ist nicht berechenbar.',first,last,delta)
        return findings
    if function in {'region_profile','balance'}:
        outbound=next((r for r in available if 'Versand' in r['label'] and 'Anteil' not in r['label']),None)
        inbound=next((r for r in available if 'Empfang' in r['label'] and 'Anteil' not in r['label']),None)
        balance=next((r for r in available if 'Saldo' in r['label']),None)
        if outbound and inbound:
            relation='höher' if outbound['value']>inbound['value'] else 'niedriger' if outbound['value']<inbound['value'] else 'gleich hoch'
            difference=abs(outbound['value']-inbound['value'])
            ending=('Der Versand liegt damit um '+compact_value(difference,outbound['unit'])+' '+relation+'.' if difference else 'Beide Richtungen sind gleich groß.')
            add('Die Statistik weist '+compact_value(outbound['value'],outbound['unit'])+' im Versand und '+compact_value(inbound['value'],inbound['unit'])+' im Empfang aus. '+ending,
                outbound,inbound,balance)
        if function=='region_profile':
            total=next((r for r in available if 'Regionalgesamt' in r['label']),None)
            shares=sorted([r for r in available if r.get('unit')=='%' and r.get('mode') in MODE_LABELS and r.get('basis')=='observed_profile'],key=lambda r:r['value'],reverse=True)
            if total and len(shares)==3:
                region=display_name(parameters.get('region'),datasets)
                parts=[MODE_LABELS[r['mode']]+' '+compact_value(r['value'],'%') for r in shares]
                add(f'{region} weist {parameters.get("year")} ein Güteraufkommen von '+compact_value(total['value'],total['unit'])+' aus. Den größten Anteil hat '+MODE_LABELS[shares[0]['mode']]+'; die Verteilung lautet '+', '.join(parts)+'.',total,*shares)
    if function in {'regional_modal_split','modal_history'}:
        years=sorted({r.get('year') for r in available if r.get('year') is not None},reverse=True)
        for year in years[:2]:
            shares=sorted([r for r in available if r.get('year')==year and r.get('unit')=='%' and r.get('mode') in MODE_LABELS],key=lambda r:r['value'],reverse=True)
            if shares:
                parts=[MODE_LABELS[r['mode']]+' '+compact_value(r['value'],'%') for r in shares]
                add(f'{year} hat {MODE_LABELS[shares[0]["mode"]]} den größten Anteil. Die Verteilung lautet: '+', '.join(parts)+'.',*shares)
    if function=='goods_structure':
        totals={r.get('direction'):r for r in available if r.get('direction') in {'outbound','inbound','all'} and 'group' not in r and r.get('unit')!='%'}
        if totals.get('outbound') and totals.get('inbound'):
            out,inc=totals['outbound'],totals['inbound']; difference=out['value']-inc['value']
            direction='mehr versandt als empfangen' if difference>0 else 'mehr empfangen als versandt' if difference<0 else 'gleich viel versandt und empfangen'
            add('Insgesamt wurden '+compact_value(out['value'],out['unit'])+' versandt und '+compact_value(inc['value'],inc['unit'])+' empfangen. Damit wurden '+compact_value(abs(difference),out['unit'])+' '+direction+'.',out,inc)
        leaders=[]
        for direction in ['outbound','inbound','all']:
            ranked=[r for r in available if r.get('direction')==direction and r.get('group') and r.get('unit')!='%' and r.get('rank')==1]
            if not ranked:continue
            leader=ranked[0]
            share=next((r for r in available if r.get('direction')==direction and r.get('group')==leader.get('group') and r.get('unit')=='%'),None)
            label=re.sub(r'^.*?/ C\d+\s*','',leader['label']).replace(' / Anteil','')
            leaders.append((direction,label,leader,share))
        if leaders:
            parts=[]; facts=[]
            for direction,label,leader,share in leaders:
                detail=compact_value(share['value'],'%') if share else compact_value(leader['value'],leader['unit'])
                parts.append(DIRECTION_LABELS[direction]+': '+label+' ('+detail+')')
                facts.extend([leader,share])
            add('Die jeweils größte Gütergruppe prägt das Ergebnis besonders: '+'; '.join(parts)+'.',*facts)
        for direction in parameters['directions']:
            total=totals.get(direction)
            ranked=sorted([r for r in available if r.get('direction')==direction and r.get('group') and r.get('unit')!='%'],key=lambda r:r['value'],reverse=True)
            if total and ranked:
                top=[r for r in ranked if r.get('rank',999)<=3]
                parts=[re.sub(r'^.*?/ C\d+\s*','',r['label'])+' mit '+compact_value(r['value'],r['unit']) for r in top]
                add(f'{parameters["year"]}: '+DIRECTION_LABELS[direction]+' auf '+MODE_LABELS[parameters['mode']]+': '+compact_value(total['value'],total['unit'])+'. Weitere Einordnung der führenden Gütergruppen: '+'; '.join(parts)+'.',total,*top)
    if function=='goods_history':
        for mode in parameters['modes']:
            for direction in parameters['directions']:
                latest=[r for r in rows if r.get('year')==parameters['end'] and r.get('mode')==mode and r.get('direction')==direction]
                quantities=[r for r in latest if r.get('group') and r['unit']!='%']
                ranked=sorted([r for r in quantities if r['value'] is not None],key=lambda r:r['value'],reverse=True)
                total=next((r for r in latest if not r.get('group') and r['unit']!='%'),None)
                text=f'{MODE_LABELS[mode]}, {DIRECTION_LABELS[direction]} {parameters["end"]}: '
                refs=[*latest]
                if ranked:
                    top=[r for r in ranked if r.get('rank',999)<=1]
                    parts=[]
                    for r in top:
                        label=re.sub(r'^.*?/ C\d+\s*','',r['label'])
                        share=next((s for s in latest if s.get('group')==r['group'] and s['unit']=='%'),None)
                        parts.append(label+' mit '+compact_value(r['value'],r['unit'])+(f' ({compact_value(share["value"],"%")})' if share and share['value'] is not None else ''))
                    text+=('Die größten Gütergruppen sind ' if all(r['value'] is not None for r in quantities) else 'Unter den bekannten Güterangaben führen ')+ '; '.join(parts)+'. '
                else:
                    text+='Es liegen keine aufgeschlüsselten Gütergruppenwerte vor; eine Rangfolge ist nicht möglich. '
                if total and total['value'] is not None:
                    text+='Der veröffentlichte Gesamtwert beträgt '+compact_value(total['value'],total['unit'])+'. '
                # Overall trend and the latest leader's trend, without inferring missing groups.
                for group in [None]:
                    endpoints=[next((r for r in rows if r.get('year')==year and r.get('mode')==mode and r.get('direction')==direction
                                     and r.get('group')==group and r['unit']!='%'),None) for year in [parameters['start'],parameters['end']]]
                    changes=[r for r in rows if r.get('change') and r.get('mode')==mode and r.get('direction')==direction and r.get('group')==group]
                    first,last=endpoints
                    relative=next((r for r in changes if r.get('change')=='relative'),None)
                    label='Gesamtwert' if group is None else 'Führende Gütergruppe'
                    if first and last and first['value'] is not None and last['value'] is not None:
                        text+=f'{label} {parameters["start"]} → {parameters["end"]}: '+compact_value(first['value'],first['unit'])+' → '+compact_value(last['value'],last['unit'])
                        if relative and relative['value'] is not None:
                            text+='; Veränderung der veröffentlichten Werte '+compact_value(relative['value'],'%')
                        else: text+='; keine prozentuale Veränderung bei Ausgangswert null'
                        text+='. '
                    else:
                        text+=f'{label}: Die Entwicklung {parameters["start"]}–{parameters["end"]} ist wegen fehlender Randjahreswerte nicht berechenbar. '
                    refs.extend([first,last,*changes])
                add(text.strip(),*refs)
    if function in {'relation_matrix','relation_history'}:
        origin=display_name(parameters.get('origin'),datasets); destination=display_name(parameters.get('destination'),datasets)
        if function=='relation_history':
            latest=parameters['end']
            year_rows=[r for r in rows if r.get('year')==latest]
            latest_rows=sorted([r for r in year_rows if r.get('value') is not None],key=lambda r:r['value'],reverse=True)
            missing_rows=[r for r in year_rows if r.get('value') is None]
            if len(parameters.get('modes',[]))>1 and latest_rows and not missing_rows:
                parts=[MODE_LABELS.get(r.get('mode'),str(r.get('mode')))+' '+compact_value(r['value'],r['unit']) for r in latest_rows]
                add(f'Im angefragten Endjahr {latest} weist {MODE_LABELS.get(latest_rows[0].get("mode"),latest_rows[0].get("mode"))} den größten veröffentlichten Wert von {origin} nach {destination} auf. Im Einzelnen: '+', '.join(parts)+'.',*latest_rows)
            elif len(parameters.get('modes',[]))>1 and latest_rows:
                parts=[MODE_LABELS.get(r.get('mode'),str(r.get('mode')))+' '+compact_value(r['value'],r['unit']) for r in latest_rows]
                missing=', '.join(MODE_LABELS.get(r.get('mode'),str(r.get('mode'))) for r in missing_rows)
                available_text=('die '+MODE_LABELS.get(latest_rows[0].get('mode'),str(latest_rows[0].get('mode')))
                                +' ein nutzbarer Wert von '+compact_value(latest_rows[0]['value'],latest_rows[0]['unit'])
                                if len(latest_rows)==1 else 'folgende Verkehrsträger nutzbar: '+', '.join(parts))
                missing_text=' und '.join(missing.rsplit(', ',1))
                add(f'Für {latest} ist von {origin} nach {destination} nur für {available_text} veröffentlicht. Für {missing_text} ist in der zugrunde liegenden Statistik kein nutzbarer Güterverkehrswert erfasst beziehungsweise veröffentlicht; deshalb ist kein vollständiger Verkehrsträgervergleich möglich.',*latest_rows,*missing_rows)
            for mode in parameters.get('modes',[]):
                endpoints=[next(r for r in rows if r.get('mode')==mode and r.get('year')==year)
                           for year in dict.fromkeys([parameters['start'],parameters['end']])]
                parts=[]
                for row in endpoints:
                    if row['value'] is not None:
                        parts.append('Für '+str(row['year'])+' weist die Statistik '+compact_value(row['value'],row['unit'])+' aus.')
                    else:
                        reason={'missing_row':'fehlt ein eigener Eintrag für diese Verbindung',
                                'not_available':'ist der Jahrgang für diese Auswahl nicht verfügbar',
                                'suppressed':'ist der Zahlenwert in der Quelle unterdrückt'}.get(row.get('source_status'),
                                'liegt keine vollständige Zahlenangabe vor')
                        parts.append('Für '+str(row['year'])+' '+reason+'.')
                route=f'von {origin} nach {destination} '+('auf der '+MODE_LABELS[mode] if mode!='iww' else 'mit dem Binnenschiff')
                parts[0]=parts[0].replace('Für ',f'Für den Güterverkehr {route} ',1)
                # Keep the year in a natural sentence after the route.
                parts[0]=parts[0].replace(route+' '+str(endpoints[0]['year']),route+' im Jahr '+str(endpoints[0]['year']),1)
                comparison=''
                if len(endpoints)==2 and all(r['value'] is not None for r in endpoints):
                    first,last=endpoints
                    if first['value']>0:
                        change=(last['value']-first['value'])/first['value']*100
                        development=('einem rechnerischen Wachstum von '+compact_value(change,'%') if change>0 else
                                     'einem rechnerischen Rückgang um '+compact_value(abs(change),'%') if change<0 else
                                     'einer unveränderten Menge (0 %)')
                        comparison='Auf Basis dieser veröffentlichten Werte entspricht das '+development+'.'
                    else:
                        comparison='Da der Ausgangswert null beträgt, wird keine prozentuale Veränderung berechnet.'
                    if any(r.get('quality_status')=='restricted' for r in endpoints):
                        comparison+=' Mindestens einer der beiden Werte ist eingeschränkt belastbar; die Rate beschreibt deshalb keine gesicherte Verkehrsentwicklung.'
                elif len(endpoints)==2:
                    comparison=f'Die Veränderung von {parameters["start"]} bis {parameters["end"]} lässt sich damit nicht beziffern.'
                add(' '.join(parts)+(' '+comparison if comparison else ''),*endpoints)
        else:
            for direction in [(parameters.get('origin'),parameters.get('destination')),(parameters.get('destination'),parameters.get('origin'))]:
                direction_rows=[r for r in rows if (r.get('origin'),r.get('destination'))==direction]
                if direction_rows:
                    parts=[MODE_LABELS.get(r.get('mode'),str(r.get('mode')))+': '+(compact_value(r['value'],r['unit']) if r['value'] is not None else 'kein eigener veröffentlichter Zahlenwert; keine Aussage über Nullverkehr') for r in direction_rows]
                    add('Von '+display_name(direction[0],datasets)+' nach '+display_name(direction[1],datasets)+' im Jahr '+str(parameters['year'])+': '+'; '.join(parts)+'.',*direction_rows)
    if function=='compare_regions':
        totals=[r for r in available if r.get('region') and not r.get('mode') and not r.get('group')]
        labels={'1':'Erzeugnisse der Land- und Forstwirtschaft, Rohstoffe','2':'Konsumgüter zum kurzfristigen Verbrauch, Holzwaren','3':'Mineralische, chemische und Mineralölerzeugnisse','4':'Metalle und Metallerzeugnisse','5':'Maschinen und Ausrüstungen, langlebige Konsumgüter','6':'Sekundärrohstoffe, Abfälle','7':'Sonstige Produkte'}
        for region in parameters['regions']:
            selected=[r for r in rows if r.get('region')==region]
            total=next((r for r in selected if not r.get('mode') and not r.get('group')),None)
            text=display_name(region,datasets)+' ('+str(parameters['year'])+', '+DIRECTION_LABELS[parameters['direction']]+'): '
            text+='Veröffentlichtes Güteraufkommen '+compact_value(total['value'],total['unit'])+'. ' if total and total['value'] is not None else 'Kein vollständiges Güteraufkommen verfügbar. '
            modes=[r for r in selected if r.get('mode') and r['unit']!='%']
            parts=[]
            for r in modes:
                share=next((s for s in selected if s.get('mode')==r['mode'] and s['unit']=='%'),None)
                parts.append(MODE_LABELS[r['mode']]+': '+(compact_value(r['value'],r['unit']) if r['value'] is not None else 'unbekannt')+((' ('+compact_value(share['value'],'%')+')') if share and share['value'] is not None else ''))
            text+='Modal Split: '+'; '.join(parts)+'. '
            groups=sorted([r for r in selected if r.get('group') and r['unit']!='%' and r['value'] is not None],key=lambda r:r['value'],reverse=True)[:3]
            text+='Größte Gütergruppen: '+'; '.join(labels[r['group']]+' mit '+compact_value(r['value'],r['unit']) for r in groups)+'.' if groups else 'Keine Rangfolge der Gütergruppen verfügbar.'
            add(text,*selected)
    if function in {'partner_ranking','node_partners'}:
        leader=next((r for r in available if r.get('rank')==1 and r.get('unit')!='%'),None)
        if leader:
            share=next((r for r in available if r.get('unit')=='%' and r.get('partner_id')==leader.get('partner_id')),None)
            label=display_name(leader.get('partner_id'),datasets) if leader.get('partner_id') else leader['label']
            ranked=[r for r in available if r.get('rank') and r.get('unit')!='%']
            add('Die wichtigsten veröffentlichten Partner der Auswahl sind: '+'; '.join((display_name(r['partner_id'],datasets) if r.get('partner_id') else r['label'])+' mit '+compact_value(r['value'],r['unit']) for r in ranked)+'.',*ranked)
    if function=='intermodal_markets':
        for share in [r for r in available if r.get('unit')=='%']:
            add(MODE_LABELS.get(share.get('mode'),str(share.get('mode')))+': Der ausgewiesene intermodale Teilmarkt umfasst '+compact_value(share['value'],'%')+' der veröffentlichten Menge dieses Verkehrsträgers.',share)
    if function=='regional_history':
        series=sorted([r for r in available if r.get('year') is not None],key=lambda r:r['year'])
        if len(series)>=2:
            highest=max(series,key=lambda r:r['value']);lowest=min(series,key=lambda r:r['value'])
            first,last=series[0],series[-1]
            if first['value']>0:
                change=(last['value']-first['value'])/first['value']*100
                development=('einem rechnerischen Wachstum von '+compact_value(change,'%') if change>0 else
                             'einem rechnerischen Rückgang um '+compact_value(abs(change),'%') if change<0 else
                             'einer unveränderten Menge (0 %)')
                comparison=' Auf Basis der veröffentlichten Anfangs- und Endwerte entspricht das '+development+'.'
            else:
                comparison=' Wegen des Ausgangswerts null wird keine prozentuale Veränderung berechnet.'
            add('Die veröffentlichten Jahreswerte reichen von '+compact_value(lowest['value'],lowest['unit'])+' ('+str(lowest['year'])+') bis '+compact_value(highest['value'],highest['unit'])+' ('+str(highest['year'])+'). Im ersten betrachteten Jahr '+str(first['year'])+' waren es '+compact_value(first['value'],first['unit'])+', im letzten Jahr '+str(last['year'])+' '+compact_value(last['value'],last['unit'])+'.'+comparison,lowest,highest,first,last)
    if function=='rail_goods':
        groups=[r for r in available if r.get('group') and r.get('unit')!='%' and r['label'].startswith('C')]
        total=next((r for r in available if 'Summe bekannter' in r['label']),None)
        if groups:
            leader=max(groups,key=lambda r:r['value'])
            text='Die größte verfügbare C1–C7-Gütergruppe ist '+leader['label'].split(' / ')[0]+' mit '+compact_value(leader['value'],leader['unit'])+'.'
            if total:text+=' Die Summe der verfügbaren veröffentlichten Feinpositionen beträgt '+compact_value(total['value'],total['unit'])+'.'
            add(text,leader,total)
    if function=='national':
        values=[r for r in available if r.get('unit')!='%' and r['label'] in MODE_LABELS]
        shares=sorted([r for r in available if r.get('unit')=='%' and r['label'].split(' / ')[0] in MODE_LABELS],key=lambda r:r['value'],reverse=True)
        if len(shares)==3:
            add('Die nationale Verteilung wird von '+MODE_LABELS[shares[0]['label'].split(' / ')[0]]+' angeführt. Die Anteile lauten '+', '.join(MODE_LABELS[r['label'].split(' / ')[0]]+' '+compact_value(r['value'],'%') for r in shares)+'.',*shares)
        elif values:
            add('Veröffentlicht sind '+', '.join(MODE_LABELS[r['label']]+' '+compact_value(r['value'],r['unit']) for r in values)+'. Ein vollständiger Modalanteil lässt sich nur mit einem kompatiblen Wert für alle drei Verkehrsträger berechnen.',*values)
    if function=='forecast_ranking':
        suffix='Absolute Änderung' if parameters['measure']=='absolute' else 'Relative Änderung'
        changes=[r for r in available if r['label'].endswith('/ '+suffix)]
        if changes:
            leading=min(r['rank'] for r in changes)
            leaders=[r for r in changes if r['rank']==leading]
            basis='absoluter Mengenänderung' if parameters['measure']=='absolute' else 'prozentualer Änderung'
            order='absteigend' if parameters['descending'] else 'aufsteigend'
            add('Szenario 2019–2040, nach '+basis+' '+order+' geordnet: Rang '+str(leading)+' belegt '
                +'; '.join(r['label'].rsplit(' / ',1)[0]+' mit '+compact_value(r['value'],r['unit']) for r in leaders)
                +'. Das ist eine Prognoseänderung, keine beobachtete Entwicklung.',*leaders)
    if function=='forecast_comparison':
        changes=[r for r in available if 'Relative Änderung' in r['label']]
        if changes:
            selected=max(changes,key=lambda r:abs(r['value']))
            add('Die auffälligste bereitgestellte relative Szenarioänderung betrifft '+selected['label'].replace(' / Relative Änderung','')+' mit '+compact_value(selected['value'],'%')+'. Sie vergleicht den Prognosebasisfall 2019 mit dem Szenario 2040 und ist keine beobachtete Entwicklung.',selected)
    if function=='node_connections':
        aggregates=[r for r in available if r.get('aggregate_role') in {'total','subtotal'} and r.get('components')]
        missing=[r for r in rows if r['value'] is None and r.get('partner_id')]
        selected=aggregates[-1:] or [r for r in available if r.get('partner_id')][:1]
        if selected:
            row=selected[0]
            text=(str(parameters['year'])+': '+row['label']+' beträgt '+compact_value(row['value'],row['unit'])+'.')
            if missing:text+=' Für weitere ausgewählte Verbindungen fehlen Werte; die vollständige Summe ist nicht bekannt.'
            add(text,row,*missing)
        if parameters.get('partner_group'):
            group=datasets.airport_groups[parameters['partner_group']]
            add('Zusammengefasst ist '+group['name']+': '+', '.join(datasets.airport_names[p] for p in parameters['partners'])+'. '+group['note'],*rows)
        detail=[r for r in available if r.get('partner_id') and not r.get('aggregate_role')]
        if len(detail)>1:
            add('\n'.join('- '+r['label']+': '+compact_value(r['value'],r['unit'])+'.' for r in detail[:3]),*detail[:3])
    if function=='node_profile':
        current=[r for r in available if r.get('year')==parameters.get('year') and r.get('unit')!='%'] or available
        if current:
            add('Für die gewählte Knotenauswertung sind '+', '.join(r['label']+' '+compact_value(r['value'],r['unit']) for r in current[:3])+ ' veröffentlicht. Kennzahlen mit anderer Einheit werden nicht miteinander addiert.',*current[:3])
    if function=='toll_month':
        unique=next((r for r in available if r['label']=='Eindeutig gezählte Fahrten'),None)
        outbound=next((r for r in available if r['label']=='Start'),None)
        inbound=next((r for r in available if r['label']=='Ziel'),None)
        if unique:
            text='Eindeutig gezählt sind '+compact_value(unique['value'],unique['unit'])+'.'
            if outbound and inbound:text+=' Davon erscheinen '+compact_value(outbound['value'],outbound['unit'])+' als Start und '+compact_value(inbound['value'],inbound['unit'])+' als Ziel; Binnenfahrten sind in beiden Richtungswerten enthalten.'
            add(text,unique,outbound,inbound)
    if function=='road_details' and available:
        leader=max(available,key=lambda r:r['value'])
        add('Der größte veröffentlichte Wert der gewählten Straßenstatistik ist '+leader['label']+' mit '+compact_value(leader['value'],leader['unit'])+'. Die übrigen Klassen bleiben in der Detailtabelle getrennt.',leader)
    return findings


def make_result(function, parameters, raw, datasets, rules_version):
    if function in {'relation_overview','relation_history','relation_matrix','goods_history'}:
        from .transport import add_modal_sums, SUM_NOTE
        raw={**raw,'observations':[dict(r) for r in raw.get('observations',[])]}
        for r in raw['observations']:
            r.setdefault('unit',raw.get('unit','t' if r.get('metric',parameters.get('metric'))=='tonnes' else 'tkm'))
        add_modal_sums(raw['observations'],parameters.get('modes',['road','rail','iww']),['year','origin','destination','direction','metric','group'])
        raw['counting']=' '.join([raw.get('counting',''),SUM_NOTE]).strip()
    source_labels = {
        'transport_history':'D01: Regionalprofile; bei Inland-/Auslandsfilter B01: gerichtete veröffentlichte Relationen',
        'relation_overview': 'B01: KBA VE7 / Destatis Schienen- und Binnenschiffsverkehr, gerichtete Jahresrelation und C1–C7',
        'road_relation_goods_limit': 'KBA VE7: veröffentlichte Straßen-OD-Gesamtwerte mit Quellenkennzeichen',
        'rail_goods_history': 'Destatis SGV: veröffentlichte Original-Feinpositionen je Jahr',
        'explain_scope': 'Gebundener B03-Klassifikationsstand und feste Fachregeln des Analyseassistenten',
        'goods_structure': 'D01: modebezogene Regionalprofile; gebundener C1–C7-Crosswalk',
        'goods_history': 'D01: modebezogene C1–C7-Regionalprofile je Jahr mit Quellenjahresprüfung',
        'intermodal_markets': 'Destatis: SGV/IWW-Rohquellen; getrennte Ladeeinheiten-/Containerteilmärkte',
        'node_profile': 'Eurostat AVIA_GOOA / Destatis Seeverkehr, je Knotentyp und Kennzahl',
        'node_connections': 'Eurostat AVIA_GOR_DE / Destatis Seeverkehr: veröffentlichte Partnerverbindungen',
        'regional_history': 'D01: Regionalprofile mit B02-Quellenjahresprüfung',
        'modal_history': 'D01: Regionalprofile mit B02-Quellenjahresprüfung',
        'relation_matrix': 'B01: KBA VE7 / Destatis Schienen- und Binnenschiffsverkehr, je Verkehrsträger',
        'relation_history': 'B01: KBA VE7 / Destatis Schienen- und Binnenschiffsverkehr, je Jahr und Verkehrsträger',
        'partner_ranking': 'B01: veröffentlichte OD-Quellzeilen mit Qualitätskennzeichen',
        'region_profile': 'D01: bestehende Dashboard-Regionalprofile' + ('; Verkehrsprognose 2040: 2019_BASE und 2040_P1' if parameters.get('include_forecast') else ''),
        'regional_modal_split': 'D01: bestehende Dashboard-Regionalprofile',
        'forecast_comparison': 'D01: bestehende Dashboard-Regionalprofile; Verkehrsprognose 2040: 2019_BASE und 2040_P1',
        'forecast_regions': 'Verkehrsprognose 2040: 2019_BASE und 2040_P1',
        'forecast_relation': 'Verkehrsprognose 2040: vollständige Originalmatrizen 2019 und 2040 P1',
        'dashboard_detail': 'Veröffentlichte Dashboarddetails: Destatis / KBA beziehungsweise Verkehrsprognose 2040',
        'toll_month': 'BALM/Toll Collect: vorhandene Berliner Monatsauszüge',
        'relation': 'KBA VE7 / Destatis Schienen- und Binnenschiffsverkehr, verkehrsträgerspezifisch',
        'compare_regions': 'D01: bestehende Dashboard-Regionalprofile',
        'union': 'B01: veröffentlichte Quelle-Ziel-Relationen',
        'time_series': 'Destatis: SGV/IWW, veröffentlichte Monatsrelationen',
        'rail_goods': 'Destatis: SGV, veröffentlichte Güter-Feinpositionen',
        'national': 'KBA VE7 und nationale Destatis-Verkehrsbeziehungen',
        'balance': 'D01: bestehende Dashboard-Regionalprofile',
        'forecast_ranking': 'Verkehrsprognose 2040: 2019_BASE und 2040_P1',
        'node_partners': 'Eurostat Luftfracht / Destatis Seeverkehr, entsprechend Knotentyp',
        'node_statistics': 'Eurostat AVIA_GOOA / Destatis Seeverkehr, entsprechend Knotentyp',
        'road_details': 'KBA: ' + str(parameters.get('product', 'VD2/VD3c')),
    }
    from .nodes import NODE_FUNCTIONS
    if function in NODE_FUNCTIONS:
        relation_source = function in {'node_partners','node_connections'} or parameters.get('partner_scope','all')!='all'
        source_labels[function] = ('Eurostat '+('AVIA_GOR_DE: veröffentlichte Flughafenverbindungen' if relation_source else 'AVIA_GOOA: veröffentlichte Flughafen-Randsumme')
                                   if parameters.get('kind')=='air' else 'Destatis Seeverkehr: veröffentlichte Hafenverbindungen')
        if function=='node_statistics' and parameters.get('kind')=='air' and parameters.get('metric')=='flights' and parameters.get('year')==2025 and raw.get('status')=='not_available':
            source_labels[function]='Eurostat AVIA_GOOA: gesperrte Flughafen-Gesamtflugzahlen 2025'
    if function not in NODE_FUNCTIONS and parameters.get('partner_scope','all')!='all':
        source_labels[function]='B01: gerichtete veröffentlichte Relationen; ausgewählter Inland-/Auslandsgegenraum'
    notices = [raw[key] for key in ['scope', 'counting', 'note', 'quality_note', 'territory_note',
                                   'population_note', 'vehicle_population', 'denominator_scope', 'sum_scope']
               if isinstance(raw.get(key), str)]
    notices.append('Datenstand: ' + datasets.snapshot_id + '. Veröffentlichtes Ergebnis im angegebenen Quellenumfang.')
    if 'text_facts' in raw:
        result_id=hashlib.sha256(json.dumps([function,parameters,datasets.snapshot_id,raw],sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:24]
        text_facts=[{**row,'fact_id':'t'+str(i+1),'source':row.get('source',source_labels[function])} for i,row in enumerate(raw['text_facts'])]
        statements=[{'id':'s'+str(i+1),'text':row['text'],'fact_ids':[row['fact_id']]} for i,row in enumerate(text_facts)]
        return {'result_id':result_id,'data_snapshot_id':datasets.snapshot_id,'rules_version':rules_version,
                'function_id':function,'parameters':parameters,'status':'ok' if raw['status']=='available' else raw['status'],
                'source_status':raw['status'],'facts':[],'text_facts':text_facts,
                'tables':[{'id':'table1','rows':text_facts,'kind':'text'}], 'statements':statements,
                'notices':notices,'sources':list(dict.fromkeys(row['source'] for row in text_facts)),'summary':[s['text'] for s in statements[:3]],
                'answer_mode':'fixed_verified'}
    rows = []
    unit = raw.get('unit', 't' if parameters.get('metric') == 'tonnes' else str(parameters.get('metric', '')))
    def add(label, value, state=None, row_unit=None, **metadata):
        status = state or raw.get('status', 'unknown')
        if value == 0:
            notices.append('Eine veröffentlichte numerische Null ist kein zusätzlicher Nachweis exakter Verkehrsfreiheit.')
        missing_status=metadata.get('source_status',status)
        value_status = metadata.pop('value_status', None) or ((missing_status if missing_status in {'missing_row','not_available','suppressed','not_applicable'} else 'missing_value') if value is None else 'reported_zero' if value == 0 else 'observed')
        rows.append({'fact_id': 'f' + str(len(rows)+1), 'label': str(label), 'value': value,
                     'display_value': format_value(value), 'unit': row_unit or unit, 'scale': 1,
                     'value_status': value_status,
                     'quality_status': metadata.pop('quality', raw.get('quality', 'unknown')),
                     'source_status': status, 'source': source_labels[function], 'parameters': parameters,
                     'data_snapshot_id': datasets.snapshot_id, **metadata})
    if function in {'node_connections','transport_history','dashboard_detail','forecast_relation','goods_history','forecast_regions','relation_overview','region_profile', 'regional_modal_split', 'forecast_comparison', 'relation_matrix','relation_history', 'partner_ranking','regional_history','modal_history','node_profile','goods_structure','intermodal_markets','road_relation_goods_limit','rail_goods_history'}:
        for observation in raw['observations']:
            metadata = {key: value for key, value in observation.items() if key not in {'label', 'value', 'unit'}}
            if function not in NODE_FUNCTIONS and parameters.get('partner_scope','all')!='all':
                metadata['source']='B01: gerichtete veröffentlichte Relationen; ausgewählter Inland-/Auslandsgegenraum'
            elif observation.get('basis'):
                metadata['source'] = ('Verkehrsprognose 2040: 2019_BASE und 2040_P1'
                                      if observation.get('basis') == 'VP2019_BASE_to_2040_P1'
                                      else 'D01: bestehende Dashboard-Regionalprofile')
            if function == 'partner_ranking':
                name = datasets.names.get(observation['id'], [observation['id']])[0]
                metadata['partner_name'] = name
                metadata['partner_id'] = observation['id']
            add(observation['label'], observation['value'], row_unit=observation.get('unit'), **metadata)
        if function == 'partner_ranking':
            add('Summe aller veröffentlichten Partner vor Top-Begrenzung', raw.get('denominator'))
            add('Davon veröffentlichte OD-Aggregate mit eingeschränktem Aussagewert', raw.get('restricted_denominator_value'), quality='restricted')
            notices.append(str(raw.get('unknown_partner_count', 0))+' Partner mit unbekanntem Wert sind nicht rangfähig; bei unbekannten Werten bleiben Anteile gesperrt.')
    elif function in {'relation', 'node_statistics'}:
        label = 'Summe veröffentlichter Verbindungen' if function=='node_statistics' and parameters.get('partner_scope','all')!='all' else 'Veröffentlichter Wert'
        add(label, raw.get('value'), value_status='missing_row' if raw.get('status') == 'missing_row' else None)
        if function=='node_statistics' and raw.get('value') is None and raw.get('known_sum') is not None:
            add('Bekannte Teilsumme veröffentlichter Verbindungen',raw['known_sum'],aggregate_role='subtotal')
    elif function == 'compare_regions':
        for row in raw['rows']:
            add(row['name'], row.get('value'), row.get('status'), region=row['id'])
            for mode, value in row.get('modes', {}).items():
                add(row['name'] + ' / ' + mode, value, row.get('status'), region=row['id'], mode=mode)
                denominator = row.get('value')
                modal_values = [row.get('modes', {}).get(m) for m in ['road','rail','iww']]
                complete = all(v is not None for v in modal_values) and denominator is not None and math.isclose(sum(modal_values),denominator,abs_tol=0.051)
                add(row['name']+' / '+mode+' / Anteil',value/denominator*100 if complete and denominator and value is not None else None,
                    row_unit='%',region=row['id'],mode=mode,denominator=denominator if complete else None,
                    denominator_scope='Gleiche Region, Jahr, Richtung und drei Landverkehrsträger')
            for group in '1234567':
                value=row.get('groups',{}).get(group)
                add(row['name']+' / C'+group,value,row.get('status'),region=row['id'],group=group)
                group_values=[row.get('groups',{}).get(g) for g in '1234567']
                denominator=row.get('value')
                complete=all(v is not None for v in group_values) and denominator is not None and math.isclose(sum(group_values),denominator,rel_tol=1e-12,abs_tol=0.051)
                add(row['name']+' / C'+group+' / Anteil',value/denominator*100 if complete and denominator and value is not None else None,
                    row_unit='%',region=row['id'],group=group,denominator=denominator if complete else None,
                    denominator_scope='Sieben Gütergruppen derselben Region, desselben Jahres und Richtungsbezugs')
        available = [r for r in raw['rows'] if r.get('value') is not None]
        if len(available)==2:
            a,b=available
            add(a['name']+' minus '+b['name'],a['value']-b['value'],formula='region_a_value - region_b_value')
    elif function == 'union':
        for key, part in raw['parts'].items():
            add(key, part.get('value'), part['status'])
        add('Eindeutig gezählte veröffentlichte Verkehre', raw.get('unique_value'))
    elif function == 'toll_month':
        for key, label in [('outbound', 'Start'), ('inbound', 'Ziel'), ('internal', 'Binnen'), ('unique', 'Eindeutig gezählte Fahrten')]:
            add(label, raw.get(key))
    elif function == 'balance':
        for key, label in [('outbound', 'Versand'), ('inbound', 'Empfang'), ('balance', 'Saldo: Versand minus Empfang')]:
            add(label, raw.get(key))
    elif function == 'national':
        for row in raw['modes']:
            if parameters['mode'] is None or row['mode'] == parameters['mode']:
                add(row['mode'], row['value'], row['status'])
                if parameters['mode'] is None:
                    add(row['mode'] + ' / Anteil', row['share_pct'], row['status'], '%',
                        denominator=raw['denominator'], denominator_scope='Drei Landverkehrsträger mit vollständigen kompatiblen Werten')
        if parameters['mode'] is not None:
            denominator=next(row['value'] for row in raw['modes'] if row['mode']==parameters['mode'])
            relationship_names=json.loads((datasets.paths['b0406']/'source_contracts.json').read_text(encoding='utf-8'))['relationships']
            for row in raw['relationships']:
                label=relationship_names.get(row['relationship'],row['relationship'])
                add(label,row['value'],relationship=row['relationship'],missing_count=row['missing_count'],
                    restricted_count=row['restricted_count'])
                add(label+' / Anteil',row.get('share_pct'),row_unit='%',
                    denominator=denominator,denominator_scope='Vollständiger nationaler Nenner desselben Verkehrsträgers',
                    relationship=row['relationship'])
    elif function == 'time_series':
        for year in raw.get('years', []):
            add(str(year['year'])+' / Jahreswert',year['annual_value'],year['status'],year=year['year'],
                missing_months=year['missing_months'],months_with_unknown_values=year['months_with_unknown_values'])
            for month in year['months']:
                add(f"{year['year']}-{month['month']:02}", month['value'], year['status'],
                    source_ids=month['source_ids'],missing_count=month['missing_count'],restricted_count=month['restricted_count'])
            add(str(year['year'])+' / Spitzenmonatsanteil',year['peak_month_share_pct'],year['status'],row_unit='%',
                denominator=year['annual_value'],peak_months=year['peak_months'],denominator_scope='Vollständige zwölf veröffentlichte Monate der Auswahl')
        notices.append('Änderungsraten bleiben ohne bestätigte Gebiets- und Revisionsvergleichbarkeit gesperrt.')
    elif function == 'rail_goods':
        for group in '1234567':
            selected=[r for r in raw.get('details',[]) if r['group_7_id']==group]
            value=sum(r['value'] for r in selected) if selected and all(r['value'] is not None for r in selected) else None
            add('C'+group+' / veröffentlichte Zeilensumme',value,group=group,
                value_status='missing_row' if not selected else None)
        for row in raw.get('details', []):
            add('NST ' + row['nst_raw'], row['value'], 'partial' if row['missing_count'] else 'available',
                group=row['group_7_id'],nst_raw=row['nst_raw'],missing_count=row['missing_count'],restricted_count=row['restricted_count'])
        add('Summe bekannter veröffentlichter Feinpositionen',raw.get('published_sum'),sum_scope='Keine Nullauffüllung fehlender Güterpositionen')
    elif function == 'road_details':
        for row in raw['rows']:
            add(row['label'], row['value'], row['value_status'], quality=row['quality_status'],
                original_symbol=row.get('raw_flag'), value_status=row['value_status'], class_id=row['class_id'])
    elif function in {'node_partners', 'forecast_ranking'}:
        for row in raw.get('rows', []):
            label = row.get('name') or datasets.names.get(row['id'], [row['id']])[0]
            if function == 'forecast_ranking':
                add(label + ' / 2019_BASE', row['base'],rank=row['rank'],region=row['id'])
                add(label + ' / 2040_P1', row['target'],rank=row['rank'],region=row['id'])
                add(label + ' / Absolute Änderung', row['absolute_change'],rank=row['rank'],region=row['id'])
                add(label + ' / Relative Änderung', row['relative_change_pct'],row_unit='%',rank=row['rank'],region=row['id'],
                    denominator=row['base'],denominator_scope='VP-Basisfall 2019_BASE derselben Auswahl',
                    formula='(VP2040_P1 - VP2019_BASE) / VP2019_BASE * 100')
            else:
                metadata = {'partner_id': row['id'], 'partner_country': row.get('partner_country')}
                if parameters.get('kind') == 'air' and row['id'] in datasets.airport_names:
                    label = datasets.airport_names[row['id']]
                    metadata['name_source'] = 'Vorhandenes Flughafenverzeichnis des Dashboards'
                add(label, row['value'], rank=row['rank'], **metadata)
                add(label + ' / Anteil', row.get('share_pct'), row_unit='%',
                    denominator=raw.get('denominator'), denominator_scope=raw.get('denominator_scope'), **metadata)
        if function=='forecast_ranking':
            notices.append('Ranking über '+str(raw['population_count'])+' passende Gebiete vor Top-Begrenzung; Ranggleichstände erhalten.')
    # Explicit result bounds, never quietly truncate an analysis.
    if len(rows) > 600:
        return limited('needs_clarification', 'Bitte Zeitraum oder Ergebnisumfang eingrenzen.')
    status = ('ok' if raw.get('status') in {'available', 'available_with_comparability_limits'}
              else 'partial' if rows and any(r['value'] is not None for r in rows) else 'not_available')
    if not rows:
        notices.append('Für diese Auswahl steht kein veröffentlichter Zahlenwert bereit.')
    result_id = hashlib.sha256(json.dumps([function, parameters, datasets.snapshot_id, raw],
                                         sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()[:24]
    summary_rows = [row for row in rows if row['value'] is not None] or rows
    insights=analytical_statements(function,parameters,rows,datasets)
    statements = [*insights,*[{'id': 's' + str(i+1), 'fact_ids': [row['fact_id']], 'role':'fact',
                   'text': row['label'] + ': ' + row['display_value'] + (' ' + row['unit'] if row['value'] is not None else '') + '.'}
                  for i, row in enumerate(summary_rows)]]
    return {'result_id': result_id, 'data_snapshot_id': datasets.snapshot_id,
            'rules_version': rules_version, 'function_id': function, 'parameters': parameters,
            'status': status, 'source_status': raw.get('status'), 'facts': rows,
            'tables': [{'id': 'table1', 'rows': rows}] if rows else [], 'statements': statements,
            'notices': list(dict.fromkeys(notices)), 'sources': [source_labels[function]],
            'summary': [s['text'] for s in (insights if function in {'goods_history','compare_regions'} else insights[:3]) or statements[:3]], 'answer_mode': 'fixed_verified'}


def limited(status, notice, *, missing_fields=None):
    return {'status': status, 'facts': [], 'tables': [], 'statements': [], 'summary': [],
            'notices': [notice], 'sources': [], 'answer_mode': 'fixed_verified',
            'missing_fields': missing_fields or []}


def apply_selection(result, selection):
    validate(ANSWER, selection)
    if selection['result_id'] != result['result_id'] or selection['data_snapshot_id'] != result['data_snapshot_id']:
        raise ValueError('Modellantwort gehört zu einem anderen Ergebnis')
    statements = {s['id']: s for s in result['statements']}
    tables = {t['id'] for t in result['tables']}
    paragraphs=[]
    used_ids=[]
    number_pattern=r'(?<!\w)[+-]?\d+(?:[.,]\d+)*(?!\w)'
    quantity_pattern=number_pattern+r'(?:\s+Mio\.)?\s*(?:Tonnenkilometer|Tonnen|tkm|t|Fahrten|Flüge|Ladeeinheiten|TEU|%)'
    sensitive_stems=('ursach','verursach','bedingt','zurückzuführ','beleg','beweis','bedeut','zeigt','spricht','potenzial',
                     'kapaz','auslast','anbindung','wettbewerb','standort','empfehl','sollt','muss','dürft','wahrschein',
                     'vermut','offensicht','effiz','attraktiv','erfolgreich','wirtschaft','ökolog','nachhalt','domin',
                     'übertriff','führ','größt','kleinst','höher','niedriger','mehr','weniger','gleich','kein','nicht',
                     'wachst','zunahm','anstieg','rückgang','abnahm','veränder','gestieg','gesunk','steig','sink','sank')
    for paragraph in selection['paragraphs']:
        ids=paragraph['statement_ids']
        if any(statement_id not in statements for statement_id in ids):
            raise ValueError('Modell hat nicht belegte Aussagen ausgewählt')
        text=paragraph['text'].strip()
        if re.search(r'<[^>]+>',text):
            raise ValueError('HTML ist in der Antwort nicht erlaubt')
        evidence=' '.join(statements[statement_id]['text'] for statement_id in ids)
        evidence_quantities=set(re.findall(quantity_pattern,evidence.casefold(),re.I))
        text_quantities=re.findall(quantity_pattern,text.casefold(),re.I)
        if any(quantity not in evidence_quantities for quantity in text_quantities):
            raise ValueError('Modell hat Zahl, Größenordnung oder Einheit verändert')
        stripped=re.sub(quantity_pattern,'',text,flags=re.I)
        bare_numbers=re.findall(number_pattern,stripped)
        evidence_numbers=set(re.findall(number_pattern,evidence))
        if any(number not in evidence_numbers or not re.fullmatch(r'(?:19|20)\d{2}',number) for number in bare_numbers):
            raise ValueError('Modell hat eine nicht belegte oder einheitenlose Zahl formuliert')
        text_words=re.findall(r'[A-Za-zÄÖÜäöüß]+',text.casefold())
        evidence_words=re.findall(r'[A-Za-zÄÖÜäöüß]+',evidence.casefold())
        for word in text_words:
            if any(word.startswith(stem) for stem in sensitive_stems) and word not in evidence_words:
                raise ValueError('Modell hat eine nicht belegte Einordnung formuliert')
        paragraphs.append(text)
        used_ids.extend(ids)
    if any(s.get('role')=='analysis' for s in statements.values()) and not any(statements[s].get('role')=='analysis' for s in used_ids):
        raise ValueError('Modellantwort enthält keine belegte Einordnung')
    if not set(selection['table_ids']) <= tables:
        raise ValueError('Modell hat eine nicht belegte Tabelle ausgewählt')
    # Required tables, sources and warnings always survive a model selection.
    return {**result, 'generated_summary': paragraphs,
            'answer_mode': 'model_synthesized_verified_numbers'}
