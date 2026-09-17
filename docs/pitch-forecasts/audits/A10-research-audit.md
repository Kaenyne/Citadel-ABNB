**R04 — 0.58: the probability is roughly defensible; the impact table beside it is not.**
The route arithmetic reproduces exactly (union 0.392063, total 0.574444).
The base rate rests on scoring the 2Q26 print a half-Yes, which the log's own convention (1) does not permit.
First repair the §9 impact table: it prices a *statement* as if the fee had delivered +20bp of net take rate.
Auditor comparison: **0.52** (judgmental 0.37–0.67), EV **≈ +$1.0/share**, not +$4.1.

**R05 — 0.17: not defensible as written; the cost stack drops the D&A add-back.**
The published Monte Carlo reproduces at 0.1905, but its adjusted-EBITDA identity is wrong by $20.6M (0.43pp).
Corrected on the line build's own definition the same script gives **0.2806**, and the required 3Q26 S&M growth becomes **+23.7%**, not +20.7% — below 2Q26's realised +26.6%.
First fix the identity, then the ceiling/threshold conflation in §6 and the stale C04 vector in §9.
Auditor comparison: **0.21** (0.13–0.32).

**R07 — 0.17: plausible as a number, incoherent as half of a pair.**
The structural mixture reproduces (P(≥4.4) 0.1076, P(≤2.0) 0.1728, median +3.12).
R07 lifts its tail ×1.5 for model bias; B02, from the same mixture, does not — the published pair implies N(3.18, 1.28), a centre below the team's own card and an sd 38% above its validated RMSE.
First build one distribution and read both tails off it; then reconcile the log's two centres (MC 3.06 vs Gaussian routes 3.43).
Auditor comparison: **0.19** (0.12–0.30), with **B02 ≈ 0.08** under the same distribution.

Audit scope: read-only review of revision 1 of all three logs and their saved evidence, plus the repo files they cite, the B02 and C11/C04/C09 revision-2 logs for cross-question coherence, and the raw letters and call mirrors for every verbatim quote. No network fetch was attempted; the Kalshi and Polymarket snapshots were read as saved. Neither prohibited directory was opened. `r05_model.py` and `r07_model.py` write into their own `datasets/` folders, so neither was executed; both were re-implemented from their source and reproduce to ±0.001.

