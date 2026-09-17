**R12 — 0.42: the arithmetic is clean, the inputs are one revision out of date.**
The published model replicates (0.4314; my independent rebuild 0.4288–0.4316) and every feed count and tape figure re-reads exactly.
But the whole target leg is the **revision-1** S04 tape block inside the **revision-1** S02 price path: residual sd 3.5% (S04 rev 2 uses 5.0%) and print weights 0.24/0.14/0.10/0.52 (S02 rev 2 uses 0.32/0.10/0.13/0.45).
Rebuilt on revision-2 parameters the model gives **0.5045**, with a 15 Dec target leg of 0.317 — which is S04 revision 2's own published 0.32, so the rebuild is verified against the sibling question.
First fix the parameters and the anchor (0.32, not 0.25); then apply B11's own feed-capture 0.85, which R12 omits. Auditor comparison: **0.47** (0.34–0.60); impact verdict (immaterial, marker only) stands.

**R13 — 0.03: the right answer, reached through a double-counted mechanism.**
Every series figure reproduces (100 settlements, mean 2.764, max 5.438, latest 2.4035% at the 34th percentile; 8 of 92 windows ≥5%, all one episode; 0 of 61 from a start below 3.0%).
The jump term (q = 2/99, U(0.9,1.5)) is calibrated on the 15 and 30 Sep 2023 rises and then added on top of an AR(1) whose residual bootstrap pool **still contains those two shocks**; removing them takes the jump model from 0.0176 to 0.0043 and the headline decomposition from 0.0307 to **0.0095**.
The down-print overlay is likewise set at the maximum of six observations (+0.70pt) rather than the mean (+0.345pt).
The published 0.03 is therefore conservative rather than wrong — the errors run toward Yes on a question the memo drops either way. Say so in one line instead of presenting 0.03 as the decomposition.
Auditor comparison: **0.02** (0.005–0.06); EV ≈ $0.06/share, immaterial, unchanged.

**R14 — 0.30: the number rests on two errors that happen to offset, and the impact table is one-sided.**
The mixture replicates exactly (0.2574, mean −0.13, sd 9.09, E[r|≥5] +10.84) and the corrected day-1 record is right where the memo's is wrong.
But the Q4 uplift is added to S01 cell means that **already contain all four post-2022 Q4 prints** (leave-one-out premium +8.85, and the full cells already sit +0.95 above ex-Q4 cells after shrink), while `p_guide_ge` 0.33 is F02 **revision 1** — revision 2 puts it at ≈0.45. Fixing both: 0.257 → **0.222**.
§9 books the up tail (+$17.8, EV $5.3) as "material" without the down tail, which contributes −$2.91 points against the up tail's +$2.77 — they net to the model mean by construction, and the event is already inside S03 revision 2.
Auditor comparison: **0.26** (0.18–0.37); the item is **immaterial as a standalone EV line**, material only as an exit-timing statement.

