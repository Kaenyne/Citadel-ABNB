# 31b. The operating profile: deriving each cost line from the revenue drivers

- **Workstream:** 31, part B. **Date:** 2026-09-08. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Question:** can each cash cost line be written as a function of the revenue drivers (nights, ADR ex-FX, FX, take rate, regional and size mix) using Airbnb's own history, so that a forward margin is an implication of the operating profile rather than an assertion?
- **Script:** `analysis/src/overnight/31b_operating_profile.py` (`py -3.13`; rebuilds every output).
- **Data written:** `data/processed/overnight/31b_line_elasticities.csv`, `31b_margin_decomposition_annual.csv`, `31b_overlay_parameters.csv`, `31b_forward_margin_by_profile.csv`, `31b_margin_bridge_fy26_fy28.csv`, `31b_sensitivities.csv`.
- **Figures:** `analysis/figures/overnight/31b_line_elasticities.png`, `31b_margin_decomposition_annual.png`, `31b_forward_profiles.png`, `31b_sensitivities.png`.
- **Builds on, does not replace:** `research/notes/2026-09-05_margin-drivers.md` (sections 3, 10, 11, 14), `research/notes/overnight/07_ops-and-margin-levers.md`, `research/notes/overnight/30_margin-walk.md`, `research/notes/2026-09-07_adr-decomposition.md`. Disagreements are in section 8.
- **Inputs:** `07_cost_lines_per_night.csv` and `07_cost_components_annual.csv` (quarterly cash stack 1Q21-2Q26, disclosed components FY2019-25), `abnb_quarterly_cost_stack_exsbc.csv` and `abnb_margin_bridge.csv`, `02_kpi_panel_quarterly.csv`, `10_regional_panel_quarterly.csv` and `10_regional_forecast.csv`, `data/processed/adr/07_full_decomposition.csv`, the workstream-29 revenue bridge (`29_q4_2026_bridge.csv`, `29_fy27_quarterly_path.csv`, `29_fx_refresh.csv`), `30_quarterly_pnl.csv` and `30_fy_summary.csv`, `07_margin_levers_fy26_fy28.csv`, **`31a_mgmt_implied_profile.csv` (part A)**, and SEC XBRL company facts for FY2019-FY2020.

---

## 1. Bottom line

1. **Only one cost line has a driver relationship tight enough to forecast with.** Cost of revenue is proportional to GBV: elasticity **1.01** (t 3.3, R² 0.48), leave-one-year-out range **0.96 to 1.11**, and a levels-regression intercept share of **0.7%** — no fixed component at all. Every other line fails: operations and support to nights is 1.39 with a LOO range of 0.41 to 1.66; product development to revenue is **negative** (−0.69); field operations to revenue is −2.25; G&A to revenue has an R² of 0.06. Five of Airbnb's six cash cost lines are not driven by volume in any measurable sense. **They are decisions, and any margin model that dresses them as elasticities is decorating a judgement.**

2. **The right unit basis for each line, and what history says it does on that basis** (1Q23-2Q26, year-on-year log differences; `31b_line_elasticities.csv`): cost of revenue **−1.3% a year per $ of GBV**; operations and support **−2.5% a year per night**; product development **+11.3% a year**; brand and performance marketing **+16.5%**; field operations and policy **+24.3%**; G&A **+9.6%**. Those six numbers, applied to the workstream-29 driver path with no overlays at all, are the "historical" profile in section 6.

3. **Operations and support does not get cheaper because of scale.** The leverage story in the existing notes — a semi-fixed line whose cost per night falls as nights grow — is not what the data shows. The fitted elasticity to nights is above one, the levels intercept share is 19%, and the per-night decline is a **trend**, not a volume effect. G&A is the only genuinely fixed-heavy line (intercept share **61%**), and product development is next (**32%**). That matters for the bear case: in a slow-nights year the lines that would cushion the margin are G&A and product development, not support.

4. **What built the ~4,000bp from 2019 to 2022 was overwhelmingly revenue per night, not cost work.** Of +39.8 points, **+30.0 came from revenue per night** (+26.2 ADR, +3.8 take rate) and only +9.8 from the cost side, of which brand and performance marketing was +5.9 and field operations +3.4. Operations and support contributed **nothing** (−0.0). Caveat: 2019 GBV and "nights and experiences booked" include Experiences seats, so the 2019 ADR of $116 is understated and the ADR term flattered. The split between "ADR windfall" and "cost reset" is roughly three to one.

