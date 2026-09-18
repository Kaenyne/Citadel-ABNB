# Independent research audit — batch A19 (X01, scenario-probabilities)

**X01 verdict: revise the option definitions before the memo quotes the vector.**
**Object:** the joint is real, seeded and reproduces to four decimals; the *classification* laid over it does not match the question's own words for the base option.
**Reproduction:** the published vector 0.1394 / 0.2231 / 0.5547 / 0.0828, every marginal check, the scenario table, the compositions, the base-rate panel and all 27 sensitivity rows replay exactly; a stdlib grid quadrature written for this audit reproduces the vector independently of the Monte Carlo to ≤0.0007 per cell.
**First required change:** the base option's gate is coded as "print < 10.6%", which is the *breaker* gate, not the question's "decelerating print". Correcting it to the S01 dead-band decel line moves **base 0.223 → 0.172 and "none" 0.083 → 0.134**; the change is not in §7 and not in the conventions.
**Assessment:** the short case being the modal option is robust (0.48–0.59 across every reading, precedence and gate variant tested) and the memo's breaker 0.25 is not reachable under the adopted print distribution; but the headline definitional choice is cited to a document that does not exist, "base = short on the day" is an artefact of the mis-set gate, and the memo's 25/45/30 *is* defensible under a published input — as the print-only partition (0.26 / 0.45 / 0.29), which is a different object from X01's disclosure gates.

Audit date 2026-09-17. Read-only; nothing in the repository was modified except this file and `A19.done`. `py -3.13` (numpy 2.x) and the repo `python` were both available. `datasets/x01_joint.py` was **not** run in place — it writes five files into its own `datasets/` directory. It was copied to a scratch directory with `HERE`/`QDIR`/`ROOT` repointed at absolute repo paths and run there (seed 20260917, n 1,000,000, ~4 min, exit 0); every figure below comes from that replay, from a reclassification of the identical draw arrays, or from the independent stdlib quadrature in the reproduction script. Neither prohibited raw directory was opened. No network was used; X01 makes no external claim (§2 line 14 records no WebSearch/WebFetch).

References below use **Q** = `docs/pitch-forecasts/questions/scenario-probabilities/`, **log** = `Q/research-log.md`, **code** = `Q/datasets/x01_joint.py`, **forecast** = `Q/forecasts/2026-09-17-forecast.json`, **panel** = `Q/datasets/x01_base_rate_panel.csv`, **memo** = `deck/drafts/memo_v2_short_2026-09-16.md`.

## Ruling on the reading (the question the response agent must settle first)

The forecaster publishes a "literal" headline (short case = nights ≤8.5% **OR C02 (d) OR C04 (d)**, 0.55) and a "material" alternative (C02 leg = the explicit mid-single bucket only, 0.49), and says the memo must name which. Ruling, on the registered text in `QUESTIONS.md` § X01:

1. **The C02 leg: literal (whole option (d)) is the better reading, but the log's stated reason is not available.** X01's three scenario phrases are verbatim extracts of C02's option labels — "low double digits" or better = (a); "high single digits"/"around 10" = (b)/(c); "mid single digits" or lower = (d) — and the fine print requires coherence with C02, which resolves at the option level on 5 Nov. The registry's own header convention defines "bucket language" as *"the letter's or call's qualitative growth descriptor for the next quarter"*, which covers a directional "moderate" sentence. And the forecaster applies whole options for (a), (b) and (c) without objection; splitting only (d) would be asymmetric. **Against**: C02 (d)'s second clause is expressly "*without a bucket*", so a literal short case includes an outcome the X01 text calls a "bucket". The text is genuinely ambiguous on this clause and the memo must disclose the composition (§ below), but the option-level reading is the one a 5 Nov resolver can apply mechanically from C02's resolution, and it is the one I adopt.
2. **C02's directional "moderate" language does belong in the short gate under that reading** — but the memo cannot call the result "the short case" without the footnote that **0.34 of short-case mass** is a one-word directional sentence with no number, and **0.110** of it sits on a print of ≥10.0% nights. In substance those draws are the memo's *base* case.
3. **C04's "approximately 35.5%" does belong in the short gate.** C04 option (d) is *"any lower or softer language (<35.5% floor, 'approximately 35.5%', floor removed)"*; X01 says "FY26 margin floor weakened". Replacing a floor ("at least 35.5%") with a point at the same number removes the floor. The map is exact and needs no interpretation.
4. **The A19 brief the log leans on does not exist** (finding A19-02). The reading has to be defended from the question text, as above, not from a citation.

