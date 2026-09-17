# Question registry — pitch forecasts

Conventions. "5 Nov print" = Airbnb's 3Q26 results release (shareholder letter, press release, 10-Q) and earnings call,
expected 5 Nov 2026 after market close; if the date moves, the same event on its actual date. "Feb print" = the 4Q26
results release and call, expected ~11 Feb 2027. "Street" = the LSEG-family consensus mean for the stated metric at the
close of the last trading day before the print, as recorded in `data/processed/forecast_methods/L0/L0_vintage_register.csv`
(fallback: Yahoo/LSEG mean captured that day). "Nights" = Nights and Seats Booked as reported. "Bucket language" is the
letter's or call's qualitative growth descriptor for the next quarter. Where the letter and call differ, the letter governs;
where neither states an item, the "not stated" option resolves. Day-1 return = close on the first trading session after
the release divided by the close on the release day, minus one. Numeric consensus and price snapshots must be saved to
`sources/` at retrieval. Scoring regime for all questions: n/a (internal pitch calibration); treat as spot-scored at
resolution. CP: not visible (no Metaculus question exists); adjacent markets per the skill's step 4.

Priority 1 = core 5 Nov disclosures; 2 = stock path and Feb; 3 = risks and bonus items; 4 = synthesis.

| ID | Slug | Type | Group | Batch | Pri |
|---|---|---|---|---|---|
| C01 | q4-revenue-guide-vs-street | binary + continuous | core | A01 | 1 |
| C02 | q4-nights-bucket | MC | core | A02 | 1 |
| C03 | fy26-revenue-guide-language | MC | core | A02 | 1 |
| C04 | fy26-margin-sentence | MC | core | A03 | 1 |
| C09 | q4-margin-direction-sentence | MC | core | A03 | 1 |
| C05 | bundle-attribution-quantified | MC | core | A04 | 1 |
| C06 | rnpl-gbv-share-disclosed | MC | core | A04 | 1 |
| C07 | rnpl-negative-effect-acknowledged | binary | core | A04 | 1 |
| C08 | q3-revenue-fx-integer | MC | core | A05 | 1 |
| C11 | q3-take-rate-above-1810 | binary | core | A05 | 1 |
| C12 | q3-unearned-fees-yoy | binary | core | A05 | 1 |
| S01 | day1-move-5nov | continuous | stock | A06 | 2 |
| S02 | close-15dec-2026 | continuous | stock | A07 | 2 |
| S03 | close-12feb-2027 | continuous | stock | A07 | 2 |
| S04 | sellside-mean-target-cut-by-15dec | binary | stock | A07 | 2 |
| F01 | q1-27-nights-guide-above-82 | binary | feb | A08 | 2 |
| F02 | q1-27-revenue-guide-growth | continuous | feb | A08 | 2 |
| F03 | fy27-margin-guide | MC | feb | A08 | 2 |
| F04 | fy27-sm-share-above-219 | binary | feb | A08 | 2 |
| R01 | risk-q3-nights-meets-guide | binary | risk | A09 | 3 |
| R02 | risk-q3-nights-accelerates | binary | risk | A09 | 3 |
| R03 | risk-july-rnpl-expansion-offsets-lap | binary | risk | A09 | 3 |
| R04 | risk-single-fee-take-rate-accretion-stated | binary | risk | A10 | 3 |
| R05 | risk-q3-margin-sandbagged | binary | risk | A10 | 3 |
| R07 | risk-adr-residual-persists | binary | risk | A10 | 3 |
| R06 | risk-buyback-upsize | binary | risk | A11 | 3 |
| R08 | risk-new-2027-growth-lever | binary | risk | A11 | 3 |
| R09 | risk-new-businesses-quantified-material | binary | risk | A11 | 3 |
| R10 | risk-dollar-weakens | binary | risk | A12 | 3 |
| R11 | risk-q4-us-revpar-strong | binary | risk | A12 | 3 |
| R15 | risk-world-cup-quantified-small | binary | risk | A12 | 3 |
| R16 | risk-q4-nights-print-meets-street | binary | risk | A12 | 3 |
| R12 | risk-sellside-upgrades | binary | risk | A13 | 3 |
| R13 | risk-short-interest-crowding | binary | risk | A13 | 3 |
| R14 | risk-feb-print-up-day | binary | risk | A13 | 3 |
| B01 | bonus-moderation-language | binary | bonus | A14 | 3 |
| B02 | bonus-adr-residual-reverts | binary | bonus | A14 | 3 |
| B03 | bonus-marketing-cut-signalled | binary | bonus | A14 | 3 |
| B04 | bonus-host-churn-cited | binary | bonus | A15 | 3 |
| B05 | bonus-eu-regulation-hit | binary | bonus | A15 | 3 |
| B06 | bonus-geopolitical-headwind-cited | binary | bonus | A15 | 3 |
| B07 | bonus-us-inbound-falls | binary | bonus | A15 | 3 |
| B08 | bonus-ai-hosting-cost-step | binary | bonus | A16 | 3 |
| B09 | bonus-sbc-step-up | binary | bonus | A16 | 3 |
| B10 | bonus-interest-income-falls | binary | bonus | A16 | 3 |
| B17 | bonus-take-rate-guided-down | binary | bonus | A16 | 3 |
| B11 | bonus-sellside-downgrades | binary | bonus | A17 | 3 |
| B12 | bonus-fy27-investment-year | binary | bonus | A17 | 3 |
| B13 | bonus-q4-nights-print-weak | binary | bonus | A17 | 3 |
| B14 | bonus-weather-event | binary | bonus | A18 | 3 |
| B15 | bonus-q4-us-revpar-soft | binary | bonus | A18 | 3 |
| B16 | bonus-insider-selling | binary | bonus | A18 | 3 |
| X01 | scenario-probabilities | MC | synthesis | A19 | 4 |

