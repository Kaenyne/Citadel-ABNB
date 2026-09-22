**1. Verdict**

The FY27 arithmetic passes, but **“costs above consensus” is a spending scenario, not an independently established forecasting edge**. Against the quarterly Street sums, the model has **$164.7M excess costs**, entirely dependent on **$195.2M of reconciliation carried forward**; without that reconciliation, costs are **$30.6M below Street**. Use the **annual LSEG adjusted-EBITDA dollar mean, $5,766.1M**, as the headline annual bar, with its implied **36.45% margin** and the conflicting margin field disclosed. I agree with the earlier audit’s fixes and C1–C8’s distinction between reproduction and predictive evidence; I disagree with the unsupported correlation explanation in WS03/V1 and C1’s treatment of hosting commitments as expense bounds.

All calculations were read-only at `401c0a41`; no files were changed and the builder was not run.

**2. Findings**

Dollar effects below are changes to modeled EBITDA from the stated alternative; **+ raises EBITDA**. Alternatives overlap and must not be added together.

| ID | Severity | File:line | Repo claim | Finding, with numbers | EBITDA effect: 2H26 / FY27 | Recommended fix |
|---|---|---|---|---|---|---|
| B-01 | major | [run.py:142](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:142) | Q3 marketing is campaign timing; hosting is recurring; both enter FY27. | The **$97.3598M** reconciliation becomes **$116.8317M hosting + $78.3746M marketing** in FY27. Treating temporary campaign timing as a permanent, growing base requires separate evidence. This favors the short. | Remove reconciliation: **+126.57 / +195.21** | Separate the Q3 budget calibration from FY27 persistence assumptions; show both cases prominently. |
| B-02 | major | [run.py:51](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:51), [run.py:161](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:161) | $330M hosting already includes an unsized AI ramp; reconciliation is additional. | Final hosting is **$446.83M**, with no evidence separating the AI already in $330M from the extra **$116.83M**. This is an overlap risk, not proven double counting. Commitments are neither annual recognized expenses nor a defensible expense ceiling. | Remove only FY27 hosting reconciliation: **0 / +116.83**. B08 $85/q alternative from Q4: **+15.21 / +106.83** | Build one hosting expense schedule separating existing compute, contractual payments/amortization, and incremental AI. Resolve DEC-0023 explicitly. |
| B-03 | minor | [run.py:65](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:65), [run.py:117](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:117) | Total-S&M seasonality estimates the historical marketing split. | Model 1H26 marketing/field cash **$1,073.754/$430.246M**; disclosed split implies **$1,091/$413M**. Marketing is understated and field overstated by **$17.246M**. Correcting both historical halves and recalculating reconciliation has little net EBITDA impact. | **−1.51 / −0.73** | Use reported component dollars; distinguish MD&A activity deltas from the component-table changes. |
| B-04 | major | [03_consensus_pit.md:216](C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/03_consensus_pit.md:216), [V1:147](C:/Users/krish/citadel-abnb-marginaudit/docs/pitch-model-v2/dossiers/V1_v1_street.md:147) | The margin-field gap follows from separately averaging ratios/high-revenue analysts having high EBITDA. | FY27 discrepancy is **1.3911pp**, equivalent to **$220.06M**. Saved aggregates do not establish its cause. Under a common matched panel, the published high/low ranges bound the weighting effect at approximately **0.107pp**, far smaller. | Forecast: **0 / 0**. Using the field changes the synthetic annual benchmark by **−$220.06M**. | Obtain contributor sets, definitions and timestamps for the margin field. Until reconciled, label the headline “margin implied by annual adjusted-EBITDA/revenue means.” |
| B-05 | major | [40_line_build.md:23](C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/40_line_build.md:23), [C4:170](C:/Users/krish/citadel-abnb-marginaudit/docs/pitch-model-v2/dossiers/C4_c4_sales_marketing.md:170) | Street requires the marketing ramp to stop; the cost disagreement can be attributed to S&M. | Annual Street implies **9.98% total-cost growth**. Even holding our other four lines fixed, its residual S&M is **$3,328.46M**, **+9.47%** on our FY26 S&M—not a spending stop. That residual is not a published Street S&M forecast. | **0 / 0**; attribution changes, not EBITDA. | Say “Street implies slower aggregate cost growth.” Present conditional S&M attribution explicitly, as C4 already recommends. |

