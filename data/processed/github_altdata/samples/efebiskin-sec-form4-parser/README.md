# efebiskin/sec-form4-parser — sample

What: MIT-licensed typed Python parser for SEC Form 4 insider-trading XML (code only, no data in the repo), plus a small live test on Airbnb.
Pulled 2026-09-14 by shallow clone (--depth 1 --filter=blob:none) and two keyless GETs to SEC EDGAR with a declared User-Agent (no key, no login).
Files: repo_README.md, parser.py, models.py, fixture_sample_form4_purchase.xml (from the repo); abnb_form4_filings_index.csv (491 Form 4/4A rows for CIK 1559720, filings 2023-05-01 to 2026-09-03, from data.sec.gov submissions JSON); abnb_form4_latest.xml (accession 0001193125-26-382108); parsed_transactions_sample.csv (parser output over the live filing and the two fixtures, 6 rows).
Caps: ~88 KB written, far under the 25 MB cap; only one Form 4 XML fetched.
Full dataset: pip install from the repo (or `from sec_form4_parser import parse, fetch_xml`), then loop the accession numbers in the index (plus the older shard CIK0001559720-submissions-001.json for pre-May-2023 filings) at <=10 req/s; the complete ABNB Form 4 history is roughly 700-900 XML files, under 10 MB.
Note: the public API is parse(), not parse_form4() as the job card assumed.
