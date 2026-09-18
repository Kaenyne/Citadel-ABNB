# B16 web/API log (2026-09-17)

WebSearch (1 of 5 budget used):
1. "Airbnb insider selling Chesky Gebbia Blecharczyk Form 4 September 2026" -> sec.gov Form 4 ownership.xml hits for 2026 (all already in the EDGAR pull below); fool.com 2026-07-23 "Airbnb's Chief Strategy Officer selling $2.6 million in stock"; snippets: Blecharczyk sales 17 Aug and 26 Aug 2026 at $182-191; Gebbia 15-16 Jul 2026 236,601 shares at ~$150 under a 10b5-1 plan; Chesky 7 Aug 2026 conversions and sales at ~$165-171. No report of a new plan or of September sales beyond Blecharczyk's.

EDGAR (data.sec.gov / www.sec.gov, User-Agent with contact, saved here):
- sec_submissions_CIK1559720_20260917.json (recent 1,001 filings to 2026-09-16) and CIK0001559720-submissions-001.json (older): the filing index.
- form4_xml/: every Form 4 and 4/A filed under CIK 1559720 with filing date >= 2022-09-01 (563 filings), raw XML, pulled by ../datasets/pull_form4.py at ~8 req/s. Parsed to ../datasets/form4_transactions.csv (1,472 non-derivative transaction rows) and form4_sales_codeS.csv (1,122 code-S open-market sales).
- tenq/: 10-Q main documents for 2Q23, 3Q23, 1Q24, 2Q24, 3Q24, 1Q25, 2Q25, 2Q26 (the 3Q25 and 1Q26 10-Qs were already in the session scratchpad); Item 5 "Director and Officer 10b5-1 Trading Plans" tables extracted to tenq_item5_10b51_tables.txt. The 10-Ks (FY2023-FY2025, repo data/raw/filings) state that no officer or director adopted, modified or terminated a plan in any Q4.

No Polymarket or Kalshi market exists on insider sales (not searched beyond the batch's earlier Airbnb searches: R13 log claim 10).
