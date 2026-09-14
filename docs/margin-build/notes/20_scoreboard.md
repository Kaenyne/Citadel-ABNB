# WS20. Scoreboard: every margin method, both windows, equal and recency weighted

Margin build run, 13-14 Sep 2026. Slug `20_scoreboard`. Overseer package: it compares, it does not refit.
Scripts `analysis/src/margin_build/20_scoreboard/` (`py -3.13 .../20_scoreboard/run.py`, exit 0, ~60 s).
Data `data/processed/margin_build/20_scoreboard/`. Inputs: the margin harness
(`10_harness_margin/scoreboard_margin.csv`, `scoreboard_by_quarter.csv`, `targets.csv`, `revenue_leg_pit.csv`),
all 32 registry objects, WS03 consensus, WS30 walk, WS31b profiles. Author: agent WS20.

---

## 0. Ranking rules, fixed before any table was read

1. **PIT replay only.** The `full_sample` replay is used only to measure hindsight (section 7).
2. **Oracle specs are not forecasts.** Any `spec_id` containing `revknown`, `nightsknown` or `ebitda_known`
   substitutes a realised driver (revenue, nights, or adj EBITDA itself) and is a diagnostic. They are excluded
   from every ranking and listed in `20_excluded_oracle_and_thin.csv`. **This matters:** on an unfiltered
   scoreboard the h=2 margin winner is `driver-lines|margin_v2|e_revknown_rw` (W2 MAE 1.37pp) and the h=0 EPS
   winner is `below-ebitda|eps|ebitda_known|rw` — both are oracles. Nobody should quote them.
3. **Minimum n:** 8 in W1, 6 in W2. `margin-ts|q_sentence_direction` has n=1 at h=1 and h=2 (one guide date
   produced a qualitative sentence about the following quarter); those cells are never ranked.
4. Rank on MAE; ties to the smaller `n_params`.
5. Objects that consume Street as an input (`street-bias`, the `street` baseline) carry
   `consensus_anchored = True` and are also ranked separately (`rank_independent`), because a pitch that says
   "we are above consensus" cannot use consensus as its only input.

---

## 1. Bottom line

**At h=0 (the quarter being guided) the contest is over and M5 won it.** `street-bias|dispersion_conditioned`
is first in all four h=0 cells on `adj_ebitda_margin_pct` and beats every baseline, including Street, in both
windows and under both weightings. **At h=1 nothing beats the raw Street**, and at h=2 nothing beats the
seasonal naive by a margin worth having. **The below-EBITDA bridge (M7) is the most reliable part of the whole
build**, and **FCF is not forecastable at quarterly frequency by anything we built.**

### The three best objects per target and horizon (PIT, non-oracle, n >= 8 / 6)

`adj_ebitda_margin_pct`, **h=0**, MAE in pp (W1 n=14 / W2 n=10; equal | recency):

| # | object | W1 eq | W1 rw | W2 eq | W2 rw | vs naive (W2 eq) | vs Street (W2 eq) | params | survives both |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M5 `dispersion_conditioned\|rw_hl4` | 1.330 | 0.820 | **0.743** | **0.622** | 0.380 | 0.567 | 5 | yes / yes |
| 2 | M5 `dispersion_conditioned\|rw_hl4_med` | **1.223** | 0.860 | 0.787 | 0.703 | 0.402 | 0.600 | 5 | yes / yes |
| 3 | M5 `street_plus_flowthrough\|rw_hl4` | 1.661 | 1.134 | 0.987 | 0.927 | 0.504 | 0.753 | 6 | yes / yes |
| — | *baseline* `street` | 1.592 | 1.245 | 1.311 | 1.117 | 0.670 | 1.000 | 1 | yes / yes |
| — | *best Street-independent*: M2 `sarima_margin\|lines_aicc` | 2.038 | — | 1.487 | — | 0.759 | 1.13 | 15 | yes / yes |
| — | *next independent*: M3 `actual_given_guide\|rw_hl4_pin` | 2.183 | 1.637 | 1.442 | 1.340 | 0.736 | 1.10 | 2 | yes / yes |

`adj_ebitda_musd`, **h=0** ($m):

| # | object | W1 eq | W1 rw | W2 eq | W2 rw | vs naive (W2 eq) | vs Street | params |
|---|---|---|---|---|---|---|---|---|
| 1 | M5 `street_plus_flowthrough\|rw_hl4` | 43.1 | 34.0 | **33.8** | 31.1 | 0.35 | 0.58 | 6 |
| 2 | M5 `street_plus_bias\|rw_hl4_usd` | 48.5 | **34.0** | 36.7 | **29.7** | 0.38 | 0.63 | 3 |
| 3 | M5 `dispersion_conditioned\|ew_usd` | 55.0 | 43.6 | 43.4 | 38.9 | 0.45 | 0.75 | 5 |
| — | *baseline* `street` | 65.3 | 61.6 | 58.1 | 59.3 | 0.60 | 1.00 | 1 |
| — | *best independent*: M2 `q_sentence_direction\|k_fit_median` | 52.8 | 45.9 | 45.2 | 40.7 | 0.46 | 0.78 | 2 |

