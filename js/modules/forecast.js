  // TAB 7: VERKEHRSPROGNOSE 2040 (BMDV BASISPROGNOSE P1)
  // ============================================================

  // Helper: Extract active forecast choropleth value for any combination of filters
  function getForecastChoroplethVal(nutsId, sc, isTkm, direction, groupFilter) {
    const r = sc?.regions?.[nutsId];
    if (!r) return 0;

    if (groupFilter && groupFilter !== 'ALL') {
      const gDict = isTkm ? r.groups_7_tkm : r.groups_7_tonnes;
      if (direction === 'outbound') return gDict?.outbound?.[groupFilter] ?? 0;
      if (direction === 'inbound') return gDict?.inbound?.[groupFilter] ?? 0;
      if (direction === 'balance') return gDict?.balance?.[groupFilter] ?? 0;
      return gDict?.all?.[groupFilter] ?? (gDict?.[groupFilter] ?? 0);
    } else {
      const dDict = isTkm ? r.directions_tkm : r.directions_tonnes;
      if (direction === 'outbound') return dDict?.outbound ?? (r.tonnes?.outbound ?? 0);
      if (direction === 'inbound') return dDict?.inbound ?? (r.tonnes?.inbound ?? 0);
      if (direction === 'balance') return dDict?.balance ?? (r.tonnes?.balance ?? 0);
      return dDict?.all ?? (isTkm ? (r.tkm?.total ?? 0) : (r.tonnes?.total ?? 0));
    }
  }

  // Für nationale Richtungs- oder Gütergruppenansichten werden die räumlich
  // zuordenbaren NUTS-3-Werte summiert. Transit und nicht zuordenbare
  // Sonderzellen bleiben dabei bewusst außerhalb dieses Filterumfangs.
  function getNationalForecastDirectionValues(sc, isTkm, direction, groupFilter) {
    const metricDirections = isTkm ? 'directions_tkm' : 'directions_tonnes';
    const metricModeDirections = isTkm ? 'modes_direction_tkm' : 'modes_direction_tonnes';
    const metricGroups = isTkm ? 'groups_7_tkm' : 'groups_7_tonnes';
    const metricModeGroups = isTkm ? 'modes_by_group_tkm' : 'modes_by_group_tonnes';
    const values = { total: 0, modes: { road: 0, rail: 0, iww: 0 } };

    Object.values(sc?.regions || {}).forEach(region => {
      if (groupFilter) {
        const groups = region?.[metricGroups] || {};
        values.total += Number(groups?.[direction]?.[groupFilter] || 0);
        const modeGroups = region?.[metricModeGroups]?.[groupFilter] || {};
        Object.keys(values.modes).forEach(mode => {
          values.modes[mode] += Number(modeGroups?.[mode]?.[direction] || 0);
        });
      } else {
        values.total += Number(region?.[metricDirections]?.[direction] || 0);
        const modeDirections = region?.[metricModeDirections] || {};
        Object.keys(values.modes).forEach(mode => {
          values.modes[mode] += Number(modeDirections?.[mode]?.[direction] || 0);
        });
      }
    });
    return values;
  }

  // Helper: Retrieve active forecast region data or national summary
  function getForecastActiveRegion() {
    if (!forecastData || !forecastData.scenarios) return null;
    const sc = forecastData.scenarios[state.forecastScenario] || forecastData.scenarios['2040_P1'];
    if (!sc) return null;

    if (!state.region) {
      return {
        isNational: true,
        data: sc.national,
        cellId: null,
        name: 'Deutschland (Gesamt)',
        choropleth: sc.choropleth
      };
    }

    const nutsId = state.region;
    const rData = sc.regions?.[nutsId];
    if (rData) {
      return {
        isNational: false,
        data: rData,
        cellId: nutsId,
        name: rData.name || regionsData[nutsId]?.name || nutsId,
        choropleth: sc.choropleth
      };
    }

    return {
      isNational: true,
      data: sc.national,
      cellId: null,
      name: 'Deutschland (Gesamt)',
      choropleth: sc.choropleth
    };
  }

  function getForecastScenarioMeta() {
    const fallback = state.forecastScenario === '2019_BASE'
      ? { id: '2019_BASE', year: 2019, is_forecast: false }
      : { id: '2040_P1', year: 2040, is_forecast: true };
    return forecastData?.metadata?.available_scenarios?.find(
      scenario => scenario.id === state.forecastScenario
    ) || fallback;
  }

  function getForecastScenarioLabel() {
    const scenario = getForecastScenarioMeta();
    return scenario.is_forecast
      ? `Prognose ${scenario.year} · Basis P1`
      : `Basisjahr ${scenario.year}`;
  }

  // The VP2040 matrices provide mode and NST-7 group on every record.  Keep
  // one retrieval path for all components so KPI cards, map tooltips and the
  // modal split always use the same group-filtered modal values.
  function getForecastModeValues(active, isTkm, direction, group) {
    const d = active?.data || {};
    const metric = isTkm ? 'tkm' : 'tonnes';
    const modes = ['road', 'rail', 'iww'];
    const values = {};

    if (group) {
      if (active?.isNational) {
        for (const mode of modes) values[mode] = d.modes_by_group?.[group]?.[mode]?.[metric];
      } else {
        const groupModes = (isTkm ? d.modes_by_group_tkm : d.modes_by_group_tonnes)?.[group] || {};
        for (const mode of modes) values[mode] = groupModes?.[mode]?.[direction];
      }
    } else if (active?.isNational) {
      for (const mode of modes) values[mode] = d.modes?.[mode]?.[metric];
    } else if (direction === 'outbound' || direction === 'inbound' || direction === 'balance') {
      const directionModes = isTkm ? d.modes_direction_tkm : d.modes_direction_tonnes;
      const fallbackModes = isTkm ? d.modes_tkm : d.modes_tonnes;
      for (const mode of modes) values[mode] = directionModes?.[mode]?.[direction] ?? fallbackModes?.[mode];
    } else {
      const allModes = isTkm ? d.modes_tkm : d.modes_tonnes;
      const fallbackValues = isTkm ? d.tkm : d.tonnes;
      for (const mode of modes) values[mode] = allModes?.[mode] ?? fallbackValues?.[mode];
    }

    return {
      available: modes.every(mode => Number.isFinite(values[mode])),
      road: values.road ?? 0,
      rail: values.rail ?? 0,
      iww: values.iww ?? 0
    };
  }

  // Values shown in a district hover must be derived from the same active
  // filters as the map.  KV detail remains available only for all goods;
  // modal values are also available for each NST-7 group.
  function getForecastRegionTooltipDetails(regInfo, isTkm) {
    const direction = state.direction || 'all';
    const hasGroupFilter = Boolean(state.selectedGroup && state.selectedGroup !== 'ALL');
    const group = hasGroupFilter ? state.selectedGroup : null;
    const metricDirections = group
      ? (isTkm ? regInfo?.groups_7_tkm : regInfo?.groups_7_tonnes)
      : (isTkm ? regInfo?.directions_tkm : regInfo?.directions_tonnes);
    const directionKey = direction === 'balance' ? 'balance' : direction;
    const modeData = getForecastModeValues({ isNational: false, data: regInfo }, isTkm, directionKey, group);
    const modeValues = ['road', 'rail', 'iww'].map(mode => {
      const raw = modeData[mode];
      return direction === 'balance' ? Math.abs(raw) : raw;
    });
    const modeTotal = modeValues.reduce((sum, value) => sum + Math.max(0, value), 0);
    const modalSplit = modeData.available && modeTotal > 0
      ? modeValues.map(value => value / modeTotal * 100)
      : null;

    const groupValue = directionName => group
      ? metricDirections?.[directionName]?.[group]
      : metricDirections?.[directionName];
    const outboundValue = groupValue('outbound') ?? 0;
    const inboundValue = groupValue('inbound') ?? 0;
    const binnenValue = groupValue('binnen') ?? 0;
    const balanceValue = groupValue('balance') ?? (outboundValue - inboundValue);
    const kv = regInfo?.kv || {};
    let kvTonnes = null;
    let kvTeu = null;
    if (!hasGroupFilter && !isTkm) {
      if (direction === 'outbound') {
        kvTonnes = kv.outbound_tonnes ?? 0;
        kvTeu = kv.outbound_teu ?? 0;
      } else if (direction === 'inbound') {
        kvTonnes = kv.inbound_tonnes ?? 0;
        kvTeu = kv.inbound_teu ?? 0;
      } else if (direction === 'balance') {
        kvTonnes = (kv.outbound_tonnes ?? 0) - (kv.inbound_tonnes ?? 0);
        kvTeu = (kv.outbound_teu ?? 0) - (kv.inbound_teu ?? 0);
      } else {
        kvTonnes = kv.tonnes ?? 0;
        kvTeu = kv.teu ?? 0;
      }
    }

    const selectedDirectionTotal = groupValue(directionKey)
      ?? groupValue('all')
      ?? (isTkm ? regInfo?.tkm?.total : regInfo?.tonnes?.total)
      ?? 0;
    const kvShare = kvTonnes !== null && Math.abs(selectedDirectionTotal) > 0
      ? Math.abs(kvTonnes) / Math.abs(selectedDirectionTotal) * 100
      : null;

    return {
      hasGroupFilter,
      modalSplit,
      outboundValue,
      inboundValue,
      binnenValue,
      balanceValue,
      kvTonnes,
      kvTeu,
      kvShare
    };
  }

  function setForecastChartEmptyState(canvas, message) {
    const chartWrap = canvas?.closest('.chart-canvas-wrap');
    if (!canvas || !chartWrap) return;
    let note = chartWrap.querySelector('.chart-empty-state');
    if (!message) {
      canvas.hidden = false;
      note?.remove();
      return;
    }
    canvas.hidden = true;
    if (!note) {
      note = document.createElement('div');
      note.className = 'chart-empty-state';
      chartWrap.appendChild(note);
    }
    note.textContent = message;
  }

  // Keep the rich regional hover card inside the visible Leaflet viewport.
  // Leaflet's built-in "auto" direction only decides left versus right; it
  // does not account for the height of this tooltip.  Test the rendered card
  // against the map frame and flip it vertically only when it would be cut off.
  function fitForecastRegionTooltip(map, layer) {
    const tooltip = layer.getTooltip?.();
    const tooltipEl = tooltip?.getElement?.();
    const mapEl = map?.getContainer?.();
    if (!tooltip || !tooltipEl || !mapEl) return;

    const mapRect = mapEl.getBoundingClientRect();
    const inset = 8;
    const anchor = map.latLngToContainerPoint(tooltip.getLatLng());
    const spaceAbove = anchor.y - inset;
    const spaceBelow = mapRect.height - anchor.y - inset;
    const preferredDirection = spaceAbove >= spaceBelow ? 'top' : 'bottom';

    if (tooltip.options.direction !== preferredDirection) {
      tooltip.options.direction = preferredDirection;
      tooltip.options.offset = L.point(0, preferredDirection === 'top' ? -10 : 10);
      tooltip.setLatLng(tooltip.getLatLng());
    }

    // Choosing north or south alone is insufficient when a long card is near
    // an edge. Clamp Leaflet's positioned element into the actual map frame.
    const tipRect = tooltipEl.getBoundingClientRect();
    let shiftX = 0;
    let shiftY = 0;
    if (tipRect.left < mapRect.left + inset) shiftX = mapRect.left + inset - tipRect.left;
    else if (tipRect.right > mapRect.right - inset) shiftX = mapRect.right - inset - tipRect.right;
    if (tipRect.top < mapRect.top + inset) shiftY = mapRect.top + inset - tipRect.top;
    else if (tipRect.bottom > mapRect.bottom - inset) shiftY = mapRect.bottom - inset - tipRect.bottom;
    if (shiftX || shiftY) {
      const position = L.DomUtil.getPosition(tooltipEl);
      if (position) L.DomUtil.setPosition(tooltipEl, position.add(L.point(shiftX, shiftY)));
    }
  }

  // Master Forecast Tab Renderer
  function renderForecastTab() {
    if (!forecastData) return;
    const active = getForecastActiveRegion();
    if (!active) return;

    // Der gemeinsame Richtungsfilter bleibt auch bei Deutschland aktiv. Bei
    // Versand, Empfang und Saldo werden Karte und KPI aus den räumlich
    // zuordenbaren NUTS-3-Werten abgeleitet; Gesamt bleibt die volle Matrix.
    const directionSelect = document.getElementById('selectDirection');
    if (directionSelect) {
      directionSelect.disabled = false;
      directionSelect.title = '';
    }

    renderForecastKpis(active);
    updateForecastLeafletMap(active);
    renderForecastSpiderLines(active);
    drawSelectedRegionOutline('forecast');
    renderForecastTopRelationsTable(active);
    renderForecastModalSplitChart(active);
    renderForecastCommodityKvChart(active);
  }

  // Render 4 Forecast KPI Cards (Filtered by Direction, Commodity Group, Metric)
  function renderForecastKpis(active) {
    active = active || getForecastActiveRegion();
    if (!active) return;

    const isTkm = state.metric === 'tkm';
    const divisor = isTkm ? 1e9 : 1e6;
    const unitLabel = isTkm ? 'Mrd. tkm' : 'Mio. t';
    const d = active.data || {};

    const setTxt = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
    const setHtml = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };

    const grp = (state.selectedGroup && state.selectedGroup !== 'ALL') ? state.selectedGroup : null;
    const dir = state.direction || 'all';
    const scenario = getForecastScenarioMeta();
    const isBaseline = !scenario.is_forecast;
    const scenarioData = forecastData?.scenarios?.[state.forecastScenario] || forecastData?.scenarios?.['2040_P1'];
    const nationalFilteredScope = active.isNational && (dir !== 'all' || grp);
    const scopedValues = nationalFilteredScope
      ? getNationalForecastDirectionValues(scenarioData, isTkm, dir, grp)
      : null;

    // KPI 1: Gesamtaufkommen 2040
    let totVal = 0;
    if (nationalFilteredScope) {
      totVal = scopedValues.total;
    } else if (active.isNational) {
      if (grp) {
        const item = d.nst_groups_7?.[grp] || {};
        totVal = isTkm ? (item.tkm || 0) : (item.tonnes || 0);
      } else {
        totVal = isTkm ? (d.total_tkm || 0) : (d.total_tonnes || 0);
      }
    } else {
      if (grp) {
        const gDict = isTkm ? d.groups_7_tkm : d.groups_7_tonnes;
        if (dir === 'outbound') totVal = gDict?.outbound?.[grp] ?? 0;
        else if (dir === 'inbound') totVal = gDict?.inbound?.[grp] ?? 0;
        else if (dir === 'balance') totVal = gDict?.balance?.[grp] ?? 0;
        else totVal = gDict?.all?.[grp] ?? (gDict?.[grp] ?? 0);
      } else {
        const dDict = isTkm ? d.directions_tkm : d.directions_tonnes;
        if (dir === 'outbound') totVal = dDict?.outbound ?? (d.tonnes?.outbound ?? 0);
        else if (dir === 'inbound') totVal = dDict?.inbound ?? (d.tonnes?.inbound ?? 0);
        else if (dir === 'balance') totVal = dDict?.balance ?? (d.tonnes?.balance ?? 0);
        else totVal = dDict?.all ?? (isTkm ? (d.tkm?.total ?? 0) : (d.tonnes?.total ?? 0));
      }
    }

    const directionSuffix = dir === 'balance' ? ' (Saldo)'
      : dir === 'outbound' ? ' (Versand)'
      : dir === 'inbound' ? ' (Empfang)'
      : '';
    // Only the national filtered scope omits foreign-to-foreign transit.
    // Further filter settings are intentionally kept out of the KPI titles.
    const scopeSuffix = nationalFilteredScope ? ' ohne Transit' : '';
    setTxt('kpiForecastTotalTitle', `Gesamtaufkommen${scopeSuffix}${directionSuffix}`);
    const formatKpiValue = value => `${dir === 'balance' && value > 0 ? '+' : ''}${formatTrafficValue(value / divisor, unitLabel, 2)} ${unitLabel}`;
    setTxt('kpiForecastTotalTonnes', formatKpiValue(totVal));
    
    let totGrowthVal, roadGrowthVal, railGrowthVal, iwwGrowthVal;
    if (isBaseline) {
      totGrowthVal = roadGrowthVal = railGrowthVal = iwwGrowthVal = null;
    } else if (nationalFilteredScope) {
      const baselineData = forecastData?.scenarios?.['2019_BASE'];
      const baselineValues = getNationalForecastDirectionValues(baselineData, isTkm, dir, grp);
      const growth = (current, baseline) => baseline > 0 ? ((current - baseline) / baseline) * 100 : null;
      totGrowthVal = growth(scopedValues.total, baselineValues.total);
      roadGrowthVal = growth(scopedValues.modes.road, baselineValues.modes.road);
      railGrowthVal = growth(scopedValues.modes.rail, baselineValues.modes.rail);
      iwwGrowthVal = growth(scopedValues.modes.iww, baselineValues.modes.iww);
    } else if (active.isNational) {
      const nationalGroup = grp ? d.nst_groups_7?.[grp] : null;
      const nationalModes = grp ? d.modes_by_group?.[grp] : d.modes;
      totGrowthVal = nationalGroup
        ? (isTkm ? nationalGroup.growth_2019_tkm_pct : nationalGroup.growth_2019_tonnes_pct)
        : (isTkm ? d.growth_2019_tkm_pct : d.growth_2019_tonnes_pct);
      roadGrowthVal = isTkm ? nationalModes?.road?.growth_2019_tkm_pct : nationalModes?.road?.growth_2019_tonnes_pct;
      railGrowthVal = isTkm ? nationalModes?.rail?.growth_2019_tkm_pct : nationalModes?.rail?.growth_2019_tonnes_pct;
      iwwGrowthVal = isTkm ? nationalModes?.iww?.growth_2019_tkm_pct : nationalModes?.iww?.growth_2019_tonnes_pct;
    } else {
      const regionalGrowth = d.growth_2019?.[isTkm ? 'tkm' : 'tonnes'] || {};
      totGrowthVal = grp
        ? regionalGrowth.groups_7?.[dir]?.[grp]
        : regionalGrowth.directions?.[dir];
      roadGrowthVal = grp ? regionalGrowth.modes_by_group?.[grp]?.road?.[dir] : regionalGrowth.modes?.road;
      railGrowthVal = grp ? regionalGrowth.modes_by_group?.[grp]?.rail?.[dir] : regionalGrowth.modes?.rail;
      iwwGrowthVal = grp ? regionalGrowth.modes_by_group?.[grp]?.iww?.[dir] : regionalGrowth.modes?.iww;
    }

    const fmtGrowthBadge = (gVal) => {
      if (isBaseline) return '<span style="color:#64748b; font-size:0.75rem; font-weight:600;">Basisjahr 2019</span>';
      if (dir === 'balance') return '<span style="color:#64748b; font-size:0.75rem; font-weight:600;">Saldo ohne Zeitvergleich</span>';
      if (gVal === null || gVal === undefined || isNaN(gVal)) return '<span style="color:#64748b; font-size:0.75rem; font-weight:600;">2019: kein Vergleichswert</span>';
      if (gVal > 0.05) return `<span style="color:#16a34a; font-size:0.75rem; font-weight:700;">↗ +${formatDeNum(gVal, 1)} % ggü. 2019</span>`;
      if (gVal < -0.05) return `<span style="color:#dc2626; font-size:0.75rem; font-weight:700;">↘ ${formatDeNum(gVal, 1)} % ggü. 2019</span>`;
      return '<span style="color:#64748b; font-size:0.75rem; font-weight:600;">→ 0,0 % ggü. 2019</span>';
    };

    setHtml('kpiForecastTotalSub', fmtGrowthBadge(totGrowthVal));

    const modeValues = nationalFilteredScope
      ? { available: true, ...scopedValues.modes }
      : getForecastModeValues(active, isTkm, dir, grp);

    setTxt('kpiForecastRoadTitle', `Straße (LKW)${scopeSuffix}${directionSuffix}`);
    setTxt('kpiForecastRailTitle', `Schiene (Bahn)${scopeSuffix}${directionSuffix}`);
    setTxt('kpiForecastIwwTitle', `Wasserstraße (Binnenschiff)${scopeSuffix}${directionSuffix}`);

    const noModeBreakdown = '<span style="color:#64748b; font-size:0.75rem; font-weight:600;">Keine Verkehrsträger-Aufteilung für diese Gütergruppe</span>';
    if (!modeValues.available) {
      setTxt('kpiForecastRoadTonnes', '—');
      setHtml('kpiForecastRoadShare', noModeBreakdown);
      setTxt('kpiForecastRailTonnes', '—');
      setHtml('kpiForecastRailShare', noModeBreakdown);
      setTxt('kpiForecastIwwTonnes', '—');
      setHtml('kpiForecastIwwShare', noModeBreakdown);
    } else {
      setTxt('kpiForecastRoadTonnes', formatKpiValue(modeValues.road));
      setHtml('kpiForecastRoadShare', fmtGrowthBadge(roadGrowthVal));
      setTxt('kpiForecastRailTonnes', formatKpiValue(modeValues.rail));
      setHtml('kpiForecastRailShare', fmtGrowthBadge(railGrowthVal));
      setTxt('kpiForecastIwwTonnes', formatKpiValue(modeValues.iww));
      setHtml('kpiForecastIwwShare', fmtGrowthBadge(iwwGrowthVal));
    }
  }

  // Update Forecast Leaflet Map with Linked Filters & Rich Interactive Tooltips
  function updateForecastLeafletMap(active) {
    active = active || getForecastActiveRegion();
    const map = maps.forecast;
    if (!map || !geojsonNuts3) return;

    const isTkm = state.metric === 'tkm';
    const divisor = isTkm ? 1e9 : 1e6;
    const unitLabel = isTkm ? 'Mrd. tkm' : 'Mio. t';
    const isBalance = (state.direction === 'balance');
    const sc = forecastData?.scenarios?.[state.forecastScenario] || forecastData?.scenarios?.['2040_P1'];

    // Compute choropleth dictionary for current filter state across all 400 districts
    const choroDict = {};
    const features = geojsonNuts3.features || [];
    features.forEach(f => {
      const nId = f.properties?.NUTS_ID || f.properties?.id;
      if (nId) {
        choroDict[nId] = getForecastChoroplethVal(nId, sc, isTkm, state.direction, state.selectedGroup);
      }
    });

    let maxVal = 1000;
    if (isBalance) {
      const absVals = Object.values(choroDict).map(v => Math.abs(v)).filter(v => v > 0).sort((a, b) => a - b);
      const p90 = absVals.length > 0 ? absVals[Math.floor(absVals.length * 0.90)] : 5e6;
      maxVal = Math.max(p90, 1000);
      updateMapLegend('forecast', null, true, maxVal);
    } else {
      const posVals = Object.values(choroDict).filter(v => v > 0).sort((a, b) => a - b);
      const p90 = posVals.length > 0 ? posVals[Math.floor(posVals.length * 0.90)] : 25e6;
      maxVal = Math.max(p90, 1000);
      updateMapLegend('forecast', null, false, maxVal);
    }

    if (mapLayers.forecast.geojson) {
      map.removeLayer(mapLayers.forecast.geojson);
      mapLayers.forecast.geojson = null;
    }

    const activeRegionId = state.region;

    const getForecastChoroColor = (val) => {
      if (isBalance) {
        if (!val || Math.abs(val) < 100) return '#f8fafc';
        const ratio = Math.min(1, Math.abs(val) / maxVal);
        if (val > 0) {
          // Netto-Versand / Export (Subtle Green)
          if (ratio < 0.20) return '#f0fdf4';
          if (ratio < 0.45) return '#dcfce7';
          if (ratio < 0.75) return '#86efac';
          return '#22c55e';
        } else {
          // Netto-Empfang / Import (Subtle Blue)
          if (ratio < 0.20) return '#f0f9ff';
          if (ratio < 0.45) return '#e0f2fe';
          if (ratio < 0.75) return '#7dd3fc';
          return '#38bdf8';
        }
      } else {
        // Subtle, discreet sky-slate palette
        if (!val || val <= 0) return '#f8fafc';
        const ratio = Math.min(1, val / maxVal);
        if (ratio < 0.12) return '#f8fafc';
        if (ratio < 0.30) return '#e0f2fe';
        if (ratio < 0.55) return '#bae6fd';
        if (ratio < 0.85) return '#60a5fa';
        return '#2563eb';
      }
    };

    mapLayers.forecast.geojson = L.geoJSON(geojsonNuts3, {
      renderer: getNutsRegionRenderer(map),
      style: (feature) => {
        const nutsId = feature.properties.NUTS_ID || feature.properties.id;
        const val = choroDict[nutsId] || 0;
        const isSelected = activeRegionId && (activeRegionId === nutsId);
        const fillColor = getForecastChoroColor(val);

        return {
          fillColor: fillColor,
          weight: isSelected ? 3.5 : 0.75,
          opacity: 1,
          color: isSelected ? '#0f172a' : '#94a3b8',
          fillOpacity: isSelected ? 0.90 : 0.68
        };
      },
      onEachFeature: (feature, layer) => {
        const nutsId = feature.properties.NUTS_ID || feature.properties.id;
        const isSelected = Boolean(activeRegionId && activeRegionId === nutsId);
        const cName = feature.properties.NUTS_NAME || feature.properties.name || regionsData[nutsId]?.name || nutsId;
        const regInfo = sc?.regions?.[nutsId];
        const val = choroDict[nutsId] || 0;

        const details = getForecastRegionTooltipDetails(regInfo, isTkm);

        let dirText = 'Gesamtaufkommen';
        if (state.direction === 'outbound') dirText = 'Versand (Güterausgang)';
        else if (state.direction === 'inbound') dirText = 'Empfang (Gütereingang)';
        else if (state.direction === 'balance') dirText = 'Verkehrssaldo (Netto)';

        let grpBadge = '';
        if (state.selectedGroup && state.selectedGroup !== 'ALL') {
          grpBadge = `<div class="map-tooltip-context">Güterart: ${NST_GROUPS_7[state.selectedGroup]}</div>`;
        }

        const balStatus = details.balanceValue > 0
          ? 'Versandüberschuss'
          : details.balanceValue < 0
            ? 'Empfangsüberschuss'
            : 'Ausgeglichen';
        const balSign = details.balanceValue > 0 ? '+' : '';
        const metricLabel = isTkm ? 'Verkehrsleistung' : 'Beförderungsmenge';
        const goodsScope = details.hasGroupFilter ? NST_GROUPS_7[state.selectedGroup] : 'alle Güter';
        const directionHtml = `<div><strong>${metricLabel} (${goodsScope}):</strong> Versand ${formatTrafficValue(details.outboundValue / divisor, unitLabel, 2)} ${unitLabel} | Empfang ${formatTrafficValue(details.inboundValue / divisor, unitLabel, 2)} ${unitLabel} | Binnenverkehr ${formatTrafficValue(details.binnenValue / divisor, unitLabel, 2)} ${unitLabel}</div>
          <div class="forecast-total-definition"><strong>Gesamtaufkommen:</strong> Versand + Empfang + Binnenverkehr</div>
          <div><strong>Netto-Saldo:</strong> ${balSign}${formatTrafficValue(details.balanceValue / divisor, unitLabel, 2)} ${unitLabel} (${balStatus}; Binnenverkehr nicht saldowirksam)</div>`;
        const modalHtml = details.modalSplit
          ? `<div><strong>${state.direction === 'balance' ? 'Modalstruktur des Saldos (Beträge)' : 'Modal Split'}:</strong> Straße ${formatDeNum(details.modalSplit[0], 1)} % | Schiene ${formatDeNum(details.modalSplit[1], 1)} % | Binnenschiff ${formatDeNum(details.modalSplit[2], 1)} %</div>`
          : '';
        const kvQuantityLabel = state.direction === 'outbound' ? 'Versand'
          : state.direction === 'inbound' ? 'Empfang'
          : state.direction === 'balance' ? 'Nettosaldo'
          : 'Gesamtaufkommen';
        const kvShareLabel = state.direction === 'outbound' ? 'der Beförderungsmenge im Versand'
          : state.direction === 'inbound' ? 'der Beförderungsmenge im Empfang'
          : 'der gesamten Beförderungsmenge';
        const kvShareHtml = details.kvShare !== null && state.direction !== 'balance'
          ? ` (${formatDeNum(details.kvShare, 1)} % ${kvShareLabel})`
          : '';
        const kvHtml = details.kvTonnes !== null && details.kvTeu !== null
          ? `<div style="margin-top:6px;"><strong>Kombinierter Verkehr:</strong><div><strong>${kvQuantityLabel}:</strong> ${formatDeNum(details.kvTonnes / 1e6, 2)} Mio. t${kvShareHtml}</div><div><strong>TEU:</strong> ${formatDeNum(details.kvTeu / 1e3, 1)} Tsd. TEU</div></div>`
          : '';

        const tipHtml = `
          <div class="map-region-tooltip">
            <div class="map-tooltip-title">${cName} <span>(${nutsId})</span></div>
            <div class="map-tooltip-meta">${getForecastScenarioLabel()} · ${dirText}</div>
            <div class="map-tooltip-value">${isTkm ? 'Verkehrsleistung' : 'Beförderungsmenge'}: ${formatTrafficValue(val / divisor, unitLabel, 2)} ${unitLabel}</div>
            ${grpBadge}
            <div class="map-tooltip-context">
              ${directionHtml}
              ${modalHtml}
              ${kvHtml}
            </div>
            <div class="map-tooltip-filter-hint">Klicken Sie, um diese Region/diesen Kreis als Filter zu aktivieren.</div>
          </div>
        `;
        layer.bindTooltip(tipHtml, {
          sticky: true,
          direction: 'top',
          offset: [0, -10],
          className: 'forecast-region-leaflet-tooltip'
        });
        delayRegionTooltip(layer);
        layer.on('tooltipopen', () => {
          requestAnimationFrame(() => fitForecastRegionTooltip(map, layer));
        });
        layer.on('mousemove', () => fitForecastRegionTooltip(map, layer));

        if (isSelected && layer.bringToFront) {
          setTimeout(() => { if (layer.bringToFront) layer.bringToFront(); }, 0);
        }

        layer.on('click', async () => {
          await setRegion(nutsId);
        });
      }
    }).addTo(map);

    renderStateBoundaries('forecast');

    if (activeRegionId && mapLayers.forecast.geojson) {
      mapLayers.forecast.geojson.eachLayer(l => {
        const nId = l.feature?.properties?.NUTS_ID || l.feature?.properties?.id;
        if (nId === activeRegionId && l.bringToFront) {
          l.bringToFront();
        }
      });
    }
  }

  function getForecastRelationRows(active) {
    const relationSource = (state.selectedGroup && state.selectedGroup !== 'ALL')
      ? active?.data?.by_group_relations?.[state.selectedGroup]
      : active?.data?.relations_overall;
    if (!relationSource) return [];

    if (state.direction === 'balance') {
      return mergeDirectionalRelations(relationSource.outbound || [], relationSource.inbound || [], {
        group: state.selectedGroup || 'ALL',
        asBalance: true
      });
    }
    if (state.direction === 'outbound' || state.direction === 'inbound') {
      return [...(relationSource[state.direction] || [])];
    }
    // The supplied all-direction list avoids double-counting Binnenverkehr.
    return [...(relationSource.all || [])];
  }

  function getForecastRelationCellName(cellId, relation = null) {
    if (!cellId) return '';
    const partnerId = relation?.partner_id || relation?.dest_id || relation?.orig_id;
    if (relation?.partner_name && String(cellId) === String(partnerId)) return relation.partner_name;
    return regionsData[cellId]?.name
      || fullCentroids[cellId]?.name
      || centroidsVp2040[cellId]?.name
      || String(cellId);
  }

  // Render Forecast Spider Lines (Uniform Royal Violet Color with High Contrast)
  function renderForecastSpiderLines(active) {
    active = active || getForecastActiveRegion();
    const map = maps.forecast;
    if (!map) return;
    bindMapHighlightReset('forecast');

    if (!mapLayers.forecast.spiderGroup) {
      mapLayers.forecast.spiderGroup = L.layerGroup().addTo(map);
    } else {
      mapLayers.forecast.spiderGroup.clearLayers();
    }
    mapLayers.forecast.spiderLookup = {};

    // If spider toggled off OR Deutschland (national) active, do NOT draw lines!
    if (!state.showForecastSpider || !state.region || !active || active.isNational) {
      return;
    }

    const isTkm = state.metric === 'tkm';
    const unitLabel = isTkm ? 'Mio. tkm' : 'Tsd. t';
    
    const rawRelations = getForecastRelationRows(active);

    if (!rawRelations || rawRelations.length === 0) return;

    // Filter Binnenverkehr if toggled off
    let fl = [...rawRelations];
    if (!state.includeBinnen) {
      fl = fl.filter(r => !r.is_binnen && (r.partner_id !== state.region) && (r.dest_id !== state.region));
    }

    const relationAmount = relation => isTkm ? (relation.tkm || 0) : (relation.tonnes || 0);
    fl.sort((a, b) => state.direction === 'balance'
      ? Math.abs(relationAmount(b)) - Math.abs(relationAmount(a))
      : relationAmount(b) - relationAmount(a));
    const relations = fl.slice(0, state.topX || 10);
    if (relations.length === 0) return;

    const cls = getFlowClassification(relations, isTkm);

    // Uniform high-contrast royal violet color across ordinary relations.
    const FORECAST_SPIDER_COLOR = '#7c3aed';

    relations.forEach(rel => {
      let origId = state.region;
      let destId = rel.partner_id || rel.dest_id;

      if (state.direction === 'inbound') {
        origId = rel.partner_id || rel.dest_id;
        destId = state.region;
      }

      if (!origId || !destId || origId === destId) return;

      const origCoord = fullCentroids[origId] || centroidsVp2040[origId] || regionsData[origId];
      const destCoord = fullCentroids[destId] || centroidsVp2040[destId] || regionsData[destId];

      if (!origCoord || !destCoord || !origCoord.lat || !destCoord.lat) return;

      const vol = isTkm ? (rel.tkm || 0) : (rel.tonnes || 0);
      const weight = cls.getWeight(vol);
      const radius = cls.getRadius(vol);

      const lineColor = state.direction === 'balance'
        ? (vol >= 0 ? '#16a34a' : '#7c3aed')
        : FORECAST_SPIDER_COLOR;
      const line = L.polyline([
        [origCoord.lat, origCoord.lng],
        [destCoord.lat, destCoord.lng]
      ], {
        pane: 'connectionPane',
        className: 'flow-relation-target',
        color: lineColor,
        weight: weight,
        opacity: 0.88
      }).addTo(mapLayers.forecast.spiderGroup);

      // For incoming relations the destination is the selected region.  The
      // endpoint marker must nevertheless remain at the partner so that both
      // direction settings show the external connection point.
      const partnerId = rel.partner_id || (state.direction === 'inbound' ? origId : destId);
      const partnerCoord = fullCentroids[partnerId] || centroidsVp2040[partnerId] || regionsData[partnerId];
      if (!partnerCoord || !partnerCoord.lat) return;
      const marker = L.circleMarker([partnerCoord.lat, partnerCoord.lng], {
        pane: 'connectionPane',
        className: 'flow-relation-target',
        radius: radius,
        fillColor: lineColor,
        color: '#ffffff',
        weight: 2.2,
        fillOpacity: 0.95
      }).addTo(mapLayers.forecast.spiderGroup);

      const lookupKey = partnerId;
      mapLayers.forecast.spiderLookup[lookupKey] = { line, marker, originalColor: lineColor, originalWeight: weight };

      const displayVol = isTkm ? vol / 1e6 : vol / 1e3;
      const formattedVol = `${state.direction === 'balance' && displayVol > 0 ? '+' : ''}${isTkm ? formatTkmQuantity(displayVol, 1, true) : formatQuantity(displayVol, 1)}`;
      const pName = getForecastRelationCellName(lookupKey, rel);
      const oName = String(origId) === String(lookupKey) ? pName : getForecastRelationCellName(origId);
      const dName = String(destId) === String(lookupKey) ? pName : getForecastRelationCellName(destId);
      const gName = (state.selectedGroup && state.selectedGroup !== 'ALL') ? (NST_GROUPS_7[state.selectedGroup] || rel.group_name) : 'Alle Güter';

      let modeBadges = '';
      if (rel.modes_list && rel.modes_list.length > 0) {
        modeBadges = rel.modes_list.map(m => {
          if (m === 'rail') return '<span class="badge-mode badge-mode-rail">Schiene</span>';
          if (m === 'iww') return '<span class="badge-mode badge-mode-iww">Binnenschiff</span>';
          if (m === 'road') return '<span class="badge-mode badge-mode-road">Straße</span>';
          return '';
        }).join(' ');
      }

      const kvInfo = rel.teu > 0 
        ? `<div class="flow-tooltip-context"><strong>Containerladung:</strong> ${formatQuantity(rel.teu / 1e3, 1)} Tsd. TEU · ${formatQuantity(rel.tonnes / 1e3, 1)} Tsd. t</div>` 
        : '';

      const outboundValue = isTkm ? (rel.outbound_tkm || 0) / 1e6 : (rel.outbound_tonnes || 0) / 1e3;
      const inboundValue = isTkm ? (rel.inbound_tkm || 0) / 1e6 : (rel.inbound_tonnes || 0) / 1e3;
      const balanceHtml = state.direction === 'balance' ? `
        <div class="flow-tooltip-context"><strong>Versand:</strong> ${isTkm ? formatTkmQuantity(outboundValue, 1, true) : formatQuantity(outboundValue, 1)} ${unitLabel}<br>
          <strong>Empfang:</strong> ${isTkm ? formatTkmQuantity(inboundValue, 1, true) : formatQuantity(inboundValue, 1)} ${unitLabel}<br>
          <strong>Saldo:</strong> ${formattedVol} ${unitLabel} · ${displayVol >= 0 ? 'Versandüberschuss' : 'Empfangsüberschuss'}</div>` : '';

      const routeArrow = (state.direction === 'all' || state.direction === 'balance') ? '↔' : '→';
      const metricLabel = isTkm ? 'Verkehrsleistung' : 'Beförderungsmenge';
      const tipHtml = `
        <div class="flow-relation-tooltip">
          <div class="flow-tooltip-eyebrow">
            Güterverbindung ${getForecastScenarioLabel()}
          </div>
          <div class="flow-tooltip-route">${oName} <span>${routeArrow}</span> ${dName}</div>
          <div><strong>Güterart:</strong> ${gName}</div>
          <div class="flow-tooltip-value">
            ${state.direction === 'balance' ? 'Nettosaldo' : metricLabel}: ${formattedVol} ${unitLabel}
          </div>
          ${balanceHtml}
          ${modeBadges ? `<div class="flow-tooltip-modes"><strong>Verkehrsträger:</strong> ${modeBadges}</div>` : ''}
          ${kvInfo}
        </div>
      `;

      const relationTooltipOptions = {
        sticky: true,
        opacity: 0.98,
        className: 'forecast-relation-leaflet-tooltip'
      };
      line.bindTooltip(tipHtml, relationTooltipOptions);
      marker.bindTooltip(tipHtml, relationTooltipOptions);

      line.on('mouseover', event => {
        openActiveRelationTooltip('forecast', line, event);
        setHighlight('forecast', lookupKey);
      });
      line.on('mouseout', () => {
        closeActiveRelationTooltip('forecast');
        clearAllHighlights('forecast');
      });
      marker.on('mouseover', event => {
        openActiveRelationTooltip('forecast', marker, event);
        setHighlight('forecast', lookupKey);
      });
      marker.on('mouseout', () => {
        closeActiveRelationTooltip('forecast');
        clearAllHighlights('forecast');
      });
    });
  }

  // Render Forecast Top Relations Table (Clean Numbers in Quantity Column, Linked Filters)
  function renderForecastTopRelationsTable(active) {
    active = active || getForecastActiveRegion();
    const tbody = document.getElementById('tableForecastRelationsBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    const isTkm = state.metric === 'tkm';
    const scenario = getForecastScenarioMeta();
    const isBaseline = !scenario.is_forecast;
    const thUnitEl = document.getElementById('thForecastMetricUnit');
    if (thUnitEl) {
      thUnitEl.textContent = state.direction === 'balance'
        ? (isTkm ? 'Saldo (in Mio. tkm)' : 'Saldo (in 1.000 Tonnen)')
        : (isTkm ? 'Verkehrsleistung (in Mio. tkm)' : 'Menge (in 1.000 Tonnen)');
      thUnitEl.title = thUnitEl.textContent;
    }
    const thChangeEl = document.getElementById('thForecastChange');
    if (thChangeEl) {
      thChangeEl.innerHTML = isBaseline ? 'Basisjahr<br><span>2019</span>' : 'Δ<br><span>ggü. 2019</span>';
      thChangeEl.title = isBaseline ? 'Ausgewähltes Basisjahr für den Vergleich' : 'Veränderung gegenüber dem Basisjahr 2019';
    }

    if (!state.region || !active || active.isNational) {
      const nationalScopeText = state.direction === 'all'
        ? 'Die nationalen Kennzahlen werden direkt aus den vollständigen VP2040-Matrizen gebildet. Die Verkehrsleistung (Tkm) ist dabei die inländische Transportleistung. Die Matrizen enthalten auch Transitverkehre und Sonderzellen; diese sind keiner deutschen Region zugeordnet und erscheinen daher nicht in regionalen Relationen.'
        : 'Bei Versand, Empfang und Saldo zeigen Karte und Kennzahlen die räumlich zuordenbaren NUTS-3-Werte. Transit und nicht regional zuordenbare Sonderzellen bleiben in diesem Richtungsumfang unberücksichtigt.';
      tbody.innerHTML = `
        <tr>
          <td colspan="4" style="text-align:center; color:#475569; padding:28px 16px; font-size:0.86rem; line-height:1.6;">
            <div class="empty-state-icon"><img src="assets/icons/map.svg" alt="" aria-hidden="true"></div>
            <strong style="color:#0f172a; font-size:0.95rem;">Deutschland aktiv</strong><br>
            <span style="color:#64748b; font-size:0.81rem;">Bitte wählen Sie in der Karte per <strong>Mausklick eine Region</strong> aus oder öffnen Sie <strong>Aktuelle Einstellungen → Raum &amp; Zeit</strong> und wählen Sie dort eine Region aus, um relationale Verflechtungen und Partnerregionen anzuzeigen.</span><br><br>
            <span style="color:#475569; font-size:0.79rem;">${nationalScopeText}</span>
          </td>
        </tr>
      `;
      return;
    }

    const rawRelations = getForecastRelationRows(active);

    // Filter Binnenverkehr if unchecked
    let list = [...rawRelations];
    if (!state.includeBinnen) {
      list = list.filter(r => !r.is_binnen && (r.partner_id !== state.region) && (r.dest_id !== state.region));
    }

    const relationAmount = relation => isTkm ? (relation.tkm || 0) : (relation.tonnes || 0);
    list.sort((a, b) => state.direction === 'balance'
      ? Math.abs(relationAmount(b)) - Math.abs(relationAmount(a))
      : relationAmount(b) - relationAmount(a));
    const relations = list.slice(0, state.topX || 10);

    if (relations.length === 0) {
      const groupText = (state.selectedGroup && state.selectedGroup !== 'ALL') ? ` für <strong>${NST_GROUPS_7[state.selectedGroup]}</strong>` : '';
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#64748b; padding:24px; font-size:0.85rem; line-height:1.5;">Für die ausgewählte Region wurden im ${getForecastScenarioLabel()}${groupText} keine bilateralen Verflechtungsdaten ermittelt.</td></tr>`;
      return;
    }

    relations.forEach((r, rank) => {
      const pId = r.partner_id || r.dest_id || r.orig_id;
      const pName = getForecastRelationCellName(pId, r);
      const groupName = (state.selectedGroup && state.selectedGroup !== 'ALL') 
        ? (NST_GROUPS_7[state.selectedGroup] || r.group_name || `Gruppe ${state.selectedGroup}`) 
        : 'Alle Güter';
      
      const val = isTkm ? (r.tkm || 0) / 1e6 : (r.tonnes || 0) / 1e3;
      const cleanValNum = `${state.direction === 'balance' && val > 0 ? '+' : ''}${isTkm ? formatTkmQuantity(val, 1, true) : formatQuantity(val, 1)}`;

      const binnenBadge = r.is_binnen ? '<span style="font-size:0.7rem; background:#e2e8f0; color:#475569; padding:1px 5px; border-radius:4px; margin-left:4px;">Binnen</span>' : '';

      let modeBadge = '';
      if (r.modes_list && r.modes_list.length > 0) {
        modeBadge = r.modes_list.map(m => {
          if (m === 'rail') return '<span class="badge-mode badge-mode-rail">Schiene</span>';
          if (m === 'iww') return '<span class="badge-mode badge-mode-iww">Binnenschiff</span>';
          if (m === 'road') return '<span class="badge-mode badge-mode-road">Straße</span>';
          return '';
        }).join('');
      } else if (r.mode === 'rail') modeBadge = '<span class="badge-mode badge-mode-rail">Schiene</span>';
      else if (r.mode === 'iww') modeBadge = '<span class="badge-mode badge-mode-iww">Binnenschiff</span>';
      else if (r.mode === 'road') modeBadge = '<span class="badge-mode badge-mode-road">Straße</span>';

      const growthVal = r.growth_2019?.[isTkm ? 'tkm' : 'tonnes'] ?? r.growth_2019_pct;
      const growthHtml = isBaseline
        ? '<span style="color:#64748b;">Basisjahr</span>'
        : state.direction === 'balance'
        ? '<span style="color:#64748b;" title="Für Salden wird kein prozentualer Zeitvergleich ausgewiesen.">—</span>'
        : (growthVal !== null && growthVal !== undefined)
        ? `<span style="color:${growthVal >= 0 ? '#16a34a' : '#dc2626'}; font-weight:700;">${growthVal >= 0 ? '↗ +' : '↘ '}${formatDeNum(growthVal, 1)} %</span>`
        : '<span style="color:#94a3b8;">--</span>';

      const row = document.createElement('tr');
      row.setAttribute('data-partner-id', pId);
      row.innerHTML = `
        <td class="relation-partner-cell"><span class="relation-rank" aria-label="Rang ${rank + 1}">${rank + 1}<span class="relation-rank-separator" aria-hidden="true">·</span></span><span class="relation-partner-details"><strong>${pName}</strong><span class="table-sub-label">(${pId})</span>${binnenBadge}${modeBadge ? `<span class="relation-mode-badges">${modeBadge}</span>` : ''}</span></td>
        <td>${groupName}</td>
        <td style="text-align: right;"><strong>${cleanValNum}</strong></td>
        <td style="text-align: right;">${growthHtml}</td>
      `;

      row.addEventListener('mouseenter', () => setHighlight('forecast', pId));
      row.addEventListener('mouseleave', () => clearAllHighlights('forecast'));

      tbody.appendChild(row);
    });

    const tableWrapper = tbody.closest('.data-table-wrapper');
    if (tableWrapper) {
      tableWrapper.onmouseleave = () => clearAllHighlights('forecast');
    }
  }

  // Render Forecast Modal Split Chart (Chart 1 - 100% Harmonized with Overview Modal Split Donut)
  function renderForecastModalSplitChart(active) {
    active = active || getForecastActiveRegion();
    const ctx = document.getElementById('chartForecastModalSplit');
    if (!ctx || !active) return;

    if (chartForecastModalSplit) {
      chartForecastModalSplit.destroy();
      chartForecastModalSplit = null;
    }

    setForecastChartEmptyState(ctx, null);

    // The modal split follows the global metric selector, just like the map,
    // KPI strip and relation table.
    const isTkm = state.metric === 'tkm';
    const divisor = isTkm ? 1e9 : 1e6;
    const unitText = isTkm ? 'Mrd. tkm' : 'Mio. t';
    const d = active.data || {};
    const dir = state.direction || 'all';
    const grp = (state.selectedGroup && state.selectedGroup !== 'ALL') ? state.selectedGroup : null;
    const isBalance = dir === 'balance';
    const scenario = getForecastScenarioMeta();
    const scenarioYear = scenario.year;
    const timeDescriptor = scenario.is_forecast ? `Prognose ${scenarioYear}` : `Basisjahr ${scenarioYear}`;
    setText('forecastModalSplitCardTitle', isBalance ? `Modalstruktur des Saldos ${scenarioYear}` : `Modal Split ${scenarioYear}`);
    setText('forecastModalSplitInfoTitle', `Modal Split ${scenarioYear}`);
    setText('forecastModalSplitInfoText', isBalance
      ? 'Bei Saldo ist ein klassischer Modal Split nicht definiert. Die Grafik zeigt daher die Anteile der absoluten Modal-Salden; die vorzeichenbehafteten Werte stehen in den Tooltipps.'
      : `Verteilung der Verkehrsleistung und Beförderungsmenge auf die drei Landverkehrsträger Straße, Schiene und Binnenschifffahrt für ${timeDescriptor}${grp ? ` und die Gütergruppe ${NST_GROUPS_7[grp]}` : ''}.`);

    const modeValues = getForecastModeValues(active, isTkm, dir, grp);
    if (!modeValues.available) {
      setForecastChartEmptyState(
        ctx,
        'Für die ausgewählte Gütergruppe liegt keine Verkehrsträger-Aufteilung vor. Der Modal Split kann daher nicht dargestellt werden.'
      );
      return;
    }

    const roadClean = (isBalance ? Math.abs(modeValues.road) : modeValues.road) / divisor;
    const railClean = (isBalance ? Math.abs(modeValues.rail) : modeValues.rail) / divisor;
    const iwwClean = (isBalance ? Math.abs(modeValues.iww) : modeValues.iww) / divisor;
    const totClean = roadClean + railClean + iwwClean;
    const signedModeValues = [modeValues.road, modeValues.rail, modeValues.iww];

    const roadPct = totClean > 0 ? formatDeNum((roadClean / totClean) * 100, 1) : '0,0';
    const railPct = totClean > 0 ? formatDeNum((railClean / totClean) * 100, 1) : '0,0';
    const iwwPct = totClean > 0 ? formatDeNum((iwwClean / totClean) * 100, 1) : '0,0';

    chartForecastModalSplit = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: [`Straße (${roadPct} %)`, `Schiene (${railPct} %)`, `Binnenschiff (${iwwPct} %)`],
        datasets: [{
          data: [roadClean, railClean, iwwClean],
          backgroundColor: ['#f59e0b', '#2563eb', '#0d9488'],
          borderWidth: 0,
          spacing: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        radius: '78%',
        cutout: '72%',
        layout: {
          padding: { top: 4, bottom: 4 }
        },
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 12, padding: 10, font: { size: 11.5, weight: '600' } }
          },
          tooltip: {
            callbacks: {
              title: () => timeDescriptor,
              label: c => {
                if (!isBalance) return ` ${c.label}: ${formatTrafficValue(c.raw, unitText, 2)} ${unitText}`;
                const signedValue = signedModeValues[c.dataIndex] || 0;
                return ` ${c.label}: ${signedValue > 0 ? '+' : ''}${formatTrafficValue(signedValue / divisor, unitText, 2)} ${unitText} (Betrag: ${formatTrafficValue(c.raw, unitText, 2)} ${unitText})`;
              }
            }
          }
        }
      }
    });
  }

  // Render Forecast KV & Commodity Structure Chart (Chart 2)
  function renderForecastCommodityKvChart(active) {
    active = active || getForecastActiveRegion();
    const ctx = document.getElementById('chartForecastCommodityKv');
    if (!ctx || !active) return;

    if (chartForecastCommodityKv) {
      chartForecastCommodityKv.destroy();
      chartForecastCommodityKv = null;
    }

    const d = active.data || {};
    const isTkm = state.metric === 'tkm';
    const divisor = isTkm ? 1e9 : 1e6;
    const unitText = isTkm ? 'Mrd. tkm' : 'Mio. t';
    const dir = state.direction || 'all';
    const scenario = getForecastScenarioMeta();
    const scenarioYear = scenario.year;
    const timeDescriptor = scenario.is_forecast ? `Prognose ${scenarioYear} (Basisfall P1)` : `Basisjahr ${scenarioYear}`;
    const isDetailedCommodityView = state.forecastChart2View === 'commodity' && state.forecastCommodityLevel === 'vp2040';
    setForecastChartEmptyState(ctx, null);
    setScrollableChartCanvas('chartForecastCommodityKv', false);
    renderStickyChartAxis('chartForecastCommodityKv', null, false, unitText);

    if (state.forecastChart2View === 'commodity') {
      setText('forecastChart2Title', `Güterstruktur ${scenarioYear} (NST-2007)`);
      // The drill-down preserves the 25 original VP2040 goods groups from
      // the source matrices. The existing crosswalk only supplies their labels.
      const isVp2040 = state.forecastCommodityLevel === 'vp2040';
      const taxonomy = isVp2040 ? (forecastData?.metadata?.vp2040_groups || {}) : NST_GROUPS_7;
      const keys = Object.keys(taxonomy).sort((a, b) => Number(a) - Number(b));
      const labels = keys.map(k => taxonomy[k]);
      setScrollableChartCanvas('chartForecastCommodityKv', isDetailedCommodityView, Math.max(860, keys.length * 32 + 110));

      const values = keys.map(k => {
        if (active.isNational) {
          const item = (isVp2040 ? d.vp2040_groups : d.nst_groups_7)?.[k] || {};
          return isTkm ? ((item.tkm || 0) / 1e9) : ((item.tonnes || 0) / 1e6);
        }
        const gDict = isVp2040
          ? (isTkm ? d.vp2040_groups_tkm : d.vp2040_groups_tonnes)
          : (isTkm ? d.groups_7_tkm : d.groups_7_tonnes);
        let v = 0;
        if (dir === 'outbound') v = gDict?.outbound?.[k] ?? 0;
        else if (dir === 'inbound') v = gDict?.inbound?.[k] ?? 0;
        else if (dir === 'balance') v = Math.abs(gDict?.balance?.[k] ?? 0);
        else v = gDict?.all?.[k] ?? (gDict?.[k] ?? 0);
        return v / divisor;
      });
      const totComm = values.reduce((a, b) => a + b, 0);

      chartForecastCommodityKv = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: unitText,
            data: values,
            backgroundColor: '#10b981',
            borderRadius: 4
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          layout: { padding: { left: 8 } },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                title: () => `Güterstruktur ${scenarioYear} (${isVp2040 ? 'VP2040 · 25 Gütergruppen' : 'NST-2007 · 7 Hauptgruppen'})`,
                label: c => {
                  const val = c.raw;
                  const pct = totComm > 0 ? formatDeNum((val / totComm) * 100, 1) : '0,0';
                  return ` ${c.label}: ${formatTrafficValue(val, unitText, 2)} ${unitText} (${pct} %)`;
                }
              }
            }
          },
          scales: {
            x: {
              beginAtZero: true,
              position: 'bottom',
              title: { display: !isDetailedCommodityView, text: unitText, font: { size: 11, weight: '600' } },
              ticks: { display: !isDetailedCommodityView, font: { size: 10.5 } }
            },
            y: {
              afterFit: scale => { scale.width = getYAxisLabelAreaWidth(scale.chart.width); },
              ticks: {
                font: { size: isVp2040 ? 10 : 10.5, weight: '600' },
                color: '#1e293b',
                crossAlign: 'far',
                callback: function (_value, index) { return abbreviateAxisLabelToWidth(labels[index], this, isVp2040 ? 10 : 10.5); }
              }
            }
          }
        }
      });
      enableYAxisLabelHover(chartForecastCommodityKv, labels);
      if (isDetailedCommodityView) requestAnimationFrame(() => {
        chartForecastCommodityKv?.resize();
        requestAnimationFrame(() => renderStickyChartAxis('chartForecastCommodityKv', chartForecastCommodityKv, true, unitText));
      });
    } else {
      // KV Ladeeinheiten View (Harmonisiert mit Intermodal-Seite)
      setText('forecastChart2Title', `Ladeeinheiten (KV) ${scenarioYear} · Gesamtmenge`);
      const behtypMap = active.isNational ? (d.behtyp_breakdown || {}) : (d.behtyp || {});

      const labels = [
        '40-Fuß Container (>30ft / 40ft)',
        '20-Fuß Container (bis 20ft / Status undiff.)',
        'Sonstige Containergrößen (25–30ft)',
        'Sattelauflieger / Lkw (beladen)',
        'Leere Container',
        'Leere Sattelauflieger / Lkw'
      ];

      const getBtVal = (bt) => {
        if (active.isNational) return (behtypMap[String(bt)]?.tonnes || 0);
        return (behtypMap[String(bt)] || 0);
      };

      const c40Tonnes = getBtVal(3) / 1e6;
      const c20Tonnes = (getBtVal(1) + getBtVal(10)) / 1e6;
      const wbTonnes = getBtVal(2) / 1e6;
      const trailerTonnes = getBtVal(4) / 1e6;
      const emptyContainerTonnes = (getBtVal(5) + getBtVal(6) + getBtVal(7)) / 1e6;
      const emptyTrailerTonnes = getBtVal(8) / 1e6;

      const values = [c40Tonnes, c20Tonnes, wbTonnes, trailerTonnes, emptyContainerTonnes, emptyTrailerTonnes];
      const totKv = values.reduce((a, b) => a + b, 0);

      if (!values.some(value => Number.isFinite(value) && value > 0)) {
        const scope = active.isNational ? 'Deutschland' : active.name;
        setForecastChartEmptyState(
          ctx,
          `Für ${scope} weist die VP2040-Matrix im ${timeDescriptor} keine Transporte nach Behältertyp bzw. Ladeeinheit aus.`
        );
        return;
      }

      chartForecastCommodityKv = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Mio. t',
            data: values,
            backgroundColor: ['#1e40af', '#3b82f6', '#4f46e5', '#10b981', '#8b5cf6', '#94a3b8'],
            borderRadius: 4
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          layout: { padding: { left: 8 } },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                title: () => `Kombinierter Verkehr ${timeDescriptor}`,
                label: c => {
                  const val = c.raw;
                  const pct = totKv > 0 ? formatDeNum((val / totKv) * 100, 1) : '0,0';
                  return ` ${c.label}: ${formatDeNum(val, 2)} Mio. t (${pct} % des KV)`;
                }
              }
            }
          },
          scales: {
            x: {
              beginAtZero: true,
              title: { display: true, text: 'Mio. Tonnen', font: { size: 11, weight: '600' } },
              ticks: { font: { size: 10.5 } }
            },
            y: {
              afterFit: scale => { scale.width = getYAxisLabelAreaWidth(scale.chart.width); },
              ticks: {
                font: { size: 10.5, weight: '600' },
                color: '#1e293b',
                crossAlign: 'far',
                callback: function (_value, index) { return abbreviateAxisLabelToWidth(labels[index], this, 10.5); }
              }
            }
          }
        }
      });
      enableYAxisLabelHover(chartForecastCommodityKv, labels);
    }
  }
