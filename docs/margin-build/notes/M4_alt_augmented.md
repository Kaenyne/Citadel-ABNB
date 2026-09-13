# M4. Alt-data-augmented line model: does any external signal add to the driver model?

Margin build run, 13-14 Sep 2026. Slug `M4_alt_augmented`. Registry method `alt-augmented`. Script
`analysis/src/margin_build/M4_alt_augmented/run.py` (`py -3.13`, exit 0). Author: agent M4.

## 0. Pre-registration (written 2026-09-14 before any fit; nothing below section 0 existed at that time)

**Base model.** M1's `b_elastic_rw` line model, imported from `analysis/src/margin_build/M1_driver_lines/run.py` (not copied), so the
`none` spec here is M1 code: `d4 log L_q = g_L + b_L d4 log D_q + e_q`, D = GBV (cor), nights (ops), revenue (sm), none (pd, ga);
recency weights half-life 4 quarters; y/y observations from 1Q22; PIT drivers from the frozen revenue leg; adj EBITDA = revenue - lines + other_net.

**Augmentation.** One signal at a time on ONE line: `d4 log L_q = g + b d4 log D_q + c x_{q-lead} + e`, where x is the signal's y/y change
(log y/y for levels; the y/y % for the LSEG peer series; the d4 of a step dummy). Strict point-in-time: an observation enters the fit, and the
signal term enters a forecast, only if WS04's `knowable_from` for the signal at quarter q-lead is `<= vintage_date`; otherwise the term is 0
(the spec reverts to M1 for that quarter) and the row is flagged. Because the harness's h=0 is the quarter *being guided* (the vintage falls
32-49 days into it), a lead-0 quarterly signal is never knowable at h=0; the WS04 contemporaneous finding can only enter through a
quarter-to-date construction. So the leads tested are 1 and 2 for quarterly series; 0 and 1 for step dummies (a step announced before the
vintage is known for every later quarter); and 0 for one new series built here: `trends_qtd4_share_{us,ww}` = Airbnb's share of category
search over the FIRST FOUR WEEKS of the quarter (same P1_peers stitched weekly values WS04 used, `data/processed/overnight/08_trends_weekly.csv`),
y/y against the same four weeks a year earlier, `knowable_from` = quarter start + 35 days (every guide date is >= 32 days into the quarter;
the fourth week is complete by day 28). This is the honest version of "Trends is daily, so it is a nowcast input".

**Signal grid (26 signal-line pairs, fixed now; expected sign of c from WS04's `SIGN` map, its observed sign for the Trends share):**

| line | signals (expected sign of c) |
|---|---|
| cor | funds_held_musd (+), fx_usd_per_eur (-), fx_broad_dollar (+), ppi_data_hosting (+), event_E02 interchange (+) |
| ops | event_E05 AI agent (-), appstore_new_ratings_per_day (+), playstore_ratings_new_per_day (+), emp_business_support_services (+), ppi_insurance_brokerage (+) |
| pd | careers_open_roles (+), emp_software_publishers (+), emp_computer_systems_design (+), ahe_information (+), eci_wages_private (+), event_E10 recruiting cut (-) |
| sm | trends_airbnb_share_us (-), trends_airbnb_share_ww (-), trends_airbnb_us level (either), peer_bkng_advertising_yoy (+), peer_expe_sga_yoy (+), trends_qtd4_share_us (-), trends_qtd4_share_ww (-) |
| ga | careers_open_roles (+), cpi_sf_bay (+), emp_computer_systems_design (+) |

Interest income (rates x earning base) is NOT modelled here: WS04 handed it to M7 and M7 has registered it (`below-ebitda__interest_income`).
E07/E08 (AI "one third" / "40 %") have 1-2 post-event quarters and are not testable; they stay as priors. Careers has capture gaps
(n 6-7 y/y pairs): it is run and reported with its n, and a `missing signal -> term 0` rule.

**Tests and pass line (each signal-lead pair is one test).** Incremental value `IV = MAE_rel(line | M1 + signal) / MAE_rel(line | M1)`,
PIT replay, matched quarters, at h=0 and h=1, in W1 (n 14 / 13) and W2 (n 10 / 9), equal- and recency-weighted (half-life 4 quarters,
anchored at 2026Q2, the scorer's convention). **A signal survives only if IV < 0.9 at h=0 in W1 AND W2, equal- AND recency-weighted
(4 comparisons), AND the fitted c at the LIVE vintage (2026-08-06) has the expected sign** ("either" counts as a match). h=1 is reported,
not required. The margin IV (`adj_ebitda_margin_pct` MAE ratio, additive) is reported for every pair. Expectation stated now: zero to two
survivors; the Trends share on S&M is the likeliest; careers is too thin to pass.

**Placebos (pre-registered, same IV statistic).** (i) Future shift: every pair re-run with the signal at q+4 (lead -4, unknowable by
construction) to show what leakage looks like; and the lead-0 alignment for quarterly series (WS04's own alignment, unknowable at h=0) as
the "mild leakage" reference. (ii) Random series: 200 iid N(0,1) series per line at lead 1, PIT, W1 vintages, h=0 and h=1; report the
distribution of IV and the false-positive rate of the single-signal pass line and of "best of 5" selection (the grid has ~5 candidates per
line, so the honest null for `best1` is the minimum IV over 5 random series).

**Registered objects** (both replays PIT / full_sample; h=0,1,2 at the 14 W1 guide dates, W2 the 10-date subset; LIVE h=0..5 at
2026-08-06 and 2026-09-11 on the WS06 v2b base path; FY26-28 in a separate annual CSV with bear / base / bull):

| object | targets | spec_ids | n_params (registry) |
|---|---|---|---|
| `lines_aug` | `cor_cash_musd, ops_cash_musd, pd_cash_musd, sm_cash_musd, ga_cash_ex_reserves_musd` | `none_rw`, `none_eq` (= M1 b_elastic), `best1_rw`, `best1_eq` (best one-signal per line by h=0 rw IV averaged over W1/W2 — in-sample selection, judged against placebo ii), `ridge_all_rw`, `ridge_all_eq` (all candidates of the line at their default lead, L2-penalised), `surv_<signal>_rw` (one per survivor; absent if none) | none 10; best1 15 (+1 c per line); ridge_all 10 + 26 + 1 (lambda) = 37; surv 11 |
| `margin_aug` | `adj_ebitda_margin_pct, adj_ebitda_musd, total_cash_costs_musd` | same | same |

Ridge: signal columns standardised on the fit sample (weighted sd), penalty lambda = n_obs on the signal coefficients only (g and b
unpenalised), missing signal values set to 0 (no information) rather than dropping the row. Quantiles: M1's walk-forward pool convention
(PIT last-12 realised errors of the same spec / target / horizon; relative for $ lines, additive for the margin; fallback 10 % / 3 pp).
LIVE: a signal term beyond the knowable horizon is 0 (reverts to M1) and flagged; `trends_qtd4` for 3Q26 uses the first four weeks of
July 2026. Count of pre-registered tests: 26 pairs x leads (52 one-signal specs + 5 ridge) + 2 x 26 placebo shifts + 5 x 200 random = written
up in section 5 whatever the outcome. Nothing in this section is edited after the run.

---
