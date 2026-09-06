"""Reopen browser exports with Excel and GIS readers; never rebuild source data."""
from pathlib import Path
import argparse
import json
import sqlite3
import openpyxl
import geopandas as gpd
from PIL import Image
from shapely import from_wkb

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_directory', type=Path)
    output = parser.parse_args().output_directory
    workbook = openpyxl.load_workbook(output / 'uebersicht.xlsx')
    assert workbook['Diagramm 1']['B2'].value == 'Mio. t'
    assert workbook['Diagramm 1']['B5'].value == 3327.944617
    assert any('Quelle' in str(row[0]) for row in workbook['Auswahl und Quellen'].values)
    for sheet in workbook:
        for row in sheet:
            assert all(cell.data_type != 'f' for cell in row), 'Export must contain values, not spreadsheet formulas'
    air = openpyxl.load_workbook(output / 'luftfracht-frankfurt.xlsx')
    values = [cell.value for row in air['Tabelle 1'] for cell in row]
    assert 215169.2 in values, 'Frankfurt-Shanghai must be exported numerically in tonnes'
    assert any('ZSPD' in str(value) for value in values)
    with Image.open(output / 'modal-split.png') as image:
        assert image.format == 'PNG' and image.width == 1800 and image.height > 1000
        assert image.convert('RGB').getpixel((0, 0)) == (255, 255, 255)
    with sqlite3.connect(output / 'kartenausschnitt.gpkg') as database:
        assert database.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert not database.execute('PRAGMA foreign_key_check').fetchall()
        assert database.execute('PRAGMA application_id').fetchone()[0] == 0x47504B47
        assert database.execute('PRAGMA user_version').fetchone()[0] == 10300
        bbox = json.loads(database.execute("SELECT angabe FROM auswahl WHERE merkmal='Kartenausschnitt WGS84'").fetchone()[0])
        records = database.execute('SELECT geom,code,wert,einheit FROM kartenausschnitt').fetchall()
        assert 0 < len(records) <= 100
        for blob, code, value, unit in records:
            assert blob[:4] == b'GP\x00\x01'
            geometry = from_wkb(blob[8:])
            assert geometry.is_valid and not geometry.is_empty, code
            w,s,e,n = geometry.bounds
            assert bbox[0]-1e-8 <= w <= e <= bbox[2]+1e-8
            assert bbox[1]-1e-8 <= s <= n <= bbox[3]+1e-8
            assert isinstance(code, str) and isinstance(value, (int, float)) and unit == 't'
    frame = gpd.read_file(output / 'kartenausschnitt.gpkg', layer='kartenausschnitt')
    assert frame.crs.to_epsg() == 4326 and len(frame) == len(records)
    print(f'PASS: numeric Excel values, units and sources, no formulas, 1800 px PNG; GeoPackage reopened with GDAL: {len(frame)} valid clipped features, EPSG:4326.')

if __name__ == '__main__':
    main()
