**F01 — 22%: plausible judgment, not defensible under the implemented resolver.**  
The simulation reproduces at 18.262%; the additional four points are judgmental.  
“Higher than Q4” at a 7.5% Q4 print does not imply growth ≥8.2%.  
The historical format count and reference-class exclusions also need correction.  
First fix the language-to-resolution mapping, then rerun; auditor estimate: **26%**.

**F02 — median +9.4%: numerically reproducible, conditionally defensible.**  
The seven percentiles and three requested threshold probabilities reproduce.  
The external anchor is an August observation, and its adjustment extrapolates across different quarters.  
The claimed three independent estimates share substantial inputs.  
Retain the distribution as a judgmental model, repair its evidence claims; auditor median: **+10.3%**.

**F03 — 8/17/27/38/10%: not defensible as written.**  
The forecast changes “no numeric guidance” into “no identifiable margin level.”  
Three of five historical February statements contain no numeric FY margin guidance.  
Applying the question literally moves the model’s option (e) probability to **48.025%**.  
First restore the original options; auditor vector: **3/5/10/32/50%**.

**F04 — 55%: defensible as a rough judgment, with repairs required.**  
The spending-ratio model reproduces at 58.091%; reported historical shares check out.  
The Street residual omits D&A, and the conditional model does not aggregate to its unconditional model.  
FY26E is improperly included in the historical base rate; management attribution is overstated.  
Repair the bridge and rebuild conditionals under corrected F03 buckets; auditor estimate: **55%**.

## Scope and reproduction

Audit date: **2026-09-17**. Reviewed the four revision-1 logs, forecast JSONs, model code, saved datasets, market snapshots, and cited repository evidence. No files were changed, no forecasts registered, and neither prohibited raw directory was opened.

The `py -3.13` launcher was inaccessible. The repository’s `python` worked. I executed the four models’ calculation functions in memory with bytecode writing disabled, avoiding their file-writing entry points. F02’s final mixture was reconstructed in memory.

This is a **saved-evidence audit**, not a live market refresh. No network retrieval was attempted. Some original sources referenced by the statement ledger—particularly `data/raw/margin_build/05_mgmt_statements_v2/web/GS26.html`—are absent from this checkout. Their ledger entries can be checked; their original page contents cannot be independently certified here.

In the findings below, `F01/`, `F02/`, `F03/`, and `F04/` abbreviate these directories:

| ID | Directory under `docs/pitch-forecasts/questions/` |
|---|---|
| F01 | `q1-27-nights-guide-above-82/` |
| F02 | `q1-27-revenue-guide-growth/` |
| F03 | `fy27-margin-guide/` |
| F04 | `fy27-sm-share-above-219/` |

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A08-01 | F03 | critical | `F03/research-log.md:28`; JSON `final.convention` | Qualitative “stable,” “maintain,” and “expand” statements are assigned numeric buckets despite option (e) explicitly being **no numeric FY27 margin guidance**. The special inclusion of “down” in (d) does not authorize converting other qualitative statements into numbers. | Compared `QUESTIONS.md:180–181` with the resolver and executed `run(strict_qual_to_e=True)`. | Use the literal options, retaining explicit down/investment framing in (d). Same-model corrected vector: **a .014980, b .044875, c .099845, d .360050, e .480250**. |
| A08-02 | F01 | critical | `F01/research-log.md:28`; `datasets/f01_model.py:24–26` | “Higher than Q4” is treated as Yes whenever Q4 ≥7.5%. A statement implying only growth >7.5% does not imply ≥8.2%. “Nearly as strong” is also assigned an unsupported fixed one-point decrement. These are substantive resolver changes, even though disclosed as conventions. | Read the original threshold and inspected the code. Draws classified Yes through the “higher” branch with Q4 in [7.5, 8.2) contribute **0.629 percentage point** to the base simulation. | Resolve from the public statement’s actual quantitative implication. Removing only the identified unsupported higher-growth slice lowers the tree from **18.262% to 17.633%**; the complete wording model still needs rebuilding. |
| A08-03 | F01–F04 | major | Each log §5 | Three independently derived estimates have not been established. F01’s base rate and anchor reuse its print distribution/tree; F02’s base estimate uses C01 and a GBV adjustment; F03’s “anchor” is an internal prior using the same historical statements; F04’s Street residual holds the team’s other cost lines fixed. | Traced the derivations, source files, and model inputs. F01’s “Street-through-tree” result reproduces at **43.607%**, demonstrating shared model dependence. | Label the estimates **partially dependent** and use `NOT_INDEPENDENTLY_DERIVED` where appropriate. Distinguish observed consensus levels from model-created event probabilities. Agreement between these estimates is not independent corroboration. |
| A08-04 | F04 | major | `F04/research-log.md:37,79`; JSON `estimates.anchor_source` | The Street-implied S&M bridge omits D&A. Under this line build, adjusted EBITDA equals revenue minus the five cash-cost lines **plus D&A**. | Read `40_line_build/40_annual.csv`, FY27/base, and `23_final_model/23_vs_consensus.csv`, FY27. Other costs = **$6,807.3146M**; D&A = **$82.5359M**. | Correct residual S&M to **$3,328.4613M / $15,819.3392M = 21.0405%**, versus the unadjusted **20.5187%**. State that the other cost lines remain team assumptions. |
| A08-05 | F04 | major | `F04/research-log.md:79–80` | Analyst EBITDA dispersion is used as though it were the predictive standard deviation of realized S&M. The subsequent increase from approximately 10% to 30% has no specified uncertainty model. | The cited CSV identifies **$154.22275M** as `lseg_ebitda_sd_musd`, not forecast-error SD or S&M uncertainty. With the corrected residual, the same mechanical Gaussian calculation gives **18.90%**, not approximately 10%. | Keep 18.90% only as a **dispersion-based illustration**, not a market probability. Model uncertainty in revenue, other costs, and realization error before constructing an anchor probability. |
| A08-06 | F04/F03 | major | `F04/research-log.md:87–107`; `datasets/f04_model.py:30–32` | The simulated conditionals do not aggregate to the simulated unconditional estimate. The published “three-point shrink toward the unconditional” is also inaccurate: all five probabilities decrease, including those already below the unconditional probability. | Exact simulated conditionals are **.283028/.436680/.580908/.783943/.620940**. Weighted by original F03, they give **.613715**, versus unconditional **.580908**. Published conditionals do aggregate to **.5494**. Reweighting those old conditionals with the literal F03 model gives **.589787**. | Construct a joint model or explicitly label the conditional table as elicited judgments. Re-estimate it after correcting F03; do not merely swap F03 weights or claim a uniform shrink. |
| A08-07 | F04 | major | `F04/research-log.md:77` | The base rate includes FY26E as a successful historical observation. That forecast also supplies the decomposition’s starting spending level, creating circular support. | Recomputed annual ex-SBC shares from `02_financial_panel/02_panel_annual.csv`. In completed years 2022–2025, increases ≥0.6pp occurred **2/4**, not 3/5. FY26 is absent from the completed annual panel. | Use **2/4 observed** as the broad reference class, with explicit regime sensitivity: 2023–2025 **2/3**, 2024–2025 **2/2**. Treat FY26E as an uncertain conditioning input, not another observation. |
| A08-08 | F04 | major | `F04/research-log.md:39,69,73` | “Management’s own language says marketing stays elevated into 2027 launches” and “management’s stated deceleration” overstate the cited evidence. No quoted management budget establishes the model’s +15% marketing/+11% field assumptions. | Checked `05_statements.csv` V021–V026 and `05_fy27_hints.csv` H07/H08. V023 announces future products; H07/H08 contain **analyst implications** about spending. The original Goldman HTML is missing locally. | Attribute these as the team’s spending interpretation. Keep the figures as scenarios; do not present them as management’s FY27 spending guidance. |
| A08-09 | F04 | major | `F04/research-log.md:42,70,82` | A historical marketing cut to defend the FY24 floor is claimed, but the cited letter describes **higher** marketing spending. The $177M cut is a modeled future action, not an observed precedent. | Read the 3Q24 letter: expected Q4 margin decline is attributed to higher marketing and product-development expenses. `40_short_case_summary.csv` labels the **$176.709M** cut as `short_with_q4_marketing_cut`. | Remove the asserted precedent. A discretionary spending response remains plausible, but the three-point forecast haircut must be justified as judgment rather than historical evidence. |
| A08-10 | F02 | major | `F02/research-log.md:45,52,92–95` | The designated live anchor is stale under the supplied forecasting standard. Its observation date is 13 August, not the September pull/build date used in the freshness summary. | `06_consensus_quarterly_2027.csv`, 1Q27: **$3,010.32375M**, n=21, `revenue_obs_date=2026-08-13`, pull `2026-09-13T011505`. It was **35 days old** at forecasting. The L0 register has no 2027Q1 row. | Retain it as a dated historical comparison, not a current verified anchor. Obtain a newer observation or state that no fresh external anchor is available; do not reset source age when copying it into a new note. |
| A08-11 | F02 | major | `F02/research-log.md:35,81,92` | The measured same-target consensus re-anchoring relationship is used to justify reducing the **following quarter’s** consensus by the anticipated Q4 guide gap. That cross-quarter transmission is not the relationship tested. | Rebuilt the 18-row join in `16_consensus_at_print_merged.csv`: prior consensus and later consensus both refer to the guided quarter. Slope **.98844**, r **.99273** reproduce. Nothing in that calculation estimates Q4-guide → Q1-consensus transmission. | Label the −1.9% Q1 adjustment as an assumption and test zero/partial/full transmission. Do not cite the .988 slope as evidence for a cross-quarter coefficient. |
| A08-12 | F01 | major | `F01/research-log.md:36,83–84` | The stated directional-format base rate, 12/16 before 2025, is wrong in the named ledger. | Filtered next-quarter nights rows by publication year <2025 in `02_guidance_ledger.csv`: **16/16 directional**. The bucket-era count **3/4**, and sentence coverage **17/17 since 2Q22**, do reproduce. | Correct the count and show the small-sample regime judgment behind the chosen 72% bucket/24% directional split. It is not an empirical estimate from 12/16. |
| A08-13 | F01 | major | `F01/research-log.md:33–34` | The February reference class excludes 4Q21 because it lacks an explicit y/y descriptor, despite its historical comparator implying growth well above the threshold. Other comparator-based sentences are included. | The ledger quotes “significantly exceed Q1 2019 levels,” comparator **83.1M**. The KPI panel’s 1Q21 actual is **64.4M**: merely exceeding 83.1M implies growth **>29.04%**. | Include this provable Yes-type case, or consistently restrict the class to explicitly numeric y/y statements. Retaining the log’s other four classifications changes its count to **3/5**, still too regime-dependent to use directly as the forecast. |
| A08-14 | F03 | minor | `F03/research-log.md:96,109`; JSON `final.strict_convention_vector` | The published literal-reading alternative sums to **1.01**, and its small-probability option is not subjected to the required extreme-probability gate. | Summed `.02+.05+.10+.36+.48`; compared with the saved sensitivity CSV and exact rerun. | Publish **.015/.045/.100/.360/.480**, which sums to 1.000 at three decimals. If adopting this vector, complete the gate for option (a) ≈1.5%; do not round it upward while also rounding (b) upward. |
| A08-15 | F03 | minor | `F03/research-log.md:42` | “February prints were up-days 6 of 6” contradicts the cited reaction panel. | `abnb_guidance_reaction_panel.csv`, 4Q23 print dated 2024-02-13: **ret_1d −1.7%, exc_1d −2.8%**. Across the six February events, both positive counts are **5/6**. | Correct to **5/6**. This is marked non-load-bearing, so it need not move F03. Also flag the inherited error in the brief. |
| A08-16 | F02 | minor | `F02/research-log.md:38,128` | “First sub-teens quarterly guide since 2023” is contradicted by the log’s own historical series. Copying the assertion from INT-20 does not validate it. | The 1Q25 guide was **4–6%**, midpoint **5%**, in the ledger and 4Q24 letter. The 4Q24 guide also implied approximately **8.88%** from its dollar midpoint. | Remove “first since 2023.” Describe the forecast as a deceleration from the 1Q26 guide, with the appropriate reported-dollar comparison. |
| A08-17 | F02 | minor | `F02/research-log.md:34,87` | The Q1-minus-Q4 guide-growth SD is misstated, and the number of February letters providing a growth range alongside dollars is understated. Rounded stated growth and dollar-implied growth are mixed. | Listed changes −1.5/0/−4/+6.5 have sample SD **4.4814pp**, not 4.3. Dollar-implied changes have mean **0.1193pp**, SD **4.4396pp**. Four of five February dollar-guide letters also have numeric growth ranges, not two. | Use the dollar-implied series consistently for this question, or label reported-integer approximations. Correct the count to **4/5**. |
| A08-18 | F01 | minor | `F01/research-log.md:40` | The approximately 100bp quote refers to the **Q2 2026 forecast**, while the paragraph attributes it to the Q1 print. Its ex-conflict comparison arithmetic is also misstated. | Read the 1Q26 letter. Q1’s separate statement says nights would have grown approximately 10% absent the conflict; the 100bp sentence is in the Q2 outlook. Relative to 4Q25’s 9.82%, a 10% comparator is **0.18pp higher**, not 1.65pp lower. | Separate Q1’s observed shortfall from Q2’s forecast assumption. Model any 2027 conflict-recovery benefit explicitly rather than describing the ex-conflict comparator as easier. |
| A08-19 | F01/F02 | minor | F01 claim 11; F02 claim 16; saved Kalshi JSONs | “Volume and open interest null” is false; “zero liquidity” conflates different fields. The purported contradiction between annual and quarterly forecasts is not a mathematical inconsistency. | Annual >575M: `volume_fp=277.20`, `open_interest_fp=87.02`; quarterly >148M: **428.14/423.14**. Both have zero 24-hour volume and `updated_time=2026-08-04…`. Subtracting marginal medians also need not produce a valid implied quarterly median. | Correct the field names and describe these as inactive/stale adjacent snapshots, with limited relevance. Keeping zero forecast weight is reasonable; the stated factual rationale needs correction. |
| A08-20 | F04 | minor | `F04/research-log.md:40` | S&M guidance outcomes use GAAP-inclusive shares without distinguishing them from this question’s ex-SBC target; two guide IDs are wrong. | Ledger GAAP outcomes are −174.66bp/−27.22bp. Recomputed ex-SBC changes are **−143.797bp/−22.579bp** for FY22/FY23. Correct IDs end **FY2023-065** and **1Q23-063**, not 066/062. | Label the GAAP basis, show ex-SBC outcomes alongside it, and repair the IDs. Do not treat the two accounting bases as interchangeable calibration observations. |
| A08-21 | F02 | minor | `F02/research-log.md:91`; JSON `model.structure`; `datasets/f02_model.py:9` | The documented Q4 nights SD is 1.6pp, but the model producing the published distribution uses **1.7pp**. | Inspected the function default and reproduced the published distribution with that default. | Correct the documentation to 1.7pp or deliberately rerun at 1.6pp. This is a reproducibility discrepancy, not evidence that the published percentiles were fabricated. |

