# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable; batch A19, question X01, the synthesis question that reads every other forecast). Reproduction script: [datasets/x01_joint.py](datasets/x01_joint.py) (numpy + standard library, seed 20260917, n 1,000,000; reads every input from disk by path; writes `x01_joint_summary.json`, `x01_joint_table.csv`, `x01_scenario_table.csv`, `x01_sensitivity.csv`, `x01_base_rate_panel.csv`). Run from the repo root: `py -3.13 docs/pitch-forecasts/questions/scenario-probabilities/datasets/x01_joint.py` (about 4 minutes; 28 sensitivity re-runs of the full joint).

## 0. Metadata
- question_name: scenario-probabilities
- question_url: n/a (docs/pitch-forecasts/QUESTIONS.md § X01)
- type: multiple_choice
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-16
- close_date: 2026-11-05
- resolution_date: 2026-11-05
- scoring: unknown
- cp_visible: no
- cp_value: n/a

## 0b. Question (verbatim)
### Title
What are the probabilities of the memo's three scenarios for the 5 Nov print: thesis breaker (accelerating print ≥10.6% nights with the 4Q26 bucket at "low double digits" or better), base (decelerating print with the 4Q26 nights bucket at "high single digits"/"around 10" and/or the revenue guide midpoint below Street), short case (nights ≤8.5% or 4Q26 bucket "mid single digits" or lower, or FY26 margin floor weakened)?
### Resolution Criteria
**Type.** Multiple choice over {thesis breaker, base, short case, none of the above (e.g., in-line print with in-line guide)}.
### Fine Print
Must be coherent with C01, C02, C04, R01, R02 and S01 (state the joint structure and the correlations assumed). Runs last; reads every `forecasts/*.json`. Resolution 5 Nov 2026.

