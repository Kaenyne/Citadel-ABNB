# Lines — registry for digger briefs

Environment: `python3` = 3.13 / pandas 3.0; fallback `.venv-pd2/bin/python` = pandas 2.3.3. Record here which interpreter each package needed.

## H0 — Printed history 1Q23–2Q26 (Sonnet, wave 1)
Judge: "Do your historicals tie to the filings, line by line?"
Sources: `data/processed/airbnb_quarterly_kpis.csv`; `data/processed/abnb_edgar_quarterly_kpis.csv`; `data/processed/abnb_quarterly_costlines.csv`; `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv`; `data/processed/abnb_driver_history_quarterly.csv`; 10-Q/10-K figures quoted in `docs/margin-build/notes/40_line_build.md`.
Repro: `analysis/src/abnb_costlines_from_xbrl.py`; `analysis/src/nights_quarterly.py`; `analysis/src/margin_build/02_financial_panel/` (read-only comparison of the three KPI files against each other and against one filing per year, quoted).
Packages: `data/processed/` KPI files above (read); `analysis/src/margin_build/02_financial_panel`.
Conflicts: G&A is on the ex-lodging-reserve basis in the pitch workbook (4Q23 ~$1bn reserve in a reconciling line); three KPI files exist and must agree; nights, ADR, GBV, revenue, take rate, adj. EBITDA, the five cash cost lines, SBC, D&A, share count.

## D1 — 3Q26 nights, level and y/y (Opus, wave 1)
Judge: "Why 146.3m when 28 sell-side estimates average 148.9m and the lowest is 147.0m?"
Sources: `docs/q3nowcast/SYNTHESIS.md`; `analysis/src/q3nowcast/E4_build_index.py`, `E5_backtest.py`, `E6_nowcast.py`, `G2_external_backtests.py`, `G3_rank_sources.py`; `data/processed/q3nowcast/`; `analysis/src/q3nowcast_v2/E/` and `data/processed/q3nowcast_v2/E/`; `docs/revenue-forecast-strategy/05_backtests/WPK_reviews-index-2023-vintage.md`; `SR_QUARTER_SUBMISSION_READINESS_v1.md` ("reviews revalidation"); `data/processed/nights_baseline_reconciliation.csv`; `docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/` and `risk-q3-nights-accelerates/`; `deck/drafts/memo_v3_short_2026-09-17.md` "Nights".
Repro: `E5_backtest.py` and `E6_nowcast.py` from the processed review counts (the raw 2023 mirror lives on Krish's machine; `~/abnb_ia_capture/` holds Theo's daily capture; state exactly what was reproducible without raw); `G2_external_backtests.py` for the external stack.
Packages: `analysis/src/q3nowcast`, `analysis/src/q3nowcast_v2/E`, `data/processed/q3nowcast`, `data/processed/q3nowcast_v2`.
Conflicts: memo v3 quotes the reviews index at 0.68x naive; WPK-A finds 0.68 was W2-only with stale training and the honest re-run is 0.76/0.84, failing the 0.75 hurdle; the SR note says not to present 0.68x as validated. The 148.9m bar is Bloomberg MODL (quote as an aggregate with date only). Calendar pace failed its backtest (sign inverted).

## D2 — 4Q26 nights and the RNPL / ex-NA lap (Opus, wave 1 follow-on; wave 2)
Judge: "How much of the 2026 re-acceleration laps in 4Q26, and how do you know it is not demand?"
Sources: `analysis/src/overnight2/` D module and `docs/overnight2/SYNTHESIS.md`; `data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv`; `analysis/src/na_nights_reconciliation.py` and `data/processed/na_nights_lap_scenarios.csv`, `na_nights_decomposition.csv`; `05_backtests/B3_FY27_DECOMPOSITION.md`; `05_backtests/ALPHA_F_RNPL.md` and `analysis/src/forecast_methods/rnpl_v2/`; `docs/pitch-forecasts/questions/risk-q4-nights-print-meets-street/` (adopted Q4 object, mean 8.61, sd 2.28); `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md`.
Repro: `analysis/src/na_nights_reconciliation.py`; `rnpl_v2/run.py`; the overnight2 D scripts.
Packages: `analysis/src/overnight2`, `analysis/src/forecast_methods/rnpl_v2`, `data/processed/overnight2`, `data/processed/forecast_methods/rnpl_v2`.
Conflicts: D-08 (adopt the ex-NA lap, 8.0–8.2%) is an open team decision; D-11 says chaining the 4Q26 ex-NA lap with PR #32's 1Q27 lap double-counts ~0.8pp; the cohort engine bounds the cancellation drag at −0.2 to −0.9pt; the 34-market calendar test found no cancellation signature.

