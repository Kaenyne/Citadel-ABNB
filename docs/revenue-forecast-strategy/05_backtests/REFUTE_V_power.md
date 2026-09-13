# REFUTE V power — independent arithmetic and evidence-count audit

Codex refuter · 2026-09-12 · branch `codex/lane1-full` · main calculation: 2.745 seconds shell / 0.0471 seconds measured computation; count-matching diagnostic: 5.686 seconds shell / 0.0328 seconds computation. Token usage unavailable; not estimated.

## Verdict

**survived** — the exact sentence is correct as conditional arithmetic under the final model's adopted target-date convention. Independently rebuilding all six base lenses from the annual model and assumptions gives $180.876286 for the FY27 EBITDA lens and $156.786845 for their mean. These round to $180.88 and $156.79. The six lenses are applications of one base operating case, not six independent observations. No confidence interval or statistical power claim follows from their count.

The hostile check did find an ancillary disclosure problem: the note's W1 change regression requires excluding January–October 2023, although that additional cutoff is not stated in its monthly-window description. Its level-regression HAC intervals also do not reproduce from the literal stated specification. These findings limit statistical support for a fair-multiple interpretation; they do not alter the two arithmetic objects in the original sentence.

## Pre-registered audit

Original exact sentence: “Using the final FY27 base model, 16.5x adjusted EBITDA implies a $180.88 12-month target, while the existing six-lens base football-field mean is $156.79; these are different valuation objects.”

Before calculation: independently reconstruct the 16.5x bridge and six-lens base arithmetic, count distinct model states versus alternative lenses, challenge horizon/units/aggregation and check whether any statistical inference is required by the exact sentence. Inventory disclosed specifications and W1/W2 support without inventing statistical power for a conditional identity. At least five numbered attacks will each state claim, attack, explicit result and evidence. Final verdict on the exact sentence will be survived, refuted or partial. There is no promotion pass line for this refuter.

Read only the V note, its named raw model/valuation inputs, actual V registry files if present, and the permitted harness README/cheatsheet. V code and V derived outputs remain unread. Write only this note; parent owns board, scorer and git.

## Numbered refutation attempts

### 1. Claim → 16.5x implies $180.88. Attack → cash, units, annual row or share denominator may be mixed.

**Result: survived.** I used the unique Base/FY2027 row of `13_model_annual.csv` and the adopted 16.5x multiple from `model/assumptions.md`:

| Bridge item | n | Independent value |
| --- | ---: | ---: |
| FY27 adjusted EBITDA | 1 base model state | $5,685.7698M |
| Enterprise value at 16.5x | 1 calculation | $93,815.2017M |
| FY27 net cash | 1 base model state | $10,115.9869M |
| Equity value | 1 calculation | $103,931.1886M |
| Modelled diluted-share proxy | 1 base model state | 574.5982M |
| Equity value / shares | 1 calculation | **$180.876286** |

USD millions divided by millions of shares gives dollars per share. The net-cash contribution is $17.605323 per share. The result differs from the raw valuation-summary row ($180.8763) by only −$0.0000136. This is a conditional model identity, not a market-price observation or statistical estimate of value.

### 2. Claim → the existing field has six lenses and mean $156.79. Attack → a summary row, extra sensitivity or the wrong DCF may have been included.

**Result: survived.** I rebuilt the six designated core lenses from the annual model and assumptions, including the DCF from its explicit ten-year growth fade. No V reconciliation output or code was read.

| Core base lens | n | Independently reconstructed price | Input summary price |
| --- | ---: | ---: | ---: |
| FY27 EV / adjusted EBITDA | 1 model state | $180.876286 | $180.8763 |
| FY27 EV / FCF | 1 same state | $152.501386 | $152.5014 |
| FY27 P / SBC-adjusted FCF | 1 same state | $117.257237 | $117.2572 |
| FY27 earnings proxy | 1 same state | $110.579763 | $110.5798 |
| FY28 EV / adjusted EBITDA, discounted one year | 1 same scenario path | $196.917488 | $196.9175 |
| DCF on FCF | 1 same scenario path | $182.588909 | $182.5889 |
| Equal-weight arithmetic mean | 6 lenses, 1 base operating state | **$156.786845** | $156.7868 |