5. **Since 2022 the margin has gone nowhere (+0.5 points to FY2025) and the composition is now measurable.** Revenue per night added **+5.1 points**, and splitting ADR with the ADR decomposition rather than treating "ADR ex-FX" as one line: **unit-size mix and like-for-like price +5.4, regional mix −2.5, FX +1.1, length of stay +0.5, take rate +0.7**. Against that, scale leverage on the semi-fixed lines added **+3.5** (G&A +1.7, product development +1.1, support +0.6), cost of revenue's ADR pass-through cost **−1.2**, and per-unit cost decisions cost **−7.2**, of which **marketing was −4.2** (brand −1.8, field −2.4), product development −1.5 and G&A −2.2. The ADR windfall was real, a third of it was eaten by regional mix before it reached revenue, and all of what survived went to marketing and headcount.

6. **AI has moved exactly one line, by about a tenth of what the equity story implies, and it has already begun to cost more than it saves on another.** 1H26 against 1H25, per unit: operations and support **−3.8% per night**, cost of revenue −1.6% per $100 of GBV, product development **+2.1% per night**, G&A −11.8%, brand marketing +20.5%, field operations +13.3%. The support saving is worth about **+0.4 points of margin a year**. Meanwhile the data-hosting commitment went from "at least $672m through 2027" to "at least **$1.7bn through 2031**" and purchase obligations $719m to $1,749m — a cost visible in Note 13 four to eight quarters before it reaches cost of revenue, and the reason the base takes cost of revenue per $ of GBV **up** 1% a year rather than 07's flat.

7. **A pure-history extrapolation gives FY2028 at 34.6%; the management-implied profile gives 37.4%; the 07 lever model says 37.5% and the 30 walk says FY27 36.4%. My base is 36.9% (FY26 35.3%, FY27 35.9%).** The 2.8-point gap between history and management is almost entirely **field operations and G&A**: history compounds them at +24.3% and +9.6% a year, management decelerates them to +12% and +5%. Brand marketing is *not* the gap — management actually spends more on brand in FY26 than history would (+25% against +16.5%) and the cumulative three-year totals are within $100m. **The forward margin case rests on the deceleration of two lines that have never decelerated.**

8. **And "management-implied" is only a management view for FY2026.** Part A (`31a_mgmt_implied_profile.csv`) scores management's confidence line by line: for FY2026 it is high on cost of revenue, support, brand marketing and G&A and medium on product development and field operations; for FY2027 it is low on four of the six; **for FY2028 management is explicitly silent on five of the six lines**, and the sixth (G&A) is a long-term tax remark that sits below Adjusted EBITDA. So the 37.4% FY2028 in this note is the house lever set carried forward under a management label, not something Airbnb has said. Any FY2028 margin — mine included — is a house view.

9. **The five things the answer turns on, in order** (FY2028E margin points, base profile; shock in FY2028 alone): support cost per night −10% **+0.84**; brand marketing growth +5pt **−0.66**; take rate +10bp **+0.47**; ADR ex-FX +1pt **+0.42** (FX +1pt the same); nights +1pt **+0.34**; a point of nights share moving from North America into LatAm and APAC **−0.33**. Two of those are estimation risk rather than business risk: putting the support-to-nights elasticity at its leave-one-year-out bounds moves FY2028 margin by **+1.14 / −1.50 points**, which is larger than every business shock in the list except the support target itself.

---

## 2. Method

The cash (ex-SBC) stack from workstream 07 runs 1Q21 to 2Q26, with the brand-and-performance versus field-operations split available from 1Q22. Field operations is GAAP field operations less **all** S&M stock compensation (the workstream-07 convention: no SBC inside brand and performance). The identity `revenue − cash costs − restructuring + D&A + other add-backs = Adjusted EBITDA` is asserted quarter by quarter and holds to a maximum of **$1.70m** (4Q22); the script fails if it exceeds $5m. FY2019 and FY2020 are added from XBRL company facts, with operations and support backed out of `CostsAndExpenses` and SBC allocated across functions on the FY2021 functional split.

**Estimation.** The primary specification is a year-on-year log difference, `dlog4(cost) = g + b·dlog4(driver)`, on 1Q23-2Q26 (n=14): seasonality cancels, the intercept `g` *is* the per-unit trend, and the form is identical to the one the forward model projects with. A levels specification with seasonal dummies and a trend is reported alongside but is **not identified** — log(revenue), log(GBV) and log(nights) each correlate 0.63 to 0.81 with the time trend on 18 quarters (interpolated headcount, 0.98) — and it produces absurdities such as a −2.77 elasticity for field operations with a +60% annual trend. Those columns (`elasticity_levels_spec`, `corr_logdriver_trend`) are a warning, not a result. 2021 is excluded and reported descriptively: nights grew 56% off a collapsed base. Headcount is disclosed only at 31 December, so it is linearly interpolated and flagged; every headcount regression fails on identification, not data quality.

