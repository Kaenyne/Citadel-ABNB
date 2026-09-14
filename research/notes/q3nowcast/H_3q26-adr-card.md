# H. The 3Q26 and 4Q26 ADR card

- **Date:** 2026-09-12. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Question:** what is the team's number for reported ADR in 3Q26 and 4Q26, built only from pieces that already exist, with a band and an explicit split between what is measured and what is assumed?
- **Script:** `analysis/src/q3nowcast/H1_adr_card.py` (`py -3.13`, no network).
- **Outputs (`data/processed/q3nowcast/H/`):** `adr_history_components.csv`, `adr_forecast_card.csv`, `adr_sensitivities.csv`, `adr_exfx_backtest.csv`, `adr_consensus_implied.csv`.
- **Inputs, all read-only:** main tree `data/processed/adr/02b, 04, 07, 13, 14b, 15`, `data/processed/overnight/04_current_consensus.csv`, `05_fx_fits.csv`, `06_fee_timeline.csv`, `model/ADR_decomposition.xlsx` sheet 5_Forecast, the 2Q26 letter `data/raw/letters/2Q26_d70413dex991.htm`; overnight-2 `data/processed/overnight2/B/B_fx_translation_schedule_refresh.csv` and `B_adr_fx_estimator_backtest.csv`, `C/C5_total_and_adr_mix.csv`; the H1-to-H2 bridge note and `data/processed/h2_bridge/`.
- **Does not redo:** the ADR decomposition, the party-size, LOS, seats-dilution and fee-reprice studies, WS-B's FX estimators, WS-C's mix drag, or the H1-to-H2 base rates. This note assembles them into one quarterly card and tests the assembly.

---

## 1. Bottom line

1. **3Q26 reported ADR: +3.2% y/y, $176.8, central band $174.0 to $179.1 (+1.6% to +4.6%), off a 3Q25 base of $171.29.** Ex-FX +3.6% (band +2.0 to +5.0), FX effect -0.4 pp at the midpoint of the two WS-B estimators. The FX estimator choice alone moves the point from +2.5% (WS05 EUR-only fit, -1.1 pp) to +3.9% (unfitted four-basket build, +0.3 pp).
2. **4Q26 reported ADR: +3.9% y/y, $174.1, central band $171.1 to $177.8 (+2.2% to +6.2%), off a 4Q25 base of $167.51.** Ex-FX +3.8% (band +2.0 to +6.0), FX +0.2 pp at the midpoint, and the estimator gap is wider here: +3.1% on the EUR fit against +4.7% on the baskets. That 1.6 pp is the single largest *quantified* disagreement in the Q4 ADR line, as WS-B said.
3. **The three routes agree, and that agreement is weaker evidence than it looks.** Component build +3.4 / +3.5 pp ex-FX, H1-to-H2 transition +3.5 / +3.8, naive last disclosed quarter +4.0 / +4.0. The component build and the bridge are both anchored on the same 1H26 disclosed ex-FX of +4%, so they are not independent draws; the agreement says the assembly is internally consistent, not that it is accurate.
4. **The component build does not beat naive, and it is reported as such.** Walk-forward from 2Q24 with every term restricted to information dated before the target quarter: RMSE 1.29 pp against 0.82 pp for naive last quarter and 0.80 pp for AR(1), a ratio of 1.58 (n 9). It is biased low by about 1.5 pp in 1H26 because a trailing residual cannot see an acceleration. Per the note-08 protocol this is a failed feature and is not tuned until it passes. The build's value is attribution, not prediction, and the naive benchmark is therefore carried as a third route rather than discarded.
5. **The components reconcile to the disclosed ex-FX figure.** The quarterly geographic-mix term is rebuilt here from the regional panel rather than taken annually, and the regional reconstruction of blended ex-FX ADR lands within a mean of -0.04 pp and a mean absolute 0.39 pp of the disclosed figure over 1Q23 to 2Q26 (max 0.92 pp, 2Q23). The residual like-for-like pricing term is therefore visible quarter by quarter: 1.9 to 3.5 pp through 2023 to 2025, then **4.4 pp in 1Q26 and 4.9 pp in 2Q26**. That step, not mix and not size, is what carried 1H26.
6. **The largest single uncertainty differs by quarter.** For 3Q26 it is the like-for-like pricing residual (31% of the variance of the band), then the FX estimator choice (26%). For 4Q26 it is the fee-migration reprice (35%), then FX (25%), then pricing (22%). Geographic mix, unit size, length of stay and seats dilution together account for under a quarter of the band in both quarters, which is the opposite of how those terms are usually discussed.
7. **At the team nights baseline this ADR gives GBV +13.4% in 3Q26 and +13.2% in 4Q26.** Management guided 3Q26 GBV to "mid teens". Our ADR is the reason we sit at the low end, not nights: 146.8mm nights is +9.9%, so reaching +15% GBV needs ADR near +4.6%, the top of our central band.
8. **No ADR consensus exists.** Deriving one from the Zacks revenue mean at an unchanged implied take rate gives 3Q26 ADR of $180.6 (+5.4%) at our nights baseline or $178.8 (+4.4%) at a guide-consistent +11% nights, and 4Q26 $177.1 (+5.7%) or $173.6 (+3.7%). Our 3Q26 point sits 1.2 to 2.2 pp below that derived figure. Comparison column only.

