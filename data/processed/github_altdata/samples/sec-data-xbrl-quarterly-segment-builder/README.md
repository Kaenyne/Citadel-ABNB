# sec-data (baimmm6767) — sample

Source: https://github.com/baimmm6767/sec-data (Apache-2.0, pushed 12 Sep 2026). A single-file Python engine that
turns SEC EDGAR 10-Q/10-K XBRL into wide quarterly CSV/Excel statements (discrete quarters from YTD/FY, business and
geographic segments, KPIs, integrity checks). Pulled 14 Sep 2026.

What is here: the 7 committed example outputs under output-examples/ (AAPL, AMZN, GOOGL, HOOD, MA, PLTR, UBER; one row
per line item, one column per fiscal quarter, 2011-Q1 to 2026-Q2 depending on ticker), the upstream README
(README_upstream.md), requirements.txt, LICENSE, and the first 200 KB of the 2.27 MB sec_data.py as a code sample.
Pulled with curl from raw.githubusercontent.com; the crawler was NOT run. Total ~0.88 MB (cap 25 MB; nothing truncated
except sec_data.py).

Full dataset: clone the repo (`git clone --depth 1 https://github.com/baimmm6767/sec-data`), `pip install -r
requirements.txt`, then `python sec_data.py --ticker ABNB` (also BKNG, EXPE, MAR, HLT). First run asks for a name/email
for the SEC User-Agent (keyless). Output lands in a local CSV per ticker.
