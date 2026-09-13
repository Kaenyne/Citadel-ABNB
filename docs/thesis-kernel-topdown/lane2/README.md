# Lane 2 — per-agent briefs (RNPL, consensus, public data, and the A / B′ re-run under the harness convention)

**Parent prompt that runs this whole lane:** `../prompts/CODEX_LANE2_FULL_PROMPT.md`.
**Read first, every agent:** `CONVENTION.md` in this folder — it is the reason Lane 2 exists.

One file per agent role. A subagent gets exactly one brief plus the shared references it names. The parent runs the two
Gate-1 verifications (H11, RET) and CLOSE itself; everything else may be a subagent.

## Order and gates

```
Gate 1 (parent): H11 harness FORMAT 1.1 verified · RET open-returns verified          ── both green ──►
Gate 2: A2 (subagent, alone) — guide surprise under the convention; clean note        ── clean ──►
parallel (max 3 children at a time in the Codex runtime; queue the rest): F · B2 · C2 · M · L (only if sanctioned)
refuters: 3 per headline claim (vintage / power / mechanism) for A2, B2, F
CLOSE (parent): both scorers → LANE2_MEMO_READY_CLAIMS → workboard → push → one PR
```

| Brief | Who | Needs internet | Est. tokens |
|---|---|---|---|
| `H11_HARNESS_V1_1.md` | parent (verify only; package already in git) | no | 0.05M |
| `RET_OPEN_RETURNS.md` | parent (verify; `--refresh` optional) | optional | 0.05M |
| `A2_GUIDE_SURPRISE_V2.md` | subagent, alone (Gate 2) | no | 0.4M |
| `F_RNPL_VARIABLE.md` | subagent | no (EDGAR optional) | 0.5M |
| `B2_TERM_STRUCTURE_V2.md` | subagent | no | 0.35M |
| `C2_MACRO_PULLS.md` | subagent | yes (public statistics) | 0.3M |
| `M_CONSENSUS_STAMP.md` | subagent | yes (yfinance, Zacks, StockAnalysis) | 0.15M |
| `L_POLICY_MONITOR.md` | subagent — **only if its header says SANCTIONED_BY_THEO: yes** | yes (airbnb.com read-only) | 0.15M |
| `REFUTER.md` (× 9) | subagents | no | 0.2M each |
| `CLOSE.md` | parent | no | 0.15M |

Expected total ≈ 4–5M tokens including orchestration.

## What Lane 1 taught us (encoded here)

1. A bug in an agent's **own new test** is fixed once, with the failing output kept as a receipt — it is not a STOP. Gate 1
   of Lane 1 stopped for ten hours on a `round()` boundary in a comparator the agent had written itself.
2. The Codex runtime allowed **three child agents** at a time; plan the parallel block as batches.
3. `gh` was absent and the GitHub integration returned 403 on PR creation: write the PR body to a file, push, and print the
   compare URL — a human opens the PR.
4. Registration needs the real date: FORMAT 1.1 (`harness_v1_1/`) exists for that; W1/W2 rules are unchanged.
5. "Strictly before the guide date" is not our convention. `CONVENTION.md` is.

## Environment (portable)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pymc arviz scikit-learn pyarrow linearmodels lightgbm duckdb yfinance
python -m pytest analysis/src/forecast_methods/harness/tests analysis/src/forecast_methods/L0 -q     # 47 passed
python -m pytest analysis/src/forecast_methods/harness_v1_1/tests analysis/src/forecast_methods/returns_v1/tests -q
python analysis/src/forecast_methods/kernel_engine_v2/run.py                                          # acceptance PASS on all 12 cells
```

## Where results go

Code `analysis/src/forecast_methods/<new folder>/` · outputs `data/processed/forecast_methods/<new folder>/` · registry files under a
new method name (shared registry; register through `harness_v1_1`) · notes `docs/revenue-forecast-strategy/05_backtests/` ·
board `docs/revenue-forecast-strategy/WORKBOARD.md`.
