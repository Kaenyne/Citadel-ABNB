# REFUTE R power — independent counts, uncertainty and registration audit

Codex refuter · 2026-09-12 · branch `codex/lane1-full` · main audit: 2.279 seconds shell wall time / 0.0802 seconds measured computation. Token usage unavailable; not estimated.

## Verdict

**partial** — the exact sentence overstates the directly filed count. The source has **72 exact regional revenue cells: 56 labelled `filed` and 16 labelled `back_out`**, covering 18 quarters. The backed-out observations are fourth-quarter values derived from annual filings; they are filing-sourced, but not 16 additional directly filed quarterly observations. Calling all 72 “filed revenue cells” erases the source's explicit distinction. The total cell count of 72 is correct.

The conditional-composition warning survives the power attacks. The note's displayed 2024 operands reproduce a signed residual of −1.3943pp, and its reported ADR endpoints reproduce a 25.6940% relative halfwidth. I could not independently re-estimate the fitted 2.0457pp attribution or its 72 fitted residuals without the R fit/output state, which this assignment forbids reading. That limitation is not evidence that the number is false; it prevents treating subtraction from the note as an independent model replication.

An explicit corrected sentence is: **“The full-sample regional refresh is reported to match 72 exact filing-sourced revenue cells, including 16 backed-out fourth-quarter cells, and its reported 2024 ex-FX ADR attribution gap is 1.39pp; FY27 composition remains conditional.”** This is a correction, not a silent substitute for the original verdict.

## Pre-registered audit

Original exact sentence: “The full-sample regional refresh matches all 72 filed revenue cells but leaves a 1.39pp gap in 2024 ex-FX ADR attribution, so its FY27 composition remains conditional.”

Before calculation: independently count source revenue cells and their provenance, distinguish inverse accounting identities from forecast observations, inspect uncertainty/sensitivity axes and the rejected-registration correction, and try to reproduce the relevant ADR-gap arithmetic from permitted inputs. A number quoted by the R note will not be represented as independently re-estimated. At least five numbered attacks will state claim, attack, explicit result and evidence. Final verdict on the exact original sentence will be survived, refuted or partial; no weaker sentence will be substituted silently. No promotion pass line applies to this refuter.

Read only the assignment, R note, actual registry files if present, named raw/input sources and permitted harness/cheatsheet. Do not read R code or derived output tables. Write only this note; parent owns board, scorer and git.

## Numbered refutation attempts

### 1. Claim → all 72 revenue cells are filed. Attack → inspect the actual provenance and count independent quarter observations.

**Result: partial on the original claim; the “all 72 filed” wording is refuted under the source's own labels.** The named `L0_exact_regional_revenue.csv` has 72 unique region-quarter cells and no duplicates. Its 16 `back_out` cells are precisely four regions × fourth quarters of 2022–2025. Their source period metadata spans 365/366 days and identifies 10-K filings. For example, APAC 4Q22 revenue is $193M, labelled `back_out`, accession `0001559720-24-000006`, source vintage 2024-02-16. The derivation does not make it a direct quarterly filing cell.

| Inventory | Total cells n | Direct `filed` n | `back_out` n | Distinct quarters n |
| --- | ---: | ---: | ---: | ---: |
| Full input, 2022Q1–2026Q2 | 72 | 56 | 16 | 18 |
| W1 target span, 2023Q1–2026Q2 | 56 | 44 | 12 | 14 |
| W2 target span, 2024Q1–2026Q2 | 40 | 32 | 8 | 10 |

The proposed wording is stronger than “filing-sourced” or “exact”. The corrected count preserves all 72 valid accounting targets while distinguishing direct disclosure from derivation.

### 2. Claim → matching 72 cells supports the regional refresh. Attack → use the match as a large-sample validation success rate or a zero-error bootstrap.

**Result: survived only as the note's stated conditional accounting construction, not as forecasting evidence.** When regional revenue is inverted to define regional GBV or its conversion rate, `revenue = GBV × conversion` can hold for every positive admissible GBV. Resampling these exact identity residuals then produces a zero-width band irrespective of whether the regional decomposition is correct. A “72/72” Wilson interval would incorrectly treat imposed equalities as independent forecasting successes.

The R note itself reports exact inversion and zero identity-residual spread. Its maximum fitted error of 2.27e−13 USD millions is a numerical implementation receipt, not an independently reproduced measurement in this audit. I checked the source inventory and algebra, but did not read `disclosure_residuals.csv` or any R fitted table. The 72-cell source count and the reported 72-cell match must therefore remain separate pieces of evidence. Eighteen correlated quarters are not 72 independent economic forecast tests.

