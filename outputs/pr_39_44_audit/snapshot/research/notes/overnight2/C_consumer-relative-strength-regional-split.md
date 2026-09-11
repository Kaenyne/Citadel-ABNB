# C. Consumer relative strength by origin region, and the 3Q26 / 4Q26 geographic split

- **Date:** 2026-09-11. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Scripts:** `analysis/src/overnight2/C1_target_panel.py`, `C2_consumer_panel.py`, `C3_relative_strength_index.py`, `C4_tests.py`, `C5_application.py`.
- **Outputs:** `data/processed/overnight2/C/`.
- **Asked:** build a consumer relative strength index by origin region and use it to forecast which regions accelerate or decelerate against the total in 3Q26 and 4Q26, and what that does to total nights and to reported ADR through mix.

## 1. Bottom line

1. **The index is built and it works as a measurement, but it fails as a forecast of the regional split, and it fails with the wrong sign.** In the disclosure era that matters (4Q24 to 2Q26, 28 region-quarters), a region whose consumer is relatively stronger than the global origin-weighted consumer grows **slower** than the total, not faster: slope **-5.8pp of growth differential per z unit**, t -3.38, permutation p 0.0098, leave-one-out RMSE 1.58pp against a naive region-mean 1.77pp, an 11% improvement. The sign survives dropping any one region (slope -4.5 to -10.1, t -2.6 to -3.4) and survives controlling for mean reversion in the differential (t -3.09 with the lagged differential in the regression). The demand-pull hypothesis the workstream was built to test is rejected in this sample.
2. **The most likely reason is confounding with the product cycle and with comps, and 28 observations across 4 regions cannot separate it from a genuine trade-down mechanism.** The two largest relative moves in the window are the US consumer weakening through 2025 and 2026 exactly while North America received the Reserve Now Pay Later and fee-redesign lift, and the Latin American consumer strengthening into 2026 exactly while the LatAm comp tightened. Both push the slope negative for reasons that have nothing to do with consumer demand. A trade-down reading, where travellers facing a weaker local consumer shift toward Airbnb and toward domestic and nearby stays, is economically coherent and is what Airbnb's own language implies in places, but it is not identified here.
3. **The index would have called North America wrong twice, and both misses are large.** It had the NA consumer at or above its own mean through the 2025 slowdown and below its own mean through the 2026 reacceleration to a three-year-high high-single-digit print. It got LatAm, APAC and EMEA right on direction, so 3 of 5 episodes, with the two misses in the region that carries 30% of nights.
4. **What the index does say, and it is worth saying on its own:** on data through August 2026 the **United States consumer composite is the weakest of the large origin markets** (-0.19 z in July and August, against +0.20 in 2024 and -0.02 for 2026 to date), while the UK (+1.00), Mexico (+0.75), Korea (+0.71) and Japan (+0.70) are the strongest. Regionally, 3Q26 to date reads **NA -0.30, EMEA +0.16, LatAm +0.15, APAC -0.02** in relative z. The 2026 year-to-date relative readings are **LatAm +0.36, EMEA -0.01, APAC -0.02, NA -0.19**. If the demand-pull sign is the true economics, a weakening US consumer stacked on top of the RNPL anniversary is a double headwind to NA in 3Q26 and 4Q26, which supports the team's deceleration base case. If the fitted negative sign is the true economics, NA gets relative support. **The index cannot tell you which, so it must not set the base case.**
5. **The split this workstream would put up is within a point of persistence everywhere except EMEA.** 3Q26: NA 6.7, EMEA 5.9, LatAm 19.5, APAC 17.1 (band +/- 1.5pp), against persistence of 6.6 / 6.6 / 18.6 / 16.6 and WS10's cells of 7 / 8 / 18 / 17. 4Q26 the same relative pattern at a lower anchor and a +/- 2.5pp band. The only non-trivial call is that **EMEA is the relative loser in 3Q26**, which comes entirely from the negative fitted sign applied to the strongest EMEA consumer reading in the sample. That is the weakest part of the output and should be read as a flag, not a forecast.
6. **A concrete, independent correction falls out of the weighting work.** WS10's regional nights shares (LatAm 15.1%, APAC 16.3% for 3Q26) do not match the 10-K, which discloses FY2025 at LatAm 16.9% and APAC 13.1%. Re-weighting WS10's own base cells on the disclosed 10-K shares gives **3Q26 10.57% instead of 10.69% and 4Q26 10.17% instead of 10.35%**, so WS10's share error overstates its own total by 0.12 to 0.18pp before its -0.41pp calibration. The error was already flagged in `research/notes/2026-09-07_adr-decomposition.md` section 5; this is the size of it in the nights build.
7. **Geographic mix drag on reported ADR is -1.2pp in 3Q26 and -1.3pp in 4Q26** on every split tested, against the -1.58pp realised in FY2025 and -1.24pp in FY2024. The drag is insensitive to which split you believe (range -1.12 to -1.25pp across all six split-by-weight combinations), because the mix term is dominated by the structural NA share decline and not by the quarter's regional growth differences. This is a useful negative: the regional split question, which is what this workstream set out to refine, moves reported ADR by at most 0.13pp.

