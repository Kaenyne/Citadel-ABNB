# Independent research audit — batch A14 (B01, B02, B03)

**B01 — 0.34: the number is defensible; three of its four inputs are superseded and its impact table is wrong.**
The tree reproduces exactly (0.3254, P(Yes ∧ C02 = d) 0.209, P(Yes | d) 0.67) and every one of the 16 letter classifications survives a full re-extraction from `data/raw/letters/*.htm`.
Three corrections (R01 rev-2 print masses, P(word | C02's directional-*moderate* branch) ≈ 0.95 not 0.85, the bucket conditionals shaded to their 0/3 evidence) move it 0.325 → 0.330, so the headline is robust to its own errors.
§9 is not: it measures the delta from 9.90 while its own unconditional is 9.67, double-counts the kernel carry, and prices the stock off S01 revision-1's **withdrawn** −8.6% base case.
Auditor comparison: **0.33** (0.23–0.45), impact ≈ 40% of the published rows, EV **≈ −$1.0/share vs the unconditional, ≈ 0 incremental** — same verdict, different arithmetic.

**B02 — 0.12 (revision 2): coherent with R07 at last, but every component of the lower tail is fitted on 5, 13 or 17 observations and three of them lean the same way.**
The joint model reproduces to 4 dp (P(≤ 2.0) 0.1194, P(≥ 4.4) 0.1723, median 3.398, sd 1.125) and the conditional tables integrate to the headline exactly.
The +0.15 half-bias is justified by a direction split that **cannot be conditioned on at forecast time**; the implementable (ex-ante) split has the opposite sign, and the two readings span B02 0.065–0.158.
The AR(1) branch uses an uncorrected small-sample ρ̂ (0.747; Kendall-corrected 0.979), and the FX mixture puts **0.171** of mass on a disclosed FX ≤ −1.0 against **1 of 17** in the disclosed-FX error record — the two together are worth 3–4 points of lower tail. The "modest/moderate increase" reference class is 7 quarters, not 5, and the two omitted are the two most recent.
Auditor comparison: **0.09** (0.05–0.16), with **R07 ≈ 0.19** from the same object; §9's stock line is **−$8.6**, not −$12 (EV −$1.0).

**B03 — 0.18: not defensible as written; every cross-question input is revision 1.**
C04, C09 and R05 are all at revision 2 on disk (C04 (a) 0.33 / (b) 0.30; C09 (c) **0.47**; R05 **0.22**), and B03 quotes 0.26 / 0.42 / 0.40 / 0.17 — the revision-1 numbers, one of which (R05's S&M ≤ $706M) R05's own RESUME says must not be quoted.
On the live inputs the four-path union is 0.291, not 0.263, and the decomposition leg carries the final up.
The §9 stock line is the only untraceable row in the batch: its own components compute to **+$5.6**, it publishes **−$3** on an unstated "sentiment term", and that flips the materiality verdict.
Auditor comparison: **0.21** (0.12–0.33), EV **≈ $0.8/share, still immaterial** — but immaterial on arithmetic, not on an undocumented judgement.

Audit scope: read-only review of revision 1 of B01 and B03 and **revision 2 of B02** (rebuilt by the A10 response agent as one distribution with R07; I audit that revision, as its header instructs). Also read for coherence: C02, C04, C09, R01, R05, R07, C11, C01 and S01 at the revisions currently on disk, and `data/raw/letters/*.htm` and `data/raw/transcripts/web/*.html` for every verbatim quote. No network fetch was attempted; the Kalshi and Polymarket snapshots were read as saved. Neither prohibited directory was opened. `adr_joint_model_v2.py` and `b01_decomposition.py` write into their own `datasets/` folders, so neither was executed; both were re-implemented from source and reproduce (the Monte Carlo to ±0.002 with `random.Random` in place of numpy).

Below, `log`, `forecast` and `dataset` mean `research-log.md`, `forecasts/2026-09-17-forecast.json` and the named file under the question's folder.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A14-01 | B03 | critical | `log:44` claims 6–8; §5; `forecast.estimates.anchor_source`; `forecast.sensitivity[1,5]` | Every cross-question input is **revision 1**. On disk: C04 rev 2 = (a) 0.33, (b) 0.30, (c) 0.05, (d) 0.27, (e) 0.05 — B03 quotes (a) 0.26, (b) 0.42, (d) 0.24. C09 rev 2 = (a) 0.22, (b) 0.26, **(c) 0.47**, (d) 0.05 — B03 quotes (c) 0.40. R05 rev 2 = **0.22** — B03 quotes 0.17. Path A and Path C, which are 0.17 of the 0.26 decomposition, are both computed off superseded marginals. | Read the three `forecasts/2026-09-17-forecast.json` files (all `"revision": 2`) and C04/C09 §6. R05's RESUME: "Do not quote the revision-1 headline, its 0.19 decomposition, its 'S&M ≤ $706M / +20.7%' thresholds". | Path A = 0.47 × 0.30 = **0.141**; Path C = 0.33 × 0.20 = **0.066**; union **0.291** (verified). Anchor on rev-2 = 0.5 × 0.33 + 0.25 × 0.30 = **0.240** (barely moved, because (a) up offsets (b) down). Final moves 0.18 → **0.20–0.21**. Also restate §7 row 6 ("R05 Yes") at 0.22. |
| A14-02 | B01 | critical | `log:129–138`; `dataset:b01_decomposition.py:76–87`; `forecast.impact` | The impact table measures the conditional delta from **9.90** (the team model path) while the tree's own unconditional mean is **9.67**, so every revenue/margin/EPS row is ~60% too large; and the 4Q26 revenue line adds a kernel carry on the *same* 3Q26 GBV shortfall (−$11M) that the FY26 margin line already counts as 3Q26 revenue (−$28M) — the double count A10-24 removed from R07/B02 and left here. | Re-implemented the truncated-normal posterior: E[nights \| Yes] 9.31, unconditional 9.67, consistent delta **−0.36**, published −0.59. On the run's adopted N(9.5, 1.70) (R01 rev 2) the same tree gives E[·\|Yes] 9.14 vs 9.49, delta −0.35. | On the adopted distribution and with the kernel term dropped: 3Q26 revenue −$17M, **4Q26 revenue −$6M** (not −22), **FY27 revenue −$22M** (not −38), **FY26 margin −0.10pp** (not −0.2), **FY27 margin −0.09pp** (not −0.15), **FY27 EPS −$0.02** (not −0.04). The "immaterial / language marker only" verdict is unchanged. |
| A14-03 | B01 | critical | `log:46` claim 14, `log:137`; `forecast.impact.note` | The stock row and the "≈ 0 incremental to the base case" verdict are priced against **S01 revision 1's base-case median −8.6% and P(≤ −8) 0.53**, which S01 revision 2 explicitly withdraws ("Revision 1 quoted median −8.6 and P(< 0) 0.87 for this case; both were the model branch alone with a stale two-gate mask and are withdrawn"). Claim 8 likewise carries R01's revision-1 headline 0.42 and its N(9.67, 1.70), which R01 rev 2 supersedes with **0.39** and **N(9.5, 1.70)** (`adopted_print_states_v2.json`). | Read `day1-move-5nov/research-log.md` §6 and `forecasts/…json` (rev 2: unconditional median **−2.1**, base case median **−5.1**, P(≤ −8) **0.374**) and `risk-q3-nights-meets-guide/research-log.md` claims 16, 20 and §10. | Re-price on rev 2: strict-class **median** −3.95 vs the unconditional median −2.1 = −1.85pt = **−$3.1/share**; vs the base case (−5.1) the increment is **+$1.9**, i.e. still ≈ 0 and if anything positive. EV ≈ **−$1.0/share** vs the unconditional. Update the branch masses to 0.384 / 0.231 / 0.384 (worth +0.007 on the headline). |
| A14-04 | B02 | major | `log:39` claim 5; `log:82` §4 row 6; `adr_joint_model_v2.py:24`; `forecast.model.structure` | The +0.15 half-bias on the centre is justified by "the bias is real in accelerations and absent in decelerations" — a split on the **realised** direction, which is not available at forecast time. Split on the direction the model itself predicts (the only implementable version) the sign reverses: predicted-decel quarters have mean error **−0.579** (model low), predicted-accel **−0.036**. 3Q26 is a predicted-decel quarter by 96.6% of the model's own mass (P(reported ≥ 2Q26's +5.30) = 0.034). | Reproduced both splits from `P1_card_v3_backtest_paths.csv` (midpoint, `t2_reported_usd_yoy`) against the prior-year actual in `adr_history_components.csv`. Ex-post decel n 5 mean +0.070 (RMSE 0.894, **SE 0.446**), accel −0.685; ex-ante decel n 5 mean −0.579, accel −0.036. Pooled −0.308. | Neither split is distinguishable from the pooled bias at n 5 (the pooled value sits inside ±1 SE of the decel mean). Stop conditioning: apply the pooled bias with a stated span. The span is the honest disclosure — bias −0.07 → B02 **0.158** / R07 0.124; +0.15 → 0.119 / 0.172; +0.31 → 0.095 / 0.215; +0.58 → 0.065 / 0.297. Delete the sentence in claim 5 that says the split justifies halving. |
| A14-05 | B02 | major | `log:38` claim 3; `adr_joint_model_v2.py:26–31`; `forecast.model.structure` (AR(1) N(4.37, 0.94), weight 0.25) | The AR(1) branch — 0.25 of the residual mass and the single largest contributor to the lower tail after the FX branch — is fitted by OLS on 13 pairs with no small-sample correction. OLS ρ̂ in a short AR(1) with an intercept is biased down by roughly (1 + 3ρ)/T; the mean reversion the branch supplies is largely that artefact. | Reproduced the fit (const 0.750, ρ 0.747, innovation sd 0.939, point 4.374, matching the log). Kendall–Marriott–Pope correction at T = 14: ρ 0.747 → **0.979**, 3Q26 point 4.374 → **4.809** (essentially the persistence branch). Re-ran the mixture with the corrected branch: **P(≤ 2.0) 0.1002, P(≥ 4.4) 0.1963**. | Either bias-correct ρ, or halve the AR(1) branch's weight and say in the log that the branch is an uncorrected small-sample fit. Either way B02's own model reads ≈ **0.10**, not 0.12, and R07 reads 0.20. The log's "kept because they are fitted rather than assumed" (§5) is the claim that does not survive: a 13-pair AR(1) is not more evidence than an assumption, it is an assumption with a standard error. |
| A14-06 | B02 | major | `log:40` claim 4; `dataset:b02_modest_increase_record.csv`; `forecast.estimates.anchor_source` | The "modest/moderate increase in ADR" reference class is **7 guides, not 5**. The record omits the 4Q25 letter ("a moderate increase in ADR due to price appreciation and FX" → 1Q26 printed **+9.03%**) and the 1Q26 letter ("a moderate increase in ADR" → 2Q26 printed **+5.30%**). Both omitted cases use the *exact wording of the live 3Q26 sentence* ("a moderate increase in ADR"), while the three low prints all used "modestly up"/"increase modestly". | Extracted every forward ADR guide sentence from `data/raw/letters/*.htm` 1Q24–2Q26 (see the reproduction script). The five in the record verify; the two omitted verify verbatim in the 4Q25 and 1Q26 letters. | Restate as **2 of 7** (0.29), and add the wording split: "moderate/modest increase in ADR" (3Q25, 4Q25, 1Q26 letters) → +5.9, +9.0, +5.3, never ≤ 2.0; "increase modestly" (1Q24, 2Q24, 3Q24) → +2.1, +1.4, +0.9. The correction cuts against a Yes and makes the 0.12 base-rate leg look, if anything, generous. |
| A14-07 | B02 (and R07) | major | `log:135` §9 stock row; `forecast.impact.stock_usd_per_share` | The stock line applies "0.40–0.48 EV/EBITDA turns **per point of forward revenue growth**" to a **level** shift. A −1.9% permanent ADR level change lowers FY26 by half a year of it and FY27 by a full year, so the FY27 growth rate falls by **1.00pt**, not 1.9. The multiple term is therefore double the truth. | `23_vs_consensus.csv`: FY26 $14,268.1M, FY27 $15,828.6M, baseline growth 10.94%. With 2H26 −$145M and FY27 −$302M: 9.94%, **−1.00pt**. Mirror for R07 (+$125M / +$260M): 11.78%, **+0.84pt**. | B02: multiple $4.18 + level $8.17 = $12.34, ×0.70 = **−$8.6/share**, EV 0.12 × 8.6 = **−$1.04** (borderline material, not comfortably so). R07: $3.52 + $7.03 = $10.55, ×0.70 = **+$7.4**, EV **+$1.26**. The two-tails-of-one-distribution presentation survives; the dollar figures shrink by 28%. |
| A14-08 | B03 | major | `log:129` §9 stock row; `forecast.impact.stock_usd_per_share` | The only untraceable row in the batch. Its own components are +$6.9 (EPS +$0.27 at 27×) and −$1.3 (growth), i.e. **+$5.6**; it publishes **−$3** via an unnamed "sentiment term". The 27× P/E is also inconsistent with the 16× EV/EBITDA the rest of the run uses (which gives +$4.84/share on +$179M of EBITDA at 591.7m shares). Brief rule 8 requires each line sourced to a repo sensitivity or a shown computation. | Recomputed both routes; EPS recomputes to **+$0.254** (+$0.297 marketing − $0.046 revenue), not +0.27. | Publish the mechanical value (**+$3.5 to +$5.6**) and, if the log wants a behavioural discount, name it and size it. At +$4 the EV is 0.21 × 4 = **+$0.8/share — still immaterial**, which is the same verdict reached honestly. As published the sign of the memo's bonus line is set by an undocumented term. |
| A14-09 | B03 | major | `log:31` convention (4); `log:85` §5 base rate | Convention (4) reads two of the resolution's four enumerated triggers out of the question. The resolution says Yes if management states spend "will grow more slowly than revenue, **be 'moderated', 'optimised' or reduced**, or quantify a reduction". Convention (4) makes "optimised" applied to a growing budget a No. The base rate then measures only the narrow event ("slower than revenue or reduced"), so the 4/23, 1/18, 0/10 counts are not the question's own reference class. | Scanned every letter and call for `optimi|moderat|discipl|leverage|efficien` co-occurring with marketing. The literal trigger appears in the letters at 2Q23, 3Q23, 4Q23, 1Q24, 3Q24 ("as we optimize the channel and audience mix") — **5 of 23 prints**, though **0 of the last 8** — and 1Q26's forward "efficient marketing spend" is the live analogue. | Keep the convention (it is stated, and the phrase has not appeared since 3Q24), but (a) raise the resolver-risk path from 0.04, and (b) report the literal-reading base rate (5/23, 0/8 recent) beside the narrow one, so a judge can see which question is being answered. The strict/loose span 0.15/0.45 is the largest single lever in the log and deserves more than one line in §6. |
| A14-10 | B01 | major | `log:85` §5 base_rate_estimate; `forecast.estimates.independence_note` | The "independent leg" is not one. Its stated construction is "regime-conditioned **between** the bucket-era rate and the W2 rate" — 0.25 to 0.30 — and it then publishes **0.35**, above both, shaded upward by the print-state argument that *is* the decomposition. So all three legs share the same mechanism and the log's "the base rate is the one independent leg" is false; the "three legs agree within 4 points" claim in §5 is circular. | Recounted from the dataset: 6/16 = 0.375, W1 5/14 = 0.357, W2 3/10 = 0.300, November 2/4 = 0.500, bucket era **0/3** (the log says 1/4; 1Q26 is not a bucket letter — its descriptor is "slightly decelerate"). | Publish two base rates: the unconditional letter rate (W1 0.36 / W2 0.30, both windows as the repo convention requires) and the **conditional** rate P(word \| down-class descriptor) = 6/8 = 0.75 with P(word \| non-down) = 0/8, which is the leg that is genuinely independent of C02's tree. The conditional route gives 0.40 × 0.75 + 0.60 × 0.06 = **0.336** — the same answer, honestly derived. |
| A14-11 | B02 | major | `log:42` claim 6; `adr_joint_model_v2.py:34` (`W_FX = (0.50, 0.25, 0.25)`); `forecast.sensitivity[3]` | The FX mixture's left branch is not supported by the estimator's own error record. It puts **0.171** of mass on a disclosed FX effect ≤ −1.0 (the euro fit being right); in 17 quarters of disclosed FX the midpoint estimator's signed error reached the required +0.69pp **once** (2Q23). The structural premise — that a wide euro/baskets spread means the disclosed value may sit at either estimator — is contradicted by the record: the correlation between the spread and the midpoint's absolute error is **−0.39**, i.e. the midpoint has been *more* accurate when the two estimators disagreed most (2Q26: spread 1.11, error 0.159). This branch is the single largest contributor to the lower tail (FX-all-euro 0.253 vs FX-all-baskets 0.031). | Computed from `N1_fx_estimator_by_quarter.csv` (17 quarters, `err_est_from_midpoint` = estimate − disclosed): \|err\| ≥ 0.69 in 1 of 17 (0.059; Laplace 2/19 = 0.105); \|err\| ≥ half that quarter's spread in 10 of 17, signed ≥ +half-spread in 7 of 17 — so the disclosed value often lands outside the interval, but by an amount that does not scale with the spread. Mean \|err\| 0.337, max 1.000; mean spread 0.471, max 1.110 (3Q26's 1.38 is outside the historical range). | Re-weight toward the empirical rate, e.g. 0.76 / 0.12 / 0.12 → **B02 0.107, R07 0.153**, or state explicitly that the branch weights are a judgement about estimator choice rather than a fitted error distribution, and report the empirical bound (0.06–0.11) beside the model's 0.171. The conditional table on the disclosed FX effect (0.32 / 0.11 / 0.03) is unaffected and should be kept — it is the log's best output. |
| A14-12 | B02 | major | `log:43` claim 7; `adr_joint_model_v2.py:32` (MIX_SD 0.35) | The mix term's sd (0.35) is tighter than the log's own account of the mix term's uncertainty: claim 7 says the geographic drag's band is −1.57 to −0.94 (±0.32 on that term alone) on "an unvalidated mapping (RMSE 0.4–0.7pp on n 10)", and party size and LOS add their own error on top. A single sd of 0.35 for the whole mix line cannot be right if one of its three components has a 0.4–0.7pp mapping RMSE. | Re-ran the mixture at mix sd 0.60: **P(≤ 2.0) 0.1370, P(≥ 4.4) 0.1947** (the log's own sensitivity row, confirmed). | Set mix sd to 0.50–0.60 and say why. It fattens both tails, which is the right direction for an un-walk-forward-validated component, and it partly offsets A14-05. |
| A14-13 | B01 | major | `dataset:b01_decomposition.py:26–31` (`dir_mod=0.85`); `log:86` | `dir_mod` is the probability the language appears **given that C02's tree has already routed the letter to a directional "moderate/decelerate" sentence**. On C02's own definition that branch *is* the word ("P('moderate' \| directional) 0.55 / 0.60 / 0.75, the remainder 'stable/higher'"), so P(Yes \| that branch) ≈ 1. The 0.85 is justified by "less the 'lower than'/'a few points below' forms", but those forms are neither "moderate" nor "stable/higher" and are not in C02's tree at all — the haircut is applied twice. | Read C02 rev 2 §5 and `decomposition_v2.py`'s parameterisation; re-ran the tree at 0.95 → **P(Yes) 0.3442**, P(Yes \| d) 0.73, P(Yes ∧ d) 0.228. | Raise `dir_mod` to 0.95 (or state that C02's directional branch admits non-"moderate" down wordings, and fix C02 instead). The correction is +2 points and is offset by A14-14's bucket shading, which is why the headline survives. |
| A14-14 | B01 | minor | `dataset:b01_decomposition.py:31` (`bucket_c=0.25`, `bucket_d=0.40`); `log:76` | The two least-evidenced parameters in the log carry 0.07 of the 0.325 with **0 of 3** bucket-era observations behind them, and the log says so in §4 and then does not shade them. Both bucket letters that exist (3Q25 "challenging Q4 2024 comparison", 4Q25 "moderate increase in ADR" — excluded as ADR) used comp language, not softening words. | Re-ran at 0.20 / 0.35: **P(Yes) 0.3047**. At 0.10 / 0.20 (bucket-era literalism): 0.258. | Shade to 0.20 / 0.35 (Laplace-ish on 0/3 with an allowance for a decelerating narrative) and widen the §7 row. Combined with A14-13 and A14-03's masses the headline lands at **0.330**. |
| A14-15 | B02 | minor | `log:38` claim 3; `forecast.model.history.with_residual_ge_3.5` | "0 of 4 with a residual ≥ 3.5" contradicts its own parenthesis in the same sentence. Strictly there are **3** such quarters (4Q25 3.699, 1Q26 4.381, 2Q26 4.849) and none printed ≤ 2.0; if 1Q23 (residual 3.4766) is rounded in — as the parenthesis does — the class is **1 of 4**, because 1Q23 printed **+0.21**. As written the reference class is stated in the direction that supports the lower number. | Recounted from `adr_history_components.csv`: `residual ≥ 3.5` → n 3, 0 at ≤ 2.0; `residual ≥ 3.45` → n 4, **1** at ≤ 2.0. | State it as "0 of 3 strictly, 1 of 4 if 1Q23's 3.48 is included — and that one case needed FX at −2.8". Laplace on the inclusive class is 2/6 = 0.33, which is a materially different prior from the 1/6 the log quotes. |
| A14-16 | B02 | minor | `log:38` claim 3; `forecast.model.history.with_fx_ge_-0.5` | "0 of **7** with FX ≥ −0.5" — there are **8** (3Q23, 4Q23, 1Q24, 2Q25, 3Q25, 4Q25, 1Q26, 2Q26). The count appears in the machine-readable history block. | Recounted: `(fx_effect_pp >= -0.5).sum()` = 8; of those, 0 at ≤ 2.0. | Correct to 0 of 8 (Laplace 1/10 = 0.10 rather than 1/9 = 0.11). It strengthens the log's own case by a hair; it should still be right. |
| A14-17 | B01 | minor | `log:95`, `log:138`; `forecast.companion.p_yes_and_c02_d` | The overlap is reported as "0.21 of its 0.34", but 0.209 is a share of the **tree's** 0.3254; the JSON's 0.21 + 0.12 = 0.33 ≠ the published 0.34, and the figure X01 actually needs is the **fraction** — 0.64 of the Yes mass, not 0.21 of 1.0. | Recomputed: P(Yes ∧ C02=d) 0.2090, P(Yes) 0.3254, ratio 0.642; P(Yes \| d) 0.676 ≤ P(d) = 0.312 ✓, so the pair is coherent with C02 rev 2's (d) = 0.31. | Publish the pair scaled to the headline (0.219 / 0.121) or publish the fraction (0.64). The coherence conclusion — B01 is mostly C02's (d) and must not be added to the base case — is correct and should be kept verbatim. |
| A14-18 | B01 | minor | `log:34` claim 2; `log:138` §9 note | §9 sells the item on "4 of 8 such prints fell ≥ 8% day 1", which is the **synonym** class, while the headline 0.34 sits nearer the strict reading (0.30) than the loose one (0.40). On the strict class the numbers are: mean −5.4, **median −3.95**, P(≤ −8) **2 of 6**. The strict class's own record is much weaker than the memo line implies, and two of the brief's four "8–13% declines" (1Q23, 2Q25) are **not** strict-word prints. | Recomputed from the dataset and `abnb_earnings_reactions.csv`: all 16 day-1 excess values match the panel exactly. Strict n 6: −10.0, −5.1, −2.8, −12.3, −0.5, −1.6. | Quote the strict class with the headline probability (median −3.95, 2 of 6 at ≤ −8), and the synonym class only alongside the 0.40 reading. A judge who opens the panel will find that the two worst of the four named declines carried no listed word. |
| A14-19 | B03 | minor | `log:120` §8 row 4; `forecast.monitoring[3]` | The 5 Nov read rule ("S&M print ≤ $710M means the Q3 step never came") is calibrated on R05 revision 1's withdrawn $706M / +20.7% threshold. On the corrected identity the line is **$724M (+23.7%)**, so a $710M print would *clear* the 51.5% bar — the rule would score the opposite of what it intends. | R05 rev 2 claim 7 and §10: "cash costs ≤ $2,351M, S&M ≤ $724M = +23.7% y/y at $4,804M (was $2,330M / $706M / +20.7%)". | Restate the monitoring rule on $724M, and re-read §4 row 7 and §7 row 6 (R05 Yes → B03 0.10), which are both built on the killed arithmetic. |
| A14-20 | B03 | minor | `log:132` §9 FY27 margin row; `forecast.impact.eps_fy27_usd` | "+1.34pp" is a **2× linear extrapolation** of `40_sensitivities.csv`'s +5pt step (−0.67pp), presented as if sourced. FY27 EPS recomputes to **+$0.254**, not +$0.27. | +1.34pp on $15,828.6M = +$212M EBITDA × $0.0014 = +$0.297; less the revenue line (−$50M × 0.66 × 0.0014 = −$0.046) = +$0.251. | Label the extrapolation, and correct EPS to +$0.25. |
| A14-21 | B03 | minor | `dataset:b03_marketing_statement_by_print.csv` row 4Q20 | The 4Q20 row is presented in single quotes as if verbatim: the letter says "**sales and marketing expenses** as a percentage of revenue in the first half of 2021 will be higher than that of the second half". The companion quote "'S&M … in 2021 will be below that of 2019'" **does not appear in the 4Q20 letter at all** — I could not locate it in the letter text, and it is load-bearing (it is what makes 4Q20 a Yes rather than a seasonal-only statement excluded by the log's own convention 5). | Extracted the 4Q20 letter in full and searched for "2019", "below", "S&M as a percentage". The 1H>2H sentence verifies; the "below 2019" sentence does not. Every other quotation in the ledger verifies word-for-word (18 of 19 checked; see the script). | Source the 2019 sentence (it may be in the 4Q20 call, which the row also cites) or drop it and re-check whether 4Q20 still scores Yes under convention 5. 3 of the 4 historical Yeses are the same 2021 sentence repeated, so the class is effectively **2 distinct events in 23 prints** — say so. |
| A14-22 | B02 | minor | `log:42` claim 9 | "with one, at most two, of 26 estimates at or below it" is not in the cited file, which carries only `street_low`, `street_mean`, `street_high` and `n_estimates`. It is an inference from a three-point summary presented as an observation. | `E_street_distribution_vs_team.csv` 3Q26 `adr_usd`: n 26, low 173.71, mean 177.06, high 179.12 — no distribution. The 18.7%-of-range figure reproduces exactly. | Keep the range position (verified); delete or explicitly label the estimate count. |
| A14-23 | B01 | minor | `log:28` conventions; `forecast.companion` | B01 carries **no resolver-risk path**, while its companion B03 carries one at 0.04 for exactly the same hazard. The nearest live case is the 4Q25 prepared remarks' "Travel is influenced by everything from currency to **macroeconomic conditions** to global events", which conventions 1–5 do not address and which a resolver applying "macro uncertainty affecting bookings" loosely would argue over. | Scanned the 3Q24, 3Q25, 4Q25, 1Q26 and 2Q26 prepared remarks; claim 6 otherwise holds exactly (no forward softening phrase in 3Q24, 3Q25, 4Q25 or 2Q26). | Add a convention for general "macro conditions" framing sentences and a small resolver path, or state in §6 that the 0.30/0.40 strict/loose span is meant to carry it. |
| A14-24 | B03 | minor | `log:36` claim 3 | "eight consecutive quarters of S&M growing faster than revenue" is **nine** (2Q24 through 2Q26). The understatement is in the direction that weakens the log's own strongest No argument. | Recomputed y/y from `abnb_quarterly_costlines.csv` 3Q23–2Q26: slower in 3Q23 (+4.9 vs +17.8), 4Q23, 1Q24; faster in every quarter from 2Q24. All four S&M/revenue pairs in `b03_sm_history.csv` verify exactly. | Correct to nine, and note the 2023 counter-example (3Q23 S&M +4.9% against revenue +17.8%) explicitly — it is the one precedent for the event and it followed exactly the 1Q23 statement the ledger scores Yes. |
| A14-25 | B01 | minor | `log:139` RESUME | The RESUME directs the next agent to `data/raw/transcripts/ir/` "if present, which have exact prepared/Q&A tags". That directory does not exist; `data/raw/transcripts/` contains only `web/`. | `ls data/raw/transcripts/` → `web`. | Drop the instruction or name the real artefact. The prepared/Q&A split in claim 6 was done by hand from the web mirrors and should be shipped as a dataset if it is load-bearing (it is: it carries the entire prepared-remarks channel). |

## B01 — what the log does well and should keep

The letter classification is the best artefact in the batch and should survive intact. I re-extracted all 16 letters and checked 30 quoted fragments: **29 of 30 verify word-for-word** (the one miss, 1Q24's "relatively stable **to that of** Q1 2024", is a dropped preposition in a descriptor field). More importantly, the *negative* classifications hold under an independent scan: 2Q23's "deceleration in Nights and Experiences Booked relative to Q1 2023" is the reported quarter (correctly excluded by convention 2); 3Q24's "softer start due to shorter booking lead times" is backward-looking and the same letter says lead times "normalized" and Q4 demand is "strong" (correctly excluded); 4Q22's "despite evolving macroeconomic uncertainties" is a foil for strength (convention 5, correctly excluded); the recurring "moderate increase in ADR" is correctly excluded and would otherwise make the question trivial. The six conventions are the right way to handle a language question and only convention 5's silence on general "macro conditions" framing needs a word (A14-23).

Claim 2 is exact: all 16 day-1 excess values match `abnb_earnings_reactions.csv` to the decimal, and the four conditional means (−5.38 strict, −6.59 synonym, +1.16 and +4.00 without) reproduce. Claim 5 is exact against `03_call_features.csv` (2025Q4 8, 2026Q1 12, 2026Q2 4 prepared demand/macro sentences; prepared share 9.60% in 1Q26, 2.86% in 2Q26). Claim 6 survives a full independent scan of the 3Q24 / 3Q25 / 4Q25 / 2Q26 prepared remarks. Claim 9's Communacopia rows verify in `intra_quarter_commentary.csv`.

The structural insight — that this question is mostly C02's option (d) wearing a different hat, and that the memo must therefore quote it as the *language marker* of the base case rather than add its EV — is correct, is the thing X01 most needs, and is exactly the coupling these runs usually miss. Keep it; just publish the fraction (A14-17).

## B02 — what the log does well and should keep

Revision 2 is a genuine repair of A10-03 and should not be walked back: one distribution, both tails read off it, no lift on either. It reproduces to four decimal places (P(≤ 2.0) 0.1194, P(≥ 4.4) 0.1723, median 3.398, mean 3.349, sd 1.125) and every conditional integrates correctly (0.171 × 0.318 + 0.486 × 0.111 + 0.344 × 0.031 = 0.1187).

The *conditional table on the disclosed FX effect* (0.32 / 0.11 / 0.03 across FX ≤ −1.0, (−1.0, −0.2), ≥ −0.2, with masses 0.171 / 0.486 / 0.344) is the single most useful output in the batch, and so is its sibling on the ex-FX letter integer. They turn 5 Nov into a scorable test rather than a pass/fail, they integrate exactly to the headline, and the monitoring row that reads the pre-print P off them is the right way to make a forecast auditable on the night. Keep them even after re-weighting the branches (A14-11): the conditional probabilities are what the model gets right; only the weights attached to them are a judgement.

The identification of the FX estimator choice as "the largest controllable uncertainty on the ADR line" is correct and well documented, and the observation behind it verifies: 3Q26's euro–baskets spread, **1.38pp, is wider than any of the 17 historical quarters** (previous maximum 1.11 at 2Q26), and the disclosed value has landed outside the euro–baskets interval in **10 of 17** quarters. The log is right that this is the thing to watch; it is the size of the tail it hangs on it that does not follow (A14-11).

The MODL anchor is exact (n 26, low $173.71 / +1.413%, mean $177.06 / +3.369%, high $179.12 / +4.571%; range/4 = 0.789 → 0.0415; at the card's RMSE 0.927 → 0.0699; threshold at 18.7% of the range). The AR(1) fit, residual series, one-quarter-change statistics (max fall −1.467, sd 0.935 on n 13) and direction-split error table all reproduce to three decimals. The §9 recognition convention (implied take rate in both quarters, kernel-lag term **not** added) is the right fix to A10-24 and is applied consistently; the FY26 −0.6pp, FY27 −1.3pp and EPS −$0.42 rows all reconcile to `23_vs_consensus.csv` under held costs. Only the stock line's growth-vs-level conflation (A14-07) is wrong.

## B03 — what the log does well and should keep

The statement ledger is honest and, apart from the 4Q20 row (A14-21), verifies: I checked 19 quotations against the raw letters and calls and **17 verify verbatim**, including every load-bearing No (2Q24 and 1Q25 "Marketing expense is expected to grow faster than revenue"; 3Q24 "Q4 2024 Adjusted EBITDA Margin is expected to decline … due to higher marketing and product development expenses"; 4Q24 "not to grow the core market marketing spend faster than revenue"; 4Q25 "reinvest top-line efficiencies"; 1Q26 "efficient marketing spend"; 2Q26 "partially offset by continued investment in sales and marketing") and the two borderlines (3Q22 "you should anticipate similar marketing as a percentage of revenue in 2023"; 4Q23 "we probably could see additional leverage on marketing"). My own independent scan of every letter and transcript for `optimi|moderat|discipl|leverage|efficien` near "marketing" found **no forward slower-than-revenue statement the ledger missed** in 1Q24–2Q26.

The S&M history is exact against `abnb_quarterly_costlines.csv` (3Q25 $639M / 15.6% / +24.3% vs revenue +9.7%; 4Q25 $695M / 25.0% / +27.1% vs +12.0%; 1Q26 $751M / 28.0% / +33.4% vs +17.9%; 2Q26 $875M / 24.3% / +26.6% vs +16.5%). The call-feature reading is exact (2Q26 marketing theme share 0.40% total, 1.43% prepared, 0.00% Q&A — a record low; 1Q26 1.58%, 4Q25 0.78%), and "the topic has almost left the call" is a fair and useful characterisation.

The four-path decomposition is the right structure, the conventions are well drawn (convention 3's treatment of "timing of investments" is exactly the distinction a resolver will need on the night), and the framing of the item — a **tell** that the FY26 floor is being defended with the growth budget, not a stock line — is the correct memo use and should lead the bullet. It just has to be rebuilt on revision-2 inputs.

## Independent numbers

**B01 — P(Yes) = 0.33**, judgmental 80% interval 0.23–0.45.
Derivation: the same C02 tree with three repairs — R01 revision 2's adopted print masses (0.384 / 0.231 / 0.384 from N(9.5, 1.70)), P(word \| C02's directional-*moderate* branch) 0.95 rather than 0.85 (that branch is defined as the word), and the bucket conditionals shaded to their 0/3 bucket-era evidence (0.20 high-single, 0.35 mid-single) — gives **0.3300**, with P(Yes \| C02 = d) 0.71 and P(Yes ∧ C02 = d) 0.229. Independent cross-check that does not touch C02's tree: P(word \| down-class descriptor) 6/8 × P(down-class) ≈ 0.40, plus P(non-down) 0.60 × 0.06 = **0.336**.
Both routes land at 0.33; the interval is wide because the whole question is the format coin-flip C02 itself prices at (c) 0.30 vs (d) 0.31. Impact on the corrected baseline: 3Q26 nights **−0.35pt**, 4Q26 revenue **−$6M**, FY27 revenue **−$22M**, FY26 margin **−0.10pp**, FY27 margin **−0.09pp**, FY27 EPS **−$0.02**, stock **−$3.1 vs the S01 rev-2 unconditional** (median −3.95 vs −2.1) and **+$1.9 vs the rev-2 base case**. EV ≈ **−$1.0/share vs the unconditional, ≈ 0 incremental — not a separate memo line**, which is the log's own verdict reached on arithmetic that holds.

**B02 — P(Yes) = 0.09**, judgmental 80% interval 0.05–0.16; **R07 = 0.19 from the same object.**
Derivation: one distribution, 0.55 weight on the structural mixture with three repairs — AR(1) branch at a small-sample-corrected 4.60 (A14-05), mix sd 0.50 (A14-12), FX weights part-way to the empirical rate at 0.63 / 0.185 / 0.185 (A14-11) — which gives **0.112 / 0.188**; and 0.45 on the only walk-forward-validated object in the chain, N(3.50, 1.00): the card's with-K point plus half the pooled bias at its measured RMSE 0.927, widened a little for the FX spread → **0.067 / 0.184**. Blend: 0.55 × 0.112 + 0.45 × 0.067 = **0.092 → 0.09**; R07 = 0.55 × 0.188 + 0.45 × 0.184 = **0.186 → 0.19**.
The gap to the published 0.12 is A14-05 and A14-11 (−2 and −1 points) net of A14-12 (+2) and the weight given to the structural mixture over the validated Gaussian; the gap to Astra's 0.08 is that some left skew is real — a pricing turn is a regime, not Gaussian noise. Two independent auditors now land at 0.08 and 0.09 against a published 0.12, and both land at 0.19 on R07, so the *pair's asymmetry* is agreed even where the level is not. Impact on the corrected growth arithmetic: stock **−$8.6**, EV at my P **−$0.8/share — immaterial**, at the log's 0.12 **−$1.04 — borderline**; R07 **+$7.4**, EV **+$1.4**. Keep the two-tails presentation; shrink the dollars 28%.

**B03 — P(Yes) = 0.21**, judgmental 80% interval 0.12–0.33.
Derivation: the four paths on revision-2 inputs — A = C09 rev 2 (c) 0.47 × 0.27 (marketing named as the slower line, shaded a little below the log's 0.30 for the 2026 no-line-names habit) = 0.127; B = 0.09 (a 2027 leverage answer in Q&A; analysts asked about marketing leverage at 4Q21, 4Q23, 4Q24 and twice at 1Q25, so the conditional is on the answer, not the question); C = C04 rev 2 (a) 0.33 × 0.20 = 0.066; D = 0.07 resolver risk (the resolution lists "optimised"/"moderated" as triggers that convention 4 reads out) — union **0.310**, less ~0.03 for the shared floor-at-risk state = **0.28**.
Blend 0.45 × 0.28 + 0.35 × the base rate 0.09 (0 of 10 since 1Q24, 0 of 5 Novembers, nine straight quarters of S&M outgrowing revenue, a 2027 launch narrative) + 0.20 × the anchor 0.24 = **0.206 → 0.21**. Impact: keep FY26 **+1.2pp** and FY27 **+1.1pp** (both trace), correct FY27 EPS to **+$0.25**, and publish the stock line as the **+$3.5 to +$5.6** its own components compute to, with any behavioural discount named. EV ≈ **$0.8/share — immaterial as a stock line**, material as the tell.

## Reproduction script

Run from the repository root with `py -3.13 -B docs/pitch-forecasts/audits/A14-reproduce.py`. Standard library plus pandas; it writes nothing and executes neither forecaster's model file (both write into their own `datasets/` folders). The Monte Carlo is re-implemented with `random.Random` in place of numpy and reproduces the seeded figures to about ±0.002.

```python
"""A14 audit reproduction - B01, B02, B03. stdlib + pandas only; writes nothing."""
from pathlib import Path
from statistics import NormalDist, mean, pstdev
import csv, glob, html, json, math, os, random, re
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
nd = NormalDist()
N = 300_000


def hdr(s):
    print("\n" + "=" * 8 + " " + s + " " + "=" * 8)


def text(p):
    s = Path(p).read_text(encoding="utf-8", errors="ignore")
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    for a, b in [("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), ("\xa0", " ")]:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s)


# ------------------------------------------------------------------ B01
hdr("B01  letter base rates and the day-1 classes")
recs = list(csv.DictReader(open(Q / "bonus-moderation-language/datasets/"
                                "b01_letter_language_by_print.csv", encoding="utf-8")))
st = sum(int(r["yes_strict"]) for r in recs)
sy = sum(int(r["yes_with_synonyms"]) for r in recs)
w1 = [r for r in recs if r["print_quarter"] not in ("3Q22", "4Q22")]
w2 = [r for r in recs if r["print_quarter"][-2:] in ("24", "25", "26")]
nov = [r for r in recs if r["print_quarter"].startswith("3Q")]
buck = [r for r in recs if "bucket" in r["descriptor_class"]]
print("n %d  strict %d  synonyms %d | W1 %d/%d  W2 %d/%d | November %d/%d | bucket era %d/%d %s"
      % (len(recs), st, sy, sum(int(r["yes_strict"]) for r in w1), len(w1),
         sum(int(r["yes_strict"]) for r in w2), len(w2),
         sum(int(r["yes_strict"]) for r in nov), len(nov),
         sum(int(r["yes_strict"]) for r in buck), len(buck),
         [r["print_quarter"] for r in buck]))
print("  (the log's Sec 5 says the bucket era is 1/4; 1Q26 is not a bucket letter)")
d1 = sorted(float(r["day1_excess_pct"]) for r in recs if int(r["yes_strict"]))
d1s = [float(r["day1_excess_pct"]) for r in recs if int(r["yes_with_synonyms"])]
d1n = [float(r["day1_excess_pct"]) for r in recs if not int(r["yes_strict"])]
print("strict n6  mean %+.2f  MEDIAN %+.2f  P(<=-8) %d/6" % (mean(d1), (d1[2] + d1[3]) / 2,
                                                             sum(v <= -8 for v in d1)))
print("synonym n8 mean %+.2f  P(<=-8) %d/8 | no-language(strict) mean %+.2f"
      % (mean(d1s), sum(v <= -8 for v in d1s), mean(d1n)))
er = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv")
key = {"1Q": "Q1", "2Q": "Q2", "3Q": "Q3", "4Q": "Q4"}
bad = [r["print_quarter"] for r in recs
       if abs(float(er[er.quarter == "20" + r["print_quarter"][2:] + key[r["print_quarter"][:2]]]
                    .excess_1d_pct.iloc[0]) - float(r["day1_excess_pct"])) > 0.051]
print("day-1 values disagreeing with abnb_earnings_reactions.csv:", bad or "none")

hdr("B01  tree: published, and with the three corrections")


def tn_mean(mu, sd, lo, hi):
    Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
    phi = lambda z: math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
    a, b = (lo - mu) / sd, (hi - mu) / sd
    return mu + sd * (phi(a) - phi(b)) / (Phi(b) - Phi(a))


def tree(branches, pl):
    p_dir = {">=10": .25, "9-10": .28, "<9": .35}
    p_mod = {">=10": .55, "9-10": .60, "<9": .75}
    bucket = {">=10": dict(a=.45, b=.20, c=.30, d=.05),
              "9-10": dict(a=.08, b=.22, c=.57, d=.13),
              "<9": dict(a=.02, b=.07, c=.50, d=.41)}
    tot, by = 0.0, {}
    opt = dict(a=0., b=0., c=0., d=0., e=0.)
    om = dict(a=0., b=0., c=0., d=0., e=0.)
    for br, m in branches.items():
        pd_, pn = p_dir[br], 0.03
        pb = 1 - pd_ - pn
        dm, do = pd_ * p_mod[br], pd_ * (1 - p_mod[br])
        l = dm * pl["dir_mod"] + do * pl["dir_other"]
        opt["d"] += m * dm * pl["dir_mod"]
        om["d"] += m * dm
        k = "a" if br == ">=10" else "b"
        opt[k] += m * do * pl["dir_other"]
        om[k] += m * do
        for o, w in bucket[br].items():
            l += pb * w * pl["bucket_" + o]
            opt[o] += m * pb * w * pl["bucket_" + o]
            om[o] += m * pb * w
        l += pn * pl["none"]
        opt["e"] += m * pn * pl["none"]
        om["e"] += m * pn
        by[br] = l
        tot += m * l
    return tot, by, opt, om


PL = dict(dir_mod=.85, dir_other=.10, bucket_a=.05, bucket_b=.15,
          bucket_c=.25, bucket_d=.40, none=.30)
M_pub = {">=10": 0.423, "9-10": 0.230, "<9": 0.347}
p10 = 1 - nd.cdf((10 - 9.5) / 1.70)
p9 = nd.cdf((9 - 9.5) / 1.70)
M_v2 = {">=10": round(p10, 3), "9-10": round(1 - p10 - p9, 3), "<9": round(p9, 3)}
print("R01 rev-2 N(9.5,1.70) masses", M_v2, "| B01/C02 still use N(9.67,1.70)", M_pub)
for lab, M, pl in [("published", M_pub, PL),
                   ("R01 rev-2 masses only", M_v2, PL),
                   ("dir_mod .95 only", M_pub, dict(PL, dir_mod=.95)),
                   ("bucket c/d .20/.35 only", M_pub, dict(PL, bucket_c=.20, bucket_d=.35)),
                   ("AUDITOR (all three)", M_v2, dict(PL, dir_mod=.95, bucket_c=.20, bucket_d=.35))]:
    t, by, opt, om = tree(M, pl)
    print("  %-26s P(Yes)=%.4f  P(Yes|d)=%.2f  P(Yes&d)=%.3f  share of Yes %.2f  branches %s"
          % (lab, t, opt["d"] / om["d"], opt["d"], opt["d"] / t,
             " / ".join("%.2f" % by[b] for b in M)))

hdr("B01  impact: the 9.90-vs-9.67 baseline and the kernel double count")
t, by, _, _ = tree(M_pub, PL)
post = {b: M_pub[b] * by[b] / t for b in M_pub}
mns = {">=10": tn_mean(9.67, 1.7, 10, 30), "9-10": tn_mean(9.67, 1.7, 9, 10),
       "<9": tn_mean(9.67, 1.7, -10, 9)}
e_y = sum(post[b] * mns[b] for b in M_pub)
e_u = sum(M_pub[b] * mns[b] for b in M_pub)
print("E[nights|Yes] %.2f ; tree's own unconditional %.2f -> delta %+.2f "
      "(the log uses 9.90 and publishes %.2f)" % (e_y, e_u, e_y - e_u, e_y - 9.90))
t2, by2, _, _ = tree(M_v2, dict(PL, dir_mod=.95, bucket_c=.20, bucket_d=.35))
post2 = {b: M_v2[b] * by2[b] / t2 for b in M_v2}
m2 = {">=10": tn_mean(9.5, 1.7, 10, 30), "9-10": tn_mean(9.5, 1.7, 9, 10),
      "<9": tn_mean(9.5, 1.7, -10, 9)}
d3 = sum(post2[b] * m2[b] for b in M_v2) - sum(M_v2[b] * m2[b] for b in M_v2)
r3, r4, f27 = d3 * 48, 0.6 * d3 * 30, 0.4 * d3 * 158
print("corrected: d3 %+.2f pt | 3Q26 rev %+.1f | 4Q26 rev %+.1f (kernel term dropped; "
      "published -22) | FY27 rev %+.1f (published -38)" % (d3, r3, r4, f27))
print("           FY26 margin %+.2f pp (published -0.2) | FY27 margin %+.2f pp | EPS %+.3f"
      % ((r3 + r4) * (1 - 0.35727) / 14268.1 * 100, f27 * 0.66 / 15828.6 * 100,
         f27 * 0.66 * 0.0014))

hdr("B01  every quoted letter fragment, checked against data/raw/letters")
QUOTES = {
    "3Q22": ["Nights and Experiences Booked growth will moderate slightly relative to Q3 2022"],
    "4Q22": ["nearly as strong as Q4 2022"],
    "1Q23": ["growth in Nights and Experiences Booked in Q2 2023 to be lower than our revenue growth"],
    "2Q23": ["modest sequential increase"],
    "3Q23": ["greater volatility early in Q4",
             "monitoring macroeconomic trends and geopolitical conflicts that may impact travel demand",
             "nights booked growth in Q4 2023 to moderate"],
    "4Q23": ["growth rate of nights booked in Q1 2024 to moderate relative to Q4 2023"],
    "1Q24": ["relatively stable to that of Q1 2024"],
    "2Q24": ["sequential moderation",
             "shorter booking lead times globally and some signs of slowing demand from U.S. guests"],
    "3Q24": ["higher than Q3 2024"],
    "4Q24": ["relatively stable compared to Q1 2024"],
    "1Q25": ["moderate relative to Q1 2025", "relatively softer results",
             "broader economic uncertainties", "broad macro uncertainty"],
    "2Q25": ["relatively stable compared to Q2 2025", "tougher year-over-year comparison",
             "putting pressure on growth rates later in the year"],
    "3Q25": ["mid-single-digit", "challenging Q4 2024 comparison",
             "strength in longer lead time bookings"],
    "4Q25": ["high-single-digit", "moderate increase in ADR"],
    "1Q26": ["slightly decelerate",
             "roughly 100bps headwind related to the conflict in the Middle East",
             "navigating a period of macroeconomic and geopolitical uncertainty"],
    "2Q26": ["low double-digit", "moderate increase in ADR"],
}
LET = {os.path.basename(f)[:4]: f for f in glob.glob("data/raw/letters/*.htm")}
miss = [(q, s) for q, ss in QUOTES.items() for s in ss if s.lower() not in text(LET[q]).lower()]
print("letter fragments checked %d ; not found: %s"
      % (sum(len(v) for v in QUOTES.values()), miss or "none"))

hdr("B01  do any 'no language' letters in fact carry a forward softening phrase?")
PAT = re.compile(r"moderat|lead time|soften|softer|softness|decelerat|macro", re.I)
for q in ["1Q24", "2Q23", "3Q24", "4Q24", "4Q22", "3Q25", "4Q25", "2Q26"]:
    hits = [s.strip() for s in re.split(r"(?<=[.!?]) +", text(LET[q]))
            if PAT.search(s) and "known and unknown risks" not in s and "Adjusted EBITDA is defined" not in s]
    print(" ", q, "|", " || ".join(h[:110] for h in hits[:3]) or "(none)")

# ------------------------------------------------------------------ B03
hdr("B03  cross-question inputs: what is actually on disk")
c04 = json.load(open(Q / "fy26-margin-sentence/forecasts/2026-09-17-forecast.json"))
c09 = json.load(open(Q / "q4-margin-direction-sentence/forecasts/2026-09-17-forecast.json"))
r05 = json.load(open(Q / "risk-q3-margin-sandbagged/forecasts/2026-09-17-forecast.json"))
a04 = [v for k, v in c04["final"]["vector"].items() if k.startswith("(a)")][0]
b04 = [v for k, v in c04["final"]["vector"].items() if k.startswith("(b)")][0]
up09 = [v for k, v in c09["final"]["vector"].items() if k.startswith("(c)")][0]
print("C04 rev%s (a) %.2f (b) %.2f   [B03 quotes 0.26 / 0.42]" % (c04["revision"], a04, b04))
print("C09 rev%s (c) up %.2f          [B03 quotes 0.40]" % (c09["revision"], up09))
print("R05 rev%s p %.2f                [B03 quotes 0.17; R05's RESUME kills its rev-1 "
      "S&M <= $706M / +20.7%% threshold]" % (r05["revision"], r05["final"]["p"]))
for lab, ps in [("B03 as published", (0.40 * 0.30, 0.08, 0.26 * 0.20, 0.04)),
                ("rev-2 inputs, same conditionals", (up09 * 0.30, 0.08, a04 * 0.20, 0.04)),
                ("AUDITOR (.27/.09/.20/.07)", (up09 * 0.27, 0.09, a04 * 0.20, 0.07))]:
    u = 1.0
    for p in ps:
        u *= (1 - p)
    print("  %-32s A %.3f B %.3f C %.3f D %.3f -> union %.3f"
          % (lab, ps[0], ps[1], ps[2], ps[3], 1 - u))
print("anchor: 0.5*C04(a)+0.25*C04(b) = %.3f on rev 2 (published used rev 1 -> %.3f)"
      % (0.5 * a04 + 0.25 * b04, 0.5 * 0.26 + 0.25 * 0.42))
print("stock line: EPS +0.254 x 27x = $%.1f ; the run's 16x EV/EBITDA on +$179M = $%.2f ; "
      "published -$3" % (0.254 * 27, 179 * 16 / 591.7))

hdr("B03  S&M history and the 'eight consecutive quarters' claim")
cl = pd.read_csv(ROOT / "data/processed/abnb_quarterly_costlines.csv").set_index("quarter")
qs = ["3Q22", "4Q22", "1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24",
      "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
run = 0
for i in range(4, len(qs)):
    a, b = qs[i], qs[i - 4]
    if a not in cl.index or b not in cl.index:
        continue
    s = 100 * (cl.loc[a, "sales_and_marketing_musd"] / cl.loc[b, "sales_and_marketing_musd"] - 1)
    r = 100 * (cl.loc[a, "revenue_musd"] / cl.loc[b, "revenue_musd"] - 1)
    run = run + 1 if s > r else 0
    print("  %s S&M %+6.1f%%  revenue %+6.1f%%  %s (run %d)"
          % (a, s, r, "FASTER" if s > r else "slower", run))
print("  -> the streak is %d quarters, not the eight claim 3 states" % run)

hdr("B03  every forward ADR/marketing guide sentence, from the raw letters")
for f in sorted(glob.glob("data/raw/letters/*.htm")):
    q = os.path.basename(f)[:4]
    if q[-2:] not in ("24", "25", "26"):
        continue
    for s in re.split(r"(?<=[.!?]) +", text(f)):
        if re.search(r"\bADR\b", s) and re.search(r"we expect|we anticipate|estimate that", s, re.I):
            print(" ", q, "|", s[:190])

# ------------------------------------------------------------------ B02
hdr("B02  AR(1) on the residual, and its small-sample bias")
h = pd.read_csv(ROOT / "data/processed/q3nowcast/H/adr_history_components.csv")
r = list(h.residual_pricing_pp.values)
x, y = r[:-1], r[1:]
sx, sy = mean(x), mean(y)
b1 = sum((a - sx) * (c - sy) for a, c in zip(x, y)) / sum((a - sx) ** 2 for a in x)
b0 = sy - b1 * sx
res = [c - (b0 + b1 * a) for a, c in zip(x, y)]
isd = (sum(v * v for v in res) / (len(res) - 2)) ** 0.5
ar1 = b0 + b1 * r[-1]
rho_c = min(0.999, b1 + (1 + 3 * b1) / len(r))
ar1c = (1 - rho_c) * (b0 / (1 - b1)) + rho_c * r[-1]
print("OLS      const %.3f rho %.3f innov %.3f -> 3Q26 point %.3f  (log: 0.750/0.747/0.94/4.37)"
      % (b0, b1, isd, ar1))
print("Kendall  rho %.3f -> 3Q26 point %.3f  (the branch's mean reversion is mostly small-sample bias)"
      % (rho_c, ar1c))
d = [y1 - x1 for x1, y1 in zip(x, y)]
print("residual one-quarter changes: mean %+.3f sd %.3f min %.3f n %d"
      % (mean(d), pstdev(d) * (len(d) / (len(d) - 1)) ** 0.5, min(d), len(d)))

hdr("B02  joint model reproduction and the branches that matter")


def mc(mix_mu=-1.16, mix_sd=0.35, k=0.17, bias=0.15, w=(.45, .15, .25, .15),
       res_=None, wf=(.50, .25, .25), seed=7):
    res_ = res_ or [(4.85, .55), (5.35, .55), (ar1, isd), (3.6, .7)]
    fx = [(-0.43, .33), (0.26, .42), (-1.12, .46)]
    g = random.Random(seed)
    cw = [sum(w[:i + 1]) for i in range(4)]
    cf = [sum(wf[:i + 1]) for i in range(3)]
    out = []
    for _ in range(N):
        m = g.gauss(mix_mu, mix_sd)
        u = g.random()
        i = 0 if u < cw[0] else 1 if u < cw[1] else 2 if u < cw[2] else 3
        rr = g.gauss(*res_[i])
        v = g.random()
        j = 0 if v < cf[0] else 1 if v < cf[1] else 2
        out.append(m + k + rr + g.gauss(*fx[j]) + bias)
    out.sort()
    return out


def rep(lab, s):
    print("  %-44s P(<=2.0)=%.4f  P(>=4.4)=%.4f  med=%.3f  sd=%.3f"
          % (lab, sum(1 for v in s if v <= 2.0) / len(s),
             sum(1 for v in s if v >= 4.4) / len(s), s[len(s) // 2], pstdev(s)))


rep("published joint model (target .119/.172)", mc())
rep("Kendall-corrected AR(1) branch", mc(res_=[(4.85, .55), (5.35, .55), (ar1c, isd), (3.6, .7)]))
rep("mix sd 0.60 (claim 7's own mapping RMSE)", mc(mix_sd=0.60))
rep("bias -0.07 (log's ex-POST decel split)", mc(bias=-0.07))
rep("bias +0.58 (implementable ex-ANTE split)", mc(bias=0.58))
rep("FX weights .76/.12/.12 (empirical rate)", mc(wf=(.76, .12, .12)))
AUD = mc(wf=(.63, .185, .185), mix_sd=0.50,
         res_=[(4.85, .55), (5.35, .55), (4.60, isd), (3.6, .7)])
rep("AUDITOR structural (A14-05, -11, -12 repaired)", AUD)
a_lo = sum(1 for v in AUD if v <= 2.0) / len(AUD)
a_hi = sum(1 for v in AUD if v >= 4.4) / len(AUD)
for m_, s_ in [(3.43, .927), (3.50, 1.00), (3.58, .927), (3.50, 1.05)]:
    print("  gaussian N(%.2f, %.3f): P(<=2.0)=%.4f  P(>=4.4)=%.4f"
          % (m_, s_, nd.cdf((2.0 - m_) / s_), 1 - nd.cdf((4.4 - m_) / s_)))
print("AUDITOR blend 0.55 structural + 0.45 N(3.50,1.00): B02 %.3f  R07 %.3f"
      % (0.55 * a_lo + 0.45 * nd.cdf((2.0 - 3.50) / 1.00),
         0.55 * a_hi + 0.45 * (1 - nd.cdf((4.4 - 3.50) / 1.00))))

hdr("B02  the direction split: ex-post (used) vs ex-ante (implementable)")
p = pd.read_csv(ROOT / "data/processed/adrv3/P/P1_card_v3_backtest_paths.csv")
q = p[(p.target == "t2_reported_usd_yoy") & (p.fx_estimator == "midpoint")].copy()
hist = h.set_index("quarter").adr_yoy_reported_pp
q["prior"] = [hist.get(pq) for pq in ["4Q23", "1Q24", "2Q24", "3Q24", "4Q24",
                                      "1Q25", "2Q25", "3Q25", "4Q25", "1Q26"]]
q["err"] = q.v3_point_last_q_plus_K_line_measured_mix - q.actual
for lab, s in [("EX-POST decel", q[q.actual < q.prior]),
               ("EX-POST accel", q[q.actual >= q.prior]),
               ("EX-ANTE decel", q[q.v3_point_last_q_plus_K_line_measured_mix < q.prior]),
               ("EX-ANTE accel", q[q.v3_point_last_q_plus_K_line_measured_mix >= q.prior])]:
    e = list(s.err)
    se = (sum((v - mean(e)) ** 2 for v in e) / (len(e) - 1)) ** 0.5 / len(e) ** 0.5
    print("  %-14s n %d  mean %+.3f  rmse %.3f  SE %.3f  %s"
          % (lab, len(e), mean(e), (sum(v * v for v in e) / len(e)) ** 0.5, se, list(s.quarter)))
print("  pooled bias %+.3f ; 3Q26 is an ex-ante decel quarter (model 3.4 vs 2Q26 actual %.2f)"
      % (mean(q.err), hist["2Q26"]))

hdr("B02  reference classes, re-counted")
print("reported <= 2.0: %d of %d" % (int((h.adr_yoy_reported_pp <= 2.0).sum()), len(h)))
print("FX >= -0.5: %d quarters (log says 7); of those <= 2.0: %d"
      % (int((h.fx_effect_pp >= -0.5).sum()),
         int(((h.fx_effect_pp >= -0.5) & (h.adr_yoy_reported_pp <= 2.0)).sum())))
print("residual >= 3.50: %d quarters -> <= 2.0 in %d"
      % (int((h.residual_pricing_pp >= 3.5).sum()),
         int(((h.residual_pricing_pp >= 3.5) & (h.adr_yoy_reported_pp <= 2.0)).sum())))
print("residual >= 3.45 (1Q23 rounded in, as the log's parenthesis does): %d -> <= 2.0 in %d"
      % (int((h.residual_pricing_pp >= 3.45).sum()),
         int(((h.residual_pricing_pp >= 3.45) & (h.adr_yoy_reported_pp <= 2.0)).sum())))

hdr("B02  is the FX branch calibrated? (17 quarters of disclosed FX)")
fxq = pd.read_csv(ROOT / "data/processed/adrv3/N/N1_fx_estimator_by_quarter.csv")
spread = (fxq.est_from_eur - fxq.est_from_regional_baskets).abs()
e = fxq.err_est_from_midpoint          # estimate - disclosed
print("euro-baskets spread: mean %.3f max %.3f (%s) ; 3Q26's 1.38 is outside the range"
      % (spread.mean(), spread.max(), fxq.quarter_h[spread.idxmax()]))
print("midpoint |err| mean %.3f max %.3f ; corr(|err|, spread) = %+.3f "
      "(the error does NOT widen when the estimators disagree)"
      % (e.abs().mean(), e.abs().max(), e.abs().corr(spread)))
print("a disclosed FX <= -1.0 needs err >= +0.69pp: that happened in %d of %d = %.3f "
      "(Laplace %.3f) ; the mixture puts 0.171 there"
      % (int((e >= 0.69).sum()), len(e), (e >= 0.69).mean(), 2 / (len(e) + 2)))
print("disclosed outside the eur-baskets interval (|err| >= spread/2): %d of %d ; "
      "signed >= +spread/2: %d of %d"
      % (int((e.abs() >= spread / 2).sum()), len(e), int((e >= spread / 2).sum()), len(e)))

hdr("B02 / R07  impact: a level shift is not a growth shift")
v = pd.read_csv(ROOT / "data/processed/margin_build/23_final_model/23_vs_consensus.csv").set_index("period")
fy26, fy27 = float(v.loc["FY26", "model_revenue_musd"]), float(v.loc["FY27", "model_revenue_musd"])
g0 = 100 * (fy27 / fy26 - 1)
for lab, d26, d27, pub in [("B02 Yes", -145.0, -302.0, 12.0), ("R07 Yes", 125.0, 260.0, 10.0)]:
    g1 = 100 * ((fy27 + d27) / (fy26 + d26) - 1)
    mult = abs(g1 - g0) * 0.44 * 9.5
    lev = abs(d27) * 16 / 591.7
    print("  %s: FY27 growth %.2f%% -> %.2f%% (delta %+.2f pt; the log assumes 1.9 / 1.65)"
          % (lab, g0, g1, g1 - g0))
    print("     multiple $%.2f + level $%.2f = $%.2f ; x0.70 = $%.2f  (published $%.0f)"
          % (mult, lev, mult + lev, (mult + lev) * 0.70, pub))

hdr("B02  MODL anchor")
ed = pd.read_csv(ROOT / "data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv")
a = ed[(ed.quarter == "3Q26") & (ed.metric == "adr_usd")].iloc[0]
sd = (a.street_high_growth - a.street_low_growth) / 4
print("n %d low/mean/high %.3f / %.3f / %.3f ; range/4 sd %.3f -> P(<=2.0) %.4f ; "
      "at RMSE 0.927 %.4f ; 174.72 at %.1f%% of range"
      % (a.n_estimates, a.street_low_growth, a.street_mean_growth, a.street_high_growth, sd,
         nd.cdf((2.0 - a.street_mean_growth) / sd), nd.cdf((2.0 - a.street_mean_growth) / 0.927),
         100 * (174.72 - a.street_low) / (a.street_high - a.street_low)))
```