### 3. Claim → a 1.39pp 2024 ex-FX gap remains. Attack → reproduce the exact figure independently and challenge threshold selection.

**Result: partial verification, with an explicit replication boundary.** The note supplies a fitted 2024 within-region ex-FX attribution of 2.0457pp and comparator 3.44pp. Their subtraction is **−1.3943pp**; the magnitude rounds to 1.39pp and exceeds the pre-registered 0.8pp limit by **0.5943pp**. The note reports all three comparable years, not just the worst or best year: 2023 −0.2815pp, 2024 −1.3943pp, 2025 −0.0101pp. Each is one annual attribution comparison, not 16 independent errors because four regions and four quarters enter its construction.

However, 2.0457pp is a fitted-model output. The comparator is attributed to a prior named note rather than a directly observed standalone price statistic. The raw annual levels and interval inputs alone do not provide the fitted regional GBV/nights path, take-rate tilts, exact FX allocation or optimization state needed to independently re-estimate that annual attribution. I did not read another fit's code or use R derived outputs to manufacture an “independent” match. The 1.39pp arithmetic is checked; the exact fitted gap remains reported, not independently established by this refuter.

No standard error, p-value or stochastic probability of exceeding 0.8pp follows from three annual residuals with shared model assumptions. It is a pre-registered deterministic discrepancy threshold, which the reported result fails.

### 4. Claim → bootstrap spread identifies regional ADR adequately. Attack → reconstruct the endpoint width and distinguish 40 computational refits from new data.

**Result: survived for the conditionality warning; a precision claim would fail.** From the reported Latin America 2025Q1 endpoints, `(211.60 − 131.82) / (2 × 155.25) = 25.6940%`. The interval is asymmetric about its median: −15.0918% / +36.2963%. It fails a ±10% precision requirement under either endpoint interpretation. These calculations use the note's stated endpoints; the 40 individual fitted draws were not read.

The n=40 count measures bootstrap refits, not 40 independent historical samples. They reuse 18 quarters through four-quarter blocks; the observed span contains only 4.5 block-length equivalents. That ratio is a scale warning, not an assertion that effective n equals 4.5. Reweighting disclosure residuals preserves exact identities and conditions on the same anchor priors, smoothing, model structure and scenario path.

There is also finite Monte Carlo uncertainty in reported tail quantiles. For 40 independent conditional bootstrap draws, the p10 estimate lies around the fourth/fifth order statistics. An exact binomial order-statistic calculation gives a bracket from the **1st to 9th order statistics** with **96.9724% conditional coverage** for the underlying bootstrap-distribution p10. The number of draws below that population p10 has standard deviation 1.8974. This diagnoses quantile resolution; it is not a confidence interval for real Airbnb ADR. The corresponding illustrative Wilson calculation for 4/40 tail draws is [3.9580%, 23.0518%], again conditional on independent draws and not an observed forecast hit rate.

Without the 40 draw values there is no numerical order-statistic bracket in dollars to report honestly. More bootstrap draws would reduce Monte Carlo noise but would not add historical data or resolve uncertain priors.

### 5. Claim → full local rank and many constraints defeat the uncertainty objection. Attack → independently count observables and model dimensions.

**Result: survived for the conditionality warning.** The declared model arithmetic is 3 share logits × 18 quarters + 3 persistent regional take-rate tilts = **57 fitted parameters**, plus four supplied kernel coefficients = **61** metadata parameters. The annual source contains **16 region-year level cells** for 2022–2025, consistent with the declared soft annual anchor count. Those anchors are prior restrictions on levels, not 16 independent out-of-sample validation events.

I independently counted **118 included regional interval rows** within the 18-quarter span in the named L0 interval input: 50 nights-growth, 38 reported-ADR-growth and 30 ex-FX-ADR-growth rows; 90 are letter-integer intervals and 28 are buckets. Another 14 regional rows in that span are explicitly excluded. Including total-region rows yields 141 intervals, so the package's stated count of 127 constraints is not directly reproduced by either transparent raw-input filter. Its exact likelihood-selection/augmentation rule needs a separate constraint manifest; I do not guess which nine rows would turn 118 into 127.

