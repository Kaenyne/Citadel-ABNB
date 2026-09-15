# L4 integration v2 — local review handoff

14 September 2026 execution; information frozen at 13 September 2026. Parent and
three subagents on `codex/lane4-full`, starting at
`29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`. New packages only:
`lane4_sources_v2`, `lane4_revenue_v2`, `lane4_model_v2`, `lane4_review_v2`,
`lane4_control_v2`. No investment decision is signed.

## Verdict and ownership

**Implementation and integration PASS within the stated conditional scope.**
The accepted L3 source is integrated into L4's revenue/guide reconciliation,
financial workbook and review materials. **Retain the operational fixed 2/3–1/3
kernel and its existing seasonal policy.** L3 completed conversion validation;
the estimated-weight candidate failed promotion in both matched chronological
windows. L4 made no new statistical fit and did not reopen the failed alpha
research. Accounting eligibility is separate: the present L3 FX/RNPL inputs do
not support a central financial adjustment. That effect remains unestimated.

The conversion scoping begun before the role correction is preserved in
`L4_CONVERSION_SCOPING_HANDOFF_TO_L3_v1.md`. It records the 22-quarter input
inventory and proposed review questions, with no fitted coefficients or test
results. L3 owns estimation and validation; L4 owns integration and presentation.

## Accepted source and delivered versions

- Bundle-containing Git commit: `8821961853e4068febbfe2712f9a4e1036c9e629`.
- Research source commit: `7fb6fe0f248d5492b899672b9b70545da62d63ee`.
- Supplied manifest SHA256:
  `9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970`.
- Verified consumption copy:
  `data/processed/forecast_methods/lane4_sources_v2/snapshot_v1/`.
- Revenue and expectations:
  `data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1/`.
- Final financial data: `data/processed/forecast_methods/lane4_model_v2/snapshot_v2/`.
- Final linked workbook:
  `model/lane4_v2/outputs/lane4_model/snapshot_v2/ABNB_L4_review.xlsx`.
- Final exactly-two-page PDF and editable Markdown:
  `deck/drafts/lane4_v2/review_v2/review_memo.pdf` and `review_memo.md`.
- The same review directory contains the separate three-page
  `accepted_L3_exhibits.pdf`, 12-rule unsigned card, 13-decision register,
  1,767-row source/assumption ledger and financial/expectations tables.

All 108 manifest files, 104 research-object lineage comparisons and 32 acceptance
bindings match the immutable Git objects exactly. The 125-file source snapshot
reproduced byte-for-byte. Two explicitly supplied QVS notes were copied with
hashes. No changing L3 worktree or unspecified supplement was consumed. Identity
verification is not an independent replication of L3's statistical tests.

All 1,187 source rows retain their source fields and explicit dispositions:
962 conditional, 198 calculated, seven descriptive, four comparators, four
unavailable and 12 rejected. None is silently promoted into measured cohort
parameters. See `L4_SOURCES_v2.md` and `snapshot_v1/row_dispositions.csv`.

## Reconciled results

USD millions except value per share. Each row is one conditional scenario, not
a historical validation sample or a probability-weighted investment case.

| Object | Reference | Main soft stress | Main firm stress |
|---|---:|---:|---:|
| Q4 2026 revenue | 3,179.343654 | 3,103.871390 | 3,205.749358 |
| Q4 2026 implied guide | 3,123.419115 | 2,987.939343 | 3,149.360344 |
| Revenue minus dated Yahoo/LSEG revenue | +18.322164 | -57.150100 | +44.727868 |
| FY27 revenue | 15,952.233241 | 15,741.165543 | 16,049.945718 |
| FY27 adjusted EBITDA | 5,807.532522 | 5,625.060886 | 5,899.671105 |
| FY27 free cash flow | 5,536.825326 | 5,364.484940 | 5,624.273710 |
| 13 September 2027 conditional value/share | 182.867016 | 177.329623 | 185.680568 |

Reference uses the retained K0 seasonal policy, explicit team nights/ADR
replacement, and trailing-eight median cushion 1.790491%. Soft uses ADR mean
reversion, seasonal lambda minus 0.10 percentage point and Q4 cushion 3.88%.
Firm uses alternative nights A, lambda plus 0.10 percentage point and median
cushion. Weight remains 2/3. These stress sizes are assumptions, not confidence
intervals. Cushion changes guide only, not revenue, earnings or cash.

The nine-case workbook also retains the other operating cases and isolated net
after-hedge revenue sensitivities of minus/plus 1%. Those give conditional
September values of $179.184576/$186.549457. They are not identified FX/RNPL
effects and are excluded from the main three-case envelope. No generic net
factor is combined with the conversion stress.

