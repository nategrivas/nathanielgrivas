#!/usr/bin/env python3
"""Builds nathanielgrivas.com into ../dist.

Data: src/hoods.py (neighborhoods, city rules), src/lamap.py (vector map), src/posts/*.html (LA Guide).
Each post file starts with a JSON header inside an HTML comment:
<!--{"title":"...","slug":"...","date":"2026-11-25","category":"Living in LA","description":"...","cta":"buy","hoods":["bhpo"]}-->
Run: python3 src/build.py
"""
import json, re, shutil, html, datetime, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from hoods import HOODS, BY_SLUG, CITIES, REGIONS, TAGS, DEALS  # noqa: E402
import lamap  # noqa: E402
import photos  # noqa: E402
from photos import PHOTOS  # noqa: E402
import places  # noqa: E402
import guide_build as G  # noqa: E402
GUIDES = G.load()
import math  # noqa: E402
from urllib.parse import quote_plus  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SITE = "https://www.nathanielgrivas.com"
PHONE = "310-269-5541"
TEL = "+13102695541"
EMAIL = "nate.grivas@compass.com"
FORM_TO = EMAIL
ADDR = "9454 Wilshire Blvd, Ste 100, Beverly Hills, CA 90212"
DRE = "02410660"
CO_DRE = "01991628"
SAME_AS = [
    "https://www.compass.com/agents/nate-grivas/",
    "https://www.linkedin.com/in/nathaniel-grivas-ab15b7234/",
    "https://www.instagram.com/nategrivas/",
    "https://www.zillow.com/profile/nate%20grivas",
    "https://www.realtor.com/realestateagents/6992bfc5702a1b78f9011763",
    "https://www.homes.com/real-estate-agents/nathaniel-grivas/zkpdjdw/",
]

PROPS = {
    "evans": dict(tag="For sale", price="$4.8M", addr="3721 Evans St", area="Los Feliz", spec="8 beds, 10 baths, 4,989 sq ft",
                  img="evans.jpg", url="https://www.compass.com/homedetails/3721-Evans-St-W-Los-Angeles-CA-90027/1K38M8_pid/", site="https://3721evans.com/", page="/homes/3721-evans/"),
    "zelzah": dict(tag="Coming soon", price="$599K", addr="5142 Zelzah Ave #26", area="Encino", spec="2 beds, 3 baths, 1,304 sq ft",
                   img="zelzah.jpg", url="https://www.compass.com/homedetails/5142-Zelzah-Ave-Unit-26-Encino-CA-91316/1I672I_pid/"),
    "edgecliffe": dict(tag="For lease", price="$7,495", per="/mo", addr="1436 Edgecliffe Dr #103", area="Silver Lake", spec="4 beds, 4.5 baths, 2,600 sq ft",
                       img="edgecliffe.jpg", url="https://www.compass.com/homedetails/1436-Edgecliffe-Dr-Unit-103-Los-Angeles-CA-90026/2FWSH6_pid/"),
    "fuller": dict(tag="Sold", price="$3.275M", addr="616 N Fuller Ave", area="Fairfax District", rep="Buyer & seller", sold=True,
                   img="fuller.jpg", url="https://www.compass.com/homedetails/616-N-Fuller-Ave-Los-Angeles-CA-90036/2072900371372293281_lid/", page="/homes/616-fuller/"),
    "lanark": dict(tag="Sold", price="$1.155M", addr="18748 Lanark St", area="Reseda", rep="Seller", sold=True,
                   img="lanark.jpg", url="https://www.compass.com/homedetails/18748-Lanark-St-Los-Angeles-CA-91335/2169982850442083505_lid/"),
    "hartland": dict(tag="Sold", price="$825K", addr="14757 Hartland St", area="Van Nuys", rep="Buyer", sold=True,
                     img="hartland.jpg", url="https://www.compass.com/homedetails/14757-Hartland-St-Van-Nuys-CA-91405/2115491441809620633_lid/"),
    "glenville": dict(tag="Leased", price="$3,400", per="/mo", addr="1127 Glenville Dr #2", area="Pico-Robertson", rep="Tenant & landlord", sold=True,
                      img="glenville.jpg", url="https://www.compass.com/homedetails/1127-Glenville-Dr-Unit-2-Los-Angeles-CA-90035/2190057374525691585_lid/"),
}
BG = "https://orbrodskygroup.com/"
ACTIVE = ["evans", "zelzah", "edgecliffe"]
SOLD = ["fuller", "lanark", "hartland", "glenville"]

CATEGORIES = ["Overrated vs. Underrated", "Eat & Drink", "Living in LA", "Renting in LA", "Courts & Outdoors",
              "Laws & Money", "Build & Develop", "Market Reports"]
CTAS = {
    "buy": ("Thinking about buying here?", "Tell me what you want and your budget. I'll send you what fits, including homes that aren't on the market yet."),
    "sell": ("Curious what your home would sell for?", "I'll pull the real comps for your street and tell you straight, no listing pitch attached."),
    "rent": ("Looking for a place?", "Tell me your budget, area, and move-in date. I'll send you what's worth seeing and what to skip."),
    "build": ("Wondering what your lot can hold?", "Send me the address. I'll check the zoning and tell you what you could build, ADU and lot split included."),
}
TOOLS = [
    ("neighborhood-quiz", "Find your place in LA", "Buy, rent, invest or build. Get matched to the right areas.", "quiz"),
    ("transfer-tax", "Transfer tax & mansion tax calculator", "What a sale costs in transfer taxes in LA, Santa Monica, Culver City, Beverly Hills and more.", "tax"),
    ("mortgage", "What will it cost per month?", "Payment, taxes, insurance and HOA, plus the price your budget really buys.", "home"),
    ("rent-vs-buy", "Rent vs. buy", "Run your real numbers and see the year buying pulls ahead, if it does.", "scale"),
    ("compare", "Compare two neighborhoods", "Side by side: rules, schools, price level and what daily life is like.", "split"),
    ("la-rules", "LA isn't one city", "Transfer taxes, rent control and schools change at every city line. Here's the map.", "map"),
]

ICONS = {
    "build": '<svg viewBox="0 0 24 24"><path d="M4 21V4h11l4 4M4 8h15M12 8v4"/><rect x="10" y="12" width="4" height="3"/><path d="M2 21h9"/></svg>',
    "key": '<svg viewBox="0 0 24 24"><circle cx="8" cy="15" r="4"/><path d="m11 12 9-9M16 7l2 2M14 9l2 2"/></svg>',
    "sign": '<svg viewBox="0 0 24 24"><path d="M5 21V3M5 5h14v8H5M9 9h6"/></svg>',
    "up": '<svg viewBox="0 0 24 24"><path d="m3 17 6-6 4 4 8-8M15 7h6v6"/></svg>',
    "eat": '<svg viewBox="0 0 24 24"><path d="M7 3v8M4 3v5a3 3 0 0 0 6 0V3M7 11v10M17 3c-2 2-3 4.5-3 7.5h3V21"/></svg>',
    "drink": '<svg viewBox="0 0 24 24"><path d="M5 4h14l-7 8zM12 12v8M8 20h8"/></svg>',
    "golf": '<svg viewBox="0 0 24 24"><path d="M9 21V3l8 3.5L9 10"/><path d="M5 21h9"/></svg>',
    "film": '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 5v14M17 5v14M3 9.5h4M3 14.5h4M17 9.5h4M17 14.5h4"/></svg>',
    "show": '<svg viewBox="0 0 24 24"><path d="M4 7a2 2 0 0 0 2-2h12a2 2 0 0 0 2 2v3a2 2 0 0 0 0 4v3a2 2 0 0 0-2 2H6a2 2 0 0 0-2-2v-3a2 2 0 0 0 0-4z"/><path d="M13 7v2M13 11v2M13 15v2"/></svg>',
    "out": '<svg viewBox="0 0 24 24"><path d="m3 18 6-10 4 6 2-3 6 7z"/><path d="M3 21.5c2-1.3 4-1.3 6 0s4 1.3 6 0 4-1.3 6 0"/></svg>',
    "call": '<svg viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
    "text": '<svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "email": '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "in": '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10v7M8 7v.01M12 17v-4a2 2 0 0 1 4 0v4M12 10v7"/></svg>',
    "quiz": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6V14M12 17v.01"/></svg>',
    "tax": '<svg viewBox="0 0 24 24"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 11h2M12 11h2M16 11v.01M8 15h2M12 15h2M16 15v2"/></svg>',
    "home": '<svg viewBox="0 0 24 24"><path d="M3 11 12 4l9 7M5 10v10h14V10M10 20v-6h4v6"/></svg>',
    "scale": '<svg viewBox="0 0 24 24"><path d="M12 4v16M5 20h14M6 8h12M6 8l-3 6a3 3 0 0 0 6 0zM18 8l-3 6a3 3 0 0 0 6 0z"/></svg>',
    "split": '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="8" height="16" rx="2"/><rect x="13" y="4" width="8" height="16" rx="2"/></svg>',
    "map": '<svg viewBox="0 0 24 24"><path d="m3 6 6-2 6 2 6-2v14l-6 2-6-2-6 2zM9 4v14M15 6v14"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "search": '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg>',
    "pin": '<svg viewBox="0 0 24 24"><path d="M12 21s7-6.1 7-11.5A7 7 0 0 0 5 9.5C5 14.9 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    "value": '<svg viewBox="0 0 24 24"><path d="M3 11 12 4l9 7M5 10v10h14V10"/><path d="M12 17v-5M9.5 13.5h4a1.5 1.5 0 0 0 0-3h-3"/></svg>',
    "list": '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="3"/><path d="M7 9h10M7 13h10M7 17h6"/></svg>',
    "team": '<svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 19a6 6 0 0 1 12 0M14 19a4.5 4.5 0 0 1 7 0"/></svg>',
    "guide": '<svg viewBox="0 0 24 24"><path d="M4 5a2 2 0 0 1 2-2h12v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5M8 7h6"/></svg>',
    "tools": '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/></svg>',
}

e = html.escape
TIER = {1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}
TIER_WORD = {1: "Most attainable", 2: "Moderate", 3: "Upper", 4: "Top of market"}
ORDER = sorted(HOODS, key=lambda h: (REGIONS.index(h["region"]), h["name"]))


# ------------------------------------------------------------------ shell
def head(title, desc, path, extra="", og="hero.jpg"):
    canon = SITE + path
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Nathaniel Grivas">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/img/{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#100d0b">
<meta name="ng-to" content="{FORM_TO}">
<link rel="icon" href="{rel(path)}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel(path)}assets/style.css">
{extra}
</head>
<body>
{lamap.base_symbol()}"""


def rel(path):
    return "/"



def nav(path, active, over=False):
    items = [("Homes", "/listings/", "listings"), ("Neighborhoods", "/neighborhoods/", "explore"), ("Sell", "/tools/neighborhood-quiz/?goal=sell", "sell"),
             ("Guide", "/guide/", "guide"), ("About", "/about/", "about")]
    links = "".join(f'<a href="{h}"{" aria-current=page" if k == active else ""}>{n}</a>' for n, h, k in items)
    cls = "top over" if over else "top"
    return f"""<header class="{cls}"><div class="wrap">
<a class="brand" href="/" aria-label="Nathaniel Grivas home"><span class="wm">Nathaniel Grivas</span><span class="bk">Compass</span></a>
<nav class="nav" aria-label="Main">{links}<a class="bg ext" href="{BG}" rel="noopener">Brodsky Group</a></nav>
<button class="searchbtn" type="button" data-cmdk aria-label="Search the site">{ICONS['search']}<span>Search</span><kbd>&#8984;K</kbd></button>
<button class="btn ghost" type="button" data-msg>{ICONS['email']}Message</button>
<a class="btn solid" href="tel:{TEL}">{ICONS['call']}{PHONE}</a>
</div></header>"""


def foot(path, scripts=(), active=""):
    year = datetime.date.today().year
    cols = ""
    for reg in REGIONS:
        items = "".join(f'<li><a href="/neighborhoods/{h["slug"]}/">{e(h["name"])}</a></li>' for h in ORDER if h["region"] == reg)
        cols += f'<div><h4>{e(reg)}</h4><ul>{items}</ul></div>'
    regions = "".join(f'<li><a href="/neighborhoods/#{slug(r_)}">{e(r_)}</a></li>' for r_ in REGIONS)
    tools = "".join(f'<li><a href="/tools/{s_}/">{e(t)}</a></li>' for s_, t, _, _ in TOOLS)
    extra = "".join(f'<script src="/assets/{s_}" defer></script>' for s_ in scripts)
    def cur(k):
        return ' aria-current="page"' if k == active else ""
    strip = "" if (path in ("/", "/listings/") or path.startswith("/homes/") or path == "/tools/neighborhood-quiz/") else featured_strip()
    return f"""{strip}<footer class="foot"><div class="wrap">