## D3 — FY27 nights path (Sonnet, wave 2)
Judge: "What does FY27 nights growth have to be for your revenue, and what is it made of?"
Sources: `analysis/src/margin_build/06_fy27_path_v2/` and `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv`; `analysis/src/h1_to_h2_bridge_v3.py` and `data/processed/h2_bridge_v3/`; `05_backtests/REBASE_h2_bridge_v3_nights_adr.md`.
Repro: `analysis/src/h1_to_h2_bridge_v3.py`; `06_fy27_path_v2/run.py` (or its script; read its README).
Packages: `analysis/src/margin_build/06_fy27_path_v2`, `data/processed/margin_build/06_fy27_path_v2`, `data/processed/h2_bridge_v3`.
Conflicts: memo v3 gives FY27 nights +6.4% (global lap) to +8.2% (NA-only) against +8–9% in the price; bridge v3 base is +10.9% revenue. State which nights path each revenue number uses.

## D4 — ADR ex-FX and its decomposition (Opus, wave 1)
Judge: "Your ADR sits on consensus for 3Q26; where does the price leg come from and how much is mix?"
Sources: `docs/adrv3/`, `analysis/src/adrv3/`, `data/processed/adrv3/`; `research/notes/2026-09-07_adr-decomposition.md`; `model/ADR_decomposition.xlsx`; `05_backtests/L3_ADR_HOTEL_RESULTS.md`, `L3_ADR_HOTEL_AUDIT_REPAIR_v1.md`, `L3_ADR_HOTEL_PREREG.md`; `analysis/src/adr/05_size_mix.py`; `data/processed/abnb_size_regression.csv`, `insideairbnb_price_by_accommodates.csv`; `docs/pitch-forecasts/questions/risk-adr-residual-persists/`, `bonus-adr-residual-reverts/`.
Repro: `analysis/src/adrv3/` run script (read its README); `analysis/src/adr/05_size_mix.py` (rebuilds a cache in ~30 s).
Packages: `analysis/src/adrv3`, `analysis/src/adr`, `data/processed/adrv3`, `data/processed/adr`.
Conflicts: "half of ADR growth is bigger units" is on the kill list (it is +0.46–0.8pp; bedroom elasticity 0.23); the like-for-like price residual (+2.8–3.6pp) is unidentified; the L3 ADR audit found historical inputs unavailable at guide dates, so the decomposition is descriptive, not a validated forecast; the ADR nowcast does not beat naive.

## D5 — ADR FX and revenue FX by quarter (Sonnet, wave 1)
Judge: "How much of 4Q26 revenue growth is FX, and is it already known?"
Sources: `analysis/src/forecast_methods/fx_lag_v2/` (`run.py`, `README.md`); `data/processed/forecast_methods/fx_lag_v2/`; `data/processed/overnight/05_fx_schedule.csv`; `05_backtests/B4_FX_EXHIBIT.md`, `fx-lag.md`, `VERIFY_fx-lag_r1.md`, `FXSWAP_h2_bridge_kernel_fx.md`; `docs/pitch-forecasts/questions/q3-revenue-fx-integer/`, `risk-dollar-weakens/`.
Repro: `python3 analysis/src/forecast_methods/fx_lag_v2/run.py` using the cached `fx_daily_2026-09-11.csv` (do not run `fetch_fx_v2.py`; it calls FRED).
Packages: `analysis/src/forecast_methods/fx_lag_v2`, `data/processed/forecast_methods/fx_lag_v2`.
Conflicts: the −3.4pp Q4 FX step and "82% of Q4 FX already determined" are on the kill list; adopted numbers are 4Q26 revenue FX +1.0pp (CS +0.3–2.2) and an effective lag of 0.4–0.5 quarters; memo v3 says revenue FX is "84% observed for 4Q26", which must be reconciled with the kill-list wording.

