# Audit of workstream C: the print reaction function and the 5 Nov breakeven

- **Date:** 12 Sep 2026. Auditor: Claude (audit agent C), for Krishang. Worktree `citadel-abnb-reversedcf`, branch `krish/reverse-dcf`. Nothing committed.
- **Scope:** `research/notes/reverse_dcf/C_reaction-function.md`; `analysis/src/reverse_dcf/C_01_print_panel.py`, `C_02_reaction_tests.py`, `C_03_breakeven.py`; the 15 CSVs under `data/processed/reverse_dcf/C/`.
- **Findings CSV:** `data/processed/reverse_dcf/audit/audit_C_findings.csv`.
- Labels follow the brief: ANCHOR, MEASURED (say which file), JUDGEMENT.

---

## 1. Verdict: PASS WITH FIXES

The three scripts re-run under `py -3.13` and every one of the 15 output CSVs reproduces byte-for-byte. The panel matches its sources on all five prints checked (returns, QQQ alignment, nights growth and acceleration, next-quarter guide vs Street). The 22 guide quotes match the verified guidance ledger verbatim and the four most consequential ones match the letter text. Every headline statistic in the note reproduces from the panel with independent code. The coding judgements are defensible and documented.

The fixes are to the claims, not the numbers. Seven findings are material; none is a blocker. In one sentence: **the printed nights-acceleration sign rule is a re-test of a prior hypothesis on the same prints, it passes the workstream's own pre-stated rule only on the secondary (post-2022, n 14) sample, its "0 of 8" phrasing depends on the QQQ-excess convention (2 of 8 on raw returns), the guide-direction "no effect" is a power statement built on 3 accelerating guides, and the team-base expected reaction of -4% to -8.5% is conditional on a decelerating print when the team's own nowcast band puts 13 to 20% of its mass in the accelerating bucket.** The synthesis should carry the sign rule as a base rate with its two counts, use the sign-only function (S1) for the expected reaction, present the two-variable function (S2) as post-hoc and illustrative, and quote the team-base number as "conditional on a decelerating print, close-to-close, captured only by a pre-print position".

---

## 2. What was checked and reproduced

### 2.1 Re-run (task 1)

| Script | Exit | Outputs changed |
|---|---|---|
| `C_01_print_panel.py` | 0 | none (C_print_panel.csv, C_guide_direction_coding.csv identical) |
| `C_02_reaction_tests.py` | 0 | none (6 files identical, incl. 2,000-shuffle permutation p values; seeded rng 20260912) |
| `C_03_breakeven.py` | 0 | none (7 files identical, incl. 3,000-draw bootstrap; seeded rng 7) |

MEASURED: `cmp` of each CSV against a pre-run snapshot.

### 2.2 Print panel vs sources, five prints (task 2)

| Print | nights y/y, accel pts, sign (panel) | `02_kpi_panel_quarterly` | Day-1 raw / excess (panel) | Recomputed from `09_prices_daily` (ABNB, QQQ) | `abnb_earnings_reactions` | Guide mid / Street / gvs (panel) | `02_guidance_ledger` / `16_consensus_at_print_merged` |
|---|---|---|---|---|---|---|---|
| 4Q21 | 58.53, +29.57, +1 | 58.53, 29.57 | +3.6 / +3.7 | 180.07 to 186.64 = +3.65; QQQ -0.03; excess +3.67 | 3.6 / 3.7 | 1,445 / 1,240 / +16.5% | 1,410-1,480 mid 1,445; 1,240 CNBC unattributed, flagged low confidence |
| 4Q23 | 12.02, -1.52, -1 | 12.02, -1.52 | -1.7 / -2.8 | 150.82 to 148.20 = -1.74; QQQ +1.09; excess -2.83 | -1.7 / -2.8 | 2,050 / 2,030 / +0.99% | 2,030-2,070; LSEG 2,030 |
| 3Q24 | 8.48, -0.21, 0 (dead band) | 8.48, -0.21 | -8.7 / -8.8 | 147.37 to 134.61 = -8.66; QQQ +0.12; excess -8.78 | -8.7 / -8.8 | 2,415 / 2,420 / -0.21% | 2,390-2,440; LSEG 2,420 |
| 4Q25 | 9.82, +1.03, +1 | 9.82, 1.03 | +4.6 / +4.4 | 115.96 to 121.35 = +4.65; QQQ +0.21; excess +4.44 | 4.6 / 4.4 | 2,610 / 2,530 / +3.16% | 2,590-2,630; LSEG 2,530 |
| 2Q26 | 10.34, +1.19, +1 | 10.34, 1.19 | +17.4 / +16.3 | 151.64 to 178.07 = +17.43; QQQ +1.17; excess +16.26 | 17.4 / 16.3 | 4,730 / 4,610 / +2.60% | 4,690-4,770; LSEG 4,610 |

