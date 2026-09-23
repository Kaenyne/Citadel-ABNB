# Income statement — the full rationale, line by line

22 September 2026. Sheet `Income_Statement` of `model/ABNB_official_model.xlsx`, rows 12–36, columns
1Q23A–4Q27E plus FY23–FY27. Builder `analysis/src/pitch_model_v2/income_statement.py`, called by
`adr_engine/workbook.py` on the live Workbook so the nights and ADR charts survive the save. Calculated copy:
`model/ABNB_official_model_complete.xlsx` (every formula evaluated, no Excel pass needed).

Filed under DEC-0026: every settled line gets a rationale file explaining why the number stands, the git data
and model behind it, and every alternative considered.

---

## 1. The instruction, and what it rules out

Theo: *"complete the income statement with the past margins, and bring the forecasted margins that we have
from the git. The take rate should be the same as the Street is modeling, then for the other 2 quarters you
can do a basic cyclical model."* Followed by: *"you should not be forecasting the cost lines, margins is
already done and ready to be plugged from git."*

So this line does three things and refuses a fourth:

1. **Plugs** the reported history.
2. **Plugs** the finished forecast cost lines and margins.
3. **Models** exactly one object, the take rate.
4. **Does not** forecast, re-key, re-fit or re-allocate any cost line. Nothing below revenue is a number
   invented here.

The margin is therefore never an assumption. It falls out of our own nights and ADR lines meeting cost
dollars that were built elsewhere.

---

## 2. Row by row: what each cell is and where it came from

`A` columns are 1Q23–2Q26, `E` columns 3Q26–4Q27. Blue = plug with a source, black = Excel formula.

| row | line | history (A) | forecast (E) |
|---|---|---|---|
| 12 | Revenue | plug, `revenue` | **formula** `= GBV × take rate` (DEC-0018) |
| 13 | y/y | formula | formula |
| 14 | Take rate | formula `= revenue ÷ GBV` | **plug**, the only modelled object (§4) |
| 16 | Cost of revenue (cash) | plug, `cor_cash` | plug, `cor_cash` |
| 17 | Operations & support (cash) | plug, `ops_cash` | plug, `ops_cash` |
| 18 | Product development (cash) | plug, `pd_cash` | plug, `pd_cash` |
| 19 | Sales & marketing (cash) | plug, `sm_cash` | plug, `sm_cash` |
| 20 | G&A (cash, ex lodging-tax) | plug, `ga_cash_ex_lodging` | plug, `ga_cash_ex_lodging` |
| 21 | Total cash costs | formula, `SUM(16:20)` | formula, `SUM(16:20)` |
| 22 | % of revenue | formula | formula |
| 23 | Depreciation & amortisation | plug, `da` | plug, `da` ($20.63M/q) |
| 24 | **Adjusted EBITDA** | plug, `adj_ebitda_reported` | **formula** `= 12 − 21 + 23 + 26` |
| 25 | **Adjusted EBITDA margin** | formula | **formula** — an output, not an input |
| 26 | Add-backs memo | plug, `other_addbacks_total − lodging_tax_reserves` | plug, `lodging_reserves` (0) |
| 27 | Stock-based compensation | plug, `sbc_total_is` | plug, `sbc` |
| 28 | Operating income (GAAP) | plug, `op_income` | **formula** `= 24 − 23 − 27` |
| 29 | Interest income | plug | plug |
| 30 | Interest expense | plug | plug ($37M/q) |
| 31 | Other income / (expense) | plug | plug ($3.70M/q) |
| 32 | Pre-tax income | plug, `pretax_income` | formula `= 28 + 29 − 30 + 31` |
| 33 | Income tax | plug, `tax_provision` | formula `= 32 × ETR` |
| 34 | Net income | plug | formula `= 32 − 33` |
| 35 | Diluted shares | plug | plug |
| 36 | Diluted EPS | plug | formula `= 34 ÷ 35` |

**Sources.** History: `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` (USD m, expenses
positive, GBV in $bn), built from SEC XBRL companyfacts, the 23 shareholder letters and the 10-Ks, with a
provenance row per cell in `02_panel_provenance.csv`. Forecast: `data/processed/margin_build/40_line_build/
40_lines_quarterly.csv`, scenario `base`, which DEC-0022 names as the cost path. Effective tax rate 18.0% FY26
and 17.5% FY27 from the M7 parameter sheet. Nights and ADR link to `Nights_Engine` and `ADR_Engine`.

