# RNPL quality-of-growth study: design

- **Date:** 2026-09-11. **Author:** Theo Machado with Claude Code. **Status:** approved direction ("both": exhibit and return model), data extraction pending.
- **Thesis under study:** Reserve Now, Pay Later inflates the metrics the Street extrapolates (Nights and Seats Booked, GBV, ADR through mix, and through them revenue and EBITDA estimates), which drives estimate revisions and price momentum, while the cash the business collects is shifted later and partly never arrives. Momentum runs on the inflated top line; free cash flow is telling the truth and is not being priced.
- **Deliverables for 2 Oct:** (1) a quality-of-growth exhibit (KPI momentum versus FCF conversion and float) with a pre-registered 5 November test; (2) a 3-to-12-month expected-return path built from estimate-revision and momentum behaviour around the lap, in the appendix.
- **Data policy:** external and disclosed data first; no parameter fitted on Airbnb's four RNPL-era quarters; every number tagged measured / derived / assumed; vendor and timestamp on every consensus figure. Bloomberg and UF library access (no WRDS).

## 1. Objects

| # | Object | Inputs | Output | Owner |
|---|---|---|---|---|
| 1 | KPI inflation ledger | ledger D001–D060, cohort engine, nights module, balance-sheet unpaid book | quarterly table 3Q25–4Q27: bundle contribution to nights, GBV, ADR; lap schedule; unpaid book; booking-to-stay wedge | done (audit folder) |
| 2 | Cash-reality object | 10-K/10-Q cash-flow statements 2021–2Q26; unearned-fees and funds-payable balances; interest income; cancellation policy; SBC | FCF as reported vs FCF ex-float (CFO − Δunearned fees − capex); interest income on customer funds and the float it needs; refund/processing cost sensitivity to the cancellation rate; SBC-adjusted FCF; conversion ratios vs revenue and adj. EBITDA; 2027 projection under the RNPL share path | Claude (filings), no Bloomberg needed |
| 3 | Street-perception object | Bloomberg BEst point-in-time consensus (revenue, EBITDA, EPS, FCF; KPI consensus for GBV and nights), revision counts, targets, ratings, estimate dispersion | did FCF estimates move with KPI estimates; Street FY26/FY27 FCF vs object 2; revision breadth around each print | Theo (extraction) then Claude |
| 4 | Momentum and reversal object | Bloomberg prices, total return, momentum indices, short interest, implied vol, earnings history; repo event studies (03, 05, 09, 20) | conditional reaction and 20/60-day drift after ABNB prints split by KPI acceleration vs deceleration and by estimate direction; ABNB's momentum-factor exposure through time; short-interest and IV state into 5 Nov | Theo (extraction) then Claude |
| 5 | Return path | objects 1–4, the +0.48 turns per point multiple rule (applied once), the macro-stress dial | 3-to-12-month expected-return path under bear/base/bull with flip rules; sizing discipline | Claude |

## 2. Tests, pre-registered

1. **Wedge test (5 Nov):** reported nights growth minus the external stays read narrows in 4Q26 guidance and inverts in 1Q27 guidance.
2. **Cash test (5 Nov):** (3Q26 unearned fees y/y − 3Q26 GBV y/y) at or below −18 points supports; −12 to −18 in line; wider than −8 weakens. FCF margin 3Q26 below 3Q25's 32.9% with revenue growth above 15% supports the conversion argument.
3. **Perception test (ongoing):** the ratio of FY27 FCF consensus revisions to FY27 revenue consensus revisions since 6 Aug 2026; if revenue estimates rise and FCF estimates do not fall, the Street is not pricing the float loss.
4. **Momentum test (5 Nov and Feb):** a print or guide that carries a KPI deceleration while consensus revenue estimates are still rising; historical conditional drift from object 4 is the prior.

## 3. Method constraints

- FCF ex-float is defined as CFO minus the period change in unearned fees minus capex; funds payable is excluded from FCF by Airbnb already.
- Interest income attributable to customer funds is estimated from disclosed interest income and the average of funds payable plus unearned fees at the disclosed yield; labelled derived.
- Consensus history is point-in-time only: each series stamped with the pull date and the Bloomberg period override.
- Momentum exposure uses index proxies (S&P 500 Momentum, MSCI USA Momentum) when factor loadings are not exportable.
- No regression of RNPL outcomes on macro; macro enters only as the propensity dial mapping stated in advance.
- The reaction function keeps the red-team's ruling: the guide-below-Street drift rule is a base rate with a story, not a mechanical rule; day-one moves are unpredictable.

## 4. Outputs and paths

- Note: `docs/rnpl-short-audit/05_quality-of-growth-study.md` (exhibit, tests, return path).
- Code: `analysis/src/rnpl_short_audit/qog_*.py`; data: `data/processed/rnpl_short_audit/qog_*.csv`.
- Bloomberg extraction workbook: `data/raw/bloomberg/requests/2026-09-11_rnpl_qog_extraction.xlsx` (formulas embedded; refresh with the Bloomberg Excel add-in; each sheet has a status column).
- Team page: the existing artifact gets a "Quality of growth" section once objects 2–5 exist.

## 5. Risks to the thesis, carried on the record

- FCF is lagging revenue, not collapsing (trailing four quarters +13% vs +15%); the transition effect fades once the RNPL share plateaus.
- The permanent float loss is bounded by the interest yield on customer funds; at current rates it is a modest annual number and must be quoted as such.
- The Street may already model FCF timing (the 10-Q and letters explain it); object 3 decides this.
- Momentum reversal is a base rate, not a prediction; the Q3 print lands after finals.
