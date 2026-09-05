# Physical-world activity edge — E1 collection/testability disposition

## Agent hierarchy

1. **ABNB Edge-Data Research Orchestrator** — main Codex task; owns orchestration, user communication, and the final source decision.
2. **abnb_alt_data** — permanent research lead; owns governance, canonical registries, point-in-time methodology, reconciliation, and the ranked combined slate.
3. **physical_world_activity_edge** — physical sensors, mobility, transportation, remote sensing, environmental, infrastructure, maritime/island, and realized-event activity lane.
4. **supply_scarcity_web_edge** — STR, regulatory, scarcity, and public-web lane.

## Scope and result

This pass performed collection and historical-testability disposition only. No ABNB outcome, guidance target, transcript, consensus series, correlation, replay, or model was inspected. Hypotheses are not treated as frozen.

The ten exact E0-registered candidates and intended paths were reconstructed as `ScrapeCandidate` objects and reevaluated with `assess_scrape_candidate` at `2026-09-03T15:25:09Z`. All ten decisions were `allowed=false`. Path-specific robots permission remained unclear for every source; WSF, Melbourne, CDOT, and TfL also retained unclear automation terms. NASA additionally required authentication and was expressly excluded by the task. Therefore **no network request was made**, no 401/403/429/CAPTCHA was encountered, no retry occurred, and no payload or response checksum exists.

The interruption audit found no partial E1 files or collection side effects. This E1 subdirectory contains the complete resumed work.

## Source decisions

| Rank | Source | Decision | Collection outcome | Historical testability conclusion |
|---:|---|---|---|---|
| 1 | WSF ferry ridership | `INCONCLUSIVE` | `not_testable` / 0 requests | Dated quarterly PDFs offer the lane's best potential vintage chain, but permission/timing failure and zero eligible observations prohibit promotion. |
| 2 | NASA Black Marble | `WATCH_PROSPECTIVELY` | `not_testable` / 0 requests | Authenticated access excluded; reprocessed collections require granule-specific vintages. |
| 3 | NOAA HMS smoke/fire | `CONTROL_ONLY` | `not_testable` / 0 requests | Environmental-disruption control only; regenerated bundles are not original vintages. |
| 4 | NPS visitor use | `WATCH_PROSPECTIVELY` | `not_testable` / 0 requests | Current revised database cannot reconstruct preliminary historical releases. |
| 5 | FTA NTD ridership | `CONTROL_ONLY` | `not_testable` / 0 requests | Broad mobility control; two-month lag and overwritten release products prevent strict replay. |
| 6 | TfL cycle hires | `WATCH_PROSPECTIVELY` | `not_testable` / 0 requests | Weekly files merit forward capture only after specific permission and replacement audits. |
| 7 | Melbourne pedestrian counts | `WATCH_PROSPECTIVELY` | `not_testable` / 0 requests | Current history lacks vintages and sensor relocations create survivorship risk. |
| 8 | MarineCadastre AIS | `WATCH_PROSPECTIVELY` | `not_testable` / 0 requests | Partial history and unresolved release/service behavior preclude replay. |
| 9 | CDOT continuous counts | `INCONCLUSIVE` | `not_testable` / 0 requests | Publication history, correction policy, and station continuity are insufficiently documented. |
| 10 | NYC 311 | `REJECT` | `not_testable` / 0 requests | Mutable records, semantic drift, reporting behavior, and privacy burden overwhelm causal specificity. |

`INCONCLUSIVE` for WSF reflects H-004's frozen failure conditions: permission and exact historical timing failed, collection is `not_testable`, and zero observations are eligible. `CONTROL_ONLY` means a source could account for broad mobility or disruption regimes if its own permission and vintage requirements are later satisfied; it should not be positioned as a primary alpha signal.

## Permission and request audit

- Exact registered URLs, terms URLs, robots URLs, intended paths, rate, caching plan, user agent, and deterministic denial reasons are preserved in `e1_permission_reassessment.csv`.
- The per-source probe ledger in `e1_probe_manifest.csv` records `actual_request_count=0`, `outcome=not_testable`, and blank HTTP, artifact, checksum, and request-time fields. Blank values mean no response existed, not missing logging.
- No authenticated API, credential, paid source, Airbnb-controlled property, OTA, or booking engine was accessed.
- No credentials or environment files were read or modified.
- No ambiguous permission was reinterpreted as consent, and no denial was retried or routed around.

## Point-in-time implications

The result is deliberately conservative. Official historical coverage is not equivalent to a replayable information set. WSF is closest because report artifacts are dated; even there, report generation time must be distinguished from first public availability. NOAA bundles show why a current archive can be misleading: later regeneration can preserve observation dates while destroying the historical publication vintage. NPS, FTA, Melbourne, CDOT, and NYC similarly require release-specific files or prospective snapshots before strict-before-cutoff eligibility can be established.

No source observation is marked historically eligible in this pass. The correct outcome is `not_testable`, not a synthetic zero, neutral signal, or failed relationship.

## Stop condition

The physical lane stops before target access. If the lead confirms hypotheses are frozen, only a user-approved source whose permissions and vintage chain have been independently resolved should proceed to an event-by-event test. Until then, the structured decisions here are the final E1 collection/testability handoff.