**h=1** (margin, pp): the Street baseline is first in all four cells (W1 1.641 eq / 1.252 rw; W2 0.993 / 0.969).
Best non-Street: M3 `actual_given_guide|last_pin` (W2 1.304 eq / 1.208 rw, ratio to Street 1.31 / 1.25) and
M5 `street_plus_flowthrough|rw_hl4` (W1 1.376 rw, ratio 1.10). **Every M5 correction fails at h=1** — M5's own
note pre-registered this failure and reported it honestly; the scoreboard confirms it.
In dollars at h=1 the Street is again first (W2 $46.7M), best non-Street M3 `nocushion_pin` $57.9M (1.24x).

**h=2** (margin, pp): W1 M2 `incremental_margin|k8_ew` 2.019 (0.81x naive, does **not** survive W2);
W2 M3 `actual_given_guide|last` 1.612 (0.94x naive, does **not** survive W1). **No object survives both
windows at h=2 on the margin except `pct_rev_seasonal|nodrift` (rw), which is the seasonal naive by another
name (ratio 1.000).** In dollars at h=2, M2 `incremental_margin|k8_median` survives both (W1 $72.7M 0.55x,
W2 $74.3M rw 0.70x) and is the only defensible h=2 object.

**Does anything beat `guide_implied` and `street`?**
- `guide_implied` is a weak baseline on the quarter (W1 h=0 MAE 4.38pp, W2 3.80pp) because it spreads an
  FY floor over the remaining quarters; **72 of the 74 rankable objects beat it** at h=0 in W2. That is not an achievement.
- `street` is the hard one. **Only M5's three objects beat it at h=0** (ratios 0.57-0.75 in W2 equal), and
  nothing beats it at h=1. Below EBITDA at h=0 the Street is first in W2 on all three GAAP targets and M7's
  `eps|ebitda_pit` is close on EPS (0.124 vs 0.120, 1.04x) and net income (78.5 vs 77.0, 1.02x) but well behind
  on operating income (72.9 vs 58.7, 1.24x). In W1, M7 is ahead of the Street on EPS (0.492 vs 0.524) and net
  income (320 vs 342) and just behind on operating income (114.6 vs 111.6).

### Below-EBITDA (M7) and lines

Six of M7's seven objects beat the seasonal naive at h=0 in both windows under both weightings.
Best-in-class at h=0 (W1 / W2 MAE, ratio to naive): `sbc|yoy_last` 10.8 / 10.9 $m (0.20 / 0.18);
`interest_income|rate_x_base|rw` 17.9 / 10.5 $m (0.32 / 0.42); `share_count|delta|rw` 4.83 / 3.90 m shares
(0.23 / 0.20); `da|last_value` 2.71 / 2.50 $m (0.39 / 0.46); `eps|ebitda_pit|rw` 0.492 / 0.124 $ (0.51 / 0.18).
**FCF fails**: the best quarterly object, `fcf|swing_x_gbv_seasonal_other|rw`, is 1.02x the seasonal naive in W1
and 0.93x in W2 — `survives_both_windows = no`, and `fcf_margin_pct` is worse than naive in both windows. Quote
no quarterly FCF forecast from this build.

Per-line h=0 winners (W2, equal, ratio to naive): `cor` M6 `flex_lines|l0_rw` 18.2 $m (0.33);
`ops` M2 `per_night_seasonal|g_k8_rw` 15.6 $m (0.91); `pd` the `seasonal_naive_drift` **baseline** 9.3 $m (0.24)
— no model beats a drift rule on product development; `sm` M4 `lines_aug|best1_eq` 29.5 $m (0.27);
`ga ex reserves` M4 `lines_aug|best1_eq` 16.9 $m (0.85); `total_cash_costs` M2 `sarima_margin|lines_aicc`
36.0 $m (0.16).

---

## 2. M4's warning, tested: good lines do not make a good margin

M4 warned that line-level improvements can make the margin worse because the line errors of a driver model
cancel. `20_line_vs_margin.csv` puts the mean line-level MAE ratio (five cash lines, h=0, W2, equal) next to the
margin-level ratio of the same method and spec.

| method / lines object / spec | mean line ratio to naive | margin MAE (pp) | margin ratio to naive |
|---|---|---|---|
| M4 `lines_aug\|best1_rw` | **0.549** (best lines in the build) | 2.157 | **1.101** (worse than naive) |
| M4 `lines_aug\|best1_eq` | 0.591 | 2.125 | 1.085 |
| M6 `flex_lines\|l0_rw` | 0.588 | 1.773 | 0.905 |
| M1 `lines_v2\|c_mix_rw` | 0.601 | 1.882 | 0.961 |
| M2 `sarima_margin\|lines_aicc` | 0.666 (mediocre lines) | **1.487** | **0.759** (best margin) |
| M2 `pct_rev_seasonal\|drift_k4_rw` | 0.720 | 2.753 | 1.406 |

