# L. Regional ex-FX ADR forecast with walk-forward proxy selection: does a region-by-region build beat the last-quarter rule?

- **Date:** 2026-09-11. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Question:** J2 tested nine price proxies against the blended residual and blended ex-FX ADR and found nothing that beats naive, with one marginal survivor (euro-area HICP accommodation services against EMEA ex-FX, walk-forward ratio 0.91, n 10, no jackknife). Does a region-by-region forecast of ex-FX ADR, each region on its own rule or proxy chosen strictly on data before the scored quarter, aggregated on nights shares into the blended series, beat the pre-registered last-quarter residual rule (`last_q`) on the S harness?
- **Pre-registered criterion (BRIEF, L):** the regional aggregate beats `last_q` on the S harness on both windows. Applied as: on target 2 (reported dollar ADR y/y, unrounded), under both the eur and baskets FX estimators, on both windows (1Q24-2Q26 n 10, 2Q24-2Q26 n 9), the aggregate's ratio vs naive is below `last_q`'s (0.916 / 0.905 eur, 0.876 / 0.871 baskets). Four checks. Jackknife and target 1 reported alongside.
- **Scripts:** `analysis/src/adrv3/L0_common.py` (shared: panel, identity, candidates, out-of-sample prediction, selection), `L1_regional_panel.py`, `L2_regional_tests_selection.py`, `L3_aggregate_score.py`, `L4_regional_nowcast.py` (`py -3.13`, offline, L2 about a minute for the permutation tests, the rest seconds).
- **Outputs (`data/processed/adrv3/L/`):** `L1_regional_panel.csv`, `L1_identity_check.csv`, `L2_proxy_tests.csv`, `L2_candidate_oos_paths.csv`, `L2_regional_selection.csv`, `L2_selection_tables.csv`, `L3_scores.csv`, `L3_pass.csv`, `L3_walk_forward_paths.csv`, `L3_regional_paths.csv`, `L3_regional_scores.csv`, `L3_error_attribution.csv`, `L3_paired_jackknife.csv`, `L4_regional_nowcast.csv`, `L4_aggregate_nowcast.csv`.
- **Does not redo:** the S harness, J2's proxy pulls and blended tests, H's regional identity, I's mix terms. Nothing under `analysis/src/adrq3/`, `analysis/src/adrv3/S*`, `data/processed/adrq3/` or `data/processed/adrv3/S/` was touched.

---

## 1. Bottom line

1. **FAIL.** The primary model (`L_wf`: walk-forward pick per region, aggregated on year-ago dollar weights, plus H's measured geo term) scores 1.198 and 1.324 vs naive under eur and 1.033 and 1.078 under baskets on target 2 (descriptive, walk-forward 1Q24-2Q26 and 2Q24-2Q26), against `last_q`'s 0.916 / 0.905 and 0.876 / 0.871. Zero of four checks met. Jackknife maxima 1.14 to 1.44. On target 1 (integer-fair ex-FX) 1.155 and 1.291 against `last_q`'s 0.985 / 1.080. The regional build is worse than the rule it was meant to beat, and worse than naive on all four checks.

2. **North America carries the loss, through the proxies.** From 2Q25 the walk-forward selection for NA picks a lagged US lodging price series (CPI lodging SA lag 1, then BEA hotels price lag 1, then CPI lodging NSA lag 1) because each had the lowest out-of-sample RMSE on the four to eight usable quarters before t. All three fits carry a negative slope (in-sample Pearson r -0.78 to -0.92 on 13 quarters, 2Q23-2Q26: NA ex-FX rose from -1.9 to +6.8 while US hotel prices fell from +8 to -3 and then jumped). The 1Q26 CPI jump was therefore read as a fall, and the 2Q26 NA forecast was 1.76 against a solved 6.75; that one quarter contributes -2.19 pp to the aggregate error (descriptive, `L3_error_attribution.csv`). NA's own ratio vs its regional naive is 1.52 (jackknife 0.93 to 1.94). Dropping 2Q26 puts `L_wf` 0.015 below `last_q` on the same nine quarters under eur on the first window and 0.002 above it on the second, and 0.09 below under baskets (paired jackknife), so the headline fail rests on 2Q26; but 2Q26 is a real quarter, and even without it the model does not beat `last_q` on both windows under both estimators (drop-one samples where `L_wf` beats `last_q`: one of ten and none of nine under eur, one of ten and one of nine under baskets).

3. **EMEA on HICP is a per-region gain that does not survive aggregation.** Euro-area HICP accommodation, level, lag 0, reproduces J2's number exactly (ratio 0.914 vs EMEA naive, n 10) and the jackknife this time is 0.780 to 1.173 with 9 of 10 drop-one samples below 1: it rests on 1Q25, its one clear win (4.28 against last quarter's 6.00 with an actual of 4.00; drop it and the ratio is 1.17), while its worst misses are 3Q25 (2.30 against 4.00) and 1Q24 (3.90 against 5.02). The fixed variant (HICP for EMEA, last_q elsewhere, no selection) scores 1.067 / 0.963 eur and 0.980 / 0.845 baskets: it beats `last_q` on one check (baskets, 2Q24-2Q26) and loses on three, and its loss on the 1Q24-2Q26 window is the 1Q24 miss (EMEA contribution -0.42 pp against +0.37 for last_q in a quarter where the rule was already 1.4 pp low). INE Spain (level lag 1, 1.48; level lag 0, 1.72) and every first-difference form lose to the regional naive. Pearson r for HICP is 0.74 (permutation p 0.001, Bonferroni 0.019 over 8 EMEA proxy tests): a level correlation with a series that was falling through 2023-25, as J2 said.