The maximum component discrepancy is $0.0000374, consistent with source rounding. Averaging the six already-rounded input lens rows instead gives $156.786850, also $156.79. The summary CSV has 60 rows: 36 Base, 12 Bear, 12 Bull. That includes reverse-DCF scenarios, alternative lenses and summary statistics. It is not a 60-observation valuation sample. The core field has 18 scenario/lens cells across three operating cases; the exact sentence uses six cells from one case.

### 3. Claim → these are different valuation objects. Attack → the EBITDA price is itself in the field, so the comparison might be false or redundant.

**Result: survived.** The single EBITDA lens is one of the six entries being averaged. The two objects overlap; they are not independent estimates. This does not make a component equal to the mean. Their independently calculated difference is **$24.089436**, or 15.3644% of the field mean. The field additionally uses FCF, SBC-adjusted FCF, an earnings proxy, FY28 EBITDA and a DCF with different valuation operators.

An attack on the aggregator succeeds against any claim of a uniquely justified target, which the exact sentence does not make:

| Deterministic alternative using this one base state | n | Price / range |
| --- | --- | ---: |
| Original arithmetic mean | 6 lenses | $156.78685 |
| Median | Same 6 lenses | $166.68885 |
| Leave one lens out | 6 possible means of 5 lenses | $148.76072–166.02826 |
| Add the excluded SBC-adjusted DCF | 7 lenses | $151.92774 |
| Replace discounted FY28 lens with its undiscounted sensitivity | 6 lenses, mixed-date sensitivity | $160.23290 |

These are aggregation sensitivities, not alternate confidence intervals. The exact sentence correctly calls $156.79 the **existing** six-lens mean; it does not establish optimal weights, independence or superiority of that mean.

### 4. Claim → six lenses provide enough precision to compare the targets. Attack → construct a standard error or bootstrap across lenses.

**Result: survived on the original sentence; statistical precision would be unsupported.** The six prices were intentionally selected valuation formulas applied to common operating assumptions. They are neither random draws from a defined population of methods nor six independent realised forecast errors. The cross-lens sample standard deviation is $36.2562 and the descriptive range is $110.5798–196.9175, but neither is calibrated uncertainty about a future ABNB price.

A bootstrap that resamples these six labels merely randomizes arbitrary method weights. A Wilson interval is also inapplicable: there are no binary successes. For the exact price identities, statistical sample n, a minimum detectable effect, W1/W2 performance and a predictive confidence interval are **not applicable**. There is one fixed base operating state and zero independent validation errors supplied for this sentence. Arithmetic replication can be precise while the model's economic forecast remains uncertain.

Transparent deterministic derivatives quantify what the assumptions do without inventing statistical support:

| Perturbation, holding other base inputs fixed | n | Price effect |
| --- | ---: | ---: |
| One extra EBITDA multiple turn | 1 conditional perturbation | +$9.895210 |
| $1,000M extra net cash | 1 conditional perturbation | +$1.740347 |
| ±10% EBITDA | 2 conditional endpoints | ±$16.327096 |
| +1% modelled diluted shares | 1 conditional perturbation | Price $179.085432, down $1.790854 |

The input 16.5x is an assumed scenario value, not a point estimate whose sampling variance is established by this calculation. None of these perturbations is assigned a probability.

### 5. Claim → $180.88 is a 12-month target under the final model. Attack → annual-end cash/shares and FY28 valuation may create a hidden horizon mismatch.

**Result: survived under the exact sentence's “using the final FY27 base model” condition.** `model/assumptions.md` expressly adopts approximately 30 September 2027 as the target date and labels the outputs 12-month targets. The annual end-FY27 cash/share convention is slightly later than that label. Independently straight-lining those two inputs 75% from FY26 to FY27 gives **$179.444873**, $1.431414 below the model's answer, at the same FY27 EBITDA and multiple. The phrase must retain the model convention; it is not a claim of an exact September-dated capital structure or present fair value.

There is a real stale-source trap: the named `25_valuation_conventions.csv` still describes the FY28 EBITDA lens as undiscounted and includes an old $160.22 base mean. The later revision explicitly recorded in `model/assumptions.md` discounts that lens one year at the base 10.5% cost of equity and excludes its undiscounted sensitivity. Rebuilding `(16.5 × FY28 EBITDA + FY28 cash) / FY28 shares / 1.105` gives $196.917488, which matches the final summary. The file inconsistency must be disclosed, but the later model rule and final raw prices agree on $156.79. No old convention table has been overwritten here.

