# RESEARCH LOG

Revision 2 (2026-09-17, audit response to A08, Fable 5.1). Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A08). Companion questions in this batch: F01 `q1-27-nights-guide-above-82` (same 4Q26 object), F03 `fy27-margin-guide`, F04 `fy27-sm-share-above-219`. Reproduction: [datasets/f02_model_v2.py](datasets/f02_model_v2.py) (base, pre-registration component, final mixture and sensitivities in one script; numpy only, seed 20260917, 400,000 draws, ~40 s; writes `f02_v2_summary.csv`, `f02_v2_percentiles.csv`, `f02_v2_hist.csv`, `f02_v2_sensitivity.csv`). Revision-1 `f02_model.py`, `f02_final_mixture.py` and their CSVs are left untouched as the audit trail. Audit: `docs/pitch-forecasts/audits/A08-research-audit.md`; response: `audits/A08-audit-response.md`.

## 0. Metadata
- question_name: q1-27-revenue-guide-growth
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` F02)
- type: continuous
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-16
- close_date: 2027-02-11
- resolution_date: 2027-02-11
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 2
- revised: 2026-09-17
- agent: fable

## 0b. Question (verbatim)
### Title
What year-over-year growth will the midpoint of Airbnb's 1Q27 revenue guidance imply, at the Feb print?
### Resolution Criteria
**Type.** Continuous (percent). Percentile table plus P(< 10%), P(< 9.4%), P(≥ 12%).
### Fine Print
Base 1Q26 revenue $2,678M. Kernel put the midpoint at $2,930–2,990M (+9.4 to +11.6%). Resolution date ~11 Feb 2027.

Conventions adopted (stated, not changing the question): (1) the midpoint is the arithmetic mean of the two dollar endpoints printed in the 4Q26 shareholder letter's Outlook, divided by $2,678M, minus one, in percent to one decimal; (2) if only a growth range is printed, its midpoint resolves; if both, the dollar range governs (registry convention for C01); (3) "Feb print" = the 4Q26 release on its actual date (Airbnb has not announced it; the last three were 13 Feb 2024, 13 Feb 2025, 12 Feb 2026); (4) if no 1Q27 revenue guide is given (never happened in 20 letters since 3Q21), the question is void; that 1% is carried outside the distribution, not as bound mass; (5) working range for bound mass is 0% to 20%.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Every February letter since 4Q21 has carried a Q1 revenue dollar range (5 of 5): 1Q22 $1.41–1.48bn (actual 1,509, +4.43% vs mid); 1Q23 $1.75–1.82bn (1,818, +1.85%); 1Q24 $2.03–2.07bn (2,142, +4.49%); 1Q25 $2.23–2.27bn (2,272, +0.98%); 1Q26 $2.59–2.63bn (2,678, +2.61%). Q1 cushion mean 2.87%, median 2.61%, sample sd 1.56pp (n 5); W1 Q1 targets (2023+, n 4) mean 2.48%, sd 1.49; W2 (2024+, n 3) mean 2.69%, sd 1.76. [rev 2] These Q1 subsamples are small subsets of W1/W2, not 14/10 observations. Extract: [datasets/feb_letter_guides_4Q20-4Q25.csv](datasets/feb_letter_guides_4Q20-4Q25.csv) | `data/processed/overnight/02_guidance_ledger.csv`; `data/raw/letters/4Q22_*`, `4Q23_*`, `4Q24_*`, `4Q25_d58192dex991.htm`; recomputed in `audits/A08-reproduce.py` | 2022-02-15 to 2026-02-12 | 2026-09-17 | yes |
| 2 | [rev 2, corrected per A08-17] Q1 guide midpoint growth on the prior-year Q1 (dollar-implied, the series this question resolves on): 1Q23 +18.5% (the preceding 4Q22 guide +20.3%), 1Q24 +13.0% (4Q23 guide +13.3%), 1Q25 +5.0% (4Q24 guide +8.9%; calendar and FX −3pts), 1Q26 +15.0% (4Q25 guide +8.6%; FX +3pts, RNPL). Dollar-implied Q1-minus-Q4 guide-growth change: −1.81, −0.28, −3.84, +6.41 (mean +0.12, sample sd 4.44pp); the rounded stated-range version rev 1 listed (−1.5, 0, −4, +6.5) has sd 4.48, not 4.3. Four of five February dollar guides also printed a numeric growth range (rev 1 said two) | same ledger; `abnb_guidance_reaction_panel.csv` nq_rev_guide_growth; `A08-reproduce.py` | 2026-02-12 | 2026-09-17 | yes |
| 3 | February Q1 guides versus the vintage-stamped pre-guide Street: 4Q21 +16.5% (CNBC unattributed), 4Q22 +5.6% (Refinitiv), 4Q23 +0.99% (LSEG), 4Q24 −2.17% (LSEG), 4Q25 +3.16% (LSEG): 4 of 5 above; W1 Q1 targets 3 of 4 (mean +1.90%); W2 2 of 3 (mean +0.66%). The Street re-anchors on the guide for the **same target quarter** with κ ≈ +0.57% (slope 0.988, r 0.993, n 18; 2023+ slope 0.960, n 14) | `data/processed/abnb_guidance_reaction_panel.csv` (guide_vs_street_pct); `data/processed/forecast_methods/L0/L0_vintage_register.csv` pre_guide rows; `data/processed/overnight/16_consensus_at_print_merged.csv`; `docs/revenue-forecast-strategy/02_proposals/M3_guidance_function_and_revision_game.md` §2.3 | 2026-09-11 | 2026-09-17 | yes |
| 4 | Kernel: revenue_q = λ_season × [⅔ GBV_{q−1} + ⅓ GBV_{q−2}]. λ_Q1 cells: 1Q23 12.80, 1Q24 13.03, 1Q25 12.33, 1Q26 12.61% (range 0.70pp, the widest of any season); kernel-lambda LIVE default (ewm) 12.66%; B3/WS06 v2 use the 2023–25 mean 12.69–12.72%. Recomputed here: [datasets/lambda_and_lagged_gbv_2023-2026.csv](datasets/lambda_and_lagged_gbv_2023-2026.csv) (1Q26: 2,678 / 21.23bn = 12.612%) | `docs/revenue-forecast-strategy/05_backtests/kernel-lambda.md` §(a); `K0_KERNEL_ENGINE_v2.md`; `data/processed/overnight/02_kpi_panel_quarterly.csv` | 2026-09-12 | 2026-09-17 | yes |
| 5 | Kernel Q1 walk-forward residuals (λ from the two prior same quarters): 1Q24 −0.55%, 1Q25 +4.81% (the 2024→2025 lead-time regime change, an over-prediction), 1Q26 +0.54%; all-season PIT last3 RMSE 2.86%, ex-COVID 2.05% with bias −0.19% (the object C01 rev 2 validated: KS p 0.63, survives W1/W2); the lag weight is not identified (bootstrap CI ≈ [0, 0.9]) but the level moves little with it once λ is re-fit | `M3_guidance_function_and_revision_game.md` §4; `kernel-lambda.md` §(c); C01 rev-2 log claim 6 / `audits/A01-audit-response.md` A01-03; `docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md` bottom line 5 | 2026-09-11 | 2026-09-17 | yes |
| 6 | [rev 2, corrected per A08-16] Pre-registered INT-20 (11 Sep, "recorded now so it cannot be fitted later"): 1Q27 guide midpoint $2,930–2,990M, +9.4 to +11.6% on $2,678M, λ̂(Q1) = 12.66% on lagGBV(1Q27) = ⅔·GBV(4Q26) + ⅓·GBV(3Q26). INT-20's phrase "the first sub-teens quarterly guide since 2023" is wrong on the ledger — the 1Q25 guide was +4–6% (mid +5%) and the 4Q24 guide implied ~+8.9% — and is not repeated here; the forecast is a deceleration from the 1Q26 guide (+15%) and print (+18%) | `docs/revenue-forecast-strategy/05_backtests/PREREG_ABNB-INT-v1.md` INT-20; `M3_guidance_function_and_revision_game.md` §5; ledger row ABNB-4Q24-revenue_yoy_pct-1Q25-128 | 2026-09-11 | 2026-09-17 | yes |
| 7 | Team GBV path (bridge v3 / WS06 v2 base): 3Q26 GBV $26,028M (nights 9.89, ADR +3.43); 4Q26 $22,987M (nights 8.12, band 8.0–8.86; ADR +4.22 incl. FX +0.15); lagged 1Q27 base $24,001M (+13.0% on 1Q26's 21,233); v2 1Q27 revenue $3,053M (+14.0%) at λ 12.72; bear 2,995 (+11.8%), bull 3,120 (+16.5%). 4Q25 GBV $20.4bn, 3Q25 $22.9bn | `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_wide.csv`, `06_comparison_quarterly.csv`; `docs/margin-build/notes/06_fy27_path_v2.md` | 2026-09-14 | 2026-09-17 | yes |
| 8 | [rev 2] C01 rev 2 (this run, after audit A01): 4Q26 revenue guide midpoint mean $3,101M, sd $97M (percentiles 2,945 / 2,980 / 3,035 / 3,100 / 3,165 / 3,225 / 3,265), P(below the LSEG-family Street $3,161M) 0.72; its validated residual structure — ε ~ N(−0.19%, 2.05%), RNPL leakage Bernoulli(0.40) × −0.84% (K1 central cell), EEA/CH single-fee step {0, +0.55, +1.11}% at 45/40/15 — is adopted here for the 1Q27 kernel (the fee migration is complete by 13 Oct 2026, so it applies in full to 1Q27 recognition). 3Q26 nights: R01 final-calibrated N(9.67, 1.70) (used by R16/B13), ADR card v3 +3.3% (band +1.9 to +4.6) | `docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/forecasts/2026-09-17-forecast.json` (rev 2), `datasets/c01_model_v2.py`; `audits/A01-audit-response.md`; `docs/q3nowcast/SYNTHESIS.md`; `docs/adrv3/SYNTHESIS.md` | 2026-09-17 | 2026-09-17 | yes |
| 9 | [rev 2] **Adopted 4Q26 nights object** (R16/B13; identical sampler to F01 v2): 0.5 × decomposition (3Q26 ~ N(9.67, 1.70) → 4Q26 = 8.1 + 0.5 × (Q3 − 9.67) + N(0, 1.4), 12% tail 5.5 ± 1.5) + 0.3 × guide route (C02 bucket vector × midpoint + N(0.9, 1.3)) + 0.2 × Street N(9.93, 1.23); mean 8.70, sd 2.05, P(≥134.0m) 0.29, P(≤131.0m) 0.27. Rev 1 used N(8.1, 1.7) + 12% tail (mean 7.8). 4Q26 ADR card +3.8 to +4.2% | F01 v2 log claim 14; `questions/risk-q4-nights-print-meets-street/datasets/r16_model.py`; `questions/q1-27-nights-guide-above-82/datasets/q4_adopted_v2_summary.csv` | 2026-09-17 | 2026-09-17 | yes |
| 10 | RNPL-aware FY27 phasing: reported 1Q27 revenue growth +9.5% (global lap) to +10.6% (NA-only lap) against the +17.9% comp, on B3's lower GBV path (B3 3Q26 GBV 25,193, ADR +0.6%); B3 itself +11.88% at w = ⅔; the Street's FY27 phased like FY26 is ~+11% every quarter | `docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md` §3; `data/processed/rnpl_short_audit/fy27_quarterly_phasing_rnpl_aware.csv`, `fy27_quarterly_phasing_b3.csv` | 2026-09-11 | 2026-09-17 | yes |
| 11 | RNPL leakage on the recognition kernel: 0.17–1.39% of the carried base (λ −0.02 to −0.17pp); 2Q26 10-Q: RNPL bookings "have experienced higher cancellation rates than historic bookings" and "the timing among GBV, revenue, and cash receipts may become less correlated"; fee-migration step on revenue +0.55% (half, adopted) to +1.11% (full) at θ = 0.83, tranche 2 through 15 Sep / 13 Oct 2026 | `05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md` §3.2; `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §1; `B2_Q4_GUIDE_EXHIBIT.md` §3.2 | 2026-09-11 | 2026-09-17 | yes |
| 12 | FX: 1Q26 guide carried "an approximate three point foreign exchange tailwind after factoring in our hedging program"; B4 spot-held 1Q27 revenue FX +0.9pp (Φ × 0.851; interval +0.2 to +1.2; ±5% dollar paths +2.9 / −1.0); under the Φ kernel FX is an output of lagged USD GBV and "must never be subtracted again" | `data/raw/letters/4Q25_d58192dex991.htm`; `05_backtests/B4_FX_EXHIBIT.md` §4; `FXSWAP_h2_bridge_kernel_fx.md` | 2026-09-12 | 2026-09-17 | yes |
| 13 | [rev 2, corrected per A08-10] LSEG 1Q27 revenue consensus $3,010.3M (n 21, sd 49.4) = +12.41% on 2,678 — **observed 13 Aug 2026** (`revenue_obs_date`), pulled 13 Sep, so 35 days old at the forecast date and predating the 2Q26 10-Q cancellation language and the September conference; **no fresher external 1Q27 observation is available** (yfinance `revenue_estimate` carries only 0q/+1q; the L0 register has no 2027Q1 row; the WS06 file is the only 1Q27 capture). It is a dated comparison, not a current verified anchor. 4Q26 $3,161.8M (n 37); FY27 $15,819M (n 44, +11.5% on LSEG's own FY26 14,190); FY27 Zacks 15,740 (n 13, 11 Sep), Alpha Vantage/Yahoo 15,758/15,790, S&P 15,770 | `data/processed/margin_build/06_fy27_path_v2/06_consensus_quarterly_2027.csv`; `data/processed/margin_build/23_final_model/23_vs_consensus.csv`; `data/processed/forecast_methods/L0/L0_vintage_register.csv` rows CU-FY2027-* | 2026-08-13 (obs) | 2026-09-13 (pull) | yes |
| 14 | 4Q25 letter, 1Q26 guide verbatim: "We expect to generate revenue of $2.59 billion to $2.63 billion, representing year-over-year growth of 14% to 16%, inclusive of an approximate three point foreign exchange tailwind after factoring in our hedging program. We expect our implied take rate in Q1 2026 to be up slightly year-over-year." (take rate then printed −0.10pt, the guide's first take-rate miss in the Q1 slot) | `data/raw/letters/4Q25_d58192dex991.htm`; ledger row ABNB-4Q25-take_rate_yoy_pts-1Q26-170 | 2026-02-12 | 2026-09-17 | no |
| 15 | 4Q24 letter, 1Q25 guide: "$2.23 billion to $2.27 billion, representing year-over-year growth of 4% to 6%, or 7% to 9% excluding the impact of FX ... Excluding the impact of the calendar factors and FX headwinds, we anticipate revenue year-over-year growth would be 10% to 12%": management prints the reported range first and explains the bridge; the reported midpoint resolves | `data/raw/letters/4Q24_d915198dex991.htm` | 2025-02-13 | 2026-09-17 | no |
| 16 | [rev 2, corrected per A08-19] Kalshi KXABNB 3Q26 nights ladder at 2026-09-17T03:18:45Z: >146m bid 0.63 / ask 0.66, >148m 0.50/0.55, >150m 0.32/0.36; lifetime `volume_fp` 50–999 per strike (>148m: 428.1, open interest 423.1), `volume_24h_fp` 0 everywhere, `updated_time` 2026-08-04 — inactive, used only as a sensitivity on GBV_3Q26; KXABNBA FY26 ladder >570m 0.63/0.71, >575m 0.37/0.41 (stale adjacent snapshot; zero weight). Polymarket public-search "Airbnb 2027" and "Airbnb guidance": no market on any 2027 Airbnb item | [sources/kalshi_KXABNB_open_20260917T031845Z.json](sources/kalshi_KXABNB_open_20260917T031845Z.json), [sources/kalshi_KXABNBA_open_20260917T031845Z.json](sources/kalshi_KXABNBA_open_20260917T031845Z.json), [sources/polymarket_search_airbnb_guidance_20260917T031845Z.json](sources/polymarket_search_airbnb_guidance_20260917T031845Z.json) | 2026-09-17 | 2026-09-17 | no |
| 17 | Web (search snippets; pages not fetched): analyst pages carry ~9–10%/yr revenue growth through 2027 (Simply Wall St) and no 1Q27 preview; the 4Q26 print date is not announced. Final 72-hour neutral check ("Airbnb latest this week"): stock −7% w/w, NYC host lawsuit; nothing bearing on the February guide | [sources/web_search_log.md](sources/web_search_log.md) | 2026-09-17 | 2026-09-17 | no |
| 18 | [rev 2] Monte Carlo (`f02_model_v2.py`): base component (adopted 4Q26 object, C01 rev-2 residual, cushion N(2.5, 1.2)) guide median $2,955M (+10.3%), print median $3,026M; pre-registration component (λ 12.66 ewm, ε 0, no leakage, no fee, cushion 2.2) median +11.1%; **final mixture 0.70/0.30: median +10.5%**, 5–95% +5.1 to +16.1, P(<10) 0.45, P(<9.4) 0.36, P(≥12) 0.34. Bridge from rev 1's +9.4: adopted 4Q26 object +0.9 (9.4 → 10.3 with the rev-1 residual); C01 rev-2 residual (fee +0.4, leakage/bias −0.2) +0.2 | [datasets/f02_v2_summary.csv](datasets/f02_v2_summary.csv), [datasets/f02_v2_percentiles.csv](datasets/f02_v2_percentiles.csv), [datasets/f02_v2_sensitivity.csv](datasets/f02_v2_sensitivity.csv) | 2026-09-17 | 2026-09-17 | yes |

Newest load-bearing source: the 13–15 Sep repo builds (claims 7, 9) and the 17 Sep C01 rev 2 / R16 / B13 logs (claims 8–9); 2–4 days old against a 147-day window. The consensus row (claim 13) is 35 days old and is carried as a dated comparison. The next real inputs are the 5 Nov print (4Q26 guide, 3Q26 GBV) and the September Inside Airbnb dumps.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md` (F01–F04 blocks and conventions); skill `SKILL.md`, `references/research-log-format.md`, `references/continuous-questions.md`; `examples/example-research-log.md`; finished logs C01, C02, C04/C09, C05–C07
2. [repo] `docs/rnpl-short-audit/00_SYNTHESIS.md` §1.3, §2, §5; `02_fy27-decomposition-rnpl-synergy.md` §3; `03_short-thesis-viability.md` (grep 1Q27); `data/processed/rnpl_short_audit/rnpl_nights_module*.csv`, `fy27_quarterly_phasing_*.csv`, `fy27_nights_lap_grid.csv`, `turns_vs_street_and_w_band.csv`
3. [repo] `research/notes/nights_quarterly.md`; `data/processed/nights_quarterly_na.csv`, `nights_quarterly_total.csv`
4. [repo] `docs/revenue-forecast-strategy/02_proposals/M3_guidance_function_and_revision_game.md` §1–5; `05_backtests/kernel-lambda.md` §(a),(c),(e); `K0_KERNEL_ENGINE_v2.md`; `B3_FY27_DECOMPOSITION.md`; `B4_FX_EXHIBIT.md` §2, §4; `PREREG_ABNB-INT-v1.md` INT-16–INT-21; `guidance-policy.md` (grep Q1)
5. [repo] `docs/margin-build/notes/06_fy27_path_v2.md`; `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_wide.csv`, `06_comparison_quarterly.csv`, `06_consensus_quarterly_2027.csv`
6. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` — all 4Q-print rows for nights, revenue, margin, S&M (claims 1–2); `data/processed/abnb_guidance_reaction_panel.csv` guide_vs_street_pct (claim 3)
7. [repo] Outlook sections extracted from `data/raw/letters/4Q22_*`, `4Q23_*`, `4Q24_*`, `4Q25_*.htm` (claims 14–15)
8. [repo, pandas] `data/processed/forecast_methods/L0/L0_vintage_register.csv` (comment='#') rows containing 2027; `data/processed/margin_build/23_final_model/23_vs_consensus.csv`
9. [repo, pandas] `data/processed/overnight/02_kpi_panel_quarterly.csv` → λ by quarter and lagged GBV (claim 4)
10. [Kalshi API] markets?status=open&series_ticker=KXABNBA and KXABNB (2026-09-17T03:18:45Z)
11. [Polymarket API] public-search?q=Airbnb 2027 ; ?q=Airbnb guidance (2026-09-17T03:18:45Z)
12. WebSearch: Airbnb news (neutral pass)
13. WebSearch: Airbnb 2027 revenue growth outlook analyst expectations
14. WebSearch: Airbnb marketing spend 2027 margin investment analysts (batch-shared)
15. WebSearch: Airbnb fourth quarter 2026 results date February 2027
16. [computed] `datasets/f02_model.py` (rev 1 base + 18 sensitivities), `datasets/f02_final_mixture.py`
17. WebSearch: Airbnb latest this week (final 72-hour neutral recency check — nothing new)
18. [rev 2, repo] `docs/pitch-forecasts/audits/A08-research-audit.md`; `audits/A08-reproduce.py` (run from the repo root, `py -3.13 -B`; output `A08-reproduce.stdout.txt`)
19. [rev 2, repo] `questions/q4-revenue-guide-vs-street/` (C01 rev 2 JSON, `c01_model_v2.py`, `audits/A01-audit-response.md` A01-03 bridge); `questions/risk-q4-nights-print-meets-street/datasets/r16_model.py`; `questions/bonus-q4-nights-print-weak/`
20. [rev 2, repo] `06_consensus_quarterly_2027.csv` `revenue_obs_date` / `pull_timestamp_local` (claim 13); `16_consensus_at_print_merged.csv` same-target join (claim 3); ledger 1Q25/4Q24 revenue rows (claim 6); `abnb_guidance_reaction_panel.csv` nq_rev_guide_growth (claim 2)
21. [rev 2, computed] `datasets/f02_model_v2.py` (final mixture + 27 sensitivities)

WebSearch calls charged to this batch: 5 in total across F01–F04 (none added in revision 2).

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, 4Q26 shareholder letter, 1Q27 revenue guide, recognition kernel λ_Q1, Reserve Now Pay Later, LSEG consensus, February 2027

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The guide lands near the Street's 1Q27 (+12.4%) because February Q1 guides have been above the pre-guide Street 4 of 5 times (claim 3) | kept as a minority inside the mixture (p75 is +12.8) | The 1Q27 Street row is an August panel (n 21) phased from FY27 and has not seen the 4Q26 guide; C01 rev 2 puts that guide below the Street with P 0.72 (−1.9% at the median). [rev 2] Whether that gap transmits to the Street's 1Q27 is an assumption, not a measured relationship (A08-11): the κ regression is same-target only; zero / half / full transmission is tabulated in §5 |
| The RNPL-aware phasing (+9.5 to +10.6% reported growth) is the central estimate | kept as the leakage branch, not as the level | That path runs on B3's GBV (3Q26 ADR +0.6%), which the adopted bridge v3 has replaced (ADR card +3.4%); its lap terms enter here through the adopted 4Q26 object and the leakage branch (0.40 × −0.84%) |
| WS06 v2's +14.0% (3,053) is what management will print | discarded as the guide, kept as the print centre's upper end | It is a print (no cushion) at λ 12.72 on the team GBV path with no RNPL leakage; the guide is the print less a 1–4.5% Q1 cushion (claim 1) |
| Management guides on an ex-FX or ex-calendar basis | discarded | The reported dollar range governs (claims 14–15); Easter 2027 (28 Mar) vs 2026 (5 Apr) moves ~1pt of Q1 revenue growth in the company's favour and is inside the kernel residual |
| The Q1 cushion is the trailing-8 all-quarter 1.86% | kept as a sensitivity (median +11.1%) | Q1 cushions run 1.0–4.5% (mean 2.87, W1 2.48); the model uses N(2.5, 1.2) |
| A 1Q25-type lead-time miss (λ −5%) recurs in 1Q27 as RNPL lengthens lead times | kept inside ε sd 2.05 plus the leakage branch and the left tail (P(<5%) 0.05) | The 2025 regime break was one event in ten Q1/Q2 cells; RNPL's lead-time lengthening is disclosed every print, which is why the leakage branch is carried at 0.40 |
| Management gives only a growth range | inside the number (converts on 2,678) | 4 of 5 February letters printed growth ranges alongside dollars; none printed growth only |
| [rev 2] Keep rev 1's own 4Q26 mixture (mean 7.8) | discarded | The run conditions every Q4-dependent question on the adopted R16/B13 object (mean 8.7); rev 1's mixture was the decomposition view alone |
| [rev 2] Omit the fee step for 1Q27 | discarded | The EEA/CH migration is complete by 13 Oct 2026 and lifts recognised revenue per unit of GBV from then on; C01 carries it for 4Q26 and there is no reason it would lapse by 1Q27. Sensitivity: no fee step −0.4pt on the median |

## 5. Independent Estimates
[rev 2] Independence label (A08-03): the three estimates are **partially dependent** — the base rate inherits C01's 4Q26 guide level; the decomposition and C01 share the kernel, GBV path and residual; the anchor is a stale panel. They are three different objects but not three independent measurements.
- base_rate_estimate: median +10.7% (sd ≈ 4.4pp) — Q1 guide growth has tracked the preceding Q4 guide growth with a dollar-implied mean change of +0.12 and sd 4.44 (claim 2); the 4Q26 guide is expected at +11.6% (C01 rev 2 median $3,100M on $2,778M) and the 1Q27 lagged-GBV base grows ~1pt more slowly than 4Q26's (13.0 vs 14.1%), so +11.6 + 0.1 − 1 ≈ +10.7
- decomposition_estimate: median +10.3%, 5–95% +4.7 to +15.9, P(<10) 0.48, P(<9.4) 0.39, P(≥12) 0.31 — Monte Carlo base component (claim 18): adopted 4Q26 object (with its 3Q26 draw), ADR_3Q26 N(3.3, 1.3), ADR_4Q26 N(4.0, 1.5), λ_Q1 12.612 × (1 + ε − leak + fee), ε ~ N(−0.19%, 2.05%), leak 0.84% w.p. 0.40, fee {0, 0.55, 1.11}% at 45/40/15, cushion N(2.5%, 1.2), $5M grid
- anchor_estimate: +12.4% raw (dated: LSEG 1Q27 mean $3,010M, n 21, observed 13 Aug 2026, pulled 13 Sep — 35 days old; no fresher external observation exists, claim 13). Transmission of the expected 4Q26 guide-vs-Street gap (C01 rev 2: −1.9% at the median) to the Street's 1Q27 is an **assumption** tested three ways: zero transmission +12.4%; half −0.95% → +11.3%; full −1.9% → +10.3%; each plus the W2 February guide-vs-Street mean (+0.66%) → +13.1 / +12.0 / +11.0%. The cross-quarter coefficient is not measured by the same-target κ regression (claim 3); the full-transmission reading (+11.0%) is the one carried as "gap-adjusted"
- anchor_value: +12.4% (LSEG 1Q27 revenue mean $3,010.3M, n 21, observed 2026-08-13, pulled 2026-09-13); gap-adjusted +11.0% under full transmission (assumption)
- final_estimate: median +10.5%; percentiles 5/10/25/50/75/90/95 = 5.1 / 6.2 / 8.3 / 10.5 / 12.8 / 14.8 / 16.1; P(<10%) 0.45, P(<9.4%) 0.36, P(≥12%) 0.34
- final_minus_anchor: −1.9pts vs the raw Street (−0.5 vs full-transmission gap-adjusted) on the median; within the distribution's own sd (3.4pp). The final is the decomposition widened by the pre-registration component (0.30 weight). Astra's independent median is +10.3% (λ 12.61 × adopted lagged GBV ÷ W1 Q1 cushion 1.0248, 4pp sd); this revision lands 0.2pt above it, the difference being the fee step (+0.4) net of the leakage/bias structure (−0.2)

## 6. Final Numbers
**Continuous: y/y growth implied by the 1Q27 revenue guide midpoint on $2,678M (final mixture, `f02_model_v2.py`).**
| Percentile | Growth, % | Guide midpoint, $M |
|---|---|---|
| 5 | 5.1 | 2,815 |
| 10 | 6.2 | 2,845 |
| 25 | 8.3 | 2,900 |
| 50 | 10.5 | 2,960 |
| 75 | 12.8 | 3,020 |
| 90 | 14.8 | 3,075 |
| 95 | 16.1 | 3,110 |
Mean +10.6%, sd 3.4pp. **P(< 10%) = 0.45; P(< 9.4%) = 0.36; P(≥ 12%) = 0.34.** Also P(< 8%) 0.23, P(< 5%) 0.05, P(≥ 14%) 0.16.
Working range [0%, 20%]: mass below 0% = 0.1% (needs a 4Q26 nights print near 3% with a 4% cushion, or a λ miss beyond 1Q25's); mass above 20% = 0.3% (needs GBV_4Q26 ≥ $24.5bn with no cushion; no precedent); P(no 1Q27 dollar guide) = 1%, carried outside the distribution (question void).
Modes: unimodal, density maximum in the +9 to +10 bin (12.6% of mass; histogram [datasets/f02_v2_hist.csv](datasets/f02_v2_hist.csv): +8–9 9.1%, +9–10 12.6%, +10–11 11.0%, +11–12 10.5%, +12–13 11.1%). The left shoulder (+4 to +8, 20% of mass) is the short-case 4Q26 tail and large-cushion combinations, not a second mode.
Floor check: none inside [+3%, +18%]; I would be genuinely surprised by a midpoint below $2,760M (+3%: below the short case's own 1Q27 *print* of $2,836M less a normal cushion) or above $3,160M (+18%: above the 1Q26 comp's own growth with a 2-point smaller FX tailwind and a 13% lagged base).
Suggested slider setup: component A centre +10.3 / sd 3.4 / weight 0.70; component B centre +11.1 / sd 3.3 / weight 0.30.
Coherence with the pre-registration: INT-20's $2,930–2,990M (+9.4 to +11.6%) spans the p40–p62 of this distribution; the median ($2,960M) sits inside it. With C01 rev 2: the 4Q26 guide median $3,100M is +11.6% on $2,778M; this 1Q27 median (+10.5%) is 1.1pt lower, matching the ~1pt slower lagged-GBV growth into 1Q27.

## 7. Sensitivity
Single-assumption reruns of `datasets/f02_model_v2.py` at the **final-mixture** level (median +10.5%; both components re-run with the changed input where it applies).
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Adopted 4Q26 object (mean 8.7) | rev-1 mixture (mean 7.8): median +9.8, P(<10) 0.53; V1 decomposition only: +9.8; Street-centred 9.93 no tail: +11.3, P(≥12) 0.42; V1 centre 7.61 (RNPL module): +10.3; short case 5.0 certain: +8.1, P(<10) 0.73 |
| 3Q26 nights N(9.67, 1.70) | Kalshi/MODL 11.0: +11.1; 8.5: +10.2 |
| Residual: ε N(−0.19, 2.05) + leakage 0.40 × −0.84 + fee 45/40/15 | rev-1 N(−0.5, 2.5) with no leakage/fee: +10.3; no fee step: +10.2; full fee certain: +11.1; no leakage branch: +10.7; leakage certain −0.84: +10.2; leakage top of K1 −1.39 certain: +9.8, P(<10) 0.54; λ 12.72 unbiased in the base: +11.3; ε sd 1.5: 5–95% +5.5 to +15.8; ε sd 3.5: +3.4 to +17.6 |
| Cushion N(2.5%, 1.2) | trailing-8 1.86%: +11.1; five-Q1 mean 2.87%: +10.3; 4.0% (1Q22/1Q24-type): +9.4, P(<10) 0.58 |
| 4Q26 ADR +4.0% | +2.5%: +9.8; +5.5%: +11.3 |
| 5 Nov 4Q26 bucket (V2 branch certain) | "low double digits": +12.8, P(≥12) 0.61; "high single digits": +10.5; "mid single / moderate": +9.0, P(<10) 0.63 |
| Joint bull (Street-centred 9.9 no tail, ADR 5.0, ε +0.5, no leakage, full fee, cushion 1.86) | median +13.5, P(<10) 0.15, P(≥12) 0.68 |
| Joint bear (V1 6.5, ADR 2.5, leakage −1.39 certain, no fee, cushion 3.0) | median +7.7, P(<10) 0.72, P(≥12) 0.15 |
| Mixture weight on the pre-registration convention 0.30 | 0: median +10.3; 1.0: +11.1 |

Pre-mortem ("it is 11 Feb 2027 and the midpoint printed +14% or more", P ≈ 0.16): (1) 4Q26 nights printed ≥ 9.5% with ADR ≥ +5% (the Street's bar) — priced at ~0.36 × the ADR draw through the adopted object; (2) the fee migration and the RNPL payment catch-up lifted Q1 recognition (λ ≥ 13.0%) — inside the fee branch (0.15 at full) and ε's upper tail; (3) management shrank the Q1 cushion below 1% to signal a strong year alongside an FY27 "low-to-mid teens" bucket — inside the cushion draw (~0.10); (4) a weak dollar (−5%) added ~2pts of FX — not modelled separately, inside ε. The opposite miss ("+6% or less", P ≈ 0.09): the short case (4Q26 nights ~5%) plus a normal cushion, or a 1Q25-type lead-time miss. Asymmetry: the memo's "sub-teens guide" sentence needs only P(<13%) ≈ 0.78; a confident sub-10 call is not supported (0.45), and revision 2 moves the centre above 10.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 2026-10-02 | September Inside Airbnb dumps; 3Q26 nights band refreshed | Re-centre the 3Q26 draw: each +0.5pt of 3Q26 nights ≈ +0.3pt on the median (⅓ of the base directly plus the 0.5 pass-through into 4Q26) |
| 2026-10-02 | Prelim memo freeze | Quote median +10.5%, P(<10%) 0.45, P(≥12%) 0.34; state that INT-20's $2,930–2,990M is the p40–p62 |
| 2026-10-13 | EEA/CH single-fee migration deadline | Confirmed complete → fee weights toward the full step (median +0.3); delayed → toward none (−0.3) |
| 2026-11-05 | 3Q26 print: 3Q26 GBV (fixes ⅓ of the 1Q27 base), 4Q26 nights bucket, 4Q26 revenue range, FX integer, any RNPL cancellation language | Re-run with GBV_3Q26 known (sd → 0) and the 4Q26 object re-set from the bucket (§7 row): "low double digits" → median ~+12.8; "high single digits" → ~+10.5; "mid single digits" → ~+9.0 |
| 2026-11-06 to 2027-01-31 | LSEG 1Q27 panel refresh after the print (n rises from 21); Kalshi 4Q26 nights ladder if listed | Re-set the anchor with a fresh `revenue_obs_date`; if the Street's 1Q27 falls below $2,950M, move the median down 0.3–0.5pt (the Street will have seen October) |
| 2027-01-20 to 2027-01-31 | Airbnb announces the 4Q26 call date (3–4 weeks ahead in prior years) | Fix the resolution date; no number change |
| 2027-02-11 (est.) | 4Q26 letter: 1Q27 revenue range, 4Q26 GBV print | Resolve on the dollar midpoint ÷ 2,678. Conditional read for the audit: at 4Q26 GBV ≤ $22.5bn the pre-print median was ≈ +9%; at $23.0bn ≈ +10.5%; at ≥ $23.6bn ≈ +12% |

## 10. Revision notes
| Change | Finding |
|---|---|
| 4Q26 nights drawn from the adopted R16/B13 object (mean 8.7) with its 3Q26 draw N(9.67, 1.70); median +9.4 → +10.3 on the rev-1 residual | run instruction (one 4Q26 object) |
| Residual re-based on C01 rev 2's validated structure (ε N(−0.19, 2.05), leakage 0.40 × −0.84%, fee 45/40/15); documentation/implementation discrepancy (1.6 vs 1.7 sd) made moot — the v2 script is the only source of the published numbers; median +10.3 → +10.5 | A08-21 (accepted), C01 rev 2 (run instruction); "what the audit missed" item 2 (fee step) |
| Final: percentiles 3.6/4.9/7.0/9.4/12.0/14.3/15.6 → **5.1/6.2/8.3/10.5/12.8/14.8/16.1**; P(<10) 0.56 → 0.45; P(<9.4) 0.48 → 0.36; P(≥12) 0.25 → 0.34; bound masses 0.3%/0.3% → 0.1%/0.3% | consequence |
| Anchor relabelled a dated comparison (observed 13 Aug, 35 days old; no fresher external observation exists); transmission of the 4Q26 gap tested at zero / half / full and labelled an assumption; κ 0.988 no longer cited for it | A08-10, A08-11 (accepted) |
| Claim 2: dollar-implied Q1-minus-Q4 series (mean +0.12, sd 4.44), rounded series sd 4.48 (not 4.3); growth-range count 4/5 (not 2/5) | A08-17 (accepted) |
| Claim 6: "first sub-teens guide since 2023" withdrawn (1Q25 guide +5%, 4Q24 guide ~+8.9%) | A08-16 (accepted) |
| Claim 16: Kalshi fields corrected (`volume_fp`, `volume_24h_fp`, `open_interest_fp`, `updated_time`); "inconsistent" → stale adjacent snapshots | A08-19 (accepted) |
| §5 relabelled partially dependent; Astra's +10.3% recorded | A08-03 (accepted) |
| §7 sensitivities now run at the mixture level, not the base component | consequence (A01-07 precedent) |

RESUME: the next agent (X01 / synthesis) should read F02 as median +10.5% (P(<10) 0.45, P(≥12) 0.34) and note it moved up 1.1pt from revision 1 for two reasons that are both run-level decisions (the adopted 4Q26 object and the C01 rev-2 residual with the fee step), not new evidence. Re-run `datasets/f02_model_v2.py` if R16/B13 or C01 change; the sampler must be kept in step with `r16_model.py`. The remaining load-bearing judgments are the cushion centre (2.5%) and the leakage probability (0.40), each worth ±0.5pt on the median.