## D6 — GBV and the regional cross-check (Sonnet, wave 2)
Judge: "Does nights times ADR give your GBV, and does the regional build sum to it?"
Sources: identity; `05_backtests/X_REGIONAL_KERNEL_OD_FX.md`, `R_REGIONAL_REFRESH.md`; `analysis/src/forecast_methods/regional_kernel_v1/`; `data/processed/airbnb_regional_revenue_quarterly.csv`; `05_backtests/PREREG_ABNB-INT-v1.md` D-04 (block ii: 147.38M nights / $180.15 / $26,550M).
Repro: `regional_kernel_v1/run.py`; recompute the identity from H0 and the D1/D4 decided values.
Packages: `analysis/src/forecast_methods/regional_kernel_v1`, `data/processed/forecast_methods/regional_kernel_v1`.
Conflicts: the object-by-object hybrid breaks the GBV identity by −3.1pp (D-04); WP-X returned underpowered.

## D7 — Take rate and the fee migration (Opus, wave 2)
Judge: "Is take rate an input or an output, and what does the single host fee do to it?"
Sources: `05_backtests/B1_TAKE_RATE_RECONCILIATION.md`; `fee-takerate.md`; `analysis/src/forecast_methods/fee_takerate/`, `fee_panels/`, `fee_panel_v1/`; `05_backtests/L3_FEE_RESULTS_v1.md`, `L3_FEE_AUDIT_CLOSE_v3.md`, `A3_fee_panels.md`, `N_THETA_DID.md` (if present); `data/processed/airbnb_adr_takerate_quarterly.csv`; `docs/pitch-forecasts/questions/q3-take-rate-above-1810/`, `risk-single-fee-take-rate-accretion-stated/`, `bonus-take-rate-guided-down/`.
Repro: `fee_takerate/run.py`; recompute 3Q26 take rate 18.14% and P(≥18.10%) by GBV band from B1's inputs.
Packages: `analysis/src/forecast_methods/fee_takerate`, `fee_panels`, `fee_panel_v1` and their `data/processed` folders.
Conflicts: pass-through θ is unidentified ("0.83–1.41" was a detection window); "+4.05% fee uplift" is on the kill list; the 1.71M quote panel is not fee-inclusive; no detectable fee effect on the printed take rate through 2Q26 (n 20).

## R1 — Kernel: λ by season and the lag weights (Opus, wave 1)
Judge: "Why should revenue be two-thirds last quarter's bookings plus one-third the quarter before?"
Sources: `analysis/src/forecast_methods/kernel_lambda/` (`run.py`, `kernel.py`, `README.md`); `kernel_engine_v2/`; `kernel_phi_v2/`; `kernel_leadtime_v2/`; notes `kernel-lambda.md`, `VERIFY_kernel-lambda_r1.md`, `K1_KERNEL_WEIGHTS_AND_BACKLOG.md`, `K2_KERNEL_FROM_LEAD_TIMES.md`, `K0_KERNEL_ENGINE_v2.md`, `GD_DECISION_REPORT_v2.md`, `GD_HORIZON_RESULTS_v1.md`, `GD_HORIZON_ELIGIBILITY_ADDENDUM_v1.md`; `data/processed/forecast_methods/gbv_decision_0915_v1/`; `~/Citadel-ABNB-untracked/.../net_gbv_reverse_v1` and `NET_GBV_REVERSE_HANDOFF_v1.md`.
Repro: `python3 analysis/src/forecast_methods/kernel_lambda/run.py` through the wrapper (it re-registers; the wrapper restores); `kernel_engine_v2/run.py`.
Packages: `kernel_lambda`, `kernel_engine_v2`, `kernel_phi_v2` under `analysis/src/forecast_methods/` and `data/processed/forecast_methods/`.
Conflicts: fixed (⅔/⅓, 4 seasonal parameters) vs joint (7 parameters) — Willem's audit finds joint beats fixed but loses to a simple guide-growth baseline at the next guide; the ⅔ weight is PIT-optimal (0.65–0.70), not identified from the ledger (φ₁+φ₂ 0.58–0.64); λ_Q4 12.03% with a three-year range of 0.17pp.

