# L — Airbnb policy monitor: RNPL, fees, cancellation (subagent; internet; **requires Theo's sanction**)

SANCTIONED_BY_THEO: no

**Parent: spawn this agent only if the line above reads `SANCTIONED_BY_THEO: yes (date)`.** Fetching Help Center / Newsroom pages touches
airbnb.com; AGENTS.md rule 6 makes that a human terms-of-service decision. Reading ~10 public pages weekly with a real User-Agent, one request per
page per run, is what is being sanctioned — nothing else.

## Files this agent reads
- `docs/thesis-kernel-topdown/prompts/WP-L_policy_monitor.md` (the full spec); `research/sources/README.md` (S66–S71, the fee-deadline sources)

## Task
Write `analysis/src/acquisition/policy_monitor.py` (new file): fetch the listed public pages (Help Center 1857 and 4095; Resource Center 771 and 746;
the Newsroom pages on Reserve Now Pay Later and cancellation policy; the host fee page; add any the fee-deadline sources cite), store the text under
`data/manifests/policy_monitor/<UTC date>/`, diff against the previous capture, and append every change (date, URL, changed sentences) to
`data/manifests/policy_monitor.log`. Polite rate, real User-Agent, no login. Provide a launchd plist **template** whose StandardOutPath /
StandardErrorPath live under `$HOME` (never inside the OneDrive repo — an agent logging into the repo folder never spawns: exit 78) and a README;
Theo installs it.

## Pass line (pre-registered — copy verbatim into the note before running)
First run stored with a manifest; a deliberate test diff detected; the plist template validated with `plutil -lint`; every date the team cites for
fees / RNPL has a log entry with the sentence.

## Outputs (all new files)
`analysis/src/acquisition/policy_monitor.py` + README + plist template · `data/manifests/policy_monitor.log` · note `05_backtests/L_POLICY_MONITOR.md`.

## Report back (final message; ≤ 150 words)
Pages captured; the test diff; the install command for Theo; the verdict.

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
