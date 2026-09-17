# RESEARCH LOG

## 0. Metadata
- question_name: q3-take-rate-above-1810
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § C11)
- type: binary
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
Will Airbnb's printed 3Q26 take rate (revenue ÷ GBV, as reported) be ≥ 18.10%?
### Resolution Criteria
Yes if 3Q26 revenue / 3Q26 GBV from the press release ≥ 0.1810, computed on unrounded dollars where given, else on the letter's rounded figures. Resolution date 5 Nov 2026.
### Fine Print
Score jointly with GBV: the log must report P(take rate ≥18.10 | GBV band) and the unconditional. Inputs: B1 take-rate reconciliation, nowcast GBV, the fee-migration timing (K note), management's "slightly higher" take-rate remark and the new-business incentives.

Conventions adopted for ambiguities: (1) revenue is the income-statement figure in $ millions (unrounded to the million); GBV is printed to $0.1bn in the letter and the 10-Q, so the ratio is computed on the rounded GBV — a ±$50M rounding cell is ±0.19% of GBV, ±3.4bp of take rate, and is inside the model's 0.33–0.39pp sd; (2) the letter's own "implied take rate" (rounded to 0.1%) is not the resolution object; (3) "Nights and Seats Booked"-basis GBV as reported (including Experiences and Services) is the denominator; (4) if the print date moves, the same release on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Printed Q3 take rates (revenue / same-quarter GBV): 3Q21 18.80%, 3Q22 18.49%, 3Q23 18.56%, 3Q24 18.57%, 3Q25 17.88% (4,095 / 22,900); 3Q25 fell 69bp y/y "primarily due to FX and the timing of when guests booked their travel and when guests stayed" (revenue FX 0 vs GBV FX +2 that quarter); Q3 is structurally the highest take-rate quarter (2Q26 13.26%, 1Q26 9.17%) | `data/processed/abnb_driver_history_quarterly.csv` (take_rate_calc_pct); `data/raw/letters/3Q25_d40503dex991.htm`; `datasets/c11_history.csv` | 2025-11-06 | 2026-09-17 | yes |
| 2 | B1 reconciliation (11 Sep): printed 3Q26 take rate 18.14%, sd 0.46pp, P(≥18.10) 0.53, P(≤17.88) 0.28, on revenue 4,816.1 (sd 48) and GBV 26,549.8 (sd 853) with ρ(revenue, GBV) 0.76; the probability is robust to ρ (0.53–0.54) but the point is a near-linear function of GBV: 25,900 → 18.59% / 0.85; 26,185 → 0.73; 26,300 → 0.68; 26,800 → 0.39; 27,000 → 0.28; the GBV at which the point equals 18.10% is 26,608; "a GBV test wearing a fee test's clothes"; the W1 walk-forward biases (revenue +0.80%, GBV +1.77%) are not applied and would lift P to 0.68 | `docs/revenue-forecast-strategy/05_backtests/B1_TAKE_RATE_RECONCILIATION.md` §2–5; `data/processed/forecast_methods/live_block_v2/04_gbv_sensitivity.csv`, `03_takerate_sensitivity.csv`, `LIVE_3Q26_CARD.csv` | 2026-09-11 | 2026-09-17 | yes |
| 3 | 2Q26 letter, verbatim: "We expect our implied take rate to remain relatively in-line year-over-year." Call (6 Aug): "For the full year, we expect our implied take rate to be relatively flat compared to 2025, accounting for the timing of bookings versus check-in with Reserve Now, Pay Later, as well as higher customer incentives related to new businesses during 2026. Absent these incentives, we would have anticipated our implied take rate to be slightly higher during the year." Letter on 2Q26: "the implied take rate … of 13.2% was in-line with Q2 2025. Factors impacting the Q2 2026 take rate included FX and the timing of when guests booked their travel and when guests stayed—a dynamic that reflects the growth of Reserve Now, Pay Later, which has resulted in guests booking further in advance." (ledger D049) | `data/raw/letters/2Q26_d70413dex991.htm`; `data/raw/transcripts/web/2Q26.html`; `data/processed/overnight2/D/rnpl_statement_ledger.csv` D049 | 2026-08-06 | 2026-09-17 | yes |
| 4 | Management's take-rate language vs the printed y/y change, six pairs: 2Q24 letter "higher" for 3Q24 → 0bp (18.57 vs 18.56); 1Q25 "higher" for 2Q25 → +9bp; 2Q25 "flat" for 3Q25 → −69bp; 3Q25 "relatively flat" for 4Q25 → −47bp; 4Q25 "up slightly" for 1Q26 → −10bp; 1Q26 "up slightly" for 2Q26 → +9bp. Mean error vs the guided direction ≈ −18bp; the print has never exceeded the guided direction by more than +9bp; "in-line" (3Q26) therefore centres 17.9% and the threshold is +22bp above the prior year | `data/raw/letters/2Q24_…`, `1Q25_…`, `2Q25_…`, `3Q25_…`, `4Q25_…`, `1Q26_…` (Outlook take-rate sentences, extracted this run); `abnb_driver_history_quarterly.csv` | 2024-08-06 to 2026-05-07 | 2026-09-17 | yes |
| 5 | 2Q26 letter guide: revenue $4.69–4.77bn (+15–17%, ~+3pp FX after hedging); "GBV growth to be in the mid teens, driven by low double-digit growth in Nights and Seats Booked and a moderate increase in ADR due to mix shift and price appreciation". At the guide midpoints (revenue 4,730; GBV +15% = 26,317) the implied take rate is 17.97%; at the guide top (4,770) and GBV +15% it is 18.12% | `data/raw/letters/2Q26_d70413dex991.htm` | 2026-08-06 | 2026-09-17 | yes |
| 6 | Next-quarter revenue guides: 19 of 19 printed above the midpoint; Q3 cushions (actual/mid − 1): 3Q22 +1.91%, 3Q23 +1.40%, 3Q24 +0.86%, 3Q25 +0.86% (mean 1.04% for 2023–25, 1.26% incl. 2022); trailing-8 all-quarter cushion 1.86% | `data/processed/overnight/02_guidance_ledger.csv` (metric revenue_usd_m, guide_type range); `05_backtests/guidance-policy.md` | 2026-09-11 | 2026-09-17 | yes |
| 7 | Team 3Q26 nights nowcast +9.5% (146.3m), band 8.5–10.0 (model path 9.9); ADR card v3 +3.3% ($176.9), central band +1.9 to +4.6; implied GBV ≈ $25.9bn (+13.2%); the brief mandates this band as the input | `docs/q3nowcast/SYNTHESIS.md` §1; `docs/adrv3/SYNTHESIS.md` §1; `docs/pitch-forecasts/00_BRIEF.md` rule 6 | 2026-09-11 / 2026-09-12 | 2026-09-17 | yes |
| 8 | Street 3Q26: LSEG-family revenue mean $4,744.9M (n 36, 2026-09-13T15:20Z; high 4,792 / low 4,677); Bloomberg MODL (12 Sep) nights 148.9m (+11.5%), GBV $26,375M (25,992–26,723), ADR $177.06; Street-implied take rate 4,744.9 / 26,375 = 17.99% | `data/processed/forecast_methods/L0/L0_vintage_register.csv` row `CU-2026Q3-revenue-Yahoo-20260913T1520Z`; `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv` | 2026-09-12 / 2026-09-13 | 2026-09-17 | yes |
| 9 | Kalshi KXABNB Q3 2026 nights ladder, yes bid/ask at 2026-09-17T03:10:10Z: >144m 0.76/0.83, >146m 0.63/0.66, >148m 0.50/0.55, >150m 0.32/0.36 (volume field None); mid-price median ≈ 148.2m (+10.9%); with ADR +3.4% this implies GBV ≈ $26.26bn. No Polymarket market on Q3 KPIs, revenue or take rate (four searches) | `sources/kalshi_markets_KXABNB_open_20260917T031010Z.json`; `sources/polymarket_search_*_20260917T031010Z.json` | 2026-09-17 | 2026-09-17 | yes |
| 10 | fee-takerate: single fee 15.50% of the host price vs split 14.99% of the guest total; the migrated cohort's GBV falls 1.6–2.3% at θ 0.83 while revenue rises 1.1–1.8%; on the printed take rate "a 40% migrated revenue share at a +1.8% cohort uplift is worth about +7 bp on a 13.3% base"; no fee effect detectable in printed take rates through 2Q26 (n 20, slope wrong sign, permutation p 0.73); the 3Q26 pre-registration "discriminates on GBV, not on the fee"; the printed take rate must be treated as an output, not a lever (neither take-rate object beats the seasonal naive on either window) | `05_backtests/fee-takerate.md` §1, §3, §4, §6 | 2026-09-11 | 2026-09-17 | yes |
| 11 | K note: tranche 2 of the single-fee migration runs through the 15 Sep (non-EEA) and 13 Oct (EEA/CH) deadlines; y/y migrated nights share +46pp in 3Q26, +75pp in 4Q26; the reprice term on the residual is +0.17pp (3Q26) at the central coefficient, a mechanics line, not a finding; the deadlines are confirmed by a third-party page (smoobu, 2026-07-09: "Hosts outside the European Economic Area: September 15, 2026. Hosts inside the European Economic Area: October 13, 2026") | `research/notes/adrv3/K_residual-decomposition-fee-migration.md` §1.5, §2.7; https://www.smoobu.com/en/blog/airbnb-host-only-fee-increase/ | 2026-09-11 / 2026-07-09 | 2026-09-17 | no |
| 12 | FX wedge for 3Q26: revenue FX guided ~+3 after hedging (C08 log: P(≥3) 0.50, P(2) 0.30); GBV/ADR FX −1.1 (EUR fit) to +0.3 (baskets); at a +3pp revenue-minus-GBV wedge the take rate gains ≈ 17.9% × 3% ≈ +50bp before timing and incentives — the reverse of 3Q25, when revenue FX 0 vs GBV FX +2 cost ~35bp | `../q3-revenue-fx-integer/research-log.md`; `research/notes/overnight2/B_*` table 2.4; `datasets/c11_history.csv` | 2026-09-17 | 2026-09-17 | yes |
| 13 | GBV guide track record (qualitative bucket → print): 3Q25 letter "low-double-digits" for 4Q25 → +15.9% (ex-FX +13); 4Q25 "low teens" for 1Q26 → +19.2% (ex-FX +13); 1Q26 "low double digits" for 2Q26 → +15.7% (ex-FX +15); GBV prints have exceeded the guided bucket by 1–4pts ex-FX; 3Q26 is guided "mid teens" with GBV FX near zero | `data/raw/letters/3Q25_…`, `4Q25_…`, `1Q26_…`, `2Q26_…`; `data/processed/overnight/02_kpi_panel_quarterly.csv` (gbv_yoy_reported_pct, gbv_yoy_exfx_pct) | 2025-11-06 to 2026-08-06 | 2026-09-17 | yes |
| 14 | Monte Carlo (this log, `datasets/c11_model.py`, seed 20260917, n 400,000): team band (nights 9.5 ± 1.6, ADR 3.3 ± 1.3, revenue = 4,730 × (1 + N(1.1%, 0.5%)) with ρ 0.5 to the GBV shock, P(guide miss) 3%): P(YES) 0.871, take median 18.47, sd 0.33; Kalshi-implied GBV N(26,260, 600): 0.604; MODL N(26,375, 600): 0.524; management mid-teens N(26,317, 550): 0.571; B1 stacked N(26,550, 853): 0.429; B1 replication (revenue N(4,816, 48), ρ 0.76): 0.536 vs B1's 0.534. Final mixture (0.50 team / 0.30 Kalshi-GBV / 0.20 wide): 0.765, take median 18.38, P(≤17.88) 0.10. Point-GBV rows: 25,900 → 0.98; 26,185 → 0.94; 26,300 → 0.80; 26,410 → 0.52; 26,550 → 0.15; 26,800 → 0.00 | computed; `datasets/c11_mc_summary.csv`, `c11_by_gbv_band.csv`, `c11_sensitivity.csv` | 2026-09-17 | 2026-09-17 | yes |
| 15 | Web pass (2 WebSearch calls attributable to this question): no sell-side 3Q26 take-rate preview found; third-party host pages confirm the 15.5% single fee (16% Brazil/Mexico) and the migration deadlines; nothing on Q3 incentives | `sources/web_queries_2026-09-17.md` | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] read `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill `SKILL.md`, `references/research-log-format.md`, `examples/example-research-log.md`, `questions/q4-revenue-guide-vs-street/research-log.md`, `datasets/c01_model.py`
2. [repo] `docs/revenue-forecast-strategy/05_backtests/B1_TAKE_RATE_RECONCILIATION.md`, `fee-takerate.md`; `research/notes/adrv3/K_residual-decomposition-fee-migration.md`; `docs/q3nowcast/SYNTHESIS.md`
3. [repo, pandas] `data/processed/abnb_driver_history_quarterly.csv` (take_rate_calc_pct, fx_pts, GBV, revenue by quarter)
4. [repo] `data/processed/forecast_methods/live_block_v2/04_gbv_sensitivity.csv`, `03_takerate_sensitivity.csv`, `LIVE_3Q26_CARD.csv`
5. [repo, python] take-rate / RNPL / single-fee sentences from the 2Q26, 1Q26, 4Q25, 3Q25 letters and the 2Q26 call mirror; Outlook take-rate sentences 2Q24–2Q26 (claims 3–5, 13); ledger rows D019, D044, D049, D051
6. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` (revenue ranges, Q3 cushions); `L0_vintage_register.csv` 2026Q3 rows; `reverse_dcf/E/E_street_distribution_vs_team.csv`
7. [Kalshi API] markets?series_ticker=KXABNB, KXABNBA (open) — saved to `sources/` (2026-09-17T03:10:10Z)
8. [Polymarket public-search] airbnb; Airbnb Q3; Airbnb take rate; Airbnb revenue — saved to `sources/`
9. [WebSearch] Airbnb news (neutral recency pass, shared by the batch — nothing on take rate)
10. [WebSearch] Airbnb take rate Q3 2026 single fee migration hosts September 2026 (result: host-facing fee explainers; migration deadlines; no take-rate preview)
11. [WebFetch] smoobu.com/en/blog/airbnb-host-only-fee-increase/ (deadline sentences, published 2026-07-09)
12. [python] `datasets/c11_model.py` — joint Monte Carlo, GBV-band table, sensitivities, Q3 history
13. [WebSearch, final 72-hour neutral recency check = query 9, 2026-09-17: nothing new on take rate, incentives or GBV] — no change to the number

