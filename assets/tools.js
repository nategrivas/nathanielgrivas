{
  // Calculators and the neighborhood quiz. All math runs in the browser; nothing is sent anywhere.
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const money = (n) => (n < 0 ? '-$' : '$') + Math.round(Math.abs(n)).toLocaleString('en-US');
  const pct = (n, d = 2) => (n * 100).toFixed(d).replace(/\.?0+$/, '') + '%';
  const num = (v) => { const n = parseFloat(String(v).replace(/[^0-9.\-]/g, '')); return isFinite(n) ? n : 0; };
  const params = new URLSearchParams(location.search);

  $$('input[data-money]').forEach((i) => {
    const fmt = () => { const n = num(i.value); if (i.value !== '') i.value = n.toLocaleString('en-US'); };
    fmt(); i.addEventListener('blur', fmt);
  });
  const val = (form, name) => num(form.elements[name].value);
  const rows = (tb, list) => { tb.innerHTML = list.map(([a, b, c]) => '<tr' + (c ? ' class="' + c + '"' : '') + '><th>' + a + '</th><td>' + b + '</td></tr>').join(''); };

  // ---------------------------------------------------------------- transfer tax
  const taxEl = $('#taxcalc');
  if (taxEl) {
    const f = $('form', taxEl);
    const county = (p) => Math.ceil(p / 500) * 0.55;
    const CC = [[1500000, 0.0045], [3000000, 0.015], [10000000, 0.03], [Infinity, 0.04]];
    const calc = (p, city, te) => {
      const t = { county: county(p), city: 0, ula: 0 };
      if (city === 'los-angeles') {
        t.city = Math.ceil(p / 500) * 2.25;
        if (!te) t.ula = p >= 10900000 ? p * 0.055 : p > 5400000 ? p * 0.04 : 0;
      } else if (city === 'santa-monica') {
        t.city = p * (p >= 8000000 ? 0.056 : p >= 5000000 ? 0.006 : 0.003);
      } else if (city === 'culver-city') {
        let lo = 0; for (const [hi, r] of CC) { if (p > lo) t.city += (Math.min(p, hi) - lo) * r; lo = hi; }
      }
      t.total = t.county + t.city + t.ula; t.net = p - t.total; return t;
    };
    const CLIFFS = { 'los-angeles': [5400000, 10899999], 'santa-monica': [4999999, 7999999] };
    const sel = f.elements.city;
    if (params.get('city')) sel.value = params.get('city');
    if (params.get('price')) f.elements.price.value = num(params.get('price')).toLocaleString('en-US');
    const run = () => {
      const p = val(f, 'price'), city = sel.value;
      $('#teRow').hidden = city !== 'los-angeles';
      const te = city === 'los-angeles' && f.elements.te.checked;
      const t = calc(p, city, te);
      $('#tTotal').textContent = money(t.total);
      $('#tRate').textContent = p ? pct(t.total / p) + ' of the price' : '';
      $('#tNet').textContent = money(t.net);
      const list = [['LA County (0.11%)', money(t.county)]];
      const cname = sel.options[sel.selectedIndex].text;
      list.push([cname + ' tax', t.city ? money(t.city) : 'None']);
      if (city === 'los-angeles') list.push(['Measure ULA', te ? 'Exempt (Prop TE)' : t.ula ? money(t.ula) + ' (' + (p >= 10900000 ? '5.5%' : '4%') + ' of the full price)' : 'None at this price']);
      rows($('#tRows'), list);
      const w = $('#tWarn'); w.hidden = true;
      for (const b of (CLIFFS[city] || [])) {
        if (te || p <= b) continue;
        const nb = calc(b, city, te).net;
        if (t.net < nb) {
          let lo = b, hi = b * 1.2;
          for (let i = 0; i < 60; i++) { const m = (lo + hi) / 2; calc(m, city, te).net < nb ? lo = m : hi = m; }
          w.innerHTML = '<b>You are in the cliff zone.</b> At ' + money(p) + ' you net about ' + money(nb - t.net) + ' less than a sale at ' + (b % 1000 === 999 ? 'just under ' + money(b + 1) : money(b)) + '. A sale has to reach about <b>' + money(Math.ceil(hi / 1000) * 1000) + '</b> just to net the same.';
          w.hidden = false;
        }
      }
    };
    f.addEventListener('input', run); f.addEventListener('change', run); run();
  }

  // ---------------------------------------------------------------- mortgage
  const mEl = $('#mortcalc');
  if (mEl) {
    const f = $('form', mEl);
    let mode = 'pay';
    $$('.tabs button').forEach((b) => b.addEventListener('click', () => {
      mode = b.dataset.tab;
      $$('.tabs button').forEach((x) => x.setAttribute('aria-selected', String(x === b)));
      $$('[data-pane]', mEl).forEach((p) => { p.hidden = p.dataset.pane !== mode; });
      run();
    }));
    const run = () => {
      const d = val(f, 'down') / 100, rate = val(f, 'rate') / 1200, n = val(f, 'term') * 12;
      const k = rate ? rate / (1 - Math.pow(1 + rate, -n)) : 1 / n;
      const tx = val(f, 'ptax') / 1200, ins = val(f, 'ins') / 12, hoa = val(f, 'hoa');
      $('#dpOut').textContent = Math.round(d * 100) + '%';
      let price = val(f, 'price');
      if (mode === 'afford') price = Math.max(0, (val(f, 'budget') - ins - hoa) / ((1 - d) * k + tx));
      const loan = price * (1 - d), pi = loan * k, tax = price * tx, total = pi + tax + ins + hoa;
      if (mode === 'pay') { $('#mHead').textContent = 'Monthly payment'; $('#mBig').textContent = money(total); $('#mSub').textContent = 'all in, per month'; }
      else { $('#mHead').textContent = 'That budget buys about'; $('#mBig').textContent = money(Math.round(price / 5000) * 5000); $('#mSub').textContent = money(total) + ' per month all in'; }
      const parts = [['Principal & interest', pi, 'a'], ['Property tax', tax, 'b'], ['Insurance', ins, 'c'], ['HOA', hoa, 'd']];
      $('#mStack').innerHTML = parts.filter((x) => x[1] > 0).map(([l, v, c]) => '<i class="' + c + '" style="flex:' + v + '" title="' + l + '"></i>').join('');
      rows($('#mRows'), [
        ...parts.map(([l, v, c]) => ['<span class="sw ' + c + '"></span>' + l, money(v)]),
        ['Down payment', money(price * d)], ['Loan amount', money(loan)],
        ['Income where this is 30% of gross', money(total * 12 / 0.30) + '/yr'],
        ['Interest over the full term', money(pi * n - loan)],
      ]);
    };
    if (params.get('price')) f.elements.price.value = num(params.get('price')).toLocaleString('en-US');
    f.addEventListener('input', run); run();
  }

  // ---------------------------------------------------------------- rent vs buy
  const rEl = $('#rvbcalc');
  if (rEl) {
    const f = $('form', rEl);
    const sim = () => {
      const price = val(f, 'price'), d = val(f, 'down') / 100, r = val(f, 'rate') / 1200, n = 360;
      const pi = r ? price * (1 - d) * r / (1 - Math.pow(1 + r, -n)) : price * (1 - d) / n;
      const mInv = Math.pow(1 + val(f, 'inv') / 100, 1 / 12) - 1;
      let bal = price * (1 - d), rent = val(f, 'rent');
      let renter = price * d + price * val(f, 'buyc') / 100, buyer = 0;
      const out = [];
      for (let m = 1; m <= 360; m++) {
        bal -= pi - bal * r;
        const yr = Math.floor((m - 1) / 12);
        const own = pi + price * val(f, 'ptax') / 1200 * Math.pow(1.02, yr) + val(f, 'own');
        renter *= 1 + mInv; buyer *= 1 + mInv;
        const diff = own - rent;
        if (diff > 0) renter += diff; else buyer -= diff;
        if (m === 1) out.firstOwn = own;
        if (m % 12 === 0) {
          const value = price * Math.pow(1 + val(f, 'appr') / 100, m / 12);
          const equity = value * (1 - val(f, 'sellc') / 100) - Math.max(bal, 0);
          out.push({ y: m / 12, buyerNW: equity + buyer, renterNW: renter, value, bal: Math.max(bal, 0), equity, buyer, renter });
          rent *= 1 + val(f, 'rentg') / 100;
        }
      }
      return out;
    };
    const run = () => {
      $('#rdpOut').textContent = Math.round(val(f, 'down')) + '%';
      const Y = Math.min(30, Math.max(1, Math.round(val(f, 'years'))));
      const s = sim(), at = s[Y - 1], gap = at.buyerNW - at.renterNW;
      const be = s.find((x) => x.buyerNW >= x.renterNW);
      $('#rHead').textContent = 'After ' + Y + ' year' + (Y > 1 ? 's' : '');
      $('#rBig').textContent = (gap >= 0 ? 'Buying' : 'Renting') + ' ahead by ' + money(Math.abs(gap));
      $('#rSub').textContent = be ? 'Buying pulls ahead in year ' + be.y : 'Buying does not pull ahead within 30 years on these numbers';
      rows($('#rRows'), [
        ['Owning, first month (all in)', money(s.firstOwn)], ['Rent, first month', money(val(f, 'rent'))],
        ['Home value in year ' + Y, money(at.value)], ['Loan balance in year ' + Y, money(at.bal)],
        ['Your equity after selling costs', money(at.equity)],
        ["Buyer's invested savings", money(at.buyer)], ["Renter's invested savings", money(at.renter)],
      ]);
      // chart: buying minus renting by year
      const svg = $('#rChart'), Wd = 600, Ht = 240, pad = 28;
      const vals = s.map((x) => x.buyerNW - x.renterNW);
      const mx = Math.max(1, ...vals.map(Math.abs));
      const y0 = Ht / 2, bw = (Wd - pad * 2) / 30;
      let g = '<line x1="' + pad + '" x2="' + (Wd - pad) + '" y1="' + y0 + '" y2="' + y0 + '" class="zero"/>';
      vals.forEach((v, i) => {
        const h = Math.abs(v) / mx * (Ht / 2 - 18), x = pad + i * bw + 1;
        g += '<rect x="' + x.toFixed(1) + '" y="' + (v >= 0 ? y0 - h : y0).toFixed(1) + '" width="' + (bw - 2).toFixed(1) + '" height="' + Math.max(h, 0.5).toFixed(1) + '" class="' + (v >= 0 ? 'pos' : 'neg') + (i === Y - 1 ? ' sel' : '') + '"><title>Year ' + (i + 1) + ': ' + money(v) + '</title></rect>';
      });
      g += '<text x="' + pad + '" y="14" class="lab">Buying ahead</text><text x="' + pad + '" y="' + (Ht - 4) + '" class="lab">Renting ahead</text>';
      g += '<text x="' + (Wd - pad) + '" y="' + (Ht - 4) + '" class="lab" text-anchor="end">Year 30</text>';
      svg.innerHTML = g;
    };
    f.addEventListener('input', run); run();
  }

  // ---------------------------------------------------------------- neighborhood quiz
  const quiz = $('.quiz');
  if (quiz && window.HOODS) {
    const H = window.HOODS;
    const steps = $$('.qstep', quiz);
    const ans = {};
    let i = 0;
    const TIERS = { u125: { 1: 3, 2: 2, 3: 0, 4: -3 }, u25: { 1: 1, 2: 3, 3: 2, 4: -1 }, u5: { 1: -1, 2: 1, 3: 3, 4: 2 }, o5: { 1: -2, 2: -1, 3: 1, 4: 3 }, rent: { 1: 1, 2: 2, 3: 2, 4: 0 } };
    const DUPLEX = ['beverly-grove', 'fairfax', 'pico-robertson', 'miracle-mile', 'palms', 'west-hollywood', 'east-hollywood', 'echo-park', 'venice', 'mar-vista'];
    const T = (h, t) => h.tags.includes(t);
    const score = (h) => {
      let s = 0; const why = [];
      const tier = TIERS[ans.budget] || {}; s += tier[h.tier] || 0;
      if ((tier[h.tier] || 0) >= 2) why.push('fits your budget range');
      if (ans.budget === 'rent' && (T(h, 'condo') || T(h, 'transit'))) s += 1;
      const day = { beach: [['beach', 3]], walk: [['walkable', 3]], hike: [['views', 3]], bbq: [['yard', 2], ['family', 1]], late: [['nightlife', 3]], art: [['creative', 2], ['walkable', 1]] }[ans.day] || [];
      day.forEach(([t, w]) => { if (T(h, t)) { s += w; why.push({ beach: 'close to the beach', walkable: 'walkable', views: 'hills and views', yard: 'yards and space', family: 'family streets', nightlife: 'nightlife', creative: 'creative scene' }[t]); } });
      const reg = { west: { Coast: 2, Westside: 2.5, 'Beverly Hills & the Hills': 1.5, Central: 0.5 }, central: { Central: 2.5, Eastside: 2, 'Beverly Hills & the Hills': 1, Westside: 0.5 }, valley: { Valley: 3, 'Beverly Hills & the Hills': 1 }, home: {} }[ans.commute] || {};
      if (reg[h.region]) { s += reg[h.region]; if (reg[h.region] >= 2) why.push('easy on your commute'); }
      const home = ans.home;
      if (home === 'house') { if (T(h, 'yard')) { s += 2; why.push('houses with yards'); } if (T(h, 'family')) s += 1; if (T(h, 'condo') && !T(h, 'yard')) s -= 1; }
      if (home === 'condo' && T(h, 'condo')) { s += 2.5; why.push('good condo choices'); }
      if (home === 'view' && T(h, 'views')) { s += 2.5; why.push('view homes'); }
      if (home === 'income' && DUPLEX.includes(h.slug)) { s += 3; why.push('duplexes and small income buildings'); }
      const who = { solo: [['nightlife', 1], ['walkable', 1]], couple: [['walkable', 1]], kids: [['family', 2], ['quiet', 1]], investor: [['value', 2]] }[ans.who] || [];
      who.forEach(([t, w]) => { if (T(h, t)) s += w; });
      if (ans.who === 'kids' && T(h, 'family')) why.push('good for families');
      if (ans.who === 'investor' && T(h, 'value')) why.push('more for the money');
      if (ans.pace === 'quiet') { if (T(h, 'quiet')) { s += 2; why.push('quiet'); } if (T(h, 'nightlife')) s -= 1; }
      if (ans.pace === 'mid' && T(h, 'walkable')) s += 1;
      if (ans.pace === 'busy') { if (T(h, 'nightlife')) s += 2; if (T(h, 'walkable')) s += 1; if (T(h, 'quiet')) s -= 1; }
      return { s, why: [...new Set(why)].slice(0, 3) };
    };
    const bar = $('.qbar i', quiz);
    const show = (n) => {
      i = n; steps.forEach((st, k) => { st.hidden = k !== n; });
      bar.style.width = (n / steps.length * 100) + '%';
      $('#qback').hidden = n === 0 || n >= steps.length;
    };
    const finish = () => {
      steps.forEach((st) => { st.hidden = true; }); bar.style.width = '100%'; $('#qback').hidden = true;
      const ranked = H.map((h) => ({ h, ...score(h) })).sort((a, b) => b.s - a.s).slice(0, 3);
      const top = ranked[0].s || 1;
      $('#qcards').innerHTML = '';
      ranked.forEach((x, k) => {
        const c = document.querySelector('#pool .hcard[data-slug="' + x.h.slug + '"]').cloneNode(true);
        const why = document.createElement('p'); why.className = 'why';
        why.innerHTML = '<b>' + (k === 0 ? 'Best match' : x.s / top > 0.85 ? 'Strong match' : 'Good match') + '</b>' + (x.why.length ? 'Because: ' + x.why.join(', ') : '');
        $('.hc-body', c).appendChild(why);
        $('#qcards').appendChild(c);
      });
      $('#qres').hidden = false;
      const names = ranked.map((x) => x.h.name).join(', ');
      const ta = document.querySelector('#contact textarea'); if (ta) ta.value = 'My quiz matches: ' + names + '. Send me homes that fit.';
      $('#qres').scrollIntoView({ behavior: 'smooth', block: 'start' });
    };
    $$('.opt', quiz).forEach((b) => b.addEventListener('click', () => {
      ans[b.dataset.k] = b.dataset.v;
      $$('.opt', b.parentElement).forEach((x) => x.classList.toggle('sel', x === b));
      setTimeout(() => (i + 1 < steps.length ? show(i + 1) : finish()), 160);
    }));
    $('#qback').addEventListener('click', () => show(Math.max(0, i - 1)));
    $('#qagain').addEventListener('click', () => { $('#qres').hidden = true; $$('.opt', quiz).forEach((x) => x.classList.remove('sel')); show(0); quiz.scrollIntoView({ behavior: 'smooth' }); });
  }

  // ---------------------------------------------------------------- compare
  const cmp = $('.cmp');
  if (cmp && window.HOODS) {
    const by = Object.fromEntries(window.HOODS.map((h) => [h.slug, h]));
    const A = $('#ca'), B = $('#cb');
    A.value = by[params.get('a')] ? params.get('a') : 'santa-monica';
    B.value = by[params.get('b')] ? params.get('b') : 'culver-city';
    const TIER = { 1: '$ Most attainable', 2: '$$ Moderate', 3: '$$$ Upper', 4: '$$$$ Top of market' };
    const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const run = () => {
      const a = by[A.value], b = by[B.value], ca = window.CITIES[a.city], cb = window.CITIES[b.city];
      const r = [
        ['', (h) => { const c = document.querySelector('#pool .hcard[data-slug="' + h.slug + '"]'); return c ? c.outerHTML : esc(h.name); }],
        ['Region', (h) => esc(h.region)], ['City', (h, c) => esc(c.label)], ['ZIP codes', (h) => esc(h.zips)],
        ['Price level', (h) => TIER[h.tier]], ['Transfer tax', (h, c) => esc(c.transfer)], ['Measure ULA', (h, c) => esc(c.ula)],
        ['Rent control', (h, c) => esc(c.rent)], ['Public schools', (h, c) => esc(c.schools)],
        ['Known for', (h) => h.tags.map((t) => '<span class="tg">' + esc(window.TAGS[t]) + '</span>').join(' ')],
        ['What it is like', (h) => esc(h.feel)], ['The housing', (h) => esc(h.housing)],
        ['Good fit if', (h) => esc(h.fit)], ['Think twice if', (h) => esc(h.skip)],
      ];
      $('#ctable').innerHTML = '<table><tbody>' + r.map(([l, fn]) => '<tr><th>' + l + '</th><td>' + fn(a, ca) + '</td><td>' + fn(b, cb) + '</td></tr>').join('') + '</tbody></table>';
      history.replaceState(null, '', '?a=' + a.slug + '&b=' + b.slug);
    };
    A.addEventListener('change', run); B.addEventListener('change', run); run();
  }
}
