# REFUTE R — mechanism lens

Agent: Codex ref_a_power (R mechanism assignment) · 2026-09-12 · branch `codex/lane1-full`.

## Preregistered refutation protocol

Written before independent calculations. The assignment has no statistical pass line; the required result is an adversarial verdict on the original exact sentence: **“The full-sample regional refresh matches all 72 filed revenue cells but leaves a 1.39pp gap in 2024 ex-FX ADR attribution, so its FY27 composition remains conditional.”** Independently count the named filed-revenue input cells, challenge exact-by-inversion matching, reconstruct the displayed residual and attribution identities, separate conditional bootstrap spread from identifying information and historical forecast coverage, and audit the rejected registration dates against any actual surviving/preserved registry records permitted by the assignment. No R model code or derived output tables will be read. An exact-number replication limitation will be stated explicitly rather than represented as a successful independent re-fit. At least five numbered attacks and one final verdict exactly `survived`, `refuted`, or `partial` will follow. Parent owns board, scorer and git.

## Verdict

**partial.** The literal provenance claim needs correction: the supplied 72-cell source contains **56 cells marked `filed` and 16 marked `back_out`**, the latter calculated for Q4 from annual revenue less the first three quarters. All 72 anchors independently reproduce from the referenced XBRL input, but they are not 72 directly filed quarterly observations. The 2024 residual subtraction is **2.0457 − 3.44 = −1.3943pp**, supporting the quoted 1.39pp magnitude, and the conclusion that FY27 composition remains conditional survives the mechanism attacks. The fitted 2.0457pp and the R model's reported matching error were not independently re-estimated because its code and derived tables are prohibited reads.

This vote is on the original exact sentence. If “filed” was intended broadly to include values calculated from filings, that would preserve the intended point, but I do not silently substitute that interpretation for the source's explicit basis labels. A precise correction for review is: **“The full-sample regional refresh matches 72 filing-derived quarterly revenue anchors—56 directly filed and 16 Q4 back-outs—but leaves a 1.39pp gap in 2024 ex-FX ADR attribution, so its FY27 composition remains conditional.”** The reported model match in that corrected sentence remains subject to the execution-replication limitation stated below. This `partial` vote does not count as a survived vote on the original sentence.

## Independently reconstructed input cells

The allowed L0 input names `data/processed/overnight/10_xbrl_revenue_geography.csv` as its raw source and provides a source-row index, accession and filing date for each cell. I independently followed those indices, checked accessions and dates, divided raw USD by one million, and subtracted Q1–Q3 for Q4 rows. Every reconstructed anchor equals the L0 amount exactly at supplied precision.

| Input slice | Quarters n | Region-quarter cells n | `filed` n | `back_out` n | Reconstructed anchor max error, USD m |
|---|---:|---:|---:|---:|---:|
| Full source, 2022Q1–2026Q2 | 18 | 72 | 56 | 16 | 0 |
| W1 target-quarter slice, 2023Q1–2026Q2 | 14 | 56 | 44 | 12 | 0 |
| W2 target-quarter slice, 2024Q1–2026Q2 | 10 | 40 | 32 | 8 | 0 |

All 16 back-outs are four regions in Q4 of 2022, 2023, 2024 and 2025. For example, the 2022 APAC source row is annual revenue of $622m in accession `0001559720-24-000006`, filed 16 February 2024. Subtracting its three earlier quarterly anchors gives the $193m Q4 value. The source's 365/366-day duration on back-out rows belongs to the annual filing input, even though the normalized quarter is Q4. These are legitimate filing-derived accounting anchors; calling them direct quarterly disclosures overstates what was observed.

W1 and W2 slices overlap and the same revenue observations appear in annual and quarterly accounting relations. They are not 56 and 40 successful historical forecasts. The source also contains later-filed comparative observations, appropriate for the stated full-sample fit but not automatically available at the original guide dates.

## Exact matching is an identity, not a price test

For any positive regional base B and observed revenue R, defining an implied conversion coefficient `tau = R/B` forces `tau*B = R`. I applied this construction to all 72 raw anchors with two arbitrary bases, 1,000 and 1,700, obtaining **144 exact-by-inversion examples**, maximum decimal arithmetic error 1e−37 USD m. The regional base changes substantially without changing reproduced revenue.

This counterexample concerns what an identity can establish. It is not an alternative fit of R's constrained 57-parameter model: persistent take-rate tilts, total-GBV constraints and annual priors can restrict which arbitrary bases are admissible jointly. But matching the revenue identities alone cannot validate those additional structural assumptions, identify regional ADR or establish forecast performance. The observed anchors' independent reconstruction is also distinct from checking the execution of R's prohibited model outputs.

