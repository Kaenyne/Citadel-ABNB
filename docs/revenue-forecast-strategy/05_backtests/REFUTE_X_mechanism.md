# REFUTE X — mechanism lens

Agent: Codex ref_a_power (X mechanism assignment) · 2026-09-12 · branch `codex/lane1-full`.

## Preregistered refutation protocol

Written before independent calculations. The assignment specifies no statistical pass line; the required outcome is an adversarial verdict. The original exact claim is: **“The regional FX reconstruction does not yet justify replacing B4: no measured Airbnb origin–destination currency matrix is identified, and the current reconstruction has 0/14 W1 and 0/10 W2 point-in-time guide observations.”** Attempt to overturn that complete sentence using the note and permitted input datasets only. Independently test Q3/Q4 sign and fading-tailwind conclusions, translation units versus ADR slopes, origin/destination exposure, applying the hedge exactly once, and predictor-rescaling invariance. A deterministic reconstruction, a tourism proxy or an unvalidated slope normalization will not be silently substituted for measured Airbnb currency exposure or a historical PIT forecast. At least five numbered attacks and one verdict exactly `survived`, `refuted`, or `partial` will follow. No X package code or derived output table will be read; parent owns board, scorer and git.

## Verdict

**survived.** The original complete sentence remains supported. Public tourism counts do not measure Airbnb nights by origin, destination and settlement currency; current scenario construction adds unmeasured mappings. Its September-12 reconstruction stamp is later than every historical W1/W2 guide. The supplied FX scenarios preserve a positive Q3/Q4 tailwind that fades into Q4, but their exact levels and the ex-FX residual depend on the chosen translation convention. A simple rescaling can also reproduce the headline change in fitted slope without changing any prediction. None of these mechanisms establishes a measured, historically validated replacement for B4.

## Results: independent arithmetic and mechanism checks

Inputs were the package note, its source-controlled `public_inputs.csv`, the supplied annual regional table, quarterly ADR table, judgement currency basket, ADR-pass-through slopes, hedge-forward table, and official releases linked by the note. No X code or X derived output CSV was inspected. Scenario FX numbers below are independently recombined from the note's displayed inputs; this is not an independent re-estimation of the prohibited model. All scenario rows have zero PIT forecast observations.

### Public evidence does not identify the currency matrix

| Source partition | Input rows n | Count denominator | Independent arithmetic | Measured Airbnb currency cells n |
|---|---:|---:|---|---:|
| NTTO 2025 actual origins | 11, including residual | 68,288,000 visitors | Named origins 77.192%; mapped currency labels 74.905% | 0 |
| JNTO July 2026 regional-origin partition | 5, including residual | 3,442,100 arrivals | Classified origins 95.116%; mapped currency labels 43.732% using seven separate currency detail rows plus Mexico | 0 |
| Eurostat 2025 domestic/foreign partition | 2 | 951,611,862 platform nights | Foreign 591,704,241 / total = 62.179% | 0 |

