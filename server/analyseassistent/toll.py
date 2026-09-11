"""Festes B07-Abbild; Fehlwerte und fehlende Monate bleiben unbekannt."""
from .datasets import read, digest, below


class Toll:
    def __init__(self, root):
        store = root / 'data/analysis/b07'
        pointer = read(store/'current.json')
        path = below(store/'releases', pointer['snapshot_id'])
        if digest(path/'manifest.json') != pointer['manifest_sha256'] or digest(path/'validation.json') != pointer['validation_sha256']:
            raise ValueError('B07-Prüfbindung ungültig')
        self.manifest = read(path/'manifest.json')
        if read(path/'validation.json')['passed'] is not True or digest(path/'records.json') != self.manifest['output_sha256']['records.json']:
            raise ValueError('B07-Daten nicht geprüft')
        self.records = read(path/'records.json')

    def query(self, *, ags, month, comparison_month=None):
        base = {'snapshot_id': self.manifest['snapshot_id'], 'unit': 'Mautfahrten', 'ags': ags, 'month': month,
                'status': 'not_available', 'outbound': None, 'inbound': None, 'internal': None, 'unique': None,
                'scope': self.manifest['scope'], 'source': self.manifest['source'],
                'counting': 'Eindeutig = Start + Ziel − Binnen; Binnen in beiden Richtungen enthalten.',
                'note': 'Fehlende Relationen sind kein Nullnachweis. Mautfahrten sind keine Tonnen.'}
        if ags != self.manifest['ags'] or month not in self.manifest['months']:
            return base
        data = [r for r in self.records if r['month'] == month]
        parts = [[r['value'] for r in data if r['direction'] == direction] for direction in [0, 1]]
        values = [sum(p) if p and all(v is not None for v in p) else None for p in parts]
        internal = next(r['value'] for r in data if r['direction'] == 0 and r['origin'] == r['destination'])
        result = {**base, 'status': 'available' if all(v is not None for v in values) and internal is not None else 'partial',
                  'outbound': values[0], 'inbound': values[1], 'internal': internal,
                  'unique': values[0]+values[1]-internal if all(v is not None for v in values) and internal is not None else None}
        if comparison_month is not None:
            expected = str(int(month[:4])-1) + month[4:]
            if comparison_month != expected:
                raise ValueError('Vorjahresvergleich benötigt denselben Monat des Vorjahres')
            result['comparison_month'] = comparison_month
            result['absolute_change'] = None
            result['relative_change_pct'] = None
            if comparison_month not in self.manifest['months']:
                result['status'] = 'partial'
                result['note'] += ' Das angefragte Vorjahresmonatspaar liegt lokal nicht vor; keine Änderungsrate verfügbar.'
            else:
                # A new comparison-capable snapshot needs a separate reference check.
                result['note'] += ' Vorjahresbestand vorhanden, Vergleichsfreigabe noch erforderlich.'
        return result
