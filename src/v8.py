"""v8 components: Google reviews, real aerial imagery, satellite maps, FAQs and AI-readable text twins."""
import html
import math
import re
from html.parser import HTMLParser
from urllib.parse import quote_plus

e = html.escape

# ------------------------------------------------------------------ reviews
GBP_URL = "https://share.google/EwuPsirAOfl9Hvj1o"
RATING = "5.0"
REVIEWS = [
    dict(name="Willy Blasquez", who="Home seller, Reseda", when="November 2026",
         short="He did an outstanding job marketing the property, generating multiple offers within the very first week it was on the market.",
         text=("We had a great experience working with our realtor, Nate [Grivas] in selling our Reseda property. He did an outstanding job "
               "marketing the property, generating multiple offers within the very first week it was on the market. His communication and "
               "coordination skills were excellent, keeping us informed throughout the entire process and making sure everything moved smoothly. "
               "Selling a property can be stressful, especially when multiple parties are involved, but he handled everything with confidence, "
               "responsiveness, and attention to detail. We truly appreciate his hard work and commitment and would gladly recommend him to anyone "
               "looking for a hardworking, dependable, and capable real estate agent. He definitely has a bright future ahead of him!")),
    dict(name="Nathan Agam", who="Home seller, Los Angeles", when="November 2026",
         short="He was professional, timely, persistent and patient in helping get the sale closed.",
         text=("My team and I had the opportunity to work with Nate representing us in a sale of a property in Los Angeles. He was professional, "
               "timely, persistent and patient in helping get the sale closed. We look forward to working with him again on other transactions.")),
]
STAR = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 1.6l2.6 5.3 5.8.8-4.2 4.1 1 5.8L10 14.9l-5.2 2.7 1-5.8L1.6 7.7l5.8-.8z"/></svg>'


def stars(n=5):
    return f'<span class="stars" role="img" aria-label="{n} out of 5 stars">{STAR * n}</span>'


def trust_row(cls=""):
    return (f'<div class="trust{(" " + cls) if cls else ""}">'
            f'<a class="trust-g" href="{GBP_URL}" target="_blank" rel="noopener">{stars()}<b>{RATING}</b><span>on Google</span></a>'
            f'<span class="trust-i">$100M+ in annual team sales</span><span class="trust-i">Compass Beverly Hills</span></div>')


def review_card(r, full=True):
    words = r["text"] if full else r["short"]
    return (f'<figure class="rv-card">{stars()}<blockquote><p>&ldquo;{e(words)}&rdquo;</p></blockquote>'
            f'<figcaption><span class="rv-av" aria-hidden="true">{e(r["name"][0])}</span><span><b>{e(r["name"])}</b>'
            f'<small>{e(r["who"])} &middot; Google review, {e(r["when"])}</small></span></figcaption></figure>')


def reviews_band(full=True, heading="What my clients say", cls=""):
    return f"""<section class="band rv{(" " + cls) if cls else ""}" id="reviews"><div class="wrap">
<div class="rv-head"><div><p class="kick">Reviews</p><h2>{e(heading)}</h2></div>
<a class="rv-score" href="{GBP_URL}" target="_blank" rel="noopener"><b>{RATING}</b><span>{stars()}<small>{len(REVIEWS)} Google reviews &middot; read them on Google &#8599;</small></span></a></div>
<div class="rv-grid">{"".join(review_card(r, full) for r in REVIEWS)}</div>
</div></section>"""


# ------------------------------------------------------------------ aerial imagery (USGS, public domain)
USGS = "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"


def tile_xy(lat, lng, z):
    n = 2 ** z
    x = (lng + 180) / 360 * n
    lr = math.radians(lat)
    y = (1 - math.log(math.tan(lr) + 1 / math.cos(lr)) / math.pi) / 2 * n
    return x, y


def aerial(lat, lng, z=15, cols=3, rows=3, ts=200, cls="", eager=False, label=""):
    """A real aerial photo of the spot, stitched from USGS tiles and centered on it."""
    x, y = tile_xy(lat, lng, z)
    x0, y0 = int(x) - cols // 2, int(y) - rows // 2
    ox, oy = x - x0, y - y0
    ld = 'fetchpriority="high"' if eager else 'loading="lazy"'
    imgs = "".join(f'<img src="{USGS.format(z=z, x=x0 + c, y=y0 + r)}" alt="" {ld} decoding="async">'
                   for r in range(rows) for c in range(cols))
    aria = f' role="img" aria-label="{e(label)}"' if label else ' aria-hidden="true"'
    return (f'<div class="aerial{(" " + cls) if cls else ""}" style="--ts:{ts}px"{aria}>'
            f'<div class="aer-g" style="grid-template-columns:repeat({cols},var(--ts));left:calc(50% - {ox:.4f} * var(--ts));top:calc(50% - {oy:.4f} * var(--ts))">{imgs}</div>'
            f'<span class="aer-pin" aria-hidden="true"></span><span class="aer-cr">Imagery: USGS</span></div>')


# ------------------------------------------------------------------ satellite map (Google Maps embed, satellite view)
GQ = {
    "santa-monica": "Santa Monica, CA", "malibu": "Malibu, CA", "culver-city": "Culver City, CA", "beverly-hills": "Beverly Hills, CA",
    "west-hollywood": "West Hollywood, CA", "marina-del-rey": "Marina del Rey, CA", "west-la": "Sawtelle, Los Angeles, CA",
    "cheviot-hills": "Cheviot Hills, Los Angeles, CA", "pico-robertson": "Pico-Robertson, Los Angeles, CA",
    "bhpo": "Beverly Crest, Los Angeles, CA", "fairfax": "Fairfax, Los Angeles, CA", "hancock-park": "Hancock Park, Los Angeles, CA",
}


