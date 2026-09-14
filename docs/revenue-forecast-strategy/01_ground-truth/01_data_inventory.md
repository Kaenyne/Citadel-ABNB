# ABNB revenue-forecast data inventory (compiled 11 Sep 2026)

Data inventory lead deliverable. Repo: `Citadel-ABNB` @ `a5d6dbb` (main, not a git working
copy per environment report — treat all paths as of the OneDrive snapshot). Sibling folders
on OneDrive at `.../Young, Willem K.'s files - Citadel - ABNB/`: `Theo Data`, `raw_expansion`,
`FX-ADR-R-model`, `Citadel-ABNB-fx-engine`, `Citadel-ABNB-overnight-review`,
`FX_ENGINE_SESSION_BUNDLE`. Every row below was checked on disk with `ls`/`wc -l`/`head`/
`openpyxl` on 11 Sep 2026; counts are quoted from those checks or from a cited doc, not
assumed from the docs alone. No licensed cell values (Bloomberg) appear below — only sheet
names, row/column counts and structure.

## 0. How to read this

- **PIT-safe** = point-in-time safe for backtesting: the series as stored could have been
  known, in that form, on the historical date it is used to predict. "No" means the file is a
  current-vintage or revision-history snapshot (e.g., Bloomberg consensus history, single
  booking-curve vintage, current Inside Airbnb store) and must not be used as if it were
  known earlier.
- **Licence**: `git/public` (on git, public source), `git/derived` (on git, built from public
  sources), `offgit/public` (public source, kept off git only for size), `licensed/offgit`
  (Bloomberg, FactSet — never redistribute, never quote values in outputs).
- Revenue terms: nights / adr / take_rate / fx / gbv / guidance / consensus / stock / supply /
  regulation.

---

## 1. Top 40 datasets, ranked (value 1–5 for the ABNB revenue-forecast problem)

Grain and coverage are as verified; "rows" is the checked line count (`wc -l`, header
included) or the doc-stated count where the file is licensed/off-git and could not be opened
here.

