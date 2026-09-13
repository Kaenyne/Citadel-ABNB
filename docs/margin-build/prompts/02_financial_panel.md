# WS02: The authoritative financial panel for the margin build

Read `docs/margin-build/00_BRIEF.md` first. Slug: `02_financial_panel`.

## Goal

Build the one quarterly (and annual) panel every method in this run will read. It must reconcile to reported adjusted EBITDA every quarter
and carry every line the targets need: the six cost lines GAAP and ex-SBC, SBC by line, D&A, restructuring, other add-backs, adjusted EBITDA
as reported, operating income, interest income and expense, other income/expense, pre-tax income, tax, net income, diluted shares, diluted EPS
(GAAP; and non-GAAP where the letter gives it), operating cash flow, capex, free cash flow as reported, changes in unearned fees and funds payable
to hosts, funds held on behalf of guests, cash and investments, plus the per-unit denominators (nights, GBV, ADR, revenue per night, take rate)
and the disclosed revenue by region where filed.

## Sources (in priority order; record which source each cell came from)

1. `data/raw/xbrl/ABNB_companyfacts.json` (SEC companyfacts; quarterly values must be de-cumulated from YTD where the filing is YTD only).
2. Shareholder letters `data/raw/letters/` (4Q20-2Q26): adjusted EBITDA reconciliation tables, SBC by line, non-GAAP items, FCF, funds held.
3. 10-K/10-Q text in `data/raw/filings/` and EDGAR (User-Agent per brief): headcount (annual), contractual hosting obligations, insurance/AirCover
   reserves, lodging tax, payment processing description, geographic revenue split (North America / EMEA / LatAm / APAC), share repurchases.
4. Existing repo panels, to reconcile against and to extend backwards: `data/processed/abnb_quarterly_costlines.csv` (1Q20-2Q26),
   `abnb_quarterly_cost_stack_exsbc.csv`, `overnight/02_kpi_panel_quarterly.csv`, `abnb_capital_return_quarterly.csv`, `abnb_fcf_bridge.csv`,
   `overnight/30_quarterly_pnl.csv`, `overnight/31b_*.csv`, `model/ABNB_historicals.xlsx`.

Go back as far as the data allow: the S-1 (Dec 2020) gives 2018-2019 annual and 2019-2020 quarterly cost lines; use them for the seasonal
profile and the 2020 shock but flag them `pre_ipo`.

## Deliverables

1. `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` (one row per quarter 1Q19-2Q26, one column per line in USD millions,
   plus `_src` provenance columns or a companion `02_panel_provenance.csv` in long form: quarter, line, value, source, source_detail).
2. `02_panel_annual.csv` FY2018-FY2025 (same lines; from 10-K, not summed, then a check column of sum-of-quarters minus annual).
3. `02_seasonality.csv`: for each line and for adjusted EBITDA margin, the within-year profile: each quarter's share of the FY total, and the
   quarter's margin, for every year 2019-2025; plus the 2023-2025 mean and range. Separate the mechanical part (revenue recognition timing:
   Q3 revenue peak against costs that are roughly flat through the year) from the discretionary part (Q1 brand campaign, Q4 hiring): show
   cost-per-night and cost-as-%-of-revenue by quarter side by side.
4. `02_reconciliation.csv`: your adjusted EBITDA (from lines) minus reported, every quarter, and your lines minus the three existing repo panels,
   with an explanation column for every non-zero difference greater than $1M. Log any error you find in existing panels under
   "Corrections to existing work" in your note (do not edit those files).
5. `02_macro_cycle_episodes.csv`: the demand-shock episodes the cycle model (M6) will use, with dates and the growth path around them:
   2020 (COVID), 2H22 (post-reopening deceleration and FX), 2023 ADR normalisation, 2025 NA slowdown/inbound shock; for each, revenue growth,
   nights growth and each cost line's growth by quarter, and what management said it cut or held (cross-reference `overnight/31a_mgmt_margin_statements.csv`).
6. Script `analysis/src/margin_build/02_financial_panel/run.py` (rebuilds all CSVs from raw; exit 0) and `README.md`.
7. Note `docs/margin-build/notes/02_financial_panel.md`: bottom line, the reconciliation table (n quarters, max abs gap), the seasonality
   table, definitions of every line (what is in "cost of revenue" per the 10-K, etc.), caveats (restatements, segment changes, the 2023 tax
   valuation-allowance release, the 2025 SBC/other add-back changes), "For the model", RESUME.

## Pass line (pre-registered)

Adjusted EBITDA rebuilt from lines matches reported within $2M for every quarter 1Q21-2Q26 (n 22); annual sums match 10-K within $5M;
every cell has a source. If XBRL and the letter disagree, the letter's reconciliation table wins for non-GAAP items and XBRL wins for GAAP.
