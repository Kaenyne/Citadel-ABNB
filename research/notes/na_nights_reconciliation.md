# Reconciling the choice model with the team's North America nights path

*7 Sep 2026. Script: `analysis/src/na_nights_reconciliation.py`. Outputs:
`data/processed/na_nights_reconciliation.csv`, `na_nights_decomposition.csv`,
`na_nights_lap_scenarios.csv`, `na_nights_step_history.csv`.*

## The contradiction

Two documents in this repo point opposite ways at the same quarters, and neither cites the other.

- **`research/blotnick_framework_abnb.md` §1** — the guide is a floor. Airbnb has beaten its own
  revenue midpoint 19 of 19 times and finished above the top of the range 15 of 19. Verdict: model
  next-quarter revenue at the midpoint × 1.018.
- **`research/notes/choice_nights_driver.md`** — NA at the team's pace "needs share gains or category
  adoption above the 2025 exit rate". The choice model gets US **+3.3%** for 2026 against WS10's NA
  base of **+7%**.

This note does not argue between them. It inverts the choice model: for each lever, what value would
be **required** to reach the team's NA path with everything else held at base? The disagreement then
resolves into a list of things that would have to be true.

## The answer: there is no disagreement about FY26

Base decomposition of the model's US nights growth, in percentage points of the prior-year base:

| Year | Market | Mix drift | Category adoption | Share | Total |
|---|---|---|---|---|---|
| 2026 | +0.65 | +0.86 | +2.50 | −0.70 | **+3.31** |
| 2027 | +0.41 | +0.88 | +2.54 | −1.52 | **+2.31** |

What each lever alone would have to be to reach WS10's NA base of +7.0% in 2026:

| Lever | Base | Required | Verdict |
|---|---|---|---|
| Category adoption | +4.0% | **+9.9%** | above even the 2024 implied rate (7.9%), more than double the 2025 exit rate (4.5%) |
| Product shift | 0.00 logit | **0.099 logit** | **plausible — see below** |
| US lodging demand | +1.7% | **+11.5%** | CoStar/TE says +1.7%. Not a candidate |
| Airbnb ADR growth | +3.5% | **+1.5%** | 2 pts below the team's own ADR line, and it costs the ADR line one-for-one |
| Switch rate | 5.0 | **unreachable at any value** | the ADR gap is ~0.4pp, so share has no traction to gain |
| Contestable share | 38% | **unreachable up to 95%** | ditto |

Two things fall out immediately. **This is not a substitution story** — neither the switch rate nor
the contestable share can close the gap at *any* value, because with Airbnb ADR growing roughly in
line with hotels there is almost no relative-price signal for share to respond to. And the only two
candidates left are category adoption and the product lever.

**The product lever is the answer, and management has already sized it.** On the 1Q26 call Mertz
attributed roughly **3 points of nights growth and 4 points of GBV** to three features together —
Reserve Now Pay Later, the cancellation-policy redesign and the single-fee migration. In this model
that is a share shift of **0.081 logit points**. Reaching WS10's +7% needs **0.099**. So the bucket
management has already quantified covers about **82% of the gap** between the choice model and the
team's NA base case.

The choice model was never contradicting the FY26 guide. It sets `PRODUCT_SHIFT = 0` and therefore
describes a world with no product initiatives in it. Put management's own number in the lever and the
two views agree to within a point.

## Where they actually diverge: the lap

A product launch is a **level** effect on share. It lifts nights in the year it lands and then laps.
The model's `PRODUCT_SHIFT` could only be expressed as a *permanent annual* share gain, which
silently compounds a one-off launch into perpetuity; `project()` now accepts a year-keyed shift so
the two can be told apart. That distinction is the whole trade:

| Scenario | 2026 | 2027 | 2028 |
|---|---|---|---|
| Base, no product lever | +3.3% | +2.3% | +3.7% |
| **One-off 2026 launch (+0.10 logit), then laps** | **+7.0%** | **+2.2%** | +3.7% |
| A launch of the same size every year | +7.0% | +5.9% | +7.5% |
| *WS10 NA base* | *+7.0%* | *+6.0%* | — |

