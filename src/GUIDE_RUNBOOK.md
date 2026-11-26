# The LA Guide: research runbook

The guide lives in `src/guide/<neighborhood-slug>.json`, one file per neighborhood. `python3 src/build.py` turns them into:
- `/guide/` hub, `/guide/<slug>/` neighborhood guides, `/guide/best/<category>/` citywide pages
- a link from each `/neighborhoods/<slug>/` page to its guide, plus entries in llms.txt and the sitemap

Neighborhood slugs come from `src/hoods.py` (HOODS). A guide file's `slug` must match one.

## JSON schema
{"slug": "venice", "updated": "YYYY-MM-DD", "intro": "2 sentences, plain English",
 "sources": {"key": ["Publisher: Title", "https://url"]},
 "places": [{"n": "Name", "c": ["primary-category", "other", ...], "a": "street address or street",
             "p": "$ | $$ | $$$ | $$$$ | Free", "w": "why people go (1-2 sentences)",
             "o": "what to order / what to do / when to go", "s": ["source keys"]}]}

Categories (first one is where the card is listed; all are used for the citywide pages):
coffee breakfast brunch lunch dinner date pizza tacos seafood sushi bakery healthy cheap
bars dive wine beer rooftop sports latenight
music comedy film museum art landmark park hike beach shop market fitness golf kids dogs spa

## Writing rules (non-negotiable)
- Everything in our own words. Never paste or closely mirror review text. No quotes.
- Say what reviewers consistently praise or warn about, then a concrete order/do line.
- Only include places a current source supports. Drop anything a source marks closed.
  Prefer sources updated in the last 18 months; older lists need a second, newer source.
- Every place lists at least one source key; every source key resolves to a real URL.
- No em dashes. Short sentences. Prices as $ to $$$$.
- Fair housing: describe places, never the kind of people who live in a neighborhood.

## Research method (per neighborhood)
A place gets in only if it passes two tests: real people rate it highly, and it is open today.

1. Critics for the shortlist: The Infatuation neighborhood guide (WebFetch, compact table),
   Eater LA, LA Times 101, Time Out, Michelin, LA Taco, LAist. Find exact URLs with WebSearch
   first; guessed Infatuation/Time Out URLs usually fail.
2. Bars: The Infatuation or Time Out bar guide for the area.
3. Things to do: Time Out / Discover LA / city tourism pages for parks, museums, shops, venues.
4. Real-people check (the most important step): Google reviews through the places_search tool
   (Google Places). Run category queries ("brunch Venice Los Angeles", "dive bars Silver Lake")
   to find well-loved places critics missed, and name queries to verify each shortlisted place.
   Use rating, review count, hours and the review text to decide who gets in and what locals
   praise or warn about. Rule of thumb: 4.4+ with 150+ reviews, or 4.6+ with 50+ for small spots.
   Drop anything Google shows as closed. Never put Google stars, counts or review text on the
   site; the write-up stays in our own words. Google is research only, so it is not a source key.
5. Reddit and Yelp: both ban automated reading and the fetch tool refuses them. Do not route
   around that (no browser, no mirror sites). Get the Reddit consensus secondhand from articles
   that round up Reddit picks (Chowhound, Tasting Table, etc.) and from local forums and tip
   sites: Food Talk Central, Foursquare tips, Atly.
6. Aim for 30 to 50 places across eat, drink and do.

## Refresh
Each run also re-checks one existing neighborhood against Google: confirm every place is open,
swap out weak ones, add new openings that locals already love, update `updated`.

## Running it from a fresh session
1. mkdir -p /home/claude/site && cd /home/claude/site
2. Download every path in src/MANIFEST.txt from
   https://raw.githubusercontent.com/nategrivas/nathanielgrivas/main/<path> (curl -fsSL).
   Also fetch links.html into links/index.html.
3. Research and edit src/guide/*.json per this runbook.
4. python3 src/build.py   (assets/ and img/ are optional; the live site already has them)
5. python3 src/changed.py  prints every deploy file that differs from main, grouped by folder,
   with the GitHub upload URL for each folder.
6. Upload each folder's files in Chrome at github.com/nategrivas/nathanielgrivas/upload/main/<folder>
   (file_upload up to 3.8MB per call), commit straight to main. Vercel deploys in about 30s.
7. Upload any changed src files the same way (src, src/guide), and add new paths to MANIFEST.txt.