<div class="foot-top">
<div class="me"><div class="name">Nathaniel Grivas</div>
<p>REALTOR&reg; with <a href="{BG}" rel="noopener">The Brodsky Group</a> at Compass<br>{ADDR}<br>
<a href="tel:{TEL}">{PHONE}</a> &nbsp; <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p class="soc"><a href="{BG}" rel="noopener">The Brodsky Group</a> <a href="{SAME_AS[0]}">Compass</a> <a href="{SAME_AS[2]}">Instagram</a> <a href="{SAME_AS[1]}">LinkedIn</a> <a href="{SAME_AS[3]}">Zillow</a> <a href="{SAME_AS[4]}">Realtor.com</a></p></div>
<div><h4>Explore</h4><ul><li><a href="/neighborhoods/">The map</a></li>{regions}</ul></div>
<div><h4>Tools</h4><ul>{tools}</ul></div>
<div><h4>More</h4><ul><li><a href="/guide/">LA Guide</a></li><li><a href="/journal/">LA Journal</a></li><li><a href="/listings/">Listings</a></li><li><a href="/about/">About</a></li><li><a href="/#contact" data-msg>Contact</a></li><li><a href="/privacy/">Privacy</a></li><li><a class="ext" href="{BG}" rel="noopener">The Brodsky Group</a></li></ul></div>
</div>
<details><summary>All neighborhoods</summary><div class="foot-hoods">{cols}</div></details>
<div class="legal">Nathaniel Grivas, REALTOR&reg;, DRE #{DRE}. Compass is a licensed real estate broker, DRE #{CO_DRE}. Equal Housing Opportunity.
Neighborhood and rules information is general, simplified and subject to change; confirm details for a specific property with the city, county or a professional. Calculators give estimates, not tax or legal advice. Listing information is shown for marketing purposes and may have changed since posting. Neighborhood photos via <a href="https://unsplash.com/" rel="noopener">Unsplash</a>. &copy; {year} Nathaniel Grivas.</div>
</div></footer>
<nav class="dock" aria-label="Quick">
<a href="/neighborhoods/"{cur("explore")}>{ICONS['pin']}Areas</a>
<a href="/listings/"{cur("listings")}>{ICONS['home']}Homes</a>
<a href="/tools/neighborhood-quiz/"{cur("tools")}>{ICONS['search']}Start</a>
<a href="sms:{TEL}">{ICONS['text']}Text</a>
<a class="call" href="tel:{TEL}">{ICONS['call']}Call</a>
</nav>
<div class="cmdk" id="cmdk" hidden role="dialog" aria-modal="true" aria-label="Search the site">
<div class="cmdk-box"><div class="cmdk-in">{ICONS['search']}<input id="cmdk-q" type="search" placeholder="Neighborhood, ZIP code, tool or topic" autocomplete="off" aria-controls="cmdk-list"><kbd data-close>esc</kbd></div>
<ul class="cmdk-list" id="cmdk-list" role="listbox"></ul>
<div class="cmdk-foot"><span>&uarr;&darr; move</span><span>&crarr; open</span><span>esc close</span></div></div></div>
<dialog class="ngd" id="ngd-reach" aria-labelledby="ngd-reach-t"><div class="ngd-box">
<button class="ngd-x" type="button" data-close aria-label="Close">&times;</button>
<p class="kick">Call Nathaniel</p>
<h2 id="ngd-reach-t"><a class="ngd-num" href="tel:{TEL}">{PHONE}</a></h2>
<p class="ngd-note">Your phone app should open now. Using your phone instead? Dial the number or scan the code with your camera.</p>
<div class="ngd-qr"><img src="/img/qr-call.svg" data-call="/img/qr-call.svg" data-text="/img/qr-text.svg" alt="QR code to call {PHONE}" width="168" height="168"></div>
<div class="ngd-row"><button class="btn" type="button" data-copy="{PHONE}">Copy number</button><a class="btn" data-alt href="sms:{TEL}">Text instead</a><button class="btn" type="button" data-msg>Send a message</button></div>
</div></dialog>
<dialog class="ngd ngd-msg" id="ngd-msg" aria-labelledby="ngd-msg-t"><div class="ngd-box">
<button class="ngd-x" type="button" data-close aria-label="Close">&times;</button>
<p class="kick">Message Nathaniel</p>
<h2 id="ngd-msg-t">What can I help with?</h2>
<p class="ngd-note">This goes straight to my email. You can also call or text <a href="tel:{TEL}">{PHONE}</a>.</p>
{lead_form("/", title="Message from website", need_first=True, btn="Send message")}
</div></dialog>
<script src="/assets/track.js" defer></script><script src="/assets/site.js" defer></script>{extra}
</body></html>"""


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def ld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj)}</script>'


def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


# ------------------------------------------------------------------ components
def prop_card(key, r):
    p = PROPS[key]
    per = f"<small>{p['per']}</small>" if p.get("per") else ""
    sold = p.get("sold")
    live = "" if sold else " live"
    bottom = (f'<div class="meta"><b>{e(p["area"])}</b>Represented {e(p["rep"].lower())}</div>' if sold
              else f'<div class="meta"><b>{e(p["area"])}</b>{e(p["spec"])}</div>')
    card = f"""<a class="card" href="{p.get('page') or p['url']}"{'' if p.get('page') else ' rel="noopener"'}>
<div class="ph"><span class="tag{live}">{e(p['tag'])}</span><img src="{r}img/{p['img']}" alt="{e(p['addr'])}, {e(p['area'])}" loading="lazy" width="960" height="720">
<div class="info"><div class="price">{p['price']}{per}</div><div class="addr">{e(p['addr'])}</div></div></div>
{bottom}</a>"""
    if p.get("site"):
        host = p["site"].split("//")[1].strip("/")
        return f'<div class="cardwrap">{card}<a class="cardsite" href="{p["site"]}" rel="noopener">Property website: {host} &#8599;</a></div>'
    return card


EVANS_PHOTOS = [
    ("p01", "3721 Evans St W from the street"), ("p03", "Great room, kitchen and floating staircase"),
    ("p04", "Chef's kitchen with professional range and pot filler"), ("p05", "Dining area beside the kitchen"),
    ("p08", "Upstairs primary suite with sitting area and walls of glass"), ("p09", "Primary suite opening to a private balcony"),
    ("p13", "Primary bath with freestanding soaking tub"), ("p14", "Primary walk-in closet with custom built-ins"),
    ("p21", "Game room and lounge with wet bar opening to the backyard"), ("p29", "Lower-level lounge opening to the yard"),
    ("p22", "Second primary suite on the lower level"), ("p02", "Main rooftop with covered outdoor kitchen, fire pit and lounge seating"),
    ("p41", "Main rooftop at dusk with the fire pit lit"), ("p32", "ADU kitchen and living room"), ("p40", "ADU private rooftop deck"),
]

FEATURED = {
    "evans": dict(
        title="3721 Evans St W", where="Los Feliz, Los Angeles, CA 90027", status="For sale", price="$4,800,000",
        stats=[("8", "Bedrooms"), ("10", "Bathrooms"), ("4,989", "Sq ft"), ("2", "Primary suites"), ("2", "Rooftop lounges")],
        line="A brand-new modern compound in Los Feliz: a five-bedroom main house and a three-bedroom ADU, each with its own rooftop lounge.",
        body=["Architectural sophistication meets warm, organic design in this brand-new modern compound in the heart of Los Feliz. A five-bedroom main residence pairs with a fully independent three-bedroom ADU, and each home is crowned by its own rooftop lounge with panoramic hillside and mountain views.",
              "The great room opens to a view balcony and a chef's kitchen built around a fluted-wood island with Thermador appliances. Upstairs, the primary suite has its own balcony, a sitting area, a custom walk-in closet and a spa-style bath with a freestanding soaking tub. Downstairs, a game room with a wet bar, a theatre and a second primary suite open to a private, hedge-lined backyard.",
              "The rooftop over the main house has a covered outdoor kitchen, a stone fire pit, built-in lounge seating and room to add a spa. The ADU has its own entrance, full kitchen, two balconies and a rooftop deck, so it works for guests, family, an office or rental income. Minutes from Los Feliz Village, Griffith Park, Sunset Junction and Silver Lake."],
        poster="/img/evans/p01.jpg", loop="/img/evans/loop.mp4", loop_poster="/img/evans/loop.jpg",
        film="https://3721evans.com/media/film.mp4", film_len="1:22",
        site="https://3721evans.com/", compass="https://www.compass.com/homedetails/3721-Evans-St-W-Los-Angeles-CA-90027/1K38M8_pid/",
        credit="Listed by The Brodsky Group at Compass"),
    "fuller": dict(
        title="616 N Fuller Ave", where="Fairfax District, Los Angeles, CA 90036", status="Sold", price="$3,275,000",
        stats=[("7", "Bedrooms"), ("8", "Bathrooms"), ("5,257", "Sq ft"), ("7,334", "Sq ft lot"), ("2016", "Built")],
        line="A three-level modern home with a pool in the Fairfax District. I sold it for $3,275,000, representing both the seller and the buyer.",
        body=["A 2016 modern home on a 7,334 sq ft lot in the Fairfax District: seven bedrooms, eight baths and three levels, with a pool.",
              "I represented both the seller and the buyer and closed it in October 2026 for $3,275,000."],
        poster="/img/fuller.jpg", vimeo="1180538967", film_len="1:00",
        compass="https://www.compass.com/homedetails/616-N-Fuller-Ave-Los-Angeles-CA-90036/2072900371372293281_lid/",
        credit="Sold by Nate Grivas of The Brodsky Group at Compass"),
}


def film_evans(big=False):
    f = FEATURED["evans"]
    return (f'<div class="film film-wide" data-film data-full="{f["film"]}">'
            f'<video data-src="{f["film"]}" poster="{f["loop_poster"]}" muted loop playsinline autoplay preload="none" aria-label="Video tour of 3721 Evans St W"></video>'
            f'<button type="button" class="film-snd" aria-label="Turn sound on" aria-pressed="false"></button></div>')


def film_fuller():
    f = FEATURED["fuller"]
    return (f'<div class="film film-tall" data-vimeo="{f["vimeo"]}">'
            f'<img src="{f["poster"]}" alt="616 N Fuller Ave" loading="lazy"></div>')


def featured_section(heading="Featured homes", kick="Watch the films"):
    e_, f_ = FEATURED["evans"], FEATURED["fuller"]
    def cap(k, f):
        links = f'<a href="{PROPS[k]["page"]}">See the home &rarr;</a>'
        if f.get("site"):
            links += f'<a href="{f["site"]}" rel="noopener">{f["site"].split("//")[1].strip("/")} &#8599;</a>'
        return (f'<div class="fh-cap"><span class="fh-st{" live" if f["status"] != "Sold" else ""}">{e(f["status"])} &middot; {e(f["price"])}</span>'
                f'<h3><a href="{PROPS[k]["page"]}">{e(f["title"])}</a></h3><p>{e(f["where"].split(",")[0])} &middot; {" &middot; ".join(v + " " + l.lower() for v, l in f["stats"][:3])}</p>'
                f'<div class="fh-links">{links}</div></div>')
    return (f'<section class="band lux-band featured" id="featured"><div class="wrap">'
            f'<div class="lux-head"><p class="kick">{e(kick)}</p><h2>{e(heading)}</h2></div>'
            f'<div class="feat-grid"><div class="feat-a">{film_evans()}{cap("evans", e_)}</div>'
            f'<div class="feat-b">{film_fuller()}{cap("fuller", f_)}</div></div></div></section>')


def featured_strip():
    cards = ""
    for k in ("evans", "fuller"):
        f = FEATURED[k]
        cards += (f'<a class="fs-card" href="{PROPS[k]["page"]}"><span class="fs-ph"><img src="{f["poster"]}" alt="" loading="lazy"><span class="fs-play" aria-hidden="true"></span></span>'
                  f'<span class="fs-t"><small>{e(f["status"])} &middot; {e(f["price"])}</small><b>{e(f["title"])}</b><span>{e(f["where"].split(",")[0])} &middot; Watch the film</span></span></a>')
    return f'<section class="fstrip" aria-label="Featured homes"><div class="wrap"><p class="kick">Featured homes</p><div class="fs-row">{cards}</div></div></section>'


def use_base():
    return f'<use href="#la" x="0" y="0" width="{lamap.W:g}" height="{lamap.HH:g}"/>'


def mini_map(h, width=170, aspect=0.56, r=1.0):
    lat, lng = h["ll"]
    x, y, w, hh = lamap.view_around(lat, lng, width=width, aspect=aspect)
    cx, cy = lamap.proj(lat, lng)
    return (f'<svg class="mini" viewBox="{x:.1f} {y:.1f} {w:.1f} {hh:.1f}" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            f'{use_base()}<circle class="halo" cx="{cx}" cy="{cy}" r="{9 * r:g}"/><circle class="pt" cx="{cx}" cy="{cy}" r="{3.6 * r:g}"/></svg>')


def hood_card(h, r, extra_cls=""):
    c = CITIES[h["city"]]
    chips = f'<span>{e(c["short"])}</span><span title="{TIER_WORD[h["tier"]]}">{TIER[h["tier"]]}</span>'
    return f"""<a class="hcard{extra_cls}" href="{r}neighborhoods/{h['slug']}/" data-slug="{h['slug']}" data-region="{slug(h['region'])}" data-tags="{' '.join(h['tags'])}" data-name="{e(h['name'].lower())}" data-zips="{h['zips']}">
{mini_map(h)}
<div class="hc-body"><span class="hc-reg">{e(h['region'])}</span><h3>{e(h['name'])}</h3><p>{e(h['line'])}</p>
<div class="hc-chips">{chips}</div></div></a>"""


def big_map(r, active=None, interactive=True):
    dots = []
    for h in ORDER:
        cx, cy = lamap.proj(*h["ll"])
        on = " on" if active == h["slug"] else ""
        dots.append(f'<a class="dot{on}" href="{r}neighborhoods/{h["slug"]}/" data-slug="{h["slug"]}" data-region="{slug(h["region"])}" data-tags="{" ".join(h["tags"])}" data-zips="{h["zips"]}" data-line="{e(h["line"])}" aria-label="{e(h["name"])}">'
                    f'<g transform="translate({cx} {cy})"><g class="s"><circle class="hit" r="12"/><circle class="ring" r="9"/><circle class="pt" r="4.6"/><text x="9" y="4">{e(h["name"])}</text></g></g></a>')
    return (f'<svg class="lamap{" live" if interactive else ""}" viewBox="0 0 {lamap.W:g} {lamap.HH:g}" role="img" aria-label="Map of Los Angeles neighborhoods">'
            f'{use_base()}<g class="places">{lamap.labels()}</g><g class="dots">{"".join(dots)}</g></svg>')


def hero_map(h):
    lat, lng = h["ll"]
    x, y, w, hh = lamap.view_around(lat, lng, width=330, aspect=0.5, fx=0.62)
    k = w / 1000
    dots = []
    for o in HOODS:
        cx, cy = lamap.proj(*o["ll"])
        if not (x - 30 < cx < x + w + 30 and y - 30 < cy < y + hh + 30):
            continue
        me = o["slug"] == h["slug"]
        if not me and cx < x + 0.5 * w:
            dots.append(f'<a class="dot" href="/neighborhoods/{o["slug"]}/" aria-label="{e(o["name"])}"><circle class="pt" cx="{cx}" cy="{cy}" r="1.5"/></a>')
            continue
        cls = "dot on" if me else "dot"
        fs = 7.4 if me else 3.9
        dots.append(f'<a class="{cls}" href="/neighborhoods/{o["slug"]}/"><circle class="ring" cx="{cx}" cy="{cy}" r="{6.5 if me else 3}"/><circle class="pt" cx="{cx}" cy="{cy}" r="{2.6 if me else 1.5}"/>'
                    f'<text x="{cx + (5 if me else 3):.1f}" y="{cy + (2.6 if me else 1.4):.1f}" font-size="{fs}">{e(o["name"])}</text></a>')
    hx, hy = lamap.proj(lat, lng)
    return (f'<svg class="heromap" viewBox="{x:.1f} {y:.1f} {w:.1f} {hh:.1f}" data-cx="{hx}" data-cy="{hy}" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            f'{use_base()}<g class="places">{lamap.labels(scale=k * 1.6)}</g><g class="dots">{"".join(dots)}</g></svg>')


def lead_form(r, preset="", msg="", title="", need_first=False, btn="Send to Nathaniel"):
    opts = ["Buy", "Sell", "Rent", "Invest", "Build"]
    pills = "".join(
        f'<label><input type="checkbox" name="looking" value="{o}"{" checked" if o.lower() == preset else ""}> {o}</label>'
        for o in opts)
    who = """<div class="f"><label>Name<input name="name" autocomplete="name" required></label></div>
<div class="f"><label>Phone<input name="phone" type="tel" autocomplete="tel"></label></div>
<div class="f full"><label>Email<input name="email" type="email" autocomplete="email" required></label></div>"""
    need = f"""<div class="f full"><span class="lbl">I'm looking to</span><div class="pills">{pills}</div></div>
