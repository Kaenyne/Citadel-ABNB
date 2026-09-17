# Audit response — batch A17 (B11, B12, B13)

Responding agent: Fable (audit-response pass), 2026-09-17. Audit under response: `A17-research-audit.md`, written by an independent Opus auditor standing in for Codex. Every finding was reproduced with `py -3.13` before it was ruled on; the audit's own script was saved as `A17-reproduce.py` and run end to end (output in §4 below, exit code 0, no path bugs, ~3 minutes).

Revised logs and forecasts (all at `revision: 2`, `run_mode: initial`, `revised: 2026-09-17`):
`questions/bonus-sellside-downgrades/`, `questions/bonus-fy27-investment-year/`, `questions/bonus-q4-nights-print-weak/`.
New models, written alongside the untouched revision-1 scripts: `b11_model_v2.py`, `b12_model_v2.py`, `b13_model_v2.py`.

## 1. Summary

**25 findings: 17 accepted in full, 6 accepted in part, 1 accepted as a specification note, 1 rejected on its arithmetic while accepted on its evidence.** The audit is the strongest of the run so far — it caught a withdrawn parameter set that a `must_adopt` list had named by id, a model running 1.6× every base rate it quoted, three whole citation blocks one revision out of date, and an impact table that used one coefficient two incompatible ways in the same eleven rows. Nothing in it was wrong on a fact. One finding is wrong on its *arithmetic*, and that is the response's main contribution back.

Three headline numbers:

- **B11 0.14 → 0.11.** The audit was right that the model ran on S02 revision 1, right that the rates are double-thinned, and right that the exponential modulations inflate the level. Revision 2 rebuilds on S02 revision 2 and adds **recentring** — dividing each count mean by its simulated `E[modulation]` so the unconditional mean equals a named base rate by construction. The model now runs at **2.98 downgrades a year** against a measured print-shaped-window 3.03/yr; revision 1 ran at 4.81. The audit proposed recentring as its own first-choice fix and then did not apply it in its own rebuild; applying it is worth about −0.03, which is the whole difference between its 0.13 and this 0.11.
- **B12 literal 0.50 → 0.49, material 0.38 → 0.36.** Every F03/F04/C04 citation is now revision 2, the impact table is computed rather than asserted, and the −$5/−$7 stock line is replaced by a split, smaller, defensible −$3.9/−$5.5 with the February reaction handed back to S03. The headline barely moves because the audit's two structural attacks, once implemented, either do not do what they say (A17-09) or belong to F03 rather than here (A17-10).
- **B13 0.26 → 0.31.** Accepted in full and without argument: `adopted_q4_states_v2.json` names this question by id and says 0.309, and `b13_model_v2.py` reproduces it to four decimals. Every §9 line moved with it, and every one moved *toward* the short case.

## 2. Finding-by-finding

### B11

**A17-01 to A17-02** — B13 findings, below.

**A17-03 (major, B11): the counts are thinned twice.** — **Accepted in part.**
The diagnosis is exactly right and is now stated in claim 7 and §5: `pre_mu` and `post_mu` are calibrated on `downgrade_base_rates.json`, which counts rows in the yfinance/Benzinga feed, and the feed is also the resolving object. I reproduce the audit's numbers on revision-2 parameters (capture 0.85 → 0.1408, capture 1.0 → 0.1792).
The *fix* is not adopted, for the reason the finding itself gives: "whichever way the run resolves it, it must resolve it the same way in both." R12 revision 2 resolves the identical construction on the identical feed by keeping 0.85 and calling it "a stated ~2–3 point conservatism because the means are feed-measured" (`risk-sellside-upgrades/forecasts/2026-09-17-forecast.json`, `estimates.conventions`). B11 revision 2 therefore keeps 0.85 as the base, states the conservatism in the same words, and publishes the capture-1.0 reading beside it in §5, §6 and §7: **0.0785 at 0.85, 0.1021 at 1.0.**
The finding's correction of the task brief is also confirmed: B11's base capture was already 0.85, not 1.0. The two questions were coherent on capture and incoherent on S02.

**A17-04 (major, B11): the model's unconditional mean is above every base rate it is compared with.** — **Accepted.**
Reproduced: with `k_pre = k_post = beta_d1 = 0` the mean falls 1.173 → 0.938 and P 0.1550 → 0.1075, and the published model runs at 4.81 downgrades a year against measured 3.51 / 3.51 / 2.59 / 0 and a print-shaped-window 3.03.
Revision 2 takes the finding's **first** proposed fix, which its own independent number did not: `b11_model_v2.py` gains `recentre=True`, dividing each mean by its simulated `E[modulation]`. The diagnostic is now a claim of its own (claim 13): the modulation means are **1.12** on the pre block and **1.30–1.32** on the post block by branch. That alone is a 1.3× level error; the rest of the gap to 1.6× is the revision-1 post means, of which the decel-below 1.1 sits 1.33× the feed's own post-print mean for day-1 ≤ −5% prints (0.833).
Post means are also moved to **0.085 / 0.525 / 0.625 / 0.965** — the midpoint of the revision-1 judgement and the feed's print-window means by day-1 sign — which is exactly the construction R12 revision 2 used on its own post means. After recentring the model's mean is **0.726 per 89 days = 2.98/yr**, against the measured 3.03.

