# python-edgar-full-index-stitcher sample

**What**: SEC EDGAR full-index (one row per filing: company, CIK, form type, filing date, accession path), 2026Q3 file as of 12 Sep 2026, plus the data.sec.gov submissions JSON for Airbnb (CIK 1559720) which adds acceptance timestamps. The GitHub repo https://github.com/edouardswiac/python-edgar (MIT, stale since 2023) is a 4 KB script that stitches every quarterly index since 1993; its `main.py`, README and LICENSE are copied here for reference. No data is committed in the repo.

**How pulled** (14 Sep 2026): shallow clone of the repo; keyless `curl` with an identifying User-Agent against `https://www.sec.gov/Archives/edgar/full-index/2026/QTR3/{company,form}.idx` and `https://data.sec.gov/submissions/CIK0001559720.json`; pandas parsed the fixed-width idx to CSV.

**Caps applied**: sec.gov ignored Range requests, so the full 39 MB idx files were downloaded to scratch and truncated locally: 20k-row heads of the company- and form-sorted indexes, all 8-K/10-Q/10-K rows of the quarter (18,351), the ABNB/BKNG/EXPE/MAR/HLT rows (119), first 2,000 raw idx lines, and the ABNB submissions 'recent' table (1,001 filings, 2023-05-01 to 2026-09-03). Total ~7 MB.

**Full dataset**: `python run.py` in the repo (or loop `https://www.sec.gov/Archives/edgar/full-index/<YYYY>/QTR<n>/company.zip` for 1993Q1-2026Q3) gives ~25-30M filing rows, ~2 GB uncompressed; older ABNB filings are in `https://data.sec.gov/submissions/CIK0001559720-submissions-001.json`. Public domain; obey SEC fair-access (UA with email, <=10 req/s).