<div class="f full"><label>{"Your message" if need_first else "Anything I should know?"}<textarea name="message" placeholder="{"What you're looking to buy, sell or rent, the area, timing, an address" if need_first else "Area, budget, timing, an address you're curious about"}">{e(msg)}</textarea></label></div>"""
    body = need + "\n" + who if need_first else who + "\n" + need
    return f"""<form class="lead" data-to="{FORM_TO}" data-subject="{e(title or 'New website lead')}" novalidate>
{body}
<div class="f full"><button class="btn solid" type="submit">{e(btn)}</button></div>
<p class="formmsg" role="status" aria-live="polite"></p>
<p class="formnote">Goes straight to me. I reply within a day, usually sooner. By sending, you agree I can contact you by call, text or email about real estate. Reply STOP to opt out of texts. <a href="/privacy/">Privacy</a></p>
</form>"""


INTAKE = "/tools/neighborhood-quiz/"


def intake_url(goal="", area=""):
    q = []
    if goal:
        q.append(f"goal={goal}")
    if area:
        q.append(f"area={area}")
    return INTAKE + ("?" + "&amp;".join(q) if q else "")


def contact_band(r, heading="Tell me what you're after", sub="Buying, selling, renting, investing or building. Start here.", preset="", msg="", title="", form=False, area=""):
    if not form:
        btn = {"sell": "Get my home's value", "rent": "Start my rental search", "build": "Tell me about the project", "invest": "Start my search"}.get(preset, "Start my search")
        return f"""<section class="band" id="contact"><div class="wrap"><div class="ctaband glass">
<img src="/img/nate-sm.jpg" alt="Nathaniel Grivas" width="88" height="110" loading="lazy">
<div class="cb-t"><h2>{e(heading)}</h2><p>{e(sub)}</p></div>
<div class="cb-b"><a class="btn solid big" href="{intake_url(preset, area)}">{btn}</a><a class="btn big" href="sms:{TEL}">{ICONS['text']}Text</a><a class="btn big" href="tel:{TEL}">{ICONS['call']}Call</a></div>
</div></div></section>"""
    q = ICONS
    return f"""<section class="band" id="contact"><div class="wrap contact">
<div><p class="eyebrow">Contact</p><h2>{e(heading)}</h2>
<p class="lede" style="margin-top:8px;font-size:15.5px">{e(sub)}</p>
<div class="quickc">
<a href="tel:{TEL}">{q['call']}<div><b>Call {PHONE}</b><span>Talk it through</span></div></a>
<a href="sms:{TEL}">{q['text']}<div><b>Text</b><span>{PHONE}</span></div></a>
<a href="mailto:{EMAIL}">{q['email']}<div><b>Email</b><span>{EMAIL}</span></div></a>
<a href="{BG}" rel="noopener">{q['team']}<div><b class="ext">The Brodsky Group</b><span>My team at Compass Beverly Hills</span></div></a>
</div></div>
{lead_form(r, preset, msg, title)}
</div></section>"""


def team_band(img, title, line):
    return team_section(img)


def team_section(img="team.jpg", bio=None):
    bio = bio or ("I represent buyers, sellers, landlords and developers with The Brodsky Group at Compass Beverly Hills. "
                  "Pricing, competitive offers, leasing, new construction, teardown and lot analysis, ADU feasibility and off-market sourcing.")
    return f"""<section class="band"><div class="wrap teamwrap">
<figure class="teamband"><img src="/img/{img}" alt="The Brodsky Group team at Compass" width="2000" height="1333" loading="lazy">
<figcaption>The Brodsky Group &middot; Compass Beverly Hills</figcaption></figure>
<div class="mecard glass">
<div class="who"><img src="/img/nate.jpg" alt="Nathaniel Grivas" width="84" height="84" loading="lazy"><div><h2>Nathaniel Grivas</h2><span>REALTOR&reg; &middot; DRE #{DRE}</span></div></div>
<p>{e(bio)}</p>
<div class="cta-row" style="margin-top:0"><a class="btn solid" href="/#contact">Work with me</a><a class="btn ext" href="{BG}" rel="noopener">The Brodsky Group</a><a class="btn" href="/about/">About me</a></div>
</div></div></section>"""


def ph_img(pid, alt, w=800, ratio=None, sizes="(max-width:700px) 92vw, 33vw", eager=False, cls=""):
    h = int(w * ratio) if ratio else None
    ld_ = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    ss = photos.srcset(pid, ratio)
    ss = f' srcset="{ss}" sizes="{sizes}"' if ss else ""
    return f'<img{c} src="{photos.url(pid, w, h)}"{ss} alt="{e(alt)}" {ld_} decoding="async">'



def photo_tile(h, cls="", sizes="(max-width:700px) 92vw, 30vw"):
    p = PHOTOS.get(h["slug"])
    if p:
        media = ph_img(p[0][0], p[0][1], 900, None, sizes)
    else:
        media = mini_map(h, 320, 1.2, 1.4)
    tier = TIER[h["tier"]]
    return (f'<a class="tile{" maptile" if not p else ""}{" " + cls if cls else ""}" href="/neighborhoods/{h["slug"]}/" data-tags="{" ".join(h["tags"])}">'
            f'{media}<div class="tile-txt"><span class="tile-k">{e(h["region"])} &middot; {tier}</span><h3>{e(h["name"])}</h3><p>{e(h["line"])}</p></div></a>')


def worth_form():
    return f"""<form class="lead worth" data-to="{FORM_TO}" data-subject="Home value request" novalidate>
<input type="hidden" name="looking" value="Sell">
<div class="f full"><label>Property address<input name="message" autocomplete="street-address" placeholder="1234 Ocean Ave, Santa Monica" required></label></div>
<div class="f"><label>Name<input name="name" autocomplete="name" required></label></div>
<div class="f"><label>Phone<input name="phone" type="tel" autocomplete="tel"></label></div>
<div class="f full"><label>Email<input name="email" type="email" autocomplete="email" required></label></div>
<div class="f full"><button class="btn solid big" type="submit">Get my home value</button></div>
<p class="formmsg" role="status" aria-live="polite"></p>
</form>"""


def nate_card(heading, sub):
    return f"""<div class="natecard glass"><img src="/img/nate-sm.jpg" alt="Nathaniel Grivas" width="72" height="90" loading="lazy">
<div><b>{e(heading)}</b><span>{sub}</span>
<div class="cta-row"><a class="btn solid small" href="tel:{TEL}">{ICONS['call']}Call</a><a class="btn small" href="sms:{TEL}">{ICONS['text']}Text</a></div></div></div>"""


def miles(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(d))


def nearby_places(h, cat, n=6):
    rows = []
    for c, name, area, lat, lng, line in places.P:
        if c != cat:
            continue
        d = miles(h["ll"], (lat, lng))
        home = area.lower() == h["name"].lower()
        rows.append((0 if home else 1, d, name, area, line))
    rad = places.RADIUS[cat]
    pick = sorted([r for r in rows if r[0] == 0 or r[1] <= rad], key=lambda r: (r[0], r[1]))[:n]
    if len(pick) < 2:
        pick = sorted([r for r in rows if r[1] <= rad * 2.5], key=lambda r: r[1])[:3]
    return pick


def dist_label(home, d, area):
    if home == 0:
        return f"In {area}"
    if d < 1:
        return f"{area} &middot; under 1 mi"
    return f"{area} &middot; {round(d * 2) / 2:g} mi"


def local_guide(h):
    tabs, panels, first = "", "", True
    for cat, label in places.CATS:
        rows = nearby_places(h, cat)
        if not rows:
            continue
        cards = "".join(
            f'<a class="place" href="https://www.google.com/maps/search/?api=1&amp;query={quote_plus(name + " " + area + " CA")}" rel="noopener">'
            f'<span class="pl-ic">{ICONS[cat]}</span><span class="pl-b"><b>{e(name)}</b><small>{dist_label(home, d, e(area))}</small><span>{e(line)}</span></span></a>'
            for home, d, name, area, line in rows)
        tabs += f'<button type="button" role="tab" data-tab="pl-{cat}" aria-selected="{"true" if first else "false"}">{ICONS[cat]}{e(label)}</button>'
        panels += f'<div class="placegrid" role="tabpanel" data-panel="pl-{cat}"{"" if first else " hidden"}>{cards}</div>'
        first = False
    if not tabs:
        return ""
    return f"""<section class="band" id="around"><div class="wrap" data-tabs>
<div class="head"><h2 class="h2">Around {e(h['name'])}</h2>{(f'<a href="/guide/{h["slug"]}/">The full {e(h["name"])} guide: {len(GUIDES[h["slug"]]["places"])} places &rarr;</a>') if h["slug"] in GUIDES else ''}</div>
<div class="tabbar pltabs" role="tablist">{tabs}</div>{panels}
</div></section>"""


def hood_flags(h):
    golf = any(c == "golf" and "Private" not in line and miles(h["ll"], (la, lo)) <= 3.5 for c, _, _, la, lo, line in places.P)
    trails = any(c == "out" and miles(h["ll"], (la, lo)) <= 2.5 for c, _, _, la, lo, _ in places.P)
    return golf, trails


def tool_card(s, r):
    slug_, t, d, ic = next(x for x in TOOLS if x[0] == s)
    return f'<a class="tool" href="/tools/{slug_}/"><span class="ic">{ICONS[ic]}</span><span><h3>{e(t)}</h3><p>{e(d)}</p></span><span class="go">{ICONS["arrow"]}</span></a>'


def load_posts():
    posts = []
    for f in sorted((ROOT / "src" / "posts").glob("*.html")):
        raw = f.read_text()
        m = re.match(r"\s*<!--(\{.*?\})-->\s*(.*)", raw, re.S)
        meta = json.loads(m.group(1))
        meta["body"] = m.group(2)
        if meta.get("draft"):
            continue
        posts.append(meta)
    posts.sort(key=lambda p: (p["date"], p.get("order", 0)), reverse=True)
    return posts


def fmt_date(d):
    return datetime.date.fromisoformat(d).strftime("%B %-d, %Y")


def post_card(p, r):
    return f"""<a class="post" href="{r}guide/{p['slug']}/" data-cat="{slug(p['category'])}">
<span class="cat">{e(p['category'])}</span><h3>{e(p['title'])}</h3><p>{e(p['description'])}</p>
<span class="when">{fmt_date(p['date'])}</span></a>"""


# ------------------------------------------------------------------ pages
def person_ld():
    return {
        "@context": "https://schema.org", "@type": "RealEstateAgent", "name": "Nathaniel Grivas",
        "jobTitle": "REALTOR", "description": "West Los Angeles REALTOR with The Brodsky Group at Compass Beverly Hills. " + AREAS_LINE,
        "url": SITE + "/", "image": SITE + "/img/nate-hero.jpg", "telephone": "+1-310-269-5541", "email": EMAIL,
        "address": {"@type": "PostalAddress", "streetAddress": "9454 Wilshire Blvd, Ste 100",
                    "addressLocality": "Beverly Hills", "addressRegion": "CA", "postalCode": "90212", "addressCountry": "US"},
        "areaServed": [h["name"] for h in ORDER],
        "parentOrganization": {"@type": "RealEstateAgent", "name": "Compass", "url": "https://www.compass.com/"},
        "memberOf": {"@type": "Organization", "name": "The Brodsky Group at Compass", "url": BG,
                     "description": "Compass Beverly Hills team with over $100M in annual sales"},
        "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": t, "description": d}} for _, t, d in HELP],
        "knowsAbout": ["Luxury residential real estate", "Development and teardown analysis", "ADU feasibility",
                       "Off-market sourcing", "Leasing", "Measure ULA", "Los Angeles neighborhoods"],
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "Loyola Marymount University"},
        "identifier": {"@type": "PropertyValue", "name": "California DRE license", "value": DRE},
        "sameAs": SAME_AS,
    }


SHELVES = [
    ("On the coast", "Sand within reach", lambda h: "beach" in h["tags"]),
    ("Walk to dinner", "Leave the car parked", lambda h: "walkable" in h["tags"] and "beach" not in h["tags"]),
    ("Hills and views", "Up above the grid", lambda h: "views" in h["tags"]),
    ("Residential streets", "Yards, parks and quiet blocks", lambda h: "family" in h["tags"] and "yard" in h["tags"]),
    ("More for the money", "Where your budget stretches", lambda h: "value" in h["tags"]),
]


HOME_HOODS = ["venice", "santa-monica", "beverly-hills", "malibu", "los-feliz", "hollywood-hills",
              "silver-lake", "marina-del-rey", "pacific-palisades", "westwood", "echo-park", "fairfax"]



HELP = [
    ("buy", "Buy a home", "New listings that fit, sent as soon as they hit the market."),
    ("sell", "Sell my home", "Pricing, prep and a plan for your sale."),
    ("rent", "Rent a home", "Leases across the Westside and the Valley."),
    ("invest", "Invest", "Income property, value-add and off-market deals."),
    ("build", "Build", "Lots, teardowns and ADU feasibility."),
]

AREAS_LINE = "From Westchester to Malibu, Hollywood to Silver Lake, and across the San Fernando Valley."


def listings_ld():
    items = []
    for i, k in enumerate(ACTIVE + SOLD):
        p_ = PROPS[k]
        items.append({"@type": "ListItem", "position": i + 1, "item": {
            "@type": "Residence", "name": f"{p_['addr']}, {p_['area']}", "url": p_.get("site") or p_["url"],
            "description": (f"{p_['tag']}, {p_['price']}{p_.get('per', '')}. Represented {p_['rep'].lower()}." if p_.get("sold")
                            else f"{p_['tag']}, {p_['price']}{p_.get('per', '')}. {p_['spec']}.")}})
    return {"@context": "https://schema.org", "@type": "ItemList", "name": "Listings by Nathaniel Grivas", "itemListElement": items}


def page_home(posts):
    path = "/"
    r = "/"
    tiles = "".join(photo_tile(BY_SLUG[s_], "big" if i == 0 else "") for i, s_ in enumerate(HOME_HOODS))
    tiles += (f'<a class="tile maptile allmap" href="/neighborhoods/"><svg viewBox="0 0 {lamap.W:g} {lamap.HH:g}" preserveAspectRatio="xMidYMid slice" aria-hidden="true">{use_base()}</svg>'
              f'<div class="tile-txt"><span class="tile-k">The map</span><h3>Every neighborhood</h3></div></a>')
    helps = "".join(f'<a href="{intake_url(g)}"><b>{e(t)}</b><span>{e(d)}</span><i aria-hidden="true">&rarr;</i></a>' for g, t, d in HELP)
    body = f"""{nav(path, "home")}
<main>
<section class="face-hero" aria-label="Nathaniel Grivas, West Los Angeles REALTOR">
<figure class="fh-me"><img src="/img/nate-hero.jpg" alt="Nathaniel Grivas, REALTOR&reg; at Compass Beverly Hills" width="1200" height="1500" fetchpriority="high"></figure>
<div class="fh-copy">
<p class="kick">The Brodsky Group at Compass Beverly Hills</p>
<h1><span class="lh-name">Nathaniel Grivas</span><span class="lh-sub">West Los Angeles REALTOR&reg;</span></h1>
<p class="fh-lede">I help people buy, sell, rent, invest and build across West LA, Beverly Hills and the Valley.</p>
<div class="lh-cta"><a class="btn lux solid" href="#help">Work with me</a><a class="btn lux" href="#homes">View listings</a></div>
<figure class="fh-team"><img src="/img/team.jpg" alt="The Brodsky Group team at Compass Beverly Hills" width="2000" height="1333" fetchpriority="high">
<figcaption><span><b>The Brodsky Group</b> &middot; $100M+ in annual team sales</span><a href="{BG}" rel="noopener">Meet the team &#8599;</a></figcaption></figure>
</div>
</section>

{featured_section()}

