# GBV conversion and earnings-event audit

This additive package completes the user-requested GBV conversion risk audit and four-quarter Excel/two-page memo. It does not build the nights/ADR/cost track or extend past Q2 2027. The exact current EWM working case remains conditional; the fixed earlier-origin ex-COVID replay fails promotion. No short trade, causal call response or calibrated four-quarter distribution is established.

Read `docs/revenue-forecast-strategy/05_backtests/GE_PREREG_v1.md`, `GE_DELIVERY_v1.md`, and `WORKBOARD_GBV_EVENT_COMPLETE_v1.md` under the strategy docs root. Subpackages each own their source and outputs:

- `forecast/`: pinned earlier-origin replay and exact three-factor covariance attribution; requires the explicitly documented preserved quant-validation source checkout.
- `events/`: full23-event panel, proxy definitions, date guards, associations, influence and entry-time boundaries.
- `sources/`: dated source inventories, intraday availability and independent arithmetic/source review.
- `integration/`: preserved four-quarter GBV conversion and explicit Q2 input dependency. Canonical output `integration_v2`.
- `registry_scoring/`: seven new LIVE point-only records and both untouched scorers redirected to additive audit outputs.
- `artifacts/`: single artifact-tool workbook author, input/zero/missing tests, sheet previews and native Excel recalculation/cache verification.
- `artifacts_pdf/`: exactly two-page ReportLab memo, three charts, Markdown companion and visual/page-count QA.

Use each subpackage's README for exact commands and fresh research-output names. Existing output directories and registry names are guarded against replacement; new research vintages require new output names. The workbook's dated draft paths may be rebuilt from these fixed inputs as described in its README. No frozen or pre-existing tracked file was modified. Local runtime junctions and Python caches are excluded from Git.

Final artifacts: `outputs/gbv-event-20260915/ABNB_GBV_guidance.xlsx` and `output/pdf/gbv-event-20260915/ABNB_GBV_two_pager.pdf`. They were not published or submitted; work remains local on `codex/submission-readiness-v1`.
