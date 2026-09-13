## What changed

Reconciles the legacy $3.059bn and K0 $3.158bn Q4 guide outputs, then links explicit team nights and ADR assumptions through the preserved fixed seasonal kernel to revenue, management guide, financial statements and conditional valuation. Adds an eight-tab recalculated workbook, exactly two-page review memo with editable source, unsigned November card, quantified decision register and source/assumption ledger.

The conditional operating review implies a $3.123bn Q4 guide. It remains provisional pending accepted L3 conversion validation and, separately, cohort FX/RNPL integration. No L3 research estimate, trade direction, adopted target or probability is invented.

## Why

Makes the guide's operating inputs, conversion, cushion and expectations comparison auditable and exposes how competing assumptions change the financial model. Preserves all completed L1/L2 work and the existing 2/3–1/3 kernel. The brief conversion scoping detour is saved for manual handoff to L3; no conversion estimation ran in L4.

Definitive deliverables and exact reproduction commands: `docs/revenue-forecast-strategy/05_backtests/L4_CLOSE_HANDOFF_v1.md`. Final versions are revenue `snapshot_v1`, model `snapshot_v4`, and memo/card `review_v4`. Historical development outputs and failures are retained.

## Validation

- 59 new implementation tests and 155 existing harness/kernel/return tests pass.
- Both actual scorers run after 14 current LIVE rows are registered across four scenario objects; all 284 old score rows match exactly, with zero floating drift and identical keys/labels/missingness.
- All 3,911 pre-existing tracked files and 135 read-only external FX files retain their hashes.
- Revenue identities independently reconstructed; legacy guide attribution reconciles within $0.001m.
- Final workbook and saved-file recapture: 1,576 formulas, zero error cells/external links, 91 independent cached-value checks within $0.001. Legacy $180.88/$156.79 valuation objects reproduced. Both PDF pages visually inspected.
- Independent economic/content review found no quantitative blocker; two wording findings were corrected.

The Windows PNG renderer emits valid inspected images but returns exit 1 during teardown; workbook build/export and recapture exit 0. Native Excel automation was not tested. An initial mixed-environment test-collection failure is preserved; corrected per-package runtime commands pass. These operational limits do not validate the investment thesis.

## Checklist

- [x] Numbers tie to the new versioned model and accompanying source/assumption ledger.
- [x] Changed assumptions are visible in the new workbook and model README; the original model and assumption files are preserved.
- [x] Binary work is isolated to a new version; no existing teammate-owned binary was edited.
- [x] No licensed/raw exports, external FX bundle, runtime modules or credentials included.
- [x] Independent subagent accounting/content review completed.
- [ ] Teammate review and any investment adoption remain open. No reviewer outreach or automatic merge performed, as instructed.