## Reproduced numerical checks

| Check | Recomputed result |
|---|---|
| F01 base tree | **P(Yes)=.1826225** |
| F01 internal expectation / Q4 print ≥8.2% | **.359060 / .421660** |
| Resolved nights buckets above their upper endpoint | **2/2**: +3.82pp and +0.15pp |
| Q1 revenue cushions, 1Q22–1Q26 | **4.4291%, 1.8487%, 4.4878%, .9778%, 2.6054%** |
| Q1 cushion mean / median / sample SD, n=5 | **2.8698% / 2.6054% / 1.5606pp** |
| Q1 cushions within W1 target years, n=4 | Mean **2.4799%**, SD **1.4947pp** |
| Q1 cushions within W2 target years, n=3 | Mean **2.6903%**, SD **1.7566pp** |
| February guides above pre-guide Street | Full **4/5**; W1 Q1 targets **3/4**; W2 Q1 targets **2/3** |
| Q1 λ, 2023–2026 | **12.8028%, 13.0345%, 12.3255%, 12.6122%** |
| Q1 last-two-season PIT errors, 2024–2026 | **−.5540%, +4.8124%, +.5371%** |
| F02 final P(<10), P(<9.4), P(≥12) | **.5616675 / .4801550 / .2539100** |
| F02 final mass below 0 / above 20 | **.003385 / .002535** |
| F03 original vector | **.0807275/.1652525/.2676175/.3861525/.1002500** |
| F04 base model | **P=.5809075**, median ratio **22.1573%** |
| FY25 reported S&M ex-SBC | **(2,588−212)/12,241 = 19.4102%** |
| 1H25 / 1H26 S&M ex-SBC shares | **21.5723% / 23.9262%**, increase **2.3539pp** |
| FY27 line-build base S&M share | **3,459.6236/15,828.6066 = 21.8568%** |

