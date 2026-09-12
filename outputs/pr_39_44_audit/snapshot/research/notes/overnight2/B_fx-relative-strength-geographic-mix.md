# B. Relative currency strength and Airbnb's geographic travel mix, applied to 3Q26 and 4Q26

- **Date:** 2026-09-11. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Question:** does relative currency strength move *where* Airbnb's guests travel, separately from the translation effect on reported ADR and revenue that WS05 already measured, and what does the FX actually observed through 4 September 2026 imply for 3Q26 and 4Q26?
- **Scripts:** `analysis/src/overnight2/B1_fx_relative_strength.py`, `B2_regional_target_panel.py`, `B3_mix_tests.py`, `B4_application_3q26_4q26.py` (all `py -3.13`).
- **Outputs:** `data/processed/overnight2/B/` (18 CSVs plus a 22-series FRED cache), listed in section 6.
- **Does not redo:** WS05's translation fits (`05_fx_fits.csv`), WS28's hedge disclosures, WS10's regional panel, WS27's bucket placement. This note uses all four as inputs.

---

## 1. Bottom line

1. **The mix channel is real and it is small.** A region's nights growth differential against the company total moves about **0.11 percentage points per 1 percentage point** of its inbound cross-border purchasing-power index, pooled across the four regions with region fixed effects (n 28 over the disclosed-bucket era, r 0.40, permutation p 0.038, leave-one-out RMSE 1.59 against 2.15 naive). On the wider window the same slope is 0.085 and loses significance (n 40, perm p 0.16). The honest range is **0.09 to 0.21 pp per pp**, and that is an elasticity on a *differential*, not on total nights.

2. **At current spot that buys almost nothing for the print.** Observed FX to 4 September plus flat spot gives FX-mix swings against 2Q26 of **North America -0.31 pp, EMEA +0.16, Latin America +0.32, Asia Pacific -0.28** in 3Q26, and **-0.19 / +0.11 / +0.45 / -0.58** in 4Q26 (base elasticity). Share-weighted they cancel to zero by construction, and the implied effect on reported ADR through nights mix is **-0.06 pp in 3Q26 and -0.04 pp in 4Q26** against a structural mix drag of **-1.20 pp**. The translation channel is twenty to forty times larger than the mix channel. **The team nights baseline of 9.9 / 8.9 does not move on this work.**

3. **The one well-identified piece of the mechanism is the American traveller, not the foreign one.** On BEA real travel spending, the **inbound-minus-outbound gap** is explained by the NA cross-border purchasing-power index at a **two-quarter lag**: n 10 on the clean window, r +0.89, slope +2.10 pp per pp, permutation p 0.001, and it beats both the naive and the leave-one-out-mean benchmarks. Decomposed, **US outbound spending responds with the right sign** (oa index, r +0.77, perm p 0.007 to 0.012) while **US inbound spending has the wrong sign** (r -0.49, perm p 0.13 to 0.15, and r -0.69 if you leave the reopening years in). The dollar moves where Americans go. It did not measurably move whether foreigners came to the United States in 2025 and 2026, because the visa fee, the tariff headlines and the Canadian boycott moved in the opposite direction to the dollar over exactly that window. **The FX mix effect on US inbound is not identified, and the confound is not small.**

4. **The two-quarter lag is the same lag WS05 found in revenue FX, from the same cause.** Bookings are made one to two quarters before the stay, and Reserve Now Pay Later has lengthened that. A corridor decision responds to the exchange rate at booking, so a mix model that uses contemporaneous spot is mis-specified in the same way WS05's contemporaneous revenue-FX fit was. This is the main methodological carry-forward.

5. **The Europe destination test fails, and it fails informatively.** Eurostat's EU27 platform nights by residence of guest is the only third-party series that measures a destination's origin mix directly. Its foreign share moves with the *wrong* sign against the EMEA inbound index at every level lag (r -0.64 to -0.82, n 13, perm p 0.001 to 0.027) and with the *right* sign in first differences (r +0.66 to +0.72). A level relationship that flips under the difference guard is a trend artefact. The likely reason the test is mismatched: Eurostat "foreign" includes intra-European travel, which is the large majority of it and for which the euro cross is irrelevant. **A better EMEA test needs origin-country data Eurostat does not publish.**

