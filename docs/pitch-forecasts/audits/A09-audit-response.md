# Response to audit A09 (R01 risk-q3-nights-meets-guide, R02 risk-q3-nights-accelerates, R03 risk-july-rnpl-expansion-offsets-lap)

Response date: 2026-09-17
Responds to: `A09-research-audit.md` (Astra, gpt-6-astra, read-only)
Revised research: the three `research-log.md` files (revision 2) and `forecasts/2026-09-17-forecast.json` (revision 2) under `questions/risk-q3-nights-meets-guide/`, `questions/risk-q3-nights-accelerates/`, `questions/risk-july-rnpl-expansion-offsets-lap/`
Revised model: `questions/risk-q3-nights-meets-guide/datasets/a09_v2_print_distribution.py` (writes `a09_v2_*.csv` and `a09_v2_final.json` into all three folders; revision-1 `a09_nights_error_distribution.py` and its `a09_*.csv` left untouched as the audit trail)
Adopted print-state object for downstream questions: `questions/risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json`
Reproduction script: `A09-reproduce.py` (the audit's script, saved verbatim; ran clean from the repo root, exit 0, no path fix; full output in `A09-reproduce.stdout.txt`, excerpt at the end of this file)

## Summary

Twenty-one findings. Seventeen accepted, three accepted in part (A09-04, A09-05, A09-15), one rejected in part and accepted in part (A09-04's "not demonstrated" claim). Every number in the audit reproduced: the revision-1 artefacts (0.4236515 / 0.3159324 / 0.074105), the W2 error statistics (n 10, mean +0.528, sd 1.447, RMSE 1.471, 7 over-predictions), the three common under-prediction quarters, the guidance outcome counts (13 / 2 / 1 / 1), the sequential rates (7/16, 6/16; W1 6/14, 5/14; W2 5/10, 4/10), the Kalshi fixed-point fields, the reaction classes, the 3Q→4Q growth pairs, the held-cost corrections (FY27 EPS $0.119 / 0.196 / 0.295 on the rev-1 shocks), the C06-v2 share rebuild (0.3891 / 0.2481) and the k-sensitivity joints (0.0944 / 0.1029 / 0.1066 / 0.1127).

**Question fidelity (A09-01), decided as reading (a).** The fine print names the object ("derive from the team's nowcast distribution ... walk-forward error distribution of the index ... report the implied probability and its sensitivity to the index's error sd") and the brief's rule 6 makes the alt-data band the input the questions condition on. Revision 1's 0.60/0.30/0.10 blend put 40% of the headline outside that object. Revision 2's headline is the nowcast-derived number; the management-delivery construction, the sequential-change class and the Kalshi ladder are computed, labelled and reported as alternatives with zero weight (`a09_v2_alternatives.csv`) so the memo can print them beside the headline. The blend was not re-justified because the fine print does not allow it and the brief favours (a); if the team wants a blended number in the memo, that is a memo decision to be written down there.

Headline numbers, revision 1 → revision 2: **R01 0.42 (0.30–0.55) → 0.39 (0.30–0.47)**; **R02 0.32 (0.20–0.42) → 0.26 (0.18–0.34)**; **R03 0.07 (0.04–0.12) → 0.11 (0.07–0.15)**. One object generates all three and every impact row: latent 3Q26 nights growth ~ N(9.5, 1.70) on the fixed 133.6m base, with the printed figure rounded to 0.1m (event = latent ≥ 146.95m / 147.75m). Print states for X01: P(<147.0m) 0.614 / P(147.0–147.7m) 0.126 / P(≥147.8m) 0.260; on S01's dead band decelerating 0.636 / flat 0.104 / accelerating 0.261.

What moved the numbers: R01 and R02 fell because the outside-view and market legs (0.55–0.67 and 0.585 for R01) left the headline, partly offset by the centre moving from 9.55 to 9.5 (mandated input) and the rounding convention (+0.008). R03 rose because C06 revision 2 raised P(a) from 0.15 to 0.25; the conditional P(R01 | a) fell from 0.514 to 0.445 (R01 lower; k 0.143 → 0.10). Impact tables changed more than the probabilities: the held-cost identity raised the EPS and FY26 margin rows, and the stock line, rebuilt from S01 revision 2's cell means conditioned on each event against its complement with the re-rating line separated, fell from $18.8 / 22.8 / 22.2 to $8.7 / 9.8 / 6.2 per share, so the EVs are $3.4 / $2.5 / $0.7 (R03 now immaterial on its own).

## Finding-by-finding

### A09-01 (critical) — 40% of the weight from outside the specified object: accepted
Reproduced: 0.6 × 0.3321 + 0.3 × 0.5521 + 0.1 × 0.5874 = 0.42365; alt-only leg 0.3321 / 0.2179; remove-market-and-renormalise 0.4055 / 0.2911. Decision (a) as above. The revision-2 headline object is N(9.5, 1.70) at the rounding-consistent thresholds: **0.386 / 0.260**. The revision-1 alt-data leg (0.332 / 0.218) was itself a mean of the seven-row kernel mixture at the rows' raw centres (mean 9.16) and a normal at 9.55; neither was the mandated centre. Every alternative (sequential class 0.44 / 0.375, management delivery 0.67 / 0.50 as an assumption, Kalshi 0.585 / 0.537, the revision-1 blend, Astra's benchmark) is in `a09_v2_alternatives.csv` with `weight_in_headline = 0`.

### A09-02 (critical) — convention 2 changed the event on restatement: accepted
Convention 2 withdrawn. The denominator is 133.6m whatever the letter shows; a restated 3Q25 base does not change the event; P(restatement) < 1% is discussed in §6 of the R01 log, not absorbed by a convention.

### A09-03 (major) — R03 stale against C06 revision 2: accepted
Reproduced C06 v2's share draws (true ≥25 0.389; disclosed-(a) 0.248) and the k-sensitivity joints. Revision 2 rebuilds the joint on C06 v2's exact structure (`c06_v2_share()` in the v2 script mirrors `share_ramp_model_v2_2026-09-17.py`: 1Q26 U(19,21), step U(0.5,3.5) with 2Q26 in [20.5,23.5], ramp U(0,0.5)×step, expansion 0.75·Exp(1.4)+0.25·Exp(3.5) cap 8, mix U(−1,1); level gate 0.75/0.68/0.55; language (a) 0.85) and R01 rev 2's nights object. The U(−2,0) penalty and the (a) = 0.15 cap are gone. Joint **0.111**; the "old conditional × new C06" 0.129 is rejected because the 0.514 was computed on withdrawn inputs (R03 log §4).

### A09-04 (major) — Kalshi fields and staleness: accepted in part, rejected in part
Accepted: revision 1 read a non-existent `volume` key; the real fields are `volume_fp` 998.66 / 428.14 / 590.96, `open_interest_fp` 689.51 / 423.14 / 413.21, `volume_24h_fp` 0, `updated_time` 2026-08-04 on all seven markets (a batch stamp); Octagon's 60/53/30 are last-trade prices (the API's `last_price_dollars` 0.60/0.53/0.30), and the mids are 0.645/0.525/0.34, not "within two points" at 150m. The ladder's weight goes to zero (fine print; stale-source rule) and it is recorded as the adjacent comparison, with mid- and last-trade interpolations both given (0.585 / 0.565 at 147.0m; 0.537 / 0.537 at 147.8m).
Rejected: "'unchanged since July 29' is not demonstrated." The cumulative `volume_fp` at 146/148/150m (998.66 / 428.14 / 590.96) equals the Octagon 29 July snapshot's volumes (999 / 428 / 591) to the rounding, so **no contract has traded on those strikes since 29 July**; the last-trade prices are the 29 July prices by construction. What changed since 29 July is the quote (mids +4.5 / −0.5 / +4 points), with no trade behind it. Revision 1's sentence was right about trades and wrong about quotes; the log now says both.

