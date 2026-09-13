# X — regional kernel and origin–destination FX

**underpowered** — accounting and software checks pass, but measured Airbnb exposure and point-in-time forecast validation do not. The regional scenarios retain a positive FX tailwind that fades into Q4. They do **not** justify superseding B4. This note's pass line was created before estimation on 12 September 2026; no team modelling decision is adopted.

## Pre-registered pass line

Annual regional lambda must reproduce revenue / GBV from the supplied 10-K summary to disclosed rounding. The regional reconstruction must sum to consolidated revenue within 0.3% in every quarter. An independently measured, dated origin–destination exposure matrix must move the fitted gross FX scale toward the disclosed 0.56 non-USD share, with a reported confidence interval. Regional 3Q26 FX must be reported beside management's approximately +3.0pp after-hedge guide assumption, with the basis aligned and differences allocated by region. Both W1 and W2 must be reported. A reconstruction identity is not a forecasting test. An assumed exposure sensitivity cannot pass the measured-exposure criterion.

The quarterly ADR table is explicitly modelled. The supplied L1 v2 directory has annual/FY27 summary files but no historical regional GBV estimates with intervals. X therefore uses the supplied ADR table and disclosed letter bands for a transparent retrospective reconstruction and labels any additional envelope as a sensitivity, not a statistical confidence interval. Modern arrivals releases and current analytical reconstructions are not backdated into historical guide origins.

## Planned commands

`python analysis/src/forecast_methods/regional_kernel_v1/run.py`

`python -m pytest analysis/src/forecast_methods/regional_kernel_v1/tests -q`

## Results and verification

Annual ratio check **24/24**, maximum error against the supplied annual ratio **1.8e-15pp**. Exact regional revenue cells **72/72**; quarter sums **18/18**, maximum error **0.000%**. The latter is an accounting identity because each cell's revenue defines its lambda; it is not forecasting validation. Measured Airbnb O-D currency cells **0**; eligible historical guide forecasts **0/14 W1, 0/10 W2**. The exposure and forecast parts of the pass line are not met.

The final portable rebuild exits 0 in 22.8 seconds (wall time varies with concurrent packages). The module suite has **19 passing tests**: publication-date refusal, separate exposure-share sums, migration endpoints, country versus regional cross-border arithmetic, public control totals, FX removal, hedge-once order, interval likelihood. See `run_log.txt` and `pytest.txt`. One development assertion compared a computed 0.6000000000000001 grid endpoint to 0.6 without numerical tolerance; it was corrected to a 1e-12 comparison tolerance. No data, analytical pass line or likelihood threshold changed. A final source check also found a finite NA pass-through slope explicitly flagged unidentified; it is excluded, defaults to the documented unit sensitivity, and is covered by a regression test. A note-formatting attempt lacked optional `tabulate`; tables were rendered without that dependency. No scorer or frozen source was modified. Parent owns frozen harness/L0 checks and scoring.

### Annual ratios, quarterly identification and drift

The tables appended below show annual measured revenue/GBV and quarterly seasonal coefficients. Annual ratios include rounding envelopes at the disclosed dollar precision. Annual revenue/GBV is **not** a quarterly recognition coefficient. The quarterly estimate uses the 2025 annual ratio times the mean 2023+ same-season factor: four observations per region for Q1/Q2, three for Q3/Q4.

The quarterly ADR source explicitly labels annual-anchor seasonal levels as modelled and other levels as derived. X multiplies nights by anchored ADR and reconciles regional GBV to the supplied consolidated GBV. The sensitivity envelope combines disclosed nights-growth bands with **assumed +/-10% ADR**; where no numerical nights band exists, +/-5% nights is a sensitivity fallback. These are not confidence intervals or an L1 posterior. The 16 region-season coefficients and their envelopes are in `regional_lambdas_k0.csv`; all 72 identities are in `lambda_regional.csv`.

The annual file's `source_10k` does not provide an exact filing publication date. Current reconstruction is stamped **2026-09-12**, never backdated to a historical guide. The 72 same-cell ratios do not constitute 72 independent forecasts.

From 2023Q3 to 2025Q3, reconstructed NA lambda falls **0.58pp** while EMEA rises **0.31pp**; Q4 NA falls **0.63pp** while EMEA rises **0.56pp**. The assumed regional GBV shape can create these offsets. After seasonal demeaning, mix-only variance is **3.07% / 2.15%** of total lambda variance in W1/W2 (14/10 quarters). Retrospective mix-only regression R-squared is **9.23% / 19.95%**; covariance allocation is **-5.32% / -6.55%**. Those answer different decomposition questions. None identifies a causal share of stability explained by mix. See `mix_variance_decomposition.csv` and `regional_drift.csv`.

