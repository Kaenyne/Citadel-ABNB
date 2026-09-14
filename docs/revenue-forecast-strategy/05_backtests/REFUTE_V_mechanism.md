# REFUTE V — mechanism lens

Agent: Codex ref_a_power (V mechanism assignment) · 2026-09-12 · branch `codex/lane1-full`.

## Preregistered refutation protocol

Written before independent arithmetic. The assignment has no statistical pass line; the required output is an adversarial verdict. Judge the original exact sentence: **“Using the final FY27 base model, 16.5x adjusted EBITDA implies a $180.88 12-month target, while the existing six-lens base football-field mean is $156.79; these are different valuation objects.”** Independently reconstruct enterprise value, equity value and the per-share bridge from the named raw annual model and valuation summary; count the included football-field lenses; challenge horizon, share-count convention, cash treatment and the possibility that the mean is merely a different EBITDA multiple. Keep arithmetic sensitivities separate from estimated relationships and economic recommendations. W1/W2 forecast performance or power will not be invented for a conditional accounting identity. At least five numbered attacks and one final verdict exactly `survived`, `refuted`, or `partial` will follow. No other package code or derived outputs will be read; parent owns board, scorer and git.

## Verdict

**survived.** The exact sentence is correct as conditional arithmetic under the final model's adopted target-date and share-count conventions. The raw final FY27 base inputs give **$180.876286**, which rounds to **$180.88**. All six field lenses independently reproduce from the annual model and declared conventions; their rebuilt mean is **$156.786845**, which rounds to **$156.79**. The difference comes from the chosen valuation constructions and aggregation. It requires neither a kernel forecast nor an estimated growth-to-multiple coefficient. This verifies what the existing model says; it does not independently validate either price as an investment recommendation.

## Independent price bridge

The raw annual model's Base, 2027 row supplies adjusted EBITDA, net cash and modelled diluted shares. `model/assumptions.md` supplies the adopted 16.5x exit multiple and describes net cash as excluding client float.

| Bridge component | Model scenario n | Value | Units |
|---|---:|---:|---|
| FY27 adjusted EBITDA | 1 | 5,685.7698 | USD m |
| Assumed FY27 exit multiple | 1 | 16.5 | EV / adjusted EBITDA |
| Enterprise value | 1 | 93,815.2017 | USD m |
| FY27 net cash added once | 1 | 10,115.9869 | USD m |
| Equity value | 1 | 103,931.1886 | USD m |
| FY27 modelled diluted shares | 1 | 574.5982 | m shares |
| Computed equity price | 1 | 180.876286 | USD/share |
| Raw valuation-summary price | 1 | 180.8763 | USD/share |

The arithmetic is `(16.5 × 5685.7698 + 10115.9869) / 574.5982`. Using millions in both equity value and shares cancels the scale. The 16.5x term produces enterprise value, not equity value; the cash bridge contributes **$17.605323 per share**. Dividing enterprise value alone by shares would answer a different question. The arithmetic error against the stored price is only **−$0.0000136**, consistent with its four-decimal output precision.

## The six-lens mean and what drives the gap

Membership was fixed by the six `in_football_field=yes` rows in `25_valuation_conventions.csv`, referenced by the allowed `model/assumptions.md`. I did not choose a subset by searching for the claimed average. The price inputs come from the final `13_valuation_summary.csv`; the older conventions file's price/horizon descriptions have a known stale FY28 entry discussed below.

| Included lens | Lens n | Independently rebuilt price | Stored price | Contribution to mean minus FY27 EBITDA price, using stored prices |
|---|---:|---:|---:|---:|
| FY27 EV / adjusted EBITDA | 1 | $180.876286 | $180.8763 | $0.000000 |
| FY27 EV / FCF | 1 | $152.501386 | $152.5014 | −$4.729150 |
| FY27 P / SBC-adjusted FCF | 1 | $117.257237 | $117.2572 | −$10.603183 |
| FY27 P / earnings proxy | 1 | $110.579763 | $110.5798 | −$11.716083 |
| FY28 EV / adjusted EBITDA, discounted one year | 1 | $196.917488 | $196.9175 | +$2.673533 |
| DCF on FCF | 1 | $182.588909 | $182.5889 | +$0.285433 |
| Equal-weight mean of six prices | 6 lenses, one model scenario | **$156.786845** | **$156.7868** | **−$24.089450** |

