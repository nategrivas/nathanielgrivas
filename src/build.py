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
import v8  # noqa: E402
from v8 import aerial, reviews_band, trust_row, GBP_URL, stars  # noqa: E402
import guide_build as G  # noqa: E402
GUIDES = G.load()
import history as HI  # noqa: E402
HIST = HI.load()
import pockets as PKT
POCKETS = PKT.load()
import math  # noqa: E402
from urllib.parse import quote_plus  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SITE = "https://www.nathanielgrivas.com"
PHONE = "310-269-5541"
TEL = "+13102695541"
EMAIL = "nate.grivas@compass.com"
FORM_TO = EMAIL
# Ad tracking: paste the IDs here when the ad accounts exist (Google tag like "AW-123..." or "G-...", Meta pixel number)
GTAG_ID = ""
META_PIXEL = ""


def ad_tags():
    out = ""
    if GTAG_ID:
        out += (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GTAG_ID}"></script>'
                f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GTAG_ID}');</script>")
    if META_PIXEL:
        out += ("<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};"
                "if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];"
                f"s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','{META_PIXEL}');fbq('track','PageView');</script>")
    return out
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
    "https://www.google.com/search?kgmid=/g/11nr10vv1j",
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
                   img="lanark.jpg", url="https://www.compass.com/homedetails/18748-Lanark-St-Los-Angeles-CA-91335/2169982850442083505_lid/", page="/homes/18748-lanark/"),
    "hartland": dict(tag="Sold", price="$825K", addr="14757 Hartland St", area="Van Nuys", rep="Buyer", sold=True,
                     img="hartland.jpg", url="https://www.compass.com/homedetails/14757-Hartland-St-Van-Nuys-CA-91405/2115491441809620633_lid/", page="/homes/14757-hartland/"),
    "glenville": dict(tag="Leased", price="$3,400", per="/mo", addr="1127 Glenville Dr #2", area="Pico-Robertson", rep="Tenant & landlord", sold=True,
                      img="glenville.jpg", url="https://www.compass.com/homedetails/1127-Glenville-Dr-Unit-2-Los-Angeles-CA-90035/2190057374525691585_lid/"),
}
BG = "https://orbrodskygroup.com/"
ACTIVE = ["evans", "zelzah", "edgecliffe"]
SOLD = ["fuller", "lanark", "hartland", "glenville"]

CATEGORIES = ["Overrated vs. Underrated", "Eat & Drink", "Living in LA", "Renting in LA", "Courts & Outdoors",
              "Laws & Money", "Build & Develop", "Market Reports"]
CTAS = {
    "buy": ("Thinking about buying here?", "Share what you want and your budget. Nathaniel will send what fits, including homes that aren't on the market yet."),
    "sell": ("Curious what your home would sell for?", "Nathaniel pulls the real comps for your street and gives it to you straight, no listing pitch attached."),
    "rent": ("Looking for a place?", "Share your budget, area and move-in date. Nathaniel will send what's worth seeing and what to skip."),
    "build": ("Wondering what your lot can hold?", "Send the address. Nathaniel will check the zoning and show what you could build, ADU and lot split included."),
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
<meta name="theme-color" content="#f7f4ef">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<link rel="alternate" type="text/markdown" href="{md_url(path)}" title="Plain text version for AI and screen readers">
<meta name="ng-to" content="{FORM_TO}">
<link rel="icon" href="{rel(path)}assets/favicon.svg" type="image/svg+xml">
<script type="speculationrules">{{"prefetch":[{{"where":{{"and":[{{"href_matches":"/*"}},{{"not":{{"href_matches":"/*.md"}}}},{{"not":{{"href_matches":"/*.txt"}}}}]}},"eagerness":"moderate"}}]}}</script>
<link rel="preconnect" href="https://images.unsplash.com">
<link rel="preconnect" href="https://basemap.nationalmap.gov">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel(path)}assets/style.css">
{ad_tags()}{extra}
</head>
<body>"""


def rel(path):
    return "/"


def md_url(path):
    return "/index.md" if path == "/" else path.rstrip("/") + ".md"



def nav(path, active, over=False):
    items = [("Free Home Valuation", "/home-value/", "value"), ("Buy", "/buy/", "buy"), ("Lease", "/lease/", "rent"), ("Listings", "/listings/", "listings"), ("Local LA", "/neighborhoods/", "explore"),
             ("Market Temperature", "/market-temperature/", "market"), ("News", "/news/", "news"), ("About", "/about/", "about")]
    links = "".join(f'<a href="{h}"{" aria-current=page" if k == active else ""}>{n}</a>' for n, h, k in items)
    cls = "top over" if over else "top"
    return f"""<header class="{cls}"><div class="wrap">
<a class="brand" href="/" aria-label="Nathaniel Grivas home"><span class="wm">Nathaniel Grivas</span><span class="bk">Compass</span></a>
<nav class="nav" aria-label="Main">{links}</nav>
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
    strip = "" if (path in ("/", "/listings/", "/about/", "/buy/", "/lease/", "/home-value/") or path.startswith("/homes/") or path.startswith("/neighborhoods/") or path == "/tools/neighborhood-quiz/") else featured_strip()
    return f"""{strip}<footer class="foot"><div class="wrap">
<div class="foot-top">
<div class="me"><div class="name">Nathaniel Grivas</div>
<p>REALTOR&reg; with <a href="{BG}" rel="noopener">The Brodsky Group</a> at Compass<br>{ADDR}<br>
<a href="tel:{TEL}">{PHONE}</a> &nbsp; <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<a class="foot-g" href="{GBP_URL}" rel="noopener">Read the Google reviews</a>
<p class="soc"><a href="{BG}" rel="noopener">The Brodsky Group</a> <a href="{SAME_AS[0]}">Compass</a> <a href="{SAME_AS[2]}">Instagram</a> <a href="{SAME_AS[1]}">LinkedIn</a> <a href="{SAME_AS[3]}">Zillow</a> <a href="{SAME_AS[4]}">Realtor.com</a></p></div>
<div><h4>Local LA</h4><ul><li><a href="/neighborhoods/">The map</a></li>{regions}</ul></div>
<div><h4>Tools</h4><ul>{tools}</ul></div>
<div><h4>More</h4><ul><li><a href="/lease/">Lease</a></li><li><a href="/neighborhoods/">Local LA</a></li><li><a href="/market-temperature/">Market Temperature</a></li><li><a href="/news/">LA News</a></li><li><a href="/listings/">Listings</a></li><li><a href="/about/">About</a></li><li><a href="/#contact" data-msg>Contact</a></li><li><a href="/privacy/">Privacy</a></li><li><a class="ext" href="{BG}" rel="noopener">The Brodsky Group</a></li></ul></div>
</div>
<details><summary>All neighborhoods</summary><div class="foot-hoods">{cols}</div></details>
<div class="legal">Nathaniel Grivas, REALTOR&reg;, DRE #{DRE}. Compass is a licensed real estate broker, DRE #{CO_DRE}. Equal Housing Opportunity.
Neighborhood and rules information is general, simplified and subject to change; confirm details for a specific property with the city, county or a professional. Calculators give estimates, not tax or legal advice. Listing information is shown for marketing purposes and may have changed since posting. Neighborhood photos via <a href="https://unsplash.com/" rel="noopener">Unsplash</a>. &copy; {year} Nathaniel Grivas.</div>
</div></footer>
<nav class="dock" aria-label="Quick">
<a href="/home-value/"{cur("value")}>{ICONS['value']}Free Valuation</a>
<a href="/buy/"{cur("buy")}>{ICONS['home']}Buy</a>
<a href="/neighborhoods/"{cur("explore")}>{ICONS['pin']}Areas</a>
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
<h2 id="ngd-msg-t">How can Nathaniel help?</h2>
<div class="ngd-paths"><a href="/home-value/"><b>What's my home worth?</b><span>Free valuation from the sales on your street</span></a><a href="/buy/"><b>Find me a home</b><span>New, coming-soon and off-market homes</span></a><a href="/lease/"><b>Lease a home, or lease yours out</b><span>Lease search or a free lease estimate</span></a></div>
<p class="ngd-note">Something else? Send Nathaniel a note, or call or text <a href="tel:{TEL}">{PHONE}</a>.</p>
{lead_form("/", title="Message from website", need_first=True, btn="Send message", show_pills=False)}
</div></dialog>
<script src="/assets/track.js" defer></script><script src="/assets/site.js" defer></script><script src="/assets/lead.js" defer></script>{extra}
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
        poster="/img/evans/p01.jpg", loop="/img/evans/loop.mp4", loop_poster="/img/evans/loop-800.jpg",
        film="https://3721evans.com/media/film.mp4", film_len="1:22",
        site="https://3721evans.com/", compass="https://www.compass.com/homedetails/3721-Evans-St-W-Los-Angeles-CA-90027/1K38M8_pid/",
        credit="Listed by The Brodsky Group at Compass"),
    "fuller": dict(
        title="616 N Fuller Ave", where="Fairfax District, Los Angeles, CA 90036", status="Sold", price="$3,275,000",
        stats=[("7", "Bedrooms"), ("8", "Bathrooms"), ("5,257", "Sq ft"), ("7,334", "Sq ft lot"), ("2016", "Built")],
        line="A three-level modern home with a pool in the Fairfax District. Nathaniel sold it with seller financing, representing both the sellers and the buyer.",
        body=["The sellers carried the loan, so the buyer closed without a bank. Nathaniel built the structure, protected the sellers and closed it in October 2026. Complicated is fine."],
        poster="/img/fuller.jpg", vimeo="1180538967", film_len="1:00",
        compass="https://www.compass.com/homedetails/616-N-Fuller-Ave-Los-Angeles-CA-90036/2072900371372293281_lid/",
        credit="Sold by Nathaniel Grivas of The Brodsky Group at Compass"),
}


def film_evans(big=False):
    f = FEATURED["evans"]
    # A short local loop plays on its own; the full film (with sound) loads only when someone asks for sound.
    return (f'<div class="film film-wide" data-film data-full="{f["film"]}">'
            f'<video data-src="{f["loop"]}" poster="{f["loop_poster"]}" muted loop playsinline autoplay preload="none" aria-label="Video tour of 3721 Evans St W"></video>'
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


def hood_card(h, r, extra_cls="", eager=False):
    c = CITIES[h["city"]]
    chips = f'<span>{e(c["short"])}</span><span title="{TIER_WORD[h["tier"]]}">{TIER[h["tier"]]}</span>'
    ph = PHOTOS.get(h["slug"])
    media = (ph_img(ph[0][0], ph[0][1], 520, 0.56, "(max-width:700px) 92vw, 300px", cls="hc-img", eager=eager) if ph
             else aerial(*h["ll"], z=15, cols=3, rows=3, ts=180, cls="hc-aer"))
    return f"""<a class="hcard{extra_cls}" href="{r}neighborhoods/{h['slug']}/" data-slug="{h['slug']}" data-region="{slug(h['region'])}" data-tags="{' '.join(h['tags'])}" data-name="{e(h['name'].lower())}" data-zips="{h['zips']}">
<div class="hc-media">{media}</div>
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


def lead_form(r, preset="", msg="", title="", need_first=False, btn="Send to Nathaniel", show_pills=True):
    opts = ["Buy", "Sell", "Rent", "Invest", "Build"]
    pills = "".join(
        f'<label><input type="checkbox" name="looking" value="{o}"{" checked" if o.lower() == preset else ""}> {o}</label>'
        for o in opts)
    who = """<div class="f"><label>Name<input name="name" autocomplete="name" required></label></div>
<div class="f"><label>Phone<input name="phone" type="tel" autocomplete="tel"></label></div>
<div class="f full"><label>Email<input name="email" type="email" autocomplete="email" required></label></div>"""
    need = (f"""<div class="f full"><span class="lbl">I'm looking to</span><div class="pills">{pills}</div></div>""" if show_pills else "") + f"""
<div class="f full"><label>{"Your message" if need_first else "Anything Nathaniel should know?"}<textarea name="message" placeholder="{"What you're looking to buy, sell or rent, the area, timing, an address" if need_first else "Area, budget, timing, an address you're curious about"}">{e(msg)}</textarea></label></div>"""
    body = need + "\n" + who if need_first else who + "\n" + need
    return f"""<form class="lead" data-to="{FORM_TO}" data-subject="{e(title or 'New website lead')}" novalidate>
{body}
<div class="f full"><button class="btn solid" type="submit">{e(btn)}</button></div>
<p class="formmsg" role="status" aria-live="polite"></p>
<p class="formnote">Goes straight to Nathaniel. He replies within a day, usually sooner. By sending, you agree Nathaniel can contact you by call, text or email about real estate. Reply STOP to opt out of texts. <a href="/privacy/">Privacy</a></p>
</form>"""


INTAKE = "/tools/neighborhood-quiz/"


def intake_url(goal="", area=""):
    q = []
    if goal:
        q.append(f"goal={goal}")
    if area:
        q.append(f"area={area}")
    return INTAKE + ("?" + "&amp;".join(q) if q else "")


def contact_band(r, heading="Tell Nathaniel what you're after", sub="Buying, selling, renting, investing or building. Start here.", preset="", msg="", title="", form=False, area=""):
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
<a href="{BG}" rel="noopener">{q['team']}<div><b class="ext">The Brodsky Group</b><span>His team at Compass Beverly Hills</span></div></a>
</div></div>
{lead_form(r, preset, msg, title)}
</div></section>"""


def team_band(img, title, line):
    return team_section(img)


def team_section(img="team.jpg", bio=None):
    bio = bio or ("Nathaniel represents buyers, sellers, landlords and developers with The Brodsky Group at Compass Beverly Hills. "
                  "Pricing, competitive offers, leasing, new construction, teardown and lot analysis, ADU feasibility and off-market sourcing.")
    return f"""<section class="band"><div class="wrap teamwrap">
<figure class="teamband"><img src="/img/{img}" alt="The Brodsky Group team at Compass" width="2000" height="1333" loading="lazy">
<figcaption>The Brodsky Group &middot; Compass Beverly Hills</figcaption></figure>
<div class="mecard glass">
<div class="who"><img src="/img/nate.jpg" alt="Nathaniel Grivas" width="84" height="84" loading="lazy"><div><h2>Nathaniel Grivas</h2><span>REALTOR&reg; &middot; DRE #{DRE}</span></div></div>
<p>{e(bio)}</p>
<div class="cta-row" style="margin-top:0"><a class="btn solid" href="/#contact">Work with Nathaniel</a><a class="btn ext" href="{BG}" rel="noopener">The Brodsky Group</a><a class="btn" href="/about/">About Nathaniel</a></div>
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
        media = aerial(*h["ll"], z=15, cols=3, rows=3, ts=230)
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
def agent_facts():
    def deal(k):
        p_ = PROPS[k]
        return f"{p_['addr']}, {p_['area']} ({p_['tag'].lower()}, {p_['price']}{p_.get('per', '')}; represented the {p_['rep'].lower()})"
    def lst(k):
        p_ = PROPS[k]
        return f"{p_['addr']}, {p_['area']} ({p_['tag'].lower()}, {p_['price']}{p_.get('per', '')})"
    return [
        ("Name", "Nathaniel Grivas"),
        ("Role", "REALTOR®, residential real estate agent"),
        ("License", f"California DRE #{DRE}"),
        ("Brokerage", f"Compass, Beverly Hills office, {ADDR} (Compass DRE #{CO_DRE})"),
        ("Team", "The Brodsky Group at Compass, led by Or Brodsky, with over $100M in annual team sales"),
        ("Reviews", "5.0 stars on Google (2 reviews)"),
        ("Areas served", "West Los Angeles, Beverly Hills, the Hollywood Hills, Central LA, the Eastside and the San Fernando Valley: " + ", ".join(h["name"] for h in ORDER)),
        ("Services", "Buying, selling, leasing, investing and building: pricing and listing prep, competitive offers, leasing, new construction, teardown and lot analysis, ADU feasibility and off-market deals"),
        ("Closed deals", "; ".join(deal(k) for k in SOLD)),
        ("Resources for clients", "Off-market and coming-soon homes through Compass Private Exclusives and his team's off-market list; lenders for self-employed (bank-statement), investor (DSCR) and non-traditional buyers; creative structures including seller financing, leasebacks, assignments and 1031 exchanges; plus inspectors, contractors, architects, escrow, title and tax pros"),
        ("Creative financing example", "Sold 616 N Fuller Ave, Fairfax District, for $3,275,000 with seller financing (the sellers carried the loan), representing both sides"),
        ("Free home valuation", f"{SITE}{VALUE_URL}"),
        ("Find a home (buyer search)", f"{SITE}{BUY_URL}"),
        ("Current listings", "; ".join(lst(k) for k in ACTIVE)),
        ("Education", "Loyola Marymount University, Marketing and Business Law"),
        ("Contact", f"Call or text {PHONE}, email {EMAIL}"),
    ]


def facts_band():
    rows = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in agent_facts())
    return f"""<section class="band facts-band" id="facts"><div class="wrap">
<div class="sec-head"><div><p class="kick">Quick facts</p><h2>Nathaniel Grivas at a glance</h2></div></div>
<dl class="qfacts">{rows}</dl></div></section>"""