**Every one of the 25 line-level objects beats the seasonal naive on the lines (ratios 0.55-0.78), and 11 of
them are at or worse than naive on the margin.** The cross-sectional correlation between the two ratios is
+0.59, i.e. weak. The object with the best lines has nearly the worst margin. WS23 must select on
`adj_ebitda_margin_pct`, never on line MAE; line models earn their place as a *story* about where the margin
comes from, not as the margin forecaster.

---

## 3. Error correlations: there are three views, not ten

Correlation of h=0 margin errors (PIT, W1, n=14 quarters, `20_error_correlations.csv`), one spec per surviving
object:

| | M1 | M4 | M6 | M2 sarima | M2 qsent | M3 | M5 disp | M5 bias | M5 flow | street |
|---|---|---|---|---|---|---|---|---|---|---|
| M1 `b_elastic_eq` | 1.00 | **1.00** | **0.99** | 0.93 | 0.37 | 0.20 | 0.72 | 0.70 | 0.66 | 0.84 |
| M4 `ridge_all_eq` | | 1.00 | 0.99 | 0.93 | 0.35 | 0.19 | 0.74 | 0.71 | 0.67 | 0.83 |
| M6 `l0_rw` | | | 1.00 | 0.94 | 0.29 | 0.11 | 0.77 | 0.72 | 0.71 | 0.82 |
| M3 `actual_given_guide\|rw_hl4_pin` | | | | | 0.12 | 1.00 | **0.06** | 0.14 | **0.02** | 0.13 |
| M5 `dispersion_conditioned` | | | | | | | 1.00 | 0.92 | 0.85 | 0.80 |

Three families:
- **A, the driver / cost-line family** — M1, M4, M6 and M2's SARIMA-on-lines: pairwise r **0.93-1.00**. These
  are four implementations of one model. Averaging them buys nothing.
- **B, the Street-anchored family** — M5's three objects and the Street baseline: r 0.85-0.92 internally, 0.66-0.84
  against family A.
- **C, the guidance-policy view** — M3 `actual_given_guide`: mean pairwise r **0.118**, minimum 0.02. It is the
  only genuinely independent object in the build. M2's `q_sentence_direction` is second (mean r 0.165) and is
  *negatively* correlated with M5 (-0.02 to -0.15).

### Shock quarters vs calm (`20_shock_vs_calm.csv`)

The prompt names 2H22 and 1Q25-2Q25. **2H22 lies outside both windows** (W1 target quarters start 2023Q1), so it
cannot be scored; I report 2025Q1-2Q25 as the shock set and 2023Q1-2Q23 (the ADR-windfall / post-reset quarters)
as a second stress set. MAE in pp:

| object | all 14 | shock 1H25 | stress 1H23 | calm (10) |
|---|---|---|---|---|
| `street` baseline | 1.592 | **2.219** | 1.343 | 1.517 |
| M5 `street_plus_bias\|rw_hl4` | 1.599 | **0.679** | **4.677** | 1.168 |
| M5 `dispersion_conditioned\|rw_hl4_med` | 1.223 | 1.215 | 2.612 | 0.947 |
| M3 `actual_given_guide\|rw_hl4_pin` | 2.183 | 1.298 | **0.792** | 2.638 |
| M6 `flex_margin\|l0_rw` | 2.201 | 1.422 | 2.420 | 2.313 |
| M1 `margin_v2\|b_elastic_eq` | 2.214 | 1.839 | 1.812 | 2.370 |

This is the single most useful table in the note. **The Street is worst exactly when it matters** (its error
rises 46% in the 2025 deceleration), and the M5 corrections are at their best there (0.68pp). But in the 2023
regime break the M5 corrections are catastrophic (4.68pp) and **M3 — which reads the guidance sentence rather
than the consensus — is the best object in the build (0.79pp)**. A blend that carries M3 is buying insurance
against precisely the event that would break M5.

Hardest quarters for everything (`20_hard_quarters.csv`, mean |error| across the ten surviving objects):
2023Q4 4.33pp (every model 4.3pp *below* the actual), 2023Q3 2.90, 2023Q1 2.85, 2024Q1 2.38. The last four
quarters are easy: 2025Q4 1.12, 2026Q1 0.74, 2026Q2 0.44. **The margin has become much more predictable since
2025**, which is the mechanical reason recency weighting helps everywhere.

---

## 4. Where equal and recency weighting disagree

At h=0 on the margin, recency weighting does not change the podium (M5 first in all four cells) but it changes
the middle of the table sharply (`20_rank_disagreement.csv`):

- M2 `q_sentence_direction|k_abs_rw`: rank 68 in W1-equal, rank **13** in W2-equal, rank 10 in W2-recency. Its
  W1 MAE is 3.97pp and its W2 MAE is 1.31pp — a pure regime artefact, and `survives_both_windows = no`.
- M3 `actual_given_guide|last`: rank 62 W1-equal, rank 20 W2-equal; the flagged rows in
  `20_parameter_budget.csv` show its recency-weighted W2 win (0.767x naive) **disappears in W1** (1.048x).
  The pinned variants (`rw_hl4_pin`, `last_pin`) do survive both windows and are the ones to quote.
