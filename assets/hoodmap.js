// Local LA: every place in a neighborhood's guide, pinned on a real map (USGS imagery with street labels, public domain).
(() => {
  const el = document.getElementById('hoodmap');
  const data = document.getElementById('hoodmap-data');
  if (!el || !data || !window.L) return;
  const D = JSON.parse(data.textContent);
  if (!D.pts || !D.pts.length) { el.closest('section').hidden = true; return; }
  const esc = (t) => String(t == null ? '' : t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const map = L.map(el, { scrollWheelZoom: false, zoomSnap: 0.5, minZoom: 10, maxZoom: 18 });
  const usgs = (k) => L.tileLayer('https://basemap.nationalmap.gov/arcgis/rest/services/' + k + '/MapServer/tile/{z}/{y}/{x}', {
    maxNativeZoom: 16, maxZoom: 18,
    attribution: 'Map data: <a href="https://www.usgs.gov/programs/national-geospatial-program/national-map" target="_blank" rel="noopener">USGS</a>'
  });
  const sat = usgs('USGSImageryOnly').addTo(map);
  L.control.layers({ Satellite: sat, Streets: usgs('USGSTopo') }, null, { position: 'topright', collapsed: false }).addTo(map);
  map.attributionControl.setPrefix('<a href="https://leafletjs.com" target="_blank" rel="noopener">Leaflet</a>');
  const marks = {};
  const layer = L.featureGroup().addTo(map);
  D.pts.forEach((p) => {
    const icon = L.divIcon({ className: 'hm-pin hm-' + p.g, html: '<i></i><b>' + esc(p.n) + '</b>', iconSize: [16, 16], iconAnchor: [8, 8] });
    const m = L.marker([p.lat, p.lng], { icon, title: p.n, riseOnHover: true });
    m.bindPopup('<div class="hm-pop"><small>' + esc(p.sl) + (p.near ? ' &middot; ' + esc(p.near) : '') + (p.p ? ' &middot; ' + esc(p.p) : '') + '</small>'
      + '<b>' + esc(p.n) + '</b><span>' + esc(p.a) + '</span><p>' + esc(p.w) + '</p>'
      + '<div><a href="#pl-' + p.i + '" data-go="' + p.i + '">Read more</a><a href="' + esc(p.u) + '" target="_blank" rel="noopener">Directions &#8599;</a></div></div>',
    { closeButton: false, maxWidth: 290, minWidth: 220, autoPanPadding: [20, 20] });
    m.on('mouseover', () => m.openPopup());
    m.addTo(layer);
    marks[p.i] = [p, m];
  });
  const fit = (ms) => {
    if (!ms.length) return;
    if (ms.length === 1) { map.setView(ms[0].getLatLng(), 16); return; }
    map.fitBounds(L.featureGroup(ms).getBounds(), { padding: [34, 34], maxZoom: 16 });
  };
  fit(Object.values(marks).map((x) => x[1]));
  const labels = () => el.classList.toggle('labels', map.getZoom() >= 15);
  map.on('zoomend', labels); labels();
  el.addEventListener('click', () => map.scrollWheelZoom.enable(), { once: true });
  addEventListener('resize', () => map.invalidateSize());

  // filter chips
  const btns = [...document.querySelectorAll('.hm-bar [data-hm]')];
  btns.forEach((b) => b.addEventListener('click', () => {
    const k = b.dataset.hm;
    btns.forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    const shown = [];
    Object.values(marks).forEach(([p, m]) => {
      const on = !k || p.s === k;
      if (on) { if (!map.hasLayer(m)) m.addTo(layer); shown.push(m); } else if (map.hasLayer(m)) layer.removeLayer(m);
    });
    map.closePopup();
    fit(shown);
  }));

  // "On the map" buttons on the cards, and "Read more" in the popups
  const focus = (i) => {
    const x = marks[i]; if (!x) return;
    const [, m] = x;
    if (!map.hasLayer(m)) { btns[0] && btns[0].click(); }
    el.scrollIntoView({ block: 'center', behavior: 'smooth' });
    setTimeout(() => { map.setView(m.getLatLng(), Math.max(map.getZoom(), 16)); m.openPopup(); }, 380);
  };
  document.addEventListener('click', (ev) => {
    const pin = ev.target.closest('[data-pin]');
    if (pin) { ev.preventDefault(); focus(+pin.dataset.pin); return; }
    const go = ev.target.closest('.hm-pop [data-go]');
    if (go) {
      const card = document.getElementById('pl-' + go.dataset.go);
      if (card) { ev.preventDefault(); card.scrollIntoView({ block: 'center', behavior: 'smooth' }); card.classList.add('flash'); setTimeout(() => card.classList.remove('flash'), 1600); }
    }
  });
})();