---

## 2. Tables

### 2.1 Reconstructed history, percentage points of ADR y/y

Terms are additive: reported = FX effect + ex-FX, and ex-FX = geographic mix + unit size + length of stay + new business + interaction + residual pricing.

| | 1Q23 | 2Q23 | 3Q23 | 4Q23 | 1Q24 | 2Q24 | 3Q24 | 4Q24 | 1Q25 | 2Q25 | 3Q25 | 4Q25 | 1Q26 | 2Q26 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADR, $ | 168.43 | 166.01 | 161.38 | 156.73 | 172.88 | 169.53 | 163.64 | 158.13 | 171.34 | 174.48 | 171.29 | 167.51 | 186.82 | 183.73 |
| Reported y/y | 0.2 | 1.4 | 3.2 | 2.6 | 2.6 | 2.1 | 1.4 | 0.9 | -0.9 | 2.9 | 4.7 | 5.9 | 9.0 | 5.3 |
| FX effect (disclosed) | -2.8 | -0.6 | 2.7 | 2.1 | 0.6 | -0.9 | -0.6 | -1.1 | -1.9 | 1.9 | 2.7 | 2.9 | 5.0 | 1.3 |
| **ex-FX y/y (disclosed)** | **3.0** | **2.0** | **0.5** | **0.5** | **2.0** | **3.0** | **2.0** | **2.0** | **1.0** | **1.0** | **2.0** | **3.0** | **4.0** | **4.0** |
| Geographic mix | -1.35 | -0.90 | -1.17 | -0.94 | -1.33 | -1.13 | -1.12 | -1.79 | -1.89 | -1.70 | -1.59 | -1.46 | -1.04 | -1.27 |
| Unit size (party size) | 0.46 | 0.36 | 0.41 | 0.29 | 0.96 | 0.77 | 0.89 | 0.71 | 0.67 | 0.73 | 0.75 | 0.82 | 0.95 | 0.70 |
| Length-of-stay mix | 0.46 | 0.12 | 0.30 | 0.36 | 0.21 | 0.23 | 0.25 | 0.43 | 0.28 | 0.35 | 0.31 | 0.22 | 0.30a | 0.30a |
| New business (seats, hotels) | | | | | | | | | -0.18 | -0.18 | -0.18 | -0.18 | -0.48 | -0.48 |
| Interaction | -0.05 | -0.05 | -0.05 | -0.05 | -0.11 | -0.11 | -0.11 | -0.11 | -0.11 | -0.11 | -0.11 | -0.11 | -0.10a | -0.10a |
| **Residual like-for-like pricing** | **3.48** | **2.47** | **1.01** | **0.83** | **2.26** | **3.23** | **2.08** | **2.76** | **2.23** | **1.91** | **2.82** | **3.70** | **4.38** | **4.85** |
| Regional reconstruction gap | -0.29 | -0.92 | -0.30 | 0.33 | -0.18 | -0.32 | 0.30 | 0.49 | 0.40 | 0.21 | 0.72 | -0.35 | -0.33 | -0.28 |

