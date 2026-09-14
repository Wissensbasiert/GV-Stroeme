"""Kompakter Katalog aus gebundenen Metadaten, ohne Rohdaten im Modellkontext."""
import json
from .dialogue import available_years


def catalog(datasets, function=None, parameters=None):
    coverage = json.loads((datasets.paths['b0406'] / 'source_coverage.json').read_text(encoding='utf-8'))
    classification = json.loads((datasets.paths['b03'] / 'classification.json').read_text(encoding='utf-8'))
    road = datasets.manifests['b03'].get('sources', [])
    result = {
        'data_snapshot_id': datasets.snapshot_id,
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
    return result
