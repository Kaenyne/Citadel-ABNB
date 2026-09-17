# RESEARCH LOG

## 0. Metadata
- question_name: q3-revenue-fx-integer
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § C08)
- type: multiple_choice
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2026-11-04
- resolution_date: 2026-11-05
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
What year-over-year FX contribution to 3Q26 revenue growth will Airbnb state at the 5 Nov print?
### Resolution Criteria
(a) ≥ +3 points (e.g., "approximately 3 points", "3 to 4 points"); (b) +2 points; (c) ≤ +1 point (incl. "minimal", "roughly neutral"); (d) not stated.
### Fine Print
Resolves on the letter's stated points or the difference between reported and ex-FX revenue growth if both are printed (rounded to the nearest integer). Resolution date 5 Nov 2026.

Conventions adopted for ambiguities (registry conventions apply: letter governs over the call; "not stated" resolves only if neither the letter nor the call gives an FX contribution or an ex-FX growth rate): (1) if the letter's prose states the points ("approximately two percentage point headwind"), the prose integer governs; otherwise the integer is round(reported growth) − round(ex-FX growth) from the letter's Key Financial Measures box, which has printed both rates as integers in every letter since 4Q20 (claim 1); (2) a stated range maps by its midpoint, with a half-integer going to the higher bucket ("3 to 4" → a; "2 to 3" → 2.5 → a; "1 to 2" → b); (3) the basis is whatever the letter states — since 3Q25 every stated point has been "after factoring in our hedging program", and the ex-FX growth in the box is on the same after-hedge basis (the hedge reclassification sits inside reported revenue; claim 9); (4) a negative integer resolves (c); (5) if the letter prints only reported growth and a dollar FX effect, convert on 3Q25 revenue $4,095M and round.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Every shareholder letter since 4Q20 (23 of 23) prints revenue growth and revenue growth "ex-FX" as integers in the Key Financial Measures box; the letter-derived integer series (reported minus ex-FX) is: 1Q23 −4, 2Q23 −1, 3Q23 +4, 4Q23 +3, 1Q24 0, 2Q24 0, 3Q24 0, 4Q24 0, 1Q25 −2, 2Q25 0, 3Q25 0, 4Q25 +1, 1Q26 +3, 2Q26 +4 (six exact zeros in the 14-quarter sample) | `data/raw/letters/*.htm` (grep of every letter, this run); `data/processed/abnb_driver_history_quarterly.csv` col `fx_pts`; `data/processed/forecast_methods/fx_lag_v2/04_analysis_panel.csv` col `stated_revenue_fx_pp` | 2021-02-25 to 2026-08-06 | 2026-09-17 | yes |
| 2 | 2Q26 letter, Outlook, verbatim: "We expect to generate revenue of $4.69 billion to $4.77 billion, representing year-over-year growth of 15% to 17%, inclusive of an approximate three percentage point FX tailwind after factoring in our hedging program." | `data/raw/letters/2Q26_d70413dex991.htm` | 2026-08-06 | 2026-09-17 | yes |
| 3 | Management's guided FX language versus the printed integer, ten guide/print pairs 3Q23–2Q26 (recomputed this run, `datasets/c08_guide_track_record.csv`): guided-as-number 2.5/2.0/−0.5/−0.5/0.5/−3.0/0.0/0.5/3.0/3.0 vs printed 4/3/0/0/0/−2/0/1/3/4; error (printed − guided) mean +0.55, sd 0.60; printed ≥ guided in 9 of 10; never printed more than 0.5 below the guided figure; the two numeric "approximately three" guides (4Q25 letter for 1Q26, 1Q26 letter for 2Q26) printed 3 and 4 | `data/raw/letters/2Q23_…`, `3Q23_…`, `1Q24_…`, `2Q24_…`, `3Q24_…`, `4Q24_…`, `2Q25_…`, `3Q25_…`, `4Q25_…`, `1Q26_…` (Outlook sections, verbatim quotes in the CSV) | 2023-08-03 to 2026-05-07 | 2026-09-17 | yes |
| 4 | B4 FX exhibit, pre-registered 5 Nov decision rule: contemporaneous ×0.56 → 0; free fit stated → +1; Φ ×0.653 / Φ ×0.56 → +2; Φ ×0.851 and management's guide → +3. "A printed 3Q26 revenue-FX of +3 or more supports the lag-loaded kernel … 0 or +1 supports the free fit … +2 is the ambiguous middle." On data to 4 Sep: free fit +1.3 (80% band −0.1 to +2.6), Φ ×0.851 +2.9 (+1.6 to +4.2), Φ ×0.653 +2.2, contemporaneous +0.3 | `docs/revenue-forecast-strategy/05_backtests/B4_FX_EXHIBIT.md` §3, §3.2; `data/processed/forecast_methods/fx_lag_v2/21_live_3q26_three_numbers.csv` | 2026-09-11 | 2026-09-17 | yes |
| 5 | fx-lag Object A (n 14, interval likelihood on letter-rounded points): effective lag 0.50 quarters on the stated series (95% CS 0.00–1.19), Φ (0, ⅔, ⅓) rejected in-sample (LR 10.2, p 0.017 stated; 16.8, p 0.0008 gross); but point-in-time at guide dates H2 (Φ on disclosed ADR-FX, one scale parameter) is the best forecaster: W1/W2 RMSE 0.99pp, bias +0.10, interval RMSE 0.58, n 10 (covers 10 of 14 W1 quarters, not quotable as a W1 winner); free fit PIT RMSE 1.59–1.82; contemporaneous 1.88–1.97 | `05_backtests/fx-lag.md` §3, §6.2; `data/processed/forecast_methods/fx_lag_v2/09c_pit_window_scores.csv` | 2026-09-11 | 2026-09-17 | yes |
| 6 | The registered H2 spec's own PIT point for 3Q26 at the 6 Aug guide date is +1.85 (coefficient 0.7313 on ⅔·1.3 + ⅓·5.0 = 2.53), sigma 1.71; H2b (Φ on the basket) +3.00 (coefficient 0.8807). H2's PIT record on the last four prints: 3Q25 0.44 vs 0; 4Q25 1.68 vs 1; 1Q26 1.92 vs 3; 2Q26 3.02 vs 4 (under-forecast the last two by ~1pp) | `data/processed/forecast_methods/fx_lag_v2/09b_pit_expanding_window_forecasts.csv` rows 62–93 | 2026-09-11 | 2026-09-17 | yes |
| 7 | Revenue-weighted currency basket rebuilt this run on FRED through 2026-09-11 (H.10 of 14 Sep; five business days beyond the programme's 4 Sep vintage) with the fx_lag_v2 judgement currency weights and trailing-4 filed regional revenue shares (NA 0.418 / EMEA 0.385 / LatAm 0.101 / APAC 0.096): 1Q26 +5.675, 2Q26 +2.266 (both reproduce the published 5.673 / 2.266); 3Q26 QTD +0.483 (published to 4 Sep: +0.426), spot held to 30 Sep +0.600; regional 3Q26: NA +0.07, EMEA −0.87, LatAm +6.73, APAC +2.39. Φ driver ⅔·2.266 + ⅓·5.675 = 3.40 | `datasets/c08_basket_rebuild.csv`; `sources/fred_fx_daily_20260917T030938Z.csv`, `fred_fetch_manifest_20260917T030938Z.csv`; `data/processed/forecast_methods/fx_lag_v2/01b_basket_weights_used.csv`, `02_basket_quarterly.csv` | 2026-09-11 (FRED) / 2026-09-11 (weights) | 2026-09-17 | yes |
| 8 | Spot on 11 Sep vs 4 Sep: EUR 1.1604 (1.1618), GBP 1.3524 (1.3521), BRL 0.1960 (0.1953), MXN 0.05893 (0.05930), JPY 0.006510 (0.006406), AUD 0.7174 (0.7209), broad USD index 118.21 (118.07). The dollar is essentially unchanged since the 6 Aug guide; the QTD basket has drifted up (+0.36 to 28 Aug, +0.43 to 4 Sep, +0.48 to 11 Sep) | `sources/fred_fetch_manifest_20260917T030938Z.csv`; `data/processed/forecast_methods/fx_lag_v2/fx_fetch_manifest_2026-09-11.csv` | 2026-09-11 | 2026-09-17 | no |
| 9 | Hedge-once rule: the letter-stated points are already after hedges; hedges subtracted −1.13 / −0.93 / −0.66 / −0.61pp in 3Q25–2Q26 (designated notional $2.6bn → $3.4bn); forward expected reclassification implies about −0.21pp in 3Q26. Gross ex-hedge series: 3Q25 +1.13, 4Q25 +1.93, 1Q26 +3.66, 2Q26 +4.61 | `05_backtests/B4_FX_EXHIBIT.md` §3.1; `data/processed/forecast_methods/fx_lag_v2/22_hedge_gross_vs_after.csv`; `data/processed/overnight/28_fx_hedge_disclosures.csv` | 2026-09-11 | 2026-09-17 | yes |
| 10 | Disclosed ADR-FX points: 1Q26 +5.0, 2Q26 +1.3 (letters); revenue FX printed +3 and +4 in the same quarters — the 2Q26 pair (ADR-FX +1.3, revenue-FX +4) is the cleanest single observation that revenue FX carries booking-date (lagged) currency: ⅔·5.0 + ⅓·2.9 = 4.3 | `data/processed/overnight/28_fx_hedge_disclosures.csv` cols `stated_adr_fx_pp`, `stated_revenue_fx_pp`; `data/raw/letters/1Q26_…`, `2Q26_…` | 2026-05-07 / 2026-08-06 | 2026-09-17 | yes |
| 11 | Overnight2 B refreshed lagged EUR/broad-USD fit (WS05 family): 3Q26 revenue FX +2.19 gross, +1.98 after hedge; "management's number is about 1 pp above the fit, within the fit's own stated ±0.8pp spread plus rounding"; about 86% of the driver observed at 4 Sep | `research/notes/overnight2/B_fx-relative-strength-geographic-mix.md` §1.9, table 2.4 | 2026-09-11 | 2026-09-17 | yes |
| 12 | FXSWAP: bridge v2/v3 carry 3Q26 revenue FX at management's stated ~3 after hedging ("which the kernel reproduces (+2.9)"); the 5 Nov printed integer is the pre-registered arbiter between the +0.15 and +1.0 4Q26 readings | `05_backtests/FXSWAP_h2_bridge_kernel_fx.md` §1, RESUME | 2026-09-12 | 2026-09-17 | no |
| 13 | Letter-rounding kernel: both growth rates are printed as integers, so a true contribution f maps to integer k with probability max(0, 1 − |f − k|) when the ex-FX growth's fractional part is uniform (verified by simulation in `datasets/c08_model.py`: f = 2.9 → P(3) 0.90, P(2) 0.10 before model error). 40% of the apparent revenue-FX model error in fx-lag is rounding (interval RMSE 0.56 vs point RMSE 0.93) | `05_backtests/fx-lag.md` §2; `datasets/c08_model.py` | 2026-09-11 / 2026-09-17 | 2026-09-17 | yes |
| 14 | Monte Carlo (this log, `datasets/c08_integer_mc.csv`, `c08_sensitivity.csv`): component integer probabilities (P≥3 / P=2 / P≤1) — management ~3 ± 0.6: 0.772 / 0.216 / 0.012; Φ ×0.851 (2.9 ± 0.6): 0.722 / 0.260 / 0.018; middle cluster (2.05 ± 0.7): 0.277 / 0.487 / 0.236; free fit (1.26 ± 0.7): 0.051 / 0.325 / 0.625; contemporaneous (0.13 ± 0.7): 0.001 / 0.034 / 0.966. Mixture at weights 0.38 / 0.20 / 0.27 / 0.12 / 0.03 and P(not stated) 0.02: 0.508 / 0.300 / 0.172 / 0.020. Model-only mixture (no management component) 0.356 / 0.354 / 0.270 | computed; `datasets/c08_model.py` (seed 20260917) | 2026-09-17 | 2026-09-17 | yes |
| 15 | No Polymarket or Kalshi market prices this quantity (searches "airbnb", "Airbnb Q3", "Airbnb take rate", "Airbnb revenue" at 2026-09-17T03:10:10Z; Kalshi KXABNB is a Q3 nights ladder, KXABNBA an FY nights ladder) | `sources/web_queries_2026-09-17.md`; `../q3-take-rate-above-1810/sources/polymarket_search_*_20260917T031010Z.json`, `kalshi_markets_KXABNB_open_20260917T031010Z.json` | 2026-09-17 | 2026-09-17 | no |
| 16 | Web pass (2 WebSearch calls attributable to this question, both logged): no sell-side 3Q26 FX preview and no management quarter-to-date FX comment found; results only restate the 6 Aug guide | `sources/web_queries_2026-09-17.md` | 2026-09-17 | 2026-09-17 | no |
| 17 | 3Q25 letter printed "10% Y/Y, 10% Y/Y (ex-FX)" after guiding "minimal foreign exchange impact after factoring in our hedging program"; 4Q25 printed 12% / 11% after "a small foreign exchange tailwind"; 1Q25 letter prose "FX contributed to an approximately two percentage point headwind" with box 6% / 8% — prose and box agree in every case checked | `data/raw/letters/3Q25_d40503dex991.htm`, `4Q25_d58192dex991.htm`, `1Q25_d40594dex991.htm` | 2025-05-01 to 2026-02-12 | 2026-09-17 | no |

## 2. Query Log
1. [repo] read `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill `SKILL.md`, `references/research-log-format.md`, `examples/example-research-log.md`, `questions/q4-revenue-guide-vs-street/research-log.md`
2. [repo] `docs/revenue-forecast-strategy/05_backtests/fx-lag.md`, `B4_FX_EXHIBIT.md`, `FXSWAP_h2_bridge_kernel_fx.md`; `research/notes/overnight2/B_fx-relative-strength-geographic-mix.md`
3. [repo, python] every letter under `data/raw/letters/*.htm`: sentences containing "foreign exchange" / "FX" / "currency" with "revenue|growth|tailwind|headwind" (claims 1, 3, 17); Outlook sections of the 4Q24–2Q26 letters (claim 3)
4. [repo, pandas] `data/processed/abnb_driver_history_quarterly.csv` (fx_pts, take rates, GBV, revenue); `data/processed/overnight/28_fx_hedge_disclosures.csv`, `05_fx_schedule.csv`, `29_fx_step_down.csv`
5. [repo] `data/processed/forecast_methods/fx_lag_v2/` — `21_live_3q26_three_numbers.csv`, `02_basket_quarterly.csv`, `04_analysis_panel.csv`, `23_forecast_4q26_v2.csv`, `22_hedge_gross_vs_after.csv`, `01b_basket_weights_used.csv`, `fx_fetch_manifest_2026-09-11.csv`, `09b_pit_expanding_window_forecasts.csv`, `09c_pit_window_scores.csv`; `analysis/src/forecast_methods/fx_lag_v2/fetch_fx_v2.py`
6. [FRED, py -3.13] DEXUSEU, DEXUSUK, DEXBZUS, DEXMXUS, DEXJPUS, DEXUSAL, DEXKOUS, DEXCAUS, DEXINUS, DTWEXBGS re-pulled 2026-09-17T03:09:38Z (all through 2026-09-11) → `sources/`
7. [Polymarket public-search] airbnb; Airbnb Q3; Airbnb take rate; Airbnb revenue (2026-09-17T03:10:10Z)
8. [Kalshi API] markets?series_ticker=KXABNB, KXABNBA (open) (2026-09-17T03:10:10Z)
9. [WebSearch] Airbnb news (neutral recency pass, shared by the batch — result: Summer Release items, fake-listing removals, hotels commentary; nothing on FX)
10. [WebSearch] Airbnb third quarter 2026 revenue FX tailwind dollar analyst preview (result: only the 6 Aug guide restated; no preview)
11. [python] `datasets/c08_model.py` — basket rebuild, spec points, integer Monte Carlo, sensitivities, guide track record
12. [WebSearch, final 72-hour neutral recency check = query 9, run 2026-09-17; no later Airbnb FX or quarter-to-date item exists in the results] — no change to the number

WebSearch calls used by this question: 2 of 5 (query 9 is shared across the batch and counted here).

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, shareholder letter Key Financial Measures box, Φ recognition kernel, fx_lag_v2 H2, FRED H.10, hedging program, "approximately three percentage point FX tailwind"

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The registered live object (fx-lag free fit +1.3 / H2 PIT +1.85) is the right centre, so +1 or +2 dominates | kept as 0.42 of the mixture (middle 0.27 + free 0.12 + contemporaneous 0.03) | In-sample the short lag wins (claim 5), but the two most recent prints were under-forecast by ~1pp by H2 PIT (claim 6) and management's stated figure has printed at or above the guided integer in 9 of 10 pairs (claim 3); the registered spec's own W1/W2 winner is the lag-loaded shape, which lands at 2.9–3.0 on the basket (claims 4, 6) |
| Management's "approximately three" is a conservative guide and the print overshoots to 4 (the 2Q26 pattern) | kept inside the management component (P(≥4) 0.23 there; 0.13 in the mixture) | one of two numeric guides printed +1 above; the basket has drifted weaker-dollar since the guide (claim 8); the hedge drag is only ~0.2pp |
| The dollar moves enough in the last three weeks of the quarter to change the integer | discarded as material | 71–78% of the quarter is printed; under the free fit the lag-0 weight is 0.45 and a −5% dollar for the remaining weeks moves the vector by under 0.02 (sensitivity row 12); under Φ it moves nothing |
| The letter drops the ex-FX growth line or gives only a dollar figure (option d) | 0.02 | 23 of 23 letters print both rates as integers (claim 1); the 1Q25 letter printed prose points and the box, which agreed (claim 17) |
| Prose and box disagree (prose "approximately 3", box 17 − 14 = 3 vs 16 − 14 = 2) | inside the rounding kernel | convention (1): prose governs; the kernel already carries the box rounding; historical prose and box agree in every case checked (claim 17) |
| The hedge reclassification grows and subtracts a full point (stated = gross − 1) | discarded as central; inside the component sds | the 2Q26 10-Q's expected 12-month reclassification (~$26M) implies −0.21pp per quarter, down from −1.13 in 3Q25 (claim 9) |
| The 3Q26 basket itself (+0.5 to +0.6) is what management will report, i.e. FX is contemporaneous | kept at 0.03 | rejected by the PIT horse race (contemporaneous RMSE 1.9pp) and by the 2Q26 pair (ADR-FX +1.3 vs revenue-FX +4, claim 10) |

## 5. Independent Estimates
- base_rate_estimate: P(a) 0.77, P(b) 0.22, P(c) 0.01 — the management guided-FX track record (claim 3): with a "3" guide the printed integer has landed at 3 or 4 in 2 of 2 numeric cases and at or above the guided figure in 9 of 10 pairs; modelled as 3.0 ± 0.6 through the rounding kernel
- decomposition_estimate: P(a) 0.36, P(b) 0.35, P(c) 0.27 — the model-only mixture (no management component): Φ ×0.851 basket 2.9 (0.29), Φ ×0.653 / WS05 lagged / H2 PIT 1.85–2.2 (0.43), free fit 1.26 (0.21), contemporaneous 0.13 (0.07), each pushed through the rounding kernel (claims 4–7, 11, 13, 14)
- anchor_estimate: P(a) 0.28 — no market prices this; the designated anchor is the programme's registered live FX object (fx-lag-v2 H2 PIT at the 6 Aug guide date, +1.85, and the Φ ×0.653 shape-scale, +2.2; the 1.85–2.2 cluster at ±0.7 gives P(≥3) 0.28, P(2) 0.49, P(≤1) 0.24)
- anchor_value: P(a) 0.28 (registered fx-lag-v2 H2 PIT point +1.85 for 3Q26, vintage 2026-08-06, refreshed basket 2026-09-11)
- final_estimate: (a) 0.50, (b) 0.30, (c) 0.18, (d) 0.02
- final_minus_anchor: +22 points on (a). Justification for the divergence: the registered spec has under-forecast the last two prints by about 1pp (claim 6) and the only party with the booking-date ledger has guided "approximately three" and has never printed more than half a point below its guided figure in ten pairs (claim 3); the three estimates disagree by 49 points on (a) and the disagreement is entirely whether management's stated number is treated as information (base rate) or ignored (decomposition); the final weights management at 0.38, the kernel that reproduces it at 0.20 and the short-lag family at 0.42, so (a) is neither the model's 0.36 nor the track record's 0.77

## 6. Final Numbers
**Multiple choice.**
| Option | Probability |
|---|---|
| (a) ≥ +3 points | **0.50** |
| (b) +2 points | **0.30** |
| (c) ≤ +1 point | **0.18** |
| (d) not stated | **0.02** |
Sum 1.00. Inside (a): P(≥ +4) ≈ 0.13. Inside (c): P(≤ 0) ≈ 0.10, P(negative) ≈ 0.02.
Structure: management ~3 ± 0.6 (0.38) + Φ ×0.851 basket 2.9 ± 0.6 (0.20) + middle cluster 2.05 ± 0.7 (0.27) + free fit 1.26 ± 0.7 (0.12) + contemporaneous 0.13 ± 0.7 (0.03), each through the letter-rounding kernel, × 0.98, plus 0.02 not stated (`datasets/c08_integer_mc.csv`).
Extreme-probability gate: option (d) at 0.02 is at the threshold. Audit: (i) criteria re-read — (d) resolves only if neither the stated points nor both growth rates are printed; (ii) edge cases — a letter that prints only reported growth (no precedent in 23 letters), a format change to the Key Financial Measures box, a dollar-only FX statement (convention 5 converts it, so not (d)), the print date moving (same event, actual date); (iii) residual 0.02 assigned to (i)–(ii); (iv) confirmed. A small reallocation 0.50/0.30/0.18/0.02 → 0.48/0.30/0.19/0.03 costs ~0.01 of expected log score and caps the (d) loss; the log carries 0.02 because the format has held for six years.
Resolution-criteria notes: the pre-registered B4 rule reads (a) as vindicating the lag-loaded kernel, (c) the short-lag fit, (b) ambiguous; this forecast is on the integer only.

## 7. Sensitivity
All rows from `datasets/c08_sensitivity.csv` (single-assumption reruns of the mixture; vector shown as a / b / c with d fixed unless stated).
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Management component weight 0.38 | 0.50 → a 0.56 / b 0.28 / c 0.14; 0.15 → a 0.42 / b 0.33 / c 0.23; 0 (model-only) → a 0.36 / b 0.35 / c 0.27; round-1 weights (0.30) → a 0.46 / b 0.31 / c 0.22 |
| Kernel view only (management + Φ ×0.851) | a 0.74 / b 0.23 / c 0.01 |
| Short-lag view only (free fit 0.6, contemporaneous 0.4) | a 0.03 / b 0.20 / c 0.75 |
| Middle cluster only (Φ ×0.653 / H2 PIT 1.85–2.2) | a 0.27 / b 0.48 / c 0.23 |
| Component sds 0.6–0.7pp | doubled → a 0.49 / b 0.24 / c 0.25; halved → a 0.53 / b 0.30 / c 0.14 |
| Management centre 3.0 | 3.5 (2Q26-style overshoot repeats) → a 0.50 / b 0.24 / c 0.17, P(≥4) rises to ~0.25 |
| P(not stated) 0.02 | 0.05 → a 0.49 / b 0.29 / c 0.17 / d 0.05 |
| Dollar flat for the rest of the quarter | −5% (weaker dollar) → a 0.51 / b 0.29 / c 0.23 (lag-0 term only) |

Pre-mortem ("it is 5 Nov and the letter says +2", the modal miss): (1) the hedge reclassification for 3Q26 was larger than the ~$26M twelve-month expectation because the designated notional kept growing (priced only inside the component sds; a −0.6pp surprise moves the management component from 3.0 to 2.4 and (a) to ~0.40); (2) management's "approximately three" was a rounded 2.6 and the box printed 16% / 14% (inside the rounding kernel, ~0.2 of the management component); (3) the free fit is right and the two most recent H2 under-forecasts were noise (the 0.42 short-lag weight carries it); (4) the letter states the FX contribution to *GBV* prominently and revenue FX only via the box, and the box lands at 2 (convention (1) handles it; no probability change). "It says +1": the short-lag family (0.15 of the mixture) plus a hedge surprise. "It says +4": management undershoots as in 2Q26 (0.13). Asymmetry: the memo quotes the FX step-down (~+3 → ~+1) as arithmetic; a printed +1 or +2 would mean the step is smaller and the Q4 guide arithmetic less favourable to the short, which is why (b) and (c) are kept at 0.48 combined rather than compressed toward the management number.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| weekly (Mon) to 2026-10-05 | FRED H.10 release (prior week); re-run `datasets/c08_model.py` after refreshing `sources/` | Only the lag-0 term moves; a ±5% dollar move for the rest of the quarter shifts the vector by ≤ 0.02 — hold unless the basket QTD crosses ±1.5% |
| 2026-09-18 to 2026-10-02 | Any management conference remark on 3Q26 FX (none found 1 Aug–16 Sep) | A restated "approximately three" → raise management weight to 0.50 (a 0.56); "closer to two" → move the management centre to 2.0 (a ≈ 0.30) |
| 2026-10-02 | Prelim memo due | Quote (a) 0.50 / (b) 0.30 / (c) 0.18 / (d) 0.02; state the B4 decision rule beside it |
| 2026-10-15 to 2026-11-03 | Sell-side 3Q26 previews with an FX line | A preview quoting management's ~3 as consensus changes nothing; a preview computing +1 to +2 from a basket → no change (that is the model family already at 0.42) |
| 2026-11-05 (after close) | 3Q26 letter: Key Financial Measures box (reported and ex-FX growth), Outlook FX sentence for 4Q26, 10-Q hedge reclassification | Resolve; record the integer against the B4 rule; the printed 3Q26 ADR-FX point settles the +0.15 vs +1.0 4Q26 reading (FXSWAP §4) |

RESUME: the next agent (audit response) should re-run `datasets/c08_model.py` (deterministic, ~20 s; it re-reads the FRED pull in `sources/`), check claim 3's ten guide/print pairs against the letters' Outlook sections and Key Financial Measures boxes (the mapping of qualitative words to numbers — "modest" ±0.5, "small" +0.5, "minimal" 0 — is judgement and is the weakest link), and attack the two load-bearing choices: the 0.38 management weight (0.15–0.50 moves (a) between 0.42 and 0.56) and the treatment of the 1.85–2.2 cluster as one component (splitting it does not move the vector by more than 0.02). If the audit finds a letter where the printed integer fell a full point below a numeric guide, the management component's sd should widen to 1.0 and (a) falls to about 0.45.
