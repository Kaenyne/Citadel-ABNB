# L4 v2 memo, exhibits, unsigned card and decision register

14 September2026; frozen information13September2026. Final artifacts are `deck/drafts/lane4_v2/review_v2/`, with source snapshots/checks under `data/processed/forecast_methods/lane4_review_v2/review_v2/`. This new note does not overwrite the existing L4_REVIEW_v2.md from prior work.

## Delivered and interpreted

- Exactly two-page `review_memo.pdf` with editable `review_memo.md`; no adopted target/direction/probabilities.
- Separate three-page `accepted_L3_exhibits.pdf`, preserving the three accepted PNG/SVG charts byte-for-byte. Chart1 is all22 descriptive calibration; chart2 is identification/year sensitivity; chart3 is matched letter-close validation. Full original limitation captions remain. Last-three baseline in chart3 is distinct from both matched fixed OLS and current K0 estimation policy; no lowest-bar adoption is implied.
- Unsigned12-rule November card in Markdown/CSV/JSON, preserving exact publication precision, missing-data states and phrase review. Explicit guide-expectations availability is a separate rule; guide is never scored against revenue consensus as a surprise.
- Thirteen quantified open decisions. L4v2-D13 preserves original team D-01, Q3 kernel versus already-issued guide times median/mean cushion, as alternative constructions that are never stacked.
- A 1,767-row source/assumption ledger: all1,187 original L3 row dispositions unchanged, plus explicit-period/unit model outputs, inherited assumptions and detailed cash schedules. Dated vendor comparisons remain separate. Rejected free-weight joint extremes are descriptive CSV only, excluded from operational financial envelopes.

Primary arithmetic: Q4 R-S=+$18.322164m/+0.579628% against Yahoo/LSEG-family3,161.021490m,13Sep15:20UTC. G-S=-$37.602375m is a mixed-object diagnostic; hypothetical S/(1+c)=3,105.419237m is not observed guide consensus. Main value$182.867016 at13Sep2027 uses fullFY27EBITDA×16.5 plus interpolatedcash/shares(256/365); December comparison$184.662755 is separate. Soft/reference/firm Q4 guides2,987.939343/3,123.419115/3,149.360344m are tied to corresponding financial outputs; cushion changes guide only.

Free-weight promotion is complete and FAIL in both nested chronological windows; operational fixed2/3 K0 remains. Letter-close conversion errors do not include pre-release forecast GBV or cushion risk. Accepted FX source is not financially eligible: unresolved pre-hedge denominator, signed H/H_new, RNPL recognition exposures and Q4/Q1 cohort data. A2 remains PARTIAL with no established executable edge; its historical sign test is a legacy guide-versus-revenue comparison. B2 FAIL (5/9,4/7 versus70%); RNPL unidentified; fee theta unavailable0/6; NCLH no ABNB adjustment; hotel comparator only.

## Commands, verification and failures

```powershell
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B analysis/src/forecast_methods/lane4_review_v2/run.py --revenue-dir data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1 --model-dir data/processed/forecast_methods/lane4_model_v2/snapshot_v2 --run-id review_v2 --render-pages
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -m unittest discover -s analysis/src/forecast_methods/lane4_review_v2/tests -v
```

Existing IDs are refused; use a new one for reproduction. The bundled ReportLab renderer uses explicit page break and verifies exactly2pages. Poppler renders all2memo+3exhibit pages; all were opened and visually reviewed, with no clipping, missing content or cropped limitations. Poppler exits0 with font fallback notices; no visible missing glyphs resulted. Final18tests pass:11interval-rule tests and7source/artifact checks. An initial exact-string test failed because extracted PDF line wrapping split a phrase; test now normalizes whitespace, failed log preserved. No content was changed to hide that test.

The runner independently checks54scenario financial identities and source eligibility. Parent verified exported workbook caches and final images. A independent source/claim review and B independent economics review passed; narrow followups confirmed A2 wording, corrected Lane2F attribution, Q3 decision continuity and envelope scope. Final receipts bind workbook/PDF/card/register and unchanged chart hashes. The generation receipt is historical; `final_QA.json` supersedes its pending review status.

No new parameters, tests of investment alpha, research fits, registrations/scorers, public actions or commits were performed by this package. Research acceptance and arithmetic integrity do not imply investment adoption. Earlier review_v1 is preserved; final review_v2 binds final model snapshot_v2.

## RESUME

Use final review_v2/model snapshot_v2 and their finalQA receipts. Parent owns the local closure and any future forecasts/registration. For a new source version, audit immutable hashes and accounting eligibility, align revenue/guide expectations, recalculate the financial chain at an explicit date, then regenerate to a new ID and visually inspect all pages. Do not turn missing evidence into zero, descriptive parameter draws into production confidence bands, or an unsigned diagnostic into a trade instruction.