WebSearch calls used by this question: 2 of 5.

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, implied take rate, Reserve Now Pay Later, single fee 15.5%, GBV mid teens, B1 live block, Kalshi KXABNB, Bloomberg MODL

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| B1's published 0.53 is the right headline | kept as the anchor's neighbourhood, not the headline | B1 integrates over the stacked GBV $26,550M, $670M above the team nowcast the brief mandates; the model reproduces B1 under B1's inputs (0.536 vs 0.534, claim 14) and moves to 0.87 on the team band alone |
| Management's "relatively in-line" is a point forecast of 17.9% with ±10bp tolerance, so YES is a ~15% event | kept as the base-rate estimate (0.18) and 0.25 of the final weight | the six-pair record (claim 4) shows prints at or below the guided direction; but "in-line" plus "mid teens" GBV is inconsistent with the revenue guide midpoint (17.97% at 4,730 / 26,317; claim 5) and the FX wedge reverses this year (claim 12), so the language is a cushioned statement, not a point |
| GBV prints at the top of "mid teens" or above (≥ +16%, ≥ $26.55bn) because GBV guides have been beaten by 1–4pts ex-FX | kept: 0.30 market-GBV component plus the wide component; P(GBV ≥ 26.5bn) ≈ 0.20 in the mixture | claim 13; needs nights ≥ 11% or ADR ≥ +4.5% on the team's numbers; Kalshi's nights median is 148.2m (+10.9%) and the reviews index says no acceleration |
| The fee migration lifts the take rate materially in 3Q26 | discarded as material (≤ +7–10bp) | fee-takerate §3–4 (claim 10): both legs move together; the 3Q26 test discriminates on GBV, not the fee |
| RNPL timing (longer lead times, July eligibility expansion) pulls 4Q bookings into 3Q26 GBV and depresses the ratio, as it did in 3Q25 (−69bp) | kept inside the revenue-cushion sd and the ρ term; not separately modelled | the 3Q25 pull-forward is in the base; a further pull-forward from the July expansion is plausible (D044) and is the main reason the management-language estimate keeps 0.25 weight |
| Revenue misses the guide for the first time | 3% inside the model | 19/19 beats; a miss at the guide low ($4,690M) with GBV $25.9bn still prints 18.1% |
| Rounded GBV in the release (to $0.1bn) flips a razor-thin outcome | inside the sd (±3.4bp) | convention (1); moves P by ≤ 0.02 |

