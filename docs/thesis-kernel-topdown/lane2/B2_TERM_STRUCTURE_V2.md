# B2 — Kernel term structure, free-data version under the convention (subagent)

**Role in Lane 2:** Thesis B′. Lane 1's B′ was empty for the same wording reason as A and because the FY ledger holds % buckets, not dollars.
This version uses targets the repo actually has at every letter.

## Files this agent reads
- `docs/thesis-kernel-topdown/lane2/CONVENTION.md` (first); `analysis/src/forecast_methods/kernel_engine_v2/` (import; same as A2)
- `data/processed/forecast_methods/harness/calendar.csv`, `targets.csv`; `data/processed/overnight/02_guidance_ledger.csv`,
  `02_fy_guide_revisions.csv`, `16_consensus_at_print_merged.csv`; `data/processed/forecast_methods/L0/L0_vintage_register.csv`
- `data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv`

## Task
Build `alpha_b2/`. At each W1 letter `d` (prints q, guides q+1):
- **Term structure**: K(q+1) as in A2; K(q+2) = λ_season(q+2) × [⅔ GBV_{q+1}^nowcast + ⅓ GBV_q] ÷ (1 + cushion), with GBV_{q+1}^nowcast = GBV_q × (1 + trailing-4 y/y)
  (state it; report a w-band 0.33–⅔ as arithmetic sensitivity, not a fitted alternative).
- **Predictors**: S1_d = K(q+1)/C_d(q+1) − 1 (as A2); S2_d = K(q+2)/C_d(q+2) − 1 where a pre-guide consensus for q+2 exists at d (else unavailable);
  T_d = kernel FY_d / FY anchor_d − 1, where kernel FY = printed quarters + K(q+1) + K(q+2) + seasonal naive beyond, and the FY anchor is the
  FY-guide bucket midpoint converted to dollars on prior-year revenue (explicitly a sensitivity — buckets are % ranges).
- **Targets available at every letter**: (T1) the revision of next-quarter consensus over the following quarter,
  R_d = C_{d'}^{at_print}(q+1) / C_d^{pre_guide}(q+1) − 1 with d' the next letter — does consensus drift toward the kernel?; (T2) the FY-guide bucket
  change at d' (up / same / down) from `02_fy_guide_revisions.csv`; (T3) `excess_open_60d_pct` (and 20d) for event d.
- Statistics: sign hit-rate with Wilson on |S1| > 0.5% (and |T| > 0.5%) cells, permutation p, corr with block-bootstrap interval, both windows;
  baselines: no-revision (random walk), last revision continues.
- **Current term structure table**: 4Q26 and 1Q27 kernel ranges (w = 0.33 / 0.5 / ⅔) beside today's stamped `current` consensus (vendor + stamp;
  LSEG family counted once) — LIVE only.

## Pass line (pre-registered — copy verbatim into the note before running)
PASS only if on BOTH windows: S1 predicts the sign of R_d on ≥ 70% of |S1| > 0.5% cells with ≥ 6 cells, and corr(S1, R_d) > 0.4. T2 and T3 are
reported, not gating. Fewer than 6 cells → underpowered. Verdict word in the first paragraph.

## Outputs (all new files)
`analysis/src/forecast_methods/alpha_b2/` (run.py, README, tests) · `data/processed/forecast_methods/alpha_b2/` (cells, statistics, the term-structure
table) · registry `alpha-b2__revenue_q_plus_2` (target `revenue_musd`, quarter q+2, horizon 2, vintage d, both replays, W1/W2 — a genuinely new
scoreable object against the naive baseline) + LIVE rows for 2026Q4 and 2027Q1 at RUN_DATE via `harness_v1_1` · note
`05_backtests/ALPHA_B2_TERM_STRUCTURE_V2.md`.

## Report back (final message; ≤ 250 words)
Cells per window; hit-rate with Wilson; corr with interval; T2 and T3 summaries; the current 4Q26 / 1Q27 table; the verdict.

## Rules that bind this agent (do not skip)

- **Read only:** this file, `docs/thesis-kernel-topdown/lane2/CONVENTION.md`, `docs/thesis-kernel-topdown/03_NUMBERS_CHEATSHEET.md`,
  `analysis/src/forecast_methods/harness/README.md`, `analysis/src/forecast_methods/harness_v1_1/README.md`, and the files named above.
  Nothing else unless a step says so (token discipline).
- **Copy, never overwrite.** New folder under `analysis/src/forecast_methods/`, new outputs under `data/processed/forecast_methods/`, registry
  files only under a NEW method name, your note as a NEW file under `docs/revenue-forecast-strategy/05_backtests/`. Never edit `harness/`,
  `harness_v1_1/`, `L0/` (append-only with a dated backup — only M may append), another package, `20_frozen_q3_2026.csv`, `research/thesis.md`,
  or any tracked data file.
- **Point-in-time as defined in `CONVENTION.md`** — a guide-date vintage includes that letter; morning-of-print consensus is pre-letter;
  `role = current` rows never appear at a historical date; executable returns are `excess_open_*` from `returns_v1`. Windows W1 (1Q23+, 14)
  and W2 (1Q24+, 10), both; letter integers scored as [x−0.5, x+0.5].
- **Pre-register the pass line** (below) in your note before running; publish a failure as a result. n < 6 evaluable cells in either window is
  "underpowered", never "pass".
- **Register through `harness_v1_1.registry.register`** (W1/W2 rows: guide-date vintages, both replays PIT and full_sample; LIVE rows: vintage
  = RUN_DATE). Do not run either scorer — the parent does at CLOSE.
- **Your own new test has a bug?** Fix it once, keep the failing output in your outputs folder as a receipt, say so in the note. Do not stop.
  A failing *frozen* test (harness / L0) is a STOP.
- **Portable commands:** `python` from `.venv`, run from the repo root, paths via `pathlib`.
- **No decisions, no kill-list numbers, no credentials, no licensed data in git, nothing that touches airbnb.com** (only L, and only if
  sanctioned). The eleven team decisions are in `docs/revenue-forecast-strategy/AGENT_BRIEF.md` §3; the kill list in §6.

## Note template

```
# <ID> — <title>          agent · date · branch · time spent
## Verdict (plain language, first): pass / fail / partial / underpowered vs the pre-registered line
## Pre-registered pass line (verbatim, with the timestamp it was written)
## What ran: exact commands, exit codes, wall time
## Results: tables with n on every row; PIT vs full-sample labelled; vendor + timestamp on every consensus number
## What failed or could not be done, and why
## Interpretation (honest)
## RESUME: one paragraph for the next agent
```
