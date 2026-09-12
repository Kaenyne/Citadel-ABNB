# K. Residual decomposition: is the 1H26 step the fee-migration reprice, and does it lap in 4Q26

- **Date:** 2026-09-11. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Question:** the like-for-like pricing residual (`residual_pricing_pp`, 1Q23 to 2Q26) stepped from 2 to 3.7 pp in 2023-25 to 4.4 and 4.9 pp in 1H26. WS-D dated the cancellation redesign and the single host-only fee as global from October 2025; the H card carried a fee-migration increment as a memo. Is the step the reprice on the migrated cohort? If so, when does it lap, and what does that say about the 3Q26 and 4Q26 residual?
- **Pre-registered criterion (BRIEF, K):** pass = a residual model using the migrated-cohort share beats `last_q` on the S harness on both windows, with a fee coefficient whose sign and size are consistent with the fee mechanics, the size stated before fitting. Otherwise the null, and the 4Q26 lap arithmetic as a scenario.
- **Scripts:** `analysis/src/adrv3/K1_cohort_share.py`, `K2_expected_effect.py`, `K3_fit_and_score.py`, `K4_residual_nowcast.py` (`py -3.13`, offline, seconds; run in that order).
- **Outputs (`data/processed/adrv3/K/`):** `K1_migrated_cohort_share.csv`, `K1_assumptions.csv`, `K2_expected_effect.csv`, `K2_expected_effect_prestated.csv` (pre-stated at 2026-09-11 21:56:17, before K3 was written; the stamp is pinned in the script and a separate last-run time is carried), `K3_residual_fit.csv`, `K3_alternatives.csv`, `K3_residual_rule_scores.csv`, `K3_walk_forward_paths.csv`, `K3_rule_residual_paths.csv`, `K3_primary_rule_margin.csv`, `K3_pass_table.csv`, `K3_k_criterion.csv`, `K4_residual_nowcast.csv`, `K4_fee_lap_schedule.csv`.
- **Does not redo:** the residual reconstruction (H), the mix terms (I), the FX estimators (B), the harness (S), the RNPL ledger and lap dating (D). Nothing under `analysis/src/adrq3/`, `analysis/src/adrv3/S*`, `data/processed/adrq3/` or `data/processed/adrv3/S/` is touched.

---

## 1. Bottom line

1. **Verdict against the K criterion: PASS on the letter, by a margin that is not evidence, and the answer to the question is no.** The primary rule, `last_q` plus the pre-stated mechanics coefficient (0.007 pp of residual per pp of y/y migrated nights share) times the quarter's change in that share, beats `last_q` on all four target-2 checks: ratio vs naive 0.912 and 0.898 (eur), 0.873 and 0.868 (baskets) against `last_q`'s 0.916, 0.905, 0.876, 0.871; jackknife maxima 0.966, 0.984, 0.916, 0.921 against 0.969, 0.989, 0.918, 0.924; every drop-one sample below 1 (descriptive, walk-forward 1Q24-2Q26 n 10 and 2Q24-2Q26 n 9). The margin is 0.003 to 0.007 of ratio. It comes from nudges of 0.001, 0.086, 0.029 and 0.034 pp in 3Q25, 4Q25, 1Q26 and 2Q26, the four quarters where the share moved, and in all four the rule was late in the same direction, so any positive coefficient would have helped (one-sided sign-test p 0.0625). The coefficient is consistent with the mechanics because it was imposed at the mechanics value; it is not an estimate. P should carry the term as a mechanics line, +0.17 pp in 3Q26 and +0.20 pp in 4Q26 at the central coefficient (band to +0.94 and +1.09 at the top of the mechanics range), the same size as the H card's fee memo, and should not describe it as a finding.