## Attribution arithmetic and its limits

The named input note `l1-reconciliation.md` §4 confirms annual comparison terms of 3.10pp, 3.44pp and 3.41pp. It also states that the regional and consolidated FX allocations can split the same blended reported-ADR growth differently. Using the R note's reported fitted terms gives:

| Year | Regions × quarters n | R fitted term as reported, pp | Named comparison term, pp | Independently subtracted residual, pp | Below 0.8pp absolute gap? |
|---|---:|---:|---:|---:|---|
| 2023 | 4 × 4 | 2.8185 | 3.10 | −0.2815 | Yes |
| 2024 | 4 × 4 | 2.0457 | 3.44 | −1.3943 | No |
| 2025 | 4 × 4 | 3.3999 | 3.41 | −0.0101 | Yes |

The 2024 gap exceeds the pass threshold by **0.5943pp**. The subtraction and its two-decimal magnitude reproduce; the 2.0457pp fitted term does not become independently estimated merely by subtracting a verified comparator. No R derived residual or regional fit table was read.

The simplest alternative explanation is a different allocation between within-region ex-FX growth and the FX component. Shifting attribution between those terms can leave reported ADR, total GBV and revenue unchanged. Thus a 1.39pp attribution discrepancy is not a measured 1.39pp revenue-growth forecast error, and the older comparator is not established here as the uniquely correct economic split. It should not be subtracted mechanically from FY27 growth. The original sentence's caution about conditional composition is justified; any causal or revenue-bias interpretation would be stronger than the evidence.

## FY27 composition is substantially imposed

The supplied regional forecast source has Base FY27 nights assumptions of 6%, 7%, 16% and 15% for NA, EMEA, LatAm and APAC, and a total within-region ex-FX ADR assumption of 3% with zero FX. Those are scenario inputs, not coefficients selected from historical arrivals. Taking the R note's geographic-mix result as its reported input, its remaining ADR subtotal is deterministic:

`(1 − 0.010650) × (1 + 0.030000) − 1 = 0.0190305`.

| Arithmetic result | Scenario/refit n represented | Independent value, pp | Meaning |
|---|---|---:|---|
| Mix × common price cross-term | One conditional scenario | −0.031950 | Product of −1.0650% and +3% |
| Blended ADR subtotal | One conditional scenario | +1.903050 | Exactly +3 + 1.03 × mix |
| Blended p10 from stated mix p10 | 40 reported conditional refits | +1.771004 | Exactly +3 + 1.03 × (−1.1932) |
| Blended p90 from stated mix p90 | 40 reported conditional refits | +1.996780 | Exactly +3 + 1.03 × (−0.9740) |
| Joint price/subregional remainder | Fixed assumptions | +2.330000 | 3.00 − 0.63 − 0.04, with the other listed channels held at zero |

The entire displayed blended-ADR band is a monotonic affine transformation of the mix band while common price growth is fixed. It is not an additional independent estimate of future price growth. The unchanged p10/p90 on +3%, unit size, LOS and the remainder are consequences of fixed assumptions. A residual of +2.33pp does not separately identify like-for-like price and subregional composition.

The mix term belongs inside blended ADR in `GBV = nights × blended ADR`. Adding it again to GBV or revenue would apply the same geographic effect twice. This identity discipline is necessary, but it does not make the component forecasts observed or their priors correct.

## Conditional uncertainty, rank and kernel weights

From the note's displayed Latin America 2025Q1 quantiles, `(211.60−131.82)/(2×155.25)` is **25.6940%**, reproducing its relative halfwidth. Relative to the median, the actual endpoints are **−15.0918% / +36.2963%**, so the interval is asymmetric and should not be read as a symmetric ±25.69% confidence interval. Both sides fail a ±10% precision target.

The 40 bootstrap refits are conditional draws from one 18-quarter dataset under the chosen constraints. They are not 40 independent historical forecast periods. Bootstrapping residuals of identities produces zero spread by construction; the nonzero disclosure-reweighting bands answer a different conditional question. The note reports 34.62% sensitivity to anchor strength and local rank 57/57. These model-dependent statistics were not independently refit. Full local rank cannot demonstrate narrow uncertainty: even a one-parameter observation `y = epsilon*theta` has rank one for positive epsilon while the uncertainty in theta becomes arbitrarily large as epsilon approaches zero.