6. **Corridor by corridor, the 2026 story is that the 2025 long-haul dislocation has unwound.** US-to-eurozone purchasing power was -10.5% y/y in 1Q26, the worst corridor reading in the panel, and is **+1.2% in 3Q26 and +0.2% in 4Q26** on flat spot. Its mirror, eurozone-to-US, goes from +10.5% to -1.2% and -0.2%. Mexico-to-US and Brazil-to-US stay strongly positive (+8.4 and +6.0 in 3Q26), so the cheap-US corridor for Latin American guests persists. The worst corridors in the book are **India-to-APAC (-16.8%)** and India-to-eurozone (-7.5%), and India is the fastest-growing origin country in the company at +60% y/y. That single pair is the cleanest evidence that FX is not what drives Airbnb's origin growth.

7. **There is a genuine correction to the ADR-FX call for 4Q26, and it comes from the geographic mix.** WS05's EUR-only fit gives ADR FX of **-1.1 pp in 3Q26 and -0.7 pp in 4Q26**. A bottom-up build from the four destination baskets and WS10's pass-throughs, with **no parameters fitted to this target**, gives **+0.3 pp and +1.0 pp**, because the Latin American basket is still +6.7% and +6.2% y/y and the APAC basket +2.2% and +5.3% while EMEA is flat. On the 17 quarters where the letters disclose the FX effect on ADR, the unfitted basket build has RMSE 0.535 pp against 0.458 pp for the two-parameter EUR fit and 0.868 pp for the broad-dollar fit. **Call 3Q26 ADR FX -1.1 to +0.3 pp and 4Q26 -0.7 to +1.0 pp, and say which estimator is being used.** The 4Q26 disagreement, about 1.7 pp on reported ADR, is larger than anything the mix channel does to nights.

8. **Cross-border share: direction is flat, and it is not identified.** The index says nothing is pushing either way (the share-weighted cross-border purchasing-power index is -1.79 in 2Q26, -1.32 in 3Q26 and -1.48 in 4Q26, and dispersion across destinations narrows). The test cannot be run properly: Airbnb stopped disclosing the cross-border share of gross nights after **1Q24 at 46%**, the 2021 to 2024 series is a reopening ramp, and the four 2019 observations (51, 50, 48, 47) are one year of a strong seasonal shape. Best fit r 0.51, perm p 0.07.

9. **Management's FX assumption for the Q3 guide is one sentence and it has no stated basis.** The 6 August 2026 letter and call both say the $4.69 to $4.77bn revenue guide is *"inclusive of an approximate three percentage point FX tailwind after factoring in our hedging program."* No spot assumption, no rate, no sensitivity is given. WS28 showed the hedge is on the loss side at roughly -0.2 pp a quarter, so gross of hedging management is carrying about **+3.2 pp**. The refreshed lagged fit gives **+2.2 pp gross and +2.0 pp after hedge** for 3Q26, so management's number is about 1 pp above the fit, within the fit's own stated +/-0.8 pp spread plus rounding. **For 4Q26 the same arithmetic gives -0.4 pp gross and -0.6 pp after hedge, a swing of about 2.5 pp against the Q3 rate. About 86% of that driver is already observed FX rather than a forecast (2Q26 complete plus 47 of 65 business days of 3Q26); WS05 recorded 84% on its 28 August vintage.**

---

## 2. Tables

### 2.1 The index, by quarter (cross-border leg only, percentage points y/y)

`ipp_xb_d` is the origin-weighted change in origin purchasing power inside destination region d, dropping the intra-regional leg. Positive means the destination got cheaper for its inbound guests than a year ago.

