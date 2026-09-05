# Supply/scarcity permission resolution

## Agent hierarchy

1. **ABNB Edge-Data Research Orchestrator** — orchestration, user communication, and final decisions.
2. **abnb_alt_data** — governance, canonical registries, point-in-time rules, and final retained slate.
3. **physical_world_activity_edge** — physical-sensor lane.
4. **supply_scarcity_web_edge** — this lane; the seven retained supply/scarcity sources below.

## Outcome

The exact-path `ScrapeCandidate` gate allowed **0 of 7** retained supply sources. Consequently, the lane made **zero data-payload requests**, transported no source records, and made no replay changes. H-005 and H-006 remain `INCONCLUSIVE` with **zero eligible observations each**. All seven existing E1 dispositions remain unchanged.

This directory covers only the seven final retained supply-lane IDs. Austin, Hawaii TAT, and Recreation.gov are lane-only appendix sources and were neither requested nor assessed here.

## Request accounting

- Permission manifest: 31 append-only rows. The seven sandbox DNS failures have exactly one preregistered retry each, identified in the later row's purpose note; the four rows skipped after those sandbox host stops were later attempted once as new first-attempt rows.
- Sandbox execution: 11 result rows — 7 pre-HTTP DNS failures and 4 local host-stop skips; none received a provider HTTP response.
- Escalated permission execution: 19 result rows — 18 provider GETs and 1 provider-host-stop skip. Provider responses were 15 HTTP 200, 2 HTTP 403, and 1 HTTP 404.
- Provider stop events: Vancouver terms HTTP 403; San Diego webmaps robots HTTP 403; Vancouver API documentation CAPTCHA marker; NOLA permit metadata CAPTCHA marker. No stopped request was retried.
- Cached provider response bodies: 18, each with UTC request time, effective URL, status, content type, byte count, SHA-256, and headers path in `permission_recon_results.csv`.
- Data-payload requests: 0. `data_probe_manifest.csv` is intentionally header-only.

## Source decisions

| Source | Exact-path gate | Existing E1 disposition | Terms | Robots | Privacy/projection and PIT blocker |
|---|---:|---|---|---|---|
| SCW-005 / NYC OSE STR snapshots | denied | INCONCLUSIVE | General terms do not clearly authorize automation | Silent for OSE paths, not affirmative | Current dated XLSX is a unit-level snapshot with no aggregate projection and no verified historical release panel; H-006 eligible n=0 |
| SCW-006 / Orange County TDT releases | denied | INCONCLUSIVE | Copyright route supplies no automation grant | Silent for archive/report paths, not affirmative | Reports are aggregate and archives look promising, but no lawful values or verified per-release publication timestamps; H-005 eligible n=0 |
| SCW-004 / Vancouver STR licences | denied | WATCH_PROSPECTIVELY | Terms returned 403 | `/api/` explicitly disallowed for User-agent `*` | API documentation triggered CAPTCHA; registered query is not aggregate/projected; no archived vintages |
| SCW-010 / NYC OSE enforcement reports | denied | CONTROL_ONLY | Public/research-use statement does not authorize automation | Silent, not affirmative | Annual vintages exist, but first-publication timestamps and revisions are unverified |
| SCW-002 / NOLA permit events | denied | INCONCLUSIVE | Policy report is not automation terms | Silent for `/resource`, not affirmative | Metadata triggered CAPTCHA; live underlying UID differs from registered path; current status revises and first-publication timing is unknown |
| SCW-003 / NOLA enforcement hearings | denied | CONTROL_ONLY | Policy report is not automation terms | Silent for `/resource`, not affirmative | Metadata request skipped after host stop; publication lag/backfill/revision evidence absent |
| SCW-008 / San Diego active STRO | denied | WATCH_PROSPECTIVELY | Data-use terms do not clearly allow automation | Portal robots 404; alternate host 403; exact CSV-host allowance unresolved | Bulk active-only CSV includes address, host contact, and tax fields with no server-side projection; no historical stock |

## Evidence interpretation

General open-data or research-use language was not elevated to affirmative automation permission. Likewise, a robots file that does not disallow a path was classified `unclear`, not `allowed`, as required for this continuation. HTTP 403 and CAPTCHA detections were provider stop events, while the original DNS failures were correctly preserved as sandbox failures and retried exactly once outside the sandbox.

The deterministic rerun is `preflight_permission_resolution.py`; its output is `scrape_candidate_decisions.csv`. Detailed cached-evidence interpretation is in `permission_evidence_assessment.csv`. The empty probe manifest and source-level no-request decisions make the absence of payload access explicit.
