# Citadel-ABNB — instructions for any agent working in this repo (Codex, Claude, or other)

This file is identical in intent to `CLAUDE.md`; read whichever your harness loads, then follow the same three steps.

You are working on a stock pitch on Airbnb (ABNB) for the 2026 Citadel Intercollegiate Stock Pitch
Competition. Prelim memo (2 pages + model) is due **2 Oct 2026**; finals **22–24 Oct**; the next earnings
print is **5 Nov 2026** (after finals). The pitch forecasts the *guide* Airbnb will give and what it is
made of — not a revenue number.

**Start here, in this order, before doing anything:**
1. `docs/revenue-forecast-strategy/AGENT_BRIEF.md` — mission, state of play, rules, every work package with its acceptance test.
2. `docs/revenue-forecast-strategy/WORKBOARD.md` — claim a work package before starting; update it when you finish.
3. The note for the package you are touching under `docs/revenue-forecast-strategy/05_backtests/`.

## Non-negotiable rules

1. **Copy, never overwrite.** Never modify or delete an existing file under `analysis/src/forecast_methods/`,
   `data/processed/forecast_methods/`, `docs/revenue-forecast-strategy/`, `model/`, or any tracked data file.
   New work goes in a NEW folder (`<package>_v2`, `_v3`, …), new registry files under a NEW method name,
   notes in NEW files. Frozen: `analysis/src/forecast_methods/harness/`, `…/L0/` (append-only for the
   vintage register, with a dated backup first), `data/processed/overnight/20_frozen_q3_2026.csv`.
2. **Point-in-time or it doesn't count.** Refit at guide dates; every consensus value carries vendor +
   timestamp (`data/processed/forecast_methods/L0/L0_vintage_register.csv`); two windows W1 (1Q23+, n≈14)
   and W2 (1Q24+, n≈10) — a result must survive both to be quoted; letter integers are scored as ±0.5 intervals.
3. **Pre-register the pass line before running the test.** A failed test is written up, not deleted.
4. **Register forecasts through the harness format** (`analysis/src/forecast_methods/harness/README.md`,
   FORMAT 1.0, authoritative). Re-run `harness/score.py` after every registration.
5. **Never commit to `main`.** Branch (`<name>/<topic>`), PR, one teammate reviews (see `CONTRIBUTING.md`).
   Never commit licensed data (Bloomberg workbooks, Third Bridge PDFs, LSEG exports) or raw stores; manifests only.
6. **Do not scrape beyond the sanctioned sources** (Inside Airbnb dumps; the fee-panel search-page capture
   already running). Anything else that touches airbnb.com is a terms-of-service decision for a human — stop and ask.
7. **Never type credentials.** UF pages: clicking the GatorLink SSO button is fine; passwords and Duo codes are not.
8. **Quote no withdrawn number.** The kill list is in `AGENT_BRIEF.md` §6.

## Environment

- Repo path contains spaces and an apostrophe — always double-quote it in shell.
- Python: `/Users/theomachado/.venvs/citadel-abnb/bin/python` (pandas 3, statsmodels, scipy, pymc, duckdb, pyarrow,
  scikit-learn, lightgbm). On another machine: `python -m venv` + `pip install -r requirements.txt pymc arviz scikit-learn pyarrow linearmodels lightgbm`.
  Run scripts from the repo root; resolve paths with `pathlib` relative to the file.
- Large raw stores (Inside Airbnb calendars/reviews) are outside the repo (`~/abnb_ia_capture/` on Theo's machine); query with DuckDB.
- Every package has a `run.py` that rebuilds it end to end with exit code 0, and a `README.md` with the command.
- Codex: no MCP browser tools here; do web research with your fetch tool and cite URLs. Do not attempt UF-licensed databases.

## How to finish a task

Write your note (`05_backtests/<WP-id>_<slug>.md`: what ran, exact commands, results tables with n, what failed,
honest interpretation, parameter count), update `WORKBOARD.md`, re-run the scorer if you registered anything,
and leave a one-paragraph `RESUME` section at the bottom of your note saying what the next agent should do.
