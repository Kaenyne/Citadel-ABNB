# PR39 second-pass audit

Scope: PR39 head `5fce83b337fd528801f6547480745308084c09b3`, four scripts (`rnpl_materiality.py`, `rnpl_calendar_pilot.py`, `rnpl_calendar_pilot_report.py`, `h1_to_h2_bridge.py`) and the RNPL handoff. Exact small inputs and aggregate results were read through GitHub. No production output or code was changed.

## P2 — Freeze the pilot vintage list instead of requiring exactly five files in the shared archive

Location: `analysis/src/rnpl_calendar_pilot.py:124-126`.

`process_market()` globs every calendar for the market and raises unless the directory contains exactly five. PR41 subsequently populated the same shared `data/raw/inside_airbnb_calendar` archive; its committed `F1_provenance.csv` contains 20 Austin, 22 Rome and 6 Sydney snapshots. Consequently the documented full-pilot rerun now fails in each market before reading data, despite all original 15 inputs still being present. A six-filename synthetic fixture reproduces `ValueError: Expected five vintages for austin` using the unchanged function. Select the original five capture dates explicitly from the pilot provenance, or accept a frozen input manifest, and ignore unrelated vintages. This preserves both reproducibility and the original cohort definition.

## Verification results

- Ran the unchanged materiality `main()` with ROOT/SOURCE/OUT redirected to the audit fixture. All 10 loss thresholds and 48 exposure/hazard scenarios match committed values exactly. Q3/Q4 one-point growth losses remain 1.336m / 1.219m nights. The saved source SHA-256 reconciles exactly with the original CRLF representation; connector text copies and trailing-newline normalization are not a provenance defect.
- Ran the unchanged pilot self-test: passed elapsed/unmatched exclusions, transition counts, run boundaries, deterministic selection. Added a missing-calendar-date boundary case; runs correctly split at the date gap.
- Ran the unchanged report generator against the three committed JSONs and committed manifest. All 15 URL/byte-size checks pass, and the generated report matches the committed text apart from a trailing blank line introduced by the audit snapshot copy.
- Reviewed H1/H2 bridge arithmetic, dimension handling, transition construction, scenario identities and output flow. No additional material hidden arithmetic bug was established in this bounded pass. The RNPL-only interpretation and fixed overlays are explicitly marked as superseded exploratory assumptions in the code and handoff; reporting those assumptions again as undisclosed defects would be misleading.
- Raw calendar archives were not downloaded or reprocessed, so raw-source validity and full numerical calendar replication remain outside this pass. The count-guard failure is proven before raw-data I/O.

Reproduction: `check_pr39.py`; numerical results: `check_results.json`; exact-source fixtures: `fixture/`; post-PR41 snapshot count evidence: `F1_provenance.csv`.