The note's three weight scenarios span **2.235pp** of FY27 growth, versus a **0.231pp** displayed conditional growth interval width per fixed-weight row. The weight span is not a probability interval, but it shows a material uncertainty dimension absent from the bootstrap interval. Changing the weight also changes FY26's denominator:

| Lag-one weight | Scenario n | Growth from displayed FY27/FY26 dollar levels | Growth if FY26 is held at $14,243.9m |
|---|---:|---:|---:|
| 0.33 | 1 | 9.916525% | 11.301680% |
| 0.50 | 1 | 11.037697% | 11.729934% |
| 2/3 | 1 | 12.150464% | 12.150464% |

Minor differences from the note's three-decimal growth figures are explained by its dollar levels being rounded to one decimal. The fixed-denominator column is an arithmetic diagnostic, not a substitute forecast. It shows why the growth span cannot be attributed solely to changes in FY27 dollars or to regional composition.

## Arrivals and the rejected registration

The normalized monthly arrivals file is an input source dataset, not an R model output table. It independently contains **397 unique series-month observations**: NTTO 66, JNTO 67, and Spain/France/Italy/Germany 66 each. There are 132 complete three-month series-quarter groups and one partial group. All **397** records are stamped `knowable_from=2026-09-13`, with `current_revised_download; not historical release`. Reference months in 2021–2026 do not establish historical publication. The file mixes 133 person-count records and 264 nonresident accommodation-night records; these require an economic mapping to Airbnb booking activity rather than direct pooling.

These current revised inputs are later than the historical W1 and W2 guides. Thus the note's absence of admissible historical arrivals coefficients is supported by the raw timing field. Expanding destinations or fitting retrospective correlations would not restore historical availability, nor establish a bridge from inbound activity to domestic/origin booking demand. No future or historical return series is inferred.

The preserved rejected files are actual R registry records, now kept outside the shared registry. They have:

| Registry audit | Files n | Rows n | Independent finding |
|---|---:|---:|---|
| Preserved revenue object | 1 | 6 | Quarters 2026Q3–2027Q4; every vintage 2026-09-11 |
| Preserved growth object | 1 | 6 | Same quarters/vintages; labelled LIVE/full_sample |
| Row notes admitting a later rebuild | 2 | 12 | Every note says rebuilt 2026-09-12 |
| Active shared `l1-reconciliation-v3__*.csv` objects | 0 | 0 | Both rejected objects are absent |

The archived `knowable_from=2026-09-06` field does not authenticate the later reconstruction as an issued September-11 forecast. The frozen schema accepting September 11 as a format slot establishes neither actual issuance nor point-in-time construction. `full_sample` describes estimation basis; it cannot repair an inaccurate vintage. The documented rejection was therefore warranted.

The preserved numeric rows remain arithmetically coherent: the four 2027 revenue points sum to **$15,974.558012m**; the two 2026 actual quarters plus the two forecast quarters sum to **$14,243.852275m**, implying **12.150545%** FY27 growth. All six archived quarterly growth values agree with their respective revenue ratios within 1.53e−14pp. This confirms the distinction between numeric consistency and invalid dating. It does not reinstate those records as forecasts.

The current local candidate table, correction receipts and preservation manifest were not inspected because the assignment excludes R derived output tables. Accordingly I verify the preserved originals, their contradiction in dates, their numerical identities and their current absence from the shared registry; I do not independently certify the separate claim that every post-correction candidate point and all 19 analytical outputs remain byte-identical. Parent owns any broader correction audit.

## Numbered refutation attempts

1. **Claim → the refresh matches 72 filed quarterly revenue cells. Attack →** Count the raw source basis labels and independently rebuild all cells from their indexed XBRL records. **Result → partially:** 72 valid filing-derived anchors reproduce exactly, but only 56 are directly filed quarterly rows; 16 are annual-minus-Q1–Q3 Q4 back-outs. This is the successful attack on the original exact wording and the reason for the final `partial` vote.

2. **Claim → a 72-cell exact match validates the regional economic reconstruction. Attack →** Construct two different positive bases for each observed revenue and solve the implied conversion ratio. **Result → survived for the conditional-evidence conclusion; the stronger validation inference is refuted:** 144 examples reproduce the same revenue to arithmetic precision while the bases differ. This is an identity counterexample, not an alternative constrained R fit. Matching targets by inversion cannot by itself identify ADR or take-rate economics.

