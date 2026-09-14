# L4 integration workboard v2

Execution date 14 September 2026; frozen information snapshot 13 September 2026. Starting commit `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`. Continue locally on `codex/lane4-full`; no public push, merge, outreach or investment adoption is authorized. All prior files are preserved.

| Package | Owner | Status | Exclusive new paths |
|---|---|---|---|
| Immutable L3 provenance and accounting eligibility | source worker | done; independently reviewed by artifact worker | lane4_sources_v2 code/data; L4_SOURCES_v2 note |
| Revenue, guide definitions and conditional uncertainty | revenue worker | done; parent independent arithmetic/hash audit PASS | lane4_revenue_v2 code/data; L4_REVENUE_v2 note |
| Linked workbook, horizon, memo/card/decisions | artifact worker | done; frozen final artifacts and rotated reviews PASS | lane4_model_v2 and lane4_review_v2 code/data; model/lane4_v2; deck/drafts/lane4_v2; corresponding new notes |
| Definitions, preservation, integration and independent review | parent | done; final export/preservation PASS; local commit only | lane4_control_v2 code/data; L4_INTEGRATION_PREREG_v2 and L4_CLOSE_HANDOFF_v2 notes |

The accepted source is Git commit `8821961853e4068febbfe2712f9a4e1036c9e629`, bundle `data/processed/forecast_methods/l3_bundle_v1/`, sourced from `7fb6fe0f248d5492b899672b9b70545da62d63ee`. Expected SHA256SUMS.json hash: `9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970`. Source extraction uses Git objects, not mutable L3 working files. The two explicitly supplied QVS notes in the original workspace are read-only support inputs and will be copied with hashes.

Independent review rotates after implementation: the source worker reviews the financial/memo claims, the revenue worker reviews artifact arithmetic and horizon behavior, and the artifact worker reviews revenue/source interpretation as capacity permits. Parent integrates findings and verifies exported artifacts and preservation. Authors do not approve their own packages.

Final versions: source/revenue `snapshot_v1`, model `snapshot_v2`, review `review_v2`.
All 4,381 pre-existing tracked files, 135 original FX dependency files, and all
registry/score files remain unchanged. Current definitions and defensible claims
are in [the L4 close handoff](05_backtests/L4_CLOSE_HANDOFF_v2.md). The original
workboard is preserved; this supplement records current L4 status.

## RESUME

Read L4_INTEGRATION_PREREG_v2.md before calculations. Retain the operational fixed kernel; conversion validation is complete and free-weight promotion failed. FX/RNPL application requires a compatible denominator, timing and reconciled hedge basis. The headline expectations comparison must use like objects. Missing explicit guide expectations, fee theta or hedge/cohort inputs remain unavailable. Complete the limited local integration rather than waiting for unidentified parameters or future captures.
