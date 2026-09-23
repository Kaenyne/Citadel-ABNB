# RNPL calendar pilot: Austin, Rome, Sydney

Completed September 10, 2026. Local-data pilot only; no forecast adjustment or causal RNPL estimate.

## Decision

The calendar files support reproducible reopening and reclosure diagnostics for retained listing/stay-date keys. They do not identify canceled reservations, RNPL use, or platform net lost nights. Use this pilot to assess the proxy and prioritize reservation-event data, not to apply a Q3/Q4 cancellation haircut.

The empirical finding is mixed rather than a common deterioration across markets. Rome's short-run reopening rises in the final interval, while Austin is roughly flat and Sydney declines. Rome's increase also appears in each of the first three fixed days-to-arrival bands, so it is not solely the change in the broad horizon mix. However, interval duration, calendar season, initial booking age, and traveler/policy mix remain uncontrolled. Treat Rome as a hypothesis for independent verification, not an identified RNPL effect.

Broad reopening levels fall materially under the short-run screen in every market, and a substantial fraction of observed reopenings later become unavailable again. These results show why the raw calendar proxy cannot be mapped directly to permanent lost nights. Neither the stricter screen nor reclosure establishes true booking status.

## Sample and provenance

Austin, Rome, and Sydney were selected before inspecting outcomes: all have five vintages, with Europe and Asia-Pacific represented alongside the US. The code applies a fixed SplitMix64 hash to listing IDs and retains one hash bucket out of ten. The same ID is selected in every vintage. This is a deterministic approximately 10% listing sample, not a demonstrated population-representative sample. Results are night-weighted within it; no listing-night independence or statistical significance is assumed.

All 15 source files fully parsed; sampled keys were checked for duplicates and sampled availability values validated. File URLs and byte sizes match the existing `data/processed/adr/14c_calendar_manifest.csv`. Fresh SHA-256 hashes are saved in the per-market JSONs; they fingerprint the files used, not an independently archived server hash. Source: Inside Airbnb, CC BY 4.0. The acquisition code streamed downloads without synthesizing rows.

| Market | Raw rows read across vintages | Sampled listing-nights across vintages | Sample listings per vintage | Listings in all five |
|---|---:|---:|---|---:|
| austin | 19,109,267 | 1,944,726 | 1073 / 1133 / 840 / 1155 / 1127 | 540 |
| rome | 65,552,051 | 6,499,269 | 3755 / 3696 / 2977 / 3689 / 3689 | 2,463 |
| sydney | 33,970,197 | 3,334,640 | 1766 / 1969 / 1347 / 2013 / 2041 | 868 |

These are repeated listing-night observations, not distinct reservations or distinct stayed nights.

## Matching and attrition

Join exact listing ID and stay date. Retain only stay dates strictly after the later snapshot; elapsed dates are never treated as conversions. Reopening = unavailable at first capture, available at second. The denominator is initially unavailable nights that remain observable in both captures. Missing listings are not treated as cancellations, bookings, or survival.

| Market | Observation interval | Days apart | Future rows retained | Initially unavailable rows retained |
|---|---|---:|---:|---:|
| austin | 2025-09-16 → 2025-12-22 | 97 | 86.6% | 82.5% |
| austin | 2025-12-22 → 2026-03-25 | 93 | 64.7% | 56.9% |
| austin | 2026-03-25 → 2026-06-22 | 89 | 91.0% | 88.7% |
| austin | 2026-06-22 → 2026-08-25 | 64 | 91.2% | 89.5% |
| rome | 2025-09-14 → 2025-12-16 | 93 | 89.0% | 87.0% |
| rome | 2025-12-16 → 2026-03-24 | 98 | 74.7% | 63.0% |
| rome | 2026-03-24 → 2026-06-20 | 88 | 94.7% | 93.7% |
| rome | 2026-06-20 → 2026-08-25 | 66 | 96.1% | 95.4% |
| sydney | 2025-09-12 → 2025-12-12 | 91 | 88.4% | 85.3% |
| sydney | 2025-12-12 → 2026-03-21 | 99 | 57.8% | 51.2% |
| sydney | 2026-03-21 → 2026-06-16 | 87 | 91.9% | 90.0% |
| sydney | 2026-06-16 → 2026-08-15 | 60 | 91.6% | 89.0% |