`a` assumed: 14b's stay-length series stops at 4Q25 (no 2026 stay-length or ALOS disclosure) and 07's interaction term is annual to 2025, so 1Q26 and 2Q26 carry the workbook base values. The 2026 residual is 0.2 pp lower than it would be with those cells blank, and that is the only place an assumption enters the history.

Residual run rates used below: trailing 8 quarters 3.09, trailing 4 quarters 3.94, 1H26 4.61.

### 2.2 The forecast card

| | 3Q26 | 4Q26 |
|---|---|---|
| Base quarter ADR | 3Q25, $171.29 | 4Q25, $167.51 |
| Route a, component build, ex-FX | +3.36 (2.20 to 4.53) | +3.47 (2.07 to 4.87) |
| Route b, H1-to-H2 transition, ex-FX | +3.50 (2.00 to 5.00) | +3.80 (2.00 to 6.00) |
| Route c, naive last disclosed, ex-FX | +4.00 (3.18 to 4.82) | +4.00 (3.18 to 4.82) |
| **Headline ex-FX, mean of routes** | **+3.62 (2.00 to 5.00)** | **+3.76 (2.00 to 6.00)** |
| FX, WS05 EUR-only fit | -1.12 | -0.66 |
| FX, unfitted four-basket build | +0.26 | +0.97 |
| FX, midpoint (used for the point) | -0.43 | +0.15 |
| **Reported ADR y/y, point** | **+3.19%** | **+3.91%** |
| Reported y/y, EUR-fit FX / basket FX | +2.50% / +3.88% | +3.10% / +4.73% |
| Reported y/y, central band | +1.57 to +4.57 | +2.15 to +6.16 |
| Reported y/y, wide band (routes plus FX estimators) | +0.88 to +5.26 | +1.34 to +6.97 |
| **ADR, $ point** | **$176.76** | **$174.06** |
| ADR, $ central band | $173.98 to $179.12 | $171.12 to $177.82 |
| GBV at the team nights baseline | $25.95bn, +13.4% | $23.10bn, +13.2% |

### 2.3 Component build, percentage points, with source and label

| Term | 3Q26 lo / point / hi | 4Q26 lo / point / hi | Source | Label |
|---|---|---|---|---|
| Like-for-like pricing residual | 3.09 / 3.94 / 4.61 | same | this note's reconstruction: trailing 8q, trailing 4q, 1H26 means | assumed, anchored on measured residuals |
| Geographic mix | -1.64 / -1.19 / -1.04 | -1.65 / -1.19 / -1.02 | overnight-2 WS-C `C5_total_and_adr_mix.csv`, 10-K FY25 shares; low end widened to the 2025 actual -1.58 | sourced and descriptive |
| Unit size via party size | 0.00 / 0.74 / 0.98 | same | `13_party_size_adr_forecast.csv`, global nights-weighted bear/base/bull | descriptive, measured on reviews |
| Length-of-stay mix | 0.00 / 0.30 / 0.45 | same | 14a/b/c, workbook 5_Forecast | descriptive, measured on disclosures plus calendars |
| New business (seats, hotels) | -0.75 / -0.48 / -0.23 | same | `15_seats_dilution_quarterly.csv`, business bull/base/bear | assumed, ticket price is the soft cell |
| Fee migration, incremental only | -0.30 / +0.16 / +0.85 | -0.50 / +0.26 / +1.42 | note 12 bounds scaled to the rise in single-fee penetration above the 1H26 average | assumed |
| Interaction | -0.15 / -0.10 / -0.05 | same | 07, stable since 2023 | descriptive |
| **Sum** | **0.25 / 3.36 / 5.58** | **0.04 / 3.47 / 6.17** | band quoted is the root-sum-square half range, 1.17 and 1.40 | |

