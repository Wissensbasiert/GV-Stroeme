"""Neues Testpaket aus geprüftem aktivem Portalstand und aktuellem Fachpaket."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys


def digest(path):
    with path.open('rb') as handle: return hashlib.file_digest(handle, 'sha256').hexdigest()


def assemble(base, expected, package, portal, output):
    base, package, portal, output = [p.resolve() for p in [base, package, portal, output]]
    scratch = Path('C:/tmp').resolve()
    if output.exists() or output == scratch or not output.is_relative_to(scratch) or not output.name.startswith('portal-test-'):
        raise ValueError('Neuer Testrelease unter C:/tmp erforderlich')
    manifest = base/'MANIFEST.sha256.json'
    if digest(manifest) != expected: raise ValueError('Ausgangsmanifest stimmt nicht mit der Serverinventur überein')
    files = json.loads(manifest.read_text(encoding='utf-8'))
    for relative, entry in files.items():
        source = (base/relative).resolve()
        if not source.is_relative_to(base) or digest(source) != entry['sha256'] or source.stat().st_size != entry['bytes']:
            raise ValueError('Ausgangsrelease beschädigt: ' + relative)
    output.mkdir()
    # Copy only manifest-bound files; never prior deployment markers or secrets.
    for relative in files:
        target = output/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(base/relative, target)
    requirements = (output/'alwaysdata_portal/requirements.txt').read_bytes()
    sys.path.insert(0, str(portal/'scripts'))
    from gueterstroeme_release import integrate
    integrate(package, output)
    additions = (package/'private/config/analyseassistent/requirements.txt').read_text(encoding='utf-8').splitlines()
    if not all(line.strip().encode() in requirements for line in additions if line.strip() and not line.startswith('#')):
        raise ValueError('Neue Portalabhängigkeit benötigt gesonderte Prüfung')
    (output/'alwaysdata_portal/requirements.txt').write_bytes(requirements)
    allowed = ('alwaysdata_portal/static/gueterstroeme/', 'alwaysdata_portal/gueterstroeme_dashboard/', 'private/gueterstroeme/')
    for relative, entry in files.items():
        if not relative.startswith(allowed) and relative != 'GUETERSTROEME.json' and digest(output/relative) != entry['sha256']:
            raise ValueError('Unbeteiligte Portaldatei geändert: ' + relative)
    targets = {p.relative_to(output).as_posix(): {'bytes': p.stat().st_size, 'sha256': digest(p)}
               for p in sorted(output.rglob('*')) if p.is_file()}
    (output/'MANIFEST.sha256.json').write_text(json.dumps(targets, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return {'base': base.name, 'release': output.name, 'files': len(targets),
            'bytes': sum(x['bytes'] for x in targets.values()), 'manifest_sha256': digest(output/'MANIFEST.sha256.json'),
            'changed': [k for k in targets if targets[k] != files.get(k)], 'unrelated_portal_files_unchanged': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['base', 'package', 'portal', 'output', 'report']: parser.add_argument('--'+name, required=True, type=Path)
    parser.add_argument('--expected-base-sha', required=True)
    args = parser.parse_args()
    report = assemble(args.base, args.expected_base_sha, args.package, args.portal, args.output)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'changed'}, ensure_ascii=False))