2. **The pre-stated expectation, recorded before the fit (K2, 21:56:17):** sign positive; central +0.007 pp of residual per pp of y/y migrated nights share (the payout-neutral reprice, +0.7% on the cohort's ADR because ADR is gross of the guest fee); plausible range 0.000 to +0.038 (half pass-through to the "+18.34%" host-forum reprice); anything above +0.05 is outside the mechanics (it needs listed prices up more than about 20% on the cohort) and anything below -0.02 is rejected by the 1H26 NA prints. On the central cohort path (y/y migrated nights share +16.6 pp in 1Q26, +21.5 pp in 2Q26) the fee reprice is worth +0.12 and +0.15 pp central and +0.63 and +0.82 pp at full over-reprice, against an observed step of +1.98 and +2.45 pp over the 2023-25 mean residual of 2.40. Before fitting, then: the reprice can explain about 5% of the step in the central case and about 30% at the top of the range.

3. **The fitted coefficient is outside the mechanics: 0.114 (se 0.025, t 4.7) on the central nights-basis share, levels against the 2023-25 baseline, n 14.** That is 16 times the central expectation and 3.0 times the top of the range. With a constant it is 0.121; in changes 0.084 to 0.089 (t 1.2 to 1.3, not distinguishable from zero). Across the K1 variants it is 0.060 (high-migrant path, the largest cohort) to 0.262 (low-migrant): even the most generous cohort path needs 1.6 times the full over-reprice. The residual rose 2.0 to 2.5 pp; the migrated share can carry 0.1 to 0.8 of it. The rest is something else.

4. **What the something else is cannot be separated at n 14, and the note says which candidates tie.** The central share series has correlation 0.974 with WS-D's RNPL nights-share path, 0.885 with a 2026 dummy and 0.717 with a linear trend. On its own the RNPL share fits the residual as well as the cohort share (R2 0.608 vs 0.605, RMSE 0.693 vs 0.697); put both in and neither is distinguishable from zero (t 0.4 and 0.5). A 4Q25-onward dummy (2.03 pp, t 3.9) does nearly as well (R2 0.565). AR(1) alone gives rho 0.75 (R2 0.41); adding the share to the AR(1) raises R2 to 0.70 and the share keeps its size (0.111, t 3.1) while rho collapses to 0.19, so the step is a level shift dated to the migration window, not a continuation of the residual's own drift. The geographic terms do nothing: geo_mix_pp R2 0.001, H's regional reconciliation gap 0.10, the NA nights-share change 0.08, NA-minus-ex-NA ex-FX ADR 0.15. The step is dated to 4Q25-2Q26 and is global in the blended series, and three things landed in that window: the cancellation redesign (October 2025, global), fee tranche 1 (27 October and 1 December 2025, global) and RNPL (US from 3Q25, rest of world from 17 February 2026). Management's own disclosure gives the bundle an ADR contribution of about 1 pp in 4Q25 (over 200 bp of nights, roughly 300 bp of GBV) and about 1 pp in 1Q26 (about 3 points and 4 points), which is the GBV-minus-nights gap of the three features together. That 1 pp is half of the 4Q25 step over baseline and half of the 1Q26 step, and the fee mechanics say at most 0.1 to 0.6 pp of it is the reprice. The remainder is consistent with RNPL's mix into larger entire homes (D016, D033, D045), which is a mix effect the H decomposition does not measure and which lands in the residual.

5. **When does it lap: the fee reprice does not lap in 4Q26, it peaks there.** The y/y migrated share on the central path is +12.5 pp in 4Q25, +16.6 in 1Q26, +21.5 in 2Q26, +46.0 in 3Q26 and +75.0 in 4Q26 (tranche 2 migrates June to October 2026, deadlines 15 September outside the EEA and 13 October inside it, complete by year-end). It then runs +70.8 in 1Q27, +65.9 in 2Q27, +41.2 in 3Q27 and zero in 4Q27. Tranche 1 anniversaries inside 4Q26 (from 27 October), but tranche 2 is three to four times larger and is migrating through 3Q26 and 4Q26, so the reprice contribution to the y/y residual rises from +0.15 pp (2Q26) to +0.32 (3Q26) and +0.52 (4Q26) at the central coefficient, +0.82 to +1.75 and +2.85 at the top of the range, and does not fall out of the y/y until 4Q27. What does lap in 4Q26 is the bundle's 4Q25 contribution (about 1 pp by management's figures), of which the fee reprice is the smaller part.

6. **3Q26 residual, one sentence:** the cohort model at the pre-stated coefficient puts it at 5.0 pp (last_q 4.85 plus 0.17), the lap arithmetic at 3.9 (the 3Q25 US-RNPL step of 0.92 falls out of the y/y) or 4.1 with tranche 2 added, persistence 4.6, mean reversion 2.4, and the fitted cohort model at 7.6, which is the reductio that says the 1H26 step is not the reprice.

7. **4Q26 residual, one sentence:** the cohort model at the pre-stated coefficient gives 5.2 pp, the lap arithmetic 3.1 (the 4Q25 step of 0.88 also falls out) or 3.8 using management's roughly 1 pp bundle contribution, 3.4 with tranche 2 at the central coefficient and 5.1 at the top of the mechanics range, persistence 4.6 and last_q 4.85; the scored rule says 5.2 and the dated arithmetic says 3.1 to 3.8, and the harness cannot rank a rule that has never seen a lap, so 4Q26 is reported as a 3.1 to 5.2 scenario band around the v3 rule, not as a point.

