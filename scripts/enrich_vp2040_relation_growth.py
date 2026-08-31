#!/usr/bin/env python3
"""Add exact 2019 growth values to the displayed VP2040 relation rows.

This is also called by ``pipeline_vp2040.py`` during a full rebuild.  Keeping
it runnable separately avoids recreating both large scenario cubes when only
the relation comparison enrichment needs to be refreshed.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline_vp2040 import add_relation_growth_from_raw_matrices  # noqa: E402


def main() -> None:
    output = ROOT / "data" / "processed" / "web_forecast_2040.json"
    bundle = json.loads(output.read_text(encoding="utf-8"))
    relation_count = add_relation_growth_from_raw_matrices(
        str(ROOT), bundle["scenarios"]["2040_P1"]
    )

    temp_dir = Path("C:/tmp/gueterstroeme-vp2040")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_output = temp_dir / output.name
    try:
        temp_output.write_text(json.dumps(bundle, ensure_ascii=False), encoding="utf-8")
        shutil.copyfile(temp_output, output)
    finally:
        if temp_output.is_file():
            temp_output.unlink()
        if temp_dir.is_dir() and not any(temp_dir.iterdir()):
            temp_dir.rmdir()

    print(f"Relation growth enrichment complete for {relation_count:,} displayed relations.")


if __name__ == "__main__":
    main()