The earlier Q4 guide reconciliation remains intact:
3,059.403011 + 32.580444 GBV replacement + 2.717883 seasonal-conversion policy
difference + 63.526624 cushion replacement = 3,158.227962 for K0's conditional
GBV case. No FX overlay closes that gap. The review operating case is a separate
3,123.419115 guide; no figure is selected because it better supports a thesis.

## Presentation claims we can defend

1. “Our conditional Q4 revenue is $3,179.34 million, $18.32 million or 0.58%
   above the Yahoo/LSEG-family revenue estimate captured on 13 September 2026
   at 15:20 UTC.” The comparison has n=1; it is not an established trading edge.
   The source panel is $3,161.021490 million, 36 analysts. S&P's $3,160 million
   (10 September, 35 analysts) and Zacks' $3,200 million (11 September, ten
   analysts) remain separate dated panels.
2. “The implied management guide is $3,123.42 million under a 1.7905% cushion.”
   Guide minus revenue consensus is -$37.60 million, a different-object
   diagnostic. It is not a negative guide surprise. Applying the same cushion
   to Street revenue gives a hypothetical $3,105.419237 million guide and a
   hypothetical $17.999878 million guide gap; explicit guide expectations are
   unavailable.
3. “Estimating the shared lag weight did not improve reliably enough to
   replace the fixed benchmark.” Accepted matched free/fixed OLS RMSE ratios
   are 1.165407390 in W1 (2023Q1–2026Q2, n=14) and 1.015512948 in W2
   (2024Q1–2026Q2, n=10). W2 is nested. The comparator's OLS season calibration
   is distinct from retained operational K0 policy. Its two early W1
   abstentions remain preserved; do not compare unmatched headline errors.
4. “The fitted weight 0.78647848 and seasonal coefficients are descriptive
   predictive coefficients, not measured booking-to-recognition shares.” Even
   within the two-lag equation, dollar shares depend on weighted cohort GBV.
   Physical recognition shares require additional cohort evidence.
5. “The conditional reference value is $182.87 per share at 13 September 2027.”
   It uses 16.5 times full FY27 EBITDA plus $10,029.055795 million net cash,
   divided by 578.854211 million shares. Net cash and shares use FY26 end plus
   256/365 of FY27 net flows under a uniform-within-year assumption. The later
   December value is $184.66; the $1.80 difference reflects only cash/share
   timing. The inherited multiple is conditional, and neither price is an
   adopted target.
6. “L3's FX scenario arithmetic is verified, but a central financial FX/RNPL
   adjustment remains unidentified.” Q3 cohort inputs do not certify the
   pre-hedge baseline or provide signed embedded/scenario hedge contributions,
   and Q4/Q1 cohort scenarios are absent. Null is not measured zero.

Accepted conversion resampling and year-deletion exhibits remain descriptive.
The 1,000 free-weight parameter vectors are propagated intact at fixed reference
operating/cushion assumptions in a separate rejected-model exhibit. Their range
is not a K0 prediction interval. Letter-close validation uses just-printed GBV;
its errors omit today's unprinted Q3 GBV and future cushion uncertainty. No new
confidence band, significance-only selection or pre-release guide-skill claim
is manufactured by L4.

## Independent review and preservation

Source worker A authored immutable provenance/accounting; revenue worker B
authored reconciliation; artifact worker C authored workbook/memo. C reviewed
A's source implementation, A reviewed C's evidence/claims, B reviewed C's
financial mechanics and decision continuity, and parent reviewed B's changed
arithmetic and C's exported OOXML/visuals. Authors did not approve themselves.

Parent independently checked 21,252 changed-integration arithmetic identities
(maximum difference $1.275e-11 million), all 30 revenue output hashes and all
30 source hashes. B's independent financial audit reproduced 759 checks across
nine cases/27 annual rows, maximum difference $2.91e-11 million. The first raw
workbook export audit found 1,875 formulas, zero error cells, zero external
links, and 316 independent cache/cash/share/expectations checks. Its largest
difference was $0.000007376 per share from rounded legacy replication inputs.
Final export receipt supersedes the preliminary draft's byte identity.

Final rotated source review also passes: 90 checksum comparisons, all 1,187
source dispositions and six unchanged accepted charts. The 319 earlier source,
arithmetic and joint-parameter checks carry through byte-identical financial
outputs. Both reviewers verified their wording/decision corrections in
`review_v2` and recorded final artifact hashes. See
`L4_INDEPENDENT_REVIEW_v2.md` and `L4_ARTIFACT_EVIDENCE_REVIEW_v2.md`.

