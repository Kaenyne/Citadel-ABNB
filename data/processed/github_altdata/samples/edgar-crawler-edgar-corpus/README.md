# edgar-crawler + EDGAR-CORPUS sample

Keyless SEC EDGAR 10-K/10-Q/8-K downloader and per-item splitter (github.com/nlpaueb/edgar-crawler, now lefterisloukas/edgar-crawler, GPL-3.0, last commit 2025-07-18) and heads of its companion EDGAR-CORPUS (one 10-K per row, every Item as plain text, 1993-2020, CC-BY-4.0 on Zenodo 5528490 / Apache-2.0 on Hugging Face eloukas/edgar-corpus).

Pulled 2026-09-14: shallow clone (`git clone --depth 1 --filter=blob:none`), copied only the 8 code/config/licence files (the 42 MB test fixtures and the 7.7 MB companies_info.json were left out; first 200 of 39,022 CIK entries kept in companies_info_head.json). Corpus heads via HTTP byte-range `curl -r 0-3000000` (2020/test.jsonl, 11 complete rows) and `curl -r 0-2000000` (1995/test.jsonl, 28 rows), trailing partial line dropped. Total 4.9 MB, under the 25 MB cap. Nothing was run against sec.gov or airbnb.com.

Full dataset: Zenodo record 5528490 (28 year zips, ~10 GB) or `huggingface.co/datasets/eloukas/edgar-corpus` (87 JSONL files, ~231 GB). To pull peer filings: edit `edgar-crawler_code/config.json` (cik_tickers, years, filing_types, a real user_agent) and run `python download_filings.py` then `python extract_items.py` - a human should sign off on the sec.gov fair-access terms first.
