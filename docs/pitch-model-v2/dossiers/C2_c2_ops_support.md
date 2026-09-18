# C2 — Operations and support

## 1. Header
- Line: C2 · Judge's question: "What drives this cost line, and what did the 10-Q say about it?"
- Digger: sonnet · Date: 2026-09-18 · Commit: e6d9832 (branch `theo/pitch-model-v2`; the brief named b098ac2, an ancestor — `git diff --stat b098ac2 e6d9832` on every file cited below returns nothing, i.e. unchanged)

**One-paragraph answer.** Operations & support is built as "same quarter last year, per booking, split into a shrinking AI-linked slice and a growing payroll slice": `ops = [ops[q-4] × v × (1 + AI decline%) × (bookings_q / bookings[q-4]) + ops[q-4] × (1 − v) × (1 + fixed growth%)] × (1 + RNPL uplift%)`, with `v = 0.215` calibrated exactly on the 1H26 identity (ops 1H26/1H25 = 624/591 = 1.056 = v × 0.87 × 1.112 + (1 − v) × 1.08). The 10-Qs and calls said, specifically: "support cost per booking" fell 10% (1Q26 call) and 16% (2Q26 call) as AI resolves ">40% of issues" without an agent; the 1H26 10-Q MD&A itemises the rest as payroll (+$14M / +$27M), customer relations (+$3M / +$10M, the +$10M explicitly "higher make-good payouts and related case reserves") and insurance (+$7M); the FY25 10-K names the AI-exposed piece as third-party contact cost run by "13,000 contingent workers." Because `v` is only 21.5% of the line, the AI narrative covers a fifth of operations & support, not the whole thing. At the guide-anchored base case this puts 3Q26 at $361.4M (7.52% of revenue, +5.4% y/y) and FY27 at $1,377.9M (8.70% of revenue, +5.7% y/y). A structural fact worth flagging up front: **the 3Q26 base case's EBITDA does not move at all when ops parameters are shocked** (every ops sensitivity row shows `d_3q26_ebitda_musd = 0.0`) — the sentence-reconciliation mechanism (DEC-0011) reallocates the gap between ops, marketing and hosting to hit management's stated margin, so 3Q26 is pinned by the budget, not by any one line's assumptions; FY27 has no such reconciliation and moves fully with the ops parameters. Independently, the two econometric objects in this repo that model the same panel column (`ops_cash_musd`, in M1's nights-elasticity spec and M6's booking-cycle-flex spec) show the underlying nights/booking relationship is real and significant (M6: booking elasticity 0.44, t = 3.4) but its **forecast** is a statistical tie with a trend-aware ("drift") baseline in both W1 and W2 — not a proven edge, and not a proven failure either.

## 2. The number

**Sources.** All rows come from the bottom-up line build (`40_line_build`, 15 Sep 2026 build note; every parameter in `40_params.csv` carries a named 10-K/10-Q/call source) per DEC-0011, which the brief binds as the workbook's cost stack for this batch. `base` = `40_lines_quarterly.csv` / `40_annual.csv` scenario `base`. `short` = `40_short_case_quarterly.csv` scenario `short_costs_at_budget` (nights-lap + RNPL revenue override; ops dollars are **not** frozen — they scale with the short case's own bookings path and additionally carry the +4% RNPL cancellation-cost overlay that base/breaker hold at 0%). `breaker` = `40_line_build`'s own documented favourable **cost column** (`cost_bull`: `v` 0.27 vs 0.215 base, AI decline −18%/−14% vs −14%/−10%, fixed growth 6% vs 8%) on the base revenue path.

### Operations & support in USD m

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 3Q26 | 361.4 | 350.0 | 375.8 | USD m | 2026-09-11 data / 2026-09-15 build |
| base | 4Q26 | 318.3 | 308.0 | 331.1 | USD m | 2026-09-11 / 15 |
| base | 1Q27 | 319.1 | 309.6 | 331.2 | USD m | 2026-09-11 / 15 |
| base | 2Q27 | 341.0 | 330.5 | 354.2 | USD m | 2026-09-11 / 15 |
| base | 3Q27 | 381.8 | 358.4 | 412.2 | USD m | 2026-09-11 / 15 |
| base | 4Q27 | 336.1 | 315.2 | 363.1 | USD m | 2026-09-11 / 15 |
| base | FY26 | 1,303.7 | 1,282.0 | 1,330.9 | USD m | 2026-09-11 / 15 |
| base | FY27 | 1,377.9 | 1,313.7 | 1,460.8 | USD m | 2026-09-11 / 15 |
| short | 3Q26 | 375.0 | — | — | USD m | 2026-09-15 |
| short | 4Q26 | 329.2 | — | — | USD m | 2026-09-15 |
| short | 1Q27 | 329.3 | — | — | USD m | 2026-09-15 |
| short | 2Q27 | 352.0 | — | — | USD m | 2026-09-15 |
| short | 3Q27 | 409.4 | — | — | USD m | 2026-09-15 |
| short | 4Q27 | 360.1 | — | — | USD m | 2026-09-15 |
| short | FY26 | 1,328.1 | — | — | USD m | 2026-09-15 (built in this dossier; not carried in `40_annual.csv`) |
| short | FY27 | 1,450.8 | — | — | USD m | 2026-09-15 (built in this dossier) |
| breaker (cost_bull) | 3Q26 | 350.0 | — | — | USD m | 2026-09-15 |
| breaker (cost_bull) | 4Q26 | 308.0 | — | — | USD m | 2026-09-15 |
| breaker (cost_bull) | 1Q27 | 309.6 | — | — | USD m | 2026-09-15 |
| breaker (cost_bull) | 2Q27 | 330.5 | — | — | USD m | 2026-09-15 |
| breaker (cost_bull) | 3Q27 | 358.4 | — | — | USD m | 2026-09-15 |
| breaker (cost_bull) | 4Q27 | 315.2 | — | — | USD m | 2026-09-15 |
| breaker (cost_bull) | FY26 | 1,282.0 | — | — | USD m | 2026-09-15 |
| breaker (cost_bull) | FY27 | 1,313.7 | — | — | USD m | 2026-09-15 |
| *memory: actual* | panel | 3Q25 $343.0M / 7.71% | 4Q25 $303.0M / 8.97% | FY25 $1,237.0M / 10.1% | 1H26 $624.0M (1Q26 $301.0M / 2Q26 $323.0M) | | 2026-09-18 (H0) |

