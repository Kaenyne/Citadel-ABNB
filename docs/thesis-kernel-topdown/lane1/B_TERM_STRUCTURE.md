# B′ — Term structure: kernel FY range vs management's FY-guide revisions (free-data variant)

**Role in Lane 1:** Tests whether the kernel's two-quarter term structure anticipates revisions. Swaps to real FY consensus when the LSEG export exists.

## Files this agent reads
- `analysis/src/forecast_methods/kernel_engine_v1/`
- `data/processed/overnight/02_fy_guide_revisions.csv`, `02_guidance_ledger.csv`, `16_consensus_at_print_merged.csv`, `L0_vintage_register.csv`
- `data/processed/abnb_earnings_reactions.csv` (`open_*` only)
- `docs/thesis-kernel-topdown/prompts/WP-B_term_structure.md`

## Task
Build `alpha_b/`. At each print date t: kernel_FY = printed quarters + kernel(q+1) + kernel(q+2) + seasonal naive beyond; T = kernel_FY −
(the FY guide midpoint in force at t; and FY consensus where a vendor-stamped value exists — flag vintages older than 30 days). Targets:
the direction of management's NEXT FY-guide revision; realised FY revenue; 20/60-day executable returns. Baselines: no revision; last
revision continues. Also emit today's term structure: 4Q26 and 1Q27 kernel ranges with the kernel-weight band (w 0.33 … ⅔) against the
stamped consensus.

## Pass line (pre-registered)
T predicts the sign of the next FY-guide revision in ≥ 70% of dates with |T| > 0.5%, and corr(T, revision) > 0.4 on both windows; the honest n
for the return leg (≈10) is stated.

## Outputs (all new files)
`alpha_b/` · registry `alpha-b__fy_gap_at_print` · `05_backtests/ALPHA_B_TERM_STRUCTURE.md` with the current term-structure table

## Report back (final message; ≤ 250 words)
Hit-rate and correlation on both windows with n; the current 4Q26 / 1Q27 kernel ranges vs consensus; what changes when LSEG history arrives.

## Rules that bind this agent (do not skip)

- **Read only:** this file, `docs/thesis-kernel-topdown/03_NUMBERS_CHEATSHEET.md`, `analysis/src/forecast_methods/harness/README.md`, and the
  files named below. Nothing else unless a step says so (token discipline).
- **Copy, never overwrite.** New folder under `analysis/src/forecast_methods/`, new outputs under `data/processed/forecast_methods/`, registry
  files only under a NEW method name, your note as a NEW file under `docs/revenue-forecast-strategy/05_backtests/`. Never edit `harness/`,
  `L0/`, another package, `20_frozen_q3_2026.csv`, `research/thesis.md`, or any tracked data file.
- **Point-in-time.** Refit at guide dates; consensus only from `data/processed/forecast_methods/L0/L0_vintage_register.csv` (vendor + timestamp
  before the date); windows W1 (1Q23+) and W2 (1Q24+), both; letter integers scored as [x−0.5, x+0.5].
- **Pre-register the pass line** (below) in your note before running; publish a failure as a result.
- **Portable commands:** use `python` from the project venv (`.venv`), never a machine-specific path. Run from the repo root.
- **No decisions, no kill-list numbers, no scraping, no credentials, no licensed data in git.** The eleven team decisions are in
  `docs/revenue-forecast-strategy/AGENT_BRIEF.md` §3; the kill list in §6.

## Note template

```
# <ID> — <title>          agent · date · branch · time spent
## Verdict (plain language, first): pass / fail / partial / underpowered vs the pre-registered line
## What ran: exact commands, exit codes, wall time
## Results: tables with n on every row; PIT vs full-sample labelled; vendor + timestamp on every consensus number
## What failed or could not be done, and why
## Interpretation (honest)
## RESUME: one paragraph for the next agent
```