**Promotion rule.** `promote = True` requires n ≥ 12, |t| > 2, a leave-one-year-out range under 0.6 and an economically admissible sign. Exactly one line-driver pair passes: cost of revenue on GBV.

**Restricted specifications.** Because five lines are not identified, the forward model imposes the elasticity and estimates only the per-unit trend: cost of revenue 1.0 on GBV, operations and support 1.0 on nights, the other four 0.0 (own growth rate). The unrestricted estimate and its LOO range sit in the same rows so the imposition is visible, and both imposed elasticities are stress-tested at their LOO bounds in `31b_sensitivities.csv`.

**Fixed/variable split.** From a separate levels regression, `cost = a + b·driver + Q2 + Q3 + Q4` on 1Q22-2Q26, the intercept as a share of the mean cost. Negative values (brand −2%, field −60%) mean the line grew faster than its driver over the window and are reported raw, then clamped to zero where used.

---

## 3. What is variable, what is semi-fixed, what is a decision

`31b_line_elasticities.csv`, figure `31b_line_elasticities.png`. Primary specification, 1Q23-2Q26, n = 14.

| Line | Natural driver | Elasticity | t | LOO range | R² | Intercept share | Per-unit trend | Usable? |
|---|---|---|---|---|---|---|---|---|
| Cost of revenue | GBV | **+1.01** | +3.3 | 0.96 to 1.11 | 0.48 | 0.7% | −1.3% / yr per $ GBV | **yes** |
| Operations and support | Nights | +1.39 | +2.0 | 0.41 to 1.66 | 0.25 | 19% | −2.5% / yr per night | no |
| Product development | Revenue | −0.69 | −2.1 | −0.85 to −0.54 | 0.26 | 32% | +11.3% / yr | no (sign) |
| Brand and performance marketing | Revenue | +1.19 | +1.6 | 0.42 to 1.89 | 0.18 | −2% | +16.5% / yr | no |
| Field operations and policy | Revenue | −2.25 | −1.9 | −2.44 to −1.86 | 0.23 | −60% | +24.3% / yr | no (sign) |
| General and administrative | Revenue | +4.59 | +0.9 | 0.96 to 9.20 | 0.06 | 61% | +9.6% / yr | no |

Reading it:

- **Structurally variable: cost of revenue only.** Merchant fees and chargebacks have run 1.82-1.89% of GBV since 2022 and the regression confirms strict proportionality with no fixed base. This is why a take-rate change flows almost entirely to margin and an ADR change does not: cost of revenue rises with ADR, so on a *per-night* basis it looks like a leak ($3.81 in 2022 to $3.91 in 2025 to $3.99 in 1H26) when the unit economics have not changed.
- **Semi-fixed, but not for the reason usually given: operations and support.** The per-night cost has fallen every year since 2023 ($2.49 to $2.32 to $2.05 in 1H26), but the regression cannot attribute that to scale. The elasticity to nights is above one and its LOO range spans 0.41 to 1.66; the 19% intercept share says roughly a fifth of the line is fixed. **The decline is a productivity trend, not operating leverage.** That is a materially different forecast object: leverage arrives automatically with volume, a trend has to keep being delivered.
- **Headcount-driven: product development and G&A.** Neither has a usable revenue elasticity, both carry the highest intercept shares (32% and 61%), and product development's disclosed driver is payroll ("1H26 +11%, entirely payroll on higher average headcount"). Modelling either as a percent of revenue is a category error.
- **Discretionary: brand and performance marketing, field operations and policy.** Both grew far faster than revenue over the window, which is why their fitted elasticities are meaningless. Notably, the intercept share for brand marketing is **−2%**: on this window there is **no measurable fixed component** in brand spend, despite Mertz's "effectively a fixed amount of spend for each market" framing. The fixed-per-market model cannot be estimated at all, because Airbnb has never published a count of expansion markets — only that origin nights in them have grown at about twice core for ten consecutive quarters. That gap is recorded as an explicit parameter row in `31b_overlay_parameters.csv` for part A to fill if a count exists.

---

## 4. What AI has actually done to cost per unit, line by line

Per-unit, 1H2026 against 1H2025 (`31b_margin_decomposition_annual.csv` and the panel behind it):

| Line | Basis | 1H25 | 1H26 | Change |
|---|---|---|---|---|
| Cost of revenue | per $100 of GBV | $2.188 | $2.152 | **−1.6%** |
| Operations and support | per night | $2.130 | $2.049 | **−3.8%** |
| Product development | per night | $2.41 | $2.46 | +2.1% |
| Brand and performance marketing | per night | $2.97 | $3.58 | +20.5% |
| Field operations and policy | per night | $1.20 | $1.36 | +13.3% |
| G&A | per night | $1.69 | $1.49 | −11.8% |
| Revenue per night | | $19.34 | $20.64 | +6.7% |