The maximum absolute independent lens-rebuild error is **$0.0000374**. Averaging the already rounded stored component prices instead gives $156.786850; the $0.00005 difference versus the stored mean is rounding, not a hidden seventh lens.

The FCF lens is `(14.3 × FY27 FCF + FY27 cash) / FY27 shares`; the SBC-adjusted FCF lens is `19.5 × (FY27 FCF − FY27 SBC) / FY27 shares`; the earnings lens is `19.5 × FY27 net income / FY27 shares`. The two P/ lenses use equity multiples and have no separate net-cash addition under the declared convention. FY28 uses its own EBITDA, cash and shares, then divides the resulting price by 1.105. The DCF starts from FY27 FCF, uses ten annual growth rates declining linearly from 9% to 3%, discounts each year at 10.5%, adds a 3% perpetual terminal value, and adds FY27 net cash before dividing by FY27 shares. One specified reconstruction of that DCF reproduces its stored price; no formula search or code inspection was needed.

The two lower P/ lenses contribute **−$22.319267**, or **92.652%** of the net $24.089450 gap. Their economic earnings bases and equity-multiple conventions differ from adjusted EBITDA, which excludes SBC. The FY28 and reported-FCF DCF lenses partly offset those reductions. This is a transparent aggregation explanation for the lower mean, not an unexplained disagreement between two versions of a 16.5x calculation.

Both outputs are dollar-per-share constructions for the same adopted horizon. “Different valuation objects” must not be interpreted as different units, independent evidence, or mutually exclusive observations: the FY27 EBITDA price is itself one of the six values in the mean.

## Numbered refutation attempts

1. **Claim → 16.5x implies $180.88 using final FY27 base inputs. Attack →** Recompute EV, net cash, equity and shares directly from the raw annual row; test whether the reported price omits cash, adds cash twice or uses a different denominator. **Result → survived:** $93,815.2017m EV plus $10,115.9869m cash, divided by 574.5982m shares, equals $180.876286. No regression is involved. The reported $180.88 is correct to cents under these inputs.

2. **Claim → the existing field is a six-lens mean of $156.79. Attack →** Fix membership before calculation using the convention table; independently reconstruct every included lens, including the DCF, and average both rebuilt and stored prices. **Result → survived:** six identified components, each within $0.000038 of its raw summary value, yield $156.786845. Adding the explicitly excluded SBC-adjusted DCF creates a seven-lens mean of $151.927743; dropping FY28 produces a five-lens mean of $148.760720. Neither is the specified existing field.

3. **Claim → these are different valuation constructions rather than an unexplained arithmetic conflict. Attack →** Allocate the entire mean-minus-EBITDA gap by lens, and construct the simplest single-multiple alternative that reproduces the mean. **Result → survived, with a scope caveat:** the gap is exactly the average of the five other lenses' deviations, dominated by the two lower P/ prices. At fixed FY27 base EBITDA/cash/shares, **14.065546x** would reproduce the field mean. That is an implied-equivalent multiple, not the field's chosen 16.5x assumption or a newly estimated fair multiple. Re-expressing a scalar average in EBITDA units does not change its source construction. The two headline prices should not be presented as independent corroboration.

4. **Claim → the prices are consistently labelled 12-month targets. Attack →** Compare adopted September-2027 conventions, actual year-end input dates and the older FY28 row; rebuild the FY28 discount and interpolate FY27 cash/shares to September. **Result → partially:** the label is a declared modelling convention, not exact September-date accounting. Interpolation gives **$179.444873**, versus $180.876286 using year-end inputs. The stale convention CSV still says FY28 is undiscounted; the later assumptions explicitly require a one-year discount, which the final summary correctly applies. Removing that discount using current final inputs gives a mean of **$160.232900**, not $156.786850. This exposes stale supporting metadata and target-date approximation, but does not overturn the original sentence's explicitly final-model arithmetic.

