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

## Site v8 notes (Nov 26, 2026)
- Light editorial theme (assets/style.css, v8 block at the end). Dark is kept for the home hero, the films, photo overlays and the footer.
- Every page has a plain-text twin next to it (page.md). When you upload a folder, upload the .md files with the .html files in the same commit.
- llms.txt, llms-full.txt, robots.txt and the IndexNow key file are built at the root. Upload them with the root files.
- Google reviews live in src/v8.py (REVIEWS). When a new Google review appears, add it there, rebuild and upload everything that changed.
- Neighborhood satellite maps are Google Maps embeds (satellite view) that load on scroll; aerial photos come from USGS (public domain).
- GitHub upload: after clicking Commit changes, wait for "Processing your files" to finish before leaving the page, or the commit is lost.

## Site v9 notes (Nov 26, 2026): conversion
- Two lead flows in assets/lead.js: "value" (home valuation) and "buy" (buyer search). The lead is emailed the moment they give name, phone and email; the optional questions after that go out as a second "details" email.
- Landing pages for ads: /home-value/ and /buy/ (lp_shell in build.py). Every other page ends in lead_band() with both flows as tabs; neighborhood and guide pages also get cta_strip() mid-page.
- Ad tracking: set GTAG_ID and META_PIXEL at the top of build.py once the ad accounts exist. lead.js fires generate_lead / Lead events when those tags are present.
- Forms go through FormSubmit to nate.grivas@compass.com. If leads stop arriving, check the inbox for an "Activate FormSubmit" email.
- Vercel Hobby rate limits deploys after a burst; failed commits show "Deployment rate limited". Upload a new src/DEPLOY_PING.txt later and the next deploy that goes through publishes all of main.

## Site v10 notes (Local LA, news, public-record prefill)
- Neighborhoods and the guide are one section now, "Local LA". The guide lives on each `/neighborhoods/<slug>/`
  page (map of every pick + sections). `/guide/<slug>/` and `/guide/` 301 to the neighborhood pages; articles stay at
  `/guide/<post>/` and best-of pages at `/guide/best/<cat>/` (only categories with 3+ picks are built).
- Sections on a neighborhood page (guide_build.SECTIONS): Coffee & breakfast, Lunch & casual, Dinner, Nightlife,
  Culture & shows, Parks & outdoors, Shops. Rule: no section shows with fewer than 3 picks. Thin sections are topped up
  with picks from neighborhoods within 2.5 miles ("Next door in ..."), then merged ("Dinner & drinks", "Things to do").
- Nightlife is only the hottest scenes and the classiest rooms. No dive bars, sports bars or beer bars (those
  categories are retired). A bar gets in if it's a see-and-be-seen spot or a polished cocktail/hotel/rooftop room.
- Pins: each place can carry `"ll": [lat, lng]`. The map shows once a neighborhood has 3+ pinned places; until then the
  page keeps the satellite view. Geocode new places (Nominatim/OSM, 1 request per second) and add `ll` when you add them.
- LA News (`/news/`): Today = the latest journal file. This week and This month come from `src/news.json`
  (`week.items`, `month.lead`, `month.items`), same item format as the journal. Refresh the week every Monday and the
  month's headline on the 1st, plus any time a bigger story lands. Facts only, every item sourced, no opinions.
- Home value flow: after the address, lead.js looks up the LA County parcel (beds, baths, sq ft, lot, year built) and
  SCAG zoning in the visitor's browser and asks them to confirm. The lead email includes APN, zoning and whether the
  owner confirmed or corrected the record.

## Site v11 notes (Nov 26, 2026)
- History lessons live in src/history/{slug}.json (see src/history.py for the shape). "story_first": true puts the story right after the overview (hill and residential pages); otherwise it sits after the guide. Did-you-know pairs also feed the page's FAQPage schema and the News page "history desk".
- Guide heading switches to "near {n}" automatically when more than half the picks are borrowed from next door.
- News page is the Local LA Ledger (newspaper front page). The moving ticker (zipper) pulls headlines from news.json and the latest journal file; it also shows on Local LA via journal_teaser().
- .wrap is 1640px max so the site fills large screens. Keep reading text capped by its own max-width, not by .wrap.
- About: never put a small single-deal dollar figure next to the $100M+ team number. Lead with both sides represented, 15.6% over asking (7 offers in 9 days), and the $4.8M team listing.
