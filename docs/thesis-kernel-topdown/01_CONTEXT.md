# 01 · Context for the kernel thesis

## The mechanism, precisely

- **GBV** (gross booking value) is recorded when a guest books, net of cancellations and alterations processed in the period.
- **Revenue** is recognised when the guest checks in. The Airbnb fee on paid-but-not-stayed bookings sits in **unearned fees**;
  the host's share sits in **funds payable**. Together they are the *paid* backlog. RNPL bookings are in neither (no cash yet).
- **Kernel:** `revenue_q = c_s × Σ_k φ_k GBV_{q−k}`. The published operating form is `λ_season × [⅔ GBV_{q−1} + ⅓ GBV_{q−2}]`
  with λ Q1 12.66 / Q2 13.71 / Q3 17.24 / Q4 12.03 % (2023–26 means; Q4 range 0.17pp). Reproduce it before anything else —
  it is the acceptance test of every package that touches revenue.
- **What ⅔ / ⅓ means.** From booking lead times (K2, 268k reservations with real booking dates): of the part of a quarter's
  revenue booked *before* the quarter starts, ~70% was booked in the previous quarter and ~30% earlier. That is the ⅔ / ⅓.
  It is NOT the split of the whole quarter: ~40% of a quarter's revenue is booked in-quarter (φ₀ 0.36–0.39 from the ledger,
  0.46–0.56 from booking data). From the ledger alone φ₁ and φ₂ are not separately identified (bootstrap corr −0.5 to −0.9);
  their sum is 0.58–0.64; ⅔ is also the point-in-time optimal weight (0.65–0.70).
