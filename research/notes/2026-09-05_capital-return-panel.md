# ABNB capital return: SBC, buybacks, share count and the cannibal scorecard

- **Sources:** SEC XBRL company facts for ABNB, BKNG, EXPE, META, NFLX, UBER, DASH (S33); Airbnb shareholder letters for quarterly free cash flow from 1Q23 (S23). Script `analysis/src/capital_return_panel.py` rebuilds both CSVs.
- **Date:** 2026-09-05
- **Author:** Krishang Surapaneni (compiled with Claude Code). Plan-of-attack branch 4. Companion to `research/notes/2026-09-05_margin-drivers.md` (SBC is excluded from Adjusted EBITDA, so this note is where it lands).

---

## 1. Bottom line

1. **About a third of Airbnb's free cash flow goes to paying for dilution.** In FY2025 SBC was $1.6B, 13.1% of revenue and 34.7% of free cash flow. Buybacks plus RSU tax withholding were $4.35B, 94% of FCF, but only $2.75B of that, 60% of FCF, was a net return to shareholders after covering the shares issued to employees.
2. **The share count is falling 3% to 4% a year and the pace is rising.** Diluted weighted shares went from 680M (FY2022) to 623M (FY2025) and 597M in 2Q26, down 4.6% year over year. Airbnb spent $11.9B on buybacks and withholding in 2023 to 2025 to cut the count 8.4%, about $1.4B per point.
3. **Per-share FCF grew 48% from 2022 to 2025 against 35% for FCF itself.** The buyback added roughly 4 points a year to per-share growth. That is the whole equity story if margin stays at the floor: per-share compounding from the share count, not from operating leverage.
4. **Airbnb carries the heaviest SBC load in the peer set.** SBC as a share of revenue in FY2025: ABNB 13.1%, META 10.2%, DASH 7.7%, UBER 3.5%, EXPE 2.7%, BKNG 2.3%, NFLX 0.8%. Booking cut its share count 18.5% over 2022 to 2025 for $24.4B, about $1.3B per point, with SBC absorbing 7% of FCF; Airbnb paid a similar dollar amount per point of reduction but only after spending a third of FCF on SBC first.
5. **For the model.** Base case: buybacks about $4.2B a year, SBC 13% of revenue, net share count down 3.5% a year; at $182 a share and 597M shares, $1B of repurchase retires about 0.9% of the count. A bull case where SBC growth falls below headcount growth, as guided for 2026, lifts the net return toward 70% of FCF without spending more.

---

## 2. ABNB quarterly panel

Source: `data/processed/abnb_capital_return_quarterly.csv`. SBC is the income-statement allocation; buybacks and withholding are cash-flow items differenced from year-to-date figures; FCF is CFO less capex from XBRL through 2022 and from the letters' Free Cash Flow reconciliation from 1Q23 (Airbnb stopped tagging capex separately). Q4 weighted shares are approximated as four times the annual average less Q1 to Q3.

| Quarter | Revenue | SBC | Buybacks | RSU withholding | FCF | Diluted shares (M) | SBC % rev | Buyback % FCF | Net cash return* | Shares YoY |
|---|---|---|---|---|---|---|---|---|---|---|
| 3Q22 | 2,884 | 234 | 1,000 | 146 | 958 | 680 | 8.1 | 104 | 912 | -0.3% |
| 4Q22 | 1,902 | 254 | 500 | 116 | 455 | 683 | 13.4 | 110 | 362 | |
| 1Q23 | 1,818 | 240 | 493 | 151 | 1,581 | 670 | 13.2 | 31 | 404 | +5.5% |
| 2Q23 | 2,484 | 304 | 507 | 721 | 900 | 665 | 12.2 | 56 | 924 | -2.8% |
| 3Q23 | 3,397 | 286 | 500 | 151 | 1,310 | 660 | 8.4 | 38 | 365 | -2.9% |
| 4Q23 | 2,218 | 270 | 752 | 201 | 46 | 653 | 12.2 | n/m | 683 | -4.4% |
| 1Q24 | 2,142 | 295 | 750 | 155 | 1,909 | 654 | 13.8 | 39 | 610 | -2.4% |
| 2Q24 | 2,748 | 382 | 749 | 154 | 1,043 | 649 | 13.9 | 72 | 521 | -2.4% |
| 3Q24 | 3,732 | 362 | 1,093 | 113 | 1,074 | 642 | 9.7 | 102 | 844 | -2.7% |
| 4Q24 | 2,480 | 400 | 838 | 208 | 458 | 635 | 16.1 | 183 | 646 | -2.8% |
| 1Q25 | 2,272 | 358 | 807 | 152 | 1,781 | 632 | 15.8 | 45 | 601 | -3.4% |
| 2Q25 | 3,096 | 424 | 1,010 | 143 | 962 | 626 | 13.7 | 105 | 729 | -3.5% |
| 3Q25 | 4,095 | 399 | 877 | 136 | 1,349 | 621 | 9.7 | 65 | 614 | -3.3% |
| 4Q25 | 2,778 | 400 | 1,095 | 130 | 521 | 613 | 14.4 | 210 | 825 | -3.5% |
| 1Q26 | 2,678 | 410 | 1,088 | 140 | 1,704 | 608 | 15.3 | 64 | 818 | -3.8% |
| 2Q26 | 3,608 | 487 | 1,051 | 165 | 1,253 | 597 | 13.5 | 84 | 729 | -4.6% |

