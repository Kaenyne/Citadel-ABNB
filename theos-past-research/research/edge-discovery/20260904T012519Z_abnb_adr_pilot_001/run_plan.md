# ABNB Historical ADR Pilot 1

- Run ID: `20260904T012519Z_abnb_adr_pilot_001`
- Request ID: `ABNB-ADR-PILOT-001`
- Frozen at: `2026-09-04T01:25:19Z`
- Target: ABNB next-quarter revenue-guidance midpoint year-over-year growth.
- Evidence gap: nominal ADR/mix input.
- Proxy: BLS CPI other lodging away from home (`CUUR0000SEHB02`) through official FRED/ALFRED vintage evidence.
- Geography: United States city average.
- Expected sign: positive, subject to accommodation-demand destruction and mix effects.

## Locked transformations

1. Primary: year-over-year percentage change in the arithmetic mean of the latest three consecutive eligible monthly NSA lodging CPI observations.
2. Control: primary lodging measure minus the identically calculated trailing-three-month year-over-year percentage change in NSA all-items CPI.

No transformation, window, threshold, vintage, or weight search is permitted. The panel will retain all 23 existing guidance events and separately identify the 16 events with a numeric prior-year comparable midpoint. Descriptive comparisons are limited to fixed Pearson, Spearman, sign concordance, and sequential-acceleration concordance. No regression, model fitting, promotion, forecast-output change, or alpha claim is authorized.

## Point-in-time rule

Each observation and its vintage-specific availability evidence must be strictly earlier than `guidance_available_at_utc`. Equality and missing or ambiguous timestamps fail. Current snapshots cannot stand in for historical vintages.

## Collection order

1. Confirm whether the registered free FRED credential is synced without exposing its value.
2. Preserve official terms, robots, API documentation, series metadata, and vintage documentation in a request-level audit.
3. Run the deterministic `ScrapeCandidate` gate for every exact data path before requesting a payload.
4. If the FRED key is absent, inspect only lawful official no-key BLS/ALFRED download routes capable of preserving vintage evidence.
5. Stop with a complete not-testable panel if no lawful vintage route passes.

