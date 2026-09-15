# NCLH transferability v1

**Implementation complete; preregistered transferability FAIL; no ABNB adoption.** The current-liability advance-ticket-sales (ATS) stock cannot be treated as a portable measured booking-to-revenue flow kernel under this specification. Main PIT windows: 2023Q1–2026Q2, n=14; 2024Q1–2026Q2, n=10.

Run from repository root with the project interpreter (on this host `C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe`). Dependencies: Python, numpy, pandas, matplotlib, requests, beautifulsoup4.

```powershell
python -m unittest discover -s analysis/src/forecast_methods/nclh_transfer_v1 -p test_nclh.py -v
python analysis/src/forecast_methods/nclh_transfer_v1/run.py --out data/processed/forecast_methods/nclh_transfer_v1/rebuild_NEW
```

Each nonempty output directory is immutable and rejected on rerun. Choose a new directory. Offline reproduction reads `inputs_v3/observations.csv`, source manifests and the existing ABNB lambda table; no network, secrets or proprietary files are required. Canonical outputs after independent review are `results_v4/`; L4 consumes its `l4_evidence.csv`. USD-level forecast errors are in **USD million**. Lambda levels are percent, seasonal ranges percentage points. Ratio denominator is the same-fold seasonal-naive USD-level RMSE. L4 bounds are empty because no uncertainty interval is estimated; descriptive lambda minimum/maximum levels remain in the stability table. All L4 rows are evidence-only and prescribe no ABNB adjustment.

Optional refresh (public network access; use a NEW input directory):

```powershell
python analysis/src/forecast_methods/nclh_transfer_v1/fetch.py --out data/processed/forecast_methods/nclh_transfer_v1/inputs_REFRESH_NEW
python analysis/src/forecast_methods/nclh_transfer_v1/run.py --input data/processed/forecast_methods/nclh_transfer_v1/inputs_REFRESH_NEW --out data/processed/forecast_methods/nclh_transfer_v1/results_REFRESH_NEW
```

The fetcher discovers NCLH IR's quarter-specific earnings releases from the [financial results index](https://www.nclhltd.com/investors/financial-information/financial-results). `FY YYYY` index headings provide the corresponding release's **Q4** income-statement columns. It extracts the first current-quarter financial value, preserving release URLs, publication clocks/timezones, retrieval clocks, SHA256 and table rows. It does not reconstruct historical series from current comparative columns. Raw HTML is cached only in the system temporary directory `citadel_nclh_transfer_v1_public_cache`; do not stage that cache. Refresh reuses cached original responses; change the cache directory deliberately if collecting a genuinely new retrieval vintage.

Inputs are 46 original-quarter issuer releases, 2015Q1–2026Q2, 184 core financial observations plus 109 KPI observations. The ATS input is the **current** balance-sheet line, excluding non-current deposits in other long-term liabilities. This is explicit throughout, not a complete total-deposit curve. Current-quarter zero/blank KPI cells during the suspended-sailing 2020–2021 years are not filled from prior-period comparative cells. Those KPI years remain unavailable; excluded COVID financial facts remain visible. Net yield is an issuer non-GAAP comparator, not GAAP passenger revenue. The guidance inventory is an availability gate, not a scored net-yield guide dataset: no metric-matched GAAP revenue guide/consensus dataset is assembled. Guide comparisons have n=0 and remain UNSCORED; this does not assert that every historical public quotation was exhaustively searched.

Procedure: each forecast vintage is the previous quarter's release timestamp; lagged ATS q−1/q−2/q−3 and every training target must already be public. Fit a fixed 66-point simplex grid with four seasonal means on expanding eligible data, six free coefficients. Exclude 2020–2021 target years and any target with COVID-era ATS lags; flag/include 2022Q4, with a separate exclusion sensitivity. The stability diagnostic freezes weights on data published before 2023-01-01 and evaluates three realized observations per season in 2023–2025. No in-sample seasonal range is called predictive accuracy.

Saved snapshots `inputs/` (missed FY-labelled Q4), `inputs_v2/` (identified KPI parsing hazards), `results_v1/` (same numerical result before expanded L4 rows), `results_v2/` (ambiguous L4 bounds and an empty exclusions CSV repaired in v3), and `results_v3/` (before independent validator repairs) are development history, **not canonical evidence**. None was used silently. `inputs_v3/` repaired the source parser before the first research run. The results and audit-repair notes document the corrections. Canonical `results_v4/` has 18 passing tests and a byte-identical rebuild `results_verify_v2/`, recorded by `reproduction_receipt_v2.json`.

See `docs/revenue-forecast-strategy/05_backtests/L3_NCLH_PREREG_v1.md`, `L3_NCLH_RESULTS_v1.md`, and `L3_NCLH_AUDIT_REPAIRS_v1.md` (supersedes its earlier canonical-version and test-count references). No ABNB registry or frozen scorer is touched. BKNG/EXPE remains deferred.