def person_ld():
    return {
        "@context": "https://schema.org", "@type": "RealEstateAgent", "@id": SITE + "/#nathaniel", "name": "Nathaniel Grivas",
        "alternateName": "Nate Grivas", "jobTitle": "REALTOR",
        "description": "West Los Angeles REALTOR with The Brodsky Group at Compass Beverly Hills. " + AREAS_LINE,
        "url": SITE + "/", "image": SITE + "/img/nate-hero.jpg", "telephone": "+1-310-269-5541", "email": EMAIL,
        "address": {"@type": "PostalAddress", "streetAddress": "9454 Wilshire Blvd, Ste 100",
                    "addressLocality": "Beverly Hills", "addressRegion": "CA", "postalCode": "90212", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 34.0675, "longitude": -118.3995},
        "openingHours": "Mo-Su 00:00-23:59",
        "areaServed": [{"@type": "Place", "name": f"{h['name']}, Los Angeles, CA", "url": f"{SITE}/neighborhoods/{h['slug']}/",
                        "geo": {"@type": "GeoCoordinates", "latitude": h["ll"][0], "longitude": h["ll"][1]}} for h in ORDER],
        "parentOrganization": {"@type": "RealEstateAgent", "name": "Compass", "url": "https://www.compass.com/"},
        "memberOf": {"@type": "Organization", "name": "The Brodsky Group at Compass", "url": BG,
                     "description": "Compass Beverly Hills team with over $100M in annual sales"},
        "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": t, "description": d}} for _, t, d in HELP],
        "knowsAbout": ["Luxury residential real estate", "Development and teardown analysis", "ADU feasibility",
                       "Off-market sourcing", "Leasing", "Measure ULA", "Los Angeles neighborhoods", "Seller financing"],
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "Loyola Marymount University"},
        "identifier": {"@type": "PropertyValue", "name": "California DRE license", "value": DRE},
        "hasCredential": {"@type": "EducationalOccupationalCredential", "credentialCategory": "license",
                          "name": "California real estate salesperson license", "identifier": DRE,
                          "recognizedBy": {"@type": "GovernmentOrganization", "name": "California Department of Real Estate"}},
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
    ("sell", "What's my home worth?", "A free valuation built by hand from the sales on your street."),
    ("buy", "Find me a home", "New, coming-soon and off-market homes, as they come up."),
    ("rent", "Lease a home", "Homes for lease, or lease yours out."),
    ("invest", "Invest", "Income property and off-market deals."),
    ("build", "Build", "Lots, teardowns and ADUs."),
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
    tiles += (f'<a class="tile maptile allmap" href="/neighborhoods/">{aerial(34.06, -118.39, z=12, cols=3, rows=3, ts=260)}'
              f'<div class="tile-txt"><span class="tile-k">The map</span><h3>Every neighborhood</h3></div></a>')
    helps = "".join(f'<a href="{VALUE_URL if g == "sell" else BUY_URL if g == "buy" else RENT_URL if g == "rent" else intake_url(g)}"><b>{e(t)}</b><span>{e(d)}</span><i aria-hidden="true">&rarr;</i></a>' for g, t, d in HELP)
    body = f"""{nav(path, "home")}
<main>
<section class="face-hero" aria-label="Nathaniel Grivas, West Los Angeles REALTOR">
<figure class="fh-me"><img src="/img/nate-hero-800.jpg" srcset="/img/nate-hero-800.jpg 800w, /img/nate-hero.jpg 1200w" sizes="(max-width:860px) 100vw, 42vw" alt="Nathaniel Grivas, REALTOR&reg; at Compass Beverly Hills" width="1200" height="1500" fetchpriority="high"></figure>
<div class="fh-copy">
<p class="kick">The Brodsky Group at Compass Beverly Hills</p>
<h1><span class="lh-name">Nathaniel Grivas</span><span class="lh-sub">West Los Angeles REALTOR&reg;</span></h1>
<p class="fh-lede">Early access to the homes that sell quietly. A straight answer on what yours is worth.</p>
<form class="fh-addr" action="/home-value/" method="get" role="search" aria-label="Get your home value"><label class="sr" for="fh-a">Your home address</label><input id="fh-a" name="addr" autocomplete="street-address" placeholder="Enter your address" required><button class="btn lux solid" type="submit">What's it worth?</button></form>
<div class="lh-cta fh-alt"><a class="btn lux" href="/buy/">Find me a home</a><a class="btn lux" href="tel:{TEL}">Call {PHONE}</a></div>
{trust_row("fh-trust")}
<figure class="fh-team"><img src="/img/team-1200.jpg" srcset="/img/team-800.jpg 800w, /img/team-1200.jpg 1200w, /img/team.jpg 2000w" sizes="(max-width:860px) 92vw, 46vw" alt="The Brodsky Group team at Compass Beverly Hills" width="1200" height="800" loading="lazy" decoding="async">
<figcaption><span><b>The Brodsky Group</b> &middot; Compass Beverly Hills</span><a href="/about/">Meet the team &rarr;</a></figcaption></figure>
</div>
</section>

{featured_section()}

{reviews_band(True, "What clients say", "rv-home")}

<section class="help" id="help"><div class="wrap">
<div class="lux-head"><p class="kick">Work with Nathaniel</p><h2>How he can help</h2></div>
<div class="help-row">{helps}</div>
</div></section>

{proof_band("Recent results", "Track record")}
<section class="band lux-band" id="areas"><div class="wrap">
<div class="lux-head"><p class="kick">Local LA</p><h2>Neighborhoods</h2><a href="/neighborhoods/">Open the map &rarr;</a></div>
<div class="bento">{tiles}</div>
</div></section>

{market_teaser()}
{lead_band("Let's talk", "You'll hear back today.")}
</main>
{foot(path, [])}"""
    desc = ("Nathaniel Grivas, West Los Angeles REALTOR® with The Brodsky Group at Compass Beverly Hills. Buy, sell, rent, invest or build across West LA, "
            "Beverly Hills and the Valley.")
    extra = ld(person_ld()) + ld(listings_ld())
    return head("Nathaniel Grivas | West Los Angeles REALTOR® | The Brodsky Group at Compass", desc, path, extra, og="nate-hero.jpg") + body


def page_explore():
    path = "/neighborhoods/"
    r = "/"
    regs = "".join(f'<button type="button" data-region="{slug(x)}" aria-pressed="false">{e(x)}</button>' for x in REGIONS)
    tags = "".join(f'<button type="button" data-tag="{k}" aria-pressed="false">{e(v)}</button>' for k, v in TAGS.items())
    cards = "".join(hood_card(h, r, eager=k < 2) for k, h in enumerate(ORDER))
    pts = [{"slug": h["slug"], "name": h["name"], "lat": h["ll"][0], "lng": h["ll"][1], "line": h["line"], "url": f"/neighborhoods/{h['slug']}/",
            "region": slug(h["region"]), "tags": " ".join(h["tags"]), "zips": h["zips"],
            "img": photos.url(PHOTOS[h["slug"]][0][0], 480, 300) if PHOTOS.get(h["slug"]) else ""} for h in ORDER]
    body = f"""{nav(path, "explore")}
<main class="wrap xp">
<div class="xp-map">
<div class="satmap" id="satmap" role="region" aria-label="Satellite map of Los Angeles neighborhoods"></div>
<script type="application/json" id="satmap-data">{json.dumps(pts)}</script>
<div class="agentbar"><img src="/img/nate.jpg" alt="" width="42" height="42"><div><b>Not sure where to start?</b><span>Take the <a href="/tools/neighborhood-quiz/">6-question quiz</a> or ask Nathaniel directly.</span></div>
<a class="btn small" href="sms:{TEL}">Text</a><a class="btn solid small" href="tel:{TEL}">Call</a></div>
</div>
<div class="xp-side">
<p class="kick">Local LA</p>
<h1>40 neighborhoods and the places locals actually go</h1>
<p class="xp-lede">Tap any neighborhood for its map of hand-picked restaurants, bars and things to do, plus the homes, the rules and who it fits.</p>
<a class="pk-cta" href="/neighborhoods/map/"><b>New: the LA pocket map</b><span>Every micro-neighborhood, from the Bird Streets to North of Montana, drawn street by street &rarr;</span></a>
<label class="search">{ICONS['search']}<input id="q" type="search" placeholder="Search a neighborhood or ZIP" autocomplete="off"></label>
<div class="chiprow" id="regions" role="group" aria-label="Region"><button type="button" data-region="" aria-pressed="true">All</button>{regs}</div>
<div class="chiprow" id="tags" role="group" aria-label="What you want">{tags}</div>
<p class="count" id="count" aria-live="polite"></p>
<div class="hgrid" id="hgrid">{cards}</div>
<p class="empty" id="empty" hidden>No neighborhood matches all of those. Remove a filter or two.</p>
</div>
</main>
{local_extras(r)}
<section class="band" style="padding-top:10px"><div class="wrap"><div class="tools">{tool_card("neighborhood-quiz", r)}{tool_card("compare", r)}{tool_card("la-rules", r)}</div></div></section>
{reviews_band(False, "What clients say")}
{lead_band("Not sure where to start?", "Tell Nathaniel what you want. He'll narrow it down.", first="buy")}
{foot(path, ["vendor/leaflet.js", "satmap.js"], "explore")}"""
    desc = "Local LA: 40 Los Angeles neighborhoods on a satellite map, each with hand-picked restaurants, bars and things to do, from Santa Monica and Beverly Hills to Los Feliz and the Valley."
    ld_ = crumbs_ld([("Home", "/"), ("Local LA", path)])
    extra = ld(ld_) + '\n<link rel="stylesheet" href="/assets/vendor/leaflet.css">\n<link rel="preload" as="script" href="/assets/vendor/leaflet.js">\n<link rel="preload" as="script" href="/assets/satmap.js">'
    return head("Local LA: Best Restaurants, Bars & Things to Do in 40 LA Neighborhoods | Nathaniel Grivas", desc, path, extra) + body


def local_extras(r):
    cnt = guide_counts()
    cats = ""
    for g, glabel, items in G.GROUPS:
        links = "".join(f'<a href="/guide/best/{k}/">{e(label)} <i>{cnt[k]}</i></a>' for k, label, _ in items if cnt.get(k, 0) >= 3)
        if links:
            cats += f'<div class="gcatg"><p class="kick">{e(glabel)}</p><div class="gcats">{links}</div></div>'
    posts = load_posts()
    return f"""{journal_teaser()}
<section class="band lux-band" id="best"><div class="wrap">
<div class="lux-head"><p class="kick">Across LA</p><h2>The best of LA, by category</h2></div>{cats}
</div></section>
<section class="band lux-band" id="articles"><div class="wrap">
<div class="lux-head"><p class="kick">Articles</p><h2>Living in LA</h2></div>
<div class="posts">{"".join(post_card(p, r) for p in posts)}</div>
</div></section>"""


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



# ------------------------------------------------------------------ Local LA: the guide and the place map on every neighborhood page
def pslug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:40]


def hood_sections(slug_):
    """Group a neighborhood's places into broad sections with 3+ picks each, topping thin ones up from next door."""
    d = GUIDES.get(slug_)
    h = BY_SLUG[slug_]
    own = d["places"] if d else []
    secs = {k: [(p, d, None) for p in own if G.sec_of(p) == k] for k in G.SEC_ORDER}
    names = {p["n"] for p in own}
    small_hood = len(own) < 25
    for k in G.SEC_ORDER:
        have = len(secs[k])
        if have >= 3 or (have == 0 and not (small_hood and k in ("morning", "dinner", "night"))):
            continue
        cands = []
        for o, od in GUIDES.items():
            if o == slug_ or o not in BY_SLUG:
                continue
            for q in od["places"]:
                if G.sec_of(q) != k or q["n"] in names:
                    continue
                dist = miles(h["ll"], tuple(q["ll"]) if q.get("ll") else BY_SLUG[o]["ll"])
                if dist <= 2.5:
                    cands.append((dist, q, od, o))
        # closest first, with a nudge toward the upscale rooms (the crowd this site is for)
        cands.sort(key=lambda x: x[0] - (0.6 if x[1].get("p") in ("$$$", "$$$$") else 0))
        for dist, q, od, o in cands[:3 - have]:
            secs[k].append((q, od, (o, dist)))
            names.add(q["n"])
    groups = [{"keys": {k}, "items": secs[k]} for k in G.SEC_ORDER if secs[k]]
    while len(groups) > 1:
        small = [g for g in groups if len(g["items"]) < 3]
        if not small:
            break
        g = min(small, key=lambda x: len(x["items"]))
        tgt = None
        for k in sorted(g["keys"], key=G.SEC_ORDER.index):
            tgt = next((x for x in groups if G.MERGE_TO[k] in x["keys"] and x is not g), None)
            if tgt:
                break
        if not tgt:
            i = groups.index(g)
            tgt = groups[i - 1] if i > 0 else groups[i + 1]
        tgt["keys"] |= g["keys"]
        tgt["items"] += g["items"]
        groups.remove(g)
    for g in groups:
        g["items"].sort(key=lambda it: (G.SEC_ORDER.index(G.sec_of(it[0])), 1 if it[2] else 0))
        g["label"] = G.combo_label(g["keys"])
        g["group"] = G.combo_group(g["keys"])
        g["id"] = "go-" + min(g["keys"], key=G.SEC_ORDER.index)
    groups.sort(key=lambda g: min(G.SEC_ORDER.index(k) for k in g["keys"]))
    return groups


def guide_card(p, d, home, near, idx):
    hn = BY_SLUG[d["slug"]]["name"]
    src = "".join(f'<a href="{d["sources"][k][1]}" rel="noopener">{e(d["sources"][k][0].split(":")[0])}</a>' for k in p.get("s", []) if k in d["sources"])
    if near:
        o, dist = near
        where = f'<span class="pc-near">Next door in <a href="/neighborhoods/{o}/">{e(hn)}</a> &middot; {dist:.1f} mi</span> &middot; {e(p.get("a") or "")}'
    else:
        where = e(p.get("a") or "")
    tip = f'<p class="pc-o"><b>{"Do" if G.CATS[p["c"][0]][2] == "do" else "Order"}:</b> {e(p["o"])}</p>' if p.get("o") else ""
    chips = "".join(f'<span>{e(G.CATS[c][0])}</span>' for c in p["c"][:3])
    pin = f'<button type="button" class="pc-pin" data-pin="{idx}">{ICONS["pin"]}On the map</button>' if p.get("ll") else ""
    return (f'<article class="pc" id="pl-{idx}"><div class="pc-h"><h3>{e(p["n"])}</h3><span class="pc-p">{e(p.get("p", ""))}</span></div>'
            f'<p class="pc-a">{where}</p><p class="pc-w">{e(p["w"])}</p>{tip}'
            f'<div class="pc-f">{pin}<a class="pc-map" href="{G.maps_url(p, hn)}" rel="noopener">Directions &#8599;</a>{("<span class=pc-s>Sources: " + src + "</span>") if src else ""}</div>'
            f'<div class="pc-c">{chips}</div></article>')


def first_sentence(t):
    m = re.match(r"(.+?[.!?])(\s|$)", t or "")
    return (m.group(1) if m else (t or ""))[:180]


def hood_local(h):
    """Returns (map section html, guide section html, map data) for a neighborhood page."""
    slug_, n = h["slug"], h["name"]
    groups = hood_sections(slug_)
    d = GUIDES.get(slug_)
    pts, blocks, chips, idx = [], "", "", 0
    for gi, g in enumerate(groups):
        cards = ""
        for p, pd, near in g["items"]:
            if p.get("ll"):
                pts.append({"i": idx, "n": p["n"], "lat": p["ll"][0], "lng": p["ll"][1], "g": G.SEC[G.sec_of(p)][1], "s": g["id"], "sl": g["label"],
                            "p": p.get("p", ""), "a": p.get("a") or "", "w": first_sentence(p["w"]), "u": G.maps_url(p, BY_SLUG[pd["slug"]]["name"]),
                            "near": BY_SLUG[near[0]]["name"] if near else ""})
            cards += guide_card(p, pd, slug_, near, idx)
            idx += 1
        chips += f'<a href="#{g["id"]}">{e(g["label"])} <i>{len(g["items"])}</i></a>'
        blocks += f'<section class="gsec" id="{g["id"]}"><p class="kick">{e(g["group"])}</p><h3 class="gsec-h">{e(g["label"])}</h3><div class="pcs">{cards}</div></section>'
        if gi == 1:
            blocks += cta_strip(f"Love {n}? Live here.", "New listings here, including off-market ones, or a free value on yours.", buy_label=f"Get {n} listings")
    total = idx
    borrowed = sum(1 for g in groups for it in g["items"] if it[2])
    nearby = total and borrowed * 2 > total
    srcs = "".join(f'<li><a href="{u}" rel="noopener">{e(t)}</a></li>' for t, u in (d["sources"].values() if d else []))
    upd = d["updated"] if d else ""
    gkick, gh = ("Down the hill", f"Where to eat, drink and go near {e(n)}") if nearby else ("Local LA", f"Where to eat, drink and go in {e(n)}")
    guide_html = f"""<section class="band nb-guide" id="eat"><div class="wrap">
<div class="sec-head"><div><p class="kick">{gkick}</p><h2>{gh}</h2></div>{f'<a href="{v8.gmaps_link(h)}" rel="noopener">Open in Google Maps &#8599;</a>' if len(pts) >= 3 else ''}</div>
<p class="nb-glede">{e(d["intro"]) if d else ""}</p>
<p class="gh-meta">{total} hand-picked places &middot; Updated {e(upd)}</p>
{{MAPSLOT}}
<nav class="gchips" aria-label="Sections">{chips}</nav>
<div class="gbody">{blocks}</div>
{f'<details class="gsrc"><summary>Sources</summary><ul>{srcs}</ul></details>' if srcs else ''}
</div></section>"""
    secs_meta = [[g["id"], g["label"], sum(1 for p in pts if p["s"] == g["id"])] for g in groups]
    data = {"c": list(h["ll"]), "name": n, "pts": pts, "secs": [s for s in secs_meta if s[2]]}
    allnames = [p["n"] for g in groups for p, _, _ in g["items"]]
    spots = "".join(f'<li><span class="n">{k + 1}</span><span><b>{e(t)}</b><span>{e(dd)}</span></span></li>' for k, (t, dd) in enumerate(h["know"]))
    bar = '<button type="button" data-hm="" aria-pressed="true">All <i>' + str(len(pts)) + '</i></button>' + "".join(
        f'<button type="button" data-hm="{k}" aria-pressed="false">{e(lab)} <i>{c}</i></button>' for k, lab, c in data["secs"])
    if len(pts) < 3:
        # no coordinates yet: keep the satellite view until the places are geocoded
        map_html = f"""<section class="band nb-map" id="map"><div class="wrap">
<div class="sec-head"><div><p class="kick">From above</p><h2>{e(n)} by satellite</h2></div><a href="{v8.gmaps_link(h)}" rel="noopener">Open in Google Maps &#8599;</a></div>
<div class="nb-mapgrid">
{v8.sat_map(h)}
<div class="nb-spots"><h3>Spots to know</h3><ol>{spots}</ol></div>
</div></div></section>"""
        return map_html, guide_html.replace("{MAPSLOT}", ""), dict(data, all=allnames)
    inner = f"""<div class="nb-map nb-map-in" id="map">
<div class="hm-bar" role="group" aria-label="Show on the map">{bar}</div>
<div class="nb-mapgrid">
<div class="hoodmap" id="hoodmap" role="region" aria-label="Map of places to eat, drink and go in {e(n)}"></div>
<div class="nb-spots"><h3>Spots to know</h3><ol>{spots}</ol></div>
</div>
<script type="application/json" id="hoodmap-data">{json.dumps(data, separators=(",", ":")).replace("</", "<\\/")}</script>
</div>"""
    guide_html = guide_html.replace("{MAPSLOT}", inner)
    map_html = ""
    return map_html, guide_html, dict(data, all=allnames)




