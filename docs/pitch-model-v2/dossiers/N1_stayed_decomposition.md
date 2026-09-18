# N1 — stayed nights from alt data: same-listing vs new-listing decomposition

## 1. Header
- Line: N1 · Judge's question: "How much of Airbnb's reported nights growth is new supply versus demand on existing listings, and does that split predict reported nights on both point-in-time windows?"
- Digger: opus · Date: 2026-09-18 · Commit: d7fba07 (branch `theo/pitch-model-v2`)

**One-sentence answer to the judge.** On the Inside Airbnb review panel, *all* of measured stays growth is new listings and then some — 2Q26 total stays +4.27% y/y is a same-listing leg of **−7.12%** plus a new-listing leg of **+11.39pp**, and the partial 3Q26 (July, 108 markets) reads −5.66% / +11.26pp / +5.60% after the package's own partial-quarter correction — but the split **does not** predict reported nights: on the pre-registered walk-forward it loses to the single index on **both** windows (W1 mean-absolute-error ratio to naive 2.99 vs the index's 0.90; W2 1.02 vs 0.76), and the same-listing leg is negative in every quarter since 2Q23 while reported nights grew 7–12%, which is listing-ageing arithmetic as much as demand.

## 2. The number

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 2Q26 | -7.12 | | | pct same-listing stays y/y (c) | Inside Airbnb dumps to 31 Aug 2026, E4 `yoy_cohort`, `w_reviews`, GLOBAL |
| base | 2Q26 | 11.39 | | | pp new-listing contribution (nl) | same, `yoy_vmatch` − `yoy_cohort` |
| base | 2Q26 | 4.27 | | | pct total stays y/y (v) | same, `yoy_vmatch` |
| base | 3Q26 | -5.66 | -8.04 | -3.27 | pct same-listing stays y/y (c), partial corrected | July 2026, 108 markets, + measured July→Q3 gap (sd 2.39pp) |
| base | 3Q26 | 11.26 | 10.84 | 11.67 | pp new-listing contribution (nl), partial corrected | same (gap sd 0.42pp) |
| base | 3Q26 | 5.60 | 2.82 | 8.38 | pct total stays y/y (v), partial corrected | same (gap sd 2.78pp) |
| base | 3Q26 | 9.28 | 9.20 | 9.28 | pct fitted reported nights y/y, spec a | OLS g_N on v; low = W2 fit, high = W1 fit |
| base | 3Q26 | 10.04 | 10.04 | 10.20 | pct fitted reported nights y/y, spec b | OLS g_N on c and nl; low = W1 fit, high = W2 fit |

**Observed months and coverage for the partial 3Q26** (`partial_3q26_coverage.csv`). July 2026 is complete in every dump taken on or after 14 Aug 2026 — the posting-completeness curve is flat from k = 14 days — so July is the primary basis, on the 108 of 123 markets that have both a settled July 2026 and a dump 300–430 days older for the vintage-matched leg. August 2026 is observed only to each market's scrape date less 14 days: median 14 Aug, max 17 Aug. September 2026 is not observed at all. So the widest basis here sees roughly the first 45 of the quarter's 92 days (about 49%), and the cohort split — which needs monthly maturity counts, not daily counts — can be read for July only. The next Inside Airbnb batch (WP-K) is what closes this.

Low/high on the three partial rows are ± the year-to-year standard deviation of the measured July→full-quarter gap (three years: 2023, 2024, 2025); they are gap uncertainty only and carry no model error. Low/high on the two fitted rows are the W1 and W2 fits of the same spec, not a predictive interval — the walk-forward errors in §6 are the honest dispersion and they are larger.

Reference points, not N1 outputs: reported nights y/y 2Q26 = **+10.342%** (computed from unrounded `nights_m` 148.3 / 134.4, never from `nights_m_yoy_pct`); the published single-index read for 3Q26 re-fitted here is +9.91% (W1) / +9.55% (W2); the committed memo line is +9.5% / 146.3m (D1, DEC-0004).

