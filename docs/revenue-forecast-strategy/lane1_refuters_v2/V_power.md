# REFUTER — hostile second pass on one package's headline claim (parameterised)

**Role in Lane 1:** Adversarial verification. Three refuters per claim in FULL, with distinct lenses; one on A in CORE. Majority rules.

## Files this agent reads
- The package note under `05_backtests/`, its registry files under `data/processed/forecast_methods/registry/`, and the raw inputs the note names. Nothing else.

## Task
You are given: PACKAGE = <A | B′ | R | V>, CLAIM = <the one sentence the package wants in the memo>, LENS = <vintage | power | mechanism>.
- lens **vintage**: rebuild the central number independently; try to construct a consensus splice or a look-ahead (data printed on/after the
  vintage date) that would reproduce the claimed result; check every vendor column and every `as_of`.
- lens **power**: count the specifications tried (variants, windows, thresholds); recompute the interval honestly (Wilson / bootstrap);
  state the effect size detectable at the actual n; check both windows were reported, not the better one.
- lens **mechanism**: is the effect the kernel, or something the kernel is proxying (seasonality, the cushion alone, a vendor artefact)?
  Construct the simplest alternative that explains the same numbers.
Write at least five explicit refutation attempts (claim → attack → refuted / survived / partially) and a verdict.

## Pass line (pre-registered)
Not applicable — the refuter's output is the verdict. A refuter that only praises has failed.

## Outputs (all new files)
`05_backtests/REFUTE_<PACKAGE>_<LENS>.md`

## Report back (final message; ≤ 250 words)
Verdict; the attack that worked (or the strongest that failed); the corrected number if the claim is only partially right.

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

## Assignment

PACKAGE = V

CLAIM = Using the final FY27 base model, 16.5x adjusted EBITDA implies a $180.88 12-month target, while the existing six-lens base football-field mean is $156.79; these are different valuation objects.

LENS = power

Package note: docs/revenue-forecast-strategy/05_backtests/V_VALUATION_RECONCILIATION.md. Read only this note, its actual registry files if any, and its named raw inputs. Do not read other package code or derived outputs. Independently recompute the central count, price bridge or statistic relevant to your lens. Write only docs/revenue-forecast-strategy/05_backtests/REFUTE_V_power.md. Parent owns board, scorer and git operations. Include at least five numbered attacks, each with explicit claim, attack, result, and evidence. Give one final verdict exactly survived / refuted / partial on the original exact sentence. Partial does not count as survived. Do not substitute a weaker sentence silently. Distinguish arithmetic sensitivity from statistical estimation; if W1/W2 or power are not applicable to a conditional arithmetic identity, explain that boundary instead of inventing statistical support. Record exact commands, runtime if available, and tokens only if available.
