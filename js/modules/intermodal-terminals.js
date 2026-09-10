  // Independent infrastructure overlay, with a minimal, prefiltered delivery file.
  const INTERMODAL_MAP_URL = 'https://www.intermodal-map.com/';
  let intermodalTerminalLayer = null;
  let terminalTooltip = null;
  let terminalTooltipTimer = null;

  function terminalInformation(properties) {
    const content = document.createElement('div');
    content.className = 'kv-terminal-information';
    const name = document.createElement('strong');
    name.textContent = properties.name;
    const kind = document.createElement('div');
    kind.className = 'kv-terminal-function';
    kind.textContent = properties.function;
    const note = document.createElement('p');
    note.textContent = 'Weitere Daten zum Betreiber, zur Ausstattung und zu Verbindungen finden Sie direkt in der Intermodal Map der SGKV.';
    const link = document.createElement('a');
    link.href = INTERMODAL_MAP_URL;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = 'Intermodal Map öffnen ↗';
    const reference = document.createElement('div');
    reference.className = 'kv-terminal-reference';
    reference.append(note, link);
    content.append(name, kind, reference);
    return content;
  }

  function closeTerminalTooltip() {
    clearTimeout(terminalTooltipTimer);
    if (terminalTooltip) maps.intermodal?.removeLayer(terminalTooltip);
    terminalTooltip = null;
  }

  function syncIntermodalTerminalLegend() {
    const body = document.querySelector('#intermodalMapLegend .legend-body');
    if (!body) return;
    body.querySelector('.kv-terminal-legend')?.remove();
    if (!state.showIntermodalTerminals || !intermodalTerminalLayer || !maps.intermodal?.hasLayer(intermodalTerminalLayer)) return;
    const row = document.createElement('div');
    row.className = 'kv-terminal-legend legend-spider-item';
    row.innerHTML = '<span class="kv-terminal-swatch" aria-hidden="true"></span><span>KV-Terminals · Deutschland</span>';
    body.appendChild(row);
  }

  function syncIntermodalTerminalButton() {
    const show = state.showIntermodalTerminals;
    document.getElementById('toggleIntermodalTerminals')?.setAttribute('aria-pressed', String(show));
    const hint = document.getElementById('intermodalTerminalToggleHint');
    if (hint) hint.textContent = show ? 'Terminals ausblenden' : 'Terminals anzeigen';
  }

  async function renderIntermodalTerminals() {
    const map = maps.intermodal;
    const button = document.getElementById('toggleIntermodalTerminals');
    const status = document.getElementById('intermodalTerminalStatus');
    if (!map || !button || !status) return;
    const show = state.showIntermodalTerminals;
    syncIntermodalTerminalButton();
    if (!show) {
      closeTerminalTooltip();
      if (intermodalTerminalLayer) map.removeLayer(intermodalTerminalLayer);
      syncIntermodalTerminalLegend();
      status.hidden = true;
      return;
    }
    try {
      if (!intermodalTerminalLayer) {
        status.hidden = false;
        status.textContent = 'Terminals werden geladen …';
        const data = await requestDataOnce('intermodal-terminals', async () => {
          const result = await fetchJson('data/processed/web_intermodal_terminals.geojson');
          if (result?.type !== 'FeatureCollection' || !result.features?.length) throw new Error('Invalid terminal data');
          return result;
        });
        // Multiple renders can await the same request. Only build one layer.
        if (!intermodalTerminalLayer) {
          const icon = L.divIcon({ className: 'kv-terminal-marker',
            html: '<span aria-hidden="true"></span>', iconSize: [12, 9], iconAnchor: [6, 4.5] });
          intermodalTerminalLayer = L.geoJSON(data, {
            pointToLayer: (feature, latlng) => {
              const marker = L.marker(latlng, { icon, title: feature.properties.name,
                alt: feature.properties.name, keyboard: true, riseOnHover: true });
              marker.bindPopup(() => {
                const height = map.getSize().y;
                const popup = marker.getPopup();
                popup.options.maxHeight = Math.max(70, Math.min(260, height - 100));
                popup.options.autoPanPaddingTopLeft = [16, height < 320 ? 16 : 50];
                return terminalInformation(feature.properties);
              }, {
                maxWidth: 280, maxHeight: 260, keepInView: true,
                autoPanPaddingTopLeft: [16, 50], autoPanPaddingBottomRight: [16, 16]
              });
              marker.on('mouseover', () => {
                closeTerminalTooltip();
                if (marker.isPopupOpen()) return;
                const content = terminalInformation(feature.properties);
                content.addEventListener('mouseenter', () => clearTimeout(terminalTooltipTimer));
                content.addEventListener('mouseleave', closeTerminalTooltip);
                terminalTooltip = L.tooltip({ direction: 'top', offset: [0, -10],
                  interactive: true, opacity: 1, className: 'kv-terminal-tooltip' })
                  .setLatLng(latlng).setContent(content).addTo(map);
              });
              marker.on('mouseout', () => { terminalTooltipTimer = setTimeout(closeTerminalTooltip, 250); });
              marker.on('click', closeTerminalTooltip);
              return marker;
            }
          });
          intermodalTerminalLayer.on('remove', closeTerminalTooltip);
          map.on('zoomstart movestart', closeTerminalTooltip);
          map.on('resize', () => intermodalTerminalLayer.eachLayer(marker => {
            if (marker.isPopupOpen()) marker.getPopup().update();
          }));
        }
      }
      if (state.showIntermodalTerminals) intermodalTerminalLayer.addTo(map);
      syncIntermodalTerminalLegend();
      status.hidden = true;
    } catch (error) {
      console.warn('Could not load KV terminals:', error);
      if (!state.showIntermodalTerminals) return;
      state.showIntermodalTerminals = false;
      syncIntermodalTerminalButton();
      syncIntermodalTerminalLegend();
      status.hidden = false;
      status.textContent = 'Terminals konnten nicht geladen werden. Zum erneuten Laden „Terminals“ einschalten.';
    }
  }
