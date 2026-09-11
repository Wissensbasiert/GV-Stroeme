  // Portal-backed assistant. There is no browser-side billing or model key.
  function createAiClient() {
    const el = id => document.getElementById(id);
    const input = el('aiQuestionInput');
    const form = el('aiQuestionForm');
    const send = form?.querySelector('button[type="submit"]');
    const base = '/api/tools/gueterstroeme';
    const connected = document.querySelector('meta[name="wbp-gueterstroeme-assistant"]')?.content === base;
    let quota = null, csrf = '', busy = false, uncertain = false, followup = null, history = [], conversation = null;
    const node = (tag, text, className) => {
      const value = document.createElement(tag);
      if (text !== undefined) value.textContent = String(text);
      if (className) value.className = className;
      return value;
    };
    const notice = message => { const status = el('aiStatusNotice'); status.textContent = message; status.hidden = !message; };
    const updateSend = () => { if (send) send.disabled = !connected || busy || uncertain || !quota || quota.remaining <= 0; if (el('aiNewChat')) el('aiNewChat').disabled = busy || uncertain; };
    const message = (kind, content) => {
      const conversation = el('aiConversation');
      conversation.closest('.ki-modal-body')?.classList.add('has-conversation');
      const article = node('article', undefined, `ki-message ki-message-${kind}`);
      const avatar = node('div', kind === 'user' ? 'Sie' : '', 'ki-message-avatar');
      if (kind !== 'user') {
        const icon = node('img'); icon.src = 'assets/icons/gueterstrom-ki-variante-c-datenkorridor.svg'; icon.alt = '';
        avatar.append(icon);
      }
      const body = node('div', undefined, 'ki-message-content');
      body.append(typeof content === 'string' ? node('p', content) : content);
      article.append(avatar, body); conversation.append(article);
      conversation.scrollTop = conversation.scrollHeight;
      return article;
    };
    async function jsonRequest(url, options = {}, timeout = 15000) {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), timeout);
      try {
        const response = await fetch(url, { credentials: 'same-origin', cache: 'no-store', ...options, signal: controller.signal });
        const body = await response.json();
        if (!response.ok) {
          const error = new Error(body.error || 'Die Anfrage konnte nicht ausgeführt werden.');
          error.status = response.status; error.requestId = body.request_id; throw error;
        }
        return body;
      } finally { clearTimeout(timer); }
    }
    async function refreshQuota() {
      if (!connected) {
        el('aiQuotaLabel').textContent = 'Keine Portalverbindung';
        el('aiQuotaProgress').hidden = true;
        notice('Der Analyseassistent ist über das freigeschaltete Kundenkonto im Portal verfügbar.');
        updateSend(); return;
      }
      try {
        const current = await jsonRequest(base + '/quota');
        if (!['basic', 'premium'].includes(current.plan) || !['limit','used','reserved','remaining'].every(k => Number.isInteger(current[k]) && current[k] >= 0) || typeof current.csrf_token !== 'string' || !current.csrf_token) throw new Error('Das Kontingent konnte nicht geprüft werden.');
        quota = current; csrf = current.csrf_token;
        el('aiQuotaLabel').textContent = `${current.used} von ${current.limit} Fragen · ${current.remaining} verfügbar`;
        el('aiQuotaProgress').hidden = false;
        el('aiQuotaProgress').max = current.limit; el('aiQuotaProgress').value = current.used;
        el('aiQuotaHint').textContent = `${current.plan === 'basic' ? 'Basic' : 'Premium'} · ${current.month}: ${current.used} genutzt, ${current.reserved} in Bearbeitung. Gezählt werden erfolgreiche numerische Auswertungen. Rückfragen zählen nicht. Zum nächsten Kalendermonat beginnt das Kontingent neu.`;
        if (!busy && !uncertain) notice(current.remaining > 0 ? '' : 'Ihr Monatskontingent ist ausgeschöpft oder durch laufende Anfragen belegt.');
      } catch (error) {
        quota = null; csrf = '';
        el('aiQuotaLabel').textContent = 'Kontingent nicht verfügbar'; el('aiQuotaProgress').hidden = true;
        notice(error.status === 401 ? 'Bitte melden Sie sich erneut im Portal an.' : error.status === 403 ? 'Für Ihr Konto ist der KI-Zugang noch nicht freigegeben.' : 'Das Kontingent konnte gerade nicht geladen werden. Bitte öffnen Sie den Assistenten später erneut.');
      }
      updateSend();
    }
    function prepare(text, action = null) {
      if (busy) return;
      input.value = text; followup = action;
      input.dispatchEvent(new Event('input')); input.focus();
    }
    function render(result) {
      const answer = result.answer;
      if (!answer || !Array.isArray(answer.paragraphs) || !Array.isArray(answer.tables)) throw new Error('Die Antwort konnte nicht dargestellt werden.');
      const fragment = document.createDocumentFragment();
      fragment.append(node('h4', answer.title));
      answer.paragraphs.forEach(text => fragment.append(node('p', text)));
      if (answer.questions?.length) {
        const list = node('ul'); answer.questions.forEach(text => list.append(node('li', text))); fragment.append(list);
        const hint = node('p', 'Antworten Sie einfach hier im Chat. Die bisherigen Angaben bleiben berücksichtigt.', 'ki-message-meta'); fragment.append(hint);
      }
      if (answer.replies?.length) {
        const replies = node('div', undefined, 'ki-suggestions');
        answer.replies.forEach(reply => { const button = node('button', reply.label, 'ki-suggestion'); button.type = 'button'; button.addEventListener('click', () => prepare(reply.question)); replies.append(button); });
        fragment.append(replies);
      }
      for (const table of answer.tables) {
        const wrapper = node('div', undefined, 'ki-answer-table');
        const element = node('table'); element.append(node('caption', table.title));
        const head = node('thead'), header = node('tr');
        table.columns.forEach(label => { const th = node('th', label); th.scope = 'col'; header.append(th); });
        head.append(header); element.append(head);
        const body = node('tbody');
        for (const row of table.rows) {
          const tr = node('tr'); ['label','value','unit','note'].forEach(key => tr.append(node('td', row[key] || ''))); body.append(tr);
        }
        element.append(body); wrapper.append(element); fragment.append(wrapper);
      }
      if (answer.notes?.length) {
        const list = node('ul', undefined, 'ki-answer-notes'); answer.notes.forEach(text => list.append(node('li', text))); fragment.append(list);
      }
      if (answer.suggestions?.length) {
        const choices = node('div', undefined, 'ki-suggestions');
        fragment.append(node('strong', 'Passende Folgefragen'));
        answer.suggestions.forEach((text, index) => {
          const button = node('button', text, 'ki-suggestion'); button.type = 'button';
          button.addEventListener('click', () => prepare(text, answer.followups?.[index] || null)); choices.append(button);
        });
        fragment.append(choices);
      }
      return message('assistant', fragment);
    }
    async function submit() {
      const question = input.value.trim();
      if (!question || busy || uncertain || !quota || quota.remaining <= 0 || !connected) { input.focus(); return; }
      const action = followup;
      const confirmed = action?.parameters || {};
      const payload = { question, confirmed, request_id: crypto.randomUUID() };
      if (action?.function_id) payload.function = action.function_id;
      else if (conversation) payload.conversation = conversation;
      else if (history.length) payload.history = history.slice();
      busy = true; updateSend(); input.disabled = true; form.setAttribute('aria-busy', 'true');
      message('user', question);
      input.value = ''; input.style.height = ''; followup = null;
      el('aiWorking').hidden = false;
      const waiting = message('assistant', 'Ich prüfe Ihre Frage und die verfügbaren Daten …');
      let rendered = null;
      try {
        const result = await jsonRequest(base + '/analysis', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-WBP-CSRF-Token': csrf }, body: JSON.stringify(payload) }, 210000);
        rendered = render(result);
        conversation = typeof result.conversation === 'string' ? result.conversation : null;
        history = [...(action ? [] : history), question].slice(-6);
        while (history.reduce((sum, text) => sum + text.length, 0) > 6000) history.shift();
      } catch (error) {
        uncertain = !error.status || !!error.requestId;
        rendered = message('assistant', uncertain ? 'Die Antwort ist nicht vollständig angekommen. Die Anfrage kann dennoch bearbeitet und gezählt worden sein. Bitte senden Sie sie nicht erneut. Laden Sie die Seite später neu und prüfen Sie Ihr Kontingent. Anfragekennung: ' + payload.request_id : error.message);
      } finally {
        waiting.remove(); el('aiWorking').hidden = true; rendered?.scrollIntoView({ block: 'start' }); busy = false; input.disabled = false; form.setAttribute('aria-busy', 'false');
        await refreshQuota(); updateSend(); input.focus();
        if (uncertain) notice('Der Abschluss der letzten Anfrage ist unklar. Eine automatische Wiederholung erfolgt nicht.');
      }
    }
    input.addEventListener('input', () => { if (followup && input.value.trim() !== followup.question) { followup = null; } });
    el('aiNewChat')?.addEventListener('click', () => {
      if (busy || uncertain) return;
      history = []; conversation = null; followup = null; input.value = ''; input.style.height = '';
      el('aiConversation').replaceChildren();
      el('aiConversation').closest('.ki-modal-body').classList.remove('has-conversation');
      notice(''); input.focus();
    });
    updateSend();
    return { submit, prepare, open: refreshQuota };
  }
