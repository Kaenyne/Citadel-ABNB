# L3 cohort FX v2 — additional period coverage gate

2026-09-13, before this repair's tests. Independent reviewer nclh retained the complete annual reference but reduced a completed booking quarter to one quote per currency; the time-average constructor accepted that sparse quarter. Initial v2 root output (if complete) is preserved as a pre-period-coverage checkpoint; final canonical output will be cohort_fx_v2/results_v2, with a separate rebuild.

For each required currency/period, define the observed slice from period start through the earlier of period end and that currency's actual last cache quote. Require at least 80% of that slice's weekdays to have valid observations, both boundaries within seven calendar days, and no gap over ten calendar days. Observations must remain finite/positive and unique. A completely future slice has no observed requirement and retains its explicit flat-spot hypothesis. These gates check minimum daily-data adequacy, not actual transaction weighting, and do not certify an unmeasured cohort.

The reviewer attack and missing-first-month/internal-month-gap variants must fail; current frozen inputs must pass without changing any rate value, kernel dollar output or YoY arithmetic. The new fields may report expected weekday coverage separately. Research PARTIAL and all original adoption limits remain unchanged.

## RESUME

Add this data-integrity check and regression tests to v2, preserve the earlier checkpoint, rebuild final results into new directories, and obtain independent review closure. Include this protocol in the final input manifest.
