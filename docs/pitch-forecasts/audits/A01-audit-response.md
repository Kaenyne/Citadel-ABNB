# Response to audit A01 (C01, q4-revenue-guide-vs-street)

Response date: 2026-09-17
Responds to: `A01-research-audit.md` (Astra, gpt-6-astra, read-only)
Revised research: `questions/q4-revenue-guide-vs-street/research-log.md` (revision 2)
Revised forecast: `questions/q4-revenue-guide-vs-street/forecasts/2026-09-17-forecast.json` (revision 2)
Revised model: `questions/q4-revenue-guide-vs-street/datasets/c01_model_v2.py` (revision-1 `c01_model.py` and its CSVs left untouched as the audit trail)
Reproduction script: `A01-reproduce.py` (the audit's script, saved verbatim; output at the end of this file)

## Summary

Thirteen findings. Eleven accepted, two accepted in part, none rejected. Every number in the audit reproduced exactly (the script ran clean from the repo root with `py -3.13 -B`; no path fix was needed). Astra's independent analytic 62% is also reproduced, and this model gives 0.626 under Astra's conventions, so the gap between the two forecasts is three named modelling choices, not arithmetic.

Headline numbers, revision 1 → revision 2: P(Yes) **0.75 (0.62–0.85) → 0.72 (0.60–0.82)**; guide-midpoint percentiles 2,960/2,990/3,040/3,100/3,160/3,215/3,250 → **2,945/2,980/3,035/3,100/3,165/3,225/3,265**; mass below $2,900M 0.8% → 1.5%, above $3,400M 0.1% → 0.3%; guide-surprise object 0.51 → 0.51; base-rate estimate 0.55 → 0.50; anchor 0.68 → 0.67 (now labelled weak).

What actually moved the number: the cut in the market route's weight (thin Kalshi book) and the larger weight on the registered-conventions component (0.15 → 0.25) after the audit showed the residual mean, residual sd and cushion blend were undocumented judgments. The gate correction, the ladder-consistent Kalshi distribution and the wider nights sd each moved the headline by less than half a point. The structural argument did not change: the team's 3Q26 GBV nowcast ($25.9bn) sits below the Street's ($26.4bn), and the kernel says that is worth about $60M on the Q4 guide.

## Finding-by-finding

### A01-01 (critical) — growth-only guidance vs no revenue guidance: accepted
Reproduced: `c01_model.py:52–53` has a single `given` gate at 0.99 and every excluded draw resolves No; the JSON field was `p_no_dollar_guide`; the pre-mortem's item (5) then said a growth-only guide "converts to 3,167 on 2,778", contradicting the gate. The resolution text converts a growth-only range; only "no 4Q26 revenue guidance" resolves No.
Fix (`c01_model_v2.py`): three-way gate — dollar range 0.985 (midpoint on a $5M grid), growth-only range 0.010 (integer-percent endpoints converted on $2,778M, so the midpoint lands on a 0.5pt = $13.9M grid), no revenue guidance 0.005 → No and excluded from the continuous object. The split rests on the guidance ledger: 20 of 20 letters since 4Q21 gave a dollar range; the only two guides without one (2Q21 "significantly higher than Q2 2020", 3Q21 "our strongest quarterly revenue on record") were qualitative, in the first two post-IPO letters. Numerical effect: +0.3 points on the mixture (the converted midpoint has the same distribution on a coarser grid; the gate stress "growth-only 10%" leaves the mixture at 0.732). JSON field renamed `p_no_revenue_guidance` = 0.005, `p_growth_only_guidance` = 0.010; log convention (5) added; pre-mortem (5) rewritten.

### A01-02 (major) — register-gated base rates: accepted
Reproduced by joining the reaction panel's guided period to the L0 register's `pre_guide` revenue rows and applying `pit_usable`: `PG-2024Q3-revenue` (LSEG 3,840, no timestamp, "NEXT-QUARTER CONSENSUS NOT FOUND") and `PG-2021Q4` (no value) drop. Counts: all 7/18 (rev 1: 8/19), LSEG era 5/11 (6/12; mean +0.49%, sd 1.85pp), LSEG/Refinitiv vendor only 7/15, November 3/4, nights-lower 4/8 (5/9), nights-higher 1/4, last four 0/4, May 2024–Aug 2025 run 4/4 (5/5), W1 6/13, W2 4/9. The audit is right that disclosing the flag is not the same as applying it. Base-rate estimate 0.55 → 0.50 (regime-conditioned toward the November and deceleration classes, as before). The register's morning-of-print quotes are now labelled as proxies for C01's previous-close convention (convention (6)). `c01_v2_base_rates.csv` carries the gated counts; claim 3 rewritten.

### A01-03 (major) — the bridge from B2's 0.497: accepted
Reproduced Astra's sequential reruns to four decimals (0.4973 → 0.6864 → 0.7396 → 0.7000 → 0.7480 → 0.8003) and the order dependence (with the residual changes applied first: 0.497 → 0.560 → 0.512 → 0.577 → 0.800). "0.80 on the nowcast alone" was false; withdrawn.
Revision-2 bridge (`c01_v2_bridge.csv`, each step at the same Street threshold, status stated):
| step | P(Yes) | guide mean | sd | status |
|---|---:|---:|---:|---|
| B2 replication, no fee (GBV N(26,550, 853), cushion 1.86, ε N(0, 2.86), 1% no-guide) | 0.497 | 3,161 | 117 | reproduces B2's 0.492 |
| + team GBV (nights N(9.5, 1.8), ADR N(3.3, 1.3)) | 0.684 | 3,109 | 103 | mandated input (brief rule 6) |
| + fee mixture 45/40/15 over 0 / +0.55 / +1.11% | 0.642 | 3,121 | 104 | judgment over B2's half-step-certain; B2's own primitives |
| + three-way gate 0.985 / 0.010 / 0.005 | 0.646 | 3,121 | 104 | resolution rule |
| + ε sd 2.86 → 2.05% | 0.678 | 3,121 | 84 | **validated**: kernel `last3_ex_covid` PIT RMSE, KS p 0.63, survives W1/W2; the three live Q4 cells are ex-COVID |
| + ε mean 0 → −0.19% | 0.701 | 3,115 | 84 | **validated**: same object's PIT bias (forecast above actual) |
| + RNPL leakage branch Bernoulli(0.40) × −0.84% | 0.740 | 3,105 | 84 | **judgment**: K1 central cell (21% share, +4pt); 1H26 shows no leakage; 10-Q language supports the mechanism |
| + cushion 1.86 → 2.4% (Q4-season blend) = component A | 0.798 | 3,088 | 84 | **judgment with a check**: Q4 cushions 3.16/2.69/3.27 (t ≈ 2.8 vs other seasons, n 3); G4's three Q4 cells show the 1.86% model over-predicting the Q4 guide by +0.53% on average |
The revision-1 residual N(−0.5%, 2.0%) is replaced by the validated ex-COVID bias and RMSE plus an explicit leakage branch (realized mean −0.53%, sd 2.09%: numerically almost the same object, but now each part has a source and a label). The audit is right that the K1 grid does not estimate −0.5%; it gives a 0.17–1.39% range for a mechanism that 1H26 has not shown, hence the 0.40 probability. The registered-conventions component C (ε N(0, 2.86), no leakage, cushion 1.86) is kept in the mixture at 0.25 so the un-judged model still carries a quarter of the weight.

### A01-04 (major) — Kalshi liquidity and timestamps: accepted
Reproduced from `sources/kalshi_markets_KXABNB_open_20260917T025304Z.json`: `volume_fp` sums to 3,237.21 contracts (49.9 at 142m to 998.7 at 146m), `volume_24h_fp` 0 at every strike, open interest ≈ 2,178, bid/ask sizes at 148m 3 / 200 contracts and at 150m 1.01 / 200, `last_price_dollars` off the mid at every strike (0.88 vs 0.955 at 138m), `updated_time` identical across all seven markets (2026-08-04T18:47:36.451419Z — a batch metadata stamp, which says nothing about quote freshness either way). Revision 1's "volume field returned None" read a non-existent `volume` key; withdrawn. Added from the `_all_` file: the finalized Q2 2026 ladder (KXABNB-26AUGNEB) traded 2,317–20,671 contracts per strike (≈ 89,500 total), so the Q3 ladder is at about 4% of the prior quarter's terminal volume. Consequence: the market route's weight is cut 0.25 → 0.20 and re-labelled the "market/Street GBV route", because the Bloomberg MODL nights mean (149.0m, n 28) independently centres at the same nights number; the anchor is labelled weak in §5 of the log and in the JSON. Claim 16 rewritten; ledger `kalshi_q3_nights_implied.csv` (rev 1 parse) superseded by `c01_v2_kalshi_ladder_distribution.csv`.

### A01-05 (major) — Kalshi-implied GBV distribution vs the ladder shape: accepted in part
Reproduced: linear interpolation gives median 148.27m and P(>147m) 0.585; the ladder assigns 4.5% at or below 138m and 34% above 150m; N(26,260, 600) at a fixed ADR puts 0.12% below the 138m-equivalent. Accepted that the median-matched normal did not preserve the market's distribution and that its $600M sd was not derived.
Fix: component B now draws nights from the ladder (piecewise-uniform between strikes with the mid-price bucket masses, exponential tails of scale 2.0m below 138m and 3.7m above 150m — the latter chosen so the density is continuous at 150m), then multiplies by ADR ~ N(3.3, 1.3)%: nights mean 148.0m, sd 5.6m, median 148.3m; GBV mean $26,189M, sd $1,041M, P(GBV < $25.0bn) 11.6%, P(> $27.0bn) 19.0%.
In part: the change is immaterial for the binary (component B 0.675 vs 0.683 — the two fat tails roughly cancel) and matters only for the continuous object's width (component B sd $110M vs $85M), which is where it now shows. The `NOT_INDEPENDENTLY_DERIVED` flag stays: the route still shares the kernel, cushion, residual and drift.

### A01-06 (major) — component arithmetic: accepted
Reproduced: components under seeds 1/2/3 are 0.8011 / 0.6826 / 0.6318 → 0.7461; the log's "0.722" was the all-wide sensitivity row (seed 20260917, without component C's cushion-1.86 and ε-unbiased settings), and the displayed 0.60×0.800 + 0.25×0.683 + 0.15×0.722 = 0.759 was never the implemented number. Component C's mean/sd were $3,121M / $109M, not ~3,105 / 105. Revision 2 reports every component as implemented (0.798 / 0.675 / 0.635 → 0.7325) and the slider setup uses the implemented means and sds (3,088/84, 3,112/110, 3,121/109).

