# M7: Below-EBITDA bridge (SBC, D&A, interest income, tax, share count, EPS) and the free-cash-flow bridge

Read `docs/margin-build/prompts/M_common.md` first. Slug: `M7_below_ebitda`. Method name: `below-ebitda`.
Inputs: WS02 panel (every below-EBITDA and cash-flow line), `data/processed/abnb_capital_return_quarterly.csv`, `abnb_fcf_bridge.csv`,
`research/notes/2026-09-05_capital-return-panel.md`, `abnb_backlog_indicators.csv` (unearned fees, funds held), WS04 rates series (or pull FRED
DTB3 / DGS1 yourself), WS05 statements on tax, buybacks, SBC, hosting capex, and the revenue/GBV paths (bridge v3, WS06).

## Objects (each with PIT backtests where the history allows, and LIVE 3Q26-4Q27 + FY26-28)

1. `sbc`: SBC total and by line; drivers: headcount proxy (10-K headcount, WS04 job postings if any), grant-cycle seasonality (Q1 step),
   the 2025-26 change in add-back treatment (WS02 caveats). Report SBC as % of revenue and the y/y path.
2. `da`: D&A from capitalised software and hosting; simple trend + the contracted hosting obligations from the 10-K as a leading indicator.
3. `interest_income`: funds held on behalf of guests + corporate cash, times a PIT yield (3-month T-bill with a lag; fit the pass-through beta on
   1Q22-2Q26, n 18); seasonality follows funds held (peaks in Q2). This line is large relative to net income; treat it carefully and show the
   sensitivity to the Fed path (WS04/FRED; spot-held-constant vs the futures-implied path if you can source it publicly, otherwise +/-100bp).
4. `tax`: effective tax rate model (statutory blend, the 2023 valuation-allowance release, the FY26 guided rate, cash taxes vs book) and the
   GAAP vs non-GAAP tax difference; forecast the rate with a range.
5. `share_count`: diluted shares from the buyback pace (authorisation remaining, trailing repurchase per quarter, price), SBC dilution and the
   convert; forecast the quarterly diluted count.
6. `eps`: GAAP diluted EPS and a non-GAAP EPS (adj. EBITDA - D&A - SBC? no: follow the Street definition the WS03 consensus uses; check what
   LSEG's EPS field measures for ABNB and match it) from the adj EBITDA of the M1/M2 base (take the harness `driver-lines` LIVE base if
   registered, else `margin-ts` seasonal) so the reader sees the whole waterfall.
7. `fcf`: FCF = CFO - capex; CFO = net income + D&A + SBC + change in unearned fees + change in funds payable + other; the two working-capital
   lines are tied to GBV seasonality and growth (fit on 1Q21-2Q26); FCF margin by quarter and FY. Backtest at h=0/1 against seasonal naive.

## Tests (pre-register)

Interest income: beat seasonal naive at h=0/1 in both windows. FCF: beat seasonal naive on FY FCF (n 4-5) and quarterly h=0. EPS: report the
error decomposition (how much from EBITDA vs below-the-line) on the last 8 prints.

## LIVE / for the 5 Nov card and the model

Full waterfall 3Q26, 4Q26, FY26, 1Q27-4Q27, FY27, FY28: adj EBITDA -> op income -> pre-tax -> net income -> EPS (GAAP, non-GAAP) and FCF,
vs consensus (WS03) where a consensus exists. A parameter sheet ("For the model": every rate, lag, beta, share-count assumption with source) that WS23
will copy into the workbook.
