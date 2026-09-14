# 40. The margin build by cost item: what each line is made of, what we assume, and what it says

Krish with Claude (Fable 5.1), 15 Sep 2026. Built directly after the 13-15 Sep run, which produced a calibrated top-down margin forecast
(`SYNTHESIS.md`) but allocated its cost lines rather than building them. This note is the line view. Script
`analysis/src/margin_build/40_line_build/run.py` (`py -3.13`, exit 0), outputs `data/processed/margin_build/40_line_build/`, workbook
`model/ABNB_margin_line_build.xlsx`. Every parameter is in `40_params.csv` with a source. Codex read-only check: `audit/CODEX_LINE_BUILD_CHECK.md`.

## Bottom line

1. **Built from the evidence alone, costs grow 11.5% in 3Q26 against revenue +17%, which puts the quarter at 52.4% and contradicts
   management's "margin down slightly" sentence.** The 1H26 10-Q component deltas, the 10-K S&M split, the hosting commitments and the
   per-booking support statements do not add up to a margin decline. At the guide midpoint ($4,730M) landing the sentence needs about
   $96M more cost in the quarter than the evidence supports, all of it in the two lines management has flagged: marketing ("some
   incremental investment") and AI hosting ("a material increase"). The base case takes management at its word and adds that $96M (70% to
   3Q26 marketing as a timing step, 30% to hosting as a run-rate step), because the quarterly sentence has not been sandbagged (WS22 A:
   realised gap mean -0.19pp, above the sentence in 4 of 10 quarters).
2. **3Q26 base: adj. EBITDA $2,420M, 50.4%** (Street $2,362M, 49.8%). The beat is our revenue ($4,804M vs the guide midpoint $4,730M) on
   management's own cost budget; the cost side is at the sentence, not below it. Cost growth +16.1% y/y, in line with 1H26's +15.5%.
   The evidence-only build ($2,516M, 52.4%) is the upside case if the sentence proves conservative.
3. **4Q26 $898M, 28.3%** (Street $914M, 28.9%); the Q3 marketing step does not recur in Q4 because carrying it into Q4 would put FY26 below
   the 35.5% floor at guide revenue, which management has never missed. **FY26 $5,098M, 35.7%** (floor 35.5%, Street 35.6%): the line build
   lands within $1M of the run's top-down number by a different route.
