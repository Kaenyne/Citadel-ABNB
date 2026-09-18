# C8 — FCF and SBC-adjusted FCF

## 1. Header
- Line: C8 · Judge's question: "What does the stock yield on cash, and is FCF timing or level?"
- Digger: sonnet · Date: 2026-09-18 · Commit: 0b0961e (branch `theo/pitch-model-v2`; the brief named b098ac2 and the tree had moved to e6d9832 when I started reading, then to 413762a and 0b0961e mid-wave as the orchestrator committed sibling dossiers. `git diff --stat b098ac2 0b0961e -- data/processed/margin_build data/processed/abnb_fcf_bridge.csv data/processed/abnb_quarterly_cost_stack_exsbc.csv docs/pitch-model-v2/dossiers/C6_c6_ebitda.md` shows only C6's dossier added; no data file this dossier reads changed, so every number below is stable at all four commits.)

**One-paragraph answer.** FCF is timing, not level, and the yield the memo quotes is real but stale on the price. History: FCF ex-SBC swings from −$244M (4Q23) to +$1,614M (1Q24) purely on the unearned-fees float cycle (`change_unearned_fees` in `abnb_fcf_bridge.csv`), and the RNPL-adjusted quality-of-growth study (`docs/rnpl-short-audit/05_quality-of-growth-study.md`) already settled the level question for 2026-27: 1H26 FCF ex-float actually *improved* (+24.4% vs revenue +17.1%; margin 29.7% vs 28.0%), the reported 47%-vs-51% FCF-margin swing is entirely the float shift, and the durable RNPL cash cost into FY27 is small (~$106M, 0.7pp of margin). No package in this repo builds a below-EBITDA (SBC/D&A/capex/tax → FCF) forecast under the pitch-model-v2 base/short/breaker scenario definitions yet — that is C7's job and its dossier landed mid-way through this run (§7). §2 below therefore reports the one FY26/FY27 FCF object that is fully built (`M7_below_ebitda`, its own "driver-lines" EBITDA source) as-is, and a second, explicitly labelled **DERIVED** re-anchoring onto C6's adopted line-build EBITDA and short/breaker scenarios, using M7's own below-EBITDA parameters (which per `M7_parameter_sheet.csv` do not vary by revenue/cost scenario). On the derived base case, at spot $167.51 (DEC-0015) the stock yields **4.85% FY26 / 5.66% FY27 on reported FCF and 3.04% FY26 / 3.52% FY27 on SBC-adjusted FCF** — close to the memo's "~3%" but on the current provisional spot, not the $170.19 the reverse-DCF growth figure below was solved at. The one place this line **has** been genuinely tested (the shared margin harness's `below-ebitda/fcf` quarterly registry, §6) shows it fails: no bridge spec beats the seasonal-naive baseline in both W1 and W2 at h=0, though it does consistently beat the Street's own FCF estimate.

## 2. The number

**Historical (actual, 1Q23–2Q26), USD m.** From `data/processed/abnb_fcf_bridge.csv` (`fcf`, `capex`, `sbc` columns); `fcf_ex_sbc = fcf − sbc`.

| period | fcf | capex | sbc | fcf_ex_sbc |
|---|---:|---:|---:|---:|
| 1Q23 | 1,581.0 | 6.0 | 240.0 | 1,341.0 |
| 2Q23 | 900.0 | 9.0 | 304.0 | 596.0 |
| 3Q23 | 1,310.0 | 15.0 | 286.0 | 1,024.0 |
| 4Q23 | 46.0 | 17.0 | 290.0 | −244.0 |
| 1Q24 | 1,909.0 | 14.0 | 295.0 | 1,614.0 |
| 2Q24 | 1,043.0 | 8.0 | 382.0 | 661.0 |
| 3Q24 | 1,074.0 | 4.0 | 362.0 | 712.0 |
| 4Q24 | 458.0 | 8.0 | 368.0 | 90.0 |
| 1Q25 | 1,781.0 | 8.0 | 358.0 | 1,423.0 |
| 2Q25 | 962.0 | 13.0 | 424.0 | 538.0 |
| 3Q25 | 1,349.0 | 7.0 | 399.0 | 950.0 |
| 4Q25 | 521.0 | 5.0 | 411.0 | 110.0 |
| 1Q26 | 1,704.0 | 4.0 | 410.0 | 1,294.0 |
| 2Q26 | 1,253.0 | 17.0 | 487.0 | 766.0 |

**FY26 / FY27, USD m, base / short / breaker.** Two objects, and they must not be blended (same convention C6 used for its two EBITDA objects):
- **M7-own** — `data/processed/margin_build/M7_below_ebitda/M7_below_ebitda_annual_forecasts.csv`, scenario `base`, `ebitda_source` `driver-lines` (spec `a_unit_rw`, vintage 2026-09-11). This is the only fully-built below-EBITDA forecast in the repo: it carries its own capex, SBC, D&A, interest, tax and working-capital rules through to FCF. It has **no short or breaker case**.
- **LB-anchored (DERIVED)** — M7-own re-anchored onto C6's adopted line-build (LB) adjusted EBITDA (`docs/pitch-model-v2/dossiers/C6_c6_ebitda.md` §2a: base/short/breaker), by adding the EBITDA delta after tax (marginal EBITDA → FCF at 1 − ETR, M7's own FY26/FY27 effective tax rates 17.74%/17.50%), holding M7's capex/SBC/interest/working-capital rules fixed (per `M7_parameter_sheet.csv` these do not vary by revenue or cost scenario — a documented simplification, not a rebuild of the below-EBITDA lines by scenario). **This re-anchoring has not been tested and is not a substitute for C7's own build**; it exists so the judge's question can be answered for all three scenarios rather than base only.

| scenario | period | fcf | fcf_ex_sbc (SBC-adjusted) | capex | sbc | fcf_yield_pct | fcf_exsbc_yield_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| base (M7-own) | FY26 | 4,906.6 | 3,092.9 | 38.9 | 1,813.7 | 4.92 | 3.10 |
| base (M7-own) | FY27 | 5,361.8 | 3,309.0 | 35.7 | 2,052.7 | 5.59 | 3.45 |
| base (LB-anchored, DERIVED) | FY26 | 4,844.6 | 3,030.8 | 38.9 | 1,813.7 | 4.85 | 3.04 |
| base (LB-anchored, DERIVED) | FY27 | 5,429.4 | 3,376.7 | 35.7 | 2,052.7 | 5.66 | 3.52 |
| short (DERIVED) | FY26 | 4,573.8 | 2,760.1 | 38.9 | 1,813.7 | 4.58 | 2.77 |
| short (DERIVED) | FY27 | 4,701.1 | 2,648.4 | 35.7 | 2,052.7 | 4.90 | 2.76 |
| breaker (DERIVED) | FY26 | 4,923.3 | 3,109.5 | 38.9 | 1,813.7 | 4.93 | 3.12 |
| breaker (DERIVED) | FY27 | 5,742.3 | 3,689.6 | 35.7 | 2,052.7 | 5.98 | 3.84 |

Yields are FCF ÷ (spot $167.51, DEC-0015 provisional × diluted shares). Diluted share count: **595.8M (FY26 average), 573.0M (FY27 average)**, from `M7_below_ebitda_annual_forecasts.csv` `diluted_shares_m` — itself rolled forward from the 2Q26 10-Q's 597.0M weighted-average diluted count (`M7_parameter_sheet.csv` `diluted_shares_2q26`) net of the buyback-pace/RSU-issuance rule. Market cap used: $99,795.2M (FY26 basis), $95,990.1M (FY27 basis).

**The reverse-DCF growth the memo quotes.** `research/notes/reverse_dcf/audit_A.md` §1 (auditor-verified, PASS WITH FIXES): "Reverse DCF at $170.19, reported / SBC-adjusted | 4.61% / 15.95%" — i.e. at the 11 Sep 2026 price of $170.19, a fade-DCF (mid-year discounting from 30 Sep 2026, linear fade FY28–FY36, Gordon terminal, WACC 10%, terminal 3%) needs FCF to grow **4.61%** (reported) or **15.95% ≈ 16%** (SBC-adjusted) to justify the price. This is the exact source of memo v3's "needs 16% FCF growth on a reverse DCF" (`deck/drafts/memo_v3_short_2026-09-17.md`: "on SBC-adjusted FCF the stock yields ~3% and the price needs 16% FCF growth on a reverse DCF"). **Not recomputed here**: it was solved at $170.19, not the $167.51 DEC-0015 provisional spot, and the reverse-DCF package (`analysis/src/reverse_dcf/`) is outside the two packages this brief permits me to touch.

### 2a. Model inputs (machine-readable)

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| fcf_musd | actual | 1Q23 | 1581.0 | USD m | abnb_fcf_bridge.csv row 1Q23, col fcf |
| fcf_musd | actual | 2Q23 | 900.0 | USD m | abnb_fcf_bridge.csv row 2Q23, col fcf |
| fcf_musd | actual | 3Q23 | 1310.0 | USD m | abnb_fcf_bridge.csv row 3Q23, col fcf |
| fcf_musd | actual | 4Q23 | 46.0 | USD m | abnb_fcf_bridge.csv row 4Q23, col fcf |
| fcf_musd | actual | 1Q24 | 1909.0 | USD m | abnb_fcf_bridge.csv row 1Q24, col fcf |
| fcf_musd | actual | 2Q24 | 1043.0 | USD m | abnb_fcf_bridge.csv row 2Q24, col fcf |
| fcf_musd | actual | 3Q24 | 1074.0 | USD m | abnb_fcf_bridge.csv row 3Q24, col fcf |
| fcf_musd | actual | 4Q24 | 458.0 | USD m | abnb_fcf_bridge.csv row 4Q24, col fcf |
| fcf_musd | actual | 1Q25 | 1781.0 | USD m | abnb_fcf_bridge.csv row 1Q25, col fcf |
| fcf_musd | actual | 2Q25 | 962.0 | USD m | abnb_fcf_bridge.csv row 2Q25, col fcf |
| fcf_musd | actual | 3Q25 | 1349.0 | USD m | abnb_fcf_bridge.csv row 3Q25, col fcf |
| fcf_musd | actual | 4Q25 | 521.0 | USD m | abnb_fcf_bridge.csv row 4Q25, col fcf |
| fcf_musd | actual | 1Q26 | 1704.0 | USD m | abnb_fcf_bridge.csv row 1Q26, col fcf |
| fcf_musd | actual | 2Q26 | 1253.0 | USD m | abnb_fcf_bridge.csv row 2Q26, col fcf |
| capex_musd | actual | 1Q23 | 6.0 | USD m | abnb_fcf_bridge.csv row 1Q23, col capex, absolute value (stored negative in the source) |
| capex_musd | actual | 2Q23 | 9.0 | USD m | abnb_fcf_bridge.csv row 2Q23, col capex, absolute value |
| capex_musd | actual | 3Q23 | 15.0 | USD m | abnb_fcf_bridge.csv row 3Q23, col capex, absolute value |
| capex_musd | actual | 4Q23 | 17.0 | USD m | abnb_fcf_bridge.csv row 4Q23, col capex, absolute value |
| capex_musd | actual | 1Q24 | 14.0 | USD m | abnb_fcf_bridge.csv row 1Q24, col capex, absolute value |
| capex_musd | actual | 2Q24 | 8.0 | USD m | abnb_fcf_bridge.csv row 2Q24, col capex, absolute value |
| capex_musd | actual | 3Q24 | 4.0 | USD m | abnb_fcf_bridge.csv row 3Q24, col capex, absolute value |
| capex_musd | actual | 4Q24 | 8.0 | USD m | abnb_fcf_bridge.csv row 4Q24, col capex, absolute value |
| capex_musd | actual | 1Q25 | 8.0 | USD m | abnb_fcf_bridge.csv row 1Q25, col capex, absolute value |
| capex_musd | actual | 2Q25 | 13.0 | USD m | abnb_fcf_bridge.csv row 2Q25, col capex, absolute value |
| capex_musd | actual | 3Q25 | 7.0 | USD m | abnb_fcf_bridge.csv row 3Q25, col capex, absolute value |
| capex_musd | actual | 4Q25 | 5.0 | USD m | abnb_fcf_bridge.csv row 4Q25, col capex, absolute value |
| capex_musd | actual | 1Q26 | 4.0 | USD m | abnb_fcf_bridge.csv row 1Q26, col capex, absolute value |
| capex_musd | actual | 2Q26 | 17.0 | USD m | abnb_fcf_bridge.csv row 2Q26, col capex, absolute value |
| sbc_musd | actual | 1Q23 | 240.0 | USD m | abnb_fcf_bridge.csv row 1Q23, col sbc (letter-reported total) |
| sbc_musd | actual | 2Q23 | 304.0 | USD m | abnb_fcf_bridge.csv row 2Q23, col sbc |
| sbc_musd | actual | 3Q23 | 286.0 | USD m | abnb_fcf_bridge.csv row 3Q23, col sbc |
| sbc_musd | actual | 4Q23 | 290.0 | USD m | abnb_fcf_bridge.csv row 4Q23, col sbc; exsbc_stack's own `sbc_total` field misreports this quarter as 270.0 (see §5) |
| sbc_musd | actual | 1Q24 | 295.0 | USD m | abnb_fcf_bridge.csv row 1Q24, col sbc |
| sbc_musd | actual | 2Q24 | 382.0 | USD m | abnb_fcf_bridge.csv row 2Q24, col sbc |
| sbc_musd | actual | 3Q24 | 362.0 | USD m | abnb_fcf_bridge.csv row 3Q24, col sbc |
| sbc_musd | actual | 4Q24 | 368.0 | USD m | abnb_fcf_bridge.csv row 4Q24, col sbc; exsbc_stack's own `sbc_total` field misreports this quarter as 400.0 (see §5) |
| sbc_musd | actual | 1Q25 | 358.0 | USD m | abnb_fcf_bridge.csv row 1Q25, col sbc |
| sbc_musd | actual | 2Q25 | 424.0 | USD m | abnb_fcf_bridge.csv row 2Q25, col sbc |
| sbc_musd | actual | 3Q25 | 399.0 | USD m | abnb_fcf_bridge.csv row 3Q25, col sbc |
| sbc_musd | actual | 4Q25 | 411.0 | USD m | abnb_fcf_bridge.csv row 4Q25, col sbc; exsbc_stack's own `sbc_total` field misreports this quarter as 400.0 (see §5) |
| sbc_musd | actual | 1Q26 | 410.0 | USD m | abnb_fcf_bridge.csv row 1Q26, col sbc |
| sbc_musd | actual | 2Q26 | 487.0 | USD m | abnb_fcf_bridge.csv row 2Q26, col sbc |
| fcf_ex_sbc_musd | actual | 1Q23 | 1341.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_ex_sbc_musd | actual | 2Q23 | 596.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_ex_sbc_musd | actual | 3Q23 | 1024.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_ex_sbc_musd | actual | 4Q23 | -244.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_ex_sbc_musd | actual | 1Q24 | 1614.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_ex_sbc_musd | actual | 2Q24 | 661.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_ex_sbc_musd | actual | 3Q24 | 712.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_ex_sbc_musd | actual | 4Q24 | 90.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_ex_sbc_musd | actual | 1Q25 | 1423.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_ex_sbc_musd | actual | 2Q25 | 538.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_ex_sbc_musd | actual | 3Q25 | 950.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_ex_sbc_musd | actual | 4Q25 | 110.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_ex_sbc_musd | actual | 1Q26 | 1294.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_ex_sbc_musd | actual | 2Q26 | 766.0 | USD m | derived: fcf_musd minus sbc_musd, same row |
| fcf_musd | base | FY26 | 4844.6 | USD m | DERIVED: M7-own FY26 base fcf (4906.6) plus (C6 LB EBITDA 5098.5 minus M7-own EBITDA 5174.0) x (1 minus 17.74% ETR) |
| fcf_musd | base | FY27 | 5429.4 | USD m | DERIVED: M7-own FY27 base fcf (5361.8) plus (C6 LB EBITDA 5644.2 minus M7-own EBITDA 5562.2) x (1 minus 17.50% ETR) |
| fcf_musd | short | FY26 | 4573.8 | USD m | DERIVED: base(LB-anchored) fcf plus (C6 short EBITDA 4769.4 minus C6 LB base EBITDA 5098.5) x (1 minus 17.74% ETR) |
| fcf_musd | short | FY27 | 4701.1 | USD m | DERIVED: base(LB-anchored) fcf plus (C6 short EBITDA 4761.4 minus C6 LB base EBITDA 5644.2) x (1 minus 17.50% ETR) |
| fcf_musd | breaker | FY26 | 4923.3 | USD m | DERIVED: base(LB-anchored) fcf plus (C6 breaker EBITDA 5194.2 minus C6 LB base EBITDA 5098.5) x (1 minus 17.74% ETR) |
| fcf_musd | breaker | FY27 | 5742.3 | USD m | DERIVED: base(LB-anchored) fcf plus (C6 breaker EBITDA 6023.5 minus C6 LB base EBITDA 5644.2) x (1 minus 17.50% ETR) |
| fcf_ex_sbc_musd | base | FY26 | 3030.8 | USD m | DERIVED: fcf_musd base FY26 minus sbc_musd 1813.7 (M7-own base SBC, held flat across scenarios per M7_parameter_sheet.csv) |
| fcf_ex_sbc_musd | base | FY27 | 3376.7 | USD m | DERIVED: fcf_musd base FY27 minus sbc_musd 2052.7 |
| fcf_ex_sbc_musd | short | FY26 | 2760.1 | USD m | DERIVED: fcf_musd short FY26 minus sbc_musd 1813.7 |
| fcf_ex_sbc_musd | short | FY27 | 2648.4 | USD m | DERIVED: fcf_musd short FY27 minus sbc_musd 2052.7 |
| fcf_ex_sbc_musd | breaker | FY26 | 3109.5 | USD m | DERIVED: fcf_musd breaker FY26 minus sbc_musd 1813.7 |
| fcf_ex_sbc_musd | breaker | FY27 | 3689.6 | USD m | DERIVED: fcf_musd breaker FY27 minus sbc_musd 2052.7 |
| capex_musd | base | FY26 | 38.9 | USD m | M7_below_ebitda_annual_forecasts.csv FY2026 base capex_musd; held flat across scenarios (M7_parameter_sheet.csv capex_musd_q, recency-weighted, not scenario-conditioned) |
| capex_musd | base | FY27 | 35.7 | USD m | M7_below_ebitda_annual_forecasts.csv FY2027 base capex_musd |
| capex_musd | short | FY26 | 38.9 | USD m | held at the base rule (see note above); NOT a short-case-specific capex build |
| capex_musd | short | FY27 | 35.7 | USD m | held at the base rule |
| capex_musd | breaker | FY26 | 38.9 | USD m | held at the base rule |
| capex_musd | breaker | FY27 | 35.7 | USD m | held at the base rule |
| fcf_yield_pct | base | FY26 | 4.85 | pct | fcf_musd base FY26 (4844.6) / (167.51 x 595.8m diluted shares = 99,795.2) |
| fcf_yield_pct | base | FY27 | 5.66 | pct | fcf_musd base FY27 (5429.4) / (167.51 x 573.0m diluted shares = 95,990.1) |
| fcf_yield_pct | short | FY26 | 4.58 | pct | fcf_musd short FY26 / 99,795.2 |
| fcf_yield_pct | short | FY27 | 4.90 | pct | fcf_musd short FY27 / 95,990.1 |
| fcf_yield_pct | breaker | FY26 | 4.93 | pct | fcf_musd breaker FY26 / 99,795.2 |
| fcf_yield_pct | breaker | FY27 | 5.98 | pct | fcf_musd breaker FY27 / 95,990.1 |
| fcf_exsbc_yield_pct | base | FY26 | 3.04 | pct | fcf_ex_sbc_musd base FY26 (3030.8) / 99,795.2; the memo's "~3%" quantity |
| fcf_exsbc_yield_pct | base | FY27 | 3.52 | pct | fcf_ex_sbc_musd base FY27 (3376.7) / 95,990.1 |
| fcf_exsbc_yield_pct | short | FY26 | 2.77 | pct | fcf_ex_sbc_musd short FY26 / 99,795.2 |
| fcf_exsbc_yield_pct | short | FY27 | 2.76 | pct | fcf_ex_sbc_musd short FY27 / 95,990.1 |
| fcf_exsbc_yield_pct | breaker | FY26 | 3.12 | pct | fcf_ex_sbc_musd breaker FY26 / 99,795.2 |
| fcf_exsbc_yield_pct | breaker | FY27 | 3.84 | pct | fcf_ex_sbc_musd breaker FY27 / 95,990.1 |
| fcf_growth_required_pct | base | all | 4.61 | pct | research/notes/reverse_dcf/audit_A.md sec 1, reverse DCF at $170.19 (11 Sep 2026, not the $167.51 DEC-0015 provisional spot), reported FCF, fade-DCF WACC 10% terminal 3% |
| fcf_growth_required_pct | base | all | 15.95 | pct | same source, SBC-adjusted FCF; this is the memo's quoted "16% FCF growth" |

## 3. Derivation chain

**Historical (§2 top table, §2a `actual` rows):**
1. Shareholder letters (8-K Ex. 99.1), Adjusted EBITDA and Free Cash Flow reconciliations, quoted verbatim per `abnb_fcf_bridge.py`'s header →
2. `data/processed/abnb_fcf_bridge.csv`, columns `fcf`, `capex`, `sbc` →
3. this dossier's `fcf_ex_sbc = fcf − sbc` (no script; arithmetic in `c8_fcf_recompute.py`, receipts/C8) →
4. `data/processed/pitch_model_v2/receipts/C8/c8_history_fcf_exsbc.csv`.

**FY26/FY27, base (M7-own):**
1. 2Q26 10-Q (diluted shares, buyback authorisation, interest expense), FRED DTB3/DGS1, WS02/WS04/WS05/WS06 panels →
2. `data/processed/margin_build/M7_below_ebitda/M7_parameter_sheet.csv` (below-EBITDA rules: SBC y/y growth off SBC[q−4], flat capex and D&A, interest-income beta rule, ETR 17.74%/17.50%, buyback/issuance share rollforward) and the `driver-lines/a_unit_rw` EBITDA registry vintage →
3. `analysis/src/margin_build/M7_below_ebitda/` (not run by me) →
4. `data/processed/margin_build/M7_below_ebitda/M7_below_ebitda_annual_forecasts.csv`, rows FY2026/FY2027, `ebitda_source=driver-lines`, `scenario=base`.

**FY26/FY27, base/short/breaker (LB-anchored, DERIVED):**
1. `M7_below_ebitda_annual_forecasts.csv` (step above) →
2. `docs/pitch-model-v2/dossiers/C6_c6_ebitda.md` §2a, adopted line-build (LB) `adj_ebitda_musd` for base/short/breaker →
3. `data/processed/pitch_model_v2/receipts/C8/c8_fy_derivation.py` (this dossier's own script: EBITDA-delta-after-tax re-anchoring, formula in §2) →
4. `data/processed/pitch_model_v2/receipts/C8/c8_fy_fcf_by_scenario.csv`.

**Reverse-DCF growth:** `research/notes/reverse_dcf/A_joint-solve.md` §3.4 (method) and `research/notes/reverse_dcf/audit_A.md` §1 (auditor-verified headline figure), read only — not recomputed.

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-11 | `analysis/src/abnb_fcf_bridge.py`, `abnb_exsbc_stack.py` (headers) | both call `ensure_letters()`, which fetches `data/raw/letters/*.htm` from SEC EDGAR when absent | **Governs** the decision not to run either script: `data/raw/letters/` does not exist in this checkout (confirmed §5), so a run would be a network fetch, which the brief forbids for these two scripts specifically |
| 2026-09-11 (late evening) | `docs/rnpl-short-audit/05_quality-of-growth-study.md` | FCF gap is timing not level; 1H26 FCF ex-float +24.4% vs revenue +17.1%; permanent 2027 RNPL cash cost ≈ $106M (0.7pp margin); cash-conversion test moves to 1Q27, not 5 Nov | **Governs** the "timing or level" half of the judge's question. This is the note the brief names ("~$106M permanent") |
| 2026-09-13 | `research/notes/reverse_dcf/audit_A.md` | reverse DCF at $170.19: reported 4.61%, SBC-adjusted 15.95% required FCF growth | **Governs** the `fcf_growth_required_pct` figure; supersedes the un-audited `A_joint-solve.md` draft numbers where they differ (none did here — the audit reproduced them byte-for-byte) |
| 2026-09-15 | `docs/margin-build/notes/40_line_build.md`, `40_short_case_summary.csv` | line-build (LB) FY26/FY27 adjusted EBITDA by scenario | **Governs** the EBITDA inputs to the LB-anchored FCF re-anchoring, via C6's dossier (below) |
| 2026-09-17 | `deck/drafts/memo_v3_short_2026-09-17.md` | "Adjusted EBITDA excludes $1.8bn of FY26 SBC (35% of EBITDA); on SBC-adjusted FCF the stock yields ~3% and the price needs 16% FCF growth on a reverse DCF" | **Governs** the judge's question and the two claims this dossier checks (both consistent with the record: $1,813.7M FY26 SBC is 35.6% of the LB FY26 EBITDA $5,098.5M; SBC-adjusted yield here is 3.0–3.5% depending on scenario/vintage; 15.95% ≈ 16% growth is exact) |
| 2026-09-18 | `docs/pitch-model-v2/dossiers/C6_c6_ebitda.md` | adopted (LB) and scenario (short/breaker) FY26/FY27 adjusted EBITDA; graded B | **Governs** the EBITDA anchor for the DERIVED FCF re-anchoring in §2 |
| 2026-09-18 | DEC-0003, DEC-0011, DEC-0015, DEC-0016 | history basis; line build is the adopted cost stack; spot $167.51 provisional; no leaning | **Governs** this dossier's basis, EBITDA choice, yield denominator, and the refusal to pick inputs that flatter either side |
| 2026-09-13/14 (harness run), read 2026-09-18 | `data/processed/margin_build/10_harness_margin/scoreboard_margin.csv`/`.md`, method `below-ebitda` object `fcf` | quarterly `fcf_musd`/`fcf_margin_pct`, h=0, PIT: no spec beats `seasonal_naive` in both W1 and W2 on both weightings; best spec beats the Street (ratio 0.49–0.60) | **Governs** §6's test record; supersedes this dossier's own first-draft claim (not published) that "no backtest exists" for FCF |

Web fetches: **none**.

## 5. Reproduction receipt

- Receipt: `data/processed/pitch_model_v2/receipts/C8/receipt.json`
- **Neither of the brief's two target scripts was run.** Both `analysis/src/abnb_fcf_bridge.py` and `analysis/src/abnb_exsbc_stack.py` call `ensure_letters()` at the top of their `__main__` (lines 158 and 131 respectively), which downloads 23 shareholder-letter `.htm` files from `www.sec.gov` via `urllib.request` whenever `data/raw/letters/` is missing or incomplete. Confirmed: `data/raw/letters/` does not exist anywhere in this checkout (`find` returned nothing), and no cached copy exists under `~/Citadel-ABNB-untracked/`. Per the brief ("if either fetches from the network, do not run it and say so"), **neither script was executed.**
- What was run instead, through the wrapper, reading only committed CSVs and writing only into `receipts/C8/`:
  - Command 1: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id C8 --watch data/processed/abnb_fcf_bridge.csv --watch data/processed/abnb_quarterly_cost_stack_exsbc.csv --cmd "python3 data/processed/pitch_model_v2/receipts/C8/c8_fcf_recompute.py"` · Exit: **0** · Wall: 0.0s · Interpreter: `python3` (3.13.0) · `changed: []`, `new_files: []` (my new files under `receipts/C8/` are outside the watched paths, as intended).
  - Command 2: same wrapper, `--watch` adding `data/processed/margin_build/M7_below_ebitda/M7_below_ebitda_annual_forecasts.csv`, `--cmd "python3 data/processed/pitch_model_v2/receipts/C8/c8_fy_derivation.py"` · Exit: **0** · `changed: []`, `new_files: []`.
- Output: `data/processed/pitch_model_v2/receipts/C8/c8_history_fcf_exsbc.csv` recomputes `fcf_ex_sbc` for all 14 quarters 1Q23–2Q26 from the committed `abnb_fcf_bridge.csv` · Committed value: n/a (this column does not exist upstream; it is newly derived here from two upstream columns that do match their letters) · **Match: yes** on the two upstream columns it reads (`fcf`, `sbc`), read back byte-identical from the committed CSV.
- **A genuine cross-check finding, not invented for this dossier.** `abnb_fcf_bridge.csv`'s `sbc` column (letter-reported total SBC) matches `abnb_quarterly_cost_stack_exsbc.csv`'s `sbc_total` field in 11 of 14 quarters, but **disagrees in three — all Q4s**: 4Q23 (290.0 vs 270.0), 4Q24 (368.0 vs 400.0), 4Q25 (411.0 vs 400.0). In every one of these three quarters, `sbc_total_letter` (the letter's own printed total, a separate field in the same CSV) and the sum of the four function components (`sbc_ops+sbc_pd+sbc_sm+sbc_ga`) both agree with `abnb_fcf_bridge.csv`'s number, not with `sbc_total`. So `abnb_exsbc_stack.py`'s `sbc_total` field appears to mis-populate itself specifically in Q4 rows (full detail: `data/processed/pitch_model_v2/receipts/C8/c8_sbc_crosscheck.json`). This does not affect `abnb_fcf_bridge.csv` (which is the source for every FCF number in this dossier) or `sbc_total_letter`; it is a latent bug in one column of the sibling package that I am not permitted to fix (packages I may touch are the two CSVs, not the exsbc script), so it is reported here as a finding for the exsbc_stack line owners.
- The `abnb_fcf_bridge.csv` internal identity `fcf_check_gap` (FCF = CFO − capex per the letter) is **0.0 in all 14 quarters** — the one identity check available on this line passes exactly.
- Artefacts in the receipt folder: `c8_fcf_recompute.py`, `c8_fy_derivation.py` (the two scripts), `c8_history_fcf_exsbc.csv`, `c8_sbc_crosscheck.json`, `c8_fy_fcf_by_scenario.csv`, `receipt.json`, `stdout.txt`/`stderr.txt`.

## 6. Test record

A quarterly registered test **does** exist for this line, in the shared, read-only margin harness (`data/processed/margin_build/10_harness_margin/scoreboard_margin.csv` / `.md`, method `below-ebitda`, object `fcf`, target `fcf_musd` — 8 competing bridge specs: `swing_x_gbv`, `swing_x_gbv_seasonal_other`, `balance_ratio`, each ×`_ebitda_known` oracle variant ×`|rw`/`|eq` weighting). I did not run the scorer (forbidden by the brief); I read its committed output. Per the margin-build kill list rule C7's dossier also applies ("do not quote a margin MAE ratio without its p-value and quarters-better count"), figures below carry both.

| window | n | metric | this line (best PIT spec, MAE ratio to seasonal_naive) | rw-weighted ratio | quarters better | p (sign test) | vs Street (ratio) | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|---|
| W1 | 14 | `fcf_musd`, h=0, PIT, spec `swing_x_gbv_seasonal_other\|rw` | 1.018 | 1.090 | 8/14 | 0.395 (not sig.) | 0.604 (beats Street) | MAE < seasonal_naive, h=0, both windows, both weightings | **FAIL** (ratio > 1) |
| W2 | 10 | `fcf_musd`, h=0, PIT, same spec | 0.927 | 1.054 | 6/10 | 0.377 (not sig.) | 0.491 (beats Street) | same | **FAIL on rw**, marginal pass on raw ratio only; not both-weightings |
| W1 | 14 | `fcf_margin_pct`, h=0, PIT, same spec | 1.219 | 1.126 | 7/14 | 0.605 | — | same | **FAIL** |
| W2 | 10 | `fcf_margin_pct`, h=0, PIT, same spec | 0.999 | 1.039 | 6/10 | 0.377 | — | same | **FAIL on rw**, essentially tied on raw |
| — | — | every other bridge spec (`swing_x_gbv`, `balance_ratio`, `\|eq` weighting), h=0, PIT, both windows | ratios 1.03–1.95 | 1.05–2.12 | — | — | — | same | **FAIL**, more decisively |
| — | 14 | `fcf_check_gap` internal identity (`abnb_fcf_bridge.csv`) | 0.0 in 14/14 quarters | — | — | — | — | identity should hold to rounding | **PASS** (exact) |
| — | 14 | `sbc` cross-check, `abnb_fcf_bridge.csv` vs `abnb_quarterly_cost_stack_exsbc.csv`'s `sbc_total` | 11/14 match | — | — | — | — | — | 3 Q4 mismatches found and reported (§5); a data-quality finding, not a pass/fail test |

Two honest caveats on the harness row. First, `prior_basis=full_sample` rows in the same table show ratios well below 1 (0.65–0.68, "both"=True) — but `full_sample` recalibrates on the whole sample including the future relative to each test date, which AGENT_BRIEF's point-in-time rule (§ "Refit at guide dates") excludes; only the `PIT` rows are admissible, and every PIT spec fails at h=0 in at least one window. Second, this quarterly harness object and this dossier's own FY26/FY27 §2 figures are **not the same build**: the harness scores an M7-family bridge spec against realised quarters; §2's forward numbers are M7's own annual roll-up (base) and this dossier's linear re-anchoring (short/breaker). They share a lineage (both descend from `M7_below_ebitda`'s below-EBITDA rules) but neither is a direct reproduction of the other.

Strongest known failure: **the one registered, both-windows-tested object for this line fails outright** — no PIT bridge spec for `fcf_musd` beats the seasonal-naive baseline in both W1 and W2 on both the raw and recency-weighted MAE ratio (all "both"/"rw_both" flags are False), and the best spec is a coin flip in significance (p ≈ 0.38–0.40, 6–8 of 10–14 quarters better). It does, however, consistently beat the Street's own FCF estimate (ratio 0.49–0.60) — the naive quarter-ago value is a harder bar than consensus for this line. The FY26/FY27 scenario table in §2 inherits this untested status one level further down, plus an unreconciled $75–82M EBITDA-source gap and, for short/breaker, a same-day linear approximation that has never been scored at all.

## 7. Kill list and consistency

- **Kill-list check:** none of `AGENT_BRIEF.md` §6's withdrawn numbers concern FCF or SBC directly; nothing here quotes one.
- **Conflicts found.**
  1. **EBITDA-source mismatch, base case.** M7's own "driver-lines/a_unit_rw" EBITDA (FY26 $5,174.0M, FY27 $5,562.2M, vintage 2026-09-11) is not the same object as C6's post-audit adopted line-build EBITDA (FY26 $5,098.5M, FY27 $5,644.2M, vintage 2026-09-15/18) — a $75.5M (FY26) and $82.0M (FY27) gap in opposite directions. §2 reports both; the LB-anchored row is this dossier's attempt to reconcile them, not an authoritative fix. **This is properly C7's line** (SBC/D&A/interest/tax/share count/EPS, per its brief) and should be resolved there, ideally by re-running `M7_below_ebitda` with the line-build EBITDA as its input rather than by the linear patch used here.
  2. **`abnb_exsbc_stack.py`'s `sbc_total` field bug** (§5): three Q4 quarters (4Q23, 4Q24, 4Q25) where that one field disagrees with its own component sum and its own `sbc_total_letter` field, which do agree with `abnb_fcf_bridge.csv`. Flagged for the exsbc_stack line owner; not fixed here (out of the two packages I may touch).
  3. **Memo v3's "~3% / 16%" claims, checked, not contradicted.** SBC-adjusted FY26/FY27 base yield here is 3.0–3.5% (M7-own or LB-anchored, at spot $167.51) and the reverse-DCF SBC-adjusted growth requirement is 15.95% ≈ 16% (at $170.19, not $167.51 — the memo's own reverse-DCF number was solved at a higher price than the current provisional spot, so the true growth requirement at $167.51 is very slightly lower than 16%, a direction not a contradiction).
  4. **Short/breaker FCF has no built object.** The brief allows "base only and say so" for scenarios the record does not support; I went further and built a labelled DERIVED estimate rather than stop at base-only, because the judge's question is explicitly about the stock's cash yield across the thesis's own bear/bull framing. That choice is flagged in §8.1 for the humans to accept, reject, or replace with C7's eventual proper build.

## 8. Open choices

1. **Keep the DERIVED short/breaker FCF re-anchoring, or report base only?** Options: **(a)** keep it, clearly labelled DERIVED/untested, because a memo answering "is FCF timing or level, and what does the stock yield" without a bear/bull cash view is incomplete; **(b)** drop short/breaker and report base only, per the brief's explicit fallback, until C7 builds a proper below-EBITDA scenario engine; **(c)** keep it but move it to an appendix/footnote rather than the headline table. — **Recommendation: (a)**, with the label kept prominent, because the DERIVED numbers are directionally sound (short FCF yield 2.8% ex-SBC, breaker 3.1–3.8%, both bracketing the base case sensibly) and the alternative is silence on exactly the question the judge is asking; but this should be superseded by C7's own build as soon as it lands.
2. **Which base FY26/FY27 FCF does the memo quote — M7-own or LB-anchored?** Options: **(a)** LB-anchored, because DEC-0011 already made the line build the model's adopted cost stack, and every other C-line (C1, C4, C6) reports on that basis; **(b)** M7-own, because it is the only object that was actually built end-to-end by a below-EBITDA engine rather than patched by this dossier; **(c)** show both, as §2 does. — **Recommendation: (a) for the headline, (c) for the workbook**, for the same consistency reason C6 gave for choosing the line build: the memo's other cost and margin lines are already on that basis, and mixing EBITDA sources across a single P&L would be worse than a $75–82M patch.
3. **Report the reverse-DCF growth figure at $170.19 (as audited) or ask for a re-solve at $167.51?** Options: **(a)** quote 15.95%/4.61% as-is with the price noted, since the direction of the DEC-0015 refresh (lower price than $170.19) only makes the required growth slightly easier, not harder, to justify — conservative for a short; **(b)** flag it as stale and defer the number until the reverse_dcf package is re-run at $167.51 (out of scope for this brief). — **Recommendation: (a)**, on the same DEC-0016 "no leaning" logic C6 and C4 used: I am not the owner of that package and should not recompute it, but noting the direction (very slightly less than 16%, not more) is honest bookkeeping, not a lean.

## 9. Judge Q&A
1. Q: **What does the stock yield on cash?** A: On SBC-adjusted (ex-SBC) FCF, about 3.0% for FY26 and 3.5% for FY27 in the base case at the DEC-0015 provisional spot of $167.51 — consistent with memo v3's "~3%." On reported FCF (which already treats SBC as non-cash, the conventional definition) the yield is materially higher, 4.85–4.93% FY26 and 4.90–5.98% FY27 across base/short/breaker, because $1.8–2.1bn/year of the reported number is stock, not cash returned to holders who are not also being diluted.
2. Q: **Is FCF timing or level?** A: Timing. The quality-of-growth study on record (`docs/rnpl-short-audit/05_quality-of-growth-study.md`) found the reported FCF-margin swing (47% vs 51% y/y in the RNPL-transition quarters) is entirely the unearned-fees float shift, not a change in underlying conversion: 1H26 FCF ex-float actually grew *faster* than revenue (+24.4% vs +17.1%), and the durable RNPL cash cost into FY27 is small, about $106M or 0.7pp of margin. History confirms the float's size: quarterly FCF ex-SBC swings from −$244M (4Q23) to +$1,614M (1Q24) purely on `change_unearned_fees`, a swing an order of magnitude larger than any plausible level shift in the underlying business that quarter.
3. Q: **The memo says the price needs 16% FCF growth on a reverse DCF — is that still right?** A: The number (15.95% SBC-adjusted, 4.61% reported) is exactly reproduced from `research/notes/reverse_dcf/audit_A.md`, which independently re-derived and verified it. It was solved at $170.19 (11 Sep close); the model's current provisional spot is $167.51 (DEC-0015, 16 Sep close), a lower price, which would require *slightly less* than 16% growth, not more — so the memo's claim is if anything conservative for a short thesis, not overstated.
4. Q: **Why isn't there a base/short/breaker FCF number already built for this line, and has FCF ever been tested?** A: FCF sits below EBITDA, and the pitch-model-v2 batch split that work into C6 (EBITDA) and C7 (SBC/D&A/interest/tax/shares/EPS); C7's dossier was still landing as I read the repo, and its own §4 notes "quarterly FCF fails both windows (out of C7's scope)." I confirmed that directly in the shared harness registry (§6): across eight competing bridge specs, the best one has an MAE ratio to the seasonal-naive baseline of 1.018 in W1 (fails) and 0.927 in W2 (passes on the raw ratio only, not the recency-weighted one, and not significantly, p ≈ 0.38–0.40) — no spec clears both windows on both weightings. It does beat the Street's own FCF estimate (ratio 0.49–0.60) consistently. Given that, and given the only complete below-EBITDA-to-FCF engine (`M7_below_ebitda`) was built on an EBITDA source that predates C6's line-build EBITDA, I built a labelled, untested linear re-anchoring for short/breaker (§2, §8.1) rather than leave them blank — but that patch, and the base case itself, should be superseded by C7's own scenario-conditioned build.

## 10. Grade
Grade: C — the two scripts that own this line cannot be run without a network fetch the brief forbids, so there is no fresh reproduction receipt for `abnb_fcf_bridge.py`/`abnb_exsbc_stack.py` themselves; the historical numbers in §2 are read directly from their committed output (one internal identity check passes exactly, and a genuine three-quarter data-quality bug was found and reported, not fixed); and the FY26/FY27 forward numbers are, for base, an as-built object with an unreconciled EBITDA-source gap to the model's adopted stack, and for short/breaker, a same-day DERIVED linear re-anchoring that has never been scored. The one place a real W1/W2 test does exist for this line (the shared harness's `below-ebitda/fcf` registry, §6) is a clean **FAIL**: no bridge spec beats the seasonal-naive baseline in both windows on both weightings at h=0. A grade of A is foreclosed by the missing reproduction receipt and by that failed test; B is foreclosed because nothing here is "reproduced, single-window or descriptive" in the sense the brief means — the forward numbers are a same-day derivation, not a reproduction of a committed object. This is a reproduced-where-possible, honestly-tested-where-testable, otherwise descriptive dossier — exactly a C, and per the brief a valid, useful one: it answers the judge's question, sources every number, reports a real (negative) test result rather than claiming none exists, and flags two concrete, unresolved issues (the EBITDA-source gap and the exsbc_stack Q4 bug) for the lines that own them.