`low`/`high` for base is the `cost_bear`/`cost_bull` bracket at the same (base) revenue path from `40_lines_quarterly.csv`/`40_annual.csv` — this is a cost-parameter dispersion band, not a formal confidence interval, and it is the natural bracket for a line whose bear/bull cost columns are already named and sourced. `low`/`high` for `short` and `breaker` are left blank: `breaker` (`cost_bull`) already **is** the low end of that same bracket, and `short` has no separately published bound of its own (it is a single overlay case, `short_costs_at_budget`; the second short row, `short_with_q4_marketing_cut`, changes only the marketing line, not ops).

### Operations & support as % of revenue, and y/y growth

| scenario | 3Q26 | 4Q26 | FY26 | FY27 |
|---|---|---|---|---|
| base | 7.52% / +5.4% | 10.01% / +5.0% | 9.14% / +5.4% | 8.70% / +5.7%¹ |
| short | 8.01% / +9.3% | 11.10% / +8.6% | 9.53% / +7.4% | 9.73% / +9.2%¹ |
| breaker (cost_bull) | 7.29% / +2.0% | 9.69% / +1.6% | 8.99% / +3.6% | 8.30% / +2.5%¹ |
| *cost_bear (the high side of base's bracket)* | 7.82% / +9.6% | 10.42% / +9.3% | 9.33% / +7.6% | 9.23% / +9.8%¹ |

¹ FY27 y/y is not carried in `40_annual.csv` (no FY26 y/y column is populated for FY27 rows); computed here as FY27 ops ÷ FY26 ops − 1 for the same scenario, from the same committed cells.

**The number that answers the judge.** At $4,804.0M of 3Q26 base revenue (the same denominator C1/C4 use), **1.0pp of 3Q26 margin is $48.0M**, so operations & support's $361.4M is worth 7.52 points of margin *by definition of the ratio* — but **not by construction of the model**: every ops-parameter sensitivity in `40_sensitivities.csv` shows `d_3q26_ebitda_musd = 0.0` (e.g. +0.10 to `ops_variable_share`, +3pts to `ops_fixed_growth`, +4pts to either AI-decline rate). The reconciliation step (DEC-0011: "3Q26 sentence a budget") reallocates the $97M evidence-vs-sentence gap between ops (implicitly, via `evidence_costs3`), marketing (70%) and hosting (30%) so that **any** line's 3Q26 assumption change is offset dollar-for-dollar by less marketing/hosting addition, leaving total 3Q26 cash costs — and EBITDA — unchanged. The FY27 margin sensitivities are where ops actually moves the model: +0.10 to `ops_variable_share` = +0.09pp FY27 margin / +$0.02 EPS; +3pts to `ops_fixed_growth` = −0.20pp / −$0.04; +4pts (slower decline) to `ops_variable_decline_fy27` = −0.08pp / −$0.02.

### 2a. Model inputs (machine-readable)

Per DEC-0011 the workbook's cost stack is `40_line_build` and management's 3Q26 sentence is treated as a budget. `ops_pct_rev` is operations & support over each scenario's own revenue path. Driver sub-lines (`ops_variable`, the AI/third-party-contact-cost slice; `ops_fixed`, the payroll/insurance/customer-relations slice) are given for 3Q26 base only, as required. `ops_rnpl_overlay_musd` is the +4%-per-booking RNPL cancellation-cost add given only in the short scenario (base/breaker hold the overlay parameter at 0%).

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| ops_musd | base (line build) | 3Q26 | 361.44 | USD m | 40_lines_quarterly.csv ops_cash, scenario base; params ops_variable_share 0.215 (1H26 10-Q identity: ops 624/591=1.056, "support cost per booking" −10% 1Q26 call / −16% 2Q26 call), ops_variable_decline_2h26 −14.0% (same calls), ops_fixed_growth 8.0% (1H26 10-Q payroll +$14M/+$27M, customer relations +$3M/+$10M, insurance +$7M) |
| ops_musd | base (line build) | 4Q26 | 318.29 | USD m | 40_lines_quarterly.csv ops_cash, scenario base; same params |
| ops_musd | base (line build) | 1Q27 | 319.09 | USD m | 40_lines_quarterly.csv ops_cash, scenario base; params ops_variable_decline_fy27 −10.0% (Chesky 4Q25/2Q26 calls: AI "continue to decline" as it moves to voice, no number given), ops_fixed_growth 8.0% held into FY27 |
| ops_musd | base (line build) | 2Q27 | 340.97 | USD m | 40_lines_quarterly.csv ops_cash, scenario base; same FY27 params |
| ops_musd | base (line build) | 3Q27 | 381.76 | USD m | 40_lines_quarterly.csv ops_cash, scenario base; same FY27 params |
| ops_musd | base (line build) | 4Q27 | 336.06 | USD m | 40_lines_quarterly.csv ops_cash, scenario base; same FY27 params |
| ops_musd | base (line build) | FY26 | 1303.73 | USD m | 40_annual.csv ops_cash, FY26 base = 1Q26 $301M + 2Q26 $323M (10-Q actuals) + 3Q26/4Q26 build |
| ops_musd | base (line build) | FY27 | 1377.88 | USD m | 40_annual.csv ops_cash, FY27 base |
| ops_musd | short | 3Q26 | 374.97 | USD m | 40_short_case_quarterly.csv, scenario short_costs_at_budget; base-column ops params on the short case's own nights-lap bookings path, plus overlay rnpl_ops_uplift_pct 4.0% (2Q26 10-Q customer relations "+$10M" on "higher make-good payouts and related case reserves"; 1Q26 10-Q "+$3M refunds and credits") |
| ops_musd | short | 4Q26 | 329.18 | USD m | 40_short_case_quarterly.csv, scenario short_costs_at_budget |
| ops_musd | short | 1Q27 | 329.27 | USD m | 40_short_case_quarterly.csv, scenario short_costs_at_budget |
| ops_musd | short | 2Q27 | 352.01 | USD m | 40_short_case_quarterly.csv, scenario short_costs_at_budget |
| ops_musd | short | 3Q27 | 409.42 | USD m | 40_short_case_quarterly.csv, scenario short_costs_at_budget |
| ops_musd | short | 4Q27 | 360.09 | USD m | 40_short_case_quarterly.csv, scenario short_costs_at_budget |
| ops_musd | short | FY26 | 1328.15 | USD m | built here (`c2_ops_short_annual.csv`): 1H26 actual $624.0M (10-Q) + 3Q26/4Q26 short-case build; not carried in 40_annual.csv, which only holds the SCN scenarios |
| ops_musd | short | FY27 | 1450.79 | USD m | built here (`c2_ops_short_annual.csv`): sum of the four short-case FY27 quarters |
| ops_musd | breaker (cost_bull) | 3Q26 | 350.01 | USD m | 40_lines_quarterly.csv ops_cash, scenario cost_bull; params ops_variable_share 0.27 bull, ops_variable_decline_2h26 −18.0% bull (same 1Q26/2Q26 call language, bull column), ops_fixed_growth 6.0% bull (same 1H26 10-Q items, bull column) |
| ops_musd | breaker (cost_bull) | 4Q26 | 307.99 | USD m | 40_lines_quarterly.csv ops_cash, scenario cost_bull |
| ops_musd | breaker (cost_bull) | 1Q27 | 309.59 | USD m | 40_lines_quarterly.csv ops_cash, scenario cost_bull; ops_variable_decline_fy27 −14.0% bull |
| ops_musd | breaker (cost_bull) | 2Q27 | 330.49 | USD m | 40_lines_quarterly.csv ops_cash, scenario cost_bull |
| ops_musd | breaker (cost_bull) | 3Q27 | 358.37 | USD m | 40_lines_quarterly.csv ops_cash, scenario cost_bull |
| ops_musd | breaker (cost_bull) | 4Q27 | 315.21 | USD m | 40_lines_quarterly.csv ops_cash, scenario cost_bull |
| ops_musd | breaker (cost_bull) | FY26 | 1281.99 | USD m | 40_annual.csv ops_cash, FY26 cost_bull |
| ops_musd | breaker (cost_bull) | FY27 | 1313.66 | USD m | 40_annual.csv ops_cash, FY27 cost_bull |
| ops_pct_rev | base (line build) | 3Q26 | 7.52 | pct | on revenue 4804.04 |
| ops_pct_rev | base (line build) | 4Q26 | 10.01 | pct | on revenue 3178.11 |
| ops_pct_rev | base (line build) | 1Q27 | 10.45 | pct | on revenue 3053.13 |
| ops_pct_rev | base (line build) | 2Q27 | 8.46 | pct | on revenue 4028.98 |
| ops_pct_rev | base (line build) | 3Q27 | 7.23 | pct | on revenue 5280.73 |
| ops_pct_rev | base (line build) | 4Q27 | 9.70 | pct | on revenue 3465.76 |
| ops_pct_rev | base (line build) | FY26 | 9.14 | pct | on revenue 14268.14 |
| ops_pct_rev | base (line build) | FY27 | 8.70 | pct | on revenue 15828.61 |
| ops_pct_rev | short | 3Q26 | 8.01 | pct | on revenue 4680.90 |
| ops_pct_rev | short | 4Q26 | 11.10 | pct | on revenue 2965.87 |
| ops_pct_rev | short | 1Q27 | 11.61 | pct | on revenue 2835.53 |
| ops_pct_rev | short | 2Q27 | 9.35 | pct | on revenue 3762.97 |
| ops_pct_rev | short | 3Q27 | 8.21 | pct | on revenue 4988.17 |
| ops_pct_rev | short | 4Q27 | 10.82 | pct | on revenue 3326.83 |
| ops_pct_rev | short | FY26 | 9.53 | pct | built here; on revenue 13932.77 (1H26 actual + short 3Q26/4Q26) |
| ops_pct_rev | short | FY27 | 9.73 | pct | built here; on revenue 14913.51 (sum of short FY27 quarters) |
| ops_pct_rev | breaker (cost_bull) | 3Q26 | 7.29 | pct | base revenue path 4804.04 |
| ops_pct_rev | breaker (cost_bull) | 4Q26 | 9.69 | pct | base revenue path 3178.11 |
| ops_pct_rev | breaker (cost_bull) | 1Q27 | 10.14 | pct | base revenue path 3053.13 |
| ops_pct_rev | breaker (cost_bull) | 2Q27 | 8.20 | pct | base revenue path 4028.98 |
| ops_pct_rev | breaker (cost_bull) | 3Q27 | 6.79 | pct | base revenue path 5280.73 |
| ops_pct_rev | breaker (cost_bull) | 4Q27 | 9.09 | pct | base revenue path 3465.76 |
| ops_pct_rev | breaker (cost_bull) | FY26 | 8.99 | pct | base revenue path 14268.14 |
| ops_pct_rev | breaker (cost_bull) | FY27 | 8.30 | pct | base revenue path 15828.61 |
| ops_variable_musd (driver sub-line) | base | 3Q26 | 70.65 | USD m | 40_lines_quarterly.csv ops_variable; the AI/third-party-contact-cost slice = ops[3Q25]=343.0 × v 0.215 × (1 − 0.14) × bookings_3Q26/bookings_3Q25; params ops_variable_share 0.215 and ops_variable_decline_2h26 −14.0% (1Q26 call "-10%", 2Q26 call "-16%") |
| ops_fixed_musd (driver sub-line) | base | 3Q26 | 290.80 | USD m | 40_lines_quarterly.csv ops_fixed; the payroll/customer-relations/insurance slice = ops[3Q25]=343.0 × (1 − 0.215) × (1 + 0.08); param ops_fixed_growth 8.0% (1H26 10-Q payroll +$14M/+$27M, customer relations +$3M/+$10M, insurance +$7M) |
| ops_rnpl_overlay_musd | short | 3Q26 | 14.42 | USD m | = ops_cash − (ops_variable+ops_fixed) = 360.55 × 0.04; param rnpl_ops_uplift_pct 4.0% (2Q26 10-Q customer relations "+$10M" "higher make-good payouts and related case reserves"; 1Q26 10-Q "+$3M refunds and credits") |
| ops_rnpl_overlay_musd | short | 4Q26 | 12.66 | USD m | same overlay, 4Q26 short-case base |
| ops_rnpl_overlay_musd | short | 1Q27 | 12.66 | USD m | same overlay, 1Q27 short-case base |
| ops_rnpl_overlay_musd | short | 2Q27 | 13.54 | USD m | same overlay, 2Q27 short-case base |
| ops_rnpl_overlay_musd | short | 3Q27 | 15.75 | USD m | same overlay, 3Q27 short-case base |
| ops_rnpl_overlay_musd | short | 4Q27 | 13.85 | USD m | same overlay, 4Q27 short-case base |
| ops_rnpl_overlay_musd | short | FY26 | 27.08 | USD m | built here: sum of the 3Q26+4Q26 overlay (1H26 actual carries no overlay) |
| ops_rnpl_overlay_musd | short | FY27 | 55.80 | USD m | built here: sum of the four FY27-quarter overlays |

## 3. Derivation chain
1. Filing/call facts → 1Q26 earnings call ("support cost per booking" −10%) and 2Q26 earnings call (−16%, ">40% of issues resolved without an agent"); 1H26 10-Q MD&A itemised deltas (payroll +$14M / +$27M, customer relations +$3M / +$10M — the +$10M explicitly "higher make-good payouts and related case reserves" from cancellations, the +$3M "refunds and credits" — and insurance +$7M); FY25 10-K "13,000 contingent workers" (the third-party contact-cost headcount the AI metric covers); 4Q25/2Q26 call language that the AI decline "continue[s]" as it "moves to voice," with no number given for FY27. All quoted with source in `data/processed/margin_build/40_line_build/40_params.csv` (rows `ops|*`, `overlay|rnpl_ops_uplift_pct`).
2. `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` → `ops_cash` = GAAP operations & support less SBC; 3Q25 $343.0M, 4Q25 $303.0M, 1Q26 $301.0M, 2Q26 $323.0M (1H26 $624.0M — the exact numerator of the `v = 0.215` calibration identity).
3. `analysis/src/margin_build/40_line_build/run.py` `build()` lines 164–169 → `d_var = ops_variable_decline_fy27 if is27 else ops_variable_decline_2h26`; `ops_var = ops[prev] × v × (1 + d_var/100) × bookings_q / bookings[prev]`; `ops_fix = ops[prev] × (1 − v) × (1 + ops_fixed_growth/100)`; `ops = (ops_var + ops_fix) × (1 + rnpl_ops_uplift_pct/100)`. `prev` is the actual same-quarter-last-year value for 3Q26/4Q26/1Q27/2Q27 (from the panel) and the **same scenario's own already-built** 3Q26/4Q26 row for 3Q27/4Q27 — the recursion this dossier's recompute script re-implements explicitly (see §5).
4. **The 3Q26 sentence-reconciliation step does not touch the ops formula at all** (`run.py` lines 130–146): `recon_gap` is computed from an `evidence_costs3` total that already includes the (possibly shocked) `ops3` estimate, and 100% of `recon_gap` is then split 70/30 into `mkt_q3_step`/`hosting_step` only — never back into ops. The net effect (confirmed in `40_sensitivities.csv`): shocking any ops parameter changes the ops line itself but leaves 3Q26 total cash costs, and therefore 3Q26 EBITDA, exactly unchanged (`d_3q26_ebitda_musd = 0.0` on every ops row), because the marketing/hosting addition shrinks by the same amount evidence-based ops grew. This holds only while `recon_gap ≥ 0` at the shocked parameter value (true for every shock actually tested).
5. `data/processed/margin_build/40_line_build/40_lines_quarterly.csv`, columns `ops_variable`/`ops_fixed`/`ops_cash`/`ops_per_booking`, rows `3Q26…4Q27` × scenario (`base`, `cost_bull`, `cost_bear`, …); `40_annual.csv` same columns for FY26/FY27; `40_short_case_quarterly.csv` for the short case (scenario `short_costs_at_budget`, which carries the `rnpl_ops_uplift_pct = 4.0` overlay from `run.py`'s `SHORT["overlays"]` dict).
6. Independent re-derivation (this dossier, read-only): `data/processed/pitch_model_v2/receipts/C2/c2_ops_recompute.py` reads `40_params.csv` directly and re-implements the recursion in step 3 (using panel actuals for the four quarters whose "previous year" is an actual, and the same scenario's own committed 3Q26/4Q26 row for 3Q27/4Q27) to recompute `ops_variable`, `ops_fixed` and `ops_cash` for all 18 committed cells (base ×6 quarters, cost_bull ×6, short ×6); every cell matches the committed CSVs to **0.0** (`c2_ops_recompute_check.csv`). The FY26/FY27 short-case aggregates (not carried in `40_annual.csv`) are built in the same script using the same "1H26 actual + 2H26/2027 build" convention `run.py` §4 uses for the SCN scenarios (`c2_ops_short_annual.csv`).
7. Backtest chain (a different object, same panel column `ops_cash_musd`): `analysis/src/margin_build/M1_driver_lines/` (nights-elasticity spec, exponent 0.76) and `analysis/src/margin_build/M6_cycle_flex/` (booking-cycle-flex spec, `k_ops` = 0.44) both fit and score this column in `data/processed/margin_build/22_discussion_group_A/groupA_paired_vs_drift.csv` and the two packages' own backtest CSVs.

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-15 | `docs/margin-build/notes/40_line_build.md` (+ `40_line_build/` outputs) | Operations & support FY27 $1,378M = **8.7%** of revenue (down from FY26's 9.1%); 3Q26 $361M (10.1%→9.1%→8.7% across FY25/FY26/FY27); "the AI decline applies to ~22% of the line, the rest is payroll growing 8%" | **Governs the dollar object per DEC-0011.** Latest note on this line |
| 2026-09-14 | `docs/margin-build/audit/CODEX_LINE_BUILD_CHECK.md` (gpt-6-astra, read-only) | Finding 5 (Medium): the note's linear-approximation calibration text ("ops 1H26/1H25 = 1.056 = v × 0.87 × 1.112 + (1−v) × 1.08 → v = 0.19") is wrong; the exact multiplicative rule solves to **v ≈ 0.2152**, not 0.19 | **Superseded/fixed.** The committed `40_params.csv` already carries `ops_variable_share = 0.215` (matches the audit's corrected value), and the current build note text (line 133-134) says so explicitly ("0.215, was 0.19 from a linear approximation") — this dossier reproduces the already-fixed 0.215, not the withdrawn 0.19 |
| 2026-09-13 (D4 correction 2026-09-15) | `docs/margin-build/notes/M6_cycle_flex.md` §7 (pre-D4) | "G&A and ops & support do not survive both windows at both weightings" against `seasonal_naive`: `ops_cash_musd` ratio 0.832 (W1 eq) / **1.066** (W2 eq, fails) / 0.927 (W1 rw) / 0.981 (W2 rw); survives eq/rw = False/True | **Superseded (softer baseline).** The harsher, later drift-baseline re-scoring below is what M6's own D4 section calls "the honest baseline for a growing dollar line" |
| 2026-09-13 (D4 correction 2026-09-15) | `docs/margin-build/notes/M6_cycle_flex.md` D4 (R14) | Re-scored `k_ops` = 0.44 against `seasonal_naive_drift`: W1 ratio **0.988** (t −0.06, p 0.95, 8/14 better), W2 ratio **0.960** (t −0.16, p 0.87, 6/10 better) — a statistical tie in both windows, no significant edge either way | **Governs.** This is the operative, current test of the ops driver-elasticity relationship |
| 2026-09-13 (D4 correction 2026-09-15) | `docs/margin-build/notes/M1_driver_lines.md` D4 (R14) | Same re-scoring on M1's nights-elasticity spec (`b_elastic_rw`, exponent 0.76): W1 ratio **0.946** (t −0.27, p 0.79, 9/14 better), W2 ratio **0.919** (t −0.33, p 0.74) — also a tie, right-signed but not significant | **Governs alongside M6's.** "Ops beats `pct_rev_last4` but only ties the seasonal naive (0.80-1.02) — half right" (M1 §4d, pre-D4 baseline) is the softer, earlier claim; the drift-scored tie above is the current one |
| 2026-09-13 | `docs/margin-build/notes/M6_cycle_flex.md` D8 (WS23 weights) | `k_ops` = 0.44 given weight **0.5**: "right sign, t 3.4, but a tie against drift at the line level" | Governs the recommended use: the *regression coefficient* (nights/booking elasticity) is real and significant; the *forecast* is not proven better than a trend baseline |
| 2026-09-18 | `docs/pitch-model-v2/dossiers/H0_h0_history.md` §5, §8.1 | `ops_cash` actuals 1Q23–2Q26 tie exactly to the panel across 14 quarters | Governs the actuals used for y/y growth and the FY26 base |
| 2026-09-18 | `docs/pitch-model-v2/dossiers/C1_c1_cost_of_revenue.md` §2, §7 | Same revenue denominators ($4,804.0M 3Q26 base, $15,828.6M FY27 base), same 70/30 marketing/hosting reconciliation split, same short-case FY26 revenue ($13,932.8M) | Consistent; cited for cross-line consistency in §7 below |

**Web fetches: 0.** Every filing/call fact this line needs (the 1Q26/2Q26 "support cost per booking" percentages, the 1H26 10-Q MD&A payroll/customer-relations/insurance deltas, the FY25 10-K's "13,000 contingent workers," the 2Q26 "material increase" and make-good language) is already quoted with its source inside `40_params.csv`. Nothing here required a fetch the five-fetch budget could have settled.

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/C2/receipt.json`
- Package run cited (not re-run; hard constraint): `data/processed/pitch_model_v2/receipts/C1/receipt.json` — C1 ran `python3 analysis/src/margin_build/40_line_build/run.py` through the wrapper this batch (commit 11b3d398bcc12c74597855084420e81aa5a1631e, exit 0, wall 0.7s, `restored: true`), producing the committed `40_lines_quarterly.csv`/`40_annual.csv`/`40_short_case_quarterly.csv` this dossier reads.
- This dossier's own command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id C2 --watch data/processed/pitch_model_v2/receipts/C2 --cmd "python3 data/processed/pitch_model_v2/receipts/C2/c2_ops_recompute.py"` · Exit: 0 · Wall: 0.2s · Interpreter: python3 (3.13.0 / pandas 3.0.0) · `restored: true`
- Output: `data/processed/pitch_model_v2/receipts/C2/c2_ops_recompute_check.csv`, column `d_ops_cash` (committed − recomputed), all 18 rows (base ×6, cost_bull ×6, short ×6) = **0.0** exactly · Committed values: `40_lines_quarterly.csv` `ops_cash`, scenario base, 3Q26/4Q26 = **361.443087 / 318.287094**; scenario cost_bull = **350.007223 / 307.986430**; `40_short_case_quarterly.csv` `ops_cash`, 3Q26/4Q26 = **374.971462 / 329.175777** · Tolerance: ±$0.01M · **Match: yes**
- FY26/FY27 short-case aggregates (`c2_ops_short_annual.csv`) and the base/breaker FY26/FY27 cells straight from `40_annual.csv` (`c2_ops_annual_base_breaker.csv`) are written alongside as supporting evidence, not separately tolerance-checked (they are direct sums/reads, not independent formula re-derivations).
- No `restored: false` was seen; no manual restore was required.

## 6. Test record

The panel column is `ops_cash_musd`. Two different forecasting *objects* have been scored against it in the harness; the line build's own recursive same-quarter-last-year formula (the object quoted in §2) has not itself been scored there — only the 1H26 calibration identity (0.0% error, by construction, not a test) and a FY25 out-of-sample backcast. All rows PIT, h=0 unless noted.

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 | 14 | `ops_cash_musd`, M1 `lines_v2\|b_elastic_rw` (nights elasticity 0.76), vs seasonal_naive/pct_rev_last4 | MAE $17.8M, MAPE 6.1% | ratio 0.797 (eq) / 0.856 (rw) vs seasonal naive; 0.472/0.428 vs pct_rev_last4 | n/a | not published for lines | M1 §4d per-line expectation: cor and ops beat both baselines | **half-pass** ("beats pct_rev_last4, only ties seasonal naive") |
| W2 | 10 | same | MAE $17.6M, MAPE 5.8% | **1.020** (eq, fails) / 0.901 (rw); 0.505/0.425 | — | — | same | eq fails, rw passes — **not both** |
| W1 | 14 | `ops_cash_musd`, M6 `cycle-flex\|l0_rw` (booking elasticity `k_ops` 0.44, HAC t 3.43), vs seasonal_naive | MAE $18.6M | ratio 0.832 (eq) / 0.927 (rw); survives (eq/rw) **False**/True | — | — | M6 harness registration: beat seasonal_naive at h=0, both windows, both weightings | not both |
| W2 | 10 | same | MAE $18.3M | **1.066** (eq, fails) / 0.981 (rw) | — | — | same | not both — **"G&A and ops & support do not survive both windows at both weightings"** (M6 §7, pre-D4) |
| W1 | 14 | `ops_cash_musd`, M1 `b_elastic_rw`, re-scored vs **drift** (harsher; R14/D4, governs) | ratio **0.946** | t −0.27, p **0.79**, 9 of 14 quarters better | — | — | — | **statistical tie** |
| W2 | 10 | same | ratio **0.919** | t −0.33, p **0.74** | — | — | — | **statistical tie** |
| W1 | 14 | `ops_cash_musd`, M6 `k_ops` = 0.44, re-scored vs **drift** (R14/D4, governs) | ratio **0.988** | t −0.06, p **0.95**, 8 of 14 better | — | — | — | **statistical tie** |
| W2 | 10 | same | ratio **0.960** | t −0.16, p **0.87**, 6 of 10 better | — | — | — | **statistical tie** |
| — | 2 | `40_line_build`'s own recursive formula, backcast (not PIT-scored) | FY25 predicted $1,294.4M vs actual $1,237.0M (+4.6%, "out of sample; the -10/-16% AI statements came in 2026"); 1H26 predicted $624.01M vs actual $624.0M (+0.0%, "calibration identity, not a test") | — | — | — | none written | descriptive only, not a W1/W2 test |
| W1/W2 | 14/10 | `total_cash_costs_musd` (all five lines, for context) vs drift | 1.165 / 1.170 | worse than drift, both windows | — | — | — | **FAIL** (M1 D4) |

**Strongest known failure:** the object this dossier's dollar figures actually come from — the recursive same-quarter-last-year, AI-decline/fixed-growth formula — has never been run through the harness scorer at all (only a 1H26 calibration identity and a single FY25 backcast point, +4.6% out of sample); and unlike C1's cost-of-revenue line, the two related econometric objects that do exist for this column (M1's nights elasticity, M6's booking elasticity `k_ops` = 0.44, itself a real and significant regression coefficient at t = 3.4) produce forecasts that are a **statistical tie with a trend-aware drift baseline in both W1 and W2** (p = 0.74–0.95) — not a proven edge in either direction, which is a materially weaker evidentiary floor than cost of revenue's p < 0.05, both-windows result.

## 7. Kill list and consistency

**Kill-list check.** None of `AGENT_BRIEF.md` §6's kill-list items (the −3.4pp Q4 FX step, "82% of Q4 FX already determined," the fee-uplift number, the 9/9 guide-below-Street drift rule, the ADR/unit-size claim, any unbanded FY27 level edge, restated unearned fees, the 1.71M quote panel, "nothing beats guide × cushion," mixed-vintage consensus, M5's hierarchical cushion model, the 120-market panel, the Stan state space) pertain to operations & support — that list covers revenue/FX/nights/ADR/fee mechanics, not the cost stack. Nothing withdrawn is quoted here.

**Superseded claims not quoted as current:**
- **`ops_variable_share = 0.19`** (the Codex/Astra audit's pre-fix linear-approximation calibration) — superseded by the committed `0.215`, which this dossier reproduces.
- **"G&A and ops & support do not survive both windows"** against plain `seasonal_naive` (M6 §7, pre-D4) — reported in §6 labelled as the softer, earlier test; the harsher, later drift-baseline re-scoring (a statistical tie, not a clean fail) is what §4/§6 treat as governing, per M6's own D4 section calling drift "the honest baseline for a growing dollar line."
- **"Ops beats `pct_rev_last4` but only ties the seasonal naive... half right"** (M1 §4d, pre-D4) — same treatment: reported, but the drift-scored tie is the current picture.

**Conflicts found and their resolution.**
1. **The pre-D4 M6 verdict ("fails both windows") vs the post-D4 M6 verdict ("statistical tie, t = −0.06/−0.16, p = 0.95/0.87").** Not a real conflict — D4 is a harsher, later, explicitly-labelled re-scoring against a baseline that itself knows the line is growing (drift, not flat `y[q-4]`); against that fairer baseline, ops neither beats nor loses to trend extrapolation. The earlier "fails" verdict came from comparing against the weak `seasonal_naive` baseline, where a merely-growing cost line looks bad on one exact eq-weighted W2 cell (ratio 1.066) purely because the baseline ignores growth — the same artefact C1 documents for cost of revenue's pre-D4 numbers.
2. **The FY25 backcast (+4.6% over, "out of sample; the -10/-16% AI statements came in 2026") vs the 1H26 calibration identity (0.0%, "calibration identity, not a test").** Not a conflict — the note explicitly labels the second one as not a real test (it is how `v` was solved), and only the FY25 point is genuinely out-of-sample evidence, at a modest +4.6% error.
3. **Consistency with C1 (cost of revenue) and the margin card:** the $48.0M-per-1.0pp-of-3Q26-margin conversion is the same C1/C4 use (same $4,804.0M revenue denominator). The `40_annual.csv` FY26/FY27 base ops figures here ($1,303.7M / $1,377.9M) sum consistently with C1's cost-of-revenue and the run's total-cash-cost identity (`run.py` line 328's internal assertion, unaffected by this dossier). The short-case FY26 revenue base ($13,932.8M) matches C1's own citation of the same figure.
4. **The reconciliation-invariance fact (§3.4, §2 "number that answers the judge") is new relative to C1's dossier** — C1's cost of revenue line *is* one of the two lines the recon_gap feeds (30% via hosting), so its 3Q26 dollars *do* move with the reconciliation; ops is upstream of that split (its own shocks change how much is left to reconcile) but is never itself a destination of the reconciled dollars. This is a structural fact worth carrying into the memo's cost-stack narrative, not a conflict with C1.

## 8. Open choices
1. **Does the memo claim operations & support is "forecastable"?** Options: **(a)** yes, citing the real, significant regression coefficient (`k_ops` = 0.44, t = 3.4, booking elasticity); **(b)** no, because the forecast built on that coefficient is a statistical tie with a trend-aware baseline in both windows (p 0.74–0.95); **(c)** the qualified claim — the *relationship* (support cost tracks bookings, and AI has genuinely cut the per-unit rate 10–16% by management's own account) is real and sourced, but the *forecast* built on it has no proven edge over simply trending the line, in either window. — **Recommendation: (c).** Why: (a) would overstate what the D4/drift re-scoring shows, and (b) would understate that the underlying mechanism (AI-driven decline in "support cost per booking," now a two-quarter-old, twice-repeated management metric) is a real, sourced, and directionally-favorable fact even without a proven forecasting edge.
2. **Is the 21.5% "AI-linked share" (`v`) the right split, or is the metric contaminated by other cost movements?** Options: **(a)** keep `v = 0.215`, calibrated exactly on the 1H26 identity; **(b)** treat `v` as understated, since management's stated per-booking decline (−10%/−16%) is steeper than what a 21.5%-weighted blend implies is needed to produce the observed +5.6% line growth, suggesting either the fixed side grew slower than assumed or the AI effect is broader than "third-party contact cost" alone; **(c)** carry `v` as a named sensitivity (already in `40_sensitivities.csv`: +0.10 to `v` = +0.09pp FY27 margin). — **Recommendation: (c).** Why: `v` is solved, not measured — it is the one free parameter that makes the FY25/1H26 identity close exactly, and the build's own bear/bull columns (0.17 / 0.27) already bracket the judgement call; the sensitivity table prices it rather than re-deciding it here.
3. **Should the 3Q26 reconciliation-invariance fact (ops-parameter shocks have zero effect on 3Q26 EBITDA in the base case) be stated in the memo's cost-stack narrative?** Options: **(a)** yes, explicitly, since it clarifies that 3Q26's margin is anchored to management's sentence rather than derived bottom-up from any one line's assumptions (consistent with DEC-0011's framing of "the 3Q26 sentence as a budget"); **(b)** no, since it may read as undermining the bottom-up build's credibility; **(c)** state it only for FY27, where ops assumptions do matter (±0.02–0.04 EPS per named shock). — **Recommendation: (a).** Why: DEC-0016 (no leaning) argues for stating mechanical facts about the model plainly; this is a fact about how the reconciliation mechanism works, not a judgement call, and a judge who runs the same sensitivity table would find it in seconds.

## 9. Judge Q&A
1. Q: **What drives operations & support?** A: Two pieces, split by a calibrated share `v = 0.215`. The AI-linked 21.5% (third-party contact cost, "13,000 contingent workers" per the FY25 10-K) is declining on management's own stated metric — "support cost per booking" down 10% (1Q26 call) and 16% (2Q26 call), with ">40% of issues resolved without an agent." The other 78.5% is payroll, customer relations and insurance, growing at 8% y/y per the 1H26 10-Q's itemised deltas (+$14M/+$27M payroll, +$3M/+$10M customer relations, +$7M insurance) — the +$10M customer-relations item is explicitly "higher make-good payouts and related case reserves," i.e. cancellation-driven, which is why the short case adds a further +4% RNPL overlay on top.
2. Q: **What did the 10-Q actually say, in the company's own words?** A: The dollar-level detail is in the MD&A tables (the specific payroll/customer-relations/insurance deltas above); the percentage claims ("support cost per booking down 10%/16%," ">40% of issues resolved without an agent," "continue to decline" as AI "moves to voice") come from the 1Q26 and 2Q26 earnings calls, not the 10-Q body text itself — the build's own params.csv is explicit about which is which. No number is given for the FY27 pace of decline; the build's −10% FY27 assumption is judgement, flagged "medium confidence" in its own source note.
3. Q: **Is this line actually forecastable, or is that also a plug?** A: The underlying relationship is real — booking-cost elasticity `k_ops` = 0.44 with t = 3.4 (highly significant as a regression coefficient) — but turning that into a **forecast** that beats even a trend-aware baseline has not been demonstrated: re-scored against the harsher `seasonal_naive_drift` baseline (the one M6's own D4 section calls "the honest baseline for a growing dollar line"), both M1's and M6's ops objects are statistical ties in both windows (p = 0.74 to 0.95). This is different from — and weaker than — cost of revenue, the one cost line that clears p < 0.05 in both windows against the same harsher baseline.
4. Q: **Does a change in the AI-decline or fixed-growth assumption move the 3Q26 number the memo prints?** A: No, by construction. Every ops-parameter shock in `40_sensitivities.csv` shows exactly $0.0M of 3Q26 EBITDA impact, because the sentence-reconciliation mechanism reallocates the gap between ops, marketing and hosting to hit management's stated "down slightly" margin — a bigger or smaller ops number just changes how much reconciliation the model assigns to marketing/hosting, not the total. FY27 has no such mechanism and does move: +3pts to fixed-cost growth is −0.20pp of FY27 margin (−$0.04 EPS); a 4-point slower AI decline is −0.08pp (−$0.02 EPS).
5. Q: **How much does RNPL add to this line in the short case?** A: A flat +4% multiplicative overlay on the pre-overlay ops total, sourced to the 2Q26 10-Q's "+$10M" of "higher make-good payouts and related case reserves" and the 1Q26 10-Q's "+$3M refunds and credits" — both cancellation-driven customer-relations items. In dollars that is $14.4M at 3Q26, rising to $15.7M by 3Q27 as the booking base grows; $27.1M for 3Q26+4Q26 combined, $55.8M for FY27.

## 10. Grade
Grade: B — the reproduction is exact (`c2_ops_recompute.py`, run through the wrapper, exit 0, `restored: true`; all 18 committed cells across base/cost_bull/short match to 0.0) — but the specific object quoted in §2 (the recursive same-quarter-last-year, AI-decline/fixed-growth formula) has never itself been run through the harness scorer, so it cannot be said to survive W1 and W2 on its own account; only a 1H26 calibration identity (not a test, by the note's own admission) and a single FY25 backcast point (+4.6% out of sample) support it directly. Not A: the closest related, genuinely-scored objects (M1's nights elasticity, M6's `k_ops` booking elasticity) are **statistical ties** with a trend-aware drift baseline in both windows (p 0.74–0.95) under the governing, harsher re-scoring — a real, sourced, and significant *relationship* (t = 3.4 on the regression coefficient itself) that has not been shown to produce a better *forecast* than trend extrapolation. Not C: the reproduction is exact and complete, the sourcing for every parameter is a named 10-Q/call quote, and — unlike the lines that actively fail the drift test (product development, S&M, G&A, all with ratios above 1.0 and the wrong sign) — every ops ratio point-estimate sits below 1.0 in both windows and both objects, i.e. directionally favorable even though not statistically distinguishable from trend. This is a materially weaker evidentiary floor than C1's cost-of-revenue line (which clears p < 0.05 in both windows on the analogous object), which is exactly what keeps this at B rather than any stronger claim.