8. **Two post-hoc results are recorded and not promoted.** (a) A level rule, expanding pre-migration mean plus 0.038 times the y/y share on the high-migrant path, scores 0.739 and 0.853 (eur), 0.591 and 0.658 (baskets), jackknife maxima 0.853 to 0.937, far better than `last_q`. It is the best of 18 rule-by-variant combinations, it takes the top coefficient and the largest cohort at once, the same rule on the central path fails under eur (0.930, 1.097) and on the low path fails everywhere (1.05 to 1.27), and its gain comes from the mean rule beating `last_q` on the 2024 swings, not from the fee term. (b) A walk-forward fitted coefficient (b fitted on prior quarters with at least 2 pp of share; 0.118 at 1Q26, 0.126 at 2Q26) passes the v3 criterion but beats `last_q` under eur only (0.860, 0.819 against 0.908, 0.910 under baskets). Neither is the K term.

---

## 2. Tables

### 2.1 The migrated-cohort share, blended, nights basis, central path (`K1_migrated_cohort_share.csv`)

Split-to-single migrants are the reprice-relevant cohort. The pre-existing single-fee cohort (voluntary from 2019; mandatory for software-connected hosts outside US, Canada, Mexico, Argentina, Uruguay, Taiwan and the Bahamas from December 2020) moved 15% to 15.5% on 1 December 2025, a +0.6% payout-neutral reprice on that cohort only, and is carried separately. Nights shares by region from `04_regional_quarterly_wide.csv` (sourced), 3Q26 and 4Q26 on prior-year shares (assumed).

| quarter | NA | EMEA | LatAm | APAC | blended migrated | y/y change, pp | total single-fee (listings) | step | label |
|---|---|---|---|---|---|---|---|---|---|
| 1Q23 to 2Q25 | 0 | 0 | 0 | 0 | 0 | 0 | 0.12 | pre-migration | assumed level, sourced dates |
| 3Q25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.002 | +0.2 | 0.12 | 25 Aug 2025 new PMS-connected hosts default to single fee | sourced date, assumed size |
| 4Q25 | 0.31 | 0.03 | 0.10 | 0.02 | 0.125 | +12.5 | 0.22 | 27 Oct tranche 1 (PMS split-fee hosts), 66 of 92 days; 1 Dec 15% to 15.5% | sourced dates, assumed regional split |
| 1Q26 | 0.43 | 0.04 | 0.15 | 0.03 | 0.166 | +16.6 | 0.25 | tranche 1 complete; "over a quarter" at the 7 May call | sourced level (D041) |
| 2Q26 | 0.47 | 0.09 | 0.20 | 0.08 | 0.215 | +21.5 | 0.30 | tranche 2 begins; UK-resident hosts 22 Jun; "about half" at the 6 Aug call | sourced dates and level (D047), path assumed |
| 3Q26 | 0.72 | 0.25 | 0.51 | 0.40 | 0.462 | +46.0 | 0.53 | 15 Sep non-EEA deadline inside the quarter; EEA lags to 13 Oct | sourced dates, path assumed |
| 4Q26 | 1.00 | 0.78 | 0.92 | 0.82 | 0.874 | +75.0 | 0.96 | 13 Oct EEA/CH deadline; complete by year-end | sourced dates, path assumed |

The NA tranche-1 share (0.32 of NA listings, calibrated) is solved so the blended total hits 0.26 in 1Q26, one point under the call's "over a quarter" because the call date is after quarter end; NA is where the split-fee PMS hosts sat because US and Canada were exempt from the 2020 mandate. Two alternative paths bracket the cohort: low-migrant (pre-existing cohort 0.18, migrants 5.1, 6.7, 9.9, 29.2, 71.7 pp y/y in 4Q25 to 4Q26) and high-migrant (pre-existing 0.06, migrants 23.4, 31.3, 41.8, 69.1, 76.6 pp). All three read "over a quarter" at the May call. Nights basis applies a 1.3 nights-per-listing factor to the PMS cohorts (assumed, 1.0 to 1.6). `K1_assumptions.csv` lists every parameter with its label.

### 2.2 The expected effect, recorded before the fit (`K2_expected_effect.csv`, 2026-09-11 21:56:17)

