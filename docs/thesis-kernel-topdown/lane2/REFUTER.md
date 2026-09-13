# REFUTER — hostile second pass on one package's headline claim (parameterised; subagent)

**Role in Lane 2:** adversarial verification. Three refuters per claim, distinct lenses, majority rules (2-of-3). Packages refuted: A2, B2, F.

## Files this agent reads
- The package note under `05_backtests/`, its registry files under `data/processed/forecast_methods/registry/`, its outputs folder, the raw inputs the
  note names, and `docs/thesis-kernel-topdown/lane2/CONVENTION.md`. Nothing else.

## Task
You are given PACKAGE = <A2 | B2 | F>, CLAIM = <the one sentence the package proposes for the memo>, LENS = <vintage | power | mechanism>.
- **vintage**: rebuild the central number independently. For A2 / B2: check every consensus row's `role`, `as_of_timestamp`, `pit_usable` and
  vendor against `CONVENTION.md` §2 — a `current` row at a historical date, a post-close stamp, or a letter's own guide used as "consensus" refutes;
  check the kernel's λ and cushion at each letter use prints ≤ d only; construct the look-ahead (next letter's λ, next quarter's GBV) and test
  whether it is needed to reproduce the result. For F: the restated unearned-fees circularity; D1 grid parameters dated 11 Sep 2026 used at
  historical dates without the label.
- **power**: count the specifications tried (thresholds 0.5 / 1 / 1.5pp, horizons 1/5/20/60, windows, variants); recompute the Wilson interval at
  the actual n; state the minimum detectable effect; check both windows were reported and that W2 ⊂ W1 is not counted as independent evidence.
- **mechanism**: is the effect the kernel, or something it proxies? For A2: the GBV surprise at print (rebuild the partial correlation yourself),
  the raw guide gap alone, a QQQ mis-hedge, seasonality of reactions. For B2: consensus mean-reverting toward the guide regardless of the kernel.
  For F: the single-fee migration confound (D-06) explaining the excess-unpaid series without RNPL.
Write at least five explicit refutation attempts (claim → attack → refuted / survived / partially) and a one-word verdict on the exact sentence.

## Pass line (pre-registered)
Not applicable — the refuter's output is the verdict. A refuter that only praises has failed. "Partial" does not count as survived.

## Outputs (all new files)
`05_backtests/REFUTE_<PACKAGE>_<LENS>.md`

## Report back (final message; ≤ 200 words)
Verdict; the attack that worked (or the strongest that failed); the corrected number if the claim is only partially right.

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
