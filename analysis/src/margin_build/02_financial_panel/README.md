# WS02 financial panel (margin build, Sep 2026)

The one quarterly and annual panel every margin method reads: six cost lines GAAP and ex-SBC, SBC by line, every
Adjusted EBITDA add-back, the GAAP bridge to net income and EPS, cash flow and FCF, funds held, balance-sheet cash,
KPIs (nights, GBV, ADR, take rate), revenue by region, and the seasonality / reconciliation / episode files.

## Run

```
python "analysis/src/margin_build/02_financial_panel/run.py"
```

From the worktree root; exit code 0. Rebuilds every file under `data/processed/margin_build/02_financial_panel/`
and the manifest `data/manifests/margin_build/02_financial_panel.csv` in about 20 s. Figures are drawn by
`figures.py` with `py -3.13` (matplotlib); that step is best-effort and never fails the build.

## Inputs (all local)

| Source | Path | Used for |
|---|---|---|
| SEC companyfacts | `data/raw/xbrl/ABNB_companyfacts.json` | GAAP P&L lines 1Q20-2Q26 and FY2019-25, cash-flow YTD lines, balance sheet |
| Shareholder letters 4Q20-2Q26 | `data/raw/letters/*.htm` | Adjusted EBITDA and FCF reconciliations (every vintage), SBC by function, statement of operations, cash-flow statement, KPI summary table |
| 424B4 prospectus (Dec 2020) | `data/raw/margin_build/02_financial_panel/424B4_*.htm` | 1Q18-3Q20 quarterly income statement, SBC by function, Adjusted EBITDA and FCF; FY2018 |
| 10-Q 1Q21, 2Q21 | `data/raw/margin_build/02_financial_panel/10Q_*.htm` | SBC by function (those two letters carry no footnote) |
| 10-K FY2020-FY2025 text | `data/raw/filings/txt/abnb_10k_FY*.txt` | annual reconciliations, SBC note, revenue by region, headcount, hosting commitment; FY2018 income statement |
| Repo panels | `data/processed/overnight/02_kpi_panel_quarterly.csv`, `10_regional_revenue_xbrl.csv`, `31a_mgmt_margin_statements.csv` | nights/GBV/ADR 3Q20+, quarterly revenue by region, management statements for the episode file |

`panel_lib.py` holds the parsers (sequential-block table reader validated by the NI-to-EBITDA identity, vintage-aware
XBRL de-cumulation paired by filing fiscal year). `run.py` assembles the panel and writes the outputs.

| Nights per booking | `data/processed/airbnb_nights_per_booking.csv` (10-K MD&A geographic mix, FY2020-25) | the per-booking / per-night converter: `nights_per_booking_fy`, `bookings_est_m`, `ops_cash_per_booking_usd`, `cor_cash_per_booking_usd` |

## Outputs

`02_panel_quarterly.csv` (34 quarters 1Q18-2Q26, 145 columns), `02_panel_provenance.csv` (long form, every source seen per
cell, quarterly and FY rows), `02_panel_annual.csv` (FY2018-25 with `soq_minus_annual__*` check columns), `02_seasonality.csv`,
`02_reconciliation.csv`, `02_macro_cycle_episodes.csv`, `02_letter_vintages.csv` (every reconciliation value by letter vintage),
`02_build_log.txt` (warnings, coverage and the pre-registered PASS LINE block); figures `analysis/figures/margin_build/02_financial_panel_*.png`.

Conventions: USD millions; expenses positive; `capex` positive (purchases); `interest_expense` positive; `other_income_expense`
signed as income (+) / expense (-); `*_cash` = GAAP line less that line's SBC; `ga_cash_ex_lodging` = `ga_cash` less the
lodging/withholding/transactional-tax add-back (the reserves sit in GAAP G&A and are added back, so this is underlying G&A);
`restr_recon` is kept separate from `other_addbacks_total`; `pre_ipo` flags 1Q18-3Q20 (424B4 / letter history).

Note: `docs/margin-build/notes/02_financial_panel.md`.
