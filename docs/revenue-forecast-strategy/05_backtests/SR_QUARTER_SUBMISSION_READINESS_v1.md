# Quarter submission readiness — 15 September 2026

Codex parent, with source_auditor, chart_auditor and roadmap_auditor. Branch `codex/submission-readiness-v1`. Read-only research and artifact audit; this note and workboard records are new files.

## Verdict

**Ready to start the Excel and visual submission now. Complete one bounded integration and event review before freezing the investment claim. Another broad L-session research campaign is not the prerequisite.**

The user's decision frame is a quarterly Citadel trade centered on the forthcoming forward guide and earnings-event stock reaction. The relevant chain is alternative-data/operating evidence plus top-down conversion, then a forecast of the announcement, a comparable expectation, and a conditional event payoff. An adopted twelve-month valuation or demonstrated post-announcement drift is not a prerequisite for this pre-event argument. It remains necessary to distinguish a pre-event forecast from calculations that use the release's own data.

This assessment does not adopt a short direction, probabilities or a new target. It does not promote an unvalidated input merely because it supports the proposed direction.

## Git and evidence versions

`git pull --ff-only` succeeded on the original `codex/lane2-full` checkout. Its upstream was already current; the fetch advanced `origin/main` and fetched other contributors' branches. A separate checkout at `.worktrees/submission-readiness-v1` holds the latest merged main, avoiding changes to the user's existing checkout and untracked work.

| Component | Reviewed version | Integration standing |
|---|---|---|
| Latest merged main | `2dfe0c2a1852181a246f4b6b9072e05e844d52d5` | Includes PR58 L4, PR59 L3 and PR60 alternative-data work |
| Margin and detailed cost build | `origin/krish/margin-build`, `9a7d7642` | Branch-only; read through Git, not merged into this review branch |
| Nights-short scenario | `origin/jessie/nights-short-q3q4`, `7ed8763b708b7599e421b61f2976bb5a3be6962a` | Branch-only; conditional overlays, not a promoted forecast |
| Quant validation | `4533811d8405403b7f465bda3b69790e4367b2d6` | Outside main by ancestry; available in the quant worktree |

No contributor branch was merged or pushed by this review.

## What already exists

| Work | Reusable deliverable | Remaining submission work |
|---|---|---|
| Top-down conversion and guidance | Fixed seasonal kernel, cushion policy, point-in-time comparisons and L4 integration | Select a coherent operating path and freeze the forecast origin |
| Bottom-up operating evidence | Nights/reviews/calendar/regional/ADR builds and a large alternative-data inventory | Carry the newest evidence classifications; preserve booking-date versus stay-date differences |
| Bottom-up costs | Margin branch's `model/ABNB_margin_line_build.xlsx`, `ABNB_margin_model.xlsx`, cost-item scripts, audit/fix notes and more than 20 PNG charts | Reconcile its revenue, GBV, nights, consensus and financial definitions to the selected L4 case |
| Integrated Excel | `model/lane4_v2/outputs/lane4_model/snapshot_v2/ABNB_L4_review.xlsx` | Make a new submission version with a quarterly event front page and the compatible cost bridge |
| Memo and appendix | Two-page L4 review memo; three-page L3 chart appendix | Rewrite around the quarterly variant view; technical charts become support |
| Event card | Twelve unsigned rules with missing/ambiguous states | Forecast the first-issued announcement, not merely score it after publication |
| Decisions | Thirteen quantified L4 decisions | Resolve the ones affecting this quarter; they are not thirteen new coding projects |

The L4 workbook has eight sheets and nine selectable cases. Its existing audit reports 1,875 formulas, 126 reconciled scenario outputs, and no formula errors or external links. Those are historical validation receipts, not tests rerun by this review. Its September 13 inputs remain a valid frozen snapshot; they are not automatically current after the pull. No final PowerPoint was found under `deck/`.

Sources: `L4_ARTIFACTS_v2.md`, `L4_CLOSE_HANDOFF_v2.md`, `analysis/src/forecast_methods/lane4_model_v2/README.md`; margin branch `docs/margin-build/notes/40_line_build.md` and `docs/margin-build/audit/CODEX_LINE_BUILD_CHECK.md`.

## What the new alternative data changes

The catalogue contains **1,773 candidate sources, 739 reviewed sources and 59 sample manifests (58 nonempty)**. These counts describe research inventory, not independent validated signals.