3. **Claim → the 2024 attribution gap is 1.39pp and signals unresolved composition. Attack →** Read the named comparator note's 3.44pp anchor, subtract it from R's displayed 2.0457pp, and test whether reallocating FX could change the gap without changing reported ADR. **Result → survived with an explicit replication limit:** subtraction gives −1.3943pp and fails the 0.8pp gate, while the source note identifies a competing FX partition. The fitted 2.0457pp was not independently re-estimated. The gap is not a measured revenue-growth miss.

4. **Claim → the FY27 subtotal and its tight band provide independently estimated price-growth evidence. Attack →** Recompute the common-price/mix product and transform both mix quantiles. **Result → survived for the original conditional conclusion; stronger identification is refuted:** +1.90305pp and its endpoints are mechanically +3 + 1.03×mix. The +3pp and +2.33pp terms are fixed assumptions/remainders, not independently learned future prices. Adding mix again to GBV would double-count it.

5. **Claim → rank 57/57 or 40 bootstrap refits identify regional ADR precisely. Attack →** Recompute the displayed interval's scale and asymmetry, distinguish residual bootstrapping from disclosure reweighting, and construct a full-rank but weakly informative observation. **Result → survived for the original caution:** the displayed interval is −15.09%/+36.30% around its median, and full rank imposes no narrow-uncertainty guarantee. The reported 34.62% prior sensitivity was not independently refit; treating conditional spread as complete predictive uncertainty would be unsupported.

6. **Claim → the FY27 revenue/growth bands validate a stable composition forecast. Attack →** Compare the 2.235pp weight span with the 0.231pp conditional interval and hold FY26's denominator fixed as a diagnostic. **Result → survived for conditionality:** weight changes affect both years, so neither the bootstrap band nor the change in annual growth isolates regional composition. The imported lambda and future booking paths remain additional assumptions.

7. **Claim → hundreds of public arrivals observations supply historical validation. Attack →** Independently count series-months, units, complete quarters and availability dates. **Result → survived for the no-validated-arrivals conclusion:** 397 observations are all current revised downloads stamped September 13, with zero date-admissible historical inputs under the stated rule. The series also measure inbound destination persons/nights, not the full Airbnb booking mechanism. More retrospective rows do not establish PIT coverage.

8. **Claim → accepted format dates or corrected file status can establish historical forecast issuance. Attack →** Read both preserved rejected registry files, compare their vintage fields with their later-rebuild notes, check their absence from the active directory and recompute their numeric identities. **Result → survived for the rejection rationale:** all 12 records are misdated even though their arithmetic is coherent. Active files are absent, as the correction says. Exact equality to the unread local candidates and the full correction audit remain outside this read scope; format validity is not historical issuance evidence.

## What ran and reproducibility

All calculations ran from the repository root with the project `.venv` first on PATH. The exact main calculation exited **0**, Python-measured runtime **0.012757 seconds**, tool wall time **0.907273 seconds**. A denominator-sensitivity calculation exited **0**, tool wall time **0.303234 seconds**. Overall agent wall time and token usage are unavailable, not estimated.

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + [IO.Path]::PathSeparator + $env:PATH
@'
import csv,hashlib,json,time
from collections import Counter,defaultdict
from decimal import Decimal,getcontext
from pathlib import Path
getcontext().prec=40
D=Decimal; started=time.perf_counter()
paths={
 'revenue':'data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv',
 'xbrl':'data/processed/overnight/10_xbrl_revenue_geography.csv',
 'arrivals':'data/processed/forecast_methods/l1_reconciliation_v3/arrivals_monthly_current.csv',
 'forecast_input':'data/processed/overnight/10_regional_forecast.csv',
 'rejected_revenue':'data/processed/forecast_methods/l1_reconciliation_v3/UNREGISTERED_rejected_registry_20260913/l1-reconciliation-v3__fy27_revenue.csv',
 'rejected_growth':'data/processed/forecast_methods/l1_reconciliation_v3/UNREGISTERED_rejected_registry_20260913/l1-reconciliation-v3__fy27_growth.csv'}
def read(k):
 with Path(paths[k]).open(encoding='utf-8-sig',newline='') as f:
  return list(csv.DictReader(f))
r=read('revenue'); x=read('xbrl'); a=read('arrivals'); fore=read('forecast_input'); rv=read('rejected_revenue'); rg=read('rejected_growth')
def canon(q):
 return f'20{q[2:]}Q{q[0]}'