### 2.4 Sensitivities, 1 pp on each component

A 1 pp move in any term moves reported ADR by exactly 1 pp, because the build is additive. The dollar and revenue translations are what differ.

| Quarter | 1 pp of ADR is | at the team nights baseline |
|---|---|---|
| 3Q26 | $1.71 of ADR | $259mm of GBV, $46mm of revenue and 1.13 pp of revenue growth on the implied-take-rate convention (17.88%) |
| 4Q26 | $1.68 of ADR | $231mm of GBV, $31mm of revenue and 1.13 pp of revenue growth (13.62%) |

Share of the band's variance by term (`adr_sensitivities.csv`):

| Term | 3Q26 | 4Q26 |
|---|---|---|
| Like-for-like pricing | 31.3% | 22.1% |
| FX estimator choice | 25.8% | 25.1% |
| Fee migration | 18.3% | 35.2% |
| Unit size | 13.0% | 9.2% |
| Geographic mix | 4.9% | 3.7% |
| New business seats | 3.7% | 2.6% |
| Length of stay | 2.9% | 2.0% |
| Interaction | 0.1% | 0.1% |

The revenue translation above is the same-quarter implied-take-rate convention the company and the guide use. It is not the recognition mechanics: revenue is recognised at check-in, so a 3Q26 ADR surprise reaches 3Q26 revenue only through the share of 3Q26 stays booked in 3Q26, and the rest lands in 4Q26. The H1-to-H2 bridge's lagged-GBV conversion is the right tool for the revenue line; this table is for sizing the ADR line only.

### 2.5 Management and consensus

6 August 2026 letter, Q3 2026 outlook, verbatim: "We expect year-over-year GBV growth to be in the mid teens, driven by low double-digit growth in Nights and Seats Booked and a **moderate increase in ADR due to mix shift and price appreciation**." On the quarter just reported: "ADR was $184 in Q2 2026, increasing 5% compared to Q2 2025. On an ex-FX basis, ADR in Q2 2026 increased 4% year-over-year and was up across all regions, particularly North America and EMEA, due to price appreciation and mix."

"Moderate increase" is the same phrase used ahead of 2Q26's +5% reported and +4% ex-FX, and management's "mix shift" is the unit-size and stay-length mix that helps ADR, not the geographic mix that hurts it. Our +3.2% reported for 3Q26 is consistent with the words and one notch below the 2Q26 print.

No vendor publishes an ADR consensus (`04_current_consensus.csv` records the search failing for Q3 nights and adjusted EBITDA too). Derived from the Zacks revenue mean at an unchanged implied take rate:

| | Consensus revenue | Implied GBV | Implied ADR at 146.8 / 132.7mm nights | at guide-consistent +11% nights |
|---|---|---|---|---|
| 3Q26 | $4,740mm (7 est.) | $26,510mm | $180.59, +5.4% | $178.76, +4.4% |
| 4Q26 | $3,200mm (10 est., mean skewed by one $3.70bn estimate) | $23,495mm | $177.05, +5.7% | $173.64, +3.7% |

---

## 3. Method

**History.** Reported ADR, the FX effect and ex-FX ADR come from `02b_adr_history_extended.csv`, disclosed in the letters from 2Q22. The geographic-mix term is computed quarterly here rather than taken from the annual 07 decomposition: for each quarter, year-ago regional ADR levels are grown by the disclosed regional ex-FX rate and aggregated twice, once on year-ago nights shares and once on current shares. The difference is the mix term; the level of the current-share aggregate against the disclosed blended ex-FX figure is the reconciliation gap in table 2.1. Unit size is the measured global nights-weighted term from `13_party_size_adr_quarterly.csv` (booked capacity from 123 markets of review data times a price elasticity of 0.59). Length of stay is `14b`'s global quarterly series. New business and the interaction term are annual and spread flat. The residual is what is left of the disclosed ex-FX figure.

