# REFUTE_V_vintage — model and valuation-vintage audit

Agent `/root/ref_x_vintage` executing V vintage · 12 September 2026 task date · parent owns board, branch, scorer and git · runtime/token totals unavailable unless recorded below.

## Verdict

**survived** on the original exact sentence. Independent calculations from the named annual model and assumptions give **$180.876286** for the 16.5x FY27 base EBITDA lens and **$156.786845** for the six-lens mean. Both round to the quoted cents. The audit did find a stale supporting conventions CSV: it still contains an undiscounted FY28 lens and a $160.22 mean. The later, explicit convention change in `model/assumptions.md` and the independently reproducible current valuation rows resolve that source conflict in favor of the headline. This is an accounting statement about conditional model outputs, not verified historical forecasting performance.

## Pre-registered audit

Original exact sentence: “Using the final FY27 base model, 16.5x adjusted EBITDA implies a $180.88 12-month target, while the existing six-lens base football-field mean is $156.79; these are different valuation objects.”

Written before independent calculations. The assignment has no statistical pass line. I will test the complete sentence with at least five explicit attacks, returning exactly survived / refuted / partial. Recompute the FY27 EBITDA/net-cash/share bridge and the six-lens arithmetic from the note's named model inputs. Audit model versions, share/cash bases, target-date conventions, any consensus dependency, and registry presence. Distinguish an arithmetic identity on conditional forecasts from a historically vintage-verified valuation estimate. Read no other package code or V derived outputs; write only this note.

## Results: seven explicit refutation attempts

1. **Claim: the final FY27 base model gives $180.88 at 16.5x adjusted EBITDA. Attack: recompute from annual dollar inputs without reading V code or V result tables. Result: survived.** The Base/2027 input is adjusted EBITDA **$5,685.7698M**, net cash **$10,115.9869M**, and modeled diluted period-end shares **574.5982M** (n=1 scenario-year). Enterprise value is 16.5×5,685.7698 = **$93,815.2017M**; equity value after adding net cash is **$103,931.1886M**. Dividing by shares gives **$180.8762864207**, or **$180.88**. The source valuation row is $180.8763, a rounding difference of $0.0000136. No current share price, analyst target, regression coefficient or consensus estimate is needed in this identity.

2. **Claim: the $156.79 figure is a six-lens base mean. Attack: reconstruct every constituent independently, then try including an extra displayed lens or dropping the FY28 lens. Result: survived.** All six prices below were rebuilt from `13_model_annual.csv` and the explicit model assumptions, including the ten-year fading-growth DCF. The maximum absolute difference from a corresponding `13_valuation_summary.csv` row is **$0.0000374** (n=6 lens prices). Their sum is **$940.7210696** and equal-weighted mean **$156.7868449**. Including the separately displayed SBC-adjusted DCF would instead give **$151.9277385** (n=7 lenses); dropping FY28 gives **$148.7607163** (n=5). Those are different memberships. The source conventions identify six core lenses and explicitly exclude the SBC-adjusted DCF from the field. Six is a model aggregation count, not six independent forecasts or observations.

| Base lens, at the adopted target convention | n model output | Independently rebuilt price | Input method |
|---|---:|---:|---|
| EV / adjusted EBITDA, FY27 | 1 | $180.876286 | (16.5×FY27 EBITDA + FY27 cash) / FY27 shares |
| EV / FCF, FY27 | 1 | $152.501386 | (14.3×FY27 FCF + FY27 cash) / FY27 shares |
| P / SBC-adjusted FCF, FY27 | 1 | $117.257237 | 19.5×(FY27 FCF−SBC) / FY27 shares; no cash add-on |
| P / earnings proxy, FY27 | 1 | $110.579763 | 19.5×FY27 net income / FY27 shares |
| EV / adjusted EBITDA, FY28, discounted one year | 1 | $196.917488 | FY28 equity/share bridge divided by 1.105 |
| DCF on FCF | 1 | $182.588909 | FY27 FCF seed; growth 9%→3% over 10 years; cost of equity 10.5%; terminal 3%; FY27 cash/shares |
| Equal-weighted field mean | 6 lenses | **$156.786845** | Sum / 6 |