FY26 lands on the guide. FY27 lands at **+2.2% against WS10's base of +6.0%** — and WS10's *bear*
case for FY27 NA is +3.0%, so the choice model's base case sits **below the team's bear case**.

Closing that gap needs a brand-new product lever of the same size in 2027, or category adoption at
9.8% against a 4.5% observed 2025 exit rate. The three features are not available for a repeat: RNPL
launched in the US in 3Q25 and laps from 3Q26 (management itself flagged "tougher comps in the back
half"), the cancellation redesign is done, and the single-fee migration completes on 13 October 2026.

## Corroboration: the disclosed NA path is a step, not a trend

If the three features are what lifted NA, the step should appear on the quarters they landed and be
absent before. WS10's NA nights estimates:

| | 1Q25 | 2Q25 | 3Q25 | 4Q25 | 1Q26 | 2Q26 | 3Q26E | 4Q26E | FY27E |
|---|---|---|---|---|---|---|---|---|---|
| NA nights y/y | +2% | +2% | **+5%** | +5% | **+8%** | +8% | +7% | +7% | +6% |

Two clean steps: +2% → +5% when RNPL launched in the US (3Q25), +5% → +8% once all three features
were live (1Q26). And the level the model produces with no product lever — **+3.3%** — is essentially
the NA run rate before any of them landed: **FY25 NA was +2.6%** (158mm / 154mm, 10-K regional
tables). The model is not missing something structural about North America. It is describing the
pre-product world accurately, and the entire acceleration is the bucket that laps.

## What this means for the pitch

- **FY26 is not the trade.** The guide is reachable, the Blotnick cushion verdict stands, and the two
  documents can be reconciled rather than adjudicated. Both should say so.
- **FY27 nights are the trade**, and the disagreement is with the team's own base case, not with
  management. WS10 already carries "FY27 nights disappoint on the three-feature lap" as a ~30%
  risk (`14_master-synthesis.md`). This analysis says it is closer to the base case: the model gets
  there mechanically, from disclosed nights and a third-party market forecast, with the product bucket
  set to management's own attribution.
- **The 5 Nov Q4 guide is the first read.** Per `catalyst_calendar.md`, the earnings sign is set by
  the nights guide, not the beat: mean absolute earnings move 12.1% with 11.3 points of excess versus
  QQQ, and every large drawdown (2 Nov 2022 −13.4%, 10 May 2023 −10.9%, 7 Aug 2024 −13.4%,
  7 Aug 2025 −8.0%) was a nights-guidance event on a revenue beat.
- **It also tells you what would kill the thesis**: a new product lever of comparable size announced
  for 2027, or evidence that category adoption is re-accelerating rather than fading. Both are
  observable before the print.

## Caveats

1. **US vs NA.** The choice model forecasts the US (145.4mm = 92% of NA's 158mm); WS10 forecasts NA.
   NA-ex-US is ~12.6mm and the global build already assumes it tracks the US, so the two are treated
   as comparable and the residual is flagged rather than modelled.
2. **The 2026 target is conservative.** 7% is WS10's *2H26* rate. FY26 NA blends a stronger 1H
   (+8%), so the true FY26 gap is larger than the one measured here, not smaller.
3. **Management's ~3 pts is a company attribution with no counterfactual**, and it is three features
   bundled, not one — `15_red-team.md` already flags people mis-citing it as RNPL alone.
4. **The model cannot separate the product bucket from category adoption.** The gap can be attributed
   to either; the arithmetic and the lap conclusion are the same either way, but the model does not
   prove which bucket it belongs in.
5. **NA quarterly nights are WS10 estimates with lo/hi bands, not disclosure.** Airbnb does not
   disclose quarterly regional nights. Only the annual regional totals in the 10-K are hard.
6. The switch rate still has no direct estimate — but note that this analysis does not lean on it.
   The conclusion holds at every value in the 2.5–10.3 grid because the ADR gap is near zero.