---

## Core: 5 Nov disclosures

### C01 — q4-revenue-guide-vs-street
**Title.** Will Airbnb's 4Q26 revenue guidance midpoint, given at the 5 Nov print, be below the Street's 4Q26 revenue consensus mean?
**Type.** Binary, plus a continuous forecast of the guidance midpoint in USD millions (percentile table).
**Resolution.** Yes if the midpoint of the 4Q26 revenue range in the 3Q26 shareholder letter is strictly below the LSEG-family 4Q26 revenue consensus mean recorded on 4 Nov 2026 (register fallback: Yahoo/LSEG mean captured that day). If only a growth-rate range is given, convert on 4Q25 revenue $2,778M. If no 4Q26 revenue guidance is given, resolves No.
**Fine print.** The consensus used is the revenue mean, not the Street's implied guide. Note in the log the separate P(midpoint below Street minus the trailing-8 cushion), which is the "guide surprise" object, but the headline resolves on the raw mean. Resolution date 5 Nov 2026.

### C02 — q4-nights-bucket
**Title.** What qualitative growth bucket will Airbnb give for 4Q26 Nights and Seats Booked at the 5 Nov print?
**Type.** Multiple choice.
**Options.** (a) "low double digits" or any language implying ≥10% (e.g., "double-digit", "similar to Q3" when Q3 printed ≥10%); (b) "around 10%" / "high single digits to low double digits" / "similar to Q3" when Q3 printed <10%; (c) "high single digits"; (d) "mid single digits" or lower, or explicitly "moderate/decelerate" without a bucket; (e) no 4Q26 nights descriptor given.
**Fine print.** Letter governs; call clarifications count only if the letter is silent. Resolution date 5 Nov 2026.

### C03 — fy26-revenue-guide-language
**Title.** How will Airbnb's FY26 revenue growth guidance change at the 5 Nov print?
**Type.** Multiple choice.
**Options.** (a) raised: a point estimate or a range whose midpoint exceeds the prior "at least mid-teens" (read as ≥15%) floor by ≥1pt, e.g., "approximately 16%" or "at least 16%"; (b) reiterated: "at least mid-teens" or equivalent unchanged; (c) narrowed to a point at ≈15% ("approximately 15%", "mid-teens"); (d) lowered or softened (any language implying <15% or removing the floor); (e) no FY26 revenue guidance.
**Fine print.** Prior guide from the 2Q26 letter (6 Aug 2026). Resolution date 5 Nov 2026.