### A09-05 (major) — W2-only construction; "revintaged" scaling: accepted in part
Accepted: the probability used only W2 errors; the ×1.107 / ×1.231 scaling of every row's errors was not a refit and is now labelled a uniform-scaling stress test; both windows are reported (R01 claim 3, claim 18, §6; `a09_v2_windows.csv`). Reproduced Astra's W1 scaled-kernel mixture (0.1766 / 0.1235, six rows) and W2 (0.2684 / 0.1672).
In part: the W1 numbers are not a second estimate of the same object. W1's headline errors carry a +1.64pp mean (11 of 14 over-predictions) that sits in the 2023 normalisation quarters (2Q23 +5.6, 1Q23 +3.0); applied to any centre they say "actual ≈ centre − 1.6", which is the 2023 base effect the E note tells readers to ignore for prior-year ratios. Demeaned W1 errors at centre 9.5 give 0.34–0.36 / 0.21–0.26 (sd 1.83), inside the revision-2 intervals; undemeaned they give 0.15 / 0.09 and are reported as such. The adopted sd 1.70 is the midpoint of the fresh-vintage W2 RMSE range (1.634–1.816), which is the object the brief quotes; W1's demeaned sd (1.83–1.98) is the top of the §6 grid.

### A09-06 (major) — "only two quarters where every row under-predicted": accepted
Reproduced: the seven-row W2 panel is negative in all columns in 4Q24, 3Q25 and 2Q26 (3Q25 range −0.06 to −0.98, headline −0.25). Claim 3 corrected to 3/10; the R02 headline-tail count (2/10 at the threshold, restated on the demeaned errors at centre 9.5 as 2 of 10 clearing −1.09) stands. The product-acceleration reading is now stated as an interpretation with 3Q25 named (the US RNPL launch quarter, a small miss).