4. **LatAm and APAC have no covering proxy and run on their own history; they do not decide the result.** Disclosed ex-FX exists for them only from 4Q24 (7 quarters), their dollar weights are 9 and 8 percent, and before 4Q24 the identity carries WS-04's modelled values, which no rule can forecast. LatAm has no eligible candidate before 4Q25 and last_q has the lowest record among the three eligible from 1Q26, so it runs last_q throughout (ratio 1.00 by construction). APAC's selection switches to persistence in 1Q26 and to trailing_4q for 3Q26. APAC's 2Q26 solved value is -1.35 (reported +1 minus a 2.35 pp basket) and every rule missed it by about 3.4 pp (weighted contribution +0.27 pp).

5. **The walk-forward selection hurts; the fixed variant and plain regional last_q do better; nothing passes.** Ranking on the four target-2 checks: `L_wf` 0 of 4; `L_wf` with a same-quarters relative criterion (sensitivity) 0 of 4 and worse (1.26 / 1.41 eur); fixed HICP 1 of 4; regional persistence 2 of 4; regional last_q 2 of 4 (0.991 / 1.037 eur, 0.853 / 0.860 baskets); walk-forward restricted to own-history rules (`L_wf_own`, no proxies) 2 of 4 (0.922 / 0.936 eur, 0.740 / 0.719 baskets; midpoint 0.845 / 0.837). `L_wf_own` is the closest thing to a positive result and it is not one: (a) its per-region ratios are 1.00 (NA), 1.04 (EMEA), 1.00 (LatAm), 1.00 (APAC), so no region is forecast better than its own last quarter; the aggregate gain comes from an EMEA AR(1) that sat near 4.4 while disclosed EMEA ex-FX was 4, 4, 4, 5 in 3Q25-2Q26 (the rule was right for the wrong reason: it mean-reverts, and the series happened not to move); (b) its eur and baskets ratios differ by 0.18 to 0.22 (0.14 to 0.18 for regional last_q) where `last_q`'s differ by 0.04, because its 1Q25 and 1Q26 errors (+1.21, -1.36 under eur) are partly offset by the baskets estimator's FX error in those quarters and not by the eur estimator's. Under eur it beats `last_q` in 5 of 10 and 3 of 9 paired drop-one samples. That is a coin flip, and the eur estimator is the one S flagged as binding.

6. **Why the regional route is structurally handicapped against the rule, and what would change that.** Disclosed blended ex-FX = within-region ex-FX + geo mix - reconstruction gap (H's identity, reproduced here to 0.000000). The gap (regional integer rounding, the blended integer, NA's assumed pass-through, modelled LatAm and APAC before 4Q24) has RMSE 0.39 pp on 1Q24-2Q26 (range -0.35 to +0.72, lag-1 autocorrelation 0.30) and is invisible to a regional forecast; the blended residual rule never pays it because H defines the residual to absorb it. Subtracting last quarter's gap (`L_wf_gap_lastq`) helps under eur (1.168 / 1.226) and hurts under baskets (1.088 / 1.092); it is noise. A regional route can only win if the regional signal is worth more than 0.4 pp of RMSE, and on ten quarters with whole-point regional disclosures it is not.

7. **3Q26 and 4Q26 (memo lines, since the model failed its criterion).** `L_wf` gives blended ex-FX +0.6 for 3Q26 (within-region +2.0, geo -1.43; central band -0.2 to +1.4, wide -1.2 to +2.4) and +1.1 for 4Q26 (+0.3 to +1.9), driven by NA at +0.15 from the BEA lag-1 fit reading the 2Q26 BEA jump (+4.96) as a fall. That number is what the failed model says and should not be used. The regional last_q aggregate, which is what the regions' latest disclosures say when carried forward, gives +3.4 for 3Q26 (2.4 to 4.5) and +3.5 for 4Q26 (2.4 to 4.6); own-rules walk-forward +3.6 (2.8 to 4.5) and +3.6; fixed HICP +3.3 (2.5 to 4.2) and +3.4, with EMEA at 4.6 on the July HICP reading of 4.6. Comparison columns, not inputs: card v2 3Q26 +3.46; the v3 last_q rule on I's measured 3Q26 terms with S's prior-year fills and the 2Q26 residual, +3.99. The regional carries sit 0.4 to 0.7 pp below the rule because NA's solved 6.75 is offset by APAC's solved -1.35 and the geo term, while the rule carries a 4.85 residual.

---

## 2. Tables

### 2.1 Regional ex-FX panel: what is usable (sourced from WS-04; descriptive counts)

