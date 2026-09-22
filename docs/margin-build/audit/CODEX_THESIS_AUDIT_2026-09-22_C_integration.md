**Verdict.** The official income statement reproduces, but its strongest defensible thesis is **revenue slowing against an assumed spending plan**, with limited near-term cost relief. Pitch v2’s FY27 EBITDA gap is $586.1M: $421.4M revenue and $164.7M higher net costs. Re-keying its variable costs changes FY27 EBITDA by only +$4.9M; the material uncertainties are discretionary spending and management’s response. The short case also contains two offsetting construction problems: inconsistent 2027 GBV/ADR chaining and a repeatedly applied RNPL support overlay.

Audit of `401c0a41`, read-only; no builder executed or files changed. I reviewed the prior audit and C-series dossiers. Their settled corrections stand; I disagree specifically with C2’s characterization of the FY27 RNPL overlay, explained below.

**Findings**

Effects are changes to reported adjusted EBITDA; **+ raises EBITDA**. Rows are separate sensitivities, not automatically additive.

| ID | Severity | File:line | Repo claim | Finding, assessment and thesis bias | EBITDA effect: 2H26 / FY27 | Recommended fix |
|---|---|---|---|---|---|---|
| C-01 | Minor | [income_statement.py:109](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/pitch_model_v2/income_statement.py:109); [final_income_statement.md:267](C:/Users/krish/citadel-abnb-marginaudit/docs/pitch-model-v2/lines/final_income_statement.md:267) | Carry base cost dollars because driver differences are small. | **Source:** correctly implements DEC-0022. **Arithmetic:** copying works, but the driver equations no longer hold. GBV differences range from **−1.158% to +0.239%**; bookings barely change. **Economics:** retain budgets, re-key variable costs. Flat dollars modestly favor the short in aggregate. | **+2.20 / +4.91** | Recalculate merchant fees, chargebacks, other COR and recursive OPS using official drivers; preserve spending assumptions separately. |
| C-02 | Major | [final_income_statement.md:246](C:/Users/krish/citadel-abnb-marginaudit/docs/pitch-model-v2/lines/final_income_statement.md:246); [run.py:351](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:351) | FY26 margin falls to 35.05%; flex is a memo alternative. | **Source:** breach is disclosed correctly. **Arithmetic:** **35.0488%**, requiring **$63.70M** less Q4 marketing to reach 35.5%. **Economics:** no management response is a scenario assumption, not evidence of inability to respond. It favors the short. | **+63.70 / undetermined** | Put the floor-defense branch beside the official case. After C-01, the remaining cut is **$61.50M**. |
| C-03 | Major | [run.py:341](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:341) | Short nights and ADR growth scale base revenue and GBV. | **Source:** growth rates are scenario judgments. **Arithmetic:** saved outputs match code, but 2027 levels contradict the stated ADR path. Implied ADR growth is **+2.665%/+6.851%** in 3Q27/4Q27, versus **+0.034%/−0.285%** specified. **Economics:** nights chain from short-case 2026; GBV does not. This understates the short’s revenue downside. | Approximately **0 / −309.90**, preserving take rates and correcting GBV-linked fees | Chain short GBV from its own prior-year GBV and stated nights/ADR growth; then derive revenue consistently. |
| C-04 | Major | [run.py:167](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:167), [189](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:189); [C2 dossier:199](C:/Users/krish/citadel-abnb-marginaudit/docs/pitch-model-v2/dossiers/C2_c2_ops_support.md:199) | RNPL adds a flat 4% support uplift; C2 reports $55.8M FY27. | **Source:** disclosures support a mechanism, not a measured 4%. **Arithmetic:** H2 FY27 applies 1.04 again to prior-year costs already uplifted: **1.0816** versus an otherwise identical no-overlay path. Total FY27 effect is **$84.26M**, not $55.8M; the latter measures only the current-year multiplication. **Economics:** annual compounding needs explicit justification. Favors the short. | **0 / +29.60** for a single persistent level uplift | Store an unoverlaid OPS history, apply the level overlay once, or explicitly document an additional annual deterioration. |
| C-05 | Major | [run.py:132](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:132); [C6 dossier:213](C:/Users/krish/citadel-abnb-marginaudit/docs/pitch-model-v2/dossiers/C6_c6_ebitda.md:213) | The cost build supports costs exceeding consensus. | **Source:** spending directions are sourced; amounts and persistence remain judgments. **Arithmetic:** the FY27 net-cost excess is **$164.65M**. But the reconciliation alone carries **$116.83M hosting + $78.37M marketing** into FY27. **Economics:** this is not independently demonstrated cost-surprise forecasting skill. Treating it as established alpha favors the short. | Removing that reconciliation persistence: **+126.57 / +195.21**; sensitivity, not a recommended base | Present the cost gap as conditional on named spending assumptions, with reconciliation persistence and management flex exposed. |
| C-06 | Minor | [final_income_statement.md:219](C:/Users/krish/citadel-abnb-marginaudit/docs/pitch-model-v2/lines/final_income_statement.md:219); [consensus CSV:4](C:/Users/krish/citadel-abnb-marginaudit/data/processed/margin_build/06_fy27_path_v2/06_consensus_quarterly_2027.csv:4) | FY27 Street margin is 36.45%, while quarterly comparisons use quarterly means. | Both source objects are valid, but different: quarterly sums give **$5,826.40M EBITDA / 36.7685%**; the annual panel gives **$5,766.10M / 36.4497%**. Using quarterly sums enlarges the EBITDA gap by **$60.30M**. | No model change; benchmark effect only | Label annual-panel and quarterly-sum comparisons explicitly. |