5. **Claim → the $180.88 level is explained or validated by a +0.486 growth-to-multiple mechanism. Attack →** Remove the regression from the central calculation and evaluate the anchored sensitivity at the base growth. **Result → survived for the original sentence; the stronger estimated-level interpretation is refuted:** `16.5 + beta*(g−11.3086)` equals 16.5 at the anchor for any beta, including zero. Neither the $180.88 target nor the $156.79 mean needs beta. A relationship in multiple changes does not supply the 16.5x level. Holding EBITDA fixed while varying growth isolates a multiple sensitivity and omits the operating-profit/cash/share response.

6. **Claim → the older 16.5x price could refute the final $180.88 price. Attack →** Recompute the older exit recommendation from its own raw inputs, then replace EBITDA, cash and shares sequentially with the final model values. **Result → survived:** the old bridge gives **$191.316513**; replacing EBITDA reduces it by **$4.052884**, cash by **$3.954744**, and shares by **$2.432599**, reaching $180.876286. This is an explicitly ordered accounting bridge, not a unique causal attribution. The same 16.5x multiple does not imply the same price when operating and capitalisation inputs change.

7. **Claim → the quoted cents and six lenses represent statistical precision. Attack →** Inspect the diluted-share proxy and shared model assumptions; perturb shares and ask what independent observations support confidence intervals or power. **Result → partially:** the final share denominator inherits a quarterly weighted-average anchor used as a period-end proxy. Just 1% more shares at fixed equity value reduces the price to **$179.085432**. Six overlapping methods using the same scenario are not six independent price observations. Exact cents are arithmetic output precision, not economic confidence. This limitation is consistent with the original conditional wording.

8. **Claim → one multiple turn adds $9.89 and the field gap could be ordinary rounding. Attack →** Differentiate the price identity with respect to the multiple and compare that scale with the $24.0894 headline gap. **Result → partially:** a turn adds exactly **$9.895210**, conventionally **$9.90** to two decimals, rather than the note's $9.89. This is a minor precision correction outside the exact sentence. The headline gap is about **2.434454 multiple turns** at the fixed FY27 inputs and cannot be explained by cent-level rounding. Translating that into a growth forecast via the historical change slope would add an unsupported economic assumption.

## Arithmetic sensitivity, statistical estimation and applicability

| Quantity checked | Calculation/sample n | Status |
|---|---|---|
| Final base EBITDA price | One annual model scenario | Deterministic conditional arithmetic |
| Field mean | Six dependent lenses on one scenario | Deterministic aggregation; no sampling interval |
| Growth sensitivities 9.18%, 10.35%, 11.52% | Three conditional scenarios | Reproduce $170.639240 / $176.266105 / $181.892970; not a predictive interval |
| W1/W2 price performance | Not applicable to the exact accounting sentence | No realized-price forecasting test was claimed or performed |
| Power / detectable effect / p-value | Not applicable | No sampled effect is being estimated |
| Registry inventory | 69 CSV filenames | No `valuation-*` or `valuation_*` registration |

The frozen harness has no annual equity-price target. This task neither registers the prices under a revenue object nor treats unregistered arithmetic as failed forecasting. The package's historical slope estimates and source-vintage diagnostics are outside what is needed to establish the exact accounting sentence; they were not re-estimated or presented as support for the two levels. No current market or consensus data were needed.

## What ran and reproducibility

All commands ran from the repository root using the project `.venv` interpreter through `python`. Raw inputs: `13_model_annual.csv`, `13_valuation_summary.csv`, and the older exit recommendation, all named by the package note; `model/assumptions.md` and its explicitly linked `25_valuation_conventions.csv`. Registry inspection was filenames only. No V code or derived output was read.

The exact main calculation below exited **0**; Python-measured runtime **0.004098 seconds**, tool wall time **0.834048 seconds**. A subsequent decimal arithmetic cross-check exited 0 with tool wall time **0.631922 seconds**. Overall agent wall time and token usage are unavailable and not estimated. No board, scorer or git mutation was made.

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + [IO.Path]::PathSeparator + $env:PATH
@'
import csv,hashlib,json,time
from decimal import Decimal,getcontext
from pathlib import Path
getcontext().prec=40
start=time.perf_counter()
D=Decimal
paths={
 'annual':'data/processed/overnight/13_model_annual.csv',
 'summary':'data/processed/overnight/13_valuation_summary.csv',
 'conventions':'data/processed/overnight/25_valuation_conventions.csv',
 'older_exit':'data/processed/overnight/12_exit_multiple_recommendation.csv',
 'assumptions':'model/assumptions.md'}