| Quarter | NA | EMEA | LatAm | APAC | US outbound affordability | Disclosed context |
|---|---|---|---|---|---|---|
| 1Q19 | -6.6 | +4.3 | +6.5 | +2.3 | +7.2 | cross-border 51% of gross nights |
| 3Q22 | -9.4 | +12.2 | -4.3 | +4.0 | +9.9 | euro at parity; cross-border 43% |
| 1Q24 | +0.5 | -1.9 | -6.1 | +6.6 | -1.6 | cross-border 46%, last disclosure |
| 4Q24 | -3.0 | -2.8 | +13.7 | -0.8 | +3.4 | BEA inbound +7.6%, outbound +14.0% |
| 1Q25 | -4.9 | -1.5 | +14.5 | +0.7 | +5.4 | BEA inbound -0.4%, outbound +9.7% |
| 3Q25 | +2.5 | -5.2 | -0.4 | +4.1 | -3.0 | BEA inbound -8.6%, outbound +5.2% |
| 1Q26 | **+6.9** | -6.3 | -8.6 | +1.4 | **-8.2** | BEA inbound -4.8%, outbound -3.4% |
| 2Q26 | +3.1 | -0.4 | -10.1 | +0.3 | -4.1 | BEA inbound -0.4%, outbound -3.7% |
| **3Q26 flat spot** | **+0.8** | **+1.7** | **-6.6** | **-0.9** | **-1.5** | no ABNB read yet |
| **4Q26 flat spot** | **+2.2** | **+1.4** | **-5.4** | **-4.1** | **-0.6** | no ABNB read yet |

The 3Q26 intra-quarter path (`B_intraquarter_3q26_path.csv`): NA moved from -0.38 on 1 July to +0.79 on 4 September, EMEA from +2.17 to +1.72, LatAm from -5.70 to -6.52, APAC from +0.51 to -0.88. The quarter has drifted toward a stronger dollar since July, which is why NA improves and APAC deteriorates as the quarter runs.

### 2.2 The fits that matter (`B_mix_fits.csv`, 146 fits in total)

| Target | Driver | Window | n | Slope | r | Perm p | LOO RMSE vs naive | Verdict |
|---|---|---|---|---|---|---|---|---|
| BEA US inbound minus outbound spend (pp) | `ipp_xb_na` lag 2 | 2019 plus from 1Q24 | 10 | +2.10 | +0.89 | 0.001 | 3.88 vs 5.08 | holds; the mechanism test |
| BEA US outbound spend y/y | `oa_na` lag 0 | 2019 plus from 1Q24 | 10 | +5.70 | +0.77 | 0.012 | 5.04 vs 3.42 | right sign, does not beat naive |
| BEA US inbound spend y/y | `ipp_xb_na` lag 0 | 2019 plus from 1Q24 | 10 | -1.38 | -0.49 | 0.136 | 10.32 vs 5.13 | **wrong sign, not significant** |
| Eurostat EU27 foreign share change (pp) | `ipp_xb_emea` lag 1 | 2019 plus from 1Q24 | 13 | -0.197 | -0.82 | 0.001 | 0.56 vs 0.81 | **wrong sign; flips in differences** |
| ABNB NA nights differential (pp) | `ipp_xb_na` lag 0 | from 4Q24 | 7 | +0.43 | +0.83 | 0.025 | 1.68 vs 1.86 | right sign, n 7, confounded |
| ABNB LatAm nights differential (pp) | `ipp_xb_latam` lag 1 | 2019 plus from 1Q24 | 10 | +0.14 | +0.59 | 0.072 | 2.00 vs 2.71 | right sign, weak |
| ABNB EMEA nights differential (pp) | `ipp_xb_emea` lag 1 | post-2022 | 16 | +0.21 | +0.49 | 0.043 | 2.86 vs 3.30 | right sign, weak |
| ABNB APAC nights differential (pp) | `ipp_xb_apac` lag 0 | from 4Q24 | 7 | -0.59 | -0.86 | 0.020 | 0.83 vs 1.93 | **wrong sign; flips to +0.40 at n 16** |
| ABNB pooled differential, region-demeaned | `ipp_xb` lag 0 | from 4Q24 | 28 | **+0.113** | +0.40 | 0.038 | 1.59 vs 2.15 | **the elasticity used** |
| ABNB pooled differential, region-demeaned | `ipp_xb` lag 0 | 2019 plus from 1Q24 | 40 | +0.085 | +0.23 | 0.156 | 1.95 vs 2.17 | same sign, not significant |
| ABNB cross-border share (%) | `ipp_xb` global equal-weight | ex-covid | 13 | +2.30 | +0.51 | 0.073 | | not identified |

### 2.3 Application to 3Q26 and 4Q26 (`B_mix_application_regional.csv`, `B_mix_application_total.csv`)