All match. The QQQ adjustment is the arithmetic difference of the same-window close-to-close returns (pre-print close to reaction-session close), taken from `abnb_earnings_reactions.csv`; dates align with `20_executable_returns.csv` (pre_close_date = print date, reaction date = next session) in all five cases. `04_consensus_at_print.csv` and `16_consensus_at_print_merged.csv` agree on every field used. Two things to note: (a) the primary target is the excess return rounded to one decimal in the reactions file (2Q23 is -0.036% in `20_executable_returns.csv` legacy_1d_pct and B's file, stored as -0.0 here); (b) the 4Q21 guide-vs-Street of +16.5% is an unattributed CNBC number the source file itself flags as low confidence, and it enters the "all" sample regressions unwinsorised (see finding 9).

### 2.3 Guide-direction coding (task 3)

All 22 quotes match `02_guidance_ledger.csv` (verified = True) verbatim. Four were checked against the letter HTML in the main tree (`data/raw/letters/4Q24_*`, `2Q26_*`, `4Q25_*`, `1Q23_*`, `3Q24_*`): all verbatim.

Label judgements, 16-print primary sample:

| Print | C's code | Auditor's reading | Agree |
|---|---|---|---|
| 2Q22 stable, 3Q22 decel (-1), 4Q22 decel (-1), 2Q23 accel, 3Q23 decel, 4Q23 decel, 1Q24 stable, 2Q24 decel, 3Q24 accel, 1Q25 decel, 2Q25 stable, 3Q25 decel (bucket 4-6 vs 8.8), 1Q26 decel (-1) | as stated | same | yes (13) |
| 1Q23 decel (-4.6) | "lower than our revenue growth"; revenue guide +12-16% vs printed 18.6 | decel; the -4.6 points is a construction (revenue-guide midpoint), direction is certain | yes, points are JUDGEMENT |
| 4Q24 decel (-3.9) | "relatively stable compared to Q1 2024 after excluding Leap Day" (1Q24 9.5% incl ~1pt) | decel vs the printed 12.35; the prior team "stable" coding used the wrong comparator. C is right | yes |
| 4Q25 decel (-1.8) | "high-single-digit" (7-9) vs 9.82 | decel, but the top of the bucket is 0.8 pt below the print; marginal | yes, marginal |
| 2Q26 accel (+0.7) | "low double-digit" (10-12) vs 10.34 | **contestable**: 10.34 is itself low double-digit; "stable" is at least as defensible as "accelerating". C codes it +1 on the bucket midpoint | partial |

Disagreements: none on direction that would change a bucket except 2Q26, where stable is an equally valid reading. Recoding 2Q26 as stable moves the +16.3 out of the accelerating-guide bucket, leaving that bucket at 2 prints (0.0, -8.8): it strengthens, not weakens, the "no detectable effect" reading, and it removes the one observation that makes the guide-direction coefficient positive (the note's own section 6 says so).

Label distribution (MEASURED, `C_guide_direction_coding.csv`): primary 16 prints: accelerating 3, stable 2, decelerating 11. 4Q21-2Q26 (19 coded): accelerating 5, stable 3, decelerating 11 (plus 2021 codes on the 2019 basis). Yes: the "no effect" is partly by construction. Eleven of sixteen guides are decelerating because management's standard letter language is "moderate relative to" the just-printed quarter, and every Q4 print guides a decelerating Q1. With 3 accelerating guides (one contestable) the test has almost no power; the correct statement is "not detectable", not "does not move the stock". See finding 4.

### 2.4 Key statistics (task 4)

Independent re-computation from `C_print_panel.csv` (auditor code, HC1 by hand, LOO and 5,000-shuffle permutation):

| Statistic | Note | Auditor | Match |
|---|---|---|---|
| Post-2022 accelerating mean, n, positive | +6.0, 5, 4 | +6.04, 5, 4 | yes |
| Post-2022 decelerating mean, n, positive | -5.6, 8, 0 | -5.59, 8, 0 | yes |
| Binomial p, 0 of 8 | 0.008 | 0.0078 two-sided vs 0.5 (`scipy.stats.binomtest` default); one-sided 0.0039 | yes; it is two-sided, null 50% |
| Sign coefficient post-2022 | b +5.66, HC1 t 2.65, R2 0.41, LOO +0.28, perm 0.013 | b +5.66, t 2.65 (OLS t 2.87), R2 0.406, LOO +0.277, perm 0.012 | yes |
| Sign coefficient primary (3Q22-2Q26) | +3.35, t 1.38, LOO -0.02, perm 0.16 | +3.35, t 1.38, LOO -0.017, perm 0.165 | yes |
| Mann-Whitney accel vs decel | post-2022 0.019; **3Q22-2Q26 "p 0.11" in note table** | 0.019; **0.145** (and `C_sorted_portfolios.csv` row 31 says 0.145) | note table transcription error |
| Guide vs Street primary | +1.92, t 2.24, R2 0.27, LOO +0.15, perm 0.040 | +1.92, t 2.24 (OLS 2.29), R2 0.273, LOO +0.152, perm 0.039, Spearman 0.51 | yes |
| M6 primary | c -1.87, +3.86 (t 1.8), +2.06 (t 2.8), R2 0.44, LOO +0.22, perm 0.022, resid sd 7.3 | same to 2 dp; perm 0.024 | yes |
| M6 post-2022 | c -0.97, +5.46 (t 2.5), +1.33 (t 1.8), LOO +0.29 | same | yes |

Definitions checked in `C_02_reaction_tests.py`: LOO R2 = 1 - SSE(leave-one-out predictions) / SSE(leave-one-out sample means), i.e. out-of-sample fit against an out-of-sample naive; a fair definition. Permutation: the target vector is shuffled 2,000 times, the regression refit, and p = (count of R2 >= observed + 1) / 2,001; standard, two-sided on the slope by construction. Binomial: two-sided against 50%. The rng is module-level and shared across all 420 fits, so the p values depend on the loop order; reproducible but not independently seeded per test (cosmetic).

### 2.5 Multiple testing (task 5)

17 pre-stated specs (12 univariate + 5 multivariate on the primary target and sample). Holm at 5%: the smallest p must clear 0.05/17 = 0.0029. Sorted p values and thresholds (MEASURED from `C_univariate_tests.csv`, `C_multivariate_tests.csv`):

| Rank | Spec | perm p | Holm threshold | Clears |
|---|---|---|---|---|
| 1 | guide vs Street | 0.040 | 0.0029 | no (Bonferroni-adjusted p 0.67) |
| 2 | nights accel sign | 0.156 | 0.0031 | no |
| 3 | momentum score | 0.176 | 0.0033 | no |
| 4-17 | all others | 0.25 to 0.98 | 0.0036 to 0.05 | no |

**Nothing pre-stated clears Holm; the sign rule does not even clear nominal 5% on the pre-stated sample.** The post-2022 sign result (perm p 0.013) is not one of the 17: it is one of 36 primary-target univariate tests across three samples, where Holm's smallest threshold is 0.0014 and it ranks first; Bonferroni-adjusted p 0.45. The note's caveat 1 says roughly this; the answer section does not.

### 2.6 Breakeven (task 6)

Coefficients reproduce (2.4). Contour reproduces: g* = -(c + b1 s)/b2 gives -0.97% / +0.91% / +2.78% for s = +1 / 0 / -1 on the primary sample, -3.39% / +0.73% / +4.85% post-2022. Team base (s -1, gvs -1.36%): -8.53% primary, -8.23% post-2022; S1 -4.02% / -6.11%. Bootstrap p10/p90 -11.3 / -6.1 and share positive 0.00 reproduce from the seeded script.

Zacks comparator ($3,200m): team base gvs becomes -2.78% and E[S2] -11.5% (primary) / -10.1% (post-2022); the Street scenario (guide at Bloomberg $3,154m) flips from +2.0% to -1.0%, and management delivered from +0.4% to -2.5%. So the vendor choice does not change the team-base sign but does change the sign of the "Street" and "delivered" scenarios; the scenarios table shows only the Bloomberg column for the headline (the Zacks column exists in `C_scenarios.csv` as `E_S2_ex_reopening_zacks_pct`).

Mapping: 1 pt of 4Q26 nights = 1% of revenue, anchored at 10.5% / $3,130m. The team's own base case (8.9% / $3,111m) implies 0.4% per point on that anchor, so the mapping over-states the revenue swing of a nights guide by about 2.5x against the team's own numbers; the "implied 4Q26 nights guide" column in the contour (14.1% and 16.2% for the decelerating breakevens) would read higher still on the team's elasticity. The direction of the conclusion (a decelerating print cannot be guided back to breakeven) is unaffected; the nights numbers quoted are not.

Executable next-open entry: sign coefficient -1.7 (HC1 t -1.6, LOO +0.02); decelerating prints ex-reopening gapped -5.3% on average and then rose +1.7% intraday (9 of 9); accelerating prints gapped +4.9% and fell -1.6% (4 of 6). MEASURED from `C_print_panel.csv`. So the entire conditional expectation lives in the overnight gap. What that means: (a) there is no post-open strategy; (b) the only way to capture the expected close-to-close move is to hold a position through the print, which is a bet on the team's 3Q26 nights nowcast being on the correct side of 10.1-10.6% and on the sign rule holding for a 15th observation; (c) the intraday retrace of a fifth to a third of the gap is itself a (descriptive, n 9) pattern that argues for covering a pre-print short at the open, not the close.

### 2.7 Cross-check with B (task 7)

`B_print_base_rates.csv`: nights accelerated 8 prints, 6 up 2 down; decelerated 11 prints, 1 up 10 down. These are 19 prints (4Q21-2Q26, the ones with `nights_yoy_accel_pts`), no dead band, on B's `cc_1d_pct`, which is in fact `20_executable_returns.csv` legacy_1d_pct, i.e. the QQQ-excess close-to-close return (4Q21 3.674, 2Q26 16.257 match legacy_1d_pct exactly; B's `B_reconcile_reaction_files.csv` compares this excess series to the raw `abnb_1d_pct` and labels the gap "diff", which is B's mislabel, not C's). C's 4Q21-2Q26 sample: accelerating 7 (5 positive), decelerating 10 (1 positive), flat 2. Reconciliation: B's 8 accelerating = C's 7 + 1Q22 (+0.01 pt, +4.3%, flat under C's 0.25-pt dead band); B's 11 decelerating = C's 10 + 3Q24 (-0.21 pt, -8.8%, flat under C). B's 6 up = C's 5 + 1Q22; B's 10 down = C's 9 + 3Q24. Fully reconciled, same return definition, different dead band. C's post-2022 counts (4 of 5 accelerating, 0 of 8 decelerating) are a 13-print subset of the same series. The task's "6 of 6" is not a C claim; C reports 4 of 5 (post-2022) and 4 of 6 (3Q22-2Q26).

