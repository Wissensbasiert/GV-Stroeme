"""Regression: a checksum-valid package can still omit forecast dependencies."""
import json
from pathlib import Path
import unittest
from scripts.analysis.build_assistant_release import validate_public_data_files


class BrowserDataCompleteness(unittest.TestCase):
    def test_actual_forecast_loader_requires_both_crosswalks(self):
        root=Path(__file__).resolve().parents[2]
        source=(root/'js/app.js').read_text(encoding='utf-8')
        # Reconstruct dependencies from the actual literal fetch calls.
        import re
        files={'public/'+m[1]:'checked' for m in re.findall(r'\bfetchJson\s*\(\s*([\'"])(data/[^\'"?]+)',source)}
        for name in ['crosswalk_spatial_vp2040.json','crosswalk_nst_vp2040.json']:
            key='public/data/crosswalks/'+name
            self.assertIn(key,files)
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,name):
                validate_public_data_files(source,{k:v for k,v in files.items() if k!=key})
        checked=validate_public_data_files(source,files)
        self.assertIn('public/data/processed/web_forecast_core.json',checked)


if __name__=='__main__': unittest.main()