3. **Claim: the numbers use the final model rather than a prior model vintage. Attack: substitute the older exit-recommendation inputs while keeping the 16.5x multiple. Result: survived.** The earlier `12_exit_multiple_recommendation.csv` Base row has EBITDA $5,825.035M, cash $12,358.220M and shares 566.973M. It produces **$191.3165133**, not $180.88 (n=1 old scenario). The current annual source uses the smaller EBITDA/cash and higher share count shown above. `model/assumptions.md` explicitly says the 6–7 September model supersedes the 5 September operating cases, and documents subsequent share-roll and net-cash corrections. The same multiple across versions does not make their price outputs interchangeable. Neither CSV contains a publication-vintage field, so this verifies the documented model hierarchy and current arithmetic; it does not prove when every underlying operating input became public.

4. **Claim: the existing six-lens mean uses the stated valuation-date convention. Attack: follow `25_valuation_conventions.csv` literally. Result: survived on the headline, but the attack exposes a stale supporting source.** That CSV's six `in_football_field=yes` Base prices average **exactly $160.22** (n=6). Its FY28 row says the lens is not discounted and reports $217.51. This directly conflicts with the updated assumptions, which explicitly record the later workstream-26 decision to discount the FY28 lens one year. Applying the updated convention to the final annual data gives an undiscounted FY28 price of **$217.5938243**, discounted to **$196.9174880**. This yields $156.7868449, matching the current summary. Replacing only that discounted lens with its current undiscounted counterpart gives **$160.2329010** (n=6); the slight difference from the stale $160.22 is due to the stale constituent values too. The assumptions' revised section and all six reproducible current outputs support the original sentence. The stale CSV should not be cited as current evidence of discount treatment.

5. **Claim: $180.88 is a 12-month target. Attack: enforce an exact September-2027 cash/share date instead of end-FY2027 arithmetic. Result: survived under the model's explicit convention, not as an exact-date identity.** The assumptions adopt approximately 30 September 2027, but use FY2027-end metrics, cash and shares. Straight-lining cash and shares 75% from FY26 to FY27 gives **$179.4448729**, **$1.4314135 lower** than the model lens (n=1 interpolation sensitivity). This approximation is expressly disclosed in the named assumptions and acknowledged in V's note. The phrase “using the final FY27 base model” ties the original sentence to that adopted convention; the arithmetic is not presented as a date-exact independently derived September capitalization. The target is also not a present discounted fair value. The annual operating forecasts and future cash/share balances are intentional forecast inputs, not realized 2027 observations backdated to 2026.

6. **Claim: the final price bridge consistently uses forecast cash and modeled diluted shares. Attack: create plausible cross-vintage bridges from other available source rows. Result: survived.** With FY27 EBITDA held fixed, using FY26 cash with FY27 shares gives **$179.6014163**; using FY27 cash with FY26 shares gives **$176.4985796**; replacing FY27 modeled shares with the 597M starting weighted-average proxy gives **$174.0890931** (n=1 arithmetic scenario each). None reproduces the headline. The current FY27/FY27 combination does. This rules out those specific splices, not uncertainty in the share forecast itself. The assumptions explicitly identify 597M as a diluted weighted-average anchor used as a period-end proxy, and future issuance as a proxy. The price therefore inherits the final model's approximate share basis; it does not certify a directly observed fully diluted cap table.

7. **Claim: these are different valuation objects, not two conflicting estimates of the same lens. Attack: use a consensus vintage or an empirical slope to explain the gap and demand W1/W2 validation. Result: survived.** The price gap is **$24.0894415** ($180.8762864−$156.7868449); it follows from changing the lens aggregation while retaining the documented model scenario. At fixed FY27 inputs one multiple turn changes the single EBITDA price by **$9.8952099**, but no fitted growth coefficient is required to compute either headline figure. The source annual and valuation files contain no vendor, `as_of`, `street_as_of`, or publication timestamp columns; the conventions' `spot_date` is 2026-09-04 and is used for upside labels, not these price identities. There are no valuation/football/multiple registry filenames. The current analyst panel discussed in V is outside the arithmetic dependencies and was not imported into this audit. W1/W2 and statistical power are **not applicable** to these conditional arithmetic identities: the n=1 base scenario and n=6 dependent model lenses are not historical test events. No scored PIT cell, confidence interval, causal multiple rule or validated target recommendation is inferred.

## Source and vintage boundaries

Only the V assignment/note, the permitted model inputs below, and registry filenames were read for this audit. The previously read authoritative harness README and cheatsheet were not reread. No V code, V derived output table, other package code or market-price refresh was read or executed. The note's supporting filename `football_field_reconciliation.csv` is a V output and was deliberately not used. The six source lens rows served only as comparison values after independently calculating the lenses from the annual model and assumptions.

