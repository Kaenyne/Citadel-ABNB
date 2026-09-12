# Quarterly nights: the three-feature lap on real quarters

*7 Sep 2026. Script: `analysis/src/nights_quarterly.py`. Outputs:
`data/processed/nights_quarterly_na.csv`, `nights_quarterly_total.csv`. Builds on
`research/notes/na_nights_reconciliation.md`.*

## Why growth space, not seasonal factors

Airbnb reports **Nights and Seats Booked** — booking date, net of cancellations — while the choice
model is built on stays (hotel room-nights sold, lodging demand). The two have different seasonal
shapes: Q1 is Airbnb's largest booking quarter and the smallest US stay quarter. Converting between
them needs a booking-to-stay lag distribution, and this repo does not have one — `booking_curve_daily.csv`
is a handful of forward-calendar snapshots, not a lag distribution.

So this does not allocate an annual number across quarters with seasonal factors. It forecasts each
quarter's **year-over-year growth**, which cancels seasonality on both sides, and applies it to the
disclosed prior-year quarter. That also forecasts the booked KPI directly — the thing that is guided
and the thing consensus is set on. Consensus never enters as an input; it is a comparison column only.

Of the choice model's four driver blocks, three are annual rates, and an annual rate is exactly what a
y/y growth contribution should be: 4% category adoption means every quarter grows 4% y/y from category
adoption. The block that genuinely is quarter-specific is the product lever, and it is the whole trade.

## The lap schedule

| Feature | US live | Y/Y window | Note |
|---|---|---|---|
| Reserve Now Pay Later | 3Q25 | 3Q25–2Q26 | laps from 3Q26. Management: *"tougher comps in the back half of this year against the rollout of Reserve Now, Pay Later"* (1Q26 call) |
| Single fee, tranche 1 | Oct 2025 | 4Q25–3Q26 | software-connected hosts |
| Cancellation redesign | not disclosed | modelled with tranche 1 | **the weakest input here** |
| Single fee, tranche 2 | 13 Oct 2026 | 4Q26–3Q27 | own nights effect is −0.3% to −1.4% at payout-neutral re-pricing (`host_only_fee_history_and_elasticity.md`), so modelled at zero; −1pt in the bear case |

The product contribution is **fitted, not asserted**: observed NA y/y less the choice model's
underlying, quarter by quarter. 3Q25 is the only quarter where RNPL is live alone, so it identifies
RNPL; the step up in 1Q26 identifies the rest.

- RNPL **+2.40 pts**
- tranche-1 single fee + cancellation redesign **+2.29 pts**
- peak NA bundle in 1H26 **+4.69 pts**
- implied ex-NA bundle, from management's global ~3.0 pts **+2.30 pts**

## North America nights, y/y by quarter

| | 3Q26 | 4Q26 | FY27 |
|---|---|---|---|
| Bear | +5.6% | +2.3% | +1.3% |
| **Base** | **+5.6%** | **+3.3%** | **+2.3%** |
| Bull | +6.8% | +3.3% | +4.7% |
| *WS10 base* | *+7.0%* | *+7.0%* | *+6.0%* |

**4Q26 is the cleanest quarter Airbnb will print.** Every 2025 feature has lapped by then, and the
only 2026 feature still inside its window — single-fee tranche 2 — is nights-neutral by the fee
model. There is no bull lever available in 4Q26, which is why bull equals base there. It is the
closest thing to an unobstructed read on underlying NA demand in the whole horizon.

## Total nights, and the 5 Nov card

| | 3Q26 | 4Q26 | FY27 |
|---|---|---|---|
| Model, NA lap only | +9.9% | +8.9% | +8.2% |
| Model, bundle laps everywhere from 1Q27 | +9.9% | +8.9% | **+6.4%** |
| *WS10 base* | *+10.3%* | *+9.9%* | *+9.2%* |

**3Q26: model +9.89% (146.8mm) against a 10–12% guide and the team's own frozen 5-Nov card of +10.2% (147.2mm).** (Relabelled 12 Sep: the 10.2% was previously called "consensus"; it is the WS13/14 frozen card, and no public nights consensus exists — see `data/processed/nights_baseline_reconciliation.csv`.)

That is essentially in line, and it revises the framing from the reconciliation note. The 5 Nov print
is unlikely to miss on 3Q26 nights — and given the guide has been beaten 19 of 19 times, the base rate
says it comes in at or above the low end. **There is no near-term nights catalyst.** What is on the
card is the **4Q26 guide**, where the model sits ~1 point below the team's build, and whatever FY27
commentary comes with it.

## The swing factor is the ex-NA lap, and it is the weakest link

Whether the bundle laps only in North America or everywhere moves FY27 total nights from **+8.2% to
+6.4%** — 1.8 points, larger than the entire NA effect. Management's ~3 pts was a *global* figure, so
something lapped outside North America too; but RNPL rolled out in the US first and the international
timing is not in our evidence base.

**This is now the highest-value open question in the nights work.** The FY27 call is worth roughly
1 point of total nights if the lap is NA-only and roughly 2.7 points if it is global — against WS14's
framing of 1–3 pts of FY27 nights being ~$0.3–0.5bn of revenue. Pinning the international rollout
dates for RNPL and the cancellation redesign is a cheaper and higher-leverage piece of research than
anything else left in this workstream.

## Caveats

1. **NA quarterly nights are WS10 estimates with lo/hi bands, not disclosure.** Airbnb publishes only
   annual regional totals. Every NA number here inherits that uncertainty.
2. **The cancellation-redesign date is unknown** and is modelled on tranche 1's window. If it landed
   later, more of the bundle laps in 2027 rather than 2026 and FY27 is worse than shown.
3. **The RNPL lap is modelled as clean.** 3Q25 was a ramping quarter, so some of the lift genuinely
   recurs in 3Q26 — that is what the bull case prices.
4. **Two free parameters fitted on four observations.** This is identification by launch timing, not
   a regression, and it cannot be error-bounded in the usual way.
5. Growth-space construction assumes the annual driver rates apply uniformly across quarters within a
   year. Fine for category adoption and market growth; weaker for the relative-price term, which does
   have a quarterly shape we are not modelling.
6. Ex-NA quarters are WS10's, unchanged. This note only re-forecasts North America.
