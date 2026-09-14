"""Kompakter Katalog aus gebundenen Metadaten, ohne Rohdaten im Modellkontext."""
import json
from .dialogue import available_years


def catalog(datasets, function=None, parameters=None):
    coverage = json.loads((datasets.paths['b0406'] / 'source_coverage.json').read_text(encoding='utf-8'))
    classification = json.loads((datasets.paths['b03'] / 'classification.json').read_text(encoding='utf-8'))
    road = datasets.manifests['b03'].get('sources', [])
    result = {
        'data_snapshot_id': datasets.snapshot_id,
        'regional_goods_history': {'tool':'goods_history','max_years':10,'modes':['road','rail','iww'],
                                  'since_time_kind':'since_available','separate_modes':True},
        'forecast': {'tool': 'forecast_regions', 'base': '2019_BASE', 'target': '2040_P1',
                     'max_regions': 5, 'metrics': ['tonnes', 'tkm'], 'modes': ['road', 'rail', 'iww'],
                     'observed_years_required': False},
        'relation_years_by_mode': datasets.manifests['b01']['years_by_mode'],
        'regional_years_by_mode': {mode: sorted({r['year'] for r in coverage if r['mode'] == mode}) for mode in ['road', 'rail', 'iww']},
        'goods_groups': classification['groups'],
        'road_detail_products': [{'product': p, 'years': sorted({y for r in road if r.get('product') == p for y in r.get('years', [])}),
                                 'region_levels': sorted({r['region_level'] for r in road if r.get('product') == p})} for p in ['VD2', 'VD3c']],
        'toll': {k: datasets.manifests.get('b07', {}).get(k) for k in ['ags', 'months', 'prior_year_pairs']},
        'limits': [
            'Jahrgangsabdeckung ist kein Nachweis eines Werts für jede Verbindung.',
            'Regionale Profile: Kreise und kreisfreie Städte; nationale Statistiken getrennt. Häfen und Flughäfen sind eigene Knoten.',
            'Straßenverbindungen: veröffentlichte Gesamtmenge, keine Güteraufteilung der einzelnen Verbindung. VD3c hat eine andere Raumebene.',
            'Schiene: veröffentlichte Original-Feinpositionen und zugeordnete C1–C7-Gruppen; keine Nullauffüllung.',
            'Prognose: 2019_BASE und 2040_P1, getrennt von beobachteten Jahren.',
            'Keine belegten Ursachen, freien Kapazitäten, Kosten oder Emissionswerte.',
        ],
    }
    if function:
        result['selection'] = {'function_id': function, 'available_years': available_years(datasets, function, parameters or {}),
                               'scope': 'Datenprodukt und gegebenenfalls Region; konkrete Werte separat abfragen'}
    if 'dashboard_access' in datasets.paths:
        path=datasets.paths['dashboard_access']
        result['dashboard_access']=json.loads((path/'coverage.json').read_text(encoding='utf-8'))
        result['forecast']['goods']={'C7':classification['groups'],'VP25':json.loads((path/'forecast_core.json').read_text(encoding='utf-8'))['metadata']['vp2040_groups'],
                                      'parameter':'goods, z.B. [4] oder [VP100]; ALL ist Gesamtverkehr, nicht Güterstruktur'}
        sea=json.loads((path/'sea.json').read_text(encoding='utf-8'))
        result['sea_port_names']={code:p['name'] for ports in sea['seaports'].values() for code,p in ports.items()}
        result['sea_country_names']={r['iso']:r['name'] for ports in sea['seaports'].values() for p in ports.values() for r in p.get('partner_countries',[])}
        result['NST20']=json.loads((path/'taxonomy.json').read_text(encoding='utf-8'))['divisions_20']
        result['forecast_cell_names']=datasets.forecast_cell_names
        result['sea_country_names']={r['iso']:r['name'] for ports in sea['seaports'].values() for p in ports.values() for r in p.get('partner_countries',[])}
        result['NST20']=json.loads((path/'taxonomy.json').read_text(encoding='utf-8'))['divisions_20']
        result['forecast_cell_names']=datasets.forecast_cell_names
        regional=json.loads((path/'regional.json').read_text(encoding='utf-8'))
        regional_years=sorted({int(y) for years in regional.values() for y in years})
        result['dashboard_detail_years']={'regional_goods':regional_years,'regional_trips':regional_years,
                                         'sea_goods':sorted(int(y) for y in sea['seaports']),'sea_partners':sorted(int(y) for y in sea['seaports']),
                                         'forecast_kv':[2019,2040],'forecast_load_units':[2019,2040],
                                         'forecast_container_types':[2019,2040],
                                         'kv_structure':json.loads((path/'intermodal.json').read_text(encoding='utf-8'))['years'],
                                         'kv_relations':json.loads((path/'intermodal.json').read_text(encoding='utf-8'))['years']}
    return result
