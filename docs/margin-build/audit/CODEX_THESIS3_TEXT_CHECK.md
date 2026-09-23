**Verdict:** [The replacement text](C:/Users/krish/citadel-abnb-marginaudit/docs/margin-build/notes/43_thesis3_integration.md) is **not ready to paste**. Most dollar arithmetic reproduces, but the memo converts descriptive evidence and modelling choices into stronger claims about cost rigidity. The ten-quarter streak is wrong, the $31M comparison mixes consensus bases, and the $143.6 target changes DEC-0014’s multiple anchor. Thesis 3 survives as a **conditional cost-persistence scenario**, with materially less certain attribution than “25% of downside.”

**Findings**

| ID | Severity | Location | Claim | Finding with numbers | Fix |
|---|---|---|---|---|---|
| F1 | major | §1 thesis/body; 43a | Ten consecutive quarters; outgrown revenue “for three years” | **Nine** consecutive quarters, 2Q24–2Q26. In 1Q24, cash S&M grew **13.51%**, revenue **17.82%**. FY23 S&M growth **16.49%** also lagged revenue **18.07%**. The valid counts are **11/14** and **9/10**. | Say “nine consecutive quarters” or “11 of 14 since 1Q23.” |
| F2 | major | §1 body | S&M grows 12–17% even at zero revenue growth; costs will not flex | **11.89–16.73%** reproduces as exponentiated regression intercepts, not observed outcomes. Revenue growth never reached zero in either window: minimum **6.07%**. W2’s intercept implies a 95% interval of roughly **−3.5% to +29.7%**. | Label this an extrapolation; replace categorical rigidity with the assumed cost path. |
| F3 | major | §1 body | Each incremental S&M dollar “bought” less revenue | Ratios **6.57/3.43/2.86/2.65** reproduce. They allocate all incremental revenue to S&M and do not measure marketing returns. The last observation is **half-year**, not another annual observation. | Say “the ratio of incremental revenue to incremental S&M declined”; retain period labels. |
| F4 | major | §1 body | Evidence-only FY27 costs within $31M of Street | **$30.55M below** matches the **sum of quarterly** consensus. Against the **annual Street benchmark used in this memo**, evidence-only EBITDA costs are **$64.04M below**. Removing the persistence additions increases FY27 EBITDA **$195.21M**. | Use one consensus basis and show the evidence-only alternative explicitly. |
| F5 | major | §1 valuation; §3 | 0.49 turns supports 15.6x→14.5x | The fitted dependent variable is **12-row changes in EV/LTM EBITDA**, not EV/FY27 EBITDA. The **0.4860, CI 0.3172–0.6548, n=35** reproduces, but transferring it to a forward multiple is an assumption. Spot re-anchoring gives **$143.59**; the literal DEC-0014 line gives **$148.06**. | Disclose both the denominator transfer and new anchor; treat compression as sensitivity. |
| F6 | major | §3 attribution | Thesis 3 supplies $5.8, or 25% | Correct only for the selected sequence. Costs first gives **$3.43, 14.75%**; revenue first gives **$5.82, 25.02%**. Equal-order attribution is **$4.62, 19.89%**. | Label the bridge sequential, or use the order average. |
| F7 | major | §3 sensitivity | One revenue-growth point gives $1.5 through EBITDA | At the final multiple, fixed costs give **$3.44/share**; the implemented 0.364 growth-flex rule gives about **$2.62**. The separate multiple effect is **$4.27**, which matches. | Replace $1.5 and specify the cost assumption. |
| F8 | major | §3 simulation | Jessie’s multiple is independent of growth; corrected median validates target | Jessie uses a **0.5 Gaussian-copula correlation**; reproduced growth/multiple correlation is **0.497**. Updated median **$145.07** becomes **$158.50** with Street-centred growth. | Call it an updated conditional scenario simulation, not a correction proving the short. |
| F9 | major | 43c; §1 risk | The 2023 cut establishes that trimming marketing is cheap in nights | E-2023 fails, but one episode of **brand-spend phasing** cannot identify the effect of cutting 2026 emerging-market performance spend. Code mislabels the least-decelerating peer and excludes the third registered condition. | Preserve “no evidence in this episode”; remove the causal reassurance. |
| F10 | major | §1 risks | A trim leaves FY27 unchanged; deferred Q3 spending lands in Q4; AI caused the 16% saving | These are conditional assumptions. Management says AI contributed **“in part.”** FY27 unchanged is imposed by the one-quarter trim scenario, not established empirically. | Add “if temporary,” “could,” and “driven partly by AI.” |
| F11 | minor | §1 valuation/catalysts | Rounded numbers and dates | Street margin is **36.4497%**: direct one-decimal rounding is **36.4%**. FY25 incremental margin is **22.4759%**, better shown as **22.5%**, not 23%. Target **$143.59 ≈ $144**. $166.84 is the **21 September** anchor; February 11 is an **estimated** date in the source research. | Avoid double rounding; date the price and label the estimated catalyst. |

