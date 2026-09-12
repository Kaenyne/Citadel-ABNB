# A — Guide surprise: does the kernel predict the guide better than the Street?

**Role in Lane 1:** The decision-relevant test. Gate 2: its note must be clean before the expensive tail starts.

## Files this agent reads
- `analysis/src/forecast_methods/kernel_engine_v1/` (import it; never re-derive λ)
- `data/processed/overnight/02_guidance_ledger.csv`, `16_consensus_at_print_merged.csv`, `04_consensus_at_print.csv`
- `data/processed/forecast_methods/L0/L0_vintage_register.csv`
- `data/processed/abnb_earnings_reactions.csv` (use `open_*` columns only — executable next-open entry)
- `docs/thesis-kernel-topdown/prompts/WP-A_guide_surprise.md` (the full spec)

## Task
Build `alpha_a/`. For each guide date d on W1 (extend to 19–23 with older, flagged vendor-stamped consensus): S = kernel_guide(q+1, as_of=d)
− consensus(q+1, latest vintage before d), in % of consensus, vendor column kept. Targets: (i) sign and size of actual guide midpoint −
consensus; (ii) executable 1/5/20-day returns conditional on sign(S) and on |S| > 1pp. Statistics: hit-rate with a Wilson interval; a
permutation test on the sign labels; an expanding-window regression of the actual gap on S with the slope shrunk toward 1 (ridge) and a
block-bootstrap CI; conditional 20-day mean returns with bootstrap CIs. Baselines: zero; previous surprise sign; the same rule with
consensus as the base. Live row: S for the 5 Nov Q4 guide against LSEG-family ~$3,159M, S&P $3,160M, Zacks $3,200M.

## Pass line (pre-registered)
Hit-rate ≥ 70% on |S| > 1pp cells on BOTH windows AND the conditional 20-day executable return has the predicted sign on both. Report the
number of |S| > 1pp cells; if fewer than 6, the verdict is "underpowered", not "pass". The first paragraph of the note answers:
may the memo claim an expectations edge on the guide? — yes / no / underpowered.

## Outputs (all new files)
`alpha_a/` · registry `alpha-a__guide_gap_next_q` (PIT rows) + the live row · one figure (S vs actual gap) · `05_backtests/ALPHA_A_GUIDE_SURPRISE.md`

## Report back (final message; ≤ 250 words)
Hit-rate with Wilson interval and cell counts on W1 and W2; permutation p; slope CI; conditional 20-day return with CI; the live 5 Nov row; the verdict.

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
