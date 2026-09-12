# 02. Model-architecture audit: how ABNB revenue is forecast today, where the identity leaks, and why the predictive programme failed

Author: model-architecture auditor, 11 Sep 2026. Every repo claim below cites a file I opened; line
numbers are from the files as they stand at `main @ a5d6dbb`. Numbers I computed myself are marked
**[recomputed]** and the script is inline in §3.1/§4.2 so they can be re-run.

Audience: the methodology proposers. The purpose is to stop the next build from repeating five
specific mistakes: (i) a revenue identity whose last term is a plug with a ±2pp error bar,
(ii) a nights build whose weights are contaminated by FX, (iii) an ADR decomposition that is
measured in one workbook and ignored in the model that actually prints the number, (iv) five FY27
estimates in the tree that differ by $250M with no reconciliation, and (v) a predictive programme
that tested ~3,500 pairs against the wrong target at n≈10.

---

## 1. The identity exactly as implemented

### 1.1 Quarterly engine — `analysis/src/overnight/13_driver_model.py`, `build_quarters()` L363-393

Term by term, for forecast quarter `q` with prior-year quarter `p = q-4`, region `r ∈ {na, emea, latam, apac}`,
scenario `s ∈ {Bear, Base, Bull}`:

| # | Term | Code | Set at |
|---|---|---|---|
| 1 | `n_r,p = nights_p × share_r,p` | L373 | `share` from `QSHARE` L104-108, = `10_regional_panel_quarterly.csv` `{r}_nights_share_est_pct`, **renormalised to 1** |
| 2 | `g_r,q,s` regional nights growth | L371 | `REGIONAL_G` L253-259 (hard-coded from `10_regional_forecast.csv`) |
| 3 | `drag_r,y = regmult × REG_DRAG_PP[y][r]` | L372 | `REG_DRAG_PP` L265-267; `regmult` L368 = `ANNUAL_INPUTS[y]["reg_mult"]` (1.67 base) |
| 4 | `n_r,q = n_r,p × (1 + g − drag)` | L374 | — |
| 5 | `N_q = Σ_r n_r,q` | L376 | **no reconciliation calibration is applied** (contrast `10_regional_forecast.py` L78, L137) |
| 6 | `a_x` = ADR growth ex-FX | L377 | `ADR_EXFX_Q` L270-271: +3.0% for 3Q26/4Q26, +2.5% for 1Q27-4Q27 (base) |
| 7 | `f_A` = FX effect on ADR | L378 | `FX_Q` L278-285, WS05 broad-USD contemporaneous fit |
| 8 | `f_R` = FX effect on revenue | L378 | `FX_Q` L278-285, WS05 **lagged** fit `−0.640 + 0.413 × mean(EUR/USD y/y at t-1,t-2)`; 3Q26 overridden to the guided +3.00 |
| 9 | `ADR_q = ADR_p × (1+a_x) × (1+f_A)` | L379 | — |
| 10 | `GBV_q = N_q × ADR_q` | L380 | — |
| 11 | `τ_q = τ_p + Δbps/10⁴` | L381 | `take_bps` L177 / L200 / L223; base = 0 bps FY26 and FY27, +5 bps FY28 |
| 12 | `w_q = (1+f_R)/(1+f_A) − 1` ("FX timing wedge") | L382 | derived |
| 13 | `CoreRev_q = GBV_q × τ_q × (1 + w_q)` | L383 | — |

### 1.2 Annual engine — `build_annual()` L396-502

- FY26 = 1H26 **actual** (`H1_26` L85-87: rev 2678+3608, nights 156.2+148.3, GBV 29 200+27 200) + 3Q26 + 4Q26 forecast quarters (L406-413).
- FY27 = sum of the four 2027 forecast quarters (L414-421).
- FY28 has **no regional and no FX build**: total nights growth is a scalar `NIGHTS_2028` (L248), ADR ex-FX a scalar `ADR_EXFX_2028` (L249), and `FX_2028` is **hard-zero in all three scenarios** (L286). Take rate rolls off `prev["take_assumed"]` (L430) — a different base from the quarterly engine's `τ_p`.
- New business: `nb_incr = new_business_y − FY25.new_business × core_y / FY25.rev` (L437), i.e. only the excess over platform-rate growth of the FY25 $12M Services base is added. `revenue = core + nb_incr` (L438).

### 1.3 The identity after algebra — this is the part that matters

Substituting 9→10→13:

```
CoreRev_q = N_p·ADR_p·τ_p × [Σ_r w_r,p (1 + g_r − drag_r)] × (1 + a_x) × (1+f_A) × (1+f_R)/(1+f_A) × (1 + Δbps/(10⁴τ_p))
          = Rev-basis_p × (1 + n̂) × (1 + a_x) × (1 + f_R) × (1 + Δτ/τ_p)
```

**`f_A` cancels exactly.** The FX effect on ADR has *zero* effect on modelled revenue in every
quarter and every scenario. It moves only the displayed `adr` and `gbv` lines (L379-380, written to
`13_model_quarterly.csv`). This is the single most consequential architectural fact in the file, and
it is not stated anywhere in `model/assumptions.md` or `research/notes/overnight/13_driver-model-build.md`.
Consequence: **the best-validated survivor in the entire ~3,500-test predictive programme — broad-USD
→ ADR FX, walk-forward error 0.44× naive (`research/notes/predictive/03_macro-altdata-nowcast.md`
finding 1; `model/ADR_decomposition.xlsx` 5_Forecast row "FX contribution, pp = 0.52 − 0.72 × USD y/y")
— is wired to a display-only line.** Revenue FX runs entirely off the *other* fit (lagged EUR/USD,
n 17, r 0.80, LOO RMSE 2.30pp per `29_fx_step_down.csv` `q4_fit ± loo`), which is the weaker of the two.

Second consequence: the model has **no take-rate mechanism at all**. `τ_p + Δbps` with `Δbps = 0`
means the take rate is a pure prior-year carry, and the entire booking-versus-check-in recognition
gap is expressed through one derived scalar `w_q`, which is itself a ratio of two FX fits. The
"FX timing wedge" is not a mechanism; it is the residual of two regressions being used as the
model's only timing term.

### 1.4 Dependency graph (text), inputs → FY27 revenue