**Why cash lines and not GAAP.** The cost rows are GAAP less that line's SBC, so SBC appears once, explicitly,
on row 27 between adjusted EBITDA and GAAP operating income. Airbnb allocates no SBC to cost of revenue, so
`cor_cash = cor_gaap`.

**Why G&A is carried ex lodging-tax reserves.** 4Q23 G&A is $1,203M because of the $931M Italian
lodging/withholding reserve, which the company adds back to adjusted EBITDA. Leaving it inside G&A would make
the cost line uninterpretable and the 4Q23 margin meaningless. It sits in the add-back memo on row 26 instead.
This is why row 21 differs from the panel's own `total_cash_costs` by exactly the reserve in every quarter,
which was verified quarter by quarter.

**Cost dollars are carried flat as revenue moves.** That is DEC-0022, a decision already on record, not a
choice made here. §8 prices what it costs.

---

## 3. The two identities, checked before a single formula was written

**Adjusted EBITDA** = revenue − (COR + OPS + PD + S&M + G&A ex-lodging) + D&A + add-backs ex-lodging.
Tested on all 14 historical quarters against reported adjusted EBITDA: **maximum gap 0.00**. It also holds
exactly in the forecast stack. Safe as a live formula on both halves.

**Operating income** = adjusted EBITDA − D&A − SBC. Holds exactly in the forecast (gap 0.0) but **fails on
history**, off by $928M in 4Q23 and by ±$55M elsewhere, because add-backs sit inside GAAP operating income but
outside adjusted EBITDA. So history plugs reported operating income and only the forecast uses the identity.

This asymmetry is the single most important construction decision in the sheet. Applying one rule to both
halves would have silently restated reported quarters.

**Documented gap.** 1Q24 interest expense was not separately disclosed; the FY24 10-K calls it immaterial and
it sits inside other income/(expense). Entered as 0 with that note, matching the panel's own flag.

**Fiscal-year columns.** Flow lines sum their four quarters. FY23–FY25 take the *reported* annual share count
and EPS rather than a mean of four quarterly counts, because the company weights shares across the year; the
mean route was off by $0.03 in FY23. FY26 and FY27 must be computed, since FY26 is half actual and half
forecast. FY revenue and margin tie to the reported annuals exactly.

---

## 4. The take rate — the only modelled object

### 4.1 Why it is modelled at all

Revenue is not plugged. DEC-0018 defines forecast revenue as nights × ADR × take rate, so that revenue
inherits our own alt-data lines. That makes the take rate the bridge, and it is the one number that has to
come from somewhere.

### 4.2 Street-implied, 3Q26 and 4Q26

| | Street revenue | Street nights | Street ADR | implied take rate |
|---|---|---|---|---|
| 3Q26 | $4,744.32M | 149.0m | $177.06 | **17.983%** |
| 4Q26 | $3,161.82M | 134.0m | $171.33 | **13.772%** |

Revenue from LSEG (`06_consensus_quarterly_2027.csv`, 13 Sep 2026 pull, n 37). Nights and ADR from the
Bloomberg MODL consensus of 12 Sep 2026, which DEC-0005 governs. Three independent routes agree within 4bp:
LSEG revenue over our arithmetic (17.983 / 13.772), LSEG revenue over MODL's own GBV (17.988 / 13.745), and
MODL's directly published take rate (18.00 / 13.76).

### 4.3 Why only two quarters, and what happens after

**The Street publishes no nights or ADR estimate beyond 4Q26, anywhere.** Not for 2027 quarters, not for FY26,
not for FY27. A Street-implied take rate is therefore literally uncomputable from 1Q27. This is what Theo's
"the other 2 quarters" refers to, and it is exactly where the Street coverage stops.

From 1Q27 the cyclical carry is the **seasonal naive τ[q−4]** with no drift imposed:

| quarter | take rate | carries |
|---|---|---|
| 1Q27 | 9.171% | 1Q26 reported |
| 2Q27 | 13.265% | 2Q26 reported |
| 3Q27 | 17.983% | 3Q26 Street-implied |
| 4Q27 | 13.772% | 4Q26 Street-implied |

### 4.4 Why the seasonal naive and not something fitted

Three independent reasons.

**The seasonality is strong, stable and mechanical.** Revenue is recognised at check-in while GBV is recorded
at booking, so Q1 books summer travel it does not yet earn. Three full years: Q1 9.2–9.4, Q2 13.0–13.3,
Q3 17.9–18.6, Q4 13.6–14.3.