<section class="help" id="help"><div class="wrap">
<div class="lux-head"><p class="kick">Work with me</p><h2>How can I help?</h2></div>
<div class="help-row">{helps}</div>
</div></section>

<section class="band lux-band" id="homes"><div class="wrap" data-tabs>
<div class="lux-head"><p class="kick">Featured</p><h2>Listings</h2>
<div class="tabbar" role="tablist"><button type="button" role="tab" data-tab="act" aria-selected="true">Available</button><button type="button" role="tab" data-tab="sold" aria-selected="false">Sold</button></div></div>
<div class="grid homes" role="tabpanel" data-panel="act">{"".join(prop_card(k, r) for k in ACTIVE)}</div>
<div class="grid homes" role="tabpanel" data-panel="sold" hidden>{"".join(prop_card(k, r) for k in SOLD)}</div>
<p class="lux-more"><a href="/listings/">All listings &rarr;</a></p>
</div></section>

<section class="meet" id="about"><div class="wrap meet-grid">
<figure class="meet-ph"><img src="/img/nate-about.jpg" alt="Nathaniel Grivas" width="900" height="990" loading="lazy"></figure>
<div class="meet-copy">
<p class="kick">About</p>
<h2>Nathaniel Grivas</h2>
<p class="meet-id">REALTOR&reg; &middot; DRE #{DRE} &middot; The Brodsky Group at Compass</p>
<p>Raised between New York and Seattle, I studied Marketing and Business Law at Loyola Marymount University and now represent buyers, sellers, landlords and developers with The Brodsky Group at Compass Beverly Hills.</p>
<p>{AREAS_LINE} My work runs from pricing and listing prep to competitive offers, leasing, new construction, teardown and lot analysis, ADU feasibility and off-market deals.</p>
<div class="lh-cta"><a class="btn lux solid" href="/about/">More about me</a><a class="btn lux" href="sms:{TEL}">Text {PHONE}</a></div>
</div></div></section>

<section class="band lux-band" id="areas"><div class="wrap">
<div class="lux-head"><p class="kick">Across Los Angeles</p><h2>Neighborhoods</h2><a href="/neighborhoods/">Open the map &rarr;</a></div>
<div class="bento">{tiles}</div>
</div></section>

<section class="band lux-band"><div class="wrap">
<div class="lux-head"><p class="kick">Insights</p><h2>The LA Guide</h2><a href="/guide/">All posts &rarr;</a></div>
<div class="posts">{"".join(post_card(p, r) for p in posts[:3])}</div>
</div></section>

{contact_band(r, "Let's talk", "Tell me what you're looking for. I'll set up your search and send new listings that match as they hit the market.", form=True)}
</main>
{foot(path, [])}"""
    desc = ("Nathaniel Grivas, West Los Angeles REALTOR® with The Brodsky Group at Compass Beverly Hills. Buy, sell, rent, invest or build across West LA, "
            "Beverly Hills and the Valley.")
    extra = ld(person_ld()) + ld(listings_ld()) + '\n<link rel="alternate" type="text/markdown" href="/index.md" title="Text version of this page">'
    return head("Nathaniel Grivas | West Los Angeles REALTOR® | The Brodsky Group at Compass", desc, path, extra, og="nate-hero.jpg") + body


def page_explore():
    path = "/neighborhoods/"
    r = "/"
    regs = "".join(f'<button type="button" data-region="{slug(x)}" aria-pressed="false">{e(x)}</button>' for x in REGIONS)
    tags = "".join(f'<button type="button" data-tag="{k}" aria-pressed="false">{e(v)}</button>' for k, v in TAGS.items())
    cards = "".join(hood_card(h, r) for h in ORDER)
    body = f"""{nav(path, "explore")}
<main class="wrap xp">
<div class="xp-map">
<div class="maphead"><span class="live">Explore LA</span><span>Drag &middot; pinch &middot; double-click to zoom</span></div>
<div class="mapwrap explore-map">{big_map(r)}<div class="tip" hidden></div>
<div class="zoom"><button type="button" data-z="in" aria-label="Zoom in">+</button><button type="button" data-z="out" aria-label="Zoom out">&minus;</button><button type="button" data-z="reset" aria-label="Reset map">&#8634;</button></div></div>
<div class="agentbar"><img src="/img/nate.jpg" alt="" width="42" height="42"><div><b>Not sure where to start?</b><span>Take the <a href="/tools/neighborhood-quiz/">6-question quiz</a> or ask me directly.</span></div>
<a class="btn small" href="sms:{TEL}">Text</a><a class="btn solid small" href="tel:{TEL}">Call</a></div>
</div>
<div class="xp-side">
<p class="eyebrow">Explore LA</p>
<h1>Explore LA</h1>
<label class="search">{ICONS['search']}<input id="q" type="search" placeholder="Search a neighborhood or ZIP" autocomplete="off"></label>
<div class="chiprow" id="regions" role="group" aria-label="Region"><button type="button" data-region="" aria-pressed="true">All</button>{regs}</div>
<div class="chiprow" id="tags" role="group" aria-label="What you want">{tags}</div>
<p class="count" id="count" aria-live="polite"></p>
<div class="hgrid" id="hgrid">{cards}</div>
<p class="empty" id="empty" hidden>No neighborhood matches all of those. Remove a filter or two.</p>
</div>
</main>
<section class="band" style="padding-top:10px"><div class="wrap"><div class="tools">{tool_card("neighborhood-quiz", r)}{tool_card("compare", r)}{tool_card("la-rules", r)}</div></div></section>
{contact_band(r, "Not sure where to start?", "Answer a few questions and I'll set up a search for the areas that fit.", "buy")}
{foot(path, ["map.js"], "explore")}"""
    desc = "Interactive map and guides to 40 Los Angeles neighborhoods, from Santa Monica and Venice to Beverly Hills, Los Feliz and the Valley. By Nathaniel Grivas, REALTOR®."
    ld_ = crumbs_ld([("Home", "/"), ("Explore LA", path)])
    return head("Explore 40 Los Angeles Neighborhoods | Interactive Map | Nathaniel Grivas", desc, path, ld(ld_)) + body


def rules_box(h, r):
    c = CITIES[h["city"]]
    ula_yes = h["city"] == "Los Angeles"
    return f"""<aside class="rules glass" id="rules"><p class="eyebrow">The rules here</p>
<dl>
<dt>Jurisdiction</dt><dd>{e(c['label'])}</dd>
<dt>Transfer tax</dt><dd>{e(c['transfer'])}</dd>
<dt>Measure ULA</dt><dd><span class="pill {'yes' if ula_yes else 'no'}">{'Applies' if ula_yes else 'No'}</span> {e(c['ula'])}</dd>
<dt>Rent control</dt><dd>{e(c['rent'])}</dd>
<dt>Public schools</dt><dd>{e(c['schools'])}</dd>
</dl>
<div class="cta-row" style="margin-top:14px"><a class="btn small" href="/tools/transfer-tax/?city={slug(h['city'])}">Run the transfer tax</a><a class="btn small" href="/tools/la-rules/">Compare cities</a></div>
<p class="fine">Rules have exemptions. Confirm for a specific address.</p></aside>"""



def page_hood(h, posts):
    path = f"/neighborhoods/{h['slug']}/"
    r = "/"
    c = CITIES[h["city"]]
    i = ORDER.index(h)
    prev_, next_ = ORDER[i - 1], ORDER[(i + 1) % len(ORDER)]
    ph = PHOTOS.get(h["slug"], [])
    spots = "".join(f'<li><span class="n">{k + 1}</span><b>{e(t)}</b><span>{e(d)}</span></li>' for k, (t, d) in enumerate(h["know"]))
    near = "".join(photo_tile(BY_SLUG[n]) for n in h["near"])
    deals = DEALS.get(h["slug"], [])
    deals_html = ""
    if deals:
        deals_html = f"""<section class="band" id="deals"><div class="wrap">
<div class="head"><h2 class="h2">My deals in {e(h['name'])}</h2><a href="/listings/">All listings &rarr;</a></div>
<div class="grid homes">{"".join(prop_card(k, r) for k in deals)}</div></div></section>"""
    rel_posts = [p for p in posts if h["slug"] in p.get("hoods", []) or (h["city"] == "Los Angeles" and "city-of-la" in p.get("hoods", []))]
    posts_html = ""
    if rel_posts:
        posts_html = f"""<div class="head" style="margin-top:26px"><h3>Read before you buy here</h3></div><div class="posts">{"".join(post_card(p, r) for p in rel_posts[:3])}</div>"""
    chips = "".join(f'<a href="/neighborhoods/#{t}">{e(TAGS[t])}</a>' for t in h["tags"])
    if ph:
        hero_media = ph_img(ph[0][0], ph[0][1], 1800, None, "100vw", eager=True, cls="hz-bg")
        credit = '' if ph[0][0].startswith("/") else '<a class="credit" href="https://unsplash.com/" rel="noopener">Photo: Unsplash</a>'
    else:
        hero_media = hero_map(h)
        credit = ""
    gal = ""
    if len(ph) > 1:
        items = ph[1:6]
        extra = len(ph) - 1 - len(items)
        figs = ""
        for k, (pid, alt) in enumerate(items):
            more = f'<span class="gend">+{extra} more</span>' if (extra > 0 and k == len(items) - 1) else ""
            figs += (f'<button type="button" class="g{" g0" if k == 0 else ""}" data-full="{photos.url(pid, 2000)}" data-alt="{e(alt)}" aria-label="View photo: {e(alt)}">'
                     f'{ph_img(pid, alt, 900 if k == 0 else 600, 0.75 if k else 0.8, "(max-width:700px) 80vw, 33vw")}{more}</button>')
        all_ = "".join(f'<i data-full="{photos.url(pid, 2000)}" data-alt="{e(alt)}"></i>' for pid, alt in ph)
        gal = f'<section class="band gband"><div class="wrap"><div class="gallery n{len(items)}" data-gallery>{figs}<div hidden class="gall">{all_}</div></div></div></section>'
    lat, lng = h["ll"]
    gmaps = f"https://www.google.com/maps/search/?api=1&query={h['name'].replace(' ', '+').replace('&', 'and')}+Los+Angeles+CA"
    place = {"@context": "https://schema.org", "@type": "Place", "name": f"{h['name']}, Los Angeles",
             "description": h["intro"], "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng},
             "containedInPlace": {"@type": "City", "name": c["label"].replace("City of ", "").replace("Unincorporated ", "")}}
    if ph:
        place["image"] = [photos.url(pid, 1600) for pid, _ in ph[:3]]
    crumbs = crumbs_ld([("Home", "/"), ("Neighborhoods", "/neighborhoods/"), (h["name"], path)])
    body = f"""{nav(path, "explore")}
<main class="hood">
<section class="hz{" nomedia" if not ph else ""}">{hero_media}
<div class="wrap hz-in">
<div class="crumbs"><a href="/neighborhoods/">Neighborhoods</a> / <a href="/neighborhoods/#{slug(h['region'])}">{e(h['region'])}</a></div>
<h1>{e(h['name'])}</h1>
<p class="hz-line">{e(h['line'])}</p>
<div class="hz-chips"><span title="{TIER_WORD[h['tier']]}">{TIER[h['tier']]} &middot; {TIER_WORD[h['tier']]}</span><span>{e(c['short'])}</span><span>ZIP {e(h['zips'])}</span></div>
<div class="cta-row"><a class="btn solid big" href="{intake_url('buy', h['slug'])}">Get {e(h['name'])} listings</a><a class="btn big" href="sms:{TEL}">{ICONS['text']}Text Nathaniel</a></div>
</div>{credit}</section>
{gal}
<section class="band"><div class="wrap feel">
<div class="feel-l">
<h2 class="h2">What it's like</h2>
<p class="big">{e(h['feel'])}</p>
<div class="taglinks">{chips}</div>
<h3 class="spots-h">Spots to know</h3>
<ol class="spots">{spots}</ol>
</div>
<aside class="feel-r">
<a class="mapcard glass" href="{gmaps}" rel="noopener">{mini_map(h, 260, 0.62, 1.3)}<span>{ICONS['pin']}Open in Google Maps</span></a>
{nate_card(f"Thinking about {h['name']}?", f"I'll send you what's for sale, and what's coming. <a href='{BG}' rel='noopener'>The Brodsky Group</a> at Compass.")}
</aside>
</div></section>
{local_guide(h)}
{deals_html}
<section class="band" id="nearby"><div class="wrap">
<div class="head"><h2 class="h2">Next door</h2><a href="/neighborhoods/">All neighborhoods &rarr;</a></div>
<div class="tilerow">{near}</div>
</div></section>
<section class="band"><div class="wrap">
<details class="guide-more glass"><summary><span><b>The full {e(h['name'])} guide</b><small>History, housing, who it fits, taxes and rules</small></span><span class="chev">+</span></summary>
<div class="gm-body">
<div class="gm-text">
<p>{e(h['intro'])}</p>
<h3>The housing</h3><p>{e(h['housing'])}</p>
<div class="fitgrid"><div class="fit yes"><b>Good fit if</b><p>{e(h['fit'])}</p></div><div class="fit no"><b>Think twice if</b><p>{e(h['skip'])}</p></div></div>
</div>
{rules_box(h, r)}
</div>
{posts_html}
<div class="toolchips"><span>Run the numbers</span><a href="/tools/mortgage/">{ICONS['home']}Mortgage</a><a href="/tools/rent-vs-buy/">{ICONS['scale']}Rent vs buy</a><a href="/tools/transfer-tax/?city={slug(h['city'])}">{ICONS['tax']}Transfer tax</a><a href="/tools/compare/?a={h['slug']}&amp;b={h['near'][0]}">{ICONS['split']}Compare</a></div>
</details>
<nav class="pager" aria-label="More neighborhoods"><a class="glass" href="/neighborhoods/{prev_['slug']}/"><span>Previous</span>{e(prev_['name'])}</a><a class="glass" href="/neighborhoods/"><span>All</span>Map</a><a class="glass" href="/neighborhoods/{next_['slug']}/"><span>Next</span>{e(next_['name'])}</a></nav>
</div></section>
{contact_band(r, f"Looking in {h['name']}?", f"Tell me what you want. I'll set up your search and send new {h['name']} listings as they hit.", "buy", area=h['slug'])}
<div class="lightbox" hidden role="dialog" aria-modal="true" aria-label="Photo viewer"><button type="button" class="lb-x" aria-label="Close">&times;</button><button type="button" class="lb-p" aria-label="Previous photo">&lsaquo;</button><img alt=""><button type="button" class="lb-n" aria-label="Next photo">&rsaquo;</button><p class="lb-c"></p></div>
</main>
{foot(path, (), "explore")}"""
    title = f"Living in {h['name']}, Los Angeles: Photos & Neighborhood Guide | Nathaniel Grivas"
    desc = f"{h['line']} {h['intro']}"[:300]
    og = "hero.jpg"
    return head(title, desc, path, ld(place) + ld(crumbs), og=og) + body


def page_tools():
    path = "/tools/"
    r = rel(path)
    body = f"""{nav(path, "tools")}
