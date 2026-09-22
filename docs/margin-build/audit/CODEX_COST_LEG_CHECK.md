**Verdict: the calculations largely reproduce, but the pitch conclusions need material qualification.** T1–T3 and R1/R3 pass their implemented tests; R2 fails as reported. However, COR’s sign-test result is sensitive to reporting precision, persistence largely disappears after controlling for the identified regime, and R1 does not establish a causal stock-price response. The **−7.5% to −9.5%** figure is a conditional historical-slope scenario, not a defensible forecast range.

Audited branch `krish/cost-leg`, commit `a0b4b01a`; pre-registration is in preceding commit `f6d01166`. I wrote no files and did not execute either `run.py`.

**Findings**

| ID | Severity | File:line | Claim | Finding with numbers | Fix |
|---|---|---|---|---|---|
| F1 | major | [41/run.py:163](C:/Users/krish/citadel-abnb-marginaudit/analysis/src/margin_build/41_cost_leg/run.py:163) | COR passes both windows | Point-value p-values reproduce. But 4Q23’s **+$0.253M** and 2Q25’s **+$0.027M** are inside the ±$0.5M reporting intervals. Adverse admissible signs give **9/14, p=.212**, and **7/10, p=.172**. | Report point-value PASS alongside interval sensitivity; resolve underlying precision before claiming robust passage. |
| F2 | major | [42 note:25](C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/42_margin_reaction.md:25) | 150bp reset is worth −7.5% to −9.5% | Revisions are measured after the stock starts moving. Day-1 slopes **2.016/2.730** already explain essentially the entire five-session slopes **2.104/2.662**. Removing 2Q24 makes W2 fail: **p=.127**. | Describe an association-based sensitivity; show uncertainty, influence tests and constant-multiple valuation. |
| F3 | major | [41 note:20](C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/41_cost_leg.md:20) | Persistence independently supports overruns | Adding the already-identified 3Q25 regime indicator reduces AR slopes from **.525/.672** to **.086/.073**, p **.254/.418**. Original forecasts are **−.683%/−.228%**, below Street costs. | Separate regime evidence from within-regime persistence. This diagnostic is exploratory, not a replacement pre-registered test. |
| F4 | major | [41 note:13](C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/41_cost_leg.md:13) | Historically low FY27 growth proves Street costs are too low | Annual ranking is correct, but Street FY25–FY27 cost CAGR is **12.495%**, versus the historical benchmark **12.614%**. Applying that benchmark for two years from FY25 produces only **$21.3M / 13.5bp** extra cost, versus the selected FY26-base scenario’s **$235M / 149bp**. | Show both bases; justify why FY26’s +15% spending growth should be followed by another historical-average year. |
| F5 | major | [42 note:21](C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/42_margin_reaction.md:21) | Six margin cuts had flat/falling revenue revisions | Three had positive revisions: **4Q23 +.269%, 3Q24 +.442%, 2Q25 +.477%**. Strictly nonpositive revenue revisions identify **3 prints, mean −11.3%**, not six averaging −8.2%. The six positive-revenue/margin-cut prints averaged **−2.6%**. | Correct membership or disclose an explicit “approximately flat” threshold. |
| F6 | major | [42 note:12](C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/42_margin_reaction.md:12), [18](C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/42_margin_reaction.md:18) | Every margin-driven fall is forward-looking; margin is not priced separately | **22/22 EBITDA beats** does not establish either assertion. 1Q23 beat EBITDA by **$2.677M** but missed reported margin by **.069pt**. R2 p **.327/.126** means insufficient evidence, not evidence of no effect. | Narrow the claims to the observed beat record and inability to isolate an independent margin coefficient. |
| F7 | major | [41 note:34](C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/41_cost_leg.md:34) | COR overrun identifies AI/hosting | The **$64M** recent COR residual identifies a broad accounting line, not its driver. FY27 modeled hosting is **$447M versus $330M** pre-plug; that assumption exceeds the **$101M** total COR excess. | Obtain hosting-specific evidence and a matched Street bridge; retain payments, amortization and other explanations. |
| F8 | minor | [41 note:26](C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/41_cost_leg.md:26) | “Line build” costs imply −$94M | This applies the build’s growth rate to Street’s FY26 base. Actual build costs exceed Street by **$131.2M**; the rebased scenario gives **$93.6M**, a **$37.5M** difference. | Call it “line-build growth rebased to Street FY26 costs.” |
| F9 | minor | [42 note:16](C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/42_margin_reaction.md:16) | Constant multiple means .9% per 1% revision | **.904×** applies to FY27 EBITDA, while R1 uses blended NTM EBITDA. The November table’s corresponding ratio is **1.048×**. Scenarios also omit regression intercepts. | Label the horizons and describe slope-only moves as changes relative to the zero-revision fitted baseline. |

**1. Pre-registration, timing and implementation**

