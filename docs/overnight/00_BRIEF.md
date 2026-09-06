# Overnight research run, 6-7 Sep 2026: shared brief for every workstream

You are one of many parallel agents working for Krishang (Krish) Surapaneni's team on the Harvard FAC x Citadel stock pitch on Airbnb (ABNB). The team's goal: turn a large pile of data into (a) a proper driver model of revenue, margins, cash and per-share value, and (b) an honest view of what, if anything, predicts KPIs, income-statement items, guidance and stock moves. Q3 2026 print is 5 Nov 2026; the pitch is ~Dec 2026. Today is 6 Sep 2026. Last close used elsewhere: $181.94 (4 Sep 2026).

## Where you work

- **Working tree (read AND write):** `C:\Users\krish\citadel-abnb-overnight` on branch `krish/overnight-synthesis`. This tree already has every open branch merged in (margin drivers, capital return, guidance margin items, transcript analytics, Inside Airbnb supply, Common Crawl panel, driver model, EU platform/backlog, regulatory forecast, predictive study, plan of attack) plus Theo's merged alt-data layer. Do NOT touch `C:\Users\krish\citadel-abnb` (main tree, has another session's uncommitted work) or any other `citadel-abnb-*` worktree.
- **Do not run git commit / checkout / merge / stash.** Krish's orchestrator commits at the end. Just write files.
- **Your outputs go in these places only** (create subfolders as you like):
  - Note: `research/notes/overnight/NN_<topic>.md` (NN = your workstream number)
  - Scripts: `analysis/src/overnight/NN_<name>.py`
  - Data outputs: `data/processed/overnight/NN_<name>.csv`
  - Figures: `analysis/figures/overnight/NN_<name>.png`
  - Scratch: `C:\Users\krish\AppData\Local\Temp\claude\C--Users-krish-citadel-abnb\fe93ae72-a37b-4547-991f-690c32a0f6a0\scratchpad\NN\`
- Do not edit other people's notes or CSVs. If you find an error in an existing file, record it in your note under "Corrections to existing work".

## Python

- Use `py -3.13` (has pandas 2.3, numpy, scipy, statsmodels, sklearn, matplotlib, yfinance, pytrends, pypdf, openpyxl, requests). The `.venv` python lacks most of these; do not use it.
- Prefer scripts that rebuild your CSVs from raw inputs so a reviewer can re-run them. Header comment: what it reads, what it writes.
- Web access: WebSearch and WebFetch tools are available. FRED keyless CSV: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=SERIES`. EDGAR needs a User-Agent with an email (use `citadel-abnb research ksurapaneni@ufl.edu`). fool.com rate-limits after ~20 requests. stockanalysis.com transcripts need a browser user agent via curl.

## What already exists (read the ones relevant to you before starting; do not redo them)

Notes in `research/notes/`:
- `2026-09-06_predictive-study.md` + `predictive/01..05` : the big "what forecasts what" study (23 prints). Headline: no print-day alpha from beat-vs-guide; nights acceleration sign sets day-1 reaction (17/21); FX→ADR mechanism r -0.95; hotel RevPAR tracks nights but no incremental forecast value; margin nowcast; prior-quarter S&M deleverage hypothesis r +0.59; macro/alt-data nowcasts are 2023-trend artefacts; pitch scorecard.
- `2026-09-05_driver-model.md` : revenue decomposition (nights / ADR ex-FX / FX / take rate), day-1 reaction regression (R² 0.04-0.07), FY26-28 bear/base/bull, football field, reverse DCF.
- `2026-09-05_margin-drivers.md` : XBRL cost lines, ex-SBC cash cost stack, margin bridge, FY26/27 margin scenarios, guidance cushion, ADR vs hotels, FCF bridge, BKNG head-to-head, hotel price monitor.
- `2026-09-05_capital-return-panel.md` : SBC, buybacks, share count, net cash return, cannibal scorecard.
- `2026-09-05_guidance-margin-items.md` : 44 margin guides added to Theo's guidance dataset.
- `2026-09-05_transcript-analytics.md` : analyst roster, topic frequency, "declined to quantify" list from 23 IR transcripts.
- `2026-09-05_inside-airbnb-supply-panel.md` : 13 cities, 168 dumps; like-for-like price (read the price-basis caveats), churn, host concentration, entire-home share.
- `2026-09-05_cc-listing-panel.md` : Common Crawl matched listings 2021-26; survival, review velocity, professionalisation. No prices exist in CC.
- `2026-09-05_eu-platform-and-backlog.md` : Eurostat platform nights (32 countries, monthly) vs ABNB EMEA; XBRL backlog indicators (unearned fees, funds held).
- `2026-09-05_regulatory-forecast-profile.md` + `research/regulatory/` : regulatory database (events, factor register, quantification), probability-weighted impact profile.
- `2026-09-05_abnb-major-moves.md` : 41 moves ≥7% attributed; earnings reactions 1/5/20 day.
- `2026-09-04_abnb-pitch-landscape.md`, `2026-09-04_abnb-pitch-catalogue.md` : what other pitches argue, KPIs used, valuation methods, debates.
- `2026-09-04_management-timeline.md`, `2026-09-05_third-bridge-transcripts.md` (digest of 5 expert calls; the PDFs are in `data/raw/licensed/third-bridge/`), `research/airbnb_earnings_call_study.md` (older call study).
- `docs/2026-09-05_plan-of-attack.md` : the team's plan; branches 3 (consensus at call), 5 (Google Trends), 8 (weekly captures), 9 (expectations map) are NOT done.
- Theo's package: `theos-past-research/` (guidance dataset in `research/guidance/data/normalized/`: guidance_items.csv, guidance_events.csv, quarterly_actuals.csv, market_returns.csv, consensus_snapshots.csv (all rows missing), driver_observations.csv, source_excerpts.csv). His alt-data hypotheses H-001..H-012 all ended inconclusive. `docs/2026-09-05-abnb-data-extraction-v2.md` and `docs/CODEX_HANDOFF_V2.md` describe his acquisition layer; `data/manifests/` lists every file he pulled (bulk files are on his external volume, NOT here).
- `ABNB-Crossover/` : method-transfer kit from a prior pitch (ideas backlog, access map, templates).
- `model/assumptions.md` : current model assumptions with sources. There is no Excel model yet.