| New evidence | Scale and measured result | Treatment in the submission |
|---|---|---|
| DoltHub revenue consensus | 1,159 appended observations across 290 weekly snapshots; merged register has 1,330 data rows. Its Street baseline ratios to naive are 1.146 W1 / 0.881 W2. | Useful expectation history; same underlying Zacks source family. Neither independent nights expectations nor observed expectations for management's guide. |
| 2023 reviews archive | 114 markets, about 41.9 million reviews dated 2015 onward, 4.884 GB. Fresh-versus-stale y/y wedge is -9.96pp across 1,357 market-months, failing the preregistered +/-2pp global limit. | Supersedes the older stable-wedge/survivor headline. Descriptive and scenario use remain possible with limitations. |
| Reviews revalidation | Old 0.683 ratio was W2 only, n=10. W1 was 0.837. Updated training gives W2 0.757 honest / 0.841 literal, both above the 0.75 survivor hurdle. | Do not present the old 0.68x result as a current two-window validated forecast. |
| EUROCONTROL flights | 112,520 country-day rows across 40 states. Primary EMEA model: 1.118x naive W1, n=12; 0.816 W2, n=10. Correlation with the already-held passenger series is 0.994. | Corroboration; fails the both-window promotion rule and is largely redundant with existing information. |

Later results supersede the catalogue's earlier integration plan and the September 11 Q3-nowcast synthesis. Failed tests are useful evidence: they tell us which claims the visual submission must remove or qualify.

Sources: `research/notes/github_altdata/CATALOG_SUMMARY.md`, `docs/revenue-forecast-strategy/05_backtests/WPK_reviews-index-2023-vintage.md`, `C2_eurocontrol-daio.md`, `G1b_dolthub_consensus_history.md`, and current L0 CSV.

## The remaining bounded integration pass

| Priority | Necessary action | Acceptance before final freeze |
|---|---|---|
| 1 | Define one forecast origin, earnings catalyst and exit window. Verify the issuer's actual event date before calendarizing. | Every input was available by the stated freeze; later observations are visibly separated. |
| 2 | Select one coherent Q3 units/ADR/GBV/revenue block and one Q4 conversion/cushion policy. Preserve the competing build as a comparison. | GBV identity, units and quarterly lags reconcile; no arbitrary averaging of correlated models or duplicated RNPL adjustment. |
| 3 | Bind the reviewed bottom-up cost build to that operating block. | Quarterly revenue, variable costs, EBITDA/addbacks, SBC and interest definitions tie; discretionary spending assumptions remain visible. |
| 4 | Explicitly select consensus vendor, target, role and timestamp. | New results cannot change because a default vendor selection changed. The output distinguishes revenue consensus, direct guide expectations and an assumed/implied guide benchmark. |
| 5 | Create one event card and conditional payoff view. | Each forecast, comparison and price scenario refers to the same information timing and target. Negative-surprise and opposing cases have observable conditions. |
| 6 | Recalculate and review the new workbook/memo/figures. | Selected-case formulas, forecast-to-consensus comparisons and cost tie-outs pass; rendered outputs carry current evidence labels and no stale survivor claims. |

Two concrete plumbing issues require scope control. PR60 changes unfiltered `l0.pit_consensus(..., vendor=None)` selections; choose vendor explicitly. The frozen harness spine expects `as_of`, while L0 provides `as_of_timestamp`, so that path falls back to a current-consensus file. This mismatch was independently confirmed by reading the function and current CSV schema. **L4 v2 already reads `as_of_timestamp` explicitly**, so the legacy issue does not block all workbook work. If the submission needs the old spine path, implement an additive adapter; do not edit the frozen harness.

A narrowly specified re-evaluation with new revenue-consensus vintages is useful if the memo claims an expectations/revisions edge. It is not a prerequisite to building the workbook. Preserve the distinction between a revenue-consensus comparison and a guide-expectations comparison. If direct guide expectations cannot be obtained, a transparently derived implied benchmark can support a conditional scenario, but it must not be labeled observed market guide consensus.

## The four separate forecast objects