Per $100 host subtotal under the split fee: guest pays about $114 (13.9 to 14.2% guest fee), host nets $97, Airbnb $17. Single fee 15.5% of the host price (4Q25 letter; the task text's 15.3% is not what the letter says). Payout-neutral listed price 97 / 0.845 = $114.79.

| case | listed price index | cohort ADR effect | pp of residual per pp of y/y migrated nights share | label |
|---|---|---|---|---|
| no reprice | 100.0 | -12.3% | -0.123 | descriptive arithmetic; rejected by the 1H26 NA prints (quote-index addendum) |
| half pass-through | 107.4 | -5.8% | -0.058 | descriptive |
| payout neutral (+14.8% listed) | 114.8 | +0.5% to +0.8% | +0.005 to +0.008 | descriptive; the letter says hosts "are able to adjust their prices to maintain the same net earnings" |
| full over-reprice (+18.34% listed) | 118.3 | +3.6% to +3.9% | +0.036 to +0.039 | descriptive |
| pre-existing cohort 15% to 15.5%, payout neutral | 100.6 | +0.6% | +0.006 on that cohort | descriptive |
| H card increment, 3Q26 low / point / high | | | -0.013 / +0.007 / +0.038 | sourced (H table 2.3 over a 0.225 penetration rise) |

Pre-stated: sign positive, central +0.007, range 0.000 to +0.038, outside the mechanics above +0.05 or below -0.02.

### 2.3 Fits of the residual on the y/y migrated share, n 14 (`K3_residual_fit.csv`, descriptive)

| variant, basis | spec | coefficient | se | t | R2 | RMSE pp | x expected central | x expected high | within mechanics |
|---|---|---|---|---|---|---|---|---|---|
| central, nights | levels, constant | 0.121 | 0.028 | 4.3 | 0.60 | 0.70 | 17.3 | 3.2 | no |
| central, nights | levels, no constant, 2023-25 mean baseline | **0.114** | 0.025 | 4.7 | 0.63 | 0.71 | 16.3 | 3.0 | no |
| central, nights | changes, constant | 0.089 | 0.074 | 1.2 | 0.12 | 0.84 | 12.6 | 2.3 | no |
| central, nights | changes, no constant | 0.084 | 0.064 | 1.3 | 0.13 | 0.85 | 12.0 | 2.2 | no |
| central, listings | levels, no constant | 0.145 | 0.031 | 4.7 | 0.63 | | 20.7 | 3.8 | no |
| low-migrant, nights | levels, no constant | 0.262 | 0.057 | 4.6 | 0.62 | | 37.5 | 6.9 | no |
| high-migrant, nights | levels, no constant | 0.060 | 0.013 | 4.7 | 0.63 | | 8.5 | 1.6 | no |

Three of the fourteen quarters carry a share above 2 pp (4Q25, 1Q26, 2Q26). The t statistics are those of a three-point step, and the 95% band on the central coefficient (0.06 to 0.17) excludes the whole mechanics range.

### 2.4 Alternatives that produce the same step (`K3_alternatives.csv`, descriptive, n 14 unless stated)

| model | coefficient (t) | R2 | RMSE pp | note |
|---|---|---|---|---|
| constant only | 2.72 | | 1.11 | reference |
| cohort share y/y, central nights | 0.121 (4.3) | 0.605 | 0.70 | the K model |
| RNPL nights share, D path at r 1.25 | 0.144 (4.3) | 0.608 | 0.69 | the other dated 2H25-26 ramp; 3Q25 and 4Q25 shares assumed |
| cohort share + RNPL share | 0.054 (0.4), 0.081 (0.5) | 0.615 | 0.69 | not separable: correlation 0.974 |
| 4Q25-onward dummy | 2.03 (3.9) | 0.565 | 0.73 | the migration window |
| 2026 dummy | 2.22 (3.4) | 0.490 | 0.79 | two quarters; correlation with the share 0.885 |
| cohort share + 2026 dummy | 0.113 (1.8), 0.18 (0.1) | 0.605 | 0.70 | the share carries the dummy |
| linear trend | 0.16 per quarter (2.5) | 0.340 | 0.90 | correlation with the share 0.717 |
| AR(1), n 13 | rho 0.75 (2.8) | 0.414 | 0.86 | |
| AR(1) + cohort share | rho 0.19 (0.7), share 0.111 (3.1) | 0.700 | 0.62 | the share is a level shift, not drift |
| AR(1) + 2026 dummy | rho 0.32 (1.0), dummy 1.75 (2.1) | 0.592 | 0.72 | |
| geo_mix_pp | -0.12 (-0.1) | 0.001 | 1.11 | the residual does not absorb the geo term |
| geo reconciliation gap | -0.83 (-1.2) | 0.103 | 1.05 | |
| NA nights-share y/y change | 0.74 (1.0) | 0.075 | 1.07 | |
| NA minus ex-NA ex-FX ADR | 0.115 (1.4) | 0.147 | 1.02 | NA accelerated from 3Q25 (3.3 to 5.0, 4.8, 6.3, 6.8) while EMEA held 3 to 5 |

### 2.5 Residual rules on the S harness, target 2, eur and baskets (`K3_residual_rule_scores.csv`, descriptive, walk-forward, measured mix)

Ratio vs naive [jackknife min to max], drop-one samples below 1. Windows 1Q24-2Q26 (n 10) and 2Q24-2Q26 (n 9). Rules starting `K_` use the central path unless stated.

| rule | eur, 1Q24- | eur, 2Q24- | baskets, 1Q24- | baskets, 2Q24- | v3 pass | beats last_q (4 checks) | K criterion |
|---|---|---|---|---|---|---|---|
| last_q (v3 rule) | 0.916 [0.87-0.97] 10 | 0.905 [0.83-0.99] 9 | 0.876 [0.79-0.92] 10 | 0.871 [0.75-0.92] 9 | PASS | reference | |
| persistence (v2 rule) | 0.983 [0.90-1.02] 5 | 1.022 [0.90-1.09] 3 | 0.892 [0.78-0.95] 10 | 0.905 [0.77-0.99] 9 | FAIL | 0 of 4 | |
| **K primary: last_q + 0.007 x change in y/y share** | **0.912 [0.87-0.97] 10** | **0.898 [0.82-0.98] 9** | **0.873 [0.78-0.92] 10** | **0.868 [0.74-0.92] 9** | PASS | **4 of 4, and on jackknife max** | **met, margin 0.003 to 0.007** |
| last_q + 0.038 x change in y/y share | 0.899 [0.85-0.96] 10 | 0.879 [0.79-0.98] 9 | 0.875 [0.78-0.92] 10 | 0.870 [0.74-0.93] 9 | PASS | 4 of 4 ratio, 2 of 4 jackknife | met on ratio |
| K primary, high-migrant path | 0.907 | 0.892 | 0.872 | 0.866 | PASS | 4 of 4 | met |
| K primary, low-migrant path | 0.914 | 0.902 | 0.875 | 0.870 | PASS | 4 of 4 | met |
| pre-migration expanding mean, no share | 1.175 | 1.406 | 1.080 | 1.201 | FAIL | 0 | |
| mean + 0.007 x y/y share | 1.128 | 1.347 | 1.021 | 1.135 | FAIL | 0 | |
| mean + 0.038 x y/y share, central path | 0.930 | 1.097 | 0.780 | 0.868 | FAIL | 2 | |
| mean + 0.038 x y/y share, high-migrant path | 0.739 [0.64-0.85] 10 | 0.853 [0.73-0.94] 9 | 0.591 [0.52-0.66] 10 | 0.658 [0.58-0.73] 9 | PASS | 4 of 4 | post hoc, not promoted (point 8) |
| last_q + b_hat x change, b_hat walk-forward | 0.860 [0.80-0.94] 10 | 0.819 [0.70-0.94] 9 | 0.908 [0.83-0.96] 10 | 0.910 [0.81-0.98] 9 | PASS | 2 of 4 | not met |

RMSE for the primary rule 1.093 / 0.928 (eur) and 0.829 / 0.780 (baskets) pp against last_q 1.099 / 0.935 / 0.831 / 0.783. Target 1 (integer-fair ex-FX) for the primary rule: 0.985 and 1.080, identical to last_q to three decimals, since a nudge under 0.1 pp never changes a rounded point. Per-quarter margin (`K3_primary_rule_margin.csv`, midpoint FX): the rule differs from last_q only in 3Q25 (+0.001 pp), 4Q25 (+0.086), 1Q26 (+0.029) and 2Q26 (+0.034); last_q's errors in those quarters were -1.25, -0.17, -0.67 and -0.33, so every nudge reduced a squared error, by 0.004, 0.022, 0.038 and 0.022.

### 2.6 3Q26 and 4Q26 residual by scenario (`K4_residual_nowcast.csv`)

Bands are plus or minus one sd of quarterly residual changes (0.94 pp) for 3Q26 and 1.41 sd for 4Q26, as J 2.5. Card v2 carried 4.61.

| scenario | 3Q26 pp | 4Q26 pp | basis | label |
|---|---|---|---|---|
| cohort model, fitted, central (b 0.114) | 7.6 | 11.0 | 2.40 + b x y/y share (46.0, 75.0 pp) | reductio: extrapolates the fitted relation; b is three times the mechanics |
| cohort model, fitted, high-migrant (b 0.060) | 6.5 | 7.0 | same on the largest cohort | reductio |
| **cohort mechanics, central (K primary)** | **5.02** (4.1 to 6.0) | **5.22** (3.9 to 6.5) | last_q + 0.007 x change in y/y share (+24.5, +29.0 pp), chained | rule, knowable |
| cohort mechanics, high | 5.78 | 6.88 | same at 0.038 | rule at the top of the mechanics |
| lap only, residual steps | 3.93 (3.0 to 4.9) | 3.06 (1.7 to 4.4) | 2Q26 4.85 minus the 3Q25 step 0.92, then minus the 4Q25 step 0.88 | assumed: every residual change since 2Q25 is a permanent dated product step |
| lap only, disclosed bundle | 4.85 | 3.85 | 4Q26 = 2Q26 minus the bundle's roughly 1 pp GBV-minus-nights contribution in 4Q25 (D014) | sourced figure, assumed to lap in full |
| lap + tranche 2, central | 4.10 | 3.43 | lap only + 0.007 x (y/y share beyond 2Q26's 21.5 pp) | assumed |
| lap + tranche 2, high | 4.86 | 5.09 | same at 0.038 | assumed |
| persistence (v2) | 4.61 | 4.61 | mean of 1Q26 and 2Q26 | rule |
| last_q (v3) | 4.85 | 4.85 | 2Q26 value | rule |
| mean reversion | 2.40 (2.0 to 2.9) | 2.40 | 2023-25 mean, interquartile | rule |
| AR(1) on the residual | 4.37 | 4.02 | rho 0.75, iterated | rule |

### 2.7 When the reprice laps (`K4_fee_lap_schedule.csv`, central path, nights basis)

| quarter | migrated share | y/y change, pp | fee contribution to the residual, central | at 0.038 |
|---|---|---|---|---|
| 4Q25 | 12.5 | +12.5 | +0.09 | +0.47 |
| 1Q26 | 16.6 | +16.6 | +0.12 | +0.63 |
| 2Q26 | 21.5 | +21.5 | +0.15 | +0.82 |
| 3Q26 | 46.2 | +46.0 | +0.32 | +1.75 |
| 4Q26 | 87.4 | +75.0 | +0.52 | +2.85 |
| 1Q27 | 87.4 | +70.8 | +0.50 | +2.69 |
| 2Q27 | 87.4 | +65.9 | +0.46 | +2.51 |
| 3Q27 | 87.4 | +41.2 | +0.29 | +1.57 |
| 4Q27 | 87.4 | 0 | 0 | 0 |

2027 holds the 4Q26 level (assumed: migration complete by year-end per the 2Q26 letter).

---

## 3. Method

**Cohort share (K1).** Two cohorts per region: pre-existing single-fee listings (level assumed by region from the 2019 option and the December 2020 mandate's country exclusions) and split-to-single migrants in two dated tranches. Tranche 1 (27 October 2025 for PMS hosts still on the split fee, from the Guesty notice and the 3Q25 and 4Q25 letters) is placed in the countries exempted in 2020, with the NA share solved so the blended total single-fee share is 0.26 in 1Q26 (call: "over a quarter" on 7 May); 4Q25 carries 66 of 92 days because the fee applies by booking confirmation date. Tranche 2 is a monthly end-of-month path for the total share (27% flat to the May call, a step at the UK's 22 June transition, a ramp into the 15 September non-EEA deadline, the 13 October EEA/CH deadline, 100% by December), averaged within quarter and distributed to regions in proportion to each region's remaining split-fee base, with EMEA lagged in 3Q26 for the EEA deadline. Nights basis multiplies the PMS cohorts by 1.3 nights per listing (assumed). The regressor is the y/y change in the blended migrated share, since the residual is a y/y quantity. The 1 December 15% to 15.5% step on the pre-existing cohort is flagged per quarter and is worth about +0.1 pp blended at payout-neutral; it is inside the y/y from 4Q25 (one third) to 3Q26 and laps in 4Q26.

**Expected effect (K2).** Arithmetic on the sourced fee rates, three guest-fee assumptions, four pass-through cases, the pre-existing cohort, and the H card's table 2.3 increments per unit of penetration; the pre-stated coefficient, range and the implied share of the 1H26 step were written to `K2_expected_effect_prestated.csv` with a timestamp before K3 was written.

**Fits (K3).** OLS on the 14 residual observations: levels with a constant; levels without a constant on the residual minus its 2023-25 mean (2.398); first differences with and without a constant; for each K1 variant and basis. Alternatives on the same 14 quarters as listed in 2.4; AR(1) specifications on 13. Standard errors are OLS; with three informative quarters they describe the fit, not a sampling distribution.

**Rules and scoring (K3).** Every rule uses residual history strictly before t and the K1 share for t. Primary rule: `last_q` plus 0.007 times (d4share_t minus d4share_{t-1}), the coefficient fixed at the K2 central value and never fitted. Sensitivities: the same at 0.038; an expanding mean over pre-migration quarters plus the coefficient times d4share_t; and a walk-forward fitted coefficient (prior quarters with at least 2 pp of share, demeaned levels, no constant; the 3Q25 quarter at 0.2 pp is excluded because it gives a degenerate slope of 2.9 and a 38 pp prediction). Each rule's residual path goes through `S.exfx_from_residual(..., mix_variant="measured")`, then `S.score`, then `S.preregistered_pass`; the K criterion compares each rule's `ratio_vs_naive` and `jackknife_ratio_max` with `last_q`'s on the four target-2 rows (eur and baskets, both windows). The knowable flag records that the tranche dates precede every scored print while the level calibration to "over a quarter" and "about half" is disclosed at the 1Q26 and 2Q26 prints themselves; the base term inherits S's v2 flag.

**Nowcast (K4).** Scenarios as in 2.6. The lap-only arithmetic treats each residual change since 2Q25 as a permanent level step dated to the products that launched in that quarter and drops it from the y/y at its anniversary; the disclosed-bundle variant uses management's 4Q25 GBV-minus-nights gap instead. The lap-plus-tranche-2 scenarios add the fee mechanics only on the cohort beyond what the 2Q26 residual already carries, to avoid counting the reprice twice.

---

## 4. What this can and cannot identify

- **The criterion is met on the letter and it should not be read as evidence.** The primary rule is `last_q` with a nudge under 0.1 pp in four quarters. It beats `last_q` because the residual rose in every one of those quarters; a coefficient of 0.007 on any series that rose in 4Q25-2Q26 would have done the same. The sign test on four helped quarters is p 0.06, and the target-1 line is unchanged to three decimals. The harness cannot distinguish the primary rule from `last_q` at n 10, and the note does not claim it can.
- **The fitted coefficient rejects the reprice as the explanation of the step, but n 14 with three informative quarters cannot say what the step is.** The cohort share, the RNPL share and a 4Q25-onward dummy are the same regressor to within measurement: correlations 0.97 and 0.89. Everything dated to October 2025 to February 2026 ties. The one thing the data does separate is drift from a level shift: with the share in the AR(1), rho falls from 0.75 to 0.19.
- **The cohort share is assumed in its regional split and its pre-existing level; only two levels and the tranche dates are disclosed.** The coefficient scales inversely with the assumed cohort size (0.06 on the largest path, 0.26 on the smallest), which is why the conclusion is stated on the ratio to the mechanics rather than on the coefficient alone: on every path it is at least 1.6 times the top of the range.
- **The mechanics are about the average listed-price response and the residual is a blended y/y.** If early switchers over-reprice and late switchers do not, the blended coefficient would drift over 2026; nothing here can see that. The quote-index addendum could not recover a reprice step in same-listing quotes either (excess mass 0.0 to 1.6% per pair against a 10% noise floor).
- **Management's bundle ADR contribution is the best anchor and it is a joint figure.** "Over 200 bp of nights, roughly 300 bp of GBV" (4Q25) and "approximately three points, approximately four points" (1Q26) give the three features together about 1 pp of ADR in each quarter. The fee reprice is at most a fraction of it; the rest is RNPL's mix into larger homes, which the H decomposition's unit-size term (booked capacity from reviews) may or may not capture. No disclosure splits the bundle.
- **The lap arithmetic is a scenario.** It assumes every residual change since 2Q25 is a dated product step and nothing replaces it. The 1Q26 and 2Q26 steps (0.68 and 0.47) stay in the y/y until 1H27 under the same assumption. The harness has never scored a lap quarter, so the choice between the rule (5.2 in 4Q26) and the arithmetic (3.1 to 3.8) cannot be made on the backtest.
- **Measured mix is an upper bound**, as S section 4: the scored paths use realised quarter-t mix terms.

---

## 5. Next evidence

1. **The disclosure that would identify the fee effect:** a split of the bundle's ADR contribution by feature, or the RNPL GBV share and RNPL nights share for the same quarter (D's next-evidence item 2; their ratio is the RNPL ADR premium, which pins the mix leg and leaves the fee leg as the remainder). Either turns the joint 1 pp into two numbers.
2. **The data that would identify it:** a same-listing realised-rate series (AirDNA or Transparent calendar-inferred booked rates) for a set of listings with known switch dates; the switch date is visible in the listing's fee display and in PMS notices. That is a treated-versus-control listed-price test that Inside Airbnb quotes cannot support (J section 1, quote-index addendum).
3. **5 November scores the two stories.** If the 3Q26 residual (backed out of the printed ex-FX ADR and I's measured mix) prints near 5.0 the rule stands and the reprice question stays open; near 3.9 to 4.1 the lap arithmetic is the better description and P's 4Q26 residual should move to the 3.1 to 3.8 band. Management's fee-migration commentary on the call (any figure for the migrated share or for the take-rate lift) updates K1 directly.
4. **For P:** carry the K term as +0.007 times the change in y/y migrated share (+0.17 pp in 3Q26, +0.20 pp in 4Q26, band to +0.94 and +1.09), labelled a mechanics line; report the 4Q26 residual as a scenario band, 3.1 (lap only) to 5.2 (rule), around the v3 rule's 4.85; do not use the fitted coefficient anywhere.

---

## 6. Files

| File | Contents |
|---|---|
| `analysis/src/adrv3/K1_cohort_share.py` | cohort share build: pre-existing and migrated cohorts by region, three paths, two bases, assumptions table |
| `analysis/src/adrv3/K2_expected_effect.py` | fee mechanics arithmetic and the pre-stated coefficient, timestamped |
| `analysis/src/adrv3/K3_fit_and_score.py` | fits, alternatives, residual rules, S harness scoring, margin table, criterion table |
| `analysis/src/adrv3/K4_residual_nowcast.py` | 3Q26 and 4Q26 scenarios and the fee lap schedule |
| `data/processed/adrv3/K/K1_migrated_cohort_share.csv` | 480 rows: quarter x region (4 + blended) x basis x variant, shares, y/y changes, step and label columns |
| `data/processed/adrv3/K/K1_assumptions.csv` | every K1 parameter with central, low, high, label and source |
| `data/processed/adrv3/K/K2_expected_effect.csv` | 20 rows: pass-through cases, pre-existing cohort, H card cross-check, all timestamped |
| `data/processed/adrv3/K/K2_expected_effect_prestated.csv` | the pre-stated sign, coefficient, range and implied share of the step |
| `data/processed/adrv3/K/K3_residual_fit.csv` | 24 fits: 3 variants x 2 bases x 4 specs, with the ratio to the expectation |
| `data/processed/adrv3/K/K3_alternatives.csv` | 15 alternative models and the collinearity diagnostics |
| `data/processed/adrv3/K/K3_residual_rule_scores.csv` | 176 rows: 22 models (4 reference rules, 6 K rules x 3 cohort paths) x 2 targets x 2 windows x (1 or 3) estimators, with last_q comparison columns |
| `data/processed/adrv3/K/K3_walk_forward_paths.csv` | per-quarter scored paths for every model, target and estimator |
| `data/processed/adrv3/K/K3_rule_residual_paths.csv` | per-quarter residual prediction of every rule, with the share, its change and the walk-forward b |
| `data/processed/adrv3/K/K3_primary_rule_margin.csv` | per-quarter error of last_q and the primary rule, the nudge and the squared-error change, three estimators |
| `data/processed/adrv3/K/K3_pass_table.csv` | S.preregistered_pass output for every model |
| `data/processed/adrv3/K/K3_k_criterion.csv` | v3 verdict, last_q comparison and the K criterion per model, with the sign test |
| `data/processed/adrv3/K/K4_residual_nowcast.csv` | 26 rows: scenario x quarter with band, basis, label and knowable flag |
| `data/processed/adrv3/K/K4_fee_lap_schedule.csv` | migrated share, y/y change and fee contribution by quarter to 4Q27, three paths |
