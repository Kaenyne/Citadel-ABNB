# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A14). Companion questions: B01 `bonus-moderation-language`, B03 `bonus-marketing-cut-signalled`; mirror question R07 `risk-adr-residual-persists` (≥ +4.4%, batch A10, whose model gave P(≤ +2.0%) ≈ 0.17 as a companion number and is the starting point here). Reused as inputs: R07's log and `datasets/r07_model.py`, ADR v3 (`docs/adrv3/SYNTHESIS.md`, `research/notes/adrv3/`), the H card (`research/notes/q3nowcast/H_3q26-adr-card.md`), the ADR Q3 nowcast (`docs/adrq3/`). Reproduction: `datasets/b02_model.py` (numpy/pandas, seed 20260917, n 400,000; seconds) → `b02_results.csv`, `b02_history.csv`, `b02_v3_errors_by_direction.csv`, `b02_modest_increase_record.csv`.

## 0. Metadata
- question_name: bonus-adr-residual-reverts
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B02)
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
Will 3Q26 reported ADR growth print ≤ +2.0% y/y?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if 3Q26 ADR ≤ $174.72. Resolution 5 Nov 2026.
### Fine Print
(none beyond the registry header conventions.)

Conventions adopted (mirroring R07): (1) "reported ADR" is the letter's GBV-per-night figure as printed; the cent figure governs where the 10-Q/KPI table gives one, else the letter's dollar figure ($174.72 rounds to $175, so a letter print of "$175" with an unrounded value of $174.73–175.49 resolves No; a print of "$174" resolves Yes); (2) the base is the printed 3Q25 ADR $171.29 as the question states, not a restated figure; (3) ADR is Nights-and-Seats-basis GBV over nights and seats, as reported (seats dilution is inside the card's new-business term); (4) if the print date moves, the same release on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | R07 (batch A10, same run): P(≥ +4.4%) 0.17; structural Monte Carlo reported = mix N(−1.15, 0.35) + residual mixture [persistence N(4.85, 0.55) 0.55 / momentum N(5.35, 0.55) 0.20 / partial reversion N(3.6, 0.7) 0.25] + FX mixture [midpoint N(−0.43, 0.33) 0.50 / baskets N(0.26, 0.42) 0.25 / euro N(−1.12, 0.46) 0.25]; median +3.1%, **P(≤ +2.0) 0.17 (reproduced here: 0.172, E[reported \| ≤ 2.0] +1.32)**; R07's RESUME flags the FX-estimator weights and the residual weights as the two levers | `../risk-adr-residual-persists/research-log.md` §5–6, claim 10; `../risk-adr-residual-persists/datasets/r07_model.py`; `datasets/b02_results.csv` rows 23–25 | 2026-09-17 | 2026-09-17 | yes |
| 2 | Card v3 (11–12 Sep): 3Q26 reported ADR +3.3% ($176.9) pre-registered, +3.4% ($177.2) with the K line; central band +1.9 to +4.6 (the threshold +2.0 is at the bottom of the central band); euro fit +2.6/+2.7%, baskets +4.0/+4.1%, midpoint FX −0.43; ex-FX +3.9 = geographic mix −1.43 + party size +0.80 + LOS +0.06 + new business −0.48 + interaction −0.10 + K line +0.17 + residual +4.85; H card (12 Sep): 3Q26 +3.2%, central band $174.0–179.1 (+1.6 to +4.6), "the FX estimator choice alone moves the point from +2.5% to +3.9%"; the component build is "biased low by about 1.5 pp in 1H26 because a trailing residual cannot see an acceleration" and does not beat naive (RMSE 1.29 vs 0.82, n 9) | `docs/adrv3/SYNTHESIS.md` §1, §4; `data/processed/adrv3/P/adr_card_v3.csv`; `research/notes/q3nowcast/H_3q26-adr-card.md` §1 items 1, 4, §2.2 | 2026-09-11 / 2026-09-12 | 2026-09-17 | yes |
| 3 | Reported ADR y/y 1Q23–2Q26 (n 14): **≤ +2.0 in 5** (1Q23 +0.2, 2Q23 +1.4, 3Q24 +1.4, 4Q24 +0.9, 1Q25 −0.9); **0 of 7 with FX ≥ −0.5; 0 of 4 with a residual ≥ 3.5** (1Q23's residual 3.48 printed +0.2 only because FX was −2.8). Residual series 3.48, 2.47, 1.01, 0.83, 2.26, 3.23, 2.08, 2.76, 2.23, 1.91, 2.82, 3.70, 4.38, 4.85: largest one-quarter fall −1.47 (2Q23→3Q23), sd of one-quarter changes 0.93 (n 13); AR(1) const 0.750, rho 0.747, innovation sd 0.94, 3Q26 point 4.37. To print ≤ 2.0 at the midpoint FX (−0.43) with the measured mix (−1.15), the residual must fall to ≤ 3.58 (−1.27 in one quarter, seen once in 13 changes); at the euro-fit FX (−1.12) to ≤ 4.27 (−0.58, seen 5 times); at the baskets FX (+0.26) to ≤ 2.89 (−1.96, never) | `datasets/b02_history.csv` (from `data/processed/q3nowcast/H/adr_history_components.csv`); `datasets/b02_results.csv` rows 0–8 | 2026-09-12 / 2026-09-17 | 2026-09-17 | yes |
| 4 | Management's "modest/moderate increase" ADR sentences resolved (ledger, n 5): 2Q24 "modestly up" → +2.1; 3Q24 "increase modestly" → +1.4; 4Q24 "increase modestly" → +0.9; 3Q25 "increase modestly, primarily driven by FX" → +4.7; 4Q25 "modest increase ... price appreciation and FX" → +5.9. **Printed ≤ +2.0 in 2 of 5** (a third at +2.1); those three sat on residuals of 2.1–2.8 and FX of −0.6 to −1.1, against 4.85 and ≈ −0.4 now. The 3Q26 sentence: "a moderate increase in ADR due to mix shift and price appreciation" (no FX credited). Ledger tell 5.5: "ADR direction calls go wrong when FX moves after the guide is set"; all 8 "ADR up" floors were met — a print ≤ +2.0 would still meet the floor | `data/processed/overnight/02_guidance_ledger.csv` rows 100, 108, 118, 147, 156, 185; `02_guidance_tells.csv`; `datasets/b02_modest_increase_record.csv` | 2024-05-08 to 2026-08-06 | 2026-09-17 | yes |
| 5 | Card v3 walk-forward errors (reported dollar y/y, P1 paths with the K line, 1Q24–2Q26, n 10): midpoint RMSE 0.93 / bias −0.31 (model low); euro 1.09 / −0.38; baskets 0.83 / −0.24. **Split by direction (new here): the five decelerating quarters (actual < prior) have mean error +0.07 and RMSE 0.89; the five accelerating quarters mean −0.69, RMSE 0.96.** So the rule is late into accelerations and roughly unbiased into decelerations; the hypothesis that the component build is "biased high into decelerations" (the mirror of its 1H26 low bias) is not supported on n 5 — the lower tail is not fatter than the symmetric RMSE says, but it is not thinner either (the rule missed 3Q24 by +1.63) | `data/processed/adrv3/P/P1_card_v3_backtest_paths.csv`; `datasets/b02_v3_errors_by_direction.csv`; `datasets/b02_results.csv` rows 9–13 | 2026-09-12 / 2026-09-17 | 2026-09-17 | yes |
| 6 | FX estimator: midpoint of the euro fit and the regional baskets (RMSE 0.33 on the scored window; euro 0.46, baskets 0.42); the two single estimators win in different eras; 3Q26 FX −0.43 (euro −1.12, baskets +0.26); "the 1.4 pp spread between the two single estimators remains the largest controllable uncertainty on the ADR line". Under the euro fit the card is +2.7% and the threshold 0.7pp away; under baskets +4.1% and 2.1pp away | `data/processed/adrv3/N/N1_fx_choice_card.csv`, `N1_fx_estimator_window_summary.csv`; `data/processed/overnight2/B/B_adr_fx_estimator_backtest.csv`; R07 claim 6 | 2026-09-11 | 2026-09-17 | yes |
| 7 | Measured 3Q26-to-date mix terms: party size +1.35% capacity → +0.80pp (unchanged vs 2Q26 +0.87 and 3Q25 +0.81); geographic mix −1.43pp on the E regional split (NA +6.9 / EMEA +0.9 / LatAm +27.5 / APAC +10.0), "a larger drag than assumed", band −1.57 to −0.94 with an unvalidated mapping (RMSE 0.4–0.7pp on n 10); LOS +0.06; the three measured terms net −0.57. The J3-fill centre used by R07 is −1.15; the geo drag is the one measured term that is one-sided against ADR this quarter (LatAm nights +27.5% at roughly half the global ADR) | `docs/adrq3/SYNTHESIS.md` §2; `docs/adrv3/SYNTHESIS.md` §3; R07 claim 7 | 2026-09-11 | 2026-09-17 | yes |
| 8 | External price proxies (one-sided toward reversion, weak): STR/CoStar US hotel ADR y/y July +5.7% (World Cup), weeks ending 8 Aug +4.1, 15 Aug +3.5, 22 Aug +2.3, 29 Aug +0.6, 5 Sep +6.1 (Labor Day shift; the week ending 12 Sep is not yet published — search returned the 5 Sep week only); CPI lodging away from home July +3.1 (from +4.9); NerdWallet on the August CPI (11 Sep 2026): "hotel and motel room rates are up by 2.9% over the past year", airfares +23.4%. The ADR Q3 nowcast found none of nine external price proxies beats naive against the residual (best ratio 1.03), so these carry direction, not weight | `data/processed/q3nowcast/G/str_weekly_us_3q26.csv`; `docs/adrq3/SYNTHESIS.md` §3–4; https://www.nerdwallet.com/travel/learn/travel-price-tracker ; https://www.asianhospitality.com/costar-us-hotel-metrics-mixed-weekly-up-yoy/ (snippet) | 2026-08-26 to 2026-09-11 | 2026-09-17 | no |
| 9 | Bloomberg MODL 3Q26 ADR (12 Sep, n 26): low $173.71 (+1.4%), mean $177.06 (+3.4%), high $179.12 (+4.6%); the threshold $174.72 sits between the low and the mean, at roughly the 4th–8th percentile of the analyst range (one, at most two, of 26 estimates at or below it); no vendor publishes an ADR consensus in the register | `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv` | 2026-09-12 | 2026-09-17 | yes |
| 10 | B02 Monte Carlo (this log, `datasets/b02_model.py`): R07's form with the residual mixture re-weighted for the lower tail — persistence N(4.85, 0.55) 0.45 / momentum N(5.35, 0.55) 0.15 / **AR(1) reversion N(4.37, 0.94) 0.25** (the fitted rule and its innovation sd, claim 3) / lap-and-proxy reversion N(3.6, 0.7) 0.15; same mix and FX mixtures: **P(≤ 2.0) 0.176**, median +3.09, P(≥ 4.4) 0.106 (R07 check), E[reported \| ≤ 2.0] +1.33, P(≤ 2.5) 0.30, P(≤ 1.0) 0.04, P(≤ 0) 0.006. Conditionals: FX ≤ −1.0 (17% of the mass) → 0.43; FX in (−1.0, −0.2) (49%) → 0.17; FX ≥ −0.2 (34%) → 0.06; residual ≤ 3.6 (13%) → 0.72, 3.6–4.5 (27%) → 0.24, > 4.5 (60%) → 0.03. Sensitivities: residual all persistence 0.08, all momentum 0.03, all AR(1) 0.25, all mean-rev 3.6 0.49; R07's weights 0.17; reversion-heavy (0.30/0.10/0.35/0.25) 0.24; FX all midpoint 0.15, all baskets 0.06, all euro 0.35; mix centre −0.98 (H fills) 0.14, −1.45 (geo band low) 0.25, −1.75 (LatAm mapped at the low end) 0.33; mix sd 0.6 → 0.20. Gaussian routes on the card: midpoint N(3.43, 0.93) 0.06 (bias-corrected 0.03; decel-quarter RMSE 1.25 → 0.13); euro N(2.74, 1.09) 0.25; baskets N(4.12, 0.83) 0.005. Sequential route (2Q26 +5.3 + ΔFX −1.7 + the 2023–25 Q2→Q3 ex-FX steps −1.5/−1.0/+1.0): 2.1 / 2.6 / 4.6, P(≤ 2.0) 0.21 at sd 1.3 | `datasets/b02_model.py`, `b02_results.csv` | 2026-09-17 | 2026-09-17 | yes |
| 11 | Sensitivities for the impact table: 1pt of 3Q26 ADR ≈ $1.71 ≈ $259M GBV ≈ $46M of 3Q26 revenue (implied-take-rate convention; recognition mostly lands in 4Q26 through the kernel, ⅔ × GBV × 12.03%); 1pt of 4Q26 ADR ≈ $30M revenue; 1pt of FY27 revenue growth ≈ $158M; margin 0.59pp per 1pt of 2H26 revenue held, 0.66 FY27; FY27 EPS $0.0014 per $M EBITDA; stock +0.40–0.48 turns per point of forward growth, ~$9–10/turn; the reaction function carries no ADR term; management guided 3Q26 GBV "mid teens", which at the team's 146.8m nights needs ADR ≈ +4.6% for +15% and reads as a GBV miss at ≤ +2.0 (GBV ≈ +12%) | `docs/pitch-forecasts/00_BRIEF.md`; R07 claim 11; H card §1 item 7, §2.4 | 2026-09-16 / 2026-09-12 | 2026-09-17 | yes (impact only) |
| 12 | No Polymarket or Kalshi market on ADR (scans 2026-09-17T08:03:45Z: price ladders, resolved Q2 GBV brackets, the Q3 nights ladder only); web pass found nothing on Airbnb pricing since 8 Sep | `sources/polymarket_search_Airbnb_20260917T080345Z.json`; `sources/kalshi_markets_KXABNB_open_20260917T080345Z.json`; `sources/web_queries_2026-09-17.md` | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing sources: R07 and the computed tables (17 Sep, same day); the card and mix inputs are 11–12 Sep (5–6 days, under the 7-day cap); the STR weekly is 5 Sep (12 days; direction only, no weight).

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill and schema, example log; R07 log, JSON, `r07_model.py`, `r07_results.csv`; C02, C04, R05, R01 logs (read-only)
2. [repo] `docs/adrv3/SYNTHESIS.md` (via R07's extract); `research/notes/q3nowcast/H_3q26-adr-card.md` §1–2; `docs/adrq3/SYNTHESIS.md` §2–4 (via R07 claims 7, 9)
3. [repo, pandas] `data/processed/q3nowcast/H/adr_history_components.csv` (all 14 rows); `data/processed/adrv3/K/K4_residual_nowcast.csv`; `data/processed/adrv3/P/adr_card_v3.csv`, `P1_card_v3_backtest_paths.csv` (t2 target, three estimators)
4. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` adr_yoy_pct and adr_usd_seq rows (22); `02_guidance_tells.csv`; `data/processed/abnb_driver_history_quarterly.csv` (adr, adr_yoy_pct, fx_pts)
5. [repo] `data/processed/q3nowcast/G/str_weekly_us_3q26.csv`, `G_feature_readings_3q26.csv`; `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv` (via R07 claim 8)
6. [Polymarket public-search] Airbnb; [Kalshi API] KXABNB open (2026-09-17T08:03:45Z, saved)
7. WebSearch: Airbnb news (neutral, shared)
8. WebSearch: STR CoStar US hotel ADR RevPAR week ending September 12 2026 — latest published week ending 5 Sep (ADR +6.1%, already in the repo); week ending 12 Sep not yet published
9. WebSearch: US travel demand consumer September 2026 hotels airlines bookings softening (shared with B01) → WebFetch nerdwallet.com travel-price-tracker (August CPI hotels +2.9%)
10. [python] `datasets/b02_model.py` → `b02_results.csv`, `b02_history.csv`, `b02_v3_errors_by_direction.csv`, `b02_modest_increase_record.csv`
11. WebSearch: Airbnb ABNB this week (final 72-hour neutral recency check, shared) — nothing on pricing or ADR

WebSearch calls charged to this question: 2 (query 8 and a share of the shared queries); batch total 5 of 15.

## 3. Leading Hypothesis Entities
Airbnb, ADR, like-for-like pricing residual, FX estimator, euro fit, regional baskets, geographic mix, LatAm, Bloomberg MODL, 3Q26 shareholder letter, "moderate increase in ADR"

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Residual holds near 4.85 and FX lands near the midpoint: reported ≈ +3.1 to +3.4, the threshold 1.1–1.4pp away | leading No path (≈0.60 of the mass at residual > 4.5, where P(Yes) is 0.03) | claims 1, 3: the residual's one-quarter falls have never exceeded 1.47pp; the last_q rule beats naive on the dollar target |
| The euro fit is the right FX estimator for 3Q26 (−1.12): card +2.7, threshold 0.7pp away | the main Yes path (0.25 FX weight; P(Yes) 0.35–0.43 on that branch) | claim 6: the euro fit won the 2022 dollar-surge era, the baskets 2024–26; the disclosed FX effect on 5 Nov scores this directly |
| Residual mean-reverts (AR(1) 4.37 with innovation sd 0.94; lap of the 3Q25 US RNPL step 3.9; 2023–25 mean 2.4) | kept, 0.40 of the residual mass across two branches | claims 3, 8: hotel ADR to +0.6% and lodging CPI to +2.9% point that way but no proxy beats naive; the RNPL mix into larger homes is the residual-side positive the decomposition cannot see |
| Geographic mix drag larger than −1.43 (LatAm +27.5% nights) | kept as the one-sided sensitivity (−1.45 → 0.25, −1.75 → 0.33) | claim 7: measured split, unvalidated mapping; the September dumps refresh it |
| The component build is biased *high* into decelerations (mirror of its 1H26 low bias), fattening the lower tail | tested and not supported (claim 5: decel-quarter bias +0.07, n 5) | the symmetric RMSE is kept; no extra tail mass |
| "Moderate increase" sentences printed ≤ +2.0 in 2 of 5, so P ≈ 0.4 | discarded as a raw rate, kept as the base-rate reference class before regime conditioning | those prints sat on residuals of 2.1–2.8 and FX −0.6 to −1.1 (claim 4) |
| A Street-derived ADR (+4.4 at guide-consistent nights) rules out ≤ 2.0 | discarded | comparison column only; assumes an unchanged take rate on a revenue mean |
| A 3Q25 base restatement flips resolution | tail < 1% | convention 2 |

## 5. Independent Estimates
- base_rate_estimate: 0.12 — reference classes: reported ≤ +2.0 in 5 of 14 quarters since 1Q23 (0.36) but 0 of 7 with FX ≥ −0.5 and 0 of 4 with a residual ≥ 3.5 (Laplace 1/6 and 1/9); management's "modest/moderate increase" sentences printed ≤ +2.0 in 2 of 5, all on residuals of 2.1–2.8 with an FX headwind (claim 4); regime-conditioned on residual 4.85 and FX ≈ −0.4 to 0.10–0.14 (the 1Q23 case shows a 3.5 residual can print +0.2 only with FX −2.8) → 0.12
- decomposition_estimate: 0.18 — the B02 Monte Carlo (claim 10) at 0.176, with the mix-centre risk one-sided (0.14 at the H fills, 0.25 at the geo band low) and the sequential route at 0.21; the Gaussian-on-the-card routes bracket it (0.03–0.13 midpoint, 0.25 euro, 0.005 baskets)
- anchor_estimate: 0.07 — Bloomberg MODL 3Q26 ADR mean +3.4% with range +1.4 to +4.6 (n 26, claim 9): range as ±2 sd gives sd 0.8 → P(≤ 2.0) 0.04; at the card's realised RMSE 0.93 → 0.066; taken as 0.07 because analyst dispersion understates realised error and the low estimate (+1.4) sits below the threshold
- anchor_value: 0.07 (Bloomberg MODL Standard Consensus, screenshot 12 Sep 2026, n 26: mean $177.06, low $173.71)
- final_estimate: 0.18 (credible interval 0.10–0.30)
- final_minus_anchor: +11 points. Independently derived: the anchor is a dispersion read on a consensus that has no ADR error record; the final is the team's structural model whose FX-estimator branch (euro fit, 0.25) and residual-reversion branches (0.40) the Street's dispersion cannot represent, plus the one-sided geographic-mix risk. The three estimates disagree by 11 points; the disagreement is whether the euro fit and a residual turn are live possibilities (the model says 0.25 and 0.40 by weight) or curiosities (the base rate and the Street). Versus R07's companion 0.17: the extension (AR(1) reversion branch with the fitted innovation sd, the decel-quarter error check, the LatAm mix sensitivity) moves the model by +0.004 and the judgement by +0.01; the number is the same to the audit's precision, which is itself the finding — the lower tail is an FX question first and a residual question second, exactly as R07 said of the upper tail

## 6. Final Numbers
**Binary.** P(3Q26 reported ADR ≤ +2.0% y/y, ≤ $174.72) = **0.18**, credible interval **0.10–0.30**.
Companion probabilities from `datasets/b02_results.csv` (model values; the final applies no lift): P(≤ +2.5%) 0.30; P(≤ +1.0%) 0.04; P(≤ 0) 0.006; median +3.1%; E[reported \| ≤ 2.0] = +1.33% ($173.6). Conditional on the disclosed FX effect: FX ≤ −1.0 (euro right, 17% of the mass) → 0.43; FX ≈ −0.4 (−1.0 to −0.2) → 0.17; FX ≥ −0.2 (baskets right) → 0.06. Conditional on the ex-FX letter integer (model ex-FX = mix + residual): "2%" or lower → Yes whenever FX ≤ +0.5 (≈ 0.9); "3%" → Yes needs FX ≤ −1.0 (≈ 0.17); "4%" or higher → ≈ 0.
Coherence with R07: the same model gives P(≥ 4.4) 0.11 (R07 quotes 0.17 after its acceleration lift); the two tails are two-sided around a +3.1 median with the lower tail the fatter by weight (0.18 vs 0.17 quoted) because the reversion branches sit closer to the threshold than the momentum branch does.
Extreme-probability gate: not triggered.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Residual mixture 0.45 persistence / 0.15 momentum / 0.25 AR(1) / 0.15 mean-rev | R07's weights (0.55/0.20/0/0.25): 0.17; reversion-heavy (0.30/0.10/0.35/0.25): 0.24; all persistence: 0.08; all AR(1): 0.25; all mean-rev 3.6: 0.49 |
| FX mixture 0.50 midpoint / 0.25 baskets / 0.25 euro | all midpoint: 0.15; all baskets: 0.06; all euro: 0.35 |
| Mix-term centre −1.15 (J3 fills) | −0.98 (H fills): 0.14; −1.45 (geo drag band low): 0.25; −1.75 (LatAm at the low end of the mapping): 0.33; mix sd 0.35 → 0.6: 0.20 |
| Card walk-forward RMSE 0.93 applied symmetrically (decel-quarter bias +0.07) | decel-quarter RMSE 1.25 on the midpoint card: 0.13; bias-corrected centre 3.74: 0.03 |
| Sequential route sd 1.3 on the Q2→Q3 ex-FX step | sd 1.0: 0.15; sd 1.6: 0.25 |
| Threshold on the cent figure | letter dollar figure "$175" counted as No / "$174" as Yes: ±0.02 |

Pre-mortem ("it is 5 Nov and ADR printed +2.0% or less"): (1) the euro fit was right (FX ≈ −1.1) and the residual slipped to ~4.3 (the AR(1) point): reported ≈ +2.0 — the single most likely Yes path, priced at 0.43 on a 0.17-weight branch; (2) LatAm and APAC nights (+27.5 / +10.0 QTD on the stays index) pulled the geographic-mix drag to −1.7 or worse while the party-size term flattened — priced at 0.25–0.33 on the mix-centre rows, the one input the September dumps will move; (3) the 4Q25 bundle step in the residual (+0.9) lapped early through the July RNPL cohort's different mix, taking the residual to the "lap only" 3.9 — inside the reversion branches; (4) hotels' collapse to +0.6% ADR in late August was the demand signal the nine failed proxies could not carry (a genuine pricing turn) — inside the mean-rev 3.6 branch at 0.15. "It printed +3.3% and the memo carried 0.18": the base case; the memo should say so. Asymmetry: a Yes here is also a GBV miss against "mid teens" (claim 11) and lowers the 3Q26 revenue print through the kernel, so it couples with C01/S01 in the short's favour; a confident No that resolved Yes would have left the memo's ADR line one-sided the wrong way, which is why the interval reaches 0.30.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-09-30 | September Inside Airbnb dumps: E regional split and I1b party size re-run; P1 card refresh; freeze the week of 21 Sep | Geographic drag ≤ −1.6 → 0.25; party size ≤ +1.0% capacity → +0.03; both benign (drag ≥ −1.3, party ≥ +1.5%) → 0.14 |
| 2026-09-17 to 2026-10-31 | EUR/USD and the four regional baskets to quarter-end (FRED H.10); B_fx_translation_schedule refresh | Euro fit and baskets converge below −0.8 → 0.30; above 0 → 0.08 |
| weekly to 2026-11-04 | STR/CoStar US hotel ADR weeklies (September, October); September lodging CPI (13 Oct) | Hotel ADR y/y ≤ +1% through September and lodging CPI ≤ +2.5 → +0.02 (direction only, ratio ≥ 1.03); no action above +3% |
| 2026-10-02 | Prelim memo due | Quote 0.18 (0.10–0.30) with the FX-conditional table, paired with R07's 0.17 so the ADR line reads two-sided |
| 2026-10-15 to 2026-11-03 | Sell-side previews; any management remark on ADR or "price appreciation" | A management "ADR roughly flat" or "mix headwind" remark → 0.35; "moderate increase" repeated → hold |
| 2026-11-05 (after close) | 3Q26 release: ADR ($), FX effect (pp), ex-FX integer, regional ADR; run `P2_score_sheet.py` | Resolve on $174.72; audit read: FX ≤ −1.0 implied pre-print P ≈ 0.43, FX ≈ −0.4 ≈ 0.17, FX ≥ −0.2 ≈ 0.06 |

## 9. Impact
If the event happens (E[reported \| ≤ 2.0] = +1.33% vs the card's +3.3%: **−2.0pt of ADR**, $173.6 vs $176.9; taken as persisting into 4Q26 at the same margin under the card's +3.8–4.2%):

| Line | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | ADR and nights are treated as independent lines (the card conditions on the team nights baseline); a mix-driven ADR miss with LatAm nights strong would coincide with *higher* nights, not modelled |
| 4Q26 nights (pts) | 0 | — |
| ADR (pts) | **−2.0** | claim 10; 3Q26 GBV −$518M (2.0 × $259M); GBV growth ≈ +12% vs the "mid teens" guide — a visible miss |
| 4Q26 revenue ($M) | **−100** | kernel lag on the 3Q26 GBV shortfall (⅔ × $518M × 12.03% ≈ −$42M) plus −2.0pt of 4Q26 ADR persisting (≈ −$60M, claim 11); 3Q26 revenue itself −$92M on the implied-take-rate convention (recognition mostly lands in 4Q26) |
| FY27 revenue ($M) | **−316** | −2.0pt × $158M per point of FY27 growth (the ADR level carries) |
| FY26 adj. EBITDA margin (pp) | **−0.7** | 2H26 revenue −~$192M (3Q26 −92, 4Q26 −100) ≈ −2.4% of 2H26 revenue × 0.59pp held ≈ −1.4pp of 2H26 ≈ −0.7pp of FY26 — enough on its own to put the 35.5% floor at risk (break-even shortfall $50–75M, C04 claim 10) |
| FY27 adj. EBITDA margin (pp) | **−1.3** | −2.0% of FY27 revenue × 0.66pp held (ADR revenue carries only merchant-fee cost) |
| FY27 EPS ($) | **−0.44** | −$316M of EBITDA (held) × $0.0014 |
| Stock ($/share) | **−12** | −2.0pt of forward growth × 0.40–0.48 turns × $9–10 ≈ −$8.4 plus the FY27 EBITDA level (−$316M × ~16x / 620m ≈ −$8.2), haircut to −$12 because the reaction function carries no ADR term (claim 11); not haircut further because a ≤ +2.0 print is also a GBV miss against the guide, which the tape does price |
| **EV = P × stock** | **0.18 × −$12 ≈ −$2.2/share** | **Material** (≥ $1/share): keep in the memo's bonus list, paired with R07 (≥ +4.4%, P 0.17, +$7) so the ADR line reads two-sided with the downside the larger; the memo's own ADR ex-FX assumption (+2.5% then flat in the short case) is inside this tail |

RESUME: the next agent (audit response) should re-run `datasets/b02_model.py` (seconds) and attack (1) the four residual weights (0.45/0.15/0.25/0.15), which span 0.08–0.49 at the extremes and 0.17–0.24 across the two stated alternatives; (2) the FX weights, which the disclosed FX effect will score (0.06–0.35 across the single estimators); (3) the mix-centre choice (−1.15 vs the measured −1.43 geo drag plus +0.80 party size, i.e. −0.98 with the H fills), which the September dumps refresh; (4) whether the decel-quarter error split (n 5) justifies the symmetric RMSE. After the dumps land, re-run the P1 card and this model before the 21 Sep freeze.