| Object | Purpose |
|---|---|
| Q3 reported units and GBV | Pre-event operating forecast; input to the following-quarter revenue bridge |
| Q4 nights-guidance wording/interval | Prediction of what management will say about forward booked-unit growth |
| Q4 revenue-guidance range/midpoint | Prediction through conversion and the guidance cushion |
| Quarterly/FY margin wording | Bottom-up cost and spending constraint that may offset or amplify the growth message |

The new nights-short branch's 8.86% Q3 / 7.23% Q4 values forecast reported booked-unit growth under assumptions. They are not independently validated forecasts of management's wording. The World Cup overlay lacks a demonstrated dated cohort bridge and stays a stress. That branch also prefers the later February guide as its catalyst; do not silently substitute it for the chosen quarterly event.

Under the retained kernel, Q3 booked GBV feeds Q4 revenue; Q4 booked GBV feeds subsequent revenue. Do not mechanically make Q4 nights guidance determine Q4 recognized revenue.

## What the event evidence permits

L2 A2's 7/8 and 6/7 sign agreement uses information released with the guide. It is not pre-event forecasting skill. Quant validation's earlier-origin candidate failed its promotion rule: guide RMSE 63.445/63.696 million versus the guide-growth benchmark 74.331/60.834 million, matched n=12/10. The archived event study does not establish an isolated forward nights-guide-surprise effect.

These limitations restrict claims of a statistically validated trading edge. They do not prevent a clearly conditional, analyst-underwritten catalyst pitch. A pre-event position can seek the announcement gap; failure to establish drift from the following open is a different strategy result. Use historical analogues with their sample sizes and counterexamples, not an assumed deterministic guide-to-price coefficient.

## Visual and workbook production

Use existing L4 schedules and bottom-up assets as the foundation. The new front page should show one forecast freeze, the four forecast objects, matching expectations and event conditions. Keep inputs and scenario judgments editable and traceable.

Recommended working exhibits:

1. Two approaches converging on the same announcement, with shared inputs identified.
2. Q3 GBV to Q4 revenue to Q4 guide waterfall; cushion visibly separate.
3. Own forecast versus matched expectations, with guide and revenue in separate panels.
4. Bottom-up quarterly cost waterfall, separating evidence-only costs from the management-budget reconciliation.
5. RNPL lap and cancellation scenarios with timing and overlap stated.
6. Event outcome matrix: weaker, in-line and stronger guidance; price outcomes conditional, not estimated causal responses.
7. Backup evidence: alternative-data coverage/failures and the existing L3 validation charts.

Select the strongest one or two exhibits for the two-page memo; keep the fuller visual analysis as supporting material. Official competition rules/rubric are not present in `docs/competition/README.md`; verify the actual submission requirements before final layout lock.

## Work to defer

No new free-weight search, cruise/OTA transfer, broad alternative-data search, causal RNPL or FX identification programme, or exhaustive FY2027/28 re-underwriting is required to start production. New admissible data may justify targeted updates; repeatedly fitting the same small event sample does not replace missing expectations.

## Commands, checks and limits

- `git pull --ff-only`: initial sandbox metadata denial; authorized elevated retry succeeded, exit 0.
- `git worktree add -b codex/submission-readiness-v1 .worktrees/submission-readiness-v1 origin/main`: initial checkout rolled back on a Windows path-length error.
- `git -c core.longpaths=true worktree add .worktrees/submission-readiness-v1 codex/submission-readiness-v1`: succeeded, exit 0.
- `git log`, `git show`, `git diff --name-only`, `rg`, and PowerShell file reads: scoped source/version inspection. An initial search used the wrong spine path; the exact `analysis/src/forecast_methods/harness/spine.py` was then inspected.
- PowerShell `Import-Csv` check: 1,330 total rows; 1,159 DoltHub rows; `as_of` absent; `as_of_timestamp` present.
- No new statistical fits, research tests, forecast registrations, scorer runs or spreadsheet recalculation. New parameter count: 0. Existing test receipts are described as existing receipts.

## RESUME

Begin a new additive submission integration version from main 2dfe0c2a, bind the reviewed margin branch and quant/L3 handoffs, select the event and coherent operating inputs, and make vendor selection explicit. Build the guidance-first Excel front page and charts concurrently with those narrow tie-outs. Preserve failed alternative-data findings, scenario-only RNPL overlays, and missing guide-expectation states. Finish by recalculating and reviewing the delivered files, then sign the quarterly thesis and event scenarios; do not reopen broad model discovery solely because the direction is not yet adopted.