The share count also inherits a weighted-average diluted-share anchor used as a period-end proxy. That is an economic measurement limitation, not a division error. The original sentence remains conditional on this existing model rather than presenting an independently verified capital structure.

### 6. Claim → background regressions can supply statistical authority for 16.5x. Attack → independently reproduce their actual n and intervals.

**Result: survived on the exact arithmetic sentence; the ancillary W1 sample description does not survive a literal reconstruction.** Using the permitted monthly input, I formed 12-row differences on the full ordered series, then applied calendar starts 2023-01-01 and 2024-01-01. Each regression has an intercept and three regressors, OLS with HAC/Bartlett covariance at 12 lags and the standard normal interval. These are retrospective inherited-vintage diagnostics, not PIT forecasts.

| Diagnostic | Independently counted n | Growth slope, independent HAC(12) 95% interval | Comparison with note |
| --- | --- | --- | --- |
| W1, full literal 12-row change | 45 changes / 16 reported-quarter labels | 0.505028 [0.356854, 0.653202] | Note reports 35 / 12 and 0.4860 [0.3172, 0.6548] |
| W2, 12-row change | 33 changes / 12 reported-quarter labels | 0.476545 [0.309997, 0.643093] | Reproduces note |
| W1, forward-multiple level | 45 months / 16 reported-quarter labels | 0.482482 [0.110345, 0.854619] | Slope matches; note's interval is [0.1182, 0.8468] |
| W2, forward-multiple level | 33 months / 12 reported-quarter labels | 0.194791 [−0.335695, 0.725278] | Slope matches; note's interval is [−0.3233, 0.7129] |
| W1, post hoc final-35-row diagnostic | 35 changes / 12 reported-quarter labels | 0.486022 [0.317229, 0.654814] | Exactly reproduces note after dropping Jan–Oct 2023 |

The last row was an explicitly post hoc diagnostic to locate the count discrepancy. Its first date is **2023-11-30**. It is not a newly preferred window. The omitted ten eligible monthly changes run from 2023-01-31 through 2023-10-31; the note does not explain that exclusion. An upstream filter could explain it, but the permitted note does not specify one, so I do not assert misconduct or infer the reason.

I also checked the standard HAC finite-sample correction on the four literal regressions. It yields wider level intervals—W1 [0.092614, 0.872350], W2 [−0.371099, 0.760682]—and does not recover the reported endpoints. This audit ran eight covariance-version fits plus one count-matching diagnostic, all disclosed here rather than selecting whichever looks best. A positive change slope, even if fully reproduced, would not identify the exit-multiple intercept. Neither target-price identity requires any of these regressions.

### 7. Claim → multiple windows and scenarios add independent evidence. Attack → count specifications, overlaps and validation separately.

**Result: survived as arithmetic; an inference from the apparent count would fail.** The package note discloses at least four monthly regression cells (two functional forms × two windows), four parameters each, with 12-lag HAC. The monthly raw file contains 68 observations from 2021-02-28 through 2026-09-04 and 23 reported-quarter labels. Its last row is not literally month-end. Monthly price changes share accounting releases, and overlapping 12-row differences share most of their ingredients. Raw n therefore overstates independent information; the number of quarter labels is not itself an exact effective sample size either.

The package's guide-date diagnostics report 14/10 origins, training availability at 8/7 and abstentions at 6/3. Those counts are reported by the V note and were not independently reconstructed from V outputs. W2 is nested in W1, so neither 14+10 nor 8+7 is a count of unique origins. Registry filename inspection found no valuation object, consistent with the note's abstention. Zero fully vintage-verified price forecasts are supplied; the revenue harness has no price target or baseline for this conditional accounting sentence.

Separately, the model exposes three operating cases, six core lenses per case and three chosen growth-sensitivity points. The raw valuation summary also has 24 reverse-DCF grid rows (two FCF bases × four discount rates × three terminal-growth values), with implied-growth outputs rather than target prices. Counting those cells does not create 24 validation observations. The three growth points are conditional sensitivities anchored at 16.5x, not probability quantiles. The historical specification search beyond what the note discloses cannot be certified without leaving the permitted scope.

## What ran and what remains unverified

