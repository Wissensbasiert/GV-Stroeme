/**
 * Güterverkehrsströme Deutschland - Main Application Controller
 * Wissensbasierte Planung (WBP) - Dr. Paul Hebes (wissensbasiert.de)
 */

(function () {
  'use strict';

  // Common national extent for the land-transport maps. Let Leaflet fit this
  // extent to the *actual* map frame instead of using a hard-coded zoom level:
  // browser zoom, a collapsed sidebar, and varying card heights otherwise
  // crop different parts of Germany in different modules.
  const GERMANY_BOUNDS = [[47.20, 5.50], [55.15, 15.35]];
  // Purposeful national coast framing for the maritime module. It keeps the
  // North Sea and Baltic Sea ports in view without allocating map space to
  // southern Germany, where this module has no locations.
  const MARITIME_COAST_BOUNDS = [[52.90, 6.50], [55.25, 14.60]];
  const mapViewportInitialized = {};
  const mapViewportTimers = {};

  // Verified coordinate corrections for locations that were missing from an
  // earlier export. Unknown locations are never placed at a generic fallback.
  const MARITIME_COORDINATE_OVERRIDES = Object.freeze({
    DENHA: { lat: 53.4833, lng: 8.4833 }, // Nordenham
    DESTL: { lat: 54.3000, lng: 13.1000 }, // Stralsund
    DEVIW: { lat: 54.1303, lng: 13.5724 }, // Vierow
    DEBSK: { lat: 54.5008, lng: 11.2260 }, // Puttgarden / Fehmarn
    DEPAP: { lat: 53.1004, lng: 7.3652 }, // Papenburg
    DELBM: { lat: 54.1550, lng: 13.6433 }  // Industriehafen Lubmin
  });

  function renderExternalChartTooltip(context) {
    const { chart, tooltip } = context;
    const canvas = chart?.canvas;
    if (!canvas?.id) return;
    const tooltipId = `chart-hover-tooltip-${canvas.id}`;
    let element = document.getElementById(tooltipId);
    if (!element) {
      element = document.createElement('div');
      element.id = tooltipId;
      element.className = 'chart-hover-tooltip';
      element.setAttribute('role', 'tooltip');
      document.body.appendChild(element);
    }
    if (!tooltip || tooltip.opacity === 0) {
      element.classList.remove('is-visible');
      return;
    }

    // The point hover and the axis-label hover describe one pointer position.
    // Hide the label panel before showing chart data so the two never overlap.
    document.getElementById(`chart-axis-label-tooltip-${canvas.id}`)?.classList.remove('is-visible');

    element.replaceChildren();
    const titleLines = tooltip.title || [];
    if (titleLines.length) {
      const title = document.createElement('div');
      title.className = 'chart-hover-tooltip-title';
      title.textContent = titleLines.join(' ');
      element.appendChild(title);
    }
    (tooltip.body || []).forEach((bodyItem, index) => {
      const row = document.createElement('div');
      row.className = 'chart-hover-tooltip-row';
      const color = tooltip.labelColors?.[index];
      if (color?.backgroundColor) {
        const swatch = document.createElement('span');
        swatch.className = 'chart-hover-tooltip-swatch';
        swatch.style.background = color.backgroundColor;
        swatch.style.borderColor = color.borderColor || color.backgroundColor;
        row.appendChild(swatch);
      }
      const text = document.createElement('span');
      text.textContent = [...(bodyItem.before || []), ...(bodyItem.lines || []), ...(bodyItem.after || [])].join(' ');
      row.appendChild(text);
      element.appendChild(row);
    });
    const footerLines = tooltip.footer || [];
    if (footerLines.length) {
      const footer = document.createElement('div');
      footer.className = 'chart-hover-tooltip-footer';
      footer.textContent = footerLines.join(' ');
      element.appendChild(footer);
    }

    // Render outside the canvas so long text can wrap and never gets clipped
    // by a narrow chart card. A deliberate gap keeps the pointer away from the
    // text without making the mouse cursor disappear.
    element.classList.add('is-visible');
    element.style.visibility = 'hidden';
    const canvasRect = canvas.getBoundingClientRect();
    const elementRect = element.getBoundingClientRect();
    const anchorX = canvasRect.left + Number(tooltip.caretX || 0);
    const anchorY = canvasRect.top + Number(tooltip.caretY || 0);
    const viewportGap = 12;
    const pointerGap = 16;
    const left = Math.min(
      window.innerWidth - elementRect.width - viewportGap,
      Math.max(viewportGap, anchorX - elementRect.width / 2)
    );
    let top = anchorY - elementRect.height - pointerGap;
    if (top < viewportGap) top = anchorY + pointerGap;
    top = Math.min(window.innerHeight - elementRect.height - viewportGap, Math.max(viewportGap, top));
    element.style.left = `${left}px`;
    element.style.top = `${top}px`;
    element.style.visibility = 'visible';
  }

  function abbreviateAxisLabel(label, maxLength = 18) {
    const text = String(label || '');
    return text.length > maxLength ? `${text.slice(0, maxLength - 1).trimEnd()}…` : text;
  }

  function getYAxisLabelAreaWidth(chartWidth) {
    return Math.min(160, Math.max(96, Number(chartWidth || 0) * 0.48));
  }

  function abbreviateAxisLabelToWidth(label, scale, fontSize = 11) {
    const text = String(label || '');
    const context = scale?.chart?.ctx;
    const maxWidth = Math.max(54, getYAxisLabelAreaWidth(scale?.chart?.width) - 8);
    if (!context || !text) return abbreviateAxisLabel(text, Math.max(10, Math.floor(maxWidth / 6)));
    context.save();
    context.font = `600 ${fontSize}px Inter, sans-serif`;
    if (context.measureText(text).width <= maxWidth) {
      context.restore();
      return text;
    }
    let low = 1;
    let high = text.length;
    while (low < high) {
      const middle = Math.ceil((low + high) / 2);
      const candidate = `${text.slice(0, middle).trimEnd()}…`;
      if (context.measureText(candidate).width <= maxWidth) low = middle;
      else high = middle - 1;
    }
    const shortened = `${text.slice(0, low).trimEnd()}…`;
    context.restore();
    return shortened;
  }

  function enableYAxisLabelHover(chart, labels) {
    const canvas = chart?.canvas;
    if (!canvas) return;
    canvas._wbpYAxisLabels = labels.map(label => String(label || ''));
    if (canvas._wbpYAxisHoverBound) return;
    canvas._wbpYAxisHoverBound = true;

    const tooltipId = `chart-axis-label-tooltip-${canvas.id}`;
    const chartTooltipId = `chart-hover-tooltip-${canvas.id}`;
    const hide = () => document.getElementById(tooltipId)?.classList.remove('is-visible');
    canvas.addEventListener('mouseleave', hide);
    canvas.addEventListener('mousemove', event => {
      const currentChart = typeof Chart !== 'undefined' && Chart.getChart ? Chart.getChart(canvas) : null;
      const scale = currentChart?.scales?.y;
      const currentLabels = canvas._wbpYAxisLabels || [];
      if (!scale || !currentLabels.length) return hide();
      const rect = canvas.getBoundingClientRect();
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;
      if (mouseX < scale.left || mouseX > scale.right || mouseY < scale.top || mouseY > scale.bottom) return hide();

      let nearestIndex = -1;
      let nearestDistance = Number.POSITIVE_INFINITY;
      currentLabels.forEach((_label, index) => {
        const distance = Math.abs(scale.getPixelForTick(index) - mouseY);
        if (distance < nearestDistance) {
          nearestDistance = distance;
          nearestIndex = index;
        }
      });
      const rowTolerance = Math.max(10, (scale.bottom - scale.top) / Math.max(1, currentLabels.length) / 2);
      if (nearestIndex < 0 || nearestDistance > rowTolerance) return hide();

      // Chart.js does not always issue a new data-tooltip update after the
      // pointer has crossed into its own Y-axis area. Remove the stale panel.
      document.getElementById(chartTooltipId)?.classList.remove('is-visible');

      let element = document.getElementById(tooltipId);
      if (!element) {
        element = document.createElement('div');
        element.id = tooltipId;
        element.className = 'chart-axis-label-tooltip';
        element.setAttribute('role', 'tooltip');
        document.body.appendChild(element);
      }
      element.textContent = currentLabels[nearestIndex];
      element.classList.add('is-visible');
      element.style.visibility = 'hidden';
      const elementRect = element.getBoundingClientRect();
      const viewportGap = 12;
      const anchorX = rect.left + scale.right + 10;
      const anchorY = rect.top + scale.getPixelForTick(nearestIndex);
      const left = Math.min(window.innerWidth - elementRect.width - viewportGap, Math.max(viewportGap, anchorX));
      const top = Math.min(window.innerHeight - elementRect.height - viewportGap, Math.max(viewportGap, anchorY - elementRect.height / 2));
      element.style.left = `${left}px`;
      element.style.top = `${top}px`;
      element.style.visibility = 'visible';
    });
  }

  // Application State
  const state = {
    region: null, // Default: Deutschland (Gesamt)
    year: '2024',
    metric: 'tonnes', // 'tonnes', 'tkm'
    direction: 'all', // 'all', 'outbound', 'inbound', 'balance'
    selectedGroup: 'ALL', // 'ALL' or '1'..'7' (NST-2007 main groups)
    selectedPort: null, // Selected Seaport UNLOCODE (e.g. 'DEHAM') or null for all
    topX: 10,
    includeBinnen: true, // Toggle for intra-regional self traffic
    modalSplitView: 'snapshot', // 'snapshot' or 'trend'
    commodityView: 'snapshot',
    roadNstLevel: '7', // '7' or '20'
    railNstLevel: '7',
    iwwNstLevel: '7',
    maritimeNstLevel: '7',
    roadCommodityView: 'snapshot',
    railCommodityView: 'snapshot',
    iwwCommodityView: 'snapshot',
    maritimeCommodityView: 'snapshot',
    showSpider: true,
    showRoadSpider: true,
    showRailSpider: true,
    showIwwSpider: true,
    showIntermodalRelations: true,
    intermodalRailStructureView: 'snapshot',
    intermodalIwwStructureView: 'snapshot',
    activeTab: 'tab-overview',
    forecastScenario: '2040_P1',
    forecastModalSplitMetric: 'tonnes',
    forecastChart2View: 'commodity',
    forecastCommodityLevel: '7',
    showForecastSpider: true
  };

  // Set Chart.js global typography, font sizes, and formatting
  if (typeof Chart !== 'undefined' && Chart.defaults) {
    Chart.defaults.locale = 'de-DE';
    Chart.defaults.color = '#334155';
    if (!Chart.defaults.font) Chart.defaults.font = {};
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
    Chart.defaults.font.size = 11.5;
    if (Chart.defaults.plugins) {
      if (Chart.defaults.plugins.legend && Chart.defaults.plugins.legend.labels) {
        Chart.defaults.plugins.legend.align = 'start';
        Chart.defaults.plugins.legend.labels.font = {
          size: 11.5,
          weight: '600',
          family: "'Inter', sans-serif"
        };
        Chart.defaults.plugins.legend.labels.textAlign = 'left';
      }
      if (Chart.defaults.plugins.tooltip) {
        // The map pop-ups and information hints use a light surface.  Apply
        // the same visual language to every Chart.js hover panel so charts do
        // not unexpectedly switch to a dark colour scheme.
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(255, 255, 255, 0.90)';
        Chart.defaults.plugins.tooltip.titleColor = '#0f172a';
        Chart.defaults.plugins.tooltip.bodyColor = '#334155';
        Chart.defaults.plugins.tooltip.borderColor = '#cbd5e1';
        Chart.defaults.plugins.tooltip.borderWidth = 1;
        Chart.defaults.plugins.tooltip.boxPadding = 4;
        Chart.defaults.plugins.tooltip.enabled = false;
        Chart.defaults.plugins.tooltip.external = renderExternalChartTooltip;
        Chart.defaults.plugins.tooltip.titleFont = {
          size: 12,
          weight: '700',
          family: "'Inter', sans-serif"
        };
        Chart.defaults.plugins.tooltip.bodyFont = {
          size: 11.5,
          weight: '500',
          family: "'Inter', sans-serif"
        };
        Chart.defaults.plugins.tooltip.padding = 9;
        Chart.defaults.plugins.tooltip.cornerRadius = 6;
      }
    }
  }

  // Data Stores
  let regionsData = {};
  let fullCentroids = {};
  let summaryData = {};
  let nationalSummaryData = {};
  let summaryDataLoad = null;
  // Compact 2019/2040 values for the regional overview tooltip. This keeps
  // the large forecast relation cube deferred until the forecast tab opens.
  let overviewForecastTooltipData = null;
  let overviewForecastTooltipDataLoad = null;
  const loadedRegionRelations = {};
  let choroplethData = {};
  // Large datasets are requested only when their respective module is opened.
  // This keeps the overview responsive and avoids downloading the 2040 forecast
  // for visitors who do not use it.
  let intermodalData = null;
  let benchmarkData = {};
  let nstData = {};
  let maritimeData = null;
  let geojsonNuts3 = null;
  let forecastData = null;
  let geojsonVp2040 = null;
  let centroidsVp2040 = {};
  let crosswalkSpatialVp = [];
  let crosswalkNstVp = [];
  const deferredModuleLoads = {};
  const nutsToVpCell = {};
  const vpCellToNuts = {};

  // Leaflet Map Instances & Layers
  const maps = { overview: null, road: null, rail: null, iww: null, intermodal: null, maritime: null, forecast: null };
  const mapLayers = {
    overview: { geojson: null, selection: null, spiderGroup: null, spiderLookup: {} },
    road: { geojson: null, selection: null, spiderGroup: null, spiderLookup: {} },
    rail: { geojson: null, selection: null, spiderGroup: null, spiderLookup: {} },
    iww: { geojson: null, selection: null, spiderGroup: null, spiderLookup: {} },
    intermodal: { geojson: null, selection: null, spiderGroup: null, spiderLookup: {} },
    maritime: { geojson: null, portsGroup: null, portsLookup: {} },
    forecast: { geojson: null, selection: null, spiderGroup: null, spiderLookup: {} }
  };

  // Central highlight tracking
  let activeHighlightedPartnerId = null;
  let activeHighlightedMapKey = null;

  function setMapDefaultViewport(mapKey, force = false) {
    const map = maps[mapKey];
    if (!map || (mapViewportInitialized[mapKey] && !force)) return;
    window.clearTimeout(mapViewportTimers[mapKey]);

    // Leaflet still needs the final, visible card size before applying the
    // shared view. Hidden module maps are therefore initialized on activation.
    const setWhenStable = (attempt = 0) => {
      const container = map.getContainer();
      const before = container.getBoundingClientRect();
      const isVisible = before.width > 0 && before.height > 0 && container.offsetParent !== null;
      if (!isVisible) {
        if (attempt < 12) {
          mapViewportTimers[mapKey] = window.setTimeout(() => setWhenStable(attempt + 1), 50);
        }
        return;
      }

      map.invalidateSize({ animate: false, pan: false });
      window.requestAnimationFrame(() => {
        const after = container.getBoundingClientRect();
        const stillChanging = Math.abs(after.width - before.width) > 1 || Math.abs(after.height - before.height) > 1;
        if (stillChanging && attempt < 12) {
          mapViewportTimers[mapKey] = window.setTimeout(() => setWhenStable(attempt + 1), 50);
          return;
        }
        if (mapKey === 'maritime') {
          map.fitBounds(MARITIME_COAST_BOUNDS, {
            padding: [4, 4],
            animate: false
          });
        } else {
          map.fitBounds(GERMANY_BOUNDS, {
            // A small safety margin keeps the outermost districts and islands
            // inside the frame while still using the available height.
            padding: [8, 8],
            animate: false
          });
        }
        mapViewportInitialized[mapKey] = true;
      });
    };

    mapViewportTimers[mapKey] = window.setTimeout(() => setWhenStable(), 90);
  }

  // Chart Instances
  let chartModalSplit = null;
  let chartCommodity = null;
  let chartRoadCommodity = null;
  let chartRailCommodity = null;
  let chartIwwCommodity = null;
  let chartMaritimeCommodity = null;
  let chartKvTimeseries = null;
  let chartKvRailUnits = null;
  let chartKvIwwUnits = null;
  let chartForecastModalSplit = null;
  let chartForecastCommodityKv = null;

  // Taxonomy Names (NST-2007)
  const NST_GROUPS_7 = {
    "1": "Erzeugnisse der Land- und Forstwirtschaft, Rohstoffe",
    "2": "Konsumgüter zum kurzfristigen Verbrauch, Holzwaren",
    "3": "Mineralische, chemische und Mineralölerzeugnisse",
    "4": "Metalle und Metallerzeugnisse",
    "5": "Maschinen und Ausrüstungen, langlebige Konsumgüter",
    "6": "Sekundärrohstoffe, Abfälle",
    "7": "Sonstige Produkte"
  };

  const NST_DIVISIONS_20 = {
    "01": "01 Land-, Jagd- & Forstwirtsch. Erzeugnisse",
    "02": "02 Kohle, rohes Erdöl, Erdgas",
    "03": "03 Erze, Steine und Erden",
    "04": "04 Nahrungs- & Genussmittel",
    "05": "05 Textilien, Bekleidung, Leder",
    "06": "06 Holzwaren, Papier & Druckwaren",
    "07": "07 Kokerei- & Mineralölerzeugnisse",
    "08": "08 Chemische Erzeugnisse, Kunststoffe",
    "09": "09 Glas, Keramik, Baustoffe",
    "10": "10 Metalle & Metallerzeugnisse",
    "11": "11 Maschinen & mechanische Geräte",
    "12": "12 Kraftwagen, Kfz-Teile, Transportmittel",
    "13": "13 Möbel & sonstige Fertigwaren",
    "14": "14 Sekundärrohstoffe, Abfälle",
    "15": "15 Postsendungen, Stückgut",
    "16": "16 Geräte & Material für Transport",
    "17": "17 Umzugsgut & persönliches Gut",
    "18": "18 Sammelgut",
    "19": "19 Unidentifizierbare Güter, Container",
    "20": "20 Sonstige Güter"
  };

  // German Number Formatter Helper
  function formatDeNum(val, maxDecimals = 1, minDecimals = 0) {
    if (val === null || val === undefined || isNaN(val)) return '--';
    return Number(val).toLocaleString('de-DE', {
      minimumFractionDigits: minDecimals,
      maximumFractionDigits: maxDecimals
    });
  }

  function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  }

  // Quantities use one decimal place by default. Very small non-zero values
  // retain further precision so an existing relation never appears as zero.
  function formatQuantity(val, standardDecimals = 1) {
    if (val === null || val === undefined || isNaN(val)) return '--';
    const absolute = Math.abs(Number(val));
    const decimals = absolute > 0 && absolute < 0.01 ? 3 : (absolute > 0 && absolute < 0.1 ? 2 : standardDecimals);
    return formatDeNum(val, decimals, decimals);
  }

  // Composition charts must calculate their share from the visible values of
  // the hovered year. This keeps the percentage consistent with all filters.
  function formatDynamicChartShare(context, unitText, suffix = '') {
    const value = Number(context.raw);
    const valuesAtYear = context.chart.data.datasets
      .map(dataset => Number(dataset.data?.[context.dataIndex]))
      .filter(Number.isFinite);
    const total = valuesAtYear.reduce((sum, item) => sum + Math.abs(item), 0);
    const share = total > 0 ? formatDeNum(Math.abs(value) / total * 100, 1) : '0,0';
    return ` ${context.dataset.label}: ${formatDeNum(value, 2)} ${unitText} (${share} %${suffix})`;
  }

  function getLatestConsolidatedOverviewYear(regYears, isTkm) {
    const metricKey = isTkm ? 'modes_tkm' : 'modes_tonnes';
    return Object.keys(regYears || {})
      .map(Number)
      .filter(year => isConsolidatedOverviewYear(regYears, year, isTkm))
      .sort((a, b) => b - a)[0] || Number(state.year);
  }

  function isConsolidatedOverviewYear(regYears, year, isTkm = false) {
    const metricKey = isTkm ? 'modes_tkm' : 'modes_tonnes';
    const modes = regYears?.[String(year)]?.[metricKey] || {};
    // A regional value of zero (for example, no inland-waterway traffic) is a
    // valid observation. A missing road series, however, makes the all-mode
    // snapshot non-comparable and is therefore not used as a profile year.
    return Number(modes.road || 0) > 0
      && ['rail', 'iww'].every(mode => Number.isFinite(Number(modes[mode])));
  }

  function getProfileYear(regYears) {
    const selectedYear = Number(state.year);
    return String(isConsolidatedOverviewYear(regYears, selectedYear, false)
      ? selectedYear
      : getLatestConsolidatedOverviewYear(regYears, false));
  }

  function getLatestAvailableModeYear(mode) {
    return Object.keys(nationalSummaryData || {})
      .map(Number)
      .filter(year => Number(nationalSummaryData?.[String(year)]?.modes_tonnes?.[mode] || 0) > 0)
      .sort((a, b) => b - a)[0] || null;
  }

  function setInitialYearToLatestCompleteData() {
    const select = document.getElementById('selectYear');
    const latestYear = String(getLatestConsolidatedOverviewYear(getActiveRegionSummary(), false));
    if (!select?.querySelector(`option[value="${latestYear}"]`)) return;
    state.year = latestYear;
    select.value = latestYear;
  }

  // ----------------------------------------------------
  // ASYNC PARTITIONED RELATION LOADER & CACHE
  // ----------------------------------------------------
  async function loadRegionRelations(regionId) {
    if (!regionId) return {};
    if (loadedRegionRelations[regionId]) {
      return loadedRegionRelations[regionId];
    }
    try {
      const res = await fetch(`data/processed/relations/${regionId}.json`);
      if (res.ok) {
        const data = await res.json();
        loadedRegionRelations[regionId] = data;
        return data;
      }
    } catch (e) {
      console.warn(`Could not load relations for ${regionId}`, e);
    }
    return {};
  }

  function getRegionRelations(regionId) {
    return loadedRegionRelations[regionId] || {};
  }

  // Helper: Return summary data for active region or national aggregates if none selected
  function getActiveRegionSummary() {
    if (state.region && summaryData[state.region]) {
      return summaryData[state.region];
    }
    return nationalSummaryData;
  }

  // Master Region Switcher
  async function setRegion(regionId) {
    if (!regionId || regionId === 'DE' || regionId === 'ALL') {
      state.region = null;
      const input = document.getElementById('regionSearchInput');
      if (input) input.value = 'Deutschland';
      updateAnalysisSummary();
      renderAll();
      return;
    }
    state.region = regionId;
    const input = document.getElementById('regionSearchInput');
    const curr = regionsData[regionId];
    if (input && curr) {
      input.value = `${curr.name} (${curr.id})`;
    }
    updateAnalysisSummary();
    await Promise.all([ensureSummaryData(), loadRegionRelations(regionId)]);
    renderAll();
  }

  function updateAnalysisSummary() {
    const selectedText = (id) => {
      const element = document.getElementById(id);
      return element?.options?.[element.selectedIndex]?.textContent?.trim() || '';
    };
    const setText = (id, value) => {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    };
    const isMaritime = state.activeTab === 'tab-maritime';
    const isIntermodal = state.activeTab === 'tab-intermodal';
    const region = isMaritime
      ? 'Hafenauswahl im Modul'
      : state.region
      ? (regionsData[state.region]?.name || document.getElementById('regionSearchInput')?.value || 'Ausgewählte Region')
      : 'Deutschland';
    const isForecast = state.activeTab === 'tab-forecast';
    const period = isForecast ? selectedText('selectScenario') : selectedText('selectYear');
    const selectedDirection = document.getElementById('selectDirection')?.value;
    const direction = {
      all: 'Versand + Empfang',
      outbound: 'Versand',
      inbound: 'Empfang',
      balance: 'Saldo'
    }[selectedDirection] || selectedText('selectDirection');
    const selectedGoods = document.getElementById('selectGlobalGroup')?.value;
    const goods = isIntermodal
      ? 'Güterfilter nicht anwendbar'
      : selectedGoods === 'ALL'
      ? 'Alle Güterarten'
      : selectedText('selectGlobalGroup');
    const topX = document.getElementById('selectTopX')?.value || state.topX || '10';
    const binnen = document.getElementById('selectBinnenverkehr')?.value === 'exclude'
      ? 'Binnenverkehr aus'
      : 'Binnenverkehr ein';

    setText('summaryRegion', region);
    setText('summaryPeriod', period);
    setText('summaryMetric', isMaritime
      ? 'Tonnen'
      : document.getElementById('selectMetric')?.value === 'tkm' ? 'Tonnen-km' : 'Tonnen');
    setText('summaryDirection', direction);
    setText('summaryGoods', goods);
    setText('summaryScope', `Top ${topX} · ${isMaritime ? 'Binnenverkehr nicht anwendbar' : binnen}`);
  }

  function setLegendCollapsedState(legend, collapsed) {
    if (!legend) return;
    legend.classList.toggle('collapsed', collapsed);
    const body = legend.querySelector('.legend-body');
    const button = legend.querySelector('.btn-legend-toggle');
    if (body) body.style.display = collapsed ? 'none' : 'block';
    if (button) {
      button.textContent = collapsed ? '+' : '−';
      button.title = collapsed ? 'Legende maximieren' : 'Legende minimieren';
    }
  }

  function applyResponsiveLegendDefaults(isMobile = window.matchMedia('(max-width: 900px)').matches) {
    document.querySelectorAll('.choropleth-legend').forEach(legend => {
      if (legend.dataset.legendUserToggled === 'true') return;
      setLegendCollapsedState(legend, isMobile);
    });
  }

  function setupAnalysisPanel() {
    const panel = document.getElementById('analysisPanel');
    const button = document.getElementById('btnToggleAnalysisPanel');
    if (!panel || !button) return;
    button.addEventListener('click', () => {
      const collapsed = panel.classList.toggle('is-collapsed');
      button.setAttribute('aria-expanded', String(!collapsed));
      const body = document.getElementById('analysisPanelBody');
      if (body) body.hidden = collapsed;
      window.setTimeout(() => {
        Object.values(maps).forEach(map => map?.invalidateSize({ animate: false }));
        setMapDefaultViewport(state.activeTab.replace('tab-', ''), true);
      }, 230);
    });
    panel.classList.add('is-collapsed');
    document.getElementById('analysisPanelBody')?.setAttribute('hidden', '');
    ['selectYear', 'selectScenario', 'selectMetric', 'selectDirection', 'selectGlobalGroup', 'selectTopX', 'selectBinnenverkehr']
      .forEach(id => document.getElementById(id)?.addEventListener('change', updateAnalysisSummary));
    updateAnalysisSummary();
  }

  // Marks global controls as unavailable where a module's source data cannot
  // support their meaning. Values are retained in state for the other modules,
  // but cannot be changed while they would have no effect.
  function updateGlobalControlAvailability(tabId = state.activeTab) {
    const unavailableByTab = {
      'tab-maritime': new Set(['region', 'metric', 'binnen']),
      // Regionalauswahl, Richtung und Binnenverkehr steuern im KV-Modul Karte
      // und Relationentabelle. NST-Güterarten sind in dieser Datenquelle nicht
      // ausgewiesen und bleiben deshalb bewusst deaktiviert.
      'tab-intermodal': new Set(['goods'])
    };
    const unavailable = unavailableByTab[tabId] || new Set();
    const controls = [
      { key: 'region', group: 'controlGroupRegion', inputs: ['regionSearchInput', 'btnClearRegion'] },
      { key: 'metric', group: 'controlGroupMetric', inputs: ['selectMetric'] },
      { key: 'direction', group: 'controlGroupDirection', inputs: ['selectDirection'] },
      { key: 'goods', group: 'controlGroupGoods', inputs: ['selectGlobalGroup'] },
      { key: 'topX', group: 'controlGroupTopX', inputs: ['selectTopX'] },
      { key: 'binnen', group: 'controlGroupBinnenverkehr', inputs: ['selectBinnenverkehr'] }
    ];

    controls.forEach(({ key, group: groupId, inputs }) => {
      const disabled = unavailable.has(key);
      const group = document.getElementById(groupId);
      if (group) {
        group.classList.toggle('is-disabled', disabled);
        group.setAttribute('aria-disabled', String(disabled));
        group.title = disabled ? 'Für dieses Analysemodul nicht anwendbar.' : '';
      }
      inputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
          input.disabled = disabled;
          input.title = disabled ? 'Für dieses Analysemodul nicht anwendbar.' : '';
        }
      });
    });

    if (unavailable.has('region')) {
      document.getElementById('regionAutocompleteList')?.classList.remove('active');
    }

    // Straßendaten liegen derzeit nur bis 2024 vor. Ein auswählbares Jahr
    // 2025 würde eine leere Karte wie einen echten Nullwert erscheinen lassen.
    const yearSelect = document.getElementById('selectYear');
    const road2025Option = yearSelect?.querySelector('option[value="2025"]');
    const road2025Unavailable = tabId === 'tab-road';
    if (road2025Option) {
      road2025Option.disabled = road2025Unavailable;
      road2025Option.title = road2025Unavailable
        ? 'Straßengüterverkehrsdaten liegen derzeit bis 2024 vor.'
        : '';
    }
    if (road2025Unavailable && state.year === '2025' && yearSelect) {
      state.year = '2024';
      yearSelect.value = '2024';
      updateMapTitles();
      updateTableHistoricalHeaders();
    }
  }

  // ----------------------------------------------------
  // INITIALIZATION
  // ----------------------------------------------------
  async function init() {
    setupEventListeners();
    observeMissingComparisons();
    updateGlobalControlAvailability();
    initLeafletMaps();
    setModuleLoadingState('tab-overview', true);
    const overviewNotice = document.querySelector('#tab-overview .module-loading-status');
    if (overviewNotice) overviewNotice.textContent = 'Startansicht wird geladen …';
    await loadData();
    setupRegionAutocomplete();
    // The overview charts need the regional summary cube.  Drawing them once
    // before and once after its background load caused the visible double draw.
    await ensureSummaryData();
    setInitialYearToLatestCompleteData();
    renderAll();
    // Load the compact preview after first render and refresh only the visible
    // overview map once the additional tooltip information is ready.
    ensureOverviewForecastTooltipData().then(loaded => {
      if (loaded && state.activeTab === 'tab-overview') updateLeafletMap('overview');
    });
    // Leaflet needs a completed layout pass after the visible card has settled.
    // Keep this map-only so charts are not rendered a second time.
    const refreshInitialOverview = () => {
      if (state.activeTab !== 'tab-overview') return;
      maps.overview?.invalidateSize({ animate: false });
      setMapDefaultViewport('overview', true);
    };
    requestAnimationFrame(refreshInitialOverview);
    setModuleLoadingState('tab-overview', false);
  }

  function setModuleLoadingState(tabId, isLoading) {
    const pane = document.getElementById(tabId);
    if (!pane) return;
    pane.setAttribute('aria-busy', String(isLoading));
    let notice = pane.querySelector('.module-loading-status');
    if (!notice) {
      notice = document.createElement('div');
      notice.className = 'module-loading-status';
      notice.setAttribute('role', 'status');
      notice.textContent = 'Fachdaten werden geladen …';
      pane.insertAdjacentElement('afterbegin', notice);
    }
    notice.hidden = !isLoading;
  }

  async function fetchJson(url, fallback) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  function hasRegionalSummaryData() {
    return Object.keys(summaryData || {}).length > 0;
  }

  async function ensureSummaryData() {
    if (hasRegionalSummaryData()) return true;
    if (!summaryDataLoad) {
      summaryDataLoad = fetchJson('data/processed/web_summary_by_region.json', {})
        .then(data => {
          summaryData = data;
          nationalSummaryData = computeNationalSummaries();
          return true;
        })
        .catch(error => {
          console.error('Could not load regional summary data:', error);
          return false;
        });
    }
    return summaryDataLoad;
  }

  async function ensureOverviewForecastTooltipData() {
    if (overviewForecastTooltipData) return true;
    if (!overviewForecastTooltipDataLoad) {
      overviewForecastTooltipDataLoad = fetchJson('data/processed/web_forecast_overview_tooltip.json?v=20260824a', null)
        .then(data => {
          overviewForecastTooltipData = data?.scenarios ? data : null;
          return Boolean(overviewForecastTooltipData);
        })
        .catch(error => {
          // The overview stays fully usable when the optional preview is not
          // available; only its forecast block is omitted from tooltips.
          console.warn('Could not load overview forecast tooltip data:', error);
          return false;
        });
    }
    return overviewForecastTooltipDataLoad;
  }

  async function ensureModuleData(moduleName) {
    const available = {
      maritime: () => Boolean(maritimeData),
      intermodal: () => Boolean(intermodalData),
      forecast: () => Boolean(forecastData)
    };
    if (available[moduleName]?.()) return true;
    if (deferredModuleLoads[moduleName]) return deferredModuleLoads[moduleName];

    const loaders = {
      maritime: async () => { maritimeData = await fetchJson('data/processed/web_maritime.json?v=20260821n', {}); },
      intermodal: async () => { intermodalData = await fetchJson('data/processed/web_intermodal.json?v=20260821a', {}); },
      forecast: async () => {
        const [forecastRes, centroidsRes, spatialCrosswalkRes, nstCrosswalkRes] = await Promise.all([
          fetchJson('data/processed/web_forecast_2040.json?v=20260821modalbygroup', null),
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
      }
    };

    deferredModuleLoads[moduleName] = loaders[moduleName]()
      .then(() => true)
      .catch(error => {
        console.error(`Could not load ${moduleName} module data:`, error);
        return false;
      });
    return deferredModuleLoads[moduleName];
  }

  function formatDataYearRange(years) {
    const ordered = [...new Set((years || []).map(Number).filter(Number.isFinite))].sort((a, b) => a - b);
    if (!ordered.length) return 'nicht verfügbar';
    return ordered.length === 1 ? String(ordered[0]) : `${ordered[0]} bis ${ordered[ordered.length - 1]}`;
  }

  function getAvailableDataYears(source, predicate = () => true) {
    return Object.keys(source || {})
      .map(Number)
      .filter(year => predicate(source[String(year)], year));
  }

  function refreshDataCoverageText() {
    const modeYears = mode => getAvailableDataYears(nationalSummaryData, record => Number(record?.modes_tonnes?.[mode] || 0) > 0);
    const coverage = [
      ['Straßengüterverkehr', formatDataYearRange(modeYears('road'))],
      ['Schienengüterverkehr', formatDataYearRange(modeYears('rail'))],
      ['Binnenschifffahrt', formatDataYearRange(modeYears('iww'))],
      ['Seeverkehr und Seehäfen', formatDataYearRange(Object.keys(maritimeData?.national || maritimeData?.seaports || {}))],
      ['Intermodale Verkehre & KV', formatDataYearRange(intermodalData?.years || [])],
      ['Verkehrsprognose VP 2040', 'Basisjahr 2019, Prognosehorizont 2040, Prognosefall 1 „Basisprognose 2040“']
    ];
    const list = document.getElementById('helpDataCoverageList');
    if (list) list.innerHTML = coverage.map(([label, years]) => `<li><strong>${label}:</strong> ${years}.</li>`).join('');
  }

  async function refreshDataCoverage() {
    await Promise.all([ensureModuleData('maritime'), ensureModuleData('intermodal')]);
    refreshDataCoverageText();
  }

  // Precompute National Aggregates from summaryData & benchmarkData
  function computeNationalSummaries() {
    const national = {};
    const years = ['2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'];
    
    years.forEach(yr => {
      const b = benchmarkData[yr] || {};
      const bModes = b.modes || {};
      
      const obj = {
        total_tonnes: b.total_tonnes || 0,
        total_tkm: b.total_tkm || 0,
        modes_tonnes: {
          road: bModes.road?.tonnes || 0,
          rail: bModes.rail?.tonnes || 0,
          iww: bModes.iww?.tonnes || 0
        },
        modes_tkm: {
          road: bModes.road?.tkm || 0,
          rail: bModes.rail?.tkm || 0,
          iww: bModes.iww?.tkm || 0
        },
        modes_direction_tonnes: { road: { inbound: 0, outbound: 0 }, rail: { inbound: 0, outbound: 0 }, iww: { inbound: 0, outbound: 0 } },
        modes_direction_tkm: { road: { inbound: 0, outbound: 0 }, rail: { inbound: 0, outbound: 0 }, iww: { inbound: 0, outbound: 0 } },
        directions_tonnes: { inbound: 0, outbound: 0 },
        directions_tkm: { inbound: 0, outbound: 0 },
        groups_7_tonnes: { all: {}, inbound: {}, outbound: {}, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0 },
        groups_7_tkm: { all: {}, inbound: {}, outbound: {}, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0 },
        by_mode_groups: { road: { all: {}, inbound: {}, outbound: {} }, rail: { all: {}, inbound: {}, outbound: {} }, iww: { all: {}, inbound: {}, outbound: {} } },
        by_mode_groups_tkm: { road: { all: {}, inbound: {}, outbound: {} }, rail: { all: {}, inbound: {}, outbound: {} }, iww: { all: {}, inbound: {}, outbound: {} } },
        by_mode_divisions: { road: {}, rail: {}, iww: {} },
        by_mode_divisions_tkm: { road: {}, rail: {}, iww: {} }
      };

      Object.keys(summaryData).forEach(nutsId => {
        if (nutsId.length === 5) {
          const rData = summaryData[nutsId]?.[yr];
          if (!rData) return;
          ['road', 'rail', 'iww'].forEach(m => {
            obj.modes_direction_tonnes[m].inbound += (rData.modes_direction_tonnes?.[m]?.inbound || 0) / 2;
            obj.modes_direction_tonnes[m].outbound += (rData.modes_direction_tonnes?.[m]?.outbound || 0) / 2;
            obj.modes_direction_tkm[m].inbound += (rData.modes_direction_tkm?.[m]?.inbound || 0) / 2;
            obj.modes_direction_tkm[m].outbound += (rData.modes_direction_tkm?.[m]?.outbound || 0) / 2;
          });

          // Inbound & Outbound
          obj.directions_tonnes.inbound += (rData.directions_tonnes?.inbound || 0) / 2;
          obj.directions_tonnes.outbound += (rData.directions_tonnes?.outbound || 0) / 2;
          obj.directions_tkm.inbound += (rData.directions_tkm?.inbound || 0) / 2;
          obj.directions_tkm.outbound += (rData.directions_tkm?.outbound || 0) / 2;

          // NST 7
          const g7 = rData.groups_7_tonnes || {};
          const g7Map = g7.all || g7;
          Object.keys(g7Map).forEach(k => {
            obj.groups_7_tonnes[k] = (obj.groups_7_tonnes[k] || 0) + (g7Map[k] || 0) / 2;
            obj.groups_7_tonnes.all[k] = (obj.groups_7_tonnes.all[k] || 0) + (g7Map[k] || 0) / 2;
          });
          ['inbound', 'outbound'].forEach(direction => Object.entries(g7[direction] || {}).forEach(([k, amount]) => {
            obj.groups_7_tonnes[direction][k] = (obj.groups_7_tonnes[direction][k] || 0) + (amount || 0) / 2;
          }));
          const g7tkm = rData.groups_7_tkm || {};
          const g7tkmMap = g7tkm.all || g7tkm;
          Object.keys(g7tkmMap).forEach(k => {
            obj.groups_7_tkm[k] = (obj.groups_7_tkm[k] || 0) + (g7tkmMap[k] || 0) / 2;
            obj.groups_7_tkm.all[k] = (obj.groups_7_tkm.all[k] || 0) + (g7tkmMap[k] || 0) / 2;
          });
          ['inbound', 'outbound'].forEach(direction => Object.entries(g7tkm[direction] || {}).forEach(([k, amount]) => {
            obj.groups_7_tkm[direction][k] = (obj.groups_7_tkm[direction][k] || 0) + (amount || 0) / 2;
          }));

          // Mode divisions 20 & Mode groups 7
          ['road', 'rail', 'iww'].forEach(m => {
            const divMap = rData.by_mode_divisions?.[m]?.all || rData.by_mode_divisions?.[m] || {};
            Object.keys(divMap).forEach(k => {
              const padK = k.padStart(2, '0');
              obj.by_mode_divisions[m][padK] = (obj.by_mode_divisions[m][padK] || 0) + (divMap[k] || 0) / 2;
            });
            const divTkmMap = rData.by_mode_divisions_tkm?.[m]?.all || rData.by_mode_divisions_tkm?.[m] || {};
            Object.keys(divTkmMap).forEach(k => {
              const padK = k.padStart(2, '0');
              obj.by_mode_divisions_tkm[m][padK] = (obj.by_mode_divisions_tkm[m][padK] || 0) + (divTkmMap[k] || 0) / 2;
            });
            const grpMap = rData.by_mode_groups?.[m]?.all || rData.by_mode_groups?.[m] || {};
            Object.keys(grpMap).forEach(k => {
              obj.by_mode_groups[m][k] = (obj.by_mode_groups[m][k] || 0) + (grpMap[k] || 0) / 2;
              obj.by_mode_groups[m].all[k] = (obj.by_mode_groups[m].all[k] || 0) + (grpMap[k] || 0) / 2;
            });
            ['inbound', 'outbound'].forEach(direction => Object.entries(rData.by_mode_groups?.[m]?.[direction] || {}).forEach(([k, amount]) => {
              obj.by_mode_groups[m][direction][k] = (obj.by_mode_groups[m][direction][k] || 0) + (amount || 0) / 2;
            }));
            const grpTkmMap = rData.by_mode_groups_tkm?.[m]?.all || rData.by_mode_groups_tkm?.[m] || {};
            Object.keys(grpTkmMap).forEach(k => {
              obj.by_mode_groups_tkm[m][k] = (obj.by_mode_groups_tkm[m][k] || 0) + (grpTkmMap[k] || 0) / 2;
              obj.by_mode_groups_tkm[m].all[k] = (obj.by_mode_groups_tkm[m].all[k] || 0) + (grpTkmMap[k] || 0) / 2;
            });
            ['inbound', 'outbound'].forEach(direction => Object.entries(rData.by_mode_groups_tkm?.[m]?.[direction] || {}).forEach(([k, amount]) => {
              obj.by_mode_groups_tkm[m][direction][k] = (obj.by_mode_groups_tkm[m][direction][k] || 0) + (amount || 0) / 2;
            }));
          });
        }
      });

      if (!obj.total_tonnes) {
        obj.total_tonnes = obj.modes_tonnes.road + obj.modes_tonnes.rail + obj.modes_tonnes.iww;
      }
      national[yr] = obj;
    });
    return national;
  }

  // Load All Precomputed JSON Data with Error Resilience
  async function loadData() {
    const fetchSafe = (url, fallback = {}) =>
      fetchJson(url, fallback).catch(err => {
        console.warn(`Could not load ${url}:`, err);
        return fallback;
      });

    try {
      const [regRes, centRes, choroRes, benRes, nstRes, geoRes] = await Promise.all([
        fetchSafe('data/processed/web_regions.json', {}),
        fetchSafe('data/processed/nuts_centroids_full.json', {}),
        fetchSafe('data/processed/web_choropleth.json', {}),
        fetchSafe('data/processed/national_benchmarks.json', {}),
        fetchSafe('data/processed/dim_nst2007.json', {}),
        fetchSafe('data/processed/nuts3_de_2024.geojson', null)
      ]);

      regionsData = regRes;
      fullCentroids = centRes;
      choroplethData = choroRes;
      benchmarkData = benRes;
      nstData = nstRes;
      geojsonNuts3 = geoRes;

      nationalSummaryData = Object.fromEntries(Object.entries(benchmarkData).map(([year, benchmark]) => {
        const modes = benchmark.modes || {};
        return [year, {
          total_tonnes: benchmark.total_tonnes || 0,
          total_tkm: benchmark.total_tkm || 0,
          modes_tonnes: Object.fromEntries(['road', 'rail', 'iww'].map(mode => [mode, modes[mode]?.tonnes || 0])),
          modes_tkm: Object.fromEntries(['road', 'rail', 'iww'].map(mode => [mode, modes[mode]?.tkm || 0])),
          directions_tonnes: {}, directions_tkm: {},
          groups_7_tonnes: {}, groups_7_tkm: {},
          by_mode_groups: { road: {}, rail: {}, iww: {} }, by_mode_groups_tkm: { road: {}, rail: {}, iww: {} },
          by_mode_divisions: { road: {}, rail: {}, iww: {} }, by_mode_divisions_tkm: { road: {}, rail: {}, iww: {} }
        }];
      }));

      // If initial region is set, load its relations
      if (state.region) {
        await Promise.all([ensureSummaryData(), loadRegionRelations(state.region)]);
      }
    } catch (err) {
      console.error("Error loading data bundle:", err);
    }
  }

  // Setup Searchable Region Autocomplete Combobox (Strict Prefix Matching)
  function setupRegionAutocomplete() {
    const input = document.getElementById('regionSearchInput');
    const dropdown = document.getElementById('regionAutocompleteList');
    const btnClear = document.getElementById('btnClearRegion');
    if (!input || !dropdown) return;

    if (btnClear) {
      btnClear.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropdown.classList.remove('active');
        await setRegion(null);
      });
    }

    const regionsList = Object.values(regionsData).sort((a, b) => a.name.localeCompare(b.name, 'de'));

    const updateInputValue = () => {
      if (!state.region) {
        input.value = 'Deutschland';
      } else {
        const curr = regionsData[state.region];
        if (curr) input.value = `${curr.name} (${curr.id})`;
      }
    };
    updateInputValue();

    const renderList = (filterText = '') => {
      dropdown.innerHTML = '';
      const q = filterText.toLowerCase().trim();

      if (!q || q.length === 0) {
        dropdown.classList.remove('active');
        return;
      }

      // If query starts with "deu" or "deutschland", or is "de", offer national entry
      if ('deutschland'.startsWith(q) || q === 'de' || q === 'ges' || q === 'bund') {
        const deItem = document.createElement('div');
        deItem.className = `autocomplete-item ${!state.region ? 'selected' : ''}`;
        deItem.innerHTML = `<span><img class="inline-ui-icon" src="assets/icons/map.svg" alt="" aria-hidden="true"><strong>Deutschland (Gesamt)</strong></span> <span style="color:#059669; font-size:0.75rem; font-weight:600;">Nationaler Überblick</span>`;
        deItem.addEventListener('click', async () => {
          dropdown.classList.remove('active');
          await setRegion(null);
        });
        dropdown.appendChild(deItem);
      }

      // Strict Prefix Matching (Beginning of region name, beginning of words in region name, or beginning of NUTS ID)
      const matches = regionsList.filter(r => {
        if (!r) return false;
        // 1. NUTS ID prefix match (e.g. DE275, DE111, DE...)
        if (r.id && r.id.toLowerCase().startsWith(q)) return true;
        // 2. Name prefix match or word prefix match (e.g. "Ber" -> Berlin, Bergstraße, etc.)
        if (r.name) {
          const nameLower = r.name.toLowerCase();
          if (nameLower.startsWith(q)) return true;
          const words = nameLower.split(/[\s,\-\/]+/);
          if (words.some(w => w.startsWith(q))) return true;
        }
        return false;
      });

      // Prioritize exact name/ID prefix match over inner-word prefix match
      matches.sort((a, b) => {
        const aNameStarts = a.name.toLowerCase().startsWith(q);
        const bNameStarts = b.name.toLowerCase().startsWith(q);
        const aIdStarts = a.id ? a.id.toLowerCase().startsWith(q) : false;
        const bIdStarts = b.id ? b.id.toLowerCase().startsWith(q) : false;

        const aPrimary = aNameStarts || aIdStarts;
        const bPrimary = bNameStarts || bIdStarts;

        if (aPrimary && !bPrimary) return -1;
        if (!aPrimary && bPrimary) return 1;
        return a.name.localeCompare(b.name, 'de');
      });

      if (matches.length === 0 && dropdown.children.length === 0) {
        const noMatch = document.createElement('div');
        noMatch.style.padding = '10px';
        noMatch.style.color = '#94a3b8';
        noMatch.style.fontSize = '0.8rem';
        noMatch.textContent = 'Keine Region gefunden';
        dropdown.appendChild(noMatch);
        dropdown.classList.add('active');
        return;
      }

      matches.slice(0, 35).forEach(r => {
        const item = document.createElement('div');
        item.className = `autocomplete-item ${r.id === state.region ? 'selected' : ''}`;
        item.innerHTML = `<span><strong>${r.name}</strong></span> <span style="color:#94a3b8; font-size:0.75rem;">${r.id}</span>`;
        item.addEventListener('click', async () => {
          dropdown.classList.remove('active');
          await setRegion(r.id);
        });
        dropdown.appendChild(item);
      });
      dropdown.classList.add('active');
    };

    // On focus, select text for quick typing, DO NOT open full list without user typing
    input.addEventListener('focus', () => {
      input.select();
    });

    input.addEventListener('input', e => {
      renderList(e.target.value);
    });

    document.addEventListener('click', e => {
      if (!e.target.closest('.search-combobox')) {
        dropdown.classList.remove('active');
        updateInputValue();
      }
    });
  }

  // Setup Global Event Listeners
  function setupEventListeners() {
    setupAnalysisPanel();
    // Window Resize Handler for Leaflet & Dynamic Views
    let resizeTimer = null;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        Object.values(maps).forEach(m => {
          if (m) m.invalidateSize({ animate: false, pan: false });
        });
        setMapDefaultViewport(state.activeTab.replace('tab-', ''), true);
      }, 150);
    });

    // Collapsible Sidebar Button
    const btnSidebar = document.getElementById('btnToggleSidebar');
    const sidebar = document.getElementById('appSidebar');
    if (btnSidebar && sidebar) {
      btnSidebar.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        sidebar.classList.toggle('collapsed');
        setTimeout(() => {
          Object.values(maps).forEach(m => {
            if (m) m.invalidateSize();
          });
          setMapDefaultViewport(state.activeTab.replace('tab-', ''));
        }, 320);
      });
    }

    // Navigation Tabs Switching
    document.querySelectorAll('#mainNav .nav-item').forEach(item => {
      item.setAttribute('tabindex', '0');
      item.setAttribute('role', 'tab');
      item.setAttribute('aria-selected', item.classList.contains('active') ? 'true' : 'false');
      item.addEventListener('click', async (e) => {
        e.preventDefault();
        document.querySelectorAll('#mainNav .nav-item').forEach(i => {
          i.classList.remove('active');
          i.setAttribute('aria-selected', 'false');
        });
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        
        item.classList.add('active');
        item.setAttribute('aria-selected', 'true');
        const tabId = item.getAttribute('data-tab');
        state.activeTab = tabId;
        document.getElementById('analysisPanelBody')?.classList.toggle('has-forecast-scenario', tabId === 'tab-forecast');
        updateGlobalControlAvailability(tabId);
        const target = document.getElementById(tabId);
        if (target) target.classList.add('active');

        const activeMapKey = tabId.replace('tab-', '');

        const deferredModule = ({
          'tab-maritime': 'maritime',
          'tab-intermodal': 'intermodal',
          'tab-forecast': 'forecast'
        })[tabId];
        if (deferredModule) {
          setModuleLoadingState(tabId, true);
          const loaded = await ensureModuleData(deferredModule);
          if (!loaded) {
            const pane = document.getElementById(tabId);
            const notice = pane?.querySelector('.module-loading-status');
            if (pane) pane.setAttribute('aria-busy', 'false');
            if (notice) {
              notice.textContent = 'Die Fachdaten konnten nicht geladen werden. Bitte laden Sie die Seite erneut.';
              notice.hidden = false;
            }
            return;
          }
          setModuleLoadingState(tabId, false);
          if (state.activeTab !== tabId) return;
        }

        if (['tab-road', 'tab-rail', 'tab-iww'].includes(tabId)) {
          setModuleLoadingState(tabId, true);
          const loaded = await ensureSummaryData();
          if (!loaded) {
            const notice = document.querySelector(`#${tabId} .module-loading-status`);
            if (notice) {
              notice.textContent = 'Die Fachdaten konnten nicht geladen werden. Bitte laden Sie die Seite erneut.';
              notice.hidden = false;
            }
            return;
          }
          setModuleLoadingState(tabId, false);
          if (state.activeTab !== tabId) return;
        }

        if (tabId === 'tab-forecast') {
          document.getElementById('controlGroupYear')?.style.setProperty('display', 'none');
          document.getElementById('controlGroupScenario')?.style.setProperty('display', 'flex');
          renderForecastTab();
        } else {
          document.getElementById('controlGroupScenario')?.style.setProperty('display', 'none');
          document.getElementById('controlGroupYear')?.style.setProperty('display', 'flex');
          if (tabId === 'tab-intermodal') {
            renderIntermodalTab();
          } else if (tabId === 'tab-maritime') {
            renderMaritimeTab();
          } else if (tabId === 'tab-overview') {
            renderOverviewTab();
          } else if (tabId.startsWith('tab-')) {
            renderModeDetailTab(tabId.replace('tab-', ''));
          }
        }
        updateAnalysisSummary();
        // Set the established Germany/coast view only after the module data
        // and its responsive card layout have finished rendering. Otherwise a
        // hidden map can retain a stale size and an extreme zoom level.
        setMapDefaultViewport(activeMapKey, true);
      });
      item.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          item.click();
        }
      });
    });

    // Year Selector
    document.getElementById('selectYear')?.addEventListener('change', async e => {
      state.year = e.target.value;
      
      let geojsonFile = 'data/processed/nuts3_de_2024.geojson';
      if (parseInt(state.year) <= 2020) geojsonFile = 'data/processed/nuts3_de_2016.geojson';
      else if (parseInt(state.year) <= 2023) geojsonFile = 'data/processed/nuts3_de_2021.geojson';

      try {
        geojsonNuts3 = await fetch(geojsonFile).then(r => r.json());
      } catch (err) {
        console.warn("Using fallback geometry:", err);
      }

      renderAll();
    });

    // Forecast Scenario Selector
    document.getElementById('selectScenario')?.addEventListener('change', e => {
      state.forecastScenario = e.target.value;
      renderForecastTab();
      updateMapTitles();
    });

    // Metric selector (Tonnes vs Tkm)
    document.getElementById('selectMetric')?.addEventListener('change', e => {
      state.metric = e.target.value;
      renderAll();
    });

    // Direction selector (Gesamt, Versand, Empfang, Bilanz)
    document.getElementById('selectDirection')?.addEventListener('change', e => {
      state.direction = e.target.value;
      renderAll();
    });

    // Top-X selector
    document.getElementById('selectTopX')?.addEventListener('change', e => {
      state.topX = parseInt(e.target.value, 10);
      const topTitle = document.getElementById('topXTitleLabel');
      if (topTitle) topTitle.textContent = `Top ${state.topX}`;
      const fcTopTitle = document.getElementById('forecastTopXTitleLabel');
      if (fcTopTitle) fcTopTitle.textContent = `Top ${state.topX}`;
      renderAll();
    });

    // Binnenverkehr Select Dropdown
    document.getElementById('selectBinnenverkehr')?.addEventListener('change', e => {
      state.includeBinnen = (e.target.value === 'include');
      renderAll();
    });

    // Global NST-2007 Commodity Selector (Header)
    document.getElementById('selectGlobalGroup')?.addEventListener('change', async e => {
      state.selectedGroup = e.target.value;
      if (state.selectedGroup !== 'ALL') await ensureSummaryData();
      renderAll();
    });

    // Spider line toggles across all maps
    document.getElementById('toggleSpider')?.addEventListener('change', e => {
      state.showSpider = e.target.checked;
      renderMapSpiderLines('overview');
    });
    document.getElementById('toggleRoadSpider')?.addEventListener('change', e => {
      state.showRoadSpider = e.target.checked;
      renderMapSpiderLines('road', 'road', state.selectedGroup || 'ALL');
    });
    document.getElementById('toggleRailSpider')?.addEventListener('change', e => {
      state.showRailSpider = e.target.checked;
      renderMapSpiderLines('rail', 'rail', state.selectedGroup || 'ALL');
    });
    document.getElementById('toggleIwwSpider')?.addEventListener('change', e => {
      state.showIwwSpider = e.target.checked;
      renderMapSpiderLines('iww', 'iww', state.selectedGroup || 'ALL');
    });
    document.getElementById('toggleIntermodalRelations')?.addEventListener('change', e => {
      state.showIntermodalRelations = e.target.checked;
      renderIntermodalTab();
    });
    document.getElementById('toggleForecastSpider')?.addEventListener('change', e => {
      state.showForecastSpider = e.target.checked;
      renderForecastSpiderLines();
    });

    // Map Legend Minimizing / Maximizing
    ['overview', 'road', 'rail', 'iww', 'intermodal', 'maritime', 'forecast'].forEach(k => {
      const btn = document.getElementById(`btnToggleLegend_${k}`);
      const leg = document.getElementById(`${k}MapLegend`) || document.getElementById(`${k}ChoroplethLegend`);
      if (btn && leg) {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          leg.dataset.legendUserToggled = 'true';
          setLegendCollapsedState(leg, !leg.classList.contains('collapsed'));
        });
      }
    });
    applyResponsiveLegendDefaults();
    const mobileLegendQuery = window.matchMedia('(max-width: 900px)');
    mobileLegendQuery.addEventListener?.('change', event => {
      applyResponsiveLegendDefaults(event.matches);
    });

    // Maritime Selected Port Reset Button
    const btnResetPort = document.getElementById('btnResetSelectedPort');
    if (btnResetPort) {
      btnResetPort.addEventListener('click', (e) => {
        e.preventDefault();
        state.selectedPort = null;
        renderMaritimeTab();
      });
    }

    // Modal Split Toggle (Snapshot vs Trend)
    document.querySelectorAll('#toggleModalSplitGroup .toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#toggleModalSplitGroup .toggle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.modalSplitView = btn.getAttribute('data-view');
        renderModalSplitChart();
      });
    });

    // Forecast chart representation: a compact selector avoids collisions in
    // the narrow forecast card header.
    document.getElementById('selectForecastChart2View')?.addEventListener('change', e => {
      state.forecastChart2View = e.target.value;
      const titleEl = document.getElementById('forecastChart2Title');
      if (titleEl) {
        titleEl.textContent = (state.forecastChart2View === 'kv')
          ? 'Kombinierter Verkehr (Ladeeinheiten)'
          : (state.forecastCommodityLevel === 'vp2040'
            ? 'Güterstruktur 2040 (VP2040)'
            : 'Güterstruktur 2040 (NST-2007)');
      }
      document.getElementById('forecastCommodityLevelControl')?.toggleAttribute('hidden', state.forecastChart2View !== 'commodity');
      renderForecastCommodityKvChart();
    });

    // Overview Commodity Structure Toggle
    document.querySelectorAll('#toggleCommodityGroup .toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#toggleCommodityGroup .toggle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.commodityView = btn.getAttribute('data-view');
        renderCommodityChart();
      });
    });

    // NST Level Dropdowns for Modes (7 vs 20)
    document.getElementById('selectRoadNstLevel')?.addEventListener('change', e => {
      state.roadNstLevel = e.target.value;
      renderRoadCommodityChart();
    });
    document.getElementById('selectRailNstLevel')?.addEventListener('change', e => {
      state.railNstLevel = e.target.value;
      renderRailCommodityChart();
    });
    document.getElementById('selectIwwNstLevel')?.addEventListener('change', e => {
      state.iwwNstLevel = e.target.value;
      renderIwwCommodityChart();
    });
    document.getElementById('selectMaritimeNstLevel')?.addEventListener('change', e => {
      state.maritimeNstLevel = e.target.value;
      renderMaritimeCommodityChart();
    });
    document.getElementById('selectForecastCommodityLevel')?.addEventListener('change', e => {
      state.forecastCommodityLevel = e.target.value;
      const titleEl = document.getElementById('forecastChart2Title');
      if (titleEl) titleEl.textContent = e.target.value === 'vp2040'
        ? 'Güterstruktur 2040 (VP2040)'
        : 'Güterstruktur 2040 (NST-2007)';
      renderForecastCommodityKvChart();
    });

    // Mode Commodity Chart Toggles
    document.querySelectorAll('#toggleRoadCommodityGroup .toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#toggleRoadCommodityGroup .toggle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.roadCommodityView = btn.getAttribute('data-view');
        renderRoadCommodityChart();
      });
    });
    document.querySelectorAll('#toggleRailCommodityGroup .toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#toggleRailCommodityGroup .toggle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.railCommodityView = btn.getAttribute('data-view');
        renderRailCommodityChart();
      });
    });
    document.querySelectorAll('#toggleIwwCommodityGroup .toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#toggleIwwCommodityGroup .toggle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.iwwCommodityView = btn.getAttribute('data-view');
        renderIwwCommodityChart();
      });
    });
    document.querySelectorAll('#toggleMaritimeCommodityGroup .toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#toggleMaritimeCommodityGroup .toggle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.maritimeCommodityView = btn.getAttribute('data-view');
        renderMaritimeCommodityChart();
      });
    });
    document.querySelectorAll('.intermodal-structure-toggle .toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const nextView = btn.getAttribute('data-view');
        const toggle = btn.closest('.intermodal-structure-toggle');
        toggle?.querySelectorAll('.toggle-btn').forEach(b => {
          b.classList.toggle('active', b.getAttribute('data-view') === nextView);
        });
        if (toggle?.id === 'toggleIntermodalRailStructure') state.intermodalRailStructureView = nextView;
        if (toggle?.id === 'toggleIntermodalIwwStructure') state.intermodalIwwStructureView = nextView;
        renderIntermodalTab();
      });
    });

    // Güterstrom-KI interaction prototype. It deliberately demonstrates the
    // intended workflow without inventing values or contacting a model.
    const getAiContextSummary = () => [
      document.getElementById('summaryRegion')?.textContent,
      document.getElementById('summaryPeriod')?.textContent,
      document.getElementById('summaryMetric')?.textContent,
      document.getElementById('summaryDirection')?.textContent
    ].filter(Boolean).join(' · ');

    const updateAiContext = () => {
      const context = document.getElementById('aiContextSummary');
      if (context) context.textContent = getAiContextSummary() || 'Aktuelle Auswahl wird geladen …';
    };

    const appendAiMessage = (kind, content) => {
      const conversation = document.getElementById('aiConversation');
      if (!conversation) return;

      conversation.closest('.ki-modal-body')?.classList.add('has-conversation');

      const message = document.createElement('article');
      message.className = `ki-message ki-message-${kind}`;

      const avatar = document.createElement('div');
      avatar.className = 'ki-message-avatar';
      if (kind === 'assistant') {
        const icon = document.createElement('img');
        icon.src = 'assets/icons/gueterstrom-ki-mark.svg';
        icon.alt = '';
        avatar.appendChild(icon);
      } else {
        avatar.textContent = 'Sie';
      }

      const body = document.createElement('div');
      body.className = 'ki-message-content';
      if (typeof content === 'string') {
        const paragraph = document.createElement('p');
        paragraph.textContent = content;
        body.appendChild(paragraph);
      } else {
        body.appendChild(content);
      }

      message.append(avatar, body);
      conversation.appendChild(message);
      conversation.scrollTop = conversation.scrollHeight;
    };

    const submitAiPrototypeQuestion = () => {
      const input = document.getElementById('aiQuestionInput');
      const question = input?.value.trim();
      if (!question) {
        input?.focus();
        return;
      }

      appendAiMessage('user', question);
      input.value = '';
      input.style.height = '';

      const response = document.createDocumentFragment();
      const title = document.createElement('strong');
      title.textContent = 'Frage erkannt – Datenabfrage noch nicht verbunden.';
      const explanation = document.createElement('p');
      const context = getAiContextSummary() || 'der aktuellen Auswahl';
      explanation.textContent = `Im späteren Ausbau würde die Güterstrom-KI für „${context}“ passende geprüfte Abfragen auswählen, die Daten auswerten und das Ergebnis mit Quellen und Einschränkungen erläutern. Dieser Interface-Test erzeugt bewusst keine Zahlen.`;
      const meta = document.createElement('span');
      meta.className = 'ki-message-meta';
      meta.textContent = 'Prototyp-Antwort · keine Modell- oder Datenverbindung';
      response.append(title, explanation, meta);
      appendAiMessage('assistant', response);
      input.focus();
    };

    // Modals Handling
    const setupModal = (btnId, modalId) => {
      const btn = document.getElementById(btnId);
      const modal = document.getElementById(modalId);
      if (btn && modal) {
        btn.addEventListener('click', async () => {
          modal.classList.add('active');
          modal.querySelector('.modal-close')?.focus();
          if (modalId === 'modalSteckbrief') await prepareSteckbriefModal();
          if (modalId === 'modalHelp' || modalId === 'modalLicenses') await refreshDataCoverage();
          if (modalId === 'modalAi') {
            updateAiContext();
            requestAnimationFrame(() => document.getElementById('aiQuestionInput')?.focus());
          }
        });
        modal.querySelectorAll('.modal-close, [data-close]')?.forEach(c => {
          c.addEventListener('click', () => {
            modal.classList.remove('active');
            btn.focus();
          });
        });
        modal.addEventListener('click', e => {
          if (e.target === modal) {
            modal.classList.remove('active');
            btn.focus();
          }
        });
        document.addEventListener('keydown', e => {
          if (e.key === 'Escape' && modal.classList.contains('active')) {
            modal.classList.remove('active');
            btn.focus();
          }
        });
      }
    };

    setupModal('btnAiModal', 'modalAi');
    setupModal('btnSteckbriefModal', 'modalSteckbrief');
    setupModal('btnHelpModal', 'modalHelp');
    setupModal('btnLicensesModal', 'modalLicenses');
    setupModal('brandLogoBtn', 'modalLicenses');

    document.getElementById('aiQuestionForm')?.addEventListener('submit', event => {
      event.preventDefault();
      submitAiPrototypeQuestion();
    });
    document.getElementById('aiQuestionInput')?.addEventListener('keydown', event => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        submitAiPrototypeQuestion();
      }
    });
    document.getElementById('aiQuestionInput')?.addEventListener('input', event => {
      const input = event.currentTarget;
      input.style.height = 'auto';
      input.style.height = `${Math.min(input.scrollHeight, 118)}px`;
    });
    document.getElementById('aiExamplesToggle')?.addEventListener('click', event => {
      const button = event.currentTarget;
      const examples = document.getElementById('aiExamples');
      if (!examples) return;
      const willOpen = examples.hidden;
      examples.hidden = !willOpen;
      button.setAttribute('aria-expanded', String(willOpen));
    });
    document.querySelectorAll('[data-ai-question]').forEach(button => {
      button.addEventListener('click', () => {
        const input = document.getElementById('aiQuestionInput');
        if (!input) return;
        input.value = button.getAttribute('data-ai-question') || '';
        input.dispatchEvent(new Event('input'));
        const examples = document.getElementById('aiExamples');
        const toggle = document.getElementById('aiExamplesToggle');
        if (examples) examples.hidden = true;
        toggle?.setAttribute('aria-expanded', 'false');
        input.focus();
      });
    });

    document.getElementById('btnPrintSteckbrief')?.addEventListener('click', () => {
      window.print();
    });

    // Keep every information panel in the viewport, regardless of its card
    // position. CSS supplies the two alternate anchor positions.
    document.querySelectorAll('.info-tooltip-wrap').forEach(wrap => {
      const positionTooltip = () => {
        wrap.classList.remove('tooltip-align-right', 'tooltip-open-up');
        requestAnimationFrame(() => {
          const box = wrap.querySelector('.info-tooltip-box');
          if (!box) return;
          let bounds = box.getBoundingClientRect();
          if (bounds.right > window.innerWidth - 12) {
            wrap.classList.add('tooltip-align-right');
            bounds = box.getBoundingClientRect();
          }
          if (bounds.bottom > window.innerHeight - 12) wrap.classList.add('tooltip-open-up');
        });
      };
      wrap.addEventListener('pointerenter', positionTooltip);
      wrap.addEventListener('focusin', positionTooltip);
    });
    // The information panel is the complete hover help. Native title bubbles
    // would otherwise overlap it after a short hover delay.
    document.querySelectorAll('.info-icon-btn[title]').forEach(icon => icon.removeAttribute('title'));

  }

  // ============================================================
  // LEAFLET MAPS INITIALIZATION (GERMAN BASEMAP & PROPER BOUNDS)
  // ============================================================
  function fitLeafletTooltipToMap(map, tooltip, inset = 8) {
    const tooltipEl = tooltip?.getElement?.();
    const mapEl = map?.getContainer?.();
    if (!tooltipEl || !mapEl) return;
    const mapRect = mapEl.getBoundingClientRect();
    const tipRect = tooltipEl.getBoundingClientRect();
    let shiftX = 0;
    let shiftY = 0;
    if (tipRect.left < mapRect.left + inset) shiftX = mapRect.left + inset - tipRect.left;
    else if (tipRect.right > mapRect.right - inset) shiftX = mapRect.right - inset - tipRect.right;
    if (tipRect.top < mapRect.top + inset) shiftY = mapRect.top + inset - tipRect.top;
    else if (tipRect.bottom > mapRect.bottom - inset) shiftY = mapRect.bottom - inset - tipRect.bottom;
    // The custom legend is a sibling of the Leaflet container and therefore
    // lives in a separate stacking context. Keep the hover card physically
    // clear of it instead of relying on a z-index across those contexts.
    const projected = {
      left: tipRect.left + shiftX,
      right: tipRect.right + shiftX,
      top: tipRect.top + shiftY,
      bottom: tipRect.bottom + shiftY
    };
    const legend = mapEl.parentElement?.querySelector('.choropleth-legend');
    if (legend && legend.offsetParent !== null) {
      const legendRect = legend.getBoundingClientRect();
      const overlapsLegend = projected.left < legendRect.right
        && projected.right > legendRect.left
        && projected.top < legendRect.bottom
        && projected.bottom > legendRect.top;
      if (overlapsLegend) {
        const candidates = [
          {
            axis: 'y',
            delta: legendRect.top - inset - projected.bottom,
            valid: projected.top + legendRect.top - inset - projected.bottom >= mapRect.top + inset
          },
          {
            axis: 'x',
            delta: legendRect.left - inset - projected.right,
            valid: projected.left + legendRect.left - inset - projected.right >= mapRect.left + inset
          },
          {
            axis: 'x',
            delta: legendRect.right + inset - projected.left,
            valid: projected.right + legendRect.right + inset - projected.left <= mapRect.right - inset
          },
          {
            axis: 'y',
            delta: legendRect.bottom + inset - projected.top,
            valid: projected.bottom + legendRect.bottom + inset - projected.top <= mapRect.bottom - inset
          }
        ].filter(candidate => candidate.valid)
          .sort((a, b) => Math.abs(a.delta) - Math.abs(b.delta));
        const best = candidates[0];
        if (best?.axis === 'x') shiftX += best.delta;
        if (best?.axis === 'y') shiftY += best.delta;
      }
    }
    if (!shiftX && !shiftY) return;
    const position = L.DomUtil.getPosition(tooltipEl);
    if (position) L.DomUtil.setPosition(tooltipEl, position.add(L.point(shiftX, shiftY)));
  }

  function initLeafletMaps() {
    const mapConfigs = [
      { key: 'overview', containerId: 'overviewLeafletMap' },
      { key: 'road', containerId: 'roadLeafletMap' },
      { key: 'rail', containerId: 'railLeafletMap' },
      { key: 'iww', containerId: 'iwwLeafletMap' },
      { key: 'intermodal', containerId: 'intermodalLeafletMap' },
      { key: 'maritime', containerId: 'maritimeLeafletMap' },
      { key: 'forecast', containerId: 'forecastLeafletMap' }
    ];

    mapConfigs.forEach(cfg => {
      const el = document.getElementById(cfg.containerId);
      if (!el || maps[cfg.key]) return;

      const map = L.map(cfg.containerId, {
        zoomControl: true,
        attributionControl: false,
        // Give also initially hidden module maps a valid, neutral view. Without
        // this Leaflet can cache a 0 x 0 size and clamp the first fitBounds call
        // to maxZoom 18. The precise Germany/coast fit follows on activation.
        center: [51.175, 10.425],
        zoom: 5,
        // Fractional zoom lets fitBounds use the card height accurately instead
        // of rounding to a different whole zoom step in another browser.
        zoomSnap: 0.1
      });
      map.createPane('connectionPane');
      map.getPane('connectionPane').style.zIndex = 450;
      map.createPane('selectionPane');
      map.getPane('selectionPane').style.zIndex = 460;

      const syncTooltipFrame = () => {
        const size = map.getSize();
        el.style.setProperty('--map-tooltip-max-width', `${Math.max(120, size.x - 16)}px`);
        el.style.setProperty('--forecast-tooltip-max-width', `${Math.max(120, size.x - 24)}px`);
        el.style.setProperty('--forecast-tooltip-max-height', `${Math.max(160, size.y - 24)}px`);
      };
      const fitOpenTooltip = () => {
        const tooltip = map._wbpOpenTooltip;
        if (tooltip?.getElement?.()) requestAnimationFrame(() => fitLeafletTooltipToMap(map, tooltip));
      };
      map.on('tooltipopen', event => {
        map._wbpOpenTooltip = event.tooltip;
        el.classList.add('wbp-tooltip-open');
        fitOpenTooltip();
      });
      map.on('tooltipclose', event => {
        if (map._wbpOpenTooltip === event.tooltip) {
          map._wbpOpenTooltip = null;
          el.classList.remove('wbp-tooltip-open');
        }
      });
      map.on('mousemove', fitOpenTooltip);
      map.on('resize', () => {
        syncTooltipFrame();
        fitOpenTooltip();
      });
      requestAnimationFrame(syncTooltipFrame);

      // Attribution positioned at bottomleft (keeps bottomright free for choropleth legend)
      L.control.attribution({
        position: 'bottomleft',
        prefix: false
      }).addTo(map);

      // German localized OpenStreetMap Basemap (DE designations & labels)
      L.tileLayer('https://tile.openstreetmap.de/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>-Mitwirkende'
      }).addTo(map);

      // Add Reset-Zoom Button (4 Outward Arrows) under +/- in Leaflet Zoom Control
      const zoomControlContainer = map.zoomControl?.getContainer();
      if (zoomControlContainer) {
        const btnReset = document.createElement('a');
        btnReset.className = 'leaflet-control-zoom-reset';
        btnReset.href = '#';
        const resetMapLabel = cfg.key === 'maritime'
          ? 'Küstenausschnitt zurücksetzen'
          : 'Deutschland-Gesamtansicht zentrieren';
        btnReset.title = resetMapLabel;
        btnReset.setAttribute('role', 'button');
        btnReset.setAttribute('aria-label', resetMapLabel);
        btnReset.innerHTML = `<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><polyline points="21 15 21 21 15 21"></polyline><polyline points="3 9 3 3 9 3"></polyline></svg>`;
        L.DomEvent.disableClickPropagation(btnReset);
        L.DomEvent.on(btnReset, 'click', (e) => {
          L.DomEvent.preventDefault(e);
          setMapDefaultViewport(cfg.key, true);
        });
        zoomControlContainer.appendChild(btnReset);
      }

      // Clean highlights on map mouseleave
      el.addEventListener('mouseleave', () => clearAllHighlights(cfg.key));

      mapLayers[cfg.key].spiderGroup = L.layerGroup().addTo(map);
      mapLayers[cfg.key].spiderLookup = {};
      maps[cfg.key] = map;
    });
  }

  // Choropleth Color Scale (Supports standard, mode-specific and diverging Balance scale)
  function getChoroplethColor(val, maxVal, isBalance = false, modeFilter = null) {
    if (isBalance) {
      if (val === undefined || val === null || Math.abs(val) < 0.05) return '#f8fafc';
      if (val > 0) {
        const ratio = Math.min(1, val / Math.max(1, maxVal));
        if (ratio < 0.2) return '#edf8f1';
        if (ratio < 0.45) return '#a7f3d0';
        if (ratio < 0.7) return '#34d399';
        return '#059669';
      } else {
        const ratio = Math.min(1, Math.abs(val) / Math.max(1, maxVal));
        if (ratio < 0.2) return '#eff6ff';
        if (ratio < 0.45) return '#93c5fd';
        if (ratio < 0.7) return '#3b82f6';
        return '#1d4ed8';
      }
    }

    if (!val || val <= 0) return '#f1f5f9';
    const ratio = Math.min(1, val / Math.max(1, maxVal));

    if (modeFilter === 'road') {
      if (ratio < 0.1) return '#fef3c7';
      if (ratio < 0.25) return '#fde68a';
      if (ratio < 0.5) return '#f59e0b';
      if (ratio < 0.75) return '#d97706';
      return '#92400e';
    } else if (modeFilter === 'rail') {
      if (ratio < 0.1) return '#eff6ff';
      if (ratio < 0.25) return '#bfdbfe';
      if (ratio < 0.5) return '#60a5fa';
      if (ratio < 0.75) return '#2563eb';
      return '#1e40af';
    } else if (modeFilter === 'iww') {
      if (ratio < 0.1) return '#f0fdfa';
      if (ratio < 0.25) return '#99f6e4';
      if (ratio < 0.5) return '#2dd4bf';
      if (ratio < 0.75) return '#0d9488';
      return '#115e59';
    }

    // Default overview emerald/green scale
    if (ratio < 0.1) return '#edf8f1';
    if (ratio < 0.25) return '#bae6c5';
    if (ratio < 0.5) return '#74c48d';
    if (ratio < 0.75) return '#3b9d5d';
    return '#1b5e35';
  }

  // Resolve Choropleth Value based on Active Filters & Mode Filters & Direction
  function resolveChoroplethValue(nutsId, cData, modeFilter) {
    const isTkm = state.metric === 'tkm';
    const yrSum = summaryData[nutsId]?.[state.year] || {};
    const dir = state.direction; // 'all', 'inbound', 'outbound', 'balance'
    
    // 1. If a specific commodity group is selected (1-7)
    if (state.selectedGroup && state.selectedGroup !== 'ALL') {
      const grpKey = state.selectedGroup;
      if (modeFilter) {
        const modeGroups = (isTkm ? yrSum.by_mode_groups_tkm : yrSum.by_mode_groups)?.[modeFilter];
        if (modeGroups) {
          if (dir === 'inbound') return modeGroups.inbound?.[grpKey] || 0;
          if (dir === 'outbound') return modeGroups.outbound?.[grpKey] || 0;
          if (dir === 'balance') return (modeGroups.outbound?.[grpKey] || 0) - (modeGroups.inbound?.[grpKey] || 0);
          return modeGroups.all?.[grpKey] || (modeGroups[grpKey] || 0);
        }
        return 0;
      }
      const grpObj = isTkm ? yrSum.groups_7_tkm : yrSum.groups_7_tonnes;
      if (grpObj) {
        if (dir === 'inbound') return grpObj.inbound?.[grpKey] || 0;
        if (dir === 'outbound') return grpObj.outbound?.[grpKey] || 0;
        if (dir === 'balance') return (grpObj.outbound?.[grpKey] || 0) - (grpObj.inbound?.[grpKey] || 0);
        return grpObj.all?.[grpKey] || (grpObj[grpKey] || 0);
      }
      return 0;
    }

    // 2. Mode filter active (Road, Rail, IWW) with Direction
    if (modeFilter === 'road') {
      if (dir === 'inbound') return isTkm ? (cData.road_inbound_tkm ?? cData.road_tkm ?? 0) : (cData.road_inbound_tonnes ?? cData.road_tonnes ?? 0);
      if (dir === 'outbound') return isTkm ? (cData.road_outbound_tkm ?? cData.road_tkm ?? 0) : (cData.road_outbound_tonnes ?? cData.road_tonnes ?? 0);
      if (dir === 'balance') return isTkm ? (cData.road_balance_tkm ?? 0) : (cData.road_balance_tonnes ?? 0);
      return isTkm ? (cData.road_tkm ?? 0) : (cData.road_tonnes ?? 0);
    }
    if (modeFilter === 'rail') {
      if (dir === 'inbound') return isTkm ? (cData.rail_inbound_tkm ?? cData.rail_tkm ?? 0) : (cData.rail_inbound_tonnes ?? cData.rail_tonnes ?? 0);
      if (dir === 'outbound') return isTkm ? (cData.rail_outbound_tkm ?? cData.rail_tkm ?? 0) : (cData.rail_outbound_tonnes ?? cData.rail_tonnes ?? 0);
      if (dir === 'balance') return isTkm ? (cData.rail_balance_tkm ?? 0) : (cData.rail_balance_tonnes ?? 0);
      return isTkm ? (cData.rail_tkm ?? 0) : (cData.rail_tonnes ?? 0);
    }
    if (modeFilter === 'iww') {
      if (dir === 'inbound') return isTkm ? (cData.iww_inbound_tkm ?? cData.iww_tkm ?? 0) : (cData.iww_inbound_tonnes ?? cData.iww_tonnes ?? 0);
      if (dir === 'outbound') return isTkm ? (cData.iww_outbound_tkm ?? cData.iww_tkm ?? 0) : (cData.iww_outbound_tonnes ?? cData.iww_tonnes ?? 0);
      if (dir === 'balance') return isTkm ? (cData.iww_balance_tkm ?? 0) : (cData.iww_balance_tonnes ?? 0);
      return isTkm ? (cData.iww_tkm ?? 0) : (cData.iww_tonnes ?? 0);
    }

    // 3. Overview Total (All modes combined) with Direction
    if (dir === 'inbound') return isTkm ? (cData.inbound_tkm || 0) : (cData.inbound_tonnes || 0);
    if (dir === 'outbound') return isTkm ? (cData.outbound_tkm || 0) : (cData.outbound_tonnes || 0);
    if (dir === 'balance') return isTkm ? (cData.balance_tkm || 0) : (cData.balance_tonnes || 0);

    return isTkm ? (cData.total_tkm || 0) : (cData.total_tonnes || 0);
  }

  function getOverviewTooltipFilteredValue(record) {
    if (!record) return null;
    const metricKey = state.metric === 'tkm' ? 'tkm' : 'tonnes';
    const direction = state.direction || 'all';
    const selectedGroup = state.selectedGroup;
    const hasSelectedGroup = selectedGroup && selectedGroup !== 'ALL';
    const series = hasSelectedGroup
      ? record[`groups_7_${metricKey}`]
      : record[`directions_${metricKey}`];
    const toFiniteNumber = value => value !== undefined && value !== null && Number.isFinite(Number(value))
      ? Number(value)
      : null;
    const directionValue = directionKey => toFiniteNumber(hasSelectedGroup
      ? series?.[directionKey]?.[selectedGroup]
      : series?.[directionKey]);
    const outbound = directionValue('outbound');
    const inbound = directionValue('inbound');
    const binnen = directionValue('binnen');
    let value = directionValue(direction);

    // The overview defines Versand and Empfang as the traffic touching a
    // region. A historic within-region movement is consequently present in
    // both directional source totals. VP2040 keeps it separately as "binnen".
    // Recombine only the forecast preview here so both series answer the same
    // question: Versand / Empfang each include Binnenverkehr once, their sum
    // includes it twice, and the saldo remains unaffected.
    if (binnen !== null && outbound !== null && inbound !== null) {
      if (direction === 'outbound') value = outbound + binnen;
      else if (direction === 'inbound') value = inbound + binnen;
      else if (direction === 'all') value = outbound + inbound + 2 * binnen;
      else if (direction === 'balance') value = outbound - inbound;
    }

    // The historic overview and the forecast preview store the all-direction
    // total differently. Resolve both formats so the trend always follows the
    // same active filter as the map tooltip.
    if (value === undefined || value === null) {
      if (direction === 'all') {
        value = hasSelectedGroup
          ? series?.all?.[selectedGroup]
          : (record[`total_${metricKey}`] ?? record?.[metricKey]?.total);
      } else if (direction === 'balance') {
        const outbound = hasSelectedGroup ? series?.outbound?.[selectedGroup] : series?.outbound;
        const inbound = hasSelectedGroup ? series?.inbound?.[selectedGroup] : series?.inbound;
        if (Number.isFinite(Number(outbound)) && Number.isFinite(Number(inbound))) {
          value = Number(outbound) - Number(inbound);
        }
      }
    }
    return toFiniteNumber(value);
  }

  function buildOverviewTooltipTrendSvg(nutsId) {
    // 2025 is only available for rail and inland waterways in the regional
    // overview. For an all-mode trend it would look like a real decline, so
    // retain the last fully comparable historical year here.
    const historyYears = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024];
    const history = historyYears.map(year => getOverviewTooltipFilteredValue(summaryData[nutsId]?.[String(year)]));
    const base = getOverviewTooltipFilteredValue(overviewForecastTooltipData?.scenarios?.['2019_BASE']?.regions?.[nutsId]);
    const target = getOverviewTooltipFilteredValue(overviewForecastTooltipData?.scenarios?.['2040_P1']?.regions?.[nutsId]);
    const finiteValues = [...history, base, target].filter(Number.isFinite);
    if (finiteValues.length < 2 || !Number.isFinite(target)) return '';

    const minValue = Math.min(...finiteValues);
    const maxValue = Math.max(...finiteValues);
    const rawSpan = Math.max(maxValue - minValue, Math.max(Math.abs(maxValue), 1) * 0.08);
    const containsNegativeValue = finiteValues.some(value => value < 0);
    // Beförderungsmengen und Verkehrsleistungen are non-negative.  Draw their
    // mini-chart from zero so the horizontal axis has an unambiguous meaning.
    // Only saldo charts retain a symmetric padded range around their values.
    const scaleMin = containsNegativeValue ? minValue - rawSpan * 0.12 : 0;
    const scaleMax = maxValue + (containsNegativeValue ? rawSpan * 0.12 : Math.max(maxValue * 0.10, 1));
    const plotLeft = 34;
    const plotRight = 270;
    const plotTop = 24;
    const plotBottom = 76;
    const y = value => plotTop + (scaleMax - value) / (scaleMax - scaleMin) * (plotBottom - plotTop);
    const x = year => plotLeft + (year - historyYears[0]) / (2040 - historyYears[0]) * (plotRight - plotLeft);
    const axisUnit = state.metric === 'tkm' ? 'Mrd. tkm' : 'Mio. t';
    const formatAxisValue = value => {
      const normalized = value / (state.metric === 'tkm' ? 1e9 : 1e6);
      const decimals = Math.abs(normalized) < 1 ? 2 : (Math.abs(normalized) < 10 ? 1 : 0);
      return formatDeNum(normalized, decimals);
    };
    const historySegments = [];
    let activeSegment = [];
    history.forEach((value, index) => {
      if (!Number.isFinite(value)) {
        if (activeSegment.length > 1) historySegments.push(activeSegment);
        activeSegment = [];
        return;
      }
      activeSegment.push(`${x(historyYears[index]).toFixed(1)},${y(value).toFixed(1)}`);
    });
    if (activeSegment.length > 1) historySegments.push(activeSegment);
    const historyLines = historySegments.map(points => `<polyline points="${points.join(' ')}" fill="none" stroke="#059669" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"></polyline>`).join('');
    const historyDots = history.map((value, index) => Number.isFinite(value)
      ? `<circle cx="${x(historyYears[index]).toFixed(1)}" cy="${y(value).toFixed(1)}" r="1.7" fill="#059669"></circle>`
      : '').join('');
    const baseX = x(2019);
    const targetX = x(2040);
    const forecastLine = Number.isFinite(base)
      ? `<line x1="${baseX}" y1="${y(base).toFixed(1)}" x2="${targetX}" y2="${y(target).toFixed(1)}" stroke="#7c3aed" stroke-width="2.4" stroke-dasharray="4 3" stroke-linecap="round"></line><circle cx="${baseX}" cy="${y(base).toFixed(1)}" r="2.5" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8"></circle>`
      : '';

    return `
      <div style="margin-top:7px; padding-top:6px; border-top:1px solid #ede9fe;">
        <svg viewBox="0 0 276 104" role="img" aria-label="Reale Entwicklung und VP2040-Prognose auf einer gemeinsamen Zeitachse von 2016 bis 2040; die Y-Achse verwendet für beide Reihen dieselbe Skala ab null" style="display:block; width:100%; height:104px; overflow:visible;">
          <text x="0" y="12" fill="#64748b" font-size="8.2" font-family="Inter, sans-serif">${axisUnit}</text>
          <text x="${plotLeft}" y="12" fill="#059669" font-size="9.5" font-family="Inter, sans-serif">Ist bis 2024</text>
          <text x="270" y="12" text-anchor="end" fill="#7c3aed" font-size="9.5" font-family="Inter, sans-serif">VP2040-Reihe (2019–2040)</text>
          <line x1="${plotLeft}" y1="${plotTop}" x2="${plotLeft}" y2="${plotBottom}" stroke="#94a3b8" stroke-width="1"></line>
          <line x1="${plotLeft}" y1="${plotTop}" x2="${plotRight}" y2="${plotTop}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="2 2"></line>
          <line x1="${plotLeft}" y1="${plotBottom}" x2="${plotRight}" y2="${plotBottom}" stroke="#94a3b8" stroke-width="1"></line>
          <text x="${plotLeft - 4}" y="${plotTop + 3}" text-anchor="end" fill="#64748b" font-size="8.4" font-family="Inter, sans-serif">${formatAxisValue(scaleMax)}</text>
          <text x="${plotLeft - 4}" y="${plotBottom + 3}" text-anchor="end" fill="#64748b" font-size="8.4" font-family="Inter, sans-serif">${formatAxisValue(scaleMin)}</text>
          ${historyLines}${historyDots}${forecastLine}
          <circle cx="${targetX}" cy="${y(target).toFixed(1)}" r="2.7" fill="#7c3aed"></circle>
          <text x="${plotLeft}" y="96" fill="#64748b" font-size="9.5" font-family="Inter, sans-serif">2016</text>
          <text x="${plotRight}" y="96" text-anchor="end" fill="#64748b" font-size="9.5" font-family="Inter, sans-serif">2040</text>
        </svg>
      </div>`;
  }

  function getOverviewForecastTooltipInfo(nutsId) {
    const forecastRecord = overviewForecastTooltipData?.scenarios?.['2040_P1']?.regions?.[nutsId];
    const baselineRecord = overviewForecastTooltipData?.scenarios?.['2019_BASE']?.regions?.[nutsId];
    const forecastValue = getOverviewTooltipFilteredValue(forecastRecord);
    const baselineValue = getOverviewTooltipFilteredValue(baselineRecord);
    const isBalance = state.direction === 'balance';
    const growth = !isBalance && Number.isFinite(forecastValue) && Number.isFinite(baselineValue) && baselineValue !== 0
      ? (forecastValue - baselineValue) / Math.abs(baselineValue) * 100
      : null;
    return {
      forecastValue,
      baselineValue,
      growth,
      trendSvg: Number.isFinite(forecastValue) ? buildOverviewTooltipTrendSvg(nutsId) : ''
    };
  }

  // ============================================================
  // UPDATE LEAFLET CHOROPLETH MAP (PRESERVE COLOR ON SELECTION!)
  // ============================================================
  function updateLeafletMap(mapKey, modeFilter = null, groupFilter = 'ALL') {
    const map = maps[mapKey];
    if (!map || !geojsonNuts3) return;

    if (mapLayers[mapKey].geojson) {
      map.removeLayer(mapLayers[mapKey].geojson);
    }

    let yrChoro = choroplethData[state.year] || {};
    // The 2025 regional summary is already available for rail and inland
    // waterways, while the precomputed choropleth file still ends at 2024.
    // Build the equivalent map cube on the client so the available data is
    // visible; road fields remain zero and are labelled NV elsewhere.
    if (!Object.keys(yrChoro).length && state.year === '2025') {
      yrChoro = {};
      Object.entries(summaryData).forEach(([nutsId, years]) => {
        const record = years?.[state.year];
        if (!record) return;
        const modesT = record.modes_tonnes || {}, modesK = record.modes_tkm || {};
        const dirT = record.modes_direction_tonnes || {}, dirK = record.modes_direction_tkm || {};
        yrChoro[nutsId] = {
          total_tonnes: record.total_tonnes || 0, total_tkm: record.total_tkm || 0,
          inbound_tonnes: record.directions_tonnes?.inbound || 0, outbound_tonnes: record.directions_tonnes?.outbound || 0,
          inbound_tkm: record.directions_tkm?.inbound || 0, outbound_tkm: record.directions_tkm?.outbound || 0,
          road_tonnes: modesT.road || 0, rail_tonnes: modesT.rail || 0, iww_tonnes: modesT.iww || 0,
          road_tkm: modesK.road || 0, rail_tkm: modesK.rail || 0, iww_tkm: modesK.iww || 0,
          road_inbound_tonnes: dirT.road?.inbound || 0, rail_inbound_tonnes: dirT.rail?.inbound || 0, iww_inbound_tonnes: dirT.iww?.inbound || 0,
          road_outbound_tonnes: dirT.road?.outbound || 0, rail_outbound_tonnes: dirT.rail?.outbound || 0, iww_outbound_tonnes: dirT.iww?.outbound || 0,
          road_inbound_tkm: dirK.road?.inbound || 0, rail_inbound_tkm: dirK.rail?.inbound || 0, iww_inbound_tkm: dirK.iww?.inbound || 0,
          road_outbound_tkm: dirK.road?.outbound || 0, rail_outbound_tkm: dirK.rail?.outbound || 0, iww_outbound_tkm: dirK.iww?.outbound || 0
        };
      });
    }
    const isBalance = (state.direction === 'balance');
    
    let maxVal = 1;
    Object.keys(yrChoro).forEach(nutsId => {
      const c = yrChoro[nutsId] || {};
      const v = resolveChoroplethValue(nutsId, c, modeFilter);
      const absV = Math.abs(v);
      if (absV > maxVal) maxVal = absV;
    });

    updateMapLegend(mapKey, modeFilter, isBalance, maxVal);

    mapLayers[mapKey].geojson = L.geoJSON(geojsonNuts3, {
      style: feature => {
        const nutsId = feature.properties.NUTS_ID;
        const isSelected = nutsId === state.region;
        const cData = yrChoro[nutsId] || {};
        const val = resolveChoroplethValue(nutsId, cData, modeFilter);
        const fillColor = getChoroplethColor(val, maxVal, isBalance, modeFilter);

        // ONLY highlight border on selected region, PRESERVE underlying choropleth color!
        return {
          fillColor: fillColor,
          weight: isSelected ? 3.5 : 0.75,
          opacity: 1,
          color: isSelected ? '#0f172a' : '#94a3b8',
          fillOpacity: isSelected ? 0.88 : 0.65
        };
      },
      onEachFeature: (feature, layer) => {
        const nutsId = feature.properties.NUTS_ID;
        const isSelected = Boolean(state.region && nutsId === state.region);
        const nutsName = feature.properties.NUTS_NAME;
        const cData = yrChoro[nutsId] || {};
        const val = resolveChoroplethValue(nutsId, cData, modeFilter);
        const isTkm = state.metric === 'tkm';
        const unit = isTkm ? 'Mrd. tkm' : 'Mio. t';
        const divisor = isTkm ? 1e9 : 1e6;

        let dirLabel = 'Aufkommen';
        if (state.direction === 'inbound') dirLabel = 'Empfang';
        else if (state.direction === 'outbound') dirLabel = 'Versand';
        else if (state.direction === 'balance') dirLabel = 'Saldo';

        const selectedGroupLabel = (state.selectedGroup && state.selectedGroup !== 'ALL') ? ` (${NST_GROUPS_7[state.selectedGroup]})` : '';
        const measureLabel = `${dirLabel}${selectedGroupLabel}`;
        const formatTooltipValue = value => {
          const sign = isBalance && value > 0 ? '+' : '';
          const status = isBalance ? `<br><span style="font-size:0.75rem; color:#64748b;">${value > 0 ? 'Netto-Versand' : (value < 0 ? 'Netto-Empfang' : 'Ausgeglichen')}</span>` : '';
          return `<span style="white-space:normal; overflow-wrap:break-word;">${measureLabel}: <strong>${sign}${formatDeNum(value / divisor, 2)} ${unit}</strong></span>${status}`;
        };
        const displayVal = formatTooltipValue(val);
        const forecastInfo = getOverviewForecastTooltipInfo(nutsId);
        const forecastDisplay = Number.isFinite(forecastInfo.forecastValue)
          ? formatTooltipValue(forecastInfo.forecastValue)
          : `${measureLabel}: <strong style="color:#64748b;">nicht verfügbar</strong>`;
        const forecastBaselineDisplay = Number.isFinite(forecastInfo.baselineValue)
          ? `• VP2040-Basisjahr 2019: <strong>${formatDeNum(forecastInfo.baselineValue / divisor, 2)} ${unit}</strong>`
          : '• VP2040-Basisjahr 2019: <strong style="color:#64748b;">nicht verfügbar</strong>';
        const growthDisplay = isBalance
          ? '<div style="font-size:0.72rem; color:#64748b; margin-top:3px;">Für Salden wird kein prozentualer Prognosevergleich ausgewiesen.</div>'
          : Number.isFinite(forecastInfo.growth)
            ? `<div style="font-size:0.72rem; color:${forecastInfo.growth >= 0 ? '#16a34a' : '#dc2626'}; font-weight:700; margin-top:3px;">${forecastInfo.growth >= 0 ? '↗ +' : '↘ '}${formatDeNum(forecastInfo.growth, 1)} % gegenüber VP2040-Basisjahr 2019</div>`
            : '<div style="font-size:0.72rem; color:#64748b; margin-top:3px;">VP2040-Basisjahr 2019: kein Vergleichswert</div>';
        const forecastBlock = mapKey === 'overview' && overviewForecastTooltipData ? `
            <div style="margin-top:7px; padding-top:6px; border-top:1px solid #ddd6fe;">
              <div style="font-size:0.68rem; font-weight:700; color:#6d28d9; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:2px;">Prognose 2040 · P1</div>
              • ${forecastDisplay}
              <div style="font-size:0.72rem; color:#475569; margin-top:3px;">${forecastBaselineDisplay}</div>
              ${growthDisplay}
              ${forecastInfo.trendSvg}
            </div>` : '';

        layer.bindTooltip(`
          <div class="map-region-tooltip" style="font-size:0.825rem; line-height:1.45; width:min(360px, calc(100vw - 42px)); min-width:0; max-width:calc(100vw - 42px); box-sizing:border-box; white-space:normal;">
            <div style="font-size:0.68rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:2px;">Landkreis / kreisfreie Stadt</div>
            <strong>${nutsName}</strong> <span style="font-size:0.75rem; color:#64748b; font-weight:600;">(${nutsId})</span>
            <div style="margin-top:7px; padding-top:6px; border-top:1px solid #e2e8f0;">
              <div style="font-size:0.68rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:2px;">Bezugsjahr · ${state.year}</div>
              • ${displayVal}
            </div>
            ${forecastBlock}
            <div class="map-tooltip-filter-hint" style="display:block; max-width:none; margin-top:7px; white-space:normal; overflow-wrap:anywhere; line-height:1.3;">Klicken Sie, um diese Region/diesen Kreis als Filter zu aktivieren.</div>
          </div>
        `, { sticky: true });

        if (isSelected && layer.bringToFront) {
          setTimeout(() => { if (layer.bringToFront) layer.bringToFront(); }, 0);
        }

        // Bi-directional click interaction
        layer.on('click', async () => {
          await setRegion(nutsId);
        });
      }
    }).addTo(map);

    if (state.region && mapLayers[mapKey].geojson) {
      mapLayers[mapKey].geojson.eachLayer(l => {
        const nId = l.feature?.properties?.NUTS_ID || l.feature?.properties?.id;
        if (nId === state.region && l.bringToFront) {
          l.bringToFront();
        }
      });
    }

    renderMapSpiderLines(mapKey, modeFilter, groupFilter);
    drawSelectedRegionOutline(mapKey);
  }

  function drawSelectedRegionOutline(mapKey) {
    const map = maps[mapKey];
    if (!map || !geojsonNuts3) return;
    if (mapLayers[mapKey].selection) map.removeLayer(mapLayers[mapKey].selection);
    if (!state.region) return;
    const selected = (geojsonNuts3.features || []).find(feature => feature.properties?.NUTS_ID === state.region);
    if (!selected) return;
    mapLayers[mapKey].selection = L.geoJSON(selected, { pane: 'selectionPane', interactive: false, style: { fillOpacity: 0, color: '#0f172a', weight: 3.5, opacity: 1 } }).addTo(map);
  }

  // Helper: Compute discrete, clean class boundaries for flow spider lines & legend
  function getFlowClassification(flows, isTkm) {
    const divF = isTkm ? 1e6 : 1e3;
    const uF = isTkm ? 'Mio. tkm' : 'Tsd. t';

    if (!flows || flows.length === 0) {
      return {
        labelThin: '--',
        labelMed: '--',
        labelThick: '--',
        unit: uF,
        getWeight: () => 2.2,
        getRadius: () => 4.5
      };
    }

    const fVals = flows.map(f => Math.abs((isTkm ? f.tkm : f.tonnes) || 0)).filter(v => v > 0);
    if (fVals.length === 0) {
      return {
        labelThin: '--',
        labelMed: '--',
        labelThick: '--',
        unit: uF,
        getWeight: () => 2.2,
        getRadius: () => 4.5
      };
    }

    const fMax = Math.max(...fVals);
    const maxInUnit = fMax / divF;

    let t1Unit, t2Unit;
    if (maxInUnit <= 0) {
      t1Unit = 1;
      t2Unit = 2;
    } else {
      const mag = Math.pow(10, Math.floor(Math.log10(maxInUnit)));
      const norm = maxInUnit / mag;

      if (norm < 2.0) {
        t1Unit = 0.4 * mag;
        t2Unit = 0.9 * mag;
      } else if (norm < 4.0) {
        t1Unit = 1.0 * mag;
        t2Unit = 2.0 * mag;
      } else if (norm < 7.0) {
        t1Unit = (mag < 10) ? 1.5 * mag : 2.0 * mag;
        t2Unit = (mag < 10) ? 3.5 * mag : 4.0 * mag;
      } else {
        t1Unit = 2.0 * mag;
        t2Unit = 5.0 * mag;
      }

      if (t2Unit >= maxInUnit) {
        t2Unit = Math.round(maxInUnit * 0.65 * 10) / 10;
        t1Unit = Math.round(maxInUnit * 0.30 * 10) / 10;
      }
    }

    if (t1Unit <= 0) t1Unit = Math.max(0.1, Math.round(maxInUnit * 0.3 * 10) / 10);
    if (t2Unit <= t1Unit) t2Unit = Math.max(t1Unit * 2, Math.round(maxInUnit * 0.7 * 10) / 10);

    const t1Raw = t1Unit * divF;
    const t2Raw = t2Unit * divF;

    const fmt = (v) => formatDeNum(v, (v % 1 !== 0) ? 1 : 0);

    const labelThin = `< ${fmt(t1Unit)} ${uF}`;
    const labelMed = `${fmt(t1Unit)} – ${fmt(t2Unit)} ${uF}`;
    const labelThick = `> ${fmt(t2Unit)} ${uF}`;

    const getWeight = (valRaw) => {
      valRaw = Math.abs(valRaw || 0);
      if (valRaw < t1Raw) return 2.2;
      if (valRaw < t2Raw) return 4.8;
      return 8.0;
    };

    const getRadius = (valRaw) => {
      valRaw = Math.abs(valRaw || 0);
      if (valRaw < t1Raw) return 4.5;
      if (valRaw < t2Raw) return 6.5;
      return 9.0;
    };

    return {
      t1Raw,
      t2Raw,
      t1Unit,
      t2Unit,
      labelThin,
      labelMed,
      labelThick,
      unit: uF,
      getWeight,
      getRadius
    };
  }

  // Update Legend Box dynamically across all modules
  function updateMapLegend(mapKey, modeFilter, isBalance, maxVal) {
    const legendEl = document.getElementById(`${mapKey}ChoroplethLegend`);
    if (!legendEl) return;

    const isTkm = state.metric === 'tkm';
    const unit = isTkm ? 'Mrd. tkm' : 'Mio. t';
    const divisor = isTkm ? 1e9 : 1e6;

    const measureTitle = isTkm ? 'Verkehrsleistung' : 'Verkehrsaufkommen';
    const modeTitles = {
      overview: `Güterverkehr: ${measureTitle}`,
      road: `Straßengüterverkehr: ${measureTitle}`,
      rail: `Schienengüterverkehr: ${measureTitle}`,
      iww: `Binnenschifffahrt: ${measureTitle}`,
      forecast: `Prognose 2040: ${measureTitle}`
    };
    const balanceTitles = {
      overview: 'Güterverkehr: Saldo',
      road: 'Straßengüterverkehr: Saldo',
      rail: 'Schienengüterverkehr: Saldo',
      iww: 'Binnenschifffahrt: Saldo',
      forecast: 'Prognose 2040: Saldo'
    };

    let titleText;
    if (isBalance) {
      titleText = balanceTitles[mapKey] || 'Güterverkehr: Saldo';
    } else {
      titleText = modeTitles[mapKey] || `Güterverkehr: ${measureTitle}`;
    }

    let scaleHtml = '';
    if (isBalance) {
      scaleHtml = `
        <span style="background: #38bdf8;" title="Netto-Empfang"></span>
        <span style="background: #e0f2fe;"></span>
        <span style="background: #f8fafc;"></span>
        <span style="background: #dcfce7;"></span>
        <span style="background: #22c55e;" title="Netto-Versand"></span>
      `;
    } else if (mapKey === 'forecast') {
      scaleHtml = `
        <span style="background: #f8fafc;"></span>
        <span style="background: #e0f2fe;"></span>
        <span style="background: #bae6fd;"></span>
        <span style="background: #60a5fa;"></span>
        <span style="background: #2563eb;"></span>
      `;
    } else if (modeFilter === 'road') {
      scaleHtml = `
        <span style="background: #fef3c7;"></span>
        <span style="background: #fde68a;"></span>
        <span style="background: #f59e0b;"></span>
        <span style="background: #d97706;"></span>
        <span style="background: #92400e;"></span>
      `;
    } else if (modeFilter === 'rail') {
      scaleHtml = `
        <span style="background: #eff6ff;"></span>
        <span style="background: #bfdbfe;"></span>
        <span style="background: #60a5fa;"></span>
        <span style="background: #2563eb;"></span>
        <span style="background: #1e40af;"></span>
      `;
    } else if (modeFilter === 'iww') {
      scaleHtml = `
        <span style="background: #f0fdfa;"></span>
        <span style="background: #99f6e4;"></span>
        <span style="background: #2dd4bf;"></span>
        <span style="background: #0d9488;"></span>
        <span style="background: #115e59;"></span>
      `;
    } else {
      scaleHtml = `
        <span style="background: #edf8f1;"></span>
        <span style="background: #bae6c5;"></span>
        <span style="background: #74c48d;"></span>
        <span style="background: #3b9d5d;"></span>
        <span style="background: #1b5e35;"></span>
      `;
    }

    let labelsHtml = '';
    if (isBalance) {
      labelsHtml = `
        <span title="Stärkste Klasse mit Empfangsüberschuss">≤ −${formatDeNum(maxVal * 0.8 / divisor, 1)} ${unit}</span>
        <span title="Stärkste Klasse mit Versandüberschuss">≥ +${formatDeNum(maxVal * 0.8 / divisor, 1)} ${unit}</span>
      `;
    } else {
      labelsHtml = `
        <span>&lt; ${formatDeNum(maxVal * 0.1 / divisor, 1)} ${unit}</span>
        <span>&gt; ${formatDeNum(maxVal * 0.8 / divisor, 1)} ${unit}</span>
      `;
    }

    // Preserve isCollapsed state if already toggled by user
    const isCollapsed = legendEl.classList.contains('collapsed');

    // Determine Spider Line thickness section
    const isSpiderEnabled = (mapKey === 'overview' && state.showSpider) ||
                            (mapKey === 'road' && state.showRoadSpider) ||
                            (mapKey === 'rail' && state.showRailSpider) ||
                            (mapKey === 'iww' && state.showIwwSpider) ||
                            (mapKey === 'forecast' && state.showForecastSpider);

    let spiderHtml = '';
    let repColor = isBalance ? '#16a34a' : '#059669';
    if (!isBalance && modeFilter === 'road') repColor = '#f59e0b';
    else if (!isBalance && modeFilter === 'rail') repColor = '#2563eb';
    else if (!isBalance && modeFilter === 'iww') repColor = '#0d9488';
    else if (!isBalance && mapKey === 'forecast') repColor = '#7c3aed';

    if (isSpiderEnabled && state.region) {
      let fl = [];
      if (mapKey === 'forecast') {
        const sc = forecastData?.scenarios?.[state.forecastScenario] || forecastData?.scenarios?.['2040_P1'];
        const rData = sc?.regions?.[state.region];
        if (rData) {
          const dirKey = (state.direction === 'inbound' || state.direction === 'outbound') ? state.direction : 'all';
          if (state.selectedGroup && state.selectedGroup !== 'ALL') {
            fl = [...(rData.by_group_relations?.[state.selectedGroup]?.[dirKey] || rData.by_group_relations?.[state.selectedGroup]?.all || [])];
          } else {
            fl = [...(rData.relations_overall?.[dirKey] || rData.relations_overall?.all || [])];
          }
        }
      } else if (modeFilter) {
        const regTopAll = getRegionRelations(state.region);
        const yrTop = regTopAll[state.year] || {};
        const modeObj = yrTop.by_mode?.[modeFilter] || {};
        const rawList = (state.direction === 'inbound') ? (modeObj.inbound || []) : (modeObj.outbound || []);
        if (state.selectedGroup && state.selectedGroup !== 'ALL') {
          if (modeObj.by_group?.[state.selectedGroup]) {
            fl = (state.direction === 'inbound') ? [...(modeObj.by_group[state.selectedGroup].inbound || [])] : [...(modeObj.by_group[state.selectedGroup].outbound || [])];
          } else {
            fl = rawList.filter(r => r.group_7 === state.selectedGroup).map(r => ({ ...r }));
          }
        } else {
          // Aggregate by partner across all commodity groups
          const partnerMap = {};
          rawList.forEach(r => {
            const pId = r.dest_id || r.origin_id;
            if (!pId) return;
            if (!partnerMap[pId]) {
              partnerMap[pId] = {
                ...r,
                group_7: 'ALL',
                tonnes: r.tonnes || 0,
                tkm: r.tkm || 0
              };
            } else {
              partnerMap[pId].tonnes += (r.tonnes || 0);
              partnerMap[pId].tkm += (r.tkm || 0);
            }
          });
          fl = Object.values(partnerMap);
        }
      } else {
        const regTopAll = getRegionRelations(state.region);
        const yrTop = regTopAll[state.year] || {};
        const ov = getOverviewRelations(yrTop, state.selectedGroup, state.direction, regTopAll);
        fl = ov.flows || [];
      }

      if (!state.includeBinnen) {
        fl = fl.filter(r => !r.is_binnen && (r.dest_id !== state.region) && (r.origin_id !== state.region) && (r.partner_id !== state.region));
      }
      const relationMetric = row => isTkm ? (row.tkm || 0) : (row.tonnes || 0);
      fl.sort((a, b) => isBalance
        ? Math.abs(relationMetric(b)) - Math.abs(relationMetric(a))
        : relationMetric(b) - relationMetric(a));
      const topFlows = fl.slice(0, state.topX);

      if (topFlows.length > 0) {
        const cls = getFlowClassification(topFlows, isTkm);

        spiderHtml = `
          <div class="legend-spider-section">
            <div class="legend-subtitle">Verbindungen</div>
            <div class="legend-spider-rows">
              <div class="legend-spider-item">
                <span class="legend-line legend-line-thin" style="background: ${repColor};"></span>
                <span class="legend-spider-val">${cls.labelThin}</span>
              </div>
              <div class="legend-spider-item">
                <span class="legend-line legend-line-med" style="background: ${repColor};"></span>
                <span class="legend-spider-val">${cls.labelMed}</span>
              </div>
              <div class="legend-spider-item">
                <span class="legend-line legend-line-thick" style="background: ${repColor};"></span>
                <span class="legend-spider-val">${cls.labelThick}</span>
              </div>
            </div>
            ${isBalance ? `
              <div class="legend-spider-rows" style="margin-top:6px;">
                <div class="legend-spider-item"><span class="legend-line legend-line-med" style="background:#16a34a;"></span><span class="legend-spider-val">Grün: Versandüberschuss</span></div>
                <div class="legend-spider-item"><span class="legend-line legend-line-med" style="background:#7c3aed;"></span><span class="legend-spider-val">Lila: Empfangsüberschuss</span></div>
              </div>` : ''}
          </div>
        `;
      }
    }

    legendEl.innerHTML = `
      <div class="legend-header">
        <span class="legend-title">${titleText}</span>
        <button type="button" class="btn-legend-toggle" id="btnToggleLegend_${mapKey}" title="${isCollapsed ? 'Legende maximieren' : 'Legende minimieren'}">${isCollapsed ? '+' : '−'}</button>
      </div>
      <div class="legend-body" ${isCollapsed ? 'style="display:none;"' : ''}>
        <div class="legend-scale">${scaleHtml}</div>
        <div class="legend-labels">${labelsHtml}</div>
        ${spiderHtml}
      </div>
    `;

    // Rebind the toggle button on dynamically updated legend
    const btn = legendEl.querySelector('.btn-legend-toggle');
    if (btn) {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        legendEl.dataset.legendUserToggled = 'true';
        setLegendCollapsedState(legendEl, !legendEl.classList.contains('collapsed'));
      });
    }
  }

  // ============================================================
  // ROBUST BI-DIRECTIONAL HIGHLIGHTING HELPER FUNCTIONS
  // ============================================================
  function clearAllHighlights(mapKey) {
    activeHighlightedPartnerId = null;
    activeHighlightedMapKey = null;

    // 1. Remove table highlights across all tables
    document.querySelectorAll('.data-table tbody tr.row-highlight').forEach(r => {
      r.classList.remove('row-highlight');
    });

    // 2. Revert all map spider lines and markers in this map
    const lookup = mapLayers[mapKey]?.spiderLookup || {};
    Object.values(lookup).forEach(item => {
      if (item.line) {
        item.line.setStyle({
          color: item.originalColor,
          weight: item.originalWeight,
          opacity: 0.85
        });
      }
      if (item.marker) {
        item.marker.setStyle({
          fillColor: item.originalColor,
          radius: Math.max(4, item.originalWeight + 1.5),
          weight: 2,
          color: '#ffffff'
        });
      }
    });
  }

  function setHighlight(mapKey, partnerId) {
    if (!partnerId) return;
    if (activeHighlightedPartnerId === partnerId && activeHighlightedMapKey === mapKey) return;

    // Reset previous
    clearAllHighlights(activeHighlightedMapKey || mapKey);
    activeHighlightedPartnerId = partnerId;
    activeHighlightedMapKey = mapKey;

    // Highlight matching table rows
    const rows = document.querySelectorAll(`.data-table tbody tr[data-partner-id="${partnerId}"]`);
    rows.forEach(r => {
      r.classList.add('row-highlight');
      r.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });

    // Highlight map relation
    const lookup = mapLayers[mapKey]?.spiderLookup || {};
    const item = lookup[partnerId];
    if (item) {
      if (item.line) {
        item.line.setStyle({
          color: '#2563eb', // Vivid Blue Highlight
          weight: Math.max(6.5, item.originalWeight + 3.5),
          opacity: 1.0
        });
        item.line.bringToFront();
      }
      if (item.marker) {
        item.marker.setStyle({
        fillColor: '#2563eb',
          radius: Math.max(6.5, item.originalWeight + 3.5),
          weight: 3,
          color: '#ffffff'
        });
        item.marker.bringToFront();
      }
    }
  }

  // Leaflet's SVG mouseout is not emitted consistently in Chromium when a
  // pointer crosses a marker, line and tooltip in rapid succession. Track the
  // currently opened relation tooltip explicitly, so a new relation replaces
  // the old one instead of allowing several panels to remain on the map.
  function closeActiveRelationTooltip(mapKey) {
    const layerState = mapLayers[mapKey];
    if (!layerState) return;
    layerState.activeTooltipLayer?.closeTooltip?.();
    layerState.activeTooltipLayer = null;
  }

  function closeMapTooltips(map) {
    if (!map?.eachLayer) return;
    const closeOnLayer = layer => {
      layer.closeTooltip?.();
      layer.eachLayer?.(closeOnLayer);
    };
    map.eachLayer(closeOnLayer);
  }

  function openActiveRelationTooltip(mapKey, layer, event) {
    const map = maps[mapKey];
    const layerState = mapLayers[mapKey];
    if (!map || !layerState || !layer) return;
    if (layerState.activeTooltipLayer !== layer) closeActiveRelationTooltip(mapKey);
    // Region tooltips and relation tooltips must not be visible concurrently.
    // Leaflet's map.closeTooltip requires a concrete tooltip object; closing
    // the bound layer tooltips avoids its undefined.close runtime error.
    closeMapTooltips(map);
    layer.openTooltip(event?.latlng);
    layerState.activeTooltipLayer = layer;
  }

  // The map itself is the reliable fallback when the pointer reaches its base
  // layer without Leaflet having emitted the corresponding SVG mouseout.
  function bindMapHighlightReset(mapKey) {
    const map = maps[mapKey];
    const layerState = mapLayers[mapKey];
    if (!map || !layerState || layerState.highlightResetBound) return;

    const resetWhenLeavingRelation = event => {
      if (activeHighlightedMapKey !== mapKey) return;
      const target = event?.originalEvent?.target;
      if (target?.closest?.('.flow-relation-target')) return;
      closeActiveRelationTooltip(mapKey);
      clearAllHighlights(mapKey);
    };

    map.on('mousemove', resetWhenLeavingRelation);
    map.getContainer().addEventListener('mouseleave', resetWhenLeavingRelation);
    layerState.highlightResetBound = true;
  }

  // Helper: Get active transport modes with traffic > 0 for a partner
  function getInvolvedModes(yrTop, partnerId, direction = 'all', groupFilter = 'ALL') {
    if (!yrTop || !yrTop.by_mode || !partnerId) return ['road'];
    const modes = ['road', 'rail', 'iww'];
    const activeModes = [];

    modes.forEach(m => {
      const mObj = yrTop.by_mode[m];
      if (!mObj) return;
      let list = [];
      const grouped = groupFilter && groupFilter !== 'ALL'
        ? mObj.by_group?.[groupFilter]
        : null;
      if (direction === 'outbound') list = grouped?.outbound || mObj.outbound || [];
      else if (direction === 'inbound') list = grouped?.inbound || mObj.inbound || [];
      else list = [...(grouped?.outbound || mObj.outbound || []), ...(grouped?.inbound || mObj.inbound || [])];

      if (groupFilter && groupFilter !== 'ALL' && !grouped) {
        list = list.filter(r => r.group_7 === groupFilter);
      }

      const hasTraffic = list.some(r => (r.dest_id === partnerId || r.origin_id === partnerId) && ((r.tonnes || 0) > 0 || (r.tkm || 0) > 0));
      if (hasTraffic) {
        activeModes.push(m);
      }
    });

    return activeModes.length > 0 ? activeModes : ['road'];
  }

  // Helper: Format list of mode keys into clean readable German string
  function formatModeList(modesList) {
    const modeLabels = { road: 'Straße', rail: 'Schiene', iww: 'Binnenschiff' };
    if (!modesList || modesList.length === 0) return 'Straße';
    return modesList.map(m => modeLabels[m] || m).join(', ');
  }

  // Helper: Compute YoY and Trend vs earliest base year (2016) dynamically from historical years in regTopAll
  function computeFlowTrends(flows, mode, direction, groupFilter, regTopAll, currentYear, isTkm) {
    if (!flows || !regTopAll || flows.length === 0) return;
    const prevYearStr = String(parseInt(currentYear) - 1);
    const baseYearStr = '2016'; // Earliest available baseline year in regional datasets

    function getHistoricalVol(yStr, pId, grp) {
      const yrObj = regTopAll[yStr];
      if (!yrObj) return null;
      const value = row => isTkm ? Number(row?.tkm || 0) : Number(row?.tonnes || 0);
      const sumForPartner = (rows, group = null) => (rows || [])
        .filter(row => (!group || group === 'ALL' || row.group_7 === group) && (row.dest_id === pId || row.origin_id === pId))
        .reduce((sum, row) => sum + value(row), 0);
      const selectDirection = (outbound, inbound) => {
        const out = sumForPartner(outbound, grp);
        const inn = sumForPartner(inbound, grp);
        if (direction === 'outbound') return out;
        if (direction === 'inbound') return inn;
        // A historic saldo uses the same definition as the current view:
        // Versand minus Empfang. It is not a percentage rate.
        if (direction === 'balance') return out - inn;
        return out + inn;
      };

      if (mode && mode !== 'overview') {
        const mObj = yrObj.by_mode?.[mode];
        if (!mObj) return 0;
        // Relation candidates are retained separately for every goods group.
        // The all-goods candidate list is intentionally not a complete
        // group-level history, so it may not contain a small but valid
        // relation from the current selection (e.g. Berlin--Nürnberg IWW).
        // Always use the matching group list when it is available.
        const grouped = grp && grp !== 'ALL' ? mObj.by_group?.[grp] : null;
        return grouped
          ? selectDirection(grouped.outbound, grouped.inbound)
          : selectDirection(mObj.outbound, mObj.inbound);
      }

      if (!grp || grp === 'ALL') {
        return selectDirection(yrObj.outbound_overall, yrObj.inbound_overall);
      }

      return ['road', 'rail', 'iww'].reduce((sum, modeKey) => {
        const mObj = yrObj.by_mode?.[modeKey];
        if (!mObj) return sum;
        const grouped = mObj.by_group?.[grp];
        return sum + (grouped
          ? selectDirection(grouped.outbound, grouped.inbound)
          : selectDirection(mObj.outbound, mObj.inbound));
      }, 0);
    }

    flows.forEach(f => {
      const pId = f.dest_id || f.origin_id;
      const currVol = isTkm ? (f.tkm || 0) : (f.tonnes || 0);
      const grp = f.group_7 || groupFilter || 'ALL';

      const prevVol = getHistoricalVol(prevYearStr, pId, grp);
      const hasPrevious = prevVol !== null && String(currentYear) !== prevYearStr;
      f.previous_value = hasPrevious ? prevVol : null;
      if (direction !== 'balance' && prevVol > 0 && hasPrevious) {
        f.yoy_pct = ((currVol - prevVol) / prevVol) * 100;
      } else if (f.yoy_pct === undefined) {
        f.yoy_pct = null;
      }

      const trendVol = getHistoricalVol(baseYearStr, pId, grp);
      const hasBaseline = trendVol !== null && String(currentYear) !== baseYearStr;
      f.baseline_value = hasBaseline ? trendVol : null;
      if (direction !== 'balance' && trendVol > 0 && hasBaseline) {
        f.trend_10yr_pct = ((currVol - trendVol) / trendVol) * 100;
      } else {
        f.trend_10yr_pct = null;
      }
    });
  }

  // Combine both directions by partner.  A balance is always defined as
  // Versand minus Empfang; it is never a relabelled total volume.
  function mergeDirectionalRelations(outbound = [], inbound = [], options = {}) {
    const mode = options.mode || 'total';
    const group = options.group || 'ALL';
    const asBalance = Boolean(options.asBalance);
    const partners = {};

    const add = (raw, direction) => {
      const partnerId = raw?.partner_id || raw?.dest_id || raw?.origin_id;
      if (!partnerId) return;
      if (!partners[partnerId]) {
        partners[partnerId] = {
          ...raw,
          partner_id: partnerId,
          dest_id: partnerId,
          origin_id: partnerId,
          dest_name: raw.dest_name || raw.origin_name || '',
          origin_name: raw.origin_name || raw.dest_name || '',
          group_7: group,
          mode,
          modes_list: mode === 'total' ? [] : [mode],
          is_binnen: Boolean(raw.is_binnen),
          outbound_tonnes: 0,
          inbound_tonnes: 0,
          outbound_tkm: 0,
          inbound_tkm: 0
        };
      }
      const target = partners[partnerId];
      target.is_binnen = target.is_binnen && Boolean(raw.is_binnen);
      target[`${direction}_tonnes`] += Number(raw.tonnes || 0);
      target[`${direction}_tkm`] += Number(raw.tkm || 0);
      target.dest_name ||= raw.dest_name || raw.origin_name || '';
      target.origin_name ||= raw.origin_name || raw.dest_name || '';
    };

    outbound.forEach(raw => add(raw, 'outbound'));
    inbound.forEach(raw => add(raw, 'inbound'));

    return Object.values(partners)
      .map(flow => ({
        ...flow,
        tonnes: asBalance ? flow.outbound_tonnes - flow.inbound_tonnes : flow.outbound_tonnes + flow.inbound_tonnes,
        tkm: asBalance ? flow.outbound_tkm - flow.inbound_tkm : flow.outbound_tkm + flow.inbound_tkm,
        yoy_pct: asBalance ? null : flow.yoy_pct,
        trend_10yr_pct: asBalance ? null : flow.trend_10yr_pct
      }))
      .filter(flow => !asBalance || Math.abs(flow.tonnes || 0) > 0 || Math.abs(flow.tkm || 0) > 0);
  }

  function getModeRelations(modeData, groupFilter, direction, mode) {
    const listForDirection = dir => {
      if (groupFilter && groupFilter !== 'ALL') {
        const grouped = modeData.by_group?.[groupFilter]?.[dir];
        return grouped ? [...grouped] : (modeData[dir] || []).filter(row => row.group_7 === groupFilter);
      }
      return [...(modeData[dir] || [])];
    };

    const outbound = direction === 'inbound' ? [] : listForDirection('outbound');
    const inbound = direction === 'outbound' ? [] : listForDirection('inbound');
    return mergeDirectionalRelations(outbound, inbound, {
      mode,
      group: groupFilter || 'ALL',
      asBalance: direction === 'balance'
    });
  }

  // Helper: Discover Relations across Modes with Aggregated Summation & YoY/Trend Calculation
  function getOverviewRelations(yrTop, groupFilter, direction, regTopAll = null) {
    const isTkm = state.metric === 'tkm';

    if (!groupFilter || groupFilter === 'ALL') {
      let list = [];
      if (direction === 'outbound') list = (yrTop.outbound_overall || []).map(r => ({ ...r, mode: 'total' }));
      else if (direction === 'inbound') list = (yrTop.inbound_overall || []).map(r => ({ ...r, mode: 'total' }));
      else if (direction === 'balance') {
        list = mergeDirectionalRelations(yrTop.outbound_overall || [], yrTop.inbound_overall || [], {
          mode: 'total',
          asBalance: true
        });
      }
      else {
        const out = yrTop.outbound_overall || [];
        const inb = yrTop.inbound_overall || [];
        const merged = {};
        [...out, ...inb].forEach(r => {
          const key = r.dest_id || r.origin_id || '';
          if (!merged[key]) { merged[key] = { ...r, mode: 'total' }; }
          else { 
            merged[key].tonnes = (merged[key].tonnes || 0) + (r.tonnes || 0);
            merged[key].tkm = (merged[key].tkm || 0) + (r.tkm || 0);
          }
        });
        list = Object.values(merged);
      }

      // Populate accurate involved modes list for each relation
      list.forEach(r => {
        const pId = r.dest_id || r.origin_id || '';
        r.modes_list = getInvolvedModes(yrTop, pId, direction, 'ALL');
      });

      // The same historical relation series also supplies raw prior saldos.
      computeFlowTrends(list, 'overview', direction, 'ALL', regTopAll, state.year, isTkm);

      return { flows: list, availability: { road: true, rail: true, iww: true } };
    }

    // Specific NST-2007 commodity group -> SUM across all modes that have data for each partner!
    const modes = ['rail', 'iww', 'road'];
    const mergedPartners = {};
    const availability = { road: false, rail: false, iww: false };

    if (direction === 'balance') {
      const outbound = [];
      const inbound = [];
      modes.forEach(m => {
        const modeObj = yrTop.by_mode?.[m];
        if (!modeObj) return;
        const selectedOutbound = modeObj.by_group?.[groupFilter]?.outbound || (modeObj.outbound || []).filter(row => row.group_7 === groupFilter);
        const selectedInbound = modeObj.by_group?.[groupFilter]?.inbound || (modeObj.inbound || []).filter(row => row.group_7 === groupFilter);
        if (selectedOutbound.length || selectedInbound.length) availability[m] = true;
        outbound.push(...selectedOutbound);
        inbound.push(...selectedInbound);
      });
      const flows = mergeDirectionalRelations(outbound, inbound, {
        mode: 'total',
        group: groupFilter,
        asBalance: true
      });
      flows.forEach(flow => {
        flow.modes_list = getInvolvedModes(yrTop, flow.partner_id, 'balance', groupFilter);
      });
      computeFlowTrends(flows, 'overview', direction, groupFilter, regTopAll, state.year, isTkm);
      return { flows, availability };
    }

    modes.forEach(m => {
      const modeObj = yrTop.by_mode?.[m];
      if (!modeObj) return;
      const grouped = modeObj.by_group?.[groupFilter];

      let modeList = [];
      if (direction === 'outbound') modeList = grouped?.outbound || modeObj.outbound || [];
      else if (direction === 'inbound') modeList = grouped?.inbound || modeObj.inbound || [];
      else {
        const out = grouped?.outbound || modeObj.outbound || [];
        const inb = grouped?.inbound || modeObj.inbound || [];
        modeList = [...out, ...inb];
      }

      const grpFlows = grouped ? modeList : modeList.filter(r => r.group_7 === groupFilter);
      if (grpFlows.length > 0) {
        availability[m] = true;
        grpFlows.forEach(f => {
          const partnerId = f.dest_id || f.origin_id || '';
          if (!partnerId) return;
          if (!mergedPartners[partnerId]) {
            mergedPartners[partnerId] = {
              ...f,
              mode: 'total',
              modes_list: [m],
              tonnes: f.tonnes || 0,
              tkm: f.tkm || 0
            };
          } else {
            mergedPartners[partnerId].tonnes += (f.tonnes || 0);
            mergedPartners[partnerId].tkm += (f.tkm || 0);
            if (!mergedPartners[partnerId].modes_list.includes(m)) {
              mergedPartners[partnerId].modes_list.push(m);
            }
          }
        });
      }
    });

    const allFlows = Object.values(mergedPartners);

    // Compute YoY and 10yr Trend dynamically from historical years in regTopAll
    computeFlowTrends(allFlows, 'overview', direction, groupFilter, regTopAll, state.year, isTkm);

    return { flows: allFlows, availability };
  }

  // Dynamic Map Title Updater for all modules (Clean & Slender phrasing with explicit Direction)
  function updateMapTitles() {
    const isTkm = state.metric === 'tkm';
    const metricText = isTkm ? 'Verkehrsleistung' : 'Verkehrsaufkommen';
    const yearText = `(${state.year})`;

    let dirText = 'Versand & Empfang';
    if (state.direction === 'outbound') dirText = 'Versand';
    else if (state.direction === 'inbound') dirText = 'Empfang';
    else if (state.direction === 'balance') dirText = 'Verkehrssaldo';

    const grpText = (state.selectedGroup && state.selectedGroup !== 'ALL') ? ` – ${NST_GROUPS_7[state.selectedGroup]}` : '';

    const ovEl = document.getElementById('overviewMapTitleText');
    if (ovEl) {
      ovEl.textContent = `${dirText}, ${metricText}${grpText} ${yearText}`;
    }

    const roadEl = document.getElementById('roadMapTitleText');
    if (roadEl) {
      roadEl.textContent = `Straßengüterverkehr (${dirText}), ${metricText}${grpText} ${yearText}`;
    }

    const railEl = document.getElementById('railMapTitleText');
    if (railEl) {
      railEl.textContent = `Schienengüterverkehr (${dirText}), ${metricText}${grpText} ${yearText}`;
    }

    const iwwEl = document.getElementById('iwwMapTitleText');
    if (iwwEl) {
      iwwEl.textContent = `Binnenschifffahrt (${dirText}), ${metricText}${grpText} ${yearText}`;
    }

    const mrtmEl = document.getElementById('maritimeMapTitle');
    if (mrtmEl) {
      const yearPorts = maritimeData?.seaports?.[state.year] || maritimeData?.seaports?.['2024'] || {};
      const isSpecific = Boolean(state.selectedPort && yearPorts[state.selectedPort]);
      const portCount = Object.keys(yearPorts).length;
      const portPrefix = isSpecific ? `Seehafen ${yearPorts[state.selectedPort]?.name} – ` : `Deutsche Seehäfen (${portCount} Standorte) – `;
      mrtmEl.textContent = `${portPrefix}Seegüterumschlag (${dirText})${grpText} ${yearText}`;
    }

    const fcEl = document.getElementById('forecastMapTitleText');
    if (fcEl) {
      const fcScenarioText = (state.forecastScenario === '2019_BASE') ? '(Basisjahr 2019)' : '(Prognose 2040 P1)';
      fcEl.textContent = `${dirText}, ${metricText}${grpText} ${fcScenarioText}`;
    }
  }

  // ============================================================
  // RENDER FLOW SPIDER LINES (WITH ROBUST BI-DIRECTIONAL BINDINGS & RICH HOVER TOOLTIPS)
  // ============================================================
  function renderMapSpiderLines(mapKey, modeFilter = null, groupFilter = 'ALL') {
    const map = maps[mapKey];
    const group = mapLayers[mapKey]?.spiderGroup;
    if (!map || !group) return;
    bindMapHighlightReset(mapKey);

    group.clearLayers();
    mapLayers[mapKey].spiderLookup = {};

    const spiderSec = document.getElementById(`${mapKey}LegendSpiderSection`);

    // Check individual per-map toggle
    const isSpiderEnabled = (mapKey === 'overview' && state.showSpider) ||
                            (mapKey === 'road' && state.showRoadSpider) ||
                            (mapKey === 'rail' && state.showRailSpider) ||
                            (mapKey === 'iww' && state.showIwwSpider);

    if (!isSpiderEnabled || !state.region) {
      if (spiderSec) spiderSec.style.display = 'none';
      return;
    }

    const regMeta = regionsData[state.region];
    if (!regMeta || !regMeta.lat) {
      if (spiderSec) spiderSec.style.display = 'none';
      return;
    }

    const regTopAll = getRegionRelations(state.region);
    const yrTop = regTopAll[state.year] || { outbound_overall: [], inbound_overall: [], by_mode: {} };

    let flows = [];
    if (modeFilter) {
      const modeObj = yrTop.by_mode?.[modeFilter] || { outbound: [], inbound: [], by_group: {} };
      flows = getModeRelations(modeObj, groupFilter, state.direction, modeFilter);
    } else {
      const overviewRes = getOverviewRelations(yrTop, state.selectedGroup, state.direction, regTopAll);
      flows = overviewRes.flows;
    }

    // Filter Binnenverkehr if toggled off
    if (!state.includeBinnen) {
      flows = flows.filter(r => !r.is_binnen && (r.dest_id !== state.region) && (r.origin_id !== state.region));
    }

    // Sort by active metric
    const isTkm = state.metric === 'tkm';
    const flowAmount = row => isTkm ? (row.tkm || 0) : (row.tonnes || 0);
    flows.sort((a, b) => state.direction === 'balance'
      ? Math.abs(flowAmount(b)) - Math.abs(flowAmount(a))
      : flowAmount(b) - flowAmount(a));

    // Compute historical trends for mode flows if in mode detail view
    if (modeFilter && state.direction !== 'balance') {
      computeFlowTrends(flows, modeFilter, state.direction, groupFilter, regTopAll, state.year, isTkm);
    }

    const topFlows = flows.slice(0, state.topX);
    if (topFlows.length === 0) {
      if (spiderSec) spiderSec.style.display = 'none';
      return;
    }

    const originLat = regMeta.lat;
    const originLng = regMeta.lng;

    const cls = getFlowClassification(topFlows, isTkm);

    // Update Spider Line Legend Section
    if (spiderSec) {
      spiderSec.style.display = 'block';
      const minEl = document.getElementById(`spiderLegMin_${mapKey}`);
      const medEl = document.getElementById(`spiderLegMed_${mapKey}`);
      const maxEl = document.getElementById(`spiderLegMax_${mapKey}`);
      const thinLine = document.getElementById(`spiderLineThin_${mapKey}`);
      const medLine = document.getElementById(`spiderLineMed_${mapKey}`);
      const thickLine = document.getElementById(`spiderLineThick_${mapKey}`);

      let repColor = state.direction === 'balance' ? '#16a34a' : '#059669';
      if (state.direction !== 'balance' && modeFilter === 'road') repColor = '#f59e0b';
      else if (state.direction !== 'balance' && modeFilter === 'rail') repColor = '#2563eb';
      else if (state.direction !== 'balance' && modeFilter === 'iww') repColor = '#0d9488';

      [thinLine, medLine, thickLine].forEach(l => { if (l) l.style.backgroundColor = repColor; });

      if (minEl) minEl.textContent = cls.labelThin;
      if (medEl) medEl.textContent = cls.labelMed;
      if (maxEl) maxEl.textContent = cls.labelThick;
    }

    topFlows.forEach(r => {
      const partnerId = r.dest_id || r.origin_id || '';
      if (!partnerId) return;

      const pMeta = fullCentroids[partnerId] || regionsData[partnerId];
      if (!pMeta || !pMeta.lat) return;

      const partnerLat = pMeta.lat;
      const partnerLng = pMeta.lng;

      const flowVal = (isTkm ? r.tkm : r.tonnes) || 0;
      const weight = cls.getWeight(flowVal);
      const radius = cls.getRadius(flowVal);
      
      let color = state.direction === 'balance'
        ? (flowVal >= 0 ? '#16a34a' : '#7c3aed')
        : '#059669'; // Default overview: uniform emerald green
      if (state.direction !== 'balance' && modeFilter === 'road') color = '#f59e0b';
      else if (state.direction !== 'balance' && modeFilter === 'rail') color = '#2563eb';
      else if (state.direction !== 'balance' && modeFilter === 'iww') color = '#0d9488';

      let latlngs;
      if (r.is_binnen || partnerId === state.region) {
        latlngs = [
          [originLat, originLng],
          [originLat + 0.08, originLng + 0.08],
          [originLat + 0.08, originLng - 0.08],
          [originLat, originLng]
        ];
      } else {
        latlngs = [
          [originLat, originLng],
          [partnerLat, partnerLng]
        ];
      }

      const line = L.polyline(latlngs, {
        pane: 'connectionPane',
        className: 'flow-relation-target',
        color: color,
        weight: weight,
        opacity: 0.85,
        smoothFactor: 1.0,
        dashArray: (r.is_binnen || partnerId === state.region) ? '4, 4' : null
      }).addTo(group);

      const marker = L.circleMarker([partnerLat, partnerLng], {
        pane: 'connectionPane',
        className: 'flow-relation-target',
        radius: radius,
        fillColor: color,
        color: '#ffffff',
        weight: 1.5,
        fillOpacity: 0.95
      }).addTo(group);

      mapLayers[mapKey].spiderLookup[partnerId] = {
        line,
        marker,
        originalWeight: weight,
        originalColor: color,
        originalRadius: radius
      };

      const partnerName = pMeta.name || partnerId;
      const isBalance = state.direction === 'balance';
      const displayValue = isTkm ? (r.tkm || 0) / 1e6 : (r.tonnes || 0) / 1e3;
      const valStr = `${isBalance && displayValue > 0 ? '+' : ''}${formatQuantity(displayValue, 1)}`;
      const unitStr = isTkm ? 'Mio. tkm' : 'Tsd. t';

      let dirLabel = 'Güterverbindung (gesamt)';
      if (state.direction === 'inbound') dirLabel = 'Empfang (aus Partnerregion)';
      else if (state.direction === 'outbound') dirLabel = 'Versand (in Partnerregion)';
      else if (isBalance) dirLabel = 'Nettosaldo (Versand − Empfang)';

      let fromToText = '';
      if (state.direction === 'inbound') {
        fromToText = `<div><strong>Quelle:</strong> ${partnerName} (${partnerId})</div><div><strong>Ziel (Auswahl):</strong> ${regMeta.name} (${regMeta.id})</div>`;
      } else if (state.direction === 'outbound') {
        fromToText = `<div><strong>Quelle (Auswahl):</strong> ${regMeta.name} (${regMeta.id})</div><div><strong>Ziel:</strong> ${partnerName} (${partnerId})</div>`;
      } else {
        fromToText = `<div><strong>Verbindung:</strong> ${regMeta.name} &harr; ${partnerName} (${partnerId})</div>`;
      }

      const activeGroupLabel = (groupFilter && groupFilter !== 'ALL') ? (NST_GROUPS_7[groupFilter] || groupFilter) : ((r.group_7 && r.group_7 !== 'ALL') ? (NST_GROUPS_7[r.group_7] || `Gruppe ${r.group_7}`) : 'Alle Güterarten');
      
      let modeText = 'Straßengüterverkehr';
      if (modeFilter === 'rail' || r.mode === 'rail') modeText = 'Schienengüterverkehr';
      else if (modeFilter === 'iww' || r.mode === 'iww') modeText = 'Binnenschifffahrt';
      else if (modeFilter === 'road' || r.mode === 'road') modeText = 'Straßengüterverkehr';
      else if (r.modes_list && r.modes_list.length > 0) {
        modeText = formatModeList(r.modes_list);
      } else if (groupFilter === 'ALL') {
        const invModes = getInvolvedModes(yrTop, partnerId, state.direction, 'ALL');
        modeText = formatModeList(invModes);
      }

      const yoyVal = (r.yoy_pct !== null && r.yoy_pct !== undefined) ? r.yoy_pct : (isTkm ? r.yoy_pct_tkm : r.yoy_pct_tonnes);
      const trendVal = (r.trend_10yr_pct !== null && r.trend_10yr_pct !== undefined) ? r.trend_10yr_pct : (isTkm ? r.trend_10yr_pct_tkm : r.trend_10yr_pct_tonnes);

      const yoyStr = (yoyVal !== null && yoyVal !== undefined)
        ? `<span style="color:${yoyVal >= 0 ? '#16a34a' : '#dc2626'}; font-weight:700;">${yoyVal >= 0 ? '↗ +' : '↘ '}${formatDeNum(yoyVal, 1)} %</span>`
        : '<span style="color:#94a3b8;">--</span>';

      const trendStr = (trendVal !== null && trendVal !== undefined)
        ? `<span style="color:${trendVal >= 0 ? '#16a34a' : '#dc2626'}; font-weight:700;">${trendVal >= 0 ? '↗ +' : '↘ '}${formatDeNum(trendVal, 1)} %</span>`
        : '<span style="color:#94a3b8;">--</span>';

      const outboundValue = isTkm ? (r.outbound_tkm || 0) / 1e6 : (r.outbound_tonnes || 0) / 1e3;
      const inboundValue = isTkm ? (r.inbound_tkm || 0) / 1e6 : (r.inbound_tonnes || 0) / 1e3;
      const balanceStatus = displayValue >= 0 ? 'Versandüberschuss' : 'Empfangsüberschuss';
      const balanceDetailHtml = isBalance ? `
        <div style="margin-top:4px; padding-top:4px; border-top:1px solid #f1f5f9;">
          <div><strong>Versand:</strong> ${formatQuantity(outboundValue, 1)} ${unitStr}</div>
          <div><strong>Empfang:</strong> ${formatQuantity(inboundValue, 1)} ${unitStr}</div>
          <div style="font-weight:800; color:${displayValue >= 0 ? '#16a34a' : '#7c3aed'};"><strong>Saldo:</strong> ${valStr} ${unitStr} · ${balanceStatus}</div>
        </div>` : '';

      const popupHtml = `
        <div style="font-size:0.83rem; line-height:1.5; min-width:220px; font-family:'Inter', sans-serif;">
          <div style="font-size:0.68rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:4px; border-bottom:1px solid #e2e8f0; padding-bottom:3px;">
            Bezugsjahr: ${state.year} • ${dirLabel}
          </div>
          ${fromToText}
          <div style="margin-top:4px;"><strong>Güterart:</strong> ${activeGroupLabel}</div>
          <div><strong>Verkehrsträger:</strong> ${modeText}</div>
          <div style="margin-top:4px; font-size:0.9rem; font-weight:800; color:#0f172a;">
            ${isBalance ? 'Nettosaldo' : (isTkm ? 'Verkehrsleistung' : 'Beförderungsmenge')}: ${valStr} ${unitStr}
          </div>
          ${balanceDetailHtml}
          ${isBalance
            ? '<div style="font-size:0.75rem; color:#64748b; margin-top:4px;">Für Salden wird kein prozentualer Zeitvergleich ausgewiesen.</div>'
            : `<div style="font-size:0.75rem; color:#475569; margin-top:4px; border-top:1px solid #f1f5f9; padding-top:3px;">Δ Vorjahr: ${yoyStr} &nbsp;|&nbsp; Δ ggü. 2016: ${trendStr}</div>`}
        </div>
      `;

      line.bindTooltip(popupHtml, { sticky: true, opacity: 0.98 });
      marker.bindTooltip(popupHtml, { sticky: true, opacity: 0.98 });

      // Map-to-Table hover bindings
      line.on('mouseover', event => {
        openActiveRelationTooltip(mapKey, line, event);
        setHighlight(mapKey, partnerId);
      });
      line.on('mouseout', () => {
        closeActiveRelationTooltip(mapKey);
        clearAllHighlights(mapKey);
      });
      marker.on('mouseover', event => {
        openActiveRelationTooltip(mapKey, marker, event);
        setHighlight(mapKey, partnerId);
      });
      marker.on('mouseout', () => {
        closeActiveRelationTooltip(mapKey);
        clearAllHighlights(mapKey);
      });
    });
  }

  // Master Render
  function renderAll() {
    updateMapTitles();
    updateRelationTableTitles();
    updateTableHistoricalHeaders();
    const tabId = state.activeTab;
    if (tabId === 'tab-forecast') renderForecastTab();
    else if (tabId === 'tab-intermodal') renderIntermodalTab();
    else if (tabId === 'tab-maritime') renderMaritimeTab();
    else if (tabId === 'tab-overview') renderOverviewTab();
    else if (tabId?.startsWith('tab-')) renderModeDetailTab(tabId.replace('tab-', ''));
    annotateMissingComparisons();
  }

  function updateRelationTableTitles() {
    const regionName = state.region ? (regionsData[state.region]?.name || state.region) : 'Region auswählen';
    const title = state.direction === 'balance'
      ? `Top ${state.topX} Nettobeziehungen: ${regionName}`
      : `Top ${state.topX} Relationen: ${regionName}`;
    ['overviewRelationsTitle', 'roadRelationsTitle', 'railRelationsTitle', 'iwwRelationsTitle', 'intermodalRelationsTitle', 'forecastRelationsTitle']
      .forEach(id => setText(id, title));

    const portName = state.selectedPort
      ? (maritimeData?.seaports?.[state.year]?.[state.selectedPort]?.name || state.selectedPort)
      : null;
    setText('maritimePartnersTitle', portName ? `Top ${state.topX} Relationen: ${portName}` : 'Top Relationen: Hafen auswählen');
  }

  function annotateMissingComparisons(root = document) {
    const cells = [];
    if (root instanceof Element && root.matches('.data-table td')) cells.push(root);
    if (root.querySelectorAll) cells.push(...root.querySelectorAll('.data-table td'));
    cells.forEach(cell => {
      if (cell.textContent.trim() === '--') {
        cell.title = 'Kein Vergleichswert für das betreffende Vorjahr bzw. Basisjahr vorhanden.';
        cell.setAttribute('aria-label', 'Kein Vergleichswert vorhanden');
        cell.classList.add('missing-comparison');
      } else {
        cell.removeAttribute('aria-label');
        cell.classList.remove('missing-comparison');
      }
    });
  }

  function observeMissingComparisons() {
    const observer = new MutationObserver(records => {
      records.forEach(record => record.addedNodes.forEach(node => {
        if (node.nodeType === Node.ELEMENT_NODE) annotateMissingComparisons(node);
      }));
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  // ============================================================
  // TAB 1: REGIONALE ÜBERSICHT
  // ============================================================
  function renderOverviewTab() {
    const regYears = getActiveRegionSummary();
    const curr = regYears[state.year] || { total_tonnes: 0, total_tkm: 0, modes_tonnes: {}, modes_tkm: {}, directions_tonnes: {}, groups_7_tonnes: {}, by_mode_groups: {} };

    const isTkm = state.metric === 'tkm';
    const metricLabel = isTkm ? 'Mrd. tkm' : 'Mio. t';
    const divisor = isTkm ? 1e9 : 1e6;
    const dir = state.direction || 'all';
    const getGroupValue = (record, group, mode) => {
      const groupCube = mode
        ? (isTkm ? record.by_mode_groups_tkm : record.by_mode_groups)?.[mode]
        : (isTkm ? record.groups_7_tkm : record.groups_7_tonnes);
      if (!groupCube) return 0;
      if (dir === 'balance') return (groupCube.outbound?.[group] || 0) - (groupCube.inbound?.[group] || 0);
      return groupCube[dir]?.[group] ?? groupCube.all?.[group] ?? groupCube[group] ?? 0;
    };
    const getOverallValue = (record, mode = null) => {
      if (!record) return 0;
      if (mode) {
        if (dir === 'all') return record[isTkm ? 'modes_tkm' : 'modes_tonnes']?.[mode] || 0;
        const byDirection = record[isTkm ? 'modes_direction_tkm' : 'modes_direction_tonnes']?.[mode] || {};
        if (dir === 'balance') return (byDirection.outbound || 0) - (byDirection.inbound || 0);
        return byDirection[dir] || 0;
      }
      if (dir === 'all') return record[isTkm ? 'total_tkm' : 'total_tonnes'] || 0;
      const totalsByDirection = record[isTkm ? 'directions_tkm' : 'directions_tonnes'] || {};
      if (dir === 'balance') return (totalsByDirection.outbound || 0) - (totalsByDirection.inbound || 0);
      return totalsByDirection[dir] || 0;
    };

    let totBase, roadValNum, railValNum, iwwValNum;
    if (state.selectedGroup && state.selectedGroup !== 'ALL') {
      const grp = state.selectedGroup;
      totBase = getGroupValue(curr, grp);
      const roadGrp = getGroupValue(curr, grp, 'road');
      const railGrp = getGroupValue(curr, grp, 'rail');
      const iwwGrp = getGroupValue(curr, grp, 'iww');
      roadValNum = roadGrp;
      railValNum = railGrp;
      iwwValNum = iwwGrp;
    } else {
      totBase = getOverallValue(curr);
      roadValNum = getOverallValue(curr, 'road');
      railValNum = getOverallValue(curr, 'rail');
      iwwValNum = getOverallValue(curr, 'iww');
    }

    const totMetric = formatDeNum(totBase / divisor, 2);
    const roadVal = formatDeNum(roadValNum / divisor, 2);
    const railVal = formatDeNum(railValNum / divisor, 2);
    const iwwVal = formatDeNum(iwwValNum / divisor, 2);

    const prevYearNum = parseInt(state.year, 10) - 1;
    const prevYearStr = String(prevYearNum);
    const prev = regYears[prevYearStr] || null;

    let totBasePrev = null, roadValNumPrev = null, railValNumPrev = null, iwwValNumPrev = null;
    if (prev) {
      if (state.selectedGroup && state.selectedGroup !== 'ALL') {
        const grp = state.selectedGroup;
        totBasePrev = getGroupValue(prev, grp);
        roadValNumPrev = getGroupValue(prev, grp, 'road');
        railValNumPrev = getGroupValue(prev, grp, 'rail');
        iwwValNumPrev = getGroupValue(prev, grp, 'iww');
      } else {
        totBasePrev = getOverallValue(prev);
        roadValNumPrev = getOverallValue(prev, 'road');
        railValNumPrev = getOverallValue(prev, 'rail');
        iwwValNumPrev = getOverallValue(prev, 'iww');
      }
    }

    const formatYoYBadge = (cVal, pVal) => {
      if (dir === 'balance') {
        return '<span style="color:#64748b; font-size:0.75rem; font-weight:600;">Saldo ohne Vorjahresvergleich</span>';
      }
      if (pVal === null || pVal === undefined || pVal <= 0 || cVal === null || cVal === undefined) {
        return `<span style="color:#64748b; font-size:0.75rem; font-weight:600;">-- ggü. ${prevYearNum}</span>`;
      }
      const pct = ((cVal - pVal) / pVal) * 100;
      if (pct > 0.05) {
        return `<span style="color:#16a34a; font-size:0.75rem; font-weight:700;">↗ +${formatDeNum(pct, 1)} % ggü. ${prevYearNum}</span>`;
      } else if (pct < -0.05) {
        return `<span style="color:#dc2626; font-size:0.75rem; font-weight:700;">↘ ${formatDeNum(pct, 1)} % ggü. ${prevYearNum}</span>`;
      } else {
        return `<span style="color:#64748b; font-size:0.75rem; font-weight:600;">→ 0,0 % ggü. ${prevYearNum}</span>`;
      }
    };

    const setTxt = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
    const setHtml = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };

    const roadUnavailable = state.year === '2025';
    const nationalGroupWithoutTransit = !state.region && state.selectedGroup && state.selectedGroup !== 'ALL';
    const directionSuffix = dir === 'balance' ? ' (Saldo)' : dir === 'outbound' ? ' (Versand)' : dir === 'inbound' ? ' (Empfang)' : '';
    const formatKpiValue = value => `${dir === 'balance' && value > 0 ? '+' : ''}${formatDeNum(value / divisor, 2)} ${metricLabel}`;
    const scopeSuffix = nationalGroupWithoutTransit ? ' ohne Transit' : '';
    setTxt('kpiTotalTitle', `${roadUnavailable ? 'Aufkommen ohne Straße' : 'Gesamtaufkommen'}${scopeSuffix}${directionSuffix}`);
    setTxt('kpiRoadTitle', `${roadUnavailable ? 'Straße (LKW) · NV' : 'Straße (LKW)'}${scopeSuffix}${directionSuffix}`);
    setTxt('kpiTotalTonnes', formatKpiValue(totBase));
    // In 2025, the first KPI is explicitly the comparable total without road.
    // Its previous-year reference must therefore exclude road traffic as well.
    const comparableTotalPrev = roadUnavailable && totBasePrev !== null
      ? (railValNumPrev || 0) + (iwwValNumPrev || 0)
      : totBasePrev;
    setHtml('kpiTotalSub', formatYoYBadge(totBase, comparableTotalPrev));
    setTxt('kpiRoadTonnes', roadUnavailable ? 'NV' : formatKpiValue(roadValNum));
    setHtml('kpiRoadShare', roadUnavailable ? '<span style="color:#854d0e; font-weight:700;">Daten noch nicht vorliegend</span>' : formatYoYBadge(roadValNum, roadValNumPrev));
    setTxt('kpiRailTitle', `Schiene (Bahn)${scopeSuffix}${directionSuffix}`);
    setTxt('kpiRailTonnes', formatKpiValue(railValNum));
    setHtml('kpiRailShare', formatYoYBadge(railValNum, railValNumPrev));
    setTxt('kpiIwwTitle', `Wasserstraße (Binnenschiff)${scopeSuffix}${directionSuffix}`);
    setTxt('kpiIwwTonnes', formatKpiValue(iwwValNum));
    setHtml('kpiIwwShare', formatYoYBadge(iwwValNum, iwwValNumPrev));

    renderTopRelationsTable();
    updateLeafletMap('overview');
    renderModalSplitChart();
    renderCommodityChart();
  }

  // The profile uses a stable scope (all goods, inbound plus outbound traffic)
  // while taking its reference year from the global year selector whenever a
  // complete all-mode snapshot is available.
  async function prepareSteckbriefModal() {
    const bodyEl = document.getElementById('steckbriefModalBody');
    if (bodyEl) {
      bodyEl.innerHTML = '<div class="steckbrief-loading" role="status">Steckbrief wird aus den Regionaldaten erstellt …</div>';
    }
    await Promise.all([
      ensureSummaryData(),
      ensureModuleData('intermodal'),
      ensureModuleData('forecast'),
      state.region ? loadRegionRelations(state.region) : Promise.resolve()
    ]);
    renderSteckbriefModal();
  }

  function escapeProfileHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, char => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[char]));
  }

  function getProfileGroups(record) {
    const groups = record?.groups_7_tonnes || {};
    return groups.all || groups;
  }

  function getProfileRelations(regionId, year, regionName) {
    if (!regionId) return [];
    const yearData = getRegionRelations(regionId)?.[String(year)] || {};
    const merged = new Map();
    const addRows = (rows, direction) => {
      (rows || []).forEach(row => {
        const partnerId = direction === 'outbound' ? row.dest_id : row.origin_id;
        if (!partnerId) return;
        const current = merged.get(partnerId) || {
          id: partnerId,
          name: direction === 'outbound' ? row.dest_name : row.origin_name,
          tonnes: 0,
          isBinnen: false
        };
        current.tonnes += Number(row.tonnes || 0);
        current.isBinnen = current.isBinnen || Boolean(row.is_binnen) || partnerId === regionId;
        if (!current.name) current.name = direction === 'outbound' ? row.dest_name : row.origin_name;
        merged.set(partnerId, current);
      });
    };
    addRows(yearData.outbound_overall, 'outbound');
    addRows(yearData.inbound_overall, 'inbound');
    return [...merged.values()]
      .filter(row => row.tonnes > 0)
      .map(row => ({
        ...row,
        name: row.isBinnen ? `Binnenverkehr in ${regionName}` : (row.name || regionsData[row.id]?.name || row.id)
      }))
      .sort((a, b) => b.tonnes - a.tonnes)
      .slice(0, 3);
  }

  function getProfileForecastRelations(regionId) {
    if (!regionId) return [];
    const rows = forecastData?.scenarios?.['2040_P1']?.regions?.[regionId]?.relations_overall?.all || [];
    return [...rows]
      .filter(row => Number(row.tonnes || 0) > 0)
      .sort((a, b) => Number(b.tonnes || 0) - Number(a.tonnes || 0))
      .slice(0, 3)
      .map(row => {
        const partnerId = row.partner_id || row.dest_id || row.orig_id;
        return {
          id: partnerId,
          name: row.partner_name || regionsData[partnerId]?.name || fullCentroids[partnerId]?.name || centroidsVp2040[partnerId]?.name || partnerId,
          tonnes: Number(row.tonnes || 0),
          isBinnen: Boolean(row.is_binnen) || partnerId === regionId
        };
      });
  }

  function profileChange(current, reference) {
    if (!(reference > 0) || !Number.isFinite(current)) return null;
    return (current - reference) / reference * 100;
  }

  function profileChangeText(change) {
    if (change === null) return 'kein Vergleichswert';
    if (change > 2) return `+${formatDeNum(change, 1)} %`;
    if (change < -2) return `${formatDeNum(change, 1)} %`;
    return 'nahezu stabil';
  }

  function profileChangeClass(change) {
    if (change === null || Math.abs(change) <= 2) return 'is-neutral';
    return change > 0 ? 'is-positive' : 'is-negative';
  }

  // The two KV source markets are intentionally kept separate. A combined
  // value would not be methodologically sound because rail load units and
  // inland-waterway containers may refer to the same transport chain.
  function getProfileIntermodalMetric(year, scopeId, mode, category, metric = 'tonnes') {
    if (!intermodalData) return null;
    const directional = intermodalData?.scoped_metrics_by_year?.[String(year)]?.[scopeId]?.[mode]?.[category];
    if (!directional) return 0;
    const read = direction => Number(directional?.[direction]?.[metric] || 0);
    if (scopeId === 'DE' && directional.all) return read('all');
    return read('outbound') + read('inbound') + read('binnen');
  }

  // The profile always uses the all-goods, all-directions volume for the P1
  // outlook. It therefore remains comparable across regions and independent
  // of the filters active in the individual analysis modules.
  function getProfileForecastOutlook(regionId) {
    const scenarios = forecastData?.scenarios;
    const targetScenario = scenarios?.['2040_P1'];
    const baselineScenario = scenarios?.['2019_BASE'];
    const target = regionId ? targetScenario?.regions?.[regionId] : targetScenario?.national;
    const baseline = regionId ? baselineScenario?.regions?.[regionId] : baselineScenario?.national;
    const asFiniteNumber = value => typeof value === 'number' && Number.isFinite(value) ? value : null;
    const getTotal = record => asFiniteNumber(regionId
      ? (record?.directions_tonnes?.all ?? record?.tonnes?.total)
      : record?.total_tonnes);
    const getMode = (record, mode) => asFiniteNumber(regionId
      ? (record?.modes_tonnes?.[mode] ?? record?.tonnes?.[mode])
      : record?.modes?.[mode]?.tonnes);
    const total = getTotal(target);
    const baselineTotal = getTotal(baseline);
    if (!(total > 0) || !(baselineTotal > 0)) return null;

    const modeLabels = { road: 'Straße', rail: 'Schiene', iww: 'Binnenschiff' };
    const modeRows = Object.keys(modeLabels)
      .map(mode => {
        const value = getMode(target, mode);
        const baselineValue = getMode(baseline, mode);
        return value === null || baselineValue === null
          ? null
          : { mode, label: modeLabels[mode], value, baselineValue, change: value - baselineValue };
      })
      .filter(Boolean);

    return {
      total,
      baselineTotal,
      totalChange: (total - baselineTotal) / baselineTotal * 100,
      strongestModeChange: [...modeRows].sort((a, b) => Math.abs(b.change) - Math.abs(a.change))[0] || null
    };
  }

  function renderProfileModalSplitTrend(regYears, fromYear, toYear, formatMio) {
    const years = Object.keys(regYears || {})
      .map(Number)
      .filter(year => year >= fromYear && year <= toYear && Number(regYears[String(year)]?.total_tonnes || 0) > 0)
      .sort((a, b) => a - b);
    if (years.length < 2) {
      return '<div class="steckbrief-empty-note">Für den Zeitverlauf liegen nicht ausreichend vergleichbare Jahreswerte vor.</div>';
    }

    const modes = [
      { key: 'road', label: 'Straße', color: '#d88925' },
      { key: 'rail', label: 'Schiene', color: '#3973c8' },
      { key: 'iww', label: 'Binnenschiff', color: '#4c8d89' }
    ];
    const latestModeYears = Object.fromEntries(modes.map(({ key }) => [key, getLatestAvailableModeYear(key)]));
    const values = Object.fromEntries(modes.map(({ key }) => [key, years.map(year => {
      if (latestModeYears[key] === null || year > latestModeYears[key]) return null;
      const value = Number(regYears[String(year)]?.modes_tonnes?.[key]);
      return Number.isFinite(value) ? value / 1e6 : null;
    })]));
    const rawMax = Math.max(1, ...Object.values(values).flat().filter(Number.isFinite));
    const order = Math.pow(10, Math.floor(Math.log10(rawMax)));
    const maxValue = Math.ceil((rawMax / order) * 2) / 2 * order;
    const formatAxis = value => `${formatDeNum(value, value < 10 ? 1 : 0)} Mio. t`;
    const axisLabels = [0, 0.5, 1].map(factor => formatAxis(maxValue * factor));
    const longestAxisLabel = Math.max(...axisLabels.map(label => label.length));
    const width = 720;
    const height = 212;
    const plot = {
      left: Math.min(112, Math.max(76, Math.ceil(longestAxisLabel * 6.2 + 12))),
      right: 16,
      top: 14,
      bottom: 33
    };
    const plotWidth = width - plot.left - plot.right;
    const plotHeight = height - plot.top - plot.bottom;
    const x = index => plot.left + (years.length === 1 ? 0 : index / (years.length - 1) * plotWidth);
    const y = value => plot.top + (1 - value / maxValue) * plotHeight;
    const grid = [0, 0.5, 1].map((factor, index) => {
      const value = maxValue * factor;
      const yy = y(value);
      return `<line x1="${plot.left}" y1="${yy.toFixed(1)}" x2="${width - plot.right}" y2="${yy.toFixed(1)}" class="steckbrief-trend-gridline"></line><text x="${plot.left - 8}" y="${(yy + 3).toFixed(1)}" class="steckbrief-trend-axis-label" text-anchor="end">${axisLabels[index]}</text>`;
    }).join('');
    const yearLabels = years.map((year, index) => {
      const showLabel = years.length <= 7 || index === 0 || index === years.length - 1 || index % 2 === 0;
      return showLabel
        ? `<text x="${x(index).toFixed(1)}" y="${height - 10}" class="steckbrief-trend-axis-label" text-anchor="middle">${year}</text>`
        : '';
    }).join('');
    const lines = modes.map(({ key, label, color }) => {
      const segments = [];
      let currentSegment = [];
      values[key].forEach((value, index) => {
        if (!Number.isFinite(value)) {
          if (currentSegment.length) segments.push(currentSegment);
          currentSegment = [];
          return;
        }
        currentSegment.push(`${x(index).toFixed(1)},${y(value).toFixed(1)}`);
      });
      if (currentSegment.length) segments.push(currentSegment);
      const polylines = segments.map(points => `<polyline points="${points.join(' ')}" fill="none" stroke="${color}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><title>${label}</title></polyline>`).join('');
      const dots = values[key]
        .map((value, index) => Number.isFinite(value) ? `<circle cx="${x(index).toFixed(1)}" cy="${y(value).toFixed(1)}" r="2.9" fill="${color}"></circle>` : '')
        .join('');
      return `${polylines}${dots}`;
    }).join('');
    const latestValues = modes.map(({ key, label, color }) => {
      const latestIndex = values[key].map((value, index) => Number.isFinite(value) ? index : -1).filter(index => index >= 0).at(-1);
      if (latestIndex === undefined) return `<span><i style="background:${color}"></i>${label} –</span>`;
      const suffix = years[latestIndex] === years.at(-1) ? '' : ` · ${years[latestIndex]}`;
      return `<span><i style="background:${color}"></i>${label} ${formatMio(values[key][latestIndex] * 1e6)}${suffix}</span>`;
    }).join('');

    return `
      <div class="steckbrief-trend-legend" style="--steckbrief-trend-axis-left:${plot.left}px">${latestValues}</div>
      <svg class="steckbrief-trend-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="Zeitverlauf der Beförderungsmenge nach Verkehrsträgern von ${years[0]} bis ${years.at(-1)}">
        ${grid}
        <line x1="${plot.left}" y1="${height - plot.bottom}" x2="${width - plot.right}" y2="${height - plot.bottom}" class="steckbrief-trend-axis"></line>
        ${yearLabels}
        ${lines}
      </svg>`;
  }

  // Render a fact-based regional profile.  The language is generated only
  // from transparent thresholds and the displayed values; no text is stored
  // per region and no AI service is used.
  function renderSteckbriefModal() {
    const isNational = !state.region;
    const regMeta = isNational
      ? { name: 'Deutschland', id: 'DE' }
      : (regionsData[state.region] || { name: state.region, id: state.region });
    const regYears = getActiveRegionSummary();
    const profileYear = getProfileYear(regYears);
    const current = regYears[profileYear] || {};
    const total = Number(current.total_tonnes || 0);
    const profileYears = Object.keys(regYears || {})
      .map(Number)
      .filter(year => Number(regYears[String(year)]?.total_tonnes || 0) > 0)
      .sort((a, b) => a - b);
    const baseYear = profileYears.find(year => year >= 2016) || profileYears[0];
    const previousYear = profileYears.filter(year => year < Number(profileYear)).at(-1);
    const trendStartYear = baseYear || profileYears[0];
    const trendEndYear = Math.max(
      Number(profileYear),
      ...['road', 'rail', 'iww'].map(getLatestAvailableModeYear).filter(Number.isFinite)
    );
    const base = baseYear ? regYears[String(baseYear)] : null;
    const previous = previousYear ? regYears[String(previousYear)] : null;
    const totalChange = profileChange(total, Number(base?.total_tonnes || 0));
    const previousChange = profileChange(total, Number(previous?.total_tonnes || 0));
    const modes = Object.fromEntries(['road', 'rail', 'iww'].map(mode => [mode, Number(current.modes_tonnes?.[mode] || 0)]));
    const totalModes = Object.values(modes).reduce((sum, value) => sum + value, 0);
    const national = nationalSummaryData[profileYear] || {};
    const nationalModes = national.modes_tonnes || {};
    const nationalModeTotal = Object.values(nationalModes).reduce((sum, value) => sum + Number(value || 0), 0);
    const modeDefinitions = {
      road: { label: 'Straße', css: 'road' },
      rail: { label: 'Schiene', css: 'rail' },
      iww: { label: 'Binnenschiff', css: 'iww' }
    };
    const modeRows = Object.entries(modes).map(([mode, value]) => {
      const share = totalModes > 0 ? value / totalModes * 100 : 0;
      const nationalShare = nationalModeTotal > 0 ? Number(nationalModes[mode] || 0) / nationalModeTotal * 100 : null;
      return { mode, value, share, nationalShare, ...modeDefinitions[mode] };
    });
    const leadingMode = [...modeRows].sort((a, b) => b.share - a.share)[0];
    const modeDifference = leadingMode?.nationalShare === null || leadingMode?.nationalShare === undefined
      ? null
      : leadingMode.share - leadingMode.nationalShare;

    const groups = getProfileGroups(current);
    const nationalGroups = getProfileGroups(national);
    const groupTotal = Object.values(groups).reduce((sum, value) => sum + Number(value || 0), 0);
    const nationalGroupTotal = Object.values(nationalGroups).reduce((sum, value) => sum + Number(value || 0), 0);
    const groupRows = Object.entries(groups)
      .map(([id, value]) => {
        const localValue = Number(value || 0);
        const share = groupTotal > 0 ? localValue / groupTotal * 100 : 0;
        const nationalShare = nationalGroupTotal > 0 ? Number(nationalGroups[id] || 0) / nationalGroupTotal * 100 : null;
        return { id, value: localValue, share, nationalShare, label: NST_GROUPS_7[id] || `Gütergruppe ${id}` };
      })
      .filter(row => row.value > 0)
      .sort((a, b) => b.value - a.value);
    const topGroup = groupRows[0] || null;
    const groupDifference = topGroup?.nationalShare === null || topGroup?.nationalShare === undefined
      ? null
      : topGroup.share - topGroup.nationalShare;
    const isPronouncedGroup = Boolean(topGroup && topGroup.share >= 20 && groupDifference !== null && groupDifference >= 7);
    const inbound = Number(current.directions_tonnes?.inbound || 0);
    const outbound = Number(current.directions_tonnes?.outbound || 0);
    const balance = outbound - inbound;
    const balanceShare = total > 0 ? Math.abs(balance) / total * 100 : 0;
    const relations = getProfileRelations(state.region, profileYear, regMeta.name);
    const formatMio = value => `${formatDeNum(value / 1e6, 1)} Mio. t`;
    const formatShare = value => Number.isFinite(value) ? `${formatDeNum(value, 1)} %` : '–';
    const formatSignedMio = value => `${value > 0 ? '+' : ''}${formatMio(value)}`;
    const forecastOutlook = getProfileForecastOutlook(isNational ? null : state.region);
    const forecastRelations = getProfileForecastRelations(isNational ? null : state.region);
    const forecastChangeText = forecastOutlook
      ? `${forecastOutlook.totalChange >= 0 ? '+' : ''}${formatDeNum(forecastOutlook.totalChange, 1)} %`
      : '–';
    const forecastSentence = !forecastOutlook
      ? ''
      : forecastOutlook.totalChange >= 0
        ? `Für das gesamte Güteraufkommen im Landverkehr (Straße, Schiene und Binnenschiff) wird im Prognosefall P1 bis 2040 gegenüber 2019 ein Anstieg um ${formatDeNum(forecastOutlook.totalChange, 1)} % erwartet.`
        : `Für das gesamte Güteraufkommen im Landverkehr (Straße, Schiene und Binnenschiff) wird im Prognosefall P1 bis 2040 gegenüber 2019 ein Rückgang um ${formatDeNum(Math.abs(forecastOutlook.totalChange), 1)} % erwartet.`;
    const profileScopeId = isNational ? 'DE' : state.region;
    const kvRows = [
      {
        label: 'KV auf der Schiene',
        totalLabel: 'Schienengüterverkehrs',
        css: 'rail',
        amount: getProfileIntermodalMetric(profileYear, profileScopeId, 'rail', 'intermodal_load_units'),
        total: getProfileIntermodalMetric(profileYear, profileScopeId, 'rail', 'total')
      },
      {
        label: 'Containerisierter KV in der Binnenschifffahrt',
        totalLabel: 'Binnenschiffsverkehrs',
        css: 'iww',
        amount: getProfileIntermodalMetric(profileYear, profileScopeId, 'iww', 'containerised_transport'),
        total: getProfileIntermodalMetric(profileYear, profileScopeId, 'iww', 'total')
      }
    ].map(row => ({
      ...row,
      share: row.amount !== null && row.total > 0 ? row.amount / row.total * 100 : null
    }));
    const hasKvData = kvRows.some(row => row.amount !== null || row.total !== null);
    const hasKvVolume = kvRows.some(row => Number(row.amount || 0) > 0);
    const kvSectionHtml = !hasKvData
      ? ''
      : !hasKvVolume
        ? `
          <section class="steckbrief-section steckbrief-kv-section">
            <div class="steckbrief-section-heading"><span>Kombinierter Verkehr</span></div>
            <p class="steckbrief-section-text">Für den ausgewählten Raum ist im Profiljahr weder Schienen-KV noch containerisierter KV in der Binnenschifffahrt ausgewiesen.</p>
          </section>`
        : `
        <section class="steckbrief-section steckbrief-kv-section">
          <div class="steckbrief-section-heading"><span>Kombinierter Verkehr</span></div>
          <p class="steckbrief-section-text">Schienen-KV (Ladeeinheiten) und containerisierter Verkehr in der Binnenschifffahrt werden getrennt ausgewiesen; sie werden nicht zu einem Gesamtwert addiert.</p>
          <div class="steckbrief-kv-grid">${kvRows.map(row => {
            const hasAmount = row.amount !== null;
            const shareText = row.share === null
              ? (hasAmount ? 'keine Bezugsmenge ausgewiesen' : 'nicht ausgewiesen')
              : `${formatShare(row.share)} des ${row.totalLabel}`;
            return `<div class="steckbrief-kv-card ${row.css}"><span>${row.label}</span><strong>${hasAmount ? formatMio(row.amount) : '–'}</strong><small>${shareText}</small></div>`;
          }).join('')}</div>
        </section>`;
    const modalSplitTrendHtml = renderProfileModalSplitTrend(regYears, trendStartYear, trendEndYear, formatMio);
    const forecastSectionHtml = !forecastOutlook
      ? ''
      : `
        <section class="steckbrief-section steckbrief-forecast-section">
          <div class="steckbrief-section-heading"><span>Ausblick bis 2040</span><small>Basisprognose P1 · Vergleich 2019–2040</small></div>
          <div class="steckbrief-forecast-grid">
            <div class="steckbrief-forecast-card"><span>Aufkommen 2040</span><strong>${formatMio(forecastOutlook.total)}</strong><small>Landverkehr im Prognosefall P1</small></div>
            <div class="steckbrief-forecast-card"><span>Entwicklung ggü. 2019</span><strong class="${profileChangeClass(forecastOutlook.totalChange)}">${forecastChangeText}</strong><small>${forecastOutlook.totalChange >= 0 ? 'Zunahme' : 'Rückgang'} des Aufkommens</small></div>
            ${forecastOutlook.strongestModeChange ? `<div class="steckbrief-forecast-card"><span>Größte absolute Veränderung</span><strong>${forecastOutlook.strongestModeChange.label}</strong><small>${formatSignedMio(forecastOutlook.strongestModeChange.change)} gegenüber 2019</small></div>` : ''}
          </div>
          ${forecastRelations.length ? `<div class="steckbrief-section-heading"><span>Stärkste prognostizierte Beziehungen 2040</span><small>Top 3 · alle Güter · beide Richtungen</small></div><div class="steckbrief-relation-table-wrap"><table class="steckbrief-relation-table"><thead><tr><th>Beziehung</th><th>Menge</th></tr></thead><tbody>${forecastRelations.map((relation, index) => `<tr><td><span class="steckbrief-rank">${index + 1}</span><strong>${escapeProfileHtml(relation.name)}</strong>${relation.isBinnen ? '<span class="steckbrief-badge">Binnenverkehr</span>' : ''}</td><td>${formatMio(relation.tonnes)}</td></tr>`).join('')}</tbody></table></div>` : ''}
        </section>`;

    const titleEl = document.getElementById('steckbriefModalTitle');
    const codeEl = document.getElementById('steckbriefModalCode');
    const bodyEl = document.getElementById('steckbriefModalBody');
    if (titleEl) titleEl.textContent = `${regMeta.name} · ${profileYear}`;
    if (codeEl) codeEl.textContent = isNational ? 'Nationaler Überblick · DE' : `NUTS-3: ${regMeta.id}`;
    if (!bodyEl) return;
    bodyEl.scrollTop = 0;

    if (!(total > 0)) {
      bodyEl.innerHTML = `
        <section class="steckbrief-empty-state">
          <h4>Keine vergleichbare Profilbasis verfügbar</h4>
          <p>Für ${escapeProfileHtml(regMeta.name)} liegen derzeit keine zusammenführbaren Werte für Straße, Schiene und Binnenschiff vor.</p>
        </section>`;
      return;
    }

    const trendSentence = totalChange === null
      ? ''
      : totalChange > 2
        ? `Seit ${baseYear} ist das Güteraufkommen um ${formatDeNum(totalChange, 1)} % gestiegen.`
        : totalChange < -2
          ? `Seit ${baseYear} ist das Güteraufkommen um ${formatDeNum(Math.abs(totalChange), 1)} % gesunken.`
          : `Seit ${baseYear} bewegt sich das Güteraufkommen auf ähnlichem Niveau.`;
    const modeSentence = modeDifference !== null && Math.abs(modeDifference) >= 5
      ? `Der Anteil ${leadingMode.label === 'Straße' ? 'der Straße' : `der ${leadingMode.label}`} liegt ${formatDeNum(Math.abs(modeDifference), 1)} Prozentpunkte ${modeDifference > 0 ? 'über' : 'unter'} dem Bundeswert.`
      : '';
    const balanceSentence = balanceShare >= 5
      ? `Der Raum weist einen ${balance > 0 ? 'Versand' : 'Empfang'}süberschuss von ${formatMio(Math.abs(balance))} auf.`
      : '';
    const goodsSentence = !topGroup
      ? 'Für die Güterstruktur liegt keine auswertbare Aufschlüsselung vor.'
      : isPronouncedGroup
        ? `${topGroup.label} prägen die Güterstruktur mit ${formatShare(topGroup.share)}; das sind ${formatDeNum(groupDifference, 1)} Prozentpunkte mehr als im Bundesvergleich.`
        : `${topGroup.label} sind mit ${formatShare(topGroup.share)} die größte ausgewiesene Gütergruppe.`;
    const relationHtml = !state.region
      ? '<div class="steckbrief-empty-note">Für Deutschland wird keine Rangfolge regionaler Partner ausgewiesen. Wählen Sie einen Kreis oder eine kreisfreie Stadt, um die drei stärksten Beziehungen zu sehen.</div>'
      : relations.length === 0
        ? '<div class="steckbrief-empty-note">Für das Profiljahr liegen keine auswertbaren regionalen Beziehungen vor.</div>'
        : `<div class="steckbrief-relation-table-wrap"><table class="steckbrief-relation-table"><thead><tr><th>Beziehung</th><th>Menge</th></tr></thead><tbody>${relations.map((relation, index) => `
          <tr><td><span class="steckbrief-rank">${index + 1}</span><strong>${escapeProfileHtml(relation.name)}</strong>${relation.isBinnen ? '<span class="steckbrief-badge">Binnenverkehr</span>' : ''}</td><td>${formatMio(relation.tonnes)}</td></tr>`).join('')}</tbody></table></div>`;
    const milestones = [...new Set([baseYear, Math.max(baseYear || 0, Number(profileYear) - 4), previousYear, Number(profileYear)])]
      .filter(year => year && regYears[String(year)] && Number(regYears[String(year)].total_tonnes || 0) > 0)
      .sort((a, b) => a - b)
      .map(year => `<div class="steckbrief-timeline-item${year === Number(profileYear) ? ' is-current' : ''}"><span>${year}</span><strong>${formatMio(Number(regYears[String(year)].total_tonnes || 0))}</strong></div>`)
      .join('');

    bodyEl.innerHTML = `
      <article class="steckbrief-report">
        <div class="steckbrief-context">Alle Güterarten · Versand und Empfang · Beförderungsmenge · einschließlich Binnenverkehr</div>

        <section class="steckbrief-summary">
          <div class="steckbrief-summary-label">Kurzfazit</div>
          <p><strong>${escapeProfileHtml(regMeta.name)}</strong>: Im Jahr ${profileYear} wurden ${formatMio(total)} Güter bewegt. ${trendSentence} ${modeSentence} ${balanceSentence} ${forecastSentence}</p>
        </section>

        <section class="steckbrief-section">
          <div class="steckbrief-section-heading"><span>Kernkennzahlen</span></div>
          <div class="steckbrief-kpi-grid">
            <div class="steckbrief-kpi-card"><span>Güteraufkommen</span><strong>${formatMio(total)}</strong><small>Versand und Empfang</small></div>
            <div class="steckbrief-kpi-card"><span>Entwicklung seit ${baseYear || '–'}</span><strong class="${profileChangeClass(totalChange)}">${profileChangeText(totalChange)}</strong><small>${baseYear ? `gegenüber ${baseYear}` : 'kein Basisjahr'}</small></div>
            <div class="steckbrief-kpi-card"><span>Größter Verkehrsträger</span><strong>${leadingMode.label}</strong><small>${formatShare(leadingMode.share)} des Aufkommens</small></div>
            <div class="steckbrief-kpi-card"><span>Verkehrssaldo</span><strong class="${balance > 0 ? 'is-positive' : balance < 0 ? 'is-negative' : 'is-neutral'}">${formatSignedMio(balance)}</strong><small>${balance > 0 ? 'Versandüberschuss' : balance < 0 ? 'Empfangsüberschuss' : 'ausgeglichen'}</small></div>
          </div>
        </section>

        <section class="steckbrief-section steckbrief-two-column">
          <div>
            <div class="steckbrief-section-heading"><span>Verkehrsstruktur</span><small>Anteil am Verkehrsaufkommen</small></div>
            <div class="steckbrief-mode-list">${modeRows.map(row => `<div class="steckbrief-mode-row ${row.css}"><div class="steckbrief-mode-label"><span>${row.label}</span><strong>${formatShare(row.share)}</strong></div><div class="steckbrief-mode-bar" aria-hidden="true"><span style="width:${Math.max(0, Math.min(100, row.share))}%"></span></div><small>${formatMio(row.value)}${row.nationalShare === null ? '' : ` · Bund: ${formatShare(row.nationalShare)}`}</small></div>`).join('')}</div>
          </div>
          <div>
            <div class="steckbrief-section-heading"><span>${isPronouncedGroup ? 'Prägende Güterart' : 'Größte Gütergruppe'}</span><small>NST-2007</small></div>
            <p class="steckbrief-section-text">${goodsSentence}</p>
            <ol class="steckbrief-goods-list">${groupRows.slice(0, 3).map((group, index) => `<li><span>${index + 1}</span><div><strong>${group.label}</strong><small>${formatMio(group.value)} · ${formatShare(group.share)}${group.nationalShare === null ? '' : ` · Bund: ${formatShare(group.nationalShare)}`}</small></div></li>`).join('')}</ol>
          </div>
        </section>

        <section class="steckbrief-section steckbrief-development-section">
          <div class="steckbrief-section-heading"><span>Entwicklung des Güteraufkommens</span></div>
          <div class="steckbrief-timeline">${milestones}</div>
          <div class="steckbrief-development-split">
            <div class="steckbrief-development-split-heading"><span>Modal Split im Zeitverlauf</span><small>${trendStartYear}–${trendEndYear}</small></div>
            <p class="steckbrief-section-text">Beförderungsmenge nach Verkehrsträgern. Die Zeitreihe reicht je Verkehrsträger bis zum zuletzt vorliegenden Jahr.</p>
            ${modalSplitTrendHtml}
          </div>
        </section>

        <section class="steckbrief-section">
          <div class="steckbrief-section-heading"><span>Stärkste Verkehrsbeziehungen</span><small>Top 3 im Jahr ${profileYear}</small></div>
          ${relationHtml}
        </section>

        ${kvSectionHtml}

        ${forecastSectionHtml}

        <footer class="steckbrief-sources">
          <strong>Datengrundlage</strong>
          <span>Straßengüterverkehr: Kraftfahrt-Bundesamt (bis ${getLatestAvailableModeYear('road') || profileYear}). Schienengüterverkehr und Binnenschifffahrt: Statistisches Bundesamt (bis ${Math.max(getLatestAvailableModeYear('rail') || 0, getLatestAvailableModeYear('iww') || 0, Number(profileYear))}). Kombinierter Verkehr: Statistisches Bundesamt.${forecastOutlook ? ' Ausblick 2040: BMDV-Verkehrsprognose 2040, Basisprognose P1.' : ''} Raumbezug: Eurostat / GISCO.</span>
        </footer>
      </article>`;
  }

  // Render Top-X Table (Overview with Metric Header, Group Filter & Clean Numbers)
  function renderTopRelationsTable() {
    const tbody = document.getElementById('tableTopRelationsBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    const isTkm = state.metric === 'tkm';
    const thUnit = document.getElementById('thMetricUnit');
    if (thUnit) {
      thUnit.textContent = state.direction === 'balance'
        ? (isTkm ? 'Saldo (in Mio. tkm)' : 'Saldo (in 1.000 Tonnen)')
        : (isTkm ? 'Verkehrsleistung (in Mio. tkm)' : 'Menge (in 1.000 Tonnen)');
      thUnit.title = thUnit.textContent;
    }

    const noticeEl = document.getElementById('overviewDataNotice');
    if (noticeEl) noticeEl.style.display = 'none';

    if (!state.region) {
      const nationalScopeText = state.selectedGroup && state.selectedGroup !== 'ALL'
        ? 'Für eine Gütergruppe zeigen die Werte räumlich zuordenbare Verkehrsströme ohne reine Transitverkehre. Sie sind deshalb nicht mit der nationalen Randsumme einschließlich Transit vergleichbar.'
        : 'Die Kennzahlen für Deutschland umfassen bei Straße, Schiene und Binnenschiff auch Transitverkehre. Diese haben keine deutsche Quell- oder Zielregion und erscheinen deshalb nicht in Karte und regionalen Relationstabellen. Die nationale Verkehrsleistung der Straße wird als Inlandstonnenkilometer ausgewiesen.';
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

    const regTopAll = getRegionRelations(state.region);
    const yrTop = regTopAll[state.year] || { outbound_overall: [], inbound_overall: [], by_mode: {} };

    const { flows: rawFlows, availability } = getOverviewRelations(yrTop, state.selectedGroup, state.direction, regTopAll);
    let list = [...rawFlows];

    // Handle Data Availability Notice Banner
    if (noticeEl) {
      if (state.selectedGroup && state.selectedGroup !== 'ALL') {
        const availableModes = [];
        if (availability.rail) availableModes.push('im <strong>Schienengüterverkehr</strong>');
        if (availability.iww) availableModes.push('in der <strong>Binnenschifffahrt</strong>');
        if (availability.road) availableModes.push('im <strong>Straßengüterverkehr</strong>');

        let noticeHtml = `
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#4f46e5" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0; margin-top:2px;">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          <div>
        `;
        if (availableModes.length > 0) {
          noticeHtml += `<strong>Hinweis zur Datenverfügbarkeit:</strong> Für die Güterart <em>${NST_GROUPS_7[state.selectedGroup]}</em> liegen relationale Verflechtungsdaten ${availableModes.join(' und ')} vor. Für den Straßengüterverkehr werden bilaterale Kreisverflechtungen im amtlichen KBA-Erhebungsdesign nur summiert über alle Güterarten auf regionaler Ebene (NUTS-3/NUTS-2) ausgewiesen (die differenzierte NST-2007-Güterstruktur dieser Region finden Sie im Analysemodul <em>Straßengüterverkehr</em>).`;
        } else {
          noticeHtml += `<strong>Hinweis zur Datenverfügbarkeit:</strong> Für die Güterart <em>${NST_GROUPS_7[state.selectedGroup]}</em> wurden in dieser Region keine bilateralen Kreisverflechtungen in den amtlichen Verkehrsstatistiken erfasst (z. B. bedingt durch das Erhebungsdesign oder statistische Abschneidegrenzen).`;
        }
        noticeHtml += `</div>`;
        noticeEl.innerHTML = noticeHtml;
        noticeEl.style.display = 'flex';
      } else {
        noticeEl.style.display = 'none';
      }
    }

    // Filter Binnenverkehr if unchecked
    if (!state.includeBinnen) {
      list = list.filter(r => !r.is_binnen && (r.dest_id !== state.region) && (r.origin_id !== state.region));
    }

    const overviewFlowAmount = row => isTkm ? (row.tkm || 0) : (row.tonnes || 0);
    list.sort((a, b) => state.direction === 'balance'
      ? Math.abs(overviewFlowAmount(b)) - Math.abs(overviewFlowAmount(a))
      : overviewFlowAmount(b) - overviewFlowAmount(a));

    const filtered = list.slice(0, state.topX);

    if (filtered.length === 0) {
      const groupText = (state.selectedGroup && state.selectedGroup !== 'ALL') ? ` für <strong>${NST_GROUPS_7[state.selectedGroup]}</strong>` : '';
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#64748b; padding:24px; font-size:0.85rem; line-height:1.5;">Für die ausgewählte Region wurden im Erhebungsjahr ${state.year}${groupText} keine Daten erfasst (z. B. bedingt durch das statistische Erhebungsdesign, regionale Erfassungsgrenzen oder Stichprobenabschneidungen).</td></tr>`;
      return;
    }

    filtered.forEach(r => {
      const partnerId = r.dest_id || r.origin_id || '';
      const partnerName = r.dest_name || r.origin_name || regionsData[partnerId]?.name || fullCentroids[partnerId]?.name || partnerId;
      const rawValue = isTkm ? (r.tkm || 0) / 1e6 : (r.tonnes || 0) / 1e3;
      const cleanValNum = `${state.direction === 'balance' && rawValue > 0 ? '+' : ''}${formatQuantity(rawValue, 1)}`;
      
      const yoyVal = (r.yoy_pct !== null && r.yoy_pct !== undefined) ? r.yoy_pct : (isTkm ? r.yoy_pct_tkm : r.yoy_pct_tonnes);
      const trendVal = (r.trend_10yr_pct !== null && r.trend_10yr_pct !== undefined) ? r.trend_10yr_pct : (isTkm ? r.trend_10yr_pct_tkm : r.trend_10yr_pct_tonnes);
      const formatHistoricSaldo = value => {
        if (value === null || value === undefined) return '<span style="color:#94a3b8;" title="Kein historischer Saldo für dieses Jahr vorhanden.">--</span>';
        const historic = isTkm ? value / 1e6 : value / 1e3;
        return `<span style="font-weight:700;">${historic > 0 ? '+' : ''}${formatQuantity(historic, 1)}</span>`;
      };

      const yoy = state.direction === 'balance'
        ? formatHistoricSaldo(r.previous_value)
        : (yoyVal !== null && yoyVal !== undefined)
        ? `<span style="color:${yoyVal >= 0 ? '#16a34a' : '#dc2626'}; font-weight:700;">${yoyVal >= 0 ? '↗ +' : '↘ '}${formatDeNum(yoyVal, 1)} %</span>`
        : '<span style="color:#94a3b8;">--</span>';

      const trend10 = state.direction === 'balance'
        ? formatHistoricSaldo(r.baseline_value)
        : (trendVal !== null && trendVal !== undefined)
        ? `<span style="color:${trendVal >= 0 ? '#16a34a' : '#dc2626'}; font-weight:700;">${trendVal >= 0 ? '↗ +' : '↘ '}${formatDeNum(trendVal, 1)} %</span>`
        : '<span style="color:#94a3b8;">--</span>';

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
      if (modeBadge) modeBadge = `<span class="relation-mode-badges">${modeBadge}</span>`;

      const row = document.createElement('tr');
      row.setAttribute('data-partner-id', partnerId);
      row.innerHTML = `
        <td><strong>${partnerName}</strong> <span style="font-size:0.75rem; color:#94a3b8;">(${partnerId})</span>${binnenBadge}${modeBadge}</td>
        <td style="text-align: right;"><strong>${cleanValNum}</strong></td>
        <td style="text-align: right;">${yoy}</td>
        <td style="text-align: right;">${trend10}</td>
      `;

      // Bi-directional hover bindings
      row.addEventListener('mouseenter', () => setHighlight('overview', partnerId));
      row.addEventListener('mouseleave', () => clearAllHighlights('overview'));
      tbody.appendChild(row);
    });

    const tableWrapper = tbody.closest('.data-table-wrapper');
    if (tableWrapper) {
      tableWrapper.onmouseleave = () => clearAllHighlights('overview');
    }
  }

  // ============================================================
  // CHART: Modal Split
  // ============================================================
  function setOverviewChartEmptyState(canvas, message) {
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

  function renderModalSplitChart() {
    const ctx = document.getElementById('chartModalSplit');
    if (!ctx) return;
    if (chartModalSplit) chartModalSplit.destroy();

    const regYears = getActiveRegionSummary();
    const isTkm = state.metric === 'tkm';
    const divisor = isTkm ? 1e9 : 1e6;
    const unitText = isTkm ? 'Mrd. tkm' : 'Mio. t';
    const isBalance = state.direction === 'balance';
    const incompleteRoadYear = state.year === '2025' && state.modalSplitView === 'snapshot';
    const splitTitle = incompleteRoadYear
      ? 'Modal Split nicht verfügbar'
      : isBalance
      ? (state.modalSplitView === 'snapshot' ? 'Modalstruktur des Saldos' : 'Saldo nach Verkehrsträgern')
      : 'Modal Split';
    const splitInfo = incompleteRoadYear
      ? 'Ein vollständiger Modal Split ist für 2025 noch nicht verfügbar, da die amtlichen Straßengüterverkehrsdaten derzeit mit 2024 enden. Die vorhandenen Werte für Schiene und Binnenschiff werden deshalb nicht auf 100 Prozent normiert.'
      : isBalance
      ? (state.modalSplitView === 'snapshot'
        ? 'Bei Saldo ist ein klassischer Modal Split nicht definiert. Die Grafik zeigt daher die Anteile der absoluten Modal-Salden: Positive und negative Verkehrsträgersalden gehen jeweils mit ihrem Betrag ein. Die Vorzeichen bleiben in den Tooltipps sichtbar.'
        : 'Die Dynamik zeigt die vorzeichenbehafteten Salden der Verkehrsträger. Werte über null stehen für Versandüberschuss, Werte unter null für Empfangsüberschuss.')
      : 'Dieses Diagramm bildet die Anteile und die zeitliche Entwicklung der drei Hauptverkehrsträger Straßengüterverkehr, Schienengüterverkehr und Binnenschifffahrt für die gewählte Region ab. Im Zeitverlauf (Dynamik) sind für Schiene und Binnenschiff bereits Daten bis 2025 enthalten, während die amtlichen Straßendaten aktuell mit dem Berichtsjahr 2024 abschließen.';
    setText('modalSplitCardTitle', splitTitle);
    setText('modalSplitInfoText', splitInfo);
    if (incompleteRoadYear) {
      setOverviewChartEmptyState(ctx, 'Für 2025 ist noch kein vollständiger Modal Split verfügbar. Straßengüterverkehrsdaten liegen derzeit bis 2024 vor.');
      return;
    }
    setOverviewChartEmptyState(ctx, null);
    if (state.modalSplitView === 'snapshot') {
      const curr = regYears[state.year] || { modes_tonnes: {}, modes_tkm: {}, by_mode_groups: {} };
      
      const getModeVal = (m) => {
        if (state.selectedGroup && state.selectedGroup !== 'ALL') {
          const grp = state.selectedGroup;
          const mg = (isTkm ? curr.by_mode_groups_tkm : curr.by_mode_groups)?.[m];
          if (!mg) return 0;
          if (state.direction === 'inbound') return mg.inbound?.[grp] || 0;
          if (state.direction === 'outbound') return mg.outbound?.[grp] || 0;
          if (state.direction === 'balance') return (mg.outbound?.[grp] || 0) - (mg.inbound?.[grp] || 0);
          return mg.all?.[grp] || mg[grp] || 0;
        } else {
          if (state.direction === 'inbound' || state.direction === 'outbound') {
            const dir = state.direction;
            const dirModes = isTkm ? curr.modes_direction_tkm : curr.modes_direction_tonnes;
            return dirModes?.[m]?.[dir] || 0;
          } else if (state.direction === 'balance') {
            const dirModes = isTkm ? curr.modes_direction_tkm : curr.modes_direction_tonnes;
            return (dirModes?.[m]?.outbound || 0) - (dirModes?.[m]?.inbound || 0);
          } else {
            const modesObj = isTkm ? (curr.modes_tkm || {}) : (curr.modes_tonnes || {});
            return modesObj[m] || 0;
          }
        }
      };

      const road = getModeVal('road') / divisor;
      const rail = getModeVal('rail') / divisor;
      const iww = getModeVal('iww') / divisor;
      const tot = Math.abs(road) + Math.abs(rail) + Math.abs(iww);

      const roadPct = tot > 0 ? formatDeNum((Math.abs(road) / tot) * 100, 1) : '0,0';
      const railPct = tot > 0 ? formatDeNum((Math.abs(rail) / tot) * 100, 1) : '0,0';
      const iwwPct = tot > 0 ? formatDeNum((Math.abs(iww) / tot) * 100, 1) : '0,0';
      const chartValues = isBalance
        ? [Math.abs(road), Math.abs(rail), Math.abs(iww)]
        : [Math.max(0, road), Math.max(0, rail), Math.max(0, iww)];
      const signedValues = [road, rail, iww];

      chartModalSplit = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: [`Straße (${roadPct} %)`, `Schiene (${railPct} %)`, `Binnenschiff (${iwwPct} %)`],
          datasets: [{
            data: chartValues,
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
              labels: { 
                boxWidth: 12, 
                padding: 10,
                font: { size: 11.5, weight: '600' } 
              } 
            },
            tooltip: {
              callbacks: {
                title: () => `Bezugsjahr: ${state.year}`,
                label: c => {
                  if (!isBalance) return ` ${c.label}: ${formatDeNum(c.raw, 2)} ${unitText}`;
                  const signedValue = signedValues[c.dataIndex] || 0;
                  return ` ${c.label}: ${signedValue > 0 ? '+' : ''}${formatDeNum(signedValue, 2)} ${unitText} (Betrag: ${formatDeNum(c.raw, 2)} ${unitText})`;
                }
              }
            }
          }
        }
      });
    } else {
      const allYears = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];
      const validYears = allYears.filter(y => {
        const yrObj = regYears[y];
        if (!yrObj) return false;
        if (state.selectedGroup && state.selectedGroup !== 'ALL') {
          const grp = state.selectedGroup;
          const cube = isTkm ? yrObj.by_mode_groups_tkm : yrObj.by_mode_groups;
          const r = cube?.road?.[grp] || cube?.road?.all?.[grp] || 0;
          const s = cube?.rail?.[grp] || cube?.rail?.all?.[grp] || 0;
          const i = cube?.iww?.[grp] || cube?.iww?.all?.[grp] || 0;
          return (r + s + i) > 0;
        }
        const modesT = yrObj.modes_tonnes || {};
        const modesK = yrObj.modes_tkm || {};
        const hasRoad = (isTkm ? modesK.road : modesT.road) > 0;
        const hasRail = (isTkm ? modesK.rail : modesT.rail) > 0;
        const hasIww = (isTkm ? modesK.iww : modesT.iww) > 0;
        return hasRoad || hasRail || hasIww;
      });

      const getModeYearVal = (yrObj, m) => {
        if (!yrObj) return null;
        if (state.selectedGroup && state.selectedGroup !== 'ALL') {
          const grp = state.selectedGroup;
          const mg = (isTkm ? yrObj.by_mode_groups_tkm : yrObj.by_mode_groups)?.[m];
          if (!mg) return null;
          let v = 0;
          if (state.direction === 'inbound') v = mg.inbound?.[grp];
          else if (state.direction === 'outbound') v = mg.outbound?.[grp];
          else if (state.direction === 'balance') v = (mg.outbound?.[grp] || 0) - (mg.inbound?.[grp] || 0);
          else v = mg.all?.[grp] ?? mg[grp];
          return (v !== undefined && v !== null && (state.direction === 'balance' || v > 0)) ? (v / divisor) : null;
        } else {
          let v = 0;
          if (state.direction === 'inbound' || state.direction === 'outbound') {
            const dir = state.direction;
            const dirModes = isTkm ? yrObj.modes_direction_tkm : yrObj.modes_direction_tonnes;
            v = dirModes?.[m]?.[dir];
          } else if (state.direction === 'balance') {
            const dirModes = isTkm ? yrObj.modes_direction_tkm : yrObj.modes_direction_tonnes;
            v = (dirModes?.[m]?.outbound || 0) - (dirModes?.[m]?.inbound || 0);
          } else {
            const modesObj = isTkm ? (yrObj.modes_tkm || {}) : (yrObj.modes_tonnes || {});
            v = modesObj[m];
          }
          return (v !== undefined && v !== null && (state.direction === 'balance' || v > 0)) ? (v / divisor) : null;
        }
      };
      
      const roadData = validYears.map(y => (y <= 2024 ? getModeYearVal(regYears[y], 'road') : null));
      const railData = validYears.map(y => getModeYearVal(regYears[y], 'rail'));
      const iwwData = validYears.map(y => getModeYearVal(regYears[y], 'iww'));

      chartModalSplit = new Chart(ctx, {
        type: 'line',
        data: {
          labels: validYears,
          datasets: [
            { label: `Straße (${unitText})`, data: roadData, borderColor: '#f59e0b', backgroundColor: '#f59e0b', tension: 0.2, spanGaps: false, borderWidth: 2.5 },
            { label: `Schiene (${unitText})`, data: railData, borderColor: '#2563eb', backgroundColor: '#2563eb', tension: 0.2, spanGaps: false, borderWidth: 2.5 },
            { label: `Binnenschiff (${unitText})`, data: iwwData, borderColor: '#0d9488', backgroundColor: '#0d9488', tension: 0.2, spanGaps: false, borderWidth: 2.5 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { 
              position: 'bottom', 
              labels: { 
                boxWidth: 12, 
                padding: 10,
                font: { size: 11.5, weight: '600' } 
              } 
            },
            tooltip: { 
              callbacks: { 
                title: items => `Jahr: ${items[0]?.label}`,
                label: c => {
                  const val = c.raw;
                  if (val === null || val === undefined) return '';
                  const idx = c.dataIndex;
                  const r = Math.abs(roadData[idx] || 0);
                  const s = Math.abs(railData[idx] || 0);
                  const w = Math.abs(iwwData[idx] || 0);
                  const yearTot = r + s + w;
                  const pct = yearTot > 0 ? formatDeNum((Math.abs(val) / yearTot) * 100, 1) : '0,0';
                  const modeName = c.dataset.label.replace(` (${unitText})`, '');
                  return ` ${modeName}: ${formatDeNum(val, 2)} ${unitText} (${pct} %)`;
                }
              } 
            }
          },
          scales: { 
            x: {
              ticks: { font: { size: 11, weight: '600' } }
            },
            y: { 
              beginAtZero: state.direction !== 'balance', 
              title: { display: true, text: unitText, font: { size: 11, weight: '600' } },
              ticks: { font: { size: 11 } }
            } 
          }
        }
      });
    }
  }

  // ============================================================
  // CHART: Güterstruktur NST-2007 (Overview)
  // ============================================================
  function renderCommodityChart() {
    const ctx = document.getElementById('chartCommodity');
    if (!ctx) return;
    if (chartCommodity) chartCommodity.destroy();

    const regYears = getActiveRegionSummary();
    const isTkm = state.metric === 'tkm';
    const divisor = isTkm ? 1e9 : 1e6;
    const unitText = isTkm ? 'Mrd. tkm' : 'Mio. t';
    // Status is a point-in-time view and must follow the year selected in
    // "Aktuelle Einstellungen". Only the time-series view below deliberately
    // uses the latest consolidated year across all modes.
    const selectedYear = String(state.year);
    const selectedDirection = (state.direction === 'inbound' || state.direction === 'outbound') ? state.direction : 'all';

    const sortedGroupKeys = Object.keys(NST_GROUPS_7).sort((a, b) => parseInt(a, 10) - parseInt(b, 10));

    if (state.commodityView === 'snapshot') {
      const curr = regYears[selectedYear] || {};
      const grpObj = isTkm ? (curr.groups_7_tkm || {}) : (curr.groups_7_tonnes || {});
      let currMap = {};
      if (state.direction === 'balance') {
        const outMap = grpObj.outbound || grpObj;
        const inMap = grpObj.inbound || grpObj;
        sortedGroupKeys.forEach(k => {
          currMap[k] = (outMap[k] || 0) - (inMap[k] || 0);
        });
      } else {
        currMap = grpObj[selectedDirection] || grpObj.all || grpObj;
      }

      const values = sortedGroupKeys.map(k => (currMap[k] || 0) / divisor);
      const totalVal = values.reduce((a, b) => a + Math.abs(b), 0);

      const cleanLabels = sortedGroupKeys.map(k => NST_GROUPS_7[k]);

      chartCommodity = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: cleanLabels,
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
                // The chart can abbreviate axis labels on narrow cards.  The
                // full NST name therefore remains available in the hover.
                title: items => cleanLabels[items[0]?.dataIndex] || `Ausgewähltes Jahr: ${selectedYear}`,
                label: c => {
                  const val = c.raw;
                  const pct = totalVal > 0 ? formatDeNum((Math.abs(val) / totalVal) * 100, 1) : '0,0';
                  return `Ausgewähltes Jahr ${selectedYear}: ${formatDeNum(val, 2)} ${unitText} (${pct} %)`;
                }
              }
            }
          },
          scales: { 
            x: { 
              beginAtZero: state.direction !== 'balance', 
              position: 'bottom',
              title: { display: true, text: unitText, font: { size: 11, weight: '600' } },
              ticks: { font: { size: 10.5 } }
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
      enableYAxisLabelHover(chartCommodity, cleanLabels);
    } else {
      const allYears = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];
      // The time series reaches the newest common year of all three modes.
      // The earlier implementation checked an incomplete first-load summary
      // and could prematurely stop at 2020 although the goods data continued.
      const latestConsolidatedYear = getLatestConsolidatedOverviewYear(regYears, isTkm);
      const validYears = allYears.filter(y => {
        if (y > latestConsolidatedYear) return false;
        const grpObj = isTkm ? regYears[y]?.groups_7_tkm : regYears[y]?.groups_7_tonnes;
        const yrMap = grpObj?.[selectedDirection] || grpObj?.all || grpObj || {};
        return sortedGroupKeys.some(key => Number(yrMap[key] || 0) !== 0);
      });

      const colors = ['#16a34a', '#dc2626', '#9333ea', '#d97706', '#4f46e5', '#475569', '#0d9488'];
      
      const datasets = sortedGroupKeys.map((k, i) => ({
        label: NST_GROUPS_7[k],
        data: validYears.map(y => {
          const yrObj = regYears[y] || {};
          const grpObj = isTkm ? (yrObj.groups_7_tkm || {}) : (yrObj.groups_7_tonnes || {});
          let val;
          if (state.direction === 'balance') {
            val = (grpObj.outbound?.[k] || 0) - (grpObj.inbound?.[k] || 0);
          } else {
            const yrMap = grpObj[selectedDirection] || grpObj.all || grpObj;
            val = yrMap[k];
          }
          return (val !== undefined && val !== null) ? (val / divisor) : null;
        }),
        borderColor: colors[i % colors.length],
        backgroundColor: colors[i % colors.length],
        tension: 0.2,
        spanGaps: false,
        borderWidth: 2
      }));

      chartCommodity = new Chart(ctx, {
        type: 'line',
        data: { labels: validYears, datasets: datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { 
              position: 'bottom',
              align: 'start',
              labels: { 
                boxWidth: 10, 
                padding: 8,
                font: { size: 11, weight: '600' } 
              } 
            },
            tooltip: { 
              callbacks: { 
                title: items => `Jahr: ${items[0]?.label}`,
                label: c => formatDynamicChartShare(c, unitText)
              } 
            }
          },
          scales: {
            x: {
              ticks: { font: { size: 10.5, weight: '600' } }
            },
            y: {
              beginAtZero: state.direction !== 'balance',
              title: { display: true, text: unitText, font: { size: 11, weight: '600' } },
              ticks: { font: { size: 10.5 } }
            }
          }
        }
      });
    }
  }

  // ============================================================
  // TAB 2-4: MODE DETAIL TABS (Road, Rail, IWW with Group Filter & Intra Toggle)
  // ============================================================
  function renderModeDetailTab(mode) {
    const groupFilter = state.selectedGroup || 'ALL';

    if (maps[mode]) {
      updateLeafletMap(mode, mode, groupFilter);
    }

    const modeTitles = {
      road: 'Straßengüterverkehr',
      rail: 'Schienengüterverkehr',
      iww: 'Binnenschifffahrt'
    };

    const isTkm = state.metric === 'tkm';
    const thUnitEl = document.getElementById(`th${mode.charAt(0).toUpperCase() + mode.slice(1)}MetricUnit`);
    if (thUnitEl) {
      thUnitEl.textContent = state.direction === 'balance'
        ? (isTkm ? 'Saldo (in Mio. tkm)' : 'Saldo (in 1.000 Tonnen)')
        : (isTkm ? 'Verkehrsleistung (in Mio. tkm)' : 'Menge (in 1.000 Tonnen)');
      thUnitEl.title = thUnitEl.textContent;
    }

    const tableBody = document.getElementById(`table${mode.charAt(0).toUpperCase() + mode.slice(1)}DetailsBody`);
    if (tableBody) {
      tableBody.innerHTML = '';

      if (!state.region) {
        tableBody.innerHTML = `
          <tr>
            <td colspan="5" style="text-align:center; color:#475569; padding:28px 16px; font-size:0.86rem; line-height:1.6;">
              <div class="empty-state-icon"><img src="assets/icons/map.svg" alt="" aria-hidden="true"></div>
              <strong style="color:#0f172a; font-size:0.95rem;">Deutschland aktiv</strong><br>
              <span style="color:#64748b; font-size:0.81rem;">Bitte wählen Sie in der Karte per <strong>Mausklick eine Region</strong> aus oder öffnen Sie <strong>Aktuelle Einstellungen → Raum &amp; Zeit</strong> und wählen Sie dort eine Region aus, um relationale Verflechtungen und Partnerregionen anzuzeigen.</span>
            </td>
          </tr>
        `;
      } else {
        const regTopAll = getRegionRelations(state.region);
        const yrTop = regTopAll[state.year] || { by_mode: {} };
        const modeData = yrTop.by_mode?.[mode] || { outbound: [], inbound: [], by_group: {} };

        let list = getModeRelations(modeData, groupFilter, state.direction, mode);

        // Filter Binnenverkehr if unchecked
        if (!state.includeBinnen) {
          list = list.filter(r => !r.is_binnen && (r.dest_id !== state.region) && (r.origin_id !== state.region));
        }

        // Sort by active metric
        const modeFlowAmount = row => isTkm ? (row.tkm || 0) : (row.tonnes || 0);
        list.sort((a, b) => state.direction === 'balance'
          ? Math.abs(modeFlowAmount(b)) - Math.abs(modeFlowAmount(a))
          : modeFlowAmount(b) - modeFlowAmount(a));

        // The historical series are also used to show raw prior saldos.
        computeFlowTrends(list, mode, state.direction, groupFilter, regTopAll, state.year, isTkm);

        if (list.length === 0) {
          const groupLabel = groupFilter !== 'ALL' ? NST_GROUPS_7[groupFilter] : modeTitles[mode];
          let emptyMsg = `Für <strong>${groupLabel}</strong> wurden im Erhebungsjahr ${state.year} in dieser Region keine Daten erfasst (z. B. bedingt durch das Erhebungsdesign oder statistische Abschneidegrenzen).`;
          if (mode === 'road' && groupFilter !== 'ALL') {
            emptyMsg = `Für die Güterart <strong>${groupLabel}</strong> werden bilaterale Kreisverflechtungen im amtlichen KBA-Erhebungsdesign nur summiert über alle Güterarten auf regionaler Ebene (NUTS-3/NUTS-2) ausgewiesen. Die differenzierte regionale Mengenverteilung dieser Gütergruppe finden Sie im Diagramm der Güterstruktur unten.`;
          }
          tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#64748b; padding:24px; font-size:0.85rem; line-height:1.5;">${emptyMsg}</td></tr>`;
        } else {
          list.slice(0, state.topX).forEach(r => {
            const partnerId = r.dest_id || r.origin_id;
            const partnerName = r.dest_name || r.origin_name || regionsData[partnerId]?.name || fullCentroids[partnerId]?.name || partnerId;
            const gName = (groupFilter && groupFilter !== 'ALL') ? (NST_GROUPS_7[groupFilter] || groupFilter) : ((r.group_7 && r.group_7 !== 'ALL') ? (NST_GROUPS_7[r.group_7] || `Gruppe ${r.group_7}`) : 'Alle Güterarten');
            const rawValue = isTkm ? (r.tkm || 0) / 1e6 : (r.tonnes || 0) / 1e3;
            const cleanValNum = `${state.direction === 'balance' && rawValue > 0 ? '+' : ''}${formatQuantity(rawValue, 1)}`;
            
            const yoyVal = (r.yoy_pct !== null && r.yoy_pct !== undefined) ? r.yoy_pct : null;
            const trendVal = (r.trend_10yr_pct !== null && r.trend_10yr_pct !== undefined) ? r.trend_10yr_pct : null;
            const formatHistoricSaldo = value => {
              if (value === null || value === undefined) return '<span style="color:#94a3b8;" title="Kein historischer Saldo für dieses Jahr vorhanden.">--</span>';
              const historic = isTkm ? value / 1e6 : value / 1e3;
              return `<span style="font-weight:700;">${historic > 0 ? '+' : ''}${formatQuantity(historic, 1)}</span>`;
            };

            const yoy = state.direction === 'balance'
              ? formatHistoricSaldo(r.previous_value)
              : (yoyVal !== null && yoyVal !== undefined)
              ? `<span style="color:${yoyVal >= 0 ? '#16a34a' : '#dc2626'}; font-weight:700;">${yoyVal >= 0 ? '↗ +' : '↘ '}${formatDeNum(yoyVal, 1)} %</span>`
              : '<span style="color:#94a3b8;">--</span>';

            const trend10 = state.direction === 'balance'
              ? formatHistoricSaldo(r.baseline_value)
              : (trendVal !== null && trendVal !== undefined)
              ? `<span style="color:${trendVal >= 0 ? '#16a34a' : '#dc2626'}; font-weight:700;">${trendVal >= 0 ? '↗ +' : '↘ '}${formatDeNum(trendVal, 1)} %</span>`
              : '<span style="color:#94a3b8;">--</span>';

            const binnenBadge = r.is_binnen ? '<span style="font-size:0.7rem; background:#e2e8f0; color:#475569; padding:1px 5px; border-radius:4px; margin-left:4px;">Binnen</span>' : '';

            const row = document.createElement('tr');
            row.setAttribute('data-partner-id', partnerId);
            row.innerHTML = `
              <td><strong>${partnerName}</strong> <span style="font-size:0.75rem; color:#94a3b8;">(${partnerId})</span>${binnenBadge}</td>
              <td>${gName}</td>
              <td style="text-align: right;"><strong>${cleanValNum}</strong></td>
              <td style="text-align: right;">${yoy}</td>
              <td style="text-align: right;">${trend10}</td>
            `;

            // Bi-directional hover bindings to Map
            row.addEventListener('mouseenter', () => setHighlight(mode, partnerId));
            row.addEventListener('mouseleave', () => clearAllHighlights(mode));

            tableBody.appendChild(row);
          });
        }
      }

      const tableWrapper = tableBody.closest('.data-table-wrapper');
      if (tableWrapper) {
        tableWrapper.onmouseleave = () => clearAllHighlights(mode);
      }
    }

    if (mode === 'road') renderRoadCommodityChart();
    else if (mode === 'rail') renderRailCommodityChart();
    else if (mode === 'iww') renderIwwCommodityChart();
  }

  // Sub-Commodity Chart Handler
  const subChartInstances = {};

  function setScrollableChartCanvas(canvasId, enabled, contentHeight = 0) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const chartWrap = canvas.closest('.chart-canvas-wrap');
    if (!chartWrap) return;
    let content = canvas.closest('.chart-scroll-content');
    let scrollPlot = canvas.closest('.chart-scroll-plot');

    if (enabled) {
      const plot = canvas.closest('.chart-plot-content');
      if (plot) {
        plot.insertAdjacentElement('beforebegin', canvas);
        plot.remove();
      }
      chartWrap.classList.remove('chart-with-scroll-legend');
      if (!content) {
        content = document.createElement('div');
        content.className = 'chart-scroll-content';
        canvas.insertAdjacentElement('beforebegin', content);
        content.appendChild(canvas);
      }
      if (!scrollPlot) {
        scrollPlot = document.createElement('div');
        scrollPlot.className = 'chart-scroll-plot';
        canvas.insertAdjacentElement('beforebegin', scrollPlot);
        scrollPlot.appendChild(canvas);
      }
      // The outer element is the scroll viewport.  The inner plot retains the
      // full chart height, so the chart itself does not shrink to the viewport.
      content.style.height = '';
      scrollPlot.style.height = `${contentHeight}px`;
      chartWrap.classList.add('chart-canvas-scroll');
      return;
    }

    if (scrollPlot) {
      content?.insertAdjacentElement('beforebegin', canvas);
      scrollPlot.remove();
    }
    if (content) {
      content.insertAdjacentElement('beforebegin', canvas);
      content.remove();
    }
    chartWrap.classList.remove('chart-canvas-scroll');
  }

  function renderStickyChartAxis(canvasId, chart, enabled, unitText) {
    const canvas = document.getElementById(canvasId);
    const chartWrap = canvas?.closest('.chart-canvas-wrap');
    const existing = chartWrap?.querySelector('.chart-sticky-axis');
    if (!canvas || !chartWrap || !chart || !enabled) {
      existing?.remove();
      return;
    }
    const axis = chart.scales?.x;
    const area = chart.chartArea;
    if (!axis || !area || !axis.ticks?.length) return;
    const stickyAxis = existing || document.createElement('div');
    stickyAxis.className = 'chart-sticky-axis';
    stickyAxis.style.setProperty('--chart-axis-left', `${area.left}px`);
    stickyAxis.style.setProperty('--chart-axis-right', `${Math.max(0, chart.width - area.right)}px`);
    stickyAxis.innerHTML = `<span class="chart-sticky-axis-title">${unitText}</span><div class="chart-sticky-axis-ticks">${axis.ticks.map(tick => `<span>${tick.label}</span>`).join('')}</div>`;
    const content = canvas.closest('.chart-scroll-content');
    // The scrolling plot sits above this separate axis.  Keeping the axis out
    // of the scrolling element fixes it at the bottom and prevents bars from
    // peeking through an artificial gap while the user scrolls.
    if (content) content.insertAdjacentElement('afterend', stickyAxis);
  }

  function renderScrollableChartLegend(canvasId, chart, enabled) {
    const canvas = document.getElementById(canvasId);
    const existing = document.getElementById(`${canvasId}-legend`);
    const chartWrap = canvas?.closest('.chart-canvas-wrap');
    if (!canvas || !chart || !enabled) {
      existing?.remove();
      const plot = canvas?.closest('.chart-plot-content');
      if (plot) {
        plot.insertAdjacentElement('beforebegin', canvas);
        plot.remove();
      }
      chartWrap?.classList.remove('chart-with-scroll-legend');
      return;
    }
    let plot = canvas.closest('.chart-plot-content');
    if (!plot) {
      plot = document.createElement('div');
      plot.className = 'chart-plot-content';
      canvas.insertAdjacentElement('beforebegin', plot);
      plot.appendChild(canvas);
    }
    const legend = existing || document.createElement('div');
    legend.id = `${canvasId}-legend`;
    legend.className = 'chart-scroll-legend';
    legend.innerHTML = chart.data.datasets.map(dataset => `<span><i style="background:${dataset.borderColor};"></i>${dataset.label}</span>`).join('');
    if (!existing) plot.insertAdjacentElement('afterend', legend);
    chartWrap?.classList.add('chart-with-scroll-legend');
    requestAnimationFrame(() => chart.resize());
  }

  function renderGenericCommodityChart(canvasId, mode, viewMode, nstLevel) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (subChartInstances[canvasId]) {
      subChartInstances[canvasId].destroy();
      subChartInstances[canvasId] = null;
    }

    const regYears = getActiveRegionSummary();
    const isTkm = state.metric === 'tkm';
    const divisor = isTkm ? 1e9 : 1e6;
    const unitText = isTkm ? 'Mrd. tkm' : 'Mio. t';

    const is20 = (nstLevel === '20');
    const isDetailedSnapshot = is20 && viewMode === 'snapshot';
    if (is20 && mode === 'road') {
      state.roadNstLevel = '7';
      const selector = document.getElementById('selectRoadNstLevel');
      if (selector) selector.value = '7';
      return renderGenericCommodityChart(canvasId, mode, viewMode, '7');
    }
    const taxonomyDict = is20 ? NST_DIVISIONS_20 : NST_GROUPS_7;
    const dataKey = is20
      ? (isTkm ? 'by_mode_divisions_tkm' : 'by_mode_divisions')
      : (isTkm ? 'by_mode_groups_tkm' : 'by_mode_groups');
    const dir = (state.direction === 'inbound' || state.direction === 'outbound') ? state.direction : 'all';

    // Strict numerical sorting for 1..7 or 1..20
    const sortedKeys = Object.keys(taxonomyDict).sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
    setScrollableChartCanvas(canvasId, isDetailedSnapshot, Math.max(650, sortedKeys.length * 31 + 100));
    renderStickyChartAxis(canvasId, null, false, unitText);

    const getVal = (dataMap, k) => {
      if (!dataMap) return 0;
      const padK = k.padStart(2, '0');
      const unpadK = String(parseInt(k, 10));
      return dataMap[padK] ?? dataMap[unpadK] ?? dataMap[k] ?? 0;
    };

    if (viewMode === 'snapshot') {
      const modeDataMap = regYears[state.year]?.[dataKey]?.[mode] || {};
      let curr = {};
      if (state.direction === 'balance') {
        const outMap = modeDataMap.outbound || modeDataMap;
        const inMap = modeDataMap.inbound || modeDataMap;
        sortedKeys.forEach(k => {
          curr[k] = getVal(outMap, k) - getVal(inMap, k);
        });
      } else {
        curr = modeDataMap[dir] || modeDataMap.all || modeDataMap;
      }

      const values = sortedKeys.map(k => getVal(curr, k) / divisor);
      const totalVal = values.reduce((a, b) => a + Math.abs(b), 0);

      // Clean Y-axis labels WITHOUT percentages so text is fully legible
      const cleanLabels = sortedKeys.map(k => taxonomyDict[k] || taxonomyDict[k.padStart(2, '0')] || taxonomyDict[String(parseInt(k, 10))]);

      const barColor = mode === 'road' ? '#f59e0b' : (mode === 'rail' ? '#2563eb' : (mode === 'maritime' ? '#4f46e5' : '#10b981'));

      subChartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: cleanLabels,
          datasets: [{ label: unitText, data: values, backgroundColor: barColor, borderRadius: 4 }]
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
                // See the corresponding overview chart: keep the complete
                // category visible in the hover even where the axis is tight.
                title: items => cleanLabels[items[0]?.dataIndex] || `Bezugsjahr: ${state.year}`,
                label: c => {
                  const val = c.raw;
                  const pct = totalVal > 0 ? formatDeNum((Math.abs(val) / totalVal) * 100, 1) : '0,0';
                  return `Bezugsjahr ${state.year}: ${formatDeNum(val, 2)} ${unitText} (${pct} %)`;
                }
              }
            }
          },
          scales: {
            x: { 
              beginAtZero: state.direction !== 'balance', 
              title: { display: !isDetailedSnapshot, text: unitText, font: { size: 11, weight: '600' } },
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
      enableYAxisLabelHover(subChartInstances[canvasId], cleanLabels);
      if (isDetailedSnapshot) requestAnimationFrame(() => {
        subChartInstances[canvasId]?.resize();
        requestAnimationFrame(() => renderStickyChartAxis(canvasId, subChartInstances[canvasId], true, unitText));
      });
      renderScrollableChartLegend(canvasId, null, false);
    } else {
      // Dynamically filter complete years
      const allYears = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];
      const validYears = allYears.filter(y => {
        const yrObj = regYears[y];
        if (!yrObj) return false;
        const modeTot = isTkm ? yrObj.modes_tkm?.[mode] : yrObj.modes_tonnes?.[mode];
        return (modeTot !== undefined && modeTot !== null && modeTot > 0);
      });

      const colors = ['#16a34a', '#dc2626', '#9333ea', '#d97706', '#4f46e5', '#475569', '#0d9488', '#ec4899', '#8b5cf6', '#3b82f6'];

      const datasets = sortedKeys.map((k, i) => ({
        label: taxonomyDict[k] || taxonomyDict[k.padStart(2, '0')] || taxonomyDict[String(parseInt(k, 10))],
        data: validYears.map(y => {
          const yData = regYears[y]?.[dataKey]?.[mode] || {};
          let val;
          if (state.direction === 'balance') {
            const outMap = yData.outbound || yData;
            const inMap = yData.inbound || yData;
            val = getVal(outMap, k) - getVal(inMap, k);
          } else {
            const yMap = yData[dir] || yData.all || yData;
            val = getVal(yMap, k);
          }
          return (val !== undefined && val !== null) ? (val / divisor) : null;
        }),
        borderColor: colors[i % colors.length],
        backgroundColor: colors[i % colors.length],
        tension: 0.2,
        spanGaps: false,
        borderWidth: 2
      })).filter(dataset => dataset.data.some(value => value !== null && value !== 0));

      subChartInstances[canvasId] = new Chart(ctx, {
        type: 'line',
        data: { labels: validYears, datasets: datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { 
              display: !is20,
              position: 'bottom',
              align: 'start',
              labels: { 
                boxWidth: 10, 
                padding: 8,
                font: { size: 11, weight: '600' } 
              } 
            },
            tooltip: { 
              callbacks: { 
                title: items => `Jahr: ${items[0]?.label}`,
                label: c => formatDynamicChartShare(c, unitText)
              } 
            }
          },
          scales: { 
            x: {
              ticks: { font: { size: 11, weight: '600' } }
            },
            y: { 
              beginAtZero: state.direction !== 'balance', 
              title: { display: true, text: unitText, font: { size: 11, weight: '600' } },
              ticks: { font: { size: 11 } }
            } 
          }
        }
      });
      renderScrollableChartLegend(canvasId, subChartInstances[canvasId], is20);
    }
  }

  function renderRoadCommodityChart() {
    renderGenericCommodityChart('chartRoadCommodity', 'road', state.roadCommodityView, state.roadNstLevel);
  }
  function renderRailCommodityChart() {
    renderGenericCommodityChart('chartRailCommodity', 'rail', state.railCommodityView, state.railNstLevel);
  }
  function renderIwwCommodityChart() {
    renderGenericCommodityChart('chartIwwCommodity', 'iww', state.iwwCommodityView, state.iwwNstLevel);
  }

  // Dynamic table headings: signed saldos are shown as raw historic values,
  // while percentage changes remain reserved for ordinary traffic volumes.
  function updateTableHistoricalHeaders() {
    const baseYear = '2016';
    const isBase = (state.year === baseYear);
    ['overview', 'road', 'rail', 'iww', 'maritime'].forEach(k => {
      const prevEl = document.getElementById(`thPrev_${k}`);
      const el = document.getElementById(`thTrend_${k}`);
      if (state.direction === 'balance') {
        const previousYear = String(Math.max(Number(baseYear), Number(state.year) - 1));
        if (prevEl) {
          prevEl.innerHTML = `Saldo<br><span>${previousYear}</span>`;
          prevEl.title = `Saldo der Relation im Vorjahr ${previousYear}`;
        }
        if (el) {
          el.innerHTML = isBase ? `Saldo<br><span>${baseYear} (Basis)</span>` : `Saldo<br><span>${baseYear}</span>`;
          el.title = `Saldo der Relation im Basisjahr ${baseYear}`;
        }
        return;
      }
      if (prevEl) {
        prevEl.innerHTML = 'Δ<br><span>Vorjahr</span>';
        prevEl.title = 'Veränderung gegenüber dem Vorjahr';
      }
      if (el) {
        const compactLabel = isBase ? `ggü. ${baseYear} (Basis)` : `ggü. ${baseYear}`;
        el.innerHTML = `Δ<br><span>${compactLabel}</span>`;
        el.title = `Veränderung gegenüber dem Basisjahr ${baseYear}`;
      }
    });
  }
