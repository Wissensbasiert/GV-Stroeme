  // Shared loading, failure recovery and delivery-partition access.
  const pendingDataLoads = new Map();
  const loadedSummaryDetails = new Set();
  const loadedForecastDetails = new Set();

  function requestDataOnce(key, loader) {
    if (!pendingDataLoads.has(key)) {
      const request = Promise.resolve().then(loader).catch(error => {
        pendingDataLoads.delete(key);
        throw error;
      });
      pendingDataLoads.set(key, request);
    }
    return pendingDataLoads.get(key);
  }

  function showDataLoadError(container, message, retry) {
    if (!container) return;
    container.setAttribute('aria-busy', 'false');
    container.dataset.loadError = 'true';
    container.querySelector('.module-loading-overlay')?.remove();
    let notice = container.querySelector('.module-loading-status');
    if (!notice) {
      notice = document.createElement('div');
      notice.className = 'module-loading-status';
      container.prepend(notice);
    }
    notice.setAttribute('role', 'alert');
    const label = document.createElement('span');
    label.textContent = message;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn-header data-retry-button';
    button.textContent = 'Erneut versuchen';
    button.addEventListener('click', () => { button.disabled = true; retry(); });
    notice.replaceChildren(label, button);
    notice.hidden = false;
  }

  const moduleLoadingTimers = new Map();
  function setModuleLoadingState(tabId, isLoading) {
    const pane = document.getElementById(tabId);
    if (!pane) return;
    delete pane.dataset.loadError;
    pane.setAttribute('aria-busy', String(isLoading));
    const errorNotice = pane.querySelector('.module-loading-status:not(.module-loading-overlay)');
    if (errorNotice) errorNotice.hidden = true;
    let notice = pane.querySelector('.module-loading-overlay');
    if (!notice) {
      notice = document.createElement('div');
      notice.className = 'module-loading-status module-loading-overlay';
      const host = pane.querySelector('.map-container-leaflet') || pane;
      host.classList.add('module-loading-host');
      host.append(notice);
    }
    notice.setAttribute('role', 'status');
    notice.textContent = 'Bitte einen Augenblick Geduld, Daten werden geladen …';
    clearTimeout(moduleLoadingTimers.get(tabId));
    moduleLoadingTimers.delete(tabId);
    notice.hidden = true;
    if (isLoading) moduleLoadingTimers.set(tabId, setTimeout(() => {
      moduleLoadingTimers.delete(tabId);
      if (pane.getAttribute('aria-busy') === 'true' && pane.dataset.loadError !== 'true' && notice.isConnected) notice.hidden = false;
    }, 1500));
  }

  // Keep local rebuilds fresh; bound stalled requests without bypassing TLS/CORS.
  async function fetchJson(url, _fallback, { timeoutMs = 30000, signal } = {}) {
    const controller = new AbortController();
    const abort = () => controller.abort();
    if (signal?.aborted) abort();
    else signal?.addEventListener('abort', abort, { once: true });
    const timer = setTimeout(abort, timeoutMs);
    try {
      const response = await fetch(url, { cache: 'no-store', signal: controller.signal });
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${url}`);
      return await response.json();
    } finally {
      clearTimeout(timer);
      signal?.removeEventListener('abort', abort);
    }
  }

  function hasRegionalSummaryData() {
    return Object.keys(summaryData || {}).length > 0;
  }

  async function ensureSummaryData(regionId = state.region) {
    try {
      await requestDataOnce('summary', async () => {
        const data = await fetchJson('data/processed/web_summary_core.json');
        if (data?.format !== 1 || !data.regions || !data.national) throw new Error('Invalid summary delivery data');
        summaryData = data.regions;
        nationalSummaryData = data.national;
      });
      if (regionId && summaryData[regionId] && !loadedSummaryDetails.has(regionId)) {
        await requestDataOnce(`summary:${regionId}`, async () => {
          const detail = await fetchJson(`data/processed/delivery/summary/${encodeURIComponent(regionId)}.json`);
          for (const year of Object.keys(summaryData[regionId])) {
            if (!detail[year]) throw new Error(`Missing regional summary year: ${year}`);
          }
          for (const [year, record] of Object.entries(detail)) Object.assign(summaryData[regionId][year], record);
          loadedSummaryDetails.add(regionId);
        });
      }
      return true;
    } catch (error) {
      console.error('Could not load regional summary data:', error);
      return false;
    }
  }

  async function ensureForecastRegionData(regionId = state.region) {
    if (!regionId || loadedForecastDetails.has(regionId)) return true;
    const scenarioIds = Object.keys(forecastData?.scenarios || {}).filter(id => forecastData.scenarios[id].regions?.[regionId]);
    if (!scenarioIds.length) return true; // Region outside the forecast source coverage.
    await requestDataOnce(`forecast:${regionId}`, async () => {
      const detail = await fetchJson(`data/processed/delivery/forecast/${encodeURIComponent(regionId)}.json`);
      for (const id of scenarioIds) {
        if (!detail[id]?.relations_overall || !detail[id]?.by_group_relations) throw new Error(`Incomplete forecast region: ${regionId}`);
      }
      for (const id of scenarioIds) Object.assign(forecastData.scenarios[id].regions[regionId], detail[id]);
      loadedForecastDetails.add(regionId);
    });
    return true;
  }

  async function ensureOverviewForecastTooltipData() {
    try {
      await requestDataOnce('overview-forecast', async () => {
        const data = await fetchJson('data/processed/web_forecast_overview_tooltip.json');
        if (!data?.scenarios) throw new Error('Invalid forecast preview');
        overviewForecastTooltipData = data;
      });
      return true;
    } catch (error) {
      console.warn('Could not load overview forecast tooltip data:', error);
      return false;
    }
  }

  async function ensureModuleData(moduleName) {
    const available = {
      maritime: () => Boolean(maritimeData),
      airfreight: () => Boolean(airfreightData),
      intermodal: () => Boolean(intermodalData),
      forecast: () => Boolean(forecastData),
      toll: () => Boolean(tollMunicipalityData)
    };

    const loaders = {
      maritime: async () => { maritimeData = await fetchJson('data/processed/web_maritime.json?v=20260821n', {}); },
      airfreight: async () => { airfreightData = await fetchJson('data/processed/web_airfreight.json?v=20260904-airfreight-dataquality1', {}); },
      // This file is regenerated by the data pipeline.  The explicit revision
      // clears copies from older application sessions; no-store also protects
      // later data refreshes when the frontend bundle itself is unchanged.
      intermodal: async () => {
        intermodalData = await fetchJson(
          'data/processed/web_intermodal.json?v=20260901-international-relations',
          {}
        );
      },
      forecast: async () => {
        const [forecastRes, centroidsRes, spatialCrosswalkRes, nstCrosswalkRes] = await Promise.all([
          fetchJson('data/processed/web_forecast_core.json', null),
          fetchJson('data/processed/nuts_centroids_vp2040.json', {}),
          fetchJson('data/crosswalks/crosswalk_spatial_vp2040.json', []),
          fetchJson('data/crosswalks/crosswalk_nst_vp2040.json', [])
        ]);
        forecastData = forecastRes;
        centroidsVp2040 = centroidsRes;
        crosswalkSpatialVp = spatialCrosswalkRes;
        crosswalkNstVp = nstCrosswalkRes;
        if (Array.isArray(crosswalkSpatialVp)) {
          crosswalkSpatialVp.forEach(item => {
            const cid = String(item.cell_id);
            if (item.nuts3_2024) nutsToVpCell[item.nuts3_2024] = cid;
            if (item.nuts3_2016) nutsToVpCell[item.nuts3_2016] = cid;
            if (item.ags_5stellig) nutsToVpCell[item.ags_5stellig] = cid;
            vpCellToNuts[cid] = item.nuts3_2024 || item.nuts3_2016 || cid;
          });
        }
      },
      toll: async () => {
        tollMunicipalityData = await fetchJson('data/processed/toll_municipalities.json?v=20260902a', null);
        initializeTollModule();
      }
    };

    try {
      if (!available[moduleName]?.()) await requestDataOnce(`module:${moduleName}`, loaders[moduleName]);
      if (moduleName === 'forecast') await ensureForecastRegionData();
      return true;
    } catch (error) {
      console.error(`Could not load ${moduleName} module data:`, error);
      return false;
    }
  }