- **41:** W1/W2 contain **14/10 prints**. T1 exhaustively evaluates **1,001/210** four-observation splits, with the correct positive tail. The post-hoc split is disclosed. T2 uses adjacent observations within each window, hence **13/9 regression observations**, an intercept and HC1 errors. T3 correctly implements the one-sided binomial test on point values, subject to F1.
- The ex-variable adjustment follows the specified formula. `cor_cash` equals `cor_gaap` throughout this input panel. Using the surprise file’s slightly different historical revenue precision changes the adjustment by at most **0.000187 percentage point**, without affecting verdicts. Economically, total COR/revenue is an average allocation, not an estimated marginal variable-cost rate.
- All **22 COGS observation dates precede their prints**, by **1–28 calendar days**. “Morning-of-print consensus” is imprecise: the source builder looks up the previous trading day, and individual observations can be older.
- **42:** FY labels roll correctly at February prints. The weight is exactly remaining calendar days divided by **365**, including leap years as specified. FY27 weights are **84.658%** in November and **88.493%** in the assumed February scenario.
- Every reaction date is the first trading session after the print. The fifth-session endpoint matches the post-revision lookup date, including holiday adjustments. Pre/post observation dates do not exceed their lookup dates. Independent local OHLC reconstruction gives maximum discrepancies of **.0498pp day 1 / .0480pp five-session excess**, consistent with rounding.
- T2 uses Student-t tails; R1–R3 use normal tails with HC1 errors. The pre-registration does not specify that distributional choice. Student-t R1 p-values become **.0186/.0208**; all headline verdicts remain unchanged. R3 deliberately uses revisions measured after its return endpoint: valid as a retrospective association, unsuitable as an executable signal.

**2. Headline reproduction**

The following match:

- **22/22 EBITDA beats**, **16/18** earlier cost undershoots; recent total cost surprise **+$72.747M**, comprising COR **+$63.965M** and residual **+$8.783M**.
- FY21–FY25 cost growth **21.21%, 24.96%, 13.96%, 12.72%, 12.51%**; Street FY26/FY27/FY28 **15.00%/10.04%/8.74%**. “Slowest since IPO” holds for completed FY21 onward.
- Historical-growth scenario: EBITDA **$5,531.073M**, gap **−$235.026M / −148.569bp / −$0.338 EPS**. Official-revenue counterpart: **−$629.639M / −314.951bp**.
- Marginal sensitivity: **57.751bp per percentage point of cost growth**, conditional on Street FY26 costs and FY27 revenue.
- 3Q26 recent-surprise scenarios: EBITDA **$2,340.066M / $2,286.660M**, gaps **−$21.455M / −$74.862M**.
- All 18 package-42 scenario rows reproduce. November’s 150bp/flat-revenue case gives **−$237.290M**, **−3.551% NTM**, **−7.473%/−9.454%** regression mapping and **−3.720%** constant multiple.

The −5.5%/＋1.7% margin-direction group averages also match; F5 concerns the subsequent subgroup interpretation. The note’s −$394M is slightly misrounded: **−$394.612M → −$395M**.

**3. Economic interpretation**

Revenue minus adjusted EBITDA is a useful **implied adjusted operating-cost residual**, conditional on comparable actual/consensus definitions. It is not literal cash expenditure. Different contributor sets also matter: 3Q26 revenue/EBITDA counts are **37/36**; equal FY27 counts of 44 do not prove identical membership.

COGS is a plausible broad comparator: annual mean COR surprises are **−2.16%, −5.77%, +.71%, −.26%, +2.57%, +.97%** across 2021–2026 YTD. That supports approximate level alignment, not exact methodological equivalence. Subtracting GAAP COR from adjusted EBITDA costs leaves a residual containing adjustment effects, not clean operating expenses.

Airbnb’s filing confirms COR includes payments, hosting and amortization. Its FY25 increase included **+$188M merchant fees, +$28M amortization and +$27M hosting**—strong reasons not to infer AI from the aggregate residual. [FY25 10-K](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm)

Analyst feedback could materially inflate R1, but these data cannot identify the bias magnitude. Illustratively, a **50% slope haircut** reduces the flat-revenue scenario to **−3.74%/−4.73%**; that is a sensitivity, not an estimated correction.

**4. What a judge can challenge**

The W1/W2 range is **not a confidence interval**, and the windows overlap. HC1/Student-t coefficient uncertainty maps the same 150bp scenario to approximately **−0.5% to −14.4%** in W1 and **−0.5% to −18.4%** in W2, before event-level residual uncertainty.

Extending R1 to 2022Q1 reduces its slope to **.445, p=.283**. Removing both 1Q23 and 2Q24 reduces W1’s slope to **1.072, p=.188**. These are substantial specification sensitivities.

The largest observed cut is **−5.473%**; the severe scenario reaches **−7.997%**, roughly **46% farther**. Linear extrapolation is acceptable as a labeled stress illustration, unsupported as an empirically validated price response.

**Reproduction log**

`py -3.13` was inaccessible. Inline read-only blocks used  
`& "C:/Users/krish/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -X utf8 -`.

| # | Command/calculation executed in inline stdin | Matched? |
|---|---|---|
| 1 | `pd.read_csv(...)`; reconstruct actual/Street costs and beat counts | Yes |
| 2 | `combinations(range(len(a)),4)`; `sm.OLS(...).fit(cov_type='HC1')`; `stats.binomtest(...,alternative='greater')` | T1–T3 yes |
| 3 | Rebuild dated FY blends; HC1 OLS for R1/R2/R3 | Yes; keyed revision error <5e−16 |
| 4 | Recompute close ratios from local OHLC and trading-session indices | Yes, within .05pp |
| 5 | `load_workbook(...,read_only=True,data_only=True)`; independently rebuild scenario arithmetic | Yes; scenario errors <1e−12 |
| 6 | Interval-sign, regime-control, event-deletion and two-year-CAGR diagnostics | New audit sensitivities above |