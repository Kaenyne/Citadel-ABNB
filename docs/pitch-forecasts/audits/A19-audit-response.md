# Response to audit A19 (X01, scenario-probabilities)

Response date: 2026-09-17
Responds to: `A19-research-audit.md` (independent Opus audit, read-only; Codex fallback per `00_BRIEF.md` orchestration)
Revised research: `questions/scenario-probabilities/research-log.md` (revision 2)
Revised forecast: `questions/scenario-probabilities/forecasts/2026-09-17-forecast.json` (revision 2)
New dataset script: `questions/scenario-probabilities/datasets/x01_reclassify_v2.py` → `x01_v2_summary.json` (revision-1 `x01_joint.py` and its five outputs left untouched as the audit trail)
Reproduction script: `A19-reproduce.py` (the audit's script, saved verbatim; output `A19-reproduce.stdout.txt`, reprinted at the end of this file)

## Summary

Eighteen findings. **Eighteen accepted** (one, A19-03, accepted with a correction that strengthens it); none rejected. Every number in the audit reproduces. The audit's stdlib quadrature ran clean from the repo root on `py -3.13` with no path change and no edits — the only fix needed was stripping the closing markdown fence when extracting it from the audit file. The 1,000,000-draw replay of `x01_joint.py` was re-run in place (seed 20260917, exit 0) and reclassified under every gate, reading and precedence variant the audit names; the published vector, every marginal check, the scenario table, the compositions, the base-rate panel and all 27 sensitivity rows replay exactly, and the audit's quadrature lands within 0.0007 of every cell of every variant.

The audit's first required change was the base option's gate. Revision 1 coded it as "print < 10.6%", which is the *thesis-breaker* threshold; the question says "base (**decelerating print** …)" and gives "in-line print with in-line guide" as its example of **none**. Correcting the gate to S01's dead-band decel line (latent < 10.09) moves 0.0514 of probability out of base and into none.

Headline, revision 1 → revision 2 (literal reading, breaker-first precedence):

| | breaker | base | short | none |
|---|---:|---:|---:|---:|
| revision 1 | 0.14 | **0.22** | 0.55 | **0.09** |
| revision 2 | 0.14 | **0.17** | 0.55 | **0.14** |

The joint itself did not move and was not re-fitted: `x01_joint.py` is byte-identical to revision 1. What moved is the classification over the identical draws, plus four things the audit was right to attack in the write-up rather than the model: the phantom citation behind the headline reading (now defended from the question text, with the clause that argues against it stated), the anchor (now `null` / `NO_EXTERNAL_ANCHOR`, and no |final − anchor| goes to SYNTHESIS), the "base = short on the day" read (withdrawn — under the corrected gate it reverses), and the instruction to delete the memo's 25/45/30 (withdrawn — as a *print partition* it reproduces at 0.26 / 0.45 / 0.29).

The two objects the memo must now carry, labelled:

1. **Print partition** (12-month scenario column, print gate only): **0.26 breaker (≥10.6%) / 0.45 base (8.5–10.6%) / 0.29 short (≤8.5%)**, with monotone conditionals — day-1 +2.1% / −3.8% / −4.8%, 15 Dec median $175.0 / $162.2 / $159.6 (mean $177.6 / $164.6 / $162.0, p25 $155.9 / $144.3 / $142.1). This is the memo's existing row: keep it, relabel it.
2. **Disclosure gates** (5 Nov, X01 proper): **0.14 / 0.17 / 0.55 / 0.14**, literal reading named in the header, material reading 0.14 / 0.20 / 0.48 / 0.18 available, with the composition footnote (0.34 of the short case is a directional "moderate" word; 0.199 of its draws sit on a print ≥10.0%).

## Finding-by-finding

### A19-01 (critical) — base gated at the breaker threshold: accepted
Reproduced on the identical draws. At the S01 decel line (x < 10.09) the vector is **0.1394 / 0.1717 / 0.5547 / 0.1342**; at a strict "below 2Q26's 10.34" line 0.1394 / 0.1985 / 0.5547 / 0.1074; the audit's quadrature gives 0.1398 / 0.1720 / 0.5540 / 0.1343. The dead band (mass 0.1034) splits 0.497 base / 0.428 short / 0.075 none under revision 1's gate and 0.428 short / 0.572 none under the corrected one; total probability reclassified base → none is **0.0514**, matching the audit's 0.051.
Fix: convention 4 rewritten to gate base on a decelerating print; convention 5 rewritten to say what "none" now contains; the gate is now the **first** row of §7 (base 0.17 → 0.22 / 0.20 / 0.21 across the four gate readings; none 0.14 → 0.08 / 0.11 / 0.10), which makes it the largest definitional swing in the table, as the audit said it should be. The classification is reproducible from `x01_reclassify_v2.py`.

### A19-02 (critical) — the headline reading cited a document that does not exist: accepted
Confirmed: the only brief text about X01 is `00_BRIEF.md:176`, which says nothing about option-level gates. The orchestrator's launch prompt has since been saved to `prompts/forecast_A19.md` (claim 10) — it does fix the legs at the option level, so the citation was not invented, but it carries no argument, and its parenthetical "(<10.6%)" for "decelerating print" is precisely the source of A19-01. A pitch cannot rest its headline scenario probability on it either way.
Fix: convention 3 now defends the literal reading from the registered text, in the audit's four steps — the three phrases are verbatim C02 option labels; the fine print requires coherence with C02, which resolves at the option level; the registry's own header convention defines bucket language as the qualitative descriptor, which covers a directional sentence; and (a)/(b)/(c) are applied whole, so splitting only (d) would be asymmetric — **with the argument against stated in the same paragraph**: C02 (d)'s second clause is expressly "without a bucket" while X01 calls the object a "bucket". Both vectors are in the §6 table and the memo is told to name the reading in the table header. The C04 (d) map ("approximately 35.5%" removes the floor) needs no interpretation and is stated as exact.

### A19-03 (major) — "base = short on the day" is an artefact and reverses: accepted, with one correction to the audit
Reproduced. Published gate: base day-1 median −3.76 / short −3.80, 15 Dec $162.3 / $161.9. Corrected gate: base **−4.66** vs short **−3.80**, 15 Dec **$160.6** vs **$161.9**, P(≤−8%) **0.356** vs 0.327, P(<0) 0.695 vs 0.659. Cause confirmed: a corrected base cell is 100% decelerating prints, while the short-case cell is 10.2% accelerating-state draws.
**Correction:** the audit's companion figure — "a tenth of it sits on an accelerating print" — repeats revision 1's ambiguous wording. 0.110 is unconditional **mass**; conditional on the short case the share with a print ≥10.0% is **0.199**, one draw in five. That strengthens the finding, so it is published in the conditional form in §6, in `short_case_composition.print_ge_10_0_share_of_short`, and in the scenario table's `read`.
Fix: the sentence is replaced by the audit's accurate one — the option labelled "short case" is not the bad-print option; a third of its mass is a directional word and a fifth of its draws sit on a print of ≥10.0%, so it carries no more day-1 downside than the base case and under the corrected gate slightly less. The conclusion the memo keeps: $115–130 is a 12-month fundamental target, not a reaction-function output.

### A19-04 (major) — the memo's 25/45/30 is a print partition, not a disclosure-gate table: accepted
Reproduced: under N(9.5, 1.70), P(≤8.5%) **0.2881**, P(8.5–10.6%) **0.4514**, P(≥10.6%) **0.2605** → **0.26 / 0.45 / 0.29** against the memo's 25 / 45 / 30. The breaker bound also reproduces: 0.25 requires P(a | ≥10.6) = **0.960** against the joint's 0.535 and a 1-of-6 historical rate on accelerating prints, and even at the adopted file's own top centre (10.3) the language-conditioned breaker is 0.166 — so 0.25 is indeed unreachable *on X01's definition*, and perfectly reachable on the print partition.
Fix: the "replace 25/45/30" instruction is withdrawn from §4, §6, §8 and the JSON. The print-partition table is computed and published as its own object with monotone conditionals (day-1 +2.1 / −3.8 / −4.8; 15 Dec median $175.0 / $162.2 / $159.6, mean $177.6 / $164.6 / $162.0, p25 $155.9 / $144.3 / $142.1, P(≤$150) 0.18 / 0.33 / 0.36), and convention 8 states that it is the 12-month object while X01's vector is the 5 Nov disclosure-gate object. The memo's conjunctive short-scenario mass is published at **0.0462** — and, for symmetry (see "what the audit missed"), its conjunctive breaker at **0.0496**.

### A19-05 (major) — the three estimates are not independent and the anchor is not an anchor: accepted
Reproduced: C02's blend weights are decomposition 0.5 / base_rate 0.3 / anchor 0.2 with `base_rate_vector.d` = 0.39 from the same 17 descriptors the X01 panel reads, and the X01 panel's short cell trips on `descriptor_option == "d"` in 8 of 16 rows. The joint is IPF-fitted to reproduce C02's final vector exactly, so the "agreement" between the W2 base rate and the joint on the short cell is the same evidence twice.
Fix: `anchor: null`, `anchor_flag: NO_EXTERNAL_ANCHOR`, `final_minus_anchor: null`; §5 says in terms that SYNTHESIS must carry no |final − anchor| row for X01 (A12-22 precedent) and that the memo table is a labelled internal comparison (claim 7). `NOT_INDEPENDENTLY_DERIVED` is flagged for the base-rate/decomposition pair with the mechanism spelled out.

### A19-06 (major) — the deceleration-depth statistic is window-inconsistent: accepted
Reproduced: the four ≥1.8-pt decelerations average **+1.75%** raw and are carried by 4Q22 **+13.4%**, a print outside both W1 and W2; the three W1 members average **−2.13%**. The better evidence reproduces too: decelerators only, **W1 n 9 slope −1.24 corr −0.620; W2 n 6 slope −1.62 corr −0.586**; across all prints W1 slope +1.01 corr 0.337 and W2 +2.49 corr 0.587.
Fix: claim 9 is new and carries the two-window regression; §6's read cites it instead of the four-observation mean. The regression makes the same point in both windows and survives the repo's two-window rule.

### A19-07 (major) — precedence defended with a return statistic: accepted
Reproduced: breaker-first 0.1394 / 0.2231 / 0.5547 / 0.0828, short-first 0.1068 / 0.2231 / 0.5873 / 0.0828 (overlap 0.0326); under the corrected gate, short-first is 0.1068 / 0.1717 / 0.5873 / 0.1342.
Fix: convention 6 now states that neither the question text nor any repo document settles precedence, withdraws the return-statistic defence, publishes the breaker as **0.11–0.14** across the two rules, and tells the memo to use short-first if it keeps its own breaker column — because that column requires an FY sentence at "approximately 36%" (C04 (b)), so the overlap draw (a breaker print with a softened floor) is not a memo breaker.

### A19-08 (major) — the probability-weighted close mixes medians: accepted
Reproduced: Σ P × conditional **mean** = **$167.28**, equal to the joint's unconditional mean $167.24; Σ P × conditional median = $164.76; the unconditional median is $164.66.
Fix: `pw_15dec` publishes both with `memo_should_use: mean_convention_usd (167.3)`. The reason is in the log and the JSON: medians do not mix, and the memo's own probability-weighted price (~$146) is built from scenario **range midpoints**, a mean-type convention — two conventions inside one document is the failure to avoid. If the memo prefers $164.8 it must be labelled `pw_dec15_median_of_branches`.

### A19-09 (minor) — the memo-conjunctive mass does not reproduce: accepted
Reproduced on the same draws: P(≤8.5% **and** C02 (d) **and** C04 (d)) = **0.0462** (s.e. 0.0002), not 0.050; the companion P(≤8.5% and (C02 (d) or C04 (d))) = **0.1937** against the published 0.194. Published as 0.046 in §4, §6 and `memo_conjunctive_short_mass`.

### A19-10 (minor) — the material reading's explicit-bucket share is a free parameter: accepted
Reproduced from C02's conditioning block: directional-moderate mass per branch (mass x P(directional) x P(moderate | directional)) = 0.0911 (<9) / 0.0386 (9–10) / 0.0582 (≥10), total 0.188 against C02's published 0.19 sub-split, over branch (d) conditionals 0.517 / 0.258 / 0.174 → explicit shares **0.492 (<9) / 0.348 (9–10) / 0.208 (≥10)**. Implementing them moves the material short case 0.4862 → **0.4783** and none 0.1705 → 0.1784 at the corrected gate (0.4862 → 0.4789 and 0.1119 → 0.1174 at the published gate, matching the audit).
Fix: implemented in `x01_reclassify_v2.py`; claim 3 carries the derivation, so the reader can see the share is in C02's own table and not chosen here.

### A19-11 (minor) — prose said 26 sessions, the code said 62: accepted
Confirmed at `abnb_path_mixture_v2.py:28` (36 pre + 26 post) and in the code's `S02_WITHIN_LOGSD` (0.171). The code is right for a branch-conditional spread: knowing the print branch does not resolve pre-print diffusion.
Fix: claim 6 and §6 item 5 say 62, and the audit's suggested check is added to §6 — X01's unconditional 15 Dec percentiles **123.3 / 131.4 / 146.2 / 164.7 / 185.4 / 206.4 / 220.0** against S02's published 120.5 / 129.4 / 145.5 / 165.6 / 186.0 / 206.5 / 221.0, P(≤150) 0.298 vs 0.30, P(≤143) 0.212 vs 0.22.

### A19-12 (minor) — day-1 and 15 Dec are independent given the branch: accepted
Confirmed by reading the code and now quantified: corr(day-1, log 15 Dec) = **0.063** unconditionally and **0.003 / −0.000 / −0.001** within the decel / flat / accel states — all of the dependence in this file is branch mixing.
Fix: §6 item 6 and `joint_structure.dependence_not_modelled` state it and forbid any day-1 × 15 Dec joint statement from this file; the 2026-11-06/12-15 monitoring row repeats the prohibition. The draws are not correlated by hand: imposing a shared shock would be a new, unvalidated parameter, and the per-option marginals the memo needs are unaffected.

### A19-13 (minor) — the base rate's nights gate is a sequential analogue and is not robust to it: accepted
Reproduced: on the level gate (`nights_yoy ≤ 8.5`) W2 literal is 0.10/0.10/0.60/0.20 and W2 material 0.10/0.20/0.40/0.30, against the sequential-gate W2 literal 0.10/0.10/0.50/0.30 (all at the corrected base gate).
Fix: §5 publishes the base rate as a **range** — short 0.50–0.60 literal, 0.30–0.40 material — names the analogue, and says that the rank order (short modal under the literal reading, not under the material one) is what survives. That is the honest claim.

### A19-14 (minor) — the C04 leg has no precedent and gets one clause: accepted
Reproduced: `fy_margin_action` is never lowered/softened in 16 prints, and the three November prints carrying an FY margin sentence (3Q23, 3Q24, 3Q25) all read **raised** (3Q22 is "none"). Dropping the C04 leg takes short **0.5547 → 0.4437** (base → 0.2378 at the corrected gate; 0.3094 at the published gate, matching the audit); C04 (d) at 0.20 takes short to 0.53.
Fix: claim 8 carries "0 of 16 ever softened; 3 of 3 Novembers raised"; §5's closing paragraph says out loud that 0.55 is a **wording bet**, with both the −0.11 gate-removal figure and the reassuring bounded effect (−0.02 at C04 (d) = 0.20) in §7.

### A19-15 (minor) — the C01 tilt is stated in the wrong units and its validation is missing: accepted
Reproduced: ⅔ × 25.88 / (⅔ × 25.88 + ⅓ × 27.20) = **0.6556** (% of guide per 1% of GBV) → **0.599** per point of nights growth at a 9.5% base. Validation reproduced: the joint gives P(below | x ≥ 10.6) = 0.567 against C01's own "0.55 at $26.6bn" and P(below | x < 10.0) = 0.795 against "0.78 at $25.9bn".
Fix: claim 2 states the unit correctly and §6 item 2 carries the C01 monitoring comparison as the reason the steeper slope is used and S01's 0.32 is the outlier. Immaterial to the vector (§7: no option moves by more than 0.001).

### A19-16 (minor) — two day-1 objects will reach SYNTHESIS: accepted, and extended
Confirmed: X01's unconditional day-1 is S01 **rebased** onto the adopted print states, while S01's published −2.1 / 0.27 / 0.22 is not. Extension: revision 1 published the rebased median as −2.4, but the model's own output file (`x01_joint_summary.json`) says **−2.50** — a transcription slip the audit endorsed as exact. Corrected to −2.50 (mean −2.16, P(≤−8) 0.282, P(≥+5) 0.214), together with the unconditional 15 Dec mean (**167.2**, not 167.3).
Fix: §6 and `marginal_checks.unconditional_day1` name the object and its provenance; the RESUME paragraph makes clearing the S01 rebasing the next agent's one open dependency, so SYNTHESIS does not carry two day-1 numbers for the same event.

### A19-17 (minor) — "8 of 17" conflates the option with the sub-branch: accepted
Reproduced: 8 of the 17 descriptors resolve (d); of those, **7 are directional and 1 is a bucket** (3Q25's explicit 4–6% for 4Q25).
Fix: claim 8 and §5 now read "8 of 17 descriptors resolve (d); 7 of those 8 were directional, and only once in 17 did the letter name a mid-single-digit bucket" — the second half being the strongest argument *for* the material reading, which revision 1 omitted.

### A19-18 (minor) — the market cross-reference was skipped and a sibling's table filled the anchor slot: accepted
Fix: §2 line 16 discloses the skip and follows it through — the anchor stays **null** rather than being filled with the Kalshi KXABNB ladder, because that ladder prices the print leg only and is already inside R01's adopted distribution (claim 1), so quoting it as an independent anchor would double-count. The monitoring calendar says a Kalshi re-price updates R01, not X01's anchor slot.

## What the audit missed

1. **Two published numbers do not match the model's own output file, and the audit endorsed one of them.** `x01_joint_summary.json` gives the unconditional day-1 median as **−2.50** and the unconditional 15 Dec mean as **167.2**; revision 1's log and JSON printed −2.4 and 167.3, and the audit wrote that "X01's replay gives exactly −2.4". Both are corrected in revision 2. Small, but the audit's standard is that every published digit reproduces.
2. **A19-03's second composition figure is a conditional/unconditional conflation** (see above): 0.110 is mass, 0.199 is the share of the short case. The audit's point survives twice as strongly as stated.
3. **The gate correction changes what "none of the above" *means*, not just its mass.** Revision 2's none cell is 0.48 accelerating prints, 0.44 in-line prints, with P(C01 below | none) = **0.54** (revision 1: 0.445) and a day-1 median of **+0.3%** (revision 1: +1.2%). The audit published the corrected row but did not flag the character change; a memo that reads "none" as "nothing happens" would be wrong about a cell that now carries 0.14.
4. **There is a middle gate reading the audit did not test.** An in-line print whose guide is *below* Street is not "an in-line print with an in-line guide", so it arguably belongs in base rather than none. That variant gives **0.14 / 0.21 / 0.55 / 0.10** and brackets the gate choice (base 0.17–0.21, none 0.10–0.13). It is not adopted — the question's base option says *decelerating print*, and the guide leg is the parenthetical "and/or", not a substitute for the print gate — but it is published as a §4 discard row, a §7 row and a JSON variant, and it is the right residual for the resolution-criteria audit (0.036).
5. **The memo's breaker column is conjunctive too, and the audit only priced the short one.** P(≥10.6% **and** C02 (a) **and** an FY sentence ≈36%) = **0.0496**, against the conjunctive short case's 0.0462. Both of the memo's scenario columns, read as their headers are written, are ≈0.05 — which is the cleanest way to show a judge that 25/45/30 can only be a print partition.
6. **The panel's breaker gate is a sequential analogue as well.** A19-13 flagged the short leg's `accel_pts ≤ −1.84` analogue for a level gate; `accel_pts ≥ 0.25` for "≥10.6%" is the same construction. It happens not to matter (the W2 breaker cell is 0.10 under both analogues), but the base rate's construction should be described accurately, and §5 now does.
7. **A19-12's independence is now quantified rather than asserted** (corr 0.063 unconditional, ≤0.004 within state), which is what makes the prohibition on day-1 × 15 Dec statements enforceable rather than a caveat.

Nothing in the audit was rejected, and nothing in it was found to be wrong on the numbers.

## Reproduction output

`py -3.13 docs/pitch-forecasts/audits/A19-reproduce.py`, run from the repository root (the script as shipped in the audit, saved verbatim; the only change was removing the closing markdown fence picked up when extracting it from the audit file). Full output in `A19-reproduce.stdout.txt`:

```
print partition  P(<=8.5) 0.2881  P(8.5-10.6) 0.4514  P(>=10.6) 0.2605
C02 anchors [7.86, 9.505, 11.243]
explicit-bucket share of (d) by branch {'lt9': 0.492, '9to10': 0.348, 'ge10': 0.208}   directional-moderate total 0.1878
C02 IPF factors [0.001, 0.009, 0.023, -0.062, 0.325]  target [0.18, 0.17, 0.3, 0.31, 0.04]
C01 g0 -1.9227  implied P(below) 0.7200
C01 slope check: 2/3 weight on GBV = 0.6555  per point of nights growth = 0.599
published gates             {'breaker': 0.1398, 'base': 0.2238, 'short': 0.554, 'none': 0.0825}
decelerating base gate      {'breaker': 0.1398, 'base': 0.172, 'short': 0.554, 'none': 0.1343}
strict decel (<10.34)       {'breaker': 0.1398, 'base': 0.199, 'short': 0.554, 'none': 0.1072}
short-first precedence      {'breaker': 0.107, 'base': 0.2238, 'short': 0.5867, 'none': 0.0825}
material (branch shares)    {'breaker': 0.1398, 'base': 0.2651, 'short': 0.4781, 'none': 0.1171}
material + decel gate       {'breaker': 0.1398, 'base': 0.204, 'short': 0.4781, 'none': 0.1782}
no C04 leg                  {'breaker': 0.1398, 'base': 0.3094, 'short': 0.443, 'none': 0.1078}
C04 (d) at 0.20             {'breaker': 0.1398, 'base': 0.246, 'short': 0.5252, 'none': 0.089}
published base gate literal sequential-gate W2 n 10 {'breaker': 0.1, 'base': 0.2, 'short': 0.5, 'none': 0.2}
published base gate literal level-gate W2 n 10 {'breaker': 0.1, 'base': 0.1, 'short': 0.6, 'none': 0.2}
published base gate material sequential-gate W2 n 10 {'breaker': 0.1, 'base': 0.3, 'short': 0.3, 'none': 0.3}
decelerating base gate literal sequential-gate all16 n 16 {'breaker': 0.062, 'base': 0.062, 'short': 0.688, 'none': 0.188}
decelerating base gate literal sequential-gate W1 n 14 {'breaker': 0.071, 'base': 0.071, 'short': 0.643, 'none': 0.214}
decelerating base gate literal sequential-gate W2 n 10 {'breaker': 0.1, 'base': 0.1, 'short': 0.5, 'none': 0.3}
decelerating base gate literal level-gate W2 n 10 {'breaker': 0.1, 'base': 0.1, 'short': 0.6, 'none': 0.2}
decelerating base gate material sequential-gate W2 n 10 {'breaker': 0.1, 'base': 0.2, 'short': 0.3, 'none': 0.4}
decelerating base gate material level-gate W2 n 10 {'breaker': 0.1, 'base': 0.2, 'short': 0.4, 'none': 0.3}
FY margin actions, November prints [('3Q22', 'none'), ('3Q23', 'raised'), ('3Q24', 'raised'), ('3Q25', 'raised')]
descriptor options: (d) count 8  of which explicit buckets 1
deep decelerations n 4 mean raw 1.75 [('4Q22', 13.4), ('2Q23', -0.5), ('1Q24', -6.9), ('1Q25', 1.0)]
  in W1 only: n 3 mean raw -2.13
W1 all prints  n 14 slope 1.01 corr 0.337
W1 decelerators n 9 slope -1.24 intercept -8.67 corr -0.620
W2 all prints  n 10 slope 2.49 corr 0.587
W2 decelerators n 6 slope -1.62 intercept -8.89 corr -0.586
PW 15 Dec by conditional median 164.8 (published 164.8)
PW 15 Dec by conditional mean   167.3 (= the joint's unconditional mean)
memo breaker 0.25 needs P(a | >=10.6) = 0.960 against the joint's 0.535
```

The 1,000,000-draw replay of `x01_joint.py` and the corrected conditional tables were produced with `datasets/x01_reclassify_v2.py` (`x01_v2_summary.json`), which imports the untouched revision-1 joint and only reclassifies it.

## Final table

| Object | revision 1 | auditor | revision 2 | note |
|---|---:|---:|---:|---|
| P(thesis breaker) | 0.14 | 0.14 | **0.14** | unchanged; 0.11 under short-first precedence, which the memo should use if it keeps its own ≈36%-FY-sentence breaker column (A19-07) |
| P(base) | 0.22 | 0.17 | **0.17** | gate corrected to "decelerating print" (<10.09); 0.0514 moves to none (A19-01). Range over gate readings 0.17–0.22 |
| P(short case) | 0.55 | 0.55 | **0.55** | unchanged under the literal reading; carry as **0.48–0.55, reading-dependent** if only one number is quoted |
| P(none of the above) | 0.09 | 0.14 | **0.14** | now 0.48 accelerating prints / 0.44 in-line prints; rounded up from 0.1342 at the short case's expense, per the audit's line 2 |
| base, day-1 median | −3.8% | −4.7% | **−4.7%** | worse than short under the corrected gate; the ordering reverses (A19-03) |
| short case, day-1 median | −3.8% | −3.8% | **−3.8%** | unchanged; 34% of the cell is a directional word and 19.9% of its draws sit on a print ≥10.0% |
| print partition (breaker / base / short) | not computed ("replace 25/45/30") | 0.26 / 0.45 / 0.29 | **0.26 / 0.45 / 0.29** | the memo's 25/45/30 *is* this object; keep it and label it as the 12-month table (A19-04) |
| PW 15 Dec close, median-of-branches | $164.8 (labelled "probability-weighted") | $164.7 median | **$164.8**, labelled `pw_dec15_median_of_branches` | medians do not mix (A19-08) |
| PW 15 Dec close, mean | not published | $167.2 | **$167.3** | the probability-weighted close; the memo should use it, because its own ~$146 is built from range midpoints |