### Public O-D evidence and currency assumptions

- [NTTO April-2026 report, 2025 actual table](https://www.trade.gov/sites/default/files/2026-05/NTTO-Spring-Forecast-2026.pdf): **68.288M** US inbound visitors; twelve named origins cover **77.19%** and **74.90%** maps to supplied FX currencies. Visitors are not Airbnb nights. The May URL supplies only a publication-month cue; June 1 is a conservative metadata cutoff, not a claimed exact release timestamp.
- [JAPAN NATIONAL TOURISM ORGANIZATION, 19 August 2026](https://www.jnto.go.jp/en/news/20260819.pdf): July arrivals **3,442,100**; classified origins cover **95.12%**, available currency matches **43.73%**. Nationality is not residence or settlement currency, and Japan is one APAC destination.
- [Eurostat platform nights API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tour_ce_omr?geo=EU27_2020&time=2025&indic_to=NGT_SP&unit=NR): HTTP 200, updated 2 July 2026; domestic/foreign nights **359,907,621 / 591,704,241**, or **62.18% foreign**. Foreign includes intra-European travel and identifies no currency. This constrains interpretation; it does not replace Airbnb's global cross-border share.

The numeric extracts and URLs are in `public_source_extracts.csv` and source-controlled `public_inputs.csv`. Public requests succeeded; rebuild is offline. The first Eurostat request used monthly values against the annual dimension and returned no data; corrected `time=2025` returned the cited data. No Airbnb website, UF database, licensed source or raw review store was accessed. Reviewer locale is **unavailable**, not measured zero.

`od_nights_matrix.csv` has four-by-four regional margins for each reconstructed/scenario quarter. Destination margins come from reconstructed Airbnb nights. The old **46% country-cross-border gross-nights share is a scenario**, not a 2026 observation. International travel within a region stays on the diagonal. US arrivals proxy NA origins; Japan arrivals proxy APAC; unresolved regions use current nights weights and unresolved currencies use destination-basket weights. EMEA/LatAm origins use current regional nights shares. Those allocations are assumptions.

GBV uses destination currency weights; fee revenue mixes origin and destination currency. Guest shares are **0, 0.5, 14.1/(14.1+3)=0.82456** of fee revenue. These are endpoints/midpoint, not measured migration penetration. At zero, revenue follows destination currency. Country, nationality and income currency do not establish payment currency. Separate GBV and revenue shares in `exposure.csv` each sum to one per geography-quarter. That is an executable **scenario** file. `fx_basket_measured.csv` deliberately contains null measured Airbnb weights and an unidentified status; `fx_basket_scenario.csv` carries the actual sensitivity weights. No measured replacement for the original basket is published.

### FX recompute, gross versus after-hedge, and the scale gap

The fixed 2/3 lag-one plus 1/3 lag-two kernel removes FX from lagged regional USD GBV and compares constant-FX revenue to the reported-dollar kernel. Percentage-point effects use prior-year revenue as denominator. **FX is never added again to a revenue forecast that already embeds booking-date USD rates.** The principal sensitivity assumes unit nominal-currency translation; the supplied regional ADR pass-through sensitivity is separately tabulated below.

The regional revenue scenario is **$4,754.7M Q3 / $3,248.3M Q4**. Q4 requires conditional Q3 regional GBV: mean of the two latest reconstructed regional y/y rates applied to the same-season base. These are scenario outputs, not adopted targets or quarterly regional disclosures.

| Guest fraction of fee revenue | Q3 gross FX | Q3 after hedge | Q4 gross FX | Q4 after hedge | Q4 minus Q3 |
|---|---:|---:|---:|---:|---:|
| 0 | +3.6 | +3.4 | +1.7 | +1.5 | -1.9 |
| 0.5 | +3.9 | +3.7 | +1.8 | +1.6 | -2.1 |
| 0.82456 | +4.1 | +3.8 | +1.9 | +1.7 | -2.2 |

All entries are pp. The supplied forward hedge is **-0.21pp, applied once**. Management's approximately **+3.0pp is after hedge**; the comparable gross figure is approximately +3.2pp under that hedge assumption. B4's approximately +2.9pp Phi and +1.0pp Q4 are on its stated/after-hedge basis. Calling those gross would introduce a basis error.

The regional comparison table below allocates management's 3pp total by prior-year regional revenue solely to reconcile the arithmetic. Management publishes no regional FX guide: this allocation is **not** an estimate of its undisclosed assumptions. At the midpoint, regional deviations sum to **+0.669pp**.

`adr_passthrough_sensitivity.csv` replaces the destination unit translation with the supplied EMEA/LatAm/APAC pass-through slope and retains only the incremental guest-origin-minus-destination shift. NA's unidentified slope is set to 1. These slopes were fitted on short samples against judgement baskets; they are not independently measured exposure. No second complete FX factor is added. Their results below show why one precise regional FX figure would overstate identification.

Retrospective free-lag fits use gross letter FX scored as **+/-0.5 intervals**, three nonnegative lag coefficients plus dispersion: **four parameters, W1 n=14, W2 n=10**. Current weights on past outcomes are explicitly **not a PIT backtest**. Profile confidence bounds assume Gaussian errors; serial dependence, proxy error and quarterly-GBV uncertainty are excluded.

At midpoint fee mix, comparable USD-inclusive scale is **0.879 [0.65,1.15] W1 / 0.731 [0.50,1.00] W2**, against B4's approximately 0.95. W1 still excludes 0.56. Dividing the driver by its assumed non-USD share yields **0.535 [0.40,0.70] / 0.447 [0.325,0.60]**; that apparent gap closure is partly a **denominator change**, not proof of measured weights. A slope on a USD-inclusive basket is not directly comparable with a non-USD revenue fraction. Full sensitivity and profile-grid tables are provided.

At 12 September, Q4 driver shares determined by the supplied 4-September FX history are **0.35 free / 0.82 Phi / 0.00 contemporaneous**. The future 5-November calendar ceiling gives **0.67 / 1.00 / 0.38**; a weekly publication-lag assumption gives **0.65 / 1.00 / 0.33**. Future availability arithmetic is not observed FX today or a statement that volume is already known. See `observed_share_triple.csv`.

### Q4 step and separate demand scenario

At midpoint fee mix the unit-translation FX step is **-2.09pp**. Paired with B4's explicit Q3 GBV cases, ex-FX step is **-0.01pp at $26,185M**, **+0.32pp at $26,300M**, and **+1.04pp at $26,550M**. Guest-fee endpoint assumptions can flip the near-zero case. The fading-tailwind direction remains; an unconditional '+0.4pp ex-FX acceleration' does not follow. **B4 is not superseded**.

The demand scenario imposes the supplied **0.11** elasticity on a lag-two purchasing-power **level**, then centers the regional differentials using scenario-quarter nights shares. It is not a fit or Krish's exact change-from-Q2 specification. Applied to regional nights, total nights delta is zero by construction. With within-region ADR fixed, geographic mix changes GBV by **$41.0M / $33.4M**, about **+0.15pp / +0.14pp** Q3/Q4, versus several points of translation. This is reallocation, not extra total demand or same-quarter revenue alpha. No demand overlay is added to revenue.

### K0/R interfaces, dates, abstentions and limits

Only verified `kernel_engine_v2` is imported. `regional_gbv_k0.csv` carries booking-dated USD and `regional_lambdas_k0.csv` coefficients in percent. **`k0_handoff_check.json` is an integration check at as_of=2026-09-13 using reconstruction data stamped 2026-09-12. It is not a September-12 or historical pre-guide forecast.** It reproduces the same regional dollar sum. Same-day/future inputs are refused in the module validation tests.

`Rscript` is absent. Python `engine_order()` implements G0, ADR factor, revenue factor, then hedge once. Its numerical example is independently unit-tested. `r_engine_handoff.csv` provides the requested geography/nights/ADR/currency/take-rate/reference columns and a real-quarter roundtrip. Since those input levels already embed FX, incremental ADR and revenue scales are zero. The roundtrip verifies units and interface arithmetic, not independent economic validation.

The requested registry objects are **not registered**; `registration_abstentions.csv` explains why. Reconstruction date 2026-09-12 lies outside frozen FORMAT 1.0's allowed current date 2026-09-11, and prior guide dates have no admissible O-D reconstruction. No false date, empty valid-looking forecast or PIT/full-sample row is fabricated. Harness change request: admit the actual current research date for LIVE scenarios while preserving historical score eligibility. No consensus value is consumed and no ratio against a missing baseline is claimed.

The quarterly kernel has **16 coefficients**, 3–4 seasonal observations each. Annual ratios are measured inputs. Currency weights and proxy allocations are borrowed assumptions; fee mix is one scenario axis; each gross-scale fit has four parameters. Rounding bands cannot cover the larger identification error. Outstanding: archived annual filing timestamps; historical regional GBV uncertainty; Airbnb O-D and settlement-currency weights; unknown-currency coverage; dated fee-migration mix. Token usage is unavailable from the subagent runtime and is not estimated.

## Recomputed evidence tables

Annual measured revenue/GBV (%):

| year | na | emea | latam | apac |
| --- | --- | --- | --- | --- |
| 2020 | 13.460 | 15.372 | 14.229 | 14.357 |
| 2021 | 12.650 | 13.218 | 11.635 | 13.156 |
| 2022 | 13.056 | 13.609 | 13.291 | 13.399 |
| 2023 | 13.274 | 13.776 | 13.611 | 13.963 |
| 2024 | 13.238 | 13.899 | 13.663 | 13.921 |
| 2025 | 12.895 | 13.843 | 13.580 | 13.971 |

Quarterly annual-anchored seasonal coefficients (%); brackets are sensitivity envelopes, not confidence intervals:

| region | Q1 | Q2 | Q3 | Q4 |
| --- | --- | --- | --- | --- |
| na | 12.17 [11.07, 13.90] | 13.88 [12.61, 15.86] | 15.54 [14.16, 17.89] | 11.18 [10.20, 12.87] |
| emea | 9.70 [8.73, 10.89] | 14.30 [12.88, 16.04] | 21.17 [18.99, 23.83] | 10.90 [9.76, 12.30] |
| latam | 21.40 [19.41, 23.93] | 11.12 [10.07, 12.45] | 10.89 [9.89, 12.17] | 15.95 [14.49, 17.84] |
| apac | 17.84 [16.14, 19.88] | 12.09 [10.93, 13.48] | 13.49 [12.21, 15.01] | 15.86 [14.35, 17.65] |

Selected midpoint currency weights; all are scenario weights and measured Airbnb weights remain null:

| region | currency | judgement_destination_weight | scenario_revenue_weight |
| --- | --- | --- | --- |
| na | USD | 0.900 | 0.745 |
| emea | USD | 0.050 | 0.107 |
| emea | EUR | 0.700 | 0.606 |
| emea | GBP | 0.250 | 0.216 |
| latam | USD | 0.070 | 0.122 |
| latam | BRL | 0.550 | 0.446 |
| latam | MXN | 0.380 | 0.310 |
| apac | USD | 0.080 | 0.091 |
| apac | AUD | 0.550 | 0.498 |
| apac | JPY | 0.200 | 0.180 |

Comparable USD-inclusive gross scale fits (95% profile grid):

| guest_fee_share | window | n | scale | scale_ci_lo | scale_ci_hi |
| --- | --- | --- | --- | --- | --- |
| 0.000 | W1 | 14 | 0.931 | 0.700 | 1.200 |
| 0.000 | W2 | 10 | 0.781 | 0.560 | 1.050 |
| 0.500 | W1 | 14 | 0.879 | 0.650 | 1.150 |
| 0.500 | W2 | 10 | 0.731 | 0.500 | 1.000 |
| 0.825 | W1 | 14 | 0.840 | 0.625 | 1.125 |
| 0.825 | W2 | 10 | 0.694 | 0.475 | 0.950 |

Q3 midpoint regional allocation (pp; comparator allocation is arithmetic only):

| region | gross_fx_contribution_pp | after_hedge_fx_contribution_pp | difference_from_allocated_management_pp |
| --- | --- | --- | --- |
| na | 0.595 | 0.513 | -0.673 |
| emea | 2.370 | 2.269 | 0.827 |
| latam | 0.674 | 0.661 | 0.489 |
| apac | 0.240 | 0.225 | 0.026 |

Regional ADR pass-through sensitivity (pp):

| guest_fee_share | quarter | gross_fx_contribution_pp | after_hedge_fx_contribution_pp |
| --- | --- | --- | --- |
| 0.000 | 2026Q3 | 3.376 | 3.166 |
| 0.000 | 2026Q4 | 1.188 | 0.978 |
| 0.500 | 2026Q3 | 3.655 | 3.445 |
| 0.500 | 2026Q4 | 1.295 | 1.085 |
| 0.825 | 2026Q3 | 3.828 | 3.618 |
| 0.825 | 2026Q4 | 1.358 | 1.148 |

## One proposed memo sentence

> The regional FX reconstruction does not yet justify replacing B4: no measured Airbnb origin–destination currency matrix is identified, and the current reconstruction has 0/14 W1 and 0/10 W2 point-in-time guide observations.

This is an evidence-limit sentence. Numerical FX tables remain scenarios, not proposed memo-ready alpha. Parent owns refuter verdicts.

## RESUME

Inspect dated provenance and null measured weights before using the scenario exposure file. A future version needs archived public input vintages and an auditable mapping from destination-specific tourism proxies to Airbnb nights and settlement currency. Preserve the same-cell identity versus forecast distinction. Parent owns scorer, workboard, commits, pushes and PR. Use new version names for subsequent analytical revisions.
