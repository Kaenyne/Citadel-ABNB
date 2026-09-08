# Access map — vendors, academic routes, free tiers (verified on SIG, mapped to ABNB)

Everything in §1–§3 was verified live on 2026-08-29 for SIG (`SIG/research/credit_card_data.md`, `channel_checks_sources.md`, `altdata_foot_traffic.md` §6, `altdata_search_traffic.md`). Items marked **verify** were not checked for ABNB specifically. §4 lists travel-specific sources that were not part of the SIG work; treat those as leads, not verified access.

## 1. Card / transaction panels (best route ranking unchanged)

| Route | Status (SIG verification) | ABNB notes |
|---|---|---|
| **Earnest Dash free tier** — `dash.earnestanalytics.com/signup`, ufl.edu email, org = University of Florida | self-serve, 1M+ household panel, company sales/transaction growth, history to 2016 | Earnest has historically published Airbnb vs Vrbo spend pieces; check `earnestanalytics.com/insights?s=airbnb` |
| **Consumer Edge academic trial** — `consumeredge.com/about-us/try-dash-for-free/`, Organization Type = "Academic Institution" | form verified; sales reviews signups | CE Transact covers travel; ask for ABNB / BKNG / EXPE dashboards and offer attribution in the deck |
| **Bloomberg Second Measure at Hough Hall** — `ABNB US Equity` → `ECAN <GO>`, `ALTD <GO>`, `BI <GO>` | terminals confirmed at Warrington; Second Measure active (Sept 2024 index launch) | Second Measure published an Airbnb-vs-Vrbo blog series pre-2024 (`secondmeasure.com/datapoints/?s=airbnb`) — **verify** the posts still exist; ECAN coverage of ABNB very likely (large cap) |
| **Dewey Data** — Consumer Edge card data, Advan, SafeGraph | UF is **not** a subscriber; FSU is (entire university); individual plan \$3,600/yr; samples available on request via a professor | Same |
| **WRDS** — UF has it | no card panels; useful for 13F, short interest, fundamentals | Same |
| Facteus free brand lookup — `facteus.com/data/brand-insights/<brand>` | 2,000+ brands, no signup | **verify** whether Airbnb / Vrbo / Booking pages exist |
| BofA Institute Consumer Checkpoint (monthly PDF) | free; category exhibits rotate | Travel/lodging and airline spend appear regularly — more useful for ABNB than it was for SIG |
| CNBC/NRF Retail Monitor | no jewelry line | no lodging line either; skip |

**Methodology caveat to carry (rewritten for ABNB):** card panels capture the guest's charge at booking (GBV, gross of host payout and taxes), not ABNB revenue, which is recognized at check-in and is ~13–14% of GBV. Panels skew US, so international GBV (majority of nights) is invisible. State both before a judge does; the SIG deck's equivalent line ("excludes 42% financed volume") was praised as differentiating.

## 2. Transcripts, expert calls, sell-side

| Route | Status | ABNB notes |
|---|---|---|
| **Bloomberg terminal transcript export** (merged PDF → per-call txt) | done for SIG (50 calls, 1,134 pages); page headers carry consensus-at-call | ~22 ABNB calls since Q4-2020; also export the UBS Evidence Lab ABNB notes and any BI travel primers while there |
| **AlphaSense trial** (2 weeks) | 12 SIG expert-call PDFs obtained | Time the trial to the ABNB sprint; search "Airbnb" in Expert Transcripts: hosts, property managers, ex-employees, OTA executives, regulators |
| Third Bridge Forum samples, Quartr app, Koyfin free | free surfaces | Same |
| Public comps' calls as free "expert calls" | BRLT was SIG's best free read-through | For ABNB: BKNG, EXPE (Vrbo), MAR, HLT, H, Sonder (bankrupt — history only), Vacasa (acquired), AirDNA/Key Data webinars |
| Seeking Alpha RSS `https://seekingalpha.com/api/sa/combined/ABNB.xml`; Substack archive API; Google News RSS; VIC guest access (45-day delay) | all worked when search engines were rate-limited | Same channels; ABNB volume will be 10x SIG's |
| **AI-content aggregators** (`rumourwithai`, `intellectia`, `trendonify`) | fabricate specifics — verified on SIG | Never cite |

