# Response to audit A07 (S02 close-15dec-2026, S03 close-12feb-2027, S04 sellside-mean-target-cut-by-15dec)

Response date: 2026-09-17
Responds to: `A07-research-audit.md` (Astra, gpt-6-astra, read-only)
Revised research: `questions/close-15dec-2026/research-log.md`, `questions/close-12feb-2027/research-log.md`, `questions/sellside-mean-target-cut-by-15dec/research-log.md` (all revision 2)
Revised forecasts: each question's `forecasts/2026-09-17-forecast.json` (revision 2; all three numbers moved)
Revised model: `questions/close-15dec-2026/datasets/implied_dist_v2.py`, `abnb_path_mixture_v2.py`, `final_blend_v2.py`; `questions/close-12feb-2027/datasets/dec_to_prerelease_window.py`, `run_v2.py`; `questions/sellside-mean-target-cut-by-15dec/datasets/target_base_rates_v2.py`, `run_v2.py` (revision-1 scripts and outputs left untouched as the audit trail)
Reproduction script: `A07-reproduce.py` (the audit's script, saved verbatim; ran clean under `py -3.13 -B`, no path fix needed; output in `A07-reproduce.stdout.txt` and at the end of this file)

## Summary

Seventeen findings. Fifteen accepted, two accepted in part (A07-08, A07-12), none rejected. Every number in the audit reproduced exactly: the legacy −3.75% drift and its −3.12% rebased value, the W1/W2 figures, the −2.125% / −0.613% accelerating-print pairings, the 1.54% / 0.47% negative RND mass, the lognormal-anchor thresholds actually used by the revision-1 blend, the session counts, the tape regressions, the corrected down-print class and the re-vintaged reviews-index ratios. Astra's independent constructions also reproduce (S02 $163.2, S03 $167.4, S04 0.331).

Headline numbers, revision 1 → revision 2:
- **S02** median $162 → **$166**; P(≤150) 0.33 → **0.30**; P(≤143) 0.24 → **0.22**; P(≥180) 0.28 → **0.32**; percentiles 121/129/144/162/183/204/217 → **121/129/146/166/186/207/221**; mass below $100 0.3% → 0.5%, above $260 0.4% → 0.7%.
- **S03** median $165 → **$166**; P(≤150) 0.34 → **0.34**; P(≤143) 0.27 → **0.27**; P(≥180) 0.35 → **0.37**; percentiles 113/123/141/165/193/222/242 → **110/121/141/166/195/224/244**; below $100 1.5% → 2.1%, above $260 2.5% → 2.9%.
- **S04** P(Yes) 0.29 (0.20–0.40) → **0.30 (0.20–0.42)**.

What moved the numbers. S02: three changes each worth $1–1.6 on the median — the adopted print-state weights (R02 puts 0.32 on an accelerating print, not 0.24; +$1.1), one drift convention for the diffusion and the anchor (total 6.97% = cash + 3% premium, not 3% total; +$1.6), and post-print drifts rebased at the reaction close and carried at about half of revision 1 (+$1.5) — plus the anchor rebuilt as an arbitrage-free mixture RND whose real-world median is $2 above the revision-1 lognormal (+$0.7 through the 0.35 weight). S03: the same three shifts (+$6) are offset by R14's February event (mean +0.8% instead of the +2.6% base-rate shrink, −$3.3) and the smaller measured pre-release window (−$0.8), so the centre is unchanged while the tails widen (the anchor now carries the 56% of the February event variance the Jan/Mar interpolation had dropped). S04: the residual sd of the exact hybrid tape equation is 4.3–5.2% on 21 historical windows, not 3.5% (+0.03), against the accel-heavier weights and lighter drift (−0.025). The structural argument is unchanged: the print view is worth about −3% on the December median, the sell-side tape follows price with a lag, and no tradable market exists for any of the three objects.

## Finding-by-finding

### A07-01 (critical, S04) — "ties resolve No" reverses the registry's ≤ $176.80 rule: accepted
Reproduced: `QUESTIONS.md` § S04 says "≤ $176.8"; revision 1's convention (5) said ties resolve No; the simulation used `<=` throughout (0.2953025). Convention (5) now reads: a mean of exactly $176.80 resolves Yes; the monitoring row for 15 Dec says "≤ $176.80 inclusive". A 32-firm mean of integer or half-dollar targets can land on $176.80 exactly (e.g. a sum of $5,657.60), so the audit is right that the measure-zero claim was wrong in kind, not only in wording. Numerical effect: none.

### A07-02 (critical, S02) — corporate-action fallback assigns a new resolution object: accepted
Reproduced: revision 1's convention (6) ("last comparable close") has no basis in the registry, and no component of the path model carried the claimed 0.5%. Convention (6) rewritten: the question asks for the 15 Dec close of ABNB as listed; a delisting before 15 Dec is a resolution case the registry does not define, it is not modelled and no substitute price is asserted. The hypotheses table entry now says "not modelled" rather than "tail 0.5%". Numerical effect: none.

### A07-03 (major, S02/S03) — the blend used a lognormal, not the smile RND it described: accepted
Reproduced: `final_blend.py:21–29` builds `norm.cdf` at the saved sigma centred on the smile median; the anchor thresholds actually blended were S02 0.187 / 0.264 / 0.362 and S03 0.240 / 0.306 / 0.401 (≤143 / ≤150 / ≥180), not the smile's 0.208 / 0.280 / 0.340 and 0.268 / 0.332 / 0.382 the logs quoted; the genuine shifted-smile blend would have put 0.80% below $100 in S02 (published 0.32%) and 2.01% in S03 (1.55%). Fix: `implied_dist_v2.py` writes the anchor CDF on the blend grid (`anchor_cdf_v2.csv`) and `final_blend_v2.py` reads that file, so the anchor in the blend is the anchor in the log. Because of A07-04 the object itself changed (next item). Final-minus-anchor is now computed against the anchor actually used (S02 −$5.0 on the median, +0.03 / +0.02 / −0.05 on the thresholds; S03 −$3.5, +0.01 / +0.01 / −0.04).

### A07-04 (major, S02/S03) — the fitted smile has negative risk-neutral density: accepted
Reproduced by the audit's own Black-76 reconstruction and by `implied_dist_v2.py`: integrated negative density 1.538% (18 Dec) and 0.475% (Jan/Mar interpolation) before clipping. Fix: the anchor is now a forward-constrained two-lognormal mixture RND fitted by weighted least squares to the same OTM mids per expiry (Bahra / Melick-Thomas) — a valid density by construction. Fits: 18 Dec w 0.81, F₁ $166.9 σ₁ 41.9%, F₂ $179.4 σ₂ 13.9%, rmse $0.16 on 15 quotes (max error $0.34); 15 Jan rmse $0.31 (14 quotes; the second component hits the 5% vol floor, a thin right tail); 19 Mar rmse $0.17 (16 quotes). At the thresholds the mixture reproduces the clipped smile within 0.01 (S02 risk-neutral 0.214 / 0.279 / 0.350 vs 0.208 / 0.280 / 0.340), which is why the tails, not the quartiles, are where the repair shows: P(<100) 0.8% vs the lognormal's 0.24%. The mixture's risk-neutral median is $169.3, $3 above the ATM-lognormal's $166.3 and $2 above the clipped smile's $167.3 — the put skew removes the lognormal's positive price skew, so the median sits at the forward. The measured ATM IVs and the event sd are unchanged and still quoted (claim 7). Effect on S02: anchor real-world median $168.6 → $170.6, and through the 0.35 weight +$0.7 on the final median.

### A07-05 (major, S02/S03) — the −3.75% "drift" is not a return earned from the reaction close: accepted
Reproduced from `09_prices_daily.csv`: legacy −3.7500% (n 23) is a difference of cumulative returns normalised to the close 21 sessions before the reaction; rebased at the reaction close it is −3.1201% at +20 (median −3.29, 9 of 23 positive), W1 −0.8592% (n 14), W2 −1.9177% (n 10); at +27 sessions W1 +0.9748% (n 13), W2 −1.2502% (n 9); after a day-1 up −5.99% (n 11), after a day-1 down −0.49% (n 12). The drift does not survive both windows at the model's horizon. Fix: claim 6 rewritten on the rebased figures; the post-print drifts are now −1.5 / −0.5 / −0.5 / −1.0% by branch (weighted −1.1%, versus −2.0% in revision 1), labelled judgment, with the no-drift row (Astra's construction) shown as the alternative (+$1.7 on the decomposition median). The 15 Dec → 11 Feb drifts are −0.5 / −0.5 / −0.5 / −2.0% (revision 1 +1 / −1 / −1 / −3), keeping the memo's estimate-cut leg on the base branch only.