def pocket_items(area, full=True):
    h = BY_SLUG.get(area)
    an = h["name"] if h else area
    return [dict(i=p["i"], n=p["n"], e=p["e"], an=an, a=area, u=f"/neighborhoods/{area}/", **({"d": p["d"], "b": p["b"]} if full else {})) for p in POCKETS.get(area, [])]


def pockets_section(h):
    """Map + cards for the pockets inside one area. Returns ("", []) when the area has none yet."""
    pk = pocket_items(h["slug"])
    if not pk:
        return "", []
    n = h["name"]
    ctx = [x for s_ in h["near"] for x in pocket_items(s_, False)]
    cards = "".join(
        f'<article class="pk-card" id="pk-{p["i"]}" data-pk="{p["i"]}"><h3>{e(p["n"])}</h3>'
        + (f'<p class="pk-b">{e(p["b"])}</p>' if p["b"] else "")
        + (f'<p>{e(p["d"])}</p>' if p["d"] else "")
        + '<button type="button" class="pk-show" data-pkshow>Show on the map</button></article>' for p in pk)
    data = {"pk": pk, "ctx": ctx}
    html = f"""<section class="band pk" id="pockets"><div class="wrap">
<div class="sec-head"><div><p class="kick">Block by block</p><h2>The pockets of {e(n)}</h2></div><a href="/neighborhoods/map/">Every LA pocket on one map &rarr;</a></div>
<p class="pk-sub">One street can change the price. {e(n)} is {len(pk)} pockets, drawn street by street. Dashed lines are the pockets next door.</p>
<div class="pk-grid">
<div class="pkmap" id="pkmap" role="region" aria-label="Map of the pockets of {e(n)}"></div>
<div class="pk-list">{cards}</div>
</div>
<script type="application/json" id="pkmap-data">{json.dumps(data, separators=(",", ":")).replace("</", "<\\/")}</script>
</div></section>"""
    return html, pk


def areas_json():
    reg = {"Coast": "Coast", "Westside": "Westside", "Beverly Hills & the Hills": "Beverly Hills & the Hills", "Central": "Central", "Eastside": "Eastside", "Valley": "Valley"}
    groups, zips = {}, {}
    for h in ORDER:
        r = h.get("region", "")
        groups.setdefault(r, []).append([h["slug"], h["name"], h.get("zips", "")])
        for z in [z.strip() for z in h.get("zips", "").split(",") if z.strip()]:
            zips.setdefault(z, h["name"])
    order = ["Westside", "Beverly Hills & the Hills", "Coast", "Central", "Eastside", "Valley"]
    g = [{"r": r, "h": groups[r]} for r in order if r in groups] + [{"r": r, "h": v} for r, v in groups.items() if r not in order]
    names = {h["slug"]: h["name"] for h in ORDER}
    p = []
    for slug, lst in POCKETS.items():
        for x in lst:
            p.append([x["n"], names.get(slug, slug)])
    return {"g": g, "p": p, "z": zips}


def pockets_json():
    allp = []
    for h in ORDER:
        allp += pocket_items(h["slug"])
    return {"all": True, "pk": allp}


def page_pocketmap():
    path = "/neighborhoods/map/"
    allp = pockets_json()["pk"]
    areas = sorted({p["an"] for p in allp})
    lis = "".join(f'<li><a href="/neighborhoods/{h["slug"]}/#pockets">{e(h["name"])}</a> <span>{", ".join(e(p["n"]) for p in POCKETS.get(h["slug"], []))}</span></li>' for h in ORDER if POCKETS.get(h["slug"]))
    body = f"""{nav(path, "explore")}
<main class="pkx">
<div class="pkx-map"><div class="pkmap pkmap-full" id="pkmap" role="region" aria-label="Map of every pocket in Local LA"></div>
<div class="pkx-panel"><p class="kick">Local LA</p><h1>The LA pocket map</h1>
<p>LA is a city of pockets. Prices, lots and the feel of a street can change the second you cross one road. Here are {len(allp)} pockets across {len(areas)} neighborhoods, each one drawn on the actual streets that bound it.</p>
<label class="search">{ICONS['search']}<input id="pk-q" type="search" placeholder="Find a pocket, like Bird Streets" autocomplete="off"></label>
<div class="pk-res" id="pk-res"></div>
<p class="pkx-note">Tap any shape for what it is and where it starts and stops. Boundaries are Nathaniel's own research from the street grid and sold history, so treat them as a guide, not a survey.</p>
<a class="btn solid small" href="tel:{TEL}">{ICONS['call']}Ask Nathaniel about a street</a></div></div>
<section class="band"><div class="wrap"><h2>Every pocket, by neighborhood</h2><ul class="pkx-list">{lis}</ul></div></section>
</main>
{lead_band("Wondering which side of the line a house sits on?", "Send the address. Nathaniel will tell you which pocket it's in and what that means for value.", first="sell")}
{foot(path, ["vendor/leaflet.js", "pockets.js"], "explore")}"""
    desc = f"An interactive map of {len(allp)} Los Angeles pockets and micro-neighborhoods, like the Bird Streets, Trousdale, Brentwood Park and North of Montana, with the streets that bound each one."
    ld_ = crumbs_ld([("Home", "/"), ("Local LA", "/neighborhoods/"), ("Pocket map", path)])
    return head("LA Neighborhood Boundaries Map: Every Pocket from the Bird Streets to North of Montana | Local LA", desc, path, ld(ld_) + '\n<link rel="stylesheet" href="/assets/vendor/leaflet.css">') + body


