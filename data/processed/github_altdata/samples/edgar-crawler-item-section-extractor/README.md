# edgar-crawler-item-section-extractor — sample

Source: https://github.com/lefterisloukas/edgar-crawler (GPL-3.0, last push 2025-07-18, commit 84a8d0c). Method/tooling repo:
keyless SEC EDGAR downloader for 10-K/10-Q/8-K plus an Item-level section extractor (one JSON per filing, one key per Item).
Pulled 2026-09-14 with a depth-1 blob-less sparse clone (root code files copied into code/), a 2 MB range GET of
datasets/companies_info.json (repaired to the last full record -> companies_info_head.csv, 10,314 of 39,022 CIKs), a
SIC-filtered lodging/travel/OTA subset built from the full 7.8 MB JSON read in scratch (2,062 rows), the test-fixture
FILINGS_METADATA_TEST.csv (799 filings, 1994-2023) and one extracted 8-K JSON taken from the 0.99 MB fixture zip.
Caps: about 1 MB written here, no EDGAR crawl run, no keys, nothing touched airbnb.com. ABNB (CIK 1559720), BKNG, EXPE, MAR and HLT are all in the CIK table.
Full dataset: clone the repo, edit config.json (cik_tickers, start_year/end_year, a real User-Agent per SEC policy), run
`python download_filings.py` then `python extract_items.py`; output is RAW_FILINGS/, FILINGS_METADATA.csv and EXTRACTED_FILINGS/*.json.
Use a separate venv: the pinned pandas 1.5.3 / numpy 1.24.4 do not fit this repo's pandas-3 environment.