**The repo already tested this and the naive won.** D7's verdict is that take rate is an output, not an input:
routing revenue through a fitted take-rate lever *adds* 1–2.5% of point-in-time error, and the seasonal naive
τ[q−4] beat every fitted take-rate object on both W1 and W2. Fitting one here would be re-running a test the
project has already failed.

**Management guides it flat.** The 2Q26 letter and call: the implied take rate will "remain relatively
in-line year-over-year" for 3Q26, and for FY26 "relatively flat compared to 2025". Zero drift is the guided
assumption, not a convenient one. Observed y/y drift over the last four quarters is +10, +15, −10 and +9bp,
so zero sits inside the noise.

A ratio-to-moving-average decomposition was built and unit-tested as a cross-check (it recovers known seasonal
factors to within 0.02%), but it is not used: it adds a level-drift assumption the guidance does not support,
and D7's finding argues against it.

### 4.5 Alternatives rejected

Street revenue ÷ our GBV, which is computable to 4Q27 since Street revenue runs that far, was rejected because
it silently forces our revenue back onto consensus and destroys the whole point of building lines 1 and 2.
D7's own base take-rate path was rejected because it is a fitted object D7 itself refuted. Any level drift was
rejected as unsupported by the guidance.

---

## 5. Source conflicts found, and how each was resolved

Three surveys of the repo turned up several files that disagree on the same reported number. Each was resolved
in favour of `02_panel_quarterly.csv`, which reads the shareholder letters' reconciliation tables directly and
carries a provenance row per cell.

| conflict | competing values | resolution |
|---|---|---|
| **Q4 total SBC** | panel 4Q23 **290** / 4Q24 **368** / 4Q25 **411**; six other files 270 / 400 / 400 | Panel. The others derived Q4 as FY-less-9M from a proxy figure rounded to $100M. Corroborated by the letter series. Their by-function rows are right, so cash cost lines are unaffected. |
| **Tax provision sign** | panel positive for an expense; two other files negative | Panel. Same magnitude, opposite convention; mixing them would flip net income. |
| **Interest expense 1Q24–4Q25** | one file carries 0 and buries it in other income | Panel. The 2Q26 letter re-presents 2Q24 onward. |
| **4Q23 diluted shares** | panel **640**; three other files 653 | Panel. 4Q23 was a net loss, so diluted equals basic, and 640 × −0.55 reproduces the reported EPS. |
| **3Q26 Street nights** | 149.0 (MODL, n 28) vs 148.9 (earlier Bloomberg FA capture) | 149.0, per DEC-0005. |
| **4Q26 Street revenue** | LSEG 3,161.82 / MODL 3,157 / Zacks 3,200 (flagged outlier) / a synthetic 3,177 midpoint in one file | LSEG, n 37. The synthetic midpoint is not any vendor's number. |

---

## 6. What the line says

### 6.1 The past margins

Adjusted EBITDA margin, reported, as the sheet now carries it:

| | Q1 | Q2 | Q3 | Q4 | FY |
|---|---|---|---|---|---|
| 2023 | 14.41% | 32.97% | 53.99% | 33.27% | **36.84%** |
| 2024 | 19.79% | 32.53% | 52.47% | 30.85% | **36.40%** |
| 2025 | 18.35% | 33.69% | 50.09% | 28.29% | **35.10%** |
| 2026 | 19.38% | 34.95% | — | — | — |

The shape that matters for the pitch: the Q3 peak has fallen three years running, 53.99 → 52.47 → 50.09, and
Q4 with it, 33.27 → 30.85 → 28.29. FY margin has compressed 174bp over two years despite revenue growth.

### 6.2 The forecast

| | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| Revenue $m | 4,691 | 3,141 | 2,955 | 3,926 | 5,118 | 3,426 |
| vs Street | −1.1% | −0.7% | −1.8% | −2.8% | −2.9% | −2.9% |
| Adj. EBITDA $m | 2,307 | 862 | 458 | 1,270 | 2,581 | 931 |
| vs Street | −2.3% | −5.7% | −25.0% | −12.5% | −4.2% | −12.9% |
| Adj. EBITDA margin | 49.17% | 27.43% | 15.50% | 32.36% | 50.43% | 27.17% |
| Diluted EPS $ | 2.75 | 0.71 | 0.17 | 1.24 | 3.19 | 0.76 |

