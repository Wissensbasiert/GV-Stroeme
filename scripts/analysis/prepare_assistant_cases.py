"""Erstellt getrennte Modelleingaben und interne Referenzen für alle 45 Fälle."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from server.analyseassistent.datasets import digest

ROOT = Path(__file__).resolve().parents[2]

# Only source-backed, unambiguous selections are executable at this stage.
# Missing contexts and incomplete compound functions remain explicit prerequisites.
EXECUTABLE = {
    'T20': ('road_relation_goods_limit', {'origin':'DEA23','destination':'DE600','year':2024,'metric':'tonnes'}),
    'T21': ('rail_goods_history', {'region':'DEA23','partner':'DE600','years':[2023,2024],'direction':'outbound','metric':'tonnes'}),
    'T16': ('goods_structure', {'region':'DEA12','year':2024,'mode':'road','metric':'tonnes','directions':['outbound','inbound'],'granularity':'C7'}),
    'T17': ('explain_scope', {'topic':'road_goods_depth'}),
    'T18': ('explain_scope', {'topic':'classification'}),
    'T31': ('intermodal_markets', {'region':'DE','year':2024,'modes':['rail','iww'],'metrics':['tonnes','tkm'],'direction':'all'}),
    'T32': ('intermodal_markets', {'region':'DEA12','year':2024,'modes':['rail'],'metrics':['tonnes'],'direction':'outbound'}),
    'T33': ('intermodal_markets', {'region':'DE','year':2024,'modes':['rail','iww'],'metrics':['tonnes'],'direction':'all'}),
    'T42': ('explain_scope', {'topic':'source_flags'}),
    'T43': ('explain_scope', {'topic':'regional_vs_national'}),
    'T45': ('explain_scope', {'topic':'outside_scope'}),
    'T34': ('node_profile', {'kind':'air','node':'EDDP','year':2025,'direction':'all','metrics':['tonnes','flights']}),
    'T37': ('toll_month', {'ags':'11000000','month':'2026-07','comparison_month':None}),
    'T38': ('toll_month', {'ags':'11000000','month':'2026-07','comparison_month':'2025-07'}),
    'T40': ('road_details', {'product':'VD2','year':2024,'region':'DE254','direction':'outbound','population':'I','metric':'trips','partner':None}),
    'T41': ('road_details', {'product':'VD3c','year':2024,'region':'DEA2','direction':'outbound','population':'I','metric':'tonnes','partner':None}),
    'T10': ('regional_history', {'region':'DEE03','start':2016,'end':2025,'mode':'rail','metric':'tonnes','direction':'all'}),
    'T23': ('modal_history', {'region':'DEA12','years':[2016,2025],'metric':'tonnes','direction':'all'}),
    'T04': ('partner_ranking', {'region':'DE600','year':2024,'mode':'road','metric':'tonnes','direction':'all','group':'ALL','top':5,'external':True}),
    'T05': ('relation_matrix', {'origin':'DEA12','destination':'DEE03','year':2024,'metric':'tonnes'}),
    'T44': ('rail_goods', {'region':'DEA23','partner':'DE600','year':2024,'direction':'outbound','group':'ALL','nst':None,'metric':'tonnes'}),
    'T01': ('region_profile', {'region': 'DEA12', 'year': 2024, 'metric': 'tonnes', 'include_forecast': True}),
    'T03': ('region_profile', {'region': 'DEA12', 'year': 2024, 'metric': 'tonnes', 'include_forecast': False}),
    'T24': ('regional_modal_split', {'region': 'DEA12', 'year': 2024, 'metric': 'tonnes', 'direction': 'all'}),
    'T29': ('forecast_comparison', {'region': 'DEA12', 'observed_years': [2019, 2024], 'metric': 'tonnes', 'direction': 'all'}),
    'T07': ('compare_regions', {'regions': ['DEA12', 'DEE03'], 'year': 2024, 'metric': 'tonnes', 'direction': 'all'}),
    'T19': ('rail_goods', {'region': 'DEA23', 'partner': 'DE600', 'year': 2024, 'direction': 'outbound', 'group': 'ALL', 'nst': None, 'metric': 'tonnes'}),
    'T22': ('national', {'year': 2024, 'metric': 'tkm', 'mode': None}),
    'T25': ('balance', {'region': 'DEA12', 'year': 2024, 'mode': 'road', 'metric': 'tonnes'}),
    'T27': ('national', {'year': 2024, 'mode': 'rail', 'metric': 'tkm'}),
    'T28': ('forecast_ranking', {'mode': 'rail', 'metric': 'tonnes', 'direction': 'all', 'measure': 'absolute', 'top': 5, 'descending': True}),
    'T35': ('node_partners', {'kind': 'air', 'node': 'EDDP', 'year': 2024, 'direction': 'outbound', 'metric': 'tonnes', 'international': True, 'top': 5}),
}

# These original cases provide no concrete geography/year selection. Their
# synthetic arithmetic controls remain separate unit evidence, never provider
# inputs or substitute geography. The API must request the missing selection.
CLARIFICATION_CASES = {
    'T02':['region','year','mode'], 'T06':['region','mode','direction'],
    'T08':['regions'], 'T09':['regions','year'], 'T11':['region','years','mode','direction'],
    'T12':['region','years','mode','group','direction'], 'T13':['regions','direction'],
    'T14':['region','mode','direction'], 'T15':['region','years'], 'T26':['region'],
    'T30':['region','metric'], 'T36':['node'], 'T39':['group','direction','years'],
}


def prepare():
    source = ROOT / 'docs/roadmap/ANALYSEASSISTENT_AUFBEREITUNGSPLAN.json'
    plan = json.loads(source.read_text(encoding='utf-8'))
    inputs, references = [], []
    for case in plan['cases']:
        question = case['question']
        # Keep the original ungraded question and input parameters only.
        guidance = case['parameters']
        if case['id'] == 'T35':
            guidance = guidance.replace('externe Flughafenpartner', 'internationale Flughafenpartner; Partnerland ungleich Deutschland')
        if case['id'] == 'T44':
            guidance = 'Köln DEA23 → Hamburg DE600, 2024, Schiene, Tonnen, Versand, Güterstruktur; aktueller gemeinsamer Datenstand.'
        if case['id'] in {'T37','T38'}:
            guidance = 'Lokaler Testumfang: Berlin, AGS 11000000 als Text; Juli 2026, Mautfahrten, Start/Ziel/Binnen getrennt.'
            if case['id']=='T38':
                guidance += ' Gewünschter Vergleich Juli 2025; keine Richtung oder einzelne Relation festgelegt.'
        if case['id'] in {'T40','T41'}:
            guidance += ' Für diesen Test ausdrücklich Inlandspopulation I: deutsche Güterkraftfahrzeuge, Lastfahrten mit erfassten Inlandskilometern; tkm nur im Inland.'
        if case['id']=='T33':
            guidance='Für diesen Test ausdrücklich Deutschland 2024, Schiene und Binnenschiff getrennt, Tonnen; statistische Teilmärkte und Frage nach Verlagerungspotenzial.'
        function, confirmed = EXECUTABLE.get(case['id'], (None, {}))
        inputs.append({'id': case['id'], 'question': question, 'parameter_guidance': guidance,
                       'confirmed': confirmed, 'structured_function': function,
                       'preparation_status': 'adapter_ready_for_review' if function else 'clarification_contract_prepared',
                       'blocking_note': None if function else 'Konkrete Auswahl fehlt im ursprünglichen Testfall; keine synthetischen Zahlen als reale Gebietsdaten senden.'})
        control = case['control']
        if case['id'] == 'T22':
            control = 'Bekannte Summe 624.919.760.431 tkm; sieben unbekannte VE7-Inlands_tkm-Zellen. Kein vollständiger Drei-Modi-Nenner und kein vollständiger Modal Split.'
        references.append({'id': case['id'], 'type': case['type'], 'control': control,
                           'source_ids': case['source_ids'], 'evaluation': 'pending_independent_review',
                           'model_test_kind':'concrete_query' if function else 'missing_context',
                           'missing_fields':CLARIFICATION_CASES.get(case['id'],[]),
                           'synthetic_control_is_not_real_data':not bool(function)})
    if len(inputs) != 45 or {r['id'] for r in inputs} != {f'T{i:02}' for i in range(1,46)}:
        raise ValueError('Testkatalog muss genau T01 bis T45 enthalten')
    if set(EXECUTABLE)|set(CLARIFICATION_CASES)!={f'T{i:02}' for i in range(1,46)} or set(EXECUTABLE)&set(CLARIFICATION_CASES):
        raise ValueError('Jeder Fall benötigt genau einen konkreten oder Rückfragevertrag')
    dest = ROOT / 'tests/analyseassistent'
    dest.mkdir(parents=True, exist_ok=True)
    for name, value in [('inputs.json', inputs), ('references.json', references),
                        ('catalog_manifest.json', {'source_sha256': digest(source), 'cases': 45,
                                                   'status': 'prepared_not_model_tested',
                                                   'note': 'Adapterbereitschaft ist keine Abnahme des vollständigen fachlichen Falls.'})]:
        (dest/name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'cases': len(inputs), 'adapter_ready_for_review': len(EXECUTABLE), 'full_model_run_ready': False}


if __name__ == '__main__':
    print(json.dumps(prepare()))