- **Customer support is the only line AI has moved, and it moved 3.8%.** Management discloses support cost per *booking* −10% (1Q26) and −16% (2Q26), AI resolving about 45% of contacts in 50+ languages, and third-party service-provider cost −$17m in 2Q26. At the line level that nets to −3.8% per night, because payroll (+$41m), customer relations (+$14m) and insurance (+$9m) absorbed most of it. In the decomposition it is worth **+0.4 points of margin** — real, and roughly a tenth of what the marketing ramp took over the same period (−3.2 points from brand alone).
- **Engineering productivity: no evidence.** Product development cash per night is *up* 2.1%; headcount rose 12.3% in 2025 while revenue per employee fell 1.8%, the first fall on record. Part A reaches the same conclusion from the statements: Chesky's +30% engineering-productivity claim (1Q23, restated 4Q24) "has never shown up as leverage on this line".
- **G&A −11.8% is not AI.** 1H26 G&A benefits from non-income taxes −$38m while underlying payroll grew. It is the line most likely to revert, which is why the base takes G&A growth to +3% in FY26 rather than 07's +2%.
- **AI is already a cost on cost of revenue and the P&L has not felt it yet.** Server costs +$15m in 1H26 on reserved-instance amortisation; purchase obligations $719m (Dec-24) to **$1,749m** (Dec-25); the data-hosting commitment from at least $672m through 2027 to at least **$1.7bn through 2031**, roughly $280m a year against about $220m. Chesky said in February 2026 that "our investment in AI will not affect the P&L"; Mertz said in August 2026 that the guide "does assume a material increase in terms of the AI spend". The commitments note is with Mertz. That is why the base takes cost of revenue per $ of GBV to **+1.0% a year** rather than continuing the historical −1.3%.

---

## 5. What built the margin, and what has moved it since

`31b_margin_decomposition_annual.csv`, figure `31b_margin_decomposition_annual.png`. Method extends `abnb_margin_bridge.csv`: each line's share of revenue is cost per night over revenue per night; the change splits into a unit-cost effect (cost per night moved, revenue per night held) and a revenue-per-night effect (denominator moved). Two things are added here. The revenue-per-night effect is split not just into take rate, FX and "ADR ex-FX" but into the full workstream-31a ADR decomposition — **regional mix, unit-size mix, length of stay and measured like-for-like price** — wherever that decomposition exists (FY2022 onward). And the unit-cost effect is split into a **nights-leverage** term, sized by the line's estimated fixed share, and a **residual per-unit cost change**, so the reader can see how much of a per-unit move was scale and how much was a decision.

The FY2022→FY2025 and FY2024→FY2025 totals reproduce `abnb_margin_bridge.csv` exactly (+0.5 and −1.3 points), as does the S&M total of −4.2.

**FY2019 → FY2022, +39.8 points.**

| Component | Margin points |
|---|---|
| Revenue per night: ADR | **+26.2** |
| Revenue per night: take rate | +3.8 |
| Brand and performance marketing, per-unit | +5.9 |
| Field operations and policy, per-unit | +3.4 |
| Product development (nights leverage +1.1, per-unit +1.5) | +2.6 |
| G&A (nights leverage +1.5, per-unit −0.3) | +1.2 |
| Operations and support | −0.0 |
| Cost of revenue (ADR pass-through −8.3, per-unit +7.2) | −1.0 |
| D&A, restructuring and add-backs | −2.2 |
| **Total** | **+39.8** (−5.3% to 34.6%) |

Three-quarters of the 4,000bp was revenue per night. The cost reset was real and it was **marketing**: brand and performance fell from $1,140m (2019) to $1,030m (2022) on 20% more nights, and field operations from $481m to $486m. Operations and support contributed nothing at all — the line most associated with the "efficiency" story did not move per unit between 2019 and 2022. Caveat: FY2019 GBV and "nights and experiences booked" include Experiences seats, so the 2019 ADR ($116) is understated and the ADR term is somewhat flattered at the expense of the take-rate term; the cost-side terms are unaffected.

**FY2022 → FY2025, +0.5 points.**