<main>
<section class="band tight"><div class="wrap">
<p class="eyebrow">Free tools</p><h1 class="h1">Do the math before you call anyone</h1>
<p class="lede" style="margin-top:14px">Calculators and guides built around how LA actually works: city-by-city transfer taxes, Measure ULA, rent control lines and real monthly costs.</p>
</div></section>
<section class="band" style="padding-top:0"><div class="wrap"><div class="tools">{"".join(tool_card(s, r) for s, *_ in TOOLS)}</div></div></section>
{contact_band(r)}
</main>
{foot(path)}"""
    desc = "Free Los Angeles real estate tools: neighborhood quiz, transfer tax and Measure ULA calculator, mortgage, rent vs buy, and city rules."
    return head("Free LA Real Estate Tools | Nathaniel Grivas", desc, path) + body


def tool_shell(slug_, title, desc, inner, scripts=("tools.js",), preset="", msg="", lean=False):
    path = f"/tools/{slug_}/"
    r = rel(path)
    _, t, d, ic = next(x for x in TOOLS if x[0] == slug_)
    others = "".join(tool_card(s, r) for s, *_ in TOOLS if s != slug_)
    data = ""
    if slug_ in ("neighborhood-quiz", "compare"):
        data = "<script>window.HOODS=" + json.dumps([dict(slug=h["slug"], name=h["name"], line=h["line"], region=h["region"],
                                                            city=h["city"], tier=h["tier"], tags=h["tags"], zips=h["zips"],
                                                            feel=h["feel"], housing=h["housing"], fit=h["fit"], skip=h["skip"],
                                                            ll=h["ll"], golf=hood_flags(h)[0], trails=hood_flags(h)[1])
                                                       for h in ORDER]) + ";window.CITIES=" + json.dumps(CITIES) + ";window.TAGS=" + json.dumps(TAGS) + "</script>"
    extra = f"""<section class="band" style="padding-top:0"><div class="wrap">
<div class="head"><div><p class="eyebrow">Keep going</p><h2 class="h2">More tools</h2></div></div>
<div class="tools">{others}</div></div></section>
{contact_band(r, "Want me to run it for a real property?", "Send the address or the area. I'll run the real numbers with current comps and tell you what I'd do.", preset, msg, f"Website lead: {t}", form=True)}
"""
    body = f"""{nav(path, "tools")}
<main class="toolpage" data-tool="{slug_}">
<section class="band tight"><div class="wrap">
<div class="crumbs"><a href="{r}tools/">Tools</a> / {e(t)}</div>
<h1 class="h1">{e(t)}</h1>
<p class="lede" style="margin-top:14px">{e(d)}</p>
</div></section>
<section class="band" style="padding-top:0"><div class="wrap">{inner}</div></section>
{"" if lean else extra}
</main>
{data}
{foot(path, scripts)}"""
    return head(f"{title} | Nathaniel Grivas", desc, path, ld(crumbs_ld([("Home", "/"), ("Tools", "/tools/"), (t, path)]))) + body


def field(label, name, value, kind="number", attrs="", hint=""):
    h = f'<small>{hint}</small>' if hint else ""
    return f'<label class="fld"><span>{label}</span><input name="{name}" type="{kind}" value="{value}" inputmode="decimal" {attrs}>{h}</label>'



def page_quiz():
    pool = "".join(photo_tile(h) .replace('<a class="tile', f'<a data-slug="{h["slug"]}" class="tile', 1) for h in ORDER)
    inner = f"""<div class="intake glass" data-intake>
<div class="qbar"><i></i></div>
<div class="qtop"><button type="button" class="qback" hidden>&larr; Back</button><span class="qcount"></span></div>
<div class="qhost" aria-live="polite"></div>
<div class="qres" hidden></div>
</div>
<div id="pool" hidden>{pool}</div>
<form class="lead qlead" data-to="{FORM_TO}" data-subject="Website lead: intake" novalidate hidden>
<input type="hidden" name="looking" value="">
<textarea name="message" hidden></textarea>
<div class="f"><label>Name<input name="name" autocomplete="name" required></label></div>
<div class="f"><label>Phone<input name="phone" type="tel" autocomplete="tel"></label></div>
<div class="f full"><label>Email<input name="email" type="email" autocomplete="email" required></label></div>
<div class="f full lenderbox" hidden><label class="check"><input type="checkbox" name="lender" value="yes"> Introduce me to a lender</label></div>
<div class="f full"><button class="btn solid big" type="submit">Send to Nathaniel</button></div>
<p class="formmsg" role="status" aria-live="polite"></p>
<p class="formnote">By sending, you agree I can contact you by call, text or email about real estate. Reply STOP to opt out of texts. <a href="/privacy/">Privacy</a></p>
</form>"""
    return tool_shell("neighborhood-quiz", "Find Your Place in LA: Buy, Rent, Invest or Build",
                      "Tell me what you're looking for and get matched to the Los Angeles neighborhoods that fit: buyers, renters, investors and developers.",
                      inner, scripts=("quiz.js",), preset="buy", lean=True)


def page_tax():
    opts = "".join(f'<option value="{slug(k)}">{e(v["label"])}</option>' for k, v in CITIES.items())
    inner = f"""<div class="calc" id="taxcalc">
<form class="inputs" onsubmit="return false">
{field("Sale price", "price", "5500000", "text", 'data-money')}
<label class="fld"><span>Where is the property?</span><select name="city">{opts}</select><small>Not sure? 90210, 90049 and 90272 addresses can be City of LA. Check the <a href="/tools/la-rules/">city guide</a>.</small></label>
<label class="chk" id="teRow"><input type="checkbox" name="te"> Palisades Fire home sold by its January 2025 owner (Prop TE)</label>
</form>
<div class="out">
<div class="bigline"><span>Total transfer taxes</span><b id="tTotal">$0</b><small id="tRate"></small></div>
<table class="rows"><tbody id="tRows"></tbody></table>
<div class="bigline net"><span>Sale price minus transfer taxes</span><b id="tNet">$0</b></div>
<div class="warn" id="tWarn" hidden></div>
</div>
</div>
<div class="body narrow notes">
<h2>How each city charges</h2>
<ul>
<li><b>City of Los Angeles:</b> 0.45% city tax on every sale, plus Measure ULA on the full price: 4% above $5.4M and 5.5% at $10.9M and up for sales closing July 1, 2026 or later. The thresholds adjust every July 1.</li>
<li><b>Santa Monica:</b> one city rate on the full price: 0.3% under $5M, 0.6% from $5M, 5.6% at $8M and up.</li>
<li><b>Culver City:</b> Measure RE brackets that work like income tax, each rate applying only to the slice of price inside it: 0.45% up to $1.5M, 1.5% to $3M, 3% to $10M, 4% above. The city can adjust the bracket lines for inflation, so confirm with Culver City.</li>
<li><b>Beverly Hills, West Hollywood, Malibu and unincorporated areas like Marina del Rey:</b> no city transfer tax. Only the county's 0.11%.</li>
<li><b>Everyone:</b> LA County charges $1.10 per $1,000 (0.11%).</li>
</ul>
<p>Who pays is negotiable. In LA the seller customarily pays transfer taxes, but it's a term in the contract. This calculator estimates taxes only. It skips exemptions, escrow, title and commission. Read more in <a href="/guide/measure-ula-mansion-tax-2026/">Measure ULA in 2026</a>.</p>
<p class="sources">Sources: <a href="https://finance.lacity.gov/faq/measure-ula">LA Office of Finance</a>, <a href="https://santamonica.gov/documentary-transfer-tax-real-property-transfer-tax">City of Santa Monica</a>, <a href="https://www.culvercity.gov/Services/Make-a-Payment/Real-Property-Transfer-Tax">City of Culver City</a>, <a href="https://weho.org/city-government/city-departments/finance-and-technology-services/taxes/property-taxes">City of West Hollywood</a>, <a href="https://www.lavote.gov/home/records/property-document-recording/documentary-transfer-taxes">LA County Registrar-Recorder</a>.</p>
</div>"""
    return tool_shell("transfer-tax", "LA Transfer Tax & Measure ULA Calculator (2026)",
                      "Estimate transfer taxes on a sale in the City of LA, Santa Monica, Culver City, Beverly Hills, West Hollywood or Malibu, including the Measure ULA mansion tax cliff.",
                      inner, preset="sell", msg="Can you run my net proceeds for a sale at ")


def page_mortgage():
    inner = f"""<div class="tabs" role="tablist"><button type="button" role="tab" aria-selected="true" data-tab="pay">Monthly cost of a price</button><button type="button" role="tab" aria-selected="false" data-tab="afford">Price for a monthly budget</button></div>
<div class="calc" id="mortcalc">
<form class="inputs" onsubmit="return false">
<div data-pane="pay">{field("Home price", "price", "1500000", "text", 'data-money')}</div>
<div data-pane="afford" hidden>{field("Monthly budget, all in", "budget", "9000", "text", 'data-money')}</div>
<label class="fld"><span>Down payment <output id="dpOut">20%</output></span><input name="down" type="range" min="3" max="60" step="1" value="20"></label>
{field("Interest rate (%)", "rate", "6.5", "number", 'step="0.05" min="0"', "Example rate. Use your lender's quote.")}
<label class="fld"><span>Loan term</span><select name="term"><option value="30">30 years</option><option value="15">15 years</option></select></label>
{field("Property tax rate (%)", "ptax", "1.2", "number", 'step="0.05" min="0"', "Prop 13 base is 1% plus local bonds and assessments. Check the actual bill.")}
{field("Insurance per year", "ins", "4000", "text", 'data-money', "Fire zones and hillsides can run much higher.")}
{field("HOA per month", "hoa", "0", "text", 'data-money')}
</form>
<div class="out">
<div class="bigline"><span id="mHead">Monthly payment</span><b id="mBig">$0</b><small id="mSub"></small></div>
<div class="stack" id="mStack"></div>
<table class="rows"><tbody id="mRows"></tbody></table>
<p class="fine">Estimate only. Excludes PMI, Mello-Roos and special assessments, and closing costs. Loan programs, limits and qualifying rules vary by lender.</p>
</div>
</div>"""
    return tool_shell("mortgage", "LA Mortgage & Affordability Calculator",
                      "See the full monthly cost of a Los Angeles home with taxes, insurance and HOA, or find the price a monthly budget buys.",
                      inner, preset="buy")


def page_rvb():
    inner = f"""<div class="calc" id="rvbcalc">
<form class="inputs" onsubmit="return false">
<p class="grp">Renting</p>
{field("Monthly rent", "rent", "6000", "text", 'data-money')}
{field("Rent increase per year (%)", "rentg", "3", "number", 'step="0.5"')}
<p class="grp">Buying</p>
{field("Home price", "price", "1400000", "text", 'data-money')}
<label class="fld"><span>Down payment <output id="rdpOut">20%</output></span><input name="down" type="range" min="3" max="60" step="1" value="20"></label>
{field("Interest rate (%)", "rate", "6.5", "number", 'step="0.05"', "Example rate. Use your lender's quote.")}
{field("Property tax rate (%)", "ptax", "1.2", "number", 'step="0.05"')}
{field("Insurance, maintenance and HOA per month", "own", "1200", "text", 'data-money')}
<p class="grp">Assumptions</p>
{field("Years you'll stay", "years", "7", "number", 'min="1" max="30"')}
{field("Home value growth per year (%)", "appr", "3", "number", 'step="0.5"')}
{field("Return on money you don't put into a house (%)", "inv", "5", "number", 'step="0.5"')}
{field("Buying costs (% of price)", "buyc", "2", "number", 'step="0.5"')}
{field("Selling costs (% of price)", "sellc", "6", "number", 'step="0.5"', "Transfer taxes, escrow, title and commission.")}
</form>
<div class="out">
<div class="bigline"><span id="rHead">After 7 years</span><b id="rBig">$0</b><small id="rSub"></small></div>
<svg class="chart" id="rChart" viewBox="0 0 600 240" role="img" aria-label="Buying minus renting, by year"></svg>
<table class="rows"><tbody id="rRows"></tbody></table>
<p class="fine">Compares where your money ends up: home equity after a sale versus the down payment and monthly savings invested. Skips income tax effects and assumes the renter invests every dollar the owner spends above rent. All assumptions are yours to change.</p>
</div>
</div>"""
    return tool_shell("rent-vs-buy", "Rent vs. Buy Calculator for Los Angeles",
                      "Compare renting and buying in LA with your own numbers. See the year buying pulls ahead, if it does.",
                      inner, preset="buy")


def page_compare():
    opts = "".join(f'<option value="{h["slug"]}">{e(h["name"])}</option>' for h in sorted(HOODS, key=lambda x: x["name"]))
    inner = f"""<div class="cmp">
<div class="cmp-pick"><label class="fld"><span>Neighborhood A</span><select id="ca">{opts}</select></label><span class="vs">vs</span><label class="fld"><span>Neighborhood B</span><select id="cb">{opts}</select></label></div>
<div class="cmp-table" id="ctable"></div>
</div><div id="pool" hidden>{"".join(hood_card(h, "/") for h in ORDER)}</div>"""
    return tool_shell("compare", "Compare Two LA Neighborhoods Side by Side",
                      "Compare two Los Angeles neighborhoods side by side: city rules, schools, Measure ULA, rent control, price level and daily life.",
                      inner, preset="buy")


def page_rules():
    r = "/"
    rows = [("Transfer tax", "transfer"), ("Measure ULA", "ula"), ("Rent control", "rent"), ("Public schools", "schools")]
    cards = ""
    for k, c in CITIES.items():
        hs = [h for h in ORDER if h["city"] == k]
        links = "".join(f'<a href="{r}neighborhoods/{h["slug"]}/">{e(h["name"])}</a>' for h in hs)
        dl = "".join(f'<dt>{n}</dt><dd>{e(c[f])}</dd>' for n, f in rows)
        cards += f'<div class="citycard"><h3>{e(c["label"])}</h3><dl>{dl}</dl><div class="chips">{links}</div><a class="btn small" href="/tools/transfer-tax/?city={slug(k)}">Run a sale here</a></div>'
    inner = f"""<div class="body narrow" style="margin-bottom:28px">