4. **FY27 $5,641M, 35.6%** against the Street's $5,766M / 36.5% and the run's $5,483M / 34.6%. The run's allocation put FY27 S&M at 23.5% of
   revenue; built from the 10-K split (marketing +15%, field +11% on top of FY26's +28%) it is 21.9%. The Street's incremental margin (43.7%)
   still needs the marketing ramp to stop; the line build's incremental margin is 34.8%.
5. **Per line, FY25 to FY27:** cost of revenue 17.0% to 17.4% of revenue (fee rate flat at 1.70% of GBV, hosting up from $224M to ~$450M
   with AI); ops & support 10.1% to 8.7% (the AI decline applies to ~19% of the line, the rest is payroll growing 8%); product development
   10.9% to 10.3%; S&M 19.4% to 21.9%; G&A ex reserves 8.1% to 6.6%. The only line that is genuinely forecastable out of sample is cost of
   revenue (backcast error -1.0% on FY25); the other four are documented spending views.

## How each line is built

| Line | FY25A | FY26E | FY27E | Formula | The view and its source |
|---|---|---|---|---|---|
| Cost of revenue | $2,086M, 17.0% | $2,432M, 17.0% | $2,758M, 17.4% | merchant fees (1.70% of GBV, quarterly factors 0.90/1.045/1.035/1.033) + chargebacks ($0.72 per booking) + hosting ($224M/yr + $30M/half step in 2H26, $330M/yr FY27, plus the AI reconciliation step) + other ($0.36 per night) | Fee rate: FY24 1.69%, FY25 1.76%, 1H26 1.68% annual-equivalent after processor rebates (1Q26 10-Q). Chargebacks +$25M y/y in 1H26 (10-Q). Hosting: $672M commitment through 2027 re-cut to $1.7bn through 2031 (10-Ks); server +$12M and RI amortisation +$12-15M in 1H26; Mertz "material increase in AI spend" |
| Operations & support | $1,237M, 10.1% | $1,306M, 9.2% | $1,384M, 8.7% | same quarter last year per booking x [v x (1 + d) + (1 - v) x (1 + g_fixed)] x bookings, v = 0.19, d = -14% (2H26) / -10% (FY27), g_fixed = 8% | v calibrated on 1H26: the line's cost per booking fell 5.1% while management's "support cost per booking" fell 10% and 16% and bookings grew 11%; so the AI metric covers about a fifth of the line (third-party contact cost, 13,000 contingent workers), the rest is payroll, customer relations and insurance |
| Product development | $1,337M, 10.9% | $1,477M, 10.4% | $1,625M, 10.3% | 2H26 +9% y/y, FY27 +8% + $30M AI tooling; quarters on the 2023-25 shares | 1H26 +12% / +10%, all payroll from average headcount (10-Q); headcount growth below FY25's +12% (2Q26 call) |
| Sales & marketing | $2,376M, 19.4% | $3,040M, 21.3% | $3,459M, 21.9% | brand + performance marketing (FY25 $1,595M; 1H26 +32% reported, 2H26 +25% plus the $67M 3Q26 reconciliation step, FY27 +15%) + field ops & policy cash (FY25 $781M; +18% / +11%) | 10-K split; 10-Q marketing +$258M and payroll +$90M in 1H26 "paid growth initiatives in emerging markets and partnerships"; 2Q26 "some incremental investment" in 2H; Sep 2026 Goldman: marketing stays elevated into next year's launches |
| G&A ex reserves | $995M, 8.1% | $996M, 7.0% | $1,045M, 6.6% | 2H26 +5%, FY27 +5%; lodging-tax reserves 0 (added back anyway) | 1H26 -5.4% on a $38M drop in non-income taxes; underlying payroll +$32M in 2Q26 (10-Q); "extremely disciplined" |
| Below EBITDA | | | | D&A $21M/q; SBC +13.2% y/y; interest income 0.876 x 3m T-bill x earning base; interest expense $37M/q; ETR 18% / 17.5%; shares -5.3M/q | M7 parameter sheet, reused unchanged |

Quarterly shares for the three spending lines are the 2023-25 means (WS02 seasonality). Bookings are nights over nights per booking (3.65
in 2026, 3.60 in 2027, continuing the 3.9 / 3.8 / 3.7 trend).

## The reconciliation, and why it is Q3-only

| Item | Value |
|---|---|
| 3Q25 margin | 50.09% |
| Sentence target used ("down slightly" = -0.5pp; "slightly" has meant 0.8-1.5pp historically) | 49.59% |
| Evidence-only 3Q26 margin at our revenue | 52.37% (cost growth +11.5%) |
| Cost budget implied by the sentence at the guide midpoint $4,730M | $2,405M cash costs, +16.1% y/y |
| Gap to the evidence build | $96M |
| Base 3Q26 after adding the gap (70% marketing, 30% hosting) | 50.37%, $2,420M |
| 2H26 marketing growth that would land the sentence on its own | +60% (3Q26 S&M +44%); not credible, hence the split with hosting |

Loading the same $96M into 4Q26 gives FY26 35.2% at our revenue and about 34.9% at guide revenue, below a floor that has been beaten by 60-140bp
every year. Management's two statements are only jointly consistent if most of the Q3 step is Q3-specific, so the marketing part is treated
as campaign timing and the hosting part as a run-rate step. FY27 marketing grows off the FY26 base including the step.

## Scenarios (FY27 margin; FY26 in brackets)

| | Cost bull | Cost base | Cost bear |
|---|---|---|---|
| Revenue bull (+15.7%) | 40.0% (36.8) | 37.7% (36.1) | |
| Revenue base (+10.9%) | 38.0% (36.4) | **35.6% (35.7)** | 32.4% (35.0) |
| Revenue bear (+5.5%) | | 32.8% (35.4) | 29.5% (34.7) |

Revenue scenarios are the WS06 v2b paths at base costs; cost scenarios are the bear/bull columns of `40_params.csv` at base revenue. Costs do
not flex with revenue in the revenue scenarios except through the drivers (GBV, bookings, nights), which is the M6 finding that Airbnb's
discretionary lines have not responded to revenue within a year.

## Sensitivities (base, FY27 margin points)

| Parameter | Shock | FY27 margin | FY27 EPS |
|---|---|---|---|
| FY27 marketing growth | +5pts | -0.67 | -$0.15 |
| Merchant fee rate | +10bp of GBV | -0.39 (evidence build -0.73) | -$0.09 |
| FY27 hosting | +$50M | -0.32 | -$0.07 |
| Sentence "slightly" | -0.5pp more | -0.30 (3Q26 -$24M) | -$0.07 |
| FY27 field ops growth | +4pts | -0.23 | -$0.05 |
| Ops fixed growth | +3pts | -0.20 | -$0.05 |
| FY27 PD growth / AI tooling / G&A growth | +2pts / +$30M / +3pts | -0.19 each | -$0.04 |
| 3m T-bill | +100bp | 0 | +$0.28 |
| RNPL: 10pts of GBV paid at check-in | | 0 | -$0.04 |

Under the reconciliation, 2H26 cost parameters are absorbed (a dearer hosting step means a smaller marketing step); their standalone effects
are in the `evidence_only_*` columns of `40_sensitivities.csv`.

## Backcast (what is evidence and what is a view)

| Test | Predicted | Actual | Error |
|---|---|---|---|
| FY25 cost of revenue from FY24-knowable rates onto FY25 drivers | $2,064M | $2,086M | -1.0% |
| FY25 ops & support from FY24 cost per booking, pre-AI trend | $1,294M | $1,237M | +4.6% |
| 1H26 cost of revenue with the base rates (in sample) | $1,224M | $1,214M | +0.8% |
| 1H26 ops per booking y/y (calibration identity) | -5.1% | -5.1% | |

Cost of revenue is forecastable from its drivers. Ops & support is forecastable to within 5% and the AI statements improve it. Product
development, marketing and G&A are spending decisions; the numbers above are views with sources, not estimates, and the M1/M6 backtests in
the run show that no driver model of those lines beats last year's value.

## Business mix

- **Regional mix** enters through the merchant fee rate (1bp of GBV per point of non-NA revenue share; 2Q26 drift +0.3pt, worth ~$3M a quarter)
  and through the revenue path's take rate. Small.
- **Experiences and Services** carry no disclosed cost; their cost sits in field operations (the ~$200M FY25 launch spend inside the $781M
  field line, growing 18% then 11%) and in the take-rate dilution already in the revenue path (seats 2-3% of revenue).
- **RNPL** has no share series in the repo. Its margin effect is below EBITDA (funds held, so interest income) and in chargebacks; the
  sensitivity above is the only quantification and is unsourced.

## Versus the run and the Street

| | Line build | Run (allocated) | Street (LSEG 11 Sep) |
|---|---|---|---|
| 3Q26 adj EBITDA / margin | $2,420M / 50.4% | $2,399M / 49.9% | $2,362M / 49.8% |
| 3Q26 S&M | $778M (+33%) | $781M (+34%) | |
| 4Q26 | $898M / 28.3% | $918M / 28.9% (= Street) | $914M / 28.9% |
| FY26 | $5,098M / 35.7% | $5,098M / 35.7% | $5,054M / 35.6% |
| FY27 | $5,641M / 35.6% | $5,483M / 34.6% | $5,766M / 36.5% |
| FY27 S&M % revenue | 21.9% | 23.5% | |
| FY27 EPS | $5.91 | $5.73 | $6.23 |

The two builds agree on 2026 and disagree on 2027 by one point, entirely in S&M: the run carried the 1H26 marketing growth rate forward in its
residual allocation; the line build applies management's stated deceleration to a base that already includes the 3Q26 step.

## Caveats

Fourteen quarters of component disclosure and one half-year of AI statements. The reconciliation takes management's Q3 sentence as the cost
budget; if the sentence is conservative (it has been beaten in 4 of 10 quarters), 3Q26 is the evidence build, $2,516M. The hosting run-rate
step ($116M a year into FY27) is the least-sourced number in the build. Nothing here is a stock view.

## For the model

`40_params.csv` is the parameter sheet; change a value and re-run. The quarterly lines feed the workbook and can replace the run's
`23_lines_quarterly.csv` allocation as the pitch's line view. The 5 Nov card keeps the run's dollar object for the beat probability (it was
backtested; this build was not) and uses this note for the composition.

## RESUME

Done. Open for Krish: (1) whether to adopt the reconciled base (sentence as budget) or the evidence build for 3Q26; (2) the hosting/AI
run-rate assumption, which the 10-Q on 5 Nov will size; (3) FY27 marketing growth, the single largest lever (+5pts = -0.67pp). To extend:
add the brand/performance split when the FY26 10-K prints, and replace the RNPL sensitivity with a share series if WS-D produces one.