**A17-05 (major, B11): the entire simulation uses S02 revision 1.** — **Accepted.**
Reproduced to the parameter: the revision-2 set (0.32 / 0.10 / 0.13 / 0.45, post drifts −1.5 / −0.5 / −0.5 / −1.0, 36 pre / 26 post, 30% vol, 6.97% drift) and the variance identity returning a within-branch day-1 sd of **8.451**, matching `abnb_path_mixture_v2.py`'s solved value. Claim 8 is rewritten; `b11_model_v2.py` carries a bridge row that reproduces the revision-1 number exactly (**0.1539** against the file's 0.15393). §9's "0.52 unconditional" is now 0.45.
One number differs from the audit's. The audit computed the December marker at **−$14.8** on revision-2 parameters with the revision-1 count structure. On the *corrected* count model the marker is **−$15.8** (E[15 Dec | Yes] $149.65 vs $165.46; median $147.08 vs $163.07). The difference is compositional: recentring changes which paths produce three downgrades, and the surviving Yes set is more concentrated in the decel-below branch. EV is unchanged in substance (−$1.8 → −$1.7).

**A17-06 (major, B11): the "anchor" is one of the log's own base-rate families.** — **Accepted.**
`downgrade_base_rates.json` `print_windows_P(>=3)_all` = 0.08696; `estimates.base_rate_detail.print_windows_all` = 0.087; `estimates.anchor` = 0.09. They are the same statistic. §5 now carries **`anchor_independent: false`** with the reason spelled out, exactly as R12 revision 2 does, and says plainly that no independent anchor exists for this object. `final_minus_anchor` is labelled a diagnostic.

**A17-07 (major, B11): conventions (1) and (4) contradict each other on Phillip.** — **Accepted.**
Verified directly: `feed_downgrades_all.csv` row 18 is `2024-11-12, Phillip Securities, Neutral, Reduce`. Convention (4) is rewritten to "an action the feed does not carry does not count, whoever the firm", Phillip is removed from the excluded-firm list with its feed row named, the 11 Aug 2026 action is identified as the dropped *action*, and Weiss stays out on the same rule. This is the resolution sentence the 15 Dec pull will be run against, so it mattered.

**A17-08 (major, B11): the headline mechanism has no positive observation.** — **Accepted.**
Reproduced from the audit's script: by day-1 sign, up ≥ +5% n 6 mean 0.167 P(≥3) **0.000**; small n 11 mean 0.909 P(≥3) **0.182**; down ≤ −5% n 6 mean 1.000 P(≥3) **0.000**. Both ≥3 windows followed small day-1 moves (Feb 2022 +3.6%, Nov 2023 −3.3%).
Claim 4 now quotes the by-sign row; §4 carries a new entry demoting the day-1 ladder to a model output with n 6 and zero supporting events; the §8 5-November row is rewritten to "**the bucket, not the day-1 move, is the signal**"; the pre-mortem says so too. The corrected model's ladder is also flatter — P(Yes | day-1 ≤ −8%) falls 0.30 → **0.17** — so the model and the record now disagree less.

**A17-17 (minor, B11): `pre_mu = 0.35` mislabelled "the 2023+ off-print rate".** — **Accepted.**
Recomputed: 3.5068/yr × 0.55 off-print share × 49/365 = **0.2589**. The base is now the measured 0.26; 0.35 appears in §7 as "the revision-1 judgement" and the all-window 0.47 is added as the upper measured row (0.105).

**A17-18 (minor, B11): `k_post` measured on a window that includes day 1, applied to one that excludes it.** — **Accepted as a specification note, and now tested.**
`b11_model_v2.py` gains `k_post_includes_day1`. Applying the coefficient to `r_day1 + r_post`, the window it was measured on, gives **0.0799** against the base 0.0785. The finding said the direction was ambiguous and the number would not move; with recentring, the level consequence is zero by construction and only the redistribution across branches remains. The specification is now a row in the sensitivity table rather than an open question.

**A17-19 (minor, B11): the −$1.5 direct effect is asserted against the source cited for it.** — **Accepted.**
Claim 9 and §9 now say the measured effect is zero (09 note §1 items 6, 9; Buy share vs forward 3m excess return r 0.128, n 66, p 0.30) and that −$1.5 is a conservative overlay for the one exception in the record. EV −$0.2 and the immaterial verdict are unchanged.

### B12

