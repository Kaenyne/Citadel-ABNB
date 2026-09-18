# NIGHTS_ENGINE — how the nights engine works, end to end

Companion to `REVIEWS_INDEX_v2.md` (spec, pre-registration, results) and `REVIEWS_INDEX_v2_RATIONALE.md` (why each
number stands). This file is the *how*: inputs → stages → outputs → the workbook, with the formulas. Everything here
re-runs with two commands:

```
cd analysis/src/forecast_methods/reviews_index_v2
python3 run.py --stage all        # ≈15 s: stages A–F, figures, outputs in data/processed/forecast_methods/reviews_index_v2/
python3 workbook.py               # rebuilds model/ABNB_official_model.xlsx from those outputs
python3 -m pytest tests -q        # 9 tests; the first pins the scorer to E5's 0.683209
```

## 1. Inputs (all committed; nothing scraped, nothing fetched at run time)

| input | file | used by |
|---|---|---|
| review counts per market × month × dump vintage (123 markets; Aug 2025 and Aug 2026 files) | `data/processed/q3nowcast/E/market_vintage_monthly.csv` | B, C, D |
| printed nights (levels 1Q21–2Q26) | `data/processed/abnb_driver_history_quarterly.csv` | B, C, E, F |
| observed platform nights by EU country, monthly | `data/processed/eurostat_platform_nights_monthly.csv` | A |
| regional revenue by quarter, ADR index, regional growth buckets | `data/processed/overnight/10_regional_panel_quarterly.csv` | mix weights (v2.1) |
| lead-time kernel (share of a stay quarter's stays booked 0..3 quarters earlier) | `data/processed/forecast_methods/kernel_leadtime_v2/K2_M_matrix.csv` | F |
| 3Q26 quarter-to-date by region (day-matched, same-age two vintages) | `data/processed/q3nowcast/E/vintage_matched_nowcast.csv`, `q3_2026_nowcast.csv` | C3 |
| unearned fees, GBV (reported, ex-FX) | `data/processed/overnight/02_kpi_panel_quarterly.csv` | E |
| base path components, Street, guidance | `final_nights.md` (DEC-0019/0025/0029), Bloomberg MODL (DEC-0005), `02_guidance_ledger.csv` | E, F |

## 2. The pipeline

**Step 1 — same-age counts (`data.py`, `index.py`).** For each market: the latest dump and the dump 300–430 days older.
Drop the two months before each dump (posting lag). For month m: `n_vm_cur` = reviews for m in the latest file;
`n_vm_prior` = reviews for m−12 in the prior file. Same distance from the dump on both sides → delisted-listing losses
cancel. (`yoy_all` = same file both sides, kept as sensitivity; `yoy_mature` = listings ≥12 months old, fails.)

**Step 2 — regional growth (`index.global_quarterly`).** Sum numerators and denominators over a region's markets and
the quarter's three months (markets must have all three): `g_r,t = Σ n_vm_cur / Σ n_vm_prior − 1`.

**Step 3 — stay-quarter mix weights (`mix.py`, v2.1).** `w_r,t = regional revenue_r,t ÷ ADR index_r`, renormalised
(index NA 1.42 / EMEA 0.97 / LatAm 0.68 / APAC 0.59). Regional revenue is check-in-dated, so this is the stay mix by
quarter (EMEA ≈ 51% in Q3, 27% in Q1). Forward: same quarter of the prior year rolled by the drift rule (NA −0.55 pp/qtr,
EMEA +0.10, LatAm +0.33, APAC +0.10).

**Step 4 — the index.** `index_t = Σ_r w_r,t × g_r,t` (percent).

**Step 5 — the mapping (`stages.frozen_mapping`).** `nights y/y_t = a + b × index_t`, a and b by OLS on 1Q23–2Q25 only
(`INTERCEPT` / `SLOPE` in the workbook), frozen. Stays-implied y/y for any quarter = a + b × index.

**Step 6 — scoring (`scoring.py`, E5's function verbatim).** For each scored quarter t: refit a, b on all quarters before t
inside the window; predict; error = prediction − printed; naive error = last quarter's y/y − printed. Ratio =
RMSE(errors) / RMSE(naive). W1: window 1Q22+, scored 1Q23–2Q26; W2: 1Q23+, scored 1Q24–2Q26. Band = RMSE of the W2
errors on the pre-RNPL scored quarters 1Q24–2Q25. Also: moving-block bootstrap interval of the ratio, Diebold–Mariano.

**Step 7 — the gap (Stage C).** For 3Q25–2Q26: `gap_t = printed y/y − (a + b × index_t)` — the option term, observed.

**Step 8 — the 3Q26 read (C3).** Per-region quarter-to-date stays y/y (1 Jul → dump − k days, day-matched vs 364 days
earlier) × 3Q26 weights = composite; + measured partial-to-full gap = full-quarter index; through the frozen mapping →
stays y/y; × 133.6m → level; ± band.

**Step 9 — the option term forward (`final_model.py`).** `print = stays + I`. 3Q26 I ∈ {0, mean gap, max gap}; base
I = mechanism print − stays read. Y/y channel: `I_yoy,t = I_t − I_{t−4}` (what the KPI laps). Level channel: each
writing wave's cancellations land at stay dates through the kernel (cohort gap × normalised kernel share).

**Step 10 — forward path and the view (Stage E/F).** Base y/y per quarter = underlying + fee/cancellation lap + ex-NA
RNPL lap + events (all sourced); level = prior-year level × (1 + y/y); FY sums. Street and guidance beside it.
`P(print ≥ Street) = 1 − Φ((Street y/y − stays read) / band)`. Unearned fees − GBV spread, z against 1Q23–2Q25.

**Validation (Stage A, `panel.py`).** Country × month: log y/y of observed Eurostat nights on log y/y of the country's
review count, country fixed effects, wild-cluster bootstrap over 18 countries; first differences; leave-one-country-out;
era split; per-country expanding walk-forward. This is what licenses "reviews measure stays".

## 3. Outputs

`data/processed/forecast_methods/reviews_index_v2/`: `prereg.json` (frozen), `stage_a_tests.csv`, `panel_*.csv`,
`index_quarterly_v2.csv` (all constructions), `index_regional_vmatch_pct.csv`, `mix_weights_stay_quarter.csv`,
`stage_b_walkforward.csv` + `stage_b_paths.csv` + `stage_b_loco_slopes.csv`, `stage_c_tests.csv` + `stage_c_gap.csv` +
`stage_c_sensitivity_1q23.csv` + `stage_c3_3q26.json`, `stage_d_*.csv`, `stage_e_*.csv`, `final_model_*.csv/json`,
`figures/fig0–fig9`, `RESULTS.json`, `workbook_refs.json`.

## 4. The workbook (`model/ABNB_official_model.xlsx`)

`Nights_Engine` lays the pipeline out cell by cell, 1Q21–4Q27 across the columns: block A printed nights and y/y (formula);
B regional growth (input) × weights (input) → index (`SUMPRODUCT`); C `INTERCEPT`/`SLOPE` on 1Q23–2Q25, stays-implied and
gaps, then the W1, W2 and band walk-forwards row by row (each prediction an `INTERCEPT`/`SLOPE` over the quarters before
it) with RMSE ratios; D the 3Q26 read; E the option term, y/y lap and kernel landing; F the forward path as sums of
components, levels, FY, Street, guidance, `NORMDIST` tail; G unearned fees vs GBV with z; H Stage A statistics as
sourced values; a block of engine reference values the builder checks against. Four native charts read those cells.
`Income_Statement` links its first line to block A (history) and block F (forward); every other line is labelled and
empty until built together. Verified with the `formulas` engine (366 formulas, 0 errors) against the Python run: W1/W2
ratios, band, a, b, 3Q26 read all match within 0.002.

## 5. When the inputs change

September dumps: replace the counted layer, `run.py --stage all`, `workbook.py`; the 2Q26 gap (48% realised at the June
cut) and the 3Q26 quarter-to-date update. A new regional revenue quarter: the mix weights extend by one quarter
automatically. A European RNPL launch: a new writing wave — `final_model.py`'s I path and the ceiling assumption are the
lines to change, and the note must say so.
