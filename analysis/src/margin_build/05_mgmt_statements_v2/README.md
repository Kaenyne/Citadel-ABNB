# WS05: management statements v2 and the November guide-language pattern

Rebuilds every CSV in `data/processed/margin_build/05_mgmt_statements_v2/` from the raw texts (exit 0; exit 1 if any
verbatim fails the exact-substring check against its source document).

```
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/05_mgmt_statements_v2/run.py
```

Needs `pandas`; `pdftotext` on PATH for the FactSet PDFs (falls back to the pypdf JSON next to each PDF). Runtime ~1 min.

Inputs (all read-only): shareholder letters `data/raw/letters/`, corrected call transcripts `data/raw/regulatory/transcripts/`,
stockanalysis.com call/conference pages `data/raw/transcripts/web/`, 10-K texts `data/raw/filings/txt/`, and the WS05 pulls
under `data/raw/margin_build/05_mgmt_statements_v2/` (17 10-Qs 1Q21-2Q26 and 8 non-earnings 8-Ks from EDGAR; Goldman
Communacopia 2026 and two 2021 product events from stockanalysis.com) listed with URL, timestamp and sha256 in
`data/manifests/margin_build/05_mgmt_statements_v2.csv`. The 194 rows of `data/processed/overnight/31a_mgmt_margin_statements.csv`
are carried with their ids.

Outputs: `05_statements.csv` (377 rows), `05_guide_language_pattern.csv` (20 prints), `05_guide_language_stats.csv`,
`05_nov2026_scenarios.csv`, `05_fy27_hints.csv`, `05_reliability_by_line.csv`, `05_reliability_by_event.csv`.
Note: `docs/margin-build/notes/05_mgmt_statements_v2.md`. Free parameters: 0 fitted.