$M except shares. *Net cash return = buybacks + RSU tax withholding - SBC. 4Q23 FCF carries the roughly $1B of one-time tax payments. Buybacks began in 3Q22 ($2B authorization, Aug 2022); the current $6B authorization (Feb 2024) had $5.6B remaining at end-2025 per the 4Q25 letter.

What the quarterly series shows:

- **Buybacks stepped up twice**: from about $500M a quarter (Q4 2022 to Q3 2023) to $750M (Q4 2023 to Q2 2024) to $1.0B to $1.1B (Q3 2024 onward, with Q3 2025 the exception at $877M). Management said in Q4 2024 it would be "slightly price-sensitive"; the $877M quarter followed the stock's summer 2025 rally.
- **SBC is seasonal in ratio, not in dollars.** Dollars have risen every year ($195M in Q1 2022 to $487M in Q2 2026) while revenue seasonality makes the Q1 and Q4 ratios look worst. The FY figure is the one to model: 11.1% (2022 and 2023), 12.6% (2024), 13.1% (2025). 2026 guidance is for SBC growth below 2025's 13%, so the ratio should flatten at about 13%.
- **RSU withholding is the second buyback.** Airbnb uses corporate cash to pay employees' RSU taxes and withholds the shares, which retires stock the same way a repurchase does: $607M in 2022, $1.2B in 2023 (the double-trigger IPO RSUs), $630M in 2024, $561M in 2025. Management's "$16B since Q3 2022" figure includes it.
- **The share-count decline is accelerating** because the buyback dollars rose while SBC dollars rose more slowly and the double-trigger RSUs finished vesting in 2024: -2.4% to -2.9% year over year through 2024, -3.3% to -3.5% in 2025, -3.8% and -4.6% in the first two quarters of 2026.

---

## 3. Cannibal scorecard: ABNB against six SBC-heavy compounders

Source: `data/processed/capital_return_scorecard_annual.csv`. FY2025 unless stated; 2022 to 2025 cumulative where labelled. FCF is CFO less capex. Netflix share counts are adjusted for the November 2025 10-for-1 split and its SBC is the cash-flow add-back. Gross bookings are not in XBRL so take rate is not shown here; see the margin note section 13 for Booking.

