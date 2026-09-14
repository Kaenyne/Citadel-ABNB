# 02 · Setup for a contributor (30 minutes)

## 1. Clone and branch

```bash
git clone https://github.com/Kaenyne/Citadel-ABNB.git
cd Citadel-ABNB
git checkout -b <yourname>/<wp-id>          # e.g. maria/wp-a
```

Read `CLAUDE.md` (or `AGENTS.md`) — the eight rules — then claim your package in
`docs/revenue-forecast-strategy/WORKBOARD.md` (set status, your name, your branch) and commit that one-line change first.

## 2. Python environment

```bash
python3 -m venv .venv && source .venv/bin/activate         # Python 3.11–3.13
pip install -r requirements.txt
pip install pymc arviz scikit-learn pyarrow linearmodels lightgbm duckdb
```

Always run scripts from the repo root. If your OS path has spaces, quote it.

## 3. Smoke tests — do not start work until both pass

```bash
# the shared harness (format 1.0, frozen) — tests must pass
python -m pytest analysis/src/forecast_methods/harness/tests -q

# the kernel acceptance table must reproduce to 2dp from the KPI panel alone
python analysis/src/forecast_methods/kernel_lambda/run.py
# expect in the output / note: Q3 17.391 / 17.145 / 17.182 ; Q4 11.946 / 12.117 / 12.026  (2023–2025 season-years)
```

If the table does not reproduce, stop and open an issue on the PR — something in your environment or the panel differs.

## 4. What is in git and what is not

In git (enough for most packages): the KPI panel and every processed table under `data/processed/`, the harness, every
package's code, notes and outputs under `analysis/src/forecast_methods/`, `data/processed/forecast_methods/` and
`docs/revenue-forecast-strategy/`, the consensus vintage register.

Not in git (large or licensed): Inside Airbnb raw dumps (public — download yourself; `04_DATA_MAP.md` says which),
the 67.5M-review store, Bloomberg workbooks, Third Bridge PDFs, LSEG exports, the fee-panel raw captures (Theo pushes the
run CSVs after each date). If your package needs one of these, the prompt says so under "Needs outside the repo".

## 5. The harness in one minute

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("analysis/src/forecast_methods").resolve()))
from harness import load_calendar, load_targets, GUIDE_DATES_W1, GUIDE_DATES_W2, history_as_of, register, load_registry, score_registry
cal = load_calendar()            # print dates, guide dates, fiscal quarters
tgt = load_targets()             # revenue, GBV, nights, ADR, take rate, FX pts, guide lo/mid/hi, PIT Street
hist = history_as_of("2025-08-07")   # everything knowable at that guide date
# build your forecasts → a DataFrame in REGISTRY_COLUMNS → register(df)  → writes data/processed/forecast_methods/registry/<method>__<object>.csv
```

Then `python analysis/src/forecast_methods/harness/score.py`. Read `analysis/src/forecast_methods/harness/README.md` for the columns
(method, object, target, quarter, vintage_date, horizon_q, point, q05, q25, q50, q75, q95, n_train, window, notes). A forecast whose
`vintage_date` is after the target's print date is rejected — that is the point-in-time guard.

## 6. Working conventions

- One package per person; new folders only; never edit another package or a frozen file.
- Consensus values come only from `data/processed/forecast_methods/L0/L0_vintage_register.csv` (vendor + timestamp) — never from memory
  or a current web page for a historical date.
- Your note goes in `docs/revenue-forecast-strategy/05_backtests/<WP>_<slug>.md` with the template in `AGENT_BRIEF.md` §7:
  verdict first, exact commands, tables with n, what failed, a `RESUME` paragraph.
- Open the PR against `main` with the note linked; one teammate reviews; do not merge your own PR.

## 7. If you use an AI agent

Paste `prompts/<WP>.md` verbatim as the task. The prompt already contains the rules, the pass line and the outputs. Claude Code
reads `CLAUDE.md` automatically; Codex reads `AGENTS.md`. Agents must not make the eleven team decisions or the terms-of-service calls —
they lay out options and stop.
