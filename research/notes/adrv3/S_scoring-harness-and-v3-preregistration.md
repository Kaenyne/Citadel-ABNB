# S. Scoring harness (integer-fair ex-FX and unrounded dollar ADR targets) and the v3 pre-registration

- **Date:** 2026-09-11. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Question:** J3's card v2 tied naive (ratio 0.994 on 1Q24-2Q26, 1.042 on 2Q24-2Q26) on a target that is rounded to whole points while the model is not. Does a scoring that treats both sides alike change the picture, and does the v3 residual rule pass a criterion written down before the new harness ran?
- **Scripts:** `analysis/src/adrv3/S1_scoring.py` (importable harness, no side effects), `analysis/src/adrv3/S2_rescore_v2.py` (`py -3.13`, offline, seconds).
- **Outputs (`data/processed/adrv3/S/`):** `reproduction_check_vs_J3.csv`, `rescore_v2.csv`, `rescore_v2_summary.csv`, `harness_change_isolation.csv`, `v3_preregistered_result.csv`, `walk_forward_paths.csv`, `error_attribution_v3.csv`.
- **Does not redo:** the residual rules, mix terms, FX estimators or card v2 (J3 and `data/processed/adrq3/J/` are untouched and are the v2 record).

---

## 1. Bottom line

1. **The v3 residual rule, last-quarter residual (`last_q`), is a post-hoc promotion.** It was not J3's pre-registered v2 rule (that was `persistence`, the mean of the last two residuals). It was the best rule in J3's sensitivity table (ratio 0.89 vs naive, below 1 in all ten jackknife samples) and the BRIEF promoted it to the v3 rule on 11 September, before this harness existed and before any Phase 1 result. Because the rule was chosen after seeing the table, the pass criterion was tightened for it: ratio vs naive below 1.0 on both windows and jackknife maximum below 1.0, on the unrounded dollar target under both FX estimators, rather than v2's "ratio below 1" on one window. Everything in this note is the pre-registered rule scored under that tightened criterion; no rule or threshold was changed after the numbers were seen.

2. **The harness reproduces the v2 record exactly.** Rebuilt from the same inputs (H components, seats dilution, 07 interaction, H backtest) and scored in J3's mode, all 32 rows of `card_v2_backtest.csv` match to a maximum absolute difference of 0.000000 on RMSE, the three ratios and both jackknife ends (descriptive): persistence measured-mix 0.903 vs naive 0.908 (0.994), last_q 0.807 (0.889), on 1Q24-2Q26.

3. **v3 verdict: PASS on target 2 (reported dollar ADR y/y, unrounded), under both FX estimators and the midpoint, on both windows, with every jackknife sample below 1 (descriptive, walk-forward 1Q24-2Q26 n 10 and 2Q24-2Q26 n 9).** last_q with measured mix: eur 0.916 (jackknife 0.871 to 0.969) and 0.905 (0.826 to 0.989); baskets 0.876 (0.786 to 0.918) and 0.871 (0.746 to 0.924); midpoint 0.893 (0.825 to 0.945) and 0.882 (0.768 to 0.955). RMSE 0.78 to 1.10 pp against naive 0.90 to 1.20 pp. Sign accuracy of the change from naive 0.78 to 0.90. The v2 persistence rule fails the same criterion (2 of 4 checks: it passes under baskets, 0.892 and 0.905, and fails under eur, 0.983 and 1.022).

4. **Target 1 (ex-FX, integer-fair) does not pass and is reported alongside: 0.985 (jackknife 0.921 to 1.080) and 1.080 (1.000 to 1.183).** Rounding the model's ex-FX to whole points before scoring removes the edge J3 saw. The rounding cost is 0.09 pp of RMSE on the first window and it rests on a knife edge: the 2Q25 model value is 1.504 and rounds up to 2 against a disclosed 1; a value 0.005 lower would round to 1, make that quarter exact and put the ratio at about 0.92. On the integer target, in other words, the rule and naive are indistinguishable at n 10.

