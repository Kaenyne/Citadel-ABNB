# 04 · Data map per work package

Paths from the repo root. "git" = committed; "fetch" = public, download yourself (how-to below); "Theo" = produced on Theo's
machine and pushed as CSV; "licensed" = never in git.

| WP | Reads | In git? | If not, how to get it |
|---|---|---|---|
| A | `data/processed/overnight/02_kpi_panel_quarterly.csv`, `02_guidance_ledger.csv`, `02_guidance_cushion_series.csv`, `16_consensus_at_print_merged.csv`, `data/processed/forecast_methods/L0/L0_vintage_register.csv`, `data/processed/abnb_earnings_reactions.csv`, harness | git | — |
| B | as A + FY consensus vintages in the register (thin pre-2024) | git | better after WP-G1 |
| C1 | Inside Airbnb `calendar.csv.gz` for the same market at consecutive months; 2024–25 vintages: manifest `data/manifests/…F0b_new_vintages_manifest.csv` (34 markets); 2026: `data/manifests/ia_daily_capture_manifest.csv` | manifests in git; files fetch | `https://data.insideairbnb.com/{country}/{region}/{city}/{YYYY-MM-DD}/data/calendar.csv.gz` — dates listed on insideairbnb.com/get-the-data; the CDN keeps ~12 months, older vintages only if someone archived them (ask Theo / Krish) |
| C2 | internet | — | NTTO I-94 (trade.gov/i-94-arrivals-program), Eurostat API (`tour_ce_oam`, `tour_occ_nim`), JNTO statistics, INE Frontur/Egatur API, DATATUR, ISTAT, STR/CoStar weekly press releases, FRED `CUSR0000SEHB` |
| C3 | `analysis/src/overnight/08_altdata_backtests.py`, `data/processed/overnight/08_feature_tests_all.csv`, `data/processed/forecast_methods/kernel_phi_v2/` (residual R), WP-C1 outputs | git (+C1) | — |
| D | `05_backtests/K1_*.md`, `PREREG_ABNB-INT-v1.md` | git | — |
| E1 | NCLH quarterly balance sheet / income statement / KPIs 2015–2Q26; NCLH guidance history | fetch | Alpha Vantage `BALANCE_SHEET`, `INCOME_STATEMENT`, `EARNINGS`, `EARNINGS_ESTIMATES` (free key); SEC EDGAR 10-Q/10-K; NCLH press releases |
| E2 | BKNG / EXPE same | fetch | same |
| F | `02_kpi_panel_quarterly.csv` (unearned fees, funds receivable/payable, GBV, revenue), `data/processed/abnb_backlog_indicators.csv`, `data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv`, `data/processed/nights_baseline_reconciliation.csv`, `analysis/src/rnpl_balance_sheet_bridge.py`, FY2025 10-K and 2Q26 10-Q notes | git (filings fetch) | EDGAR full-text: search "unearned fees" and "funds payable and amounts payable to customers" in the 10-K notes on revenue recognition and foreign currency |
| G1 | LSEG Workspace estimates history export | licensed | UF: businesslibrary.uflib.ufl.edu/refinitivworkspace → workspace.refinitiv.com/web; export to `data/raw/consensus/lseg/` (gitignored); commit the manifest only |
| J | `data/processed/forecast_methods/registry/*.csv`, `harness/score.py` | git | — |
| L | public Airbnb pages (Help Center 1857, 4095; Resource Center 771, 746; Newsroom) | internet | read-only fetch, rate-limited |
| M | Alpha Vantage `EARNINGS_ESTIMATES`, Zacks detailed estimates page, S&P where visible | internet | append to the register with vendor + timestamp |
| N | `data/processed/forecast_methods/fee_panels/sample_ids.csv`, `…/fee_panels/runs/*.csv` (14 / 16 / 18 Sep; 12 / 14 / 16 Oct) | sample in git; runs = Theo | Theo pushes each run's CSV the same day; do not re-scrape |

## Sources you must NOT use

Any airbnb.com endpoint other than public search pages already covered by the running fee-panel capture (a terms-of-service
decision is pending for the fee-inclusive route); anything behind a login except LSEG via your own UF entitlement; Google Trends
(not point-in-time — the team's 432 tests failed); calendar blocked-rate curves as booking-lead-time evidence.

## Big files, by size (so you know what you are downloading)

Inside Airbnb per market per month: listings ~5–50 MB, reviews ~20–300 MB, calendar ~50–300 MB (gz). The 120-market monthly
set is ~10 GB. Query gz files with DuckDB (`read_csv_auto('file.csv.gz')`); never `pandas.read_csv` a calendar whole.
