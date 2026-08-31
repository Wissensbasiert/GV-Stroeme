#!/usr/bin/env python3
"""Build the browser files from small, maintainable source fragments.

The generated files remain the files delivered by the static website.  Do not
edit them directly: update the relevant source fragment and run this script.
All input and output are treated as UTF-8 bytes so German umlauts remain
unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BUNDLES = {
    "app": {
        "output": ROOT / "js" / "app.js",
        "parts": [
            ROOT / "js" / "source" / "core-head.js",
            ROOT / "js" / "modules" / "maritime.js",
            ROOT / "js" / "source" / "core-middle.js",
            ROOT / "js" / "modules" / "forecast.js",
            ROOT / "js" / "source" / "core-tail.js",
        ],
    },
    "html": {
        "output": ROOT / "index.html",
        "parts": [
            ROOT / "html" / "shell-head.html",
            ROOT / "html" / "modules" / "overview.html",
            ROOT / "html" / "modules" / "road.html",
            ROOT / "html" / "modules" / "rail.html",
            ROOT / "html" / "modules" / "iww.html",
            ROOT / "html" / "modules" / "maritime.html",
            ROOT / "html" / "modules" / "intermodal.html",
            ROOT / "html" / "modules" / "forecast.html",
            ROOT / "html" / "shell-tail.html",
        ],
    },
    "css": {
        "output": ROOT / "css" / "style.css",
        "parts": [
            ROOT / "css" / "source" / "base.css",
            ROOT / "css" / "source" / "components.css",
            ROOT / "css" / "source" / "modules.css",
            ROOT / "css" / "source" / "responsive.css",
        ],
    },
}


def build(names: list[str]) -> None:
    for name in names:
        bundle = BUNDLES[name]
        missing = [str(part.relative_to(ROOT)) for part in bundle["parts"] if not part.is_file()]
        if missing:
            raise FileNotFoundError(f"{name}: missing source file(s): {', '.join(missing)}")
        content = b"".join(part.read_bytes() for part in bundle["parts"])
        bundle["output"].write_bytes(content)
        digest = hashlib.sha256(content).hexdigest()[:12]
        print(f"{name}: {bundle['output'].relative_to(ROOT)} ({len(content):,} bytes, sha256 {digest})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", choices=[*BUNDLES, "all"], nargs="?", default="all")
    args = parser.parse_args()
    build(list(BUNDLES) if args.bundle == "all" else [args.bundle])


if __name__ == "__main__":
    main()
