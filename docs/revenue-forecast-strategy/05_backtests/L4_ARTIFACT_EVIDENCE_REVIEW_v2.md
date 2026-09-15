# L4 artifact evidence review v2

Independent reviewer: source worker / committed_evidence_audit · 14 September
2026 · `codex/lane4-full`. This is the rotated review of the artifact worker's
model/memo, not self-approval of the reviewer's source package. No artifact,
model, forecast, source or registry was changed by this review.

## Verdict

**PASS on source claims and economic/numerical consistency. Both minor wording
findings are closed in final `review_v2` / model `snapshot_v2`; no unresolved
financial or source-accounting blocker remains.** The candidate distinguishes completed
conversion validation from failed free-weight promotion and keeps the existing
operational K0 policy. Its expectations comparison uses revenue versus revenue;
explicit management-guide expectations remain unavailable. FX research
acceptance is correctly separated from current financial ineligibility.

Exact reviewed candidate:

- `data/processed/forecast_methods/lane4_model_v2/snapshot_v1/` and
  `model/lane4_v2/outputs/lane4_model/snapshot_v1/ABNB_L4_review.xlsx`.
- `deck/drafts/lane4_v2/review_v1/`: memo Markdown/PDF, unsigned card,
  decisions, source ledger, financial/expectations/descriptive tables and
  accepted L3 exhibits.
- `data/processed/forecast_methods/lane4_review_v2/review_v1/`: receipt,
  input manifest and frozen input copies.

The parent separately checked the workbook's exported OOXML (1,875 formulas,
zero formula errors, zero external links and 316 checks). This reviewer did not
repeat that scan or assert independent visual approval; parent/author own the
final page and workbook visual inspections.

## Findings sent to author and parent

| ID | Severity | Location | Requested correction |
|---|---|---|---|
| AE-01 | Minor claim precision | Memo final evidence paragraph; decision D08 status | Say "no established executable edge" instead of "no executable edge". A2 failed to demonstrate the edge; this is not proof that an edge cannot exist. |
| AE-02 | Minor attribution | Decision L4v2-D10 period/source cell | Replace "Lane1 corrected F evidence" with "Committed Lane2 F evidence". Authoritative `ALPHA_F_RNPL.md` is Lane2. |

Both corrections are wording-only and do not alter accepted source values,
thresholds, scenarios, accounting or valuation. The final closure below records
the repaired frozen version; the original candidate and initial review remain
preserved.

## Independent checks

Checks used Python standard-library CSV/JSON/hash arithmetic from the L4 root,
without importing or executing the artifact/model calculation functions.
Immutable evidence and independent check rows are saved under
`data/processed/forecast_methods/lane4_sources_v2/artifact_review_v3/` as
`receipt.json`, `checked_hashes.csv` and `numeric_checks.csv`.

| Check | n | Result |
|---|---:|---|
| Artifact/input/chart hash identities | 82 | PASS; unchanged at end of read |
| Review manifest records | 29 | Original inputs and corresponding frozen copies verified |
| Original L3 disposition rows | 1,187 | All fields preserved within the 1,367-row artifact ledger |
| Accepted conversion chart PNG/SVG files | 6 | Byte-identical to accepted bundle |
| Financial/expectations/parameter identities | 319 | PASS; maximum absolute numerical difference 5.912e-12 |
| Financial scenarios | 9 | Each September/December valuation and annual cash/share bridge checked |
| Scenario/year financial rows | 27 | FCF, FCF-less-SBC, operating-income, cash and share identities checked |
| Descriptive joint-parameter rows | 9 | Six rows preserve draws 706/542; three preserve the all22 point |

The 319 checks cover the calendar fraction, horizon cash/shares, enterprise and
equity values, per-share values and date-only differences; annual FCF,
SBC-adjusted FCF, operating-income proxy and cash/share bridges; all 15
vendor/scenario expectations rows; and every coefficient in the nine displayed
descriptive parameter tuples. Dollar/share tolerance was 0.001, while identical
source coefficient comparisons used 1e-10 or tighter. These are arithmetic
tolerances, not economic precision or uncertainty claims.

Two preliminary reviewer reads stopped on schema assumptions: chart snapshot
paths are root-relative whereas numerical copies are review-relative; the
descriptive extrema file also contains explicitly labelled all22 point rows
with no bootstrap draw ID. The completed check resolved exactly one existing
hashed path per record and read those point coefficients from `parameters.csv`.
Neither stop identified an artifact defect or caused a source edit.

## Economic and evidence conclusions

The reference Q4 revenue is USD3,179.343654286m, versus captured Yahoo/LSEG-family
revenue USD3,161.021490m at 13 September 2026 15:20 UTC. The same-basis gap is
+USD18.322164286m (+0.579628%). The USD3,123.419115173m own guide assumes a
1.790491031% trailing-eight median cushion. Its -USD37.602374827m comparison with
revenue consensus is explicitly a different-object diagnostic. The
USD3,105.419237090m hypothetical Street guide assumes the same cushion and is
not labelled observed guide expectations. Separate S&P and Zacks families and
their dates remain in the data table; no relay is counted as independent.

The accepted L3 full22 model and W1/W2 result are attributed correctly. Free/fixed
matched-OLS RMSE is 1.165407/1.015513 at n=14/10; both fail promotion. The memo
distinguishes that comparator from K0's existing seasonal estimator. It retains
the nested windows, letter-close information, unprinted-Q3-GBV and cushion
uncertainty, and the difference between reduced-form weights and actual booking
cohort probabilities. Descriptive joint extremes preserve intact source tuples;
they are excluded from production and labelled neither prediction bands nor
confidence intervals.