## R2 — 3Q26 revenue: kernel vs guide+cushion vs bridge (Opus, wave 2)
Judge: "You say 3Q26 revenue beats and you do not trade it; what is the number and why three of them?"
Sources: `K1_KERNEL_WEIGHTS_AND_BACKLOG.md` ($4,795M ledger-only, $4,816M combined); `B1_TAKE_RATE_RECONCILIATION.md`; `data/processed/h2_bridge_v3/` ($4,804M); `analysis/src/forecast_methods/live_block_v2/`; `PREREG_ABNB-INT-v1.md` D-01; `05_backtests/SCOREBOARD_v2.md` (guide×cushion RMSE ratio 0.377/0.319); LSEG 3Q26 $4,744M via `L0_vintage_register.csv`; guide $4,690–4,770M.
Repro: `live_block_v2/run.py`; recompute kernel 3Q26 from H0 GBV and R1 λ; recompute guide×(1+cushion) from R3.
Packages: `analysis/src/forecast_methods/live_block_v2`, `data/processed/forecast_methods/live_block_v2`.
Conflicts: D-01 is open (guide+cushion $4,816M vs kernel $4,804M as the card value); memo v3 uses $4,804M.

## R3 — Guide cushion, trailing eight (Sonnet, wave 1)
Judge: "Airbnb beat its guide 19 of 19 times; how much of that is mechanics?"
Sources: `analysis/src/forecast_methods/guidance_policy/` (`run.py`, `lib.py`); `data/processed/forecast_methods/guidance_policy/`; notes `guidance-policy.md`, `VERIFY_guidance-policy_r1.md`, `_r2.md`; `data/processed/abnb_revenue_guidance_vs_actual.csv`; `data/processed/overnight/02_guidance_ledger.csv`.
Repro: `python3 analysis/src/forecast_methods/guidance_policy/run.py` through the wrapper.
Packages: `analysis/src/forecast_methods/guidance_policy`, `data/processed/forecast_methods/guidance_policy`.
Conflicts: the 9/9 guide-below-Street drift rule as a tradeable signal, any p-value for it, and M5's hierarchical cushion model are on the kill list; cushion mean +1.86%, median +1.79%, sd 1.006pp.

## R4 — 4Q26 guide midpoint the model implies (Opus, wave 2)
Judge: "What guide do you expect on 5 Nov, and what is the Street's number for the same object?"
Sources: `05_backtests/B2_Q4_GUIDE_EXHIBIT.md` ($3,161M, 80% $3,012–3,312); `analysis/src/forecast_methods/guidance_policy_v2/`; `data/processed/h2_bridge_v3/` (implied guide mid $3,059M); `docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/` (C01 0.72; guide mid p50 $3,100M); `GD_DECISION_REPORT_v2.md`; `data/processed/forecast_methods/gbv_decision_0915_v1/`; `A1_consensus_vintages.md` (Street revenue ≠ guide consensus).
Repro: `guidance_policy_v2/run.py`; recompute the implied guide from R2 and R3.
Packages: `analysis/src/forecast_methods/guidance_policy_v2`, `data/processed/forecast_methods/guidance_policy_v2`, `gbv_decision_0915_v1`.
Conflicts: three midpoints in the record ($3,161M B2; $3,059M bridge v3; $3,100M pitch-forecasts p50) against a Street revenue mean of $3,157–3,162M that is not a guide consensus; D-07 (no-fee-step guide as headline) is open.

## R5 — 4Q26 and FY26 revenue (Sonnet, wave 2)
Judge: "Walk me from 3Q26 to FY26 revenue."
Sources: `analysis/src/h1_to_h2_bridge_v3.py`; `data/processed/h2_bridge_v3/`; `REBASE_h2_bridge_v3_nights_adr.md`; `06_fy27_path_v2` quarterly path.
Repro: `python3 analysis/src/h1_to_h2_bridge_v3.py` through the wrapper.
Packages: `data/processed/h2_bridge_v3`.
Conflicts: 4Q26 $3,178M (bridge v3) vs the Street $3,157–3,162M; memo's short case $2,966M comes from `40_line_build` §8b, not the bridge.

