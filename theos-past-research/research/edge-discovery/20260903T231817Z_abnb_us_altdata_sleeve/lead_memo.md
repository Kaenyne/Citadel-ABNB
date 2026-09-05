# ABNB U.S. alternative-data sleeve — lead memo

Run: `20260903T231817Z_abnb_us_altdata_sleeve`  
Lead: `abnb_alt_data`  
Lanes: `physical_world_activity_edge`, `supply_scarcity_web_edge`

## Decision

The smallest governed sleeve is complete, but it is **not a historical backtest**. It contains 384 monthly SFO aggregate passenger rows and 99 monthly EU27 collaborative-platform-night control rows, all from governed current snapshots. Their original historical publication vintages are unavailable, so strict point-in-time eligibility is zero observations and zero event features.

SFO and Eurostat are `WATCH_PROSPECTIVELY`. FHWA, Census QSS, BLS archived CPI, TSA, BTS, NPS, FTA, PANYNJ, LAX, and the three reviewed municipal STR sources remain `INCONCLUSIVE`, blocked, or prospective-only. No source is promoted. No alpha or predictive power is claimed.

## Collection and permission outcome

- 22 permission-reconnaissance attempts were preregistered in lane manifests; 15 provider HTTP GETs were actually made. Every GET was for a robots, terms, license, documentation, metadata, or publication page. This run made **zero data-payload requests**.
- PANYNJ's official terms support public download and reuse, but neither terms nor robots evidence affirmatively authorizes automation of `/resource/h87k-kqb6.json`. The deterministic exact-path gate is false, and no parking payload was requested.
- LAX permission review stopped after the official terms response triggered the conservative CAPTCHA/human-verification marker. No metadata or passenger payload was requested, and there was no retry.
- FHWA robots explicitly disallows `/policyinformation/travel_monitoring/` while allowing only the `tvt.cfm` index inside it. That exception does not cover dated XLS/XLSX payloads.
- BLS robots returned HTTP 403 before any archived CPI release page was requested. Census API-host robots returned a rejection page and the tested QSS metadata path returned 404. Neither source produced observations.
- Governed SFO and Eurostat data caches from the earlier broad-scrape run were reused locally; there was no new provider request.

## Compliance exception retained in the audit

Eight executed physical-lane permission-page GETs have `registered_at_utc` later than `requested_at_utc` in the lane's final manifest: three FHWA rows and five PANYNJ/LAX rows. The combined request audit preserves those timestamps and marks `manifest_precedes_request=false`; it does not rewrite history. No data payload followed any of these requests, and every corresponding exact data-path gate remained false. This is a process-control exception and prevents treating those reconnaissance rows as cleanly preregistered evidence.

## Fixed descriptive comparison

Six hypothesis IDs, H-007 through H-012, were frozen before target comparison. The fixed transforms use trailing three-complete-month year-over-year growth, a 120-day diagnostic lag for EU27 platform nights, and an exactly 50/50 U.S./Europe composite. The target is the guidance midpoint's year-over-year growth and its sequential acceleration. No thresholds, windows, cities, lags, or weights were optimized.

The current-snapshot diagnostic has 16 numeric guidance-growth comparisons and 15 acceleration comparisons where values overlap:

| Diagnostic | Pearson vs guidance YoY | Spearman vs guidance YoY | Acceleration direction concordance |
|---|---:|---:|---:|
| SFO passenger growth | 0.8155 | 0.4824 | 0.4000 |
| EU27 platform-night growth | 0.7252 | 0.3853 | 0.4000 |
| Fixed 50/50 composite | 0.7783 | 0.4118 | 0.4000 |

These values are retrospective alignments built from later current snapshots. They may reflect revisions, the pandemic recovery regime, common trends, and implicit historical backfill. They are not PIT evidence, do not satisfy any minimum-evidence rule, and must not be interpreted as a backtest, alpha, predictive power, or statistical significance.

## Artifact inventory

- `source_manifest.csv`: 14 official/public source records linked to canonical governance.
- `permission_audit.csv`: 33 request/reuse audit rows with request class, timestamps, URL, status, checksum, cache path, exact-field policy, personal-data scan, gate treatment, and eligibility exclusion.
- `observations_long.csv`: 495 normalized rows: 384 SFO, 99 EU27, and 12 explicit not-collected source rows.
- `guidance_targets.csv`: 23 fixed guidance events with prior-year comparable midpoint, YoY level, and sequential acceleration.
- `event_aligned_features.csv`: 161 rows, seven fixed feature records per event, with strict and diagnostic reference-period fields kept separate.
- `descriptive_comparison.csv`: fixed Pearson, Spearman, and acceleration-direction summaries, with strict `n=0` distinct from diagnostics.
- `publication_vintage_audit.csv`: publication, revision, vintage, and PIT disposition by source.
- `raw_file_manifest.csv`: three reused governed raw artifacts with retrieval time, URL, size, and SHA-256.
- `validation.json` and `checksums.sha256`: structural validation and artifact hashes.

## What would resolve the blocker

Strict historical testing requires immutable dated release artifacts or provider-supplied release/vintage timestamps that are demonstrably earlier than each guidance cutoff, plus affirmative exact-path automation permission. For PANYNJ and LAX, written provider authorization or explicit robots allowance for the precise aggregate API path would resolve the collection gate, but their current SODA histories would still remain non-PIT unless original vintages can be reconstructed. A prospective capture program can create defensible vintages going forward.

