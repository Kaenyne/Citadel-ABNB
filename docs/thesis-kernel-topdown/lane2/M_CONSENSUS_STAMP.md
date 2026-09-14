# M — Consensus re-stamp (subagent; internet; the one agent allowed to append to the L0 register)

**Role in Lane 2:** every live number in the memo needs a vendor and a timestamp. This agent adds today's rows and, for A2 / B2's future use,
any nights / ADR / GBV consensus a vendor shows.

## Files this agent reads
- `docs/thesis-kernel-topdown/prompts/WP-M_consensus_stamp.md` (the full spec); `data/processed/forecast_methods/L0/L0_vintage_register.csv`
  (header comments included — they carry the hard rule); `analysis/src/forecast_methods/L0/test_l0.py` (what a valid row must satisfy)

## Task
1. Back up first: copy the register to `data/processed/forecast_methods/L0/backups/L0_vintage_register_<UTC timestamp>.csv` (new file).
2. Capture the current revenue consensus for 3Q26, 4Q26, FY26, FY27 (and 1Q27 / FY28 if shown): `yfinance` `Ticker("ABNB").revenue_estimate`
   and `earnings_estimate` (LSEG family — count once with Yahoo / Alpha Vantage), the Zacks detailed-estimates page, StockAnalysis (S&P). Also EPS,
   adj. EBITDA, and nights / ADR / GBV wherever a vendor prints them. Alpha Vantage only if `ALPHAVANTAGE_API_KEY` is in the environment.
3. Append rows with `role = current`, real `as_of_timestamp` (UTC, to the minute), vendor, `n_estimates`, url, `capture_method`, `pit_usable = True`,
   `vendor_attributed = True`. Never touch an existing row. Never place a September value at a historical date.
4. Run `python -m pytest analysis/src/forecast_methods/L0 -q` — it must stay green; if your rows break a test, fix your rows, not the test.

## Pass line (pre-registered — copy verbatim into the note before running)
Every new row has vendor + timestamp + n; the 6 Aug 2026 LSEG $4,610M row is byte-identical; the backup exists; row counts before / after are in
the note; the L0 tests pass after the append.

## Outputs
Register rows (the only sanctioned modification of a tracked data file in this lane) · the backup · note `05_backtests/M_CONSENSUS_<UTC date>.md`.

## Report back (final message; ≤ 150 words)
Rows added by vendor and period; the 4Q26 revenue consensus per vendor with timestamps; any nights / ADR / GBV rows found; test result.

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
