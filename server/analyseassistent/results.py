"""Tabellen und Aussagen aus geprüften Werten, ohne frei erzeugte Fakten."""
import hashlib
import json
import math
from .contracts import ANSWER, validate


def format_value(value):
    if value is None:
        return 'nicht verfügbar'
    if type(value) not in {int, float} or not math.isfinite(value):
        raise ValueError('Ungültiger Ergebniswert')
    return f'{value:,.2f}'.replace(',', '\x00').replace('.', ',').replace('\x00', '.')


def make_result(function, parameters, raw, datasets, rules_version):
    source_labels = {
        'road_relation_goods_limit': 'KBA VE7: veröffentlichte Straßen-OD-Gesamtwerte mit Quellenkennzeichen',
        'rail_goods_history': 'Destatis SGV: veröffentlichte Original-Feinpositionen je Jahr',
        'explain_scope': 'Gebundener B03-Klassifikationsstand und feste Fachregeln des Analyseassistenten',
        'goods_structure': 'D01: modebezogene Regionalprofile; gebundener C1–C7-Crosswalk',
        'intermodal_markets': 'Destatis: SGV/IWW-Rohquellen; getrennte Ladeeinheiten-/Containerteilmärkte',
        'node_profile': 'Eurostat AVIA_GOOA / Destatis Seeverkehr, je Knotentyp und Kennzahl',
        'regional_history': 'D01: Regionalprofile mit B02-Quellenjahresprüfung',
        'modal_history': 'D01: Regionalprofile mit B02-Quellenjahresprüfung',
        'relation_matrix': 'B01: KBA VE7 / Destatis Schienen- und Binnenschiffsverkehr, je Verkehrsträger',
        'partner_ranking': 'B01: veröffentlichte OD-Quellzeilen mit Qualitätskennzeichen',
        'region_profile': 'D01: bestehende Dashboard-Regionalprofile' + ('; Verkehrsprognose 2040: 2019_BASE und 2040_P1' if parameters.get('include_forecast') else ''),
        'regional_modal_split': 'D01: bestehende Dashboard-Regionalprofile',
        'forecast_comparison': 'D01: bestehende Dashboard-Regionalprofile; Verkehrsprognose 2040: 2019_BASE und 2040_P1',
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
                'notices':notices,'sources':list(dict.fromkeys(row['source'] for row in text_facts)),'summary':[s['text'] for s in statements[:4]],
                'answer_mode':'fixed_verified'}
    rows = []
    unit = raw.get('unit', 't' if parameters.get('metric') == 'tonnes' else str(parameters.get('metric', '')))
    def add(label, value, state=None, row_unit=None, **metadata):
        status = state or raw.get('status', 'unknown')
        if value == 0:
            notices.append('Eine veröffentlichte numerische Null ist kein zusätzlicher Nachweis exakter Verkehrsfreiheit.')
        value_status = metadata.pop('value_status', None) or ('missing_value' if value is None else 'reported_zero' if value == 0 else 'observed')
        rows.append({'fact_id': 'f' + str(len(rows)+1), 'label': str(label), 'value': value,
                     'display_value': format_value(value), 'unit': row_unit or unit, 'scale': 1,
                     'value_status': value_status,
                     'quality_status': metadata.pop('quality', raw.get('quality', 'unknown')),
                     'source_status': status, 'source': source_labels[function], 'parameters': parameters,
                     'data_snapshot_id': datasets.snapshot_id, **metadata})
    if function in {'region_profile', 'regional_modal_split', 'forecast_comparison', 'relation_matrix', 'partner_ranking','regional_history','modal_history','node_profile','goods_structure','intermodal_markets','road_relation_goods_limit','rail_goods_history'}:
        for observation in raw['observations']:
            metadata = {key: value for key, value in observation.items() if key not in {'label', 'value', 'unit'}}
            if observation.get('basis'):
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
        add('Veröffentlichter Wert', raw.get('value'))
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
    statements = [{'id': 's' + str(i+1), 'fact_ids': [row['fact_id']],
                   'text': row['label'] + ': ' + row['display_value'] + (' ' + row['unit'] if row['value'] is not None else '') + '.'}
                  for i, row in enumerate(summary_rows)]
    return {'result_id': result_id, 'data_snapshot_id': datasets.snapshot_id,
            'rules_version': rules_version, 'function_id': function, 'parameters': parameters,
            'status': status, 'source_status': raw.get('status'), 'facts': rows,
            'tables': [{'id': 'table1', 'rows': rows}] if rows else [], 'statements': statements,
            'notices': list(dict.fromkeys(notices)), 'sources': [source_labels[function]],
            'summary': [s['text'] for s in statements[:4]], 'answer_mode': 'fixed_verified'}


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
    if any(s not in statements for s in selection['statement_ids']) or not set(selection['table_ids']) <= tables:
        raise ValueError('Modell hat nicht belegte Aussagen ausgewählt')
    # Required tables, sources and warnings always survive a model selection.
    return {**result, 'summary': [statements[s]['text'] for s in selection['statement_ids']],
            'answer_mode': 'model_selected_verified'}
