# Pitch-forecasts run — agent brief

Run started 16 Sep 2026 22:40 local, branch `krish/pitch-forecasts`. Orchestrator: Claude (Fable 5.1) in the main
session. Owner: Krish (asleep; the run is autonomous; a session cron resumes it after any usage cutoff).

## Mission

The team's ABNB short memo (`deck/drafts/memo_v2_short_2026-09-16.md`, PDF `deck/drafts/ABNB_short_memo_draft_2026-09-16.pdf`)
carries dozens of implicit probabilities: what management guides on 5 Nov, what it says about RNPL, how the stock
reacts, each risk and each bonus item. Every one of them must be a defended, data-backed probability produced by
Krish's forecasting flow, so that any number in the pitch can be traced to a research log, an independent audit and
an audit response. Krish is a top-25 Metaculus forecaster; the flow is his, and it is the standard.

The flow, per question (or small batch of related questions):

1. **Forecast (Fable).** Read `C:/Users/krish/.claude/skills/forecast/SKILL.md` and its `references/` and follow it in
   INITIAL mode. Write `docs/pitch-forecasts/questions/<slug>/research-log.md` in the exact schema of
   `references/research-log-format.md`, plus `forecasts/2026-09-17-forecast.json` (schema below).
2. **Audit (Astra).** Codex `gpt-6-astra`, read-only, writes `audits/YYYY-MM-DD-research-audit.md` for the batch:
   reproduces every computation, checks every claim's source and date, attacks the reasoning, and ships a
   dependency-free reproduction script under `audits/`.
3. **Audit response (Fable).** A fresh agent answers every finding (accept / accept in part / reject, with the
   recomputation), revises the research log to revision 2, rewrites `forecasts/2026-09-17-forecast.json` if the
   number moved, and writes `audits/YYYY-MM-DD-audit-response.md`.

Templates: `docs/pitch-forecasts/prompts/`. Model examples of steps 2 and 3: the USD/toman audit and response in
the forecasting repo (copied to `docs/pitch-forecasts/examples/`). Question registry: `docs/pitch-forecasts/QUESTIONS.md`.
Disk-truth state: `py -3.13 analysis/src/pitch_forecasts/state.py`. Ledger: `docs/pitch-forecasts/RUN_STATE.md`.

## Rules (all agents)

1. **Copy, never overwrite.** Never modify a tracked file outside `docs/pitch-forecasts/` and (at the very end, by the
   orchestrator only) `deck/drafts/`. Frozen dirs in `CLAUDE.md` rule 1 stay frozen. Nothing on the kill list
   (`docs/revenue-forecast-strategy/AGENT_BRIEF.md` §6, `docs/margin-build/SYNTHESIS.md` §9) may be quoted as ours.
2. **The repo is the primary source; the web is secondary.** The team holds reams of alternative data and
   point-in-time backtests (data map below). Every question must be researched from the repo first: the guidance
   ledger, the reaction panel, the RNPL statement ledger, the consensus register, the nowcast, the margin build,
   the reverse DCF, the line build, the raw letters and transcripts. Only then search the web, and log every query.
   WebSearch has a session-wide budget shared by every agent: **at most 5 WebSearch calls per question**; prefer
   WebFetch or `curl -sL` on known URLs. Polymarket and Kalshi APIs (see the skill's Environment section) do not
   count against the WebSearch budget.
3. **Proper questions.** Each question in `QUESTIONS.md` has a title, type, resolution criteria, fine print and
   resolution date. Forecast exactly that question. If the criteria are ambiguous, resolve the ambiguity in the log's
   fine-print section by stating the convention you adopted, and forecast under it. Do not change the question.
4. **Answer the question or retry.** If a run produces a number that does not answer the question as written (wrong
   object, wrong date, a conditional when an unconditional was asked, a range with no point, a "cannot forecast"),
   the agent must re-run that question until it does. A note saying "could not answer" is not an output.
5. **Point-in-time discipline.** Consensus values carry vendor and timestamp
   (`data/processed/forecast_methods/L0/L0_vintage_register.csv`); never mix a September consensus into a historical
   guide date. Base rates on management guidance behaviour come from `data/processed/overnight/02_guidance_ledger.csv`
   (every guide since 4Q20, with outcome) and `data/processed/abnb_guidance_reaction_panel.csv` (per-print reaction,
   guide vs Street, nights direction).
6. **The alt-data band is an input, not a question.** The team's 3Q26 nights nowcast (+9.5%, band 8.5–10.0, model path
   9.9 at the top of the band; reviews index walk-forward RMSE 1.48pp vs naive 2.16) is the calculated number the
   alt data exists to produce. Questions that depend on the print (guide language, reaction) condition on that band
   and its error distribution; do not re-forecast the print from the web.