The fitted Jacobian and its singular values are prohibited derived state in this audit, so rank 57/57 is only the note's report. Even if correct, full local rank is not an uncertainty bound. Near-collinearity, weak directional curvature and arbitrary persistent-tilt structure can coexist with full rank. The note's **34.62%** maximum anchor-strength sensitivity is also a reported model diagnostic, not independently recomputed here. It reinforces the warning but is not a 95% error bound or a probability distribution over priors.

### 6. Claim → 397 arrivals rows provide historical test power. Attack → aggregate the actual input months and enforce availability separately.

**Result: survived for the note's zero historical-coverage conclusion.** The normalized current-download source has exactly **397 rows, six series, no duplicate series/month pairs**, and every row has `knowable_from=2026-09-13` with `current_revised_download; not historical release` basis. The source manifest records seven HTTP-200 endpoints, including a rejected DataTur monetary workbook. HTTP success is not a usable count-series observation.

| Series | Monthly rows n | Complete quarters n | Incomplete quarters n | Retrospective lag-one growth cells W1/W2 n | Historically admissible W1/W2 n |
| --- | ---: | ---: | ---: | --- | --- |
| NTTO US | 66 | 22 | 0 | 14 / 10 | 0 / 0 |
| JNTO Japan | 67 | 22 | 1 | 14 / 10 | 0 / 0 |
| Eurostat Spain | 66 | 22 | 0 | 14 / 10 | 0 / 0 |
| Eurostat France | 66 | 22 | 0 | 14 / 10 | 0 / 0 |
| Eurostat Italy | 66 | 22 | 0 | 14 / 10 | 0 / 0 |
| Eurostat Germany | 66 | 22 | 0 | 14 / 10 | 0 / 0 |

I calculated complete quarter sums, year-on-year growth, then a one-quarter lag using only the normalized input. The 14/10 covariate counts reproduce the overlap obtainable **if availability is ignored**. They do not independently reproduce any fitted regional correlation coefficient, since that would require R's fitted regional outcomes. Every current input date is later than the historical guide origins. There is zero PIT forecast-error n; no finite historical forecasting effect size, RMSE confidence interval or superiority test can be estimated from that absence. W2 is nested in W1, and four European destinations do not create four independent regional forecast histories.

### 7. Claim → the LIVE-registration correction restores a usable issued forecast. Attack → inspect the preserved actual rows, hashes and surviving shared paths.

**Result: survived for the note's rejection/abstention statement; a restoration-of-evidence interpretation is refuted.** The two preserved registry files each contain six rows. All **12 rows** are stamped `vintage_date=2026-09-11`, `window=LIVE`, `prior_basis=full_sample`, `knowable_from=2026-09-06`, `n_params=61`, `n_train=18`. Their own notes admit a later reconstruction and describe the earlier date as a format slot. Data available by 6 September does not establish that these particular forecasts were issued on 11 September. A full-sample label does not change that distinction.

Both preserved files' SHA-256 hashes match the rejection manifest, whose preservation timestamp is 2026-09-13T00:47:59.310978+00:00. Both original shared-registry paths are currently absent. This independently confirms the preserved bytes against the manifest and the current withdrawal state; it does not independently prove every historical filesystem step.

The archived files hold six target quarters, 2026Q3–2027Q4, in two representations of the same path. They are not 12 independent forecasts or six FY27 quarters. Exactly four revenue rows comprise FY27 and sum to **$15,974.558012M**, reproducing the note's $15,974.6M conditional 2/3-weight row. Neither the rejected LIVE rows nor a corrected local candidate creates W1/W2 historical issuance.

Per the read boundary, I did not inspect the derived replacement-candidate table or rerun the correction. Therefore the note's equality claim for all 12 replacement points, actual candidate creation timestamp and byte preservation of 19 analytical outputs remain reported receipt claims. The verified withdrawal state is sufficient to reject any assertion that format acceptance provides historical validation.

### 8. Claim → narrow FY27 composition bands imply confident annual forecasts. Attack → separate scenario axes, identities and genuine uncertainty.

**Result: survived for the original conditionality warning.** The note discloses four ADR anchor strengths (baseline 5%, sensitivities 2.5%, 10%, effectively none), three kernel weights, six descriptive arrivals candidates, two nested historical windows, four-quarter bootstrap blocks, one seed and 40 refits. Those are specification/assumption axes, not extra observations. No annual forecast target has been realised in the input. The full unreported development-search count cannot be recovered within scope.

