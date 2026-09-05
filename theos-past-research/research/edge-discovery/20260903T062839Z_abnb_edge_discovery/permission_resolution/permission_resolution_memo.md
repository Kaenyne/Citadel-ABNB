1. ABNB Edge-Data Research Orchestrator — owns orchestration, user communication, and the final decision.
2. abnb_alt_data — owns governance, canonical registries, PIT methodology, reconciliation, and the final slate.
3. physical_world_activity_edge — eight retained physical-world sources.
4. supply_scarcity_web_edge — seven retained supply/scarcity sources.

# Permission-resolution and lawful-extraction continuation

## Decision

All 15 approved retained IDs were reviewed. Final exact-path result: **0 allowed, 15 blocked**. Exactly one unauthorized-under-final-gate data probe occurred: the NYC 311 aggregate request made under a superseded robots-silence interpretation. It is quarantined, unused, and ineligible. No other data payload was requested. Predictive alpha remains untested.

## Request accounting

- Permission manifest rows: 83.
- Sent permission attempts: 68 (33 sandbox DNS failures; 35 provider-facing GETs).
- Provider responses: 29×200, 5×403, 1×404; 35 cached bodies.
- Planned rows not sent after stop: 14; one supply manifest row had no execution row and is retained as not executed.
- Data payload requests: 1; HTTP 200; one row/one field; quarantined and excluded.

## Source resolutions

| Rank | Source | Terms | Robots | Payloads | Eligible features | Decision |
|---:|---|---|---|---:|---:|---|
| 1 | NASA_BLACK_MARBLE_VNP46A2 | unclear | unclear | 0 | 0 | WATCH_PROSPECTIVELY |
| 2 | NOAA_HMS_SMOKE | unclear | unclear | 0 | 0 | CONTROL_ONLY |
| 3 | WSF_FERRY_RIDERSHIP | unclear | unclear | 0 | 0 | INCONCLUSIVE |
| 4 | NYC_OSE_STR_SNAPSHOTS | unclear | unclear | 0 | 0 | INCONCLUSIVE |
| 5 | ORANGE_FL_TDT_RELEASES | unclear | unclear | 0 | 0 | INCONCLUSIVE |
| 6 | VANCOUVER_STR_LICENSES | unclear | disallowed | 0 | 0 | WATCH_PROSPECTIVELY |
| 7 | NPS_VISITOR_USE | allowed | disallowed | 0 | 0 | WATCH_PROSPECTIVELY |
| 8 | NYC_OSE_ENFORCEMENT_REPORTS | unclear | unclear | 0 | 0 | CONTROL_ONLY |
| 9 | FTA_NTD_MONTHLY_RIDERSHIP | unclear | unclear | 0 | 0 | CONTROL_ONLY |
| 10 | NOLA_STR_PERMIT_EVENTS | unclear | unclear | 0 | 0 | INCONCLUSIVE |
| 11 | NOLA_STR_ENFORCEMENT_HEARINGS | unclear | unclear | 0 | 0 | CONTROL_ONLY |
| 12 | SAN_DIEGO_STRO_ACTIVE | unclear | unclear | 0 | 0 | WATCH_PROSPECTIVELY |
| 13 | MARINECADASTRE_AIS | unclear | unclear | 0 | 0 | WATCH_PROSPECTIVELY |
| 14 | NYC_311_TOURISM_STRESS | allowed | unclear | 1 | 0 | REJECT |
| 15 | MELB_PED_HOURLY | unclear | disallowed | 0 | 0 | WATCH_PROSPECTIVELY |

## Frozen pilots

H-004 WSF, H-005 Orange TDT, and H-006 NYC OSE each remain `INCONCLUSIVE`: zero strict-cutoff-eligible feature observations, no replay rebuild, and no outcome inspection. Archive promise is not permission clearance, and neither is event-level eligibility.

## Compliance exception

DP-PW-001 was preregistered before request and used server-side projection `count(*) as request_count`; the cached JSON contains only `request_count`. The physical lane treated robots silence as ordinary REP allowance. The lead applied the user's stricter rule, changed final robots status to `unclear`, set gate=false, quarantined the response, excluded it from every downstream artifact, and stopped further NYC 311 requests.

## Stop

This continuation ends inside Phase E1. No later quant phase was started.
