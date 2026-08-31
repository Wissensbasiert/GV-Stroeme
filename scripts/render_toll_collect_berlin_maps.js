#!/usr/bin/env node
/* Rendert zwei statische Deutschlandkarten aus den aggregierten GeoJSON-Dateien. */

const fs = require("fs");
const path = require("path");
const { createCanvas } = require("@napi-rs/canvas");

const INPUT_DIR = path.join("outputs", "mautdaten_berlin_auswertung", "karten");
const OUTPUTS = [
  {
    input: "berlin_von_berlin_2025-08_bis_2026-07.geojson",
    output: "karte_relationen_von_berlin_2025-08_bis_2026-07.png",
    reportOutput: "karte_relationen_von_berlin_bericht.jpg",
    title: "Mautfahrten von Berlin zu externen Gemeinden",
  },
  {
    input: "berlin_nach_berlin_2025-08_bis_2026-07.geojson",
    output: "karte_relationen_nach_berlin_2025-08_bis_2026-07.png",
    reportOutput: "karte_relationen_nach_berlin_bericht.jpg",
    title: "Mautfahrten von externen Gemeinden nach Berlin",
  },
];

const WIDTH = 1800;
const HEIGHT = 1180;
const MAP = { left: 64, top: 130, width: 1160, height: 850 };
const LEGEND_X = 1305;
const BERLIN = [13.405, 52.52];

function mercatorY(latitude) {
  const radians = (latitude * Math.PI) / 180;
  return Math.log(Math.tan(Math.PI / 4 + radians / 2));
}

function mercatorX(longitude) {
  return (longitude * Math.PI) / 180;
}

function visitCoordinates(geometry, callback) {
  if (!geometry) return;
  const walk = (coordinates) => {
    if (!Array.isArray(coordinates)) return;
    if (typeof coordinates[0] === "number" && typeof coordinates[1] === "number") {
      callback(coordinates[0], coordinates[1]);
      return;
    }
    coordinates.forEach(walk);
  };
  walk(geometry.coordinates);
}

function boundsFor(features) {
  const bounds = { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity };
  for (const feature of features) {
    visitCoordinates(feature.geometry, (lon, lat) => {
      const x = mercatorX(lon);
      const y = mercatorY(lat);
      bounds.minX = Math.min(bounds.minX, x);
      bounds.maxX = Math.max(bounds.maxX, x);
      bounds.minY = Math.min(bounds.minY, y);
      bounds.maxY = Math.max(bounds.maxY, y);
    });
  }
  const paddingX = (bounds.maxX - bounds.minX) * 0.055;
  const paddingY = (bounds.maxY - bounds.minY) * 0.055;
  bounds.minX -= paddingX;
  bounds.maxX += paddingX;
  bounds.minY -= paddingY;
  bounds.maxY += paddingY;
  return bounds;
}

function projector(bounds) {
  const scale = Math.min(
    MAP.width / (bounds.maxX - bounds.minX),
    MAP.height / (bounds.maxY - bounds.minY),
  );
  const drawnWidth = (bounds.maxX - bounds.minX) * scale;
  const drawnHeight = (bounds.maxY - bounds.minY) * scale;
  const offsetX = MAP.left + (MAP.width - drawnWidth) / 2;
  const offsetY = MAP.top + (MAP.height - drawnHeight) / 2;
  return (lon, lat) => [
    offsetX + (mercatorX(lon) - bounds.minX) * scale,
    offsetY + (bounds.maxY - mercatorY(lat)) * scale,
  ];
}

function mix(a, b, t) {
  return Math.round(a + (b - a) * t);
}

function colourFor(value, minValue, maxValue) {
  const t = Math.max(0, Math.min(1, (Math.log10(value) - Math.log10(minValue)) / (Math.log10(maxValue) - Math.log10(minValue))));
  const start = [227, 242, 237];
  const end = [0, 91, 69];
  return `rgb(${mix(start[0], end[0], t)}, ${mix(start[1], end[1], t)}, ${mix(start[2], end[2], t)})`;
}

