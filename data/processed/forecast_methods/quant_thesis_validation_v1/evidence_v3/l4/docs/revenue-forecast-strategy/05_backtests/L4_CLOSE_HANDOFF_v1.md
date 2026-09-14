# L4 close and manual handoff

13 September 2026 · `codex/lane4-full` · starting evidence commit `1c87628cedbc94ab8a0e8552743c94485ef353b8`. The user confirmed that this task owns L4; the separate “Complete and audit L3” task owns conversion estimation and validation. Three subagents handled revenue reconciliation, the financial workbook, and evidence/memo production; a different package owner independently reviewed the workbook and memo. Parent owns registration, source preservation and final integration review.

## Completion and limits

**The baseline L4 review package is complete. L3 integration and investment adoption remain pending.** No L3 input bundle has been accepted. Fixed 2/3 conversion is preserved as the provisional benchmark; no new conversion fit ran here. FX/RNPL estimates remain unavailable, separately from the conversion-method decision. The user can manually bring the accepted L3 version/commit and checksums to this task for a new integration version.

The short-lived conversion steering produced only a read-only sample/method scoping note: `L4_CONVERSION_SCOPING_HANDOFF_TO_L3_v1.md` in this folder. It locates the 22 lag-complete quarters and records methodological cautions. It contains no fitted weight, new conversion-rate estimates, validation result or pre-registered L3 research claim. No message was sent to the separate task or teammates.

## Review artifacts

Paths are relative to the isolated L4 worktree root. Earlier outputs and failures remain preserved; these explicit versions are the delivery set.

| Artifact | Final path |
|---|---|
| Revenue/guide, operating inputs, sensitivities, attribution and source ledger | `data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1/` |
| Linked, recalculated eight-tab workbook | `model/lane4_v1/outputs/lane4_model/snapshot_v4/ABNB_L4_review.xlsx` |
| Independent model calculations and seven-case outputs | `data/processed/forecast_methods/lane4_model_v1/snapshot_v4/` |
| Exactly two-page review PDF and editable Markdown | `deck/drafts/lane4_v1/review_v4/review_memo.pdf` and `review_memo.md` |
| Unsigned November card | `deck/drafts/lane4_v1/review_v4/unsigned_november_card.md` plus CSV/JSON |
| Quantified open decisions | `deck/drafts/lane4_v1/review_v4/decision_register.md` plus CSV |
| Combined source/assumption ledger | `deck/drafts/lane4_v1/review_v4/source_assumption_ledger.csv` |
| Independent economic/content review | `L4_INDEPENDENT_REVIEW_v1.md` in this folder |
| Final scorer, hash and test receipt | `data/processed/forecast_methods/lane4_control_v1/close/receipt.json` |

The workbook's selected case recalculates through one linked build. The comparison columns are explicitly saved captures; a visible stale-input warning and documented `build.mjs --refresh` command recapture them after edits. The supplied workbook and its saved-file recapture both pass independent OOXML checks. Do not substitute a development or recapture-test workbook for the final artifact above.

## Exact claims supported by this package

All current scenario rows below are deterministic conditional calculations, n=1 per quarter, W1/W2 n=0. They are neither probability intervals nor newly validated forecasts.

| Claim | Defensible number and interpretation |
|---|---|
| Operating review | 146.8m Q3 nights × $177.17 ADR = $26,008.556m GBV. Fixed K0 conversion produces Q4 revenue $3,179.343654m and guide $3,123.419115m using the 1.790491031% trailing-eight median cushion. |
| Captured expectations comparator | The guide is $37.602375m / 1.189564% below Yahoo/LSEG-family revenue consensus of $3,161.021490m, observed 13 September at 15:20 UTC. This is revenue consensus, not an explicit management-guide consensus or established expectations edge. |
| Old guide reconciliation | $3,059.403011m → $3,158.227962m: GBV +$32.580444m, lambda +$2.717883m, cushion +$63.526624m, in that order. Unexplained residual is below $0.001m. |
| Cushion uncertainty | On the same review revenue, mean cushion yields $3,121.387508m guide; inherited 3.88% Q4 cushion yields $3,060.592659m. These are estimator/assumption comparisons, not confidence bounds. |
| Kernel timing | Q3 nights affect Q4 revenue; Q4 nights first affect Q1 2027. Q4 review USD contribution weights are 65.6640% / 34.3360%, rather than mechanically 2/3 / 1/3. They are model contribution weights, not measured booking-to-recognition shares. |
| Conditional financial value | At the inherited 16.5× multiple, FY27 EBITDA $5,807.532522m, net cash $10,282.596149m and ending diluted-share proxy 574.598178m produce $184.662755/share at 31 December 2027. Longer-horizon growth/cost/cash/share inputs are inherited assumptions; this is not an adopted target. |
| Illustrative revenue sensitivity | Net after-hedge consolidated revenue ±1% in covered Q3/Q4 2026 and Q1 2027, with disclosed later-base propagation, gives $180.893822–188.431688/share. It is not a measured FX/RNPL sensitivity coefficient or probability range. |
| Legacy valuation reconciliation | $180.876286 EBITDA lens and $156.786845 six-lens mean reproduce within $0.001/share. They use distinct valuation calculations and do not imply an adopted target. |

A2 remains PARTIAL without an established executable trading edge; B2 failed its revision-mechanism hurdle. ADRv3's n=10/9 dollar-target windows are distinct from main n=14/10 windows and its rule was selected after earlier analysis. RNPL migration and revenue-cohort shares remain unidentified. None of those findings is improved by a successful accounting or spreadsheet test. No withdrawn +0.48 causal growth-to-multiple claim, trade direction, scenario probability or signed November card is adopted.

