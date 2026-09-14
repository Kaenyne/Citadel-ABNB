# trade-copier-13f-berkshire-panel (sample)

Source: https://github.com/tsushanth/trade-copier-13f (commit 383c5ad, 2026-09-02, no LICENSE file).
What it is: EDGAR 13F-HR holdings of Berkshire Hathaway (CIK 0001067983) for 16 quarters, 3Q22-2Q26, parsed to JSON
with report_date, filing_date and accession on every snapshot; a CUSIP->ticker map; one raw infotable XML as a format
exemplar; a mirror-vs-SPY daily equity curve (993 rows) from a dry-run backtest; and the Python that pulls/parses/diffs.
`holdings_panel.csv` (658 rows) is our flattening of the 16 holdings JSONs into one long table.
How pulled (14 Sep 2026): `git clone --depth 1 --filter=blob:none --sparse` + `git sparse-checkout set data results src`,
then copied the files listed in manifest.json. Nothing run; no keys; Alpaca adapter untouched.
Caps: 0.41 MB written (well under 25 MB); skipped 15 of 16 infotable XMLs, two EDGAR submissions JSONs and the PNG.
Full dataset: clone the repo (~1.5 MB); for other filers run `src/edgar_client.py` with a new CIK against the free EDGAR API.
ABNB relevance: the point-in-time (filing-date) convention and the reusable EDGAR/13F code, not the Berkshire positions.
