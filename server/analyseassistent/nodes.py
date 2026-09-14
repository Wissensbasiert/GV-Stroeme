"""Knotenabfragen auf unveränderten geprüften Flughafen- und Seehafenbeständen."""
import math
from pathlib import Path
from scripts.analysis import b0406

UNITS = {'tonnes': 't', 'flights': 'Flüge', 'teu': 'TEU'}
SCOPES = {'all': 'alle Gegenräume', 'domestic': 'Inland (Deutschland)',
          'international': 'Ausland (außerhalb Deutschlands)'}
RELATION_NOTE = ('Veröffentlichte Partnerverbindungen, keine vollständige Flughafen-Randsumme. '
                 'Fehlende Einträge können unter Veröffentlichungsschwellen liegen; die konkrete Ursache ist nicht belegt. '
                 'Fehlende Werte sind kein Nachweis von Nullverkehr.')
FLIGHT_NOTE = 'Flüge bezeichnet hier reine Fracht- und Postflüge (CAF_FRM), nicht Passagierflüge mit Beiladefracht.'
NODE_FUNCTIONS = {'node_profile', 'node_statistics', 'node_partners', 'node_connections'}


def airport_groups(names):
    # A named, inspectable catalogue group, not a parser for the user's wording.
    return {'london': {'name': 'London (Flughäfen im vorhandenen Katalog)',
                       'partners': sorted(code for code, name in names.items() if name.startswith('London ')),
                       'note': 'Die Gruppe umfasst die Londoner Flughäfen des vorhandenen Katalogs; keine Zusage vollständiger Stadtabdeckung.'}}


def check(kind, direction, metric, partner_scope):
    if (kind not in {'air', 'sea'} or direction not in {'all', 'outbound', 'inbound'}
            or partner_scope not in SCOPES
            or metric not in ({'tonnes', 'flights'} if kind == 'air' else {'tonnes', 'teu'})):
        raise ValueError('Kennzahl, Richtung oder Gegenraum passt nicht zum Knotentyp')


def partner_rows(con, dataset, *, kind, node, year, direction, metric, partner_scope='all', partners=None):
    check(kind, direction, metric, partner_scope)
    where = 'node=? AND year=? AND metric=?'
    args = [str(Path(dataset) / (kind + '_partners.parquet')), node, year, metric]
    # Air already has a separately published "all" row. Sea has only in/out.
    if kind == 'air' or direction != 'all':
        where += ' AND direction=?'
        args.append(direction)
    if partner_scope == 'domestic':
        where += " AND partner_country='DE'"
    elif partner_scope == 'international':
        where += (" AND regexp_full_match(partner_country, '[A-Z]{2}')"
                  " AND partner_country NOT IN ('DE','ZZ','XX','QU','QV','QW','QX','QY','QZ')")
    if partners is not None:
        if not partners or len(partners) > 10 or len(set(partners)) != len(partners):
            raise ValueError('Bitte eine eindeutige Auswahl von höchstens zehn Partnern verwenden')
        where += ' AND partner IN (' + ','.join('?' for _ in partners) + ')'
        args.extend(partners)
    applicable = 'sum(not_applicable_count)' if kind == 'sea' else '0'
    cursor = con.execute('SELECT partner AS id, partner_country, sum(known_sum) AS known_sum, '
                         'sum(missing_count) AS missing_count, sum(restricted_count) AS restricted_count, '
                         'sum(source_rows) AS source_rows, list(DISTINCT source_id) AS source_ids, '
                         + applicable + ' AS not_applicable_count FROM read_parquet(?) WHERE '
                         + where + ' GROUP BY partner, partner_country ORDER BY partner', args)
    records = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]
    if len({r['id'] for r in records}) != len(records):
        raise ValueError('Mehrdeutige Länderzuordnung eines Knotenpartners')
    for row in records:
        row['value'] = None if row['missing_count'] else row['known_sum']
        row['status'] = ('partial' if row['missing_count'] else 'available' if row['value'] is not None
                         else 'not_applicable' if row['not_applicable_count'] else 'missing_value')
    return records


def relation_metadata(kind, metric, partner_scope):
    return {'unit': UNITS[metric], 'scope': 'Gegenraum: ' + SCOPES[partner_scope] + '.',
            'note': ((RELATION_NOTE if kind == 'air' else
                      'Seehäfen: veröffentlichte Ein- und Ausladungen; TEU ausschließlich bei Containertransporten. '
                      'Nicht anwendbare TEU sind keine fehlenden Containerwerte. Unbekannte anwendbare Werte bleiben unbekannt.')
                     + (' ' + FLIGHT_NOTE if metric == 'flights' else '')),
            'counting': ('Luft: AVIA_GOR_DE, ausgewählte veröffentlichte Flughafenverbindungen; keine AVIA_GOOA-Randsumme.'
                         if kind == 'air' else 'See: Bei beiden Richtungen werden Ein- und Ausladung addiert.')}


