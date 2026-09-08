"""Erstellt eine druckfeste HTML-Fassung der Berlin-Mautdaten-Auswertung.

Die HTML-Datei ist die statische Quelle für den PDF-Export. Sie nutzt die
vorhandenen Analyseergebnisse und Karten und verändert keine Roh- oder
Auswertungsdaten.
"""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "mautdaten_berlin_auswertung" / "bericht"
ANALYSIS_PATH = ROOT / "outputs" / "mautdaten_berlin_auswertung" / "analysis_data.json"
OUTPUT_PATH = OUTPUT_DIR / "Berlin_Mautfahrten_Auswertung_2025-08_bis_2026-07.html"

BLUE = "#2f6f9f"
ORANGE = "#d97706"
GREEN = "#2f855a"
GRID = "#d9e2e8"


def fmt_int(value: float | int) -> str:
    return f"{round(value):,}".replace(",", ".")


def fmt_pct(value: float) -> str:
    return f"{value:.2f}".replace(".", ",") + " %"


def esc(value: object) -> str:
    return html.escape(str(value))


def line_chart(rows: list[dict], value_field: str, y_label: str, title: str, percent: bool = False) -> str:
    width, height = 920, 330
    left, right, top, bottom = 72, 22, 26, 58
    plot_w, plot_h = width - left - right, height - top - bottom
    periods = [row["zeitraum"] for row in rows if row["perspektive"] == "Berlin als Quelle"]
    groups = {
        "Berlin als Quelle": (BLUE, [row[value_field] for row in rows if row["perspektive"] == "Berlin als Quelle"]),
        "Berlin als Ziel": (ORANGE, [row[value_field] for row in rows if row["perspektive"] == "Berlin als Ziel"]),
    }
    all_values = [value for _, values in groups.values() for value in values]
    maximum = max(all_values) * 1.08 if all_values else 1
    ticks = [maximum * part / 4 for part in range(5)]
    grid = []
    for tick in ticks:
        y = top + plot_h - tick / maximum * plot_h
        label = fmt_pct(tick) if percent else fmt_int(tick)
        grid.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" class="grid"/><text x="{left-10}" y="{y+4:.1f}" text-anchor="end" class="axis">{label}</text>')
    x_labels = []
    for index, label in enumerate(periods):
        x = left + (plot_w * index / max(len(periods) - 1, 1))
        short = label.split()[0][:3] + " " + label.split()[1][-2:]
        x_labels.append(f'<text x="{x:.1f}" y="{height-30}" text-anchor="middle" class="axis">{esc(short)}</text>')
    paths = []
    legend = []
    for index, (name, (color, values)) in enumerate(groups.items()):
        coords = []
        for point, value in enumerate(values):
            x = left + (plot_w * point / max(len(values) - 1, 1))
            y = top + plot_h - value / maximum * plot_h
            coords.append(f"{x:.1f},{y:.1f}")
        paths.append(f'<polyline points="{" ".join(coords)}" class="series" stroke="{color}"/>')
        for point, value in enumerate(values):
            x = left + (plot_w * point / max(len(values) - 1, 1))
            y = top + plot_h - value / maximum * plot_h
            paths.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{color}"/>')
        lx = left + index * 210
        legend.append(f'<rect x="{lx}" y="5" width="15" height="5" fill="{color}" rx="2"/><text x="{lx+22}" y="12" class="legend">{name}</text>')
    return f'''<figure><figcaption>{esc(title)}</figcaption><svg viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}"><style>.grid{{stroke:{GRID};stroke-width:1}}.axis{{font:12px Arial;fill:#50616d}}.series{{fill:none;stroke-width:3;stroke-linejoin:round;stroke-linecap:round}}.legend{{font:13px Arial;fill:#263746}}</style>{''.join(grid)}{''.join(paths)}{''.join(x_labels)}{''.join(legend)}<text x="18" y="{top+plot_h/2:.1f}" class="axis" transform="rotate(-90 18 {top+plot_h/2:.1f})">{esc(y_label)}</text></svg></figure>'''