## R6 — FY27 revenue and its band (Opus, wave 3)
Judge: "FY27 +11% is the Street; you have +10.9% base and +4.5% short. Which is the pitch, and what is the honest band?"
Sources: `05_backtests/B3_FY27_DECOMPOSITION.md` (+9.18 to +11.52% across w); `06_fy27_path_v2`; `ALPHA_F_RNPL.md` (FY27 nights +6.4%); `docs/pitch-forecasts/questions/q1-27-revenue-guide-growth/`, `q1-27-nights-guide-above-82/`; `40_line_build` short case revenue path; `citadel-abnb-rnpl-balance-sheet` memory note: B3 has no lap and its w-band collapses on λ re-fit.
Repro: the B3 package (find under `analysis/src/forecast_methods/` by grep "B3"); `06_fy27_path_v2`.
Packages: the B3 package and `06_fy27_path_v2`.
Conflicts: "any FY27 level edge without the +9.2–11.5% band" is on the kill list; the short case (+4.5%) is a scenario, not a forecast; the run's F02 median 1Q27 guide growth is +10.5%.

## C1 — Cost of revenue · C2 — Operations and support · C3 — Product development · C5 — G&A ex lodging reserve (Sonnet, wave 2; one digger per line)
Judge: "What drives this cost line, and what did the 10-Q say about it?"
Sources: `analysis/src/margin_build/40_line_build/run.py`; `data/processed/margin_build/40_line_build/40_params.csv`, `40_lines_quarterly.csv`, `40_annual.csv`, `40_backcast.csv`; `docs/margin-build/notes/40_line_build.md`; `docs/margin-build/audit/CODEX_LINE_BUILD_CHECK.md`; `data/processed/abnb_quarterly_costlines.csv`; `analysis/src/margin_build/M1_driver_lines/`, `M6_cycle_flex/`; `docs/pitch-forecasts/questions/bonus-ai-hosting-cost-step/` (C1).
Repro: `python3 analysis/src/margin_build/40_line_build/run.py` through the wrapper, watching `data/processed/margin_build/40_line_build` and `model/ABNB_margin_line_build.xlsx` (~40 s). Only one of C1/C2/C3/C5 runs it; the others read its committed outputs and recompute their line from `40_params.csv` in a scratch script saved under their receipt folder.
Packages: `analysis/src/margin_build/40_line_build`, `data/processed/margin_build/40_line_build`.
Conflicts: the line build says 3Q26 costs grow 11.5% at budget; every parameter must name its 10-Q source; cash lines are GAAP less SBC and still contain D&A.

## C4 — Sales and marketing, the swing line (Opus, wave 1)
Judge: "Why is S&M the whole FY27 disagreement, and what if management just cuts it?"
Sources: everything in C1's list, plus `analysis/src/margin_build/23_final_model/` (`README.md`; `MARGIN_VERIFY_ONLY=1` mode), `data/processed/margin_build/23_final_model/`, `docs/margin-build/SYNTHESIS.md` (§1, §4, §9 kill list, §11), `docs/margin-build/audit/AUDIT_RESPONSE.md`, `M5_street_bias/`, `M3_guide_policy_margin/`, `docs/pitch-forecasts/questions/fy27-sm-share-above-219/`, `bonus-marketing-cut-signalled/`.
Repro: `MARGIN_VERIFY_ONLY=1 python3 analysis/src/margin_build/23_final_model/run.py` (~4 min; writes only `_verify/`; delete it after saving its comparison output to the receipt folder); `40_line_build/run.py` if C1's digger has not already run it this wave (coordinate: never concurrently).
Packages: `analysis/src/margin_build/23_final_model`, `40_line_build`, `M3_guide_policy_margin`, `M5_street_bias` and their data folders.
Conflicts: 3Q26 S&M $781M +33.5% (post-audit) vs $790M +35% (pre-audit); FY27 S&M 21.9–23.5% of revenue vs the Street's implied 21.04%; peer cost elasticity k 0.14 with SE ≈ 0.30 is imprecise, not zero; cash-cost elasticity 0.364; the combination fails its test at h ≥ 2, so FY27 is a spending scenario.

