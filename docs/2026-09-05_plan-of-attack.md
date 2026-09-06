# Plan of attack, 5 Sep 2026 to the Q3 print (5 Nov) and the ~Dec pitch

**Author:** Krishang (compiled with Claude Code). **Inputs:** open PRs, the uncommitted working tree, Theo's `theos-past-research/` package, `ABNB-Crossover/`, and the notes in `research/notes/`. Branch names follow `CONTRIBUTING.md` (`<name>/<topic>`, small, merged within days). Hours are the crossover's estimates where they exist.

## 1. Open PRs: merge order

| PR | Branch | Contents | Action |
|---|---|---|---|
| #3 | `research/management-timeline` | one note | Merge first. No dependencies. |
| #4 | `research/third-bridge-digest` | one note | Merge second, but pair it with a decision on the five Third Bridge PDFs tracked in `research/`. The repo rule and Theo's import policy both say licensed PDFs go to Drive. Recommended: merge the digest now, then open `krish/licensed-pdfs-to-drive` (below) so the digest's links point at Drive. |

Merged already: #1 Theo's package, #2 pitch catalogue.

## 2. Uncommitted work: split into six small PRs

Everything below is in the working tree today. Grouping is by what a reviewer can check in one sitting. Merge in the order listed because later PRs cite earlier files.

| Order | Branch | Files | Reviewer checks |
|---|---|---|---|
| 1 | `krish/stock-reactions` | `research/notes/2026-09-05_abnb-major-moves.md`, `data/processed/abnb_major_moves_events.csv`, `abnb_daily_close.csv`, `abnb_earnings_reactions.csv`, `abnb_revenue_guidance_vs_actual.csv`, `analysis/figures/abnb_major_moves.png`, `analysis/src/abnb_from_theo_guidance.py` | 41 moves attributed; 1-day returns match Theo's file; script rebuilds the two derived CSVs |
| 2 | `krish/margin-drivers` | `research/notes/2026-09-05_margin-drivers.md`, `data/processed/abnb_quarterly_costlines.csv`, `abnb_kpi_vs_category_quarterly.csv`, `data/raw/fred/*.csv`, `analysis/src/abnb_costlines_from_xbrl.py`, `abnb_kpi_vs_category.py`, plus the `data/README.md` and `research/sources/README.md` rows | Cost lines tie to XBRL; guidance cushion table (5.1) ties to Theo's letters extract; ADR vs hotels (3.4) ties to BEA |
| 3 | `krish/pitch-landscape` | `research/notes/2026-09-04_abnb-pitch-landscape.md` | Complements the merged catalogue (KPIs, valuation methods, debates); no overlap in content |
| 4 | `krish/regulatory-db` | `research/regulatory/*`, `analysis/src/build_regulatory_database.py`, `complete_regulatory_archive.py`, `pull_regulatory_documents.py`, `download_abnb_transcripts.py`, `data/processed/abnb_regulatory.sqlite`, `requirements.txt`, `.gitignore` | Being built in another session today; open the PR when it stops moving. Add Theo's five municipal registry sources (NYC OSE data page and enforcement reports, Vancouver, New Orleans, San Diego) from his `source_registry.csv` |
| 5 | `krish/crossover-kit` | `ABNB-Crossover/` (move to `research/crossover/` to fit the layout), `research/notes/2026-09-05_crossover-checklist.md`, `analysis/src/abnb_options_ledger.py`, `data/processed/abnb_options_ledger.csv`, `analysis/src/cc_airbnb_probe.py` | Planning kit; scripts still carry SIG paths, which the checklist says; `.obsidian/` goes in `.gitignore` |
| 6 | `krish/licensed-pdfs-to-drive` | remove the five Third Bridge PDFs, link Drive paths from `research/sources/README.md` S16 to S20 | Team call on whether to rewrite history. Theo's `validate_import.py` pattern can be reused as a repo-wide check |

## 3. New branches for the build (priority order)