```
data/raw/letters/*.htm ──(hand-coded REG dict, 10_regional_panel.py L~95-115)──┐
data/processed/overnight/10_xbrl_revenue_geography.csv ──┐                     │
                                                         ▼                     ▼
                         nights_shares(q) = trailing-4Q regional revenue / IDX{na 1.42, emea 0.97,
                              latam 0.68, apac 0.59}, normalised   [10_regional_panel.py L~200-210]
                                                         │
                                     10_regional_panel_quarterly.csv
                        ┌────────────────────────────────┴───────────────────────────┐
                        ▼                                                            ▼
     10_regional_forecast.py: shares drifted fwd (L67-75)                 13_driver_model.py QSHARE
     + judgemental F{} growth dict (L84-107) + CALIB −0.41pp (L78)        (L104-108, prior-yr shares,
     → 10_regional_forecast.csv                                            NO calibration)
                        │                                                            │
                        │            ┌───────────────────────────────────────────────┤
                        │            │  REGIONAL_G (L253-259, hard copy of F{})       │
                        ▼            ▼                                               ▼
   29_q4_fy27_bridge.py         11_regulatory_overlay.csv ──REG_DRAG_PP──►   N_q  (L370-376)
   (FY27 $15,804M)                   (Monte Carlo, WS11/WS22)                        │
                                                                                     │
 FRED DEXUSEU/DTWEXBGS ──05_macro_transmission.py──► 05_fx_schedule.csv ──FX_Q──► f_A, f_R
                                                                    │                │
 WS06/WS07 judgement ─────────────────────► ADR_EXFX_Q (+2.5% FY27) ─┼──► ADR_q ──► GBV_q
                                                                     │                │
 02_kpi_panel_quarterly.csv ──► τ_p (prior-yr quarter take) ──ANNUAL_INPUTS take_bps──┤
                                                                                      ▼
                                                        CoreRev_q = GBV·τ·(1+w)  (L383)
                                                                                      │
 11_new_business_scenarios.csv ──► new_business ($212M FY27 base) ──nb_incr (L437)────┤
                                                                                      ▼
                                                        FY27 revenue $15,842M (13_model_annual.csv)
                                                                                      │
                              WS12 exit multiple 16.5x (+0.48 turns / pt fwd growth) ──► $157 base target
```

