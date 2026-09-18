# N1 — stayed nights: same-listing vs new-listing decomposition

Line N1 of the pitch-model-v2 nights line. Governed by `docs/pitch-model-v2/lines/nights_v3_prereg.md`
(DEC-0033), which was registered before any regression here was run and may not be changed by this
package. Dossier: `docs/pitch-model-v2/dossiers/N1_stayed_decomposition.md`.

**Judge's question.** How much of Airbnb's reported nights growth is new supply versus demand on
existing listings, and does that split predict reported nights on both point-in-time windows?

## Run

```bash
python3 analysis/src/pitch_model_v2/nights_v3/n1_stayed/run.py
```

Reproduction receipt (the wrapper restores the tree, so run the line above once more afterwards so
the outputs persist):

```bash
PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id N1 \
  --watch data/processed/pitch_model_v2/nights_v3/N1 \
  --cmd "python3 analysis/src/pitch_model_v2/nights_v3/n1_stayed/run.py"
```

Interpreter: system `python3` (pandas 3.0.0, statsmodels 0.14.6, numpy 2.4.2). Nothing here needs
`.venv-pd2`. Wall time about 20 s. Exit 0.

## Inputs (all read-only, already on disk; no downloads)

| path | what is taken |
|---|---|
| `data/processed/q3nowcast/E/index_quarterly.csv` | `yoy_cohort`, `yoy_vmatch`, `yoy_all`, `w_reviews` and `w_equal`, GLOBAL + NAM/EMEA/APAC/LatAm |
| `data/processed/q3nowcast/E/market_vintage_monthly.csv` | monthly maturity counts for the July-2026 partial read and `n_new_listing_cohort / n_listings` |
| `data/processed/q3nowcast/E/market_geo.csv` | market → region |
| `data/processed/q3nowcast/E/vintage_matched_nowcast.csv` | E6 day-matched Jul+Aug-to-date vintage-matched read |
| `data/processed/q3nowcast/E/partial_vs_full_quarter.csv` | E6 partial→full-quarter gap for the day-matched basis |
| `data/processed/q3nowcast/E/q3_2026_coverage.csv` | August 2026 coverage dates |
| `data/processed/abnb_driver_history_quarterly.csv` | `nights_m` levels; g_N is computed from the levels, never from `nights_m_yoy_pct` |
| `data/processed/airbnb_regional_revenue_quarterly.csv` | regional revenue, USD (ADR- and FX-contaminated) |
| `data/processed/overnight/10_regional_forecast.csv` | WS10 regional nights bucket midpoints, 3Q26 bear/base/bull |

## Outputs — `data/processed/pitch_model_v2/nights_v3/N1/`

| file | contents |
|---|---|
| `series_quarterly.csv` | 1Q23–2Q26, five geographies: `c_pct` (same-listing), `v_pct` (vintage-matched total), `nl_pct = v − c` (new-listing contribution), `a_pct` (raw `yoy_all`), `new_share_pct` and its y/y in points, equal-weighted variants, market counts |
| `partial_3q26.csv` | partial-3Q26 reads on two bases with the gap correction and its dispersion |
| `partial_3q26_coverage.csv` | markets, August coverage dates, settle-days trim |
| `regressions.csv` | specs a / b / c_incl / c_drop / single-index reference × W1, W2: coefficient, HAC(3) SE, t, p, R², leave-one-out slope range |
| `walkforward.csv` | expanding-window one-step-ahead MAE and RMSE, ratios to naive, jackknife ratio range, single-index comparator on the identical scored set, published comparator |
| `walkforward_paths.csv` | per-quarter walk-forward errors for each spec and window |
| `reads_3q26.csv` | the fitted g_N read for 3Q26 from each spec and window |
| `regional_revenue_regressions.csv` | regional USD revenue y/y on regional v, and on c and nl — descriptive only |
| `regional_vs_ws10.csv` | regional c, nl, v for 2Q26 and July 2026 next to the WS10 3Q26 bucket midpoints |

## Method notes, in the order they matter

1. **Definitions are E4's, unchanged.** `c = n_mature24[m] / n_mature12[m−12] − 1` fixes the listing
   set by birth date on both sides. `v = n[m]` in the latest dump over `n[m−12]` in a dump 300–430
   days older; because the two dumps are about 12 months apart and the two months are exactly 12
   months apart, both sides sit the same distance from their own scrape for every month in the
   history, not only for the newest one. `nl = v − c`.
2. **`c` is not a clean demand measure.** A listing's review rate decays with age, so holding the
   birth cohort fixed builds a downward drift into `c` and the mirror-image upward drift into `nl`.
   Over 1Q23–2Q26 `c` sits 16.6pp below reported nights y/y on average (sd 4.1pp). The *level* of the
   split is therefore not identified; only its movement is informative. This is stated in the dossier
   and is the reason the line is descriptive.
3. **Partial 3Q26.** July 2026 is complete in every dump taken on or after 14 Aug 2026 (the E6
   posting-completeness curve is flat from k = 14 days), so the primary partial basis is July only,
   on the 108 markets that have both a settled July 2026 and a year-ago dump. August 2026 is
   truncated at each scrape date and the maturity counts are monthly, so **no cohort split of August
   is possible**; the E6 day-matched Jul-1→(dump − 14 d) window is carried as a second basis for `v`
   and `a` only. September 2026 is not observed. The July→full-quarter gap is measured on the same
   market set in 2023, 2024 and 2025 and added; its year-to-year sd (2.4–2.8pp) is carried, not hidden.
4. **Walk-forward is E5's protocol.** Expanding window, OLS refit on data strictly before the scored
   quarter, naive = previous quarter's y/y, W1 trains from 1Q22 and scores 1Q23–2Q26, W2 trains from
   1Q23 and scores 1Q24–2Q26. One deviation: E5's minimum training count of 4 becomes `k + 3`, so a
   two-regressor spec is never fitted on 4 observations with 3 parameters. Two-regressor specs
   therefore score 13 (W1) and 9 (W2) quarters instead of 14 and 10, and the naive **and** the
   single-index comparator are recomputed on the identical scored set so every ratio is comparable.
5. **Spec c cannot produce a 3Q26 read.** The brief's timing spec regresses g_N(t) on stays at t+1;
   a 3Q26 read would need 4Q26 stays. It is reported as a structural-timing diagnostic, with and
   without the 2Q26 point whose t+1 is the partial 3Q26, and it is flagged as not point-in-time
   usable (a quarter's nights print about five weeks into t+1, when t+1's stays are a third done).
6. **Nothing is chosen by its 3Q26 output.** Every spec in the brief is reported, passing or not.