| region | usable from | n usable to 2Q26 | basis of the usable cells | dollar weight at 2Q26 (year-ago share x anchored ADR) | not usable |
|---|---|---|---|---|---|
| NA | 2Q23 | 13 | solved 12 (disclosed reported y/y minus basket, pass-through 1.00 assumed, NA basket under 1 percent), disclosed 1 (1Q25) | 0.439 | 1Q22-1Q23 modelled |
| EMEA | 1Q23 | 14 | disclosed 9 (3Q23, 4Q23, 4Q24-2Q26), solved 5 (1Q23, 2Q23, 1Q24-3Q24, pass-through 1.04 fitted) | 0.391 | 1Q22-4Q22 modelled |
| LatAm | 4Q24 | 7 | disclosed 7 | 0.090 | 1Q22-3Q24 modelled (annual anchor x seasonal) |
| APAC | 4Q24 | 7 | disclosed 6, solved 1 (2Q26: reported +1 minus basket, pass-through 0.86 fitted) | 0.081 | 1Q22-3Q24 modelled |

Identity check (`L1_identity_check.csv`, descriptive): within-region ex-FX and geo mix rebuilt from the panel match H's `within_region_exfx_pp` and `geo_mix_pp` to 0.000000 in every quarter 1Q23-2Q26. Reconstruction gap (reconstructed minus disclosed integer) on 1Q24-2Q26: RMSE 0.388, mean +0.07, min -0.35 (4Q25), max +0.72 (3Q25), lag-1 autocorrelation 0.30. A plain nights-share mean of regional ex-FX (no ADR weights) differs from H's within by up to 0.7 pp (2Q26: 4.28 vs 4.99) and is not used.

### 2.2 Note-08 tests per region, usable quarters of 1Q24-2Q26, ratio vs the region's own naive (`L2_proxy_tests.csv`, descriptive)

Own rules and the best proxy forms. Full table: 29 NA rows, 13 EMEA, 5 each for LatAm and APAC.

| region | candidate | n | RMSE | naive RMSE | ratio vs naive | jackknife | sign acc. | r (usable window) | perm p | Bonferroni |
|---|---|---|---|---|---|---|---|---|---|---|
| NA | last_q | 10 | 1.31 | 1.31 | 1.000 | | | | | |
| NA | last_q_ex_size (I1 regional size term) | 10 | 1.35 | 1.31 | 1.030 | 0.99 to 1.13 | 0.40 | | | |
| NA | BEA hotels price, level, lag 1 | 9 | 1.15 | 0.95 | 1.207 | 0.93 to 1.48 | 0.67 | -0.915 | 0.001 | 0.000 |
| NA | persistence | 10 | 1.66 | 1.31 | 1.264 | 1.12 to 1.37 | 0.60 | | | |
| NA | CPI lodging SA, level, lag 1 | 9 | 1.26 | 0.95 | 1.319 | 0.98 to 1.60 | 0.56 | -0.898 | 0.001 | 0.001 |
| NA | CPI lodging NSA, level, lag 1 | 9 | 1.85 | 0.95 | 1.939 | 0.86 to 2.39 | 0.67 | -0.779 | 0.003 | 0.040 |
| NA | Marriott RevPAR, level, lag 0 (test only) | 9 | 1.88 | 0.95 | 1.972 | 1.66 to 2.45 | 0.56 | -0.774 | 0.003 | 0.046 |
| NA | ar1 | 9 | 3.33 | 0.95 | 3.491 | 1.38 to 4.31 | 0.67 | | | |
| NA | every other candidate (20, trailing_4q at 2.03 the best of them) | 9 | | | 2.03 to 3.78 | | | | | |
| EMEA | HICP EA accommodation, level, lag 0 | 10 | 0.92 | 1.00 | **0.914** | 0.78 to 1.17 (9 of 10 below 1) | 0.63 | 0.742 | 0.001 | 0.019 |
| EMEA | ar1 | 10 | 0.99 | 1.00 | 0.990 | 0.82 to 1.14 | 0.75 | | | |
| EMEA | last_q | 10 | 1.00 | 1.00 | 1.000 | | | | | |
| EMEA | persistence | 10 | 1.05 | 1.00 | 1.044 | 0.88 to 1.24 | 0.38 | | | |
| EMEA | last_q_ex_size | 10 | 1.14 | 1.00 | 1.141 | 1.04 to 1.22 | 0.50 | | | |
| EMEA | trailing_4q | 10 | 1.35 | 1.00 | 1.347 | 1.01 to 1.68 | 0.50 | | | |
| EMEA | INE Spain hotel price, level, lag 1 | 10 | 1.48 | 1.00 | 1.476 | 1.20 to 1.87 | 0.63 | 0.572 | 0.021 | 0.260 |
| EMEA | HICP, level, lag 1 | 10 | 1.83 | 1.00 | 1.829 | | 0.50 | 0.783 | 0.001 | 0.007 |
| EMEA | every difference form (4) and INE level lag 0 | 10 | | | 1.64 to 2.32 | | | | | |
| LatAm | last_q | 7 | 0.97 | 0.97 | 1.000 | | | | | |
| LatAm | last_q_ex_size | 6 | 1.03 | 1.00 | 1.032 | 0.98 to 1.21 | 0.33 | | | |
| LatAm | persistence | 6 | 1.02 | 0.65 | 1.571 | 1.28 to 1.85 | 0.33 | | | |
| APAC | trailing_4q | 4 | 1.69 | 2.48 | 0.683 | 0.13 to 0.96 | 0.67 | | | |
| APAC | persistence | 6 | 1.70 | 2.33 | 0.728 | 0.53 to 0.85 | 0.80 | | | |
| APAC | last_q_ex_size | 6 | 1.83 | 1.88 | 0.974 | 0.95 to 1.00 | 0.60 | | | |
| APAC | last_q | 7 | 2.19 | 2.19 | 1.000 | | | | | |