bycell={(v['quarter'],v['region']):v for v in r}
assert len(bycell)==len(r)==72
quarter_counts=Counter(v['quarter'] for v in r)
assert len(quarter_counts)==18 and set(quarter_counts.values())=={4}
rebuild=[]
for v in r:
 s=x[int(v['source_row'])]
 assert s['accn']==v['accn'] and s['filed']==v['vintage']
 value=D(s['value_usd'])/D(1000000)
 if v['basis']=='back_out':
  assert v['quarter'].startswith('4Q') and s['start'].endswith('01-01')
  value-=sum(D(bycell[(f'{q}Q{v["quarter"][2:]}',v['region'])]['revenue_musd']) for q in [1,2,3])
 rebuild.append({'quarter':v['quarter'],'region':v['region'],'basis':v['basis'],'error_musd':value-D(v['revenue_musd'])})
windows=[]
for w,first in [('all','2022Q1'),('W1','2023Q1'),('W2','2024Q1')]:
 z=[v for v in r if first<=canon(v['quarter'])<='2026Q2']
 windows.append({'window':w,'quarters':len(set(v['quarter'] for v in z)),'cells':len(z),'basis':dict(Counter(v['basis'] for v in z))})
# Exact-by-inversion counterexample: two arbitrary positive regional bases.
identity_errors=[]
for v in r:
 y=D(v['revenue_musd'])
 for base in [D('1000'),D('1700')]:
  implied_rate=y/base
  identity_errors.append(implied_rate*base-y)