**A17-09 (major, B12): T5 modelled as mutually exclusive with a numeric floor, against its only historical instance.** — **Accepted on the evidence; rejected on the arithmetic.**
The evidential point is right and is now in claim 2: both glosses (`05_statements.csv` V007 2024-05-30, V011 2024-09-10) post-date the February 2024 letter and describe the T1 floor *in* it, and a standalone explicit-down February sentence is 0 of 5.
The arithmetic does not survive. The finding's proposed fix is "model T5 as a language overlay on T1 (and, at low weight, on T3) rather than an alternative to it". I implemented exactly that in `b12_model_v2.py` — 70% of T5 draws resolve through the T1 numeric floor instead of standing alone — and on F03 revision 2's engine it gives:

```
base                                          literal 0.5086  material 0.3748
T5 as a LANGUAGE OVERLAY on the T1 floor      literal 0.5086  material 0.3741
```

**No change.** A T1 floor is strictly below the print by construction (the haircut is clipped at 0.25pp and then rounded down to the 0.5 grid), so folding T5 into T1 moves nothing under either reading. The finding's **−0.07 literal / −0.08 material** comes from a different change: pushing T5 to 0.02–0.03 and redistributing the mass to **T3 and T6**, which are No regimes. That is a *regime re-weighting*, not an overlay reframing — and it belongs to F03, whose revision-2 regime weights are the run's adopted object, not to B12. The audit's own "what the log does well" section says this log was right not to re-weight F03's regimes for a second opinion on the same five sentences.
What revision 2 does instead: both variants are §7 rows (`T5 mass to T3/T6`: 0.4353 / 0.3024) and they are one of the two named reasons the final is trimmed below the engine.

**A17-10 (major, B12): T2 has never appeared in a February letter and carries the whole literal-vs-material wedge.** — **Accepted.**
Reproduced on the F03 revision-2 engine: T2 halved gives literal **0.4086** / material 0.3410; **T2 = 0 gives 0.3093 / 0.3076** — the two readings coincide, as the audit says. Verified the letter forms independently: the three February numeric sentences are two ~190bp haircuts (FY24, FY25) and a qualitative "stable" (FY26); "at least 35.5%" is the mid-2026 form with **n 0 in February**.
§4 and claim 12 say so; §7 now **leads** with T2 as the headline sensitivity (0.31–0.51 literal, wider than any other assumption in the log); §8 gains a T2 test — any interim FY27 sentence using the "at least X%" form would be the first February-form precedent. The trim from the 0.507 blend to the published 0.49 is principally this.

**A17-11 (major, B12): every F03/F04 figure is revision 1.** — **Accepted.**
Rebuilt `f03_f04_joint_v2.py`: literal **0.5086**, material **0.3748**, realised regime weights {T1 .191, T2 .205, T3 .339, T4 .079, T5 .115, T6 .071}, FY26 print mean **35.8203**, sd 0.4941, **P(< 35.5) 0.1766** — identical to the audit's line. Claims 4, 5 and 8 are rewritten to revision 2 and the "F03's implied B12 0.35" reconciliation is **deleted**: F03 revision 2 computes B12 directly (`conditionals.b12_from_same_draws` = 0.51 / 0.38) and agrees with this log.
The audit is right that this is a citation repair with no headline consequence, and revision 2 turns that into a published result: **0.5086 on the revision-2 print vs 0.5088 on the revision-1 print**, despite P(FY26 < 35.5) doubling from 0.09 to 0.18. The level-insensitivity claim, which revision 1 asserted, is now demonstrated on both print distributions.

**A17-12 (major, B12): the FY27 margin row contradicts its own derivation.** — **Accepted.**
The row is now computed on the same draws rather than hand-cut. Realised FY27 margin given Yes = floor + U(0.6, 1.4) for numeric sentences (the 60–140bp beat record, n 3), print − |N(1.0, 0.5)| for T5:

```
literal Yes    E[floor] 34.83   E[realised FY27 margin] 35.60   vs team 35.7: -0.10pp   vs Street 36.45: -0.85pp
material Yes   E[floor] 34.45   E[realised FY27 margin] 35.25   vs team      : -0.45pp   vs Street      : -1.20pp
```

So the answer is neither revision 1's headline −0.3 nor its parenthetical +0.2: it is **−0.1pp, i.e. flat — a Yes delivers roughly the team's line build.** The −0.9 vs the Street reproduces at −0.85 and is the base the EPS and stock lines use, which the table now says.