---

## 3. Findings

Severity: blocker (invalidates a headline), material (changes how a headline should be read or used), minor (fix on the next pass).

**1. Material. The "0 of 8 decelerating prints positive, p 0.008" depends on the QQQ-excess convention and one-decimal rounding.** `C_reaction-function.md` section 1 item 1, section 4 table; `C_sorted_portfolios.csv`. Of the 8 post-2022 decelerating prints, 2Q23 is -0.036% excess (stored -0.0), 1Q25 is -0.5% excess but +1.0% raw, 1Q26 is -1.6% excess but +0.7% raw. On raw close-to-close returns the bucket is 2 of 8 positive (binomial p 0.29). On the primary 3Q22-2Q26 sample it is 1 of 9 excess, 3 of 9 raw. The excess return is the right target for a revaluation, but "sold 8 of 8 times" is a knife-edge count. Fix: quote both counts ("0 of 8 on excess, 2 of 8 on raw; three of the eight are within 1.6 points of zero") and replace the per-bucket binomial with the between-bucket test, which is what the claim actually needs: Fisher exact accelerating-vs-decelerating positive, post-2022 p 0.007, 3Q22-2Q26 p 0.089; Mann-Whitney 0.019 / 0.145. Against the sample's own base rate of positive prints (0.29) rather than 50%, the 0-of-8 is p 0.068 one-sided.

