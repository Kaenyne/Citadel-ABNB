# Lane 1 — per-agent briefs (kernel, guide, valuation, regional FX)

**Parent prompt that runs this whole lane:** `../prompts/CODEX_LANE1_FULL_PROMPT.md` (FULL) or `../prompts/CODEX_HANDOFF_LANE1.md` (CORE).

One file per agent role. A subagent gets exactly one of these files plus the two shared references it names
(`03_NUMBERS_CHEATSHEET.md`, `harness/README.md`). The parent agent runs `K0` and `CLOSE` itself; everything else may be a subagent.

## Order and gates

```
K0 (parent)  ── Gate 1: λ table to 2dp, pytest green ──►  A (subagent, alone)  ── Gate 2: clean note ──►
   parallel subagents: B′ · V · D · R (needs internet) · C3 · X (regional kernel + O–D FX exposure; needs internet)
   then refuters: 3 per headline claim (vintage / power / mechanism) for A, B′, R, V   [CORE: 1 refuter on A]
   then CLOSE (parent): score → memo-ready claims → workboard → one PR
```

| Brief | Model tier | Needs internet | Est. tokens |
|---|---|---|---|
| `K0_KERNEL_ENGINE.md` | strong (estimation) | no | 0.3M |
| `A_GUIDE_SURPRISE.md` | strong | no | 0.35M |
| `B_TERM_STRUCTURE.md` | strong | no | 0.3M |
| `V_VALUATION_RECONCILIATION.md` | mid (arithmetic) | yes (yfinance) | 0.2M |
| `D_LAMBDA_CARD.md` | mid | no | 0.1M |
| `R_REGIONAL_REFRESH.md` | strong | yes (arrivals pulls) | 0.4M |
| `C3_GBV_FEATURES.md` | strong | no | 0.35M |
| `X_REGIONAL_KERNEL_OD_FX.md` | strong | yes (arrivals pulls) | 0.5M |
| `REFUTER.md` (× 1 in CORE, × 12 in FULL) | strong | no | 0.2M each |
| `CLOSE.md` | mid | no | 0.15M |

CORE ≈ 2M tokens: K0 · A · B′ · V · D · one refuter on A · CLOSE. FULL ≈ 7.5–8.5M: everything above.

**Why X exists:** the consolidated build applies FX through one judgement-weighted basket; FX is regional (currency of each booking, pass-through by region),
so the FX carried through the kernel, the observed-share triple and the Q4 step decomposition all inherit the regional error. X builds the regional kernel
and the origin–destination exposure matrix the R FX engine expects; B4's numbers stand as the consolidated approximation until X reports.

## Environment (portable)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pymc arviz scikit-learn pyarrow linearmodels lightgbm duckdb yfinance
python -m pytest analysis/src/forecast_methods/harness/tests -q
python analysis/src/forecast_methods/kernel_lambda/run.py     # λ table must print Q3 17.391/17.145/17.182 · Q4 11.946/12.117/12.026
```

Older package docstrings mention a machine-specific interpreter path; use `python` from `.venv`. All packages resolve the repo root from
their own file location. Nothing in Lane 1 needs the external raw stores.

## Where results go

Code `analysis/src/forecast_methods/<new folder>/` · outputs `data/processed/forecast_methods/<new folder>/` · registry files under a new method
name · notes `docs/revenue-forecast-strategy/05_backtests/` · board `docs/revenue-forecast-strategy/WORKBOARD.md`.