**3. Reproduction log**

Calculations used inline PowerShell here-strings piped to **`py -3.13 -`**. Common CSV setup for the expressions below:

```python
import pandas as pd
from pathlib import Path
r = Path("data/processed")
b = r / "margin_build"
L = pd.read_csv(b/"40_line_build/40_lines_quarterly.csv")
A = pd.read_csv(b/"40_line_build/40_annual.csv")
H = pd.read_csv(b/"02_financial_panel/02_panel_quarterly.csv")
S = pd.read_csv(b/"03_consensus_pit/03_current_consensus.csv")
S = S[S.vendor.eq("LSEG")].set_index("period")
Q = pd.read_csv(b/"06_fy27_path_v2/06_consensus_quarterly_2027.csv")
B = L[L.scenario.eq("base")].set_index("quarter")
E = L[L.scenario.eq("evidence_only")].set_index("quarter")
F = B.loc[B.index.str.endswith("27")].sum(numeric_only=True)
V = E.loc[E.index.str.endswith("27")].sum(numeric_only=True)
C = ["cor_cash","ops_cash","pd_cash","sm_cash","ga_cash_ex_lodging"]
T = Q[Q.quarter.str.match("[1-4]Q27")]
sr, se = T.revenue_mean_musd.sum(), T.ebitda_mean_musd.sum()
```

| Recomputed object | Python calculation/command body | Result / match |
|---|---|---|
| Cost formulas and annual roll-up | Independent inline reconstruction of formulas at `run.py:117–178`, using CSV parameters, panel and forecast drivers; compare nine component columns across base/evidence-only. Annual check: `B.loc[B.index.str.endswith("27")].sum(numeric_only=True)` against FY27 annual row. | **108 component cells match**, max error **2.3e−13**; annual monetary rows match within **1.9e−12**. |
| EBITDA identity | `abs(B.revenue-B.total_cash_costs+B.da+B.lodging_reserves-B.adj_ebitda).max()` | **4.6e−13**, match. FY27 **$5,644.2042M**; evidence-only **$5,839.4106M**. |
| Street bridge | `F.revenue-sr`; `F.total_cash_costs-(sr-se+F.da)`; `F.adj_ebitda-se`; repeat with `S.loc["FY27"]` dollar means. | Quarterly: **−17.5394 / +164.6516 / −182.1910**. Annual: **+9.2674 / +131.1623 / −121.8949**. Matches proposed rounded quarterly bridge. |
| Reconciliation | `(F-V)[["cor_hosting","sm_marketing","total_cash_costs"]]`; `V.total_cash_costs-(sr-se+F.da)` | **116.8317 / 78.3746 / 195.2063**; evidence-only cost gap **−30.5548**. |
| S&M source split | `1595*.51*1.32`; `1504-1595*.51*1.32`; `535-122`; `(1091/824-1)*100`; `(413/334-1)*100` | **1,073.754 / 430.246 / 413 / 32.4029% / 23.6527%**. Historical model split does **not** match filing. Replacing marketing halves with **1091** and **771×1.25**, then recalculating reconciliation, gives B-03 effects. |
| Margins and history | `100*S.ebitda_mean/S.revenue_mean`; `H.assign(c=H[C].sum(axis=1)).groupby("year").c.sum()` | Margins **35.6158/36.4497/37.6543%** for FY26–28. Historical costs **6,305/7,119/8,031**, growth **12.9104/12.8108%**. |
| Assumption magnitudes | `F.sm_marketing/1.15*.15`; `F.cor_hosting-224`; `1477.12*.08+30`; `781*1.18*.11`; `F.cor_hosting-340` | **317.8265 / 222.8317 / 148.1696 / 101.3738 / 106.8317**. Counterfactual sensitivities, not source observations. |

**4. Answers**

**B1. Line-by-line assessment**

The filing check uses the cached [2Q26 10-Q:8](C:/Users/krish/citadel-abnb-marginaudit/docs/pitch-forecasts/questions/bonus-insider-selling/sources/tenq/abnb-20260630.htm:8); annual component provenance is in [07_cost_components_annual.csv:4](C:/Users/krish/citadel-abnb-marginaudit/data/processed/overnight/07_cost_components_annual.csv:4).

