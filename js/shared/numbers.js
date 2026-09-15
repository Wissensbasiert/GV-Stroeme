  // German Number Formatter Helper
  function formatDeNum(val, maxDecimals = 1, minDecimals = 0) {
    if (val === null || val === undefined || !Number.isFinite(Number(val))) return '--';
    return Number(val).toLocaleString('de-DE', {
      minimumFractionDigits: minDecimals,
      maximumFractionDigits: maxDecimals
    });
  }

  function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  }

  // KPI precision follows the displayed unit, not the unscaled source value.
  function formatKpiNumber(value) {
    if (value === null || value === undefined || !Number.isFinite(Number(value))) return '--';
    const number = Number(value), absolute = Math.abs(number);
    if (absolute === 0) return '0';
    const decimals = absolute >= 100 ? 0 : absolute >= 1 ? 1 : Math.max(1, 1 - Math.floor(Math.log10(absolute)));
    if (decimals > 10) return number.toLocaleString('de-DE', { notation: 'scientific', maximumFractionDigits: 1 });
    return formatDeNum(number, decimals);
  }

  // Keep adjacent axis ticks distinguishable, including sub-unit and signed scales.
  function formatChartAxisTick(value, index, ticks) {
    const values = (ticks || []).map(tick => Number(tick.value)).filter(Number.isFinite).sort((a, b) => a - b);
    const gaps = values.slice(1).map((v, i) => v - values[i]).filter(gap => gap > 0);
    const step = gaps.length ? Math.min(...gaps) : Math.abs(Number(value));
    if (!step || Math.abs(Number(value)) < step * 1e-8) return '0';
    let decimals = Math.max(0, Math.ceil(-Math.log10(step)));
    while (decimals < 10 && Math.abs(step * 10 ** decimals - Math.round(step * 10 ** decimals)) > 1e-7) decimals++;
    if (decimals > 10) return Number(value).toLocaleString('de-DE', { notation: 'scientific', maximumFractionDigits: 2 });
    return formatDeNum(value, decimals);
  }

  // Quantities use one decimal place by default. Very small non-zero values
  // retain further precision so an existing relation never appears as zero.
  function formatQuantity(val, standardDecimals = 1) {
    if (val === null || val === undefined || isNaN(val)) return '--';
    const absolute = Math.abs(Number(val));
    const decimals = absolute > 0 && absolute < 0.01 ? 3 : (absolute > 0 && absolute < 0.1 ? 2 : standardDecimals);
    return formatDeNum(val, decimals, decimals);
  }

  // Verkehrsleistungen behalten in einer Ansicht die etablierte Einheit. Bei
  // sehr kleinen positiven tkm-Werten wird nur so weit präzisiert, wie es
  // lesbar bleibt; darunter steht ein begrenzter, aber nicht irreführend
  // gerundeter Wert.
  function formatTkmQuantity(val, standardDecimals = 1, fixedDecimals = false) {
    if (val === null || val === undefined || isNaN(val)) return '--';
    const numeric = Number(val);
    const absolute = Math.abs(numeric);
    if (absolute === 0) return formatDeNum(0, standardDecimals, fixedDecimals ? standardDecimals : 0);
    if (absolute < 0.000001) {
      return `${numeric < 0 ? '−' : ''}<${formatDeNum(0.000001, 6, 6)}`;
    }
    const decimals = absolute < 0.00001 ? 6
      : absolute < 0.0001 ? 5
      : absolute < 0.001 ? 4
      : absolute < 0.01 ? 3
      : absolute < 0.1 ? 2
      : standardDecimals;
    const finalDecimals = Math.max(standardDecimals, decimals);
    return formatDeNum(numeric, finalDecimals, fixedDecimals ? finalDecimals : 0);
  }

  function formatTrafficValue(val, unit, standardDecimals = 1) {
    return String(unit).includes('tkm')
      ? formatTkmQuantity(val, standardDecimals)
      : formatDeNum(val, standardDecimals);
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
    return ` ${context.dataset.label}: ${formatTrafficValue(value, unitText, 2)} ${unitText} (${share} %${suffix})`;
  }

  // Tables specify one scale for every row; compact values must carry a unit.
  function formatFixedUnitValue(value, { divisor = 1, decimals = 1, signed = false } = {}) {
    if (value === null || value === undefined || !Number.isFinite(Number(value))) return '--';
    const number = Number(value) / divisor;
    return `${signed && number > 0 ? '+' : ''}${formatDeNum(number, decimals)}`;
  }
