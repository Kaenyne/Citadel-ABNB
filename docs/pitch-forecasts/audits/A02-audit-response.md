# Response to audit A02 (C02 q4-nights-bucket, C03 fy26-revenue-guide-language)

Response date: 2026-09-17
Responds to: `A02-research-audit.md` (Astra, gpt-6-astra, read-only)
Revised research: `questions/q4-nights-bucket/research-log.md` (revision 2); `questions/fy26-revenue-guide-language/research-log.md` (revision 2)
Revised forecasts: both `forecasts/2026-09-17-forecast.json` (revision 2)
Revised models: `questions/q4-nights-bucket/datasets/decomposition_v2.py` (+ `nights_descriptor_vs_printed_and_comp_v2.csv`); `questions/fy26-revenue-guide-language/datasets/decomposition_v2.py`. The revision-1 scripts, datasets and outputs are left untouched as the audit trail.
Reproduction script: `A02-reproduce.py` (the audit's script, saved verbatim — `diff` against the listing in the audit is empty); output in `A02-reproduce.stdout.txt` and at the end of this file.

This response was written in two passes: the first agent reproduced the audit, revised both logs and JSONs and saved the script, and was cut off before writing this document; the second agent re-ran the script, checked the revision-2 files against each other and against the audit, and wrote this file. Nothing in the revision-2 logs or JSONs was changed in the second pass.

## Summary

Sixteen findings (ten major, six minor). **Sixteen accepted, none in part, none rejected.** Every number in the audit reproduced exactly: the script ran clean from the repo root under `py -3.13 -B` with no path fix, all 17 next-quarter nights quotes and 3 FY revenue quotes matched the saved letters, and every count, cushion, kappa, normal-bin, tree and consensus figure in the findings table matches the script's output below. Astra's two comparison vectors also reproduce (C02 unrounded 0.171484 / 0.178516 / 0.30 / 0.30 / 0.05; C03 0.346856 / 0.1925 / 0.209775 / 0.100869 / 0.15 on a $14,174.3M mean).

In three cases the repair adopted is not the audit's illustrative one, and the finding-by-finding section says why: A02-03 uses R01's print distribution N(9.67, 1.70) rather than the audit's N(9.5, 1.48) (the audit's normal is carried as sensitivity row S1d and lands one point from the final); A02-04 takes P(no FY sentence) to 0.12, not the raw 1-in-4 or Astra's 0.15; A02-05 lets the Kalshi ladder into C02 through R01's blend at weight 0.1 rather than as a direct anchor.

Headline vectors (a–e), revision 1 → revision 2:

- **C02** (0.21, 0.19, 0.39, 0.17, 0.04) → **(0.18, 0.17, 0.30, 0.31, 0.04)**. The leading option moves from (c) "high single digits" to (d) by one point; the two are a coin flip on whether the letter names a bucket or writes "moderate", and the memo should quote (c)+(d) = 0.61 as the deceleration-language block. Astra: (0.17, 0.18, 0.30, 0.30, 0.05) — within one point on every option.
- **C03** (0.37, 0.18, 0.28, 0.08, 0.09) → **(0.36, 0.16, 0.28, 0.08, 0.12)**. (a) "raised" still leads. Astra: (0.35, 0.19, 0.21, 0.10, 0.15) — the only gap above three points is (c), +0.07, named in the final table.

What actually moved C02: (i) the revision-1 base rate split the historical "down" descriptors 2:1 into (c):(d), but on the question's own labels 8 of 17 descriptors (9 of the 10 down-class ones) resolve (d) — this was not in the audit and was found in reproduction; (ii) replacing the hard-coded 0.38 / 0.42 / 0.20 Q3 branches with R01's distribution moves ~0.12 of mass from the 9–10 branch into the <9 branch, where (d) is the modal outcome; (iii) the branch conditionals are now format × content with every parameter printed, so the directional-"moderate" path to (d) is explicit (0.19 of the 0.31). What moved C03: almost nothing on the headline — the corrected anchor lifts the anchor's (a) from 0.30 to 0.38 but carries only 0.2 of the blend; (e) rises 0.03 for the 3Q22 omission precedent; the shared-demand correlation moves mass from (c) to (d) inside the numeric branch and the base-rate rebuild moves it back, so (c) and (d) net to unchanged.