### C04 — fy26-margin-sentence
**Title.** What FY26 adjusted EBITDA margin guidance will Airbnb give at the 5 Nov print?
**Type.** Multiple choice.
**Options.** (a) held: "at least 35.5%" unchanged; (b) "approximately 36%" or "at least 36%" (35.75–36.24 implied); (c) ≥36.5% or "approximately 36.5%"/higher; (d) any lower or softer language (<35.5% floor, "approximately 35.5%", floor removed); (e) no FY26 margin guidance.
**Fine print.** The margin-build M3 rule (November sentence = numeric floor + 50bp, exact 2 of 2) is one input; base rates from the guidance ledger are another. Resolution date 5 Nov 2026.

### C09 — q4-margin-direction-sentence
**Title.** What will Airbnb say about 4Q26 adjusted EBITDA margin versus 4Q25 (28.3%) at the 5 Nov print?
**Type.** Multiple choice.
**Options.** (a) down y/y ("lower", "down", "decline"); (b) approximately flat / "similar"; (c) up y/y; (d) no quarterly margin sentence.
**Fine print.** Any numeric 4Q26 margin guide maps to the option its midpoint implies vs 28.3%. Resolution date 5 Nov 2026.

### C05 — bundle-attribution-quantified
**Title.** Will Airbnb quantify the growth contribution of the RNPL / cancellation-policy / single-fee bundle (or of RNPL alone) for 3Q26 at the 5 Nov print, and at what level?
**Type.** Multiple choice.
**Options.** (a) quantified at ≥2.5 points of nights (or ≥3.5 points of GBV); (b) quantified at 1.5 to <2.5 points of nights (2.0–<3.5 GBV); (c) quantified at <1.5 points of nights (<2.0 GBV); (d) not quantified in points (qualitative only, or share-of-GBV only).
**Fine print.** "Over 200bp" style lower bounds map to the bucket containing the bound. A figure for a subset of features counts. Resolution date 5 Nov 2026.

### C06 — rnpl-gbv-share-disclosed
**Title.** What RNPL share of 3Q26 GBV will Airbnb disclose at the 5 Nov print?
**Type.** Multiple choice.
**Options.** (a) ≥25%; (b) 21–24% (incl. "nearly a quarter", "mid-twenties" if the midpoint is <25); (c) "over 20%" repeated, "roughly 20%", or ≤20%; (d) not disclosed.
**Fine print.** Nights-share or bookings-share disclosures resolve as (d) unless a GBV share is also given. Resolution date 5 Nov 2026.

### C07 — rnpl-negative-effect-acknowledged
**Title.** Will Airbnb management, in the 3Q26 letter, 10-Q or call, state that RNPL reduced or will reduce a reported metric (nights, GBV, revenue, take rate, unearned fees, FCF or cash) in 3Q26 or 4Q26, beyond the boilerplate "higher cancellation rates" and "timing" language already in the 2Q26 10-Q?
**Type.** Binary.
**Resolution.** Yes if any of: a quantified negative effect (points, dollars, or "meaningful"/"notable" drag) on any reported metric; an explicit statement that cancellations from RNPL cohorts exceeded expectations or the tested curve; a statement that the net benefit has declined or turned; or a change to RNPL terms motivated by cancellations. No if statements are limited to net-positive reiteration, unchanged boilerplate, or timing effects described as neutral.
**Fine print.** The 2Q26 10-Q sentences ("higher cancellation rates than historic bookings"; GBV/revenue/cash timing "may become less correlated"; FCF seasonality) are the boilerplate baseline; repeating them verbatim is No. Resolution date 5 Nov 2026 (10-Q filing date if later).

### C08 — q3-revenue-fx-integer
**Title.** What year-over-year FX contribution to 3Q26 revenue growth will Airbnb state at the 5 Nov print?
**Type.** Multiple choice.
**Options.** (a) ≥ +3 points (e.g., "approximately 3 points", "3 to 4 points"); (b) +2 points; (c) ≤ +1 point (incl. "minimal", "roughly neutral"); (d) not stated.
**Fine print.** Resolves on the letter's stated points or the difference between reported and ex-FX revenue growth if both are printed (rounded to the nearest integer). Resolution date 5 Nov 2026.