### A07-06 (major, S02) — the −4.7% accelerating-print drift mixed n 5 and n 4: accepted
Reproduced: `05_reaction_by_accel.csv` reports day-1 n 5 and day-20 n 4 for accelerating post-2022 prints; paired on the four observations in `abnb_earnings_reactions.csv` the day-1 → day-20 difference is −2.125% (median +1.1, 3 of 4 positive); the C panel's five prints give −0.613% under its cumulative-excess convention. The missing observation was 2Q26 (+17.4% day-1). Revision 2's accel post-print drift is −1.5% (between the two paired figures and the day-1-up reversal of −6.0% at n 11, which RED_TEAM lists as dead); "half-strength of −4.7%" is withdrawn.

### A07-07 (major, S04) — down-print class contaminated with 2Q22; "any net cut" became "cut ≥ 3.8%": accepted
Reproduced from `D_print_revisions.csv`: the six day-1 ≤ −5% prints are 3Q22, 1Q23, 1Q24, 2Q24, 3Q24, 2Q25 with +20-session target changes −7.62, −6.45, +1.66, −14.07, +3.51, −0.02%; any net cut 4 of 6, cut ≥ 3.8% 3 of 6; 2Q22 (day-1 −1.13%, targets −10.1%) belongs to the small-print class. Claim 28 rewritten (1Q24 added, 2Q22 removed, 2Q25 labelled effectively unchanged); the 6 Nov monitoring rule now quotes the model's own conditional P(Yes | day-1 ≤ −8%) = 0.57 (0.50–0.60) with "3 of 6" as the rationale, instead of 0.55–0.65 on "4 of 6". `target_base_rates_v2.json` carries the corrected class.

