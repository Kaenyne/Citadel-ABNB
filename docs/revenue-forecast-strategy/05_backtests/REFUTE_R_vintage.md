# REFUTE_R_vintage — independent source-vintage and registration audit

Agent `/root/ref_x_vintage` executing R vintage · 12 September 2026 task date · parent owns board, branch, scorer and git · session/token totals unavailable unless reported below.

## Verdict

**partial** on the complete original sentence; this does **not** count as survived. The input panel independently contains **72 exact filing-derived cells: 56 directly filed quarterly values and 16 Q4 back-outs**. All 72 reproduce from their named XBRL inputs with zero difference. The note's subtraction **2.0457−3.44 = −1.3943pp** rounds to the quoted 1.39pp absolute gap, but its fitted 2.0457pp endpoint and the actual R model's 72 output matches cannot be independently regenerated from the permitted inputs without the prohibited R code/derived tables. That is an explicit replication limit, not evidence the fitted number is wrong. Conditionality and the rejection of historical-vintage claims are supported. No replacement residual estimate is invented.

## Pre-registered audit

Original exact sentence: “The full-sample regional refresh matches all 72 filed revenue cells but leaves a 1.39pp gap in 2024 ex-FX ADR attribution, so its FY27 composition remains conditional.”

Written before independent computations. The assignment has no statistical pass threshold. Audit the whole original sentence with at least five explicit refutation attempts and return survived / refuted / partial. Independently count and inspect the filed input cells and dates; check disclosed arithmetic and whether the exact residual can be identified from allowed inputs; distinguish conditional draws, priors and historical observations; inspect the actual preserved rejected registry rows and current registry presence without reading R code or derived analytical tables. Current download/reference periods and format-valid dates will not be treated as issuance evidence. Output only this note.

## Results: seven explicit refutation attempts

1. **Claim → all 72 revenue cells are filed. Attack → audit unique source rows and whether each is a directly reported quarterly amount. Result: partial.** `L0_exact_regional_revenue.csv` contains 72 unique quarter/region cells across 18 quarters and four regions. Its own `basis` field is **56 `filed` / 16 `back_out`**, not 72 directly filed quarterly figures. Each `filed` value reproduces the referenced row of `10_xbrl_revenue_geography.csv`; each Q4 value reproduces the referenced annual amount minus the same region's Q1–Q3. Maximum discrepancy is **$0.0M** (n=72). Source accession and filing-date fields agree in all 72 cases. For example, APAC 2022 is $622M annually; Q1–Q3 are $136M+$137M+$156M, leaving Q4 $193M. Thus “72 exact filing-derived cells” is precise. This source-count qualification alone does not invalidate the panel, but the original sentence should not be read as 72 directly disclosed quarterly observations.

2. **Claim → the full-sample R refresh matches all 72. Attack → reconstruct the match without reading its output residuals and ask whether exact matching identifies composition. Result: partial.** The preceding check verifies the **input targets**, not the R model's predictions or its claimed maximum error of 2.27e−13. The note does not fully specify the 57-parameter objective, interval transforms and inherited smoothing/ridge needed to independently reproduce its fitted vector. Reading `disclosure_residuals.csv` or `regional_panel_v3.csv` is explicitly prohibited. The exact-by-inversion mechanism is nevertheless non-validating: for positive regional nights N and take rate t, setting ADR = revenue/(N×t) makes revenue match by definition. More generally, holding total nights fixed, an offsetting reallocation of two regional GBV amounts that preserves total GBV can be offset by inverse take-rate changes, preserving both revenue cells while changing ADR. Persistent regional tilts and annual anchors restrict such alternatives by model assumptions; an identity alone does not. I do not substitute that generic algebraic possibility for proof that the actual R implementation matched its outputs.

