# GBV event two-page memo

Canonical output: `output/pdf/gbv-event-20260915/ABNB_GBV_two_pager.pdf`.
The same directory includes editable Markdown, extracted text, exact input/output hashes,
layout bounds, two Poppler page PNGs and an additive QA receipt.

The builder uses held `integration_v2`, `forecast_v1/results_v1`, `events_v1/run_v3`
and independent `sources_v1/review_v2` outputs. It performs no research fit. The historical
ex-COVID candidate is explicitly different from the current same-season EWM scenario.
Three vector charts show like-for-like guide proxies, matched forecast error and all 23
daily earnings gap/session pairs. Daily legs are not call-only candles.

From this worktree root, choose a **new** output directory:

```powershell
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B analysis/src/forecast_methods/gbv_event_v1/artifacts_pdf/run.py --out output/pdf/gbv-event-review-new
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe' -png -r 125 output/pdf/gbv-event-review-new/ABNB_GBV_two_pager.pdf output/pdf/gbv-event-review-new/page
```

Dependencies: ReportLab, pypdf and Windows Arial fonts (`C:/Windows/Fonts/arial.ttf`
and `arialbd.ttf`); Poppler renders the PDF. The builder rejects an existing output
directory, paragraph overflow, a non-two-page result, unexpected input counts,
failed independent checks or a changed primary Holm verdict.

The PDF skill's authoring-operation marker ran successfully once before authoring.
The first build stopped on a 1.274-point paragraph-height excess and produced no PDF;
the empty output directory was removed, line leading was adjusted, and the subsequent
build passed. No source/data artifact was removed or changed. Both final pages were
rendered at 125 dpi and visually inspected: no clipping, overlap, illegible glyphs or
truncated tables. Source hashes, independent claim closure and this attempt history
are retained in the additive QA receipt.

Parent independently reviews the final PDF. A successful visual review is not forecast
promotion, probability calibration, source-refresh certification or investment execution.