### A07-08 (major, S04) — the 3.5% residual sd was not established by any fitted object: accepted in part
Reproduced: the 22-window two-regressor refit gives −0.0848 + 0.0968 × Δprice + 0.4048 × day-1, residual sd 6.677 (W1 5.92, W2 6.86), and raising the simulation's noise to 6.68% moves P from 0.2953 to 0.3495. Accepted that 3.5% was a judgment from the one-month sd applied to a three-month hybrid. The audit asked for the residual of the exact hybrid equation at the exact horizon: `target_base_rates_v2.py` now evaluates the model's Δln T equation (two known lags, p1 21 sessions, p2pre 15, day-1 × 0.40, post 26 × 0.14, constants) on every historical print window (n 21): residual sd **5.21% (rmse 5.14) all, 4.26% W1 (n 13), 4.70% W2 (n 9)**; a regression of realised on predicted has slope 1.25 (R² 0.55), so the equation is directionally right and under-sized by about a quarter in-sample. Revision 2 carries 5.0%, with 3.5% and 6.68% as the sensitivity's bounds (0.27 / 0.33). In part: the 6.68% figure is the residual of a different, lag-free equation, so it is the upper case rather than the estimate; and the calibration is in-sample (not walk-forward, as the audit preferred) — stated in claim 36. Effect: +0.03 on the model probability, offset by the other revision-2 changes (net 0.295 → 0.299).

### A07-09 (major, S04) — the 50% "anchor" is an interpretation of a repo judgment: accepted
Reproduced: `D_sell-side-dispersion.md` §5 (the JUDGEMENT paragraph) gives a qualitative 3–4% cut and no probability, on the same tape-lag history this log uses. Revision 2 states that no independent anchor exists (no market; the $182.98 `targetMeanPrice` is a level), labels the 0.50 a non-independent repo prior in the log and the JSON (`anchor_independent: false`), and no longer presents the 0.20 gap as disagreement with a consensus. The JSON's `estimates.anchor` field is kept at 0.50 so the ledger schema still parses, with the label beside it.

