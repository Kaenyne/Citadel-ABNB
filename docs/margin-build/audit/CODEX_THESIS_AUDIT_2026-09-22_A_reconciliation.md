**1. Verdict**

Section A reproduces arithmetically, but does **not establish an independent “costs above consensus” thesis**: base 2H26 costs exceed Street-implied costs by just **$32.70M**, mostly the assumed hosting carryover. The principal weaknesses are the revenue basis used to convert management’s margin sentence into dollars, the unsupported 70/30 allocation, and persistence chosen partly to preserve the FY26 floor. Historical sentence performance measures margins at **actual revenue**, so it does not validate a cost budget calculated at guide-midpoint revenue. I reviewed the earlier audit and C1–C8 dossiers: their reproduction conclusions stand, but I disagree with C4/C6’s inference that the quarterly history establishes this particular dollar budget.

All amounts below are USD millions. Calculations were read-only at `401c0a41`; no files changed and the builder was not run.

**2. Findings**

Effects are versus the saved base unless otherwise stated; **+ raises EBITDA**. Sensitivities are alternatives, not additive.

| ID | Severity | File:line | Repo claim | Finding: sourcing, arithmetic, economics and bias | EBITDA effect: 2H26 / FY27 | Recommended fix |
|---|---|---|---|---|---|---|
| A01 | major | [run.py:132](/C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:132) | Evidence costs use guide-midpoint drivers. | **Sourcing:** false label; code reads base-path drivers. **Arithmetic:** correct on those drivers. Proportionally scaling nights and GBV to guide revenue reduces evidence costs **$9.42**, increasing the gap from **$97.36 to $106.78**. **Economics:** adjustment depends on what causes the revenue difference. **Bias:** understates the gap, against the short, under proportional scaling. | **−12.25 / −18.89**, if the larger residual is applied back to unchanged forecast drivers with existing propagation. | Identify the assumed guide-driver bridge; distinguish volume, ADR and take-rate differences. |
| A02 | major | [run.py:139](/C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:139); [group_A.md:191](/C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/discussion/group_A.md:191) | Historical sentence fidelity supports budgeting at $4,730 revenue. | **Sourcing:** history supports a margin comparison at actual revenue, not this denominator. **Arithmetic:** budget identity works. **Economics:** management’s internal expected revenue is unobserved. Using midpoint plus DEC-0001’s **1.857%** cushion gives budget **$2,449.31**, **$44.28** above base. **Bias:** midpoint budgeting lowers costs, against the short relative to that alternative. | **−57.56 / −88.78** under existing 70/30 propagation. | Show midpoint and expected-revenue budgets as explicit alternatives; do not call either an observed management budget. |
| A03 | major | [run.py:75](/C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:75); [M3 run.py:670](/C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/M3_guide_policy_margin/run.py:670) | “Down slightly” supports −0.5pp; M3 supplies historical magnitude. | **Sourcing:** −0.5pp is judgment. M3’s n=3 classification mistakenly catches “slightly” describing **EBITDA dollars** in Q4 2025. **Arithmetic:** published statistics reproduce. **Economics:** mixed statements and tiny n cannot identify a precise haircut. **Bias:** −0.5pp is against the short versus −0.7 to −1.5pp. | Using −0.7 to −1.5pp: **−12.30 to −61.49 / −18.97 to −94.84**. | Correct the adverb’s grammatical target; retain a sensitivity range rather than promote it to a fitted rule. |
| A04 | major | [run.py:142](/C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:142); [note:57](/C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/40_line_build.md:57) | 70% marketing is Q3-only; 30% hosting persists because full recurrence breaks the floor. | **Sourcing:** management named spending categories, not percentages or expiry dates. **Arithmetic:** allocation works. **Economics:** plausible scenarios, not identified facts; floor preservation is circular if used to demonstrate the floor’s reliability. **Bias:** reconciliation supports the short versus evidence-only; limiting recurrence works against it. | No/full Q4 recurrence: **+29.21 / −68.15** in 2H26. Existing reconciliation reduces FY27 EBITDA **$195.21 versus evidence-only**. | Separate the spending forecast, persistence assumption and management’s possible response to a floor breach. |
| A05 | minor | [run.py:32](/C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:32), [35](/C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:35) | Historical shares and fee factors represent seasonality. | **Sourcing/arithmetic:** shares match; fee factors closely reconstruct with equal quarterly chargebacks and hosting. **Economics:** S&M shares mix seasonality with a spending ramp, but distortion is small. G&A reserves are correctly excluded. **Bias:** including 2025 modestly increases Q4 S&M versus pre-2025 shares, supporting the short. | Pre-2025 S&M allocation only, with reconciliation recalculated: **+3.23 / +4.98**. | Generate coefficients from documented component allocations and disclose the small sensitivity. |
| A06 | major | [note:17](/C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/40_line_build.md:17); [income_statement.py:116](/C:/Users/krish/citadel-abnb-marginaudit/analysis/src/pitch_model_v2/income_statement.py:116) | Budgeted costs underpin the earnings view. | **Sourcing/arithmetic:** consensus comparison reproduces. **Economics:** near-consensus costs cannot independently establish a material cost surprise. **Bias:** describing the official model’s revenue-driven earnings miss as cost alpha overstates support for the short. | Cost difference alone: **−32.70** for 2H26 versus Street; no separate FY27 inference established here. | Attribute earnings differences explicitly to revenue and cost dollars. |