## 5. Independent Estimates
- base_rate_estimate: 0.18 — management's take-rate language record (claim 4): six guided directions, prints at or below the guided direction in 5 of 6, max overshoot +9bp; "relatively in-line" centres 17.9% and the threshold needs +22bp; modelled as N(17.90, 0.25) → P(≥18.10) ≈ 0.21, trimmed to 0.18 for the two −47/−69bp misses
- decomposition_estimate: 0.77 — joint Monte Carlo (claim 14): revenue = guide midpoint × Q3 cushion, GBV = 3Q25 base × nights × ADR from the team band (0.50), the Kalshi-implied GBV (0.30) and a wide component (0.20); take median 18.38, sd 0.39
- anchor_estimate: 0.45 — no market prices the ratio; the anchor is the Street's own means: LSEG revenue 4,744.9 / MODL GBV 26,375 = 17.99% (claim 8), which at the model's 0.39pp sd gives P(≥18.10) ≈ 0.39; the Kalshi-nights route gives 0.60 and B1's published number is 0.53; 0.45 is the Street-means figure nudged toward the Kalshi route
- anchor_value: 0.45 (Street-implied take rate 17.99% on LSEG revenue 2026-09-13T15:20Z and Bloomberg MODL GBV 12 Sep; Kalshi 2026-09-17T03:10Z)
- final_estimate: 0.55 (credible interval 0.40–0.70)
- final_minus_anchor: +10 points. Independence: the decomposition's GBV input is the team nowcast, not the Street's; the base rate is management's language; the final is 0.45 × 0.77 + 0.25 × 0.18 + 0.30 × 0.45 = 0.53, rounded to 0.55 because the FX wedge (claim 12) points up and is not in the language record. The three estimates disagree by 59 points; the disagreement is one number, printed 3Q26 GBV: below $26.3bn the answer is YES on almost any revenue beat, above $26.6bn it is NO on almost any beat (claim 14)