**Reproduced vs inherited.** Reproduced on this machine at this commit: every cell above; the whole 1Q23–2Q26 series for five geographies; the regressions and their HAC(3) statistics; the walk-forward; and — as a protocol check — the published single-index RMSE ratios 0.837125 (W1) and 0.683209 (W2) to within 7e-6 and 6.5e-5. Inherited, not re-derived here: the Inside Airbnb counting layer itself (E1–E4 on Krish's raw capture), the WS10 regional bucket midpoints, and the 149.0m Bloomberg MODL nights bar.

### 2a. Model inputs (machine-readable)

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| stays_same_listing_yoy_pct | base | 2Q26 | -7.12 | pct | c = E4 yoy_cohort w_reviews GLOBAL |
| stays_new_listing_contrib_pp | base | 2Q26 | 11.39 | pp | nl = v minus c |
| stays_total_yoy_pct | base | 2Q26 | 4.27 | pct | v = E4 yoy_vmatch w_reviews GLOBAL |
| stays_same_listing_yoy_pct_observed | base | 3Q26 | -6.58 | pct | July 2026 only; 108 markets; no correction applied |
| stays_new_listing_contrib_pp_observed | base | 3Q26 | 11.41 | pp | July 2026 only; 108 markets; no correction applied |
| stays_total_yoy_pct_observed | base | 3Q26 | 4.83 | pct | July 2026 only; 108 markets; no correction applied |
| stays_same_listing_yoy_pct_corrected | base | 3Q26 | -5.66 | pct | July 2026 plus measured July-to-Q3 gap +0.93pp |
| stays_new_listing_contrib_pp_corrected | base | 3Q26 | 11.26 | pp | July 2026 plus measured July-to-Q3 gap -0.16pp |
| stays_total_yoy_pct_corrected | base | 3Q26 | 5.60 | pct | July 2026 plus measured July-to-Q3 gap +0.77pp |
| stays_total_yoy_pct_corrected_e6basis | base | 3Q26 | 5.30 | pct | E6 day-matched Jul plus Aug-to-date window; 119 markets |
| fitted_nights_yoy_pct | base | 3Q26 | 9.28 | pct | spec a g_N on v alone fitted on W1 |
| fitted_nights_yoy_pct | base | 3Q26 | 9.20 | pct | spec a g_N on v alone fitted on W2 |
| fitted_nights_yoy_pct | base | 3Q26 | 9.19 | pct | spec a fitted on W1 read off the E6 day-matched basis |
| fitted_nights_yoy_pct | base | 3Q26 | 9.14 | pct | spec a fitted on W2 read off the E6 day-matched basis |
| fitted_nights_yoy_pct | base | 3Q26 | 10.04 | pct | spec b g_N on c and nl fitted on W1 |
| fitted_nights_yoy_pct | base | 3Q26 | 10.20 | pct | spec b g_N on c and nl fitted on W2 |
| fitted_nights_yoy_pct | base | 3Q26 | na | pct | spec c one-quarter-ahead timing with 2Q26 included - no 3Q26 read exists because it would need 4Q26 stays |
| fitted_nights_yoy_pct | base | 3Q26 | na | pct | spec c one-quarter-ahead timing with 2Q26 dropped - no 3Q26 read exists because it would need 4Q26 stays |
| fitted_nights_yoy_pct | base | 3Q26 | 9.91 | pct | reference spec single index g_N on yoy_all fitted on W1 |
| fitted_nights_yoy_pct | base | 3Q26 | 9.55 | pct | reference spec single index g_N on yoy_all fitted on W2 |

## 3. Derivation chain
1. Inside Airbnb monthly review dumps, 123 markets, 363 market-vintages, review dates to 31 Aug 2026 — raw store outside the repo (`~/abnb_ia_capture/`, Krish's capture); the counted layer is what this line reads →
2. `data/processed/q3nowcast/E/market_vintage_monthly.csv` (49,243 rows), `market_vintage_daily.csv`, `market_geo.csv` →
3. `analysis/src/q3nowcast/E4_build_index.py` → `data/processed/q3nowcast/E/index_quarterly.csv` (measures `yoy_cohort`, `yoy_vmatch`, `yoy_all`; column `w_reviews`); `analysis/src/q3nowcast/E6_nowcast.py` → `vintage_matched_nowcast.csv`, `partial_vs_full_quarter.csv`, `q3_2026_coverage.csv` →
4. `analysis/src/pitch_model_v2/nights_v3/n1_stayed/run.py` →
   - `data/processed/pitch_model_v2/nights_v3/N1/series_quarterly.csv`, rows `region=GLOBAL`: columns `c_pct`, `nl_pct`, `v_pct`, `a_pct`, `new_share_pct`; row `quarter=2Q26` = −7.119 / 11.389 / 4.270 / 25.023 / 5.172
   - `partial_3q26.csv`, rows `basis=jul_only_monthly, region=GLOBAL`: `observed_pct` and `corrected_pct` for c, v, nl, a
   - `regressions.csv`, `walkforward.csv`, `walkforward_paths.csv`, `reads_3q26.csv`
   - `regional_revenue_regressions.csv`, `regional_vs_ws10.csv`
5. Target: `data/processed/abnb_driver_history_quarterly.csv`, column `nights_m` (levels), y/y computed in the script — 2Q26 = 148.3 / 134.4 − 1 = **+10.3423%**.

The panel is a **stay-date review-count** series. It is not a nights measurement; the mapping onto a booking-date KPI is an OLS slope, and that mapping is where any forecast content lives.

## 4. Governing sources
| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-18 | `docs/pitch-model-v2/lines/nights_v3_prereg.md` (DEC-0033) | H2: both γ1 and γ2 positive on W1 and W2 **and** walk-forward MAE beats the single index on both windows; every spec reported; no spec chosen by its 3Q26 output | **governs** this line entirely |
| 2026-09-12 | `analysis/src/q3nowcast/E4_build_index.py` docstring | definitions of `yoy_all`, `yoy_mature`, `yoy_cohort`, `yoy_vmatch` | governs — used unchanged |
| 2026-09-12 | `analysis/src/q3nowcast/E5_backtest.py` §protocol | expanding-window walk-forward, naive = previous quarter, W1 trains from 1Q22 / scores 1Q23+, W2 trains from 1Q23 / scores 1Q24+ | governs — reused, with the `k+3` minimum-training deviation stated in §8 |
| 2026-09-12 | `data/processed/q3nowcast/E/backtest_abnb_quarterly.csv` | single-index (`GLOBAL\|yoy_all\|w_reviews`) RMSE ratio to naive 0.837125 (W1, n 14) / 0.683209 (W2, n 10) | governs as the comparator; reproduced here to 7e-6 / 6.5e-5 |
| 2026-09-14 | `05_backtests/WPK_reviews-index-2023-vintage.md`, `SR_QUARTER_SUBMISSION_READINESS_v1.md` §Reviews revalidation | the 0.683 comparator is W2-only and its 1Q23–4Q23 training quarters were read from a stale vintage; re-vintaged it is 0.757 honest / 0.841 literal | **qualifies** the comparator — N1's "beats the index" test is therefore against a comparator that is itself flattered; the failure in §6 is not softened by it |
| 2026-09-18 | `docs/pitch-model-v2/dossiers/D1_d1_nights_3q26.md` | committed nights line +9.5% / 146.3m is the index read bias-corrected on its own walk-forward | not superseded by N1; N1 produces no competing committed number |
| 2026-09-06 | `data/processed/overnight/10_regional_forecast.csv` (WS10) | 3Q26 regional nights bucket midpoints, base NAM 7.0 / EMEA 8.0 / LatAm 18.0 / APAC 17.0 | governs the regional comparison table (descriptive) |

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/N1/receipt.json`
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id N1 --watch data/processed/pitch_model_v2/nights_v3/N1 --cmd "python3 analysis/src/pitch_model_v2/nights_v3/n1_stayed/run.py"` · Exit: 0 · Wall: 1.2 s · Interpreter: python3 (3.13, pandas 3.0.0, statsmodels 0.14.6)
- The wrapper restored the tree (9 new files listed and removed); `run.py` was then run once directly, exit 0, so the outputs persist.
- Output: `data/processed/pitch_model_v2/nights_v3/N1/walkforward.csv` cell `rmse_ratio, row spec=ref_single_index window=W2` = **0.683144** · Committed value: **0.683209** (`backtest_abnb_quarterly.csv`, feature `GLOBAL|yoy_all|w_reviews`, lag 0, level, target nights_yoy, window 2023Q1+) · Tolerance: ±0.001 · **Match: yes**
- Second cell: same file, `window=W1` = **0.837118** vs committed **0.837125**, tolerance ±0.001, match yes. The residual 7e-6 / 6.5e-5 is the only intended difference: E5 regresses on the rounded `nights_m_yoy_pct` column, N1 on y/y computed from unrounded `nights_m` levels, as the brief requires.
- Third cell: `series_quarterly.csv` row `region=GLOBAL, quarter=2Q26` `v_pct` = **4.26992** vs `index_quarterly.csv` `measure=yoy_vmatch, region=GLOBAL, w_reviews` = **0.0426992**, tolerance ±1e-6, match yes.

## 6. Test record

Pre-registered criteria are prereg §4 H2. "This line" is the walk-forward mean-absolute-error ratio to naive; the single-index column is that same statistic recomputed on the **identical scored set** (so it is comparable even where the two-regressor specs score one quarter fewer).

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 | 14 | H2 sign: γ1 (c) and γ2 (nl) both positive | +0.3704 and +0.1511 | n/a | n/a | n/a | both positive on W1 and W2 | **pass** |
| W2 | 10 | H2 sign: γ1 (c) and γ2 (nl) both positive | +0.4184 and +0.1088 | n/a | n/a | n/a | both positive on W1 and W2 | **pass** |
| W1 | 13 scored | spec b walk-forward MAE ratio to naive | **2.990** | 1.000 | n/a | n/a | beat the single index (0.903 on this set) | **fail** |
| W2 | 9 scored | spec b walk-forward MAE ratio to naive | **1.019** | 1.000 | n/a | n/a | beat the single index (0.760 on this set) | **fail** |
| W1 | 14 scored | spec a (v alone) walk-forward MAE ratio | 0.823 | 1.000 | n/a | n/a | not a pre-registered promotion spec | beats the index (0.958) — reported, not promoted |
| W2 | 10 scored | spec a (v alone) walk-forward MAE ratio | 0.723 | 1.000 | n/a | n/a | same | beats the index (0.765) — reported, not promoted |
| W1 | 13 scored | spec c_incl (t+1 timing) walk-forward MAE ratio | 0.641 | 1.000 | n/a | n/a | same | beats the index (0.903) but is not point-in-time usable |
| W2 | 9 scored | spec c_incl (t+1 timing) walk-forward MAE ratio | 1.018 | 1.000 | n/a | n/a | same | **fail** on W2, so it fails the two-window rule anyway |

Regression detail (HAC(3); coefficient, t, p, R², leave-one-out slope range across the window):

| spec | window | n | term | coef | SE | t | p | R² | LOO slope range |
|---|---|---|---|---|---|---|---|---|---|
| a: g_N(t) on v(t) | W1 | 14 | v | 0.3222 | 0.0201 | 16.06 | <0.001 | 0.745 | 0.248 to 0.351 |
| a | W2 | 10 | v | 0.1911 | 0.1520 | 1.26 | 0.209 | 0.102 | 0.130 to 0.411 |
| b: g_N(t) on c(t), nl(t) | W1 | 14 | c | 0.3704 | 0.0267 | 13.86 | <0.001 | 0.760 | 0.300 to 0.400 |
| b | W1 | 14 | nl | 0.1511 | 0.1084 | 1.39 | 0.163 | 0.760 | 0.082 to 0.253 |
| b | W2 | 10 | c | 0.4184 | 0.0912 | 4.59 | <0.001 | 0.184 | 0.320 to 0.568 |
| b | W2 | 10 | nl | 0.1088 | 0.1446 | 0.75 | 0.452 | 0.184 | 0.012 to 0.309 |
| c_incl: g_N(t) on c(t+1), nl(t+1) | W1 | 14 | c(t+1) | 0.6495 | 0.1586 | 4.09 | <0.001 | 0.733 | 0.349 to 0.845 |
| c_incl | W1 | 14 | nl(t+1) | 0.4915 | 0.0753 | 6.52 | <0.001 | 0.733 | 0.429 to 0.538 |
| c_incl | W2 | 10 | c(t+1) | 0.0113 | 0.3879 | 0.03 | 0.977 | 0.006 | −0.343 to 0.676 |
| c_incl | W2 | 10 | nl(t+1) | 0.0655 | 0.2650 | 0.25 | 0.805 | 0.006 | −0.262 to 0.330 |
| c_drop (2Q26 dropped) | W1 | 13 | c(t+1) | 0.6270 | 0.1768 | 3.55 | <0.001 | 0.736 | 0.253 to 0.828 |
| c_drop | W1 | 13 | nl(t+1) | 0.5380 | 0.0966 | 5.57 | <0.001 | 0.736 | 0.477 to 0.597 |
| c_drop | W2 | 9 | c(t+1) | −0.1751 | 0.4580 | −0.38 | 0.702 | 0.095 | −0.499 to 0.568 |
| c_drop | W2 | 9 | nl(t+1) | 0.1510 | 0.2743 | 0.55 | 0.582 | 0.095 | −0.169 to 0.354 |
| reference: g_N(t) on yoy_all(t) | W1 | 14 | yoy_all | 0.3222 | 0.0147 | 21.94 | <0.001 | 0.743 | 0.261 to 0.341 |
| reference | W2 | 10 | yoy_all | 0.2197 | 0.1082 | 2.03 | 0.042 | 0.174 | 0.174 to 0.366 |

Walk-forward detail (E5 protocol; MAE and RMSE, both as ratios to naive; jackknife = the MAE ratio recomputed dropping one scored quarter at a time):

| spec | window | scored | MAE ratio | RMSE ratio | jackknife MAE ratio range | single index, same scored set (MAE / RMSE) |
|---|---|---|---|---|---|---|
| a: v alone | W1 | 14 (1Q23–2Q26) | 0.823 | 0.754 | 0.769 to 0.906 | 0.958 / 0.837 |
| a: v alone | W2 | 10 (1Q24–2Q26) | 0.723 | 0.682 | 0.662 to 0.916 | 0.765 / 0.683 |
| b: c + nl | W1 | 13 (2Q23–2Q26) | **2.990** | 5.148 | 1.508 to 3.415 | 0.903 / 0.797 |
| b: c + nl | W2 | 9 (2Q24–2Q26) | **1.019** | 0.858 | 0.849 to 1.280 | 0.760 / 0.664 |
| c_incl: c,nl at t+1 | W1 | 13 | 0.641 | 0.693 | 0.537 to 0.699 | 0.903 / 0.797 |
| c_incl | W2 | 9 | 1.018 | 1.068 | 0.834 to 1.213 | 0.760 / 0.664 |
| c_drop | W1 | 12 (2Q23–1Q26) | 0.615 | 0.684 | 0.502 to 0.674 | 0.931 / 0.801 |
| c_drop | W2 | 8 (2Q24–1Q26) | 1.051 | 1.080 | 0.858 to 1.292 | 0.766 / 0.663 |
| reference single index | W1 | 14 | 0.958 | 0.837 | 0.885 to 1.041 | — |
| reference single index | W2 | 10 | 0.765 | 0.683 | 0.674 to 0.934 | — |

Regional, descriptive only — **USD revenue is ADR- and FX-contaminated and is not a nights series**; these are not nights tests and nothing is promoted on them. Regional revenue y/y on regional v (W1 = 4Q23–2Q26 n 11, the first quarter a y/y exists for; W2 = 1Q24–2Q26 n 10): NAM slope 0.98 (t 4.59) / 0.98 (t 4.45), R² 0.54; EMEA 0.59 (t 3.03) / 0.39 (t 1.38), R² 0.14 / 0.03; LatAm 0.45 (t 2.18) / 0.30 (t 1.39), R² 0.16 / 0.05; APAC 0.74 (t 9.35) / 0.71 (t 6.81), R² 0.65 / 0.58. Split into c and nl the signs stop agreeing across regions — NAM nl +1.56 (t 3.78), EMEA nl +0.10 (t 0.26), LatAm c −0.01 (t −0.08), APAC nl **−0.24** (t −1.70) — which is the regional restatement of the same failure.

Regional stays vs the WS10 3Q26 bucket midpoints (`regional_vs_ws10.csv`):

| region | c 2Q26 | nl 2Q26 | v 2Q26 | c Jul-26 | nl Jul-26 | v Jul-26 | WS10 3Q26 bear / base / bull |
|---|---|---|---|---|---|---|---|
| NAM | −4.35 | 11.25 | 6.90 | −4.62 | 11.95 | 7.34 | 5.0 / 7.0 / 9.0 |
| EMEA | −6.97 | 8.45 | 1.48 | −6.79 | 8.47 | 1.68 | 6.0 / 8.0 / 10.0 |
| APAC | −11.14 | 13.44 | 2.30 | −11.23 | 17.17 | 5.94 | 14.0 / 17.0 / 19.0 |
| LatAm | −9.70 | 30.10 | 20.40 | −5.92 | 27.24 | 21.33 | 15.0 / 18.0 / 21.0 |

NAM and LatAm sit inside or above their WS10 buckets; EMEA (+1.7 vs a 6–10 bucket) and APAC (+5.9 vs 14–19) sit far below them. Either the review panel under-covers those two regions' growth or WS10's EMEA and APAC buckets are too high; N1 cannot tell which, and the panel's regional composition (57 EMEA markets, 17 APAC, 42 NAM, 7 LatAm) makes the first at least as likely.

**Strongest known failure: the decomposition loses to the one-variable index it was meant to replace on the pre-registered walk-forward on *both* windows (spec b mean-absolute-error ratio to naive 2.990 on W1 and 1.019 on W2, against the index's 0.903 and 0.760 on the identical scored sets), and the failure is not one bad quarter — dropping the worst scored quarter still leaves the W1 ratio at 1.508.**

## 7. Kill list and consistency
- Kill-list check (AGENT_BRIEF §6): **"the 120-market panel as a nights measurement" applies directly to this line and is respected** — every number here is a review-count stays proxy on a 123-market panel, labelled as such in §2, §3 and every output file; nothing in this dossier calls it a nights measurement. No other kill-list item is touched: no −3.4pp FX step, no "82% determined", no +4.05% fee uplift, no drift rule, no restated unearned fees, no FY27 level, no September consensus on a historical date, no M5, no Stan.
- Comparator caveat carried, not buried: the 0.837 / 0.683 single-index ratios are the *published* ones and are reproduced here, but WPK-A showed the W2 figure is flattered by stale training vintages (0.757 honest / 0.841 literal re-vintaged). N1's verdict does not depend on which version is used — spec b loses to both.
- Conflicts: none with D1's committed +9.5% / 146.3m. N1 produces no competing committed number; its spec-a read (+9.2 to +9.3%) happens to sit close to D1's line and its spec-b read (+10.0 to +10.2%) close to the raw index read, and neither is offered as a replacement because both fail the promotion test. N1 does **not** address prereg H1 (the backlog term) — that is N2's object, and until N2 lands the identity `g_N ≈ g_S + β·b` is only half tested here.
- Consistency with the prereg: no lag, window, weighting or market set was chosen after seeing a result; all five specs are reported; the two partial-quarter bases are both reported.

## 8. Open choices
1. **Does N1 enter the memo, and as what?** Options: (a) drop it; (b) one descriptive sentence — "on the review panel, all of stays growth is new listings; demand on the existing listing base is not growing" — with the ageing caveat attached; (c) a support row beside the index. Recommendation: **(b)**. The prereg only allows a support row if the decomposition beats the index on at least one window, and it beats on neither; but the descriptive split is reproduced, is the direct answer to the judge's question, and is the most quotable bear fact in the nights line.
2. **Walk-forward training start on W1.** Options: (a) E5's 1Q22 (used here); (b) 1Q23, which would cut training to three points at the first scored quarter and is not viable; (c) report W1 only from 2Q23 onward. Recommendation: **(a)**, and say plainly that spec b's W1 blow-up is driven by fitting a two-regressor model across the 2022 reopening base — that *is* the result, because the naive and the index face the same 2022 and survive it.
3. **Minimum training count in the walk-forward.** Options: (a) E5's literal 4 for every spec (4 observations, 3 parameters); (b) `k + 3` as used here, costing one scored quarter per window. Recommendation: **(b)**; under (a) spec b's W1 MAE ratio is 3.01 rather than 2.99, so the verdict is unchanged either way, which is worth stating.
4. **Which partial-3Q26 basis feeds any downstream read.** Options: (a) July-only monthly, 108 markets — the only basis that can be split into c and nl; (b) E6's day-matched Jul + Aug-to-date, 119 markets and more of the quarter but no split; (c) both, as here. Recommendation: **(c)** for the dossier and **(b)** for any total-stays number, because it covers six more weeks and its gap correction is an order of magnitude tighter (sd 0.22pp vs 2.78pp).
5. **Whether spec c is shown at all.** Options: (a) show it — it has the best W1 walk-forward in the table (0.641) and the largest, most significant coefficients; (b) drop it as not point-in-time usable (a quarter's nights print about five weeks into t+1, when t+1's stays are a third observed, and it can never produce a 3Q26 read); (c) show it only as a lead-structure diagnostic. Recommendation: **(c)** — and never in a slide where 0.641 can be read as a forecast.
6. **Weighting.** Options: (a) `w_reviews` (count-weighted, used here and by the published index); (b) `w_equal`; (c) `GLOBAL_NW`, the FY25 nights-share weighting. Recommendation: **(a)** for consistency with the comparator, with (c) reported in `series_quarterly.csv`'s equal-weighted columns for anyone who wants the regional-weight version.
7. **Whether the listing-ageing wedge should be removed from c before the split is quoted.** Options: (a) leave it, quote only changes in the split (recommended); (b) de-trend c on listing age. (b) would be a specification chosen after seeing results, which prereg §6 forbids for this round; it is a legitimate object for a *new* pre-registration.

## 9. Judge Q&A
1. Q: Airbnb reported +10.3% nights in 2Q26 and your panel says existing listings shrank 7%. Which is wrong? A: Neither, and that is the point. The panel counts reviews at stay date on a fixed birth cohort, and a listing's review rate decays with age, so the cohort leg carries a mechanical drift — it has sat about 16.6pp below reported nights y/y on average since 1Q23, with a standard deviation of only 4.1pp. The level of the split is not identified; what is informative is that the new-listing contribution has fallen from +18.9pp in 1Q23 to +11.4pp in 2Q26 while the same-listing leg has improved only from −11.2pp (1Q25) to −7.1pp. Growth is coming from supply, and that engine is decelerating.
2. Q: Then why does the split fail to predict reported nights? A: Because the two legs are not independent — they correlate 0.53, both are dominated by the same 2022–23 reopening decay, and splitting one index into two collinear pieces costs a degree of freedom without adding information. In the regression the same-listing leg carries almost all of it (t 13.9 on W1, 4.6 on W2) while the new-listing leg is insignificant on both windows (t 1.39 and 0.75), and out of sample the two-regressor fit is unstable enough to lose to naive on W1 by a factor of three.
3. Q: What would change your mind before 5 Nov? A: Two things. First, N2's backlog leg: if `β` lands in [0.5, 1.5] with p ≤ 0.10, the identity holds and the stays half gains a partner that could stabilise it. Second, the September Inside Airbnb batch (WP-K): it would make 3Q26 a nearly complete stay quarter instead of a five-week partial, which would cut the July→quarter gap uncertainty of ±2.4 to ±2.8pp that currently dominates the partial read and would let the cohort split be measured on August as well as July.
4. Q: Your 3Q26 fitted reads are +9.2% to +10.2% and the Street bar is 149.0m, about +11.5%. Is that your call? A: No. N1 is not a committed number — none of its specs passed, so it does not get to move the card. The memo's line stays D1's +9.5% / 146.3m. What N1 adds is that every specification it ran, including the one that reproduces the published index, reads *below* +11.5%, and that the reason is compositional: the new-supply leg that has carried stays growth is smaller in 2Q26 and July 2026 than in any quarter since 1Q23.

## 10. Grade
Grade: B — reproduced end to end (exit 0, receipt at commit d7fba07, and the published single-index walk-forward ratios reproduced to 7e-6 / 6.5e-5), and the decomposition itself is a clean, quotable descriptive answer to the judge's question on both windows; but the pre-registered H2 promotion test fails on both windows — the split loses to the one-variable index it was meant to replace — so this is a descriptive line, not the alt-data core, and it may not be quoted as a forecast.
