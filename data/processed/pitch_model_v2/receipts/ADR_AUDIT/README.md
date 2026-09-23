# ADR audit receipts (22 Sep 2026)

Scripts, logs and CSVs behind every number in `docs/pitch-model-v2/dossiers/ADR_AUDIT_krish.md`.
Run each script from the repo root with `PYTHONPATH=analysis/src py -3.13 <script>`; they read the ADR engine's
outputs and write only here.

Not committed (raw downloads): the two SEC filings fetched by the C5 search (`C5_fetched_abnb_2025q3_10q.html`,
`C5_fetched_abnb_2026_def14a.html`) and the INE Chile SDMX structure file fetched by C4. Their URLs, times, status
codes and byte counts are in `C5_fetch_log.json` and `C4_pooled_reconciliation.md` section 6.1; re-fetch from there.