def gquery(h):
    return GQ.get(h["slug"], f"{h['name']}, Los Angeles, CA")


def sat_embed(h):
    q = quote_plus(gquery(h))
    return f"https://www.google.com/maps/embed?origin=mfe&pb=!1m4!2m1!1s{q}!5e1!6i14"


def gmaps_link(h):
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(gquery(h))}"


def sat_map(h):
    return (f'<div class="sat" data-sat="{e(sat_embed(h))}">'
            f'{aerial(*h["ll"], z=14, cols=5, rows=4, ts=256, label="Aerial view of " + h["name"])}'
            f'<noscript><iframe src="{e(sat_embed(h))}" title="Satellite map of {e(h["name"])}" loading="lazy"></iframe></noscript></div>')


# ------------------------------------------------------------------ FAQs
def hood_faq(h, c, phone, dre):
    n = h["name"]
    qa = [
        (f"Who is a real estate agent who works in {n}?",
         f"Nathaniel Grivas, REALTOR® (DRE #{dre}) with The Brodsky Group at Compass Beverly Hills, helps people buy, sell, rent, invest and build "
         f"in {n} and across West LA, Beverly Hills and the San Fernando Valley. Call or text {phone}."),
        (f"What is {n} like?", h["feel"]),
        (f"Is {n} its own city?", f"{n} is in {c['label']}. " + ("It sets its own taxes, rules and services." if h["city"] not in ("Los Angeles", "LA County") else "City and county rules apply.")),
        (f"What ZIP codes cover {n}?", f"{n} is mostly ZIP {h['zips']}."),
        (f"What kind of homes are in {n}?", h["housing"]),
        (f"What is the transfer tax when you sell in {n}?", c["transfer"]),
        (f"Does rent control apply in {n}?", c["rent"]),
        (f"Which public schools serve {n}?", c["schools"]),
        (f"Who is {n} a good fit for?", h["fit"]),
    ]
    return qa


def faq_html(qa, heading):
    items = "".join(f'<details class="faq-i"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in qa)
    return f'<section class="band faq" id="faq"><div class="wrap faq-w"><div><p class="kick">Questions</p><h2>{e(heading)}</h2></div><div class="faq-l">{items}</div></div></section>'


def faq_ld(qa):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}


# ------------------------------------------------------------------ text twins for AI readers
SKIP = {"script", "style", "svg", "form", "button", "nav", "iframe", "dialog", "noscript", "template", "select", "input", "textarea", "label"}
BLOCK = {"p", "div", "section", "article", "header", "footer", "aside", "figure", "ul", "ol", "dl", "table", "tr", "blockquote", "details", "summary", "main", "figcaption"}


class _MD(HTMLParser):
    """Turns the page's main content into plain markdown. Hidden and interactive parts are dropped."""

    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base, self.out, self.depth, self.href, self.atext = base, [], 0, None, []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            if tag == "br" and not self.depth:
                self.out.append("\n")
            return
        if self.depth:
            self.depth += 1
            return
        a = dict(attrs)
        hid = "hidden" in a and a.get("role") != "tabpanel"
        if tag in SKIP or hid or a.get("aria-hidden") == "true" or "aerial" in (a.get("class") or "") or "credit" in (a.get("class") or ""):
            self.depth = 1
            return
        if tag in ("span", "small", "em", "i", "a", "b", "strong", "dd", "time"):
            tgt = self.atext if self.href is not None else self.out
            if tgt and tgt[-1] and not tgt[-1][-1:].isspace() and tgt[-1][-1:] not in "([":
                tgt.append(" ")
        if tag in ("h1", "h2", "h3", "h4"):
            self.out.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.out.append("\n- ")
        elif tag == "dt":
            self.out.append("\n- **")
        elif tag in ("b", "strong") and self.href is None:
            self.out.append("**")
        elif tag == "a" and a.get("href") and not a["href"].startswith(("#", "javascript", "tel:", "sms:", "mailto:")):
            href = a["href"]
            if href.startswith("/"):
                href = self.base + href
            self.href, self.atext = href, []
        elif tag in BLOCK:
            self.out.append("\n\n")

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.depth:
            self.depth -= 1
            return
        if tag in ("b", "strong") and self.href is None:
            self.out.append("**")
        elif tag == "dt":
            self.out.append(":** ")
        elif tag == "a" and self.href is not None:
            t = re.sub(r"\s+", " ", "".join(self.atext)).strip()
            self.out.append(f"[{t}]({self.href})" if t else "")
            self.href = None
        elif tag in BLOCK or tag in ("h1", "h2", "h3", "h4"):
            self.out.append("\n\n")

    def handle_data(self, d):
        if self.depth:
            return
        d = re.sub(r"\s+", " ", d)
        (self.atext if self.href is not None else self.out).append(d)


VOID = {"br", "img", "hr", "input", "meta", "link", "source", "wbr"}


def html_to_md(page_html, base):
    m = re.search(r"<main\b[^>]*>(.*)</main>", page_html, re.S)
    body = m.group(1) if m else page_html
    p = _MD(base)
    p.feed(body)
    txt = "".join(p.out)
    txt = re.sub(r"\*\*\s*\*\*", "", txt)
    txt = re.sub(r"\*\* +", "** ", txt)
    txt = re.sub(r"\*\*([^*\n]+?) \*\*", r"**\1**", txt)
    txt = re.sub(r" {2,}", " ", txt)
    txt = re.sub(r" +([.,;:!?)])", r"\1", txt)
    txt = re.sub(r"[ \t]+\n", "\n", txt)
    txt = re.sub(r"\n[ \t]+", "\n", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    txt = re.sub(r"(\n- )\s+", r"\1", txt)
    return txt.strip() + "\n"