**Route a, component build.** Each term is set to a low, point and high from its own source note, listed in table 2.3. The pricing residual is the only term with no external measurement; it is anchored on the three run rates of the reconstructed residual and nothing is padded. The fee-migration term carries only the *incremental* rise in single-fee penetration above the 1H26 average, because the 1H26 residual already embeds repricing on the cohort that had migrated by then. Penetration is assumed at 0.375 for the 1H26 average (a quarter of listings at 1Q26, about half at 2Q26, from `06_fee_timeline.csv`), 0.60 at 3Q26 and 0.75 at 4Q26, against the 2Q26 letter's "most remaining hosts during 2026". Per migrated listing the reprice effect on ADR is note 12's +0.7% payout-neutral base and +3.8% over-reprice high; the low end scales note 12's recommended -0.5 pp downside for 4Q26. The quoted band is the root-sum-square of the seven half ranges, because the terms are independently sourced; the arithmetic extremes are also in the output and are much wider.

**Route b, H1-to-H2 transition.** 1H26 disclosed ex-FX ADR was +4% in both quarters. The bridge's 2023 to 2025 base-rate transition from the H1 mean is -0.5 pp to Q3 (range -2.0 to +1.0) and -0.2 pp to Q4 (range -2.0 to +2.0), n 3.

**Route c, naive.** Last disclosed ex-FX ADR y/y, 2Q26 = +4.0%, banded at its own walk-forward RMSE of 0.82 pp. Included because the backtest says it is the best available estimator of this series.

**Backtest.** Walk-forward from 2Q24, every term restricted to information dated before the target quarter: pricing residual, geographic mix, unit size and length of stay as trailing four-quarter means, new business and interaction as the prior calendar year's value. Benchmarks are naive last quarter, same quarter prior year and an AR(1) on ex-FX. RMSE 1.292 for the build against 0.816 naive, 1.810 prior year and 0.804 AR(1); ratio to naive 1.58. n 9, so no permutation test is reported. Every term in the build is knowable before the print except the pricing residual, which is only ever knowable after it.

**FX.** WS-B's refreshed schedule is used unchanged. A fresh FRED pull on 11 September 2026 returned a last observation of 2026-09-04 for both DTWEXBGS and DEXUSEU, identical to WS-B's vintage, so no refresh was possible; H.10 has not published past 4 September. Recomputing 3Q26 quarter-to-date from that pull on observed days only gives EURUSD -1.24% y/y and the broad dollar -0.61% y/y, against WS-B's -1.22% and -0.87% with the remaining 18 business days held at flat spot. Through the WS05 EUR fit (slope 0.4512, intercept -0.5687, fitted on 17 disclosed quarters) that is -1.13 pp against WS-B's -1.12 pp, so the estimator is reproduced. On the 17 disclosed quarters the estimator RMSEs are 0.458 pp (EUR fit), 0.535 pp (unfitted four-basket build) and 0.868 pp (broad dollar). The broad-dollar estimator is excluded from the band on that basis, which is also why the band is -1.1 to +0.3 and not -1.1 to +1.1.

---

## 4. What this can and cannot identify

