# CLOSE — score, assemble memo-ready claims, update the board, push (run by the parent, never a subagent)

**Role in Lane 2:** only claims that survived 2-of-3 refuters reach the memo; everything is pushed even if the PR cannot be opened.

## Files this agent reads
- every Lane-2 note and REFUTE file written in this run; `data/processed/forecast_methods/registry/`; `docs/revenue-forecast-strategy/WORKBOARD.md`

## Task
1. `python analysis/src/forecast_methods/harness/score.py` (frozen) then `python analysis/src/forecast_methods/harness_v1_1/score.py`. If any
   W1/W2 leader changed on the frozen board, write `05_backtests/SCOREBOARD_v3.md` (new file; "no baseline exists" for empty ratios, "vacuous"
   for same-ten-quarter survivors). List every LIVE row now recorded under FORMAT 1.1 (method, object, quarter, vintage) — that is the 5 Nov score sheet.
2. Write `05_backtests/LANE2_MEMO_READY_CLAIMS.md`: per surviving claim — the exact sentence, the number, the evidence file, the caveat, W1 and W2.
   Refuted and partial claims in a separate section with the attack that worked. State plainly whether A2 established, partially established, or
   did not establish an expectations edge, and what F changed in the RNPL leg.
3. Write `05_backtests/LANE2_PULL_REQUEST_BODY.md`: per package — pass line, result, three refuter verdicts; Gate 1 and Gate 2 evidence; the claims
   file quoted in full; anything undone and why. (This is the PR body; `gh` may be unavailable.)
4. Update `WORKBOARD.md` (status, note links) and finish `05_backtests/LANE2_RUN_LOG.md` (totals, wall time; say "unavailable" for tokens if the
   runtime does not report them).
5. Push and PR:
   ```bash
   git add -A analysis/src/forecast_methods data/processed/forecast_methods docs/revenue-forecast-strategy analysis/src/acquisition data/manifests/policy_monitor.log
   git status --short          # review every line; never commit .venv, __pycache__, raw stores or licensed data
   git commit -m "Lane 2 full: A2 guide surprise under the harness convention, B2 term structure, RNPL v2, macro pulls, consensus stamp, refuters"
   git push -u origin codex/lane2-full
   gh pr create --base main --head codex/lane2-full --title "Lane 2 full: A2 guide surprise, B2 term structure, RNPL v2, macro pulls, consensus stamp, refuters" \
     --body-file docs/revenue-forecast-strategy/05_backtests/LANE2_PULL_REQUEST_BODY.md \
     || echo "open https://github.com/Kaenyne/Citadel-ABNB/compare/main...codex/lane2-full"
   ```

## Pass line (pre-registered)
Every sentence in the claims file has a number, a file, a caveat and both windows; nothing from the kill list; both scorers ran after the last
registration; the branch is pushed; the PR is open or the compare URL is printed.

## Outputs (all new files except the board)
`05_backtests/LANE2_MEMO_READY_CLAIMS.md`, `LANE2_PULL_REQUEST_BODY.md`, `LANE2_RUN_LOG.md` (+ `SCOREBOARD_v3.md` if needed) · updated `WORKBOARD.md` · the push · the PR or URL.

## Report back (final message)
The claims file verbatim; the LIVE rows recorded; the PR link or compare URL; anything left undone and why.

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