## Finding-by-finding

Dispositions are those recorded in each log's `## 10. Revision notes`; the recomputations are from `A02-reproduce.py` and the two `decomposition_v2.py` scripts.

### A02-01 (major, C03) — quarterly kappa applied to the whole FY consensus: accepted
Reproduced: kappa from the L0 `AP-*-revenue` rows matched to quarterly guides is 0.603954%, n 12, sample sd 0.30pp, trailing-eight 0.515673%; $14,189.557 / 1.006 = $14,104.93M (+15.23%) reproduces the faulty revision-1 anchor. Fix (claim 10): the anchor now deflates only the not-yet-guided quarter — 1H26 actual $6,286M + LSEG 3Q26 $4,744.3M + LSEG 4Q26 $3,161.8M / 1.006 = **$14,173.3M, +15.79%** (deflating the Q4 leg of the annual figure instead gives $14,170.7M, +15.76%; both are on the same side of the 15.5% rounding line, unlike revision 1's 15.23%). The anchor vector moves from (a) 0.30 to (a) 0.38, and revision 1's "+0.07 divergence from the anchor" is withdrawn as an artefact: team 15.73% and Street 15.79% agree within 0.06pp. Monitoring row 6 now specifies this construction for the 4 Nov re-registration.

### A02-02 (major, C02) — the 4Q24 comparator and the pending-guide exclusion: accepted
Reproduced from the 4Q24 letter: "relatively stable compared to Q1 2024 after excluding Leap Day" compares with 1Q24's 9.496% less about a point, not the 12.348% just printed; the driver history confirms 1Q24 − 1 < 4Q24. Re-classed "down". The 2Q26→3Q26 "low double-digit" bucket (11 vs 10.342% printed, "up") is included because the study object is the descriptor, not its accuracy. The 1Q23 "lower than our revenue growth" comparator was verified separately (claim 25): the 2Q23 revenue guide's top, $2,450M on $2,104M = +16.4%, sits below the 18.6% just printed, so "down" holds. Corrected counts: **down 10 / stable 4 / up 3** on 17; resolved-only 10/4/2 (n 16); W1 9/2/3 (n 14); W2 6/2/2 (n 10); excluding both indirect comparators 8/4/3 (n 15). New dataset `nights_descriptor_vs_printed_and_comp_v2.csv`; convention 4 added in §0b for non-adjacent comparators.

### A02-03 (major, C02) — hard-coded Q3 branch probabilities: accepted
Reproduced: under N(9.5, 1.48²) the ≥10 / 9–10 / <9 masses are 0.367743 / 0.264515 / 0.367743, and the most a normal with sd 1.48 can put in a one-point interval is 0.264515, so revision 1's 0.42 on 9–10 was not derivable from any stated distribution. Holding revision 1's conditionals fixed and using the audit's normal gives (0.199, 0.169, 0.382, 0.216, 0.034), which reproduces. Fix: the branches are now taken from R01 (batch A09, written after revision 1 and after the audit), whose calibrated print distribution is N(9.67, 1.70) with P(≥10.0) = 0.42 — the number R01 §5 says X01 and C02 should use — giving masses **0.423 / 0.230 / 0.347** (claim 24). The audit's N(9.5, 1.48) is carried as sensitivity S1d: (0.18, 0.17, 0.30, 0.32, 0.03), one point from the final on (d), so the choice between the two distributions does not decide the leading option; the P(directional) assumption does (S2a/S2b).

### A02-04 (major, C03) — the November reference class omits 2022: accepted
Reproduced from `05_guide_language_pattern.csv`: November FY sentence types 3Q21 none, 3Q22 none, 3Q23 approx_yoy, 3Q24 approx, 3Q25 approx; the 2Q22 letter carried an FY2022 margin-expansion sentence that the 3Q22 letter dropped; the two numeric-floor conversions were +50bp each, not +1pt; FY revenue updates are 2 of 2 raises with zero prior November updates of the line. Fix (claim 2, §5): the class is now "November letters with an existing same-year FY guide", n 4: **convert 3, omit 1, reiterate 0** (raw Laplace 0.57 / 0.29 / 0.14), regime-conditioned to 0.70 / 0.15 / 0.15 and labelled an analogical judgment on a margin line, not an MC frequency for the revenue line. The +0.5pp step maps to "approximately 15.5%", which resolves (c) as readily as a rounded "approximately 16%" resolves (a), so the conversion mass is split 0.47 / 0.47 / 0.06 (a / c / d). P(e) rises 0.09 → 0.12 rather than to the raw 0.25 or Astra's 0.15 because the 3Q22 sentence that vanished was a qualitative y/y margin line the Q4 guide had made redundant, while the 2026 revenue line is a headline numeric line that both 2026 letters lead with (claim 12); the raw-omission case is sensitivity S5 (P(e) 0.25 → (a) 0.31).

### A02-05 (major, both) — "quotes only, no volume" and the "inconsistent ladders": accepted
Reproduced from the saved 148m contract: `volume` None, `volume_fp` **428.14**, `open_interest_fp` **423.14**, `liquidity_dollars` 0.0000, bid 0.50 / ask 0.55; the other rungs carry `volume_fp` 50–999, `volume_24h_fp` 0, `updated_time` 2026-08-04. Revision 1 read the empty legacy fields; withdrawn in both logs (C02 claims 14–15, C03 claim 14). The market is now described as thin but traded around the 6 Aug guide and quiescent since; its implied median (~148m, +10.8%) coincides with the Bloomberg Street (149m) and disagrees with the team band, and it enters C02 as contrary evidence through R01's blend (weight 0.1) rather than being dismissed. The "mutually inconsistent ladders" claim is reworded: medians of two marginals need not add, so the Q3 and FY ladders leaving 4Q26 at ≈120m (−1.6%) is not a contradiction, only evidence that no one is pricing the two jointly.

### A02-06 (major, both) — the three estimates are not independent: accepted
Reproduced: C02's revision-1 anchor vector was a literal dictionary and its base rate assumed the 2:1 split; C03's base and anchor vectors were literal dictionaries. Fix: both logs keep `NOT_INDEPENDENTLY_DERIVED` and now say what each vector shares (the letters, the team baselines, one level-to-language mapping); every branch conditional is format × content with the parameters printed; the anchors are labelled "dependent judgmental construction — the level is external, the vector is ours"; the blend weights (0.5 / 0.3 / 0.2) are stated and the mapping is varied in §7. The revision-1 six- and seven-point final–anchor differences are no longer claimed as evidence of agreement: C03's was an artefact (A02-01), and C02's +0.08 on (d) is now attributed to the base rate alone.

### A02-07 (major, C03) — the bridge's "80% band" and the independence of the two errors: accepted
Reproduced: `h1_to_h2_bridge_v3.py:436–437` computes `revenue_low/high` as lagged GBV × min/max historical conversion, which gives exactly $3,156.008–3,201.217M; `math.hypot(40, 80)` was the zero-correlation assumption. Fix (claims 7, 9): the band is named a historical-conversion envelope with lagged GBV fixed; the $40M / $80M sds are labelled assumptions; a shared-demand correlation **ρ = 0.5** is adopted, giving FY sd **0.86pp** (0.73 at ρ 0, 0.94 at ρ 0.8) and, given a numeric sentence, (d) 0.14 (0.10 at ρ 0) and (c) 0.36 (0.40 at ρ 0). ρ moves (c)/(d) and leaves (a) unchanged; both alternatives are §7 rows.

### A02-08 (major, C02) — five bucket rows as a "1–3 point cushion": accepted
Reproduced: 5 of 5 resolved nights/GBV bucket rows above the top, but three print events and only two nights observations (+4.82 / +1.15pp vs the midpoint; +3.82 / +0.15 above the top). Fix (claim 4, §4): the conservatism is kept with n and clustering explicit; "Street minus 1–3 points" is now a sensitivity assumption inside the anchor's level-to-language mapping (0–2pt margin), not a measured policy, and the log no longer claims it identifies management's expectation.

### A02-09 (major, C02) — ordinal unions that turn language into thresholds: accepted
Reproduced: the 3Q23 letter's "moderate" came with a call remark of "a few points below" 13.5%, so the language category imposes no ≤9% ceiling. Fix (§6): literal unions **P(a or b) = 0.35**, **P(c or d) = 0.61**, with the sub-splits carried for X01 — (d) = directional-moderate 0.19 + explicit mid-single 0.12; (b) = directional-similar 0.06 + around-10 / hyphenated bucket 0.11 — and the JSON carries them as `unions` and `subsplits`.

### A02-10 (major, C03) — revenue language substituted for the X01 margin-floor leg: accepted
Reproduced from QUESTIONS.md X01: the short-case leg is "FY26 margin floor weakened" (C04). Fix (§6, JSON `x01_note`): the mapping is removed; C03(d) cannot satisfy the trigger. The correlation through the Q4 revenue guide (a midpoint below ≈$2,990M lowers both the implied FY revenue and the achievable FY margin) is stated as a joint assumption, P(C04 = d | C03 = d) ≈ 0.5 versus the C04 marginal, for X01 to use or replace.

### A02-11 (minor, C02) — 8.5–10.0 vs the source's 8.5–11.0: accepted
Reproduced: `docs/q3nowcast/SYNTHESIS.md` lines 9, 19, 40 and `h2_bridge_v3_rebased_lines.csv` carry 8.5–11.0. Fix (claim 8): the source band and the brief's imposed conditioning band are both stated, with the note that neither specifies probabilities; the distribution actually used is R01's (claim 24), and the reviews-index error sample (n 10, RMSE 1.48, mean −0.46, sample sd 1.48) is cited for what it is.

### A02-12 (minor, C02) — two wrong counts: accepted
Reproduced: `nq_nights_dir` is −1 in 8, 0 in 6, +1 in 3, NaN in 6 (not 9 negative); the nights ledger is 14 directional of 17, 11 of 11 before 2025 (not "12 of 16"). Both corrected (claims 3, 18) with the window stated, and the reaction panel is labelled a derived encoding of the same letters, not independent corroboration — it also codes 4Q24 as 0 where the corrected class is "down".

### A02-13 (minor, C02) — "45th percentile": accepted
Reproduced: `team_position_pct_of_range` = (132.7 − 130) / (136 − 130) = 45%. Claim 13 now says "45% of the way from the minimum to the maximum".

### A02-14 (minor, C03) — the EBITDA n and the missing observation date: accepted
Reproduced from `03_current_consensus.csv`: 3Q26 / 4Q26 revenue n 37 (EBITDA n 36), FY26 n 44; means $4,744.32 / $3,161.82 / $14,189.56M; row date 2026-09-11, revenue observation date 2026-09-07. Claims 6, 7 and 10 carry the metric-specific n and both dates and cite the provenance file; the freshness note now says the 7 Sep observation is 10 days old (above the 7-day cap) and monitoring row 6 re-registers it on 4 Nov.

### A02-15 (minor, both) — "credible ranges" with no coverage: accepted
Both §6 sections and both JSONs now call them sensitivity ranges (`leading_option_sensitivity_range`), defined as the span of the §7 rows over stated assumption reversals, with no coverage claim.

### A02-16 (minor, C02) — the 80% concentration and the missing joint table: accepted
Reproduced: 0.38 × 0.42 / 0.2116 = 75.4253% under the revision-1 tree. The revision-2 tree gives P(Q3 ≥ 10 | a) = **0.92** (0.184 / 0.201) and P(Q3 < 9 | d) = 0.57, and §6 publishes the full branch × option joint table (row masses 0.423 / 0.230 / 0.347; column sums equal the decomposition to ±0.001), which the JSON carries as `conditioning.joint_branch_x_option` for X01.

## What the audit missed

1. **The 2:1 split of "down" descriptors into (c):(d) was the largest single error in C02.** Astra corrected the descriptor classes (A02-02) and criticised the split as a judgment (A02-06), but did not map the corrected classes onto the question's own labels. Doing so puts 8 of 17 descriptors on (d) — 0.47 unconditionally, 0.50 in W1, 0.40 in W2 — against revision 1's base-rate (d) of roughly 0.20. Nine of the ten down-class descriptors are directional sentences with no bucket, which the fine print resolves as (d) whatever the level. This, not the branch masses, is why (d) rises from 0.17 to 0.31; it is recorded in C02 §10 as "missed by the audit, found in reproduction".
2. **The reaction panel shares the 4Q24 error.** The audit used `abnb_guidance_reaction_panel.csv` to correct the direction counts (A02-12) while flagging 4Q24 in the ledger (A02-02); the panel codes 4Q24 as 0 ("stable") from the same sentence. The two sources are one encoding; the log now says so (claim 18).
3. **(b) has no precedent as a nights bucket.** Management has never written "around 10%" or a hyphenated nights range (hyphenated buckets exist for FY revenue only), so (b)'s only historical route is a directional "similar to Q3" with Q3 printing 9.0–9.9. Astra's C02 comparison puts 0.09 of its 0.18 on (b) through an explicit-bucket conditional of 0.15; the log carries 0.11 through the same route but says why it is speculative (§4).
4. **R01/R02 now supply the print distribution the audit asked for.** The audit's N(9.5, 1.48) was the best available at audit time; batch A09 (written afterwards) calibrated the print at N(9.67, 1.70) with the Kalshi ladder at 0.1 weight, which is also how A02-05's contrary evidence enters C02. The audit's normal survives as S1d and changes nothing material.
5. **The 3Q22 omission is a weaker precedent than the audit's 0.15 on C03(e) implies.** The sentence that vanished was "we continue to forecast delivering Adjusted EBITDA margin expansion for the full-year 2022 relative to 2021" — qualitative, y/y, and made redundant by the numeric Q4 guide. The 2026 revenue line is the first bullet of the "Full-Year 2026" section in May and August. The log takes (e) to 0.12 and puts the raw case in S5.
6. **The C03 (c) bucket carries the +0.5pp margin analogy.** Astra's finding A02-04 established that both numeric-floor conversions stepped +50bp, then its comparison forecast gave the descriptive branch only 0.10 on (c). Applied to a 15% floor, +0.5pp is "approximately 15.5%", which the conventions resolve (c). This is the named asymmetry behind the seven-point gap on (c) (final table).
7. **Rounding to sum 1.** The C03 blend gives (e) 0.129, rounded down to 0.12 so the vector sums to 1.00 after (a) 0.356 rounds to 0.36; the C02 blend gives (d) 0.320 and (e) 0.030, with 0.01 moved from (d) to (e) by the §6 resolution audit. Neither log hid this, but the audit's summing check would not have caught a vector that summed to 1.01, so it is stated here.

## Reconciliation with Astra's comparison vectors

C02: every option within one point (final 0.18 / 0.17 / 0.30 / 0.31 / 0.04 vs 0.17 / 0.18 / 0.30 / 0.30 / 0.05). The two constructions differ in structure — Astra's is a one-level format split (0.60 / 0.35 / 0.05) with a single explicit-bucket conditional; the log's is branch-conditional on the print — and arrive at the same place because both put the modal economic outcome at "high single digits" and both give a directional "moderate" sentence 0.19–0.21 of the mass. The decision to hold (d) one point ahead of (c) rests on the base rate (item 1 above); the log says the pair should be quoted jointly.

C03: (a) +0.01, (b) −0.03, (c) **+0.07**, (d) −0.02, (e) −0.03. The (c) gap is the margin-step analogy (item 6) plus the base rate's 0.3 weight, which Astra's derivation does not use; the (b) and (e) gaps are Astra's heavier descriptive and omission branches (0.35 / 0.15 vs the log's 0.33 / 0.12), each defended in §4 and §5 of the log. The decision is to hold (0.36, 0.16, 0.28, 0.08, 0.12): under Astra's own conventions the leading option is the same and the (a)-vs-(c) question is a rounding call on a 15.5% line whose centre sits 0.2–0.3pp above it, which the log states plainly.