Below, `log`, `model` and `forecast` mean `research-log.md`, `datasets/r0N_model.py` and `forecasts/2026-09-17-forecast.json` under the question's folder.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A10-01 | R04 | critical | `log:113–126`; `forecast.impact` | §9 prices the **event** (management *says* the fee is accretive) as if the fee had **delivered** +20bp of net FY27 take rate: +$230M revenue, +1.3pp FY27 margin, +$7/share, EV $4.1. But the log's own convention (2) and its route split say ~0.90 of the Yes mass is a *gross or conditional* statement consistent with a flat printed take rate (the 2Q26 form), which carries no revenue delta at all. A statement does not change the fee's arithmetic; only the market's mark changes. | `fee-takerate.md` §4: "no fee effect detectable in printed take rates through 2Q26 (n 20, slope wrong sign, permutation p 0.730)" and "a 40% migrated revenue share at a +1.8% cohort uplift is worth about +7 bp". C11 rev 2 claim 10: "the printed take rate must be treated as an output, not a lever". The same source shows the migrated cohort's **GBV falls 1.6–2.3%** while revenue rises 1.1–1.8%, so the mechanism is not a clean revenue add. | Split the impact by Yes type: direction-only/gross (0.90 of the mass) ≈ +$1–2/share of re-rating and **$0** of revenue; a quantified FY27 figure (0.10) ≈ +$230M and +$8/share. Expected stock impact ≈ **+$2/share**, EV ≈ **0.58 × 2 = $1.2** (auditor's P: **$1.0**). Materiality becomes borderline, not comfortable. |
| A10-02 | R05 | critical | `model:37`; `log:44,79`; `forecast.model.structure` | The Monte Carlo sets `ebitda = rev - cost` with `cost_budget = 2405`, citing the 40 note. But in `40_lines_quarterly.csv` **D&A sits inside `total_cash_costs`**: `adj_ebitda = revenue − total_cash_costs + da`. Dropping the $20.634M add-back puts the centre at 49.937% instead of the line build's **50.367%** — a 0.43pp error that happens to land exactly on the card, so the log reports the card's number under the line build's label. | Reproduced: cash lines sum to 2405.027 = `total_cash_costs`; 4804.036 − 2405.027 + 20.634 = 2419.642 = `adj_ebitda`; `revenue − cash − sbc = op_income` confirms D&A is inside the lines. Same identity on the 3Q25 print: cost lines ex-SBC $2,071M, revenue − cash $2,024M, printed adj EBITDA $2,051M, implied D&A $27M. | Add `+ da` (20.634). The same script then returns **P(≥51.5) = 0.2806**, median 50.663, P(above the ceiling) 0.661. Either do that and call the object the line build, or keep 49.94 and call the object the card — but not both. |
| A10-03 | R07 | critical | `log:85,98,124`; `forecast.companion`; B02 `log:89` | R07 and B02 are sold as "two tails of one distribution" but are not. R07 multiplies its model's 0.108 by ~1.5 for acceleration bias; B02 takes 0.176 from a *differently weighted* residual mixture and applies no lift. Each question is therefore quoted above its own model, in the direction that makes that risk look bigger. | Re-implemented the mixture: P(≥4.4) **0.1076**, P(≤2.0) **0.1728**, median 3.120, sd 1.121 — matching `r07_results.csv`. The Normal carrying both published tails (0.17, 0.18) is **N(3.18, 1.28)**: a centre below the card without K (3.26) and with K (3.43), and an sd 38% above the card's own walk-forward RMSE (0.927). | Publish one distribution, then read both tails. On N(3.43, 0.93) the pair is 0.148 / 0.062; on N(3.50, 1.05) it is 0.196 / 0.077; on the bias-corrected N(3.74, 0.93) it is 0.239 / 0.031. B02's 0.18 must fall whenever R07's lift is applied. |
| A10-04 | R04 | major | `log:78,83`; `forecast.estimates.base_rate` | The base rate scores the 2Q26 print a **half-Yes**, which the log's own convention (1) forbids: the fee must be named *in the accretion sentence or as an enumerated member of the "monetization initiatives" the sentence credits*. In the 2Q26 call the credited sentence enumerates nothing, and the single fee is named twice elsewhere — once as helping hosts "price more competitively", once as "in aggregate, has a kind of downward pressure on pricing". Both are negative or non-take-rate framings that convention (5) explicitly excludes. | Read the 2Q26 call mirror in full; the log's own `datasets/r04_statement_record.csv` row annotates it "fee not named in the sentence" and "(fee named elsewhere in the call as a growth driver and as downward pressure on pricing)" — then records "marginal yes". | Score 2Q26 **No**. Per-print base 1/4 = 0.25; two prints (independent) 0.4375. The log's own sensitivity puts the final at 0.52 under this classification. |
| A10-05 | R04 | major | `log:78`; `datasets/r04_decomposition.csv:two_print_base_rate` | The two-print base rate compounds `1 − (1 − p)²`, i.e. treats the 5 Nov and February prints as **independent**. Management's framing is the most persistent thing in the record (the "price more competitively" frame has now been used at three consecutive prints), so a November No is strong evidence for a February No. | Reproduced 1 − 0.625² = 0.6094. The log itself prices the dependence correctly in the *decomposition* (Feb conditional 0.30 given a November No) and then ignores it in the base rate, so the two estimates are not measuring the same object. | State the base rate as a range between the perfectly-correlated case (0.25) and the independent case (0.4375); ~0.35 at a plausible correlation. This removes the "the two estimates agree within 4 points" claim in §5. |
| A10-06 | R04 | major | `log:121,123`; `forecast.impact.margin_fy27_pp` | FY27 margin "+1.3pp" divides the EBITDA delta by the **old** revenue and ignores the denominator. | `23_vs_consensus.csv` FY27: revenue $15,828.6M, EBITDA $5,483.3M, 34.642%. With +$230M of revenue at 90% flow-through the new margin is 35.435% = **+0.79pp**. The brief's own rule (1.453% of revenue × 0.66) gives **+0.96pp**. | Use +0.8 to +1.0pp. FY27 EPS (+$0.29) is unaffected because it is computed off the EBITDA delta, not the margin. Note also that all three impact tables use 620m shares while the card uses 591.7m ($5.54 vs $5.29 per share on $205M at 16×). |
| A10-07 | R04 | major | `log:28` convention (3) | Convention (3) says an FY26 sentence at the 5 Nov print "counts only if it explicitly covers Q4". With one quarter left in the year, an FY26 take-rate statement made on 5 Nov **is** a statement about 4Q26; the resolution text asks only that accretion be attributed "for 4Q26 or FY27". This is a silent narrowing of the Yes space, and it runs the other way from the base rate, which counts the 1Q26 print's **FY26** statement as a full Yes. | Compared convention (3) with the R04 resolution text in `QUESTIONS.md:206–208` and with the 1Q26 letter, verified verbatim: "improvements to monetization through a simplified fee structure and our insurance programs, which are expected to lift our full-year take rate." | Drop the "explicitly covers Q4" qualifier, or apply the same standard to the base rate (in which case 1Q26 would also need a Q4-specific reading). As it stands the log scores history loosely and the forecast strictly. |
| A10-08 | R05 | major | `log:87`; `forecast.companion.p_above_ceiling_50.085` | "P(print above the 50.085% ceiling) ≈ 0.54 (**the card says 0.54** for a margin beat vs Street and the bias-corrected point sits on the ceiling)" conflates two thresholds. The card's 0.5403 is P(margin > **Street 49.776**). The card's own Gaussian at 50.085 gives **0.464**. | `23_card_5nov.csv` row "P(3Q26 margin beats Street margin)" = 0.540286; recomputed 1 − Φ((49.776 − 49.940)/1.6232) = 0.5403 and 1 − Φ((50.085 − 49.940)/1.6232) = **0.4644**. The MC's 0.543 is a coincidence of the two errors. | Quote the two objects separately: card route 0.46, corrected cost stack 0.66, uncorrected cost stack 0.54. The companion number as published overstates the card's agreement. |
| A10-09 | R05 | major | `log:83,87`; `forecast.final` | The final 0.17 is the decomposition 0.19 "less the two exact 'down' prints of 2025". Those two prints (3Q25 −2.4, 4Q25 −2.5) are already two of the ten observations in the ceiling base-rate class the log cites in the same paragraph. The adjustment double-counts them. | Read `r05_ceiling_record.csv`: both rows are present with excess −2.4 and −2.5 and are two of the nine non-qualifiers behind the Laplace 0.167. | Drop the ad-hoc haircut. With the D&A correction the decomposition is 0.28, so the haircut is also pointing the wrong way. |
| A10-10 | R05 | major | cross-question: C04 `log:57,135`, `datasets/mc_sentence_model_v2.py` | C04 revision 2 — same run, same day — draws the 3Q26 margin as **N(49.95, 1.0)**, which implies P(≥51.5) = **0.061**. R05 publishes 0.17. Two questions in the run carry incompatible distributions for the same printed number. | Recomputed 1 − Φ((51.5 − 49.95)/1.0) = 0.0606. C04's own sensitivity row ("sd 1.6 instead of 1.0") shows the tail is live at the card's real spread; the card's conformal sd is 1.62 (W2) / 1.72 (W1), at which P(≥51.5) is 0.168–0.182. | C04's sd 1.0, not R05's headline, is the outlier: raise C04's 3Q26 draw to the card's conformal sd. Record the joint value so X01 does not reconcile them twice. |
| A10-11 | R05 | major | `log:43,124`; `forecast.impact.stock_usd_per_share` | The impact line values the C04 knock-on off a **superseded** C04 vector: "(b) 0.42 → ~0.48". C04 revision 2 publishes (a) 0.33, **(b) 0.30**, (c) 0.05, (d) 0.27, (e) 0.05. | Read `fy26-margin-sentence/forecasts/2026-09-17-forecast.json` (revision 2) and `log:126`; the 0.42 figure is the revision-1 headline, replaced after audit A03. | Re-anchor on rev 2. C04's own row for a 51.5% Q3 gives b ≈ 0.44, c ≈ 0.20 — a **+14pt** move in (b), not +6pt, so the C04 channel is worth more than the log says. It does not lift the verdict above $1/share at P = 0.17, but it should at P = 0.21. |
| A10-12 | R07 | major | `log:42,77,85`; `forecast.estimates.decomposition` | The log carries **two centres** and never reconciles them. The Monte Carlo centres at +3.06/+3.12 (residual-mixture mean 4.6375, no K line); the Gaussian routes in the same log and the same JSON use the card's **with-K** point +3.43. §6 reports "median +3.1%" while claim 1 reports the card at +3.3/+3.4%. Worse, `decomposition_estimate: 0.14` is not the headline model (0.108) but the `mix −0.98` *sensitivity* row. | Reproduced the mixture (median 3.120) and read `adr_card_v3.csv`: without-K midpoint reported +3.26, with-K +3.43; the card's mix term is −1.160 in every row, so the MC's −1.15 is the card's mix and the "−0.98 (H fills)" row is the same decomposition with the K line moved out of the residual, not a different mix estimate. | Pick the with-K card as the centre (the log quotes +3.4% as the card), restore the K line in the MC, and make the decomposition estimate the model's own headline. The "mix −0.98 = the card's own" label in §7 is wrong and should be relabelled "K line counted in mix". |
| A10-13 | R07 | major | `log:81,85`; `forecast.estimates` | The final 0.17 is **above all three** of its own estimates (0.09 / 0.14 / 0.12), justified by a bias argument that is available as a fourth route but was never made one: the bias-corrected card gives 0.238. The "~1.5× lift" is then applied non-uniformly to the conditionals (FX ≥ +0.2: 0.37 → 0.45 is 1.22×; FX ≤ −1.0: 0.003 → 0.01 is 3.3×), so the conditional table no longer integrates to the headline. | Recomputed the Gaussian routes: midpoint raw 0.1478, bias-corrected 0.2376; baskets 0.3677 / 0.4803; euro 0.0644 / 0.1201. An FX-weighted (0.50/0.25/0.25) Gaussian on the card gives 0.182 raw and 0.269 bias-corrected. | Re-centre rather than lift: apply the bias (or half of it) to the centre, rerun, and let the conditionals fall out. That also repairs A10-03, because B02's tail then moves down automatically. |
| A10-14 | R04 | minor | `log:47`; `datasets/r04_decomposition.csv` | "overlap ρ 0.5" is never defined. The implemented rule is intersection = independence + 0.5 × (min − independence); a reader checking `0.225 + 0.315 − 0.5 × …` cannot reproduce 0.3921. | Reproduced: independence intersection 0.070875, blended 0.147937, union **0.392063**; total with the Feb conditional **0.574444**. Both match the file to 4dp. | State the blending rule in §5. The arithmetic itself is correct and should be kept. |
| A10-15 | R04 | minor | `datasets/r04_statement_record.csv`; `log:54` | The four-row statement record **does not parse** (unquoted commas; `Expected 8 fields in line 4, saw 9`), and the extraction script referenced in query-log step 5 is not saved anywhere in `datasets/`. R05 and R07 both ship runnable models; R04's central base-rate table cannot be re-derived. | `pd.read_csv` raises `ParserError` on line 4. The 13-row `r04_driver_attribution_history.csv` does parse and its counts reproduce (driver named 9/13, positive monetization driver 5/13, conditional 1). | Quote the free-text fields and ship the extraction script. Until then the 13-row table is the only reproducible base-rate artefact in R04. |
| A10-16 | R04 | minor | `log:120`; `forecast.impact.rev_4q26_musd` | The 4Q26 revenue line adds a real revenue step (+$17M) to a **market re-rating** ("the market's mark-up of the 4Q26 take rate by ~+5bp", +$12M). A re-rating belongs in the stock line, not the revenue line, where it is then double-counted through the multiple. The same line misstates C01, which carries the fee as a three-point mixture 45/40/15 over 0/+0.55%/+1.11% (expected step $12.3M), not "the bridge's half step". | Read `q4-revenue-guide-vs-street/forecasts/2026-09-17-forecast.json`: "fee in {0, +0.55%, +1.11%} at 45/40/15". 0.40 × 0.55% + 0.15 × 1.11% = 0.387% × $3,178M = $12.3M. | Report 4Q26 revenue as the move from the C01 mixture expectation to the full step (+$23M) or from the half step (+$18M), and move the $12M mark to the stock line. |
| A10-17 | R04 | minor | `log:37` claim 5 | "the migrated cohort's take rate on guest spend rises ~**+51–58bp**" — the cited table gives 14.99% → 15.50%, i.e. **+51bp**; the 58bp end is unsourced (15.50 − 14.7929 is the payout-neutral *listed reprice*, a different object). The claim also omits that the same rows show migrated-cohort **GBV falling 1.6–2.3%**, which is load-bearing against the impact table. | `fee-takerate.md` §1 row A6 and the θ table: revenue +1.07% to +2.66% across θ 0.83–0.90, GBV −1.34% to −2.87%, take 14.99 → 15.50 in every row. | Quote +51bp and carry the GBV offset into §9. |
| A10-18 | R05 | minor | `model:27–28`; `log:37` | `gaussian-from-MAE 1.30` is used as an **sd**. In `23_bands.csv` the column is `gaussian_from_mae_80` = 1.2971, an 80% **half-width**; the matching sd is 1.012. | Recomputed: at sd 1.2971 the route gives 0.1145 (the published value); at the implied sd 1.012 it gives **0.0616**. | Either use 1.012 as the sd or relabel the row as an 80% interval. The low end of the log's bracket is currently a point too high. |
| A10-19 | R05 | minor | `model:32–37`; `log:79` | The cost-stack MC's total sd is **1.42pp**, 12–17% tighter than the card's own validated conformal sd (1.62 W2 / 1.72 W1) for the same target at the same horizon. The decomposition is therefore more confident than the only object in the run with a walk-forward calibration. | Reproduced sd = 1.421 from the published parameterisation; `23_bands.csv` `gaussian_sd_from_qhat80` = 1.6232 (n 10) and 1.7197 (n 14). | Widen the cost sd, or state explicitly that the MC deliberately excludes the model-selection error the conformal band contains. |
| A10-20 | R05 | minor | `log:35` claim 3; `model:20` | "n 10 ceilings after de-duplicating **the 2Q25 letter's two Q4 sentences**" mis-describes the operation. The duplicate is one target quarter (4Q25) guided at **two different prints** (2Q25, h=2; 3Q25, h=1). `drop_duplicates` keeps the h=2 sentence; the h=1 sentence is the true analogue of 3Q26's (given in the 2Q26 letter one quarter ahead). | Read `quarterly_margin_sentence_ledger.csv`: rows 17 and 18 both target 4Q25, from the 2Q25 and 3Q25 prints. Both realised −2.5, so the count is unchanged; only the description is wrong. | Correct the sentence and say the choice is numerically immaterial. Also fix claim 5's "W1/W2 h=0 MAE 1.13 / 0.79pp" — the file gives 0.808. |
| A10-21 | R05 | minor | `log:109`; `forecast.monitoring` 2026-11-05 | The 5 Nov audit-read rule ("S&M ≤ $710M with revenue ≥ $4,800M implies the pre-print P should have been ~0.35") is calibrated on the uncorrected identity, so it will mis-score the forecast on the night. | With the D&A add-back, a 51.5% print at $4,804M needs cash costs ≤ $2,350.6M, i.e. S&M ≤ **$724M = +23.7% y/y** — *below* 2Q26's realised +26.6% and 1Q26's +33.4%. The published thresholds ($706M, +20.7%) are $18M too tight. | Restate the monitoring thresholds on the corrected arithmetic. This is also the single biggest change to the rhetoric: the log's headline argument ("Yes needs S&M growth to halve") becomes "Yes needs S&M growth to decelerate by two points". |
| A10-22 | R07 | minor | `log:35` claim 3; `forecast.estimates.anchor_source` | "0 of **7** quarters with FX ≤ 0" — there are **6** (1Q23, 2Q23, 2Q24, 3Q24, 4Q24, 1Q25). The "96th percentile of the analyst range" is **94.6%**. Neither changes a number, but both appear in the machine-readable anchor field. | Recomputed from `adr_history_components.csv` and `E_street_distribution_vs_team.csv` (low $173.71, high $179.12; (178.83 − 173.71)/5.41 = 0.946). The MODL-as-±2sd anchor reproduces at **0.0958** (log: 0.10). | Correct both counts in the log and the JSON. |
| A10-23 | R07 | minor | `log:44` claim 12 | Claim 12 quotes C11 at "0.87 → 0.71" under ADR +4.4. C11 is now **revision 2** at 0.76, with the ADR N(4.4, 1.0) sensitivity at **0.62**; C11's own RESUME says "Do not quote the revision-1 headline". | Read `q3-take-rate-above-1810/forecasts/2026-09-17-forecast.json` (revision 2) and `log:158`. | Re-quote 0.76 → 0.62. Note the reverse dependency too: C11 rev 2 claim 7 adopts the **raw** R07/B02 mixture ("P(≥4.4) 0.11–0.17, P(≤2.0) 0.18"), so if R07's lift survives, C11's GBV centre rises ~$100M and C11 falls roughly 3–4 points. |
| A10-24 | R07 | minor | `log:120`; `forecast.impact.margin_fy26_pp` | The FY26 margin line adds "3Q26 +51, 4Q26 +50" where the 4Q26 figure already contains +$23M of kernel lag on the **same** 3Q26 GBV surprise that produced the +$51M. ~$23M is counted twice. | `log:118` derives the 4Q26 line as "⅔ × $285M × 12.0% ≈ +$23M plus +1.1pt of 4Q26 ADR ≈ +$30M"; `log:120` then sums both quarters' revenue effects. | Use 2H26 revenue ≈ +$78M (or state the recognition convention once and apply it consistently). FY26 margin becomes ≈ +0.30pp rather than +0.35pp. |
| A10-25 | R07 | minor | `log:37` claim 5 | The load-bearing claim that "v3 beats naive at 0.87–0.92 on the dollar target" omits the three qualifications the source insists the pitch carry: `last_q` is a **post-hoc** rule promoted on 11 September after seeing J3's table; the binding case passes by **0.011** (eur, W2, jackknife max 0.989); and the card's ex-FX is 0.30pp below the harness-convention value because it uses J3's H fills. | `docs/adrv3/SYNTHESIS.md` lines 10 and 34 state all three verbatim, including "A reader who cares about the ex-FX sentence in the letter should use that line." | Carry the three qualifications wherever the residual rule is used as the centre. A Citadel judge who opens the SYNTHESIS will find them on the first screen. |