FX-mix swing against 2Q26, in percentage points of regional nights growth, base elasticity 0.113 with the 0.085 to 0.211 range in brackets:

| Region | Nights share | 3Q26 swing | 4Q26 swing | Why |
|---|---|---|---|---|
| North America | 28.3% | **-0.31** (-0.23 to -0.57) | **-0.19** (-0.14 to -0.35) | the dollar's 1Q26 weakness has faded; eurozone-to-US goes +10.5% to -1.2% |
| EMEA | 41.6% | **+0.16** (+0.12 to +0.29) | **+0.11** (+0.08 to +0.20) | US-to-eurozone turns from -10.5% to +1.2%; Brazil-to-eurozone +7.3% |
| Latin America | 17.9% | **+0.32** (+0.24 to +0.59) | **+0.45** (+0.34 to +0.83) | BRL and MXN strength decelerates, so the region is less expensive than in 2Q26 |
| Asia Pacific | 12.3% | **-0.28** (-0.21 to -0.52) | **-0.58** (-0.44 to -1.08) | AUD is 55% of the APAC destination basket and is +7.4% to +9.3% vs USD |
| **Share-weighted total** | 100% | **0.0** | **0.0** | zero by construction: the term reallocates, it does not create nights |
| Reported ADR, mix term | | **-0.06** FX increment on a **-1.20** structural drag | **-0.04** on **-1.20** | |
| **Team baseline, comparison only** | | **9.9%** | **8.9%** | unchanged by this work |

### 2.4 Refreshed FX translation schedule (`B_fx_translation_schedule_refresh.csv`)

Observed daily rates to 4 September 2026, flat spot for the remaining 18 business days of 3Q26 and all of 4Q26.

| Quarter | EUR/USD avg | EUR y/y | Broad USD y/y | ADR FX from EUR fit | ADR FX from broad fit | ADR FX from regional baskets | Revenue FX gross | Hedge | Revenue FX after hedge |
|---|---|---|---|---|---|---|---|---|---|
| 1Q26 actual | 1.170 | +11.1% | -6.7% | +4.45 | +5.33 | **+5.06** | | | disclosed +3 |
| 2Q26 actual | 1.163 | +2.6% | -2.5% | +0.59 | +2.34 | **+1.70** | | | disclosed +4 |
| **3Q26** | 1.154 | **-1.2%** | -0.9% | **-1.12** | +1.14 | **+0.26** | **+2.19** | -0.21 | **+1.98** (guide ~+3.0) |
| **4Q26** | 1.162 | **-0.2%** | -2.2% | **-0.66** | +2.11 | **+0.97** | **-0.36** | -0.21 | **-0.57** |

Disclosed ADR FX was +5.0 in 1Q26 and +1.3 in 2Q26. Regional-basket y/y in 3Q26 and 4Q26: NA +0.07 / +0.22, EMEA -0.85 / +0.26, LatAm +6.72 / +6.15, APAC +2.17 / +5.31. The **3Q26 to 4Q26 revenue-FX swing is about -2.5 pp**, slightly smaller than WS05's -3.4 pp because 3Q26 spot firmed through the quarter.

---

## 3. Method

**Indices.** 22 FRED daily series are pulled fresh (`B/fred/`), converted to USD per unit of foreign currency, and averaged by calendar quarter. Each region gets a **destination** currency basket (the listing-side basket, carried over from WS10's `10_fx_basket.csv` so that WS10's fitted ADR pass-throughs stay usable) and an **origin** currency basket (new: the currency a guest from that region earns in, wider than the destination basket because origin demand in EMEA and APAC spans more currencies than supply does). All basket levels are geometric weighted averages. Then

- inbound purchasing power, destination d: `IPP_d = sum_o w[o,d] * ( dlog(USD per origin basket o) - dlog(USD per destination basket d) )`
- outbound affordability, origin o: `OA_o = sum_d v[o,d] * ( dlog(USD per origin basket o) - dlog(USD per destination basket d) )`

with `v` derived from `w` and the regional nights shares so the two sides are arithmetically consistent. The `_xb` variants drop the intra-regional leg and renormalise, which is what the tests use, because the intra-regional leg is close to zero by construction and simply scales the index down by a factor of six to eight.