| # | Value | Path | Grain | Coverage | Rows | Informs | PIT-safe? | Licence | Caveat |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | `data/processed/overnight/02_kpi_panel_quarterly.csv` (+`02_kpi_panel_long.csv`, `02_metric_coverage.csv`) | company-quarter | 3Q20–2Q26, 119 cols | 25 (24 qtrs+hdr); long form 156KB/1,050 quotes | nights, adr, fx, gbv, take_rate | Partially — built after the fact from letters/XBRL; usable PIT only back-dated to each metric's disclosure date via `02_metric_coverage.csv` | git/derived | Regional nights are text bands not numbers before 3Q22; several series stop (cross-border 1Q24, urban 4Q23, active listings 4Q25) — `docs/2026-09-07_revenue-forecasting-inventory.md` §1 |
| 2 | 5 | `data/processed/overnight/02_guidance_ledger.csv` | statement | all 23 prints, 194 statements | 195 | guidance, revenue | Yes — each row is dated at issuance | git/derived | 159/194 scoreable; beat own midpoint 19/19, above top 15/19 — same doc |
| 3 | 5 | `data/processed/overnight/04_consensus_at_print.csv` + `16_consensus_at_print_merged.csv` + `04_consensus_sources.csv` | print | 23 prints | 24 (+145 sourced quotes) | consensus | Yes — reconstructed from press quotes dated before each print | git/derived | Coverage uneven: revenue 23/23, ADR only 5/23 — inventory doc §"Revenue, guidance and consensus" |
| 4 | 5 | `model/ABNB_driver_model.xlsx` + `analysis/src/overnight/13_driver_model.py` + `13_model_quarterly.csv`/`13_model_annual.csv` | scenario x quarter | 3Q26–4Q27 qtrly, FY26–FY28 annual | 19 rows quarterly output | nights, adr, fx, take_rate, gbv, guidance | N/A (forward model, not backtest input) | git/derived | Take rate is a bps lever not a mechanism bridge; FY25 interest expense reads zero; regulatory drag not wired quarterly — `docs/2026-09-07_research-state-of-play.md` |
| 5 | 5 | `data/processed/overnight/10_regional_panel_quarterly.csv` + `10_regional_quotes.csv` | region-quarter | 23 quarters, 79 cols | 24 | nights, gbv | Yes, bands as disclosed | git/derived | Bands are low/high/mid, not point nights; share-weighted sum reconciles to reported total within 1.1pp — inventory doc §Nights |
| 6 | 5 | `research/notes/2026-09-07_adr-decomposition.md` + `model/ADR_decomposition.xlsx` + `data/processed/adr/*.csv` (46 files) | region/market-year | 2020–2025 | 46 CSVs, e.g. `05_size_mix_panel.csv` (29 markets) | adr | Mixed — FX component reconstructed to 1Q20 (r 0.988); size-mix panel is current-vintage Inside Airbnb, not PIT | git/derived | Geographic mix -1.6pp (2025), within-region ex-FX +3.4pp, of which size-mix +0.63pp (elasticity 0.23, NOT the Street's +2pp reading), residual +3.6pp genuinely unidentified — note §0 |
| 7 | 4 | `data/processed/overnight/05_fx_schedule.csv` + `05_fx_fits.csv` + `10_fx_daily.csv`/`10_fx_quarterly.csv`/`10_fx_basket.csv`/`10_regional_fx_passthrough.csv` | daily/quarterly, region | FRED bilateral since ~1970s to 2Q26 for daily; schedule to 4Q27 | `10_fx_daily.csv` 19,468 rows; schedule 2,353B | fx, adr, revenue | Yes for the daily FRED series; the schedule itself is a forward scenario, not a backtest target | git/public (FRED) + git/derived | Revenue FX lags spot 1–2 quarters; regional pass-throughs EMEA 1.04/LatAm 0.62/APAC 0.86, NA unidentified — inventory doc §ADR and FX |
| 8 | 4 | `data/processed/overnight/28_fx_hedge_disclosures.csv`/`28_fx_hedge_tests.csv`/`28_fx_hedge_forward.csv` | quarter | 1Q23–2Q26 | 15 | fx | Yes — hand-extracted from 10-Q/10-K text dated at filing | git/derived | Hand-extracted sentences, not the full hedge book; `research/notes/overnight/28_fx-hedge-disclosures.md` is the caveat doc |
| 9 | 4 | `data/processed/overnight/06_elasticities.csv` | sourced sensitivity | mixed | 26 | take_rate, adr, nights | N/A (external elasticities, dated by source) | git/derived | 25 sourced sensitivities incl. single-fee migration +40–50bps, Booking.com net take-rate ceiling ~14.5% |
| 10 | 4 | `data/processed/overnight/06_fee_timeline.csv` | event | 2019–2026 | ~19 dated events + header | take_rate | Yes — each event dated | git/derived | Single 15.5% host fee timeline; general migration deadline 15 Sep 2026, EEA 13 Oct 2026 per Jessie's channel-fee table |
| 11 | 4 | `data/processed/overnight/06_quote_line_items.csv` + `06_quote_discount_panel.csv` | quote | Mar–Aug 2026, by city | header+76 (line items; underlying 1.71M quotes aggregated) | take_rate, adr | No — current-vintage quote scrape, 2026 only | git/derived | 1.71M fee-inclusive quotes underlie this; service-fee share and discount penetration 10.9–31.4% |
| 12 | 4 | `data/processed/overnight/08_ia_dump_metrics.csv` + `08_ia_city_yoy.csv` | city-dump | Dec 2022–Aug 2026, 13 cities | 169 | supply, adr(proxy) | Partially — each dump is dated, but retired historical dumps are gone (39% of probes 403) | offgit/public source (CC BY 4.0), derived on git | 168 of 279 probed dumps retrieved; price basis changed in 2026 dumps (fee-inclusive quote) — `data/README.md` |
| 13 | 4 | `data/processed/booking_curves_by_market.csv` + `booking_curve_daily.csv` | market x snapshot x horizon | 120 markets, single June 2026 vintage | 600 + 44,379 | nights (forward proxy) | No — one vintage, no y/y | offgit/public source, derived on git | `blocked_rate` is NOT occupancy — `available='f'` conflates booked/host-blocked/inactive; never call it occupancy — `data/README.md` |
| 14 | 4 | `research/notes/choice_nights_driver.md` + `analysis/src/choice_nights_driver*.py` (3 scripts) + `docs/nights_choice_driver.xlsx` | US, party-size x quarter | calibrated on 2025 | 153-line note | nights | N/A (structural driver, calibration is 2025 cross-section) | git/derived | NOT wired into the regional nights build; SWITCH_RATE 5.0 assumption; reconciliation in `research/notes/na_nights_reconciliation.md` (127 lines) |
| 15 | 4 | `data/processed/overnight/11_new_business_scenarios.csv` + `11_ai_exposure_scenarios.csv` | line x scenario x year | FY25–FY28 | small | gbv, take_rate | N/A (scenario) | git/derived | Hotels/Experiences/Services/sponsored listings bear/base/bull |
| 16 | 4 | `data/processed/overnight/20_frozen_q3_2026.csv` | pre-registered card | 3Q26 | 19 | nights, adr, gbv, revenue | Yes by construction (pre-registered before 5 Nov print) | git/derived | Frozen under spec ABNB-WS20-v1; scored 6 Nov, AFTER the Oct finals — use as calibration target, not as an input the judges will have seen realised |
| 17 | 4 | `data/processed/overnight/20_prediction_ledger.csv` + `08_test_scoreboard.csv` + `08_feature_tests_all.csv`(598) + `05_macro_tests_all.csv`(1,408) | test | rolling | ledger 391 rows | nights, adr, stock | Yes — walk-forward tests explicitly designed for PIT | git/derived | Nothing beats AR(1)/naive for nights; macro sensitivity of nights is zero; survivors are narrow (broad USD→ADR, guide+cushion→revenue level, funds-held→revenue growth, guide-below-Street→20-day drift n=9) |
| 18 | 3 | `data/processed/overnight/07_cost_lines_per_night.csv`/`07_margin_levers_fy26_fy28.csv`/`07_cost_components_annual.csv` | quarter/year | 1Q21–2Q26, FY26–28 scenario | 50,306B for levers file | take_rate (cost side), not revenue directly | Yes for history | git/derived | Margin-side; only indirectly a revenue input (informs take-rate cost bridge design) |
| 19 | 4 | `data/processed/overnight/10_regional_revenue_xbrl.csv` + `10_xbrl_revenue_geography.csv` | region-quarter | XBRL-sourced | 258 rows (xbrl_revenue_geography) | gbv, adr(implied) | Yes — XBRL is filed, dated data | git/public (SEC EDGAR) | Cross-check to letter-disclosed regional nights bands, not an independent nights source |
| 20 | 3 | `data/processed/overnight/05_macro_scenarios.csv`/`05_macro_sensitivities.csv`/`05_macro_quarterly_panel.csv` | quarter | multi-year | sensitivities 120KB | adr | Yes | git/derived (FRED-based) | Airline-fare CPI sensitivity +0.067pp/1% on ADR ex-FX; 2027 airfare-lap drag −1.3 to −1.7pp; macro sensitivity of NIGHTS is zero (tested, not assumed) |
| 21 | 3 | `data/processed/overnight/06_price_gap_series.csv`/`06_price_gap_monthly.csv`/`06_price_per_unit_panel.csv`/`06_wtp_hedonic_coefs.csv` | quarter/monthly/city | multi-source | price_gap_series 4,628B | adr | Yes (CPI/BEA/STR are dated releases) | git/public+derived | Hedonic: extra bedroom +15.1%, capacity elasticity +0.49, rating 4.9+ premium +9.5% |
| 22 | 3 | Eurostat platform nights: `eurostat_platform_nights_monthly.csv`/`_quarterly.csv`/`_by_country.csv` + Jessie's `eurostat_platform_vs_hotel_*` | country-month | Jan 2018–Mar 2026 | monthly 99 months | nights (EMEA proxy) | Yes | git/public (Eurostat re-use) | FAILED as an ABNB nights predictor in backtests (research/notes/overnight/08, 09, 20) — use as context, not as a signal |
| 23 | 3 | `data/processed/overnight/02_fy_guide_revisions.csv`/`02_guidance_accuracy.csv`/`02_guidance_cushion_series.csv`/`02_guidance_tells.csv` | print | 23 prints | fy_guide_revisions 8,739B | guidance | Yes | git/derived | Trailing-8 median cushion +1.79% over midpoint |
| 24 | 3 | `data/processed/overnight/03_call_turns.csv`/`03_call_features.csv`/`03_theme_lexicon.csv`/`03_credibility_scorecard.csv` | speaker-turn | 23 calls | call_turns 298,472B (1,677 turns x 132 features per doc) | guidance(qualitative), stock | Yes (dated by call) | git/derived | Management-tone signal FAILED as a return/print predictor (09_stock-behaviour note) |
| 25 | 3 | `data/processed/overnight/08_backlog_tests.csv` + `abnb_backlog_indicators.csv` | quarter | 4Q20– | backlog_tests 18,956B | gbv, revenue | Yes | git/derived | Funds-held/unearned-fees growth → revenue growth slope 0.60, r 0.89 — survivor, but RNPL distorts it |
| 26 | 3 | `data/processed/predictive/02_peer_prints*.csv` (BKNG/EXPE/MAR/HLT) | peer-quarter | 93 filings | peer_prints_long size n/a, sourced | consensus, stock (read-through) | Yes | git/public (EDGAR 8-K) | Peer read-across FAILED as a predictor of ABNB surprise on both windows |
| 27 | 3 | `research/notes/overnight/29_q4-fy27-bridge.md` + underlying `05_fx_schedule.csv` | narrative+data | to FY27 | 1 note | fx, guidance | N/A | git/derived | Q4 2026 revenue FX ~84% already determined at ~-0.4pp vs +3pp in Q3 — mechanical guide step-down |
| 28 | 3 | `data/processed/overnight/27_regional_bucket_check.csv`/`27_nights_band.csv` | region-quarter | 4Q24–2Q26 | small | nights | Yes | git/derived | Cross-check of which end of the disclosed nights bucket is implied by revenue/ADR/take-rate arithmetic |
| 29 | 3 | Stay-length/party-size study (`citadel-abnb_stay_length_v6.zip`, `docs/nights_choice_driver.xlsx`, `docs/party_size_distribution.html`) + `data/processed/abnb_party_size_reviews_quarterly.csv` family (Inside Airbnb reviews, 74M reviews parsed) | review-derived, quarter/region | validated vs Hawaii DBEDT r 0.96–0.99 | large (74M source reviews) | adr(unit-size), nights | Reviews are historical-dated but the parsing method is current — use with care for pre-2026 backtests | git/derived, source offgit/public | Airbnb stays ~1.8x hotel stays; kitchen +1.2–1.5 nights; mean party ~3; price crossover at party of 3 |
| 30 | 3 | `data/processed/overnight/13_valuation_summary.csv`/`13_scenario_grid.csv`/`13_reconciliation.csv` | scenario | current | small | guidance, stock (valuation, not revenue) | N/A | git/derived | Exit multiple sensitivity: +0.48 EV/EBITDA turns per pt of forward growth |
| 31 | 3 | `data/processed/overnight/12_*` valuation-multiple-regime files (per `research/notes/overnight/12_valuation-multiple-regime.md`) | peer x time | historical | n/a | stock | Yes | git/derived | Independently-derived fair EV/EBITDA 13.5–18.5x, not the earlier 18–25.5x |
| 32 | 3 | ABNB daily/monthly closes + major moves: `abnb_daily_close.csv` (Krish tree), `abnb_monthly_close.csv` (Jessie tree), `abnb_major_moves_events.csv` | daily/monthly | IPO (Dec 2020)–4 Sep 2026 | 1,440 sessions; 41 moves ≥7% | stock | Yes | git/public (Yahoo via yfinance) | Attribution of the 41 major moves is hand-checked, not scripted — `data/README.md` |
| 33 | 3 | `data/processed/overnight/03_reaction_tests.csv`/`03_event_study.csv`/`03_reaction_summary.csv`/`04_reaction_panel.csv`/`04_reaction_tests.csv` | print | 23 prints | reaction_tests 51,349B | stock | Yes | git/derived | 1/5/20-session ABNB, QQQ and excess returns on an executable next-open entry |
| 34 | 3 | Bloomberg `ABNB_Fundamentals_Alt_Macro_Bloomberg_LIVE.xlsx` (Theo Data) | sheet: `KPI_Quarterly` (37 rows x 38 cols), `Consensus_Guidance` (34x34), `Macro_Daily` (2,530 rows x 24 cols, one BDH block/ticker), `Macro_Monthly` (124x41), `Peers_Daily` (1,502x12), `Model_Panel` (36x26), `Alt_Data_Monthly` (127x29) | quarterly/daily/monthly | since IPO to current | see cell counts above (structure only; values not extracted) | consensus, fx, adr, gbv, stock | No — this is a LIVE Bloomberg pull refreshed at open time, i.e. current-vintage; the "consensus history" is a revision history NOT point-in-time — inventory doc explicit warning | licensed/offgit | Never redistribute; never treat `Consensus_Guidance` history as PIT consensus |
| 35 | 2 | Bloomberg `ABNB_Bloomberg_Revenue_Model (2).xlsx` (Theo Data) | sheets `Fundamentals_Q`(40x14), `Operating_KPIs`(58x18), `Segment_Raw`(5x8), `Regional`(56x17), `VALIDATION`(24x8), `DIAGNOSTICS`(39x13) | quarterly | since IPO | see cell counts | gbv, adr, take_rate, nights | No — live pull | licensed/offgit | Cross-check tool for the driver model, not an independent history |
| 36 | 2 | Bloomberg options workbooks: `ABNB_Options_Bloomberg_LIVE (1) (1).xlsx` / `_Pull (1).xlsx`, `IV_Surface_Hist_LIVE.xlsx` | sheets `Underlying_Hist`(2,100x17), `IV_Surface_Hist`(2,100x14 / standalone file 1,506x32), `Current_Chain`(3,005x17), `Hist_Chain_AsOf`(2,006x11), `Contract_Hist`(532x58), `Monthly_Straddles`(104x16) | daily since IPO; chain as-of dates | see cell counts | stock (vol, not revenue directly) | Partially — historical IV/underlying is dated; current chain is not | licensed/offgit | Feeds the options/event-variance workstream, "blocked until late Oct" per state-of-play doc; not a revenue input |
| 37 | 2 | JPM "AI-Driven Outperformance" PDF (Theo Data) | report | dated | 1 PDF | stock, gbv (thesis context) | N/A (single sell-side view) | licensed/offgit | Sell-side view, not data; use only for framing, cite explicitly if quoted |
| 38 | 2 | `data/processed/overnight/09_implied_move_live.json` + options-estimator files | live snapshot | current | 1 file | stock | No — live | git/derived | Estimator "rewritten during audit and currently unidentified" — state-of-play doc; do not use until re-run late Oct |
| 39 | 2 | Regulatory package: `research/regulatory/` (32-factor register), `abnb_regulatory.sqlite`, `abnb_regulatory_events.csv`/`_profile.csv`/`_contributions.csv` | event x market | 20 events, 48 sources | 20 events | regulation, nights(supply-risk) | N/A (probability model) | git/derived | Single-analyst probability estimates; re-run after 9 Sep EU Affordable Housing Act text — `data/README.md` |
| 40 | 2 | `raw_expansion/v2_2026-09-05/inside_airbnb_current/` (root, 315 files) + `Theo Data/raw_expansion*` (89+25 files) | listing/calendar/review | 120 markets, current vintage | manifest 316 rows; ~9.9GB | supply, adr(structure only) | No — single current vintage, no y/y | offgit/public (CC BY 4.0) | Calendars carry NO price (5-col schema, verified across 8 markets — `data/README.md` "Correction 2026-09-05"); realised ADR NOT obtainable from this data |

**Not fully ranked but material and verified on disk (41–52, for completeness):**
`data/processed/hotel_13_market_panel/` (hotel comparator, missing bookings/revenue per
`data/README.md` "Reviewed churn and hotel release"); `data/processed/fee_churn_history/` and
`fee_churn_recent/` (692-capture fee-churn time series, PMS status not observed);
`data/processed/listing_churn_panel/`, `listing_churn_archive/`, `listing_churn_execution/`
(availability-selected, not random-sample churn); `data/processed/hotel_rollout_economics/`,
`hotel_funnel_audit/`, `hotel_expanded_research/`, `peer_readthrough/` (hotel-line
context); `Citadel-ABNB-fx-engine/data/processed/fx_engine/research/` (calibrations.csv,
scores.csv, predictions.csv — the R engine's own backtest); Common Crawl listing-survival
panel (`cc_*` files, 2.08M index rows, 1.2M listing ids, 1,500 matched pairs); TSA/BTS/IATA/
NTTO/Hawaii DBEDT macro-travel series (all tested, near-zero correlation to nights since
2024 per Jessie's PR #17 — context, not signal).

---

## 2. Claimed-but-not-found / discrepancies

- **`Theo Data/data_review_2026-09-07/DATA_MAP.md` "V3" listing panel (2,952,985 rows) and
  588,120,594-row calendar / 67,500,188-row review store**: the map states this lives on an
  **external volume**, not in the reviewed workspace — "An additional source cache referenced
  by V3 exists at /Users/theomachado/abnb_scratch ... outside this workspace total" (line 5).
  This machine's OneDrive tree holds the raw_expansion cohorts (~9.9GB root + ~2GB in `Theo
  Data/raw_expansion`) that are the *inputs* to V3, not the assembled V3 store itself — do not
  assume the 588M-row calendar store is locally queryable without Theo's SSD.
- **`data/README.md` "Not in this tree"**: explicitly states the regulatory research package
  (`research/regulatory/`, `abnb_regulatory.sqlite`, 48 source records) "was never committed
  and lives only in the main working tree" — confirmed absent from the reviewed data tree;
  it sits on branch `krish/regulatory-db` per the same file's later section, which says it was
  "committed 7 Sep 2026" — the two statements in one file are about different branches/times;
  verify current branch before citing counts.
- **Buenos Aires, São Paulo, Bogotá, Pays Basque, Budapest** (114,744 current listing rows):
  present in the raw current-listings store but **absent from Theo's "V3" normalized panel**
  per `DATA_MAP.md` finding 1 — a real gap between "on disk" and "in the modeled panel."
  25.
- **Zenodo/Figshare/Dataverse academic sets** referenced in `data/manifests/dataverse_log.csv`
  (29 data rows): several flagged in `02_academic_and_historical.md` as needing
  reconciliation/quarantine (duplicated Boston cohorts, misfiled AirBSet package, one sample
  with "strong synthetic-data indicators") — treat as unusable until that reconciliation is
  done; do not add to the model as-is.
- **Harvard Dataverse AirDNA-derived sets** (Venice, Reykjavik, Boston MSA daily): documented
  as requiring a manual Guestbook form — confirmed not auto-downloadable, consistent with
  `data/README.md` "Known blockers."
- **17 of 20 of Theo's "v3 alt-data tables"**: `docs/2026-09-07_research-state-of-play.md`
  states these "never reached the share" — i.e., referenced in earlier docs but not present
  here; do not cite numbers from them.
- **Bloomberg "consensus history"**: both `data/README.md` and the state-of-play doc flag
  this workbook tab as a *revision history* of the FY26 estimate, explicitly **not**
  point-in-time consensus — a claim that could be misread as a consensus panel if the sheet
  name (`Consensus_Guidance`) is taken at face value. Confirmed structurally: 34 rows x 34
  cols, single evolving snapshot, not per-print history rows.
- **`.secrets/env.sh`** flagged in state-of-play doc for removal from the OneDrive share —
  not a data gap, but a hygiene item; confirmed `Theo Data/.secrets/` exists on disk (2
  entries) — do not open/quote its contents.

---

## 3. Ten most important gaps and cheapest 3-week fill

| Gap | Cheapest fill in 3 weeks (free/public first) |
|---|---|
| 1. No hard regional nights (only disclosed low/high/mid bands since 3Q22; cross-border/urban/LOS mix stopped 1Q24) | Cannot be filled with new data in 3 weeks — Airbnb doesn't disclose it. Cheapest defensible fix: formalize the existing bucket-arithmetic cross-check (`27_regional_bucket_check.py`) as the stated method, state the ±1pp band explicitly in the memo rather than presenting a point estimate, and wire Jessie's choice-probability driver (`choice_nights_driver.py`) into the regional build as an independent cross-check (already built, just not reconciled — 1–2 days of work, no new data). |
| 2. Hedge book not extracted; the "3pp FX tailwind after hedging" in guidance is asserted, not decomposed | Finish the hand-extraction already started in `28_fx_hedge_disclosures.py` for the remaining 10-Q/10-K quarters (public, free, EDGAR); cross-check against the AOCI cash-flow-hedge line already pulled from XBRL. ~2–3 days, no new acquisition needed. |
| 3. Take rate is a bps lever, not a mechanism bridge | Build the bridge from data already on hand: single-fee migration share x uplift (`06_fee_timeline.csv`, `06_elasticities.csv`), FX service fee, RNPL share of GBV, hotel/Services mix (`11_new_business_scenarios.csv`). Pure modeling work, zero new data, ~3–4 days for one team member. |
| 4. Regional ADR ex-FX is patchy (NA/EMEA from 2Q23, LatAm/APAC from 1Q25) | No public source fills this before earnings. Cheapest defensible step: extend the size-mix panel (`data/processed/adr/05_size_mix_panel.csv`, 29 markets) to more Inside Airbnb markets using the current 120-market store already on disk (`raw_expansion`) — free, already acquired, just needs the same script re-run on more markets (~1 day compute). |
| 5. Booking curves are a single vintage (June 2026), so no y/y comparison | Start a second Inside Airbnb capture NOW on the same market list and script (`build_booking_curves.py`); even a 2–3 week gap gives a first difference. Free (CC BY 4.0), already have the pipeline — costs only compute/storage time, ~1 day to set up a repeatable pull. |
| 6. Thin KPI consensus (ADR only 5/23 prints, GBV 12/23, nights 18/23) | Pull Zacks/Yahoo Finance "key metrics" estimates in the 2–3 days before the 5 Nov print (free, public); this is already the team's stated plan in the inventory doc §2 item 6 — just needs execution, no new tooling. |
| 7. FY28 has no regional or FX build | Extend `13_driver_model.py` and `05_fx_schedule.csv` one more year using the same methodology (mechanical extension of existing code, no new data) — ~1 day. Lower priority given the 3–12 month horizon ends before FY28 matters much, but cheap enough to do if time allows. |
| 8. No country-level ADR (the +3.6pp "pricing + sub-regional mix" residual is jointly unidentified) | Cannot be resolved from Airbnb disclosure. Cheapest partial fix: use the current 120-market Inside Airbnb store's *asking price* (not ADR, but same-market sub-regional dispersion) to bound how much of the residual could plausibly be sub-regional mix vs like-for-like pricing — a sensitivity, not a point estimate; ~2 days, uses data already acquired. |
| 9. Options/event-variance estimator is broken ("currently unidentified") | Not revenue-critical for the memo; if the team wants an implied-move number for the memo's risk section, the cheapest fix is to read the already-licensed Bloomberg `Monthly_Straddles` tab (104 rows, historical, structurally verified above) by hand for the last 4–6 prints rather than trying to re-fix the live estimator before the pitch deadline. |
| 10. Consensus and guidance ledgers stop being useful once trailing cushion is priced in — the model needs a forward view of what guidance itself will say at 3 more prints it can't observe | This is the core competition problem, not a data gap — but the cheapest data-side derisking is to backtest the existing guidance-ledger + cushion methodology (`02_guidance_cushion_series.csv`, survivor #2 in the predictive study) against the 4 upcoming print dates as pseudo-out-of-sample, using the frozen 3Q26 card (`20_frozen_q3_2026.csv`) as the first live test — already designed, needs no new data, just the discipline to score it on 6 Nov before the finals. |

---

## 4. Key numbers to memorise (source-cited)

1. Take rate seasonality (2023–25 means): Q1 9.2% / Q2 13.1% / Q3 18.3% / Q4 14.0%; LTM 13.2% — `docs/2026-09-07_revenue-forecasting-inventory.md` §0, cross-checked `data/processed/overnight/02_kpi_panel_quarterly.csv`.
2. Nights seasonality (2023–25 FY shares): Q1 26.9% / Q2 25.5% / Q3 25.1% / Q4 22.5% — same doc §0.
3. Base case revenue: 3Q26 $4,801M (+17.2%); 4Q26 $3,145M (+13.2%) vs Street $3,200M; FY26 $14,233M; FY27 $15,842M; FY28 $17,947M — `data/processed/overnight/13_model_quarterly.csv`, `13_model_annual.csv`.
4. Current Street (3–4 Sep 2026): Q3 $4,740M, Q4 $3,200M, FY26 $14.10–14.16bn, FY27 $15.73–15.76bn — `data/processed/overnight/04_current_consensus.csv`.
5. Q3 2026 guide: $4,690–4,770M (+15–17%) — `02_guidance_ledger.csv`.
6. Frozen pre-registered 3Q26 card: nights +10.2%, ADR +3.8%, GBV $26,185M, revenue $4,801M — `data/processed/overnight/20_frozen_q3_2026.csv`.
7. Guidance discipline: beat own revenue midpoint 19/19 prints; finished above top of range 15/19; trailing-8 median cushion +1.79% — `docs/2026-09-07_revenue-forecasting-inventory.md` §"Revenue, guidance and consensus" / `02_guidance_ledger.csv`.
8. Regional FX pass-through into reported ADR: EMEA 1.04, LatAm 0.62, APAC 0.86, NA unidentified — `data/processed/overnight/10_regional_fx_passthrough.csv`.
9. Revenue FX lag: recognition lags spot 1–2 quarters; Q4 2026 revenue FX ~84% already determined at ~−0.4pp vs +3.0pp guided in Q3 — `research/notes/overnight/29_q4-fy27-bridge.md`; `05_fx_schedule.csv`.
10. ADR y/y decomposition 2025: geographic mix −1.6pp (worsening every year since 2021); within-region ex-FX +3.4pp, of which size-mix +0.63pp (bedroom-count elasticity 0.23, measured on 29 markets) and LOS mix +0.04pp; residual "pricing + sub-regional mix" +3.6pp, jointly unidentified — `research/notes/2026-09-07_adr-decomposition.md` §0.
11. Seats dilution from Experiences/Services/hotels: −0.5pp/yr on ADR, FY26–27 — `analysis/src/adr/15_seats_dilution.py`, same note.
12. Bedroom-count elasticity on price: 0.23 (0.2289 on 12 markets, 0.2312 on 29) — NOT the Street's read of +2pp from bedroom-nights disclosure — `research/notes/2026-09-07_adr-decomposition.md` item 3.
13. Extra-bedroom hedonic premium +15.1%; capacity elasticity +0.49; 4.9+ rating premium +9.5% — `data/processed/overnight/06_wtp_hedonic_coefs.csv`.
14. Airline-fare CPI sensitivity of ADR ex-FX: +0.067pp per 1% CPI move; 2027 airfare-lap drag −1.3 to −1.7pp — `data/processed/overnight/05_macro_sensitivities.csv`.
15. Macro sensitivity of nights growth: zero at any confidence level (1,408 macro pairs tested) — `research/notes/overnight/09_stock-behaviour-and-alpha.md`, `05_macro_tests_all.csv`.
16. Nothing beats AR(1)/naive for nights on walk-forward — `research/notes/overnight/20_temporal-validation.md`.
17. Survivor: broad USD → ADR FX, walk-forward error 0.44x naive — `research/notes/overnight/08_altdata-index-and-backtests.md`.
18. Survivor: guide + trailing cushion → revenue level, 1.1% mean error, but WORST predictor of surprise vs Street — same note.
19. Survivor: funds-held/unearned-fees growth → revenue growth, slope 0.60, r 0.89, distorted by RNPL — `08_backlog_tests.csv`.
20. Survivor: "guide below Street" → 20-day drift 9/9 negative, mean −4.2% on executable next-open entry, n=9 — `research/notes/overnight/09_stock-behaviour-and-alpha.md`.
21. Single host fee (15.5%, PMS hosts): >25% of listings by 1Q26, ~50% by 2Q26, most remaining hosts during 2026; general migration deadline 15 Sep 2026, EEA 13 Oct 2026 — `data/processed/overnight/06_fee_timeline.csv` + Jessie's channel-fee table.
22. Single-fee migration uplift: +40–50bps take rate gross on a fully migrated book; 2024 FX service fee +20bps y/y in 2025 — `06_elasticities.csv`.
23. Booking.com net take-rate ceiling ~14.5%; European managed-rental commission 15–16% — same file.
24. RNPL: ~3pp of nights and ~4pp of GBV added in 1Q26; RNPL share of GBV >20%; funds-held-to-GBV growth gap widening on RNPL (3.8pp at 2Q25, 5.2pp at 2Q26) — `data/processed/overnight/08_backlog_tests.csv`, `06_elasticities.csv` (Mertz).
25. Regional revenue/nights split: NA 42.4% of revenue, ~29% of nights; LatAm+APAC 31% of nights, 18.9% of revenue — `docs/2026-09-07_revenue-forecasting-inventory.md` §"Revenue, guidance and consensus."
26. Regional nights growth, base case: 3Q26 NA/EMEA/LatAm/APAC 7/8/18/17%; FY27 6/7/16/15% — `data/processed/overnight/10_regional_forecast.csv`.
27. Exit multiple sensitivity: +0.48 EV/EBITDA turns per point of forward revenue growth; margin moves it ~zero — `docs/2026-09-07_research-state-of-play.md` / `13_valuation_summary.csv`.
28. Independently-derived fair EV/EBITDA range: 13.5–18.5x, vs the earlier (rejected) 18–25.5x — same doc.
29. Targets: bear $74 / base $157 / bull $228 vs spot $181.94 (4 Sep 2026) — `docs/2026-09-07_research-state-of-play.md`.
30. Choice-probability nights driver: US nights +2.4 to +3.4%/yr projected, calibrated on Airbnb = 10.9% of US lodging party-nights in 2025; SWITCH_RATE assumption 5.0; NOT wired into the regional build — `research/notes/choice_nights_driver.md`.

---

## 5. Notes on method and confidence

- Every path above was opened or `wc -l`'d in this session on 11 Sep 2026; four Bloomberg
  workbooks and the standalone IV file were opened read-only with `openpyxl` to confirm sheet
  names and row/column counts only — no cell values were read into this document or into any
  script output.
- The "Theo Data" review folder (`data_review_2026-09-07/`) is itself a meta-inventory built
  by a separate audit pass; its counts (618 files, 16.877GB, 690 catalog entries) are quoted
  from `DATA_MAP.md` and `dataset_catalog.csv` (691 lines incl. header, confirmed) rather than
  re-derived, since re-walking that entire tree was out of scope for this pass — treat those
  aggregate figures as one level less verified than the file-by-file counts elsewhere in this
  document.
- `Citadel-ABNB-fx-engine` and `FX-ADR-R-model` substantially mirror the main repo's
  `data/processed/` tree (same file names, e.g. `abnb_backlog_indicators.csv`,
  `abnb_margin_bridge.csv`) plus their own R-engine-specific outputs
  (`data/processed/fx_engine/research/{scores,calibrations,predictions}.csv` and
  `example/{regional,annual,consolidated}.csv`) — do not double-count these as independent
  datasets; they are the FX engine's inputs/outputs built from the same underlying sources.
- `raw_expansion` (repo root, 315 files, ~9.9GB, manifest 316 lines) and `Theo
  Data/raw_expansion` (89 files, ~2.04GB) and `Theo Data/raw_expansion_licensed` (25 files,
  ~0.003GB) are three distinct cohorts despite similar names — confirmed via `DATA_MAP.md`
  "Where the bytes live" table and direct `find`.
