# L4 v2 review memo, evidence exhibits and unsigned decisions

Final artifacts: `deck/drafts/lane4_v2/review_v2/`; numerical bindings and QA: `data/processed/forecast_methods/lane4_review_v2/review_v2/`. The editable Markdown memo renders to exactly two pages. Three accepted L3 charts are preserved byte-for-byte as PNG/SVG, with a separate three-page PDF adding explicit interpretation limits. This appendix does not change the two-page memo count.

From the L4 worktree root, with bundled Python (ReportLab and pypdf):

```powershell
$l4Python = 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $l4Python -B analysis/src/forecast_methods/lane4_review_v2/run.py --revenue-dir data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1 --model-dir data/processed/forecast_methods/lane4_model_v2/snapshot_v2 --run-id reproduction_v1 --render-pages
& $l4Python -B -m unittest discover -s analysis/src/forecast_methods/lane4_review_v2/tests -v
```

An existing run ID is refused. Explicit source paths are snapshotted and hashed before/after use. No changing L3 research worktree is followed. Source acceptance comes from `lane4_sources_v2/snapshot_v1`, consuming Git bundle 8821961853e4068febbfe2712f9a4e1036c9e629 and research commit 7fb6fe0f248d5492b899672b9b70545da62d63ee. No research fit, registration, scenario probability or investment adoption occurs here.

Outputs include `review_memo.md/pdf`, `accepted_L3_exhibits.pdf`, 12-rule unsigned November card in Markdown/CSV/JSON, 13-row quantified decision register, same-basis expectations and financial scenarios, and a 1,767-row source/assumption ledger. The ledger retains all 1,187 original L3 dispositions and adds explicit model-period/unit, inherited-assumption and cash-flow rows. Rejected free-weight joint extrema remain a separate descriptive CSV, not production cases or K0 error bands. Three main financial envelopes are shown within the nine-case model, excluding isolated net-revenue sensitivities.

R-S compares Q4 revenue to dated revenue consensus. G-S is a different-object diagnostic. The hypothetical S/(1+c) is explicitly not observed guide consensus. Management-guide expectations remain unavailable. The main horizon is 13 September 2027 with 256/365 of uniform FY27 net cash/share flows from FY26 end; the December comparison is separate. Cushion changes the guide only, not revenue/earnings/cash.

`scoring.py` preserves conservative interval arithmetic, missing/ambiguous evidence, exact wording and the unsigned status. Original team D-01 remains open as L4v2-D13: Q3 kernel versus already-issued guide times median/mean cushion, alternatives that are never stacked. A2 is PARTIAL with no established executable edge; B2 FAIL; RNPL unidentified; fee theta unavailable; NCLH no ABNB adjustment; hotel comparator only.

Eighteen tests pass, including 11 interval-rule tests and seven artifact/source-integrity checks. The initial PDF text assertion treated line wrapping as content mismatch; whitespace normalization corrected the test, with the failed log preserved. Both final memo pages and all three appendix pages were visually inspected. Poppler exits 0 with font fallback notices for unused Symbol/ArialUnicode fonts; the rendered pages contain no missing visible text. `receipt.json` records generation-time status; `final_QA.json` records subsequent visual and independent review.

To edit the memo, make a NEW Markdown source and pass `--render-source <path>` with a new run ID; reread every changed claim against the ledger. Review tests target the frozen final review_v2 by default. Do not overwrite final artifacts. The PDF skill marker ran once before first authoring.

## RESUME

Use final review_v2 and model snapshot_v2 with their final QA receipts. Parent integrates local work and owns commits/registrations; no outreach or public push is authorized. On a new source version, verify explicit immutable bindings and same-basis expectations first, then regenerate the financial link, exact two-page memo and unsigned card. Preserve accepted charts with limitations and keep failed-promotion descriptive draws outside the operational envelope. Missing guide expectations, matching FX denominator/hedges, or RNPL identification block those claims only.