The Q1 subsamples are small subsets of W1/W2, not 14/10 independent observations. None of the four new probability models establishes probability calibration through a historical W1/W2 replay. Their 400,000 draws establish numerical integration precision, not empirical sample size.

The main F03 vector sums to one; F02’s percentile table is monotone and its tail masses reproduce. F01/F04 do not trigger the binary extreme gate. Impact tables are not required for these F questions.

## F01 — what the log does well and should keep

Keep the distinction between actual nights growth and management’s descriptor: “high single digits” alone resolves No. The RNPL module values reproduce—4Q26 base **7.61%**, 1Q27 base **6.47%**, versus the WS06 v2 1Q27 base **8.21%**. The source comparison and print-conditioned sensitivity table are useful.

The strongest case against 22% is the independently observed Bloomberg Q4 nights level: **134M, +9.926%, n=28**, in `E_street_distribution_vs_team.csv`. The thesis models share RNPL assumptions; their agreement should not overwhelm that disagreement. Conversely, a healthy actual print still need not produce qualifying guidance.

## F02 — what the log does well and should keep

Keep the explicit guide-versus-print distinction, fixed $2,678M denominator, separate cushion, and prohibition on subtracting FX twice. The underlying kernel calculations, final mixture, percentile table, and threshold probabilities reproduce.