### A07-10 (major, S02/S03/S04) — the reviews-index RMSE was cited without the re-vintaging failure: accepted
Reproduced from `t1_fail_e5_rerun.csv`: 1.4751 / 2.1591 = 0.6832 (original), 1.8159 / 2.1591 = 0.8410 (literal substitution), 1.6336 / 2.1591 = 0.7566 (103-market variant), each on n 10; the WPK note withdraws the survivor interpretation while leaving the vintage-matched band unchanged. Claim 11 rewritten with the corrected provenance; the named asymmetry in the S02 log and JSON no longer cites an established edge and the December asymmetry is carried at ~3% rather than 4%. The larger practical change is that the print-state weights are now the adopted R01/R02/S01 values (accel 0.32 / flat 0.10 / decel-ok 0.13 / decel-below 0.45), which already embed the outside view and the market leg; the day-1 mixture mean moves −2.5% → −1.8%.

### A07-11 (major, S03) — the Jan/Mar interpolation prices only 44% of the February event: accepted
Reproduced: calendar weight 28/63 = 0.4444; restoring the missing 55.6% of a 9.5% event takes the revision-1 lognormal's horizon log sd from 24.058% to 25.078% (annual IV 37.65% → 39.25%). Fix: `implied_dist_v2.py` interpolates the Jan and Mar mixture RNDs in log-quantile space (log-sd 24.3%) and convolves with N(0, 0.5556 × 0.095²) in log space (log-sd 25.2%), then shifts by the premium. The anchor's P(<100) is 2.5% (revision-1 lognormal 1.4%) and P(≥180) 0.41. "1.44 events is close to two" withdrawn; the event sd (8.5% R14 low case) is a sensitivity row (< 0.005 at the thresholds).

### A07-12 (major, S03) — full Jan/Feb seasonality double-counts the February reaction; "+2% is not a quarter of +14.6%": accepted in part
Reproduced: calendar January +6.861% and February +7.667% excess (n 6 each), sum 14.53%; +2% retains 13.8%, not 25%; and the calendar-February observation contains the reaction day. Accepted on both points. The audit's remedy was to measure the actual 15 Dec → pre-release window: `dec_to_prerelease_window.py` does so (close on 15 Dec to the close before the reaction day, 39–48 sessions): excess +43.9 (2020/21, IPO window), +17.3, +22.3, −3.1, +6.5, −10.5; ex-IPO **mean +6.5%, median +6.5, sd 12.3, 3 of 5 positive** (raw +7.8%). In part: the audit's default was to remove the increment ("this alone lowers the decomposition median $162.83 → $159.64" — reproduced as the "no pre-release seasonal" row, $162.3 on the revision-2 base); revision 2 instead carries 25% of the measured ex-IPO window (+1.5%), separated from the earnings day, with the "none" and "half" rows beside it, because the measured window is positive in three of five years and the shrinkage is now stated consistently. Effect vs revision 1: −$0.8 on the S03 decomposition median.

### A07-13 (major, S02/S03) — crash evidence understated the tails and misidentified the episode: accepted
Reproduced from the merged close series: worst 63-session return since 2023 −29.28% (start 7 May 2024; revision 1 said −18%), all-history p1 −40.82% (said ≈ −33%), minimum −48.7% (30 Mar 2022); 19 overlapping 63-session windows ≤ −40% (18 at ≤ −40.3%), all starting 16 Feb–14 Apr 2022; 103 sessions: 11 windows ≤ −40%, worst −47.67% from 16 Feb 2022 (revision 1 named Sep–Dec 2022 plus May 2023). Added: no 63-session window ≥ +55% (max +54.9% from the IPO week; 2023+ +43.7%); one 103-session window ≥ +55% (from 27 Mar 2026). Claims 10 and 22 and both § 6 bound-mass paragraphs rewritten, with overlapping windows distinguished from episodes (one episode in each horizon). The bound masses now come from the revised models (S02 0.5% / 0.7%, S03 2.1% / 2.9%) and the text says they are model tails, not measured frequencies.