<p>Los Angeles County has 88 cities, and the Westside alone has five of them sitting next to each other. Beverly Hills, Santa Monica, Culver City, West Hollywood and Malibu each set their own transfer taxes, rent control and schools. Brentwood, Bel Air, Venice, Pacific Palisades and the Valley are all inside the City of LA. Marina del Rey belongs to no city at all.</p>
<p>That's how two homes a block apart can owe very different taxes at sale, follow different rent rules and feed into different school districts. A few that catch people:</p>
<ul>
<li><b>90210 isn't always Beverly Hills.</b> The hills above it, Beverly Hills Post Office, use 90210 but are in the City of LA. <a href="{r}neighborhoods/bhpo/">See BHPO</a>.</li>
<li><b>Measure ULA stops at the city line.</b> A $6M sale in Brentwood pays it. The same sale in Santa Monica pays Santa Monica's tier instead.</li>
<li><b>Culver City taxes by bracket.</b> Only the slice of price inside each bracket pays that bracket's rate.</li>
</ul>
<p>To check an exact address, LA's <a href="https://zimas.lacity.org/" rel="noopener">ZIMAS</a> shows whether a parcel is in the City of LA. The county's assessor portal shows the rest.</p>
</div>
<div class="citygrid">{cards}</div>
<p class="sources body narrow">Sources: <a href="https://finance.lacity.gov/faq/measure-ula">LA Office of Finance</a>, <a href="https://santamonica.gov/documentary-transfer-tax-real-property-transfer-tax">City of Santa Monica</a>, <a href="https://www.culvercity.gov/City-Hall/General-Info-Finance/Local-Voter-Approved-Tax-Measures">City of Culver City</a>, <a href="https://weho.org/city-government/city-departments/finance-and-technology-services/taxes/property-taxes">City of West Hollywood</a>, <a href="https://www.lavote.gov/home/records/property-document-recording/documentary-transfer-taxes">LA County Registrar-Recorder</a>, <a href="https://www.malibucity.org/MUSD">City of Malibu</a>. Rent control summaries are simplified and every ordinance has exemptions.</p>"""
    return tool_shell("la-rules", "LA Isn't One City: Transfer Tax, Rent Control & Schools by City",
                      "How transfer taxes, Measure ULA, rent control and school districts change between the City of LA, Santa Monica, Beverly Hills, Culver City, West Hollywood and Malibu.",
                      inner, scripts=(), preset="sell")


def page_featured(k):
    f = FEATURED[k]
    p_ = PROPS[k]
    path = p_["page"]
    other = "fuller" if k == "evans" else "evans"
    o = FEATURED[other]
    film = film_evans(True) if k == "evans" else film_fuller()
    stats = "".join(f'<div><b>{e(v)}</b><span>{e(l)}</span></div>' for v, l in f["stats"])
    body_p = "".join(f"<p>{e(x)}</p>" for x in f["body"])
    links = ""
    if f.get("site"):
        links += f'<a class="btn lux" href="{f["site"]}" rel="noopener">{f["site"].split("//")[1].strip("/")} &#8599;</a>'
    links += f'<a class="btn lux" href="{f["compass"]}" rel="noopener">View on Compass &#8599;</a>'
    gal = ""
    if k == "evans":
        figs = "".join(f'<button type="button" class="g" data-full="/img/evans/{pid}.jpg" data-alt="{e(alt)}" aria-label="View photo: {e(alt)}"><img src="/img/evans/{pid}.jpg" alt="{e(alt)}" loading="lazy" width="1600" height="1067"></button>' for pid, alt in EVANS_PHOTOS)
        all_ = "".join(f'<i data-full="/img/evans/{pid}.jpg" data-alt="{e(alt)}"></i>' for pid, alt in EVANS_PHOTOS)
        gal = f'<section class="band lux-band"><div class="wrap"><div class="lux-head"><p class="kick">Gallery</p><h2>Inside {e(f["title"])}</h2></div><div class="hgal" data-gallery>{figs}<div hidden class="gall">{all_}</div></div></div></section>'
    cta_txt = "Schedule a showing" if f["status"] != "Sold" else "Ask about homes like this"
    body = f"""{nav(path, "listings")}
<main>
<section class="home-top"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/listings/">Listings</a> / <span>{e(f["title"])}</span></nav>
<div class="ht-grid{" tall" if k == "fuller" else ""}">
<div class="ht-film">{film}</div>
<div class="ht-copy">
<p class="kick">{e(f["status"])} &middot; {e(f["where"].split(",")[0])}</p>
<h1>{e(f["title"])}</h1>
<p class="ht-where">{e(f["where"])}</p>
<p class="ht-price">{"Sold for " if f["status"] == "Sold" else "Offered at "}{e(f["price"])}</p>
<div class="ht-stats">{stats}</div>
<p class="ht-line">{e(f["line"])}</p>
<div class="lh-cta"><button type="button" class="btn lux solid" data-msg>{cta_txt}</button><a class="btn lux" href="tel:{TEL}">Call {PHONE}</a></div>
<div class="lh-cta">{links}</div>
<p class="ht-credit">{e(f["credit"])}</p>
</div></div></div></section>
<section class="band lux-band"><div class="wrap narrow ht-body"><p class="kick">The home</p>{body_p}</div></section>
{gal}
<section class="band lux-band"><div class="wrap"><div class="lux-head"><p class="kick">Also featured</p><h2><a class="plain" href="{PROPS[other]["page"]}">{e(o["title"])}</a></h2></div>
<a class="also" href="{PROPS[other]["page"]}"><img src="{o["poster"]}" alt="{e(o["title"])}" loading="lazy"><span><small>{e(o["status"])} &middot; {e(o["price"])}</small><b>{e(o["title"])}</b>{e(o["line"])} <i>Watch the film &rarr;</i></span></a></div></section>
{contact_band("/", "Want a result like this?", f"Thinking about selling, or looking for a home like this in the {f['where'].split(',')[0]}? Tell me what you're after.", "sell", "", "Website lead: " + f["title"] + " (sold)", form=True) if f["status"] == "Sold" else contact_band("/", "Let's talk", "Questions about this home, or looking for something like it? Send me a note.", "buy", "Interested in " + f["title"], "Website lead: " + f["title"], form=True)}
{'<div class="lightbox" hidden role="dialog" aria-modal="true" aria-label="Photo viewer"><button type="button" class="lb-x" aria-label="Close">&times;</button><button type="button" class="lb-p" aria-label="Previous photo">&lsaquo;</button><img alt=""><button type="button" class="lb-n" aria-label="Next photo">&rsaquo;</button><p class="lb-c"></p></div>' if gal else ''}
</main>
{foot(path)}"""
    ld_ = {"@context": "https://schema.org", "@type": "SingleFamilyResidence", "name": f["title"], "url": SITE + path,
           "address": {"@type": "PostalAddress", "streetAddress": f["title"], "addressLocality": "Los Angeles", "addressRegion": "CA", "postalCode": f["where"][-5:]},
           "numberOfRooms": f["stats"][0][0], "floorSize": {"@type": "QuantitativeValue", "value": f["stats"][2][0].replace(",", ""), "unitCode": "FTK"},
           "image": SITE + f["poster"], "description": f["line"]}
    title = f'{f["title"]}, {f["where"].split(",")[0]} | {f["status"]} {f["price"]} | Nathaniel Grivas'
    return head(title, f["line"], path, ld(ld_) + ld(crumbs_ld([("Home", "/"), ("Listings", "/listings/"), (f["title"], path)])), og=f["poster"].replace("/img/", "")) + body


def page_listings():
    path = "/listings/"
    r = rel(path)
    body = f"""{nav(path, "listings")}
<main>
<section class="band tight"><div class="wrap">
<p class="eyebrow">Listings</p><h1 class="h1">For sale, for lease and recently closed</h1>
<p class="lede" style="margin-top:14px">Homes I'm representing now and deals I've closed for buyers, sellers, tenants and landlords.</p>
</div></section>
{featured_section("Featured homes", "Watch the films")}
<section class="band" style="padding-top:0"><div class="wrap">
<div class="head"><div><p class="eyebrow">Now available</p><h2 class="h2">Active</h2></div></div>
<div class="grid">{"".join(prop_card(k, r) for k in ACTIVE)}</div></div></section>
<section class="band" style="padding-top:0"><div class="wrap">
<div class="head"><div><p class="eyebrow">Track record</p><h2 class="h2">Closed</h2></div></div>
<div class="grid">{"".join(prop_card(k, r) for k in SOLD)}</div></div></section>
{contact_band(r, "Get homes before they hit the market", "Tell me the area and the budget. Off-market and coming-soon homes go to my list first.", "buy", "", "Website lead: off-market list")}
</main>
{foot(path)}"""
    return head("Listings | Nathaniel Grivas, Compass", "Active listings and recent transactions by Nathaniel Grivas, REALTOR® at Compass.", path) + body


def page_about():
    path = "/about/"
    r = rel(path)
    body = f"""{nav(path, "about")}
<main>
<section class="band"><div class="wrap split">
<div class="portrait"><img src="{r}img/nate-about.jpg" alt="Nathaniel Grivas, REALTOR at Compass" width="900" height="990"></div>
<div><p class="eyebrow">About Nathaniel</p><h1 class="h1">Nathaniel Grivas</h1>
<p class="lede" style="margin-top:18px">Raised between New York and Seattle before relocating to Los Angeles, Nathaniel Grivas is a REALTOR&reg; with The Brodsky Group at Compass Beverly Hills, a team with over $100M in annual sales. He represents buyers, sellers, landlords and developers across West Los Angeles, Beverly Hills and the San Fernando Valley.</p>
<div class="facts"><div class="glass"><b>$100M+</b><span>annual team sales</span></div><div><b>DRE</b><span>#{DRE}</span></div><div><b>LMU</b><span>Marketing &amp; Business Law</span></div></div>
<div class="cta-row"><a class="btn solid" href="tel:{TEL}">Call {PHONE}</a><a class="btn" href="#contact" data-msg>Send a message</a><a class="btn ext" href="{BG}" rel="noopener">The Brodsky Group</a></div>
</div></div></section>
<section class="band" style="padding-top:0"><div class="wrap narrow body">
<h2>How I work</h2>
<p>I earned my degree in Marketing and Business Law from Loyola Marymount University, and that shapes how I approach outreach, positioning and negotiation. My work covers listing preparation and pricing strategy, buyer representation in competitive offers, leasing, new construction and development deals, including teardown and lot value analysis, ADU feasibility and off-market sourcing.</p>
<h2>Where I work</h2>
<p>From Malibu and the Palisades to Los Feliz and Silver Lake, and across the Valley. Every area I cover has a guide on the <a href="{r}neighborhoods/">Explore LA map</a>.</p>
<h2>Outside of real estate</h2>
<p>Basketball, golf and tennis, and time with friends and family. I write about the parts of LA that are actually worth your time in the <a href="{r}guide/">LA Guide</a>.</p>
</div></section>
{team_section("team-2.jpg", "I work on The Brodsky Group, led by Or Brodsky at Compass Beverly Hills. Over $100M in sales every year, from new construction to off-market deals.")}
{contact_band(r)}
</main>
{foot(path)}"""
    desc = "About Nathaniel Grivas, REALTOR® with The Brodsky Group at Compass Beverly Hills. DRE #02410660."
    return head("About Nathaniel Grivas | REALTOR® at Compass", desc, path, ld(person_ld())) + body


def place_card(p, d, hood_name, show_hood=False, primary=None):
    src = "".join(f'<a href="{d["sources"][k][1]}" rel="noopener">{e(d["sources"][k][0].split(":")[0])}</a>' for k in p.get("s", []) if k in d["sources"])
    chips = "".join(f'<span>{e(G.CATS[c][0])}</span>' for c in p["c"] if c != primary)
    where = (f'<a href="/guide/{d["slug"]}/">{e(hood_name)}</a> &middot; ' if show_hood else "") + e(p.get("a") or "")
    tip = f'<p class="pc-o"><b>{"Do" if G.CATS[p["c"][0]][2] == "do" else "Order"}:</b> {e(p["o"])}</p>' if p.get("o") else ""
    return (f'<article class="pc"><div class="pc-h"><h3>{e(p["n"])}</h3><span class="pc-p">{e(p.get("p", ""))}</span></div>'
            f'<p class="pc-a">{where}</p><p class="pc-w">{e(p["w"])}</p>{tip}'
            f'<div class="pc-f"><a class="pc-map" href="{G.maps_url(p, hood_name)}" rel="noopener">Map &#8599;</a>{("<span class=pc-s>Sources: " + src + "</span>") if src else ""}</div>'
            f'{("<div class=pc-c>" + chips + "</div>") if chips else ""}</article>')


def guide_counts():
    cnt = {}
    for d in GUIDES.values():
        for p in d["places"]:
            for c in p["c"]:
                cnt[c] = cnt.get(c, 0) + 1
    return cnt


def page_hood_guide(d):
    h = BY_SLUG[d["slug"]]
    path = f"/guide/{d['slug']}/"
    places_ = d["places"]
    by = {}
    for p in places_:
        by.setdefault(p["c"][0], []).append(p)
    nav_ = ""
    secs = ""
    for g, glabel, items in G.GROUPS:
        gsec = ""
        for k, label, _ in items:
            ps = by.get(k)
            if not ps:
                continue
            nav_ += f'<a href="#{k}">{e(label)} <i>{len(ps)}</i></a>'
            gsec += f'<section class="gsec" id="{k}"><h3 class="gsec-h">{e(label)}</h3><div class="pcs">{"".join(place_card(p, d, h["name"], primary=k) for p in ps)}</div></section>'
        if gsec:
            secs += f'<div class="ggroup"><p class="kick">{e(glabel)}</p>{gsec}</div>'
    srcs = "".join(f'<li><a href="{u}" rel="noopener">{e(t)}</a></li>' for t, u in d["sources"].values())
    photo = ""
    ph = PHOTOS.get(d["slug"]) or []
    if ph:
        photo = f'<figure class="gh-ph">{ph_img(ph[0][0], ph[0][1], 1400, 0.56, "(max-width:900px) 100vw, 50vw")}</figure>'
    others = [x for x in GUIDES.values() if x["slug"] != d["slug"]][:8]
    more = "".join(f'<a href="/guide/{x["slug"]}/">{e(BY_SLUG[x["slug"]]["name"])}</a>' for x in others)
    body = f"""{nav(path, "guide")}
<main>
<section class="ghero"><div class="wrap gh-grid">
<div><nav class="crumbs" aria-label="Breadcrumb"><a href="/guide/">The LA Guide</a> / <span>{e(h["name"])}</span></nav>
<p class="kick">The LA Guide</p>
<h1>{e(h["name"])}: where to eat, drink and go</h1>
<p class="lede">{e(d["intro"])}</p>
<p class="gh-meta">{len(places_)} places &middot; Updated {e(d["updated"])} &middot; Written from critic reviews, user tips and ratings, rewritten in plain English</p>
<div class="lh-cta"><a class="btn lux solid" href="#{by and next(iter(by))}">Start reading</a><a class="btn lux" href="/neighborhoods/{d["slug"]}/">Living in {e(h["name"])}</a></div>
</div>{photo}</div></section>
<nav class="gnav" aria-label="Categories"><div class="wrap">{nav_}</div></nav>
<div class="wrap gbody">{secs}</div>
{journal_band(d["slug"], h["name"])}
<section class="band lux-band"><div class="wrap"><div class="gend">
<div><p class="kick">Thinking about living here?</p><h2>Homes in {e(h["name"])}</h2><p>Tell me what you're after and I'll send new {e(h["name"])} listings as they hit the market.</p>
<div class="lh-cta"><a class="btn lux solid" href="{intake_url("buy", d["slug"])}">Get {e(h["name"])} listings</a><a class="btn lux" href="/neighborhoods/{d["slug"]}/">The {e(h["name"])} neighborhood guide</a></div></div>
<div><p class="kick">More guides</p><div class="gend-l">{more}<a href="/guide/">All neighborhoods &rarr;</a></div>
<details class="gsrc"><summary>Sources</summary><ul>{srcs}</ul></details></div>
</div></div></section>
</main>
{foot(path)}"""
    items = [{"@type": "ListItem", "position": i + 1, "name": p["n"]} for i, p in enumerate(places_)]
    ld_ = {"@context": "https://schema.org", "@type": "ItemList", "name": f"Where to eat, drink and go in {h['name']}", "itemListElement": items}
    title = f"{h['name']} Guide: Best Restaurants, Coffee, Bars & Things to Do | The LA Guide"
    desc = f"The best of {h['name']}, Los Angeles: {len(places_)} restaurants, coffee shops, bars and things to do, picked from critic reviews and real user tips."
    return head(title, desc, path, ld(ld_) + ld(crumbs_ld([("Home", "/"), ("The LA Guide", "/guide/"), (h["name"], path)]))) + body


def page_best(cat):
    label, plural, _ = G.CATS[cat]
    path = f"/guide/best/{cat}/"
    rows = []
    for d in GUIDES.values():
        h = BY_SLUG[d["slug"]]
        for p in d["places"]:
            if cat in p["c"]:
                rows.append((h, d, p))
    by_reg = {}
    for h, d, p in rows:
        by_reg.setdefault(h["region"], []).append((h, d, p))
    secs = ""
    for reg in REGIONS:
        if reg not in by_reg:
            continue
        secs += f'<section class="gsec"><h3 class="gsec-h">{e(reg)}</h3><div class="pcs">{"".join(place_card(p, d, h["name"], show_hood=True, primary=cat) for h, d, p in by_reg[reg])}</div></section>'
    cnt = guide_counts()
    other = "".join(f'<a href="/guide/best/{k}/">{e(G.CATS[k][0])} <i>{cnt[k]}</i></a>' for k in G.ORDERED if cnt.get(k) and k != cat)
    body = f"""{nav(path, "guide")}
