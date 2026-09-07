# ABNB-Crossover: what was checked, what was used, what is left to build

**Source:** `ABNB-Crossover/` (built 2026-09-05 from the SIG project: five planning docs, 12 data files, 5 CSV templates, 13 scripts). Cross-checked against Theo's `theos-past-research/` package and the notes in `research/notes/`.
**Date:** 2026-09-05
**Author:** Krishang (compiled with Claude Code)

## 1. What the folder contains

| Item | Verdict after cross-check |
|---|---|
| `00_README`, `01_METHOD_TRANSFER_MAP` | Planning docs mapping every SIG workstream to an ABNB analog with effort estimates. Accurate on structure (calendar FY, no footprint, ~40 analysts). Two factual nits: 23 calls not "~22", and the Q3 print is 5 Nov 2026 per the major-moves note. |
| `02_DATA_ALREADY_IN_HAND` + `data/bea_pce_travel_monthly_2015_2026.csv` | **Used.** BEA PCE accommodations, hotels, air, inbound and outbound foreign travel, monthly to Jul 2026. Now merged into `data/processed/abnb_kpi_vs_category_quarterly.csv`. |
| `data/fred_*.csv` (UMCSENT, PSAVERT, PCEDG, RSXFS, PCEPI, CPIAUCSL, e-commerce) | Consumer backdrop only. Not merged; CPI all-items re-pulled fresh with the two lodging series (see below). |
| `data/options_ledger.csv`, `bb_consensus_at_call.csv`, `web_traffic_snapshot_2026-08.csv` | SIG data kept for format. Options ledger re-run for ABNB peers (below). Consensus-at-call is the schema for the Bloomberg transcript export; Theo's dataset has the slot for it (`consensus_snapshots.csv`, all rows "missing, Bloomberg pending"). |
| `templates/` (KPI panel, bear scoreboard, print-day moves, notable moves) | KPI panel and print-day moves are now built (below). Notable-moves schema is already matched by `data/processed/abnb_major_moves_events.csv` except the confidence grade. Bear scoreboard is not started. |
| `tools/` | `options_ledger.py` adapted and run. `forward_exhibits.py` style block and `deck_charts_v2.py` print-day distribution chart are reusable for the deck. Common Crawl and Wayback scrapers are usable but see the policy note in section 4. |
| `03_ACCESS_MAP`, `04_IDEAS_BACKLOG`, `05_PITCH_CRAFT_CARRYOVER` | Reference. Backlog items ranked below against what already exists. |

## 2. Built today from the crossover material

1. **KPI vs category panel** (`data/processed/abnb_kpi_vs_category_quarterly.csv`, script `analysis/src/abnb_kpi_vs_category.py`). ABNB nights, GBV, ADR, revenue, EBITDA and take rate for 1Q21 to 2Q26 next to BEA accommodations and hotels (nominal, real, price), inbound and outbound travel, CPI lodging and airfare. Derived: implied ADR (matches reported within 50 cents every quarter), real ADR, and the nights-minus-category share gap. Findings are in the margin note section 3.4: ABNB nights have beaten real US lodging volume growth every quarter since Q3 2022 by 4 to 14 points; ABNB ADR rose 3% to 9% from Q2 2025 to Q1 2026 while US hotel prices fell 2% to 3%; Q2 2026 is the first quarter hotels caught up (+4.9% vs +5.3%).
2. **FRED CPI lodging and airfare** (`data/raw/fred/`). Keyless download works for the seasonally adjusted lodging series and airline fares. The unadjusted lodging series Theo wanted (CUUR0000SEHB02) is bot-blocked on FRED, matching his finding.
3. **Options ledger** (`data/processed/abnb_options_ledger.csv`, script `analysis/src/abnb_options_ledger.py`, run with `py -3.13`). Baseline as of 5 Sep 2026, 76 days before the 20 Nov expiry:

| Ticker | Spot | Straddle to 20 Nov | ATM IV | 25-delta skew | Put/call OI |
|---|---|---|---|---|---|
| ABNB | 181.94 | 13.4% | 37.9% | -0.5 | 1.11 |
| BKNG | 193.29 | 15.7% | 48.7% | +0.7 | 1.12 |
| MAR | 336.51 | 10.3% | 30.0% | +2.5 | 0.44 |
| H | 165.85 | 13.5% | 41.8% | -2.2 | 0.41 |

   The event-implied move is meaningless this far out (the Nov and Dec expiries both contain the print, so variance differencing nets to zero). Re-run the week of the print with the first weekly expiry after 5 Nov as the near leg. ABNB's skew is flat (calls and puts priced alike) and its put/call open interest is the highest of the group. TRIP and JETS chains were too thin. EXPE and HLT had no 20 Nov expiry and fell back to 23 Oct.
4. **Print-day distribution** (from `data/processed/abnb_earnings_reactions.csv`): 23 prints, median absolute day-one move 6.9%, mean 7.1%, 48% above 7%, 35% above 10%, 26% above 13%, max 17.4%. This is the line to set against the implied move in the expectations map.