| Component | Margin points |
|---|---|
| ADR: unit-size mix and like-for-like price (not separated before 2024) | **+5.4** |
| ADR: regional mix | **−2.5** |
| ADR: FX | +1.1 |
| ADR: length of stay | +0.5 |
| ADR: interaction | −0.2 |
| Take rate | +0.7 |
| *Revenue per night, total* | *+5.1* |
| Nights leverage across the semi-fixed lines (G&A +1.7, product dev +1.1, support +0.6, cost of revenue +0.0) | **+3.5** |
| Cost of revenue: ADR pass-through | −1.2 |
| Per-unit cost decisions: brand −1.8, field ops −2.4, G&A −2.2, product dev −1.5, support +0.1, cost of revenue +0.6 | **−7.2** |
| Add-backs | +0.3 |
| **Total** | **+0.5** (34.6% to 35.1%) |

**How much of 2022-2025 was ADR windfall, cost work and marketing give-back?** The windfall gross was +5.4 points of size mix and pricing, but **regional mix took 2.5 of them back before they reached revenue**, leaving about +3.3 from ADR ex-FX, plus +1.1 FX and +0.7 take rate. Cost work — scale leverage on the semi-fixed lines plus the cost-of-revenue per-unit gain — was worth **+4.1 points**. Both were spent: marketing gave back **−4.2**, product development and G&A per-unit gave back another **−3.7**, and cost of revenue's ADR pass-through took **−1.2**. The residual is the +0.5 that shows up in the reported margin.

**1H2025 → 1H2026, +1.1 points.** Revenue per night +4.9 (FX +2.4, ADR ex-FX +2.7, take rate −0.3), support +0.4, G&A +1.0, against brand marketing **−3.2**, cost of revenue −1.1 and field operations −0.8. The 2026 shape is: an FX tailwind and an ADR gain paying for a paid-media ramp, with the AI support saving a rounding error next to the marketing.

---

## 6. Forward: three profiles, FY2026E to FY2028E

`31b_forward_margin_by_profile.csv` (quarter and year × profile × scenario × line), `31b_margin_bridge_fy26_fy28.csv` (the walks), figure `31b_forward_profiles.png`. The top line is the workstream-29 bridge and **reconciles to `30_quarterly_pnl.csv` within $1m in all 18 scenario-quarters** (asserted in the script). Each cash line is then projected as `cost(t) = cost(t−4) × driver growth^elasticity × (1 + target)`, where the target is a full-year figure; FY2026 targets are converted into the H2 rate that, with reported 1H26, delivers them, so an FY2026 target here is directly comparable to a workstream-07 FY2026 lever. FY2028 is annual, off the 07 FY2028 driver levers.

**Profiles.** `historical` uses the fitted trends with no overlay at all. `management` sets every target to what management's statements imply, using part A's line-by-line reading (`31a_mgmt_implied_profile.csv`) for the qualitative trajectory and the 07 base lever for the number, because **part A finds no quantified management figure for any cost line in any year**. Each row in `31b_overlay_parameters.csv` now carries part A's `mgmt_confidence`, `mgmt_silent` and the underlying statement IDs. `base` is my judgement.

Part A's confidence scoring is the important qualification on this profile: high for FY2026 on cost of revenue, support, brand marketing and G&A; medium on product development and field operations; **low on four of six lines for FY2027; and silent on five of six for FY2028**. The FY2027 and FY2028 columns of the `management` profile are therefore the house lever set wearing a management label.

| Target (annual) | historical | management | base | Unit |
|---|---|---|---|---|
| Cost of revenue | −1.3 / −1.3 / −1.3 | 0.0 / 0.0 / −0.5 | **+1.0 / +1.0 / +0.5** | % per $ of GBV |
| Operations and support | −2.5 / −2.5 / −2.5 | −5.0 / −5.0 / −5.0 | **−4.0 / −4.5 / −4.5** | % per night |
| Product development | +11.3 each year | 11.0 / 10.0 / 9.5 | 11.0 / 9.5 / 9.0 | % cash growth |
| Brand and performance marketing | +16.5 each year | 25 / 16 / 13.5 | **27 / 15 / 12** | % cash growth |
| Field operations and policy | +24.3 each year | 18 / 14 / 12 | 18 / 13 / 11 | % cash growth |
| G&A | +9.6 each year | 2.0 / 5.5 / 5.0 | 3.0 / 5.0 / 5.0 | % cash growth |

**Adjusted EBITDA margin, bear / base / bull revenue scenario:**

