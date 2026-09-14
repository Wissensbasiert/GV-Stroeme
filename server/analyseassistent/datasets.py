"""Geprüfte, unveränderlich adressierte Datenstände und begrenzte Abfragen."""
import hashlib
import json
import threading
import re
from pathlib import Path
import duckdb
from scripts.analysis import b01, b02, b03, b0406
from .contracts import FUNCTIONS, validate
from . import profiles
from . import relations
from . import nodes
from . import support
from . import scope
from . import access


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def below(root, name):
    root = Path(root).resolve()
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Unzulässiger interner Dateiverweis')
    return path


class Datasets:
    def __init__(self, root, *, include_support=True):
        self.root = Path(root).resolve()
        self.paths, self.manifests, self.pointers = {}, {}, {}
        packages=['b01','b02','b03','b0406']
        if include_support and (self.root/'data/analysis/assistant_support/current.json').exists():
            packages.append('assistant_support')
        if (self.root/'data/analysis/dashboard_access/current.json').exists():
            packages.append('dashboard_access')
        for package in packages:
            store = self.root / 'data/analysis' / package
            pointer = read(store / 'current.json')
            path = below(store / 'releases', pointer['snapshot_id'])
            if path.parent != (store / 'releases').resolve():
                raise ValueError('Ungültiger Datenstand')
            manifest = read(path / 'manifest.json')
            for file, key in [('manifest.json', 'manifest_sha256'), ('validation.json', 'validation_sha256')]:
                if digest(path / file) != pointer[key]:
                    raise ValueError('Prüfbindung des Datenstands ungültig')
            report = read(path / 'validation.json')
            if (report.get('passed') is not True or report['snapshot_id'] != pointer['snapshot_id']
                    or manifest['snapshot_id'] != pointer['snapshot_id']):
                raise ValueError('Datenstand ist nicht geprüft')
            if package == 'b0406':
                partner = read(path / 'partner_mapping_validation.json')
                if digest(path / 'partner_mapping_validation.json') != pointer['partner_mapping_validation_sha256'] or partner.get('passed') is not True:
                    raise ValueError('Partnerprüfung fehlt')
            for file, sha in manifest['output_sha256'].items():
                if digest(below(path, file)) != sha:
                    raise ValueError('Datenartefakt wurde seit der Prüfung verändert')
            for file, sha in manifest.get('code_sha256', {}).items():
                if digest(below(self.root, file)) != sha:
                    raise ValueError('Geprüfter Abfrage-/Aufbereitungscode wurde verändert')
            self.paths[package], self.manifests[package], self.pointers[package] = path, manifest, pointer
        for package, manifest in self.manifests.items():
            dependencies = manifest.get('dependencies', {})
            dependencies.update({p: manifest[p] for p in ['b01', 'b02'] if p in manifest})
            for dep, reference in dependencies.items():
                if reference['snapshot_id'] != self.pointers[dep]['snapshot_id'] or reference['manifest_sha256'] != self.pointers[dep]['manifest_sha256']:
                    raise ValueError('Datenstände sind nicht zusammengehörig')
        self.toll = None
        if (self.root / 'data/analysis/b07/current.json').exists():
            from .toll import Toll
            self.toll = Toll(self.root)
            self.pointers['b07'] = read(self.root / 'data/analysis/b07/current.json')
            self.paths['b07'] = self.root / 'data/analysis/b07/releases' / self.pointers['b07']['snapshot_id']
            self.manifests['b07'] = self.toll.manifest
        reference_path = self.root/'config/analyseassistent/DARSTELLUNGSREFERENZEN.json'
        self.display_references = read(reference_path)
        self.display_reference_sha256 = digest(reference_path)
        if self.display_references.get('schema_version') != 1:
            raise ValueError('Unbekannte Darstellungsreferenz')
        for source in ['data/processed/web_summary_by_region.json', 'data/processed/nuts3_de_2024.geojson']:
            if self.display_references['source_sha256'][source] != self.manifests['b0406']['input_sha256'][source]:
                raise ValueError('Methodikreferenz passt nicht zum geprüften Datenbestand')
        self.airport_names = self.display_references['airport_names']
        if not all(isinstance(code, str) and isinstance(name, str) and name.strip()
                   for code, name in self.airport_names.items()):
            raise ValueError('Ungültige Flughafennamen')
        self.snapshot_id = hashlib.sha256(json.dumps(
            {'datasets': self.pointers, 'display_references': self.display_reference_sha256},
            sort_keys=True).encode()).hexdigest()[:24]
        registry = read(self.paths['b0406'] / 'regions.json')
        self.names = {'DE':['Deutschland']}
        self.forecast_cell_names=read(self.paths['dashboard_access']/'forecast_cells.json') if 'dashboard_access' in self.paths else {}
        self.forecast_cell_names=read(self.paths['dashboard_access']/'forecast_cells.json') if 'dashboard_access' in self.paths else {}
        for entries in registry.values():
            for code, name in entries.items():
                self.names.setdefault(code, [])
                if name not in self.names[code]:
                    self.names[code].append(name)
        # Short city names are allowed only when unique in the source registry.
        # Augsburg/Stadt versus Augsburg/Landkreis must remain ambiguous.
        shortened={}
        for code,names in self.names.items():
            for name in names:
                alias=re.sub(r', (?:Kreisfreie Stadt|Stadtkreis|Landkreis|Kreis)$','',name)
                shortened.setdefault(alias,set()).add(code)
        for alias,codes in shortened.items():
            if len(codes)==1:
                code=next(iter(codes))
                if alias not in self.names[code]: self.names[code].append(alias)
            else:
                # Ein bloßer Ortsname bezeichnet im üblichen Sprachgebrauch die
                # Stadt. Bei einem gleichnamigen Landkreis wird die kreisfreie
                # Stadt als sichtbarer Standard verwendet.
                city_codes=[code for code in codes if any(
                    name == alias+', Kreisfreie Stadt' or name == alias+', Stadtkreis'
                    for name in self.names[code])]
                if len(city_codes)==1 and alias not in self.names[city_codes[0]]:
                    self.names[city_codes[0]].append(alias)

    def query(self, function, parameters, *, timeout_seconds=180):
        if function not in FUNCTIONS:
            raise ValueError('Funktion nicht freigegeben')
        validate(FUNCTIONS[function][3], parameters)
        if 'start' in parameters and parameters['start'] > parameters['end']:
            raise ValueError('Zeitraum ist umgekehrt')
        # Freeze pointers for a process lifetime; update means restarting after verification.
        for package, pointer in self.pointers.items():
            if read(self.root / 'data/analysis' / package / 'current.json') != pointer:
                raise ValueError('Datenstand gewechselt; Anwendung muss neu geprüft gestartet werden')
        package = FUNCTIONS[function][2]
        if package=='assistant_support' and package not in self.paths:
            return {'status':'not_available','observations':[],'note':'Das zusätzliche geprüfte Güter-/KV-Abbild ist noch nicht eingerichtet.'}
        if package=='dashboard_access' and package not in self.paths:
            return {'status':'not_available','observations':[],'note':'Dieser zusätzliche Dashboardzugriff ist noch nicht eingerichtet. Das ist eine Zugriffsgrenze des KI-Chats, kein Nachweis fehlender Quelldaten.'}
        if function == 'toll_month':
            if self.toll is None:
                return {'status': 'not_available', 'note': 'B07-Testabbild fehlt', 'unit': 'Mautfahrten'}
            return self.toll.query(**parameters)
        dispatch = {'relation_matrix': relations.relation_matrix,
                    'forecast_relation': access.forecast_relation,
                    'dashboard_detail': access.dashboard_detail,
                    'relation_overview': relations.relation_overview,
                    'relation_history': relations.relation_history,
                    'road_relation_goods_limit': relations.road_relation_goods_limit,
                    'rail_goods_history': relations.rail_goods_history,
                    'explain_scope': scope.explain_scope,
                    'goods_structure': support.goods_structure,
                    'goods_history': support.goods_history,
                    'intermodal_markets': support.intermodal_markets,
                    'node_profile': nodes.node_profile,
                    'regional_history': profiles.regional_history,
                    'modal_history': profiles.modal_history,
                    'partner_ranking': relations.partner_ranking,
                    'region_profile': profiles.region_profile,
                    'regional_modal_split': profiles.regional_modal_split,
                    'forecast_comparison': profiles.forecast_comparison,
                    'forecast_regions': profiles.forecast_regions,
                    'relation': b01.query_relation, 'compare_regions': profiles.compare_regions,
                    'union': b0406.query_union, 'time_series': b02.query_series,
                    'rail_goods': b03.query_rail, 'national': b0406.national,
                    'balance': b0406.direction_balance, 'forecast_ranking': b0406.forecast_ranking,
                    'node_partners': b0406.node_partners, 'node_statistics': b0406.node_statistics,
                    'road_details': b03.query_road}
        with duckdb.connect(config={'threads': 2, 'memory_limit': '512MB'}) as con:
            # The fixed Python functions own every SQL statement and file path.
            timer = threading.Timer(max(0.001, timeout_seconds), con.interrupt)
            timer.daemon = True
            timer.start()
            try:
                if function == 'forecast_regions' and ('goods' in parameters or 'DE' in parameters.get('regions',[])):
                    if 'dashboard_access' not in self.paths:
                        return {'status':'not_available','observations':[],'note':'Prognosegüter sind im Dashboard vorhanden, aber der zusätzliche Chat-Zugriff ist noch nicht eingerichtet.'}
                    return access.forecast_regions(con,self.paths['dashboard_access'],**{'goods':['ALL'],**parameters})
                extra = {'regional_scope': self.display_references['regional_scope']} if function == 'explain_scope' else {}
                result = dispatch[function](con, self.paths[package], **parameters, **extra)
            finally:
                timer.cancel()
        return result
