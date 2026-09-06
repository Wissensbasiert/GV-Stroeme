# Lokal ausgelieferte Exportbibliotheken

Die Bibliotheken werden erst bei einem entsprechenden Export geladen. Es werden keine Auswertungsdaten an externe Exportdienste übermittelt.

| Datei | Bibliothek | Lizenz |
|---|---|---|
| `exceljs/exceljs.min.js` | ExcelJS 4.4.0 | MIT; `exceljs/LICENSE` |
| `sqljs/sql-wasm.js`, `sqljs/sql-wasm.wasm` | sql.js 1.13.0 | MIT; `sqljs/LICENSE` |
| `polygon-clip.js` | polygon-clipping 0.15.7; robust-predicates 3.0.3; splaytree 3.2.3 | MIT bzw. Unlicense; zugehörige LICENSE-Dateien in diesem Ordner |

Originale: https://github.com/exceljs/exceljs, https://github.com/sql-js/sql.js, https://github.com/mfogel/polygon-clipping.
GeoPackage-Struktur: https://www.geopackage.org/spec131/.

## Reproduzierbare Pflege

Pakete und Buildwerkzeuge ausschließlich in einem eigenen Ordner unter `C:\tmp` installieren. Die unveränderten ExcelJS- und sql.js-Distributionsdateien sowie ihre Lizenzen werden von dort hierher kopiert. Keine `node_modules` im Projekt anlegen.

Für `polygon-clip.js` wird folgende kleine Fassade mit esbuild 0.25.9 als minimiertes IIFE gebündelt (ohne Source Map):

```javascript
import polygonClipping from 'polygon-clipping';
window.wbpClipPolygon = (feature, bbox) => {
  const [w,s,e,n] = bbox;
  const coordinates = polygonClipping.intersection(feature.geometry.coordinates,
    [[[w,s],[e,s],[e,n],[w,n],[w,s]]]);
  return {type:'Feature', geometry:{type:'MultiPolygon',coordinates}, properties:feature.properties};
};
```

Der Export schreibt nur ausgewählte Vektorobjekte und freigegebene Attribute. Keine Hintergrundkarten, Verbindungen oder vollständigen Quellenattribute. Fachliche und mengenbezogene Regeln stehen in `js/modules/export.js`; Browser- und Dateiprüfungen unter `scripts/validation/`.
