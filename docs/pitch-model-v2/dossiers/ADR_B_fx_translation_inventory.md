> Research survey by an autonomous Opus subagent on 21 Sep 2026 (overnight ADR session), read-only against the repo at HEAD 2a77a36; archived verbatim as provenance for docs/pitch-model-v2/lines/adr_v1_design.md. Model output, not a team decision.

# B — FX-on-ADR translation: full inventory for an ex-ante (point-in-time) model

Read-only survey, 2026-09-21. Repo `/Users/theomachado/Citadel-ABNB` @ `theo/pitch-model-v2`.
Sibling licensed folders read but never modified; no web fetches. No file in any location was created,
edited or deleted except this report and two throwaway openpyxl scan scripts in the scratchpad.

Target identity throughout: `reported ADR y/y = ex-FX ADR y/y + fx_pts_adr`, `fx_pts_adr` in pp of y/y
ADR growth, denominator = prior-year quarter ADR, **gross of hedging** (hedges are designated against
revenue, never GBV/ADR — see §5).

---

## 1. FX daily data — what exists, coverage, and which is freshest

### 1.1 `data/processed/forecast_methods/fx_lag_v2/fx_daily_2026-09-11.csv` — **FRESHEST. Use this.**
- Columns: `date, ccy, fred_id, usd_per_unit, unit`
- 21,678 data rows (21,679 incl. header). Range **2018-01-02 → 2026-09-04**.
- 10 series, each 2,168 rows (USD_BROAD 2,166):

| ccy | fred_id | unit | last value 2026-09-04 |
|---|---|---|---|
| EUR | DEXUSEU | usd_per_foreign_unit | 1.1618 |
| GBP | DEXUSUK | usd_per_foreign_unit | 1.3521 |
| BRL | DEXBZUS | usd_per_foreign_unit | 0.195259 |
| MXN | DEXMXUS | usd_per_foreign_unit | 0.059301 |
| JPY | DEXJPUS | usd_per_foreign_unit | 0.006406 |
| AUD | DEXUSAL | usd_per_foreign_unit | 0.7209 |
| KRW | DEXKOUS | usd_per_foreign_unit | 0.000743 |
| CAD | DEXCAUS | usd_per_foreign_unit | 0.722857 |
| INR | DEXINUS | usd_per_foreign_unit | 0.010583 |
| USD_BROAD | DTWEXBGS | index_level_usd_strength | 118.0732 |

  **Unit convention:** all nine bilaterals are normalised to USD per one foreign unit (BRL/MXN/JPY/KRW/CAD/INR
  are inverted from the FRED "foreign per USD" convention by `1/v`). A **positive y/y on a bilateral = weaker
  dollar = ADR tailwind**. USD_BROAD is an **index level, not a price**: positive y/y = **stronger** dollar =
  headwind. Downstream code must filter on `unit`, never on `ccy`.
- Companion: `fx_fetch_manifest_2026-09-11.csv` (per-series `last_obs`, `last_value`, `n_obs_since_2018`,
  `fetched_at` 2026-09-11T16:53:04), and `fx_quarterly_2026-09-11.csv` (MultiIndex header
  `avg` / `yoy_pct` / `n_days` × 10 series, quarter labels `1Q18`…`3Q26`).

### 1.2 `data/processed/overnight/10_fx_daily.csv` — stale
- Columns `date, ccy, fred_id, usd_per_unit`. 19,467 rows. **2018-01-02 → 2026-08-28**. 9 bilaterals,
  **no USD_BROAD**. Superseded by 1.1 (5 business days older, and lacks the broad index).

### 1.3 `data/processed/overnight/05_fred_cache/` — 38 FRED CSVs, `observation_date,<SERIES>` format
- The ten FX series all end **2026-08-28**; histories are long:
  DEXUSEU 1999-01-04 (7,215), DEXUSUK 1971-01-04 (14,520), DEXBZUS 1995-01-02 (8,260),
  DEXMXUS 1993-11-08 (8,560), DEXJPUS 1971-01-04 (14,520), DEXUSAL 1971-01-04 (14,520),
  DEXKOUS 1981-04-13 (11,840), DEXCAUS 1971-01-04 (14,520), DEXINUS 1973-01-02 (13,999),
  DTWEXBGS 2006-01-02 (5,390).
- **Only use for pre-2018 history** (the v2 file starts 2018-01-02). Note the cache is in raw FRED units
  (not inverted) — `DEXBZUS` etc. are BRL per USD.

### 1.4 `FX-ADR-R-model/inputs/fx_daily.csv` (licensed sibling) — stale
- Columns `date, currency, value, source`. 21,628 rows. **2018-01-02 → 2026-08-28**.
  10 series × 2,163 (BROAD_USD 2,161): AUD BRL CAD EUR GBP INR JPY KRW MXN + `BROAD_USD`.
  Same FRED origin, different column names and `BROAD_USD` label.

### 1.5 "Theo Data" Bloomberg workbooks (licensed — series names and ranges only, no values copied)
- **`ABNB_Fundamentals_Alt_Macro_Bloomberg_LIVE.xlsx`** — sheets: `README, TEST_FIRST, Inputs, Prints,
  Consensus_Guidance, KPI_Quarterly, Alt_Data_Monthly, Macro_Daily, Macro_Monthly, Peers_Daily, Model_Panel`.
  - `Macro_Daily` (2,530 rows × 24 cols): BDH spill, header row 5 = alternating `Date` / series. FX series
    present: **EURUSD, GBPUSD, AUDUSD, USDCAD, USDBRL, USDMXN, USDJPY, USDINR Curncy (PX_LAST)** plus
    `DXY Curncy`, `VIX`, `SPX`, `USGG10YR`. Date range **2017-01-02 → 2026-09-04**, 2,525 daily rows.
    **No KRW.** End date is identical to the FRED refresh, so it offers no freshness edge — only a
    cross-check and a longer pre-2018 tail (2017 vs 2018).
  - `Macro_Monthly` (124 rows × 41 cols): monthly FX averages and a constructed basket —
    columns `EUR avg, GBP avg, AUD avg, CAD avg (USDCAD), BRL avg (USDBRL), MXN avg (USDMXN),
    JPY avg (USDJPY), INR avg (USDINR)`, index columns `USD/EUR idx … USD/INR idx`,
    **`FX basket (base = first month)`** and **`FX basket YoY %`**; month ends 2017-01-31 → 2026-12-31 (120 rows;
    forward months blank). Basket weights are the workbook's own, undocumented here.
  - `Model_Panel` (36 rows × 26 cols): quarterly regression panel with `FX basket YoY (q avg)`, `ADR YoY`,
    `GBV YoY`, `Revenue YoY`, `Take rate`, lags, alt-data, consensus surprise and reaction columns.
- `ABNB_Bloomberg_Revenue_Model (2).xlsx` — `README, TEST_FIRST, MNEMONICS, Fundamentals_Q, Operating_KPIs,
  Segment_Raw, Regional, VALIDATION, DIAGNOSTICS`. **No FX sheet.** (`Regional` is the FA_ABNB-style regional
  block the R-model rejected — see §3c.)
- `2026-09-11_rnpl_qog_extraction_BLOOMBERG.xlsx` — `README, TEST_FIRST, Inputs, FIELDS, PROBE_PAD,
  01_Prices_TR, 02_Consensus_PIT, 03_Fundamentals_Q, 04_Valuation_Daily, 05_Short_Interest, 06_Implied_Vol,
  07_Earnings_Hist, 08_Macro_Stress, 09_Peers_Fund_Q, 10_Manual_Exports, STATUS`. **No FX series**
  (`08_Macro_Stress` is consumer-stress: CONSSENT/UMCSENT etc.).
- `altd_export_trend_analysis_mzchki0v (1).xlsx` — single sheet `Trend Analysis`, alt-data, no FX.