**A17-13 (major, B12): −$5 and EV −$2.5 booked as additive with no S03 test.** — **Accepted.**
Verified `abnb_path_mixture_v2.py` `PARAMS.scen[*]["feb"]` = 2.5 / 1.0 / 0.5 / −0.5 with `feb_sd` 9.0, and `abnb_earnings_reactions.csv` 4Q24 +14.4 / 4Q23 −1.7. §9 is split the way B11's is:
- **additive**: the Street's FY27 EBITDA cut at a constant multiple — literal −$135M → **−$3.9/share** (EV −$1.9), material −$189M → **−$5.5/share** (EV −$2.0). Still material either way.
- **non-additive**: the 11 February reaction, owned by S02/S03 revision 2, with the sentence the audit asked for — the day-1 sign is not the sign of the estimate cut, and the Feb 2025 letter cut the floor 190bp and printed **+14.4%**.
The multiple effect revision 1 bolted on ("−0.3 turn ≈ −$3") is part of the repricing, i.e. part of the reaction, i.e. S03's; it is removed from the additive leg rather than kept.

**A17-20 (minor, B12): the reference class is cut at 4Q21 without saying why.** — **Accepted.**
Both 4Q20 sentences extracted verbatim and confirmed: "we will be focused on making continued progress in **expanding** our Adjusted EBITDA margin as we scale" and "we expect our Adjusted EBITDA margins to be **lower in the first half of 2021 than the second half**". New claim 1b adds the row with its exclusion reason and carries **2 of 6 = 0.333 (Laplace 0.375)** alongside 2 of 5. The base rate moves 0.45 → 0.41.

**A17-21 (minor, B12): F04 figures are revision 1.** — **Accepted.**
Claim 8 now cites F04 revision 2's joint unconditional **0.5805** and conditionals a 0.398 / b 0.463 / c 0.564 / **d 0.673** / e 0.531, and notes that F04's published headline stayed 0.55. Not load-bearing, as the finding says.