Only these named model inputs were read: `13_model_annual.csv`, `13_valuation_summary.csv`, `12_abnb_multiples_monthly.csv`, `12_exit_multiple_recommendation.csv`, `25_valuation_conventions.csv` under `data/processed/overnight/`, plus `model/assumptions.md`. The older exit-recommendation input was inspected to distinguish it from the final model; its operating inputs were not silently substituted. The V note, assignment and permitted harness/cheatsheet supplied scope and definitions. No V code or V derived output was read. No network refresh, historical consensus splice, registration or source mutation was performed.

Both numerical commands below exited 0 from the repository root using the existing project `.venv`. Main command shell wall time was 2.7451 seconds, measured Python computation 0.04707 seconds. The second, post hoc count-matching diagnostic took 5.6860 seconds shell / 0.03275 seconds computation. Commands are included verbatim. No bootstrap interval for target prices was produced because the input contains deterministic lenses rather than a valid sampling unit for such an interval. Full component vintages and the unreported regression exclusion remain unresolved.

```powershell
& ".venv/Scripts/Activate.ps1"
@'
import time,json
import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path
s=time.perf_counter()
annual=pd.read_csv('data/processed/overnight/13_model_annual.csv')
vals=pd.read_csv('data/processed/overnight/13_valuation_summary.csv')
a=annual.query("scenario == 'Base'").set_index('year')
b=a.loc[2027]; e=a.loc[2028]; p=a.loc[2026]
turn=b.adj_ebitda/b.shares_end
ev=16.5*b.adj_ebitda; equity=ev+b.net_cash
price=equity/b.shares_end
strip=b.fcf*np.cumprod(1+np.linspace(.09,.03,10))
dcf=(sum(strip/(1.105**np.arange(1,11)))+strip[-1]*1.03/(.105-.03)/(1.105**10)+b.net_cash)/b.shares_end
calcs={
'EV / adj. EBITDA, FY27E':price,
'EV / FCF, FY27E':(14.3*b.fcf+b.net_cash)/b.shares_end,
'P / SBC-adjusted FCF, FY27E':19.5*b.sbc_adj_fcf/b.shares_end,
'P / earnings proxy, FY27E':19.5*b.net_income/b.shares_end,
'EV / adj. EBITDA, FY28E':(16.5*e.adj_ebitda+e.net_cash)/e.shares_end/1.105,
'DCF on FCF':dcf}
base=vals.query("scenario == 'Base'").set_index('lens')
for name,x in calcs.items(): print('LENS',name,x,'input',base.loc[name,'price'],'delta',x-base.loc[name,'price'])
field=np.array([base.loc[name,'price'] for name in calcs])
sep=(16.5*b.adj_ebitda+.25*p.net_cash+.75*b.net_cash)/(.25*p.shares_end+.75*b.shares_end)
print('BRIDGE',json.dumps({'ebitda':b.adj_ebitda,'cash':b.net_cash,'shares':b.shares_end,'ev':ev,'equity':equity,'price':price,'cash_per_share':b.net_cash/b.shares_end,'one_turn':turn,'one_billion_cash':1000/b.shares_end,'ebitda_10pct_price_move':.1*16.5*turn,'shares_plus1pct_price':price/1.01,'sep30_interpolated':sep,'model_vs_sept':price-sep}))
print('FIELD',json.dumps({'lens_n':len(field),'operating_state_n':1,'input_summary_rows':len(vals),'by_scenario':vals.groupby('scenario').size().to_dict(),'mean':field.mean(),'median':np.median(field),'sd_descriptive':field.std(ddof=1),'range':[field.min(),field.max()],'gap':price-field.mean(),'gap_pct_field':100*(price/field.mean()-1),'leave_one_out_mean_range':[(field.sum()-field.max())/5,(field.sum()-field.min())/5],'seven_lens_including_sbc_dcf':(field.sum()+base.loc['DCF on SBC-adjusted FCF','price'])/7,'undiscounted_fy28_substitution':(field.sum()-calcs['EV / adj. EBITDA, FY28E']+base.loc['EV / adj. EBITDA, FY28E (undiscounted, value at end-FY2028; sensitivity)','price'])/6,'recomputed_six_lens_mean':np.mean(list(calcs.values()))}))
print('REGISTRY',[f.name for f in Path('data/processed/forecast_methods/registry').glob('*.csv') if f.name.startswith(('valuation','v__','v-','v_'))])
monthly=pd.read_csv('data/processed/overnight/12_abnb_multiples_monthly.csv')
monthly['month_end']=pd.to_datetime(monthly.month_end)
cols=['ev_ltm_ebitda_x','ntm_growth_proxy_pct','dgs10_pct','ndx_fwd_pe']
change=monthly[cols].diff(12)
change['month_end']=monthly.month_end
change['last_reported_quarter']=monthly.last_reported_quarter
print('MONTHLY',len(monthly),str(monthly.month_end.min()),str(monthly.month_end.max()),'unique_quarters',monthly.last_reported_quarter.nunique())
for typ,frame,dep in [('change',change,'ev_ltm_ebitda_x'),('level',monthly,'ev_ntm_ebitda_x')]:
    for w,start in [('W1','2023-01-01'),('W2','2024-01-01')]:
        reg=frame[frame.month_end>=start].dropna(subset=[dep,'ntm_growth_proxy_pct','dgs10_pct','ndx_fwd_pe'])
        X=sm.add_constant(reg[['ntm_growth_proxy_pct','dgs10_pct','ndx_fwd_pe']])
        fit=sm.OLS(reg[dep],X).fit(cov_type='HAC',cov_kwds={'maxlags':12})
        fitt=sm.OLS(reg[dep],X).fit(cov_type='HAC',cov_kwds={'maxlags':12,'use_correction':True})
        print('REGRESSION',typ,w,'n',len(reg),'quarters',reg.last_reported_quarter.nunique(),'beta',fit.params['ntm_growth_proxy_pct'],'CI',fit.conf_int().loc['ntm_growth_proxy_pct'].tolist(),'CI_corrected',fitt.conf_int().loc['ntm_growth_proxy_pct'].tolist())
print('elapsed_seconds',time.perf_counter()-s)
'@ | python -
```