Soft/reference/firm are coherent assumed envelopes, with no invented
probabilities. The separate +/-1% sensitivities are net after-hedge revenue
sensitivities on Q3/Q4 2026 and Q1 2027 with later-base propagation; they are not
called identified FX effects or combined with the conversion stresses.

The September reference independently reproduces USD182.867016317/share using
16.5x full FY27 EBITDA, USD10,029.055795274m net cash and 578.854210747m diluted
share proxy. The 13 September 2027 fraction is exactly 256/365 of FY27 net flows
from FY26 end, explicitly assumed uniform within year. The later December
comparison is USD184.662755253/share; the USD1.795738935 difference changes balance
timing only. Neither is an adopted target. No current-price return claim or
unvalidated +0.48 growth-to-multiple mechanism appears.

FCF deducts cash taxes and capex and includes the stated net-interest,
unearned-fee and working-capital assumptions. FCF-less-SBC is kept separate;
operating income subtracts SBC and total EBITDA addbacks once, with no second
D&A deduction. The zero unearned-fee change is identified as an inherited model
assumption, not a measured RNPL effect. The inherited USD181.94 repurchase-price
anchor is dated and is not used as a return denominator.

The memo/card retain the missing pre-hedge/H/H_new and recognition-cohort inputs,
Q3-only source FX coverage and no Q4/Q1 extrapolation. Incremental FX is null,
not measured zero. Fee theta is unavailable at 0/6 frozen scheduled captures;
NCLH transfer FAIL adds nothing to ABNB; hotel observations remain comparators.
The card's reported blended ADR is not called composition-controlled pricing,
and its RSS scenario band is not a calibrated prediction interval.

A2/B2 conclusions and the proposed F conjunction remain unsigned. Card lambda
uses the exact USD27,866.666666667m denominator, warning 17.09% and escalation
16.93%, with whole-million revenue intervals. The proposed F condition requires
all three components, including UF-minus-GBV growth strictly above -8pp and exact
management wording. Missing information is ABSENT; no test automatically trades
or validates the opposite thesis. Funds-payable growth is a neutral comparison
requiring accounting reconciliation, not proof that deferral is on schedule.

## Final narrow closure — review_v2 / snapshot_v2

The final artifacts are `deck/drafts/lane4_v2/review_v2/`, bound to
`data/processed/forecast_methods/lane4_model_v2/snapshot_v2/` and workbook
`model/lane4_v2/outputs/lane4_model/snapshot_v2/ABNB_L4_review.xlsx`.
AE-01 now says "no established executable edge" in memo and decision D08.
AE-02 now attributes the corrected F evidence to Lane2. **Both closed.**

The narrow final verification passed 90 checksum comparisons and recorded the
final workbook identity (91 records total), covering 31 source-manifest records,
their snapshots, final artifacts and the six exact accepted chart files. The
1,187 source rows remain unchanged in the expanded 1,767-row ledger. The four
financial files `annual.csv`, `scenario_summary.csv`, `valuation.csv` and
`horizon.json` are byte-identical to the independently checked model snapshot_v1,
so the 319 prior arithmetic/source-parameter checks remain applicable without
another broad test run. Parent separately repeated its OOXML check.

Added memo guide values match the unchanged soft/reference/firm scenario rows.
The new sentence correctly limits a cushion-only change to guide, with no
change to revenue, earnings or cash. Decision D13 preserves the original team
D-01 alternatives: kernel USD4,808.362929m versus issued-guide/cushion median
USD4,814.690226m (+USD6.327296m) and mean USD4,817.823947m (+USD9.461017m).
These remain unsigned replacements rather than additions to the kernel.

Final identities:

| Artifact | SHA256 |
|---|---|
| Memo Markdown | `f7603c8eefe56a2396c56258a946e5e79803eed07729d60391e2cd882739d0ab` |
| Two-page memo PDF | `53e102eeca2dcda418368924cacb9a28486f3274332ba0b06fc804a6b1fe0187` |
| Unsigned card Markdown | `beda7d4ee84f3c3ee824193bf6c5a526435a3dc890b8cb4fa9974b4a26c1a821` |
| Decisions CSV | `e353b7250c925c3aa46767a8efde368a17f949a333745c8603af518d85fbf69f` |
| Expanded source ledger | `ed17a52d3ab1f2de68d8aed3f372c50b95215f0e84132fc442ef5e78658f6bab` |
| Accepted L3 exhibit PDF | `da5636822a00075e9692adb8adb602d4b503525393f0765ac71bdfc3942a6db3` |
| Final workbook | `882b6d7b321d2f791fecc9b1d7ec57265b5e2fdcedd705326ee7bd3ee9ce6f92` |

Final narrow receipt and all checked file hashes:
`data/processed/forecast_methods/lane4_sources_v2/artifact_review_final_v1/`.
No source, financial value or statistical model was changed or re-estimated.

## Review limits and RESUME

This review checks the candidate's source claims and identities, not whether its
inherited cost, multiple, buyback or uniform-timing assumptions are economically
optimal. It does not repeat L3 statistical estimation, independently re-extract
public filings, endorse source-package implementation, sign investment choices
or certify the final visual layout. The final source/economic claim review is
closed on `review_v2` / model `snapshot_v2`. Parent should retain the original
candidate, this review, the final narrow receipts and the separate visual/OOXML
reviews when completing local integration. Any later content or numerical
change requires an appropriately scoped fresh review; investment choices remain
unsigned.
