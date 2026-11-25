// Intake: goal-first questions, tap or type. Typed answers are read in the browser and mapped to the closest options.
(() => {
  const root = document.querySelector('[data-intake]');
  if (!root || !window.HOODS) return;
  const H = window.HOODS;
  const BY = Object.fromEntries(H.map((h) => [h.slug, h]));
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  // ------------------------------------------------------------ places people commute to
  const ANCH = {
    sm: ['Santa Monica / Venice', [34.016, -118.48], ['santa monica', 'venice', 'snap', 'ocean park', 'main street', 'abbot kinney', 'third street promenade']],
    cc: ['Century City / Westwood / UCLA', [34.062, -118.43], ['century city', 'westwood', 'ucla', 'brentwood', 'west la', 'sawtelle', 'avenue of the stars', 'caa']],
    bh: ['Beverly Hills', [34.07, -118.4], ['beverly hills', 'rodeo', 'wilshire blvd beverly']],
    sb: ['Culver City / Playa Vista', [34.0, -118.41], ['culver', 'playa vista', 'silicon beach', 'google', 'sony', 'amazon studios', 'apple tv', 'hbo', 'marina del rey', 'mdr', 'playa']],
    weho: ['West Hollywood / Hollywood', [34.093, -118.35], ['west hollywood', 'weho', 'hollywood', 'netflix', 'sunset strip', 'paramount', 'sunset blvd']],
    mid: ['Mid-City / Cedars-Sinai', [34.07, -118.36], ['mid city', 'mid-city', 'miracle mile', 'cedars', 'fairfax', 'la brea', 'koreatown', 'ktown', 'k-town', 'hancock park', 'larchmont', 'beverly center', 'the grove']],
    dtla: ['Downtown LA', [34.05, -118.25], ['downtown', 'dtla', 'arts district', 'usc', 'city hall', 'financial district', 'staples', 'crypto.com']],
    bur: ['Burbank / Studio City / studios', [34.155, -118.34], ['burbank', 'disney', 'warner', 'universal', 'studio city', 'toluca', 'nbc', 'radford', 'studios']],
    sfv: ['Sherman Oaks / Encino', [34.155, -118.47], ['sherman oaks', 'encino', 'van nuys', 'ventura blvd', 'tarzana', 'valley']],
    wh: ['Woodland Hills / Warner Center', [34.18, -118.6], ['woodland hills', 'warner center', 'calabasas', 'canoga', 'west hills', 'agoura', 'thousand oaks']],
    lax: ['LAX / El Segundo / Hawthorne', [33.93, -118.4], ['lax', 'airport', 'el segundo', 'hawthorne', 'spacex', 'westchester', 'inglewood', 'sofi', 'lmu', 'loyola marymount']],
    pas: ['Pasadena / Glendale', [34.15, -118.2], ['pasadena', 'glendale', 'caltech', 'jpl', 'eagle rock', 'occidental']],
    east: ['Silver Lake / Los Feliz / Echo Park', [34.09, -118.27], ['silver lake', 'silverlake', 'los feliz', 'echo park', 'atwater', 'griffith', 'highland park', 'kaiser sunset', 'childrens hospital', "children's hospital"]],
    mal: ['Malibu / Palisades', [34.04, -118.6], ['malibu', 'palisades', 'pepperdine', 'topanga']],
    south: ['South Bay', [33.88, -118.4], ['manhattan beach', 'redondo', 'hermosa', 'torrance', 'south bay', 'long beach']],
    home: ['I work from home', null, ['remote', 'from home', 'wfh', 'home office', 'retired', 'no commute', "don't commute", 'dont commute']],
  };
  const REGIONS = ['Coast', 'Westside', 'Beverly Hills & the Hills', 'Central', 'Eastside', 'Valley'];

  const OPT = {
    goal: [['buy', 'Buy a home to live in'], ['invest', 'Buy to rent out'], ['build', 'Build or develop'], ['rent', 'Rent a place'], ['sell', 'Sell a property']],
    budget: [['u1', 'Under $1M'], ['1to2', '$1M to $2M'], ['2to35', '$2M to $3.5M'], ['35to6', '$3.5M to $6M'], ['6p', '$6M and up'], ['lender', "Not sure yet. I'd like to talk to a lender"]],
    rentbudget: [['r3', 'Under $3,000 a month'], ['r5', '$3,000 to $5,000'], ['r8', '$5,000 to $8,000'], ['r15', '$8,000 to $15,000'], ['r15p', '$15,000 and up']],
    pay: [['cash', 'All cash'], ['pre', 'Loan, already pre-approved'], ['loan', 'Loan, not pre-approved yet'], ['1031', '1031 exchange']],
    when: [['now', 'Within 3 months'], ['soon', '3 to 6 months'], ['later', '6 to 12 months'], ['explore', 'Just looking for now']],
    where: Object.entries(ANCH).map(([k, v]) => [k, v[0]]),
    areas: REGIONS.map((r) => [r, { Coast: 'The coast', Westside: 'Westside', 'Beverly Hills & the Hills': 'Beverly Hills & the hills', Central: 'Hollywood & Mid-City', Eastside: 'Silver Lake, Los Feliz, Echo Park', Valley: 'The Valley' }[r]]).concat([['any', 'Anywhere the numbers work']]),
    strategy: [['ltr', 'Long-term rental'], ['mtr', 'Furnished, 30+ day stays'], ['str', 'Short-term rental'], ['flip', 'Fix and flip'], ['adu', 'Add an ADU or split the lot'], ['mf', 'Multifamily building']],
    build: [['spec', 'New single-family home'], ['adu', 'ADUs or a lot split'], ['small', 'Duplex to fourplex'], ['apts', 'Apartments, 5+ units'], ['condo', 'Condos or townhomes']],
    land: [['own', 'I own it'], ['need', 'I need a lot'], ['teardown', 'I want a teardown']],
    must: [['beach', 'Near the beach'], ['walkable', 'Walk to coffee and dinner'], ['schools', 'Strong public schools'], ['yard', 'Space and a yard'], ['views', 'A view'], ['quiet', 'Quiet street'], ['nightlife', 'Nightlife'], ['transit', 'Near the Metro'], ['value', 'More home for the money'], ['luxury', 'Top-tier luxury'], ['creative', 'Arts and creative scene'], ['golf', 'Near a public golf course'], ['hikes', 'Near parks and trails']],
    home: [['house', 'House'], ['condo', 'Condo or townhome'], ['multi', 'Duplex to fourplex, live in one'], ['land', 'Land to build on'], ['open', 'Open to anything']],
    renthome: [['house', 'House'], ['condo', 'Apartment or condo'], ['open', 'Open to anything']],
    beds: [['1', '1'], ['2', '2'], ['3', '3'], ['4', '4'], ['5', '5+']],
    who: [['solo', 'Just me'], ['partner', 'Partner'], ['kids', 'Kids'], ['pets', 'Pets'], ['family', 'Parents or extended family']],
    sell_next: [['buyla', 'Yes, in LA'], ['buyout', 'Yes, outside LA'], ['no', 'No'], ['unsure', 'Not sure yet']],
  };

  const A = {}; // answers
  const RAW = {}; // typed text per step
  const AUTO = new Set(); // steps answered from something typed earlier
  const CUSTOM = []; // typed places: {label, ll}
  const PREF = new Set(); // typed neighborhoods for investors/builders

  const STEPS = {
    goal: { q: () => 'What are you looking to do?', o: () => 'goal', one: true, ph: 'Or type it, like "buy a duplex in Venice and live in one unit"' },
    budget: { q: () => (A.goal === 'rent' ? 'What can you spend each month?' : "What's your budget?"), o: () => (A.goal === 'rent' ? 'rentbudget' : 'budget'), one: true, ph: () => (A.goal === 'rent' ? 'Or type it, like "$4,500 a month"' : 'Or type it, like "around $1.8M"') },
    pay: { q: () => 'How are you paying?', o: () => 'pay', one: true, ph: 'Or type it' },
    when: { q: () => (A.goal === 'rent' ? 'When do you want to move?' : A.goal === 'sell' ? 'When do you want to sell?' : A.goal === 'build' ? 'When do you want to start?' : 'When do you want to buy?'), o: () => 'when', one: true, ph: 'Or type it, like "by June"' },
    where: { q: () => 'Where do you need to be most days?', o: () => 'where', many: true, ph: 'Type a workplace, school or address, like "Cedars-Sinai" or "SpaceX"' },
    areas: { q: () => (A.goal === 'build' ? 'Where do you want to build?' : 'Where do you want to invest?'), o: () => 'areas', many: true, ph: 'Or type neighborhoods or ZIP codes' },
    strategy: { q: () => "What's the plan for it?", o: () => 'strategy', many: true, ph: 'Or describe it' },
    build: { q: () => 'What do you want to build?', o: () => 'build', many: true, ph: 'Or describe the project' },
    land: { q: () => 'Do you have the land?', o: () => 'land', one: true, ph: 'Or type the address' },
    must: { q: () => 'Pick up to three must-haves', o: () => 'must', many: true, max: 3, ph: 'Or type what matters, like "walk to the beach, good schools"' },
    home: { q: () => 'What kind of place?', o: () => (A.goal === 'rent' ? 'renthome' : 'home'), one: true, ph: 'Or type it' },
    beds: { q: () => 'How many bedrooms?', o: () => 'beds', one: true, ph: 'Or type it' },
    who: { q: () => "Who's moving in?", o: () => 'who', many: true, ph: 'Or type it, like "me, my wife and our dog"' },
    sell_addr: { q: () => 'Which property are you selling?', text: true, ph: 'Street address, or just the neighborhood' },
    sell_next: { q: () => 'Are you buying after you sell?', o: () => 'sell_next', one: true, ph: 'Or type it' },
  };

  const flow = () => {
    let f;
    switch (A.goal) {
      case 'buy': f = ['goal', 'budget', 'pay', 'when', 'where', 'must', 'home', 'beds', 'who']; break;
      case 'rent': f = ['goal', 'budget', 'when', 'where', 'must', 'home', 'beds', 'who']; break;
      case 'invest': f = ['goal', 'budget', 'pay', 'strategy', 'areas', 'when']; break;
      case 'build': f = ['goal', 'build', 'land', 'budget', 'pay', 'areas', 'when']; break;
      case 'sell': f = ['goal', 'sell_addr', 'when', 'sell_next'].concat(A.sell_next === 'buyla' ? ['budget', 'pay', 'where', 'must', 'home', 'beds', 'who'] : []); break;
      default: f = ['goal'];
    }
    return f.filter((k) => !(k === 'pay' && A.budget === 'lender'));
  };

  // ------------------------------------------------------------ reading typed answers
  const RX = {};
  const has = (t, words) => words.some((w) => {
    if (/[^a-z*'-]/.test(w)) return t.includes(w);
    const k = w;
    if (!RX[k]) RX[k] = new RegExp('\\b' + w.replace('*', '').replace(/[-']/g, (c) => '\\' + c) + (w.endsWith('*') ? '' : '\\b'));
    return RX[k].test(t);
  });
  const MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'];
  const MRX = /\b(?:by|in|before|around|until|after|early|late|mid)\s+(may)\b|\b(january|february|march|april|june|july|august|september|october|november|december)\b/;
  const money = (t, rent) => {
    const s = t.toLowerCase().replace(/,/g, '');
    const out = [];
    const re = /(\$)?\s*(\d+(?:\.\d+)?)\s*(million|mil|mm|m\b|k\b|thousand|grand)?/g;
    let m;
    while ((m = re.exec(s))) {
      let n = parseFloat(m[2]);
      const u = m[3] || '';
      if (/^(million|mil|mm|m)/.test(u)) n *= 1e6;
      else if (/^(k|thousand|grand)/.test(u)) n *= 1e3;
      if (!m[1] && !u && (n < 1000 || /^9\d{4}$/.test(m[2]) || /^(19|20)\d{2}$/.test(m[2]))) continue;
      if (/^\s*(sq|sf\b|square)/.test(s.slice(re.lastIndex, re.lastIndex + 8))) continue;
      out.push(n);
    }
    if (!out.length) return null;
    const v = Math.max(...out);
    if (rent || (v < 40000 && /mo|month|rent|lease/.test(s))) {
      return v < 3000 ? 'r3' : v < 5000 ? 'r5' : v < 8000 ? 'r8' : v < 15000 ? 'r15' : 'r15p';
    }
    if (v < 50000) return null;
    return v < 1e6 ? 'u1' : v <= 2e6 ? '1to2' : v <= 3.5e6 ? '2to35' : v <= 6e6 ? '35to6' : '6p';
  };
  const whenOf = (t, step) => {
    if (has(t, ['asap', 'right away', 'immediately', 'this month', 'next month', '30 days', '60 days', '90 days', 'now', 'soon', 'urgent', 'yesterday', 'right now'])) return 'now';
    const mm = t.match(MRX);
    const mo = mm ? MONTHS.indexOf(mm[1] || mm[2]) : -1;
    if (mo >= 0) {
      const now = new Date();
      let diff = mo - now.getMonth();
      if (diff <= 0) diff += 12;
      return diff <= 3 ? 'now' : diff <= 6 ? 'soon' : 'later';
    }
    if (/\b([3-6])\s*(months|mos|mo)\b/.test(t) || has(t, ['spring', 'summer', 'half a year'])) return 'soon';
    if (/\b([7-9]|1[0-2])\s*(months|mos)\b/.test(t) || has(t, ['year', 'fall', 'winter', '2027', '2028'])) return 'later';
    if (has(t, ['just looking', 'browsing', 'explor*', 'someday', 'eventually', 'curious', 'no rush', 'just seeing'])) return 'explore';
    if (step === 'when' && has(t, ['not sure', "don't know", 'dont know', 'unsure', 'depends'])) return 'explore';
    return null;
  };
  const read = (raw, step) => {
    const t = ' ' + raw.toLowerCase() + ' ';
    const f = {};
    // goal
    const buyW = has(t, ['buy*', 'purchas*', 'first home', 'own a', 'owning', 'mortgage', 'pre-approved', 'preapproved']);
    if (has(t, ['build', 'builder', 'develop*', 'construct*', 'teardown', 'tear down', 'ground up', 'ground-up', 'entitle*', 'subdivid*', 'spec home', 'adu', 'lot split'])) f.goal = 'build';
    else if (has(t, ['rent out', 'rental', 'rentals', 'cash flow', 'cashflow', 'invest*', 'income property', 'airbnb', 'cap rate', 'portfolio', 'roi', 'flip', 'flipping', '1031'])) f.goal = 'invest';
    else if (has(t, ['sell', 'selling', 'seller', 'list my', 'listing my', 'worth'])) f.goal = 'sell';
    else if (buyW) f.goal = 'buy';
    else if (has(t, ['rent', 'renting', 'lease', 'leasing', 'apartment for rent'])) f.goal = 'rent';
    else if (has(t, ['house', 'home', 'condo', 'townhouse', 'place', 'move', 'moving', 'relocat*'])) f.goal = 'buy';
    if (f.goal === 'sell' && buyW) f.sell_next = 'buyla';
    // budget
    const b = money(t, A.goal === 'rent' || f.goal === 'rent');
    if (b) { if (b[0] === 'r') f.rentbudget = b; else f.budget = b; }
    if (has(t, ['lender', 'not sure what i can afford', "don't know what i can afford", 'pre-qual', 'prequal*', 'how much can i', 'not sure', 'no idea', "don't know", 'dont know'])) { if (!b && (step === 'budget' || has(t, ['lender', 'afford', 'qualif*']))) f.budget = 'lender'; }
    // pay
    if (has(t, ['1031', 'exchange'])) f.pay = '1031';
    else if (/\bcash\b/.test(t) && !has(t, ['cash flow', 'cashflow'])) f.pay = 'cash';
    else if (has(t, ['pre-approved', 'preapproved', 'pre approved'])) f.pay = 'pre';
    else if (has(t, ['loan', 'mortgage', 'financ*', 'fha', 'va loan', 'conventional'])) f.pay = 'loan';
    // timing
    const w = whenOf(t, step); if (w) f.when = w;
    // places
    const where = []; const custom = [];
    Object.entries(ANCH).forEach(([k, v]) => { if (has(t, v[2])) where.push(k); });
    H.forEach((h) => {
      if (t.includes(h.name.toLowerCase()) || h.zips.split(/,\s*/).some((z) => t.includes(z))) custom.push(h);
    });
    for (let k = custom.length - 1; k >= 0; k--) {
      const nm = custom[k].name.toLowerCase();
      const longer = custom.filter((o) => o !== custom[k] && o.name.toLowerCase().includes(nm));
      if (longer.length) { let rest = t; longer.forEach((o) => { rest = rest.split(o.name.toLowerCase()).join(' '); }); if (!rest.includes(nm) && !custom[k].zips.split(/,\s*/).some((z) => t.includes(z))) custom.splice(k, 1); }
    }
    if (where.length) f.where = where;
    if (custom.length) f.hoods = custom;
    const regs = [];
    if (has(t, ['coast', 'beach'])) regs.push('Coast');
    if (has(t, ['westside', 'west side'])) regs.push('Westside');
    if (has(t, ['the hills', 'beverly hills', 'bel air', 'bel-air', 'hollywood hills'])) regs.push('Beverly Hills & the Hills');
    if (has(t, ['central', 'mid city', 'mid-city', 'midcity'])) regs.push('Central');
    if (has(t, ['eastside', 'east side', 'silver lake', 'los feliz', 'echo park'])) regs.push('Eastside');
    if (has(t, ['valley', 'sfv', 'the valley'])) regs.push('Valley');
    if (has(t, ['anywhere', 'wherever', "doesn't matter", 'dont care', "don't care", 'numbers work', 'pencil'])) regs.push('any');
    if (regs.length) f.areas = regs;
    // must-haves
    const MUST = { beach: ['beach*', 'ocean', 'sand', 'surf*'], walkable: ['walk*', 'coffee', 'shops', 'restaurant*'], schools: ['school*', 'education'], yard: ['yard', 'backyard', 'garden', 'pool', 'space', 'big lot'], views: ['view*', 'canyon', 'hillside'], quiet: ['quiet', 'peaceful', 'privacy', 'private', 'safe*'], nightlife: ['nightlife', 'bars', 'going out', 'clubs', 'night life'], transit: ['metro', 'train', 'transit', 'subway', 'no car'], value: ['affordable', 'cheap*', 'value', 'deal', 'for the money', 'bang for'], luxury: ['luxury', 'estate', 'gated', 'high end', 'high-end', 'prestig*'], creative: ['art', 'arts', 'creative', 'music', 'galler*'], golf: ['golf*'], hikes: ['hike', 'hikes', 'hiking', 'trail*', 'park', 'parks', 'outdoors'] };
    const must = Object.entries(MUST).filter(([, ws]) => has(t, ws)).map(([k]) => k);
    if (must.length) f.must = must;
    // home type and size
    if (has(t, ['duplex', 'triplex', 'fourplex', '4plex', '4-plex', 'units', 'multifamily', 'multi-family', 'multi family', 'income property'])) f.home = 'multi';
    else if (has(t, ['condo*', 'townho*', 'apartment*', 'loft', 'no yard'])) f.home = 'condo';
    else if (has(t, ['land', 'lot', 'vacant'])) f.home = 'land';
    else if (has(t, ['house', 'single family', 'single-family', 'sfr'])) f.home = 'house';
    const bd = t.match(/(\d)\s*\+?\s*(bed|br\b|bd\b|bedroom)/) || t.match(/\b(one|two|three|four|five)\s*(bed|bedroom)/);
    if (bd) { const n = { one: 1, two: 2, three: 3, four: 4, five: 5 }[bd[1]] || +bd[1]; f.beds = String(Math.min(5, Math.max(1, n))); }
    if (has(t, ['studio apartment', 'a studio', 'studio unit'])) f.beds = '1';
    // household
    const who = [];
    if (has(t, ['just me', 'myself', 'alone', 'single', 'only me'])) who.push('solo');
    if (has(t, ['wife', 'husband', 'partner', 'spouse', 'girlfriend', 'boyfriend', 'fiance', 'fiancé', 'my love', 'couple'])) who.push('partner');
    if (has(t, ['kid*', 'child*', 'son', 'sons', 'daughter*', 'baby', 'toddler*', 'twins', 'family of'])) who.push('kids');
    if (has(t, ['dog*', 'cat', 'cats', 'pet', 'pets', 'pupp*'])) who.push('pets');
    if (has(t, ['parents', 'mom', 'dad', 'mother', 'father', 'in-law', 'in-laws', 'grandma', 'grandpa'])) who.push('family');
    if (who.length) f.who = who;
    // investor plan
    const st = [];
    if (has(t, ['airbnb', 'short term', 'short-term', 'vacation', 'vrbo', 'str'])) st.push('str');
    if (has(t, ['mid term', 'mid-term', 'furnished', 'travel nurse', '30 day', '30-day', 'corporate'])) st.push('mtr');
    if (has(t, ['long term', 'long-term', 'tenant', 'cash flow', 'cashflow', 'buy and hold', 'hold it'])) st.push('ltr');
    if (has(t, ['flip*', 'fix and', 'renovat*', 'rehab*', 'value add', 'value-add'])) st.push('flip');
    if (has(t, ['adu', 'granny', 'back house', 'guest house', 'lot split', 'sb 9', 'sb9'])) st.push('adu');
    if (has(t, ['multifamily', 'multi-family', 'apartment building', 'units', 'duplex', 'triplex', 'fourplex'])) st.push('mf');
    if (st.length) f.strategy = st;
    const bu = [];
    if (has(t, ['spec', 'single family', 'single-family', 'new home', 'custom home', 'dream home'])) bu.push('spec');
    if (has(t, ['adu', 'lot split', 'sb 9', 'sb9'])) bu.push('adu');
    if (has(t, ['duplex', 'triplex', 'fourplex'])) bu.push('small');
    if (has(t, ['apartment*', 'units', 'multifamily', 'multi-family', 'mixed use', 'mixed-use'])) bu.push('apts');
    if (has(t, ['condo*', 'townho*', 'small lot'])) bu.push('condo');
    if (bu.length) f.build = bu;
    if (has(t, ['own it', 'already have', 'my lot', 'my land', 'inherit', 'we own', 'i own'])) f.land = 'own';
    else if (has(t, ['teardown', 'tear down', 'knock down', 'scrape'])) f.land = 'teardown';
    else if (has(t, ['need a lot', 'find a lot', 'looking for land', 'need land'])) f.land = 'need';
    if (has(t, ['outside la', 'out of state', 'another state', 'leaving la', 'moving away', 'out of la', 'out of california'])) f.sell_next = 'buyout';
    else if (has(t, ['also buy', 'buy another', 'upgrade', 'downsize', 'buy in la', 'buying in la'])) f.sell_next = 'buyla';
    else if (step === 'sell_next' && has(t, ['yes', 'yeah', 'yep', 'probably'])) f.sell_next = 'buyla';
    else if (step === 'sell_next' && has(t, ['no', 'nope', 'not buying', 'rent after', 'renting after'])) f.sell_next = 'no';
    else if (step === 'sell_next' && has(t, ['maybe', 'not sure', 'unsure', 'depends'])) f.sell_next = 'unsure';
    if (f.goal === 'sell' || step === 'sell_addr') { f.sellText = raw; delete f.home; delete f.beds; delete f.where; delete f.hoods; delete f.must; delete f.areas; }
    return f;
  };

  // apply what was read; returns labels for the current step
  const LBL = (o, v) => { const x = (OPT[o] || []).find((p) => p[0] === v); return x ? x[1] : v; };
  const apply = (f, cur) => {
    const map = { goal: 'goal', budget: 'budget', rentbudget: 'budget', pay: 'pay', when: 'when', where: 'where', areas: 'areas', strategy: 'strategy', build: 'build', land: 'land', must: 'must', home: 'home', beds: 'beds', who: 'who', sell_next: 'sell_next' };
    let got = [];
    Object.entries(f).forEach(([k, v]) => {
      if (k === 'hoods') return;
      const step = map[k];
      if (!step) return;
      if (step === cur) { A[step] = v; got = Array.isArray(v) ? v : [v]; }
      else if (A[step] === undefined) { A[step] = v; AUTO.add(step); }
    });
    if (f.sellText && A.sell_addr === undefined) { A.sell_addr = f.sellText; if (cur !== 'sell_addr') AUTO.add('sell_addr'); }
    (f.hoods || []).forEach((h) => {
      if (!CUSTOM.some((c) => c.label === h.name)) CUSTOM.push({ label: h.name, ll: h.ll });
      PREF.add(h.slug);
      if (cur === 'where' || cur === 'areas') got.push('hood:' + h.name);
    });
    if (f.must && A.must && A.must.length > 3) A.must = A.must.slice(0, 3);
    return got;
  };

  // ------------------------------------------------------------ rendering
  const host = $('.qhost', root), bar = $('.qbar i', root), back = $('.qback', root), count = $('.qcount', root);
  let cur = 'goal';
  const visible = () => flow().filter((k) => k === cur || !AUTO.has(k));

  const render = () => {
    const st = STEPS[cur];
    const list = visible();
    const i = list.indexOf(cur);
    bar.style.width = Math.round((i / Math.max(list.length, 1)) * 100) + '%';
    count.textContent = A.goal ? (i + 1) + ' of ' + list.length : '';
    back.hidden = i <= 0;
    const ph = typeof st.ph === 'function' ? st.ph() : st.ph;
    let body = '';
    if (st.text) {
      body = '<form class="qtype big"><input type="text" placeholder="' + esc(ph) + '" value="' + esc(RAW[cur] || '') + '" aria-label="' + esc(st.q()) + '"><button class="btn solid" type="submit">Next</button></form>';
    } else {
      const o = st.o();
      const sel = A[cur] === undefined ? [] : [].concat(A[cur]);
      body = '<div class="opts' + (st.many ? ' many' : '') + (o === 'beds' ? ' row' : '') + '">' +
        OPT[o].map(([v, l]) => '<button type="button" class="opt' + (sel.includes(v) ? ' sel' : '') + '" data-v="' + esc(v) + '" aria-pressed="' + sel.includes(v) + '">' + esc(l) + '</button>').join('') +
        (cur === 'where' || cur === 'areas' ? CUSTOM.map((c) => '<button type="button" class="opt sel custom" disabled>' + esc(c.label) + '</button>').join('') : '') +
        '</div>' +
        '<form class="qtype"><input type="text" placeholder="' + esc(ph) + '" aria-label="Type your own answer"><button class="btn" type="submit" aria-label="Use what I typed">&rarr;</button></form>' +
        '<p class="qread" hidden></p>' +
        (st.many || cur !== 'goal' ? '<div class="qnav">' + (st.many ? '<button type="button" class="btn solid qnext">Next</button>' : '') + (cur !== 'goal' ? '<button type="button" class="qskip">Skip</button>' : '') + '</div>' : '');
    }
    host.innerHTML = '<fieldset class="qstep"><legend>' + esc(st.q()) + '</legend>' + body + '</fieldset>';
    wire();
  };

  const track = () => { if (window.NG) { try { summary().forEach(([k, v]) => window.NG.answer(k, v)); } catch (e) { /* ignore */ } } };
  const next = () => {
    AUTO.delete(cur);
    track();
    const list = visible();
    const i = list.indexOf(cur);
    if (i + 1 < list.length) { cur = list[i + 1]; render(); }
    else finish();
  };

  const wire = () => {
    const st = STEPS[cur];
    const form = $('.qtype', host);
    const note = $('.qread', host);
    $$('.opt:not(.custom)', host).forEach((b) => b.addEventListener('click', () => {
      const v = b.dataset.v;
      if (st.many) {
        let arr = [].concat(A[cur] || []);
        arr = arr.includes(v) ? arr.filter((x) => x !== v) : arr.concat(v);
        if (st.max && arr.length > st.max) arr = arr.slice(arr.length - st.max);
        if (v === 'home' || v === 'any') arr = [v];
        else arr = arr.filter((x) => x !== 'home' && x !== 'any');
        A[cur] = arr;
        $$('.opt:not(.custom)', host).forEach((x) => { const on = arr.includes(x.dataset.v); x.classList.toggle('sel', on); x.setAttribute('aria-pressed', on); });
      } else {
        A[cur] = v;
        $$('.opt', host).forEach((x) => { const on = x === b; x.classList.toggle('sel', on); x.setAttribute('aria-pressed', on); });
        setTimeout(next, 170);
      }
    }));
    form.addEventListener('submit', (ev) => {
      ev.preventDefault();
      const val = $('input', form).value.trim();
      if (!val) return;
      RAW[cur] = val;
      if (st.text) { A[cur] = val; apply(read(val, cur), cur); next(); return; }
      const got = apply(read(val, cur), cur);
      const o = st.o();
      if (got.length) {
        const names = got.map((g) => (String(g).startsWith('hood:') ? g.slice(5) : LBL(o, g)));
        note.innerHTML = '<b>Got it:</b> ' + names.map(esc).join(', ');
        note.hidden = false;
        if (st.many) render(), ($('.qread', host).innerHTML = '<b>Got it:</b> ' + names.map(esc).join(', ')), ($('.qread', host).hidden = false);
        else { $$('.opt', host).forEach((x) => x.classList.toggle('sel', x.dataset.v === A[cur])); setTimeout(next, 650); }
      } else if (cur === 'goal') {
        note.innerHTML = 'Pick the closest option above so the next questions fit.';
        note.hidden = false;
      } else {
        if (A[cur] === undefined) A[cur] = 'other';
        note.innerHTML = '<b>Got it.</b> I\'ll read your note.';
        note.hidden = false;
        setTimeout(next, 650);
      }
    });
    const nx = $('.qnext', host); if (nx) nx.addEventListener('click', next);
    const sk = $('.qskip', host); if (sk) sk.addEventListener('click', () => { if (A[cur] === undefined) A[cur] = 'skip'; next(); });
  };

  back.addEventListener('click', () => {
    const list = flow();
    const i = list.indexOf(cur);
    if (i > 0) { cur = list[i - 1]; AUTO.delete(cur); render(); }
  });

  // ------------------------------------------------------------ scoring
  const R = (d) => d * Math.PI / 180;
  const mi = (a, b) => { const x = Math.sin(R(b[0] - a[0]) / 2) ** 2 + Math.cos(R(a[0])) * Math.cos(R(b[0])) * Math.sin(R(b[1] - a[1]) / 2) ** 2; return 3958.8 * 2 * Math.asin(Math.sqrt(x)); };
  const TIERS = {
    u1: { 1: 3, 2: 1, 3: -1, 4: -3 }, '1to2': { 1: 2, 2: 3, 3: 1, 4: -2 }, '2to35': { 1: 0, 2: 2, 3: 3, 4: 0 }, '35to6': { 1: -1, 2: 1, 3: 3, 4: 2 }, '6p': { 1: -2, 2: -1, 3: 1, 4: 3 },
    r3: { 1: 3, 2: 2, 3: 0, 4: -2 }, r5: { 1: 2, 2: 3, 3: 2, 4: -1 }, r8: { 1: 0, 2: 2, 3: 3, 4: 1 }, r15: { 1: -1, 2: 1, 3: 3, 4: 2 }, r15p: { 1: -2, 2: 0, 3: 1, 4: 3 },
  };
  const DUPLEX = ['beverly-grove', 'fairfax', 'pico-robertson', 'miracle-mile', 'palms', 'west-hollywood', 'east-hollywood', 'echo-park', 'venice', 'mar-vista', 'silver-lake', 'hollywood', 'north-hollywood', 'van-nuys', 'santa-monica', 'culver-city'];
  const OWN_DISTRICT = ['Santa Monica', 'Beverly Hills', 'Culver City'];
  const arr = (k) => [].concat(A[k] || []).filter((x) => x !== 'skip' && x !== 'other');
  const T = (h, t) => h.tags.includes(t);

  const score = (h) => {
    const living = A.goal === 'buy' || A.goal === 'rent' || A.sell_next === 'buyla';
    let s = 0; const why = [];
    const add = (n, w) => { s += n; if (w && n > 0) why.push(w); };
    const tier = TIERS[A.budget];
    if (tier) add(tier[h.tier] || 0, (tier[h.tier] || 0) >= 2 ? 'fits your budget' : '');
    // commute
    const anchors = (living ? arr('where') : []).filter((k) => ANCH[k] && ANCH[k][1]).map((k) => ({ label: ANCH[k][0].split(' / ')[0], ll: ANCH[k][1] }));
    if (living) anchors.push(...CUSTOM);
    anchors.forEach((a) => {
      const d = mi(h.ll, a.ll);
      const pts = Math.max(0, 3.4 - d / 2.4);
      add(pts, d < 4.5 ? (d < 1.2 ? 'right by ' + a.label : Math.round(d) + ' mi from ' + a.label) : '');
    });
    // must-haves
    const M = living ? arr('must') : [];
    const tag = { beach: 3, walkable: 2.5, yard: 2, views: 2.5, nightlife: 2.5, transit: 2.5, value: 2.5, luxury: 2.5, creative: 2 };
    const WHY = { beach: 'near the beach', walkable: 'walkable', yard: 'yards and space', views: 'views', nightlife: 'nightlife', transit: 'near the Metro', value: 'more for the money', luxury: 'luxury homes', creative: 'creative scene', quiet: 'quiet streets', family: 'family streets' };
    M.forEach((m) => {
      if (tag[m] && T(h, m)) add(tag[m], WHY[m]);
      if (m === 'schools') { if (T(h, 'family')) add(1.5); if (OWN_DISTRICT.includes(h.city)) add(1.8, 'its own school district'); }
      if (m === 'quiet') { if (T(h, 'quiet')) add(2, 'quiet streets'); if (T(h, 'nightlife')) s -= 1; }
      if (m === 'golf' && h.golf) add(2, 'public golf nearby');
      if (m === 'hikes' && (h.trails || T(h, 'views'))) add(2, 'parks and trails close by');
    });
    // home
    const home = living ? A.home : undefined;
    if (home === 'house') { if (T(h, 'yard')) add(1.5, 'houses with yards'); if (T(h, 'condo') && !T(h, 'yard')) s -= 1; }
    if (home === 'condo' && T(h, 'condo')) add(2, 'good condo choices');
    if (home === 'multi' && DUPLEX.includes(h.slug)) add(2.5, 'duplexes and small income buildings');
    if (home === 'land' && (T(h, 'yard') || T(h, 'value'))) add(1);
    if (['4', '5'].includes(A.beds) && (T(h, 'yard') || T(h, 'family'))) add(1);
    if (A.beds === '1' && (T(h, 'condo') || T(h, 'walkable'))) add(1);
    const W = living ? arr('who') : [];
    if (W.includes('kids')) { if (T(h, 'family')) add(2, 'family streets'); if (T(h, 'quiet')) add(1); }
    if (W.includes('pets') && T(h, 'yard')) add(1);
    if (W.includes('solo') && (T(h, 'walkable') || T(h, 'nightlife'))) add(1);
    if (W.includes('family') && T(h, 'yard')) add(1);
    // investors and builders
    const ST = A.goal === 'invest' ? arr('strategy') : [];
    if (ST.includes('ltr')) { if (T(h, 'value')) add(2, 'stronger rent-to-price'); if (T(h, 'transit') || T(h, 'walkable')) add(1, 'renter demand'); }
    if (ST.includes('mtr')) { if (T(h, 'walkable') || T(h, 'transit')) add(1.5, 'furnished-rental demand'); }
    if (ST.includes('str')) { if (T(h, 'beach')) add(2, 'visitor demand'); if (T(h, 'nightlife') || T(h, 'walkable')) add(1); }
    if (ST.includes('flip')) { if (T(h, 'value')) add(2, 'room to add value'); if (h.tier === 2 || h.tier === 3) add(1); }
    if (ST.includes('adu')) { if (T(h, 'yard')) add(2, 'lots with room for an ADU'); if (T(h, 'value')) add(1); }
    if (ST.includes('mf') && DUPLEX.includes(h.slug)) add(2, 'small multifamily stock');
    const BU = A.goal === 'build' ? arr('build') : [];
    if (BU.includes('spec')) { if (T(h, 'luxury') || T(h, 'views')) add(1.5, 'strong new-construction resale'); if (T(h, 'yard')) add(1); }
    if (BU.includes('adu')) { if (T(h, 'yard')) add(2, 'lots with room for an ADU'); if (T(h, 'value')) add(1); }
    if (BU.includes('small')) { if (T(h, 'yard') || T(h, 'value')) add(1.5); }
    if (BU.includes('apts') || BU.includes('condo')) { if (T(h, 'transit')) add(2, 'near transit'); if (T(h, 'walkable')) add(1); }
    const bigSale = ['35to6', '6p'].includes(A.budget) || BU.includes('spec');
    if ((A.goal === 'build' || A.goal === 'invest') && bigSale) {
      if (h.city === 'Los Angeles') s -= 1.2;
      else if (['Beverly Hills', 'West Hollywood', 'Malibu', 'LA County'].includes(h.city)) add(1.2, 'no city transfer tax on resale');
    }
    const AR = A.goal === 'invest' || A.goal === 'build' ? arr('areas') : [];
    if (AR.length && !AR.includes('any') && AR.includes(h.region)) add(3);
    if (AR.includes('any') && T(h, 'value')) add(1);
    if (PREF.has(h.slug)) add(living ? 2 : 4, 'you named it');
    return { s, why: [...new Set(why)].slice(0, 3) };
  };

  // ------------------------------------------------------------ results
  const res = $('.qres', root), lead = $('.qlead');
  const summary = () => {
    const rows = [];
    const L = (o, v) => LBL(o, v);
    const goal = L('goal', A.goal);
    rows.push(['Goal', goal]);
    if (A.sell_addr) rows.push(['Selling', A.sell_addr]);
    if (A.sell_next && A.sell_next !== 'skip') rows.push(['Buying after', L('sell_next', A.sell_next)]);
    if (A.budget && !['skip', 'other'].includes(A.budget)) rows.push(['Budget', L(A.goal === 'rent' ? 'rentbudget' : 'budget', A.budget)]);
    if (A.pay && !['skip', 'other'].includes(A.pay)) rows.push(['Paying', L('pay', A.pay)]);
    if (A.when && !['skip', 'other'].includes(A.when)) rows.push(['Timing', L('when', A.when)]);
    if (arr('strategy').length) rows.push(['Plan', arr('strategy').map((v) => L('strategy', v)).join(', ')]);
    if (arr('build').length) rows.push(['Build', arr('build').map((v) => L('build', v)).join(', ')]);
    if (A.land && !['skip', 'other'].includes(A.land)) rows.push(['Land', L('land', A.land)]);
    const wh = arr('where').map((v) => L('where', v));
    if (wh.length) rows.push(['Most days', wh.join(', ')]);
    if (CUSTOM.length && A.goal !== 'invest' && A.goal !== 'build') rows.push(['Named areas', CUSTOM.map((c) => c.label).join(', ')]);
    const ar = arr('areas').map((v) => L('areas', v)).concat(A.goal === 'invest' || A.goal === 'build' ? CUSTOM.map((c) => c.label) : []);
    if (ar.length) rows.push(['Areas', ar.join(', ')]);
    if (arr('must').length) rows.push(['Must-haves', arr('must').map((v) => L('must', v)).join(', ')]);
    if (A.home && !['skip', 'other'].includes(A.home)) rows.push(['Type', L(A.goal === 'rent' ? 'renthome' : 'home', A.home)]);
    if (A.beds && !['skip', 'other'].includes(A.beds)) rows.push(['Bedrooms', L('beds', A.beds)]);
    if (arr('who').length) rows.push(['Household', arr('who').map((v) => L('who', v)).join(', ')]);
    Object.entries(RAW).forEach(([k, v]) => { if (k !== 'sell_addr') rows.push(['In their words (' + k.replace('_', ' ') + ')', v]); });
    return rows;
  };

  const finish = () => {
    bar.style.width = '100%'; back.hidden = true; count.textContent = '';
    host.innerHTML = '';
    const rows = summary();
    const wantsLender = A.budget === 'lender' || A.pay === 'loan';
    const matchable = A.goal !== 'sell' || A.sell_next === 'buyla';
    const living = A.goal === 'buy' || A.goal === 'rent' || A.sell_next === 'buyla';
    let ranked = [];
    const picked = [];
    if (matchable) {
      ranked = H.map((h) => ({ h, ...score(h) })).sort((a, b) => b.s - a.s);
      [...PREF].forEach((sl) => { if (!picked.includes(sl)) picked.push(sl); });
      ranked.slice(0, 3).forEach((x) => { if (!picked.includes(x.h.slug) && picked.length < 4) picked.push(x.h.slug); });
    }
    const crit = () => {
      const c = [];
      const take = (o, k) => { if (A[k] && !['skip', 'other'].includes(A[k])) c.push(LBL(o, A[k])); };
      if (A.goal === 'rent') take('rentbudget', 'budget'); else take('budget', 'budget');
      if (A.beds && !['skip', 'other'].includes(A.beds)) c.push(A.beds.replace('5', '5') + '+ beds');
      if (living) take(A.goal === 'rent' ? 'renthome' : 'home', 'home');
      arr('strategy').forEach((v) => c.push(LBL('strategy', v)));
      arr('build').forEach((v) => c.push(LBL('build', v)));
      if (living) arr('must').forEach((v) => c.push(LBL('must', v)));
      take('when', 'when');
      if (A.budget !== 'lender') take('pay', 'pay');
      return c;
    };
    const message = () => {
      const lines = ['SEARCH TO SET UP'];
      if (matchable) lines.push('Areas: ' + (picked.map((sl) => BY[sl].name).join(', ') || 'open'));
      if (A.goal === 'sell') lines.push('SELLER: ' + (A.sell_addr || 'address not given'));
      rows.forEach(([k, v]) => lines.push(k + ': ' + v));
      if ($('input[name=lender]', lead).checked) lines.push('Wants a lender intro: yes');
      return lines.join('\n');
    };
    let html = '';
    if (matchable) {
      html += '<p class="eyebrow">Your search</p><h2 class="h2">Here\'s what I\'ll set up</h2>' +
        '<div class="srch"><div class="crit">' + crit().map((c) => '<span>' + esc(c) + '</span>').join('') + '</div>' +
        '<div class="areas"><b>Areas</b><div class="achips"></div></div>' +
        '<div class="addrow"><span>Add</span><div class="addchips"></div></div></div>';
    } else {
      html += '<p class="eyebrow">Your home</p><h2 class="h2">' + esc(A.sell_addr || 'Your property') + '</h2><p class="lede">I\'ll pull the recent sales around it and send you a real price range.</p>';
    }
    html += '<div class="qsend"><h3>' + (matchable ? 'Get new listings that match' : 'Get your numbers') + '</h3><p>' +
      (matchable ? 'I\'ll save this search on Compass and send you an invite, so new homes come straight to you.' : 'Comps and a price range within a day.') + '</p></div>';
    if (matchable) {
      html += '<h3 class="whyh">Why these areas</h3><div class="matches"></div>';
      const notes = [];
      if (arr('strategy').includes('str')) notes.push('Los Angeles and Santa Monica both restrict stays under 30 days. Furnished rentals of 30+ days avoid those rules.');
      if ((A.goal === 'invest' || A.goal === 'build') && (['35to6', '6p'].includes(A.budget) || arr('build').includes('spec')) && ranked.slice(0, 3).some((x) => x.h.city === 'Los Angeles')) notes.push('City of LA sales over $5.4M pay Measure ULA: 4%, or 5.5% from $10.9M. Santa Monica and Culver City have their own high-end transfer taxes. Beverly Hills, West Hollywood, Malibu and unincorporated areas pay only the county rate.');
      if (arr('strategy').some((v) => ['ltr', 'mf'].includes(v)) || arr('build').includes('apts')) {
        [...new Set(ranked.slice(0, 3).map((x) => x.h.city))].forEach((c) => { const ci = window.CITIES[c]; if (ci) notes.push(ci.rent + '.'); });
      }
      if (notes.length) html += '<div class="qnotes"><b>Good to know</b><ul>' + notes.map((n) => '<li>' + esc(n) + '</li>').join('') + '</ul></div>';
    }
    html += '<details class="qsum"><summary>Your answers</summary><dl>' + rows.map(([k, v]) => '<dt>' + esc(k) + '</dt><dd>' + esc(v) + '</dd>').join('') + '</dl></details><button type="button" class="qagain">Start over</button>';
    res.innerHTML = html;
    res.hidden = false;

    const sync = () => { $('textarea[name=message]', lead).value = message(); if (window.NG && matchable) window.NG.answer('Areas picked', picked.map((sl) => BY[sl].name).join(', ')); };
    const drawAreas = () => {
      if (!matchable) return;
      $('.achips', res).innerHTML = picked.map((sl) => '<button type="button" class="achip on" data-s="' + sl + '">' + esc(BY[sl].name) + ' <i aria-hidden="true">&times;</i></button>').join('') || '<span class="muted">Add at least one</span>';
      const sugg = ranked.filter((x) => !picked.includes(x.h.slug)).slice(0, 6);
      $('.addchips', res).innerHTML = sugg.map((x) => '<button type="button" class="achip" data-s="' + x.h.slug + '">+ ' + esc(x.h.name) + '</button>').join('');
      $$('.achip', res).forEach((b) => b.addEventListener('click', () => {
        const sl = b.dataset.s, i = picked.indexOf(sl);
        if (i >= 0) picked.splice(i, 1); else picked.push(sl);
        drawAreas(); drawTiles(); sync();
      }));
    };
    const drawTiles = () => {
      if (!matchable) return;
      const by = Object.fromEntries(ranked.map((x) => [x.h.slug, x]));
      $('.matches', res).innerHTML = picked.slice(0, 6).map((sl) => {
        const x = by[sl]; const c = $('#pool [data-slug="' + sl + '"]');
        const tile = c ? c.outerHTML.replace('loading="lazy"', 'loading="eager"') : '';
        return '<div class="match">' + tile + (x && x.why.length ? '<ul class="whys">' + x.why.map((w) => '<li>' + esc(w) + '</li>').join('') + '</ul>' : '') + '</div>';
      }).join('');
    };
    drawAreas(); drawTiles();

    lead.hidden = false;
    $('.qsend', res).appendChild(lead);
    lead.dataset.subject = matchable ? 'Search to set up' : 'Home value request';
    lead.dataset.ok = matchable ? 'Got it, {name}. I\'ll set up your search on Compass and send you the invite.' : 'Got it, {name}. Your numbers are on the way within a day.';
    $('input[name=looking]', lead).value = LBL('goal', A.goal) || 'Not specified';
    $('.lenderbox', lead).hidden = !matchable || A.goal === 'rent';
    const cb = $('input[name=lender]', lead); cb.checked = wantsLender;
    cb.onchange = sync; sync();
    $('.qagain', res).addEventListener('click', () => {
      Object.keys(A).forEach((k) => delete A[k]); Object.keys(RAW).forEach((k) => delete RAW[k]);
      AUTO.clear(); CUSTOM.length = 0; PREF.clear();
      res.hidden = true; lead.hidden = true; root.after(lead); cur = 'goal'; render();
      root.scrollIntoView({ behavior: 'smooth' });
    });
    root.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  // ------------------------------------------------------------ start
  const qs = new URLSearchParams(location.search);
  const area = BY[qs.get('area')];
  if (area) { CUSTOM.push({ label: area.name, ll: area.ll }); PREF.add(area.slug); }
  const goal = qs.get('goal');
  if (goal && OPT.goal.some((g) => g[0] === goal)) { A.goal = goal; cur = flow()[1]; }
  render();
  window.__intake = { read, money, whenOf, score, A, flow }; // for testing
})();