def read(key):
 with Path(paths[key]).open(encoding='utf-8-sig',newline='') as f:
  return list(csv.DictReader(f))
a=read('annual'); v=read('summary'); c=read('conventions'); old=read('older_exit')
b={r['year']:r for r in a if r['scenario']=='Base'}
vb={r['lens']:D(r['price']) for r in v if r['scenario']=='Base' and r['price']}
E,C,S=[D(b['2027'][k]) for k in ['adj_ebitda','net_cash','shares_end']]
mult=D('16.5')
price=(mult*E+C)/S
selected=[r['lens'] for r in c if r['in_football_field']=='yes']
assert len(selected)==len(set(selected))==6
components=[{'lens':x,'price':vb[x],'contribution_to_mean_minus_EBITDA':(vb[x]-vb['EV / adj. EBITDA, FY27E'])/D(6)} for x in selected]
field=sum(vb[x] for x in selected)/D(6)
old28=vb['EV / adj. EBITDA, FY28E (undiscounted, value at end-FY2028; sensitivity)']
new28=((D('16.5')*D(b['2028']['adj_ebitda'])+D(b['2028']['net_cash']))/D(b['2028']['shares_end']))/D('1.105')
field_undisc=(sum(vb[x] for x in selected)-vb['EV / adj. EBITDA, FY28E']+old28)/D(6)
field_seven=(sum(vb[x] for x in selected)+vb['DCF on SBC-adjusted FCF'])/D(7)
field_no28=(sum(vb[x] for x in selected)-vb['EV / adj. EBITDA, FY28E'])/D(5)
c_sep=D(b['2026']['net_cash'])+D('.75')*(C-D(b['2026']['net_cash']))
s_sep=D(b['2026']['shares_end'])+D('.75')*(S-D(b['2026']['shares_end']))
direct_lenses={
 'EV / adj. EBITDA, FY27E':price,
 'EV / FCF, FY27E':(D('14.3')*D(b['2027']['fcf'])+C)/S,
 'P / SBC-adjusted FCF, FY27E':D('19.5')*(D(b['2027']['fcf'])-D(b['2027']['sbc']))/S,
 'P / earnings proxy, FY27E':D('19.5')*D(b['2027']['net_income'])/S,
 'EV / adj. EBITDA, FY28E':new28}
# Single reconstruction of the declared 10-year linear fade: first growth 9%, last 3%.
f=D(b['2027']['fcf']); pv=D(0); k=D('.105'); terminal=D('.03')
for t in range(1,11):
 g=D('.09')+(terminal-D('.09'))*D(t-1)/D(9)
 f*=1+g
 pv+=f/(1+k)**t
pv+=f*(1+terminal)/(k-terminal)/(1+k)**10
direct_lenses['DCF on FCF']=(pv+C)/S
ob=next(r for r in old if r['scenario']=='Base')
oE,oC,oS=[D(ob[k]) for k in ['fy27_adj_ebitda_musd','fy27_net_cash_musd','fy27_diluted_shares_m']]
bridge=[(mult*oE+oC)/oS,(mult*E+oC)/oS,(mult*E+C)/oS,price]
slope=D('.4860216575'); anchor=D(b['2027']['revenue_yoy_pct'])
sensitivity=[{'growth_pct':g,'multiple':mult+slope*(g-anchor),'price':((mult+slope*(g-anchor))*E+C)/S} for g in map(D,['9.18','10.35','11.52'])]
files=sorted(p.name for p in Path('data/processed/forecast_methods/registry').glob('*.csv'))
print(json.dumps({'base_inputs':{'EBITDA_musd':E,'net_cash_musd':C,'shares_m':S,'multiple':mult,'enterprise_value_musd':mult*E,'equity_value_musd':mult*E+C},
 'price':price,'summary_price':vb['EV / adj. EBITDA, FY27E'],'field_components':components,
 'field_mean':field,'summary_mean':vb['Football field mean'],'headline_gap':price-field,
 'equivalent_EBITDA_multiple_for_field':(field*S-C)/E,'dollars_per_multiple_turn':E/S,
 'direct_lens_rebuilds':[{'lens':x,'computed':y,'summary':vb[x],'error':y-vb[x]} for x,y in direct_lenses.items()],
 'altered_membership_or_horizon':{'undiscounted_FY28_mean':field_undisc,'seven_lens_mean_including_SBC_DCF':field_seven,'five_lens_mean_without_FY28':field_no28,'sept_cash_share_interpolation_price':(mult*E+c_sep)/s_sep},
 'older_input_bridge_prices':bridge,'sequential_deltas':[bridge[i+1]-bridge[i] for i in range(3)],
 'conditional_growth_sensitivity':sensitivity,'registry_csv_n':len(files),'valuation_registry_files':[f for f in files if f.startswith(('valuation-','valuation_'))],
 'sha256':{k:hashlib.sha256(Path(p).read_bytes()).hexdigest() for k,p in paths.items()},
 'runtime_seconds':round(time.perf_counter()-start,6)},indent=2,default=str))