## 2. Tables

### 2.1 Consumer relative strength, quarterly, z units

Region composite less the global origin-weighted composite. Positive means that region's consumer is stronger than the global Airbnb-origin-weighted consumer. Source `regional_strength_quarterly.csv`; chart `C5_relative_strength_and_differential.png`.

| Quarter | NA | EMEA | LatAm | APAC |
|---|---|---|---|---|
| 4Q24 | +0.12 | -0.06 | -0.06 | -0.01 |
| 1Q25 | +0.09 | +0.02 | -0.21 | +0.01 |
| 2Q25 | 0.00 | +0.02 | -0.05 | -0.01 |
| 3Q25 | -0.01 | +0.01 | -0.06 | +0.06 |
| 4Q25 | -0.20 | +0.01 | +0.30 | +0.05 |
| 1Q26 | -0.14 | -0.13 | +0.57 | +0.01 |
| 2Q26 | -0.15 | +0.01 | +0.29 | -0.06 |
| **3Q26 (Jul-Aug)** | **-0.30** | **+0.16** | **+0.15** | **-0.02** |
| 2026 YTD (Jan-Aug) | -0.19 | -0.01 | +0.36 | -0.02 |

Country composites for July and August 2026, for the large origin markets: GBR +1.00, MEX +0.75, KOR +0.71, JPN +0.70, CAN +0.44, ESP +0.43, CHN +0.28, BRA +0.26, ITA +0.24, FRA -0.04, USA -0.19, DEU -0.33, AUS -0.34, IND -0.82. Full set in `country_strength_monthly.csv`.

### 2.2 The target: disclosed regional nights growth less total nights growth, pp

From `C4_regression_panel.csv`, which also carries 1Q23 to 3Q24 where only Latin America and Asia Pacific were quantified.

| Quarter | NA | EMEA | LatAm | APAC |
|---|---|---|---|---|
| 4Q24 | -7.3 | -1.3 | +8.7 | +8.7 |
| 1Q25 | -5.9 | -2.9 | +13.1 | +7.1 |
| 2Q25 | -5.4 | -2.4 | +10.6 | +7.6 |
| 3Q25 | -3.8 | -3.8 | +12.2 | +6.2 |
| 4Q25 | -4.8 | -1.8 | +8.2 | +5.2 |
| 1Q26 | -1.2 | -4.2 | +8.8 | +8.8 |
| 2Q26 | -2.3 | -2.3 | +9.7 | +7.7 |

### 2.3 Tests

`C4_fits.csv`, `C4_acceleration_fits.csv`, `C4_mean_reversion.csv`, `C4_leave_region_out.csv`. Target is the growth differential, region fixed effects absorbed, permutation p shuffles the predictor within region over 20,000 draws, leave-one-out RMSE against the region-mean naive.

