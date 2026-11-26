{
  // Lead forms: send to Nathaniel through FormSubmit. Show a call/text fallback if sending fails.
  document.querySelectorAll('form.lead').forEach((form) => {
    const msg = form.querySelector('.formmsg');
    const say = (t) => { msg.textContent = t; msg.classList.add('on'); };
    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const d = new FormData(form);
      const name = (d.get('name') || '').trim();
      const email = (d.get('email') || '').trim();
      if (!name || !/^\S+@\S+\.\S+$/.test(email)) { say('Add your name and a valid email so I can reply.'); return; }
      const looking = d.getAll('looking').join(', ') || 'Not specified';
      const payload = { name, email, phone: d.get('phone') || '', looking, message: d.get('message') || '',
        page: location.pathname + location.search, _subject: (form.dataset.subject || 'Website lead') + ': ' + looking + ' (' + name + ')', _template: 'table',
        ...(window.NG ? window.NG.journey() : {}) };
      if (d.get('lender')) payload.lender_intro = 'Yes';
      const btn = form.querySelector('button[type=submit]');
      const label = btn.textContent;
      btn.disabled = true; btn.textContent = 'Sending...';
      try {
        const r = await fetch('https://formsubmit.co/ajax/' + form.dataset.to, {
          method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload) });
        if (!r.ok) throw new Error('bad status');
        form.reset();
        if (window.NG) window.NG.submitted();
        say(form.dataset.ok ? form.dataset.ok.replace('{name}', name.split(' ')[0]) : 'Got it, ' + name.split(' ')[0] + '. I will get back to you within a day.');
      } catch (err) {
        say('This message could not be sent from here. Call or text 310-269-5541, or email nate.grivas@compass.com.');
      } finally { btn.disabled = false; btn.textContent = label; }
    });
  });

  // Guide filters
  const list = document.getElementById('postlist');
  const btns = document.querySelectorAll('.filters button');
  if (list && btns.length) {
    const apply = (f) => {
      btns.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.f === f)));
      list.querySelectorAll('.post').forEach((p) => { p.style.display = (f === 'all' || p.dataset.cat === f) ? '' : 'none'; });
    };
    btns.forEach((b) => b.addEventListener('click', () => { apply(b.dataset.f); if (b.dataset.f !== 'all') location.hash = b.dataset.f; else history.replaceState(null, '', location.pathname); }));
    const h = location.hash.slice(1);
    if (h && [...btns].some((b) => b.dataset.f === h)) apply(h);
  }

  // Neighborhood hero map: on narrow screens, center the neighborhood instead of setting it right of the title
  const hm = document.querySelector('.heromap');
  if (hm) {
    const fit = () => {
      const v = hm.viewBox.baseVal, cx = +hm.dataset.cx, cy = +hm.dataset.cy;
      const r = hm.getBoundingClientRect();
      const narrow = r.width < 760;
      const x = narrow ? cx - v.width / 2 : cx - v.width * 0.62;
      hm.setAttribute('viewBox', Math.max(-v.width * 0.35, Math.min(1000 - v.width * 0.65, x)).toFixed(1) + ' ' + (narrow ? cy - v.height * 0.13 : v.y).toFixed(1) + ' ' + v.width + ' ' + v.height);
    };
    fit(); addEventListener('resize', fit);
  }

  // Horizontal shelves: drag to scroll on desktop
  document.querySelectorAll('.row').forEach((row) => {
    let down = false, sx = 0, sl = 0, moved = false;
    row.addEventListener('pointerdown', (e) => { if (e.pointerType !== 'mouse') return; down = true; moved = false; sx = e.clientX; sl = row.scrollLeft; });
    window.addEventListener('pointerup', () => { down = false; });
    row.addEventListener('pointermove', (e) => { if (!down) return; const dx = e.clientX - sx; if (Math.abs(dx) > 4) moved = true; row.scrollLeft = sl - dx; });
    row.addEventListener('click', (e) => { if (moved) { e.preventDefault(); moved = false; } }, true);
  });

  // Tabs: any [data-tabs] block with [data-tab] buttons and [data-panel] panels
  document.querySelectorAll('[data-tabs]').forEach((box) => {
    const btns = [...box.querySelectorAll('[data-tab]')];
    btns.forEach((b) => b.addEventListener('click', () => {
      btns.forEach((x) => x.setAttribute('aria-selected', String(x === b)));
      box.querySelectorAll('[data-panel]').forEach((p) => { p.hidden = p.dataset.panel !== b.dataset.tab; });
    }));
  });

  // "What's my home worth" style shortcuts pre-check the right box in the contact form
  document.querySelectorAll('[data-preset]').forEach((a) => a.addEventListener('click', () => {
    const box = document.querySelector('#contact input[value="' + a.dataset.preset[0].toUpperCase() + a.dataset.preset.slice(1) + '"]');
    if (box) box.checked = true;
  }));

  // On-page section nav: highlight the section in view
  const sub = document.querySelector('.subnav');
  if (sub && 'IntersectionObserver' in window) {
    const links = [...sub.querySelectorAll('a[href^="#"]')];
    const map = new Map(links.map((a) => [a.getAttribute('href').slice(1), a]));
    const io = new IntersectionObserver((ents) => {
      ents.forEach((en) => { if (en.isIntersecting) { links.forEach((l) => l.classList.remove('on')); const a = map.get(en.target.id); if (a) { a.classList.add('on'); a.scrollIntoView({ block: 'nearest', inline: 'nearest' }); } } });
    }, { rootMargin: '-30% 0px -60% 0px' });
    map.forEach((_, id) => { const el = document.getElementById(id); if (el) io.observe(el); });
  }

  // Search palette: Cmd/Ctrl+K or "/" anywhere, or any [data-cmdk] button
  const dlg = document.getElementById('cmdk');
  if (dlg) {
    const input = document.getElementById('cmdk-q');
    const list = document.getElementById('cmdk-list');
    let data = null, items = [], sel = 0, lastFocus = null;
    const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const load = () => data ? Promise.resolve(data) : fetch('/assets/search.json').then((r) => r.json()).then((d) => (data = d)).catch(() => (data = []));
    const QUICK = ['Explore the map', 'Which LA neighborhood fits you?', 'Transfer tax & mansion tax calculator', 'Contact', 'The Brodsky Group'];
    const score = (it, words) => {
      const t = it.t.toLowerCase(), hay = (it.t + ' ' + it.s + ' ' + it.k).toLowerCase();
      let sc = 0;
      for (const w of words) { if (!hay.includes(w)) return -1; sc += t.startsWith(w) ? 5 : t.includes(w) ? 3 : 1; }
      return sc + (it.g === 'Neighborhoods' ? 1 : 0);
    };
    const render = () => {
      const q = input.value.trim().toLowerCase();
      let res;
      if (!q) {
        const nav = [{ t: 'Explore the map', s: 'All 40 neighborhoods', u: '/neighborhoods/', g: 'Jump to', i: 'M' }];
        res = nav.concat((data || []).filter((x) => QUICK.includes(x.t)).map((x) => Object.assign({}, x, { g: 'Jump to' })))
          .concat((data || []).filter((x) => x.g === 'Neighborhoods').slice(0, 6));
      } else {
        const words = q.split(/\s+/);
        res = (data || []).map((x) => [score(x, words), x]).filter((x) => x[0] >= 0).sort((a, b) => b[0] - a[0]).slice(0, 14).map((x) => x[1]);
      }
      items = res; sel = 0;
      if (!res.length) { list.innerHTML = '<li class="cmdk-empty">Nothing found. Try a neighborhood name, a ZIP like 90049, or a word like "tax".</li>'; return; }
      let g = '', html = '';
      res.forEach((x, i) => {
        if (x.g !== g) { g = x.g; html += '<li class="grp">' + esc(g) + '</li>'; }
        html += '<li><a href="' + esc(x.u) + '" role="option" data-i="' + i + '" aria-selected="' + (i === 0) + '"' + (x.u.startsWith('http') ? ' rel="noopener"' : '') + '><span class="ic">' + esc(x.i || '') + '</span><span><b>' + esc(x.t) + '</b><small>' + esc(x.s || '') + '</small></span></a></li>';
      });
      list.innerHTML = html;
    };
    const move = (d) => {
      const as = [...list.querySelectorAll('a')]; if (!as.length) return;
      sel = (sel + d + as.length) % as.length;
      as.forEach((a, i) => a.setAttribute('aria-selected', String(i === sel)));
      as[sel].scrollIntoView({ block: 'nearest' });
    };
    const open = () => { lastFocus = document.activeElement; dlg.hidden = false; document.body.style.overflow = 'hidden'; input.value = ''; load().then(render); render(); setTimeout(() => input.focus(), 10); };
    const close = () => { dlg.hidden = true; document.body.style.overflow = ''; if (lastFocus) lastFocus.focus(); };
    document.querySelectorAll('[data-cmdk]').forEach((b) => b.addEventListener('click', open));
    dlg.addEventListener('click', (e) => { if (e.target === dlg || e.target.closest('[data-close]')) close(); });
    list.addEventListener('click', (e) => { if (e.target.closest('a')) close(); });
    input.addEventListener('input', render);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
      else if (e.key === 'Enter') { const a = list.querySelector('a[aria-selected="true"]'); if (a) { e.preventDefault(); a.click(); } }
    });
    document.addEventListener('keydown', (e) => {
      const typing = /INPUT|TEXTAREA|SELECT/.test((document.activeElement || {}).tagName || '');
      if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) { e.preventDefault(); dlg.hidden ? open() : close(); }
      else if (e.key === '/' && !typing && dlg.hidden) { e.preventDefault(); open(); }
      else if (e.key === 'Escape' && !dlg.hidden) close();
    });
  }
}