## 6. Final Numbers
**Binary.** P(printed 3Q26 take rate ≥ 18.10%) = **0.55**, credible interval **0.40–0.70**. P(≤ 17.88%, i.e. no recovery at all) ≈ 0.12.

**Conditional on the printed GBV (fine print), from the final mixture (`datasets/c11_by_gbv_band.csv`):**
| GBV band, $M | GBV y/y | mass in mixture | P(≥ 18.10 \| band) | take-rate median |
|---|---|---|---|---|
| < 25,600 | < +11.9% | 0.24 | 1.00 | 18.82 |
| 25,600–25,900 | +11.9 to +13.2% | 0.19 | 0.99 | 18.54 |
| 25,900–26,200 | +13.2 to +14.5% | 0.20 | 0.97 | 18.36 |
| 26,200–26,500 | +14.5 to +15.8% | 0.17 | 0.76 | 18.18 |
| 26,500–26,800 | +15.8 to +17.1% | 0.11 | 0.17 | 18.00 |
| ≥ 26,800 | ≥ +17.1% | 0.10 | 0.00 | 17.74 |
Point-GBV rows (revenue at the guide midpoint × Q3 cushion): 25,900 → 0.98; 26,185 (frozen card) → 0.94; 26,300 → 0.80; 26,410 → 0.52 (the break-even GBV at a 1% revenue beat: 4,777 / 0.1810); 26,550 → 0.15; 26,800 → 0.00.
The unconditional 0.55 is lower than the mixture's 0.77 because the mixture's GBV mass (median ≈ $26.0bn) is the team's; the final gives 0.25 weight to management's "in-line" language and 0.30 to the Street's implied 17.99%, both of which sit at or above $26.3bn of GBV.
Extreme-probability gate: not triggered.