7. **Every forecast carries three independent estimates, an anchor, a pre-mortem and a monitoring calendar** (the
   skill's steps). For binaries: point + credible interval. For MC: full vector. For continuous: the 5/10/25/50/75/90/95
   percentile table. Extreme-probability gate applies.
8. **Risk and bonus questions also quantify impact.** Each risk (R) and bonus (B) log ends with an `## 9. Impact`
   table: if the event happens, the delta to 3Q26 nights (pts), 4Q26 nights (pts), ADR (pts), 4Q26 revenue ($M),
   FY27 revenue ($M), FY26 and FY27 adj. EBITDA margin (pp), FY27 EPS ($), and the stock ($/share) — each line
   sourced to a repo sensitivity (list below) or computed — and the expected value = P × impact. Say plainly when an
   item is immaterial (P × stock impact under $1/share) so the memo can drop it.
9. **Write for the audit.** Claims ledger rows for every load-bearing number with file path or URL, published and
   retrieved dates. A repo file is a source: cite the path and the note that produced it. Complete beats concise.
10. **No submissions, no trading, no external posting.** Files only.

## Data map (read before searching)

Management record
- Letters (official): `data/raw/letters/*.htm` (4Q20–2Q26). Transcripts (mirror): `data/raw/transcripts/web/<Q>.html`.
- Every guide since 4Q20 with outcome and cushion: `data/processed/overnight/02_guidance_ledger.csv`;
  `02_guidance_accuracy.csv`, `02_guidance_cushion_series.csv`, `02_guidance_tells.csv`.
- Management statements on margin: `data/processed/margin_build/05_mgmt_statements_v2/`, note
  `docs/margin-build/notes/05_mgmt_statements_v2.md` (incl. `05_nov2026_scenarios.csv` — the November sentence rule).
- RNPL/bundle/fee/cancellation ledger (60 dated statements, verbatim): `data/processed/overnight2/D/rnpl_statement_ledger.csv`,
  note `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md`; pre-registered 5 Nov thresholds
  `data/processed/overnight2/D/D1_prereg_thresholds.csv`.
- Insider mechanics (what changed 2025–26, disclosure history, "what a good Q4 guide looks like"):
  `docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md`; recent facts `04_recent_facts.md`.
- Catalyst calendar: `research/notes/catalyst_calendar.md`. Competition format: `docs/competition/citadel_2026_format.md`.

Consensus and market
- Point-in-time consensus register (1,330 rows, vendor-stamped, incl. DoltHub weekly history 2021–2026):
  `data/processed/forecast_methods/L0/L0_vintage_register.csv`; note `docs/revenue-forecast-strategy/05_backtests/A1_consensus_vintages.md`, `G1b_dolthub_consensus_history.md`.
- Current consensus (LSEG 11 Sep, n, sd): `data/processed/margin_build/23_final_model/23_vs_consensus.csv`,
  `data/processed/margin_build/03_consensus_pit/`; Bloomberg MODL distribution vs team: `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`.
- Sell-side tape (32 targets, actions, lag behaviour): `data/processed/reverse_dcf/D/`; note `research/notes/reverse_dcf/D_sell-side-dispersion.md`.
- Options (event sd 9.5%, skew, 12M distribution): `data/processed/reverse_dcf/B/`; note `research/notes/reverse_dcf/B_options-implied.md`; ledger `data/processed/abnb_options_ledger.csv`.
- Positioning (SI, ratings, institutional): `data/processed/reverse_dcf/D/D_positioning_summary.csv`, `data/processed/overnight/09_*`.
- Price history: `data/processed/abnb_daily_close.csv` (to 4 Sep; use `py -3.13` + yfinance for later closes; 16 Sep close $167.51).

Stock reaction
- Per-print reactions 1/5/20-day, raw and QQQ-excess: `data/processed/abnb_earnings_reactions.csv`; per-print panel with
  guide-vs-Street, nights direction, margin direction: `data/processed/abnb_guidance_reaction_panel.csv`; regression
  results `abnb_guidance_reaction_results.csv`; by-acceleration `data/processed/overnight/05_reaction_by_accel.csv`;
  executable-return conventions `data/processed/overnight/20_executable_returns.csv`.
- Reaction function re-test (sign rule, n 14/16; guide-vs-Street +1.4–1.9%/1%, fragile): `research/notes/reverse_dcf/C_reaction-function.md`, `data/processed/reverse_dcf/C/`.
- Positioning card and repricing ladder: `research/notes/2026-09-13_market-implied-model.md` §5, §7, §10; `data/processed/reverse_dcf/E/E_repricing_ladder.csv`.
- Big moves with causes: `research/notes/2026-09-05_abnb-major-moves.md`, `data/processed/abnb_big_moves_7pct.csv`.
- Predictive study (what forecasts prints and the stock): `research/notes/predictive/`, `data/processed/predictive/`.
- Red team (what is dead: drift rule, etc.): `docs/revenue-forecast-strategy/05_backtests/RED_TEAM.md`.

Revenue, guide and nights
- Guide × cushion (19/19 beats; trailing-8 cushion +1.86%): `docs/revenue-forecast-strategy/05_backtests/guidance-policy.md`.
- Q4 guide grid and P(below panels): `docs/revenue-forecast-strategy/05_backtests/B2_Q4_GUIDE_EXHIBIT.md`, `data/processed/forecast_methods/`.
- Kernel (λ, weights, backlog): `05_backtests/K0_*`, `K1_*`, `K2_*`, `kernel-lambda.md`; numbers cheatsheet
  `docs/thesis-kernel-topdown/03_NUMBERS_CHEATSHEET.md`.
- H1→H2 bridge v3 (adopted revenue path, 4Q26 $3,178M, implied guide mid $3,059M): `data/processed/h2_bridge_v3/`,
  note `docs/revenue-forecast-strategy/05_backtests/FXSWAP_h2_bridge_kernel_fx.md`; v1 note `research/notes/2026-09-10_h1-to-h2-bridge.md`.
- Nights baseline reconciliation, quarterly nights model (PR #32), NA lap: `research/notes/2026-09-10_nights-baseline-reconciliation.md`, `research/notes/nights_quarterly.md`, `research/notes/na_nights_reconciliation.md`.
- Q3 nowcast (reviews index, external stack, calendar pace, ADR card): `docs/q3nowcast/SYNTHESIS.md`, `research/notes/q3nowcast/`, `data/processed/q3nowcast/`, `data/processed/q3nowcast_v2/`.
- ADR v3 (card, FX estimator, residual, fee migration): `docs/adrv3/SYNTHESIS.md`, `research/notes/adrv3/`, `data/processed/adrv3/`; ADR decomposition `research/notes/2026-09-07_adr-decomposition.md`.
- FX: `05_backtests/fx-lag.md`, `B4_FX_EXHIBIT.md`; `data/processed/overnight/05_fx_*`; FRED cache `data/raw/fred`.
- RNPL: `docs/rnpl-short-audit/` (00–05), `analysis/src/rnpl_short_audit/rnpl_nights_module.py`, `data/processed/rnpl_short_audit/`,
  `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md`, `docs/RNPL_HANDOFF.md`, calendar reopening test `research/notes/overnight2/A_*`.
- Fee migration / host churn: `research/notes/2026-09-07_fee-churn-catalyst.md`, `2026-09-07_fee-churn-recent-followup.md`,
  `research/notes/host_only_fee_history_and_elasticity.md`, `data/processed/fee_churn_*`, `data/processed/listing_churn_*`.
- Regional / consumer / FX mix: `research/notes/overnight/10_regional-and-segment-decomposition.md`, `research/notes/overnight2/B_*`, `C_*`, `data/processed/overnight2/B`, `C`.
- Macro and travel demand (STR, TSA, NTTO, hotels, peers): `research/notes/overnight/05_macro-outlook-and-transmission.md`,
  `data/processed/q3nowcast/G/`, `data/processed/govdata*/`, `docs/govdata/`, `data/processed/peer_readthrough/`, `data/processed/hotel_*`.
- Regulatory: `data/processed/abnb_regulatory_events.csv`, `abnb_regulatory_profile.csv`, `data/processed/regulatory_v2/`, `data/raw/regulatory/`.
- Supply / competition: `research/notes/overnight/11_competition-supply-and-overlays.md`; Inside Airbnb raw under `data/raw/inside_airbnb*` and `~/abnb_ia_capture/` (query with DuckDB; large).

Margins and costs
- Margin build (top-down combination, 5 Nov card, budget identity, floor break-even, M-notes):
  `docs/margin-build/MORNING_REPORT.md`, `SYNTHESIS.md`, `notes/*.md`, `data/processed/margin_build/23_final_model/`.
- Line build and short case: `docs/margin-build/notes/40_line_build.md`, `data/processed/margin_build/40_line_build/`
  (`40_params.csv`, `40_sensitivities.csv`, `40_short_case_*.csv`).
- Financial panel: `data/processed/abnb_driver_history_quarterly.csv`, `data/processed/margin_build/02_financial_panel/`;
  cost lines `data/processed/abnb_quarterly_costlines.csv`; capital return `abnb_capital_return_quarterly.csv`.
- Valuation / reverse DCF: `docs/reverse_dcf/SYNTHESIS.md`, `research/notes/2026-09-12_management-implied-model.md`,
  `research/notes/2026-09-13_market-implied-model.md`, `data/processed/reverse_dcf/market/`, `A/`; multiple-growth slope
  `research/notes/overnight/12_valuation-multiple-regime.md`.
- Pitch workbook: `model/ABNB_pitch_model.xlsx` (read with openpyxl on `py -3.13`); note `docs/2026-09-16_pitch-model-workbook.md`.

Sensitivities to use for impact tables (all sourced in the notes above)
- 1pt of 3Q26 nights ≈ 1.34m nights ≈ $48M of 3Q26 revenue; 1pt of 4Q26 nights ≈ 1.22m nights ≈ $30M of 4Q26 revenue.
- 1pt of ADR ≈ $1.71 of ADR ≈ $259M GBV ≈ $46M of quarterly revenue (3Q26).
- 1pt of FY27 revenue growth ≈ $158M revenue; margin change per 1pt of revenue shortfall: 2H26 0.59pp held / 0.38pp flex; FY27 0.66 / 0.42.
- $48M of S&M = 1.0pp of 3Q26 margin; $0.0666 of 3Q26 EPS per 1pp of margin; FY27 EPS ≈ $0.0014 per $M of EBITDA.
- Stock: +0.40 to +0.48 EV/EBITDA turns per point of forward revenue growth; one turn ≈ $9–10/share; 1pt of FY27
  nights ≈ $4.90/share (joint solve) or $1.50 (fixed multiple); 1pp of FY26 margin sentence = 4.49pp of 4Q26 margin.
- Reaction base rates: decelerating prints post-2022 −5.6% day-1 excess (0 of 8 positive), accelerating +6.0%;
  Q4-guide-below-Street AND nights direction lower: −8.0% mean, −10.9% median (n 5); all prints day-1 rms 8.9%;
  options-implied 5 Nov event sd 9.5%; February Q4 prints positive 6 of 6.

## Output schema: `forecasts/2026-09-17-forecast.json`

```json
{"question_id": "C01", "slug": "q4-revenue-guide-vs-street", "type": "binary|multiple_choice|continuous",
 "revision": 1, "run_date": "2026-09-17", "agent": "fable",
 "final": {"p": 0.55, "ci": [0.45, 0.65]}                      // binary
 // MC: {"vector": {"option A": 0.4, ...}} ; continuous: {"percentiles": {"5":..,"10":..,"25":..,"50":..,"75":..,"90":..,"95":..}, "below_lower": 0.01, "above_upper": 0.02, "unit": "USD m"}
 ,"estimates": {"base_rate": 0.5, "decomposition": 0.6, "anchor": 0.49, "anchor_source": "..."},
 "impact": {"nights_3q26_pts": 0, "nights_4q26_pts": 0, "adr_pts": 0, "rev_4q26_musd": 0, "rev_fy27_musd": 0,
            "margin_fy26_pp": 0, "margin_fy27_pp": 0, "eps_fy27_usd": 0, "stock_usd_per_share": 0,
            "ev_stock_usd_per_share": 0, "material": true, "note": "..."},   // R and B questions only
 "sensitivity": [{"assumption": "...", "moves_to": 0.4}],
 "monitoring": [{"date": "2026-11-05", "event": "...", "action": "..."}],
 "log": "docs/pitch-forecasts/questions/<slug>/research-log.md"}
```

## Orchestration (orchestrator and heartbeat only)

- Batches and question ids: `docs/pitch-forecasts/batches.json`. Stage per batch: `forecast` → `audit` → `response`.
  Disk truth: `py -3.13 analysis/src/pitch_forecasts/state.py` (lists each batch's stage from the files present).
- Forecast and response agents: `Agent` tool, `subagent_type: general-purpose`, model Fable (fallback Opus if Fable
  is rate-limited), at most **4 concurrent**. Prompt = the template in `prompts/` with the batch id substituted.
- Audits: `codex exec --ephemeral -s read-only -C "<repo>" -o <audit path> "$(cat <prompt file>)" < /dev/null`, one at a
  time, launched detached (`analysis/src/pitch_forecasts/run_audit.sh <batch>`), completion marked by
  `audits/<batch>.done`. If Codex fails twice for a batch, run the audit as an independent Opus agent with the same
  prompt and say so in RUN_STATE.
- After every completed stage: append to RUN_STATE.md, `git add docs/pitch-forecasts && git commit`.
- When every batch has a revision-2 log: run batch X01 (scenario MC, reads all forecast JSONs), then write
  `docs/pitch-forecasts/SYNTHESIS.md` (table of every question: P, CI, anchor, |final − anchor|, audit verdict,
  impact and EV for R/B, materiality flag), then update `deck/drafts/memo_v2_short_2026-09-16.md`, the HTML and
  re-render the PDF with the audited probabilities, keeping a change log in `docs/pitch-forecasts/MEMO_CHANGES.md`.
- Never run two Codex audits concurrently; never run method `run.py` packages (they call `score.py`).