Retention refers to baseline dates still in the future at capture 2. Stable-all-five screens additionally condition on surviving future snapshots; they are descriptive sensitivity checks with look-ahead, not point-in-time backtests.

## Reopening: broad versus screened

Four regimes are saved. **Broad** is all matched keys. **Stable** requires the listing in all five vintages. **Screened** also requires less than 95% unavailable in each full calendar, unchanged minimum nights, and a minimum of at most seven nights. **Short-run** further requires an interior initial unavailable run of 1–14 consecutive days (runs touching a calendar boundary are excluded). These thresholds were selected before outcomes; they do not establish which dates are real bookings. Short-run selection intentionally changes the cohort and may select more transient states.

| Market | Interval ending | Broad rate | Stable rate | Screened rate | Short-run rate | Short-run reopened / initially unavailable |
|---|---|---:|---:|---:|---:|---:|
| austin | 2025-12-22 | 40.3% | 47.0% | 47.9% | 20.6% | 283 / 1,373 |
| austin | 2026-03-25 | 39.9% | 42.1% | 43.1% | 8.2% | 146 / 1,786 |
| austin | 2026-06-22 | 34.4% | 37.8% | 40.0% | 10.2% | 224 / 2,205 |
| austin | 2026-08-25 | 23.6% | 29.1% | 32.5% | 10.0% | 395 / 3,969 |
| rome | 2025-12-16 | 36.8% | 46.9% | 47.4% | 11.6% | 1,949 / 16,802 |
| rome | 2026-03-24 | 36.5% | 37.4% | 35.6% | 7.8% | 2,599 / 33,347 |
| rome | 2026-06-20 | 30.3% | 31.0% | 29.5% | 9.0% | 3,397 / 37,724 |
| rome | 2026-08-25 | 27.9% | 31.3% | 30.6% | 13.3% | 5,225 / 39,237 |
| sydney | 2025-12-12 | 24.7% | 29.7% | 31.8% | 7.2% | 513 / 7,152 |
| sydney | 2026-03-21 | 36.0% | 35.7% | 38.6% | 11.9% | 444 / 3,739 |
| sydney | 2026-06-16 | 28.5% | 30.3% | 32.9% | 9.4% | 637 / 6,788 |
| sydney | 2026-08-15 | 17.9% | 22.0% | 23.6% | 7.7% | 881 / 11,475 |

### Fixed-horizon cross-check: short-run reopening

| Market | Days after second snapshot | March→June rate | June→August rate |
|---|---|---:|---:|
| austin | d001_030 | 10.0% | 11.4% |
| austin | d031_060 | 20.2% | 8.6% |
| austin | d061_090 | 9.5% | 6.9% |
| rome | d001_030 | 7.9% | 11.9% |
| rome | d031_060 | 9.4% | 11.0% |
| rome | d061_090 | 9.6% | 15.2% |
| sydney | d001_030 | 8.7% | 8.4% |
| sydney | d031_060 | 14.2% | 9.2% |
| sydney | d061_090 | 8.5% | 6.6% |

Different intervals are 60–100 days apart and cover different seasons/horizons. Their raw percentages cannot establish acceleration or deceleration in cancellation risk. Fixed 1–30, 31–60, 61–90, and 91–180 day-to-arrival slices are also in the JSONs; they still have different interval lengths and seasonal stay dates. No annualization or causal before/after estimate is made.

The short-run regime also filters initially available spells in the underlying transition table. Its newly-unavailable and net-unavailable-change fields are not a full inventory-flow estimate and are not used here to infer demand or cancellation offsets. All regimes are selected subpopulations; the strictest one is not proven to be the most accurate.