**Origin weights (`B_index_weights.csv`), and the evidence for them.** The origin mix of each destination region's nights is judgement, anchored on: cross-border travel was 46% of gross nights in 1Q24 and 51% in 1Q19 (letters); *"only a single-digit percentage of global nights booked are international inbound to the U.S."* (1Q25 letter) and 2 to 3% on the 1Q25 call; *"the majority of travel in North America, both pre-pandemic and now, is domestic"* (4Q22 letter); *"cross-border continues to drive the majority of nights booked in APAC"* (4Q24 letter), with cross-border nights to APAC growing 22 to 29% y/y in 2023 and 2024; Eurostat foreign-residence nights at 57 to 67% of EU27 platform nights, the large majority intra-European; and NTTO, which puts Canada and Mexico at 48.6% of 2025 US inbound arrivals against 51.4% overseas. The resulting non-domestic weights are NA 12%, EMEA 16%, LatAm 20%, APAC 20%. I could not retrieve a UNWTO intra-regional share table for Europe or Asia Pacific from a primary document; the Europe weight rests on the Eurostat split plus the long-standing observation that European arrivals are predominantly intra-European, and is flagged as the weakest weight in the set.

**Nights shares use the corrected figures, not WS10's.** `research/notes/2026-09-07_adr-decomposition.md` found that WS10's regional ADR index has LatAm and APAC swapped (it uses LatAm 0.68 and APAC 0.59; the 10-K gives 0.554 and 0.690 for 2025), so the nights shares calibrated on it understate LatAm by about a fifth. This note uses the rebuilt 2Q26 shares from `data/processed/adr/04_regional_quarterly.csv`: NA 28.26%, EMEA 41.55%, LatAm 17.86%, APAC 12.33%, against WS10's 28.8 / 39.7 / 15.1 / 16.3. Regional ADR levels are the FY2025 10-K values: NA $255, EMEA $159, LatAm $95, APAC $118, global $171.

**Target panel.** `regional_target_panel.csv` is 997 long-format rows across 41 periods, every row carrying a basis and a source and, where it is a disclosure in prose, the sentence. It combines WS10's letter extraction (regional nights growth as numeric, bucket midpoint or derived residual; regional reported and ex-FX ADR; cross-border share and growth; cross-border growth to NA, EMEA and APAC; origin-country growth for Brazil, India, Japan, Mexico and China outbound), WS05's 2019 cross-border share comparators, annual revenue by geography from 10-K XBRL for FY2019 to FY2025, BEA inbound and outbound travel spending, and Eurostat EU27 platform nights split by residence of guest. 15 hand-curated corridor and guide sentences are added with full quotes.

**Tests.** Every pair is fitted by OLS at lags 0, 1 and 2 on four windows, with a 1,000-shuffle permutation p on the absolute correlation and leave-one-out RMSE against naive-last-value and leave-one-out-mean benchmarks, the same shape as `05_fx_fits.csv`. A **first-difference guard** refits quarter-on-quarter changes on both sides; a level relationship that flips sign or collapses under the guard is treated as a shared trend. The primary windows exclude the reopening years: BEA travel spending ran +200% to +20% y/y from 1Q21 to 4Q23 and Eurostat foreign nights the same, so the primary window is **2019 plus 1Q24 onward**. Fits on the full and post-2022 windows are retained in the CSV and flagged, because they are where the spurious results live.

**Pooling.** The four regional differentials are pooled with both sides demeaned by region, which is a region fixed-effects regression and removes the permanent level gaps (LatAm always above the total, NA always below) that would otherwise dominate.

**Application.** The regional index is demeaned by the nights-share-weighted mean before the elasticity is applied, so the mix term reallocates growth between regions and contributes exactly zero to total nights. The reported-ADR mix term is the change in the nights-weighted blend of the FY2025 regional ADR levels implied by the regional growth rates, holding regional ADR fixed.

---

## 4. What this can and cannot identify

**Can.**
- That relative currency strength moves the *American* traveller's corridor choice, on the BEA inbound-minus-outbound gap, at a two-quarter lag, with a slope and a confidence interval.
- That the same lag structure WS05 found in revenue FX applies to mix, for the same booking-date reason.
- The sign and rough size of the FX-mix term for each region in 3Q26 and 4Q26, to within a factor of about two on the elasticity.
- That the mix channel is one to two orders of magnitude smaller than the translation channel for every line the pitch cares about.
- That the ADR-FX estimator choice matters more for 4Q26 than the whole mix channel does, and which estimator is unfitted.