**Reproduction log**

Read-only inline Python used  
`& 'C:/Users/krish/AppData/Local/Python/pythoncore-3.14-64/python.exe' -B -X utf8 -`  
with pandas/numpy/scipy/statsmodels. No `run.py` was executed and I wrote no files. Expressions below abbreviate the executed inline calculations.

| Claim | Command/calculation | Matched? |
|---|---|---|
| S&M growth, shares, streak | Panel: `pct_change(4)`; annual/half-year sums; `sm_cash/revenue` | Growth/shares yes; streak **no: nine** |
| H2/H3/H5 tests | `OLS(...).fit(cov_type="HAC", cov_kwds={"maxlags":3,"use_correction":True})` | Reported pass/fail outcomes yes |
| M6 elasticity | WLS log cost growth on log revenue growth; four-quarter half-life; HAC(2) | **k=0.364173**, t=6.575 |
| Multiple slope | Filter eligible monthly rows; `.diff(12)`; OLS with rates/Nasdaq controls, HAC(12) | **0.486022**, stated CI, n=35 |
| Bridge and order reversal | `P=(EBITDA*multiple+9593)/597`; recalculate counterfactuals | Published bridge yes; attribution changes |
| Monte Carlo | Independent PERT/normal draws, seed 2026, n=20,000 | **$145.071**; saved draw sample maximum difference **1.8×10⁻¹²** |
| Quotes, catalysts, E-2023 | Normalised filing/transcript substring checks; ledger, consensus and peer CSV arithmetic | Quotes yes; interpretation issues above |

**1. Numbers, quotes and bases**

The principal historical arithmetic matches: cash S&M **21.13%/20.12%/29.88%** versus revenue **11.95%/10.26%/17.10%**; cash S&M shares **16.47% FY23, 19.41% FY25, 23.93% 1H26 versus 21.57% 1H25**. These are GAAP expenses less SBC, not cash-flow-statement expenditures.

Street EBITDA-cost growth **15.003%→10.042%**, incremental margin **43.710%**, and FY24 incremental margin **32.743%** reproduce. However, Street FY25–27 cost CAGR is **12.495%**, close to historical **12.614%**: the disagreement is whether the FY26 step repeats.

The cost-surprise counts **3/4 above after 16/18 below** match, although the latest “below” is only **$0.374M**. Official **$15.425bn revenue/$5.240bn EBITDA/33.97% margin** matches the cited model.

All three substantive management quotations and the November 2024 quotation with its ellipsis are supported verbatim. The fixed-headcount quotation concerns **some** 2025 investments carrying into **2026**; it does not establish FY27 persistence.

Catalyst arithmetic matches: segment Marketing **$506M/$600M**, growth **32.46%/28.21%**; November 2024 next-quarter EBITDA revision **−9.6%**, stock **−8.7%**; probabilities **22%/72%/49%**, conditionals **78%/30%**, and **$158.19M/2.744%** per margin point. These probabilities and the sandbag branch’s **+$3.5** are team-model outputs.

