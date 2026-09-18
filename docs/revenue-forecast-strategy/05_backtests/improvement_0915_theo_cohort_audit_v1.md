# improvement_0915_theo — booking-cohort evidence and charts

15 September 2026. Parent with independent historical-source and alternative-data subagents. Branch: `codex/submission-readiness-v1`. Additive follow-up to `improvement_0915_theo.md`; existing protected files were not edited.

## Verdict

**Partial against the preregistered descriptive acceptance condition.** The inspected local data do not provide current, consolidated Airbnb fee revenue attributable to bookings made in the same quarter, one quarter earlier, and two quarters earlier. We can calculate the historical aggregate conversion ratio and plot the older K2 study's reconstructed Melbourne accommodation-value shares. These are separate objects. Neither identifies actual current corporate booking-cohort revenue. Improvement 1 remains identified / to scope; the live model is unchanged.

## What ran

Read-only audits covered K1/K2 notes, code and saved outputs; the local alternative-data catalog and manifests; and official public source documentation. No purchases, external outreach, raw-data downloads or Airbnb scraping occurred. Raw Melbourne reservation files were not found by the subagent's filename search across Desktop, including worktrees; expected local Theo Data and capture-store paths were absent. This is a statement of local availability, not nonexistence elsewhere.

Reproduction command, run from this worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_cohorts_0915_v1/run.py
```

Exit 0, approximately 2.6 seconds. Python was not on PATH and the bundled interpreter lacked matplotlib; the existing repository virtual environment supplied matplotlib and pandas. A non-fatal pandas fragmentation warning occurred when adding the quarter key. No numerical failures. Output directory: `outputs/gbv-cohorts-20260915-v1/`. The script refuses to overwrite an existing output directory; use `--out` with a new path for a repeat run.

Checks: all 14 aggregate ratios reconcile to frozen KPI revenue and lagged GBV; 10 rows lie in W2; four proxy groups each sum to 100% including the 3+ tail; source reservation counts total 268,110; hashes of all three input files were unchanged. Both PNGs were visually inspected. CSVs, SVGs and a source/output SHA-256 manifest accompany the figures. No forecast registration or scorer run was required. Parameter count added: zero; no estimation model was fitted.

## Figure 1 — observable aggregate conversion variation

`01_aggregate_conversion.png` plots:

`lambda_t = revenue_t / [(2/3) GBV_(t-1) + (1/3) GBV_(t-2)]`

This is an ex-post ratio calculated from the frozen financial panel, not a reservation completion probability or a forecast error. Seasonal differences should be separated from variation within the same season.

| Window | Season | n | Mean ratio (%) | Sample SD (percentage points) | Sample variance (pp squared) | Range (pp) |
|---|---|---:|---:|---:|---:|---:|
| W1, 2023Q1–2026Q2 | Q1 | 4 | 12.693760 | 0.300137 | 0.090083 | 0.708985 |
| W1 | Q2 | 4 | 13.713589 | 0.203968 | 0.041603 | 0.497333 |
| W1 | Q3 | 3 | 17.239362 | 0.132389 | 0.017527 | 0.245303 |
| W1 | Q4 | 3 | 12.029793 | 0.085626 | 0.007332 | 0.171124 |
| W2, 2024Q1–2026Q2 | Q1 | 3 | 12.657408 | 0.356644 | 0.127195 | 0.708985 |
| W2 | Q2 | 3 | 13.710200 | 0.249671 | 0.062336 | 0.497333 |
| W2 | Q3 | 2 | 17.163650 | 0.025693 | 0.000660 | 0.036336 |
| W2 | Q4 | 2 | 12.071619 | 0.064552 | 0.004167 | 0.091290 |

All rows are retrospective and descriptive, using sample variance with denominator n−1. The small n does not establish a stable future distribution. The current EWM estimate is a different statistic from these simple sample means. Input GBV precision is inherited from the frozen panel; this exercise does not upgrade its provenance or precision.

## Figure 2 — available historical booking-cohort proxy

`02_melbourne_cohort_proxy.png` uses `kernel_leadtime_v2/K2_recommended_prior.csv`, `weighting=value`. Rows are relabelled using the original Melbourne month groups instead of the source's northern-hemisphere seasonal analogy.

| Melbourne check-in months | Reservations | Same-quarter (%) | One earlier (%) | Two earlier (%) | Three or more earlier (%) |
|---|---:|---:|---:|---:|---:|
| Jan–Mar, pooled across years | 78,040 | 46.34 | 38.94 | 9.55 | 5.18 |
| Apr–Jun 2016 | 45,508 | 50.17 | 35.28 | 11.74 | 2.80 |
| Jul–Sep 2016 | 59,500 | 55.84 | 31.45 | 10.00 | 2.71 |
| Oct–Dec 2016 | 85,062 | 49.81 | 36.06 | 8.21 | 5.92 |

Window: March 2016–February 2017. Jan–Mar combines March 2016 with January–February 2017. Rounded cells need not sum exactly to 100%. The source is Harvard Dataverse `doi:10.7910/DVN/1XPDEU`, documented in `data/manifests/dataverse_log.csv`; only processed K2 outputs are locally available. No fresh raw reconstruction was performed.

The plotted object is **reconstructed accommodation-value share**, not observed Airbnb fee-revenue share. K2 uses nightly price capped at the 99.5th percentile, multiplied by nights, with observation-probability weighting and lead-time reconstruction. Currency and price units were not independently verified. Central shares average no-tail and imported-tail assumptions. The earlier analytic CSV is a different specification and was not mixed into this chart.

The original truncation diagnostic did not recover the reference mean: 52.31 days versus 40.61–43.64 days after adjustment in the simulated truncated cases. Consequently these estimates are exploratory. Source bounds are sensitivity/identification bounds, not confidence intervals. One city and one seasonal cycle cannot measure current global shares, historical year-to-year cohort variance, or RNPL effects.

## Corrections to stronger language in earlier K1/K2 notes

K1's fitted phi values are normalized regression coefficients, not directly measured revenue shares. Even a fitted attribution would be `phi_k × GBV_(t-k) / sum_j(phi_j × GBV_(t-j))`, not phi alone. K1's own ex-COVID bootstrap intervals for the one-quarter and two-quarter coefficients span approximately 0–0.724 and 0–0.640; the split is poorly identified.

K2 asks the reverse question: of accommodation value associated with these check-ins, when was it booked? Those shares cannot simply replace the coefficients applied to each earlier quarter's total reported GBV. The literal conversion equation suggested by `K2_M_matrix.csv` should not be adopted without a compatible booking-cohort denominator and fee/recognition bridge. Multiplying old Melbourne shares by current corporate revenue would create an assumed allocation, not historical evidence.

## The data object we actually need

Build a matrix with **booking quarter as the row, revenue-recognition quarter as the column, and recognized fee dollars as the cell**. Then read a target-quarter column to obtain the requested stacked chart. Include a 3+ earlier bucket and keep unallocated adjustments visible.

Two questions must remain separate:

- Revenue composition: how much of this quarter's revenue came from each booking quarter? Denominator: this quarter's total revenue.
- Forward conversion: how much of a particular booking quarter's value later becomes recognized revenue in each future quarter? Denominator: that booking cohort's consistently defined original value.

Airbnb's reported GBV includes host earnings, service fees, cleaning fees and taxes and is net of cancellations/alterations occurring in the reporting period, including cancellations of older bookings. It is not a clean original-booking-cohort denominator. A proposed matrix must reconcile these cancellation flows rather than subtract a second generic haircut. For ordinary stays, fees are recognized at check-in; long-term stays have monthly recognition, including subsequent monthly anniversaries. Accommodation receipts are not corporate fees. These definitions come from the [2025 10-K, KPI definitions and revenue recognition](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm), accessed 15 September 2026.

### Minimum sample specification

| Field group | Required content | Why |
|---|---|---|
| Stable identifiers | Reservation, listing, provider and booking channel | Deduplicate and isolate Airbnb reservations |
| Timing | Original booking timestamp, check-in/out, modification and cancellation timestamps | Attribute cohorts and handle changes |
| Historical information | Capture timestamp and status/value known at each past observation date | Prevent final outcomes leaking into guide-date forecasts |
| Dollars | Accommodation amount, currency, taxes, cleaning fees, refunds and host/guest platform fees separately where available | Distinguish rental value, GBV and Airbnb revenue |
| Population | Destination, property type, professional/individual host characteristics where available | Measure coverage and sampling bias |
| RNPL | Payment-option flag and its effective date, if actually observable | Separate RNPL-specific claims from general lead-time changes |

First inspect a small sample or aggregated booking-month × check-in-month extract. Desired eventual coverage is multiple regions and years before and after RNPL, with sufficient prehistory to capture long-lead reservations. A full 2023+ validation requires earlier booking cohorts and training data. A professional-manager panel is not automatically representative of Airbnb globally. Where actual fees are absent, name the output **completed accommodation value by booking cohort**, and keep the later corporate revenue mapping explicitly estimated. Missing RNPL flags mean timing changes alone cannot identify RNPL causality.

## Alternative-data routes, checked 15 September 2026

| Route | What is supported | What remains to verify |
|---|---|---|
| Direct PMS sample, including KeyData | Booking dates, arrival-based value, pacing/curves; a promising candidate for the matrix | Airbnb-only filter, actual creation/change timestamps, complete cancellation history, sample selection, fee fields and export access |
| AirDNA | Broad lead-time and accommodation-performance estimates | Direct observations versus inference; channel mixing; historical cohort access; actual fees |
| Repeated Inside Airbnb snapshots already held | Intervals in which availability changed for the same listing/stay date | Blocks versus reservations, cancellations, capture frequency and missed same-quarter stays |
| Existing K2 Melbourne study | Dated illustration and a method to inspect | Old city sample, raw availability, truncation and value definitions; not current calibration |
| Airbnb forecasting research papers | Relevant booking-to-check-in methodology using internal data | No verified downloadable current corporate cohort ledger |

KeyData's [Revenue Booked documentation](https://help.keydatadashboard.com/report/shared-revenue-booked-table-pm) explicitly connects a selected booking-date range to arrival months. Its [enterprise documentation](https://www.keydata.co/products/enterprisedata) describes direct PMS records and data delivery. The [cancellation coverage note](https://support.keydatadashboard.com/en/knowledge/how-to-use-bookings-by-date-to-track-the-upcoming-decrease-in-cancellations) says not every PMS supplies cancelled reservations. This is a candidate to evaluate, not a purchase recommendation or confirmation that the exact feed is accessible.

AirDNA's [occupancy methodology](https://help.airdna.co/en/articles/8062178-how-does-airdna-calculate-occupancy-rate) describes inferred calendar classifications and combined-channel treatment of matched properties. Its [performance dashboard](https://help.airdna.co/en/articles/10011518-performance-dashboard) includes lead time; that alone does not establish a downloadable booking-cohort ledger. [Lighthouse's data guide](https://www.mylighthouse.com/resources/insights/introductory-guide-hospitality-data-as-a-service) is an additional candidate; required field access remains unverified.

The [2026 Airbnb forecasting paper](https://arxiv.org/html/2601.12175v2) analyzes internal North American booking-to-check-in distributions for nights and GBV during 2019–2025. Its use of the term revenue for GBV must not be confused with corporate fee revenue. The [earlier study](https://arxiv.org/html/2501.10535v3) states that its data are confidential. Neither supplies a verified downloadable solution here.

With Inside Airbnb snapshots, infer only a booking-time interval between consecutive captures, not an exact date. If that interval spans a quarter boundary, preserve ambiguity. A stay booked and completed entirely between monthly snapshots can be invisible, biasing the very same-quarter share being investigated. Reviews provide a stay-related signal but do not recover the original booking date. These sources can corroborate a directly observed panel; they cannot manufacture missing reservation events.

## Next decision and validation design

Agree on the target matrix and audit a small direct-PMS sample before expanding acquisition or changing model weights. If a usable sample exists, produce value levels and shares with the 3+ tail, then examine changes within each season across years and markets. Report reservation, listing, market and quarter counts; do not confuse a large reservation count with many independent quarterly observations. Uncertainty should reflect property/market clustering, coverage, missing cancellations and fee assumptions. Keep retrospective realized-cohort charts separate from guide-date snapshots. Pre-register the forecast comparison against the existing lagged-GBV benchmark before fitting any replacement, and apply the repository's W1/W2 requirements.

## Harness change requests

None. No forecasts were registered, no model was promoted and no current guide or stock-price estimate changed.

## RESUME

Continue the discussion from Improvement 1. The desired current corporate revenue-by-booking-quarter graph remains unavailable; the delivered aggregate-conversion and old accommodation-value proxy figures define what is and is not measured. The next useful step is a small, explicitly scoped direct-PMS sample or equivalent aggregated cohort extract with booking date, check-in date, channel, value, cancellation and historical-vintage fields. No acquisition, outreach or model replacement has been executed. Preserve the distinction between backward revenue shares and forward booking conversion rates, the 3+ tail, long-term recognition, and the double-counting safeguard.