- **Paid vs booked, at quarter start (next quarter's revenue):** Q3 35% paid / 32% booked-unpaid / 33% not yet booked;
  Q4 30 / 27 / 42. A quarter's GBV converts to ~14.1% of itself in revenue over its lifetime.
- **Guide:** `guide_mid = E[revenue] ÷ (1 + c)`, c = trailing-8 actual/guide-midpoint (mean +1.86%, median +1.79%, sd 1.006pp).
  Range width 1.7–2.2% of midpoint. Airbnb beat its own midpoint 19/19, the top of the range 15/19.
- **Street:** at-print consensus sits ~+0.5% above the guide midpoint (κ). The guide-vs-Street gap has sd ≈ 2.5pp; the
  print-vs-guide surprise sd ≈ 1.1pp. That asymmetry is the expectations edge (Thesis A tests whether it is tradeable).
- **Multiple:** ABNB's EV/EBITDA moves +0.48 turns per point of forward revenue growth; margin explains nothing. Fair exit
  band 13.5 / 16.5 / 18.5x; football field base $154–157 vs $181.94 spot (4 Sep 2026).

## RNPL — the variable

- Reserve Now, Pay Later: ~21% of GBV; no payment at booking; "higher cancellation rates than historic bookings" (2Q26 10-Q MD&A).
- Rollout: US 3Q25 (laps 3Q26); UK 18 Feb, Australia / APAC 23 Feb, Canada 4 Mar 2026 (laps 1Q27, partial). The "bundle"
  (RNPL + cancellation redesign + total-price display) was worth "over 200bps nights / ~300bps GBV" in 4Q25 and ~3 pts / ~4 pts in 1Q26.
- Balance sheet: excess unpaid share of the backlog vs the pre-RNPL norm **+2.0 (4Q25) → +8.1 (1Q26) → +9.7pp (2Q26)**;
  unpaid share u = 6–16% of the backlog ($1.6–4.7bn; 7–19M live unpaid nights at 30 Jun 2026); migration share m ≈ 8%.
- In the kernel: `revenue_q = c_s Σ φ_k GBV_{q−k} × (1 − L_q)`, L = RNPL share × differential cancellation ≈ 0.2–1.4%
  → −$8M to −$67M on 3Q26. 1H26 λ shows no break yet.
- **λ control rule for 5 Nov:** λ_Q3 = revenue ÷ $27,867M; < 17.09% (revenue < $4,761M) warning; < 16.93% ($4,719M) escalate.
- Re-based nights (Theo): 3Q26 +9.3% (band 8.8–9.8) vs team +9.9%; 4Q26 +7.6% (7.2–8.1) vs +8.9%; ex-NA lap question 8.0–8.2%.
- Open: which line carries the FX confound — K1 says unearned fees is FX-clean and funds payable is confounded; Theo's note
  says the reverse. WP-F resolves it (decision D-06).

## The pitch skeleton (what every package feeds)

1. Mechanism (above). 2. Composition: FY26→FY27 halving = dollar lap (4Q26 revenue FX ≈ +1.0pp as an *output*; the −3.4pp
subtraction double counts) + bundle lap + mix identity (geo −1.1 to −1.5pp; unit size +0.63pp at bedroom elasticity 0.23, not +2pp;
LOS +0.04; seats −0.5pp; like-for-like price + sub-regional mix +2.8–3.6pp **unidentified**). 3. Trade and flip rule: short, $157;
the 5 Nov guide is a coin toss vs the broad panels (P below 0.49–0.50) and below vs Zacks (0.63); the asymmetry is the 3Q26
take rate read *with* GBV — cover and go long if take rate ≥ 18.10% on GBV ≥ $26.3bn AND Q4 nights "low double digit"; add if
λ_Q3 < 16.93% or nights "high single digit". 4. RNPL is the bear engine.

## The eleven team decisions (humans decide; agents lay out options)

D-01 3Q26 revenue card value: guide+cushion $4,816M vs kernel $4,804M · D-02 nights: reviews index (+9.5–10.0%) vs team baseline
(+9.9%) · D-03 ADR card v2 (+3.0%) quoted with its failed naive test · D-04 which 3Q26 **block** to register (recommended block ii:
147.38M nights / $180.15 ADR / $26,550M GBV; the object-by-object hybrid breaks the identity by −3.1pp) · D-05 stated 3Q26 FX:
lag-loaded spec → predict ≈ +3 · D-06 which balance-sheet line is FX-clean · D-07 no-fee-step Q4 guide as headline · D-08 adopt the
ex-NA lap (Q4 nights 8.0–8.2%) · D-09 predictive sd 3.03% conditional · D-10 one funds-payable refutation condition (two incompatible
versions exist) · D-11 the 4Q26 ex-NA lap chained with the 1Q27 lap double-counts ~0.8pp.

## Kill list — never quote as ours

The −3.4pp Q4 FX step · "82% of Q4 FX already determined" · "+4.05% fee uplift" as measured (θ is unidentified; +1.1–1.8% at θ 0.83) ·
the 9/9 guide-below-Street drift rule as a signal · "half of ADR growth is bigger units" · any FY27 level edge without the
+9.2–11.5% band · any p-value for the drift rule · restated unearned fees `reported/(1−d)` as a pin or feature (circular) ·
the 1.71M quote panel as "fee-inclusive" (it is listed price only) · "nothing beats guide × cushion" (say: no single object beats
it on both windows) · mixing a September consensus value into a historical guide date · calendar blocked-rate curves as
booking-lead-time evidence (U-shaped past ~90 days; they measure blocks).

## Where the evidence lives (all paths from the repo root)

`docs/revenue-forecast-strategy/05_backtests/`: `K1_KERNEL_WEIGHTS_AND_BACKLOG.md`, `K2_KERNEL_FROM_LEAD_TIMES.md`,
`kernel-lambda.md`, `guidance-policy.md`, `B1_TAKE_RATE_RECONCILIATION.md`, `B2_Q4_GUIDE_EXHIBIT.md`, `B3_FY27_DECOMPOSITION.md`,
`B4_FX_EXHIBIT.md`, `A1_consensus_vintages.md`, `A3_fee_panels.md`, `PREREG_ABNB-INT-v1.md`, `RED_TEAM.md`, `SCOREBOARD_v2.md`.
Plan and synthesis: `docs/revenue-forecast-strategy/04_synthesis/00_INTEGRATED_SYSTEM.md`, `07_MORNING_REPORT.md`, `AGENT_BRIEF.md`.
Team context from other workstreams: `docs/q3nowcast/SYNTHESIS.md` (reviews stays index), `docs/adrq3/SYNTHESIS.md` (ADR card v2),
`docs/overnight2/SYNTHESIS.md` (RNPL ledger, ex-NA lap), `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md`,
`docs/overnight/FINAL_SUMMARY.md` (valuation, the 3,500-test record).