| Sample | Predictor | n | slope pp per z | t | within R2 | perm p | LOO model | LOO naive |
|---|---|---|---|---|---|---|---|---|
| 4Q24-2Q26 | relative z, lag 0 | 28 | **-5.80** | -3.38 | 0.306 | **0.0098** | 1.58 | 1.77 |
| 4Q24-2Q26 | relative z, lag 1 | 28 | -3.55 | -1.78 | 0.108 | 0.166 | 1.80 | 1.77 |
| 4Q24-2Q26 | relative z, lag 2 | 28 | -4.03 | -1.39 | 0.069 | 0.278 | 1.76 | 1.77 |
| 4Q24-2Q26 | 2-quarter change, lag 0 | 28 | -3.17 | -1.81 | 0.112 | 0.155 | 1.78 | 1.77 |
| 1Q24-2Q26 | relative z, lag 2 | 34 | -6.21 | -2.46 | 0.159 | 0.034 | 1.87 | 1.98 |
| 3Q22-2Q26 | relative z, lag 0 | 50 | -8.04 | -1.39 | 0.039 | 0.043 | 5.87 | 5.92 |
| 3Q22-2Q26 | 2-quarter change, lag 1 | 50 | -8.13 | -2.32 | 0.101 | 0.0010 | 5.73 | 5.92 |

Only lag 0 clears in the modern sample. Lags 1 and 2 are insignificant there, so the index is **not a leading indicator of the split**, which is the property a forecast needs. With the target switched to the **change** in the differential, the relative acceleration that the 5 November print actually trades, nothing survives in the modern sample (perm p 0.26 to 0.45, leave-one-out worse than naive), even though it looks significant on the full COVID-inclusive sample (perm p 0.0036). That contrast is the clearest evidence that the full-sample result is the 2022-2023 Asia Pacific reopening, not a consumer channel.

Mean reversion is not the explanation. In the bucket era, the lagged differential on its own carries t 1.39 and 7% of within variance; relative z keeps t -3.09 and the pair together reach 33%. On the full sample the lagged differential is strong (t 4.61) and relative z still keeps t -3.10.

Origin-country test, the only true origin-basis target Airbnb gives (`C4_origin_country_fits.csv`): 15 observations across 4 countries with at least two observations each (BRA 6, CHN 3, IND 3, MEX 2 after dropping the Japan domestic-only figure). Slope -10.4pp per z at lag 0, t -1.00, perm p 0.116; +14.4 at lag 1, t 1.22, p 0.117; -8.7 on the 2-quarter change, p 0.065. Nothing is identified. The sign is the same negative sign as the regional test, which is at least consistent, and the magnitudes are meaningless at this n.

### 2.4 Episode checks

`C4_episode_checks.csv`. Direction of the window mean against the region's own full-sample mean, actual versus index.

| Episode | Region | Actual differential vs own mean | Index relative z vs own mean | Called |
|---|---|---|---|---|
| 2025 NA slowdown (4Q24-3Q25) | NA | below (-5.62 vs -4.49) | above (+0.052) | no |
| 2026 NA reacceleration (4Q25-2Q26) | NA | above (-2.77 vs -4.49) | below (-0.167) | no |
| 2025-26 LatAm strength | LatAm | above (+10.42 vs +8.82) | above (+0.139) | yes |
| 2025-26 APAC strength | APAC | below (+7.09 vs +13.07) | below (+0.010) | yes |
| 2025-26 EMEA recovery | EMEA | below (-2.91 vs -1.67) | below (-0.011) | yes |

The APAC and EMEA hits are near-zero index readings against clear actual moves, so they are weak hits. The LatAm hit is real in level but wrong in dynamics: LatAm relative strength rose from -0.21 in 1Q25 to +0.57 in 1Q26 while the LatAm differential fell from +13.1 to +8.8.

### 2.5 Application: the 3Q26 and 4Q26 split

`C5_regional_split_forecast.csv`. The total is the team baseline (3Q26 +9.9, 4Q26 +8.9); this workstream supplies only the split, and the differentials are renormalised to be weight-zero-sum on the 10-K FY2025 shares so that they are consistent with whatever total the team carries. Comparison columns are not inputs.