| FY27 line | Sourcing and arithmetic | Economics and thesis bias |
|---|---|---|
| **Marketing: $2,436.67M** | FY25 **$1,595M** is correctly sourced. Actual 1H25 marketing is **$824M**, or **51.6614%**, not the assumed 51%; 1H26 is **$1,091M**. Table growth is **$267M**, versus MD&A’s **$258M** activity driver. The code implies **$260.304M** growth on its proxy base. FY27 formula otherwise matches exactly. | The 2H26 **25%** and FY27 **15%** rates are opinions supported directionally by expansion/launch language. FY27 growth decelerates, but still adds **$317.83M** versus flat marketing; carrying the campaign step adds another identifiable **$78.37M** versus evidence-only. Both support the short relative to those counterfactuals. |
| **Field/policy cash: $1,022.95M** | **993−212=781** follows the model’s allocation of S&M SBC to field operations. **781×1.18×1.11** is correct. Actual 1H26 field cash is **535−122=413**, versus **430−96=334** in 1H25: **+23.65%**, not the source note’s +21%. FY25 cash-field growth was **49.33%**; “43%” describes GAAP field growth. | **18%/11%** are deceleration judgments, reasonable scenarios but not guidance. They moderate the short versus extrapolating recent growth; FY27 nevertheless adds **$101.37M** versus flat field cash. The approximately $200M launch budget spans field and PD; it is not wholly evidenced as field expense. |
| **Hosting: $446.83M** | Arithmetic is correct: **330+116.8317**. Neither **$224M** nor **$330M** is a disclosed annual hosting expense. Additionally, the source note confuses **Q2 server growth of $12M** with **1H growth of $15M**; reserved-instance amortization explains that increase, rather than establishing another additive increment. | Layered AI assumptions favor the short. B08’s **$85/q** is also an estimate, not ground truth. C1 correctly flags the disagreement; its proposed commitment “ceiling” is not economically established. |
| **PD: $1,625.29M** | **1,477.12×1.08+30** matches. Historical headcount/payroll language is sourced; **5% headcount +3% compensation** and **$30M tooling** are judgments. C3 already identifies the GAAP/cash growth-basis caveat. | Hiring normalization is plausible. The separate AI increment needs evidence that it is outside ordinary PD growth and hosting spend. Combined FY27 uplift **$148.17M** favors the short versus flat PD. |
| **G&A ex reserves: $1,044.54M** | **(453+516×1.05)×1.05** matches. The forecast’s ex-reserve FY26 base is **$994.8M**; annual CSV G&A includes **$1M** historical reserves. FY27 **5%** is an opinion. C5 already settles the mis-cited “extremely disciplined” quotation. | Plausible modest growth; substantial revenue leverage makes it relatively favorable to EBITDA. No new predictive evidence establishes 5%. |
| **Ops/support: $1,377.88M** | Exact calibration solves **v=0.2152096**; rounded **0.215** predicts **$624.014M** versus actual **$624M**. This is calibration, not validation. Future **−10% variable-unit cost/+8% fixed growth** are assumptions. | AI direction is supported; its scope and magnitude are unidentified jointly with fixed growth. Removing FY27’s 10% decline lowers EBITDA **$30.29M**: that assumption works **against** the short. |
| **COR total: $2,759.61M** | Fees **$1,964.55M**, chargebacks **$124.37M**, hosting **$446.83M**, other **$223.86M** sum correctly. Bookings **172.7337M = 621.8414M nights/3.60**. Fees include seasonal factors and a small cross-border adjustment, not simply 1.70% of GBV. | Fee rebates and chargeback deterioration are sourced directions; persistence, seasonal factors and 3.60 nights/booking are estimates. Payment-processing levels after 2021 are accumulated MD&A deltas. The residual implies approximately **$0.369/night**, not exactly $0.36. Lower fees favor EBITDA; shorter stays and elevated chargebacks favor the short. |

**B2. Which Street bar?**