### 1.6 `Citadel-ABNB-fx-engine/data` (licensed sibling)
- Mirrors the repo's overnight FX set at an older vintage: `data/processed/overnight/{10_fx_daily.csv,
  10_fx_quarterly.csv, 10_fx_basket.csv, 10_regional_fx_passthrough.csv, 10_regional_adr_fx.csv,
  05_fx_fits.csv, 05_fx_schedule.csv, 28_fx_hedge_{disclosures,forward,tests}.csv}`.
- `data/inputs/fx_engine/example/` — **synthetic** `exposure.csv, reference_rates.csv, scenario_rates.csv,
  parameters.csv, hedges.csv, prior_year.csv, forecasts.csv`. See §3e.
- `data/processed/fx_engine/research/` — `calibrations.csv, features.csv, predictions.csv, scores.csv,
  source_manifest.csv, study_metadata.csv, target_intervals.csv` (the R backtest study; §3e).

### 1.7 The fetch script — `analysis/src/forecast_methods/fx_lag_v2/fetch_fx_v2.py`
- **Confirmed: no API key.** It hits `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>` with
  `requests.get(..., timeout=60)` — the public unauthenticated CSV endpoint. Ten GETs, ~10 s.
- Series dict (with an `invert` flag):
  `DEXUSEU→EUR(F), DEXUSUK→GBP(F), DEXBZUS→BRL(T), DEXMXUS→MXN(T), DEXJPUS→JPY(T), DEXUSAL→AUD(F),
   DEXKOUS→KRW(T), DEXCAUS→CAD(T), DEXINUS→INR(T)`, plus `BROAD = DTWEXBGS`.
- Writes only into `data/processed/forecast_methods/fx_lag_v2/` with a hard-coded `STAMP = '2026-09-11'`.
  **A refresh today must change `STAMP`** or it silently overwrites the 11 Sep vintage (which the whole
  fx_lag_v2 / D5 / X1 chain depends on). Filters to `date >= 2018-01-01`.
- **H.10 publication lag**: FRED prints the H.10 weekly, so a fetch on day *d* reaches roughly *d*−5 business
  days. On 2026-09-11 it reached 2026-09-04. A fetch on **2026-09-21** should reach ~**2026-09-11/18**.

---

## 2. The disclosed ADR-FX target series — 17 points, 2Q22–2Q26 (CONFIRMED)

### 2.1 Canonical source
`data/processed/overnight/02_kpi_panel_quarterly.csv`, column **`fx_pts_adr`** (col 120 of 120; 24 quarterly
rows 3Q20–2Q26, of which **exactly 17 are non-empty: 2Q22 … 2Q26 inclusive**, no gaps).

Construction (`analysis/src/overnight/02_kpi_panel.py` L609):
```
w["fx_pts_adr"] = w["adr_yoy_reported_pct"] - num("adr_yoy_exfx_pct")
```
where `adr_yoy_reported_pct` is computed from the disclosed ADR **levels** (`adr_usd`, cents) and rounded to
1 dp, and `adr_yoy_exfx_pct` is the **letter's own whole-point ex-FX figure**. The same definition appears as
`adr_fx_effect = adr_yoy − adr_exfx_yoy` in `analysis/src/predictive/03_nowcast_tests.py` L66 →
`data/processed/predictive/03_quarterly_panel.csv`.

### 2.2 The 17 points

| q | adr_usd | adr_yoy_reported_pct | adr_yoy_exfx_pct | **fx_pts_adr** |
|---|---|---|---|---|
| 2Q22 | 163.74 | 1.4 | 7 | **−5.6** |
| 3Q22 | 156.44 | 4.9 | 12 | **−7.1** |
| 4Q22 | 152.81 | −0.5 | 5 | **−5.5** |
| 1Q23 | 168.43 | 0.2 | 3 | **−2.8** |
| 2Q23 | 166.01 | 1.4 | 2 | **−0.6** |
| 3Q23 | 161.38 | 3.2 | **0.5** | **+2.7** |
| 4Q23 | 156.73 | 2.6 | **0.5** | **+2.1** |
| 1Q24 | 172.88 | 2.6 | 2 | **+0.6** |
| 2Q24 | 169.53 | 2.1 | 3 | **−0.9** |
| 3Q24 | 163.64 | 1.4 | 2 | **−0.6** |
| 4Q24 | 158.13 | 0.9 | 2 | **−1.1** |
| 1Q25 | 171.34 | −0.9 | 1 | **−1.9** |
| 2Q25 | 174.48 | 2.9 | 1 | **+1.9** |
| 3Q25 | 171.29 | 4.7 | 2 | **+2.7** |
| 4Q25 | 167.51 | 5.9 | 3 | **+2.9** |
| 1Q26 | 186.82 | 9.0 | 4 | **+5.0** |
| 2Q26 | 183.73 | 5.3 | 4 | **+1.3** |

### 2.3 Rounding convention — the 0.5 quarters
Ex-FX ADR is disclosed as a **whole point in 15 of 17 quarters**. The two exceptions are
**3Q23 and 4Q23**, both coded **0.5**, and both come from the same phrasing
(`02_kpi_panel_long.csv` rows 481, 531):
- 3Q23: *"Excluding the impact of FX, ADR in Q3 2023 increased less than 1%"* (`letters/3Q23_d481318dex991.htm`)
- 4Q23: *"Excluding the impact of FX, ADR in Q4 2023 increased less than 1%"* (`letters/4Q23_d646462dex991.htm`)

So 0.5 is a **midpoint of the interval [0, 1)**, not a disclosed half-point. `fx_lag_v2/fits.py` scores the
ADR-FX target on **intervals of half-width 0.05** (`half = 0.05 if ycol == "fx_pts_adr"`), which is the
1-dp rounding of the *reported* leg only and **understates the uncertainty on the 3Q23/4Q23 rows by ~10×**.
An ex-ante fit should use a wider interval there ([reported−1, reported−0] ⇒ ±0.5 pp).

Two other verbatim wordings worth keeping (both fold to the same integer):
- 2Q22: *"a 1% increase from Q2 2021 (or 7% ex-FX)"*
- 3Q22: *"a 5% increase from Q3 2021 (or 12% ex-FX)"*
- 2Q26: *"On an ex-FX basis, ADR in Q2 2026 increased 4%"* (`letters/2Q26_d70413dex991.htm`, 6 Aug 2026).
  X1 notes the unrounded reported leg is **+5.301%**, so +1.3 is the panel figure to 1 dp.

### 2.4 Cross-references — one has fewer rows
- `docs/pitch-model-v2/dossiers/X1_x1_adr_fx_reconciliation.md` **§2a** publishes all **17** points as
  `adr_fx_pp_disclosed`, identical to §2.2 above. Governing dossier for the object's definition.
- `data/processed/q3nowcast/H/adr_history_components.csv`, column **`fx_effect_pp`** — **only 14 rows
  (1Q23–2Q26)**; 2Q22–4Q22 are absent. Values match §2.2 exactly on the overlap. It also carries
  `adr_exfx_yoy_pp`, `identity_check_pp` (|·| ≤ 0.043 pp everywhere — the identity closes), and the
  ex-FX decomposition (`geo_mix_pp, unit_size_pp, los_mix_pp, new_business_pp, interaction_pp,
  residual_pricing_pp`), plus `fx_basis = "disclosed (letter)"` on every row.
- **Contradiction to flag:** the 14-row `H` file and `fx_lag_v2`'s 14-quarter W1 window (1Q23–2Q26) both drop
  2Q22–4Q22, which are the three largest-magnitude observations (−5.6/−7.1/−5.5) and carry most of the
  identification of the basket weights. The 17-point series in the panel / X1 §2a is the full record and is
  the one an exposure-weight fit should use.

---

## 3. Existing estimators and their records

### (a) `adrv3` N / `overnight2` B4 — the COMMITTED estimator (DEC-0027)

**Source:** `analysis/src/overnight2/B4_application_3q26_4q26.py` (builds the two legs and the backtest);
`analysis/src/adrv3/N1_fx_estimator.py` (forms the midpoint and scores it).

**Leg 1, euro fit** — two-parameter OLS of the 17 disclosed points on contemporaneous quarterly-average
EUR/USD y/y, window `ex21`, n = 17 (`data/processed/overnight/05_fx_fits.csv`):
```
est_from_eur = -0.5687 + 0.4512 x EURUSD_yoy_pct(q)      r 0.9901, p 0.0, loo_rmse 0.5072
```
Alternative in the same file: `est_from_usd_broad = 0.5246 - 0.7154 x USD_BROAD_yoy_pct(q)`
(`ex21`, n 17, r −0.9641, loo_rmse 0.9905). `post22` (n 14) versions: eur `-0.6073 + 0.4602x` (r 0.9721),
broad `0.7285 - 0.5925x` (r −0.9508).

**Leg 2, regional baskets** — **no parameter fitted to the ADR-FX target**:
```
est_from_regional_baskets = SUM_r [ GBV_share_2025_r / SUM(shares) ] x passthrough_r x basket_yoy_r(q)
basket_yoy_r(q) = 100 * (exp( SUM_c w_c*ln(rate_c,q) - SUM_c w_c*ln(rate_c,q-4) ) - 1)   # log/geometric
```
with (exact, from B4 lines 116–130):
- `GBV_SHARE_2025 = {na 0.4415, emea 0.3743, latam 0.0936, apac 0.0907}` (sums to **0.9001**, then
  renormalised by `/sum` inside the formula → effective NA .4905, EMEA .4158, LatAm .1040, APAC .1008).
  **These are `gbv_share_pct`/100 for FY2025 from `data/processed/adr/01_regional_annual.csv`**
  (44.1478 / 37.4284 / 9.3587 / 9.0651 — the residual 9.99% is rounding across the four regions; confirmed).
- `PASSTHROUGH = {na 1.00, emea 1.04, latam 0.62, apac 0.86}` — the WS10 regional fits, re-tested in the ADR
  decomposition note. Source table `data/processed/overnight/10_regional_fx_passthrough.csv`:
  emea slope 1.043 (n 10, r 0.987, 1Q24–2Q26), latam 0.623 (n 7, r 0.996, 4Q24–2Q26),
  apac 0.86 (n 5, r 0.972, 1Q25–1Q26), **na 3.205 (n 5, r 0.849) explicitly "not identified: the NA basket
  moves less than 1.5pp across the sample, so the slope is noise" → carried at 1.00 by judgement**;
  pooled 0.712 (n 27).
- `DEST_BASKET` (destination-currency weights, judgement):
  `na  {USD .90, CAD .08, MXN .02}`
  `emea{EUR .70, GBP .25, USD .05}`
  `latam{BRL .55, MXN .38, USD .07}`
  `apac{AUD .55, JPY .20, KRW .10, INR .07, USD .08}`
  These are **identical in effect** to `data/processed/overnight/10_fx_basket.csv` once its proxy legs are
  mapped (`OTHER_EUR_LINKED .08 → EUR` gives EMEA EUR .62+.08=.70; `OTHER_LATAM .10 → BRL` gives .45+.10=.55;
  `OTHER_APAC .15 → AUD` gives .40+.15=.55). **No contradiction between B4 and 10_fx_basket.**

**Leg 3 (the committed one), midpoint** (`N1_fx_estimator.py`):
```
est_from_midpoint = (est_from_eur + est_from_regional_baskets) / 2
```

**Backtest file** `data/processed/overnight2/B/B_adr_fx_estimator_backtest.csv` — 17 rows, columns
`quarter, adr_fx_disclosed_pp, est_from_eur, est_from_usd_broad, est_from_regional_baskets,
err_est_from_eur, err_est_from_usd_broad, err_est_from_regional_baskets` (quarters `2022Q2`…`2026Q2`):

| q | disclosed | eur | usd_broad | baskets | err eur | err broad | err baskets |
|---|---|---|---|---|---|---|---|
| 2022Q2 | −5.6 | −5.828 | −4.042 | −4.752 | −0.228 | 1.558 | 0.848 |
| 2022Q3 | −7.1 | −7.149 | −5.931 | −6.357 | −0.049 | 1.169 | 0.743 |
| 2022Q4 | −5.5 | −5.376 | −5.602 | −4.945 | 0.124 | −0.102 | 0.555 |
| 2023Q1 | −2.8 | −2.525 | −2.461 | −2.558 | 0.275 | 0.339 | 0.242 |
| 2023Q2 | −0.6 | 0.459 | 0.264 | 0.342 | 1.059 | 0.864 | 0.942 |
| 2023Q3 | 2.7 | 3.100 | 2.655 | 3.395 | 0.400 | −0.045 | 0.695 |
| 2023Q4 | 2.1 | 1.829 | 2.395 | 2.453 | −0.271 | 0.295 | 0.353 |
| 2024Q1 | 0.6 | −0.042 | 0.326 | 0.826 | −0.642 | −0.274 | 0.226 |
| 2024Q2 | −0.9 | −1.076 | −1.344 | −0.661 | −0.176 | −0.444 | 0.239 |
| 2024Q3 | −0.6 | −0.143 | −1.146 | −0.213 | 0.457 | −0.546 | 0.387 |
| 2024Q4 | −1.1 | −0.960 | −1.963 | −1.005 | 0.140 | −0.863 | 0.095 |
| 2025Q1 | −1.9 | −1.915 | −3.627 | −2.439 | −0.015 | −1.727 | −0.539 |
| 2025Q2 | 1.9 | 1.844 | 0.584 | 1.311 | −0.056 | −1.316 | −0.589 |
| 2025Q3 | 2.7 | 2.301 | 1.932 | 2.026 | −0.399 | −0.768 | −0.674 |
| 2025Q4 | 2.9 | 3.549 | 3.384 | 3.364 | 0.649 | 0.484 | 0.464 |
| 2026Q1 | 5.0 | 4.446 | 5.332 | 5.060 | −0.554 | 0.332 | 0.060 |
| 2026Q2 | 1.3 | 0.586 | 2.343 | 1.696 | −0.714 | 1.043 | 0.396 |

**Window scores** (`data/processed/adrv3/N/N1_fx_estimator_window_summary.csv`) — note these are **in-sample**
(the euro coefficients were fitted on all 17), so they are an upper bound on ex-ante skill:

| window | n | RMSE eur | RMSE baskets | RMSE midpoint | bias eur | bias baskets | bias mid | wins e/b/m | best |
|---|---|---|---|---|---|---|---|---|---|
| full 2Q22–2Q26 | 17 | 0.458 | 0.535 | **0.406** | −0.000 | +0.261 | +0.131 | 7/6/4 | midpoint |
| 2022 surge 2Q22–4Q22 | 3 | **0.152** | 0.726 | 0.333 | −0.051 | +0.715 | +0.332 | 3/0/0 | eur |
| 2023 | 4 | 0.598 | 0.623 | **0.585** | +0.366 | +0.558 | +0.462 | 1/2/1 | midpoint |
| scored 1Q24–2Q26 | 10 | 0.455 | 0.416 | **0.332** | −0.131 | +0.006 | −0.062 | 3/4/3 | midpoint |
| scored 2Q24–2Q26 | 9 | 0.429 | 0.432 | **0.343** | −0.074 | −0.018 | −0.046 | 3/4/2 | midpoint |

**Forward card** `data/processed/adrv3/N/N1_fx_choice_card.csv` (ex-FX base +3.46 pp both quarters):

| q | estimator | fx_effect_pp | adr_reported_yoy_pp | adr_usd_point | base_adr_usd | recommended |
|---|---|---|---|---|---|---|
| 3Q26 | eur_fit | −1.12 | 2.34 | 175.29 | 171.29 | |
| 3Q26 | baskets | +0.26 | 3.72 | 177.66 | 171.29 | |
| **3Q26** | **midpoint** | **−0.43** | **3.03** | **176.47** | 171.29 | **True** |
| 4Q26 | eur_fit | −0.66 | 2.80 | 172.20 | 167.51 | |
| 4Q26 | baskets | +0.97 | 4.43 | 174.93 | 167.51 | |
| **4Q26** | **midpoint** | **+0.15** | **3.61** | **173.55** | 167.51 | **True** |

FY27 legs from D4's `06_adr_build.csv` (same family): 1Q27 −0.30, 2Q27 −0.19, 3Q27 +0.03, 4Q27 −0.29.

Per-quarter detail incl. the midpoint errors: `data/processed/adrv3/N/N1_fx_estimator_by_quarter.csv`.
Reconciliation of B's and S's published RMSEs: `N1_fx_estimator_reconciliation_check.csv`.

**Also in B4** (relevant to an ex-ante model that wants a mix channel):
`B_fx_translation_schedule_refresh.csv` (per-quarter `eurusd_level, eurusd_yoy_pct, usd_broad_yoy_pct,
adr_fx_pp_from_eur, adr_fx_pp_from_usd_broad, eurusd_yoy_avg_prior_2q, revenue_fx_pp_gross, hedge_pp,
revenue_fx_pp_after_hedge, basket_yoy_pct_{na,emea,latam,apac}, adr_fx_pp_from_regional_baskets`);
`B_mix_application_{regional,total}.csv` (the FX→cross-border-mix→nights→reported-ADR-mix channel, elasticity
base 0.1134 / low 0.0854 / high 0.2106 pp per pp on the cross-border purchasing-power index);
`B_index_weights.csv`, `B_relative_strength_quarterly.csv`, `B_forward_flat_spot_indices.csv`,
`B_fx_quarterly_avg.csv`, `B_fx_quarterly_yoy_logpct.csv`, `B_fx_daily_usd_per_unit.csv`.
**Caveat:** B4's hard-coded `ROOT`/`MAIN` are Windows paths (`C:\Users\krish\...`); it will not re-run
unmodified on this machine.

### (b) `data/processed/overnight/05_fx_fits.csv`
26 rows, columns `target, driver, lag, window, n, slope, intercept, r, p, spearman, perm_p, loo_rmse,
naive_rmse, loo_mean_rmse`. Windows `post22` (n 14) and `ex21` (n 17). Targets `adr_fx` and `rev_fx`.
The two `adr_fx … ex21` rows are the coefficients B4 hard-codes. `naive_rmse` for adr_fx is 2.0447 (ex21) /
2.053 (post22) — the "repeat-last" benchmark any new estimator must beat.
Also present: `rev_fx` fits on `eurusd_avg01 / avg12 / avg012` and `usd_broad_avg01 / avg12` (lag-averaged
drivers) — the revenue-side analogues, **not applicable to ADR** (see §3d/§6).

### (c) `FX-ADR-R-model` (licensed sibling) — the nearest existing ex-ante ADR-FX model

README summary: built 2026-09-07 from the `FA_ABNB_US.xlsx` Bloomberg workbook + the repo at `df833f5`.
R (4.5.2) + a Python openpyxl reader. `run_info.csv`: `asof 2026-09-07, latest_fx 2026-08-28,
financial_last 2026Q2, primary_adr "eurusd", primary_revenue "eur_lag12", publication_lag_calendar_days 7,
minimum_train 8, historical_vintage "current cached history; original publication vintages not verified"`.

**Backtest protocol (this is the template to copy for the walk-forward requirement):**
- Three forecast origins: **(i) the day before the quarter begins ("quarter_ahead"), (ii) day 60,
  (iii) 30 days after quarter-end or the day before the earnings release if earlier ("pre_earnings")**.
- FX observations restricted to **≥ 7 calendar days before the origin** (the H.10 lag). Unknown remaining
  weekdays take the last eligible quote; future holidays are approximated as weekdays.
- Each regression starts with ≥ 8 released observations and refits on earlier quarters only. Release dates
  from the repo guidance ledger; same-day releases excluded; pre-IPO rows fall back to a 90-day delay.
- Quarter-ahead origins also exclude financial results not yet released.

**Headline results (README table, RMSE):**

| target / timing | model | repeat-last | trailing-growth | n, span |
|---|---|---|---|---|
| **ADR FX, day 60** | **0.45 pp** | 2.02 pp | — | 9, 2Q24–2Q26 |
| **ADR FX, pre-earnings** | **0.49 pp** | 2.02 pp | — | 9, 2Q24–2Q26 |
| **ADR FX, quarter-ahead** | **1.39 pp** | 2.32 pp | — | 8, 3Q24–2Q26 |
| Total ADR, day 60 | $2.49 | $3.64 | $4.95 | 9 |
| Total revenue, day 60 | $90.6m | $102.4m | $125.7m | 9 |
| Total ADR, quarter-ahead | $3.13 | $4.57 | $6.19 | 8 |
| Total revenue, quarter-ahead | $106.4m | $134.7m | $148.4m | 8 |

**`outputs/fx_accuracy_common.csv`** (39 rows; `target, origin, model, n, first, last, mae, rmse, bias,
common_quarters`) — the full model horse-race. ADR-FX rows:

| origin | model | n | span | MAE | **RMSE** | bias |
|---|---|---|---|---|---|---|
| day60 | eurusd | 9 | 2024Q2–2026Q2 | 0.4037 | **0.4511** | −0.2743 |
| day60 | broadusd | 9 | | 1.0815 | 1.2039 | −0.4179 |
| day60 | basket | 9 | | 1.1230 | 1.2493 | −0.5348 |
| day60 | zero | 9 | | 2.0484 | 2.4183 | −1.0322 |
| day60 | last | 9 | | 1.5280 | 2.0206 | −0.0733 |
| day60 | trailing4 | 9 | | 2.3284 | 2.4462 | −0.4191 |
| pre_earnings | eurusd | 9 | | 0.4243 | **0.4853** | −0.1955 |
| pre_earnings | broadusd | 9 | | 1.0540 | 1.1418 | −0.4253 |
| pre_earnings | basket | 9 | | 1.0523 | 1.1226 | −0.5031 |
| quarter_ahead | eurusd | 8 | 2024Q3–2026Q2 | 1.2194 | **1.3919** | −0.4334 |
| quarter_ahead | broadusd | 8 | | 1.7757 | 2.0097 | −0.5987 |
| quarter_ahead | basket | 8 | | 1.7991 | 2.1146 | −0.8206 |
| quarter_ahead | zero | 8 | | 2.1945 | 2.5461 | −1.2711 |
| quarter_ahead | last | 8 | | 1.9434 | 2.3228 | −0.8172 |
| quarter_ahead | trailing4 | 8 | | 2.5967 | 2.9013 | −0.9740 |

(Revenue-FX rows in the same file: `eur_lag12` wins at 0.977 / 0.977 / 0.968 pp across the three origins,
`basket_lag12` 0.937 / 0.937 / 0.966 on 7/7/6 quarters — confirming the lag asymmetry of §6.)

**`outputs/currency_weight_assumptions.csv`** — exactly the B4/`10_fx_basket` destination weights:

| region | USD | CAD | MXN | EUR | GBP | BRL | AUD | JPY | KRW | INR |
|---|---|---|---|---|---|---|---|---|---|---|
| na | 0.90 | 0.08 | 0.02 | | | | | | | |
| emea | 0.05 | | | 0.70 | 0.25 | | | | | |
| latam | 0.07 | | 0.38 | | | 0.55 | | | | |
| apac | 0.08 | | | | | | 0.55 | 0.20 | 0.10 | 0.07 |

**`outputs/forecast_regional_weights.csv`** — *revenue*-based, last four released quarters, identical for
2026Q3 and 2026Q4: `na 0.4177369101, emea 0.3853636295, latam 0.0926362186, apac 0.1042632419`,
basis string *"last four released quarters; revenue share is a proxy for booking-currency exposure"*.
**Contrast with B4's FY2025 GBV shares (NA .4415 / EMEA .3743 / LatAm .0936 / APAC .0907)** — same
LatAm, ~2.4 pp less NA, ~1.1 pp more EMEA, ~1.4 pp more APAC. Both are proxies; neither is booking currency.

**`outputs/fx_predictions.csv`** — 498 data rows, columns `quarter, origin, cutoff, target, model, actual,
prediction, lower80, upper80, n_train, last_train_release`. Spans 2022Q2 → 2026Q2, targets `fx_adr_pp` and
`rev_fx_pp`, six/seven models × three origins. **This is the ready-made walk-forward scoring frame.**
Companions: `analysis_panel.csv`, `driver_predictions.csv`, `driver_accuracy.csv`, `fx_accuracy_all.csv`,
`forecasts.csv`, `forecast_model_comparison.csv`, `workbook_forward_comparison.csv`, `run_info.csv`,
`fx_backtest.png`, `forecast_scenarios.png`.

**Its live conditional forecast (FX through 2026-08-28, spot held):**
3Q26 ADR FX **−1.14 pp**, 4Q26 **−0.74 pp**; 3Q26 reported ADR $174.90, 4Q26 $171.72; 80% band on 3Q26
ADR FX **−1.83 to −0.45 pp**. Alternative specs for 3Q26: broad-dollar **+1.02**, regional basket **+0.06**.
Scenarios ±5% on foreign-currency USD values: 4Q26 ADR $167.95 / $175.49.

**Its own stated limits (verbatim in the README):** regional GBV fails to sum to global GBV in all 18
workbook quarters and is **excluded from primary exposure weights**; regional nights fails in 12 of 18;
71 of 72 regional cells fail `GBV = nights × ADR` at 1% → regional operating forecasts excluded.
*"Regressor selection had already been explored in the repository and preceding conversation, so these
should not be described as untouched validation results."* No transaction-level FX exposures, no hedge book,
no country currency shares, no booking-cohort conversion schedule.
`refresh-2026-09-07/` is a second, earlier variant of the same package (its own README/METHOD/outputs).

### (d) `analysis/src/forecast_methods/fx_lag_v2/` — the PIT machinery to reuse

Files: `common.py, baskets.py, fits.py, panel.py, pit_fx.py, exhibit.py, stages.py, registry_out.py,
run.py, fetch_fx_v2.py, README.md`. Outputs in `data/processed/forecast_methods/fx_lag_v2/` (27 files).

**`baskets.py` — how the basket is built.**
- `currency_quarterly()`: filters `unit == 'usd_per_foreign_unit'`, groups to `Period('Q')`, takes the
  **simple mean of daily rates**, then `yoy = (avg / avg.shift(4) - 1) * 100`. Also returns `n_days_min`.
- `basket_weights()`: reads `data/processed/overnight/10_fx_basket.csv`, drops `currency == 'BASKET'`,
  maps `proxy_series` onto a traded currency (`ccy_used`). **Judgement weights**, written out verbatim to
  `01b_basket_weights_used.csv` with `weight_vintage = "10_fx_basket.csv, overnight build; JUDGEMENT weights"`:

```
na    USD .90  CAD .08  MXN .02
emea  EUR .62  GBP .25  USD .05  OTHER_EUR_LINKED .08 -> EUR
latam BRL .45  MXN .38  USD .07  OTHER_LATAM .10      -> BRL
apac  AUD .40  JPY .20  KRW .10  INR .07  USD .08  OTHER_APAC .15 -> AUD
```
  (17 rows; each region sums to 1.00. Effective per-currency weights equal B4's `DEST_BASKET`.)
- `regional_baskets()`: **arithmetic** weighted mean of the per-currency y/y, USD legs at 0, divided by the
  region's total weight. (**Differs from B4, which uses a log/geometric weighted basket.** On moves of a few
  percent the two agree to ~0.01 pp; on the 2022 surge they can differ by ~0.1 pp. Flagged, not resolved.)
- `regional_revenue_weights()`: **trailing-4-quarter filed regional revenue shares** from
  `data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv`, forward/back-filled before 4Q22.
  Its own docstring records the PIT caveat: this function is **not** filtered on `knowable_from`, so the
  training features `b_lag1/2/3` and `eur_lag1/2` carry the current vintage; only the target quarter's own
  lag-0 basket is vintage-filtered (`pit_fx.regional_shares_asof`). Logged in `00_pit_caveats.csv`.
- Global basket `= SUM_r regional_basket_r x revenue_share_r`. Outputs `02_basket_quarterly.csv`
  (`quarter, quarter_canon, basket_{na,emea,latam,apac}_yoy_pct, basket_global_rev_wtd_yoy_pct,
  eurusd_yoy_pct, usd_broad_yoy_pct, w_na, w_emea, w_latam, w_apac, basket_global_qend_yoy_pct`,
  from 2019Q1) and `03_basket_reconciliation.csv`.

**`pit_fx.py` — the spot-held reconstruction and the observed share. This is the core PIT primitive.**
```python
def _q_avg_spot_held(ccy_px, q, asof, hold=None):
    days = pd.bdate_range(q.start, q.end)          # business days in the quarter
    s    = ccy_px.dropna()[index.date <= min(asof, q.end)]
    hold = last observed rate on/before asof (optionally shifted by hold_shift_pct)
    ff   = s.reindex(s.index | days).ffill().reindex(days)   # as-of fill for interior gaps
    vals = ff.values;  vals[days > last_obs] = hold          # spot held ONLY after last obs
    n_obs = count of days with a REAL print inside q
    return mean(vals), n_obs, len(days)