**A17-22 (minor, B12): "material: 0.38 × −$7" introduces a −$7 that appears nowhere else.** — **Accepted.**
The audit is right that no equivalent calculation existed. It does now, from the same draws: **E[gap | material Yes] = 1.37pp**, median 1.30, p90 2.30, 43% above 1.5pp (the audit's guess of ≈1.4pp was close). On the revision-1 judgement ladder that gap prices at −$7.4, which is where the −$7 came from; on the corrected additive-only convention it prices at **−$5.5**, and the second EV is **0.36 × −$5.5 = −$2.0**.

### B13

**A17-01 (critical, B13): the published 0.26 is computed on a parameter set the run has withdrawn.** — **Accepted in full.**
`adopted_q4_states_v2.json` (A12 revision 2) names this question by id: "B13 bonus-q4-nights-print-weak (batch A17): P(≤131.0m) = 0.309, not 0.26". `b13_model_v2.py` re-implements the object parameter-for-parameter and reproduces it exactly:

```
B13 P(<=131.0m) rebuild 0.3089  vs adopted_q4_states_v2.json 0.3089  (delta 0.0000)
mixture mean 8.6122 sd 2.2782 ; P(>=134.0m) 0.3070 ; middle 0.3841
E[4Q26 | Yes] 5.925 ; E[3Q26 | Yes] 9.091
views: V1 0.4514  V2 0.2585  V3 0.0248
```

`final.p` = **0.31**, CI **0.19–0.43**. §§5–8 rewritten against the object.

**A17-02 (critical, B13): the "one 4Q26 object" claim was false when written.** — **Accepted in full.**
Reproduced: the revision-1 mixture's own mean is **8.789** with middle mass **0.432** and P(≥134.0m) 0.3054 — not "0.26 / 0.47 / 0.27, mean ≈ 8.3". The 0.47 was 1 − 0.26 − 0.27 on two headlines from two different blends (R16 revision 1 hand-cut 0.3032 → 0.27; B13 used its own 0.2622 raw). §§5–6 now quote the adopted object's computed triple **0.309 / 0.384 / 0.307, mean 8.61, sd 2.28** with the percentile table, and §4 carries a row recording the failure.

**A17-14 (major, B13): the brief's coefficient used two incompatible ways in one table.** — **Accepted in full.**
Identity check reproduced: Street FY27 revenue 15,829 at 36.45%; a −158 revenue delta with costs held gives 35.81% = −0.64pp (the brief's 0.66); solving the flex 0.42pp back out gives ΔE/ΔR = **0.78**, not 0.66. §9 states one convention — **held costs, ΔEBITDA = ΔR** — and gives the flex alternative at 78%. FY27 EPS −$0.20 → **−$0.34** (flex −$0.26). The correction runs toward the short case.

**A17-15 (major, B13): the 3Q26 row is wrong and reverse-causal.** — **Accepted in full.**
`conditional_means_pct.q3_given_le_131_0m` = 9.091 against R01 revision 2's centre 9.50 → **−0.41pt**, not −0.9 against a 9.9 centre no adopted object carries. The row is labelled **"(indirect: selection, not impact)"** with the timing stated — 3Q26 prints 5 Nov 2026, this resolves ~11 Feb 2027 — the way B11 §9 labels its own indirect rows.

**A17-16 (major, B13): the three "independent estimates" are not three estimates, and one is not the number used.** — **Accepted in full.**
Reproduced: 0.5 × 0.4211 + 0.3 × 0.1558 + 0.2 × 0.0245 = **0.2622**, the published blend — while §5 published `base_rate_estimate` 0.18. §5 now opens by saying these are the three legs of one blend and that **no independent anchor exists**, and quotes the adopted object's own views with no hand-cut: V1 **0.4514**, V2 **0.2585**, V3 **0.0248**.

**A17-23 (minor, B13): two anchors in one block, and the gap measured off the unused one.** — **Accepted in full.**
**One anchor: 0.02**, the raw Bloomberg dispersion, which is also how R16 revision 2 treats the same object (it anchors on the bar's upper tail, 0.51). The gap-adjusted 0.05 is deleted; `final_minus_anchor` = **+0.29** with `anchor_independent: false`.

**A17-24 (minor, B13): the two stock components are one move.** — **Accepted**, with a coherence flag the audit did not raise (see §3).
The brief's sensitivity line says "$4.90/share (joint solve) **or** $1.50 (fixed multiple)" — alternatives. The joint solve is the post-repricing level and the February reaction is the market arriving at it. **−$7.5** (1.53pt × $4.90), EV **−$2.3**.

**A17-25 (minor, B13): V3 is the Street's dispersion, not a forecast.** — **Accepted as a stated caveat.**
Claim 6 now says so and quantifies it: a forecast-shaped V3 built from the measured at-print record (+0.9%, sd 1.5%, ≥ 0 in 10 of 12) would be ≈ N(135.2m, 2.0m) → P(≤131.0m) ≈ 0.02, essentially V3's own 0.0248. Re-centring V3 that way moves the blend 0.3089 → **0.3078**. The weight is kept, as the audit recommends.

**A17's one substantive disagreement — the V2 cushion (it would use 1.5–2.0 and land at 0.30).** — **Noted, not adopted, and written down.**
The case is real: 4 of 4 Q4 nights guides met, bucket-era beats +4.8 and +1.15. Cushion 1.5 gives **0.289** and 2.0 gives **0.272**. Against it: the directional-era record is a mean of **−0.2** on five stable guides, and the cushion is a single parameter of the run's *adopted* object, settled at 1.0 in A12 revision 2 after F01 revision 2 had used 0.9 and R16 revision 1 had hand-cut to the equivalent of 0.78. Moving it here would un-adopt the object and hand X01 two 4Q26 distributions. The audit's own instruction is "adopt 0.31 for coherence and note the one-point trim I would take"; §4 of the B13 log is that note.

## 3. What the audit missed

1. **A17-09's fix does not produce A17-09's number.** The finding asks for T5 to be modelled as a language overlay on the numeric floor and books that reframing at −0.07 literal / −0.08 material. Implemented as written it is worth **+0.000 / −0.001**, because a T1 floor is below the print by construction. The −0.07 belongs to a different change — moving T5's mass into T3/T6 — which is a regime re-weighting the audit elsewhere praises this log for not doing. This is the single largest correction going back the other way, and it is why B12's literal reading lands at 0.49 rather than 0.44.
2. **A17-04's independent number does not apply A17-04's own first-choice fix.** The finding offers two remedies — re-centre, or state the 1.6× overrun and why. Its corrected band (0.12–0.14) and final (0.13) take neither; they re-set the *levels* and let the modulations lift them again. Applying the recentring the finding asked for is worth about −0.03 and is the whole difference between 0.13 and this response's 0.11.
3. **The audit's own A17-24 recommendation breaks the R16/B13 mirror, and the audit read R16 revision 2 for coherence without saying so.** R16 revision 2 books **+$11 = 1.8pt × $4.90 (joint solve) *plus* ≈ $4 of February reaction** and an EV of +$3.4. A17-24 tells B13 not to add the reaction. Both cannot be right, and the pair is the memo's headline symmetry. B13 revision 2 publishes the joint-solve-only −$7.5 (the defensible one) **and** records that on R16's convention the mirror is −$10.5 / EV −$3.3 — the exact mirror of R16's +$3.4. **X01 must pick one convention before the memo freezes**; this is now an open item in both B13's §9 and its RESUME.
4. **B13's FY27 persistence asymmetry is unexamined.** B13 uses 70% persistence where R16 uses 60%, and the audit recomputed the FY27 lines at 70% without asking whether the asymmetry is justified. It is — a lap-plus-cancellation level effect carries while an upside surprise is more likely a pull-forward — but revision 1 never said so and the audit never asked. §9 now states it.
5. **B12's operating delta against the team is −0.1pp, not 0.0 or +0.2.** A17-12 proposed "book 0.0 / +0.2pp vs the team", taking the +0.2 from revision 1's own hand-cut parenthetical. Computed on the engine over all literal-Yes draws, E[realised FY27 margin | Yes] is **35.60** against the line build's 35.7, i.e. **−0.10pp**. The audit's fix improved a wrong number with another approximate one.
6. **B11's December marker deepens rather than shrinks.** A17-05 computes −$14.8 on revision-2 parameters with revision-1 counts. On the corrected count model it is **−$15.8**: recentring changes which paths reach three downgrades and concentrates the Yes set further in the decel-below branch.
7. **The two B12 readings agree on EV to within a dime.** Literal 0.49 × −$3.9 = −$1.9; material 0.36 × −$5.5 = −$2.0. A 13-point disagreement about *P* produces a one-dime disagreement about *money*, because the material subset carries a wider gap (1.37pp vs 0.99pp). Neither the log nor the audit noticed, and it is the fact that makes the reading ambiguity immaterial to the memo — which is worth more to the deck than either probability.
8. **The 4Q20 comparison is undefined, not merely excludable.** A17-20 offers the row as a possible No. It is a No, but FY20's adjusted EBITDA margin was negative (−$251M on $3.38bn), so "a FY21 floor below the FY20 actual" has no content at all, and the second sentence the finding quotes is intra-year seasonality rather than a full-year guide. Claim 1b says both.
9. **A17-18 was left as an untested note.** It is now a sensitivity row: applying `k_post` to `r_day1 + r_post` gives **0.0799** against the base 0.0785. With recentring the level consequence is zero by construction, so the specification question is closed rather than open.

## 4. Reproduction

`A17-reproduce.py` saved verbatim from the audit (no path bugs; `ROOT = Path.cwd()` and it is run from the repository root as documented). `py -3.13 -B docs/pitch-forecasts/audits/A17-reproduce.py`, exit code 0, ~3 minutes.

```
========== B11  the downgrade feed and every base rate in claims 2-4 ==========
feed pull rows 469, action mix {'main': 350, 'init': 38, 'reit': 35, 'up': 26, 'down': 20}
down rows 20, all to Hold/Sell True, by year {2021: 2, 2022: 5, 2023: 6, 2024: 5, 2025: 2}
last downgrade 2025-05-30 -> 474 days to 2026-09-16; largest earlier gap 345 days
same-calendar 17 Sep - 15 Dec: {2021: 0, 2022: 2, 2023: 5, 2024: 1, 2025: 0}
  90-day windows 2021+  n 1995  mean 0.8596  P(>=3) 0.1063  P(>=2) 0.2386  max 5
  90-day windows 2023+  n 1265  mean 0.8735  P(>=3) 0.0822  P(>=2) 0.2277  max 5
  90-day windows 2024+  n  900  mean 0.6500  P(>=3) 0.0056  P(>=2) 0.1922  max 3
  print-shaped (-49/+39d) counts [0, 0, 0, 0, 3, 0, 0, 2, 1, 0, 0, 4, 1, 2, 1, 1, 0, 2, 0, 0, 0, 0, 0]
  all n 23 mean 0.7391 P(>=3) 0.0870 | 2023+ n 15 mean 0.800 P(>=3) 0.0667
  by day-1 sign: {'up>=5': 'n 6 mean 0.167 P(>=3) 0.000', 'small': 'n 11 mean 0.909 P(>=3) 0.182', 'down<=-5': 'n 6 mean 1.000 P(>=3) 0.000'}
  NOTE: both >=3 windows (Feb 2022, Nov 2023) followed SMALL day-1 moves (+3.6, -3.3);
        0 of 6 windows around a day-1 <= -5pct print ever reached 3 - the model's mechanism has no positive case

========== B11  published model, the revision-2 parameter swap, and the two corrections ==========
  S02 revision-2 within-branch day-1 sd from the variance identity: 8.451 (S02 v2 solves 8.451)
  published (S02 revision 1, capture 0.85)             P 0.1550  mean 1.173 (= 4.81/yr)  E[Dec|Yes] 147.9 vs 161.1
  no modulation at all (k_pre = k_post = beta = 0)     P 0.1075  mean 0.938 (= 3.85/yr)  E[Dec|Yes] 157.6 vs 161.3
  S02 revision-2 parameters                            P 0.1408  mean 1.096 (= 4.50/yr)  E[Dec|Yes] 150.5 vs 165.5
  rev2 + capture 1.0 (base rates are ALREADY feed counts) P 0.1792  mean 1.293 (= 5.30/yr)  E[Dec|Yes] 152.0 vs 165.5
  rev2 + feed print-window post means .02/.55/.55/.83  P 0.1064  mean 0.896 (= 3.68/yr)  E[Dec|Yes] 150.7 vs 165.6
  rev2 + capture 1.0 + feed post means                 P 0.1374  mean 1.058 (= 4.34/yr)  E[Dec|Yes] 152.1 vs 165.6
  rev2 + pre 0.26 (2023+ OFF-print 49-day rate)        P 0.1271  mean 1.010 (= 4.14/yr)  E[Dec|Yes] 149.5 vs 165.4
  rev2 + capture 1.0 + pre 0.26 + feed post means      P 0.1207  mean 0.956 (= 3.92/yr)  E[Dec|Yes] 150.4 vs 165.5
  the file's numpy run (b11_summary.json): P 0.15393 mean 1.169 E[Dec|Yes] 148.05 vs 161.11
  measured rates: 3.51/yr (2021+), 3.51 (2023+), 2.59 (2024+), 0 trailing 12m;
  print-shaped-window mean 0.74 per 89 days = 3.03/yr

========== B12  the five February letters and the literal / material record ==========
  4Q21 2022-02-15  prior 26.57  floor_vs_prior +0 bp  literal No material No  [qualitative_flat]
  4Q22 2023-02-14  prior 34.56  floor_vs_prior +0 bp  literal No material No  [qualitative_flat]
  4Q23 2024-02-13  prior 36.84  floor_vs_prior -184 bp  literal Yes material Yes  [numeric_floor_haircut]
  4Q24 2025-02-13  prior 36.40  floor_vs_prior -190 bp  literal Yes material Yes  [numeric_floor_haircut_with_named_investment]
  4Q25 2026-02-12  prior 35.10  floor_vs_prior +0 bp  literal No material No  [qualitative_flat]
  literal 2 of 5 = 0.400 (Laplace 0.429); a numeric floor given at all 2 of 5; explicit 'down' 0 of 5 (Laplace 0.143)
  NOTE the 4Q20 (Feb 2021) letter also carries a forward FY margin sentence - 'focused on ... expanding our
  Adjusted EBITDA margin as we scale' - so the reference class can be read as 2 of 6 = 0.333

========== B12  published model, and what the T5 and T2 regimes are doing ==========
  published rebuild: literal 0.5181 material 0.3890 T2-as-flat 0.3002 gap mean 1.03 p50 0.70 p90 2.10 share<50bp 0.25
  the file's numpy run: literal 0.517 material 0.388 t2-as-flat 0.299 gap mean 1.04 p50 0.7 p90 2.1 share 0.25
  F03 rev-2 FY26 print N(35.72,0.58), 50pct defence              literal 0.5183  material 0.3878
  F03 rev-2 realised regime weights (T1 .20 T2 .20 T3 .33 T4 .08 T5 .12 T6 .07) literal 0.5176  material 0.4004
  T5 as a LANGUAGE OVERLAY on T1, not a separate regime (T5 0.02) literal 0.4377  material 0.3085
  T2 halved to 0.11 (no February letter has ever used that form) literal 0.4089  material 0.3449
  T2 = 0                                                         literal 0.3004  material 0.3004
  the whole literal-vs-material wedge is T2: at T2 = 0 the two readings coincide.
  F03 revision 2's own joint model (f03_f04_joint_v2.py, A08 response) publishes literal 0.5086 / material 0.3748.

========== B13  the published blend, its mean, and the ADOPTED 4Q26 object ==========
  thresholds: <=131.0m = 7.4651 pct y/y ; >=134.0m = 9.9262 pct y/y
  revision-1 parameters (the published B13): V1 0.4225  V2 0.1568  V3 0.0240  ->  blend P(<=131.0m) 0.2628
    file: V1 0.4211  V2 0.1558  V3 0.0245  blend 0.2622 -> published 0.26
    BLEND MEAN 8.789, sd 2.090  <-- the log's sections 3 and 5 assert 'mean ~ 8.3'
    blend P(>=134.0m) 0.3054 -> middle mass 0.4317, not the log's 0.47
  ADOPTED object (adopted_q4_states_v2.json, R16 rev 2): V1 0.4528  V2 0.2574  V3 0.0240  -> P(<=131.0m) 0.3074
    file: V1 0.4514  V2 0.2585  V3 0.0248  blend 0.3089  mean 8.6122  sd 2.2782
    my rebuild mean 8.614 sd 2.276 ; E[Q4|Yes] 5.922 (file 5.925) ; E[Q3|Yes] 9.091 (file 9.091) ; E[Q3] 9.494
    cushion 1.5                      P(<=131.0m) 0.2881
    cushion 2.0                      P(<=131.0m) 0.2720
    Q4 centre 7.61 (RNPL module)     P(<=131.0m) 0.3474
    Q4 centre 8.9 (case A)           P(<=131.0m) 0.2470
    blend 0.4/0.4/0.2                P(<=131.0m) 0.2873
    equal thirds                     P(<=131.0m) 0.2441

========== B13  the section-9 impact arithmetic on the adopted object ==========
  4Q26 nights  -2.18 pt   (log: -2.0)
  3Q26 nights  -0.41 pt   (log: -0.9, measured against 9.9 rather than R01 revision 2's 9.5)
  4Q26 revenue -65 M    (log: -60)   [1pt = $30M]
  FY27 revenue -241 M    (log: -220)  [70pct persistence x $158M/pt]
  FY27 margin  -1.01 pp   (log: -0.92) [0.66pp per pt, HELD costs]
  FY27 EPS held-cost -0.337  flex-cost -0.263   (log: -0.20, from $220M x 0.66 x $0.0014)
  the log books the HELD margin coefficient (0.66pp/pt) and a 66pct dollar flow-through in the same table;
  held costs = 100pct flow-through; the brief's flex case solves to 78pct. Either way the EPS line is understated.
  stock, joint solve -7.47  (log: -6.9 on 1.4pt); the -$3 February reaction is that same repricing, not an addition
```

The script reproduces every figure it claims to, within the ±0.005 Monte-Carlo tolerance it states. Two small notes for the record: its stdlib B12 rebuild of the *published* revision-1 model returns 0.5181 against the file's 0.517 (inside tolerance), and its "T5 as a language overlay" row is labelled as an overlay but implemented as a re-weighting to T3/T6 — the discrepancy §3 item 1 is about.

### This response's own runs

```
b11_model_v2.py   base (S02 v2, recentred, pre 0.26, post .085/.525/.625/.965, capture 0.85)
                  P 0.0785  mean 0.726 (2.98/yr)  P>=2 0.178  decel-below 0.127  accel 0.017
                  recentring scales: pre 1.120, post 1.323 / 1.302 / 1.300 / 1.315
                  capture 1.0 0.1021 | +entry-state lift 0.1097 | bridge to revision 1 0.1539
                  E[15 Dec | Yes] 149.65 vs 165.46 uncond (median 147.08 vs 163.07)

b12_model_v2.py   literal 0.5086  material 0.3748  (F03 revision 2 publishes 0.51 / 0.38)
                  T5 as a LANGUAGE OVERLAY on T1 (70% of T5):  literal 0.5086  material 0.3741   <- no change
                  T5 mass moved to T3/T6 (the audit's arithmetic): literal 0.4353  material 0.3024
                  T2 halved 0.4086 / 0.3410 ; T2 = 0  0.3093 / 0.3076
                  gap | literal Yes  mean 0.99 p50 0.60 p90 2.20  <50bp 0.340
                  gap | MATERIAL Yes mean 1.37 p50 1.30 p90 2.30  >150bp 0.426
                  literal:  E[realised FY27] 35.60  vs team -0.10pp  vs Street -0.85pp  dEBITDA -135  EPS -0.189  stock -3.92
                  material: E[realised FY27] 35.25  vs team -0.45pp  vs Street -1.20pp  dEBITDA -189  EPS -0.265  stock -5.50

b13_model_v2.py   P(<=131.0m) rebuild 0.3089 vs adopted_q4_states_v2.json 0.3089 (delta 0.0000)
                  mean 8.6122 sd 2.2782 ; P(>=134.0m) 0.3070 ; middle 0.3841
                  E[4Q26|Yes] 5.925 ; E[3Q26|Yes] 9.091 ; views V1 0.4514 V2 0.2585 V3 0.0248
                  Q3 ladder 0.384 / 0.307 / 0.271 / 0.217 ; bucket ladder 0.001 / 0.006 / 0.126 / 0.652
```

## 5. Final table

| question | revision 1 | auditor | revision 2 | anchor | \|final − anchor\| | EV $/share | material |
|---|---:|---:|---:|---:|---:|---:|---|
| **B11** sell-side downgrades ≥3 by 15 Dec | 0.14 | 0.13 | **0.11** | 0.09 † | 0.02 | **−0.2** direct (−1.7 as a non-additive branch marker) | **no** |
| **B12** FY27 margin guided down — *literal* | 0.50 | 0.47 | **0.49** | 0.65 † | 0.16 | **−1.9** | **yes** |
| **B12** FY27 margin guided down — *material* | 0.38 | 0.36 | **0.36** | 0.60 † | 0.24 | **−2.0** | **yes** |
| **B13** 4Q26 nights ≤ 131.0m | 0.26 | 0.30 | **0.31** | 0.02 † | 0.29 | **−2.3** (−3.3 on R16's additive stock convention) | **yes** |

† `anchor_independent: false` in all four rows. B11's anchor is one of its own base-rate families; B12's is the WS05 repo prior F03 also anchors on, with no qualitative February in its n-3 sample; B13's is V3, which carries 0.2 of the blend it is being compared with. No tradable market prices any of the three (Kalshi and Polymarket scanned 2026-09-17T08:27:05Z).

No revision-2 number differs from the auditor's by more than 5 points, so no asymmetry justification is owed under the response rule. The three differences and their reasons, all written into the logs: **B11 −0.02** (the recentring the audit proposed and did not apply); **B12 literal +0.02** (weight on F03 revision 2's own B12 draws for run coherence, since the audit's structural correction does not reproduce); **B13 +0.01** (the V2 cushion, where the audit itself said to adopt 0.31 for coherence and note its trim).
