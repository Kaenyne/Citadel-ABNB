# CODEX — Lane 1 end to end, full subagentic run (paste verbatim as the first message; repo root, branch `theo/thesis-kernel-topdown`)

You are the PARENT ORCHESTRATOR for Lane 1 (kernel, guide, valuation, regional FX) of the Citadel-ABNB kernel thesis. Your job is to
deliver the whole lane end to end by spawning subagents for every independent package, gating on the two results that everything
else depends on, refuting every headline claim adversarially, and closing with one PR. `AGENTS.md` is loaded automatically — obey it.
Everything you need is in git; nothing requires Theo's machine. Work only from files; never ask a human mid-run except for the
STOP conditions listed at the end.

## 0. Setup (you; ~10 minutes)

```bash
git pull
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pymc arviz scikit-learn pyarrow linearmodels lightgbm duckdb yfinance
python -m pytest analysis/src/forecast_methods/harness/tests analysis/src/forecast_methods/L0 -q     # expect: 47 passed
python analysis/src/forecast_methods/kernel_lambda/run.py                                            # expect: "acceptance test: PASS on all 12 cells"
```
If either line does not match, STOP and report the exact output. Then read, in this order and nothing else yet:
`docs/thesis-kernel-topdown/lane1/README.md` · `docs/thesis-kernel-topdown/03_NUMBERS_CHEATSHEET.md` ·
`analysis/src/forecast_methods/harness/README.md` · `docs/revenue-forecast-strategy/AGENT_BRIEF.md` §3 and §6 (decisions you may not make; numbers you may not quote).
Create your branch `codex/lane1-full` and open `docs/revenue-forecast-strategy/05_backtests/LANE1_RUN_LOG.md` — append one line per
subagent: name, brief, start, end, verdict, tokens. Claim the Lane-1 rows in `docs/revenue-forecast-strategy/WORKBOARD.md` (add the date; WP-X too).

## 1. Gate 1 — K0, run by you (no subagent)

Follow `docs/thesis-kernel-topdown/lane1/K0_KERNEL_ENGINE.md` exactly. Gate 1 passes only if the 12-cell λ table reproduces to 2dp
(Q3 17.391 / 17.145 / 17.182; Q4 11.946 / 12.117 / 12.026), pytest for the new module is green, every function refuses data printed on or
after its `as_of`, AND the regional-ready interface exists (accepts a per-region GBV frame; consolidated = sum). If Gate 1 fails, STOP and
report; do not spawn anything on a broken spine.

## 2. Gate 2 — A, one subagent, alone

Spawn `sub-A` with exactly one file: `docs/thesis-kernel-topdown/lane1/A_GUIDE_SURPRISE.md`. When it returns, you (not the subagent) check
its note for: the pre-registered pass line written BEFORE results; hit-rate with Wilson interval and cell counts on BOTH windows W1 and W2;
vendor + timestamp on every consensus value and no September-2026 value used at a historical date; executable `open_*` returns only; a
one-word verdict pass / fail / underpowered in the first paragraph; K0 imported, λ not re-derived. Any miss → send `sub-A` back once with the
specific defect; a second miss → STOP and report. Gate 2 passes on a clean note regardless of whether the verdict is pass, fail or underpowered
(a clean negative is a result).

## 3. Parallel packages — one subagent per brief, all at once

Spawn these six together; each receives exactly one brief and nothing else; each writes only its own new folder, its own new registry
method name and its own new note; none runs `score.py`; none edits another package, `harness/`, `L0/` (append-only with backup) or any frozen file.

| subagent | brief | internet |
|---|---|---|
| `sub-B`  | `lane1/B_TERM_STRUCTURE.md` | no |
| `sub-V`  | `lane1/V_VALUATION_RECONCILIATION.md` | yes (yfinance) |
| `sub-D`  | `lane1/D_LAMBDA_CARD.md` | no |
| `sub-R`  | `lane1/R_REGIONAL_REFRESH.md` | yes (NTTO / Eurostat / national arrivals) |
| `sub-C3` | `lane1/C3_GBV_FEATURES.md` | no |
| `sub-X`  | `lane1/X_REGIONAL_KERNEL_OD_FX.md` | yes (arrivals) — **priority**: its regional FX recompute supersedes B4's consolidated numbers |