Three parallel branches **read the same inputs and do not feed back**:
`analysis/src/adr/01→15` → `model/ADR_decomposition.xlsx` 5_Forecast (ADR ex-FX +1.37% FY27 base);
`analysis/src/overnight/14_revenue_by_line.py` (imports `13` wholesale, L57-59, and re-cuts by line);
`analysis/src/choice_nights_driver{,_global}.py` (nights +7.2% FY27 vs 13's +8.9%).

---

## 2. Free parameters, classified

Legend: **measured** = estimated from data with a reported error; **fitted** = regression output;
**assumed** = judgement with a cited rationale but no estimate; **plug** = set so something else
reconciles, or carried forward with no mechanism.

| Parameter | Where | How set | Class |
|---|---|---|---|
| Regional nights growth `g_r` (24 cells) | `13_driver_model.py:253-259`; source `10_regional_forecast.py:84-107` | Hand-written bear/base/bull per region per period with a prose rationale citing StatCan/BEA/JNTO/Eurostat. No estimator, no error bar. | **assumed** |
| Regional nights shares `w_r,p` | `13_driver_model.py:104-108` ← `10_regional_panel.py` `nights_shares()` | trailing-4Q XBRL regional **revenue** ÷ a fixed ADR index, normalised | **plug** (see §3.2) |
| ADR index `IDX = {1.42, 0.97, 0.68, 0.59}` | `10_regional_panel.py` `IDX` | "calibrated so North America averages 30% of nights in 2025" (letters 1Q25-3Q25) and ordered as the letters describe. One year of calibration, held fixed 2020-2026. | **plug** |
| Reconciliation calibration `CALIB = −0.41pp` | `10_regional_forecast.py:78, 137` | mean `residual_vs_total_pp` over 3Q25-2Q26 | **plug**, and **not applied in `13`** |
| NA/EMEA nights 4Q22-3Q24 | `10_regional_panel.py` derived block | solved as the residual to reported total, split by XBRL revenue growth net of regional ADR, clipped to ±12 | **plug** |
| Regulatory drag `REG_DRAG_PP` | `13_driver_model.py:265-267` | WS11 Monte Carlo medians, repaired by WS22 | **measured** (model-based) |
| `reg_mult = 1.67` | `13_driver_model.py:194, 217` | = WS11 mean ÷ median; used to convert a median to a mean | **assumed** |
| ADR ex-FX `a_x` (+3.0% 2H26, +2.5% FY27) | `13_driver_model.py:270-271` | "WS06 and WS07 agree"; contradicted by the ADR workbook's own +1.37% (§5) | **assumed** |
| `f_A` FX on ADR | `13_driver_model.py:278-285` ← `05_fx_schedule.csv` | broad-USD contemporaneous fit, r 0.96, walk-forward 0.44× naive | **fitted** — and **inert** (§1.3) |
| `f_R` FX on revenue | same | lagged EUR/USD fit, n 17, r 0.80, LOO RMSE 2.30pp; 3Q26 overridden to the guided +3.00pp | **fitted**, with one **assumed** override |
| Take rate `τ_p` carry | `13_driver_model.py:381` | prior-year same quarter, unchanged | **plug** |
| `take_bps` (0 / 0 / +5) | `13_driver_model.py:177, 200, 223` | "management guided FY26 take rate flat" | **assumed** |
| FX timing wedge `w_q` | `13_driver_model.py:382` | derived ratio of the two FX fits | **plug** |
| `new_business` ($42/212/516M) | `13_driver_model.py:192, 215, 238` ← `11_new_business_scenarios.csv` | Services GBV ≈ $80M FY25 "assumed"; ads = a launch scenario, $0 in FY26 | **assumed** |
| FY25 Services base $12M | `13_driver_model.py:80` `new_business=12.0` | assumption inside an assumption (`11_new_business_scenarios.csv` assumptions column) | **assumed** |
| `NIGHTS_2028`, `ADR_EXFX_2028`, `FX_2028=0` | `13_driver_model.py:248, 249, 286` | scalars; FX literally zero | **assumed** / **plug** |
| Seats-dilution drag (−0.48 FY26, −0.57 FY27) | `adr/15_seats_dilution.py:95-97` | unit-mix arithmetic on undisclosed volumes; tickets $75/$120, hotel ADR $140, hotel nights 18.7M | **assumed** (structure measured, inputs assumed) |
| `HOME_NIGHTS_GROWTH = {bear .06, base .08, bull .10}` | `adr/15_seats_dilution.py:55` | literally commented `# placeholder` | **plug** |
| LOS elasticity | `adr/03_annual_decomposition.py:94-121` | fit is **NOT IDENTIFIED** (t 1.8, sign flips ex-APAC, n 16); `LOS_BAND` central −0.15 from host weekly/monthly discount structure | **assumed** (honestly flagged) |
| LOS mix term (+0.30pp base) | `adr/14a-c`, `2026-09-09_los_synthesis.md` | bucket shares disclosed 2021-22, solved off ALOS 2023-25; ratios 1 / 0.966 / 0.852 from 139 quote dumps | **measured** |
| Unit-size term (+0.74pp base) | `adr/13_party_size_adr.py:61-84` | hedonic 0.399·dln(capacity) + 0.140·d(bedrooms), bedrooms-per-log-capacity 1.37 ⇒ ε = 0.59, applied to booked-capacity growth from 123-market review panel | **measured** |
| Geographic mix (−1.7pp base) | `ADR_decomposition.xlsx` 5_Forecast | "Ran −1.1, −1.2, −1.6pp in 2023-25. Drive off the regional nights build." — **nobody drove it off the regional build** | **assumed** |
| "Pricing + sub-regional mix" (+2.2pp base) | `adr/07_assemble.py:103-104` | residual by subtraction: `within_region_exfx − size − LOS` | **plug**, explicitly named as jointly unidentified |
| Fee-migration reprice (+0.5pp) | `ADR_decomposition.xlsx` 5_Forecast ← `adr/12_fee_migration_reprice.py` | +0.7% / −12.3% / +3.8% bounds on the migrated cohort | **assumed** |
| Hotel commission 11% | `14_revenue_by_line.py:67`; `11_new_business_scenarios.csv` | undisclosed; note says 13% closes half the 13↔14 gap | **assumed** |
| `SWITCH_RATE = 5.0` | `choice_nights_driver.py` | Farronato & Fradkin implied 10.3, discounted by judgement to 5.0 | **assumed** |
| `CONTESTABLE = 0.38` | `choice_nights_driver.py` | F&F survey: 62% would not have used a hotel | **measured (external)** |
| `CATEGORY_GROWTH = 4%` | `choice_nights_driver.py` | inverted from disclosed NA nights 146→154→158M | **fitted (identity inversion)** |
| `PRODUCT_SHIFT = 0` | `choice_nights_driver.py` | zero by default; `na_nights_reconciliation.md` shows 0.099 logit is needed to hit WS10 NA +7%, and management's own 3-pt attribution = 0.081 | **plug** |
| `REST_OF_WORLD_NIGHTS_GROWTH = 0.10` | `choice_nights_driver.py` | commented "10% placeholder"; superseded by `_global.py` fades of 16%/13% | **plug** |
| WS29 "take-rate/timing residual" (−0.53pp Q4, 0.0 FY27) | `29_q4_fy27_bridge.py:150-160` | base = trailing-4 mean of `rev_yoy_exfx − nights − adr_exfx`; bear/bull hand-set | **plug** |
| Exit multiple 13.5/16.5/18.5x | `13_driver_model.py:312` | WS12 blend; slope +0.48 EV/EBITDA turns per pt of forward revenue growth | **fitted** |
| `dcf_start_growth = 9%` | `13_driver_model.py:320` | "a round number just under the model's own FCF CAGR of 9.9%, clipped to 0-15%" | **plug** (self-documented) |
| FY25 working-capital residual −$139M | `model/assumptions.md` §3 | "chosen so the eight lines above reproduce reported FY2025 FCF exactly. It is a plug" | **plug** (self-documented) |

**Count: 12 plugs and 18 assumed parameters sit between the inputs and FY27 revenue.** Two of the
plugs (`τ_p` carry and `w_q`) jointly carry the entire recognition-timing mechanism, which is the
largest single source of quarterly revenue error (§3.1).

---

## 3. Overlaps, double counts and measured biases

### 3.1 The take-rate carry × FX-wedge construction is a plug with a ±2pp error bar **[recomputed]**

I ran the exact `build_quarters` arithmetic backwards over the last eight reported quarters, feeding
it **perfect foresight** of nights growth, ADR ex-FX, ADR FX and revenue FX as disclosed in
`data/processed/overnight/02_kpi_panel_quarterly.csv`, with `take = τ_{t-4}` and `Δbps = 0`:

| q | model rev ($M) | actual ($M) | rev error % | GBV error % | wedge pp | prior-yr wedge pp |
|---|---|---|---|---|---|---|
| 3Q24 | 3 751.7 | 3 732 | **+0.53** | −0.04 | +0.60 | +1.27 |
| 4Q24 | 2 539.4 | 2 480 | **+2.39** | −0.28 | +1.11 | +0.88 |
| 1Q25 | 2 289.6 | 2 272 | **+0.77** | +0.05 | −0.10 | −0.60 |
| 2Q25 | 2 982.3 | 3 096 | **−3.67** | −0.22 | −1.86 | +0.91 |
| 3Q25 | 4 140.8 | 4 095 | **+1.12** | 0.00 | −2.63 | +0.60 |
| 4Q25 | 2 825.5 | 2 778 | **+1.71** | +0.15 | −1.85 | +1.11 |
| 1Q26 | 2 657.5 | 2 678 | **−0.77** | +0.08 | −1.90 | −0.10 |
| 2Q26 | 3 685.8 | 3 608 | **+2.16** | +0.22 | +2.67 | −1.86 |

Mean error **+0.53%**, sd **1.97%**, trailing-four mean **+1.05%**. The GBV column is ~0 in every
quarter — nights × ADR is exact by construction. **100% of the error is in `τ_p × (1+w_q)`.**

Mechanism of the bias: `τ_{t-4}` is not an FX-neutral take rate. It already embeds the prior year's
own timing wedge. The correct construction is `τ_{t-4}/(1+w_{t-4}) × (1+w_t)`; the model uses
`τ_{t-4} × (1+w_t)`, i.e. it omits dividing out the prior-year wedge. The last column shows how big
that omission is: the prior-year wedge ranges −1.86pp to +1.27pp.

**Bias direction and size for the live forecast:** 3Q26 base carries `τ_{3Q25} = 17.88%` — a take
rate depressed by 3Q25's own wedge of −2.63pp — multiplied by a fresh wedge of +2.18pp. On the
trailing-four evidence the construction over-predicts by **+1.05% of revenue ≈ +1.1pp of growth
≈ $50M on 3Q26 and ~$165M on FY27**, with a ±2% one-sigma band that is **larger than the entire
$82-112M gap between the model's FY27 and the Street's**. WS29 parameterises the same unidentified
quantity differently and explicitly (`29_residual_history.csv`: residual −0.79, −1.82, +1.85, −1.34pp
over 3Q25-2Q26; base = trailing-4 mean, FY27 set to 0.0 by hand). Two parameterisations, one plug,
no mechanism.

**Fix by construction.** Stop forecasting a take rate. Model revenue as a **check-in-weighted
convolution of GBV**: `Rev_q = Σ_k φ_k · GBV_{q-k} · fee`, with `φ` a booking-to-stay lag kernel
estimated from (a) the `unearned_fees` / `funds_held` balance sheet identity in
`data/processed/abnb_backlog_indicators.csv` and (b) the 120-market booking curves in
`booking_curves_by_market.csv`. `research/notes/2026-09-10_h1-to-h2-bridge.md` §1.3 already shows
this works: the lagged-GBV conversion (⅔ prior quarter, ⅓ two quarters back) has been **17.4 / 17.1 /
17.2%** for three consecutive Q3s and **12.0 / 12.1 / 12.0%** for three Q4s — an order of magnitude
more stable than the take rate the model carries. That single change removes the take-rate plug, the
wedge plug and the take-rate seasonality assumption at once, and it makes RNPL (which lengthens the
book-to-stay gap) a shift in `φ` rather than an unexplained residual.

### 3.2 The nights weights are built from FX-translated revenue — FX enters the nights build

`10_regional_panel.py` `nights_shares(q)` = trailing-4Q regional **revenue** (XBRL, USD) ÷ a fixed
ADR index `IDX`, normalised. Regional revenue is reported in USD. A LatAm FX tailwind therefore
raises LatAm's revenue share → raises its estimated *nights* share → raises the weight on an 18%-growth
region inside `N_q = Σ_r w_r (1+g_r)`.

- Size: LatAm basket FX ran +11.4% y/y in 2Q26 and +6.4% in 3Q26 QTD (`10_regional_forecast.py:156`).
  On a trailing-4Q basis LatAm revenue is inflated ~8-9% relative to NA, overstating its share by
  roughly **0.7-0.8pp**. Reallocating 0.8pp of weight from NA (+7%) to LatAm (+18%) adds
  **~0.09pp** to total nights growth.
- Direction: **procyclical with dollar weakness** — the same event that inflates `f_A` and `f_R`
  inflates the nights weights. This is the worst possible correlation structure: it makes a
  weak-dollar scenario look like a volume scenario.
- Second defect: `IDX` is calibrated on **2025 only** and held fixed across 2020-2026, while the
  decomposition's own geographic-mix term (−1.1, −1.2, −1.6pp in 2023-25,
  `research/notes/2026-09-07_adr-decomposition.md`) says regional ADR spreads are *widening every
  year*. A fixed deflator applied to a widening spread mis-states shares in every non-2025 year.