5. **The harness change alone does not move the verdict; the rule change does, but only under one of the two estimators.** Same rule, three scorings (`harness_change_isolation.csv`): last_q was 0.889 / 0.881 with jackknife maxima 0.937 / 0.950 on J3's target (it would have met the strict criterion there too), fails on target 1 (0.985 / 1.080) and passes on target 2 (0.876 to 0.916). Persistence was 0.994 / 1.042 on J3's target, fails target 1 (1.155 / 1.291), and on target 2 passes under baskets only. So: the scoring fix (target 2) leaves last_q where J3 found it and lifts persistence from a coin flip to a pass under baskets and a fail under eur; the promotion to last_q is what makes the result hold under both estimators. The reader should treat the pass as a rule result on the dollar target, not a scoring artefact, and should also see that the same rule does not beat naive on the integer ex-FX target.

6. **Where the error now sits.** For the last_q rule on target 2 (midpoint FX), the per-quarter error is the residual-rule error to within the two small fills: residual-rule RMSE 0.86 pp, new-business-and-interaction fill 0.18 pp (always positive, 0.06 to 0.30), FX-estimator error 0.33 pp midpoint (0.46 eur, 0.42 baskets), disclosed identity gap 0.04 pp or less. The largest quarters are the turns: 3Q24 +1.63 (residual rule +1.15, the 2Q24 residual of 3.2 carried into a 2.1 quarter; FX +0.42), 1Q24 -1.61 (residual -1.42, the 4Q23 residual of 0.8 carried into 2.3), 3Q25 -1.25 (residual -0.92, FX -0.54), 2Q24 -0.91 (residual -0.98). The rule is late by 0.5 to 1.4 pp in every acceleration quarter (1Q24, 2Q24, 3Q25, 4Q25, 1Q26) and early by 1.15 in the one deceleration (3Q24). That is the target for K (dating the 1H26 step), L (regional rule) and M (fifth mix term): a residual rule that reads a turn one quarter sooner.

