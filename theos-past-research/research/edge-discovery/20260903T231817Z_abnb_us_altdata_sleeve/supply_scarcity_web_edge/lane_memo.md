# U.S. accommodation and STR supply lane memo

## Scope and outcome

This lane performed source-side permission and point-in-time reconnaissance only. It did not inspect ABNB outcomes, guidance values, transcripts, or signal relationships.

Five candidate sources were assessed: the canonically registered BLS lodging CPI, newly registered Census QSS accommodation series, and a fixed three-city official STR panel covering New York City, New Orleans, and San Diego. The deterministic exact-path gate allowed **0 of 5**, so **zero data-payload requests** were made and `observations_long.csv` preserves explicit missing/not-collected rows rather than invented observations.

## Permission reconnaissance

The lane preregistered five permission-only GETs. Four reached providers and one BLS archive-index request was skipped after the BLS host stop:

- BLS `robots.txt` returned HTTP 403 with an Access Denied page warning that nonconforming bot activity is prohibited. The run did not request the archive index or any archived CPI release page.
- Census API terms returned HTTP 200 and expressly permit API services to retrieve and analyze Census data subject to attribution and anti-reidentification rules.
- Census API-host `robots.txt` returned HTTP 200 but the body was a request-rejection page, so robots status is `unclear`, not allowed.
- The canonically registered QSS metadata URL returned HTTP 404. The exact data path therefore remains unavailable/ambiguous and was not probed.

The status-only collector did not recognize the Census robots rejection carried inside an HTTP 200 body during execution, so the already-preregistered metadata request was issued next and returned 404. Cached-body review then imposed the ambiguity stop. This sequencing is preserved in `permission_response_interpretation.csv`; no later Census request and no data request occurred.

Same-day cached permission evidence was reused without duplicate requests for all three city sources. NYC terms/robots remain unclear and its workbook is a unit-level current snapshot. NOLA lacks affirmative automation permission and earlier metadata access triggered CAPTCHA. San Diego lacks exact download-host permission and offers only a bulk active-current file containing fields that cannot be excluded before transport.

## Point-in-time disposition

- **BLS_CPI_LODGING — not testable in this run.** The original-release route is economically and temporally preferable to the current API, but archive access stopped at permission. No current API value was backfilled as a vintage. H-003 remains unresolved; no relationship test occurred.
- **CENSUS_QSS_ACCOMMODATION — discovery only / path unavailable.** Terms are favorable, but exact-host robots evidence is unresolved and the registered metadata path is 404. QSS estimates are revisable, so even a current endpoint would require contemporaneous release artifacts for strict PIT use.
- **NYC_OSE_STR_SNAPSHOTS — blocked; current snapshot only.** No historical multi-city panel observation was created.
- **NOLA_STR_PERMIT_EVENTS — blocked; event dates are not publication vintages.** No observation was created.
- **SAN_DIEGO_STRO_ACTIVE — blocked; prospective-only if permission and provider-side privacy-safe aggregation later clear.** No observation was created.

## Artifacts

`candidate_source_manifest.csv` records the slate; `permission_request_manifest.csv`, `permission_request_results.csv`, `permission_response_interpretation.csv`, and `permission_evidence_reuse.csv` provide the request audit; `preflight_exact_paths.py` and `exact_path_gate_decisions.csv` preserve the policy gate; `data_request_manifest.csv` is intentionally header-only; `observations_long.csv` preserves missing outcomes with full PIT fields; and `publication_vintage_audit.csv` records the timing/vintage limitations.