### C11 — q3-take-rate-above-1810
**Title.** Will Airbnb's printed 3Q26 take rate (revenue ÷ GBV, as reported) be ≥ 18.10%?
**Type.** Binary.
**Resolution.** Yes if 3Q26 revenue / 3Q26 GBV from the press release ≥ 0.1810, computed on unrounded dollars where given, else on the letter's rounded figures. Resolution date 5 Nov 2026.
**Fine print.** Score jointly with GBV: the log must report P(take rate ≥18.10 | GBV band) and the unconditional. Inputs: B1 take-rate reconciliation, nowcast GBV, the fee-migration timing (K note), management's "slightly higher" take-rate remark and the new-business incentives.

### C12 — q3-unearned-fees-yoy
**Title.** Will unearned fees on Airbnb's 30 Sep 2026 balance sheet be ≤ −3% year over year?
**Type.** Binary.
**Resolution.** Yes if the 10-Q's unearned fees at 30 Sep 2026 divided by the 30 Sep 2025 figure, minus one, is ≤ −0.03. Resolution date: 3Q26 10-Q filing.
**Fine print.** Management's 1Q26 letter predicted higher unearned fees in Q3 from RNPL timing; the single-fee migration and FX confound the line (audit note 04). The log must decompose deferral, migration and FX before assigning probability.

## Stock path

### S01 — day1-move-5nov
**Title.** What will ABNB's close-to-close return be on the first trading session after the 3Q26 print?
**Type.** Continuous (percent, −40 to +40). Percentile table required, plus P(≤ −8%), P(≤ −5%), P(≥ +5%), P(≥ +10%).
**Fine print.** Unconditional: the log must build the mixture from the print scenarios (team nowcast band → P(deceleration), C01/C02 outcomes, the reaction-panel conditional means and residual sd, the options-implied event sd) and show the conditional day-1 distribution for the team's base case separately. Resolution date 6 Nov 2026.

### S02 — close-15dec-2026
**Title.** What will ABNB's closing price be on 15 Dec 2026?
**Type.** Continuous (USD). Percentile table plus P(≤ $150), P(≤ $143), P(≥ $180).
**Fine print.** Reference price $167.51 (16 Sep 2026 close). Build from S01, the 20-day drift base rates, sell-side lag behaviour, the multiple-growth line and the options 12M distribution. Resolution date 15 Dec 2026.

### S03 — close-12feb-2027
**Title.** What will ABNB's closing price be on the first trading session after the 4Q26 print (expected 12 Feb 2027)?
**Type.** Continuous (USD). Percentile table plus P(≤ $150), P(≤ $143), P(≥ $180).
**Fine print.** If the print date moves, the first session after the actual 4Q26 release. Resolution date ~12 Feb 2027.

### S04 — sellside-mean-target-cut-by-15dec
**Title.** Will the mean sell-side 12-month price target for ABNB on 15 Dec 2026 be at least $5 below its 12 Sep 2026 level ($181.8, 32 targets)?
**Type.** Binary.
**Resolution.** Yes if the mean of live targets in the same feed convention (`data/processed/reverse_dcf/D/`, 365-day window; fallback yfinance `targetMeanPrice`) on 15 Dec 2026 ≤ $176.8. Resolution date 15 Dec 2026.

## February 2027

### F01 — q1-27-nights-guide-above-82
**Title.** Will Airbnb's 1Q27 nights guidance at the Feb print imply year-over-year growth of ≥ +8.2%?
**Type.** Binary.
**Resolution.** Yes if the letter gives a 1Q27 nights descriptor or number implying ≥8.2% on 1Q26's 156.2m (i.e., ≥169.0m): "high single digits" resolves Yes only if a number ≥8.2 or "high single digit to low double digit" is given; "high single digits" alone resolves by the midpoint convention 8.0 → No. "Low double digits" → Yes. No descriptor → No.
**Fine print.** This is the RNPL module's pre-registered falsifier. Resolution date ~11 Feb 2027.

