# talsan/ishares — iShares ETF holdings history (sample)

Sample of https://github.com/talsan/ishares (scraper for ishares.com per-fund holdings-history CSVs; no licence declared; last push 2024-10-28).
Pulled 2026-09-14 by raw-URL curl only; the scraper was NOT run (third-party site, terms-of-service decision for a human).

Files: IWB_holdings_20220823.csv (full committed file, 5.8 MB, Russell 1000 ETF month-ends 2019-12-31..2022-07-29, 32,626 rows),
IWV_holdings_20220516_head.csv (first 2 MB of the 93.6 MB Russell 3000 file, 2006-09..2007-01, 12,695 rows), ishares-etf-index.csv
(395 iShares ETFs with product URLs), repo_README.md, repo_README_Quant.md, athena_ishares_etf_holdings.sql (schema).
Caps: skipped IWB_holdings_20220621.csv (14 MB) and the rest of IWV (93.6 MB); total here ~7.9 MB.
ABNB appears only in the 2022-06-30 and 2022-07-29 IWB snapshots (weight 0.094% / 0.107%, ~274k shares); BKNG/EXPE/MAR/HLT in all 32.
Full dataset: clone the repo and run `python ishares/easy_downloader.py` or `sync_etf_downloader.py --outputpath <dir> IWB IWV ...`
(history back to 2006 for 395 ETFs) — only after a human clears the iShares terms of use.
