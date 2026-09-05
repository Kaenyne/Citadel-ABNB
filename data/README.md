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
| processed/abnb_driver_history_quarterly.csv, abnb_revenue_decomposition.csv, abnb_reaction_inputs.csv, abnb_reaction_regression.csv, abnb_reaction_regression_loo.csv, abnb_valuation_scenarios.csv, abnb_valuation_sensitivity.csv, abnb_reverse_dcf.csv, abnb_multiples_today.csv | Derived: KPI study table, XBRL cost lines and capital-return panel (krish/margin-drivers), margin scenarios (same branch), Theo's guidance dataset (FX split, guides), earnings reactions, 30 Jun 2026 balance sheet from XBRL, 4 Sep 2026 close | Krish (Claude Code) | 2026-09-05 | Driver model: quarterly history with y/y and LTM; revenue growth decomposed into nights, ADR ex-FX, FX, take rate; OLS of day-1 and day-5 excess returns on beat, guide acceleration, margin and nights (18 prints, with leave-one-out); FY2026E-FY2028E bear/base/bull to FCF per share and prices on EV/EBITDA, EV/FCF, P/SBC-adjusted FCF and an earnings proxy; sensitivity grids; reverse DCF. Rebuild: `py -3.13 analysis/src/abnb_driver_model.py` after krish/margin-drivers is merged (needs statsmodels). Assumptions: model/assumptions.md. Write-up: research/notes/2026-09-05_driver-model.md. |
| processed/booking_curves_by_market.csv | Derived from 588M Inside Airbnb calendar rows | Theo (Claude Code) | 2026-09-05 | 600 rows: blocked-night rate by market x snapshot x horizon bucket (0-30/31-60/61-90/91-180/181-372 days ahead), 120 markets, 35 countries. Rebuild: `python analysis/src/build_booking_curves.py`. **blocked_rate is a bounded proxy - `available='f'` conflates booked, host-blocked and inactive. Never call it occupancy.** |
| processed/booking_curve_daily.csv | Same source, daily granularity | Theo (Claude Code) | 2026-09-05 | 44,379 rows: blocked rate by market x snapshot x days_ahead (0-372). Same caveat. |
| processed/market_summary_2026.csv | Inside Airbnb listings, 2026 vintage (incl. frozen v1, read-only) | Theo (Claude Code) | 2026-09-05 | 120 markets: listings, hosts, entire-home/multi-host/superhost/licence-disclosure shares, median asking price (native currency, no FX), availability, review flow, ratings. Rebuild: `python analysis/src/build_market_summary.py`. |

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