// Photo gallery lightbox
{
  const box = document.querySelector('.lightbox');
  const gal = document.querySelector('[data-gallery]');
  if (box && gal) {
    const all = [...gal.querySelectorAll('.gall i')].map((i) => ({ src: i.dataset.full, alt: i.dataset.alt }));
    const img = box.querySelector('img'), cap = box.querySelector('.lb-c');
    let at = 0;
    const show = (k) => { at = (k + all.length) % all.length; img.src = all[at].src; img.alt = all[at].alt; cap.textContent = all[at].alt + '  (' + (at + 1) + ' of ' + all.length + ')'; };
    const open = (src) => { const k = all.findIndex((a) => a.src === src); show(k < 0 ? 0 : k); box.hidden = false; document.body.style.overflow = 'hidden'; box.querySelector('.lb-x').focus(); };
    const close = () => { box.hidden = true; document.body.style.overflow = ''; };
    gal.querySelectorAll('.g').forEach((b) => b.addEventListener('click', () => open(b.dataset.full)));
    box.querySelector('.lb-x').addEventListener('click', close);
    box.querySelector('.lb-p').addEventListener('click', () => show(at - 1));
    box.querySelector('.lb-n').addEventListener('click', () => show(at + 1));
    box.addEventListener('click', (ev) => { if (ev.target === box) close(); });
    document.addEventListener('keydown', (ev) => { if (box.hidden) return; if (ev.key === 'Escape') close(); if (ev.key === 'ArrowLeft') show(at - 1); if (ev.key === 'ArrowRight') show(at + 1); });
  }
}

