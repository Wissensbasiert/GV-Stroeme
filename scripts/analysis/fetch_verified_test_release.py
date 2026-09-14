"""Read the active test release into a new local directory, verifying every byte."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import sys


def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def fetch(portal, base, output, expected, report_path):
    sys.path.insert(0, str(portal.resolve()/'deployment/automation'))
    from deploy_alwaysdata_test import Api, resource_id, collection_items
    from release_maintenance import connect, read_bytes
    output = output.resolve()
    if output.exists() or output.parent != Path('C:/tmp').resolve() or not output.name.startswith('portal-test-'):
        raise ValueError('Neuer Releaseordner direkt unter C:/tmp erforderlich')
    api = Api(os.environ['ALWAYSDATA_API_TOKEN'])
    site = api.request('GET', '/site/1067000/')
    relative = 'portal_test/releases/'+output.name
    if site.get('path') != relative+'/alwaysdata_portal/wsgi.py' or {str(a).rstrip('/') for a in site.get('addresses', [])} != {'test.portal.wissensbasiert.de'}:
        raise ValueError('Aktive Testsite stimmt nicht mit dem Ziel überein')
    name, password = 'wbp-solutions_read_'+secrets.token_hex(5), secrets.token_urlsafe(32)
    ftp_id = ftp = None
    report = {'passed': False, 'release': output.name, 'copied': 0, 'downloaded': 0, 'downloaded_bytes': 0}
    try:
        created = api.request('POST', '/ftp/', {'name': name, 'password': password, 'path': relative})
        ftp_id = resource_id(created, api.request('GET', '/ftp/'), name)
        if ftp_id is None:
            raise ValueError('Temporärer Lesezugang nicht auflösbar')
        ftp = connect(name, password)
        content = read_bytes(ftp, 'MANIFEST.sha256.json')
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError('Servermanifest weicht von geprüfter Inventur ab')
        files = json.loads(content)
        output.mkdir()
        for relative_file, entry in files.items():
            target = (output/relative_file).resolve()
            if not target.is_relative_to(output):
                raise ValueError('Unzulässiger Manifestpfad')
            target.parent.mkdir(parents=True, exist_ok=True)
            source = (base/relative_file).resolve()
            if source.is_relative_to(base.resolve()) and source.is_file() and source.stat().st_size == entry['bytes'] and digest(source) == entry['sha256']:
                shutil.copyfile(source, target)
                report['copied'] += 1
            else:
                with target.open('wb') as handle:
                    ftp.retrbinary('RETR '+relative_file, handle.write)
                report['downloaded'] += 1
                report['downloaded_bytes'] += target.stat().st_size
            if target.stat().st_size != entry['bytes'] or digest(target) != entry['sha256']:
                raise ValueError('Zieldatei weicht vom Manifest ab: '+relative_file)
        (output/'MANIFEST.sha256.json').write_bytes(content)
        if api.request('GET', '/site/1067000/') != site:
            raise ValueError('Testsite während des Abrufs verändert')
        report.update(passed=True, manifest_sha256=expected, files=len(files))
    finally:
        if ftp is not None:
            ftp.close()
        if ftp_id is not None:
            api.request('DELETE', '/ftp/'+str(ftp_id)+'/')
            report['temporary_ftp_removed'] = all(item.get('id') != ftp_id for item in collection_items(api.request('GET', '/ftp/')))
            report['passed'] = report['passed'] and report['temporary_ftp_removed']
        report_path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    if not report['passed']:
        raise ValueError('Releaseabruf nicht vollständig bestätigt')
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['portal', 'base', 'output', 'report']:
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--expected-sha', required=True)
    args = parser.parse_args()
    fetch(args.portal, args.base, args.output, args.expected_sha, args.report)
