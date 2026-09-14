# CODEX — Lane 2 end to end, full subagentic run (paste verbatim as the first message of a fresh Codex session)

You are the PARENT ORCHESTRATOR for Lane 2 (RNPL, consensus, public data, and the guide-surprise / term-structure tests re-run under the
harness's own point-in-time convention) of the Citadel-ABNB kernel thesis. Deliver the whole lane end to end: verify the two infrastructure
pieces already in git, gate on the one result everything else depends on, spawn a subagent per independent package, refute every headline
claim adversarially, push a checkpoint after every stage, and close with one pushed branch and one PR. `AGENTS.md` at the repo root is
loaded automatically — obey it. Everything you need is in git or on the public internet; nothing requires Theo's machine. Never ask a human
mid-run except for the STOP conditions at the end.

## 0. Get the repo and set up (you)

```bash
git clone https://github.com/Kaenyne/Citadel-ABNB.git && cd Citadel-ABNB        # or, inside an existing clone: git fetch --all --prune
git checkout main && git pull --ff-only
git log --oneline -1                                                              # record this commit in the run log
git checkout -b codex/lane2-full
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pymc arviz scikit-learn pyarrow linearmodels lightgbm duckdb yfinance
```

## 0b. Audit — data access and infrastructure, all green before anything is spawned

Run every block below and paste the verbatim output as the first section of `docs/revenue-forecast-strategy/05_backtests/LANE2_RUN_LOG.md`
(new file) together with the branch, the starting commit and the UTC time.

**(1) Files the briefs read — every line must print `ok`:**
```bash
for f in \
  docs/thesis-kernel-topdown/lane2/CONVENTION.md docs/thesis-kernel-topdown/lane2/README.md docs/thesis-kernel-topdown/lane2/RULES.md \
  docs/thesis-kernel-topdown/lane2/H11_HARNESS_V1_1.md docs/thesis-kernel-topdown/lane2/RET_OPEN_RETURNS.md \
  docs/thesis-kernel-topdown/lane2/A2_GUIDE_SURPRISE_V2.md docs/thesis-kernel-topdown/lane2/B2_TERM_STRUCTURE_V2.md \
  docs/thesis-kernel-topdown/lane2/F_RNPL_VARIABLE.md docs/thesis-kernel-topdown/lane2/C2_MACRO_PULLS.md \
  docs/thesis-kernel-topdown/lane2/L_POLICY_MONITOR.md docs/thesis-kernel-topdown/lane2/M_CONSENSUS_STAMP.md \
  docs/thesis-kernel-topdown/lane2/REFUTER.md docs/thesis-kernel-topdown/lane2/CLOSE.md \
  docs/thesis-kernel-topdown/03_NUMBERS_CHEATSHEET.md docs/revenue-forecast-strategy/AGENT_BRIEF.md docs/revenue-forecast-strategy/WORKBOARD.md \
  analysis/src/forecast_methods/harness/README.md analysis/src/forecast_methods/harness/score.py \
  analysis/src/forecast_methods/harness_v1_1/README.md analysis/src/forecast_methods/harness_v1_1/registry.py analysis/src/forecast_methods/harness_v1_1/score.py \
  analysis/src/forecast_methods/returns_v1/README.md analysis/src/forecast_methods/returns_v1/run.py \
  analysis/src/forecast_methods/kernel_engine_v2/README.md analysis/src/forecast_methods/kernel_engine_v2/run.py \
  data/processed/forecast_methods/harness/calendar.csv data/processed/forecast_methods/harness/targets.csv data/processed/forecast_methods/harness/scoreboard.csv \
  data/processed/forecast_methods/returns_v1/ohlc_daily.csv data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv data/processed/forecast_methods/returns_v1/manifest.json \
  data/processed/forecast_methods/L0/L0_vintage_register.csv analysis/src/forecast_methods/L0/test_l0.py \
  data/processed/overnight/02_kpi_panel_quarterly.csv data/processed/overnight/02_guidance_ledger.csv data/processed/overnight/02_guidance_cushion_series.csv \
  data/processed/overnight/02_fy_guide_revisions.csv data/processed/overnight/16_consensus_at_print_merged.csv data/processed/overnight/04_consensus_at_print.csv \
  data/processed/forecast_methods/alpha_a/pit_cells.csv data/processed/forecast_methods/alpha_a/post_letter_diagnostic.csv \
  docs/revenue-forecast-strategy/05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md docs/revenue-forecast-strategy/05_backtests/tracker-backlog.md \
  docs/revenue-forecast-strategy/05_backtests/D_CARD_ADDENDUM_LAMBDA.md docs/RNPL_HANDOFF.md \
  research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md analysis/src/rnpl_balance_sheet_bridge.py \
  research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv \
  analysis/src/forecast_methods/regional_kernel_v1/public_inputs.csv analysis/src/forecast_methods/l1_reconciliation_v3/fetch_arrivals.py \
  docs/thesis-kernel-topdown/prompts/WP-F_rnpl_variable.md docs/thesis-kernel-topdown/prompts/WP-C2_macro_pulls.md \
  docs/thesis-kernel-topdown/prompts/WP-L_policy_monitor.md docs/thesis-kernel-topdown/prompts/WP-M_consensus_stamp.md ; do
  [ -f "$f" ] && echo "ok       $f" || echo "MISSING  $f"; done
```
Any `MISSING` → STOP and report the list.

**(2) Tests and acceptance — the expected numbers are exact:**
```bash
python -X utf8 -m pytest analysis/src/forecast_methods/harness/tests analysis/src/forecast_methods/L0 -q     # expect: 47 passed
python -X utf8 -m pytest analysis/src/forecast_methods/harness_v1_1/tests -q                                 # expect: 37 passed
python -X utf8 -m pytest analysis/src/forecast_methods/returns_v1/tests -q                                   # expect: 8 passed
python -X utf8 -m pytest analysis/src/forecast_methods/kernel_engine_v2/tests -q                             # expect: 63 passed
python -X utf8 analysis/src/forecast_methods/kernel_engine_v2/run.py > /tmp/k0.txt; sed -n '1p' /tmp/k0.txt             # expect: "acceptance test: PASS on all 12 cells" (never pipe it to head: BrokenPipe)
python -X utf8 analysis/src/forecast_methods/harness/score.py > /tmp/s10.txt; sed -n '1,2p' /tmp/s10.txt            # expect: 4109 registry rows (or more), 276 scoreboard rows (or more), exit 0
python -X utf8 analysis/src/forecast_methods/harness_v1_1/score.py > /tmp/s11.txt; sed -n '1,2p' /tmp/s11.txt       # expect: same counts, exit 0, writes only under harness_v1_1/
git status --short data/processed/forecast_methods/harness/                                                  # expect: nothing (frozen board unchanged)
git checkout -- data/processed/forecast_methods/kernel_engine_v2/                                            # the acceptance run rewrites two of its own output files; discard, they are not your work
```
**(3) Loader check:**
```bash
python -X utf8 - <<'PY'
import sys, io, pandas as pd; sys.path.insert(0, "analysis/src/forecast_methods")
from harness_v1_1 import RUN_DATE, LIVE_VINTAGE_MIN, paths as P
cal = pd.read_csv(P.OUT_CALENDAR); tg = pd.read_csv(P.OUT_TARGETS)
txt = open(P.SRC_L0_VINTAGE_REGISTER, encoding="utf-8").read().splitlines(); hdr = next(i for i,l in enumerate(txt) if l.count(",") >= 8)
reg = pd.read_csv(io.StringIO("\n".join(txt[hdr:])))
pg = reg[(reg.register_id == "PG-2026Q3-revenue")]
ret = pd.read_csv("data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv")
print("calendar rows", len(cal), "| targets rows", len(tg), "| L0 rows", len(reg), "| roles", reg.role.value_counts().to_dict())
print("6 Aug pre-guide 3Q26:", pg[["vendor","value","as_of_timestamp","pit_usable"]].to_dict("records"))       # expect LSEG 4610.0, 2026-08-06, True
print("returns events", len(ret), "| last event", ret.event_date.max(), "| RUN_DATE", RUN_DATE, "| LIVE from", LIVE_VINTAGE_MIN, "| format", P.FORMAT_VERSION)
PY
```
Expect: calendar 25 · targets 25 · L0 ≥ 161 rows · LSEG 4610.0 stamped 2026-08-06 · 23 return events · RUN_DATE = today.
**(4) Network (not a STOP if it fails — C2 and M then run offline parts and say so):**
```bash
for u in "https://api.stlouisfed.org" "https://www.trade.gov" "https://ec.europa.eu/eurostat" "https://query1.finance.yahoo.com"; do printf "%s -> " "$u"; curl -s -o /dev/null -w "%{http_code}\n" --max-time 15 "$u"; done
python -X utf8 -c "import yfinance as yf; print('yfinance ok', yf.Ticker('ABNB').history(period='5d')['Close'].iloc[-1])"
command -v gh && gh auth status 2>&1 | head -2 || echo "gh unavailable: CLOSE prints the compare URL"
```
Then read, in this order and nothing else yet: `docs/thesis-kernel-topdown/lane2/CONVENTION.md` · `lane2/README.md` · `03_NUMBERS_CHEATSHEET.md` ·
`harness/README.md` · `harness_v1_1/README.md` · `AGENT_BRIEF.md` §3 and §6 (decisions you may not make; numbers you may not quote).
Claim the Lane-2 rows (WP-A2, WP-B2, WP-F, WP-C2, WP-M, WP-H11, WP-RET, and WP-L only if sanctioned) in `WORKBOARD.md` with the date and
branch, commit, and push the first checkpoint: `git push -u origin codex/lane2-full`.

## 1. Gate 1 — H11 and RET, run by you (no subagent)

Follow `lane2/H11_HARNESS_V1_1.md` then `lane2/RET_OPEN_RETURNS.md`. Both are verifications of packages already in git. Gate 1 passes only if:
47 frozen tests · 37 FORMAT 1.1 tests · 8 returns tests · 1.1 scorer exit 0 with the frozen board unchanged · 23 return events with every entry
strictly after its letter. Fail → STOP and report (this is infrastructure). Pass → checkpoint: commit the run log and push.

## 2. Gate 2 — A2, one subagent, alone

Spawn `sub-A2` with exactly one file: `docs/thesis-kernel-topdown/lane2/A2_GUIDE_SURPRISE_V2.md`. When it returns, you check the note for: the
pre-registered pass line written BEFORE results, verbatim; evaluable-cell counts per window (under `CONVENTION.md` every W1 letter is evaluable
unless the kernel itself is undefined there, with the reason stated); hit-rate with Wilson interval and cell counts on BOTH windows; vendor +
timestamp on every consensus value, no `current` row at a historical date; return legs from `returns_v1` `excess_open_*` only; the controls table
(GBV surprise, raw guide gap); `kernel_engine_v2` imported, λ not re-derived; a one-word verdict in the first paragraph; the LIVE 2026Q4 row
registered under FORMAT 1.1 at RUN_DATE. Any miss → send `sub-A2` back once with the specific defect; a second miss → STOP. Gate 2 passes on a
clean note whatever the verdict. If A2 reports 0 evaluable cells, that is a defect (the convention was not applied), not a result — send it back.
Pass → checkpoint: commit and push.

## 3. Parallel packages — one subagent per brief; the runtime allows about three children at a time, so run in batches and keep the queue full

| subagent | brief | internet | batch |
|---|---|---|---|
| `sub-F`  | `lane2/F_RNPL_VARIABLE.md` | no (EDGAR optional) | 1 |
| `sub-B2` | `lane2/B2_TERM_STRUCTURE_V2.md` | no | 1 |
| `sub-M`  | `lane2/M_CONSENSUS_STAMP.md` | yes | 1 |
| `sub-C2` | `lane2/C2_MACRO_PULLS.md` | yes | 2 |
| `sub-L`  | `lane2/L_POLICY_MONITOR.md` — **only if its header line reads `SANCTIONED_BY_THEO: yes`**; otherwise log "L skipped: not sanctioned" | yes | 2 |

Each receives exactly one brief and nothing else; each writes only its own new folder, its own new registry method name and its own new note;
none runs a scorer; none edits another package, `harness/`, `harness_v1_1/`, `L0/` (only M appends, with a dated backup) or any frozen file.
A failure → re-spawn once with the failure text appended; twice → log and continue. No network → C2 and M deliver the offline parts and say so.
All returned → checkpoint: commit and push.

## 4. Refuters — three per headline claim, distinct lenses, 2-of-3

For A2, B2 and F, take the ONE sentence each proposes for the memo and spawn three subagents with `lane2/REFUTER.md` plus PACKAGE, CLAIM and
LENS ∈ {vintage, power, mechanism}. They read only the package note, its registry files, its outputs, the raw inputs and `CONVENTION.md`. Each
returns refuted / survived / partial with at least five explicit attacks; partial does not count as survived. Record every verdict in the run log.
→ checkpoint: commit and push.

## 5. Close — you (`lane2/CLOSE.md`)

Both scorers (frozen first, then 1.1); `SCOREBOARD_v3.md` only if a W1/W2 leader changed; the list of LIVE rows now recorded under FORMAT 1.1;
`05_backtests/LANE2_MEMO_READY_CLAIMS.md`; `05_backtests/LANE2_PULL_REQUEST_BODY.md`; `WORKBOARD.md`; finish `LANE2_RUN_LOG.md`. Then:
```bash
git add -A analysis/src/forecast_methods data/processed/forecast_methods docs/revenue-forecast-strategy analysis/src/acquisition data/manifests/policy_monitor.log
git status --short            # review every line; never commit .venv, __pycache__, raw stores or licensed data
git commit -m "Lane 2 full: A2 guide surprise under the harness convention, B2 term structure, RNPL v2, macro pulls, consensus stamp, refuters"
git push -u origin codex/lane2-full
gh pr create --base main --head codex/lane2-full --title "Lane 2 full: A2 guide surprise, B2 term structure, RNPL v2, macro pulls, consensus stamp, refuters" \
  --body-file docs/revenue-forecast-strategy/05_backtests/LANE2_PULL_REQUEST_BODY.md \
  || echo "open https://github.com/Kaenyne/Citadel-ABNB/compare/main...codex/lane2-full"
```

## 6. Budget and fallback

Expected ≈ 4–5M tokens (A2 0.4 · F 0.5 · B2 0.35 · C2 0.3 · M 0.15 · L 0.15 · 9 refuters ≈ 1.8 · close 0.15 · orchestration). If quota runs short,
complete in THIS order, push what exists, and open the PR or print the URL: Gate 1 → A2 → 3 refuters on A2 → F → 3 refuters on F → CLOSE.
Checkpoint pushes mean a hard cut loses at most one stage.

## 7. Hard constraints (from AGENTS.md and `lane2/RULES.md`; repeated because they are where runs go wrong)

- Copy, never overwrite. Frozen: `harness/`, `harness_v1_1/`, `L0/` (append-only + dated backup, M only), `20_frozen_q3_2026.csv`,
  `research/thesis.md`, every existing package and note.
- Point-in-time **as defined in `lane2/CONVENTION.md`**: a guide-date vintage includes that letter's prints; morning-of-print consensus
  (`role` pre_guide / at_print, stamped that day, `pit_usable = True`) is pre-letter; `current` rows never at a historical date; both windows;
  letter integers ±0.5; executable returns are `returns_v1` `excess_open_*` only. Do NOT reinstate "strictly before the guide date".
- Registration through `harness_v1_1.registry.register` (W1/W2 rules unchanged; LIVE rows at RUN_DATE). Only you run the scorers.
- Pre-register every pass line; a failed test is written up, not deleted; n < 6 is underpowered, never pass.
- **An agent's own new test with a bug is fixed once, with the failing output kept as a receipt — not a STOP.** A failing frozen test is a STOP.
- No scraping; nothing touches airbnb.com except L when sanctioned; no credentials; no licensed data in git; no commits to `main`; you do NOT
  make the eleven team decisions (AGENT_BRIEF §3) and do NOT quote the kill list (§6). Portable commands only.

## 8. STOP conditions (report and halt)

Any `MISSING` file in 0b · frozen test count ≠ 47 · FORMAT 1.1 tests ≠ 37 · returns tests ≠ 8 · kernel acceptance not PASS · frozen board changed
by any step · Gate 2 fails twice · a subagent needs data not in git and not on the public internet · anything that would touch airbnb.com
(other than sanctioned L), a UF database or a licensed source.

Report back in this order: the 0b audit output; Gate 1 evidence; A2's verdict, cell counts per window, and its three refuter verdicts; F's
verdict and its three refuter verdicts; B2's verdict; the LIVE rows recorded under FORMAT 1.1; the memo-ready claims file; confirmation that
`codex/lane2-full` is pushed and the PR link or compare URL; wall time (tokens if the runtime reports them).