**3. Reproduction log**

All successful calculations used PowerShell inline scripts:

```powershell
@'
# Python statements, operating only on CSVs in memory
'@ | py -3.13 -X utf8 -B -
```

The launcher initially failed in the sandbox; the same read-only invocation subsequently succeeded. The following setup and command expressions reproduce the reported checks:

```python
import pandas as pd
from pathlib import Path
D = Path("data/processed/margin_build")
rd = lambda f: pd.read_csv(D / f)
L = rd("40_line_build/40_lines_quarterly.csv")
B = L[L.scenario.eq("base")].set_index("quarter")
E = L[L.scenario.eq("evidence_only")].set_index("quarter")
A = rd("40_line_build/40_annual.csv").set_index(["scenario","period"])
H = rd("02_financial_panel/02_panel_quarterly.csv").set_index("quarter")
P = rd("40_line_build/40_params.csv").set_index("name").base
C = rd("03_consensus_pit/03_current_consensus.csv")
C = C[C.vendor.eq("LSEG")].set_index("period")
cost = ["cor_cash","ops_cash","pd_cash","sm_cash","ga_cash"]
G, R, da = 4730, B.loc["3Q26","revenue"], P.da_per_q
budget = lambda r, delta: r*(1-(50.09+delta)/100)+da
gap = budget(G,-.5)-E.loc["3Q26",cost].sum()
v = E.loc["3Q26",
          ["cor_fees","cor_chargebacks","cor_other","ops_variable"]].sum()
```

| Check and command expression | Result / match |
|---|---|
| For each quarter/scenario: `c=t.loc[q,cost].sum(); e=t.loc[q,"revenue"]-c+da` | All four builds below match CSVs within **$5×10⁻¹³M**. Independently rebuilding the five lines from parameter CSVs and actuals also matched. |
| `gap; .7*gap; .3*gap; 2.005*gap` | **97.359775; 68.151842; 29.207932; 195.206349**. Current CSV matches; older note’s 52.37% does not. |
| `v*(1-G/R); gap+v*(1-G/R)` | **9.419636; 106.779411**. New proportional-driver sensitivity. |
| `budget(G*1.01857,-.5); budget(G*1.01857,-.5)-E.loc["3Q26",cost].sum()` | **2,449.305149; 141.637953**. New expected-revenue budget. |
| For `d in [-.7,-1,-1.5]`: `budget(G,d)-budget(G,-.5)` | Incremental costs **9.46; 23.65; 47.30**. Propagation multipliers: **−1.3** for 2H26, **−2.005** for FY27. |
| For `w in [0,.3,1]`: `change=(w-.3)*gap; e4=B.loc["4Q26","adj_ebitda"]-change; fy=A.loc[("base","FY26"),"adj_ebitda"]-change` | Matches the recurrence table below. |
| `25+(budget(R,-.5)-E.loc["3Q26",cost].sum())/(1595*.237)*100` | Marketing-only sentence solve **60.628499%**; matches `40_sentence_implied.csv`. |
| `C.loc[q,"revenue_mean"]-C.loc[q,"ebitda_mean"]+da` | Street costs **2,403.434301 / 2,268.766361**; matches requested rounded comparison. |