def totals(records):
    known = [r['known_sum'] for r in records if r.get('known_sum') is not None]
    subtotal = math.fsum(known) if known else None
    missing = any(r['status'] not in {'available', 'not_applicable'} for r in records)
    return (None if missing else subtotal), subtotal, missing


def node_partners(con, dataset, *, kind, node, year, direction, metric, top, international=False, partner_scope=None):
    selected_scope = partner_scope if partner_scope is not None else ('international' if international else 'all')
    if international and selected_scope != 'international':
        raise ValueError('Widersprüchliche Gegenraumfilter')
    records = partner_rows(con, dataset, kind=kind, node=node, year=year,
                           direction=direction, metric=metric, partner_scope=selected_scope)
    positive = [r for r in records if r['value'] is not None and r['value'] > 0]
    denominator = math.fsum(r['value'] for r in positive) if positive else None
    unknown = sum(r['status'] not in {'available', 'not_applicable'} for r in records)
    if kind == 'sea' and unknown:
        denominator = None
    for row in positive:
        row['share_pct'] = row['value'] / denominator * 100 if denominator else None
    return {**relation_metadata(kind, metric, selected_scope), 'rows': b0406.rank(positive, top=top),
            'status': 'missing_row' if not records else 'partial' if unknown else 'not_applicable' if all(r['status']=='not_applicable' for r in records) else 'available',
            'denominator': denominator, 'positive_relations': len(positive), 'unknown_relations': unknown,
            'not_applicable_relations': sum(r['status'] == 'not_applicable' for r in records),
            'not_applicable_count': sum(r['not_applicable_count'] for r in records),
            'denominator_scope': 'Summe aller veröffentlichten positiven numerischen Partnerrelationen der Auswahl, vor Top-Begrenzung'}


def node_statistics(con, dataset, *, kind, node, year, direction, metric, partner_scope='all'):
    check(kind, direction, metric, partner_scope)
    if kind == 'air' and metric == 'flights' and b0406.airport_flights_blocked(dataset, year):
        # No fallback from a blocked GOOA statistic to a different GOR population.
        return {'status':'not_available','value':None,'unit':UNITS[metric],
                'scope':'Angefragter Gegenraum: '+SCOPES[partner_scope]+'.',
                'note':'Flughafen-Gesamtflugzahlen 2025 (AVIA_GOOA) bleiben wegen dokumentiertem Quellenwiderspruch gesperrt, auch mit Gegenraumfilter. '
                       'Verfügbare GOR-Einzelverbindungen sind ein anderes Datenprodukt und kein Ersatz für die Gesamtzahl. '+FLIGHT_NOTE}
    if partner_scope == 'all':
        raw = b0406.node_statistics(con, dataset, kind=kind, node=node, year=year, direction=direction, metric=metric)
        if metric == 'flights':
            raw['note'] = ' '.join([raw.get('note', ''), FLIGHT_NOTE]).strip()
        return raw
    records = partner_rows(con, dataset, kind=kind, node=node, year=year, direction=direction,
                           metric=metric, partner_scope=partner_scope)
    value, subtotal, missing = totals(records)
    return {**relation_metadata(kind, metric, partner_scope), 'value': value, 'known_sum': subtotal,
            'status': 'missing_row' if not records else 'partial' if missing else 'available' if value is not None else 'not_applicable',
            'restricted_count': sum(r['restricted_count'] for r in records),
            'source_ids': sorted({s for r in records for s in r['source_ids']})}