### Conventions adopted (the question's gates are unions and intersections of other questions' resolutions; each is fixed here so 5 Nov resolves mechanically)
1. **Print gates** are on the letter's printed 3Q26 Nights and Seats Booked y/y rate to one decimal on the 133.6m base: "≥10.6%" = latent ≥ 10.5913 (R02's 147.75m threshold); "≤8.5%" = latent < 8.55 (prints 145.0m or less, rate rounds to 8.5% or lower). S01's dead band (decelerating < 10.09, flat 10.09–10.59, accelerating ≥ 10.59) is used for the return cells; the 0.0013-point gap between 10.59 and 10.5913 is empty in practice (mass < 0.0003).
2. **Thesis breaker** = printed nights ≥ 10.6% AND C02 resolves (a) ("low double digits" or language implying ≥10%). Both conditions required; "or better" is inside C02 (a).
3. **Short case** = printed nights ≤ 8.5% OR C02 resolves (d) OR C04 resolves (d). The A19 brief operationalises the three legs at the option level of C02 and C04; I follow it as the headline ("literal" reading). C02 (d) therefore includes the directional "moderate / decelerate" sentence without a bucket (0.19 of C02's 0.31), and C04 (d) includes "approximately 35.5%" (a point at the floor, no +50bp). Because the question text says *bucket* "mid single digits" or lower, a second, "material" reading (C02 leg = an explicit mid-single-or-lower bucket only, i.e. the 0.12 explicit sub-split of C02's (d)) is computed and published in §6–7 as the alternative vector; the memo must say which it quotes.
4. **Base** = printed nights < 10.6% AND (C02 ∈ {(b), (c)} OR C01 = Yes, guide midpoint below the LSEG-family Street mean) AND not short case.
5. **None of the above** = every other joint outcome. It contains (i) an accelerating print (≥10.6%) whose descriptor is not (a) and which trips no short gate (e.g., 10.8% printed with "high single digits" for Q4 and the floor held) and (ii) a flat/decelerating print with C02 (a) or (e) and the guide at/above Street.
6. **Precedence** where two options' conditions both hold: thesis breaker > short case > base > none. Short beats base by construction (base excludes short). Breaker vs short can overlap only through C04 (d) on an accelerating "low double digits" print (mass 0.033); the breaker wins because the memo's breaker is the growth outcome and the S01 cell for that print is positive; the reverse precedence is a published sensitivity (breaker 0.14 → 0.11).
7. If the letter gives no 4Q26 nights descriptor (C02 (e), 0.04) the breaker cannot resolve; the draw falls to base (if C01 Yes) or none. If no FY26 margin sentence (C04 (e)) the C04 leg is simply not tripped.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Adopted 3Q26 print distribution (R01/R02 revision 2): latent nights y/y ~ N(9.5, 1.70) on 133.6m; P(printed ≥147.0m, ≥10.0%) 0.386; P(≥147.8m, ≥10.6%) 0.260; print states P(<10.0) 0.614 / P(10.0–10.6) 0.126 / P(≥10.6) 0.260; S01 states decel 0.636 / flat 0.104 / accel 0.261; rev-1 N(9.67, 1.70) and 0.42/0.32 withdrawn; the file names X01 as a reader | docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json (revision 2); forecasts/2026-09-17-forecast.json R01 rev 2 (0.39, CI 0.30–0.47); questions/risk-q3-nights-accelerates/forecasts/2026-09-17-forecast.json R02 rev 2 (0.26, CI 0.18–0.34) | 2026-09-17 | 2026-09-17 | yes |
| 2 | C01 revision 2: P(4Q26 revenue guide midpoint < LSEG-family Street mean on 4 Nov) = 0.72 (CI 0.60–0.82); model structure guide = 12.03% × (1+eps−leak) × [⅔ GBV_3Q26 + ⅓ × 27,200] × (1+fee)/(1+cushion), so d(guide)/d(GBV_3Q26) = ⅔ × 17.27/(17.27+9.07) ≈ 0.66% of guide per 1% of 3Q26 GBV, i.e. 0.66% of the guide-vs-Street gap per point of 3Q26 nights at fixed ADR; guide midpoint sd $97M (3.1%); published conditional read: pre-print mixture 0.78 / 0.69 / 0.55 at printed GBV $25.9bn / $26.2bn / $26.6bn (GBV held at the printed value) | docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/forecasts/2026-09-17-forecast.json (revision 2, `model.structure`, `monitoring[6]`); research-log.md §6 and §8 | 2026-09-17 | 2026-09-17 | yes |
| 3 | C02 revision 2 final vector (a) 0.18 / (b) 0.17 / (c) 0.30 / (d) 0.31 / (e) 0.04; unions (a∨b) 0.35, (c∨d) 0.61; sub-splits (d) = directional-moderate 0.19 + explicit mid-single 0.12, (b) = directional-similar 0.06 + around-10/hyphenated 0.11; branch × option joint under N(9.67, 1.70): ≥10.0 (mass 0.423): 0.184/0.061/0.091/0.074/0.013; 9.0–9.99 (0.230): 0.013/0.061/0.090/0.059/0.007; <9.0 (0.347): 0.004/0.045/0.108/0.179/0.010; P(Q3 ≥10 \| a) 0.92, P(Q3 <9 \| d) 0.57; "X01 should use this joint structure with the final marginals (A02-16)"; the adopted-object file says the v2 print distribution moves (a) by −0.01 and (d) by +0.01, below C02's noise floor | docs/pitch-forecasts/questions/q4-nights-bucket/forecasts/2026-09-17-forecast.json (revision 2); datasets/decomposition_v2_output.csv; research-log.md §6 | 2026-09-17 | 2026-09-17 | yes |
| 4 | C04 revision 2 vector (a) 0.33 / (b) 0.30 / (c) 0.05 / (d) 0.27 / (e) 0.05 (model 0.3366/0.2953/0.0458/0.2727/0.0496); conditionals on C01: C04 \| guide below = a 0.3937, b 0.2245, c 0.0149, d 0.3171, e 0.0498; C04 \| not below = 0.1818 / 0.4874 / 0.1294 / 0.1524 / 0.049; the model's own P(guide below) 0.7306; C04 × C09 joint published; C04's log treats R01 as immaterial to its draw (C04 ⟂ print \| C01) | docs/pitch-forecasts/questions/fy26-margin-sentence/forecasts/2026-09-17-forecast.json (revision 2); datasets/mc_joint_and_conditionals_v2.json | 2026-09-17 | 2026-09-17 | yes |
| 5 | S01 revision 2 joint (print state × C01 × C02 c/d × latent signal × return): twelve cells with percentiles p5–p95, P(≤−8), P(≤−5), P(<0), P(≥5), P(≥10), P(≥17), P(<−15), P(<−25) and bound mass; within-state C01–C02 odds ratio 2; P(below \| state) 0.761 / 0.704 / 0.651 (decel/flat/accel) at gap tilt 0.32%/pt; base-case cell (decel & below & c/d) p 0.358, median −5.08, P(≤−8) 0.374, P(≥5) 0.144; breaker cell (accel & at/above) p 0.112, median +2.9, P(≥5) 0.404; the cell-conditional tables barely move when the print states are re-weighted (sensitivity row "R01 normal untouched": base-case p50 −5.07, breaker p50 2.90); C02 carries no day-1 coefficient; unconditional median −2.1, P(≤−8) 0.27, P(≥5) 0.22; S01 was built on the rev-1 states (0.595/0.085/0.32, N(9.67,1.70)) and the adopted file says S01 rebases to 0.636/0.104/0.261 (median about −0.3) | docs/pitch-forecasts/questions/day1-move-5nov/forecasts/2026-09-17-forecast.json (revision 2); datasets/s01_v2_cells.csv, s01_v2_conditionals.csv, s01_v2_sensitivity.csv, s01_v2_components.json, s01_joint_v2.py | 2026-09-17 | 2026-09-17 | yes |
| 6 | S02 revision 2: 15 Dec close p5–p95 121/129/146/166/186/207/221, P(≤150) 0.30, P(≤143) 0.22, P(≥180) 0.32; decomposition = four-branch path mixture (accel ≥10.6 p 0.32 median 172.3; flat 0.10, 165.5; decel & guide ok 0.13, 163.0; decel & guide below 0.45, 156.1) with decomposition median 163.07 blended 0.65/0.35 with the options RND (final median 165.6); within-branch day-1 sd 8.45%, 26 post sessions at 30% vol; the adopted file says S02 rebasing to the v2 states moves the median about −$0.7 | docs/pitch-forecasts/questions/close-15dec-2026/forecasts/2026-09-17-forecast.json (revision 2); datasets/mixture_base_run_v2.json, final_blend_v2.json, abnb_path_mixture_v2.py | 2026-09-17 | 2026-09-17 | yes |
| 7 | Memo scenario table (the anchor): thesis breaker 25% ($180–190; ≥10.6%, "low double digits" reiterated, bundle ≥2.5pt, FY sentence ≈36%), base 45% ($138–148; 9.5–10.0%, "high single digit", guide $3.05–3.10bn vs Street $3.16bn), short case 30% ($115–130; ≤8.5%, guide implies ≤7.5%, no bundle figure, floor at risk); probability-weighted $146; "at 60/25/15 on the deceleration cases, $138"; no "none" option | deck/drafts/memo_v2_short_2026-09-16.md § Scenarios (read-only) | 2026-09-16 | 2026-09-17 | yes |
| 8 | Reaction panel, 16 ex-reopening prints 3Q22–2Q26: nights y/y, sequential change (pts), guide vs Street, day-1 raw and excess return; joined to C02's descriptor dataset (question option a/b/c/d per print, bucket vs directional) and the FY-margin action (never "lowered/softened" in the record); classified into the four X01 cells under both readings (extract: datasets/x01_base_rate_panel.csv) | data/processed/reverse_dcf/C/C_print_panel.csv; docs/pitch-forecasts/questions/q4-nights-bucket/datasets/nights_descriptor_vs_printed_and_comp_v2.csv; data/processed/abnb_guidance_reaction_panel.csv; docs/pitch-forecasts/questions/fy26-margin-sentence/datasets/fy_margin_guide_ledger_v2.csv | 2026-09-13 to 2026-09-17 | 2026-09-17 | yes |
| 9 | Adopted 4Q26 print object (R16 revision 2): three-component mixture, mean 8.61, sd 2.28, P(≥134.0m) 0.307, P(≤131.0m) 0.309, corr(Q3, Q4) 0.19; names X01 as a reader. Not a gate of any X01 option (all X01 gates are 5 Nov disclosures); read for coherence: E[Q4 \| Q3 ≤ 8.5] sits at the mid-single bucket, consistent with C02 (d) concentrating in the <9 branch | docs/pitch-forecasts/questions/risk-q4-nights-print-meets-street/datasets/adopted_q4_states_v2.json; forecasts/2026-09-17-forecast.json R16 rev 2 (0.31) | 2026-09-17 | 2026-09-17 | no |
| 10 | Every other revision-2 forecast, read for coherence and not used as a gate (question id, final): C03 fy26-revenue-guide-language (a .36/b .16/c .28/d .08/e .12); C05 bundle-attribution-quantified (a .07/b .11/c .10/d .72); C06 rnpl-gbv-share-disclosed (.25/.20/.26/.29); C07 rnpl-negative-effect-acknowledged 0.27; C08 q3-revenue-fx-integer (.49/.28/.21/.02); C09 q4-margin-direction-sentence (.22/.26/.47/.05); C11 q3-take-rate-above-1810 0.76; C12 q3-unearned-fees-yoy 0.43; S03 close-12feb-2027 p50 166; S04 sellside-mean-target-cut-by-15dec 0.30; F01 q1-27-nights-guide-above-82 0.28; F02 q1-27-revenue-guide-growth p50 10.5; F03 fy27-margin-guide (.02/.04/.10/.36/.48); F04 fy27-sm-share-above-219 0.55; R03 0.11; R04 0.52; R05 0.22; R06 0.46; R07 0.17; R08 0.13; R09 0.25; R10 0.10; R11 0.26; R12 0.47; R13 0.02; R14 0.26; R15 0.18; B02 0.12; B04 0.21; B05 0.62; B06 0.32; B07 0.63; B08 0.44; B09 0.08; B10 0.04; B17 0.41; B01 0.33 (rev 2) | docs/pitch-forecasts/questions/<slug>/forecasts/2026-09-17-forecast.json for each slug listed in docs/pitch-forecasts/QUESTIONS.md (all `"revision": 2`) | 2026-09-17 | 2026-09-17 | no |
| 11 | Revision-1 forecasts with the auditor's number used in their place where a number is needed (none is an X01 gate): B03 marketing-cut 0.18 rev 1 → A14 auditor 0.20–0.21; B11 sellside-downgrades 0.14 rev 1 → A17 auditor 0.13; B12 fy27-investment-year 0.50 rev 1 → A17 0.47 literal / 0.36 material; B13 q4-nights-print-weak 0.26 rev 1 → A17 0.31 (must adopt, per the adopted 4Q26 object); B14 weather 0.08, B15 q4-us-revpar-soft 0.10 (RUN_STATE says re-base to 0.23), B16 insider-selling 0.87: revision 1, A18 audit not on disk at run time (12:12) | docs/pitch-forecasts/audits/A14-research-audit.md; audits/A17-research-audit.md; docs/pitch-forecasts/RUN_STATE.md lines 86–89; the six forecast JSONs (`"revision": 1`) | 2026-09-17 | 2026-09-17 | no |
| 12 | Structural sensitivities for the impact/price rows (not used to move the vector): decelerating prints post-2022 −5.6% day-1 excess (0 of 8 positive), accelerating +6.0%; Q4-guide-below-Street AND nights guided lower −8.0% mean / −10.9% median (n 5); options-implied event sd 9.5% | docs/pitch-forecasts/00_BRIEF.md § Sensitivities; data/processed/overnight/05_reaction_by_accel.csv | 2026-09-16 | 2026-09-17 | no |