### A07-14 (major, S02/S03) — the ladder does not produce the branch medians; parameter flexibility undisclosed: accepted
Reproduced: `E_repricing_ladder.csv` holds the team pivot $167.02 and ex-NA cases $166.21 / $164.39; no calculation in the model maps them to $181 / $168 / $166 / $153. Claim 13 relabels the ladder a qualitative cross-check (its ±2–3% fundamental range brackets the branch drifts); S02 log § 9 discloses the model's 22 judgment settings (four day-1 means, four post drifts, four mid drifts, four Feb means, background vol, pre-release window, chase, stale refresh, residual sd, blend weight, the shrink on the day-1 means) against the measured or externally fixed inputs (branch probabilities, within-branch sd by the variance identity, drift, sessions, tape betas, known lags, bases, gate). Revision 1's "24 branch settings" is now 20 (the within-branch sd is solved, not set).

### A07-15 (minor, all three) — session accounting: accepted
Reproduced: exclusive-start/inclusive-end counts 16 Sep → 5 Nov 36, 6 Nov → 15 Dec 26, 15 Dec → 11 Feb 39; revision 1's 35 + 1 + 27 and 35 + 1 + 27 + 39 + 1 had the right totals with one diffusion session on the wrong side of the print. Revision 2 uses 36 / 26 / 39; S04's blocks are 21 + 15 + 26; the S03 convention (6) no longer calls itself one session short. Numerical effect on S02/S03: < $0.2.

