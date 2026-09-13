# REFUTE X power — independent sample-size and uncertainty audit

Codex refuter · 2026-09-12 · branch: `codex/lane1-full` · numerical confirmation: 3.15 seconds shell wall time, 0.083 seconds measured Python computation. Token usage unavailable; not estimated.

## Verdict

**survived** — the original sentence survives this power audit. The independently inspected inputs support 72 accounting cells, 18 quarter totals and 14/10 retrospective FX targets, with zero admissible X historical forecasts. The public inputs contain tourism proxies, not an identified Airbnb origin–destination/payment-currency matrix. The strongest challenge was the apparent scale improvement: all six disclosed USD-inclusive intervals contain 0.95, while normalization alone accounts for much of the apparent movement toward 0.56. This does not establish that B4 is correct; it leaves X without evidence for replacing it.

## Original sentence and pre-registered audit

> The regional FX reconstruction does not yet justify replacing B4: no measured Airbnb origin–destination currency matrix is identified, and the current reconstruction has 0/14 W1 and 0/10 W2 point-in-time guide observations.

Recorded before numerical audit: try to disprove the sentence by finding an identified Airbnb origin–destination/payment-currency matrix, an admissible historical X forecast, independent forecasting information in the accounting identities, adequate statistical power, or a scale result robust to normalization. Count all disclosed specification axes without treating nested windows or algebraic rescalings as new independent observations. Independently recompute sample counts, public-proxy coverage and finite-sample power from permitted inputs. The final verdict must be exactly survived, refuted, or partial on the original sentence. There is no promotion pass line for this refuter.

Only the X note, named input datasets, actual X registry files if present, official public inputs, and the permitted harness README/cheatsheet will be used. X source code and X derived tables will not be read. Parent owns workboard, scorer and git.

## Results and numbered refutation attempts

### 1. Claim → no measured Airbnb currency matrix. Attack → large official tourism totals may already identify enough exposure.

**Result: survived.** I independently counted 25 rows in `public_inputs.csv`: NTTO 11, JNTO 5, JNTO_CCY 7 and Eurostat 2. The seven currency rows disaggregate parts of the JNTO rows; they are not seven additional destination samples. Aggregation reproduces the note:

| Input | n and unit | Independent arithmetic |
| --- | --- | --- |
| NTTO | 11 input aggregates, one destination-country/year | 68,288,000 visitors; named-origin coverage 77.1922%; currencies with a supplied FX series 74.9048% |
| JNTO | 5 origin aggregates plus 7 overlapping currency subaggregates, one destination-country/month | 3,442,100 visitors; classified-origin coverage 95.1164%; currency-proxy coverage 43.7320% |
| Eurostat | 2 residence categories, one EU/year total | 951,611,862 nights; foreign share 62.1792% |
| Airbnb O-D/payment-currency observations | 0 identified cells in these inputs | No measured joint matrix |