## 7. Sensitivity
Single-assumption reruns of `datasets/c11_model.py` from the team-band base (0.871); the final moves roughly 0.6 × the base move.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| GBV centre = team nowcast $25.9bn | Kalshi-implied $26.26bn: 0.60; MODL $26.38bn: 0.52; management mid-teens $26.32bn: 0.57; B1 stacked $26.55bn: 0.43 |
| Nights 9.5 ± 1.6 | 10.0: 0.81; 8.5: 0.95; 11.0 with ADR 3.4: 0.62 |
| ADR +3.3 ± 1.3 | +2.0: 0.96; +4.4: 0.71 |
| Q3 cushion 1.1% ± 0.5% | 0.86% (2024–25): 0.84; 1.40% (3Q23): 0.90; 1.86% (trailing-8): 0.93; 0 (print at midpoint): 0.70 |
| ρ(cushion, GBV) 0.5 | 0: 0.84; 0.8: 0.89 |
| P(guide miss) 3% | 0: 0.88; 10%: 0.84 |
| Joint bull GBV (nights 11.0, ADR 4.4, cushion 0.86) | 0.36 (median 17.98) |
| Joint bear GBV (nights 8.5, ADR 2.0, cushion 1.4) | 0.99 (median 18.93) |
| Final blend weights 0.45 / 0.25 / 0.30 | all on the decomposition: 0.77; all on management language: 0.18; all on the Street means: 0.45 |