### A09-07 (major) — management record heterogeneous; cushion not a base rate: accepted
Reproduced: outcomes 13 met / 2 above_range / 1 not_met / 1 pending; 15/16 met or exceeded; the 1Q25 comparator is 1Q24 ex-Leap Day (8.5), not the prior quarter; 1Q23 was "nearly as strong". Claim 10 recoded in both logs; "a 16-print record of guides met" withdrawn; the N(0.6, 0.5) cushion and 1.3 error sd are relabelled assumptions with no comparable sample (no numeric floor has ever been set at the printed rate) and the whole construction is moved to the zero-weight alternatives table. The sequential rates reproduce (7/16, 6/16; W1 6/14, 5/14; W2 5/10, 4/10) and are reported as the outside view.

### A09-08 (major) — R03 base rate internally inconsistent: accepted
Reproduced: 0.16 × 0.55 × (0.51/0.42) = 0.1069; × 0.7 = 0.0616. The base-rate estimate is withdrawn; the R03 log states NOT_INDEPENDENTLY_DERIVED (the independence product 0.096 is the floor and shares every input) and NO_EXTERNAL_ANCHOR; no third estimate is invented.

### A09-09 (major) — "adoption saturated": accepted
D005 (people offered the product, US) and D022 (global GBV-weighted adoption among eligible bookings) have different denominators; D022's note warns against chaining them. Claim 5 relabelled: saturation is an assumption used only to motivate the common-cause structure; adoption and booking-mix paths within existing eligibility are allowed (and are inside C06 v2's ramp and mix terms).

### A09-10 (major) — "every outside series decelerates": accepted
G §1 reports NTTO improving (−14.1 → −7.0), Expedia July consistent with Q2, STR +1.7 then +16.1 with the Labor Day artefact named. Claim 6 rewritten as mixed evidence in both logs; the sentence removed from R01 §5. The query log was neutral (Astra agrees); this was an interpretation error.