| Period | Region | relative z | index split | band | persistence | WS10 base | team total |
|---|---|---|---|---|---|---|---|
| 3Q26 | NA | -0.30 | **6.7** | 5.2 to 8.2 | 6.6 | 7.0 | 9.9 |
| 3Q26 | EMEA | +0.16 | **5.9** | 4.4 to 7.4 | 6.6 | 8.0 | 9.9 |
| 3Q26 | LatAm | +0.15 | **19.5** | 18.0 to 21.0 | 18.6 | 18.0 | 9.9 |
| 3Q26 | APAC | -0.02 | **17.1** | 15.6 to 18.6 | 16.6 | 17.0 | 9.9 |
| 4Q26 | NA | -0.30 | **5.7** | 3.2 to 8.2 | 5.6 | 7.0 | 8.9 |
| 4Q26 | EMEA | +0.16 | **4.9** | 2.4 to 7.4 | 5.6 | 7.0 | 8.9 |
| 4Q26 | LatAm | +0.15 | **18.5** | 16.0 to 21.0 | 17.6 | 18.0 | 8.9 |
| 4Q26 | APAC | -0.02 | **16.1** | 13.6 to 18.6 | 15.6 | 17.0 | 8.9 |

4Q26 carries the 3Q26 macro reading forward, because no 4Q26 macro month exists on 11 September 2026, and the band widens to +/- 2.5pp to say so.

### 2.6 Implied total and the ADR mix term

`C5_total_and_adr_mix.csv`. The index and persistence splits are zero-sum by construction, so they reproduce the anchor; the informative rows are WS10's cells under the two weightings.

| Period | Split | Weights | Implied total nights y/y | ADR geographic mix, pp |
|---|---|---|---|---|
| 3Q26 | index | 10-K FY2025 shares | 9.90 | -1.24 |
| 3Q26 | persistence | 10-K FY2025 shares | 9.90 | -1.19 |
| 3Q26 | WS10 base cells | 10-K FY2025 shares | **10.57** | -1.14 |
| 3Q26 | WS10 base cells | WS10 shares | **10.69** | -1.14 |
| 4Q26 | index | 10-K FY2025 shares | 8.90 | -1.25 |
| 4Q26 | WS10 base cells | 10-K FY2025 shares | **10.17** | -1.12 |
| 4Q26 | WS10 base cells | WS10 shares | **10.35** | -1.13 |

Reference: FY2025 realised geographic mix was -1.58pp of ADR, FY2024 -1.24pp, from `research/notes/2026-09-07_adr-decomposition.md` section 3. Regional ADR levels used are the 10-K FY2025 values: NA $255.03, EMEA $158.89, LatAm $94.91, APAC $118.20.

## 3. Method

**Target panel (`C1`).** Fifty region-quarter nights growth figures from the 23 shareholder letters, 3Q22 to 2Q26, plus 20 annual 10-K regional growth rates, 24 annual regional shares and 24 annual regional ADRs, and 18 origin-country figures. Every quote is checked by normalised substring match against the raw letter HTML before it is written; all 71 letter-sourced rows verified and `C1_quote_failures.csv` is empty. Qualitative buckets are mapped low-single 2, mid-single 5, high-single 8, low-double 11, low-teens 13, mid-teens 15, high-teens 18, low-20s 21, each carrying a 1pp half-width. That mapping is a researcher reading, not a company statement.

**Consumer panel (`C2`).** One OECD SDMX request to `DSD_KEI@DF_KEI` returns monthly composite consumer confidence, unemployment rate, retail trade volume y/y, share prices y/y, CPI y/y and hourly earnings y/y for 29 countries from 2016 to August 2026. A second request to `DSD_HHDASH@DF_HHDASH_INDIC` returns the quarterly household saving rate and real household disposable income per capita, expanded to months. Real wage is hourly earnings y/y less CPI y/y. Raw pulls are cached under `raw/` so the build is reproducible offline. 23,438 country-month-indicator observations.