## 3. Backlog ranked against what already exists

Effort estimates are the crossover's. "Have" means the repo already holds it.

| # | Idea (crossover rank) | Status | Next step |
|---|---|---|---|
| 1 | Quarterly KPI panel with derived series (T1 #1) | **Have**: `airbnb_earnings_call_study.md` 3.1 plus today's category panel | Add SBC, buybacks, diluted shares, FCF per quarter from the letters and 10-Q covers (net share change after SBC is the missing derived series) |
| 2 | Guidance-vs-actual and reaction-function test (T1 #2) | **Half**: cushion table built (margin note 5.1); Theo's brief found guidance-to-return Pearson 0.03 to 0.08 | Needs consensus at call. Bloomberg transcript export page headers carry it for free (crossover `bb_consensus_at_call.csv` schema); Theo's `consensus_snapshots.csv` is the target table |
| 3 | BEA travel panel exhibit (T1 #3) | **Have** (today) | Chart it: nights y/y vs BEA real accommodations, ADR y/y vs hotels price |
| 4 | Google Trends share-of-search with first-differences test (T1 #4) | Not started | 3h; `pytrends` is in the 3.13 Python. Run levels and first differences before quoting |
| 5 | Options ledger and print-day distribution (T1 #5) | **Have** (today) | Weekly re-run; pre-print run in the week of 5 Nov |
| 6 | Pitch-mine and score every writeup (T1 #6) | **Have**: 30 pitches in `2026-09-04_abnb-pitch-landscape.md`, catalogue in progress in `2026-09-04_abnb-pitch-catalogue.md` | Score each call at its date's price using `abnb_daily_close.csv`; tally which metrics nobody used |
| 7 | Buyback-vs-SBC cannibal scorecard (T2 #7) | Not started; XBRL script pattern exists in `abnb_costlines_from_xbrl.py` | 5h; add BKNG, EXPE, META, NFLX, UBER, DASH via the same companyfacts endpoint |
| 8 | Common Crawl listing-price panel (T2 #8) | Not started | See policy note, section 4 |
| 9 | Inside Airbnb supply and host-concentration panel (T2 #9) | Not started; Theo's lodging-map plan downloaded 16 city files but they were omitted from git | 4h; Inside Airbnb terms allow download; NYC pre/post LL18 is the natural experiment for the regulatory work in `research/regulatory/` |
| 10 | Transcript analytics on 23 calls (T2 #10) | **Half**: `airbnb_earnings_call_study.md` has sentiment by quarter and analyst topics; Theo has speaker-tagged excerpts | Rebuild the parser on the IR PDFs already in `data/raw/regulatory/transcripts/`; add roster churn and the "declined to quantify" list (margin note section 9 has three items) |
| 11 | Expectations map for the 5 Nov print (T2 #11) | Not started | 6h, the week before the print; peers BKNG, EXPE, MAR, HLT report first |
| 12 | Regulatory tracker from primary text (T2 #12) | **In progress** in `research/regulatory/` (44 sources, factors, earnings observations) | Add exposed-nights estimates from Inside Airbnb; add Theo's five municipal registry sources |
| 13 to 20 | Blotnick audit, consensus-vs-price, event ledger, FX and interest ledgers, app trackers, SimilarWeb, expert-call claims, prediction card | Event ledger **have** (`2026-09-05_abnb-major-moves.md`, 41 moves). Expert-call claims **half** (Third Bridge digest). Rest not started | App trackers and SimilarWeb are build-forward series: start monthly captures now or they will not exist by the pitch |

## 4. Two conflicts to settle as a team

- **Scraping airbnb.com.** The crossover's most differentiated idea (Common Crawl listing-page pricing panel, Airbnb GraphQL capture) targets Airbnb-controlled pages. Theo's package has an explicit scraping policy that blocks Airbnb-controlled sources and OTAs and gates every request on robots and terms; his runs logged Airbnb IR as blocked. Common Crawl fetches archived copies rather than hitting airbnb.com, which is the argument for it, but the team should decide one rule before anyone builds it. Inside Airbnb (already scraped, published under its own licence) is the uncontroversial route to listing-level data.
- **Licensed material in git.** The crossover's access map routes through Bloomberg exports, AlphaSense and Earnest. The repo rule and Theo's import policy both say paid exports stay in Drive. The five Third Bridge PDFs in `research/` still break that rule.

## 5. Pitch-craft rules worth carrying into the deck now

From `05_PITCH_CRAFT_CARRYOVER.md`, the ones that bind this pitch: the print is one dated catalyst among three or four, never the only one; decompose growth as nights times ADR times take rate times FX; show ADR real (now possible with the CPI lodging series); alt data as spread or mechanism, not nowcast; a named comparator running the other playbook (Booking); pre-frame the disqualifier (take rate, Services losses) on a slide; quantified risks; a pre-registered prediction card for 5 Nov with falsifiers.