Rules for you while they run: do not merge their work by hand; if one fails, re-spawn it once with the failure text appended to its brief;
if it fails twice, record it in the run log and continue without it. If the sandbox has no outbound network, `sub-V`, `sub-R` and `sub-X`
must say so in their notes and deliver the offline parts (V without the price refresh; R and X with the repo data only).

## 4. Refuters — three per headline claim, distinct lenses, majority rules

For each package that returned (A, B′, R, V, X — not D, not C3 unless it claims a survivor), take the ONE sentence it proposes for the memo
and spawn three subagents, each with `lane1/REFUTER.md` plus the filled fields PACKAGE, CLAIM and LENS ∈ {vintage, power, mechanism}.
They read only the package note, its registry files and the raw inputs. Each returns refuted / survived / partially with at least five
explicit attacks. A claim survives on 2-of-3. Record every verdict in the run log. Special instruction for X's refuters: the vintage lens must
check that the O–D matrix and the exposure weights use only data available at each historical guide date; the mechanism lens must test whether
the regional recompute merely re-weights the same basket or actually changes the 3Q26 / 4Q26 FX conclusion.

## 5. Close — you, no subagent (`lane1/CLOSE.md`)

1. `python analysis/src/forecast_methods/harness/score.py`; write `05_backtests/SCOREBOARD_v3.md` (new file) if any leader changed; label empty-ratio
   rows "no baseline exists" and same-ten-quarter survivors "vacuous".
2. Write `05_backtests/LANE1_MEMO_READY_CLAIMS.md`: for every claim that survived 2-of-3 — the exact memo sentence, the number, the evidence file,
   the caveat, W1 and W2 results. Refuted and partial claims in a separate section with the attack that worked. If X changed the FX conclusion,
   say so explicitly and mark B4's numbers superseded; if X did not, say that too.
3. Update `WORKBOARD.md` (status, note links) and finish `LANE1_RUN_LOG.md` (totals: subagents spawned, tokens, wall time).
4. Commit on `codex/lane1-full`; open ONE PR against `main` titled "Lane 1 full: kernel engine, guide surprise, term structure, valuation page,
   regional refresh, GBV features, regional kernel + O–D FX, refuters". PR body: per package — pass line, result, refuter verdicts (3), tokens; the
   Gate 1 and Gate 2 evidence; the memo-ready claims file quoted in full; anything left undone and why.

## 6. Budget and fallback

Expected total ≈ 7.5–8.5M tokens (K0 0.3 · A 0.35 · B′ 0.3 · V 0.2 · D 0.1 · R 0.4 · C3 0.35 · X 0.5 · 15 refuters ≈ 3.0 · close 0.15, plus your own
orchestration). If quota runs short at any point, complete in THIS order and stop cleanly with a PR of whatever exists:
K0 → A → 3 refuters on A → X → 3 refuters on X → CLOSE. Never leave a subagent's outputs unrecorded in the run log.

## 7. Hard constraints (from AGENTS.md; repeated because they are where runs go wrong)

- Copy, never overwrite. New folders, new registry method names, new notes. Frozen: `harness/`, `L0/` (append-only + dated backup),
  `data/processed/overnight/20_frozen_q3_2026.csv`, `research/thesis.md`, every existing package and note.
- Point-in-time or it does not count: consensus only from `data/processed/forecast_methods/L0/L0_vintage_register.csv` with vendor + timestamp
  before the date; refit at guide dates; both windows; letter integers as ±0.5 intervals; executable `open_*` returns only.
- Pre-register every pass line before running; a failed test is written up, not deleted.
- No scraping of any kind; no credentials; no licensed data in git; no commits to `main`.
- You do NOT make the eleven team decisions (AGENT_BRIEF §3) — lay out options. You do NOT quote the kill list (§6).
- Portable commands only (`python` from `.venv`, repo root); paths via `pathlib`.

## 8. STOP conditions (report and halt — do not improvise)

Gate 1 fails · Gate 2 fails twice · the harness tests fail after any step · a subagent needs data that is not in git and not on the public
internet · anything that would require touching airbnb.com, a UF database, or a licensed source.

Report back with, in this order: Gate 1 evidence; A's verdict and its three refuter verdicts; X's verdict and whether it changed the FX
conclusion; the memo-ready claims file; the PR link; tokens and wall time.