**Index (`C3`).** Each indicator is z-scored within country over a window that starts in 2018 and **excludes 2020 and 2021**, because the COVID collapse and rebound would otherwise set the scale for every country. Signs: confidence, retail volume, real wage, equity and real household income positive; unemployment, saving rate and CPI negative. A country needs at least two available indicators. Region index is the origin-weighted mean of country composites; relative strength is the region index less the global origin-weighted index, so a common global cycle is differenced out by construction. Origin weights are an assumption (`C3_weights.csv`): region weights are the 10-K FY2025 nights shares by listing location used as an origin proxy, country weights inside a region are judgement anchored on the core and expansion markets the letters name, with China held at 8% of APAC because Airbnb closed its China domestic business in July 2022 and now serves China outbound only. Four sensitivities are run (`C3_weight_sensitivity.csv`): dropping CPI, dropping the saving rate, a core-four set, equal country weights inside each region, equal region weights, and a tilt that moves 3pp of region weight out of NA. **Every variant keeps the same sign pattern in 2026: LatAm positive, NA negative.** The 3Q26 APAC reading is the only one that flips sign across variants, from -0.02 in the base to +0.15 when CPI is dropped, because APAC inflation is what holds it down.

**Tests (`C4`).** Region fixed effects absorbed by within-region demeaning on both sides, so the test is whether a region grows relatively faster in its own relatively stronger quarters. The level regression without the fixed effect would only recover the structural fact that LatAm and APAC grow faster than NA, which is penetration and expansion strategy, not a consumer cycle. Permutation p shuffles the predictor within region, preserving the region means and the predictor's own distribution, 20,000 draws. Leave-one-out refits the slope on 27 observations and predicts the 28th, against a naive that predicts the region mean.

**Application (`C5`).** Predicted differentials are renormalised to weight-zero-sum, then added to the team total. ADR geographic mix is the standard term: next-period nights-weighted regional ADR over this-period nights-weighted regional ADR, minus one.

## 4. What this can and cannot identify

- **It cannot separate the consumer channel from the product channel.** The window in which the regional disclosure is a usable bucket (4Q24 onward) is the same window as the RNPL launch, the cancellation-policy change and the single-fee redesign, which management says were worth about 3 points of 1Q26 nights growth and which landed in North America first. North America is also the region with the clearest consumer deterioration. Twenty-eight observations across four regions cannot pull those apart, and the negative fitted slope is exactly what collinearity of that kind produces.
- **It cannot establish the trade-down mechanism it would need to justify the negative sign.** That would need within-region evidence on Airbnb-versus-hotel substitution at a time of local consumer weakness, which is WS06's territory, not a four-region panel's.
- **The target is destination-based and the predictor is origin-based.** Airbnb's regional disclosure is by listing location. Roughly 46% of gross nights were cross-border when that was last disclosed in 1Q24, and the letters stress that the majority of North American and EMEA travel is domestic or in-region, so the mismatch is second order for NA and EMEA and larger for APAC, the region most reliant on cross-border travel. Using destination shares as origin weights is a stated approximation and the tilt sensitivity exists only to size it, not to fix it.
- **Buckets, not numbers.** Twenty-seven of the 28 modern observations are bucket midpoints with 1pp half-widths, only 2Q26 LatAm being numeric, and `research/notes/overnight/27_regional-bucket-check.md` shows that North America has sat at the bottom of its bucket in five of the last six quarters while the 2026 midpoint sum overshoots the reported total by 0.6 to 0.9pp. A 1pp mapping error on NA is a third of the fitted slope's effect at a 0.2 z move, so the slope is not cleanly measured.
- **The index cannot see India, and India is the fastest-growing origin market.** India has only two indicators in the panel, CPI and share prices, because the OECD carries no harmonised Indian consumer confidence, unemployment or retail volume. Its composite reads -0.82 in July and August 2026 while Airbnb reports Indian origin net nights accelerating to +60% y/y. That single contradiction is enough to disqualify the index as an APAC forecasting tool.
- **Canada has no consumer confidence series in either OECD dataflow**, so its composite rests on unemployment, retail volume, real wage, equity and saving rate. Canada's 2025 travel pattern was in any case political, a pullback from US destinations, and a consumer-strength index would not capture it even with full coverage.
- **LatAm coverage is thin at the right-hand edge.** In July and August 2026 only about 65% of the LatAm origin weight has data, effectively Brazil and Mexico. Argentina, Chile, Colombia and Costa Rica report with a lag. The LatAm reading is a Brazil-and-Mexico reading.
- **4Q26 has no macro data at all.** The 4Q26 column carries the 3Q26 reading forward. It is an assumption with a wider band, not a forecast.
- **Nothing here is a total-nights nowcast.** The total is taken from the team baseline throughout, consistent with the instruction not to rebuild what `research/notes/predictive/03_macro-altdata-nowcast.md` and `research/notes/overnight/08_altdata-index-and-backtests.md` already found to be weak.