The final `snapshot_v2` export passes the same 316 independent checks and
1,875-formula/no-error/no-external-link audit in
`lane4_control_v2/export_review_v2.json`. Parent inspected the final case table
and both memo pages: the ninth column is formatted consistently and text/table
content is readable with no clipping. A separate PDF parse confirms two memo
pages and three appendix pages. Final memo SHA256 is
`53e102eeca2dcda418368924cacb9a28486f3274332ba0b06fc804a6b1fe0187`;
appendix SHA256 is
`da5636822a00075e9692adb8adb602d4b503525393f0765ac71bdfc3942a6db3`.

Package tests pass: sources 18, revenue 49, model nine, review 18 (94 total).
One review test initially treated whitespace differences in PDF text extraction
as a content failure; the assertion was repaired and the failed log retained.
An initial model-development quote-escaping failure was also repaired and its
failed output/log retained. Final code and outputs pass the applicable checks.
Workbook preview rendering writes all PNGs but exits 1 during the bundled
runtime teardown, as in v1. The numerical build/export and PDF runners exit 0;
rendered images were opened and inspected. This preview limitation is disclosed
rather than reported as an entirely clean rendering command.

All 126 saved outputs in a fresh nine-case recapture match the frozen workbook
exactly. Final author QA receipts are in `lane4_model_v2/snapshot_v2/final_QA.json`
and `lane4_review_v2/review_v2/final_QA.json`. The final workbook SHA256 is
`882b6d7b321d2f791fecc9b1d7ec57265b5e2fdcedd705326ee7bd3ee9ce6f92`.
Author package/peer-review notes are `L4_MODEL_v2.md`, `L4_ARTIFACTS_v2.md`
and `L4_SOURCE_INTERPRETATION_REVIEW_v2.md`.

Review repaired explicit LSEG vendor selection, the ninth-column formatting,
text encoding, the guide-to-financial scenario connection, cautious A2 wording,
the L2 attribution and the open Q3 revenue-method decision. The initial draft
receipts are retained as developmental evidence; final files use new IDs.

Preservation receipt `lane4_control_v2/close/receipt.json` passes: 4,381
pre-existing tracked files and 135 external FX dependency files are unchanged.
All 76 registry files and historical score files are unchanged. No operational
forecast was replaced or newly registered; assumed stress scenarios are
sensitivity diagnostics. Both scorers were therefore not unnecessarily rerun.

The first strict Git whitespace check failed while all staged bytes matched
and no pre-existing file was modified. The diagnostic is retained in
`lane4_control_v2/staging_review_v1.json`. Review classified 25,345 CRLF-only
findings, 21,852 cosmetic trailing-whitespace findings in serialized/copied
text (including the unchanged source SVGs), and two blank EOF lines. The
checksum-preservation rule takes precedence over reformatting these sources.
`staging_review_v2.json` records the explicit exception policy, no unexpected
diagnostics, no prohibited files and no byte mismatches. The raw Git whitespace
exit remains 2; it is not represented as a clean strict whitespace check.

## Reproduction and remaining limits

Run from the L4 worktree root. Python calculations use the repository virtual
environment; PDF creation uses the bundled Python; workbook creation uses the
bundled artifact-tool Node runtime. Package READMEs provide exact commands.
Every rebuild ID must be new; existing snapshots refuse overwrite.

```powershell
python -B -X utf8 analysis/src/forecast_methods/lane4_revenue_v2/run.py --as-of 2026-09-13 --output data/processed/forecast_methods/lane4_revenue_v2/reproduction_new
python -B -X utf8 analysis/src/forecast_methods/lane4_model_v2/run.py --revenue-dir data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1 --run-id reproduction_new
```

Use the source runner's documented Git-object extraction/audit command and the
review runner's documented bundled-Python command for source and PDF rebuilds.
`lane4_control_v2/README.md` gives independent revenue/export/preservation checks.
No original workbook, protected input, L0 file or harness was edited. Missing
guide expectations, hedge/cohort exposures, fee theta and team adoption remain
open. A2 is PARTIAL with no established executable edge; B2 failed its revision
hurdle; NCLH failed transferability; hotel data remain comparators. The model
does not validate a trade direction, target or probability.

Public publication remains outside the authorized scope. This package ends in
a reviewed local commit, with no push, PR, merge, outreach or signed card.

## RESUME

Read the final version identities and all three review notes before using these
materials. Consume the frozen source/revenue/model/review versions, preserve
the fixed operational conversion policy, and use the same-object expectations
comparison. A later L3 supplement requires an explicit immutable commit,
accounting/cohort compatibility and fresh propagation artifacts. The separate
quantitative task owns any new thesis validation. Team direction, target,
probabilities and November card adoption remain unsigned. Do not retry public
publication without separate user authorization.
