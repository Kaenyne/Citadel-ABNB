# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A08). Companion questions in this batch: F01 `q1-27-nights-guide-above-82`, F03 `fy27-margin-guide`, F04 `fy27-sm-share-above-219`. Reproduction: [datasets/f02_model.py](datasets/f02_model.py) (base model and sensitivities) then [datasets/f02_final_mixture.py](datasets/f02_final_mixture.py) (final mixture); numpy only, seed 20260917, 400,000 draws, ~20 s.

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
- revision: 1
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
| 1 | Every February letter since 4Q21 has carried a Q1 revenue dollar range (5 of 5): 1Q22 $1.41–1.48bn (actual 1,509, +4.43% vs mid); 1Q23 $1.75–1.82bn (1,818, +1.85%); 1Q24 $2.03–2.07bn (2,142, +4.49%); 1Q25 $2.23–2.27bn (2,272, +0.98%); 1Q26 $2.59–2.63bn (2,678, +2.61%). Q1 cushion mean 2.87%, median 2.61%, sd 1.6pp; 2023–25 mean 2.44%. Extract: [datasets/feb_letter_guides_4Q20-4Q25.csv](datasets/feb_letter_guides_4Q20-4Q25.csv) | `data/processed/overnight/02_guidance_ledger.csv`; `data/raw/letters/4Q22_*`, `4Q23_*`, `4Q24_*`, `4Q25_d58192dex991.htm` | 2022-02-15 to 2026-02-12 | 2026-09-17 | yes |
| 2 | Q1 guide midpoint growth on the prior-year Q1: 1Q23 +18.5% (4Q22 guide had been +20%), 1Q24 +13% (4Q23 guide +13%), 1Q25 +5% (4Q24 guide +9%; calendar and FX −3pts), 1Q26 +15% (4Q25 guide +8.5%; FX +3pts, RNPL). Q1 guide growth minus the preceding Q4 guide growth: −1.5, 0, −4, +6.5 (mean +0.25, sd 4.3) | same ledger; `data/raw/letters/*` | 2026-02-12 | 2026-09-17 | yes |
| 3 | February Q1 guides versus the vintage-stamped pre-guide Street: 4Q21 +16.5%, 4Q22 +5.6%, 4Q23 +0.99%, 4Q24 −2.17%, 4Q25 +3.16% (4 of 5 above; LSEG era 2 of 3 above, mean +0.66%). The Street re-anchors on the guide with κ ≈ +0.52% (slope 0.988) | `data/processed/abnb_guidance_reaction_panel.csv` (guide_vs_street_pct); `docs/revenue-forecast-strategy/02_proposals/M3_guidance_function_and_revision_game.md` §2.3 | 2026-09-11 | 2026-09-17 | yes |
| 4 | Kernel: revenue_q = λ_season × [⅔ GBV_{q−1} + ⅓ GBV_{q−2}]. λ_Q1 cells: 1Q23 12.80, 1Q24 13.03, 1Q25 12.33, 1Q26 12.61% (range 0.70pp, the widest of any season); kernel-lambda LIVE default (ewm) 12.66%; B3/WS06 v2 use the 2023–25 mean 12.69–12.72%. Recomputed here: [datasets/lambda_and_lagged_gbv_2023-2026.csv](datasets/lambda_and_lagged_gbv_2023-2026.csv) (1Q26: 2,678 / 21.23bn = 12.612%) | `docs/revenue-forecast-strategy/05_backtests/kernel-lambda.md` §(a); `K0_KERNEL_ENGINE_v2.md`; `data/processed/overnight/02_kpi_panel_quarterly.csv` | 2026-09-12 | 2026-09-17 | yes |
| 5 | Kernel Q1 walk-forward residuals (λ from the two prior same quarters): 1Q24 −0.55%, 1Q25 +4.81% (the 2024→2025 lead-time regime change, an over-prediction), 1Q26 +0.54%; all-season PIT last3 RMSE 2.86%, ex-COVID 2.05%; the lag weight is not identified (bootstrap CI ≈ [0, 0.9]) but the level moves little with it once λ is re-fit | `M3_guidance_function_and_revision_game.md` §4; `kernel-lambda.md` §(c); `docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md` bottom line 5 | 2026-09-11 | 2026-09-17 | yes |
| 6 | Pre-registered INT-20 (11 Sep, "recorded now so it cannot be fitted later"): 1Q27 guide midpoint $2,930–2,990M, +9.4 to +11.6% on $2,678M, λ̂(Q1) = 12.66% on lagGBV(1Q27) = ⅔·GBV(4Q26) + ⅓·GBV(3Q26); "the first sub-teens quarterly guide since 2023" | `docs/revenue-forecast-strategy/05_backtests/PREREG_ABNB-INT-v1.md` INT-20; `M3_guidance_function_and_revision_game.md` §5 | 2026-09-11 | 2026-09-17 | yes |
| 7 | Team GBV path (bridge v3 / WS06 v2 base): 3Q26 GBV $26,028M (nights 9.89, ADR +3.43); 4Q26 $22,987M (nights 8.12, band 8.0–8.86; ADR +4.22 incl. FX +0.15); lagged 1Q27 base $24,001M (+13.0% on 1Q26's 21,233); v2 1Q27 revenue $3,053M (+14.0%) at λ 12.72; bear 2,995 (+11.8%), bull 3,120 (+16.5%). 4Q25 GBV $20.4bn, 3Q25 $22.9bn | `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_wide.csv`, `06_comparison_quarterly.csv`; `docs/margin-build/notes/06_fy27_path_v2.md` | 2026-09-14 | 2026-09-17 | yes |
| 8 | Team 3Q26 nights nowcast +9.5% (band 8.5–10.0; walk-forward RMSE 1.48pp), ADR card v3 +3.3% (band +1.9 to +4.6): GBV_3Q26 ≈ N(25,884, 499) as used in C01 (`c01_model.py`); C01 puts the 4Q26 revenue guide midpoint at median $3,100M (+11.6%), P(below Street) 0.75 | `docs/q3nowcast/SYNTHESIS.md`; `docs/adrv3/SYNTHESIS.md`; `docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/research-log.md` §5–6 | 2026-09-17 | 2026-09-17 | yes |
| 9 | 4Q26 nights views: team 8.1 (band 8.0–8.9), RNPL module 7.61 (band 6.6–8.4), Bloomberg MODL 4Q26 134.0m (+9.9%, n 28, 12 Sep screenshot), short case 5.0; C02 puts "high single digits" at 0.39 as the modal 4Q26 bucket. 4Q26 ADR card +3.8 to +4.2% | `data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv`; `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`; `data/processed/margin_build/40_line_build/40_short_case_revenue_path.csv`; C02 log | 2026-09-15 | 2026-09-17 | yes |
| 10 | RNPL-aware FY27 phasing: reported 1Q27 revenue growth +9.5% (global lap) to +10.6% (NA-only lap) against the +17.9% comp, on B3's lower GBV path (B3 3Q26 GBV 25,193, ADR +0.6%); B3 itself +11.88% at w = ⅔; the Street's FY27 phased like FY26 is ~+11% every quarter | `docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md` §3; `data/processed/rnpl_short_audit/fy27_quarterly_phasing_rnpl_aware.csv`, `fy27_quarterly_phasing_b3.csv` | 2026-09-11 | 2026-09-17 | yes |
| 11 | RNPL leakage on the recognition kernel: 0.17–1.39% of the carried base (λ −0.02 to −0.17pp); 2Q26 10-Q: RNPL bookings "have experienced higher cancellation rates than historic bookings" and "the timing among GBV, revenue, and cash receipts may become less correlated"; fee-migration step on revenue +0.55% (half, adopted) to +1.11% (full) at θ = 0.83, tranche 2 through 15 Sep / 13 Oct 2026 | `05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md` §3.2; `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §1; `B2_Q4_GUIDE_EXHIBIT.md` §3.2 | 2026-09-11 | 2026-09-17 | yes |
| 12 | FX: 1Q26 guide carried "an approximate three point foreign exchange tailwind after factoring in our hedging program"; B4 spot-held 1Q27 revenue FX +0.9pp (Φ × 0.851; interval +0.2 to +1.2; ±5% dollar paths +2.9 / −1.0); under the Φ kernel FX is an output of lagged USD GBV and "must never be subtracted again" | `data/raw/letters/4Q25_d58192dex991.htm`; `05_backtests/B4_FX_EXHIBIT.md` §4; `FXSWAP_h2_bridge_kernel_fx.md` | 2026-09-12 | 2026-09-17 | yes |
| 13 | LSEG 1Q27 revenue consensus $3,010.3M (n 21, sd 49.4, obs 13 Aug 2026, pulled 13 Sep) = +12.41% on 2,678; 4Q26 $3,161.8M (n 37); FY27 $15,819M (n 44, +11.5% on LSEG's own FY26 14,190). Register: FY27 Zacks 15,740 (n 13, 11 Sep), Alpha Vantage/Yahoo 15,758/15,790 (one LSEG-family panel), S&P 15,770. No vendor-stamped 1Q27 row exists in the register; the WS06 file is the only 1Q27 capture | `data/processed/margin_build/06_fy27_path_v2/06_consensus_quarterly_2027.csv`; `data/processed/margin_build/23_final_model/23_vs_consensus.csv`; `data/processed/forecast_methods/L0/L0_vintage_register.csv` rows CU-FY2027-* | 2026-09-13 | 2026-09-17 | yes |
| 14 | 4Q25 letter, 1Q26 guide verbatim: "We expect to generate revenue of $2.59 billion to $2.63 billion, representing year-over-year growth of 14% to 16%, inclusive of an approximate three point foreign exchange tailwind after factoring in our hedging program. We expect our implied take rate in Q1 2026 to be up slightly year-over-year." (take rate then printed −0.10pt, the guide's first take-rate miss in the Q1 slot) | `data/raw/letters/4Q25_d58192dex991.htm`; ledger row ABNB-4Q25-take_rate_yoy_pts-1Q26-170 | 2026-02-12 | 2026-09-17 | no |
| 15 | 4Q24 letter, 1Q25 guide: "$2.23 billion to $2.27 billion, representing year-over-year growth of 4% to 6%, or 7% to 9% excluding the impact of FX ... Excluding the impact of the calendar factors and FX headwinds, we anticipate revenue year-over-year growth would be 10% to 12%": management prints the reported range first and explains the bridge; the reported midpoint resolves | `data/raw/letters/4Q24_d915198dex991.htm` | 2025-02-13 | 2026-09-17 | no |
| 16 | Kalshi KXABNB 3Q26 nights ladder at 2026-09-17T03:18:45Z: >146m bid 0.63 / ask 0.66, >148m 0.50/0.55, >150m 0.32/0.36 (volume and open interest null; zero weight as a price, used only as a sensitivity on GBV_3Q26); KXABNBA FY26 ladder >570m 0.63/0.71, >575m 0.37/0.41 (mutually inconsistent with the Q3 ladder per C02; zero weight). Polymarket public-search "Airbnb 2027" and "Airbnb guidance": no market on any 2027 Airbnb item | [sources/kalshi_KXABNB_open_20260917T031845Z.json](sources/kalshi_KXABNB_open_20260917T031845Z.json), [sources/kalshi_KXABNBA_open_20260917T031845Z.json](sources/kalshi_KXABNBA_open_20260917T031845Z.json), [sources/polymarket_search_airbnb_guidance_20260917T031845Z.json](sources/polymarket_search_airbnb_guidance_20260917T031845Z.json) | 2026-09-17 | 2026-09-17 | no |
| 17 | Web (search snippets; pages not fetched): analyst pages carry ~9–10%/yr revenue growth through 2027 (Simply Wall St) and no 1Q27 preview; the 4Q26 print date is not announced. Final 72-hour neutral check ("Airbnb latest this week"): stock −7% w/w, NYC host lawsuit; nothing bearing on the February guide | [sources/web_search_log.md](sources/web_search_log.md) | 2026-09-17 | 2026-09-17 | no |
| 18 | Monte Carlo (this log): base run guide median $2,920M (+9.0%), print median $2,995M, 5–95% +3.2 to +15.2%, P(<10) 0.60, P(<9.4) 0.52, P(≥12) 0.22; final mixture (0.70 base + 0.30 pre-registration convention λ 12.66 / unbiased / cushion 2.2) median +9.4%, P(<10) 0.56, P(<9.4) 0.48, P(≥12) 0.25 | [datasets/f02_summary.csv](datasets/f02_summary.csv), [datasets/f02_final_mixture.csv](datasets/f02_final_mixture.csv), [datasets/f02_sensitivity.csv](datasets/f02_sensitivity.csv) | 2026-09-17 | 2026-09-17 | yes |

Newest load-bearing source: the 13–15 Sep repo builds (claims 7, 9) and the 17 Sep C01/C02 logs (claim 8); 2–4 days old against a 147-day window. Nothing web-side is newer or bears on the number; the next real inputs are the 5 Nov print (4Q26 guide, 3Q26 GBV) and the September Inside Airbnb dumps.

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
16. [computed] `datasets/f02_model.py` (base + 18 sensitivities), `datasets/f02_final_mixture.py`
17. WebSearch: Airbnb latest this week (final 72-hour neutral recency check — nothing new)

WebSearch calls charged to this batch: 5 in total across F01–F04 (each question's share ≤ 5).

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, 4Q26 shareholder letter, 1Q27 revenue guide, recognition kernel λ_Q1, Reserve Now Pay Later, LSEG consensus, February 2027

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The guide lands near the Street's 1Q27 (+12.4%) because February Q1 guides have been above the pre-guide Street 4 of 5 times (claim 3) | kept as a minority inside the mixture (upper quartile) | The 1Q27 Street row is an August panel (n 21) phased from FY27 and has not seen the 4Q26 guide; C01 puts that guide below the Street with P 0.75 (−1.9% at the median), and the Street re-anchors on guides (κ slope ≈ 1). The two above-Street February guides in the LSEG era (4Q23 +1.0%, 4Q25 +3.2%) came with FX tailwinds of +1 to +3pts and 16–19% GBV growth; the 1Q27 lagged base grows ~13% with FX ≈ +0.9 |
| The RNPL-aware phasing (+9.5 to +10.6% reported growth) is the central estimate | kept as the tilt on λ, not as the level | That path runs on B3's GBV (3Q26 ADR +0.6%), which the adopted bridge v3 has replaced (ADR card +3.4%); its lap terms enter here through the 4Q26 nights distribution (team 8.1 / RNPL 7.6) and the −0.5% λ tilt (leakage, lead-time lengthening) |
| WS06 v2's +14.0% (3,053) is what management will print | discarded as the guide, kept as the print centre's upper end | It is a print (no cushion) at λ 12.72 on the team GBV path with no RNPL leakage; the guide is the print less a 1–4.5% Q1 cushion (claim 1) |
| Management guides on an ex-FX or ex-calendar basis | discarded | The reported dollar range governs (claims 14–15); Easter 2027 (28 Mar) vs 2026 (5 Apr) moves ~1pt of Q1 revenue growth in the company's favour and is inside the kernel residual |
| The Q1 cushion is the trailing-8 all-quarter 1.86% | kept as a sensitivity (median +9.8%) | Q1 cushions run 1.0–4.5% (mean 2.87); the model uses N(2.5, 1.2) |
| A 1Q25-type lead-time miss (λ −5%) recurs in 1Q27 as RNPL lengthens lead times | kept inside ε sd 2.5% and the left tail (P(<5%) 0.11) | The 2025 regime break was one event in ten Q1/Q2 cells; RNPL's lead-time lengthening is disclosed every print, which is why ε is tilted −0.5% rather than 0 |
| Management gives only a growth range | inside the number (converts on 2,678) | 2 of 5 February letters printed growth ranges alongside dollars; none printed growth only |

## 5. Independent Estimates
- base_rate_estimate: median +10.6% (sd ≈ 4pp) — Q1 guide growth has tracked the preceding Q4 guide growth with mean +0.25 and sd 4.3 (claim 2); the 4Q26 guide is expected at +11.6% (C01 median) and the 1Q27 lagged-GBV base grows ~1pt more slowly than 4Q26's (13.0 vs 14.1%), so +11.6 − 1 = +10.6
- decomposition_estimate: median +9.0%, 5–95% +3.2 to +15.2%, P(<10) 0.60, P(<9.4) 0.52, P(≥12) 0.22 — Monte Carlo: GBV_3Q26 from the team band, GBV_4Q26 from nights N(8.1, 1.6) with a 12% short-case tail (5.5 ± 1.5) and ADR N(4.0, 1.5), λ_Q1 12.61 × (1 + N(−0.5%, 2.5%)), cushion N(2.5%, 1.2), $5M grid (claim 18)
- anchor_estimate: +11.0% gap-adjusted (raw +12.4%) — LSEG 1Q27 mean $3,010M (n 21, 13 Aug) less the expected re-anchoring after a below-Street 4Q26 guide (−1.9% at the C01 median) plus the LSEG-era February guide-vs-Street mean (+0.66%) → ≈ $2,973M; no tradable market exists (claim 16)
- anchor_value: +12.4% (LSEG 1Q27 revenue mean $3,010.3M, n 21, observed 2026-08-13, pulled 2026-09-13); gap-adjusted +11.0%
- final_estimate: median +9.4%; percentiles 5/10/25/50/75/90/95 = 3.6 / 4.9 / 7.0 / 9.4 / 12.0 / 14.3 / 15.6; P(<10%) 0.56, P(<9.4%) 0.48, P(≥12%) 0.25
- final_minus_anchor: −3.0pts vs the raw Street (−1.6 vs gap-adjusted) on the median; the estimates disagree by 2pts (decomposition vs base rate) to 3.4pts (vs raw anchor), less than the distribution's own sd (3.6pp), so the disagreement is inside the noise and the final is the decomposition widened by the base-rate/anchor component (30% weight on the pre-registration convention). Independence: the base rate uses only the ledger's guide sequence; the decomposition uses GBV, λ and the cushion; the anchor is the Street's stale panel — three different objects that land within one sd of each other

## 6. Final Numbers
**Continuous: y/y growth implied by the 1Q27 revenue guide midpoint on $2,678M (final mixture).**
| Percentile | Growth, % | Guide midpoint, $M |
|---|---|---|
| 5 | 3.6 | 2,775 |
| 10 | 4.9 | 2,810 |
| 25 | 7.0 | 2,865 |
| 50 | 9.4 | 2,930 |
| 75 | 12.0 | 3,000 |
| 90 | 14.3 | 3,060 |
| 95 | 15.6 | 3,095 |
Mean +9.5%, sd 3.6pp. **P(< 10%) = 0.56; P(< 9.4%) = 0.48; P(≥ 12%) = 0.25.** Also P(< 8%) 0.34, P(< 5%) 0.11, P(≥ 14%) 0.11.
Working range [0%, 20%]: mass below 0% = 0.3% (needs a 4Q26 nights print near 3% with a 4% cushion, or a λ miss beyond 1Q25's); mass above 20% = 0.3% (needs GBV_4Q26 ≥ $24.5bn with no cushion; no precedent); P(no 1Q27 dollar guide) = 1%, carried outside the distribution (question void).
Modes: unimodal, density maximum in the +8 to +11 bin (histogram [datasets/f02_final_hist.csv](datasets/f02_final_hist.csv): 10.4% of mass in each of the +8–9, +9–10 and +10–11 bins). The left shoulder (+3 to +7, 24% of mass) is the short-case 4Q26 print and large-cushion combinations, not a second mode.
Floor check: none inside [+2%, +17%]; I would be genuinely surprised by a midpoint below $2,730M (+2%: below the short case's own 1Q27 *print* of $2,836M less a normal cushion) or above $3,130M (+17%: above the 1Q26 comp's own growth with a 2-point smaller FX tailwind and a 13% lagged base).
Suggested slider setup: component A centre +9.0 / sd 3.6 / weight 0.70; component B centre +10.2 / sd 3.6 / weight 0.30.
Coherence with the pre-registration: INT-20's $2,930–2,990M (+9.4 to +11.6%) spans the p50–p70 of this distribution; the median coincides with INT-20's low end because this run carries the RNPL λ tilt and the short-case tail that INT-20 did not.

## 7. Sensitivity
Single-assumption reruns of `datasets/f02_model.py` from the base run (median +9.0%; the final mixture sits ≈ +0.4 above each row).
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| 4Q26 nights centred 8.1 with a 12% short tail (mean 7.8) | RNPL module 7.6: median +8.9, P(<10) 0.64; Street bar 9.9 with no tail: +10.5, P(<10) 0.45, P(≥12) 0.34; short case 5.0 certain: +7.4, P(<10) 0.79 |
| GBV_3Q26 on the team band (nights 9.5) | Kalshi/MODL nights 11.0: +9.6; nights 8.5: +8.7 |
| λ_Q1 = 12.61 × (1 + N(−0.5%, 2.5%)) | ewm 12.66 unbiased: +10.2, P(≥12) 0.31; 2023–25 mean 12.72 unbiased: +10.5, P(<10) 0.44; leakage top −1.4%: +8.1, P(<10) 0.71; ε sd 1.5: 5–95% +4.6 to +13.9; ε sd 3.5: +1.8 to +16.7 |
| Cushion N(2.5%, 1.2) | trailing-8 1.86%: +9.8; five-Q1 mean 2.87%: +8.7; 4.0% (1Q22/1Q24-type): +7.5, P(<10) 0.76 |
| 4Q26 ADR +4.0% | +2.5%: +8.1; +5.5%: +10.2 |
| Joint bull (nights 9.9, ADR 5.0, ε +0.5, cushion 1.86) | median +13.0, P(<10) 0.21, P(≥12) 0.62 |
| Joint bear (nights 6.5, ADR 2.5, ε −1.4, cushion 3.0) | median +5.7, P(<10) 0.89, P(≥12) 0.04 |
| Mixture weight on the pre-registration convention 0.30 | 0: median +9.0; 0.60: +9.8 |

Pre-mortem ("it is 11 Feb 2027 and the midpoint printed +13% or more", P ≈ 0.20): (1) 4Q26 nights printed ≥ 9.5% with ADR ≥ +5% (the Street's bar, not the team's) — priced at ~0.17 through the nights/ADR draws; (2) the fee migration and the RNPL payment catch-up lifted Q1 recognition (λ ≥ 13.0%) — inside ε's upper tail (~0.10); (3) management shrank the Q1 cushion below 1% to signal a strong year alongside an FY27 "low-to-mid teens" bucket — inside the cushion draw (~0.10); (4) a weak dollar (−5%) added ~2pts of FX — not modelled separately, inside ε. The opposite miss ("+6% or less", P ≈ 0.17): the short case (4Q26 nights ~5%) plus a normal cushion, or a 1Q25-type lead-time miss. Asymmetry: the memo's "first sub-teens guide" sentence needs only P(<12%) ≈ 0.75; a confident sub-10 call is not supported (0.56).

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 2026-10-02 | September Inside Airbnb dumps; 3Q26 nights band refreshed | Re-centre GBV_3Q26: each +0.5pt of 3Q26 nights ≈ +0.2pt on the median |
| 2026-10-02 | Prelim memo freeze | Quote median +9.4%, P(<10%) 0.56, P(≥12%) 0.25; state that INT-20's $2,930–2,990M is the p50–p70 |
| 2026-11-05 | 3Q26 print: 3Q26 GBV (fixes ⅓ of the 1Q27 base), 4Q26 nights bucket, 4Q26 revenue range, FX integer, any RNPL cancellation language | Re-run with GBV_3Q26 known (sd → 0) and the 4Q26 nights centre re-set from the bucket: "high single digits" → centre 8.0; "low double digits" → 10.0 (median +10.5); "mid single digits" → 6.0 (median +7.9) |
| 2026-11-06 to 2027-01-31 | LSEG 1Q27 panel refresh after the print (n rises from 21); Kalshi 4Q26 nights ladder if listed | Re-set the anchor; if the Street's 1Q27 falls below $2,950M, move the median down 0.3–0.5pt (the Street will have seen October) |
| 2027-01-20 to 2027-01-31 | Airbnb announces the 4Q26 call date (3–4 weeks ahead in prior years) | Fix the resolution date; no number change |
| 2027-02-11 (est.) | 4Q26 letter: 1Q27 revenue range, 4Q26 GBV print | Resolve on the dollar midpoint ÷ 2,678. Conditional read for the audit: at 4Q26 GBV ≤ $22.5bn the pre-print median was ≈ +8%; at $23.0bn ≈ +9.5%; at ≥ $23.6bn ≈ +11% |

RESUME: the next agent (audit response) should re-run `datasets/f02_model.py` then `datasets/f02_final_mixture.py` (deterministic, ~20 s), check claim 1 (Q1 cushions) and claim 4 (λ_Q1 cells) against the raw files, and attack the three load-bearing choices: the λ tilt (−0.5% vs 0), the 4Q26 nights mixture (mean 7.8 vs the Street's 9.9) and the cushion centre (2.5% vs 1.86%). All three are tabulated in §7; the median moves between +7.4 and +10.5 across them.