## 5. Next evidence

1. **The decisive test is available on 5 November.** The 3Q26 letter will give four new bucket observations. The index's out-of-sample call, in differential terms against whatever total prints, is NA -3.2pp, EMEA -4.0pp, LatAm +9.6pp, APAC +7.2pp. Persistence says -3.3, -3.3, +8.7, +6.7. The sharp disagreement is EMEA, where the index says relatively weaker and persistence says relatively stronger. One observation will not settle the sign, but EMEA is where to look.
2. **Put the product terms in the regression.** PR #32 fits RNPL at +2.4pp and the fee and cancellation redesign at +2.3pp on four North American observations with dated launch timing. Adding those as a regressor, rather than letting them sit in the NA fixed effect, is the one step that could break the collinearity that most likely produces the negative sign. It would still be four identifying observations.
3. **Get a real origin weighting.** UNWTO outbound departures by origin country, or NTTO US outbound, would replace the destination-share proxy. The World Bank international tourism expenditure series is null for 2021 to 2024 and cannot do it.
4. **Fill the India and Canada holes from national sources.** RBI's consumer confidence survey for India and the Conference Board of Canada index would lift two of the panel's weakest countries. Both are outside the OECD SDMX service.
5. **Test the trade-down reading directly.** If a weaker local consumer genuinely pushes travellers onto Airbnb, it should show as a widening Airbnb-versus-hotel price gap effect in the quarters and countries where the composite is weakest. WS06's `06_price_gap_monthly.csv` and `06_quote_discount_panel.csv` are the inputs.
6. **Re-weight WS10 and the FY27 bridge on the 10-K shares.** The correction is small (0.12 to 0.18pp on the total) but it is free and it removes a known error.

## 6. Files

Scripts, all under `analysis/src/overnight2/`:

- `C1_target_panel.py` regional and origin target panels, with quote verification
- `C2_consumer_panel.py` OECD pulls and the monthly country panel
- `C3_relative_strength_index.py` country composites, regional and relative indices, weight sensitivities
- `C4_tests.py` fits, acceleration fits, mean-reversion controls, leave-one-region-out, origin-country tests, episode checks
- `C5_application.py` the 3Q26 and 4Q26 split, implied total, ADR mix, chart

Outputs, all under `data/processed/overnight2/C/`:

- `regional_target_panel.csv`, `origin_country_panel.csv`, `C1_quote_failures.csv` (empty)
- `consumer_panel_monthly.csv`, `C2_coverage.csv`, `C2_source_gaps.csv`, `raw/oecd_kei_monthly.csv`, `raw/oecd_hhdash_quarterly.csv`
- `country_strength_monthly.csv`, `regional_strength_monthly.csv`, `regional_strength_quarterly.csv`, `C3_weights.csv`, `C3_weight_sensitivity.csv`
- `C4_regression_panel.csv`, `C4_fits.csv`, `C4_acceleration_fits.csv`, `C4_mean_reversion.csv`, `C4_leave_region_out.csv`, `C4_origin_panel.csv`, `C4_origin_country_fits.csv`, `C4_episode_checks.csv`
- `C5_regional_split_forecast.csv`, `C5_total_and_adr_mix.csv`, `C5_relative_strength_and_differential.png`

Data sources that failed or are incomplete, recorded in `C2_source_gaps.csv`: OECD `DSD_PRICES@DF_PRICES_ALL` returned 404 on the key tried, so there is no travel-price term by country; the World Bank international tourism expenditure indicator returns null for 2021 to 2024; OECD consumer confidence is absent for Canada, India, Argentina and South Africa, and was filled from the household dashboard for Switzerland, New Zealand and Costa Rica; the OECD `DF_CS` consumer opinion survey dataflow returned 404 on every key shape tried within the time budget.

