// Two lead flows, one tap at a time: "value" (what's my home worth) and "buy" (find me a home).
// The lead is sent the moment they give contact info; the questions after that sharpen it and go out as a second note.
(() => {
  const TO = (document.querySelector('meta[name=ng-to]') || {}).content;
  const roots = document.querySelectorAll('[data-flow]');
  if (!roots.length) return;
  const PHONE = '310-269-5541', TEL = '+13102695541';
  const esc = (t) => String(t == null ? '' : t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const q = new URLSearchParams(location.search);

  const AREAS = [['Westside', 'Westside'], ['Beverly Hills & the Hills', 'Beverly Hills & the hills'], ['Coast', 'The coast'], ['Central', 'Hollywood & Mid-City'], ['Eastside', 'Silver Lake, Los Feliz, Echo Park'], ['Valley', 'The Valley']];
  const WHEN = [['ASAP', 'As soon as possible'], ['1-3 months', 'In 1 to 3 months'], ['3-6 months', 'In 3 to 6 months'], ['6-12 months', 'In 6 to 12 months'], ['Just curious', 'Just curious for now']];

  const FLOWS = {
    value: {
      kind: 'Home value request',
      steps: [
        { k: 'address', t: 'text', q: "What's the address?", sub: 'I pull the latest sales around it and build your number by hand.', ph: 'Street address, city or ZIP', req: true, unit: true },
        { k: 'type', t: 'one', q: 'What kind of property is it?', o: ['House', 'Condo or townhome', 'Duplex to fourplex', 'Apartment building (5+ units)', 'Land or a teardown'] },
        { k: 'size', t: 'size', q: 'How big is it?', sub: 'Close is fine. Skip anything you are not sure about.' },
        { k: 'condition', t: 'one', q: 'What shape is it in?', o: ['Needs major work', 'Original but well kept', 'Partly updated', 'Fully remodeled', 'Built in the last 5 years'] },
        { k: 'timing', t: 'one', q: 'When might you sell?', o: WHEN.map((w) => w[1]) },
        { k: 'contact', t: 'contact', q: 'Where should I send your valuation?', sub: 'You get a value range from the most recent sales near you, plus what you would walk away with after costs. Free, within 24 hours.', btn: 'Get my home value' },
        { k: 'updates', t: 'many', post: true, q: "What's been updated?", sub: 'Pick everything that applies.', o: ['Kitchen', 'Bathrooms', 'Roof', 'Windows', 'Heating and AC', 'Electrical', 'Plumbing or sewer line', 'Foundation', 'Flooring', 'Paint', 'Solar', 'Landscaping', 'None of these'] },
        { k: 'features', t: 'many', post: true, q: 'Anything that adds value?', o: ['Pool', 'Spa', 'ADU or guest house', 'View', 'Garage', 'Corner lot', 'Home office', 'Primary bedroom downstairs', 'Outdoor kitchen', 'Gated', 'Additions without permits', 'None of these'] },
        { k: 'occupancy', t: 'one', post: true, q: 'Who lives there now?', o: ['I do', 'A tenant', 'No one, it is vacant', "It's a second home"] },
        { k: 'lease', t: 'text', post: true, q: 'When does the lease end, and what is the rent?', ph: 'Like "month to month, $4,200"', when: (A) => A.occupancy === 'A tenant' },
        { k: 'reason', t: 'one', post: true, q: "What's behind the move?", o: ['Upsizing or downsizing', 'Relocating', 'Cashing out or investing', 'Estate, trust or family change', 'Refinancing or a HELOC', 'Just curious'] },
        { k: 'next', t: 'one', post: true, q: 'Are you buying after you sell?', o: ['Yes, in LA', 'Yes, outside LA', 'No', 'Not sure yet'] },
        { k: 'mortgage', t: 'one', post: true, q: 'Is there a loan on it?', sub: 'Helps me show what you would walk away with.', o: ['Yes', 'No, it is paid off', 'Rather not say'] },
        { k: 'guess', t: 'text', post: true, q: 'What do you think it is worth?', sub: 'Optional. I like to know where your head is.', ph: 'Like "$1.8M"' },
        { k: 'notes', t: 'area', post: true, q: 'Anything else I should know?', ph: 'Recent work, issues, tenants, more than one owner, a trust, a tight timeline. Complicated is fine.' },
      ],
      subject: (A) => 'Home value request: ' + (A.address || 'no address') + (A.unit ? ' #' + A.unit : ''),
      done: (A, first) => `<p class="lf-kick">Request received</p><h3>Got it, ${esc(first)}.</h3><p>I'm pulling the latest sales around <b>${esc(A.address)}</b> now. You'll have your value range within 24 hours, usually the same day.</p>`,
      after: 'A few more taps make your number sharper. All optional:',
      end: (A, first) => `<p class="lf-kick">All set</p><h3>Thanks, ${esc(first)}. That's everything I need.</h3><p>Want it faster? Call or text me and I'll walk you through it today.</p>`,
    },
    buy: {
      kind: 'Buyer search',
      steps: [
        { k: 'areas', t: 'many', q: 'Where do you want to live?', sub: 'Pick any, or type neighborhoods and ZIP codes.', o: AREAS.map((a) => a[1]), type: 'Or type it, like "Venice, Mar Vista, 90066"' },
        { k: 'home', t: 'one', q: 'What kind of home?', o: ['House', 'Condo or townhome', 'Duplex to fourplex', 'Land or a teardown', 'Open to anything'] },
        { k: 'budget', t: 'one', q: "What's your budget?", o: ['Under $1M', '$1M to $2M', '$2M to $3.5M', '$3.5M to $6M', '$6M and up', 'Not sure yet'] },
        { k: 'rooms', t: 'rooms', q: 'How many bedrooms and bathrooms?' },
        { k: 'pay', t: 'one', q: 'How are you paying?', sub: 'Every answer works. I have lenders for all of these.', o: ['All cash', 'Loan, already pre-approved', 'Loan, need a lender', "I'm self-employed or my income is non-traditional", 'Seller financing or another creative structure', '1031 exchange'] },
        { k: 'timing', t: 'one', q: 'When do you want to buy?', o: WHEN.map((w) => w[1]).slice(0, 4).concat(['Just looking for now']) },
        { k: 'contact', t: 'contact', q: 'Where should I send your matches?', sub: 'New listings that fit, Compass coming-soon homes and my team\'s off-market list, sent as they come up.', btn: 'Start my search' },
        { k: 'must', t: 'many', post: true, q: 'What matters most?', o: ['A yard', 'A pool', 'A view', 'Single story', 'Primary bedroom downstairs', 'Home office', 'Guest house or ADU', 'Garage', 'Move-in ready', 'A fixer with upside', 'Modern or new construction', 'Walk to coffee and dinner', 'Good schools', 'Quiet street'] },
        { k: 'sell_first', t: 'one', post: true, q: 'Do you need to sell a home first?', o: ['Yes', 'No', 'Not sure'] },
        { k: 'now', t: 'one', post: true, q: 'Where are you living now?', o: ['Renting in LA', 'Own in LA', 'Moving from outside LA'] },
        { k: 'notes', t: 'area', post: true, q: 'Anything else I should know?', ph: 'Must-haves, deal-breakers, a street you love, a tricky financing situation. Complicated is fine.' },
      ],
      subject: (A) => 'Buyer search: ' + [[].concat(A.areas || []).join(', '), A.budget].filter(Boolean).join(', '),
      done: (A, first) => `<p class="lf-kick">Search started</p><h3>Got it, ${esc(first)}.</h3><p>I'm setting up your search now. You'll get homes that fit, including ones that aren't public yet. I'll reach out today.</p>`,
      after: 'A few more so I only send what fits. All optional:',
      end: (A, first) => `<p class="lf-kick">All set</p><h3>Thanks, ${esc(first)}. Your search is set.</h3><p>Want to talk it through? Call or text me anytime.</p>`,
    },
  };

  const label = (k) => ({ address: 'Address', unit: 'Unit', type: 'Property type', beds: 'Bedrooms', baths: 'Bathrooms', sqft: 'Interior sq ft', lot: 'Lot sq ft', condition: 'Condition', timing: 'Timing',
    updates: 'Updated', features: 'Features', occupancy: 'Occupied by', lease: 'Lease', reason: 'Reason', next: 'Buying after', mortgage: 'Loan on it', guess: 'Owner thinks it is worth', notes: 'Notes',
    areas: 'Areas', home: 'Home type', budget: 'Budget', pay: 'Paying with', must: 'Must-haves', sell_first: 'Needs to sell first', now: 'Living now', prefer: 'Best way to reach' }[k] || k);

  const post = (payload) => {
    if (!TO) return Promise.reject(new Error('no endpoint'));
    return fetch('https://formsubmit.co/ajax/' + TO, { method: 'POST', keepalive: true, headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload) })
      .then((r) => r.json().catch(() => ({})).then((j) => { if (!r.ok || j.success === 'false' || j.success === false) throw new Error(j.message || 'not sent'); return j; }));
  };

  roots.forEach((root) => {
    const F = FLOWS[root.dataset.flow];
    if (!F) return;
    const KEY = 'ng_flow_' + root.dataset.flow;
    let A = {};
    try { A = JSON.parse(sessionStorage.getItem(KEY) || '{}'); } catch (e) { A = {}; }
    if (A._sent && A._done) A = {};
    if (q.get('addr') && root.dataset.flow === 'value') A.address = q.get('addr');
    if (root.dataset.area && root.dataset.flow === 'buy' && !A.typed) A.typed = root.dataset.area;
    if (root.dataset.addrph) F.steps[0].ph = root.dataset.addrph;
    const save = () => { try { sessionStorage.setItem(KEY, JSON.stringify(A)); } catch (e) { /* private mode */ } };
    let i = 0;
    const live = () => F.steps.filter((s) => !s.when || s.when(A));
    const pre = () => live().filter((s) => !s.post);
    const pst = () => live().filter((s) => s.post);
    if (A._sent) i = pre().length + Math.min(A._pi || 0, pst().length);
    else if (q.get('addr') && root.dataset.flow === 'value') i = 1;

    const rows = (keys) => keys.filter((k) => A[k] != null && A[k] !== '' && !(Array.isArray(A[k]) && !A[k].length))
      .map((k) => [label(k), Array.isArray(A[k]) ? A[k].join(', ') : A[k]]);
    const fields = () => {
      const o = {};
      rows(Object.keys(A).filter((k) => !k.startsWith('_') && !['name', 'email', 'phone', 'typed'].includes(k))).forEach(([k, v]) => { o[k] = v; });
      if (A.typed) o[root.dataset.flow === 'buy' ? 'Neighborhoods typed' : 'Typed'] = A.typed;
      return o;
    };

    const render = () => {
      const steps = live();
      const s = steps[i];
      const P = pre().length;
      if (!s) { root.innerHTML = `<div class="lf-done">${F.end(A, (A.name || '').split(' ')[0])}${reach()}</div>`; return; }
      const inPost = s.post;
      const n = inPost ? i - P + 1 : i + 1, of = inPost ? pst().length : P;
      const pct = Math.round(((inPost ? n : n - 1) / of) * 100);
      let body = '';
      if (s.t === 'one') body = `<div class="lf-opts">${s.o.map((o) => `<button type="button" class="lf-opt${A[s.k] === o ? ' on' : ''}" data-v="${esc(o)}">${esc(o)}</button>`).join('')}</div>`;
      if (s.t === 'many') {
        const cur = [].concat(A[s.k] || []);
        body = `<div class="lf-opts lf-many">${s.o.map((o) => `<button type="button" class="lf-opt${cur.includes(o) ? ' on' : ''}" aria-pressed="${cur.includes(o)}" data-v="${esc(o)}">${esc(o)}</button>`).join('')}</div>`
          + (s.type ? `<input class="lf-in" name="typed" placeholder="${esc(s.type)}" value="${esc(A.typed || '')}">` : '');
      }
      if (s.t === 'text') body = `<input class="lf-in" name="${s.k}" placeholder="${esc(s.ph || '')}" value="${esc(A[s.k] || '')}"${s.k === 'address' ? ' autocomplete="street-address"' : ''}>`
        + (s.unit ? `<input class="lf-in lf-unit" name="unit" placeholder="Unit (optional)" value="${esc(A.unit || '')}">` : '');
      if (s.t === 'area') body = `<textarea class="lf-in" name="${s.k}" rows="3" placeholder="${esc(s.ph || '')}">${esc(A[s.k] || '')}</textarea>`;
      if (s.t === 'size' || s.t === 'rooms') {
        const step = (k, lab, min, max, inc) => `<div class="lf-step"><span>${lab}</span><div><button type="button" data-inc="${k}" data-d="-${inc}" aria-label="Fewer ${lab.toLowerCase()}">&minus;</button><b data-show="${k}">${A[k] != null ? A[k] + (A[k] >= max ? '+' : '') : (s.t === 'rooms' ? 'Any' : 'Skip')}</b><button type="button" data-inc="${k}" data-d="${inc}" data-min="${min}" data-max="${max}" aria-label="More ${lab.toLowerCase()}">+</button></div></div>`;
        body = step('beds', 'Bedrooms', s.t === 'rooms' ? 1 : 0, 8, 1) + step('baths', 'Bathrooms', 1, 8, 0.5);
        if (s.t === 'size') body += `<div class="lf-two"><input class="lf-in" name="sqft" inputmode="numeric" placeholder="Interior sq ft" value="${esc(A.sqft || '')}"><input class="lf-in" name="lot" inputmode="numeric" placeholder="Lot size, sq ft" value="${esc(A.lot || '')}"></div>`;
      }
      if (s.t === 'contact') body = `<div class="lf-two"><input class="lf-in" name="name" autocomplete="name" placeholder="Your name" value="${esc(A.name || '')}"><input class="lf-in" name="phone" type="tel" autocomplete="tel" placeholder="Mobile number" value="${esc(A.phone || '')}"></div>
<input class="lf-in" name="email" type="email" autocomplete="email" placeholder="Email" value="${esc(A.email || '')}">
<div class="lf-pref"><span>Best way to reach you</span>${['Text', 'Call', 'Email'].map((p) => `<button type="button" class="lf-chip${(A.prefer || 'Text') === p ? ' on' : ''}" data-pref="${p}">${p}</button>`).join('')}</div>`;
      const needsBtn = s.t !== 'one';
      const intro = inPost && i === P && A._sent ? `<div class="lf-done lf-mini">${F.done(A, (A.name || '').split(' ')[0])}</div><p class="lf-after">${esc(F.after)}</p>` : '';
      root.innerHTML = `${intro}<div class="lf-top"><button type="button" class="lf-back"${i === 0 || (inPost && i === P) ? ' hidden' : ''}>&larr; Back</button><span class="lf-n">${inPost ? 'Optional' : 'Step'} ${n} of ${of}</span></div>
<div class="lf-bar"><i style="width:${Math.max(6, pct)}%"></i></div>
<h3 class="lf-q">${esc(s.q)}</h3>${s.sub ? `<p class="lf-sub">${esc(s.sub)}</p>` : ''}
<div class="lf-body">${body}</div>
<p class="lf-err" role="alert"></p>
<div class="lf-nav">${needsBtn ? `<button type="button" class="btn solid big lf-go">${esc(s.btn || (inPost ? 'Next' : 'Continue'))}</button>` : ''}${(inPost || (!s.req && s.t !== 'contact')) ? '<button type="button" class="lf-skip">Skip</button>' : ''}</div>
${s.t === 'contact' ? `<p class="lf-legal">Free, no obligation. By sending, you agree I can contact you by call, text or email about real estate. Reply STOP to opt out. <a href="/privacy/">Privacy</a></p>` : ''}`;
      const first = root.querySelector('input.lf-in, textarea.lf-in');
      if (first && root.dataset.started) first.focus({ preventScroll: true });
    };

    const reach = () => `<div class="lf-reach"><a class="btn solid" href="tel:${TEL}">Call ${PHONE}</a><a class="btn" href="sms:${TEL}">Text me</a></div>`;
    const grab = () => {
      root.querySelectorAll('input.lf-in, textarea.lf-in').forEach((el) => { const v = el.value.trim(); if (v) A[el.name] = v; else delete A[el.name]; });
    };
    const go = (d) => {
      root.dataset.started = '1';
      i = Math.max(0, i + d);
      if (A._sent) { A._pi = Math.max(0, i - pre().length); }
      save(); render();
      const r = root.getBoundingClientRect();
      if (r.top < 60 || r.top > innerHeight * 0.5) root.scrollIntoView({ block: 'start', behavior: 'smooth' });
    };
    const err = (t) => { const p = root.querySelector('.lf-err'); if (p) p.textContent = t; };

    const sendMain = async () => {
      const first = (A.name || '').split(' ')[0];
      const payload = Object.assign({ name: A.name, email: A.email, phone: A.phone, 'Best way to reach': A.prefer || 'Text', looking: F.kind,
        page: location.pathname + location.search, _subject: F.subject(A) + ' (' + A.name + ')', _template: 'table', _captcha: 'false' }, fields(), window.NG ? window.NG.journey() : {});
      delete payload.prefer;
      await post(payload);
      A._sent = 1; A._pi = 0; save();
      if (window.NG) window.NG.submitted();
      if (window.gtag) window.gtag('event', 'generate_lead', { form: root.dataset.flow });
      if (window.fbq) window.fbq('track', 'Lead', { content_name: root.dataset.flow });
      return first;
    };
    let detailsSent = false;
    const sendDetails = () => {
      if (!A._sent || detailsSent) return;
      const extra = fields();
      const keys = pst().map((s) => label(s.k));
      if (!keys.some((k) => extra[k])) return;
      detailsSent = true;
      post(Object.assign({ name: A.name, email: A.email, phone: A.phone, _subject: F.subject(A).replace(/^[^:]+/, (m) => m + ' details') + ' (' + A.name + ')', _template: 'table', _captcha: 'false' }, extra)).catch(() => { detailsSent = false; });
    };
    addEventListener('pagehide', sendDetails);
    document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') sendDetails(); });

    root.addEventListener('click', async (ev) => {
      const t = ev.target.closest('button');
      if (!t || !root.contains(t)) return;
      const s = live()[i];
      if (t.classList.contains('lf-back')) { grab(); go(-1); return; }
      if (t.classList.contains('lf-skip')) { grab(); if (!pst()[i - pre().length + 1] && s && s.post) { i = live().length; sendDetails(); A._done = 1; save(); render(); return; } go(1); return; }
      if (t.dataset.pref) { A.prefer = t.dataset.pref; root.querySelectorAll('[data-pref]').forEach((b) => b.classList.toggle('on', b === t)); return; }
      if (t.dataset.inc) {
        const k = t.dataset.inc, d = +t.dataset.d, min = +(t.dataset.min || root.querySelector(`[data-inc="${k}"][data-min]`).dataset.min), max = +(root.querySelector(`[data-inc="${k}"][data-max]`).dataset.max);
        const base = A[k] != null ? A[k] : (d > 0 ? Math.max(min, 1) - d : min);
        let v = Math.round((base + d) * 2) / 2;
        if (v < min) { delete A[k]; } else { A[k] = Math.min(max, v); }
        const b = root.querySelector(`[data-show="${k}"]`);
        b.textContent = A[k] != null ? A[k] + (A[k] >= max ? '+' : '') : (s.t === 'rooms' ? 'Any' : 'Skip');
        save(); return;
      }
      if (t.classList.contains('lf-opt')) {
        if (s.t === 'one') { A[s.k] = t.dataset.v; save(); t.classList.add('on'); setTimeout(() => { if (s.post && !pst()[i - pre().length + 1]) { i = live().length; sendDetails(); A._done = 1; save(); render(); } else go(1); }, 160); return; }
        const cur = new Set([].concat(A[s.k] || []));
        const v = t.dataset.v;
        if (v === 'None of these') { cur.clear(); cur.add(v); } else { cur.delete('None of these'); if (cur.has(v)) cur.delete(v); else cur.add(v); }
        A[s.k] = [...cur];
        root.querySelectorAll('.lf-opt').forEach((b) => { const on = cur.has(b.dataset.v); b.classList.toggle('on', on); b.setAttribute('aria-pressed', String(on)); });
        save(); return;
      }
      if (t.classList.contains('lf-go')) {
        grab();
        if (s.req && !A[s.k]) { err(s.k === 'address' ? 'Add the address so I can pull the sales around it.' : 'This one is needed.'); return; }
        if (s.t === 'many' && !s.post && !(A[s.k] || []).length && !A.typed) { err('Pick at least one, or type it.'); return; }
        if (s.t === 'contact') {
          if (!A.name) { err('Add your name.'); return; }
          if (!/\d{3}.*\d{4}/.test(A.phone || '')) { err('Add a mobile number so I can reach you.'); return; }
          if (!/^\S+@\S+\.\S+$/.test(A.email || '')) { err('Add a valid email.'); return; }
          t.disabled = true; t.textContent = 'Sending...';
          try { await sendMain(); go(1); } catch (e) {
            t.disabled = false; t.textContent = s.btn;
            err(`That didn't go through from here. Call or text ${PHONE} and I'll take it from there.`);
          }
          return;
        }
        if (s.post && !pst()[i - pre().length + 1]) { i = live().length; sendDetails(); A._done = 1; save(); render(); return; }
        go(1);
      }
    });
    root.addEventListener('keydown', (ev) => {
      if (ev.key === 'Enter' && ev.target.matches('input.lf-in')) { ev.preventDefault(); const b = root.querySelector('.lf-go'); if (b) b.click(); }
    });
    // Embedded starters: a field outside the card can hand its value in (like an address box in a hero)
    document.querySelectorAll(`[data-flow-start="${root.dataset.flow}"]`).forEach((f) => f.addEventListener('submit', (ev) => {
      ev.preventDefault();
      const v = (f.querySelector('input') || {}).value || '';
      if (v.trim()) A.address = v.trim();
      i = A.address ? 1 : 0; save(); root.dataset.started = '1'; render(); root.scrollIntoView({ block: 'start', behavior: 'smooth' });
    }));
    render();
  });
})();
