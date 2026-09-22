# Income statement — why the numbers in rows 12–36 stand

22 September 2026. Builder `analysis/src/pitch_model_v2/income_statement.py`, called by
`adr_engine/workbook.py` on the live Workbook so the nights and ADR charts survive. Sheet
`Income_Statement` of `model/ABNB_official_model.xlsx`; the calculated copy is
`model/ABNB_official_model_complete.xlsx`.

## 1. What is plugged, what is a formula, what is modelled

Theo's instruction: **do not forecast the cost lines or the margins — they are already built, plug them.**
That is what this line does. Nothing below revenue is a number invented here.

| block | treatment | source |
|---|---|---|
| History 1Q23–2Q26, every reported line | **plugged** (reported is reported, never reconstructed) | `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` |
| Forecast cost lines, SBC, D&A, interest, other income, diluted shares | **plugged in dollars** | `data/processed/margin_build/40_line_build/40_lines_quarterly.csv`, scenario `base` |
| Effective tax rate 18.0% FY26 / 17.5% FY27 | **plugged parameter**, applied to our own pre-tax | M7 parameter sheet, reproduced in both builds |
| Nights, ADR, GBV | **linked** to lines 1 and 2 | `Nights_Engine`, `ADR_Engine` |
| Revenue, total costs, adjusted EBITDA, margin, operating income, pre-tax, tax, net income, EPS, all ratios and y/y, all FY columns | **Excel formulas** | — |
| Take rate | **the only modelled object** | §3 |

Cost dollars are carried unchanged as revenue changes, per DEC-0022. That is a decision on record, not a
choice made here, and §5 prices what it costs.

## 2. The two identities, verified before any formula was written

**Adjusted EBITDA** = revenue − (COR + OPS + PD + S&M + G&A ex-lodging) + D&A + add-backs ex-lodging.
Checked on all 14 historical quarters: **maximum gap 0.00** against reported adjusted EBITDA. G&A is carried
ex lodging/withholding-tax reserves, so the reserve is netted out of the add-back row rather than counted
twice; this is why row 21 differs from the panel's own `total_cash_costs` by exactly the reserve in every
quarter (4Q23 by $931M, the Italian reserve). Verified quarter by quarter.

**Operating income** = adjusted EBITDA − D&A − SBC holds exactly in the forecast (gap 0.0 in the line build)
but **not** in history, where add-backs sit inside GAAP operating income (4Q23 off by $928M). So history
plugs reported operating income and the forecast uses the identity. History is actuals; the forecast is live.

One documented gap: 1Q24 interest expense was not separately disclosed and sits inside other income/(expense).
It is entered as 0 with that note, matching the panel's own flag.

## 3. The take rate — the only thing modelled here, and why it is done this way

Theo: Street where the Street models it, a basic cyclical model elsewhere.

