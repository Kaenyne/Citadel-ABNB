# Margin build, 13-14 Sep 2026: shared brief for every agent in this run

You are one of several agents working overnight for Krish's team on the Citadel stock pitch on Airbnb (ABNB).
The revenue side is largely settled (3Q26 and 4Q26 from the H2 bridge v3; FY27 by quarter is being audited in
this run). **This run decides how margins are modelled**: adjusted EBITDA margin and its six cost lines, the GAAP
bridge to operating income and EPS, free cash flow, and the margin language management will give on 5 Nov 2026.
Today is 13 Sep 2026 (Saturday night). Prelim memo due 2 Oct 2026; finals 22-24 Oct; the 3Q26 print is 5 Nov 2026.

Read `CLAUDE.md` at the repo root first (the eight non-negotiable rules apply here in full). Then this file.
Then your own prompt in `docs/margin-build/prompts/`.

## Where you work

- **Working tree (read and write):** `C:\Users\krish\citadel-abnb-margins`, branch `krish/margin-build`, cut from
  `origin/main` at `fd4272f` (includes PR #53 Lane 1, PR #32 quarterly nights path, PR #52 bridge v3, PR #35 WS31 margin model).
  Gitignored raw stores (`data/raw/letters`, `transcripts`, `xbrl`, `licensed`, `theo_onedrive`, `inside_airbnb*`, ...) are
  junctioned in from the main tree; treat them as read-only.
- Do NOT touch `C:\Users\krish\citadel-abnb` (main tree) or any other `citadel-abnb-*` worktree.
- **Do not run `git commit`, `checkout`, `merge`, `stash`, `push`.** The orchestrator commits after each stage. Just write files.
- Always double-quote paths in shell. Run scripts from the worktree root; resolve paths with `pathlib` relative to the file.

## Output locations (create the folders; nothing else gets written)

| What | Where |
|---|---|
| Scripts | `analysis/src/margin_build/<NN_slug>/` with a `run.py` that rebuilds the package end to end (exit code 0) and a `README.md` with the command |
| Processed data | `data/processed/margin_build/<NN_slug>/` (CSV; small parquet is fine) |
| Raw pulls (LSEG, Wayback, web) | `data/raw/margin_build/<NN_slug>/` (gitignored by `data/raw/*`; write a manifest CSV of every file with URL, timestamp, sha256 to `data/manifests/margin_build/<NN_slug>.csv`, which IS committed) |
| Note | `docs/margin-build/notes/<NN_slug>.md` |
| Figures | `analysis/figures/margin_build/<NN_slug>_*.png` |
| Registry (stage 2 methods only) | `data/processed/margin_build/registry/<method>__<object>.csv` via the margin harness (`analysis/src/margin_build/10_harness_margin/`) |
| Scratch | `C:\Users\krish\AppData\Local\Temp\claude\C--Users-krish-citadel-abnb\31f75449-dd5c-48ac-9930-274b79541ad2\scratchpad\margin_build\<NN>\` |

Never modify an existing file outside `docs/margin-build/`, `analysis/src/margin_build/`, `data/processed/margin_build/`,
`data/raw/margin_build/`, `data/manifests/margin_build/`, `analysis/figures/margin_build/`, or `model/ABNB_margin_model*.xlsx`
(new file). If an existing file is wrong, record it in your note under "Corrections to existing work" and build a corrected copy in your folder.

## Python

- `python` (repo venv, 3.11): pandas 3, numpy, scipy, statsmodels, scikit-learn, lightgbm, pymc, duckdb, pyarrow, openpyxl.
  Use it for all modelling. It has NO lseg-data, yfinance, pytrends, matplotlib.
- `py -3.13`: pandas 2.3, lseg-data 2.1.1, yfinance, pytrends, matplotlib, pypdf, openpyxl, requests. Use it for LSEG pulls,
  Google Trends, prices, and figures.
- **LSEG / Refinitiv (Workspace desktop is open and logged in; app key in env `LSEG_APP_KEY`):**
  ```python
  import os, lseg.data as ld
  s = ld.session.desktop.Definition(app_key=os.environ["LSEG_APP_KEY"]).get_session(); s.open(); ld.session.set_default(s)
  df = ld.get_data("ABNB.O", ["TR.EBITDAMean", "TR.EBITDAMean.date", "TR.EBITDAMean.periodenddate"],
                   {"SDate": "2021-01-01", "EDate": "2026-09-13", "Frq": "D", "Period": "FQ1"})
  ```
  Tested 13 Sep 23:30: returns consensus EBITDA history. Never print or write the key. Never type credentials anywhere.
  LSEG output is licensed: raw pulls stay under `data/raw/` (gitignored); only derived statistics and small derived
  series (a consensus value per guide/print date with vendor and timestamp) go to `data/processed/`.
- Bloomberg local file (licensed, never commit, never copy out of `data/raw`):
  `data/raw/theo_onedrive/AIRBNB DATA/raw_expansion_licensed/v2_2026-09-05/bloomberg/bbg_extracted_long.csv`
  (sheet `1_Consensus_TS`: BEST_SALES / BEST_EBITDA / BEST_EPS for 1FQ, 2FQ, 1FY, 2FY by obs_date; ABNB, BKNG, EXPE, MAR, HLT, H, IHG).
- Web: WebSearch and WebFetch are available. FRED keyless: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=SERIES`.
  EDGAR needs a User-Agent with an email (`citadel-abnb research ksurapaneni@ufl.edu`). Wayback: `http://archive.org/wayback/available?url=...&timestamp=...`
  and the CDX API `http://web.archive.org/cdx/search/cdx?url=...&output=json&from=2019`. Common Crawl index API blocks after ~40 queries
  (see `analysis/src/cc_airbnb_probe.py` for the cluster.idx route). fool.com rate-limits after ~20 requests; stockanalysis.com needs a browser UA.
  **No live request to any airbnb.com page** (careers, newsroom, help centre included): archives only.

## What already exists on margins (read before you build; do not redo)

- `research/notes/overnight/31_margin-model.md` (+ `31a_mgmt-margin-statements.md`, `31b_operating-profile.md`): the current
  margin model. Six cash cost lines; only cost of revenue is a volume function (elasticity to GBV +1.01); ops & support falls
  ~2.5%/yr per night as a trend; product dev, brand marketing, field ops, G&A are spending decisions. Annual decomposition of
  every margin move since 2019; three forward profiles FY26-28 (historical 34.6 / management 37.4 / base 36.9 at FY28).
  Data: `data/processed/overnight/31a_*.csv`, `31b_*.csv` (overlay parameters, line elasticities, sensitivities). Scripts `analysis/src/overnight/31a_*.py`, `31b_*.py`.
- `research/notes/overnight/30_margin-walk.md`, `data/processed/overnight/30_*.csv`: quarterly margin walk 4Q25 -> 4Q26 by scenario, quarterly P&L.
- `research/notes/overnight/07_ops-and-margin-levers.md`, `data/processed/overnight/07_*.csv`: cost lines per night, lever model, peer benchmark.
- `research/notes/2026-09-05_margin-drivers.md`, `data/processed/abnb_quarterly_costlines.csv` (1Q20-2Q26 GAAP lines),
  `abnb_quarterly_cost_stack_exsbc.csv` (cash lines, SBC by line, D&A, add-backs, per-night), `abnb_margin_bridge.csv`, `abnb_fcf_bridge.csv`.
- `research/notes/predictive/04_margin-and-reaction.md`, `data/processed/predictive/04_margin_predictability*.csv`: what predicts margin (n 23 prints).
- `research/notes/2026-09-05_guidance-margin-items.md`; `data/processed/overnight/02_guidance_ledger.csv` (194 guidance rows incl. margin);
  `02_kpi_panel_quarterly.csv`; `16_consensus_at_print_merged.csv` (EBITDA consensus 8/23 prints); `data/processed/forecast_methods/L0/L0_vintage_register.csv` (frozen, append-only).
- Capital return / SBC / share count: `research/notes/2026-09-05_capital-return-panel.md`, `data/processed/abnb_capital_return_quarterly.csv`.
- Revenue side the margin model consumes: `data/processed/h2_bridge_v3/` (3Q26 nights +9.9%, ADR ex-FX +3.9%; 4Q26 nights +8.1%, ADR ex-FX +4.1%,
  revenue $3,178M, implied guide mid $3,059M), `analysis/src/h1_to_h2_bridge_v3.py`; FY27: `analysis/src/nights_quarterly.py` +
  `data/processed/nights_quarterly_*.csv` + `research/notes/nights_quarterly.md` (PR #32), `data/processed/overnight/29_fy27_*.csv` (WS29),
  `docs/revenue-forecast-strategy/05_backtests/B3_FY27_DECOMPOSITION.md` (band +9.2-11.5%), reverse DCF `docs/reverse_dcf/SYNTHESIS.md`.
- Regional mix: `research/notes/overnight/10_*.md`, `data/processed/overnight/10_*.csv`; FX: `analysis/src/forecast_methods/fx_lag_v2/`;
  seats dilution: `data/processed/adr/15_seats_dilution_*.csv`; revenue by line (Experiences/Services): `data/processed/overnight/14_revenue_by_line_*.csv`.
- Forecast harness (frozen, FORMAT 1.0): `analysis/src/forecast_methods/harness/README.md`. Guide dates W1 (14, targets 1Q23-2Q26) and
  W2 (10, targets 1Q24-2Q26). Margin targets are NOT in its `targets.csv`; stage 2 builds a margin harness that imports its calendar and validator.
- Repo inventory: `docs/2026-09-06_research-inventory.md`; forecast programme: `docs/revenue-forecast-strategy/AGENT_BRIEF.md` (kill list in §6, never quote those numbers).

## Standards (the team has been burned by false positives)

- n is small: 26 quarters of cost lines (1Q20-2Q26), 14 W1 guide dates, 10 W2. State n every time. Backtest point-in-time: refit at each
  guide date using only what was public then; report both windows; a claim must survive both. Compare to a naive baseline
  (same-quarter-last-year margin, trailing-4, y/y-change persistence), to the guide-implied number, and to Street.
- **Bias toward recent quarters.** Airbnb's operating profile changes (2021 reset, 2023 ADR windfall, 2025-26 brand-marketing ramp, AI spend).
  Report every accuracy statistic both equal-weighted and recency-weighted (exponential, half-life 4 quarters) and say when they disagree.
- Pre-register the pass line in your note before running the test. A failed test is written up, not deleted. Count your tests.
- Publish the free-parameter count of every object. Prefer few parameters.
- Every number carries a source (file path, URL, letter quarter, LSEG field + pull timestamp). Do not invent numbers.
- Consensus is the comparison column, never an input to a forecast of the print, except inside a method explicitly built around it (M5).
- Never call a quarter "close to known". Forecast every quarter independently.
- Distinguish: forecasts the actual, forecasts the guide, forecasts the consensus surprise.
- Write for a smart teammate who did not watch you work: bottom line first, tables with n, caveats, then "For the model" (exact series and
  parameters you supply: name, value, unit, source) and "For the 5 Nov card".
- Your final message to the orchestrator: 300-500 words with the key numbers and every file path you wrote. The orchestrator relays it; it will
  not read your full note until synthesis.
- Do not ask the orchestrator questions; make the judgement call, state it, and continue. If something is impossible (access, licence), log it and move on.

## Resume rule

If your prompt starts with `RESUME:`, first list your output folder, read your own note if it exists, and continue from what is on disk.
Do not restart from scratch.