### F02 — q1-27-revenue-guide-growth
**Title.** What year-over-year growth will the midpoint of Airbnb's 1Q27 revenue guidance imply, at the Feb print?
**Type.** Continuous (percent). Percentile table plus P(< 10%), P(< 9.4%), P(≥ 12%).
**Fine print.** Base 1Q26 revenue $2,678M. Kernel put the midpoint at $2,930–2,990M (+9.4 to +11.6%). Resolution date ~11 Feb 2027.

### F03 — fy27-margin-guide
**Title.** What FY27 adjusted EBITDA margin guidance will Airbnb give at the Feb print?
**Type.** Multiple choice.
**Options.** (a) ≥36.5% floor or point; (b) 36.0–36.4%; (c) 35.5–35.9%; (d) <35.5%, "down year over year", or an explicit investment-year framing; (e) no numeric FY27 margin guidance.
**Fine print.** Resolves on the floor if "at least X%" is used, on the midpoint if a range. Resolution date ~11 Feb 2027.

### F04 — fy27-sm-share-above-219
**Title.** Will Airbnb's FY27 sales and marketing expense (GAAP, ex-SBC, as reported in the FY27 10-K) be ≥ 21.9% of FY27 revenue?
**Type.** Binary.
**Resolution.** Yes if FY27 S&M ex-SBC ÷ FY27 revenue ≥ 0.219 in the 10-K filed ~Feb 2028. Resolution date ~Feb 2028.
**Fine print.** Far out; the log should also give P(≥21.9%) conditional on the Feb 2027 FY27 margin guide buckets in F03.

## Risks (things that move the stock against the short)

Each R and B log ends with the `## 9. Impact` table (brief §Rules 8). "Materiality": P × stock impact ≥ $1/share.

### R01 — risk-q3-nights-meets-guide
**Title.** Will 3Q26 Nights and Seats Booked growth print ≥ +10.0% y/y (the floor of "low double digits")?
**Type.** Binary. **Resolution.** Yes if 3Q26 nights ÷ 133.6m − 1 ≥ 0.100 (≥147.0m). Resolution 5 Nov 2026.
**Fine print.** Derive from the team's nowcast distribution (reviews index +9.5–10.0, external stack +9.2, module 9.49; band 8.5–10.0; walk-forward error distribution of the index), not from web sources. Report the implied probability and its sensitivity to the index's error sd.

### R02 — risk-q3-nights-accelerates
**Title.** Will 3Q26 nights growth print ≥ +10.6% y/y (an acceleration vs 2Q26's +10.34% under the positioning card's 0.25pt dead band)?
**Type.** Binary. **Resolution.** Yes if 3Q26 nights ≥ 147.8m. Resolution 5 Nov 2026. Same derivation rule as R01.

### R03 — risk-july-rnpl-expansion-offsets-lap
**Title.** Will the 5 Nov print show both an RNPL GBV share ≥25% and 3Q26 nights growth ≥ +10.0%?
**Type.** Binary. **Resolution.** Yes only if both C06 resolves (a) and R01 resolves Yes. Resolution 5 Nov 2026.

### R04 — risk-single-fee-take-rate-accretion-stated
**Title.** Will management state at the 5 Nov or Feb print that the single-fee migration is (or will be) accretive to take rate or revenue in 4Q26 or FY27, with a number or a direction ("higher take rate")?
**Type.** Binary. **Resolution.** Yes if either print's letter or call attributes a higher take rate, higher revenue per GBV, or a quantified revenue uplift to the fee migration for 4Q26 or FY27. Resolution ~11 Feb 2027.