## R04 — what the log does well and should keep

The six conventions in §0b are the right way to handle a language question and should survive audit essentially intact — only (3) needs loosening (A10-07). The verbatim evidence is accurate: I re-extracted the 1Q26 letter ("improvements to monetization through a simplified fee structure and our insurance programs, which are expected to lift our full-year take rate"), the 2Q26 letter and call ("relatively in-line"; "Absent these incentives, we would have anticipated our implied take rate to be slightly higher during the year, driven by our monetization initiatives"; "in aggregate, has a kind of downward pressure on pricing"; "Approximately half of our active listings are now subject to the single service fee"), and the 4Q24 call ("we introduced an FX service fee mid-2024. That service fee is approximately 100 basis points applied to 20% of our GBV. On an annualized basis, you would assume that it would lift the implied take rate by about 20 basis points … for full year 2025, you should assume that the implied take rate gets the full benefit"). Every one is word-for-word.

The 13-row driver table reproduces (9/13 name a driver; 5/13 name a positive monetization driver; 1 conditional), the migrated-share path reproduces from `fee-takerate.md` §2 (3Q26 0.394, 4Q26 0.625, 1Q27 0.873), and the route arithmetic reproduces to 4dp. The recognition that the **call** route dominates the letter route, and that the 4Q24 February precedent is the template for the second print, is the log's best insight and should lead the memo paragraph. The pre-mortem's leading No path — management keeps the host-pricing frame — is correctly identified as the CEO's own framing (D053, D047) rather than a hypothetical.