def horizontal_bar_chart(rows: list[dict], title: str) -> str:
    width, height = 920, 380
    left, right, top, bottom = 275, 85, 28, 20
    plot_w = width - left - right
    maximum = max(row["befahrungen"] for row in rows) * 1.08
    bar_h = (height - top - bottom) / len(rows) * 0.66
    bars = []
    for index, row in enumerate(rows):
        y = top + index * ((height - top - bottom) / len(rows))
        bar_w = row["befahrungen"] / maximum * plot_w
        bars.append(f'<text x="{left-10}" y="{y+bar_h*0.78:.1f}" text-anchor="end" class="axis">{esc(row["gebiet"].replace("Gemeinde, ", "").replace("Stadt, ", ""))}</text>')
        bars.append(f'<rect x="{left}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{BLUE}" rx="3"/>')
        bars.append(f'<text x="{left+bar_w+7:.1f}" y="{y+bar_h*0.76:.1f}" class="value">{fmt_int(row["befahrungen"])} · {fmt_pct(row["anteil_prozent"])}</text>')
    return f'''<figure><figcaption>{esc(title)}</figcaption><svg viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}"><style>.axis{{font:12px Arial;fill:#334b5c}}.value{{font:11.5px Arial;fill:#50616d}}</style>{''.join(bars)}</svg></figure>'''


def grouped_distance_chart(rows: list[dict]) -> str:
    labels = ["unter 50", "50–100", "100–200", "200–300", "≥ 300"]
    source = [row for row in rows if row["perspektive"] == "Berlin als Quelle"]
    target = [row for row in rows if row["perspektive"] == "Berlin als Ziel"]
    width, height, left, right, top, bottom = 920, 340, 72, 25, 28, 62
    plot_w, plot_h = width-left-right, height-top-bottom
    maximum = max(row["befahrungen"] for row in rows) * 1.08
    parts = []
    for ratio in range(5):
        val = maximum * ratio / 4
        y = top + plot_h - val / maximum * plot_h
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" class="grid"/><text x="{left-10}" y="{y+4:.1f}" text-anchor="end" class="axis">{fmt_int(val)}</text>')
    group_w = plot_w / len(labels)
    for idx, label in enumerate(labels):
        x = left + idx*group_w + group_w*0.17
        for offset, (row, color) in enumerate(((source[idx], BLUE), (target[idx], ORANGE))):
            bh = row["befahrungen"] / maximum * plot_h
            bx = x + offset * group_w*0.28
            by = top + plot_h - bh
            parts.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{group_w*0.22:.1f}" height="{bh:.1f}" fill="{color}" rx="3"/>')
        parts.append(f'<text x="{left+(idx+0.5)*group_w:.1f}" y="{height-30}" text-anchor="middle" class="axis">{label} km</text>')
    parts.append(f'<rect x="{left}" y="6" width="15" height="5" fill="{BLUE}" rx="2"/><text x="{left+22}" y="13" class="legend">Berlin als Quelle</text><rect x="{left+180}" y="6" width="15" height="5" fill="{ORANGE}" rx="2"/><text x="{left+202}" y="13" class="legend">Berlin als Ziel</text>')
    return f'''<figure><figcaption>Befahrungen ohne Berlin–Berlin nach Distanzklasse</figcaption><svg viewBox="0 0 {width} {height}" role="img" aria-label="Befahrungen ohne Berlin–Berlin nach Distanzklasse"><style>.grid{{stroke:{GRID};stroke-width:1}}.axis{{font:12px Arial;fill:#50616d}}.legend{{font:13px Arial;fill:#263746}}</style>{''.join(parts)}</svg></figure>'''


