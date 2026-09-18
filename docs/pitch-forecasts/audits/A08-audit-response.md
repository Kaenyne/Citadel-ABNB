# Response to audit A08 (F01–F04: q1-27-nights-guide-above-82, q1-27-revenue-guide-growth, fy27-margin-guide, fy27-sm-share-above-219)

Response date: 2026-09-17
Responds to: `A08-research-audit.md` (Astra, gpt-6-astra, read-only)
Revised research: the four `research-log.md` files (revision 2) and the four `forecasts/2026-09-17-forecast.json` files (revision 2)
Revised models (revision-1 scripts and CSVs left untouched as the audit trail):
- `questions/q1-27-nights-guide-above-82/datasets/f01_model_v2.py` (+ `q4_adopted_v2_summary.csv`, `f01_v2_summary.csv`, `f01_v2_sensitivity.csv`)
- `questions/q1-27-revenue-guide-growth/datasets/f02_model_v2.py` (+ `f02_v2_summary.csv`, `f02_v2_percentiles.csv`, `f02_v2_hist.csv`, `f02_v2_sensitivity.csv`)
- `questions/fy27-margin-guide/datasets/f03_f04_joint_v2.py` — ONE joint simulation for F03, F04 and B12 (+ `f03_v2_summary.csv`, `f03_v2_sensitivity.csv`; and `f04_v2_summary.csv`, `f04_v2_conditionals.csv`, `f04_v2_sensitivity.csv` in the F04 folder)
Reproduction script: `A08-reproduce.py` (the audit's script, saved verbatim; output `A08-reproduce.stdout.txt`, reproduced at the end of this file)

## Summary

Twenty-one findings. Nineteen accepted, two accepted in part (A08-08, A08-11), none rejected. Every number in the audit reproduced exactly: the script ran clean from the repo root with `py -3.13 -B` (no path fix needed — the audit's `python` fallback note does not apply here), and the four model recomputations (F01 tree 0.1826, F03 strict 0.015/0.045/0.100/0.360/0.480, F04 0.5809 with conditionals 0.283/0.437/0.581/0.784/0.621 aggregating to 0.614, F02 percentiles and tail masses) match the saved CSVs and in-memory reruns.

Headline numbers, revision 1 → revision 2:
- **F01** P(1Q27 nights descriptor ≥ +8.2%): **0.22 (0.12–0.35) → 0.28 (0.16–0.42)**. Astra 0.26.
- **F02** 1Q27 revenue-guide growth: median **+9.4% → +10.5%**; percentiles 3.6/4.9/7.0/9.4/12.0/14.3/15.6 → **5.1/6.2/8.3/10.5/12.8/14.8/16.1**; P(<10) 0.56 → 0.45; P(<9.4) 0.48 → 0.36; P(≥12) 0.25 → 0.34. Astra median +10.3%.
- **F03** FY27 margin-guide vector: **0.08/0.17/0.27/0.38/0.10 → 0.02/0.04/0.10/0.36/0.48** (literal convention; (e) is now the modal option). Astra 0.03/0.05/0.10/0.32/0.50.
- **F04** P(FY27 S&M ex-SBC ≥ 21.9%): **0.55 (0.40–0.68) → 0.55 (0.40–0.68)**; conditionals now from a joint model, a 0.37 / b 0.43 / c 0.53 / d 0.64 / e 0.50, aggregating to 0.548. Astra 0.55.

What moved the numbers. F03 moved because the audit is right about the question: option (e) says "no numeric FY27 margin guidance", and a "stable year-over-year" sentence is not a number — the rev-1 convention had converted three of five historical February forms into numeric buckets. F01 and F02 moved mostly for a run-level reason the audit did not raise but the run requires: both now condition on the one adopted 4Q26 nights object (R16/B13: mean 8.7, P(≥134.0m) 0.29) instead of rev 1's own decomposition-only mixture (mean 7.8); the resolver fix the audit asked for (A08-02) moved F01 by −1 point on the old object, the adopted object by +11. F02 also picks up C01 rev 2's validated residual structure including the single-fee step, which rev 1 had omitted. F04 did not move: the audit's corrections changed the anchor (0.30 → 0.33, D&A-corrected residual with a real uncertainty model), the base rate (0.55 → 0.50, FY26E removed) and the justification for the 3-point trim (the marketing-cut "precedent" does not exist), not the centre.

Convention decision for F03 (made explicitly, as the run asked): **literal**. Numeric floor/point/range → (a)–(c) or the <35.5 leg of (d); explicit down/investment-year language → (d) (the option names it); every other qualitative sentence, a dollar-only sentence, and no sentence → (e). Reasons: (i) the option text enumerates exactly one qualitative form that maps to a bucket, so the others do not; (ii) brief rule 3 lets a log resolve ambiguity but not change the question, and rev 1's mapping made (e) narrower than written; (iii) a flat-margin sentence and an economic expectation of ~36% are different objects (the audit's phrase, and correct). B12 (`bonus-fy27-investment-year`) already uses the literal reading for its own text; from the joint draws B12-literal = 0.51 and B12-material = 0.38 against its published 0.50 / 0.38, so F03 and B12 are now one object: B12-literal = P(F03 d) + P(numeric floor in (b)/(c) strictly below the one-decimal print) = 0.36 + 0.15.

## Finding-by-finding

### A08-01 (critical, F03) — qualitative sentences converted into numeric buckets: accepted
Reproduced: `run(strict_qual_to_e=True)` on the rev-1 model gives 0.014980 / 0.044875 / 0.099845 / 0.360050 / 0.480250; the rev-1 log's "strict" vector was the same object rounded to a 1.01 sum. The literal convention is adopted (decision above). Revision-2 vector on the joint model with the C04 rev-2 FY26 print: 0.013 / 0.041 / 0.101 / 0.357 / 0.490, published as **0.02 / 0.04 / 0.10 / 0.36 / 0.48** after the (a) gate (A08-14). The rev-1 mapping is retained only as a reference sensitivity (0.08 / 0.16 / 0.28 / 0.41 / 0.07 on the new print distribution).

### A08-02 (critical, F01) — "higher than Q4" at a 7.5 print, "nearly as strong" decrement: accepted
Reproduced: draws classified Yes through the "higher" branch with Q4 in [7.5, 8.2) contribute 0.629 points; removing them takes the rev-1 tree 0.1826 → 0.1763. Fix in `f01_model_v2.py`: `up_floor = 8.2` (a sentence implying only "> Q4" clears the bar only when the Q4 print itself does); "nearly as strong" is now an explicit branch (35% of the below-print half of the stable band) resolving Yes iff the Q4 print ≥ 9.2, stated as a convention with sensitivities at 8.7 (0.289) and "never Yes" (0.278) — it moves the number by ≤ 1 point. On the rev-1 object the corrected tree gives 0.173; on the adopted object 0.287.

### A08-03 (major, F01–F04) — three estimates not independent: accepted
Reproduced F01's "Street through the tree" at 0.436 (v2: 0.434). Every §5 now opens with an independence label ("partially dependent"), every anchor that is a model output or a repo prior carries NOT_INDEPENDENTLY_DERIVED in the JSON, and Astra's independent number is recorded beside each anchor. Observed consensus levels (LSEG 1Q27 $3,010M; MODL 134.0m) are distinguished from the model-created event probabilities built on them.

### A08-04 (major, F04) — Street residual omits D&A: accepted
Reproduced: other four lines $6,807.31M, D&A $82.54M; corrected S&M $3,328.46M / $15,819.34M = **21.04%** (rev 1: 20.52%). The other lines are labelled team assumptions. The anchor level moves 0.5pp closer to the bar.

### A08-05 (major, F04) — dispersion used as predictive sd: accepted
Reproduced: `lseg_ebitda_sd_musd` = $154.22M is analyst dispersion; the mechanical Gaussian tail on the corrected residual is 18.90%. Revision 2 keeps 0.19 as a labelled illustration and builds the anchor probability from an explicit uncertainty model (`street_anchor()`: EBITDA sd √(154² + 175²) adding a ~3% one-year-ahead realisation error [judgment], other lines sd $200M; share sd 1.9pp) → **0.33**. Rev 1's "P ≈ 0.10 raised to 0.30" is withdrawn; the anchor is 0.33 with its model stated.

### A08-06 (major, F04/F03) — conditionals do not aggregate; "3-point shrink" not uniform: accepted
Reproduced: rev-1 exact conditionals 0.283/0.437/0.581/0.784/0.621 weighted by the rev-1 F03 vector give 0.614 against the unconditional 0.581; the published table aggregated to 0.549 only because the shrink was non-uniform. Fix: F03 and F04 are one simulation (`f03_f04_joint_v2.py`) with a latent reinvestment-intensity z that tilts the F03 regime (haircut/investment-year up, expand down) and adds 3.0 pts per sd to FY27 S&M growth, plus a link from the FY26 print surprise to the FY26 S&M base (−$40M per sd). Conditionals read off the same draws: a 0.40 / b 0.46 / c 0.56 / d 0.67 / e 0.53, Σ = 0.581 exactly. The final table subtracts a uniform 0.03 (the judgment trim, see A08-09) from every row so it aggregates to 0.548 ≈ 0.55. Removing the z link flattens the table to 0.40/0.48/0.58/0.60/0.58 (§7 of the F04 log).

### A08-07 (major, F04) — FY26E in the base rate: accepted
Reproduced from `02_panel_annual.csv`: completed-year increases ≥ 0.6pp are 2/4 (2022–25), 2/3, 2/2. FY26 is removed from the reference class and kept as a conditioning input; base-rate estimate 0.55 → 0.50 (read 0.50–0.60 with the regime sensitivity).

### A08-08 (major, F04) — management attribution overstated: accepted in part
Reproduced: V023 announces future products; H07/H08 are WS05 implications (`confidence = medium`); no quoted management statement gives an FY27 marketing growth rate; `GS26.html` is absent locally (ledger rows quote-verified against the recorded stockanalysis.com URL). Accepted: claim 7 re-attributes every sentence, and the +15%/+11% pair is labelled the team's spending interpretation. In part: the pair stays as the model's *central* growth assumption rather than being demoted to "scenarios", because the line build is the pitch's adopted margin view (`40_line_build.md`) and the question's decomposition has to run on some path; the sensitivity table shows what the alternative centres (+10, +12, +17, +20, +22) do.

### A08-09 (major, F04) — marketing-cut precedent is false: accepted
Read the 3Q24 letter: "Q4 2024 Adjusted EBITDA Margin is expected to decline relative to the same time period last year due to **higher** marketing and product development expenses" — the opposite of a cut; the $176.7M cut is `short_with_q4_marketing_cut` in `40_short_case_summary.csv`, a modelled action. Claim 10 rewritten; the 3-point trim below the decomposition is now a labelled judgment toward the base rate (0.50) and the anchor (0.33), not a historical-evidence haircut. The number stays at 0.55 because the trim's size was never derived from the precedent.

### A08-10 (major, F02) — stale anchor: accepted
Reproduced: `revenue_obs_date = 2026-08-13`, pull 2026-09-13, 35 days old at forecast; no 2027Q1 row in the L0 register. Checked for a fresher observation: yfinance `revenue_estimate` carries only 0q/+1q (1Q27 is +2q), so **no fresher external 1Q27 observation exists**; the row is relabelled a dated comparison in the log, JSON and monitoring calendar (the January refresh must record a new `revenue_obs_date`).

### A08-11 (major, F02) — cross-quarter transmission not measured: accepted in part
Reproduced the same-target join: n 18, κ +0.565, slope 0.988, r 0.993 (2023+: 0.960, n 14). Accepted: the −1.9% Q1 adjustment is labelled an assumption, the κ slope is no longer cited for it, and zero / half / full transmission are tabulated (+12.4 / +11.3 / +10.3; +13.1 / +12.0 / +11.0 with the W2 February premium). In part: the full-transmission reading (+11.0%) is still the one carried as "gap-adjusted", because the Street phases 1Q27 from FY27 and a below-Street 4Q26 guide mechanically lowers the FY27 base it phases from; the choice is now visible and the raw +12.4% is the recorded anchor_value.

### A08-12 (major, F01) — 12/16 directional is wrong: accepted
Reproduced: 16/16 directional pre-2025; bucket era 3/4; 17/17 sentences since 2Q22. Claim 4 corrected and the 72/24/4 split labelled a regime judgment (n 4).

### A08-13 (major, F01) — 4Q21 comparator case excluded: accepted
Reproduced: comparator 83.1m over the 1Q21 actual 64.4m implies > +29.04%. Included as a provable Yes-type case; the class count becomes 3/5 and the log says explicitly it is too regime-dependent to be the forecast (the three Yes-types came with Q4 prints of 25+, 20.2 and 12.3).

### A08-14 (minor, F03) — strict vector sums to 1.01; no gate on (a): accepted
Reproduced (sum 1.01). Moot for the strict vector (no longer published); the revision-2 vector sums to 1.000 and the extreme-probability gate was completed for (a): model 0.013, edge cases (a "36–37%" range resolving on its midpoint, "approximately 36.5%" chosen to match the Street's 36.45%, a T2 floor on a ≥ 36.75 print) → 0.02; (b) 0.04 audited and left at the model value; the 1-point move from (e) to (a) is recorded as the small-tail trade-off.

### A08-15 (minor, F03) — February up-days 6/6 is wrong: accepted
Reproduced: 4Q23 print 2024-02-13 ret_1d −1.7%, exc_1d −2.8%; 5/6 on both. Claim 10 corrected; the brief's inherited "positive 6 of 6" is flagged for the orchestrator (it is quoted in `00_BRIEF.md` reaction base rates and in R16's impact note).

### A08-16 (minor, F02) — "first sub-teens guide since 2023" is wrong: accepted
Reproduced: 1Q25 guide 4–6% (mid 5%); 4Q24 guide ≈ +8.9% dollar-implied. Phrase withdrawn from claim 6 and the JSON; the forecast is described as a deceleration from the 1Q26 guide (+15%) and print (+18%).

### A08-17 (minor, F02) — sd misstated, growth-range count understated: accepted
Reproduced: rounded series sd 4.48; dollar-implied series −1.81/−0.28/−3.84/+6.41, mean +0.12, sd 4.44; 4 of 5 February letters printed a growth range. Claim 2 now uses the dollar-implied series (the one this question resolves on) and the base-rate estimate is re-derived from it (+10.7).

### A08-18 (minor, F01) — 100bp quote misattributed; arithmetic wrong: accepted
Read the 1Q26 letter: the "approximately 10%" ex-conflict figure is in the Q1 results section; the "roughly 100bps headwind" is the Q2 2026 outlook assumption. Relative to 4Q25's 9.82, the 10% comparator is 0.18pt *higher*; the reported 9.15 comp is 0.67pt easier. Claim 8 rewritten; the conflict recovery is modelled as a base effect (≤ ~0.85pt) already inside WS06 v2's +1.0 Middle East base effect rather than as an "easier ex-conflict comparator".

### A08-19 (minor, F01/F02) — Kalshi fields and "inconsistency": accepted
Reproduced from the saved JSONs: `volume_fp` 277.2 / `open_interest_fp` 87.0 at >575m; 428.1 / 423.1 at >148m; `volume_24h_fp` 0 and `updated_time` 2026-08-04 everywhere. Claims 11 (F01) and 16 (F02) rewritten: inactive, stale adjacent snapshots; the annual-minus-quarterly subtraction is described as a staleness illustration, not a mathematical inconsistency. Zero weight unchanged.

### A08-20 (minor, F04) — GAAP vs ex-SBC basis; wrong guide IDs: accepted
Reproduced: ex-SBC changes −143.8bp (FY22) and −22.6bp (FY23); IDs …-FY2023-065 and …-1Q23-063. Claim 8 labels the GAAP basis, shows the ex-SBC outcomes alongside, and fixes the IDs.

### A08-21 (minor, F02) — 1.6 vs 1.7 sd discrepancy: accepted
Reproduced (`n4_sd=1.7` default; the log said 1.6). Moot in revision 2 — the v2 script is the sole source of the published numbers and draws 4Q26 nights from the adopted object (sd 2.05 as implemented); the rev-1 discrepancy is recorded in the revision notes.

## Re-runs on the objects that landed after the A08 forecast

- **F01/F02 on the adopted 4Q26 distribution (R16/B13).** Implemented as a sampler mirroring `r16_model.py`: 0.5 V1 (Q3 ~ N(9.67, 1.70) → Q4 = 8.1 + 0.5(Q3 − 9.67) + N(0, 1.4), 12% tail 5.5 ± 1.5) + 0.3 V2 (C02 bucket vector × midpoint + N(0.9, 1.3); R16's "V2 used" 0.40 sits between its 0.6 and 1.2 cushion rows) + 0.2 V3 (N(9.93, 1.23)). As implemented: P(≥134.0m) 0.29 (R16 quotes 0.27), P(≤131.0m) 0.27 (B13 0.26), mean **8.70** — R16's "mean ~8.3" is the V1-conditional-means shortcut, not the blend's mean; the blend is right-skewed by V2/V3. Effect: F01 tree 0.173 → 0.287; F02 median +9.4 → +10.3 (before the residual change).
- **F02 on C01 rev 2.** The C01 rev-2 residual structure (ε N(−0.19, 2.05) validated ex-COVID, leakage Bernoulli(0.40) × −0.84%, fee step 45/40/15) replaces rev 1's single N(−0.5, 2.5) tilt: +0.2 on the median (fee +0.4, leakage/bias −0.2). The 4Q26 guide-vs-Street gap (C01 rev 2: −1.9% at the median, P(below) 0.72) enters only through the anchor's transmission table.
- **F03/F04 on C04 rev 2's FY26 print.** FY26 print = C04's internal MC (mean 35.72, sd 0.58) with C04's own floor-defence rule (below 35.5: p 0.50 Q4 cost cut restores 35.5 + 0.1): mean 35.82, sd 0.49, **P(<35.5) 0.18** (rev 1: 0.09), 35.5–35.9 0.51, 36.0–36.4 0.23, ≥36.5 0.09. Effect on F03: (d) +0.03 via T2 floors that round below 35.5; on F04: nil directly (the FY26 print enters F04 only through the S&M-base link).
- **B12 reconciliation.** From the joint draws: literal 0.51, material 0.38 (B12's own: 0.50 / 0.38). Consistent within 1 point; the difference is B12's rev-1 FY26 object. F03 (d) 0.36 ≠ B12 literal 0.50 by construction (B12 counts a T2 "at least 35.5%" against a 35.7 print as Yes; F03 puts it in (c)); the memo should cite B12 for the *content* ("guide below FY26") and F03 (d) for the *form*.
- **S03 rev 2, B08, B17.** Context only: B08 (AI/hosting cost step 0.38) and B17 (take-rate guide-down 0.42) support T5 0.10 → 0.12 in F03; S03 does not enter the F questions.

## Reconciliation with Astra's numbers (the > 10-point rule)

| Q | rev 2 | Astra | gap | decision |
|---|---|---|---|---|
| F01 | 0.28 | 0.26 | +2 | no asymmetry needed; both sit on the adopted object's ~0.36 mass above 9.5 and a ~0.5–0.7 language pass-through |
| F02 | +10.5 | +10.3 | +0.2 | inside noise; the fee step is the named difference |
| F03 (e) | 0.48 | 0.50 | −2 | none needed |
| F03 (d) | 0.36 | 0.32 | +4 | within tolerance; the joint model's T2 floors below 35.5 (P(FY26 < 35.5) 0.18) and T5 0.12 are the named sources |
| F04 | 0.55 | 0.55 | 0 | coincide; conditionals differ in shape (joint model flatter at (a)/(b) because those are rare numeric-floor cases driven by the FY26 print level, Astra's are elicited) |

Versus the anchors: F01 −15 (Street bar as a certain centre vs 0.2 weight in the adopted object; every repo 1Q27 object at or below the bar); F03 −19 on (d) / +15 on (e) (the WS05 prior reads "stable" as a 0-haircut numeric floor; the literal question sends it to (e)); F04 +22 (the Street's FY27 margin is the one line the team's margin build disputes; base rate and decomposition agree without it). Each is written in the respective §5.

## What the audit missed

1. **F01/F02 used their own 4Q26 print mixture (mean 7.8) while R16/B13, forecast in the same run, adopted a blended 4Q26 object (mean 8.7).** This is the single largest driver of both revisions (+11 points on the F01 tree, +0.9pt on the F02 median) and the audit's independent F01/F02 numbers implicitly assume something closer to the adopted object. The run now conditions all Q4-dependent questions on one distribution; the sampler is duplicated in `f01_model_v2.py` and `f02_model_v2.py` and must be kept in step with `r16_model.py`.
2. **F02 omitted the EEA/CH single-fee step that C01 carries** (claim 11 mentioned it; the model did not draw it). It is complete by 13 Oct 2026 and applies in full to 1Q27 recognition: +0.4pt on the median.
3. **The F02 anchor cannot be refreshed from any available source** (yfinance carries only 0q/+1q; L0 has no 2027Q1 row); the audit asked for a newer observation or a statement that none exists — the latter is now in the log.
4. **R16's "mean ~8.3" for the adopted object is a shortcut**; the blend's mean is 8.7 (its two tail probabilities reproduce). Recorded in F01 claim 14 for X01.
5. **F04's Street-residual anchor and the F03 (a)/(b) buckets share a mechanism the rev-1 conditionals ignored**: a high FY26 print (needed for a numeric ≥ 36 floor) is itself evidence of a lower 2H26 S&M base. The joint model carries it (−$40M per sd of print surprise); it is what makes P(F04 | a) < P(F04 | c) without eliciting the gap.
6. **The brief's "February Q4 prints positive 6 of 6"** (A08-15) is inherited by R16's impact note and the reaction base rates in `00_BRIEF.md`; flagged for the orchestrator (not edited here — outside this batch's files).

## Reproduction output

`py -3.13 -B docs/pitch-forecasts/audits/A08-reproduce.py` from the repo root, 2026-09-17 (no edits to the script; exit 0):

```
F01 pre-2025 formats
{'directional': 16}

F01 bucket outcomes
print_quarter target_period  value_mid  value_high  actual  top_beat
         3Q25          4Q25        5.0         6.0    9.82      3.82
         4Q25          1Q26        8.0         9.0    9.15      0.15
         2Q26          3Q26       11.0        12.0     NaN       NaN

F01 resolved bucket beats
{'n': 2, 'above_top': 2}

F01 nights statements since 2Q22
17

F01 2019-comparator implied lower growth bound
29.037267080745323

F02 Q1 cushions
print_quarter target_period  value_mid  actual  cushion_pct
         4Q21          1Q22     1445.0  1509.0     4.429066
         4Q22          1Q23     1785.0  1818.0     1.848739
         4Q23          1Q24     2050.0  2142.0     4.487805
         4Q24          1Q25     2250.0  2272.0     0.977778
         4Q25          1Q26     2610.0  2678.0     2.605364

F02 cushion statistics
{'mean': 2.8697503760487697, 'median': 2.605363984674325, 'std': 1.5605678839881338}

Q1 target window 2023+
{'n': 4, 'mean': np.float64(2.4799215340748026), 'sample_sd': np.float64(1.4946747652299393)}

Q1 target window 2024+
{'n': 3, 'mean': np.float64(2.6903155468336326), 'sample_sd': np.float64(1.7565549058011776)}

F02 Q1 lambda and last-two-season PIT errors
quarter  lambda_pct        pred  error_pct
   1Q21   13.411825         NaN        NaN
   1Q22   13.121739         NaN        NaN
   1Q23   12.802817 1883.883067   3.623931
   1Q24   13.034483 2130.134354  -0.553952
   1Q25   12.325497 2381.337785   4.812403
   1Q26   12.612245 2692.384548   0.537138

F02 dollar-implied Q1-minus-Q4 growth changes
{'values': [-1.8141801929934864, -0.27763028668799095, -3.8398587568480904, 6.409018627896401], 'mean': np.float64(0.11933734784170835), 'sample_sd': np.float64(4.439647049921979)}

F02 listed rounded-change sample SD
4.481443219916251

F02 February numeric growth-range count
4

February reaction and guide-gap panel
quarter print_date  ret_1d  exc_1d  guide_vs_street_pct
   4Q20 2021-02-25    13.3    12.9                  NaN
   4Q21 2022-02-15     3.6     3.7               16.532
   4Q22 2023-02-14    13.4    12.6                5.621
   4Q23 2024-02-13    -1.7    -2.8                0.985
   4Q24 2025-02-13    14.4    14.0               -2.174
   4Q25 2026-02-12     4.6     4.4                3.162

February positive returns
{'n': 6, 'raw_positive': 5, 'excess_positive': 5}

February guide vs Street, 2022+
{'n': 5, 'above': 4, 'mean_gap_pct': np.float64(4.8252)}

February guide vs Street, 2023+
{'n': 4, 'above': 3, 'mean_gap_pct': np.float64(1.8985)}

February guide vs Street, 2024+
{'n': 3, 'above': 2, 'mean_gap_pct': np.float64(0.6576666666666666)}

F02 historical pre-guide vendor/timestamp rows
period            vendor  value as_of_timestamp
2022Q1 CNBC unattributed 1240.0      2022-02-15
2023Q1         Refinitiv 1690.0      2023-02-14
2024Q1              LSEG 2030.0      2024-02-13
2025Q1              LSEG 2300.0      2025-02-13
2026Q1              LSEG 2530.0      2026-02-12

F02 2027Q1 L0 row count
0

F02 separate 1Q27 consensus observation
period_code period_end  revenue_mean_musd  revenue_n  revenue_sd_musd revenue_obs_date  ebitda_mean_musd  ebitda_n                                                   vendor pull_timestamp_local quarter
        FQ3 2027-03-31         3010.32375         21          49.4461       2026-08-13         610.73207        19 LSEG (lseg-data desktop, TR.RevenueMean / TR.EBITDAMean)    2026-09-13T011505    1Q27

Same-target revision regression 1900+
{'n': 18, 'mean_kappa': np.float64(0.565339187345682), 'slope': np.float64(0.9884399200165607), 'correlation': np.float64(0.9927270307102302)}

Same-target revision regression 2023+
{'n': 14, 'mean_kappa': np.float64(0.5972065048791331), 'slope': np.float64(0.9603862325982235), 'correlation': np.float64(0.9939686027781173)}

Same-target revision regression 2024+
{'n': 10, 'mean_kappa': np.float64(0.5720198206643934), 'slope': np.float64(0.9707223061005231), 'correlation': np.float64(0.9895407147696154)}

F03 February FY statements
print_quarter target_period                                                                                                quote  numeric_in_quote
         4Q21        FY2022                         we would expect Adjusted EBITDA margin to be directionally in-line with 2021             False
         4Q22        FY2023 For the full year 2023, we expect to maintain the strong Adjusted EBITDA margin we delivered in 2022             False
         4Q23        FY2024              For the full-year 2024, we expect to maintain an Adjusted EBITDA Margin of at least 35%              True
         4Q24        FY2025                            we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%              True
         4Q25        FY2026                           For 2026, we expect our Adjusted EBITDA Margin to be stable year-over-year             False

F03 numeric/qualitative counts
{False: 3, True: 2}

F03 resolved February numeric floor beats
target_period  value_low  actual  beat_bp
       FY2024       35.0    36.4    140.0
       FY2025       34.5    35.1     60.0

F04 reported annual ex-SBC shares
 year   revenue  sm_gaap  sbc_sm  sm_cash     share  change_pp
 2018  3651.985 1101.327  12.465 1088.862 29.815621       NaN
 2019  4805.239 1621.519  23.919 1597.600 33.247046   3.431425
 2020  3378.199 1175.325 435.272  740.053 21.906732 -11.340314
 2021  5991.760 1186.332 100.000 1086.332 18.130432  -3.776299
 2022  8399.000 1516.000 114.000 1402.000 16.692463  -1.437969
 2023  9917.000 1763.000 130.000 1633.000 16.466673  -0.225790
 2024 11102.000 2148.000 170.000 1978.000 17.816610   1.349936
 2025 12241.000 2588.000 212.000 2376.000 19.410179   1.593569

F04 observed >=0.6pp increases, 2022-2025
{'n': 4, 'hits': 2}

F04 observed >=0.6pp increases, 2023-2025
{'n': 3, 'hits': 2}

F04 observed >=0.6pp increases, 2024-2025
{'n': 2, 'hits': 2}

F04 H1 2025
{'sm_cash': np.float64(1158.0), 'revenue': np.float64(5368.0), 'share': np.float64(21.572280178837556)}

F04 H1 2026
{'sm_cash': np.float64(1504.0), 'revenue': np.float64(6286.0), 'share': np.float64(23.92618517340121)}

F04 Street residual accounting bridge
{'other_costs': np.float64(6807.314603339216), 'DA': np.float64(82.53588239963007), 'uncorrected_SM': np.float64(3245.925466660784), 'uncorrected_share': np.float64(20.51871710578971), 'corrected_SM': np.float64(3328.4613490604142), 'corrected_share': np.float64(21.040457496759608), 'dispersion_tail_NOT_predictive': 0.1889769910945882}

F04 exact line-build base share
21.856779508113497

Published F03 vector sum
1.0

Published strict F03 vector sum
1.01

Published F03/F04 total probability
0.5494

Saved model conditional weighted probability (CSV rounded)
0.61382

kalshi_KXABNBA_open_20260917T031845Z.json
                    ticker yes_bid_dollars yes_ask_dollars volume_fp volume_24h_fp open_interest_fp                updated_time
KXABNBA-27FEBNEB-600000000          0.0500          0.0800    294.02          0.00           170.00 2026-08-04T18:47:36.451419Z
KXABNBA-27FEBNEB-595000000          0.0500          0.0800    293.01          0.00           160.02 2026-08-04T18:47:36.451419Z
KXABNBA-27FEBNEB-590000000          0.0800          0.1200    142.03          0.00            52.02 2026-08-04T18:47:36.451419Z
KXABNBA-27FEBNEB-585000000          0.1000          0.1500     36.01          0.00            14.01 2026-08-04T18:47:36.451419Z
KXABNBA-27FEBNEB-580000000          0.1900          0.2800     68.01          0.00             2.02 2026-08-04T18:47:36.451419Z
KXABNBA-27FEBNEB-575000000          0.3700          0.4100    277.20          0.00            87.02 2026-08-04T18:47:36.451419Z
KXABNBA-27FEBNEB-570000000          0.6300          0.7100    162.01          0.00            86.01 2026-08-04T18:47:36.451419Z
KXABNBA-27FEBNEB-565000000          0.7900          0.8800      0.01          0.00             0.01 2026-08-04T18:47:36.451419Z

kalshi_KXABNB_open_20260917T031845Z.json
                   ticker yes_bid_dollars yes_ask_dollars volume_fp volume_24h_fp open_interest_fp                updated_time
KXABNB-26NOVNEB-150000000          0.3200          0.3600    590.96          0.00           413.21 2026-08-04T18:47:36.451419Z
KXABNB-26NOVNEB-148000000          0.5000          0.5500    428.14          0.00           423.14 2026-08-04T18:47:36.451419Z
KXABNB-26NOVNEB-146000000          0.6300          0.6600    998.66          0.00           689.51 2026-08-04T18:47:36.451419Z
KXABNB-26NOVNEB-144000000          0.7600          0.8300    347.64          0.00            36.06 2026-08-04T18:47:36.451419Z
KXABNB-26NOVNEB-142000000          0.8400          0.9200     49.86          0.00            38.35 2026-08-04T18:47:36.451419Z
KXABNB-26NOVNEB-140000000          0.8900          0.9600    409.93          0.00           272.19 2026-08-04T18:47:36.451419Z
KXABNB-26NOVNEB-138000000          0.9400          0.9700    412.02          0.00           306.00 2026-08-04T18:47:36.451419Z
```

Revision-2 model runs (same session): `f01_model_v2.py` → adopted object mean 8.7046 / P(≥134.0m) 0.2897 / P(≤131.0m) 0.2720; P(Yes) 0.2867. `f02_model_v2.py` → final mixture median 10.53, P(<10) 0.445, P(<9.4) 0.359, P(≥12) 0.340, mass <0 0.001 / >20 0.003. `f03_f04_joint_v2.py` → FY26 print mean 35.82, P(<35.5) 0.1766; F03 0.0127/0.0405/0.1008/0.3565/0.4895; F04 0.5805 with conditionals 0.398/0.463/0.564/0.673/0.531 (Σ 0.5805); B12 literal 0.5086 / material 0.3748; Street anchor point share 21.04%, P 0.3286 (dispersion-only 0.1897).

## Final table

| question | revision 1 | Astra | revision 2 | anchor | \|final − anchor\| |
|---|---|---|---|---|---|
| F01 P(1Q27 nights descriptor ≥ +8.2%) | 0.22 (0.12–0.35) | 0.26 (0.12–0.45) | **0.28 (0.16–0.42)** | 0.43 (MODL 4Q26 bar through the tree; NOT_INDEPENDENTLY_DERIVED) | 0.15 |
| F02 1Q27 revenue-guide growth, median (p5–p95) | +9.4% (3.6–15.6); P(<10) 0.56, P(<9.4) 0.48, P(≥12) 0.25 | +10.3% (3.7–16.9); 0.47 / 0.41 / 0.34 | **+10.5% (5.1–16.1); P(<10) 0.45, P(<9.4) 0.36, P(≥12) 0.34** | +12.4% raw (LSEG 1Q27, obs 13 Aug, dated); +11.0% full-transmission | 1.9pt raw / 0.5pt adjusted |
| F03 FY27 margin guide (a/b/c/d/e) | 0.08 / 0.17 / 0.27 / 0.38 / 0.10 | 0.03 / 0.05 / 0.10 / 0.32 / 0.50 | **0.02 / 0.04 / 0.10 / 0.36 / 0.48** | (d) 0.55 / (e) 0.33 (WS05/H12 prior, literal mapping) | 0.19 on (d); 0.15 on (e) |
| F04 P(FY27 S&M ex-SBC ≥ 21.9%) | 0.55 (0.40–0.68); cond. 0.25/0.40/0.52/0.70/0.55 | 0.55 (0.35–0.75); cond. 0.25/0.35/0.50/0.70/0.50 | **0.55 (0.40–0.68); cond. 0.37/0.43/0.53/0.64/0.50 (Σ 0.548)** | 0.33 (Street residual 21.04%, uncertainty model) | 0.22 |