The only survivor by J2's definition (flagged r, beats naive and AR(1), n at least 6) is HICP level lag 0 for EMEA, as in J2. The NA proxies are flagged on negative correlations and lose the walk-forward. APAC's trailing_4q and persistence ratios are on four and six quarters of a whole-point series that went 2, 3, 1, 3, 2, 2, -1.35 and mean nothing at that n.

### 2.3 Walk-forward picks (`L2_regional_selection.csv`, descriptive)

| quarter | NA pick (prior OOS n; pick RMSE vs last_q RMSE on the pick's record) | EMEA pick | LatAm | APAC |
|---|---|---|---|---|
| 1Q24 | last_q (default, 3) | last_q (default, eligible 1) | last_q (default) | last_q (default) |
| 2Q24 | last_q (4) | persistence (4; 2.19 vs 3.45) | last_q | last_q |
| 3Q24 | last_q (5) | persistence (5; 2.00 vs 3.15) | last_q | last_q |
| 4Q24 | last_q (6) | last_q_ex_size (4; 0.92 vs 2.92) | last_q | last_q |
| 1Q25 | last_q (7) | ar1 (4; 0.88 vs 2.78) | last_q | last_q |
| 2Q25 | CPI lodging SA level lag 1 (4; 0.96 vs 1.30) | HICP level lag 0 (5; 0.90 vs 2.70) | last_q | last_q |
| 3Q25 | CPI lodging SA level lag 1 (5; 0.90 vs 1.23) | HICP level lag 0 (6; 0.86 vs 2.58) | last_q | last_q |
| 4Q25 | BEA hotels level lag 1 (6; 0.89 vs 1.29) | HICP level lag 0 (7; 1.02 vs 2.48) | last_q (4, eligible 1) | last_q (4, eligible 1) |
| 1Q26 | BEA hotels level lag 1 (7; 0.83 vs 1.23) | HICP level lag 0 (8; 0.99 vs 2.37) | last_q | persistence (4; 1.21 vs 2.12) |
| 2Q26 | CPI lodging NSA level lag 1 (8; 0.86 vs 1.26) | HICP level lag 0 (9; 0.94 vs 2.28) | last_q | persistence (5; 1.10 vs 1.93) |
| 3Q26, 4Q26 | BEA hotels level lag 1 (9; 1.15 vs 1.22) | HICP level lag 0 (10; 0.92 vs 2.21) | last_q (7, eligible 4) | trailing_4q (4; 1.69 vs 2.19) |

The "last_q RMSE" in the comparison is last_q's RMSE over all of its own prior usable quarters (the pre-stated absolute criterion), which for NA and EMEA includes the 2023 quarters where solved ex-FX swung by 4 to 7 pp; a proxy that only has predictions from 2Q24 is compared against that. The same-quarters relative criterion (`L_wf_rel`, sensitivity) makes the picks worse, not better, so this is not what decides the fail.

### 2.4 S harness, target 2 and target 1 (`L3_scores.csv`, `L3_pass.csv`, descriptive; walk-forward 1Q24-2Q26 n 10 and 2Q24-2Q26 n 9)

Ratio vs naive [jackknife min to max], drop-one samples below 1. Bold = in the L criterion.

| model | t2 eur, 1Q24- | t2 eur, 2Q24- | t2 baskets, 1Q24- | t2 baskets, 2Q24- | t2 mid, 1Q24- | t2 mid, 2Q24- | t1, 1Q24- | t1, 2Q24- | L checks met |
|---|---|---|---|---|---|---|---|---|---|
| **last_q (v3 rule, S)** | **0.916 [0.87-0.97] 10/10** | **0.905 [0.83-0.99] 9/9** | **0.876 [0.79-0.92] 10/10** | **0.871 [0.75-0.92] 9/9** | 0.893 | 0.882 | 0.985 [0.92-1.08] | 1.080 [1.00-1.18] | reference |
| **L_wf (primary)** | **1.198 [0.89-1.32] 1/10** | **1.324 [0.89-1.44] 1/9** | **1.033 [0.79-1.14] 1/10** | **1.078 [0.79-1.24] 1/9** | 1.147 | 1.240 | 1.155 [0.92-1.29] | 1.291 [1.00-1.34] | 0 of 4, FAIL |
| L_wf_gap_lastq | 1.168 [0.93-1.24] | 1.226 [0.86-1.36] | 1.088 [0.94-1.17] | 1.092 [0.91-1.21] | 1.148 | 1.182 | 1.348 | 1.354 | 0 of 4 |
| L_wf_rel (same-quarters selection) | 1.262 [0.98-1.41] | 1.410 [1.02-1.55] | 1.137 [0.93-1.23] | 1.200 [0.96-1.33] | 1.230 | 1.346 | 1.206 | 1.354 | 0 of 4 |
| L_fixed_hicp (HICP EMEA, last_q elsewhere) | 1.067 [0.96-1.12] 1/10 | 0.963 [0.92-1.04] 8/9 | 0.980 [0.85-1.06] 9/10 | 0.845 [0.76-0.91] 9/9 | 1.037 | 0.907 | 0.985 [0.82-1.05] | 0.816 [0.78-0.89] | 1 of 4 |
| L_reg_lastq (every region last_q) | 0.991 [0.95-1.04] 7/10 | 1.037 [0.98-1.11] 2/9 | 0.853 [0.81-0.88] 10/10 | 0.860 [0.81-0.90] 9/9 | 0.936 | 0.962 | 0.985 [0.92-1.08] | 1.080 [1.00-1.18] | 2 of 4 |
| L_reg_persist | 1.047 [0.98-1.12] | 1.090 [0.99-1.21] | 0.870 [0.78-0.95] | 0.857 [0.73-0.96] | 0.981 | 0.996 | 1.155 | 1.291 | 2 of 4 |
| L_wf_own (own rules only) | 0.922 [0.89-0.97] 10/10 | 0.936 [0.90-1.02] 8/9 | 0.740 [0.71-0.81] 10/10 | 0.719 [0.68-0.80] 9/9 | 0.845 | 0.837 | 0.853 [0.78-0.91] 10/10 | 0.913 [0.82-1.00] 7/9 | 2 of 4 |
| naive RMSE, pp | 1.199 | 1.033 | 0.949 | 0.898 | 1.043 | 0.932 | 0.908 | 0.816 | |

No variant meets the strict v3 criterion either (ratio and jackknife max below 1 on all four checks); `L_wf_own` is the only one with all four ratios below 1 and it has a jackknife max of 1.02 under eur on the second window.

Paired jackknife (`L3_paired_jackknife.csv`: variant and `last_q` on the same nine-quarter subsample, count of drops where the variant is lower): `L_wf` 1/10, 0/9 eur and 1/10, 1/9 baskets, the one favourable drop being 2Q26 in every case; `L_fixed_hicp` 0/10, 1/9 eur and 1/10, 8/9 baskets; `L_reg_lastq` 0/10, 0/9 eur and 9/10, 7/9 baskets; `L_wf_own` 5/10, 3/9 eur and 10/10, 9/9 baskets. The drop that hurts most regional variants most is 3Q24, the one deceleration (for `L_wf` and `L_wf_rel` under eur on the first window it is 1Q24), where the rule's residual carry was 1.15 pp early and the regional carry only 0.4.

### 2.5 Per-region scores against the region's own naive (`L3_regional_scores.csv`, descriptive, usable quarters of 1Q24-2Q26)

| variant | NA (n 10) | EMEA (n 10) | LatAm (n 7) | APAC (n 7) |
|---|---|---|---|---|
| L_wf | 1.519 [0.93-1.94] | 1.024 [0.92-1.18] | 1.000 | 1.004 |
| L_fixed_hicp | 1.000 | 0.914 [0.78-1.17] | 1.000 | 1.000 |
| L_reg_persist | 1.264 | 1.044 | 1.252 | 0.738 [0.56-0.86] |
| L_wf_own | 1.000 | 1.039 [0.89-1.21] | 1.000 | 1.004 |

Regional naive RMSE: NA 1.31, EMEA 1.00, LatAm 0.97, APAC 2.19 pp.

### 2.6 Error attribution, primary model vs the rule (`L3_error_attribution.csv`, descriptive, pp; contribution = dollar weight x regional error, linearised)

| quarter | L_wf error | last_q rule error | naive error | within error | gap | NA | EMEA | LatAm | APAC |
|---|---|---|---|---|---|---|---|---|---|
| 1Q24 | -1.26 | -1.36 | -1.5 | -1.08 | -0.18 | -1.39 | +0.37 | +0.13 | -0.19 |
| 2Q24 | -0.83 | -0.92 | -1.0 | -0.50 | -0.32 | -0.62 | +0.34 | -0.35 | +0.12 |
| 3Q24 | +0.69 | +1.21 | +1.0 | +0.39 | +0.30 | +0.37 | +0.07 | -0.41 | +0.36 |
| 4Q24 | -0.31 | -0.62 | 0.0 | -0.80 | +0.49 | -0.07 | -0.52 | +0.06 | -0.27 |
| 1Q25 | +1.23 | +0.71 | +1.0 | +0.83 | +0.40 | +0.21 | +0.54 | +0.17 | -0.09 |
| 2Q25 | +0.34 | +0.50 | 0.0 | +0.13 | +0.21 | -0.26 | +0.24 | 0.00 | +0.15 |
| 3Q25 | -0.57 | -0.74 | -1.0 | -1.29 | +0.72 | -0.43 | -0.58 | -0.09 | -0.20 |
| 4Q25 | -0.50 | -0.70 | -1.0 | -0.15 | -0.35 | +0.03 | -0.26 | 0.00 | +0.08 |
| 1Q26 | -0.93 | -0.38 | -1.0 | -0.60 | -0.33 | -0.63 | -0.02 | 0.00 | +0.05 |
| 2Q26 | -2.40 | -0.17 | 0.0 | -2.12 | -0.28 | -2.19 | -0.29 | +0.09 | +0.27 |

Model error = within error + gap (the geo term is measured, so it adds nothing). The regional build is less wrong than the rule in seven of ten quarters (all but 1Q25, 1Q26 and 2Q26) and less early at the 3Q24 turn; from 1Q26 the NA proxy picks turn it into the worst model in the table, and 2Q26 alone outweighs the seven small gains.

### 2.7 3Q26 and 4Q26 (`L4_regional_nowcast.csv`, `L4_aggregate_nowcast.csv`; ex-FX ADR y/y, pp)

Regional inputs in hand: HICP July 4.6 (sourced, Eurostat prc_hicp_minr), INE July 5.91, CPI lodging SA July-August 3.54, BEA hotels July 3.55 (all from `J2_proxy_readings_3q26.csv`). Weights: 3Q25 (4Q25) nights shares and anchored regional ADR. Geo term: I's measured 3Q26 split, -1.43 (lo -1.57, hi -0.94), carried to 4Q26 (assumed). Regional band = the pick's out-of-sample RMSE before 3Q26 (descriptive); aggregate central band = root sum of squares of weighted regional bands, the gap RMSE (0.39) and the geo half-range; wide = arithmetic sum.

| variant | NA | EMEA | LatAm | APAC | within | geo | **blended 3Q26** | central | wide | **blended 4Q26** | central |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L_wf (failed; memo) | 0.15 (BEA lag 1 on the 2Q26 jump 4.96; band 1.15) | 4.63 (HICP 4.6; 0.92) | 2.00 (last_q; 0.97) | 1.41 (trailing 4q; 1.69) | 2.01 | -1.43 | **+0.6** | -0.2 to +1.4 | -1.2 to +2.4 | **+1.1** | +0.3 to +1.9 |
| L_reg_lastq | 6.75 (2Q26 solved; 1.22) | 5.00 (2.21) | 2.00 (0.97) | -1.35 (2Q26 solved; 2.19) | 4.87 | -1.43 | **+3.4** | +2.4 to +4.5 | +1.1 to +5.8 | **+3.5** | +2.4 to +4.6 |
| L_wf_own | 6.75 (last_q) | 4.70 (ar1; 0.99) | 2.00 | 1.41 (trailing 4q) | 5.05 | -1.43 | **+3.6** | +2.8 to +4.5 | +1.8 to +5.5 | **+3.6** | +2.7 to +4.4 |
| L_fixed_hicp | 6.75 | 4.63 (HICP 4.6) | 2.00 | -1.35 | 4.74 | -1.43 | **+3.3** | +2.5 to +4.2 | +1.4 to +5.2 | **+3.4** | +2.5 to +4.2 |
| comparison: v3 last_q rule (I terms, S fills, 2Q26 residual 4.85) | | | | | | -1.43 | +3.99 | | | +3.99 (3Q26 terms carried) | |
| comparison: card v2 (J3) | | | | | | -1.43 | +3.46 | | | | |

4Q26 assumptions: own-history rules chain on the 3Q26 forecast; lag-0 proxy forms hold the July reading; BEA lag 1 for NA uses the July reading 3.55 (giving NA 1.06 in `L_wf`). None of the 4Q26 numbers has an out-of-sample record.

---

## 3. Method

**Panel (L1, sourced).** `data/processed/adr/04_regional_quarterly_wide.csv` for regional ex-FX y/y, reported y/y, FX pp, nights share, anchored ADR; the long file `04_regional_quarterly.csv` for the per-cell basis string of `adr_yoy_exfx_pct`, classed as disclosed (letter), solved (derived from a disclosed reported y/y minus the WS-02 basket times pass-through) or modelled (derived from modelled levels). Usable = disclosed or solved. Workstream I's regional `size_term_pp` from `I1_party_size_quarterly.csv` (2023Q3 on) for the size-adjusted rule. Identity: within = sum(s0 A0 (1+g)) / sum(s0 A0) - 1, total = sum(s1 A0 (1+g)) / sum(s0 A0) - 1, geo = total - within, with s0 and A0 at t-4 and s1 at t, copied from `H1_adr_card.py` and checked against H's columns.

**Candidates and predictions (L0, L2).** Own rules on the region's usable history strictly before t: last_q, persistence (mean of last two), trailing_4q, ar1 (expanding np.polyfit, at least four training quarters, S's benchmark convention), last_q_ex_size (last quarter's ex-FX minus its I1 size term plus the current quarter's I1 size term). Where a region has no usable prior quarter (LatAm and APAC before 1Q25) last_q, persistence and trailing_4q fall back to the latest value of any basis, which is what the identity contains; the fallback is flagged in the OOS record and those quarters are never scored per region. Proxy forms: expanding OLS (np.polyfit) of regional ex-FX on the proxy in level or first difference at lag 0 or 1, fitted on usable quarters strictly before t with at least four training pairs, exactly J2's forms; the lag-0 forms use the proxy's value for t, which publishes before the print. Coverage: NA on the three BLS CPI series and BEA hotels; EMEA on HICP and INE; LatAm and APAC none. Marriott and Hilton worldwide RevPAR are tested for NA (they are US-weighted) but excluded from the selection pool because no 3Q26 reading exists. The tests table scores each candidate on the usable quarters of 1Q24-2Q26 against the region's last quarter, prior year (usable only) and the expanding AR(1), with Pearson r and p, Spearman, 1,000-shuffle permutation p (seed 20260911) and Bonferroni over the region's proxy tests, and a drop-one jackknife of the ratio vs naive.

