# 13. The driver model: an Excel workbook with live formulas and a Python mirror

**What this is.** Every other workstream's "For the model" parameters, assembled into one model that
runs from nights by region to a price per share, built twice so it can be checked: `model/ABNB_driver_model.xlsx`
(eight sheets, live Excel formulas, three scenarios computed in full) and `analysis/src/overnight/13_driver_model.py`
(the same arithmetic in Python). The workbook's 2,303 formula cells were recalculated by a purpose-built
evaluator and every one of 216 output checks agrees with the Python mirror to 1e-6.

**Compiled:** 6-7 Sep 2026, overnight run. Price used: **$181.94** (4 Sep 2026 close). Balance sheet:
30 Jun 2026.

---

## 1. Bottom line

**1. The base case is $15.8bn of FY2027 revenue at a 35.9% adjusted EBITDA margin, and on WS12's exit
multiples that is worth about $184 a share against a $181.94 spot.** The stock is priced for the base
case on an EBITDA lens and for the bull case on any cash-after-SBC lens. Nothing here is a call to buy.

| Base case | FY2026E | FY2027E | FY2028E |
|---|---|---|---|
| Nights & experiences booked (M) | 585.7 (+9.9%) | 637.6 (+8.9%) | 685.0 (+7.4%) |
| ADR ($) | 180.32 (+5.3%) | 185.18 (+2.7%) | 189.81 (+2.5%) |
| GBV ($M) | 105,614 (+15.7%) | 118,081 (+11.8%) | 130,026 (+10.1%) |
| Take rate, reported | 13.45% | 13.25% | 13.42% |
| **Revenue ($M)** | **14,233 (+16.3%)** | **15,842 (+11.3%)** | **17,944 (+13.3%)** |
| **Adjusted EBITDA ($M) / margin** | **5,158 / 36.2%** | **5,686 / 35.9%** | **6,701 / 37.3%** |
| SBC ($M) / % of revenue | 1,787 / 12.6% | 1,965 / 12.4% | 2,122 / 11.8% |
| GAAP operating income ($M) | 3,243 | 3,578 | 4,417 |
| Net income ($M) / EPS ($) | 3,065 / 5.28 | 3,258 / 5.76 | 3,906 / 7.06 |
| **FCF ($M) / margin** | **5,129 / 36.0%** | **5,420 / 34.2%** | **6,197 / 34.5%** |
| SBC-adjusted FCF ($M) | 3,342 | 3,455 | 4,075 |
| Diluted shares, period end (M) | 580.3 | 566.0 | 553.0 |
| **FCF per share ($)** | **8.84** | **9.58** | **11.21** |
| **SBC-adjusted FCF per share ($)** | **5.76** | **6.10** | **7.37** |
| Net cash ex float ($M) | 9,383 | 10,116 | 11,570 |

| Bear case | FY2026E | FY2027E | FY2028E | | Bull case | FY2026E | FY2027E | FY2028E |
|---|---|---|---|---|---|---|---|---|
| Revenue ($M) | 13,933 (+13.8%) | 14,181 (+1.8%) | 14,968 (+5.5%) | | Revenue ($M) | 14,527 (+18.7%) | 17,421 (+19.9%) | 20,874 (+19.8%) |
| Adj. EBITDA ($M) / margin | 4,812 / 34.5% | 4,027 / 28.4% | 3,812 / 25.5% | | Adj. EBITDA ($M) / margin | 5,496 / 37.8% | 6,620 / 38.0% | 7,932 / 38.0% |
| FCF ($M) | 4,555 | 3,531 | 3,122 | | FCF ($M) | 5,660 | 6,543 | 7,593 |
| FCF per share ($) | 7.85 | 6.17 | 5.53 | | FCF per share ($) | 9.76 | 11.63 | 13.89 |
| SBC-adj. FCF per share ($) | 4.69 | 2.52 | 1.38 | | SBC-adj. FCF per share ($) | 6.76 | 8.35 | 10.38 |
| EPS ($) | 4.56 | 3.07 | 2.39 | | EPS ($) | 5.95 | 7.47 | 9.46 |