### A07-16 (minor, S04) — threshold conventions: accepted
Reproduced: exact MS-adjusted log threshold ln(176.8 / 183.21875) = −0.035662; daily hit rates 346/1,366 = 25.33%, 150/863 = 17.38%, 104/613 = 16.97% (revision 1's −0.035: 351 / 153 / 107). Claim 29 now carries the exact-gate rates, the feed-as-is gate (−0.02796: 29.4 / 21.8 / 18.1%), the −36/+26 print windows on the simple gate −3.5033% (6/21, 3/13, 2/9) and the overlapping-observation caveat. Base-rate estimate unchanged at 0.22.

### A07-17 (minor, S02/S03) — inconsistent drift conventions; the within-branch sd did not reproduce S01's 9.5%: accepted
Reproduced: the four branch means contribute variance 0.00170475 (revision-1 weights), so 9% within branch gives 9.90% unconditional and 8.556% is needed for 9.5%; and the decomposition used 3% as the total drift while the anchor added 3% above a forward already carrying 3.97%. Fix: one convention, total expected return 6.97% (3.97% cash + 3% premium) in the diffusion and in the anchor shift (the same total Astra used); the within-branch sd is solved from the variance identity at run time (8.45% with the revision-2 weights and means, between-branch sd 4.34%) so the unconditional day-1 sd is S01's 9.5%. Effect: +$1.6 on the S02 decomposition median from the drift convention; the wider event sd adds ~0.01 to P(≤150).

### Closing note on C01/C02 vintages: accepted
Claim 12 labels the C01/C02 values as the revision-1 vintage the batch conditioned on and records that C01 is now revision 2 (0.72, same $3,100M median guide). The branch weights no longer depend on C01 directly (S01's P(guide below | decel) 0.78 is used), so no re-run was needed.

## Re-run with the adopted print-state weights and R14's February event

The orchestrator's inputs that landed after the revision-1 forecast were applied inside `abnb_path_mixture_v2.py` and their effects isolated in `sensitivity_v2.csv` (decomposition level, revision-2 base):

| Input | Setting used | S02 median / P(≤150) | S03 median / P(≤150) / P(≥180) | S04 |
|---|---|---|---|---|
| Revision-1 print weights (0.24 / 0.14 / 0.10 / 0.52) | sensitivity row | $161.9 / 0.33 | $163.1 / 0.36 / 0.34 | 0.31 |
| **R01/R02/S01 weights (0.32 / 0.10 / 0.13 / 0.45)** | **base** | **$163.1 / 0.32** | **$164.7 / 0.35 / 0.35** | **0.30** |
| Revision-1 February means (+4.0 / +2.5 / +2.5 / +2.0; unconditional +2.6%) | sensitivity row | — | $168.0 / 0.31 / 0.39 | — |
| **R14-mapped February means (+2.5 / +1.0 / +0.5 / −0.5; unconditional +0.7%, P(≥ +5%) 0.32)** | **base** | — | **$164.7 / 0.35 / 0.35** | — |

So the adopted weights lift the S02 decomposition median $1.1 and cut P(≤150) by 0.014; R14's event lowers the S03 decomposition median $3.3 and lifts P(≤150) by 0.04. S04 falls 0.015 on the weights alone. R16 (4Q26 mean ~8.3) and F02 (1Q27 guide +9.4% vs Street +11–12.4%) enter through R14's construction and are not applied twice; R12 is a marker of the print branch and does not enter the price path. The mapping of R14's unconditional distribution onto the four 5 Nov branches is a judgment (R14 conditions on the 4Q26 sign, not the 5 Nov branch); its unconditional mean and P(≥ +5%) match R14 to 0.02.

## What the audit missed

1. **The anchor's median is not the ATM-lognormal's.** Once the smile is fitted with a valid density, the risk-neutral median sits at the forward ($169.3), $3 above the lognormal median revision 1 and the audit both used as "the market's centre"; the market's implied centre was understated in both. This is the reason the revision-2 S02 median is $2.6 above Astra's, and it is a property of the quotes, not a judgment.
2. **The hybrid equation is testable on history, and it is under-sized.** The audit asked for its residual and did not compute it; on 21 windows it is 5.2% (not 3.5, not 6.68) and the realised-on-predicted slope is 1.25 — the tape chases price about a quarter harder than the D betas say. The 2023+ betas row (0.32) is the model's own version of that correction.
3. **The measured pre-release window exists and is positive three years in five.** The audit's default of removing the seasonal is one defensible reading; the other is the 25%-shrunk measured window, and the difference between them is $1.6 on the S03 median — inside the run-to-run noise of the blend but worth stating rather than defaulting.
4. **The February event's own mean was the larger S03 error.** The audit repaired the anchor's variance and the seasonal but accepted +2.6% as the February reaction mean; R14's conditional construction (4Q26 sign, 1Q27 guide vs Street) puts it at +0.8%, which is worth −$3.3 on the S03 decomposition — more than any single finding.
5. **The S04 day-1 conditionals are model outputs, not base-rate quotes.** The monitoring rule's "0.55–0.65" was a reading of the (mis-stated) 4-of-6 record; the model itself gives 0.57 given day-1 ≤ −8% and 0.08 given ≥ +5%, which is the number to update to. The audit corrected the record but not the rule's source.
6. **R12 inherits S04's P(T ≥ 190).** Revision 2 moves it 0.25 → 0.32 (wider residual, accel-heavier weights); R12's repo prior should be refreshed at its own revision.

## Reconciliation with Astra's numbers

| Object | Revision 2 | Astra | Gap | Decision |
|---|---|---|---|---|
| S02 median | $166 | $163 | +$2.6 | Hold. The decompositions agree ($163.1 vs $163.2); the gap is the 0.35 weight on an anchor whose valid-density median is $170.6 rather than the lognormal's $168.6. Inside one percentile band. |
| S02 P(≤150) / P(≤143) / P(≥180) | 0.30 / 0.22 / 0.32 | 0.32 / 0.23 / 0.29 | ≤ 0.03 | Hold; same reason. |
| S03 median | $166 | $167 | −$1 | Hold. Astra's two symmetric events with no drift or seasonal land $1 above; the print-view drift on the base branch (−2%) and R14's February event (+0.7%) net to about that. |
| S03 thresholds | 0.34 / 0.27 / 0.37 | 0.32 / 0.25 / 0.38 | ≤ 0.02 | Hold. |
| S04 | 0.30 (0.20–0.42) | 0.33 (0.20–0.45) | −0.03 | Hold. The two constructions differ by two named terms: the measured +2.1% lag-2 term of the August rally (Astra's equation has no lag structure; without it this model gives 0.33) and the +0.5% stale-refresh judgment (without it 0.32). Astra's 8.3% sd also stacks the 6.68% two-regressor residual on top of the price uncertainty that residual was estimated with. |

No object differs from Astra by more than one percentile band at the median or by more than 0.10 on a threshold, so no compression was required; each gap is named above.

## Reproduction output

`py -3.13 -B docs/pitch-forecasts/audits/A07-reproduce.py` from the repo root, 2026-09-17 (no edits to the script; full output in `A07-reproduce.stdout.txt`). Key lines:

```
price_return_63_all {'n': 1384, 'mean': 1.1479, 'sd_sample': 17.1364, 'median': 0.6587, 'positive': 706}
thresholds {'le150': 0.25, 'le143': 0.1756, 'ge180': 0.3620, 'minimum': -48.6955, 'minimum_start': '2022-03-30', 'overlapping_windows_le_minus40': 19}
price_return_63_starts_2023plus {'n': 866, 'mean': 3.4643, 'sd_sample': 13.8080, 'median': 2.4954} ... 'minimum': -29.2848, 'minimum_start': '2024-05-07'
price_return_103_all {'n': 1344, ...} thresholds {... 'minimum': -47.6693, 'minimum_start': '2022-02-16', 'overlapping_windows_le_minus40': 11}
annualized_vol 2023plus {'all_pct': 37.82, 'excluding_prints_pct': 33.60}; 2024plus {36.10, 31.53}
abnb_1d_pct {'n': 23, 'mean': 1.1565, 'sd_sample': 9.0390, 'median': 0.7, 'positive': 13}; rms 8.9156
February_raw {'n': 6, 'mean': 7.9333, 'sd_sample': 6.6812, 'median': 8.95, 'positive': 5}
guide_below_lower_raw {'n': 5, 'mean': -8.0, 'median': -10.9}
sign_2023Q1_-1_excess {'n': 8, 'mean': -5.5889, 'positive': 0}; sign_2023Q1_1_excess {'n': 5, 'mean': 6.0379, 'positive': 4}
sign_2023Q1_1_paired_cumulative_difference {'n': 5, 'mean': -0.6130}; old_accelerating_paired_difference {'n': 4, 'mean': -2.125}
drift_all_legacy20 {'n': 23, 'mean': -3.7500}; drift_all_proper20 {'n': 23, 'mean': -3.1201}; drift_all_proper27 {'n': 22, 'mean': -2.3362}
drift_W1_proper20 {'n': 14, 'mean': -0.8592}; drift_W1_proper27 {'n': 13, 'mean': 0.9748}
drift_W2_proper20 {'n': 10, 'mean': -1.9177}; drift_W2_proper27 {'n': 9, 'mean': -1.2502}
drift_day1_up_proper20 {'n': 11, 'mean': -5.9903}; drift_day1_down_proper20 {'n': 12, 'mean': -0.4891}
calendar_month_1 {'n': 6, 'mean': 6.8610}; calendar_month_2 {'n': 6, 'mean': 7.6674, 'positive': 6}; calendar_month_11 {'n': 5, 'mean': -5.0544, 'positive': 0}
live_tape {'n': 32, 'mean': 181.8125, 'median': 182.5, 'MS_adjusted_mean': 183.21875, 'oldest': '2026-02-13'}
target_daily_rate (exact -0.035662): all 346/1366 = 0.2533; 2023plus 150/863 = 0.1738; 2024plus 104/613 = 0.1697
target_print_windows all {'n': 22, 'hits_simple_le_minus3_5': 6, 'ols': ([-0.0848, 0.0968, 0.4048], 6.6768, 0.3097)}; W1 n 13 hits 3 resid 5.9224; W2 n 9 hits 2 resid 6.8642
target_chase all 1366 ([0.00048, 0.07396, 0.12809, 0.09535], 0.0322, 0.2344); 2023plus 926 ([0.0017, 0.1414, 0.1914, 0.1039], ...)
print_target_changes down 5%+ {'n': 6, 'mean20': -3.8331, 'any_cut': 4, 'cut_ge3_8': 3}: 2022Q3 -7.62, 2023Q1 -6.45, 2024Q1 +1.66, 2024Q2 -14.07, 2024Q3 +3.51, 2025Q2 -0.02
reviews_revintaging: v1 0.6832; a (literal) 0.8410; b (103-market) 0.7566; c (estimate) 0.7125
sessions 2026-09-16 -> 2026-11-05: 36; 2026-11-06 -> 2026-12-15: 26; 2026-12-15 -> 2027-02-11: 39; totals 63 / 103
actual_lognormal_anchor S02 168.5726 {'100': 0.00239, '143': 0.1870, '150': 0.2641, '180': 0.6385}; S03 169.4836 {'100': 0.01415, '143': 0.2400, '150': 0.3059, '180': 0.5988}
saved_final_CDF_at_thresholds S02 [100: 0.00317, 143: 0.2395, 150: 0.3316, 180: 0.7231]; S03 [100: 0.01545, 143: 0.2682, 150: 0.3400, 180: 0.6456]
February_event_corrected_log_sd 0.25078
negative_RND_mass 2026-12-15 0.015382; 2027-02-12 0.004750
independent_price S02 {50: 163.2047, CDF 143: 0.2287, 150: 0.3176, 180: 0.7091}; S03 {50: 167.3733, CDF 143: 0.2493, 150: 0.3188, 180: 0.6227}
independent_S04 {'target_change_mean_pct': -1.2763, 'sd_pct': 8.3372, 'required': -3.5033, 'model_p': 0.3947, 'outside_p': 0.2023, 'final_p': 0.3306}
```

Revision-2 model runs (not in the audit's script): `implied_dist_v2.py` (mixture fits, negative-mass diagnostic 0.015382 / 0.004750 — identical to the audit's), `abnb_path_mixture_v2.py` (seed 20260917, n 400,000: S02 decomposition median 163.07, 0.320 / 0.232 / 0.288; S03 164.73, 0.346 / 0.275 / 0.354; S04 0.29862; within-branch sd 8.4511), `final_blend_v2.py` (S02 165.60, 0.3019 / 0.2224 / 0.3164; S03 166.39, 0.3383 / 0.2713 / 0.3732), `target_base_rates_v2.py` (hybrid residual sd 5.214 / 4.256 / 4.703), `dec_to_prerelease_window.py` (ex-IPO mean excess +6.50, n 5).

## Final table

| Question | Object | Revision 1 | Astra | Revision 2 | Anchor | \|final − anchor\| |
|---|---|---:|---:|---:|---:|---:|
| S02 | median (USD) | 162 | 163 | **166** | 170.6 (real-world mixture RND; 169.3 risk-neutral) | 5.0 |
| S02 | P(≤ $150) | 0.33 | 0.32 | **0.30** | 0.27 | 0.03 |
| S02 | P(≤ $143) | 0.24 | 0.23 | **0.22** | 0.21 | 0.02 |
| S02 | P(≥ $180) | 0.28 | 0.29 | **0.32** | 0.37 | 0.05 |
| S03 | median (USD) | 165 | 167 | **166** | 169.9 (real-world, event-corrected; 167.8 risk-neutral) | 3.5 |
| S03 | P(≤ $150) | 0.34 | 0.32 | **0.34** | 0.32 | 0.01 |
| S03 | P(≤ $143) | 0.27 | 0.25 | **0.27** | 0.26 | 0.01 |
| S03 | P(≥ $180) | 0.35 | 0.38 | **0.37** | 0.41 | 0.04 |
| S04 | P(mean target ≤ $176.80 on 15 Dec) | 0.29 | 0.33 | **0.30** | 0.50 (non-independent repo prior; no market anchor exists) | 0.20 |

S02 percentiles (5/10/25/50/75/90/95): 121 / 129 / 146 / 166 / 186 / 207 / 221. S03: 110 / 121 / 141 / 166 / 195 / 224 / 244.