The **$63.70M/$176.71M** cuts refer to different revenue scenarios. The **$66M** commitment figure is correct **as of December 2025**, but does not establish that all remaining marketing is immediately cancellable. The support-saving scope—approximately a fifth of a $1.3bn line—is a calibrated model assumption. The five-November and four-of-ten records reproduce under their stated classifications.

**2. Valuation bridge and attribution**

Step (a) correctly computes:

\[
\Delta C=0.364173\times(-2.49447\%)\times \$10{,}053.24M=-\$91.33M.
\]

Thus EBITDA is **$5,462.82M**, price **$158.91**. The exact log-elasticity version gives **$158.93**: linearisation is immaterial.

M6 uses the same revenue-minus-adjusted-EBITDA cost basis, so there is no hidden GAAP/cash mismatch here. Nevertheless, its contemporaneous quarterly association is not an identified annual response to a forecast miss. Restricted-window estimates are **0.301/0.337**; W1’s interval includes zero. Use 0.364 as a scenario coefficient.

Revenue-first prices are:

**$166.84 → $158.91 → $156.52 → $153.09 → $143.59.**

Costs-first prices are:

**$166.84 → $163.41 → $153.09 → $143.59**, allocating **$3.43 costs, $10.32 revenue, $9.50 multiple**.

Step (c)’s **$131.17M** includes **$37.19M from the higher FY26 cost base**, plus **$93.98M from faster FY27 growth**. “Street growth means non-flex only” therefore remains inaccurate.

Earnings reductions and genuine forward-multiple compression are not automatically double-counting. Here, however, the slope was estimated on a **trailing** denominator, so an independent forward-multiple effect has not been demonstrated. The **$140.29–146.89** range varies only the slope; it is not a target-price confidence interval.

**3. Monte Carlo**

The implementation matches its stated PERT growth/cost inputs, normal elasticity/slope draws, growth-linked costs, and margin calculated as an output. The **8.7–15%** cost bounds apply before the growth adjustment.

| Alternative | Median | P5–P95 |
|---|---:|---:|
| Primary | $145.07 | $126.19–168.49 |
| Multiple noise, SD 1.5 turns | $145.30 | $116.54–177.13 |
| Street-centred growth | $158.50 | $136.20–179.59 |
| Literal DEC-0014 anchor | $149.61 | $130.10–173.31 |

The Street-centred variant also recentres the cost-flex reference. Holding that reference fixed gives **$156.59**—still materially higher.

Jessie’s **$175.73 median/68.0% upside** reproduces at $166.84. Updating obsolete inputs is fair; replacing it solely because the updated assumptions generate downside is not. Present the alternatives and avoid interpreting **93.58% below spot** as a calibrated trading probability.

**4. Pre-registration and test fairness**

43a’s **H2 PASS**, **H3/H5c PASS**, and **H5a FAIL** reproduce. H2 has **11/14, p=.0467** and **9/10, p=.000147**; contemporaneous W1 correlation is **.0434**. Neither passing growth tests nor overlapping trailing-four-quarter trends establishes rigidity or causal marketing efficiency.

E-2023’s exact deceleration is **−4.04pp ABNB**, versus **−14.5 Booking/−7.5 Expedia**: FAIL remains correct. But code uses `min` while describing the least-decelerating peer, and drops the stacked-growth condition. That stack is computable—**−31.04pp**—although pandemic-confounded, not mathematically undefined. E-2025/26 remains unsupported (**1/4 LatAm, 0/4 APAC**); omitted NA/EMEA checks cannot rescue its failure.

**5. First judge attack; best single change**

The first attack is: **“Why does historical S&M growth prove management cannot flex a budget when your revenue forecast misses?”**

Replace the thesis sentence with:

> “Our FY27 case assumes the spending step persists despite slower revenue, producing $5.24bn EBITDA versus $5.77bn consensus. Removing the model’s persistence additions raises EBITDA to $5.44bn; management’s ability to trim spending is the principal risk to this cost scenario.”