## C6 — Adjusted EBITDA and margin, 3Q26 to FY27 (Opus, wave 2)
Judge: "Pick one FY27 margin. Why 34.6% or 35.7%, and what does the Street's 36.5% require?"
Sources: `23_final_model` outputs (`final-margin__combined`, `combined_dollar_from_margin`), `docs/margin-build/SYNTHESIS.md` §2, §5–§8, §11; `40_line_build/40_annual.csv`; `docs/pitch-forecasts/questions/fy26-margin-sentence/`, `q4-margin-direction-sentence/`, `fy27-margin-guide/`, `risk-q3-margin-sandbagged/`; `analysis/src/margin_build/10_harness_margin/` (read only; never run its scorer); `data/processed/margin_build/20_scoreboard/`.
Repro: `MARGIN_VERIFY_ONLY=1` run if C4's digger has not already saved one this wave (share the receipt; do not run concurrently); recompute 3Q26 margin 49.9% and dollars $2,399M from the committed member scores and weights.
Packages: `analysis/src/margin_build/23_final_model`, `data/processed/margin_build/23_final_model`, `20_scoreboard`.
Conflicts: FY27 34.64% (calibrated run) vs 35.7% (line build) vs 36.45% Street; 3Q26 49.9% (run) vs 50.4% (line build in memo v3); "nothing in this build forecasts the margin ratio better than the Street beyond h=0".

## C7 — SBC, D&A, interest, tax, share count, EPS (Sonnet, wave 3)
Judge: "How do you get from EBITDA to $5.93 and $4.58 of EPS?"
Sources: `analysis/src/margin_build/M7_below_ebitda/` and `data/processed/margin_build/M7_below_ebitda/M7_parameter_sheet.csv`; `40_line_build` (`40_annual.csv`, `40_short_case_summary.csv`, `40_short_case_quarterly.csv`); `data/processed/abnb_capital_return_quarterly.csv` and `analysis/src/capital_return_panel.py`; `analysis/src/abnb_exsbc_stack.py`; `docs/pitch-forecasts/questions/bonus-sbc-step-up/`, `bonus-interest-income-falls/`, `risk-buyback-upsize/`.
Repro: `M7_below_ebitda` run script; `capital_return_panel.py`; recompute EPS from decided C6 and the M7 rules.
Packages: `analysis/src/margin_build/M7_below_ebitda`, `data/processed/margin_build/M7_below_ebitda`, `analysis/src/capital_return_panel.py` outputs.
Conflicts: adjusted EBITDA excludes $1.8bn of FY26 SBC (35% of EBITDA); share count 597m diluted at 16 Sep; buyback renewal at pace is already in the count.

## C8 — FCF and SBC-adjusted FCF (Sonnet, wave 3)
Judge: "What does the stock yield on cash, and is FCF timing or level?"
Sources: `analysis/src/abnb_fcf_bridge.py`, `data/processed/abnb_fcf_bridge.csv`; `abnb_exsbc_stack.py`, `data/processed/abnb_quarterly_cost_stack_exsbc.csv`; grep `research/notes/` for "FCF" and "quality of growth" (the study found FCF misread in timing, ~$106M permanent).
Repro: `python3 analysis/src/abnb_fcf_bridge.py` through the wrapper.
Packages: `data/processed/abnb_fcf_bridge.csv`, `data/processed/abnb_quarterly_cost_stack_exsbc.csv`.
Conflicts: memo says "~3% SBC-adjusted FCF yield, needs 16% FCF growth on a reverse DCF"; tie to V3.

## V1 — Street rows, vendor and date stamped (Sonnet, wave 1)
Judge: "Which consensus, from whom, as of when?"
Sources: `data/processed/forecast_methods/L0/L0_vintage_register.csv` (frozen; read only); `analysis/src/forecast_methods/L0/`, `L0_dolthub_v2/`, `consensus_stamp_v2/`; notes `A1_consensus_vintages.md`, `M_CONSENSUS_2026-09-13.md`, `G1b_dolthub_consensus_history.md`, `LANE2_DATA_CONVENTION_AUDIT.md`, `docs/thesis-kernel-topdown/lane2/CONVENTION.md`; `data/processed/margin_build/03_consensus_pit/`; memo v3 for the Bloomberg MODL aggregates (28 estimates, 148.9m mean, 12 Sep).
Repro: `L0/test_l0.py` (pytest; read-only); `consensus_stamp_v2/run.py` if it is offline-capable (read its README first; no network stamping in this programme).
Packages: `analysis/src/forecast_methods/consensus_stamp_v2`, `L0_dolthub_v2` (read), `data/processed/forecast_methods/consensus_stamp_v2`.
Conflicts: Yahoo = Alpha Vantage = one LSEG-family panel; Zacks Q4 $3,200M vs LSEG $3,158M; never a September value at a historical date; DoltHub quoted externally as Zacks needs a human decision (WP-O G1b); Bloomberg figures enter only as dated aggregates.