3. **Claim → the 2024 gap is 1.39pp. Attack → recompute it independently rather than quote the derived residual table. Result: partial.** The only allowed presentation of the R-fitted 2024 within-region ex-FX endpoint is **2.0457pp in the note**. Subtracting its stated comparator, 3.44pp, gives **−1.3943pp**, correctly rounded in the headline. Likewise the note's 2023/2025 pairs give −0.2815/−0.0101pp (n=1 annual subtraction each; four regions/four quarters under each fitted endpoint). These are independently checked **subtractions of reported endpoints**, not independent estimates of the endpoints. `01_regional_annual.csv` gives annual reported-dollar ADR and fiscal-year source labels; it does not identify R's quarterly fitted shares, its regional FX allocation or a dated 2024 ex-FX endpoint. The requested gap therefore remains reported-but-not-independently-replicated under this audit boundary. Its sign is negative in the note; 1.39pp is the absolute magnitude, not positive acceleration.

4. **Claim → no historical arrivals coefficient is admitted. Attack → use old reference months, older-looking URLs, or current API update dates to manufacture historical eligibility. Result: survived.** The six normalized input series contain **397 rows**, all with `knowable_from=2026-09-13` and `vintage_basis=current_revised_download; not historical release`. Counts are NTTO 66, JNTO 67 and four Eurostat series of 66 each. They form **132 complete three-month quarters and one incomplete JNTO 2026Q3**, so the extra July value cannot stand in for a complete quarter. Every W1/W2 guide predates the stored cutoff, leaving **0/14 and 0/10 admissible arrivals origins**. An intentionally invalid alternative that replaces the release date with the lagged observation-quarter end makes **84/84 W1 and 60/60 W2 series/origin covariate-readiness cells** appear ready (six series × 14/10 origins); the documented vintage gives zero. This is a concrete look-ahead construction, not a usable forecast test. The NTTO URL's `2024-06` directory does not date every value in its current-through-2026 workbook. Even substituting the manifest's Eurostat update date, 2026-09-11, does not admit a scored guide.

