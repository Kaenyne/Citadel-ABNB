# Churn and hotel research: code and model-use audit

**Disposition: suitable for shared research, diagnostics, and explicit sensitivities after the corrections below. No new direct guidance coefficient or revenue overlay is approved by this review.** The work improves the questions and bounds used in the existing models; it does not establish causal fee-related churn, hotel bookings, or incremental hotel revenue.

The [file register](2026-09-07_churn-hotel-code-register.csv) covers every Python file added by this release: **30 source modules and 13 test modules**. Each entry records its purpose, approved use, overlap rule, audit disposition, and SHA-256 with Git newlines normalized. This is a code/read/replay review, not an independent certification of the underlying publications.

## Where the work belongs in the models

| Existing work | Useful contribution from this release | Boundary that prevents double counting |
|---|---|---|
| [`overnight/13_driver_model.py`](../src/overnight/13_driver_model.py) | Challenge regional nights, hotel mix, realized economics, and recapture assumptions | Its core nights already include Hotels and Experiences. Only Services and ads enter its separate new-business increment. Do not add `hotel_mix_scenarios.csv` revenue on top of core revenue. |
| [`overnight/11_competition_supply_overlays.py`](../src/overnight/11_competition_supply_overlays.py) | Test the hotel activation and productivity needed to support its assumed business path | Its hotel base, ADR, fee and growth inputs are assumptions. This release's scenarios reuse some of those assumptions; they are not corroborating measurements. Reconcile one scenario and one baseline before changing the driver model. |
| [`overnight/02_guidance_analysis.py`](../src/overnight/02_guidance_analysis.py) and [`predictive/03_nowcast_tests.py`](../src/predictive/03_nowcast_tests.py) | Supply diagnostics and falsifiable hypotheses for later forecast evaluation | Keep the existing guidance-error baseline. The new retrospective archive uses later observations to establish presence and confirmation. It is not a point-in-time historical predictor. Any later experiment needs as-of availability, forecast-horizon alignment, held-out errors and comparison with the current baseline. |
| [`inside_airbnb_supply_panel.py`](../src/inside_airbnb_supply_panel.py) and the [regulatory matched-cohort study](../../research/regulatory/phase2/README.md) | Persistent-ID and source-coverage diagnostics, plus distinctions among license, listing and physical-property identities | These studies reuse Inside Airbnb observations. Broad disappearance already includes regulatory and other exits. Do not add the same lost listings again as a fee-loss or regulatory-loss factor. Lost booked value, incremental exposure, timing and internal recapture remain separate unobserved quantities. |
| New visible guidance and nights branches | Reuse their model and expectation framework when testing a future signal | `krish/earnings-guidance-regressions` adds guidance/reaction regressions; `krish/nights-driver-followups` adds choice-based nights and party-size work. This release does not fork those models or reinterpret competitor hotel demand as Airbnb hotel bookings. |
| New visible `krish/blotnick-bridge` branch | Use its existing Q4/FY27 decomposition to locate a future proposed adjustment | `overnight/29_q4_fy27_bridge.py` already combines regional nights, ADR, the take-rate/timing residual and FX. The new supply studies do not validate another growth adjustment or duplicate that bridge. |
| New visible fee-elasticity branch | Keep the new observed churn diagnostics separate from modeled guest price response | `krish/unpack-delivery-notes:analysis/src/fee_split_elasticity_model.py` models price, demand, fee incidence and payout. Its illustrative old guest fee is 14%; this dated study uses 15%. Both are assumptions. Do not stack their fee/take-rate or demand effects with this study's scenarios. Align inputs and the affected population first; retain this study's three arithmetic examples only to reproduce its memo. |

Hotel supply follows a required bridge: eligible properties to actual activation, allocated rooms, completed room nights, recognized platform revenue, and incremental contribution after promotions and displacement. A registry room count supplies only one denominator. Credits affect contribution and potentially future periods; they are not automatically same-quarter revenue deductions. Revenue must also be reconciled with what management guidance and the existing forecast already include.

## Corrections made before publication

| Finding | Correction and observed effect |
|---|---|
| Pilot license matching could assign another existing baseline listing as a replacement | Restricted replacements to IDs absent from the baseline. In San Diego's all-listing pilot, candidate replacements fall from 221 to 220; the source-flags linked 90-day count rises from 1,945 to 1,946. The conservative pending count rises from 1,765 to 1,766; its confirmed count remains 1,049. The reviewed short-stay-home cohort and fixed 20-case manual sample are unchanged. The affected summary and note were regenerated/corrected. |
| Invalid numeric values could be accepted or silently truncated | Reject fractional/negative/nonfinite counts, booleans masquerading as counts or assumptions, invalid observation states and persistence days, and impossible fee/room/scenario inputs. Zero promotional exposure has no break-even redemption threshold. |
| Equal manifest lengths did not prove the requested market/date set was acquired | Require exact unique identities. A later failed compact source cannot shadow a successful capture. Duplicate comparison identities raise an error instead of silently replacing a row. |
| Some output and cache writes could destroy the previously reviewed file on failure or rerun | CSV serialization validates before atomic replacement where hardened; unchanged compact captures retain their original bytes. Changed cached evidence is refused. Pilot sample identity and manually reviewed identity fields cannot be silently replaced. This does not make an entire multi-file research run transactional; use a separate output directory/worktree for new observations. |
| Checks implemented with `assert` disappeared under optimized Python | Replaced critical hotel verifier, stock-flow and recent-report assertions with explicit errors. The 13-market verifier was also run with `python -O`. |
| Dated report text could be regenerated against changed data while retaining old claims | Added [frozen input guards](../config/churn_hotel_report_inputs.json) to four reports and the selected-market assembler. A changed evidence bundle requires review of the narrative before regeneration. Hashes normalize CRLF/LF so a Git checkout does not create false drift. |
| Overlap collector could change its frozen evidence or lose URL distinctions | Verify Git blobs, reject truncated trees, preserve changed cache files for review, retain URL path case, and discover GitHub CLI on PATH with a Windows fallback. |
| A useful authored data request was hidden by the repository's vendor-name ignore rule | Published it as [`hotel_channel_and_consensus_request.md`](../../data/requests/hotel_channel_and_consensus_request.md) and corrected links. It is a request/schema explanation, not a licensed export. |