## Validation completed

- Both actual, unchanged harness scorers ran after the final registration: 4,232 registry rows across 76 objects, 284 historical score rows. All 284 completed L2 rows match exactly, including keys, labels and missingness; maximum numerical drift is zero. The two scorers match each other exactly.
- All 3,911 starting tracked files and all 135 files in the explicit read-only external FX bundle remain byte-identical. No changing L3 worktree research was consumed.
- Existing test suites: 47 frozen-harness, 37 FORMAT 1.1, eight return and 63 kernel tests, all passed (155 total).
- New package suites: 36 revenue/adapter, seven model and 16 card/review tests, all passed (59 total). These are implementation tests, not 59 empirical forecast observations.
- Parent independently reconstructed all 15 revenue rows, verified 17 source hashes and found maximum revenue difference 8.19×10⁻¹² USDm. All 13 revenue CSVs separately rebuilt byte-identically.
- Final exported workbook: 1,576 formulas, zero error cells, zero external links, 91 independent cached-value checks, maximum difference 0.000007376 in stated output units, below the $0.001 tolerance. Saved-workbook recapture passes the same checks. Owner also tested 84 scenario output ties, perturbations, timing and stale captures.
- Both final memo pages were visually inspected: exactly two pages, 10.5pt body, readable tables and no clipping. Final review_v4 page images are byte-identical to the parent-approved review_v3 images; only card C05's prior-year blended-ADR wording changed. Independent accounting/content review found no quantitative blocker; its two wording suggestions were addressed.

The 14 newly registered LIVE rows comprise four scenario objects under `l4-review-v1`. The unchanged Q3 result, K0 comparison, duplicate Q4 nights case, and unavailable FX estimates were not registered as new information. All rows use the actual 13 September date. They have no historical performance claim or calibrated distribution.

## Failures and operational limits retained

The revenue and workbook development failures are described in their package notes and preserved in their output directories. Parent's attempted single pytest call across all packages failed during collection because the repository venv lacks ReportLab; `test_collection_failure_01.json` records it. The corrected commands use the repository venv for 43 revenue/model tests and bundled Python's unittest for 16 review tests, both exit 0. A dependency probe also confirmed bundled Python does not include pytest, so it was not used for that aggregate command.

Workbook build and saved-workbook recapture exit 0. The Windows PNG renderer writes complete, visually inspected images but exits 1 during teardown; this operational issue remains documented, not recast as a passing render command. Native desktop Excel recalculation was not tested. Numerical workbook export and independent cached-formula validation passed. Neither limitation is concealed by the polished review PDF.

## Reproduction

From this worktree root, use explicit runtime paths and fresh output names. These commands rebuild the frozen September 13 research inputs; they do not refresh market data or register a new vintage.

```powershell
$l4ResearchPython = 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe'
$l4ArtifactPython = 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $l4ResearchPython -X utf8 analysis/src/forecast_methods/lane4_revenue_v1/run.py --output data/processed/forecast_methods/lane4_revenue_v1/reproduce_01
& $l4ArtifactPython -X utf8 analysis/src/forecast_methods/lane4_model_v1/run.py --revenue-dir data/processed/forecast_methods/lane4_revenue_v1/reproduce_01 --run-id reproduce_01
& $l4ArtifactPython -X utf8 analysis/src/forecast_methods/lane4_review_v1/run.py --revenue-dir data/processed/forecast_methods/lane4_revenue_v1/reproduce_01 --model-dir data/processed/forecast_methods/lane4_model_v1/reproduce_01 --run-id reproduce_01
& $l4ResearchPython -X utf8 -m pytest analysis/src/forecast_methods/lane4_revenue_v1/tests analysis/src/forecast_methods/lane4_model_v1/test_model.py -q
& $l4ArtifactPython -X utf8 -m unittest discover -s analysis/src/forecast_methods/lane4_review_v1/tests -v
& $l4ResearchPython -X utf8 analysis/src/forecast_methods/lane4_control_v1/run.py verify --snapshot reproduce_01 --tests
```

The artifact runtime's package-local ignored Node-module junction must exist as documented in the model README. Package READMEs include render, input-edit/recapture and independent export-review commands. Existing run names are deliberately refused. Do not rerun `register.py --register` on published method/object names.

Scoped new `.gitattributes` files disable newline rewriting only for new L4 packages, notes and registry objects so Git preserves their recorded SHA-256 bytes. The root attributes and all completed research files remain unchanged. Earlier-lane source hashes describe their verified Windows checkout bytes; a different platform must honor those original line endings or obtain the exact source snapshot before claiming a byte-identical reproduction.

The initial pre-publication index audit caught newline normalization, repaired through scoped attributes and explicit re-indexing. `staging_failure_01.json` preserves the failure and `staging_review_final.json` records zero byte mismatches, no pre-existing edits or prohibited files, and a passing whitespace check. No analytical value changed during this repair.

## RESUME

Review the final artifact versions above and the separate independent-review note. The current work is a baseline review package, not completed L3 research or an adopted investment. Accept L3 only through a user-provided immutable version/commit and checksums, verify the actual committed file contents, and consume matched conversion parameters together. Review FX/RNPL reference bases, denominator bridge, recognition hypothesis and baseline hedge treatment separately; apply an accepted adjustment once in a new version. Then rerun affected financial/memo calculations, source checks, any new current-date registrations and both scorers. Preserve this baseline, the conversion-scoping handoff, all completed prior lanes and the external FX bundle. No automatic merge or teammate outreach.
