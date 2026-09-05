1. ABNB Edge-Data Research Orchestrator — main Codex task; owns orchestration, user communication, and the final decision.
2. abnb_alt_data — permanent gpt-5.6-sol research lead; owns source governance, permission decisions, canonical registries, point-in-time methodology, hypothesis reconciliation, and the final ranked slate.
3. physical_world_activity_edge — searches physical sensors, mobility, transportation, remote sensing, environmental, and infrastructure data.
4. supply_scarcity_web_edge — searches STR supply, regulatory, public-calendar, capacity-scarcity, pricing, and permitted web-exhaust data.

# Source-selection memo — Phase E0

## Decision boundary

Phase E0 is complete. This is an ex-ante source-governance ranking, not evidence of forecast improvement. **Predictive alpha has not been tested.** No ABNB outcome relationship was inspected, no hypothesis was added, no model or replay was run, and Phase E1 has not begun.

`historical_class=backtestable_now` below means only that dated source artifacts exist. It does not mean collectibility is cleared. Each such source has `status=pending_permission`, and every candidate currently has `strict_cutoff_eligible_now=false` until exact permission and event-level release timestamps are verified.

| Rank | Source | Score | Class | Potential target | Biggest failure reason |
| --- | --- | --- | --- | --- | --- |
| 1 | NASA_BLACK_MARBLE_VNP46A2 | 80 | prospective_only | Nights booked; geographic mix; quarterly revenue | Radiance may be dominated by stable infrastructure and environmental artifacts rather than lodging occupancy |
| 2 | NOAA_HMS_SMOKE | 77 | prospective_only | Nights booked; geographic mix; quarterly revenue; guidance downside risk | Smoke is sparse, highly seasonal, and may proxy widely known wildfire news rather than incremental destination demand. |
| 3 | WSF_FERRY_RIDERSHIP | 77 | backtestable_now | Nights booked; geographic mix; quarterly revenue; next-quarter guidance | Single-region materiality may be too small and route counts may mostly reflect commuter/service-supply dynamics |
| 4 | NYC_OSE_STR_SNAPSHOTS | 74 | backtestable_now | nights booked; revenue; geographic mix; next-quarter guidance | The regime is too new and NYC's legal home-share segment may be too small to explain consolidated ABNB. |
| 5 | ORANGE_FL_TDT_RELEASES | 73 | backtestable_now | quarterly revenue; nights booked; U.S. leisure demand; guidance direction | TDT is a lagging all-lodging/price signal dominated by hotels and theme parks rather than an early Airbnb-specific signal. |
| 6 | VANCOUVER_STR_LICENSES | 72 | prospective_only | active host supply; nights booked; geographic mix; revenue | Historical status survivorship cannot be ruled out from the present extract. |
| 7 | NPS_VISITOR_USE | 71 | prospective_only | Nights booked; geographic mix; quarterly revenue | Lack of preliminary vintages means the most decision-relevant recent months cannot yet meet strict cutoff rules |
| 8 | NYC_OSE_ENFORCEMENT_REPORTS | 68 | backtestable_now | nights booked; revenue; active supply; geographic mix | Annual policy-driven counts may measure enforcement effort rather than economically material supply removal. |
| 9 | FTA_NTD_MONTHLY_RIDERSHIP | 67 | prospective_only | Nights booked; domestic geographic mix; quarterly revenue | Two-month lag and no station detail may leave little incremental information after broader mobility/transport data |
| 10 | NOLA_STR_PERMIT_EVENTS | 66 | prospective_only | active supply; nights booked; revenue; U.S. geographic mix | A present extract may not preserve the historical state or prove when each event was public. |
| 11 | NOLA_STR_ENFORCEMENT_HEARINGS | 64 | prospective_only | active supply; nights booked; revenue | Enforcement activity may be policy effort and backfilled workflow data rather than timely supply removal. |
| 12 | SAN_DIEGO_STRO_ACTIVE | 63 | prospective_only | active supply; nights booked; U.S. geographic mix | The active-only snapshot has no defensible historical reconstruction and contains avoidable personal data fields. |
| 13 | MARINECADASTRE_AIS | 62 | prospective_only | Nights booked; geographic mix; travel disruption | Operational service is unavailable and annual publication timing is likely too late for same-quarter forecasting |
| 14 | NYC_311_TOURISM_STRESS | 60 | prospective_only | Nights booked; active supply; geographic mix | Complaints measure reporting and enforcement behavior, not tourist presence, and vintage reconstruction is unresolved. |
| 15 | MELB_PED_HOURLY | 58 | prospective_only | Nights booked; geographic mix; quarterly revenue | No defensible historical publication vintages and undefined portal terms |

## Backtestable-now archive candidates