## Reproduction output

`py -3.13 -B docs/pitch-forecasts/audits/A02-reproduce.py` from the repo root, 2026-09-17, exit 0 (no edits to the script; identical to `A02-reproduce.stdout.txt` saved by the first pass):

```
Original-letter quote checks
20

Corrected descriptor classes
print_quarter  guide_type            direction  printed_growth  class
         2Q22 directional               stable          24.789 stable
         3Q22 directional                below          25.094   down
         4Q22 directional               approx          20.163 stable
         1Q23 directional below_revenue_growth          18.609   down
         2Q23 directional                above          10.993     up
         3Q23 directional                below          13.541   down
         4Q23 directional                below          12.018   down
         1Q24 directional               stable           9.496 stable
         2Q24 directional                below           8.688   down
         3Q24 directional                above           8.481     up
         4Q24 directional               stable          12.348   down
         1Q25 directional                below           7.919   down
         2Q25 directional               stable           7.434 stable
         3Q25      bucket                  NaN           8.795   down
         4Q25      bucket                  NaN           9.820   down
         1Q26 directional                below           9.154   down
         2Q26      bucket                  NaN          10.342     up

all observable guides
{'n': 17, 'down': 10, 'stable': 4, 'up': 3}

resolved target quarters only
{'n': 16, 'down': 10, 'stable': 4, 'up': 2}

W1: print quarter 1Q23+
{'n': 14, 'down': 9, 'up': 3, 'stable': 2}

W2: print quarter 1Q24+
{'n': 10, 'down': 6, 'stable': 2, 'up': 2}

direct-comparison-only sensitivity
{'n': 15, 'down': 8, 'stable': 4, 'up': 3}

Format counts, all 17
{'directional': 14, 'bucket': 3}

Format counts, print before 2025
{'directional': 11}

November nights classes
{'down': 3, 'up': 1}

Reaction-panel direction counts
{-1.0: 8, nan: 6, 0.0: 6, 1.0: 3}

Resolved volume buckets
print_quarter         metric  actual  beat_mid_pp  beat_top_pp
         3Q25    gbv_yoy_pct   15.91         4.91         3.91
         3Q25 nights_yoy_pct    9.82         4.82         3.82
         4Q25    gbv_yoy_pct   19.18         6.18         5.18
         4Q25 nights_yoy_pct    9.15         1.15         0.15
         1Q26    gbv_yoy_pct   15.74         4.74         3.74

Volume sample dependence
{'rows': 5, 'print_events': 3, 'above_top': 5, 'nights_rows': 2}

Revenue beats all
{'n': 19, 'above_mid': 19, 'above_top': 15}

Revenue beats W1 target 1Q23+
{'n': 14, 'above_mid': 14, 'above_top': 11}

Revenue beats W2 target 1Q24+
{'n': 10, 'above_mid': 10, 'above_top': 9}

Trailing-eight cushion mean/median/sample SD
(1.8567430632975808, 1.7904910308494282, 1.0047995786447292)

Q4 cushions
target_period  cushion_pct
         4Q21     6.759582
         4Q22     3.369565
         4Q23     3.162791
         4Q24     2.691511
         4Q25     3.271375

Q4 mean/median/last-three mean
(3.8509649296892823, 3.271375464684012, 3.041892516507335)

FY revenue guide updates
print_quarter target_period  value_mid  change
         4Q25        FY2026       11.0    NaN
         1Q26        FY2026       14.0    3.0
         2Q26        FY2026       15.0    1.0

Revenue raises/updates
(2, 2)

All November margin sentences
print fy_sentence_type  actual_minus_guide_bp  q4_actual_minus_implied_pts
 3Q21             none                    NaN                        12.27
 3Q22             none                    NaN                         4.60
 3Q23       approx_yoy                   77.0                         3.65
 3Q24           approx                   90.0                         4.26
 3Q25           approx                   10.0                         0.69

November point beats: n/mean bp
(3, 59.0)

November letters with an existing same-year FY guide
{'n': 4, 'approx_point': 3, 'omitted': 1}

L0 quarterly kappa: n/mean/sample SD/trailing-eight mean
(12, 0.6039538075130505, 0.30013804644373737, 0.5156727823105556)

Actual consensus provenance
period as_of_row_date revenue_obs_date  revenue_mean  revenue_n  revenue_sd  revenue_high
  3Q26     2026-09-11       2026-09-07    4744.32212       37.0    24.27626        4792.0
  4Q26     2026-09-11       2026-09-07    3161.81627       37.0    48.55902        3223.0
  FY26     2026-09-11       2026-09-07   14189.55705       44.0    59.21929       14296.0

log: deflate entire FY
{'musd': 14104.927485089462, 'growth_pct': 15.226921698304574}

illustrative: deflate only Q4
{'musd': 14170.69929888668, 'growth_pct': 15.764229220543102}

quarter-sum version
{'musd': 14173.280638886681, 'growth_pct': 15.785316876780332}

Bridge range is fixed-GBV conversion extrema
(3156.00796755095, 3201.2165536755674)

Bridge points
quarter  revenue_musd
   3Q26   4804.035503
   4Q26   3178.107848

C02 original decomposition
{'a': 0.2116, 'b': 0.1884, 'c': 0.3964, 'd': 0.1734, 'e': 0.0302}

C02 normal bins 9.5
[0.36774269705599305, 0.2645146058880139, 0.36774269705599305]

C02 repaired-bin tree 9.5
{'a': 0.199291, 'b': 0.168516, 'c': 0.382322, 'd': 0.216194, 'e': 0.033677}

C02 normal bins 9.6
[0.39347616771494187, 0.2639340631210201, 0.34258976916403805]

C02 repaired-bin tree 9.6
{'a': 0.208783, 'b': 0.17102, 'c': 0.379176, 'd': 0.208104, 'e': 0.032917}

Maximum one-point interval mass under SD 1.48
0.2645146058880139

Original P(Q3 >=10 | C02=a)
0.7542533081285443

Reviews error sample: n/RMSE/naive RMSE/mean/sample SD
(10, 1.4801155663934527, 2.1591433023308118, -0.46450310902658065, 1.4813578424258271)

C03 original
{'fy_mean': 14166.0, 'growth_pct': 15.72583939220651, 'sd_pp': 0.7306814729188105, 'p_ge16': 0.35375132635326134, 'vector': {'a': 0.3679, 'b': 0.168284, 'c': 0.273015, 'd': 0.090801, 'e': 0.1}}

C03 Street-centred
{'fy_mean': 14115.0, 'growth_pct': 15.30920676415326, 'sd_pp': 0.6979824969624647, 'p_ge16': 0.16116040200265225, 'vector': {'a': 0.254215, 'b': 0.168284, 'c': 0.320627, 'd': 0.156873, 'e': 0.1}}

C03 B2 guide
{'fy_mean': 14242.0, 'growth_pct': 16.346703700678056, 'sd_pp': 1.0101192378810127, 'p_ge16': 0.634287458118026, 'vector': {'a': 0.491438, 'b': 0.168284, 'c': 0.171579, 'd': 0.068698, 'e': 0.1}}

C03 positive-correlation sensitivity
{'fy_mean': 14166.0, 'growth_pct': 15.72583939220651, 'sd_pp': 0.8645539779640848, 'p_ge16': 0.37557923671557414, 'vector': {'a': 0.368843, 'b': 0.168284, 'c': 0.252735, 'd': 0.110137, 'e': 0.1}}

Kalshi stored fields
{'volume': None, 'volume_fp': '428.14', 'open_interest': None, 'open_interest_fp': '423.14', 'liquidity_dollars': '0.0000', 'yes_bid_dollars': '0.5000', 'yes_ask_dollars': '0.5500'}

Audit C02 unrounded
{'a': 0.171484, 'b': 0.178516, 'c': 0.3, 'd': 0.3, 'e': 0.05}

Audit C03 unrounded
{'mean_musd': 14174.322650860277, 'vector': {'a': 0.346856, 'b': 0.1925, 'c': 0.209775, 'd': 0.100869, 'e': 0.15}}
```

