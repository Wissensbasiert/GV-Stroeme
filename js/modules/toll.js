  // ============================================================
  // LIVE-MODUL: GEMEINDEBEZOGENE MAUTDATEN
  // ============================================================
  const TOLL_API_QUERY_URL = (
    'https://webgis.toll-collect.de/arcgis/rest/services/lkw-verkehrsportal/' +
    'mautdaten_bund_monat_sz/FeatureServer/0/query'
  );
  const TOLL_MUNICIPALITY_BOUNDARY_BASE_URL = 'data/processed/toll_municipality_boundaries';
  // Municipal geometry is a local, checked VG250 export. At the national
  // overview it would still be visual noise, so only overlapping Länderdateien
  // are loaded after a deliberate zoom-in.
  const TOLL_MUNICIPALITY_MIN_ZOOM = 7;
  const TOLL_PAGE_SIZE = 2000;
  const TOLL_CONNECTION_COLOR = '#0ea5e9';
  const TOLL_CONNECTION_HIGHLIGHT_COLOR = '#2563eb';
  const TOLL_REQUIRED_FIELDS = [
    'ags_start', 'ags_ziel', 'name_start', 'name_ziel',
    'anzahl_befahrungen', 'fahrleistung_km',
    'distanz_km_mittelw', 'zeit_min_mittelw'
  ];
  const TOLL_METRICS = {
    trips: { label: 'Mautfahrten', unit: 'Fahrten', field: 'trips' },
    mileage: { label: 'Fahrleistung', unit: 'km', field: 'mileage' },
    distance: { label: 'Mittlere Distanz', unit: 'km', field: 'distance' },
    time: { label: 'Mittlere Fahrzeit', unit: 'Min.', field: 'time' }
  };
  const TOLL_DISTANCE_CLASSES = [
    { label: 'unter 50 km', lower: 0, upper: 50 },
    { label: '50 bis unter 100 km', lower: 50, upper: 100 },
    { label: '100 bis unter 200 km', lower: 100, upper: 200 },
    { label: '200 bis unter 300 km', lower: 200, upper: 300 },
    { label: '300 km und mehr', lower: 300, upper: Infinity }
  ];
  const TOLL_DISTANCE_CLASS_COLORS = ['#b9dfc2', '#79c48a', '#63b472', '#4c9b83', '#4c7f83'];
  let tollModuleInitialized = false;
  let tollEventListenersReady = false;
  let tollRelations = [];
  let tollLoadedSelectionKey = null;
  let tollRequestSequence = 0;
  let tollRequestPending = false;
  let tollApiFailed = false;
  let tollMunicipalityMapReady = false;
  let tollMunicipalityBoundaryRequest = null;
  let tollMunicipalityBoundarySequence = 0;
  let tollMunicipalityBoundaryTimer = null;
  let tollMunicipalityBoundaryIndexPromise = null;
  const tollMunicipalityBoundaryPayloads = new Map();
  let tollMonthAvailabilityPromise = null;
  let tollCountryOutlinePromise = null;
  let tollHoverTimer = null;
  let tollHoverSequence = 0;
  let tollDistanceChartKey = null;
  let tollActiveHighlightedPartnerAgs = null;

  function escapeTollHtml(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function normalizeTollSearch(value) {
    return String(value || '')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLocaleLowerCase('de-DE')
      .trim();
  }

  function formatTollMonth(value) {
    const match = /^(\d{4})-(\d{2})$/.exec(String(value || ''));
    return match ? `${match[2]}/${match[1]}` : String(value || '');
  }

  function getTollMunicipalityRecord() {
    return tollMunicipalityData?.municipalities?.find(
      municipality => municipality.ags === state.tollMunicipality
    ) || null;
  }

  function getTollMunicipalityLabel() {
    const municipality = getTollMunicipalityRecord();
    if (municipality) return municipality.name;
    return state.tollMunicipality
      ? (document.getElementById('tollMunicipalitySearchInput')?.value || state.tollMunicipality)
      : 'Gemeinde auswählen';
  }

  function getTollSelectionKey() {
    if (!state.tollMunicipality || !state.tollMonth || !state.tollDirection) return null;
    return `${state.tollMunicipality}|${state.tollMonth}|${state.tollDirection}`;
  }

  function parseTollApiMonth(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return null;
    return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}`;
  }

  function fetchTollAvailableMonths() {
    if (tollMonthAvailabilityPromise) return tollMonthAvailabilityPromise;
    const params = new URLSearchParams({
      where: '1=1',
      outFields: 'monat',
      returnGeometry: 'false',
      returnDistinctValues: 'true',
      orderByFields: 'monat DESC',
      f: 'json'
    });
    tollMonthAvailabilityPromise = fetch(`${TOLL_API_QUERY_URL}?${params.toString()}`, {
      cache: 'no-store',
      headers: { Accept: 'application/json' }
    }).then(async response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      if (payload?.error) throw new Error(payload.error.message || 'API-Fehler');
      const months = [...new Set((payload?.features || [])
        .map(feature => parseTollApiMonth(feature?.attributes?.monat))
        .filter(Boolean))]
        .sort((a, b) => b.localeCompare(a));
      if (!months.length) throw new Error('Die API meldet keine verfügbaren Berichtsmonate.');
      return months;
    }).catch(error => {
      tollMonthAvailabilityPromise = null;
      throw error;
    });
    return tollMonthAvailabilityPromise;
  }

  async function buildTollMonthOptions() {
    const select = document.getElementById('selectTollMonth');
    if (!select) return;
    select.disabled = true;
    select.innerHTML = '<option value="">Monate werden geladen …</option>';
    try {
      const months = await fetchTollAvailableMonths();
      const selectedMonth = months.includes(state.tollMonth) ? state.tollMonth : months[0];
      select.innerHTML = '';
      months.forEach(value => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = formatTollMonth(value);
        select.appendChild(option);
      });
      state.tollMonth = selectedMonth;
      select.value = selectedMonth;
      select.disabled = false;
      setTollStatus('', '');
      updateAnalysisSummary();
      if (state.tollMunicipality) loadTollRelations();
    } catch (error) {
      console.error('Could not load available Toll Collect months:', error);
      state.tollMonth = null;
      select.innerHTML = '<option value="">Monate nicht verfügbar</option>';
      setTollStatus('error', 'Die verfügbaren Berichtsmonate konnten nicht aus der Mautdaten-API geladen werden. Versuchen Sie es später erneut.', true);
      updateAnalysisSummary();
    }
  }

  function updateTollMunicipalityInput() {
    const input = document.getElementById('tollMunicipalitySearchInput');
    if (!input) return;
    const record = getTollMunicipalityRecord();
    input.value = record ? `${record.name} (${record.ags})` : '';
  }

  function selectTollMunicipality(ags) {
    const municipality = (tollMunicipalityData?.municipalities || [])
      .find(item => item.ags === String(ags || ''));
    if (!municipality) return;
    tollMunicipalityBoundaryRequest?.abort();
    tollMunicipalityBoundaryRequest = null;
    tollMunicipalityBoundarySequence += 1;
    state.tollMunicipality = municipality.ags;
    tollRelations = [];
    tollLoadedSelectionKey = null;
    updateTollMunicipalityInput();
    updateTollMunicipalityBoundaryStyles();
    updateAnalysisSummary();
    loadTollRelations();
  }

  function setupTollAutocomplete() {
    const input = document.getElementById('tollMunicipalitySearchInput');
    const dropdown = document.getElementById('tollMunicipalityAutocompleteList');
    const clearButton = document.getElementById('btnClearTollMunicipality');
    if (!input || !dropdown || input.dataset.tollReady === 'true') return;
    input.dataset.tollReady = 'true';

    const closeList = () => dropdown.classList.remove('active');
    const renderList = rawQuery => {
      const query = normalizeTollSearch(rawQuery);
      dropdown.innerHTML = '';
      if (query.length < 2) {
        closeList();
        return;
      }
      const matches = (tollMunicipalityData?.municipalities || [])
        .filter(item => normalizeTollSearch(item.name).includes(query) || item.ags.includes(query))
        .slice(0, 35);
      if (!matches.length) {
        const empty = document.createElement('div');
        empty.className = 'autocomplete-item autocomplete-empty';
        empty.textContent = 'Keine Gemeinde im Mautdatenbestand gefunden';
        dropdown.appendChild(empty);
      } else {
        matches.forEach(item => {
          const option = document.createElement('div');
          option.className = `autocomplete-item ${item.ags === state.tollMunicipality ? 'selected' : ''}`;
          option.innerHTML = `<span><strong>${escapeTollHtml(item.name)}</strong></span> <span class="autocomplete-code">${escapeTollHtml(item.ags)}</span>`;
          option.addEventListener('click', () => {
            closeList();
            selectTollMunicipality(item.ags);
          });
          dropdown.appendChild(option);
        });
      }
      dropdown.classList.add('active');
    };

    input.addEventListener('focus', () => input.select());
    input.addEventListener('input', event => renderList(event.target.value));
    input.addEventListener('keydown', event => {
      if (event.key === 'Escape') {
        closeList();
        updateTollMunicipalityInput();
      }
    });
    clearButton?.addEventListener('click', () => {
      state.tollMunicipality = null;
      tollRelations = [];
      tollLoadedSelectionKey = null;
      input.value = '';
      closeList();
      updateTollMunicipalityBoundaryStyles();
      updateAnalysisSummary();
      renderTollEmptySelection();
      input.focus();
    });
    document.addEventListener('click', event => {
      if (!event.target.closest('#controlGroupTollMunicipality')) {
        closeList();
        if (!dropdown.classList.contains('active')) updateTollMunicipalityInput();
      }
    });
  }

  function initializeTollModule() {
    if (!tollMunicipalityData?.municipalities?.length) return;
    buildTollMonthOptions();
    setupTollAutocomplete();
    if (!getTollMunicipalityRecord()) state.tollMunicipality = null;
    updateTollMunicipalityInput();
    tollModuleInitialized = true;
    initializeTollMunicipalityMapSelection();
    updateAnalysisSummary();
  }

  function setTollFilterMode(isToll) {
    const normalGroups = [
      'controlGroupRegion', 'controlGroupYear', 'controlGroupMetric',
      'controlGroupDirection', 'controlGroupGoods'
    ];
    const tollGroups = [
      'controlGroupTollMunicipality', 'controlGroupTollMonth',
      'controlGroupTollMetric', 'controlGroupTollDirection'
    ];
    normalGroups.forEach(id => {
      const element = document.getElementById(id);
      if (element) element.hidden = isToll;
    });
    tollGroups.forEach(id => {
      const element = document.getElementById(id);
      if (element) element.hidden = !isToll;
    });
    document.getElementById('analysisPanelBody')?.classList.toggle('is-toll-mode', isToll);
    const binnenLabel = document.querySelector('#controlGroupBinnenverkehr label');
    if (binnenLabel) {
      binnenLabel.textContent = 'Binnenverkehr:';
      binnenLabel.title = isToll
        ? 'Steuert, ob eine Relation innerhalb derselben Gemeinde in Karte, Tabelle und Diagramm enthalten ist.'
        : 'Darstellungsfilter für Selbstrelationen in Verbindungslinien und Relationstabellen; Kennzahlen und Flächenwerte bleiben unverändert.';
    }
    const binnenSelect = document.getElementById('selectBinnenverkehr');
    if (binnenSelect) {
      const include = binnenSelect.querySelector('option[value="include"]');
      const exclude = binnenSelect.querySelector('option[value="exclude"]');
      if (include) include.textContent = isToll ? 'Einbeziehen' : 'Einbeziehen';
      if (exclude) exclude.textContent = isToll ? 'Ausblenden' : 'Ausblenden';
    }
  }

  function setupTollEventListeners() {
    if (tollEventListenersReady) return;
    tollEventListenersReady = true;
    document.getElementById('selectTollMonth')?.addEventListener('change', event => {
      state.tollMonth = event.target.value;
      tollLoadedSelectionKey = null;
      updateAnalysisSummary();
      loadTollRelations();
    });
    document.getElementById('selectTollMetric')?.addEventListener('change', event => {
      state.tollMetric = event.target.value;
      updateAnalysisSummary();
      if (!tollRequestPending) renderTollData();
    });
    document.getElementById('selectTollDirection')?.addEventListener('change', event => {
      state.tollDirection = event.target.value;
      tollLoadedSelectionKey = null;
      updateAnalysisSummary();
      loadTollRelations();
    });
    document.getElementById('toggleTollConnections')?.addEventListener('change', event => {
      state.showTollConnections = event.target.checked;
      if (!tollRequestPending) renderTollMap(getVisibleTollRows());
    });
    document.getElementById('btnOpenRoadModule')?.addEventListener('click', () => {
      document.querySelector('#mainNav .nav-item[data-tab="tab-road"]')?.click();
    });
  }

  function setTollStatus(kind, message, showRoadLink = false) {
    const banner = document.getElementById('tollStatusBanner');
    const text = document.getElementById('tollStatusText');
    const link = document.getElementById('btnOpenRoadModule');
    if (!banner || !text || !link) return;
    banner.hidden = !message;
    banner.classList.toggle('is-error', kind === 'error');
    banner.classList.toggle('is-loading', kind === 'loading');
    text.textContent = message || '';
    link.hidden = !showRoadLink;
  }

  function setTollMapEmpty(message = '', kind = '') {
    const empty = document.getElementById('tollMapEmpty');
    if (!empty) return;
    empty.textContent = message;
    empty.hidden = !message;
    empty.classList.toggle('is-guidance', kind === 'guidance');
  }

  function setTollChartEmpty(message = '') {
    const canvas = document.getElementById('chartTollDistanceClasses');
    const wrap = canvas?.closest('.chart-canvas-wrap');
    const empty = document.getElementById('tollChartEmpty');
    if (!wrap || !empty) return;
    empty.textContent = message;
    empty.hidden = !message;
    wrap.classList.toggle('has-toll-empty-state', Boolean(message));
  }

  function setTollTableMessage(title, message) {
    const body = document.getElementById('tableTollRelationsBody');
    if (!body) return;
    body.innerHTML = `
      <tr>
        <td colspan="5" class="empty-state-cell">
          <div class="toll-empty-state-content">
            <div class="empty-state-icon"><img src="assets/icons/map.svg" alt="" aria-hidden="true"></div>
            <strong>${escapeTollHtml(title)}</strong><br>
            <span>${message}</span>
          </div>
        </td>
      </tr>`;
  }

  function clearTollMunicipalityBoundaries() {
    const map = maps.toll;
    if (map && mapLayers.toll.municipalityBoundaries) {
      map.removeLayer(mapLayers.toll.municipalityBoundaries);
      mapLayers.toll.municipalityBoundaries = null;
    }
  }

  function updateTollMunicipalityBoundaryStyles() {
    mapLayers.toll.municipalityBoundaries?.eachLayer(layer => {
      const selected = String(layer.feature?.properties?.ags || '') === state.tollMunicipality;
      layer.setStyle({
        color: selected ? '#0f172a' : '#64748b',
        weight: selected ? 2.8 : 0.8,
        opacity: selected ? 1 : 0.72,
        fillColor: selected ? '#79c48a' : '#ffffff',
        fillOpacity: selected ? 0.18 : 0.025
      });
    });
  }

  function getTollMunicipalityBoundaryUrl(fileName) {
    return `${TOLL_MUNICIPALITY_BOUNDARY_BASE_URL}/${fileName}?v=20260902b`;
  }

  function fetchTollMunicipalityBoundaryIndex() {
    if (!tollMunicipalityBoundaryIndexPromise) {
      tollMunicipalityBoundaryIndexPromise = fetch(getTollMunicipalityBoundaryUrl('index.json'), {
        cache: 'force-cache',
        headers: { Accept: 'application/json' }
      }).then(async response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const payload = await response.json();
        if (!Array.isArray(payload?.states) || !payload.states.length || !payload.country_outline_file) {
          throw new Error('Der lokale BKG-Grenzindex ist unvollständig.');
        }
        return payload;
      }).catch(error => {
        tollMunicipalityBoundaryIndexPromise = null;
        throw error;
      });
    }
    return tollMunicipalityBoundaryIndexPromise;
  }

  function fetchTollMunicipalityBoundaryFile(fileName) {
    if (!tollMunicipalityBoundaryPayloads.has(fileName)) {
      const request = fetch(getTollMunicipalityBoundaryUrl(fileName), {
        cache: 'force-cache',
        headers: { Accept: 'application/geo+json, application/json' }
      }).then(async response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const payload = await response.json();
        if (!Array.isArray(payload?.features)) throw new Error(`${fileName}: keine GeoJSON-Features.`);
        return payload;
      }).catch(error => {
        tollMunicipalityBoundaryPayloads.delete(fileName);
        throw error;
      });
      tollMunicipalityBoundaryPayloads.set(fileName, request);
    }
    return tollMunicipalityBoundaryPayloads.get(fileName);
  }

  function tollBboxesOverlap(a, b) {
    return Array.isArray(a) && a.length === 4 && b
      && a[0] <= b.getEast() && a[2] >= b.getWest()
      && a[1] <= b.getNorth() && a[3] >= b.getSouth();
  }

  function buildTollMunicipalityTooltip(municipality, selectable) {
    const hint = selectable
      ? 'Klicken Sie, um diese Gemeinde auszuwählen.'
      : 'Für diese Gemeinde liegen im aktuellen Mautregister keine auswählbaren Relationen vor.';
    return `<div class="map-tooltip"><strong>${escapeTollHtml(municipality.name)}</strong><br><span class="map-tooltip-filter-hint">${hint}</span></div>`;
  }

  async function refreshTollMunicipalityBoundaries() {
    const map = maps.toll;
    if (!map || state.activeTab !== 'tab-toll' || !tollModuleInitialized) return;
    renderStateBoundaries('toll');
    // Relation polygons remain the interactive layer after a municipality has
    // been selected. The local geometry selector is used before that point and
    // again whenever an API error leaves the selection view visible.
    if (state.tollMunicipality && !tollApiFailed) return;
    if (map.getZoom() < TOLL_MUNICIPALITY_MIN_ZOOM) {
      tollMunicipalityBoundaryRequest?.abort();
      tollMunicipalityBoundaryRequest = null;
      clearTollMunicipalityBoundaries();
      if (!state.tollMunicipality && !tollRequestPending) {
        setTollMapEmpty('Zoomen Sie in die Karte, um Gemeindegrenzen einzublenden – oder suchen Sie in den Aktuellen Einstellungen nach einer Gemeinde.', 'guidance');
      }
      return;
    }

    tollMunicipalityBoundaryRequest?.abort();
    const controller = new AbortController();
    tollMunicipalityBoundaryRequest = controller;
    const requestId = ++tollMunicipalityBoundarySequence;
    if (!state.tollMunicipality) setTollMapEmpty('Gemeindegrenzen werden geladen …', 'guidance');
    try {
      const index = await fetchTollMunicipalityBoundaryIndex();
      const stateFiles = index.states.filter(entry => tollBboxesOverlap(entry?.bbox, map.getBounds()));
      if (requestId !== tollMunicipalityBoundarySequence || controller.signal.aborted) return;
      const payloads = await Promise.all(stateFiles.map(entry => fetchTollMunicipalityBoundaryFile(entry.file)));
      if (requestId !== tollMunicipalityBoundarySequence || controller.signal.aborted) return;
      const availableMunicipalities = new Map((tollMunicipalityData?.municipalities || []).map(item => [item.ags, item]));
      const features = payloads.flatMap(payload => payload.features);
      clearTollMunicipalityBoundaries();
      mapLayers.toll.municipalityBoundaries = L.geoJSON({ type: 'FeatureCollection', features }, {
        pane: 'selectionPane',
        style: feature => {
          const selected = String(feature?.properties?.ags || '') === state.tollMunicipality;
          return {
            color: selected ? '#0f172a' : '#64748b',
            weight: selected ? 2.8 : 0.8,
            opacity: selected ? 1 : 0.72,
            fillColor: selected ? '#79c48a' : '#ffffff',
            fillOpacity: selected ? 0.18 : 0.025
          };
        },
        onEachFeature: (feature, layer) => {
          const ags = String(feature?.properties?.ags || '');
          const selectableMunicipality = availableMunicipalities.get(ags);
          const municipality = selectableMunicipality || {
            name: String(feature?.properties?.name || ags)
          };
          bindTollHoverTooltip(
            layer,
            () => buildTollMunicipalityTooltip(municipality, Boolean(selectableMunicipality))
          );
          if (selectableMunicipality) layer.on('click', () => selectTollMunicipality(ags));
        }
      }).addTo(map);
      if (!state.tollMunicipality) {
        setTollMapEmpty(features.length
          ? 'Klicken Sie eine Gemeinde in der Karte an – oder suchen Sie in den Aktuellen Einstellungen nach einer Gemeinde.'
          : 'In diesem Kartenausschnitt wurde keine auswählbare Gemeinde gefunden.', 'guidance');
      }
    } catch (error) {
      if (error?.name === 'AbortError' || requestId !== tollMunicipalityBoundarySequence) return;
      console.warn('Could not load local BKG municipality boundaries:', error);
      clearTollMunicipalityBoundaries();
      if (!state.tollMunicipality) {
        setTollMapEmpty('Gemeindegrenzen sind derzeit nicht verfügbar. Nutzen Sie bitte die Gemeindesuche oben.', 'guidance');
      }
    } finally {
      if (tollMunicipalityBoundaryRequest === controller) tollMunicipalityBoundaryRequest = null;
    }
  }

  function scheduleTollMunicipalityBoundaryRefresh() {
    window.clearTimeout(tollMunicipalityBoundaryTimer);
    tollMunicipalityBoundaryTimer = window.setTimeout(refreshTollMunicipalityBoundaries, 180);
  }

  function initializeTollMunicipalityMapSelection() {
    const map = maps.toll;
    if (!map || tollMunicipalityMapReady) return;
    tollMunicipalityMapReady = true;
    if (!map.getPane('countryBoundaryPane')) {
      map.createPane('countryBoundaryPane');
      map.getPane('countryBoundaryPane').style.zIndex = 445;
    }
    map.on('zoomend', scheduleTollMunicipalityBoundaryRefresh);
    map.on('moveend', scheduleTollMunicipalityBoundaryRefresh);
    if (!map._wbpTollHoverResetBound) {
      map.getContainer().addEventListener('mouseleave', () => {
        closeTollHoverTooltip();
        resetTollPartnerHighlight();
      });
      map._wbpTollHoverResetBound = true;
    }
    if (!map._wbpBkgAttributionAdded) {
      map.attributionControl?.addAttribution('<a href="https://www.bkg.bund.de" target="_blank" rel="noopener noreferrer">© BKG 2025</a> <a href="https://www.govdata.de/dl-de/by-2-0" target="_blank" rel="noopener noreferrer">dl-de/by-2-0</a>, <a href="https://sgx.geodatenzentrum.de/web_public/gdz/datenquellen/datenquellen_vg_nuts.pdf" target="_blank" rel="noopener noreferrer">Datenquellen</a>');
      map._wbpBkgAttributionAdded = true;
    }
    renderStateBoundaries('toll');
    loadTollCountryOutline();
    scheduleTollMunicipalityBoundaryRefresh();
  }

  function loadTollCountryOutline() {
    const map = maps.toll;
    if (!map || mapLayers.toll.countryOutline) return Promise.resolve();
    if (tollCountryOutlinePromise) return tollCountryOutlinePromise;
    tollCountryOutlinePromise = fetchTollMunicipalityBoundaryIndex()
      .then(index => fetchTollMunicipalityBoundaryFile(index.country_outline_file))
      .then(payload => {
        if (!Array.isArray(payload?.features) || !payload.features.length) {
          throw new Error('Die lokale BKG-Datei enthält keine Deutschland-Geometrie.');
        }
        if (mapLayers.toll.countryOutline) map.removeLayer(mapLayers.toll.countryOutline);
        mapLayers.toll.countryOutline = L.geoJSON(payload, {
          pane: 'countryBoundaryPane',
          interactive: false,
          style: {
            // Match the Ländergrenzen: it should orient the map without
            // competing with municipalities or relations.
            color: '#475569',
            weight: 1.15,
            opacity: 0.64,
            fill: false,
            lineCap: 'round',
            lineJoin: 'round'
          }
        }).addTo(map);
      }).catch(error => {
        console.warn('Could not load local BKG country outline:', error);
      }).finally(() => {
        tollCountryOutlinePromise = null;
      });
    return tollCountryOutlinePromise;
  }

  function closeTollHoverTooltip(layer = null) {
    window.clearTimeout(tollHoverTimer);
    tollHoverTimer = null;
    const activeLayer = mapLayers.toll.activeTooltipLayer;
    if (layer && activeLayer && activeLayer !== layer) return;
    activeLayer?.unbindTooltip?.();
    closeActiveRelationTooltip('toll');
  }

  function scheduleTollHoverTooltip(layer, getContent, event, delay = 400) {
    window.clearTimeout(tollHoverTimer);
    closeTollHoverTooltip();
    const latlng = event?.latlng;
    const openTooltip = () => {
      const map = maps.toll;
      if (!map || !latlng) return;
      layer.unbindTooltip?.();
      layer.bindTooltip(getContent(), tollRelationTooltipOptions);
      openActiveRelationTooltip('toll', layer, { latlng });
      tollHoverTimer = null;
    };
    if (delay <= 0) {
      openTooltip();
      return;
    }
    tollHoverTimer = window.setTimeout(openTooltip, delay);
  }

  function bindTollHoverTooltip(layer, getContent, onEnter = null, onLeave = null, options = {}) {
    const delay = Number.isFinite(options.delay) ? Math.max(0, options.delay) : 400;
    layer.on('mouseover', event => {
      layer._wbpTollHoverSequence = ++tollHoverSequence;
      onEnter?.();
      scheduleTollHoverTooltip(layer, getContent, event, delay);
    });
    layer.on('mouseout', () => {
      const hoverSequence = layer._wbpTollHoverSequence;
      window.setTimeout(() => {
        if (hoverSequence !== tollHoverSequence) return;
        onLeave?.();
        closeTollHoverTooltip(layer);
      }, 0);
    });
  }

  function clearTollMap() {
    const map = maps.toll;
    if (!map) return;
    closeTollHoverTooltip();
    if (mapLayers.toll.geojson) {
      map.removeLayer(mapLayers.toll.geojson);
      mapLayers.toll.geojson = null;
    }
    mapLayers.toll.spiderGroup?.clearLayers();
    mapLayers.toll.spiderLookup = {};
    tollActiveHighlightedPartnerAgs = null;
    mapLayers.toll.partnerLayers = {};
    tollViewportBounds = null;
  }

  function clearTollChart() {
    if (chartTollDistanceClasses) {
      chartTollDistanceClasses.destroy();
      chartTollDistanceClasses = null;
    }
    tollDistanceChartKey = null;
  }

  function getTollDistanceChartKey(rows, emptyMessage = '') {
    const relations = rows
      .slice()
      .sort((a, b) => a.partnerAgs.localeCompare(b.partnerAgs))
      .map(row => [row.partnerAgs, row.trips, row.distance].join(':'))
      .join('|');
    return [
      state.tollMunicipality || '',
      state.tollMonth || '',
      state.tollDirection || '',
      state.includeBinnen ? 'include' : 'exclude',
      emptyMessage,
      relations
    ].join('~');
  }

  function renderTollEmptySelection() {
    clearTollMap();
    setTollStatus('', '');
    renderStateBoundaries('toll');
    renderTollDistanceChart([], 'Daten werden nach Auswahl einer Gemeinde angezeigt.');
    setTollMapEmpty('Zoomen Sie in die Karte, um Gemeindegrenzen einzublenden – oder suchen Sie in den Aktuellen Einstellungen nach einer Gemeinde.', 'guidance');
    setText('tollMapTitle', 'Mautrelationen: Gemeinde auswählen');
    setText('tollRelationsTitle', `Top ${state.topX} Relationen: Gemeinde auswählen`);
    setTollTableMessage(
      'Gemeinde auswählen',
      'Zoomen Sie in die Karte und wählen Sie per <strong>Mausklick eine Gemeinde</strong> aus. Alternativ öffnen Sie <strong>Aktuelle Einstellungen → Raum &amp; Zeit</strong> und nutzen dort die Gemeindesuche. Danach werden die wichtigsten Relationen angezeigt.'
    );
    setMapDefaultViewport('toll', true);
    scheduleTollMunicipalityBoundaryRefresh();
  }

  async function fetchTollFeaturePage(where, offset) {
    const params = new URLSearchParams({
      where,
      outFields: '*',
      returnGeometry: 'true',
      orderByFields: 'objectid ASC',
      resultOffset: String(offset),
      resultRecordCount: String(TOLL_PAGE_SIZE),
      f: 'geojson'
    });
    const response = await fetch(`${TOLL_API_QUERY_URL}?${params.toString()}`, {
      cache: 'no-store',
      headers: { Accept: 'application/geo+json, application/json' }
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    if (payload?.error) throw new Error(payload.error.message || 'API-Fehler');
    if (!Array.isArray(payload?.features)) {
      throw new Error('Die API-Antwort enthält keine GeoJSON-Features.');
    }
    return payload;
  }

  async function fetchTollRelationsForDirection(tollDirection) {
    const isOutbound = tollDirection === 'outbound';
    const agsField = isOutbound ? 'ags_start' : 'ags_ziel';
    const direction = isOutbound ? 0 : 1;
    const where = (
      `${agsField} = '${state.tollMunicipality}' AND ` +
      `monat = DATE '${state.tollMonth}-01' AND richtung = ${direction}`
    );
    const features = [];
    let offset = 0;
    while (true) {
      const payload = await fetchTollFeaturePage(where, offset);
      const page = payload.features;
      features.push(...page);
      if (!payload.exceededTransferLimit) break;
      if (!page.length) throw new Error('Leere API-Seite trotz Fortsetzungskennzeichen.');
      offset += page.length;
    }
    features.forEach(feature => {
      const properties = feature?.properties || {};
      const missing = TOLL_REQUIRED_FIELDS.filter(field => !(field in properties));
      if (missing.length) throw new Error(`Unvollständiger Feldsatz: ${missing.join(', ')}`);
      if (String(properties[agsField]) !== state.tollMunicipality || Number(properties.richtung) !== direction) {
        throw new Error('Die API-Antwort weicht von Gemeinde oder Richtung der Abfrage ab.');
      }
    });
    return features;
  }

  async function fetchTollRelations() {
    if (state.tollDirection === 'both') {
      const [outbound, inbound] = await Promise.all([
        fetchTollRelationsForDirection('outbound'),
        fetchTollRelationsForDirection('inbound')
      ]);
      return [...outbound, ...inbound];
    }
    return fetchTollRelationsForDirection(state.tollDirection);
  }

  function numericTollValue(value) {
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  function normalizeTollFeatures(features) {
    const grouped = new Map();
    features.forEach(feature => {
      const properties = feature.properties || {};
      const isOutbound = Number(properties.richtung) === 0;
      const partnerAgsField = isOutbound ? 'ags_ziel' : 'ags_start';
      const partnerNameField = isOutbound ? 'name_ziel' : 'name_start';
      const partnerAgs = String(properties[partnerAgsField] || '');
      if (!partnerAgs) return;
      // A municipal internal trip occurs in both directional API views. It is
      // one relation, not one outbound and one inbound trip, so retain the
      // outbound record once in the combined display.
      if (state.tollDirection === 'both'
        && partnerAgs === state.tollMunicipality
        && !isOutbound) return;
      const trips = numericTollValue(properties.anzahl_befahrungen) || 0;
      let row = grouped.get(partnerAgs);
      if (!row) {
        row = {
          partnerAgs,
          partnerName: String(properties[partnerNameField] || properties.name || partnerAgs),
          trips: 0,
          mileage: 0,
          distanceWeighted: 0,
          timeWeighted: 0,
          distanceWeight: 0,
          timeWeight: 0,
          geometry: feature.geometry || null
        };
        grouped.set(partnerAgs, row);
      }
      row.trips += trips;
      row.mileage += numericTollValue(properties.fahrleistung_km) || 0;
      const distance = numericTollValue(properties.distanz_km_mittelw);
      const time = numericTollValue(properties.zeit_min_mittelw);
      if (distance !== null) {
        row.distanceWeighted += distance * trips;
        row.distanceWeight += trips;
      }
      if (time !== null) {
        row.timeWeighted += time * trips;
        row.timeWeight += trips;
      }
      if (!row.geometry && feature.geometry) row.geometry = feature.geometry;
    });
    return [...grouped.values()].map(row => ({
      partnerAgs: row.partnerAgs,
      partnerName: row.partnerName,
      trips: row.trips,
      mileage: row.mileage,
      distance: row.distanceWeight > 0 ? row.distanceWeighted / row.distanceWeight : null,
      time: row.timeWeight > 0 ? row.timeWeighted / row.timeWeight : null,
      geometry: row.geometry
    }));
  }

  async function loadTollRelations() {
    if (state.activeTab !== 'tab-toll' || !tollModuleInitialized) return;
    const selectionKey = getTollSelectionKey();
    if (!selectionKey) {
      if (!selectionKey) renderTollEmptySelection();
      return;
    }
    const requestId = ++tollRequestSequence;
    tollRequestPending = true;
    tollApiFailed = false;
    setTollStatus('', '');
    setModuleLoadingState('tab-toll', true);
    const loadingNotice = document.querySelector('#tab-toll .module-loading-status');
    if (loadingNotice) loadingNotice.textContent = 'Mautdaten werden live aus der Toll-Collect-API geladen …';
    setTollMapEmpty('Live-Daten werden geladen …');
    const body = document.getElementById('tableTollRelationsBody');
    if (body) body.innerHTML = '<tr><td colspan="5" class="empty-state-cell">Live-Daten werden geladen …</td></tr>';
    try {
      const features = await fetchTollRelations();
      if (requestId !== tollRequestSequence) return;
      tollRelations = normalizeTollFeatures(features);
      tollLoadedSelectionKey = selectionKey;
      tollApiFailed = false;
      setTollStatus('', '');
      renderTollData();
    } catch (error) {
      if (requestId !== tollRequestSequence) return;
      console.error('Could not load live Toll Collect relations:', error);
      tollRelations = [];
      tollLoadedSelectionKey = selectionKey;
      tollApiFailed = true;
      renderTollApiError();
    } finally {
      if (requestId === tollRequestSequence) {
        tollRequestPending = false;
        setModuleLoadingState('tab-toll', false);
      }
    }
  }

  function renderTollApiError() {
    const keepMunicipalityViewport = Boolean(mapLayers.toll.municipalityBoundaries);
    clearTollMap();
    setTollMapEmpty('Die Mautdaten-API ist derzeit nicht erreichbar.');
    renderStateBoundaries('toll');
    renderTollDistanceChart([], 'Für das Diagramm sind derzeit keine Live-Daten verfügbar.');
    setTollStatus(
      'error',
      'Die Mautdaten-API ist derzeit nicht erreichbar. Weitere Daten zum Straßengüterverkehr sind im Analysemodul „Straßengüterverkehr“ verfügbar.',
      true
    );
    setTollTableMessage('Keine Live-Daten verfügbar', 'Die gewählte Gemeinde bleibt aktiv. Versuchen Sie den Abruf später erneut oder öffnen Sie das Modul Straßengüterverkehr.');
    setText('tollMapTitle', `Mautrelationen: ${getTollMunicipalityLabel()}`);
    setText('tollRelationsTitle', `Top ${state.topX} Relationen: keine Live-Daten`);
    if (!keepMunicipalityViewport) setMapDefaultViewport('toll', true);
  }

  function getTollMetricValue(row) {
    return numericTollValue(row?.[TOLL_METRICS[state.tollMetric]?.field || 'trips']) || 0;
  }

  function getVisibleTollRows() {
    const rows = state.includeBinnen
      ? tollRelations
      : tollRelations.filter(row => row.partnerAgs !== state.tollMunicipality);
    const totalTrips = rows.reduce((sum, row) => sum + row.trips, 0);
    return [...rows]
      .sort((a, b) => getTollMetricValue(b) - getTollMetricValue(a) || a.partnerName.localeCompare(b.partnerName, 'de'))
      .map((row, index) => ({
        ...row,
        rank: index + 1,
        tripShare: totalTrips > 0 ? row.trips / totalTrips * 100 : 0
      }));
  }

  function formatTollMetricValue(value, metricKey = state.tollMetric) {
    const metric = TOLL_METRICS[metricKey] || TOLL_METRICS.trips;
    const number = numericTollValue(value);
    if (number === null) return '–';
    const decimals = metricKey === 'distance' || metricKey === 'time' ? 1 : 0;
    return `${formatDeNum(number, decimals, decimals)}${metric.unit ? ` ${metric.unit}` : ''}`;
  }

  function formatTollConnectionValue(value, metricKey = state.tollMetric) {
    const number = numericTollValue(value);
    if (number === null) return '–';
    return formatDeNum(number, 0, 0);
  }

  function getTollConnectionClassification(rows) {
    const values = rows.map(getTollMetricValue).filter(value => value > 0);
    if (!values.length) {
      return {
        labelThin: '–', labelMed: '–', labelThick: '–',
        getWeight: () => 2.2
      };
    }
    const maxValue = Math.max(...values);
    const magnitude = 10 ** Math.floor(Math.log10(maxValue));
    const normalized = maxValue / magnitude;
    let lower;
    let upper;
    if (normalized < 2) {
      lower = 0.4 * magnitude;
      upper = 0.9 * magnitude;
    } else if (normalized < 4) {
      lower = 1 * magnitude;
      upper = 2 * magnitude;
    } else if (normalized < 7) {
      lower = magnitude < 10 ? 1.5 * magnitude : 2 * magnitude;
      upper = magnitude < 10 ? 3.5 * magnitude : 4 * magnitude;
    } else {
      lower = 2 * magnitude;
      upper = 5 * magnitude;
    }
    if (upper >= maxValue) {
      lower = maxValue * 0.3;
      upper = maxValue * 0.65;
    }
    const wholeNumberMetric = state.tollMetric === 'trips' || state.tollMetric === 'mileage';
    if (wholeNumberMetric) {
      lower = Math.max(1, Math.round(lower));
      upper = Math.max(lower + 1, Math.round(upper));
    }
    const unit = TOLL_METRICS[state.tollMetric]?.unit || '';
    const withUnit = value => `${formatTollConnectionValue(value)}${unit ? ` ${unit}` : ''}`;
    return {
      labelThin: `< ${withUnit(lower)}`,
      labelMed: `${formatTollConnectionValue(lower)} – ${withUnit(upper)}`,
      labelThick: `> ${withUnit(upper)}`,
      getWeight: value => value < lower ? 2.2 : (value < upper ? 3.8 : 5.6)
    };
  }

  function getTollGeometryRepresentativePoint(geometry) {
    if (!geometry?.coordinates) return null;
    const polygons = geometry.type === 'Polygon'
      ? [geometry.coordinates]
      : geometry.type === 'MultiPolygon' ? geometry.coordinates : [];
    if (!polygons.length) return null;
    const ringAreaTwice = ring => ring.reduce((sum, point, index) => {
      const next = ring[(index + 1) % ring.length];
      return sum + point[0] * next[1] - next[0] * point[1];
    }, 0);
    const polygon = polygons.reduce((largest, candidate) => {
      const candidateArea = Math.abs(ringAreaTwice(candidate[0] || []));
      const largestArea = Math.abs(ringAreaTwice(largest?.[0] || []));
      return candidateArea > largestArea ? candidate : largest;
    }, polygons[0]);
    const ring = polygon?.[0] || [];
    if (ring.length < 3) return null;
    const areaTwice = ringAreaTwice(ring);
    if (Math.abs(areaTwice) < 1e-12) {
      const lngs = ring.map(point => point[0]);
      const lats = ring.map(point => point[1]);
      return L.latLng((Math.min(...lats) + Math.max(...lats)) / 2, (Math.min(...lngs) + Math.max(...lngs)) / 2);
    }
    let lngSum = 0;
    let latSum = 0;
    ring.forEach((point, index) => {
      const next = ring[(index + 1) % ring.length];
      const cross = point[0] * next[1] - next[0] * point[1];
      lngSum += (point[0] + next[0]) * cross;
      latSum += (point[1] + next[1]) * cross;
    });
    return L.latLng(latSum / (3 * areaTwice), lngSum / (3 * areaTwice));
  }

  function getTollDirectionLabel(direction = state.tollDirection) {
    if (direction === 'outbound') return 'Von Gemeinde';
    if (direction === 'inbound') return 'Zu Gemeinde';
    return 'Beide Richtungen';
  }

  function formatTollTripShare(value) {
    const number = numericTollValue(value);
    if (number === null || number <= 0) return '0,0';
    if (number < 0.01) return '&lt; 0,01';
    const decimals = number < 0.1 ? 2 : 1;
    return formatDeNum(number, decimals, decimals);
  }

  function buildTollTooltip(row) {
    const selected = getTollMunicipalityLabel();
    const isOutbound = state.tollDirection === 'outbound';
    const isInbound = state.tollDirection === 'inbound';
    const origin = isInbound ? row.partnerName : selected;
    const destination = isInbound ? selected : row.partnerName;
    const arrow = isOutbound ? '→' : isInbound ? '→' : '↔';
    return `
      <div class="map-tooltip toll-map-tooltip">
        <div class="toll-map-tooltip-eyebrow">
          <span>Monat und Jahr: ${escapeTollHtml(formatTollMonth(state.tollMonth))}</span>
          <span>Richtung: ${getTollDirectionLabel()}</span>
        </div>
        <div class="toll-map-tooltip-title">
          ${escapeTollHtml(origin)} <span class="toll-map-tooltip-route-arrow">${arrow}</span> ${escapeTollHtml(destination)}
        </div>
        <div class="toll-map-tooltip-details">
          <div><strong>Mautfahrten:</strong> ${formatDeNum(row.trips, 0)}</div>
          <div><strong>Fahrleistung:</strong> ${formatDeNum(row.mileage, 0)} km</div>
          <div><strong>Mittlere Distanz:</strong> ${formatDeNum(row.distance, 1, 1)} km</div>
          <div><strong>Mittlere Fahrzeit:</strong> ${formatDeNum(row.time, 1, 1)} Min.</div>
          <div class="toll-map-tooltip-context">Platz ${row.rank} · Anteil der Mautfahrten: <strong>${formatTollTripShare(row.tripShare)} %</strong></div>
        </div>
      </div>`;
  }

  const tollRelationTooltipOptions = {
    className: 'toll-relation-leaflet-tooltip',
    direction: 'top',
    offset: [0, -7],
    opacity: 0.98,
    interactive: false
  };

  function getTollFillColor(value, maxValue) {
    if (!Number.isFinite(value) || value <= 0) return '#f1f5f9';
    if (state.tollMetric === 'distance') {
      const classIndex = TOLL_DISTANCE_CLASSES.findIndex(distanceClass => (
        value >= distanceClass.lower && value < distanceClass.upper
      ));
      return TOLL_DISTANCE_CLASS_COLORS[classIndex] || TOLL_DISTANCE_CLASS_COLORS.at(-1);
    }
    const ratio = Math.sqrt(Math.min(1, value / Math.max(maxValue, 1)));
    if (ratio < 0.2) return '#e8f5ec';
    if (ratio < 0.4) return '#b9dfc2';
    if (ratio < 0.6) return '#79c48a';
    if (ratio < 0.8) return '#63b472';
    return '#4c7f83';
  }

  function resetTollPartnerHighlight() {
    document.querySelectorAll('#tableTollRelationsBody tr').forEach(row => row.classList.remove('row-highlight'));
    Object.entries(mapLayers.toll.partnerLayers || {}).forEach(([partnerAgs, layer]) => {
      layer.setStyle({
        weight: partnerAgs === state.tollMunicipality ? 2.8 : 0.8,
        color: partnerAgs === state.tollMunicipality ? '#0f172a' : '#64748b'
      });
    });
    Object.values(mapLayers.toll.spiderLookup || {}).forEach(connection => {
      connection.line?.setStyle({
        color: connection.originalColor || TOLL_CONNECTION_COLOR,
        weight: connection.originalWeight || 2.2,
        opacity: connection.originalOpacity ?? 0.75
      });
      connection.marker?.setStyle({
        fillColor: connection.originalColor || TOLL_CONNECTION_COLOR,
        radius: connection.originalRadius || connection.markerRadius || 4.5,
        color: '#ffffff',
        weight: 2,
        fillOpacity: 0.95
      });
    });
    tollActiveHighlightedPartnerAgs = null;
  }

  function highlightTollPartner(partnerAgs, active) {
    if (!active) {
      if (tollActiveHighlightedPartnerAgs === partnerAgs) resetTollPartnerHighlight();
      return;
    }
    // A new relation always restores every prior visual state first. This is
    // deliberately independent of Leaflet's mouseout timing, which can vary
    // while the pointer crosses endpoints, SVG lines and table rows.
    resetTollPartnerHighlight();
    tollActiveHighlightedPartnerAgs = partnerAgs;
    document.querySelector(`#tableTollRelationsBody tr[data-partner-id="${partnerAgs}"]`)?.classList.add('row-highlight');
    const layer = mapLayers.toll.partnerLayers?.[partnerAgs];
    if (layer) {
      layer.setStyle({ weight: 3, color: TOLL_CONNECTION_HIGHLIGHT_COLOR });
      layer.bringToFront?.();
    }
    const connection = mapLayers.toll.spiderLookup?.[partnerAgs];
    connection?.line?.setStyle({
      color: TOLL_CONNECTION_HIGHLIGHT_COLOR,
      weight: Math.max(5.5, (connection.originalWeight || 2.2) + 2.2),
      opacity: 1
    });
    connection?.marker?.setStyle({
      fillColor: TOLL_CONNECTION_HIGHLIGHT_COLOR,
      radius: Math.max(6.5, (connection.originalRadius || connection.markerRadius || 4.5) + 2),
      color: '#ffffff',
      weight: 2.8,
      fillOpacity: 1
    });
    connection?.marker?.bringToFront?.();
  }
  function renderTollMap(rows) {
    const map = maps.toll;
    if (!map) return;
    clearTollMap();
    clearTollMunicipalityBoundaries();
    renderStateBoundaries('toll');
    if (!rows.length) {
      setTollMapEmpty('Für diese Auswahl wurden keine Relationen geliefert.');
      setMapDefaultViewport('toll', true);
      return;
    }
    setTollMapEmpty('');
    const metric = TOLL_METRICS[state.tollMetric] || TOLL_METRICS.trips;
    const maxValue = Math.max(...rows.map(getTollMetricValue), 1);
    const positiveValues = rows.map(getTollMetricValue).filter(value => value > 0);
    const minValue = positiveValues.length ? Math.min(...positiveValues) : 0;
    const featureCollection = {
      type: 'FeatureCollection',
      features: rows
        .filter(row => row.geometry)
        .map(row => ({
          type: 'Feature',
          geometry: row.geometry,
          properties: { tollRow: row }
        }))
    };
    mapLayers.toll.partnerLayers = {};
    mapLayers.toll.geojson = L.geoJSON(featureCollection, {
      renderer: getNutsRegionRenderer(map),
      style: feature => {
        const row = feature.properties.tollRow;
        const selected = row.partnerAgs === state.tollMunicipality;
        return {
          fillColor: getTollFillColor(getTollMetricValue(row), maxValue),
          fillOpacity: selected ? 0.88 : 0.68,
          color: selected ? '#0f172a' : '#64748b',
          weight: selected ? 2.8 : 0.8,
          opacity: 1
        };
      },
      onEachFeature: (feature, layer) => {
        const row = feature.properties.tollRow;
        mapLayers.toll.partnerLayers[row.partnerAgs] = layer;
        bindTollHoverTooltip(
          layer,
          () => buildTollTooltip(row),
          () => highlightTollPartner(row.partnerAgs, true),
          () => highlightTollPartner(row.partnerAgs, false)
        );
        layer.on('click', () => selectTollMunicipality(row.partnerAgs));
      }
    }).addTo(map);

    const bounds = mapLayers.toll.geojson.getBounds();
    tollViewportBounds = bounds.isValid() ? bounds : null;
    setText('tollLegendTitle', metric.label);
    const isDistanceMetric = state.tollMetric === 'distance';
    const legendScale = document.querySelector('#tollChoroplethLegend .toll-legend-scale');
    legendScale?.classList.toggle('is-distance-classes', isDistanceMetric);
    const legendLabels = document.getElementById('tollLegendLabels');
    if (legendLabels) {
      legendLabels.classList.toggle('is-distance-classes', isDistanceMetric);
      legendLabels.innerHTML = isDistanceMetric
        ? '<span>&lt; 50 km</span><span>≥ 300 km</span>'
        : `<span>${formatTollMetricValue(minValue)}</span><span>${formatTollMetricValue(maxValue)}</span>`;
    }

    const selfRow = tollRelations.find(row => row.partnerAgs === state.tollMunicipality && row.geometry);
    const origin = getTollGeometryRepresentativePoint(selfRow?.geometry);
    const topRows = rows.slice(0, state.topX).filter(row => row.partnerAgs !== state.tollMunicipality);
    const connectionClassification = getTollConnectionClassification(topRows);
    if (state.showTollConnections && origin) {
      // As in the other relations modules, one point marks the selected
      // municipality and a point at every partner makes both ends legible.
      L.circleMarker([origin.lat, origin.lng], {
        pane: 'connectionPane',
        className: 'flow-relation-target',
        radius: 6,
        fillColor: TOLL_CONNECTION_COLOR,
        color: '#ffffff',
        weight: 2.2,
        fillOpacity: 0.96,
        interactive: false
      }).addTo(mapLayers.toll.spiderGroup);
      topRows.forEach(row => {
        const partnerLayer = mapLayers.toll.partnerLayers[row.partnerAgs];
        if (!partnerLayer) return;
        const destination = getTollGeometryRepresentativePoint(row.geometry);
        if (!destination) return;
        const lineWeight = connectionClassification.getWeight(getTollMetricValue(row));
        const line = L.polyline([origin, destination], {
          pane: 'connectionPane',
          color: TOLL_CONNECTION_COLOR,
          weight: lineWeight,
          opacity: 0.75,
          interactive: false
        }).addTo(mapLayers.toll.spiderGroup);
        const hitLine = L.polyline([origin, destination], {
          pane: 'connectionPane',
          color: '#ffffff',
          weight: Math.max(14, lineWeight + 8),
          opacity: 0,
          interactive: true,
          bubblingMouseEvents: false
        }).addTo(mapLayers.toll.spiderGroup);        const markerRadius = Math.max(4.5, lineWeight + 1);
        const marker = L.circleMarker([destination.lat, destination.lng], {
          pane: 'connectionPane',
          className: 'flow-relation-target',
          radius: markerRadius,
          fillColor: TOLL_CONNECTION_COLOR,
          color: '#ffffff',
          weight: 2,
          fillOpacity: 0.95
        }).addTo(mapLayers.toll.spiderGroup);
        const highlight = () => highlightTollPartner(row.partnerAgs, true);
        const clearHighlight = () => highlightTollPartner(row.partnerAgs, false);
        bindTollHoverTooltip(hitLine, () => buildTollTooltip(row), highlight, clearHighlight, { delay: 0 });
        bindTollHoverTooltip(marker, () => buildTollTooltip(row), highlight, clearHighlight, { delay: 0 });
        marker.on('click', () => selectTollMunicipality(row.partnerAgs));
        mapLayers.toll.spiderLookup[row.partnerAgs] = {
          line,
          hitLine,
          marker,
          markerRadius,
          originalColor: TOLL_CONNECTION_COLOR,
          originalWeight: lineWeight,
          originalRadius: markerRadius,
          originalOpacity: 0.75
        };
      });
    }
    const connectionSection = document.getElementById('tollLegendConnectionSection');
    if (connectionSection) {
      connectionSection.style.display = state.showTollConnections && origin && topRows.length ? 'block' : 'none';
      setText('tollConnectionLegendTitle', 'Verbindungen');
      setText('tollConnectionLegendThin', connectionClassification.labelThin);
      setText('tollConnectionLegendMedium', connectionClassification.labelMed);
      setText('tollConnectionLegendThick', connectionClassification.labelThick);
    }
    setMapDefaultViewport('toll', true);
  }

  function renderTollTable(rows) {
    const body = document.getElementById('tableTollRelationsBody');
    if (!body) return;
    const topRows = rows.slice(0, state.topX);
    if (!topRows.length) {
      body.innerHTML = '<tr><td colspan="5" class="empty-state-cell">Für diese Auswahl wurden keine Relationen geliefert.</td></tr>';
      return;
    }
    body.innerHTML = topRows.map(row => {
      const binnenBadge = row.partnerAgs === state.tollMunicipality
        ? '<span class="toll-binnen-badge">Binnen</span>'
        : '';
      return `
      <tr data-partner-id="${escapeTollHtml(row.partnerAgs)}" tabindex="0">
        <td class="toll-partner-cell"><span class="relation-rank" aria-label="Rang ${row.rank}">${row.rank}<span class="relation-rank-separator" aria-hidden="true">·</span></span><span class="toll-partner-details"><strong>${escapeTollHtml(row.partnerName)}</strong>${binnenBadge}<span class="table-sub-label">(${escapeTollHtml(row.partnerAgs)})</span></span></td>
        <td class="numeric">${formatDeNum(row.trips, 0)}</td>
        <td class="numeric">${formatDeNum(row.mileage, 0)} km</td>
        <td class="numeric">${formatDeNum(row.distance, 1, 1)} km</td>
        <td class="numeric">${formatDeNum(row.time, 1, 1)} Min.</td>
      </tr>`;
    }).join('');
    body.querySelectorAll('tr[data-partner-id]').forEach(tableRow => {
      const partnerAgs = tableRow.dataset.partnerId;
      tableRow.addEventListener('mouseenter', () => highlightTollPartner(partnerAgs, true));
      tableRow.addEventListener('mouseleave', () => highlightTollPartner(partnerAgs, false));
      tableRow.addEventListener('focus', () => highlightTollPartner(partnerAgs, true));
      tableRow.addEventListener('blur', () => highlightTollPartner(partnerAgs, false));
      tableRow.addEventListener('click', () => {
        const layer = mapLayers.toll.partnerLayers?.[partnerAgs];
        if (layer) maps.toll?.fitBounds(layer.getBounds(), { padding: [30, 30], maxZoom: 10 });
      });
    });
  }

  function renderTollDistanceChart(rows, emptyMessage = '') {
    const chartKey = getTollDistanceChartKey(rows, emptyMessage);
    const canvas = document.getElementById('chartTollDistanceClasses');
    if (!canvas || typeof Chart === 'undefined') return;
    if (chartTollDistanceClasses && tollDistanceChartKey === chartKey) {
      setTollChartEmpty(emptyMessage);
      return;
    }
    clearTollChart();
    setTollChartEmpty(emptyMessage);
    const totalTrips = rows.reduce((sum, row) => sum + row.trips, 0);
    const chartClasses = [...TOLL_DISTANCE_CLASSES].reverse();
    const classTrips = chartClasses.map(distanceClass => rows
      .filter(row => Number.isFinite(row.distance)
        && row.distance >= distanceClass.lower
        && row.distance < distanceClass.upper)
      .reduce((sum, row) => sum + row.trips, 0));
    const shares = classTrips.map(value => totalTrips > 0 ? value / totalTrips * 100 : 0);
    chartTollDistanceClasses = new Chart(canvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels: chartClasses.map(item => item.label),
        datasets: [{
          label: 'Anteil der Mautfahrten',
          data: shares,
          backgroundColor: [...TOLL_DISTANCE_CLASS_COLORS].reverse(),
          borderRadius: 4,
          borderSkipped: false,
          tollTrips: classTrips
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: context => {
                const trips = context.dataset.tollTrips?.[context.dataIndex] || 0;
                return ` Anteil: ${formatDeNum(context.raw, 1, 1)} % (${formatDeNum(trips, 0)} Mautfahrten)`;
              }
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            suggestedMax: Math.max(25, Math.ceil(Math.max(...shares, 0) / 10) * 10),
            grid: { color: '#e2e8f0' },
            ticks: { callback: value => `${formatDeNum(value, 0)} %` }
          },
          y: {
            grid: { display: false },
            ticks: { font: { size: 11 } }
          }
        }
      }
    });
    tollDistanceChartKey = chartKey;
  }

  function renderTollData() {
    if (state.activeTab !== 'tab-toll') return;
    if (tollApiFailed) {
      renderTollApiError();
      return;
    }
    const rows = getVisibleTollRows();
    const selected = getTollMunicipalityLabel();
    const direction = state.tollDirection === 'outbound'
      ? 'mit Start in'
      : state.tollDirection === 'inbound' ? 'mit Ziel in' : 'mit Start oder Ziel in';
    setText('tollMapTitle', `Mautrelationen ${direction} ${selected}, ${formatTollMonth(state.tollMonth)}`);
    setText('tollRelationsTitle', `Top ${state.topX} Relationen: ${selected} · ${getTollDirectionLabel()}`);
    renderTollMap(rows);
    renderTollTable(rows);
    renderTollDistanceChart(rows);
  }

  function renderTollTab() {
    if (!tollModuleInitialized) return;
    if (!state.tollMunicipality) {
      renderTollEmptySelection();
      return;
    }
    const selectionKey = getTollSelectionKey();
    if (selectionKey !== tollLoadedSelectionKey && !tollRequestPending) {
      loadTollRelations();
      return;
    }
    if (!tollRequestPending) renderTollData();
  }
