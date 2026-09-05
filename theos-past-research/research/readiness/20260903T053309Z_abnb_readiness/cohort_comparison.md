# Phase-A cohort comparison

Run ID: `20260903T053309Z_abnb_readiness`  
Owner: `abnb_alt_data`

Agent hierarchy:

1. **ABNB Research Orchestrator** — orchestration and final readiness verdict.
2. **abnb_alt_data** — registries, preregistration, collection, reconciliation, and comparison-validity decision.
3. **guidance_2020q4_2023q2** — independent early-cohort replay.
4. **guidance_2023q3_2026q2** — independent late-cohort replay.

## Comparison-validity decision

Strict H-001 results are descriptively comparable. Both cohorts use the same next-quarter revenue-guidance midpoint, USD millions, reported-currency basis, dated Board H.10 archives, fixed 28-calendar-day first-to-last transformation, negative expected direction, strict-before-cutoff rule, and seasonal-naive same-guided-quarter-prior-year baseline. The 16 comparable event rows meet H-001's numeric-target minimum, and the prospective sample can support at least eight later walk-forward test folds. Phase A did not construct or fit folds, so this is a fixed-rule descriptive replay—not evidence of modeled incremental value.

Strict H-002 cannot be compared or pooled: zero observations have verified initial publication timestamps in the API response. Its separate sensitivity calculation assumes availability at 16:00 UTC on the observation day, but the early cohort has only four comparable seasonal-baseline events and fails H-002's preregistered minimum of six per cohort. Sensitivity hit rates therefore remain separate.

H-003 cannot be compared or pooled: exact historical BLS release timestamps were not reconstructed, so all observations are strict-PIT ineligible.

## Separate cohort results

| Signal | Early cohort | Late cohort | Valid interpretation |
|---|---:|---:|---|
| H-001 strict H.10 | 3 hits, 1 miss; 7 not testable | 6 hits, 6 misses | Comparable descriptively; pooled 9/16, but no significance or forecast-edge claim |
| H-002 strict ECB | 0 eligible | 0 eligible | Not testable; do not compare |
| H-002 timing sensitivity | 3 hits, 1 miss | 7 hits, 5 misses | Separate only; early minimum fails and timing is inferred |
| H-003 BLS lodging CPI | 0 eligible | 0 eligible | Not testable; do not compare |

The apparent H-001 weakening from 75% early to 50% late is a regime-stability warning, not statistical evidence. The early denominator is four. No threshold, subgroup, or transformation was changed to rescue the result.

## Reconciliation notes

- Three early events contain qualitative guidance only; no numeric midpoint was invented.
- Four additional early numeric events lack a same-guided-quarter prior-year midpoint, leaving only four comparable early baseline events.
- The 2023Q4 transcript contains a material 70%/17% discrepancy; the official SEC shareholder-letter value controls and the discrepancy is retained in all late-cohort rows.
- Transcript text is target context only and was never used as a pre-call signal.

