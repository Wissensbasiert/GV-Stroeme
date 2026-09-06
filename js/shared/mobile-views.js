  // A mobile view is a presentation choice; it never changes filters or moves cards.
  const mobileAnalysisViews = new Map();
  const mobileAnalysisQuery = window.matchMedia('(max-width: 900px)');

  function refreshMobileAnalysisSize(pane, camera = null) {
    requestAnimationFrame(() => {
      if (!pane.classList.contains('active')) return;
      const map = maps[pane.id.replace('tab-', '')];
      if (pane.querySelector('.map-card-tall')?.getClientRects().length && map) {
        map.invalidateSize({ animate: false, pan: false });
        // Leaflet otherwise rounds the center to whole pixels after reappearance.
        if (camera) map.setView(camera.center, camera.zoom, { animate: false, reset: true });
      }
      pane.querySelectorAll('canvas').forEach(canvas => {
        if (canvas.getClientRects().length) Chart.getChart(canvas)?.resize();
      });
    });
  }

  function setMobileAnalysisView(pane, view, focus = false) {
    const entry = mobileAnalysisViews.get(pane.id);
    if (!entry) return;
    const previousView = entry.view;
    if (mobileAnalysisQuery.matches && previousView === 'map' && view !== 'map') {
      const map = maps[pane.id.replace('tab-', '')];
      if (map) entry.camera = { center: map.getCenter(), zoom: map.getZoom() };
    }
    entry.view = view;
    pane.dataset.mobileView = view;
    entry.buttons.forEach((button, key) => {
      const selected = key === view;
      button.setAttribute('aria-selected', String(selected));
      button.tabIndex = selected ? 0 : -1;
    });
    entry.panels.forEach((panel, key) => {
      const hidden = mobileAnalysisQuery.matches && key !== view;
      panel.inert = hidden;
      if (mobileAnalysisQuery.matches) {
        panel.setAttribute('role', 'tabpanel');
        panel.setAttribute('aria-labelledby', entry.buttons.get(key).id);
        panel.setAttribute('aria-hidden', String(hidden));
      } else {
        panel.removeAttribute('role');
        panel.removeAttribute('aria-labelledby');
        panel.removeAttribute('aria-hidden');
      }
    });
    if (focus) entry.buttons.get(view).focus({ preventScroll: true });
    updateMobileAnalysisContext();
    refreshMobileAnalysisSize(pane, mobileAnalysisQuery.matches && previousView !== 'map' && view === 'map' ? entry.camera : null);
  }

  function mobileAnalysisSelection() {
    const key = state.activeTab.replace('tab-', '');
    const regionLabel = document.getElementById('summaryRegion')?.textContent || 'Deutschland';
    if (key === 'airfreight') return { noun: 'Flughafen', article: 'einen Flughafen', control: 'selectAirfreightAirport', selected: !!state.selectedAirport, label: regionLabel, empty: 'Alle Flughäfen' };
    if (key === 'maritime') return { noun: 'Hafen', article: 'einen Hafen', control: 'selectMaritimePort', selected: !!state.selectedPort, label: regionLabel, empty: 'Alle Häfen' };
    if (key === 'toll') return { noun: 'Gemeinde', article: 'eine Gemeinde', control: 'tollMunicipalitySearchInput', selected: !!state.tollMunicipality, label: regionLabel, empty: 'Keine Gemeinde ausgewählt' };
    return { noun: 'Region', article: 'eine Region', control: 'regionSearchInput', selected: !!state.region, label: regionLabel, empty: 'Deutschland aktiv' };
  }

  function updateMobileAnalysisContext() {
    const entry = mobileAnalysisViews.get(state.activeTab);
    if (!entry) return;
    const selection = mobileAnalysisSelection();
    entry.title.textContent = selection.selected ? `${selection.label} ausgewählt` : selection.empty;
    entry.hint.textContent = selection.selected
      ? `Die Auswahl gilt für alle drei Ansichten. Ändern können Sie sie unter „Aktuell → Raum & Zeit“.`
      : `${selection.noun === 'Gemeinde' ? 'Zoomen Sie in die Karte und tippen' : 'Tippen'} Sie auf ${selection.article} in der Karte oder wählen Sie ${selection.article} unter „Aktuell → Raum & Zeit“. `;
    entry.settings.textContent = selection.selected ? `${selection.noun} ändern` : `${selection.noun} in „Aktuell“ wählen`;
    entry.relations.hidden = !selection.selected || entry.view !== 'map';
  }

  function openMobileAnalysisSettings() {
    const selection = mobileAnalysisSelection();
    const panel = document.getElementById('analysisPanel');
    if (panel.classList.contains('is-collapsed')) document.getElementById('btnToggleAnalysisPanel').click();
    const control = document.getElementById(selection.control);
    control?.scrollIntoView({ block: 'center', behavior: 'auto' });
    control?.focus({ preventScroll: true });
    if (control instanceof HTMLInputElement) control.select();
  }

  function setupMobileAnalysisViews() {
    document.querySelectorAll('.tab-pane').forEach(pane => {
      const grid = pane.querySelector('.module-layout-grid');
      const panels = new Map([
        ['map', pane.querySelector('.map-card-tall')],
        ['relations', pane.querySelector('.table-card-compact')],
        ['charts', pane.querySelector('.bottom-split-charts-row, .chart-card-single')]
      ]);
      if (!grid || [...panels.values()].some(panel => !panel)) return;
      const nav = document.createElement('nav');
      nav.className = 'mobile-analysis-navigation';
      nav.setAttribute('aria-label', 'Mobile Analyseansichten');
      nav.innerHTML = '<div class="mobile-analysis-context"><strong class="mobile-analysis-title"></strong><p class="mobile-analysis-hint"></p><div class="mobile-analysis-actions"><button type="button" class="mobile-analysis-settings"></button><button type="button" class="mobile-analysis-relations" hidden>Relationen ansehen</button></div></div><div class="mobile-analysis-tabs" role="tablist" aria-label="Analyseansicht"></div>';
      grid.before(nav);
      const buttons = new Map();
      for (const [key, label] of [['map', 'Karte'], ['relations', 'Relationen'], ['charts', 'Diagramme']]) {
        const panel = panels.get(key);
        panel.dataset.mobileViewPanel = key;
        if (!panel.id) panel.id = `${pane.id}-${key}-panel`;
        const button = document.createElement('button');
        button.type = 'button';
        button.id = `${pane.id}-view-${key}`;
        button.dataset.view = key;
        button.textContent = label;
        button.setAttribute('role', 'tab');
        button.setAttribute('aria-controls', panel.id);
        button.addEventListener('click', () => setMobileAnalysisView(pane, key));
        buttons.set(key, button);
        nav.querySelector('.mobile-analysis-tabs').append(button);
      }
      nav.querySelector('.mobile-analysis-tabs').addEventListener('keydown', event => {
        const keys = [...buttons.keys()], index = keys.indexOf(event.target.dataset.view);
        if (index < 0 || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
        event.preventDefault();
        const next = event.key === 'Home' ? 0 : event.key === 'End' ? keys.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + keys.length) % keys.length;
        setMobileAnalysisView(pane, keys[next], true);
      });
      const entry = { pane, panels, buttons, view: 'map', title: nav.querySelector('.mobile-analysis-title'), hint: nav.querySelector('.mobile-analysis-hint'), settings: nav.querySelector('.mobile-analysis-settings'), relations: nav.querySelector('.mobile-analysis-relations') };
      entry.settings.addEventListener('click', openMobileAnalysisSettings);
      entry.relations.addEventListener('click', () => setMobileAnalysisView(pane, 'relations', true));
      mobileAnalysisViews.set(pane.id, entry);
      setMobileAnalysisView(pane, 'map');
    });
    mobileAnalysisQuery.addEventListener('change', () => {
      mobileAnalysisViews.forEach(entry => setMobileAnalysisView(entry.pane, entry.view));
    });
  }