**Fix by construction.** Deflate regional revenue by a *time-varying* regional ADR index built from
`10_regional_adr_fx.csv` (which already carries reported and ex-FX regional ADR), and deflate on an
**ex-FX** basis so the weights are FX-neutral. Then impose the adding-up constraint
`Σ_r w_r,t · n̂_r,t = n̂_total,t` as a hard constraint rather than a post-hoc calibration — i.e. run
the regional panel as a **constrained state-space / shift-share system** where the disclosed bands are
interval observations and total nights is an exact aggregation constraint. That is the natural home
for the disclosed bands: interval-censored observations in a Kalman/Bayesian filter, not midpoints.

### 3.3 The regional weighting uses the wrong index base, and the correction is not applied at all **[recomputed]**

`10_regional_panel.py` computes `residual_vs_total_pp = total − Σ_r w_r,**t** · g_r,t`, i.e. it weights
y/y growth rates by **current-period** shares. A Laspeyres growth decomposition requires **base-period**
weights. Because LatAm/APAC shares are rising and they are the fast growers, current-period weighting
mechanically overstates the aggregate:

| q | actual | base-wtd Σw·g | current-wtd Σw·g | resid (base) | resid (current) | index effect |
|---|---|---|---|---|---|---|
| 3Q25 | 8.80 | 8.65 | 8.81 | +0.15 | −0.01 | **+0.16** |
| 4Q25 | 9.82 | 9.42 | 9.63 | +0.40 | +0.19 | **+0.21** |
| 1Q26 | 9.15 | 9.73 | 9.91 | −0.58 | −0.76 | **+0.18** |
| 2Q26 | 10.34 | 11.20 | 11.40 | −0.86 | −1.06 | **+0.20** |

The index-number effect is a stable **+0.19pp** overstatement. The repo's `CALIB = −0.41pp` is the
*current-weighted* residual, so roughly half of it (−0.19pp) is an index-number artefact and the rest
(−0.22pp mean, but **−0.72pp over the last two quarters**) is genuine band-midpoint bias from mapping
"high-single digit" → 8.

**The critical finding: `13_driver_model.py` applies base-period weights (correct, L373) but applies
NO calibration at all (L376).** So it inherits the full band-midpoint bias with none of the
correction. On the trailing-two-quarter evidence the driver model's nights growth is **~0.7pp too
high**, which passes 1:1 into GBV and revenue — **~$110M on FY27**. Note this cuts the *opposite* way
to WS10's headline: WS10's `−0.41` and the driver model's `0.00` differ by 0.41pp of nights growth
and the two builds are quoted as agreeing.

**Fix by construction.** Never weight y/y growth rates. Build the regional panel in **log levels**
with chain-linking, so the aggregate is an identity (`ln N_t = ln Σ_r n_r,t`) and no residual exists
to calibrate. Treat the letters' buckets as interval constraints `lo ≤ Δln n_r,t ≤ hi` and solve the
whole panel by constrained least squares against the disclosed total. That makes the reconciliation
residual structurally zero and turns the band width into an honest posterior interval.

### 3.4 Geographic mix: the model regionalises nights but not ADR

`13` builds nights by region and then applies a **single global** ADR growth to a **single global**
blended ADR (L377-379). The regional mix shift it is itself generating (NA 30.7%→29.3% of nights over
four quarters, LatAm 13.5%→14.8%; `10_regional_panel_quarterly.csv`) has **no channel** into ADR.

This is *not* an arithmetic double count — `ADR_EXFX_Q` is on a reported-blended basis, which already
contains geo mix, so the levels are consistent. It is a **broken feedback loop**: if the bull case
raises LatAm nights growth to 19%, the geographic drag on ADR deepens and the model does not know.
The ADR workbook says so in its own words (`ADR_decomposition.xlsx` 5_Forecast, "How to use this" row 5):

> "Sanity check: at base this scaffold gives ex-FX ADR around +1.5%, against the driver model's FY27
> assumption of +2.5%. If the mix drag is real and regional pricing stays near 3.25%, the model's ADR
> is roughly 1pp too high."

Recomputed from the 5_Forecast base column: `2.2 (pricing) + 0.30 (LOS) + 0.74 (unit size) + 0.50
(fee) − 1.70 (geo mix) − 0.57 (new-business mix) − 0.10 (interaction) = **+1.37%**` against the driver
model's **+2.50%**. **Gap 1.13pp of ADR = 1.13pp of GBV = ~$175M on FY27 revenue.**

**Fix by construction.** Make geographic mix an *output*: `ADR_blended,t = Σ_r w_r,t · ADR_r,t` with
`w` from the same nights build, and forecast only the four regional ADRs ex-FX. Then geo mix is an
identity, not a row, and the bull/bear nights cases automatically carry their own ADR mix consequence.
The decomposition's finding that regional pricing has converged to one number
(`2026-09-07_adr-decomposition.md`, "Regional pricing is one number now, not four") makes this cheap:
one pricing parameter + four disclosed ADR levels + the nights weights.

### 3.5 Unit-size × party-size × LOS: the double count was found and fixed — but only in the workbook

All three terms are drawn from the same Inside Airbnb listing universe. The team caught it twice:

- `2026-09-09_party-size-adr.md`, "Workbook": *"The pricing row was re-based to exclude size (base 2.5%
  from 3.25%) so the size term is not double counted."*
- `2026-09-09_los_synthesis.md`, "Forecast and workbook": *"The pricing row was re-based **again** to
  exclude it (base 2.2%)."*

Residual risk, in order of size:

1. **LOS discount vs unit-size composition.** `2026-09-09_los_synthesis.md` explicitly scopes the LOS
   term to the *discount channel only*: "the lower base rate of listings that accept long stays is
   composition and belongs with the unit-size and sub-regional terms." Good — but the unit-size term
   (`adr/13_party_size_adr.py`) is built on **booked capacity from reviews**, which contains no
   stay-length filter. If long-stay-accepting listings are systematically larger, part of the LOS
   composition effect is inside the +0.74pp size term. Unquantified; bounded by the LOS term's own
   size (+0.30pp).
2. **Party size vs unit size are the same term twice, correctly collapsed.** `13_party_size_adr.py`
   builds ε = 0.399 + 0.140×1.37 = 0.59 and applies it to booked-capacity growth. The note warns
   against the alternative: the composition-implied party index moves *against* capacity
   (annual beta −0.36, p 0.11). **Do not let a proposer add a "party size" driver on top of unit-size
   mix** — that is the live double-count trap.
3. **Elasticity basis mismatch.** `03_annual_decomposition.py` uses a bedroom elasticity of 0.23
   (cited in the brief) while `13_party_size_adr.py` uses a capacity elasticity of 0.59 with
   bedrooms-per-log-capacity 1.37 — and `13_party_size_adr.py:7` says **1.27** in its docstring while
   the note and the computed value say **1.37**. A 0.10 discrepancy in a multiplicative chain is
   ~0.05pp on the size term. Small, but it means the docstring and the code disagree.

**Fix by construction.** Estimate one **log-additive hedonic index** on the quote panel
(`06_quote_line_items.csv`, 1.71M fee-inclusive quotes) with capacity, bedrooms, stay-length bucket
and market fixed effects in a *single* regression, then decompose the fitted index by a **shift-share
on the estimated coefficients**. Terms estimated jointly from one specification cannot double count
by construction; terms estimated in three separate scripts always can.

### 3.6 Seats in the denominator vs new-business revenue lines

Three builds treat the same units three ways:

| | nights denominator | GBV | revenue |
|---|---|---|---|
| `13_driver_model.py` | seats implicitly inside `nights_p` (FY25 base) grown at **home-nights regional rates** | implicitly inside `ADR_p × nights` | hotels+experiences inside `GBV×τ`; Services+ads added via `nb_incr` |
| `adr/15_seats_dilution.py` | explicit: home + hotel + exp seats + svc seats | explicit, at ρ = 0.81 / 0.43 / 0.69 | n/a |
| `14_revenue_by_line.py` | takes `13`'s printed total, backs out home as residual (L147) | sums four lines (L157) | four lines at 13.4 / 11 / 20 / 15% |

- **`nb_incr` is correctly netted.** `L437` subtracts `FY25.new_business × core/FY25.rev`, i.e. only
  the excess over platform-rate growth is added. FY27 base: `212 − 12×1.274 = $196.7M`, of which ads
  $120M (genuinely outside GBV) and Services ~$77M excess. That construction is defensible. **Do not
  "fix" it by adding the full WS11 incremental column** — `13_driver_model.py:345-347` already
  documents why.
- **The real leak is the ADR side.** `13` uses `ADR_EXFX_Q` with **no seats-dilution drag**, while
  `14` reads it as *already net* of dilution and adds the drag back to get home ADR
  (`14_revenue_by_line.py:152`: `home_exfx = dm.ADR_EXFX_Q − dilution_drag`). Meanwhile the ADR
  workbook carries `−0.57pp` as a **separate deductible row**. Two of these three readings are
  mutually exclusive. Whoever writes the next model must state explicitly whether `a_x` is
  home-ADR or blended-ADR. The ambiguity is worth **0.57pp of revenue growth = $88M on FY27**.
- **`15_seats_dilution.py:55` grows home nights at a hard-coded `{bear .06, base .08, bull .10}`
  marked `# placeholder`** — a *different* nights path from the regional build the model actually
  uses (+8.9% printed / +6.8% home per `14_revenue_by_line_annual.csv`). The dilution drag is
  therefore computed off a nights path no other file uses.

**Fix by construction.** Make `14`'s line build the primary engine and let the printed KPIs
(Nights and Seats, blended ADR, blended take) fall out as outputs — which is exactly what
`14_revenue_by_line.py` already does. `13` should then consume `14`, not the reverse. Today the
dependency runs the wrong way (`14` imports `13` at L57-59).

### 3.7 FX appears three times; two of the three cancel or are inert

1. `f_A` on ADR (L379) — **cancels exactly** against the wedge (§1.3). Inert for revenue.
2. `f_R` on revenue via the wedge (L382-383) — the only live FX channel.
3. **Hedge reclass**: `research/notes/overnight/28_fx-hedge-disclosures.md` recommends "carry a
   separate hedge line under revenue FX: −0.21 / −0.21 / −0.18 / −0.18pp for 3Q26-2Q27." **This would
   be a double count** if added to `f_R`, because WS05's fit is estimated on the *letter-stated,
   after-hedge* FX points. `29_q4_fy27_bridge.py` handles it correctly — the hedge column is labelled
   `hedge_memo_pp` and is a memo, "already inside the after-hedge FX number"
   (`29_bridge_assumptions.csv`). Flagging it because the WS28 note's "For the model" section reads
   like an instruction to add it.
4. Fourth, indirect channel: FX inside the nights weights (§3.2).

**Fix by construction.** Two FX objects only: a **booking-date FX index** `X^B_t` and a
**check-in-date FX index** `X^C_t`, both constructed from the same currency basket. Then
`GBV` translates at `X^B`, revenue translates at the `φ`-convolution of `X^B` (because the fee is
struck at booking — which is the mechanism WS28 §3 establishes), and ADR translates at `X^B`. No
wedge, no cancellation, no hedge ambiguity: the hedge is an explicit overlay on the *gross* series.
The FX engine in the sibling `FX-ADR-R-model` / `Citadel-ABNB-fx-engine` folders is the natural home.

### 3.8 Regulatory drag vs supply-panel churn vs the growth assumptions