Newest load-bearing source: every input is dated 2026-09-17 (today), 49 days before resolution.

## 2. Query Log
1. [repo] docs/pitch-forecasts/00_BRIEF.md; QUESTIONS.md § X01, C01, C02, C04, C09, R01, R02, S01, S02
2. [repo] C:/Users/krish/.claude/skills/forecast/SKILL.md; references/research-log-format.md
3. [repo] deck/drafts/memo_v2_short_2026-09-16.md § Scenarios (lines 58–72), read-only
4. [repo] questions/risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json; questions/risk-q4-nights-print-meets-street/datasets/adopted_q4_states_v2.json
5. [repo] questions/day1-move-5nov/datasets/s01_joint_v2.py, s01_v2_cells.csv, s01_v2_conditionals.csv, s01_v2_sensitivity.csv, s01_v2_components.json; forecasts/2026-09-17-forecast.json; README.md
6. [repo] questions/fy26-margin-sentence/datasets/mc_joint_and_conditionals_v2.json, fy_margin_guide_ledger_v2.csv
7. [repo] questions/q4-nights-bucket/research-log.md (§5–§7, the joint branch table), datasets/decomposition_v2_output.csv, decomposition_v2.py, nights_descriptor_vs_printed_and_comp_v2.csv
8. [repo] questions/q4-revenue-guide-vs-street/forecasts/2026-09-17-forecast.json, datasets/c01_v2_sensitivity.csv, c01_v2_bridge.csv, research-log.md (grep "conditional")
9. [repo] questions/close-15dec-2026/forecasts/2026-09-17-forecast.json, datasets/final_blend_v2.json, mixture_base_run_v2.json, abnb_path_mixture_v2.py (docstring and run())
10. [repo] all 53 questions/*/forecasts/2026-09-17-forecast.json (compact dump of id, slug, revision, final)
11. [repo] audits/A14-research-audit.md, A17-research-audit.md (independent numbers); `ls audits/` for A18 (absent); RUN_STATE.md (A18/A19 lines)
12. [repo] data/processed/abnb_guidance_reaction_panel.csv; data/processed/overnight/05_reaction_by_accel.csv; data/processed/reverse_dcf/C/C_print_panel.csv
13. [repo] docs/pitch-forecasts/batches.json
14. No WebSearch, WebFetch, Polymarket or Kalshi call was made for this question (the question is a function of repo objects; C01/C02/C04/S01/S02 carry the market scans dated 2026-09-17T02:50–03:13Z and 07:57Z). Final 72-hour recency check: not applicable to a synthesis object; the newest input is dated today.

## 3. Leading Hypothesis Entities
Airbnb, ABNB, 5 November 2026 print, 3Q26 Nights and Seats Booked, 4Q26 nights bucket, FY26 adjusted EBITDA margin floor, LSEG 4Q26 revenue consensus, short case, thesis breaker

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Product of marginals (P(breaker) = P(≥10.6) × P(C02 a); short = 1 − (1−P(≤8.5))(1−P(d))(1−P(C04 d))) | discarded | The gates are strongly dependent: (a) sits 0.89 in the ≥10.0 branch, (d) 0.61 in the <9 branch, C04 (d) is 0.317 given guide-below vs 0.152 not; independence gives breaker 0.047 and short 0.63 — wrong in both directions. The joint is the object (claims 1–5) |
| Rebuild the C02 tree or the S01 reaction model inside X01 | discarded | X01 must be coherent with the audited marginals; the joint reproduces them (§6 checks) and only adds the within-branch allocation of C02 in nights (piecewise log-odds through C02's own three anchors) and the C01 slope from C01's own structure (claim 2). Nothing upstream is re-forecast |
| Use S01's C01 tilt (0.32%/pt) as the primary | kept as sensitivity | C01's own model gives 0.66%/pt (claim 2). The choice moves no option by more than 0.001 because C01 enters X01 only through base-vs-none and the C04 conditional; both rows are in §7 |
| Make C04 (d) more likely on a weak print beyond its C01 link | tested, discarded | C04's log conditions on C01 only; an odds ×2 on (d) when the print is ≤8.5 changes nothing (those draws are already short via the nights gate). Row in §7 |
| Treat the memo's conjunctive short case (≤8.5% AND guide ≤7.5% AND floor at risk) as the question | discarded | The registered question is a disjunction; the brief operationalises it. The conjunction is a different, much smaller object (≈0.06–0.08 in this joint: nights ≤8.5 & C02 d & C04 d has mass 0.05, plus adjacent cells) and is reported in §6 for the memo, not forecast as X01 |
| "None of the above" ≈ 0 (the memo's table) | discarded | Accelerating prints with a non-(a) descriptor and no short gate are 0.065 in the joint and 2 of the last 10 prints (4Q24, 4Q25 — both +14.4% and +4.6% days); log-score discipline forbids a zero |
| Shrink the vector toward the memo's 25/45/30 | discarded | The disagreement is definitional (the memo's short case is a fundamental scenario, the question's is a language union) and the memo's breaker 0.25 exceeds P(≥10.6) × P(a \| ≥10.6) under any published input; anchoring to it would break coherence with C02/R02 |

## 5. Independent Estimates
- base_rate_estimate: breaker 0.10 / base 0.20 / short 0.50 / none 0.20 — the 16 ex-reopening prints (3Q22–2Q26) classified into the four cells under the literal reading (claim 8; datasets/x01_base_rate_panel.csv): all 16 = 0.06/0.13/0.69/0.13; W1 (1Q23+, n 14) = 0.07/0.14/0.64/0.14; W2 (1Q24+, n 10) = 0.10/0.20/0.50/0.20; bucket era (n 4) = 0.25/0/0.50/0.25; November prints (n 4) = 0/0.25/0.75/0. Regime-conditioned on W2 (the two-window rule; the 2022–23 rows are reopening-normalisation decelerations of 1.5–7.6pt that the 1.70-sd print distribution does not admit). Under the material reading the same rows give W1 0.07/0.29/0.29/0.36 and W2 0.10/0.30/0.30/0.30. The historical "short case" (literal) is the modal cell because the directional "moderate" sentence was management's default next-quarter language (8 of 17 descriptors) and the margin floor has never been softened (0 of 16), so the historical C04 leg is empty and the joint's 0.27 on it is forward-looking.
- decomposition_estimate: breaker 0.139 / base 0.223 / short 0.555 / none 0.083 — the joint simulation (datasets/x01_joint.py; §6 for the structure and the marginal checks).
- anchor_estimate: breaker 0.25 / base 0.45 / short 0.30 / none 0.00 — the memo's own scenario table (claim 7, 2026-09-16), the only prior anyone holds on this object; no market prices it.
- anchor_value: 0.25 / 0.45 / 0.30 / 0.00
- final_estimate: thesis breaker 0.14 / base 0.22 / short case 0.55 / none of the above 0.09
- final_minus_anchor: −0.11 / −0.23 / +0.25 / +0.09 — independent by construction: the final is the joint of six audited marginals plus the reaction panel's cell frequencies, and the anchor is the un-audited table those numbers were commissioned to replace. Reconciliation of the three: (i) breaker — the memo's 0.25 needs P(≥10.6) × P(a \| ≥10.6) ≈ 0.26 × 0.96, i.e. "low double digits" reiterated on nearly every accelerating print, against C02's tree (0.44 in the ≥10 branch) and a 1-of-6 historical rate on accelerating prints; the joint's 0.14 and the W2 base rate's 0.10 agree; (ii) short — the joint (0.55) and the W2 base rate (0.50) agree under the literal reading and the memo's 0.30 is a different object (its conjunctive scenario, ≈0.06–0.08 here; its "deceleration cases" 60/25/15 split is closer to the joint's base+short 0.78); (iii) none — the joint 0.08 vs W2 0.20 (n 2 of 10): the two historical cases were accelerating prints with a high-single descriptor; the joint carries that cell at 0.065 because P(accel) is 0.26 and C02 (a \| accel) is 0.535; I round "none" up to 0.09 (0.7 points, inside Monte Carlo noise) rather than blend, so the vector stays the coherent joint. Final = the joint, rounded.

## 6. Final Numbers

**Vector (multiple choice, sums to 1.00):**

| Option | P | 80% span over §7 rows |
|---|---:|---|
| thesis breaker (printed ≥10.6% AND C02 (a)) | **0.14** | 0.11–0.17 |
| base (print <10.6% AND (C02 b/c OR C01 below) AND not short) | **0.22** | 0.16–0.29 |
| short case (printed ≤8.5% OR C02 (d) OR C04 (d)) | **0.55** | 0.45–0.61 |
| none of the above | **0.09** | 0.06–0.13 |

Alternative ("material") reading of the short case — explicit mid-single-or-lower bucket only (0.39 of C02's (d)) OR ≤8.5% OR C04 (d): **0.14 / 0.26 / 0.49 / 0.11**; with C04 (d) at 0.20 as well: 0.14 / 0.29 / 0.45 / 0.12. The memo's conjunctive short case (≤8.5% AND C02 (d) AND C04 (d)) has mass 0.050 in the joint; ≤8.5% AND (C02 (d) OR C04 (d)) has 0.194.

**Joint structure (all in `datasets/x01_joint.py`; one draw per row, n 1,000,000, seed 20260917):**
1. 3Q26 latent nights y/y x ~ N(9.5, 1.70) (claim 1). Printed-rate gates at 8.55 and 10.5913; S01 states at 10.09 / 10.59.
2. C01: guide-vs-Street gap ~ N(g0 + 0.66·(x − 9.5), 3.1) with g0 = −1.923 solved so that P(gap < 0) = 0.72 (claims 2, 5). Implied P(below \| x ≤ 8.5) 0.849, \| <10.0 0.795, \| S01 decel 0.792, \| flat 0.673, \| ≥10.6 0.567 (S01's own 0.761 / 0.704 / 0.651 at tilt 0.32 is the §7 sensitivity; no option moves).
3. C02 \| x, C01: log-odds of each option piecewise-linear in x through C02's three branch conditionals anchored at the branch means of N(9.67, 1.70) (7.86 / 9.52 / 11.24; claim 3), linear extrapolation clamped to [6, 14]; per-option factors fitted (IPF, 200 iterations) so the marginal under N(9.5, 1.70) equals C02's final vector exactly (factors 0.001 / 0.009 / 0.023 / −0.062 / 0.325 — the (e) factor is large only because (e) was 0.03 in the tree and 0.04 in the final). Within each x, the (c∨d) block is split by C01 at odds ratio 2 (S01's OR_C02); the a/b/e and c/d sub-splits are independent of C01. Resulting C02 \| S01 state: decel a .036 / b .182 / c .344 / d .397 / e .042; flat .169 / .222 / .338 / .225 / .046; accel .535 / .118 / .181 / .132 / .034. P(x ≥ 10.0 \| a) 0.887 (C02: 0.92); P(x < 9 \| d) 0.607 (C02: 0.57); P(c∨d \| below) 0.682 vs \| not below 0.427.
4. C04 \| C01: the published conditionals (claim 4); C04 ⟂ x given C01.
5. Day-1 return: drawn from the S01 revision-2 cell (state × C01 × c∨d) by inverse-CDF interpolation of each cell's published percentile and threshold table (claim 5). 15 Dec close: lognormal around the S02 revision-2 branch median (accel / flat / decel-ok / decel-below) × 1.0156 (so the four-branch mixture reproduces S02's final median 165.6 at S02's weights) with within-branch log-sd 0.172 (26 sessions at 30% plus the 8.45% event sd; claim 6).

**Marginal checks (joint vs the published inputs; all within Monte Carlo error ±0.001):** print P(<10.0) 0.6146 (0.614), P(10.0–10.6) 0.1248 (0.126), P(≥10.6) 0.2606 (0.260), P(≤8.5) 0.2886; S01 states 0.636 / 0.103 / 0.261 (0.636 / 0.104 / 0.261); C01 0.7208 (0.72); C02 0.1795 / 0.1695 / 0.3004 / 0.3104 / 0.0401 (0.18 / 0.17 / 0.30 / 0.31 / 0.04); C04 0.3347 / 0.2972 / 0.0473 / 0.2713 / 0.0496 (0.3366 / 0.2953 / 0.0458 / 0.2727 / 0.0496); C04 (d) \| below 0.317, \| not below 0.152 (0.3171 / 0.1524); S01 base-case cell (decel & below & c∨d) 0.392 (S01 published 0.358 on the rev-1 states; the adopted file's rebasing note says +0.02 to +0.03); S01 breaker cell (accel & at/above) 0.113 (0.112); unconditional day-1 median −2.4, P(≤−8) 0.28, P(≥5) 0.21 (S01: −2.1 / 0.27 / 0.22; the −0.3 is the rebasing the adopted file predicted); unconditional 15 Dec median 164.7 (S02 165.6 less the predicted −0.7). The 0.011 gap between the historical-count "none" cell and the joint is the only place the joint does not sit on an input, and it is not an input.

**Joint table, option × print state (rows sum to the print masses):**

| 3Q26 printed nights | mass | thesis breaker | base | short case | none |
|---|---:|---:|---:|---:|---:|
| ≤8.5% | 0.289 | 0 | 0 | 0.289 | 0 |
| 8.5–10.0% | 0.326 | 0 | 0.161 | 0.156 | 0.009 |
| 10.0–10.6% | 0.125 | 0 | 0.062 | 0.054 | 0.009 |
| ≥10.6% | 0.261 | 0.139 | 0 | 0.057 | 0.065 |

Option × C01: below (0.721) → 0.070 / 0.160 / 0.455 / 0.037; not below (0.279) → 0.070 / 0.064 / 0.100 / 0.046. Option × C02: (a) 0.180 → 0.139 / 0.016 / 0.013 / 0.012; (b) 0.170 → 0 / 0.078 / 0.069 / 0.023; (c) 0.300 → 0 / 0.121 / 0.145 / 0.034; (d) 0.310 → all short; (e) 0.040 → 0 / 0.009 / 0.019 / 0.013. Option × C04: (d) 0.271 → 0.033 breaker (the precedence overlap) / 0.239 short. Full table: `datasets/x01_joint_table.csv`.

**Composition of the short case (0.555):** one gate only — nights ≤8.5 alone 0.095, C02 (d) alone 0.112, C04 (d) alone 0.111; two or more gates 0.237; the directional "moderate" sentence (not an explicit bucket) is 0.34 of all short-case draws; 0.110 of the short case has a print ≥10.0% (a good print with a "moderate" sentence or a softened floor). **Composition of "none" (0.083):** accelerating print with a non-(a) descriptor and no short gate 0.065; flat/decelerating print with C02 (a) and the guide at/above 0.012; with C02 (e) and the guide at/above 0.006.

**Scenario table for the memo (conditional on each option; day-1 from the S01 rev-2 cells, 15 Dec from the S02 rev-2 branches):**

| Option | P | day-1 median | day-1 mean | P(≤ −8%) | P(≥ +5%) | P(<0) | 15 Dec median | 15 Dec p25–p75 | P(≤$150) | P(≥$180) | E[nights] | P(C01 below) |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|
| thesis breaker | 0.14 | +2.2% | +2.5% | 0.12 | 0.37 | 0.40 | $175 | 156–197 | 0.18 | 0.44 | 12.0 | 0.50 |
| base | 0.22 | −3.8% | −3.4% | 0.32 | 0.17 | 0.66 | $162 | 144–182 | 0.33 | 0.28 | 9.6 | 0.72 |
| short case | 0.55 | −3.8% | −3.4% | 0.33 | 0.18 | 0.66 | $162 | 144–182 | 0.33 | 0.27 | 8.6 | 0.82 |
| none of the above | 0.09 | +1.2% | +1.5% | 0.15 | 0.33 | 0.45 | $173 | 154–195 | 0.20 | 0.41 | 10.9 | 0.45 |

Probability-weighted 15 Dec close (Σ P × conditional median) **$164.8**; the joint's unconditional 15 Dec median 164.7, mean 167.3 (S02 final: median 166, mean 167). Read: base and short case have the *same* day-1 and 15 Dec distributions because the repo's reaction function (S01) prices the print state and the guide-vs-Street sign, not the descriptor wording or the margin sentence, and the reaction panel gives no evidence that deeper decelerations sold harder on the day (the four ≥1.8-pt decelerations since 3Q22 averaged +1.8% raw). The memo's $115–130 short-case price is a 12-month fundamental target (FY27 31.9% margin, +4.5% growth), not a reaction-function output; the 15 Dec conditional for the short case is $162 (p25 $144). The memo should not put a lower 5 Nov / 15 Dec price on the short case than on the base case unless it sources a coefficient the run does not have.

**Extreme-probability gate:** not triggered (smallest option 0.09). Resolution-criteria audit anyway for "none" (the option closest to the memo's zero): edge cases that resolve it — (i) an accelerating print with "high single digits" for Q4 (the 4Q24 and 4Q25 pattern), 0.065; (ii) C02 (e) with the guide at/above Street, 0.006; (iii) a flat/decelerating print whose letter still says "low double digits" with the guide at/above, 0.012. Residual for a resolver reading "in-line print with in-line guide" more broadly (e.g., 10.0–10.6% printed, C02 (b), C01 No — which this log classifies as base): 0.02–0.03 would move from base to none; the 0.09 stands.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Print centre 9.5 (sd 1.70) — 9.0 / 9.2 / 9.9 / 10.0 | breaker 0.11 / 0.12 / 0.16 / 0.16; short 0.61 / 0.58 / 0.52 / 0.52; base 0.22 / 0.22 / 0.21 / 0.21; none 0.06 / 0.07 / 0.11 / 0.11 |
| Print sd 1.70 — 1.475 (published RMSE) / 2.159 (naive) | breaker 0.12 / 0.16; base 0.25 / 0.19; short 0.55 / 0.56; none 0.08 / 0.09 |
| C01 slope 0.66%/pt of nights — 0.32 (S01) / 1.0 | no option moves by more than 0.001 |
| C01 P(below) 0.72 — 0.62 (Astra) / 0.82 | short 0.55 / 0.56; none 0.09 / 0.07; base 0.22 / 0.22 |
| C02–C01 odds ratio 2 — 1 / 4 | base 0.23 / 0.22; none 0.08 / 0.09 |
| C02 (d) 0.31 — 0.23 / 0.36 (C02's own range, mass traded with (c)) | short 0.52 / 0.58; base 0.25 / 0.21 |
| C02 (a) 0.18 — 0.13 (base-rate (a)) / 0.24 | breaker 0.11 / 0.17; short 0.56 / 0.54 |
| C04 (d) 0.27 — 0.20 / 0.35 | short 0.53 / 0.59; base 0.25 / 0.20 |
| C04 (d) odds ×2 when the print is ≤8.5 | unchanged (those draws are already short) |
| Precedence: short case beats thesis breaker | breaker 0.11; short 0.59 |
| Short-case C02 leg = explicit mid-single bucket only ("material" reading) | 0.14 / 0.26 / 0.49 / 0.11; with C04 (d) 0.20 as well 0.14 / 0.29 / 0.45 / 0.12 |
| Short nights gate 8.5% — 8.0% / 9.0% | short 0.52 / 0.61; base 0.26 / 0.17 |
| Breaker print gate 10.6% — 10.0% (R01's line) | breaker 0.16; base 0.16; none 0.13 |
| Monte Carlo (seed 20260918) | 0.140 / 0.224 / 0.554 / 0.082 (±0.001) |

The two load-bearing assumptions: (1) the literal disjunctive short case, in particular counting C02's directional "moderate" sentence and C04's "approximately 35.5%" as short-case gates (0.55 → 0.45–0.49 under the material reading); (2) the alt-data print distribution N(9.5, 1.70) (short 0.52–0.61 and breaker 0.11–0.16 across the 9.0–10.0 centre range; the September Inside Airbnb dumps re-set it).

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 2026-09-30 | September Inside Airbnb reviews/calendar dumps; R01/R02 re-set the print centre (adopted_print_states_v2.json is rewritten) | Re-run `x01_joint.py` (it reads the file): each +0.5pt on the centre ≈ +0.02 breaker, −0.04 short, +0.03 none (§7 row 1) |
| 2026-10-02 | Prelim memo freeze | Quote 0.14 / 0.22 / 0.55 / 0.09 with the literal definition stated, or 0.14 / 0.26 / 0.49 / 0.11 with the material one — the memo must name which; replace 25/45/30; add the "none" row; carry the scenario table's day-1 and 15 Dec rows (base = short on the day) |
| 2026-10-13 | EEA/CH single-fee migration deadline (C01's fee-step weights) | C01 0.72 → 0.64–0.67 if the full step is confirmed; X01 moves < 0.01 |
| 2026-10-15 to 2026-11-03 | Sell-side 3Q26 previews; Street 4Q26 mean re-captured; any management QTD remark; EXPE/BKNG prints (~28–30 Oct) | Re-run with the refreshed C01 and C02 inputs if either moves ≥0.03; C02 (a) +0.03 ≈ breaker +0.02 |
| 2026-11-04 | Record the resolution Street value (LSEG-family 4Q26 revenue mean) | Fix the C01 gate value |
| 2026-11-05 (after close) | 3Q26 letter: printed nights (rate to one decimal on 133.6m), 4Q26 nights descriptor (C02), 4Q26 revenue range midpoint vs the 4 Nov mean (C01), FY26 margin sentence (C04) | Resolve mechanically under §0b conventions 1–7 and precedence 6; record which gates tripped |
| 2026-11-06 / 2026-12-15 | Reaction close; 15 Dec close | Score the scenario table's conditional rows (S01/S02 objects), not X01 |