7. **Two caveats the reader should carry.** First, the reported dollar y/y is within 0.04 pp of disclosed integer ex-FX plus disclosed FX in every quarter (H solved the FX effect from the reported number for most quarters, so this holds by construction). Target 2 therefore does not reveal an unrounded ex-FX; what it does is score the ex-FX model plus an FX estimate against a continuous number without charging the model a rounding it cannot control, while the naive keeps its integer. Second, because the FX estimator error is common to model and naive under target 2, it does not cancel in the ratio: the cross term between FX error and ex-FX error moves the ratio by about 0.03 either way (eur 0.916, baskets 0.876, J3's ex-FX-only 0.889). The eur estimator is the harder case and is the one that binds.

---

## 2. Tables

### 2.1 Reproduction check against the v2 record (descriptive)

S1 in J3 mode (unrounded model ex-FX against disclosed integer ex-FX, naive over every window quarter) against `data/processed/adrq3/J/card_v2_backtest.csv`, 32 rows (3 benchmarks, H route a, 12 v2 variants, two windows). Max abs diff over RMSE, ratio vs naive, vs prior year, vs AR(1), jackknife min and max: 0.000000.

| model | window | RMSE S1 | RMSE J3 | ratio S1 | ratio J3 |
|---|---|---|---|---|---|
| naive last disclosed ex-FX | 1Q24-2Q26 | 0.908 | 0.908 | 1.000 | 1.000 |
| v2 measured mix, persistence | 1Q24-2Q26 | 0.903 | 0.903 | 0.994 | 0.994 |
| v2 measured mix, last_q | 1Q24-2Q26 | 0.807 | 0.807 | 0.889 | 0.889 |
| naive | 2Q24-2Q26 | 0.816 | 0.816 | 1.000 | 1.000 |
| v2 measured mix, persistence | 2Q24-2Q26 | 0.851 | 0.851 | 1.042 | 1.042 |
| v2 measured mix, last_q | 2Q24-2Q26 | 0.719 | 0.719 | 0.881 | 0.881 |

### 2.2 The v3 pre-registered result (`v3_preregistered_result.csv`, descriptive, walk-forward)

Model: measured mix (realised quarter-t geographic, size and LOS terms, the upper bound on workstream I) + prior-calendar-year new business and interaction + last-quarter residual. Knowable before print: no (the prior-quarter residual is only known at the print of that quarter; the rule uses prior residuals only).

| target | FX | window | n | RMSE | naive RMSE | ratio | jackknife | below 1 | sign acc. | in criterion | met |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 reported $ y/y | eur | 1Q24-2Q26 | 10 | 1.099 | 1.199 | **0.916** | 0.871 to 0.969 | 10/10 | 0.80 | yes | yes |
| 2 reported $ y/y | eur | 2Q24-2Q26 | 9 | 0.935 | 1.033 | **0.905** | 0.826 to 0.989 | 9/9 | 0.78 | yes | yes |
| 2 reported $ y/y | baskets | 1Q24-2Q26 | 10 | 0.831 | 0.949 | **0.876** | 0.786 to 0.918 | 10/10 | 0.90 | yes | yes |
| 2 reported $ y/y | baskets | 2Q24-2Q26 | 9 | 0.783 | 0.898 | **0.871** | 0.746 to 0.924 | 9/9 | 0.89 | yes | yes |
| 2 reported $ y/y | midpoint | 1Q24-2Q26 | 10 | 0.932 | 1.043 | 0.893 | 0.825 to 0.945 | 10/10 | 0.80 | alongside | |
| 2 reported $ y/y | midpoint | 2Q24-2Q26 | 9 | 0.822 | 0.932 | 0.882 | 0.768 to 0.955 | 9/9 | 0.78 | alongside | |
| 1 ex-FX integer-fair | none | 1Q24-2Q26 | 10 | 0.894 | 0.908 | 0.985 | 0.921 to 1.080 | 8/10 | 0.29 | alongside | no |
| 1 ex-FX integer-fair | none | 2Q24-2Q26 | 9 | 0.882 | 0.816 | 1.080 | 1.000 to 1.183 | 0/9 | 0.17 | alongside | no |

**Verdict: PASS (4 of 4 checks).** Ratios vs prior year 0.19 to 0.27 and vs AR(1) 0.28 to 0.41 on target 2; on target 1, 0.49 to 0.51 and 0.71 to 0.76.

### 2.3 Every J3 rule rescored, measured mix (ratio vs naive; jackknife min to max; drop-one samples below 1)

Rows are residual rules with measured mix. Benchmarks sit at the bottom. `rescore_v2_summary.csv` carries the trailing-4q-mix variants and H route a as well.

| rule | t1, 1Q24-2Q26 | t1, 2Q24-2Q26 | t2 eur, 1Q24- | t2 eur, 2Q24- | t2 baskets, 1Q24- | t2 baskets, 2Q24- | t2 mid, 1Q24- | t2 mid, 2Q24- |
|---|---|---|---|---|---|---|---|---|
| **last_q (v3, pre-registered)** | 0.985 [0.92-1.08] 8/10 | 1.080 [1.00-1.18] 0/9 | **0.916 [0.87-0.97] 10/10** | **0.905 [0.83-0.99] 9/9** | **0.876 [0.79-0.92] 10/10** | **0.871 [0.75-0.92] 9/9** | 0.893 [0.82-0.94] 10/10 | 0.882 [0.77-0.96] 9/9 |
| persistence (v2) | 1.155 [0.98-1.29] 1/10 | 1.291 [1.10-1.41] 0/9 | 0.983 [0.90-1.02] 5/10 | 1.022 [0.90-1.09] 3/9 | 0.892 [0.78-0.95] 10/10 | 0.905 [0.77-0.99] 9/9 | 0.945 [0.85-1.00] 10/10 | 0.971 [0.83-1.06] 6/9 |
| trailing_4q (H) | 1.101 [0.91-1.29] 1/10 | 1.291 [1.10-1.41] 0/9 | 0.991 [0.84-1.17] 6/10 | 1.174 [0.99-1.33] 1/9 | 0.848 [0.75-0.95] 10/10 | 0.943 [0.84-1.10] 7/9 | 0.934 [0.82-1.09] 7/10 | 1.087 [0.94-1.26] 1/9 |
| trailing_8q | 1.044 [0.78-1.22] 2/10 | 1.225 [0.91-1.34] 1/9 | 1.009 [0.80-1.20] 4/10 | 1.197 [0.94-1.34] 1/9 | 0.912 [0.81-1.01] 8/10 | 1.014 [0.91-1.16] 4/9 | 0.970 [0.80-1.13] 7/10 | 1.131 [0.93-1.29] 1/9 |
| ar1_residual (n 8, from 3Q24) | 1.000 [0.89-1.12] 2/10 | 1.000 [0.89-1.12] 2/9 | 1.051 [0.90-1.18] 2/10 | 1.051 [0.90-1.18] 2/9 | 0.907 [0.81-1.03] 9/10 | 0.907 [0.81-1.03] 8/9 | 0.988 [0.88-1.13] 7/10 | 0.988 [0.88-1.13] 6/9 |
| blend | 0.921 [0.85-1.00] 9/10 | 1.000 [0.91-1.10] 2/9 | 0.963 [0.85-1.08] 8/10 | 1.081 [0.94-1.18] 1/9 | 0.843 [0.77-0.91] 10/10 | 0.913 [0.84-1.00] 8/9 | 0.912 [0.83-1.01] 9/10 | 1.013 [0.91-1.12] 4/9 |
| naive RMSE, pp | 0.908 | 0.816 | 1.199 | 1.033 | 0.949 | 0.898 | 1.043 | 0.932 |
| prior year, ratio | 1.923 | 2.217 | 3.396 | 4.080 | 4.292 | 4.690 | 3.903 | 4.521 |
| AR(1) expanding, ratio | 1.393 | 1.414 | 2.237 | 2.737 | 2.828 | 3.147 | 2.571 | 3.033 |

The ar1_residual rule starts at 3Q24 (six residuals needed), so its two windows are the same eight quarters; the naive is aligned to the model's quarters, which is why its ratios coincide. With trailing-4q mix (H's rule) every rule fails every target: ratios 1.08 to 1.63 on target 1, 0.98 to 1.44 on target 2, no jackknife maximum below 1.05. H route a: 1.42 to 1.58 on J3's target and no better here. Only last_q meets the strict criterion under every FX estimator; blend and trailing_4q meet it under baskets only on the first window.