| Profile | FY2026E | FY2027E | FY2028E |
|---|---|---|---|
| historical | 34.8 / **35.8** / 36.8 | 30.5 / **35.4** / 38.5 | 26.6 / **34.6** / 39.4 |
| management | 34.8 / **35.8** / 36.8 | 31.7 / **36.5** / 39.5 | 29.9 / **37.4** / 41.9 |
| base | 34.3 / **35.3** / 36.3 | 31.1 / **35.9** / 39.0 | 29.5 / **36.9** / 41.5 |
| *07 lever model* | *34.6 / 36.1 / 37.6* | *32.0 / 36.6 / 40.7* | *30.4 / 37.5 / 43.7* |
| *30 quarterly walk* | *34.0 / 36.2 / 38.0* | *30.6 / 36.4 / 41.3* | *—* |

The FY2026 tie between `historical` and `management` is a coincidence of offsetting lines, not agreement: on FY2026 cash costs of about $9.2bn each, history spends **$135m less on brand marketing** but **$82m more on G&A, $48m more on field operations and $34m more on support**, netting to a $2m difference. From FY2027 the profiles separate, and by FY2028 the spread is **2.8 points**.

**The FY2028 gap, by line** ($m, base scenario, history vs management): field operations **1,499 vs 1,177** (+$322m), G&A **1,408 vs 1,208** (+$200m), support 1,487 vs 1,374, product development 1,842 vs 1,788, cost of revenue 2,867 vs 2,967 (history is *cheaper*, extrapolating a per-GBV decline the commitments note contradicts), brand marketing 2,524 vs 2,625 (history spends **less**). **The forward margin case is a bet on field operations and G&A decelerating** — not on marketing discipline and not on AI. Field operations has compounded at 24% a year since 2023, grew 43% in FY2025 and 24% in 1H26; management's profile needs 12%.

**Base-case walk** (`31b_margin_bridge_fy26_fy28.csv`, base profile, base scenario, margin points):

| | FY25→FY26E | FY26E→FY27E | FY27E→FY28E |
|---|---|---|---|
| Revenue per night | +3.47 | +1.49 | +1.72 |
| Cost of revenue | −1.14 | −0.56 | −0.49 |
| Operations and support | +0.40 | +0.41 | +0.39 |
| Product development | −0.11 | −0.04 | −0.09 |
| Brand and performance marketing | −2.02 | −0.78 | −0.55 |
| Field operations and policy | −0.47 | −0.24 | −0.18 |
| G&A | +0.55 | +0.29 | +0.20 |
| Add-backs | −0.54 | +0.12 | 0.00 |
| **Total** | **+0.15** (35.1 → 35.3) | **+0.69** (→ 35.9) | **+1.00** (→ 36.9) |

**Reconciliation.** Base profile against the 30 walk: FY26 **−0.94** points, FY27 **−0.49**. Against 07: FY26 −0.90, FY27 −0.61, FY28 −0.59. Three causes: brand marketing at +27% in FY26 rather than the +25% implied by 30's H2 phasing (about half a point); cost of revenue at +1.0% per $ of GBV rather than flat (about a quarter point a year); support at −4.0/−4.5% rather than −5.0% (about a tenth). In the bear and bull a fourth, deliberate reason widens the gap: **this model holds the cost profile fixed across revenue scenarios**, while 07 and 30 flex marketing down in the bear — so this model's bear is kinder (+0.6 against 30 in FY27) and its bull harsher (−2.2). Costs here are decisions; if you want management to cut, set the overlay and say so.

---

## 7. Sensitivities

`31b_sensitivities.csv`, figure `31b_sensitivities.png`. Base profile, base revenue scenario. The single-year column applies the shock in FY2028 alone and is the number to quote per unit; the compounded column applies it every year FY2026-FY2028.

| Shock | FY2028E margin, single year | FY2028E margin, compounded | FY2028E Adj. EBITDA, compounded |
|---|---|---|---|
| Operations and support cost per night −10% | **+0.84** | +2.26 | +$396m |
| Brand marketing growth +5pt | **−0.66** | −1.98 | −$347m |
| Take rate +10bp | **+0.47** | +0.69 | +$194m |
| ADR ex-FX +1pt | **+0.42** | +1.06 | +$340m |
| FX on revenue +1pt | **+0.42** | +1.06 | +$340m |
| Nights +1pt | **+0.34** | +0.88 | +$308m |
| 1pt of nights share from NA to LatAm/APAC | **−0.33** | −0.86 | −$264m |

These are built from a different construction to the 07 note's and land close to it (07: ADR ex-FX +0.46, FX +0.47, take +0.48, nights +0.35, support −10% +0.96 on the FY2026 base), which is a useful cross-check on both.

