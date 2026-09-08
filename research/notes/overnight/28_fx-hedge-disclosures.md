# 28. Airbnb's FX hedge disclosures, and what "after hedging" is worth

Krish with Claude Code, 7 Sep 2026. Script `analysis/src/overnight/28_fx_hedge_disclosures.py`; outputs `data/processed/overnight/28_fx_hedge_disclosures.csv`, `28_fx_hedge_tests.csv`, `28_fx_hedge_forward.csv`. Sources: the "Derivative Instruments and Hedging" note in every 10-Q and 10-K 1Q23 to 2Q26 (22 filings pulled from EDGAR; hedge paragraphs in `data/raw/edgar/hedge_paragraphs.txt`, gitignored), XBRL company facts, the KPI panel's letter-stated FX points, `10_fx_quarterly.csv`.

## Bottom line

1. **The hedge program is small in revenue terms.** Airbnb began designating FX forwards as cash-flow hedges of forecast revenue in 1Q23, "typically for up to 18 months". Designated notional grew from $0.5bn (1Q23) to $3.4bn (2Q26), about 46% of LTM non-USD revenue (56% of revenue is non-USD). Realised gains or losses reclassified from AOCI into revenue were immaterial in 2023 and 2024. They turned into losses as the dollar fell: −$42M (3Q25), −$23M (4Q25), −$15M (1Q26), −$19M (2Q26), which is −1.1, −0.9, −0.7 and −0.6pp of revenue growth.
2. **Hedging cannot be the source of the 3Q26 "approximately three point FX tailwind after hedging".** Hedges are on the loss side, and the 2Q26 10-Q expects about $26M of deferred net losses to reach revenue over the next twelve months, roughly −0.2pp a quarter. Gross of the hedge the 3Q26 tailwind is closer to +3.2pp.
3. **The lag is the booking-date rate, not the hedge.** Stripping the hedge out of the letter-stated FX effect and refitting on EUR/USD y/y gives r 0.76 at lag 0, 0.86 at lag 1, 0.58 at lag 2 (n 14), against 0.71 / 0.82 / 0.57 on the stated number. Removing the hedge sharpens the lag-1 relationship slightly and does not remove it. The 10-K supplies the mechanism: service fees are collected at booking, guests pay in their preferred currency, and the company names "timing differences" as a source of currency risk. The USD value of a stay's revenue is largely fixed when it is booked, one to two quarters before check-in.
4. **The "expected to be reclassified within 12 months" figure is a mark, not a forecast.** It matched the realised amount when rates stayed put (2Q25: expected −$104M, realised −$99M over the next four quarters) and missed badly when they moved (4Q24: expected +$68M, realised −$65M). Use it as the hedge contribution conditional on spot staying where it is.

## The series (USD M; pp of prior-year revenue)

| Quarter | Designated notional | AOCI on hedges | Reclassified to revenue | Hedge pp | Stated revenue FX pp | Gross ex hedge pp | EUR y/y |
|---|---|---|---|---|---|---|---|
| 4Q24 | 2,500 | +80 | 0 | 0.0 | 0 | 0.0 | −0.9% |
| 1Q25 | 2,500 | +7 | 0 | 0.0 | −2 | −2.0 | −3.0% |
| 2Q25 | 2,400 | −123 | 0 | 0.0 | 0 | 0.0 | +5.3% |
| 3Q25 | 2,600 | −77 | −42 | −1.1 | 0 | +1.1 | +6.4% |
| 4Q25 | 3,100 | −59 | −23 | −0.9 | +1 | +1.9 | +9.1% |
| 1Q26 | 3,300 | +14 | −15 | −0.7 | +3 | +3.7 | +11.1% |
| 2Q26 | 3,400 | +39 | −19 | −0.6 | +4 | +4.6 | +2.6% |

2Q26 is the lag in one row: EUR was up only 2.6% in the quarter but 11.1% the quarter before, and gross revenue FX was +4.6pp.

AOCI flipped from −$59M (4Q25) to +$39M (2Q26) as the dollar recovered in the second quarter, so the hedges now in the book are in the money for 2027 stays if EUR/USD holds near 1.15. The next-twelve-month figure still shows a loss because the near-dated contracts were struck at weaker-dollar rates.

## For the model

- Carry a separate hedge line under revenue FX: `28_fx_hedge_forward.csv` gives −0.21 / −0.21 / −0.18 / −0.18pp for 3Q26 to 2Q27 from the 2Q26 disclosure, spread by revenue seasonality. Update it each 10-Q from one sentence in the derivatives note.
- Keep WS05's lagged revenue-FX fit for the gross effect. The hedge does not explain the lag, so the fit stands; the gross-ex-hedge version at lag 1 (slope 0.35pp per 1% EUR, r 0.86) is marginally tighter and is in `28_fx_hedge_tests.csv`.
- The hedge ratio has risen every year (27% of LTM non-USD revenue at 3Q23, 46% at 2Q26). If it keeps rising, the reported FX effect will be damped more in 2027 than the history implies. That is a question for the 5 November call: is the program still growing.

## Caveats

Quarterly reclass amounts are as disclosed ("immaterial" recorded as zero); 4Q25 is FY less nine months. Non-designated derivatives ($2.9bn notional) hedge balance-sheet remeasurement and hit other income, not revenue, so they are outside this note. The AOCI figures are net of tax. The lag fit has 14 observations.
