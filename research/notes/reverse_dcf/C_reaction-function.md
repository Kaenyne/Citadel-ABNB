# C. The print reaction function and the 5 Nov breakeven: what moves ABNB on the day, and what print is priced

- **Date:** 12-13 Sep 2026 overnight run (reverse-DCF brief, workstream C). Author: Claude (agent C), for Krishang. **Revised 13 Sep after audit** (`research/notes/reverse_dcf/audit_C.md`, verdict pass with fixes; all 13 findings applied, list in section 12).
- **Scripts:** `analysis/src/reverse_dcf/C_01_print_panel.py`, `C_02_reaction_tests.py`, `C_03_breakeven.py` (py -3.13).
- **Data out:** `data/processed/reverse_dcf/C/` (19 CSVs, listed in section 11).
- **Builds on:** `research/notes/predictive/04_margin-and-reaction.md` (nights-acceleration sign rule), `overnight/04_consensus-and-reaction.md` (consensus at print, 97 tests), `overnight/20_temporal-validation.md` (executable entry), `overnight/12_valuation-multiple-regime.md` (multiple share of the move), `overnight/02_kpi-panel-and-guidance-ledger.md` (guidance ledger). Labels: ANCHOR (from the brief), MEASURED (computed here, file named), JUDGEMENT (mine).

---

## 1. The answer