// Header over the hero: solid once scrolled
(() => {
  const top = document.querySelector('.top.over');
  if (!top) return;
  const on = () => top.classList.toggle('scrolled', window.scrollY > 30);
  on();
  window.addEventListener('scroll', on, { passive: true });
})();

// Hero slideshow
(() => {
  const hero = document.querySelector('.lux-hero');
  if (!hero) return;
  const figs = [...hero.querySelectorAll('.lh-slides figure')];
  const dots = [...hero.querySelectorAll('.lh-dots button')];
  const cap = hero.querySelector('.lh-cap');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let i = 0, timer = null, ready = false;
  const load = (f) => {
    const im = f && f.querySelector('img[data-src]');
    if (!im) return;
    im.srcset = im.dataset.srcset; im.src = im.dataset.src;
    im.removeAttribute('data-src'); im.removeAttribute('data-srcset');
  };
  const show = (n) => {
    i = (n + figs.length) % figs.length;
    load(figs[i]);
    figs.forEach((f, k) => f.classList.toggle('on', k === i));
    dots.forEach((d, k) => d.setAttribute('aria-current', k === i ? 'true' : 'false'));
    const f = figs[i], c = f.dataset.cap, h = f.dataset.href;
    if (c) { cap.hidden = false; cap.textContent = c; if (h) cap.setAttribute('href', h); else cap.removeAttribute('href'); }
    else cap.hidden = true;
    if (ready) load(figs[(i + 1) % figs.length]);
  };
  const play = () => {
    clearInterval(timer);
    if (reduce) return;
    timer = setInterval(() => { if (!document.hidden) show(i + 1); }, 6500);
  };
  dots.forEach((d, k) => d.addEventListener('click', () => { show(k); play(); }));
  show(0);
  const start = () => { ready = true; load(figs[1]); play(); };
  if (document.readyState === 'complete') start(); else window.addEventListener('load', start);
})();