`REG_DRAG_PP` (EMEA −0.71pp of EMEA nights growth in FY27) is subtracted from `g_emea`. But
`g_emea = 7%` was set in `10_regional_forecast.py:103` from *realised* EMEA growth and a judgement
that "the gap [to Eurostat] stops widening" — realised growth **already contains** the regulatory
losses that had occurred by 2Q26 (Barcelona, Spain's registry, the EU STR regulation). The overlay is
a *cumulative run-rate* loss vs a 2Q26 baseline (`13_driver_model.py:262`), so in principle only the
increment is subtracted — but nothing in the code enforces that the base growth rate is
regulation-free.

- Size: EMEA drag 0.71pp × 39.6% weight = **0.28pp of total FY27 nights ≈ $44M of revenue**. With
  `reg_mult = 1.67` applied on top, the assumed-vs-measured split is itself 40% assumption.
- Independent evidence cuts the other way: `research/notes/overnight/21_inside-airbnb-pair-eligibility.md`
  restated the seven-city retention claim — ex-Austin, six-city retention moved **75.5% → 73.4%**
  with the new-listing share *exactly flat*, i.e. the supply-churn channel is weaker than the
  original claim. The supply panel and the Monte Carlo have never been reconciled to each other.

**Fix by construction.** Put regulation in as a **market-level treatment effect** on the
120-market Inside Airbnb store (982k listings) with a difference-in-differences design around dated
ordinance effective dates, and aggregate to EMEA by nights weight. That is identified, PIT-safe
(ordinance dates are public and dated) and replaces both the Monte Carlo and the `reg_mult` fudge.

### 3.9 The choice driver and the regional build disagree by 1.7pp of FY27 nights, and neither wins

| Build | FY26 nights | FY27 nights |
|---|---|---|
| `13_driver_model.py` (WS10 regional) | +9.9% | +8.9% |
| `choice_nights_driver_global.py` (`choice_driver_global_projection.csv`) | **+7.1%** | **+7.2%** |

`research/notes/na_nights_reconciliation.md` resolves the *level* disagreement honestly: the gap is
the product lever, `PRODUCT_SHIFT = 0` describes "a world with no product initiatives in it," and
management's own 3-point attribution (1Q26 call) = 0.081 logit against the 0.099 needed — **82% of
the gap**. But it also identifies the trade: a launch is a **level** effect that laps.

| Scenario | 2026 | 2027 | 2028 |
|---|---|---|---|
| one-off 2026 launch (+0.10 logit), then laps | +7.0% | **+2.2%** | +3.7% |
| a launch of the same size every year | +7.0% | +5.9% | +7.5% |
| WS10 NA base | +7.0% | +6.0% | — |

**WS10's FY27 NA +6% implicitly assumes Airbnb ships a product lever of the same size every year and
that it is never lapped.** That is the sharpest unstated assumption in the whole tree, it is worth
~3.8pp of NA nights (≈1.1pp of total nights ≈ $170M of FY27 revenue), and it is exactly the kind of
thing a Citadel PM asks about. It is not in `model/assumptions.md`.

---

## 4. The predictive programme: what was tested, and why it failed

### 4.1 Inventory

| Family | Script | Target(s) | n (tests) | Sample / window | Result |
|---|---|---|---|---|---|
| Google Trends | `08_altdata_backtests.py` `trends_features()` | nights/GBV/ADR/rev y/y | 432 (216 × 2 windows) | 2022Q1-2026Q2 (n≤18), WF from 2023Q1 / 2024Q1 | 0 beat naive in window 1; 7 in window 2; **0 beat naive by 20%**; mean WF ratio **3.05×** naive |
| Eurostat platform nights | same, `eurostat_features()` | nights/GBV/rev y/y | 64 | same | best ratio 0.932; 0 beat naive+AR(1) by 20%; mean ratio **1.75×** |
| Inside Airbnb (13-city) | same, `ia_features()` | nights y/y | 36 | 12 evaluable | 4 beat naive in window 1, **0 beat naive AND AR(1)** in window 2 |
| Backlog (unearned / funds held) | same, `backlog_features()` | rev/nights/GBV y/y | 42 | same | **survivor**: `bl_funds_yoy_lag1 → rev_yoy`, ratio **0.600** |
| Component (FX, CC survival) | same | ADR y/y, nights y/y | 24 | same | **survivor**: `mx_usd_yoy → adr_yoy`, ratio **0.637** |
| Macro | `05_macro_transmission.py`, `predictive/03_nowcast_tests.py` | 8 KPI + beat + 1-day return | **1 408** (05) + **890** (03) | 3 windows: full, ex-2021, post-2022 | 5 pass Bonferroni, **all five are the FX mechanism or the 2023 normalisation trend** |
| Peer read-across | `predictive/02_*`, `peer_readthrough/*` | nights/rev surprise | — | 23 prints | fails; and PIT-defective (§4.3) |
| Management tone | `overnight/03_call_features.py` | 1-day / 20-day return | 1 677 turns × 132 features | 23 prints | no survivor |
| Composite indexes | `08_altdata_backtests.py` `build_index`/`nnls_walk_forward` | all KPIs | 3 indexes | same | all three fail |
| Pre-earnings surprise forecast | `20_temporal_validation.py` Task A | **nights / revenue surprise vs Street** | 51 summary rows | 2023Q1+ and 2024Q1+, min train 8 | **4 of 51 beat every baseline, 2 distinct pairs, neither survives both windows ⇒ nothing survives** |
| Post-release drift | Task B | open_5d / open_20d excess | 18 primary rows | 11 events | **0 of 18** beat baselines; ratios 1.03-1.23 |

### 4.2 Why each family failed — the five distinct causes

**(a) Genuinely no signal.** Google Trends. 432 tests, mean walk-forward RMSE **3.05× naive**, best
0.836 and only in the shorter window. A feature that is three times worse than "last quarter's number"
is not an underpowered signal; it is noise with a seasonal pattern that does not match ABNB's.
**Binding. Do not re-open.**

**(b) Wrong target — the single largest cause.** This is the programme's central error and it is
documented in the repo's own words (`research/notes/overnight/20_temporal-validation.md` §3):

> "The **guide and guide+cushion baselines are the worst on this target** (RMSE 2.0-2.4 vs 1.33 for the
> trailing-4 mean). That is not a contradiction of the WS02/WS16 finding that the guide plus its
> cushion forecasts *revenue*; it says the guide-vs-Street gap does not forecast the *surprise vs
> Street*."

The programme tested **surprise vs Street** (a difference of two nearly-equal numbers whose sd is
~1.3pp) using features that predict **level** (sd ~5pp). Predicting a level to 1.1% accuracy is
excellent; it is useless for a target with 1.3pp of total variation. The diagnostic is in
`20_task_summary.csv`: `pred_sd_over_actual_sd` = **0.14 to 0.33** on 16 of 17 Task A model/target
pairs. Every "winner" was an intercept shift — the model learned "expect a +1.4% beat," which the
trailing-4 mean says for free. **Re-openable, with a different target (see §6).**

**(c) PIT leakage / vintage problems.** Three found and repaired, one still live:
- `pr_hotel_revpar_yoy` averaged MAR and HLT unconditionally, but **MAR reported after ABNB in 2023Q3
  (−1d) and 2025Q1 (−5d), HLT in 2024Q2 (−1d)** (`20_temporal_validation.py` PRIMARY_FEATURES
  comment). The `_pit` version is strictly worse (RMSE 3.16 vs 3.22), which tells you the original
  "signal" was the leak.
- `bl_unearned_to_next_rev_lag1` was commented out (`08_altdata_backtests.py:123-131`) because "a lag
  applied after forming a ratio does not" remove the forward-looking denominator.
- `08_altdata_backtests.py:248`: the Inside Airbnb "retrospective scope flag uses LATER scrapes, so a
  frozen replay may only…" — the IA panel is **not vintage-reconstructible** and is labelled as such.
