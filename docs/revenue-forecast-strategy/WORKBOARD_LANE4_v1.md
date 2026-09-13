# Lane 4 workboard supplement

2026-09-13. Branch `codex/lane4-full`; starting commit `1c87628cedbc94ab8a0e8552743c94485ef353b8`. User requested subagents and explicitly confirmed L4 ownership. This new supplement preserves WORKBOARD.md.

| Package | Owner | Status | Scope |
|---|---|---|---|
| L4 control and integration | parent | baseline complete; publication awaiting permission | 14 new LIVE rows; both scorers pass; all 284 old scores and 3,911 starting tracked files unchanged; local commit complete, public push rejected by automatic approval review |
| L4 revenue and guide | reconciliation subagent | implementation complete; L3 pending | Snapshot v1; 36 tests; exact legacy attribution; no competing RNPL or conversion estimate |
| L4 financial model | model subagent | complete for baseline review | Snapshot v4 workbook; legacy valuations reproduced; 84 internal and 91 parent export ties; renderer teardown limitation documented |
| L4 evidence review | committed_evidence_audit + independent reconciliation reviewer | complete | Committed L1/L2 provenance checked; independent final accounting/content review; wording findings resolved |
| L4 memo and card | committed_evidence_audit | complete, unsigned | Review v4: exactly two pages, editable source, 11 card items, 23 decision rows, 437 ledger rows; 16 tests |
| L3 conversion and FX/RNPL input acceptance | user handoff / L3 | pending | Zero accepted L3 inputs; separately versioned research, commit contents and checksums required |

The user explicitly confirmed L4 ownership after a brief conversion-research steering correction. Conversion work stopped at read-only sample/method scoping; no estimation ran. The scoping handoff is `05_backtests/L4_CONVERSION_SCOPING_HANDOFF_TO_L3_v1.md`.

L3 conversion and FX/RNPL integration are pending explicit accepted versions/commits and checksums supplied by the user. No research files are consumed from its changing worktree. Existing fixed-kernel outputs and conversion-dependent claims remain provisional. Direction, target, probabilities and card adoption remain unsigned.

## RESUME

Read `05_backtests/L4_CLOSE_HANDOFF_v1.md` for the definitive artifact versions, exact claims, reproduction commands, validation evidence and remaining gaps. Preserve the isolated L4 baseline and all earlier work. Accept L3 only through the user's explicit immutable handoff; do not silently read its worktree. Rebuild affected outputs in a new version, register only supported new current-date objects and run both scorers again. Direction, target, probabilities, card adoption and merge remain open.
