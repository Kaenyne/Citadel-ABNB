# Response to audit A05 (C08 q3-revenue-fx-integer, C11 q3-take-rate-above-1810, C12 q3-unearned-fees-yoy)

Response date: 2026-09-17
Responds to: `A05-research-audit.md` (Astra, gpt-6-astra, read-only)
Revised research: the three `research-log.md` files (revision 2) and `forecasts/2026-09-17-forecast.json` (revision 2) under `questions/q3-revenue-fx-integer/`, `questions/q3-take-rate-above-1810/`, `questions/q3-unearned-fees-yoy/`
Revised models: `datasets/c08_model_v2.py`, `datasets/c11_model_v2.py`, `datasets/c12_model_v2.py` (the revision-1 scripts and their CSVs are left untouched as the audit trail)
Reproduction script: `A05-reproduce.py` (the audit's script, saved verbatim from the audit; ran clean from the repo root with `py -3.13`, no path fix needed; output at the end of this file)

## Summary

Eighteen findings. Fifteen accepted, three accepted in part (A05-06 on C12's flag, A05-12, A05-17), none rejected. Every number in the audit reproduced: the 14 generated tables, the 1Q23 numeric FX miss (−2 guided, −4 printed), the +21.2bp 2Q25 take-rate change, the C11 band integral 0.7646 against the 0.55 headline, the two un-normalised C08 sensitivity rows (0.921 / 1.048), the C08 analytic tails (0.044 / 0.007), the two-year unearned-fees norm 0.6648, the 0/14 and 0/10 historical counts, and all three of Astra's comparison forecasts (0.558 / 0.263 / 0.159; 0.684; 0.438).

Headline numbers, revision 1 → revision 2:
- **C08** 0.50 / 0.30 / 0.18 / 0.02 → **0.49 / 0.28 / 0.21 / 0.02**. The management component is widened to sd 1.0 (the rev-1 RESUME pre-registered exactly this response to a full-point numeric miss), each model component now carries its own point-in-time error, and every sensitivity holds the weights fixed. Astra 0.56 on (a); the 7-point gap is one weight choice (§C08 reconciliation).
- **C11** 0.55 (0.40–0.70) → **0.76 (0.60–0.88)**. Rev 1 was incoherent: its own conditional table integrated to 0.765 while the headline was a separately pooled 0.55. Revision 2 is one joint model whose band table integrates to the headline by construction, built on the run's print-state distributions (R01 nights N(9.67, 1.70), B02 ADR mixture) with a 0.25 Street/market GBV route. Astra 0.68; the 8-point gap is Astra's 30% "language regime", which on the same GBV marginal implies a first-ever revenue-guide miss with probability 0.24 against 19/19 beats.
- **C12** 0.55 (0.40–0.70) → **0.43 (0.28–0.60)**. The unpaid-share input is now a three-branch mixture that prices the alternative reading of management's D038 sentence (catch-up 0.30 / convergence 0.45 / deepening 0.25; mean 16.9, sd 3.1), the norm is the two-year pre-RNPL 0.6648, the 13 Oct rule is withdrawn, and the historical zero count is published. Astra 0.44; agreement to a point.

What moved the numbers: C08, the sd repairs (A05-02, A05-05) — the weights did not change; C11, the coherence repair (A05-01) plus the run's nights distribution — the rev-1 pooled 0.55 had no model behind it; C12, the D038 alternative reading and the corrected norm (A05-07, A05-09) — the rev-1 u N(18, 3) alone carried 0.56.

## Finding-by-finding

### A05-01 (critical, C11) — conditionals and unconditional were different forecasts: accepted
Reproduced: `c11_by_gbv_band.csv` masses sum to 1.000 and Σ mass × P(YES | band) = 0.7646 (in-memory replay 0.7650); the JSON headline was 0.55, the stated linear pool 0.5265 rounded up. The table was the decomposition; the headline was something else. Fix: `c11_model_v2.py` is one joint model (GBV marginal = 0.75 print-state + 0.25 Street/market route; revenue conditional on GBV inside each component) and the headline, the band table and the point-GBV rows are read off the same 600,000 draws. Band integral 0.7783 = headline 0.7783 (`c11_v2_by_gbv_band.csv`). Convention (5) in the log says no adjustment is ever applied to the pooled number outside the model. Any "language" or "Street" view now enters as a component weight before conditioning, which is the only place it can enter coherently.

### A05-02 (major, C08) — selected reference class; the 1Q23 numeric miss; ambiguous codings: accepted
Reproduced from the letters and the ledger: the 4Q22 letter guided 1Q23 at "16% to 21% … on an ex-FX basis between 18% and 23%" (FX −2, ledger midpoints 18.5 / 20.5) and the 1Q23 letter printed 20% / 24% ex-FX (FX −4): a two-point miss below an explicit numeric guide. Re-read the 3Q23 Outlook: "12% to 14%, which is relatively stable growth compared to Q3 2023 excluding the impact of FX" — the natural reading (4Q23 ex-FX ≈ 3Q23's 14%, reported 12–14) gives FX −1 to 0, not the +2 rev 1 coded, and the print was +3; and the 1Q24 letter's "significant sequential headwind … Easter, Leap Day, and the impact of FX rate changes" gives no FX share. Both dropped. Rev-2 track record (`c08_v2_track_record.csv`): numeric guides n 4, errors −2 / +1 / 0 / +1 (mean 0.0, sample sd 1.41, ≈ 1.35 net of the two-integer rounding), printed ≥ guided 3/4 (W1) and 3/3 (W2), within ±0.5 in 1 of 4; analyst-coded phrases n 5 (mean +0.4, sd 0.74), labelled judgement. "9 of 10 / never more than 0.5 below" withdrawn. Consequence: the management component's sd goes 0.6 → 1.0 (the rev-1 RESUME's pre-registered response), which on its own moves (a) 0.51 → 0.49 at rev-2 sds elsewhere; the record is two-sided with mean zero, so the centre stays at 3.0 (rev 1's implicit "+0.55 upward bias" is gone). The audit's "+3 subgroup 2/2 is too small to establish a 0.6-point sd" is right; the sd is now a judgement (1.0) sitting between the pre-hedge numeric record (1.35) and the rev-1 value, with both ends in the sensitivity table (0.47–0.52 on (a)).

### A05-03 (major, C11) — 2Q25 take-rate change +21.2bp, not +9; "errors vs guided direction" undefined: accepted
Reproduced: 3096/23500 − 2748/21200 = 21.22bp; the six rev-1 pairs' realised changes are +0.4 / +21.2 / −68.5 / −47.3 / −10.2 / +9.0bp (mean −15.9). Fix: claim 4 rebuilt from the guidance ledger's `take_rate_yoy_pts` metric, all twelve resolved pairs 1Q23–2Q26 (`c11_v2_language_record.csv`): direction met 9 of 12; realised ≥ +22bp (what YES needs on 17.88) in 3 of 12, all under "higher"-type language; the three "flat"-class guides realised +14 / −69 / −47 (0 of 3); last six mean −20bp, sd 34. The base-rate estimate stays 0.18 but is now labelled an elicited judgement between the flat-class Laplace (0.20) and the all-class frequency (0.25), with the normal-on-recent-errors figure (0.11) beside it. "The print has never exceeded the guided direction by more than +9bp" withdrawn (2Q23 +63, 1Q24 +44, 4Q23 +22 all did).

### A05-04 (major, C08) — un-normalised sensitivity rows; dollar sign error: accepted
Reproduced: the "centre 3.5" row used weights summing to 0.92 (vector sum 0.921) and the "dollar −5%" row 1.05 (1.048); the code subtracted 0.8 from a basket defined positive for a weaker dollar. Fix: `c08_model_v2.py` holds weights fixed in every row and asserts every vector sums to 1 (`c08_v2_sensitivity.csv`, 21 rows). Rev-2 corrected rows: centre 3.5 → 0.54 / 0.25 / 0.19 (Astra's repair of the rev-1 row: 0.568 / 0.244 / 0.168 at rev-1 sds — reproduced); dollar −5% for the remaining 21% of the quarter (73 of 92 days observed at 11 Sep) = +1.05pp on the quarter-average basket, moving only the lag-0 loadings (free fit 0.45, contemporaneous 0.56) → 0.50 / 0.29 / 0.19, and the mirror +5% → 0.48 / 0.28 / 0.22. The mapping from a dollar move to the basket is now stated (days remaining × move).

### A05-05 (major, C08) — H2's 0.99 RMSE attributed to the Φ × 0.851 basket construction: accepted
Reproduced from `09c_pit_window_scores.csv`: H2 (ADR-FX driver) W1/W2 RMSE 0.9936, interval 0.5782, n 10/10, live point 1.8527; H2b (basket) W1 1.7975 / W2 1.3155, interval 1.4619 / 0.9923, n 14/10, live 2.9960; B4 §3: "The 0.851 scale is the free fit's total scale re-assigned onto the Φ shape — it is a construction, not a fitted object." Fix: claim 5 attributes each score to its spec; each model component carries the midpoint of its own point and interval RMSE (the kernel adds the ±0.5 rounding itself, so the point RMSE would count it twice and the interval RMSE would drop it): Φ × 0.851 / H2b 1.15 (was 0.6), the H2 cluster 0.80 (was 0.7), the free fit 1.60 (was 0.7), the contemporaneous 1.75 (was 0.7). Effect at rev-2 management sd: the wider basket and short-lag sds move mass from (b) to (c) (0.51 / 0.30 / 0.17 → 0.49 / 0.28 / 0.21) and leave (a) nearly unchanged, which is the sensitivity table's "all sds × 1.5 / × 0.75" result too.

### A05-06 (major, all three) — three independent estimates not established: accepted (C08, C11); accepted in part (C12)
C08: the anchor (registered H2 PIT object) is a member of the decomposition's middle cluster; flag set true, anchor re-labelled, Astra's vector recorded as the audit comparison. C11: the anchor's 0.45 was a "nudge" between an internal transformation of observed Street levels (17.99% at a model sd) and the Kalshi route already in the decomposition; rev 2 records the levels (LSEG 4,744.88 at 2026-09-13T15:20Z; MODL 26,375, 12 Sep) as external, the probability (0.40 at the joint model's sd 0.42) as internal, flag true, and Astra's 0.68 as the audit number. C12: the flag was already true; in part because the audit's further point — that the anchor's 0.45 "is not derived from a probability distribution" — is accepted as a description (it is a reading of note 04's table at u 15–16, "roughly even") and the anchor is now stated that way, but no external probability exists to replace it, and the log says so rather than manufacturing one.

### A05-07 (major, C12) — the D038 alternative model given no weight: accepted
Reproduced: the 1Q26 letter's FCF paragraph says "lower unearned fees in Q1 and Q2 and higher unearned fees in Q3"; D038/D055 read it as a forward test of a higher Q3 line; rev 1 read it as a flow statement and then modelled a deeper Q3 shortfall (deepening −1.5 ± 1.5 on the sequential route) — as the audit says, the flow reading implies the 30 Sep shortfall is smaller than the 30 Jun one, the opposite of what rev 1 modelled. The accounting argument ("RNPL cannot raise the stock") holds only with the booking book fixed. Fix: convention (4) rewritten as two readings with weights; the unpaid share u_3Q26 is a three-branch mixture — catch-up N(14.5, 2) at 0.30 (the flow reading; u below 30 Jun's 15.1), convergence N(17.0, 2.5) at 0.45, deepening N(19.5, 3) at 0.25 (July expansion, longer-dated Q4/Q1 book, C06 v2's P(flow ≥ 25) 0.39) — and Route B's deepening term is now the same mixture instead of a free normal. Branch-by-branch the mixture gives 0.17 / 0.45 / 0.70; the catch-up branch's 0.17 is what the alternative model "changes P" to, which is what the audit asked to see.

### A05-08 (major, C12) — quoted unpaid-share ranges too narrow; u and B inseparable; flow ≠ stock: accepted
Reproduced from note 04 C3: at B = 1.00, 1Q26 10.7–13.9% (median 13.0) and 2Q26 14.0–16.8% (median 15.1); at B = 1.10, 18.8–21.8 / 21.8–24.4; "No public constraint separates u from B; u stays a range." Rev 1 quoted the narrow verdict-table figures. Fix: claim 5 quotes the full table; convention (5) defines u as the effective shortfall at B = 1 (a longer-dated book raises the counterfactual and the shortfall together, so it is carried as a higher effective u in the deepening branch); claim 9 states that flow adoption is not a stock measurement and uses the one observed pair (2Q26 flow "over 20%", solved u 15.1) only as a ~0.70 stock/flow ratio for the convergence branch. u N(18, 3) is replaced by the mixture (mean 16.9, sd 3.1); replayed Route A alone moves 0.455 → 0.360.

### A05-09 (major, C12) — the "pre-RNPL" norm included the launch quarter: accepted
Reproduced: 3Q UF / next-quarter revenue 0.661407, 0.668145, 0.655148 for 2023–25; two-year mean 0.664776, three-year 0.661566 = rev 1's 0.661. Fix: Route C uses N(0.6648, 0.008) (n 2 kept as uncertainty); 0.661 and 0.655 are sensitivities (0.44 / 0.46 on the mixture).

### A05-10 (major, C12) — the 13 Oct deadline cannot move a 30 Sep balance: accepted
Reproduced: the rule "migration term to the top of its range … final −0.03" attached a probability change to an event after the balance date. Fix: the monitoring row now says no direct change; update only if the announcement reveals EEA migration effective before 30 Sep (migration term +1.5 in Route A → −0.02); the non-EEA deadline (15 Sep) is already inside the migration term.

### A05-11 (major, C11) — point-GBV rows were alternative priors, not conditionals: accepted
Reproduced: `run(gbv_override=g, gbv_override_sd=1.0)` re-centred the GBV prior at each g and recomputed z from it. Fix: the release prints GBV to $0.1bn, so {printed GBV = g} is an event with mass in the joint model; `c11_v2_point_gbv.csv` conditions on those draws (7,450–43,000 draws per cell), with the revenue conditional rising with GBV through ρ: 25,900 → 0.98, 26,000 → 0.97, 26,100 → 0.95, 26,300 → 0.78, 26,400 → 0.58, 26,500 → 0.33, 26,600 → 0.12, 26,800 → 0.004. Break-even GBV at the median cushion $26,404M, at the guide low $25,912M.

### A05-12 (major, C11) — the "+0.02 for the FX wedge" counted information twice: accepted in part
Accepted that the uplift was applied to a pooled number and that the wedge is already in the inputs (the revenue guide is stated inclusive of ~+3 FX; the ADR draws are reported, FX-inclusive); rev 2 has no post-model adjustment and claim 12 says so. In part: the audit's remark that "C08 assigns only 0.50 to ≥ +3 stated points" is not an inconsistency with C11 — C11 uses the dollar revenue guide, whose FX content is whatever management built in, and the printed FX integer does not enter the take-rate ratio; no cross-question adjustment is needed.

### A05-13 (major, C12) — Route A is a model, not a base rate; the historical frequency was absent: accepted
Reproduced: UF y/y ≤ −3% in 0/14 (W1), 0/10 (W2), 0/4 Q3s, 0/4 post-launch quarters (`c12_v2_base_rate.csv`); the UF-minus-GBV gap ran −0.3 to +6.1 through 2Q25, then −4.1 / −8.1 / −18.8 / −16.7. Fix: the counts are published in claim 17 with the regime-break caveat; the base-rate estimate is 0.10 (Laplace on a zero count, lifted for the break) and is not blended numerically — the log says the regime-conditioned outside view is the gap itself; rev 1's "base rate 0.46" is relabelled the gap-model estimate.

### A05-14 (major, C11) — extreme gate skipped on the conditionals; GBV rounding not modelled: accepted
Reproduced: the rev-1 table showed 1.00 / 0.99 / 0.97 / 0.00 with no gate; the ≥ 26,800 band's raw 0.004 was displayed as 0.00. Fix: `c11_model_v2.py` rounds every GBV to $100M before the ratio (headline unchanged to 3 dp; a cell is ±3.4bp); the gate is run on the conditionals in §6 (edge cases: GBV rounding, revenue definition, first-ever guide miss at 0.03, 3Q25 restatement irrelevant to a same-quarter ratio, print date); conditionals are quoted with floors/caps 0.005 / 0.995 and the raw values are kept in the JSON beside them.

### A05-15 (minor, C08) — within-option tails did not follow from the model: accepted
Reproduced analytically: P(integer ≤ 0) 0.0444 and P(< 0) 0.0073 under the rev-1 components, against the published 0.10 / 0.02; P(≥ 4) 0.128 did reproduce. Fix: rev 2's tails come from the same model — P(≥ 4) 0.20, P(≤ 0) 0.07, P(< 0) 0.03 (wider because the component sds widened).

### A05-16 (minor, C11) — "volume field None" missed the activity fields: accepted
Reproduced: `volume_fp` 590.96 (150m), 428.14 (148m), 998.66 (146m), 347.64 (144m), 49.86–412.02 at the lower strikes; `volume_24h_fp` 0.00 and `liquidity_dollars` 0.0000 everywhere; interpolated median 148.27m. Claim 9 rewritten; the ladder is labelled a thin resting book; the Kalshi route sits inside the Street/market component rather than standing as an anchor.

### A05-17 (minor, all three) — the recency check re-used the broad query; excerpts, not full responses: accepted in part
Accepted that query 12/13 in each log was the batch's "Airbnb news" query re-used, not a separate date-filtered search, and that the smoobu and help-centre pages are held as excerpts; each log now says so (claims 16 / 15 / 16 and the query-log entries). In part: no new search was run — this response is repo-only, as A01's was, and the WebSearch budget is shared across the run; the logs record that the recency evidence is the 17 Sep snippet set and nothing later. The audit's own caution that nothing here warrants alleging a confirmation-shaped search is noted and agreed.

### A05-18 (minor, C11) — "inconsistent" not demonstrated: accepted
Reproduced: 4730/26317 = 17.9732%, prior 17.8821%, +9.1bp, inside ±10bp. Claim 5 now says the guide midpoints and "in-line" are consistent, and the explanation of why the realised ratio can leave the language interval is the joint model (revenue beat, GBV dispersion).

## What the audit missed

1. **Astra's own C11 language regime implies a revenue-guide miss.** With take rate ~ N(17.90, 0.35) independent of GBV and the mandated GBV marginal, revenue = take × GBV lies below the guide floor ($4,690M) in 67.5% of the regime's draws (below the midpoint in 77.7%), so the pooled 0.68 carries an unconditional first-ever guide-miss probability of about 0.24 against 19/19 midpoint beats (15/19 above the top of the range). The information in "in-line" is about GBV, and that is where the joint model carries it (component S, 0.25). This is the asymmetry that keeps C11 at 0.76 rather than 0.68.
2. **The numeric FX record is two-sided, which removes rev 1's upward bias, not just its floor.** The audit's framing ("printed ≥ guide 3/4") keeps the flavour of a floor; the four errors (−2 / +1 / 0 / +1) have mean zero, so the management component should be centred at 3.0 with a wider sd, and the rev-1 pre-mortem item "management undershoots as in 2Q26" is no more likely than the mirror. The 3Q23 → 4Q23 pair the audit flagged as ambiguous is, on its natural reading, a three-point miss *above* the guide — further evidence for width, not direction.
3. **Point RMSE and the rounding kernel double-count.** The audit proposes calibrating the Φ × 0.851 component "using its own errors" (H2b point RMSE 1.32); the kernel already adds the ±0.5 letter rounding, and fx-lag §2 measures that rounding at 40% of the apparent error. Rev 2 uses the midpoint of each spec's point and interval RMSE; using the point RMSE straight would over-widen every component by 0.15–0.35pp.
4. **The D038 flow reading flips the sign of the sequential route, not just its weight.** The audit noted the contradiction; the replay shows the size: under the catch-up branch the Q3 sequential change is *less* negative than the 2023–25 norm (−36.9 → about −35.4 at u 13), and the sequential route alone drops from 0.68 to about 0.2. Rev 1's Route B was the highest of the three routes for a reason that pointed the other way.
5. **3Q25's own sequential change already contradicts small-u reasoning.** The RNPL launch quarter (u rising 0 → ~3.5) should have produced the most negative Q3 change of the three; it produced the least negative (−36.3 vs −36.8 / −37.5). GBV acceleration (+14% vs +11%) dominated. The season's noise is therefore wider than the 0.6pp sample sd suggests; Route B's norm sd is 1.0 in rev 2.
6. **The run's own print-state distributions.** R01/R02 (nights N(9.67, 1.70)), R07/B02 (the ADR mixture) and C06 v2 (P(flow ≥ 25) 0.39) landed after the A05 forecast; the audit could not use them. Plugging them in moves C11's print-state component from 0.87 (rev-1 inputs) to 0.86 and C12's Route A from 0.42 (rev-1 GBV) to 0.36 (with the u mixture); the C06 share model is what justifies the deepening branch's 0.25.
7. **The GBV printing grid makes the point rows well-defined.** Because the release prints GBV to $0.1bn, "P(YES | GBV = 26,300)" is a conditional on an event of positive mass, not a density slice; the audit asked for a kernel-density conditioning that is not needed.
8. **The quarter is 79% observed.** 73 of 92 days of 3Q26 were printed in FRED at 11 Sep, which is why a ±5% dollar move for the rest of the quarter is worth ±1.05pp on the basket and ≤ 0.015 on (a); the audit asked for the mapping but did not note how little room the calendar leaves.

## Reconciliation with Astra's numbers

**C08 (Astra 0.56 vs rev 2 0.49 on (a)).** Astra's vector reproduces to 3 dp under its construction. The gap is one weight choice: Astra drops the free-fit and contemporaneous specs and puts 0.50 on management; this log keeps 0.15 on the short-lag family (the in-sample winner on n 14, Φ rejected at p 0.017, and the spec the programme registered) and management at 0.38 (numeric record n 4 with one two-point miss). With Astra's weights and the rev-2 sds the model gives 0.55 / 0.28 / 0.15 — the sds are not the disagreement. Decision: hold 0.49; inside 10 points; both say (a) is a coin flip.

**C11 (Astra 0.68 vs rev 2 0.76).** Astra's direct route (0.857) is this model's print-state component under rev-1 inputs (0.856 reproduced). The gap is the 30% language regime, which implies a 0.24 guide-miss probability (item 1 above). Decision: hold 0.76; inside 10 points. What takes the number into Astra's interval without judgement: a nights centre ≥ 10.5 (0.69) or a MODL GBV mean ≥ $26.6bn (≈ 0.72).

**C12 (Astra 0.44 vs rev 2 0.43).** Astra's model reproduces (0.310 / 0.437 / 0.569 at u 15 / 16.5 / 18) and is Route C with u N(16.5, 4); rev 2's u mixture has mean 16.9, sd 3.1, and its three routes (0.36 / 0.53 / 0.43) bracket Astra. Decision: 0.43; the remaining difference is presentational.

## Reproduction output

`py -3.13 docs/pitch-forecasts/audits/A05-reproduce.py` from the repo root, 2026-09-17 (script saved verbatim from the audit; exit 0; no edits):

```
Revenue midpoint beats: successes, n
(19, 19)

Revenue beats, targets 2023+
(14, 14)

Revenue beats, targets 2024+
(10, 10)

Q3 revenue cushions
target_period  beat_pct
         3Q22  1.908127
         3Q23  1.402985
         3Q24  0.864865
         3Q25  0.862069
Q3 mean including 2022: 1.2595115283723812
Q3 mean 2023-25: 1.0433063016696515
Trailing-eight mean: 1.8567430632975808

Historical Q3 printed take rates
quarter  revenue_musd  gbv_musd      take
   3Q21        2237.0   11900.0 18.798319
   3Q22        2884.0   15600.0 18.487179
   3Q23        3397.0   18300.0 18.562842
   3Q24        3732.0   20100.0 18.567164
   3Q25        4095.0   22900.0 17.882096

Six language-pair actual changes; not guidance residuals
quarter      take  change_bp
   3Q24 18.567164   0.432265
   2Q25 13.174468  21.220393
   3Q25 17.882096 -68.506811
   4Q25 13.617647 -47.326203
   1Q26  9.171233 -10.223651
   2Q26 13.264706   9.023780
Q3 take >=18.10, starting year 23 2 / 3
Q3 take >=18.10, starting year 24 1 / 2
Guide-midpoint take rate: 17.973173234031236
Prior Q3 take rate: 17.882096069868997
Difference, bp: 9.10771641622371

Supplied FX track: n, >=guide, mean error, sample SD: 10 9 0.55 0.5986094998689324

Explicit numeric FX guide/print pairs
target  guided_fx  printed_fx  error
  1Q23       -2.0        -4.0   -2.0
  1Q25       -3.0        -2.0    1.0
  1Q26        3.0         3.0    0.0
  2Q26        3.0         4.0    1.0
Numeric FX printed >= guide, starting year 23 3 / 4
Numeric FX printed >= guide, starting year 24 3 / 3
PIT H2_phi_adrfx in_W1 n 10 RMSE 0.9935896461819638 interval RMSE 0.5782344412087541
PIT H2_phi_adrfx in_W2 n 10 RMSE 0.9935896461819638 interval RMSE 0.5782344412087541
PIT H2b_phi_basket in_W1 n 14 RMSE 1.7975128837209644 interval RMSE 1.4618843439205442
PIT H2b_phi_basket in_W2 n 10 RMSE 1.3154521534438264 interval RMSE 0.9923250188320358

Live H2/H2b points
          spec guide_date  point  sigma
  H2_phi_adrfx 2026-08-06 1.8527 1.7143
H2b_phi_basket 2026-08-06 2.9960 2.2395

C08 analytic original mixture: [np.float64(0.5084853571203934), np.float64(0.2995990233305788), np.float64(0.1719156195490278), 0.02]
Corrected centre-only sensitivity: [np.float64(0.5683259350528906), np.float64(0.24371639602599865), np.float64(0.16795766892111072), 0.02]
Corrected +0.8-point basket sensitivity: [np.float64(0.5170514790882818), np.float64(0.31522083023307224), np.float64(0.14772769067864605), 0.02]
C08 P(integer <= 0): 0.044406966686856106
C08 P(integer <= -1): 0.007291926760275773

Invalid saved C08 sensitivity vectors
                                                                          assumption  a_ge3  b_eq2  c_le1  d_not_stated  vector_sum
                             management centre 3.5 (2Q26-style +1 overshoot repeats)  0.495  0.238  0.168          0.02       0.921
dollar -5% for the rest of the quarter (basket lag-0 term only; Phi specs unchanged)  0.505  0.289  0.234          0.02       1.048

C11 band mass: 1.0
C11 integrated probability: 0.764632
C11 stated final linear pool: 0.5265

C11 L0 revenue anchor
     value                      vendor   as_of_timestamp  n_estimates
4744.88187 Yahoo Finance (LSEG family) 2026-09-13T15:20Z           36.0

C11 MODL GBV anchor
 street_mean  n_estimates                                                                                        source
     26375.0           28 Bloomberg MODL, Standard Consensus, screenshot 12 Sep 2026 (Krish); values read off the image

Saved Kalshi activity fields
 floor_strike yes_bid_dollars yes_ask_dollars volume_fp volume_24h_fp liquidity_dollars
    150000000          0.3200          0.3600    590.96          0.00            0.0000
    148000000          0.5000          0.5500    428.14          0.00            0.0000
    146000000          0.6300          0.6600    998.66          0.00            0.0000
    144000000          0.7600          0.8300    347.64          0.00            0.0000
    142000000          0.8400          0.9200     49.86          0.00            0.0000
    140000000          0.8900          0.9600    409.93          0.00            0.0000
    138000000          0.9400          0.9700    412.02          0.00            0.0000
Interpolated Kalshi median, million nights: 148.27027027027026
UF <=-3%, starting year 23 0 / 14
UF <=-3%, starting year 24 0 / 10

C12 Q3 historical observations
quarter  unearned_fees_musd       yoy  sequential     norm
   3Q23              1467.0 20.216340  -37.494674 0.661407
   3Q24              1657.0 12.951602  -36.779855 0.668145
   3Q25              1820.0   9.837055  -36.296815 0.655148
Q3 sequential mean / sample SD: -36.857114636630776 0.6026553402129475
Pre-RNPL norm: 0.6647759169842055
Norm including RNPL launch quarter: 0.6615664740537852
Dollar threshold: 1765.3999999999999
Route A central unpaid-share threshold: 18.32758620689655
Route C central unpaid-share threshold: 17.201641351063035
C12 weighted probability from rounded components: 0.55755

Auditor C08: [0.5581914219154107, 0.2626209758559656, 0.1591876022286236, 0.02]
Auditor C11 direct route / final: 0.85656 0.6844
Auditor C11 bands: mass, conditional probability
0.28501333333333334 0.7868403817365269
0.2283 0.7717038983793254
0.22468666666666667 0.752336587247426
0.15264666666666668 0.6353670786565926
0.07544 0.20104277129727818
0.03391333333333333 0.0815804993119717
Auditor C12: unpaid mean, P, median UF: 0.15 0.3126 1812.5593309535066
Auditor C12: unpaid mean, P, median UF: 0.165 0.43818 1780.5163264197208
Auditor C12: unpaid mean, P, median UF: 0.18 0.56926 1748.5136514246158
```

Separately replayed in the revision-2 scripts (not in the audit's script): Astra's C08 mixture 0.558 / 0.263 / 0.159 (`c08_v2_sensitivity.csv` row 19); Astra's C11 construction 0.856 / 0.284 / 0.685 and its language regime's guide-miss share 0.675 (`c11_model_v2.py` output); Astra's C12 model 0.310 / 0.437 / 0.569 (`c12_model_v2.py` output). All match the audit.

## Final table

| question | revision-1 number | Astra's number | revision-2 number | anchor | \|final − anchor\| |
|---|---|---|---|---|---|
| C08 MC: stated 3Q26 revenue-FX integer (a ≥ +3 / b +2 / c ≤ +1 / d not stated) | 0.50 / 0.30 / 0.18 / 0.02 | 0.56 / 0.26 / 0.16 / 0.02 | **0.49 / 0.28 / 0.21 / 0.02** | (a) 0.22 — registered fx-lag-v2 H2 PIT +1.85 through the kernel (NOT_INDEPENDENTLY_DERIVED; no market) | 0.27 on (a) (vs Astra 0.07) |
| C08 within-option: P(≥ +4) / P(≤ 0) / P(< 0) | 0.13 / 0.10 / 0.02 | 0.128 / 0.044 / 0.007 (rev-1 model, analytic) | **0.20 / 0.07 / 0.03** | — | — |
| C11 binary: P(printed 3Q26 take rate ≥ 18.10%) | 0.55 (0.40–0.70); own band table integrated to 0.765 | 0.68 (0.50–0.85) | **0.76 (0.60–0.88)**; band integral 0.778 = model headline | 0.40 — Street-implied 17.99% (LSEG 4,744.9 / MODL 26,375) at the model sd (NOT_INDEPENDENTLY_DERIVED; Kalshi thin) | 0.36 (vs Astra 0.08; vs B1's published 0.53: 0.23) |
| C11 conditionals: P(YES \| GBV band) for < 25.6 / 25.6–25.9 / 25.9–26.2 / 26.2–26.5 / 26.5–26.8 / ≥ 26.8 $bn | 1.00 / 0.99 / 0.97 / 0.76 / 0.17 / 0.00 | 0.79 / 0.77 / 0.75 / 0.64 / 0.20 / 0.08 | **≥ 0.995 / 0.99 / 0.97 / 0.76 / 0.18 / ≤ 0.005** (masses 0.24 / 0.20 / 0.21 / 0.16 / 0.09 / 0.10) | — | — |
| C12 binary: P(30 Sep 2026 unearned fees ≤ −3% y/y) | 0.55 (0.40–0.70) | 0.44 (0.25–0.65) | **0.43 (0.28–0.60)**; median $1,780M (−2.2%) | 0.45 — note-04 deferral-only table at u 15–16 (internal, NOT_INDEPENDENTLY_DERIVED) | 0.02 (vs Astra 0.01) |
