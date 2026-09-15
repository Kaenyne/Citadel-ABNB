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

## 1. Bottom line

**The alt-data route does not move Airbnb's margin.** Fifty pre-registered one-signal tests were run on top of
M1's driver-line model under a strict `knowable_from` gate. **One survived** the pass line — G&A on private
computer-systems-design employment (BLS CES6054150001) at a two-quarter lead: line MAE ratio 0.898 / 0.896 (W1
equal / recency) and 0.895 / 0.898 (W2), sign as expected (+), `t` 2.11 on 18 y/y observations. It is not
believable as a finding: the random-series placebo puts the false-positive rate of exactly this pass line at
**5.5% for a single G&A test and 22.5% for best-of-5 selection**, six G&A specs were tested, and 50 tests were
run in total — one survivor is precisely what the null predicts. And it barely matters even if real: it cuts the
G&A line MAE by ~10% and the **adjusted EBITDA margin MAE by 0.6% in W1 and 0.1% in W2** (2.245 pp vs 2.259 pp;
1.908 pp vs 1.910 pp), because G&A is ~6% of revenue and the margin error is dominated by revenue, S&M and
cost of revenue. Registered as `surv_emp_computer_systems_design_rw`, flagged here as noise-indistinguishable,
**not carried into the LIVE margin view**.

The three secondary results are worth more than the survivor:

1. **The best-of-grid composite makes the margin worse, not better.** `best1` (the best signal per line, selected
   in-sample on h=0 recency-weighted line IV) improves four of the five lines at h=0 — S&M IV 0.899/0.880, G&A
   0.896/0.898, product dev 0.906/0.890, ops 0.929/0.911 — and yet the **margin** MAE goes from 2.259 pp to
   2.431 pp in W1 and 1.910 pp to 2.157 pp in W2 (margin IV 1.233 / 1.290). M1's line errors partially cancel in
   the sum; "improving" each line separately breaks the cancellation. Any future work that tunes cost lines one at
   a time must be scored on the margin, not on the lines.