residuals=[{'year':y,'within_region_note_pp':D(m),'comparator_pp':D(c),'residual_pp':D(m)-D(c),'passes_0_8':abs(D(m)-D(c))<D('.8')} for y,m,c in [(2023,'2.8185','3.10'),(2024,'2.0457','3.44'),(2025,'3.3999','3.41')]]
mix=D('-1.0650'); price=D('3')
composition={'cross_pp':mix*price/100,'blended_pp':mix+price+mix*price/100,'q10_from_mix_pp':D('-1.1932')*D('1.03')+3,'q90_from_mix_pp':D('-.9740')*D('1.03')+3,'price_subregional_remainder_pp':3-D('.63')-D('.04')}
interval={'relative_halfwidth_pct':(D('211.60')-D('131.82'))/(2*D('155.25'))*100,'downside_from_median_pct':(1-D('131.82')/D('155.25'))*100,'upside_from_median_pct':(D('211.60')/D('155.25')-1)*100,'reported_anchor_sensitivity_pct':D('34.62')}
months=defaultdict(set)
for v in a:
 year,month=map(int,v['month'].split('-'))
 months[(v['series'],year,(month-1)//3+1)].add(month)
monthly_summary={'rows':len(a),'unique_series_months':len(set((v['series'],v['month']) for v in a)),'series_rows':dict(Counter(v['series'] for v in a)),'knowable_from':dict(Counter(v['knowable_from'] for v in a)),'complete_series_quarters':sum(len(z)==3 for z in months.values()),'incomplete_series_quarters':sum(len(z)<3 for z in months.values())}
actual=defaultdict(D)
for v in r: actual[canon(v['quarter'])]+=D(v['revenue_musd'])
forecasts={v['quarter']:D(v['point']) for v in rv}
levels={**actual,**forecasts}
growth_err=[]
for v in rg:
 q=v['quarter']; prior=f'{int(q[:4])-1}{q[4:]}'
 growth_err.append(100*(levels[q]/levels[prior]-1)-D(v['point']))
fy27=sum(v for q,v in forecasts.items() if q.startswith('2027'))
fy26=sum(levels[f'2026Q{q}'] for q in [1,2,3,4])
registry_dir=Path('data/processed/forecast_methods/registry')
print(json.dumps({'revenue_windows':windows,'raw_revenue_rebuild_max_error_musd':max(abs(v['error_musd']) for v in rebuild),'backout_quarters':sorted(set(v['quarter'] for v in r if v['basis']=='back_out')),
 'inversion_examples_n':len(identity_errors),'inversion_max_error':max(map(abs,identity_errors)),
 'annual_attribution':residuals,'FY27_composition':composition,'regional_interval_from_displayed_quantiles':interval,'arrivals':monthly_summary,
 'forecast_source_base_FY27':[{'region':v['region'],'nights_yoy_pct':v['nights_yoy_pct'],'adr_exfx_yoy_pct':v['adr_exfx_yoy_pct'],'fx_pp_on_revenue':v['fx_pp_on_revenue']} for v in fore if v['period']=='FY27' and v['scenario']=='base'],
 'rejected_registry':{'files':2,'rows':len(rv)+len(rg),'dates':dict(Counter(v['vintage_date'] for v in rv+rg)),'labels':dict(Counter((v['window']+' '+v['prior_basis']) for v in rv+rg)),'row_notes_admit_later_rebuild':all('rebuilt 2026-09-12' in v['notes'] for v in rv+rg),'active_R_files':[p.name for p in registry_dir.glob('l1-reconciliation-v3__*.csv')],'FY27_revenue_sum_musd':fy27,'FY26_revenue_sum_musd':fy26,'FY27_growth_pct':100*(fy27/fy26-1),'quarterly_growth_identity_max_error_pp':max(map(abs,growth_err))},
 'sha256':{k:hashlib.sha256(Path(p).read_bytes()).hexdigest() for k,p in paths.items()},'runtime_seconds':round(time.perf_counter()-started,6)},indent=2,default=str))
'@ | python -X utf8 -
```

Exact denominator-sensitivity calculation:

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + [IO.Path]::PathSeparator + $env:PATH
@'
from decimal import Decimal as D
import json
rows=[]
for w,fy26,fy27 in [('0.33','14423.4','15853.7'),('0.50','14332.7','15914.7'),('2/3','14243.9','15974.6')]:
 rows.append({'weight':w,'growth_from_rounded_levels_pct':str((D(fy27)/D(fy26)-1)*100),'growth_if_FY26_denominator_fixed_pct':str((D(fy27)/D('14243.9')-1)*100)})
print(json.dumps({'kernel_denominator_sensitivity':rows,'growth_weight_span_pp':str(D('12.151')-D('9.916')),'conditional_growth_interval_width_pp':str(D('12.190')-D('11.959')),'residual_excess_over_gate_pp':str(D('1.3943')-D('.8'))},indent=2))
'@ | python -X utf8 -
```

Input fingerprints; keys map to paths in the main command:

| Input | SHA-256 |
|---|---|
| revenue | `c16c26f5f78c5f1c94a0353bdb5b6a3290c51674b6ec3c27a375acfcaf69db46` |
| xbrl | `ecebf58ed890e83ea104e8c8b365eb7589abcf74230a803dee42b2605180c12b` |
| arrivals | `2487d304a9228e0402f76ca6e34c945a4fe78bf126d0773a5f91c1d328e51097` |
| forecast_input | `eaff3ad4128b37dfc159dca6129b1cdf7b845278ec176153bec4554f8139ecc7` |
| rejected_revenue | `9a6f1de5959dcf9856d32a9a5607b2fe9a5ddb051d93c766109dd4fecc317973` |
| rejected_growth | `173c6fa33c4414edf37f326cef85349f563239e026f5d4b95c67dd6d086f6d93` |

## What failed or could not be done

An initial read of the named comparator note failed at console output because the default Windows encoding could not print a Unicode minus sign. Repeating the same bounded §4 read with `python -X utf8` succeeded. No numeric result uses the failed print attempt.

The core exact-number limitation is substantive: the task forbids R source code and derived output tables, so the fitted 2.0457pp, reported full-model revenue error of 2.27e−13 USD m, 40 model refits, rank 57/57 and 34.62% anchor sensitivity were not independently regenerated. This note independently verifies the 72 raw anchors, their basis split, the displayed residual and composition arithmetic, observed input vintages and archived registry numerical identities. Those checks must not be described as an independent successful fit of the full R model. No statistical power or forecast accuracy is inferred from an exact identity or a conditional bootstrap.

## Interpretation

The economic caution is sound: an exact accounting reconstruction and a locally full-rank constrained fit do not settle the split among geographic mix, within-region prices, FX and take rates. The narrow FY27 composition band omits several forecast and structural uncertainties, while arrivals provide no usable historical-vintage test in these downloads. The specific original sentence should distinguish directly filed quarters from calculated Q4 anchors. This is a provenance correction, not a finding that the 16 back-outs are numerically wrong or that the FY27 conditionality warning should be removed.

## RESUME

Parent should record `partial` on the original exact sentence, not silently count it as survived. If the team revises the wording, describe 72 filing-derived quarterly anchors and preserve the 56 directly filed / 16 backed-out distinction. The displayed 1.39pp attribution gap is arithmetically consistent but the fitted component has not been independently rerun under this read scope. Preserve the zero historical arrivals coverage and rejected-registry history; a valid format slot is not a historical issuance date. Parent owns any broader correction audit, scorer, workboard and git actions. This assignment wrote only this new note and changed no source, data or registry record.
