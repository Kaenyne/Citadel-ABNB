# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A10). Companion questions: R04 `risk-single-fee-take-rate-accretion-stated`, R05 `risk-q3-margin-sandbagged`; mirror question B02 `bonus-adr-residual-reverts` (≤ +2.0%), batch A14. Reused as inputs: ADR v3 (`docs/adrv3/SYNTHESIS.md`, `research/notes/adrv3/`), ADR Q3 nowcast (`docs/adrq3/`), the H card (`research/notes/q3nowcast/H_3q26-adr-card.md`), C11 (GBV/take-rate coupling). Reproduction: `datasets/r07_model.py` (numpy/pandas, seed 20260917, n 400,000; seconds).

## 0. Metadata
- question_name: risk-adr-residual-persists
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § R07)
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
Will 3Q26 reported ADR growth print ≥ +4.4% y/y (consensus +3.4%; team +3.3%)?
### Resolution Criteria
Yes if 3Q26 ADR ÷ $171.29 − 1 ≥ 0.044 (≥$178.83). Resolution 5 Nov 2026.
### Fine Print
(none beyond the registry header conventions.)

Conventions adopted: (1) "reported ADR" is the letter's GBV-per-night figure as printed (the letter prints ADR to the dollar; the 10-Q/KPI table to the cent where given — the cent figure governs, else the dollar figure; $178.83 rounds to $179, so a letter print of "$179" with an unrounded value of $178.50–178.82 would be a No on the cent basis — a measure-small edge case carried inside the sd); (2) the base is the printed 3Q25 ADR $171.29 as the question states, not a restated figure; (3) ADR here is Nights-and-Seats-basis GBV over nights and seats, as reported (Experiences/Services dilution is inside the card's "new business" term); (4) if the print date moves, the same release on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Card v3 (11–12 Sep): 3Q26 reported ADR +3.3% ($176.9) pre-registered form, +3.4% ($177.2) with the K mechanics line; central band +1.9 to +4.6% (+2.0 to +4.8 with K); under the single FX estimators +2.6/+2.7% (euro fit, FX −1.12) and +4.0/+4.1% (baskets, FX +0.26); midpoint FX −0.43. Decomposition of ex-FX +3.9%: geographic mix −1.43 (band −1.57 to −0.94), party size +0.80 (+0.53 to +1.00), length of stay +0.06, new-business dilution −0.48, interaction −0.10, fee mechanics +0.17 (0.00 to +0.93), unobserved like-for-like pricing residual +4.85 (band 2.40 to 4.85). 4Q26 +3.8/+4.2% | `docs/adrv3/SYNTHESIS.md` §1, §4; `data/processed/adrv3/P/adr_card_v3.csv`; `research/notes/adrv3/K_residual-decomposition-fee-migration.md` | 2026-09-11 / 2026-09-12 | 2026-09-17 | yes |
| 2 | Residual history (H reconstruction, pp of ex-FX ADR): 1Q23 3.48, 2Q23 2.47, 3Q23 1.01, 4Q23 0.83, 1Q24 2.26, 2Q24 3.23, 3Q24 2.08, 4Q24 2.76, 1Q25 2.23, 2Q25 1.91, 3Q25 2.82, 4Q25 3.70, 1Q26 4.38, 2Q26 4.85 (2023–25 mean 2.40); the last four moves +0.9, +0.7, +0.5 — a rising series whose step ties with the RNPL share and a 4Q25 dummy (r 0.97, 0.89, n 14); K's 3Q26 scenarios: cohort mechanics 5.02 (band 4.09–5.96), last_q 4.85, persistence 4.62, AR(1) 4.37, lap-only 3.93, lap + tranche 2 4.10, mean reversion 2.40; the fitted cohort model 7.6 is a reductio | `data/processed/q3nowcast/H/adr_history_components.csv`; `data/processed/adrv3/K/K4_residual_nowcast.csv`; K note §1 points 3–6 | 2026-09-12 / 2026-09-11 | 2026-09-17 | yes |
| 3 | Reported ADR y/y 1Q23–2Q26 (n 14): ≥ +4.4% in 4 (3Q25 +4.7, 4Q25 +5.9, 1Q26 +9.0, 2Q26 +5.3), every one with an FX tailwind of +1.3 to +5.0pp; 0 of 7 quarters with FX ≤ 0; disclosed ex-FX has never exceeded 4% (integer) since 2Q22's +7% (the reconstructed 2022 ex-FX prints were post-COVID rebounds); ex-FX adjusted to 3Q26's midpoint FX (−0.43) ≥ 4.4 in 0 of 14 | `datasets/r07_history.csv` (from `adr_history_components.csv`); `research/notes/2026-09-07_adr-decomposition.md` §2 | 2026-09-17 | 2026-09-17 | yes |
| 4 | Management's ADR guidance record (ledger metric adr_yoy_pct, 21 rows): "modest/moderate increase" sentences and outcomes — 2Q24 "modestly up" → +2.1, 3Q24 "increase modestly" → +1.4, 4Q24 "increase modestly" → +0.9, 3Q25 "increase modestly, primarily driven by FX" → +4.7 (FX +2.7), 4Q25 "modest increase ... price appreciation and FX" → +5.9 (FX +2.9); 3Q26 guide "a moderate increase in ADR due to mix shift and price appreciation" (no FX credited). Floors were met 12 of 12; two ≥ +4.4 prints, both FX-driven; on an FX-neutral basis 0 of 5 "modest" sentences reached +4.4 | `data/processed/overnight/02_guidance_ledger.csv` rows 100, 108, 118, 147, 156, 185; `data/raw/letters/2Q26_d70413dex991.htm` | 2024-05-08 to 2026-08-06 | 2026-09-17 | yes |
| 5 | Card v3 walk-forward errors on reported dollar y/y (P1 paths, 1Q24–2Q26, n 10; with the K line): midpoint FX RMSE 0.93pp, bias −0.31 (model low); euro 1.09 / −0.38; baskets 0.83 / −0.24; errors: 1Q24 −1.61, 2Q24 −0.91, 3Q24 +1.63, 4Q24 −0.50, 1Q25 +0.42, 2Q25 +0.16, 3Q25 −1.25, 4Q25 −0.09, 1Q26 −0.64, 2Q26 −0.30; the rule "is late by 0.5 to 1.4 pp in five accelerations and early by 1.15 in the one deceleration"; the H component build was biased ~1.5pp low in 1H26 (RMSE 1.29 vs naive 0.82, n 9); v3 beats naive at 0.87–0.92 on the dollar target, ties on the integer ex-FX target | `data/processed/adrv3/P/P1_card_v3_backtest_paths.csv`; `datasets/r07_v3_errors.csv`; `docs/adrv3/SYNTHESIS.md` §1, §3; `research/notes/q3nowcast/H_3q26-adr-card.md` §1 point 4 | 2026-09-12 | 2026-09-17 | yes |
| 6 | FX estimator: midpoint of the euro fit and the regional baskets, RMSE 0.33pp on the scored window (euro 0.46, baskets 0.42), 0.41 on 2Q22–2Q26; the two single estimators win in different eras (euro in the 2022 dollar surge, baskets in 2024–26); 3Q26 FX −0.43 (euro −1.12, baskets +0.26); "the 1.4 pp spread between the two single estimators remains the largest controllable uncertainty on the ADR line". Under the baskets estimator the card is +4.1% and the threshold is 0.3pp away; under the euro fit it is 1.7pp away | `data/processed/adrv3/N/N1_fx_choice_card.csv`, `N1_fx_estimator_window_summary.csv`; `data/processed/overnight2/B/B_adr_fx_estimator_backtest.csv` | 2026-09-11 | 2026-09-17 | yes |
| 7 | Measured 3Q26-to-date mix terms (ADR Q3 nowcast): party size booked capacity +1.35% y/y on 2.05m vintage-matched reviews → +0.80pp (NA +2.5%, EMEA +0.7, APAC +1.6, LatAm −0.1), unchanged vs 2Q26 (+0.87) and 3Q25 (+0.81); geographic mix −1.43pp (E regional split NA +6.9 / EMEA +0.9 / LatAm +27.5 / APAC +10.0), a larger drag than assumed; length of stay +0.06; the three measured terms net −0.57. RNPL's mix into larger entire homes is a residual-side positive the decomposition does not measure (K point 4; D016/D033/D045) and the bundle's ADR contribution was ~1pp in 4Q25 and 1Q26 by the GBV-minus-nights gap (D014, D032) | `docs/adrq3/SYNTHESIS.md` §2; `docs/adrv3/SYNTHESIS.md` §3 | 2026-09-11 | 2026-09-17 | yes |
| 8 | Bloomberg MODL 3Q26 ADR (12 Sep, n 26): low $173.71 (+1.4%), mean $177.06 (+3.4%), high $179.12 (+4.6%); the threshold $178.83 sits at the 96th percentile of the analyst range (one or two of 26 estimates at or above it); 3Q26 GBV mean $26,375M on nights 148.9m. No vendor publishes an ADR consensus in the register; the MODL screen is the only one | `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv` | 2026-09-12 | 2026-09-17 | yes |
| 9 | STR/CoStar US hotel ADR y/y through 3Q26: July +5.7% (World Cup; NYC +24%), week ending 8 Aug +4.1, 15 Aug +3.5, 22 Aug +2.3, 29 Aug +0.6 ("slowest RevPAR growth since early April"), 5 Sep +6.1 (Labor Day calendar shift, "not a clean demand signal"); the ADR Q3 nowcast noted "hotel ADR growth collapsing to +0.6% by mid-August and lodging CPI falling from +4.9 to +3.1 both point" toward residual mean reversion, though none of nine external price proxies beats naive against the residual (best ratio 1.03) | `data/processed/q3nowcast/G/str_weekly_us_3q26.csv`; `docs/adrq3/SYNTHESIS.md` §3–4; web pass (week ending 12 Sep not yet published) | 2026-08-26 to 2026-09-14 | 2026-09-17 | no |
| 10 | Structural Monte Carlo (this log, `datasets/r07_model.py`): reported = mix N(−1.15, 0.35) + residual mixture [persistence N(4.85, 0.55) 0.55 / momentum N(5.35, 0.55) 0.20 / partial mean reversion N(3.6, 0.7) 0.25] + FX mixture [midpoint N(−0.43, 0.33) 0.50 / baskets N(0.26, 0.42) 0.25 / euro N(−1.12, 0.46) 0.25]: P(≥4.4) 0.108, median +3.1%, P(≤2.0) 0.17 (B02). Reruns: residual all persistence 0.10, all momentum 0.24, all mean reversion 0.01; FX all midpoint 0.07, all baskets 0.27, all euro 0.02; mix centre −0.98 (H fills, the card's own) 0.14; mix at the geo-drag low −1.45 → 0.06. Gaussian on the card: midpoint N(3.43, 0.93) 0.15, bias-corrected N(3.74, 0.93) 0.24; baskets N(4.12, 0.83) 0.37 (bias-corrected 0.48); euro N(2.74, 1.09) 0.06 (0.12) | `datasets/r07_model.py`, `r07_results.csv` | 2026-09-17 | 2026-09-17 | yes |
| 11 | Sensitivities for the impact table: 1pt of 3Q26 ADR ≈ $1.71 ≈ $259M GBV ≈ $46M of 3Q26 revenue (implied-take-rate convention; recognition lags, most of a 3Q26 ADR surprise reaches 4Q26 revenue through the kernel); 1pt of 4Q26 ADR ≈ $221–231M GBV ≈ $30M revenue; 1pt of FY27 revenue growth ≈ $158M; margin per 1pt of revenue: 2H26 0.59pp held, FY27 0.66pp held; FY27 EPS $0.0014 per $M of EBITDA; stock +0.40–0.48 turns per point of forward growth, ~$9–10/turn; the reaction function carries no ADR term (nights sign and guide-vs-Street only) | `docs/pitch-forecasts/00_BRIEF.md` sensitivities; `research/notes/q3nowcast/H_3q26-adr-card.md` §2.4; `research/notes/reverse_dcf/C_reaction-function.md` | 2026-09-16 / 2026-09-13 | 2026-09-17 | yes (impact only) |
| 12 | C11 coupling: at ADR +4.4 the take-rate question's base P moves from 0.87 to 0.71 (GBV +$285M); the Kalshi nights median 148.2m (+10.9%) with ADR +4.4 implies GBV ≈ $26.5bn, the top of management's "mid teens" | `../q3-take-rate-above-1810/forecasts/2026-09-17-forecast.json` sensitivity; `sources/kalshi_markets_KXABNB_open_20260917T033427Z.json` | 2026-09-17 | 2026-09-17 | no |
| 13 | No Polymarket or Kalshi market on ADR (scans 2026-09-17T03:34:27Z); web pass (3 WebSearch calls attributable, one specific) found only STR data already in the repo and nothing on Airbnb pricing since 8 Sep | `sources/polymarket_search_Airbnb_ADR_20260917T033427Z.json`; `sources/web_queries_2026-09-17.md` | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] read `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill and schema, example log; C01, C11, C04, C09, S01 logs (read-only)
2. [repo] `docs/adrv3/SYNTHESIS.md` (all); `docs/adrq3/SYNTHESIS.md` §1–4; `research/notes/q3nowcast/H_3q26-adr-card.md` §1–2; `research/notes/2026-09-07_adr-decomposition.md` §0–4; `research/notes/adrv3/K_residual-decomposition-fee-migration.md` §1
3. [repo] `data/processed/q3nowcast/H/adr_history_components.csv`, `adr_exfx_backtest.csv`, `adr_forecast_card.csv`; `data/processed/adrv3/K/K4_residual_nowcast.csv`; `data/processed/adrv3/P/adr_card_v3.csv`, `P1_card_v3_backtest.csv`, `P1_card_v3_backtest_paths.csv`; `data/processed/adrv3/S/rescore_v2.csv`, `error_attribution_v3.csv`, `walk_forward_paths.csv`; `data/processed/adrv3/N/N1_*.csv`; `data/processed/overnight2/B/B_adr_fx_estimator_backtest.csv`, `B_fx_translation_schedule_refresh.csv`
4. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` rows metric ∈ {adr_yoy_pct, adr_usd_seq} (22 rows); `data/processed/abnb_driver_history_quarterly.csv` (adr, adr_yoy_pct, fx_pts)
5. [repo] `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv` (MODL ADR); `data/processed/q3nowcast/G/str_weekly_us_3q26.csv`
6. [Kalshi API] KXABNB open markets; [Polymarket public-search] airbnb, Airbnb Q3, Airbnb margin, Airbnb ADR (2026-09-17T03:34:27Z)
7. [WebSearch] Airbnb news (neutral, shared)
8. [WebSearch] STR CoStar US hotel ADR week ending September 12 2026 (latest published: week ending 5 Sep, already in the repo)
9. [python] `datasets/r07_model.py` → `r07_results.csv`, `r07_history.csv`, `r07_v3_errors.csv`
10. [WebSearch] Airbnb ABNB this week (final 72-hour neutral recency check, shared, 2026-09-17) — nothing on pricing or ADR