## 3. Web, search, apps, archives

| Route | Status | ABNB notes |
|---|---|---|
| Google Trends via `pytrends` (urllib3 patch in `altdata_search_traffic.md` §1.1) | ~7 payloads before 429; `related_queries` captcha-blocked | Same limits; cache |
| SimilarWeb free tier | 3-month aggregate, MoM only, top-3 channels, no history | Build forward monthly; airbnb.com is large enough that panel error is small |
| Semrush free tier | monthly visits, organic/paid split; 404s intermittently | Same |
| **Sensor Tower free tier / Appfigures / AppMagic** | not needed for SIG | **Tier 1 for ABNB** — downloads, DAU/MAU, Airbnb vs Vrbo vs Booking vs Hopper; **verify** current free-tier depth |
| Common Crawl (`index.commoncrawl.org`, `data.commoncrawl.org` range fetches) | worked at scale (10k fetches); systematic monthly timing | Airbnb listing pages are JS-heavy; the archive may hold the SSR JSON — prototype one crawl |
| Wayback Machine CDX + `id_` raw fetch | replay tier went down mid-build; outage guard written | Fallback for homepage messaging history |
| Placer.ai education tier (`analytics.placer.ai/auth/signup` with .edu) | free tier exists; chain-level depth unknown | Not useful for ABNB (no stores); skip |
| Reddit (`r/AirBnB`, `r/airbnb_hosts`, `r/vrbo`, `r/travel`) | SIG used engagement-ring subs for sentiment | Host-side subs are the ABNB edge: fee changes, algorithm complaints, regulation impact, occupancy anecdotes — the SIG rule stands: n, date, and role on every quote |

## 4. Travel-specific sources (not part of SIG; leads to verify)

| Source | What | Access |
|---|---|---|
| **Inside Airbnb** (`insideairbnb.com/get-the-data`) | quarterly listing-level dumps for ~100 cities: price, availability, reviews, host IDs, room type | free, immediate; the supply/host-concentration panel |
| **AirDNA** | the professional STR panel (ADR, occupancy, RevPAR, supply by market); UBS/sell-side cite it | free market snapshots on city pages; full data paid; ask for an academic sample |
| **Key Data** | second STR panel (property-manager sourced) | monthly free blog posts (the Edge-Retail-Academy analog: two panels agreeing beats one) |
| **STR / CoStar** | weekly US hotel occupancy, ADR, RevPAR | paid; weekly headline numbers are free via press (Hotel News Now, CoStar releases) — the hotel-vs-STR wedge exhibit |
| **TSA checkpoint throughput** (`tsa.gov/travel/passenger-volumes`) | daily passengers, free, backfillable to 2019 | demand proxy; no y/y noise problem |
| **BTS / DOT T-100, A4A** | airline passengers and fares | quarterly; free |
| **NTTO** (`trade.gov/i-94-arrivals`) | monthly international arrivals to the US by country | free; the inbound-travel line for ABNB's US business (matches BEA "foreign travel in the US" in `data/`) |
| **City STR registries** (NYC OSE, New Orleans, etc.) | registered listing counts by month | free; primary regulatory exposure data |
| **UBS Evidence Lab / sell-side app panels** | ABNB app usage, listing counts, pricing | terminal |
| **Phocuswright, Skift Research, Euromonitor** | TAM sizing | paid; reconcile before any TAM slide (SIG rule) |

## 5. Do-first list (adapted from SIG's "Do-this-Monday" plan)

1. Earnest Dash + Consumer Edge academic signups (same day; both free).
2. Hough Hall terminal session: ABNB transcripts export, `ECAN`, `ALTD`, UBS Evidence Lab ABNB notes, BI travel primers, consensus history.
3. Inside Airbnb dumps for 8–10 cities incl. NYC (pre/post LL18), plus AirDNA free city pages screenshot monthly.
4. Sensor Tower / Appfigures free tiers.
5. AlphaSense trial timed to start the week the KPI panel is done.
6. Common Crawl prototype: one crawl, one city's listing URLs, inspect the JSON.
