# D7 — Take rate and the fee migration

## 1. Header
- Line: D7 · Judge's question: "Is take rate an input or an output, and what does the single host fee do to it?"
- Digger: opus · Date: 2026-09-18 · Commit: e6d9832
- Note on the commit: the brief names `b098ac2`; HEAD moved twice while this ran (`11b3d39` at the opening `git rev-parse`, then `e6d9832`, the pitch_model_v2 period-scoped-provenance commit). Every receipt below carries `e6d9832`.
- **One-line answer.** Take rate is an **output** — ABNB defines it as revenue ÷ same-quarter GBV, and the programme's own PIT backtest says routing revenue through a take-rate lever *adds* 1–2.5% of error for nothing — so the only defensible forecast line is the seasonal norm (`τ[q−4]`, the benchmark nothing beats) times an exogenous, dated fee-migration multiplier times an RNPL revenue haircut. **The single host fee does almost nothing to the printed take rate**: it lifts revenue and cuts GBV together, so across the entire θ range the FY27 take multiplier moves 1.59 bp while FY27 revenue moves +0.97% to +3.98%. Argue the fee on the revenue level and the GBV drag, never on the ratio.

## 2. The number

**Convention.** The line is built from three stated mechanisms, in this order:

1. **Seasonal norm** — the last *clean* (pre-migration) printed same-quarter take rate. 3Q → 3Q25 17.88; 4Q → 4Q25 13.62; 1Q → 1Q26 9.17 de-contaminated to 9.128; 2Q → 2Q26 13.26 de-contaminated to 13.119 (both 2026 anchors already carry migration, so they are divided by their own multiplier before re-use). The anchor is held at the clean print for 2027 as well, because the migration multiplier is cumulative from a zero-migration base. This is the seasonal naive `τ[q−4]`, and §6 shows it is the only take-rate object on the board that nothing beats.
2. **Fee-migration θ** — multiply by `take_mult(q, θ-case)` from `fee_takerate/05a_migration_effect_by_quarter.csv`. base = central θ 0.833 (Austin, repo units); short = the **observed 11.5 pp modal listed-price jump** (the case the data actually supports, per Finding 1); breaker = **θ = 1, the labelled upper bound** (this is the case whose *revenue* uplift is the kill-listed "+4.05%"; it is quoted here only as a bound and never as measured).
3. **RNPL leakage** — multiply by (1 − L), L from K1 §3.2 `C3_leakage_grid`. base L = 0.84% (21% GBV-share row × Δc = +4 pt, K1's own central cell); short L = 1.39% (23.1% backlog share × Δc = +6 pt, the management-implied top); breaker L = 0.17% (16.7% nights share × Δc = +1 pt, the floor). Applied to the numerator only.
4. FY27 quarters only: the **non-migration** mechanism lines of `05b_takerate_mechanism_fy27.csv` (FX/cross-currency service fee, hotels at ~11% take, Experiences at ~20%, Services, ads outside GBV, the 6–10% direct-link pilot) net to −18.0 / −1.0 / +14.0 bp on a 13.199% LTM base for short / base / breaker. They are FY27 objects and are set to zero for 3Q26, 4Q26 and FY26.

FY take rates are Σrevenue ÷ ΣGBV, not an average of the quarters: FY26 uses 1Q26 and 2Q26 actuals plus the 3Q26 GBV decided in DEC-0004 × DEC-0008 and a stated 4Q26 GBV; FY27 uses the FY26 quarterly GBV shares as weights.

θ does **not** order the scenarios. `take_mult` for 3Q26 is 1.01700 (short) / 1.01828 (base) / 1.01513 (breaker) — non-monotonic in θ, because at θ = 1 GBV rises too. The scenario ordering is carried by RNPL leakage and, in FY27, by the non-migration lines. That is Finding 3 made mechanical and it is the honest answer to the judge.

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 3Q26 | 18.054 | 17.931 | 18.120 | pct | fee_takerate 05a/04a, 11 Sep 2026; K1 C3 grid; reproduced at e6d9832 |
| short | 3Q26 | 17.931 | 17.931 | 18.120 | pct | as above |
| breaker | 3Q26 | 18.120 | 17.931 | 18.120 | pct | as above |
| base | 4Q26 | 13.865 | 13.787 | 13.916 | pct | as above |
| short | 4Q26 | 13.787 | 13.787 | 13.916 | pct | as above |
| breaker | 4Q26 | 13.916 | 13.787 | 13.916 | pct | as above |
| base | FY27 | 13.610 | 13.351 | 13.878 | pct | as above + 05b non-migration lines |
| short | FY27 | 13.351 | 13.351 | 13.878 | pct | as above |
| breaker | FY27 | 13.878 | 13.351 | 13.878 | pct | as above |

**The consistency ledger, and why this line does not fit the block.** At the decided 3Q26 GBV — DEC-0004 146.3 m nights × DEC-0008 $176.88 = **$25,877.5 M** — every revenue object the programme carries implies a *higher* take rate than this line's whole band (`receipts/D7/05_consistency_ledger_3q26.csv`):

| object | 3Q26 revenue $M | take rate at the decided GBV | vs 3Q25 17.882 |
|---|---|---|---|
| D7 mechanism line, short | 4,640.2 | 17.931% | +5 bp |
| D7 mechanism line, base | 4,671.9 | **18.054%** | +17 bp |
| D7 mechanism line, breaker | 4,688.9 | 18.120% | +24 bp |
| management's guide, low | 4,690.0 | 18.124% | +24 bp |
| management's guide, midpoint | 4,730.0 | 18.278% | +40 bp |
| Street (LSEG, L0 register) | 4,744.9 | 18.336% | +45 bp |
| management's guide, high | 4,770.0 | 18.433% | +55 bp |
| **R1 kernel (DEC-0006) 4,804.0** | 4,804.0 | **18.564%** | **+68 bp** |
| B1 optimal-mix combined | 4,816.1 | 18.611% | +73 bp |
| guide midpoint × cushion (DEC-0001, 1.857%) | 4,817.8 | 18.618% | +74 bp |

The **top** of D7's band (18.120%) sits 0.4 bp *below* the bottom of management's own guide range. The R1-consistent identity — λ_Q3 17.2394% on the printed lagged base 27,866.7, divided by the decided GBV — is **18.564%**, **51.1 bp above this line's base** (`receipts/D7/08_r1_identity_bridge.csv`). In 4Q26 the two constructions agree to **1.2 bp** (13.877% identity vs 13.865% mechanism), because 4Q26's lagged base already contains the low 3Q26 GBV. **The whole inconsistency is 3Q26 and it is a GBV problem, not a fee problem.**

Independent corroboration of the identity side: C11 revision 2 (17 Sep), reading its joint model at the GBV band 25,600–25,900, returns a conditional take-rate median of **18.56%** — the same number the kernel gives — at P(≥18.10) = 0.995.

### 2a. Model inputs (machine-readable)

`take_rate_pct` is the mechanism line above (GBV-free, defined for every period). `take_rate_pct_r1_identity` is the alternative bridge that reproduces the DEC-0006 kernel exactly and is only computable where a GBV is decided or stated; §8 choice 1 is which one the workbook carries. `p_take_ge_1810` is B1's joint block with its GBV mean moved to the decided level, which is what the brief asked for; the other readings of that probability are in `receipts/D7/07_p_take_ge_1810_variants.csv` and in §9 Q2.

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| take_rate_pct | base | 3Q26 | 18.054 | pct | 17.88 x 1.018282 (central theta) x (1 - 0.0084) |
| take_rate_pct | base | 4Q26 | 13.865 | pct | 13.62 x 1.026643 x (1 - 0.0084) |
| take_rate_pct | base | 1Q27 | 9.331 | pct | 9.128 clean x 1.031667 x 0.999242 x (1 - 0.0084) |
| take_rate_pct | base | 2Q27 | 13.437 | pct | 13.119 clean x 1.033697 x 0.999242 x (1 - 0.0084) |
| take_rate_pct | base | 3Q27 | 18.318 | pct | 17.88 x 1.033956 x 0.999242 x (1 - 0.0084) |
| take_rate_pct | base | 4Q27 | 13.954 | pct | 13.62 x 1.033999 x 0.999242 x (1 - 0.0084) |
| take_rate_pct | base | FY26 | 13.437 | pct | sum revenue / sum GBV; 1Q26 and 2Q26 actual; FY25 actual was 13.407 so this is +3 bp y/y |
| take_rate_pct | base | FY27 | 13.610 | pct | FY26 GBV shares as weights |
| take_rate_pct | short | 3Q26 | 17.931 | pct | 11.5 pp modal-jump theta; L 1.39 pct |
| take_rate_pct | short | 4Q26 | 13.787 | pct | same |
| take_rate_pct | short | 1Q27 | 9.160 | pct | same plus non-migration lines -18.0 bp |
| take_rate_pct | short | 2Q27 | 13.188 | pct | same |
| take_rate_pct | short | 3Q27 | 17.961 | pct | same |
| take_rate_pct | short | 4Q27 | 13.682 | pct | same |
| take_rate_pct | short | FY26 | 13.390 | pct | -2 bp vs FY25 actual 13.407 |
| take_rate_pct | short | FY27 | 13.351 | pct | FY26 GBV shares as weights |
| take_rate_pct | breaker | 3Q26 | 18.120 | pct | theta = 1 LABELLED UPPER BOUND; L 0.17 pct |
| take_rate_pct | breaker | 4Q26 | 13.916 | pct | same |
| take_rate_pct | breaker | 1Q27 | 9.522 | pct | same plus non-migration lines +14.0 bp |
| take_rate_pct | breaker | 2Q27 | 13.729 | pct | same |
| take_rate_pct | breaker | 3Q27 | 18.657 | pct | same |
| take_rate_pct | breaker | 4Q27 | 14.212 | pct | same |
| take_rate_pct | breaker | FY26 | 13.464 | pct | +6 bp vs FY25 actual 13.407 |
| take_rate_pct | breaker | FY27 | 13.878 | pct | FY26 GBV shares as weights |
| p_take_ge_1810 | base | 3Q26 | 0.861 | probability | B1 joint block, GBV mean moved to the decided 25877.5; revenue 4816.1 sd 48.0, GBV sd 853.209, rho 0.7595, 500k draws seed 20260911 |
| take_rate_pct_r1_identity | base | 3Q26 | 18.564 | pct | lambda_Q3 17.2394 x lagged base 27866.7 / decided GBV 25877.5; reproduces DEC-0006 kernel revenue 4804.0 exactly |
| take_rate_pct_r1_identity | base | 4Q26 | 13.877 | pct | lambda_Q4 12.0298 x lagged base 26318.4 / stated 4Q26 GBV 22814.7 |
| revenue_3q26_implied_musd | base | 3Q26 | 4671.9 | musd | take_rate_pct base x decided GBV; BELOW the guide low of 4690 |
| revenue_3q26_implied_musd | short | 3Q26 | 4640.2 | musd | same |
| revenue_3q26_implied_musd | breaker | 3Q26 | 4688.9 | musd | same |
| gbv_3q26_decided_musd | base | 3Q26 | 25877.5 | musd | DEC-0004 146.3 x DEC-0008 176.88; carried here only as the denominator, D1/D4/D6 own it |
| gbv_4q26_stated_musd | base | 4Q26 | 22814.7 | musd | 121.9 x 1.076 nights (AGENT_BRIEF 4Q26 +7.6 pct) x DEC-0008 ADR 173.94; NOT a D7 decision, D2 is open |
| fee_take_mult_3q26 | base | 3Q26 | 1.018282 | ratio | 05a central theta; 1.017004 short, 1.015126 breaker - NON-MONOTONIC in theta |
| rnpl_leakage_L_pct | base | 3Q26 | 0.84 | pct | K1 C3 grid central cell; 1.39 short, 0.17 breaker |

## 3. Derivation chain
1. `data/raw/letters/*.htm` printed revenue and GBV → `data/processed/abnb_driver_history_quarterly.csv` (`take_rate_calc_pct`), cross-checked against `data/processed/airbnb_adr_takerate_quarterly.csv` →
2. `analysis/src/forecast_methods/fee_takerate/fee_schedule.py` (the fee function, the de-gross-up, the migrated-share path from `data/processed/overnight/06_fee_timeline.csv` letters) →
3. `analysis/src/forecast_methods/fee_takerate/run.py` stages (a)–(f) → `data/processed/forecast_methods/fee_takerate/04a_takerate_history.csv` (clean anchors), `03_migrated_share_path.csv`, `05a_migration_effect_by_quarter.csv` (`take_mult`), `05b_takerate_mechanism_fy27.csv` (non-migration bp), `07d_take_rate_mechanism_all_quarters.csv` (the registered LIVE rows) →
4. `data/processed/forecast_methods/kernel_phi_v2/C3_leakage_grid.csv` (RNPL L) and `data/processed/forecast_methods/kernel_lambda/04_season_lambda_by_weight.csv` (λ at w = 0.6667: Q3 17.239362, Q4 12.029793) →
5. `data/processed/pitch_model_v2/receipts/D7/03_take_rate_mechanism_path.csv` column `take_rate_pct`, rows (scenario, quarter); `04_fy_take_rate.csv` columns `FY26_take_rate_pct` / `FY27_take_rate_pct`; `08_r1_identity_bridge.csv` column `r1_identity_take_rate_pct`.

Probability chain: `data/processed/forecast_methods/live_block_v2/04_gbv_sensitivity.csv` and `LIVE_3Q26_CARD.csv` → replicated in `receipts/D7/01_b1_replication_and_decided_gbv.csv`, checked in `02_b1_match_check.csv`, extended in `07_p_take_ge_1810_variants.csv`.

## 4. Governing sources

Web fetches this run: **none** (0 of the 5 allowed). The one missing source — the 15-Sep-2026 and 13-Oct-2026 migration deadlines — exists only on Airbnb's Resource Center (art. 771), which rule 3 of the brief and CLAUDE.md rule 6 both forbid fetching. It stays an unsourced assumption; see §7.

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-08-06 | 2Q26 shareholder letter | "We expect our implied take rate to remain relatively in-line year-over-year" (3Q26) | **governs** as management's own 3Q26 statement |
| 2026-08-06 | 2Q26 call, Mertz | "For the full year, we expect our implied take rate to be relatively flat compared to 2025, accounting for … Reserve Now, Pay Later, as well as higher customer incentives related to new businesses … Absent these incentives … slightly higher" | **governs** as management's own FY26 statement |
| 2026-09-11 | `fee-takerate.md` + `fee_takerate` package | θ **unidentified** for the mandatory cohort; migrated-share path exogenous and dated; take-rate effect θ-robust to 1.59 bp on FY27 while revenue moves +0.97–3.98%; **the printed take rate is an OUTPUT and must not carry a forecasting lever**; A10 null (n 20, 2 informative quarters) | **governs** the mechanism, θ and the parameter count |
| 2026-09-11 | `B1_TAKE_RATE_RECONCILIATION.md` | one number 18.14%, sd 0.46 pp, P(≥18.10) = 0.53 at GBV 26,549.8; "a GBV test wearing a fee test's clothes"; flip GBV 26,608.3; the 17.81 / 18.40 readings are withdrawn | identity method and the joint-draw machinery **govern**; its published **probability is superseded** by C11 rev 2 |
| 2026-09-11 | `K1_KERNEL_WEIGHTS_AND_BACKLOG.md` §3.2 + `C3_leakage_grid.csv` | RNPL leakage L = 0.17% to 1.39% of recognised revenue; 1H26 λ deviations both inside the 80% band, so Δc is not identified | **governs** the leakage term |
| 2026-09-11 | `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` | unpaid share 14–15% (B = 1.00) / 22–23% (B = 1.10), 17–28 m unpaid nights; **the 7–19 m figure is withdrawn**; the script over-states the backlog 7–25% by dividing by 0.124 | **governs**; supersedes the 2026-09-10 conversion-framework handoff on the backlog size |
| 2026-09-13 | `L3_FEE_RESULTS_v1.md` | 0 of 6 scheduled wave captures present; **no θ estimated**; L4 receives explicit nulls; the calendar gives one pre and two post observations, so no pre-trend | **governs**; supersedes `A3_fee_panels.md` §4 (two-before/one-after) and A3's suggestion to pool unknown-residence listings |
| 2026-09-13 | `L3_FEE_AUDIT_CLOSE_v3.md` | `fee_panel_v1/reviewed_v3/` is the canonical L4 source; 19 tests pass; wave n = 0, θ unavailable, adoption pending | **governs** the output path; supersedes `L3_FEE_AUDIT_REPAIR_v2.md` on that path only |
| 2026-09-17 | C11 `q3-take-rate-above-1810` rev 2 | headline P(≥18.10) = **0.76**; band integral 0.778; conditional by printed GBV: <25,600 → 1.00, 25,600–25,900 → **0.995 with take median 18.56**, 26,200–26,500 → 0.76, ≥26,800 → 0.001; the three "flat"-class guides realised +14 / −69 / −47 bp, 0 of 3 ≥ +22 bp | **governs** the published probability; supersedes B1's 0.53 as the memo number |
| 2026-09-17 | B17 `bonus-take-rate-guided-down` rev 2 | the **−0.8 pt direct-link figure is STRUCK** (no retrievable object); P(take rate guided lower) 0.41 | **governs** |
| 2026-09-17 | R04 `risk-single-fee-take-rate-accretion-stated` rev 2 | 2Q26 rescored **No**; P(accretion stated) 0.58 | **governs**; supersedes rev 1's half-Yes |
| 2026-09-17 | `deck/drafts/memo_v3_short_2026-09-17.md` | "the printed take rate vs 18.10% (P 0.76 …) paired with GBV vs $26,608M"; "our take rate is inside the range"; "no detectable fee effect on the printed take rate through 2Q26 (n 20)" | consistent with C11 rev 2; see §7 for the GBV pairing conflict |
| 2026-09-18 | DECISIONS.md DEC-0004 / DEC-0008 / DEC-0016 / DEC-0006 / DEC-0001 | 3Q26 nights 146.3 m; ADR 176.88 (3Q26) and 173.94 (4Q26); no leaning; kernel drives forward revenue; cushion 1.857 | **binding** |

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/D7/receipt.json`
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id D7 --watch data/processed/forecast_methods/fee_takerate --watch analysis/src/forecast_methods/fee_takerate --cmd "PYTHONPATH=analysis/src python3 analysis/src/forecast_methods/fee_takerate/run.py"` · Exit: **0** · Wall: 1.2 s · Interpreter: `python3` (3.13 / pandas 3.0.0; the `.venv-pd2` fallback was not needed) · `"restored": true`
- Output: `data/processed/forecast_methods/fee_takerate/07d_take_rate_mechanism_all_quarters.csv`, column `point`, row `2026Q3 / mechanism_theta_central` = **18.206890** · Committed value: 18.206890 (= 17.88 × 1.0182824) · Tolerance: ±1e−6 pp · **Match: yes**
- Whole-package check: all 19 output files rebuilt; the only file that differed from HEAD was `04b_takerate_regression.csv` at **max abs diff 5.68e−14** (float noise in the permutation-test columns); every other file reproduced byte-for-byte. Acceptance tests **16 of 17 pass**; A5 is the deliberate documented failure (the "more listings cut >10% than raised >10%" claim is Austin-only).
- Second receipt, the B1 replication and the D7 derivation: `data/processed/pitch_model_v2/receipts/D7/derive/receipt.json`, exit **0**, `"restored": true`. It reproduces `live_block_v2/04_gbv_sensitivity.csv` from B1's published inputs alone — **max abs diff 0.000000 on the take rate, 0.000000 on P(≥18.10), 5.6e−17 on the sd across all six grid rows** — and then re-centres the block on the decided GBV. Third and fourth receipts: `receipts/D7/probs/receipt.json` and `receipts/D7/identity/receipt.json`, both exit 0, both restored.
- What was **not** reproducible: nothing in the D7 package. `fee_panel_v1` and `fee_panels` were not re-run because `L3_FEE_RESULTS_v1` and `L3_FEE_AUDIT_CLOSE_v3` both record **zero of six wave captures present and θ unavailable**, so a re-run cannot produce an estimate; `run.py` there also rejects an existing output directory by design. The registered `take_rate_mechanism` object carries only 6 of its 24 rows because the harness rejects 2026Q4+ targets under FORMAT 1.0 (change request already filed in the note); no scorer was run.

## 6. Test record

Pre-registered pass line (AGENT_BRIEF rule 2 + `fee-takerate.md` §4): a take-rate object must beat the **seasonal naive `τ[q−4]`** on **both** windows, i.e. RMSE ratio < 1.00 on W1 (1Q23+, n 14) and W2 (1Q24+, n 10), PIT replay.

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 PIT | 14 | RMSE ratio, `take_rate_kernel` | 1.342 | 1.000 (RMSE 0.3251 pp) | n/a — cushion is a revenue object | n/a — no Street take-rate tape | < 1.00 both windows | **fail** |
| W2 PIT | 10 | RMSE ratio, `take_rate_kernel` | 1.299 | 1.000 (RMSE 0.3178 pp) | n/a | n/a | < 1.00 both windows | **fail** |
| W1 PIT | 14 | RMSE ratio, `take_rate_lastyear` | 1.003 | 1.000 | n/a | n/a | < 1.00 both windows | **fail** |
| W2 PIT | 10 | RMSE ratio, `take_rate_lastyear` | 1.056 | 1.000 | n/a | n/a | < 1.00 both windows | **fail** |
| W1 full | 14 | RMSE ratio, both objects | 1.234 / 1.158 | 1.000 | n/a | n/a | < 1.00 both windows | **fail** |
| W2 full | 10 | RMSE ratio, both objects | 1.181 / 1.327 | 1.000 | n/a | n/a | < 1.00 both windows | **fail** |
| full sample | 20 | fee effect: Δtake (bp) on Δ migrated revenue share | slope −105.7 bp/unit, se 448.5, t −0.24, perm p 0.730, R² 0.003; **only 2 of 20 quarters informative** | — | — | — | a positive, significant slope | **fail (null, wrong sign, unidentified)** |
| W1 PIT | 14 | perfect-foresight-GBV revenue error | kernel conversion +2.00% (sd 2.45); lever +0.97% (sd 2.54) | — | — | — | ≤ the direct revenue route | **fail** |
| n/a | 20 | calibration of the mechanism line itself | **never backtested** — it is `τ[q−4]` times an exogenous multiplier and an unidentified L | — | — | — | — | **not tested** |
| n/a | 8 | conformal coverage (n_cal 6, α 0.2) | 0.75–0.88 inside an attainable band [0.857, 1.000] | — | — | — | — | uninformative; **exchangeability violated** |
| n/a | 4 | FY26 sanity vs management's own FY guide | FY26 13.437 base vs FY25 actual 13.407 = **+3 bp**, "relatively flat compared to 2025" | — | — | — | descriptive | **consistent** |
| n/a | 6 | FY27 vs `05b` total (+5.4 / +22.7 / +41.9 bp) | FY27 vs FY25: −6 / +20 / +47 bp | — | — | — | descriptive | **consistent** |

Both backtested objects are **positively biased** (+0.10 to +0.29 pp, PIT means 0.27–0.42), so their intervals are shifted, not merely wide. The harness scoreboard's 0.07–0.09 ratios for these rows are an artefact of applying a growth naive to a seasonal ratio and are **not a win**; A17 confirms the shared registry carries no `take_rate_pct` denominator at all, so `rmse_ratio_to_naive = NaN` there means *no denominator*.

**Strongest known failure:** at the decided 3Q26 GBV of $25,877.5 M this line's entire scenario band (17.931–18.120%) implies a revenue print of $4,640–4,689 M — **at or below the bottom of management's own guide range ($4,690 M)** and 51.1 bp of take rate / $132 M below the DEC-0006 kernel's $4,804 M, so the take-rate line and the D1×D4 GBV line cannot both be right and the take rate is silently absorbing the gap.

## 7. Kill list and consistency
- **Kill-list check.**
  - **"+4.05% fee uplift" as measured** — not quoted as ours anywhere. It is the *revenue* uplift at θ = 1; the breaker scenario uses that θ case for the *take-rate* multiplier only (1.015126 in 3Q26) and it is labelled an upper bound in §2, §2a and §9. The number +4.05% appears in this dossier only in this sentence, as the withdrawn claim.
  - **θ "0.83–1.41"** — a detection window over 402 Inside-Airbnb rows in which θ is *defined* as jump ÷ 13.8 off half-integer bin midpoints, not an estimate. Never used as a range over evidence. Finding 1 governs: the "+1.07% modal-jump" and "+1.82% central" cases are one Austin observation under two normalisations, so the carried +1.1–1.8% is a normalisation span. The short scenario deliberately uses the modal-jump case, the number the data actually supports.
  - **"the 1.71 M quote panel as fee-inclusive"** — not used; the tax-and-cleaning de-rate row it fed is deleted in `05b`.
  - **"the −0.8 pt direct-link figure"** — STRUCK by B17 rev 2 and by `fee-takerate.md` §5. This line uses `05b`'s −15 / −5 / 0 bp band instead.
  - **restated unearned fees (`reported / (1 − d)`) as a pin or a feature** — not used. RNPL enters only through K1's L grid.
  - **A5** ("more listings cut price by over 10% than raised it") — Austin-only, not stated here as a general fact.
- **Conflicts.**
  1. **With the block (material).** D7's mechanism line, R1's kernel and D1×D4's GBV are mutually inconsistent in 3Q26 by 51.1 bp of take rate. They reconcile to 1.2 bp in 4Q26. Either D1's 146.3 m nights is too low, or the printed 3Q26 take rate must be ~18.56% (+68 bp y/y) — which flatly contradicts management's own "relatively in-line year-over-year" guide, and C11 rev 2's language record shows the three flat-class guides realised +14 / −69 / −47 bp, **0 of 3 ever reaching +22 bp**.
  2. **Three live probabilities for one pre-registration.** B1 (11 Sep) 0.53 at GBV 26,549.8; memo v3 and C11 rev 2 (17 Sep) 0.76 unconditional; this dossier's B1-method recomputation at the decided GBV 0.861, and the same block conditional on that GBV printing 0.997. They are not contradictory — they are the same identity at different GBVs and different conditioning — but only one may reach a slide. C11 rev 2 governs the unconditional; B1's flip GBV of $26,608 M governs the pairing.
  3. **Memo v3 pairs the take rate with GBV ≥ $26,608 M**, which is B1's flip point on B1's GBV. With D1/D4 decided at $25,877.5 M the pairing is no longer live in the same way: the decided GBV is 2.75% *below* the flip point, so on the model's own GBV the pre-registered test is nearly a foregone Yes rather than a coin flip. The memo sentence needs rewording or the pairing needs re-basing.
  4. **`07d` rows for 1Q27 and 2Q27 use contaminated anchors.** The package applies the full cumulative multiplier to `τ[q−4]` even when `q−4` already carried migration, double-counting +4.3 bp in 1Q27 and +14.6 bp in 2Q27. This dossier de-contaminates; the registered rows do not. Small, but it is a defect in a registered object.
  5. **Finding 2 is still unruled.** The fiat de-gross-up `host payout = reported ADR / (1 + s·θ·0.1479)` is dimensionally wrong for a GBV-basis reported ADR (at s = 0.5, θ = 0.833 the fiat divisor is 1.0616 against the GBV-consistent 0.9922). The package defaults to the GBV-consistent form; the decisions document still fiats the other. D4's ADR card carries a +0.17 pp fee-migration term K that DEC-0008 excluded from base — consistent with this line, which puts the fee in the take rate and not in ADR, but the two must not both carry it.
  6. **The 15-Sep-2026 and 13-Oct-2026 deadlines have no repo source** (A8: `06_fee_timeline.csv` has 19 rows, latest 2026-08, and neither date appears). They are carried in code as a dated assumption. The only source is an Airbnb-hosted Resource Center page, which the brief forbids fetching. **The entire 4Q26 fee step rests on an unsourced date.**
  7. **Double-count risk with D1.** DEC-0004's nights are already RNPL-re-based (+9.3% vs the +9.9% team baseline). K1 §3.1 says a cancelled RNPL booking reduces **GBV_q**, not GBV_{q−1}; if the reversal lands fully in the same-quarter GBV denominator, the leakage is approximately *take-rate neutral* at t ≈ the take rate, and charging L to the ratio as this line does double-counts. The opposite reading — a stay pushed out of the quarter, not cancelled — hits the numerator only and is what is modelled here. This is §8 choice 2.

## 8. Open choices
1. **Which take-rate line does the workbook carry?** — options: (a) **formula** `TAKE = 100 × REV / GBV`, take rate an output, revenue from R1/R2 (this is `fee-takerate.md` §4's own ruling and it makes the block consistent by construction); (b) **input = the D7 mechanism line** (18.054% base 3Q26), which is the only line D7's own evidence supports but which forces 3Q26 revenue to $4,672 M, below the guide floor; (c) **input = the R1-consistent identity** (18.564% base 3Q26), which reproduces DEC-0006 exactly but is +68 bp y/y against a "relatively in-line" guide with no precedent in twelve resolved language pairs. — recommendation: **(a)**, with the D7 mechanism band published beside it as the pre-registered 5 Nov test. — why: R1/DEC-0006 already determines revenue; a take-rate input would double-specify it, and the PIT backtest says the take-rate route costs 1–2.5% of revenue error even with GBV known exactly. Taking (a) also converts the 51 bp gap from a hidden plug into a visible question about D1's nights, which is where it belongs.
2. **Does RNPL leakage hit the printed take rate at all?** — options: (a) charge L to the numerator only, as modelled here (base 0.84%, ≈ −15 bp of 3Q26 take rate); (b) treat it as ratio-neutral because K1 §3.1 puts the cancellation reversal in the same-quarter GBV denominator, and D1's nights are already re-based; (c) split it, charging only the "stay pushed out of the quarter" part. — recommendation: **(b) for the base, (a) as the short**, and say so explicitly. — why: 1H26 shows no leakage at all (both λ deviations inside the 80% band, implied Δc +8.8 pt then −1.3 pt, i.e. noise), and charging a revenue haircut on top of an already-re-based nights line is the cleanest way to double-count the same dollar twice. Moving base to (b) lifts the 3Q26 base line from 18.054% to 18.207% and FY26 from 13.437% to 13.551%.
3. **Rule on Finding 2, the de-gross-up basis.** — options: (a) ratify the GBV-consistent form (`fee_schedule` default, what every downstream number already uses); (b) re-ratify the fiat form in `00_IMPLEMENTATION_DECISIONS`. — recommendation: **(a)**, and amend the decisions document. — why: ABNB's reported ADR is GBV ÷ nights, so the fiat divisor strips ~7% out of ADR that migration never put there and that error flows into GBV and into the fee edge.
4. **What does the memo say the fee does?** — options: (a) "the single fee lifts the *revenue level* by +1.1% to +1.8% on the migrated cohort and **cuts that cohort's GBV by 1.6–2.3% and host payout by 2.1–2.9%**, and it is worth about 1.6 bp of FY27 printed take rate"; (b) keep a take-rate accretion story. — recommendation: **(a)**. — why: Finding 3 — across the whole θ range the FY27 take multiplier moves 1.59 bp while FY27 revenue moves +0.97% to +3.98%. A judge who attacks θ cannot touch the take-rate number, and a judge who accepts the take-rate number has not yet accepted the revenue number. The GBV and host-payout drag is the part the Street does not have.
5. **Re-base or reword memo v3's take-rate pairing.** — options: (a) re-base the paired GBV threshold from B1's $26,608 M to the flip GBV on the model's own revenue (at kernel revenue $4,804 M the flip GBV is $26,541 M); (b) keep $26,608 M and state that it came from a superseded GBV; (c) drop the pairing and publish the conditional table from C11 rev 2. — recommendation: **(c)**, with (a) as the one-line footnote. — why: the conditional table is already built, already reproduces, and makes the GBV dependence impossible to miss; a single paired threshold hides it.
6. **Source the 15-Sep / 13-Oct deadlines, or label the 4Q26 fee step as undated.** — options: (a) a human fetches the Resource Center page (an airbnb.com terms-of-service decision, per CLAUDE.md rule 6); (b) find a PMS-vendor or trade-press notice that is not airbnb.com; (c) publish the 4Q26 step with an explicit "dates from a host resource page and a PMS notice, not a filing" caveat, which is what memo v3 already does. — recommendation: **(c) now, (b) before finals**. — why: the step is small in the take rate (2.7% multiplier ≈ +25 bp of 4Q26 printed take rate) but it is the whole dated basis of the 4Q26 revenue step, and an undated assumption in a footnote is safer than an unsourced date in the body.
7. **Fix or flag the `07d` anchor contamination.** — options: (a) leave the registered rows and carry the de-contaminated values in the workbook, as this dossier does; (b) re-register `take_rate_mechanism` with de-contaminated anchors (a new package version under the copy-never-overwrite rule). — recommendation: **(a) for the prelim, (b) before finals**. — why: +4.3 bp in 1Q27 and +14.6 bp in 2Q27 is ~$43 M of FY27 revenue — too small to re-cut a package for on 2 Oct, too large to leave unstated in a model that runs to 4Q27.

## 9. Judge Q&A
1. Q: Is take rate an input or an output? A: An output. Airbnb defines it as revenue ÷ same-quarter GBV, and we compute history that way. In the forecast we deliberately do **not** let it drive revenue: on fourteen point-in-time guide dates neither of our two take-rate objects beats the seasonal naive "print last year's same-quarter take rate" — ratios 1.18 to 1.34 for the kernel conversion and 1.00 to 1.33 for the last-year lever, failing on both windows in both prior replays — and even with GBV known exactly, routing revenue through a take rate adds 1.0 to 2.5 percentage points of error. So revenue comes from the kernel and GBV from nights × ADR, and the take rate is what falls out. Where the workbook needs a bridge line, it is the identity, and we publish the mechanism forecast beside it as the thing that gets tested on 5 November.
2. Q: So what is your 3Q26 take rate, and what is the probability it clears 18.10%? A: Two different objects, and we quote both. Our **mechanism** forecast — last year's 17.88% times the dated migration multiplier times an RNPL haircut — is **18.05%**, +17 bp, which is within 6 bp of the Street's own implied take rate of 17.99% and inside management's "relatively in-line" guide. Our **identity** at our own GBV of $25.88 bn is **18.56%**, +68 bp, because our nights call is below the Street and a low denominator mechanically lifts the ratio. On B1's joint block re-centred on our GBV, P(≥18.10%) is **0.86**; the published unconditional we carry is C11's **0.76**; and if GBV actually prints at $25.9 bn the conditional is 0.99. The honest sentence is: **this is a GBV test wearing a fee test's clothes.** The 50 bp gap between our two readings is not a fee question — it is our nights call, and it is the single largest open item in the block.
3. Q: What does the single host fee actually do to the take rate? A: Almost nothing, and that is the finding. The migration moves a cohort from a split 3% host / ~14.1% guest fee taking 14.99% to a single 15.50% host fee. Both legs of the ratio move together, so across the entire pass-through range we can construct — from full pass-through down to the 11.5 pp listed-price jump we actually observe — the FY27 printed take multiplier moves **1.59 bp**, while FY27 revenue moves +0.97% to +3.98%. Our take-rate scenarios are not ordered by θ at all; they are ordered by RNPL leakage. The fee's real signature is on the **revenue level** and, at any pass-through below one, a **1.6% to 2.3% cut to the migrated cohort's GBV and a 2.1% to 2.9% cut to host payout** — which is what the Street does not have.
4. Q: You say θ is unidentified. Then how can you use any fee number? A: We use the fee *schedule*, which is disclosed arithmetic with zero free parameters, and the migrated-*share* path, which is exogenous and read off the shareholder letters ("over a quarter" at 1Q26, "about half" at 2Q26). θ enters only as an explicit three-point range and we never estimate it. The panel that would identify it does not exist yet: zero of six scheduled wave captures were available on 13 September, and the deadline calendar gives one pre-observation and two post, so no pre-trend can be established. The one existing repricing panel is a **voluntary** PMS cohort whose excess repricing mass is 0.0029 against a background rate of 0.105 — about 3% the size of the noise — and the modal θ of 0.8333 is exactly a histogram bin edge, 11.5/13.8, not an estimate.
5. Q: Your regression says the fee has no effect on the printed take rate. Doesn't that kill the thesis? A: No, and we are careful about which way it cuts. Over twenty quarters only two carry a non-zero migrated share; the slope is −106 bp per unit share with a standard error of 449 and a permutation p of 0.73 on 4,000 seeded draws. That is an unidentified regression, reported as a negative, not as evidence of absence. Mechanically the printed take rate is revenue over same-quarter GBV with revenue lagging GBV by one to two quarters, so it is dominated by the seasonal conversion and by GBV growth — a 40% migrated revenue share at a +1.8% cohort uplift is about +7 bp on a 13.3% base, well inside the 50 to 70 bp the seasonal mix moves it. **The absence of a take-rate move through 2Q26 is not evidence the migration is not flowing.**
6. Q: What breaks your line? A: Our own GBV. At the decided $25.88 bn, our whole take-rate band implies a 3Q26 revenue print of $4,640 to $4,689 M, which is at or below the floor of management's guide — and management has beaten the midpoint 19 times out of 19. Either our nights are too low or our take rate is 50 bp too low. We are flagging it rather than plugging it.

## 10. Grade
Grade: B — the package reproduces exactly (exit 0, `restored: true`, max abs diff 5.68e−14 across 19 files, and B1's published GBV/probability grid replicates to 0.000000 from its inputs alone), but the line is **descriptive**: θ is unidentified, the fee effect on the printed take rate is undetectable on twenty quarters with two informative ones, both backtested take-rate objects lose to the seasonal naive on **both** windows in both replays, and the mechanism line itself — seasonal anchor × exogenous multiplier × an unidentified leakage — has never been backtested. No stretch to A is available; C would understate a clean, complete reproduction and a decision-relevant negative.