### A09-11 (major) — two distributions for one event; R03 copied R01's conditional mean: accepted
Reproduced: N(9.6726, 1.70) gives P(≥10.6) 0.2927 against the blended 0.3159. Revision 2 has one object: N(9.5, 1.70) generates R01, R02, the print states, R03's nights marginal (the joint draw's `p_r01` 0.385 matches the analytic 0.386 to MC error) and every impact row; R03's conditional mean (11.25) is read from the joint draw conditional on both legs, not copied from R01 (11.18).

### A09-12 (major) — S01 cells mis-selected; 10.00–10.09 sliver omitted; old state weights retained: accepted
Reproduced: the four chosen cells summed to 0.37 with mean +1.30%; the sliver has 2.29% mass under N(9.55, 1.48) (2.17% under the adopted object). The stock line is rebuilt from S01 revision 2's twelve cells (`s01_v2_cells.csv`): state means accel +2.02 / flat −0.89 / decel −4.30, re-weighted to the adopted distribution and conditioned on each event exactly (R01-Yes = accel 0.70 + flat 0.24 + sliver 0.06 with the sliver at the decelerating mean; R01-No = decelerating only; R03 conditioned on both legs from the joint draw's within-event mix). Revision 1's −8.6 / −2.9 were S01 revision-1 medians and are withdrawn.