**The regional mix sensitivity is new.** Moving one point of nights share out of North America (regional ADR index 1.42) into LatAm and APAC (nights-weighted index 0.632) is a −0.79% hit to blended ADR and **−0.33 points of margin**. This is not hypothetical: North America's share of nights fell from 39.1% (FY2020) to 29.6% (FY2025) and 29.3% in 2Q26, while LatAm plus APAC went 25.9% to 30.0%, and the measured geographic-mix drag on ADR has been negative every year — −0.5, −2.8, −1.1, −1.2, **−1.6pp** (`data/processed/adr/07_full_decomposition.csv`). At about 0.42 margin points per 1% of ADR, the recent drag is running **−0.5 to −0.7 margin points a year** and it is compounding with Airbnb's own growth mix. It is the single most underweighted item in every margin model in this repo, including 07 and 30, both of which fold it silently into "ADR ex-FX".

**Estimation risk is comparable to business risk.** Putting the imposed elasticities at their leave-one-year-out bounds:

| | FY2028E margin points |
|---|---|
| Support-to-nights elasticity 1.00 → 0.41 | **+1.14** |
| Support-to-nights elasticity 1.00 → 1.66 | **−1.50** |
| Cost of revenue-to-GBV elasticity 1.00 → 0.96 | +0.25 |
| Cost of revenue-to-GBV elasticity 1.00 → 1.11 | −0.70 |

A ±1.5-point range on the support line from estimation alone is bigger than every business shock in the table above except the support target itself. **The honest statement is that we do not know how operations and support scales with nights**, and any FY2028 margin quoted to a tenth of a point is over-claiming.

---

## 8. Corrections to existing work

1. **`2026-09-05_margin-drivers.md` section 10 attributes +3.7 margin points to "ADR ex-FX" over FY2022-FY2025. That single line is a net of two large opposing terms.** On the workstream-31a decomposition it is **+5.4 points of unit-size mix and like-for-like price against −2.5 points of regional mix**. The mix drag has been negative every year since 2021 (−0.5, −2.8, −1.1, −1.2, −1.6pp of ADR) and it is getting worse. Modelling ADR ex-FX as one positive number under-states both the pricing gain and a structural drag that compounds with Airbnb's own growth mix.
2. **The FX contribution to the FY2022-FY2025 bridge is +1.1 points here against +0.7 in `abnb_margin_bridge.csv`.** This is a basis difference, not an error: the existing bridge uses the letters' reported-versus-ex-FX revenue growth, this uses the reconstructed regional currency basket in `data/processed/adr/07_full_decomposition.csv` (validated at r 0.988, RMSE 0.68pp against the 17 disclosed quarters). Both are defensible; they should not be mixed inside one table.
3. **"Product development is flat at 10-11% of revenue in cash" (margin-drivers section 3.5, carried into 07) is an artefact of rising ADR.** Cash product development per night went $2.42 (2022) → $2.29 (2023) → $2.38 → $2.51 (2025) → $2.46 (1H26). The percent-of-revenue reading is flat because revenue per night rose 8% over the same period. The line's measured elasticity to revenue is **negative**; it is a headcount plan, and the flat-percent framing will mislead in any year when ADR stops rising.
4. **Operations and support is not a leverage story.** Both 07 and 30 model it as cost per night with a declining rate, which is the right *basis*, but the surrounding language in the margin-drivers note ("the quiet source of leverage") implies scale economies. The fitted nights elasticity is 1.39 with a LOO range spanning 0.41 to 1.66 and a fixed share of 19%. What is falling is a per-unit trend that has to be re-earned each year, and the only measured year is −3.8%.
5. **The "brand marketing is a fixed amount per market" model cannot be estimated and should not be asserted.** The levels intercept share for brand and performance marketing is −2% on 1Q22-2Q26. There is no disclosed expansion-market count, so the fixed-per-market structure is unidentified from public data; the parameter row exists in `31b_overlay_parameters.csv` marked NOT DISCLOSED for part A.
6. **My FY2026 base of 35.3% is 0.9 points below the 30 walk's 36.2% and 0.8 below 07's 36.1%**, and the causes are named in section 6. I do not think either is wrong; the difference is that this model refuses to step brand marketing down to +17% in H2 2026 on the strength of "investment timing" language, and it takes the data-hosting commitment as a real cost of revenue increase rather than a flat line. **Both notes' FY2026 numbers still clear the 35.5% floor; mine does not (35.3%).** That is a live disagreement to carry into 5 November, alongside the Q3 margin disagreement already logged in the 30 note.

---

## 9. For the model

Every row is in `31b_overlay_parameters.csv` or `31b_line_elasticities.csv` with its source string.