The new regression module contains 12 tests for the audited failure cases. The final suite has 110 passing tests. Numerical scenario results remain unchanged; the fee scenario interpretation now states the correct relative take-rate units and supplied horizon/margin assumptions.

## Evidence reuse and scope

The historical 13-market and archive 25-market hotel comparisons have 76 capture references to 64 unique hashes. They are separate sensitivity views, not 76 independent observations. The selected 13-market extension contains 113 previously collected Airbnb pages, clustered into 111 property identities; its 26 accepted Paris room-count links represent 1,060 registered rooms already present in the earlier crosswalk. None establishes Airbnb allocation, bookings, revenue or current verified independent-room totals. Missing outcomes remain missing, and mixed units, vintages and geographic boundaries are never summed into a TAM.

The frozen expanded source audit flags 13 exact team-URL matches among 253 source records. The extension flags six among 201 URL-bearing records. Different URLs, translations, newer publications and repeated management claims do not establish independent evidence. Legacy overlap/probe scripts remain only because they explain and reproduce the dated studies; the expanded collector and selected 13-market table are the entry points for this release's evidence inventory and selected scope.

The release also checks the live GitHub branch inventory. New regulatory work was merged into `main` during the review, advancing the base from `3de6ec7` to `90c826b`; the review branch incorporates it. New guidance, choice/nights and fee-elasticity branches were inspected for overlapping purpose. The older hotel source-audit cutoffs in the research tables remain accurately frozen at their recorded commits; this release review does not relabel them as newly collected evidence. Private/unshared work remains outside the overlap check.

## Verification and preservation

The [validation record](2026-09-07_churn-hotel-validation.json) records the actual reconciliations, file checks and inspected remote refs. Validation includes:

- 110 passing unit tests, including identity, coverage, date boundaries, stock-flow, invalid inputs, scenario arithmetic and output-preservation regressions.
- Full broad-panel replay from 478 captures and fee-history replay from 692 captures; all 9,120 fee interval rows reconcile. These capture counts overlap and must not be added together.
- Pilot, team-panel, recent/winter, manual-evidence, hotel-tag and selected-market replays; scenario/aggregate recalculation; four official spreadsheet anchors; 89 expanded and 204 extension source path/hash checks. Source hashes prove artifact integrity, not publication truth.
- All five dated memo texts reproduced in isolated output storage. Four charts were visually checked. Each published Python file was parsed and inspected; CSV schemas/row widths and JSON syntax were checked, along with common credential patterns and file sizes.
- Every existing `main` file is preserved byte-for-byte at the Git-blob level except four README files with additive documentation. Both sides of README merge conflicts were retained. No model, workbook, teammate code, or existing data output is replaced by this release.

Your original workspace is preserved. The initial work was checkpointed locally, and the subsequent hotel extension was copied into the isolated review worktree before being audited. Corrections were made in that review worktree. The original files are compared with their captured hashes; raw replays write only into separate audit output folders. Publishing uses a new branch and draft PR, with no force push, deletion, direct `main` push or merge into `main`.

## Reproduction limits and next model decision

Use Python 3.11 or newer (reviewed on 3.13), repository requirements, and Git/GitHub CLI for the acquisition scripts. Run the regression suite with:

```powershell
python -m unittest discover -s analysis/tests -v
python -O analysis/src/verify_hotel_13_market_panel.py --raw-root PATH_TO_PRESERVED_CHECKOUT
```

Raw listing captures, public-source extraction bundles and some earlier acquisition helpers remain under ignored `data/raw/` storage. A fresh clone alone cannot reproduce the full source acquisition/extraction; it needs those dated bundles. The published ledgers retain source paths and checksums, and the processed tables and scenario assumptions are inspectable without the bundles. Live registries and archive endpoints may change or disappear. No new download was substituted for an old observation during verification.

Before a forecast change, obtain a point-in-time production measure with reliable exposure, hotel/home classification and realized economics; test whether it improves the existing guidance/revenue model out of sample. Until then, use these outputs to reject unsupported assumptions, choose sensible sensitivities and define the missing data request. Passing code tests does not establish predictive usefulness or causality.
