# B2 — Kernel term structure under the Lane 2 convention

Codex B2 subagent · 2026-09-13 · branch `codex/lane2-full` · packages: new `alpha_b2/` only.

## Verdict

PENDING: the pass line is recorded before running the analytical test. No performance claim is made at preregistration.

## Pre-registered pass line

Recorded 2026-09-13 before model execution:

PASS only if on BOTH windows: S1 predicts the sign of R_d on ≥ 70% of |S1| > 0.5% cells with ≥ 6 cells, and corr(S1, R_d) > 0.4. T2 and T3 are
reported, not gating. Fewer than 6 cells → underpowered. Verdict word in the first paragraph.

Fixed before testing: weights 0.33, 0.5, and 2/3; headline 2/3. The prescribed GBV extrapolation is GBV(q+1) = GBV(q) × (1 + mean of the last four available GBV year-over-year growth rates). For the LIVE Q1 2027 extension, persist the same growth for a second successive quarter. These are arithmetic assumptions, with no fitted GBV coefficients. Lambda is imported from `kernel_engine_v2`, never re-estimated locally. The non-seasonal extrapolation can distort quarterly levels and must be shown as such.

S1 and consensus revision are in percent. The primary correlation uses all evaluable paired S1/revision cells; sign hit rate uses |S1| > 0.5%. Wilson intervals are 95%; a fixed-seed 10,000-draw permutation test permutes revision outcomes, and a fixed-seed 10,000-draw paired moving-block bootstrap uses two consecutive events for the correlation interval. These are descriptive diagnostics for a short, dependent time series. No-revision and last-observed-revision baselines are evaluated on matched cells; zero is a distinct sign, not automatically a correct call. Current consensus roles never enter historical predictors or targets. Missing fiscal-year buckets or q+2 consensus remain missing.

## What ran

Preregistration only. Execution receipts and results will be added in a new companion result note to preserve this file.

## RESUME

Execute the fixed alpha_b2 specification and tests, retain failures, register through FORMAT 1.1, and report complete results in `ALPHA_B2_TERM_STRUCTURE_V2_RESULTS.md`. The parent runs both scorers and updates the shared workboard after registration.