def page_hood(h, posts):
    path = f"/neighborhoods/{h['slug']}/"
    r = "/"
    c = CITIES[h["city"]]
    i = ORDER.index(h)
    prev_, next_ = ORDER[i - 1], ORDER[(i + 1) % len(ORDER)]
    ph = PHOTOS.get(h["slug"], [])
    n = h["name"]
    map_html, guide_html, mapdata = hood_local(h)
    pk_html, pk_list = pockets_section(h)
    hx = HIST.get(h["slug"])
    hist_html = HI.render(h, hx) if hx else ""
    first = bool(hx and hx.get("story_first"))
    near = "".join(photo_tile(BY_SLUG[x]) for x in h["near"])
    deals = DEALS.get(h["slug"], [])
    hero_deal = next((k for k in deals if ph and ph[0][0].endswith("/" + PROPS[k]["img"])), None)
    hero_tag = ""
    if hero_deal:
        hp_ = PROPS[hero_deal]
        hero_tag = (f'<a class="nb-hdeal" href="{hp_.get("page") or hp_["url"]}"{"" if hp_.get("page") else " rel=\"noopener\""}>'
                    f'<b>{e(hp_["tag"])}</b>{e(hp_["addr"])} &middot; {"Represented " + e(hp_["rep"].lower()) if hp_.get("sold") else e(hp_["spec"])} &rarr;</a>')
        deals = [k for k in deals if k != hero_deal]
    deals_html = ""
    if deals:
        deals_html = f"""<section class="band" id="deals"><div class="wrap">
<div class="sec-head"><div><p class="kick">Track record</p><h2>Nathaniel's deals in {e(n)}</h2></div><a href="/listings/">All listings &rarr;</a></div>
<div class="grid homes">{"".join(prop_card(k, r) for k in deals)}</div></div></section>"""
    rel_posts = [p for p in posts if h["slug"] in p.get("hoods", []) or (h["city"] == "Los Angeles" and "city-of-la" in p.get("hoods", []))]
    posts_html = ""
    if rel_posts:
        posts_html = f"""<div class="nb-reads"><h3>Read before you buy here</h3><div class="posts">{"".join(post_card(p, r) for p in rel_posts[:3])}</div></div>"""
    chips = "".join(f'<a href="/neighborhoods/#{t}">{e(TAGS[t])}</a>' for t in h["tags"])
    if ph:
        hero_media = ph_img(ph[0][0], ph[0][1], 2000, None, "100vw", eager=True, cls="nb-hero-img")
        credit = hero_tag or ('' if ph[0][0].startswith("/img/") else '<a class="credit" href="https://unsplash.com/" rel="noopener">Photo: Unsplash</a>')
    else:
        hero_media = aerial(*h["ll"], z=15, cols=7, rows=4, ts=300, cls="nb-hero-aer", eager=True, label=f"Aerial photo of {n}")
        credit = ""
    gal = ""
    if len(ph) > 3:
        items = ph[1:6]
        extra = len(ph) - 1 - len(items)
        figs = ""
        for k, (pid, alt) in enumerate(items):
            more = f'<span class="gend">+{extra} more</span>' if (extra > 0 and k == len(items) - 1) else ""
            figs += (f'<button type="button" class="g{" g0" if k == 0 else ""}" data-full="{photos.url(pid, 2000)}" data-alt="{e(alt)}" aria-label="View photo: {e(alt)}">'
                     f'{ph_img(pid, alt, 900 if k == 0 else 600, 0.75 if k else 0.8, "(max-width:700px) 80vw, 33vw")}{more}</button>')
        all_ = "".join(f'<i data-full="{photos.url(pid, 2000)}" data-alt="{e(alt)}"></i>' for pid, alt in ph)
        gal = (f'<section class="band nb-gal" id="photos"><div class="wrap"><div class="sec-head"><div><p class="kick">Photos</p><h2>{e(n)} in pictures</h2></div></div>'
               f'<div class="gallery n{len(items)}" data-gallery>{figs}<div hidden class="gall">{all_}</div></div></div></section>')
    lat, lng = h["ll"]
    qa = v8.hood_faq(h, c, PHONE, DRE)
    place = {"@context": "https://schema.org", "@type": "Place", "name": f"{n}, Los Angeles", "url": SITE + path,
             "description": h["intro"], "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng},
             "hasMap": v8.gmaps_link(h),
             "containedInPlace": {"@type": "City", "name": c["label"].replace("City of ", "").replace("Unincorporated ", "")}}
    if ph:
        place["image"] = [photos.url(pid, 1600) for pid, _ in ph[:3]]
    service = {"@context": "https://schema.org", "@type": "Service", "serviceType": "Real estate agent",
               "name": f"Buying, selling and renting in {n}", "url": SITE + path,
               "provider": {"@id": SITE + "/#nathaniel"}, "areaServed": {"@type": "Place", "name": f"{n}, Los Angeles, CA",
               "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng}}}
    crumbs = crumbs_ld([("Home", "/"), ("Local LA", "/neighborhoods/"), (n, path)])
    sub = [("overview", "Overview")] + ([("pockets", "Pockets")] if pk_list else []) + ([("history", "History")] if first else []) + [("living", "Living here")] + \
          ([("map", "Map")] if len(mapdata["pts"]) < 3 else []) + [("eat", "Eat, drink &amp; go")] + ([("history", "History")] if hx and not first else []) + \
          ([("photos", "Photos")] if gal else []) + ([("deals", "Deals")] if deals_html else []) + [("faq", "FAQ")]
    subnav = "".join(f'<a href="#{a}">{b}</a>' for a, b in sub)
    body = f"""{nav(path, "explore")}
<main class="nb">
<section class="nb-hero{" nb-aer" if not ph else ""}">{hero_media}<div class="nb-shade"></div>
<div class="wrap nb-hin">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/neighborhoods/">Local LA</a> / <a href="/neighborhoods/#{slug(h['region'])}">{e(h['region'])}</a></nav>
<h1>{e(n)}</h1>
<p class="nb-line">{e(h['line'])}</p>
<div class="nb-chips"><span>{e(c['short'])}</span><span>ZIP {e(h['zips'])}</span><span title="{TIER_WORD[h['tier']]}">{TIER[h['tier']]} &middot; {TIER_WORD[h['tier']]}</span></div>
<div class="nb-cta"><a class="btn lux solid" href="#lead" data-tabgo="b">Get {e(n)} listings</a><a class="btn lux" href="#lead" data-tabgo="v">What's my {e(n)} home worth?</a></div>
</div>{credit}</section>
<nav class="nb-sub" aria-label="On this page"><div class="wrap">{subnav}<a class="nb-sub-cta" href="tel:{TEL}">{ICONS['call']}{PHONE}</a></div></nav>
<section class="band nb-ov" id="overview"><div class="wrap nb-ov-grid">
<div class="nb-ov-l">
<p class="kick">What it&rsquo;s like</p>
<p class="nb-lead">{e(h['feel'])}</p>
<p class="nb-intro">{e(h['intro'])}</p>
<div class="taglinks">{chips}</div>
</div>
<aside class="nb-facts" aria-label="{e(n)} at a glance">
<h2>At a glance</h2>
<dl>
<div><dt>Jurisdiction</dt><dd>{e(c['label'])}</dd></div>
<div><dt>ZIP</dt><dd>{e(h['zips'])}</dd></div>
<div><dt>Price level</dt><dd>{TIER[h['tier']]} &middot; {TIER_WORD[h['tier']]}</dd></div>
<div><dt>Region</dt><dd>{e(h['region'])}</dd></div>
<div><dt>Good fit if</dt><dd>{e(h['fit'])}</dd></div>
</dl>
<div class="nb-agent"><img src="/img/nate-sm.jpg" alt="Nathaniel Grivas" width="64" height="80" loading="lazy">
<div><b>Nathaniel Grivas</b><span>REALTOR&reg; &middot; The Brodsky Group at Compass</span><a href="{GBP_URL}" rel="noopener">Google reviews &#8599;</a></div></div>
<div class="nb-agent-cta"><a class="btn solid" href="tel:{TEL}">{ICONS['call']}Call</a><a class="btn" href="sms:{TEL}">{ICONS['text']}Text</a><button type="button" class="btn" data-msg>{ICONS['email']}Message</button></div>
</aside>
</div></section>
{pk_html}
{hist_html if first else ""}
<section class="band nb-live" id="living"><div class="wrap">
<div class="sec-head"><div><p class="kick">Living here</p><h2>The homes, the rules and who it fits</h2></div></div>
<div class="nb-live-grid">
<div class="nb-live-l">
<h3>The housing</h3><p>{e(h['housing'])}</p>
<div class="fitgrid"><div class="fit yes"><b>Good fit if</b><p>{e(h['fit'])}</p></div><div class="fit no"><b>Think twice if</b><p>{e(h['skip'])}</p></div></div>
<div class="toolchips"><span>Run the numbers</span><a href="/tools/mortgage/">{ICONS['home']}Mortgage</a><a href="/tools/rent-vs-buy/">{ICONS['scale']}Rent vs buy</a><a href="/tools/transfer-tax/?city={slug(h['city'])}">{ICONS['tax']}Transfer tax</a><a href="/tools/compare/?a={h['slug']}&amp;b={h['near'][0]}">{ICONS['split']}Compare</a></div>
</div>
{rules_box(h, r)}
</div>
{posts_html}
</div></section>
{map_html}
{guide_html}
{"" if first else hist_html}
{gal}
{deals_html}
<section class="band" id="nearby"><div class="wrap">
<div class="sec-head"><div><p class="kick">Next door</p><h2>Neighborhoods nearby</h2></div><a href="/neighborhoods/">All 40 neighborhoods &rarr;</a></div>
<div class="tilerow">{near}</div>
</div></section>
{journal_band(h['slug'], n)}
{v8.faq_html(qa, f"{n}: common questions")}
{lead_band(f"Buying or selling in {n}?", f"First look at new {n} listings, or a free number on yours.", first="buy", area=n, addr_ph=f"Your {n} address", rating=True)}
<div class="lightbox" hidden role="dialog" aria-modal="true" aria-label="Photo viewer"><button type="button" class="lb-x" aria-label="Close">&times;</button><button type="button" class="lb-p" aria-label="Previous photo">&lsaquo;</button><img alt=""><button type="button" class="lb-n" aria-label="Next photo">&rsaquo;</button><p class="lb-c"></p></div>
</main>
{foot(path, (["vendor/leaflet.js"] if len(mapdata["pts"]) >= 3 or pk_list else []) + (["hoodmap.js"] if len(mapdata["pts"]) >= 3 else []) + (["pockets.js"] if pk_list else []), "explore")}"""
    if first:
        title = f"{n}, Los Angeles: History, Landmarks, Map & Where to Eat | Local LA"
        desc = f"The story of {n}: {hx['title']}. A timeline, landmarks and did-you-know facts, plus the best places to eat and drink nearby and what it's like to live there."[:300]
    else:
        title = f"{n}, Los Angeles: Best Restaurants, Bars, Things to Do & Map | Local LA"
        desc = f"{h['line']} The best places to eat, drink and go in {n}, pinned on a map, plus its history, homes, rules and what it's like to live there."[:300]
    items = [{"@type": "ListItem", "position": k + 1, "name": nm} for k, nm in enumerate(mapdata["all"])]
    il = {"@context": "https://schema.org", "@type": "ItemList", "name": f"Where to eat, drink and go in {n}", "itemListElement": items}
    faq_all = qa + (HI.faq_pairs(hx) if hx else [])
    if pk_list:
        faq_all = faq_all + [(f"What are the neighborhoods inside {n}?", f"{n} breaks into {len(pk_list)} pockets: " + "; ".join(p["n"] + (f" ({p['b']})" if p["b"] else "") for p in pk_list) + ". Values can change from one pocket to the next, sometimes across a single street.")]
    webpage = {"@context": "https://schema.org", "@type": "WebPage", "url": SITE + path, "name": title, "dateModified": datetime.date.today().isoformat(),
               "about": {"@type": "Place", "name": f"{n}, Los Angeles"}, "author": {"@id": SITE + "/#nathaniel"}, "inLanguage": "en-US"}
    return head(title, desc, path, ld(webpage) + ld(place) + ld(service) + ld(crumbs) + ld(il) + ld(v8.faq_ld(faq_all)) + '\n<link rel="stylesheet" href="/assets/vendor/leaflet.css">', og="hero.jpg") + body


def page_tools():
    path = "/tools/"
    r = rel(path)
    body = f"""{nav(path, "tools")}
<main>
<section class="band tight"><div class="wrap">
<p class="eyebrow">Free tools</p><h1 class="h1">Do the math before you call anyone</h1>
<p class="lede" style="margin-top:14px">Transfer taxes, Measure ULA, rent control and real monthly costs, city by city.</p>
</div></section>
<section class="band" style="padding-top:0"><div class="wrap"><div class="tools">{"".join(tool_card(s, r) for s, *_ in TOOLS)}</div></div></section>
{lead_band()}
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
{lead_band("Want the real number for a real property?", "Send the address and Nathaniel will run it with current comps, or share what you're looking for and he'll send homes that fit.", first="value" if preset == "sell" else "buy")}
"""
    body = f"""{nav(path, "tools")}
<main class="toolpage" data-tool="{slug_}">
<section class="band tight"><div class="wrap">
<div class="crumbs"><a href="{r}tools/">Tools</a> / {e(t)}</div>
<h1 class="h1">{e(t)}</h1>
<p class="lede" style="margin-top:14px">{e(d)}</p>
</div></section>
<section class="band" style="padding-top:0"><div class="wrap">{inner}</div></section>
{"" if lean else cta_strip("Want the real number for a real property?", "Estimates are a start. Send the address and Nathaniel will run it with current comps and the exact taxes, free.")}
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
<p class="formnote">By sending, you agree Nathaniel can contact you by call, text or email about real estate. Reply STOP to opt out of texts. <a href="/privacy/">Privacy</a></p>
</form>"""
    return tool_shell("neighborhood-quiz", "Find Your Place in LA: Buy, Rent, Invest or Build",
                      "Share what you're looking for and get matched to the Los Angeles neighborhoods that fit: buyers, renters, investors and developers.",
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


# ------------------------------------------------------------------ conversion: two lead flows, resources, proof
VALUE_URL = "/home-value/"
BUY_URL = "/buy/"
RENT_URL = "/lease/"

RESOURCES = [
    ("key", "Off-market and coming-soon homes", "Compass Private Exclusives and The Brodsky Group's off-market list, where many of the best homes trade first."),
    ("value", "Lenders for every kind of buyer", "Jumbo, bank-statement and DSCR loans. Lenders who approve buyers the big banks pass on."),
    ("split", "Creative deal structures", "Seller financing, leasebacks, assignments and 1031 exchanges, structured so every side is protected."),
    ("build", "Developers and builders", "Land plays, teardowns and ADUs, priced on what can be built."),
    ("team", "The right people for every step", "Inspectors, contractors, architects, escrow, title and tax pros, brought in with one call."),
    ("sign", "Complicated is fine", "Trusts, estates, tenants, six owners on one title, additions without permits."),
]

PROOF = [
    ("fuller", "fuller.jpg", "616 N Fuller Ave, Fairfax", "Both sides, seller financed", "The sellers carried the loan, and Nathaniel represented the buyer and the sellers."),
    ("lanark", "lanark.jpg", "18748 Lanark St, Reseda", "15.6% over asking", "7 offers in 9 days after Nathaniel marketed it to builders as a land play. Sold for $1,155,000."),
    ("hartland", "hartland.jpg", "14757 Hartland St, Van Nuys", "Won in multiple offers", "Then Nathaniel priced every inspection item and took $31,000 off in escrow, on a contract that said no credits."),
]


def resources_band(heading="One call. The whole network.", sub="Every resource it takes to close, behind one phone number."):
    cards = "".join(f'<div class="res-c"><span class="res-i" aria-hidden="true">{ICONS[ic]}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>' for ic, t, d in RESOURCES)
    return f"""<section class="band res-band"><div class="wrap">
<div class="lux-head"><p class="kick">What you get</p><h2>{e(heading)}</h2><p class="res-sub">{e(sub)}</p></div>
<div class="res-grid">{cards}</div>
<div class="res-cta"><a class="btn lux solid" href="{VALUE_URL}">What's my home worth?</a><a class="btn lux" href="{BUY_URL}">Find me a home</a><a class="btn lux" href="tel:{TEL}">Call {PHONE}</a></div>
</div></section>"""


def proof_band(heading="Recent results", kick="Track record", skip=()):
    cards = "".join(f'<a class="pf-c" href="{PROPS[k]["page"]}"><img src="/img/{img}" alt="{e(addr)}" loading="lazy" width="960" height="720">'
                    f'<span class="pf-t"><small>{e(addr)}</small><b>{e(big)}</b><span>{e(line)}</span><i>See how &rarr;</i></span></a>' for k, img, addr, big, line in PROOF if k not in skip)
    return f"""<section class="band pf-band"><div class="wrap">
<div class="lux-head"><p class="kick">{e(kick)}</p><h2>{e(heading)}</h2></div>
<div class="pf-grid">{cards}</div></div></section>"""


def lead_band(heading="Let's get you a number, or a home", sub="You'll hear back today.", first="value", area="", addr_ph="", kick="Free, no obligation", rating=False):
    tabs = [("v", "What's my home worth?"), ("b", "Find me a home")]
    if first == "buy":
        tabs = tabs[::-1]
    sel = tabs[0][0]
    btns = "".join(f'<button type="button" role="tab" data-tab="{k}" aria-selected="{str(k == sel).lower()}">{e(t)}</button>' for k, t in tabs)
    a_ = f' data-area="{e(area)}"' if area else ""
    ph = f' data-addrph="{e(addr_ph)}"' if addr_ph else ""
    panels = (f'<div data-panel="v"{"" if sel == "v" else " hidden"}><div class="lflow" data-flow="value"{ph}></div></div>'
              f'<div data-panel="b"{"" if sel == "b" else " hidden"}><div class="lflow" data-flow="buy"{a_}></div></div>')
    gets = "".join(f"<li>{x}</li>" for x in (
        "What your home would sell for, and what you'd keep",
        "Homes before they go public",
        "Financing that fits how you earn"))
    return f"""<section class="band lead-band" id="contact"><div class="wrap lb-grid">
<div class="lb-copy lb-head">
<p class="kick">{e(kick)}</p><h2>{e(heading)}</h2><p class="lb-sub">{e(sub)}</p>
</div>
<div class="lb-copy lb-more">
<ul class="lb-get">{gets}</ul>
<div class="lb-me"><img src="/img/nate-sm.jpg" alt="Nathaniel Grivas" width="64" height="80" loading="lazy"><div><b>Nathaniel Grivas</b><span>REALTOR&reg; &middot; The Brodsky Group at Compass</span>{(f'<a href="{GBP_URL}" target="_blank" rel="noopener">{stars()} 5.0 on Google</a>') if rating else ''}</div></div>
<div class="lb-quick"><a class="btn" href="tel:{TEL}">{ICONS['call']}Call {PHONE}</a><a class="btn" href="sms:{TEL}">{ICONS['text']}Text Nathaniel</a></div>
</div>
<div class="lb-card" data-tabs id="lead">
<div class="lb-tabs" role="tablist">{btns}</div>
{panels}
<noscript><p>Call or text {PHONE}, or email {EMAIL}.</p></noscript>
</div></div></section>"""


def cta_strip(t, s_, area="", sell_label="What's my home worth?", buy_label="Find me a home"):
    return (f'<aside class="cta-strip"><div class="wrap cs-in"><div><b>{e(t)}</b><span>{e(s_)}</span></div>'
            f'<div class="cs-b"><a class="btn solid" href="#lead" data-tabgo="v">{e(sell_label)}</a><a class="btn" href="#lead" data-tabgo="b">{e(buy_label)}</a></div></div></aside>')


VALUE_FAQ = [
    ("How is this different from a Zestimate?", "Nathaniel builds your number by hand from the most recent sales near you, then adjusts for what algorithms can't see: your upgrades, your condition, your lot and your street. You get a range and the sales behind it."),
    ("Does it cost anything?", "No. The valuation is free, and you're under no obligation to list with him."),
    ("How fast will I get it?", "Within 24 hours, usually the same day. Call or text 310-269-5541 if you need it sooner."),
    ("Will the valuation show what I'd walk away with?", "Yes. Nathaniel includes an estimate of your net after transfer taxes, Measure ULA where it applies, and typical selling costs."),
    ("My home needs work, has tenants or has additions without permits. Can it still be valued?", "Yes. Share what's going on and Nathaniel will price it as it stands, plus what it could sell for if you fixed the few things that pay off."),
    ("Can I sell without putting my home on the open market?", "Yes. Compass Private Exclusives and The Brodsky Group's buyer network let you sell quietly to qualified buyers first, and still test the open market later if you want."),
    ("Which areas do you value?", "West LA, Beverly Hills, the coast from Westchester to Malibu, Hollywood, Silver Lake, Los Feliz and the San Fernando Valley."),
]

BUY_FAQ = [
    ("Can Nathaniel really get me off-market homes?", "Yes. Compass Private Exclusives and coming-soon listings, plus The Brodsky Group's off-market list, go to Nathaniel's buyers before the public. Many of the best homes trade there first."),
    ("I'm self-employed. Can I still get pre-approved?", "Yes. Nathaniel works with lenders who use bank statements instead of tax returns, DSCR loans for investors and other non-traditional programs."),
    ("What is seller financing, and can I use it?", "The seller carries the loan instead of a bank. Nathaniel closed 616 N Fuller Ave this way. It works on the right property with the right seller, and he knows how to ask."),
    ("Does it cost me anything to work with Nathaniel as a buyer?", "His compensation is set in a written buyer agreement before any tour, and it's often paid by the seller. He'll walk you through it before anything is signed."),
    ("How fast will I hear back?", "Today. Call or text 310-269-5541 if you want to talk now."),
]


def lp_shell(path, active, kick, h1, lede, checks, flow, proof_k, faq, faq_t, title, desc, after_hero=""):
    li = "".join(f"<li>{e(c)}</li>" for c in checks)
    body = f"""{nav(path, active)}
<main class="lp">
<section class="lp-hero"><div class="wrap lp-grid">
<div class="lp-head">
<p class="kick">{e(kick)}</p>
<h1>{e(h1)}</h1>
<p class="lp-lede">{e(lede)}</p>
</div>
<div class="lp-card" id="lead"><div class="lflow" data-flow="{flow}"></div></div>
<div class="lp-more">
<ul class="lp-checks">{li}</ul>
{trust_row("lp-trust")}
</div>
</div></section>
{after_hero}
{proof_band("Recent results", "Track record")}
{reviews_band(True, "What clients say")}
{v8.faq_html(faq, faq_t)}
<section class="band lp-end"><div class="wrap lp-end-in"><h2>Ready when you are</h2><p>One minute here, or one call to {PHONE}.</p>
<div class="lh-cta"><a class="btn lux solid" href="#lead">{"Get my home value" if flow == "value" else "Start my search"}</a><a class="btn lux" href="tel:{TEL}">Call {PHONE}</a></div></div></section>
</main>
{foot(path)}"""
    svc = {"@context": "https://schema.org", "@type": "Service", "name": title.split(" | ")[0], "provider": {"@id": SITE + "/#nathaniel"},
           "areaServed": "Los Angeles, CA", "description": desc, "url": SITE + path, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
    return head(title, desc, path, ld(svc) + ld(v8.faq_ld(faq)) + ld(crumbs_ld([("Home", "/"), (h1, path)]))) + body


HOW_VALUE = [("Confirm your home", "Type the address. Nathaniel pulls the county record for beds, baths, square feet and lot, and you just confirm it."),
             ("He pulls the sales by hand", "Recent sales and pendings on your street, adjusted for your upgrades and lot."),
             ("You get your number and a plan", "A value range, your estimated net, and what to fix or skip. Within 24 hours.")]


def method_band():
    pts = [("value", "Every recent sale, adjusted by hand",
            "Each sale, pending and listing near you, adjusted for size, lot, condition, upgrades and the exact block."),
           ("pin", "Measured block by block",
            "In LA, one street can change the price. Your home is compared to the pocket it sits in."),
           ("build", "The land counts too",
            "Lot size, zoning and ADU room. On some lots the land is the value, and that changes who you sell to."),
           ("up", "The market sets the strategy",
            "Days on market, sale-to-list and new supply decide the list price and how to launch.")]
    cards = "".join(f'<div class="mth-c"><span class="mth-i" aria-hidden="true">{ICONS.get(ic, ICONS["home"])}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>' for ic, t, d in pts)
    return f"""<section class="band mth-band"><div class="wrap">
<div class="lux-head"><p class="kick">The method</p><h2>A data-driven price, checked by a local</h2><p class="res-sub">The data does the heavy lifting. A local reads what the data misses.</p></div>
<div class="mth-grid">{cards}</div>
<p class="mth-mk"><a class="btn lux" href="/market-temperature/">See this week's Market Temperature &rarr;</a></p>
</div></section>"""


def how_band(steps, heading):
    items = "".join(f'<li><span>{i + 1}</span><b>{e(t)}</b><p>{e(d)}</p></li>' for i, (t, d) in enumerate(steps))
    return f'<section class="band how-band"><div class="wrap"><div class="lux-head"><p class="kick">How it works</p><h2>{e(heading)}</h2></div><ol class="how">{items}</ol></div></section>'


MARKET_URL = "/market-temperature/"


def page_market():
    path = MARKET_URL
    M = json.loads((pathlib.Path(__file__).parent / "market" / "latest.json").read_text())
    H = json.loads((pathlib.Path(__file__).parent / "market" / "history.json").read_text())
    wk = datetime.date.fromisoformat(M["week"])
    wtxt = wk.strftime("%B %-d, %Y")
    rg = M["regions"]
    tot_a = sum(r["active"] for r in rg); tot_c = sum(r["cut"] for r in rg)
    share = lambda r: 100.0 * r["cut"] / r["active"] if r["active"] else 0
    R = M["rate"]; C = M["county"]
    d_rate = R["v"] - R["prev"]
    def card(k, v, s_):
        return f'<div class="mt-k"><span>{e(k)}</span><b>{v}</b><small>{s_}</small></div>'
    cards = (card("30-year fixed rate", f'{R["v"]:.2f}%', f'{"Up" if d_rate > 0 else "Down" if d_rate < 0 else "Flat"} {abs(d_rate):.2f} pts on the week &middot; {R["yago"]:.2f}% a year ago')
             + card("Homes for sale", f'{tot_a:,}', "Across the 40 neighborhoods covered here")
             + card("Listings with a price cut", f'{100.0 * tot_c / tot_a:.1f}%', f'{tot_c:,} of {tot_a:,} active listings')
             + card(f'LA County price, {C["month"].split()[0]}', f'${C["price"]:,}', f'{C["price_yoy"]:+.1f}% year over year')
             + card(f'LA County sales, {C["month"].split()[0]}', f'{C["sales_yoy"]:+.1f}%', "Closed sales, year over year"))
    mx = max(share(r) for r in rg) or 1
    rows = "".join(
        f'<tr><th scope="row"><a href="/neighborhoods/#{slug(r["r"])}">{e(r["r"])}</a></th><td>{r["active"]:,}</td><td>{r["cut"]:,}</td>'
        f'<td class="mt-bar"><span style="width:{100 * share(r) / mx:.0f}%"></span><b>{share(r):.1f}%</b></td></tr>'
        for r in sorted(rg, key=share))
    prev = H[-2] if len(H) > 1 else None
    wow = ""
    if prev:
        pa = sum(r["active"] for r in prev["regions"])
        wow = f'<p class="mt-note">Week over week: homes for sale {"up" if tot_a >= pa else "down"} {abs(tot_a - pa):,} from {pa:,} on {e(prev["week"])}.</p>'
    take = "".join(f"<li>{e(x)}</li>" for x in M["take"])
    hist = "".join(f'<tr><td>{e(h["week"])}</td><td>{h["rate"]:.2f}%</td><td>{sum(r["active"] for r in h["regions"]):,}</td><td>{100.0 * sum(r["cut"] for r in h["regions"]) / max(1, sum(r["active"] for r in h["regions"])):.1f}%</td></tr>' for h in reversed(H[:-1]))
    histbox = (f'<div><p class="kick">Week by week</p><h2>Earlier weeks</h2>'
               f'<table class="mt-t mt-h"><thead><tr><th>Week</th><th>30-year rate</th><th>For sale</th><th>Share reduced</th></tr></thead><tbody>{hist}</tbody></table></div>') if hist else ""
    howcls = "mt-two" if hist else "mt-one"
    body = f"""{nav(path, "market")}
<main>
<section class="band mt-hero"><div class="wrap">
<p class="eyebrow">Week of {e(wtxt)} &middot; Updated weekly</p>
<h1 class="h1">Market Temperature</h1>
<p class="lede">The Los Angeles market, measured every week. Just the numbers.</p>
<div class="mt-cards">{cards}</div>
</div></section>
<section class="band" style="padding-top:0"><div class="wrap mt-two">
<div class="mt-take"><p class="kick">This week</p><h2>What the data shows</h2><ul>{take}</ul>{wow}</div>
<div class="mt-reg"><p class="kick">By area</p><h2>Price cuts by region</h2>
<p class="mt-sub">Active listings and the share showing a price reduction. A lower share means sellers are holding price; a higher share means more of them are adjusting.</p>
<table class="mt-t"><thead><tr><th>Region</th><th>For sale</th><th>Reduced</th><th>Share reduced</th></tr></thead><tbody>{rows}</tbody></table></div>
</div></section>
<section class="band" style="padding-top:0"><div class="wrap {"mt-two" if hist else "mt-one"}">
{histbox}
<div class="mt-how"><p class="kick">How it is measured</p><h2>Sources and method</h2>
<p><b>Listings:</b> {e(M["listings_src"])}, counted by region across the 40 neighborhoods on this site. "Reduced" counts active listings Zillow flags as price reduced.</p>
<p><b>Mortgage rates:</b> <a href="{R["url"]}" rel="noopener">{e(R["src"])}</a>, latest weekly survey as of {e(R["asof"])}.</p>
<p><b>County prices and sales:</b> <a href="{C["url"]}" rel="noopener">{e(C["src"])}</a>, {e(C["month"])}, existing single-family homes.</p>
<p>Region counts use public listing data, so they can differ from MLS totals. Nathaniel can run any single neighborhood, pocket or price band from the MLS on request.</p></div>
</div></section>
<section class="band mt-cta"><div class="wrap"><div class="lux-head"><p class="kick">What it means for you</p><h2>The market sets the strategy</h2><p class="res-sub">Get a number built on this week's data.</p></div>
<div class="cta-row" style="justify-content:center"><a class="btn lux solid" href="{VALUE_URL}">Get a free home valuation</a><a class="btn lux" href="{BUY_URL}">Start a home search</a><a class="btn lux" href="tel:{TEL}">Call {PHONE}</a></div></div></section>
</main>
{foot(path)}"""
    desc = (f"Los Angeles Market Temperature for the week of {wtxt}: {tot_a:,} homes for sale across 40 neighborhoods, {100.0 * tot_c / tot_a:.1f}% with a price cut, "
            f"30-year rate {R['v']:.2f}%. Updated weekly by Nathaniel Grivas, REALTOR® at Compass.")
    data_ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Los Angeles Market Temperature", "description": desc,
               "url": SITE + path, "temporalCoverage": M["week"], "creator": {"@id": SITE + "/#nathaniel"},
               "variableMeasured": ["Active listings by region", "Share of listings with a price reduction", "30-year fixed mortgage rate", "Los Angeles County median price"],
               "dateModified": M["week"], "isAccessibleForFree": True, "spatialCoverage": {"@type": "Place", "name": "Los Angeles, CA"},
               "license": SITE + "/privacy/", "publisher": {"@id": SITE + "/#nathaniel"}}
    return head(f"Market Temperature: Los Angeles Housing Market This Week ({wtxt}) | Nathaniel Grivas", desc, path, ld(data_ld)) + body


def market_teaser():
    try:
        M = json.loads((pathlib.Path(__file__).parent / "market" / "latest.json").read_text())
    except Exception:
        return ""
    rg = M["regions"]; a = sum(x["active"] for x in rg); c = sum(x["cut"] for x in rg)
    wk = datetime.date.fromisoformat(M["week"]).strftime("%B %-d")
    return f"""<section class="band mt-tease"><div class="wrap"><div class="mt-tease-in">
<div><p class="kick">Market Temperature &middot; week of {e(wk)}</p><h2>The LA market this week</h2></div>
<dl><div><dt>30-year rate</dt><dd>{M["rate"]["v"]:.2f}%</dd></div><div><dt>Homes for sale</dt><dd>{a:,}</dd></div><div><dt>With a price cut</dt><dd>{100.0 * c / a:.1f}%</dd></div></dl>
<a class="btn lux" href="{MARKET_URL}">See the full read &rarr;</a></div></div></section>"""


def page_value():
    return lp_shell(VALUE_URL, "value", "Los Angeles", "Free Home Valuation",
                    "Your number within 24 hours, built from the sales on your street and this week's market.",
                    ["A value range, with the sales behind it", "What you'd keep after taxes and costs",
                     "The option to sell quietly, off-market"],
                    "value", "lanark", VALUE_FAQ, "Home value questions",
                    "Free Home Valuation in Los Angeles: What's My Home Worth? | Nathaniel Grivas",
                    "Get a free, hand-built home valuation from Nathaniel Grivas, REALTOR® with The Brodsky Group at Compass: your value range from recent sales near you plus your estimated net. West LA, Beverly Hills and the Valley.",
                    method_band() + how_band(HOW_VALUE, "Your number in three steps"))


def page_buy():
    return lp_shell(BUY_URL, "buy", "Buying in Los Angeles", "See it before it hits Zillow",
                    "Tell Nathaniel what you want. He'll send what fits, including homes that never go public, and the lender who can get you there.",
                    ["New matches the day they list", "Private and off-market homes", "Lenders for every kind of income"],
                    "buy", "hartland", BUY_FAQ, "Buying questions",
                    "Buy a Home in Los Angeles: Off-Market Homes, Lenders & Creative Financing | Nathaniel Grivas",
                    "Find a home in West LA, Beverly Hills or the Valley with Nathaniel Grivas, REALTOR® at Compass: off-market and coming-soon homes, lenders for self-employed and investor buyers, and creative financing like seller carry.")


RENT_FAQ = [
    ("What do landlords in Los Angeles usually ask for?", "A rental application, photo ID, proof of income (many landlords look for income around three times the rent), a credit report and references from past landlords. Having them ready makes your application stronger when several people apply for the same place."),
    ("Is the place rent controlled?", "It depends on the city and the building. In the City of Los Angeles, most apartments built before October 1978 fall under the Rent Stabilization Ordinance, and California's statewide cap covers many other rentals. Santa Monica, West Hollywood, Culver City and Beverly Hills have their own rules. Nathaniel can check a specific address."),
    ("Can Nathaniel lease out my property?", "Yes. He prices the rent from recent leases nearby, markets the home, screens applicants, and handles the lease and move-in. He leased 1127 Glenville Dr in Pico-Robertson, representing both the landlord and the tenant."),
]


def page_rent():
    path = RENT_URL
    tabs = (f'<div class="lb-tabs" role="tablist"><button type="button" role="tab" data-tab="r" aria-selected="true">Find a home to lease</button>'
            f'<button type="button" role="tab" data-tab="l" aria-selected="false">What will my place lease for?</button></div>'
            f'<div data-panel="r"><div class="lflow" data-flow="rent"></div></div><div data-panel="l" hidden><div class="lflow" data-flow="lease"></div></div>'
            f'<noscript><p>Call or text {PHONE}, or email {EMAIL}.</p></noscript>')
    checks = "".join(f"<li>{e(c)}</li>" for c in (
        "New matches as they list",
        "An application that stands out",
        "For owners: the right price and the right tenant"))
    cards = "".join(prop_card(k, "/") for k in ("edgecliffe", "glenville"))
    title = "Homes for Lease in Los Angeles: Leasing for Tenants and Owners | Nathaniel Grivas"
    desc = "Homes for lease in Los Angeles with Nathaniel Grivas, REALTOR® at Compass: 1436 Edgecliffe Dr #103 in Silver Lake is available now. Start a lease search, or get a free lease estimate for your property."
    body = f"""{nav(path, "rent")}
<main class="lp">
<section class="lp-hero"><div class="wrap lp-grid">
<div class="lp-head">
<p class="kick">Leasing in Los Angeles</p>
<h1>Lease a home, or lease yours out</h1>
<p class="lp-lede">Tell Nathaniel what you need. He'll send homes that fit, or price and lease yours.</p>
</div>
<div class="lp-card" id="lead" data-tabs>{tabs}</div>
<div class="lp-more">
<ul class="lp-checks">{checks}</ul>
</div>
</div></section>
<section class="band" id="leases"><div class="wrap">
<div class="sec-head"><div><p class="kick">For lease now and recently leased</p><h2>Nathaniel's leases</h2></div><a href="/listings/">All listings &rarr;</a></div>
<div class="grid g2">{cards}</div>
</div></section>
{v8.faq_html(RENT_FAQ, "Leasing questions")}
<section class="band lp-end"><div class="wrap lp-end-in"><h2>Ready when you are</h2><p>One minute here, or one call to {PHONE}.</p>
<div class="lh-cta"><a class="btn lux solid" href="#lead">Start my lease search</a><a class="btn lux" href="tel:{TEL}">Call {PHONE}</a></div></div></section>
</main>
{foot(path)}"""
    il = {"@context": "https://schema.org", "@type": "ItemList", "name": "Nathaniel Grivas leases",
          "itemListElement": [{"@type": "ListItem", "position": n + 1, "url": PROPS[k]["url"],
                               "name": f"{PROPS[k]['addr']}, {PROPS[k]['area']}: {PROPS[k]['tag']}, {PROPS[k]['price']}{PROPS[k].get('per', '')}"}
                              for n, k in enumerate(("edgecliffe", "glenville"))]}
    svc = {"@context": "https://schema.org", "@type": "Service", "name": "Leasing in Los Angeles", "serviceType": "Residential leasing",
           "provider": {"@id": SITE + "/#nathaniel"}, "areaServed": "Los Angeles, CA", "description": desc, "url": SITE + path}
    return head(title, desc, path, ld(svc) + ld(il) + ld(v8.faq_ld(RENT_FAQ)) + ld(crumbs_ld([("Home", "/"), ("Lease", path)]))) + body


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
    cta_txt = "Schedule a showing" if f["status"] != "Sold" else "Get a result like this"
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
<div class="lh-cta">{f'<a class="btn lux solid" href="#lead" data-tabgo="v">{cta_txt}</a>' if f["status"] == "Sold" else f'<button type="button" class="btn lux solid" data-msg>{cta_txt}</button>'}<a class="btn lux" href="tel:{TEL}">Call {PHONE}</a></div>
<div class="lh-cta">{links}</div>
<p class="ht-credit">{e(f["credit"])}</p>
</div></div></div></section>
<section class="band lux-band"><div class="wrap narrow ht-body"><p class="kick">The home</p>{body_p}</div></section>
{gal}
<section class="band lux-band"><div class="wrap"><div class="lux-head"><p class="kick">Also featured</p><h2><a class="plain" href="{PROPS[other]["page"]}">{e(o["title"])}</a></h2></div>
<a class="also" href="{PROPS[other]["page"]}"><img src="{o["poster"]}" alt="{e(o["title"])}" loading="lazy"><span><small>{e(o["status"])} &middot; {e(o["price"])}</small><b>{e(o["title"])}</b>{e(o["line"])} <i>Watch the film &rarr;</i></span></a></div></section>
{resources_band("Creative deals, real resources", "A $100M+ annual team behind every deal.")}
{sale_review(1) if k == "fuller" else reviews_band(False, "What clients say")}
{lead_band("Want a result like this?", "Start with what your home is worth.", first="value") if f["status"] == "Sold" else lead_band("Want a home like this?", "Ask about this one, or see what else fits before it goes public.", first="buy")}
{'<div class="lightbox" hidden role="dialog" aria-modal="true" aria-label="Photo viewer"><button type="button" class="lb-x" aria-label="Close">&times;</button><button type="button" class="lb-p" aria-label="Previous photo">&lsaquo;</button><img alt=""><button type="button" class="lb-n" aria-label="Next photo">&rsaquo;</button><p class="lb-c"></p></div>' if gal else ''}
</main>
{foot(path)}"""
    ld_ = {"@context": "https://schema.org", "@type": "SingleFamilyResidence", "name": f["title"], "url": SITE + path,
           "address": {"@type": "PostalAddress", "streetAddress": f["title"], "addressLocality": "Los Angeles", "addressRegion": "CA", "postalCode": f["where"][-5:]},
           "numberOfRooms": f["stats"][0][0], "floorSize": {"@type": "QuantitativeValue", "value": f["stats"][2][0].replace(",", ""), "unitCode": "FTK"},
           "image": SITE + f["poster"], "description": f["line"]}
    title = f'{f["title"]}, {f["where"].split(",")[0]} | {f["status"]} {f["price"]} | Nathaniel Grivas'
    return head(title, f["line"], path, ld(ld_) + ld(crumbs_ld([("Home", "/"), ("Listings", "/listings/"), (f["title"], path)])), og=f["poster"].replace("/img/", "")) + body


DEAL_PAGES = {
    "lanark": dict(
        title="18748 Lanark St", where="Reseda, Los Angeles, CA 91335", zip="91335", status="Sold", price="$1,155,000",
        kick="Sold &middot; Land play", side="Represented the sellers", img="lanark.jpg", alt="18748 Lanark St in Reseda from the street",
        aerial="lanark-aerial.jpg", aerial_alt="Drone view of 18748 Lanark St showing the open land behind the house",
        q="18748 Lanark St, Reseda, CA 91335", ll=(34.217395, -118.541811),
        stats=[("21,758", "Sq ft lot"), ("300 ft", "Lot depth"), ("7", "Offers"), ("9", "Days to escrow"), ("+15.6%", "Over asking")],
        line="A half-acre lot in Reseda that Nathaniel marketed to developers as a land play. Multiple offers came in the first week.",
        h2="The play: market the land to builders",
        body=["18748 Lanark is a 21,758 sq ft lot, 72 feet wide and 300 feet deep, zoned RA-1. A 1928 house sits near the street, and about 150 feet of open land runs behind it. The family had owned it since 1994.",
              "The value was in the land, so Nathaniel marketed it as a land play for builders and developers. He flew drone aerials to show the full depth of the lot, pulled the zoning, and put it in front of investors and the agents who work with them.",
              "It hit the MLS on August 11, 2026 at $999,000. Multiple offers came in the first week, seven by day nine, six of them all cash. On August 20 it went into escrow at $1,200,000.",
              "The buyer's appraisal came back at $1,108,300. He held the price $46,700 above the appraisal, and got his sellers a 29-day stay after closing for $1 in rent. It closed on September 25, 2026."],
        timeline=[("Aug 11", "Listed at $999,000"), ("First week", "Multiple offers in"), ("Aug 20", "In escrow at $1,200,000"),
                  ("Aug 27", "Appraisal at $1,108,300"), ("Sep 8", "Price held above the appraisal"), ("Sep 25", "Closed")],
        ai="Nathaniel Grivas marketed this half-acre Reseda lot to developers as a land play. It drew multiple offers in the first week and seven by day nine, went into escrow on day nine, and sold for $1,155,000, $156,000 over the $999,000 asking price and $46,700 above the appraisal. Closed September 25, 2026.",
        review=0,
        cta=("Own a lot builders would want?", "Send the address. See what a builder would pay.", "sell"),
        credit="Sold by Nathaniel Grivas of The Brodsky Group at Compass"),
    "hartland": dict(
        title="14757 Hartland St", where="Van Nuys, Los Angeles, CA 91405", zip="91405", status="Sold", price="$825,000",
        kick="Bought &middot; Development play", side="Represented the buyer", img="hartland.jpg", alt="14757 Hartland St in Van Nuys from the street",
        q="14757 Hartland St, Van Nuys, CA 91405", ll=(34.195057, -118.455056), sqft="1591",
        stats=[("7,119", "Sq ft corner lot"), ("1,591", "Sq ft house"), ("5", "Days to contract"), ("$31K", "Cut in escrow"), ("2", "ADUs planned")],
        line="A corner-lot development play in Van Nuys for Nathaniel's buyer: remodel the house, add two ADUs in the back and rent them out. He won it in multiple offers, then negotiated the price down in escrow.",
        h2="The play: remodel, add two ADUs, rent",
        body=["His buyer wanted a Valley corner lot with room to build. 14757 Hartland hit the MLS on May 28, 2026 at $825,000: a 1954 three-bedroom, two-bath house with 1,591 sq ft on a 7,119 sq ft corner lot at the start of a cul-de-sac.",
              "The plan is to remodel the front house, add two ADUs in the back and rent them out. The corner lot and the position of the garage leave room behind the house for both units.",
              "The seller had multiple offers. His buyer came in all cash and went into contract on June 2, five days after it listed, at $856,000.",
              "The seller's terms said no repairs and no credits. The inspections found sewer, foundation, termite and chimney work, so Nathaniel priced every item from the reports and took it back to the seller. A week into escrow the price came down to $825,000, $31,000 less. It closed on July 13, 2026."],
        timeline=[("May 28", "Listed at $825,000"), ("Jun 2", "In contract at $856,000 after multiple offers"),
                  ("Jun 9", "Price cut to $825,000 in escrow"), ("Jul 13", "Closed at $825,000")],
        ai="Nathaniel Grivas represented an investor buyer on this Van Nuys corner lot, bought to remodel the house and add two ADUs in the back to rent out. He won it in a multiple-offer situation five days after it listed, then negotiated the price from $856,000 down to $825,000 in escrow using the inspection reports. Closed July 13, 2026.",
        review=None,
        cta=("Looking for a deal like this?", "Share the area, the budget and the plan. Nathaniel will send lots and fixers that pencil, including ones before they hit the market.", "buy"),
        credit="Buyer represented by Nathaniel Grivas of The Brodsky Group at Compass"),
}


def sale_review(idx):
    r_ = v8.REVIEWS[idx]
    return (f'<section class="band rv"><div class="wrap narrow"><div class="rv-head"><div><p class="kick">From this sale</p><h2>What the sellers said</h2></div>'
            f'<a class="rv-score" href="{GBP_URL}" target="_blank" rel="noopener"><b>{v8.RATING}</b><span>{stars()}<small>Read it on Google &#8599;</small></span></a></div>'
            f'<div class="rv-grid one">{v8.review_card(r_, True, link=False)}</div></div></section>')


def deal_sat(d):
    src = f"https://www.google.com/maps/embed?origin=mfe&pb=!1m4!2m1!1s{quote_plus(d['q'])}!5e1!6i18"
    return (f'<div class="sat deal-sat" data-sat="{e(src)}">{aerial(*d["ll"], z=16, cols=5, rows=4, ts=256, label="Aerial view of " + d["title"])}'
            f'<noscript><iframe src="{e(src)}" title="Satellite map of {e(d["title"])}" loading="lazy"></iframe></noscript></div>')


def page_deal(k):
    d = DEAL_PAGES[k]
    path = PROPS[k]["page"]
    stats = "".join(f'<div><b>{e(v)}</b><span>{e(l)}</span></div>' for v, l in d["stats"])
    body_p = "".join(f"<p>{e(x)}</p>" for x in d["body"])
    tl = "".join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in d["timeline"])
    gmaps = f"https://www.google.com/maps/search/?api=1&query={quote_plus(d['q'])}"
    photo2 = ""
    if d.get("aerial"):
        photo2 = f'<figure class="deal-fig"><img src="/img/{d["aerial"]}" alt="{e(d["aerial_alt"])}" loading="lazy" width="1400" height="788"><figcaption>{e(d["aerial_alt"])}. Drone photo from the listing.</figcaption></figure>'
    rv = ""
    if d.get("review") is not None:
        rv = sale_review(d["review"])
    else:
        rv = reviews_band(False, "What clients say")
    more = "".join(prop_card(x, "/") for x in SOLD if x != k)
    h_, s_, pre = d["cta"]
    body = f"""{nav(path, "listings")}
<main>
<section class="home-top"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/listings/">Listings</a> / <span>{e(d["title"])}</span></nav>
<div class="ht-grid">
<div class="ht-film deal-hero"><img src="/img/{d["img"]}" alt="{e(d["alt"])}" width="960" height="720" fetchpriority="high"></div>
<div class="ht-copy">
<p class="kick">{d["kick"]} &middot; {e(d["where"].split(",")[0])}</p>
<h1>{e(d["title"])}</h1>
<p class="ht-where">{e(d["where"])} &middot; {e(d["side"])}</p>
<p class="ht-price">Sold for {e(d["price"])}</p>
<div class="ht-stats">{stats}</div>
<p class="ht-line">{e(d["line"])}</p>
<div class="lh-cta"><a class="btn lux solid" href="#lead" data-tabgo="{"v" if d["cta"][2] == "sell" else "b"}">{"Get a result like this" if d["cta"][2] == "sell" else "Find a deal like this"}</a><a class="btn lux" href="tel:{TEL}">Call {PHONE}</a></div>
<div class="lh-cta"><a class="btn lux" href="{PROPS[k]["url"]}" rel="noopener">View on Compass &#8599;</a></div>
<p class="ht-credit">{e(d["credit"])}</p>
</div></div></div></section>
<section class="band lux-band"><div class="wrap deal-grid">
<div class="ht-body"><p class="kick">How it went</p><h2 class="deal-h">{e(d["h2"])}</h2>{body_p}</div>
<aside class="deal-tl"><p class="kick">Timeline</p><ol>{tl}</ol></aside>
</div></section>
<section class="band lux-band"><div class="wrap">
<div class="lux-head"><p class="kick">From above</p><h2>The lot</h2></div>
<div class="deal-media{" two" if photo2 else ""}">{photo2}<div>{deal_sat(d)}<p class="deal-cap">Satellite view. <a href="{gmaps}" target="_blank" rel="noopener">Open in Google Maps &#8599;</a></p></div></div>
</div></section>
{resources_band()}
{rv}
<section class="band"><div class="wrap"><div class="head"><div><p class="eyebrow">Track record</p><h2 class="h2">More closed deals</h2></div></div>
<div class="grid">{more}</div></div></section>
{lead_band(h_, s_, first="value" if pre == "sell" else "buy")}
</main>
{foot(path)}"""
    ld_ = {"@context": "https://schema.org", "@type": "SingleFamilyResidence", "name": d["title"], "url": SITE + path,
           "address": {"@type": "PostalAddress", "streetAddress": d["title"], "addressLocality": d["where"].split(",")[0],
                       "addressRegion": "CA", "postalCode": d["zip"], "addressCountry": "US"},
           "image": SITE + "/img/" + d["img"], "description": d["line"]}
    if d.get("ll"):
        ld_["geo"] = {"@type": "GeoCoordinates", "latitude": d["ll"][0], "longitude": d["ll"][1]}
    if d.get("sqft"):
        ld_["floorSize"] = {"@type": "QuantitativeValue", "value": d["sqft"], "unitCode": "FTK"}
    title = f'{d["title"]}, {d["where"].split(",")[0]} | Sold {d["price"]} | Nathaniel Grivas'
    return head(title, d["line"], path, ld(ld_) + ld(crumbs_ld([("Home", "/"), ("Listings", "/listings/"), (d["title"], path)])), og=d["img"]) + body


def page_listings():
    path = "/listings/"
    r = rel(path)
    body = f"""{nav(path, "listings")}
<main>
<section class="band tight"><div class="wrap">
<p class="eyebrow">Listings</p><h1 class="h1">For sale, for lease and recently closed</h1>
<p class="lede" style="margin-top:14px">On the market now, and already closed.</p>
</div></section>
{featured_section("Featured homes", "Watch the films")}
<section class="band" style="padding-top:0"><div class="wrap">
<div class="head"><div><p class="eyebrow">Now available</p><h2 class="h2">More for sale and lease</h2></div></div>
<div class="grid">{"".join(prop_card(k, r) for k in ACTIVE if k not in FEATURED)}</div></div></section>
<section class="band" style="padding-top:0"><div class="wrap">
<div class="head"><div><p class="eyebrow">Track record</p><h2 class="h2">Closed</h2></div></div>
<div class="grid">{"".join(prop_card(k, r) for k in SOLD if k not in FEATURED)}</div></div></section>
{reviews_band(False, "What sellers say")}
{lead_band("Be first on the list", "Coming-soon and off-market homes reach his list first.", first="buy")}
</main>
{foot(path)}"""
    return head("Listings | Nathaniel Grivas, Compass", "Active listings and recent transactions by Nathaniel Grivas, REALTOR® at Compass.", path) + body


WHY = [
    ("split", "Deals that close", "Seller financing, leasebacks, assignments and 1031s, built so both sides are protected."),
    ("up", "Listings launched like products", "A marketer first. Your home goes in front of the buyers most likely to pay up."),
    ("scale", "Negotiation to the close", "Inspection items priced, credits argued with data, terms held through escrow."),
    ("build", "A developer's eye", "Zoning, lot size and ADU room, priced in from day one."),
    ("key", "First access", "Compass Private Exclusives, coming-soon homes and The Brodsky Group's off-market list."),
    ("call", "He answers", "Same day. Trusts, tenants, six owners on one title: complicated is fine."),
]


def page_about():
    path = "/about/"
    r = rel(path)
    why = "".join(f'<div class="why-c"><span class="why-i" aria-hidden="true">{ICONS.get(ic, ICONS["home"])}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>' for ic, t, d in WHY)
    body = f"""{nav(path, "about")}
<main>
<section class="band"><div class="wrap split">
<div class="portrait"><img src="{r}img/nate-about.jpg" alt="Nathaniel Grivas, REALTOR at Compass" width="900" height="990"></div>
<div><p class="eyebrow">About Nathaniel</p><h1 class="h1">Nathaniel Grivas</h1>
<p class="ab-tag">The agent who finds a way to get it done.</p>
<p class="lede" style="margin-top:14px">Nathaniel Grivas is a REALTOR&reg; with The Brodsky Group at Compass Beverly Hills. Clients call him when the deal is worth getting right.</p>
{trust_row()}
<div class="cta-row"><a class="btn solid" href="tel:{TEL}">Call {PHONE}</a><a class="btn" href="{VALUE_URL}">What's my home worth?</a><a class="btn" href="{BUY_URL}">Find me a home</a></div>
</div></div></section>
<section class="band why-band"><div class="wrap">
<div class="lux-head"><p class="kick">Why clients hire him</p><h2>What he brings to every deal</h2></div>
<div class="why-grid">{why}</div>
<div class="cta-row" style="justify-content:center;margin-top:26px"><a class="btn solid" href="#lead" data-tabgo="v">Get my home value</a><a class="btn" href="#lead" data-tabgo="b">Start my home search</a><a class="btn" href="tel:{TEL}">Call {PHONE}</a></div>
</div></section>
{proof_band("The results behind it", "Track record")}
<section class="band" style="padding-top:0"><div class="wrap ab-body body">
<div><h2>Background</h2>
<p>Nathaniel was raised between New York and Seattle and moved to Los Angeles for Loyola Marymount University, where he graduated cum laude in Marketing with a minor in Business Law. He worked in marketing at Compass before becoming an agent on The Brodsky Group, and he brings both to every deal: a marketer's eye for how a home is presented and found, and a contract-minded approach to terms, timelines and risk.</p>
</div><div><h2>What he does</h2>
<p>Pricing and listing preparation, marketing and launch, buyer representation in competitive offers, negotiation through escrow, leasing, and development work: teardown and lot value analysis, zoning and ADU feasibility, and off-market sourcing for builders and investors. When a deal needs a lender, a contractor, an architect, a 1031 intermediary or a tax professional, he brings in the right one.</p>
</div><div><h2>Where he works</h2>
<p>West Los Angeles, Beverly Hills and the Hills, the beach cities from Malibu to Playa del Rey, Hollywood to Silver Lake, and the San Fernando Valley. Every neighborhood he covers has its own page in <a href="{r}neighborhoods/">Local LA</a>, with a map of the places locals go.</p>
</div><div><h2>Outside of real estate</h2>
<p>Basketball, golf and tennis, and time with friends and family.</p></div>
</div></section>
{reviews_band(True, "What clients say")}
{team_section("team-2.jpg", "Nathaniel works on The Brodsky Group, led by Or Brodsky at Compass Beverly Hills, on everything from new construction to off-market sales.")}
{lead_band("Work with Nathaniel", "You'll hear back today.", rating=False)}
</main>
{foot(path)}"""
    desc = ("Nathaniel Grivas, REALTOR® with The Brodsky Group at Compass Beverly Hills ($100M+ annual team sales). Seller financing, development sites, "
            "off-market homes and complicated deals across West LA, Beverly Hills and the Valley. DRE #02410660.")
    return head("About Nathaniel Grivas | REALTOR® at Compass Beverly Hills | The Brodsky Group", desc, path, ld(person_ld())) + body


def place_card(p, d, hood_name, show_hood=False, primary=None):
    src = "".join(f'<a href="{d["sources"][k][1]}" rel="noopener">{e(d["sources"][k][0].split(":")[0])}</a>' for k in p.get("s", []) if k in d["sources"])
    chips = "".join(f'<span>{e(G.CATS[c][0])}</span>' for c in p["c"] if c != primary)
    where = (f'<a href="/neighborhoods/{d["slug"]}/#eat">{e(hood_name)}</a> &middot; ' if show_hood else "") + e(p.get("a") or "")
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
            if secs.count('class="ggroup"') == 1:
                secs += cta_strip(f"Love {h['name']}? Live here.", f"Get new {h['name']} listings, including off-market ones, or a free value on your {h['name']} home.", buy_label=f"Get {h['name']} listings")
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
<div><p class="kick">Thinking about living here?</p><h2>Homes in {e(h["name"])}</h2><p>Share what you're after and Nathaniel will send new {e(h["name"])} listings as they hit the market.</p>
<div class="lh-cta"><a class="btn lux solid" href="#lead" data-tabgo="b">Get {e(h["name"])} listings</a><a class="btn lux" href="/neighborhoods/{d["slug"]}/">The {e(h["name"])} neighborhood guide</a></div></div>
<div><p class="kick">More guides</p><div class="gend-l">{more}<a href="/guide/">All neighborhoods &rarr;</a></div>
<details class="gsrc"><summary>Sources</summary><ul>{srcs}</ul></details></div>
</div></div></section>
{lead_band(f"Living in {h['name']}?", f"Get new {h['name']} listings as they hit, including off-market ones, or find out what your home is worth.", first="buy", area=h["name"], addr_ph=f"Your {h['name']} address")}
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
        if secs.count('class="gsec"') == 2:
            secs += cta_strip("Want to live near spots like these?", "Get homes that fit, including off-market ones, or a free value on your home.")
    cnt = guide_counts()
    other = "".join(f'<a href="/guide/best/{k}/">{e(G.CATS[k][0])} <i>{cnt[k]}</i></a>' for k in G.ORDERED if cnt.get(k, 0) >= 3 and k != cat)
    body = f"""{nav(path, "explore")}
<main>
<section class="ghero"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/neighborhoods/">Local LA</a> / <span>{e(label)}</span></nav>
<p class="kick">Local LA</p>
<h1>The best {e(plural)} in Los Angeles</h1>
<p class="lede">{len(rows)} picks across the neighborhoods Nathaniel covers, grouped by area. Each one is written from what critics and real people consistently say about it.</p>
</div></section>
<div class="wrap gbody">{secs}</div>
<section class="band lux-band"><div class="wrap"><div class="lux-head"><p class="kick">Keep browsing</p><h2>More categories</h2></div><div class="gcats">{other}</div></div></section>
{lead_band("Want to live near the best of LA?", "Share what you love and Nathaniel will send homes that fit, including off-market ones. Or get a free value on yours.", first="buy")}
</main>
{foot(path)}"""
    title = f"Best {label} in Los Angeles by Neighborhood | Local LA"
    desc = f"The best {plural} in Los Angeles, neighborhood by neighborhood, picked from critic reviews and real user tips."
    return head(title, desc, path, ld(crumbs_ld([("Home", "/"), ("Local LA", "/neighborhoods/"), (label, path)]))) + body


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
        f'<a class="gtile" href="/guide/{h["slug"]}/">{(ph_img(PHOTOS[h["slug"]][0][0], PHOTOS[h["slug"]][0][1], 700, 0.7, "(max-width:700px) 50vw, 25vw") if PHOTOS.get(h["slug"]) else aerial(*h["ll"], z=15, cols=3, rows=3, ts=200))}'
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
{lead_band("Buying or selling in LA?", "Get a free value on your home, or homes that fit, including off-market ones. You'll hear back today.")}
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
<div class="crumbs"><a href="/neighborhoods/">Local LA</a> / <a href="/neighborhoods/#articles">Articles</a> / {e(p['category'])}</div>
<h1>{e(p['title'])}</h1>
<div class="byline"><img src="{r}img/nate.jpg" alt=""><span>By <a href="{r}about/" style="color:inherit">Nathaniel Grivas</a>, REALTOR&reg;<br>{fmt_date(p['date'])}</span></div>
<div class="body">{p['body']}</div>
<div class="endcta"><h3>{e(t)}</h3><p class="muted" style="margin:0">{e(line)}</p>
<div class="cta-row" style="margin-top:4px"><a class="btn solid" href="tel:{TEL}">Call or text {PHONE}</a><a class="btn" href="#contact" data-msg>Send a message</a></div></div>
</div></article>
{tool_html}{hood_html}{rel_html}
{lead_band(first="value" if p.get('cta', 'buy') == "sell" else "buy")}
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
<h2>What is collected</h2>
<p><b>What you provide.</b> Your name, email, phone, the answers you choose or type in the search questions, a property address, and any message you send.</p>
<p><b>How you use the site.</b> The pages you view and for how long, the buttons you tap (for example Call, Text, a listing or a neighborhood), the website or ad that brought you here, and your device type, browser, screen width, language and time zone. Your browser keeps a random visitor ID and this visit's activity in local storage so repeat visits can be connected.</p>
<h2>When it is sent to Nathaniel</h2>
<p>Your activity is sent to Nathaniel by email when you send a form, when you tap Call, Text or Email, and when you leave after starting a search or showing interest without reaching out. If your browser sends a Global Privacy Control signal, activity alerts are not sent. Forms you send still include your activity.</p>
<h2>How it is used</h2>
<p>To reply to you, set up home searches and listing alerts, follow up about buying, selling, renting, investing or building, and improve this site. Your contact details and search may be added to Nathaniel's client records at Compass.</p>
<h2>Who it is shared with</h2>
<p>Nathaniel does not sell your information. It is shared with the services that run this site and deliver messages (Vercel for hosting, FormSubmit for form email), with Compass and The Brodsky Group to provide real estate services, and when the law requires it. Pages also load fonts and satellite maps from Google, neighborhood photos from Unsplash, aerial imagery from the U.S. Geological Survey, and a listing video from Vimeo when you scroll to it. These services receive standard web request data.</p>
<h2>Calls and texts</h2>
<p>If you send a form, you agree Nathaniel can contact you by call, text or email about real estate. Reply STOP to any text to opt out. Message and data rates may apply.</p>
<h2>Your choices</h2>
<p>Email Nathaniel to see, correct or delete what he has about you. You can also clear this site's storage in your browser settings at any time.</p>
<h2>Children</h2>
<p>This site is not meant for anyone under 16, and Nathaniel does not knowingly collect their information.</p>
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
<div class="cta-row"><a class="btn solid" href="/home-value/">What's my home worth?</a><a class="btn" href="/buy/">Find me a home</a><a class="btn" href="/neighborhoods/">Explore the map</a></div>
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
    return ", ".join(f'<a href="/neighborhoods/{h["slug"]}/">{e(h["name"])}</a>' for h in hs)


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
    return (f'<section class="band lux-band"><div class="wrap"><div class="lux-head"><p class="kick">LA News</p><h2>{e(name)} in the news</h2><a href="/news/">All LA news &rarr;</a></div>'
            f'<div class="jits">{"".join(jitem(it, d) for d, it in rows)}</div></div></section>')


def journal_teaser():
    if not JOURNAL:
        return ""
    j = JOURNAL[0]
    heads = "".join(f'<li>{e(it["h"])}</li>' for it in j["items"][:4])
    return zipper("/news/") + (f'<section class="band lux-band" style="padding-top:6px"><div class="wrap"><a class="jteaser" href="/news/">'
            f'<span class="kick">LA News &middot; {jdate(j["date"])}</span><b>{e(j["title"])}</b><span class="jt-d">{e(j["dek"])}</span>'
            f'<ul>{heads}</ul><span class="jt-go">Today, this week and this month in LA &rarr;</span></a></div></section>')


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
    body = f"""{nav(path, "news")}
<main>
<section class="ghero"><div class="wrap narrow">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/news/">LA News</a> / <span>{fmt_date(j["date"])}</span></nav>
<p class="kick">LA News &middot; {jdate(j["date"])}</p>
<h1 class="jh1">{e(j["title"])}</h1>
<p class="lede">{e(j["dek"])}</p>
<p class="gh-meta">By Nathaniel Grivas, REALTOR&reg; &middot; Written in plain English with links to the original reporting</p>
</div></section>
<div class="wrap narrow gbody"><section class="gsec"><h2 class="gsec-h">Today in LA</h2><div class="jits">{items}</div></section>{opens}{pn}</div>
<section class="band lux-band"><div class="wrap"><div class="gend">
<div><p class="kick">Where to go</p><h2>Local LA</h2><p>Hand-picked restaurants, bars and things to do in {len(GUIDES)} neighborhoods, pinned on a map and updated as places open and close.</p>
<div class="lh-cta"><a class="btn lux solid" href="/neighborhoods/">Open Local LA</a><a class="btn lux" href="/news/">Today in LA</a></div></div>
<div><p class="kick">Buying or selling?</p><h2>Talk to Nathaniel</h2><p>Off-market homes, lenders for any situation and creative deals. West LA, Beverly Hills and the Valley.</p>
<div class="lh-cta"><a class="btn lux solid" href="#lead" data-tabgo="v">What's my home worth?</a><a class="btn lux" href="#lead" data-tabgo="b">Find me a home</a></div></div>
</div></div></section>
{lead_band("Buying or selling in LA?", "Get a free value on your home, or homes that fit, including off-market ones. You'll hear back today.")}
</main>
{foot(path)}"""
    art = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": j["title"], "description": j["dek"],
           "datePublished": j["date"], "dateModified": j.get("updated", j["date"]),
           "author": {"@type": "Person", "name": "Nathaniel Grivas", "url": SITE + "/about/"},
           "publisher": {"@type": "Person", "name": "Nathaniel Grivas"}, "mainEntityOfPage": SITE + path}
    title = f"{j['title']} | LA News, {fmt_date(j['date'])}"
    return head(title, j["dek"], path, ld(art) + ld(crumbs_ld([("Home", "/"), ("LA News", "/news/"), (fmt_date(j["date"]), path)]))) + body


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
{lead_band("Buying or selling in LA?", "Get a free value on your home, or homes that fit, including off-market ones. You'll hear back today.")}
</main>
{foot(path)}"""
    desc = "The LA Journal by Nathaniel Grivas: a short daily roundup of Los Angeles news, new restaurant openings, events and real estate, with links to the original reporting."
    return head("The LA Journal: Daily Los Angeles News, Openings & Events | Nathaniel Grivas", desc, path, ld(crumbs_ld([("Home", "/"), ("The LA Guide", "/guide/"), ("The LA Journal", path)]))) + body


NEWS_F = ROOT / "src" / "news.json"
NEWS = json.loads(NEWS_F.read_text()) if NEWS_F.exists() else {}


def nitem(it, big=False):
    srcs = ", ".join(f'<a href="{u}" rel="noopener">{e(t)}</a>' for t, u in it.get("src", []))
    hs = jhoods(it.get("hoods"))
    when = fmt_date(it["date"]) + " &middot; " if it.get("date") else ""
    return (f'<article class="jit{" nlead" if big else ""}"><p class="jit-t">{e(it.get("tag", "LA"))}</p><h3>{e(it["h"])}</h3><p class="jit-b">{e(it["t"])}</p>'
            f'<p class="jit-f">{when}{("Neighborhoods: " + hs + " &middot; ") if hs else ""}{("Sources: " + srcs) if srcs else ""}</p></article>')


def ticker_items():
    """Headlines for the moving ticker: the month's headline, today, the week, then the month."""
    out = []
    mo, wk = NEWS.get("month", {}), NEWS.get("week", {})
    if mo.get("lead"):
        out.append(("The headline", mo["lead"]["h"], "lead"))
    if JOURNAL:
        out += [(it.get("tag", "LA"), it["h"], f"t{i}") for i, it in enumerate(JOURNAL[0]["items"])]
    th = {it["h"] for it in (JOURNAL[0]["items"] if JOURNAL else [])}
    out += [(it.get("tag", "LA"), it["h"], f"w{i}") for i, it in enumerate([x for x in wk.get("items", []) if x["h"] not in th])]
    out += [(it.get("tag", "LA"), it["h"], f"m{i}") for i, it in enumerate(mo.get("items", []))]
    seen, uniq = set(), []
    for t, h, a in out:
        if h not in seen:
            seen.add(h)
            uniq.append((t, h, a))
    return uniq


def zipper(base="", label="LA News"):
    """The moving headline ticker, styled like the old Times Square news zipper."""
    items = ticker_items()
    if not items:
        return ""
    run = "".join(f'<a href="{base}#{a}"><b>{e(t)}</b>{e(h)}</a>' for t, h, a in items)
    secs = max(40, sum(len(h) for _, h, _ in items) // 5)
    return (f'<div class="zip" role="region" aria-label="Latest Los Angeles headlines"><a class="zip-l" href="/news/"><i aria-hidden="true"></i>{e(label)}</a>'
            f'<div class="zip-w"><div class="zip-r" style="--zd:{secs}s"><div class="zip-s">{run}</div><div class="zip-s" aria-hidden="true">{run}</div></div></div></div>')


def nstory(it, aid, cls="", photo=False, drop=False):
    srcs = ", ".join(f'<a href="{u}" rel="noopener">{e(t)}</a>' for t, u in it.get("src", []))
    hs = jhoods(it.get("hoods"))
    meta = " &middot; ".join(x for x in ((fmt_date(it["date"]) if it.get("date") else ""), (hs if hs else "")) if x)
    fig = ""
    if photo:
        for s_ in it.get("hoods") or []:
            ph = PHOTOS.get(s_)
            if ph:
                fig = (f'<figure class="ns-fig">{ph_img(ph[0][0], ph[0][1], 1100, 0.6, "(max-width:900px) 92vw, 46vw")}'
                       f'<figcaption>{e(ph[0][1])}. File photo of {e(BY_SLUG[s_]["name"])} via Unsplash, not of the news event.</figcaption></figure>')
                break
    return (f'<article class="ns {cls}" id="{aid}">{fig}<p class="ns-tag">{e(it.get("tag", "LA"))}</p><h3>{e(it["h"])}</h3>'
            f'{("<p class=ns-meta>" + meta + "</p>") if meta else ""}<p class="ns-b{" drop" if drop else ""}">{e(it["t"])}</p>'
            f'{("<p class=ns-src>Sources: " + srcs + "</p>") if srcs else ""}</article>')


def history_desk(n=3):
    """Three did-you-know facts from the neighborhood histories, rotating by day."""
    pool = [(s_, q, a) for s_, hx in HIST.items() if s_ in BY_SLUG for q, a in hx.get("dyk", [])]
    if not pool:
        return ""
    day = datetime.date.today().toordinal()
    pick = [pool[(day * 7 + k * 11) % len(pool)] for k in range(min(n, len(pool)))]
    seen, cards = set(), ""
    for s_, q, a in pick:
        if q in seen:
            continue
        seen.add(q)
        cards += (f'<a class="hd-c" href="/neighborhoods/{s_}/#history"><span class="hd-h">{e(BY_SLUG[s_]["name"])}</span><b>{e(q)}</b>'
                  f'<span class="hd-a">{e(a)}</span><i>Read the full story &rarr;</i></a>')
    return cards


def page_news():
    path = "/news/"
    j = JOURNAL[0] if JOURNAL else None
    wk, mo = NEWS.get("week", {}), NEWS.get("month", {})
    day = datetime.date.fromisoformat(j["date"] if j else NEWS.get("updated"))
    issue = len(JOURNAL)
    # the front page: month's headline on the left, today's briefing on the right
    lead = mo.get("lead")
    lead_html = ""
    today_heads = {it["h"] for it in (j["items"] if j else [])}
    wk_items = [it for it in wk.get("items", []) if it["h"] not in today_heads]
    more = ""
    if wk_items:
        more = (f'<div class="np-more" id="week"><p class="np-label">The week in LA &middot; {e(wk["label"])}</p>'
                f'<div class="np-grid cols2">{"".join(nstory(it, f"w{i}", photo=True) for i, it in enumerate(wk_items))}</div></div>')
    if lead:
        srcs = ", ".join(f'<a href="{u}" rel="noopener">{e(t)}</a>' for t, u in lead.get("src", []))
        lead_html = (f'<div class="np-lead" id="lead"><p class="np-label">The headline &middot; {e(mo["label"])}</p>'
                     f'<h1>{e(lead["h"])}</h1><p class="np-by">By Nathaniel Grivas, from public reporting &middot; {fmt_date(lead["date"]) if lead.get("date") else ""}</p>'
                     f'<p class="np-body drop">{e(lead["t"])}</p>{("<p class=ns-src>Sources: " + srcs + "</p>") if srcs else ""}{more}</div>')
    brief = ""
    if j:
        lis = "".join(f'<li><a href="#t{i}"><span>{e(it.get("tag", "LA"))}</span>{e(it["h"])}</a></li>' for i, it in enumerate(j["items"]))
        brief = (f'<aside class="np-brief"><p class="np-label">Today&rsquo;s briefing</p><p class="np-bt">{e(j["title"])}</p><ol>{lis}</ol>'
                 f'<a class="np-jump" href="#today">Read today&rsquo;s edition &darr;</a></aside>')
    today = ""
    if j:
        stories = "".join(nstory(it, f"t{i}", "big" if i == 0 else "", photo=(i == 0), drop=(i == 0)) for i, it in enumerate(j["items"]))
        opens = ""
        if j.get("openings"):
            opens = "".join(f'<div class="cl"><b>{e(o["n"])}</b><p>{e(o["w"])}</p>'
                            f'<span>{(jhoods([o.get("hood")]) + " &middot; ") if o.get("hood") else ""}'
                            f'{("<a href=" + chr(34) + o["src"][1] + chr(34) + " rel=noopener>" + e(o["src"][0]) + "</a>") if o.get("src") else ""}</span></div>'
                            for o in j["openings"])
            opens = f'<section class="np-sec np-class" id="openings"><h2 class="np-sh"><span>New openings</span><small>Just opened around town</small></h2><div class="cls">{opens}</div></section>'
        today = (f'<section class="np-sec" id="today"><h2 class="np-sh"><span>Today</span><small>{jdate(j["date"])}</small></h2>'
                 f'<p class="np-dek">{e(j["dek"])}</p><div class="np-grid">{stories}</div></section>{opens}')
    week = more
    month = ""
    if mo.get("items"):
        month = (f'<section class="np-sec" id="month"><h2 class="np-sh"><span>Also this month</span><small>{e(mo["label"])}</small></h2>'
                 f'<div class="np-grid cols3">{"".join(nstory(it, f"m{i}") for i, it in enumerate(mo["items"]))}</div></section>')
    desk = history_desk()
    desk = (f'<section class="np-sec np-desk" id="history-desk"><h2 class="np-sh"><span>From the history desk</span><small>Local LA, then and now</small></h2>'
            f'<div class="hd">{desk}</div></section>') if desk else ""
    past = "".join(f'<a class="np-ed" href="/journal/{x["date"]}/"><span>{fmt_date(x["date"])}</span><b>{e(x["title"])}</b></a>' for x in JOURNAL[1:31])
    past = (f'<section class="np-sec" id="archive"><h2 class="np-sh"><span>Previous editions</span><small>Every day, archived</small></h2>'
            f'<div class="np-eds">{past}</div></section>') if past else ""
    secs = [("lead", "Front page", lead_html), ("today", "Today", today), ("openings", "Openings", j and j.get("openings")),
            ("week", "The week", week), ("month", "The month", month), ("history-desk", "History desk", desk), ("archive", "Archive", past)]
    secnav = "".join(f'<a href="#{k}">{t}</a>' for k, t, ok in secs if ok)
    body = f"""{nav(path, "news")}
{zipper()}
<main class="np">
<div class="wrap">
<article class="paper">
<header class="np-mast">
<div class="np-ear"><b>Late edition</b><span>{day.strftime("%A")}</span><span>Updated daily</span></div>
<div class="np-name"><span class="np-the">The</span>Local LA Ledger</div>
<div class="np-ear r"><b>Free</b><span>Facts only</span><span>Every story sourced</span></div>
</header>
<p class="np-motto">All the facts from across Los Angeles, none of the spin</p>
<div class="np-date"><span>Vol. I &middot; No. {issue}</span><span>Los Angeles, {jdate(day.isoformat())}</span><span>Compiled by Nathaniel Grivas</span></div>
<nav class="np-secs" aria-label="Sections">{secnav}</nav>
<section class="np-front">{lead_html}{brief}</section>
{today}
{month}
{desk}
{past}
<footer class="np-foot"><p>The Local LA Ledger is written by Nathaniel Grivas, REALTOR&reg; with The Brodsky Group at Compass Beverly Hills, from public reporting. Facts only: no endorsements, no predictions, and every story links to its sources so you can read them yourself. See something wrong? <a href="mailto:{EMAIL}">Email Nathaniel</a> and he&rsquo;ll fix it.</p></footer>
</article>
</div>
</main>
{lead_band("Buying or selling in LA?", "Get a free value on your home, or homes that fit, including off-market ones. You'll hear back today.")}
{foot(path, (), "news")}"""
    desc = "The Local LA Ledger: today's Los Angeles news, the week's biggest stories and the month's headline, written as plain facts with links to the original reporting."
    coll = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "The Local LA Ledger: LA News", "url": SITE + path, "description": desc,
            "dateModified": NEWS.get("updated") or (j["date"] if j else "")}
    fonts = ('<link href="https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Playfair+Display:ital,wght@0,700;0,900;1,700&display=swap" rel="stylesheet">')
    return head("LA News Today: The Local LA Ledger | This Week & This Month in Los Angeles", desc, path,
                ld(coll) + ld(crumbs_ld([("Home", "/"), ("LA News", path)])) + fonts) + body


# ------------------------------------------------------------------ speed: versioned assets, WebP images, non-blocking fonts
import hashlib  # noqa: E402

def asset_version():
    """Short hash of everything under assets/ plus the data that feeds the JSON files. Fresh sessions without assets/ reuse the saved one."""
    saved = pathlib.Path(__file__).parent / "asset_ver.txt"
    a = ROOT / "assets"
    if not a.exists():
        return saved.read_text().strip() if saved.exists() else "1"
    h = hashlib.sha1()
    for f in sorted(a.rglob("*")):
        if f.is_file() and f.suffix in (".css", ".js", ".svg"):
            h.update(f.name.encode()); h.update(f.read_bytes())
    for f in sorted((pathlib.Path(__file__).parent / "pockets").glob("*")) + [pathlib.Path(__file__).parent / "hoods.py"]:
        if f.is_file():
            h.update(f.read_bytes())
    v = h.hexdigest()[:10]
    saved.write_text(v + "\n")
    return v


def make_webp():
    """WebP copies of the site's own JPGs (kept next to them in img/). The list is saved so a fresh session builds the same HTML."""
    saved = pathlib.Path(__file__).parent / "webp.txt"
    img = ROOT / "img"
    if not img.exists():
        return set(saved.read_text().split()) if saved.exists() else set()
    from PIL import Image
    out = set()
    for f in sorted(img.rglob("*.jpg")):
        w = f.with_suffix(".webp")
        if not w.exists() or w.stat().st_mtime < f.stat().st_mtime:
            im = Image.open(f)
            im = im.convert("RGB")
            if im.width > 2000:
                im = im.resize((2000, round(im.height * 2000 / im.width)), Image.LANCZOS)
            im.save(w, "WEBP", quality=78, method=6)
        if w.stat().st_size < f.stat().st_size:
            out.add("/" + str(f.relative_to(ROOT)))
    saved.write_text("\n".join(sorted(out)) + "\n")
    return out


FONT_LINK = re.compile(r'<link href="(https://fonts\.googleapis\.com/css2\?[^"]+)" rel="stylesheet">')
LEAF_CSS = re.compile(r'<link rel="stylesheet" href="(/assets/vendor/leaflet\.css[^"]*)">')
ASSET_REF = re.compile(r'((?:src|href)="/assets/[^"?#]+\.(?:css|js|svg))"')
IMG_ATTR = re.compile(r'((?:src|srcset|data-full|poster|data-src)=")([^"]+)(")')


def speed(t, v, webp):
    t = ASSET_REF.sub(lambda m: f'{m.group(1)}?v={v}"', t)
    t = t.replace('<meta charset="utf-8">', f'<meta charset="utf-8">\n<meta name="ng-v" content="{v}">', 1)
    t = FONT_LINK.sub(lambda m: f'<link rel="preload" as="style" href="{m.group(1)}" onload="this.onload=null;this.rel=\'stylesheet\'"><noscript><link rel="stylesheet" href="{m.group(1)}"></noscript>', t)
    t = LEAF_CSS.sub(lambda m: f'<link rel="stylesheet" href="{m.group(1)}" media="print" onload="this.media=\'all\'">', t)
    if webp:
        def sw(m):
            val = re.sub(r'(/img/[^"\s,?]+\.jpg)', lambda x: x.group(1)[:-4] + ".webp" if x.group(1) in webp else x.group(1), m.group(2))
            return m.group(1) + val + m.group(3)
        t = IMG_ATTR.sub(sw, t)
    return t


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
        "/listings/": page_listings(), "/market-temperature/": page_market(), "/about/": page_about(), "/news/": page_news(), "/privacy/": page_privacy(),
        "/homes/3721-evans/": page_featured("evans"), "/homes/616-fuller/": page_featured("fuller"),
        "/homes/18748-lanark/": page_deal("lanark"), "/homes/14757-hartland/": page_deal("hartland"),
        VALUE_URL: page_value(), BUY_URL: page_buy(), RENT_URL: page_rent(), "/neighborhoods/map/": page_pocketmap(),
    }
    (DIST / "assets" / "pockets.json").write_text(json.dumps(pockets_json(), separators=(",", ":")))
    (DIST / "assets" / "areas.json").write_text(json.dumps(areas_json(), separators=(",", ":")))
    for h in HOODS:
        pages[f"/neighborhoods/{h['slug']}/"] = page_hood(h, posts)
    for p in posts:
        pages[f"/guide/{p['slug']}/"] = page_post(p, posts)
    for k, n in guide_counts().items():
        if n >= 3:
            pages[f"/guide/best/{k}/"] = page_best(k)
    if JOURNAL:
        for i, j in enumerate(JOURNAL):
            pages[f"/journal/{j['date']}/"] = page_journal_day(j, JOURNAL[i - 1] if i > 0 else None, JOURNAL[i + 1] if i + 1 < len(JOURNAL) else None)
    V, WEBP = asset_version(), make_webp()
    if (ROOT / "img").exists():
        shutil.rmtree(DIST / "img"); shutil.copytree(ROOT / "img", DIST / "img")
    pages = {u: speed(t, V, WEBP) for u, t in pages.items()}
    for u, t in pages.items():
        write(u, t)
    (DIST / "404.html").write_text(ext_tabs(speed(page_404(), V, WEBP)))
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
    (DIST / "robots.txt").write_text(robots_txt())
    mds = text_twins(pages, posts)
    (DIST / "llms.txt").write_text(llms_txt(posts))
    (DIST / "llms-full.txt").write_text(llms_full(posts, mds))
    (DIST / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)
    (DIST / "assets" / "search.json").write_text(json.dumps(search_index(posts), separators=(",", ":")))
    export_deploy(pages, today)
    print(f"built {len(pages)} pages, {len(posts)} posts, {len(HOODS)} neighborhoods")


TRAIL = re.compile(r'(="(?:https://www\.nathanielgrivas\.com)?/[^"?#\s]+)/(?=[?#"])')
TRAIL_JSON = re.compile(r'("https://www\.nathanielgrivas\.com/[^"?#\s]+)/(?=")')


def flat(text):
    return TRAIL_JSON.sub(r"\1", TRAIL.sub(r"\1", text))


def redirects(pages):
    """Old URLs from before Local LA merged the guide into the neighborhood pages."""
    out = [{"source": "/guide", "destination": "/neighborhoods", "permanent": True},
           {"source": "/rent", "destination": "/lease", "permanent": True},
           {"source": "/rent.md", "destination": "/lease.md", "permanent": True},
           {"source": "/journal", "destination": "/news", "permanent": True}]
    for k in GUIDES:
        if k in BY_SLUG:
            out.append({"source": f"/guide/{k}", "destination": f"/neighborhoods/{k}", "permanent": True})
            out.append({"source": f"/guide/{k}.md", "destination": f"/neighborhoods/{k}.md", "permanent": True})
    for k in list(G.CATS) + ["dive", "sports", "beer"]:
        if f"/guide/best/{k}/" not in pages:
            out.append({"source": f"/guide/best/{k}", "destination": "/guide/best/bars" if k in ("dive", "sports", "beer") else "/neighborhoods", "permanent": True})
    return out


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
        "headers": [
            {"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
            {"source": "/img/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=604800, stale-while-revalidate=2592000"}]},
        ],
        "redirects": [{"source": "/", "has": [{"type": "host", "value": "nathanielgrivas.vercel.app"}], "destination": "/links", "permanent": False}] + redirects(pages),
    }, indent=2))
    sm = "".join(f"<url><loc>{SITE}{u.rstrip('/') if u != '/' else '/'}</loc><lastmod>{today}</lastmod></url>" for u in pages)
    (out / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    (out / "robots.txt").write_text(robots_txt())
    for name in ("llms.txt", "llms-full.txt"):
        (out / name).write_text(flat_txt((DIST / name).read_text()))
    (out / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)
    for u in pages:
        src = DIST / md_url(u).lstrip("/")
        if src.exists():
            dst = out / md_url(u).lstrip("/")
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(flat_txt(src.read_text()))


def flat_txt(text):
    text = re.sub(r"(https://www\.nathanielgrivas\.com/[^)\s]+)/\)", r"\1)", text)
    return re.sub(r"(https://www\.nathanielgrivas\.com/[^\s)]+)/(?=[\s.,;]|$)", r"\1", text, flags=re.M)


INDEXNOW_KEY = "7c1f4e2a9b8d4f6e8a3c5d7e9f1b2c4d"
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "anthropic-ai", "PerplexityBot",
           "Perplexity-User", "Google-Extended", "Googlebot", "Bingbot", "Applebot", "Applebot-Extended", "DuckAssistBot", "meta-externalagent",
           "Amazonbot", "MistralAI-User", "cohere-ai", "YouBot", "CCBot"]


