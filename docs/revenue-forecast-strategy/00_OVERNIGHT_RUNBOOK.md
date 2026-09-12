# Overnight runbook — revenue-forecast methodology programme (started 11 Sep 2026, ~07:00 ET)

Orchestrator: Claude (Fable 5.1) in Theo's Claude Code session. Theo asleep; instruction is to run to completion,
resume after any usage-limit window, and leave a readable report. Nothing here is committed to git; Theo decides.

## Stages

| # | Stage | Mechanism | Status | Outputs |
|---|---|---|---|---|
| 1 | Methodology: ground truth -> 6 proposals -> 6 critiques -> architect | Workflow `wf_8fd0fedf-d78` (16 agents, 89 min, 3.66M tokens) + gap-fill `wf_857b02c4-1fe` | DONE on disk 04:50 ET (harness says 'failed' only because 3 JSON indexes overshot caps; all 18 files written) | `01_ground-truth/`, `02_proposals/`, `03_critiques/` (all six), `04_synthesis/` |
| 2 | Reconcile plan -> L0 spine + harness -> 7 packages (build/verify/fix/re-verify) -> scoreboard -> optimal mix -> red team -> morning report draft | Workflow `wf_33ac450d-fff` (first launch ~05:20 local; ALL 14 agents killed within 9 min by the Claude session usage limit, 'resets 7am ET'; RESUMED 10:03 ET with resumeFromRunId, full re-run: 33 agents, 0 errors, 2h35m, 5.78M tokens) | DONE 12:38 ET | `analysis/src/forecast_methods/`, `data/processed/forecast_methods/{L0,harness,registry,<pkg>,optimal_mix}`, `05_backtests/`, `07_MORNING_REPORT.md` |
| 3 | Orchestrator final pass: re-ran harness scorer (273 rows, mix objects now scored), added addendum to the report, published artifact, notified | orchestrator | DONE 13:05 ET | `07_MORNING_REPORT.md` (final); artifact https://claude.ai/code/artifact/253022ba-033a-43f8-a930-1d769a674a03 |

Architect ranking (04_synthesis, 04:32 ET): 1 M6 kernel/fee/FX (core engine, 7.0) - 2 M3 guidance policy (terminal layer, 6.0) -
3 M1 constrained-LS spine (5.5) - 4 M2 tracker accounting core (5.0) - 5 M5 calibration rail only (4.0) - 6 M4 discard as lens (3.0).
Key ruling: revenue_q = lambda_season x [2/3 GBV_{q-1} + 1/3 GBV_{q-2}] on PRINTED GBV; booking-date FX is inside that base, the
check-in remeasurement is ~0 (t 0.57, n 12), so the Q4-26 FX step is an OUTPUT (-2.0pp carried through Phi) and must not be
subtracted again. Q4-26 central: print $3,200M, guide mid $3,141M (-1.8% vs Zacks $3,200M, -0.5% vs 36-analyst $3,158M);
P(guide < Zacks) ~0.60. FY27 +0.7% vs Street - not variant on level; the variant view is compositional (dollar lap, product lap,
mix identity) and the asymmetry is the 3Q26 printed take rate (>= 18.10% = flip to bull).

## Environment for stage 2/3 agents

- Python: `~/.venvs/citadel-abnb/bin/python` (3.13; venv kept OUTSIDE OneDrive on purpose). Installed: pandas 3.0,
  numpy, scipy, statsmodels, duckdb, openpyxl, matplotlib, requests, yfinance, pytrends, pypdf, pyarrow, scikit-learn,
  pymc + arviz, linearmodels, lightgbm (install log: task `bk05r9tf8`). System `python3` lacks pymc/sklearn/pyarrow.
- R 4.5.2 at `/opt/homebrew/bin/Rscript`; only `dplyr` and `forecast` present (no KFAS/dlm/rstan) — prefer Python.
- Disk: 38 GB free. The 588M-row calendar store is NOT all local; `raw_expansion/` (9.9 GB) holds current Inside
  Airbnb compressed files. Use DuckDB over compressed CSVs; never load into pandas whole.
- Paths contain spaces and an apostrophe; always double-quote in shell.

## Theo's standing instructions for the backtest stage

1. Find the optimal mix of methods; backtest properly (point-in-time, expanding window, against AR(1), guide+cushion,
   Street). No Monte-Carlo-only, no SARIMAX-only.
2. **FX proxy (Theo, 11 Sep):** because Airbnb is booked well ahead of the stay, today's FX move hits *revenue*
   roughly two quarters ahead. Build the revenue-FX term as a lag-weighted function of the currency basket,
   `fx_rev_pts(t) = sum_k w_k * basket_yoy(t-k)`, with weights from the booking lead-time distribution (repo prior:
   mean of t-1 and t-2 EUR y/y, r 0.80; Q4-26 already ~84% determined). Backtest against disclosed
   `fx_pts_revenue` 2Q22-2Q26, report the "already-determined share" at each guide date, and use it to
   proxy the Q4-26 / FY27 FX path under spot-held-constant and +/-1sd USD.