function polygonPath(context, rings, project) {
  for (const ring of rings) {
    ring.forEach((coordinate, index) => {
      const [x, y] = project(coordinate[0], coordinate[1]);
      if (index === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    });
    context.closePath();
  }
}

function drawGeometry(context, geometry, project) {
  context.beginPath();
  if (geometry.type === "Polygon") polygonPath(context, geometry.coordinates, project);
  else if (geometry.type === "MultiPolygon") geometry.coordinates.forEach((polygon) => polygonPath(context, polygon, project));
}

function number(value) {
  return new Intl.NumberFormat("de-DE").format(value);
}

function drawMap(config) {
  const collection = JSON.parse(fs.readFileSync(path.join(INPUT_DIR, config.input), "utf8"));
  const features = collection.features;
  const values = features.map((feature) => feature.properties.befahrungen);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const bounds = boundsFor(features);
  const project = projector(bounds);
  const canvas = createCanvas(WIDTH, HEIGHT);
  const context = canvas.getContext("2d");

  context.fillStyle = "#f8faf9";
  context.fillRect(0, 0, WIDTH, HEIGHT);
  context.fillStyle = "#17382f";
  context.font = "700 42px Segoe UI, Arial, sans-serif";
  context.fillText(config.title, 64, 58);
  context.fillStyle = "#49645c";
  context.font = "24px Segoe UI, Arial, sans-serif";
  context.fillText("August 2025 bis Juli 2026 · ohne Relation Berlin–Berlin · Farbskala: Summe der Befahrungen", 64, 95);

  context.fillStyle = "#ffffff";
  context.strokeStyle = "#cbd8d3";
  context.lineWidth = 1;
  context.fillRect(MAP.left, MAP.top, MAP.width, MAP.height);
  context.strokeRect(MAP.left, MAP.top, MAP.width, MAP.height);

  const regular = features.filter((feature) => !feature.properties.top_10);
  const topTen = features.filter((feature) => feature.properties.top_10);
  for (const feature of regular) {
    drawGeometry(context, feature.geometry, project);
    context.fillStyle = colourFor(feature.properties.befahrungen, minValue, maxValue);
    context.fill("evenodd");
    context.strokeStyle = "rgba(255,255,255,0.38)";
    context.lineWidth = 0.35;
    context.stroke();
  }
  for (const feature of topTen) {
    drawGeometry(context, feature.geometry, project);
    context.fillStyle = colourFor(feature.properties.befahrungen, minValue, maxValue);
    context.fill("evenodd");
    context.strokeStyle = "#e05b36";
    context.lineWidth = 3.2;
    context.stroke();
  }

  const [berlinX, berlinY] = project(BERLIN[0], BERLIN[1]);
  context.beginPath();
  context.arc(berlinX, berlinY, 6.5, 0, Math.PI * 2);
  context.fillStyle = "#1a2522";
  context.fill();
  context.strokeStyle = "#ffffff";
  context.lineWidth = 2;
  context.stroke();
  context.fillStyle = "#1a2522";
  context.font = "700 18px Segoe UI, Arial, sans-serif";
  context.fillText("Berlin", berlinX + 12, berlinY - 10);

  context.fillStyle = "#17382f";
  context.font = "700 26px Segoe UI, Arial, sans-serif";
  context.fillText("Leseschlüssel", LEGEND_X, 165);
  context.font = "20px Segoe UI, Arial, sans-serif";
  context.fillStyle = "#49645c";
  context.fillText("Befahrungen je Gemeinde", LEGEND_X, 196);
  const gradient = context.createLinearGradient(LEGEND_X, 235, LEGEND_X, 465);
  gradient.addColorStop(0, colourFor(maxValue, minValue, maxValue));
  gradient.addColorStop(1, colourFor(minValue, minValue, maxValue));
  context.fillStyle = gradient;
  context.fillRect(LEGEND_X, 235, 32, 230);
  context.strokeStyle = "#9db1aa";
  context.lineWidth = 1;
  context.strokeRect(LEGEND_X, 235, 32, 230);
  context.fillStyle = "#49645c";
  context.font = "18px Segoe UI, Arial, sans-serif";
  [maxValue, Math.sqrt(minValue * maxValue), minValue].forEach((value, index) => {
    const y = 242 + index * 108;
    context.fillText(number(Math.round(value)), LEGEND_X + 48, y);
  });
  context.strokeStyle = "#e05b36";
  context.lineWidth = 3.2;
  context.strokeRect(LEGEND_X, 500, 32, 22);
  context.fillStyle = "#49645c";
  context.fillText("Top-10-Relation", LEGEND_X + 48, 518);

  context.fillStyle = "#17382f";
  context.font = "700 26px Segoe UI, Arial, sans-serif";
  context.fillText("Top 10", LEGEND_X, 577);
  const topRows = [...topTen].sort((a, b) => a.properties.rang_nach_befahrungen - b.properties.rang_nach_befahrungen);
  topRows.forEach((feature, index) => {
    const y = 616 + index * 42;
    context.fillStyle = "#e05b36";
    context.beginPath();
    context.arc(LEGEND_X + 11, y - 6, 11, 0, Math.PI * 2);
    context.fill();
    context.fillStyle = "#ffffff";
    context.font = "700 14px Segoe UI, Arial, sans-serif";
    context.textAlign = "center";
    context.fillText(String(feature.properties.rang_nach_befahrungen), LEGEND_X + 11, y - 1);
    context.textAlign = "left";
    context.fillStyle = "#17382f";
    context.font = "18px Segoe UI, Arial, sans-serif";
    const shortName = feature.properties.gebiet.replace(/^(Gemeinde|Stadt), /, "");
    context.fillText(shortName, LEGEND_X + 32, y);
    context.fillStyle = "#49645c";
    context.textAlign = "right";
    context.fillText(number(feature.properties.befahrungen), 1740, y);
    context.textAlign = "left";
  });

  context.fillStyle = "#49645c";
  context.font = "16px Segoe UI, Arial, sans-serif";
  const note = "Hinweis: Gemeinden stehen für Eintritt bzw. Austritt aus dem Mautnetz, nicht zwingend für tatsächliche Start- und Zielorte.";
  context.fillText(note, 64, 1085);
  context.fillText("Quelle: Bundesamt für Logistik und Mobilität, Toll Collect GmbH; Gemeindegeometrien: BKG.", 64, 1113);

  const output = path.join(INPUT_DIR, config.output);
  fs.writeFileSync(output, canvas.toBuffer("image/png"));
  const reportCanvas = createCanvas(960, 629);
  reportCanvas.getContext("2d").drawImage(canvas, 0, 0, 960, 629);
  fs.writeFileSync(
    path.join(INPUT_DIR, config.reportOutput),
    reportCanvas.toBuffer("image/jpeg", 82),
  );
  console.log(output);
}

OUTPUTS.forEach(drawMap);