**Selection (L2).** At each scored quarter t (1Q24-2Q26, 3Q26, 4Q26), each candidate's out-of-sample record is its predictions at usable quarters s < t, each built on data strictly before s. Eligible if the record has at least four quarters; the pick is the eligible candidate with the lowest RMSE on its own record; ties go to the earlier candidate in the order own rules, then proxies; no eligible candidate gives last_q. This was the pre-stated rule and is the primary. Because it compares RMSEs over different quarter sets, a sensitivity (`L_wf_rel`) picks on the ratio of the candidate's RMSE to last_q's RMSE on the same quarters; a second sensitivity (`L_wf_own`) restricts the pool to own rules. Both were added after the primary ran and are labelled as sensitivities.

**Aggregation and scoring (L3).** For each variant and scored quarter, the four regional forecasts are aggregated with the identity's weights (year-ago nights share times year-ago anchored ADR, both knowable) into a within-region ex-FX forecast; the model's blended ex-FX is that plus H's measured `geo_mix_pp` for t (the same realised geo term S's measured mix uses, so the L paths and the `last_q` rule face the same geo information; this is an upper bound on workstream I as in S). `S.exfx_from_residual` is not used because it adds measured size and LOS, which the regional ex-FX already carries. The reconstruction gap is not modelled in the primary; `L_wf_gap_lastq` subtracts last quarter's gap. Each path is scored with `S.score` on both targets, three FX estimators, both windows, and `S.preregistered_pass`; the L criterion compares each variant's target-2 ratio vs naive with `last_q`'s from `S.v2_model_paths()["v2_measured_last_q"]` scored in the same call. Per-region scores use the region's last quarter as naive on usable quarters. The paired jackknife recomputes both the variant's and `last_q`'s ratio on each nine-quarter drop-one subsample from `L3_walk_forward_paths.csv`. Attribution splits model error into within error and gap, and within error into dollar-weight times regional error.

