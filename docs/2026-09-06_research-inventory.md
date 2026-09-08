# ABNB research inventory: everything we have, as of 6 Sep 2026

Compiled by Krishang with Claude Code, 6 Sep 2026, from a read-only pass over the GitHub repo (main, origin/main, every open branch and worktree, Theo's archive) and Theo's OneDrive share. Every number below is quoted from a note, CSV or script in the repo; where two notes disagree the later or audited figure is used and the conflict is flagged.

Reading order if you have ten minutes: section 1 (where things live), section 5.1 (the thesis the overnight synthesis reached), section 6 (claims to stop making), section 7 (what to do before 5 November).

---

## 1. Where things live

### 1.1 The repo

| Location | State | What is there |
|---|---|---|
| `origin/main` (9c3dc97) | canonical | Theo's alt-data acquisition layer (PRs #9, #10), the pitch landscape and catalogue, management timeline, major-moves study, Third Bridge digest, the 22-quarter earnings-call study, Theo's Codex archive (`theos-past-research/`), two of Jessie's zip drops still unpacked at the root |
| local `main` | 5 commits behind origin; 86 untracked files | Untracked: the regulatory package (`research/regulatory/`, 11 scripts, SQLite), `ABNB-Crossover/`, the options ledger, older copies of the driver-model and supply-panel outputs. The audit warns this tree holds stale, uncorrected copies; do not port fixes into it blind |
| `krish/overnight-synthesis` (worktree `../citadel-abnb-overnight`, unpushed) | **the most complete branch**: 509 files, 331,925 insertions vs origin/main | Union-merges all eleven open branches, then the 6-7 Sep overnight run (workstreams 01-15), follow-ups 16-18 and audit repairs 19-26. Framed as PR #16; on merge it closes PRs #5, #8, #11-#15 |
| PRs #8, #11, #12, #13, #14, #15 (worktrees `../citadel-abnb-margin-gaps`, `-supply`, `-cc`, `-model`, `-eu`, `-reg`) | open | margin drivers, Inside Airbnb supply panel, Common Crawl panel, driver model v1, Eurostat/backlog, regulatory forecast |
| `krish/capital-return-panel`, `krish/predictive-study`, `krish/transcript-analytics`, `krish/guidance-margin-items` | local branches, no PR | capital-return panel, predictive study (five sub-notes), transcript analytics, 44 margin guides added to Theo's guidance dataset |
| `origin/krish/plan-of-attack` (PR #5) | open | the 5 Sep plan: branch split, ten build branches, cadence to the Q3 print |

Merge order is forced: margin-drivers first, then driver-model, capital-return and predictive-study (they read its CSVs). Source IDs collide across branches (S32-S37 each used twice); the overnight branch renumbered them S40-S45.

### 1.2 Theo's OneDrive share ("Citadel - ABNB")

Downloaded 6 Sep to `data/raw/theo_onedrive/AIRBNB DATA/` (420 MB, gitignored). Not downloaded: `raw_expansion/v2_2026-09-05/` (2.8 GB of single-vintage Jun-Aug 2026 Inside Airbnb dumps for about 60 markets, none in our 13-city panel except London; re-downloadable from the Inside Airbnb CDN).

What is unique there:
- **Bloomberg options workbook** (built 4 Sep, cached values): daily implied and realised vol, put/call ratios and option volume since the IPO (1,436 rows); ATM IV term structure 30D to 12M with 90/95/105/110 moneyness; 67 monthly ATM straddles Jan 2021 to Sep 2026 (implied vs realised; average implied 10.4%, realised 10.7%; Aug 2026 implied 10.0% vs realised 33.7%); full chain on 4 Sep (1,255 contracts with IV).
- **Bloomberg long export** (6,365 rows, licensed): PX_LAST and 30-day vol daily; comps for ABNB, BKNG, EXPE, H, HLT, IHG, MAR (ABNB 26.3x EV/EBITDA, 41.3x P/E, $108.9B cap on 5 Sep); target price and analyst-rating history; BEST_SALES/EBITDA/EPS by period. **Caveat: the "consensus time series" is anchored to the pull date (FY1 revenue at 31 Dec 2020 reads 14,270), so it is a revision history of the FY26/Q3 26 estimates, not point-in-time consensus at each print.**
- **Bloomberg FA consensus PDF** (6 pages): quarterly 3Q24 to 4Q26E for revenue (3Q26E $4,743.7M, 4Q26E $3,154.0M), nights (148.9M / 134.2M), GBV, ADR, take rate, EBITDA, FCF, SBC, regional revenue and balance sheet.
- **FactSet transcripts** Q4 2020, Q4 2021, Q4 2022 (not in the repo's IR archive, which starts Q1 2023) plus Q3 23, Q2 24, Q2 25.
- Handoff docs V2/V3 and `A_LEVEL` describing Theo's 315-file, 9.2 GB, 120-market Inside Airbnb store (on his external SSD, not on the share) and the v1/v3 processed panels. **17 of the 20 v3 E-series artifacts listed in the manifest (hotel nights, TSA throughput, Wikipedia pageviews, regulatory events, app engagement, listing and review fact tables) are not on the share.** Only `market_lodging_tax.csv` (14 US markets, mostly annual) and `cohort_status.csv` synced.
- V3 §0.1 corrections worth knowing: US historical Inside Airbnb dumps do return 200 for latest-2025 snapshots (17 of 17 US markets), reversing V2's "US 0%"; TSA passenger volumes now return 200.
- A `.secrets/env.sh` with Theo's API tokens is on the share; not read; he should remove it.

### 1.3 Theo's external SSD (described, not held)

Inside Airbnb current cohort: 120 markets, 35 countries incl. all 34 US: 982,188 listing rows, 588,120,594 calendar rows, 67,500,188 review rows. Municipal STR registries: 25 datasets, 17 portals, 109,343 rows (Austin daily active licences 527 dates; California TOT 482 cities x 8 FY). Harvard Dataverse daily STR replication files (210 MB + 370 MB). All fully described by SHA-256 in `data/manifests/`.

---

## 2. Data we hold

### 2.1 Company financials and KPIs (all rebuildable)

| Dataset | Grain / coverage | Where | Notes |
|---|---|---|---|
| Definitive KPI panel, 119 columns | quarterly 1Q21-2Q26 (24 quarters) | overnight `02_kpi_panel_quarterly.csv`; predecessors `abnb_quarterly_kpis_from_study.csv`, `abnb_driver_history_quarterly.csv` | nights, GBV, ADR, revenue, take rate, adj. EBITDA, SBC, cost lines, regional shares; 342 verbatim quotes re-verify |
| GAAP cost lines from XBRL | 1Q20-2Q26 | `abnb_quarterly_costlines.csv` (margin branch) | Q4 = FY less 9M; ops & support backed out |
| Cash (ex-SBC) cost stack, per night and % revenue | 1Q21-2Q26 | `abnb_quarterly_cost_stack_exsbc.csv`; overnight `07_cost_lines_per_night` with a brand-vs-field S&M split | identity holds within $2M except 4Q23 |
| Margin bridge and scenarios | FY22 to FY25 bridges; bear/base/bull FY26-FY27 | `abnb_margin_bridge.csv`, `abnb_margin_scenarios.csv` | |
| FCF bridge | 1Q21-2Q26 and FY21-FY25 | `abnb_fcf_bridge.csv` | CFO less capex ties to the letters in all 22 quarters |
| Capital return panel | 1Q21-2Q26 | `abnb_capital_return_quarterly.csv`; peer scorecard `capital_return_scorecard_annual.csv` (ABNB, BKNG, EXPE, META, NFLX, UBER, DASH) | |
| Backlog indicators (unearned fees, funds held) | 4Q20-2Q26 | `abnb_backlog_indicators.csv` (EU branch, leakage fixed by audit A01 on overnight) | |
| Regional panel, 79 columns | 23 quarters | overnight `10_regional_panel.csv` from 766 tagged letter sentences plus XBRL geography | share-weighted sum reconciles to total nights within 1.1pp |
| ABNB vs BKNG vs EXPE annual | FY21-FY25 | `abnb_vs_bkng_annual.csv` | |
| Theo's EDGAR extracts | 2020Q1-2026Q2 | `abnb_edgar_quarterly_kpis.csv` (43 rows), `abnb_filing_kpis.csv` (368 KPI sentences) | evidence-grade, not series-grade |

### 2.2 Guidance and consensus

| Dataset | Coverage | Where | Notes |
|---|---|---|---|
| Guidance ledger, 194 statements (159 scoreable) | all 23 prints | overnight `02_guidance_ledger.csv`; Theo's `guidance_items.csv` (100 rows, plus 44 margin guides from `krish/guidance-margin-items`) | ranges, floors, points, ceilings, buckets, directional |
| Revenue guide vs actual | 4Q21-3Q26 | `abnb_revenue_guidance_vs_actual.csv` | 19 of 19 beat the midpoint, 15 above the top |
| **Consensus at all 23 prints** | revenue 23/23, next-Q revenue 18/23, EPS 17/23, nights 18/23, GBV 12/23, EBITDA 8/23, ADR 5/23 | overnight `04_consensus_at_print.csv` from 145 sourced press/vendor quotes (LSEG, Refinitiv, StreetAccount, Zacks) | closes the biggest hole in Theo's archive (his `consensus_snapshots.csv` is 23 rows of "missing"). Vendors spliced; keep the vendor column |
| Current Street (3-4 Sep 2026) | Q3 26 to FY27 | overnight `04_*`, `12_analyst_targets.csv` (466 actions, 31 live targets) | Q3 revenue $4.74bn, Q4 $3.20bn (21% spread), FY27 $15.73-15.76bn; mean target $178.96, 46% Hold or worse |

### 2.3 Stock, market and options

| Dataset | Coverage | Where |
|---|---|---|
| Daily closes ABNB and 20 tickers, Ken French factors, 466 sell-side actions, 84 short-interest settlements | Dec 2020 to 4 Sep 2026 | `abnb_daily_close.csv`; overnight WS09 outputs |
| 41 moves of 7%+ since IPO, attributed | | `abnb_major_moves_events.csv` |
| 1/5/20-session reactions to all 23 prints (now on an executable next-open entry) | | `abnb_earnings_reactions.csv`; overnight `20_event_returns_executable.csv`, 391-row prediction ledger |
| Monthly ABNB multiples, point-in-time on last-reported LTM; 19-name peer cross-section 4 Sep | 2021-2026 | overnight `12_abnb_multiples_monthly.csv`, `12_peer_multiples.csv` |
| Options ledger (Yahoo, current chains) | run 5 and 6 Sep | `abnb_options_ledger.csv`; the Bloomberg workbook on OneDrive is the historical upgrade |

### 2.4 Transcripts and language

- 23 earnings calls Q4 2020 to Q2 2026: IR-hosted FactSet PDFs for Q4 21 and Q1 23 onward, stockanalysis.com text for the rest (`data/raw/transcripts/`, gitignored). The OneDrive FactSet files add Q4 20, Q4 21, Q4 22 in corrected form.
- 23 shareholder letters (SEC 8-K Ex. 99.1), parsed for KPIs, SBC-by-function footnotes and outlook sentences.
- Derived: call roster (317 analyst-call rows), churn, 14-topic mix per call, 37 hand-verified "declined to quantify" instances (`krish/transcript-analytics`); 1,677 speaker turns and 132 language features per print, 83 management claims scored for credibility (overnight WS03).
- Five Third Bridge expert transcripts (May-Aug 2026), digested in `research/notes/2026-09-05_third-bridge-transcripts.md`. **The licensed PDFs are still tracked on origin/main under `research/` despite the sources log saying they were purged.**

### 2.5 Supply-side alternative data

| Source | What we hold | Where |
|---|---|---|
| **Inside Airbnb** | 13 cities (NYC, LA, Chicago, Austin, Nashville, New Orleans, San Diego, Paris, London, Barcelona, Rome, Sydney, Mexico City), 168 dumps Dec 2022 to Aug 2026 (2.6 GB raw, gitignored); city snapshots, like-for-like pairs (now with `pair_eligible` flags), host concentration; 1.71M fee-inclusive quotes Mar-Aug 2026; hedonic panel of 2.85M listing-dumps | PR #11; overnight WS06/WS08/WS21 |
| **Common Crawl** | 2.08M CDX rows over 50 crawls (2021-2026), 1.2M unique listing ids, 3,000 WARC renders, 1,500 matched pairs; survival by crawl and by age | PR #12 |
| **Booking curves** (Theo) | blocked-night rate by market x snapshot x horizon, 120 markets, 44,379 daily rows; single Jun 2026 vintage | origin/main `booking_curve_daily.csv`, `booking_curves_by_market.csv` |
| **Market summary 2026** (Theo) | 120 markets: listings, hosts, entire-home / multi-host / superhost / licence shares, native-currency median price | origin/main `market_summary_2026.csv` |
| **Austin daily active STR licences** (Jessie) | 527 dates, by type and district | in `citadel-abnb-austin-rnpl-hotels.zip` at the repo root, never unpacked |

### 2.6 Category, macro and demand data

- **Eurostat `tour_ce_omr`**: EU27 + 31 countries platform nights, monthly Jan 2018 to Mar 2026 (PR #14). Theo also pulled seven other `tour_ce_*` datasets and `tour_occ_nim` hotel nights (on his SSD / v3, not synced).
- **BEA PCE travel panel**: 10 series nominal/real/price, monthly 2015 to Jul 2026 (committed as an exception to the raw rule); **FRED**: CPI lodging, airfares, all-items, plus 16 series on the predictive branch and 28 re-pulled on overnight WS05, cached in `05_fred_cache/`.
- **FX schedule**: EUR/USD and broad-dollar paths to 4Q27 with the fitted ADR-FX and revenue-FX contributions (`05_fx_schedule.csv`); regional currency baskets (WS10).
- **Peer prints**: 93 8-K Ex. 99.1 releases for BKNG, EXPE, MAR, HLT parsed to KPIs with sentence and URL (predictive branch); BKNG alternative-accommodation nights derived (WS11).
- **Google Trends**: 9 terms, US and worldwide, 2019 to Sep 2026 (WS08); not point-in-time (Google renormalises on every pull).
- Air traffic (TSA, IATA, BTS), NTTO inbound, hotel CPI/BEA price monitors, CoStar/AirDNA monthly figures quoted from public releases.

### 2.7 Regulatory

- 32-factor register (REG-01 to REG-32, four tiers), 48 source records, 9-observation earnings digest, SQLite database with full-text search, per-market supply-at-risk inventory (20 Inside Airbnb snapshots, INE Spain series, RNAL, ELSTAT, Scotland, BC), identifier-matched cohorts (Barcelona 5,146 HUTB licences, Maui 3,862 unit ids across 92 parcels), Hawaii DBEDT monthly vintages, the NYC CRA guest-nights benchmark, two editable sensitivity workbooks. All untracked in the main tree (planned `krish/regulatory-db`, never opened as a PR).
- 20-event probability table and Monte Carlo outputs (PR #15; dependency structure fixed by audit A06 on overnight).

### 2.8 Licensed material (never commit)

Bloomberg options workbook, Bloomberg long export and PDF (OneDrive); FactSet transcripts (OneDrive); LSEG/Refinitiv story bodies (`data/raw/regulatory/lseg/`); five Third Bridge PDFs (currently tracked, must be purged); the Henry Fund PDF (link only). `.gitignore` already matches `*bloomberg*`, `*factset*`, `*capiq*`.

### 2.9 What we do not have

- **Point-in-time consensus from a terminal** (WS04's press-quote reconstruction is the stand-in; Bloomberg's pull is revision history, not point-in-time).
- **Occupancy**: nothing measures it; the booking curve is a blocked-night rate.
- **Realised ADR from any free source**: 2026 Inside Airbnb calendars have no price column; Common Crawl carries none in 3,000 renders.
- Quarterly ADR ex-FX before 4Q25 (only three letter-stated quarters), RNPL share of GBV beyond ">20%", segment revenue for hotels / Experiences / Services, brand-vs-field S&M before 2023, headcount and SBC per employee, cross-border / urban / long-term-stay shares after 1Q24 (all stopped while decelerating).
- NYC pre/post Local Law 18 Inside Airbnb dumps (403; must be requested naming 2023-06-05, 2023-10-01, 2023-11-01, 2024-01-05, 2024-03-07).
- Theo's v3 E-series tables, his 67.5M-review store and 25 municipal registries (on his SSD).
- A true vintage (ALFRED/Eurostat revision) series for any macro input; a 13F concentration history; regional MAR/HLT RevPAR; LatAm external benchmarks; a period-end fully diluted share count.
- Card panels, app downloads, web traffic, AirDNA listing-level exports, VIC and AlphaSense content.

---

## 3. Models built

### 3.1 The driver model (overnight WS13, supersedes the 5 Sep Python model)

`model/ABNB_driver_model.xlsx`: 9 sheets, 2,353 live formulas, 216 named outputs, scenario selector on `Inputs!B4`, mirrored by `13_driver_model.py` and verified in real Excel (0 errors in 5,553 cells, 216/216 outputs and 2,353/2,353 formulas reconciling, scenario switch 144 comparisons / 0 mismatches, both audit scripts exit 0). Rebuild per `docs/overnight/BUILD.md`.

Structure: regional nights build (NA/EMEA/LatAm/APAC growth less a regulatory drag) x ADR ex-FX x ADR FX x take rate, plus an FX timing wedge, a new-business line and an AI referral cost; lever-by-lever cost stack to adj. EBITDA, GAAP operating income and net income; FCF bridge with buybacks, RSU withholding and a share-count path; six valuation lenses, a DCF ladder, a reverse DCF, a 441-cell sensitivity grid and the 5 Nov card as live formulas.

| Base case | FY2026E | FY2027E | FY2028E |
|---|---|---|---|
| Nights | 585.7M (+9.9%) | 637.6M (+8.9%) | 685.0M (+7.4%) |
| ADR | $180.32 (+5.3%) | $185.18 (+2.7%) | $189.81 (+2.5%) |
| Revenue | $14,233M (+16.3%) | $15,842M (+11.3%) | $17,947M (+13.3%) |
| Adj. EBITDA / margin | $5,158M / 36.2% | $5,686M / 35.9% | $6,704M / 37.35% |
| SBC % revenue | 12.6% | 12.4% | 11.8% |
| FCF / margin | $5,129M / 36.0% | $5,420M / 34.2% | $6,197M / 34.5% |
| Diluted shares | 588.9M | 574.6M | 561.5M |
| FCF / share | $8.71 | $9.43 | $11.04 |

Scenario anchors: FY27 nights +5.5 / +8.9 / +11.7%; revenue FX −2.6 / −0.63 / +0.9pp; take rate −15 / 0 / +15 bps; margin FY27 28.4 / 35.9 / 38.0% (38% cap); cost of equity 11.5 / 10.5 / 10.3%; **exit EV/EBITDA on FY27E 13.5 / 16.5 / 18.5x** (was 18 / 22 / 25.5x on 5 Sep).

Outputs: **football field bear $74 / base $157 / bull $228** against $181.94; the base EV/EBITDA lens alone is **$180.88**. Prices are 12-month forward targets on FY2027E exit metrics (target date ~30 Sep 2027), the FY28 lens discounted one year. Reverse DCF: $99.0bn EV needs 7.5% ten-year FCF growth on reported FCF, 13.3% on SBC-adjusted FCF (WACC 10%, terminal 3%).

Known limits: no reaction function (deliberate), no FY28 regional or FX build, new businesses at an assumed 70% incremental margin, no float model, buybacks exogenous and above the $3.4bn of remaining authorisation, no Monte Carlo, share count off a weighted-average anchor.

### 3.2 The 5 Sep driver model (PR #13, superseded)

`abnb_driver_model.py`: log-additive revenue decomposition (nights / ADR ex-FX / FX / take rate), a reaction regression on 18 guided prints, bear/base/bull FY26-FY28 through four lenses, reverse DCF. Its $176 / $248 / $325 football field rested on 18 / 22 / 25.5x exit multiples that WS12 could not support; keep it only as the labelled "if the market keeps paying 2026 multiples" sensitivity.

### 3.3 Margin lever model (PR #8 and overnight WS07)

Bottom-up from nights, ADR (ex-FX and FX), take rate, cost of revenue per GBV dollar, support cost per night, product-dev / brand / field-ops / G&A cash growth; a 40,000-draw correlated Monte Carlo to FY28 (rho 0.75). Sensitivities on the FY26 base: +1pt ADR ex-FX +0.46 margin pts, +1pt FX +0.47, +10bps take rate +0.48, support cost per night −10% +0.96, S&M cash growth +5pts −0.84. FY26 margin as a function of brand-and-performance growth: +17% → 37.0%, +25% → 36.2%, +31% → 35.5% (the floor).

### 3.4 Regulatory Monte Carlo (PR #15, repaired on overnight)

20 events with horizon probabilities, triangular conditional losses, Gaussian copula (rho 0.45 EU, 0.25 US), 200,000 draws; EU tail now nested inside its parent, Barcelona as one ordinal ladder, one correlated path per trial. Translates to EBITDA at 70% contribution and value per share at 22x.

### 3.5 Test harnesses (no alpha found, but the negatives are the result)

- Reaction function: 97 tests on consensus surprises (WS04), 189 + 180 tests on print features (predictive 04), 17 on the guide ledger (WS02), 948 on call language (WS03), 218 on stock behaviour (WS09), 195 temporal-validation specs with executable entries and a frozen spec `ABNB-WS20-v1` (WS20).
- Nowcasts: 890 macro pairs (predictive 03), 1,408 (WS05), 598 alt-data feature tests + 42 index backtests with expanding-window walk-forwards against naive / prior-year / AR(1) (WS08), 255 peer read-through cells (predictive 02), 3,446 regional correlations (WS10).
- Valuation: 77 tests on what moves the multiple (WS12).
- Others: transcript parser (`transcript_analytics.py`, 652 lines), options event-variance estimator (rewritten by A08, currently unidentified), pitch scorecard (37 calls), Inside Airbnb and Common Crawl panel builders, Eurostat/backlog builder, acquisition layer (`analysis/src/acquisition/`, Theo).

---

## 4. Figures

| Group | Files | What they show |
|---|---|---|
| Driver model v1 (PR #13) | `abnb_revenue_decomposition.png`, `abnb_reaction_function.png`, `abnb_football_field.png` | growth split into nights / ADR ex-FX / FX / take rate; the near-zero fit of day-one return on the beat; the superseded $176/$248/$325 field |
| Inside Airbnb (PR #11), 8 | `inside_airbnb_lfl_price_yoy`, `_retention_yoy`, `_reviews_ltm_yoy`, `_reviews_ltm_level`, `_multi_listing_share`, `_superhost_share`, `_listings`, `_entire_home_share` | 13-city small multiples; retention and reviews-yoy panels need the `pair_eligible` fix applied before use |
| Common Crawl (PR #12), 3 | `cc_listing_survival`, `cc_review_velocity`, `cc_professionalisation` | review velocity is the usable slide exhibit |
| Eurostat / backlog (PR #14), 3 | `eurostat_platform_vs_abnb_emea`, `eurostat_platform_country_growth`, `abnb_backlog_indicators` | category vs ABNB EMEA; regulated countries at the bottom; the RNPL break in unearned fees |
| Regulatory (PR #15) | `abnb_regulatory_profile.png` | loss distribution 2027 vs 2030 and expected loss by event |
| Stock reactions (PR #6) | `abnb_major_moves.png` | closes since IPO annotated with 41 moves of 7%+ |
| Overnight, 24 | `02_guidance_cushion`, `03_theme_timeline`, `03_feature_vs_reaction`, `03_event_study`, `05_fx_mechanism`, `05_macro_vs_nights`, `05_sensitivity_bars`, `08_indexes_vs_kpis`, `09_rolling_betas`, `09_variance_decomposition`, `09_earnings_drift`, `09_seasonality`, `09_rules_backtest`, `09_positioning`, `10_regional_nights_growth`, `10_regional_revenue_mix`, `10_regional_forecast`, `11_alt_accom_growth`, `12_abnb_multiples_history`, `12_abnb_multiple_drivers`, `12_abnb_lens_tracking`, `12_exit_multiple_evidence`, `12_analyst_targets`, `12_peer_crosssection` | the deck-grade set; `12_exit_multiple_evidence` and `11_alt_accom_growth` carry the thesis |
| Jessie's Austin drop, 3 | `05_austin_daily_active_str`, `06_austin_str_by_type`, `07_austin_str_by_district` | licences 2,268 → 2,920 (+29% in 18 months), owner-occupied types shrinking, Type 2 +78% |
| Bloomberg ALTD screenshot (OneDrive) | | app time, downloads, web visits, observed sales monthly y/y 2017-2026 |

No figures are committed on the margin, capital-return, predictive or transcript-analytics branches (table-based notes).

---

## 5. Conclusions

### 5.1 The thesis the overnight synthesis reached

**The stock is priced at the base case, and the prior "buy" case was an exit multiple no evidence supports.** The base 12-month target fell from $248 (5 Sep) to $181 (7 Sep); $55 of the $67 is the multiple, the rest is a net-cash correction (RSU withholding was never subtracted), a share-count double-count and small EBITDA changes. WS12 attacked the exit multiple three ways (ABNB's own multiple vs forward growth 2023-26, a 19-name cross-section, a fade DCF) and all three land below 18 / 22 / 25.5x; recommended 13.5 / 16.5 / 18.5x. The highest live sell-side target ($220) implies 19.3x on FY27E, the mean ($178.96) 15.4x, the whole tape 10.1-19.3x.

**Growth is the only fundamental that has moved this multiple**: +0.48 turns of EV/EBITDA per point of forward revenue growth (t 8.3 in levels, +0.49 t 5.6 in 12-month changes); margin moves it zero (t 0.3). Print days are re-ratings: 71% of the absolute move is multiple (84% on moves of 7%+); 2Q26's +17.4% came with an estimate change of −0.2%.

**Once SBC is charged the market pays ABNB nothing for being ABNB**: EV/NTM SBC-adjusted FCF 27.3x vs a peer median of 27.2x. The seven-turn gap between a 19.7x reported-FCF DCF and a 12.7x SBC-adjusted one (~$70 a share) is the SBC debate.

A long therefore has three honest routes to upside and must pick one: (1) FY27 revenue above ~$16.0bn (model $15.84bn, Street $15.73-15.76bn); (2) SBC below ~10% of revenue (it is 12.9%); (3) a separately named and sized optionality bucket (WS11: $235M / $914M / $1,987M = 1.4% / 5.4% / 11.7% of FY28 revenue).

**The variant perception**: the market is arguing about whether the 2026 nights re-acceleration is real. It is, and it is priced (13.3x forward EBITDA in Nov 2025 to 18.2x). Not priced: (a) the dateable FY27 dollar lap, and (b) that half of ADR growth is a bigger unit, not a higher price (Bedroom Nights Booked +12% vs nights +10% in 2Q26, implying at least 1.786 bedrooms per night and at most $102.87 per bedroom-night vs $172 for a US hotel room).

`research/thesis.md` is still the empty template; the synthesis supplies the text.

### 5.2 What predicts what (about 3,500 tests; five survivors)

1. **The dollar forecasts the FX part of ADR**: `ADR FX (pp) = 0.52 − 0.715 x broad USD y/y` (r −0.96) or `−0.61 + 0.460 x EUR/USD y/y` (r +0.99), walk-forward RMSE 0.44x naive, sign right 8 of 10. The only genuine out-of-sample forecast the team owns.
2. **Guide midpoint plus trailing cushion forecasts the revenue level** (MAE 1.1%; 19 of 19 above the midpoint, 15 of 19 above the top; cushion trailing-8 median +1.79%). It is the worst baseline for the surprise vs Street.
3. **Revenue FX lags spot by one to two quarters** (revenue recognised at check-in): `revenue FX = −0.640 + 0.413 x mean(EUR/USD y/y at t−1, t−2)`, r +0.80, predicts +2.19pp for 3Q26 vs management's +3.0pp. **4Q26 is −0.4pp under all three dollar paths, 84% already determined: a ~3.4pp mechanical step-down in reported growth with no demand change.** 3Q27 prints the slowest revenue growth of the path (+9.9%) on unchanged nights (+8.9%).
4. **"Guide below Street" is a binary risk flag**: 9 of 9 such prints negative at 20 days, mean −4.21% on an executable entry, base-rate p 0.038 (n 9, exploratory). The day-1 half of the rule collapses on an executable entry.
5. **BKNG room-night acceleration is a coincident check** (r +0.91 with total nights, +0.88 EMEA, n 7) and prints ~8 days earlier.

Everything else fails: nothing predicts the day-one move (every day-1 spec has negative LOO R² across four independent studies; 73% of the historical day-1 "signal" is the overnight gap); the beat is a constant (22 of 23 vs consensus, 19 of 19 vs guide); Google Trends (0 of 162 beat naive); Eurostat as a nowcast (150-day lag, lead correlation −0.11); the Inside Airbnb panel as built (n = 0 usable year-ago quarters on the fixed 13 cities; listings y/y 3.6x worse than naive); macro (Michigan sentiment vs nights r −0.05; every nights-level hit is the 2023 normalisation); management tone (948 tests, zero survive BH); peer read-across; short interest; analyst actions outside print weeks; all three composite alt-data indexes (lose to "same as last quarter"). Funds held for clients is window-dependent (0.60x AR(1) from 2023Q1, 1.85x from 2022Q1) and confounded by RNPL. Air traffic stopped predicting nights in 2024 (TSA vs nights +0.84 → +0.16). The oil vs North America revenue relationship was tested and marked spurious.

Nights acceleration sets the sign of the day-1 move (15 of 19 to 17 of 21 depending on definition; margin met + nights accelerating averaged +5.0%, margin met + decelerating −2.1%), but only as a sign rule known at the print.

### 5.3 KPI and operating facts

- Nights +7-10% for ten straight quarters (2Q26 148.3M, +10%); reported revenue +17-18% in 1H26, ~3pts FX; ex-FX +13% in 2Q26. Decomposition 2Q26: nights 10.6pts, ADR ex-FX 1.6, FX 4.0, take rate +0.7.
- The 2025-26 re-acceleration is three product changes (RNPL, cancellation redesign, single fee: ~2-3pts nights, ~3-4pts GBV), not AI. RNPL >20% of GBV, ~70% adoption of eligible, +1pt cancellations, laps US 3Q26 and global 1Q27.
- Take rate 13.2-13.3% flat y/y, LTM −31bps, guided flat; seasonal path 9.2 / 13.2 / 17.9 / 13.6%; single 15.5% host fee on ~50% of listings, all by year-end (worth +40-45bps fully migrated, not 200-300bps); the 29 Aug 6-10% host-fee pilot is worth 0-15bp of FY27 take rate. Three of five experts say the OTA take rate is at a ceiling ("Airbnb and the rest have set a plateau").
- Regional: NA 29% of nights / 42% of revenue (US 39.3% of revenue vs 50.0% in 2021); LatAm + APAC 31% of nights and delivered 52% of 2Q26 growth; NA was an inbound shock (BEA foreign travel in the US −9.9% in 3Q25, Canadians returning −31%) now reversing; NA revenue +3.0% (3Q25) → +15.8% (2Q26).
- Share: Airbnb's nights growth is ~5x AirDNA US category demand (+2.0%); BKNG's alternative-accommodation premium over its own total went +6pts (3Q24) to −1pt (2Q26), alt-accom +4% vs Airbnb +10.3%. Airbnb is 41.5% of Phocuswright's $219.9bn 2025 global STR pool; the base case needs 51.5% by 2028.
- Supply is endogenous: nights per active listing 62.5-62.7 for four years while listings went 6.6M → 9.0M. Inside Airbnb: same-listing prices fell 1-11% through 2025 in every clean pair (reported ADR growth is mix and FX); churn 20-30% a year, corrected six-city retention 75.5% → 73.4% ex-Austin; 55-81% of listings belong to multi-listing hosts and the share rose in all 13 cities; largest host 908 entire homes in NYC. Common Crawl: survival 85-90% a year, review velocity flat five years, no price in any era.
- Category: EU27 platform nights +11.4% (2025), +9.7% (1Q26); Airbnb EMEA grows with the category once FX is removed (corr 0.81); regulated markets are the slow ones (Spain +6.5%, Portugal +4.9% in 1Q26 vs Italy +14.7%, Germany +14.9%). US real accommodations spend +1.8% with prices +3.4% (Jul 2026): the US category is price, not volume.
- Hotels: the price gap has closed; US hotel ADR $171.74 (+5.7%) in Jul 2026 vs Airbnb ex-FX ADR +4%; luxury RevPAR +17.7% vs economy +3.6%. Hedonics: Superhost premium +1.0% (a myth of the raw data), each bedroom +15.1%, rating ≥4.9 +9.5%.
- Backlog: unearned fees explained next-quarter revenue with R² 0.96 through 2Q25, then RNPL broke it (−0.9% y/y vs revenue +16.5%). Funds held +10.5% at 2Q26 fits revenue +12.0% against a +14.5-16.5% guide; not a miss call, the RNPL confound is the size of the gap.
- Macro: volume is macro-insensitive since 2024; reported growth is FX-sensitive (broad USD vs ADR r −0.99; EMEA revenue ~0.8pts per 1% EUR/USD); rates matter through ~$120M pre-tax per 100bp on the cash pile and the multiple, not demand; rates beta 0.0.

### 5.4 Margins, cash and capital return

- Adj. EBITDA margin −5% (2019) → 35-37% (2022-25); FY26 floor 35.5%. Four things built it: a permanent marketing reset (24% of revenue in 2019 → 12-13%), a fixed-cost reset, variable-cost work, and an ADR windfall. Since Q4 2023 management guides a floor, not a target, and every floor since 2023 has been beaten by 60-180bps.
- FY22 → FY25 bridge: revenue per night +5.1pts (ADR ex-FX +3.7), S&M −4.2, net +0.5. FY25 → FY26: ADR ex-FX +2.29, FX +1.32, brand and performance −1.78; if ADR ex-FX and FX go to zero the base is a 2.5pt decline, not a 1pt gain.
- Cash S&M is 85% of the rise in cost per night since 2Q22 ($2.08 of $2.44); 2025 was field ops +43%, 1H26 is brand and performance +32% (media, reversible). Cash product development flat at 10-11% for four years; the GAAP creep is SBC. Ops & support cash per night $2.48 (2022) → ~$2.05 (1H26), the one working AI lever (+0.39 margin pts a year, not 2). Non-cancelable purchase obligations $719M → $1,749M and the hosting commitment to "at least $1.7bn through 2031" settle the Chesky/Mertz AI-spend dispute in Mertz's favour.
- Path to 40% by FY28: P ≈ 21% (Monte Carlo p10/median/p90 33.3 / 37.6 / 41.3); treat 38% as the realistic ceiling.
- FCF margin 44.2% (3Q23 TTM) → 36.7% (2Q26 TTM), entirely below the EBITDA line: cash taxes converging on the provision, the RNPL-killed float, fading interest income. FCF / adj. EBITDA 117% (FY22) → 105% TTM; model 100-105%.
- vs BKNG: the 12pt GAAP operating-margin gap is SBC (13.0% vs 2.3%); adjusted margins are within 2pts; SBC-adjusted FCF margin 24.6% vs 31.5% flips the ranking. Take rate (14.5% vs 13.4%) is BKNG's one structural edge.
- Capital return: FY25 SBC $1.6B = 13.1% of revenue and 34.7% of FCF; buybacks + withholding $4.35B = 94% of FCF but net return after SBC 59.6% (BKNG 70%, NFLX 93%); $1.4B buys 1% of share count; FCF +35.5% but FCF/share +47.9% 2022-25; diluted count 649M (2Q24) → 597M (2Q26). Heaviest SBC load in the peer set. $3.4bn of authorisation left in Aug 2026.
- FX: 55% of revenue non-USD; 1% weaker dollar = +$67M revenue, +$56M EBITDA, +0.26 margin pts.

### 5.5 Regulatory

- Incremental net revenue loss beyond the 2Q26 run-rate: median 0.45% (end-2027), 0.855% (2028), 1.7% (2030); mean 0.75% / 1.24% / 2.2%; P95 2.7% / 4.0% / 6.7%; P(>1%) 18.9% by 2027, 71.0% by 2030; 93% European. Median EBITDA hit $72M (2027) / $218M (2030) = $2.8 / $8.4 a share at 22x; 2030 P95 $30.04 a share. **Regulation is a 1-2% growth tax on Europe with an 8% tail, not an existential risk.**
- One event carries the tail: the EU Affordable Housing Act (45% in force with enforcement by 2030) is 33% of 2030 variance alone, 78% with its binding-caps tail; remove it and the median falls to 1.2%. Re-run after the 9 Sep 2026 proposal text (repricing rules in the note).
- What the Street prices (NYC-style enforcement spreading, Barcelona 2028) contributes a median 0.3%. NYC is a small upside (20% chance of LL18 loosening by 2027). The Spanish EUR64m fine is one-off cash, not run-rate.
- Measured cohorts: Barcelona 5,146 matched HUTB licences (do not reconcile to the announced 10,101) → $23.9M / 0.20% of FY25 revenue; Maui 3,862 unit ids → $18.0M / 0.15%; NYC guest-nights −56.1% (6.56M → 2.88M), the right benchmark rather than the −83% listing count; Spain INE tourist dwellings −10.7% y/y (Madrid −28.9%, Barcelona −14.1%). No jurisdiction-level revenue loss exists anywhere in filings or transcripts.
- No dated European regulatory event has ever moved the stock outside a 2-sigma band; every quarter since NYC enforcement met or beat its revenue guide (which cannot establish absorption).

### 5.6 Stock behaviour and positioning

- 41 moves of 7%+ since IPO: 20 macro, 11 earnings, 9 company, 1 industry. Six of eleven 7%+ earnings moves were down days on beats. Mean absolute day-1 move 7.07%, median 6.87%; 10 of 23 prints ≥8%, 5 of 23 ≤1.1%.
- Post-print drift: +1..+20 −3.7% (t −2.16, negative 15 of 23); up-prints fade (−7.1% at 20d, −14.8% at 60d), down-prints do not bounce. From 2023 the drift is −2.3% and not significant; the last three up-prints drifted −1.4%, +5.5%, +3.2%.
- Factor decay: beta to QQQ 1.28 (2022) → 0.91 (2026), to hotels 1.24 → 0.45; persistent negative momentum loading (−0.77 in 2026); idiosyncratic share 64%. 2026 YTD +34pts = QQQ +14.2, consumer-orthogonal −12.9, alpha +32.7 (the Q2 print alone +17.4%).
- Seasonality (n 5-6, found among 54 tests): May −14.5% excess (0 of 6), February +7.7% (6 of 6), November −5.1% (0 of 5).
- Analyst actions are a print echo (PT raises +2.94% overall, −0.20% ex-print-week). Short interest 2.17%, a three-year low. Spot $181.94 is above the mean target $178.96; 55% of targets sit below spot; 46% of ratings Hold or worse; 22 raises and 0 cuts since the 2Q26 print. The asymmetry has flipped versus the last two prints.
- Sell side: 21 Buy / 11 Hold / 2 Sell; targets $125 (Morgan Stanley) to $220 (Rosenblatt, DA Davidson). Every Buy is an EBITDA lens that holds or expands; every Sell is a cash-after-SBC lens. The $125-$220 range is a multiple debate on a consensual ~10-12% growth path.
- Pitch scorecard: framings built on nights acceleration won (6 of 7, +25.3pts vs QQQ); all 7 holds scored zero; take-rate-expansion bulls were wrong on the KPI and unpunished.

### 5.7 Management, calls and experts

- 2026 C-suite turnover wave hired from Booking (x2), Viator, Uber and Meta AI; CBO Rijvers 1 Sep 2026, Stephenson leaves end-2026; inaugural IG ratings and a $2.5B bond in Mar 2026 (stock −5%); insider flow one-way (Gebbia ~$71M, Blecharczyk ~$13M+ sold), no open-market buying in 12 months; Chesky founded an outside AI lab (Jun 2026). No management change ever moved the stock 3%.
- Calls: analysts per call 15.0 (2022) → 11.5 (2026), questions 36 → 22, no new house since 2024; prepared remarks doubled from 3Q25. Analysts ask regulation at 4.9x the prepared-remark rate, marketing 2.8x, take rate 2.3x; management leads on margin and capital return. 37 declined quantifications; the four that matter (Experiences economics, hotels economics, AI spend, long-term margin) have never had a number. Management credibility 62% overall (Stephenson 74%, Mertz 63%, Chesky 42%; multi-year claims 26%; pricing/ADR claims 0 of 7). Sell-side tone tracks the second derivative of nights growth, not the level.
- Experts (Third Bridge): supplier power sits with property managers; fee stack on a $100 night is Airbnb ~15%, manager 20-25% plus guest fees, owner keeps ~$60-65; European managers pay 15-17% and see commissions as a plateau; AI-native bookings ~3% in 12-24 months with no EBITDA impact, the exposure being Airbnb's ~90% direct traffic; Booking's Genius members drive high-50s to low-60s % of room nights; US ~2M professionally managed rentals across ~20,000 firms; India ~$1.2B/yr, "a narrative, not a number".
- Theo's IC brief verdict: "Forecast edge remains unproven; trading edge remains untested"; every hypothesis H-001 to H-012 ended weak, ineligible, inconclusive or watch; his `model_results.csv` is empty.

---

## 6. Claims to stop making (from the red team and the audit)

- 18 / 22 / 25.5x exit multiples; use 13.5 / 16.5 / 18.5x and show the old grid as a labelled sensitivity.
- "Zero of 233 alt-data features beat AR(1)"; the file has 598 rows and 52 beat AR(1). Say: nothing beats AR(1) on both windows and every apparent winner is mechanical FX, not knowable before the print, or window-dependent.
- "RNPL added 3 points of nights" (three features together); "a −0.8pt direct-booking hit" (0-15bp); the discount-share series (schema change, not behaviour).
- The seven-city retention fall 75.4% → 71.1% and the Paris 33% / Nashville 44% / Chicago 40% "supply exit" figures (partial-scrape artefacts).
- Any ABNB event-implied move until the 6 Nov weekly lists; the options estimator is currently unidentified.
- "Unearned fees R² 0.96" as a forecast (in-sample; walk-forward 1.85x AR(1)).
- "The only out-of-sample signal in 97 tests" (nine at 20 days, none at day 1); "nights per listing 62.5-62.7 for four years" (say flat within rounding).
- "Mean 20-session excess −4.7% across 22 prints" (−3.6% across 23 with the 2Q26 window complete); ABNB never had a significant rates beta.
- Inside Airbnb `estimated_occupancy_l365d` is estimated nights booked (0-365), not a percentage; `blocked_rate` is not occupancy; XBRL `AdvertisingExpense` ($843M) is not the brand-and-performance line ($1,595M).

Open defects: the pre-7 Sep notes still carry some of the above; `16_web-gap-fill.md` quotes stale EPS rows; permutation p-values in `04_reaction_vs_consensus.py` are order-dependent; four workbook items remain open (memo multiples hard-coded, FY25 interest expense $0, quarterly regulatory drag); the build graph has not been run end to end in a clean checkout.

---

## 7. What to do next

### 7.1 Before anything else (the run's own list)

1. Update `model/assumptions.md` to 13.5 / 16.5 / 18.5x with the old grid as a labelled sensitivity.
2. Refresh `05_fx_schedule.csv` weekly (one FRED pull); add the Airbnb-weighted 22-currency basket. Locks the 4Q26 and 1Q27 revenue-FX numbers.
3. Freeze and publish the 5 Nov prediction card (spec `ABNB-WS20-v1`, do not change `spec_id`), score all items on 6 Nov.
4. Start the monthly Inside Airbnb capture on the fixed 13 cities; the CDN keeps about a year and every month missed cannot be recovered.

### 7.2 Ranked build-forward

Re-run the options ledger in the week of 26-30 Oct once the 6 Nov weekly lists; reconcile the four FY27 revenue estimates into one number; pull the Zacks key-metrics preview 2-3 Nov (nights, ADR, GBV consensus); merge WS04's 23 consensus rows into Theo's `consensus_snapshots.csv` and rebuild the multiples panel on consensus; get Theo's Bloomberg export, review store and municipal registries off his SSD (and the 17 missing v3 artifacts onto the share); price the optionality bucket separately; standardise the nights-acceleration definition; LatAm external benchmarks; log funds-held and unearned-fee balances the day each 10-Q posts; MAR/HLT regional RevPAR; 13F concentration history; weekly Trends capture with the pull date stamped (insurance only).

Explicitly do not build: a broader composite demand index, Trends share-of-search, Eurostat as a nowcast, Inside Airbnb listed prices, Common Crawl as a demand series, more free-source scraping of the kind Theo's runs exhausted.

### 7.3 Housekeeping

- Merge the overnight branch (PR #16), close #5, #8, #11-#15, remove the nine worktrees; do not port fixes into the main tree's stale copies.
- Open the regulatory-db PR (the package is untracked in main); add Theo's five municipal registry sources.
- Purge the five Third Bridge PDFs from git history and link Drive; merge the duplicate `citadel-abnb-files 2/` folder; unpack Jessie's two zips.
- Request NYC pre/post-LL18 dumps from Inside Airbnb; ask Theo to remove `.secrets/env.sh` from the share.
- Fill `research/thesis.md`, `docs/TIMELINE.md` and the top of `model/assumptions.md` (all still templates).

### 7.4 The 5 November prediction card (pre-registered)

Guide: revenue $4,690-4,770M (+15-17%, ~3pp FX after hedging), nights low double digits, GBV mid-teens, margin down slightly from 50.1%, FY26 revenue at least mid teens, margin at least 35.5%. Street: revenue $4,740M, EPS $2.87, Q4 revenue $3,200M.

| Item | Our estimate | Bar |
|---|---|---|
| Nights & seats y/y | +10.2% (147.2M), range 7.9-12.6% | ~144-146M derived |
| ADR y/y | +3.8% ($177.84), of which FX −1.3 to +0.8pp | Zacks ADR consensus 2-3 days before |
| GBV | $26,185M (+14.3%) | "mid teens" |
| Revenue | $4,801M (+17.2%), honest range $4.78-4.82bn | Street $4,740M; frozen surprise +1.37% → $4,805M |
| Adj. EBITDA margin | 49.0% (48.3-50.2%) | 9 of 10 ceilings met |
| Brand & performance marketing y/y | +17-25% (1H26 +32%) | the single most informative line: FY margin 37.0% at +17%, 35.5% at +31% |
| Implied take rate | 17.88% flat; reported ~18.27% | +2.2pp of FX timing between the two |
| 4Q26 revenue guide | midpoint +11-13% (model $3,145M) | Street $3,200M = +15.2%, a live "guide below Street" setup |
| FY26 guide | revenue to high teens; margin "approximately 36%+" | the FY guide has only ever been raised |

Expected reaction: nights ≥+11% with Q4 nights guided at or above the Q3 rate → +5 to +10%; nights +10% with Q4 revenue +11-13% and FX quantified → −2 to +5% (likeliest); the same guide without FX quantified → −5 to −10% (the specific risk of this print); nights guided below Q3 or "moderation" language → −8 to −13%. One turn of EV/NTM EBITDA = $9.11 = 5.0%; a Q4 guide implying >18% growth is worth ~2 turns ≈ $20.

### 7.5 Dated calendar

9 Sep EU Affordable Housing Act text (re-run the regulatory model) · Oct NYC registration renewals · 21 Oct HLT, ~28 Oct BKNG, ~3 Nov MAR print · 26-30 Oct options ledger · 2-3 Nov Zacks preview · **5 Nov Q3 print** · 1 Dec Ireland register · 31 Dec Greek freeze decision · Feb 2027 FY27 margin floor · 31 Mar 2027 EU first readings, Chicago rulings · May 2027 Barcelona election · Nov 2028 Barcelona licence expiry · Jan 2029 / 2031 Maui phases.
