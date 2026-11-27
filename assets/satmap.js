// Explore LA: a real satellite map (USGS imagery, public domain) with every neighborhood, plus filters and search that drive the map and the cards.
(() => {
  const el = document.getElementById('satmap');
  const data = document.getElementById('satmap-data');
  if (!el || !data) return;
  const pts = JSON.parse(data.textContent);
  const markers = {};
  let map = null, start = 11, home = null;
  if (window.L) {
    map = L.map(el, { scrollWheelZoom: false, zoomSnap: 0.5, minZoom: 9, maxZoom: 16, attributionControl: true, fadeAnimation: false });
    L.tileLayer('https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 16, attribution: 'Imagery: <a href="https://www.usgs.gov/programs/national-geospatial-program/national-map" target="_blank" rel="noopener">USGS</a>'
    }).addTo(map);
    const group = L.featureGroup().addTo(map);
    pts.forEach((p) => {
      const icon = L.divIcon({ className: 'sm-pin', html: '<i></i><b>' + p.name + '</b>', iconSize: [14, 14], iconAnchor: [7, 7] });
      const m = L.marker([p.lat, p.lng], { icon, title: p.name, riseOnHover: true });
      const img = p.img ? '<img src="' + p.img + '" alt="" loading="lazy">' : '';
      m.bindPopup('<a class="sm-pop" href="' + p.url + '">' + img + '<b>' + p.name + '</b><span>' + p.line + '</span><em>Open the guide &rarr;</em></a>', { closeButton: false, maxWidth: 260, minWidth: 220 });
      m.on('mouseover', () => m.openPopup());
      m.addTo(group);
      markers[p.slug] = m;
    });
    map.attributionControl.setPrefix('<a href="https://leafletjs.com" target="_blank" rel="noopener">Leaflet</a>');
    // Start one step closer than "fit everything" so the names are readable right away. One setView, so tiles load once.
    const med = (a) => { const v = a.slice().sort((x, y) => x - y); return v[Math.floor(v.length / 2)]; };
    home = [med(pts.map((p) => p.lat)), med(pts.map((p) => p.lng))];
    map.setView(home, map.getBoundsZoom(group.getBounds(), false, L.point(48, 48)) + 1, { animate: false });
    start = map.getZoom();
    const labels = () => el.classList.toggle('labels', map.getZoom() >= (el.clientWidth < 700 ? start + 1 : Math.min(11.5, start)));
    map.on('zoomend', labels); labels();
    el.addEventListener('click', () => map.scrollWheelZoom.enable(), { once: true });
    window.addEventListener('resize', () => map.invalidateSize());
  }

  // filters and search
  const grid = document.getElementById('hgrid');
  if (!grid) return;
  const cards = [...grid.querySelectorAll('.hcard')];
  const regBtns = [...document.querySelectorAll('#regions button')];
  const tagBtns = [...document.querySelectorAll('#tags button')];
  const q = document.getElementById('q');
  const count = document.getElementById('count');
  const empty = document.getElementById('empty');
  const st = { region: '', tags: new Set(), q: '' };
  const ok = (d) => {
    if (st.region && d.region !== st.region) return false;
    const t = (d.tags || '').split(' ');
    for (const x of st.tags) if (!t.includes(x)) return false;
    if (st.q && !(d.name || '').toLowerCase().includes(st.q) && !(d.zips || '').includes(st.q)) return false;
    return true;
  };
  const apply = () => {
    let n = 0;
    cards.forEach((c) => { const v = ok({ region: c.dataset.region, tags: c.dataset.tags, name: c.dataset.name, zips: c.dataset.zips }); c.hidden = !v; if (v) n++; });
    if (map) {
      const shown = [];
      pts.forEach((p) => {
        const m = markers[p.slug];
        const v = ok(p);
        if (v) { if (!map.hasLayer(m)) m.addTo(map); shown.push(m.getLatLng()); } else if (map.hasLayer(m)) map.removeLayer(m);
      });
      if (shown.length && shown.length < pts.length) map.fitBounds(L.latLngBounds(shown), { padding: [40, 40], maxZoom: 14 });
      else if (shown.length === pts.length) { map.setView(home, start, { animate: false }); }
    }
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
  // hovering a card opens its pin on the map
  cards.forEach((c) => {
    c.addEventListener('mouseenter', () => { const m = markers[c.dataset.slug]; if (m && map && map.hasLayer(m)) m.openPopup(); });
  });
})();
