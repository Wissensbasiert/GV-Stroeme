  // Complete monthly responses, cached only within this browser session.
  const tollMonthlyCache = new Map();
  let tollAvailableMonths = [];
  let tollComparison = { status: 'idle', month: null, rows: new Map() };
  const TOLL_CACHE_TTL_MS = 15 * 60 * 1000;

  function previousTollYearMonth(month) {
    const match = /^(\d{4})-(\d{2})$/.exec(String(month || ''));
    return match ? `${Number(match[1]) - 1}-${match[2]}` : null;
  }

  function latestTollComparableMonth(months = tollAvailableMonths) {
    const available = new Set(months);
    return [...available].filter(month => available.has(previousTollYearMonth(month))).sort().at(-1) || null;
  }
  function tollComparisonAvailabilityHint() {
    const latest = latestTollComparableMonth();
    if (!latest) return 'Für die veröffentlichten Monate ist derzeit kein Vorjahresvergleich möglich.';
    const label = new Intl.DateTimeFormat('de-DE', { month: 'long', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${latest}-01T00:00:00Z`));
    return `Letzter verfügbarer Berichtsmonat mit Vorjahresvergleich: ${label}.`;
  }

  function compareTollValues(current, previous) {
    if (current === null || previous === null || !Number.isFinite(current) || !Number.isFinite(previous)) return null;
    return { current, previous, absolute: current - previous, percent: previous === 0 ? null : (current - previous) / previous * 100 };
  }

  async function getTollMonthlySnapshot(scope, signal) {
    const key = `${scope.municipality}|${scope.month}|${scope.direction}`;
    const cached = tollMonthlyCache.get(key);
    if (cached && Date.now() - cached.fetchedAtMs < TOLL_CACHE_TTL_MS) return cached;
    const features = await fetchTollRelations(scope, signal);
    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
    const snapshot = { ...scope, fetchedAt: new Date().toISOString(), fetchedAtMs: Date.now(), rows: normalizeTollFeatures(features, scope), complete: true };
    tollMonthlyCache.set(key, snapshot);
    while (tollMonthlyCache.size > 24) tollMonthlyCache.delete(tollMonthlyCache.keys().next().value);
    return snapshot;
  }

  function updateTollComparisonNotice() {
    const notice = document.getElementById('tollComparisonNotice');
    if (!notice) return;
    notice.hidden = !state.tollMunicipality || !state.tollMonth || tollApiFailed || !['loading', 'error'].includes(tollComparison.status);
    const month = formatTollMonth(tollComparison.month);
    const text = {
      loading: `Vorjahresvergleich ${month} wird geladen …`,
      available: `Vorjahresvergleich zu ${month}: Werte in den Gemeinde- und Verbindungsinformationen.`,
      unavailable: `Vorjahresvergleich: ${month} ist in der API nicht verfügbar.`,
      error: `Vorjahresvergleich ${month} konnte nicht geladen werden. Die aktuellen Werte bleiben verfügbar.`
    }[tollComparison.status] || '';
    notice.replaceChildren(document.createTextNode(text));
    if (tollComparison.status === 'error') {
      const retry = document.createElement('button');
      retry.className = 'btn-header'; retry.type = 'button'; retry.textContent = 'Vergleich erneut laden';
      retry.addEventListener('click', () => loadTollComparison({ municipality: state.tollMunicipality, month: state.tollMonth, direction: state.tollDirection }, tollRequestSequence, tollRelationsController?.signal));
      notice.append(retry);
    }
  }

  async function loadTollComparison(scope, requestId, signal) {
    const month = previousTollYearMonth(scope.month);
    tollComparison = { status: tollAvailableMonths.includes(month) ? 'loading' : 'unavailable', month, rows: new Map() };
    updateTollComparisonNotice();
    if (tollComparison.status === 'unavailable') return;
    try {
      const snapshot = await getTollMonthlySnapshot({ ...scope, month }, signal);
      if (requestId !== tollRequestSequence) return;
      tollComparison = { status: 'available', month, rows: new Map(snapshot.rows.map(row => [row.partnerAgs, row])), fetchedAt: snapshot.fetchedAt };
    } catch (error) {
      if (requestId !== tollRequestSequence) return;
      tollComparison = { status: 'error', month, rows: new Map() };
      console.warn('Previous-year Toll data unavailable:', error);
    }
    updateTollComparisonNotice();
  }

  function getTollComparisonForRow(row, metric = state.tollMetric) {
    if (tollComparison.status !== 'available') return null;
    const previous = tollComparison.rows.get(row.partnerAgs);
    if (!previous) return null;
    const field = TOLL_METRICS[metric]?.field || 'trips';
    return compareTollValues(row[field], previous[field]);
  }

  function buildTollComparisonTooltip(row) {
    const month = formatTollMonth(tollComparison.month);
    if (!tollComparison.month) return '';
    const result = getTollComparisonForRow(row);
    let body;
    if (tollComparison.status === 'loading') body = 'Vergleich wird geladen …';
    else if (tollComparison.status === 'error') body = 'Vergleichsdaten konnten nicht geladen werden.';
    else if (tollComparison.status === 'unavailable') body = `Dieser Vorjahresmonat ist nicht verfügbar. ${tollComparisonAvailabilityHint()}`;
    else if (!result) body = 'Kein vergleichbarer Vorjahreswert für diese Relation veröffentlicht.';
    else {
      const metric = TOLL_METRICS[state.tollMetric] || TOLL_METRICS.trips;
      const decimals = ['distance', 'time'].includes(state.tollMetric) ? 1 : 0;
      const percent = result.percent === null ? 'Prozentänderung nicht berechenbar (Vorjahreswert 0)' : `${formatFixedUnitValue(result.percent, { decimals: 1, signed: true })} %`;
      const arrow = result.absolute > 0 ? '↗' : result.absolute < 0 ? '↘' : '→';
      const color = result.absolute > 0 ? '#16a34a' : result.absolute < 0 ? '#dc2626' : '#64748b';
      body = `${metric.label}: ${formatDeNum(result.previous, decimals)} ${metric.unit}<br>Veränderung: <span style="color:${color};"><strong>${arrow} ${formatFixedUnitValue(result.absolute, { decimals, signed: true })} ${metric.unit}</strong> · ${percent}</span>`;
    }
    return `<div class="toll-comparison-tooltip"><strong>Vorjahresmonat ${escapeTollHtml(month)}</strong><br>${body}</div>`;
  }

