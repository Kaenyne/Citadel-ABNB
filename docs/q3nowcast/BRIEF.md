# Q3 2026 nowcast run, 11 Sep 2026: shared brief

Branch `krish/q3-nowcast`, worktree `C:\Users\krish\citadel-abnb-q3nowcast`. Owner Krishang Surapaneni (ksurapaneni@ufl.edu), compiled with Claude Code.

## The question
Airbnb's fiscal year is the calendar year. 3Q26 runs 1 Jul to 30 Sep 2026; today is 11 Sep, day 73 of 92. The print is 5 Nov. Can the data the team holds give a good number for 3Q26 Nights and Seats Booked and ADR, by reconstructing past quarters from the same data and checking against what Airbnb disclosed, then applying the identical procedure to the quarter in progress? If the held data is insufficient, what other source can give a better read now?

## What is already known (do not redo, do build on)
- Team nights baseline: 3Q26 +9.9% (146.8mm, band 8.5-10.3), 4Q26 +8.9% (band 8.1-9.9; overnight-2 WS-D argues 8.0-8.2). `research/notes/2026-09-10_nights-baseline-reconciliation.md`. Guide: "low double digits" nights growth, revenue $4.69-4.77bn incl ~3 pp FX tailwind after hedge.
- Main tree `C:\Users\krish\citadel-abnb` (read-only, raw data gitignored there): `docs/2026-09-06_research-inventory.md` is the whole-project inventory, read section 2 first. `research/notes/overnight/08_altdata-index-and-backtests.md`: every composite alt-data index lost to naive; Google Trends 0 of 162; Eurostat lags 5 months; the 13-city Inside Airbnb panel had n = 0 usable year-ago quarters because of composition. `research/notes/predictive/03_macro-altdata-nowcast.md`: level correlations post-2022 are the 2023 normalisation. Survivors: USD y/y to ADR FX (r -0.95), revenue FX lagged 1-2 quarters, hotel RevPAR tracks nights (r 0.88) but does not beat naive, BKNG room-night acceleration coincident (r 0.91, n 7).
- Overnight-2 (12 Sep, PR #40) synthesis copied to `docs/q3nowcast/overnight2_synthesis_copy.md`: 4Q26 ADR FX -0.7 to +1.0 depending on estimator; 3Q26 revenue FX +2.0 after hedge; calendar reopening shows no RNPL signature.
- Inside Airbnb regimes (memory): price basis changed Mar 2026 (fee-inclusive quote per night, 24-29% higher), Dec 2025-Feb 2026 dumps have no price, Dec 2025-May 2026 monthly dumps are partial scope; old dumps stay on the CDN about 12 months. `analysis/src/inside_airbnb_supply_panel.py` has discover/download code. Quote indices do not track disclosed regional ADR (`research/notes/` quote index test, 8 Sep).
- Common Crawl: index API blocks after ~40 queries; use `cdx_via_cluster()` in `analysis/src/cc_listing_panel.py`. 3,000 WARC renders carry no price.

## Data on disk (main tree)
- `data/raw/inside_airbnb_reviews/`: 123 markets, one `<country>_<region>_<market>_<date>_reviews.csv.gz` each (dump dates 107 in Jun 2026, 15 in Jul, 1 in Aug), 8.9 GB. Review dates go back years; reviews belong to listings live at dump time (survivorship).
- `data/raw/inside_airbnb_calendar/`: 34 markets x 5 vintages Sep 2025 to Aug 2026 (164 files). Manifest `data/processed/adr/14c_calendar_manifest.csv`.
- `data/raw/inside_airbnb/`: 13 cities, 168 listings dumps Dec 2022 to Aug 2026 (parquet alongside).
- `data/processed/booking_curve_daily.csv`, `booking_curves_by_market.csv` (Theo, 120 markets, blocked-night rate by market x snapshot x horizon, one Jun 2026 vintage), `market_summary_2026.csv`.
- `data/raw/theo_onedrive/AIRBNB DATA/`: Theo's share. `processed/airbnb_quant_panel_v1` and `_v3`, `raw/mongodb`, `raw_expansion/v2_2026-09-05`, handoff docs `CODEX_HANDOFF_V3.md`, `docs/V3_DELIVERABLES.md`. Inspect before assuming what it holds. `.secrets` and `raw_expansion_licensed` are off limits.
- `data/raw/commoncrawl/` (index, records, matched_pairs.json), `data/processed/abnb_regulatory.sqlite`, `data/processed/abnb_driver_history_quarterly.csv` (disclosed KPIs by quarter), `data/processed/predictive/03_quarterly_panel.csv` (ADR ex-FX, FX effect by quarter), `data/processed/overnight/05_fred_cache/`.
- Other branches: `origin/jessie/backlog-conversion`, `origin/jessie/nights-driver-v7`, `origin/krish/nights-quarterly` (PR #32), `origin/krish/margin-model` (PR #35). Use `git show origin/<branch>:<path>` from the main tree.

## Rules
- Backtest protocol from note 08: quarterly y/y target from `abnb_driver_history_quarterly.csv`; expanding-window walk-forward from 2024Q1 (or the earliest the data allow); report RMSE ratio vs naive last-quarter, prior-year and AR(1); permutation p; say whether each feature is knowable before the print. A feature that does not beat naive is reported as such; do not tune until it does.
- Forecast the quarter independently. The team baseline and the guide are comparison columns, not inputs. No valuation, no target price, no long/short call.
- Label every number sourced / descriptive / assumed / causal. Survivorship, composition and basis breaks must be stated where they bite.
- Write only inside this worktree: scripts `analysis/src/q3nowcast/<WS>_*.py`, outputs `data/processed/q3nowcast/<WS>/`, note `research/notes/q3nowcast/<WS>_<slug>.md`. Do not touch other workstreams' paths. Never modify the main tree. Do not commit raw dumps; commit processed CSVs and manifests with URLs and sizes.
- New raw downloads go to the MAIN tree raw directories (`C:\Users\krish\citadel-abnb\data\raw\inside_airbnb_reviews` etc., gitignored) so the team keeps one store; record every file you add in a manifest under your output path.
- Python: `py -3.13` (pandas 2.3.3, numpy, pyarrow, statsmodels, openpyxl, matplotlib). Bash calls time out at 10 minutes; checkpoint per market, run long jobs in the background with a log, poll.
- Note format: date 2026-09-11, author line "Krishang Surapaneni (compiled with Claude Code)", sections Bottom line, Tables, Method, What this can and cannot identify, Next evidence, Files. Plain prose, no em-dashes.
- At the end commit ONLY your own files (`git add <your paths>`; on `index.lock` wait 30 s and retry up to five times). Never push.