### A09-13 (major) — EV mixed conditional means with medians and added an overlapping re-rating line: accepted
The stock line is now one horizon (the 5 Nov reaction session), one statistic (means, not medians), one comparison (the event against its complement, so P × impact is the event's contribution to the unconditional expected move; the base-case-cell and unconditional comparisons are shown beside it). The fundamental re-rating line (FY27 growth × 0.44 turns × $9.5) is reported as a separate horizon and **not added**. Materiality is re-evaluated on that basis: R01 $3.4 and R02 $2.5 material; R03 $0.7 immaterial on its own ($1.0 against the base-case cell is the margin).

### A09-14 (major) — 0.66 is a margin sensitivity, not a flow-through; FY26 margin approximated: accepted
Reproduced Astra's held-cost corrections on the rev-1 shocks (FY27 EPS $0.119 / 0.196 / 0.295; FY26 margins 0.514 / 0.669 / 0.567). Revision 2 computes margins as annual ratios from `23_forecast_annual.csv` (FY26 $14,268M / $5,098M; FY27 $15,829M / $5,483M) under held costs (incremental revenue = incremental EBITDA) and reports the brief's "flex" alternative beside it as a 0.77 flow-through (the flow-through implied by the brief's 0.42/0.66 and 0.38/0.59 pairs); FY27 EPS = $M × $0.0014 under held costs. R01: FY26 +0.64pp (flex +0.41), FY27 +0.44pp (+0.28), EPS +$0.15 (+$0.11).

### A09-15 (major) — "2 of 2 bucket-era cases" false: accepted in part
Reproduced: 3Q22 25.09 → 4Q22 20.16; 3Q23 13.54 → 4Q23 12.02; 3Q25 8.79 → 4Q25 9.82 — 1 of 3 since 2022 was followed by a Q4 at or above the Q3 rate. The sentence is deleted. In part: those pairs compare growth levels, while the impact rows carry the persistence of the *surprise versus the base case* into 4Q26, which the level pairs do not estimate either way; the 0.6 / 0.4 factors stay as labelled judgements (harmonised across the three questions) with a sensitivity file (`a09_v2_impact_persistence_sensitivity.csv`: 0.3/0.2, 0.9/0.6, 1.0/1.0).

### A09-16 (major) — "the lap thesis is wrong, not just early": accepted
The card says "weakens"; resolution is a joint observation and R03 keeps a non-RNPL nights path. Convention 5 added to the R03 log; §9 rewritten; the FY27 +0.8pt of revision 1 is replaced by the module's identified scenario difference (+0.47pt) as a labelled line excluded from the deltas and the EV.

### A09-17 (major) — ADR +0.3 not propagated: accepted
Withdrawn rather than propagated: the larger-home mix effect (D016, D033) is a direction with no measured magnitude, and the brief's ADR sensitivity would have carried $13.8M of Q3 revenue on a judgement. Driver and financial rows are now consistent (ADR 0.0 in all three tables).

### A09-18 (minor) — rounding convention unspecified: accepted
Convention stated in all three logs: the latent quantity is continuous, the print rounds to 0.1m, "printed ≥ X.Ym" = latent ≥ X.Ym − 0.05m; thresholds 9.9925% / 10.5913%. The printed-exact alternative (10.0299 / 10.6287; Astra's) is reported: 0.378 / 0.253, i.e. 0.008 / 0.007 lower.

### A09-19 (minor) — EV from hidden unrounded inputs: accepted
Every EV is now computed from the published rounded P and the published rounded stock impact (0.39 × 8.7 = 3.4; 0.26 × 9.8 = 2.5; 0.11 × 6.2 = 0.7) and the JSON says so.

### A09-20 (minor) — "September is 40% of the quarter": accepted
30 / 92 = 32.6%; the observation cut-off (reviews to 17 Aug; roughly 45–48% of the quarter's days unobserved; E note "60–65% complete") is stated separately.

### A09-21 (minor) — conflicting §7 / §8 update rules: accepted
One update rule in each log: re-centre the same normal and read P = 1 − Φ((threshold − c) / 1.70); tables at c = 8.5 … 10.6 in `a09_v2_final.json` (`monitoring_rule`). The external-series rows (CPI, NTTO, Hilton, EXPE) are demoted to context: the object moves only through the index centre, so they no longer carry ±0.02/0.03 instructions of their own.

## What the audit missed

1. **The centre 9.55 had no source.** Revision 1 used N(9.55, ·) "the C02/S01 convention"; the brief's mandated input is 9.5 (memo: 146.3m), the bias-corrected headline row is 9.52, and the seven bias-corrected rows average 9.42. Astra used 9.5 without noting that revision 1 had not. Effect +0.01 on R01.
2. **The memo's base case is 9.5, not 9.9.** Revision 1's deltas were "vs team 9.9" (the model path, the top of the band); the memo's own 3Q26 read is +9.5% (146.3m), and 9.9 is labelled there as the pre-alt-data path. Deltas are now versus 9.5, which is also the object's mean, so E[nights | event] − 9.5 is the correct conditional shift. This raises every nights delta by 0.4pt and is the main reason the revenue and EPS rows rose despite the lower probabilities.
3. **The empirical error shape is right-skewed in the actual and lowers P(≥10) by 0.08 against the normal.** Astra's benchmark is the parametric normal; the log's own ten demeaned W2 errors at the same centre give 0.30 / 0.20 (five errors of +1.3 to +1.6, one of −3.2). At n = 10 that shape is not a measured feature, so the normal is adopted, but it is the reason the intervals reach 0.30 / 0.18 rather than being symmetric around the point.
4. **The seven-row kernel mixture "at raw centres" is the bias-corrected mixture.** Subtracting a row's own raw errors from its implied level centres the draws at implied − mean(error); revision 1 reported this as a construction distinct from the bias-corrected one. It is the same object (0.257 / 0.156), and it is not the mandated centre either (mean 9.43).
5. **The Kalshi volume identity.** Astra reported the fixed-point volumes but not that they equal the 29 July snapshot's, which is the evidence that settles the staleness question (A09-04 above).
6. **The S01 within-band centre.** S01 revision 2 draws nights within each state from revision 1's N(9.67, 1.70); moving to N(9.5, 1.70) changes the within-state mix (P(accel | ≥10.0) 0.75 → 0.68) as well as the state weights, so S01's re-basing is two parameters, not one; its own "rev-1 N(9.55, 1.48)" sensitivity row (states 0.642 / 0.116 / 0.241) is the nearest already-computed neighbour of the adopted states and shows the direction (median about −0.3, base-case cell +0.02, breaker cell −0.02).
7. **R03's disclosure lift changes C06's marginal unless centred.** Adding +0.10 / +0.05 to the gate on strong prints raises P(a) above C06's 0.25; revision 2 subtracts the lift's expectation so C06's published marginal is preserved (P(a) 0.249 in the joint) and the dependence shows up only in P(R01 | a).

## Reconciliation with Astra's numbers

| question | Astra | revision 2 | difference | cause |
|---|---|---|---|---|
| R01 | 0.38 (0.378 at 10.0299%) | 0.39 (0.386 at 9.9925%) | +0.008 | rounding convention only; same centre, same sd |
| R02 | 0.25 (0.253 at 10.6287%) | 0.26 (0.260 at 10.5913%) | +0.007 | same |
| R03 | 0.11 (0.107 at k 0.143, no disclosure lift) | 0.11 (0.111 at k 0.10 with the centred disclosure lift) | +0.004 | the disclosure dependence (+0.008) less the smaller k (−0.004) |

No divergence exceeds one point, so no asymmetry needs naming. The one place this response declines Astra's suggested treatment is A09-05's implication that W1 offers a comparable second estimate: W1's undemeaned errors are dominated by the 2023 normalisation bias and are reported as a stress, not as a competing probability.

## Re-basing verdict for S01 / S02 / C02 / C04 (and X01)

| question | re-base? | why |
|---|---|---|
| S01 (day1-move-5nov, rev 2) | **Yes** | adopted print states 0.595/0.085/0.32 → 0.636/0.104/0.261 and within-band N(9.67, 1.70) → N(9.5, 1.70); the cell probabilities X01 conditions on move 2–3 points (base-case cell ≈ 0.36 → 0.38, breaker ≈ 0.11 → 0.09); a two-parameter re-run of `s01_joint_v2.py` |
| S02 (close-15dec-2026, rev 2) | **Yes, for coherence; immaterial** | branch weights accel 0.32 → 0.26, flat 0.10 → 0.13; its own sensitivity row (P(accel) 0.22) shows the decomposition median moving about −$1 and P(≤150) +0.01, inside its noise floor |
| C02 (q4-nights-bucket, rev 2) | **No** | P(≥10.0) 0.423 → 0.386 moves (a) by about −0.01 and (d) by +0.01, below its 2–3 point noise floor; record the input change at X01 time |
| C04 (fy26-margin-sentence, rev 2) | **No** | R01 is recorded there as an input the log calls immaterial to its 3Q26 revenue draw ($8M on an $80M sd) |
| X01 | reads `adopted_print_states_v2.json` | must not use the rev-1 0.42 / 0.32 or N(9.67, 1.70) |

## Reproduction output

`py -3.13 -B docs/pitch-forecasts/audits/A09-reproduce.py` from the repo root, 2026-09-17, exit 0 (no edits to the script). Full output in `A09-reproduce.stdout.txt` (92 lines); the lines that carry the findings:

```
Guidance outcomes: {'met': 13, 'above_range': 2, 'not_met': 1, 'pending': 1}
Resolved guides meeting/exceeding coded guidance: 15 / 16
All 3Q22-2Q26 n = 16 [(-0.34, 7, 0.4375), (0.26, 6, 0.375)]
W1 target 1Q23+ n = 14 [(-0.34, 6, 0.428571), (0.26, 5, 0.357143)]
W2 target 1Q24+ n = 10 [(-0.34, 5, 0.5), (0.26, 4, 0.4)]
Q2-to-Q3 n = 4 [(-0.34, 4, 1.0), (0.26, 3, 0.75)]
Stable/approximate comparators: 3Q22 24.6 -> 25.09 (+0.49); 1Q23 20.2 -> 18.61 (-1.59); 2Q24 9.5 -> 8.69 (-0.81); 1Q25 8.5 (1Q24 ex Leap Day) -> 7.92 (-0.58); 3Q25 7.4 -> 8.79 (+1.39)
Revintage inputs: v1 rmse 1.475147 ratio 0.683209 | a: 1.815866 / 0.841012 | b: 1.633596 / 0.756595 | c: 1.538458 / 0.712532
ERROR WINDOW 2023Q1+
GLOBAL|yoy_all|w_reviews n 10 bias 0.528315 sample_sd 1.446836 rmse 1.470755 overpredictions 7 plugin [0.3, 0.2, 0.2] scaled_kernel [0.302661, 0.201810, 0.197510]
(six further rows) ... Equal-model kernel mixture: [0.268391, 0.167173, 0.163797] models 7
All models underpredicted: ['2024Q4', '2025Q3', '2026Q2']
Minimum pairwise error correlation: 0.799072
ERROR WINDOW 2022Q1+
GLOBAL|yoy_all|w_reviews n 14 bias 1.637423 sample_sd 1.831818 rmse 2.407702 overpredictions 11 plugin [0.214286, 0.142857, 0.142857] scaled_kernel [0.202431, 0.146498, 0.143715]
  MISSING: GLOBAL|yoy_all|w_median
(five further rows) ... Equal-model kernel mixture: [0.176605, 0.123499, 0.121258] models 6
Analytic alt-only blend at original thresholds: [0.332004, 0.217788]
Kalshi 150.0 mid 0.34 last 0.3000 volume 590.96 OI 413.21 24h 0.00 updated 2026-08-04T18:47:36.451419Z
Kalshi 148.0 mid 0.525 last 0.5300 volume 428.14 OI 423.14 24h 0.00 updated 2026-08-04T18:47:36.451419Z
Kalshi 146.0 mid 0.645 last 0.6000 volume 998.66 OI 689.51 24h 0.00 updated 2026-08-04T18:47:36.451419Z
(144m 0.795 / 0.83 / 347.64; 142m 0.88 / 0.84 / 49.86; 140m 0.925 / 0.90 / 409.93; 138m 0.955 / 0.88 / 412.02)
Market interpolation, printed thresholds: 0.585 0.537
Market interpolation, original script: 0.5874 0.539304
Original blend r01 0.4236515384106209 saved 0.4236515384106209 remove market and renormalize 0.40545726490068995
Original blend r02 0.31593242397572463 saved 0.31593242397572463 remove market and renormalize 0.29111335997302745
Impact normal P(R02): 0.29270421759956716
Current C06 revision/vector: 2 {'a_ge_25pct': 0.25, 'b_21_to_24pct': 0.2, 'c_over_20_repeated_or_le_20': 0.26, 'd_not_disclosed': 0.29}
Current C06 times old conditional: 0.12851840932345954
R03 base-rate formula with stated lift: 0.10685714285714287 with unexplained .7: 0.0616
Disclosure continuation (v2 matrix) 4Q20 93/113 0.823 | 1Q23 60/78 0.769 | 1Q24 40/56 0.714
Reaction W1 -1.0 n 8 mean -5.588948 positive 0 | 0.0 n 1 mean -8.775318 | 1.0 n 5 mean 6.037883 positive 4
Reaction W2 -1.0 n 5 mean -5.967519 positive 0 | 0.0 n 1 mean -8.775318 | 1.0 n 4 mean 8.831939 positive 4
Accelerating Street bars: 4Q21 3.7, 3Q23 -5.1, 4Q24 14.0 mean 4.2
Accelerating Q3 to Q4: 22 25.09 20.16 | 23 13.54 12.02 | 25 8.79 9.82
Impact R01 held-cost margin changes {'FY26': 0.513896, 'FY27': 0.349100} held-cost EPS27 0.119 EV from displayed p/stock 7.896
Impact R02 held-cost margin changes {'FY26': 0.668672, 'FY27': 0.573008} held-cost EPS27 0.196 EV from displayed p/stock 7.296
Impact R03 held-cost margin changes {'FY26': 0.567047, 'FY27': 0.859782} held-cost EPS27 0.2954 EV from displayed p/stock 1.554
S01 mean of chosen cells: 1.302703
S01 omitted 10.00-10.09 mass: 0.022937
Auditor normal probabilities: 0.377623 0.253356
Auditor sd sensitivity: 1.0 0.298077 0.129503 | 1.48 0.360146 0.222832 | 1.633596 0.372817 0.244797 | 1.7 0.377623 0.253356 | 1.815866 0.385205 0.267102 | 2.159143 0.403058 0.300566 | 2.5 0.416063 0.325816
C06-v2 true high share / disclosed-a: 0.3891 0.24805125
Auditor joint sensitivity k 0 nights marginal 0.377623 P(R01|a) 0.377623 joint at current C06 0.094406
Auditor joint sensitivity k 0.1 nights marginal 0.377486 P(R01|a) 0.411765 joint at current C06 0.102941
Auditor joint sensitivity k 0.142857 nights marginal 0.377216 P(R01|a) 0.426520 joint at current C06 0.106630
Auditor joint sensitivity k 0.214286 nights marginal 0.376208 P(R01|a) 0.450878 joint at current C06 0.112719
```

Revision-2 model: `py -3.13 -B docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/datasets/a09_v2_print_distribution.py`, exit 0; `a09_v2_final.json`: final r01 0.386017, r02 0.260452, r03 0.110768; conditional means 11.185 / 11.619 / 11.246; print states 0.614 / 0.126 / 0.260 (S01 cut: 0.636 / 0.104 / 0.261); R03 joint p_a 0.2488, p_r01 0.3851, p_r01_given_a 0.4451, product 0.0958.

## Final table

| question | revision-1 | Astra | revision-2 | anchor | \|final − anchor\| | EV $/share | material |
|---|---|---|---|---|---|---|---|
| R01: P(3Q26 nights printed ≥ 147.0m, +10.0%) | 0.42 (0.30–0.55) | 0.38 (0.27–0.50) | **0.39 (0.30–0.47)** | 0.585 (Kalshi mids, untraded since 29 Jul; zero weight) | 0.20 (vs Astra 0.01) | 0.39 × $8.7 = **$3.4** (vs the R01-No world; $3.6 vs the base-case cell) | yes |
| R02: P(3Q26 nights printed ≥ 147.8m, +10.6%) | 0.32 (0.20–0.42) | 0.25 (0.14–0.38) | **0.26 (0.18–0.34)** | 0.537 (Kalshi mids; zero weight) | 0.28 (vs Astra 0.01) | 0.26 × $9.8 = **$2.5** (subset of R01; do not add) | yes |
| R03: P(C06 = (a) and R01 = Yes) | 0.07 (0.04–0.12) | 0.11 (0.06–0.18) | **0.11 (0.07–0.15)** | none (NO_EXTERNAL_ANCHOR) | n/a (vs Astra 0.00) | 0.11 × $6.2 = **$0.7** ($1.0 vs the base-case cell; subset of R01) | **no** (one sentence inside R01) |

Adopted print-state distribution for X01 (`adopted_print_states_v2.json`): N(9.5, 1.70) on latent growth; P(<10.0) 0.614 / P(10.0–10.6) 0.126 / P(≥10.6) 0.260; S01 states 0.636 / 0.104 / 0.261; sd sensitivity R01 0.31–0.42 over sd 1.0–2.5 (0.37 / 0.38 / 0.39 / 0.39 / 0.41 at 1.475 / 1.634 / 1.70 / 1.816 / 2.159), R02 0.14–0.33; centre sensitivity R01 0.32 (9.2) / 0.48 (9.9) / 0.50 (10.0). S01 and S02 to be re-based; C02 and C04 not.