Historical checks used these additional calculations:

- **Shares:** for each line/year, `x/x.sum()`, then the equal-weight mean across 2023–25. All coded shares match the source rounded to two percentage decimals.
- **Fee factors:** `fee=cor_cash-chargebacks/4-224/4-.36*nights_m`; divide quarterly `fee/GBV` by annual `sum(fee)/sum(GBV)`, then average 2024–25. Result: **0.899238 / 1.044581 / 1.034518 / 1.033628**, close to the hardcodes.
- **M3:** filter `M3_slightly_magnitude.csv` to realised `adverb=="slightly"`; signed mean **−0.720655pp**, mean absolute **1.491241pp**. Matches, but classification is flawed.
- **WS22:** join PIT, h=0 margin rows in `baselines-margin__q_guide_implied.csv` to `10_harness_margin/targets.csv`; calculate `actual-point`. W1: **n=14, mean +0.47326pp, 6 above**; W2: **n=10, mean −0.19350pp, 4 above**; last eight: **−0.85999pp**. Matches.

**4. Answers to A1–A5**

**A1. Reconciliation and the driver mismatch**

The current saved builds are:

| Quarter / case | Cash costs | EBITDA | Margin |
|---|---:|---:|---:|
| 3Q26 evidence-only | 2,307.667 | 2,517.002 | 52.3935% |
| 3Q26 base | 2,405.027 | 2,419.643 | 50.3669% |
| 4Q26 evidence-only | 2,270.662 | 928.080 | 29.2023% |
| 4Q26 base | 2,299.870 | 898.872 | 28.2832% |

Sources: [quarterly CSV:2](/C:/Users/krish/citadel-abnb-marginaudit/data/processed/margin_build/40_line_build/40_lines_quarterly.csv:2), [evidence rows:8](/C:/Users/krish/citadel-abnb-marginaudit/data/processed/margin_build/40_line_build/40_lines_quarterly.csv:8).

At guide revenue, base EBITDA is `4730−2405.027+20.634`, exactly **49.59%**. The gap is **$97.36M**, rather than the pre-fix $96M figure.

The mismatch is real as a **labelling and conditional-basis issue**, but revenue does not uniquely determine nights and GBV. Scaling both proportionally gives evidence costs **$2,298.25M** and a **$106.78M** gap: the current gap is understated **$9.42M**. Scaling only GBV lowers costs **$7.07M**; a purely take-rate-driven revenue difference leaves these cost drivers unchanged. Those distinctions prevent treating $9.42M as an unconditional accounting error.

**A2. What “slightly” and WS22 actually establish**

M3 measures **actual year-over-year margin changes**; WS22 measures **actual margin minus a coded sentence level**. They are different statistics, and neither is a measurement of costs at guide revenue. The harness often represents qualitative “down” language as the prior-year margin ceiling, without a −0.5pp haircut. See [guides.py:136](/C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/10_harness_margin/harness_margin/guides.py:136).

M3’s three outcomes are **−0.76, +1.16 and −2.55pp**. Its “−0.7 to −1.5pp” interpretation combines a signed mean and an absolute-magnitude statistic; it is not an estimated confidence interval. Moreover, Q4 2025’s “slightly” modifies EBITDA dollars, while margin is merely expected to decline—the source explicitly distinguishes them. [Guide-language CSV:18](/C:/Users/krish/citadel-abnb-marginaudit/data/processed/margin_build/05_mgmt_statements_v2/05_guide_language_pattern.csv:18)

If management budgets on midpoint plus the **1.857%** cushion, expected revenue is **$4,817.84M** and the −0.5pp sentence implies costs **$2,449.31M**. Against unchanged base-path evidence, the gap becomes **$141.64M**; proportionally matching evidence drivers to that expected revenue gives **$139.88M**. Holding the resulting dollar budget against the existing $4,804.04M forecast gives EBITDA **$2,375.36M**, margin **49.445%**.