## R05 — what the log does well and should keep

The reference class is the right one and is honestly built: I reproduced 10 ceiling sentences, 1 exceeded by ≥1.4pp, 2 exceeded at all, Laplace 0.167. The WS22 numbers are exact (`q_guide_implied` gaps W1 mean +0.47 / median −0.60, 6 of 14; W2 mean −0.19 / median −0.94, 4 of 10; last eight −0.86pp) and the log is right to treat "the quarterly sentence has not been sandbagged" as the governing prior rather than reaching for the evidence-only build. The card figures are exact (49.9399%, band 47.86–52.02, adj EBITDA $2,399.13M, P(beat Street) 0.7794, PIT bias −0.669 / last-five −0.271), as are M1 (51.5748%, gap 1.489pp = $71.5M) and the Street (LSEG $2,361.52M, 49.776%, n 36, EBITDA sd $20.04M).

The M5 anchor construction is legitimate and well disclosed: sd 1.356 backed out of the composite's own P(margin beat) 0.62 gives P(≥51.5) 0.167, and the log says plainly that the raw Street at its own $20M EBITDA sd gives ~0.00 — a useful reminder that consensus dispersion is not a predictive distribution. The distinction between the FY-floor beat pattern (real, 60–140bp) and the quarterly sentence (not sandbagged) is the correct structural insight and is exactly the reply the memo needs. Keep the S&M arithmetic as the memo's answer to "the sentence is sandbagged" — but on the corrected threshold (A10-21), where it is a weaker argument than the log believes.

