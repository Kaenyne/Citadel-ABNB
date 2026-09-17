# Response to audit A13 (R12 risk-sellside-upgrades, R13 risk-short-interest-crowding, R14 risk-feb-print-up-day)

Response date: 2026-09-17
Responds to: `A13-research-audit.md` (independent Opus auditor standing in for Codex, read-only; 25 findings, 3 critical, 10 major, 12 minor)
Revised research: `questions/risk-sellside-upgrades/research-log.md`, `questions/risk-short-interest-crowding/research-log.md`, `questions/risk-feb-print-up-day/research-log.md` (all revision 2)
Revised forecasts: each question's `forecasts/2026-09-17-forecast.json` (revision 2)
Revised models: `datasets/r12_model_v2.py`, `datasets/r13_model_v2.py`, `datasets/r14_model_v2.py` (revision-1 scripts and outputs untouched as the audit trail; each v2 script prints a bridge from the revision-1 number)
Reproduction script: `A13-reproduce.py` (the audit's script, saved from the audit file; one fix — the trailing markdown fence that had been copied into the file was removed; output in `A13-reproduce.stdout.txt` and at the end of this file)

## Summary

Twenty-five findings: 21 accepted, 4 accepted in part, none rejected. Every number in the audit reproduced (the script ran clean from the repo root with `py -3.13 -B` in about four minutes; every revision-1 file figure it quotes matches to the stated ±0.005). The auditor's three independent numbers were each rebuilt in this model's own scripts and land within a point: R12 0.47 vs 0.47, R13 0.02 vs 0.02, R14 0.26 vs 0.26. The three critical findings were all right, and two of them were the same mistake — R12 and R14 were built on superseded sibling inputs (S02/S04 revision 1; F02 revision 1) — while the third (R14's one-sided impact line) was a construction error that made an immaterial item look like the run's largest risk.

Headline numbers, revision 1 → revision 2:
- **R12** 0.42 (0.30–0.55) → **0.47 (0.34–0.60)** on the any-day reading; 0.43 on the 15 Dec reading, now published alongside. Bridge: revision-1 parameters 0.431 → S02/S04 revision-2 parameters 0.504 → B11's feed capture 0.85 → 0.478 → post-print means moved halfway to the empirical record 0.469. Anchor 0.25 → 0.32 (S04 revision 2), flagged not independent. Impact unchanged in substance: direct +$1.5, EV $0.7, immaterial; marker +$14.5 (not additive).
- **R13** 0.03 (0.01–0.08) → **0.02 (0.005–0.06)**. The decomposition is restated as it should have been: internally consistent model 0.005 (0.009 with the maximum overlay) + structural-event allowance 0.008 + resolver-basis residual ≈ 0.007 + other residuals 0.002 = 0.022. The revision-1 "0.03" was the jump term double-counting the September-2023 episode plus the overlay at the maximum of six observations. EV $0.09 → $0.02, immaterial.
- **R14** 0.30 (0.20–0.42) → **0.26 (0.17–0.37)**. Bridge: revision 1 0.258 → ex-Q4 cells with the leave-one-out Q4 premium 0.205 → F02 revision 2's P(guide ≥ Street) 0.45 → 0.225; final = 0.50 × 0.225 + 0.35 × options anchor 0.274 + 0.15 × corrected base rate 0.36. The impact table is now two-sided: additive operating carry +$1.5, EV $0.4, immaterial as a standalone line; the ±$17 price tail is reported unpriced as S03's object; the "+$17.8 / EV $5.3 / Material" line is withdrawn. The item stays material as an exit-timing statement.

What did not change: R12's feed work and live-target arithmetic, R13's series construction and structural argument, R14's record correction and options work — the audit confirmed all of them and they carry through unchanged.

## Finding-by-finding

### A13-01 (critical, R12) — model built on the revision-1 S02/S04 parameters: accepted
Reproduced: the audit's rebuild gives 0.4288 / 0.4632 / 0.4614 / 0.5050 for the four steps; this model's `r12_model_v2.py` bridge rows give 0.431 (revision-1 set) and 0.504 (revision-2 set), and its 15 Dec target reading is 0.3168 against S04 revision 2's published 0.32, its P(T ≤ 176.8) 0.298 against S04's 0.299. The whole model now runs on `abnb_path_mixture_v2.py`'s PARAMS (weights 0.32/0.10/0.13/0.45, within-branch day-1 sd 8.45 from the variance identity, drifts −1.5/−0.5/−0.5/−1.0, 36/26 sessions, 30% vol, 6.97% drift, tape residual sd 5.0%, p1 = 21 of 36 sessions). Claim 6 rewritten; the revision-1 parameter set is kept as the first sensitivity row so the bridge is visible.

### A13-02 (critical, R14) — one-sided impact line: accepted
Reproduced from the model draws: revision 1's up tail 0.2574 × 10.84 = +2.79 points against the down tail 0.2709 × (−10.66) = −2.89 points, netting to the mean; on the revision-2 draws +2.4 vs −3.2, netting to −0.9. The "+$17.8, EV $5.3, Material" line was E[r | Yes] − E[r] and is mechanically positive for any upper tail; withdrawn. §9 is now split the way R12 and B11 already do it: the additive part is the operating carry the up-day selects (+0.1pt of 4Q26 nights, +$4M of 4Q26 revenue, ≈ +$40M of FY27 revenue re-derived against F02 revision 2, +0.1pp FY27 margin, +$0.02 EPS, ≈ +$1.5/share; EV 0.26 × 1.5 ≈ $0.4, immaterial as a standalone line); the two-way tail (0.26 × +10.9% against 0.30 × −10.7% on a ~$163 pre-print price) is reported separately and unpriced because it is inside S03 revision 2's 12 Feb distribution. The exit-timing sentence stays and is the item's materiality: the memo should delete the $5.3 and say the February leg is a coin-flip on sign with a 0.26 chance of a ≥5% up day and a 0.30 chance of a ≥5% down day.

### A13-03 (critical, R14) — Q4 premium added to cells that already contain the Q4 prints: accepted
Reproduced: `s01_cells.csv` puts 4Q25 in "accel & at/above" (n 3), 4Q24 in "accel & below" (n 3), 4Q22 and 4Q23 in "decel & at/above" (n 5); the ex-Q4 means are aa +8.85, ab −8.35, fl −8.7, da −2.60, db −7.55 and the four Q4 deviations from them are +16.0, +0.9, +22.75, −4.25, mean +8.85 (the audit's block prints exactly these). The revision-2 model uses the ex-Q4 cells with the leave-one-out premium at the log's own 30% (+2.66): 0.2053 with p_guide 0.33 (audit 0.2027), and the auditor's equivalent (full cells + 1.7) gives 0.238 at p_guide 0.45. The §7 bracket is now 0.15 (none) – 0.29 (50%) – 0.51 (full), not 0.16–0.59, and claim 4 records the cell membership and the leave-one-out arithmetic. The remaining judgement — 30% of an n-4 post-hoc premium — is unchanged and is the log's load-bearing choice, stated as such in RESUME.

### A13-04 (major, R14) — F02 at revision 2, P(guide ≥ Street) ≈ 0.45: accepted
Reproduced: interpolating F02 revision 2's table (p50 10.5, p75 12.8) at the gap-adjusted 11.0 gives 0.446; a normal on its mean/sd (10.6, 3.4) gives 0.453. Set to 0.45; F01 re-cited at 0.28. Alone on the revision-1 cells it lifts the model to 0.288 (audit 0.2837); with A13-03 the two land at 0.225 (audit 0.2212). The log now says plainly that revision 1's 0.257 was the average of two errors of opposite sign.

### A13-05 (major, R14) — "3 of 14" is 2 of 14: accepted in part
Reproduced from `abnb_earnings_reactions.csv` and `r14_base_rates.json` (`post2022_ge5_raw` 2): only 4Q24 and 2Q26 clear +5% since 1Q23 → 2 of 14 = 0.143, Laplace 0.188. Claim 1 and the JSON corrected. In part: the base-rate blend. Revision 1's §5 was 0.5 × 0.50 + 0.5 × 0.26 (the all-print rate), so the miscount did not enter the arithmetic; the auditor's 0.345 replaces the all-print class with the post-2022 Laplace. Revision 2 takes the other half as the mean of the two classes (0.26 and 0.19 → 0.22): 0.5 × 0.50 + 0.5 × 0.22 = 0.36. The difference to the auditor's 0.345 is worth 0.002 on the final at the 0.15 weight.

### A13-06 (major, R12) — no feed-capture term while B11 uses 0.85: accepted
Reproduced: B11's JSON `model.structure` carries "feed capture 0.85" and its sensitivity row (1.0 → 0.19, 0.70 → 0.11); R12 revision 1 named the risk in pre-mortem item (4) and priced it at 1.0. Revision 2 adopts **0.85 on every modelled count** as the single convention for the two feed questions, written into R12 convention (6) and claim 10 (0.504 → 0.478; audit 0.4766). The convention is stated with its caveat: the historical rates that set the means are themselves feed counts, so thinning them again is a ~2–3-point conservatism toward No, not a measured correction, and capture 1.0 is the sensitivity row (0.49). The same wording should go into B11 at its revision 2 (batch A17, still revision 1), where the same double-thin applies.

### A13-07 (major, R12) — post-print means 1.6–1.8× the empirical print-window record: accepted in part
Reproduced from `upgrade_base_rates.json` (`upgrades_to_buy.print_windows`, 2023+): post-print to-Buy counts 8 in 15 windows, mean 0.53; by day-1 sign up 1.67 (1, 2, 2), down 0.20 (0, 1, 0, 0, 0), small 0.29; the audit's rerun with 1.67/0.9/0.5/0.2 and capture 0.85 gives 0.4612 and this model 0.459. In part: revision 2 moves to the **midpoint** 1.8 / 0.9 / 0.6 / 0.3 (0.469) rather than the empirical means, with the justification the auditor asked for: the 2026 regime (three prints, post counts 2 / 0 / 2 on day-1 moves +4.6 / +0.7 / +17.4; 8 to-Buy upgrades YTD, 4 within 5 days of a print) supports a lift on the up and small branches, but no 2026 print was a down print, so the lift on the decelerating branches has no evidence and is halved. The empirical means, ×1.5 and halved are all sensitivity rows (0.46 / 0.51 / 0.43); the honest model range on revision-2 inputs is 0.46–0.50, as the audit says.

### A13-08 (major, R13) — jump term double-counts the September-2023 episode: accepted
Reproduced: with the two residuals of |r| ≥ 0.75 removed (n 97, sd 0.2488 vs 0.3072), the jump model falls from 0.018 to 0.004 (audit 0.0181 → 0.0041); with the revision-1 overlay (0.70 at 0.41) on the clean pool 0.0093 (audit 0.0095). `r13_model_v2.py` uses the clean pool whenever the jump term is on, keeps the full-pool construction as the "double count" sensitivity row, and §5 now states the decomposition as model + a separate structural allowance (A13-25). The two residuals in this fit are +0.97 and +1.52 (the audit quotes +0.80 / +1.17; same two steps, same removal rule).

### A13-09 (major, R13) — overlay at the maximum, not the mean: accepted
Reproduced from `si_after_prints.csv`: the six post-down-print rises are +0.68, +0.70, −0.32, +0.51, +0.06, +0.44 → mean +0.345, median +0.475, max +0.70. The central overlay is now +0.35 (model 0.0054 on the clean pool); +0.70 (0.009) and +1.5 (0.036) are the sensitivity rows. The audit also missed that the overlay probability was S01 revision 1's 0.41; revision 2 uses S01 revision 2's P(day-1 ≤ −5%) = 0.38 (0.41 gives 0.0060).

### A13-10 (major, R12) — any-day leg assumes perfect rank correlation; all-history ratio mis-stated: accepted
Reproduced by the audit's script on `D_target_panel_daily.csv` (n_targets ≥ 10, log mean target, 63-session windows, threshold +3.70%): all history P(end) 0.3719 / P(max) 0.4407 / ratio 1.185 (revision 1 had 0.353 / 0.429 / 1.22); 2023+ 0.4403 / 0.4902 / 1.113 (matches). Claim 5 corrected. The ratio 1.15 is kept, the rank-preserving assumption and the tail growth of the running-max premium are stated in §4, the leg's honest range 0.317 (15 Dec) – 0.364 (any-day) – ≈0.40 (three-checkpoint) is named, and the interval widens to 0.34–0.60 to hold it. The 35-session all-history ratio is 1.099 and the 2023+ 1.017, both also in the reproduction output.

### A13-11 (major, R14) — §6 coherence text stale by one revision: accepted
Reproduced: S03 revision 2's `feb_print_event` carries R14 revision 1's object (branch means +2.5/+1.0/+0.5/−0.5, model P(≥+5%) 0.32, mean +0.7, sd 9.0) and its first sensitivity row prices the mapping (zero means → 12 Feb decomposition median $163.5 vs $165). R14's §6 and claim 8 are rewritten against revision 2: R14 revision 2 (0.26, model mean −0.9, ≈ −0.3 with the pull) would take S03's branch means down about 1 point, worth ≈ −$1 to −$1.5 on the 12 Feb median and ±0.01 on the thresholds; the "do not re-run S03" instruction is withdrawn and the decision is left to the orchestrator at X01 time. S03 is not edited here.

### A13-12 (major, R12) — "with prints inside 0.22 / 0.26" are the all-window figures: accepted
Reproduced: 35-session windows, all 0.2181 / 0.2604 (2023+); with a print inside n 817, 0.3586; with no print n 577, 0.0191, mean −0.26%, sd 2.08%. Claim 5 now reads "with a print inside: 0.359 (n 817)"; the claim's conclusion (the tape moves ≥3.7% almost only through prints) is stronger.

### A13-13 (minor, R12) — anchor stale and not independent: accepted
Anchor re-set to S04 revision 2's P(T ≥ 190 on 15 Dec) = 0.32 and flagged NOT_INDEPENDENTLY_DERIVED in §5 and the JSON (`anchor_independent: false`), with the model's own 15 Dec reading (0.317) shown beside it. |final − anchor| +0.15 is justified by construction (the anchor omits the upgrades leg, +0.10, and the any-day reading, +0.05), which is stated as such rather than as information the anchor lacks.

### A13-14 (minor, R12) — 14 values printed for 15 prints: accepted
Reproduced from the JSON: 1, 0, 0, 0, 0, 2, 0, 0, 2, 1, 0, 0, 4, 2, 2 (sum 14, mean 0.933, P(≥3) 1/15). Claim 2 prints the 15-value series and adds the post-print counts by day-1 sign that A13-07 uses.

### A13-15 (minor, R12) — tape dated 16 Sep, data are 11–12 Sep: accepted
Reproduced: the panel ends 2026-09-11 (mean 181.8125, n 32); the live-target file is dated 12 Sep with Morgan Stanley at $125, so the $170 re-initiation gives 183.21875 and +3.70%. Claim 3 dated 11–12 Sep with the 16 Sep Morgan Stanley action separately.

### A13-16 (minor, R14) — event sd used as the residual, total sd above the target: accepted in part
Reproduced: revision 1's total sd 9.09 at residual 8.5 (audit 9.089), and the term-structure identity 11.15 / 9.46 / 8.47 / 6.77. In part: on the revision-2 construction the cell dispersion is 2.8 and the total is **9.04** at the same 8.5 residual, i.e. the object it is meant to match, so the residual is kept rather than solved down to 8.0 (which would put the total at 8.6, below the central event sd). Claim 7 now reports the total sd against the event sd, and 8.0 / 9.5 are sensitivity rows (0.21 / 0.24).

### A13-17 (minor, R14) — superseded nights band: accepted
The model now draws 3Q26 from the A09 revision-2 adopted object N(9.5, 1.70) (`adopted_print_states_v2.json`; the audit cited R01 revision 2's N(9.67, 1.70), which the adopted file supersedes) and 4Q26 from the F01/F02 revision-2 V1 conditional 8.1 + 0.5(Q3 − 9.5) + N(0, 1.4) with the 12% tail. Immaterial, as the audit said: 0.222 at N(9.67, 1.70), 0.225 here; P(accel) 0.12 → 0.14 because the conditional construction gives the sign difference a slightly wider spread.

### A13-18 (minor, R14) — FY27 revenue line derived against F02 revision 1: accepted
Re-derived: P(guide ≥ Street | up) 0.63 vs 0.45 (revision 2 draws); on F02 revision 2's N(10.6, 3.4) the conditional means above and below the 11.0 bar are 13.6 and 8.1, so the +0.18 shift is ≈ +1.0pt on the 1Q27 guide midpoint ≈ +$26M; carry-through to FY27 at ~40% persistence of the Q1 delta ≈ +0.25pt of FY27 growth ≈ +$40M, with the persistence stated as a judgement (none +$26M, full +$105M) and the row labelled reverse-causal. The auditor's ≈ +$30M is inside that range; either way ≈ $0.3–0.5/share.

### A13-19 (minor, R13) — denominator is a weighted-average count: accepted
Reproduced: `abnb_capital_return_quarterly.csv` 2Q26 `basic_wa_shares_m` 592.0; yfinance `impliedSharesOutstanding` 598,785,682 → threshold 29.94m shares (×2.104), latest 2.376%. Convention (3), claim 1 and the JSON describe the denominator as the repo file's basic weighted-average count and record the outstanding-count alternative; no change to the answer.

### A13-20 (minor, R13) — 3.44% vs 3.51% on the same float: accepted
Reproduced: 14,228,547 / 405,782,346 = 3.506%; yfinance's `shortPercentOfFloat` 0.0344 is not reproducible from its own `sharesShort` and `floatShares`. Claim 1 quotes the computed 3.51% and says the 3.44% field is not used.

### A13-21 (minor, R13) — two stock numbers and a revision-1 branch weight: accepted
§9 now carries one figure: +$1/share branch-weighted (2–3 points ≈ +$3–5 on the accelerating branch, S02 revision 2 weight 0.32), EV 0.02 × $1 = $0.02 ($0.06 on the accelerating branch alone); the borrow-cost/recall sentence leads the row. Verdict unchanged (immaterial).

### A13-22 (minor, R12) — marker computed on revision-1 parameters: accepted
Rebuilt: E[15 Dec | Yes] $179.9 vs $165.5 = +$14.5 (median +$15.0; audit +$14.2 with capture, +$12.9 without); EV-as-marker $6.8 (P rose more than the spread narrowed). Direct effect and verdict unchanged.

### A13-23 (minor, R14) — C's disclaimer and the overlap with p_guide_ge: accepted in part
C §10 item 3 ("a reading, not a result") is now quoted in claim 3 where the premium is used, and §4 states why the guide-vs-Street penalty and the Q4 premium are not both carried at full strength (cells shrunk 35% toward −1.0; premium at 30% of the leave-one-out value, which is itself smaller than the sign-only S1 gap because the cells already condition on the guide). In part: the two are still both carried, because the panel evidence for the guide term (n 8/8, fragile) and for the Q4 residual (n 4, post-hoc) are different objects and the shrink/30% treatment is the discipline for both; the market-neutral row (0.32) shows what dropping the cells entirely does.

### A13-24 (minor, R12) — any-day reading is a live re-reading of the resolution sentence: accepted
Both readings are in `forecasts/2026-09-17-forecast.json` (`final.p` 0.47 any-day, `final.p_dec15_only_reading` 0.43) and in §6; convention (3) now says which reading makes Yes easier and by how much (≈ 5 points on revision-2 parameters); pre-mortem item (6) added; the monitoring row for 2 Oct tells the memo to state which it quotes.

### A13-25 (minor, R13) — the stated derivation is not the one doing the work: accepted
§5 restated: model 0.005 (0.009 with the maximum overlay) + structural-event allowance 0.008 (new convertible/exchangeable ≈ 0.005, stock-component deal or index event ≈ 0.003) = 0.013; §6 adds the resolver-basis residual ≈ 0.007 (≈ 0.03 that the resolver reads the float basis × 0.22) and 0.002 of other residuals → 0.022, quoted as **0.02 (0.005–0.06)**. The extreme-probability gate's floor is no longer holding the number up; the structural allowance and the resolver edge are.

## What the audit missed

1. **S01 revision 2's down-print probability.** R13's overlay was at 0.41 (S01 revision 1's P(≤ −5%)); S01 revision 2 publishes 0.38. Fixed in `r13_model_v2.py` (0.0060 → 0.0054 on the clean pool). The audit's own R13 rebuild carried 0.41.
2. **The A09 revision-2 adopted print states.** `risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json` (S01 states accel 0.261 / flat 0.104 / decel 0.636; R01 0.386, R02 0.260) post-dates S02 revision 2's 0.32/0.10/0.13/0.45, and its rebasing note says S02 should move for coherence ("immaterial"). R12 revision 2 keeps S02 revision 2 as its base (so R12, S02, S03, S04 and B11 share one state vector) and records the A09 states as claim 12 and a sensitivity row (0.452; each −0.06 on P(accel) ≈ −0.017). R14 draws 3Q26 from the adopted object directly. The orchestrator should pick one vector at X01 time; the audit compared R12 only against S02 revision 2.
3. **The feed-measured-means point on capture.** The audit asked for one capture convention but not why 0.85 on feed-measured rates is a double thin. Revision 2 adopts 0.85 for coherence and says what it is (a ~2–3-point conservatism), so B11's revision 2 can carry the same sentence instead of the "counts are lower bounds" framing, which argues for the opposite adjustment.
4. **R14's bridge row for revision 1 needs the correlation.** Reproducing revision 1 exactly requires the independent 4Q26 draw at corr 0.5 (0.258); an uncorrelated override gives 0.274. `r14_model_v2.py` carries the correlation so the bridge is exact; the audit's script re-implements revision 1 correctly and did not need this.
5. **The residual on the revision-2 R14 cells already matches the event sd.** A13-16's proposed fix (solve the residual down to 8.0) was right on the revision-1 cells and wrong on the ex-Q4 cells, whose dispersion is smaller; the audit did not re-check A13-16 after applying A13-03.
6. **The S03 monitoring rows that reference R14.** S03 revision 2's calendar ("R14 owns the February event — re-run it first, then map its branch means here"; 25 Jan "−0.5% on the Feb day-1 means (R14 rule)") already delegates the February object to R14, so the coherence fix is a one-parameter S03 re-run, not a judgement; noted in R14 §6 for the orchestrator.

## Reconciliation with the auditor's numbers

| question | auditor | revision 2 | gap | decision |
|---|---:|---:|---:|---|
| R12 | 0.47 (0.34–0.60) | 0.47 (0.34–0.60) | 0.00 | same number by a slightly different route (midpoint post means 0.469 vs the auditor's midpoint of 0.461–0.477); no asymmetry to name |
| R13 | 0.02 (0.005–0.06) | 0.02 (0.005–0.06) | 0.00 | same; the model part is 0.005 here vs the auditor's 0.0095 because the overlay is the mean (A13-09) and S01 revision 2's 0.38, offset by a slightly larger resolver residual (0.007 vs 0.003) |
| R14 | 0.26 (0.18–0.37) | 0.26 (0.17–0.37) | 0.00 | same weights (0.50 / 0.35 / 0.15); the base rate is 0.36 vs 0.345 (A13-05 in part), worth 0.002 |

No revised number differs from the auditor's by more than a point, so no asymmetry needs to be named. Where the routes differ (R12's post means, R13's overlay, R14's base-rate class) the difference is stated in the finding above and is inside the rounding of the headline.

## Reproduction output

`py -3.13 -B docs/pitch-forecasts/audits/A13-reproduce.py` from the repo root, 2026-09-17 (the only edit to the script: the trailing ``` fence copied from the audit file was removed; no path fix was needed; runtime ≈ 4 minutes):

```
========== R14  day-1 record and the S1 Q4 residual ==========
Q4 day-1 raw: {'2020Q4': 13.3, '2021Q4': 3.6, '2022Q4': 13.4, '2023Q4': -1.7, '2024Q4': 14.4, '2025Q4': 4.6}
Q4: positive 5/6, >=5% 3/6, >=3.5% 5/6, mean 7.933, median 8.95
  all 23           n 23  >=+5% 6  rate 0.261  Laplace 0.280
  3Q22+ (16)       n 16  >=+5% 3  rate 0.188  Laplace 0.222
  post-2022 (14)   n 14  >=+5% 2  rate 0.143  Laplace 0.188
  log/JSON claim post-2022 '3 of 14 (0.21)' -> the file gives 2 of 14
S1 residual: Q4 mean 7.720 (sd 7.537, n 4), non-Q4 -2.567, gap 10.288, Welch t 2.379

========== R14  the Q4 uplift is already inside the S01 cells ==========
  cell aa  full   7.43 (n3)   ex-Q4   8.85 (n2)
  cell ab  full  -0.77 (n3)   ex-Q4  -8.35 (n2)
  cell fl  full  -8.70 (n1)   ex-Q4  -8.70 (n1)
  cell da  full   0.78 (n5)   ex-Q4  -2.60 (n3)
  cell db  full  -7.55 (n4)   ex-Q4  -7.55 (n4)
  Q4 deviations from ex-Q4 cell means: [('4Q25', -4.25), ('4Q24', 22.75), ('4Q22', 16.0), ('4Q23', 0.9)] -> leave-one-out premium 8.85 (the log uses the S1 gap 10.29)

========== R14  Feb event sd from the Jan / Mar 2027 expiries ==========
  background 29.00% -> event sd 11.154%
  background 32.30% -> event sd 9.460%
  background 33.85% -> event sd 8.473%
  background 36.00% -> event sd 6.773%
  anchor at sd 8.5: P(>=+5%) 0.2626 at mode -0.4, 0.2782 at mean 0
  anchor at sd 9.0: P(>=+5%) 0.2743 at mode -0.4, 0.2893 at mean 0
  anchor at sd 9.5: P(>=+5%) 0.2849 at mode -0.4, 0.2993 at mean 0

========== R14  published mixture, and the two corrections ==========
published (full cells, uplift 3.0, p_guide 0.33): {"p_ge5": 0.2571, "p_le_m5": 0.2717, "p_lt0": 0.5126, "mean": -0.1666, "sd": 9.0558, "E_up": 10.7651, "E_dn": -10.6946, "pctiles": {"5": -14.32, "25": -5.54, "50": -0.24, "75": 5.18, "95": 14.15}}
  the file's numpy run: p_ge5 0.2574, mean -0.13, sd 9.09, E[r|>=5] +10.84, E[r|<=-5] -10.66
F02 revision 2 (p_guide 0.45)                   : p_ge5 0.2837
ex-Q4 cells + leave-one-out uplift 8.85 x 0.3   : p_ge5 0.2027
both corrections (auditor mixture)              : {"p_ge5": 0.2212, "p_le_m5": 0.3021, "p_lt0": 0.5566, "mean": -0.9627, "sd": 8.9726, "E_up": 10.7471, "E_dn": -10.724, "pctiles": {"5": -14.91, "25": -6.24, "50": -1.08, "75": 4.22, "95": 13.44}}
  up-tail EV +2.77 pts vs down-tail EV -2.91 pts: they net to the mean (A13-02)

========== R12  feed, live targets, D panel ==========
feed 'up' rows since 2021: 26, to Buy-equivalent: 21
to-Buy by year: {'2021': 5, '2022': 1, '2023': 1, '2024': 2, '2025': 4, '2026': 8}
live targets n 32  mean 181.8125  median 182.5  buckets {'Buy': 22, 'Hold': 8, 'Sell': 2}
Morgan Stanley is in the feed at $125 -> replacing with $170 gives base 183.21875; $190 needs +3.70%
panel n_targets>=10: 1429 rows, 2021-01-04 to 2026-09-11; threshold +3.700%
  63s all n 1366 P(end) 0.3719 P(max) 0.4407 ratio 1.185 | 2023+ n  863 0.4403 / 0.4902 ratio 1.113
      no print in window n   27 P(end) 0.0741 mean -1.072% sd 3.134% | with print n 1339 P(end) 0.3779
  35s all n 1394 P(end) 0.2181 P(max) 0.2396 ratio 1.099 | 2023+ n  891 0.2604 / 0.2649 ratio 1.017
      no print in window n  577 P(end) 0.0191 mean -0.258% sd 2.083% | with print n  817 P(end) 0.3586
  claim 5 reports the 35s 'with prints inside' as 0.22 / 0.26: those are the ALL-window figures

========== R12  published parameters vs the revision-2 parameters of S02 and S04 ==========
  published (S02/S04 revision 1)               P 0.4288 | up 0.2443  T 0.2846 (15 Dec 0.2475) | E[Dec|Yes] 175.6 vs 161.1
  S02 rev2 weights + post drifts               P 0.4632 | up 0.2693  T 0.3132 (15 Dec 0.2723) | E[Dec|Yes] 177.6 vs 163.8
  S04 rev2 tape residual sd 5.0%               P 0.4614 | up 0.2443  T 0.3225 (15 Dec 0.2804) | E[Dec|Yes] 173.4 vs 161.1
  all revision-2 parameters                    P 0.5050 | up 0.2730  T 0.3648 (15 Dec 0.3172) | E[Dec|Yes] 178.5 vs 165.5
  revision-2 + B11 feed capture 0.85           P 0.4766 | up 0.2222  T 0.3640 (15 Dec 0.3165) | E[Dec|Yes] 179.7 vs 165.5
  revision-2 + capture + empirical post means  P 0.4612 | up 0.1870  T 0.3665 (15 Dec 0.3187) | E[Dec|Yes] 180.3 vs 165.5
  the file's numpy run: P 0.4314, up 0.2454, T 0.2861 (15 Dec 0.2488), E[Dec|Yes] 175.7 vs 161.1
  S04 revision 2 publishes P(mean target >= 190 on 15 Dec) = 0.32: the rebuild lands on it

========== R13  series, windows, AR(1), and the jump double count ==========
Nasdaq latest settlement 08/31/2026: 14228547 shares
  on 592.000m shares: 2.4035% of shares; 5% needs 29.600m shares (x2.080 of the latest)
  on 598.786m shares: 2.3762% of shares; 5% needs 29.939m shares (x2.104 of the latest)
MarketBeat reconstruction vs the repo series: n 65, ratio mean 0.9999 sd 0.0009
series n 100, mean 2.764, median 2.605, max 5.438, min 1.477, latest at the 34th percentile
  8-settlement windows all                n 92  P(max>=5) 0.0870  P(max>=4) 0.1848  largest rise 2.34pt
  8-settlement windows prior level < 3.0  n 61  P(max>=5) 0.0000  P(max>=4) 0.0492  largest rise 2.03pt
  8-settlement windows prior level < 2.5  n 42  P(max>=5) 0.0000  P(max>=4) 0.0238  largest rise 2.03pt
  the rise now required is 2.60pt: no window in the series delivers it
  per-step sd 0.3147, 99 steps, rises >= 0.9pt: [0.94, 1.4] (both the Sep 2023 S&P 500 inclusion)
  AR(1) slope 0.9057, intercept 0.2621, long-run mean 2.7792, residual sd 0.3072 (clean pool n 97 sd 0.2488)
  AR(1) only                                     P(max>=5) 0.0055  P(max>=4) 0.0667
  AR(1) + jump 2/99                              P(max>=5) 0.0181  P(max>=4) 0.1278
  AR(1) + jump + down-print overlay (published)  P(max>=5) 0.0316  P(max>=4) 0.1847
  episode shocks removed from the pool, + jump   P(max>=5) 0.0041  P(max>=4) 0.0601
  episode shocks removed, + jump + overlay       P(max>=5) 0.0095  P(max>=4) 0.1044
  the file's numpy run: 0.0051 / 0.0176 / 0.0307 for the first three
exit 0
```

Separately run (this response's own scripts, outputs saved beside each): `r12_model_v2.py` base 0.4685 (bridge rows 0.4309 / 0.5044 / 0.4777 / 0.4594, matching the audit's 0.4288 / 0.5050 / 0.4766 / 0.4612 to the stated tolerance); `r13_model_v2.py` clean-pool jump 0.0040, + mean overlay at 0.38 0.0054, + max overlay 0.0093, full-pool revision-1 construction 0.0307; `r14_model_v2.py` base 0.2249 (bridge: revision-1 construction 0.2579, ex-Q4 + LOO 0.2051, F02 rev 2 alone 0.2881, auditor's full-cells + 1.7 equivalent 0.2377).

## Final table

| question | revision-1 | auditor | revision-2 | anchor | \|final − anchor\| | EV $/share | material |
|---|---|---|---|---|---|---|---|
| R12 P(≥3 to-Buy upgrades or mean target ≥ $190, 17 Sep–15 Dec) | 0.42 (0.30–0.55) | 0.47 (0.34–0.60) | **0.47 (0.34–0.60)** any-day; **0.43** on the 15 Dec reading | 0.32 (S04 rev 2 P(T ≥ 190 on 15 Dec); NOT_INDEPENDENTLY_DERIVED) | 0.15 (construction: upgrades leg +0.10, any-day +0.05) | direct +$1.5 × 0.47 = **$0.7**; marker +$14.5 × 0.47 = $6.8 (not additive) | **No** as a standalone line; marker of the thesis-breaker branch |
| R13 P(short interest ≥ 5.0% of shares at any settlement 30 Sep–15 Jan) | 0.03 (0.01–0.08) | 0.02 (0.005–0.06) | **0.02 (0.005–0.06)**; float basis ≈ 0.22 | ≈ 0.01 (repo prior, no market) | 0.01 | +$1 × 0.02 = **$0.02** | **No**; keep one sentence on borrow cost and recall |
| R14 P(day-1 after the 4Q26 print ≥ +5%) | 0.30 (0.20–0.42) | 0.26 (0.18–0.37) | **0.26 (0.17–0.37)** | 0.27 (options-implied Feb event sd 9.0, symmetric) | 0.01 | additive carry +$1.5 × 0.26 = **$0.4**; two-way tail ±$17 reported unpriced (S03's object) | **No** as an EV line; **yes** as an exit-timing statement (P(< 0) 0.55; 0.26 up ≥5% vs 0.30 down ≥5%) |

**Other question folders carrying S02/S04 revision-1 PARAMS** (grep for the print weights 0.24/0.14/0.10/0.52, `p=0.24`, `resid_sd=0.035` or "residual sd 3.5" across `questions/**` datasets, forecasts and logs):
- `questions/bonus-sellside-downgrades/datasets/b11_model.py` and `forecasts/2026-09-17-forecast.json` — B11 (batch A17, still revision 1) runs on the revision-1 S02 branches (0.24/0.14/0.10/0.52) and price blocks; its revision 2 should rebuild on `abnb_path_mixture_v2.py` PARAMS, keep capture 0.85 with the caveat above, and re-state its marker (E[15 Dec | Yes] vs the revision-2 unconditional $165.5).
- Hits that are not stale: `questions/close-15dec-2026/datasets/abnb_path_mixture.py` (revision 1, kept untouched by rule), `abnb_path_mixture_v2.py` and the S02 / S04 logs (they cite the revision-1 values as superseded history or as a sensitivity row), and R12's own `r12_model.py` / `r12_model_v2.py` / log (revision-1 script kept; revision 2 carries the values only as the bridge row).
- No other folder hard-codes the revision-1 set. The A09 revision-2 adopted print states (accel 0.26) are a separate, newer input that S02 revision 2 itself has not adopted; the orchestrator should pick one state vector for X01 (R12's sensitivity row prices the difference at −0.017).