- M2 `incremental_margin|k8_*`: rank ~49 in W1, ~25 in W2; rw-W2 wins that do not repeat in W1.

Five (object, spec, target) pairs have a recency-weighted W2 win that vanishes in W1, all listed in
`20_parameter_budget.csv` under `FLAG_rw_W2_win_vanishes_in_W1`. **Nothing from M5 or M7 is on that list.**
Reading: the 2024-26 sample is kinder to almost every model than 2023 was, so a W2-only result is the default
expectation, not evidence. Only a result that survives W1 as well should reach the memo.

---

## 5. Interval calibration: unusable across the board

At h=0 on the two headline targets, mean empirical coverage of the registered 80% interval, by method:
M5 1.000, M6 0.991, M4 0.987, M1 0.982, M2 0.950, baselines 0.920, M3 0.910 (min 0.333). **Nominal is 0.80.**
Every family's intervals are too wide — M5's CRPS (1.40) is nearly twice its MAE (0.74), which is what a
too-wide predictive distribution looks like — and M3 has a handful of cells that are far too narrow. The
rolling split-conformal column tells the same story (empirical 0.75-1.00 on n_eval 4-8).

**Recommendation: WS23 should not take any registered quantile at face value.** Size the 5 Nov interval from
the realised dispersion of the chosen combination: the leave-future-out RMSE of the recommended scheme is
**1.12pp** over 2024Q1-2026Q2 and **0.99pp** over the last five quarters. That implies roughly +/-1.6pp at 80%
and +/-2.0pp at 90% for the 3Q26 margin, which is 3-5x tighter than what the registry quantiles say and still
wider than the 0.74pp MAE of the best single object.

---

## 6. Parameter budget

`20_parameter_budget.csv` (162 object-spec-target rows at h=0). Error removed versus the seasonal naive per free
parameter (W2, equal, margin), best first:

| object | params | W1 MAE | W2 MAE | naive error removed / param |
|---|---|---|---|---|
| `street` baseline | 1 | 1.592 | 1.311 | 0.331 |
| M3 `actual_given_guide\|rw_hl4_pin` | 2 | 2.183 | 1.442 | 0.132 |
| M5 `street_plus_bias\|rw_hl4` | 3 | 1.599 | 1.189 | 0.131 |
| M5 `dispersion_conditioned\|rw_hl4` | 5 | 1.330 | 0.743 | 0.124 |
| M5 `street_plus_flowthrough\|rw_hl4` | 6 | 1.661 | 0.987 | 0.083 |
| M1 `margin_v2\|b_elastic_eq` | 10 | 2.214 | 1.842 | 0.006 |
| M6 `flex_margin\|l0_rw` | 12 | 2.201 | 1.773 | 0.008 |
| M4 `margin_aug\|ridge_all_eq` | **37** | 2.183 | 1.803 | 0.002 |
| M2 `sarima_margin\|lines_aicc` | 15 | 2.038 | 1.487 | 0.016 |

The structural models (M1, M4, M6, 10-15 parameters) buy an order of magnitude less error reduction per
parameter than the three- to five-parameter consensus corrections, and M1/M4/M6 are mutually correlated at
0.99. **The build is carrying 59 free parameters across three mutually redundant driver models (M1 10, M6 12,
M4 37), plus 15 more in M2's SARIMA-on-lines.** For the memo,
one of them should be named as the *narrative* model and the other two retired to the appendix.

---

## 7. Hindsight (PIT vs full_sample)

`hindsight_share = (MAE_PIT - MAE_full_sample) / MAE_PIT`, h=0, both headline targets, mean by method:
**M5 0.000**, M1 0.051, M4 0.062, M6 0.143, M2 0.195, **M3 0.243** (max 0.635).

M5's point forecast contains nothing fitted on the future, so its two replays are identical — the strongest
structural argument in its favour. M3's cushion and M2's drift terms look up to 63% better when fitted on the
whole history (e.g. M3 `rw_hl4_prorata` W1 margin 4.60pp PIT vs 1.68pp full_sample). Those PIT numbers are the
honest ones, and any quotation of M2/M3 must come from the PIT replay. It also means M3's true edge would be
larger with more history — a reason to keep it in the blend rather than drop it on raw MAE.

---

## 8. The LIVE table (`20_live_comparison.csv`, `20_live_spread.csv`)

Vintage 2026-09-11 (harness TODAY). One preferred spec per object (the survivor with the lowest W2 h=0 MAE;
rule in `build_live.py`). FY margins use ONE common denominator, the harness PIT revenue leg, so the table
compares margin models and not revenue legs.

