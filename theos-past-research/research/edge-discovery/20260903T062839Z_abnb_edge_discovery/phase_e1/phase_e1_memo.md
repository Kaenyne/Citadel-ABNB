1. ABNB Edge-Data Research Orchestrator — main Codex task; owns orchestration, user communication, and the final decision.
2. abnb_alt_data — permanent gpt-5.6-sol research lead; owns source governance, permission decisions, canonical registries, point-in-time methodology, hypothesis reconciliation, and the final ranked slate.
3. physical_world_activity_edge — searches physical sensors, mobility, transportation, remote sensing, environmental, and infrastructure data.
4. supply_scarcity_web_edge — searches STR supply, regulatory, public-calendar, capacity-scarcity, pricing, and permitted web-exhaust data.

# Phase E1 source testability and fixed-rule replay memo

## Executive decision

All 15 E0 source IDs are recorded as user-approved for lawful collection and testability review. That approval did not override provider terms, robots rules, authentication, privacy, rate limits, or point-in-time evidence. The permission-resolution continuation completed 35 provider-facing permission GETs and cached every response. Final lead review left all 15 exact data paths blocked. One privacy-safe NYC 311 aggregate GET occurred under a superseded lane interpretation of robots silence; it was immediately quarantined and excluded. Consequently, no lawful edge feature could be computed and no predictive relationship could be tested. **Predictive alpha remains untested.**

The three frozen pilot hypotheses received an event-level replay with explicit missing and not-testable rows, seasonal and prior-quarter guidance baselines, and H-001 as a control comparator where comparable. No regression, machine learning, threshold search, geography selection, imputation, or post-hoc feature change occurred.

## Pilot decisions

### H-004 — WSF Ferry Ridership: INCONCLUSIVE

- Information versus seasonality: not testable; no WSF feature was lawfully collected.
- Timing: archive cadence appears potentially early enough, but exact report-level first-publication evidence is unverified.
- Consolidated breadth: a Washington route panel is unlikely to be broad enough alone.
- Costs: direct data cost may be low, but permission, route mapping, service-capacity controls, and vintage maintenance are unresolved.
- Stability: not testable across time or geography.
- Falsification: reject usefulness if a permission-cleared 12-event panel fails the fixed direction across reporting regimes or adds no descriptive information versus the named baselines.

### H-005 — Orange County TDT: INCONCLUSIVE

- Information versus seasonality: not testable; no monthly PDF was lawfully collected. The all-lodging series is likely to contain known Orlando seasonality.
- Timing: the collection and publication lag may be too late for guidance even if exact release timestamps are established.
- Consolidated breadth: one hotel-heavy county is not broad enough for consolidated ABNB.
- Costs: data cost may be low, but PDF/vintage maintenance and tax-definition auditing are non-trivial.
- Stability: not testable across time or geography.
- Falsification: reject as an edge signal if a 12-event lawful panel only mirrors the seasonal baseline or changes implication across the COVID/tax regimes.

### H-006 — NYC OSE STR Snapshots: INCONCLUSIVE

- Information versus seasonality: not testable; no snapshot was lawfully collected. The series may primarily identify the Local Law 18 regime.
- Timing: exact snapshot publication timing is unresolved; current records cannot be backfilled.
- Consolidated breadth: NYC's compliant home-share segment is too narrow to establish consolidated materiality alone.
- Costs: aggregate prospective capture may be inexpensive, but regime-definition and snapshot preservation are operationally demanding.
- Stability: no two-year post-regime history or four-transition chain is available.
- Falsification: reject predictive use if a lawful eight-event post-regime panel is dominated by implementation ramp or has unstable direction; retain only as a regulatory control.

## Remaining source decisions

`WATCH_PROSPECTIVELY`: NASA Black Marble, Vancouver STR Licenses, NPS Visitor Use, San Diego STRO Active, MarineCadastre AIS, and Melbourne Pedestrian Counts.

`CONTROL_ONLY`: NOAA HMS Smoke, NYC OSE Enforcement Reports, FTA NTD Monthly Ridership, and New Orleans STR Enforcement Hearings.

`INCONCLUSIVE`: WSF Ferry Ridership, Orange County TDT, NYC OSE STR Snapshots, and New Orleans STR Permit Events.

`REJECT`: NYC 311 Tourism Stress.

No source is promoted. A decision reflects E1 readiness, not the sign or size of an outcome relationship.

The lane-local E1 appendices also preserve five E0 lane candidates that were not retained in the final combined 15: TfL Cycle Hire, CDOT Continuous Counts, Austin Active STR, Hawaii TAT district archives, and Recreation.gov availability. They were not user-approved as part of the final 15, were not included in the combined disposition table, and were not tested against ABNB outcomes.

## Leakage and collection conclusion

Observation date, reference period, initial publication, revision, local collection, and prediction cutoff remain separate fields. Blank timestamps remain blank. No present snapshot was treated as a historical vintage, no equality-at-cutoff row was admitted, and no ineligible edge row entered the proposed model matrix. NASA remains blocked pending separate credential-sync confirmation and an exact-path version audit; no credential value was accessed.

## Stop

Phase E1 stops here. The proposed handoff is schema-complete but deliberately non-executable. A later quant phase requires separate authorization plus lawful point-in-time source artifacts meeting the frozen minimum-evidence rules.


## Permission-resolution continuation

At 2026-09-03T17:15:18Z, both fixed lanes had completed the authorized official-page reconnaissance. The combined append-only manifest contains 83 permission rows. There were 68 sent permission attempts: 33 sandbox attempts that ended before HTTP because DNS was unavailable and 35 one-time provider-facing GETs after preregistered retries. Provider responses were 29 HTTP 200, five HTTP 403, and one HTTP 404; all 35 bodies were cached and checksummed. Stop rows prevented 14 further planned requests. No refusal was retried.

No final exact data path passed the lead gate. Terms and robots were evaluated separately, and silence was not treated as affirmative robots permission. The sole data-payload request, DP-PW-001, was a one-row NYC 311 `count(*)` response made after the physical lane had treated an unlisted `/resource/` path as allowed. Lead review superseded that interpretation: the request is the run's sole unauthorized-under-final-gate compliance exception, robots status is `unclear`, the final gate is false, the payload is quarantined, and no further NYC 311 request is permitted. A parsed-field audit found only `request_count`; no row-level or personal field was transported. It is also a current response rather than a historical publication vintage, so it is excluded from H-004/H-005/H-006, all features, and any model.

H-004, H-005, and H-006 therefore remain unreplayed: each still has zero strict-cutoff-eligible edge observations and remains `INCONCLUSIVE` under its frozen failure rule. All other source decisions are unchanged. No source is promoted, no outcome was inspected, and no regression, machine learning, threshold tuning, or quant phase began. The complete request-level evidence is in `permission_resolution/request_level_audit.csv`.