**Reproduction log**

All calculations used inline `py -3.13`; costs came from CSVs. Exact official drivers were read from the completed workbook’s cached cells, then EBITDA was independently recomputed. This matters: `adr_path.csv` uses a rounded nights cross-check and produces FY27 EBITDA **$5,243.44M**, versus the official workbook’s **$5,240.32M**.

The following shared setup and commands reproduce the reported checks without writes:

```powershell
@'
import pandas as pd, openpyxl
from pathlib import Path
M=Path('data/processed/margin_build'); L=M/'40_line_build'
read=lambda f: pd.read_csv(f).set_index('quarter')
B=read(L/'40_lines_quarterly.csv').query("scenario=='base'")
S=read(L/'40_short_case_quarterly.csv')
H=read(M/'02_financial_panel/02_panel_quarterly.csv')
T=read(M/'06_fy27_path_v2/06_consensus_quarterly_2027.csv')
SP=read(L/'40_short_case_revenue_path.csv')
P=pd.read_csv(L/'40_params.csv').set_index('name')['base']
Q=list(B.index)
w=openpyxl.load_workbook('model/ABNB_official_model_complete.xlsx',
                         read_only=True,data_only=True)
ws=w['Income_Statement']
V=pd.DataFrame({q:{k:ws.cell(r,c).value for k,r in
    [('n',5),('gbv',8),('adr',10),('rev',12),('saved_e',24)]}
    for q,c in zip(Q,range(17,23))}).T
w.close()
E=V.rev-B.total_cash_costs+B.da+B.lodging_reserves

def ops(n,u=0):
    z={q:(H.loc[q,'ops_cash'],H.loc[q,'nights_m']/d)
       for q,d in [('3Q25',3.7),('4Q25',3.7),
                   ('1Q26',3.65),('2Q26',3.65)]}
    out={}
    for q in Q:
        old=q[0]+'Q'+str(int(q[2:])-1)
        c,b=z[old]; bk=n[q]/(3.6 if q.endswith('27') else 3.65)
        out[q]=c*(.215*(.9 if q.endswith('27') else .86)*bk/b
                  +.785*1.08)*(1+u)
        z[q]=(out[q],bk)
    return pd.Series(out)

# R1: official statement, annual totals, floor cut
print(pd.DataFrame({'revenue':V.rev,'EBITDA':E,
      'margin':100*E/V.rev,'op_income':E-B.da-B.sbc}))
for qs,hr,he in [(Q[:2],6286,1780),(Q[2:],0,0)]:
    r=V.loc[qs,'rev'].sum()+hr; e=E.loc[qs].sum()+he
    print(r,e,100*e/r,.355*r-e)
print('saved EBITDA maximum error',abs(E-V.saved_e).max())
cut=.355*(6286+V.rev.iloc[:2].sum())-(1780+E.iloc[:2].sum())
print('cut fractions',cut/B.loc['4Q26','sm_marketing'],
      cut/B.loc['4Q26','sm_cash'])

# R2: volume comparison and mechanical re-key
print(V[['n','adr','gbv']])
print(B[['nights_m','gbv_busd','bookings_m']])
dc=(B.cor_fees*(V.gbv/B.gbv_busd-1)
    +(B.cor_chargebacks+B.cor_other)*(V.n/B.nights_m-1))
do=ops(V.n)-B.ops_cash
print(pd.DataFrame({'COR_delta':dc,'OPS_delta':do,'EBITDA_delta':-dc-do}))

# R3: consensus decomposition; cost effect = EBITDA gap minus revenue gap
for name,r,e in [('base',B.revenue,B.adj_ebitda),
                 ('pitch',V.rev,E),('short',S.revenue,S.adj_ebitda)]:
    dr=r-T.revenue_mean_musd; de=e-T.ebitda_mean_musd
    print(name,pd.DataFrame({'revenue':dr,'cost':de-dr,'EBITDA':de})
          .loc[Q])
print(T.loc[Q[2:],['revenue_mean_musd','ebitda_mean_musd']].sum())

# R4: RNPL recursion and short-path identity
print('OPS replay error',abs(ops(S.nights_m,.04)-S.ops_cash).max())
print('total overlay',S.ops_cash-ops(S.nights_m))
print('repeated overlay',S.ops_cash-1.04*ops(S.nights_m))
for q in Q[-2:]:
    old=q[0]+'Q26'
    implied=100*((S.loc[q,'gbv_busd']/S.loc[q,'nights_m'])/
                 (S.loc[old,'gbv_busd']/S.loc[old,'nights_m'])-1)
    g=S.loc[old,'gbv_busd']*(1+SP.loc[q,'nights_yoy_pct']/100)*(
        1+SP.loc[q,'adr_reported_yoy_pct']/100)
    dg=(g-S.loc[q,'gbv_busd'])*1000
    dr=dg*S.loc[q,'revenue']/(S.loc[q,'gbv_busd']*1000)
    df=dg*S.loc[q,'merchant_fee_rate_q_pct']/100
    print(q,implied,g,dr,df,dr-df)
'@ | py -3.13 -
```