## Latest June-to-August interval: dates still ahead

Q3 below covers only the remainder of Q3 after each market's August snapshot, not all Q3 stays and not cancellations recorded throughout Q3. Q4 covers the matched October–December stay dates. These are stay-date windows; reported Nights and Seats Booked uses booking/cancellation transaction dates.

| Market | Stay-date window | Broad reopening | Short-run reopening | Short-run reopened / initial unavailable | Top 10 listings' share of short-run reopenings |
|---|---|---:|---:|---:|---:|
| austin | Q3_2026 | 19.2% | 11.6% | 123 / 1,060 | 52.8% |
| austin | Q4_2026 | 23.0% | 8.5% | 223 / 2,609 | 41.3% |
| rome | Q3_2026 | 13.5% | 12.0% | 1,931 / 16,134 | 12.5% |
| rome | Q4_2026 | 24.5% | 12.8% | 2,172 / 16,995 | 13.2% |
| sydney | Q3_2026 | 16.4% | 9.6% | 326 / 3,398 | 27.0% |
| sydney | Q4_2026 | 21.2% | 7.4% | 411 / 5,565 | 29.2% |

## Reopened then unavailable again

The latest triple is March → June → August. Restrict to identical stay dates after the August capture, observable in all three. Among dates unavailable in March and available in June, count those unavailable again in August. Reclosure can represent a booking, a host block, or other calendar changes. It is not confirmed replacement booking and cannot be used as the rebooking offset in the RNPL materiality table.

| Market | Regime | Reopened nights followed | Reclosed by August | Reclosed share |
|---|---|---:|---:|---:|
| austin | all_matched | 18,599 | 3,400 | 18.3% |
| austin | screened_short_run | 130 | 50 | 38.5% |
| rome | all_matched | 69,998 | 11,806 | 16.9% |
| rome | screened_short_run | 1,646 | 721 | 43.8% |
| sydney | all_matched | 35,242 | 8,017 | 22.7% |
| sydney | screened_short_run | 402 | 127 | 31.6% |

The denominator excludes reopened dates that elapsed before August or lost listing/date coverage. The JSON records pre-third-join reopened counts for the broad all-future cohort. There is no September/December observation after the final August capture, so June→August reopenings cannot yet be followed to a later reclosure or completed stay.

## What this changes for the forecast

Do not multiply these reopening rates by Airbnb nights or RNPL GBV share. The missing links are booking-versus-block classification, RNPL eligibility/use, guest origin, exact cancellation timestamps, treatment/control assignment, representative platform weights, and the cancellation risk already in the forecast. The directory starts after US RNPL launch and has no 2024 baseline. International snapshots cross global rollout, but also seasons and other policy changes; those comparisons are not a natural experiment without additional fields.

The pilot establishes technical feasibility for matched calendar diagnostics and measures how much those diagnostics change under screening. It does not establish excess RNPL cancellations or rule them out. Keep the RNPL cancellation adjustment uncalibrated; prioritize a small reservation-event sample with booking/cancellation dates and RNPL or eligibility fields before expanding this analysis to all 34 markets.

## Reproduction and checks

Run `.venv/Scripts/python.exe analysis/src/rnpl_calendar_pilot.py`, then `.venv/Scripts/python.exe analysis/src/rnpl_calendar_pilot_report.py`. `--market austin` runs one market; `--self-test` runs a synthetic check covering elapsed/unmatched exclusion and known transition counts. The main run checks sampled key uniqueness, availability states, one-to-one joins and transition-count identities. Source manifest URL/size reconciliation checks run during report generation.

Artifacts: [Austin](austin.json), [Rome](rome.json), [Sydney](sydney.json). Each holds provenance, raw/sample coverage, every horizon/regime pair, and three-capture reclosure results. No raw guest or reservation information was acquired; no existing forecast was changed.