### A01-07 (major) — sensitivities at the wrong level: accepted
Reproduced the mixture-level reruns on the revision-1 model: Street +1% 0.8397, −1% 0.6257, full fee 0.6639, no fee 0.7881, trailing-8 cushion throughout 0.6933 (the log had shown 0.885 / 0.68 / 0.72 / 0.84 / 0.74, all component-A numbers, with "moves proportionally" as the rule). Revision 2 runs every sensitivity through all three components (`c01_v2_sensitivity.csv`, columns `mix_*`, with the component-A-alone value beside it) and states the update rule: re-run the script, never scale the headline. The 13 Oct monitoring delta for a certain full fee step is now −0.08 (0/40/60 weights −0.05), not −0.04.

### A01-08 (major) — reviews-index vintage caveat: accepted
Read `WPK_reviews-index-2023-vintage.md` §2.3/§4 and `t1_fail_e5_rerun.csv`: the 0.683 ratio is a W2-scored statistic whose 1Q23–4Q23 training quarters were read from a stale vintage; fresh-vintage variants give 0.757 (RMSE 1.63pp, honest) and 0.841 (1.82pp, literal), both above the 0.75 line. The note leaves the vintage-matched nowcast band unchanged, which is the brief's mandated input, so the centre stays at 9.5; the nights sd is widened 1.6 → 1.8pp to match the honest re-vintaged RMSE, and claim 11 carries the caveat. Effect on the mixture: −0.3 points.