The [official NTTO methodology](https://www.trade.gov/i-94-arrivals-program) describes country-of-residence coverage, preliminary/revised/final release stages and revisions extending up to 36 months. [JNTO's releases page](https://www.jnto.go.jp/statistics/data/visitors-statistics/) and [Eurostat's API documentation](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started/api) were opened as the named public source references. Neither a present access route nor a reference-month label certifies a historical version. The local manifest records successful public fetches at **2026-09-13T00:29:50.630434+00:00**; those HTTP results are historical manifest evidence, not fresh re-downloads certified by this audit. There is no consensus vendor field in these inputs: source providers are tourism agencies, not historical Street panels.

5. **Claim → rejected LIVE registrations were withdrawn and cannot count as historical issuance. Attack → inspect the actual preserved registry rows and see whether their field values or format labels repair the timing. Result: survived for withdrawal and rejection; correction internals remain unverified.** Both preserved CSVs exist, each with six rows, for **12 rejected rows**. Every row says `vintage_date=2026-09-11`, `knowable_from=2026-09-06`, `window=LIVE`, `prior_basis=full_sample`, `n_params=61`, `n_train=18`. Yet every row's note explicitly says it was rebuilt **2026-09-12** and calls the earlier date a format slot. The numerical conditions `knowable_from≤vintage_date` and an accepted frozen-harness date cannot prove the forecast existed then; the rows contradict that interpretation themselves. Exactly **zero `l1-reconciliation-v3__*.csv` files remain in the shared registry** at audit. The preserved originals are withdrawal evidence, not promoted forecasts. The note's later actual reconstruction timestamp is explicitly distinguished from its financial input cutoff. I did not read the prohibited local candidate/result tables, correction receipt or R code, so I do not independently certify the claimed 19 unchanged analytical files, 12 replacement-point comparisons, tests, or absence of every possible future write path.

6. **Claim → the reported bootstrap and model diagnostics do not establish unconditional FY27 precision. Attack → treat 40 refits, a full-rank Jacobian, or a zero-width identity band as predictive evidence. Result: survived as an interpretation boundary.** The reported Latin America p10/median/p90 imply **(211.60−131.82)/(2×155.25)=25.6940%** relative halfwidth, consistent with the reported 25.69% (n=40 refits **reported**, not rerun here). Identity residuals that are zero by construction produce zero residual-bootstrap spread without identifying regional ADR. A local rank of 57/57, even if reproduced, would characterize the chosen parameterization and constraints, not remove prior/model uncertainty. The note separately reports **34.62% anchor-strength sensitivity**, whose fit was not independently reproduced here. Its fixed-kernel FY27 growth sensitivity spans **2.235pp** (12.151−9.916) versus **0.231pp** for the reported 2/3-weight conditional p10–p90 spread (12.190−11.959). Those are different experiments; neither is an unconditional predictive interval. A new set of 40 fit results or a verified Jacobian cannot be created from the published endpoints alone.

7. **Claim → FY27 composition remains conditional. Attack → reconstruct the internal identities and see whether they imply measured price, unconditional growth or a consensus edge. Result: survived.** The stated −1.0650% mix and fixed +3% within-region ADR give **(1−0.010650)×1.03−1 = 1.903050%** blended ADR, including the −0.03195pp cross term (n=1 fixed scenario). The +2.33pp residual is simply 3.00−0.63−0.04 with seats and FX held at zero; it is not an independently measured price channel. The four FY2027 revenue rows in the preserved rejected registry sum to **$15,974.5580M**, matching the note's rounded $15,974.6M scenario; summing all six quarterly rows would incorrectly give $23,932.4103M. These preserved values confirm what the rejected object contained, not a new verified annual forecast. No vendor-stamped consensus is used, no prediction interval is present in the archived headers, and no comparison to Street can be manufactured from these rows. Conditionality survives, but it does not certify the exact fitted 2024 residual needed for full survival of the original sentence.

## Source dates and window counts

The revenue rows below are historical **target/accounting cells**, not prediction successes. W2 is a subset of W1. Each guide has four target-region input cells; none of those target cells' stored `knowable_from` dates precedes its guide. For arrivals, the available reconstruction uses current revised values with a common 2026-09-13 conservative cutoff; this does not claim the underlying statistics never had earlier releases, only that those earlier versions are absent from the admitted input evidence.

| Window | n guide origins | First / last guide | Full-sample target cells | Direct / Q4 back-out cells | Origins with admissible current arrivals |
|---|---:|---|---:|---:|---:|
| W1 | 14 | 2023-02-14 / 2026-05-07 | 56 | 44 / 12 | 0 |
| W2 | 10 | 2024-02-13 / 2026-05-07 | 40 | 32 / 8 | 0 |
| Entire input panel | 18 quarter groups | 2022Q1–2026Q2 | 72 | 56 / 16 | Not a forecast window |

`L0_exact_regional_revenue.csv` carries source filing vintages from 2023-05-09 through 2026-08-06. These are the input's actual chosen source vintages, not independently proven earliest possible public disclosures. For example, its 2022 Q4 back-outs use annual comparison figures in a 2024-02-16 10-K. Substituting the economic period end for that source stamp would create an inadmissible earlier version of this particular input. The annual ADR file has `source_10k` labels but no publication/as-of field.

| Preserved rejected object | n rows | SHA-256 |
|---|---:|---|
| `l1-reconciliation-v3__fy27_growth.csv` | 6 | `173c6fa33c4414edf37f326cef85349f563239e026f5d4b95c67dd6d086f6d93` |
| `l1-reconciliation-v3__fy27_revenue.csv` | 6 | `9a6f1de5959dcf9856d32a9a5607b2fe9a5ddb051d93c766109dd4fecc317973` |

These were read from `data/processed/forecast_methods/l1_reconciliation_v3/UNREGISTERED_rejected_registry_20260913/` as the preserved **actual rejected registry files**, not as derived analytical outputs. Current registry absence was checked separately. The corrected candidates were not read, and preservation hashes were calculated here rather than taken from a correction receipt.

## What ran and exact replication limits

All commands ran from the repository root using `python` after prepending `.venv/Scripts` to PATH. Reads used `Get-Content -LiteralPath` for the assignment, R note, the specified L0/annual inputs, source-provenance manifest, normalized monthly arrivals inputs, frozen calendar and two preserved registry files. File-name discovery used `rg --files` and path filters; no model table was opened during discovery. The upstream XBRL input was accessed through the exact `source_path` named in L0. No R code, `disclosure_residuals.csv`, `annual_adr_residuals.csv`, `regional_panel_v3.csv`, bootstrap output, sensitivity table, local candidate table or correction receipt was read.

The principal source/count/timestamp arithmetic command below exited **0**, **0.500s shell wall time / 0.0168s computation**. The deliberately invalid reference-date counterexample exited **0**, **0.851s / 0.0080s computation**. An earlier input schema/basis inspection exited 0 (0.789s), and a source-row indexing check exited 0 (0.647s). No estimator, test suite or harness scorer was run. There were no failed numerical calculations to conceal. Actual session elapsed time and token usage are unavailable and are not estimated.

The unresolved replication is substantive: an input-cell checksum is not an output-fit checksum, and subtracting a reported fitted endpoint is not refitting that endpoint. The note lists parameter counts, hyperparameter choices and model components, but not a complete independently executable specification of the 57-parameter objective and its FX attribution. The audit's explicit read boundary prevents resolving that missing evidence. This is why the whole original sentence receives **partial**, rather than silently substituting the weaker conclusion that its caveats sound appropriate.

Exact principal PowerShell command:

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + [IO.Path]::PathSeparator + $env:PATH
@'
import csv,collections,decimal,time,hashlib
from pathlib import Path
D=decimal.Decimal; started=time.perf_counter()
def read(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def canon(q):return '20'+q[2:]+'Q'+q[0]
e=read('data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv')
s=read('data/processed/overnight/10_xbrl_revenue_geography.csv')
assert len(e)==72 and len({(r['quarter'],r['region']) for r in e})==72
errors=[];stamp_errors=[]
for row in e:
    src=s[int(row['source_row'])]; val=D(src['value_usd'])/1000000
    if row['basis']=='back_out':
        yr=row['quarter'][2:]
        val-=sum(D(x['revenue_musd']) for x in e if x['region']==row['region'] and x['quarter'][2:]==yr and x['quarter'][0] in '123')
    errors.append(abs(val-D(row['revenue_musd'])))
    stamp_errors.append(row['vintage']!=src['filed'] or row['accn']!=src['accn'] or row['knowable_from']<src['filed'])
print('REVENUE_INPUTS',len(e),'quarters',len({r['quarter'] for r in e}),'basis',dict(collections.Counter(r['basis'] for r in e)),'source_max_error',max(errors),'bad_source_stamps',sum(stamp_errors))
cal=read('data/processed/forecast_methods/harness/calendar.csv')
g=sorted((r['next_quarter_guided'],r['guide_date']) for r in cal if '2023Q1'<=r['next_quarter_guided']<='2026Q2')
assert len(g)==14
arr=read('data/processed/forecast_methods/l1_reconciliation_v3/arrivals_monthly_current.csv')
print('ARRIVAL_COUNT',len(arr),'series',dict(collections.Counter(x['series'] for x in arr)))
print('ARRIVAL_STAMPS',sorted(set(x['knowable_from'] for x in arr)))
for q,d in g:
    ec=[x for x in e if canon(x['quarter'])==q]
    print('GUIDE',q,d,'n_cells',len(ec),'filed',sum(x['basis']=='filed' for x in ec),'back_out',sum(x['basis']=='back_out' for x in ec),'target_cells_known',sum(x['knowable_from']<d for x in ec),'arrivals_known',sum(x['knowable_from']<d for x in arr))
for w,rows in [('W1',g),('W2',[(q,d) for q,d in g if q>='2024Q1'])]:
    print('WINDOW',w,'n',len(rows),'full_sample_cells',sum(canon(x['quarter']) in [q for q,d in rows] for x in e),'eligible_arrivals_origins',sum(any(x['knowable_from']<d for x in arr) for q,d in rows))
by=collections.defaultdict(list)
for x in arr:
    yr,mm=x['month'].split('-');q=yr+'Q'+str((int(mm)-1)//3+1);by[x['series'],q].append(x)
print('QUARTER_GROUPS',len(by),'complete',sum(len(x)==3 for x in by.values()),'incomplete',[(k,len(v)) for k,v in by.items() if len(v)!=3])
regdir=Path('data/processed/forecast_methods/l1_reconciliation_v3/UNREGISTERED_rejected_registry_20260913')
rejected=[]
for p in sorted(regdir.glob('l1-reconciliation-v3__*.csv')):
    rows=read(p);rejected.extend(rows)
    print('PRESERVED',p.name,'rows',len(rows),'sha256',hashlib.sha256(p.read_bytes()).hexdigest())
print('REJECTED_STAMPS',{k:sorted(set(r[k] for r in rejected)) for k in ['vintage_date','knowable_from','window','prior_basis','n_params','n_train']})
print('LIVE_R_CURRENT',list(Path('data/processed/forecast_methods/registry').glob('l1-reconciliation-v3__*.csv')))
rr=[r for r in rejected if r['object']=='fy27_revenue']
print('PRESERVED_FY27_SUM',sum(D(r['point']) for r in rr if r['quarter'].startswith('2027')),'FY27_rows',sum(r['quarter'].startswith('2027') for r in rr),'all_six_sum',sum(D(r['point']) for r in rr))
for year,model,comparator in [(2023,'2.8185','3.10'),(2024,'2.0457','3.44'),(2025,'3.3999','3.41')]:
    print('NOTE_ARITHMETIC_ONLY',year,D(model)-D(comparator))
print('NOTE_HALF_WIDTH',100*(D('211.60')-D('131.82'))/(2*D('155.25')))
print('NOTE_FY27_IDENTITY',100*((1+D('-1.0650')/100)*(1+D('3')/100)-1))
print('NOTE_WEIGHT_GROWTH_SPAN',D('12.151')-D('9.916'),'conditional_growth_span',D('12.190')-D('11.959'))
print('seconds',round(time.perf_counter()-started,4))
'@ | python -
```

Exact counterexample command; its fake readiness counts must never be used as PIT evidence:

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + [IO.Path]::PathSeparator + $env:PATH
@'
import csv,collections,time
from datetime import date
started=time.perf_counter()
def read(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
a=read('data/processed/forecast_methods/l1_reconciliation_v3/arrivals_monthly_current.csv')
months=collections.defaultdict(set)
for r in a:
    yy,mm=map(int,r['month'].split('-')); months[(r['series'],yy,(mm-1)//3+1)].add(mm)
cal=read('data/processed/forecast_methods/harness/calendar.csv')
g=sorted((r['next_quarter_guided'],r['guide_date']) for r in cal if '2023Q1'<=r['next_quarter_guided']<='2026Q2')
for w,rows in [('W1',g),('W2',[(q,d) for q,d in g if q>='2024Q1'])]:
    fake=0; real=0
    for q,d in rows:
        yy,qq=int(q[:4]),int(q[-1]); yy,qq=(yy-1,4) if qq==1 else (yy,qq-1)
        end=date(yy,qq*3,[31,30,30,31][qq-1]).isoformat()
        for series in set(x['series'] for x in a):
            complete=len(months[(series,yy,qq)])==3 and len(months[(series,yy-1,qq)])==3
            fake+=complete and end<d
            real+=complete and '2026-09-13'<d
    print(w,'origins',len(rows),'series',6,'false_reference_date_ready_cells',fake,'documented_vintage_ready_cells',real)
print('seconds',round(time.perf_counter()-started,4))
'@ | python -
```

## Interpretation

The vintage attacks verify two meaningful limitations: current revised arrivals cannot support this historical replay, and accepted schema dates did not make the rejected forecasts historically issued. The complete numeric headline has a separate evidence gap. Correcting the provenance wording to 56 directly filed plus 16 filing-derived Q4 cells is warranted; independently reproducing the actual R match and the 2024 ex-FX endpoint requires additional permitted evidence. The 1.39pp value is not replaced with a guessed alternative, and the headline is not credited as fully survived merely because its conclusion is cautious.

## RESUME

Parent should count this lens as **partial, not survived**, preserving the distinction between verified source counts and unverified fitted output endpoints. The next independent check needs a complete standalone mathematical specification/input inventory for the 57-parameter fit, or an explicitly expanded read boundary permitting the relevant output evidence; do not quietly read prohibited tables to convert this result into a pass. Keep the 72 cells labeled filing-derived (56 direct/16 back-outs), retain actual source/reconstruction dates, and leave the rejected 12 registry rows archived with no shared-registry promotion. No existing file, scorer, workboard or git state was changed by this agent; only this note was written.