The documentation has an explicit supersession order: 5 September model → 6–7 September annual model and share/cash fixes → the documented workstream-26 discount convention. Filesystem modification times were not treated as financial publication dates. The underlying CSVs lack source-publication timestamps. That prevents historical information-set certification but does not falsify a statement conditional on the supplied final scenario. The stale `25_valuation_conventions.csv` conflict is documented here without changing that file.

| Input (all read-only) | SHA-256 at audit |
|---|---|
| `data/processed/overnight/13_model_annual.csv` | `e97388cd9c4a3aba283caa13a327dd398c97655497a88612c23c3f10cb6fe318` |
| `data/processed/overnight/13_valuation_summary.csv` | `3edf09f83e8e59c0184e9ff80d2c466fb71a1a008058f06cc976a32aee029b36` |
| `data/processed/overnight/12_exit_multiple_recommendation.csv` | `db980fe5795a0ee78b32058281ac160358f1ecb275595c879ec1fb9f9d240f22` |
| `data/processed/overnight/25_valuation_conventions.csv` | `bae7d2dd56ef0a98bf82d3bd57014d0f762c35f6f8463c39103f99334a597561` |
| `model/assumptions.md` | `2de963d51ad050545c94374b9bb7cea4b421232e83cd449c6d5feb4a969b46dd` |

## What ran and what was not established

Commands ran from the repository root. Source reads used `Get-Content -LiteralPath` for the paths named above. Path discovery used `rg --files "data" "model"` with filename filters, exit 0 (0.75s). Registry discovery used `rg --files "data/processed/forecast_methods/registry" | rg "(valuation|football|ev-ebitda|multiple)"`, exit 1 because there were no matches (0.66s), later confirmed independently through `pathlib`. The primary Decimal arithmetic command below exited **0**, **0.345s shell wall time / 0.0013s computation**. The supplementary stale-CSV mean and registry check exited **0**, **1.938s shell wall time / 0.0053s computation**. There was no failed numerical replication. Session elapsed time and token totals are unavailable and are not estimated.

No regression was estimated and no statistical parameter was fitted. Six existing valuation rules were evaluated with fixed documented assumptions. Model-input realism, historical publication vintages, market targets, monthly regression diagnostics and the investment merit of 16.5x were outside the original accounting sentence and are not certified. No financial recommendation or team valuation decision is made. Only this new note was written; parent retains scorer, workboard and git operations.