### 2.4 Error attribution, last_q rule (`error_attribution_v3.csv`, descriptive, pp)

Target 2, midpoint FX. Total = residual rule + new-business-and-interaction fill + FX estimator + disclosed identity gap (checked to 1e-9). Target 1 total = residual rule + fill + rounding.

| quarter | t2 total | t2 naive | residual rule | nb + interaction fill | FX est. (mid) | FX est. (eur) | FX est. (baskets) | t1 total | t1 rounding |
|---|---|---|---|---|---|---|---|---|---|
| 1Q24 | -1.61 | -1.75 | -1.42 | +0.06 | -0.21 | -0.64 | +0.23 | -1 | +0.36 |
| 2Q24 | -0.91 | -0.99 | -0.98 | +0.06 | +0.03 | -0.18 | +0.24 | -1 | -0.08 |
| 3Q24 | +1.63 | +1.42 | +1.15 | +0.06 | +0.42 | +0.46 | +0.39 | +1 | -0.21 |
| 4Q24 | -0.50 | +0.12 | -0.68 | +0.06 | +0.12 | +0.14 | +0.10 | -1 | -0.38 |
| 1Q25 | +0.42 | +0.71 | +0.53 | +0.18 | -0.28 | -0.02 | -0.54 | +1 | +0.29 |
| 2Q25 | +0.16 | -0.34 | +0.33 | +0.18 | -0.32 | -0.06 | -0.59 | +1 | +0.50 |
| 3Q25 | -1.25 | -1.51 | -0.92 | +0.18 | -0.54 | -0.40 | -0.67 | -1 | -0.26 |
| 4Q25 | -0.17 | -0.48 | -0.88 | +0.18 | +0.56 | +0.65 | +0.46 | -1 | -0.30 |
| 1Q26 | -0.67 | -1.28 | -0.68 | +0.30 | -0.25 | -0.55 | +0.06 | 0 | +0.38 |
| 2Q26 | -0.33 | -0.16 | -0.47 | +0.30 | -0.16 | -0.71 | +0.40 | 0 | +0.17 |
| RMSE | 0.93 | 1.04 | 0.86 | 0.18 | 0.33 | 0.46 | 0.42 | 0.89 | 0.31 |