Audit scope: read-only review of revision 1 of all three logs and their saved evidence, plus the repo files they cite and the revision-2 forecasts of S01, S02, S03, S04, R01, C02, F01, F02 and B11 for cross-question coherence. No network fetch was attempted; the Nasdaq, yfinance, MarketBeat, Kalshi and Polymarket captures were read as saved. Neither prohibited directory was opened. `r12_model.py`, `r13_model.py` and `r14_model.py` all write into their own `datasets/` folders, so none was executed; all three were re-implemented from source and reproduce to ±0.005. Below, `log`, `model` and `forecast` mean `research-log.md`, `datasets/r1N_model.py` and `forecasts/2026-09-17-forecast.json` under the question's folder.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A13-01 | R12 | critical | `model:20–28` `S02` dict; `log:38` claim 6; `forecast.estimates.anchor` | The entire question is simulated on **superseded** sibling parameters. S02 revision 2 (`close-15dec-2026/datasets/abnb_path_mixture_v2.py:4,10,32–36`) uses print weights **0.32 / 0.10 / 0.13 / 0.45**, post-print drifts **−1.5 / −0.5 / −0.5 / −1.0**, 36 pre / 26 post sessions, 30% background vol, 6.97% total drift and a within-branch day-1 sd solved to an unconditional 9.5%; S04 revision 2 uses a tape residual sd of **5.0%** and publishes **P(mean target ≥ $190 on 15 Dec) = 0.32**. R12 hard-codes the revision-1 values (0.24/0.14/0.10/0.52, −2.0/−1.0/−1.0/−2.5, 35/27, 29%, 3%, within sd 7.5, residual 3.5%) and takes the revision-1 anchor 0.25. Every one of these differences pushes the same way. | Re-implemented the model and re-ran it parameter by parameter: published 0.4288 (numpy file 0.4314); rev-2 weights and drifts alone **0.4632**; residual sd 5.0% alone **0.4614**; **all revision-2 parameters 0.5050**, with the 15 Dec target leg at **0.3172** — S04 revision 2's own 0.32, which validates the rebuild. The variance identity on the rev-2 weights gives within-branch sd 8.451 (between 4.339). | Re-run on the revision-2 parameter set. Model → **0.50**; anchor → **0.32** (so \|final − anchor\| is +0.10, not +0.17). After A13-06 and A13-07 the final lands near **0.47**, not 0.42. |
| A13-02 | R14 | critical | `log:128–130`; `forecast.impact.stock_usd_per_share`, `ev_stock_usd_per_share`, `material` | §9 prices the event as **+$17.8/share, EV $5.3, "Material"**. That figure is E[r \| Yes] − E[r] × price, i.e. the up tail's contribution to the unconditional mean. The lower tail contributes the offsetting amount: the two sum to the model mean (≈0) by construction, so the line is mechanically positive for any upper tail and is not an expected value of anything. The February event is also already inside S03 revision 2's 12 Feb distribution, so it is not additive. R12 §9 and B11 §9 — the same construction, the same run — both label it "a marker … already counted … not additive" and book a separate direct effect; R14 does neither. | Reproduced from the model draws: P(≥+5%) 0.2574 at E[r \| ≥5] **+10.84%** → +2.79 points; P(≤−5%) 0.2709 at E[r \| ≤−5] **−10.66%** → −2.89 points; sum −0.10 = the model mean. S03 revision 2 `forecast.feb_print_event` already carries R14's own distribution (branch means +2.5/+1.0/+0.5/−0.5, model P(≥+5%) 0.32, mean +0.7%, sd 9.0). | Split the line the way R12 and B11 do. Additive operating carry: +$40M of FY27 revenue → ≈ **+$1–2/share**, EV ≈ **$0.5** → *immaterial as a standalone line*. Report the two-way tail separately and unpriced: "0.26 × +10.7% of loss against 0.30 × −10.7% of gain on a short held through 11 Feb; net ≈ 0; the price distribution is S03's." Keep the exit-timing sentence, drop the $5.3. |
| A13-03 | R14 | critical | `model:46,54`; `log:75` decomposition | The Q4 uplift is added on top of cell means that already contain the Q4 prints it is measuring. `s01_cells.csv` puts **4Q22 and 4Q23 in "decel & guide at/above" (n 5), 4Q24 in "accel & guide below" (n 3) and 4Q25 in "accel & guide at/above" (n 3)** — all four post-2022 Q4 prints are inside the centres, so `mu + q4_uplift` books the premium twice. The premium is also mis-measured for this use: +10.29 is the residual gap against S1, a **sign-only** rule, while the model conditions on sign *and* guide-vs-Street, which absorbs part of it. | Leave-one-out from the same file: ex-Q4 cell means are aa **+8.85**, ab **−8.35**, da **−2.60**, db **−7.55**; the Q4 deviations from them are 4Q22 +16.00, 4Q23 +0.90, 4Q24 +22.75, 4Q25 −4.25, mean **+8.85**, not +10.29. State-weighted, the full cells already sit **+1.45 raw / +0.95 after the 0.65 shrink** above the ex-Q4 cells. Re-ran the mixture: ex-Q4 cells + 30% of +8.85 (= +2.66) gives **0.2027**; equivalently, full cells + uplift **+1.7** gives the same answer (+1.5 → 0.2038). | Either use ex-Q4 cells with the leave-one-out premium, or keep the published cells and cut the uplift from +3.0 to **+1.7**. Both give ≈0.20 before A13-04. The §7 row "no Q4 uplift → 0.16" is then the wrong bracket end; the honest bracket is 0.16–0.26, not 0.16–0.59. |
| A13-04 | R14 | major | `log:38` claim 6; `model:43` `p_guide_ge=0.33` | F02 is at **revision 2** and its distribution moved. Claim 6 quotes revision 1 (p5/25/50/75/95 = 3.6/7.0/9.4/12.0/15.6, P(≥11.0%) ≈ 0.33, P(<10%) 0.56). Revision 2 publishes **5.1 / 8.3 / 10.5 / 12.8 / 16.1, mean 10.6, P(<10%) 0.45** against the same gap-adjusted Street of **+11.0%**. Claim 6 also quotes F01 at 0.22; F01 revision 2 is **0.28**. | Read `q1-27-revenue-guide-growth/forecasts/2026-09-17-forecast.json` (revision 2) and `q1-27-nights-guide-above-82/…` (revision 2, p 0.28). Interpolating the rev-2 percentile table at 11.0 gives P(guide ≥ Street) ≈ **0.45**. Re-ran at 0.45: **0.2837** on the published cells, **0.2212** with A13-03 applied. | Set `p_guide_ge` to 0.45 and re-cite F01/F02 revision 2. Combined with A13-03 the decomposition becomes **0.222**; note that the published 0.257 is the average of two errors pointing in opposite directions, not a number that survives either fix alone. |
| A13-05 | R14 | major | `log:33` claim 1; `forecast.record_corrected.post2022_ge5` | The block whose stated purpose is to correct the memo's day-1 record introduces its own error: "post-2022 (1Q23–2Q26, n 14): **3** (0.21)". The model's own output file says otherwise. | `datasets/r14_base_rates.json`: `post2022_n 14`, **`post2022_ge5_raw 2`**. Recounted from `abnb_earnings_reactions.csv`: only 4Q24 (+14.4) and 2Q26 (+17.4) clear +5% since 1Q23 → **2 of 14 = 0.143** (Laplace 0.188). The "3Q22+ 3 of 16 (0.19)" in the same sentence is correct. | Correct the log and the JSON to 2 of 14. The §5 base-rate route then reads 0.5 × 0.50 (Q4 Laplace) + 0.5 × 0.19 = **0.345**, not 0.38, and the "+4-point base-rate pull" that carries the final from 0.26 to 0.30 shrinks with it. |
| A13-06 | R12 | major | `model:74–80` (no capture term); cross-question: B11 `forecast.model.structure` | Two questions on the *same* Yahoo/Benzinga feed, in the same run, treat the feed's known capture rate differently. B11 applies **`feed capture 0.85`** to its downgrade counts; R12 applies none, although its own pre-mortem item (4) names the risk ("96 chain breaks, whole firms missing, so three real upgrades count as two — a resolution-source risk on the Yes side") and then prices it at 1.0. `D_live_targets_2026-09-12.csv` carries `chain_breaks_total` per firm, so the feed's gaps are documented in the repo. | Read B11's forecast JSON (`sensitivity`: "feed capture 0.85 → capture 1.0 gives 0.19; 0.70 gives 0.11"). Re-ran R12 with capture 0.85 on the revision-2 parameter set: upgrades leg 0.273 → **0.222**, total 0.5050 → **0.4766**. | Adopt one capture convention across R12 and B11, or state why upgrades are captured better than downgrades. At 0.85 the R12 model is ≈0.48. |
| A13-07 | R12 | major | `model:30` `post_mu=(2.0,1.0,0.7,0.35)`; `log:34` claim 2 | The post-print branch means are 1.6–1.8× what the log's own print-window table measures. `upgrade_base_rates.json` gives, for the 15 prints since 1Q23, **8 post-print to-Buy upgrades in total (mean 0.53)**: 1.67 on the three days that closed ≥+5% (4Q22, 4Q24, 2Q26) and **0.20** on the five that closed ≤−5%. R12 uses 2.00 and 0.35. The resulting model mean count of **1.67 upgrades** over the 89 days sits 1.8× the empirical print-shaped-window mean of 0.93 (2023+). | Summed the `post` column of `upgrade_base_rates.json["upgrades_to_buy"]["print_windows"]` by day-1 sign. Re-ran the rev-2 model with the empirical means (1.67 / 0.9 / 0.5 / 0.2) and capture 0.85: upgrades leg 0.222 → **0.187**, total → **0.4612**. | Either use the empirical branch means or justify the 1.6–1.8× regime lift explicitly against the 2026 run rate (8 to-Buy upgrades YTD, of which 4 within 5 days of a print). The honest model range on revision-2 parameters is **0.46–0.50**. |
| A13-08 | R13 | major | `model:53–62`, `:70–72`; `log:39–40` claims 7–8 | The jump term double-counts the only episode in the sample. `jump_q` is set to the frequency of the two one-step rises ≥0.9pt — **15 Sep 2023 (+0.94) and 30 Sep 2023 (+1.40)**, both the S&P 500 inclusion — and is then added on top of an AR(1) whose residuals are **bootstrapped from the full series, which still contains those two shocks** as residuals of +0.80 and +1.17. The same shock is therefore priced twice. | Refit and re-simulated. Full pool: AR(1) 0.0055, +jump **0.0181**, +jump+overlay **0.0316** (file: 0.0051 / 0.0176 / 0.0307). Pool with \|residual\| ≥ 0.75 removed (n 97, sd 0.2488 vs 0.3072): +jump **0.0041**, +jump+overlay **0.0095**. | Remove the two shocks from the bootstrap pool *or* drop the jump term, not both. The internally consistent decomposition is **≈0.010**, not 0.030. This does not force the headline down — the unmodelled structural routes justify a floor — but §5's "decomposition_estimate: 0.03" should be re-labelled as decomposition 0.010 plus a stated structural allowance. |
| A13-09 | R13 | major | `model:76` `overlay_pts=0.7`; `log:40` claim 8 | The down-print overlay is set at the **maximum** of its six observations, not the mean. `si_after_prints.csv` gives, for the six prints that closed ≤−5%, three-settlement rises of +0.68, +0.70, −0.32, +0.51, +0.06, +0.44: mean **+0.345**, median +0.475, max +0.70. Applying the maximum at the full P 0.41 is a second, smaller conservatism stacked on A13-08. | Read `si_after_prints.csv` and recomputed the six rises; the log's own claim 8 states "mean max rise +0.35pt, largest +0.70" and then the model uses 0.70. | Use +0.35 as the central overlay and keep +0.70 and +1.5 as the sensitivity rows. With the corrected jump pool the overlay then adds ≈0.002, not ≈0.013. |
| A13-10 | R12 | major | `model:67–72`; `log:37` claim 5, `log:69` | The any-day leg is implemented as "take the top 1.15 × P(end) of the **end-value** distribution", which assumes the paths that touched $190 are exactly the paths that finished highest — perfect rank correlation between the max and the end. The ratio itself is also not scale-free: the running-max premium over the end reading grows as the threshold moves into the tail (it tends to 2 in the driftless-diffusion limit), and the model's P(end) is 0.25–0.32 against the historical 0.37–0.44 on which 1.15 was measured. | Recomputed the ratio from `D_target_panel_daily.csv` (n_targets ≥ 10, log mean target, 63-session windows): all history **P(end) 0.3719, P(max) 0.4407, ratio 1.185**; 2023+ 0.4403 / 0.4902, ratio 1.113 (the log reports 0.353 / 0.429 / 1.22 and 0.438 / 0.49 / 1.12 — the 2023+ pair matches, the all-history pair does not). The rejected three-checkpoint construction gives 0.351. | Keep 1.15 but state the rank-preserving assumption in §4, and correct the all-history figures to 0.372 / 0.441 / 1.185. The leg's honest range is 0.317 (15 Dec only, rev-2) to 0.365 (any-day) to ≈0.40 (three-checkpoint); the ±0.05 is a real part of the question's uncertainty and belongs in the interval, not only in the sensitivity table. |
| A13-11 | R14 | major | `log:85` §6 "Coherence with S03"; `log:133` RESUME item (3) | Stale by one revision, and the instruction is now wrong. §6 says S03 carries the event at P(≥5) 0.39 / mean +2.6 and tells the orchestrator to "use R14's number … rather than re-run S03". S03 is at **revision 2** and has already re-run: it adopts R14's own object (branch means +2.5 / +1.0 / +0.5 / −0.5, model P(≥+5%) **0.32**, mean +0.7%, sd 9.0) and restates the corrected record verbatim. The published gap is 0.30 vs 0.32, not 0.30 vs 0.39. | Read `close-12feb-2027/forecasts/2026-09-17-forecast.json` revision 2, `feb_print_event` and `sensitivity` row 1. | Rewrite §6 against revision 2. If R14 moves to ≈0.26 per A13-03/A13-04, S03's Feb branch means should come down ≈0.5–0.8pt (its own sensitivity row prices the mapping), which moves the 12 Feb median by roughly −$1 — small, but it is the orchestrator's call, not "do not re-run". |
| A13-12 | R12 | major | `log:37` claim 5 | "with prints inside (all): P(≥ +3.7%) 0.22 / 0.26 (2023+)" mislabels the figures. Those are the **all-window** 35-session numbers; the with-print subset is far higher, which understates the print channel the claim exists to demonstrate. | Recomputed: 35-session all windows **0.2181 / 0.2604 (2023+)** — the quoted pair; with a print inside, n 817, **0.3586**; with no print inside, n 577, **0.0191**. The no-print figures in the same claim (0.019, P(≥2%) 0.12, mean −0.26%, sd 2.1%) are exact. | Correct the sentence to "with a print inside: 0.359 (n 817)". The claim's conclusion — that the tape moves ≥3.7% almost only through prints — becomes stronger, not weaker. |
| A13-13 | R12 | minor | `log:80–83`; `forecast.estimates.anchor` | The anchor is a repo prior from a sibling question rather than a market, and it is one revision stale; `final_minus_anchor: +0.17` is measured against a number that no longer exists. There is no `NOT_INDEPENDENTLY_DERIVED` flag even though the anchor is literally the same tape block the model replicates. | S04 revision 2 `model.outputs["P(T>=190)"] = 0.32`. My rev-2 rebuild of R12's own tape block returns 0.3172 on the 15 Dec reading — the anchor and the model are the same object. | Re-anchor on 0.32 and flag the dependence explicitly, as S04 revision 2 does for its own anchor ("NO INDEPENDENT ANCHOR"). \|final − anchor\| on my number is +0.15 and is justified by the upgrades leg alone. |
| A13-14 | R12 | minor | `log:34` claim 2 | The printed 2023+ print-window series "0,0,0,0,2,0,0,2,1,0,0,4,2,2" is **14** values for **15** prints: the 2023-02-15 window (n 1) is dropped and the list is shifted. | `upgrade_base_rates.json["upgrades_to_buy"]["print_windows"]` from 2023-01-01: 1,0,0,0,0,2,0,0,2,1,0,0,4,2,2 — sum 14, mean 0.933, P(≥3) 1/15 = 0.0667. The mean and P(≥3) quoted in the same sentence are right. | Print the 15-value series. |
| A13-15 | R12 | minor | `log:35` claim 3 | "Tape on **16 Sep**: 32 live targets, mean $181.81, median $182.5" — the panel's last observation is **11 Sep** and the live-target file is dated 12 Sep. The retrieval column on the row says "2026-09-12 to 2026-09-16". | `D_target_panel_daily.csv` ends 2026-09-11 (mean_target 181.8125, n_targets 32). `D_live_targets_2026-09-12.csv`: n 32, mean **181.8125**, median 182.5, buckets 22 Buy / 8 Hold / 2 Sell — all exact. Morgan Stanley sits in the file at **$125** (Underweight, 30 Jul), so replacing it with $170 gives 181.8125 + 45/32 = **183.21875** and $190 needs **+3.70%** — both exact. | Date the tape 11–12 Sep and keep the rest; this claim is otherwise the best-sourced in the log. |
| A13-16 | R14 | minor | `model:44,55`; `log:39` claim 7 | The options-implied Feb **event sd** (central 9.0, 8.47 at S01's own 33.85% background) is used as the model's *residual* sd, after which the cell-mean dispersion and a QQQ term are added — so the model's total sd is **9.09**, above the object it is meant to match. The anchor is then computed at 9.0 on a different construction. | Reproduced the term-structure identity: 11.15 / 9.46 / 8.47 / 6.77 at backgrounds 29 / 32.3 / 33.85 / 36 (exactly the saved JSON). Model sd 9.089. Solving the residual back out (8.0) gives total sd 8.62 and P(≥5) **0.248**. | Solve the residual sd from the target total, or say plainly that the model is deliberately one notch wider than the option. Worth −0.01 on the headline. |
| A13-17 | R14 | minor | `model:43` `n3=(9.55,1.48)` | The run's **adopted** 3Q26 nights object is N(9.5–9.67, **1.70**) — R01 revision 2 ("latent 3Q26 nights growth ~ N(9.5, 1.70)"), and F01/F02 revision 2's V1 leg (Q3 ~ N(9.67, 1.70), Q4 = 8.1 + 0.5(Q3 − 9.67) + N(0, 1.4), 12% tail). R14 uses the revision-1 nowcast sd 1.48 and an independent 4Q26 draw with corr 0.5. | Re-ran at N(9.67, 1.70): P(accel) 0.121 → 0.122, P(≥5) 0.257 → 0.258. Immaterial here because the two constructions give nearly the same sign distribution (analytically, sd of the difference 1.543 vs 1.638, mean −1.45 vs −1.57). | Cite the adopted object and note the immateriality, rather than carrying a superseded band silently. |
| A13-18 | R14 | minor | `log:125`; `forecast.impact.rev_fy27_musd` | The +$40M FY27 revenue line is derived against **F02 revision 1's** +9.4% median ("conditional 1Q27 guide midpoint ≈ +10.3% vs F02's +9.4%"); revision 2's median is +10.5%, so the conditional-minus-base gap is smaller. The row is also reverse-causal — an up day does not raise FY27 revenue, it selects worlds with a better guide — and the "0.25pt of FY27 growth" step from a +$25M one-quarter guide delta is an undisclosed judgement. | F02 revision 2 percentile table, median 10.5; `p_guide_ge_given_ge5` 0.522 vs 0.33 reproduces from the model draws. | Re-derive against revision 2, show the quarter-to-year carry-through assumption, and keep the "(indirect)" label. The row is small either way (≈$0.3/share). |
| A13-19 | R13 | minor | `log:28` convention (3); `model:16` | The convention says "basic shares **outstanding**, Class A plus Class B, as the repo file uses (`shares_out_m` from `abnb_capital_return_quarterly.csv`)". That column is `basic_wa_shares_m` — a **weighted-average** count — and the 09 note says so explicitly ("converted to % of shares outstanding using basic weighted-average shares"). Actual shares outstanding are ≈598.8m. | `abnb_capital_return_quarterly.csv` 2Q26: `basic_wa_shares_m` 592.0, `diluted_wa_shares_m` 597.0. `yfinance_info_short_20260917T035213Z.json`: `sharesOutstanding` 419,529,556 (Class A only), `impliedSharesOutstanding` **598,785,682**. On 598.786m the threshold is 29.939m shares (×2.104 of the latest) and the latest reading is 2.376%, not 2.403%. | Describe the denominator as the repo file's basic weighted-average count and record the outstanding-count alternative. No change to the answer (the threshold moves by 0.34m shares). |
| A13-20 | R13 | minor | `log:33` claim 1 | The claim reports yfinance `shortPercentOfFloat` **3.44%** and, in the same row, a computed **3.51%** on the same float, as if they were the same observation. 14,228,547 / 405,782,346 = 3.506%; 3.44% is not reproducible from yfinance's own `sharesShort` and `floatShares`. | Read the saved `yfinance_info_short_20260917T035213Z.json`: `sharesShort` 14,228,547, `floatShares` 405,782,346, `shortPercentOfFloat` 0.0344, `sharesPercentSharesOut` 0.0241. | Say which reading each number uses, or quote only the computed 3.51%. The 0.0241 vs the log's 2.40% is the same rounding and is fine. |
| A13-21 | R13 | minor | `log:130`; `forecast.impact.note` | The impact note carries two different stock numbers ("**+$3**" in the column, "≈ **+$1** unconditional at $167.5" in the text) and conditions on "P 0.24" — the **S02 revision-1** accelerating-print weight; revision 2 is 0.32. | S02 revision 2 `scen` block, weight 0.32. EV at either number is ≤ $0.1/share. | Pick one figure, update the branch weight, and keep the verdict (immaterial). The borrow-cost/recall sentence is the only consequential part and should lead the row. |
| A13-22 | R12 | minor | `log:133`; `forecast.impact.stock_usd_per_share_as_marker` | The marker "+$14.6 (E[15 Dec \| Yes] $175.7 vs $161.1)" is computed on revision-1 parameters. | Rebuilt on revision-2 parameters: **$178.5 vs $165.5 = +$12.9** (and +$14.2 once the 0.85 capture is applied). The direct effect (+$1.5) and the materiality verdict are unaffected. | Update the marker. The EV-as-marker coincidentally stays near $6.1 because P rises as the spread narrows; say so rather than leaving both numbers stale. |
| A13-23 | R14 | minor | `log:35` claim 3; `log:67` | The Q4 uplift's own source disowns it more strongly than the log admits, and its stated mechanism is the same one the model already prices through `p_guide_ge`. C §10 item 3: "Decelerating guides at Q4 prints average +7% (4 prints), elsewhere −6% (7 prints). With four observations this could be 'the market looks through the Q1 comp' or four coincidences; **it was found after the guide-direction test failed and is a reading, not a result**." C §1 item 1 adds that none of the 17 pre-stated specs clears Holm. | Read `C_reaction-function.md:12,170–171,180,258`; the +7.1 / −5.8 split and the 4Q22 4Q23 4Q24 4Q25 membership reproduce exactly. | Quote the disclaimer where the uplift is used, and reconcile it with `p_guide_ge`: if the Q4 premium exists because "a guide that says what the calendar says is not news", then the guide-vs-Street penalty and the uplift are two views of one effect and should not both be carried at full strength. |
| A13-24 | R12 | minor | `log:28` convention (3) | "rise to ≥ $190" is read as *any feed date in the window*. That is a live re-reading of the resolution sentence worth roughly 4 points (0.317 on the 15 Dec reading vs 0.365 any-day on revision-2 parameters), and it is the reading that makes the question easier to resolve Yes. | Re-ran both: rev-2 any-day 0.3648 vs 15 Dec only 0.3172; published 0.2861 vs 0.2488. The log reports both, and §7 carries the sensitivity. | Keep the convention but make the memo state which reading it quotes, and put both in `forecast.final` rather than only the any-day number. |
| A13-25 | R13 | minor | `log:79,82,91` | §5 presents 0.03 as the decomposition and the final. After A13-08 and A13-09 the decomposition is ≈0.010 and the final 0.03 is being held up by the extreme-gate floor ("the point is not taken below 0.02 because of edge (a)") plus an unstated structural-event allowance. The published number is right to within a point but its stated derivation is not the one doing the work. | Reproduced the routes: AR(1) 0.0055; internally consistent jump+overlay 0.0095; conditional empirical 0 of 61 windows from a start below 3.0%; episode base rate 0.06. | Restate §5 as: decomposition 0.010, structural-event allowance ≈0.008 (a new convertible, an index or M&A event — none of which the 100-settlement series can contain), resolver-basis residual ≈0.003, total ≈0.02, rounded up to 0.03 for model risk. That is an honest 0.02–0.03 and survives the audit as written. |

## R12 — what the log does well and should keep

The feed work is exact and should survive intact. I re-read `feed_upgrades_all.csv`: **26 `up` rows since 2021, 21 to Buy-equivalent**, by year 2021 5 / 2022 1 / 2023 1 / 2024 2 / 2025 4 / 2026 YTD 8 — every year matches, and the five excluded rows (Goldman Sell→Neutral, Cantor, Barclays and Wells UW→EW, Truist Sell→Hold) are correctly excluded as upgrades to Hold-equivalent. The 2026 list (B. Riley 12 Jan, Citizens 4 Feb, Deutsche 13 Feb, Evercore 13 Feb, Wells 22 Apr, Oppenheimer 4 May, Wedbush 7 Aug, Raymond James 8 Sep) is right, as is "4 of the 9 trailing-12-month upgrades within 5 days of a print". The live-target arithmetic is exact to the cent: 32 firms, mean $181.8125, median $182.5, 22/8/2, Morgan Stanley in the file at $125 so the $170 re-initiation lifts the base to $183.21875 and the threshold to +3.70%. Convention (1)'s exclusion of initiations (Rosenblatt Buy $220, 1 Sep) and of the Morgan Stanley UW→EW row is the right reading of "upgrades to Buy/Outperform-equivalent", and convention (4)'s exclusion of Weiss and Phillip Securities is correct on the feed evidence.

Every quotation from the D note is verbatim and in context: the chase numbers (0.40 at +20 sessions, 0.47 on up prints, 77 raises vs 10 cuts on six ≥+5% prints, mean target +6.3%), the ratings sentence ("Across the last four prints: 5 upgrades, 0 downgrades in the [−5, +25] session windows; across all 23 prints 21 upgrades, 15 downgrades"), and the off-print +5.9% after a 15%+ rise. The 90-day rolling-window base rates reproduce exactly from `upgrade_base_rates.json` (2021+ 0.062, 2023+ 0.090, 2024+ 0.127; all-`up` 2024+ 0.257), as do the no-print tape statistics (35-session P(≥3.7%) 0.019, P(≥2%) 0.12, mean −0.26%, sd 2.1%) — that pair is the single best fact in the log and should lead the memo sentence, because it says the target leg is a print bet, not a drift bet. The §4 decision to discard the three-checkpoint construction (0.351) in favour of a measured running-max ratio is the right instinct, and the pre-mortem's item (2) — that a de-risking 9–10% print could draw catch-up upgrades from the Hold/Sell pool even after a sell-off — is the correct non-obvious Yes path.

## R13 — what the log does well and should keep

The series construction is careful and checks out. The MarketBeat dollar-series reconstruction calibrates against the repo's known settlements at **ratio mean 0.9999, sd 0.0009 (n 65)** — that is as good as this kind of extension gets, and it earns the 100-settlement sample. Every summary figure reproduces: mean 2.764, median 2.605, max 5.4375, min 1.4766, latest 2.4035% at the 34th percentile; local peaks ≥3.3 at Jul 2022 3.50, Dec 2022 3.34, Jan 2023 3.49, Jun 2023 4.04, Sep 2023 5.44, Sep 2025 3.53; per-step sd 0.3147 with exactly two rises ≥0.9pt, both September 2023.

The structural argument is the strongest thing in the batch and should be the memo's one sentence on this item: the single 5% episode in five years is the S&P 500 inclusion front-run (3.10 → 4.04 → 5.44 → 4.70 → 4.56 → 3.91 → 3.00, verified settlement by settlement in the extended file), ABNB is already in both indices, and the other historical hedge-short source — the $2.0bn 0% converts — was retired in March 2026 into **straight** senior notes (the saved 424B2 says so verbatim). The regime-conditioned base rate is therefore the right one, and **0 of 61 windows starting below 3.0% and 0 of 42 starting below 2.5% ever reached 5%**, against a required rise of **2.60pt** that exceeds the largest 8-settlement rise in the whole sample (2.34pt). The eight-settlement convention is right, including 13 Nov for the Sunday 15 Nov settlement (I checked every weekday). The extreme-probability audit in §6 is done properly — edge (a), the float basis, is correctly identified as the dominant resolution risk, correctly excluded on the question's own wording ("of shares outstanding … as in `09_short_interest.csv`", which divides by basic shares), and correctly carried in the interval rather than the point. Keep the float number (≈0.25) in the log so the memo cannot be ambushed by a MarketBeat screenshot.

## R14 — what the log does well and should keep

The record correction is the log's best contribution and is right where the memo and the task brief are wrong: **5 of 6 positive, 3 of 6 ≥ +5%, 5 of 6 ≥ +3.5%, mean +7.93, median +8.95** — all exact from `abnb_earnings_reactions.csv`, and the diagnosis is right too (the memo's "6 of 6" at line 77 is the 09 note's calendar-February *excess* count, a different object). The monitoring row that tells the memo to replace the sentence should be executed before 2 Oct.

The options work is exact and well constructed. The Jan/Mar variance difference isolates the February event correctly — the 5 Nov print is inside both expiries and cancels — and reproduces to three decimals at every background (11.15 / 9.46 / 8.47 / 6.77). Presenting the event sd as a function of the background assumption rather than as a point is the right way to carry an estimate that swings 8.5 → 11.2 on a 4-point vol assumption. The S1 residual arithmetic is exact (Q4 mean +7.72, sd 7.54, non-Q4 −2.57, gap +10.29, Welch t 2.379), and §4's decision to carry it at 30% rather than in full, with the +5 and +10 rows published, is the correct discipline for a post-hoc n-4 effect — my objection in A13-03 is to the base it is added to, not to the shrink. The conditional tables (by 4Q26 sign, by 1Q27 guide-vs-Street) are the most useful output here because they turn 11 Feb into a scorable test, and the monitoring calendar's 5 Nov re-centring rule is the right shape. The pre-mortem's item (2) — the "November short case makes February a relief print" mechanism, explicitly named as *not* separately modelled — is exactly the kind of honest gap an audit should find already flagged.

## Independent numbers

**R12 — P(Yes) = 0.47**, judgmental 80% interval 0.34–0.60.
Derivation: rebuild the published two-leg simulation on the run's **current** inputs — S02 revision 2 (weights 0.32/0.10/0.13/0.45, post drifts −1.5/−0.5/−0.5/−1.0, 36/26 sessions, 30% background, 6.97% total drift, within-branch day-1 sd 8.451 from the variance identity) and S04 revision 2 (tape residual sd 5.0%) — which gives **0.5045** with legs 0.273 / 0.365 and a 15 Dec target reading of 0.317, i.e. S04 revision 2's own 0.32. Then apply the two corrections that run the other way: B11's feed capture 0.85 (→ 0.4766) and the empirical print-window post-print means (→ 0.4612).
Take the midpoint of that corrected model range (0.47) and check it against a base rate built the same way: upgrades leg ≈0.22, target leg 0.32 × 1.15 = 0.37, intersection ≈0.11 at the measured print correlation → union **0.48**. Both routes land at 0.47–0.48; I take **0.47**. Impact: unchanged in substance — direct effect ≈ +$1.5/share, **EV ≈ 0.47 × 1.5 = $0.7/share, immaterial as a standalone line**; as a marker of the accelerating-print branch, E[15 Dec \| Yes] $178.5 vs $165.5 = +$12.9, EV $6.1, explicitly not additive with R01/R02/S02.

**R13 — P(Yes) = 0.02**, judgmental 80% interval 0.005–0.06.
Derivation: the internally consistent model — AR(1) on the 100-settlement series (slope 0.9057, long-run mean 2.779) with the two September-2023 index-inclusion shocks removed from the bootstrap pool (residual sd 0.249), the jump term calibrated on those same two shocks at q = 2/99, and the down-print overlay at S01's P(day-1 ≤ −5%) = 0.41 — gives **0.0095**, against an empirical rate of 0 of 61 windows from a start below 3.0% and a required rise (2.60pt) larger than anything in the sample.
Add ≈0.008 for the structural routes the settlement series cannot contain (a new convertible or exchangeable, an index event, a stock-component deal) and ≈0.003 for the float-basis resolver edge (≈0.04 × 0.25) → **0.021**. Companions on the same basis: P(max ≥ 4.0%) ≈ 0.10, P(max ≥ 3.5%) ≈ 0.25, window-max median ≈ 2.9%, p90 ≈ 3.9%. Impact: **EV ≈ 0.02 × $3 = $0.06/share — immaterial**; the memo should drop the line and keep only the borrow-cost sentence.

**R14 — P(Yes) = 0.26**, judgmental 80% interval 0.18–0.37.
Derivation: rebuild the mixture with the two fixes — ex-Q4 cell means (aa +8.85, ab −8.35, fl −8.70, da −2.60, db −7.55), the leave-one-out Q4 premium **+8.85** carried at the log's own 30% (= +2.66), and F02 revision 2's P(1Q27 revenue guide ≥ the gap-adjusted Street +11.0%) = **0.45** — which gives **0.2212** (mean −0.96%, sd 8.97, P(<0) 0.557, P(≤−5%) 0.302, E[r \| ≥5] +10.75).
Weight 0.50 on that, 0.35 on the options anchor (risk-neutral symmetric at the Jan/Mar-implied 9.0% event sd, mode −0.4: **0.274**) and 0.15 on the corrected class base rate (0.5 × Q4 Laplace 0.50 + 0.5 × post-2022 Laplace 0.19 = **0.345**): 0.111 + 0.096 + 0.052 = **0.259 → 0.26**.

| Companion (R14, auditor mixture) | value |
|---|---:|
| P(day-1 < 0) | 0.55 |
| P(day-1 ≥ +10%) | 0.10 |
| P(day-1 ≤ −5%) | 0.30 |
| P(day-1 ≤ −8%) | 0.18 |
| mean / sd (%) | −0.6 / 9.0 |
| p5 / p25 / p50 / p75 / p95 (%) | −14.9 / −6.2 / −1.1 / +4.2 / +13.4 |

Impact: the additive part is the operating carry only — +0.1pt of 4Q26 nights, +$3M of 4Q26 revenue, ≈+$30M of FY27 revenue (re-derived against F02 revision 2, not revision 1), +0.1pp of FY27 margin, +$0.02 of FY27 EPS, worth **≈ +$1–2/share, EV ≈ $0.4 — immaterial as a standalone line**. The two-way price risk is real but belongs to S03: on my distribution a short held through 11 Feb faces 0.26 × +10.75% of loss against 0.30 × −10.7% of gain, which nets to roughly zero and is already inside S03 revision 2's 12 Feb percentiles. The memo should keep the exit-timing sentence and delete the $5.3.

## Reproduction script

Run from the repository root with `python -B docs/pitch-forecasts/audits/A13-reproduce.py`. Stdlib and pandas only; it writes nothing and executes none of the three forecast models (all write into their own `datasets/` folders). The Monte Carlos are re-implemented with `random.Random` at 120,000 draws rather than numpy at 300–400,000, so they reproduce the seeded numpy figures to about ±0.005; each block prints the file's own numbers underneath for comparison. Runtime ≈ 4 minutes.

```python
"""A13 audit reproduction - R12, R13, R14. stdlib + pandas only; writes nothing."""
from pathlib import Path
from statistics import NormalDist, mean, stdev
import json
import math
import random
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
N = 120_000


def hdr(s):
    print("\n" + "=" * 10 + " " + s + " " + "=" * 10)


def pct(v, q):
    s = sorted(v)
    k = (len(s) - 1) * q
    lo = int(k)
    return s[lo] if lo + 1 >= len(s) else s[lo] + (k - lo) * (s[lo + 1] - s[lo])


# ------------------------------------------------------------------ R14 (A)
hdr("R14  day-1 record and the S1 Q4 residual")
rx = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv")
rx["lbl"] = rx.quarter.map(lambda q: q[5] + "Q" + q[2:4])
ACC = {"3Q22", "3Q23", "4Q24", "3Q25", "4Q25", "2Q26"}
DEC = {"4Q22", "1Q23", "2Q23", "4Q23", "1Q24", "2Q24", "1Q25", "2Q25", "1Q26"}
FLT = {"3Q24"}
rx["sign"] = rx.lbl.map(lambda s: 1 if s in ACC else (-1 if s in DEC else (0 if s in FLT else None)))
rx["resid"] = rx.excess_1d_pct - (-0.67 + 3.35 * rx["sign"].astype(float))
q4 = rx[rx.quarter.str.endswith("Q4")]
print("Q4 day-1 raw:", dict(zip(q4.quarter, q4.abnb_1d_pct)))
print("Q4: positive %d/6, >=5%% %d/6, >=3.5%% %d/6, mean %.3f, median %.2f"
      % ((q4.abnb_1d_pct > 0).sum(), (q4.abnb_1d_pct >= 5).sum(),
         (q4.abnb_1d_pct >= 3.5).sum(), q4.abnb_1d_pct.mean(), q4.abnb_1d_pct.median()))
for lo, name in [("2020Q4", "all 23"), ("2022Q3", "3Q22+ (16)"), ("2023Q1", "post-2022 (14)")]:
    s = rx[rx.quarter >= lo]
    print("  %-16s n %2d  >=+5%% %d  rate %.3f  Laplace %.3f"
          % (name, len(s), (s.abnb_1d_pct >= 5).sum(), (s.abnb_1d_pct >= 5).mean(),
             ((s.abnb_1d_pct >= 5).sum() + 1) / (len(s) + 2)))
print("  log/JSON claim post-2022 '3 of 14 (0.21)' -> the file gives",
      int((rx[rx.quarter >= "2023Q1"].abnb_1d_pct >= 5).sum()), "of 14")
r16 = rx[rx["sign"].notna()]
a = r16[r16.lbl.str.startswith("4Q")]
b = r16[~r16.lbl.str.startswith("4Q")]
print("S1 residual: Q4 mean %.3f (sd %.3f, n %d), non-Q4 %.3f, gap %.3f, Welch t %.3f"
      % (a.resid.mean(), a.resid.std(), len(a), b.resid.mean(),
         a.resid.mean() - b.resid.mean(),
         (a.resid.mean() - b.resid.mean())
         / math.sqrt(a.resid.var() / len(a) + b.resid.var() / len(b))))

hdr("R14  the Q4 uplift is already inside the S01 cells")
CELLS = {"aa": ["3Q25", "4Q25", "2Q26"], "ab": ["3Q22", "3Q23", "4Q24"], "fl": ["3Q24"],
         "da": ["4Q22", "2Q23", "4Q23", "2Q25", "1Q26"],
         "db": ["1Q23", "1Q24", "2Q24", "1Q25"]}
raw = dict(zip(r16.lbl, r16.abnb_1d_pct))
exq4 = {}
dev = []
for k, v in CELLS.items():
    ex = [q for q in v if not q.startswith("4Q")]
    exq4[k] = mean(raw[q] for q in ex)
    print("  cell %-3s full %6.2f (n%d)   ex-Q4 %6.2f (n%d)"
          % (k, mean(raw[q] for q in v), len(v), exq4[k], len(ex)))
    dev += [(q, raw[q] - exq4[k]) for q in v if q.startswith("4Q")]
print("  Q4 deviations from ex-Q4 cell means:", [(q, round(d, 2)) for q, d in dev],
      "-> leave-one-out premium %.2f (the log uses the S1 gap 10.29)" % mean(d for _, d in dev))

hdr("R14  Feb event sd from the Jan / Mar 2027 expiries")
ts = pd.read_csv(Q / "close-15dec-2026/datasets/implied_term_structure_20260917T031221Z.csv")
jan = ts[ts.expiry == "2027-01-15"].iloc[0]
mar = ts[ts.expiry == "2027-03-19"].iloc[0]
vj = (jan.atm_iv / 100) ** 2 * jan["T"]
vm = (mar.atm_iv / 100) ** 2 * mar["T"]
for bg in (29.0, 32.3, 33.85, 36.0):
    print("  background %5.2f%% -> event sd %.3f%%"
          % (bg, 100 * math.sqrt(max(vm - vj - (bg / 100) ** 2 * (mar["T"] - jan["T"]), 0))))
for sd in (8.5, 9.0, 9.5):
    print("  anchor at sd %.1f: P(>=+5%%) %.4f at mode -0.4, %.4f at mean 0"
          % (sd, 1 - NormalDist().cdf((5 + 0.4) / sd), 1 - NormalDist().cdf(5 / sd)))


def r14(seed=7, n=N, n3=(9.55, 1.48), n4=(8.1, 1.6), tw=.12, tail=(5.5, 1.5), corr=.5,
        band=.25, p_guide=.33, cells=None, shrink=.65, uplift=3.0, rsd=8.5, df=5,
        qqq=1.3, unc=-1.0):
    g = random.Random(seed)
    if cells is None:
        cells = dict(aa=7.4, ab=-0.8, fl=-8.7, da=0.8, db=-7.6)
    k = math.sqrt(df / (df - 2))
    out = []
    for _ in range(n):
        z1 = g.gauss(0, 1)
        z2 = corr * z1 + math.sqrt(1 - corr ** 2) * g.gauss(0, 1)
        x3 = n3[0] + n3[1] * z1
        x4 = n4[0] + n4[1] * z2
        if g.random() < tw:
            x4 = tail[0] + tail[1] * g.gauss(0, 1)
        d = x4 - x3
        ge = g.random() < p_guide
        if d >= band:
            m = cells["aa"] if ge else cells["ab"]
        elif d > -band:
            m = cells["fl"]
        else:
            m = cells["da"] if ge else cells["db"]
        mu = unc + shrink * (m - unc) + uplift
        c2 = sum(g.gauss(0, 1) ** 2 for _ in range(df))
        t = g.gauss(0, 1) / math.sqrt(c2 / df)
        out.append(mu + rsd * t / k + qqq * g.gauss(0, 1))
    up = [r for r in out if r >= 5]
    dn = [r for r in out if r <= -5]
    return dict(p_ge5=len(up) / n, p_le_m5=len(dn) / n,
                p_lt0=sum(r < 0 for r in out) / n, mean=mean(out), sd=stdev(out),
                E_up=mean(up), E_dn=mean(dn),
                pctiles={q: round(pct(out, q / 100), 2) for q in (5, 25, 50, 75, 95)})


hdr("R14  published mixture, and the two corrections")
pub = r14()
print("published (full cells, uplift 3.0, p_guide 0.33):",
      json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in pub.items()}))
print("  the file's numpy run: p_ge5 0.2574, mean -0.13, sd 9.09, E[r|>=5] +10.84, E[r|<=-5] -10.66")
print("F02 revision 2 (p_guide 0.45)                   : p_ge5 %.4f" % r14(p_guide=.45)["p_ge5"])
print("ex-Q4 cells + leave-one-out uplift 8.85 x 0.3   : p_ge5 %.4f" % r14(cells=exq4, uplift=2.66)["p_ge5"])
aud = r14(cells=exq4, uplift=2.66, p_guide=.45)
print("both corrections (auditor mixture)              :",
      json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in aud.items()}))
print("  up-tail EV %+.2f pts vs down-tail EV %+.2f pts: they net to the mean (A13-02)"
      % (pub["p_ge5"] * pub["E_up"], pub["p_le_m5"] * pub["E_dn"]))

# ------------------------------------------------------------------ R12
hdr("R12  feed, live targets, D panel")
feed = pd.read_csv(Q / "risk-sellside-upgrades/datasets/feed_upgrades_all.csv")
print("feed 'up' rows since 2021: %d, to Buy-equivalent: %d" % (len(feed), feed.to_buy.sum()))
print("to-Buy by year:", feed[feed.to_buy].date.str[:4].value_counts().sort_index().to_dict())
lt = pd.read_csv(ROOT / "data/processed/reverse_dcf/D/D_live_targets_2026-09-12.csv")
print("live targets n %d  mean %.4f  median %.1f  buckets %s"
      % (len(lt), lt.target.mean(), lt.target.median(), lt.rating_bucket.value_counts().to_dict()))
ms = float(lt.loc[lt.Firm == "Morgan Stanley", "target"].iloc[0])
base_ms = lt.target.mean() + (170 - ms) / len(lt)
print("Morgan Stanley is in the feed at $%.0f -> replacing with $170 gives base %.5f; $190 needs %+.2f%%"
      % (ms, base_ms, 100 * (190 / base_ms - 1)))

p = pd.read_csv(ROOT / "data/processed/reverse_dcf/D/D_target_panel_daily.csv", parse_dates=["date"])
p = p[p.n_targets >= 10].reset_index(drop=True)
prints = set(pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv",
                         parse_dates=["reaction_date"]).reaction_date)
lnT = [math.log(v) for v in p.mean_target]
thr = math.log(190 / 183.22)
print("panel n_targets>=10: %d rows, %s to %s; threshold +%.3f%%"
      % (len(p), p.date.min().date(), p.date.max().date(), 100 * (math.exp(thr) - 1)))
for W in (63, 35):
    ends, maxs, hp, d23 = [], [], [], []
    for i in range(len(p) - W):
        seg = lnT[i:i + W + 1]
        ends.append(seg[-1] - seg[0])
        maxs.append(max(seg) - seg[0])
        hp.append(any(d in prints for d in list(p.date[i:i + W + 1])))
        d23.append(p.date[i] >= pd.Timestamp("2023-01-01"))
    pe = sum(e >= thr for e in ends) / len(ends)
    pm = sum(m >= thr for m in maxs) / len(maxs)
    e2 = [e for e, f in zip(ends, d23) if f]
    m2 = [m for m, f in zip(maxs, d23) if f]
    pe2 = sum(e >= thr for e in e2) / len(e2)
    pm2 = sum(m >= thr for m in m2) / len(m2)
    npw = [e for e, f in zip(ends, hp) if not f]
    wpw = [e for e, f in zip(ends, hp) if f]
    print("  %ds all n %4d P(end) %.4f P(max) %.4f ratio %.3f | 2023+ n %4d %.4f / %.4f ratio %.3f"
          % (W, len(ends), pe, pm, pm / pe, len(e2), pe2, pm2, pm2 / pe2))
    print("      no print in window n %4d P(end) %.4f mean %+.3f%% sd %.3f%% | with print n %4d P(end) %.4f"
          % (len(npw), sum(e >= thr for e in npw) / len(npw), 100 * mean(npw),
             100 * stdev(npw), len(wpw), sum(e >= thr for e in wpw) / len(wpw)))
print("  claim 5 reports the 35s 'with prints inside' as 0.22 / 0.26: those are the ALL-window figures")


def r12(seed=11, n=N, weights=(.24, .14, .10, .52), d1=(4., -1., -2.5, -6.), d1sd=7.5,
        post_drift=(-2., -1., -1., -2.5), spre=35, spost=27, bg=.29, drift=.03,
        rsd=.035, base=183.22, pre_mu=.7, post_mu=(2., 1., .7, .35), beta=.06,
        od=1.6, thrT=190., ratio=1.15, any_day=True, capture=1.0):
    g = random.Random(seed)
    dt = 1 / 252
    kl = (.13 + .10) * (-.068) + .10 * .206 + 3 * .0005
    b0, b1, b2, chase, stale = .075, .13, .10, .40, .005
    cum, acc = [], 0.
    for w in weights:
        acc += w
        cum.append(acc)
    ka = round(spost * 13 / 27)
    kb = spost - ka
    f = 21 / spre

    def nb(m):
        lam = m if od <= 1.0 else g.gammavariate(m / (od - 1.0), od - 1.0)
        k, term, cdf, u = 0, math.exp(-lam), math.exp(-lam), g.random()
        while u > cdf and k < 60:
            k += 1
            term *= lam / k
            cdf += term
        return k

    T, dec, up_leg = [], [], []
    for _ in range(n):
        u = g.random()
        z = next(i for i, c in enumerate(cum) if u <= c)
        rpre = (drift - .5 * bg * bg) * spre * dt + bg * math.sqrt(spre * dt) * g.gauss(0, 1)
        day1 = d1[z] / 100 + d1sd / 100 * g.gauss(0, 1)
        rd1 = math.log1p(day1)
        pdr = math.log1p(post_drift[z] / 100)
        rpa = pdr * (ka / spost) + (drift - .5 * bg * bg) * ka * dt + bg * math.sqrt(ka * dt) * g.gauss(0, 1)
        rpb = pdr * (kb / spost) + (drift - .5 * bg * bg) * kb * dt + bg * math.sqrt(kb * dt) * g.gauss(0, 1)
        p1 = f * rpre + math.sqrt(f * (1 - f)) * bg * math.sqrt(spre * dt) * g.gauss(0, 1)
        p2 = rpre - p1
        ln = (kl + (b0 + b1 + b2) * p1 + (b0 + b1) * p2 + chase * rd1
              + (b0 + .5 * b1) * (rpa + rpb) + stale + rsd * g.gauss(0, 1))
        T.append(base * math.exp(ln))
        dec.append(167.51 * math.exp(rpre + rd1 + rpa + rpb))
        cnt = nb(pre_mu * capture) + nb(post_mu[z] * math.exp(beta * (day1 * 100 - d1[z])) * capture)
        up_leg.append(cnt >= 3)
    pend = sum(t >= thrT for t in T) / n
    lo = pct(T, 1 - min(ratio * pend, .999)) if any_day else thrT
    tleg = [t >= lo for t in T]
    yes = [a or b for a, b in zip(up_leg, tleg)]
    return dict(p=sum(yes) / n, p_up=sum(up_leg) / n, p_T=sum(tleg) / n, p_T_end=pend,
                E_dec_yes=mean(d for d, y in zip(dec, yes) if y), E_dec=mean(dec))


hdr("R12  published parameters vs the revision-2 parameters of S02 and S04")
REV2 = dict(weights=(.32, .10, .13, .45), post_drift=(-1.5, -.5, -.5, -1.),
            spre=36, spost=26, bg=.30, drift=.0697, d1sd=8.451, rsd=.05)
for name, kw in [("published (S02/S04 revision 1)", {}),
                 ("S02 rev2 weights + post drifts", dict(weights=(.32, .10, .13, .45),
                                                         post_drift=(-1.5, -.5, -.5, -1.))),
                 ("S04 rev2 tape residual sd 5.0%", dict(rsd=.05)),
                 ("all revision-2 parameters", REV2),
                 ("revision-2 + B11 feed capture 0.85", dict(REV2, capture=.85)),
                 ("revision-2 + capture + empirical post means",
                  dict(REV2, capture=.85, post_mu=(1.67, .9, .5, .2)))]:
    r = r12(**kw)
    print("  %-44s P %.4f | up %.4f  T %.4f (15 Dec %.4f) | E[Dec|Yes] %.1f vs %.1f"
          % (name, r["p"], r["p_up"], r["p_T"], r["p_T_end"], r["E_dec_yes"], r["E_dec"]))
print("  the file's numpy run: P 0.4314, up 0.2454, T 0.2861 (15 Dec 0.2488), E[Dec|Yes] 175.7 vs 161.1")
print("  S04 revision 2 publishes P(mean target >= 190 on 15 Dec) = 0.32: the rebuild lands on it")

# ------------------------------------------------------------------ R13
hdr("R13  series, windows, AR(1), and the jump double count")
h = pd.read_csv(Q / "risk-short-interest-crowding/datasets/si_history_2022_2026.csv",
                parse_dates=["date"]).sort_values("date")
nas = json.loads((Q / "risk-short-interest-crowding/sources/"
                  "nasdaq_short_interest_20260917T080127Z.json").read_text())
rows = nas["data"]["shortInterestTable"]["rows"]
latest = float(rows[0]["interest"].replace(",", ""))
print("Nasdaq latest settlement %s: %d shares" % (rows[0]["settlementDate"], int(latest)))
for so in (592.0, 598.785682):
    print("  on %.3fm shares: %.4f%% of shares; 5%% needs %.3fm shares (x%.3f of the latest)"
          % (so, latest / (so * 1e6) * 100, .05 * so, .05 * so * 1e6 / latest))
x = list(h.si_pct_used) + [latest / (592.0 * 1e6) * 100]
ov = h.dropna(subset=["si_pct_shares"])
rat = ov.shares_m_est / (ov.short_interest_shares / 1e6)
print("MarketBeat reconstruction vs the repo series: n %d, ratio mean %.4f sd %.4f"
      % (len(rat), rat.mean(), rat.std()))
print("series n %d, mean %.3f, median %.3f, max %.3f, min %.3f, latest at the %.0fth percentile"
      % (len(x), mean(x), pct(x, .5), max(x), min(x),
         100 * sum(v < x[-1] for v in x) / len(x)))
W = 8
win = [(x[i - 1], max(x[i:i + W])) for i in range(1, len(x) - W + 1)]
for name, sub in [("all", win), ("prior level < 3.0", [w for w in win if w[0] < 3.0]),
                  ("prior level < 2.5", [w for w in win if w[0] < 2.5])]:
    print("  8-settlement windows %-18s n %2d  P(max>=5) %.4f  P(max>=4) %.4f  largest rise %.2fpt"
          % (name, len(sub), sum(m >= 5 for _, m in sub) / len(sub),
             sum(m >= 4 for _, m in sub) / len(sub), max(m - p0 for p0, m in sub)))
print("  the rise now required is %.2fpt: no window in the series delivers it" % (5 - x[-1]))
ch = [x[i + 1] - x[i] for i in range(len(x) - 1)]
print("  per-step sd %.4f, %d steps, rises >= 0.9pt: %s (both the Sep 2023 S&P 500 inclusion)"
      % (stdev(ch), len(ch), [round(c, 2) for c in ch if c >= 0.9]))
sx, sy = x[:-1], x[1:]
mx, my = mean(sx), mean(sy)
slope = sum((u - mx) * (v - my) for u, v in zip(sx, sy)) / sum((u - mx) ** 2 for u in sx)
icept = my - slope * mx
res = [v - (slope * u + icept) for u, v in zip(sx, sy)]
clean = [r for r in res if abs(r) < 0.75]
print("  AR(1) slope %.4f, intercept %.4f, long-run mean %.4f, residual sd %.4f (clean pool n %d sd %.4f)"
      % (slope, icept, icept / (1 - slope), stdev(res), len(clean), stdev(clean)))


def ar1(pool, seed=3, n=60_000, jq=0.0, op=0.0, opts=0.7):
    g = random.Random(seed)
    hit5 = hit4 = 0
    for _ in range(n):
        v = x[-1]
        ov = g.random() < op
        m = -9.9
        for k in range(9):
            v = slope * v + icept + pool[g.randrange(len(pool))]
            if jq and g.random() < jq:
                v += g.uniform(0.9, 1.5)
            if op and (k - 1) in (3, 4):
                v += ov * opts / 2
            if k >= 1:
                m = max(m, v)
        hit5 += m >= 5
        hit4 += m >= 4
    return hit5 / n, hit4 / n


for name, pool, jq, op in [("AR(1) only", res, 0.0, 0.0),
                           ("AR(1) + jump 2/99", res, 2 / 99, 0.0),
                           ("AR(1) + jump + down-print overlay (published)", res, 2 / 99, 0.41),
                           ("episode shocks removed from the pool, + jump", clean, 2 / 99, 0.0),
                           ("episode shocks removed, + jump + overlay", clean, 2 / 99, 0.41)]:
    p5, p4 = ar1(pool, jq=jq, op=op)
    print("  %-46s P(max>=5) %.4f  P(max>=4) %.4f" % (name, p5, p4))
print("  the file's numpy run: 0.0051 / 0.0176 / 0.0307 for the first three")
```
