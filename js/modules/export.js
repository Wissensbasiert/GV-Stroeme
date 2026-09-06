  // Exports are snapshots of the active view. No source dataset is downloaded.
  const exportLibraries = new Map();
  let exportSnapshot = null;
  let enlargedChart = null;
  let enlargedSnapshot = null;
  const EXPORT_ROW_LIMIT = 2000;
  const EXPORT_FEATURE_LIMIT = 100;

  function exportText(node) {
    if (!node) return '';
    const copy = node.cloneNode(true);
    copy.querySelectorAll('svg, button, .info-tooltip-wrap, .map-tooltip-filter-hint').forEach(n => n.remove());
    return copy.textContent.replace(/\s+/g, ' ').trim();
  }
  function exportTableCell(cell) {
    const text = exportText(cell);
    // Only right-aligned, unscaled quantities become numbers. Codes stay text.
    if (cell.tagName === 'TD' && getComputedStyle(cell).textAlign === 'right' && !/^0\d/.test(text) && /^[+\-−]?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?$/.test(text)) return Number(text.replaceAll('.', '').replace(',', '.').replace('−', '-'));
    return text;
  }
  function exportChartTitle(canvas) {
    return exportText(canvas.closest('.card')?.querySelector('.card-title')) || canvas.id;
  }
  function cloneChartSetting(value) {
    if (Array.isArray(value)) return value.map(cloneChartSetting);
    if (value && Object.getPrototypeOf(value) === Object.prototype) return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, cloneChartSetting(v)]));
    return value;
  }
  function snapshotChart(chart) {
    const config = cloneChartSetting(chart.config._config);
    config.data.datasets.forEach((dataset, i) => { dataset.hidden = !chart.isDatasetVisible(i); });
    config.options = config.options || {};
    Object.assign(config.options, { responsive: true, maintainAspectRatio: false, animation: false });
    config.options.font = { ...(config.options.font || {}), size: 14 };
    Object.values(config.options.scales || {}).forEach(axis => { axis.ticks = { ...(axis.ticks || {}), font: { ...(axis.ticks?.font || {}), size: 14 } }; });
    config.options.plugins = config.options.plugins || {};
    if (config.options.plugins.legend?.labels) config.options.plugins.legend.labels.font = { ...(config.options.plugins.legend.labels.font || {}), size: 14 };
    config.options.plugins.tooltip = { ...(config.options.plugins.tooltip || {}), enabled: true, external: null };
    if (chart.canvas.closest('.card')?.querySelector('.chart-scroll-legend')) config.options.plugins.legend = { ...(config.options.plugins.legend || {}), display: true, position: 'bottom' };
    if (chart.canvas.closest('.card')?.querySelector('.chart-sticky-axis') && config.options.scales?.x) { config.options.scales.x.ticks.display = true; config.options.scales.x.title.display = true; }
    // Expanded horizontal charts need room for the complete commodity labels.
    if (config.options.indexAxis === 'y' && config.options.scales?.y) {
      delete config.options.scales.y.afterFit;
      config.options.scales.y.ticks = { ...(config.options.scales.y.ticks || {}), autoSkip: false, crossAlign: 'near', callback: function(value) {
        const words = String(this.getLabelForValue(value)).split(/\s+/); const lines = []; let line = '';
        for (const word of words) { if (line && (line + ' ' + word).length > 48) { lines.push(line); line = word; } else line = line ? line + ' ' + word : word; }
        if (line) lines.push(line); return lines;
      }};
    }
    // Custom legend callbacks may close over the small chart. Use this chart's defaults.
    if (config.options.plugins.legend) delete config.options.plugins.legend.onClick;
    const unit = chart.canvas.id.includes('Toll') ? '%' : chart.canvas.id.includes('Airfreight') ? (state.airfreightMetric === 'flights' ? 'Flüge' : 'Mio. t') : chart.data.datasets.some(d => d.label === 'Mio. t') ? 'Mio. t' : state.metric === 'tkm' ? 'Mrd. tkm' : 'Mio. t';
    return { unit, id: chart.canvas.id, title: exportChartTitle(chart.canvas), config, hiddenIndices: (chart.data.labels || []).map((_, i) => chart.getDataVisibility(i) ? -1 : i).filter(i => i >= 0) };
  }
  function createSnapshotChart(canvas, snapshot, responsive = true) {
    const config = cloneChartSetting(snapshot.config);
    config.options.responsive = responsive;
    config.options.devicePixelRatio = 1;
    const chart = new Chart(canvas, config);
    snapshot.hiddenIndices.forEach(i => chart.toggleDataVisibility(i));
    chart.update('none');
    return chart;
  }
  function captureExportSnapshot() {
    const pane = document.getElementById(state.activeTab);
    const ready = pane && pane.getAttribute('aria-busy') !== 'true' && pane.dataset.loadError !== 'true';
    const tabName = exportText(document.querySelector(`#mainNav [data-tab="${state.activeTab}"]`));
    const context = [...document.querySelectorAll('.analysis-summary-item')].filter(n => !n.hidden && n.style.display !== 'none').map(exportText).filter(Boolean).join(' · ');
    const sources = [...document.querySelectorAll('#modalLicenses .source-item')].map(n => [exportText(n), ...[...n.querySelectorAll('a[href]')].map(a => a.href)].join('\n'));
    const charts = ready ? [...pane.querySelectorAll('canvas')].filter(c => c.getClientRects().length).map(c => Chart.getChart(c)).filter(Boolean).map(snapshotChart) : [];
    const kpis = ready ? [...pane.querySelectorAll('.kpi-card')].filter(n => n.getClientRects().length).map(n => [exportText(n.querySelector('.kpi-title')), exportText(n.querySelector('.kpi-value')), exportText(n.querySelector('.kpi-sub'))]) : [];
    const tables = ready ? [...pane.querySelectorAll('table')].filter(n => n.getClientRects().length).map(table => ({ title: exportText(table.closest('.card')?.querySelector('.card-title')) || 'Tabelle', rows: [...table.querySelectorAll('tr')].filter(n => n.getClientRects().length).map(row => [...row.querySelectorAll('th,td')].map(exportTableCell)) })) : [];
    const notes = [...pane.querySelectorAll('.info-tooltip-box')].map(exportText);
    const key = state.activeTab.replace('tab-', '');
    const map = maps[key];
    const bounds = map?.getBounds();
    const bbox = bounds ? [Math.max(-180, bounds.getWest()), Math.max(-90, bounds.getSouth()), Math.min(180, bounds.getEast()), Math.min(90, bounds.getNorth())] : null;
    const candidates = [];
    const addLayer = layer => {
      if (!layer?.wbpExport || !map.hasLayer(layer)) return;
      if (layer.getBounds ? !bounds.intersects(layer.getBounds()) : !bounds.contains(layer.getLatLng())) return;
      let tooltip = layer.getTooltip?.()?.getContent();
      if (typeof tooltip === 'function') tooltip = tooltip(layer);
      const textNode = document.createElement('div');
      if (typeof tooltip === 'string') textNode.innerHTML = tooltip;
      candidates.push({ type: 'Feature', geometry: cloneChartSetting(layer.toGeoJSON().geometry), properties: { ...layer.wbpExport, information: exportText(textNode) } });
    };
    if (ready && bounds) {
      mapLayers[key]?.geojson?.eachLayer(addLayer);
      Object.values(mapLayers[key]?.portsLookup || {}).forEach(x => addLayer(x.marker));
      Object.values(mapLayers[key]?.airportsLookup || {}).forEach(addLayer);
    }
    if (key === 'toll') {
      notes.push(exportText(document.getElementById('tollComparisonNotice')));
      const current = tollMonthlyCache.get(`${state.tollMunicipality}|${state.tollMonth}|${state.tollDirection}`);
      if (current) notes.push(`Mautdaten abgerufen: ${current.fetchedAt}; Gemeinde ${current.municipality}; Monat ${current.month}; Richtung ${current.direction}.`);
      if (tollComparison.fetchedAt) notes.push(`Vorjahresdaten abgerufen: ${tollComparison.fetchedAt}; Monat ${tollComparison.month}.`);
    }
    const localExtent = bbox && map.distance([bbox[1], bbox[0]], [bbox[1], bbox[2]]) <= 250000 && map.distance([bbox[1], bbox[0]], [bbox[3], bbox[0]]) <= 250000;
    return { localExtent, ready, tabName, context, createdAt: new Date().toISOString(), sources, notes, charts, kpis, tables, bbox, candidates };
  }
  async function loadExportLibrary(url) {
    if (!exportLibraries.has(url)) exportLibraries.set(url, new Promise((resolve, reject) => {
      const script = document.createElement('script'); script.src = url;
      script.onload = resolve;
      script.onerror = () => { script.remove(); exportLibraries.delete(url); reject(new Error('Die Exportfunktion konnte nicht geladen werden. Bitte erneut versuchen.')); };
      document.head.append(script);
    }));
    return exportLibraries.get(url);
  }
  function downloadExport(blob, snapshot, extension, label = '') {
    const slug = `${snapshot.tabName}-${label}`.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9]+/g, '-').replace(/-+$/, '').slice(0, 90);
    const url = URL.createObjectURL(blob), anchor = document.createElement('a');
    anchor.href = url; anchor.download = `Gueterstroeme-${slug}-${snapshot.createdAt.slice(0, 10)}.${extension}`;
    document.body.append(anchor); anchor.click(); anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  }
  function canvasTextLines(ctx, text, width) {
    const lines = []; let line = '';
    for (const word of text.split(/\s+/)) {
      if (line && ctx.measureText(`${line} ${word}`).width > width) { lines.push(line); line = word; }
      else line = line ? `${line} ${word}` : word;
    }
    if (line) lines.push(line);
    return lines;
  }
  async function exportChartPng(chartSnapshot, snapshot) {
    if (!chartSnapshot) throw new Error('Für diese Auswahl ist kein Diagramm verfügbar.');
    const canvas = document.createElement('canvas'); canvas.width = 1680; const chartHeight = chartSnapshot.config.options?.indexAxis === 'y' ? Math.max(920, (chartSnapshot.config.data.labels?.length || 0) * 44 + 100) : 920; canvas.height = chartHeight;
    const chart = createSnapshotChart(canvas, chartSnapshot, false);
    try {
      const output = document.createElement('canvas'), ctx = output.getContext('2d');
      output.width = 1800;
      ctx.font = '24px Arial';
      const titleLines = canvasTextLines(ctx, chartSnapshot.title, 1680);
      ctx.font = '19px Arial';
      const contextLines = canvasTextLines(ctx, `${snapshot.tabName} · ${snapshot.context} · Diagrammwerte: ${chartSnapshot.unit}`, 1680);
      const sourceText = 'Wissensbasierte Planung · ' + sourceCredit(snapshot.tabName) + ' · Eigene Auswertung. Export: ' + snapshot.createdAt.slice(0, 10) + '. Quellen und Nutzungsbedingungen: Menü Quellen.';
      const sourceLines = canvasTextLines(ctx, sourceText, 1680);
      const chartTop = 48 + titleLines.length * 32 + contextLines.length * 26;
      output.height = chartTop + chartHeight + sourceLines.length * 25 + 72;
      ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, output.width, output.height);
      ctx.fillStyle = '#0f172a'; ctx.font = 'bold 24px Arial'; let y = 42;
      titleLines.forEach(line => { ctx.fillText(line, 60, y); y += 32; });
      ctx.fillStyle = '#475569'; ctx.font = '19px Arial';
      contextLines.forEach(line => { ctx.fillText(line, 60, y); y += 26; });
      ctx.drawImage(canvas, 60, chartTop);
      y = chartTop + chartHeight + 38;
      sourceLines.forEach(line => { ctx.fillText(line, 60, y); y += 25; });
      const blob = await new Promise(resolve => output.toBlob(resolve, 'image/png'));
      if (!blob) throw new Error('Das PNG konnte nicht erstellt werden.');
      downloadExport(blob, snapshot, 'png', chartSnapshot.title);
    } finally { chart.destroy(); }
  }
  function sourceCredit(name) {
    if (/Maut/i.test(name)) return 'BALM / Toll Collect GmbH; © BKG 2025, dl-de/by-2-0';
    if (/Prognose/i.test(name)) return 'BMV (Hrsg.), Verkehrsprognose 2040, Teil 2, VB970423; Bereitstellung BASt / Mobilithek';
    if (/Luft/i.test(name)) return 'Eurostat: AVIA_GOOC / AVIA_GOOA / AVIA_GOR_DE';
    if (/Straße/i.test(name)) return 'Kraftfahrt-Bundesamt (KBA), dl-de/by-2-0';
    if (/Überblick|Übersicht/i.test(name)) return 'KBA und Destatis, dl-de/by-2-0';
    return 'Statistisches Bundesamt (Destatis), dl-de/by-2-0';
  }
  async function exportExcelSnapshot(snapshot) {
    await loadExportLibrary('assets/vendor/exceljs/exceljs.min.js');
    const workbook = new ExcelJS.Workbook();
    workbook.creator = 'Wissensbasierte Planung'; workbook.created = new Date(snapshot.createdAt);
    let rowCount = 0;
    const addSheet = (name, rows, data = false) => {
      if (data) { rowCount += Math.max(0, rows.length - 1); if (rowCount > EXPORT_ROW_LIMIT) throw new Error('Die Auswahl überschreitet 2.000 Datenzeilen. Bitte grenzen Sie die Auswertung ein.'); }
      const sheet = workbook.addWorksheet(name.slice(0, 31));
      rows.forEach(row => sheet.addRow(row.map(value => typeof value === 'number' ? (Number.isFinite(value) ? value : null) : value == null ? null : String(value))));
      sheet.getRow(1).font = { bold: true, color: { argb: 'FFFFFFFF' } };
      sheet.getRow(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF17613C' } };
      sheet.views = [{ state: 'frozen', ySplit: 1 }];
      sheet.columns.forEach((column, i) => { column.width = i === 0 ? 42 : 30; column.alignment = { vertical: 'top', wrapText: true }; });
      return sheet;
    };
    addSheet('Auswahl und Quellen', [ ['Merkmal', 'Angabe'], ['Modul', snapshot.tabName], ['Auswahl', snapshot.context], ['Exportzeit (UTC)', snapshot.createdAt], ['Bearbeitungsstand Tool', 'September 2026'], ['Umfang', 'Sichtbare Kennzahlen, Tabellenzeilen und Diagrammwerte; keine vollständigen Ausgangsdaten. Tabellen und Kennzahlen enthalten ihre angezeigte Rundung. Diagrammwerte sind numerisch; Einheit jeweils laut Achse bzw. Diagrammtitel.'], ['Nachnutzung', 'Originalquellen und Nutzungsbedingungen beachten; eigene Aufbereitung durch Wissensbasierte Planung.'], ...snapshot.notes.filter(Boolean).map(n => ['Fachlicher Hinweis', n]), ...snapshot.sources.map(s => ['Quelle und Lizenz', s]) ]);
    addSheet('Kennzahlen', [['Kennzahl', 'Wert wie angezeigt', 'Einheit / Einordnung'], ...snapshot.kpis], true);
    snapshot.tables.forEach((table, i) => addSheet(`Tabelle ${i + 1}`, [['Darstellung', table.title], ...table.rows], true));
    snapshot.charts.forEach((chart, index) => {
      const axes = Object.entries(chart.config.options?.scales || {}).map(([key, axis]) => `${key}: ${axis.title?.text || 'Einheit laut Diagrammtitel'}`).join('; ');
      const datasets = chart.config.data.datasets;
      const labels = chart.config.data.labels || [];
      const rows = [['Diagramm', chart.title], ['Einheit der Diagrammwerte', chart.unit], ['Achsen', axes || chart.title], ['Kategorie', ...datasets.filter(d => !d.hidden).map(d => Array.isArray(d.label) ? d.label.join(' ') : d.label || 'Wert')]];
      labels.forEach((label, i) => {
        if (chart.hiddenIndices.includes(i)) return;
        rows.push([Array.isArray(label) ? label.join(' ') : label, ...datasets.filter(d => !d.hidden).map(d => { const v = d.data[i]; return v && typeof v === 'object' ? JSON.stringify(v) : v; })]);
      });
      addSheet(`Diagramm ${index + 1}`, rows, true);
    });
    downloadExport(new Blob([await workbook.xlsx.writeBuffer()], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), snapshot, 'xlsx');
  }

  // GeoPackage 1.3: WGS84, a bounded vector subset, no basemap or raw properties.
  function encodeGpkgGeometry(geometry) {
    const bytes = [];
    const u32 = n => { const b = new Uint8Array(4); new DataView(b.buffer).setUint32(0, n, true); bytes.push(...b); };
    const number = n => { const b = new Uint8Array(8); new DataView(b.buffer).setFloat64(0, n, true); bytes.push(...b); };
    const point = coordinates => { number(coordinates[0]); number(coordinates[1]); };
    const line = coordinates => { u32(coordinates.length); coordinates.forEach(point); };
    const write = g => {
      const types = { Point: 1, LineString: 2, Polygon: 3, MultiPoint: 4, MultiLineString: 5, MultiPolygon: 6 };
      if (!types[g.type]) throw new Error('Diese Geometrie wird nicht unterstützt.');
      bytes.push(1); u32(types[g.type]);
      if (g.type === 'Point') point(g.coordinates);
      else if (g.type === 'LineString') line(g.coordinates);
      else if (g.type === 'Polygon') { u32(g.coordinates.length); g.coordinates.forEach(line); }
      else { u32(g.coordinates.length); g.coordinates.forEach(c => write({ type: g.type.replace('Multi', ''), coordinates: c })); }
    };
    bytes.push(71, 80, 0, 1); u32(4326); write(geometry); return new Uint8Array(bytes);
  }
  async function exportGeoSnapshot(snapshot) {
    if (!snapshot.localExtent || !snapshot.candidates.length || snapshot.candidates.length > EXPORT_FEATURE_LIMIT) throw new Error('Bitte zoomen Sie auf einen Ausschnitt mit 1 bis 100 Gebieten oder Standorten.');
    await Promise.all([loadExportLibrary('assets/vendor/sqljs/sql-wasm.js'), loadExportLibrary('assets/vendor/polygon-clip.js')]);
    const SQL = await initSqlJs({ locateFile: file => `assets/vendor/sqljs/${file}` });
    const features = snapshot.candidates.map(feature => feature.geometry.type === 'Point' ? feature : { ...wbpClipPolygon(feature, snapshot.bbox), properties: feature.properties }).filter(f => f.geometry.coordinates.length);
    if (!features.length) throw new Error('Im Ausschnitt liegen keine exportierbaren Geometrien.');
    const db = new SQL.Database();
    try {
      db.run(`PRAGMA application_id = 1196444487; PRAGMA user_version = 10300;
        CREATE TABLE gpkg_spatial_ref_sys (srs_name TEXT NOT NULL,srs_id INTEGER NOT NULL PRIMARY KEY,organization TEXT NOT NULL,organization_coordsys_id INTEGER NOT NULL,definition TEXT NOT NULL,description TEXT);
        CREATE TABLE gpkg_contents (table_name TEXT NOT NULL PRIMARY KEY,data_type TEXT NOT NULL,identifier TEXT UNIQUE,description TEXT DEFAULT '',last_change DATETIME NOT NULL,min_x DOUBLE,min_y DOUBLE,max_x DOUBLE,max_y DOUBLE,srs_id INTEGER,FOREIGN KEY(srs_id) REFERENCES gpkg_spatial_ref_sys(srs_id));
        CREATE TABLE gpkg_geometry_columns (table_name TEXT NOT NULL,column_name TEXT NOT NULL,geometry_type_name TEXT NOT NULL,srs_id INTEGER NOT NULL,z TINYINT NOT NULL,m TINYINT NOT NULL,PRIMARY KEY(table_name,column_name),FOREIGN KEY(table_name) REFERENCES gpkg_contents(table_name),FOREIGN KEY(srs_id) REFERENCES gpkg_spatial_ref_sys(srs_id));
        CREATE TABLE kartenausschnitt (fid INTEGER PRIMARY KEY AUTOINCREMENT,geom BLOB NOT NULL,code TEXT,name TEXT,wert REAL,einheit TEXT,information TEXT);
        CREATE TABLE auswahl (id INTEGER PRIMARY KEY AUTOINCREMENT,merkmal TEXT,angabe TEXT);`);
      const wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]';
      for (const row of [['Undefined Cartesian SRS',-1,'NONE',-1,'undefined','Undefined Cartesian coordinate reference system'],['Undefined geographic SRS',0,'NONE',0,'undefined','Undefined geographic coordinate reference system'],['WGS 84',4326,'EPSG',4326,wkt,'Longitude, latitude']]) db.run('INSERT INTO gpkg_spatial_ref_sys VALUES (?,?,?,?,?,?)',row);
      const extent = [Infinity, Infinity, -Infinity, -Infinity];
      const visit = coords => { if (typeof coords[0] === 'number') { extent[0]=Math.min(extent[0],coords[0]);extent[1]=Math.min(extent[1],coords[1]);extent[2]=Math.max(extent[2],coords[0]);extent[3]=Math.max(extent[3],coords[1]); } else coords.forEach(visit); };
      for (const feature of features) {
        visit(feature.geometry.coordinates);
        const p = feature.properties;
        db.run('INSERT INTO kartenausschnitt (geom,code,name,wert,einheit,information) VALUES (?,?,?,?,?,?)', [encodeGpkgGeometry(feature.geometry),String(p.code || ''),String(p.name || ''),Number.isFinite(p.value) ? p.value : null,String(p.unit || ''),p.information || '']);
      }
      const note = 'Geometrien am sichtbaren Kartenausschnitt geschnitten. Kennwerte gelten für vollständige Gebiete oder Standorte; keine anteilige Flächenberechnung. Keine Verbindungen oder Hintergrundkarten enthalten.';
      db.run('INSERT INTO gpkg_contents VALUES (?,?,?,?,?,?,?,?,?,?)',['kartenausschnitt','features','Kartenausschnitt',note,snapshot.createdAt,...extent,4326]);
      db.run('INSERT INTO gpkg_contents (table_name,data_type,identifier,description,last_change) VALUES (?,?,?,?,?)',['auswahl','attributes','Auswahl und Quellen','Filter und Quellenangaben',snapshot.createdAt]);
      db.run("INSERT INTO gpkg_geometry_columns VALUES ('kartenausschnitt','geom','GEOMETRY',4326,0,0)");
      for (const row of [['Modul',snapshot.tabName],['Auswahl',snapshot.context],['Exportzeit (UTC)',snapshot.createdAt],['Kartenausschnitt WGS84',JSON.stringify(snapshot.bbox)],['Umfang',note],['Konzeption und Aufbereitung','Wissensbasierte Planung; Bearbeitungsstand September 2026'],...snapshot.notes.map(n=>['Hinweis',n]),...snapshot.sources.map(s=>['Quelle und Lizenz',s])]) db.run('INSERT INTO auswahl (merkmal,angabe) VALUES (?,?)',row);
      downloadExport(new Blob([db.export()], { type: 'application/geopackage+sqlite3' }), snapshot, 'gpkg');
    } finally { db.close(); }
  }
  async function runExport(button, statusId, work) {
    const status = document.getElementById(statusId);
    button.disabled = true; status.textContent = 'Download wird vorbereitet …';
    try { await work(); status.textContent = 'Datei wurde zum Download bereitgestellt.'; }
    catch (error) { status.textContent = error.message || 'Der Export ist fehlgeschlagen. Bitte erneut versuchen.'; console.error('Export failed:', error); }
    finally { button.disabled = false; }
  }
  function setupExportActions() {
    const expandHint = document.createElement('div');
    expandHint.id = 'chartExpandHint';
    expandHint.className = 'chart-expand-hint';
    expandHint.setAttribute('role', 'tooltip');
    expandHint.textContent = 'Diagramm vergrößern';
    expandHint.hidden = true;
    document.body.append(expandHint);
    const hideExpandHint = () => { expandHint.hidden = true; };
    window.addEventListener('resize', hideExpandHint);
    document.addEventListener('scroll', hideExpandHint, true);
    document.addEventListener('keydown', event => { if (event.key === 'Escape') hideExpandHint(); });
    document.querySelectorAll('.tab-pane canvas').forEach(canvas => {
      const button = document.createElement('button');
      button.id = `enlarge-${canvas.id}`; button.type = 'button'; button.className = 'btn-chart-enlarge'; button.setAttribute('aria-label', 'Diagramm vergrößern'); button.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 3H3v5m0-5 6 6m7-6h5v5m0-5-6 6M3 16v5h5m-5 0 6-6m12 1v5h-5m5 0-6-6"/></svg>'; button.disabled = true;
      const header = canvas.closest('.card').querySelector('.card-header');
      let actions = header.querySelector('.card-actions');
      if (!actions) { actions = document.createElement('div'); actions.className = 'card-actions'; header.append(actions); }
      actions.append(button);
      button.setAttribute('aria-describedby', expandHint.id);
      const showExpandHint = () => {
        if (button.disabled) return;
        const rect = button.getBoundingClientRect();
        expandHint.hidden = false;
        expandHint.style.left = `${Math.max(8, Math.min(rect.right - expandHint.offsetWidth, innerWidth - expandHint.offsetWidth - 8))}px`;
        expandHint.style.top = `${rect.bottom + 8}px`;
      };
      button.addEventListener('mouseenter', showExpandHint);
      button.addEventListener('focus', showExpandHint);
      button.addEventListener('mouseleave', hideExpandHint);
      button.addEventListener('blur', hideExpandHint);
      button.addEventListener('click', hideExpandHint);
      bindDialog(button.id, 'modalChartLarge', () => {
        const source = Chart.getChart(canvas); if (!source) return;
        document.querySelectorAll('.chart-hover-tooltip.is-visible, .chart-axis-label-tooltip.is-visible').forEach(node => node.classList.remove('is-visible'));
        enlargedSnapshot = captureExportSnapshot(); const chartSnapshot = snapshotChart(source);
        enlargedSnapshot.charts = [chartSnapshot];
        document.getElementById('largeChartTitle').textContent = chartSnapshot.title;
        document.getElementById('largeChartContext').textContent = `${enlargedSnapshot.tabName} · ${enlargedSnapshot.context} · Diagrammwerte: ${chartSnapshot.unit}`;
        document.getElementById('largeChartStatus').textContent = '';
        document.querySelector('.large-chart-canvas').style.height = chartSnapshot.config.options?.indexAxis === 'y' && chartSnapshot.config.data.labels.length >= 12 ? `${chartSnapshot.config.data.labels.length * 40 + 110}px` : 'clamp(320px, 60vh, 720px)';
        enlargedChart?.destroy();
        enlargedChart = createSnapshotChart(document.getElementById('largeChartCanvas'), chartSnapshot);
      });
    });
    Chart.register({ id: 'wbpExportActions', afterUpdate(chart) { const button = document.getElementById(`enlarge-${chart.canvas.id}`); if (button) button.disabled = !chart.data.datasets?.length; }, beforeDestroy(chart) { const button = document.getElementById(`enlarge-${chart.canvas.id}`); if (button) button.disabled = true; } });
    bindDialog('btnExportModal', 'modalExport', () => {
      exportSnapshot = captureExportSnapshot();
      document.getElementById('exportContext').textContent = `${exportSnapshot.tabName} · ${exportSnapshot.context}`;
      document.getElementById('exportStatus').textContent = exportSnapshot.ready ? '' : 'Die Auswertung wird noch geladen oder ist nicht verfügbar. Bitte schließen und nach dem Laden erneut öffnen.';
      const select = document.getElementById('exportChartSelect'); select.replaceChildren();
      exportSnapshot.charts.forEach((chart, i) => { const option = document.createElement('option'); option.value = String(i); option.textContent = chart.title; select.append(option); });
      if (!exportSnapshot.charts.length) { const option = document.createElement('option'); option.textContent = 'Kein Diagramm in dieser Auswahl verfügbar'; select.append(option); }
      document.getElementById('exportPng').disabled = !exportSnapshot.charts.length;
      document.getElementById('exportExcel').disabled = !exportSnapshot.ready || !(exportSnapshot.kpis.length || exportSnapshot.charts.length || exportSnapshot.tables.length);
      const count = exportSnapshot.candidates.length;
      document.getElementById('exportGeo').disabled = !exportSnapshot.ready || !exportSnapshot.localExtent || !count || count > EXPORT_FEATURE_LIMIT;
      document.getElementById('exportGeoScope').textContent = !exportSnapshot.localExtent ? 'Bitte schließen und näher in die Karte zoomen: Der Ausschnitt darf höchstens 250 km breit und 250 km hoch sein.' : count > EXPORT_FEATURE_LIMIT ? `${count} Objekte im Ausschnitt. Bitte schließen und näher in die Karte zoomen (höchstens 100).` : count ? `Bis zu ${count} Gebiete / Standorte im aktuellen Ausschnitt.` : 'Keine exportierbaren Gebiete oder Standorte in diesem Ausschnitt.';
    });
    document.getElementById('exportPng').addEventListener('click', event => { const snapshot = exportSnapshot, chart = snapshot.charts[Number(document.getElementById('exportChartSelect').value)]; runExport(event.currentTarget, 'exportStatus', () => exportChartPng(chart, snapshot)); });
    document.getElementById('exportExcel').addEventListener('click', event => { const snapshot = exportSnapshot; runExport(event.currentTarget, 'exportStatus', () => exportExcelSnapshot(snapshot)); });
    document.getElementById('exportGeo').addEventListener('click', event => { const snapshot = exportSnapshot; runExport(event.currentTarget, 'exportStatus', () => exportGeoSnapshot(snapshot)); });
    document.getElementById('largeChartPng').addEventListener('click', event => { const snapshot = enlargedSnapshot; const chart = snapshotChart(enlargedChart); chart.title = snapshot.charts[0].title; chart.unit = snapshot.charts[0].unit; runExport(event.currentTarget, 'largeChartStatus', () => exportChartPng(chart, snapshot)); });
  }

