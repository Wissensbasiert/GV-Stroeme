"""Erzeugt ein prüfbares Übergabepaket unter C:\\tmp; keine Serverumschaltung."""
import argparse
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from server.analyseassistent.datasets import Datasets, digest, below

ROOT = Path(__file__).resolve().parents[2]


def build(output):
    output = output.resolve()
    scratch = Path('C:/tmp').resolve()
    if output == scratch or not output.is_relative_to(scratch) or output.exists():
        raise ValueError('Neuer, noch nicht vorhandener Paketordner unter C:\\tmp erforderlich')
    datasets = Datasets(ROOT)
    # A fresh directory means a failed build cannot overwrite an older package.
    output.mkdir(parents=True)
    hashes = {}
    def copy(source, relative):
        target = below(output, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        source_sha, target_sha = digest(source), digest(target)
        if source_sha != target_sha:
            raise ValueError('Kopierte Datei stimmt nicht mit Quelle überein')
        hashes[relative] = target_sha
    for file in ['index.html', 'css/style.css', 'js/app.js']:
        copy(ROOT/file, 'public/'+file)
    # Explicit allowlist from actual fetch paths, including dynamic region/year paths.
    browser_data = ['web_summary_core.json', 'web_forecast_core.json', 'web_forecast_overview_tooltip.json',
                    'web_maritime.json', 'web_airfreight.json', 'web_intermodal.json', 'web_intermodal_terminals.geojson',
                    'nuts_centroids_vp2040.json', 'toll_municipalities.json', 'web_regions.json',
                    'nuts_centroids_full.json', 'web_choropleth.json', 'national_benchmarks.json', 'dim_nst2007.json',
                    'nuts1_de_boundaries.geojson', *[f'nuts3_de_{year}_display.geojson' for year in [2016,2021,2024]]]
    for file in browser_data:
        copy(ROOT/'data/processed'/file, 'public/data/processed/'+file)
    for directory in ['assets', 'data/processed/delivery', 'data/processed/relations', 'data/processed/toll_municipality_boundaries']:
        for source in sorted((ROOT/directory).rglob('*')):
            if source.is_file() and '__pycache__' not in source.parts:
                copy(source, 'public/'+source.relative_to(ROOT).as_posix())
    private_files = set()
    for directory in ['server/analyseassistent', 'config/analyseassistent', 'integration/analyseassistent']:
        private_files.update(p.relative_to(ROOT).as_posix() for p in (ROOT/directory).rglob('*') if p.is_file() and p.suffix in {'.py','.json','.md','.txt'})
    private_files.update('scripts/analysis/'+name for name in ['b01.py','b02.py','b03.py','b0406.py','run_assistant.py'])
    for package, manifest in datasets.manifests.items():
        if isinstance(manifest.get('code_sha256'),dict):
            private_files.update(manifest['code_sha256'])
        path = datasets.paths[package]
        for filename in [*manifest['output_sha256'], 'manifest.json', 'validation.json']:
            private_files.add((path/filename).relative_to(ROOT).as_posix())
        if package == 'b0406':
            private_files.add((path/'partner_mapping_validation.json').relative_to(ROOT).as_posix())
        private_files.add('data/analysis/'+package+'/current.json')
    for file in sorted(private_files):
        copy(below(ROOT,file), 'private/'+file)
    summary={'format_version':'0.3.0', 'data_snapshot_id':datasets.snapshot_id,
             'status':'local_handoff_not_deployed', 'portal_adapter_status':'local_integration_requires_release_validation',
             'files_sha256':hashes, 'file_count':len(hashes),
             'bytes':sum(below(output,p).stat().st_size for p in hashes),
             'note':'Private Daten und Programme niemals unter dem öffentlichen Webpfad bereitstellen. Portaladapter und PostgreSQL-Verbrauch lokal geprüft; vollständiger Release und Liveabnahme bleiben gesondert erforderlich.'}
    (output/'release.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {k:v for k,v in summary.items() if k!='files_sha256'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    print(json.dumps(build(parser.parse_args().output),ensure_ascii=False,indent=2))
