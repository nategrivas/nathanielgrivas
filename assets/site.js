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
        page: location.pathname + location.search, _subject: (form.dataset.subject || 'Website lead') + ': ' + looking + ' (' + name + ')', _template: 'table' };
      const btn = form.querySelector('button[type=submit]');
      btn.disabled = true; btn.textContent = 'Sending...';
      try {
        const r = await fetch('https://formsubmit.co/ajax/' + form.dataset.to, {
          method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload) });
        if (!r.ok) throw new Error('bad status');
        form.reset();
        say('Got it, ' + name.split(' ')[0] + '. I will get back to you within a day.');
      } catch (err) {
        say('This message could not be sent from here. Call or text 310-269-5541, or email nate.grivas@compass.com.');
      } finally { btn.disabled = false; btn.textContent = 'Send to Nathaniel'; }
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
      hm.setAttribute('viewBox', Math.max(-v.width * 0.35, Math.min(1000 - v.width * 0.65, x)).toFixed(1) + ' ' + (narrow ? cy - v.height * 0.3 : v.y).toFixed(1) + ' ' + v.width + ' ' + v.height);
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
}
