# Data

| File | Source | Pulled by | Date | Notes |
|---|---|---|---|---|
| processed/abnb_daily_close.csv | Yahoo Finance daily closes (ABNB), via yfinance | Krish (Claude Code) | 2026-09-05 | Date, Close, 10 Dec 2020 to 4 Sep 2026 (1,440 sessions). Input to the major-moves screen. |
| processed/abnb_major_moves_events.csv | Derived from abnb_daily_close.csv plus same-day QQQ, BKNG, EXPE moves; triggers from shareholder letters, call transcripts and same-day press | Krish (Claude Code) | 2026-09-05 | 41 close-to-close moves of 7% or more, each attributed macro/industry vs company-specific with headline and KPI detail. Attribution is hand-checked, not scripted. See research/notes/2026-09-05_abnb-major-moves.md. |
| processed/abnb_earnings_reactions.csv | Theo's guidance dataset (`theos-past-research/research/guidance/data/normalized/market_returns.csv`, Nasdaq closes vs QQQ) | Krish (Claude Code) | 2026-09-05 | 1/5/20-session ABNB, QQQ and excess returns for all 23 prints Q4 2020 to Q2 2026. Rebuild with `python analysis/src/abnb_from_theo_guidance.py`. Q2 2026 20-session window incomplete at Theo's 3 Sep cutoff. |
| processed/abnb_revenue_guidance_vs_actual.csv | Theo's guidance dataset (`guidance_items.csv`, `quarterly_actuals.csv`, from SEC-filed shareholder letters) | Krish (Claude Code) | 2026-09-05 | Next-quarter revenue guide range, midpoint, actual, beat vs midpoint and vs top, Q4 2021 to Q3 2026 (20 numeric guides). Same rebuild script. |
| processed/abnb_edgar_quarterly_kpis.csv | SEC EDGAR XBRL companyfacts, CIK 1559720 | Theo (Claude Code) | 2026-09-05 | 20 quarterly revenue + 23 deferred-revenue points, 2020Q1-2026Q2. Public domain. Rebuild: `python analysis/src/acquisition/run_edgar_filings.py`. |
| processed/abnb_filing_kpis.csv | ABNB 10-Q/10-K primary documents (SEC EDGAR) | Theo (Claude Code) | 2026-09-05 | 368 KPI sentences from 14 filings 2023Q1-2026Q2, tagged nights_booked/gbv/adr/rnpl, 50 carrying figures. Evidence-grade not series-grade: the clean KPI tables are HTML tables, not prose. Public domain. |
| manifests/*.csv | Acquisition provenance for every file pulled | Theo (Claude Code) | 2026-09-05 | Append-only logs: source, URL, HTTP status, byte count, SHA-256, licence tier. Bulk data itself lives on an external volume - see below. |
| processed/booking_curves_by_market.csv | Derived from 588M Inside Airbnb calendar rows | Theo (Claude Code) | 2026-09-05 | 600 rows: blocked-night rate by market x snapshot x horizon bucket (0-30/31-60/61-90/91-180/181-372 days ahead), 120 markets, 35 countries. Rebuild: `python analysis/src/build_booking_curves.py`. **blocked_rate is a bounded proxy - `available='f'` conflates booked, host-blocked and inactive. Never call it occupancy.** |
| processed/booking_curve_daily.csv | Same source, daily granularity | Theo (Claude Code) | 2026-09-05 | 44,379 rows: blocked rate by market x snapshot x days_ahead (0-372). Same caveat. |
| processed/market_summary_2026.csv | Inside Airbnb listings, 2026 vintage (incl. frozen v1, read-only) | Theo (Claude Code) | 2026-09-05 | 120 markets: listings, hosts, entire-home/multi-host/superhost/licence-disclosure shares, median asking price (native currency, no FX), availability, review flow, ratings. Rebuild: `python analysis/src/build_market_summary.py`. |
| processed/abnb_quarterly_costlines.csv | SEC XBRL company facts (CIK 1559720) plus Adjusted EBITDA from shareholder letters | Krish (Claude Code) | 2026-09-05 | Quarterly GAAP cost lines incl. SBC, % of revenue, Adj. EBITDA margin, 1Q20 to 2Q26. Rebuild with `python analysis/src/abnb_costlines_from_xbrl.py`. Q4 = FY less 9M; ops & support backed out of total costs. |
| processed/abnb_quarterly_kpis_from_study.csv | research/airbnb_earnings_call_study.md table 3.1 (shareholder letters) | Krish (Claude Code) | 2026-09-05 | Nights, GBV, ADR, revenue, Adj. EBITDA, take rate by quarter, 1Q21 to 2Q26. Since 2026-09-05 a cross-check only: `abnb_exsbc_stack.py` parses nights, GBV and ADR from the letters and stops if any quarter differs from this file (all 22 match; implied ADR = GBV / nights within $0.50). Still the KPI input to `abnb_kpi_vs_category.py`. |
| processed/abnb_quarterly_cost_stack_exsbc.csv | Shareholder letters (SBC by function footnote, Adj. EBITDA reconciliation, KPI box and quarterly summary table for nights, GBV, ADR) plus abnb_quarterly_costlines.csv; 1Q21 and 2Q21 SBC by function from the 10-Q footnotes (accessions 0001628280-21-010389, 0001628280-21-016979, hardcoded in the script) | Krish (Claude Code) | 2026-09-05 | Cash (ex-SBC) cost per line, per night and % of revenue, D&A and add-backs, identity check to Adj. EBITDA, 1Q21 to 2Q26. Rebuild with `python analysis/src/abnb_exsbc_stack.py` (downloads letters to data/raw/letters if missing). 4Q23 gap of -$36M reflects the letter-vs-XBRL Q4 derivation; 1Q21 and 2Q21 gaps are under $1M. |
| processed/abnb_margin_bridge.csv | abnb_quarterly_cost_stack_exsbc.csv | Krish (Claude Code) | 2026-09-05 | Adj. EBITDA margin bridge FY2022, FY2023, FY2024 to FY2025 by cost line (cost per night), revenue per night (take rate, FX, ADR ex-FX) and add-backs. `python analysis/src/abnb_margin_bridge.py`. |
| processed/abnb_margin_scenarios.csv | abnb_quarterly_cost_stack_exsbc.csv, Aug 2026 outlook | Krish (Claude Code) | 2026-09-05 | Base, bear, bull for FY2026E, FY2027E, Q3 2026E and implied Q4 2026E. Assumptions are in the SCEN dict of `analysis/src/abnb_margin_bridge.py` and in research/notes/2026-09-05_margin-drivers.md section 11. |
| processed/abnb_fcf_bridge.csv | Shareholder letters: Adj. EBITDA reconciliation (interest income and expense, tax provision, other income, D&A, SBC), Free Cash Flow reconciliation (CFO, capex, FCF), balance sheet (unearned fees, funds payable); cash taxes paid from the 10-K via XBRL as a memo | Krish (Claude Code) | 2026-09-05 | Quarterly 1Q21 to 2Q26 plus FY2021 to FY2025: Adj. EBITDA + interest income - interest expense - tax provision - other (income) expense + change in unearned fees + residual = CFO, less capex = FCF; TTM margins and FCF / Adj. EBITDA. CFO - capex ties to the letters' FCF in every quarter. Each quarter comes from its own letter; 2Q24, 4Q24 and 1Q26 letters run table cells together and are read from the next letter's column (source_letter column). Interest expense is folded into other income in the 1Q24 to 4Q25 letters. Rebuild with `python analysis/src/abnb_fcf_bridge.py`. |
| processed/abnb_vs_bkng_annual.csv | SEC XBRL company facts for ABNB (CIK 1559720), BKNG (1075531), EXPE (1324424) in `data/raw/xbrl/` (downloaded if missing); ABNB GBV, D&A, Adj. EBITDA from abnb_quarterly_cost_stack_exsbc.csv and capex from abnb_fcf_bridge.csv; ABNB brand and performance marketing from the 10-K S&M split; BKNG gross bookings from Q4 earnings press releases (hardcoded with source) | Krish (Claude Code) | 2026-09-05 | FY2021 to FY2025 per company: revenue growth, take rate, marketing % revenue, personnel % revenue (BKNG), SBC % revenue, operating margin, EBITDA proxy (op. income + D&A + SBC) margin, ABNB reported Adj. EBITDA margin, FCF margin, FCF conversion, buybacks % FCF, diluted share change. EXPE take rate blank (gross bookings not in XBRL). Rebuild with `python analysis/src/bkng_head_to_head.py`. |
| processed/hotel_price_monitor_monthly.csv | FRED CPI lodging away from home (`data/raw/fred/CUSR0000SEHB.csv`), BEA hotels and motels price index (`data/raw/bea/`), ABNB ADR from abnb_quarterly_cost_stack_exsbc.csv, ex-FX ADR growth as stated in the 4Q25 to 2Q26 letters (hardcoded) | Krish (Claude Code) | 2026-09-05 | Monthly 2023-01 to 2026-07: CPI lodging y/y, BEA hotel price y/y, ABNB ADR y/y on quarter-end months with the letter's reported and ex-FX figure where given. Oct 2025 CPI missing at source. Rebuild with `python analysis/src/hotel_price_monitor.py`. |
| processed/abnb_kpi_vs_category_quarterly.csv | ABNB KPIs from `research/airbnb_earnings_call_study.md` 3.1 (shareholder letters) + BEA PCE travel panel (`data/raw/bea/bea_pce_travel_monthly_2015_2026.csv`, BEA NIPA underlying Table 2.4.x U, Aug 2026 release) + FRED CPI (`data/raw/fred/`) | Krish (Claude Code) | 2026-09-05 | 1Q21 to 2Q26: nights, GBV, ADR, revenue, EBITDA, take rate next to BEA accommodations / hotels nominal, real and price y/y, inbound and outbound foreign travel, CPI lodging and airfare. Derived: implied ADR (GBV/nights), real ADR y/y, nights-minus-category share gap. Rebuild with `python analysis/src/abnb_kpi_vs_category.py`. BEA is US-resident spend only. |
| raw/xbrl/ABNB.json, BKNG.json, EXPE.json | SEC XBRL company facts API (`https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`) | Krish (Claude Code) | 2026-09-05 | Full company-facts JSON (1 to 3.5 MB each), gitignored; `bkng_head_to_head.py` downloads them if missing. Same files as the citadel-abnb-margin worktree. |
| raw/fred/CUSR0000SEHB.csv, CUSR0000SETG01.csv, CPIAUCSL.csv | FRED keyless CSV (`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>`) | Krish (Claude Code) | 2026-09-05 | CPI lodging away from home (SA), airline fares (SA), all items (SA), monthly to Jul 2026. Oct 2025 lodging value is missing at source (shutdown gap). Small text files, kept in git as an exception to the raw rule. |
| raw/bea/bea_pce_travel_monthly_2015_2026.csv | BEA NIPA underlying detail Tables 2.4.4U/2.4.5U/2.4.6U (PCE by type of product, monthly), Aug 2026 release | Krish (Claude Code) | 2026-09-05 | Accommodations, hotels and motels, air transportation, foreign travel in the US, foreign travel by US residents: nominal SAAR, real, price index, 2015-01 to 2026-07. Long format (date, series, measure, value). Copy of the ABNB-Crossover extract so `abnb_kpi_vs_category.py` runs from this repo alone. 390 KB text, kept in git as an exception to the raw rule. |

`raw/` is gitignored except this log - put the actual files in the shared Drive if they're large or licensed, and record them here.
`processed/` files should be reproducible by running something in `analysis/src/`.

## Alt-data cohort (2026-09-05, Theo)

Bulk files are **not** in the repo - too large for git, per CONTRIBUTING. They live on an
external volume and are fully described by `data/manifests/`, with a SHA-256 for every file.

| Cohort | Scope | Size | Licence |
|---|---|---|---|
| Inside Airbnb current | 120 markets incl. **all 34 US**, listings + calendar + reviews (calendars are 5-col: NO price) | ~10 GB | CC BY 4.0 |
| Municipal STR registries | 25 datasets, 17 portals, 109,343 rows. Austin daily active-STR counts (527 dates); California TOT, 482 cities x 8 fiscal years | 28 MB | Open government |
| Eurostat `tour_ce_*` | Platform-sourced guest nights/stays, 32 countries, 2018-2026 monthly, NUTS 1/2/3 + cities | 6.8 MB | Eurostat re-use |
| FRED | 10 macro series incl. CPI lodging-away-from-home (ADR proxy) and trade-weighted USD | 1.1 MB | Public domain |
| SEC EDGAR | XBRL companyfacts + 14 10-Q/10-K primary documents | 20 MB | Public domain |
| Zenodo / Figshare / Dataverse | Academic replication packages | small | Per-record |

**Not committed, by design:** FactSet transcripts and Bloomberg terminal exports are licensed
and live in the private shared Drive, per CONTRIBUTING. They appear in the manifests as
references with `license_tier=licensed_norestribute` so provenance stays complete, but no
licensed content is in this public repo.

**Known blockers (lawful, not worked around):**
- Harvard Dataverse AirDNA-derived sets (Venice, Reykjavik, Boston MSA daily) require a
  Guestbook form response - must be completed manually in a browser.
- Inside Airbnb retired snapshots: ~39% return HTTP 403. Country-consistent, verified with
  paced retries as a source decision, logged and respected.
- TSA passenger volumes returns 403 to non-browser clients; FRED air revenue passenger miles
  is used instead rather than spoofing a user agent.

### Correction 2026-09-05: current calendars carry no price

Inside Airbnb's **2026** `calendar.csv.gz` has 5 columns -
`listing_id, date, available, minimum_nights, maximum_nights`. **There is no price column.**
Verified across 8 markets on 3 continents. The 2019-20 legacy files had 7 columns and did
carry price; do not generalise from them.

Consequence: **realised ADR is not obtainable** from this data. `listings.price` is an
*asking* price for a single scrape date (~76% populated, format `$1,234.56`) and must never
be presented as ADR or reconciled to the company's reported ADR without stating the gap.

What calendars DO give is a **372-day forward booking curve** per listing - see
`processed/booking_curves_by_market.csv`.