3. Use as many opus / sonnet / haiku agents as the work needs.

## Workflow 2 design (draft, to be finalised from the architect's ranking)

- **A. Shared harness first (1 opus agent, barrier):** `analysis/src/forecast_methods/harness/` — target panel
  (revenue, nights, ADR, GBV, take rate, FX pts, guide midpoints, consensus-at-print, actuals) assembled from
  `data/processed/overnight/02_kpi_panel_quarterly.csv`, `02_guidance_ledger.csv`, `16_consensus_at_print_merged.csv`,
  `abnb_revenue_decomposition.csv`; PIT calendar of guide/print dates; baselines (naive, AR(1), guide+cushion,
  Street); expanding-window scorer (RMSE/MAE on level and on surprise; pinball/CRPS on quantiles); a registration
  format `method, target, quarter, vintage_date, point, q05, q25, q50, q75, q95`; unit tests; runs exit 0.
- **B. Per adopted lens (pipeline: implement -> verify):** implementer writes `analysis/src/forecast_methods/<lens>/`,
  runs it end-to-end with the venv, emits harness-format CSVs to `data/processed/forecast_methods/<lens>/`, and a
  results note in `docs/revenue-forecast-strategy/05_backtests/<lens>.md`. Verifier re-runs from clean, checks exit
  codes, checks every input's vintage <= vintage_date (leakage), checks note numbers match CSVs.
- **C. Scoreboard (1 agent):** runs the harness scorer over all methods + baselines; writes `05_backtests/SCOREBOARD.md`.

## Workflow 3 design (draft)

- Stacking / Bayesian model averaging across method outputs with leave-future-out weight learning; conformal
  intervals; combined forecasts for the 3Q26 print, the 5-Nov Q4 guide midpoint vs Street $3,200M, the Feb-27 FY27
  guide vs Street $15.73-15.76bn; comparison with the frozen card `20_frozen_q3_2026.csv`; an adversarial leakage
  check; a report writer.

## Known issues

- Stage 1, ~03:55 ET: `propose:ml-signal-extraction (sonnet)` wrote `02_proposals/M5_ml_signal_extraction_and_challengers.md`
  (240 lines) but its final StructuredOutput JSON (13.5 KB) failed to parse, so the harness marked it failed and skipped
  its critique. M5 is NOT in the architect's inputs.
- Stage 1, ~04:00 ET: same failure for `propose:fx-takerate-timing (opus)` — `02_proposals/M6_fx_takerate_timing_mechanics.md`
  (343 lines, complete) written, but a 28 KB StructuredOutput JSON failed to parse after 9 retries. M6 is also NOT
  in the architect's inputs. The architect therefore ranked only M1-M4.
- Recovery launched 04:30 ET: gap-fill workflow `wf_c2e9547c-1cd` (sonnet summariser -> opus critic for each of M5, M6;
  writes `03_critiques/C_M5_*.md`, `C_M6_*.md`). Workflow 2 phase 0 then runs an architect ADDENDUM that folds M5/M6
  into the ranking and the integrated system before implementation starts.
- 04:35 ET: gap-fill v1 failed at the summarise stage for both (one overshot maxLength caps by ~30-60 chars; one emitted
  invalid JSON). ROOT CAUSE across all failures: agents put the OneDrive path in the JSON and escape the apostrophe
  as \\' which is not legal JSON. Relaunched as `wf_857b02c4-1fe` (critics read files directly; no paths in JSON;
  generous caps; explicit escaping rules).
- 05:05 ET: gap-fill v2 succeeded. M5 (ML layer): REJECT (scores 3/2/3/4/2/3) — keep only the calibration harness
  (PIT/CRPS/coverage on the 391-row prediction ledger) and the zero-shot foundation-TS interval benchmark. M6 (FX /
  take-rate / timing): ADOPT WITH FIXES (3/4/4/5/5/5) — keep the convolution-of-printed-GBV object, single-numeraire fee
  algebra, hedge-once rule, interval likelihoods, Phi; FIX: drop the circular unearned-fee pin, carry fee uplift as a
  range with pass-through theta explicit (+1.1 to +1.8%, not +4.05%), re-estimate the FX lag jointly on lag-0/1/2
  baskets with rounding as an interval (critic: Theo's two-quarter lead is probably right; M6's lambda 0.75 is
  unidentified), recompute determined share (~54% at 5 Nov under lambda 0.75, not 82%).
- Rule for all later workflows: no file paths inside structured returns; generous maxLength (1500) with an
  'aim for half' instruction; agents write long content to disk; JSON strings contain no backslashes or double quotes.

## Resume notes

- Workflow 1 script: `~/.claude/projects/.../workflows/scripts/abnb-revenue-forecast-methods-wf_8fd0fedf-d78.js`;
  resume with `Workflow({scriptPath, resumeFromRunId: "wf_8fd0fedf-d78"})`. Check `journal.jsonl` in the transcript
  dir before assuming cached results are non-empty.
- Loop: dynamic `/loop` with a 30-minute fallback heartbeat; workflow completion notifications are the primary wake.
