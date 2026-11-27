// Local LA: the pockets inside each neighborhood, drawn street by street. Boundaries are our own research.
(() => {
  const el = document.getElementById('pkmap');
  if (!el || !window.L) return;
  const esc = (t) => String(t == null ? '' : t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const dec = (s) => { const pts = []; let i = 0, la = 0, lo = 0; while (i < s.length) { for (let k = 0; k < 2; k++) { let r = 0, sh = 0, b; do { b = s.charCodeAt(i++) - 63; r |= (b & 31) << sh; sh += 5; } while (b >= 32); const v = r & 1 ? ~(r >> 1) : r >> 1; if (k) lo += v; else la += v; } pts.push([la / 1e5, lo / 1e5]); } return pts; };
  const PAL = ['#b5652d', '#2f6f73', '#8c3b52', '#5b6b2e', '#4b4f9c', '#a07a1f', '#6d3f8f', '#1f6b45', '#9c4a1a', '#3d6a99', '#8a5a44', '#476b2f'];
  const start = async () => {
    let D;
    const inline = document.getElementById('pkmap-data');
    if (inline) D = JSON.parse(inline.textContent);
    else { const r = await fetch('/assets/pockets.json?v=' + (document.querySelector('meta[name=ng-v]')||{}).content||''); D = await r.json(); }
    const map = L.map(el, { scrollWheelZoom: false, zoomSnap: 0.5, minZoom: 10, maxZoom: 18 });
    const usgs = (k) => L.tileLayer('https://basemap.nationalmap.gov/arcgis/rest/services/' + k + '/MapServer/tile/{z}/{y}/{x}', {
      maxNativeZoom: 16, maxZoom: 18,
      attribution: 'Map data: <a href="https://www.usgs.gov/programs/national-geospatial-program/national-map" target="_blank" rel="noopener">USGS</a> &middot; Boundaries: Nathaniel Grivas'
    });
    const streets = usgs('USGSTopo').addTo(map);
    L.control.layers({ Streets: streets, Satellite: usgs('USGSImageryOnly') }, null, { position: 'topright', collapsed: false }).addTo(map);
    map.attributionControl.setPrefix('<a href="https://leafletjs.com" target="_blank" rel="noopener">Leaflet</a>');
    const focus = L.featureGroup().addTo(map), ctx = L.featureGroup().addTo(map);
    const byId = {};
    const areaCol = {};
    let ci = 0;
    const colorFor = (p, idx) => D.all ? (areaCol[p.a] = areaCol[p.a] || PAL[(ci++) % PAL.length]) : PAL[idx % PAL.length];
    (D.ctx || []).forEach((p) => {
      const poly = L.polygon(dec(p.e), { color: '#6b6258', weight: 1.4, dashArray: '4 4', fill: true, fillOpacity: 0.04, interactive: true });
      poly.bindTooltip(esc(p.n) + (p.an ? ' <small>' + esc(p.an) + '</small>' : ''), { sticky: true, className: 'pk-tip' });
      poly.on('click', () => { if (p.u) location.href = p.u + '#pockets'; });
      poly.addTo(ctx);
    });
    (D.pk || []).forEach((p, idx) => {
      const col = colorFor(p, idx);
      const poly = L.polygon(dec(p.e), { color: col, weight: 2.2, fillColor: col, fillOpacity: 0.16 });
      poly.bindTooltip(esc(p.n), { permanent: true, direction: 'center', className: 'pk-lab', opacity: 1 });
      poly.bindPopup('<div class="pk-pop"><small>' + esc(p.an || '') + '</small><b>' + esc(p.n) + '</b>' + (p.b ? '<em>' + esc(p.b) + '</em>' : '') + '<p>' + esc(p.d || '') + '</p>'
        + (D.all && p.u ? '<a href="' + esc(p.u) + '#pockets">Explore ' + esc(p.an) + ' &rarr;</a>' : '<a href="#pk-' + esc(p.i) + '" data-pkgo="' + esc(p.i) + '">Read more</a>') + '</div>', { maxWidth: 300, minWidth: 220, closeButton: false, autoPanPadding: [24, 24] });
      poly.on('mouseover', () => { poly.setStyle({ fillOpacity: 0.34, weight: 3 }); hl(p.i, true); });
      poly.on('mouseout', () => { poly.setStyle({ fillOpacity: 0.16, weight: 2.2 }); hl(p.i, false); });
      poly.addTo(focus);
      byId[p.i] = poly;
    });
    const hl = (id, on) => { const c = document.getElementById('pk-' + id); if (c) c.classList.toggle('on', on); };
    const b = focus.getLayers().length ? focus.getBounds() : ctx.getBounds();
    if (b.isValid()) map.fitBounds(b, { padding: [18, 18] });
    const labels = () => el.classList.toggle('pk-labels', map.getZoom() >= (D.all ? 13.5 : 12.5));
    map.on('zoomend', labels); labels();
    el.addEventListener('click', () => map.scrollWheelZoom.enable(), { once: true });
    addEventListener('resize', () => map.invalidateSize());
    const go = (id) => { const poly = byId[id]; if (!poly) return; el.scrollIntoView({ block: 'center', behavior: 'smooth' }); setTimeout(() => { map.fitBounds(poly.getBounds(), { padding: [40, 40], maxZoom: 16 }); poly.openPopup(); }, 350); };
    document.querySelectorAll('[data-pk]').forEach((c) => {
      const id = c.dataset.pk, poly = byId[id]; if (!poly) return;
      c.addEventListener('mouseenter', () => poly.setStyle({ fillOpacity: 0.36, weight: 3.2 }));
      c.addEventListener('mouseleave', () => poly.setStyle({ fillOpacity: 0.16, weight: 2.2 }));
      const btn = c.querySelector('[data-pkshow]'); if (btn) btn.addEventListener('click', (ev) => { ev.preventDefault(); go(id); });
    });
    document.addEventListener('click', (ev) => { const a = ev.target.closest('[data-pkgo]'); if (!a) return; const card = document.getElementById('pk-' + a.dataset.pkgo); if (card) { ev.preventDefault(); map.closePopup(); card.scrollIntoView({ block: 'center', behavior: 'smooth' }); card.classList.add('flash'); setTimeout(() => card.classList.remove('flash'), 1600); } });
    const q = document.getElementById('pk-q');
    if (q && D.all) {
      const list = document.getElementById('pk-res');
      q.addEventListener('input', () => {
        const t = q.value.trim().toLowerCase(); list.innerHTML = '';
        if (t.length < 2) return;
        D.pk.filter((p) => (p.n + ' ' + p.an).toLowerCase().includes(t)).slice(0, 8).forEach((p) => {
          const a = document.createElement('button'); a.type = 'button'; a.innerHTML = '<b>' + esc(p.n) + '</b> <span>' + esc(p.an) + '</span>';
          a.addEventListener('click', () => { list.innerHTML = ''; q.value = p.n; map.fitBounds(byId[p.i].getBounds(), { padding: [40, 40], maxZoom: 16 }); byId[p.i].openPopup(); });
          list.appendChild(a);
        });
      });
    }
  };
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((en) => { if (en.some((x) => x.isIntersecting)) { io.disconnect(); start(); } }, { rootMargin: '400px' });
    io.observe(el);
  } else start();
})();