FY26 revenue $14,118M, adjusted EBITDA $4,948M, margin **35.05%**, EPS $5.07.
FY27 $15,425M, $5,240M, **33.97%**, EPS $5.35, against a Street FY27 margin of 36.45%. FY27 revenue embeds 4Q27 ADR
at a spot-held FX of exactly zero, an artefact of holding spot on both 4Q27 and its base quarter (ADR line §2.8);
each 1pp of 4Q27 FX is about $0.40 of FY27 ADR (labelled 23 Sep).

---

## 7. Verification log

- Adjusted EBITDA identity: max gap **0.00** on 14 of 14 historical quarters.
- Revenue, adjusted EBITDA, net income, EPS and margin: tie to the panel on **14 of 14** quarters.
- Row 21 versus the panel's `total_cash_costs`: difference equals the lodging reserve in **every** quarter.
- FY23–FY25 revenue, margin and EPS: tie to the reported annuals exactly.
- Workbook: **0** blank formula cells, **0** error cells, all six charts intact, 27 engine tests pass.

---

## 8. What a lodging analyst attacks, and the honest answer

**"Your EBITDA gap is ten times your revenue gap."** It is, and it is arithmetic, not a second claim. Revenue
runs 1–3% below consensus because our nights and ADR lines do. Cost dollars are then carried flat per
DEC-0022, so the entire shortfall drops to EBITDA. On a thin seasonal base the percentage looks violent:
1Q27 revenue is 1.8% light but EBITDA is 25% light, because the Q1 margin base is only about 20%.

**"Carrying costs flat is itself an assumption."** Correct, and it is unresolved in the repo, not settled
here. C4 asks whether management's 3Q26 margin sentence is a binding budget, in which case costs flex with
revenue, or a floor, in which case they do not. If costs flexed to hold the line build's own margin at our
revenue, EBITDA would be higher by $56M in 3Q26, $27M in 4Q26 and $68–80M per quarter through 2027. Those are
memo rows 43–44 on the sheet. No side is taken.

**"Your FY26 margin breaks the company's own guidance."** It does: 35.05% against a guided floor of at least
35.5%, a 45bp miss. It is an output of DEC-0016 arithmetic, not an input chosen to embarrass the guide, and it
should be presented that way. The cost-flex memo closes most of it, which is precisely why the flex question
has to be named out loud rather than buried in a footnote.

**"1Q27 GAAP operating income is negative."** −$27M, against +$86M reported in 1Q26. Q1 is the seasonally
weak quarter and SBC of $464M exceeds a $458M EBITDA. It is a consequence of the plugged SBC schedule meeting
our lower revenue, not a separate forecast.

---

## 9. What this line does not settle

**DEC-0023, the hosting step, stays open.** The plugged figure is $100.21M a quarter in 2026 and $111.71M in
2027; B08's independent Monte Carlo puts it at $85.0M. Memo row 45 carries the difference, $15M a quarter in
2026 and $27M in 2027, as EBITDA that returns if B08 is right. The 4Q26 cost-of-revenue print against $575M
resolves it.

Only the `base` scenario is carried, per DEC-0020. The calibrated combination's $2,399M 3Q26 object is **not**
used as an input; it remains a 5 November card reference under DEC-0022. No kill-listed number from
`ABNB_margin_model.xlsx` appears anywhere in this sheet. The cost stack was built on a revenue path whose ADR
differs from DEC-0035's by 0.2–1.2% a quarter; since PD, S&M and G&A are intended to carry unchanged and COR
and OPS key off GBV, which differs by only +0.2% in 3Q26, the dollars are plugged as filed rather than
re-keyed, and this paragraph is the disclosure.

---

## 10. Proposed decision (pending Theo)

**DEC-0042.** The income statement's history is the reconciled financial panel, plugged as reported. Its
forecast cost lines, SBC, D&A and below-the-line items are the 40_line_build base, carried in dollars per
DEC-0022. Revenue is nights × ADR × take rate, with the take rate Street-implied for 3Q26–4Q26 and seasonal
naive τ[q−4] thereafter. Adjusted EBITDA and the margin are outputs.

Rejected: forecasting the cost lines (they are built; plug them); flexing costs to hold the budget margin
(C4 unresolved, carried as a memo); using the calibrated combination's allocated lines (DEC-0022 names the
line build); fitting a take-rate model (D7 refuted it); Street revenue ÷ our GBV for 2027 (forces revenue back
onto consensus).