The NTTO actual-country counts were checked against the [official April 2026 report, table on page 3](https://www.trade.gov/sites/default/files/2026-05/NTTO-Spring-Forecast-2026.pdf). Japan counts were checked against the [19 August 2026 JAPAN NATIONAL TOURISM ORGANIZATION release](https://www.jnto.go.jp/en/news/20260819.pdf); its 2026 figures are preliminary visitor estimates. Neither measures Airbnb nights or payment currencies. High visitor counts cannot repair the missing mapping. The Eurostat share is independently recalculated from the local extract; its [official API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tour_ce_omr?geo=EU27_2020&time=2025&indic_to=NGT_SP&unit=NR) could not be fetched in this audit.

### 2. Claim → 0/14 W1 and 0/10 W2 PIT observations. Attack → the retrospective rows, latest releases or a registry object may restore a usable sample.

**Result: survived.** Registry filename inspection found no X/regional/origin/exposure object, consistent with the note's registration abstention. The raw gross-FX target input has exactly 14 non-null quarters from 2023Q1 through 2026Q2 and 10 from 2024Q1 through 2026Q2. Those are outcomes available for a retrospective fit, not archived forecasts.

The reconstruction is explicitly dated 2026-09-12. The last regional revenue input publication is 2026-08-06; all target outcomes in these windows precede the reconstruction. The JNTO input is dated 2026-08-19, later even than that final historical print. NTTO/Eurostat metadata dates are 2026-06-01/2026-07-02. A forecast built from the current full input set therefore cannot have existed at any of these historical guide origins. A publication-month proxy is not an exact historical timestamp either.

| Window | Actual FX targets n | Actual regional cells n | Eligible X PIT forecasts n | Completeness |
| --- | ---: | ---: | ---: | ---: |
| W1 | 14 | 56 | 0 | 0/14 |
| W2, nested inside W1 | 10 | 40 | 0 | 0/10 |

The zeros are missing eligible forecasts, **not** 14 or 10 forecasting failures. A Wilson interval treating these as zero successful predictions would answer the wrong question. Relaxing the harness's frozen LIVE date does not turn September reconstruction into historical forecasts.

### 3. Claim → accounting success does not supply forecast validation. Attack → treat 72 exact cells or 18 zero-error sums as the effective sample.

**Result: survived.** `L0_exact_regional_revenue.csv` contains 72 unique region-quarter cells, four per quarter over 2022Q1–2026Q2: 56 labelled `filed`, 16 `back_out`. The latter remain useful exact accounting reconstructions but are not separate disclosed-quarter draws. Their 18 quarter sums match the consolidated KPI revenue exactly at supplied precision: maximum relative error 0.000%.

The annual input has 24 region-year observations across six years and four regions. Independently calculated `100 × revenue / GBV` differs from its supplied annual ratio by at most 1.7764e-15pp. This is a recomputation of a ratio from its defining operands. Likewise, for arbitrary positive carried GBV B, setting lambda = revenue/B ensures lambda × B = revenue. Neither identity supplies an out-of-sample error or an independent estimate of forecast accuracy. Within each quarter, regional components share the same consolidated total and common economic shocks; 72 is not an independent forecast n.

### 4. Claim → regional identification remains weak. Attack → annual anchors and seasonal replication may make the coefficient count harmless.

**Result: survived.** Every one of the 72 matching quarterly ADR input cells is labelled modelled or derived: 31 annual-anchor seasonal levels, 39 disclosed-growth chains on modelled bases, and 2 ex-FX-growth/pass-through chains. Independent revenue measurement therefore does not make quarterly regional GBV independently measured.

The note uses 16 region-season coefficients. The raw quarter inventory gives four Q1 and four Q2 observations per region in W1, versus three each for Q3/Q4. Restricting the same inventory to W2 gives three Q1/Q2 and two Q3/Q4 observations. The actual X coefficient construction uses the stated 2023+ seasonal factors and a 2025 annual anchor; the W2 count is a sensitivity of available seasonal support, not a claim that X refit coefficients using only W2.

| Object | n | Parameters/support |
| --- | ---: | --- |
| Quarterly kernel, W1 regional inventory | 56 cells in 14 quarters | 16 coefficients; only 3–4 same-season cells per coefficient |
| Quarterly kernel, W2 regional inventory | 40 cells in 10 quarters | 16 coefficients; only 2–3 same-season cells per coefficient if restricted |
| Each gross-FX fit, W1 | 14 quarter outcomes | 3 nonnegative lag coefficients plus dispersion; 4/14 = 28.6% |
| Each gross-FX fit, W2 | 10 quarter outcomes | Same 4 parameters; 4/10 = 40.0% |

The last two ratios are parameter-to-observation diagnostics, not exact degrees of freedom for a bounded interval likelihood. They also omit upstream exposure allocations, anchors and pass-through assumptions. Borrowed assumptions reduce neither measurement uncertainty nor the need for PIT validation.

### 5. Claim → both-window scale evidence is insufficient. Attack → a robust specification search may establish improvement despite small n.

**Result: survived.** Both W1 and W2 are disclosed; I found no omission of the weaker W1 result in the note. The auditable minimum is **six scale fits**, from three fee mixes × two windows. Each fits four parameters. The note also reports the following axes:

| Disclosed axis | Count of settings/output combinations | Independent sample n |
| --- | --- | --- |
| Fee-revenue guest share | 3: 0, 0.5, 14.1/17.1 = 0.82456 | Same 14/10 outcomes reused |
| Scale normalization | 2 representations: USD-inclusive, non-USD normalized | Same fits/outcomes; not twice the sample |
| Live translation sensitivity | 3 fee mixes × 2 quarters × 2 translation choices = 12 scenario cells | 0 realised/PIT forecast scores |
| Q4 ex-FX step at midpoint fee mix | 3 conditional GBV cases | 0 independent historical tests |
| Availability arithmetic | 3 lag rules × 3 date/publication assumptions = 9 Q4 combinations | 0 realised/PIT forecast scores |
| Mix-stability attribution | 3 diagnostics × 2 windows = 6 reported statistics | Same 14/10 quarters reused |

Further assumptions include the fixed 2/3–1/3 recognition weights, the country-cross-border scenario, regional destination baskets, unresolved-currency allocations, the annual anchor, ±10% ADR envelopes, fallback ±5% nights and a fixed demand elasticity. Their full development search count is not recoverable from the permitted note/inputs. Six is a lower bound on disclosed scale fits, not a certified count of everything tried. Normalization is algebra, not an independent model. I do not sum unlike outputs into a fictitious multiplicity-adjusted trial count. W2 is a subset of W1 and cannot be treated as an independent replication.

### 6. Claim → scale results do not justify replacing B4. Attack → the midpoint scale appears to approach the disclosed non-USD fraction.

**Result: survived; the attack works against an upgrade claim, not the original abstention.** The note's USD-inclusive midpoint is 0.879 [0.650, 1.150] for W1 and 0.731 [0.500, 1.000] for W2, versus B4's approximate 0.95. Both conditional intervals have width 0.50. All six fee-mix/window intervals in the note contain 0.95, with the final W2 upper endpoint exactly 0.95. None establishes a difference from that point reference under X's own interval model. This is not a formal paired comparison with an estimated B4 coefficient and does not prove equivalence.

If driver x is divided by an assumed non-USD share s, preserving predictions requires beta' = s × beta. From the displayed midpoint numbers:

| Window | n | USD-inclusive beta | Normalized beta | Implied s = beta'/beta | 0.95 expressed in that normalized convention |
| --- | ---: | ---: | ---: | ---: | ---: |
| W1 | 14 | 0.879 | 0.535 | 0.60865 | 0.57821 |
| W2 | 10 | 0.731 | 0.447 | 0.61149 | 0.58092 |

Thus 0.535's visual proximity to 0.56 is not evidence of a new exposure measurement. Predictions and uncertainty must be compared under the same denominator; the normalized reference also lies inside the reported normalized intervals. Values are inferred from rounded note entries and should not be mistaken for an exact constant share used every quarter. W1's USD-inclusive interval excludes 0.56 while W2's includes it, but a basket slope is not inherently the same estimand as a disclosed non-USD revenue fraction.

### 7. Claim → the available history cannot establish forecasting superiority. Attack → 14/10 observations may already offer adequate power.

**Result: survived.** Actual PIT paired forecast-error n is zero: no bootstrap of X-minus-B4 forecasting loss is defined, and the unconstrained set of possible hit probabilities remains [0,1]. The following independently calculated diagnostics are explicitly **hypothetical benchmarks**, not X hit rates or X confidence intervals. They assume independent trials, ignore specification selection and temporal dependence, and therefore do not grant precision to this reconstruction.

| Hypothetical independent validation sample n | One-sided exact 5% binomial rejection of p = 0.5 | Power at true p = 0.70 | True p required for 80% power | Wilson 95% interval at approximately 70% observed hits |
| ---: | --- | ---: | ---: | --- |
| 14 | at least 11/14 | 35.52% | 83.12% | 10/14: [45.35%, 88.28%] |
| 10 | at least 9/10 | 14.93% | 91.67% | 7/10: [39.68%, 89.22%] |

For an independent normal paired-mean comparison, an exact noncentral-t calculation at two-sided alpha 0.05 gives an 80%-power detectable mean difference of **0.810 paired-error standard deviations at n=14** and **0.996 at n=10**. These optimistic one-mean calculations do not include X's fitted lag coefficients. No honest pp or dollar detectable effect follows without a validated paired-error dispersion. More windows cut from the same quarters do not increase the number of independent observations.

### 8. Claim → quoted uncertainty is not total forecasting uncertainty. Attack → profile bounds, rounding intervals or scenario envelopes may already cover the unidentified exposures.

**Result: survived.** The note's profile intervals condition on the scenario design and assume Gaussian errors. It explicitly excludes serial dependence, proxy error and regional-GBV uncertainty. Letter FX values are ±0.5 intervals; they cannot be promoted to exact targets to manufacture extra precision. The independently inspected L0 interval input also explicitly excludes derived residual-to-total rows from likelihoods.

The ±10% ADR and fallback ±5% nights bands are imposed sensitivity bounds, not coverage-calibrated probabilities. Currency exposures, migration penetration and origin-to-payment mapping lack measured error distributions. Bootstrapping the 14 or 10 historical outcomes while fixing these assumptions would leave that uncertainty untouched. I independently recomputed Wilson/binomial/noncentral-t diagnostics and scale-normalization arithmetic; I did **not** independently reproduce X's profile-likelihood endpoint grids. Those endpoints are quoted from the permitted note, not read from X outputs or treated as newly verified model results. No apparent precision in them rescues the original claim's missing measured matrix or missing PIT forecasts.

## What ran, commands and limits

Read-only discovery used `rg --files` and registry filename enumeration; no X code or X derived table was read. The permitted project brief and workboard were loaded to comply with startup instructions; no other package analysis was used. Python was initially absent from PATH; activating the existing project `.venv` resolved it. An initial uppercase `L1_v2` directory lookup was absent; filename discovery located `l1_reconciliation_v2` without reading its output content.

The numerical confirmation below ran from the repository root, exit code 0, shell wall time 3.1518 seconds; its measured computation took 0.08255 seconds. An earlier fuller calculation also exited 0, measured computation 0.1164 seconds, with matching results. Official NTTO/JNTO web fetches succeeded. Eurostat web access failed; an independent Python URL request was also blocked by socket permissions (caught exception; fetch unsuccessful despite script exit 0). No public source was changed or scraped, no consensus was consumed, no registration was made, and no scorer was necessary.

```powershell
& ".venv/Scripts/Activate.ps1"
@'
from pathlib import Path
import time
import pandas as pd
from scipy.stats import binom,norm,t,nct
from scipy.optimize import brentq
s=time.perf_counter()
q=lambda x: pd.Period('20'+x[-2:]+'Q'+x[0],freq='Q')
a=pd.read_csv('data/processed/adr/01_regional_annual.csv').query("region != 'total'")
r=pd.read_csv('data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv')
k=pd.read_csv('data/processed/overnight/02_kpi_panel_quarterly.csv').set_index('quarter')
h=pd.read_csv('data/processed/overnight/28_fx_hedge_disclosures.csv')
d=pd.read_csv('data/processed/adr/04_regional_quarterly.csv')
p=pd.read_csv('analysis/src/forecast_methods/regional_kernel_v1/public_inputs.csv')
print('annual',len(a),abs(100*a.revenue_musd/a.gbv_musd-a.take_rate_pct).max())
total=r.groupby('quarter').revenue_musd.sum()
print('regional',len(r),r.quarter.nunique(),r.basis.value_counts().to_dict(),100*(total/k.loc[total.index,'revenue_musd']-1).abs().max())
print('latest_input_publication',r.knowable_from.max(),p.publication_date.max())
print('adr',d.query("metric == 'adr_usd'").merge(r[['quarter','region']],on=['quarter','region']).basis.value_counts().to_dict())
print('registry',[f.name for f in Path('data/processed/forecast_methods/registry').glob('*.csv') if any(s in f.name.lower() for s in ['regional','origin','exposure']) or f.name.lower().startswith(('x__','x-','x_'))])
for name,start in [('W1','2023Q1'),('W2','2024Q1')]:
    rr=r[r.quarter.map(q).between(pd.Period(start),pd.Period('2026Q2'))]
    hh=h[h.quarter.map(q).between(pd.Period(start),pd.Period('2026Q2'))]
    print(name,'cells/quarters/fx_targets',len(rr),rr.quarter.nunique(),hh.gross_fx_ex_hedge_pp.notna().sum(),'season_counts',rr.query("region == 'na'").quarter.map(lambda x:q(x).quarter).value_counts().sort_index().to_dict())
ccys={'USD','AUD','BRL','CAD','EUR','GBP','INR','JPY','KRW','MXN'}
print('public_rows',len(p),p.provider.value_counts().to_dict())
for provider in ['NTTO','JNTO']:
    v=p[p.provider.eq(provider)]
    tot=v.visitors_or_nights.sum()
    matched=v.loc[v.currency.isin(ccys),'visitors_or_nights'].sum()
    if provider=='JNTO': matched+=p.loc[p.provider.eq('JNTO_CCY'),'visitors_or_nights'].sum()
    print(provider,tot,100*v.loc[v.origin_region.ne('UNRESOLVED'),'visitors_or_nights'].sum()/tot,100*matched/tot)
e=p[p.provider.eq('EUROSTAT')].set_index('origin')
print('Eurostat',e.visitors_or_nights.sum(),100*e.loc['FOR','visitors_or_nights']/e.visitors_or_nights.sum())
for n in [14,10]:
    cutoff=next(k for k in range(n+1) if binom.sf(k-1,n,.5)<=.05)
    p80=brentq(lambda p:binom.sf(cutoff-1,n,p)-.8,.5,1-1e-9)
    successes={14:10,10:7}[n]; rate=successes/n; z=norm.ppf(.975)
    den=1+z*z/n; center=(rate+z*z/(2*n))/den
    half=z*((rate*(1-rate)/n+z*z/(4*n*n))**.5)/den
    crit=t.ppf(.975,n-1)
    d80=brentq(lambda d:nct.sf(crit,n-1,d*n**.5)+nct.cdf(-crit,n-1,d*n**.5)-.8,0,3)
    print('power',n,cutoff,binom.sf(cutoff-1,n,.7),p80,'Wilson',successes,center-half,center+half,'paired_d80',d80)
for name,beta,scaled,lo,hi in [('W1',.879,.535,.65,1.15),('W2',.731,.447,.50,1.00)]:
    share=scaled/beta
    print('normalization',name,share,.95*share,hi-lo,.95-beta)
print('elapsed_seconds',time.perf_counter()-s)
'@ | python -
```

Only this new note was written. Parent owns board, scorer and git. No harness change is needed to express this audit's result.

## Interpretation

The original sentence is an evidence-limit statement and survives every attempted route to reverse it. Accounting accuracy and a coherent live scenario are useful engineering checks. They cannot stand in for measured exposure, archived forecasting vintages or a powered comparison. Keep the exact 0/14 and 0/10 completeness counts; do not quote them as accuracy scores, confidence intervals or proof that a regional approach could never work.

## RESUME

Parent can use the verdict **survived** for the original X sentence and the independently verified distinction between 72 cells, 18 totals, 14/10 retrospective observations and zero PIT forecasts. Future work should archive source vintages, identify Airbnb O-D/payment-currency exposure, preregister one prospective comparison and report predictive uncertainty that includes proxy and regional-GBV error. Preserve conditional profile intervals as conditional, retain both nested windows, and do not count scenario variants or normalization conventions as additional evidence. The Eurostat arithmetic is locally reproduced but its live API fetch remains unverified in this session.