def node_profile(con, dataset, *, kind, node, year, direction, metrics, partner_scope='all'):
    observations, notes = [], []
    for metric in metrics:
        raw = node_statistics(con, dataset, kind=kind, node=node, year=year, direction=direction,
                              metric=metric, partner_scope=partner_scope)
        meta = {'unit': UNITS[metric], 'year': year, 'node': node, 'direction': direction, 'metric': metric,
                'source_status': raw['status'], 'source_ids': raw.get('source_ids', []),
                'restricted_count': raw.get('restricted_count', 0),
                'quality':'restricted' if raw.get('restricted_count',0) else 'unflagged'}
        if kind=='air' and metric=='flights' and year==2025 and raw['status']=='not_available':
            meta['source']='Eurostat AVIA_GOOA: gesperrte Flughafen-Gesamtflugzahlen 2025'
        label = node + ' / ' + str(year) + ' / ' + {'tonnes': 'Frachtgewicht', 'flights': 'Fracht- und Postflüge', 'teu': 'TEU'}[metric]
        if partner_scope != 'all':
            label += ' / ' + SCOPES[partner_scope] + ' / veröffentlichte Verbindungen'
        observations.append({'label': label, 'value': raw['value'], **meta})
        if raw['value'] is None and raw.get('known_sum') is not None:
            observations.append({'label': label + ' / Bekannte Teilsumme', 'value': raw['known_sum'],
                                 **meta, 'aggregate_role': 'subtotal'})
        notes.extend(raw[k] for k in ['note', 'counting'] if raw.get(k))
    return {'observations': observations,
            'status': 'available' if all(r['value'] is not None and r.get('aggregate_role') != 'subtotal' for r in observations) else 'partial',
            'scope': ('Veröffentlichte Randsumme des gewählten Knotens, Jahres und Richtungsbezugs.'
                      if partner_scope == 'all' else 'Summe veröffentlichter Verbindungen: ' + SCOPES[partner_scope] + '.'),
            'note': ' '.join(dict.fromkeys(notes)) + ' Unterschiedliche Einheiten bleiben getrennt. Kein stiller Wechsel des Bezugsjahrs.'}


def node_connections(con, dataset, *, kind, node, year, direction, metric, partners,
                     partner_scope='all', partner_group=None, airport_names=None):
    names = airport_names or {}
    if partner_group:
        group = airport_groups(names).get(partner_group)
        if kind != 'air' or not group or set(partners) != set(group['partners']):
            raise ValueError('Flughafengruppe stimmt nicht mit dem Katalog überein')
    records = partner_rows(con, dataset, kind=kind, node=node, year=year, direction=direction,
                           metric=metric, partner_scope=partner_scope, partners=partners)
    by_id = {r['id']: r for r in records}
    selected, observations = [], []
    for partner in partners:
        row = by_id.get(partner, {'id': partner, 'value': None, 'known_sum': None, 'status': 'missing_row',
                                 'missing_count': 0, 'restricted_count': 0, 'source_rows': 0, 'source_ids': []})
        selected.append(row)
        endpoints = (node, partner) if direction != 'inbound' else (partner, node)
        route = (' ↔ ' if direction == 'all' else ' → ').join(names.get(c, c) for c in endpoints)
        meta = {'unit': UNITS[metric], 'year': year, 'node': node, 'partner_id': partner,
                'direction': direction, 'metric': metric, 'source_status': row['status'],
                'source_ids': row['source_ids'], 'restricted_count': row['restricted_count'],
                'quality':'restricted' if row['restricted_count'] else 'unflagged',
                'partner_country': row.get('partner_country'), 'source_rows': row['source_rows']}
        observations.append({'label': str(year) + ' / ' + route, 'value': row['value'], **meta})
        if row['value'] is None and row['known_sum'] is not None:
            observations.append({'label': str(year) + ' / ' + route + ' / Bekannte Teilsumme',
                                 'value': row['known_sum'], **meta, 'aggregate_role': 'subtotal'})
    value, subtotal, missing = totals(selected)
    if len(partners) > 1:
        meta = {'unit': UNITS[metric], 'year': year, 'node': node, 'direction': direction, 'metric': metric,
                'source_status': 'partial' if missing else 'available',
                'components': list(partners), 'missing_partners': [r['id'] for r in selected if r['status'] not in {'available', 'not_applicable'}]}
        observations.append({'label': 'Summe der ausgewählten veröffentlichten Verbindungen', 'value': value,
                             **meta, 'aggregate_role': 'total'})
        if missing and subtotal is not None:
            observations.append({'label': 'Bekannte Teilsumme der ausgewählten Verbindungen', 'value': subtotal,
                                 **meta, 'aggregate_role': 'subtotal'})
    raw = {**relation_metadata(kind, metric, partner_scope), 'observations': observations,
           'status': 'partial' if missing else 'available' if value is not None else 'not_applicable'}
    if partner_group:
        raw['scope'] += ' ' + group['name'] + ': ' + ', '.join(names[p] for p in partners) + '. ' + group['note']
    elif len(partners)>1:
        raw['scope'] += ' Gemeinsam ausgewertete Knoten: '+', '.join(names.get(p,p) for p in partners)+'. Keine zusätzliche Zusage vollständiger Stadtabdeckung.'
    return raw