| Parameter | Value | Unit | Source |
|---|---|---|---|
| Cost of revenue elasticity to GBV | **1.01** (LOO 0.96-1.11) | elasticity | estimated, 1Q23-2Q26, n=14, t 3.3, R² 0.48 |
| Operations and support elasticity to nights | 1.39 (LOO 0.41-1.66) — imposed at 1.0 | elasticity | estimated but not identified; imposition documented |
| Product dev / brand / field / G&A elasticity | not identified — imposed at 0.0 | elasticity | see section 3; all fail sign, t or LOO |
| Fixed share: G&A / product dev / support / cost of revenue | 61 / 32 / 19 / 1 | % of the line | levels regression intercept, 1Q22-2Q26 |
| Historical per-unit trends | cost of revenue −1.3, support −2.5, product dev +11.3, brand +16.5, field +24.3, G&A +9.6 | % per year | mean y/y log change, 1Q23-2Q26 |
| Base cost of revenue | +1.0 / +1.0 / +0.5 | % per $ GBV per year | judgement; purchase obligations $719m→$1,749m, hosting commitment $1.7bn through 2031 |
| Base operations and support | −4.0 / −4.5 / −4.5 | % per night per year | judgement; 1H26 realised −3.8% is the only measured figure |
| Base brand and performance marketing | +27 / +15 / +12 | % cash growth | judgement; 1H26 +32%, needs H2 2026 at about +21% |
| Base field operations and policy | +18 / +13 / +11 | % cash growth | judgement; FY25 +43%, 1H26 +24% |
| Base product development / G&A | 11 / 9.5 / 9 and 3 / 5 / 5 | % cash growth | judgement, close to 07 |
| D&A and other add-backs | 0.9 | % of revenue | 07 lever set; FY2026 uses reported 1H26 add-backs for the reported half |
| Non-USD share of cost of revenue | 55 | % of the line | margin-drivers section 14; used in the FX sensitivity only |
| Regional ADR index (NA / EMEA / LatAm / APAC) | 1.42 / 0.97 / 0.68 / 0.59 | index | `10_regional_panel_quarterly.csv` |
| Mix drag per 1pt of nights share NA → LatAm/APAC | −0.79% ADR, −0.33 margin points | | this note, section 7 |
| FY2026E / FY2027E / FY2028E margin, base profile, base scenario | **35.3 / 35.9 / 36.9** | % | this model |
| FY2028E margin, pure history | **34.6** | % | this model, no overlays |
| FY2028E margin, management-implied | **37.4** | % | 07 lever set applied to the 29 driver path |
| Sensitivities (FY2028E, single-year shock) | support −10% +0.84; brand +5pt −0.66; take +10bp +0.47; ADR ex-FX +1pt +0.42; FX +1pt +0.42; nights +1pt +0.34; mix 1pt −0.33 | margin points | `31b_sensitivities.csv` |
| Elasticity estimation risk on the support line | ±1.14 / −1.50 | margin points, FY2028E | LOO bounds |

---

## 10. Caveats

- **n = 14.** A small sample for six lines and four candidate drivers each. Only one relationship clears the promotion rule; the other five are reported as failures rather than dressed up. Do not cite any elasticity here except cost of revenue's without its LOO range beside it.
- **The restricted elasticities are impositions, not estimates.** Support at 1.0 on nights and the four discretionary lines at 0.0 are economic priors chosen because the unrestricted estimates are not usable. Both imposed values are stress-tested, and the support one moves FY2028 by ±1.5 points.
- **The 2019 and 2020 legs are on a different basis** — GAAP lines from XBRL with SBC allocated on the FY2021 functional split — and FY2020's $3,003m of IPO stock compensation makes any 2020 comparison close to meaningless.
- **The cost profile does not flex with the revenue scenario.** That is deliberate (see section 6) but it means the bear and bull columns here are the operating leverage of the driver path, not a forecast of how management would respond. 07 and 30 make the opposite choice.
- **The forward quarters compound.** 3Q27 and 4Q27 are computed against this model's own 3Q26 and 4Q26, so any 2026 error carries into the 2027 rates. The FY2028 step is annual and rests on the 07 FY2028 driver levers, themselves judgement.
- **Everything here is Adjusted EBITDA.** Stock compensation, at 13% of revenue, sits outside it; the SBC-adjusted picture in 07 section 8 is the one the pitch has to defend. This note does not project SBC, taxes, interest or free cash flow.
- **The `management` profile's numbers are still house numbers.** Part A supplies the trajectory, the statement IDs and the confidence for each line and year, but no quantified management figure exists for any cost line, so the levels come from the 07 base levers. The weakest link remains the mapping from "support cost per booking −16%" to a line-level per-night rate; part A confirms the −10%/−16% figures are per booking and that the line as a whole is only said to "scale somewhat linearly".
- **Nothing here predicts the stock.** The print-day evidence is in workstreams 02, 04 and 20.