<main>
<section class="ghero"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/guide/">The LA Guide</a> / <span>{e(label)}</span></nav>
<p class="kick">The LA Guide</p>
<h1>The best {e(plural)} in Los Angeles</h1>
<p class="lede">{len(rows)} picks across the neighborhoods I cover, grouped by area. Each one is written from what critics and real people consistently say about it.</p>
</div></section>
<div class="wrap gbody">{secs}</div>
<section class="band lux-band"><div class="wrap"><div class="lux-head"><p class="kick">Keep browsing</p><h2>More categories</h2></div><div class="gcats">{other}</div></div></section>
</main>
{foot(path)}"""
    title = f"Best {label} in Los Angeles by Neighborhood | The LA Guide"
    desc = f"The best {plural} in Los Angeles, neighborhood by neighborhood, picked from critic reviews and real user tips."
    return head(title, desc, path, ld(crumbs_ld([("Home", "/"), ("The LA Guide", "/guide/"), (label, path)]))) + body


def page_guide(posts):
    path = "/guide/"
    r = rel(path)
    cnt = guide_counts()
    total = sum(len(d["places"]) for d in GUIDES.values())
    cats = ""
    for g, glabel, items in G.GROUPS:
        links = "".join(f'<a href="/guide/best/{k}/">{e(label)} <i>{cnt[k]}</i></a>' for k, label, _ in items if cnt.get(k))
        if links:
            cats += f'<div class="gcatg"><p class="kick">{e(glabel)}</p><div class="gcats">{links}</div></div>'
    ready = [BY_SLUG[s_] for s_ in GUIDES if s_ in BY_SLUG]
    tiles = "".join(
        f'<a class="gtile" href="/guide/{h["slug"]}/">{(ph_img(PHOTOS[h["slug"]][0][0], PHOTOS[h["slug"]][0][1], 700, 0.7, "(max-width:700px) 50vw, 25vw") if PHOTOS.get(h["slug"]) else mini_map(h, 320, 0.7, 1.2))}'
        f'<span><small>{e(h["region"])}</small><b>{e(h["name"])}</b><em>{len(GUIDES[h["slug"]]["places"])} places</em></span></a>' for h in ready)
    soon = [h for h in ORDER if h["slug"] not in GUIDES]
    soon_html = ""
    if soon:
        soon_html = f'<p class="gsoon"><b>Being researched now:</b> {", ".join(e(h["name"]) for h in soon)}. New neighborhoods are added every week.</p>'
    listing = "".join(post_card(p, r) for p in posts)
    body = f"""{nav(path, "guide")}
<main>
<section class="ghero"><div class="wrap">
<p class="kick">The LA Guide</p>
<h1>Where to eat, drink and go in every corner of LA</h1>
<p class="lede">{total} places across {len(ready)} neighborhoods so far, from coffee and brunch to dive bars, live music, hikes and golf. Every pick is written from what critics and real people consistently say about it, and checked again as places open and close.</p>
</div></section>
{journal_teaser()}
<section class="band lux-band" style="padding-top:10px"><div class="wrap">
<div class="lux-head"><p class="kick">By neighborhood</p><h2>Pick a neighborhood</h2></div>
<div class="gtiles">{tiles}</div>{soon_html}
</div></section>
<section class="band lux-band"><div class="wrap">
<div class="lux-head"><p class="kick">By category</p><h2>The best of LA</h2></div>{cats}
</div></section>
<section class="band lux-band"><div class="wrap">
<div class="lux-head"><p class="kick">Articles</p><h2>Living in LA</h2></div>
<div class="posts" id="postlist">{listing}</div>
</div></section>
</main>
{foot(path)}"""
    desc = f"The LA Guide by Nathaniel Grivas: the best restaurants, coffee, bars and things to do in {len(ready)} Los Angeles neighborhoods, picked from critic reviews and real user tips."
    return head("The LA Guide: Best Restaurants, Bars & Things to Do by Neighborhood | Nathaniel Grivas", desc, path) + body


def page_post(p, posts):
    path = f"/guide/{p['slug']}/"
    r = rel(path)
    t, line = CTAS.get(p.get("cta", "buy"))
    related = [x for x in posts if x["slug"] != p["slug"]][:2]
    rel_html = ""
    if related:
        rel_html = f'<section class="band" style="padding-top:0"><div class="wrap"><div class="head"><h2 class="h2">Keep reading</h2></div><div class="posts">{"".join(post_card(x, r) for x in related)}</div></div></section>'
    hs = [BY_SLUG[s] for s in p.get("hoods", []) if s in BY_SLUG]
    hood_html = ""
    if hs:
        hood_html = f'<section class="band" style="padding-top:0"><div class="wrap"><div class="head"><div><p class="eyebrow">Mentioned in this post</p><h2 class="h2">Neighborhood guides</h2></div></div><div class="hgrid">{"".join(hood_card(h, r) for h in hs)}</div></div></section>'
    tools = p.get("tools", [])
    tool_html = ""
    if tools:
        tool_html = f'<section class="band" style="padding-top:0"><div class="wrap"><div class="tools">{"".join(tool_card(s, r) for s in tools)}</div></div></section>'
    art = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["description"],
           "datePublished": p["date"], "dateModified": p.get("updated", p["date"]),
           "author": {"@type": "Person", "name": "Nathaniel Grivas", "url": SITE + "/about/"},
           "publisher": {"@type": "Person", "name": "Nathaniel Grivas"}, "mainEntityOfPage": SITE + path}
    body = f"""{nav(path, "guide")}
<main>
<article class="band article"><div class="wrap narrow">
<div class="crumbs"><a href="{r}guide/">LA Guide</a> / {e(p['category'])}</div>
<h1>{e(p['title'])}</h1>
<div class="byline"><img src="{r}img/nate.jpg" alt=""><span>By <a href="{r}about/" style="color:inherit">Nathaniel Grivas</a>, REALTOR&reg;<br>{fmt_date(p['date'])}</span></div>
<div class="body">{p['body']}</div>
<div class="endcta"><h3>{e(t)}</h3><p class="muted" style="margin:0">{e(line)}</p>
<div class="cta-row" style="margin-top:4px"><a class="btn solid" href="tel:{TEL}">Call or text {PHONE}</a><a class="btn" href="#contact" data-msg>Send a message</a></div></div>
</div></article>
{tool_html}{hood_html}{rel_html}
{contact_band(r, preset=p.get('cta', 'buy'))}
</main>
{foot(path)}"""
    return head(f"{p['title']} | Nathaniel Grivas", p["description"], path, ld(art)) + body


def page_privacy():
    path = "/privacy/"
    updated = "November 25, 2026"
    body = f"""{nav(path, "")}
