"""Neighborhood history lessons: src/history/{slug}.json -> "The story of ..." section.

JSON shape
  title        headline for the section
  lede         one paragraph that hooks the reader
  story_first  true for hill and residential pages: the story goes right after the overview
  tl           timeline [[year, text], ...]
  ch           chapters [{k: kicker, h: heading, p: [paragraphs], fact: [big, small]}]
  dyk          did-you-know cards [[question, answer], ...]
  lm           landmarks [[name, year, line], ...]
  src          sources [[title, url], ...]
Write in our own words. No quotes from sources, no em dashes, describe places rather than the people who live there.
"""
import json
from html import escape
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent


def e(s):
    return escape(str(s), quote=True)


def load():
    out = {}
    d = ROOT / "history"
    if d.exists():
        for f in sorted(d.glob("*.json")):
            out[f.stem] = json.loads(f.read_text())
    return out


ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]


def words(hx):
    parts = [hx.get("lede", "")]
    parts += [t for _, t in hx.get("tl", [])]
    parts += [p for c in hx.get("ch", []) for p in c.get("p", [])]
    parts += [q + " " + a for q, a in hx.get("dyk", [])]
    return len(" ".join(parts).split())


def gmaps(name, where):
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(f"{name}, {where}, CA")


def render(h, hx):
    n = h["name"]
    where = h.get("city") if h.get("city") not in (None, "Los Angeles", "LA County") else "Los Angeles"
    mins = max(3, round(words(hx) / 220))
    tl = "".join(f'<li><span class="ht-y">{e(y)}</span><p>{e(t)}</p></li>' for y, t in hx.get("tl", []))
    chips = "".join(f'<a href="#ch-{i + 1}"><i>{ROMAN[i]}</i>{e(c["h"])}</a>' for i, c in enumerate(hx.get("ch", [])))
    chs = ""
    for i, c in enumerate(hx.get("ch", [])):
        fact = f'<aside class="hc-fact"><b>{e(c["fact"][0])}</b><span>{e(c["fact"][1])}</span></aside>' if c.get("fact") else ""
        ps = "".join(f"<p>{e(p)}</p>" for p in c.get("p", []))
        chs += (f'<article class="hc" id="ch-{i + 1}"><p class="hc-k"><span>{ROMAN[i]}</span>{e(c.get("k", ""))}</p>'
                f'<h3>{e(c["h"])}</h3><div class="hc-b">{fact}{ps}</div></article>')
    dyk = "".join(f'<details class="dyk"><summary><span class="dyk-n">{i + 1:02d}</span><b>{e(q)}</b><i>Tap for the answer</i></summary><p>{e(a)}</p></details>'
                  for i, (q, a) in enumerate(hx.get("dyk", [])))
    lm = "".join(f'<li><a href="{gmaps(nm, n if where == "Los Angeles" else where)}" rel="noopener"><b>{e(nm)}</b>'
                 f'{("<span class=lm-y>" + e(y) + "</span>") if y else ""}<span class="lm-t">{e(t)}</span><i>Map &#8599;</i></a></li>'
                 for nm, y, t in hx.get("lm", []))
    src = "".join(f'<li><a href="{e(u)}" rel="noopener">{e(t)}</a></li>' for t, u in hx.get("src", []))
    meta = [f"{mins} min read", f"{len(hx.get('tl', []))} milestones", f"{len(hx.get('ch', []))} chapters"]
    if hx.get("lm"):
        meta.append(f"{len(hx['lm'])} landmarks")
    return f"""<section class="band hist" id="history"><div class="wrap">
<header class="hist-head">
<p class="kick">The story of {e(n)}</p>
<h2>{e(hx["title"])}</h2>
<p class="hist-lede">{e(hx["lede"])}</p>
<p class="hist-meta">{"".join(f"<span>{m}</span>" for m in meta)}</p>
<nav class="hist-chips" aria-label="Chapters">{chips}</nav>
</header>
<div class="hist-grid">
<aside class="hist-tl" aria-label="{e(n)} timeline"><h3>Timeline</h3><ol>{tl}</ol></aside>
<div class="hist-ch">{chs}</div>
</div>
{f'<div class="hist-dyk"><div class="hist-sub"><p class="kick">Test yourself</p><h3>Did you know?</h3></div><div class="dyk-grid">{dyk}</div></div>' if dyk else ''}
{f'<div class="hist-lm"><div class="hist-sub"><p class="kick">Go see it</p><h3>Landmarks worth the drive</h3></div><ul>{lm}</ul></div>' if lm else ''}
{f'<details class="gsrc hist-src"><summary>Sources for this history</summary><ul>{src}</ul></details>' if src else ''}
</div></section>"""


def faq_pairs(hx):
    return [(q, a) for q, a in hx.get("dyk", [])]


def teaser(h, hx):
    """Short card for index pages: the first did-you-know."""
    q, a = (hx.get("dyk") or [["", ""]])[0]
    return {"slug": h["slug"], "name": h["name"], "title": hx["title"], "q": q, "a": a}