// Call, text and message popups. Call/Text still open the phone app; on a computer the popup also shows the number and a QR code.
(() => {
  const reach = document.getElementById('ngd-reach');
  const msg = document.getElementById('ngd-msg');
  if (!reach || !msg || typeof reach.showModal !== 'function') return;
  const phoneUI = window.matchMedia('(pointer: coarse) and (max-width: 820px)');
  const kick = reach.querySelector('.kick'), num = reach.querySelector('.ngd-num');
  const qr = reach.querySelector('.ngd-qr img'), alt = reach.querySelector('[data-alt]');
  const tel = num.getAttribute('href').replace(/^(tel|sms):/, '');
  const setMode = (m) => {
    const text = m === 'text';
    kick.textContent = text ? 'Text Nathaniel' : 'Call Nathaniel';
    num.setAttribute('href', (text ? 'sms:' : 'tel:') + tel);
    qr.src = text ? qr.dataset.text : qr.dataset.call;
    qr.alt = 'QR code to ' + (text ? 'text ' : 'call ') + num.textContent;
    alt.setAttribute('href', (text ? 'tel:' : 'sms:') + tel);
    alt.textContent = text ? 'Call instead' : 'Text instead';
  };
  const open = (d) => {
    [reach, msg].forEach((x) => { if (x !== d && x.open) x.close(); });
    if (!d.open) d.showModal();
  };
  document.addEventListener('click', (ev) => {
    const a = ev.target.closest('a[href^="tel:"], a[href^="sms:"], a[href^="mailto:"], [data-msg]');
    if (!a) return;
    const href = a.getAttribute('href') || '';
    if (a.hasAttribute('data-msg') || (href.startsWith('mailto:') && !a.closest('dialog'))) {
      ev.preventDefault();
      open(msg);
      return;
    }
    if (href.startsWith('mailto:')) return;
    const m = href.startsWith('sms:') ? 'text' : 'call';
    if (a.closest('#ngd-reach')) { setMode(m); return; }
    if (phoneUI.matches) return;
    setMode(m);
    setTimeout(() => open(reach), 60);
  });
  [reach, msg].forEach((d) => d.addEventListener('click', (ev) => {
    if (ev.target === d || ev.target.closest('[data-close]')) d.close();
  }));
  const copy = reach.querySelector('[data-copy]');
  copy.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(copy.dataset.copy); copy.textContent = 'Copied'; }
    catch (e) { copy.textContent = copy.dataset.copy; }
    setTimeout(() => { copy.textContent = 'Copy number'; }, 1800);
  });
})();

// Listing films: a silent loop plays while in view; tapping plays the full film with sound. Vimeo loads only on tap.
(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('[data-film]').forEach((box) => {
    const v = box.querySelector('video'), btn = box.querySelector('.film-play');
    let full = false;
    if (!reduce && 'IntersectionObserver' in window) {
      new IntersectionObserver((ents) => ents.forEach((en) => {
        if (full) return;
        if (en.isIntersecting) { if (!v.getAttribute('src')) v.src = v.dataset.src; const pr = v.play(); if (pr) pr.catch(() => {}); } else v.pause();
      }), { threshold: 0.25 }).observe(box);
    }
    btn.addEventListener('click', () => {
      full = true;
      v.src = box.dataset.full; v.loop = false; v.muted = false; v.controls = true; v.preload = 'auto';
      box.classList.add('playing');
      const pr = v.play(); if (pr) pr.catch(() => {});
      if (window.NG) window.NG.answer('Watched film', document.title);
    });
  });
  document.querySelectorAll('[data-vimeo]').forEach((box) => {
    box.querySelector('.film-play').addEventListener('click', () => {
      const f = document.createElement('iframe');
      f.src = 'https://player.vimeo.com/video/' + box.dataset.vimeo + '?autoplay=1&dnt=1&title=0&byline=0&portrait=0';
      f.allow = 'autoplay; fullscreen; picture-in-picture'; f.allowFullscreen = true; f.title = 'Video tour';
      box.innerHTML = ''; box.appendChild(f); box.classList.add('playing');
      if (window.NG) window.NG.answer('Watched film', document.title);
    });
  });
})();