def table(rows: list[dict], columns: list[tuple[str, str, callable]]) -> str:
    header = ''.join(f"<th>{esc(label)}</th>" for _, label, _ in columns)
    body = []
    for row in rows:
        cells = ''.join(f"<td>{esc(formatter(row[field]))}</td>" for field, _, formatter in columns)
        body.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def main() -> None:
    data = json.loads(ANALYSIS_PATH.read_text(encoding="utf-8"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    monthly_external = data["monthly_external"]
    for row in monthly_external:
        direction_total = sum(item["befahrungen"] for item in monthly_external if item["perspektive"] == row["perspektive"])
        row["anteil_am_richtungsvolumen"] = row["befahrungen"] / direction_total * 100
    sources = data["top_external_sources_to_berlin_mit_zeiten_distanzen"]
    targets = data["top_external_targets_from_berlin_mit_zeiten_distanzen"]
    thresholds = []
    for row in data["schwelle_300_km_extern"]:
        total = row["befahrungen_insgesamt"]
        thresholds.append({
            "perspektive": row["perspektive"],
            "gesamt": f"{fmt_int(total)} (100,00 %)",
            "kern": f"{fmt_int(row['befahrungen_relation_mittelwert_ab_300_km'])} ({fmt_pct(row['befahrungen_relation_mittelwert_ab_300_km'] / total * 100)})",
            "unten": f"{fmt_int(row['befahrungen_sicher_ab_300_km'])} ({fmt_pct(row['befahrungen_sicher_ab_300_km'] / total * 100)})",
            "oben": f"{fmt_int(row['befahrungen_potenziell_ab_300_km'])} ({fmt_pct(row['befahrungen_potenziell_ab_300_km'] / total * 100)})",
        })
    comparison = data["richtungsvergleich"]["ohne_berlin_berlin"]
    source_total = comparison["befahrungen_von_berlin_gesamt"]
    target_total = comparison["befahrungen_nach_berlin_gesamt"]
    top_source_table = table(sources, [
        ("rang", "Rang", str), ("gebiet", "Quellgebiet", str), ("befahrungen", "Befahrungen", fmt_int),
        ("anteil_prozent", "Anteil", fmt_pct), ("gewichtete_fahrzeit_min", "Mittlere Fahrzeit", lambda x: f"{x:.1f} Min.".replace(".", ",")),
        ("gewichtete_distanz_km", "Mittlere Distanz", lambda x: f"{x:.1f} km".replace(".", ",")),
    ])
    top_target_table = table(targets, [
        ("rang", "Rang", str), ("gebiet", "Zielgebiet", str), ("befahrungen", "Befahrungen", fmt_int),
        ("anteil_prozent", "Anteil", fmt_pct), ("gewichtete_fahrzeit_min", "Mittlere Fahrzeit", lambda x: f"{x:.1f} Min.".replace(".", ",")),
        ("gewichtete_distanz_km", "Mittlere Distanz", lambda x: f"{x:.1f} km".replace(".", ",")),
    ])
    threshold_table = table(thresholds, [
        ("perspektive", "Perspektive", str), ("gesamt", "Befahrungen ohne Berlin–Berlin", str),
        ("kern", "Kernwert: mittlere Distanz der Relation ≥ 300 km", str),
        ("unten", "Untergrenze: Distanz-Minimum der Relation ≥ 300 km", str),
        ("oben", "Obergrenze: Distanz-Maximum der Relation ≥ 300 km", str),
    ])
    total_monthly = sorted(monthly_external, key=lambda item: (item["jahr"], item["monat"]))
    source_under_50 = next(row for row in data["distanzklassen_extern"] if row["perspektive"] == "Berlin als Quelle" and row["distanzklasse"] == "unter 50 km")
    target_under_50 = next(row for row in data["distanzklassen_extern"] if row["perspektive"] == "Berlin als Ziel" and row["distanzklasse"] == "unter 50 km")
    html_report = f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Berlin: Mautfahrten nach Start und Ziel, August 2025 bis Juli 2026</title>
<style>
@page {{ size:A4; margin:13mm 12mm 14mm; }}
* {{ box-sizing:border-box; }} body {{ color:#243746; font:10pt/1.45 Arial, sans-serif; margin:0; }}
h1 {{ color:#174c73; font-size:22pt; line-height:1.12; margin:0 0 6mm; }} h2 {{ color:#174c73; font-size:15pt; margin:10mm 0 3mm; page-break-after:avoid; }} h3 {{ color:#174c73; font-size:11.5pt; margin:6mm 0 2mm; page-break-after:avoid; }}
p {{ margin:0 0 3mm; }} .subtitle {{ color:#50616d; font-size:11pt; margin-bottom:7mm; }} .lead {{ border-left:4px solid {BLUE}; background:#f2f7fa; padding:4mm 5mm; margin:4mm 0 7mm; font-size:10.5pt; }}
.metrics {{ display:grid; grid-template-columns:repeat(2,1fr); gap:3mm; margin:4mm 0 6mm; }} .metric {{ background:#f5f8fa; border:1px solid #dbe5ea; border-radius:4px; padding:3mm; }} .metric strong {{ display:block; color:#174c73; font-size:15pt; }}
figure {{ border:1px solid #dbe5ea; border-radius:4px; margin:5mm 0 6mm; padding:3mm; page-break-inside:avoid; }} figcaption {{ color:#174c73; font-weight:bold; font-size:10pt; margin:0 0 2mm; }} svg {{ display:block; width:100%; height:auto; }}
.maps {{ display:grid; grid-template-columns:1fr 1fr; gap:4mm; }} .map img {{ display:block; width:100%; height:auto; border:1px solid #dbe5ea; }} .map p {{ font-weight:bold; margin:0 0 2mm; }}
table {{ border-collapse:collapse; font-size:8.2pt; margin:3mm 0 7mm; width:100%; page-break-inside:auto; }} th {{ background:#174c73; color:white; font-weight:bold; }} th,td {{ border:1px solid #cbd8df; padding:1.8mm 1.6mm; text-align:left; vertical-align:top; }} tr {{ page-break-inside:avoid; }} tbody tr:nth-child(even) {{ background:#f5f8fa; }}
.note {{ background:#fff9ed; border-left:4px solid {ORANGE}; padding:3.5mm 4mm; margin:4mm 0; }} .small {{ color:#50616d; font-size:8.7pt; }} .break {{ break-before:page; }}
</style></head><body>
<h1>Berlin: Mautfahrten nach Start und Ziel</h1>
<p class="subtitle">Start-Ziel-Analyse des Lkw-Verkehrsportals · August 2025 bis Juli 2026 · Statische PDF-Fassung</p>
<div class="lead"><strong>Ergebnis in Kürze:</strong> Die Auswertung zeigt {fmt_int(source_total)} Mautfahrten von Berlin und {fmt_int(target_total)} nach Berlin ohne die administrative Relation Berlin–Berlin. Das direkte Berliner Umland prägt das Bild deutlich; nach mittlerer Relationsdistanz entfallen rund {fmt_pct(source_under_50['anteil_prozent'])} bzw. {fmt_pct(target_under_50['anteil_prozent'])} auf Distanzen unter 50 km.</div>
<div class="metrics"><div class="metric"><strong>{fmt_int(source_total)}</strong>Berlin als Quelle<br><span class="small">ohne Berlin–Berlin</span></div><div class="metric"><strong>{fmt_int(target_total)}</strong>Berlin als Ziel<br><span class="small">ohne Berlin–Berlin</span></div></div>
<h2>Entwicklung der Mautfahrten</h2>
<p>Die monatlichen Verläufe beider Richtungen sind sehr ähnlich. Das ist ein Befund zur Anzahl der Mautfahrten – nicht zum Warenwert, zur Gütermenge oder zur Beladung der Fahrzeuge.</p>
{line_chart(total_monthly, 'befahrungen', 'Befahrungen', 'Mautfahrten ohne Berlin–Berlin nach Richtung')}
<h2>Häufigste Relationen außerhalb Berlins</h2>
<p>Die zehn wichtigsten Quell- und Zielgebiete liegen überwiegend im Berliner Umland. Die Anteile beziehen sich jeweils auf alle Befahrungen ohne Berlin–Berlin in der betreffenden Richtung.</p>
{horizontal_bar_chart(sources, 'Zehn wichtigste Quellgebiete außerhalb Berlins nach Berlin')}
{top_source_table}
{horizontal_bar_chart(targets, 'Zehn wichtigste Zielgebiete außerhalb Berlins von Berlin')}
{top_target_table}
<div class="break"></div><h2>Räumliche Verteilung der Relationen</h2>
<p>Die Karten zeigen alle beteiligten Gemeinden mit einer Farbskala nach Anzahl der Befahrungen. Die zehn stärksten Relationen sind hervorgehoben. Sie stellen Ein- bzw. Austrittsgemeinden auf dem mautpflichtigen Netz dar.</p>
<div class="maps"><div class="map"><p>Von Berlin</p><img src="../karten/karte_relationen_von_berlin_bericht.jpg" alt="Karte der Mautfahrten von Berlin"></div><div class="map"><p>Nach Berlin</p><img src="../karten/karte_relationen_nach_berlin_bericht.jpg" alt="Karte der Mautfahrten nach Berlin"></div></div>
<h2>Distanz und Fahrzeit</h2>
<p>Für die Distanzklassen wird die mittlere Distanz der jeweils aggregierten Monatsrelation verwendet. Damit ist die Darstellung eine Einordnung auf Relationsniveau, keine Auszählung einzelner Fahrten mit exakt derselben Distanz.</p>
{grouped_distance_chart(data['distanzklassen_extern'])}
<h3>Einordnung der 300-km-Schwelle</h3>
<div class="note"><strong>Der Kernwert ist maßgeblich.</strong> Er klassifiziert Befahrungen anhand der mittleren Distanz der aggregierten Monatsrelation. Die Untergrenze umfasst nur Relationen, deren minimale Distanz bereits mindestens 300 km beträgt. Die Obergrenze umfasst Relationen, in denen mindestens eine Fahrt 300 km erreicht; sie ist deshalb keine exakte Zahl einzelner langer Fahrten.</div>
{threshold_table}
<h2>Grenzen der Interpretation</h2>
<p>Die Daten bilden Mautfahrten auf dem mautpflichtigen Netz ab, nicht den gesamten Lkw-Verkehr. Eine Mautfahrt beginnt beim Eintritt in das mautpflichtige Netz und endet beim Austritt. Quelle und Ziel bezeichnen somit die Verwaltungsgebiete dieses Eintritts beziehungsweise Austritts; der nicht mautpflichtige Vor- und Nachlauf kann in anderen Gemeinden liegen.</p>
<p>Die vorliegenden Start-Ziel-Daten enthalten keine Achs- oder Gewichtsklasse und keine Nutzlast. Daher können die Fahrten nicht direkt in Tonnen oder Tonnenkilometer überführt und nicht unmittelbar mit Gütermengen im Schienen- oder Binnenschiffsverkehr verglichen werden.</p>
<h2>Quelle und Datenstand</h2>
<p class="small">Quelle: Bundesamt für Logistik und Mobilität, Toll Collect GmbH und Bundesamt für Kartographie und Geodäsie; Lkw-Verkehrsportal, Start-Ziel-Analyse auf Gemeindeebene. Datenzeitraum: August 2025 bis Juli 2026. Grundlage: anonymisierte Mautfahrten auf dem mautpflichtigen Netz. Lizenz: Datenlizenz Deutschland – Namensnennung – Version 2.0.</p>
</body></html>'''
    OUTPUT_PATH.write_text(html_report, encoding="utf-8")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