WebSearch calls used by this question: 3 of 5 (two shared).

## 3. Leading Hypothesis Entities
Airbnb, ADR, like-for-like pricing residual, Reserve Now Pay Later, FX estimator, euro fit, regional baskets, Bloomberg MODL, 3Q26 shareholder letter, geographic mix, party size

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Residual persists at 4.85 (the v3 rule) and FX lands at the midpoint: reported ≈ +3.4%, the threshold is 1pp away | leading, ~0.55 of the residual mass | claims 1, 2, 5: the rule beats naive on the dollar target; the residual's turns are rare |
| Residual keeps rising (+0.4–0.5 a quarter, RNPL mix into larger homes + tranche-2 reprice): 5.3–5.4 → reported +3.9% midpoint, +4.5% baskets | kept, 0.20 of the residual mass; the main Yes path with the baskets FX | claim 2's momentum (+0.9, +0.7, +0.5) and K's cohort mechanics 5.0 (band to 5.96); the rule has been late into every acceleration by 0.5–1.4pp (claim 5) |
| FX estimator: baskets is right for 3Q26 (2024–26 regime), FX +0.26 → card +4.1% | kept, 0.25 weight; P(≥4.4) 0.27–0.37 on this branch alone | claim 6: baskets win 4 of 10 scored quarters, midpoint is best on RMSE; the 3Q26 disclosed FX effect will score this directly |
| Residual mean-reverts toward 2.4–3.6 (hotel ADR slowing to +0.6%, lodging CPI decelerating, the 4Q25 bundle step lapping) | kept, 0.25 weight (and the whole of B02's mass) | claims 7, 9; the ADR Q3 nowcast's one-sided risk; contributes ~0.01 to Yes |
| Geographic mix drag larger than −1.43 (LatAm +27.5% nights) | kept as a sensitivity (0.06 at −1.45 centre) | measured split, unvalidated mapping (RMSE 0.4–0.7pp on n 10) |
| Management's "moderate increase" language implies ≥ +4% as it did for 2Q26 (+5.3%) | discarded as evidence for Yes | claim 4: the same phrase preceded +0.9 to +2.1 in 2024; the two ≥4.4 outcomes were FX-driven and FX is now ~0 |
| A Street-style derived ADR (+4.4% at guide-consistent +11% nights from the Zacks revenue mean) | discarded | comparison column only (H note §2.5); it assumes an unchanged take rate and the Zacks panel is a high outlier |

## 5. Independent Estimates
- base_rate_estimate: 0.09 — reference classes: reported ≥ +4.4 in 4 of 14 quarters since 1Q23 (0.29) but 0 of 7 with FX ≤ 0 and 0 of 14 on an FX-neutral (−0.43) basis (Laplace 1/16 = 0.06); management's five "modest/moderate increase" sentences reached +4.4 twice, both on +2.7–2.9pp of FX, 0 of 5 FX-neutral; regime-conditioned up for the four-quarter run of ≥ +4.4 reported prints and the rising residual → 0.09
- decomposition_estimate: 0.14 — structural Monte Carlo on the card's terms (claim 10): 0.11 at the J3-fill mix centre, 0.14 at the card's own H-fill centre (−0.98); the Gaussian-on-the-card routes bracket it (0.15 raw, 0.24 bias-corrected at the midpoint FX; 0.06–0.12 euro; 0.37–0.48 baskets), weighted by the N note's estimator choice → 0.14–0.20
- anchor_estimate: 0.12 — Bloomberg MODL 3Q26 ADR mean +3.4% with the analyst range +1.4 to +4.6 (n 26, claim 8): treating the range as ±2 sd gives sd 0.8 and P(≥4.4) 0.10; the threshold sits at the 96th percentile of the 26 estimates; adjusted up to 0.12 because analyst dispersion understates realised error (the card's own RMSE is 0.93)
- anchor_value: 0.12 (Bloomberg MODL Standard Consensus, screenshot 12 Sep 2026, n 26: mean $177.06, high $179.12)
- final_estimate: 0.17 (credible interval 0.10–0.28)
- final_minus_anchor: +5 points. NOT_INDEPENDENTLY_DERIVED flag: raised by the arithmetic and answered: the decomposition (0.14) is built on the team's card and its walk-forward errors, not the Street's; the final sits above both the base rate and the decomposition because the model's errors are one-sided into accelerations (bias −0.31, late in all five accelerations) and the residual has risen four quarters running, which the base rate cannot see; the anchor is the least informative of the three (the Street has no ADR error record)

## 6. Final Numbers
**Binary.** P(3Q26 reported ADR ≥ +4.4% y/y, ≥ $178.83) = **0.17**, credible interval **0.10–0.28**.
Companion probabilities from the structural Monte Carlo (`datasets/r07_results.csv`; its unconditional P(≥4.4) is 0.11, the final 0.17 lifts it ~1.5× for the model's one-sided bias into accelerations, so read the conditionals below as model values with the same lift applying): P(≥ +4.0%) 0.20; P(≥ +3.4%, the Street mean) 0.40; P(≤ +2.0%, B02) 0.17; median +3.1%. Conditional on the disclosed FX effect: FX ≥ +0.2 (baskets right, 15% of the FX mass) → 0.37 model / ~0.45 lifted; FX ≈ −0.4 (−0.6 to −0.2) → 0.06 / ~0.10; FX ≤ −1.0 (euro right) → 0.003 / ~0.01. Conditional on the ex-FX letter integer (model ex-FX = mix + residual): "5%" (ex-FX ≥ 4.5, 13% of the mass) → 0.52 (Yes whenever FX ≥ −0.1); "4%" (41%) → 0.10 (needs FX ≥ +0.4); "3%" or lower (46%) → 0.00.
Extreme-probability gate: not triggered.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Residual mixture 0.55 persistence / 0.20 momentum / 0.25 mean reversion | all persistence (4.85): 0.10; all momentum (5.35): 0.24; all mean reversion (3.6): 0.01 |
| FX mixture 0.50 midpoint / 0.25 baskets / 0.25 euro | all midpoint (−0.43): 0.07; all baskets (+0.26): 0.27; all euro (−1.12): 0.02 |
| Mix-term centre −1.15 (J3 fills) | −0.98 (card's H fills): 0.14; −1.45 (geo drag at the band low): 0.06 |
| Model bias −0.31 not applied to the centre | bias-corrected centre (3.74 midpoint): 0.24; baskets bias-corrected (4.36): 0.48 |
| Error sd 0.93 (walk-forward RMSE) | 0.7: 0.08; 1.2: 0.21 |
| Threshold arithmetic on the cent figure | letter dollar figure "$179" counted as Yes: +0.03 |

Pre-mortem ("it is 5 Nov and ADR printed +4.4% or more"): (1) the baskets FX estimator was right (FX ≈ +0.3) and the residual held at 4.85 — the card's baskets line is +4.1%, so a +0.3 residual/mix surprise did it (priced at ~0.27 on that branch, 0.25 weight); (2) RNPL's July eligibility expansion pushed more bookings into larger entire homes and the residual stepped to 5.5+ (the momentum branch, 0.20 weight); (3) party size or LOS surprised above the measured +0.80/+0.06 (the measured terms carry sd 0.35 in the model; a +0.5 surprise adds ~0.05); (4) 3Q25's base ADR was revised down in the letter (convention (2) says the question's $171.29 governs, but a resolver might use the restated base). "It printed +3.3% and the memo carried 0.17": expected; the risk is one-sided in the other direction (B02). Asymmetry: this risk couples with C11 (a high ADR lowers the take-rate P) and with GBV "mid teens" being met, so a Yes here is also a small revenue-leg positive for the print; the interval reaches 0.28 for that reason.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-09-30 | September Inside Airbnb dumps: E (regional split), I1b (party size) re-run → `I_mix_terms_3q26.csv`, P1 card refresh; freeze the week of 21 Sep | Party size ≥ +1.8% capacity → +0.03; geographic drag ≤ −1.6 → −0.03 |
| 2026-09-17 to 2026-10-31 | EUR/USD and the four regional baskets to quarter-end (FRED H.10 weekly); B_fx_translation_schedule refresh | If the euro fit and baskets converge above 0 → 0.25; below −0.8 → 0.08 |
| weekly to 2026-11-04 | STR/CoStar US hotel ADR weeklies (Sep–Oct), lodging CPI (mid-Oct) | Hotel ADR y/y ≤ +1% through September → −0.02 (weak proxy, ratio ≥ 1.03); no action above +3% |
| 2026-10-02 | Prelim memo due | Quote 0.17 (0.10–0.28) with the FX-conditional table; carry B02 as the larger one-sided risk |
| 2026-10-15 to 2026-11-03 | Sell-side previews; any management remark on "price appreciation" or RNPL mix at a conference | A management ADR "high single digits" remark → 0.35; "moderate" repeated → hold |
| 2026-11-05 (after close) | 3Q26 release: ADR ($), FX effect (pp), ex-FX integer, regional ADR; run `P2_score_sheet.py` | Resolve; audit read: FX ≥ +0.2 implied pre-print P ~0.45, FX ≈ −0.4 ~0.10, FX ≤ −1.0 ~0.01 (lifted model conditionals, §6) |

## 9. Impact
If the event happens (ADR +4.4% vs the card's +3.3%, +1.1pt; taken as persisting into 4Q26 at the same margin over the card's +3.8–4.2%):

| Line | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | ADR and nights surprises are treated as independent (the card conditions on the team nights baseline; a mix-driven ADR could coincide with lower nights, not modelled) |
| 4Q26 nights (pts) | 0 | — |
| ADR (pts) | +1.1 | 4.4 − 3.3 (claim 1); 3Q26 GBV +$285M (1.1 × $259M) |
| 4Q26 revenue ($M) | +50 | kernel lag on the 3Q26 GBV surprise (⅔ × $285M × 12.0% ≈ +$23M) plus +1.1pt of 4Q26 ADR persisting (≈ +$30M, claim 11); 3Q26 revenue itself +$51M on the implied-take-rate convention (recognition mostly lands in 4Q26) |
| FY27 revenue ($M) | +174 | +1.1pt × $158M per point of FY27 growth, i.e. the ADR level carries |
| FY26 adj. EBITDA margin (pp) | +0.35 | 2H26 revenue +~$100M (3Q26 +51, 4Q26 +50) ≈ +1.25% of 2H26 revenue × 0.59pp held ≈ +0.74pp of 2H26 ≈ +0.35pp of FY26 |
| FY27 adj. EBITDA margin (pp) | +0.7 | +1.1% of FY27 revenue × 0.66pp held (ADR revenue carries only merchant-fee cost) |
| FY27 EPS ($) | +0.24 | +$174M of EBITDA (held) × $0.0014 |
| Stock ($/share) | +7 | +1.1pt of forward growth × 0.40–0.48 turns × $9–10 ≈ +$4.6 plus the FY27 EBITDA level (~$174M × ~16x / 620m ≈ +$4.5), haircut to +$7 because the reaction function carries no ADR term and the market keys on nights (claim 11) |
| **EV = P × stock** | **0.17 × $7 ≈ +$1.2/share** | **Material, marginally** (≥ $1/share): keep in the memo's risk list as "ADR residual persists/accelerates", paired with B02 (≤ +2.0%, P ≈ 0.17, the larger downside) so the ADR line reads as two-sided with a one-sided mean-reversion skew |

RESUME: the next agent (audit response) should re-run `datasets/r07_model.py` (seconds), check the FX-estimator weights (0.50/0.25/0.25) against `N1_fx_estimator_window_summary.csv` (the number is most sensitive to this: 0.02–0.27 across the single estimators), re-read the residual mixture weights (0.55/0.20/0.25) against K's scenario table, and decide whether the model bias (−0.31, late into accelerations) should be applied to the centre, which would lift the number to ~0.24; after the September dumps land, refresh the mix terms and the K line before the 21 Sep freeze.