| source | 3Q26 $m | 3Q26 % | 4Q26 $m | 4Q26 % | FY26 $m | FY27 $m |
|---|---|---|---|---|---|---|
| **LSEG consensus (11 Sep)** | **2,361.5** | **49.78** | **913.7** | **28.90** | **5,053.7** | **5,766.1** |
| Bloomberg BEST (5 Sep pull) | 2,359.9 | 49.75 | — | — | 5,046.8 | — |
| Management (2Q26 letter) | — | <= 50.09 (ceiling) | — | — | >= 35.5% FY (floor) | — |
| M5 `dispersion_conditioned` | 2,398.5 | 50.30 | 949.6 | 29.28 | 5,128.1 | — |
| M5 `street_plus_bias` | 2,406.2 | 50.83 | 943.6 | 29.49 | 5,129.9 | — |
| M3 `actual_given_guide` | 2,406.1 | 50.09 | 965.2 | 34.51 | 5,151.3 | 5,514.6 |
| M1 `margin_v2\|b_elastic_eq` | 2,482.4 | 51.67 | 910.3 | 28.64 | 5,172.7 | 5,603.9 |
| M6 `flex_margin\|l0_rw` | 2,461.2 | 51.23 | 891.4 | 28.05 | 5,132.6 | 5,438.1 |
| M4 `margin_aug\|ridge_all_eq` | 2,476.1 | 51.54 | 909.9 | 28.63 | 5,166.0 | 5,593.8 |
| M2 `sarima_margin\|lines_aicc` | 2,474.0 | 51.50 | 903.4 | 28.43 | 5,157.4 | 5,412.1 |
| M2 `incremental_margin\|k8` | 2,298.9 | 47.93 | 925.9 | 29.20 | 5,004.8 | 5,550.4 |
| WS31b base profile | 2,447.6 | 51.30 | 766.9 | **24.65** | — | — |
| WS31b management profile | 2,488.2 | 52.15 | 806.7 | 25.93 | — | — |
| **method median (preferred specs)** | **2,406.1** | **50.19** | **910.3** | **28.64** | **5,129.9** | **5,565.7** |
| **spread max - min across methods** | **183.5** | **3.74pp** | **73.7** | **6.46pp** | **167.9** | **213.2** |

Readings:
1. **3Q26: the methods sit above consensus.** Median 50.19% vs Street 49.78% (+0.41pp) and $2,406M vs $2,361M
   (+$45M). M5, the only object that has earned the right to disagree with the Street at h=0, says 50.30% /
   +$37M. The spread across methods is 3.74pp, dominated by the driver family (51.2-51.7%) pulling up and M2's
   incremental-margin object (47.9%) pulling down.
2. **The management sentence is a binding constraint that half the methods violate.** "Adjusted EBITDA Margin
   down slightly compared to Q3 2025" caps 3Q26 at the 3Q25 actual **50.085%**. M1, M4, M6 and M2-SARIMA all
   print 51.2-51.7%, i.e. margin *up* 1.1-1.6pp y/y. Either they are wrong or management is sandbagging by more
   than "slightly". M5 (50.30%) is 0.2pp over the cap; M3 (50.09%) sits exactly on it by construction.
3. **4Q26: everyone agrees with the Street except WS31b.** Method median 28.64% vs Street 28.90%. WS31b's three
   forward profiles say 24.7-25.9%, **3-4pp below every method and the Street** — the incumbent repo margin
   model is the outlier and should not be carried into WS23 for 4Q26 without a reconciliation.
4. **FY27 is where the real disagreement is.** Method median $5,566M vs Street $5,766M, **-$200M (-3.5%)**, and
   FY28 $5,679M vs Street $6,603M (-$924M, -14%) on two objects only. On the common revenue leg the method FY27
   margin is 33.31% vs Street's implied 36.45%. Denominator caveat (`20_live_fy_margin_denominator.csv`): the
   harness naive revenue leg sums to $16,709M for FY27 against LSEG's $15,819M (+5.6%); re-based on Street
   revenue the method median FY27 margin is **35.18%**, still 1.27pp below Street. **The margin methods are
   structurally less optimistic than the Street about FY27, and that gap survives the revenue-leg correction.**
5. **The 4Q26 revenue leg is a known wedge.** The harness naive leg gives 4Q26 revenue $3,237M against Street
   $3,162M and the team's bridge v3 $3,178M. Every method's 4Q26 EBITDA **$** inherits ~$60-75M of extra
   revenue, worth roughly $20-25M of EBITDA at a 33% incremental rate; the 4Q26 **margins** in the table are
   only mildly affected (the ratio is less sensitive than the level). WS23 should re-run the LIVE leg on bridge
   v3 before quoting any 4Q26 dollar number.