**Nowcast (L4).** Picks at 3Q26 from the L2 selection (the information set at 4Q26 is the same, so the same pick). Proxy panel extended by the J2 3Q26 readings; for 4Q26 the reading is held (assumed). Own rules chain on the 3Q26 forecast for 4Q26 (assumed). Geo from `I_mix_terms_3q26.csv`. The v3 last_q comparison is geo -1.43 + size +0.80 + LOS +0.06 + S's prior-calendar-year new-business and interaction fills for 2026 (-0.28 together, from `S.v2_components()` at 2Q26) + the 2Q26 residual 4.85 = 3.99; J3's card used H's -0.48 and -0.10 fills and a 4.61 residual nowcast, which is why card v2 is 3.46.

---

## 4. What this can and cannot identify

- **The fail is a fail of the proxies, not of the regional arithmetic.** With no proxies the regional carry (`L_reg_lastq`) is close to the rule under baskets and behind it under eur; with proxies it is behind on every check. Nothing in the US lodging price series tracks NA ex-FX ADR in a way that survives a walk-forward: the correlations are negative and the level fits invert the sign of the 2026 jump. This is J2's null at the regional level, with the walk-forward selection demonstrating how a data-chosen proxy fails out of sample.
- **HICP against EMEA is real but small and not robust.** 0.914 with a jackknife that reaches 1.17 on ten quarters, and its aggregate value sign changes with the window. J2's "carry into the regional read for the 5 November letter, nothing more" stands. The July reading (4.6) implies EMEA ex-FX about 4.6 for 3Q26, against a 2Q26 disclosed 5.
- **The own-rules result is not a discovery.** Its aggregate ratios under baskets (0.74, 0.72) are the best in the table, and they come from an EMEA AR(1) that mean-reverts to about 4.4 during four quarters when disclosed EMEA ex-FX did not move, and from an FX cross term that flatters it under baskets and not under eur. Per region it forecasts nothing better than last quarter. The pre-registered criterion requires both estimators for exactly this reason (S, point 7), and it does not meet it. P should treat it as a memo line, not a term.
- **Solved regional ex-FX is not independent of FX.** NA's and part of EMEA's usable history is reported y/y minus a basket times an assumed or fitted pass-through, so the target these regional rules fit already embeds an FX estimate; the eur-vs-baskets spread of 0.14 to 0.22 on the regional carry variants (vs 0.04 for the rule) is consistent with that. A regional model on whole-point disclosures with two of four regions disclosed for seven quarters cannot resolve it.
- **The reconstruction gap is a floor.** 0.39 pp of RMSE that the regional route pays and the blended residual rule does not. On a series whose naive RMSE is 0.9 to 1.2 pp, that is a third to a half of the error budget before any regional signal is counted.
- **Ten quarters, one deceleration.** All regional variants are less early than the rule at 3Q24 and later than it in 1Q26 and 2Q26; the paired jackknife names 3Q24 as the quarter every regional variant leans on. The window has one turn each way and the jackknife bounds within-sample only.
- **Measured geo term is an upper bound, as in S.** I's real-time geo split reproduces H's disclosed-share term only loosely (RMSE 0.4 to 0.7, I note); the L ratios would be worse with I's term in place of H's.
- **Modelled quarters were not used to fit anything, and the 3Q26 APAC and LatAm picks are on seven quarters.** APAC's trailing_4q pick for 3Q26 (1.41) is on a four-quarter out-of-sample record; treat its band (1.69) as the honest statement.

