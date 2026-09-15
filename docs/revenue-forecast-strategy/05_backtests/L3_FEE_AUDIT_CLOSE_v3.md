# L3 fee audit close — archival metadata isolation

Lead · 2026-09-13 · supersedes only the canonical output path in L3_FEE_AUDIT_REPAIR_v2.md.

Independent follow-up found that the September 11 dry-run diagnostic was using the caller's newly supplied metadata. Correctly requiring metadata to predate capture could then reject legitimate September 13 metadata intended for September 14's wave. The diagnostic now always uses its original frozen `sample_ids.csv`; both metadata sources are hashed if different. Actual wave rows retain the strict metadata-on/before-capture rule.

The regression supplies metadata dated September 13, confirms the future-wave consumer runs, and verifies that the archival dry run still reports six known-residence rows and hashes its original frame. `python -m pytest analysis/src/forecast_methods/fee_panel_v1/test_fee_panel.py -q` exits 0: **19 passed in 7.15 seconds**. The offline runner exits 0 into **`data/processed/forecast_methods/fee_panel_v1/reviewed_v3/`**, the canonical L4 source. Earlier output versions remain intact. No research estimate changed: wave n=0, theta unavailable, adoption pending.

## RESUME

Use reviewed_v3 for the immutable L4 handoff. New metadata may improve sanctioned future-wave matching, but it must never rewrite the archival diagnostic's information set. Preserve the initial independent findings and both repair notes; the final reviewer close note records whether all counterexamples are resolved.
