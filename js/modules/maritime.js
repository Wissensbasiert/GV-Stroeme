  // Helper: Compute YoY and Trend vs earliest base year (2016) for Maritime Partner Countries
  function computeMaritimePartnerTrends(partnerList, activePortCode, yr, groupFilter, dirFilter) {
    const currentYear = parseInt(yr);
    const prevYearStr = String(currentYear - 1);
    const baseYearStr = '2016'; // Earliest baseline reporting year

    const getPartnerYearFlow = (yearStr, iso, name) => {
      const yPorts = maritimeData.seaports?.[yearStr];
      const yNat = maritimeData.national?.[yearStr];
      let pList = [];
      if (activePortCode && yPorts?.[activePortCode]) {
        pList = yPorts[activePortCode].partner_countries || [];
      } else if (yNat) {
        pList = yNat.partner_countries || [];
      }
      const match = pList.find(p => p.iso === iso || p.name === name);
      if (!match) return 0;
      if (groupFilter && groupFilter !== 'ALL') {
        if (dirFilter === 'inbound') return match.groups_7_inbound?.[groupFilter] || 0;
        if (dirFilter === 'outbound') return match.groups_7_outbound?.[groupFilter] || 0;
        if (dirFilter === 'balance') return (match.groups_7_outbound?.[groupFilter] || 0) - (match.groups_7_inbound?.[groupFilter] || 0);
        return match.groups_7?.[groupFilter] || 0;
      } else {
        if (dirFilter === 'inbound') return match.inbound_tonnes || 0;
        if (dirFilter === 'outbound') return match.outbound_tonnes || 0;
        if (dirFilter === 'balance') return (match.outbound_tonnes || 0) - (match.inbound_tonnes || 0);
        return match.tonnes || 0;
      }
    };

    partnerList.forEach(p => {
      const curVal = p.flowVal || 0;
      const prevVal = getPartnerYearFlow(prevYearStr, p.iso, p.name);
      const baseVal = getPartnerYearFlow(baseYearStr, p.iso, p.name);

      // Percent changes on a signed balance are not meaningful. Preserve the
      // raw historic saldo values instead, so the table remains comparable.
      p.previous_value = String(currentYear) === prevYearStr ? null : prevVal;
      p.baseline_value = String(currentYear) === baseYearStr ? null : baseVal;
      p.yoy_pct = (dirFilter !== 'balance' && prevVal > 0 && String(currentYear) !== prevYearStr) ? ((curVal - prevVal) / prevVal) * 100 : null;
      p.trend_10yr_pct = (dirFilter !== 'balance' && baseVal > 0 && String(currentYear) !== baseYearStr) ? ((curVal - baseVal) / baseVal) * 100 : null;
    });
  }

  // Smart Dynamic Decimal Formatter for Tonnages in Millions of Tonnes
  // Ensures small quantities (e.g. 3.400 t = 0.0034 Mio. t) are never shown as "0,0" or "0"
  function formatSmartMioTonnes(tonnes, unit = 'Mio. t') {
    if (tonnes === null || tonnes === undefined || isNaN(tonnes) || tonnes === 0) {
      return unit ? `0,0 ${unit}` : '0,0';
    }
    const sign = tonnes < 0 ? '-' : '';
    const mio = Math.abs(tonnes) / 1e6;
    let formatted = '';
    if (mio >= 10) {
      formatted = formatDeNum(mio, 1);
    } else if (mio >= 0.1) {
      formatted = formatDeNum(mio, 2);
    } else if (mio >= 0.01) {
      formatted = formatDeNum(mio, 3);
    } else {
      // Very small values: if 3 decimals would round to 0,000, use 4 decimals
      const d3 = Math.round(mio * 1000) / 1000;
      formatted = d3 > 0 ? formatDeNum(mio, 3) : formatDeNum(mio, 4);
    }
    return unit ? `${sign}${formatted} ${unit}` : `${sign}${formatted}`;
  }

  // ============================================================
  // TAB 5: SEEVERKEHR & HÄFEN (INTERACTIVE PORTS, KPIS & CHARTS)
  // ============================================================
  function renderMaritimeTab() {
    if (!maritimeData) return;
    const yr = state.year;
    const prevYr = String(parseInt(yr) - 1);
    const yearPorts = maritimeData.seaports?.[yr] || maritimeData.seaports?.['2024'] || {};
    const prevPorts = maritimeData.seaports?.[prevYr] || {};

    // Helper: Dynamically build nationwide maritime aggregation across all ports and commodities
    const buildNationalMaritime = (targetYr) => {
      const officialNational = maritimeData.national?.[targetYr];
      if (officialNational) return officialNational;

      const ports = maritimeData.seaports?.[targetYr] || {};
      let totT = 0, totIn = 0, totOut = 0, totTeu = 0, totUnits = 0;
      const byGrp = { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0 };
      const byDiv = {};

      Object.values(ports).forEach(p => {
        const pTonnes = p.tonnes || 0;
        totT += pTonnes;
        totIn += (p.inbound_tonnes !== undefined && p.inbound_tonnes !== null ? p.inbound_tonnes : pTonnes * 0.58);
        totOut += (p.outbound_tonnes !== undefined && p.outbound_tonnes !== null ? p.outbound_tonnes : pTonnes * 0.42);
        totTeu += (p.teu || 0);
        totUnits += (p.units || 0);
        if (p.by_group) {
          for (let g = 1; g <= 7; g++) {
            const gs = String(g);
            const val = typeof p.by_group[gs] === 'number' ? p.by_group[gs] : (p.by_group[gs]?.tonnes || 0);
            byGrp[gs] += val;
          }
        }
      });

      // Integrate national commodities from commodities dictionary if available
      const commObj = maritimeData.commodities?.[targetYr];
      if (commObj?.groups_7) {
        for (let g = 1; g <= 7; g++) {
          const gs = String(g);
          if (commObj.groups_7[gs]) {
            byGrp[gs] = commObj.groups_7[gs];
          }
        }
      }
      if (commObj?.divisions_20) {
        Object.assign(byDiv, commObj.divisions_20);
      }

      if (totT === 0 && commObj?.groups_7) {
        totT = Object.values(commObj.groups_7).reduce((a, b) => a + b, 0);
        totIn = totT * 0.58;
        totOut = totT * 0.42;
      }

      return {
        name: 'Deutschland Gesamt',
        tonnes: totT,
        inbound_tonnes: totIn,
        outbound_tonnes: totOut,
        teu: totTeu,
        units: totUnits,
        by_group: byGrp,
        commodities: { groups_7: byGrp, divisions_20: byDiv },
        partner_countries: maritimeData.partner_countries?.[targetYr] || []
      };
    };

    const nationalData = buildNationalMaritime(yr);
    const prevNational = buildNationalMaritime(prevYr);

    const isSpecific = Boolean(state.selectedPort && yearPorts[state.selectedPort]);
    const activePort = isSpecific ? yearPorts[state.selectedPort] : null;
    const prevActivePort = isSpecific ? (prevPorts[state.selectedPort] || null) : null;
    const activeObj = isSpecific ? activePort : nationalData;
    const prevObj = isSpecific ? prevActivePort : prevNational;
    const portName = isSpecific ? activePort.name : 'Deutschland Gesamt';

    const groupFilter = state.selectedGroup || 'ALL';
    const dirFilter = state.direction || 'all';

    // Calculate volume based on global filters (Direction & Commodity Group)
    const getFilteredTonnage = (targetObj, grp, dir) => {
      if (!targetObj) return 0;
      if (grp !== 'ALL') {
        const bg = targetObj.by_group?.[grp] || targetObj.commodities?.groups_7?.[grp] || {};
        const gVal = typeof bg === 'number' ? bg : (bg.tonnes || 0);
        if (dir === 'inbound') return (typeof bg === 'object' && bg.inbound !== undefined) ? bg.inbound : (gVal * 0.58);
        if (dir === 'outbound') return (typeof bg === 'object' && bg.outbound !== undefined) ? bg.outbound : (gVal * 0.42);
        if (dir === 'balance') {
          const inVal = (typeof bg === 'object' && bg.inbound !== undefined) ? bg.inbound : (gVal * 0.58);
          const outVal = (typeof bg === 'object' && bg.outbound !== undefined) ? bg.outbound : (gVal * 0.42);
          return outVal - inVal;
        }
        return gVal;
      } else {
        const tVal = targetObj.tonnes || 0;
        if (dir === 'inbound') return (targetObj.inbound_tonnes !== undefined && targetObj.inbound_tonnes !== null) ? targetObj.inbound_tonnes : (tVal * 0.58);
        if (dir === 'outbound') return (targetObj.outbound_tonnes !== undefined && targetObj.outbound_tonnes !== null) ? targetObj.outbound_tonnes : (tVal * 0.42);
        if (dir === 'balance') {
          const inVal = (targetObj.inbound_tonnes !== undefined && targetObj.inbound_tonnes !== null) ? targetObj.inbound_tonnes : (tVal * 0.58);
          const outVal = (targetObj.outbound_tonnes !== undefined && targetObj.outbound_tonnes !== null) ? targetObj.outbound_tonnes : (tVal * 0.42);
          return outVal - inVal;
        }
        return tVal;
      }
    };

    // TEU use the same raw directional rows as the tonnage.  Do not derive a
    // direction by a percentage split: the pipeline supplies separate values
    // for the total, good group and direction whenever the source provides it.
    const getFilteredTeu = (targetObj, grp, dir) => {
      if (!targetObj) return 0;
      const bucket = grp !== 'ALL'
        ? (targetObj.by_group?.[grp] || targetObj.commodities?.groups_7?.[grp] || {})
        : targetObj;
      const total = typeof bucket === 'object' ? (bucket.teu || 0) : 0;
      if (dir === 'inbound') return typeof bucket === 'object' ? (bucket.inbound_teu || 0) : 0;
      if (dir === 'outbound') return typeof bucket === 'object' ? (bucket.outbound_teu || 0) : 0;
      if (dir === 'balance') return typeof bucket === 'object' ? ((bucket.outbound_teu || 0) - (bucket.inbound_teu || 0)) : 0;
      return total;
    };

    const totVal = getFilteredTonnage(activeObj, groupFilter, dirFilter);
    const inVal = getFilteredTonnage(activeObj, groupFilter, 'inbound');
    const outVal = getFilteredTonnage(activeObj, groupFilter, 'outbound');

    const prevTot = prevObj ? getFilteredTonnage(prevObj, groupFilter, dirFilter) : null;
    const prevIn = prevObj ? getFilteredTonnage(prevObj, groupFilter, 'inbound') : null;
    const prevOut = prevObj ? getFilteredTonnage(prevObj, groupFilter, 'outbound') : null;

    // 1. Standardized Seeverkehr KPIs (Matching Overview Design with Diagonal YoY Arrows)
    const setTxt = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
    const setHtml = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };
    setTxt('legendTitle_maritime', 'Seehafen-Umschlag');
    const scopeDirectionLabel = { inbound: 'Empfang', outbound: 'Versand', balance: 'Saldo' }[dirFilter] || 'Versand + Empfang';
    const scopeGroupLabel = groupFilter !== 'ALL' ? (NST_GROUPS_7[groupFilter] || `Gütergruppe ${groupFilter}`) : 'alle Güterarten';
    const scopeFilterText = `${scopeDirectionLabel}, ${scopeGroupLabel}`;
    const maritimeMeasureHeader = document.getElementById('thMaritimeMetricUnit');
    if (maritimeMeasureHeader) {
      maritimeMeasureHeader.textContent = dirFilter === 'balance' ? 'Saldo (Mio. t)' : 'Menge (Mio. t)';
      maritimeMeasureHeader.title = dirFilter === 'balance' ? 'Saldo der Relation in Millionen Tonnen' : 'Menge in Millionen Tonnen';
    }
    setTxt('maritimePartnersTitle', isSpecific
      ? `Top ${state.topX} Relationen: ${portName}`
      : 'Top Relationen: Hafen auswählen');

    const formatYoYBadge = (cVal, pVal) => {
      if (dirFilter === 'balance') {
        return '<span style="color:#64748b; font-size:0.75rem; font-weight:600;">Saldo ohne Vorjahresvergleich</span>';
      }
      if (pVal === null || pVal === undefined || pVal <= 0 || cVal === null || cVal === undefined) {
        return `<span style="color:#64748b; font-size:0.75rem; font-weight:600;">-- ggü. ${prevYr}</span>`;
      }
      const pct = ((cVal - pVal) / pVal) * 100;
      if (pct > 0.05) {
        return `<span style="color:#16a34a; font-size:0.75rem; font-weight:700;">↗ +${formatDeNum(pct, 1)} % ggü. ${prevYr}</span>`;
      } else if (pct < -0.05) {
        return `<span style="color:#dc2626; font-size:0.75rem; font-weight:700;">↘ ${formatDeNum(pct, 1)} % ggü. ${prevYr}</span>`;
      } else {
        return `<span style="color:#64748b; font-size:0.75rem; font-weight:600;">→ 0,0 % ggü. ${prevYr}</span>`;
      }
    };
    
    // KPI 1: Seegüterumschlag (Gesamt)
    const directionSuffix = dirFilter === 'balance' ? ' · Saldo' : dirFilter === 'inbound' ? ' · Empfang' : dirFilter === 'outbound' ? ' · Versand' : '';
    const formatSaldo = (value, unit) => `${dirFilter === 'balance' && value > 0 ? '+' : ''}${formatSmartMioTonnes(value, unit)}`;
    setTxt('kpiMrtmTotalTitle', isSpecific ? `Seegüterumschlag (${portName}${directionSuffix})` : `Seegüterumschlag (Gesamt${directionSuffix})`);
    setTxt('kpiMrtmTotalVal', formatSaldo(totVal, 'Mio. t'));
    setHtml('kpiMrtmTotalSub', formatYoYBadge(totVal, prevTot));

    // KPI 2: Containerumschlag (TEU)
    const teuVal = getFilteredTeu(activeObj, groupFilter, dirFilter);
    const prevTeu = prevObj ? getFilteredTeu(prevObj, groupFilter, dirFilter) : null;
    let formattedTeu = '0 TEU';
    if (teuVal !== 0) {
      if (Math.abs(teuVal) >= 10000) {
        formattedTeu = formatSaldo(teuVal, 'Mio. TEU');
      } else {
        formattedTeu = `${dirFilter === 'balance' && teuVal > 0 ? '+' : ''}${formatDeNum(teuVal, 0)} TEU`;
      }
    }
    const teuDirectionLabel = { inbound: 'Empfang', outbound: 'Versand', balance: 'Saldo' }[dirFilter] || 'Gesamt';
    setTxt('kpiMrtmTeuTitle', isSpecific ? `Containerumschlag (${portName} · ${teuDirectionLabel})` : `Containerumschlag (${teuDirectionLabel})`);
    setTxt('kpiMrtmTeuVal', formattedTeu);
    setHtml('kpiMrtmTeuSub', formatYoYBadge(teuVal, prevTeu));

    // KPI 3: Seeseitiger Empfang
    setTxt('kpiMrtmInTitle', isSpecific ? `Seeseitiger Empfang (${portName})` : 'Seeseitiger Empfang');
    setTxt('kpiMrtmInVal', formatSmartMioTonnes(inVal, 'Mio. t'));
    setHtml('kpiMrtmInSub', formatYoYBadge(inVal, prevIn));

    // KPI 4: Seeseitiger Versand
    setTxt('kpiMrtmOutTitle', isSpecific ? `Seeseitiger Versand (${portName})` : 'Seeseitiger Versand');
    setTxt('kpiMrtmOutVal', formatSmartMioTonnes(outVal, 'Mio. t'));
    setHtml('kpiMrtmOutSub', formatYoYBadge(outVal, prevOut));

    // 2. Map & Port Circle Markers (with Hover Tooltips and Detail Popups)
    const map = maps.maritime;
    if (map) {
      if (mapLayers.maritime.portsGroup) {
        mapLayers.maritime.portsGroup.clearLayers();
      } else {
        mapLayers.maritime.portsGroup = L.layerGroup().addTo(map);
      }
      mapLayers.maritime.portsLookup = {};

      const getMrtmRadius = (t) => {
        const m = (t || 0) / 1e6;
        if (m < 5) return 6.5;
        if (m <= 25) return 11;
        return 16.5;
      };

      Object.values(yearPorts).forEach(p => {
        const portFlow = getFilteredTonnage(p, groupFilter, dirFilter);
        const portTeu = getFilteredTeu(p, groupFilter, dirFilter);
        const radius = getMrtmRadius(portFlow);
        const isThisSelected = isSpecific && (state.selectedPort === p.unlocode);
        const isAnotherSelected = isSpecific && !isThisSelected;
        const coordinate = MARITIME_COORDINATE_OVERRIDES[p.unlocode] || p;
        const lat = Number(coordinate.lat);
        const lng = Number(coordinate.lng);
        if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;

        const marker = L.circleMarker([lat, lng], {
          radius: isThisSelected ? radius + 2.5 : radius,
          fillColor: '#4f46e5',
          color: isThisSelected ? '#0f172a' : '#ffffff',
          weight: isThisSelected ? 4 : 2,
          fillOpacity: (portFlow === 0) ? 0.25 : (isAnotherSelected ? 0.45 : 0.95)
        }).addTo(mapLayers.maritime.portsGroup);

        mapLayers.maritime.portsLookup[p.unlocode] = { marker, originalRadius: radius };

        // Lightweight Hover Tooltip with smart dynamic decimal formatting
        const teuTooltip = (portTeu !== 0)
          ? `<br>• Containerumschlag (${teuDirectionLabel}): <strong>${Math.abs(portTeu) >= 10000 ? formatSmartMioTonnes(portTeu, 'Mio. TEU') : formatDeNum(portTeu, 0) + ' TEU'}</strong>`
          : '';
        marker.bindTooltip(`
          <div style="font-size:0.825rem; line-height:1.45;">
            <div style="font-size:0.68rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:2px;">Bezugsjahr: ${state.year} · ${teuDirectionLabel}</div>
            <strong>Seehafen ${p.name}</strong> (${p.unlocode})<br>
            • Umschlag: <strong>${formatSmartMioTonnes(portFlow, 'Mio. t')}</strong>
            ${teuTooltip}
            <div class="map-tooltip-filter-hint">Klicken Sie, um diesen Hafen auszuwählen und die Analysen darauf zu begrenzen.</div>
          </div>
        `, { sticky: true });

        // Rich Click Detail Popup
        const teuInfo = portTeu !== 0 ? `• Containerumschlag (${teuDirectionLabel}): <strong>${Math.abs(portTeu) >= 10000 ? formatSmartMioTonnes(portTeu, 'Mio. TEU') : formatDeNum(portTeu, 0) + ' TEU'}</strong><br>` : '';
        const unitsInfo = p.units > 0 ? `• RoRo / Ladeeinheiten / Trailer: <strong>${p.units >= 1000 ? formatDeNum(p.units / 1e3, 1) + ' Tsd. Einheiten' : formatDeNum(p.units, 0) + ' Einheiten'}</strong><br>` : '';
        const inInfo = `• Seeseitiger Empfang: <strong>${formatSmartMioTonnes(p.inbound_tonnes ?? (p.tonnes * 0.58), 'Mio. t')}</strong><br>`;
        const outInfo = `• Seeseitiger Versand: <strong>${formatSmartMioTonnes(p.outbound_tonnes ?? (p.tonnes * 0.42), 'Mio. t')}</strong><br>`;
        const filterHint = `<div class="port-filter-hint"><img class="popup-state-icon" src="assets/icons/${isThisSelected ? 'check_circle' : 'location_on'}.svg" alt="" aria-hidden="true">${isThisSelected ? 'Dieser Hafen filtert aktuell die Analysen. Klicken Sie zum Aufheben.' : 'Klicken Sie auf diesen Hafen, um KPIs, Tabellen und Diagramme einzugrenzen.'}</div>`;

        marker.bindPopup(`
          <div style="font-size:0.85rem; line-height:1.5; min-width:220px;">
            <div style="font-size:0.68rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:3px;">Berichtsjahr: ${state.year}</div>
            <div style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-bottom:2px;">Seehafen ${p.name} <span style="font-size:0.75rem; color:#64748b; font-weight:600;">(${p.unlocode})</span></div>
            <div style="font-size:0.78rem; color:#4f46e5; font-weight:600; margin-bottom:6px;">${p.hub_type}</div>
            • Güterumschlag gesamt: <strong>${formatSmartMioTonnes(p.tonnes, 'Mio. t')}</strong><br>
            ${inInfo}${outInfo}
            ${teuInfo}${unitsInfo}
            ${filterHint}
          </div>
        `);

        marker.on('click', () => {
          state.selectedPort = (state.selectedPort === p.unlocode) ? null : p.unlocode;
          renderMaritimeTab();
        });
      });
    }

    // 3. UI Titles & Filter Actions
    const resetActionEl = document.getElementById('maritimePortResetAction');
    if (resetActionEl) resetActionEl.style.display = isSpecific ? 'block' : 'none';

    updateMapTitles();

    const filterStatusEl = document.getElementById('mrtmFilterStatus');
    if (filterStatusEl) {
      filterStatusEl.innerHTML = isSpecific 
        ? `<span style="color:#4f46e5; font-weight:700;">Hafen: ${portName}</span>` 
        : 'Alle Seehäfen aktiv';
    }

    const commTitleEl = document.getElementById('maritimeCommodityTitle');
    if (commTitleEl) commTitleEl.textContent = isSpecific ? `Güterstruktur des Seeverkehrs (${portName})` : 'Güterstruktur des deutschen Seeverkehrs';

    // 4. Update Partners Table with Dynamic Trends and Standardized Columns
    const tbody = document.getElementById('tableMaritimePartnersBody');
    const partnersTable = document.getElementById('tableMaritimePartners');
    if (tbody) {
      tbody.innerHTML = '';
      if (!isSpecific) {
        if (partnersTable) partnersTable.hidden = false;
        tbody.innerHTML = `
          <tr>
            <td colspan="5" style="text-align:center; color:#475569; padding:28px 16px; font-size:0.86rem; line-height:1.6;">
              <div class="empty-state-icon"><img src="assets/icons/directions_boat.svg" alt="" aria-hidden="true"></div>
              <strong style="color:#0f172a; font-size:0.95rem;">Deutschland aktiv</strong><br>
              <span style="color:#475569; font-size:0.79rem;">Die vier Kennzahlen oben beziehen sich auf die nationale Destatis-Aggregation des deutschen Seeverkehrs im Berichtsjahr ${yr} (${scopeFilterText}) – nicht auf die Summe der ${Object.keys(yearPorts).length} kartierten Seehäfen.</span><br><br>
              <span style="color:#64748b; font-size:0.81rem;">Bitte wählen Sie auf der Karte einen <strong>Seehafen</strong> aus, um dessen wichtigste internationale Seeverkehrsbeziehungen anzuzeigen.</span>
            </td>
          </tr>
        `;
        renderMaritimeCommodityChart();
        return;
      }
      if (partnersTable) partnersTable.hidden = false;

      const rawPartners = activePort.partner_countries || [];

      const partnersList = rawPartners.map(p => {
        let flow = 0;
        if (groupFilter !== 'ALL') {
          if (dirFilter === 'inbound') flow = p.groups_7_inbound?.[groupFilter] || 0;
          else if (dirFilter === 'outbound') flow = p.groups_7_outbound?.[groupFilter] || 0;
          else if (dirFilter === 'balance') flow = (p.groups_7_outbound?.[groupFilter] || 0) - (p.groups_7_inbound?.[groupFilter] || 0);
          else flow = p.groups_7?.[groupFilter] || 0;
        } else {
          if (dirFilter === 'inbound') flow = p.inbound_tonnes || 0;
          else if (dirFilter === 'outbound') flow = p.outbound_tonnes || 0;
          else if (dirFilter === 'balance') flow = (p.outbound_tonnes || 0) - (p.inbound_tonnes || 0);
          else flow = p.tonnes || 0;
        }
        return { ...p, flowVal: flow };
      }).filter(p => dirFilter === 'balance' ? p.flowVal !== 0 : p.flowVal > 0);

      partnersList.sort((a, b) => dirFilter === 'balance' ? Math.abs(b.flowVal) - Math.abs(a.flowVal) : b.flowVal - a.flowVal);

      computeMaritimePartnerTrends(partnersList, isSpecific ? state.selectedPort : null, yr, groupFilter, dirFilter);

      if (partnersList.length === 0) {
        const groupLabel = groupFilter !== 'ALL' ? NST_GROUPS_7[groupFilter] : 'Seeverkehr';
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#64748b; padding:24px; font-size:0.85rem;">Für <strong>${groupLabel}</strong> wurden im Erhebungsjahr ${state.year} für ${portName} keine bilateralen Außenhandelsverkehre erfasst.</td></tr>`;
      } else {
        const gName = (groupFilter && groupFilter !== 'ALL') ? (NST_GROUPS_7[groupFilter] || `Gruppe ${groupFilter}`) : 'Alle Güterarten';

        partnersList.slice(0, state.topX).forEach(p => {
          // Dynamic formatting so small amounts e.g. 1.700 t are shown as 0,0017 rather than 0,00
          const cleanValNum = formatSmartMioTonnes(p.flowVal, '');
          const yoyVal = (p.yoy_pct !== null && p.yoy_pct !== undefined) ? p.yoy_pct : null;
          const trendVal = (p.trend_10yr_pct !== null && p.trend_10yr_pct !== undefined) ? p.trend_10yr_pct : null;
          const formatHistoricSaldo = value => {
            if (value === null || value === undefined) return '<span style="color:#94a3b8;" title="Kein historischer Saldo für dieses Jahr vorhanden.">--</span>';
            return `<span style="font-weight:700;">${value > 0 ? '+' : ''}${formatSmartMioTonnes(value, '')}</span>`;
          };

          const yoy = dirFilter === 'balance'
            ? formatHistoricSaldo(p.previous_value)
            : (yoyVal !== null && yoyVal !== undefined)
            ? `<span style="color:${yoyVal >= 0 ? '#16a34a' : '#dc2626'}; font-weight:700;">${yoyVal >= 0 ? '↗ +' : '↘ '}${formatDeNum(yoyVal, 1)} %</span>`
            : '<span style="color:#94a3b8;">--</span>';

          const trend10 = dirFilter === 'balance'
            ? formatHistoricSaldo(p.baseline_value)
            : (trendVal !== null && trendVal !== undefined)
            ? `<span style="color:${trendVal >= 0 ? '#16a34a' : '#dc2626'}; font-weight:700;">${trendVal >= 0 ? '↗ +' : '↘ '}${formatDeNum(trendVal, 1)} %</span>`
            : '<span style="color:#94a3b8;">--</span>';

          const row = document.createElement('tr');
          row.setAttribute('data-partner-id', p.iso);
          row.innerHTML = `
            <td><strong>${p.name}</strong> <span style="font-size:0.75rem; color:#94a3b8;">(${p.iso})</span></td>
            <td>${gName}</td>
            <td style="text-align: right;"><strong>${cleanValNum}</strong></td>
            <td style="text-align: right;">${yoy}</td>
            <td style="text-align: right;">${trend10}</td>
          `;
          tbody.appendChild(row);
        });
      }
    }

    // 5. Update Commodity Chart
    renderMaritimeCommodityChart();
  }

  function renderMaritimeCommodityChart() {
    const ctx = document.getElementById('chartMaritimeCommodity');
    if (!ctx) return;

    if (chartMaritimeCommodity) {
      chartMaritimeCommodity.destroy();
      chartMaritimeCommodity = null;
    }

    const yr = state.year;
    const is20 = (state.maritimeNstLevel === '20');
    const isDetailedSnapshot = is20 && state.maritimeCommodityView === 'snapshot';
    const axisLabel = state.direction === 'balance' ? 'Saldo (Mio. t)' : 'Mio. t';
    const taxonomyDict = is20 ? NST_DIVISIONS_20 : NST_GROUPS_7;

    // Strict numerical sorting of the 20 NST-2007 divisions (01 to 20)
    const keys = Object.keys(taxonomyDict).sort((a, b) => parseInt(a) - parseInt(b));
    setScrollableChartCanvas('chartMaritimeCommodity', isDetailedSnapshot, Math.max(650, keys.length * 31 + 100));
    renderStickyChartAxis('chartMaritimeCommodity', null, false, axisLabel);

    const isSpecific = Boolean(state.selectedPort && maritimeData.seaports?.[yr]?.[state.selectedPort]);
    const dimensionKey = is20 ? 'divisions_20' : 'groups_7';
    const detailKey = is20 ? 'by_division' : 'by_group';
    const getCommodityValues = (targetYear) => {
      const source = isSpecific
        ? maritimeData.seaports?.[targetYear]?.[state.selectedPort]
        : (maritimeData.national?.[targetYear] || null);
      const fallback = isSpecific
        ? maritimeData.seaports?.[targetYear]?.[state.selectedPort]?.commodities?.[dimensionKey]
        : maritimeData.commodities?.[targetYear]?.[dimensionKey];
      const detail = source?.[detailKey];
      if (!detail) return fallback || {};

      return Object.fromEntries(Object.entries(detail).map(([key, bucket]) => {
        const total = typeof bucket === 'number' ? bucket : (bucket.tonnes || 0);
        const inbound = typeof bucket === 'number' ? total * 0.58 : (bucket.inbound || 0);
        const outbound = typeof bucket === 'number' ? total * 0.42 : (bucket.outbound || 0);
        if (state.direction === 'inbound') return [key, inbound];
        if (state.direction === 'outbound') return [key, outbound];
        if (state.direction === 'balance') return [key, outbound - inbound];
        return [key, total];
      }));
    };
    const rawComm = getCommodityValues(yr);

    if (state.maritimeCommodityView === 'snapshot') {
      const values = keys.map(k => (rawComm[k] || 0) / 1e6);
      const totalVal = values.reduce((a, b) => a + Math.abs(b), 0);

      // Clean Y-axis labels WITHOUT percentages so text is fully legible
      const cleanLabels = keys.map(k => taxonomyDict[k]);

      chartMaritimeCommodity = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: cleanLabels,
          datasets: [{ label: 'Mio. t', data: values, backgroundColor: '#4f46e5', borderRadius: 4 }]
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
                title: () => `Bezugsjahr: ${state.year}`,
                label: c => {
                  const val = c.raw;
                  if (state.direction === 'balance') return ` ${c.label}: ${formatDeNum(val, 2)} Mio. t Saldo`;
                  const pct = totalVal > 0 ? formatDeNum((val / totalVal) * 100, 1) : '0,0';
                  return ` ${c.label}: ${formatDeNum(val, 2)} Mio. t (${pct} %)`;
                }
              }
            }
          },
          scales: {
            x: { 
              beginAtZero: state.direction !== 'balance', 
              position: 'bottom',
              title: { display: !isDetailedSnapshot, text: axisLabel, font: { size: 11, weight: '600' } },
              ticks: { display: !isDetailedSnapshot, font: { size: 10.5 } }
            },
            y: {
              afterFit: scale => { scale.width = getYAxisLabelAreaWidth(scale.chart.width); },
              ticks: { 
                font: { size: 11, weight: '600' },
                color: '#1e293b',
                crossAlign: 'far',
                callback: function (_value, index) { return abbreviateAxisLabelToWidth(cleanLabels[index], this, 11); }
              }
            }
          }
        }
      });
      enableYAxisLabelHover(chartMaritimeCommodity, cleanLabels);
      if (isDetailedSnapshot) requestAnimationFrame(() => {
        chartMaritimeCommodity?.resize();
        requestAnimationFrame(() => renderStickyChartAxis('chartMaritimeCommodity', chartMaritimeCommodity, true, axisLabel));
      });
      renderScrollableChartLegend('chartMaritimeCommodity', null, false);
    } else {
      // Dynamically filter complete years
      const allYears = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];
      const validYears = allYears.filter(y => {
        const commObj = getCommodityValues(String(y));
        return Object.values(commObj).some(v => Math.abs(v) > 0);
      });

      const colors = ['#4f46e5', '#059669', '#d97706', '#dc2626', '#8b5cf6', '#475569', '#0d9488'];

      const datasets = keys.map((k, i) => ({
        label: taxonomyDict[k],
        data: validYears.map(y => {
          const commObj = getCommodityValues(String(y));
          const val = commObj?.[k];
          return (val !== undefined && val !== null && val !== 0) ? (val / 1e6) : null;
        }),
        borderColor: colors[i % colors.length],
        backgroundColor: colors[i % colors.length],
        tension: 0.2,
        spanGaps: false,
        borderWidth: 2
      })).filter(dataset => dataset.data.some(value => value !== null && value !== 0));

      chartMaritimeCommodity = new Chart(ctx, {
        type: 'line',
        data: { labels: validYears, datasets: datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { 
              display: !is20,
              position: 'bottom', 
              labels: { 
                boxWidth: 10, 
                padding: 8,
                font: { size: 11, weight: '600' } 
              } 
            },
            tooltip: { 
              callbacks: { 
                title: items => `Jahr: ${items[0]?.label}`,
                label: c => formatDynamicChartShare(c, axisLabel)
              } 
            }
          },
          scales: { 
            x: {
              ticks: { font: { size: 11, weight: '600' } }
            },
            y: { 
              beginAtZero: state.direction !== 'balance', 
              title: { display: true, text: axisLabel, font: { size: 11, weight: '600' } },
              ticks: { font: { size: 11 } }
            } 
          }
        }
      });
      renderScrollableChartLegend('chartMaritimeCommodity', chartMaritimeCommodity, is20);
    }
  }

  // ============================================================