**Cannot.**
- **Separate FX from US travel policy in 2025 and 2026.** The dollar fell while the $250 visa integrity fee, tariff headlines and a Canadian consumer boycott all pushed US inbound the other way. The inbound-alone fit has the wrong sign and the gap fit works mainly through the outbound leg. No instrument is available in this data.
- **Separate FX from Airbnb's own product cycle.** The NA differential improved from -7.4 pp (4Q24) to -1.2 pp (1Q26) over the same quarters in which the dollar fell *and* Reserve Now Pay Later, the cancellation redesign and the single fee were rolled out in North America first. The n 7 NA fit at r +0.83 cannot distinguish them, and the team's own reconciliation attributes roughly 3 points of 1Q26 nights growth to the product bundle. **Treat the NA fit as an upper bound on the FX contribution, not an estimate of it.**
- **Say anything about APAC.** The sign flips with the window (-0.59 at n 7, +0.40 at n 16). India is the fastest-growing origin country in the company at +50 to +60% y/y with the two worst corridor FX readings in the panel (India-to-APAC -16.8%, India-to-eurozone -7.5%), and Japan inbound is flat to negative despite Australia-to-Japan purchasing power up 10.7 to 15.7%, because Chinese arrivals collapsed for political reasons. Both are direct counterexamples to the mechanism in the region where it should be largest.
- **Test the cross-border share.** The disclosure stops at 1Q24. The 2021 to 2024 series is a reopening ramp and the four 2019 points are one year of a seasonal shape (51, 50, 48, 47 through the year). The direction call in section 1.8 is the index speaking, not a fitted relationship.
- **Test EMEA properly.** Eurostat's "foreign" residence category is dominated by intra-European travel, for which the euro cross does nothing. The wrong-sign level result and the right-sign difference result together say the test is mismatched, not that the mechanism is absent.
- **Validate the origin weights against primary data.** They are judgement against eight disclosed or third-party anchors. No origin-by-destination matrix for Airbnb exists publicly. Doubling the long-haul weights roughly doubles every index reading and therefore halves the fitted elasticity, leaving the *applied* mix term unchanged to first order, which is the one reassuring property of the construction.
- **Use FX later than 4 September 2026.** The Federal Reserve H.10 release had not published past 4 September when this ran (7 September 2026 was the Labor Day holiday), so "observed to 10 September" is in practice observed to 4 September with flat spot for the remaining 18 business days. EUR/USD at 1.1618 on 4 September matches WS05's independently recorded spot of 1.16143 for that date.

**Preserved evidence that weakens the hypothesis.** Management has twice said the opposite of this note's thesis in writing: *"Even with foreign currency fluctuations, we saw cross-border travel to all regions increase in Q3 2022 from last year"* and *"Globally, we saw cross-border travel to all regions increase in Q4 2022 from last year despite continued foreign currency volatility."* Those are the two quarters with the largest currency dispersion in the sample. The 4Q23 letter adds that *"cross-currency transactions only make up a portion of cross border bookings."* All three point the same way: Airbnb's own view is that FX does not redirect its guests much. This note's measured elasticity of 0.11 pp per pp is consistent with management being roughly right.

---

## 5. Next evidence

1. **The 5 November letter's regional paragraph and any corridor sentence.** The specific thing to read for is whether EMEA accelerates while NA decelerates, which is the sign this note predicts from FX at about 0.3 to 0.5 pp of differential, and which is small enough that the product lap will swamp it. Also whether the cross-border share is reinstated.
2. **The disclosed ADR FX effect for 3Q26.** It arbitrates the estimator disagreement directly: the EUR fit says -1.1, the regional-basket build says +0.3. One observation resolves a 1.7 pp question for 4Q26.
3. **BEA PCE travel by function for 3Q26** (month three lands about a week before the print). The inbound-minus-outbound gap is the live test of the two-quarter-lag fit and the only place this note has a forecastable relationship.
4. **Eurostat tour_ce_omr for 2Q26 and 3Q26.** The series runs about 150 days late; 2Q26 should publish in the autumn. It will not fix the intra-European contamination but it extends n.
5. **NTTO country-of-residence monthlies for 2026.** The Excel files behind the trade.gov summaries give US inbound by origin market, which would replace the judgement origin weights for North America with measured ones. This is the single highest-value data pull left on this workstream and it was not completed here.
6. **Ask on the call:** what share of gross nights is now cross-border, and has the company seen corridor substitution respond to the dollar. The 2022 quotes suggest management will say no, which is itself the answer the model needs.