**2. Material. The sign rule is a re-test on the same prints, not a confirmation, and it fails the workstream's own pre-stated rule on the pre-stated sample.** `C_reaction-function.md` section 1 item 1 ("confirms the predictive study's finding ... on a cleaner panel"), section 3 pre-stated design, section 4. The predictive study's 17-of-21 used the same prints and the same returns; C's panel drops two prints into a dead band and starts at 4Q21. Nothing new was observed. On the pre-stated primary sample (3Q22-2Q26, n 16) the sign rule has t 1.4, LOO R2 -0.02, perm p 0.16, and is not a survivor; it survives only on the secondary post-2022 sample (n 14). None of the 17 pre-stated specs clears Holm (section 2.5). Fix: in section 1 lead with both samples side by side, state that the post-2022 result is a secondary-sample result that would not survive a multiplicity correction, and replace "confirms" with "re-tests, on the same prints, and finds the same base rate". The right status is "a prior hypothesis with a 15th observation due on 5 Nov", which section 9 already says well.

**3. Material. The sign result is carried by two prints and the dead-band choice; report the sensitivity.** `C_01_print_panel.py` line defining `nights_accel_sign` (0.25-point dead band); note section 10 caveat 2. Auditor sensitivity, primary target:

| Dead band (pts) | 3Q22-2Q26: accel n / positive / mean; decel n / positive / mean; b, t, LOO | 1Q23-2Q26: same |
|---|---|---|
| 0.00 | 6 / 4 / +3.4; 10 / 1 / -4.1; +3.7, 1.6, +0.02 | 5 / 4 / +6.0; 9 / 0 / -5.9; +6.0, 2.8, +0.34 |
| 0.25 (C) | 6 / 4 / +3.4; 9 / 1 / -3.6; +3.4, 1.4, -0.02 | 5 / 4 / +6.0; 8 / 0 / -5.6; +5.7, 2.7, +0.28 |
| 0.50 | 5 / 4 / +6.0; 8 / 1 / -3.0; +4.0, 1.6, +0.03 | 5 / 4 / +6.0; 7 / 0 / -5.2; +5.4, 2.5, +0.22 |
| 1.00 | 5 / 4 / +6.0; 6 / 1 / -1.6; +3.5, 1.3, -0.04 | 5 / 4 / +6.0; 5 / 0 / -4.5; +5.3, 2.2, +0.16 |
| 1.50 | 2 / 1 / +4.5; 6 / 1 / -1.6; +1.9, 0.5, -0.16 | 2 / 1 / +4.5; 5 / 0 / -4.5; +4.1, 1.3, -0.07 |

