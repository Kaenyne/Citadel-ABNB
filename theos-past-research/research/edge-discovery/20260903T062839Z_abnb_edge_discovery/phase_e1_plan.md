# ABNB Edge Discovery Phase E1 Implementation Plan

> **For agentic workers:** Execute only the ownership assigned here. The research lead owns canonical files and reconciliation; the two existing lane agents own only their lane-specific E1 directories and may not spawn agents.

**Goal:** Determine which of the 15 user-approved E0 sources can be lawfully and point-in-time tested, run a fixed-rule event replay for at most the three frozen pilot families, and produce an audit-ready proposed long-format quant handoff without beginning modeling.

**Architecture:** The lead freezes H-004 through H-006 in the canonical hypothesis ledger, reconciles two independent source lanes, and generates one combined E1 package. Eligibility requires verified source availability strictly before each target cutoff; blocked or missing evidence produces explicit `not_testable` rows rather than imputation.

**Tech stack:** UTF-8 CSV, Markdown, Python standard library for deterministic generation and validation, repository `abnb_alt_data.scraping_policy` for request gates.

**Spec:** the approved pasted specification supplied with this edge-discovery task

## Global constraints

- Run ID is `20260903T062839Z_abnb_edge_discovery`; run-specific output stays under this run directory.
- No paid source, authenticated access, Airbnb-controlled scraping, OTA, commercial booking engine, Bloomberg, credential readback, personal data, regression, or machine learning.
- Reuse exactly `physical_world_activity_edge` and `supply_scarcity_web_edge`; spawn no agents.
- Test only WSF Ferry Ridership, Orange County TDT, and NYC OSE STR Snapshots against ABNB outcomes.
- Preserve observation, reference-period, first-publication, revision, collection, and cutoff timestamps separately.

### Task 1: Freeze the pilot hypotheses

**Files:** Modify `research/hypothesis_ledger.csv` append-only.

- [x] Append H-004 for WSF Ferry Ridership.
- [x] Append H-005 for Orange County TDT.
- [x] Append H-006 for NYC OSE STR Snapshots.
- [x] Validate exactly six total hypotheses and preserve H-001 through H-003.

### Task 2: Reassess source collection and testability

**Files:** Create lane-specific E1 evidence only within each existing lane directory; modify canonical source and scrape registries only through the lead.

- [x] Record user approval for all 15 source IDs without overriding provider restrictions.
- [x] Run the deterministic gate before every contemplated direct request.
- [x] Preserve blocked, prospective, pending-sync, rejected, and lawful-probe outcomes with request counts and checksums.
- [x] Reconcile one final disposition per source: `PROMOTE`, `WATCH_PROSPECTIVELY`, `CONTROL_ONLY`, `INCONCLUSIVE`, or `REJECT`.

### Task 3: Construct strict point-in-time feature and replay rows

**Files:** Create `phase_e1/features_long.csv`, `phase_e1/event_level_replay.csv`, and `phase_e1/baseline_audit.csv`.

- [x] Use the existing 23-event target panel only after the H-004–H-006 freeze.
- [x] Apply the frozen primary formula and single sensitivity without threshold or geography search.
- [x] Keep every event, including exclusions, missing values, regime breaks, and `not_testable` rows.
- [x] Compare with seasonal-naive, prior-quarter, and H-001 where comparable; fit no model.

### Task 4: Produce the E1 decision memo and proposed handoff

**Files:** Create `phase_e1/source_dispositions.csv`, `phase_e1/phase_e1_memo.md`, `phase_e1/claim_source_ledger.csv`, and `phase_e1/proposed_quant_handoff/`.

- [x] Answer the seven required decision questions for each pilot and state when no lawful test ran.
- [x] Define the exact leakage-audited long format, dictionary, provenance, cutoff audit, replay, model restrictions, and manifest.
- [x] Exclude ineligible rows from any proposed model matrix and label the package non-executable until a later quant authorization.

### Task 5: Verify and stop

- [x] Validate schemas, row counts, timestamps, decisions, formulas, and checksums.
- [x] Run repository tests, project validation, and `git diff --check`.
- [x] Confirm no paid/authenticated source, credential, restricted transcript, regression, or ML was used.
- [x] Stop after Phase E1.