- **3Q26 17.983%, 4Q26 13.772%** — Street-implied per DEC-0018, Street revenue ÷ (Street nights × Street ADR),
  on the DEC-0005 governing numbers. Three independent routes (LSEG revenue ÷ our arithmetic, ÷ MODL GBV, and
  MODL's own published take rate) agree within 4bp.
- **1Q27 onward** — the Street publishes **no** nights or ADR estimate beyond 4Q26, anywhere, so a
  Street-implied take rate cannot be computed. The cyclical carry is the **seasonal naive τ[q−4]**: 1Q27 takes
  1Q26 actual (9.171%), 2Q27 takes 2Q26 actual (13.265%), 3Q27 and 4Q27 take the 3Q26/4Q26 Street-implied
  values. No level drift is imposed.

Three reasons this is the right cyclical model rather than a fitted one. The seasonal shape is strong and
stable (Q1 ≈ 9.2–9.4, Q2 ≈ 13.0–13.3, Q3 ≈ 17.9–18.6, Q4 ≈ 13.6–14.3). D7 already tested this line and found
**the seasonal naive τ[q−4] beats every fitted take-rate object on both windows**, with take rate best treated
as an output. And management guided the take rate "relatively in-line year-over-year" for 3Q26 and
"relatively flat" for FY26, which is precisely a zero-drift seasonal carry. Observed y/y drift over the last
four quarters is +10, +15, −10 and +9bp, so zero is inside the noise.

## 4. What the line says

Revenue is an output of our own nights × ADR × take rate, so the margin is an output too, never an assumption.

| | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| Revenue $m | 4,691 | 3,141 | 2,955 | 3,926 | 5,118 | 3,426 |
| vs Street | −1.1% | −0.7% | −1.8% | −2.8% | −2.9% | −2.9% |
| Adj. EBITDA $m | 2,307 | 862 | 458 | 1,270 | 2,581 | 931 |
| vs Street | −2.3% | −5.7% | −25.0% | −12.5% | −4.2% | −12.9% |
| Adj. EBITDA margin | 49.17% | 27.43% | 15.50% | 32.36% | 50.43% | 27.17% |
| Diluted EPS $ | 2.75 | 0.71 | 0.17 | 1.24 | 3.19 | 0.76 |

FY26 revenue $14,118M, adjusted EBITDA $4,948M, margin **35.05%**, EPS $5.07. FY27 $15,425M, $5,240M,
**33.97%**, EPS $5.35.

## 5. What a lodging analyst will attack, and the honest answer

**The EBITDA gap to the Street is far wider than the revenue gap.** That is arithmetic, not a second claim.
Revenue runs 1–3% below consensus because our nights and ADR lines do; cost dollars are then carried flat
per DEC-0022, so the entire shortfall drops to EBITDA. On a thin seasonal base the percentage looks dramatic:
1Q27 revenue is 1.8% light but EBITDA is 25% light, because the 1Q margin base is only ~20%.

**Carrying cost dollars flat is an unresolved choice, not a finding.** C4 asks whether management's 3Q26
margin sentence is a binding budget (costs flex with revenue) or a floor (costs are fixed). If costs flexed to
hold the line build's own margin at our revenue, EBITDA would be higher by $56M in 3Q26, $27M in 4Q26 and
$68–80M per quarter through 2027. Those memo rows are on the sheet at rows 43–44. We are not choosing a side.

**FY26 margin of 35.05% sits below management's guided floor of "at least 35.5%".** It is an output of
DEC-0016 arithmetic, not an input picked to embarrass the guide, and it should be presented as such: on our
volumes, with costs at budget, the FY26 floor is missed by 45bp. The cost-flex memo closes most of that gap,
which is exactly why the flex question has to be named rather than buried.

**DEC-0023 is still open.** The plugged hosting step is $100.21M a quarter in 2026 and $111.71M in 2027; B08's
independent Monte Carlo says $85.0M. Row 45 carries the difference, $15M a quarter in 2026 and $27M in 2027,
as EBITDA that comes back if B08 is right. Both sides stay on record; the 4Q26 cost-of-revenue print against
$575M resolves it.

## 6. What this line does not do

No cost line is forecast or re-keyed here. Only the `base` scenario is carried, per DEC-0020. The calibrated
combination's $2,399M 3Q26 object is not used as a cost input; it remains a 5 November card reference. The
kill-listed numbers in `ABNB_margin_model.xlsx` are not quoted anywhere in this sheet. The cost stack was
built on a revenue path whose ADR differs from DEC-0035's by 0.2–1.2% per quarter; since PD, S&M and G&A are
intended to carry unchanged and COR/OPS key off GBV, which differs by only +0.2% in 3Q26, the dollars are
plugged as filed rather than re-keyed, and this paragraph is the disclosure.

## 7. Proposed decision (pending Theo)

DEC-0042: the income statement's history is the reconciled financial panel and its forecast cost lines,
SBC, D&A and below-the-line items are the 40_line_build base, carried in dollars; revenue is nights × ADR ×
take rate with the take rate Street-implied for 3Q26–4Q26 and seasonal naive τ[q−4] thereafter; adjusted
EBITDA and the margin are outputs. Alternatives rejected: modelling the cost lines (Theo: they are built,
plug them); flexing costs to hold the budget margin (C4 unresolved, carried as a memo); using the calibrated
combination's allocated lines instead of the line build (DEC-0022 names the line build).