Use **LSEG annual adjusted EBITDA $5,766.10M / revenue $15,819.34M**, **n=44 for each**, as of **11 September**; EBITDA last changed September 10 and revenue September 8. The repo verifies the adjusted-dollar series against reported adjusted EBITDA. Label **36.45%** an *implied margin*, not the average analyst margin. [Consensus CSV:5](C:/Users/krish/citadel-abnb-marginaudit/data/processed/margin_build/03_consensus_pit/03_current_consensus.csv:5)

The quarterly sum is **$5,826.40M/$15,846.15M = 36.7685%**, from smaller panels—EBITDA n=17–19, revenue n=19–21—and different observation dates. It is a useful quarterly comparison, not an interchangeable annual consensus.

For matched analysts, ratio-of-means is a **revenue-weighted** average margin; its difference from the simple average depends on covariance between **revenue and margin**, not merely revenue and EBITDA. The observed **1.3911pp** gap is too large for that explanation under the published common-panel ranges. Different contributors, definitions or vintages require investigation; the saved files cannot identify which.

FY26’s **35.6158% versus 34.6593%**, and FY28’s **37.6543% versus 35.1062%**, reinforce the unresolved basis issue. Being below management’s floor does not itself invalidate the field. If FY27’s field were comparable, **35.6583% modeled margin exceeds 35.0586% by 0.600pp**; applying the field to Street revenue gives a synthetic **$5,546.04M** EBITDA bar, below our model.

**B3. Gap, attribution and growth**

Using common forecast D&A of **$82.536M**, Street cash costs are approximated as revenue minus adjusted EBITDA plus D&A; undisclosed Street add-backs remain a limitation.

| FY27 comparison | Annual Street | Quarterly-sum Street |
|---|---:|---:|
| Our revenue minus Street | +9.27 | −17.54 |
| Our costs minus Street | +131.16 | +164.65 |
| **Our EBITDA minus Street** | **−121.89** | **−182.19** |
| Evidence-only costs minus Street | −64.04 | −30.55 |

Your mechanism is verified, but the excess does **not equal** reconciliation exactly:

**−$30.55M underlying cost difference + $116.83M hosting + $78.37M marketing = +$164.65M.**

No quarterly Street estimates for all five cost lines exist here, so a genuine five-line attribution is unavailable. The annual COGS field suggests **$101.19M COR excess**, leaving **$29.98M** across other lines, but that field has its own vintage/contributor limitations. Assigning everything to S&M by holding our other lines fixed is conditional algebra, as C4 acknowledges.

| Ex-reserve cash costs, including D&A | FY26 | FY27 | Growth |
|---|---:|---:|---:|
| Our build | 9,248.90 | 10,266.94 | **11.01%** |
| Annual Street, common D&A assumption | 9,216.10 | 10,135.78 | **9.98%** |
| Quarterly Street plus actual 1H26 | 9,216.20 | 10,102.29 | **9.61%** |

Panel history: **$6,305M → $7,119M → $8,031M**, FY23–25, giving **12.91%/12.81%** growth. Both forecasts imply deceleration. Raw panel totals include lodging reserves and would distort this comparison.

**B4. Evidence, opinions and the defensible claim**

Evidence comprises reported component dollars, historical SBC, booking/stay data, contractual commitments and management’s qualitative investment/AI statements. **Every FY27 numerical growth rate, the hosting expense level and reconciliation persistence remain opinions.** “Evidence-only” therefore means *without reconciliation*, not *without judgment*.

Ranked against explicitly flat/no-new-investment counterfactuals:

1. **Marketing +15%:** **$317.83M** EBITDA exposure; five percentage points alone equal **$105.94M**.
2. **Hosting versus the model’s $224M historical proxy:** **$222.83M**; **$116.83M** specifically comes from reconciliation. The historical proxy itself is estimated.
3. **PD +8% plus tooling:** **$148.17M**, including **$30M** explicitly unsized AI spending.

These are sensitivity magnitudes, not confidence intervals.

To defend “FY27 costs above consensus,” the team needs evidence that the Q3 spending increment **persists**, a hosting expense schedule that avoids overlapping AI allocations, marketing budgets/component disclosures supporting continued growth, and a matched annual Street benchmark. On the current quarterly comparison, only **$30.55M** of additional cost above the evidence-only case is needed to cross Street—but the claimed **$164.65M excess** requires substantially more support. Until then, pitch it as a **conditional cost-persistence risk**, with the evidence-only outcome visible.