(`np.float64(...)` wrappers stripped for readability; values unchanged.)

Separately replayed in the second pass (not in the audit's script): both `datasets/decomposition_v2.py` scripts under `py -3.13 -B`. C02: base rate (0.126, 0.146, 0.306, 0.393, 0.029); branch masses 0.423 / 0.230 / 0.347; decomposition (0.202, 0.167, 0.289, 0.312, 0.030), Monte-Carlo check (seed 20260917, 10⁵) (0.201, 0.167, 0.289, 0.314, 0.030); anchor (0.192, 0.231, 0.315, 0.232, 0.030); blend (0.177, 0.174, 0.299, 0.320, 0.030); final (0.18, 0.17, 0.30, 0.31, 0.04); P(Q3 ≥ 10 | a) 0.916; S1d audit normal (0.180, 0.171, 0.297, 0.322, 0.030). C03: FY $14,166M, +15.73%, sd 0.86pp (0.73 at ρ 0); P(≥16) 0.376, P(<15) 0.201, P(≥15.5) 0.603, Monte-Carlo 0.375 / 0.201 / 0.602; given-numeric (0.48, 0.02, 0.364, 0.137); decomposition (0.363, 0.159, 0.250, 0.108, 0.120); base rate (0.329, 0.15, 0.329, 0.042, 0.15); anchor $14,173.3M, +15.785%, vector (0.381, 0.159, 0.281, 0.060, 0.120); blend (0.356, 0.156, 0.280, 0.079, 0.129); final (0.36, 0.16, 0.28, 0.08, 0.12). Every figure matches the logs' §5–§7, both regenerated `decomposition_v2_output.csv` files are identical to the committed ones, both JSON vectors equal the §6 tables and sum to 1.00, and the JSON option labels match QUESTIONS.md.

## Final table

| question | revision-1 vector (a–e) | Astra's vector | revision-2 vector | anchor | \|final − anchor\| on the leading option |
|---|---|---|---|---|---|
| C02 4Q26 nights bucket language, 5 Nov | 0.21 / 0.19 / 0.39 / 0.17 / 0.04 (leader (c)) | 0.17 / 0.18 / 0.30 / 0.30 / 0.05 | **0.18 / 0.17 / 0.30 / 0.31 / 0.04** (leader (d) by one point; quote (c)+(d) = 0.61) | (c) 0.32 — Bloomberg MODL 4Q26 nights 134.0m (+9.9%, n 28, 12 Sep) mapped to language through a stated bucket/directional split; anchor vector 0.19 / 0.23 / 0.32 / 0.23 / 0.03; dependent construction, no tradable market on the descriptor | 0.08 on (d) (final 0.31 vs anchor 0.23); −0.02 on (c). Sensitivity range (d) 0.23–0.36, (c) 0.25–0.33 |
| C03 FY26 revenue guide language, 5 Nov | 0.37 / 0.18 / 0.28 / 0.08 / 0.09 | 0.35 / 0.19 / 0.21 / 0.10 / 0.15 | **0.36 / 0.16 / 0.28 / 0.08 / 0.12** (leader (a)) | (a) 0.38 — Street-implied FY26 guide $14,173.3M (+15.79%): 1H26 actual + LSEG 3Q26 + LSEG 4Q26 / (1 + κ 0.6%), obs 7 Sep / row 11 Sep, passed through the log's format and rounding mapping; anchor vector 0.38 / 0.16 / 0.28 / 0.06 / 0.12; dependent construction, no market | 0.02 on (a) (final 0.36 vs anchor 0.38). Sensitivity range (a) 0.26–0.47 |

Notes on the gaps to Astra. No option differs from Astra's vector by more than 10 points on either question. C02 is within one point everywhere. C03 (c) is +0.07 (0.28 vs 0.21): the named asymmetry is the November margin precedent — both numeric-floor conversions stepped +0.5pp, which on a 15% floor is "approximately 15.5%" and resolves (c) under the conventions; the log's base rate carries that at 0.33 with weight 0.3, and its descriptive branch gives (c) 0.15 against Astra's 0.10. C03 (b) −0.03 and (e) −0.03 are Astra's heavier descriptive (0.35) and omission (0.15) branches against 0 of 4 November reiterations and the redundant-qualitative-sentence reading of 3Q22. The C02 +0.08 on (d) versus the anchor is the base rate: the Street's level says "high single digits", but management has expressed that view as a no-bucket "moderate" in 8 of 17 letters and 3 of 4 Novembers, and the question resolves that sentence as (d).
