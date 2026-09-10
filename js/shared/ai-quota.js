  // Local interface preview only. The future server must enforce account quotas.
  const AI_PREVIEW_MONTHLY_LIMIT = 50;
  const AI_PREVIEW_QUOTA_KEY = 'wbp.ai-preview-quota.v1';
  let aiPreviewQuota = null;

  function currentAiQuotaMonth(date = new Date()) {
    const parts = new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Berlin', year: 'numeric', month: '2-digit' }).formatToParts(date);
    return `${parts.find(p => p.type === 'year').value}-${parts.find(p => p.type === 'month').value}`;
  }

  function readAiPreviewQuota() {
    const month = currentAiQuotaMonth();
    if (!aiPreviewQuota) {
      try { aiPreviewQuota = JSON.parse(sessionStorage.getItem(AI_PREVIEW_QUOTA_KEY)); } catch { /* Storage may be unavailable. */ }
    }
    if (!aiPreviewQuota || aiPreviewQuota.month !== month || !Number.isInteger(aiPreviewQuota.used)
        || aiPreviewQuota.used < 0 || aiPreviewQuota.used > AI_PREVIEW_MONTHLY_LIMIT) {
      aiPreviewQuota = { month, used: 0 };
    }
    return aiPreviewQuota;
  }

  function refreshAiPreviewQuota() {
    const quota = readAiPreviewQuota();
    const full = quota.used >= AI_PREVIEW_MONTHLY_LIMIT;
    const label = document.getElementById('aiQuotaLabel');
    const bar = document.getElementById('aiQuotaProgress');
    const hint = document.getElementById('aiQuotaHint');
    if (label) label.textContent = `${quota.used} von ${AI_PREVIEW_MONTHLY_LIMIT} Fragen`;
    if (bar) { bar.max = AI_PREVIEW_MONTHLY_LIMIT; bar.value = quota.used; }
    if (hint) hint.textContent = full
      ? `${quota.used} von ${AI_PREVIEW_MONTHLY_LIMIT} Fragen genutzt. Das Monatskontingent ist ausgeschöpft.`
      : `${quota.used} von ${AI_PREVIEW_MONTHLY_LIMIT} Fragen des Monatskontingents genutzt. Zum nächsten Kalendermonat stehen wieder ${AI_PREVIEW_MONTHLY_LIMIT} Fragen zur Verfügung.`;
    const submit = document.querySelector('#aiQuestionForm button[type="submit"]');
    if (submit) submit.disabled = full;
    return quota;
  }

  function consumeAiPreviewQuestion() {
    const quota = refreshAiPreviewQuota();
    if (quota.used >= AI_PREVIEW_MONTHLY_LIMIT) return false;
    quota.used += 1;
    try { sessionStorage.setItem(AI_PREVIEW_QUOTA_KEY, JSON.stringify(quota)); } catch { /* Session-only fallback. */ }
    refreshAiPreviewQuota();
    return true;
  }
