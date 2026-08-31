#!/usr/bin/env python3
"""Create the initially separated frontend source files from current outputs.

Run this only once when adopting the modular maintenance structure.  It splits
at existing section headers and preserves every byte, including UTF-8 content.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def split_at_markers(source: bytes, markers: list[bytes]) -> list[bytes]:
    offsets = [source.index(marker) for marker in markers]
    if offsets != sorted(offsets):
        raise ValueError("Section markers are not in document order")
    return [source[start:end] for start, end in zip([0, *offsets], [*offsets, len(source)])]


def write_parts(parts: list[bytes], paths: list[Path]) -> None:
    if len(parts) != len(paths):
        raise ValueError("Part count does not match destination count")
    for part, path in zip(parts, paths):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(part)


def main() -> None:
    app = (ROOT / "js" / "app.js").read_bytes()
    write_parts(
        split_at_markers(app, [
            b"  // Helper: Compute YoY and Trend vs earliest base year (2016) for Maritime Partner Countries",
            b"  // TAB 6: INTERMODALE VERKEHRE & KV",
            b"  // TAB 7: VERKEHRSPROGNOSE 2040 (BMDV BASISPROGNOSE P1)",
            b"  // Start on DOM ready",
        ]),
        [
            ROOT / "js" / "source" / "core-head.js",
            ROOT / "js" / "modules" / "maritime.js",
            ROOT / "js" / "source" / "core-middle.js",
            ROOT / "js" / "modules" / "forecast.js",
            ROOT / "js" / "source" / "core-tail.js",
        ],
    )

    html = (ROOT / "index.html").read_bytes()
    write_parts(
        split_at_markers(html, [
            b'      <section id="tab-overview"', b'      <section id="tab-road"',
            b'      <section id="tab-rail"', b'      <section id="tab-iww"',
            b'      <section id="tab-maritime"', b'      <section id="tab-intermodal"',
            b'      <section id="tab-forecast"', b"    </main>",
        ]),
        [
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
    )

    css = (ROOT / "css" / "style.css").read_bytes()
    css_parts = split_at_markers(css, [
        b"/* Module Layout Grid: Tall Map on Left (Full Height), Analytics Stack on Right */",
        b"/* Intermodal / SGKV Layout */",
        b"/* ============================================================\n   RESPONSIVE MEDIA QUERIES",
    ])
    write_parts(css_parts, [
        ROOT / "css" / "source" / "base.css",
        ROOT / "css" / "source" / "components.css",
        ROOT / "css" / "source" / "modules.css",
        ROOT / "css" / "source" / "responsive.css",
    ])
    print("Frontend sources have been separated.")


if __name__ == "__main__":
    main()