| Check | Result |
|---|---|
| R1: six quarterly identities, FY26/FY27, negative 1Q27 operating income | **Matched** exact workbook; prompt’s rounded revenues give immaterial rounding differences. |
| R2: COR/OPS re-key | **Mismatch with flat-dollar treatment**, quantified below. |
| R3: all three FY27 gap decompositions | **Matched** the question after rounding. |
| R4: saved OPS formula | **Matched** within $0.000000001M; **failed** single-level-overlay interpretation. |
| R4: short ADR/GBV consistency | **Failed** in 3Q27/4Q27. |
| Additional inline checks: short `k` multiplication, nights recursion, fees, chargebacks, other COR, adjacent-quarter interest calculation | **Matched** within numerical precision. Hosting, PD, S&M and G&A equal base exactly. |

**C1. Variable costs and the reconciliation**

Pairs below are **line build → official pitch**. Nights/bookings are millions; GBV is $M. Cost deltas are corrected minus plugged costs.

| Quarter | Nights | ADR, $ | GBV | Bookings | ΔCOR | ΔOPS |
|---|---:|---:|---:|---:|---:|---:|
| 3Q26 | 146.813→146.808 | 177.287→177.681 | 26,028.0→26,085.0 | 40.2227→40.2213 | +1.001 | −0.003 |
| 4Q26 | 131.798→131.798 | 174.413→173.034 | 22,987.3→22,805.6 | 36.1091→36.1091 | −3.197 | ≈0 |
| 1Q27 | 169.018→169.016 | 192.877→190.646 | 32,599.6→32,222.2 | 46.9494→46.9489 | −5.785 | −0.001 |
| 2Q27 | 157.100→157.099 | 188.720→188.378 | 29,647.9→29,593.9 | 43.6389→43.6385 | −0.962 | −0.001 |
| 3Q27 | 155.958→155.919 | 182.041→182.522 | 28,390.8→28,458.6 | 43.3217→43.3107 | +1.173 | −0.019 |
| 4Q27 | 139.766→139.677 | 177.685→178.112 | 24,834.2→24,878.1 | 38.8238→38.7992 | +0.723 | −0.042 |

Official nights follow [workbook.py:216](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/forecast_methods/reviews_index_v2/workbook.py:216); ADR/GBV wiring follows [adr_engine/workbook.py:219](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/pitch_model_v2/adr_engine/workbook.py:219). Re-keying retains seasonal fee factors, cross-border adjustment, nights-per-booking assumptions and OPS recursion.

The question’s calibration premise needs correction: the **$97.36M plug is solved at $4,730M guide-midpoint revenue**, using line-build volume drivers—not at its $4,804M forecast revenue. It creates a $2,405.03M cost budget and 49.59% calibration margin.