The [NTTO official report](https://www.trade.gov/sites/default/files/2026-05/NTTO-Spring-Forecast-2026.pdf) confirms the 2025 actual total and named-country counts. The [JAPAN NATIONAL TOURISM ORGANIZATION release](https://www.jnto.go.jp/en/news/20260819.pdf), dated 19 August 2026, confirms the July total and origin counts; 2026 values are preliminary. These releases do not give Airbnb bookings or payment currencies. The Eurostat arithmetic reproduces the local input extract; fresh verification of its [official API response](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tour_ce_omr?geo=EU27_2020&time=2025&indic_to=NGT_SP&unit=NR) was unavailable in this session.

The JNTO currency-detail rows overlap its regional-origin partition. Adding both gives 4,924,300, not 3,442,100 arrivals. They must be used as alternate classifications, not additional visitors. The correct partition reproduces the note. The NTTO Canada count alone is 23.458% of US inbound visitors: those trips cross countries but remain inside the analytic NA region. Therefore country-cross-border share cannot be substituted for the off-diagonal share of a four-region matrix.

The raw currency basket sums to one for all four regions, but its own rows call the weights judgement. Sum-to-one supplies a normalization constraint, not evidence about settlement currency. Observationally identical visitor counts can coexist with different USD, origin-currency or destination-currency settlement choices. Airbnb-specific currency exposure is not identified by these counts. A complete O-D matrix is not the only possible route to a better consolidated FX model—directly measured currency revenue shares could suffice—but these inputs provide neither measurement.

### Q3/Q4 direction and precision

The four displayed midpoint Q3 regional gross contributions sum independently to **3.879pp**. Deducting the supplied hedge once gives **3.669pp**, or **0.669pp above** management's approximately 3pp after-hedge assumption. The individually rounded after-hedge regional cells sum to 3.668pp; the 0.001pp difference is display rounding. The displayed regional deviations sum to 0.669pp.

| Convention and fee mix | Scenario n | PIT n | Q3 after hedge, pp | Q4 after hedge, pp | Q4−Q3, pp |
|---|---:|---:|---:|---:|---:|
| Unit translation, guest share 0 | 1 | 0 | 3.4 | 1.5 | −1.9, rounded |
| Unit translation, guest share 0.5 | 1 | 0 | 3.7 | 1.6 | −2.1, rounded |
| Unit translation, guest share 0.82456 | 1 | 0 | 3.8 | 1.7 | About −2.1 from rounded endpoint cells |
| ADR slopes, guest share 0 | 1 | 0 | 3.166 | 0.978 | −2.188 |
| ADR slopes, guest share 0.5 | 1 | 0 | 3.445 | 1.085 | −2.360 |
| ADR slopes, guest share 0.82456 | 1 | 0 | 3.618 | 1.148 | −2.470 |

The unit-translation endpoints are reported to one decimal place. Subtracting two such endpoints has a rounding uncertainty of up to 0.1pp. The highest-fee endpoint's separately printed −2.2pp step is compatible with that rounding envelope; it is not an independently reproducible extra decimal. Every possible step in these rounding envelopes is negative. The ADR rows are recomputed from the note's gross values by subtracting 0.21pp once from each quarter.

Thus the regional recompute **does not change the positive, fading-tailwind conclusion**. It does change the level sensitivity. Unit translation places Q4 roughly 0.5–0.7pp above B4's stated/after-hedge approximately 1pp benchmark. The ADR alternatives put Q4 only −0.022 to +0.148pp from that benchmark. Neither family is a measured forecast interval or an independently validated improvement. At midpoint, changing conventions changes the FX step from the note's −2.09pp to −2.36pp, a further 0.27pp fade.

Holding the note's total-growth scenarios fixed illustrates the consequence for the residual partition:

| Conditional Q3 GBV, USD m | Scenario n | PIT n | Fixed total Q4−Q3 growth step, pp | Ex-FX step with unit translation, pp | Ex-FX step with ADR sensitivity, pp |
|---|---:|---:|---:|---:|---:|
| 26,185 | 1 | 0 | −2.10 | −0.01 | +0.26 |
| 26,300 | 1 | 0 | −1.77 | +0.32 | +0.59 |
| 26,550 | 1 | 0 | −1.05 | +1.04 | +1.31 |

These are conditional arithmetic partitions, not revised revenue forecasts: total growth is held fixed, total minus FX defines ex-FX. The near-zero case changes sign under a permitted mechanism sensitivity. A precise unconditional residual-acceleration claim would not survive.

### Units, origin/destination mix and the hedge

For booked USD GBV with an embedded currency factor f, constant-FX GBV is `G_USD / (1+f)`. In the fixed recognition kernel the correct diagnostic is the difference between the USD and constant-FX revenue sums, divided by **prior-year revenue** to express growth percentage points. Multiplying embedded USD GBV by the currency factor again double-counts it. Unit nominal translation is an accounting convention conditional on the currency assignment; it does not mean a short-sample ADR regression slope measures a physical currency share.

The input ADR slopes are EMEA 1.043 (n=10), LatAm 0.623 (n=7), APAC 0.86 (n=5). NA is 3.205 (n=5) but explicitly labelled unidentified because its basket has less than 1.5pp variation. Treating that finite NA coefficient as measured would be indefensible. Moreover, reported-minus-ex-FX ADR growth is a reduced-form growth gap: even without behavioural pass-through, `(1+local growth)*(1+currency change)−1` includes an interaction. Short regressions against judgement baskets can absorb price, growth and composition effects. They are sensitivity coefficients, not identified translation shares.

A transparent first-order origin/destination driver is `f_destination + g*(f_origin−f_destination)`. A separate ADR-slope sensitivity can replace the first term with `beta_destination*f_destination` while retaining only that incremental guest-origin shift. Adding `g*f_origin` to an already complete destination driver would add an extra `g*f_destination`. Guest-fee share `g=14.1/(14.1+3)=0.8245614` is a scenario endpoint, not measured current migration. At g=0 the revenue currency follows destination currency. Countries, nationality and income do not establish the payment currency for either fee side.

The raw hedge dollars imply −0.212454pp Q3 and −0.212383pp Q4, each rounded to −0.21pp in the supplied forward table. Their difference is only +0.000071pp, so hedging does not create the approximately 2pp fade. Management's approximately 3pp after-hedge assumption corresponds to approximately 3.21pp gross under the rounded hedge. Comparing 3.879pp gross with 3pp after hedge would overstate the difference by 0.21pp; deducting the hedge twice would understate the scenario by the same amount.

### The scale can change without new information

For any positive constant s, `y_hat = beta*x = (beta*s)*(x/s)`. Rescaling the predictor alone changes the fitted coefficient's numerical denominator and preserves every fitted value. The note's reported point slopes admit the following construction:

| Window | Retrospective fit n stated by note | PIT n | USD-inclusive beta | Normalized beta | Implied s = normalized / inclusive | Maximum numerical prediction difference on five illustrative x values |
|---|---:|---:|---:|---:|---:|---:|
| W1 | 14 | 0 | 0.879 | 0.535 | 0.608646 | 0 |
| W2 | 10 | 0 | 0.731 | 0.447 | 0.611491 | 4.44e−16 |

This is a constructive alternative explanation for the apparent coefficient improvement, not an assertion that the original model uses a constant share in every quarter. Time-varying exposure shares, grid discretization and the actual profile fit can also matter; they were not re-estimated. The construction is enough to show that approaching 0.56 numerically does not itself establish measured currency exposure or better prediction. The displayed USD-inclusive W1 lower confidence bound is 0.65, still above 0.56. Current-weight retrospective fits do not become PIT forecasts by changing the units of their predictor.

### Historical eligibility and accounting fit

| Check | Candidate/data n | Eligible PIT n | Independent result |
|---|---:|---:|---|
| Annual revenue/GBV ratios, 2020–2025 | 24 region-years | Not a forecast test | Recomputed ratios equal supplied take-rate ratios to displayed floating-point precision; max difference 0pp |
| Quarterly ADR source | 691 records across metrics | Not a forecast test | 110 labelled modelled; 412 derived; other rows contain disclosures, qualitative statements or missing values |
| W1 target quarters, 2023Q1–2026Q2 | 14 | 0 | September-12 reconstruction postdates all eligible historical guide origins |
| W2 target quarters, 2024Q1–2026Q2 | 10 | 0 | Same; W2 is nested inside W1 |
| Shared registry filename inventory | 69 CSVs | 0 X files | No regional-kernel, regional-FX or X-method registration found |

The current reconstruction date is later even than the frozen harness's 6-August LIVE guide, which is excluded from W1/W2. Counting the specified target quarters independently gives 14 and 10; none can consume a reconstruction stamped 12 September. The public-input dates are 1 June, 2 July and 19 August 2026, not a historical sequence of guide-date measurements. This necessary-condition proof verifies eligibility without reading X's reconstructed exposure outputs or executing its code. It does not claim those files contain no retrospective values.

For any chosen positive lagged regional GBV base B, defining `lambda = observed revenue/B` forces `lambda*B = observed revenue`. It would pass the same-quarter revenue identity with an economically wrong B as well. A revenue-conserving regional decomposition of the existing lagged FX basket is therefore a simpler explanation of the qualitative Q3/Q4 result than new O-D identification. The 24 annual ratio checks, 72 same-cell identities reported in the note and share-sum checks cannot supply a forecasting edge.

## Numbered refutation attempts

1. **Claim → public origin data may already identify the missing Airbnb currency matrix. Attack →** Rebuild NTTO, JNTO and Eurostat control totals; distinguish duplicated JNTO currency details from its population partition; compare measured units with the target exposure. **Result → survived:** totals and coverage reproduce, but destinations are US, Japan and EU27 and observations are visitors/platform nights, not Airbnb currency transactions. Unmatched currencies and unmeasured mapping choices remain.

2. **Claim → the reconstruction's strong accounting fit could justify replacing B4 despite missing direct exposures. Attack →** Recompute annual ratios and construct an arbitrary-base lambda identity. **Result → survived:** all 24 annual ratios reproduce, yet exact same-cell fit is guaranteed by the construction. The quarterly input is substantially modelled/derived, and no independent forecast is created by multiplying a ratio back by its denominator.

3. **Claim → the coefficient moving toward 0.56 demonstrates that regional exposure is more accurate. Attack →** Construct constant predictor rescalings that yield the displayed coefficient changes with unchanged predictions. **Result → survived for the original evidence-limit sentence; the stronger identification claim is refuted:** scales 0.608646 and 0.611491 reproduce the numerical changes. No new data or predictive improvement is required. The note correctly warns that the change is partly a denominator effect.

4. **Claim → a unit translation and a measured ADR slope are interchangeable FX mechanisms. Attack →** Inspect the short-sample slope estimates, their intercept/basket interpretation and NA's explicit non-identification; recompute the supplied sensitivity. **Result → partially:** exact Q3/Q4 levels depend materially on convention, so a precise regional FX forecast would fail this attack. The original sentence survives because it does not promote these sensitivities to a measured replacement.

5. **Claim → the Q3 discrepancy or Q4 fade could be a hedge/basis mistake. Attack →** Independently sum regional gross contributions, convert hedge dollars to prior-year growth pp, deduct once and align management's comparator. **Result → survived:** Q3 is 3.879 gross / 3.669 after hedge, +0.669pp versus management on the same basis. Hedge precision is immaterial for the step. Double deduction or gross-versus-after-hedge comparison would introduce a 0.21pp error; the note's presented calculation does neither.

6. **Claim → regional recomputation could reverse the FX conclusion and therefore demand a replacement. Attack →** Recompute all three ADR-slope endpoints, use explicit rounding envelopes on all three unit-translation pairs, and compare Q4 with B4. **Result → survived:** every scenario remains positive in Q3 and Q4 with a negative Q4−Q3 FX step. The ADR-slope Q4 range 0.978–1.148pp closely brackets B4's approximately 1pp; a different unit-translation level alone does not establish a superior method.

7. **Claim → origin/destination reconstruction could be mechanically complete because regional shares normalize. Attack →** Contrast country-cross-border and regional-cross-border using Canada's 23.458% of US inbound visitors, vary settlement-currency assignments without changing visitors, and inspect the guest-origin incremental formula. **Result → survived:** normalized regional margins and country labels leave currency settlement unidentified. Adding a complete origin FX factor instead of an origin-minus-destination increment would double-count part of the driver. This supports the caution in the exact sentence, not a claim that an O-D matrix is the only conceivable way to improve B4.

8. **Claim → a stable ex-FX acceleration could validate the regional mechanism. Attack →** Hold total-growth cases fixed and replace the midpoint unit step −2.09pp with the ADR-sensitivity step −2.36pp. **Result → partially:** the lowest residual changes from −0.01pp to +0.26pp. The economic partition near zero is convention-sensitive. This is a successful attack on any unconditional precise acceleration claim, but that is not the original sentence being voted on.

9. **Claim → historical rows, current source data or a registry object could supply PIT observations even if current exposures are assumed. Attack →** Independently enumerate both windows, compare the September-12 reconstruction stamp to the excluded August-6 live-guide boundary, inspect raw publication dates and registry filenames. **Result → survived:** 0/14 and 0/10 eligible current-reconstruction observations, and no X registry file. The existence of earlier FX prices or retrospective outcomes cannot backdate the later exposure reconstruction.

## What ran: commands and receipts

All commands ran from the repository root. The six input paths and hashes are recorded below. The primary calculation exited **0**, Python-measured runtime **0.007738 seconds**, tool wall time **0.654232 seconds**. The residual-partition calculation exited **0**, Python-measured runtime **0.000016 seconds**, tool wall time **0.319576 seconds**. Overall agent wall time and token usage are unavailable, not estimated. The portable `python` command used `.venv` first on PATH.

Exact primary calculation:

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + [IO.Path]::PathSeparator + $env:PATH
@'
import csv,hashlib,json,math,time
from collections import Counter
from datetime import date
from pathlib import Path
start=time.perf_counter()
paths={
 'public':'analysis/src/forecast_methods/regional_kernel_v1/public_inputs.csv',
 'annual':'data/processed/adr/01_regional_annual.csv',
 'quarterly_adr':'data/processed/adr/04_regional_quarterly.csv',
 'basket':'data/processed/overnight/10_fx_basket.csv',
 'passthrough':'data/processed/overnight/10_regional_fx_passthrough.csv',
 'hedge':'data/processed/overnight/28_fx_hedge_forward.csv'}
def read(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:
  return list(csv.DictReader(f))
d={k:read(p) for k,p in paths.items()}
def amount(rows):
 return sum(float(r['visitors_or_nights']) for r in rows)
p=d['public']
nt=[r for r in p if r['provider']=='NTTO']
jn=[r for r in p if r['provider']=='JNTO']
jc=[r for r in p if r['provider']=='JNTO_CCY']
eu=[r for r in p if r['provider']=='EUROSTAT']
nt_total=amount(nt); jn_total=amount(jn); eu_total=amount(eu)
public_summary={
 'ntto_total':nt_total,
 'ntto_named_origin_pct':100*amount([r for r in nt if r['origin']!='Other'])/nt_total,
 'ntto_mapped_currency_pct':100*amount([r for r in nt if r['currency']!='UNRESOLVED'])/nt_total,
 'ntto_canada_within_NA_pct':100*amount([r for r in nt if r['origin']=='Canada'])/nt_total,
 'jnto_total':jn_total,
 'jnto_classified_origin_pct':100*amount([r for r in jn if r['origin_region']!='UNRESOLVED'])/jn_total,
 'jnto_mapped_currency_pct':100*(amount(jc)+amount([r for r in jn if r['currency']!='UNRESOLVED']))/jn_total,
 'jnto_if_currency_extracts_double_counted':amount(jn+jc),
 'eurostat_total_nights':eu_total,
 'eurostat_foreign_pct':100*amount([r for r in eu if r['origin']=='FOR'])/eu_total,
 'public_input_dates':sorted(set(r['publication_date'] for r in p)),
 'public_destinations':sorted(set(r['destination'] for r in p))}
annual=[r for r in d['annual'] if r['region']!='total' and 2020<=int(r['year'])<=2025]
annual_err=max(abs(100*float(r['revenue_musd'])/float(r['gbv_musd'])-float(r['take_rate_pct'])) for r in annual)
baskets={r:sum(float(v['weight']) for v in d['basket'] if v['region']==r and v['currency']!='BASKET') for r in ['na','emea','latam','apac']}
slopes={r['region']:{'n':int(r['n']),'slope':float(r['slope_pp_per_pp']),'note':r['note']} for r in d['passthrough']}
hedges={r['quarter']:{'rounded_pp':float(r['hedge_effect_on_revenue_growth_pp']),
 'from_dollars_pp':100*float(r['hedge_reclass_musd'])/float(r['prior_year_revenue_musd'])} for r in d['hedge'] if r['quarter'] in ['3Q26','4Q26']}
# Published note tables are inputs to these independent arithmetic checks.
regional_gross=[0.595,2.370,0.674,0.240]
regional_after=[0.513,2.269,0.661,0.225]
regional_difference=[-0.673,0.827,0.489,0.026]
q3_gross=sum(regional_gross); q3_after=q3_gross-0.21
pass_results=[]
for g,q3,q4 in [(0,3.376,1.188),(.5,3.655,1.295),(14.1/(14.1+3),3.828,1.358)]:
 pass_results.append({'guest_fee_share':g,'q3_gross_pp':q3,'q4_gross_pp':q4,
 'q3_after_pp':q3-.21,'q4_after_pp':q4-.21,'q4_minus_q3_pp':q4-q3,
 'q3_vs_management_pp':q3-.21-3,'q4_vs_B4_pp':q4-.21-1})
unit_rounding=[{'guest':g,'step_center_pp':b-a,'step_rounding_interval_pp':[b-a-.10,b-a+.10]} for g,a,b in [(0,3.4,1.5),(.5,3.7,1.6),(.82456,3.8,1.7)]]
rescaling=[]
for window,b,bn in [('W1',.879,.535),('W2',.731,.447)]:
 s=bn/b; x=[-4.0,-1.0,0.0,3.0,7.0]
 err=max(abs(b*v-bn*(v/s)) for v in x)
 rescaling.append({'window':window,'inclusive_slope':b,'normalized_slope':bn,'implied_rescale_share':s,'max_prediction_error':err})
windows={w:len([i for i in range(4*y,4*2026+2)]) for w,y in [('W1',2023),('W2',2024)]}
files=sorted(p.name for p in Path('data/processed/forecast_methods/registry').glob('*.csv'))
xfiles=[f for f in files if f.startswith(('regional-kernel','regional_kernel','regional-fx','regional_fx','x__','x-'))]
print(json.dumps({'public':public_summary,'annual_n':len(annual),'annual_ratio_max_error_pp':annual_err,
 'quarterly_adr_rows':len(d['quarterly_adr']),'quarterly_adr_basis':dict(Counter(r['basis'].split(' (')[0] for r in d['quarterly_adr'])),
 'basket_region_sums':baskets,'pass_slopes':slopes,'hedges':hedges,
 'q3_midpoint':{'gross_pp':q3_gross,'after_once_pp':q3_after,'after_region_sum_pp':sum(regional_after),'vs_management_pp':q3_after-3,'region_difference_sum_pp':sum(regional_difference),'after_twice_error_pp':-.21},
 'unit_rounding_steps':unit_rounding,'passthrough_fx':pass_results,
 'normalization_invariance':rescaling,'window_dates_n':windows,
 'current_stamp_after_excluded_live_guide':date(2026,9,12)>date(2026,8,6),
 'registry_csv_n':len(files),'x_registry_files':xfiles,
 'input_sha256':{k:hashlib.sha256(Path(p).read_bytes()).hexdigest() for k,p in paths.items()},
 'runtime_seconds':round(time.perf_counter()-start,6)},indent=2))
'@ | python -
```

Exact residual-partition calculation:

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + [IO.Path]::PathSeparator + $env:PATH
@'
import json,time
start=time.perf_counter()
unit_step=-2.09
adr_step=(1.295-.21)-(3.655-.21)
rows=[]
for gbv,exfx in [(26185,-.01),(26300,.32),(26550,1.04)]:
 total_step=exfx+unit_step
 rows.append({'conditional_Q3_GBV_musd':gbv,'fixed_total_growth_step_pp':round(total_step,3),'unit_exfx_step_pp':exfx,'ADR_sensitivity_exfx_step_pp':round(total_step-adr_step,3)})
print(json.dumps({'conditional_partition_only':rows,'runtime_seconds':round(time.perf_counter()-start,6)},indent=2))
'@ | python -
```

Input SHA-256 fingerprints (keys map to the exact paths in the command):

| Input | SHA-256 |
|---|---|
| public | `72d973f06e03c89b6720135b9938156327feb01f53d8313d728a0e5dd479a0a2` |
| annual | `ba0c9a68c4bf36831b7f0cbed67e8ec34799210e79899b4fb123b999efefac24` |
| quarterly_adr | `82d2c3afd2552bc8d727e27e7b2a308687a2962ceb4f3e42271e29cb242dee38` |
| basket | `cece41677eb65d995c2ccd4c862651b6c1fd69a0e4bee333535ee08cb974ca2e` |
| passthrough | `af22b8bdf9df91c44854eda1dc0e499566dbab1aecf39cf9c5194a0b5da5999e` |
| hedge | `9781efd0649a10bc190f7edd2e2510b334b18250d64916c3f0c5cd2a05c657e2` |

## What failed or could not be done

The official NTTO and JNTO PDFs opened successfully through the web fetch tool. The Eurostat API failed in that tool; a direct in-memory `urllib.request.urlopen(url, timeout=20)` attempt also failed because outbound socket access was restricted. No official release or raw file was saved, no credentials were used, and no licensed source was accessed. The Eurostat result is therefore labelled a verification of the local source extract, not a fresh API confirmation.

The assignment prohibited X code and derived tables, so this note does not claim independent reconstruction of the full regional forecast, exposure weights, 72 quarterly accounting cells, profile likelihood or forecast publication-date validator. Instead it tests their necessary mechanisms and reproduces relevant arithmetic from allowed inputs. The original reconstruction's timestamp is taken from its note; the zero-PIT proof is conditional on that declared timestamp. No numerical power is inferred from the retrospective fit's n. No consensus estimate is consumed.

## Interpretation

Keep the original exact sentence. The stronger statements that regional accounting fit validates a forecast, that approaching a 0.56 slope identifies exposure, or that the ex-FX residual has a precise convention-independent sign do not survive the attacks. The positive tailwind that fades from Q3 to Q4 survives the displayed sensitivity families; that shared direction is also explained by a lagged consolidated currency driver with assumed regional weights. It is not evidence of a measured O-D advantage.

## RESUME

Parent should record a `survived` vote on the original sentence, preserve 0/14 W1 and 0/10 W2 eligible current-reconstruction observations, and retain the distinction between scenario arithmetic and measured exposure. Any successor needs dated Airbnb-relevant origin and settlement-currency evidence, an explicit currency-driver normalization and a real PIT forecast comparison before replacing B4. Keep hedge adjustments on the prior-year-revenue pp basis and apply them once; retain the ADR/unit sensitivity because the near-zero ex-FX case changes sign. Parent owns board, scorer and git. This agent wrote only this new refutation note.