2. **The WS04 S&M / Google-Trends finding does not survive knowability.** WS04's headline survivor (Trends category
   share vs S&M per night, r -0.64, n 18) is a *contemporaneous* relationship. Aligned as WS04 aligned it (lead 0,
   the completed quarter's Trends value, which is not knowable on a guide date 32-49 days into the quarter) it is
   the strongest thing in the whole grid: with the gate switched off, `sm | trends_airbnb_share_us@0` scores IV
   0.827/0.847 (W1) and 0.948/0.894 (W2). Lagged one quarter so it *is* knowable, it is worth nothing: 1.079/1.023
   (W1), 1.051/1.002 (W2). The honest quarter-to-date version built here (`trends_qtd4_share_ww`, first three weeks
   of the quarter, knowable ~day 28) recovers most but not all of it — 0.936/0.899 (W1), 0.905/0.880 (W2) — and
   **fails the pass line on the equal-weighted leg in both windows**. It is the closest near-miss in the grid and
   the only signal worth more data (see section 7).
3. **The leakage placebos price the noise floor.** With the gate off, 47 placebo specs (26 at a +4-quarter future
   shift, 21 at the lead-0 alignment) have median IV 1.02-1.05 and **none** clears the pass line. Future values of
   BLS/FRED/Trends series do not predict Airbnb's cost lines even when you cheat — the cleanest available evidence
   that the "relationships" in this grid are fitted noise rather than weak signal.

**For the 5 Nov card there is no alt-data edge on margins.** The LIVE margin table below is M1's, unchanged.

## 2. What ran

```
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/M4_alt_augmented/run.py       # 465 s, exit 0
py -3.13 analysis/src/margin_build/10_harness_margin/score.py    # run by run.py at the end
```

Equation, per line, per signal (M1's model is imported from `M1_driver_lines/run.py`, never copied, so the `none`
spec is bit-for-bit M1):

```
d4 log L_q = g_L + b_L * d4 log D_q + c * x_{q-lead} + e_q ,   weights exp(-ln2 * (T-q)/4)
D = gbv (cor), nights (ops), revenue (sm), none (pd, ga);  x = the signal's y/y change
```

Free parameters as registered: `none` 10 (M1's), `best1` 15 (+1 c per line), `ridge_all` 37 (10 + 26 c + lambda),
`surv_*` 11. Registry rows: 9,632 across `alt-augmented__lines_aug.csv` (6,020) and `alt-augmented__margin_aug.csv`
(3,612), both replays (`PIT`, `full_sample`), seven `spec_id`s, h=0/1/2 at 18 vintages and h=0..5/9 LIVE.

**Test count.** 50 one-signal tests (26 line-signal pairs x their leads); 47 leakage placebos; 1,000 random-series
placebos (200 per line); 5 `ridge_all` fits and 5 `best1` fits as composites. Nothing was dropped or re-specified
after seeing a result; section 0 is as written before the first fit.

### Deviations from section 0, stated

1. **The QTD Trends series is three weeks, not four.** `build_qtd` takes the weeks whose Monday falls in the first
   21 days of the quarter (n = 3 in every quarter of the sample) and stamps `knowable_from` = that last Monday + 8
   days, i.e. about day 28 of the quarter, not day 35. This is *stricter* on knowability than section 0 promised and
   noisier in the signal. It changes nothing about the pass line and the result is a fail either way.
2. **The placebos are run with the knowability gate switched off.** With the gate on, an unknowable alignment simply
   reverts to M1 and every placebo IV is exactly 1.000 — which demonstrates nothing. Disabling the gate for the
   placebo *only* is what a careless analyst would do, and pricing that mistake is the whole point of the placebo.
   The pass line and the 50 real tests are untouched and still run with the gate on.
3. **`c_live` equals `c_full` in every row** of the test table. That is not a bug: `history_as_of(2026-08-06)` and
   `history_as_of(2026-09-11)` both end at 2Q26 (printed 6 Aug 2026), and both fits anchor recency weights at 2026Q2,
   so the last PIT fit and the full-sample fit are the same fit. Disclosed here so nobody reads it as leakage.

## 3. The grid (50 tests, h=0, PIT, matched quarters; pass = IV below 0.9 on all four and sign OK)

IV = MAE(M1 + signal) / MAE(M1) on the line in relative terms. Full file:
`data/processed/margin_build/M4_alt_augmented/M4_alt_augmented_signal_tests.csv`. Best 12 of 50 by W1 recency IV:

| line | signal | lead | n obs | n qtrs signal used (W1, 14) | c | t | IV W1 eq | W1 rw | W2 eq | W2 rw | sign OK | pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ga | emp_computer_systems_design | 2 | 18 | 13 | +1.910 | 2.11 | **0.898** | **0.896** | **0.895** | **0.898** | yes | **PASS** |
| sm | trends_qtd4_share_ww | 0 | 18 | 13 | -0.526 | -2.39 | 0.936 | 0.899 | 0.905 | 0.880 | yes | fail (eq) |
| pd | careers_open_roles | 2 | 7 | **2** | +0.055 | 9.61 | 0.938 | 0.906 | 0.908 | 0.890 | yes | fail (eq) |
| sm | trends_qtd4_share_us | 0 | 18 | 13 | -0.728 | -2.35 | 0.931 | 0.924 | 0.948 | 0.928 | yes | fail |
| ops | emp_business_support_services | 1 | 18 | 13 | -2.080 | -1.42 | 0.977 | 0.929 | 0.945 | 0.911 | **no** | fail |
| ga | cpi_sf_bay | 2 | 18 | 13 | +1.764 | 0.75 | 0.917 | 0.976 | 0.951 | 0.989 | yes | fail |
| sm | trends_airbnb_share_ww | 1 | 18 | 13 | -0.611 | -2.36 | 1.352 | 1.056 | 0.958 | 0.896 | yes | fail |
| ga | emp_computer_systems_design | 1 | 18 | 13 | +1.675 | 1.56 | 1.007 | 0.965 | 0.958 | 0.953 | yes | fail |
| ga | careers_open_roles | 2 | 7 | 2 | -0.036 | -0.59 | 0.971 | 0.973 | 0.965 | 0.971 | no | fail |
| ops | emp_business_support_services | 2 | 18 | 13 | +0.725 | 0.49 | 0.986 | 0.980 | 0.968 | 0.972 | yes | fail |
| pd | ahe_information | 2 | 18 | 13 | -0.908 | -1.04 | 1.032 | 1.008 | 1.011 | 0.998 | no | fail |
| sm | trends_airbnb_share_us | 1 | 18 | 13 | -0.679 | -1.90 | 1.079 | 1.023 | 1.051 | 1.002 | yes | fail |

Read the `pd | careers_open_roles@2` row carefully: **the signal term was present in only 2 of the 14 W1 quarters**
(Airbnb's careers page has capture gaps, so only 6-7 y/y pairs exist and only the newest vintages can use them).
Its IV is 12 quarters of "identical to M1" plus 2 quarters of luck. WS04's `r 0.9, n 6-7` on postings versus
product development is not testable point-in-time and should not be quoted as a forecasting result.

The other 38 tests are all above 0.9 somewhere, most above 1.0. By line, the median W1 recency IV of the tested
signals is cor 1.11, ops 1.15, pd 1.08, sm 1.07, ga 0.97 — i.e. **adding an external series to M1 makes the
typical cost line worse.** The cost lines are spending decisions, and macro series do not know about them.

### 3a. Margin IV: none of it reaches the margin

| spec | margin IV W1 rw | W2 rw |
|---|---|---|
| `surv_emp_computer_systems_design_rw` (the survivor) | 1.009 | 1.016 |
| `best1_rw` (best signal per line) | 1.233 | 1.290 |
| `best1_eq` | 1.273 | 1.333 |
| `ridge_all_rw` (all 26, L2) | 1.020 | 1.026 |
| `ridge_all_eq` | **0.972** | **0.966** |

The only composite that helps the margin at all is the equal-weighted ridge, by 3%, with 37 free parameters against
14 backtest quarters. That is not a model, it is a shrinkage artefact. On `adj_ebitda_margin_pct` at h=0 the
scoreboard gives `ridge_all_eq` MAE 2.183 pp (W1) and 1.803 pp (W2) against `none_eq` 2.214 and 1.842 — a 1.4% and
2.1% improvement for 27 extra parameters.

## 4. Placebos

**(i) Leakage (gate off), 47 specs.** Median IV 1.052 (lead 0) and 1.020 (+4-quarter future shift); **zero pass**.
Distribution of W1 recency IV: lead 0 min 0.847 / p25 1.022 / max 1.348; future shift min 0.940 / p25 1.000 / max
1.303. The strongest leakage rows are `sm | trends_airbnb_share_us@0` (0.827 eq / 0.847 rw, W1) and
`sm | trends_airbnb_share_ww@0` (0.969 / 0.922) — the WS04 contemporaneous finding, and the only place in the grid
where cheating buys anything. Note what this says about the survivor: `ga | emp_computer_systems_design` at lead 0,
with the gate off, scores 0.974 / 0.979. **Contemporaneously the signal does nothing; only the two-quarter lag
"works"**, which is the signature of a spurious lag, not of a payroll-cost mechanism.

**(ii) Random series (200 iid N(0,1) per line at lead 1, PIT, 14 W1 vintages, h=0 and h=1).**

| line | FP rate, single test | FP rate, best of 5 | median IV W1 rw | median IV W2 rw | 5th pct W1 rw | median margin IV W1 rw |
|---|---|---|---|---|---|---|
| cor | 0.5% | 2.5% | 1.106 | 1.080 | 0.936 | 1.021 |
| ops | 1.0% | 5.0% | 1.075 | 1.076 | 0.879 | 1.017 |
| pd | 1.0% | 5.0% | 1.136 | 1.151 | 0.966 | 1.008 |
| sm | 2.0% | 10.0% | 1.085 | 1.081 | 0.930 | 1.053 |
| **ga** | **5.5%** | **22.5%** | 1.026 | 1.022 | 0.838 | 1.016 |

G&A is the noisiest line and the easiest to "improve" with nothing. Six G&A specs were tested; at a 5.5% per-test
rate the chance of at least one G&A false positive is 29%. Across the whole grid the expected number of false
positives under the null is roughly 50 x 2% = **1.0**. We observed 1. There is no evidence here of any real signal.
Note also that **the median random series makes the margin worse** (margin IV 1.01-1.05 in every line): adding a
pure-noise regressor to a 14-18 observation recency-weighted fit costs about 1-5% of margin accuracy, which is the
right prior for any un-validated alt-data line item.

## 5. Scoreboard

`data/processed/margin_build/10_harness_margin/scoreboard_margin.csv`, target `adj_ebitda_margin_pct`, h=0, PIT.

| spec | window | n | MAE pp | rw MAE pp | MAE / seasonal_naive | rw ratio | beats sn | rw beats sn | survives both | rw survives both | n_params |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `none_eq` (= M1) | W1 | 14 | 2.214 | 1.627 | 0.990 | 0.851 | yes | yes | **yes** | **yes** | 10 |
| `none_eq` | W2 | 10 | 1.842 | 1.432 | 0.941 | 0.816 | yes | yes | | | 10 |
| `none_rw` (= M1) | W1 | 14 | 2.259 | 1.667 | 1.010 | 0.871 | no | yes | no | **yes** | 10 |
| `none_rw` | W2 | 10 | 1.910 | 1.483 | 0.975 | 0.845 | yes | yes | | | 10 |
| `surv_emp_computer_systems_design_rw` | W1 | 14 | 2.245 | 1.681 | 1.004 | 0.879 | no | yes | no | **yes** | 11 |
| `surv_...` | W2 | 10 | 1.908 | 1.507 | 0.974 | 0.859 | yes | yes | | | 11 |
| `best1_rw` | W1 | 14 | 2.431 | 2.055 | 1.087 | 1.074 | no | no | no | no | 15 |
| `best1_rw` | W2 | 10 | 2.157 | 1.913 | 1.101 | 1.090 | no | no | | | 15 |
| `best1_eq` | W1 | 14 | 2.445 | 2.072 | 1.093 | 1.083 | no | no | no | no | 15 |
| `best1_eq` | W2 | 10 | 2.125 | 1.910 | 1.085 | 1.088 | no | no | | | 15 |
| `ridge_all_eq` | W1 | 14 | 2.183 | 1.582 | 0.976 | 0.827 | yes | yes | **yes** | **yes** | 37 |
| `ridge_all_eq` | W2 | 10 | 1.803 | 1.384 | 0.920 | 0.788 | yes | yes | | | 37 |
| `ridge_all_rw` | W1 | 14 | 2.248 | 1.699 | 1.005 | 0.888 | no | yes | no | **yes** | 37 |
| `ridge_all_rw` | W2 | 10 | 1.904 | 1.521 | 0.972 | 0.867 | yes | yes | | | 37 |

`cov80` is 0.93-1.00 and `cov90` is 1.00 for every spec: M1's Gaussian walk-forward bands are too wide at h=0 and
the augmentations inherit that. That is an M1 issue, not an M4 one; flagged for the red team.

Line-level h=0 W1 / W2 MAE ($m), `none_rw` then `best1_rw`: cor 18.4/20.6 then 20.4/20.6 (worse), ops 17.8/17.6
then 17.3/16.4, pd 11.2/11.4 then 10.4/10.3, sm 37.9/34.9 then 35.0/31.6, ga 16.0/18.9 then 14.5/17.0. Four lines
better, the margin worse — see section 1, point 1.

## 6. LIVE forecasts (vintage 2026-09-11; revenue path = bridge v3 3Q26/4Q26 + WS06 v2b 1Q27-4Q27)

Adjusted EBITDA margin, %, base scenario, PIT replay. `none_rw` is M1's registered `b_elastic_rw`.

| quarter | `none_rw` (= M1) | `surv_...` | `best1_rw` | `ridge_all_rw` | consensus |
|---|---|---|---|---|---|
| 3Q26 | 51.57 | 51.70 | 52.06 | 51.50 | 49.78 |
| 4Q26 | 28.47 | 28.62 | 28.63 | 28.47 | 28.90 |
| 1Q27 | 19.46 | 19.46 | 19.46 | 19.45 | |
| 2Q27 | 34.38 | 34.38 | 34.38 | 34.38 | |
| 3Q27 | 50.58 | 50.58 | 50.58 | 50.49 | |
| 4Q27 | 26.33 | 26.33 | 26.33 | 26.31 | |

Adjusted EBITDA $m, base: 3Q26 `none_rw` 2,477.7 / `surv` 2,483.6 / `best1_rw` 2,501.0 against consensus 2,361.5;
4Q26 904.8 / 909.7 / 909.8 against consensus 913.7. Annual (`..._annual_forecasts.csv`): FY26 36.18 / 36.26 /
36.38%, FY27 35.14 / 35.14 / 35.15%, FY28 32.62 / 32.62 / 32.63% (Street FY27 36.45%, WS31b base FY27 35.94%).
Bear and bull columns are in `M4_alt_augmented_live_quarterly.csv`.

From 1Q27 on, every augmented spec is identical to M1 to two decimals: the signals are knowable at most one or two
quarters ahead, so beyond h=1 the model reverts to M1 by construction. **Even the survivor changes the 5 Nov
quarter by +0.13 pp and 4Q26 by +0.15 pp** — inside M1's own h=0 residual sd (about 2.2 pp) by a factor of 15.

## 7. What failed, and what would settle it

- **The WS04 S&M / Trends result.** The correlation is real and contemporaneous; the forecasting version is not.
  The quarter-to-date reconstruction gets to IV 0.88-0.94 and fails on the equal-weighted leg. What would settle
  it: a *daily* Trends pull at each historical guide date (we only have weekly stitched values, and only for the
  P1_peers payload), so the QTD window can be the full 32-49 days the guide date actually allows instead of three
  weeks; plus a paid-search cost proxy (ad-transparency impression counts) which we do not have point-in-time.
  Both are data acquisitions, not modelling. I would not spend the time before 2 Oct.
- **Careers postings for product development and G&A.** n = 6-7 y/y pairs, 2 usable backtest quarters. Untestable.
  If the capture keeps running this becomes testable around FY28 — not for this pitch.
- **App / Play store review flow for ops and support.** Wrong sign at both leads (c -0.007 to -0.020), IV 1.13-1.24.
  The AI-support step dummy E05 has the right sign (c -0.008) but t -0.27 and IV 1.04. WS04's "right sign, under
  the line" verdict is confirmed: the AI-support saving is real in management's language but not yet in the ops
  line at a size the data can see.
- **LightGBM was not attempted.** With 14-18 y/y observations per line, a gradient-boosted model has no honest
  point-in-time fit. Section 0 said "probably skip and say so"; skipped.
- **Interest income** is not modelled here (handed to M7, which has registered `below-ebitda__interest_income`).
  The WS04 diagnostic (`04_interest_income_yield_diagnostic.csv`) is clean and worth quoting: realised yield on the
  average earning base (cash + short-term investments + funds held on behalf of customers) runs at
  **0.83-0.97 times the 3-month T-bill**, ratio 0.862 in 2Q26 and drifting up as rates fall (0.77 in 1Q23). The
  arithmetic check: 2Q26 average earning base $23,424m x 3.624% x 0.862 / 4 = $183m against $183m reported. A
  forward rule of `avg earning base x tbill3m x 0.86` is defensible; the earning base is seasonal, peaking in Q2
  on funds held on behalf of customers.

## 8. Corrections to existing work

None. WS04's findings are not wrong — they are correlations, correctly labelled as such in
`docs/margin-build/notes/04_alt_signals.md`. This note adds the point-in-time forecasting test WS04 did not run,
and reports that the two headline survivors (Trends to S&M, careers to product development) do not convert into
forecast accuracy under a strict knowability gate. Anyone quoting WS04 should quote it as a diagnostic, not as an
input to the margin forecast.

## 9. Files written

Scripts: `analysis/src/margin_build/M4_alt_augmented/run.py`, `analysis/src/margin_build/M4_alt_augmented/README.md`.

Processed, all under `data/processed/margin_build/M4_alt_augmented/`:
`M4_alt_augmented_signal_tests.csv`, `_iv_grid.csv`, `_iv_registered.csv`, `_placebo_random.csv`,
`_placebo_summary.csv`, `_best1_selection.csv`, `_coefs_by_vintage.csv`, `_forecasts_wide.csv`,
`_registry_long.csv`, `_live_quarterly.csv`, `_live_margin_by_spec.csv`, `_annual_forecasts.csv`,
`_trends_qtd_us.csv`, `_trends_qtd_ww.csv`, `_scoreboard_rows.csv`, `_build.json`.

Registry: `data/processed/margin_build/registry/alt-augmented__lines_aug.csv` (6,020 rows),
`data/processed/margin_build/registry/alt-augmented__margin_aug.csv` (3,612 rows).

Figures: `analysis/figures/margin_build/M4_alt_augmented_iv_grid.png`,
`analysis/figures/margin_build/M4_alt_augmented_placebo.png`.

Note: `docs/margin-build/notes/M4_alt_augmented.md` (this file).

## For the model

| series / parameter | value | unit | source |
|---|---|---|---|
| Alt-data margin overlay, 3Q26-4Q27 | **0.00** | pp | this note, sections 1 and 6 — no signal survives; use M1 unchanged |
| Prior for an un-validated alt-data cost regressor | margin MAE ratio **1.01-1.05** | ratio | section 4(ii), random-series placebo, 1,000 draws |
| False-positive rate, IV<0.9 pass line, single test | 0.5-5.5% by line (G&A worst) | prob | `M4_alt_augmented_placebo_summary.csv` |
| False-positive rate, best-of-5 selection | 2.5-22.5% by line | prob | same |
| Score cost-line work on the margin, not the lines | best1 improves 4/5 lines, margin MAE +7.6% (W1) | — | sections 3a and 5 |
| Trends category share to S&M, knowable version | IV 0.936 / 0.899 (W1), 0.905 / 0.880 (W2) — **fails** | ratio | section 3 |
| `trends_qtd4_share_ww` 3Q26 | 65.00 (66.92 in 3Q25, -2.9% y/y) | % of P1_peers search | `M4_alt_augmented_trends_qtd_ww.csv`, knowable 2026-07-27 |
| `trends_qtd4_share_us` 3Q26 | 53.04 (55.63 in 3Q25, -4.7% y/y) | % of P1_peers search | `M4_alt_augmented_trends_qtd_us.csv`, knowable 2026-07-27 |
| Interest income rule (hand-off to M7) | avg earning base x tbill3m x **0.862** | ratio to T-bill | WS04 `04_interest_income_yield_diagnostic.csv`; 2Q26 check $183m vs $183m |
| G&A on computer-systems-design employment, c | +1.91 (t 2.11, n 18, lead 2) | elasticity | `M4_alt_augmented_coefs_by_vintage.csv` — registered, **not** recommended |

## For the 5 Nov card

There is no external dataset in our reach that improves the 3Q26 margin call. Do not put an alt-data line on the
card. Two defensible sentences if asked: (1) "We tested 50 external series against the five cost lines
point-in-time; one cleared the bar, and the random-series placebo says a bar like that fires 5.5% of the time on
noise, so we treat the margin as a spending-decision forecast, not a nowcast." (2) "The one external series that
does correlate with S&M — Airbnb's share of category search — only works contemporaneously; by the time it is
knowable on a guide date it is worth nothing, and the quarter-to-date version misses our bar." The margin numbers
on the card stay M1's: **3Q26 51.6% / $2,478m, 4Q26 28.5% / $905m, FY26 36.2%, FY27 35.1%.**

## RESUME

M4 is complete: `run.py` rebuilds end to end in 465 s with exit code 0, both objects are registered and the
scoreboard is current. The next agent should NOT re-run the grid — it is a negative result and it is written up.
Three things are worth someone's time, in order. First, the red team should check section 1, point 1 (the
best-of-grid composite improves four lines and degrades the margin) against M2 and M6, because it implies every
line-level tuning result in this run should be re-scored on `adj_ebitda_margin_pct` before it is quoted; the
machinery is in `M4_alt_augmented_iv_registered.csv`. Second, M7 should take the interest-income ratio in section 7
(average earning base x tbill3m x 0.862, which checks to the dollar in 2Q26) and confirm it against whatever it
registered; if M7's object disagrees by more than $5m a quarter, one of the two earning-base definitions is wrong.
Third, if anyone acquires a *daily* Google Trends pull for the P1_peers payload back to 2022, re-run only the
`sm | trends_qtd4_*` specs with the window extended to the full pre-guide-date period (the code path is
`build_qtd` in `run.py`; change the 21-day cut and the +8-day stamp); that is the single near-miss in the grid
(IV 0.88-0.94) and the only route by which alt data could earn a place in the margin model before the 22-24 Oct
finals. Everything else in the grid is noise and should stay in the drawer.

---

# Discussion response (WS22, 14 Sep 2026)

Written by the group A discussion agent (M1 / M4 / M6). Everything above this line is the original note and was
not edited. Findings addressed: **R01, R02, R03 (inherited), R08, R10, R11, R14, R17, R19**.
Backups: `data/processed/margin_build/M4_alt_augmented/_pre_discussion/` and
`data/processed/margin_build/registry/alt-augmented__*_pre_discussion.csv.bak`.
Rebuild: `MARGIN_SKIP_SCORE=1 py -3.13 analysis/src/margin_build/M4_alt_augmented/run.py` (130 s, exit 0).
`score.py` was **not** run; the orchestrator re-scores once.

**Every M4 output is byte-identical to the pre-discussion build**, both registry files included
(`cmp` on `alt-augmented__margin_aug.csv`, `alt-augmented__lines_aug.csv`, `_live_quarterly.csv`,
`_annual_forecasts.csv`, `_signal_tests.csv`, `_placebo_summary.csv`). The only code change in this package is the
`MARGIN_SKIP_SCORE` guard and a tolerant read of a missing scoreboard file. That identity is itself a result: it
confirms that M1's R04 step gate does not touch the `b_elastic` base M4 imports, so M4's 50 tests, its 47 leakage
placebos and its 1,000 random-series draws all stand exactly as written.

## D1. R03 — "M4 inherits the oracle spec". REJECTED on the facts.

The red team lists M4 as inheriting M1's oracle spec. It does not. M4's registered `spec_id`s are `none_rw`,
`none_eq`, `best1_rw`, `best1_eq`, `ridge_all_rw`, `ridge_all_eq` and `surv_emp_computer_systems_design_rw`;
a substring scan for `revknown` / `nightsknown` over both `alt-augmented__*.csv` files returns **0 rows**, and M4
never calls M1's family-`e` path. M4's `none` spec is M1's `b_elastic`, which uses the PIT revenue leg. Nothing to
fix. (M1's own oracle spec *has* been withdrawn from the registry — see M1's D2.)

## D2. R11 — the LIVE 3Q26 ceiling breach. ACCEPTED; M4 adopts M1's reconciliation.

M4's LIVE margin table is M1's by construction: `none_rw` 3Q26 **51.57%**, and every augmented spec is within
+0.15pp of it (`surv` 51.70, `best1_rw` 52.06, `ridge_all_rw` 51.50) against the 2Q26 letter's ceiling of
**50.085%** and Street 49.776%. The defence that the quarterly sentence is sandbagged fails on the data
(`q_guide_implied` realised gaps: W2 mean -0.19pp, median -0.94pp, 4 of 10 quarters above the sentence — see M1's
D3), so the card number is the clipped **50.09% / $2,406M**, not 51.6%. M4 adds one thing here that M1 cannot: the
augmentations move 3Q26 by at most **+0.49pp** (`best1_rw`) and the survivor by **+0.13pp**, so **no external
series in the grid closes any part of the 1.49pp gap to the sentence.** The gap is a spending-level question, not
an information question — which is the same conclusion M4 reached from the other direction.

## D3. R14 — line wins are free. ACCEPTED; M4 raised it and it is now confirmed and sharpened.

M4's own section 1 point 1 (best1 improves four of five lines and makes the margin worse) is confirmed by the red
team's check 06 and generalises. Re-scored against `seasonal_naive_drift` rather than `seasonal_naive` (PIT, h=0;
paired loss differentials with Newey-West(1) and a sign test; `analysis/src/margin_build/22_discussion_group_A/repro_drift.py`), `best1_rw`'s line "wins" mostly disappear too:

| line | `best1_rw` ratio vs seasonal naive (W1) | vs **drift** (W1) | t | p | vs drift (W2) |
|---|---|---|---|---|---|
| cost of revenue | 0.381 | 0.836 | -1.21 | 0.23 | 0.768 |
| operations and support | 0.773 | 0.917 | -0.42 | 0.67 | 0.860 |
| product development | 0.315 | **1.032** | +0.12 | 0.90 | **1.104** |
| sales and marketing | 0.371 | **1.088** | +0.39 | 0.70 | **1.032** |
| G&A ex reserves | 0.702 | 0.918 | -0.63 | 0.53 | 0.988 |
| **total cash costs** | 0.281 | **1.226** | +1.37 | 0.17 | **1.242** |
| **adj EBITDA margin** | **1.087** | **1.019** | +0.13 | 0.90 | **1.068** |

So the honest version of M4's warning is stronger than the one in section 1: **`best1` does not really improve
four of five lines either — it improves them against a baseline that does not know the line is growing.** Against
a drift naive it improves none of them at any conventional level, and it still makes the margin worse. The rule
M4 proposed ("score cost-line work on the margin, not on the lines") should be amended to: **score cost-line work
on the margin, and score lines against `seasonal_naive_drift`.**

This also puts a number on the `ridge_all_eq` cell that WS20 might otherwise pick up: its margin ratio of 0.976
(W1) / 0.920 (W2) against seasonal naive has t **-0.20** / **-0.52**, p **0.84** / **0.60**, and is better in
7 of 14 and 5 of 10 quarters — on **37 free parameters against 14 backtest quarters**. It is not a result.

### D3b. Addendum for WS20 open question 7: what margin-first selection would have picked

The board asks whether `best1` churns signals by vintage and whether a shared signal would trade line accuracy
for margin accuracy. **It does not churn**: the five picks are made once on the full-window h=0 recency-weighted
line IV and held fixed at every vintage; only `c` is refit (`_best1_selection.csv`, `_coefs_by_vintage.csv`).
And the margin damage is concentrated in **one** pick: the per-signal margin IVs (h=0, W1, rw) of the five
selected signals are cor 1.011, ops 1.032, pd 1.018, ga 1.009 — and **sm `trends_qtd4_share_ww@0` 1.253**. The
signal with the best *line* IV in the whole grid is, on its own, responsible for almost all of the composite's
23% margin degradation, because S&M is the largest cash line ($730M of a $2,326M stack) and its error is
**negatively** correlated with the rest of the stack. Improving it in isolation removes a hedge.

Ranking each line's candidates by **margin** IV instead (50 real gated tests, placebos excluded):

| line | n | best-on-margin | margin IV W1 / W2 | candidates < 1.0 in both windows |
|---|---|---|---|---|
| cor | 10 | `ppi_data_hosting@1` | 0.974 / 0.948 | 2 |
| ops | 10 | `playstore_ratings_new_per_day@2` | **0.903 / 0.876** | 6 |
| pd | 12 | `ahe_information@2` | 0.992 / 0.988 | 5 |
| sm | 12 | `trends_airbnb_share_us@2` | **0.906 / 0.901** | 2 |
| ga | 6 | `careers_open_roles@1` | 0.989 / 0.986 | 3 |

A margin-selected composite would therefore land near 0.90-0.99 rather than 1.233. **We did not fit it**, and it
should not be believed: the median margin IV over the 50 real tests is **1.010 / 1.011** and **18 of 50** are
below 1.0 in both windows (36%, the coin-flip rate this note's own random-series placebo predicts for a
two-window bar); it is a five-way best-of-6-to-12 in-sample selection on 14 quarters, which section 4(ii) prices
at up to a **22.5%** false-positive rate; the two picks doing the work fail on economics (`playstore` on ops is
wrong-signed at both leads, and `trends_airbnb_share_us@2` is the lagged Trends series section 3 shows is worth
nothing once knowable); and it would be a post-hoc spec added after seeing the grid — the failure mode R05 caught
in M3. If it is fitted before the finals it needs its own pre-registration, its own best-of-k placebo and a
paired p-value.

## D4. R01, R02, R08, R10, R17, R19 — accepted as quoting rules.

- **R01 / R02.** Reproduced on M4's cells (`22_discussion_group_A/groupA_paired_tests.csv`), h=0, PIT, vs seasonal naive: `none_rw`
  t +0.07 / -0.14 (W1 / W2), `ridge_all_eq` -0.20 / -0.52, `surv_...` +0.02 / -0.14, `best1_rw` **+0.57 / +0.52**
  (worse). Every W1 p >= 0.39. M4's conclusion was already a negative result, so nothing is withdrawn; but the
  survivor row's `rw_survives_both_windows = yes` in section 5's table must always be quoted with its
  **t +0.02, p 0.98, better in 6 of 14** and with the 5.5% / 22.5% placebo false-positive rate that section 4
  already reports. M4 is the one method in the run whose placebo machinery *prices* R01 rather than being caught
  by it: the random-series draws say a pass line like the scoreboard's fires on noise 2.5-22.5% of the time
  depending on the line, which is the same order as the red team's 30% survivor null.
- **R08.** No M4 cell rests on n < 8, except the `pd | careers_open_roles@2` row, where the **signal term is
  present in only 2 of the 14 W1 quarters** — section 3 already says so and says it is untestable. Agreed that the
  scoreboard should carry n beside the flag.
- **R10.** Confirmed; M4 flagged it first ("cov80 0.93-1.00 and cov90 1.00 for every spec — an M1 issue, not an M4
  one, flagged for the red team"). ACCEPT-DEFER: the augmentations inherit M1's over-dispersed Gaussian bands, so
  M4's quantiles should not be quoted either.
- **R17.** Accepted, and it matters more for M4 than for anyone else: the reason a lead-0 quarterly signal can
  never be knowable at h=0 is exactly the same convention. Section 0's lead structure already encodes it.
- **R19.** M4's pre-registration is at commit `fdf3447`, before the results. No action.

## D5. What M4 now claims

Unchanged in substance, with two amendments. **There is no external dataset in our reach that improves the 3Q26
margin call.** Fifty pre-registered point-in-time tests under a strict `knowable_from` gate produced one survivor
(G&A on computer-systems-design employment, lead 2, IV 0.895-0.898), which the random-series placebo says fires
on noise 5.5% of the time per G&A test and 22.5% under best-of-5 selection; across 50 tests the null expects 1.0
false positives and we observed 1. It moves the margin MAE by 0.6% (W1) and 0.1% (W2) and the 5 Nov quarter by
+0.13pp. The two amendments: (a) the composite result is stronger than stated — against a drift baseline `best1`
improves **no** line, not four of five; (b) M4's LIVE margin table is M1's and therefore carries M1's clipped
3Q26 of 50.09%, not 51.57%. The WS04 Trends-to-S&M relationship still does not survive knowability
(lead 0 gate-off 0.83-0.85, knowable lead 1 1.02-1.08, honest quarter-to-date 0.88-0.94, fails the equal-weighted
leg) and the interest-income hand-off to M7 (avg earning base x tbill3m x 0.862) still checks to the dollar in 2Q26.

## D6. Recommended WS23 weights for M4's objects

| object / use | weight | why |
|---|---|---|
| **The negative result itself** ("no alt-data edge on margins"; 50 tests, 47 leakage placebos, 1,000 random draws) | **1.0** | the best-evidenced statement in the run and the one that keeps the pitch honest under questioning |
| The false-positive priors (single test 0.5-5.5%, best-of-5 2.5-22.5%, margin IV 1.01-1.05 for a noise regressor) | **1.0** | the only calibrated prior anyone in this run has for "an unvalidated cost regressor" |
| `margin_aug` / `lines_aug` as **forecasts** (any spec) | **0** | `none` is M1 (already weighted there); `best1` and `ridge_all` are worse on the margin and worse against drift |
| `surv_emp_computer_systems_design_rw` | **0** | registered, and explicitly not recommended by its own author |
| Alt-data margin overlay for 3Q26-4Q27 | **0.00pp** | unchanged |
| Interest-income rule (0.862 x T-bill x earning base) | **1.0**, but it belongs to M7 | verified to the dollar in 2Q26 |
| M4 quantiles | **0** | inherited from M1 and over-dispersed |