The strongest case against the low median is parameter uncertainty: the current observed λ and adopted GBV path, with the W1 Q1 mean cushion, imply approximately **+10.3%** before introducing the additional negative λ tilt. That does not invalidate +9.4%; it identifies the judgment that needs defending.

## F03 — what the log does well and should keep

Keep the verbatim February statements, the distinction between numeric floors and qualitative language, the explicit regime model, and the acknowledgment that the historical February margin-rule test failed.

The strongest opposing case is already in the evidence: three of five February guides were qualitative. Under the actual question, that evidence supports option (e), rather than being redistributed among numeric buckets. A qualitative flat-margin statement and an economic expectation of roughly 36% are different forecast objects.

## F04 — what the log does well and should keep

Keep the precise ex-SBC construction, unrounded threshold, FY27 10-K resolution source, and sensitivities to both spending growth and revenue. The line-build base is correctly recognized as **below** 21.9%, despite rounding to 21.9% in presentation.

The strongest No case is ordinary spending deceleration: the saved model gives approximately **32%** breach probability at 10% S&M growth. The strongest Yes case is a revenue shortfall with spending largely maintained. Neither requires treating the allocated 23.5% spending forecast as an independent measurement.

## Auditor estimates

These are separately constructed audit judgments using the saved information set, not blind forecasts or fresh market consensus.

**F01: 26%, subjective uncertainty interval 12–45%.**  
Use three judgmental states: persistent RNPL drag 45%, ordinary growth 35%, strong bookings/recovery 20%; qualifying public-language probabilities are 8%, 25%, and 70%, respectively.  
The weighted probability is **26.35%**. These language probabilities require an actual qualifying descriptor or quantitative implication; they do not use the unsupported 7.5% shortcut.

**F02: median +10.3%; distribution below.**  
Current Q1 λ **12.6122%** × adopted lagged GBV **$24,000.9M**, divided by **1.024799** for the W1 Q1 cushion, gives a guide around **$2,953.8M**, or **+10.30%**.  
Use a judgmental **4pp SD** to reflect uncertain GBV, recognition, cushion, and February policy; this is not a calibrated confidence interval.

| Percentile | Growth |
|---|---:|
| 5 | 3.7% |
| 10 | 5.2% |
| 25 | 7.6% |
| 50 | 10.3% |
| 75 | 13.0% |
| 90 | 15.4% |
| 95 | 16.9% |

Under that normal approximation: **P(<10%)=.470; P(<9.4%)=.411; P(≥12%)=.335**. Working-range mass: **below 0%=.0050; above 20%=.0077**. No material near-zero-density region appears within the central working range.

**F03: (a) 3%, (b) 5%, (c) 10%, (d) 32%, (e) 50%.**  
Start with the observed qualitative/numeric split **3/5 versus 2/5**, then increase numeric-guidance probability to 50% for the more recent floor-setting practice.  
Allocate the remaining mass to numeric buckets and explicit investment/down language, preserving (e) for nonnumeric flat/expansion statements. All options exceed 2%.