### A01-09 (major) — DoltHub is not the LSEG-family series: accepted
Confirmed from the register's vendor fields and the DoltHub sample (2026Q4 slot 3,200 n 10 = the Zacks panel; yfinance +1q 3,161.02 n 36 = the LSEG family). The weekly monitoring row is split: (a) yfinance `revenue_estimate` +1q avg and n — the resolution series, drives updates; (b) DoltHub — the Zacks-mirror proxy, logged only; "a DoltHub move without an LSEG move is not an update".

### A01-10 (minor) — drift endpoint rule: accepted
Reproduced all 20 observations (mean −0.155%, sd 0.610pp; 2023+ mean +0.013%, sd 0.462pp) and the 2024-08-06 endpoint age of 9 days (others 2–4 days for the November prints). Claim 15 now says "last available observation before the print", gives the endpoint ages, and keeps the vendor/rounding caveat on the 0.6% forward-drift scale.

### A01-11 (minor) — FY floor is a realized-revenue requirement: accepted
Reproduced: 12,241 × 1.15 − 2,678 − 3,608 − 4,800 = $2,991M of required 4Q26 revenue; the guide consistent with it is $2,921M at a 2.4% cushion ($2,937M at 1.86%, $2,903M at 3.04%), and it moves $1 for $1 with the 3Q26 print. Claim 20 rewritten as a soft floor on the guide; "not binding on any plausible guide" and "below every FY26 arithmetic" withdrawn. The revision-2 p5 (2,945) sits above the cushion-consistent floor, and the mass below 2,920 is ~3%.