The bull's uncapped FY27/FY28 margins are 41.7% and 46.0%; both are cut to WS07's 38% realistic ceiling
(BKNG's five-year EBITDA-proxy range is 30.0-37.4%). A bull that needs a 46% margin is not a bull, it
is a broken model, and saying so is more useful than printing the number.

**2. Price per lens, on FY2027E unless stated.** Multiples from WS12; cost of equity 10.5% from WS09.

| Lens | Multiple (bear / base / bull) | Bear | **Base** | Bull |
|---|---|---|---|---|
| EV / adj. EBITDA | 13.5 / 16.5 / 18.5x | $110 | **$184** | $238 |
| EV / FCF | 11.3 / 14.3 / 17.3x | $85 | **$155** | $221 |
| P / SBC-adjusted FCF | 15 / 19.5 / 24x | $38 | **$119** | $200 |
| P / earnings proxy | 15 / 19.5 / 24x | $46 | **$112** | $179 |
| EV / adj. EBITDA, FY2028E | same | $105 | **$221** | $294 |
| DCF, 10-yr fade to 3%, CoE 10.5% | - | $79 | **$185** | $285 |
| **Football field (low / mean / high)** | | **$38 / $77 / $110** | **$112 / $163 / $221** | **$179 / $236 / $294** |
| Implied upside vs $181.94, mean | | **-58%** | **-11%** | **+30%** |
| *Memo: on the 5 Sep 18/22/25.5x multiples* | | *$142* | *$239* | *$320* |

**3. Reverse DCF is unchanged, and that is the point.** At 10% cost of equity and 3% terminal growth,
$181.94 discounts **7.50%** a year FCF growth for ten years on reported FCF and **13.32%** on
SBC-adjusted FCF - identical to the 5 Sep note's 7.497% / 13.322%, because the convention was kept
deliberately identical. At the model's own 10.5% cost of equity the numbers are 8.51% and 14.42%. The
base case grows FCF 5.7% in FY27 and 14.3% in FY28 (a 9.9% CAGR), so **the stock is priced roughly at the
base case on reported cash flow and above the bull case on cash flow after SBC.** That gap is the whole
debate and it has not moved in two days of work.

**4. What changed versus the 5 Sep driver-model note, and why.**

| | 5 Sep | This model | Why |
|---|---|---|---|
| FY27 base revenue | $15,959M (+12.3%) | $15,842M (+11.3%) | WS10's regional nights build (+8.9% after WS11's regulatory drag) replaces a single +9% assumption; WS06/WS07's +2.5% ADR ex-FX replaces +3%; WS05's lagged FX schedule puts -0.6pp on FY27 revenue where the old model had zero. Partly offset by +$197M of new-business revenue outside GBV x take rate |
| FY27 base margin | 36.5% | 35.9% | Same WS07 lever stack, less 0.38pp of AI referral cost (WS11 low case). Ex the AI line the model is at 36.3%, between WS07's 36.6% and WS05's 36.4% |
| FY27 base FCF | $5,825M | $5,420M | The 5 Sep model set FCF = 100% of EBITDA. This one runs WS07's bridge (interest, cash taxes, unearned fees, working capital, capex), giving 95% conversion |
| FY27 net cash | $12,358M | $10,116M | **Correction.** The earlier path did not subtract RSU tax withholding, which is roughly $0.7bn a year of real cash |
| FY27 base price, EV/EBITDA | $248 | $184 | Bridge: -$55 from the multiple (22x to WS12's 16.5x), -$5 from lower EBITDA, -$4 from lower net cash. **The multiple is 86% of the change.** At 22x this model still gives $239 |
| FY27 bear revenue / margin | +4.3% / 33.8% | +1.8% / 28.4% | The bear now stacks WS10's regional demand bear, WS05's strong-dollar path (-2.6pp on FY27 revenue), a -15bp take rate and WS11's high AI referral cost (2.28% of revenue = 2.3 margin points). Four separate tails; see "Choices made" |
| FY27 bull margin | 39.8% | 38.0% (41.7% uncapped) | Capped at WS07's stated realistic ceiling |
| FY28 base revenue growth | +11.0% | +13.3% | An FX artefact, not a demand call: FY27 carries a -0.6pp revenue FX drag and a -0.8pp FX timing wedge, both of which lap in FY28. See section 3 |
| Regional build, quarterly cadence, hotels/Experiences | listed as "not in the model" | in the model | WS10 and WS11 supplied them |

**5. Against the Street** (`Street` sheet; consensus from WS04, 3-4 Sep 2026). We are **above** the Street
on revenue and **below** on FY27 EPS, which is the honest version of the pitch: more revenue, more SBC,
more AI cost, fewer shares retired than the sell side assumes.

| | Street | Our base | Delta |
|---|---|---|---|
| 3Q26 revenue | $4,740M (Zacks, 7 est.) | $4,801M | +1.3% |
| 4Q26 revenue | $3,200M (10 est., 3,050-3,700) | $3,145M | **-1.7%** |
| FY26 revenue | $14,100M / $14,160M | $14,233M | +0.9% / +0.5% |
| FY26 adj. EPS | $5.23 / $5.28 | $5.28 | +1.0% / 0.0% |
| FY26 FCF | $5,350M (S&P Global) | $5,129M | -4.1% |
| FY27 revenue | $15,730M / $15,760M | $15,842M | +0.7% / +0.5% |
| FY27 adj. EPS | $6.02 / $6.14 | $5.76 | **-4.3% / -6.2%** |

---

## 2. The input table

Every input sits on the workbook's `Inputs` sheet in a yellow cell with its source string, laid out
bear / base / bull with an `Active` column driven by the selector in `Inputs!$B$3`. Full detail is in
`model/assumptions.md`, section "Overnight run 6-7 Sep 2026". Summary of what came from where:

| Block | Rows | Supplied by |
|---|---|---|
| A. Valuation and control | 15 (price, net cash, shares, cost of equity, terminal growth, DCF start growth, four exit multiples, withholding, price growth, new-business margin, margin cap, fade period) | WS09, WS12, plus the 5 Sep model's conventions |
| B. Annual drivers, FY26/27/28 | 21 per year x 3 years = 63 (take rate, six cost levers, add-backs, SBC, interest, cash tax, unearned fees, effective tax, AI referral, new business, buybacks, regulatory multiplier, capex, working capital, D&A) | WS07 supplies 21 of them verbatim; WS02 the tax rate; WS11 the AI and new-business lines |
| C. Quarterly drivers, 3Q26-4Q27 | 7 per quarter x 6 quarters = 42 (four regional nights growth rates, ADR ex-FX, revenue FX, ADR FX) plus two quarterly margins | WS10 (regional), WS06/WS07 (ADR ex-FX), WS05 and WS08 (FX), WS07 (2026 quarterly margins) |
| D. Regulatory nights drag | 12 (year x region) | WS11 |
| E. Documented alternatives | 11 rows of "the value that lost", with why | see section 6 |

Historical anchors sit on the `History` sheet: 22 quarters of KPIs and cost lines (1Q21-2Q26) from WS02's
panel, and 40 derived anchors (FY2025 totals, 1H2026 totals, the four prior-year quarters the forecast
grows off, regional nights shares, seasonal margin spreads, LTM figures) written as formulas over that
table, so correcting a historical cell propagates.

---

## 3. Seasonality and FX mechanics

**Seasonality is derived from history, not assumed.** Two places:

*Nights and revenue.* The model does not allocate an annual total across quarters. Each forecast quarter
grows off the **same quarter a year earlier** by region, so seasonality is inherited from the actual
base. FY2026 = 1H26 actual + 3Q26 + 4Q26; FY2027 = the sum of its four quarters; FY2028 is the only
annual-only step. A memo row on the `Revenue` sheet compares each forecast quarter's implied share of
full-year nights against the 2023-2025 mean (26.9% / 25.5% / 25.1% / 22.5%) as a sanity check.

*Margin.* 1Q26 (19.4%) and 2Q26 (35.0%) are actual; 3Q26 (49.0%) and 4Q26 (32.5%) come from WS07's 5 Nov
card. Those four reproduce the FY2026 margin exactly on a revenue weighting, which is a real check on
WS07's card. Each 2027 quarter then takes the FY2027 margin **plus its own 2026 spread**, with a constant
correction so the revenue-weighted quarters reproduce the FY2027 margin. Using the 2026 spread rather
than the 2023-2025 mean matters: the mean spread would put 3Q27 at 52.5% against a 3Q26 of 49.0%, an
implausible jump. On the 2026 template 3Q27 is 48.8%, continuous with the card.

**FX has two effects and they are not the same size.** This is the single most important mechanical
change versus the 5 Sep model, and it comes straight out of WS05.

- **ADR FX** is contemporaneous: reported ADR moves with the spot basket in the same quarter. WS05's
  broad-USD fit (`ADR FX = 0.52 - 0.72 x USD y/y`, re-estimated by WS08 at r 0.96 and walk-forward
  tested at 0.44x the naive error) gives **+0.80pp for 3Q26**, against +1.3pp in 2Q26 and +5.0pp in 1Q26.
- **Revenue FX lags one to two quarters**, because revenue is recognised at check-in while GBV is booked
  earlier and hedges roll. WS05's fit is `revenue FX = -0.640 + 0.413 x mean(EUR/USD y/y at t-1, t-2)`,
  n 17, r 0.80. The company guided **+3.0pp** for 3Q26; the fit says +2.19pp, inside its own ±0.8pp band.
- The model therefore carries an explicit **FX timing wedge = (1 + revenue FX) / (1 + ADR FX) - 1**.
  GBV is built on ADR FX; revenue is GBV x take rate x (1 + wedge). The wedge is +2.2pp in 3Q26, -0.1pp
  in 4Q26 and about -0.8pp on average through 2027. This is exactly the gap the 5 Sep note flagged and
  could not model ("management's own ex-FX ADR is higher than this split's because the revenue FX effect
  is larger than the ADR FX effect"). It is also why the model reports two take rates: the **assumed**
  rate (prior-year quarter plus the lever, 13.34% FY26 / 13.37% FY27) and the **implied reported** rate
  (core revenue / GBV, 13.45% FY26 / 13.25% FY27). The 20bp swing between them is FX timing, not
  monetisation, and it is the reason FY2028 revenue growth (+13.3%) is above FY2027's (+11.3%).

**The FX schedule, base case, pp:**

| | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 | FY27 |
|---|---|---|---|---|---|---|---|
| Revenue FX (lagged fit) | +3.00 | -0.43 | -1.03 | -0.80 | -0.61 | -0.07 | **-0.63** |
| ADR FX (contemporaneous fit) | +0.80 | -0.36 | -0.40 | +0.02 | +0.66 | +0.49 | +0.19 |
| Timing wedge | +2.18 | -0.07 | -0.63 | -0.82 | -1.26 | -0.56 | -0.82 |

Bear uses WS05's strong-dollar path (FY27 revenue FX -2.6pp), bull the weak-dollar path (+0.9pp).
**4Q26 is the same in all three cases (-0.43pp) because 84% of that quarter's driver is already realised** -
a rare piece of near-certainty and the sharpest thing to say on 5 November.

---

## 4. The quarterly path, 3Q26 to 4Q27 (base case)

| | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| Nights (M) | 147.2 | 134.0 | 170.0 | 161.4 | 160.3 | 145.9 |
| Nights y/y | +10.2% | +9.9% | +8.8% | +8.8% | +8.9% | +9.0% |
| ADR ($) | 177.84 | 171.91 | 190.72 | 188.36 | 183.49 | 177.08 |
| ADR y/y (of which ex-FX) | +3.8% (3.0) | +2.6% (3.0) | +2.1% (2.5) | +2.5% (2.5) | +3.2% (2.5) | +3.0% (2.5) |
| GBV ($M) | 26,185 | 23,029 | 32,424 | 30,404 | 29,410 | 25,843 |
| Take rate, assumed | 17.88% | 13.62% | 9.17% | 13.26% | 17.88% | 13.62% |
| **Revenue ($M)** | **4,801** | **3,145** | **2,992** | **4,049** | **5,257** | **3,544** |
| Revenue y/y | +17.2% | +13.2% | +11.7% | +12.2% | +9.9% | +12.7% |
| Adj. EBITDA margin | 49.0% | 32.5% | 19.2% | 34.8% | 48.8% | 32.3% |
| Adj. EBITDA ($M) | 2,353 | 1,022 | 573 | 1,407 | 2,563 | 1,143 |

Bear 3Q26 revenue $4,632M (+13.1%), bull $4,977M (+21.5%). Bear 4Q26 $3,015M (+8.5%), bull $3,264M (+17.5%).

Two features worth arguing about on a slide. **3Q27 revenue growth (+9.9%) is the low point of the
path**, and it is entirely the FX lap: 3Q26 carries +3.0pp of revenue FX and 3Q27 carries -0.6pp. Nights
growth in that quarter is +8.9%, in line with every other quarter. **4Q27 (+12.7%) then re-accelerates**
for the same reason in reverse. Anyone reading this model as a demand call in 2027 is reading the dollar.

---

## 5. Choices made where workstreams disagreed

The prompt asked for these to be listed. Each losing value is on the `Inputs` sheet, section E, so a
teammate can swap it in.

1. **FX: WS05's lagged schedule beats the contemporaneous FX in WS10 and the 5 Sep model.** WS05's fit is
   estimated (n 17, r 0.80) and validated against a company-quantified number; the contemporaneous
   version is an assumption. FY27 base revenue FX = **-0.63pp**, not 0. *Alternative on the sheet: 0.0pp.*
2. **3Q26 revenue FX = the guided +3.0pp, not the fit's +2.19pp.** Management quantified it and the fit's
   error band covers the guide. *Alternative: +2.19pp.*
3. **ADR FX uses the broad-USD fit, not the EUR/USD one.** WS08 re-estimated the broad-USD version
   independently and walk-forward tested it; the EUR version would put 3Q26 ADR FX at -1.27pp against
   WS08's headline +0.80pp. This affects the ADR/GBV display only, since revenue runs off the revenue-FX
   line. *Alternative: FY27 ADR FX -0.11pp.*
4. **FY27 nights: WS10's regional rates, weighted on base-period nights shares and net of WS11's regulatory drag, give +8.9%** (WS10 publishes +9.2% gross on its own weighting) -
   between WS07's and WS05's +8.5% and WS10's gross number. WS10's is the only bottom-up build and the
   only one with external benchmarks (BKNG room-night acceleration r 0.88-0.91). *Alternatives listed:
   +8.5%.*
5. **FY27 ADR ex-FX = +2.5%, not WS10's +3.0%.** WS06 and WS07 independently arrive at +2.5%, and WS06
   shows the bedroom-mix half of ADR growth decaying while hotel pricing decelerates (CoStar 2027 ADR
   +1.6%). Two workstreams against one. *Alternative: +3.0%.*
6. **FY27 revenue growth lands at +11.3%**, against WS10's +12.4%, WS07's +11.2% and WS05's +10.3%. It is
   not an average - it is the consequence of choices 1, 4 and 5 plus WS11's new-business line.
   *All three alternatives are on the sheet.*
7. **FY27 margin comes from WS07's lever build (35.9% after the AI cost, 36.3% before), not WS05's
   probability-weighted 36.4%.** WS05's number is an overlay on WS07's own base; WS07's is bottom-up by
   cost line. The gap is 0.1-0.5pp. *Alternative: 36.4%.*
8. **Exit multiples: WS12's 13.5 / 16.5 / 18.5x, not the 5 Sep 18 / 22 / 25.5x.** WS12 triangulates three
   independent methods (time series, cross-section, intrinsic) and all three land below 22x. The 5 Sep
   set simply held today's multiple. This single choice is $55 of the $64 fall in the base-case price.
   *Alternative: 18/22/25.5x, shown as a memo row on the `Valuation` sheet.*
9. **The other three multiples are the 5 Sep set rescaled by WS12's same 0.75x haircut** (EV/FCF
   15/19/23x becomes 11.3/14.3/17.3x; the two price multiples 20/26/32x become 15/19.5/24x). WS12 only
   recommended an EBITDA multiple; applying its haircut uniformly is a derivation, not a source, and is
   labelled as such.
10. **Cost of equity 10.5%, the low end of WS09's 10.5-11.5%, rather than WS12's 10.3%.** WS09 estimated
    beta across several windows and factor models (1.16-1.32) and is the more thorough estimate.
    *Alternative: 10.3%.*
11. **AI referral cost: WS11's low case (0.38% of FY27 revenue) in the base, high (2.28%) in the bear,
    zero in the bull.** WS11's own evidence - Booking put AI tools at under 1% of room nights in 2Q26, and
    its Third Bridge expert sees no EBITDA impact for 12-24 months - puts the mid case beyond 2027.
    *Alternative: the mid case, 1.14%.*
12. **New business adds sponsored listings and Services only ($197M incremental in FY27 base), not WS11's
    full incremental column ($412M).** Hotel and Experiences nights are already inside "nights and
    experiences booked" and therefore already inside the nights build; ads and Services are not.
    *Alternative: the full column.*
13. **Regulation is applied as a nights drag by region (WS01's instruction), at 1.67x WS11's median,
    which is WS11's mean.** *Alternative: 0.75% of FY27 revenue applied globally - the same loss, stated
    differently.*
14. **The bear does not use WS11's p95 regulatory tail (6.1x the median).** Stacking a p95 regulatory
    outcome on WS10's demand bear, WS05's strong-dollar bear and WS11's high AI cost would be
    quadruple-counting the tail; it pushed FY27 bear revenue to +0.5%, below every workstream's own bear.
    At the mean it is +1.8%, against WS07's +3.7% and WS10's +4.9%; the remaining gap is the AI referral
    cost, which WS07's bear does not carry. *Alternative: the p95 multipliers, 6.10 / 6.08 / 4.56.*
15. **A 38% cap on the adjusted EBITDA margin**, which is WS07's own stated realistic ceiling. It binds
    only in the bull, from FY27. The uncapped figure is shown on the `Costs` sheet immediately above.
16. **DCF start growth is an input (0% / 9% / 15%), not the model's own FY28 FCF growth.** Unclipped, the
    bear starts a ten-year fade at -21% and the bull at +26%, which produces $46 and $462 - extrapolation
    artefacts, not valuations. The base 9% is a round number just under the model's own FY2026-FY2028 FCF CAGR of 9.9%.
17. **The reverse DCF keeps the 5 Sep convention** (constant growth for ten years, then terminal) even
    though the forward DCF uses a linear fade, so the two notes' implied-growth numbers are comparable.
    They agree to 0.01pp.

---

## 6. Corrections to existing work

- **`data/processed/abnb_valuation_scenarios.csv` overstates net cash.** Its FY27E base $12,358M does not
  subtract RSU tax withholding, which ran $561M in FY2025 and is projected at $688M in FY2027. Rolling
  the 30 Jun 2026 actual ($9,593M) forward with FCF less buybacks **and** withholding gives $10,116M.
  Worth about $4 a share on every EV-based lens.
- **The same file sets FY26-FY28 FCF equal to adjusted EBITDA in the base case** (100% conversion). WS07's
  bridge gives 99% / 95% / 92%; FY2025 actual was 107% and falling as the guest float stops growing.
- **WS10 weights regional nights growth by the forecast quarter's share rather than the base quarter's.**
  For 3Q26 that gives +10.29% where base-period weights give +10.47%; the difference is 0.2pp and does not
  change any conclusion, but the base-period weight is the correct one and is what this model uses.
- **WS10 adds the FX contribution to GBV growth additively** (13.60 + 3.00 = 16.60%). Compounding gives
  17.01%. On 3Q26 revenue that is $19M.
- **WS07's FCF bridge needs an "other income/(expense)" line to tie to the FY2025 actual.** Without the
  -$112M of FY2025 other expense the bridge produces $4,725M against the reported $4,613M. The line is in
  this model's `Cash` sheet (zero in every forecast year, as in WS07's projection) and the FY2025A column
  now ties exactly.
- **Not an error, but worth flagging:** WS07 holds D&A and other add-backs at 0.9% of revenue while the
  FY2025 actual was 1.32% ($161M). That is a deliberate 0.42-point margin drag in FY2026 and it appears in
  WS07's own bridge; it is carried here unchanged so the two models reconcile.

---

## 7. What the model cannot do yet

1. **It has no reaction function.** WS03, WS04, WS09 and the 5 Sep note between them ran hundreds of tests
   and nothing survived leave-one-out: the day-one move regresses on the beat with R² 0.04. Putting a
   reaction equation in the workbook would be dressing a negative result as a feature. The `Card_5Nov`
   sheet carries the base rates instead.
2. **FY2028 has no regional build and no FX view.** WS10 stops at FY27 and WS05 at 4Q27. FY2028 runs off a
   single total-nights lever and zero FX in every case, which is why its revenue growth is mechanically
   flattered by the FY27 FX drag lapping.
3. **New businesses are a revenue line, not a segment.** Hotels and Experiences are inside the nights
   build at platform economics; only ads and Services are broken out, and their 70% incremental margin is
   an assumption with no disclosure behind it. There is no hotel take rate, no Experiences ADR, no
   Services unit economics, because none is disclosed.
4. **No balance sheet below net cash, and no float model.** Funds held for clients ($12.2bn) is excluded
   from net cash and does not roll. WS08's finding that the funds-held-to-GBV gap is widening on RNPL is a
   diagnostic in the note, not a line in the model.
5. **The bear's 1Q27 margin (13.3%) is arithmetically fine and economically odd.** Seasonal spreads are
   applied additively, so at a depressed full-year margin the weakest quarter goes to a place the company
   would not actually let it reach - management would cut marketing. There is no cost-response function.
   WS05's scenarios have one (a "cost response share"); it is not in this model.
6. **Buybacks are exogenous and exceed the authorisation.** $3.4bn was left in Aug 2026; the base case
   spends $4.2bn in FY26 and $4.0bn a year after. A top-up is assumed, not modelled.
7. **The share-count path assumes RSUs are issued at market with 35% withheld and buybacks execute at a
   price rising 5% a year.** Both are conventions inherited from the 5 Sep model. They reproduce
   `abnb_valuation_scenarios.csv`'s 581 / 567 / 554, which is the point.
8. **No Monte Carlo.** WS07 ran 40,000 correlated draws for the path-to-40% question; this model runs
   three discrete scenarios plus a 7 x 7 x 9 deterministic grid (`13_scenario_grid.csv`, on the
   `Valuation` sheet). Probability-weighting the three cases is a synthesis decision, not a model one.
9. **It cannot be recalculated by LibreOffice on this machine.** LibreOffice headless is not installed and
   the `formulas` package is unavailable, so `analysis/src/overnight/13_xlsx_eval.py` was written to walk
   the formula graph instead. It supports exactly the syntax the builder emits and raises on anything
   else. All 2,303 formula cells evaluate; 216 named outputs match the Python mirror to 1e-6
   (`13_reconciliation.csv`). The `Recon` sheet repeats the same check as live Excel formulas, so opening
   the file in Excel re-verifies it independently.

---

## 8. For the 5 Nov card

The `Card_5Nov` sheet holds this live. Model columns are formulas; the bars are constants with sources.

| Line | Bear | **Base** | Bull | Company guide | Street / cushion bar |
|---|---|---|---|---|---|
| 3Q26 revenue ($M) | 4,632 | **4,801** | 4,977 | $4,690-4,770 (+15-17%) | Street $4,740; WS02 cushion-adjusted $4,815; WS04 base-rate $4,821-4,845 |
| 3Q26 revenue y/y | +13.1% | **+17.2%** | +21.5% | +15% to +17% | +15.8% (Street) |
| 3Q26 nights (M) | 144.2 | **147.2** | 150.4 | "low double digit" | WS04 derived bar 144-146m; WS02 cushion 150-154m |
| 3Q26 nights y/y | +7.9% | **+10.2%** | +12.6% | 10-12% | WS08 nowcast +12.1% (9.3-14.9); naive +10.3% |
| 3Q26 ADR ($) | 176.11 | **177.84** | 179.57 | "up moderately" | - |
| 3Q26 ADR y/y | +2.8% | **+3.8%** | +4.8% | - | WS08 +4.05% |
| ... of which FX | +0.80pp | **+0.80pp** | +0.80pp | - | WS05/WS08, r 0.96 |
| 3Q26 GBV ($M) | 25,391 | **26,185** | 27,013 | "mid teens" | WS02 $26.6-27.2bn |
| 3Q26 take rate | 17.83% | **17.88%** | 17.93% | "relatively in line y/y" | 17.9% ± 0.2pt; 3Q25 was 17.88% |
| 3Q26 adj. EBITDA margin | 48.3% | **49.0%** | 50.2% | "down slightly" from 50.1% | WS02 48.7-50.0% |
| 3Q26 adj. EBITDA ($M) | 2,237 | **2,353** | 2,498 | up y/y | WS04 derived $2,300-2,400 |
| **4Q26 revenue ($M)** | 3,015 | **3,145** | 3,264 | no guide yet | **Street $3,200 (3,050-3,700)** |
| 4Q26 revenue y/y | +8.5% | **+13.2%** | +17.5% | - | WS05 expects a +11-13% guide |
| 4Q26 nights y/y | +7.0% | **+9.9%** | +12.3% | - | accelerating vs Q3 is the bull tell |
| FY26 revenue ($M) | 13,933 | **14,233** | 14,527 | "at least mid teens" | Street $14,100-14,160 |
| FY26 adj. EBITDA margin | 34.5% | **36.2%** | 37.8% | "at least 35.5%" | WS02 cushion 36.1-36.9% |

**Four things this model says about the print that the individual workstreams do not.**

1. **Our 4Q26 revenue is 1.7% below the Street and the reason is entirely FX.** The Street's $3,200M
   implies +15.2% y/y. Ours implies +13.2%, of which the revenue FX line contributes -0.4pp against
   +3.0pp in Q3. If management guides Q4 to +11-13% - which is what WS05 expects and what our base is -
   the Street's number falls, and the risk is that the sell side reads a mechanical FX lap as a demand
   deceleration. **Have the FX bridge ready before the guide, not after.** And note that the FX line for
   4Q26 is identical in all three of our cases, because 84% of it has already happened.
2. **The base case beats the guide midpoint by 1.5% and the Street by 1.3%** - below the post-2022 median
   beat of 2.15% versus the midpoint. That is deliberate: WS02 shows the cushion has halved to 1.79%, and
   the last two third quarters beat by only 0.9%. A print at $4,850M (the full-history cushion) would be
   a genuine upside surprise on this model; $4,740-4,780M would not be a miss.
3. **The single most informative line in the release is 3Q26 brand-and-performance marketing.** WS07's
   sensitivity, carried into this model's `bpm_cash` lever: FY26 margin is 37.0% at +17% growth, 36.2% at
   +25% (our base), 35.5% at +31%. 1H26 ran +32%. A Q3 print above +28% puts the FY at the 35.5% floor;
   below +20% is the first evidence the reinvestment cycle is easing and is worth more than any AI
   datapoint.
4. **Check the take rate against 17.88% but read it through the wedge.** Our base has the *assumed* take
   rate flat at 17.88% and the *implied reported* rate at 18.27%, the difference being +2.2pp of FX
   timing. A reported 3Q26 take rate near 18.3% is therefore consistent with a completely flat
   monetisation rate. Do not call the single fee a success on that number alone.

Also on the sheet, for the day itself: WS08's demand index at -0.325 for 3Q26 to date (up from -0.509 in
2Q26, but only 4 of 7 components populated and no composite beat a naive baseline walk-forward); WS08's
funds-held backlog nowcast of +12.0% revenue growth with its RNPL confound stated; WS09's 7.07% mean
absolute day-one move and -3.7% 20-session drift; the nights-acceleration sign rule at 17 of 21; WS12's
finding that the day-one move correlates +0.97 with the multiple change and +0.09 with the estimate
change, and that one turn of EV/NTM EBITDA is $9.11 a share.

