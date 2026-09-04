  // ============================================================
  // LUFTFRACHT & FLUGHÄFEN
  // ============================================================
  let chartAirfreightAirports = null;
  const AIRFREIGHT_COLOR = '#0ea5e9';
  const AIRFREIGHT_TREND_COLORS = ['#0ea5e9', '#2563eb', '#0f766e', '#7c3aed', '#d97706', '#4c7f83'];

  function setAirfreightHtml(id, html) {
    const element = document.getElementById(id);
    if (element) element.innerHTML = html;
  }

  function getAirfreightDirection() {
    return ['outbound', 'inbound', 'balance'].includes(state.direction) ? state.direction : 'all';
  }

  function getAirfreightMetric() {
    return state.airfreightMetric === 'flights' ? 'flights' : 'tonnes';
  }

  function getAirfreightMetricLabel(metric = getAirfreightMetric()) {
    return metric === 'flights' ? 'Reine Fracht- und Postflüge' : 'Fracht und Post';
  }

  function getAirfreightDirectionLabel(direction = getAirfreightDirection(), compact = false) {
    if (direction === 'outbound') return compact ? 'Versand (geladen)' : 'Versand · am ausgewählten Flughafen geladen';
    if (direction === 'inbound') return compact ? 'Empfang (entladen)' : 'Empfang · am ausgewählten Flughafen entladen';
    if (direction === 'balance') return compact ? 'Saldo (geladen − entladen)' : 'Saldo · am ausgewählten Flughafen geladen minus entladen';
    return compact ? 'Gesamt (geladen und entladen)' : 'Gesamt · geladen und entladen';
  }

  function getAirfreightValue(record, metric = getAirfreightMetric(), direction = getAirfreightDirection()) {
    const values = record?.[metric];
    if (!values) return null;
    if (direction === 'balance') {
      const hasOutbound = values.outbound !== null && values.outbound !== undefined;
      const hasInbound = values.inbound !== null && values.inbound !== undefined;
      if (!hasOutbound && !hasInbound) return null;
      return Number(values.outbound || 0) - Number(values.inbound || 0);
    }
    const value = values[direction];
    return value === null || value === undefined ? null : Number(value);
  }

  function formatAirfreightValue(value, metric = getAirfreightMetric(), withUnit = true, direction = getAirfreightDirection()) {
    if (value === null || value === undefined || !Number.isFinite(Number(value))) return '--';
    const numeric = Number(value);
    const sign = direction === 'balance' && numeric > 0 ? '+' : '';
    if (metric === 'flights') {
      const formatted = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 }).format(numeric);
      return withUnit ? `${sign}${formatted} Flüge` : `${sign}${formatted}`;
    }
    const absolute = Math.abs(numeric);
    if (absolute >= 1e6) return `${sign}${formatDeNum(numeric / 1e6, 2)}${withUnit ? ' Mio. t' : ''}`;
    if (absolute >= 1e3) return `${sign}${formatDeNum(numeric / 1e3, 1)}${withUnit ? ' Tsd. t' : ''}`;
    return `${sign}${formatDeNum(numeric, absolute < 10 ? 1 : 0)}${withUnit ? ' t' : ''}`;
  }

  function formatAirfreightDelta(value) {
    if (value === null || value === undefined || !Number.isFinite(Number(value))) {
      return '<span style="color:#94a3b8;">--</span>';
    }
    const numeric = Number(value);
    return `<span style="color:${numeric >= 0 ? '#16a34a' : '#dc2626'}; font-weight:700;">${numeric >= 0 ? '↗ +' : '↘ '}${formatDeNum(numeric, 1)} %</span>`;
  }

  function getAirfreightPercentChange(current, reference) {
    const currentValue = Number(current);
    const referenceValue = Number(reference);
    return Number.isFinite(currentValue) && Number.isFinite(referenceValue) && referenceValue > 0
      ? ((currentValue - referenceValue) / referenceValue) * 100
      : null;
  }

  function getAirfreightCountryName(code) {
    if (!code) return '--';
    try {
      return new Intl.DisplayNames(['de'], { type: 'region' }).of(code) || code;
    } catch (_error) {
      return code;
    }
  }

  function bindAirfreightTableTooltip(target, text) {
    if (!target || !text) return;
    let tooltip = document.getElementById('airfreightTableHoverTooltip');
    if (!tooltip) {
      tooltip = document.createElement('div');
      tooltip.id = 'airfreightTableHoverTooltip';
      tooltip.className = 'table-hover-tooltip';
      tooltip.hidden = true;
      tooltip.setAttribute('role', 'tooltip');
      document.body.appendChild(tooltip);
    }
    const show = () => {
      tooltip.textContent = text;
      tooltip.hidden = false;
      tooltip.style.visibility = 'hidden';
      const rect = target.getBoundingClientRect();
      const tipRect = tooltip.getBoundingClientRect();
      const gap = 8;
      const left = Math.min(window.innerWidth - tipRect.width - 12, Math.max(12, rect.left));
      let top = rect.top - tipRect.height - gap;
      if (top < 12) top = rect.bottom + gap;
      tooltip.style.left = `${left}px`;
      tooltip.style.top = `${top}px`;
      tooltip.style.visibility = 'visible';
    };
    const hide = () => { tooltip.hidden = true; };
    target.addEventListener('mouseenter', show);
    target.addEventListener('mouseleave', hide);
    target.addEventListener('focus', show);
    target.addEventListener('blur', hide);
  }

  function scheduleAirfreightHighlightClear() {
    window.setTimeout(() => {
      const mapHovered = document.querySelector('#airfreightLeafletMap .flow-relation-target:hover');
      const rowHovered = document.querySelector('#tableAirfreightRelationsBody tr[data-partner-id]:hover');
      if (mapHovered || rowHovered) return;
      closeActiveRelationTooltip('airfreight');
      clearAllHighlights('airfreight');
    }, 60);
  }

  function getAirfreightAirportEntries(year = state.year, metric = getAirfreightMetric(), direction = getAirfreightDirection()) {
    return Object.values(airfreightData?.airportValues?.[year] || {})
      .map(record => ({
        ...record,
        meta: airfreightData?.airports?.[record.code] || {},
        value: getAirfreightValue(record, metric, direction)
      }))
      .filter(record => record.value !== null)
      .sort((a, b) => {
        const difference = getAirfreightDirection() === 'balance'
          ? Math.abs(b.value) - Math.abs(a.value)
          : b.value - a.value;
        return difference || String(a.meta.name || a.code).localeCompare(String(b.meta.name || b.code), 'de');
      });
  }

  function isAirfreightAirportMetricYearAvailable(year = state.year, metric = getAirfreightMetric()) {
    const years = metric === 'flights'
      ? airfreightData?.metadata?.availableAirportFlightYears
      : airfreightData?.metadata?.availableAirportYears;
    return Array.isArray(years) && years.map(String).includes(String(year));
  }

  function ensureAirfreightAirportSelection(entries) {
    if (state.selectedAirport && !entries.some(record => record.code === state.selectedAirport)) {
      state.selectedAirport = null;
    }
  }

  function updateAirfreightAirportSelect(entries) {
    const select = document.getElementById('selectAirfreightAirport');
    if (!select) return;
    const options = entries.map(record => {
      const name = record.meta.name || record.code;
      return `<option value="${record.code}">${name} (${record.code})</option>`;
    }).join('');
    select.innerHTML = `<option value="">Alle Flughäfen</option>${options}`;
    select.value = state.selectedAirport || '';
  }

  function getAirfreightRelations() {
    if (!state.selectedAirport) return [];
    const metric = getAirfreightMetric();
    const direction = getAirfreightDirection();
    const relationSet = airfreightData?.relations?.[state.year]?.[state.selectedAirport]?.[metric] || {};
    if (direction !== 'balance') return relationSet[direction] || [];

    const byPartner = new Map();
    const merge = (records, factor) => (records || []).forEach(record => {
      const current = byPartner.get(record.partner) || { partner: record.partner, value: 0, previous_value: 0, baseline_value: 0, hasPrevious: false, hasBaseline: false };
      current.value += factor * Number(record.value || 0);
      if (record.previous_value !== null && record.previous_value !== undefined) {
        current.previous_value += factor * Number(record.previous_value || 0);
        current.hasPrevious = true;
      }
      if (record.baseline_value !== null && record.baseline_value !== undefined) {
        current.baseline_value += factor * Number(record.baseline_value || 0);
        current.hasBaseline = true;
      }
      byPartner.set(record.partner, current);
    });
    merge(relationSet.outbound, 1);
    merge(relationSet.inbound, -1);
    return [...byPartner.values()]
      .map(record => ({ ...record, previous_value: record.hasPrevious ? record.previous_value : null, baseline_value: record.hasBaseline ? record.baseline_value : null }))
      .filter(record => record.value !== 0)
      .sort((a, b) => Math.abs(b.value) - Math.abs(a.value) || String(a.partner).localeCompare(String(b.partner), 'de'));
  }

  function niceAirfreightBoundary(value) {
    if (!Number.isFinite(value) || value <= 0) return 1;
    const magnitude = 10 ** Math.floor(Math.log10(value));
    const normalized = value / magnitude;
    const nice = normalized < 1.5 ? 1 : normalized < 3.5 ? 2 : normalized < 7.5 ? 5 : 10;
    return nice * magnitude;
  }

  function formatAirfreightBoundary(value, metric) {
    if (metric === 'flights') return `${formatDeNum(value, 0)} Flüge`;
    if (value >= 1e6) return `${formatDeNum(value / 1e6, value % 1e6 === 0 ? 0 : 1)} Mio. t`;
    if (value >= 1e3) return `${formatDeNum(value / 1e3, value % 1e3 === 0 ? 0 : 1)} Tsd. t`;
    return `${formatDeNum(value, 0)} t`;
  }

  function getAirfreightClassification(values, metric = getAirfreightMetric()) {
    const positive = values.map(value => Math.abs(Number(value))).filter(value => Number.isFinite(value) && value > 0);
    const maximum = positive.length ? Math.max(...positive) : 1;
    let first = niceAirfreightBoundary(maximum * 0.25);
    let second = niceAirfreightBoundary(maximum * 0.60);
    if (second <= first) second = niceAirfreightBoundary(first * 2.1);
    if (second >= maximum && maximum > first) second = niceAirfreightBoundary(maximum * 0.55);
    if (second <= first) second = first * 2;
    const labels = [
      `< ${formatAirfreightBoundary(first, metric)}`,
      `${formatAirfreightBoundary(first, metric)} – ${formatAirfreightBoundary(second, metric)}`,
      `> ${formatAirfreightBoundary(second, metric)}`
    ];
    const getClass = value => {
      const numeric = Math.abs(Number(value) || 0);
      if (numeric < first) return 0;
      if (numeric <= second) return 1;
      return 2;
    };
    return {
      first,
      second,
      labels,
      getRadius: value => [6.5, 11, 16.5][getClass(value)],
      getWeight: value => [2.2, 4.8, 8][getClass(value)]
    };
  }

  function updateAirfreightLegend(entries, relations) {
    const metric = getAirfreightMetric();
    const airportClasses = getAirfreightClassification(entries.map(record => record.value), metric);
    const isBalance = getAirfreightDirection() === 'balance';
    setText('airfreightLegendTitle', isBalance ? `${getAirfreightMetricLabel(metric)} · Saldo` : getAirfreightMetricLabel(metric));
    setText('airfreightAirportLegendSubtitle', isBalance
      ? 'Absoluter Saldo an Flughäfen'
      : (metric === 'flights' ? 'Flugaufkommen der Flughäfen' : 'Frachtaufkommen der Flughäfen'));
    setText('airfreightAirportLegendLow', airportClasses.labels[0]);
    setText('airfreightAirportLegendMedium', airportClasses.labels[1]);
    setText('airfreightAirportLegendHigh', airportClasses.labels[2]);

    const visibleRelations = state.selectedAirport ? relations.slice(0, state.topX) : [];
    const relationSection = document.getElementById('airfreightRelationLegendSection');
    if (relationSection) relationSection.hidden = visibleRelations.length === 0;
    setText('airfreightRelationLegendSubtitle', isBalance ? 'Absoluter Saldo der Top-Relationen' : 'Top-Relationen');
    if (visibleRelations.length) {
      const relationClasses = getAirfreightClassification(visibleRelations.map(record => record.value), metric);
      setText('airfreightRelationLegendLow', relationClasses.labels[0]);
      setText('airfreightRelationLegendMedium', relationClasses.labels[1]);
      setText('airfreightRelationLegendHigh', relationClasses.labels[2]);
    }
    return { airportClasses, relationClasses: getAirfreightClassification(visibleRelations.map(record => record.value), metric) };
  }

  function setAirfreightRelationStatus(message = '', showYearAction = false) {
    const status = document.getElementById('airfreightRelationStatus');
    if (!status) return;
    status.hidden = !message;
    status.innerHTML = message;
    if (showYearAction) {
      status.querySelector('button')?.addEventListener('click', () => {
        const year = String(airfreightData.metadata.latestRelationYear);
        state.year = year;
        const yearSelect = document.getElementById('selectYear');
        if (yearSelect) yearSelect.value = year;
        renderAll();
        updateAnalysisSummary();
      }, { once: true });
    }
  }

  function renderAirfreightKpis(entries) {
    const metric = getAirfreightMetric();
    const direction = getAirfreightDirection();
    const current = getAirfreightValue(airfreightData?.national?.[state.year], metric, direction);
    const previousYear = String(Number(state.year) - 1);
    const previous = getAirfreightValue(airfreightData?.national?.[previousYear], metric, direction);
    const directionLabel = getAirfreightDirectionLabel(direction, true);
    const metricLabel = metric === 'flights' ? 'Reine Luftfracht- und Luftpostflüge in Deutschland' : 'Luftfracht- und Luftpostaufkommen in Deutschland';
    setText('airfreightNationalTitle', metricLabel);
    setText('airfreightNationalValue', formatAirfreightValue(current, metric));
    setText('airfreightNationalSub', directionLabel);

    const isBalance = direction === 'balance';
    setText('airfreightYoYTitle', isBalance ? `Saldo ${previousYear}` : 'Veränderung zum Vorjahr');
    if (isBalance) {
      setText('airfreightYoYValue', formatAirfreightValue(previous, metric, true, 'balance'));
      setText('airfreightYoYSub', previous === null ? `Kein Vergleichswert für ${previousYear}` : 'Historischer Saldo; keine Prozentveränderung');
    } else {
      const change = current !== null && previous > 0 ? ((current - previous) / previous) * 100 : null;
      setAirfreightHtml('airfreightYoYValue', change === null
        ? '--'
        : `<span style="color:${change >= 0 ? '#16a34a' : '#dc2626'};">${change >= 0 ? '+' : ''}${formatDeNum(change, 1)} %</span>`);
      setText('airfreightYoYSub', previous === null ? `Kein Vergleichswert für ${previousYear}` : `gegenüber ${previousYear}`);
    }

    setText('airfreightAirportCountTitle', metric === 'flights'
      ? 'Deutsche Flughäfen mit ausgewiesener Zahl reiner Fracht- und Postflüge'
      : 'Deutsche Flughäfen mit ausgewiesenem Frachtaufkommen');
    const airportMetricAvailable = isAirfreightAirportMetricYearAvailable();
    setText('airfreightAirportCount', airportMetricAvailable ? String(entries.length) : '--');
    setText('airfreightAirportCountSub', airportMetricAvailable ? 'Einschließlich veröffentlichter Nullwerte' : 'Flughafenwerte derzeit nicht belastbar');

    const total = entries.reduce((sum, record) => sum + (direction === 'balance' ? Math.abs(record.value || 0) : Math.max(0, record.value || 0)), 0);
    const topThree = entries.slice(0, 3).reduce((sum, record) => sum + (direction === 'balance' ? Math.abs(record.value || 0) : Math.max(0, record.value || 0)), 0);
    setText('airfreightTop3Share', total > 0 ? `${formatDeNum((topThree / total) * 100, 1)} %` : '--');
    setText('airfreightTop3Sub', airportMetricAvailable
      ? (direction === 'balance' ? 'Anteil an der Summe absoluter Salden' : 'Anteil an der Summe der Flughafenwerte')
      : 'Flughafenwerte derzeit nicht belastbar');
  }

  function renderAirfreightMap(entries, relations) {
    const map = maps.airfreight;
    if (!map) return;
    if (mapLayers.airfreight.airportsGroup) map.removeLayer(mapLayers.airfreight.airportsGroup);
    mapLayers.airfreight.airportsGroup = L.layerGroup().addTo(map);
    mapLayers.airfreight.airportsLookup = {};
    mapLayers.airfreight.spiderLookup = {};

    const metric = getAirfreightMetric();
    const directionLabel = getAirfreightDirectionLabel();
    const direction = getAirfreightDirection();
    const { airportClasses, relationClasses } = updateAirfreightLegend(entries, relations);
    entries.forEach(record => {
      const { lat, lng, name } = record.meta;
      if (!Number.isFinite(Number(lat)) || !Number.isFinite(Number(lng))) return;
      const selected = record.code === state.selectedAirport;
      const radius = airportClasses.getRadius(record.value);
      const marker = L.circleMarker([lat, lng], {
        pane: 'selectionPane',
        className: 'airfreight-airport-marker',
        radius: selected ? radius + 2.5 : radius,
        fillColor: AIRFREIGHT_COLOR,
        fillOpacity: selected ? 1 : (state.selectedAirport ? 0.62 : 0.86),
        color: selected ? '#0f172a' : '#ffffff',
        weight: selected ? 3.5 : 1.7
      }).addTo(mapLayers.airfreight.airportsGroup);
      const previousRecord = airfreightData?.airportValues?.[String(Number(state.year) - 1)]?.[record.code];
      const baselineRecord = airfreightData?.airportValues?.['2016']?.[record.code];
      const previousValue = getAirfreightValue(previousRecord, metric, getAirfreightDirection());
      const baselineValue = getAirfreightValue(baselineRecord, metric, getAirfreightDirection());
      const previousYear = String(Number(state.year) - 1);
      const airportComparisonInfo = direction === 'balance'
        ? 'Saldo ' + previousYear + ': <strong>' + formatAirfreightValue(previousValue, metric, true, 'balance') + '</strong><br>Saldo 2016: <strong>' + formatAirfreightValue(baselineValue, metric, true, 'balance') + '</strong>'
        : 'Δ Vorjahr: ' + formatAirfreightDelta(getAirfreightPercentChange(record.value, previousValue)) + '<br>Δ ggü. 2016: ' + formatAirfreightDelta(getAirfreightPercentChange(record.value, baselineValue));
      marker.bindTooltip(`
        <div class="map-region-tooltip">
          <div class="map-tooltip-title">${name || record.code} <span>(${record.code})</span></div>
          <div class="map-tooltip-meta">Bezugsjahr: ${state.year}</div>
          <div class="map-tooltip-value">${getAirfreightMetricLabel(metric)}: ${formatAirfreightValue(record.value, metric)}</div>
          <div class="map-tooltip-context">${getAirfreightDirectionLabel()}<br>${airportComparisonInfo}</div>
          <div class="map-tooltip-filter-hint">Klicken Sie, um diesen Flughafen auszuwählen und seine Top-Relationen anzuzeigen.</div>
        </div>`, { sticky: true, className: 'airfreight-leaflet-tooltip' });
      marker.on('click', () => {
        state.selectedAirport = selected ? null : record.code;
        renderAirfreightTab();
        updateAnalysisSummary();
      });
      mapLayers.airfreight.airportsLookup[record.code] = marker;
    });

    const selected = airfreightData.airports?.[state.selectedAirport];
    const visibleRelations = selected ? relations.slice(0, state.topX) : [];
    const relationSum = visibleRelations.reduce((sum, relation) => sum + Math.abs(Number(relation.value) || 0), 0);
    visibleRelations.forEach(relation => {
      const partner = airfreightData.airports?.[relation.partner];
      if (!partner || !Number.isFinite(Number(partner.lat)) || !Number.isFinite(Number(partner.lng))) return;
      const weight = relationClasses.getWeight(relation.value);
      const share = relationSum > 0 ? (Math.abs(relation.value) / relationSum) * 100 : null;
      const allPublishedSum = direction === 'balance'
        ? null
        : getAirfreightValue(airfreightData?.relationTotals?.[state.year]?.[state.selectedAirport], metric, direction);
      const shareAll = Number.isFinite(allPublishedSum) && Math.abs(allPublishedSum) > 0
        ? (Math.abs(relation.value) / Math.abs(allPublishedSum)) * 100
        : null;
      const route = getAirfreightDirection() === 'outbound'
        ? `${selected.name} <span>(${state.selectedAirport})</span> → ${partner.name} <span>(${relation.partner})</span>`
        : getAirfreightDirection() === 'inbound'
        ? `${partner.name} <span>(${relation.partner})</span> → ${selected.name} <span>(${state.selectedAirport})</span>`
        : `${selected.name} <span>(${state.selectedAirport})</span> ↔ ${partner.name} <span>(${relation.partner})</span>`;
      const relationComparisonInfo = direction === 'balance'
        ? 'Saldo ' + String(Number(state.year) - 1) + ': <strong>' + formatAirfreightValue(relation.previous_value, metric, true, 'balance') + '</strong><br>Saldo 2016: <strong>' + formatAirfreightValue(relation.baseline_value, metric, true, 'balance') + '</strong>'
        : 'Vorjahr: ' + formatAirfreightDelta(relation.yoy_pct) + '<br>Gegenüber 2016: ' + formatAirfreightDelta(relation.trend_pct);
      const shareAllInfo = direction === 'balance'
        ? 'Anteil an allen veröffentlichten Top-Relationen: <strong>--</strong><br><span style="color:#64748b;">Für Salden wird kein Gesamtanteil ausgewiesen.</span>'
        : 'Anteil an allen veröffentlichten Top-Relationen: <strong>' + (shareAll === null ? '--' : formatDeNum(shareAll, 1) + ' %') + '</strong>';
      const tooltip = `
        <div class="flow-relation-tooltip">
          <div class="flow-tooltip-eyebrow">Veröffentlichte Top-Relation im Luftfrachtverkehr · ${state.year}</div>
          <div class="flow-tooltip-route">${route}</div>
          <div class="flow-tooltip-value">${getAirfreightMetricLabel(metric)}: ${formatAirfreightValue(relation.value, metric)}</div>
          <div class="flow-tooltip-modes">${directionLabel}</div>
          <div class="flow-tooltip-context">${relationComparisonInfo}<br>Anteil an der angezeigten Top-Auswahl: <strong>${share === null ? '--' : `${formatDeNum(share, 1)} %`}</strong><br>${shareAllInfo}</div>
        </div>`;
      const tooltipOptions = { sticky: true, opacity: 0.98, className: 'airfreight-leaflet-tooltip' };
      const line = L.polyline([[selected.lat, selected.lng], [partner.lat, partner.lng]], {
        pane: 'connectionPane',
        className: 'airfreight-relation-line flow-relation-target',
        color: AIRFREIGHT_COLOR,
        opacity: 0.72,
        weight
      }).bindTooltip(tooltip, tooltipOptions).addTo(mapLayers.airfreight.airportsGroup);
      const partnerRadius = relationClasses.getRadius(relation.value);
      const partnerMarker = L.circleMarker([partner.lat, partner.lng], {
        pane: 'connectionPane',
        className: 'airfreight-relation-marker flow-relation-target',
        radius: partnerRadius,
        fillColor: AIRFREIGHT_COLOR,
        fillOpacity: 0.9,
        color: '#ffffff',
        weight: 1.2
      }).bindTooltip(tooltip, tooltipOptions).addTo(mapLayers.airfreight.airportsGroup);
      mapLayers.airfreight.spiderLookup[relation.partner] = {
        line,
        marker: partnerMarker,
        originalColor: AIRFREIGHT_COLOR,
        originalWeight: weight,
        originalOpacity: 0.72,
        originalRadius: partnerRadius,
        originalMarkerColor: AIRFREIGHT_COLOR,
        originalMarkerOpacity: 0.9,
        originalMarkerWeight: 1.2,
        originalMarkerBorderColor: '#ffffff'
      };
      [line, partnerMarker].forEach(layer => {
        layer.on('mouseover', event => {
          openActiveRelationTooltip('airfreight', layer, event);
          setHighlight('airfreight', relation.partner);
        });
        layer.on('mouseout', scheduleAirfreightHighlightClear);
      });
    });
    bindMapHighlightReset('airfreight');

    // The analytical focus remains Germany even when worldwide relations are
    // shown. Selecting an airport therefore never expands the viewport.
    airfreightViewportBounds = null;
    setMapDefaultViewport('airfreight');
  }

  function renderAirfreightRelations(relations) {
    const body = document.getElementById('tableAirfreightRelationsBody');
    if (!body) return;
    const metric = getAirfreightMetric();
    const selected = airfreightData.airports?.[state.selectedAirport];
    setText('airfreightRelationsTitle', selected
      ? `Top ${state.topX} Relationen: ${selected.name}`
      : 'Top Relationen: Flughafen auswählen');
    setText('thAirfreightMeasure', metric === 'flights' ? 'Flüge (Anzahl)' : 'Menge (t)');
    const isBalance = getAirfreightDirection() === 'balance';
    const historicalSaldo = value => value === null || value === undefined
      ? '<span style="color:#94a3b8;">--</span>'
      : '<span style="font-weight:700;">' + formatAirfreightValue(value, metric, false, 'balance') + '</span>';
    const yoyHeader = document.getElementById('thAirfreightYoY');
    const trendHeader = document.getElementById('thTrend_airfreight');
    if (yoyHeader) {
      yoyHeader.innerHTML = isBalance ? 'Saldo<br><span>' + (Number(state.year) - 1) + '</span>' : 'Δ<br><span>Vorjahr</span>';
      yoyHeader.title = isBalance ? 'Historischer Saldo im Vorjahr' : 'Veränderung gegenüber dem Vorjahr';
    }
    if (trendHeader) {
      trendHeader.innerHTML = isBalance ? 'Saldo<br><span>2016</span>' : 'Δ<br><span>ggü. 2016</span>';
      trendHeader.title = isBalance ? 'Historischer Saldo im Basisjahr 2016' : 'Veränderung gegenüber dem Basisjahr 2016';
    }

    if (!state.selectedAirport) {
      setAirfreightRelationStatus('');
      const airportMetricAvailable = isAirfreightAirportMetricYearAvailable();
      setText('airfreightMapScope', airportMetricAvailable ? `${state.year} · Flughafen auswählen` : `${state.year} · Flughafenwerte nicht belastbar`);
      body.innerHTML = `
        <tr><td colspan="5" style="text-align:center; color:#475569; padding:28px 16px; font-size:0.86rem; line-height:1.6;">
          <div class="empty-state-icon"><img src="assets/icons/map.svg" alt="" aria-hidden="true"></div>
          <strong style="color:#0f172a; font-size:0.95rem;">${airportMetricAvailable ? 'Alle deutschen Flughäfen sichtbar' : `Flughafen-Flugzahlen ${state.year} derzeit nicht belastbar`}</strong><br>
          <span style="color:#64748b; font-size:0.81rem;">${airportMetricAvailable ? 'Bitte wählen Sie auf der Karte einen <strong>Flughafen</strong> aus oder öffnen Sie <strong>Aktuelle Einstellungen → Raum &amp; Zeit</strong>, um dessen stärkste veröffentlichte Top-Relationen im Luftfrachtverkehr anzuzeigen.' : 'Die veröffentlichten Flughafenwerte widersprechen der nationalen Reihe und werden deshalb nicht dargestellt. Die nationale Flugzahl bleibt verfügbar.'}</span>
        </td></tr>`;
      return;
    }

    const availableYears = airfreightData.metadata.availableRelationYears.map(String);
    if (!availableYears.includes(state.year)) {
      const latest = airfreightData.metadata.latestRelationYear;
      body.innerHTML = '';
      setAirfreightRelationStatus(
        `Für das ausgewählte Jahr <strong>${state.year}</strong> liegen keine Relationsdaten vor. Das letzte verfügbare Relationsjahr ist <strong>${latest}</strong>. <button type="button" class="select-input-sm">${latest} auswählen</button>`,
        true
      );
      setText('airfreightMapScope', `Relationen ${state.year} nicht verfügbar`);
      return;
    }

    setAirfreightRelationStatus('');
    setText('airfreightMapScope', `${getAirfreightDirectionLabel(getAirfreightDirection(), true)} · ${state.year}`);
    const visible = relations.slice(0, state.topX);
    if (!visible.length) {
      body.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748b; padding:28px 16px;">Für diese Auswahl sind keine veröffentlichten Top-Relationen vorhanden.</td></tr>';
      return;
    }
    body.innerHTML = visible.map((relation, rank) => {
      const partner = airfreightData.airports?.[relation.partner] || { code: relation.partner, name: relation.partner, country: '' };
      const noPoint = !Number.isFinite(Number(partner.lat)) || !Number.isFinite(Number(partner.lng));
      const countryName = getAirfreightCountryName(partner.country);
      return `<tr data-partner-id="${relation.partner}">
        <td class="relation-partner-cell"><span class="relation-rank" aria-label="Rang ${rank + 1}">${rank + 1}<span class="relation-rank-separator" aria-hidden="true">·</span></span><span class="relation-partner-details"><strong>${partner.name || relation.partner}</strong><span class="table-sub-label">(${relation.partner})</span>${noPoint ? '<span class="table-status-label">ohne Kartenpunkt</span>' : ''}</span></td>
        <td><span class="table-truncated-label" tabindex="0" data-full-label="${countryName}">${countryName}</span></td>
        <td style="text-align:right; font-weight:700;">${formatAirfreightValue(relation.value, metric, false)}</td>
        <td style="text-align:right;">${isBalance ? historicalSaldo(relation.previous_value) : formatAirfreightDelta(relation.yoy_pct)}</td>
        <td style="text-align:right;">${isBalance ? historicalSaldo(relation.baseline_value) : formatAirfreightDelta(relation.trend_pct)}</td>
      </tr>`;
    }).join('');
    body.querySelectorAll('tr[data-partner-id]').forEach(row => {
      const partnerId = row.dataset.partnerId;
      row.addEventListener('mouseenter', () => setHighlight('airfreight', partnerId, false));
      row.addEventListener('mouseleave', scheduleAirfreightHighlightClear);
    });
    body.querySelectorAll('[data-full-label]').forEach(label => bindAirfreightTableTooltip(label, label.dataset.fullLabel));
    const tableWrapper = body.closest('.data-table-wrapper');
    if (tableWrapper) tableWrapper.onmouseleave = () => clearAllHighlights('airfreight');
  }

  function renderAirfreightChart(entries) {
    const canvas = document.getElementById('chartAirfreightAirports');
    if (!canvas) return;
    if (chartAirfreightAirports) {
      chartAirfreightAirports.destroy();
      chartAirfreightAirports = null;
    }
    const metric = getAirfreightMetric();
    const direction = getAirfreightDirection();
    const isBalance = direction === 'balance';
    const unit = metric === 'flights' ? 'Flüge' : 'Mio. t';
    const selectedName = airfreightData.airports?.[state.selectedAirport]?.name || state.selectedAirport;
    const measurementTitle = metric === 'flights' ? 'Anzahl reiner Fracht- und Postflüge' : 'Fracht- und Postaufkommen';

    if (state.airfreightChartView === 'trend') {
      const codes = [...new Set([...entries.slice(0, 5).map(record => record.code), state.selectedAirport].filter(Boolean))];
      const years = (metric === 'flights'
        ? airfreightData.metadata.availableAirportFlightYears
        : airfreightData.metadata.availableAirportYears).map(String);
      const datasets = codes.map((code, index) => ({
        label: airfreightData.airports?.[code]?.name || code,
        data: years.map(year => {
          const value = getAirfreightValue(airfreightData.airportValues?.[year]?.[code], metric, direction);
          return value === null ? null : metric === 'tonnes' ? value / 1e6 : value;
        }),
        borderColor: AIRFREIGHT_TREND_COLORS[index % AIRFREIGHT_TREND_COLORS.length],
        backgroundColor: AIRFREIGHT_TREND_COLORS[index % AIRFREIGHT_TREND_COLORS.length],
        borderWidth: code === state.selectedAirport ? 3.5 : 2,
        pointRadius: code === state.selectedAirport ? 3 : 2,
        tension: 0.2,
        spanGaps: false
      }));
      setText('airfreightChartTitle', `Entwicklung führender deutscher Flughäfen: ${isBalance ? 'Saldo Fracht und Post' : measurementTitle}${selectedName ? ` · Auswahl: ${selectedName}` : ''}`);
      chartAirfreightAirports = new Chart(canvas, {
        type: 'line',
        data: { labels: years, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: true, position: 'bottom', labels: { boxWidth: 10, padding: 8 } },
            tooltip: {
              callbacks: {
                label: item => ` ${item.dataset.label}: ${formatDeNum(item.parsed.y, metric === 'tonnes' ? 2 : 0)} ${unit}`
              }
            }
          },
          scales: {
            x: { ticks: { font: { size: 11, weight: '600' } } },
            y: { beginAtZero: !isBalance, title: { display: true, text: isBalance ? `Saldo (${unit})` : unit, font: { size: 11, weight: '600' } } }
          }
        }
      });
      return;
    }

    const visible = entries.slice(0, state.topX);
    const labels = visible.map(record => record.meta.name || record.code);
    const values = visible.map(record => metric === 'tonnes' ? record.value / 1e6 : record.value);
    setText('airfreightChartTitle', `Top ${state.topX} deutsche Flughäfen nach ${isBalance ? 'absolutem Saldo von Fracht und Post' : measurementTitle} · ${state.year}`);
    chartAirfreightAirports = new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: isBalance ? `Saldo (${unit})` : unit,
          data: values,
          backgroundColor: AIRFREIGHT_COLOR,
          borderRadius: 4,
          maxBarThickness: 24
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: !isBalance, title: { display: true, text: isBalance ? `Saldo (${unit})` : unit, font: { size: 11, weight: '600' } } },
          y: { ticks: { callback: (_value, index) => abbreviateAxisLabel(labels[index], 22), font: { size: 11, weight: '600' } } }
        }
      }
    });
    enableYAxisLabelHover(chartAirfreightAirports, labels);
  }

  function renderAirfreightTab() {
    if (!airfreightData) return;
    const metric = getAirfreightMetric();
    const direction = getAirfreightDirection();
    const entries = getAirfreightAirportEntries(state.year, metric, direction);
    ensureAirfreightAirportSelection(entries);
    updateAirfreightAirportSelect(entries);
    const relations = getAirfreightRelations();
    setText('airfreightMapTitle', `Deutsche Flughäfen · ${getAirfreightDirectionLabel(direction, true)} · ${state.year}`);
    renderAirfreightKpis(entries);
    renderAirfreightMap(entries, relations);
    renderAirfreightRelations(relations);
    renderAirfreightChart(entries);
  }

  function setAirfreightFilterMode(isAirfreight, isToll = false, isMaritime = false) {
    const normalGroups = ['controlGroupRegion', 'controlGroupMetric', 'controlGroupGoods'];
    const airfreightGroups = ['controlGroupAirfreightAirport', 'controlGroupAirfreightMetric'];
    if (!isToll) {
      normalGroups.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.hidden = isAirfreight || (isMaritime && id === 'controlGroupRegion');
      });
    }
    airfreightGroups.forEach(id => {
      const element = document.getElementById(id);
      if (element) element.hidden = !isAirfreight;
    });
    document.getElementById('analysisPanelBody')?.classList.toggle('is-airfreight-mode', isAirfreight);
  }

  function setupAirfreightEventListeners() {
    document.getElementById('selectAirfreightAirport')?.addEventListener('change', event => {
      state.selectedAirport = event.target.value || null;
      renderAirfreightTab();
      updateAnalysisSummary();
    });
    document.getElementById('selectAirfreightMetric')?.addEventListener('change', event => {
      state.airfreightMetric = event.target.value === 'flights' ? 'flights' : 'tonnes';
      renderAirfreightTab();
      updateAnalysisSummary();
    });
    document.querySelectorAll('#toggleAirfreightChartView .toggle-btn').forEach(button => {
      button.addEventListener('click', () => {
        state.airfreightChartView = button.dataset.view === 'trend' ? 'trend' : 'snapshot';
        document.querySelectorAll('#toggleAirfreightChartView .toggle-btn').forEach(item => item.classList.toggle('active', item === button));
        renderAirfreightChart(getAirfreightAirportEntries());
      });
    });
  }
