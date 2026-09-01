  // TAB 6: INTERMODALE VERKEHRE & KV
  // ============================================================
  function getScopedIntermodalMetricForRegion(year, scopeId, mode, category, metric) {
    const scopedYear = intermodalData?.scoped_metrics_by_year?.[String(year)];
    if (!scopedYear) return null;
    const directional = scopedYear?.[scopeId]?.[mode]?.[category];
    // The current pipeline explicitly contains the directional data set. A
    // missing market within a known region means zero, not a national fallback.
    if (!directional) return 0;

    const read = direction => Number(directional?.[direction]?.[metric] || 0);
    const direction = state.direction || 'all';
    // Der globale Binnenverkehrsschalter ist ein reiner Relationsfilter.
    // KPI und Flächenwerte behalten stets die vollständige Grundgesamtheit.
    const binnen = read('binnen');
    if (direction === 'outbound') return read('outbound') + binnen;
    if (direction === 'inbound') return read('inbound') + binnen;
    if (direction === 'balance') return read('outbound') - read('inbound');
    if (scopeId === 'DE' && directional.all) {
      return read('all');
    }
    return read('outbound') + read('inbound') + binnen;
  }

  function getScopedIntermodalMetric(year, mode, category, metric) {
    return getScopedIntermodalMetricForRegion(year, state.region || 'DE', mode, category, metric);
  }

  function renderIntermodalTab() {
    const years = (intermodalData.years || []).map(Number).sort((a, b) => a - b);
    if (!years.length) return;

    const activeYear = years.includes(Number(state.year)) ? Number(state.year) : years.at(-1);
    const pack = intermodalData.data_by_year?.[String(activeYear)];
    if (!pack?.rail || !pack?.iww) return;

    const isTkm = state.metric === 'tkm';
    const metric = isTkm ? 'tkm' : 'tonnes';
    const unit = isTkm ? 'Mrd. tkm' : 'Mio. t';
    const measurementLabel = isTkm ? 'Verkehrsleistung' : 'Beförderungsmenge';
    const divisor = isTkm ? 1e9 : 1e6;
    const value = record => Number(record?.[metric] || 0);
    const formatMetric = record => `${state.direction === 'balance' && value(record) > 0 ? '+' : ''}${formatTrafficValue(value(record) / divisor, unit, 1)} ${unit}`;
    const share = (part, whole) => whole > 0 ? part / whole * 100 : 0;
    const setText = (id, text) => { const el = document.getElementById(id); if (el) el.textContent = text; };
    const previous = intermodalData.data_by_year?.[String(activeYear - 1)];
    const formatYoY = (current, prior, points = false) => {
      if (state.direction === 'balance') return '<span style="color:#64748b; font-size:0.75rem; font-weight:600;">Saldo ohne Vorjahresvergleich</span>';
      if (prior === null || prior === undefined || (!points && prior <= 0)) return '-- ggü. Vorjahr';
      const delta = points ? current - prior : (current - prior) / prior * 100;
      return `<span style="color:${delta >= 0 ? '#16a34a' : '#dc2626'}; font-weight:700;">${delta >= 0 ? '↗ +' : '↘ '}${formatDeNum(delta, 1)} ${points ? 'PP' : '%'} ggü. Vorjahr</span>`;
    };

    const scopeValue = (year, mode, category, fallback) => {
      const directional = getScopedIntermodalMetric(year, mode, category, metric);
      return directional === null ? value(fallback) : directional;
    };
    const scopedRecord = amount => ({ [metric]: amount });
    const railKv = scopeValue(activeYear, 'rail', 'intermodal_load_units', pack.rail.intermodal_load_units);
    const iwwKv = scopeValue(activeYear, 'iww', 'containerised_transport', pack.iww.containerised_transport);
    const railTotal = scopeValue(activeYear, 'rail', 'total', pack.rail.total);
    const iwwTotal = scopeValue(activeYear, 'iww', 'total', pack.iww.total);
    const isBalance = state.direction === 'balance';
    const railShare = isBalance ? null : share(railKv, railTotal);
    const iwwShare = isBalance ? null : share(iwwKv, iwwTotal);
    const previousRailKv = previous ? scopeValue(activeYear - 1, 'rail', 'intermodal_load_units', previous.rail?.intermodal_load_units) : null;
    const previousIwwKv = previous ? scopeValue(activeYear - 1, 'iww', 'containerised_transport', previous.iww?.containerised_transport) : null;
    const previousRailTotal = previous ? scopeValue(activeYear - 1, 'rail', 'total', previous.rail?.total) : null;
    const previousIwwTotal = previous ? scopeValue(activeYear - 1, 'iww', 'total', previous.iww?.total) : null;
    // The source statistics remain separate: no common KV total is calculated.
    // Keep KPI titles as compact as in the overview; only the national
    // directional scope needs the material "ohne Transit" qualification.
    const directionSuffix = state.direction === 'balance' ? ' (Saldo)'
      : state.direction === 'outbound' ? ' (Versand)'
      : state.direction === 'inbound' ? ' (Empfang)'
      : '';
    const scopeSuffix = !state.region && state.direction !== 'all' ? ' ohne Transit' : '';
    setText('sgkvRailTitle', `KV Schiene${scopeSuffix}${directionSuffix}`);
    setText('sgkvIwwTitle', `KV Binnenschiff${scopeSuffix}${directionSuffix}`);
    setText('sgkvRailShareTitle', `KV-Anteil Schiene${scopeSuffix}${directionSuffix}`);
    setText('sgkvIwwShareTitle', `KV-Anteil Binnenschiff${scopeSuffix}${directionSuffix}`);
    setText('sgkvRailIntermodal', formatMetric(scopedRecord(railKv)));
    setText('sgkvIwwContainer', formatMetric(scopedRecord(iwwKv)));
    setText('sgkvRailShareKpi', railShare === null ? '—' : `${formatDeNum(railShare, 1)} %`);
    setText('sgkvIwwShareKpi', iwwShare === null ? '—' : `${formatDeNum(iwwShare, 1)} %`);
    const railYoY = document.getElementById('sgkvRailShare');
    if (railYoY) railYoY.innerHTML = formatYoY(railKv, previousRailKv);
    const iwwYoY = document.getElementById('sgkvIwwShare');
    if (iwwYoY) iwwYoY.innerHTML = formatYoY(iwwKv, previousIwwKv);
    const railShareYoY = document.getElementById('sgkvRailTotal');
    if (railShareYoY) railShareYoY.innerHTML = railShare === null
      ? '<span style="color:#64748b; font-size:0.75rem; font-weight:600;">Saldo ohne Anteilsvergleich</span>'
      : formatYoY(railShare, previousRailTotal > 0 ? share(previousRailKv, previousRailTotal) : null, true);
    const iwwShareYoY = document.getElementById('sgkvIwwTotal');
    if (iwwShareYoY) iwwShareYoY.innerHTML = iwwShare === null
      ? '<span style="color:#64748b; font-size:0.75rem; font-weight:600;">Saldo ohne Anteilsvergleich</span>'
      : formatYoY(iwwShare, previousIwwTotal > 0 ? share(previousIwwKv, previousIwwTotal) : null, true);

    const relationLists = intermodalData.relations_by_year || {};
    const relationValue = relation => Number(relation?.[metric] || 0);
    const allRelationsForYear = year => ['rail', 'iww'].flatMap(mode =>
      (relationLists[String(year)]?.[mode] || []).map(item => ({ ...item, mode }))
    ).filter(relation => relationValue(relation) > 0);
    const allRelations = allRelationsForYear(activeYear);
    const direction = state.direction || 'all';

    // A relation is indexed by partner and source market for the map, or just
    // by partner for the table. In either case inbound and outbound records
    // are combined for the overall-direction view.
    const aggregateSelectedRelations = (year, mergeMarkets = false) => {
      if (!state.region) return new Map();
      const grouped = new Map();
      allRelationsForYear(year).forEach(relation => {
        const isBinnen = relation.origin_id === relation.destination_id;
        if (!state.includeBinnen && isBinnen) return;
        const isOutbound = relation.origin_id === state.region;
        const isInbound = relation.destination_id === state.region;
        if ((direction === 'outbound' && !isOutbound) ||
            (direction === 'inbound' && !isInbound) ||
            (direction === 'all' && !isOutbound && !isInbound) ||
            (direction === 'balance' && !isOutbound && !isInbound)) return;

        const partnerId = isOutbound ? relation.destination_id : relation.origin_id;
        const key = mergeMarkets ? partnerId : `${relation.mode}:${partnerId}`;
        if (!grouped.has(key)) {
          grouped.set(key, {
            relation_id: key,
            mode: relation.mode,
            modes: new Set(),
            partner_id: partnerId,
            origin_id: direction === 'inbound' ? partnerId : state.region,
            destination_id: direction === 'inbound' ? state.region : partnerId,
            tonnes: 0,
            tkm: 0,
            load_units: 0,
            load_carriers: 0,
            teu: 0
          });
        }
        const target = grouped.get(key);
          target.modes.add(relation.mode);
        const sign = direction === 'balance'
          ? (isOutbound && isInbound ? 0 : (isOutbound ? 1 : -1))
          : 1;
        ['tonnes', 'tkm', 'load_units', 'load_carriers', 'teu'].forEach(field => {
          const amount = Number(relation[field] || 0);
          if (isOutbound) target[`outbound_${field}`] = (target[`outbound_${field}`] || 0) + amount;
          if (isInbound) target[`inbound_${field}`] = (target[`inbound_${field}`] || 0) + amount;
          target[field] += sign * amount;
        });
      });
      return grouped;
    };

    const selectedNow = aggregateSelectedRelations(activeYear);
    const selectedPrevious = aggregateSelectedRelations(activeYear - 1);
    const selectedBaseline = aggregateSelectedRelations(years[0]);
    const buildRankedRelations = (currentRelations, previousRelations, baselineRelations) =>
      [...currentRelations.values()]
        .sort((a, b) => Math.abs(relationValue(b)) - Math.abs(relationValue(a)))
        .slice(0, state.topX)
        .map(relation => {
        const current = relationValue(relation);
        const prior = relationValue(previousRelations.get(relation.relation_id));
        const baseline = relationValue(baselineRelations.get(relation.relation_id));
        return {
          ...relation,
          current,
          yoy: prior > 0 && activeYear !== years[0] ? (current - prior) / prior * 100 : null,
          trend: baseline > 0 && activeYear !== years[0] ? (current - baseline) / baseline * 100 : null
        };
      });
    const tableRelations = buildRankedRelations(
      aggregateSelectedRelations(activeYear, true),
      aggregateSelectedRelations(activeYear - 1, true),
      aggregateSelectedRelations(years[0], true)
    );
    // The table ranks the combined value per partner. Once a partner is in
    // that Top-X set, draw every source market recorded for that partner. A
    // previous Top-X cut across individual market records could discard the
    // smaller IWW record although the table correctly showed both badges.
    const tablePartnerIds = new Set(tableRelations.map(relation => relation.partner_id));
    const topRelations = [...selectedNow.values()]
      .filter(relation => tablePartnerIds.has(relation.partner_id))
      .map(relation => {
        const current = relationValue(relation);
        const prior = relationValue(selectedPrevious.get(relation.relation_id));
        const baseline = relationValue(selectedBaseline.get(relation.relation_id));
        return {
          ...relation,
          current,
          yoy: prior > 0 && activeYear !== years[0] ? (current - prior) / prior * 100 : null,
          trend: baseline > 0 && activeYear !== years[0] ? (current - baseline) / baseline * 100 : null
        };
      })
      // Blue rail is drawn first; the green dashed IWW line is then guaranteed
      // to remain visible above it where both markets share the same geometry.
      .sort((a, b) => (a.mode === 'rail' ? 0 : 1) - (b.mode === 'rail' ? 0 : 1));

    const setIntermodalPartnerHighlight = partnerId => {
      if (!partnerId) return;
      clearAllHighlights('intermodal');
      activeHighlightedPartnerId = `intermodal:${partnerId}`;
      activeHighlightedMapKey = 'intermodal';
      document.querySelectorAll(`#tableIntermodalRelationsBody tr[data-partner-id="${partnerId}"]`).forEach(row => {
        row.classList.add('row-highlight');
        row.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });
      Object.values(mapLayers.intermodal?.spiderLookup || {}).forEach(item => {
        if (item.partnerId !== partnerId) return;
        item.line?.setStyle({ color: item.originalColor, weight: Math.max(6.5, item.originalWeight + 3.5), opacity: 1 });
        item.line?.bringToFront();
        item.marker?.setStyle({ fillColor: item.originalColor, radius: Math.max(6.5, item.originalWeight + 3.5), weight: 3, color: '#ffffff' });
        item.marker?.bringToFront();
      });
    };

    // Die Flächenkarte bündelt die beiden amtlich erfassten KV-Teilmärkte als
    // Intensitätsmaß. Sie ist keine Zahl eindeutiger Sendungen, weil dieselbe
    // Transportkette in beiden Teilmarktstatistiken vorkommen kann. KPIs und
    // Anteile bleiben deshalb weiterhin getrennt.
    const mapMarketLabel = 'Summe erfasster KV-Teilmärkte';
    const intermodalDirectionLabel = direction === 'outbound' ? 'Versand'
      : direction === 'inbound' ? 'Empfang'
      : direction === 'balance' ? 'Verkehrssaldo'
      : 'Versand & Empfang';
    const intermodalMetricLabel = isTkm ? 'Verkehrsleistung' : 'Verkehrsaufkommen';
    const intermodalLegendTitle = `Intermodaler Verkehr: ${direction === 'balance' ? 'Saldo' : intermodalMetricLabel}`;
    setText('intermodalMapTitle', `${mapMarketLabel}: ${intermodalMetricLabel} (${intermodalDirectionLabel}) (${activeYear})`);
    setText('intermodalAreaLegendTitle', intermodalLegendTitle);
    setText('intermodalRelationsTitle', `${state.direction === 'balance' ? `Top ${state.topX} Nettobeziehungen` : `Top ${state.topX} Relationen`}: ${state.region ? (regionsData[state.region]?.name || state.region) : 'Region auswählen'}`);
    setText('thIntermodalMeasure', state.direction === 'balance'
      ? (isTkm ? 'Saldo (Mrd. tkm)' : 'Saldo (Mio. t)')
      : (isTkm ? 'Leistung (Mrd. tkm)' : 'Menge (Mio. t)'));

    // Area values deliberately come from the same complete regional data basis
    // as the KPIs. Inland relation lines below remain a separate, cartographic
    // detail view and must not be re-summed into a regional total.
    const choro = {};
    (geojsonNuts3?.features || []).forEach(feature => {
      const id = feature.properties?.NUTS_ID;
      if (!id) return;
      const railAmount = getScopedIntermodalMetricForRegion(activeYear, id, 'rail', 'intermodal_load_units', metric) || 0;
      const iwwAmount = getScopedIntermodalMetricForRegion(activeYear, id, 'iww', 'containerised_transport', metric) || 0;
      choro[id] = railAmount + iwwAmount;
    });
    const maxChoro = Math.max(1, ...Object.values(choro).map(v => Math.abs(v)));
    const map = maps.intermodal;
    const closeRelationTooltip = () => {
      mapLayers.intermodal?.activeTooltipLayer?.closeTooltip();
      mapLayers.intermodal.activeTooltipLayer = null;
    };
    const openRelationTooltip = (layer, event) => {
      closeMapTooltips(map);
      closeRelationTooltip();
      layer.openTooltip(event.latlng);
      mapLayers.intermodal.activeTooltipLayer = layer;
    };
    if (map && geojsonNuts3) {
      if (mapLayers.intermodal.geojson) map.removeLayer(mapLayers.intermodal.geojson);
      mapLayers.intermodal.geojson = L.geoJSON(geojsonNuts3, {
        renderer: getNutsRegionRenderer(map),
        style: feature => {
          const id = feature.properties?.NUTS_ID;
          const selected = id === state.region;
          return {
            // Intermodal areas deliberately use the same blue scale as the
            // legend; relation lines distinguish the two source markets.
            fillColor: getChoroplethColor(choro[id] || 0, maxChoro, direction === 'balance', 'rail'),
            color: selected ? '#0f172a' : '#94a3b8',
            weight: selected ? 3.5 : 0.75,
            opacity: 1,
            fillOpacity: selected ? 0.88 : 0.65
          };
        },
        onEachFeature: (feature, layer) => {
          const id = feature.properties?.NUTS_ID;
          const amount = choro[id] || 0;
          const railAmount = getScopedIntermodalMetricForRegion(activeYear, id, 'rail', 'intermodal_load_units', metric) || 0;
          const iwwAmount = getScopedIntermodalMetricForRegion(activeYear, id, 'iww', 'containerised_transport', metric) || 0;
          const directionSuffix = direction === 'balance' ? ' · Saldo'
            : direction === 'outbound' ? ' · Versand'
            : direction === 'inbound' ? ' · Empfang'
            : '';
          layer.bindTooltip(`
            <div class="map-region-tooltip">
              <div class="map-tooltip-eyebrow">Kombinierter Verkehr · ${activeYear}${directionSuffix}</div>
              <div class="map-tooltip-title">${feature.properties?.NUTS_NAME || id} <span>(${id})</span></div>
              <div class="map-tooltip-value"><span>Summe erfasster KV-Teilmärkte:</span> ${amount > 0 && direction === 'balance' ? '+' : ''}${formatTrafficValue(amount / divisor, unit, 2)} ${unit}</div>
              <div class="map-tooltip-context">Schiene: <strong>${railAmount > 0 && direction === 'balance' ? '+' : ''}${formatTrafficValue(railAmount / divisor, unit, 2)} ${unit}</strong> · Binnenschiff: <strong>${iwwAmount > 0 && direction === 'balance' ? '+' : ''}${formatTrafficValue(iwwAmount / divisor, unit, 2)} ${unit}</strong></div>
              <div class="map-tooltip-context">Intensitätsmaß; keine Zahl eindeutiger Sendungen.</div>
              <div class="map-tooltip-filter-hint">Klicken Sie, um diese Region/diesen Kreis als Filter zu aktivieren.</div>
            </div>`,
          { sticky: true, className: 'intermodal-region-leaflet-tooltip' });
          delayRegionTooltip(layer);
          layer.on('click', () => setRegion(id));
        }
      }).addTo(map);
      if (state.region) mapLayers.intermodal.geojson.eachLayer(layer => {
        if (layer.feature?.properties?.NUTS_ID === state.region) layer.bringToFront?.();
      });
    }

    renderStateBoundaries('intermodal');
    closeRelationTooltip();
    const drawableTopRelations = topRelations.filter(relation =>
      hasUsableMapLocation(fullCentroids[relation.origin_id]) &&
      hasUsableMapLocation(fullCentroids[relation.destination_id])
    );
    const spider = mapLayers.intermodal?.spiderGroup;
    if (spider) spider.clearLayers();
    mapLayers.intermodal.spiderLookup = {};
    if (map && state.region && state.showIntermodalRelations) {
      bindMapHighlightReset('intermodal');
      const maxRelation = Math.max(1, ...drawableTopRelations.map(relation => Math.abs(relation.current)));
      drawableTopRelations.forEach(relation => {
        const origin = fullCentroids[relation.origin_id];
        const destination = fullCentroids[relation.destination_id];
        const partner = fullCentroids[relation.partner_id];
        if (!hasUsableMapLocation(origin) || !hasUsableMapLocation(destination) || !hasUsableMapLocation(partner)) return;
        const relationModes = tableRelations.find(item => item.partner_id === relation.partner_id)?.modes || new Set([relation.mode]);
        const hasBothMarkets = relationModes.has('rail') && relationModes.has('iww');
        const isCombinedMarketLine = !isBalance && hasBothMarkets;
        const partnerMarketRelations = topRelations.filter(item => item.partner_id === relation.partner_id);
        const railRelation = partnerMarketRelations.find(item => item.mode === 'rail');
        const iwwRelation = partnerMarketRelations.find(item => item.mode === 'iww');
        const color = direction === 'balance'
          ? (relation.current >= 0 ? '#16a34a' : '#7c3aed')
          : (relation.mode === 'rail' ? '#2563eb' : '#0f766e');
        const weight = 1.5 + 4 * Math.sqrt(Math.abs(relation.current) / maxRelation);
        const line = L.polyline([[origin.lat, origin.lng], [destination.lat, destination.lng]], {
          pane: 'connectionPane', className: 'flow-relation-target', color, weight, opacity: 0.82, lineCap: 'round',
          // Combined relations use two complementary dash phases: blue,
          // gap, green, gap. Both source markets therefore remain distinct
          // without one continuous line visually swallowing the other.
          dashArray: isCombinedMarketLine ? '7 17' : null,
          dashOffset: isCombinedMarketLine ? (relation.mode === 'iww' ? '-12' : '0') : null
        }).addTo(spider);
        // The endpoint marker belongs to the partner region, not always to
        // the stored destination. It is therefore visible for inbound, outbound
        // and combined-direction relations alike.
        const marker = L.circleMarker([partner.lat, partner.lng], {
          pane: 'connectionPane', className: 'flow-relation-target', radius: Math.max(4.5, weight + 1), color: '#ffffff', weight: 2, fillColor: color, fillOpacity: 0.92
        }).addTo(spider);
        const market = relation.mode === 'rail' ? 'Schiene' : 'Binnenschiff · Containerverkehr';
        const unitDetails = relation.mode === 'rail'
          ? `<div>Ladeeinheiten: <strong>${formatDeNum(relation.load_units, 0)}</strong></div>${relation.teu > 0 ? `<div>TEU: <strong>${formatDeNum(relation.teu, 1)}</strong></div>` : ''}`
          : `<div>Ladungsträger: <strong>${formatDeNum(relation.load_carriers, 0)}</strong></div><div>TEU: <strong>${formatDeNum(relation.teu, 1)}</strong></div>`;
        const routeLabel = (direction === 'all' || direction === 'balance') ? `${origin.name} ↔ ${destination.name}` : `${origin.name} → ${destination.name}`;
        const delta = amount => amount === null
          ? '<span class="popup-delta-neutral">--</span>'
          : `<span class="popup-delta ${amount >= 0 ? 'is-positive' : 'is-negative'}">${amount >= 0 ? '↗ +' : '↘ '}${formatDeNum(amount, 1)} %</span>`;
        const balanceDetails = direction === 'balance'
          ? `<div><strong>Versand:</strong> ${isTkm ? formatTkmQuantity(relation.outbound_tkm / divisor, 1, true) : formatQuantity(relation.outbound_tonnes / divisor, 1)} ${unit}</div><div><strong>Empfang:</strong> ${isTkm ? formatTkmQuantity(relation.inbound_tkm / divisor, 1, true) : formatQuantity(relation.inbound_tonnes / divisor, 1)} ${unit}</div><div><strong>Saldo:</strong> ${relation.current >= 0 ? '+' : ''}${isTkm ? formatTkmQuantity(relation.current / divisor, 1, true) : formatQuantity(relation.current / divisor, 1)} ${unit} · ${relation.current >= 0 ? 'Versandüberschuss' : 'Empfangsüberschuss'}</div>`
          : '';
        const combinedPopup = isCombinedMarketLine && railRelation && iwwRelation
          ? `<div class="intermodal-relation-popup"><div class="popup-eyebrow">${activeYear} · Schiene und Binnenschiff</div><strong>${routeLabel}</strong><div class="popup-market-amount rail"><span>Schiene</span><strong>${formatTrafficValue(railRelation.current / divisor, unit, 3)} ${unit}</strong></div><div class="popup-market-amount iww"><span>Binnenschiff</span><strong>${formatTrafficValue(iwwRelation.current / divisor, unit, 3)} ${unit}</strong></div><div class="popup-market-total"><span>Summe erfasster Teilmärkte</span><strong>${formatTrafficValue((railRelation.current + iwwRelation.current) / divisor, unit, 3)} ${unit}</strong></div><div class="popup-deltas">Die Linienstärke zeigt die Menge des jeweiligen Teilmarkts.</div></div>`
          : '';
        const popup = combinedPopup || `<div class="intermodal-relation-popup"><div class="popup-eyebrow">${activeYear} · ${market}</div><strong>${routeLabel}</strong><div>${direction === 'balance' ? 'Nettosaldo' : measurementLabel}: <strong>${relation.current >= 0 && direction === 'balance' ? '+' : ''}${isTkm ? formatTkmQuantity(relation.current / divisor, 1, true) : formatQuantity(relation.current / divisor, 1)} ${unit}</strong></div>${balanceDetails || unitDetails}${direction === 'balance' ? '<div class="popup-deltas">Für Salden wird kein prozentualer Zeitvergleich ausgewiesen.</div>' : `<div class="popup-deltas">Vorjahr: ${delta(relation.yoy)} · ggü. ${years[0]}: ${delta(relation.trend)}</div>`}</div>`;
        const tooltipOptions = { sticky: true, opacity: 0.98, className: 'intermodal-leaflet-tooltip' };
        line.bindTooltip(popup, tooltipOptions);
        marker.bindTooltip(popup, tooltipOptions);
        mapLayers.intermodal.spiderLookup[relation.relation_id] = { line, marker, partnerId: relation.partner_id, originalColor: color, originalWeight: weight };
        line.on('mouseover', event => { openRelationTooltip(line, event); setIntermodalPartnerHighlight(relation.partner_id); });
        line.on('mouseout', () => { closeRelationTooltip(); clearAllHighlights('intermodal'); });
        marker.on('mouseover', event => { openRelationTooltip(marker, event); setIntermodalPartnerHighlight(relation.partner_id); });
        marker.on('mouseout', () => { closeRelationTooltip(); clearAllHighlights('intermodal'); });
      });
    }

    updateIntermodalLegend(maxChoro, drawableTopRelations, unit, divisor, activeYear, isTkm, mapMarketLabel, intermodalLegendTitle);
    drawSelectedRegionOutline('intermodal');

    const tbody = document.getElementById('tableIntermodalRelationsBody');
    if (tbody) {
      tbody.innerHTML = '';
      if (!state.region) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#475569; padding:28px 16px; font-size:0.86rem; line-height:1.6;"><div class="empty-state-icon"><img src="assets/icons/map.svg" alt="" aria-hidden="true"></div><strong style="color:#0f172a; font-size:0.95rem;">Deutschland aktiv</strong><br><span style="color:#64748b; font-size:0.81rem;">Bitte wählen Sie in der Karte per <strong>Mausklick eine Region</strong> aus oder öffnen Sie <strong>Aktuelle Einstellungen → Raum &amp; Zeit</strong> und wählen Sie dort eine Region aus, um intermodale Verflechtungen anzuzeigen.</span><br><br><span style="color:#475569; font-size:0.79rem;">Die nationalen Teilmarktwerte für Schiene und Binnenschiff enthalten auch Transitverkehre. Diese sind keiner deutschen NUTS-3-Region zugeordnet und erscheinen daher nicht in Karte und Relationstabelle.</span></td></tr>';
      } else if (!tableRelations.length) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748b; padding:24px;">Für diese Auswahl liegen keine qualifizierten KV-Relationen mit Ladeeinheit (Schiene) oder Containerklasse (Binnenschiff) vor.</td></tr>';
      } else {
        tableRelations.forEach((relation, rank) => {
          const origin = fullCentroids[relation.origin_id];
          const destination = fullCentroids[relation.destination_id];
          const partnerName = fullCentroids[relation.partner_id]?.name || relation.partner_id;
          const locationBadge = mapLocationBadge(relation.partner_id);
          const change = amount => direction === 'balance'
            ? '<span style="color:#64748b;" title="Für Salden wird kein prozentualer Zeitvergleich ausgewiesen.">—</span>'
            : amount === null
            ? '<span style="color:#94a3b8;">--</span>'
            : `<span style="color:${amount >= 0 ? '#16a34a' : '#dc2626'}; font-weight:700;">${amount >= 0 ? '↗ +' : '↘ '}${formatDeNum(amount, 1)} %</span>`;
          const row = document.createElement('tr');
          const modes = [...relation.modes].sort();
          // A double badge means that two independent source-market records
          // share the same region pair.  The table amount is their displayed
          // sum for ranking; it is not a count of unique transport chains.
          const modeBadges = modes.map(mode => mode === 'rail'
            ? '<span class="intermodal-mode-badge rail">Schiene</span>'
            : '<span class="intermodal-mode-badge iww">Binnenschiff</span>'
          ).join('');
          row.setAttribute('data-partner-id', relation.partner_id);
          row.innerHTML = `<td><span class="relation-rank" aria-label="Rang ${rank + 1}">${rank + 1}<span class="relation-rank-separator" aria-hidden="true">·</span></span><strong>${partnerName}</strong>${locationBadge}</td><td><span class="intermodal-mode-badges">${modeBadges}</span></td><td style="text-align:right;"><strong>${direction === 'balance' && relation.current > 0 ? '+' : ''}${isTkm ? formatTkmQuantity(relation.current / divisor, 1, true) : formatQuantity(relation.current / divisor, 1)}</strong></td><td style="text-align:right;">${change(relation.yoy)}</td><td style="text-align:right;">${change(relation.trend)}</td>`;
          row.addEventListener('mouseenter', () => setIntermodalPartnerHighlight(relation.partner_id));
          row.addEventListener('mouseleave', () => clearAllHighlights('intermodal'));
          tbody.appendChild(row);
        });
      }
    }

    const renderStructure = (canvasId, labels, getters, colors, denominator, axis, structureView) => {
      const canvas = document.getElementById(canvasId);
      if (!canvas) return;
      const old = canvasId === 'chartKvRailUnits' ? chartKvRailUnits : chartKvIwwUnits;
      if (old) old.destroy();
      const trend = structureView === 'trend';
      const chart = trend
        ? new Chart(canvas, {
          type: 'line',
          data: {
            labels: years,
            datasets: labels.map((label, index) => ({
              label,
              data: years.map(year => value(getters[index](intermodalData.data_by_year?.[String(year)])) / divisor),
              borderColor: colors[index], backgroundColor: colors[index], borderWidth: 2.25, pointRadius: 2.5, tension: 0.18
            }))
          },
          options: {
            responsive: true, maintainAspectRatio: false, interaction: { mode: 'nearest', intersect: true },
            plugins: {
              legend: { position: 'bottom', align: 'start', labels: { boxWidth: 10, padding: 8, font: { size: 10, weight: '600' } } },
              tooltip: { callbacks: { title: items => `Berichtsjahr ${items[0]?.label}`, label: item => formatDynamicChartShare(item, unit, canvasId === 'chartKvRailUnits' ? ' aller Ladeeinheiten' : ' aller Containergrößen') } }
            },
            scales: {
              x: { title: { display: true, text: 'Berichtsjahr', font: { weight: '600' } }, ticks: { font: { size: 10 } }, grid: { display: false } },
              y: { beginAtZero: true, title: { display: true, text: unit, font: { weight: '600' } }, ticks: { callback: tick => formatDeNum(tick, 0) } }
            }
          }
        })
        : new Chart(canvas, {
          type: 'bar',
          data: { labels, datasets: [{ data: getters.map(getter => share(value(getter(pack)), value(denominator(pack)))), backgroundColor: colors, borderRadius: 5, maxBarThickness: 26 }] },
          options: {
            indexAxis: 'y', responsive: true, maintainAspectRatio: false,
            layout: { padding: { left: 8 } },
            plugins: { legend: { display: false }, tooltip: { callbacks: { label: item => ` ${formatDeNum(item.raw, 1)} % (${formatMetric(getters[item.dataIndex](pack))})` } } },
            scales: {
              x: { beginAtZero: true, max: 100, title: { display: true, text: axis, font: { weight: '600' } }, ticks: { callback: tick => `${tick} %` }, grid: { color: '#e2e8f0' } },
              y: {
                afterFit: scale => { scale.width = getYAxisLabelAreaWidth(scale.chart.width); },
                ticks: {
                  font: { size: 10.5, weight: '600' },
                  color: '#334155',
                  crossAlign: 'far',
                  callback: function (_value, index) { return abbreviateAxisLabelToWidth(labels[index], this, 10.5); }
                },
                grid: { display: false }
              }
            }
          }
        });
      if (!trend) enableYAxisLabelHover(chart, labels);
      if (canvasId === 'chartKvRailUnits') chartKvRailUnits = chart;
      else chartKvIwwUnits = chart;
    };

    renderStructure(
      'chartKvRailUnits',
      ['Container / Wechselbehälter', 'Sattelauflieger (unbegleitet)', 'Lkw / Sattelzug (begleitet)'],
      [
        p => p?.rail?.load_unit_structure?.containers_and_swap_bodies,
        p => p?.rail?.load_unit_structure?.unaccompanied_semitrailers,
        p => p?.rail?.load_unit_structure?.accompanied_road_vehicles
      ],
      ['#4d7c0f', '#c4a20a', '#f6c31c'],
      p => p?.rail?.intermodal_load_units,
      'Anteil am Ladeeinheiten-Verkehr (%)',
      state.intermodalRailStructureView
    );
    renderStructure(
      'chartKvIwwUnits',
      ['C/WB 20 Fuß', 'C/WB 40 Fuß', 'Sonstige C/WB'],
      [p => p?.iww?.container_size_structure?.c20, p => p?.iww?.container_size_structure?.c40, p => p?.iww?.container_size_structure?.other_sizes],
      ['#155e75', '#2f95c5', '#7b8796'],
      p => p?.iww?.containerised_transport,
      'Anteil am Containerverkehr (%)',
      state.intermodalIwwStructureView
    );
    const range = `${years[0]}–${years.at(-1)}`;
    setText('intermodalRailStructureTitle', state.intermodalRailStructureView === 'trend' ? `Ladeeinheiten · Schiene (${range})` : 'Ladeeinheiten · Schiene');
    setText('intermodalIwwStructureTitle', state.intermodalIwwStructureView === 'trend' ? `Containergrößen · Binnenschiff (${range})` : 'Containergrößen · Binnenschiff');
  }

  function updateIntermodalLegend(maxValue, relations, unit, divisor, year, isTkm, mapMarketLabel, legendTitle) {
    const legend = document.getElementById('intermodalMapLegend');
    if (!legend) return;
    const collapsed = legend.classList.contains('collapsed');
    const classification = getFlowClassification(relations, isTkm);
    const isBalance = state.direction === 'balance';
    const modeInfo = isBalance ? '' : `<div class="legend-subtitle">Relationen der Auswahl</div><div class="legend-spider-rows"><div class="legend-spider-item"><span class="legend-line legend-line-med" style="background:#2563eb;"></span><span class="legend-spider-val">Schiene · Ladeeinheiten</span></div><div class="legend-spider-item"><span class="legend-line legend-line-med" style="background:#0f766e;"></span><span class="legend-spider-val">Binnenschiff · Container</span></div><div class="legend-spider-item"><span class="legend-line legend-line-med legend-line-combined"></span><span class="legend-spider-val">Schiene und Binnenschiff</span></div></div>`;
    const balanceColors = isBalance ? `<div class="legend-spider-rows" style="margin-top:6px;"><div class="legend-spider-item"><span class="legend-line legend-line-med" style="background:#16a34a;"></span><span class="legend-spider-val">Grün: Versandüberschuss</span></div><div class="legend-spider-item"><span class="legend-line legend-line-med" style="background:#7c3aed;"></span><span class="legend-spider-val">Lila: Empfangsüberschuss</span></div></div>` : '';
    const relationInfo = relations.length
      ? `<div class="legend-spider-section">${modeInfo}<div class="legend-subtitle"${modeInfo ? ' style="margin-top:7px;"' : ''}>Verbindungen</div><div class="legend-spider-rows"><div class="legend-spider-item"><span class="legend-line legend-line-thin" style="background:${isBalance ? '#16a34a' : '#64748b'};"></span><span class="legend-spider-val">${classification.labelThin}</span></div><div class="legend-spider-item"><span class="legend-line legend-line-med" style="background:${isBalance ? '#16a34a' : '#64748b'};"></span><span class="legend-spider-val">${classification.labelMed}</span></div><div class="legend-spider-item"><span class="legend-line legend-line-thick" style="background:${isBalance ? '#16a34a' : '#64748b'};"></span><span class="legend-spider-val">${classification.labelThick}</span></div></div>${balanceColors}</div>`
      : '';
    const scaleHtml = isBalance
      ? '<span style="background:#38bdf8;"></span><span style="background:#e0f2fe;"></span><span style="background:#f8fafc;"></span><span style="background:#dcfce7;"></span><span style="background:#22c55e;"></span>'
      : '<span style="background:#eff6ff;"></span><span style="background:#bfdbfe;"></span><span style="background:#60a5fa;"></span><span style="background:#2563eb;"></span><span style="background:#1e40af;"></span>';
    const scaleLabels = isBalance
      ? `<span>≤ −${formatTrafficValue(maxValue * 0.8 / divisor, unit, 1)} ${unit}</span><span>≥ +${formatTrafficValue(maxValue * 0.8 / divisor, unit, 1)} ${unit}</span>`
      : `<span>&lt; ${formatTrafficValue(maxValue * 0.1 / divisor, unit, 1)} ${unit}</span><span>&gt; ${formatTrafficValue(maxValue * 0.8 / divisor, unit, 1)} ${unit}</span>`;
    legend.innerHTML = `<div class="legend-header"><span class="legend-title">${legendTitle}</span><button type="button" class="btn-legend-toggle" title="${collapsed ? 'Legende maximieren' : 'Legende minimieren'}">${collapsed ? '+' : '−'}</button></div><div class="legend-body" ${collapsed ? 'style="display:none;"' : ''}><div class="legend-scale">${scaleHtml}</div><div class="legend-labels">${scaleLabels}</div>${relationInfo}<div class="intermodal-map-scope">${year} · Kartenfläche: ${mapMarketLabel}</div></div>`;
    legend.querySelector('.btn-legend-toggle')?.addEventListener('click', event => {
      event.preventDefault();
      event.stopPropagation();
      legend.dataset.legendUserToggled = 'true';
      setLegendCollapsedState(legend, !legend.classList.contains('collapsed'));
    });
  }