1. **The printed nights-acceleration sign rule re-tests on the same prints the predictive study used, and the same base rate comes back.** Since the 1Q23 print (n 14): the 5 prints where nights y/y accelerated versus the prior quarter closed up on the day (close to close, QQQ-excess) 4 times, mean **+6.0%**; the 8 decelerating prints closed up **0 of 8 times on the excess return and 2 of 8 on the raw return**, mean **-5.6%** (raw -5.0%); three of the eight are within 1.6 points of zero. On the 3Q22-2Q26 sample (n 16): **4 of 6 (+3.4%) vs 1 of 9 (-3.6%)** on excess, 3 of 9 on raw. The test the claim needs is between the buckets: Fisher exact on the share positive **p 0.007 post-2022, 0.089 on n 16**; Mann-Whitney 0.019 / 0.145. MEASURED, `C_sorted_portfolios.csv`. As a regression on the sign it passes the pre-stated selection rule on the post-2022 sample only (b +5.7 per unit of sign, HC1 t 2.7, LOO R2 +0.28, permutation p 0.017) and fails it on the pre-stated n 16 sample (t 1.4, LOO R2 -0.02, perm p 0.16). The coefficient is positive in all three samples (+3.4, +3.5, +5.7) and significant in one. **None of the 17 pre-stated specs clears a Holm correction** (threshold 0.0029, best p 0.040) and the post-2022 p 0.017 is the best of 36 primary-target univariate tests across samples (Bonferroni p 0.61). Status: a prior hypothesis with a 15th observation due on 5 Nov, not an established coefficient. The acceleration in points is not significant in any sample (b +0.3 to +1.0 per point, Spearman 0.20 on n 16 and 0.38 on n 14, p 0.19), which at these n is a power limit as much as a finding.
2. **The direction of the next-quarter nights guide versus the just-printed rate is not detectable.** Coded for all 22 guided prints from the letters (coding table in `C_guide_direction_coding.csv`, quotes verbatim): the label distribution is 3 accelerating / 2 stable / 11 decelerating in the primary 16, by construction (management's standard sentence is "moderate relative to", and every Q4 print guides a hard Q1 comp). The three accelerating guides returned 0.0% (2Q23), -8.8% (3Q24) and +16.3% (2Q26), and 2Q26 ("low double-digit" after a 10.34% print) can as reasonably be coded stable, which leaves two. Regression coefficient +1.0 per step (t 0.3, LOO R2 -0.23); with 2Q26 recoded stable it is -0.3. A t of 0.3 on three observations cannot distinguish +1 from 0 or from +5. The prior team's outcome table ("accelerating guide: +5% to +10%") was asserted from analogues and cannot be tested on this history. MEASURED / JUDGEMENT.
3. **What the guide is compared with matters: the next-quarter revenue guide midpoint versus the Street's next-quarter revenue is the one pre-stated survivor on the primary sample.** +1.9% of day-1 excess return per 1% the guide sits above Street (HC1 t 2.2, R2 0.27, LOO R2 +0.15, permutation p 0.04, Spearman 0.51; n 16). With the low-confidence 4Q21 point clipped it also passes on the 19-print sample (b +1.4, t 2.4, LOO +0.15, perm 0.02) and fails on the 14-print sample (LOO -0.03). It is fragile to single prints: drop 2Q24 and LOO R2 is +0.006, drop 4Q22 -0.009, drop 2Q24 and 2Q26 together and b 1.4, t 1.2, LOO -0.13 (`C_fragility.csv`). It is the same variable behind WS04/WS20's 9-of-9 guide-below-Street 20-day rule, which is why it is carried at all. Direction only: a next-quarter revenue guide below the then-current Street number has been sold.
4. **Revenue beat (vs consensus, vs guide midpoint, vs guide top), EPS surprise, EBITDA surprise, the FY guide raise, the nights beat vs consensus and the pre-print run-up carry no day-1 information** (all |t| under 0.6 on the primary sample, LOO R2 -0.06 to -0.26; all pre-stated, all fail). This is the cleanest negative in the workstream.
5. **The multiple responds the same way as the price, because it is the price.** EV/NTM-revenue multiple change on the print (WS12): accelerating-sign b +6.4 (t 2.5, LOO R2 +0.26) post-2022; guide-vs-Street b +1.8 (t 1.5, LOO 0.00) ex-reopening; nothing else. The WS12 multiple change is the price move with a guide-implied estimate adjustment (correlation 0.84 to 0.99 with the return), so this is not separate evidence.
6. **The whole conditional expectation is the overnight gap, and none of it is capturable after the open.** 3Q22-2Q26: decelerating prints gapped **-5.3%** (1 of 9 positive) and then rose **+1.7%** intraday (9 of 9); accelerating prints gapped +4.9% (5 of 6) and gave back -1.5% intraday (4 of 6). On the executable next-open entry the sign coefficient is -1.7 (LOO +0.02). The expected close-to-close move is captured only by a position held through the print; the intraday retrace argues for covering a pre-print short at the open, not the close (descriptive, n 9). MEASURED, `C_sorted_portfolios.csv`.
7. **What is priced for 5 Nov.** On the sign rule alone (S1, pre-stated, the headline function): an accelerating 3Q26 nights print (above ~10.6%) carries an expected day-1 excess of **+2.7% (n 16) to +5.2% (n 14)**; a decelerating print (below ~10.1%) **-4.0% to -6.1%**; no guide term exists in S1 to offset either. The post-hoc two-variable function (S2, illustrative) adds the 4Q26 revenue guide vs Street: with acceleration the stock absorbs a guide 1% (n 16) to 3% (n 14) below the Bloomberg Street ($3,154m) at zero expectation; with deceleration the guide would need to sit 2.8% to 4.9% above Street ($3,240-3,310m). The Street's own 3Q26 nights number (+11.1%) is already in the accelerating bucket: consensus and price agree that 3Q26 accelerates.
8. **The team's base case (3Q26 +9.9%, 4Q26 +8.9%, $3,111m), conditional on it being a decelerating print: expected day-1 close-to-close excess -4.0% (n 16) to -6.1% (n 14) on S1**, with the fitted mean's sampling range (bootstrap p10/p90) -6.5% to -0.4% and the realised-move range (E plus or minus 1.28 residual sd) -15% to +7%. S2 puts it at -8.5% (Bloomberg comparator) to -11.5% (Zacks $3,200m); post-hoc, and 2Q24 and 4Q22 carry its second coefficient. **Unconditionally**, the team's own nowcast band (9.5-10.0, band 8.5-11.0) puts 13-21% of its mass in the accelerating bucket and 19-20% in the flat zone (JUDGEMENT on the shape), which brings the S1 expectation to **-1.9% to -3.5%** and S2 to -6 to -7%. The sign of the conditional expectation is robust (every specification, sample and bootstrap draw, because the decelerating bucket mean is negative with 1 of 9 positive); the magnitude is not (residual sd 6.9 to 8.8 points; decelerating prints have closed anywhere from -12.3% to +12.6%). MEASURED conditional / JUDGEMENT unconditional; `C_scenarios.csv`, `C_unconditional.csv`.

The one-line version for the synthesis: **conditional on a decelerating 3Q26 nights print (the team's central case; the nowcast band gives roughly a one-in-five chance of acceleration), the day-1 close-to-close excess return has been -4% to -6% on average and negative 8 of 9 times since 3Q22 on the excess convention (6 of 9 on raw); it is captured only by a position held through the print, nothing is capturable after the open, and the 4Q26 revenue guide against the then-current Street number is the second lever, at roughly 2 points per 1% on a fragile coefficient.**

---

## 2. The prior result Krish referred to, exactly

The claim "nights actually does affect stock movements and valuation (accelerating vs decelerating guidance)" traces to four places in the repo, which say slightly different things:

| Where | What it says | Strength as stated |
|---|---|---|
| `research/notes/predictive/04_margin-and-reaction.md` section 1.2 and 4 | "Direction is a nights-acceleration story, size is not. Prints where **nights growth accelerated versus the prior quarter** were up on the day 7 of 9 times (mean excess +3.2%); decelerations were down 10 of 12 (mean -2.7%). Sign concordance 17 of 21 (81%, binomial p = 0.007; Mann-Whitney p = 0.06). Pearson r is only -0.18 because the 2021 base effects dominate the magnitude, so treat this as a directional rule, not a slope." | Sign test, survives a 5-test correction (0.035); fails as a regression (LOO R2 -0.18); n 21 incl. hand-entered 2020 KPIs |
| same note, section 4 two-way sort | "Margin met with nights accelerating: 6 of 7 positive, mean +5.0%; margin met with nights decelerating: 2 of 11 positive, mean -2.1%." | Cells of 7 and 11 |
| `overnight/14_master-synthesis.md` line 105 and 7.1 | "Nights acceleration sign sets the day-1 reaction: 17 of 21; post-2022 accelerating prints +6.7% day-1 (n 5) vs decelerating -5.4% (n 9). **As a regression it fails: R2 0.032, LOO R2 -0.18.** A base rate with its n, not a model." Expected-reaction table keys the outcomes on "Nights >= +11% and Q4 nights **guided at or above the Q3 rate**: +5% to +10%" vs "Nights guided below the Q3 rate: -8% to -13%". | Base rate only; the **guide-direction** framing in the outcome table was asserted from analogues (4Q22, 4Q24, 2Q26 vs 3Q22, 2Q24, 3Q24, 2Q25), not tested |
| `overnight/02_kpi-panel-and-guidance-ledger.md` section 4 | Nights acceleration day-1 sign hit rate 0.79 (15 of 19); "nothing about the guide predicts the stock reaction"; next-Q margin guide direction hit rate 0.47 | Sign test; the nights **guide** direction was not tested there |
| `data/processed/abnb_guidance_reaction_results.csv` | "implied nights acceleration (pts; +/-2 for above/below)" from the next-Q nights guide: slope 1.41, t 1.16, p 0.26, R2 0.07 (n 20); 2023 onward slope 0.65, p 0.67 | The only prior test of the nights guide direction; weak, and the coding left the three bucket guides (3Q25, 4Q25, 2Q26) as NaN in the direction column and read 4Q24 as "stable" |

So the established result is about the **printed** acceleration sign, on these same prints. The **guide** direction was either asserted from three analogues or tested once, weakly, with an incomplete coding. Section 5 tests it with a complete coding and finds it not detectable. Nothing in this workstream is a new observation; the 5 Nov print will be the first.

---

## 3. Panel and method

**Panel (`C_print_panel.csv`, 23 rows, 4Q20-2Q26).** Returns: raw close-to-close from `abnb_earnings_reactions.csv`; QQQ-excess close-to-close (pre-print close to reaction-session close), gap and next-open entry returns from `20_executable_returns.csv` at full precision (`legacy_*_pct`; the one-decimal series in the reactions file stores 2Q23 as -0.0 where the value is -0.036); intraday excess = close-to-close excess minus gap. Multiple and estimate change from `12_abnb_print_decomposition.csv` (19 prints from 4Q21); nights growth and `nights_yoy_accel_pts` from `02_kpi_panel_quarterly.csv` (19 prints from 4Q21); consensus surprises from `16_consensus_at_print_merged.csv` (revenue 23, nights 19, comparable EPS 20, EBITDA 8, next-Q revenue 19); revenue guide range from `02_guidance_ledger.csv` (19 guided quarters); FY guide action from `abnb_guidance_reaction_panel.csv`; run-up from `04_reaction_panel.csv`. Acceleration sign uses a 0.25-point dead band (1Q22 at +0.01 and 3Q24 at -0.21 are "flat"); the dead-band sensitivity is in section 4. The 4Q21 guide-vs-Street value (+16.5%, an unattributed CNBC number flagged low-confidence in the source) is clipped to +8 for the 19-print sample regressions only; it is not in the primary sample.

**Guide direction coding (`C_guide_direction_coding.csv`).** Next-quarter nights guide versus the just-printed y/y rate, coded from the Outlook section of each letter (quotes verbatim; 3Q23, 4Q23 and 1Q24 say "nights booked" in lower case and were checked in the letter text). Code -1 / 0 / +1; points: directional language "higher" or "modest sequential increase" = +2, "stable" = 0, "moderate" or "lower" = -2, "moderate slightly" or "nearly as strong" or "slightly decelerate" = -1 (the realised |change| after directional guides averages 2.3 points, so +/-2 is the right scale); bucket guides use the bucket midpoint minus the printed rate.

| Print | Guide for | Coded | Pts | Printed rate | Next Q actual | Realised | Day-1 excess | Quote (verbatim) |
|---|---|---|---|---|---|---|---|---|
| 2Q22 | 3Q22 | stable | 0 | 24.8 | 25.1 | accelerated | -3.9 | "we expect Nights and Experienced Booked year-over-year growth to be stable with the year-over-year growth in Q2 2022" |
| 3Q22 | 4Q22 | decel | -1 | 25.1 | 20.2 | decelerated | -10.0 | "we expect Nights and Experiences Booked growth will moderate slightly relative to Q3 2022" |
| 4Q22 | 1Q23 | decel | -1 | 20.2 | 18.6 | decelerated | +12.6 | "we expect Nights and Experiences Booked year-over-year growth to be nearly as strong as Q4 2022" |
| 1Q23 | 2Q23 | decel | -4.6 | 18.6 | 11.0 | decelerated | -12.0 | "We expect year-over-year growth in Nights and Experiences Booked in Q2 2023 to be lower than our revenue growth during the quarter" (revenue guide +12-16%) |
| 2Q23 | 3Q23 | **accel** | +2 | 11.0 | 13.5 | accelerated | 0.0 | "We expect a modest sequential increase in the year-over-year growth rate of Nights and Experiences Booked from Q2 2023 to Q3 2023" |
| 3Q23 | 4Q23 | decel | -2 | 13.5 | 12.0 | decelerated | -5.1 | "We currently expect our nights booked growth in Q4 2023 to moderate relative to Q3 2023" |
| 4Q23 | 1Q24 | decel | -2 | 12.0 | 9.5 | decelerated | -2.8 | "we expect the growth rate of nights booked in Q1 2024 to moderate relative to Q4 2023" |
| 1Q24 | 2Q24 | stable | 0 | 9.5 | 8.7 | decelerated | -7.1 | "We expect the year-over-year growth rate of nights booked in Q2 2024 to be relatively stable to that of Q1 2024" |
| 2Q24 | 3Q24 | decel | -2 | 8.7 | 8.5 | flat | -12.3 | "we expect a sequential moderation in the year-over-year growth of Nights and Experiences Booked relative to Q2 2024" |
| 3Q24 | 4Q24 | **accel** | +2 | 8.5 | 12.3 | accelerated | -8.8 | "we expect year-over-year growth of Nights and Experienced Booked in Q4 2024 to be higher than Q3 2024" |
| 4Q24 | 1Q25 | decel | -3.9 | 12.3 | 7.9 | decelerated | +14.0 | "We expect year-over-year growth of Nights and Experiences Booked in Q1 2025 to be relatively stable compared to Q1 2024 after excluding Leap Day" (1Q24 was 9.5% incl. ~1pt leap day) |
| 1Q25 | 2Q25 | decel | -2 | 7.9 | 7.4 | decelerated | -0.5 | "In Q2 2025, we expect year-over-year growth of Nights and Experiences Booked to moderate relative to Q1 2025" |
| 2Q25 | 3Q25 | stable | 0 | 7.4 | 8.8 | accelerated | -8.4 | "In Q3 2025, we expect year-over-year growth of Nights and Seats Booked to be relatively stable compared to Q2 2025" |
| 3Q25 | 4Q25 | decel | -3.8 | 8.8 | 9.8 | accelerated | +0.6 | "In Q4 2025, we expect year-over-year growth of Nights and Seats Booked in the mid-single-digit range due to the challenging Q4 2024 comparison" |
| 4Q25 | 1Q26 | decel | -1.8 | 9.8 | 9.2 | decelerated | +4.4 | "driven by high-single-digit growth in Nights and Seats Booked and a moderate increase in ADR due to price appreciation and FX" |
| 1Q26 | 2Q26 | decel | -1 | 9.2 | 10.3 | accelerated | -1.6 | "In Q2 2026, we expect Nights and Seats booked growth to slightly decelerate, relative to Q1 2026, assuming an estimated roughly 100bps headwind related to the conflict in the Middle East" |
| 2Q26 | 3Q26 | **accel** (contestable) | +0.7 | 10.3 | pending | pending | +16.3 | "driven by low double-digit growth in Nights and Seats Booked and a moderate increase in ADR due to mix shift and price appreciation" |

The six 2021-1H22 prints are coded on the 2019 basis in the file and excluded from the primary sample. Three coding judgements matter: **4Q24** (the letter compares with 1Q24's rate, not the printed 4Q24 rate; relative to the printed 12.3% it is a ~4-point deceleration; the prior team coding read it as "stable"; the auditor agrees with the recoding), **1Q23** ("lower than revenue growth" mapped through the revenue guide), and **2Q26** (coded accelerating on the bucket midpoint 11.0 vs 10.34; "stable" is at least as defensible since 10.34 is itself low double-digit). The 2Q26 recode is carried as a sensitivity in section 5.

**Pre-stated design.** Primary target: day-1 close-to-close excess return vs QQQ (the revaluation; the executable open-entry return is reported alongside). Primary sample: 3Q22-2Q26 (16 prints; the 2021-1H22 prints carry +30 to -34 point base effects in acceleration). Twelve primary univariate features and five primary multivariate specs (M1 sign + guide direction; M2 + revenue surprise; M3 acceleration pts + guide pts; M4 + revenue surprise; M5 = M2 + EPS + FY raise). Selection rule written before running: LOO R2 > 0, coefficient sign unchanged in every leave-one-out fit, permutation p < 0.10. Three post-hoc specs (M6 sign + guide vs Street; M7 + guide direction; M8 + revenue surprise) were added after seeing the univariate results and are labelled post-hoc in every file. Statistics: HC1 t, R2, LOO R2 against the leave-one-out mean, 2,000-shuffle permutation p for R2, leave-one-out coefficient range, Fisher exact and Mann-Whitney between buckets.

**Test count and multiplicity (`C_test_count.csv`, `C_multiplicity_holm.csv`).** This run: 252 univariate and 168 multivariate regressions across 7 targets and 3 samples (17 of them primary), plus 688 sorted-portfolio cells (descriptive). Prior team: 661 reaction tests. Holm over the 17 pre-stated specs: the smallest p must clear 0.0029; the best is 0.040 (guide vs Street; Bonferroni-adjusted 0.67), so nothing pre-stated clears. Over the 36 primary-target univariate tests across the three samples: best p 0.017 (sign, post-2022) against a threshold of 0.0014, Bonferroni 0.61. Read the cross-sample consistency and the buckets, not the best p.

---

## 4. Results: the printed nights acceleration

**Sorted portfolios, day-1 close-to-close excess vs QQQ, both counts (`C_sorted_portfolios.csv`).**

| Sample | Bucket | n | Mean excess | Median | Positive, excess | Positive, raw | Mean raw | Prints |
|---|---|---|---|---|---|---|---|---|
| 3Q22-2Q26 | accelerating | 6 | +3.4 | +2.5 | 4 | 4 | +3.3 | 3Q22 3Q23 4Q24 3Q25 4Q25 2Q26 |
| 3Q22-2Q26 | flat | 1 | -8.8 | | 0 | 0 | -8.7 | 3Q24 |
| 3Q22-2Q26 | decelerating | 9 | -3.6 | -2.8 | 1 | 3 | -2.9 | 4Q22 1Q23 2Q23 4Q23 1Q24 2Q24 1Q25 2Q25 1Q26 |
| 3Q22-2Q26 | between buckets | 15 | spread +6.9 | | Fisher p 0.089 | Fisher p 0.315 | MW p 0.145 / 0.288 | |
| 1Q23-2Q26 | accelerating | 5 | +6.0 | +4.4 | 4 | 4 | +6.7 | 3Q23 4Q24 3Q25 4Q25 2Q26 |
| 1Q23-2Q26 | decelerating | 8 | -5.6 | -5.0 | **0** | **2** | -5.0 | 1Q23 2Q23 4Q23 1Q24 2Q24 1Q25 2Q25 1Q26 |
| 1Q23-2Q26 | between buckets | 13 | spread +11.6 | | **Fisher p 0.007** | Fisher p 0.103 | MW p 0.019 / 0.045 | |
| 4Q21-2Q26 | accelerating | 7 | +3.4 | +3.7 | 5 | | | 4Q21 3Q22 3Q23 4Q24 3Q25 4Q25 2Q26 |
| 4Q21-2Q26 | decelerating | 10 | -3.6 | -3.3 | 1 | | | 2Q22 4Q22 1Q23 2Q23 4Q23 1Q24 2Q24 1Q25 2Q25 1Q26 |
| 4Q21-2Q26 | between buckets | 17 | spread +7.0 | | Fisher p 0.035 | | MW p 0.088 | |

The three post-2022 decelerating prints that flip between conventions: 2Q23 (-0.04% excess), 1Q25 (-0.5% excess, +1.0% raw), 1Q26 (-1.6% excess, +0.7% raw). Unconditional base rate (`C_base_rates.csv`): share of prints with a positive day-1 excess 0.31 in 3Q22-2Q26 and 0.29 post-2022, mean -1.3% / -1.7%, mean absolute move 7.3% / 6.7%, sd 9.1 / 8.7. Against that base rate the 0-of-8 is p 0.068 one-sided; the accelerating bucket (4 of 5 vs 0.29) is p 0.026. The decelerating bucket is close to the base rate; the accelerating bucket is the anomaly.

**Dead-band sensitivity (`C_deadband_sensitivity.csv`, audit finding 3).** Which prints move, and whether the result survives:

| Dead band (pts) | 3Q22-2Q26: accel n / positive / mean | decel n / positive / mean | b, t, LOO R2, Fisher p | 1Q23-2Q26: accel | decel | b, t, LOO R2, Fisher p | Prints made flat |
|---|---|---|---|---|---|---|---|
| 0.00 | 6 / 4 / +3.4 | 10 / 1 / -4.1 | +3.7, 1.6, +0.02, 0.036 | 5 / 4 / +6.0 | 9 / 0 / -5.9 | +6.0, 2.8, +0.34, 0.005 | none |
| 0.25 (used) | 6 / 4 / +3.4 | 9 / 1 / -3.6 | +3.4, 1.4, -0.02, 0.089 | 5 / 4 / +6.0 | 8 / 0 / -5.6 | +5.7, 2.7, +0.28, 0.007 | 3Q24 |
| 0.50 | 5 / 4 / +6.0 | 8 / 1 / -3.0 | +4.0, 1.6, +0.03, 0.032 | 5 / 4 / +6.0 | 7 / 0 / -5.2 | +5.4, 2.5, +0.22, 0.010 | 3Q22 3Q24 2Q25 |
| 1.00 | 5 / 4 / +6.0 | 6 / 1 / -1.6 | +3.5, 1.3, -0.04, 0.080 | 5 / 4 / +6.0 | 5 / 0 / -4.5 | +5.3, 2.2, +0.16, 0.048 | + 2Q24 1Q26 |
| 1.50 | 2 / 1 / +4.5 | 6 / 1 / -1.6 | +1.9, 0.5, -0.16, 0.46 | 2 / 1 / +4.5 | 5 / 0 / -4.5 | +4.1, 1.3, -0.07, 0.29 | + 3Q25 4Q25 2Q26 |

The post-2022 result is stable for dead bands up to 1 point; the n 16 result is not significant at any band; both collapse at 1.5 points, which removes 3Q25, 4Q25 and 2Q26 from the accelerating bucket. 3Q22 (+0.30 pt, just over the band, stock -10.0%) is the one accelerating print that fails, and it is in the n 16 sample only; 4Q22 (decelerated, +12.6%) is the other print that separates the two samples.

**Regressions on the primary target (`C_feature_ranking.csv`, `C_univariate_tests.csv`).**

| Feature | 3Q22-2Q26 n | b | t | R2 | LOO R2 | perm p | 1Q23-2Q26 b | t | LOO R2 | perm p | 4Q21-2Q26 b | t | LOO R2 | perm p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Nights acceleration sign (-1/0/+1)** | 16 | +3.35 | 1.38 | 0.13 | -0.02 | 0.16 | **+5.66** | **2.65** | **+0.28** | **0.017** | +3.46 | 1.66 | +0.04 | 0.087 |
| Nights acceleration, points | 16 | +0.33 | 0.38 | 0.01 | -0.18 | 0.69 | +1.01 | 1.13 | -0.20 | 0.24 | +0.38 (winsorised) | 1.17 | -0.02 | 0.44 |
| Momentum score (sign + guide direction) | 16 | +2.48 | 1.17 | 0.12 | -0.11 | 0.18 | +3.90 | 2.16 | +0.14 | 0.032 | +2.44 | 1.53 | 0.00 | 0.12 |
| **Next-Q revenue guide vs Street (%)** | 16 | **+1.91** | **2.24** | **0.27** | **+0.15** | **0.040** | +1.47 | 1.35 | -0.03 | 0.18 | +1.39 (4Q21 clipped) | 2.38 | +0.15 | 0.022 |
| Guide direction code (-1/0/+1) | 16 | +0.98 | 0.29 | 0.01 | -0.23 | 0.75 | +1.35 | 0.40 | -0.27 | 0.69 | +2.41 | 1.01 | -0.07 | 0.29 |
| Guide direction, points | 16 | -0.03 | -0.03 | 0.00 | -0.20 | 0.98 | -0.06 | -0.05 | -0.25 | 0.96 | +0.71 | 0.65 | -0.12 | 0.46 |
| Revenue surprise vs consensus (%) | 16 | +0.44 | 0.22 | 0.00 | -0.14 | 0.86 | +0.69 | 0.33 | -0.18 | 0.77 | +0.48 | 1.51 | -0.17 | 0.15 |
| Revenue vs guide top (%) | 16 | +1.19 | 0.60 | 0.02 | -0.14 | 0.63 | +0.67 | 0.35 | -0.16 | 0.77 | +1.48 | 1.19 | -0.03 | 0.34 |
| EPS surprise (bps of price) | 14 | +0.03 | 0.13 | 0.00 | -0.26 | 0.91 | +0.15 | 0.50 | -0.14 | 0.67 | -0.07 | -2.74 | -0.01 | 0.20 |
| FY guide raised (0/1) | 16 | +2.27 | 0.45 | 0.01 | -0.14 | 0.66 | +3.02 | 0.60 | -0.16 | 0.56 | -0.29 | -0.06 | -0.12 | 0.94 |
| Nights surprise vs consensus (%) | 13 | +0.90 | 0.56 | 0.03 | -0.18 | 0.58 | +2.47 | 1.60 | -0.06 | 0.17 | +0.16 | 0.23 | -0.07 | 0.85 |
| Pre-print 20-day run-up (%) | 16 | +0.29 | 1.22 | 0.09 | -0.06 | 0.25 | +0.11 | 0.41 | -0.17 | 0.73 | +0.09 | 0.66 | -0.07 | 0.58 |

Only the guide-vs-Street row passes the pre-stated rule on the primary sample (and, with 4Q21 clipped, on the 19-print sample). The acceleration sign passes it on the post-2022 sample and is positive with the same order of magnitude in all three samples. The EPS coefficient on the full sample (-0.07, t -2.7) is the 2021 GAAP-EPS artefact WS04 also found; ignore it.

**Multiple change, gap, intraday and executable return, same features, 3Q22-2Q26 (`C_univariate_tests.csv`, `C_sorted_portfolios.csv`).**

| Feature | Multiple: b | t | LOO R2 | Multiple post-2022: b | t | LOO R2 | Open-entry: b | t | LOO R2 |
|---|---|---|---|---|---|---|---|---|---|
| Nights acceleration sign | +3.7 | 1.30 | -0.03 | **+6.4** | **2.52** | **+0.26** | -1.7 | -1.57 | +0.02 |
| Guide vs Street (%) | +1.8 | 1.54 | 0.00 | +1.0 | 0.70 | -0.19 | +0.2 | 0.62 | -0.13 |
| Guide direction code | +0.4 | 0.11 | -0.25 | +1.0 | 0.24 | -0.30 | +1.4 | 1.18 | -0.08 |
| Revenue surprise (%) | +0.9 | 0.36 | -0.13 | +1.1 | 0.45 | -0.16 | -0.4 | -0.45 | -0.12 |

| Bucket (3Q22-2Q26) | n | Gap excess (positive) | Intraday excess (positive) | Close-to-close excess |
|---|---|---|---|---|
| Accelerating | 6 | +4.9 (5 of 6) | -1.5 (2 of 6) | +3.4 |
| Decelerating | 9 | **-5.3 (1 of 9)** | **+1.7 (9 of 9)** | -3.6 |
| Between buckets | | Fisher p 0.011, MW 0.026 | Fisher p 0.011 | |
| Post-2022 accelerating / decelerating | 5 / 8 | +7.0 (5 of 5) / -7.0 (0 of 8) | -1.0 (2 of 5) / +1.4 (8 of 8) | +6.0 / -5.6 |

The multiple re-rates with the acceleration sign (accelerating prints +4.9% mean multiple change vs -2.9% decelerating). The whole conditional expectation is the gap: after the open, decelerating prints have retraced a fifth to a third of the gap 9 of 9 times, accelerating prints have given back 4 of 6 times. There is no post-open strategy in either direction; the expected close-to-close move belongs to a position held through the print.

**Multivariate (`C_multivariate_tests.csv`, primary target).**

| Spec | Sample | n | R2 | LOO R2 | perm p | const | b sign (t) | b guide dir (t) | b guide vs Street (t) | b rev surprise (t) |
|---|---|---|---|---|---|---|---|---|---|---|
| M1 sign + guide direction | 3Q22-2Q26 | 16 | 0.14 | -0.24 | 0.37 | -0.1 | +3.4 (1.4) | +1.1 (0.4) | | |
| M2 M1 + revenue surprise | 3Q22-2Q26 | 16 | 0.16 | -0.44 | 0.55 | -1.8 | +3.6 (1.3) | +1.2 (0.4) | | +1.0 (0.5) |
| M3 accel pts + guide pts | 3Q22-2Q26 | 16 | 0.01 | -0.44 | 0.92 | -0.7 | +0.39/pt (0.4) | +0.21/pt (0.1) | | |
| M5 M2 + EPS + FY raise | 3Q22-2Q26 | 14 | 0.19 | -1.96 | 0.84 | -1.9 | +4.1 (1.2) | +0.6 (0.2) | | +1.0 (0.4); EPS 0.0; FY +1.6 (0.4) |
| **M6 post-hoc: sign + guide vs Street** | **3Q22-2Q26** | **16** | **0.44** | **+0.21** | **0.019** | **-1.87** | **+3.86 (1.8)** | | **+2.06 (2.8)** | |
| M7 M6 + guide direction | 3Q22-2Q26 | 16 | 0.44 | +0.06 | 0.059 | -2.0 | +3.9 (1.7) | -0.3 (-0.1) | +2.1 (2.8) | |
| M8 M6 + revenue surprise | 3Q22-2Q26 | 16 | 0.44 | +0.02 | 0.057 | -1.8 | +3.9 (1.6) | | +2.1 (2.3) | -0.1 (0.0) |
| M1 | 1Q23-2Q26 | 14 | 0.43 | +0.09 | 0.048 | +0.2 | +5.7 (2.7) | +1.5 (0.6) | | |
| **M6** | **1Q23-2Q26** | **14** | **0.52** | **+0.29** | **0.009** | **-0.96** | **+5.46 (2.5)** | | **+1.32 (1.8)** | |
| M6 (4Q21 clipped) | 4Q21-2Q26 | 19 | 0.37 | +0.12 | 0.020 | -2.2 | +3.1 (1.5) | | +1.3 | |

Adding the guide direction to M6 costs LOO R2 (0.21 to 0.06) and its coefficient turns negative; adding the revenue surprise does the same. The two-variable M6 is the most that 16 prints support, and it is post-hoc; its guide-vs-Street coefficient depends on 2Q24 and 4Q22 (section 1 item 3, `C_fragility.csv`: drop both and the M6 LOO R2 is +0.01; drop 2Q24 and 2Q26 and it is -0.13).

---

## 5. Results: guide direction, and why it is not detectable

| Sample | Guide bucket | n | Mean | Median | Positive | Prints |
|---|---|---|---|---|---|---|
| 3Q22-2Q26 | accelerating | 3 | +2.5 | 0.0 | 1 | 2Q23 3Q24 2Q26 |
| 3Q22-2Q26 | accelerating, **2Q26 recoded stable** | 2 | -4.4 | -4.4 | 0 | 2Q23 3Q24 |
| 3Q22-2Q26 | stable | 2 | -7.7 | -7.7 | 0 | 1Q24 2Q25 |
| 3Q22-2Q26 | decelerating | 11 | -1.2 | -1.6 | 4 | 3Q22 4Q22 1Q23 3Q23 4Q23 2Q24 4Q24 1Q25 3Q25 4Q25 1Q26 |
| 3Q22-2Q26 | decelerating, **Q4 print** | 4 | **+7.1** | +8.5 | 3 | 4Q22 4Q23 4Q24 4Q25 |
| 3Q22-2Q26 | decelerating, non-Q4 print | 7 | **-5.8** | -5.1 | 1 | 3Q22 1Q23 3Q23 2Q24 1Q25 3Q25 1Q26 |
| 4Q21-2Q26 | accelerating | 5 | +4.8 | +3.7 | 3 | 3Q21 4Q21 2Q23 3Q24 2Q26 |
| 4Q21-2Q26 | decelerating | 12 | -1.0 | -1.1 | 5 | |

Cross-sort with the printed sign (3Q22-2Q26): printed accel + guide accel: 1 print (2Q26, +16.3); printed accel + guide decel: 5 prints, +0.8% mean, 3 positive (3Q22 3Q23 4Q24 3Q25 4Q25); printed decel + guide accel: 1 print (2Q23, 0.0); printed decel + guide decel: 6 prints, -2.8%, 1 positive; printed decel + guide stable: 2 prints, -7.7%. The accelerating guide has exactly one positive observation, it is 2Q26, and 2Q26 is the contestable code. With 2Q26 recoded stable, the M1 guide-direction coefficient is -0.3 (t -0.1) and the sign coefficient +3.3 (t 1.3).

Three readings, all JUDGEMENT:

1. The label distribution (3 / 2 / 11) means the test has almost no power. The right statement is "not detectable on three accelerating guides", not "no effect". What the data do rule out is the prior team's asserted "accelerating guide: +5% to +10%" as an established pattern: two of the three accelerating guides returned 0.0% and -8.8%.
2. The guide direction versus the printed rate is mostly seasonal arithmetic the market already knows (every Q4 print guides a decelerating Q1 on a hard comp; every Q2 print since 2023 has guided "stable" or "moderate" for Q3). A guide that says what the calendar says is not news. That is consistent with guide-vs-Street carrying a coefficient while guide-vs-printed does not; the 2Q26 guide was read as accelerating because it sat 2.6% above the Street's 3Q26 revenue and above the 10.3% just printed, not because of the direction alone.
3. At 20 days the guide-direction coefficient is +2.2 (t 0.5, LOO -0.30) on n 16; nothing there either.

---

## 6. The 2Q26 print as a case study (`C_case_study_2q26.csv`)

Inputs: raw +17.4%, of which the gap was +8.6% and the open-to-close +7.7% excess; NTM revenue estimate change -0.2%; EV/NTM revenue multiple +19.7%; nights +10.3% (acceleration +1.2 pts, beat vs StreetAccount +2.0%); revenue surprise +0.8%; EPS surprise +9.6%; 3Q26 nights guide "low double-digit" (+0.7 pts vs printed on the bucket midpoint; stable on a literal reading); 3Q26 revenue guide 2.6% above Street; FY26 revenue guide raised to "at least mid teens".

| Function | Fitted | Actual | Residual |
|---|---|---|---|
| M1 sign + guide direction, fit on 3Q22-2Q26 incl. 2Q26 | +4.5 | +16.3 | +11.8 |
| M6 sign + guide vs Street, incl. 2Q26 | +7.4 | +16.3 | +8.9 |
| M6 fit excluding 2Q26 | +4.9 | +16.3 | +11.4 |
| M1 fit excluding 2Q26 (guide-direction coefficient turns to -1.9) | -3.3 | +16.3 | +19.6 |

Every variable in the function pointed the right way on 2Q26 and the best of them explains under half of the move. The other 9 to 12 points are positioning and language (the stock had fallen from $141 to $152 over the prior quarter after two flat prints; the letter used "accelerated pace of Nights and Seats Booked"), which WS12 labels the multiple and WS03 labels language. 2Q26 is also the single observation that makes the guide-direction coefficient positive.

---

## 7. The 5 Nov breakeven

**Anchors (BRIEF).** 2Q26 printed nights +10.34%. Street 3Q26 nights +11.1% (148.9m), revenue $4,744m; Street 4Q26 revenue $3,154m (Bloomberg FA, 4 Sep) or $3,200m (Zacks, 4 Sep), nights +10.1%. Management delivered: 3Q26 nights +11.5%, revenue $4,815m; 4Q26 nights +10.5%, revenue $3,130m. Team base: 3Q26 +9.9% / $4,771m; 4Q26 +8.9% (8.0-8.2% if the ex-NA lap is adopted) / $3,111m. 3Q26 guide midpoint $4,730m. Nowcast: 3Q26 nights +9.5 to +10.0, band 8.5 to 11.0 (`docs/q3nowcast/SYNTHESIS.md`).

**Functions (`C_coefficients_used.csv`).** S1, pre-stated, **the headline**: E[r] = c + b x sign(acceleration); c -0.67, b +3.35 (3Q22-2Q26, residual sd 8.8) and c -0.45, b +5.66 (1Q23-2Q26, residual sd 6.9). S2, post-hoc M6, **illustrative**: E[r] = c + b1 x sign + b2 x (4Q26 revenue guide midpoint vs Street, %); c -1.87, b1 +3.86, b2 +2.06 (n 16, residual sd 7.3) and c -0.96, b1 +5.46, b2 +1.32 (n 14, residual sd 6.5). The revenue surprise (M8: -0.05 to +1.6 per 1%) and the guide direction (M7: -0.3 to +0.3 per step) are carried as sensitivities and change nothing by more than 1.5 points; the $4,815m vs $4,730m revenue cases are both in the grid. Mapping a 4Q26 nights guide to a revenue guide is carried at two elasticities (JUDGEMENT): the H-note 1.0% of revenue per point (anchored on management delivered, 10.5% at $3,130m) and the team's own 0.38% per point implied by its base (8.9% at $3,111m) against the delivered case; team-derived scenarios use the team elasticity.

**Named scenarios (`C_scenarios.csv`).** E is the expected day-1 close-to-close excess return. "Fitted mean p10/p90" is the bootstrap sampling range of the fitted expectation (3,000 resamples of the prints); "realised p10/p90" is E plus or minus 1.28 residual sd, the range for one print.

| Scenario | 3Q26 nights | Conditional on | 4Q26 nights guide | 4Q26 revenue guide | vs Bbg $3,154m | vs Zacks $3,200m | **S1 n 16** | **S1 n 14** | S1 n 16 fitted-mean p10 / p90 | S1 n 16 realised p10 / p90 | S2 n 16 Bbg / Zacks | S2 n 14 Bbg / Zacks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Team base (WS29/30)** | 9.9 | decelerating | 8.9 | 3,111 | -1.4% | -2.8% | **-4.0** | **-6.1** | -6.5 / -0.4 | -15.3 / +7.2 | -8.5 / -11.5 | -8.2 / -10.1 |
| Team base, ex-NA lap (4Q26 8.1%, team elasticity) | 9.9 | decelerating | 8.1 | 3,102 | -1.7% | -3.1% | -4.0 | -6.1 | -6.6 / -0.4 | -15.3 / +7.2 | -9.2 / -12.1 | -8.6 / -10.5 |
| Q3 nowcast central (9.75), stable 4Q guide, team elasticity | 9.75 | decelerating | 9.75 | 3,121 | -1.0% | -2.5% | -4.0 | -6.1 | -6.6 / -0.3 | -15.3 / +7.2 | -7.9 / -10.8 | -7.8 / -9.7 |
| Street (Bloomberg FA) | 11.1 | accelerating | 10.1 | 3,154 | 0.0% | -1.4% | +2.7 | +5.2 | -1.7 / +8.5 | -8.6 / +14.0 | **+2.0 / -1.0** | +4.5 / +2.6 |
| Management delivered | 11.5 | accelerating | 10.5 | 3,130 | -0.8% | -2.2% | +2.7 | +5.2 | -1.5 / +8.2 | -8.6 / +14.0 | **+0.4 / -2.5** | +3.5 / +1.6 |
| Flat print, stable guide, revenue at Street | 10.34 | flat | 10.34 | 3,154 | 0.0% | -1.4% | -0.7 | -0.5 | -4.0 / +1.6 | -11.9 / +10.6 | -1.9 / -4.8 | -1.0 / -2.9 |
| Accelerating, 4Q26 guide 2% below Street | 11.0 | accelerating | 9.3 | 3,091 | -2.0% | -3.4% | +2.7 | +5.2 | | | -2.1 / -5.0 | +1.9 / 0.0 |
| Decelerating, 4Q26 guide 3% above Street | 9.9 | decelerating | 14.3 | 3,249 | +3.0% | +1.5% | -4.0 | -6.1 | | | +0.5 / -2.6 | -2.5 / -4.4 |
| 2Q26 replay: accelerating, guide +2.6% vs Street | 11.0 | accelerating | 13.9 | 3,236 | +2.6% | +1.1% | +2.7 | +5.2 | | | +7.4 / +4.3 | +7.9 / +6.0 |
| **Team base, unconditional over the nowcast band** (centre 9.9, sd 0.85: P accel 0.21, flat 0.20, decel 0.59) | | mixture | 8.9 | 3,111 | -1.4% | -2.8% | **-1.9** | **-2.6** | | | -6.1 / -9.1 | -4.8 / -6.7 |
| Team base, unconditional (centre 9.75, sd 0.75: P accel 0.13, flat 0.19, decel 0.67) | | mixture | 8.9 | 3,111 | -1.4% | -2.8% | **-2.5** | **-3.5** | | | -6.8 / -9.7 | -5.7 / -7.6 |

The vendor comparator flips the sign of the Street and management-delivered scenarios under S2 (Bloomberg +2.0% / +0.4%; Zacks -1.0% / -2.5%) and moves the team base from -8.5% to -11.5%; the number that matters is the 4Q26 consensus on the tape on 5 Nov, which is neither. S1 has no vendor sensitivity. Under a Street-centred distribution (11.1, sd 0.85: P accel 0.73) the unconditional S1 expectation is +1.4% to +3.0% (`C_unconditional.csv`).

**Zero-expected-reaction contour (`C_breakeven_zero_contour.csv`).** S1 has no guide term, so the "priced" print under the headline function is simply the accelerating bucket: no 4Q26 guide offsets a decelerating print or is needed to support an accelerating one. S2 (illustrative):

| Printed 3Q26 nights | S2 sample | E if the 4Q26 guide is at Street | Breakeven 4Q26 guide vs Street | In $m vs Bbg / Zacks | Implied 4Q26 nights guide at 1%/pt (H-note) / at 0.38%/pt (team) |
|---|---|---|---|---|---|
| Accelerating (> 10.6%) | n 16 | +2.0% | -1.0% | 3,123 / 3,169 | 10.3 / 10.0 |
| Accelerating | n 14 | +4.5% | -3.4% | 3,047 / 3,091 | 7.8 / 3.5 |
| Flat (10.1-10.6%) | n 16 | -1.9% | +0.9% | 3,183 / 3,229 | 12.2 / 14.9 |
| Decelerating (< 10.1%) | n 16 | -5.7% | **+2.8%** | **3,242** / 3,289 | 14.1 / 19.9 |
| Decelerating | n 14 | -6.4% | **+4.9%** | **3,307** / 3,356 | 16.2 / 25.4 |

Read: under S2, an accelerating print absorbs a 4Q26 revenue guide 1% to 3% below Street at zero expectation; a decelerating print needs a guide 3% to 5% above Street, which on either elasticity is a 4Q26 nights guide of 14% or more (20% or more on the team's own elasticity). Not a plausible letter, so on both functions the 3Q26 nights sign dominates the 4Q26 guide. The full grids are in `C_breakeven_grid_nights_x_guidepts.csv` (3Q26 nights 8.5-12.5 by 0.25 x 4Q26 guide -3 to +2 points vs printed, both revenue cases, both elasticities, six functions) and `C_breakeven_grid_nights_x_gvs.csv` (3Q26 nights x 4Q26 guide vs Street -4% to +4%).

**What the team base case implies, and how confident.** Conditional on a decelerating print, every function gives a negative expectation: -4.0% (S1, n 16), -6.1% (S1, n 14), -8 to -12% (S2, post-hoc, both comparators). The sign is robust because the decelerating bucket mean is negative in every sample with 1 of 9 (excess) positive; "100% of bootstrap refits negative" is close to automatic given that and is not additional evidence. The magnitude is not robust: the fitted-mean sampling range is -6.5% to -0.4% on S1 (n 16), the realised-move range -15% to +7%, and decelerating prints have closed at -12.3% (2Q24) and +12.6% (4Q22, a Q4 print guiding a hard Q1 comp). Unconditionally, on the nowcast band, -1.9% to -3.5% (S1). JUDGEMENT on how to quote it: "a decelerating 3Q26 nights print has been sold 8 of 9 times since 3Q22 on the excess convention (6 of 9 on raw), mean -4% to -6% close to close, captured only by holding through the print; the nowcast band gives roughly a one-in-five chance the print accelerates instead, in which case the same history says +3% to +5%". Do not quote -8.5% as a point forecast.

---

## 8. Critique of the prior breakeven (`04_q3_2026_breakeven.csv`; `C_prior_breakeven_critique.csv`)

| Line | Prior | Reproduced | Comment |
|---|---|---|---|
| Median revenue beat vs consensus, post-2022 | +1.70% -> $4,821m | +1.70% -> $4,825m | Reproduces (same 14 prints; $4,744m Bloomberg vs $4,740m Zacks) |
| Median revenue beat vs guide midpoint, post-2022 | +2.15% -> $4,832m | +2.18% -> $4,833m | Reproduces to rounding |
| Street 3Q26 nights bar | "not published", derived ~144-146m (+8-9%) | Bloomberg FA 148.9m = **+11.1%** (ANCHOR) | Superseded. The Street bar is 2.5-3 points above the derived one and above the 2Q26 rate. The Street expects an accelerating print; the prior file assumed a decelerating bar |
| Reaction content | Revenue above $4.74bn "carries no information"; nights beat vs StreetAccount > 1.8% -> positive 20-day drift | Revenue surprise day-1 b +0.4 to +0.7 per 1%, LOO negative in every sample; the 20-day nights-drift rule fails an executable entry (WS20, LOO -0.016) | The prior file is a table of consensus bars, not a reaction breakeven. Its one reaction claim has since been retracted. Its conclusion that the revenue line is uninformative is confirmed here |
| 4Q26 revenue consensus | Zacks $3,200m (range 3,050-3,700) | Bloomberg FA $3,154m | This is the one pre-stated feature with a day-1 coefficient on the primary sample (+1.9% per 1% above Street, n 16, fragile). The vendor choice is a 1.5% swing in guide-vs-Street, about 3 points of S2 expected reaction, and flips two scenario signs |

---

## 9. What cannot be identified with 23 prints, and what a 24th adds

**Not identifiable here.**

1. **Guide direction vs the printed rate against guide direction vs the Street's next-quarter nights.** There is no history of a next-quarter nights consensus (WS04 found none), so the "accelerating guide" effect can only be tested against the printed rate (not detectable on three observations) or proxied by the revenue guide vs Street (works on n 16 and n 19, fails on n 14, rests on two prints). For 5 Nov the Street's 4Q26 nights number is +10.1% against a 3Q26 of +11.1%, so the Street itself expects a decelerating nights guide; a "stable" guide would be above Street. Which comparison the market makes is the question, and it cannot be settled on this data.
2. **A slope on nights.** The acceleration in points is not significant in any sample (Spearman 0.20 on n 16, 0.38 on n 14). A 3Q26 print of +10.8% and one of +12.5% get the same expected reaction here. That is a power limit at 14 to 16 observations, not a finding that the slope is zero.
3. **The Q4-print seasonal.** Decelerating guides at Q4 prints average +7% (4 prints), elsewhere -6% (7 prints). With four observations this could be "the market looks through the Q1 comp" or four coincidences; it was found after the guide-direction test failed and is a reading, not a result. 5 Nov is a Q3 print.
4. **Language and positioning.** 2Q26 leaves a 9 to 12 point residual on the best function; WS03 attributes such residuals to tone. Nothing in a 23-print numeric panel identifies that.
5. **The multiple's reaction separately from the price's.** The WS12 multiple change is computed from the same price move with a guide-implied estimate path. A genuinely separate test needs a consensus-estimate vintage around each print.
6. **Whether guide-vs-Street is real or the expected false positive.** It is the one pre-stated survivor on the primary sample and it has prior support (the 9-of-9 20-day rule) and an economic story, which is why it is carried; it fails on n 14, loses its LOO R2 when 2Q24 or 4Q22 is dropped, and would not survive Holm.

**What a 24th observation (5 Nov) adds.**

- If 3Q26 nights decelerate and the stock closes up on the day (excess vs QQQ), the post-2022 decelerating bucket goes from 0 of 8 to 1 of 9 positive on excess, and the 0-of-8 is confirmed as the knife edge it is; the team should stop quoting the rule as near-deterministic. If it decelerates and closes down, 0 of 9 on excess and the sign rule is as good as 23 prints can make it. Either way the raw count (2 of 8) should be quoted beside it.
- If nights accelerate and the stock falls, that is the second such case (3Q22 was the first in the sample) and the accelerating-bucket hit rate drops from 4 of 6 to 4 of 7.
- The 4Q26 guide will almost certainly be a bucket ("high single digits" or "low double digits"), the fourth bucket guide. It tests the guide-vs-Street coefficient at a known Street number if the team captures the Bloomberg and Zacks 4Q26 revenue consensus on 4 Nov (WS20 item 13.3 asked for the same).
- Score the S1 and S2 point forecasts against the realised day-1 excess. One observation cannot validate a coefficient, but a realised move outside -15% to +7% on a decelerating print, or a positive close on a guide more than 1% below Street, would each be a direct contradiction of the function's terms.

---

## 10. Caveats

1. **Multiple testing.** 420 regressions here on top of 661 prior; 17 primary. Nothing pre-stated clears Holm. One pre-stated survivor on the primary sample (guide vs Street, fragile), one feature (acceleration sign) that is positive everywhere and passes the rule only on the secondary sample, and one post-hoc combination. The correct reading is "two variables with the right sign everywhere and a plausible mechanism, re-tested on prints the team had already looked at", not "a fitted model".
2. **The sample the result lives in.** The post-2022 sign result (n 14, t 2.7, LOO +0.28, perm p 0.017) is the strongest statistic; on 3Q22-2Q26 (n 16) the same coefficient is +3.4 with t 1.4 and LOO -0.02, because 3Q22 (accelerated +0.3 pt, stock -10%) and 4Q22 (decelerated, +12.6%) are in it. Two prints move the statistics from significant to not; the dead-band table in section 4 shows the same.
3. **Convention.** All coefficients are on the close-to-close excess return. The gap is the reaction (decelerating prints gap -5.3% and bounce +1.7% intraday); the function describes the revaluation, not a capturable return, and the open-entry coefficients are zero or wrong-signed. The 0-of-8 is 2-of-8 on raw returns.
4. **Coding judgements.** 4Q24, 1Q23 and 2Q26 guide directions, the 0.25-point dead band, the +/-2 scale for directional guides, and the 2019-basis 2021 codes are mine and are documented in `C_guide_direction_coding.csv` and `C_fragility.csv`. The FY-raise variable uses the existing team coding (5 raises); 1Q22 and 2Q23 could be argued as raises and are not.
5. **The mapping from a 4Q26 nights guide to a revenue guide** is carried at two elasticities, the H-note 1.0%/pt and the team's own 0.38%/pt; the contour's implied nights guides are quoted at both and the direction of the conclusion is the same at either.
6. **Vendor and vintage.** The historical guide-vs-Street series is LSEG/Refinitiv at the print date (WS04); the 5 Nov inputs are Bloomberg FA and Zacks from 4 Sep, and the two differ by 1.5% on 4Q26 revenue, enough to flip two S2 scenario signs. Consensus will move before the print, and the Street's 3Q26 nights bar (148.9m) is a Bloomberg population, not the StreetAccount series the historical nights-surprise column uses.
7. **Workstream B.** B's `cc_1d_pct` in `B_print_base_rates.csv` and `B_reconcile_reaction_files.csv` is the same QQQ-excess close-to-close series used here (`20_executable_returns.csv` legacy_1d_pct), not a raw close-to-close return; B's 6/2 and 1/10 counts are the 19-print sample with no dead band and reconcile exactly with this panel's 5/7 and 1/10 plus 1Q22 and 3Q24 as flat. B's implied move is not used here; it gives the unconditional dispersion (B's Bloomberg-based event sd is 6.5 to 10%; the historical mean absolute day-1 move is 7.1%), which is the sd around the expectations in section 7, not a substitute for them.
8. **The 20-day series** now comes from `20_executable_returns.csv` (legacy_20d_pct, full precision, includes 2Q26 at +21.7%), so the 20-day base rates differ slightly from the predictive study's (mean -3.5% on 23 prints here vs -4.7% on 22 there).

---

## 11. Files

| File | Content |
|---|---|
| `analysis/src/reverse_dcf/C_01_print_panel.py` | Builds the panel and the guide-direction coding table |
| `analysis/src/reverse_dcf/C_02_reaction_tests.py` | Univariate, multivariate, sorted portfolios (with Fisher / Mann-Whitney between buckets, gap and intraday targets), feature ranking, 2Q26 case study, dead-band sensitivity, Holm table, fragility, test count |
| `analysis/src/reverse_dcf/C_03_breakeven.py` | Coefficients used, scenarios (S1 headline, S2 both comparators, bootstrap of the fitted mean, realised-move range, unconditional rows), two breakeven grids at two elasticities, zero contour, base rates, prior-breakeven critique |
| `data/processed/reverse_dcf/C/C_print_panel.csv` | 23 prints x 64 columns: returns (raw, excess at full precision and one decimal, gap, intraday, executable, 5d, 20d), multiple and estimate change, nights growth and acceleration, consensus surprises, guide direction and quote, guide vs Street (raw and clipped), FY raise, run-up, sample flags |
| `C_guide_direction_coding.csv` | 23 rows: the coding, quote, basis, realised next-quarter outcome, day-1 return, coding notes |
| `C_univariate_tests.csv` | 252 rows (12 features x 7 targets x 3 samples), primary flag, HC1 t, R2, LOO R2, permutation p, LOO coefficient range, survives-rule flag |
| `C_multivariate_tests.csv` | 168 rows (8 specs x 7 targets x 3 samples), primary and post-hoc flags |
| `C_feature_ranking.csv` | 12 features ranked by LOO R2 on the primary target and sample, with the other samples, the multiple and the open-entry return |
| `C_sorted_portfolios.csv` | 688 rows: bucket means, medians, hit rates, binomial p vs 0.5 and vs the sample base rate, Fisher and Mann-Whitney between top and bottom buckets, prints per bucket, for 5 sorts x 9 targets x 3 samples |
| `C_deadband_sensitivity.csv` | The sign result at dead bands 0 / 0.25 / 0.5 / 1.0 / 1.5 points, both samples, with the prints made flat |
| `C_multiplicity_holm.csv` | Holm step-down over the 17 pre-stated specs and over the 36 primary-target univariate tests |
| `C_fragility.csv` | Guide-vs-Street and M6 with 2Q24 / 4Q22 / 2Q26 dropped; guide-direction buckets and M1 with 2Q26 recoded stable |
| `C_case_study_2q26.csv` | 2Q26 fitted vs actual under every spec, with and without 2Q26 in the fit, plus the WS12 decomposition |
| `C_test_count.csv` | Tests run here and previously |
| `C_coefficients_used.csv` | The six functions used in the breakeven, with status (pre-stated headline / post-hoc illustrative / sensitivity) |
| `C_scenarios.csv` | 12 rows: 10 named scenarios plus two unconditional mixtures, with S1 and S2 (both comparators) expectations, fitted-mean and realised-move ranges |
| `C_unconditional.csv` | P(accelerate / flat / decelerate) under three band shapes x three guide cases, with the unconditional expectation under each function |
| `C_breakeven_grid_nights_x_guidepts.csv` | 3Q26 nights 8.5-12.5 x 4Q26 guide direction in points x revenue case x elasticity |
| `C_breakeven_grid_nights_x_gvs.csv` | 3Q26 nights x 4Q26 revenue guide vs Street, with implied nights guides at both elasticities |
| `C_breakeven_zero_contour.csv` | The zero-expected-reaction combinations (S1: bucket means; S2: breakeven guide vs Street) |
| `C_base_rates.csv` | Unconditional day-1 (raw, excess, gap, intraday, open-entry), multiple and 20-day statistics by sample |
| `C_prior_breakeven_critique.csv` | Reproduction and critique of `04_q3_2026_breakeven.csv` |

## 12. Audit fixes applied (13 Sep)

| Finding | Applied |
|---|---|
| 1 excess vs raw counts, between-bucket test | Both counts in sections 1 and 4; Fisher and Mann-Whitney between buckets in `C_sorted_portfolios.csv`; base-rate binomial added; "sold 8 of 8" removed |
| 2 re-test, not confirmation; Holm | Section 1 item 1 and section 2 reworded; `C_multiplicity_holm.csv`; both samples side by side |
| 3 dead-band sensitivity | `C_deadband_sensitivity.csv`, table in section 4 with the prints that move |
| 4 guide direction "not detectable" | Section 1 item 2 and section 5 relabelled; 2Q26-stable recode in `C_fragility.csv` and section 5 |
| 5 conditional vs unconditional; bootstrap meaning | Unconditional rows in `C_scenarios.csv` and `C_unconditional.csv`; one-liner rewritten; fitted-mean vs realised-move ranges separated |
| 6 S1 headline, S2 illustrative; fragility; Zacks; mapping | S1 first everywhere; `C_fragility.csv`; Zacks column beside Bloomberg; mapping at both elasticities, team scenarios on the team elasticity |
| 7 gap / intraday | Section 1 item 6, section 4 table, one-liner |
| 8 Mann-Whitney 0.145 | Corrected |
| 9 4Q21 clipped in the all sample | `guide_vs_street_pct_clipped`, used for the 19-print sample only; result reported in section 1 item 3 |
| 10 full-precision target | `legacy_*_pct` from `20_executable_returns.csv`; the one-decimal series kept as `ret_1d_cc_excess_1dp_pct` |
| 11 wording | "only variable that works in every sample" and "threshold not slope" softened |
| 12 mapping anchor | Team elasticity 0.38%/pt used for team-derived scenarios |
| 13 B's series label | Caveat 7 |
