# A2 — Guide surprise, re-run under the harness convention (subagent, alone; Gate 2)

**Role in Lane 2:** the decision-relevant test. Lane 1's A returned 0/14, 0/10 because its brief said "strictly before the guide date";
`CONVENTION.md` §1–§3 restores the harness's own rules, under which every one of the 14 W1 letters is evaluable. Your note must be clean
before the parallel block starts. A clean negative is a result; an empty sample is not.

## Files this agent reads
- `docs/thesis-kernel-topdown/lane2/CONVENTION.md` (first), `analysis/src/forecast_methods/kernel_engine_v2/README.md` and the module (import it;
  never re-derive λ; it refuses same-day inputs by design — call it with `as_of = d + 1 day` for the letter dated `d`, or use its post-letter
  path, and state which in the note)
- `data/processed/forecast_methods/harness/calendar.csv`, `targets.csv`; `data/processed/overnight/02_guidance_ledger.csv`,
  `16_consensus_at_print_merged.csv`; `data/processed/forecast_methods/L0/L0_vintage_register.csv`
- `data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv` (the only source of return legs)
- `data/processed/forecast_methods/alpha_a/pit_cells.csv` and `post_letter_diagnostic.csv` — to reconcile your cell counts with Lane 1's
  exclusions only; not inputs, not results

## Task
Build `alpha_a2/`. Universe: the 14 W1 letters (targets 2023Q1–2026Q2; W2 = the 10 from 2024Q1); an extension to the 2021Q4–2022Q4 letters
is a flagged sensitivity (older vendors; `vendor_attributed = False` rows excluded from the headline).

For each letter `d` (prints quarter q, guides q+1):
- **K_d** = kernel-implied guide midpoint for q+1 = λ_season(q+1) × [⅔ GBV_q + ⅓ GBV_{q−1}] ÷ (1 + trailing-8 cushion), with λ and the cushion
  fitted on prints ≤ d (PIT, nested selection as K0 v2 does it; report the ex-COVID variant beside the default).
- **C_d** = pre-guide Street for q+1: the L0 `PG-<q+1>-revenue` row (or `16_consensus…next_q_cons_revenue_musd`) with `as_of_timestamp = d`,
  `pit_usable = True`, vendor kept in a column.
- **S_d** = K_d / C_d − 1 (%). **G_d** = actual guide midpoint for q+1 issued at d. **gap_d** = G_d / C_d − 1.
- **Returns**: `excess_open_{1,5,20,60}d_pct` for event `d` (entry at the open of d+1).

Evaluation (i) — mechanism: sign(S_d) vs sign(gap_d) on |S_d| > 1pp cells; hit-rate with Wilson 95%; permutation p on sign labels (9,999,
seed 20260913); corr(S, gap) with a length-2 block bootstrap (2,000). Expanding ridge of gap on S, slope shrunk toward 1, ≥ 6 prior pairs.
Evaluation (ii) — trade: mean `excess_open_20d_pct` (and 1/5/60) conditional on sign(S) and on |S| > 1pp; direction-adjusted pooled mean
sign(S)×return; bootstrap 90% intervals; both windows.
Controls (the mechanism refuter will demand them): partial correlation of S with `excess_open_20d_pct` controlling for (a) the GBV surprise at
d — printed GBV_q vs the at-print GBV consensus (`cons_gbv_busd` / L0 `AP-<q>-gbv`) where it exists, (b) the raw guide gap, (c) the revenue
surprise at print. Baselines as strategies: the guide-gap-only rule (trade sign(gap)), the zero rule, previous-surprise sign.
Live row: S for the 5 Nov 2026Q4 guide against the September `current` consensus rows (LSEG-family, S&P, Zacks; vendor + stamp; count the
LSEG family once), dated RUN_DATE, labelled scenario.

## Pass line (pre-registered — copy verbatim into the note before running)
PASS only if, on BOTH W1 and W2: (1) sign hit-rate ≥ 70% on |S| > 1pp cells with at least 6 such cells; (2) the direction-adjusted mean
`excess_open_20d_pct` is positive with a bootstrap 90% interval excluding zero; (3) the partial correlation of S with `excess_open_20d_pct`,
controlling for the GBV surprise and the raw guide gap, keeps the sign of the raw correlation. Fewer than 6 cells in either window → underpowered.
(1) met and (2) or (3) not → "partial: mechanism confirmed, trade unproven". The first paragraph of the note answers: may the memo claim an
expectations edge on the guide? — yes / no / partial / underpowered.

## Outputs (all new files)
`analysis/src/forecast_methods/alpha_a2/` (run.py exit 0, README, ≥ 8 tests) · `data/processed/forecast_methods/alpha_a2/`: `cells.csv` (one row
per letter: every input, vendor, stamp, availability reason), `statistics.csv`, `conditional_returns.csv`, `controls.csv`, one figure (S vs gap;
S vs 20-day return) · registry `alpha-a2__guide_mid_next_q` (target `guide_mid`, quarter q+1, vintage d, point K_d, q05–q95 from the cushion
residuals, both replays, W1/W2) + the LIVE 2026Q4 row at RUN_DATE via `harness_v1_1` · note `05_backtests/ALPHA_A2_GUIDE_SURPRISE_V2.md`.

## Do not
Use `role = current` rows at a historical date · use close-based or `gap_pct` returns · drop a letter silently (if the kernel is undefined at a
letter — e.g. no admissible same-season λ observation — record the reason; it is "unavailable", not a miss) · reinterpret Lane 1's 11-point
post-letter diagnostic as your result · tighten the convention back to "strictly before d".

## Report back (final message; ≤ 250 words)
Cells evaluable per window; hit-rate with Wilson and counts; permutation p; the conditional 20-day mean with interval; the partial correlation
after controls; the live 5 Nov row; the verdict in one word.

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
