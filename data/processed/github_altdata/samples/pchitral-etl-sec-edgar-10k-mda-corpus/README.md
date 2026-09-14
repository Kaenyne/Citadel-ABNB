# Sample: pChitral/ETL-SEC-EDGAR-10-k-Filings (10-K MD&A text corpus)

- **What**: Item 7 MD&A text extracted from annual 10-Ks, one row per company-fiscal-year, one parquet per ticker (135 tickers upstream, ~200 MB). Sampled here: BKNG (20 rows, FY2004-2023), MAR (21 rows, FY2003-2023), UBER (4 rows, FY2020-2023). No ABNB/EXPE/HLT parquet exists upstream.
- **Columns**: cik, ticker, title, year, mda_section (full text, ~100k chars), processed_timestamp (all 2024-01-15).
- **Also here**: `*_head.csv` (same rows, mda_section truncated to 2,000 chars, for git-friendly viewing; `*.parquet` is gitignored), `processing_status.csv` (10,909-row ticker universe; `processed` is False everywhere), upstream `UPSTREAM_README.md` and `LICENSE` (custom MIT-equivalent).
- **How pulled** (14 Sep 2026): `curl -sL https://raw.githubusercontent.com/pChitral/ETL-SEC-EDGAR-10-k-Filings/HEAD/<path>` for the six files; sparse git clone failed on Windows (path too long). Read with `py -3.13` (pandas + pyarrow); the repo venv lacks pyarrow.
- **Caps applied**: 6 files, 2.55 MB total (well under the 25 MB cap); no logs, no other tickers.
- **Full dataset**: `git clone --depth 1 https://github.com/pChitral/ETL-SEC-EDGAR-10-k-Filings` (~210 MB) or GET individual `ticker_data/<TICKER>.parquet` files. To add ABNB, run the repo's ETL scripts (sec_edgar_downloader, needs only a user-agent string).
- **ABNB use**: cross-sectional baseline for management-tone / topic scoring of ABNB's own 10-K MD&A against BKNG, MAR and 133 other large caps. Annual cadence only.