- `WSF_FERRY_RIDERSHIP`: archive proven through dated quarterly PDFs; permission pending; 0/23 event rows are currently strict-eligible. Estimated 23/23 guidance cutoffs have a prior report, subject to exact publication verification.
- `ORANGE_FL_TDT_RELEASES`: archive proven through separate monthly PDFs with explicit release timestamps; permission pending; 0/23 event rows are currently strict-eligible. Estimated 23/23 coverage.
- `NYC_OSE_STR_SNAPSHOTS`: archive proven for FY23-FY26 reports and a dated 2026 snapshot; permission pending; 0/23 event rows are currently strict-eligible. Roughly 11/23 cutoffs have regime context, with high-frequency history only in 2026.
- `NYC_OSE_ENFORCEMENT_REPORTS`: archive proven through annual 2016-2024 PDFs; permission pending; 0/23 event rows are currently strict-eligible. Annual cadence is weak.

## Prospective-only candidates

`VANCOUVER_STR_LICENSES`, `NOLA_STR_PERMIT_EVENTS`, `NOLA_STR_ENFORCEMENT_HEARINGS`, `SAN_DIEGO_STRO_ACTIVE`, `FTA_NTD_MONTHLY_RIDERSHIP`, `MARINECADASTRE_AIS`, `NYC_311_TOURISM_STRESS`, and `MELB_PED_HOURLY` have present extracts or operational histories but no defensible historical publication-state reconstruction. They must start with timestamped prospective snapshots if permissions clear.

`NASA_BLACK_MARBLE_VNP46A2`, `NOAA_HMS_SMOKE`, and `NPS_VISITOR_USE` are also classified `prospective_only` for E0 despite their source archives: NASA is pending `EARTHDATA_TOKEN` sync and a granule-version audit; NOAA is pending path permission and daily-file provenance; NPS lacks a preliminary-vintage solution, so the current API cannot reconstruct what was visible at each cutoff.

## Best three historical pilots

### WSF_FERRY_RIDERSHIP

Mechanism: Ferry riders—especially Anacortes/San Juan, Bainbridge, Vashon and other leisure-sensitive route segments—measure realized movement into island/coastal destinations; foot/vehicle mix and service completion help separate demand from capacity disruption

Primary formula: Latest dated report strictly before cutoff: YoY change in fixed leisure-route foot passengers minus YoY change in fixed Seattle/Bainbridge and Seattle/Bremerton commuter-control foot passengers.

Single sensitivity: Use total riders instead of foot passengers with the same fixed route sets.

Biggest failure: Single-region materiality may be too small and route counts may mostly reflect commuter/service-supply dynamics

Coverage: Estimated 23/23 target events have a preceding completed-quarter report by cadence; exact per-report availability must be audited before eligibility

### ORANGE_FL_TDT_RELEASES

Mechanism: Tax remittances capture realized paid transient-lodging receipts in Orlando before many conventional annual statistics.

Primary formula: YoY percent change in the trailing three-month sum of Orange County TDT collections from PDFs released strictly before the cutoff.

Single sensitivity: Use the latest single released collection month YoY instead of the trailing three-month sum.

Biggest failure: TDT is a lagging all-lodging/price signal dominated by hotels and theme parks rather than an early Airbnb-specific signal.

Coverage: Likely 23/23 events have at least one prior monthly release; exact event-level audit remains required.

### NYC_OSE_STR_SNAPSHOTS

Mechanism: Registrations granted less refusals/revocations measure legally executable host supply under Local Law 18.

Primary formula: Percent change in unique active registration numbers between consecutive dated OSE snapshots released strictly before the cutoff, aggregated citywide and never retaining addresses or listing identifiers.

Single sensitivity: Use the grant-to-application ratio from the latest dated annual registration report strictly before the cutoff.

Biggest failure: The regime is too new and NYC's legal home-share segment may be too small to explain consolidated ABNB.

Coverage: Approximately 11 of 23 guidance events have post-regime context; high-frequency snapshots only verified in 2026.

## Moonshot prospective collectors

- `NASA_BLACK_MARBLE_VNP46A2`: Median quality-screened radiance YoY change across fixed resort polygons minus matched resident-control polygons over the last 28 eligible days. Sensitivity: Fraction of valid pixels with positive YoY radiance change under identical masks. Main risk: radiance is not occupancy.
- `MULTICITY_STR_PUBLIC_SNAPSHOT_MESH`: Daily aggregate active-permit stock by city from approved official APIs; quarterly feature is net active-stock change divided by beginning active stock across a fixed equal-weight city panel. Sensitivity: Renewal survival rate for the same fixed city panel. Main risk: non-comparable municipal regimes and unresolved automated-access permission.

## Informational advantage and replication difficulty

The differentiated sources are operational by-products: route/fare ferry counts, individual dated tax releases, jurisdiction-specific permit workflows, manual smoke polygons, and quality-screened satellite tiles. Replication requires stable geography mappings, release-time archives, sensor/regime change ledgers, and lawful collector maintenance. Their strangeness alone earned no score.

## Credential and cost boundary

Only `EARTHDATA_TOKEN` would be required, with no value stored in this run. No credential was accessed. No paid source, paid trial, Bloomberg request, commercial booking engine, OTA, Airbnb-controlled property, or authenticated API was accessed.

## Required stop

Stop after E0 and wait for the user's source-selection decision. Do not preregister a target relationship, run a backtest, fit a model, or start a prospective collector.