6. EPS/FCF/GAAP have one supplier each (M7): 3Q26 EPS $2.904 vs Street $2.845; 4Q26 $0.820 vs $0.862;
   3Q26 FCF $1,403M vs Street $1,736M (M7's FCF object failed its backtest — do not quote it);
   3Q26 operating income $1,940M vs Street $1,909M; net income $1,713M vs $1,703M.

---

## 9. Recommended weighting scheme for WS23, with leave-future-out evidence

`build_combination.py` forms every scheme **only from quarters that printed before the quarter being forecast**
(expanding window, minimum 4 prior quarters), so nothing below is a hindsight blend. Evaluation window
2024Q1-2026Q2 (n=10) with a first/second-half split; MAE in pp on `adj_ebitda_margin_pct` at h=0.

| scheme | full (n=10) | 1st half (n=5) | 2nd half (n=5) | bias (full) | ratio to Street (full) |
|---|---|---|---|---|---|
| `ew_three_least_correlated` | **0.749** | **0.436** | 1.062 | -0.085 | 0.571 |
| `m5_dispersion_only` | 0.787 | 0.873 | 0.700 | +0.069 | 0.600 |
| `ew_top3_prior_mae` | 0.974 | 1.318 | **0.631** | -0.142 | 0.743 |
| **`recommended_ws23_60_20_20`** | **0.992** | 1.100 | 0.884 | **+0.155** | **0.757** |
| `m5_60_plus_two_independent_40` | 0.974 | 1.185 | 0.763 | -0.046 | 0.743 |
| `invmae_recency` | 1.088 | 1.364 | 0.811 | +0.051 | 0.830 |
| `ew_all` (all ten objects) | 1.129 | 1.391 | 0.868 | +0.050 | 0.861 |
| `median_all` | 1.292 | 1.664 | 0.921 | +0.122 | 0.986 |
| `_street_baseline` | 1.311 | 1.572 | 1.051 | -1.126 | 1.000 |

**Recommendation for h=0: `recommended_ws23_60_20_20` — 60% M5 `dispersion_conditioned|rw_hl4_med`, 20% M3
`actual_given_guide|rw_hl4_pin`, 20% the driver family averaged (M1 `b_elastic_eq`, M4 `ridge_all_eq`,
M6 `l0_rw`, M2 `sarima|lines_aicc` at 5% each).** Reasons, in order:

1. It beats the Street in **every** split (0.757 / 0.700 / 0.842 of Street MAE) — no other scheme except pure M5
   does that, and pure M5 is one object.
2. Pure M5 has the lower MAE (0.787 vs 0.992) but the largest bias swing between halves (+0.61 -> -0.47pp); the
   blend swings +0.37 -> -0.06. On a single print, a stable small bias is worth more than a lower average MAE.
3. M3 at 20% is explicit insurance: in the 2023 regime break M5's family produced 2.6-4.7pp errors while M3
   produced 0.79pp. M3's errors correlate 0.06 with M5's.
4. The driver family at 20% (not 40%) reflects that its four members are one model (r 0.99) and that it buys the
   least error per parameter.
5. `ew_three_least_correlated` and `ew_top3_prior_mae` each win one half and lose the other; neither is stable
   enough to pre-commit to three weeks before the memo.

**Do not use this blend beyond h=0.** At h=1 M5 fails and the raw Street is unbeaten; use the Street for 4Q26,
with M3 `last_pin` as the Street-independent cross-check. At h=2+ use M2 `incremental_margin|k8_median`
(dollars) or the seasonal-naive-drift floor, and treat FY27 as a scenario, not a forecast.

**LIVE output of the recommended scheme** (`20_combination_live.csv`): 3Q26 **50.39%**, 4Q26 30.17%,
1Q27 19.27%, 2Q27 34.38%, 3Q27 50.05%, 4Q27 30.10%. The 4Q26-onward numbers carry M3's 34.51% 4Q26 outlier at
20% weight and should be replaced by the h=1 rule above (Street 28.90%, method median 28.64%).

---

## 10. Run status of every method (`20_runpy_status.csv`)

All seven method packages and the harness rebuild end to end with exit code 0:

| package | exit | runtime |
|---|---|---|
| `10_harness_margin/run.py` | 0 | 81 s |
| `M1_driver_lines/run.py` | 0 | 69 s |
| `M2_margin_ts/run.py` | 0 | 93-94 s |
| `M3_guide_policy_margin/run.py` | 0 | 11-14 s |
| `M4_alt_augmented/run.py` | 0 | 144-159 s |
| `M5_street_bias/run.py` | 0 | 33-35 s |
| `M6_cycle_flex/run.py` | 0 | 147-199 s |
| `M7_below_ebitda/run.py` | 0 | 175-226 s |
| `10_harness_margin/score.py` (alone, from clean) | 0 | 141 s |

**Incident, reported not fixed.** When this agent started, the *first* WS20 session's shell was still alive and
running the same `run.py` sequence (its log directory was live in the scratchpad). Two sequences therefore ran
concurrently for ~12 minutes. In this agent's sequence `M1_driver_lines/run.py` returned **exit 127** after
registering its 9,632 rows, at the point where it shells out to `score.py` — a collision with the other
sequence's `score.py`, not an M1 defect; the other sequence's M1 returned 0 in 69 s, and M1's registry files are
intact. After both sequences went idle I deleted the five scorer outputs and ran `score.py` alone from clean
(exit 0, 141 s); every table in this note was rebuilt from that run, and all 32 registry files parse with the
expected row counts. **Consequence for the run: several method `run.py` scripts invoke `score.py` internally, so
two agents must never run method packages at the same time.**

---

## 11. Open questions for the discussion round

1. **To M5.** Your 3Q26 call rests on a dispersion ratio clipped at the pre-registered 0.5 floor (3Q26 EBITDA
   sd/mean 0.0085 vs an rw reference of 0.0497). That is an extrapolation outside the fitted range, and the
   backtest never tested a clipped quarter. What does `dispersion_conditioned` print at 3Q26 with the floor at
   0.3 and at 0.7, and how much of the +0.41pp beat is the clip rather than the fitted slope?
2. **To M5.** Your errors correlate 0.80 with the raw Street's and 0.92 across your own three objects. If the
   Street is collectively wrong on 3Q26 in the way it was in 1H25, your correction helped (0.68pp). If it is
   wrong in the way it was in 1H23, your correction cost 4.7pp. Which of those two regimes is 3Q26, and what
   observable would tell us before 5 Nov?
3. **To M3.** Your object is the only independent view in the build (mean pairwise r 0.118) and the best in the
   2023 stress set (0.79pp), but your hindsight share is 0.24 (up to 0.64 for `rw_hl4_prorata`), and
   `rw_hl4`/`last` have rw-W2 wins that vanish in W1. Are the pinned specs (`rw_hl4_pin`, `last_pin`) the ones
   you want quoted, and can the cushion be estimated on more than the FEB/MAY/AUG/NOV bucket so the PIT sample
   stops being four observations?
4. **To M3.** Your LIVE 4Q26 margin is 34.51% against a method median of 28.64% and Street 28.90% — a 5.6pp
   outlier that moves any blend that carries you. Is that the FY-floor-plus-cushion arithmetic implying a very
   strong Q4, or an allocation artefact of the remaining-quarter rule?
5. **To M1, M4 and M6 jointly.** Your h=0 margin errors correlate 0.99-1.00 with each other. Which single one
   should carry the narrative in the memo, and what would the other two have to show to justify their ~35
   combined parameters? Specifically: is there any quarter in 2023Q1-2026Q2 where your points differ by more
   than 0.5pp, and why?
6. **To M1, M4, M6 and M2-SARIMA.** Your LIVE 3Q26 margins (51.2-51.7%) breach the management ceiling implied by
   "margin down slightly compared to Q3 2025" (50.085%). Either your cost lines are too low or the sentence is
   sandbagging. Which line is responsible, and what would it take for 3Q26 margin to print *above* 3Q25?
7. **To M4.** Your warning is confirmed: the object with the best cash lines in the build
   (`lines_aug|best1_rw`, mean line ratio 0.549) is one of the worst on margin (1.101x naive). Is `best1`
   selecting a different alt-signal per line per vintage, and would a single shared signal across lines give up
   line accuracy for margin accuracy?
8. **To M2.** `q_sentence_direction` is the best Street-independent object at h=0 in W2 ($ MAE 37.6M) and
   ranks 68th in W1-equal, and it has n=1 at h=1. Is the object usable at all outside quarters with a
   directional sentence, and should the h=1/h=2 rows be withdrawn rather than registered with n=1?
9. **To M2.** `incremental_margin|k8_median` is the only object that survives both windows at h=2 in dollars.
   Does it have a LIVE 1Q27-4Q27 path you are willing to stand behind, given the FY27 method median is $200M
   below Street?
10. **To M7.** Your quarterly FCF object fails its pre-registered pass line (1.02x naive W1, 0.93x W2) and
    `fcf_margin_pct` is worse than naive in both windows. Do you want the FCF rows withdrawn from the quotable
    set, and is the annual FCF result (which passed) the only FCF claim the memo should make?
11. **To M7.** Your `eps|ebitda_known` specs are oracles and I excluded them; on `ebitda_pit` you are within
    2-4% of Street in W2 and ahead in W1. If WS23 feeds the recommended margin blend into your bridge instead of
    the harness baseline, what changes in the 3Q26 EPS number, and does your interval widen?
12. **To WS31b / WS30 (via the orchestrator).** The WS31b forward profiles put 4Q26 margin at 24.7-25.9%,
    3-4pp below every method in this build and below the Street. WS30's walk needs the same check. Which is
    wrong, and does the FY26 "at least 35.5%" floor still bind under either?
13. **To WS21.** Not a leakage claim, but flagged for your audit: 25 registered spec variants condition on a
    realised driver (`revknown`, `nightsknown`, `ebitda_known`). They are correctly labelled in the notes, but
    they sit in the same `scoreboard_margin.csv` rows as forecasts and they top several rankings. Recommend a
    `is_oracle` column in the harness rather than a naming convention.

---

## 12. Which registry state this board reflects, and how to refresh it

Every table above was built from `score.py` run alone from clean at **2026-09-14 03:52-03:55 UTC**, over the
registry as it stood then (32 objects, row counts verified against the pre-run backup).

**While this note was being written, the WS22 discussion round began re-registering methods** — the
`*_pre_discussion.csv.bak` backups appear at 23:50:59 local, then M3 23:54, M1 23:55, M2 23:56, M4 00:01,
M6 00:03. M1 has already dropped `e_revknown_rw` from the registry and routed it to
`M1_driver_lines_oracle_diagnostic.csv` (a fix labelled "WS22 discussion R03"), and M4 has added a
`04_signal_knowable_from.csv` gate (R04). **Those two changes implement exactly what section 0 rule 2 and open
question 13 asked for**, so the direction of this board is unaffected: every oracle spec was already excluded
from every ranking here, and the M5 / M3 / M7 objects that carry the recommendation were not touched.

Refresh is one command each, in this order, and must be run with **no other agent running a method package**
(they invoke `score.py` internally, which is what produced the exit-127 collision in section 10):

```bash
py -3.13 analysis/src/margin_build/10_harness_margin/score.py
py -3.13 analysis/src/margin_build/20_scoreboard/run.py
```

Everything in `data/processed/margin_build/20_scoreboard/` and the digest regenerate in about 60 s. The numbers
quoted in sections 1-9 of this note should be re-read off the refreshed CSVs before they go into the memo; the
one number that cannot move is the LIVE consensus (LSEG 3Q26 $2,361.5M / 49.78%, 11 Sep).

---

## For the model

Series and parameters WS20 supplies to WS23 (all PIT, all from
`data/processed/margin_build/20_scoreboard/`):

| name | value | unit | source |
|---|---|---|---|
| Recommended h=0 margin combination | 60% M5 `dispersion_conditioned\|rw_hl4_med`, 20% M3 `actual_given_guide\|rw_hl4_pin`, 20% driver family (M1 `b_elastic_eq`, M4 `ridge_all_eq`, M6 `l0_rw`, M2 `sarima\|lines_aicc`, 5% each) | weights | `20_combination_weights_live.csv` |
| Leave-future-out MAE of that combination | 0.992 (full), 1.100 (1H), 0.884 (2H) | pp | `20_combination_scores.csv` |
| Leave-future-out RMSE of that combination | 1.121 (full), 0.994 (2H) | pp | same |
| 3Q26 adj EBITDA margin, recommended combination | 50.39 | % | `20_combination_live.csv` |
| 3Q26 adj EBITDA margin, method median (preferred specs) | 50.19 | % | `20_live_spread.csv` |
| 3Q26 adj EBITDA $, method median | 2,406.1 | USD m | same |
| 4Q26 margin / $, method median (use Street at h=1) | 28.64 / 910.3 | % / USD m | same |
| FY26 adj EBITDA $, method median | 5,129.9 | USD m | same |
| FY27 adj EBITDA $, method median | 5,565.7 | USD m | same |
| FY27 margin on Street revenue | 35.18 | % | `20_live_fy_margin_denominator.csv` |
| 80% / 90% interval for the 3Q26 margin (do NOT use registry quantiles) | +/-1.6 / +/-2.0 | pp | section 5, from the combination RMSE |
| h=1 rule | use the Street baseline; M3 `last_pin` as the independent cross-check | — | section 1 |
| h=2+ rule | M2 `incremental_margin\|k8_median` ($) or seasonal-naive-drift; FY27 is a scenario | — | section 1 |

## For the 5 Nov card

- Consensus to beat: **LSEG 3Q26 adj EBITDA $2,361.5M / 49.78% margin** (11 Sep, n=36 estimates, sd $20.0M).
- WS20 combination: **50.39% / ~$2,410M**, i.e. **+0.6pp / +$50M**, but capped in spirit by management's
  "down slightly vs 3Q25" = 50.085%. The honest statement is "at or slightly above the top of what the
  guidance sentence allows, and above consensus".
- Model-uncertainty band across the seven methods on 3Q26: **47.93% - 51.67%** (3.74pp), $2,299M - $2,482M.
- 4Q26: methods and Street agree (28.6% vs 28.9%); WS31b's 24.7-25.9% is the outlier to reconcile.
- FY27 is the differentiated call: methods $5,566M vs Street $5,766M, -3.5%.

---

## RESUME

Everything WS20 was asked for is on disk and rebuilds with
`py -3.13 analysis/src/margin_build/20_scoreboard/run.py` (exit 0). The next agent (WS22, the discussion round)
should send section 11's numbered questions to the named methods — questions 1, 2 and 4 are the ones that can
change the 5 Nov number, and questions 5 and 6 are the ones that can shrink the build. Two items need an owner
outside the discussion: (a) the LIVE revenue leg for 4Q26 and FY27 is the harness naive rule, which is $75M
above bridge v3 for 4Q26 and 5.6% above Street for FY27 — WS23 should re-run every method's LIVE dollar row on
the bridge v3 path before quoting a dollar number; (b) WS31b's 4Q26 margin profile (24.7-25.9%) contradicts the
entire build and the Street, and needs a reconciliation note before the incumbent model is cited anywhere.
WS23 should also build its own interval from section 5 rather than from the registered quantiles, which are
too wide in every method (mean 80% coverage 0.91-1.00).