Reusing the resulting spending dollars is economically coherent **conditional on a fixed budget**. It does not preserve the margin sentence under another revenue path or constitute fresh bottom-up evidence. Holding 49.59% at official revenue instead would require approximately **$19.70M less Q3 cost**; that is a different management-response assumption.

**C2. Floor breach and marketing response**

| Period | Revenue | Adjusted EBITDA | Margin |
|---|---:|---:|---:|
| 3Q26 | 4,690.92 | 2,306.52 | 49.1700% |
| 4Q26 | 3,140.80 | 861.56 | 27.4313% |
| FY26 | 14,117.72 | 4,948.09 | **35.0488%** |
| FY27 | 15,424.73 | 5,240.32 | **33.9735%** |

1Q27 EBITDA is **$458.02M**, margin **15.4994%**, and GAAP operating income **−$26.64M**.

The breach is genuine arithmetic **conditional on flat spending**; it is not an independently forecast management decision. The **$63.70M** Q4 cut equals **12.63% of marketing**, or **8.40% of total S&M**. S&M would still grow approximately **9.7% year over year**.

That is plausible as a scenario, substantially less demanding than the short case’s **$176.71M / 35.03% marketing cut**. M6’s peer coefficient reproduces a 95% interval of **−0.4437 to +0.7220**: it cannot establish zero flexibility. C4 already makes this correction.

The claimed 4Q24 floor-defense precedent is weakly sourced: [run.py:84](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:84) asserts it, but the reviewed ledger records higher marketing and product-development spending, while the [marketing research log:71](C:/Users/krish/citadel-abnb-marginaudit/docs/pitch-forecasts/questions/bonus-marketing-cut-signalled/research-log.md:71) explicitly distinguishes that precedent from a cut. Historical phasing supports flexibility; it does not establish the precise claimed causal episode.

**C3. Short-case consistency**

The six `k` factors reproduce: **0.974368, 0.933218, 0.928731, 0.933976, 0.944599, 0.959913**. Applying each to both revenue and GBV preserves base take rate mechanically. Nights correctly use actual prior-year levels initially and short-case 2026 levels for H2 2027. The inconsistent GBV chaining in C-03 raises implied 2027 ADR; correcting it lowers fees by **$40.12M**, but revenue by **$350.02M**.

The cost equations otherwise run as written:

- Fees fall with GBV; chargebacks use **$0.87 per booking**; other COR falls with nights.
- The **$0.15** chargeback increment adds **$11.22M in 2H26 / $24.84M in FY27** before volume offsets. Its magnitude is judgment, not a disclosed RNPL-specific estimate.
- OPS applies 4% to the **whole line**, including fixed costs. The code uses booked nights divided by nights per booking, despite the “completed booking” label. Cancellation intensity therefore has no explicit completed-stay denominator.
- The **10% funds haircut is applied once**, correctly preserving the earlier audit fix; it affects interest income, **not EBITDA**.
- Fixed hosting, PD, marketing and G&A are coherent budget scenarios, but FY27 immobility is unproven. The Q4 marketing-cut branch leaves FY27 unchanged, implicitly making the cut temporary.

Thus fees should fall further under a consistent short GBV path; OPS should be lower under a single persistent 4% overlay. The remaining RNPL magnitudes are adverse assumptions requiring sensitivities.

**C4. What the thesis can defend**

Using **LSEG’s 13 September pull**, summing FY27 quarterly means:

| Case | Revenue gap | Net-cost effect | EBITDA gap |
|---|---:|---:|---:|
| Line-build base | −17.54 | −164.65 | **−182.19** |
| Official pitch v2 | −421.42 | −164.65 | **−586.07** |
| Short case | −932.63 | −132.33 | **−1,064.96** |

“Net cost” here is the residual **revenue minus adjusted EBITDA**, not published Street forecasts for individual expense lines. In 3Q26, base and pitch have only **$1.59M** higher net costs than Street; the short case has **$8.28M**.

The weakest link in **“costs exceed consensus”** is the independently unsupported spending level—particularly reconciliation persistence and marketing growth—plus reliance on residual Street costs. The weakest link in **operating deleverage** is whether the revenue shortfall occurs and spending remains sticky through management’s response horizon.

A buy-side judge can defendably hear: **“Our revenue scenario falls below consensus while planned spending adjusts slowly, creating operating deleverage; management cuts are the principal offset.”** Calling the entire FY27 spending base “already committed,” or presenting the EBITDA gap as independently established cost-surprise alpha, exceeds the evidence.