def robots_txt():
    bots = "".join(f"User-agent: {b}\nAllow: /\n\n" for b in AI_BOTS)
    return (f"# Search engines and AI assistants are welcome to read and cite this site.\n"
            f"# Plain-text summary for AI: {SITE}/llms.txt  Full text: {SITE}/llms-full.txt\n\n"
            f"User-agent: *\nAllow: /\n\n{bots}Sitemap: {SITE}/sitemap.xml\n")


MD_FOOT = (f"\n---\n\nNathaniel Grivas, REALTOR\u00ae (California DRE #{DRE}), The Brodsky Group at Compass Beverly Hills, {ADDR}. "
           f"Rated 5.0 on Google. Call or text {PHONE}, email {EMAIL}. Website: {SITE}/  Summary for AI: {SITE}/llms.txt\n")


def hood_summary_md(u):
    """Answer-first block at the top of each neighborhood's text twin."""
    m = re.fullmatch(r"/neighborhoods/([a-z0-9-]+)/", u)
    if not m or m.group(1) not in BY_SLUG:
        return ""
    h = BY_SLUG[m.group(1)]
    n, c = h["name"], CITIES[h["city"]]
    pk = [p["n"] for p in pocket_items(h["slug"])]
    deals = [PROPS[k] for k in DEALS.get(h["slug"], [])]
    lines = ["## In short", "",
             f"- {n} is in {('the ' + c['label']) if c['label'].startswith(('City', 'Unincorporated')) else c['label']}, {'ZIPs' if ',' in h['zips'] else 'ZIP'} {h['zips']} (region: {h['region']}). {h['line']}",
             f"- Price level: {TIER_WORD[h['tier']]}. Good fit if: {h['fit']}"]
    if pk:
        lines.append(f"- {n} breaks into {len(pk)} pockets, mapped street by street: {', '.join(pk)}.")
    lines.append(f"- Local real estate agent: Nathaniel Grivas, REALTOR\u00ae (California DRE #{DRE}) with The Brodsky Group at Compass Beverly Hills, "
                 f"buys, sells and leases homes in {n}. Call or text {PHONE}.")
    for p_ in deals:
        lines.append(f"- His {n} deal: {p_['addr']} ({p_['tag'].lower()}, {p_['price']}{p_.get('per', '')}" + (f", represented the {p_['rep'].lower()})" if p_.get("rep") else ")"))
    lines += [f"- Free home valuation in {n}: {SITE}{VALUE_URL}",
              f"- This week's market by region: {SITE}{MARKET_URL}", "", ""]
    return "\n".join(lines)