**F04: 55%, subjective uncertainty interval 35–75%.**  
Use spending-discipline, ordinary-budget, and renewed-investment states weighted **25/50/25%**, with breach probabilities **20/55/90%**: weighted probability **55%**.  
This is consistent with the exact 21.8568% base ratio sitting just below the threshold, while revenue downside and continued investment supply upside skew.

For comparison under the corrected auditor F03 vector, judgmental F04 conditionals **a .25 / b .35 / c .50 / d .70 / e .50** aggregate to **.549**. These are elicited conditional judgments, not outputs of the original conditional simulation.

## Reproduction script

Save as `docs/pitch-forecasts/audits/A08-reproduce.py` and run from the repository root:

```powershell
python -B docs/pitch-forecasts/audits/A08-reproduce.py
```

The script uses only Python’s standard library and pandas, makes no network requests, and writes nothing. It recomputes historical statistics from primary repository CSVs; checks explicitly labeled “saved model” read the saved simulation summaries.

```python
from pathlib import Path
from statistics import NormalDist
import json
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path.cwd()
QROOT = ROOT / "docs/pitch-forecasts/questions"


def read(path):
    return pd.read_csv(ROOT / path, comment="#")


def show(label, value):
    print("\n" + label)
    if isinstance(value, pd.DataFrame):
        print(value.to_string(index=False))
    else:
        print(value)


def qkey(q):
    return (2000 + int(q[2:])) * 4 + int(q[0])


g = read("data/processed/overnight/02_guidance_ledger.csv")
p = read("data/processed/abnb_guidance_reaction_panel.csv")
k = read("data/processed/overnight/02_kpi_panel_quarterly.csv")[
    ["quarter", "gbv_musd", "revenue_musd", "nights_m"]
].copy()
k = k.assign(order=k.quarter.map(qkey)).sort_values("order")
k["lag_gbv"] = 2 * k.gbv_musd.shift(1) / 3 + k.gbv_musd.shift(2) / 3
k["lambda_pct"] = 100 * k.revenue_musd / k.lag_gbv

# F01: count statements, not repeated commentary about the same guide.
n = g[g.metric.str.contains("nights")].copy()
pre = n[pd.to_datetime(n.print_date).dt.year < 2025]
show("F01 pre-2025 formats", pre.guide_type.value_counts().to_dict())

bucket = n[n.guide_type == "bucket"].copy()
bucket["top_beat"] = bucket.actual - bucket.value_high
show("F01 bucket outcomes", bucket[
    ["print_quarter", "target_period", "value_mid",
     "value_high", "actual", "top_beat"]
])
resolved = bucket.dropna(subset=["actual", "value_high"])
show("F01 resolved bucket beats", {
    "n": len(resolved),
    "above_top": int((resolved.top_beat > 0).sum()),
})
show("F01 nights statements since 2Q22",
     len(n[n.print_quarter.map(qkey) >= qkey("2Q22")]))

old = n[(n.print_quarter == "4Q21") &
        (n.target_period == "1Q22")].iloc[0]
prior = k.set_index("quarter").loc["1Q21", "nights_m"]
show("F01 2019-comparator implied lower growth bound",
     100 * (old.comparator_value / prior - 1))

# F02: actual / dollar-guide midpoint, without rounded growth integers.
q = g[(g.metric == "revenue_usd_m") &
      g.print_quarter.str.startswith("4Q")].copy()
q["cushion_pct"] = 100 * (q.actual / q.value_mid - 1)
show("F02 Q1 cushions", q[
    ["print_quarter", "target_period", "value_mid",
     "actual", "cushion_pct"]
])
show("F02 cushion statistics",
     q.cushion_pct.agg(["mean", "median", "std"]).to_dict())

for year in [23, 24]:
    s = q[q.target_period.map(qkey) >= qkey("1Q" + str(year))]
    show(f"Q1 target window 20{year}+", {
        "n": len(s), "mean": s.cushion_pct.mean(),
        "sample_sd": s.cushion_pct.std(),
    })

l = k[k.quarter.str.startswith("1Q")].copy()
l["pred"] = l.lambda_pct.shift().rolling(2).mean() / 100 * l.lag_gbv
l["error_pct"] = 100 * (l.pred / l.revenue_musd - 1)
show("F02 Q1 lambda and last-two-season PIT errors",
     l[["quarter", "lambda_pct", "pred", "error_pct"]])

pp = p.set_index("quarter")
changes = pd.Series([
    pp.loc[f"4Q{y}", "nq_rev_guide_growth"] -
    pp.loc[f"3Q{y}", "nq_rev_guide_growth"]
    for y in range(22, 26)
])
show("F02 dollar-implied Q1-minus-Q4 growth changes", {
    "values": changes.tolist(), "mean": changes.mean(),
    "sample_sd": changes.std(),
})
show("F02 listed rounded-change sample SD",
     pd.Series([-1.5, 0, -4, 6.5]).std())
show("F02 February numeric growth-range count", len(g[
    g.print_quarter.str.startswith("4Q") &
    (g.metric == "revenue_yoy_pct") &
    (g.guide_type == "range")
]))

feb = p[p.quarter.str.startswith("4Q")].copy()
show("February reaction and guide-gap panel", feb[
    ["quarter", "print_date", "ret_1d", "exc_1d",
     "guide_vs_street_pct"]
])
show("February positive returns", {
    "n": len(feb),
    "raw_positive": int((feb.ret_1d > 0).sum()),
    "excess_positive": int((feb.exc_1d > 0).sum()),
})
for year in [2022, 2023, 2024]:
    s = feb[pd.to_datetime(feb.print_date).dt.year >= year]
    s = s.dropna(subset=["guide_vs_street_pct"])
    show(f"February guide vs Street, {year}+", {
        "n": len(s),
        "above": int((s.guide_vs_street_pct > 0).sum()),
        "mean_gap_pct": s.guide_vs_street_pct.mean(),
    })

reg = read("data/processed/forecast_methods/L0/L0_vintage_register.csv")
show("F02 historical pre-guide vendor/timestamp rows", reg[
    reg.period.isin(
        ["2022Q1", "2023Q1", "2024Q1", "2025Q1", "2026Q1"]
    ) & (reg.role == "pre_guide")
][["period", "vendor", "value", "as_of_timestamp"]])
show("F02 2027Q1 L0 row count", int(reg.period.eq("2027Q1").sum()))
cons = read(
    "data/processed/margin_build/06_fy27_path_v2/"
    "06_consensus_quarterly_2027.csv"
)
show("F02 separate 1Q27 consensus observation",
     cons[cons.quarter == "1Q27"])

# Rebuild the SAME-TARGET consensus revision relationship.
cs = read("data/processed/overnight/16_consensus_at_print_merged.csv")
rows = []
for _, r in cs.iterrows():
    if not isinstance(r.next_quarter, str):
        continue
    following = cs[cs.print_quarter == r.next_quarter]
    if len(following) != 1:
        continue
    pre_c = r.next_q_cons_revenue_musd
    guide = r.next_q_guide_mid_musd
    post_c = following.iloc[0].cons_revenue_musd
    if any(pd.isna(x) for x in [pre_c, guide, post_c]):
        continue
    rows.append({
        "print_date": r.print_date,
        "target": r.next_quarter,
        "kappa": 100 * (post_c / guide - 1),
        "gap": 100 * (guide / pre_c - 1),
        "revision": 100 * (post_c / pre_c - 1),
    })
rev = pd.DataFrame(rows)
for start in ["1900", "2023", "2024"]:
    s = rev[rev.print_date >= start]
    show("Same-target revision regression " + start + "+", {
        "n": len(s),
        "mean_kappa": s.kappa.mean(),
        "slope": s.gap.cov(s.revision) / s.gap.var(),
        "correlation": s.gap.corr(s.revision),
    })

# F03: ledger "point=0" is not a numeric margin in the public sentence.
fy = g[
    g.print_quarter.str.startswith("4Q") &
    g.target_period.str.startswith("FY") &
    g.metric.str.startswith("adj_ebitda_margin") &
    g.print_quarter.map(qkey).ge(qkey("4Q21"))
].copy()
fy["numeric_in_quote"] = fy.quote.str.contains(
    r"\d+(?:\.\d+)?\s*%", regex=True
)
show("F03 February FY statements",
     fy[["print_quarter", "target_period", "quote", "numeric_in_quote"]])
show("F03 numeric/qualitative counts",
     fy.numeric_in_quote.value_counts().to_dict())
floors = fy[fy.numeric_in_quote &
            fy.guide_type.eq("floor")].copy()
floors["beat_bp"] = 100 * (floors.actual - floors.value_low)
show("F03 resolved February numeric floor beats",
     floors[["target_period", "value_low", "actual", "beat_bp"]])

# F04: recompute from GAAP expense less functional SBC.
annual = read(
    "data/processed/margin_build/02_financial_panel/02_panel_annual.csv"
)[["year", "revenue", "sm_gaap", "sbc_sm", "sm_cash"]].copy()
annual["share"] = 100 * (annual.sm_gaap - annual.sbc_sm) / annual.revenue
annual["change_pp"] = annual.share.diff()
show("F04 reported annual ex-SBC shares", annual)
for start in [2022, 2023, 2024]:
    s = annual[annual.year.between(start, 2025)]
    show(f"F04 observed >=0.6pp increases, {start}-2025", {
        "n": len(s), "hits": int((s.change_pp >= 0.6).sum()),
    })

quarterly = read(
    "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv"
)
for year in [2025, 2026]:
    h = quarterly[(quarterly.year == year) & quarterly.qn.le(2)]
    show(f"F04 H1 {year}", {
        "sm_cash": h.sm_cash.sum(), "revenue": h.revenue.sum(),
        "share": 100 * h.sm_cash.sum() / h.revenue.sum(),
    })

line = read("data/processed/margin_build/40_line_build/40_annual.csv")
b = line[(line.period == "FY27") & (line.scenario == "base")].iloc[0]
street = read(
    "data/processed/margin_build/23_final_model/23_vs_consensus.csv"
)
v = street[street.period == "FY27"].iloc[0]
other = b[["cor_cash", "ops_cash", "pd_cash", "ga_cash"]].sum()
raw = v.lseg_revenue_musd - v.lseg_ebitda_musd - other
corrected = raw + b.da
show("F04 Street residual accounting bridge", {
    "other_costs": other, "DA": b.da,
    "uncorrected_SM": raw,
    "uncorrected_share": 100 * raw / v.lseg_revenue_musd,
    "corrected_SM": corrected,
    "corrected_share": 100 * corrected / v.lseg_revenue_musd,
    "dispersion_tail_NOT_predictive": 1 - NormalDist(
        corrected, v.lseg_ebitda_sd_musd
    ).cdf(0.219 * v.lseg_revenue_musd),
})
show("F04 exact line-build base share", 100 * b.sm_cash / b.revenue)

# Published vector/coherence checks; these are not new simulations.
f3 = json.loads((
    QROOT / "fy27-margin-guide/forecasts/2026-09-17-forecast.json"
).read_text(encoding="utf-8"))
f4 = json.loads((
    QROOT / "fy27-sm-share-above-219/forecasts/2026-09-17-forecast.json"
).read_text(encoding="utf-8"))
weights = list(f3["final"]["vector"].values())
conditional = list(f4["conditionals"]["p_given_f03"].values())
show("Published F03 vector sum", sum(weights))
show("Published strict F03 vector sum",
     sum(f3["final"]["strict_convention_vector"].values()))
show("Published F03/F04 total probability",
     sum(w * c for w, c in zip(weights, conditional)))

saved = read(
    "docs/pitch-forecasts/questions/fy27-sm-share-above-219/"
    "datasets/f04_sensitivity.csv"
)
model_c = saved[saved["case"].str.startswith("F03")]["p_ge_21.9"]
show("Saved model conditional weighted probability (CSV rounded)",
     sum(w * c for w, c in zip(weights, model_c)))

# Inspect the actual saved API fields, not deprecated field names.
source = QROOT / "q1-27-nights-guide-above-82/sources"
for name in [
    "kalshi_KXABNBA_open_20260917T031845Z.json",
    "kalshi_KXABNB_open_20260917T031845Z.json",
]:
    markets = json.loads((source / name).read_text())["markets"]
    fields = [
        "ticker", "yes_bid_dollars", "yes_ask_dollars",
        "volume_fp", "volume_24h_fp", "open_interest_fp", "updated_time",
    ]
    show(name, pd.DataFrame([
        {field: market.get(field) for field in fields}
        for market in markets
    ]))
```