- **Still live:** `ADR_EXFX` in `predictive/03_nowcast_tests.py:48-51` is hard-coded from the letters.
  The letters round to integers ("less than 1%" coded 0.5). Half the variance of a target with a
  3.5pp range is rounding.

**(d) Underpowered at n≈10.** Task A evaluates **6 to 15 events** with `MIN_TRAIN = 8`
(`20_temporal_validation.py:48`). An expanding OLS with one regressor and 8-13 training points has a
slope whose standard error is comparable to the slope; the fit shrinks to the training mean. That is
exactly what `pred_sd/actual_sd ≈ 0.2` means. **With 23 prints total and 19 guided quarters, no
quarterly-frequency single-feature regression will ever clear a trailing-mean baseline.** The n
problem is structural, not fixable by a better feature. **Binding at quarterly frequency;
re-openable only by changing the unit of observation (§6).**

**(e) Wrong grain.** The Inside Airbnb panel as built is 13 cities against a 220-country platform,
and the city mix goes from 1 city to 13 across the sample (`predictive/03_macro-altdata-nowcast.md`
finding 7), so the series is not comparable through time. `08_test_scoreboard.csv` shows `n_flagged_r05_perm05 = 0`
for both IA windows — the panel does not even produce a spurious correlation. Separately, Inside
Airbnb **dropped listed prices from late-2025 dumps**, so the like-for-like price series cannot be
extended (same note). **Re-openable at a different grain:** the 120-market current store (982k
listings, 588M calendar rows) is ~9× the market coverage of the backtested panel, and the failure
was coverage, not concept.

### 4.3 What actually survived, and what it is worth