## R07 — what the log does well and should keep

The FX mixture is well constructed and should be kept: weighting midpoint 0.50 and the two single estimators 0.25 each leaves the mean at the midpoint (−0.43) while fattening the tails, which is the right way to price an estimator choice whose two members are 1.4pp apart. The card figures reproduce exactly (eur −1.12 / baskets +0.26 / midpoint −0.43; reported +3.26 without K, +3.43 with K; usd $176.88 / $177.17; central band 1.93–4.59 and 2.03–4.84), and the walk-forward errors reproduce to 3dp (midpoint RMSE 0.927, bias −0.308; eur 1.093 / −0.377; baskets 0.829 / −0.239), as do all four Gaussian routes in the JSON.

The history is read correctly where it matters: 4 of 14 quarters at ≥ +4.4%, every one with an FX tailwind of +1.3 to +5.0pp, and 0 of 14 on an FX-neutral basis. The conditional tables (on the disclosed FX effect and on the ex-FX letter integer) are the most useful output in the batch — they turn the 5 Nov print into a scorable test rather than a pass/fail, and the model-value version of the ex-FX table integrates correctly to the model's 0.108. Keep them; just publish them off one distribution (A10-03). The pre-mortem correctly identifies that a Yes here is a revenue-leg positive that couples to C11 and to "mid teens" GBV, which is the kind of second-order coupling the memo usually misses.

## Independent numbers

**R04 — P(Yes) = 0.52**, judgmental 80% interval 0.37–0.67.
Derivation: 5 Nov letter route P(4Q26/FY take-rate sentence reads up) 0.52 × P(fee named as the driver | up) 0.50 = 0.26 — the 4Q25 comp is depressed 47bp by FX and timing and management names a driver for 9 of 13 stated directions; call route P(question asked) 0.80 (asked at each of the last three prints, and the migration completes this quarter) × P(answer attributes a positive fee effect | asked) 0.40 (observed 1 of 3) = 0.32; same ρ-blend as the log gives a 5 Nov union of 0.41, and a February conditional of 0.35 (the 4Q24 precedent is exactly this event at exactly this print) gives 0.615.
Blended 0.45 on that decomposition, 0.30 on a base rate of ~0.35 (2Q26 rescored No per A10-04, two prints positively correlated per A10-05) and 0.25 on the 0.50 flat prior: **0.507 → 0.52**. Impact: expected stock effect **+$2/share** (0.90 direction-only at ~+$1.5, 0.10 quantified at ~+$8), FY27 margin **+0.8 to +1.0pp** if fully marked, **EV ≈ +$1.0/share — borderline material**, not the published $4.1.

**R05 — P(Yes) = 0.21**, judgmental 80% interval 0.13–0.32.
Derivation: four routes — the card bias-corrected on its last five PIT errors at its own conformal sd, N(50.211, 1.6232) → 0.2136 (weight 0.40); the log's cost stack with the D&A add-back restored, centre 50.67, sd 1.42 with the slip skew → 0.2806 (0.25); the M5 dispersion-conditioned Street composite N(50.19, 1.356) → 0.167 (0.20); the ceiling base rate, 1 of 10 at Laplace → 0.167 (0.15).
Weighted: 0.40 × 0.2136 + 0.25 × 0.2806 + 0.20 × 0.167 + 0.15 × 0.167 = **0.2131 → 0.21**. The move from 0.17 is almost entirely A10-02; the ad-hoc −2pt haircut (A10-09) is removed. Impact verdict unchanged in direction but tighter: at 0.21 and a C04-rev-2-corrected stock effect of ~$3.5, **EV ≈ $0.7/share — still immaterial**, so the memo can still drop it as a stock risk and keep only the (corrected) S&M arithmetic.

**R07 — P(Yes) = 0.19**, judgmental 80% interval 0.12–0.30; **and B02 ≈ 0.08 under the same distribution.**
Derivation: centre = the card's with-K midpoint +3.43 plus **half** the measured walk-forward bias (+0.15, i.e. n = 10 and the bias is concentrated in two quarters) = **+3.50**; sd = the midpoint walk-forward RMSE 0.927, widened to **1.05** for the FX-estimator choice and the geographic-mapping error (RMSE 0.4–0.7pp on n 10) that the in-sample RMSE does not fully carry. N(3.50, 1.05) gives P(≥4.4) = **0.196** and P(≤2.0) = **0.077**.
Cross-check from the residual's own dynamics: residual changes since 1Q23 have mean +0.106 and sd 0.898 with |Δ| ≥ 1.26 in 2 of 13 quarters, so a random walk with drift plus mix (0.35) and unconditional FX (0.50) uncertainty gives N(3.37, 1.10) → 0.175 / 0.107. Both routes land in 0.17–0.20 for R07 and 0.08–0.11 for B02; I take **0.19 / 0.08**. The published pair (0.17 / 0.18) is not reachable from any single distribution the team's own evidence supports. Impact: R07's §9 stands after removing the $23M double count (A10-24) — FY26 +0.30pp rather than +0.35pp — and **EV ≈ 0.19 × $7 = $1.3/share, material**.