| | ABNB | BKNG | EXPE | META | NFLX | UBER | DASH |
|---|---|---|---|---|---|---|---|
| Revenue FY25 ($B) | 12.2 | 26.9 | 14.7 | 201.0 | 45.2 | 52.0 | 13.7 |
| SBC % revenue | 13.1 | 2.3 | 2.7 | 10.2 | 0.8 | 3.5 | 7.7 |
| SBC % FCF | 34.7 | 6.7 | 12.8 | 44.3 | 3.9 | 18.7 | 48.3 |
| Buybacks + withholding % FCF | 94.3 | 76.7 | 62.1 | 96.8 | 97.0 | 66.8 | 0.0 |
| Net cash return % FCF (after SBC) | 59.6 | 70.0 | 49.3 | 52.5 | 93.1 | 48.1 | -48.3 |
| Diluted shares YoY | -3.4% | -4.2% | -4.3% | -1.5% | -1.1% | -1.4% | +2.2% |
| Diluted shares 2022 to 2025 | -8.4% | -18.5% | -18.4% | -4.7% | -3.7% | +7.3% | +18.4% |
| Buybacks + withholding 2023 to 2025 ($B) | 11.9 | 24.4 | 5.9 | 115.3 | 21.5 | 7.8 | 1.0 |
| SBC 2023 to 2025 ($B) | 4.1 | 1.7 | 1.3 | 51.1 | 1.0 | 5.6 | 3.2 |
| $B spent per 1% share reduction | 1.4 | 1.3 | 0.3 | 24.3 | 5.7 | n/a | n/a |
| FCF growth 2022 to 2025 | +36% | +47% | +12% | +139% | +485% | +2,403% | +1,038% |
| FCF per share growth 2022 to 2025 | +48% | +80% | +37% | +151% | +507% | +2,232% | +862% |

Reading the scorecard:

- **Two groups.** Booking, Expedia and Netflix run SBC at 1% to 3% of revenue and convert 70% to 93% of FCF into net capital return. Airbnb, Meta and DoorDash run SBC at 8% to 13% and return roughly half of FCF or less after paying for it. Uber sits between, having only started buying back in 2024.
- **Airbnb buys the same share reduction Booking does, but has to earn twice the FCF to fund it.** Both spent about $1.3B to $1.4B per point of share-count reduction over 2023 to 2025. Booking got 18.5 points for 260% of its 2022 FCF; Airbnb got 8.4 points for 350% of its 2022 FCF, because a third of the spend went to offsetting SBC first.
- **The per-share gap is the argument for the buyback.** Airbnb's FCF grew 36% over 2022 to 2025 while FCF per diluted share grew 48%. That 12-point gap is what shareholders got for the $11.9B. Booking's gap was 33 points on $24.4B.
- **The SBC ratio is also a margin question.** In the margin note the cash cost stack shows product development flat at 10% to 11% of revenue in cash while the GAAP line rose; the difference is this SBC, 60% of which sits in product development. Management's 2026 guide that SBC and headcount grow more slowly than 2025 is the first time the ratio is guided down.

---

## 4. For the model and the deck

- **Net share change.** Base: buybacks of $4.0B to $4.4B a year (the 2025 run rate of about $1.05B a quarter), RSU withholding about $0.6B, SBC 13% of revenue, giving a diluted count down about 3.5% a year: 623M (FY25) to roughly 600M (FY26 average) and 580M (FY27). Bear: buybacks cut to $3B if FCF slips, count down 2%. Bull: SBC ratio drifts to 12% and buybacks hold, count down 4% to 4.5%.
- **FCF versus EBITDA.** FCF margin (38% in 2025) sits above Adjusted EBITDA margin (35%) only because SBC is excluded from EBITDA and unearned fees front-run revenue. Reserve Now, Pay Later is now deferring cash from bookings closer to stays, which management said cut Q1 and Q2 2026 unearned fees; the FCF bridge in the margin note (section 12) quantifies it.
- **Slide framing.** Show SBC as a percent of revenue against the peer set, then net cash return as a percent of FCF. The point is not that Airbnb's buyback is fake; it is that the equity story needs both the margin floor and a falling SBC ratio to convert 36% FCF growth into per-share growth near 50%.

---

## 5. Caveats

- XBRL cash-flow items are year-to-date; quarters are differenced, so a restatement in a later 10-Q shifts the quarter it lands in.
- Airbnb FCF from 1Q23 is keyed from the letters because the capex tag stops in FY2022. The four FY2025 quarters sum to the letter's $4,613M.
- Q4 weighted share counts are derived (4 x FY less Q1 to Q3) because Airbnb tags only the annual figure for Q4.
- Booking's 2021 RSU withholding equals its buyback figure in XBRL, which looks like a tagging overlap; it does not affect the 2023 to 2025 figures.
- Netflix's SBC is the cash-flow add-back; its income-statement allocation tag is empty in XBRL.
- Gross bookings, and therefore take rate, are outside XBRL; Booking's are in the margin note from press releases.