### A01-12 (minor) — floor check covered only part of the range: accepted in part
Reproduced the revision-1 tail masses (0.806% below 2,900, 0.113% above 3,400) and the $3,427M scenario (GBV 26.3bn, +7% residual, full primitive fee, 1% cushion). Accepted that the "necessary conditions" wording was wrong and that the whole declared range must be audited: revision 2 reports masses below 2,950 (5.1%) and above 3,275 (4.0%), the densities in [2,900, 2,950] and [3,275, 3,400], and the scenario that reaches each bound (joint bear print median 3,015 / p5 2,870; joint bull print median 3,175 / p95 3,335 plus ~+2% residual). The continuous object is labelled conditional on resolvable guidance. In part: the tails stay thin (1.5% / 0.3%) because every route to them stacks two or three 2-sd events; the audit's reproduction "verifies these tail probabilities under the assumptions, not their calibration", and the same is true here — the sensitivity table is the calibration evidence on offer.

### A01-13 (minor) — MODL 3Q26 nights: accepted
`E_street_distribution_vs_team.csv`, 3Q26 / nights_m: street_mean 149.0, low 147.0, high 151.0, n 28. Claim 21 corrected; the 4Q26 revenue row (3,157, low 3,052, high 3,223, n 37) is now also cited to show the MODL and LSEG-family panels share the same low/high and are the same population.

## What the audit missed

1. **The G4 rows contain a small-n check on the Q4 cushion blend.** On the three Q4 targets in `07b_backtest_guide_mid_rows.csv` (2023Q4, 2024Q4, 2025Q4) the trailing-8-cushion kernel over-predicted the guide midpoint by +1.37, −0.40, +0.63% (mean +0.53%) — the size of the blend's premium over 1.86% (0.54pp). The audit called the blend an unvalidated judgment; it is a judgment with a consistent, if tiny, backtest signature. Recorded in claim 6 and §9.
2. **The G4 bias is a COVID artefact on the guide too.** On the six origins whose `last3` cells are all ex-COVID (2025Q1–2026Q2) the model's guide-midpoint bias is +0.24%, against +1.12% on the full W1 — the same pattern kernel-lambda documents on the print. This is the reason the ex-COVID object is the right one for the live cell, which the audit's 3.03% error scale (COVID-inclusive) does not reflect.
3. **Sign agreement is better than the level test.** The audit's "no established historical guide-sign advantage" rests on G4's level wins (7/14, 4/10). Model-below vs realized-below agree 10/14 (W1) and 7/10 (W2), and 4 of the 5 W1 "below" calls were realized below. n is far too small to lean on (and the 2024Q3 cell is the register-excluded vintage), so it is recorded in claim 6 as context, not as evidence for a higher number.
4. **The prior quarter's Kalshi ladder quantifies "thin".** The finalized Q2 2026 ladder settled with ≈ 89,500 contracts against 3,237 on the Q3 ladder today; the audit noted the volume but not the comparison.
5. **The two non-range guides in the ledger.** 2Q21 and 3Q21 were qualitative sentences; they are the only historical "resolves No" cases and pin the no-guidance branch below the Laplace 4.5% the 20-print run alone would give.
6. **The cushion draw interacts with the FY sentence.** The FY floor (A01-11) is not just a wording issue: at a 3.04% cushion the cushion-consistent guide floor is $2,903M, so the bear-print scenario's lower quartile (~2,950) sits close to the FY sentence — a reason the bear tail should be thin that the audit did not use.

## Reconciliation with Astra's 62%

