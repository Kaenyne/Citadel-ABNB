# Response to audit A16 (B08, B09, B10, B17)

Response date: 2026-09-17
Responds to: `A16-research-audit.md` (independent Opus auditor standing in for Codex/Astra, read-only, after two Codex failures on this batch)
Revised research: `questions/bonus-ai-hosting-cost-step/`, `questions/bonus-sbc-step-up/`, `questions/bonus-interest-income-falls/`, `questions/bonus-take-rate-guided-down/` — all four `research-log.md` at revision 2
Revised forecasts: all four `forecasts/2026-09-17-forecast.json` at `"revision": 2`
Reproduction script: `A16-reproduce.py` (the audit's script, saved verbatim from the fenced block; **no path fix was needed** — it ran clean from the repo root with `py -3.13 -B`). Output at the end of this file.
Revision-1 models (`b08_model.py`, `b09_model.py`, `b10_model.py`, `b17_model.py`) and their CSVs are left untouched as the audit trail; every revision-2 number in this response was recomputed independently in `py -3.13` at N = 400,000 and agrees with the audit's N = 200,000 replay to within Monte Carlo error.

## Summary

Twenty-five findings across four questions. **Twenty-two accepted, three accepted in part, none rejected.** Every computation in the audit reproduced: the $578.0M line-build base and the 6-of-8 scenario count, the $368M / $411M SBC correction and the guidance ledger's driver-history basis, the un-ramped buyback draw, the zero "take rate" hits in the 3Q24 and 3Q25 call mirrors, the +12.8bp team FY26 take-rate path, and every §7 row the audit said did not replay.

Headline numbers, revision 1 → revision 2:

| | rev 1 | rev 2 | auditor |
|---|---:|---:|---:|
| B08 | 0.38 (0.25–0.52) | **0.44 (0.31–0.57)** | 0.45 |
| B09 | 0.10 (0.05–0.20) | **0.08 (0.04–0.14)** | 0.08 |
| B10 | 0.05 (0.02–0.10) | **0.04 (0.015–0.08)** | 0.04 |
| B17 | 0.42 (0.28–0.56) | **0.41 (0.28–0.55)** | 0.38 |

No gap to the auditor exceeds three points, so no asymmetry needs naming under the >10-point rule; the three-point B17 gap is argued in A16-08 below and is a disagreement about a reference class, not about arithmetic.

What actually moved. **B08** moved six points because the hosting mixture moved and the spreads widened — and because the audit was right that a memo cannot show a base case of $578M next to a 26% probability of ≥$575M. **B09** and **B10** each moved down because the errors the audit found both ran toward Yes: B09's route C was calibrated on a guidance record that this log's own SBC correction dissolves, and B10's buyback branch spent the incremental draw a quarter early. **B17's headline barely moved — its impact table moved by a factor of 2.4**, from −$6/share to −$2.5, because the modal Yes is a sentence the CFO already said on 6 August, and both margin rows were dividing by an unchanged revenue base.

The share count is now unified across the four: **591.7m for 3Q26-dated rows, 573m for FY27 rows** (B08 was using 620m).

## Finding-by-finding

### A16-01 (critical, B08) — the published number contradicts the team's own margin view: **accepted**
Reproduced: `40_lines_quarterly.csv` 4Q26 cost of revenue by scenario is 578.0 / 548.8 / 571.9 / 586.9 / 581.9 / 575.3 / 575.5 / 583.9 — **6 of 8 at or above $575M**, only `evidence_only` and `rev_bear` below. The $19M gap to this log's mixture mean is entirely hosting ($100.2M build vs $82.3M mixture at revision-1 weights); fees ($403.7 vs $404.4), chargebacks ($26.0) and other ($47.8 vs $47.4) agree.
Fix: the hosting mixture moves a third of the way toward the build (below), and the coherence break is **stated in three places** rather than resolved in prose — a new §4 row, §6 ("the team's own adopted path resolves this question Yes"), and §9's EV note. The monitoring calendar now opens with settling the hosting line before 2 October. I did not move the line build: CLAUDE.md rule 1 forbids it from this run, and the choice belongs to whoever owns `40_line_build`.

### A16-02 (critical, B17) — §9 prices the modal Yes as news: **accepted**
Reproduced R04 revision 2's `impact.note` and `split_by_form` and re-priced B17's Yes mass on the same structure. Route (b) is **0.82** of the Yes mass and its modal form is the CFO restating the 6 August FY26 sentence — already inside the LSEG 4Q26 mean this log uses ($3,162M) and inside FY27 estimates. On the split (0.60 repeat-of-standing-form at −$0.5, 0.15 new period/mechanism at −$5, 0.20 letter-Q4-lower at −$5, 0.05 quantified FY27 at −$9): **E[stock | Yes] = −$2.50**, **EV = 0.41 × −2.50 = −$1.0/share**.
`material` stays `true` with R04 rev 2's borderline language, for the reason the audit gives: the row survives because the 0.05 tail form is genuinely worth −$9, not because the modal form is worth anything. The two tables are now mirrors: R04 +$2.2 / EV +$1.1, B17 −$2.5 / EV −$1.0.

### A16-03 (major, B17) — margin rows divided by an unchanged revenue base: **accepted**
Recomputed: FY27 (5,483 − 153)/(15,829 − 170) = 34.038% against 34.639% = **−0.60pp**, not −1.0; FY26 (5,098 − 27)/(14,268 − 30) = 35.613% against 35.730% = **−0.11pp**, not −0.2. The audit is also right that R04's mirror row (+$23M revenue → +0.080pp, published 0.09) is computed correctly on the same annuals, so the run was using one coefficient two ways. Published: the full-mark rows inside `split_by_form`, the expectation across forms at the top level (−0.04 / −0.11). The EPS row (−$0.21 = $0.0014 × $153M) applies the coefficient once and does not move.

### A16-04 (major, B09) — route C calibrated on the uncorrected SBC series: **accepted**
Reproduced both bases. Printed releases: 1,120/930 = **+20.43%**, 1,407/1,120 = **+25.63%**, 1,592/1,407 = **+13.15%**. Driver history: 1,100/930 = 18.28, 1,439/1,100 = 30.82, 1,581/1,439 = 9.87 — and 18.28 / 30.82 are exactly what `02_guidance_ledger.csv` carries as `actual` for the `sbc_yoy_pct` rows. So FY23 "~20%" was **met** (not beaten), the 1Q24 "~20%" guide missed by **5.6** points (not 10.8), and the 3Q24 "~25%" guide was **met** (not missed by 5.8).
Fix: route C recalibrated to P(miss) **0.15** × N(**+4**, 3): 0.197 → **0.127**. The ledger defect is written into claim 3, into the monitoring calendar, into a `data_defect_flag` block in the JSON, and flagged to the synthesis (see the last line of this response).

### A16-05 (major, B09) — three §7 rows do not replay: **accepted**
Reproduced: the audit's replay of 0.4A + 0.4B + 0.2C + 0.02 gives 0.131 / 0.093 / 0.180 / 0.095 against the published 0.13 / 0.05 / 0.22 / 0.06 — the 0.05 and 0.06 were route-level readings and the 0.22 was neither route nor blend. §7 is now a **computed blend loop** at the revision-2 weights (0.45A + 0.45B + 0.10C + 0.012): all-four 0.105, sd 0.02 0.063, last-8 0.161, 1H26 0.065, P(miss) 0.25 0.087, P(miss) 0.08 0.077. Honest §7 width **0.06–0.16**, against the published 0.05–0.25, and now consistent with the 0.04–0.14 credible interval.

### A16-06 (major, B10) — the buyback branch spends the draw a quarter early: **accepted**
Reproduced: flat conditionals 0.0957 / 0.3803 against ramped 0.0621 / 0.2074; published mixture 0.0431 → **0.0355** on the ramp alone. The `avg_base` construction in `b10_history.csv` confirms the average-of-quarter-ends definition, so a 2H26 upsize has reached roughly half its size by 30 September. Ramped in the revision-2 model. This was the single largest error in the revision-1 log and it ran toward Yes.

### A16-07 (major, B10) — the "any y/y decline" companion is below its own base regime: **accepted**
Reproduced: base regime P(≤$162M) **0.154**, published mixture **0.187** (the audit's 0.213 is on the revision-1 weights, before the ramp and the emergency-branch cut), against the log's "≈ 0.13". Published as **0.15 base regime / 0.19 mixture** with which is which stated, in §6 and in the JSON. This is the number a memo sentence would use, and the sentence is "interest income more likely than not **rises**".

### A16-08 (major, B17) — P(take rate is a topic) = 0.80 comes from the wrong reference class: **accepted in part**
Reproduced the audit's evidence exactly: the 3Q24 and 3Q25 **call** mirrors contain "take rate" **zero** times in 146,320 and 165,027 characters with ten and nine analyst firms in Q&A (3Q23 16, 3Q22 14, 3Q21 2), and no letter since 1Q23 has named customer incentives as reducing the take rate (the only letter since 1Q23 containing "incentive" is 1Q24, where it is "payment processing incentive benefits", a cost item).
**Where I part company: that is evidence about the call, and the question resolves on letter *or* call.** Checked independently:
- **Every Q3 letter carries a forward Q4 take-rate sentence and a standing "Monetization and Take Rate" section.** 3Q23: "we anticipate that our implied take rate… in Q4 2023 will be slightly higher than Q4 2022". 3Q24: "we anticipate that our implied take rate in Q4 2024 will be **slightly lower on a year-over-year basis**" — a realised leg-(a) Yes. 3Q25: "we anticipate our implied take rate in Q4 2025 to be relatively flat year over year". Five "take rate" hits in each of the 3Q24 and 3Q25 letters. The *print* addresses forward take rate in 3 of 3 Q3s even when the call is silent.
- **The two silent Q3 calls had no standing FY take-rate guidance to update.** The 2Q24 call contains "take rate" zero times; the 2Q25 call twice, both inside Chesky's hotels answer ("our take rate is very, very competitive"). The 6 August 2026 call left an explicit FY26 take-rate sentence in the CFO's prepared-remarks outlook block, and the 3Q25 call did carry a "Q4 and full year 2025 outlook" block. **2026 is the first Q3 in the record with a standing FY take-rate guide to restate.**
- **R04 revision 2 carries 0.75** for a take-rate/fee question on the same 5 November call, and the audit's own coherence section requires the batch to share one taxonomy. Setting 0.65 here while R04 holds 0.75 would price the same call two ways.
Fix: P(topic) **0.80 → 0.78**, redefined as "P(the print carries a forward take-rate discussion capable of naming a driver)" rather than "take rate is a topic on the call", with the Q3-call record written into a new claim 9b. Union 0.481 → **0.473**. The audit's 0.65 is carried as a §7 row (0.37).

### A16-09 (major, B17) — the team's own FY26 path is +12.8bp, not flat: **accepted in part**
Reproduced: FY26 revenue $14,268M ÷ GBV $105.4bn = **13.535%** against FY25 $12,241M ÷ $91.3bn = **13.407%**, i.e. **+12.8bp** against management's standing "relatively flat compared to 2025"; C11 revision 2 puts 0.76 on the 3Q26 ratio printing above +22bp. The row is added to §4, §7 and a new claim 9c, and the C11 tension is stated rather than resolved by fiat.
**Where I part company: this is not a reason to cut route (b).** The audit's own upheld ruling on convention (5) is that "flat, with incentives offsetting gains" counts, because the question's parenthetical is "or that incentives/new businesses **will reduce it**". By the same reading, "we now expect the implied take rate to be **up slightly**; absent higher customer incentives it would be higher still" qualifies. A better-than-guided take rate changes the **direction word**, not whether the incentives clause survives. Only dropping the clause entirely resolves No. So A16-09 is a strong argument against **route (a)** — which is why route (a) stays at 0.12 and is not raised — and a modest one inside route (b)'s P(qualifies), which sits at 0.50 rather than the 0.55–0.60 the standing guidance alone would justify. §7 carries the extreme version: if a direction upgrade certainly dropped the clause, the number is **0.31**.
Revision 1 stated convention (5) and then reasoned as though "up slightly" were a No. That inconsistency is fixed in §0b.

### A16-10 (major, B08) — the 10-K argument is over-read: **accepted**
Verified the FY25 10-K Note 13 schedule verbatim ($1,749 / 219 / 930 / 600 / —, "at least $1.7 billion… through 2031") and the 2Q26 10-Q MD&A sentence in full. The audit is right: the `less than 1 year` bucket is a contractual **minimum**, and the increase is attributed to "higher amortization related to **reserved instance purchases**" — prepaid capacity whose expense recognition can step ahead of the committed minimum. Claim 6 is re-scoped to leg 1, where it is strong and makes leg 1 *more* likely, and withdrawn from the leg-2 argument, where revision 1 used it as the primary reason to cut the team's own hosting path from 1.00 to 0.20. Replaced there by 2Q26 server costs +$12M y/y, S162, and the point in "what the audit missed" below.

### A16-11 (major, B08) — the 0.45 weight contradicts claim 7: **accepted in part**
Reproduced the branch arithmetic and the re-weighting. The evidence-only branch is +$15M/quarter on a $56M FY25 base — roughly the y/y increase already printed in 2Q26 — so it is the "no further ramp" case, and Mertz said on 6 August that the guidance "obviously does assume a material increase in terms of the AI spend over the course of the year". A 0.45 plurality on it is not defensible.
**Re-weighted to 0.35 / 0.37 / 0.28, not the audit's 0.33 / 0.37 / 0.30.** The reason for the residual 2 points: Chesky's framing is on the record too ("our investment in AI will not affect the P&L… we're not building data centers", S140/S181), and a material increase in *AI spend* is not the same event as a material increase in *cost of revenue* — inference and tooling spend can land in product development. That is a live possibility for **this line** specifically and it is worth some mass. Effect: leg 2 **0.3158** against the audit's 0.3246, a 0.9-point difference.

### A16-12 (major, B08) — analyst-dispersion spreads used as outcome spreads: **accepted**
Reproduced: at gbv_sd 800 and rate_sd 0.05 the published mixture gives leg 2 0.2777, and with the A16-11 re-weight 0.3158. $650M is the MODL cross-sectional range for a quarter that has not started; the team's own 4Q26 nights uncertainty is ~2 points ≈ $460M of GBV before ADR and FX, and the merchant-fee annual-equivalent rate has moved 1.69 → 1.76 → 1.68 across three years against an assumed sd of 0.04. Adopted at gbv_sd **800**, rate_sd **0.05**, and labelled outcome spreads in claim 11 and §7. The revision-1 spreads are carried as a §7 row (0.43).

### A16-13 (major, all four) — no question in the batch has an external anchor: **accepted**
Confirmed: no Kalshi or Polymarket market exists on any of the four objects, and the three ABNB pulls are byte-identical copies of one fetch of the `KXABNB-26NOVNEB` nights ladder. All four now carry `anchor: null` with `NO_EXTERNAL_ANCHOR`; the internal objects are relabelled `internal_comparison` (B08 the line build 0.63, B09 M7 0.16, B10 M7's LIVE quantile 0.11) and `final_minus_anchor` is not reported against them. B08's `not_independently_derived_flag` is corrected **false → true**.
B17 had no internal comparison at all — its "anchor" was a self-chosen flat prior — so for B17 the fix goes further: **the 0.50 prior is removed from the blend as well as from the anchor field** (0.5/0.3/0.2 → 0.65/0.35), which is where its 0.20 weight was doing real work. B10's adjacent Kalshi Fed ladders stay as an input to the rate path; they price the Fed, not this line, so they are not an anchor for the question either.

### A16-14 (major, B17) — sibling re-basing: **accepted**
Confirmed from the revision-2 JSONs: R04 is at 0.52 (0.38–0.66) and C11 at 0.76, both written after B17's forecast file (04:41:01). Claim 7 re-based from 0.58 to **0.52**, with R04 rev 2's decomposition (call 0.75 × 0.40) and its adoption of the **same convention (1)** recorded — the two questions now share a period rule as well as a Yes-mass taxonomy. R04's `split_by_form` is carried into B17 §9 (A16-02).

### A16-15 (minor, B09) — route C is not an independent third route: **accepted**
Confirmed: `model:45–47` fixes 3Q26 at 399 × 1.132 as a scalar and loads the entire FY residual onto Q4, so a high-SBC regime is made to *offset* itself; adding independent Q3 noise of $25M raises the route to 0.216, the wrong sign for the correlation that holds. Weight **0.20 → 0.10**, described in §4 and claim 8 as a guidance-miss overlay on route B.

### A16-16 (minor, B09) — companion quantiles not computed anywhere: **accepted**
Sampled the published 0.45/0.45/0.10 blend: median **$466M**, p10–p90 **$432–495M**, P(≥$480M) **0.27**, P(≤$450M) **0.26**, against the published $468M / 0.30 / 0.25, which were the seasonal route's. Published and labelled.

### A16-17 (minor, B10) — the 16 Sep FOMC is not in the saved evidence: **accepted**
Confirmed: `DFEDTARU`'s last row is 2026-09-16 = 3.75 and `DTB3`'s 2026-09-15 = 3.97. Claim 5 is re-cited to the Kalshi ladder inside this question's own `sources/` — `KXFED-26OCT-T3.75` at bid **0.98** / ask 0.99 with 22,734 contracts and 8,559 in 24 hours — and states that DFEDTARU's 3.75 on 16 Sep is the pre-effective-date reading. "Traders price three hikes through June 2027", sourced to R10 claim 10 which has no saved snapshot either, is withdrawn.

### A16-18 (minor, B10) — "thin" carried across from Polymarket onto Kalshi: **accepted**
Confirmed: `KXFEDDECISION-26OCT-H0` has 502,083 contracts of volume, 360,307 open interest and **298,901 in the last 24 hours**; `updated_time` reads 2026-04-09 on all 55 KXFEDDECISION and all 76 KXFED markets including January-2027 strikes, so it is series metadata, not a quote stamp — the reverse of the inference A01-04/A12-14 drew on the ABNB ladder, where the liquidity evidence was independent and pointed the other way. The ladders are weighted as deep and live and the **emergency-easing branch is cut 0.02 → 0.005**: the market prices a single December cut at 0.01–0.02 and that branch needs roughly three.

### A16-19 (minor, B10) — two §7 rows do not replay: **accepted**
Reproduced at mixture level: β 0.94 gives **0.015** (published 0.03) and funds held flat y/y **0.076** (published 0.07); the other rows land within a point. §7 is recomputed at mixture level on the revision-2 mixture and the level is stated.

### A16-20 (minor, B08) — three arithmetic slips in one table: **accepted**
(i) "~−0.9pp on the Street's $15.8bn" is withdrawn: +$100M on $15,819M is **−0.63pp**, the same as on the team's base; what widens is the team-vs-Street FY27 margin **gap**, 1.81pp → **2.44pp**. (ii) The FY26 row is stated as −0.08pp full-mark. (iii) The share count is **620m → 573m** for FY27 rows, giving −$2.79 not −$2.58, and the run convention (591.7m for 3Q26-dated rows, 573m for FY27) is written into claim 14. B09's and B10's GAAP-EPS rows replay exactly (−$0.202 and −$0.130) and are unchanged.

### A16-21 (minor, B08) — the convention-(2) row understates the largest lever: **accepted**
Confirmed from Note 13: 2026 $219M against 1–3 years $930M ≈ $465M/yr, already ~+$246M for 2027, and the FY26 10-K **will** restate a schedule. The row is re-priced 0.85 → **~0.96** and moved to the top of §7; the monitoring calendar now opens with settling the convention with Krish before 2 October.

### A16-22 (minor, B08) — two thresholds for one question: **accepted**
Confirmed: $487M × 1.18 = $574.66M, and leg 2 is **0.320** on that reading against 0.316 on $575M — 0.4 points. §6 states that convention (1) adopts the dollar threshold, quotes the difference, and notes that releases print whole millions so no realistic print falls between the two.

### A16-23 (minor, B17) — the strict multiplier 0.55 is unsourced: **accepted in part**
Accepted that 0.55 was asserted. **Derived at 0.50** rather than re-derived to 0.55: of the two forward take-rate objects at the last print, one was FY-worded (the call) and one quarter-worded (the letter), and 4 of 13 letters carry an FY-form sentence. It remains a judgement and is labelled one. Strict companion **0.33 → 0.31**, which is the audit's number.

### A16-24 (minor, B17) — claim 5's sources were never saved: **accepted**
Confirmed: `sources/` holds only the shared Kalshi and Polymarket pulls and the query log. The Skift and Bloomberg rows are marked "search snippet, unsaved"; the **"−0.8pt scaling" row is struck** — it cites no retrievable object and must not enter the memo under any label.

### A16-25 (minor, B17) — the short-case row is tautological: **accepted**
Confirmed: GBV is scaled by revenue ÷ 3,178.1, so the take rate is identically 13.8256%. The §6 companion no longer quotes it as an independent scenario and the field is renamed `short_case_take_rate_held_by_construction_pct`.

### Rulings requested by the audit prompt: **adopted as ruled**
Convention (1) upheld **with the tightening**, which is now written into §0b: the statement must be forward *in form* ("expect", "anticipate", "will") and its period must extend into 4Q26; a retrospective "our nine-month take rate was held back by incentives" does not qualify. Convention (5) upheld and, as the audit says, it is not really a convention — it is the question's parenthetical read literally; the net-only reading stays in §7 and nowhere else (it is **~0.25** at revision-2 inputs, blend level; revision 1's ~0.22 was a union). Convention (2) on B08's 10-K table upheld, with the alternative re-priced to ~0.96.

## What the audit missed

1. **B08's §9 conflates the two legs** — the biggest §9 error in the batch after A16-02, and the audit did not catch it. Revision 1 applied *both* the 4Q26 print effect (+$12M of cost) *and* the FY27 quantification (+$100M) to every Yes, but only ~28% of the Yes mass is both legs (P(both) 0.126 of P(Yes) 0.446); 0.425 is leg 2 only and 0.292 is leg 1 only. Split by leg, **E[stock | Yes] is −$3.2, not −$4**, and the EV −$1.4 rather than −$1.5 — still material, but on an honest table.
2. **B08: the internal-use-software amortisation offset is a declining tailwind.** The audit quotes the 2Q26 10-Q sentence as verbatim-verified and treats the +$12M net server increase as the evidence-only run-rate. But that +$12M is *after* "a decrease in amortization expenses related to capitalized internal-use software projects" — an offset that shrinks as those projects fully amortise. At constant gross hosting the **reported** line's y/y growth therefore accelerates. This argues for the higher hosting branches and neither the log nor the audit used it; it is now in §4 and in the 6 Nov monitoring row.
3. **B17: the letter door is open for the question, even though it is shut for the incentives clause.** The audit's "route (b) is a call-only route in the one slot where the call has been silent" is right about the incentives clause and wrong about the print: every Q3 letter carries a forward Q4 take-rate sentence and a standing "Monetization and Take Rate" section, and the **3Q24 letter guided 4Q24 take rate lower** — a realised leg-(a) Yes in the very slot the audit calls silent.
4. **B17: the two silent Q3 calls had nothing to restate.** The 2Q24 call contains "take rate" zero times and the 2Q25 call twice (both Chesky on hotels' competitive take rate), so there was no standing FY take-rate guidance going into 3Q24 or 3Q25 — while the 3Q25 call *did* carry a "Q4 and full year 2025 outlook" block. 5 November 2026 is the first Q3 in the record with a standing FY take-rate sentence to update. This is the asymmetry that holds P(topic) at 0.78.
5. **B17: A16-09's own logic cuts the other way under the convention the same audit upheld.** "Up slightly, absent higher customer incentives it would be higher still" qualifies under convention (5). A direction upgrade is not a No.
6. **B10: Q4 seasonality in β is recorded in claim 4 and never used.** The two Q4 realisations are **0.966 and 0.942** against the rule's 0.876 and a nine-quarter non-Q4 mean of 0.842 — revision 1 centred a Q4 question on a non-Q4 parameter. At a Q4-appropriate centre of 0.90 the base regime falls **0.0133 → 0.0064** and the mixture to ~0.030. The audit checked the β 0.94 §7 row (A16-19) but did not make the structural point. M7's registered 0.88 is kept (n = 2 is a thin seasonal) and the bias is stated in §5, §7 and the gate audit as the reason the honest centre may be 0.03.
7. **B10's gate audit and companion were reported at different levels.** The gate's residual sum (≈0.04–0.05) is a mixture number; the "≈0.13" companion was a base-regime intuition. Revision 2 states the level on every number in §6 and §7.
8. **B09: the corrected record removes the only precedent for a miss of the required size.** This question needs ≈8.5 points of overshoot against the M7 path (+21.65% required against a 13.2% path). On the printed record the largest miss of an SBC sentence is **5.6** points (FY24 against the 1Q24 "~20%" guide), and the regime that produced it — the last of the double-trigger RSUs — is spent. The audit corrected the record; it did not draw this consequence. §4's "2024-style step" row falls from ~0.08 to ~0.05 on it.
9. **B09: the FY26 bar is easier than the ledger implies.** "Lower than 2025" is measured against FY25's **+13.15%**, not the ledger's 9.87%, so 1H26 at +14.7% is a **1.5-point** overshoot of the sentence rather than a 4.8-point one — a smaller tell, and the reason route C's miss branch is 0.15 rather than 0.20.
10. **R04 revision 2 uses 591.7m shares on an FY27 level effect**, which is off the run convention (573m for FY27). At 573m its quantified-form level leg is +$5.78 rather than +$5.6. Not edited here — R04 is outside this batch — and flagged to the synthesis.

## Reconciliation with the auditor's numbers

| | rev 2 | auditor | gap | decision |
|---|---:|---:|---:|---|
| B08 | 0.44 | 0.45 | 1 pt | The two leg-2 inputs differ by 0.9 points (mixture 0.35/0.37/0.28 vs 0.33/0.37/0.30, A16-11) and the final differs by one more because revision 2 keeps revision 1's blending rule (0.9 weight on the decomposition, 0.1 on the base rate) rather than publishing the decomposition neat. Held at 0.44; the difference is not worth a convention change. |
| B09 | 0.08 | 0.08 | 0 | Same route C recalibration and weight; the +0.012 tail against the auditor's +0.010 is inside rounding. |
| B10 | 0.04 | 0.04 | 0 | Same ramp, same emergency-branch cut, same unmodelled-tail allowance; my mixture is 0.0356 against the auditor's 0.036. |
| B17 | 0.41 | 0.38 | 3 pts | Entirely P(topic) — 0.78 against 0.65 (A16-08 above). Held at 0.41 because the question resolves on letter **or** call, every Q3 letter carries a forward Q4 take-rate sentence, the two silent Q3 calls had no standing FY guide to restate, and R04 rev 2 prices the same call at 0.75. The auditor's 0.65 is published as a §7 row (0.37), so a reader can take either. |

No gap exceeds ten points, so no question needed a named asymmetry or a move toward the auditor beyond the ones made above.

## Final table

| question | revision 1 | auditor | **revision 2** | anchor | \|final − anchor\| | EV $/share | material |
|---|---:|---:|---:|---|---|---:|---|
| B08 bonus-ai-hosting-cost-step | 0.38 (0.25–0.52) | 0.45 | **0.44 (0.31–0.57)** | **null** (NO_EXTERNAL_ANCHOR); internal comparison 0.63 = the line build | n/a (internal gap −19 pts) | **−1.4** | **yes** (borderline-plus) |
| B09 bonus-sbc-step-up | 0.10 (0.05–0.20) | 0.08 | **0.08 (0.04–0.14)** | **null**; internal comparison 0.16 = M7 rule | n/a (internal gap −8 pts) | −0.24 | no |
| B10 bonus-interest-income-falls | 0.05 (0.02–0.10) | 0.04 | **0.04 (0.015–0.08)** | **null**; internal comparison 0.11 = M7 LIVE q10 | n/a (internal gap −7 pts) | −0.08 | no |
| B17 bonus-take-rate-guided-down | 0.42 (0.28–0.56) | 0.38 | **0.41 (0.28–0.55)** | **null**; rev 1's 0.50 was a flat prior, now removed from the blend too | n/a | **−1.0** | **yes** (borderline, mirror of R04's +1.1) |

Two of the four are material and two are not. The batch's `|final − anchor|` column in SYNTHESIS.md should be **empty for all four**, which is the honest presentation.

**Flag for the synthesis.** `data/processed/overnight/02_guidance_ledger.csv`'s `sbc_yoy_pct` **actuals are wrong**: FY23 18.28 and FY24 30.82 reproduce only from `data/processed/abnb_driver_history_quarterly.csv` (4Q23 270, 4Q24 400), which the releases contradict (290, 368, 411; FY25 $1,592M reconciles only with 411). On the printed basis the actuals are FY23 **20.43**, FY24 **25.63**, FY25 **13.15**, which changes the outcome column from beat/miss/miss to met/miss-by-5.6/met. Neither file may be edited from this run (CLAUDE.md rule 1). Any question in the run that used `sbc_yoy_pct` as a base rate inherits the error — **B08 claim 8 cites the same metric** for its February-letter record of quantified cost items — and the synthesis should say so before the ledger is quoted anywhere in the memo.

## Reproduction output

`py -3.13 -B docs/pitch-forecasts/audits/A16-reproduce.py` from the repo root, 2026-09-17. The script is the audit's, saved verbatim from its fenced block; it ran clean with no path fix.

```
==============================================================================
0. line-build annuals behind every section 9 table
   FY26 rev 14268 ebitda 5098 margin 35.730% | FY27 rev 15829 ebitda 5483 margin 34.639%
==============================================================================
B08 / 1. claims 1 and 3 against the repo
   panel cor_cash 1Q25-2Q26: [506, 544, 549, 487, 581, 633]
   FY25 2086 ; 9M25 1599 ; 4Q25 487  (registry base 487)
   CoR/GBV y/y (n=10) mean -1.00 sd 3.74   (log: -1.0 / 3.7)
   needed ratio change at GBV +12.7pct = 4.70 ; observed >= that in 1 of 10 quarters
   40_lines_quarterly 4Q26 cost of revenue by scenario:
     scenario   cor_fees  cor_chargebacks  cor_hosting  cor_other   cor_cash  cor_cash_yoy_pct
         base 404.385568        25.998569   100.207932  47.447388 578.039457         18.693934
evidence_only 404.385568        25.998569    71.000000  47.447388 548.831525         12.696412
     rev_bear 398.316433        25.969710   100.207932  47.394720 571.888796         17.430964
     rev_bull 412.778566        26.176498   100.207932  47.772108 586.935104         20.520555
    cost_bear 418.633097        30.692755    85.116179  47.447388 581.889418         19.484480
    cost_bull 390.138040        21.665474   116.063462  47.447388 575.314364         18.134366
    both_bear 412.350131        30.658685    85.116179  47.394720 575.519715         18.176533
    both_bull 398.235331        21.813748   116.063462  47.772108 583.884649         19.894178
   scenarios at or above the 575 threshold: 6 of 8
B08 / 2. leg-2 Monte Carlo (stdlib replay of b08_model.py)
   published 0.45/0.35/0.20, gbv_sd 650           p2 0.2586 median 559 | total at leg1|no 0.18 0.3921 / 0.19 0.3995
   audit 0.33/0.37/0.30, gbv_sd 800, rate_sd 0.05 p2 0.3234 median 563 | total at leg1|no 0.18 0.4452 / 0.19 0.4519
   model values: p2 0.2598, median 559.2, total 0.3930; published headline 0.38
B08 / 3. FY25 10-K purchase-obligation schedule (claim 6)
    non-cancelable commitments and obligations as of December 31, 2025 (in millions): Total Less than 1 year 1 to 3 years 3 to 5 years More than 5 years Purchase obligations $ 1,749 $ 219 $ 930 $ 600 $ � Other commitments 169 66 80 5 18 Total $ 1,918 $ 285 $ 1,010 $ 605 $ 18 Purchase commitments include amounts related to the Company�s commercial agreement with a data hosting services provider, pursu
B08 / 4. section 9 arithmetic
   FY26 +12 of cost, revenue unchanged -> -0.084pp (log -0.1)
   FY27 +100 of cost -> -0.632pp (log -0.6); on Street revenue 15819 -> -0.632pp (log ~ -0.9)
   EPS -100 x 0.0014 = -0.140 (log -0.14): one application, correct
   level effect -100 x 16 / 573m = -2.79 ; / 620m as the log uses = -2.58
==============================================================================
B09 / 1. SBC series: the releases against the repo CSVs
   4Q25 letter -> Stock-based compensation expense $368 $411 $1,407 $1,59
   4Q24 letter -> Stock-based compensation expense $290 $368 $1,120 $1,40
   2Q26 letter nine-quarter row -> Stock-based compensation expense 382 362 368 358 424 399 411
   4Q23: driver_history 270 | 02_panel sbc_total_is 290 | printed release 290
   4Q24: driver_history 400 | 02_panel sbc_total_is 368 | printed release 368
   4Q25: driver_history 400 | 02_panel sbc_total_is 411 | printed release 411
B09 / 2. the guidance ledger's sbc_yoy_pct actuals are on the DRIVER-HISTORY basis
print_quarter target_period  value_mid  actual outcome
         3Q23        FY2023       20.0   18.28    beat
         1Q24        FY2024       20.0   30.82    miss
         3Q24        FY2024       25.0   30.82    miss
   printed basis: FY23 20.43  FY24 25.63  FY25 13.15
   driver basis : FY23 18.28  FY24 30.82  FY25 9.87  <- the ledger's 18.28 / 30.82
   so FY23 ~20pct was MET, FY24 ~20pct missed by 5.6 points not 10.8, 3Q24 ~25pct was MET
B09 / 3. seasonal and y/y routes
   Q4/Q2 [1.0283, 0.9539, 0.9634, 0.9693] | mean4 0.9787 sd4 0.0337 | mean 23-25 0.9622 sd 0.00776 | needed 1.0267
   needed y/y on the printed 4Q25 411 = 21.65 pct (on the registry's 400 = 25.0)
   A(.962,.035) 0.0475 | B(M7 13.2 +- 6) 0.0776 | C(miss .20 / +6) 0.1965 -> blend 0.0893, +0.02 = 0.1093
   model blend 0.0904; published headline 0.10
   section 7 replay: all-four 0.131 (pub 0.13) | sd 0.02 0.093 (pub 0.05) | last-8 0.180 (pub 0.22) | 1H26 0.095 (pub 0.06)
   corrected C (0.15 x N(+4,3)) 0.1273 -> blend .45/.45/.10 + 0.010 = 0.0790  [audit number]
   section 9: +140 FY27 SBC x (1 - 0.175) / 573m = -0.202 EPS (log -0.20)
==============================================================================
B10 / 1. interest-income series, threshold, rates
   2Q26 letter nine-quarter row -> Interest income (226) (207) (183) (173) (190) (180) (162) (155) (183)
   threshold = 0.90 x 162 = 145.8
   DTB3 quarter means: {'2025Q4': 3.726, '2026Q1': 3.594, '2026Q2': 3.624, '2026Q3': 3.749}
   DFEDTARU last row 2026-09-16 = 3.75 ; DTB3 last row 2026-09-15 = 3.97 -> the 16 Sep hike is NOT in the snapshot
   KXFED-26DEC-T4.25  bid 0.27 ask 0.31 vol 19838 oi 14985 vol24 3829 updated 2026-04-09
   KXFED-26DEC-T4.00  bid 0.82 ask 0.83 vol 24097 oi 16876 vol24 5756 updated 2026-04-09
   KXFED-26OCT-T3.75  bid 0.98 ask 0.99 vol 22734 oi 13034 vol24 8559 updated 2026-04-09
   updated_time is 2026-04-09 on all 55 KXFEDDECISION and all 76 KXFED markets, newly listed
   27JAN strikes included -> metadata, not a quote stamp; 26OCT-H0 volume_24h = 298901, so live.
B10 / 2. the M7 rule replay and the buyback-draw ramp
   base regime P(<=145.8) 0.0132 | P(<=162, any decline) 0.1548 | median 177
   model values 0.01365 / -- / 176.7 ; the log's companion states P(<=162) about 0.13
   upsize conditionals: flat 1.5bn 0.0965 / 3bn 0.3817  vs ramped 1.5bn 0.0621 / 3bn 0.2074
   mixture .88/.07/.03/.02 published 0.0431 | ramped 0.0355
   section 9: -90 FY27 x (1 - 0.175) / 573m = -0.130 EPS (log -0.13)
==============================================================================
B17 / 1. the 13-letter take-rate direction record (claim 1)
   ledger rows 13 | 'lower' 1 | flat/similar/in-line 4 | higher/above 6
   realised y/y pts: [0.14, 0.63, 0.07, 0.22, 0.44, 0.01, -0.22, 0.21, -0.69, -0.47, -0.1, 0.09, None]
B17 / 2. the Q3-call record, the gate route (b) must pass
   3Q21 call chars 149695 | Q&A firms  9 | 'take rate'  2 | 'moneti' 0 | 'incentive' 0
   3Q22 call chars 165449 | Q&A firms 11 | 'take rate' 14 | 'moneti' 4 | 'incentive' 0
   3Q23 call chars 157117 | Q&A firms 10 | 'take rate' 16 | 'moneti' 6 | 'incentive' 0
   3Q24 call chars 146320 | Q&A firms 10 | 'take rate'  0 | 'moneti' 0 | 'incentive' 0
   3Q25 call chars 165027 | Q&A firms  9 | 'take rate'  0 | 'moneti' 0 | 'incentive' 0
   4Q25 call chars 156670 | Q&A firms 11 | 'take rate'  8 | 'moneti' 0 | 'incentive' 0
   1Q26 call chars 160563 | Q&A firms  8 | 'take rate' 14 | 'moneti' 6 | 'incentive' 0
   2Q26 call chars 155070 | Q&A firms  8 | 'take rate'  7 | 'moneti' 5 | 'incentive' 5
   letters from 1Q23 on that contain the word 'incentive': ['1Q24']
   so route (b) has no letter door, and the Q3 call was silent in 2 of the last 3 years
B17 / 3. the 2Q26 sentence (claim 2), verbatim
    For the full year, we expect our implied take rate to be relatively flat compared to 2025, accounting for the timing of bookings versus check-in with Reserve Now, Pay Later, as well as higher customer incentives related to new businesses during 2026. Absent these incentives, we would have anticipated our implied take rate to be slightly higher during the year, driven by our monetization
   (CFO prepared-remarks outlook block, not Q&A)
B17 / 4. route union replay
   published (.12/.80/.50/.06, rho .5) 0.4824 (model 0.4812) | strict x0.55 0.3342 (model 0.3344)
   audit     (.13/.65/.52/.06, rho .5) 0.4263 | strict 0.3080
B17 / 5. section 9 arithmetic, the R04 mirror, and the team's own FY26 take rate
   FY26 -30 rev / -27 ebitda -> -0.114pp (log -0.2) | FY27 -170 / -153 -> -0.601pp (log -1.0)
   R04 mirror +23 rev / +20.7 ebitda -> +0.080pp ; R04 publishes 0.09 (computed correctly there)
   R04 revision 2 p 0.52 (B17 claim 7 quotes 0.58) | C11 revision 2 p 0.76
   team FY26 implied take rate 13.535% vs FY25 13.407% = +12.8bp -- management guides 'relatively flat'
   R04-style split of the Yes mass -> E[stock|Yes] -2.50 ; EV at p 0.38 = -0.95 (log -6 and -2.5)
==============================================================================
Batch register
  B08  rev 1 p 0.38 ci [0.25, 0.52] | anchor 0.63 flag False | stock -4 EV -1.5 material True | EV check -1.52
  B09  rev 1 p 0.10 ci [0.05, 0.2] | anchor 0.16 flag True | stock -3 EV -0.3 material False | EV check -0.30
  B10  rev 1 p 0.05 ci [0.02, 0.1] | anchor 0.11 flag True | stock -2 EV -0.1 material False | EV check -0.10
  B17  rev 1 p 0.42 ci [0.28, 0.56] | anchor 0.50 flag True | stock -6 EV -2.5 material True | EV check -2.52
```