---

## 9. Files written and how to run it

```
py -3.13 analysis/src/overnight/13_driver_model.py      # rebuilds every output below
```

- `model/ABNB_driver_model.xlsx` - Inputs / History / Revenue / Costs / Cash / Valuation / Street /
  Card_5Nov / Recon. 2,303 live formulas. Yellow = input, green = key output. Scenario selector at
  `Inputs!$B$3`; all three scenarios are computed in full regardless.
- `analysis/src/overnight/13_driver_model.py` - inputs, engine, valuation, CSV outputs.
- `analysis/src/overnight/13_excel_builder.py` - the workbook builder.
- `analysis/src/overnight/13_xlsx_eval.py` - the formula evaluator used to verify it.
- `data/processed/overnight/13_model_quarterly.csv` - 18 rows (3 scenarios x 6 quarters), 34 columns.
- `data/processed/overnight/13_model_annual.csv` - 9 rows, 59 columns.
- `data/processed/overnight/13_valuation_summary.csv` - 57 rows: 33 price rows plus 24 reverse-DCF rows.
- `data/processed/overnight/13_scenario_grid.csv` - 441 rows: FY27 revenue growth x margin x multiple.
- `data/processed/overnight/13_reconciliation.csv` - 216 checks, all `ok`, max |delta| 0.000000.
- `model/assumptions.md` - appended section "Overnight run 6-7 Sep 2026", 30 driver rows with sources.
