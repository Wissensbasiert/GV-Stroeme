#!/usr/bin/env python3
"""Erzeugt die Gemeinde-Suchliste für das Live-Mautdatenmodul.

Die Relationswerte werden nicht übernommen. Sie werden im Dashboard weiterhin
gezielt nach Gemeinde, Monat und Richtung aus der Toll-Collect-API geladen.
"""

from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "data" / "raw" / "Straße" / "Lkw-Portal"
OUTPUT = ROOT / "data" / "processed" / "toll_municipalities.json"
ZIP_PATTERN = re.compile(r"mautdaten_bund_monat_sz_(\d{4})-(\d{2})\.zip$")


def latest_monthly_zip() -> tuple[Path, str]:
    candidates: list[tuple[str, Path]] = []
    for path in INPUT_DIR.glob("mautdaten_bund_monat_sz_*.zip"):
        match = ZIP_PATTERN.fullmatch(path.name)
        if match:
            candidates.append((f"{match.group(1)}-{match.group(2)}", path))
    if not candidates:
        raise FileNotFoundError("Kein bundesweiter Toll-Collect-Monatsdownload gefunden.")
    month, path = max(candidates)
    return path, month


def read_municipalities(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    with zipfile.ZipFile(path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise RuntimeError(f"Erwartet wurde genau eine CSV im ZIP, gefunden: {csv_names}")
        with archive.open(csv_names[0]) as raw_handle:
            # utf-8-sig toleriert zusätzlich einen möglichen BOM, ohne Umlaute
            # und andere Zeichen der amtlichen Bezeichnungen zu verändern.
            with io.TextIOWrapper(raw_handle, encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle, delimiter=";")
                required = {"ags_start", "ags_ziel", "name_start", "name_ziel"}
                missing = required.difference(reader.fieldnames or [])
                if missing:
                    raise RuntimeError(f"Felder im Monatsdownload fehlen: {sorted(missing)}")
                for row in reader:
                    for ags_field, name_field in (
                        ("ags_start", "name_start"),
                        ("ags_ziel", "name_ziel"),
                    ):
                        ags = str(row.get(ags_field, "")).strip()
                        name = str(row.get(name_field, "")).strip()
                        if len(ags) == 8 and ags.isdigit() and name:
                            previous = result.get(ags)
                            if previous and previous != name:
                                raise RuntimeError(
                                    f"Widersprüchliche Gemeindebezeichnung für AGS {ags}: "
                                    f"{previous!r} / {name!r}"
                                )
                            result[ags] = name
    return result


def main() -> None:
    source_path, latest_month = latest_monthly_zip()
    municipalities = read_municipalities(source_path)
    payload = {
        "metadata": {
            "source_file": source_path.name,
            "source_month": latest_month,
            "purpose": "Gemeinde-Suchliste; keine Relationswerte",
            "provider": "Bundesamt für Logistik und Mobilität / Toll Collect GmbH",
            "count": len(municipalities),
        },
        "municipalities": [
            {"ags": ags, "name": name}
            for ags, name in sorted(
                municipalities.items(), key=lambda item: (item[1].casefold(), item[0])
            )
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"{OUTPUT.relative_to(ROOT)}: {len(municipalities)} Gemeinden, Stand {latest_month}")


if __name__ == "__main__":
    main()