The FY27 attribution itself has assumed components with zero bootstrap spread. Its multiplicative arithmetic checks: `(1 − 1.065/100) × 1.03 − 1 = 1.90305%`; the cross term is −0.03195pp. The within-region remainder is `3.00 − 0.63 − 0.04 = 2.33pp` when seats and FX are held flat. Forty identical +3% growth assumptions cannot establish that growth with zero real-world uncertainty.

The three reported FY27 conditional revenue-band widths are $34.9M, $35.5M and $36.3M, whereas changing the kernel weight moves the central level by $120.9M and annual growth by **2.235pp**. These are arithmetic comparisons of the note's displayed numbers, not newly estimated predictive intervals. The sensitivity range and conditional bootstrap must not be combined as if both had calibrated probabilities. The bands omit growth, FX, lambda and booking-path uncertainty; that omission directly supports keeping FY27 composition conditional.

## What ran and exact-number limitations

The independent calculation used the named L0 revenue/interval inputs, the annual ADR anchor input, the normalized monthly arrivals **source input** and its download manifest, and the actual preserved rejected registry files plus their preservation manifest. The normalized arrivals input is a current-download input to R, not its derived quarterly/correlation output. The supplied regional projection input and annual ADR decomposition source were inspected for input provenance; no alternative decomposition was substituted for R's fitted 2024 result. No R code, fitted residual table, uncertainty-draw table or replacement-candidate table was read. No download or source update was performed.

The audit was pre-registered in this new note before calculation. The main command below ran from the repository root using the project `.venv`, exit 0, 2.2795 seconds shell wall time, 0.08016 seconds measured computation. The follow-up interval-inventory command also exited 0. Commands are reproduced verbatim. Only this assigned note was written. No scorer was needed because no forecast was registered.

```powershell
& ".venv/Scripts/Activate.ps1"
@'
import json,time,hashlib
from pathlib import Path
import pandas as pd
from scipy.stats import binom,norm
s=time.perf_counter()
root=Path('.')
q=lambda x:pd.Period('20'+x[-2:]+'Q'+x[0],freq='Q')
r=pd.read_csv('data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv')
r['q']=r.quarter.map(q)
print('REVENUE',json.dumps({'rows':len(r),'quarters':r.quarter.nunique(),'basis':r.basis.value_counts().to_dict(),'duplicates':int(r.duplicated(['quarter','region']).sum()),'backout_quarters':r.loc[r.basis.eq('back_out'),'quarter'].unique().tolist(),'backout_days':r.loc[r.basis.eq('back_out'),'period_days'].unique().tolist()}))
print('BACKOUT_EXAMPLE',r.loc[r.basis.eq('back_out')].head(1).drop(columns='q').to_dict('records'))
for w,start in [('W1','2023Q1'),('W2','2024Q1')]:
    cells=r[r.q.between(pd.Period(start),pd.Period('2026Q2'))]
    print('WINDOW',w,'cells',len(cells),'quarters',cells.quarter.nunique(),'basis',cells.basis.value_counts().to_dict())
a=pd.read_csv('data/processed/adr/01_regional_annual.csv')
print('ANNUAL_ANCHOR_CELLS',len(a[(a.region.ne('total'))&(a.year.between(2022,2025))]))
i=pd.read_csv('data/processed/forecast_methods/L0/L0_interval_observations.csv',comment='#')
j=i[i.region.isin(['na','emea','latam','apac'])&i.included]
j=j[j.quarter_or_year.isin(r.quarter)]
print('INTERVALS',len(i),'regional_included_in_span',len(j),'metrics',j.metric.value_counts().to_dict(),'basis',j.basis.value_counts().to_dict(),'excluded_in_span',int((i.region.isin(['na','emea','latam','apac'])&~i.included&i.quarter_or_year.isin(r.quarter)).sum()))
arrival=pd.read_csv('data/processed/forecast_methods/l1_reconciliation_v3/arrivals_monthly_current.csv')
arrival['q']=pd.PeriodIndex(arrival.month,freq='M').asfreq('Q')
print('ARRIVALS',len(arrival),'series',arrival.series.nunique(),'duplicates',int(arrival.duplicated(['series','month']).sum()),'knowable',arrival.knowable_from.unique().tolist())
for name,g in arrival.groupby('series'):
    group=g.groupby('q').value.agg(['size','sum'])
    complete=group[group['size'].eq(3)]['sum']
    growth=100*(complete/complete.shift(4)-1)
    feature=growth.copy();feature.index=feature.index+1
    matches=[int(feature.reindex(pd.period_range(start,'2026Q2',freq='Q')).notna().sum()) for start in ['2023Q1','2024Q1']]
    print('ARRIVAL_SERIES',name,'months',len(g),'complete_quarters',len(complete),'incomplete_quarters',int(group['size'].ne(3).sum()),'retrospective_lag1_W1_W2',matches)
rej=Path('data/processed/forecast_methods/l1_reconciliation_v3/UNREGISTERED_rejected_registry_20260913')
manifest=json.loads((rej/'rejection_manifest.json').read_text(encoding='utf-8'))
for entry in manifest['files']:
    path=Path(entry['preserved_path'])
    frame=pd.read_csv(path)
    live=Path(entry['original_registry_path'])
    print('REJECTED_REGISTRY',json.dumps({'name':path.name,'sha256_matches_manifest':hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'],'rows':len(frame),'shared_exists':live.exists(),'vintages':frame.vintage_date.unique().tolist(),'windows':frame.window.unique().tolist(),'basis':frame.prior_basis.unique().tolist(),'quarter_n':frame.quarter.nunique(),'fy27_rows':int(frame.quarter.str.startswith('2027').sum()),'n_params':frame.n_params.unique().tolist(),'n_train':frame.n_train.unique().tolist()}))
    if frame.target.eq('revenue_musd').all(): print('REJECTED_FY27_REVENUE_SUM',frame.loc[frame.quarter.str.startswith('2027'),'point'].sum())
print('SOURCE_RESIDUAL_ARITHMETIC',2.0457-3.44,'over_08_threshold',abs(2.0457-3.44)-.8)
print('BOOTSTRAP_REPORTED_ENDPOINT_ARITHMETIC',100*(211.60-131.82)/(2*155.25),'lower_rel',100*(155.25-131.82)/155.25,'upper_rel',100*(211.60-155.25)/155.25)
z=norm.ppf(.975); n=40;k=4;rate=k/n;den=1+z*z/n
center=(rate+z*z/(2*n))/den;half=z*((rate*(1-rate)/n+z*z/(4*n*n))**.5)/den
lo=int(binom.ppf(.025,n,.1));hi=int(binom.ppf(.975,n,.1))+1
print('BOOTSTRAP_RANK_DIAGNOSTIC','n',n,'p10_orders',[lo,hi],'coverage',binom.cdf(hi-1,n,.1)-binom.cdf(lo-1,n,.1),'tail_count_SD',(n*.1*.9)**.5,'Wilson_if_4_of_40',[center-half,center+half])
print('FY27_ATTRIBUTION_ARITHMETIC','mix_cross',-1.065*.03,'blended',(1-1.065/100)*1.03*100-100,'remainder',3-.63-.04)
print('elapsed_seconds',time.perf_counter()-s)
'@ | python -
```

