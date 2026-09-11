"""Prüft ausschließlich die vorhandenen Berliner Mautauszüge, ohne Netzabruf."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from server.analyseassistent.datasets import digest, read, below

ROOT = Path(__file__).resolve().parents[2]


def prepare():
    source = ROOT / 'data/raw/Straße/Lkw-Portal/Berlin'
    index = read(source / 'README.json')
    checks, records, hashes = [], [], {'README.json': digest(source/'README.json')}
    seen_files, seen_records = set(), set()
    for entry in index['files']:
        filename, month, role = entry['file'], entry['month'][:7], entry['role']
        if (month, role) in seen_files or role not in {'Quelle', 'Ziel'}:
            raise ValueError('Doppelte oder unbekannte Monats-/Richtungsauswahl')
        seen_files.add((month, role))
        path = below(source, filename)
        hashes[filename] = digest(path)
        content = read(path)
        if len(content['features']) != entry['relation_count']:
            raise ValueError('Relationszahl stimmt nicht mit lokalem Abrufverzeichnis überein')
        direction = 0 if role == 'Quelle' else 1
        for feature in content['features']:
            p = feature['properties']
            actual_month = datetime.fromtimestamp(p['monat']/1000, timezone.utc).strftime('%Y-%m')
            if actual_month != month or p['richtung'] != direction:
                raise ValueError('Quellmonat oder Richtung widerspricht Dateiverzeichnis')
            if p['ags_start' if direction == 0 else 'ags_ziel'] != '11000000':
                raise ValueError('Auszug enthält andere Fokusgemeinde')
            for field in ['ags_start', 'ags_ziel']:
                if not isinstance(p[field], str) or not re.fullmatch(r'\d{8}', p[field]):
                    raise ValueError('AGS ist nicht als achtstelliger Text erhalten')
            key = (month, direction, p['ags_start'], p['ags_ziel'])
            if key in seen_records:
                raise ValueError('Mehrdeutige gerichtete Gemeinderelation')
            seen_records.add(key)
            value = p['anzahl_befahrungen']
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError('Ungültige Fahrtenzahl')
            records.append({'month': month, 'direction': direction, 'origin': p['ags_start'],
                            'destination': p['ags_ziel'], 'value': value, 'source_file': filename,
                            'source_record_id': p['objectid']})
        checks.append({'name': filename, 'passed': True, 'rows': len(content['features'])})
    months = sorted({r['month'] for r in records})
    annual_pairs = [(f'{int(m[:4])-1}{m[4:]}', m) for m in months if f'{int(m[:4])-1}{m[4:]}' in months]
    internal_checks = []
    for month in months:
        internal = [r for r in records if r['month'] == month and r['origin'] == r['destination']]
        if len(internal) != 2 or {r['direction'] for r in internal} != {0, 1} or internal[0]['value'] != internal[1]['value']:
            raise ValueError('Binnenabgleich zwischen Start- und Zielauszug ist nicht eindeutig')
        internal_checks.append({'month': month, 'passed': True, 'value': internal[0]['value']})
    manifest = {'scope': 'Vorhandene veröffentlichte Berliner Gemeindeauszüge; kein erneuter Liveabruf und kein bundesweiter Bestand',
                'source': index['source'], 'ags': '11000000', 'months': months, 'prior_year_pairs': annual_pairs,
                'source_sha256': hashes, 'code_sha256': digest(Path(__file__)),
                'status': 'T37_real_available_T38_prior_year_missing' if not annual_pairs else 'prior_year_pair_available'}
    snapshot = hashlib.sha256(json.dumps(manifest, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]
    manifest['snapshot_id'] = snapshot
    dest = ROOT / 'data/analysis/b07/releases' / snapshot
    dest.mkdir(parents=True, exist_ok=True)
    def save(name, value):
        text = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        path = dest / name
        if path.exists() and path.read_text(encoding='utf-8') != text:
            raise ValueError('Vorhandener Datenstand darf nicht überschrieben werden')
        path.write_text(text, encoding='utf-8')
    save('records.json', records)
    manifest['output_sha256'] = {'records.json': digest(dest/'records.json')}
    save('manifest.json', manifest)
    save('validation.json', {'passed': True, 'snapshot_id': snapshot, 'checks': checks,
                            'internal_checks': internal_checks, 'records': len(records),
                            'prior_year_comparison_passed': bool(annual_pairs),
                            'limit': 'Keine erneute externe Vollständigkeitsprüfung. T38 ohne vorhandenes Vorjahresmonatspaar nicht numerisch abgenommen.'})
    pointer = {'snapshot_id': snapshot, 'manifest_sha256': digest(dest/'manifest.json'),
               'validation_sha256': digest(dest/'validation.json')}
    target = ROOT / 'data/analysis/b07/current.json'
    pending = target.with_suffix('.pending.json')
    pending.write_text(json.dumps(pointer, indent=2) + '\n', encoding='utf-8')
    pending.replace(target)
    return {**pointer, 'records': len(records), 'months': months, 'prior_year_pairs': annual_pairs}


if __name__ == '__main__':
    print(json.dumps(prepare(), ensure_ascii=False, indent=2))