The post hoc count-matching diagnostic was:

```powershell
& ".venv/Scripts/Activate.ps1"
@'
import time,pandas as pd,statsmodels.api as sm
s=time.perf_counter()
m=pd.read_csv('data/processed/overnight/12_abnb_multiples_monthly.csv')
m['month_end']=pd.to_datetime(m.month_end)
c=m[['ev_ltm_ebitda_x','ntm_growth_proxy_pct','dgs10_pct','ndx_fwd_pe']].diff(12)
c['month_end']=m.month_end; c['last_reported_quarter']=m.last_reported_quarter
reg=c[c.month_end>='2023-01-01'].dropna()
print('full_W1_first_last',str(reg.month_end.min()),str(reg.month_end.max()))
print('first_ten_months',reg.head(10)[['month_end','last_reported_quarter']].to_string(index=False))
tail=reg.tail(35)
f=sm.OLS(tail.ev_ltm_ebitda_x,sm.add_constant(tail[['ntm_growth_proxy_pct','dgs10_pct','ndx_fwd_pe']])).fit(cov_type='HAC',cov_kwds={'maxlags':12})
print('count_matching_tail35_start',str(tail.month_end.min()),'n_quarters',tail.last_reported_quarter.nunique(),'beta',f.params.ntm_growth_proxy_pct,'CI',f.conf_int().loc['ntm_growth_proxy_pct'].tolist())
print('elapsed_seconds',time.perf_counter()-s)
'@ | python -
```

## Interpretation

The exact sentence survives because it compares two reproducible, explicitly conditional model outputs. Its six-lens count is an aggregation definition, not six votes on fair value. The regression and horizon attacks identify real boundaries: the statistical specification needs fuller disclosure, the price labels follow an adopted approximate horizon, and modelled shares are a proxy. None licenses turning either arithmetic price into a statistically validated recommendation. No corrected headline number is required.

## RESUME

Parent can record **survived** for the original exact sentence. Preserve $180.88 as the single FY27 EBITDA lens and $156.79 as the existing six-lens mean, with no confidence interval inferred from lens dispersion. Before quoting regression evidence, require a dated explanation for excluding January–October 2023 and the exact level-regression HAC settings; the post hoc final-35-row reproduction locates the gap but does not justify it. Carry the approximate target date and diluted-share proxy, and flag the stale convention CSV through a new correction note rather than overwriting it. Only this assigned refuter note was written; parent owns board, scorer and git.
