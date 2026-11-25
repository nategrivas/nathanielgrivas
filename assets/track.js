// Visitor activity: pages, taps on intent buttons, search answers, and where they came from.
// Sent to Nate with any form, on Call/Text/Email taps, and as one summary when a visitor with intent leaves.
(() => {
  const TO = (document.querySelector('meta[name=ng-to]') || {}).content;
  if (!TO) return;
  const URL_ = 'https://formsubmit.co/ajax/' + TO;
  const now = () => Date.now();
  const ls = (k, v) => { try { if (v === undefined) return JSON.parse(localStorage.getItem(k) || 'null'); localStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } return v; };
  const ss = (k, v) => { try { if (v === undefined) return JSON.parse(sessionStorage.getItem(k) || 'null'); sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } return v; };
  const gpc = navigator.globalPrivacyControl === true;

  // visitor (kept across visits) and session (this visit)
  const q = new URLSearchParams(location.search);
  const utm = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'].map((k) => q.get(k)).filter(Boolean).join(' / ');
  const ad = q.get('gclid') ? 'Google Ads click' : q.get('fbclid') ? 'Facebook/Instagram click' : q.get('msclkid') ? 'Microsoft Ads click' : '';
  let ref = document.referrer && !document.referrer.includes(location.host) ? document.referrer.replace(/^https?:\/\//, '').split('/')[0] : '';
  let V = ls('ng_v');
  let S = ss('ng_s');
  if (!V) V = { id: Math.random().toString(36).slice(2, 8), first: now(), visits: 0, firstSource: '' };
  if (!S) {
    V.visits += 1;
    S = { start: now(), landing: location.pathname, source: [ref, utm, ad].filter(Boolean).join(' · ') || 'direct (typed the address or a bookmark)', pages: [], taps: [], answers: {}, sent: [], signals: 0, lastSent: 0, done: false };
    if (!V.firstSource) V.firstSource = S.source;
  }
  V.last = now();
  ls('ng_v', V);
  S.pages.push({ p: location.pathname + (location.search && !utm ? location.search : ''), t: now(), d: 0 });
  const save = () => ss('ng_s', S);
  save();

  const ua = navigator.userAgent;
  const device = [
    /iPhone/.test(ua) ? 'iPhone' : /iPad/.test(ua) ? 'iPad' : /Android/.test(ua) ? 'Android' : /Mac/.test(ua) ? 'Mac' : /Windows/.test(ua) ? 'Windows' : 'Other',
    /Edg\//.test(ua) ? 'Edge' : /CriOS|Chrome\//.test(ua) ? 'Chrome' : /Safari\//.test(ua) ? 'Safari' : /Firefox/.test(ua) ? 'Firefox' : 'Browser',
    innerWidth + 'px wide', navigator.language, Intl.DateTimeFormat().resolvedOptions().timeZone,
  ].join(' · ');

  const dur = (ms) => { const s = Math.round(ms / 1000); return s < 60 ? s + 's' : Math.floor(s / 60) + 'm ' + (s % 60) + 's'; };
  const fmtDate = (t) => new Date(t).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
  const touchPage = () => { const p = S.pages[S.pages.length - 1]; if (p) p.d = now() - p.t; };

  const journey = () => {
    touchPage();
    const pages = S.pages.map((p) => p.p + (p.d > 4000 ? ' (' + dur(p.d) + ')' : '')).join('  >  ');
    const taps = S.taps.map((t) => t.what + ' [' + t.where + ']').join('  |  ');
    const ans = Object.entries(S.answers).map(([k, v]) => k + ': ' + v).join('  |  ');
    return {
      visitor: 'V-' + V.id + ' · visit ' + V.visits + ' · first seen ' + fmtDate(V.first),
      came_from: S.source + (V.visits > 1 && V.firstSource !== S.source ? ' (first visit from ' + V.firstSource + ')' : ''),
      landing_page: S.landing,
      device,
      time_on_site: dur(now() - S.start),
      pages_viewed: pages || '-',
      buttons_tapped: taps || '-',
      search_answers: ans || '-',
    };
  };

  const send = (subject, extra) => {
    const body = new URLSearchParams({ _subject: subject, _template: 'table', _captcha: 'false', ...journey(), ...(extra || {}) });
    try {
      fetch(URL_, { method: 'POST', body, keepalive: true, mode: 'no-cors', headers: { Accept: 'application/json' } }).catch(() => { if (navigator.sendBeacon) navigator.sendBeacon(URL_, body); });
    } catch (e) { if (navigator.sendBeacon) navigator.sendBeacon(URL_, body); }
  };

  const label = (el) => (el.getAttribute('aria-label') || el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60);
  const where = () => location.pathname;
  const tap = (what, strong) => {
    S.taps.push({ what, where: where(), t: now() });
    S.signals += strong ? 2 : 1;
    save();
  };

  // high-intent taps get an immediate alert, once per kind per visit
  const instant = (kind, what) => {
    if (gpc || S.sent.includes(kind)) return;
    S.sent.push(kind); S.lastSent = S.signals; save();
    send('Website: someone tapped ' + what + ' on ' + where(), { alert: 'Tapped ' + what + ' at ' + fmtDate(now()) });
  };

  document.addEventListener('click', (ev) => {
    const a = ev.target.closest('a,button');
    if (!a) return;
    const href = a.getAttribute('href') || '';
    if (href.startsWith('tel:')) { tap('Call', true); instant('call', 'Call'); return; }
    if (href.startsWith('sms:')) { tap('Text', true); instant('text', 'Text'); return; }
    if (href.startsWith('mailto:')) { tap('Email', true); instant('email', 'Email'); return; }
    if (a.closest('.goals')) return tap('I want to: ' + label(a), true);
    if (href.includes('neighborhood-quiz')) return tap(label(a) || 'Start search', true);
    if (a.matches('.card')) return tap('Listing: ' + label(a.querySelector('.addr') || a), true);
    if (href.includes('orbrodskygroup')) return tap('Brodsky Group site');
    if (a.matches('.place')) return tap('Place: ' + label(a.querySelector('b') || a));
    if (a.matches('.tile')) return tap('Neighborhood: ' + label(a.querySelector('h3') || a));
    if (a.matches('.g')) return tap('Photo: ' + (a.dataset.alt || ''));
    if (a.matches('[data-tab]')) return tap('Tab: ' + label(a));
  }, true);

  // summary when a visitor with intent leaves or switches away
  const summary = () => {
    if (gpc || S.done || S.signals === 0 || S.signals === S.lastSent) return;
    const n = Object.keys(S.answers).length;
    if (S.signals < 2 && n === 0) return;
    if (S.sent.filter((k) => k.startsWith('sum')).length >= 3) return;
    S.sent.push('sum' + S.sent.length); S.lastSent = S.signals; save();
    const goal = S.answers.Goal ? ' (' + S.answers.Goal + (S.answers.Budget ? ', ' + S.answers.Budget : '') + ')' : '';
    send(n ? 'Website: unfinished search' + goal : 'Website: visitor activity', { alert: n ? 'Answered ' + n + ' search questions but did not send the form' : 'Showed interest but did not reach out' });
  };
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') { touchPage(); save(); summary(); } });
  addEventListener('pagehide', () => { touchPage(); save(); summary(); });

  window.NG = {
    journey,
    answer(k, v) { S.answers[k] = v; S.signals += 1; save(); },
    submitted() { S.done = true; S.lastSent = S.signals; save(); },
  };
})();
