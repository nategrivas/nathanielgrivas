{
  // Explore LA map: hover/tap tooltips, zoom and pan, filters and search that drive both the map and the card grid.
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;

  document.querySelectorAll('.mapwrap').forEach((wrap) => {
    const svg = wrap.querySelector('svg.lamap');
    const tip = wrap.querySelector('.tip');
    if (!svg) return;
    const W = 1000, H = svg.viewBox.baseVal.height;
    const vb = { x: 0, y: 0, w: W, h: H };
    let tipFor = null;

    const hideTip = () => { if (tip) { tip.hidden = true; tipFor = null; } };
    const showTip = (dot) => {
      if (!tip) return;
      const href = dot.getAttribute('href');
      tip.innerHTML = '<b>' + dot.getAttribute('aria-label') + '</b><span>' + (dot.dataset.line || '') + '</span><a href="' + href + '">Open the guide &rarr;</a>';
      tip.hidden = false;
      const wr = wrap.getBoundingClientRect(), dr = dot.querySelector('.pt').getBoundingClientRect();
      const x = dr.left + dr.width / 2 - wr.left, y = dr.top - wr.top;
      const tw = tip.offsetWidth, th = tip.offsetHeight;
      tip.style.left = Math.min(Math.max(8, x - tw / 2), wr.width - tw - 8) + 'px';
      tip.style.top = (y - th - 12 < 8 ? y + dr.height + 12 : y - th - 12) + 'px';
      tipFor = dot;
    };

    const set = () => {
      svg.setAttribute('viewBox', vb.x + ' ' + vb.y + ' ' + vb.w + ' ' + vb.h);
      const k = (vb.w / W).toFixed(3);
      svg.querySelectorAll('.dot .s').forEach((g) => g.setAttribute('transform', 'scale(' + k + ')'));
      svg.classList.toggle('z2', vb.w < 600);
      wrap.classList.toggle('zoomed', vb.w < W - 1);
      hideTip();
    };
    const clamp = () => {
      vb.w = Math.min(W, Math.max(150, vb.w)); vb.h = vb.w * H / W;
      vb.x = Math.min(Math.max(0, vb.x), W - vb.w); vb.y = Math.min(Math.max(0, vb.y), H - vb.h);
    };
    const toSvg = (cx, cy) => {
      const r = svg.getBoundingClientRect();
      return { x: vb.x + (cx - r.left) / r.width * vb.w, y: vb.y + (cy - r.top) / r.height * vb.h };
    };
    const zoomAt = (f, p) => {
      const nw = Math.min(W, Math.max(150, vb.w * f)), s = nw / vb.w;
      vb.x = p.x - (p.x - vb.x) * s; vb.y = p.y - (p.y - vb.y) * s; vb.w = nw; clamp(); set();
    };

    // dots: hover on desktop, first tap shows the card on touch
    svg.querySelectorAll('.dot').forEach((dot) => {
      if (fine) {
        dot.addEventListener('mouseenter', () => showTip(dot));
        dot.addEventListener('focus', () => showTip(dot));
      }
      dot.addEventListener('click', (ev) => {
        if (dragMoved) { ev.preventDefault(); return; }
        if (!fine && tipFor !== dot) { ev.preventDefault(); showTip(dot); }
      });
    });
    wrap.addEventListener('mouseleave', () => { if (fine) hideTip(); });
    document.addEventListener('click', (ev) => { if (!wrap.contains(ev.target)) hideTip(); });

    // zoom and pan only on the full explorer
    let dragMoved = false;
    if (!wrap.classList.contains('explore-map')) return;
    wrap.querySelectorAll('.zoom button').forEach((b) => b.addEventListener('click', () => {
      const c = { x: vb.x + vb.w / 2, y: vb.y + vb.h / 2 };
      if (b.dataset.z === 'in') zoomAt(0.6, c);
      else if (b.dataset.z === 'out') zoomAt(1 / 0.6, c);
      else { vb.x = 0; vb.y = 0; vb.w = W; clamp(); set(); }
    }));
    svg.addEventListener('wheel', (ev) => {
      if (!(ev.ctrlKey || ev.metaKey)) return; // pinch on trackpads sends ctrl+wheel; plain scrolling stays page scrolling
      ev.preventDefault();
      zoomAt(Math.exp(ev.deltaY * 0.01), toSvg(ev.clientX, ev.clientY));
    }, { passive: false });
    svg.addEventListener('dblclick', (ev) => { ev.preventDefault(); zoomAt(0.55, toSvg(ev.clientX, ev.clientY)); });
    let down = null;
    const pts = new Map();
    let pinch = null;
    svg.addEventListener('pointerdown', (ev) => {
      pts.set(ev.pointerId, { x: ev.clientX, y: ev.clientY });
      if (pts.size === 2) {
        const [a, b] = [...pts.values()];
        pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), w: vb.w, c: toSvg((a.x + b.x) / 2, (a.y + b.y) / 2) };
        down = null; return;
      }
      if (vb.w >= W - 1 && ev.pointerType !== 'mouse') return; // let the page scroll when the map isn't zoomed
      down = { x: ev.clientX, y: ev.clientY, vx: vb.x, vy: vb.y }; dragMoved = false;
    });
    svg.addEventListener('pointermove', (ev) => {
      if (pts.has(ev.pointerId)) pts.set(ev.pointerId, { x: ev.clientX, y: ev.clientY });
      if (pinch && pts.size === 2) {
        const [a, b] = [...pts.values()];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        const target = Math.min(W, Math.max(150, pinch.w * pinch.d / d));
        zoomAt(target / vb.w, pinch.c); dragMoved = true; return;
      }
      if (!down) return;
      const r = svg.getBoundingClientRect();
      const dx = (ev.clientX - down.x) / r.width * vb.w, dy = (ev.clientY - down.y) / r.height * vb.h;
      if (Math.abs(ev.clientX - down.x) + Math.abs(ev.clientY - down.y) > 5) dragMoved = true;
      if (!dragMoved) return;
      vb.x = down.vx - dx; vb.y = down.vy - dy; clamp(); set();
    });
    const end = (ev) => { pts.delete(ev.pointerId); if (pts.size < 2) pinch = null; down = null; setTimeout(() => { dragMoved = false; }, 0); };
    svg.addEventListener('pointerup', end); svg.addEventListener('pointercancel', end); svg.addEventListener('pointerleave', end);
  });

  // filters and search (Explore page)
  const grid = document.getElementById('hgrid');
  if (grid) {
    const cards = [...grid.querySelectorAll('.hcard')];
    const dots = [...document.querySelectorAll('.explore-map .dot')];
    const regBtns = [...document.querySelectorAll('#regions button')];
    const tagBtns = [...document.querySelectorAll('#tags button')];
    const q = document.getElementById('q');
    const count = document.getElementById('count');
    const empty = document.getElementById('empty');
    const st = { region: '', tags: new Set(), q: '' };
    const ok = (el) => {
      if (st.region && el.dataset.region !== st.region) return false;
      const t = el.dataset.tags.split(' ');
      for (const x of st.tags) if (!t.includes(x)) return false;
      if (st.q) {
        const name = (el.dataset.name || el.getAttribute('aria-label') || '').toLowerCase();
        if (!name.includes(st.q) && !(el.dataset.zips || '').includes(st.q)) return false;
      }
      return true;
    };
    const apply = () => {
      let n = 0;
      cards.forEach((c) => { const v = ok(c); c.hidden = !v; if (v) n++; });
      dots.forEach((d) => d.classList.toggle('off', !ok(d)));
      regBtns.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.region === st.region)));
      tagBtns.forEach((b) => b.setAttribute('aria-pressed', String(st.tags.has(b.dataset.tag))));
      count.textContent = n === cards.length ? '' : 'Showing ' + n + ' of ' + cards.length;
      empty.hidden = n > 0;
      const h = [st.region, ...st.tags].filter(Boolean).join('+');
      history.replaceState(null, '', h ? '#' + h : location.pathname);
    };
    regBtns.forEach((b) => b.addEventListener('click', () => { st.region = b.dataset.region; apply(); }));
    tagBtns.forEach((b) => b.addEventListener('click', () => { const t = b.dataset.tag; st.tags.has(t) ? st.tags.delete(t) : st.tags.add(t); apply(); }));
    q.addEventListener('input', () => { st.q = q.value.trim().toLowerCase(); apply(); });
    const init = location.hash.slice(1).split('+').filter(Boolean);
    init.forEach((h) => {
      if (regBtns.some((b) => b.dataset.region === h)) st.region = h;
      else if (tagBtns.some((b) => b.dataset.tag === h)) st.tags.add(h);
    });
    if (init.length) apply();
    // hovering a card lights up its dot on the map
    const bySlug = Object.fromEntries(dots.map((d) => [d.dataset.slug, d]));
    cards.forEach((c) => {
      c.addEventListener('mouseenter', () => { const d = bySlug[c.dataset.slug]; if (d) d.classList.add('hl'); });
      c.addEventListener('mouseleave', () => { const d = bySlug[c.dataset.slug]; if (d) d.classList.remove('hl'); });
    });
    dots.forEach((d) => {
      const c = grid.querySelector('.hcard[data-slug="' + d.dataset.slug + '"]');
      d.addEventListener('mouseenter', () => { if (c) c.classList.add('hl'); });
      d.addEventListener('mouseleave', () => { if (c) c.classList.remove('hl'); });
    });
  }
}