| Survivor | Target | Statistic | Where it is wired |
|---|---|---|---|
| broad USD → ADR FX | `adr_fx_effect` | r 0.96-0.99, WF **0.44× naive**, Bonferroni-clean post-2022 | `FX_Q` `f_A` — **inert in revenue (§1.3)** |
| funds held / unearned fees y/y → revenue y/y | `rev_yoy` | slope 0.60, r 0.89, WF ratio **0.600** | **not in the model at all** |
| guide + trailing cushion → revenue **level** | revenue $M | 1.1% mean error, 19/19 beats, trailing-8 median cushion +1.79% | `02_q3_2026_guide_card.csv`; used as a cross-check only |
| guide below Street → 20-day drift | `open_20d_pct` | 9/9 negative, mean **−4.21%** executable, binomial p 0.0020 (0.0382 vs ABNB's own 69.6% base rate) | not in the model; it is the trade |

**The most under-used asset in the repo is the funds-held / unearned-fees series.** It is the only
alt-data survivor on a *revenue* target, it beats naive by 40%, it is 10-Q sourced and therefore
strictly PIT, it is distorted by RNPL in a *known, signed* way — and it is the direct observable
counterpart of the booking-to-check-in kernel `φ` that §3.1 says should replace the take-rate plug.
It is currently used as a standalone regressor (where it fails at n=10) rather than as a
**structural constraint on the revenue identity** (where it does not need a regression at all:
`ΔUnearned = Fees booked − Fees recognised` is an accounting identity).

---

## 5. The reconciliation problem: five FY27 revenue estimates, $250M apart

| Build | FY27 revenue | y/y | Source | Why it differs from `13` |
|---|---|---|---|---|
| **Driver model (`13`)** | **$15,842M** | +11.3% | `13_model_annual.csv` | reference |
| Q4/FY27 bridge (`29`) | $15,804M | +11.55% | `29_fy27_bridge.csv` base, order 5 | different FY26 base ($14,168M vs $14,232M: 3Q26 $4,771 vs $4,801, 4Q26 $3,111 vs $3,145); explicit residual term set to 0.0 instead of the wedge; ADR ex-FX +3.0% not +2.5% |
| Revenue-by-line (`14`) | $15,727.8M | +10.9% | `14_revenue_by_line_annual.csv` | **−$114.2M**: hotel GBV monetised at 11% not the blended 13.4%; seats at 15-20% on far smaller GBV. Nights and ADR identical by construction |
| WS10 regional note | ~$15,925M | +12.4% on its own FY26 | `10_regional_forecast.csv` FY27 TOTAL base, FX at 0pp | gross of regulation, FX set to 0 rather than −0.63pp, ADR ex-FX +3.0% |
| ADR-workbook ADR path through `14` | ≈$15,555M | ≈+9.7% | `14_revenue_by_line.py:74` `ADR_WB_HOME_EXFX` Base **+1.94%** vs `13`'s implied home **+3.07%** | ADR ex-FX 1.13pp lower (§3.4) |
| Choice driver + `13` ADR/take | ≈$15,570M | ≈+9.8% | `choice_driver_global_projection.csv` FY27 nights **+7.2%** vs +8.9% | 1.7pp lower nights |
| **Street (3-4 Sep 2026)** | **$15,730-15,760M** | — | `04_current_consensus.csv` | — |

**Range $15.56bn to $15.93bn = $370M = 2.4pp of growth.** The Street sits at $15.73-15.76bn, i.e.
**at the low end of the team's own tree**, essentially on top of `14` and the ADR-workbook path, and
$82-112M below the headline `13` number the pitch would quote.

The four sources of difference, ranked:

1. **ADR ex-FX +2.50% (`13`) vs +1.37% (`ADR_decomposition.xlsx` 5_Forecast) — 1.13pp, ~$175M.**
   The workbook is the only build with a measured decomposition (geo mix disclosed in the 10-K, unit
   size from 1.4M quote-basis listings, LOS from 139 quote dumps). The driver model's +2.5% is
   "WS06 and WS07 agree" — two judgement calls agreeing is not an estimate. **The workbook wins on
   evidence and it is the only one of the two that is documented against its own data.**
2. **Nights +8.9% (`13`) vs +7.2% (choice global) — 1.7pp, ~$270M.** Resolved in
   `na_nights_reconciliation.md` as the product lever, unresolved on the lap (§3.9).
3. **Take-rate treatment: blended 13.4% (`13`) vs by-line (`14`) — $114M.** `14`'s note is explicit:
   "The gap is hotels: 13 monetises every dollar of GBV at the blended 13.4%, this build monetises
   hotel GBV at 11%… a 13% commission closes the FY27 gap to 13 by about half." Since hotel GBV is
   the fastest-growing GBV component, **`13` structurally over-monetises the mix, and the error
   compounds** (FY26 −$46M → FY27 −$114M → FY28 −$283M, bull FY28 −$877M).
4. **FY26 base: $14,232M (`13`) vs $14,168M (`29`) — $64M carried into every FY27 number.** Two
   builds of the same two forecast quarters, different by 0.45%, both quoted as "the base case."

**Nothing in the repo reconciles these.** `13_reconciliation.csv` (216 rows, all `ok`, delta 0.0)
reconciles the **Python mirror to the Excel workbook** — i.e. it verifies that two implementations of
the *same* model agree. It does not reconcile the *models*. That is the missing artefact.

---

## 6. Ten architecture recommendations, ranked

**1. Replace the take rate with a booking-to-check-in kernel.** `Rev_q = Σ_k φ_k · fee · GBV_{q-k}`,
`φ` estimated from the unearned-fees / funds-held identity (`abnb_backlog_indicators.csv`) and the
120-market booking curves. Evidence it works: the lagged-GBV conversion has been 17.4/17.1/17.2% for
three Q3s and 12.0/12.1/12.0% for three Q4s (`2026-09-10_h1-to-h2-bridge.md` §1.3) against a
take-rate construction whose backtest error is +0.53% ±1.97% **[recomputed, §3.1]**. This kills the
two largest plugs (take carry, FX wedge), makes RNPL a shift in `φ` rather than a residual, and turns
the single best alt-data survivor (funds held, WF 0.600× naive) from a failed regressor into a
structural constraint.

**2. Run the regional nights panel as a constrained, interval-observation state-space model.** Log
levels, chain-linked, with (i) the letters' qualitative buckets as interval constraints
`lo ≤ Δln n_r,t ≤ hi`, (ii) `Σ_r n_r,t = N_t` as an exact aggregation constraint, (iii) FX-neutral
regional ADR deflators (time-varying, from `10_regional_adr_fx.csv`) replacing the fixed `IDX`. This
removes the reconciliation residual by construction (**+0.19pp index-number bias and a 0.41pp
uncalibrated-vs-calibrated gap between WS10 and `13`, §3.3**), removes the FX contamination of the
weights (**§3.2**), and produces honest posterior intervals on regional nights instead of band
midpoints. Bands as interval-censored observations is the textbook-correct use of this disclosure.

**3. Make geographic mix an output, not a row.** `ADR_blended,t = Σ_r w_r,t ADR_r,t` with `w` from
recommendation 2. Forecast four regional ADRs ex-FX (the decomposition says regional pricing has
converged, so that is one pricing parameter plus four levels). Closes the 1.13pp / $175M gap in §3.4
and makes every nights scenario carry its own ADR consequence automatically.

**4. Invert the 13 ↔ 14 dependency: make the by-line build primary.** `14_revenue_by_line.py` already
lets the printed KPIs (Nights and Seats, blended ADR, blended take) fall out as outputs, which is
structurally correct in a business whose KPI denominator changed definition twice in five quarters.
Today `14` imports `13` (L57-59) and inherits its blended nights. Reverse it. This resolves §3.6 by
construction and removes the $114M (FY27) → $283M (FY28) hotel-monetisation error.

**5. One hedonic regression for all listing-derived ADR terms.** Estimate capacity, bedrooms,
stay-length bucket and market fixed effects **jointly** on `06_quote_line_items.csv` (1.71M
fee-inclusive quotes), then shift-share the fitted index. Terms estimated in one specification
cannot double count; the current three-script construction required two documented re-basings of the
pricing row and still leaves the LOS-composition ↔ unit-size overlap open (§3.5). Also reconcile the
bedrooms-per-log-capacity discrepancy (docstring 1.27 vs computed 1.37,
`adr/13_party_size_adr.py:7` vs `:64`).

**6. Two FX objects, not four.** A booking-date currency index and a check-in-date index, both from
one basket; GBV and ADR translate at booking, revenue at the `φ`-convolution of booking. This makes
the FX-on-ADR survivor (WF 0.44× naive) **live in revenue** instead of cancelling (§1.3), eliminates
the wedge, and makes the hedge an explicit overlay on a gross series rather than an ambiguous
memo that WS28 invites you to double-subtract (§3.7). The R engine in the sibling folders is the home.

**7. Change the predictive target from "surprise vs Street" to "the guide range Airbnb will set."**
This is the target the pitch is actually judged on: the 3-12 month window covers four *guides* and
zero realised prints that matter. The repo has the dependent variable already built — a 194-statement
guidance ledger (`02_guidance_ledger.csv`), 19 guided quarters, a trailing-8 median cushion of +1.79%,
19/19 midpoint beats and 15/19 above the top of the range. Model the **guidance policy function**
(`guide_mid_{q+1} = f(operating state at print q, cushion history, FX already realised)`) rather than
the surprise. Diagnostic that this is the right move: the same features that score `pred_sd/actual_sd ≈ 0.2`
against surprise (§4.2b) score 1.1% mean error against the *level*. Keep the frozen-spec discipline
of `20_experiment_spec.json` and increment `spec_id`.

**8. Re-open alt data only at the market grain, never at the aggregate.** The 13-city panel failed on
coverage (`n_flagged = 0`, §4.2e); the 120-market store is 982k listings and 588M calendar rows. Test
at the **market × month** level (n in the thousands, not 20) against a **market-level** target —
ordinance-driven supply changes, Eurostat country nights, Hawaii DBEDT — and only then aggregate. The
n≈20 quarterly aggregate is a dead end for any single-feature regression and no amount of feature
engineering fixes it (§4.2d, **binding**).

**9. Identify regulation with a market-level difference-in-differences, not a Monte Carlo.** Dated
ordinance effective dates (the 32-factor register + SQLite) against the 120-market panel. That is
PIT-safe, identified, and replaces both `REG_DRAG_PP` and the `reg_mult = 1.67` median→mean fudge
(§3.8). It also settles the open contradiction between the Monte Carlo and the supply panel's
restated six-city retention (75.5% → 73.4%, new-listing share flat).

**10. Build the one artefact that does not exist: a model-to-model reconciliation.** Five FY27
estimates spanning $370M (§5), and the only reconciliation file in the repo
(`13_reconciliation.csv`, 216 rows, all zero) checks Python against Excel — the same model twice. The
deliverable is a bridge from `13` to `14` to the ADR-workbook path to the choice driver, one named
term at a time, in the style `29_q4_fy27_bridge.py` already uses for the quarterly walk. Until that
exists the pitch cannot answer "which of your four numbers is it?" — and the Street sits at the
**bottom** of the team's own range, which is the fact a Citadel PM will find in ninety seconds.

---

## Appendix: three things that are right and should not be changed

1. **`nb_incr` netting** (`13_driver_model.py:437`). Only the excess over platform-rate growth of the
   FY25 Services base is added; hotels and Experiences are correctly left inside `GBV × τ`. The
   alternative (adding the full WS11 incremental column) is documented and rejected at L345-347.
   A proposer who "fixes" this creates a real double count.
2. **The executable-return convention** (`20_executable_returns.py`). Entering at the next-session
   open rather than the print-date close cut the 9/9 guide-below-Street rule from −8.90% to −4.21%
   and killed the nights→20-day-drift result outright. Any new backtest must use `open_*`, not `legacy_*`.
3. **The LOS-elasticity refusal** (`adr/03_annual_decomposition.py:94-121`). The panel fit is
   insignificant and sign-unstable ex-APAC on n=16; the code records the fit, sets
   `identified = False`, and uses an externally bounded value instead. That is the standard the rest
   of the tree should meet.
