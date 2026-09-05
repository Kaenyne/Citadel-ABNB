# ABNB Macro-to-Equity IC Brief

This directory contains the editable LaTeX source, the auditable report-assets
builder, generated vector charts, and the generated metrics contract for the
eight-page brief.

The report is a system document and retrospective diagnostic as of 2026-09-03.
It is not a live ABNB forecast, a backtest, or an alpha claim.

## Build

Run from the repository root:

```bash
MPLCONFIGDIR=/tmp/abnb-ic-brief-mpl \
XDG_CACHE_HOME=/tmp/abnb-ic-brief-cache \
python3 docs/forecasting/abnb_ic_brief/build_assets.py

TEXMFVAR=/tmp/abnb-texmf-var \
TEXMFCACHE=/tmp/abnb-texmf-cache \
latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -jobname=abnb_macro_to_equity_ic_brief \
  -output-directory=outputs/reports \
  docs/forecasting/abnb_ic_brief/brief.tex
```

`build_assets.py` recalculates every displayed report statistic from preserved
CSV/workbook inputs, verifies reviewed counts and values, records SHA-256 input
hashes in `generated/metrics.json`, and emits PDF vector figures. It fails the
build if a sample size or reviewed metric drifts.

## Overleaf

The document is a complete standalone LaTeX file. Do not paste it beneath an
existing `\\begin{document}`. Replace the entire Overleaf `main.tex`, then place
`metrics.tex`, `correlation_contrast.pdf`,
`guidance_vs_stock_performance.pdf`, and `event_excess_returns.pdf` beside it at
the project root. The source automatically supports both the repository layout
and this flat Overleaf layout.

## Verify

```bash
python -m pytest -q tests/test_abnb_ic_brief_assets.py
python -m pytest -q
python scripts/validate_project.py --root . --expected-transcripts 23 --metadata-only
pdfinfo outputs/reports/abnb_macro_to_equity_ic_brief.pdf
```

The public archive validation above checks the complete tracked metadata
boundary without licensed bodies. Authorized reviewers can separately hash the
23 acquired PDFs and 23 cleaned Markdown files:

```bash
: "${ABNB_PRIVATE_INPUT_ROOT:?set to the approved licensed-input root}"
python scripts/validate_project.py --root . --expected-transcripts 23 --private-checksums --private-input-root "$ABNB_PRIVATE_INPUT_ROOT"
```

The brief's primary reviewed workbook is
`outputs/workbooks/ABNB_edge_guidance_stock_reaction.xlsx`. Its normalized
supporting panel and reproducibility inputs live under
`outputs/reproducibility/us-europe-guidance`; the rendered report lives at
`outputs/reports/abnb_macro_to_equity_ic_brief.pdf`.