The post-2022 result is stable for dead bands up to 1 point; the primary-sample result is not significant at any dead band; at 1.5 points (which removes 3Q25, 4Q25 and 2Q26 from the accelerating bucket) both collapse. 3Q22 (+0.30 pt, just over the band, -10.0%) is the one accelerating print that fails, and it sits in the primary sample only. Fix: add this table (or the 0 / 0.25 / 0.5 rows) to section 4 and say which prints move.

**4. Material. "Guide direction does not move the stock" is a power statement.** `C_reaction-function.md` section 1 item 2, section 5. Three accelerating guides in 16 (2Q23 0.0, 3Q24 -8.8, 2Q26 +16.3), one of which (2Q26, "low double-digit" vs a 10.34% print) is as reasonably coded stable; eleven decelerating guides because the standard letter language is "moderate relative to" and every Q4 print guides a hard Q1 comp. The regression's t of 0.3 says the data cannot distinguish +1.0 per step from zero or from +5; it does not say the effect is zero. The seasonal confound the note identifies (Q4 prints +7.1 on decelerating guides, non-Q4 -5.8) is a further reason a guide-vs-printed comparison is the wrong variable. Fix: re-label item 2 as "not detectable on 3 accelerating guides; the label distribution is 3 / 2 / 11 by construction; the variable that carries information is the guide against the Street (item 3)". The statement that the 2Q26 move "does not generalise" as an accelerating-guide reaction should read "cannot be tested: there are two other accelerating guides".