Astra's analytic derivation reproduces (GBV 25,885, guide mean 3,126, sd 102.7, P 0.6244, cushion-subtracted 0.4055) and this model returns 0.626 under the same conventions (team GBV with nights sd 1.6, cushion 1.857, ε N(0, 2.86), half fee certain, 1% no-guide). The 10-point gap to revision 2's 0.72 is: kernel calibration ex-COVID (+0.06, repo-validated), Q4 cushion blend (+0.06, judgment with the check in item 1 above), leakage branch (+0.04, judgment), less the weight the mixture gives Astra's conventions through component C (−0.04). The decision is to hold 0.72: the first item is an asymmetry the repo has already adjudicated (kernel-lambda §(c): "the memo should use the ex-COVID estimation window and say so"), and the two judgments are each carried at half weight. §9 of the log records the two triggers that would take the number into Astra's interval without further judgment (nights band ≥ 10.5; LSEG-family mean ≤ $3,140M).

## Reproduction output

`py -3.13 -B docs/pitch-forecasts/audits/A01-reproduce.py` from the repo root, 2026-09-17 (no edits to the script):

```
Dollar ranges: 20 realized: 19 midpoint beats: 19 top beats: 15
Trailing eight: {'mean': 1.8567430632975808, 'median': 1.7904910308494282, 'std': 1.0047995786447292}
All Q4: {'count': 5.0, 'mean': 3.8509649296892823, 'std': 1.6466358503311773}
        count      mean       std
season
Q1          4  2.479922  1.494675
Q2          4  2.120799  1.109220
Q3          3  1.043306  0.311494
Q4          3  3.041893  0.308258
Cushion trend: -0.1233523470048328 pp/print; p = 0.05484560458114762
Panel as used {'n': 19, 'below': 8, 'rate': 0.42105263157894735, 'laplace': 0.42857142857142855, 'mean': np.float64(1.8357894736842106), 'sd': np.float64(4.411934755472899)}
PIT-eligible all vendors {'n': 18, 'below': 7, 'rate': 0.3888888888888889, 'laplace': 0.4, 'mean': np.float64(2.1404655166230753), 'sd': np.float64(4.329551092439388)}
PIT LSEG-era {'n': 11, 'below': 5, 'rate': 0.45454545454545453, 'laplace': 0.46153846153846156, 'mean': np.float64(0.4923659307997198), 'sd': np.float64(1.8466641238397143)}
PIT LSEG/Refinitiv only {'n': 15, 'below': 7, 'rate': 0.4666666666666667, 'laplace': 0.47058823529411764, 'mean': np.float64(0.9138404848771945), 'sd': np.float64(2.285287421022594)}
PIT November {'n': 4, 'below': 3, 'rate': 0.75, 'laplace': 0.6666666666666666, 'mean': np.float64(-0.34355880734182886), 'sd': np.float64(0.8789421990287452)}
PIT nights lower {'n': 8, 'below': 4, 'rate': 0.5, 'laplace': 0.5, 'mean': np.float64(0.5843128856671376), 'sd': np.float64(1.7811728289798372)}
PIT nights higher {'n': 4, 'below': 1, 'rate': 0.25, 'laplace': 0.3333333333333333, 'mean': np.float64(5.7414876128423185), 'sd': np.float64(7.406637822025355)}
PIT last four {'n': 4, 'below': 0, 'rate': 0.0, 'laplace': 0.16666666666666666, 'mean': np.float64(2.4233366585453), 'sd': np.float64(1.1478244495858294)}
PIT five-print run {'n': 4, 'below': 4, 'rate': 1.0, 'laplace': 0.8333333333333334, 'mean': np.float64(-1.0333274653793023), 'sd': np.float64(0.8424437418342102)}
W1 {'n': 13, 'below': 6, 'rate': 0.46153846153846156, 'laplace': 0.4666666666666667, 'mean': np.float64(0.8957777644109773), 'sd': np.float64(2.3829724143944637)}
W2 {'n': 9, 'below': 4, 'rate': 0.4444444444444444, 'laplace': 0.45454545454545453, 'mean': np.float64(0.4654594612702222), 'sd': np.float64(1.807930329666034)}
Excluded:       register_id period  value as_of_timestamp
PG-2021Q4-revenue 2021Q4    NaN             NaN
PG-2024Q3-revenue 2024Q3 3840.0             NaN
DoltHub All {'count': 20.0, 'mean': -0.15491036338566355, 'median': 0.0, 'std': 0.610396588100871}
DoltHub 2023+ {'count': 15.0, 'mean': 0.013020374969882434, 'median': 0.0, 'std': 0.4615094256727938}
November drift: print_date early_date  late_date  drift_pct  late_age_days
2021-11-04 2021-09-12 2021-10-31  -0.694444              4
2022-11-01 2022-09-11 2022-10-30   0.529101              2
2023-11-01 2023-09-10 2023-10-29   0.462963              3
2024-11-07 2024-09-15 2024-11-03   0.000000              4
2025-11-06 2025-09-14 2025-11-02  -0.373134              4
Stale endpoint: print_date early_date  late_date  drift_pct  late_age_days
2024-08-06 2024-06-16 2024-07-28    0.25974              9
Published G4 W1 n 14 wins 7 MAE 1.9860781645221153 1.9661065926750907 bias 1.1245897089270642 -0.5073937012804309
Published G4 W2 n 10 wins 4 MAE 1.7615821137894163 1.6094084260442643 bias 0.8030258962823378 -0.012946812200268498
Q4 lambdas %: [11.946140035906643, 12.117263843648207, 12.025974025974026] mean 12.02979263517629 range pp 0.17112380774156472
 floor_strike   mid  volume_fp  volume_24h_fp                updated_time
    138000000 0.955     412.02            0.0 2026-08-04T18:47:36.451419Z
    140000000 0.925     409.93            0.0 2026-08-04T18:47:36.451419Z
    142000000 0.880      49.86            0.0 2026-08-04T18:47:36.451419Z
    144000000 0.795     347.64            0.0 2026-08-04T18:47:36.451419Z
    146000000 0.645     998.66            0.0 2026-08-04T18:47:36.451419Z
    148000000 0.525     428.14            0.0 2026-08-04T18:47:36.451419Z
    150000000 0.340     590.96            0.0 2026-08-04T18:47:36.451419Z
Volumes: 3237.21 0.0
Interpolated median nights: 148.27027027027026 P(>147): 0.585
Stated mixture arithmetic: 0.7590499999999999
Saved mixture: {'p_yes': 0.7460941249999999, 'p_surprise': 0.507700375, 'q05': 2960.0, 'q10': 2990.0, 'q25': 3040.0, 'q50': 3100.0, 'q75': 3160.0, 'q90': 3215.0, 'q95': 3250.0, 'mean': 3101.3356, 'sd': 87.44431684014691, 'p_below_2900': 0.0080625, 'p_above_3400': 0.00113, 'p_below_3050': 0.26992, 'p_below_3100': 0.490865, 'p_below_3161': 0.76528, 'p_below_3200': 0.86689}
Auditor GBV, guide mean, SD, P(Yes): 25885.282450439998 3126.1728929301676 102.6769825089756 0.6244102897572612
Percentiles: {5: 2957.284285845846, 10: 2994.587045250394, 25: 3056.918320646801, 50: 3126.1728929301676, 75: 3195.427465213534, 90: 3257.758740609941, 95: 3295.061500014489}
Bounds mass: 0.013805785328961317 0.0038279594379246884
Auditor cushion-subtracted comparison: 0.40553491141575543
```