def text_twins(pages, posts):
    """Writes a markdown version of every page next to it (page.md) so AI readers get the full text fast."""
    out = {}
    for u, t in pages.items():
        m = re.search(r"<title>(.*?)</title>", t, re.S)
        title = html.unescape(m.group(1)) if m else u
        if u == "/":
            md = home_md(posts)
        else:
            body_md = v8.html_to_md(t, SITE)
            body_md = re.sub(r"(?m)^(?:Call|Text|Message)(?: (?:Call|Text|Message))*\s*$\n?", "", body_md)
            body_md = re.sub(r"(?m)^Get [^.\n]{0,60} listings What's my [^.\n]{0,60} home worth\?\s*$\n?", "", body_md)
            body_md = re.sub(r"\n{3,}", "\n\n", body_md)
            md = f"# {title}\n\nSource page: {SITE}{u}\n\n" + hood_summary_md(u) + body_md
        md += MD_FOOT
        f = DIST / md_url(u).lstrip("/")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(md)
        out[u] = md
    return out


def llms_full(posts, mds):
    keep = ["/", "/about/", "/home-value/", "/buy/", RENT_URL, MARKET_URL, "/listings/", "/homes/3721-evans/", "/homes/616-fuller/", "/homes/18748-lanark/", "/homes/14757-hartland/", "/neighborhoods/"] + \
           [f"/neighborhoods/{h['slug']}/" for h in ORDER] + [f"/guide/{p['slug']}/" for p in posts]
    parts = [llms_txt(posts), "\n\n# Full text of the main pages\n"]
    for u in keep:
        if u in mds:
            parts.append(f"\n\n<!-- {SITE}{u} -->\n\n" + mds[u])
    return "".join(parts)