```
- **v2 fix (vs `fx_lag/pit_fx.py`):** the original filled *every* business day with no FRED print — bank
  holidays inside long-completed quarters included — with the *current* spot, injecting 2026 rates into 2025
  averages on 2–3 days of ~64. v2 uses the last rate observed on or before the day, and holds spot only
  after the last observation. `n_obs` therefore counts real prints and is the honest observed-share
  numerator. Effect: basket-driven PIT specs move 0.1–0.3 pp of RMSE (H0 W1 1.77→1.88, H3 W1 1.49→1.59);
  H2 unchanged because its driver is the disclosed ADR-FX point, not the basket.
- `regional_shares_asof(asof)`: filters L0 on `knowable_from <= asof`, takes the **last 4 available quarters**
  of filed regional revenue, normalises; falls back to `{na .42, emea .39, latam .10, apac .09}` if < 4.
- `basket_yoy_asof(q, asof, hold_shift_pct=0.0)`: both the target quarter **and its year-ago base** are
  rebuilt with the same `hold`, returning `{quarter, global_pct, elapsed_frac, na, emea, latam, apac}`.
  `hold_shift_pct` is the scenario knob (+x% = weaker dollar).

**`19_baskets_spot_held_v2.csv`** — `quarter, global_pct, obs_frac, source, na, emea, latam, apac`:

| q | global % | obs_frac | source | na | emea | latam | apac |
|---|---|---|---|---|---|---|---|
| 1Q26 | 5.6728 | 0.9531 | completed (as fitted) | 0.6948 | 9.5928 | 12.3831 | 4.8901 |
| 2Q26 | 2.2661 | 0.9692 | completed (as fitted) | 0.2436 | 1.8844 | 11.3685 | 2.6811 |
| 3Q26 | **0.5950** | **0.7121** | pit_reconstruction | 0.0697 | −0.8779 | 6.7136 | 2.3611 |
| 4Q26 | **1.3491** | 0.0 | pit_reconstruction | 0.2299 | 0.2690 | 6.1877 | 5.4691 |
| 1Q27 | 0.4137 | 0.0 | pit_reconstruction | 0.0136 | −0.4305 | 3.0240 | 2.8005 |
| 2Q27 | 0.3392 | 0.0 | pit_reconstruction | 0.0636 | 0.1107 | 0.3723 | 2.4218 |
| 3Q27 | 0.4958 | 0.0 | pit_reconstruction | 0.0994 | 0.5358 | 0.6897 | 1.8571 |
| 4Q27 | 0.0000 | 0.0 | pit_reconstruction | 0 | 0 | 0 | 0 |

(4Q27 is 0 by construction — at held spot the y/y base is itself the held spot. A forward path is needed to
make 4Q27 non-trivial; see the "NOT DERIVABLE" note in §6.)

**The package's own contemporaneous ADR-FX fit** (`fits.py` stage (b), printed live by `run.py`):
OLS of the disclosed ADR-FX on the **contemporaneous global basket**, 1Q23–2Q26, n = 14 →
**slope 0.8717, intercept −0.076, r 0.962, se 0.667** (`fx-lag.md` §2; `B4_FX_EXHIBIT.md` §5).
Its 3Q26 value is published as `adr_fx_3Q26_fitted_pp = 0.44` in `27_kernel_carried_fx_v2.csv`;
X1's arithmetic on the same coefficients gives 4Q26 **+1.10**. X1 uses these as the "high" leg of the band.
`fits.py` scores the ADR target on intervals of half-width **0.05** and the revenue target on **0.5**
(`NON_USD_SHARE = 0.56` is a module constant there, sourced to `28_fx_hedge_disclosures.csv`).
Objects A/B/C and the PIT machinery: `06_object_a_summary.csv`, `06b_object_a_hypothesis_tests.csv`,
`09b_pit_expanding_window_forecasts.csv` (cols `guide_date, target_quarter, spec, prior_basis, n_train,
n_train_pit, coef, point, sigma, actual, b0_pit, b0_elapsed_frac, n_params, in_W1, in_W2`),
`09c_pit_window_scores.csv`, `09d/09e` (full-sample-prior replay), `09f_replay_delta_pit_vs_full.csv`.

**`09c_pit_window_scores.csv`** (revenue-FX target, W1 = 14 guide dates, W2 = 10):
H2_phi_adrfx is best on both (RMSE 0.9936, bias +0.0975, interval RMSE 0.5782, hit-rate 0.30);
H0_contemporaneous 1.88/1.97; H3_free_weights 1.59/1.82; H1_repo_eur_mean_t1_t2 2.46/1.09.

**`20_observed_share_triple.csv`** — see §6.

### (e) The FX engine (licensed siblings) — a translation engine, **not** an estimated exposure model

`Citadel-ABNB-fx-engine/analysis/src/fx_engine/{engine,rates,calibration,backtest,io,contract,
run_forecast,RStudio_start}.R` + tests; mirrored in `FX_ENGINE_SESSION_BUNDLE/reusable_r/fx_engine/`.
Base R, offline, no packages.

**What exposure weights it assumes: none of its own.** `exposure.csv` is a *required input*
(`quarter, geography, currency, gbv_share, revenue_share, provenance`, each summing to 1 per
geography-quarter). The only shipped file is explicitly synthetic:
```
2027Q1,FR,EUR,1,1,SYNTHETIC example; replace with researched currency exposure
2027Q1,US,USD,1,1,SYNTHETIC example; replace with researched currency exposure
```
The README is blunt: *"Country or destination is not necessarily the actual transaction currency… Label
destination-based allocations as proxies."* and *"this release cannot establish an empirically calibrated
country-basket FX forecast."*

**Arithmetic it implements** (directly reusable for the ADR leg):
```
ADR factor      = 1 + adr_scale     x GBV-weighted currency change
Revenue factor  = 1 + revenue_scale x revenue-weighted LAGGED currency change
GBV after FX    = nights x reference-USD ADR x ADR factor
```
`parameters.csv` carries `adr_scale, revenue_scale, lag0, lag1, lag2, feature_basis, provenance`; lag weights
must be non-negative and sum to 1; `feature_basis` must be `exposure_basket_v1`. **The engine refuses an
EUR-proxy feature basis** precisely so an aggregate coefficient is never applied to an already
exposure-weighted basket. Default parameters are `scale = 1, lag0 = 1` — *"mechanical translation
assumptions… not fitted company timing."* "Latest-spot mode" (`quotes.csv`, `scenarios.csv`,
`run_config.csv` with `as_of, max_stale_days` default 14) implements exactly the spot-held rule:
*"Rates through the as-of date remain observed; later weekdays hold the last eligible quote, with the
scenario multiplier applied only to those future days… Quotes after as-of are excluded."*
`quote_audit.csv` records the true latest quote date.

**Calibration study** — `backtest.R` → `data/processed/fx_engine/research/`:
`calibrations.csv` (through-origin **non-negative slope, no intercept, bounded [0, 1.5]**, EUR proxy):

| target | candidate | slope | n_train | last_train_q | required_as_of | status |
|---|---|---|---|---|---|---|
| adr | current | **0.40880** | 16 | 2026Q1 | 2026-06-30 | research_only_incompatible_with_exposure_basket |
| adr | lag1 | 0.40265 | 16 | | | same |
| adr | lag12 | 0.37042 | 16 | | | same |
| adr | lag2 | 0.28566 | 16 | | | same |
| revenue_reported_cc | current | 0.30546 | 20 | | | same |
| revenue_reported_cc | lag1 | 0.33035 | 20 | | | same |
| revenue_reported_cc | lag12 | 0.31428 | 20 | | | same |
| revenue_reported_cc | lag2 | 0.22684 | 20 | | | same |

`scores.csv` (quarter-ahead origin only, **level**-effect pp — *not* comparable to the reported-minus-CC gap
RMSEs elsewhere): ADR current 1.348 midpoint / 1.011 interval (n 7, 2024Q3–2026Q1); rolling_selected 2.175 /
1.828; repeat_last 2.249 / 1.854; zero 2.594 / 2.169. Revenue: current 1.282 / 0.696; zero 1.661 / 1.119;
rolling_selected 1.813 / 1.177 — **the selector loses to zero on revenue**, which the validation note says
"does not justify automatic deployment of a revenue regression".
`study_metadata.csv`: `as_of 2026-09-08, last_cached_eur_quote 2026-08-28, minimum_training 8,
origin "quarter ahead", rate_buffer_days 7, assumed_release_delay_days 90`.
Validation report: `FX_ENGINE_SESSION_BUNDLE/reusable_r/fx-engine-validation.md` (dated 8 Sep 2026) —
17 ADR targets and 21 revenue targets; whole-percentage disclosures represented as **rounding intervals**,
and the **3Q23/4Q23 "less than 1%" statements kept as intervals [0, 1)** — the right treatment, and the
one thing it does better than `fits.py` (§2.3). Also `FX_ENGINE_SESSION_BUNDLE/repository_docs/
{fx-engine-design.md, fx-engine-plan.md}` and `FX_ENGINE_MENTAL_MAP.md`.

**Bottom line for exposure weights:** *no* object in the FX-engine family estimates GBV currency exposure.
Every exposure number in the programme is either (i) B4/`10_fx_basket` judgement destination weights,
(ii) filed **revenue** geography shares, or (iii) FY2025 **GBV** geography shares. The proposed
estimate-the-weights-from-the-17-points approach is genuinely new here.

### (f) `cohort_fx_v2` / L3 — one paragraph, and it does **not** touch ADR

`analysis/src/forecast_methods/cohort_fx_v2/{engine.py, run.py, README.md, tests}` →
`data/processed/forecast_methods/cohort_fx_v2/results_v2/` (11 files, byte-reproducible).
It is an offline deterministic **sensitivity engine on top of the frozen K0 two-lag revenue kernel**: it
splits the reported-dollar kernel contribution by currency, normalises to a fixed reference FX basis, and
replaces only the assumed **RNPL revenue-recognition FX timing**, producing a 180-cell scenario grid
(3 non-USD shares × 5 RNPL-exposure shares × 4 timing hypotheses × 3 post-cache FX paths) for 3Q26.
Headline conditional cell: at 20% RNPL exposure, 56% non-USD mix, equal recognition-month timing and flat
cached spot, the incremental Q3 timing replacement is **−$2.434M** on an unchanged $4,808.363M ordinary
kernel (replacement multiplier ≈ 0.999494). **Newly fitted parameters: zero. Historical predictive evidence:
W1 n = 0, W2 n = 0.** Its illustrative currency split (`L3_COHORT_FX_PREREG.md`) is
`USD 0.44; EUR 0.32, GBP 0.07, CAD 0.05, AUD 0.04, BRL 0.04, MXN 0.04` — explicitly "illustrative", with only
the 0.56 aggregate anchored to the FY2025 disclosure. **It is a revenue/RNPL-timing object; it neither
produces nor consumes an ADR number, and nothing in it should be quoted on the ADR line.** Docs:
`docs/revenue-forecast-strategy/05_backtests/L3_COHORT_FX_{PREREG, ACCOUNTING, RESULTS, RESULTS_v2,
INDEPENDENT_REVIEW_v1, INDEPENDENT_REVIEW_v2, AUDIT_REPAIR_v2, PERIOD_COVERAGE_v2}.md`.

---

## 4. Exposure priors — what can anchor the weight estimation

### 4.1 Regional **revenue** shares by quarter — `data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv`
72 data rows (4 regions × 18 quarters, **1Q22 – 2Q26**). Columns:
`quarter, region, revenue_musd, basis, source_row, period_days, vintage, accn, form, period_start,
period_end, source_path, knowable_from`. `basis` ∈ {`filed` 56, `back_out` 16}; `region` ∈
{na, emea, latam, apac}; source `data/processed/overnight/10_xbrl_revenue_geography.csv`.
**`knowable_from` is populated on every row** (= the filing date, e.g. 2Q26 rows 2026-08-06, 1Q26 2026-05-07,
4Q25 2026-02-12) — this is the field that makes PIT weights legal. Latest quarter (2Q26, $m):
na 1,594 / emea 1,425 / latam 291 / apac 298.
Derived trailing-4 shares at 2026Q3/Q4 (R-model, same filings):
**na .41774, emea .38536, latam .09264, apac .10426**.

### 4.2 Regional **GBV** shares by year — `data/processed/adr/01_regional_annual.csv`
30 rows = 6 years (2020–2025) × 5 (na, emea, latam, apac, total). Column **`gbv_share_pct`**:

| year | na | emea | latam | apac |
|---|---|---|---|---|
| 2020 | 55.111 | 27.870 | 7.117 | 9.901 |
| 2021 | 53.983 | 31.160 | 7.906 | 6.951 |
| 2022 | 51.012 | 33.990 | 7.654 | 7.344 |
| 2023 | 47.700 | 35.823 | 8.265 | 8.213 |
| 2024 | 46.239 | 36.376 | 8.672 | 8.713 |
| **2025** | **44.148** | **37.428** | **9.359** | **9.065** |

Also carries `nights_share_pct`, `revenue_share_pct`, `gbv_musd`, `nights_m`, `adr_computed`,
`adr_stated`, `take_rate_pct`, `alos_nights`, `source_10k`. FY2025 regional ADR levels
(`adr_computed`): na **255.03**, emea **158.89**, latam **94.91**, apac **118.20**, global **171.24**
— these are the levels B4 uses for the mix channel. Quarterly rebuild:
`data/processed/adr/04_regional_quarterly.csv`; 2Q26 nights shares
`{na .28255, emea .41550, latam .17862, apac .12333}` (B4 `SHARE_2Q26`).
**Note the drift: NA GBV share falls ~2 pp/yr. A fixed FY2025 weight vector applied back to 2Q22 (as B4 does)
mis-weights the 2022 surge quarters by ~7 pp of NA share. An ex-ante model should use the
point-in-time-available annual (or trailing-4 quarterly) shares.**

### 4.3 The "non-USD share" — **the ~56% is REVENUE, not GBV. Do not use it as the GBV constraint.**
- Primary disclosure: **FY2025 10-K**, *"56% non-USD revenue for 2025"*
  (`docs/revenue-forecast-strategy/05_backtests/L3_COHORT_FX_ACCOUNTING.md`, citing the FY2025 10-K Note 2 /
  Item 7A, filed 12 Feb 2026, `sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm`).
- Machine-readable series: `data/processed/overnight/28_fx_hedge_disclosures.csv`, column
  **`non_usd_revenue_share`** — **0.54 for 1Q23–4Q24, 0.56 from 1Q25 through 2Q26** (14 quarters).
  Mirrored in `fx_lag_v2/22_hedge_gross_vs_after.csv` and hard-coded as `NON_USD_SHARE = 0.56` in
  `fx_lag_v2/fits.py`.
- **The non-USD share of GBV is nowhere disclosed.** The repo's two estimates:
  - `docs/revenue-forecast-strategy/02_proposals/M6_fx_takerate_timing_mechanics.md` §"Priors":
    `s_G ~ Normal(0.68, 0.05)` "from the nights mix" (against `s_R ~ Normal(0.56, 0.03)`
    "hard-anchored on the disclosed non-USD revenue share"); its two-parameter basket fit lands the ADR leg
    at **`s_G = 0.66`** — "essentially the disclosed non-USD share of GBV implied by the nights mix".
  - The judgement destination baskets imply a much lower non-USD GBV share:
    `1 − Σ_r share_r × USD_weight_r` with FY2025 GBV shares ≈ **1 − (.4905×.90 + .4158×.05 + .1040×.07
    + .1008×.08) ≈ 0.52** — i.e. the B4 basket assumes *less* non-USD exposure on GBV than the disclosed
    revenue share, which is backwards (GBV is the more foreign of the two: NA's USD .90 and EMEA's USD .05
    are the two weights `fx-lag.md` names as the culprits).
  - `fx-lag.md` §"scale": the fitted gross revenue-FX scale is **0.95 with CS [0.63, 1.33]** on the basket,
    against the disclosed 0.56 — *"the basket has to move 0.95 pp to explain 1 pp of disclosed revenue FX,
    i.e. it understates the true currency exposure by about 70%… a finding about the basket weights"*.
    Repeated in `07_MORNING_REPORT.md` L121 and `AGENT_BRIEF.md` §2 (FX row) and
    `lane1_briefs_v2/X_REGIONAL_KERNEL_OD_FX.md`.
  - `docs/2026-09-06_research-inventory.md` L241 says *"FX: 55% of revenue non-USD"* — a third figure,
    inconsistent with the 0.54/0.56 series. **Treat 0.56 (1Q25→) / 0.54 (1Q23–4Q24) as governing.**

  **This is the single most useful finding for the proposed model:** the 0.95 fitted scale against a 0.56
  disclosed revenue share is exactly the evidence that the judgement weights are too USD-heavy, and it says
  the free-weight estimate should be allowed to run well above the naive 0.52–0.56, toward 0.66–0.70 on GBV.
  Do **not** hard-constrain `Σ non-USD weights = 0.56`; that is the revenue constraint and it is the wrong
  object for a GBV-weighted ADR basket. The defensible constraints are
  `w ≥ 0`, `Σ w = s_G`, with `s_G` regularised toward 0.66–0.68 and reported as a fitted quantity.

### 4.4 Cross-currency share of GBV — the quote
`data/processed/overnight/02_kpi_panel_quarterly.csv` column **`cross_currency_share_of_gbv_pct = 20.0`,
one row only (1Q25)**. Provenance (`02_kpi_panel_long.csv` L775 and `analysis/src/overnight/02_kpi_panel.py`
L472, verbatim):
```
add("1Q25", "cross_currency_share_of_gbv_pct", 20, "pct",
    "cross-currency transactions comprise approximately 20% of our GBV")   # letters/1Q25_d40594dex991.htm