**5. Material. The team-base expected reaction is conditional on a decelerating print; the note does not weight the probability that the print accelerates.** `C_reaction-function.md` section 1 item 8, section 7 scenarios, one-line synthesis. The team's nowcast is 9.5-10.0 with band 8.5-11.0 (`docs/q3nowcast/SYNTHESIS.md`); the accelerating threshold is 10.6 (dead band) or 10.34 (strict); the Street is at 11.1; the company has beaten its revenue guide 19 of 19 times. Treating the band as roughly normal (centre 9.75-9.9, sd 0.75-1.0) puts 13 to 20% of the mass above 10.6 and 17 to 22% in the flat zone (JUDGEMENT on the shape; the nowcast note gives no distribution). The unconditional expectation under S1 is then about -2 to -2.5%, and under S2 with the team's guide (-1.4% vs Street) in every state about -6 to -7%, against the conditional -4.0 / -8.5. Fix: add an unconditional row to `C_scenarios.csv` with the probability of acceleration as an explicit input, and change the one-line synthesis to "conditional on a decelerating print (the team's central case; the nowcast band gives roughly a one-in-six chance of acceleration), the day-1 close-to-close excess has been ...". Also state that the bootstrap p10/p90 (-11.3 / -6.1) is the sampling distribution of the fitted mean, not of the realised move (residual sd 7.3), and that "0% of refits positive" is close to automatic when the decelerating bucket mean is -3.6 with 1 of 9 positive.

**6. Material. The two-variable breakeven function (S2 / M6) is post-hoc and its second coefficient is fragile; the Street comparator changes two scenario signs.** `C_03_breakeven.py`; note section 7, zero contour, section 1 item 7. Guide-vs-Street on the primary sample: drop 2Q24 (guide -3.6% vs Street, return -12.3) and LOO R2 falls to +0.007; drop 4Q22 and it is -0.008; drop 2Q24 and 2Q26 together and b 1.4, t 1.2, LOO -0.13. It fails the pre-stated rule on n 14 and n 19. M6 was specified after seeing the univariate results (the script says so). With Zacks $3,200m instead of Bloomberg $3,154m the Street scenario goes from +2.0% to -1.0% and management delivered from +0.4% to -2.5%; team base from -8.5% to -11.5%. The contour's "implied 4Q26 nights guide" uses a 1 pt = 1% mapping that the team's own base case (8.9% at $3,111m vs 10.5% at $3,130m, i.e. 0.4% per point) contradicts, so "~14%" and "~16%" nights guides at breakeven are not on the team's elasticity. Fix: make S1 (sign only) the number in the answer and the synthesis (-4.0% / -6.1% conditional), present S2 as "post-hoc, illustrative, sensitive to two prints and to the consensus vendor", print the Zacks column next to the Bloomberg one in the scenarios table, and either drop the implied-nights column from the contour or restate it on the team's elasticity ("about 0.4-1.0% of revenue per point; breakeven nights guide 13 to 20%+").

**7. Material. The tradeable content is a pre-print position, and the note's one-liner should say so.** Note section 1 item 6 and 8, one-line synthesis. Section 2.6 above: the conditional expectation is entirely in the overnight gap (decelerating prints gap -5.3% and retrace +1.7% intraday, 9 of 9). The note's own text says "the reaction is the gap ... not a trade", but the one-line version for the synthesis ("the team's decelerating base case is worth roughly -4% to -9% on the day") reads as a return. Fix: "-4% to -6% close-to-close excess conditional on a decelerating print, captured only by a position held through the print; nothing is capturable after the open, and decelerating prints have bounced 9 of 9 times intraday".

**8. Minor. Transcription error: 3Q22-2Q26 Mann-Whitney p.** `C_reaction-function.md` section 4 table, row "3Q22-2Q26 spread, MW p": note says "p 0.11"; `C_sorted_portfolios.csv` row 31 and the auditor's recomputation say 0.145 (Welch 0.197). Fix the table.

**9. Minor. 4Q21 guide-vs-Street +16.5% (CNBC, unattributed, flagged low-confidence in the source) enters the "all" sample unwinsorised.** `C_01_print_panel.py` (no clip on `guide_vs_street_pct`; the script winsorises only `nights_yoy_accel_pts` for the all sample). It drives the all-sample guide-vs-Street and M6 rows (b +0.78, t 1.8; M6 all b +0.7). Not in the primary sample. Fix: clip or set to NaN in the all sample and say so.

**10. Minor. Primary target rounded to one decimal.** `C_01_print_panel.py` reads `abnb_earnings_reactions.csv` (one-decimal `excess_1d_pct`); `20_executable_returns.csv` legacy_1d_pct carries the same quantity at full precision (2Q23 -0.036, 1Q25 -0.476, 1Q26 -1.611). Fix: use legacy_1d_pct as the target; nothing changes at two decimals except the 2Q23 sign is then unambiguous.