- **Nothing here measures realised ADR.** 2026 Inside Airbnb calendars carry no price, the quote-index test (8 September) showed listing-level quotes do not track disclosed regional ADR on a constant methodology (13 clean same-basis pairs, wrong sign in Rome, Paris, Austin and Nashville), and 3,000 Common Crawl renders carry no price. This is a structural build off disclosed identities, not a nowcast off observed prices.
- **The pricing residual is unidentified and it is the largest term.** It is 3 to 5 pp of a 4 pp number. It absorbs like-for-like pricing, sub-regional mix inside each region, any measurement error in the other terms and the fee-migration reprice on the already-migrated cohort. Calling it "price appreciation" is management's description, not our measurement.
- **The two model routes are not independent of each other.** Both start from the 1H26 disclosed ex-FX of +4%. Their agreement is a consistency check on the assembly.
- **The component build fails the note-08 protocol.** It loses to naive and to AR(1) on nine walk-forward quarters and is biased low into accelerations. It is kept because it tells you which pieces moved, which is what the card is for, and because the naive route is carried alongside it rather than being replaced by it.
- **The fee-migration term is an assumption on an assumption.** Penetration above 2Q26's "about half" is our path, not a disclosure, and note 12's quote-based attempt to measure a reprice step failed outright: observed excess mass in the signature bins was 0.0 to 1.6% per pair against a noise floor near 10%. What the prints bound is that the no-reprice case is rejected.
- **Seats dilution is seasonal in the wrong direction for us.** `15_seats_dilution_quarterly.csv` spreads the annual drag flat, and Experiences seats are summer-heavy, so -0.48 pp probably understates 3Q26 and overstates 4Q26. Not correctable without a seats disclosure.
- **The geographic-mix reconstruction leans on modelled regional ADR before 4Q24.** The 2023 and part of 2024 regional cells are modelled rather than disclosed-chained, which is where the reconciliation gap is widest (2Q23, -0.92 pp).
- **Basis breaks.** The KPI became Nights and Seats Booked from the 2Q25 letter, so ADR is GBV over a denominator that now includes seats; the 10-K regional table is on the same basis. ADR is gross of the guest service fee, which is the entire reason the single-fee migration touches it at all.

---

## 5. Next evidence

1. **The 5 Nov letter's ex-FX ADR sentence and the regional ex-FX lines.** A 3Q26 ex-FX print of +4% or better says the pricing residual has not rolled over and the naive route was right; +3% or below says the H1-to-H2 transition and the component build were right. Either way it is a one-line resolution of the 31% of the band this note cannot close.
2. **Any seats, Experiences GBV or hotel-night number.** It replaces the ticket assumption in the seats term and fixes its quarterly shape at the same time.
3. **Single-fee penetration at 3Q26.** The letters have given a quarter (1Q26) and about half (2Q26). A third data point pins the penetration path and removes most of the 4Q26 fee band, which is that quarter's largest term.
4. **One decision for Krish, carried forward from WS-B point 7 and still open:** pick the ADR-FX estimator. The EUR-only fit has the better RMSE (0.458 against 0.535) but the basket build uses no parameters fitted to the target and is the one that says Latin American and Asian baskets are still up 6% year over year. The card reports both; the model should name one.
5. **Do not spend more on quote collection for this line.** The quote-index test and the fee-reprice addendum both failed on the same data that agent-scraped quotes would reproduce.

---

## 6. Files

| File | Contents |
|---|---|
| `analysis/src/q3nowcast/H1_adr_card.py` | the whole build, reproducible with `py -3.13`, no network |
| `data/processed/q3nowcast/H/adr_history_components.csv` | 1Q23 to 2Q26, reported and ex-FX y/y, FX, the five measured terms, the residual, the identity and reconciliation checks |
| `data/processed/q3nowcast/H/adr_forecast_card.csv` | three routes times three FX estimators times two quarters, ex-FX and reported y/y, bands, dollar ADR, GBV |
| `data/processed/q3nowcast/H/adr_sensitivities.csv` | per-term range, dollar, GBV and revenue translation, share of band variance |
| `data/processed/q3nowcast/H/adr_exfx_backtest.csv` | walk-forward component build against naive, prior year and AR(1), 2Q24 to 2Q26 |
| `data/processed/q3nowcast/H/adr_consensus_implied.csv` | ADR implied by the Zacks revenue mean under two nights assumptions |
