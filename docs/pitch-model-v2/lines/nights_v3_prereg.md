# Nights v3 pre-registration — stayed-nights decomposition + backlog identity

Date 2026-09-18. Author: pitch-model-v2 brain session with Theo. Status: registered BEFORE any regression is run. DEC-0033.

## 0. Why

The reviews-index OLS (final_nights.md §3.12) is one slope on one proxy. It was judged not compelling for the competition. This registration replaces it with a mechanism that has two measurable halves and an identity that binds them.

## 1. The identity

Airbnb reports Nights and Experiences Booked in quarter t **net of cancellations that occurred in t**, counted at booking. Stays happen later (mean lead 2.2 months, Little's law on unearned fees, pre-RNPL). Let

- `N(t)`  = reported booked nights, net (disclosed)
- `S(t)`  = nights stayed in t (alt data: reviews, E package)
- `K(t)`  = backlog of booked-not-yet-stayed nights at end of t, net of cancellations (balance sheet: unearned fees ÷ fee share ÷ ADR, plus the RNPL unpaid share)

Then, as an accounting identity: `N(t) = S(t) + K(t) − K(t−1)`.

In y/y growth: `g_N(t) ≈ g_S(t) · S(t−4)/N(t−4) + b(t)`, with `b(t) = [ΔK(t) − ΔK(t−4)] / N(t−4)` in growth points. Since S ≈ N over a full year, `g_N ≈ g_S + β·b` with **β = 1 under the identity**. That restriction is testable.

## 2. Measurement

| object | source in repo | construction |
|---|---|---|
| `g_S` total | `data/processed/q3nowcast/E/index_quarterly.csv`, measure `yoy_vmatch` (vintage-matched, wedge-free) | quarterly, GLOBAL and NAM / EMEA / APAC / LatAm, 1Q16–2Q26 |
| `g_S` same-listing | same file, measure `yoy_cohort` (identical listing set both sides) | as above |
| new-listing contribution | `yoy_vmatch − yoy_cohort`; cross-check with `n_new_listing_cohort / n_listings` from `market_vintage_monthly.csv` | as above |
| partial 3Q26 stays | `partial_vs_full_quarter.csv`, `partial_window_yoy_index.csv`, `q3_2026_coverage.csv` | Jul–Aug (Sep if present) with the package's partial-quarter correction |
| `K_UF` | `data/processed/overnight/02_kpi_panel_quarterly.csv` (`unearned_fees_musd`, ADR, GBV) | `UF / fee_share / ADR`; fee share grid {0.124, 0.133, 0.151, 0.155} from `analysis/src/rnpl_balance_sheet_bridge.py` |
| RNPL unpaid nights `U` | `data/processed/rnpl_short_audit/verify_bs_unpaid_gbv_nights.csv`, bridge output §3 | joint solve on UF and funds-held ratios; grid u × B × ADR ratio; 3Q25–2Q26 |
| `K` | `K_UF + U` | pre-RNPL quarters: `U = 0` |
| 3Q26 backlog scenarios | bridge output §4 score sheet (u 7–15%, m 0–18%) | gives `b(3Q26)` band |

Timing: stays lag bookings. Both contemporaneous (`g_S(t)`) and one-quarter-ahead (`g_S(t+1)`) specifications are run and both are reported. The nowcast uses only stays observed by 18 Sep 2026.

## 3. Windows

W1 = 1Q23–2Q26 (n 14). W2 = 1Q24–2Q26 (n 10). A result must hold on both to be promoted. Naive = last quarter's y/y. Single-index comparator = the published `yoy_all` OLS (ratio to naive 0.837 W1 / 0.683 W2).

## 4. Hypotheses and pass criteria (fixed now)

- **H1 structural (backlog).** In `g_N = a + γ·g_S + β·b`, β is positive and within [0.5, 1.5] with p ≤ 0.10 (HAC) on W1, and positive on W2. Pass → the backlog term is the RNPL quant row of the nights line.
- **H2 decomposition (supply vs demand).** In `g_N = a + γ1·c + γ2·nl (+ β·b)`, both γ1 and γ2 are positive on W1 and W2; walk-forward mean absolute error beats the single-index model on **both** windows. Pass → the decomposition replaces the index as the alt-data core. Beats on one window only → support row.
- **H3 convergence.** The 3Q26 read is reported as a band: observed partial-quarter stays (corrected) + the 3Q26 backlog scenario band. It is compared with the mechanism read 146.8m (+9.89%) and the Street card. No spec is chosen for where it lands.
- **Regional.** Regional `yoy_vmatch` and `yoy_cohort` are checked against regional revenue y/y (`airbnb_regional_revenue_quarterly.csv`, USD, ADR/FX-contaminated, stated) and against the WS10 bucket midpoints. Descriptive only; no promotion on regional evidence alone.

## 5. Falsifiers at the 5 Nov print

Unearned fees and funds held for clients at 3Q26 (bridge §4 score sheet). If reported UF y/y lands outside the scenario band, the backlog half is wrong and the row is withdrawn. If reported nights y/y lands outside the H3 band, the alt-data half is wrong.

## 6. What will not be done

No lag or window chosen after results. No quarter dropped. No spec selected by its 3Q26 output. Every spec listed here is reported, passing or not. Reviews-index OLS is not re-run.

## 7. Outputs

N1 dossier (stays decomposition), N2 dossier (backlog identity), then a joint fit and a convergence table in `final_nights.md` §3.13 with figures.

## 8. Results (filed 18 Sep 2026, after the tests; nothing above this line was changed)

- H1 **fail**: β = 0.080 (SE 0.093, p 0.41) on W1; 0.184 (SE 0.054, p 0.012) on W2; Wald β = 1 rejected on both (t −9.9 and −15.1). Walk-forward with the term: MAE ratio to naive 1.27 (W1) and 1.45 (W2) versus 0.78 and 0.87 without it.
- H2 **fail**: two-component spec MAE ratio 2.99 (W1) and 1.02 (W2) versus the single index 0.90 and 0.76 on identical scored sets (N1).
- H3 delivered: stays-only read 146.0m (W1, July) and 145.8m (W2, July+August), bands 144.8 to 147.2 and 145.1 to 146.5; joint fit 144.6 to 145.5m; identity-imposed 139.7m (not a forecast). Mechanism base 146.8m unchanged.
- Files: dossiers N1, N2; `analysis/src/pitch_model_v2/nights_v3/`; outputs `data/processed/pitch_model_v2/nights_v3/N1..N3/`; receipts N1, N2, N3; `final_nights.md` §3.13; figure `figures/nights_v3_identity.png`.