**11. Minor. "Only print variable that does so in every sample" overstates.** Section 1 item 1. What is true is that the sign coefficient is positive in all three samples (+3.4, +3.5, +5.7); it is significant and passes the rule in one. Same for "threshold, not a slope": the points variable has Spearman 0.20 (p 0.45) on n 16 and 0.38 (p 0.19) on n 14, so the slope is under-powered rather than absent. Fix: "positive in every sample, significant in one; the points version is not significant at n 14, which is a power limit as much as a finding" (section 9 item 2 already says the latter).

**12. Minor. Mapping anchor and 4Q26 revenue.** `C_03_breakeven.py` REV_PER_NIGHT_PT = 0.01 anchored on management delivered. The "ex-NA lap" scenario maps 8.1% to $3,055m; the team's own bridge would put 4Q26 revenue at about $3,090-3,100m on its 0.4% per point. Fix: take the team's revenue from the WS29/30 files rather than the mapping, or state the elasticity used is 2.5x the team's.

**13. Minor. B's reconcile file mislabels its series.** `data/processed/reverse_dcf/B/B_reconcile_reaction_files.csv` compares `cc_1d_pct` (which is the QQQ-excess legacy_1d_pct) to the raw `abnb_1d_pct` and calls the gap a discrepancy. Not C's file; noted here because task 7 asked for the reconciliation. For the synthesis: B's 6/2 and 1/10 and C's counts are the same return series with a different dead band.

---

## 4. Headline claims judged (task 8)

| Claim | Verdict | Reasons |
|---|---|---|
| (i) The printed nights-acceleration sign rule is real, and it is a threshold not a slope | **Partly supported.** The base rate is real and reproduces (post-2022 4 of 5 vs 0 of 8 excess; Fisher p 0.007; sign coefficient positive in all three samples). It is not a new finding (same prints as the predictive study), it fails the pre-stated rule on the pre-stated sample, it clears no multiplicity correction, and the 0-of-8 is 2-of-8 on raw returns. "Threshold not slope" is a power statement at n 14 (points Spearman 0.38, p 0.19). | Findings 1, 2, 3, 11 |
| (ii) Guide direction vs printed rate has no effect | **Not supported as stated; supported as "not detectable".** 3 accelerating guides, one contestable; 11 of 16 decelerating by construction; seasonal confound. The negative result is real in the sense that nothing in the data supports the prior team's asserted "accelerating guide = +5 to +10%", and the 4Q24 recoding is correct. | Finding 4 |
| (iii) Guide vs Street revenue has an effect | **Partly supported.** It is the only pre-stated survivor on the primary sample (t 2.2, LOO +0.15, perm 0.04, Spearman 0.51) and it has prior support (WS04/WS20). It is sample-dependent, carried by 2Q24 and 4Q22, fails on n 14 and n 19, and would not survive Holm. The note is candid about this in section 9; the answer section and the breakeven use it as if established. | Finding 6 |
| (iv) The team base case implies a negative day-1 reaction with robust sign | **Partly supported.** Conditional on a decelerating print the sign is robust across specifications and bootstraps because the decelerating bucket mean is negative in every sample (1 of 9 / 0 of 8 positive). Unconditionally, 13 to 20% of the nowcast band is accelerating, so the expectation is smaller (-2 to -2.5% under S1). The magnitude (-4 to -8.5%) rests on S2 for the lower end, which is post-hoc and vendor-sensitive. | Findings 5, 6, 7 |

**Post-hoc selection flagged.** (a) M6/M7/M8 were added after the univariate results; the note labels them post-hoc everywhere, which is correct, but the breakeven contour and the -8.5% headline are built on M6. (b) The post-2022 sample (1Q23 onward) is not the pre-stated primary sample; the headline statistics in section 1 item 1 are from it. (c) The 0.25-point dead band was chosen before the tests (the script comment says so) and moves 3Q24 and 1Q22 into "flat"; the sensitivity in finding 3 shows the post-2022 result does not depend on it, the primary-sample result is not significant at any band. (d) The Q4-print seasonal split (4 vs 7) was found after the guide-direction test failed and is presented as a reading, not a result; fine.

---

## 5. What the synthesis should and should not use (task 9)

**Use:**

