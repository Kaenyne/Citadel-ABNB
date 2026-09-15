# GE-SOURCE additive closure and two-page memo handoff

15 September 2026. Final reviewed analytical versions: `integration_v2/model.json` and
`events_v1/run_v3`; earlier notes and review receipts remain preserved.

**Bounded repair review: PASS. Overall source availability: PARTIAL.** No outstanding
material arithmetic or source-label issue was found in these versions. No held real
ABNB/QQQ intraday panel or directly observed market guide-expectation panel was found.
The conditional four-quarter model is not a promoted forecast or demonstrated trade.

The independent deterministic review passed **314/314 checks**, maximum absolute
difference **3.637978807091713e-12**. Two obsolete historical-comparison checks disappear
after the role-filter repair; there is no lost numerical test failure. Four-quarter
arithmetic, all 23 events' daily return legs, strictly prior cushions and 21 earlier-origin
consensus joins remain checked. The review imports no owning-agent functions.

Additional closure proves nine event CSVs byte-identical from run_v2 to run_v3 and
**1,472 shared event-panel cells** unchanged. The event panel adds raw timestamps and
eligibility labels. Manual review confirms that an explicitly timed observation no
longer inherits the date-only morning exception: aware timestamps must strictly precede
16:00 America/New_York; naive, exact-close and post-close timestamps are rejected. The
owning agent's canonical test receipt reports 12 passed. No association was refit in
this independent closure.

Integration_v2 filters current/pit_history expectations, uses the conditional break-even
conversion name, distinguishes true Q1 publication from a common information cutoff,
and binds all nine transitive input hashes. Q3's already-issued guide remains a diagnostic.
The historical audit candidate uses ex-COVID conversion; its first-guide error metrics
are not direct validation of the current EWM four-quarter conditional scenario.

The price hash discrepancy is solely line endings: working CRLF SHA256
`a94c35e2c70f5bc9ce4b5bd85343fed199ac1e941b94d287bb3ee7780b799286`
becomes retained LF SHA256
`5b03005c30b1793e2d146e6a76fc352ecee56b7fbaf0e9f737bd479652b7a253`
after CRLF-to-LF normalization. Exact bytes and numerical contents are not conflated.

Exact bindings, unchanged-file results and scope limits:
`data/processed/forecast_methods/gbv_event_v1/sources_v1/closure_v3.json`.

## Two-page research memo

`output/pdf/gbv-event-20260915/ABNB_GBV_two_pager.pdf` has exactly two pages and three vector
charts: Q4 common-cushion guide proxies, matched guide RMSE and all 23 daily gap/session
pairs. An editable Markdown companion, extracted text, exact input/output manifest,
layout bounds and both rendered PNGs are in the same directory. No synthetic intraday
candle, calibrated probability, share-price target, forced short or FY2028 model is added.

Current Q4 common-cushion guide gap is +$17.999878m, +0.579628%, versus the selected dated
Yahoo/LSEG family. The conditional zero-gap Q3 GBV is $25,780.296790m, or Q4 conversion
11.970979793%, fixing other inputs. These are algebraic boundaries, not executable trade
thresholds. The PDF explicitly separates the ex-COVID historical audit from current EWM.

The PDF skill was read and the required operation marker ran once successfully before
authoring. Initial layout validation stopped before PDF creation on a paragraph-height
limit; the empty directory was removed and leading shortened. The next build passed.
Both final 125-dpi Poppler PNGs were visually inspected with no overlap, clipping,
unreadable labels or missing glyphs. Parent was asked to independently inspect both pages.
The additive QA receipt does not pre-claim the parent's pending independent approval.

## Reproduction / RESUME

From the worktree root:

```text
python -B analysis/src/forecast_methods/gbv_event_v1/sources/review.py --name review_new --model data/processed/forecast_methods/gbv_event_v1/integration_v2/model.json --events data/processed/forecast_methods/gbv_event_v1/events_v1/run_v3
python -B analysis/src/forecast_methods/gbv_event_v1/artifacts_pdf/run.py --out output/pdf/gbv-event-new
pdftoppm -png -r 125 output/pdf/gbv-event-new/ABNB_GBV_two_pager.pdf output/pdf/gbv-event-new/page
```

Use a new output name; builders refuse overwrite. Bundled-runtime exact Windows commands
and font dependencies are in `artifacts_pdf/README.md`. The fixed-version closure script
and QA recorder also refuse existing receipts; they already ran for canonical outputs.
Parent should finish workbook review, inspect final PDF pages and bind this package in
the overall delivery receipt. Source gaps remain explicit; no additional model search is
needed to finish the requested deliverables.