Thus −0.5pp is a defensible *scenario*, but neither M3 nor WS22 identifies it—or the midpoint denominator—as management’s true budget.

**A3. Allocation, recurrence and circularity**

The sources support incremental marketing and AI expenditure qualitatively. They do not establish **70/30**, a Q3-only marketing campaign, or an exactly recurring hosting amount.

Holding Q3’s full reconciliation unchanged and varying only how much repeats in Q4:

| Q4 recurrence | Q4 costs | Q4 EBITDA | Q4 margin | FY26 EBITDA | FY26 margin |
|---|---:|---:|---:|---:|---:|
| None | 2,270.66 | 928.08 | 29.20% | 5,127.72 | 35.94% |
| Base: 30% | 2,299.87 | 898.87 | 28.28% | 5,098.51 | 35.73% |
| Whole gap | 2,368.02 | 830.72 | 26.14% | 5,030.36 | 35.26% |

These use the line build’s revenue, not the official income statement’s different revenue.

Floor protection is legitimate **conditional management-behaviour modelling**. It becomes circular when floor compliance determines persistence and is then presented as evidence that the forecast independently supports the floor.

“Q3-only” also needs qualification: FY27 marketing grows from a base **including** the Q3 addition. Consequently, FY27 inherits **$78.37M** of marketing plus **$116.83M** of hosting, totaling **$195.21M**. Full expiry would remove both; merely removing Q4 recurrence does not specify FY27 treatment. [run.py:146](/C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/40_line_build/run.py:146)

**A4. Q4 seasonality and fee factors**

Q4’s five costs independently reproduce as **578.039 + 318.287 + 369.025 + 758.108 + 276.411 = $2,299.870M**.

The quarterly shares are correctly sourced:

| Line | Q1 | Q2 | Q3 | Q4 |
|---|---:|---:|---:|---:|
| PD | 25.48% | 24.66% | 24.59% | 25.27% |
| S&M | 23.97% | 27.03% | 23.70% | 25.30% |
| G&A ex reserves | 23.86% | 26.00% | 24.56% | 25.58% |

G&A’s Q4 lodging reserves—**$931M in 2023 and $81M in 2025**—are excluded, so they do not contaminate these weights. PD has no conspicuous Q4 spike.

S&M’s Q4 annual share rises **23.94% → 25.33% → 26.64%**, mixing seasonality with the ramp. But normalising over H2 substantially cancels that effect: pre-2025 weights lower Q4 S&M only **$2.48M** before reconciliation feedback.

Fee factors are approximately reproducible under the allocation documented in the log. Using those exact reconstructed factors changes reconciled 2H26 EBITDA only **−$0.31M**. They remain inferred residual seasonality, not observed quarterly merchant-fee rates.

**A5. Consensus comparison and the thesis**

LSEG’s snapshot is **11 September**, with Q3/Q4 revenue and EBITDA observations dated **7 September**; the 13 September pull reproduces those values. D&A uses the model’s common **$20.634M** assumption. [Consensus CSV:2](/C:/Users/krish/citadel-abnb-marginaudit/data/processed/margin_build/03_consensus_pit/03_current_consensus.csv:2)

| | Street-implied costs | Base costs | Base excess | Evidence-only excess |
|---|---:|---:|---:|---:|
| 3Q26 | 2,403.43 | 2,405.03 | **1.59 / 0.07%** | **−95.77 / −3.98%** |
| 4Q26 | 2,268.77 | 2,299.87 | **31.10 / 1.37%** | **1.90 / 0.08%** |

The base has **$76.00M more 2H26 revenue** and **$32.70M more costs** than Street, yielding **$43.31M more EBITDA**. Almost all Q4’s cost excess is the **$29.21M hosting carryover**. Section A therefore supports a modest, assumption-dependent Q4 cost disagreement; the official income statement’s earnings shortfall principally reflects its lower revenue against these plugged cost dollars, not independently demonstrated cost inflation.