def search_index(posts):
    out = []
    for h in ORDER:
        out.append({"t": h["name"], "s": f"{h['region']} \u00b7 {CITIES[h['city']]['short']} \u00b7 {h['zips']}", "u": f"/neighborhoods/{h['slug']}/",
                    "k": " ".join([h["zips"], h["region"], CITIES[h["city"]]["label"], " ".join(TAGS[t] for t in h["tags"]), " ".join(k for k, _ in h["know"])]), "g": "Neighborhoods"})
    for s_, t, d, _ in TOOLS:
        out.append({"t": t, "s": d, "u": f"/tools/{s_}/", "k": "calculator tool", "g": "Tools"})
    for p in posts:
        out.append({"t": p["title"], "s": p["category"], "u": f"/guide/{p['slug']}/", "k": p["description"], "g": "Articles"})
    for k in ACTIVE + SOLD:
        pr = PROPS[k]
        out.append({"t": pr["addr"], "s": f"{pr['tag']} \u00b7 {pr['price']} \u00b7 {pr['area']}", "u": pr.get("page") or pr["url"], "k": "listing home sold", "g": "Listings"})
    out = [{"t": "What's my home worth?", "s": "Free home valuation, within 24 hours", "u": VALUE_URL, "k": "sell selling value valuation worth price cma appraisal estimate", "g": "Start here"},
           {"t": "Find me a home", "s": "New, coming-soon and off-market homes", "u": BUY_URL, "k": "buy buying search listings off-market lender preapproved", "g": "Start here"},
           {"t": "Lease a home, or lease yours out", "s": "Lease search and free lease estimates", "u": RENT_URL, "k": "rent rental lease leasing apartment tenant landlord for lease", "g": "Start here"}] + out
    out += [{"t": "Local LA", "s": "Restaurants, bars and things to do in 40 neighborhoods", "u": "/neighborhoods/", "k": "guide restaurants bars nightlife things to do map", "g": "Pages", "i": "P"},
            {"t": "LA News", "s": "Today, this week and this month in LA", "u": "/news/", "k": "news journal today mayor election", "g": "Pages", "i": "P"},
            {"t": "About Nathaniel", "s": "REALTOR\u00ae at Compass", "u": "/about/", "k": "agent bio", "g": "Pages", "i": "P"},
            {"t": "Contact", "s": "Call, text or send a message", "u": "/#contact", "k": "phone email", "g": "Pages", "i": "P"},
            {"t": "The Brodsky Group", "s": "His team at Compass Beverly Hills", "u": BG, "k": "team or brodsky", "g": "Pages", "i": "P"},
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
        "", "## Articles", ""] + [f"- [{p['title']}]({SITE}/guide/{p['slug']}/): {p['description']}" for p in posts]
    return "\n".join(out) + "\n"