| # | Branch | What it produces | Hours | Depends on | Suggested owner |
|---|---|---|---|---|---|
| 1 | `krish/inside-airbnb-supply` | Listing-level panel for 8 to 10 cities from Inside Airbnb `listings.csv.gz` (price, reviews_ltm, availability, host listing count, room type). Current dumps: NYC 2026-08-10, LA 06-15, Paris 06-16, London 06-19, Barcelona 06-24, Austin 06-22, Nashville 06-26. Request archived quarterly dumps from Inside Airbnb for the NYC pre/post Local Law 18 series. Outputs: like-for-like nightly price on matched listing IDs across dumps, entire-home and multi-listing host share, exposed nights for the regulatory tracker | 4 to 6 | none; CC-BY 4.0 licence, attribution in the deck | Krish |
| 2 | `krish/cc-listing-panel` | Common Crawl matched-listing panel, 2021 to 2026 (see section 4). Review-count velocity, Superhost and Guest Favorite share, survival, geography mix | 8 to 12 | none | Krish (started) |
| 3 | `krish/consensus-at-call` | Bloomberg transcript export at Hough Hall; the page headers give consensus EPS and revenue at every call. Fills Theo's `consensus_snapshots.csv` (all 23 rows currently "missing"). Then the reaction-function test: guide-vs-consensus gap against day-one move, versus the beat | 3 plus terminal time | terminal booking | whoever has the terminal slot |
| 4 | `krish/capital-return-panel` | Quarterly SBC, buybacks, diluted shares, FCF and net share change from the letters and 10-Q covers; XBRL cannibal scorecard for BKNG, EXPE, META, NFLX, UBER, DASH using the pattern in `abnb_costlines_from_xbrl.py` | 5 | none | Krish or Theo |
| 5 | `krish/trends-share-of-search` | Google Trends: airbnb, vrbo, booking.com, hotels.com, expedia in one payload; category terms in another; y/y in levels and first differences against nights growth | 3 | `pytrends` in the 3.13 Python | Krish |
| 6 | `theo/guidance-margin-items` | Add Adjusted EBITDA margin guides and the SEC 8-K acceptance timestamps to `guidance_items.csv` and `guidance_events.csv`; his dataset has revenue and KPI-direction guides only | 3 | none | Theo |
| 7 | `krish/transcript-analytics` | Parser on the 23 IR PDFs already in `data/raw/regulatory/transcripts/`: analyst roster churn, topic frequency, "declined to quantify" list. Extends `airbnb_earnings_call_study.md` | 5 | none | Krish |
| 8 | `krish/weekly-captures` | Scheduled weekly runs: options ledger, SimilarWeb free-tier snapshot (airbnb.com, vrbo.com, booking.com), Sensor Tower or Appfigures free tier. Build-forward series; start now or they will not exist by December | 1 plus 15 min/week | none | anyone |
| 9 | `krish/expectations-map` | The pre-print document for 5 Nov: guidance detail, consensus by aggregator, revisions, options (re-run the ledger with the first weekly expiry after 5 Nov), positioning, peer calendar (BKNG, EXPE, MAR, HLT report first), scenario map. Includes the pre-registered prediction card | 6 | 3, 8 | Krish |
| 10 | `theo/h10-walkforward` (optional) | The one alt-data test his brief left open: H.10 dollar index in eight walk-forward folds against seasonal and prior-quarter baselines. Low pitch value; do only if Theo wants the closure | 4 | none | Theo |

Not recommended: more free-source scraping of the kind Theo's edge-discovery runs already exhausted (TSA, BLS, FHWA, municipal portals all blocked or non-point-in-time), and any AirDNA or card-panel work before the free tiers are confirmed.

## 4. Common Crawl: what the prototype found and what the branch should build

Probe script: `analysis/src/cc_airbnb_probe.py`. Run 5 Sep 2026 against three crawls.

**Coverage.** CC-MAIN-2026-30 holds 9,946 index rows for `airbnb.com/rooms/*`: 7,884 status-200 captures, 7,534 unique listings, every full render about 1 MB of HTML. Crawls back to 2021 hold 4 to 10 index blocks each, so roughly 8k to 20k room captures per crawl, five to six crawls a year. Only 11% of URLs carry check-in dates.

**No prices, in any era.** Samples from 2022, 2024 and 2026 all have `structuredDisplayPrice: null` and no price strings, with or without dates in the URL. Airbnb loads price client-side through GraphQL, so the archive never sees it. The crossover's "free Evidence Lab clone" for nightly rates does not exist for Airbnb. Inside Airbnb is the price source (branch 1).

**What every era does carry.** Listing ID, Superhost flag, room type, capacity, city, latitude and longitude, review count (`visibleReviewCount` in 2022 and 2024, `ratingCount` and `ratingValue` in the 2026 LD+JSON block), cancellation policies, amenities. Guest Favorite appears from 2024.

**The panel to build.**
1. Harvest the CDX index for every crawl since CC-MAIN-2021-25 (about 30 crawls, one index page each) and keep status-200 room captures with their listing IDs.
2. Intersect listing IDs across crawls to get matched panels (same listing seen in crawl A and crawl B), then range-fetch both captures. Adapt `cc_matched_sku.py` from the crossover: the product-code regex becomes `/rooms/(\d+)`, the parser becomes the field regexes in the probe script.
3. Exhibits: review-count growth on matched listings by year (a bookings-velocity proxy, the same role `reviews_ltm` plays in Inside Airbnb), Superhost and Guest Favorite share over time (professionalization), listing survival between crawls (churn), and city mix of captured listings.
4. Caveats to state on the slide: Common Crawl's sample of listings is whatever the crawler reached, not a random draw; review counts lag stays by weeks; the 2023 template change moved the review count into a different JSON block.

**Policy.** The probe never touched airbnb.com; it read a public archive. Theo's package blocks scraping Airbnb-controlled sources and the team should record that Common Crawl reads are outside that rule before the branch goes further. Keep request volume polite (four workers, one index page per crawl, range fetches only for matched IDs).

**Go/no-go.** Go, as a supplement. Budget 8 to 12 hours and expect one or two exhibits, not a pricing panel. If the matched-listing intersection between crawls a year apart is under about 500 listings, stop and rely on Inside Airbnb alone.

## 5. Cadence to the print

| Week of | Milestone |
|---|---|
| 7 Sep | Merge #3, #4, PRs 1 to 3 from section 2. Start branches 1 (Inside Airbnb) and 2 (Common Crawl). Start weekly captures. |
| 14 Sep | Merge regulatory-db and crossover-kit. Consensus-at-call terminal session. Capital-return panel. |
| 21 Sep | Trends share-of-search. Transcript analytics. First Inside Airbnb and Common Crawl exhibits. Thesis v1 (fill `docs/TIMELINE.md`). |
| 28 Sep to 19 Oct | Model base case; deck first draft; peer prints start late Oct. |
| 26 Oct | Expectations map; options ledger with the post-print weekly expiry; prediction card frozen before 5 Nov. |
| 5 Nov | Q3 print. Score the prediction card; update the guidance cushion and drift tables. |
| Nov | Deck final; dry run; submission ~Dec per `docs/TIMELINE.md`. |
