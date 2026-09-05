# WSF H-004 post-freeze event replay summary

## Agent hierarchy

1. **ABNB Edge-Data Research Orchestrator** — main Codex task; owns orchestration, user communication, and the final decision.
2. **abnb_alt_data** — permanent research lead; owns governance, canonical registries, point-in-time methodology, reconciliation, and the combined result.
3. **physical_world_activity_edge** — WSF H-004 replay owner for this artifact.
4. **supply_scarcity_web_edge** — separate STR, regulatory, scarcity, and public-web lane; not used here.

## Result

The WSF H-004 post-freeze replay contains exactly 23 target events and **zero eligible WSF observations**. Every event is explicitly `not_testable` because the WSF permission gate denied collection and no lawful WSF report data, route values, or verified initial-publication timestamps exist in this run. No WSF request was made, and no current report was backfilled into a historical cutoff.

The frozen H-004 primary formula, sensitivity, positive expected direction, fixed route baskets, and strict-before-cutoff rule are repeated unchanged on all rows. Each row preserves the approved target-panel cutoff. The replay does not open transcripts and does not inspect or test any other physical source.

## Baseline and control context

- The target panel contains 23 events: 3 qualitative targets and 20 numeric-range targets.
- The seasonal-naive midpoint for the same guided fiscal quarter one year earlier is numeric and comparable for 16 events. It is explicitly `missing` for the other 7; no baseline is manufactured.
- The prior-quarter guidance midpoint is numeric and comparable for 19 events. It is explicitly `missing` for the other 4.
- The existing Phase-A H-001 implication/classification is joined only for its 16 already-comparable events. Those unchanged classifications contain 9 hits and 7 misses. They are control context, not evidence about WSF and not a fitted combination.
- WSF classifications are `not_testable` for the 16 seasonal-comparable and 19 prior-quarter-comparable rows. Rows lacking a named baseline are classified `missing` for that comparison.

H-004 therefore fails its prerequisite for testing: 0 strictly eligible events versus a minimum of 12. No directional accuracy, error metric, or relative-baseline performance can be computed. The corrected source-level E1 disposition is `INCONCLUSIVE`, as required when permission or exact historical timing fails; it is not positive signal evidence.

## Validation and provenance

- Output: `wsf_h004_event_replay.csv`
- Rows: 23
- Columns: 54
- Unique prediction IDs: 23
- Source ID: `WSF_FERRY_RIDERSHIP` on every row
- Hypothesis: `H-004` on every row
- Eligible rows: 0
- `not_testable` rows: 23
- Output SHA-256: `909ae2397f0f156056316f3342a48e6dc953e60dc24c9494c29bae56c18a61f2`
- Target-panel SHA-256: `c6b9455480ff004b0252ce26c5ccf10a1666ab3eefbf761d9902bb99b53d5ec7`
- Early-cohort H-001 replay SHA-256: `8aa15ef0e4ddd5968e393b175cafa36cba25fda4bc7c220586c6297634462d1e`
- Later-cohort H-001 replay SHA-256: `236e7e0664588e50f7e8c3c117472da555ae34b14cbf76a1a344e75978f530e1`

The auditable builder `build_wsf_not_testable_replay.py` reads only the approved target panel and the two existing Phase-A replay tables, selects H-001 rows, computes the two named arithmetic baselines without fitting, and asserts the row counts and comparison totals.
