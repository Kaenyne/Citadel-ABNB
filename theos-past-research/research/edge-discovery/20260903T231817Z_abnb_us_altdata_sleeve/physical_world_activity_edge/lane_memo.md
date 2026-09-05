# Physical-world activity lane memo

Run: `20260903T231817Z_abnb_us_altdata_sleeve`

## Ownership and scope

Hierarchy: ABNB Edge-Data Research Orchestrator -> `abnb_alt_data` -> `physical_world_activity_edge` (this lane) and `supply_scarcity_web_edge` (peer lane).

This is source-side collection and point-in-time readiness work only. The lane did not inspect ABNB outcomes, guidance values, transcripts, or signal/outcome relationships. It made no hypothesis or alpha claim.

## Outcome

Eight official public candidates were audited. None passed the strict exact-path collection gate. No new data payload was requested. The only observations delivered are 384 aggregate SFO airport-month rows from a separately governed same-day cache. Every SFO row is marked `strict_pit_eligible=false` because the payload is an August 2026 current snapshot and original historical publication vintages were not recovered.

`SFO_AIR_PASSENGERS` is therefore `WATCH_PROSPECTIVELY`. TSA, FHWA, BTS, NPS, FTA, PANYNJ, and LAX remain `INCONCLUSIVE` rather than promoted.

## Permission audit

There were 17 preregistered permission-only rows and 11 actual provider GETs. Seven completed, three reached provider/conservative stop conditions, one was an HTTP 404, and six were not requested after source stops. Five additional NPS/FTA permission responses were reused from the same UTC day with matching SHA-256 checksums. There were zero new data-probe rows and zero new data GETs.

- TSA robots returned HTTP 403; the terms request was not attempted afterward.
- BTS TranStats robots returned HTTP 404 and BTS robots returned HTTP 403; remaining BTS permission requests were stopped.
- FHWA robots explicitly `Disallow: /policyinformation/travel_monitoring/` and only `Allow: /policyinformation/travel_monitoring/tvt.cfm`. The monthly XLSX path is therefore disallowed. The official FAQ says TVT is published within 60 days after month close, while the index warns estimates are continually updated and annually re-adjusted.
- NPS reused robots evidence explicitly says `Disallow: /`.
- FTA reused robots evidence is HTTP 403, leaving exact-path permission unresolved.
- PANYNJ official OPEN-NY terms and dataset metadata completed. The terms invite lawful content download/reuse but do not clearly authorize the proposed automation; robots lists a crawl delay and unrelated disallows but contains no explicit `Allow` for `/resource`. Under the governing rule that silence is not affirmative allowance, the gate is false.
- LAX robots similarly contains no explicit `Allow` for `/resource`. Its terms request returned HTTP 200 HTML but triggered the conservative human-verification marker stop; metadata was not requested afterward.
- SFO received no new request. The raw aggregate and metadata files were copied from governed run `20260903T204950Z_broad_scrape` under the lead's explicit provenance-only authorization.

## Point-in-time limits

The SFO observation rows retain `observation_date`, `reference_period`, blank `initial_publication_timestamp_utc`, the current snapshot's `data_as_of` as `revision_timestamp_utc`, `data_loaded_at`, local collection timestamp, vintage label, raw path, and raw SHA-256. Missing historical initial-publication timestamps force ineligibility. No present-day snapshot is represented as historical data.

FHWA has strong economic coverage and dated monthly artifacts, but its data directory is robots-disallowed and estimates are revised. PANYNJ has dated quarterly periods and a 2026 metadata update date, but that does not establish row-level historical publication vintages. LAX terms state older versions are not retained and data may be updated, corrected, overwritten, or refreshed. These are discovery or prospective candidates, not retrospective point-in-time features.

## Files

- `candidate_source_manifest.csv`: eight retained candidates and negative outcomes.
- `permission_request_manifest.csv` / `permission_request_results.csv`: TSA, BTS, and FHWA permission audit.
- `airport_permission_manifest.csv` / `airport_permission_results.csv`: PANYNJ and LAX permission audit.
- `permission_reuse_manifest.csv`: same-day NPS/FTA cache reuse.
- `permission_audit_summary.csv`: source-level request reconciliation.
- `exact_path_gate_decisions.csv`: fully instantiated `ScrapeCandidate` inputs and deterministic gate outputs.
- `data_probe_manifest.csv` / `data_probe_results.csv`: header-only proof of zero data requests.
- `observations_long.csv`: 384 SFO current-snapshot rows, all retrospective-PIT ineligible.
- `publication_vintage_audit.csv`: publication, revision, vintage, and eligibility findings.
- `source_dispositions.csv`: one decision per source.
- `raw_cache/`: immutable permission evidence and the two reused SFO payloads.
- `validation.json` and `checksums.sha256`: deterministic validation and artifact integrity.

The lane is complete for the permission state observed at the cutoff. Retrospective testing would require lawful exact-path permission plus defensible historical publication vintages; otherwise the source should only be watched prospectively.