1. MEASURED, `C_sorted_portfolios.csv`, `C_print_panel.csv`: the sign base rate with both counts. "Since the 1Q23 print, the 5 accelerating nights prints closed up on the day (QQQ-excess) 4 times, mean +6.0%; the 8 decelerating prints closed up 0 times on excess, 2 of 8 on raw, mean -5.6%. On the 16-print 3Q22-2Q26 sample: 4 of 6 (+3.4%) vs 1 of 9 (-3.6%). Fisher exact between buckets p 0.007 / 0.09." Label it a base rate with n, not a model.
2. MEASURED, `C_coefficients_used.csv` S1 rows: the conditional expected reaction from the sign only, -4.0% (n 16) / -6.1% (n 14) for a decelerating print, +2.7% / +5.2% for an accelerating one, with residual sd 8.8 / 6.9 on a single print.
3. MEASURED, `C_print_panel.csv`: the gap / intraday split (decelerating prints gap -5.3%, retrace +1.7% intraday, 9 of 9), and the statement that nothing is capturable after the open.
4. MEASURED, `C_guide_direction_coding.csv`: the 4Q24 recoding (decelerating guide, +14% day), the label distribution (3 / 2 / 11), and the conclusion that the prior team's "accelerating guide" outcome table was asserted, not tested.
5. MEASURED, `C_univariate_tests.csv`: guide vs Street as the one pre-stated survivor on n 16 (+1.9% per 1%, t 2.2, LOO +0.15), with the caveat that it fails on n 14 and n 19 and rests on 2Q24 and 4Q22; direction only, "a 4Q26 revenue guide below the then-current Street number has been sold".
6. MEASURED: revenue, EPS, EBITDA surprises, FY raise, run-up carry no day-1 information on any sample (all pre-stated, all fail). This is the cleanest negative in the workstream.
7. ANCHOR / MEASURED: the Street's 3Q26 nights bar (148.9m, +11.1%) is already in the accelerating bucket, so consensus expects acceleration; the team's nowcast (9.5-10.0, band 8.5-11.0) does not.

**Do not use, or use only with the label:**

1. The -8.5% (or -8.2%, -11.5% Zacks) team-base expectation as a point forecast. JUDGEMENT built on post-hoc S2; quote at most as "the two-variable function, post-hoc, puts it at -8 to -9%; the sign-only base rate at -4 to -6%".
2. "0 of 8, p 0.008" or "sold 8 of 8 times" without the raw-return count and the between-bucket test.
3. The zero-contour "implied 4Q26 nights guide of ~14% / ~16%" (mapping is 2.5x the team's elasticity).
4. "Guide direction does not move the stock" as a finding. Use "not detectable on 3 accelerating guides".
5. "Confirms the predictive study on a cleaner panel". Same prints; re-test.
6. The bootstrap p10/p90 as a range for the realised move. It is the sampling range of the fitted mean; the realised-move range is the residual sd (7 to 9 points), i.e. a decelerating print has closed anywhere from -12.3% to +12.6%.
7. Any of the multiple-change (EV/NTM revenue) coefficients as separate evidence: WS12's multiple change is the price move with a guide-implied estimate adjustment (corr 0.84-0.99 with the return, per the note).

**Re-labelling.** In the note's section 1: item 1 first sentence ("the only print variable that does so in every sample") is JUDGEMENT, not MEASURED; item 2 ("does not move the stock") is JUDGEMENT from an under-powered test; item 7's contour is MEASURED on a post-hoc function with a JUDGEMENT mapping; item 8's "-4% to -8.5%" is MEASURED conditional on a JUDGEMENT (decelerating print) and its lower end is post-hoc; the confidence sentence ("sign robust, magnitude not") is correctly labelled JUDGEMENT and is the best sentence in the section.

---

## 6. What would change this audit's reading

- A 5 Nov print that decelerates and closes up on excess (post-2022 decelerating goes to 1 of 9) would confirm finding 1's point that the 0-of-8 is a knife edge; one that decelerates and closes down would not validate the coefficient but would keep the base rate at 9 of 9 on excess.
- A next-quarter nights consensus history (none exists, per WS04) would allow the guide to be tested against the Street's nights number rather than the printed rate, which is the test the prior team's claim actually needs.
- If the team's 4Q26 revenue in the WS29/30 files is confirmed at $3,111m for 8.9% nights, the mapping in `C_03_breakeven.py` should be replaced by the team's own elasticity before any nights-guide breakeven is quoted.