## V2 — Exit multiple and the turns-per-point rule (Opus, wave 1)
Judge: "Why 16.5x, and why does one point of growth move the multiple half a turn?"
Sources: `analysis/src/forecast_methods/valuation_v1/` (`run.py` without `--refresh`, `valuation_page.md`, `tests/`); `05_backtests/V_VALUATION_RECONCILIATION.md`, `REFUTE_V_*.md`; `docs/overnight/FINAL_SUMMARY.md`; `research/notes/overnight/` valuation note (12_ or 13_; grep "football"); `data/processed/abnb_valuation_scenarios.csv`, `abnb_valuation_sensitivity.csv`, `abnb_multiples_today.csv`, `abnb_vs_bkng_annual.csv`; `deck/drafts/memo_v0_2026-09-11.md` branch analogues.
Repro: `python3 analysis/src/forecast_methods/valuation_v1/run.py` and its pytest through the wrapper.
Packages: `analysis/src/forecast_methods/valuation_v1`, `data/processed/forecast_methods/valuation_v1`.
Conflicts: fair exit 13.5/16.5/18.5x replaced the old 18/22/25.5x ($248 base was the multiple, not the business); +0.48 turns per point of forward growth is a descriptive regression with four parameters and inherited vintages; memo v3 uses 15.7x Street / 19.0x short-case EV/FY27 EBITDA at $167.51.

## V3 — Reverse DCF, market-implied and management-implied (Sonnet, wave 3)
Judge: "What growth is the price paying for?"
Sources: `analysis/src/reverse_dcf/` (mgmt_implied_*, market, A–E scripts), `data/processed/reverse_dcf/`, `docs/reverse_dcf/`; `model/ABNB_management_implied.xlsx`, `model/ABNB_market_implied.xlsx`; `data/processed/abnb_reverse_dcf.csv`.
Repro: the reverse_dcf run script(s) through the wrapper.
Packages: `analysis/src/reverse_dcf`, `data/processed/reverse_dcf`.
Conflicts: the joint-solve prices in memo v3 ($143 at ~7.5% NTM growth; $150 at 8.6%) come from this package; the short-case price is not in the run and was interpolated.

## V4 — Scenario prices and their probabilities (Opus, wave 3)
Judge: "Where do 26/45/29 and $148 come from, and why is the December median only $166?"
Sources: `docs/pitch-forecasts/questions/scenario-probabilities/` (X01), `close-15dec-2026/` (S02), `day1-move-5nov/` (S01), `close-12feb-2027/` (S03); `docs/pitch-forecasts/SYNTHESIS.md`; `docs/pitch-forecasts/audits/`; `analysis/src/pitch_forecasts/`; `adopted_print_states_v2.json` and `x01_joint.py` (find under the question folders); memo v3 "Scenarios" and "5 Nov disclosure gates".
Repro: `x01_joint.py` and the S02 reaction-function script through the wrapper (they should be deterministic; if seeded Monte Carlo, record the seed).
Packages: `docs/pitch-forecasts/questions/*` (read; write nothing there), `analysis/src/pitch_forecasts`.
Conflicts: print partition 26/45/29 (12-month object) vs disclosure gates 14/17/55/14 (5 Nov object); the −8 to −13% event claim was withdrawn; probability-weighted 15 Dec close $167.3 vs 12-month fundamental $148.

## V5 — The call (Theo and Claude, wave 4)
Judge: "Long or short, target, horizon, and what makes you wrong?"
Sources: the decided V1–V4 lines and the workbook's implied return by scenario; `05_backtests/PREREG_ABNB-INT-v1.md`; `deck/drafts/lane4_v2/review_v2/decision_register.md`; memo v3 recommendation block.
Repro: none; a formula line (`V5 = probability-weighted target / spot − 1`) plus a recorded decision.
Conflicts: WP-H is still `human` on the workboard; START_HERE (15 Sep) records no adopted direction; memo v3 asserts SHORT $143.