def market_ai_lines():
    try:
        M = json.loads((pathlib.Path(__file__).parent / "market" / "latest.json").read_text())
    except Exception:
        return []
    rg = M["regions"]; a = sum(x["active"] for x in rg); c = sum(x["cut"] for x in rg)
    R, C = M["rate"], M["county"]
    wk = datetime.date.fromisoformat(M["week"]).strftime("%B %-d, %Y")
    out = ["", f"## Los Angeles housing market this week (Market Temperature, week of {wk}, updated weekly)", "",
           f"- Source page: {SITE}{MARKET_URL}",
           f"- 30-year fixed mortgage rate: {R['v']:.2f}% ({R['src']}, {R['asof']}), {R['prev']:.2f}% the week before, {R['yago']:.2f}% a year ago",
           f"- Homes for sale across the 40 neighborhoods covered: {a:,}; {100.0 * c / a:.1f}% have had a price cut ({c:,} listings)"]
    out += [f"- {x['r']}: {x['active']:,} for sale, {100.0 * x['cut'] / max(1, x['active']):.1f}% with a price cut" for x in sorted(rg, key=lambda x: x["cut"] / max(1, x["active"]))]
    out += [f"- Los Angeles County median price, {C['month']}: ${C['price']:,} ({C['price_yoy']:+.1f}% year over year); closed sales {C['sales_yoy']:+.1f}% year over year ({C['src']})",
            f"- Listing counts: {M.get('listings_src', 'public listing data')}"]
    return out


def llms_txt(posts):
    lines = ["# Nathaniel Grivas, REALTOR® in Los Angeles", "",
             f"> Nathaniel Grivas is a Los Angeles REALTOR® (California DRE #{DRE}) with The Brodsky Group at Compass Beverly Hills, {ADDR}. "
             "He helps people buy, sell, rent, invest and build across West Los Angeles, Beverly Hills, the Hollywood Hills, Central LA, "
             f"the Eastside and the San Fernando Valley. Rated 5.0 on Google. His team does over $100M in annual sales. Call or text {PHONE}, email {EMAIL}.", "",
             "Every page on this site has a plain-text twin: add .md to the address (for example /neighborhoods/venice.md). "
             f"Everything in one file: {SITE}/llms-full.txt", "",
             "## Key facts", ""]
    lines += [f"- {k}: {v}" for k, v in agent_facts()]
    lines += ["", f"## Client reviews (Google, {v8.RATING} stars, read them at {GBP_URL})", ""]
    lines += [f"- {r_['name']}, {r_['who']}, 5 stars, {r_['when']}: “{r_['text']}”" for r_ in v8.REVIEWS]
    lines += ["", "## Main pages", "",
              f"- [Free home valuation]({SITE}{VALUE_URL}): what a Los Angeles home is worth, built by hand from recent sales, within 24 hours",
              f"- [Find a home]({SITE}{BUY_URL}): buyer search with off-market homes, lenders for every situation and creative financing",
              f"- [Lease]({SITE}{RENT_URL}): homes for lease, a lease search for tenants and a free lease estimate for owners",
              f"- [About Nathaniel Grivas]({SITE}/about/): background, quick facts, team, reviews",
              f"- [Listings]({SITE}/listings/): active listings and closed deals",
              f"- [All 40 neighborhoods on a satellite map]({SITE}/neighborhoods/)",
              f"- [Local LA]({SITE}/neighborhoods/): where to eat, drink and go in each neighborhood, every pick pinned on a map",
              f"- [Market Temperature]({SITE}{MARKET_URL}): the Los Angeles housing market this week, by region, updated weekly from public data",
              f"- [LA News]({SITE}/news/): today's Los Angeles news, the week's biggest stories and the month's headline, facts only"]
    lines += market_ai_lines()
    lines += ["", "## Listings and closed deals", ""]
    for k in ACTIVE + SOLD:
        p_ = PROPS[k]
        rep_ = f", represented the {p_['rep'].lower()}" if p_.get("rep") else ""
        lines.append(f"- [{p_['addr']}, {p_['area']}]({SITE + p_['page'] if p_.get('page') else p_.get('site') or p_['url']}): {p_['tag']}, {p_['price']}{p_.get('per', '')}{rep_}" + (" (video tour on the page)" if k in FEATURED else (f". {DEAL_PAGES[k]['ai']}" if k in DEAL_PAGES else "")))
    lines += ["", "## Neighborhoods he works in (each page: satellite map, photos, places, rules, FAQ)", ""]
    lines += [f"- [{h['name']}]({SITE}/neighborhoods/{h['slug']}/): {h['line']} {CITIES[h['city']]['label']}, ZIP {h['zips']}." for h in ORDER]
    lines += ["", "## Local LA: where to eat, drink and go (on each neighborhood page, with a map of every pick)", ""]
    lines += [f"- [{BY_SLUG[k]['name']}: restaurants, bars and things to do]({SITE}/neighborhoods/{k}/): {len(d['places'])} hand-picked places" for k, d in GUIDES.items() if k in BY_SLUG]
    lines += ["", "## Local LA: best of LA by category", ""]
    lines += [f"- [Best {G.CATS[k][1]} in LA]({SITE}/guide/best/{k}/)" for k in G.ORDERED if guide_counts().get(k, 0) >= 3]
    if NEWS.get("month", {}).get("lead"):
        ml = NEWS["month"]["lead"]
        lines += ["", f"## LA News: the headline for {NEWS['month']['label']}", "", f"- {ml['h']}: {ml['t']}"]
    if JOURNAL:
        lines += ["", "## LA News: daily Los Angeles news and openings", "", f"- [Today, this week and this month]({SITE}/news/)"]
        lines += [f"- [{j['title']}]({SITE}/journal/{j['date']}/) ({j['date']}): {j['dek']}" for j in JOURNAL[:30]]
    lines += ["", "## Tools", ""] + [f"- [{t}]({SITE}/tools/{s}/): {d}" for s, t, d, _ in TOOLS]
    lines += ["", "## Articles", ""] + [f"- [{p['title']}]({SITE}/guide/{p['slug']}/): {p['description']}" for p in posts]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