## Reproduction script

Run from the repository root with `python -B docs/pitch-forecasts/audits/A10-reproduce.py`. Stdlib and pandas only; it writes nothing and executes neither forecaster's model file (both write into their own `datasets/` folders). The Monte Carlo sections are re-implemented with `random.Random` rather than numpy, so they reproduce the seeded numpy figures to about ±0.002.

```python
"""A10 audit reproduction - R04, R05, R07. stdlib + pandas only; writes nothing."""
from pathlib import Path
from statistics import NormalDist, mean, pstdev
import random
import pandas as pd

ROOT = Path.cwd()
N = 400_000


def read(p):
    return pd.read_csv(ROOT / p)


def hdr(s):
    print("\n" + "=" * 8 + " " + s + " " + "=" * 8)


# ---------------------------------------------------------------- R05
hdr("R05  ceiling base rate")
led = read("docs/pitch-forecasts/questions/fy26-margin-sentence/"
           "datasets/quarterly_margin_sentence_ledger.csv")
led = led[led.guide_type.isin(["ceiling", "point", "floor"]) & led.actual.notna()].copy()
led = led[~led.target_period.isin(["3Q21", "4Q21", "2Q22", "4Q22"])]
led.loc[led.target_period == "3Q22", "actual"] = 50.52 - 49.22
led.loc[led.target_period == "3Q22", "value_high"] = 49.0 - 49.22
ceil = led[led.guide_type == "ceiling"].drop_duplicates("target_period").copy()
ceil["excess"] = ceil.actual - ceil.value_high
n_c = len(ceil)
k14 = int((ceil.excess >= 1.4).sum())
k0 = int((ceil.excess > 0).sum())
print("ceilings n:", n_c, " exceeded by >=1.4pp:", k14, " exceeded at all:", k0,
      " Laplace:", (k14 + 1) / (n_c + 2))
print("rows in the source with target 4Q25 (2Q25 and 3Q25 prints):",
      int((led.target_period == "4Q25").sum()),
      "- drop_duplicates keeps the h=2 sentence, not the h=1 analogue")
print(ceil[["print_quarter", "target_period", "value_high", "actual", "excess"]]
      .to_string(index=False))

hdr("R05  line build: is D&A inside total_cash_costs?")
lb = read("data/processed/margin_build/40_line_build/40_lines_quarterly.csv")
b = lb[(lb.quarter == "3Q26") & (lb.scenario == "base")].iloc[0]
lines = ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash"]
print("sum of cash lines:", round(sum(b[c] for c in lines), 3),
      " total_cash_costs:", round(b.total_cash_costs, 3))
print("revenue - cash costs       :", round(b.revenue - b.total_cash_costs, 3))
print("revenue - cash costs + D&A :", round(b.revenue - b.total_cash_costs + b.da, 3),
      " == 40_lines adj_ebitda", round(b.adj_ebitda, 3))
print("op_income check rev-cash-SBC:", round(b.revenue - b.total_cash_costs - b.sbc, 3),
      " == op_income", round(b.op_income, 3))
print("line-build 3Q26 margin:", round(b.adj_ebitda_margin_pct, 4),
      " vs R05 MC centre (rev-cost, no add-back):",
      round(100 * (b.revenue - b.total_cash_costs) / b.revenue, 4),
      " -> D&A is worth", round(100 * b.da / b.revenue, 4), "pp")
cl = read("data/processed/abnb_quarterly_costlines.csv")
r25 = cl[cl.quarter == "3Q25"].iloc[0]
cash25 = (r25.cost_of_revenue_musd + r25.operations_and_support_musd
          + r25.product_development_musd + r25.sales_and_marketing_musd
          + r25.general_and_administrative_musd - r25.stock_based_comp_total_musd)
print("3Q25 identity: cash costs ex-SBC", cash25,
      " revenue-cash", r25.revenue_musd - cash25,
      " printed adj EBITDA", r25.adjusted_ebitda_musd,
      " implied D&A", round(r25.adjusted_ebitda_musd - (r25.revenue_musd - cash25), 1))
print("3Q25 printed S&M:", r25.sales_and_marketing_musd,
      " line-build S&M base implied by 40_lines:",
      round(b.sm_cash / (1 + b.sm_cash_yoy_pct / 100), 1))

hdr("R05  cost-stack Monte Carlo, as published and with the D&A add-back")
rng = random.Random(20260917)
draws = [(rng.gauss(4804, 50), rng.random(), rng.gauss(0, 60), rng.uniform(30, 97))
         for _ in range(N)]
for da, lab in [(0.0, "as published"), (20.634, "with line-build D&A add-back")]:
    hits = hits_ceiling = tot = 0
    ms = []
    for rev, u, e, slp in draws:
        cost = 2405.0 + e - (slp if u < 0.25 else 0.0) + 0.20 * (rev - 4804)
        m = 100 * (rev - cost + da) / rev
        ms.append(m)
        hits += m >= 51.5
        hits_ceiling += m >= 50.085
        tot += 1
    ms.sort()
    print(f"{lab:32s} P(>=51.5)={hits/tot:.4f}  median={ms[tot//2]:.3f}  "
          f"sd={pstdev(ms):.3f}  P(>=50.085)={hits_ceiling/tot:.4f}")

hdr("R05  Gaussian routes on the card, and what the card's own band says")
bands = read("data/processed/margin_build/23_final_model/23_bands.csv")
bm = bands[(bands.target == "adj_ebitda_margin_pct") & (bands.horizon_q == 0)]
print(bm[["calibration", "n", "qhat80", "gaussian_from_mae_80",
          "gaussian_sd_from_qhat80", "mae", "bias", "bias_last5"]].to_string(index=False))
card = read("data/processed/margin_build/23_final_model/23_card_5nov.csv")
mu = float(card.loc[card["item"] == "3Q26 adj EBITDA margin", "value"].iloc[0])
sd_w1 = float(bm[bm.calibration == "W1_all_n14"].gaussian_sd_from_qhat80.iloc[0])
sd_w2 = float(bm[bm.calibration == "recent_2024Q1plus"].gaussian_sd_from_qhat80.iloc[0])
b5 = float(bm.bias_last5.iloc[0])
for lab, m, s in [("card raw, W1 sd", mu, sd_w1), ("card raw, W2 sd", mu, sd_w2),
                  ("bias-corrected (last5), W2 sd", mu - b5, sd_w2)]:
    d = NormalDist(m, s)
    print(f"{lab:30s} mu={m:.3f} sd={s:.3f} P(>=51.5)={1-d.cdf(51.5):.4f} "
          f"P(>=50.085)={1-d.cdf(50.085):.4f} P(>Street 49.776)={1-d.cdf(49.7757):.4f}")
print("gaussian_from_mae_80 (1.297) is an 80% HALF-WIDTH; r05_model uses 1.30 as an sd."
      f"  as sd: {1-NormalDist(mu,1.2971).cdf(51.5):.4f}"
      f"  as half-width: {1-NormalDist(mu,1.2971/1.2816).cdf(51.5):.4f}")
print("C04 rev-2 draws 3Q26 margin ~ N(49.95, 1.0) -> P(>=51.5) =",
      round(1 - NormalDist(49.95, 1.0).cdf(51.5), 4), "(R05 publishes 0.17)")

hdr("R05  revenue leg: cash costs and S&M implied by a 51.5% print")
for rv in [4744.32, 4770, 4804.04, 4850]:
    c_pub = rv * (1 - 0.515)
    c_da = c_pub + 20.634
    sm_pub = 778.3 - (2405.0 - c_pub)
    sm_da = 778.3 - (2405.0 - c_da)
    print(f"rev {rv:8.1f} published: costs<={c_pub:7.1f} S&M<={sm_pub:6.0f} "
          f"({100*(sm_pub/585-1):+5.1f}% y/y) | with D&A: costs<={c_da:7.1f} "
          f"S&M<={sm_da:6.0f} ({100*(sm_da/585-1):+5.1f}% y/y)")
print("1H26 printed S&M growth: 1Q26", round(100 * (751 / 563 - 1), 1),
      "%  2Q26", round(100 * (875 / 691 - 1), 1), "%")

hdr("R05  Street and the M5 anchor")
vc = read("data/processed/margin_build/23_final_model/23_vs_consensus.csv")
q3 = vc[vc.period == "2026Q3"].iloc[0]
print("LSEG 3Q26 EBITDA", round(q3.lseg_ebitda_musd, 2), "margin",
      round(q3.lseg_margin_pct, 4), "n", q3.lseg_n, "EBITDA sd", q3.lseg_ebitda_sd_musd)
sd_m5 = (50.19 - q3.lseg_margin_pct) / NormalDist().inv_cdf(0.62)
print("sd implied by M5 composite 50.19 and P(margin beat) 0.62:", round(sd_m5, 3),
      "-> P(>=51.5) =", round(1 - NormalDist(50.19, sd_m5).cdf(51.5), 4))
print("raw Street at its own EBITDA sd: P(EBITDA >= 0.515 x 4804) =",
      round(1 - NormalDist(q3.lseg_ebitda_musd, q3.lseg_ebitda_sd_musd)
            .cdf(0.515 * 4804.0355), 6))

# ---------------------------------------------------------------- R07
hdr("R07  ADR history and base rates")
h = read("data/processed/q3nowcast/H/adr_history_components.csv")
hh = h[["quarter", "adr_yoy_reported_pp", "fx_effect_pp", "adr_exfx_yoy_pp",
        "residual_pricing_pp"]]
print(hh.to_string(index=False))
print("n:", len(hh), " reported >= 4.4:", int((hh.adr_yoy_reported_pp >= 4.4).sum()),
      " quarters with FX <= 0:", int((hh.fx_effect_pp <= 0).sum()), "(the log says 7)",
      " reported>=4.4 with FX<=0:",
      int(((hh.adr_yoy_reported_pp >= 4.4) & (hh.fx_effect_pp <= 0)).sum()),
      " ex-FX-0.43 >= 4.4:", int(((hh.adr_exfx_yoy_pp - 0.43) >= 4.4).sum()))
res = hh.residual_pricing_pp.tolist()
dif = [y - x for x, y in zip(res, res[1:])]
print("residual quarterly changes:", [round(x, 2) for x in dif])
print("  mean", round(mean(dif), 3), " sd", round(pstdev(dif), 3),
      " |change| >= 1.26 in", sum(abs(x) >= 1.26 for x in dif), "of", len(dif))

hdr("R07  card v3: what the mix term actually is")
c3 = read("data/processed/adrv3/P/adr_card_v3.csv")
for _, r in c3[c3.quarter == "3Q26"].iterrows():
    print(f"{r.variant:14s} {r.fx_estimator:9s} fx={r.fx_effect_pp:+.2f} "
          f"resid={r.residual_pp:.2f} exfx={r.adr_exfx_yoy_pp:.2f} "
          f"reported={r.adr_reported_yoy_pp:.2f} usd={r.adr_usd_point:.2f} "
          f"mix(exfx-resid)={r.adr_exfx_yoy_pp - r.residual_pp:+.3f}")
print("=> the card's mix term is -1.16, so r07_model's -1.15 IS the card's mix and its")
print("   'mix -0.98 (H fills)' row is the same thing with the K line moved out of the")
print("   residual. The MC's persistence branch reproduces the WITHOUT-K card (+3.26).")

hdr("R07  walk-forward errors and Gaussian routes")
p = read("data/processed/adrv3/P/P1_card_v3_backtest_paths.csv")
p2 = p[p.target == "t2_reported_usd_yoy"]
for fx, pt in [("midpoint", 3.43), ("eur", 2.74), ("baskets", 4.12)]:
    qf = p2[p2.fx_estimator == fx]
    e = (qf.v3_point_last_q_plus_K_line_measured_mix - qf.actual).tolist()
    rmse = (sum(x * x for x in e) / len(e)) ** 0.5
    bi = mean(e)
    print(f"{fx:9s} n={len(e)} RMSE={rmse:.3f} bias={bi:+.3f} "
          f"P(>=4.4) raw={1-NormalDist(pt, rmse).cdf(4.4):.4f} "
          f"bias-corrected={1-NormalDist(pt-bi, rmse).cdf(4.4):.4f}")

hdr("R07 / B02  one distribution or two?")
rng = random.Random(20260917)
lo = hi = tot = 0
vals = []
for _ in range(N):
    mix = rng.gauss(-1.15, 0.35)
    u = rng.random()
    r = (rng.gauss(4.85, 0.55) if u < 0.55 else
         rng.gauss(5.35, 0.55) if u < 0.75 else rng.gauss(3.6, 0.7))
    v = rng.random()
    fx = (rng.gauss(-0.43, 0.33) if v < 0.5 else
          rng.gauss(0.26, 0.42) if v < 0.75 else rng.gauss(-1.12, 0.46))
    x = mix + r + fx
    vals.append(x)
    hi += x >= 4.4
    lo += x <= 2.0
    tot += 1
vals.sort()
print(f"r07_model mixture: P(>=4.4)={hi/tot:.4f} P(<=2.0)={lo/tot:.4f} "
      f"median={vals[tot//2]:.3f} sd={pstdev(vals):.3f}")
print("published pair: R07 0.17 (model 0.11, lifted ~1.5x); B02 0.18 (model 0.176, no lift)")
z1, z2 = NormalDist().inv_cdf(1 - 0.17), NormalDist().inv_cdf(0.18)
sg = (4.4 - 2.0) / (z1 - z2)
mu_j = 4.4 - z1 * sg
print(f"the Normal that would carry BOTH published tails: N({mu_j:.2f}, {sg:.2f})")
print("  its centre is below the card without K (3.26) and with K (3.43); its sd is 38%")
print("  above the card's own walk-forward RMSE (0.93)")
for m, s in [(3.43, 0.93), (3.50, 1.05), (3.74, 0.93)]:
    d = NormalDist(m, s)
    print(f"  coherent alternative N({m}, {s}): R07 {1-d.cdf(4.4):.3f}  B02 {d.cdf(2.0):.3f}")

hdr("R07  MODL anchor")
e = read("data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv")
a = e[(e.quarter == "3Q26") & (e.metric == "adr_usd")].iloc[0]
sd_modl = (a.street_high_growth - a.street_low_growth) / 4
print("MODL n", a.n_estimates, "low/mean/high growth",
      round(a.street_low_growth, 3), round(a.street_mean_growth, 3),
      round(a.street_high_growth, 3), " range/4 =", round(sd_modl, 3),
      " P(>=4.4) =", round(1 - NormalDist(a.street_mean_growth, sd_modl).cdf(4.4), 4))
print("threshold 178.83 sits at",
      round(100 * (178.83 - a.street_low) / (a.street_high - a.street_low), 1),
      "% of the analyst range (the log says the 96th percentile)")

# ---------------------------------------------------------------- R04
hdr("R04  driver-attribution table and route arithmetic")
d4 = read("docs/pitch-forecasts/questions/risk-single-fee-take-rate-accretion-stated/"
          "datasets/r04_driver_attribution_history.csv")
print("letters/calls n:", len(d4),
      " driver named:", int((~d4.driver_named.str.startswith("none")).sum()),
      " positive monetization driver:",
      int(d4.positive_monetization_driver_named.str.startswith("yes").sum()),
      " conditional:",
      int((d4.positive_monetization_driver_named == "conditional").sum()))
dec = read("docs/pitch-forecasts/questions/risk-single-fee-take-rate-accretion-stated/"
           "datasets/r04_decomposition.csv").set_index("item").value
a_, b_ = dec.letter_route_5nov, dec.call_route_5nov
ind = a_ * b_
inter = ind + dec.overlap_rho * (min(a_, b_) - ind)
union = a_ + b_ - inter
print(f"letter {a_} call {b_}  independence-intersection {ind:.6f}  "
      f"rho-blended intersection {inter:.6f}  union {union:.6f} "
      f"(file: {dec.p_yes_5nov})")
tot4 = union + (1 - union) * dec.p_yes_feb_given_no_nov
print("total with the Feb conditional:", round(tot4, 6), "(file:", dec.p_yes_total, ")")
for per in [0.375, 0.25, 0.5]:
    print(f"  per-print base {per} -> two prints, independent: {1-(1-per)**2:.4f}")
print("the two-print base rate assumes the prints are independent; management's framing")
print("is persistent, so 0.61 is an upper bound on that class.")
try:
    read("docs/pitch-forecasts/questions/risk-single-fee-take-rate-accretion-stated/"
         "datasets/r04_statement_record.csv")
    print("r04_statement_record.csv parses")
except Exception as exc:
    print("r04_statement_record.csv DOES NOT PARSE:", type(exc).__name__, exc)

hdr("R04  impact arithmetic")
fy27 = vc[vc.period == "FY27"].iloc[0]
fy27_rev, fy27_eb = float(fy27.model_revenue_musd), float(fy27.model_ebitda_musd)
d_rev, flow = 230.0, 0.90
old_m = 100 * fy27_eb / fy27_rev
new_m = 100 * (fy27_eb + d_rev * flow) / (fy27_rev + d_rev)
print(f"FY27 model revenue {fy27_rev:.1f} EBITDA {fy27_eb:.1f} margin {old_m:.3f}%")
print(f"  log's arithmetic  d_EBITDA / OLD revenue = {100*d_rev*flow/fy27_rev:.3f} pp "
      f"(the published +1.3pp)")
print(f"  correct           new margin {new_m:.3f}% -> {new_m-old_m:+.3f} pp")
print(f"  brief's rule      {100*d_rev/fy27_rev:.3f}% of revenue x 0.66 = "
      f"{0.66*100*d_rev/fy27_rev:+.3f} pp")
print("share count: the card uses 591.7m; the R04/R05/R07 impact tables use 620m "
      f"(205M of EBITDA at 16x: ${205*16/591.7:.2f} vs ${205*16/620:.2f} per share)")
```