<main class="band"><div class="wrap narrow article">
<p class="eyebrow">Privacy</p>
<h1 class="h1">Privacy policy</h1>
<p class="muted">Last updated {updated}</p>
<p>This site is run by Nathaniel Grivas, REALTOR&reg; (DRE #{DRE}), with The Brodsky Group at Compass, {ADDR}. Questions: <a href="mailto:{EMAIL}">{EMAIL}</a> or {PHONE}.</p>
<h2>What I collect</h2>
<p><b>What you give me.</b> Your name, email, phone, the answers you choose or type in the search questions, a property address, and any message you send.</p>
<p><b>How you use the site.</b> The pages you view and for how long, the buttons you tap (for example Call, Text, a listing or a neighborhood), the website or ad that brought you here, and your device type, browser, screen width, language and time zone. Your browser keeps a random visitor ID and this visit's activity in local storage so repeat visits can be connected.</p>
<h2>When it is sent to me</h2>
<p>Your activity is sent to me by email when you send a form, when you tap Call, Text or Email, and when you leave after starting a search or showing interest without reaching out. If your browser sends a Global Privacy Control signal, I don't send activity alerts. Forms you send still include your activity.</p>
<h2>How I use it</h2>
<p>To reply to you, set up home searches and listing alerts, follow up about buying, selling, renting, investing or building, and improve this site. Your contact details and search may be added to my client records at Compass.</p>
<h2>Who it is shared with</h2>
<p>I don't sell your information. It is shared with the services that run this site and deliver messages (Vercel for hosting, FormSubmit for form email), with Compass and The Brodsky Group to provide real estate services, and when the law requires it. Pages also load fonts from Google and neighborhood photos from Unsplash, and a listing video from Vimeo loads when you scroll to it. These services receive standard web request data.</p>
<h2>Calls and texts</h2>
<p>If you send a form, you agree I can contact you by call, text or email about real estate. Reply STOP to any text to opt out. Message and data rates may apply.</p>
<h2>Your choices</h2>
<p>Email me to see, correct or delete what I have about you. You can also clear this site's storage in your browser settings at any time.</p>
<h2>Children</h2>
<p>This site is not meant for anyone under 16, and I don't knowingly collect their information.</p>
</div></main>
{foot(path)}"""
    return head("Privacy Policy | Nathaniel Grivas", "How nathanielgrivas.com collects and uses visitor information.", path) + body


def page_404():
    path = "/404/"
    r = "/"
    cards = "".join(hood_card(h, r) for h in ORDER[:6])
    body = f"""{nav("/", "")}
<main><section class="band"><div class="wrap">
<p class="eyebrow">Page not found</p><h1 class="h1">That street doesn't exist</h1>
<p class="lede" style="margin-top:14px">The page moved or never existed. Here's somewhere better to be.</p>
<div class="cta-row"><a class="btn solid" href="/neighborhoods/">Explore the map</a><a class="btn" href="/">Home</a></div>
</div></section>
<section class="band" style="padding-top:0"><div class="wrap"><div class="hgrid">{cards}</div></div></section></main>
{foot("/")}"""
    return (head("Page not found | Nathaniel Grivas", "Page not found.", path) + body).replace('"../', '"/')


# ------------------------------------------------------------------ write
EXT_A = re.compile(r'<a\b[^>]*\bhref="https?://[^"]+"[^>]*>')


def ext_tabs(html):
    def fix(m):
        tag = m.group(0)
        if "target=" in tag or "nathanielgrivas.com" in tag:
            return tag
        if 'rel="' in tag:
            if "noopener" not in tag:
                tag = tag.replace('rel="', 'rel="noopener ', 1)
        else:
            tag = tag[:-1] + ' rel="noopener"' + ">"
        return tag[:-1] + ' target="_blank">'
    return EXT_A.sub(fix, html)


def write(path, text):
    out = DIST / path.strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(ext_tabs(text))


# ------------------------------------------------------------------ LA Journal (daily, src/journal/YYYY-MM-DD.json)
def load_journal():
    out = []
    d_ = ROOT / "src" / "journal"
    if d_.exists():
        for f in sorted(d_.glob("*.json")):
            j = json.loads(f.read_text())
            if not j.get("draft"):
                out.append(j)
    out.sort(key=lambda j: j["date"], reverse=True)
    return out


JOURNAL = load_journal()


def jdate(d):
    return datetime.date.fromisoformat(d).strftime("%A, %B %-d, %Y")


def jhoods(slugs):
    hs = [BY_SLUG[s_] for s_ in slugs or [] if s_ in BY_SLUG]
    return ", ".join(f'<a href="/guide/{h["slug"]}/">{e(h["name"])}</a>' if h["slug"] in GUIDES else f'<a href="/neighborhoods/{h["slug"]}/">{e(h["name"])}</a>' for h in hs)


def jitem(it, date=None):
    srcs = ", ".join(f'<a href="{u}" rel="noopener">{e(t)}</a>' for t, u in it.get("src", []))
    hs = jhoods(it.get("hoods"))
    when = f'<a href="/journal/{date}/">{fmt_date(date)}</a> &middot; ' if date else ""
    return (f'<article class="jit"><p class="jit-t">{e(it.get("tag", "LA"))}</p><h3>{e(it["h"])}</h3><p class="jit-b">{e(it["t"])}</p>'
            f'<p class="jit-f">{when}{("Neighborhoods: " + hs + " &middot; ") if hs else ""}{("Sources: " + srcs) if srcs else ""}</p></article>')


def journal_for(slug_, n=4):
    rows = []
    for j in JOURNAL:
        for it in j["items"]:
            if slug_ in (it.get("hoods") or []):
                rows.append((j["date"], it))
    return rows[:n]


def journal_band(slug_, name):
    rows = journal_for(slug_)
    if not rows:
        return ""
    return (f'<section class="band lux-band"><div class="wrap"><div class="lux-head"><p class="kick">The LA Journal</p><h2>{e(name)} in the news</h2><a href="/journal/">All journal entries &rarr;</a></div>'
            f'<div class="jits">{"".join(jitem(it, d) for d, it in rows)}</div></div></section>')


def journal_teaser():
    if not JOURNAL:
        return ""
    j = JOURNAL[0]
    heads = "".join(f'<li>{e(it["h"])}</li>' for it in j["items"][:4])
    return (f'<section class="band lux-band" style="padding-top:6px"><div class="wrap"><a class="jteaser" href="/journal/{j["date"]}/">'
            f'<span class="kick">The LA Journal &middot; {jdate(j["date"])}</span><b>{e(j["title"])}</b><span class="jt-d">{e(j["dek"])}</span>'
            f'<ul>{heads}</ul><span class="jt-go">Read today&rsquo;s journal &rarr;</span></a></div></section>')


def page_journal_day(j, newer, older):
    path = f"/journal/{j['date']}/"
    items = "".join(jitem(it) for it in j["items"])
    opens = ""
    if j.get("openings"):
        cards = "".join(
            f'<article class="jit"><p class="jit-t">New opening</p><h3>{e(o["n"])}</h3><p class="jit-b">{e(o["w"])}</p>'
            f'<p class="jit-f">{("Neighborhood: " + jhoods([o.get("hood")]) + " &middot; ") if o.get("hood") else ""}{("Source: " + chr(60) + "a href=" + chr(34) + o["src"][1] + chr(34) + " rel=noopener" + chr(62) + e(o["src"][0]) + "</a>") if o.get("src") else ""}</p></article>'
            for o in j["openings"])
        opens = f'<section class="gsec"><h2 class="gsec-h">New openings</h2><div class="jits">{cards}</div></section>'
    pn = ""
    if newer or older:
        pn = ('<nav class="jpn">' + (f'<a href="/journal/{older["date"]}/">&larr; {fmt_date(older["date"])}</a>' if older else "<span></span>")
              + (f'<a href="/journal/{newer["date"]}/">{fmt_date(newer["date"])} &rarr;</a>' if newer else "") + '</nav>')
    body = f"""{nav(path, "guide")}
<main>
<section class="ghero"><div class="wrap narrow">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/guide/">The LA Guide</a> / <a href="/journal/">The LA Journal</a> / <span>{fmt_date(j["date"])}</span></nav>
<p class="kick">The LA Journal &middot; {jdate(j["date"])}</p>
<h1 class="jh1">{e(j["title"])}</h1>
<p class="lede">{e(j["dek"])}</p>
<p class="gh-meta">By Nathaniel Grivas, REALTOR&reg; &middot; Written in plain English with links to the original reporting</p>
</div></section>
<div class="wrap narrow gbody"><section class="gsec"><h2 class="gsec-h">Today in LA</h2><div class="jits">{items}</div></section>{opens}{pn}</div>
<section class="band lux-band"><div class="wrap"><div class="gend">
<div><p class="kick">Where to go</p><h2>The LA Guide</h2><p>The best restaurants, coffee, bars and things to do in {len(GUIDES)} neighborhoods, updated as places open and close.</p>
<div class="lh-cta"><a class="btn lux solid" href="/guide/">Browse the guide</a><a class="btn lux" href="/journal/">All journal entries</a></div></div>
<div><p class="kick">Buying or selling?</p><h2>Talk to Nate</h2><p>West LA, Beverly Hills and the Valley. Call or text {PHONE}.</p>
<div class="lh-cta"><a class="btn lux solid" href="tel:{TEL}">Call {PHONE}</a><a class="btn lux" href="/neighborhoods/">Explore neighborhoods</a></div></div>
</div></div></section>
</main>
{foot(path)}"""
    art = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": j["title"], "description": j["dek"],
           "datePublished": j["date"], "dateModified": j.get("updated", j["date"]),
           "author": {"@type": "Person", "name": "Nathaniel Grivas", "url": SITE + "/about/"},
           "publisher": {"@type": "Person", "name": "Nathaniel Grivas"}, "mainEntityOfPage": SITE + path}
    title = f"{j['title']} | The LA Journal, {fmt_date(j['date'])}"
    return head(title, j["dek"], path, ld(art) + ld(crumbs_ld([("Home", "/"), ("The LA Guide", "/guide/"), ("The LA Journal", "/journal/"), (fmt_date(j["date"]), path)]))) + body


def page_journal_index():
    path = "/journal/"
    rows = "".join(
        f'<a class="jrow" href="/journal/{j["date"]}/"><span class="kick">{jdate(j["date"])}</span><b>{e(j["title"])}</b><span class="jt-d">{e(j["dek"])}</span>'
        f'<ul>{"".join(chr(60) + "li" + chr(62) + e(it["h"]) + "</li>" for it in j["items"][:3])}</ul></a>' for j in JOURNAL)
    body = f"""{nav(path, "guide")}
<main>
<section class="ghero"><div class="wrap narrow">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/guide/">The LA Guide</a> / <span>The LA Journal</span></nav>
<p class="kick">The LA Journal</p>
<h1>What's happening in LA, every day</h1>
<p class="lede">A short daily read on Los Angeles: city news, new openings, events and the real estate stories worth knowing, written in plain English with links to the original reporting.</p>
</div></section>
<div class="wrap narrow gbody"><div class="jrows">{rows}</div></div>
</main>
{foot(path)}"""
    desc = "The LA Journal by Nathaniel Grivas: a short daily roundup of Los Angeles news, new restaurant openings, events and real estate, with links to the original reporting."
    return head("The LA Journal: Daily Los Angeles News, Openings & Events | Nathaniel Grivas", desc, path, ld(crumbs_ld([("Home", "/"), ("The LA Guide", "/guide/"), ("The LA Journal", path)]))) + body


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    # assets/ and img/ are optional so the guide can be rebuilt from src/ alone
    for d in ("assets", "img"):
        if (ROOT / d).exists():
            shutil.copytree(ROOT / d, DIST / d)
        else:
            (DIST / d).mkdir()
    posts = load_posts()
    pages = {
        "/": page_home(posts), "/neighborhoods/": page_explore(), "/tools/": page_tools(),
        "/tools/neighborhood-quiz/": page_quiz(), "/tools/transfer-tax/": page_tax(), "/tools/mortgage/": page_mortgage(),
        "/tools/rent-vs-buy/": page_rvb(), "/tools/compare/": page_compare(), "/tools/la-rules/": page_rules(),
        "/listings/": page_listings(), "/about/": page_about(), "/guide/": page_guide(posts), "/privacy/": page_privacy(),
        "/homes/3721-evans/": page_featured("evans"), "/homes/616-fuller/": page_featured("fuller"),
    }
    for h in HOODS:
        pages[f"/neighborhoods/{h['slug']}/"] = page_hood(h, posts)
    for p in posts:
        pages[f"/guide/{p['slug']}/"] = page_post(p, posts)
    for d in GUIDES.values():
        if d["slug"] in BY_SLUG:
            pages[f"/guide/{d['slug']}/"] = page_hood_guide(d)
    for k, n in guide_counts().items():
        if n:
            pages[f"/guide/best/{k}/"] = page_best(k)
    if JOURNAL:
        pages["/journal/"] = page_journal_index()
        for i, j in enumerate(JOURNAL):
            pages[f"/journal/{j['date']}/"] = page_journal_day(j, JOURNAL[i - 1] if i > 0 else None, JOURNAL[i + 1] if i + 1 < len(JOURNAL) else None)
    for u, t in pages.items():
        write(u, t)
    (DIST / "404.html").write_text(ext_tabs(page_404()))
    # the phone link page keeps living at /links/ and on nathanielgrivas.vercel.app
    links = ROOT / "links" / "index.html"
    if links.exists():
        (DIST / "links").mkdir(exist_ok=True)
        shutil.copy(links, DIST / "links" / "index.html")
    (DIST / "vercel.json").write_text(json.dumps({
        "trailingSlash": True,
        "rewrites": [{"source": "/", "has": [{"type": "host", "value": "nathanielgrivas.vercel.app"}], "destination": "/links/"}],
    }, indent=2))
    today = datetime.date.today().isoformat()
    sm = "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>" for u in pages)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    (DIST / "llms.txt").write_text(llms_txt(posts))
    (DIST / "index.md").write_text(home_md(posts))
    (DIST / "assets" / "search.json").write_text(json.dumps(search_index(posts), separators=(",", ":")))
    export_deploy(pages, today)
    print(f"built {len(pages)} pages, {len(posts)} posts, {len(HOODS)} neighborhoods")


TRAIL = re.compile(r'(="(?:https://www\.nathanielgrivas\.com)?/[^"?#\s]+)/(?=[?#"])')
TRAIL_JSON = re.compile(r'("https://www\.nathanielgrivas\.com/[^"?#\s]+)/(?=")')


def flat(text):
    return TRAIL_JSON.sub(r"\1", TRAIL.sub(r"\1", text))


def export_deploy(pages, today):
    """Vercel copy: /a/b/ pages become a/b.html with cleanUrls, so the repo needs one upload per folder."""
    out = ROOT / "deploy"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    shutil.copytree(DIST / "assets", out / "assets")
    shutil.copytree(DIST / "img", out / "img")
    for u, t in pages.items():
        f = out / ("index.html" if u == "/" else u.strip("/") + ".html")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(flat(ext_tabs(t)))
    (out / "404.html").write_text(flat((DIST / "404.html").read_text()))
    if (DIST / "links" / "index.html").exists():
        shutil.copy(DIST / "links" / "index.html", out / "links.html")
    (out / "vercel.json").write_text(json.dumps({
        "cleanUrls": True, "trailingSlash": False,
        "redirects": [{"source": "/", "has": [{"type": "host", "value": "nathanielgrivas.vercel.app"}], "destination": "/links", "permanent": False}],
    }, indent=2))
    sm = "".join(f"<url><loc>{SITE}{u.rstrip('/') if u != '/' else '/'}</loc><lastmod>{today}</lastmod></url>" for u in pages)
    (out / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    (out / "llms.txt").write_text(flat_txt((DIST / "llms.txt").read_text()))
    (out / "index.md").write_text(flat_txt((DIST / "index.md").read_text()))


def flat_txt(text):
    return re.sub(r"(https://www\.nathanielgrivas\.com/[^)\s]+)/\)", r"\1)", text)


def search_index(posts):
    out = []
    for h in ORDER:
        out.append({"t": h["name"], "s": f"{h['region']} \u00b7 {CITIES[h['city']]['short']} \u00b7 {h['zips']}", "u": f"/neighborhoods/{h['slug']}/",
                    "k": " ".join([h["zips"], h["region"], CITIES[h["city"]]["label"], " ".join(TAGS[t] for t in h["tags"]), " ".join(k for k, _ in h["know"])]), "g": "Neighborhoods", "i": "N"})
    for s_, t, d, _ in TOOLS:
        out.append({"t": t, "s": d, "u": f"/tools/{s_}/", "k": "calculator tool", "g": "Tools", "i": "T"})
    for p in posts:
        out.append({"t": p["title"], "s": p["category"], "u": f"/guide/{p['slug']}/", "k": p["description"], "g": "LA Guide", "i": "G"})
    for k in ACTIVE + SOLD:
        pr = PROPS[k]
        out.append({"t": pr["addr"], "s": f"{pr['tag']} \u00b7 {pr['price']} \u00b7 {pr['area']}", "u": pr["url"], "k": "listing home", "g": "Listings", "i": "L"})
    out += [{"t": "About Nathaniel", "s": "REALTOR\u00ae at Compass", "u": "/about/", "k": "agent bio", "g": "Pages", "i": "P"},
            {"t": "Contact", "s": "Call, text or send a message", "u": "/#contact", "k": "phone email", "g": "Pages", "i": "P"},
            {"t": "The Brodsky Group", "s": "My team at Compass Beverly Hills", "u": BG, "k": "team or brodsky", "g": "Pages", "i": "P"},
            {"t": "All listings", "s": "Active and closed", "u": "/listings/", "k": "homes for sale", "g": "Pages", "i": "P"}]
    return out


def home_md(posts):
    def line(k):
        p_ = PROPS[k]
        extra = f" Property website: {p_['site']}" if p_.get("site") else ""
        what = f"represented {p_['rep'].lower()}" if p_.get("sold") else p_["spec"]
        return f"- {p_['addr']}, {p_['area']}: {p_['tag']}, {p_['price']}{p_.get('per', '')}, {what}. Listing: {p_['url']}{extra}"
    out = [
        "# Nathaniel Grivas, West Los Angeles REALTOR®", "",
        f"Nathaniel Grivas is a REALTOR® (California DRE #{DRE}) with The Brodsky Group at Compass Beverly Hills, {ADDR}. "
        f"Compass is a licensed real estate broker, DRE #{CO_DRE}.", "",
        f"- Call or text: {PHONE}", f"- Email: {EMAIL}", f"- Website: {SITE}/",
        f"- Team: The Brodsky Group at Compass, over $100M in annual team sales ({BG})", "",
        "## Areas served", "", AREAS_LINE + " Neighborhoods: " + ", ".join(h["name"] for h in ORDER) + ".", "",
        "## How he helps", ""] + [f"- {t}: {d}" for _, t, d in HELP] + [
        "", "## Featured homes (with video tours)", ""] + [f"- [{FEATURED[k]['title']}, {FEATURED[k]['where']}]({SITE}{PROPS[k]['page']}): {FEATURED[k]['status']}, {FEATURED[k]['price']}. {FEATURED[k]['line']}" for k in ("evans", "fuller")] + [
        "", "## Listings", "", "Available:", ""] + [line(k) for k in ACTIVE] + ["", "Sold and leased:", ""] + [line(k) for k in SOLD] + [
        "", "## About", "",
        "Raised between New York and Seattle, Nathaniel studied Marketing and Business Law at Loyola Marymount University. "
        "He represents buyers, sellers, landlords and developers with The Brodsky Group at Compass Beverly Hills. "
        "His work covers pricing and listing prep, competitive offers, leasing, new construction, teardown and lot analysis, ADU feasibility and off-market deals.", "",
        "## Neighborhood guides", ""] + [f"- [{h['name']}]({SITE}/neighborhoods/{h['slug']}/): {h['line']}" for h in ORDER] + [
        "", "## Tools", ""] + [f"- [{t}]({SITE}/tools/{s_}/): {d}" for s_, t, d, _ in TOOLS] + [
        "", "## LA Guide", ""] + [f"- [{p['title']}]({SITE}/guide/{p['slug']}/): {p['description']}" for p in posts]
    return "\n".join(out) + "\n"


def llms_txt(posts):
    lines = ["# Nathaniel Grivas", "",
             f"> Nathaniel Grivas is a West Los Angeles REALTOR® (CA DRE #{DRE}) with The Brodsky Group at Compass, {ADDR}. "
             "He helps people buy, sell, rent, invest and build across West Los Angeles, Beverly Hills and the San Fernando Valley. "
             f"His team does over $100M in annual sales. Call or text {PHONE}, email {EMAIL}.", "",
             f"Full text version of the homepage, with listings and services: {SITE}/index.md", "",
             "## Listings"]
    for k in ACTIVE + SOLD:
        p_ = PROPS[k]
        lines.append(f"- [{p_['addr']}, {p_['area']}]({SITE + p_['page'] if p_.get('page') else p_.get('site') or p_['url']}): {p_['tag']}, {p_['price']}{p_.get('per', '')}" + (" (video tour on the page)" if p_.get("page") else ""))
    lines += ["", "## The LA Guide: where to eat, drink and go (by neighborhood)"]
    lines += [f"- [{BY_SLUG[k]['name']} guide]({SITE}/guide/{k}/): {len(d['places'])} restaurants, coffee shops, bars and things to do" for k, d in GUIDES.items() if k in BY_SLUG]
    if JOURNAL:
        lines += ["", "## The LA Journal: daily Los Angeles news and openings", f"- [All entries]({SITE}/journal/)"]
        lines += [f"- [{j['title']}]({SITE}/journal/{j['date']}/) ({j['date']}): {j['dek']}" for j in JOURNAL[:30]]
    lines += ["", "## The LA Guide: best of LA by category"]
    lines += [f"- [Best {G.CATS[k][1]} in LA]({SITE}/guide/best/{k}/)" for k in G.ORDERED if guide_counts().get(k)]
    lines += ["", "## Neighborhood guides"]
    lines += [f"- [{h['name']}]({SITE}/neighborhoods/{h['slug']}/): {h['line']}" for h in ORDER]
    lines += ["", "## Tools"] + [f"- [{t}]({SITE}/tools/{s}/): {d}" for s, t, d, _ in TOOLS]
    lines += ["", "## LA Guide"] + [f"- [{p['title']}]({SITE}/guide/{p['slug']}/): {p['description']}" for p in posts]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