Both vectors are given below. The difference between them is 7 points of probability on the memo's headline scenario, so the memo must state the reading in the table, not in a footnote.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A19-01 | X01 | critical | `log:30` (convention 4); `code:232`; `forecast.final.definitions.base` | The base option is gated at **print < 10.6%**, which is the *breaker* threshold. The question says "base (**decelerating print** with the 4Q26 nights bucket …)" and gives "in-line print with in-line guide" as the example of **none**. The entire flat/in-line band — S01's dead band 10.09–10.59, mass **0.1031** — is therefore classified base whenever C02 ∈ {b,c} or C01 is Yes. 0.051 of probability sits in the option the question reserves for the opposite case. | Reclassified the identical draw arrays: at the S01 decel line (x < 10.09) the vector is **0.1394 / 0.1717 / 0.5547 / 0.1342**; at a strict "below 2Q26's 10.34" line, 0.1394 / 0.1985 / 0.5547 / 0.1074. The flat band alone splits 0.497 base / 0.428 short / 0.075 none under the published code. Independently confirmed by the stdlib quadrature (0.1398 / 0.1720 / 0.5540 / 0.1343). | Set the base gate to x < 10.09 (S01's decel state, which the fine print already requires X01 to be coherent with) and publish **base 0.17, none 0.13**. Add the gate to §7 as a row; it is a larger swing than nine of the thirteen rows already there. |
| A19-02 | X01 | critical | `log:29` (convention 3); `code:17,22`; `forecast.final.alternative_material_reading.note` | The single definitional choice that sets the headline — "the A19 brief operationalises the three legs at the option level of C02 and C04; I follow it as the headline" — is attributed to a document that is not in the repository. It is worth 7 points of probability on the short case (0.55 vs 0.48). | `grep -rn "operationalis"` over `docs/pitch-forecasts/` returns only this log, the code docstring and two unrelated A15 lines. The only brief text about X01 is `00_BRIEF.md:176` ("run batch X01 (scenario MC, reads all forecast JSONs)"), which says nothing about option-level gates. The A19 launch commit `9417fef` adds one line to `RUN_STATE.md` and no prompt. | Delete the citation and defend the reading from the question text (the four-point ruling above), or name the actual source if one exists outside the repo and mark it unverifiable. A pitch cannot rest its headline scenario probability on an uncheckable reference. |
| A19-03 | X01 | major | `log:135`; `forecast.scenario_table.read`; README "Headline" | "Base and short case are identical on the day and at 15 Dec" is an artefact of A19-01, and it **reverses** once the base gate is corrected. The published claim then becomes an argument the memo should not make in that form. | Published gate: base day-1 median −3.76 / short −3.80, 15 Dec $162.3 / $161.9 (reproduces). Decelerating gate: base **−4.66** vs short **−3.80**, 15 Dec **$160.6** vs **$161.9**, P(≤−8%) 0.356 vs 0.327. Cause: 10.2% of short-case draws are in S01's *accelerating* state and 11.0% have a print ≥10.0%, while a corrected base cell is 100% decelerating. | Replace the sentence with the accurate one: *the option labelled "short case" is not the bad-print option — a third of its mass is a directional word and a tenth of it sits on an accelerating print, so it carries no more day-1 downside than the base case, and under the corrected gate slightly less.* Keep the conclusion that the memo's $115–130 is a 12-month target, not a reaction-function output. |
| A19-04 | X01 | major | `log:81` (discard row), `log:89` (iii), `:163`; `forecast.estimates.anchor_source`; `forecast.monitoring[1].action` | "The memo's breaker 0.25 exceeds P(≥10.6) × P(a \| ≥10.6) under any published input; anchoring to it would break coherence" is used to justify discarding 25/45/30 wholesale and telling the memo to "replace" it. The memo's table is **not** a disclosure-gate table; its scenario row is a *print* partition, and as a print partition 25/45/30 reproduces almost exactly from the adopted distribution. | Under N(9.5, 1.70): P(≤8.5%) = **0.2881**, P(8.5–10.6%) = **0.4514**, P(≥10.6%) = **0.2605** → **26 / 45 / 29** against the memo's 25 / 45 / 30. (Separately I bounded the breaker claim: even at the top of the adopted file's own `centre_sensitivity`, centre 10.3, the joint's breaker is **0.166**, so 0.25 is indeed unreachable on the *language-conditioned* definition.) | Do not tell the memo to delete 25/45/30. Tell it there are two tables: a 12-month **print-partition** table at **0.26 / 0.45 / 0.29** (no "none" row needed, and its conditionals are monotone: day-1 +2.1% / −3.8% / −4.8%, 15 Dec $175 / $162 / $160) and X01's four-option **disclosure-gate** table. Label which is which. A judge shown 14/22/55/9 against a scenario column headed "≤8.5%, guide implies ≤7.5%, no bundle figure, floor at risk" will assume the memo believes P(that conjunction) = 0.55; it is **0.046**. |
| A19-05 | X01 | major | `log:84–89`; `forecast.estimates.independence_note`, `.anchor`, `.final_minus_anchor` | The three estimates are not independent and the anchor is not an anchor. The W2 base rate's short cell is driven by the (d) descriptor frequency (8 of 17), which is also 30% of the weight inside C02's own final vector that the joint is IPF-fitted to reproduce exactly. "The base rate (W2) and the joint agree on short (0.50 vs 0.55)" is the same evidence counted twice. The anchor is the team's own un-audited memo table, which no market prices and which the run was commissioned to replace. | C02 `forecasts/…json` `estimates.blend_weights` = decomposition 0.5 / base_rate 0.3 / anchor 0.2, with `base_rate_vector.d` = 0.39 from the same 17 descriptors the X01 panel reads. The X01 panel's short cell trips on `descriptor_option == "d"` in 8 of 16 rows. | Flag `NOT_INDEPENDENTLY_DERIVED` for the base-rate/decomposition pair; set `anchor: null` with `NO_EXTERNAL_ANCHOR` and keep the memo table as a labelled internal comparison. Do not report \|final − anchor\| = 0.25 in SYNTHESIS — it measures nothing (A12-22 precedent). |
| A19-06 | X01 | major | `log:135`; `forecast.scenario_table.read` | "The reaction panel gives no evidence that deeper decelerations sold harder on the day (the four ≥1.8-pt decelerations since 3Q22 averaged +1.8% raw)" reproduces (+1.75, n 4) but is window-inconsistent: it is carried by **4Q22 +13.4%**, a print outside both W1 and W2 under the repo's own two-window rule. The three W1 members average **−2.13%**. The conclusion survives on much better evidence the log never cites. | Panel regression of day-1 excess on the sequential change, decelerators only: **W1 n 9, slope −1.24pp per point, corr −0.62; W2 n 6, slope −1.62, corr −0.586** — i.e. within decelerating prints, deeper decelerations sold *less* hard (1Q25 −4.43pt → −0.48% excess; 3Q24 −0.21pt → −8.78%). Across all 16, corr(sequential change, excess) is +0.34 (W1) / +0.59 (W2), which is the sign effect S01 already prices. | Quote the two-window regression, not the four-observation mean. It makes the same point in both windows, survives the repo's window rule, and is the honest reason the memo cannot put a lower 5 Nov price on the short case. |
| A19-07 | X01 | major | `log:32` (convention 6); `forecast.final.definitions.precedence` | Precedence is undefined by the question and the justification given is about *returns*, not definitions: "the breaker wins because the memo's breaker is the growth outcome and the S01 cell for that print is positive". The overlap is a breaker print on which the FY26 margin floor is softened — and the memo's own breaker column requires the FY sentence at "approximately 36%", so under the memo's definition that draw is not a breaker. | Reproduced both rules: breaker-first **0.1394 / 0.2231 / 0.5547 / 0.0828**; short-first **0.1068 / 0.2231 / 0.5873 / 0.0828**. Overlap mass 0.0326. Confirmed by the stdlib quadrature (0.1070 / 0.5867). | State the rule as a convention with no textual basis, publish the breaker as **0.11–0.14**, and if the memo keeps its own breaker column (which requires an ≈36% FY sentence) use short-first for memo coherence. Do not defend a classification rule with a return statistic. |
| A19-08 | X01 | major | `log:135`; `forecast.scenario_table.pw_dec15_close_usd` = 164.8 | "Probability-weighted 15 Dec close $164.8" is Σ P × conditional **median**, which is not a probability-weighted close. Medians do not mix. The memo's analogous "probability-weighted price ≈ $146" is built from range midpoints, so the two numbers are computed on different conventions inside one document. | Σ P × conditional **mean** = **$167.2**, identical to the joint's unconditional mean $167.2; the unconditional **median** is $164.7. Verified on the replayed draws. | Publish **$167.2** as the probability-weighted close and $164.7 as the median, or relabel the field `pw_dec15_median_of_branches`. Whichever the memo carries, the scenario table and the memo's PW price must use the same convention. |
| A19-09 | X01 | minor | `log:102`; `forecast.final.alternative_material_reading.memo_conjunctive_short_case_mass` = 0.050 | The memo-conjunctive mass does not reproduce. | Same draws, same seed: P(nights ≤8.5% **and** C02 (d) **and** C04 (d)) = **0.0462** (MC s.e. 0.0002). The companion figure does reproduce: P(≤8.5% and (C02 (d) or C04 (d))) = **0.1937** vs the published 0.194. | Publish 0.046. It is the number the memo needs if it keeps a conjunctive short-case scenario, so it should be right. |
| A19-10 | X01 | minor | `code:78,218`; `log:29` | The "material" reading splits C02 (d) with a **constant** explicit-bucket share 0.12/0.31 = 0.387 at every print level. C02's own conditioning block implies the share is branch-varying and is derivable from published numbers. | From C02 `conditioning`: directional-moderate mass per branch = mass × `p_directional_by_branch` × `p_moderate_given_directional_by_branch` = 0.0582 / 0.0386 / 0.0911 (sums to 0.188 ≈ the published 0.19 sub-split), against branch (d) masses 0.074 / 0.059 / 0.179 → explicit shares **0.208 (≥10) / 0.348 (9–10) / 0.492 (<9)**. Implementing them moves the material short case 0.4862 → **0.4788** and none 0.1119 → 0.1176. | Immaterial to the number (0.007), but implement it and say so: the share is not a free parameter, it is in C02's own table, and a judge who checks will find the constant. |
| A19-11 | X01 | minor | `log:109` (claim 6 restated); `forecast.joint_structure.dec15`; `code:123` | The prose says the 15 Dec within-branch spread is "**26** post sessions at 30%"; the code uses **62/252** (S02's 36 pre + 26 post). 62 is the right number for a *branch-conditional* spread — knowing the print branch does not resolve pre-print diffusion — so the code is right and the description is wrong. | `abnb_path_mixture_v2.py:28` (`sessions_pre=36, sessions_post_to_dec15=26`). The construction checks out end to end: X01's unconditional 15 Dec percentiles **123.3 / 131.4 / 146.2 / 164.7 / 185.4 / 206.4 / 220.0** against S02's published 120.5 / 129.4 / 145.5 / 165.6 / 186.0 / 206.5 / 221.0, with P(≤150) 0.298 vs 0.30. | Correct the prose to 62 sessions and keep the sentence that the 0.65/0.35 options blend is applied as a location rescale — the percentile comparison above is the evidence that the rescale is adequate, and it belongs in §6 as a check. |
| A19-12 | X01 | minor | `code:238–249` | The day-1 return and the 15 Dec close are drawn from **independent** uniforms given the branch. The per-option marginals in the scenario table are therefore fine, but the file cannot answer any joint question, and "if 5 Nov is −8%, where is 15 Dec" is exactly the question the memo's catalyst section invites. | Read the code: `r` is filled from `uu` per S01 cell; `close` from an independent `standard_normal`. No correlation is imposed. | Say so in one line in §6, or correlate the two draws through a shared branch-level shock. Do not publish a day-1/15 Dec joint statement from this file. |
| A19-13 | X01 | minor | `code:344`; `log:84`; panel | The base rate's nights gate is a **sequential** analogue (`accel_pts <= -1.84`) of a **level** gate (≤8.5%). Defensible — the question's gate is 1.84pt below 2Q26's 10.34% — but the base rate is not robust to it, and only one version is published. | Reclassified the panel with `nights_yoy <= 8.5` instead: W2 literal **0.10 / 0.10 / 0.60 / 0.20** (published 0.10 / 0.20 / 0.50 / 0.20); W2 material 0.10 / 0.20 / 0.40 / 0.30 (published 0.10 / 0.30 / 0.30 / 0.30). Short moves 10 points in both readings. | Publish the base rate as a range (short 0.50–0.60 literal, 0.30–0.40 material) and name the analogue. The rank order — short modal under literal, not under material — is what survives, and that is the honest claim. |
| A19-14 | X01 | minor | `log:84`; claim 4; `forecast.sensitivity[6]` | The C04 leg is 0-for-16 historically and the November record is stronger than the log states. X01 inherits C04 (d) = 0.27 from A03 and it is the single largest exogenous driver of the short case, yet the log gives it one clause. | Panel `fy_margin_action`: the three November prints that carried an FY margin sentence (3Q23, 3Q24, 3Q25) all read **raised**; 3Q22 is "none"; no row in 16 reads lowered/softened. Dropping the C04 leg entirely takes short **0.5547 → 0.4437** (base → 0.3086); C04 (d) at 0.20 takes short to 0.53 (published row reproduces). | Add the "November: 3 of 3 raised, 0 of 16 ever softened" line to §5 next to the C04 leg, with the −0.11 gate-removal figure, so the reader can see how much of the 0.55 is a forward-looking judgement with no precedent. The bounded effect (−0.02 at C04 (d) = 0.20) is the reassuring half and should be there too. |
| A19-15 | X01 | minor | `log:106`; claim 2; `forecast.joint_structure.c01` | The C01 tilt is stated in the wrong units and its best validation is missing. 0.66 is *% of guide per 1% of GBV*; a **point** of nights growth is 0.913% of nights at a 9.5% base, so the slope in points is ≈**0.60**. Separately, the log asserts C01's slope beats S01's 0.32 but never shows it, when C01's own file settles it. | Recomputed the weight: ⅔ × 25.88 / (⅔ × 25.88 + ⅓ × 27.20) = **0.6556**. Validation: the joint gives P(below \| x ≥ 10.6) = **0.567** at E[x] = 11.96 → GBV ≈ $26.5bn, against C01 `monitoring[6]` "0.78 at $25.9bn, 0.69 at $26.2bn, **0.55 at $26.6bn**"; and P(below \| x < 10.0) = **0.795** against 0.78 at $25.9bn. | Correct the unit or the coefficient (immaterial: §7 shows no option moves by >0.001), and move the C01 monitoring comparison into §6. It is the reason 0.66 is right and S01's 0.32 is the outlier, and right now it is an assertion. |
| A19-16 | X01 | minor | `log:111`; `forecast.marginal_checks.unconditional_day1` | X01's unconditional day-1 (median −2.4, P(≤−8) 0.28, P(≥5) 0.21) is **not** S01's published object (−2.1 / 0.27 / 0.22), because S01 revision 2 is still built on the rev-1 print states. X01's is the rebased one. Correct and disclosed — but two day-1 objects will reach SYNTHESIS. | `adopted_print_states_v2.json` `rebasing.S01` ("YES … median about −0.3"); X01's replay gives exactly −2.4. | In SYNTHESIS, name X01's day-1 as the rebased S01 object and either re-run `s01_joint_v2.py` on the adopted states or footnote S01's published numbers as pre-rebasing. The memo must quote one. |
| A19-17 | X01 | minor | `log:84` | "The directional 'moderate' sentence was management's default next-quarter language (**8 of 17** descriptors)" conflates the option with the sub-branch. This is the sentence that carries the literal reading, so it should be exact. | Descriptor dataset: 8 of 17 resolve **(d)**, of which **7** are directional and **1** (3Q25, an explicit 4–6% bucket for 4Q25) is a bucket. So directional-moderate is 7 of 17; explicit mid-single buckets are 1 of 17. | Write "8 of 17 descriptors resolve (d); 7 of those 8 were directional, and only once in 17 did the letter name a mid-single-digit bucket". The second half is the strongest argument *for* the material reading and the log omits it. |
| A19-18 | X01 | minor | `log:67` (§2 line 14); `forecast.estimates.anchor` | The skill's market cross-reference was skipped and a sibling's internal table put in the anchor slot. The reasoning given ("not applicable to a synthesis object") is fine; the consequence was not followed through. | No `sources/` directory exists under `Q/`. The anchor field carries the memo. | Either leave `anchor: null` (A19-05) or, if an anchor is wanted, derive it from the Kalshi KXABNB nights ladder that C02/R01 already saved — it prices the print leg (P(≤8.5%)) if not the language legs, and it is at least external. |

## What the X01 log does well and should keep

The joint is the right object and it was built the right way. §4's first discard row — that a product of marginals gives breaker 0.047 and short 0.63 and is wrong in both directions — is the correct diagnosis, and the construction that replaces it (piecewise log-odds in nights through C02's own three branch anchors, IPF-fitted so the marginal lands exactly on C02's published vector, C01 entering through its own guide structure, C04 through its published conditionals) is the least-invasive way to get a joint that does not re-forecast anything upstream. Nothing is re-estimated; the conditionals that drift (P(Q3 ≥10 | a) 0.887 vs C02's 0.92; P(Q3 <9 | d) 0.607 vs 0.57) are the two the construction cannot hold fixed, and both are disclosed with their sizes.

The marginal-check block in §6 is the single best thing in the log and should be the template for every future synthesis question. Every one of these replays: print states 0.6146 / 0.1248 / 0.2606 against the adopted 0.614 / 0.126 / 0.260; S01 states 0.6361 / 0.1031 / 0.2608 against 0.6357 / 0.1036 / 0.2607; C01 0.7208; C02 0.1795 / 0.1695 / 0.3004 / 0.3104 / 0.0401; C04 0.3347 / 0.2972 / 0.0473 / 0.2713 / 0.0496 with (d)|below 0.317 and |not-below 0.152; the S01 breaker cell 0.1129 against 0.112; C01 `g0` −1.923; the C02 IPF factors 0.001 / 0.009 / 0.023 / −0.062 / 0.325. The 15 Dec construction, which the log describes least well (A19-11), turns out to be the one that needed checking least: its unconditional percentiles sit on S02's published table across the whole distribution.

The following also survive re-reading and recomputation:

| Source and definition | Recomputed result |
|---|---|
| `x01_joint.py`, seed 20260917, n 1,000,000 — published vector | **0.1394 / 0.2231 / 0.5547 / 0.0828**, exact |
| Independent stdlib grid quadrature (this audit, no Monte Carlo) | **0.1398 / 0.2238 / 0.5540 / 0.0825** — every cell within 0.0007 |
| Short-case composition | nights-only 0.0949, C02 (d)-only 0.1120, C04 (d)-only 0.1110, two-or-more 0.2368, directional share of short 0.342, short with print ≥10.0% 0.1102 — all exact |
| "None" composition | accelerating print, non-(a) descriptor, no short gate 0.0646; C02 (a) or (e) with guide at/above 0.0183 — exact |
| Base-rate panel, all 16 / W1 n 14 / W2 n 10, literal | 0.062/0.125/0.688/0.125; 0.071/0.143/0.643/0.143; **0.10/0.20/0.50/0.20** — exact |
| Base-rate panel, material | all 16 0.062/0.250/0.312/0.375; W1 0.071/0.286/0.286/0.357; W2 0.10/0.30/0.30/0.30 — exact |
| §5 breaker reconciliation: 0.25 needs P(a \| ≥10.6) ≈ 0.96 | 0.25 / 0.2605 = **0.960**; the joint's P(a \| accel) is 0.535; accelerating prints gave (a) in **1 of 6** historically (2Q26) |
| "Four ≥1.8-pt decelerations averaged +1.8% raw" | **+1.75%**, n 4 — reproduces, but see A19-06 |
| "Margin floor never softened" | **0 of 16**; the three November FY-margin sentences all read "raised" |
| All 27 sensitivity rows, incl. seed 20260918 | 0.1397 / 0.2239 / 0.5541 / 0.0823 — every row replays |

The strongest countercase to the published number is the one §7 half-names and does not press: **two of the three short-case gates are language events with weak or no precedent in the relevant window** — the FY margin floor has never been softened in 16 prints and was raised in all three Novembers, and the explicit mid-single-digit bucket has appeared once in 17 descriptors. Remove the C04 leg and the short case is 0.444; take the material reading of the C02 leg and it is 0.479; do both and it falls further. The 0.55 is a bet that the November letter's *wording* turns negative in at least one of three places, on a print the run's own centre puts at +9.5% — a good quarter by the Street's 4Q26 bar. That bet is defensible, and the log should say out loud that it is a wording bet, because that is what a Citadel judge will call it.

Two things the memo should not carry from this log without the repairs above: the sentence that base and short are the same trade (A19-03, and it reverses), and the instruction to delete 25/45/30 (A19-04, which is right as a print partition).

## Independent X01 forecast

Constructed by reclassifying the forecaster's own draws and, independently, by stdlib quadrature over the same joint. This is an independent *construction*, not independent underlying evidence: it inherits R01/R02, C01, C02, C04, S01 and S02 exactly as X01 does.

**Literal reading (my headline):**

| Option | P |
|---|---:|
| thesis breaker (print ≥10.6% **and** C02 (a)) | **0.14** |
| base (**decelerating** print **and** (C02 (b)/(c) **or** C01 Yes) **and** not short) | **0.17** |
| short case (print ≤8.5% **or** C02 (d) **or** C04 (d)) | **0.55** |
| none of the above | **0.14** |

**Material reading:** 0.14 / 0.20 / 0.48 / 0.18. **Under short-first precedence:** literal 0.11 / 0.17 / 0.59 / 0.13.

**Derivation, line 1:** Take the published joint unchanged — it reproduces every audited marginal — and make one change: gate the base option on a *decelerating* print (x < 10.09, S01's dead-band line, which the fine print already obliges X01 to share) instead of x < 10.6. Raw output 0.1394 / 0.1717 / 0.5547 / 0.1342 (quadrature 0.1398 / 0.1720 / 0.5540 / 0.1343).
**Derivation, line 2:** Round "none" up to 0.14 at the short case's expense rather than by largest remainder, because both the independent pressures on that cell push the same way — the W2 panel puts none at 0.20–0.30 under this gate, and §6's own resolution-criteria audit concedes 0.02–0.03 more would move to none under a broader reading of "in-line print with in-line guide". No other judgemental adjustment is applied and I do not shrink toward the base rate, which is not independent evidence (A19-05).

**Conditional table under my definitions** (day-1 from the S01 rev-2 cells, 15 Dec from the S02 rev-2 branches, same draws):

| Option | P | day-1 median | P(≤−8%) | P(≥+5%) | 15 Dec median | p25–p75 | E[3Q26 nights] | P(C01 below) |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| thesis breaker | 0.14 | +2.2% | 0.12 | 0.37 | $175 | 156–197 | 12.0% | 0.50 |
| base | 0.17 | **−4.7%** | 0.36 | 0.15 | **$161** | 143–180 | 9.4% | 0.72 |
| short case | 0.55 | −3.8% | 0.33 | 0.18 | $162 | 144–182 | 8.6% | 0.82 |
| none of the above | 0.14 | +0.3% | 0.17 | 0.29 | $171 | 152–192 | 10.7% | 0.54 |

Probability-weighted 15 Dec close **$167.2** (mean convention); median $164.7.

**What the memo should quote.** Two tables, labelled:

1. **The 12-month scenario table** keeps three columns and re-derives its probabilities from the *print* gate alone — **0.26 breaker (≥10.6%) / 0.45 base (8.5–10.6%) / 0.29 short (≤8.5%)** — which is within a point of the memo's existing 25/45/30 and is the partition its own scenario row describes. Its conditionals are monotone and publishable: day-1 +2.1% / −3.8% / −4.8%; 15 Dec median $175 / $162 / $160 (mean $178 / $165 / $162; p25 $156 / $144 / $142). The memo's $115–130 short-case price remains a 12-month fundamental target and must be labelled as such, because nothing in this run produces it for 15 Dec.
2. **The 5 Nov disclosure table** carries X01 in full — **0.14 / 0.17 / 0.55 / 0.14**, literal reading named in the header, with the one-line composition note that 0.34 of the short case is a directional "moderate" sentence and 0.11 of it sits on a print of ≥10.0% nights. If the memo prefers the material reading, quote 0.14 / 0.20 / 0.48 / 0.18 and say so in the same header.

If only one number can be carried, it is P(short case) and it should be given as a range, **0.48–0.55, reading-dependent**, not as 0.55.

## Reproduction script

Run from the repository root:

```powershell
py -3.13 docs/pitch-forecasts/audits/A19-reproduce.py
```

Standard library and `csv` only — no numpy, no pandas, no network, no writes. It recomputes the print partition, the full option vector by grid quadrature under every gate/reading/precedence variant tested above (independently of the Monte Carlo), the base-rate panel under both nights-gate analogues and both readings, the within-decelerator regressions, the C02 branch-varying explicit share, and the probability-weighted-close arithmetic. The 1,000,000-draw replay of `x01_joint.py`, the day-1/15 Dec conditional tables and the memo-conjunctive mass were produced separately as described at the top.

```python
"""A19 audit reproduction — X01 scenario-probabilities. Stdlib only; reads, prints, writes nothing."""
import csv, math
from pathlib import Path
from statistics import NormalDist

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
Phi = NormalDist().cdf

CENTRE, SD, GAP_SD, TILT, OR_C02 = 9.5, 1.70, 3.1, 0.66, 2.0
THR_R01, THR_R02, SHORT_THR = 9.9925149701, 10.5913173652, 8.55
P_C01, C04_D_BELOW, C04_D_NOT = 0.72, 0.3171, 0.1524
DECEL_THR = 10.09                      # S01 revision-2 dead band on 2Q26's 10.34
OPTS = ["breaker", "base", "short", "none"]

# ---------------------------------------------------------------- 1. print partition
print("print partition  P(<=8.5) %.4f  P(8.5-10.6) %.4f  P(>=10.6) %.4f" % (
    Phi((SHORT_THR - CENTRE) / SD),
    Phi((THR_R02 - CENTRE) / SD) - Phi((SHORT_THR - CENTRE) / SD),
    1 - Phi((THR_R02 - CENTRE) / SD)))

# ---------------------------------------------------------------- 2. C02 revision-2 branch table
c02_final, branch = [], {}
with open(Q / "q4-nights-bucket/datasets/decomposition_v2_output.csv", encoding="utf-8") as f:
    block = None
    for row in csv.reader(f):
        if not row or not row[0]:
            continue
        if row[0] in ("estimate", "joint_branch"):
            block = row[0]
            continue
        if block == "estimate" and row[0] == "final":
            c02_final = [float(v) for v in row[1:6]]
        if block == "joint_branch":
            mass = float(row[6])
            branch[row[0]] = dict(mass=mass, cond=[float(v) / mass for v in row[1:6]])


def truncated_mean(lo, hi, mu, sd):
    def pdf(z):
        return math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
    a = None if lo is None else (lo - mu) / sd
    b = None if hi is None else (hi - mu) / sd
    Fa, Fb = (0.0 if a is None else Phi(a)), (1.0 if b is None else Phi(b))
    fa, fb = (0.0 if a is None else pdf(a)), (0.0 if b is None else pdf(b))
    return mu + sd * (fa - fb) / (Fb - Fa)


# anchors at the branch means of the rev-1 normal the C02 tree was built on
ANCHOR_X = [truncated_mean(None, 9.0, 9.67, 1.70),
            truncated_mean(9.0, 10.0, 9.67, 1.70),
            truncated_mean(10.0, None, 9.67, 1.70)]
ANCHOR_L = [[math.log(p) for p in branch[k]["cond"]] for k in ("lt9", "9to10", "ge10")]
print("C02 anchors", [round(v, 3) for v in ANCHOR_X])

# branch-varying explicit-bucket share of option (d), from C02's own conditioning block
DIRECTIONAL = {"lt9": 0.35 * 0.75, "9to10": 0.28 * 0.60, "ge10": 0.25 * 0.55}
EXPLICIT_SHARE = {}
for k in ("lt9", "9to10", "ge10"):
    EXPLICIT_SHARE[k] = 1 - DIRECTIONAL[k] / branch[k]["cond"][3]
print("explicit-bucket share of (d) by branch",
      {k: round(v, 3) for k, v in EXPLICIT_SHARE.items()},
      "  directional-moderate total",
      round(sum(branch[k]["mass"] * DIRECTIONAL[k] for k in DIRECTIONAL), 4))


def logits(x):
    xc = min(max(x, 6.0), 14.0)
    out = []
    for j in range(5):
        s0 = (ANCHOR_L[1][j] - ANCHOR_L[0][j]) / (ANCHOR_X[1] - ANCHOR_X[0])
        s2 = (ANCHOR_L[2][j] - ANCHOR_L[1][j]) / (ANCHOR_X[2] - ANCHOR_X[1])
        if xc <= ANCHOR_X[1]:
            out.append(ANCHOR_L[0][j] + s0 * (xc - ANCHOR_X[0]))
        else:
            out.append(ANCHOR_L[1][j] + s2 * (xc - ANCHOR_X[1]))
    return out


# IPF on the model's own 0.01 grid, so the fitted factors match the published ones
GRID = [4.0 + i * 0.01 for i in range(1201)]
W = [math.exp(-0.5 * ((g - CENTRE) / SD) ** 2) for g in GRID]
W = [w / sum(W) for w in W]
LG = [logits(g) for g in GRID]
FACT = [0.0] * 5
for _ in range(400):
    marg = [0.0] * 5
    for w, lg in zip(W, LG):
        e = [math.exp(lg[j] + FACT[j]) for j in range(5)]
        t = sum(e)
        for j in range(5):
            marg[j] += w * e[j] / t
    for j in range(5):
        FACT[j] += math.log(c02_final[j] / marg[j])
print("C02 IPF factors", [round(v, 3) for v in FACT], " target", c02_final)

# ---------------------------------------------------------------- 3. C01 intercept
def mean_p_below(g0):
    return sum(w * Phi(-(g0 + TILT * (g - CENTRE)) / GAP_SD) for w, g in zip(W, GRID))


lo, hi = -10.0, 10.0
for _ in range(100):
    mid = 0.5 * (lo + hi)
    lo, hi = (mid, hi) if mean_p_below(mid) > P_C01 else (lo, mid)
G0 = 0.5 * (lo + hi)
print("C01 g0 %.4f  implied P(below) %.4f" % (G0, mean_p_below(G0)))
print("C01 slope check: 2/3 weight on GBV = %.4f" % (
    (2 / 3 * 25.88) / (2 / 3 * 25.88 + 1 / 3 * 27.20)),
    " per point of nights growth = %.3f" % (0.6556 / 1.095))


def cd_split(marginal, p_below, odds_ratio):
    """P(c or d | below), P(c or d | not below) with the given odds ratio and marginal."""
    lo, hi = 1e-9, 1 - 1e-9
    for _ in range(80):
        pa = 0.5 * (lo + hi)
        pb = odds_ratio * pa / (1 - pa + odds_ratio * pa)
        lo, hi = (lo, pa) if p_below * pb + (1 - p_below) * pa > marginal else (pa, hi)
    pa = 0.5 * (lo + hi)
    return odds_ratio * pa / (1 - pa + odds_ratio * pa), pa


# ---------------------------------------------------------------- 4. the vector, by quadrature
FINE = [2.0 + i * 0.0005 for i in range(32001)]
FW = [math.exp(-0.5 * ((g - CENTRE) / SD) ** 2) for g in FINE]
FW = [w / sum(FW) for w in FW]
FLG = [logits(g) for g in FINE]


def vector(base_thr=THR_R02, reading="literal", precedence="breaker_first",
           short_thr=SHORT_THR, breaker_thr=THR_R02,
           c04_d_below=C04_D_BELOW, c04_d_not=C04_D_NOT, use_c04=True):
    total = {o: 0.0 for o in OPTS}
    for w, g, lg in zip(FW, FINE, FLG):
        if w < 1e-13:
            continue
        e = [math.exp(lg[j] + FACT[j]) for j in range(5)]
        pc = [v / sum(e) for v in e]
        p_cd = pc[2] + pc[3]
        d_share = pc[3] / max(p_cd, 1e-12)
        p_below = Phi(-(G0 + TILT * (g - CENTRE)) / GAP_SD)
        cd_b, cd_a = cd_split(p_cd, p_below, OR_C02)
        share = (EXPLICIT_SHARE["lt9"] if g < 9.0 else
                 EXPLICIT_SHARE["9to10"] if g < 10.0 else
                 EXPLICIT_SHARE["ge10"]) if reading == "material" else 1.0
        for below, pb in ((True, p_below), (False, 1 - p_below)):
            if pb <= 0:
                continue
            cd = cd_b if below else cd_a
            rest = (1 - cd) / max(1 - p_cd, 1e-12)
            opts = {"a": rest * pc[0], "b": rest * pc[1], "e": rest * pc[4],
                    "c": cd * (1 - d_share), "d": cd * d_share}
            p_c04d = (c04_d_below if below else c04_d_not) if use_c04 else 0.0
            for o2, p2 in opts.items():
                for c04d, p4 in ((True, p_c04d), (False, 1 - p_c04d)):
                    for frac, d_gate in ([(share, True), (1 - share, False)]
                                         if o2 == "d" else [(1.0, False)]):
                        m = w * pb * p2 * p4 * frac
                        if m <= 0:
                            continue
                        breaker = (g >= breaker_thr) and o2 == "a"
                        short = (g < short_thr) or d_gate or c04d
                        base = (g < base_thr) and (o2 in ("b", "c") or below) and not short
                        if precedence == "breaker_first":
                            o = ("breaker" if breaker else "short" if short
                                 else "base" if base else "none")
                        else:
                            o = ("short" if short else "breaker" if breaker
                                 else "base" if base else "none")
                        total[o] += m
    return {k: round(v, 4) for k, v in total.items()}


print("published gates            ", vector())
print("decelerating base gate     ", vector(base_thr=DECEL_THR))
print("strict decel (<10.34)      ", vector(base_thr=10.34))
print("short-first precedence     ", vector(precedence="short_first"))
print("material (branch shares)   ", vector(reading="material"))
print("material + decel gate      ", vector(base_thr=DECEL_THR, reading="material"))
print("no C04 leg                 ", vector(use_c04=False))
print("C04 (d) at 0.20            ", vector(c04_d_below=0.3171 * 0.20 / 0.27,
                                            c04_d_not=0.1524 * 0.20 / 0.27))

# ---------------------------------------------------------------- 5. base-rate panel
rows = list(csv.DictReader(open(
    Q / "scenario-probabilities/datasets/x01_base_rate_panel.csv", encoding="utf-8")))
for r in rows:
    r["accel_pts"] = float(r["accel_pts"])
    r["nights_yoy"] = float(r["nights_yoy"])
    r["raw"] = float(r["ret_1d_raw"])
    r["excess"] = float(r["ret_1d_excess"])
    r["below"] = r["guide_below_street"] == "True"


def classify(r, base_thr=0.25, material=False, level_gate=False):
    opt = r["descriptor_option"]
    d_gate = (r["descriptor_type"] == "bucket" and opt == "d") if material else opt == "d"
    nights = (r["nights_yoy"] <= 8.5) if level_gate else (r["accel_pts"] <= -1.84)
    short = nights or d_gate or r["fy_margin_action"] in ("lowered", "softened")
    if (r["accel_pts"] >= 0.25) and opt == "a":
        return "breaker"
    if short:
        return "short"
    if (r["accel_pts"] < base_thr) and (opt in ("b", "c") or r["below"]) and not short:
        return "base"
    return "none"


WINDOWS = {"all16": lambda r: True,
           "W1": lambda r: r["print_date"] >= "2023-05-01",
           "W2": lambda r: r["print_date"] >= "2024-05-01"}
for thr, gl in ((0.25, "published base gate"), (-0.25, "decelerating base gate")):
    for material in (False, True):
        for level in (False, True):
            for wname, wf in WINDOWS.items():
                sub = [r for r in rows if wf(r)]
                cells = [classify(r, thr, material, level) for r in sub]
                print(gl, "material" if material else "literal",
                      "level-gate" if level else "sequential-gate", wname, "n", len(sub),
                      {o: round(cells.count(o) / len(cells), 3) for o in OPTS})

print("FY margin actions, November prints",
      [(r["print_quarter"], r["fy_margin_action"]) for r in rows
       if r["print_quarter"].startswith("3Q")])
print("descriptor options: (d) count", sum(1 for r in rows if r["descriptor_option"] == "d"),
      " of which explicit buckets",
      sum(1 for r in rows if r["descriptor_option"] == "d"
          and r["descriptor_type"] == "bucket"))


# ---------------------------------------------------------------- 6. reaction regressions
def ols(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    return sxy / sxx, my - (sxy / sxx) * mx, sxy / math.sqrt(sxx * syy)


deep = [r for r in rows if r["accel_pts"] <= -1.84]
print("deep decelerations n", len(deep),
      "mean raw %.2f" % (sum(r["raw"] for r in deep) / len(deep)),
      [(r["print_quarter"], r["raw"]) for r in deep])
deep_w1 = [r for r in deep if r["print_date"] >= "2023-05-01"]
print("  in W1 only: n", len(deep_w1),
      "mean raw %.2f" % (sum(r["raw"] for r in deep_w1) / len(deep_w1)))
for wname, wf in WINDOWS.items():
    sub = [r for r in rows if wf(r)]
    b, a, rho = ols([r["accel_pts"] for r in sub], [r["excess"] for r in sub])
    print(wname, "all prints  n", len(sub), "slope %.2f corr %.3f" % (b, rho))
    dec = [r for r in sub if r["accel_pts"] < 0]
    b, a, rho = ols([r["accel_pts"] for r in dec], [r["excess"] for r in dec])
    print(wname, "decelerators n", len(dec),
          "slope %.2f intercept %.2f corr %.3f" % (b, a, rho))

# ---------------------------------------------------------------- 7. memo arithmetic
scen = {"breaker": (0.1394, 175.1, 177.7), "base": (0.2231, 162.3, 164.8),
        "short": (0.5547, 161.9, 164.4), "none": (0.0828, 173.1, 175.7)}
print("PW 15 Dec by conditional median %.1f (published 164.8)"
      % sum(p * m for p, m, _ in scen.values()))
print("PW 15 Dec by conditional mean   %.1f (= the joint's unconditional mean)"
      % sum(p * mu for p, _, mu in scen.values()))
print("memo breaker 0.25 needs P(a | >=10.6) = %.3f against the joint's 0.535"
      % (0.25 / (1 - Phi((THR_R02 - CENTRE) / SD))))
```
