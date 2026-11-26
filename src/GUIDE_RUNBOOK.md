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
   site; the write-up stays in our own words. A local favorite that only Google covers can still
   get in: give it the neighborhood's "gm" source key
   (["Google Maps reviews (local favorites we checked)", "https://www.google.com/maps/search/?api=1&query=<Area>+CA"])
   and keep its write-up to plain facts about the place.
5. Reddit and Yelp: both ban automated reading and the fetch tool refuses them. Do not route
   around that (no browser, no mirror sites). Get the Reddit consensus secondhand from articles
   that round up Reddit picks (Chowhound, Tasting Table, etc.) and from local forums and tip
   sites: Food Talk Central, Foursquare tips, Atly.
6. Aim for 30 to 50 places across eat, drink and do.

## Monthly refresh (1st of each month)
Re-check every neighborhood: confirm each place is still open (Google places_search, critics'
closure notes), remove closures, swap out weak ones, and add places that opened in the last few
months once real people rate them highly (same bar as above). Openings that are only weeks old go
in the LA Journal first, not the guide. Update `updated` on every file you touch.

## The LA Journal (daily, evening)
One file per day: src/journal/YYYY-MM-DD.json
  {"date","title","dek","items":[{"tag","h","t","hoods":[slugs],"src":[[outlet,url]]}],
   "openings":[{"n","hood","w","src":[outlet,url]}]}
- 5 to 8 items about Los Angeles that day: city news, weather, transit, real estate and housing,
  food, things to do this week, sports. Lead with what matters most to people living in the areas
  Nate covers (West LA, Beverly Hills, the Valley, Hollywood to Silver Lake, the beach cities).
- `h` and `t` are our own words: 2 to 4 short sentences, plain facts, no quotes, nothing copied or
  closely paraphrased. Always link the original reporting in `src` (1 to 3 outlets).
- Tag `hoods` with neighborhood slugs from src/hoods.py when an item is about one; the item then
  shows on that neighborhood's guide page under "in the news".
- `openings`: notable new restaurants or bars in our neighborhoods (Infatuation's New Openings,
  Eater LA, Time Out). They go in the journal, not the guide, until they earn strong reviews.
- Neutral on politics: report what happened, no opinions. No crime-victim details, no private people.
- Fair housing: describe places and events, never the people who live somewhere.
- Never use em dashes. Search the web for every item; never write news from memory.

## Commit tips
Vercel's free Hobby plan allows 100 deployments per rolling 24 hours, and every GitHub commit
triggers one. Past that, commits still land on main but the site stops updating until the window
resets; the next commit after that deploys everything. Keep each run to about 10 commits or fewer:
one commit per folder, never one per file.
Keep GitHub commit summaries under 50 characters. Longer ones show a ProTip that shifts the
layout and the Commit button click can miss. Check github.com/nategrivas/nathanielgrivas/commits/main
after uploading.

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
   (file_upload takes at most 32 files and 3.8MB per call; call it again on the same page to add
   more before committing). Run find again after every page load: element refs change. Commit
   straight to main. Vercel deploys in about 30s.
7. Upload any changed src files the same way (src, src/guide), and add new paths to MANIFEST.txt.