```
Context (`docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` §2.3):
*"Cross-currency / FX service fee — take rate (+) — +20 bps y/y in 2025 (Mertz, 4Q24 call).
Cross-currency ≈ 20% of GBV (1Q25). Disclosed once each, then dropped."*
**Interpretation warning:** "cross-currency" = guest's payment currency differs from the listing's currency.
It is a **lower** bound on foreign exposure in one sense and an unrelated quantity in another — a French
guest booking a French listing in EUR is *not* cross-currency but *is* 100% non-USD for translation. It
constrains the fee/take-rate line, **not** the translation weight vector. Related: `cross_border_share_pct`
(20 → 46 across 1Q21–1Q24, then dropped) and `data/processed/overnight/05_crossborder_share.csv`.

### 4.5 Per-country supply data — the only route to a supply-weighted currency split
`data/processed/q3nowcast/E/market_geo.csv`: **123 markets, 3 columns (`market_key, country, region`),
37 countries**:
- **NAM 42 markets** — united-states 34, canada 8
- **EMEA 57** — italy 10, spain 9, france 4, united-kingdom 4, greece 4, belgium 3, switzerland 3,
  the-netherlands 3, germany 2, ireland 2, portugal 2, austria/czech-republic/denmark/hungary/kenya/latvia/
  malta/norway/south-africa/sweden/turkey 1 each
- **APAC 17** — australia 11, china/japan/new-zealand/singapore/taiwan/thailand 1 each
- **LatAm 7** — brazil 2, argentina/belize/chile/colombia/mexico 1 each

Companions in the same directory usable as weights: `inventory.csv` (per-market Inside Airbnb listings/reviews
dumps with byte sizes and dump dates), `stable_listing_index.csv`, `index_quarterly.csv`,
`market_monthly_yoy.csv`, `market_vintage_{daily,monthly}.csv`, `coverage_monthly.csv`,
`region_monthly_index.csv`, `partial_vs_full_quarter_market.csv`, `q3_2026_coverage.csv`.
**Caveats:** 123 markets is a *sample*, not a census; it is city-level and coverage is wildly uneven
(34 US markets vs 1 for all of Japan); and — critically — `AGENT_BRIEF.md` §6 kills *"the 120-market panel as
a nights measurement"*. As a **currency-share prior** (listing counts × local currency) it is a different use
than the killed one, but the same coverage bias applies and it must be said out loud. Listing-level *prices*
(which would give a value-weighted, not count-weighted, split) are in the raw Inside Airbnb dumps referenced
by `inventory.csv`, not in the processed tree.

---

## 5. Hedging — and whether ADR/GBV is hedged (verified)

**Answer: ADR and GBV are NOT hedged. The disclosed ADR-FX effect is gross, a pure translation restatement.**

Verified statements:
- X1 §2, verbatim: *"It is **gross of hedging** — Airbnb's hedges are designated against *revenue*, never
  against GBV or ADR, so the letters' ADR ex-FX sentence is a pure translation restatement while the revenue
  FX sentence is stated after hedging."*
- `B4_FX_EXHIBIT.md` §3.1, the **hedge-once rule**: *"the letter-stated revenue-FX points are ALREADY AFTER
  hedges… `28_fx_hedge_forward.csv` is never added on top of a letter-stated point… Hedges are on the loss
  side and cannot be the source of the tailwind; any note that says otherwise is wrong."*
- `07_MORNING_REPORT.md` L124: *"`gross_ex_hedge + hedge_effect = stated` holds on all 14 quarters to 1e-6.
  Hedges did nothing to revenue growth 1Q23-2Q25; from 3Q25 they subtract −1.13, −0.93, −0.66, −0.61 pp as
  designated notional grew $2.6bn → $3.4bn (45–47% of LTM non-USD revenue). **The forward hedge file is never
  added on top of stated after-hedge FX.**"*
- `03_insider_mechanics.md` §2.4: policy is cash-flow hedges of **forecast revenue** "typically for up to
  18 months", 1Q23 onward; designated notional $0.5bn (1Q23) → $3.4bn (2Q26); AOCI on hedges −$59m (4Q25) →
  +$39m (2Q26).

**Files:**
- `data/processed/overnight/28_fx_hedge_disclosures.csv` — 14 rows 1Q23–2Q26, 19 columns:
  `designated_notional_musd, non_designated_notional_musd, aoci_cash_flow_hedges_musd,
  oci_cash_flow_hedges_in_quarter_musd, reclassified_to_revenue_musd, expected_reclass_next_12m_musd,
  revenue_musd, revenue_prior_year_musd, hedge_effect_on_revenue_growth_pp, stated_revenue_fx_pp,
  gross_fx_ex_hedge_pp, **stated_adr_fx_pp**, eur_usd_yoy_pct, gbp_usd_yoy_pct, ltm_revenue_musd,
  non_usd_revenue_share, designated_notional_pct_of_ltm_non_usd_revenue, expected_reclass_pp_of_ltm_revenue`.
  **Note `stated_adr_fx_pp` has NO gross/after-hedge pair** — because there is nothing to pair it with. That
  is the file-level confirmation that ADR is unhedged. Its 14 values match §2.2 exactly on 1Q23–2Q26.
- `data/processed/overnight/28_fx_hedge_forward.csv` — 4 rows (3Q26 −0.21, 4Q26 −0.21, 1Q27 −0.18,
  2Q27 −0.18 pp), note: *"2Q26 10-Q: ~$26M of deferred net losses expected to be reclassified to revenue in
  the next 12 months; spread by 2025 revenue seasonality"*. **Revenue only.**
- `data/processed/overnight/28_fx_hedge_tests.csv` — the lag tests (EUR/USD y/y on gross revenue FX:
  r 0.763 lag 0, **0.861 lag 1**, 0.58 lag 2, n 14).
- `data/processed/forecast_methods/fx_lag_v2/22_hedge_gross_vs_after.csv` — 18 rows (14 historical + 4
  forward), with `identity_gross_plus_hedge_equals_stated = True` on all 14 and a `hedge_once_rule` string
  repeated on every row.
- Broader grep hits (`grep -ril hedg docs data/processed`): `docs/terminal_guide.md`,
  `2026-09-07_revenue-forecasting-inventory.md`, `2026-09-06_research-inventory.md`,
  `rnpl-short-audit/{01,02,03,04,05a}`, `q3nowcast/{BRIEF.md, overnight2_synthesis_copy.md}`,
  `revenue-forecast-strategy/{WORKBOARD_L3_SOURCE_CONTRACT_v1, WORKBOARD_L3_v3, 00_OVERNIGHT_RUNBOOK,
  07_MORNING_REPORT, WORKBOARD_LANE4_v2, lane1_refuters_v2/X_mechanism, 01_ground-truth/*,
  lane1_briefs_v2/X_REGIONAL_KERNEL_OD_FX, 02_proposals/{M1,M2,M3}}`, and the L3 cohort set.

**Consequence for the model: no hedge term enters the ADR-FX equation at all.** Any hedge pp appearing
anywhere near the ADR line is an error of the same family as the D5/X1 mislabelling.

---

## 6. Point-in-time conventions already established

### 6.1 `docs/thesis-kernel-topdown/lane2/CONVENTION.md` (the authoritative PIT page)
Written because Lane 1's A and B′ came back **0/14, 0/10 — empty, not negative** from over-tight wording.
Five rules:
1. **"A guide-date vintage is the close of the letter day."** Airbnb releases after the close; FORMAT 1.0 §PIT
   allows `knowable_from <= vintage_date`, so everything in the letter dated *d* is knowable at
   `vintage_date = d` (including GBV_q and GBV_{q−1}). `kernel_engine_v2` refuses same-day inputs by design —
   call it with `as_of = d + 1 day` and say so.
2. **Morning-of-print consensus is pre-letter.** `16_consensus_at_print_merged.next_q_cons_revenue_musd`;
   L0 roles `pre_guide` (`PG-<quarter>-revenue`) / `at_print` (`AP-…`), `pit_usable = True`.
   Inadmissible: rows stamped after *d*, `pit_usable = False`, `vendor_attributed = False`, and every
   `role = current` (September-2026) row at a historical date. The 6 Aug 2026 pre-guide 3Q26 Street is
   **LSEG $4,610M and nothing else**.
3. **Executable returns start at the next open** (`returns_v1/earnings_reactions_open_v1.csv`);
   `gap_pct` is not executable and enters no return statistic.
4. **Registration dates:** historical W1/W2 rows take vintage = the guide date (FORMAT 1.0); LIVE rows
   (2026Q3, 2026Q4, 1Q27) take vintage = **the real run date** (FORMAT 1.1).
   *"Never backdate a September forecast to 2026-09-11; never date it 5 Nov."*
   Subagents register; **only the parent scores.**
5. Worked example: *d* = 2026-08-06, guide 3Q26 $4,690–4,770M (mid 4,730), entry 2026-08-07 open,
   `excess_open_20d_pct` +12.8 pp.

### 6.2 `docs/revenue-forecast-strategy/05_backtests/B4_FX_EXHIBIT.md` §2 — observed share
Definition (unchanged from `00_IMPLEMENTATION_DECISIONS` §2.4):
```
FX-determined share = w1 + w2 + w0 x f      # f = share of the target quarter already in the average
```
Three specifications always reported **together**: (a) free fit (stated `w0 = 0.5315`, gross `w0 = 0.5654`),
(b) Φ kernel (0, ⅔, ⅓) → `w0 = 0`, (c) contemporaneous → `w0 = 1`.
Two readings of `f`: **calendar days elapsed** (the programme's existing convention, and the one that
reproduces M6's 0.54) and **FRED business days actually printed** (allows the H.10 one-week lag).

`20_observed_share_triple.csv` (20 rows; `as_of, what, target_quarter, spec, w0, days_elapsed,
days_in_quarter, elapsed_frac_calendar, observed_frac_fred_prints, fred_data_through,
fx_determined_share_calendar, fx_determined_share_fred_observed, fx_determined_share_cs_lo,
fx_determined_share_cs_hi, volume_determined_share`):

| as_of | target | f calendar | f FRED | fred_data_through | (a) free | (b) Φ | (c) contemp | volume |
|---|---|---|---|---|---|---|---|---|
| **2026-08-06** 3Q26 guide | 3Q26 | 0.3913 | 0.3788 | 2026-08-05 | 0.68 [0.39,1.00] | 1.00 | 0.39 | 1.00 |
| **2026-09-11** today (build) | 3Q26 | 0.7826 | 0.7121 | 2026-09-04 | 0.88 [0.78,1.00] | 1.00 | 0.78 | 1.00 |
| **2026-10-02** memo / pitch | 4Q26 | 0.0109 | 0.0000 | 2026-09-25 | 0.47 [0.01,1.00] | 1.00 | 0.01 | **0.333** |
| **2026-11-05** 4Q26 guide (3Q26 print) | 4Q26 | 0.3804 | 0.3182 | 2026-10-29 | 0.67 [0.38,1.00] | 1.00 | 0.38 | 1.00 |
| **2027-02-11** 1Q27 + FY27 guide (4Q26 print) | 1Q27 | 0.4556 | 0.3906 | 2027-02-04 | 0.71 [0.46,1.00] | 1.00 | 0.46 | 1.00 |

*"Read off the FRED-print column instead and every free-fit number falls by 2–4 pp… and every contemporaneous
number by 6 pp. The gap between the calendar and the data is the publication lag, and it is the one part of
'already observed' that is a fact rather than a modelling choice."*

**The three decision dates are therefore: 2026-10-02 (pitch/memo), 2026-11-05 (3Q26 print + 4Q26 guide),
2027-02-11 (4Q26 print + 1Q27/FY27 guide).** Note the asymmetry the exhibit insists must be said out loud:
at the 2 Oct pitch date the **volume**-determined share of the 4Q26 kernel is only **0.333** (only 2Q26 GBV
has printed) while the FX-determined share on a contemporaneous reading is **0.011**.

**ADR is contemporaneous.** Because ADR FX is contemporaneous-at-booking (§6.3), the relevant column for the
ADR line is **(c)**: at the 2 Oct pitch date **1.1% of 4Q26's FX is observed on the calendar and 0.0% has
printed**; at 5 Nov, 38.0% / 31.8%; at 11 Feb 2027 for 1Q27, 45.6% / 39.1%. **That is the honest observed
share for an ADR-FX call, and it is small.** The 0.67/0.88/1.00 numbers belong to revenue.

### 6.3 The "spot held" rule and the contemporaneity of ADR
- Rule (from `pit_fx.py` and repeated in the README/exhibit): **"QTD actual + spot held"** — actual daily
  prints through `min(asof, quarter_end)`, interior missing days filled with the last rate observed **on or
  before** them, and the last observed rate held constant for all business days **after** the last
  observation. **The year-ago base quarter is rebuilt under the same rule.** Quarterly aggregation is the
  simple mean over business days.
- `fx-lag.md` §4 (the sentence X1 calls definitive): ***"ADR FX is contemporaneous-at-booking by
  construction, so if the revenue leg needs a lag and the ADR leg does not, the wedge should load on lags
  1-2 and not on lag 0"*** — and it does (r −0.05 at lag 0, positive at lags 1 and 2). GBV, nights and
  therefore ADR are **booking-quarter** metrics; revenue is recognised at check-in, ~0.43–0.50 quarters later.
  Effective revenue lag point estimate **0.50 q** (95% CS 0.00–1.19) stated / **0.43 q** (CS 0.03–0.92) gross.
- **No forward curve exists.** `fx-lag.md` §"Forward curve: NOT DERIVABLE" — *"The FRED cache contains spot
  bilaterals and DTWEXBGS only — no forward points, no FX futures, no interest-rate differentials for the
  non-USD legs. The forward-curve path requested in (e) is therefore reported as unavailable rather than
  fabricated, and the scenario set is spot-held plus a parallel shift."* So the predictive band must come
  from **realised FX volatility**, not from option-implied or forward-implied distributions, unless a new
  source is licensed. (Bloomberg `DXY Curncy` and the eight bilaterals in `Macro_Daily` are spot only.)
- Existing scenario grammar: `05_fx_schedule.csv` carries three named paths — `consensus`, `strong_usd`,
  `weak_usd` — quarterly from 2025Q3 to 2027Q4, with columns `eurusd_level, eurusd_yoy_pct, usd_broad_yoy_pct,
  adr_fx_effect_fit_eur_pp, adr_fx_effect_fit_usd_pp, revenue_fx_fit_pp, revenue_fx_fit_contemp_pp,
  adr_fx_effect_actual_pp, revenue_fx_actual_pp, driver_realised_share, status`. Its `status` values are
  `actual` / `quarter-to-date to 2026-08-28` / `path`, and `driver_realised_share` is the older analogue of
  the observed-share column (2026Q4 0.84, 2027Q1 0.34, 2027Q2+ 0.00 — those are the **revenue** driver's
  realised shares and must not be reused for ADR). `fx_lag_v2` uses `hold_shift_pct` ±x% instead.
- `00_pit_caveats.csv` records four caveats that carry over to any new build: the H.10 5-business-day lag;
  the gross-ex-hedge target being non-PIT structural; the training-feature basket lags not being
  vintage-stamped; and the holiday-fill bug fixed in v2.

---

## 7. Constraints on how ADR FX may be quoted

### 7.1 `docs/pitch-model-v2/DECISIONS.md`

- **DEC-0027** (2026-09-18, D4, 3Q26–4Q26, base) — **the binding one**:
  > ADR FX = card N midpoint. The ADR FX object is D4's adrv3 N1 midpoint (3Q26 **−0.43 pp**, band
  > **−1.12 to +0.44**; 4Q26 **+0.15 pp**, band **−0.66 to +1.10**): it is the effect Airbnb discloses
  > (reported minus ex-FX ADR y/y) and scores RMSE 0.42 pp against the 17 disclosed quarters; D5's
  > "adr_fx_pp" (+2.89) is fx_lag_v2's Φ-lagged revenue-FX construction and is **renamed at source, never
  > added to an ADR growth rate**; no committed cell changes (DEC-0008's 176.88 already carries −0.43).
  > Rejected: D5's +2.89; a range of both.

- **DEC-0010** (2026-09-18, D5, 4Q26) — the *revenue* FX decision, kept strictly separate:
  revenue FX **+0.98 pp** base (spot held; Φ×0.851 adopted), +0.52 short (USD one sigma stronger),
  +1.45 breaker (one sigma weaker); confidence set +0.3 to +2.2; **"memo's '84% observed for 4Q26' relabelled
  as a 3Q26 figure"**; grade B accepted.

- **DEC-0008** (D4, 3Q26, base **176.88**): ADR card v3 **without** the fee-migration term K; K (+0.17 pp)
  carried as a labelled sensitivity (with_K 177.17).
- **DEC-0020** (all): **base scenario only** — *"The spec's `meta.scenarios` is reduced to `[base]` until
  reopened; dossier short/breaker rows stay on record."* So a new ADR-FX model may publish a band, but only
  the base row enters the spec.
- **DEC-0029** (D1, 3Q26): nights base 146.8m (+9.89%), superseding DEC-0024/DEC-0004.

### 7.2 `docs/revenue-forecast-strategy/AGENT_BRIEF.md` §6 kill list — verbatim, FX-relevant items
> The **−3.4 pp Q4 FX step (double subtraction)** · **"82% of Q4 FX already determined"** · "+4.05% fee uplift"
> as measured · the 9/9 guide-below-Street drift rule as a tradeable signal · "half of ADR growth is bigger
> units" (it is +0.46–0.8 pp) · any FY27 level edge without the +9.2–11.5% band · any p-value for the drift
> rule · restated unearned fees as a pin or a feature (circular) · the 1.71M quote panel as "fee-inclusive" ·
> "nothing beats guide × cushion" (say: no single object beats it on both windows) · **mixing a September
> consensus value into a historical guide date** · M5's hierarchical cushion model · **the 120-market panel as
> a nights measurement** · the Stan state space for the prelim.
> (Full lists: `05_backtests/RED_TEAM.md`, `research/notes/overnight/14_master-synthesis.md` §11.)

Also from §2 (FX row): *"4Q26 revenue FX +1.0 pp (CS +0.3–2.2); the −3.4 pp step double counts;
pre-registered: stated 3Q26 FX ≈ +3 → kernel"* — X1 notes explicitly: **"the brief's §2 FX row is entirely
about revenue FX; the programme has no pre-registered line for the ADR-FX estimator at all."**
That is the opening for a new registered ADR-FX object — and it also means a new one must be registered
before it is scored, per CONVENTION.md §4.

### 7.3 Other governing constraints found
- `docs/revenue-forecast-strategy/05_backtests/FXSWAP_h2_bridge_kernel_fx.md` §1/§4 already swapped the
  bridge's ADR-FX line to **−0.43 / +0.15** and named the live gap as *"basket-contemporaneous +0.4 vs
  midpoint −0.4, a 0.8 pp disagreement"* — **0.8 pp, not 3.3 pp**.
- `REBASE_h2_bridge_v3_nights_adr.md` §5/§7.3: bridge v3 reproduces the ADR v3 card exactly
  (3Q26 ADR $177.17, 4Q26 $174.58) on the same FX leg.
- `N1_fx_estimator.py` self-declares: *"not a test … decision memos, not pre-registered pass/fail
  workstreams."* X1 §4 records this as a weakness of the committed object.
- `docs/pitch-forecasts/questions/q3-revenue-fx-integer/datasets/c08_spec_points.csv` — the candidate list
  for the 3Q26 **revenue**-FX integer; contains "Φ on disclosed ADR-FX at scale 1 (reading A), less 0.21 pp
  hedge" = 2.32 and "H2 Φ on disclosed ADR-FX, PIT coefficient 0.7313 (the registered spec)" = 1.85.
  Independent confirmation that the Φ-on-ADR-FX family is a **revenue** family in the programme's registry.

---

## 8. Contradictions and open items to flag

1. **56% is a REVENUE share, not GBV.** (§4.3) The task brief asks for "the disclosed non-USD share (~56%?)".
   It is disclosed, it is 0.56 (0.54 pre-1Q25), and it is **revenue**. The non-USD GBV share is **not
   disclosed anywhere**; the repo's estimates are 0.66 (M6 fit) and 0.68 (M6 prior from the nights mix),
   against ~0.52 implied by the judgement destination baskets. Constraining `Σ w = 0.56` would bake in a
   known-wrong number.
2. **Two different regional weight vectors are both in live use.** B4/adrv3 uses FY2025 **GBV** shares
   (.4415/.3743/.0936/.0907, renormalised from a 0.9001 sum); `fx_lag_v2/baskets.py` and the R-model use
   trailing-4-quarter filed **revenue** shares (2026Q3: .4177/.3854/.0926/.1043). NA differs by 2.4 pp.
   For an ADR (booking-value) model, GBV shares are the right family — but they are annual and stale, and
   they drift ~2 pp/yr in NA.
3. **Fixed FY2025 weights are applied to 2Q22.** B4 backtests all 17 quarters on a single FY2025 GBV weight
   vector. NA's GBV share was 51.0% in 2022 vs 44.1% in 2025. This mis-specification is largest exactly in
   the 2022 surge quarters that carry most of the identification.
4. **Arithmetic vs geometric basket.** B4 uses log/geometric weighting; `fx_lag_v2/baskets.py` uses an
   arithmetic weighted mean. Immaterial at small moves, ~0.1 pp in 2022.
5. **The 3Q23/4Q23 interval is mis-scored.** `fits.py` uses ±0.05 pp on every ADR-FX observation; the two
   "less than 1%" quarters are really ±0.5 pp. The FX-engine study (`fx-engine-validation.md`) handles this
   correctly with intervals [0, 1). Fix in any new likelihood.
6. **n = 14 vs n = 17.** `q3nowcast/H/adr_history_components.csv` and `fx_lag_v2`'s W1 both start at 1Q23 and
   drop 2Q22–4Q22. The full disclosed record is 17.
7. **`fetch_fx_v2.py` has a hard-coded `STAMP = '2026-09-11'`** — re-running it today overwrites the vintage
   that D5/X1/B4 depend on. Change the stamp.
8. **B4 will not re-run here** (hard-coded `C:\Users\krish\...` paths). Its outputs are trustworthy; the
   script is not executable on this machine without edits.
9. **Three different non-USD figures appear in docs**: 0.54, 0.56, and a stray "55%" in
   `docs/2026-09-06_research-inventory.md` L241. The 28_fx_hedge_disclosures series governs.
10. **The observed-share table's headline numbers (0.67 / 0.88) are revenue numbers.** For the ADR line the
    contemporaneous column applies: 0.011 calendar / 0.000 FRED at the 2 Oct pitch date for 4Q26.
    Quoting 0.67 or "82%" on an ADR-FX claim is exactly the AGENT_BRIEF §6 kill-list error.
11. **No forward FX curve is available in-repo.** The predictive band must come from realised volatility of
    the currency basket, and the scenario set is spot-held ± a parallel shift.
12. **The committed midpoint's 0.406 / 0.332 pp RMSEs are in-sample** (the euro leg's coefficients were
    fitted on all 17 points). The only genuinely walk-forward ADR-FX scores in the programme are the
    R-model's — **0.45 pp day-60, 0.49 pp pre-earnings, 1.39 pp quarter-ahead** — and the R-model's own README
    warns that even those are not untouched validation. **1.39 pp at the quarter-ahead origin is the honest
    bar a 2 Oct pitch-date ADR-FX number has to clear.**

---

## 9. Shortest path to the requested model — what to reuse, exactly

| need | reuse |
|---|---|
| Daily FX, PIT-safe | `fx_lag_v2/fx_daily_2026-09-11.csv` (re-fetch with a new `STAMP` for a 2026-09-21 vintage); `05_fred_cache/` for pre-2018 |
| 17-point target | `02_kpi_panel_quarterly.csv:fx_pts_adr`; verbatim quotes in `02_kpi_panel_long.csv`; interval treatment from `fx-engine-validation.md` |
| Spot-held quarterly average + observed share | `fx_lag_v2/pit_fx.py::_q_avg_spot_held` and `basket_yoy_asof` (verbatim; the v2 holiday fix matters) |
| PIT regional weights | `pit_fx.py::regional_shares_asof` + `L0_exact_regional_revenue.csv:knowable_from` (revenue); `adr/01_regional_annual.csv:gbv_share_pct` by year (GBV) |
| Priors for the weight vector | FY-by-FY GBV shares (§4.2) × destination baskets (§3a) as the prior mean; `s_G` regularised to 0.66–0.68, **not** 0.56 |
| Walk-forward harness at 3 origins | `FX-ADR-R-model/run_model.R` + `model_functions.R`; origins, 7-day FX buffer and release-ledger logic already implemented; `outputs/fx_predictions.csv` is the scoring frame |
| Benchmarks to beat | zero 2.42/2.55 pp; repeat-last 2.02/2.32; euro fit 0.45 (day 60) / 1.39 (quarter-ahead); N midpoint 0.41 in-sample |
| Decision dates + conventions | `lane2/CONVENTION.md`; `20_observed_share_triple.csv` (use the **contemporaneous** row for ADR) |
| Hedging | nothing — ADR is unhedged (§5) |
| Registration | FORMAT 1.1, vintage = real run date; parent scores, subagent registers (CONVENTION.md §4) |
