# Supply/scarcity web edge — Phase E1 collection and testability disposition

Run: `20260903T062839Z_abnb_edge_discovery`  
Lane: `supply_scarcity_web_edge`  
Policy assessment time: `2026-09-03T15:57:08Z`

## Agent hierarchy and ownership

1. **ABNB Edge-Data Research Orchestrator** — main Codex task; owns orchestration, user communication, and the final decision.
2. **abnb_alt_data** — permanent `gpt-5.6-sol` research lead; owns governance, canonical registries, point-in-time standards, and the final slate.
3. **physical_world_activity_edge** — physical sensor lane.
4. **supply_scarcity_web_edge** — this lane; owns only the ten E0 `SCW-*` sources and these lane-local E1 artifacts.

## Outcome

Every exact E0-registered source/path was reconstructed as an `abnb_alt_data.scraping_policy.ScrapeCandidate` and passed through `assess_scrape_candidate`. All 10 decisions were blocked. Therefore:

- direct source requests: **0**;
- HTTP responses, cached payloads, and response checksums: **none**;
- 401/403/429/CAPTCHA events or retries: **none**;
- credentials, paid sources, Airbnb-controlled sources, OTAs, personal data, and collection from booking engines: **none**;
- ABNB outcomes inspected: **no**;
- signal relationships tested: **no**;
- E1 historical observations eligible for testing: **0**.

The exact gate decisions, vintage limitations, and one disposition per source are in `e1_source_dispositions.csv`; the zero-request audit is in `e1_request_manifest.csv`.

These ten records are the supply/scarcity lane's discovery candidates. They are not the final combined 15-source approval slate and must not be described as such.

## Disposition slate

| Decision | Count | Sources | Interpretation |
|---|---:|---|---|
| `PROMOTE` | 0 | — | No source cleared both collection permission and historical point-in-time testability. |
| `WATCH_PROSPECTIVELY` | 2 | SCW-004, SCW-008 | Potential fixed aggregate snapshot panels after permission resolution; no historical backfill. |
| `CONTROL_ONLY` | 2 | SCW-003, SCW-010 | Better suited to regulatory-regime or enforcement context than a standalone predictive signal. |
| `INCONCLUSIVE` | 4 | SCW-001, SCW-002, SCW-005, SCW-006 | Economically plausible measures, but historical publication state or frozen minimum evidence is unresolved or unmet. |
| `REJECT` | 2 | SCW-007, SCW-009 | Explicit automation prohibition for SCW-007; undocumented dynamic route, booking-engine exclusion, and no vintages for SCW-009. |

## Point-in-time conclusions

- Genuine release-vintage potential is strongest for SCW-006 monthly Orange County TDT PDFs and SCW-010 annual NYC enforcement reports. Both remain `not_testable` because exact-path automation permission is not established. SCW-006 is `INCONCLUSIVE` because H-005 has zero eligible observations and fails its frozen minimum-evidence rule; SCW-010 remains `CONTROL_ONLY` as regulatory context.
- SCW-005 has genuine annual report vintages, but H-006 has zero eligible observations and fails its frozen minimum-evidence rule; the short, structurally discontinuous post-March-2023 regime is therefore `INCONCLUSIVE`.
- SCW-004 and SCW-008 are present-state extracts. Historical event dates inside a current file do not establish historical availability. Only prospective timestamped aggregate snapshots are defensible.
- SCW-002 and SCW-003 mix event dates with mutable workflow/status fields. No event is eligible without evidence of first public availability strictly before a future cutoff.
- SCW-001 lacks a stable underlying historical dataset identifier and verified vintages.
- SCW-007's 1997-present archive is unusable under the reviewed State terms despite excellent timing evidence.
- SCW-009 is overwritten live availability with no documented public availability API or historical snapshots; the exact dynamic route was not requested.

## Guardrails for any later reconsideration

No candidate may move out of `not_testable` based on the current record. Reconsideration requires a new timestamped exact-path policy assessment. Historical use additionally requires independently verified observation date, reference period, initial publication timestamp, revision/vintage, collection timestamp, and strict pre-cutoff availability. Current snapshots must never be backfilled. Any future collection from SCW-004 or SCW-008 must project only aggregate-safe/non-personal fields before transport and must retain fixed timestamped snapshots.

This phase is collection/testability disposition only. Hypotheses remain unfrozen in this lane record and no ABNB outcome was accessed.