'@ | python -
```

Exact arithmetic cross-check:

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + [IO.Path]::PathSeparator + $env:PATH
@'
from decimal import Decimal as D
p=D('180.8762864206675203646652565'); e=D('5685.7698'); c=D('10115.9869'); s=D('574.5982')
print('one_turn_dollars',e/s)
print('price_with_one_percent_more_shares',p/D('1.01'))
print('cash_per_share',c/s)
print('two_equity_lenses_share_of_gap_pct',D('22.31926666666666666666666666')/D('24.08945')*100)
print('all_six_independent_rebuild_mean',sum(map(D,['180.8762864206675203646652565','152.5013860642097382135899486','117.2572372311643162126160507','110.5797626933046431401977939','196.9174880188335673248189424','182.5889091775542056528278232']))/6)
'@ | python -
```

Input fingerprints; keys map to exact paths in the main command:

| Input | SHA-256 |
|---|---|
| annual | `e97388cd9c4a3aba283caa13a327dd398c97655497a88612c23c3f10cb6fe318` |
| summary | `3edf09f83e8e59c0184e9ff80d2c466fb71a1a008058f06cc976a32aee029b36` |
| conventions | `bae7d2dd56ef0a98bf82d3bd57014d0f762c35f6f8463c39103f99334a597561` |
| older_exit | `db980fe5795a0ee78b32058281ac160358f1ecb275595c879ec1fb9f9d240f22` |
| assumptions | `2de963d51ad050545c94374b9bb7cea4b421232e83cd449c6d5feb4a969b46dd` |

## What failed or remains unavailable

No arithmetic rebuild failed. Supporting metadata do disagree: the older convention CSV describes an undiscounted FY28 horizon, whereas the later model assumptions explicitly supersede that convention and the final numerical output applies the discount. Its older $160.22 field-mean prose is not reproduced by simply undoing the discount on current final inputs; that sensitivity is $160.2329. This stale supporting text must not override the final input set. The only minor numerical correction within the package discussion is $9.895210 per turn, rounding to $9.90 rather than $9.89.

This task did not validate economic assumptions, confirm a true period-end dilution count, re-estimate valuation regressions or backtest a price forecast. Those are separate estimation questions; exact reproduction of six formulas cannot answer them. No statistical confidence or new direction/target decision is attached to this note.

## Interpretation

Retain the original exact sentence as a reconciliation of existing model outputs. The final FY27 single EBITDA lens and the six-lens arithmetic mean have different constructions even though both are expressed as prices at the adopted horizon. Their discrepancy is explained quantitatively by the mixture of profit/cash-flow bases, multiples and discounting conventions. The mean is not an estimated distribution of six independent forecasts, and the EBITDA multiple's level is a chosen scenario assumption. The verified arithmetic supports comparing the two; it does not choose one for the team.

## RESUME

Parent should record a `survived` vote on the original exact sentence and keep its final-model qualifier. The raw bridge and all six lenses have been independently reproduced without package code or derived outputs. Preserve the cash/share and adopted-horizon conventions, note the stale FY28 metadata in the older conventions file, and round the one-turn sensitivity to $9.90 if quoting cents. A later team decision should specify which valuation construction and economics it adopts; no choice is made here. Parent owns board, scorer and git. This assignment wrote only this new refutation note.
