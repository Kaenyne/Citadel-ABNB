# B16 - bonus-insider-selling

**Question.** Between 17 Sep 2026 and 31 Jan 2027, will Airbnb insiders (Form 4 filers) sell >= $150M of stock in aggregate, or will a new 10b5-1 plan for the CEO be disclosed? Binary. Resolution 31 Jan 2027. Full text and conventions: `research-log.md` section 0b.

**Forecast (revision 1, 2026-09-17, Fable, batch A18 with B14 and B15).** **P = 0.87**, credible interval 0.75-0.95 (sales leg about 0.75, CEO-plan leg about 0.70).

**Why.** A full EDGAR pull (563 Form 4s since Sep 2022, $4.5bn of code-S sales) shows 95% of 137-day windows since 2023 clear $150M, but 68% of that is Gebbia, whose Feb-2026 plan (3.45m shares, $511M) is fully executed with no successor disclosed; ex-Gebbia only 40% of windows clear and the last two Sep-Jan windows were $112M and $61M. Against that, 1.12m shares remain open under Chesky's (525k to 25 Nov) and Blecharczyk's (596k to 20 Nov) plans, about $190M at $167, and the founders adopt plans every February and August (Chesky 5 of the last 6 half-year slots, Gebbia 5 of 5), so a Chesky plan in the 3Q26 10-Q on about 5 Nov is the base case and would resolve the question on its own. A 200,000-path Monte Carlo over these pieces gives 0.915; the final is shaded to 0.87 because the routes to No (both founders paused below their August prices, no August plans) share one driver, the price.

**Impact if it happens.** No operating content. Stock about -$0.5 (a day of headlines; no insider-sale move in the big-moves file). EV 0.87 x -$0.5 = **-$0.4/share: immaterial.** One sentence of colour at most: the founders have sold $4.3bn since 2022 on overlapping half-yearly plans, so a new Chesky plan in November is routine, not a signal.

**Files.**
- `research-log.md`: claims ledger, query log (1 WebSearch), three estimates, sensitivity, pre-mortem, monitoring, `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json`.
- `datasets/pull_form4.py` (EDGAR pull and parse) writes `form4_transactions.csv`, `form4_sales_codeS.csv`, `sales_by_owner_and_plan.csv`; `b16_model.py` writes `b16_summary.json`, `b16_window_history.csv`.
- `sources/`: submissions JSON, 563 Form 4 XMLs (`form4_xml/`), eight 10-Q main documents (`tenq/`) and the extracted Item 5 tables, web log.

**Not submitted anywhere.** Next: Astra audit, then a revision-2 response.