## E1 — 5 Nov print partition (Sonnet, wave 3)
Judge: "What is the probability the print accelerates, and on what distribution?"
Sources: `docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/` and `risk-q3-nights-accelerates/` (R01 0.39, R02 0.26); `a09_v2_print_distribution.py` and `adopted_print_states_v2.json` (find under `docs/pitch-forecasts/` or `analysis/src/pitch_forecasts/`); N(9.5, 1.70).
Repro: run `a09_v2_print_distribution.py` through the wrapper; recompute P(<10.0) 0.614, P(10.0–10.6) 0.126, P(≥10.6) 0.260 from N(9.5, 1.70).
Packages: `analysis/src/pitch_forecasts`.
Conflicts: management-delivery constructions give 0.57–0.82 and are published at zero weight; Kalshi mids untraded since 29 Jul.

## E2 — Guide-below-Street, descriptor, FY-sentence probabilities (Opus, wave 2)
Judge: "0.72 that the guide comes in below the Street: below what, and how was it built?"
Sources: `docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/` (C01), `q4-nights-bucket/` (C02), `fy26-margin-sentence/` (C04), `fy26-revenue-guide-language/` (C03), their audits and audit responses under `docs/pitch-forecasts/audits/`; `GD_DECISION_REPORT_v2.md`; `data/processed/overnight/02_guidance_ledger.csv`; `guidance_policy` nights-bucket words.
Repro: the C01 research log's computation (reproduce its P(below) given nights < 10.0 = 0.795 and ≥ 10.6 = 0.567 from its stated inputs) through the wrapper.
Packages: `analysis/src/pitch_forecasts`; question folders read-only.
Conflicts: C01 leans on kernel arithmetic that Willem's GD audit finds loses to a guide-growth baseline at the next guide; the Street mean used ($3,161M, LSEG family) is a revenue consensus, not a guide consensus; 8 of 17 historical descriptors resolve to the "moderate" word.

## E3 — Day-1 and 15 Dec reaction (Opus, wave 3)
Judge: "If you are right on 5 Nov, what does the stock do, and on how many observations?"
Sources: `analysis/src/abnb_guidance_reaction.py`; `data/processed/abnb_guidance_reaction_panel.csv`, `abnb_guidance_reaction_results.csv`, `abnb_earnings_reactions.csv`, `abnb_reaction_regression.csv`, `abnb_reaction_regression_loo.csv`, `abnb_big_moves_7pct.csv`; `analysis/src/big_move_reaction_stats.py`; `analysis/src/forecast_methods/returns_v1/` (23 next-open events); `docs/pitch-forecasts/questions/day1-move-5nov/` (S01), `close-15dec-2026/` (S02); `data/processed/abnb_options_ledger.csv` (event sd 9.0%).
Repro: `python3 analysis/src/abnb_guidance_reaction.py` and `returns_v1/run.py` through the wrapper; the S01 joint draw script.
Packages: `analysis/src/forecast_methods/returns_v1`, `data/processed/forecast_methods/returns_v1`, reaction CSVs above.
Conflicts: the historical "guide below and nights guided lower" cell is n 5 (4 of 5 down, median −10.9%) and is a base rate, not the model; the run's base-case day is median −5.1%, P(≤−8%) 0.37; unconditional day median −2.1%.

## E4 — Flip rules and thresholds (Sonnet, wave 3)
Judge: "What number on 5 Nov makes you cover?"
Sources: `05_backtests/PREREG_ABNB-INT-v1.md`; `D_CARD_ADDENDUM_LAMBDA.md`; `data/processed/forecast_methods/kernel_phi_v2/C5_control_chart_5nov.csv`; `LANE2_LIVE_SCORE_SHEET.md`; memo v3 "5 Nov score sheet" and "Risks" item 1 (flip: nights ≥10.3% with a bundle figure ≥2.5pt); AGENT_BRIEF §4 flip rule (take rate ≥18.10% on GBV ≥$26.3bn and Q4 nights "low double digit").
Repro: recompute the λ thresholds (λ_Q3 < 17.09% warning, < 16.93% escalate, on $27,867M) and the take-rate/GBV pair from the decided R1, D6, D7.
Packages: none to run; read-only.
Conflicts: two flip rules in the record (AGENT_BRIEF §4 vs memo v3 risk 1); D-10's refutation condition was written two incompatible ways.