---

## 5. Next evidence

1. **P should carry no L term into card v3.** Report the fail and the regional last_q carry (+3.4 / +3.5) as a memo line alongside card v2 and the v3 rule, with EMEA's HICP-implied 4.6 as a regional read for the letter, nothing more.
2. **The 5 November print scores each region's carry.** `L4_regional_nowcast.csv` fixes NA 6.75, EMEA 5.0 (HICP 4.6), LatAm 2.0, APAC -1.35 (or 1.4 on trailing) before the print; the disclosed regional ex-FX will say which region moved and by how much. If APAC prints well above -1.35 the 2Q26 solved value was a basket artefact, which would argue for treating APAC solved quarters as unusable.
3. **September HICP (flash mid-October) and the August-September CPI and BEA readings** update the L4 proxy inputs; the NA proxy fits should not be used regardless.
4. **If a same-listing realised-rate series ever exists (J section 5), test it by region first.** The regional route only wins if a regional signal is worth more than the 0.4 pp gap; a realised-rate series is the one candidate that could be.

---

## 6. Files

| File | Contents |
|---|---|
| `analysis/src/adrv3/L0_common.py` | shared: regional panel and basis classes, H identity, candidate definitions, strictly out-of-sample prediction, walk-forward selection, permutation test |
| `analysis/src/adrv3/L1_regional_panel.py` | writes the panel and the identity check |
| `analysis/src/adrv3/L2_regional_tests_selection.py` | note-08 tests per region, OOS paths, walk-forward picks and the full selection tables |
| `analysis/src/adrv3/L3_aggregate_score.py` | aggregation, S-harness scoring of seven variants plus the rule, L verdicts, per-region scores, attribution, paired jackknife |
| `analysis/src/adrv3/L4_regional_nowcast.py` | 3Q26 and 4Q26 regional forecasts and aggregates with bands |
| `data/processed/adrv3/L/L1_regional_panel.csv` | 88 rows (22 quarters x 4 regions): ex-FX, reported, FX, share, anchored ADR, basis class and raw string, usable flag, I1 size term |
| `data/processed/adrv3/L/L1_identity_check.csv` | 18 quarters 1Q22-2Q26: within, geo, reconstructed from the panel, H's columns where H exists (1Q23 on); disclosed; gap; dollar weights; regions modelled |
| `data/processed/adrv3/L/L2_proxy_tests.csv` | 52 rows: every candidate per region on the usable quarters of 1Q24-2Q26, walk-forward ratios, jackknife, correlations, Bonferroni, survivor flag |
| `data/processed/adrv3/L/L2_candidate_oos_paths.csv` | every candidate's out-of-sample prediction at every quarter 1Q23-2Q26 per region, with actual and usable flag |
| `data/processed/adrv3/L/L2_regional_selection.csv` | pick per region per quarter 1Q24-4Q26 with prior-OOS RMSE, eligible count, runner-up, last_q's RMSE, prediction and actual |
| `data/processed/adrv3/L/L2_selection_tables.csv` | every candidate's prior-OOS n and RMSE at every selection point |
| `data/processed/adrv3/L/L3_scores.csv` | S.score rows for benchmarks, the v2 rules and the seven L variants (both targets, three estimators, two windows) |
| `data/processed/adrv3/L/L3_pass.csv` | per variant: the four L checks against last_q, target 1 and midpoint alongside, L verdict and the strict v3 verdict |
| `data/processed/adrv3/L/L3_walk_forward_paths.csv` | per target, estimator, quarter: actual, naive, prior year, AR(1), every model in scored units |
| `data/processed/adrv3/L/L3_regional_paths.csv` | per variant, region, quarter: candidate used, prediction, actual, usable |
| `data/processed/adrv3/L/L3_regional_scores.csv` | per variant and region: RMSE vs the regional naive, ratio, jackknife, picks |
| `data/processed/adrv3/L/L3_error_attribution.csv` | per quarter for L_wf, L_fixed_hicp, L_reg_lastq, L_wf_own: model, rule and naive error, within error, gap, regional contributions |
| `data/processed/adrv3/L/L3_paired_jackknife.csv` | per variant, target, estimator, window: drop-one comparison with last_q on identical subsamples |
| `data/processed/adrv3/L/L4_regional_nowcast.csv` | 3Q26 and 4Q26 per region and variant: pick, proxy input, forecast, band, basis |
| `data/processed/adrv3/L/L4_aggregate_nowcast.csv` | blended ex-FX per variant and quarter with central and wide bands, plus the two comparison columns |
