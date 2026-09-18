# Response to audit A04 (C05 bundle-attribution-quantified, C06 rnpl-gbv-share-disclosed, C07 rnpl-negative-effect-acknowledged)

Response date: 2026-09-17
Responds to: `A04-research-audit.md` (Astra, gpt-6-astra, read-only)
Revised research: the three `research-log.md` files (revision 2) under `questions/bundle-attribution-quantified/`, `questions/rnpl-gbv-share-disclosed/`, `questions/rnpl-negative-effect-acknowledged/`
Revised forecasts: each folder's `forecasts/2026-09-17-forecast.json` (revision 2; all three numbers moved)
New datasets (revision-1 files left untouched as the audit trail): `metric_persistence_matrix_v2_recode.py` and its outputs (`metric_persistence_matrix_v2_4Q20-2Q26.csv`, `persistence_rates_v2.csv`, `metric_gap_events_v2.csv`, `persistence_by_metric_v2.csv`), `bundle_3q26_mechanical_contribution_v2.csv`, `c05_state_decomposition_v2.csv`, `share_ramp_model_v2_2026-09-17.py/.csv`, `c07_classification_table_v2.csv`, `c07_scenario_partition_v2.csv`, `kalshi_q3_nights_implied_v2_2026-09-17.csv` (in all three folders); builder `audits/A04-response-datasets.py`
Reproduction script: `A04-reproduce.py` (the audit's script, saved verbatim from the audit file; output at the end of this response)

## Summary

Eighteen findings. Fourteen accepted, four accepted in part (A04-04, A04-06, A04-09, A04-13), none rejected. Every number in the audit reproduced: the script ran clean on `py -3.13 -B` from the repo root with no path fix, and the four independent checks I ran beyond it (the 1Q25/3Q25/2Q26 transcript cells, the Guest Favorites letter series, the driver-history GBV means, the balance-sheet solve rows) all came out as the audit said. The audit missed two things that cut in opposite directions: the Guest Favorites row was worse than it reported (four more blank cells that the letters fill, which raises the continuation rate slightly), and the run's own R01/R02 forecasts, which landed after revision 1, supply the print-state weights the audit asked for, so the headline no longer rests on the undocumented team/Kalshi blend or on the team normal alone.

Headline numbers, revision 1 → revision 2:
- **C05** (0.08, 0.12, 0.07, 0.73) → **(0.07, 0.11, 0.10, 0.72)**; P(any quantification) 0.27 → 0.28. Small move; the composition changed more than the total: (c) now carries the quantified-lap route that C07 also counts, and the RNPL-alone branch of the repaired bridge.
- **C06** (0.15, 0.24, 0.31, 0.30) → **(0.25, 0.20, 0.26, 0.29)**. The largest move in the batch, all of it from A04-07: the directional Q3 "lead-time" penalty had no evidence and was doing the work of holding (a) down. The v2 share model, with every input labelled an assumption and the ramp tied to the one observed increment, puts the true share at ≥24.5 with probability 0.39, against the audit's 0.40 benchmark.
- **C07** 0.20 (0.12–0.32) → **0.27 (0.15–0.40)**. The contract was read too narrowly in revision 1: a quantified lap effect and an explicit decline in the net benefit both resolve Yes and need no cancellation surprise. The decomposition is now a mutually exclusive partition (adverse / ordinary-decelerating / routine) on the R01/R02 print states.
- **R03 implied recompute**: R03's log records joint ≈ 0.51 × P(C06 = a); with (a) at 0.25 that is **≈ 0.13 (from 0.07)** if R03's own model is left unchanged. That recompute belongs to batch A09 and is flagged in C06 §6 and its JSON.

## Finding-by-finding

### A04-01 (critical, C07) — quantified lap and net-benefit decline are Yes under the registry: accepted
Re-read the registry against the rev-1 conventions. The resolution clause "a quantified negative effect (points, dollars, or 'meaningful'/'notable' drag) on any reported metric" covers "the RNPL comparison reduced Q3 nights growth by about 2 points", and "a statement that the net benefit has declined or turned" does not require the benefit to be negative. Revision 1 priced the first as 0.02 of resolver risk and had no route at all for the second. C05's convention 2 already treated the same sentence as a 3Q26 quantification, so the two logs disagreed on one object.
Fix: a literal classification table (`c07_classification_table_v2.csv`, ten statement types with the resolving clause and an example each). Qualitative "tougher comps" sentences stay No; repeated direction-only timing sentences (D037/D051/D049/D050) stay No and are not promoted; a quantified lap on a listed 3Q26/4Q26 metric is Yes; "the lift is smaller now that we have lapped" is Yes. The decomposition was rebuilt (see A04-12) and the number reforecast: 0.27. The reading of convention 3 is the largest resolver risk and is priced both ways in §7 (0.22 if the resolver demands a decline in level; 0.19 if a quantified lap is read as a prior-year comp).

### A04-02 (major, C05/C06) — matrix confuses mentions with numeric disclosure: accepted
Reproduced by re-reading the mirrors: the 1Q25 "cancellation rates" hit is Richard Clarke's question ("Is it higher cancellation rates, shorter trips..."), the 3Q25 hit is Clarke again ("Any early signs of what cancellation rates might look like") with a management answer that carries no rate (D006), and the 2Q26 Middle East passage is "less than we had anticipated" with no points. All three were coded as disclosures. On Guest Favorites the audit was right and understated it: the letters state cumulative nights booked at Guest Favorite listings in 1Q24 (>100m), 2Q24 (>150m), 3Q24 (>200m), 1Q25 (>350m), 2Q25 (>400m), 3Q25 (~500m) and 4Q25 (>500m); revision 1 coded 1Q24, 1Q25, 2Q25 and 3Q25 blank and 4Q25 call-only.
Fix (`metric_persistence_matrix_v2_recode.py`): the three false-positive cells removed and the five Guest Favorites cells added; every other cell is explicitly uncertified. Result: continuation All 93/113 = 0.823 (rev 1 0.820; audit's three-cell repair 0.807), W1 60/78 = 0.769, W2 40/56 = 0.714; gap returns All 4/18 = 0.222, W1 4/16 = 0.250, W2 4/15 = 0.267. The audit's 88/109 and 4/19 reproduce exactly when only its three cells are removed; the Guest Favorites completion adds one continuation and one gap event. A full recode with metric/denominator/period/venue fields is not done; the v2 file is labelled a partial repair.

### A04-03 (major, C05/C06) — no window robustness, 16 not 17 metrics, post-hoc group: accepted
Reproduced: the matrix has 16 rows (the logs said 17); All/W1/W2 are 0.820/0.763/0.704 on rev 1 and 5/19, 5/17, 5/16 on the gap ledger. Both windows are now published in every claim that uses the matrix, per-metric counts are in `persistence_by_metric_v2.csv` (four series carry 58 of the 113 eligible transitions), the logs say plainly that metric-quarters are not independent management decisions, and the five "stopped flattering" series are labelled a retrospective grouping reported as descriptive only (0/5 vs 4/13 on the recode). C06's decomposition gate of 0.70 now sits inside the W1–W2 continuation range (0.71–0.77) rather than being a cut from a single pooled 0.82.

### A04-04 (major, C05/C07) — historical denominators are not trials of the current question: accepted in part
Reproduced: bundle points in 2/4 post-launch prints, continuation 1/2, completed return-after-gap trials n = 0; C07 author labels 0/4 strict, 3/4 generous, Laplace 1/6; the GBV-share history is 1/1. Accepted that C05's 2/23 includes pre-RNPL quarters and that C07's 0/4 applies a baseline set at the last of those prints. Both base rates are now labelled descriptive analogues and discounted (C05's base rate uses the recoded gap-return rate 0.22–0.27 rather than 2/23; C07's literal-table count is stated as 0–1 of 4 and discounted to 0.22).
In part: the analogues are kept as the base-rate estimate because the skill requires one and nothing closer exists; the logs say what they are.

### A04-05 (major, C05) — bridge combined incompatible endpoints: accepted
Reproduced from D note §2.5: the 40% and 50% splits of the 1.75-point ex-NA bundle give fee/cancellation 0.70 or 0.88 and RNPL 1.05 or 0.87, summing to 1.75 at either endpoint. Revision 1 added 0.70+0.87 and 0.88+1.05. Repaired (`bundle_3q26_mechanical_contribution_v2.csv`): gross 2.81–3.06, net 1.88–2.91 after the same drag slice (audit's numbers), central 2.4–2.6.

### A04-06 (major, C05) — total-bundle bridge used for RNPL-alone; fitted baseline; "could truthfully state": accepted in part
Reproduced: `D1_bundle_crosscheck.csv` labels the 1Q26 row "fitted, so agreement is by construction"; D033 describes the lift as net of cancellation. Accepted: the v2 bridge has separate `bundle` and `rnpl_only` branches (RNPL-alone 1.27–1.70 gross, 0.34–1.55 net, i.e. (c) or low (b)); the drag is labelled a scenario slice that may partly sit inside the fitted net baseline, so the subtraction is an upper bound on the drag; "could truthfully state" is replaced by "scenario-implied under these assumptions"; a new convention 4 in C05 records that only a three-feature bundle figure reaches (a).
In part: I did not attempt to separate which part of the y/y-differenced drag is incremental to PR #32's fit, because the fit is on four WS10 estimates with no error bound (D note §4); the sensitivity row "drag fully additional" shows what the literal reading costs (0.02 from (a) to (b)).

### A04-07 (major, C06) — Q3 lowest-GBV claim false; seasonal penalty unsupported: accepted
Reproduced from `abnb_driver_history_quarterly.csv`: 2023–25 means Q1 $22.6bn, Q2 $21.3bn, Q3 $20.4bn, Q4 $17.8bn; Q4 is lower in each year. The 18.3% Q3 take rate is the check-in peak over that quarter's bookings (mechanics note §1.3), and §1.4 says lead time is undisclosed. The U(−2, 0) penalty is withdrawn; the v2 model carries symmetric mix noise U(−1, +1) instead (RNPL's payment rule gives a plausible mechanism in either direction and no evidence on sign or size). The audit's no-season numbers (0.4006/0.5994/0; wording 25.23/18.88/25.88/30) reproduce and are recorded as the benchmark.

### A04-08 (major, C06) — U(21,23), U(0,2), Exp(1.4) are assumptions manufacturing a narrow distribution: accepted
Accepted that "over 20%" supplies no 23% ceiling and that the ~70% adoption figures use different denominators (people offered, US: D005; eligible bookings, global GBV: D022) and do not establish saturation. Claim 5 rewritten. The v2 model (`share_ramp_model_v2_2026-09-17.py`) labels every input an assumption and widens them: 1Q26 share U(19,21), 1Q26→2Q26 increment U(0.5,3.5) with 2Q26 constrained to [20.5, 23.5] (the management vocabulary reason for the ceiling is stated), Q3 residual ramp U(0, 0.5) × that increment (tying the ramp to the one observed step, which is the asymmetry that keeps the distribution from running away: the entire ex-US rollout moved the stated share by one word), July expansion 0.75·Exp(1.4) + 0.25·Exp(3.5) capped 8. Result P(true ≥25) 0.389; a first pass with unanchored U(0,2.5) ramp and U(20.5,23.5) start gave 0.57 and was rejected as stacking upward assumptions. The large-expansion sensitivity is preserved (Exp(3.5) only: 0.593; rev-1's Exp(4): 0.553). Eight variants are tabulated in the CSV and §7.

### A04-09 (major, C06) — backlog-stock solve does not identify the flow share: accepted in part
Reproduced: `verify_bs_uf_only_solve.csv`, note baseline, 2Q26: 15.377% at B = 1.00, 19.407% at 1.05, 23.070% at 1.10 (and 14.0–24.4% across the other normalizations). Accepted that unpaid share and book length are inseparable and that the solve says nothing about the quarterly flow share; claim 6 is downgraded to a stock consistency check, its load-bearing flag set to no, and it is not used in the v2 model.
In part: the check is kept in the log because it is the only balance-sheet read the team has and it is not inconsistent with any share the model produces.

### A04-10 (major, C05/C07) — nowcast/Kalshi blend without a rule: accepted
Reproduced: the team normal gives 0.3677/0.2645/0.3677, not 0.42/0.30/0.28; C05's decomposition with its rev-1 conditionals is 0.2646 on its states and 0.2837 on the team normal. The blend is withdrawn. The headline now uses the run's R01/R02 forecasts, which landed after revision 1 and are the run's reconciled print-state numbers (P(≥10.0) 0.42, P(≥10.6) 0.32, implied N(9.67, 1.70): P(<9) 0.347, P(9–10) 0.233, P(decelerating vs 2Q26) ≈ 0.64). The team normal and the Kalshi ladder are each reported as a separate sensitivity (`c05_state_decomposition_v2.csv` carries all three state sets). On C05 the state choice moves the vector by at most 2 points; on C07 by 1–2 points. Kalshi claims are now marked "not used in the headline".

### A04-11 (all) — Kalshi fields misread: accepted
Reproduced: `volume_fp` 998.66 and `open_interest_fp` 689.51 at 146m; ladder totals 3,237.21 and 2,178.46; `volume_24h_fp` 0 at all seven strikes; `updated_time` 2026-08-04T18:47:36Z identical across strikes. Parsed and saved to `kalshi_q3_nights_implied_v2_2026-09-17.csv` in all three folders with bid/ask sizes; the logs distinguish the fetch time from quote freshness and say the batch stamp proves nothing either way. KXABNBA-27FEBNEB is identified as an FY2026 annual nights ladder (strikes 570–590m) in every claim that cites it.

### A04-12 (major, C07) — model centred on a bad cancellation quarter; "bounds" are a scenario slice: accepted
Reproduced: D note §2.3 full grid −1.37 to −0.10 in 3Q26; `rnpl_nights_module.csv` 3Q26 propensity effects −1.425 / −0.568 / −0.158 (bear/base/bull). The decomposition is now three mutually exclusive scenarios covering the whole contract (`c07_scenario_partition_v2.csv`): S1 adverse RNPL performance 0.15 × 0.65; S2 ordinary performance with a decelerating print 0.49 × 0.27 (quantified lap, moderated-lift wording, new dollar timing figure, 10-Q creep, terms change, resolver risk, with the routes listed); S3 routine or accelerating 0.36 × 0.10. The central −0.15 to −0.93 range is labelled a scenario slice, the full-grid and module numbers are quoted, and claim 8 now says the Q3 positive cash prediction does not close off Q4 effects or non-cash metrics.

### A04-13 (major, all) — three independent estimates not obtained; reframing is an inference: accepted in part
Accepted: every §5 now says the anchor is NO_EXTERNAL_ANCHOR and that the three-estimate requirement is unmet; C06's §5 says the base rate and decomposition share the share model and wording map and differ only in the disclosure gate; C05's claim 4 is relabelled an inference from the coincidence of a strong quarter and a "no single product" message, with the alternative (the figure stopped flattering) priced in §4 and §7. The reproduced facts (nights 9.154/10.342%, day-one +17.4%/+16.3% excess) are kept as facts.
In part: no market number was forced and no third estimate was invented; the logs record the shortfall rather than paper over it.

### A04-14 (minor, C07) — arithmetic: accepted
Reproduced: 0.28 × 0.6 = 0.168 (rev 1 wrote 0.20) → 0.1924 on the stated conditionals; strong-print sensitivity 0.05 × 0.65 + 0.95 × 0.10 = 0.1275 (rev 1 wrote 0.11). Both displayed calculations were wrong; revision 2 recomputes everything from the new partition (strong print 0.14; weak print 0.46) and the revision note records the rev-1 errors.

### A04-15 (minor, C06) — stated 3:1 blend does not produce the final: accepted
Reproduced: (3 × decomposition + base rate) / 4 = (0.145, 0.250, 0.335, 0.270), not (0.15, 0.24, 0.31, 0.30). Revision 2 no longer claims a blend: the final adopts the level-gate decomposition (0.248, 0.200, 0.259, 0.293) with rounding, and §5 says so.

### A04-16 (minor, C05/C06) — sensitivity vectors not normalized: accepted
Reproduced (C05 rounding row 1.03; C06 strong-print row 1.01). Every sensitivity row in both revision-2 JSONs is a complete four-option vector; a validator run over the saved files finds none off by more than rounding (one 1.01 row caught and corrected before saving). The audit's 80%-gate result (15.56/27.67/36.77/20 on rev-1 inputs) reproduces and is superseded by the v2 gate rows.

### A04-17 (minor, C05) — log-score cost misstated: accepted
Reproduced: ln(0.70/0.73) = −0.0420 realized if (d) resolves, not "about −0.01". Revision 2 states the realized change for its own defensive variant (ln(0.69/0.72) = −0.043) and notes that an expected-score comparison needs the whole vector (about −0.03 in expectation at these probabilities).

### A04-18 (minor, all) — absence claims not substantiated by the sources folders: accepted
Inventoried the three `sources/` folders: Polymarket and Kalshi API responses plus RNPL passage extracts; no search-result snapshots, no 4,000-event enumeration file, no conference-page capture. Every absence claim (C05 15/17/21; C06 12/14/15; C07 9/13/16/17) now reads "no relevant result found in the searches recorded", says no snapshot was saved, and separates the historical evidence from the claim about current news. The "this week" query is not described as a 72-hour filter.

## What the audit missed

1. **The Guest Favorites row is missing more than 1Q24.** The letters carry cumulative nights at Guest Favorite listings in seven quarters (1Q24 through 4Q25 except 4Q24); revision 1 coded four of them blank and 4Q25 as call-only. The audit noted only the 1Q24 omission. Completing the row raises continuation slightly (0.807 → 0.823 on the three-cell repair) and changes the gap ledger (the 4Q24 gap returned in 1Q25; a new 1Q26 gap did not return in 2Q26). It cuts against the audit's direction on the continuation rate, which is why both are published.
2. **The run's own R01/R02 forecasts supply the print-state weights.** The audit asked for the team-normal states under brief rule 6; the batch that reconciles the team band with the outside view and the market (R01 0.42, R02 0.32) landed after revision 1 and is the number the rest of the run (X01, S01) is told to use. Revision 2 uses it as the headline and the team normal as the sensitivity; the audit's team-normal C05 (0.3184 quantification) and this log's R01-state version (0.284) differ by the conditional-quantification judgment, not by the states.
3. **An RNPL-alone figure cannot reach (a).** The repaired bridge's RNPL-only branch is 1.3–1.7 points gross. The audit asked for the branch (A04-06) but did not draw the consequence for the option split: any RNPL-alone statement lands in (c) or low (b), which is one reason (c) rises in revision 2.
4. **C05 and C07 are coupled through the quantified lap.** The audit flagged the inconsistency (A04-01) but not that fixing it makes the quantified-lap portion of C05 (c) (about 0.06) a strict subset of C07 Yes; both logs now say so, which is a coherence constraint X01 can use.
5. **Management's lap vocabulary is on the record and qualitative.** The 2Q26 call said "tougher comps in the back half of the year" without naming RNPL; the 1Q26 letter named it. That is evidence for the S2 conditional in C07 being modest (0.27) rather than the audit's 0.40 for its middle branch: management has so far chosen the No-resolving form of the sentence twice.
6. **The v2 share model's first pass over-corrected.** Widening every input the audit called narrow (start, ramp, expansion) without tying the ramp to the observed 1Q26→2Q26 step gives P(true ≥25) 0.57; the audit's own benchmark (0.40) implicitly kept rev-1's narrow ramp. The response records both so the reader can see that the final 0.39 is not the widest defensible number.

## Reconciliation with Astra's numbers

| question | Astra | revision 2 | max option gap | decision |
|---|---|---|---|---|
| C05 | (0.10, 0.14, 0.08, 0.68) | (0.07, 0.11, 0.10, 0.72) | 4 pts on (d) | Hold. The gap is the conditional-quantification judgment in the strong state (0.18 vs 0.20) and the flat vs state-specific split; both are inside the sensitivity table. No asymmetry to name beyond the RNPL-alone branch (item 3), which moves mass from (a)/(b) to (c). |
| C06 | (0.25, 0.19, 0.26, 0.30) | (0.25, 0.20, 0.26, 0.29) | 1 pt | Adopted in substance: the v2 model with wider, labelled inputs lands where the audit's benchmark lands. |
| C07 | 0.25 (0.10–0.45) | 0.27 (0.15–0.40) | 2 pts | Hold. The partitions differ in shape (this log conditions the middle scenario on a decelerating print, 0.49 of the mass at 0.27, against the audit's 0.25 at 0.40) and agree in total. |

No option differs from Astra's by more than 10 points, so no divergence needs a named asymmetry; the interval on C07 is narrower than the audit's because the classification table removes part of the resolver ambiguity the audit's wider band was carrying.

## Reproduction output

`py -3.13 -B docs/pitch-forecasts/audits/A04-reproduce.py` from the repo root, 2026-09-17, first run against the revision-1 files (no edits to the script; exit code 0):

```
MATRIX SHAPE (16, 23)
         window  continued  eligible  continuation  returned  gaps  return_rate
            All         91       111      0.819820         5    19     0.263158
W1 target>=1Q23         58        76      0.763158         5    17     0.294118
W2 target>=1Q24         38        54      0.703704         5    16     0.312500
SAVED GAP LEDGER 5 / 19
POST-HOC FIVE-METRIC GROUP 0 / 5
OTHER GAP EVENTS 5 / 14
THREE VERIFIED CELL REMOVALS
         window  continued  eligible  continuation  returned  gaps  return_rate
            All         88       109      0.807339         4    19     0.210526
W1 target>=1Q23         55        74      0.743243         4    17     0.235294
W2 target>=1Q24         35        52      0.673077         4    16     0.250000
EXCLUDE THREE MIXED/INCORRECT SERIES; SENSITIVITY ONLY
         window  continued  eligible  continuation  returned  gaps  return_rate
            All         81        94      0.861702         3    12     0.250000
W1 target>=1Q23         52        64      0.812500         3    11     0.272727
W2 target>=1Q24         32        43      0.744186         3    11     0.272727
FOUR POST-LAUNCH PRINTS
                                3Q25 4Q25 1Q26 2Q26
metric
RNPL/bundle contribution (pts)   --   -C   -C   --
RNPL GBV share                   --   --   LC   -C
RNPL/bundle contribution (pts) disclosed 2 /4
RNPL GBV share disclosed 2 /4
BUNDLE RETURN-AFTER-GAP: completed n=0
GBV SHARE CONTINUATION: 1/1, 1Q26 -> 2Q26
RNPL LEDGER 60 rows; 57 local quote checks; failed []
BUNDLE NUMERIC DISCLOSURES
 statement_id       date period_referenced                   quantity
        D014 2026-02-12              4Q25 >200bp nights / ~300bp GBV
        D032 2026-05-07              1Q26 ~3 pts nights / ~4 pts GBV
GUIDANCE LEDGER (194, 25) RNPL ROWS 0
DECLINES 37 2Q26 4
quarter        analyst      firm                                                                asked                                                                 management_answer_excerpt     speaker category
 2025Q3 Richard Clarke Bernstein Percent of the US acceleration that came from Reserve Now, Pay Later So about 70% of people that we offer Reserve Now, Pay Later, take us up on that offering. Ellie Mertz    other
C07 AUTHOR LABELS 0 / 4 generous 3 / 4 Laplace 0.16666666666666666
CURRENT KPI VALUES
 quarter  nights_m  nights_m_yoy_pct
   3Q25     133.6             8.795
   1Q26     156.2             9.154
   2Q26     148.3            10.342
2023-25 GBV/TAKE-RATE MEANS
        gbv_b  take_rate_calc_pct
q
1  22.600000            9.179667
2  21.266667           13.047000
3  20.433333           18.337333
4  17.833333           14.006333
2Q26 REACTION
 print_date  ret_1d  exc_1d
 2026-08-06    17.4    16.3
reaction_date  abnb_1d_pct  excess_1d_pct
   2026-08-07         17.4           16.3
SHARE SIM base [0.216085, 0.76869, 0.015225] wording [0.13613355, 0.24213735, 0.3217291, 0.30000000000000004]
SHARE SIM large [0.552555, 0.44121, 0.006235] wording [0.34810965, 0.13898115, 0.21290919999999997, 0.30000000000000004]
SHARE SIM no season [0.400555, 0.599445, 0.0] wording [0.25234965, 0.188825175, 0.258825175, 0.30000000000000004]
AUTHOR BUNDLE 2.63 3.2399999999999998 net 1.6999999999999997 3.09
PAIRED EX-NA TOTAL 1.75 1.75
PAIRED GROSS 2.81 3.06
PAIRED NET 1.88 2.91
EARLIER-COHORT Q3 CANCELLATION SHARE 0.4574876577070762
Q3 MODULE
 scenario  m4_propensity_drag_pts  nights_yoy_pct
     bear                  -1.425            8.76
     base                  -0.568            9.49
     bull                  -0.158           10.25
UF STOCK SOLVE
                                      norm quarter   B  u_pct
note baseline: next-Q rev, 2023+2024+1H25    2Q26 1.0 15.377
note baseline: next-Q rev, 2023+2024+1H25    2Q26 1.1 23.070
KALSHI 138000000 0.955 412.02 306.00 0.00 2026-08-04T18:47:36.451419Z
KALSHI 140000000 0.925 409.93 272.19 0.00 2026-08-04T18:47:36.451419Z
KALSHI 142000000 0.88 49.86 38.35 0.00 2026-08-04T18:47:36.451419Z
KALSHI 144000000 0.7949999999999999 347.64 36.06 0.00 2026-08-04T18:47:36.451419Z
KALSHI 146000000 0.645 998.66 689.51 0.00 2026-08-04T18:47:36.451419Z
KALSHI 148000000 0.525 428.14 423.14 0.00 2026-08-04T18:47:36.451419Z
KALSHI 150000000 0.33999999999999997 590.96 413.21 0.00 2026-08-04T18:47:36.451419Z
KALSHI TOTAL VOLUME/OI 3237.21 2178.46
TEAM NORMAL STATES >=10, 9-10, <9 [0.36774269705599305, 0.2645146058880139, 0.36774269705599305]
C05 AUTHOR DECOMPOSITION 0.26460000000000006
C05 TEAM-ONLY SAME CONDITIONALS 0.2836774269705599
C07 S FROM STATED INPUTS 0.168 P 0.19240000000000002
C07 STRONG-PRINT SENSITIVITY 0.1275
C05 LOG-SCORE CHANGE IF d -0.04196419909903219
C06 STATED 3:1 BLEND [0.14500000000000002, 0.25, 0.33499999999999996, 0.26999999999999996]
C06 80% DISCLOSURE SENSITIVITY [0.15558120000000003, 0.27672840000000004, 0.36769040000000003, 0.19999999999999996]
FINAL C05 {'vector': {'a_quantified_ge_2.5pts': 0.08, 'b_quantified_1.5_to_2.5pts': 0.12, 'c_quantified_lt_1.5pts': 0.07, 'd_not_quantified': 0.73}}
FINAL SUM 1.0
INVALID SENSITIVITY SUM management rounds up to 'approximately 3 points' again 1.03
FINAL C06 {'vector': {'a_ge_25pct': 0.15, 'b_21_to_24pct': 0.24, 'c_over_20_repeated_or_le_20': 0.31, 'd_not_disclosed': 0.3}}
FINAL SUM 1.0
INVALID SENSITIVITY SUM nights print >= 10.6% (P(disclosed) 0.80) 1.01
FINAL C07 {'p': 0.2, 'ci': [0.12, 0.32]}
FINAL R03 {'p': 0.07, 'ci': [0.04, 0.12]}
FINAL R01 {'p': 0.42, 'ci': [0.3, 0.55]}
R03 CAP 0.07 <= 0.15
AUDIT C05 [0.0987000118043679, 0.14009033933523185, 0.07959678371319992, 0.6816128651472003]
AUDIT C06 NO-SEASON BENCHMARK [0.25234965, 0.188825175, 0.258825175, 0.30000000000000004]
AUDIT C07 0.25
```

Second run, after the revision-2 files were saved (only the tail changes): `FINAL C05 (0.07, 0.11, 0.10, 0.72)`, `FINAL C06 (0.25, 0.20, 0.26, 0.29)`, `FINAL C07 {'p': 0.27, 'ci': [0.15, 0.4]}`, `R03 CAP 0.07 <= 0.25`, no `INVALID SENSITIVITY SUM` lines (one 1.01 row in C06 was caught by this check and corrected before the final save). Independent revision-2 computations: `metric_persistence_matrix_v2_recode.py` (0.823/0.769/0.714; 4/18, 4/16, 4/15), `share_ramp_model_v2_2026-09-17.py` (0.389/0.606/0.005 base; benchmark 0.400/0.599/0.000 and rev-1 0.216/0.769/0.015 reproduced inside the same script), `A04-response-datasets.py` (C05 states and vector; C07 partition 0.2658).

## Final table

| question | revision-1 number | Astra's number | revision-2 number | anchor | \|final − anchor\| |
|---|---|---|---|---|---|
| C05 MC: bundle/RNPL contribution quantified for 3Q26 (a ≥2.5 / b 1.5–2.5 / c <1.5 / d not) | 0.08 / 0.12 / 0.07 / 0.73 | 0.10 / 0.14 / 0.08 / 0.68 | **0.07 / 0.11 / 0.10 / 0.72** | none (NO_EXTERNAL_ANCHOR; Kalshi nights ladder adjacent, sensitivity only) | n/a (vs Astra: 4 pts max, on (d)) |
| C06 MC: RNPL share of 3Q26 GBV disclosed (a ≥25 / b 21–24 / c "over 20%" or ≤20 / d not) | 0.15 / 0.24 / 0.31 / 0.30 | 0.25 / 0.19 / 0.26 / 0.30 | **0.25 / 0.20 / 0.26 / 0.29** | none (NO_EXTERNAL_ANCHOR) | n/a (vs Astra: 1 pt max) |
| C07 binary: RNPL negative effect acknowledged beyond the 2Q26 boilerplate | 0.20 (0.12–0.32) | 0.25 (0.10–0.45) | **0.27 (0.15–0.40)** | none (NO_EXTERNAL_ANCHOR; Kalshi P(≤146m) ≈ 0.355 adjacent, sensitivity only) | n/a (vs Astra: 2 pts) |
| R03 (batch A09) implied recompute | 0.07 (on C06 a = 0.15) | — | **≈ 0.13** (0.51 × 0.25, R03's own rule; cap min(C06 a, R01) = 0.25) | — | — |