---

## 6. Files

**Scripts** (`analysis/src/overnight2/`): `B1_fx_relative_strength.py`, `B2_regional_target_panel.py`, `B3_mix_tests.py`, `B4_application_3q26_4q26.py`.

**Outputs** (`data/processed/overnight2/B/`):

| File | Contents |
|---|---|
| `regional_target_panel.csv` | 997 rows, 41 periods: regional nights growth and differentials, regional ADR reported and ex-FX, regional and annual revenue by geography, cross-border share and growth, corridor and origin-country disclosures, BEA inbound and outbound, Eurostat EU27 residence split, each with basis, source and quote |
| `B_relative_strength_quarterly.csv` | the indices by quarter 1Q18 to 3Q26: `ipp_*`, `ipp_xb_*`, `oa_*`, `oa_xb_*`, destination and origin basket y/y, dispersion, USD-versus-rest |
| `B_index_weights.csv` | every weight used: origin mix of each destination, destination mix of each origin, and both currency baskets |
| `B_corridor_relative_strength_quarterly.csv`, `B_corridor_forward_flat_spot.csv` | 20 named bilateral corridors by quarter, plus the flat-spot 3Q26 and 4Q26 readings |
| `B_intraquarter_3q26_path.csv` | every index on a cumulative quarter-to-date basis for each trading day of 3Q26 to 4 September |
| `B_forward_flat_spot_indices.csv` | 3Q26 and 4Q26 indices under observed-plus-flat-spot |
| `B_mix_fits.csv` | all 146 fits with slope, r, p, Spearman, permutation p and three RMSEs |
| `B_alignment_table.csv` | the indices next to BEA, Eurostat and ABNB regional differentials by quarter, for eyeballing |
| `B_pooled_regional_differential_inputs.csv` | the pooled regression inputs with the basis of each ABNB observation |
| `B_mix_application_regional.csv`, `B_mix_application_total.csv` | the 3Q26 and 4Q26 overlay by region and in total, three elasticity cases |
| `B_fx_translation_schedule_refresh.csv` | refreshed ADR and revenue FX for 1Q26 to 4Q26, three ADR estimators, destination basket y/y, hedge line |
| `B_adr_fx_estimator_backtest.csv` | the three ADR-FX estimators against the disclosed letter FX effect, 2Q22 to 2Q26 |
| `B_cross_border_direction_card.csv` | the cross-border direction call and why it is not identified |
| `B_fx_daily_usd_per_unit.csv`, `B_fx_quarterly_avg.csv`, `B_fx_quarterly_yoy_logpct.csv`, `B_fx_meta.json` | the FX panel and its vintage |
| `fred/` | 22 cached FRED series: DEXUSEU, DEXUSUK, DEXUSAL, DEXUSNZ, DEXCAUS, DEXMXUS, DEXBZUS, DEXJPUS, DEXKOUS, DEXINUS, DEXCHUS, DEXSZUS, DEXSDUS, DEXNOUS, DEXDNUS, DEXTHUS, DEXSIUS, DEXTAUS, DEXHKUS, DEXMAUS, DEXSFUS, DTWEXBGS |

**Read-only inputs from the main tree:** `data/processed/overnight/10_regional_panel_quarterly.csv`, `10_regional_quotes.csv`, `10_xbrl_revenue_geography.csv`, `10_fx_basket.csv`, `05_crossborder_share.csv`, `05_regional_growth.csv`, `05_macro_quarterly_panel.csv`, `05_fx_fits.csv`, `28_fx_hedge_forward.csv`, `data/processed/adr/01_regional_annual.csv`, `04_regional_quarterly.csv`, `data/processed/eurostat_platform_nights_monthly.csv`, `data/raw/letters/2Q26_d70413dex991.htm`, `data/raw/transcripts/web/2Q26.html`.