Data in `data/processed/` (51 files + `predictive/`): quarterly KPIs (`abnb_quarterly_kpis_from_study.csv`, `abnb_driver_history_quarterly.csv`), cost lines (`abnb_quarterly_costlines.csv`, `abnb_quarterly_cost_stack_exsbc.csv`), guidance vs actual (`abnb_revenue_guidance_vs_actual.csv`), reactions (`abnb_earnings_reactions.csv`, `abnb_reaction_inputs.csv`), daily closes (`abnb_daily_close.csv`), capital return, valuation scenarios, Inside Airbnb panels, CC panels, Eurostat platform nights, booking curves (`booking_curves_by_market.csv`, blocked-rate proxy, NOT occupancy), `market_summary_2026.csv`, EDGAR KPI sentences (`abnb_filing_kpis.csv`), backlog indicators, regulatory profile, options ledger. Read `data/README.md` for provenance of each.

Raw in `data/raw/` (junctions to the main tree): `letters/` (23 shareholder letters 4Q20-2Q26 as 8-K Ex. 99.1 HTML), `regulatory/transcripts/` (IR call transcripts 2023-Q1..2026-Q2 PDF+JSON, 2026-Q2 txt), `xbrl/ABNB_companyfacts.json`, `fred/`, `bea/`, `eurostat/`, `inside_airbnb/` (337 listing dumps for 13 cities), `commoncrawl/`, `licensed/third-bridge/` (5 expert-call PDFs, do not quote at length), `regulatory/` documents.

Transcripts before 2023: `https://stockanalysis.com/stocks/abnb/transcripts/` (curl with a browser UA) or the IR CDN pattern in `analysis/src/download_abnb_transcripts.py`.

## Standards (these matter; the team has been burned by false positives)

- n is small (23 prints, 14 post-2022). State n, use leave-one-out or walk-forward against a naive baseline (prior-year, AR(1), or the guide), and report negatives alongside positives. Count how many tests you ran.
- Point-in-time discipline: a feature only counts if it was knowable before the print/guide it claims to predict. Say when each input becomes available.
- Every number carries its source (file path, URL, or letter quarter). Do not invent numbers; if you can't get one, say so.
- Distinguish: (i) forecasts the KPI, (ii) forecasts the guide, (iii) forecasts the stock reaction. Most things do at most one.
- Write for a smart teammate who did not watch you work. Lead with the bottom line, then evidence, then caveats, then "what to build next". Plain sentences, tables for numbers, no hype.
- Add a final section "For the model" listing the exact parameters/series your work supplies to the driver model (name, value, unit, source), and a section "For the 5 Nov card" if your work bears on the Q3 print.
- Your final message back to the orchestrator: a ~300-500 word summary of findings with the file paths you wrote. The orchestrator will not read your full note until synthesis, so put the important numbers in the summary.
