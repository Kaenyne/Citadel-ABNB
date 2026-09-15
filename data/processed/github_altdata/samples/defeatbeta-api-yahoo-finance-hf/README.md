# defeatbeta-api / Hugging Face `defeatbeta/yahoo-finance-data` — sample

**What it is.** A daily-refreshed (2026-09-14) ~4.1 GB Hugging Face dataset (ODC-BY) of Yahoo Finance / SEC-derived tables behind the Apache-2.0 `defeatbeta-api` DuckDB client (https://github.com/defeat-beta/defeatbeta-api). No API key: every file is a plain HTTPS URL under `https://huggingface.co/datasets/defeatbeta/yahoo-finance-data/resolve/main/`.

**What is here (6.4 MB, all CSV because the repo gitignores parquet).** Every ABNB earnings-call transcript (23 calls, 4Q20–2Q26, one row per speaker paragraph); 8 recent BKNG calls; the earnings calendar for ABNB + BKNG/EXPE/MAR/HLT/NCLH and a 10k-row head of the full calendar (5,310 symbols, 2023-01 → 2026-09); the revenue-breakdown rows for the peer set (BKNG only — ABNB/EXPE/MAR/HLT/NCLH are not in that table) plus a 10k-row head; daily USD FX for 42 pairs from 2023-01-02 (full file runs from 1996); the whole daily Treasury curve (1990 → 2026-09-11); `spec.json` (file timestamps + SHA-256 of the current release).

**How it was pulled.** `curl -sL -o` for the small parquet/json files; the 2.27 GB transcript table was never downloaded — DuckDB `httpfs` range-scanned it in place (`read_parquet('https://huggingface.co/.../stock_earning_call_transcripts.parquet') WHERE symbol='ABNB'`, 0.7 MB out), then the `transcripts` struct list was `unnest`-ed to paragraphs. Exact commands are in `manifest.json`. duckdb had to be pip-installed into `py -3.13`.

**Caps applied.** ≤ 25 MB hard / ≤ 5 MB preferred: heads of 10k rows for the two broad tables, FX trimmed to 2023+, `company_tickers.json` dropped; 10 URLs fetched.

**Full dataset.** `pip install defeatbeta-api` then `Ticker('ABNB').earning_call_transcripts()` etc., or fetch any of the 16 files directly by URL (`stock_prices.parquet` 467 MB, `stock_statement.parquet` 118 MB, `stock_sec_filing.parquet` 91 MB, `stock_news.parquet` 1.17 GB, transcripts 2.27 GB). DuckDB `httpfs` filters on `symbol` without downloading whole files.

**Human decision needed.** Transcript text is third-party call transcripts redistributed under ODC-BY via a Yahoo scrape; confirm it may be quoted in the pitch package before relying on it.