FX estimator error against the disclosed effect on 1Q24-2Q26 (descriptive): eur RMSE 0.455 bias -0.13; baskets 0.416 bias +0.01; midpoint 0.332. The B note's 0.46 / 0.54 was on 2Q22-2Q26; on the scored window the baskets estimator is the slightly better one and the midpoint is better than either. The disclosed identity gap (reported minus integer ex-FX minus disclosed FX) is -0.04 to +0.03.

---

## 3. Method

**Inputs (sourced).** `data/processed/q3nowcast/H/adr_history_components.csv` for adr_usd, disclosed ex-FX (whole points), disclosed FX effect, the residual and the five components, 1Q23 to 2Q26; `data/processed/overnight2/B/B_adr_fx_estimator_backtest.csv` for est_from_eur and est_from_regional_baskets by quarter (labels 2024Q1 mapped to 1Q24); `data/processed/adr/15_seats_dilution_annual.csv` and `07_full_decomposition.csv` for the prior-calendar-year new-business and interaction fills, exactly as J3; `data/processed/q3nowcast/H/adr_exfx_backtest.csv` for H route a. All read from the worktree copies, which are the committed main-tree files.

**Target 1, ex-FX integer-fair.** Actual = disclosed ex-FX (integer). Model ex-FX rounded to the nearest whole point, halves away from zero (2.5 to 3, -0.5 to -1; numpy's default is banker's rounding and is not used). Naive = last disclosed ex-FX; prior year = disclosed ex-FX four quarters earlier; AR(1) = expanding np.polyfit on the disclosed series strictly before t with at least four training quarters (J3's convention: three lag pairs at 1Q24), prediction rounded the same way as the model so every continuous forecast faces the same rounding. Exact halves occur twice, both in the trailing-4q-mix variants at 1Q24 (trailing_4q and trailing_8q residual, 1.5 pp, rounded to 2 against a disclosed 2); none occur in the measured-mix paths or the AR(1) benchmark, so the v3 rule's target-1 numbers do not depend on the half convention.

**Target 2, reported dollar ADR y/y, unrounded.** Actual = 100 x (adr_usd[t] / adr_usd[t-4] - 1), adr_usd carrying two decimals; it agrees with H's adr_yoy_reported_pp to 1e-9 where both exist, and H's column (on H's 2022 ADR base) supplies the 2023 values that the AR(1) and prior-year benchmarks need. Model = ex-FX model + FX estimator for quarter t; naive = last disclosed ex-FX + the same FX estimator for quarter t; prior year = reported y/y four quarters earlier; AR(1) = expanding fit on the reported series before t, unrounded. Three estimators: eur, baskets, midpoint (their mean). The disclosed fx_effect_pp is never used as the model's or the naive's FX: it is only known at the print, and using it would hand the model the one number the print resolves. Both estimators are knowable at quarter end (WS-B), so the FX term does not change the knowable flag.

**Per model, target, window, estimator.** n, RMSE, bias, MAE, RMSE of naive, prior year and AR(1) on the model's quarters, the three ratios, sign accuracy of the predicted change from naive over quarters where the actual change from naive is non-zero (J3's definition), jackknife drop-one min and max of the ratio vs naive and the count of samples below 1, and the knowable-before-print flag the caller supplies verbatim. Windows 1Q24-2Q26 (n 10) and 2Q24-2Q26 (n 9). Where a model has fewer quarters (ar1_residual, H route a) the naive is aligned to the model's quarters; J3 scored the naive on all window quarters, and the reproduction check uses J3's convention so the record matches.

**v2 paths.** `v2_components()` rebuilds J3's per-quarter blocks (measured mix = realised geo + size + LOS; trailing-4q mix; prior-year new business and interaction; the six residual rules on residual history strictly before t) and `v2_model_paths()` assembles the twelve variants. The residual rules are copied logic, not an import of J3, so J3 stays untouched.

**Pre-registered pass.** `preregistered_pass()` filters the target-2 rows for eur and baskets on both windows and requires ratio vs naive below 1.0 and jackknife maximum below 1.0 on all four; target 1 and the midpoint rows are returned alongside and are not part of the pass. The criterion string is written into `v3_preregistered_result.csv`.

**Error attribution.** With measured mix, model ex-FX minus disclosed integer ex-FX is exactly (rule minus actual residual) plus (prior-year fills minus actual new business and interaction), because H defines the residual so that components plus residual equal the disclosed integer. Target 1 adds the rounding step; target 2 adds (FX estimate minus disclosed FX) and the disclosed identity gap (reported minus integer ex-FX minus disclosed FX, sign chosen so the pieces sum to the total). The sum is asserted to 1e-9 per row.

---

## 4. What this can and cannot identify

- **The scoring fix and the rule change are separable, and the note separates them.** Same rule on three scorings: last_q passes the strict criterion on J3's target and on target 2 and fails on target 1; persistence fails J3's target and target 1 and splits target 2 by estimator. The v3 pass is a rule result on the dollar target. It is not a pass on the integer ex-FX target, and a reader who cares about the ex-FX sentence in the letter should use the target-1 line: indistinguishable from naive at n 10.
- **Target 2 is not an unrounded ex-FX.** Reported y/y equals integer ex-FX plus disclosed FX to within 0.04 pp in every quarter, by construction of the H reconstruction (FX solved from the reported number). What target 2 removes is the charge for rounding the model, not the rounding in the data. The disclosed FX effect (one decimal) absorbs the ex-FX rounding residue, which is why the "FX-estimator error" column in the attribution includes it.
- **The FX estimator does not cancel.** It is common to model and naive but enters the ratio through its cross term with the ex-FX error, worth about 0.03 either way. That is why both estimators are in the criterion and why the eur case (0.916, 0.905, jackknife to 0.989) is the binding one. A 0.99 jackknife maximum on the eur second window is a pass by 0.011; P should report it as such.
- **Ten quarters, one turn each way.** The rule is late in five accelerations and early in one deceleration; the pass comes from being less late than "no change" in the accelerations. A regime with two decelerations in ten quarters would score differently. The jackknife bounds this within the sample and cannot speak to a different sample.
- **Measured mix is an upper bound on workstream I.** The paths use the realised quarter-t geographic, size and LOS terms; I's real-time terms carry error the rescored numbers do not. K, L and M inherit this: pass or fail on the S harness with measured mix says what a perfect in-quarter measurement would deliver.
- **The rounding argument cuts both ways.** J section 4 argued that naive is hard to beat because the target is rounded; target 1 shows that rounding the model as well does not restore the edge, and that the target-1 ratio can move 0.06 on a 0.005 pp perturbation of one quarter. A whole-point target with quarterly changes of 0 or 1 is not a usable discriminator at n 10, and the pitch should not lean on it.
- **The AR(1) benchmark is weak on target 2** (2.2 to 3.1 times naive) because the reported series is dominated by FX swings of -1.9 to +5.0 pp that an AR(1) on its own history cannot anticipate; the ratio vs AR(1) is reported for completeness and is not evidence about the model.

---

## 5. Next evidence

1. **K, L, M score on this harness, measured mix, both targets, and report the four target-2 checks plus target 1 alongside.** A term passes only if it beats last_q, not naive, on both windows (BRIEF): compare its `ratio_vs_naive` with last_q's 0.916 / 0.905 (eur) and 0.876 / 0.871 (baskets), and its jackknife maximum with 0.969 / 0.989 and 0.918 / 0.924.
2. **N's FX memo should use the scored-window errors** (eur 0.455, baskets 0.416, midpoint 0.332 on 1Q24-2Q26) alongside B's longer-window numbers; the midpoint is the better estimator on both windows here.
3. **The 5 November print scores the rule on target 2.** The 3Q26 reported y/y from adr_usd is the actual; the rule's prediction, the naive and the FX estimates are all fixed before the print. P's score-sheet script should write the four target-2 checks and the target-1 line from `walk_forward_paths.csv` extended by one row.
4. **A same-listing realised-rate series remains the only thing that could see a turn sooner than the last-quarter rule** (J section 5); nothing in this note changes that.

---

## 6. How to call S1 from K, L, M and P

`analysis/src/adrv3/S1_scoring.py` imports with no side effects. From a script in `analysis/src/adrv3/`:

```python
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import S1_scoring as S
```

- `S.score(ex_fx_model: pd.Series, name: str, knowable: str, root=None, targets=S.TARGETS, fx_estimators=S.FX_ESTIMATORS, windows=None, align_naive_to_model=True) -> pd.DataFrame`. `ex_fx_model` is the model's ex-FX ADR y/y in pp indexed by quarter label (`'1Q24'` to `'2Q26'`; missing quarters count as missing). Returns one row per (target, window, fx_estimator): two rows for target 1 (fx_estimator `none`), six for target 2. Columns: model, target, window, fx_estimator, fx_estimator_source, n, rmse_pp, bias_pp, mae_pp, rmse_naive_pp, rmse_prior_year_pp, rmse_ar1_pp, ratio_vs_naive, ratio_vs_prior_year, ratio_vs_ar1, sign_accuracy_vs_naive, jackknife_ratio_min, jackknife_ratio_max, jackknife_below_1, jackknife_n, knowable_before_print, scoring.
- `S.exfx_from_residual(residual_pred: pd.Series, mix_variant="measured", extra_pp=None, root=None) -> pd.Series`. Builds the ex-FX path J3-style from a residual prediction (K and L: pass your residual model's per-quarter walk-forward prediction, strictly out of sample). `extra_pp` adds a further per-quarter term (M: the new-listing premium times E's share) on top of the measured mix.
- `S.preregistered_pass(df: pd.DataFrame, model: str = "v2_measured_last_q") -> dict` with keys pass, verdict, criterion, checks (the four target-2 rows), alongside (target 1 and midpoint), n_checks, n_checks_met. `S.pass_table(result)` flattens it to a DataFrame. To test a K, L or M term against last_q rather than naive, compare the term's rows with `S.score(S.v2_model_paths()["v2_measured_last_q"], ...)` on ratio_vs_naive and jackknife_ratio_max; both are on the same naive so the comparison is direct.
- `S.score_benchmarks(root=None, ...)` returns the naive, prior-year and AR(1) rows in the same shape. `S.paths(models: dict[str, pd.Series], ...)` returns per-quarter paths in scored units. `S.v2_model_paths()` returns every J3 variant (columns `S.V2_MODELS` plus `h_route_a`); `S.v2_components()` the building blocks (mix, fills, actual residual, every residual rule per quarter). `S.target_frame(target, fx_estimator)` exposes actual, naive, prior_year and ar1 per quarter. `S.reproduce_j3()` returns the comparison table and a boolean and should be re-run if any input file changes.
- Constants: `S.TARGETS`, `S.FX_ESTIMATORS`, `S.WINDOWS`, `S.RULES`, `S.V3_RULE_MODEL`, `S.V2_RULE_MODEL`, `S.KNOWABLE_V2`. Quarter labels are H style (`1Q24`); `S.b_to_h_quarter('2024Q1')` converts B style.

---

## 7. Files

| File | Contents |
|---|---|
| `analysis/src/adrv3/S1_scoring.py` | the harness: inputs, both targets, benchmarks, scoring with jackknife, v2 path rebuild, reproduction check, pre-registered pass function |
| `analysis/src/adrv3/S2_rescore_v2.py` | reproduction check, rescore of every J3 variant and benchmark, isolation table, verdict, paths, attribution |
| `data/processed/adrv3/S/reproduction_check_vs_J3.csv` | 32 rows, S1 vs `card_v2_backtest.csv` per metric with absolute differences |
| `data/processed/adrv3/S/rescore_v2.csv` | 128 rows: 16 models (3 benchmarks, H route a, 12 v2 variants) x 2 targets x 2 windows x (1 or 3) FX estimators |
| `data/processed/adrv3/S/rescore_v2_summary.csv` | the same rows, compact columns, with a strict-criterion flag per row |
| `data/processed/adrv3/S/harness_change_isolation.csv` | six models under J3's scoring, target 1 and target 2 (three estimators), both windows |
| `data/processed/adrv3/S/v3_preregistered_result.csv` | the last_q rule: four criterion rows plus target 1 and midpoint alongside, verdict PASS |
| `data/processed/adrv3/S/walk_forward_paths.csv` | 40 rows (target x estimator x quarter): actual, naive, prior year, AR(1), every model in scored units |
| `data/processed/adrv3/S/error_attribution_v3.csv` | 40 rows: last_q error split per quarter under target 1 and target 2 (three estimators) |