Separately replayed (not in the script): the revision-1 model's three components under seeds 1/2/3 = 0.8011275 / 0.6826175 / 0.6317550, mixture 0.746094; the sequential bridge 0.4973 → 0.6864 → 0.7396 → 0.7000 → 0.7480 → 0.8003; mixture-level sensitivities 0.83968 / 0.62573 / 0.66388 / 0.78813 / 0.69333. All match the audit.

## Final table

| question | revision-1 number | Astra's number | revision-2 number | anchor | \|final − anchor\| |
|---|---|---|---|---|---|
| C01 binary: P(4Q26 guide midpoint < LSEG-family mean, 4 Nov) | 0.75 (0.62–0.85) | 0.62 (0.50–0.80) | **0.72 (0.60–0.82)** | 0.67 (Kalshi ladder through the kernel, thin; NOT_INDEPENDENTLY_DERIVED) | 0.05 (vs Astra 0.10; vs B2's published 0.49: 0.23) |
| C01 continuous: guide midpoint p5 / p50 / p95, USD m | 2,960 / 3,100 / 3,250 | 2,955 / 3,125 / 3,295 | **2,945 / 3,100 / 3,265** | — | — |
| C01 fine print: guide-surprise P(midpoint < Street × (1 − 0.0186)) | 0.51 | 0.41 | **0.51** | — | — |
| C01 gate: P(no 4Q26 revenue guidance → No) | 0.01 (mis-labelled "no dollar guide") | 0.01 | **0.005** (+0.010 growth-only, resolvable) | — | — |