### R05 — risk-q3-margin-sandbagged
**Title.** Will 3Q26 adjusted EBITDA margin print ≥ 51.5% (i.e., "down slightly" was sandbagged by ≥1.4pp vs 3Q25's 50.09%)?
**Type.** Binary. **Resolution.** Yes if reported 3Q26 adj. EBITDA ÷ revenue ≥ 0.515. Resolution 5 Nov 2026.

### R07 — risk-adr-residual-persists
**Title.** Will 3Q26 reported ADR growth print ≥ +4.4% y/y (consensus +3.4%; team +3.3%)?
**Type.** Binary. **Resolution.** Yes if 3Q26 ADR ÷ $171.29 − 1 ≥ 0.044 (≥$178.83). Resolution 5 Nov 2026.

### R06 — risk-buyback-upsize
**Title.** Will Airbnb announce a new share repurchase authorization of ≥ $5bn, or repurchase ≥ $1.5bn in a single quarter (4Q26), by the Feb print?
**Type.** Binary. **Resolution.** Yes on either a board authorization ≥$5bn announced 17 Sep 2026–Feb print, or 4Q26 repurchases ≥$1.5bn per the 4Q26 letter/10-K. Resolution ~11 Feb 2027.

### R08 — risk-new-2027-growth-lever
**Title.** By the Feb print, will management announce and quantify a new product or pricing initiative expected to add ≥1 point to 2027 nights or GBV growth?
**Type.** Binary. **Resolution.** Yes if a letter or call gives a numeric expected contribution (≥1pt, or ≥$1bn GBV) for a product launched or announced after 16 Sep 2026 (or a named 2027 rollout, e.g., RNPL for new booking types, a new payment product, an AI booking agent, hotels at scale). Resolution ~11 Feb 2027.

### R09 — risk-new-businesses-quantified-material
**Title.** By the Feb print, will management disclose that hotels, Experiences or Services together account for ≥3% of nights and seats booked, or ≥3% of GBV, or give a FY27 revenue figure for them of ≥$500M?
**Type.** Binary. **Resolution.** Yes on any of the three disclosures. Resolution ~11 Feb 2027.

### R10 — risk-dollar-weakens
**Title.** Will the Fed's broad trade-weighted dollar index (FRED DTWEXBGS) on 11 Feb 2027 be ≥4% below its 16 Sep 2026 value?
**Type.** Binary. **Resolution.** Yes if DTWEXBGS(2027-02-11 or last available) ≤ 0.96 × DTWEXBGS(2026-09-16). Resolution 11 Feb 2027.
**Fine print.** Impact via the FX schedule: ±2.3 points of FY27 revenue growth per one-sigma dollar move.

### R11 — risk-q4-us-revpar-strong
**Title.** Will STR's US hotel RevPAR growth for 4Q26 (Oct–Dec, as reported by STR/CoStar in Jan 2027) be ≥ +4% y/y?
**Type.** Binary. **Resolution.** Yes if the quarterly (or the average of the three monthly) US RevPAR y/y ≥ 4.0%. Resolution ~25 Jan 2027.

### R15 — risk-world-cup-quantified-small
**Title.** By the Feb print, will management quantify the 2026 World Cup's contribution to nights or GBV at ≤1 point (or state it was not material)?
**Type.** Binary. **Resolution.** Yes if a letter or call gives a figure ≤1pt of nights or GBV, or says the contribution was immaterial/not meaningful to the growth rate. Resolution ~11 Feb 2027.

### R16 — risk-q4-nights-print-meets-street
**Title.** Will 4Q26 Nights and Seats Booked growth print ≥ +9.9% y/y (the Bloomberg 4Q26 bar of 134m as of 12 Sep 2026)?
**Type.** Binary. **Resolution.** Yes if 4Q26 nights ≥ 134.0m (base 121.9m). Resolution ~11 Feb 2027.

### R12 — risk-sellside-upgrades
**Title.** Between 17 Sep and 15 Dec 2026, will ABNB receive ≥3 rating upgrades (to Buy/Outperform-equivalent) from firms in the tracked feed, or will the mean target rise to ≥$190?
**Type.** Binary. **Resolution.** Yes on either condition using the feed convention of `data/processed/reverse_dcf/D/`. Resolution 15 Dec 2026.

### R13 — risk-short-interest-crowding
**Title.** Will ABNB short interest exceed 5.0% of shares outstanding at any Nasdaq settlement date between 30 Sep 2026 and 15 Jan 2027?
**Type.** Binary. **Resolution.** Yes if any settlement-date short interest ÷ shares outstanding ≥ 0.05 (Nasdaq/MarketBeat series as in `data/processed/overnight/09_short_interest.csv`). Resolution 15 Jan 2027 (data lag allowed).

### R14 — risk-feb-print-up-day
**Title.** Will ABNB's close-to-close return on the first session after the 4Q26 print be ≥ +5%?
**Type.** Binary. **Resolution.** Yes if the day-1 return ≥ 0.05. Resolution ~12 Feb 2027.

## Bonus (things that would take the stock down more than the base case)

### B01 — bonus-moderation-language
**Title.** At the 5 Nov print, will management use demand-softening language of the kind that preceded 8–13% declines ("moderation"/"moderate" applied to nights or demand, "shorter lead times", "softening", "macro uncertainty affecting bookings", or "deceleration" for 4Q26)?
**Type.** Binary. **Resolution.** Yes if the letter or prepared remarks contain any such phrase applied to forward demand or bookings (not to ADR, costs or FX). Resolution 5 Nov 2026.

### B02 — bonus-adr-residual-reverts
**Title.** Will 3Q26 reported ADR growth print ≤ +2.0% y/y?
**Type.** Binary. **Resolution.** Yes if 3Q26 ADR ≤ $174.72. Resolution 5 Nov 2026.

### B03 — bonus-marketing-cut-signalled
**Title.** At the 5 Nov print, will management state that 4Q26 or FY27 marketing/S&M spend will grow more slowly than revenue, be "moderated", "optimised" or reduced, or quantify a reduction?
**Type.** Binary. **Resolution.** Yes on any such statement about S&M or marketing in the letter or call. Resolution 5 Nov 2026.

### B04 — bonus-host-churn-cited
**Title.** By the Feb print, will management or the 10-K/10-Q attribute slower active-listing growth, host attrition, or lower host pricing competitiveness to the single-fee migration, or disclose active listings growth ≤ +3% y/y?
**Type.** Binary. **Resolution.** Yes on either. Resolution ~11 Feb 2027.

### B05 — bonus-eu-regulation-hit
**Title.** By 11 Feb 2027, will a new short-term-rental restriction take effect or be enacted in an EU/UK city or country whose Airbnb nights exceed 1% of EMEA nights (e.g., a Barcelona-style licence withdrawal, a national registration regime with removal of unregistered listings, or the EU Affordable Housing Act with binding STR caps)?
**Type.** Binary. **Resolution.** Yes if enacted (not proposed) with an effective date on or before 30 Jun 2027 and the affected market ≥1% of EMEA nights by the team's regional panel. Resolution 11 Feb 2027.

### B06 — bonus-geopolitical-headwind-cited
**Title.** At the 5 Nov print, will management cite the Middle East conflict or another geopolitical event as a headwind to 3Q26 or 4Q26 nights of ≥0.5 point, or as a named reason for the 4Q26 guide?
**Type.** Binary. **Resolution.** Yes on a quantified drag ≥0.5pt or an explicit attribution in the guide paragraph. Resolution 5 Nov 2026.

### B07 — bonus-us-inbound-falls
**Title.** Will NTTO's overseas (non-Canada/Mexico) visitor arrivals to the US for 4Q26 be ≤ −5% y/y?
**Type.** Binary. **Resolution.** Yes if the sum of Oct–Dec 2026 overseas arrivals (NTTO I-94 monthly) ÷ Oct–Dec 2025 − 1 ≤ −0.05. Resolution ~Feb 2027 when December data posts.

### B08 — bonus-ai-hosting-cost-step
**Title.** By the Feb print, will management quantify incremental AI/hosting/infrastructure spend for FY27 of ≥$50M, or will 4Q26 cost of revenue grow ≥ +18% y/y?
**Type.** Binary. **Resolution.** Yes on either (4Q25 cost of revenue $487M; threshold $575M). Resolution ~11 Feb 2027.

### B09 — bonus-sbc-step-up
**Title.** Will 4Q26 stock-based compensation be ≥ $500M?
**Type.** Binary. **Resolution.** Yes if 4Q26 SBC per the 4Q26 release ≥ $500M (4Q25 $400M; team path $465M). Resolution ~11 Feb 2027.

### B10 — bonus-interest-income-falls
**Title.** Will 4Q26 interest income be ≤ 90% of 4Q25's?
**Type.** Binary. **Resolution.** Yes if 4Q26 interest income ≤ 0.90 × 4Q25 interest income (4Q26 release / 10-K). Resolution ~11 Feb 2027.
**Fine print.** Mechanism: RNPL reduces funds held for clients; rates. Use M7's interest-income rule (0.876 × 3m T-bill × earning base) and the RNPL funds-held overlay.

### B17 — bonus-take-rate-guided-down
**Title.** At the 5 Nov print, will management guide 4Q26 or FY27 take rate lower (any statement that take rate will be down y/y, or that incentives/new businesses will reduce it)?
**Type.** Binary. **Resolution.** Yes on any such forward statement. Resolution 5 Nov 2026.

### B11 — bonus-sellside-downgrades
**Title.** Between 17 Sep and 15 Dec 2026, will ABNB receive ≥3 rating downgrades from firms in the tracked feed?
**Type.** Binary. **Resolution.** Yes if ≥3 downgrades (to Hold/Sell-equivalent) in the feed convention of `data/processed/reverse_dcf/D/`. Resolution 15 Dec 2026.

### B12 — bonus-fy27-investment-year
**Title.** At the Feb print, will management guide FY27 adjusted EBITDA margin down year over year versus FY26 actual, or explicitly frame 2027 as an investment year with margin below FY26?
**Type.** Binary. **Resolution.** Yes if the FY27 margin floor/point is below the FY26 reported margin, or the letter/call says margin will be down/lower in 2027. Resolution ~11 Feb 2027.

### B13 — bonus-q4-nights-print-weak
**Title.** Will 4Q26 Nights and Seats Booked growth print ≤ +7.5% y/y?
**Type.** Binary. **Resolution.** Yes if 4Q26 nights ≤ 131.0m. Resolution ~11 Feb 2027.

### B14 — bonus-weather-event
**Title.** Between 17 Sep 2026 and 31 Dec 2026, will a hurricane or other natural disaster be cited by Airbnb management as reducing nights or GBV, or will a Category 3+ hurricane make US landfall in Florida, Texas or the Carolinas?
**Type.** Binary. **Resolution.** Yes on either condition (NHC landfall record; letter/call citation). Resolution 31 Dec 2026 (management citation counted through the Feb print).

### B15 — bonus-q4-us-revpar-soft
**Title.** Will STR's US hotel RevPAR growth for 4Q26 be ≤ +1% y/y?
**Type.** Binary. **Resolution.** As R11 with threshold ≤ 1.0%. Resolution ~25 Jan 2027.

### B16 — bonus-insider-selling
**Title.** Between 17 Sep 2026 and 31 Jan 2027, will Airbnb insiders (Form 4 filers) sell ≥ $150M of stock in aggregate, or will a new 10b5-1 plan for the CEO be disclosed?
**Type.** Binary. **Resolution.** Yes on either (SEC Form 4s; disclosure in a 10-Q/8-K). Resolution 31 Jan 2027.

## Synthesis

### X01 — scenario-probabilities
**Title.** What are the probabilities of the memo's three scenarios for the 5 Nov print: thesis breaker (accelerating print ≥10.6% nights with the 4Q26 bucket at "low double digits" or better), base (decelerating print with the 4Q26 nights bucket at "high single digits"/"around 10" and/or the revenue guide midpoint below Street), short case (nights ≤8.5% or 4Q26 bucket "mid single digits" or lower, or FY26 margin floor weakened)?
**Type.** Multiple choice over {thesis breaker, base, short case, none of the above (e.g., in-line print with in-line guide)}.
**Fine print.** Must be coherent with C01, C02, C04, R01, R02 and S01 (state the joint structure and the correlations assumed). Runs last; reads every `forecasts/*.json`. Resolution 5 Nov 2026.