The follow-up source-inventory command was:

```powershell
& ".venv/Scripts/Activate.ps1"
@'
import pandas as pd
r=pd.read_csv('data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv')
i=pd.read_csv('data/processed/forecast_methods/L0/L0_interval_observations.csv',comment='#')
s=i[i.included & i.quarter_or_year.isin(r.quarter)]
print('ALL_INCLUDED_MATCHED_QUARTERS',len(s))
print(s.groupby(['region','metric','basis']).size().to_string())
print('OUTSIDE_SPAN_INCLUDED_REGIONAL',i[i.included&i.region.isin(['na','emea','latam','apac'])&~i.quarter_or_year.isin(r.quarter)][['quarter_or_year','region','metric','basis']].to_string(index=False))
'@ | python -
```

## Interpretation

The source precision and the model's identification are different questions. All 72 source targets are exact accounting cells, but only 56 carry the directly filed label. Neither exact inversion nor 40 conditional refits supplies predictive power. The 2024 discrepancy remains numerically consistent with the note, but its fitted operands were not independently re-estimated here. The exact proposed sentence therefore receives **partial**, while its warning to keep FY27 composition conditional is supported. This verdict does not discard the backed-out source values or claim that their revenue amounts are wrong.

## RESUME

Parent should record **partial** on the original sentence and explicitly correct “72 filed” to “72 exact filing-sourced cells, including 16 backed-out fourth-quarter cells.” Preserve the rejected registry files and their verified hashes; no R rows currently remain at the original shared paths. A next version needs a reproducible constraint manifest explaining the reported 127 likelihood rows, a permitted independent rerun of the 2024 attribution, archived arrivals vintages and uncertainty that includes priors, FX, growth and booking paths. Do not promote 40 refits or zero identity residuals into independent validation. Only this assigned note was written; parent owns board, scorer and git.