Pre-mortem ("it is 5 Nov and the take rate printed 17.9–18.0%"): (1) GBV printed ≥ $26.5bn — nights 11%+ from late-quarter RNPL bookings the reviews index cannot see, or ADR +4.5% — priced at ~0.20 in the mixture and the main reason the interval reaches 0.40; (2) the July RNPL eligibility expansion pulled 4Q26 bookings into 3Q26 GBV without adding Q3 revenue (the 3Q25 mechanism repeating) — priced only through the management-language weight; (3) new-business customer incentives (contra-revenue) were larger than in 2Q26 — priced inside the cushion sd; (4) the revenue beat was the smallest on record (≤ 0.5%) — P(cushion ≤ 0.5%) ≈ 0.11. "It printed 18.4%+": the team's GBV was right (0.55 of the mixture mass sits above 18.3). Asymmetry: the memo's take-rate sentence is pre-registered as a pair with GBV; a confident YES that resolves NO on a GBV beat would be read as a fee-thesis failure when it is a demand surprise — the log keeps the interval wide and the conditional table in front for that reason.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-10-02 | September Inside Airbnb reviews/calendar dumps; E/F re-run; 3Q26 nights band refreshed | Re-centre GBV: each +0.5pt of nights ≈ +$115M GBV ≈ −0.06 on the base P (−0.04 on the final); a band centred ≥ 10.5 moves the final toward 0.45 |
| weekly to 2026-11-04 | Kalshi KXABNB mid-price median; LSEG 3Q26 revenue mean and MODL GBV (register the capture) | Kalshi median ≥ 149.5m (+11.9%) → Street-route P falls below 0.35, final ~0.48; ≤ 147m → final ~0.60 |
| 2026-10-02 | Prelim memo due | Quote 0.55 (0.40–0.70) with the GBV-conditional table; state that B1's 0.53 is the same model at the stacked GBV |
| 2026-10-13 | EEA/CH single-fee deadline | No change to P (fee effect ≤ 10bp); note any host-side pricing evidence for R04/B17 |
| 2026-10-15 to 2026-11-03 | Sell-side 3Q26 previews; any management remark on incentives or take rate at a conference | A repeated "in-line" → hold; "slightly higher" or a quantified fee lift → +0.05; a GBV "high teens" remark → −0.10 |
| 2026-11-05 (after close) | 3Q26 release: revenue ($M), GBV ($0.1bn), nights, ADR, letter's implied take rate | Resolve; audit read: at printed GBV ≤ $26.2bn the pre-print P was ~0.95, at $26.3–26.5bn ~0.75, at ≥ $26.6bn ~0.15 |

RESUME: the next agent (audit response) should re-run `datasets/c11_model.py` (deterministic, ~60 s), check claim 4's six take-rate language pairs against the letters (the mapping of "higher / flat / up slightly / in-line" to a centre is judgement), and challenge the blend weights in section 5 (0.45 decomposition / 0.25 language / 0.30 Street): the headline moves between 0.45 and 0.65 across defensible weightings, and the whole question is the printed GBV, tabulated in section 6.
