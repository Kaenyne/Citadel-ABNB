# ABNB Historical ADR Pilot 1 — concise memo

## Decision

**INCONCLUSIVE / NOT TESTABLE.** No lawful vintage-specific lodging CPI payload passed the deterministic collection gate, so the two preregistered features contain zero observations and zero guidance events are strictly eligible. No Pearson, Spearman, direction, or acceleration statistic was computed. This is not a negative signal result; it is a source-readiness failure.

## Frozen design

H-003 version 2 was appended at `2026-09-04T01:25:19Z` before signal/outcome comparison. The primary is NSA lodging CPI trailing-three-month mean YoY growth. The sole control subtracts the identically calculated NSA all-items CPI trailing-three-month mean YoY growth. The target snapshot retains 23 guidance events, including 16 with numeric prior-year-comparable midpoint growth. No transformation, threshold, lag, window, or weight was searched.

## Permission and vintage outcome

- The free FRED API route is governed by official terms but requires `FRED_API_KEY`; no synced key or local `.env` was present. The exact API-host robots path was not established, so the gate remained false even apart from authentication.
- FRED Services terms prohibit automated data mining, scraping, or extraction outside the expressly allowed API. Therefore the otherwise robots-allowed ALFRED graph CSV route was not requested.
- The exact requested series ID `CUUR0000SEHB02` returned HTTP 404 on the official FRED and ALFRED series pages. The all-items control `CPIAUCNS` exists, but it is unusable without the primary.
- BLS's official robots request had already returned terminal HTTP 403 in same-day governed reconnaissance. No retry, archive-page request, or BLS payload occurred. Its current no-key API was not substituted for historical vintages.

There were **9 permission-page/provider GETs**, **6 registered candidate data requests**, and **0 data-payload GETs**. The exact `api.bls.gov` robots file states `User-agent: *` and `Disallow: /`, so the no-key BLS API path is affirmatively disallowed for this automated run despite the public API documentation and final-on-release CPI policy. All cached responses are checksummed. No personal data, paid source, credential value, authenticated request, restricted transcript, regression, or model was used.

## Usability

Data-source usability is **1.7/5** on the six prespecified dimensions: free aggregate data and privacy are favorable, but exact-series availability, credential sync, path permission, vintage access, and event-specific publication evidence failed. Forecast-signal usability remains **2.0/5 ex ante**: the ADR mechanism is coherent, but the proxy is lagged, U.S.-only, hotel-heavy, and currently untestable. These scores describe usability, not predictive performance.

## What would resolve the blocker

Either (1) a synced free FRED key plus official confirmation that a supported ALFRED series exactly matches NSA BLS lodging CPI and exact API-path robots permission, or (2) written BLS automation permission or user-supplied lawful original CPI release artifacts with publication timestamps. Until then, H-003 v2 must not enter an ABNB forecast.

Predictive alpha has not been tested, and this pilot is not promoted to forecasting.