Exact primary PowerShell reproduction command:

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + [IO.Path]::PathSeparator + $env:PATH
@'
import csv,time,decimal,hashlib
from pathlib import Path
started=time.perf_counter(); D=decimal.Decimal
def read(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
a=read('data/processed/overnight/13_model_annual.csv')
v=read('data/processed/overnight/13_valuation_summary.csv')
c=read('data/processed/overnight/25_valuation_conventions.csv')
f={int(x['year']):{k:D(z) for k,z in x.items() if k!='scenario'} for x in a if x['scenario']=='Base'}
r=f[2027]; y=f[2028]
raw28=(D('16.5')*y['adj_ebitda']+y['net_cash'])/y['shares_end']
prices={'EV / adj. EBITDA, FY27E':(D('16.5')*r['adj_ebitda']+r['net_cash'])/r['shares_end'],'EV / FCF, FY27E':(D('14.3')*r['fcf']+r['net_cash'])/r['shares_end'],'P / SBC-adjusted FCF, FY27E':D('19.5')*(r['fcf']-r['sbc'])/r['shares_end'],'P / earnings proxy, FY27E':D('19.5')*r['net_income']/r['shares_end'],'EV / adj. EBITDA, FY28E':raw28/D('1.105')}
flow=r['fcf']; pv=D(0)
for i in range(10):
    growth=D('.09')+(D('.03')-D('.09'))*i/9
    flow*=1+growth
    pv+=flow/(D('1.105')**(i+1))
pv+=flow*D('1.03')/D('.075')/(D('1.105')**10)
prices['DCF on FCF']=(pv+r['net_cash'])/r['shares_end']
for key,val in prices.items():
    src=next(x for x in v if x['scenario']=='Base' and x['lens']==key)
    print(key,'computed',val,'source',src['price'],'delta',val-D(src['price']))
mean=sum(prices.values())/6
print('SIX_MEAN',mean,'SUM',sum(prices.values()),'MIN',min(prices.values()),'MAX',max(prices.values()))
source6=[D(x['price']) for x in v if x['scenario']=='Base' and x['lens'] in prices]
print('SIX_SOURCE_MEAN',sum(source6)/6,'n',len(source6))
print('EV',D('16.5')*r['adj_ebitda'],'EQUITY',D('16.5')*r['adj_ebitda']+r['net_cash'],'NET_CASH_PER_SHARE',r['net_cash']/r['shares_end'],'ONE_TURN',r['adj_ebitda']/r['shares_end'])
print('FY28_RAW',raw28,'DISCOUNTED',raw28/D('1.105'),'OLD_MIXED_DATE_FIELD',(sum(prices.values())-prices['EV / adj. EBITDA, FY28E']+raw28)/6)
for name, cash, shares in [('FY26 cash + FY27 shares',f[2026]['net_cash'],r['shares_end']),('FY27 cash + FY26 shares',r['net_cash'],f[2026]['shares_end']),('weighted_average_anchor',r['net_cash'],D(597)),('Sept interpolation',f[2026]['net_cash']+D('.75')*(r['net_cash']-f[2026]['net_cash']),f[2026]['shares_end']+D('.75')*(r['shares_end']-f[2026]['shares_end']))]:
    print('BRIDGE_ATTACK',name,(D('16.5')*r['adj_ebitda']+cash)/shares)
old=next(x for x in read('data/processed/overnight/12_exit_multiple_recommendation.csv') if x['scenario']=='Base')
print('OLD_BASE',(D(old['recommended_x'])*D(old['fy27_adj_ebitda_musd'])+D(old['fy27_net_cash_musd']))/D(old['fy27_diluted_shares_m']))
for label,pp in [('seven operating/DCF lenses',(sum(prices.values())+D('122.7731'))/7),('drop discounted FY28',(sum(prices.values())-prices['EV / adj. EBITDA, FY28E'])/5)]: print('MEMBERSHIP_ATTACK',label,pp)
for name,rows in [('annual',a),('valuation',v),('conventions',c)]:
    print('STAMP_COLUMNS',name,[k for k in rows[0] if any(s in k.lower() for s in ['date','vintage','as_of','vendor','publication','knowable'])])
print('CONVENTION_FY28',[x for x in c if x['lens']=='EV / adj. EBITDA, FY28E'])
for p in ['data/processed/overnight/13_model_annual.csv','data/processed/overnight/13_valuation_summary.csv','data/processed/overnight/12_exit_multiple_recommendation.csv','data/processed/overnight/25_valuation_conventions.csv','model/assumptions.md']:
    print('SHA256',p,hashlib.sha256(Path(p).read_bytes()).hexdigest())
print('seconds',round(time.perf_counter()-started,4))
'@ | python -
```

Exact supplementary command:

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + [IO.Path]::PathSeparator + $env:PATH
@'
import csv,decimal,time
from pathlib import Path
started=time.perf_counter(); D=decimal.Decimal
with open('data/processed/overnight/25_valuation_conventions.csv',encoding='utf-8-sig',newline='') as f:c=list(csv.DictReader(f))
x=[D(r['price_base']) for r in c if r['in_football_field']=='yes']
print('stale convention mean',sum(x)/len(x),'n',len(x))
print('V registry names',[p.name for p in Path('data/processed/forecast_methods/registry').glob('*.csv') if any(k in p.name.lower() for k in ['valuation','football','multiple'])])
print('seconds',round(time.perf_counter()-started,4))
'@ | python -
```

## Interpretation

The attack that worked found a real source-vintage inconsistency in the conventions CSV. It did not overturn the headline because the later explicit convention and six independently rebuilt current lenses agree. The strict target-date interpolation and older cash/share versions demonstrate how easily different price objects arise; those alternatives must retain their own labels. No corrected headline number is required, and no statistical support is attached to the arithmetic.

## RESUME

Parent should record **survived** for the V vintage lens and retain the original accounting sentence with its conditional-model context. Flag `25_valuation_conventions.csv` as stale relative to the explicitly revised assumptions and current annual/valuation inputs; any repair must be a new version under copy-never-overwrite. Keep the modeled diluted-share proxy and approximate September-2027 horizon visible, and do not relabel the arithmetic as a vintage-verified valuation recommendation. Future analytical claims require a separately dated source reconstruction; parent owns board, scorer and git.
