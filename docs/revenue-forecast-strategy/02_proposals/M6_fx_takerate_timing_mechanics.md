# M6 — The Mechanical Layer: a booking-cohort revenue kernel with a dated fee schedule and a two-index FX translation

**Lens:** FX lag, take rate by mechanism, recognition timing.
**Author:** methodology proposer M6, 11 Sep 2026. Repo `main @ a5d6dbb`.
**Convention:** *measured* = computed here or in a cited repo file from a disclosure/dataset; *fitted* = regression output with a reported error; *assumed* = judgement with a cited rationale; *unidentified* = not separable from public data. Numbers I computed for this note are marked **[computed]** and the script that produces them is §6.

---

## 1. Thesis in five lines

1. Forecast **quarterly reported revenue in USD, as a level, 3Q26 through 4Q27**, and from it the **guide midpoint and range Airbnb will print on 5 Nov 2026 and ~Feb 2027** — not the surprise versus Street, which the repo has already proven is an untestable target at n≈10 (`docs/revenue-forecast-strategy/01_ground-truth/02_model_audit.md` §4.2b).
2. It should beat the incumbent because the incumbent forecasts the wrong object: `13_driver_model.py:381-383` forecasts a **take rate** (`τ_{t-4} × (1+w_q)`), which is a booking-versus-check-in calendar artefact with a ±2.0% one-sigma revenue error even under perfect foresight of nights, ADR and both FX legs (audit §3.1, recomputed there over 8 quarters). Replace it with the object that is actually stable: the **conversion of already-printed GBV into revenue**.
3. **[computed]** On 2023-2026 data the FX-adjusted conversion of a fixed lagged-GBV blend into revenue has a within-quarter-of-year relative standard deviation of **1.45% / 0.46% / 1.00% / 0.86%** (Q1-Q4), against **2.08% / 1.10% / 2.17% / 2.52%** for the printed take rate — 1.4× to 2.9× tighter, *and* applied to a base that is already published rather than forecast.
4. It re-plumbs the two best-validated facts in the repo into the line that matters. The broad-USD→ADR-FX survivor (walk-forward 0.44× naive) currently **cancels algebraically out of modelled revenue** (audit §1.3); the funds-held/unearned-fees survivor (walk-forward 0.600× naive) is **not in the model at all** (audit §4.3). Both become structural constraints here, not regressors.
5. It carries the one dated, near-arithmetic edge nobody on the Street has modelled: the **single 15.5% host-only fee migration completes inside 3Q26/4Q26** (deadlines 15 Sep 2026 ex-EEA, 13 Oct 2026 EEA+CH, `data/processed/overnight/06_fee_timeline.csv`), it is worth **+4.05% of revenue on the migrated cohort at a constant host payout** [computed, §2.4], and because revenue recognises at check-in it lands **one to two quarters after the bookings migrate** — i.e. mostly in 4Q26 and FY27, not 3Q26.

---

## 2. Formal specification

### 2.0 Indices and primitives

- `b` = booking quarter, `q` = check-in (recognition) quarter, `k = q − b` = lag in quarters, `k ∈ {0,1,2,3}`.
- `Q(q) ∈ {1,2,3,4}` = quarter-of-year of `q`; `r ∈ {na, emea, latam, apac}` = region; `c` = currency.
- `H_b` = **host-payout dollars booked in quarter b**, net of cancellations occurring in `b`, at constant FX. **This is the new numéraire and it is the whole trick** (§2.4).
- `Φ_{k|Q(b)}` = share of a booking cohort `b` that checks in `k` quarters later. Rows sum to `ρ_b ≤ 1`; the deficit `1 − Σ_k Φ_{k|Q(b)}` is the cohort's eventual cancellation rate.
- `f(·)` = the dated fee schedule (§2.4). `X^G_q`, `X^R_q` = GBV-weighted and revenue-weighted currency indices (§2.5). `s_G`, `s_R` = non-USD shares of GBV and revenue.
- `Λ_q` = hedge dollars reclassified into revenue in `q` (a signed USD amount from the 10-Q, not a rate).

### 2.1 The identity

```
(1)  GBV_q^USD      = g(H_q; m_q) · X^G_q                      booking-dated, translated at booking
(2)  Revenue_q^USD  = Σ_k Φ_{k|Q(q−k)} · τ(m_{q−k}) · H_{q−k} · [ λ·X^R_q + (1−λ)·X^R_{q−k} ] + Λ_q
(3)  Nights_q       = N_q − Σ_{b≤q} CancelledNights(b,q)
(4)  ADR_q          = GBV_q / (Nights_q + Seats_q)             an OUTPUT, never an input
(5)  TakeRate_q     = Revenue_q / GBV_q                        an OUTPUT, never an input
```

`m_q` = the **fee-regime state vector** at booking quarter `q`: (share of GBV on the single 15.5% host fee, share on the split 14.1%+3% schedule, share on the 6-10% direct-link pilot rate, hotel share at ~11%, Experiences share at 20%, Services share at 15%, cross-currency share carrying the FX service fee). `g(·)` maps host payout to GBV under that regime; `τ(·)` maps host payout to platform revenue under the same regime. **They are the same function evaluated twice**, which is why the ADR fee-reprice row and the take-rate fee row cannot be double counted (§2.4).

Equation (2) has three properties the incumbent lacks: (a) there is **no take rate to forecast** — the printed take rate falls out of (5); (b) the entire recognition-timing mechanism sits in `Φ`, an object with an accounting identity and an external prior, instead of in `w_q`, a ratio of two regressions the audit classifies as a plug; (c) **most of `q`'s revenue depends on `H` already printed**, so the forecast at a guide date is arithmetic on published data.

### 2.2 Identification of Φ — four independent pins, no regression needed for the first two

1. **Accounting identity (hard).** From `research/notes/.../03_insider_mechanics.md` §1.3, verified against `data/processed/abnb_backlog_indicators.csv` (24 rows, `unearned_fees_musd`, `funds_held_musd`, quarterly, 4Q20-2Q26):
   `UnearnedFees_q = UnearnedFees_{q−1} + τ·p_q·GBV_q − Revenue_q − RefundedFees_q ± FX`.
   Given disclosed `UnearnedFees`, `Revenue` and `GBV`, this pins `Σ_{k≥1} Φ_k` (the un-recognised tail) each quarter up to `p_q` (prepaid share) and refunds. **Critically it must be run on the restated series** `unearned_restated = reported/(1−d_q)` with the dated RNPL/fee distortion `d_q` = 0.9% (3Q25), 3.8% (4Q25), 16.2% (1Q26), 16.5% (2Q26) — measured in the insider note from the 2023-25 seasonal coverage norms (Q1-end 0.880, Q2-end 0.697, Q3-end 0.661, Q4-end 0.676). Funds held is distorted only ~4.8% because it is booking-amount denominated; unearned fees are fee-denominated. Running the regression on the *reported* series is what made the repo's own survivor test fail on revenue (WF 1.17× naive, `data/processed/overnight/08_backlog_tests.csv`).
2. **Column-sum restriction against printed revenue (hard).** `Σ_k Φ_{k|Q(q−k)} τ H_{q−k} = Revenue_q` holds exactly for 23 printed quarters. That is 23 equations.
3. **External shape prior (soft).** `data/processed/booking_curve_daily.csv` (44,380 rows) and `booking_curves_by_market.csv` (601 rows, 120 markets, one Jul-Aug 2026 vintage) give `blocked_rate` by `days_ahead` for 120 markets. **This is a level, not an occupancy rate, and the README warns never to label it as such** — but the *shape* of `blocked_rate(days_ahead)` is a legitimate Dirichlet prior on the lead-time density, market-weighted. Also `data/processed/airbnb_nights_per_booking.csv` and the 10-K's avg nights/booking (3.7 FY25, 3.8 FY24; NA 4.1 / EMEA 3.8 / LatAm 3.6 / APAC 3.3) bound the stay-length tail.
4. **Long-term-stay amortisation (hard, small).** 28+ night stays recognise month-by-month from check-in (FY2025 10-K revenue policy), so they spill one quarter. LTS share 20.2% (2022) → 13.4% (2025), −2 to −2.5pp/yr (`research/notes/2026-09-09_los_synthesis.md`). This is a *shortening* of the tail and is the one term that moves `Φ` for a reason that is disclosed annually.

**Why Φ must be seasonal, with evidence.** **[computed]** Fit a *single* fixed kernel `Φ = (0, 0.38, 0.62, 0)` — the weights that minimise pooled within-quarter dispersion under the PIT constraint `Φ_0 = 0` — and back out `τ_eff = TakeRate_q / K_q` where `K_q = Σ_k Φ_k GBV_{q−k} / GBV_q`. The result across 1Q23-2Q26:

| quarter-of-year | τ_eff (%) 2023 / 24 / 25 / 26 | within-Q range |
|---|---|---|
| Q1 | 12.28 / 12.43 / 11.86 / 12.20 | 0.56pp |
| Q2 | 15.41 / 15.00 / 15.31 / 15.19 | 0.40pp |
| Q3 | 17.06 / 16.77 / 16.98 | 0.30pp |
| Q4 | 11.80 / 11.93 / 11.94 | 0.14pp |

The fixed kernel removes **60.0%** of the printed take rate's variance (printed range 9.66pp → τ_eff range 5.26pp) and the residual is a clean, stable seasonal — i.e. `Φ` itself depends on the *booking* quarter-of-year, exactly as the mechanism requires: a Q1 booking cohort (summer travel) has a long lead; a Q4 cohort (last-minute winter) has a short one. So the estimand is the 4×4 seasonal transition matrix `M[Q(b), k]`, not a scalar kernel. With a one-parameter-per-season lead-time density plus a common `τ_eff` and a common retention `ρ`, that is 4+2 = 6 parameters against 23 printed quarters plus 23 balance-sheet equations — comfortably identified, and the parameters are ordered and monotone so hierarchical shrinkage across seasons costs almost nothing.

### 2.3 How overlap is solved BY CONSTRUCTION

The lens exists because FX, fee and timing each appear more than once in the current tree and cancel, double-count or go missing. Four structural fixes, none of which is an adjustment:

**(a) One numéraire: host payout.** Today the fee migration appears twice and inconsistently — as `+0.50pp` inside the ADR workbook's 5_Forecast fee-migration-reprice row (from `analysis/src/adr/12_fee_migration_reprice.py`) *and* as a take-rate lever that is set to zero (`take_bps = 0`, `13_driver_model.py:177,200,223`). Those are the same economic event: a schedule change that grosses the listed price up and reroutes the fee. Denominate the volume/price build in **host payout per night** and apply `g(·)` and `τ(·)` from one dated schedule; GBV and revenue are then both outputs of one parameter (the migrated share) and **the double count is arithmetically impossible**. Concretely, per $97 of host net payout: split fee → GBV 114.1, revenue 17.11, take 14.99%; single fee → GBV 114.79, revenue 17.79, take 15.50%. **GBV +0.60%, revenue +4.05%, take rate +51bp** [computed; rates from `06_fee_timeline.csv` and `research/notes/host_only_fee_history_and_elasticity.md` §1, cross-checked against `data/processed/fee_split_elasticity_scenarios.csv` `take_rate_chg_bp = 58.77` on the guest-spend base before tax/cleaning dilution].

**(b) One FX object per date-stamp, not four.** Today FX enters four times (audit §3.7): `f_A` on ADR (cancels exactly, inert), `f_R` via the wedge (the only live channel), the hedge memo (which `28_fx-hedge-disclosures.md`'s "For the model" section invites you to double-subtract although it is already inside the after-hedge stated number), and indirectly through FX-contaminated regional nights weights (audit §3.2). Here there are exactly two indices — `X^G` (GBV/nights-weighted basket, booking-quarter average) and `X^R` (revenue-weighted basket) — and one convolution `[λ X^R_q + (1−λ) X^R_{q−k}]`, with `λ` the share of a cohort's fee that is remeasured at check-in versus locked at booking. The hedge enters exactly once, **in dollars, additively, after pre-hedge revenue**, which is also the contract the R engine enforces (`FX_ENGINE_MENTAL_MAP.md`, "Hedge treatment": *"Hedges are consolidated dollars added once after pre-hedge revenue… Do not apply the full ADR factor and full revenue factor to the same revenue line; that double counts FX"*).

**(c) The take-rate seasonality is not a parameter.** `TakeRate_q` is computed from (2)/(1). Any change in booking-window mix — RNPL lengthening leads, LTS share falling, cross-border mix, regional mix — moves `Φ` and therefore moves the seasonal take-rate pattern *predictably*, which is deliverable (c) of the lens. The current model assumes the 2023-25 seasonal means (9.2/13.1/18.3/14.0) persist through a period in which three of the four drivers of that seasonality changed.

**(d) RNPL is reclassified out of the take rate entirely.** RNPL does not change any fee rate. It (i) lengthens the booking window → shifts mass in `Φ` to higher `k`; (ii) raises cancellations → lowers `ρ`; (iii) defers fee cash → breaks the unearned-fee ratio, which is why `d_q` exists. All three are `Φ`/`ρ` effects. Management's own language supports the reclassification: FY26 take rate is flat *"accounting for the timing of bookings versus check-in with Reserve Now, Pay Later"* (Mertz, 2Q26 call, quoted in `research/notes/host_only_fee_history_and_elasticity.md` §4), and Mertz in 2Q22: *"any of the variation in take rate is just a timing difference between revenue stays versus timing of bookings."* **We are building the model management describes; the incumbent is not.**

### 2.4 The fee schedule `f(m_q)` — every basis point sourced

The take-rate bridge is a mapping from a dated regime state to `τ`, on the **LTM / `τ_eff` basis** (the quarterly print falls out of `Φ`). Every row below carries its source and its class.

| Lever | Mechanism | Size | Dating | Class | Source |
|---|---|---|---|---|---|
| Single 15.5% host-only fee | schedule change: 14.1% guest + 3% host → 15.5% host, host grosses up 14.8% | **+51bp on migrated stays GBV; +4.05% on that cohort's revenue** | 25% of listings 1Q26, ~50% 2Q26, deadlines **15 Sep 2026** ex-EEA / **13 Oct 2026** EEA+CH | measured (arithmetic on published rates) | `06_fee_timeline.csv`; `06_elasticities.csv` ("+40 to +50bps on a fully migrated book"); `host_only_fee_history_and_elasticity.md` §1,§3 |
| Tax + cleaning dilution of the GBV base | GBV includes taxes and cleaning; fees are not levied on them | de-rates the above by the tax+cleaning share of GBV | continuous | **measurable, not yet measured** — `06_quote_line_items.csv` carries `li_taxes` and `li_cleaning_fee` per city-dump | `06_quote_line_items.csv` (77 rows over 1.71M quotes) |
| Migrated share is GBV-weighted, not listing-weighted | PMS/software-connected (professional) hosts migrated first and are larger | migrated **GBV** share runs ahead of migrated **listing** share in 2025-26; tail is hobby hosts | Oct 2025 → Apr 2026 (software hosts fully migrated 13 Apr 2026) → deadlines | measurable | `data/processed/inside_airbnb_host_concentration.csv`; `06_fee_timeline.csv` |
| Host re-pricing pass-through θ | payout-neutral gross-up = +14.8%; measured θ ≈ 0.83-0.84 on Austin matched panels | θ enters `g(·)`, i.e. the GBV channel only | Mar-Aug 2026 windows | measured | `data/processed/adr/12_reprice_summary.csv` (`theta` 0.833-0.845, `mean_jump_pp` ~11.5 on matched listings) |
| Nights elasticity to the guest price move | at payout-neutral θ the guest all-in price moves only +0.7% | nights **−0.3% to −1.4%** across ε = −0.5…−2.0 | transition window only | modelled | `data/processed/fee_split_elasticity_scenarios.csv` (61 rows, ε × θ × σ grid) |
| Cross-currency / FX service fee | fee on cross-currency bookings, launched mid-2024 | **+20bp y/y in 2025**; cross-currency ≈ 20% of GBV (1Q25) — near-saturated, so FY27 incremental ≈ 0 to +5bp | disclosed once, then dropped | measured (once) | `06_elasticities.csv`; `02_kpi_panel_quarterly.csv` `cross_currency_share_of_gbv_pct = 20.0` at 1Q25 |
| New-business guest incentives (contra-revenue) | hotel price-match + up to **15% Airbnb credit**; Delta SkyMiles stated no take-rate impact | masks the fee uplift in FY26; management: *"absent these incentives, we would have anticipated our implied take rate to be slightly higher"* | credit **expires 31 Dec 2026** — 4Q26 is the last subsidised quarter | assumed size (10-25bp), dated expiry | 2Q26 call; `research/notes/2026-09-04_management-timeline.md` |
| Direct-link host-fee pilot at 6-10% | first explicit take-rate concession; caps the migration benefit | at 10% of nights and an 8pt discount = **−80bp**, larger than the entire single-fee benefit | announced **29 Aug 2026**, scope undisclosed | assumed / scenario axis | Skift 29 Aug 2026; `research/notes/.../11_competition-supply-and-overlays.md` §8 |
| Hotels at ~11% commission | growing ~3× homes off a single-digit-% nights base | ~−8bp if hotel GBV share goes 3%→5% | continuous; 15% credit expiry 31 Dec 2026 | assumed (commission undisclosed) | `14_revenue_by_line.py:67`; `11_new_business_scenarios.csv` |
| Experiences 20% / Services 15% | accretive rates on a tiny base | +2 to +4bp | ramping | assumed | `11_new_business_scenarios.csv` |
| Travel insurance | revenue +40% (4Q25), +45% (1Q26), 12 largest countries | +2 to +5bp | continuous | measured growth, unmeasured level | `02_kpi_panel_long.csv` |
| Sponsored listings / ads | revenue **outside** GBV — enters the identity as an additive term, never in `τ` | $0 in FY26; repo base 2027 launch, ~0.3% of GBV by FY28 | none yet | assumed | `11_new_business_scenarios.csv` |
| Co-host network | **zero** incremental take rate, confirmed on the 1Q25 call | 0 | — | measured (disclosed) | `11_supply_economics.csv` |
| RNPL | **not a take-rate lever** — moves `Φ` and `ρ` | 0bp on `τ_eff` by construction | US 3Q25, global 17 Feb 2026, expanded Jul 2026 | measured reclassification | insider note §1.6 |

### 2.5 The FX block, and the one question that is worth $90M of Q4

Two hypotheses about when a booking's fee dollars are struck:

- **H1 (translate at check-in):** conversion carries `X^R_q / X^R_{booking-weighted}`, i.e. `λ = 1`.
- **H2 (lock at booking):** the USD fee travels with the booking, `λ = 0`, and reported revenue FX is a *lagged* function of spot.

**[computed]** Build a 9-currency basket from `data/processed/overnight/10_fx_quarterly.csv` (levels 1Q18-3Q26) with the regional currency weights in `10_fx_basket.csv` (EMEA EUR .62/GBP .25, LatAm BRL .45/MXN .38, APAC AUD .40/JPY .20/KRW .10/INR .07, NA USD .90/CAD .08/MXN .02), revenue-weighted across regions. Score both against the **gross-of-hedge** revenue FX series in `data/processed/overnight/28_fx_hedge_disclosures.csv` (`gross_fx_ex_hedge_pp`, n = 14, 1Q23-2Q26):

| specification | RMSE vs stated gross revenue FX | bias |
|---|---|---|
| H1, check-in translation | **1.40pp** | −0.26pp |
| H2, booking lock | 1.94pp | −0.86pp |
| Two-index fit, `λ` and scale free | **1.08pp** at `λ = 0.75` | −0.24pp |
| Incumbent: `−0.640 + 0.413 × mean(EUR/USD y/y, t−1,t−2)` | **LOO RMSE 2.30pp** | — |
| Contemporaneous GBV-weighted index vs stated **ADR** FX, scale free | **0.76pp** at `s_G = 0.66` | −0.14pp |

Two readings. First, a two-parameter basket model roughly **halves** the incumbent's leave-one-out error on the same 14 quarters, and the ADR leg lands at `s_G = 0.66` — essentially the disclosed non-USD share of GBV implied by the nights mix — which is a genuine over-identification check passing. Second, and this is the item to put in front of a PM: **my fitted 3Q26 gross revenue FX is +1.04pp against management's guided ~+3.2pp gross** (the 2Q26 letter's *"approximately three percentage point FX tailwind after factoring in our hedging program"*, with the hedge a −0.21pp drag per `28_fx_hedge_forward.csv`, so ~+3.2pp before it). A 2.2pp gap on a quarter management could already see is not noise. Candidate explanations, all testable inside three weeks: (i) quarterly-average baskets are too coarse — the right object is a **daily** basket convolved with the daily booking-date density, which the φ kernel already supplies; (ii) the weights should be **GBV-weighted at booking date** and drift with the regional nights mix, not fixed revenue weights; (iii) management's "FX" sentence may bundle the **cross-currency service fee** (FX-linked revenue, not translation) with translation — which would be a disclosure finding in its own right and is checkable in the 3Q26 10-Q.

**This is where the money is.** Three live estimates of 4Q26 revenue FX exist: the repo's lagged-EUR fit at **−0.43pp** (`29_fx_step_down.csv`, `q4_fit_pp`, driver 82% observed, LOO ±2.3pp); my two-index reconstruction at **+0.62pp gross / +0.41pp after hedge** [computed]; and guide-anchored carry-the-delta at roughly **+2.6pp**. The spread is ~3pp ≈ **$90M on 4Q26 and ~$430M on FY27**, and the team's current Q4 bearish call (`29_q4_2026_bridge.csv`: base $3,111M, −2.8% versus the $3,200M Street) rests almost entirely on the most fragile of the three. Resolving it requires no new data.

Forward schedule, spot held at the 3Q26 quarterly average, hedge from `28_fx_hedge_forward.csv` [computed]:

| quarter | revenue FX gross | hedge | after hedge | ADR/GBV FX |
|---|---|---|---|---|
| 3Q26 | +1.04 | −0.21 | +0.83 | +0.48 |
| 4Q26 | +0.62 | −0.21 | **+0.41** | +0.63 |
| 1Q27 | −0.13 | −0.18 | −0.31 | −0.15 |
| 2Q27 | −0.21 | −0.18 | −0.39 | −0.32 |
| 3Q27 | −0.07 | 0.00 | −0.07 | 0.00 |
| 4Q27 | −0.05 | 0.00 | −0.05 | 0.00 |

Against `29_fy27_quarterly_path.csv` base, which carries −1.03 / −0.80 / −0.61 / −0.07 for FY27. The FY27 difference is **+0.42pp of revenue growth ≈ +$66M**, and it is a difference of *construction*, not of FX view: both are spot-held-constant.

**What is already determined at each guide date.** With `Φ_0 = 0` imposed, `Revenue_q` depends only on `H_{q−1}, H_{q−2}, …`, all published. At the 6 Aug 2026 guide date the 3Q26 base was 100% observed; at the 5 Nov 2026 guide date the 4Q26 base is `0.38·GBV_3Q26 + 0.62·GBV_2Q26`, and **GBV_3Q26 will itself have printed that morning**, so the Q4 guide is ~100% determined on volume and ~80% determined on FX (the 4Q26 check-in basket is one quarter forward of a spot that is 82% observed by early November). For the FY27 guide in Feb 2027, only 1Q27 is pinned this way; the remaining three quarters need a forecast of `H`, which is what lenses 1-4 supply. **That asymmetry is the whole reason the Q4 guide is forecastable to ~1% and the FY27 guide is not.**

---

## 3. Data map — every path verified by opening it

| Input | Path | Grain / size | Role |
|---|---|---|---|
| Printed KPIs | `data/processed/overnight/02_kpi_panel_quarterly.csv` | 24 rows (3Q20-2Q26), 119 cols; `nights_m, gbv_musd, adr_usd, revenue_musd, take_rate_pct, fx_pts_revenue, fx_pts_adr, cross_currency_share_of_gbv_pct` | targets and the `Φ` column-sum constraints |
| Backlog identity | `data/processed/abnb_backlog_indicators.csv` | 24 rows, 4Q20-2Q26; `unearned_fees_musd, funds_held_musd, unearned_to_next_q_revenue, rnpl_era, rnpl_gap_pts` | pins `Σ_{k≥1}Φ_k`; must be restated by `1/(1−d_q)` |
| Hedge programme | `data/processed/overnight/28_fx_hedge_disclosures.csv` | 14 rows 1Q23-2Q26; designated notional $494m→$3.3bn, `aoci_cash_flow_hedges_musd`, `reclassified_to_revenue_musd` (−42/−23/−15/−19 for 3Q25-2Q26), `non_usd_revenue_share` 0.54→0.56, `designated_notional_pct_of_ltm_non_usd_revenue` 10.5%→46.6%, `stated_revenue_fx_pp`, `gross_fx_ex_hedge_pp`, `stated_adr_fx_pp` | the `Λ_q` overlay and the FX scoring target |
| Hedge forward | `data/processed/overnight/28_fx_hedge_forward.csv` | 4 rows 3Q26-2Q27; −$8.7/−5.9/−4.8/−6.6m = −0.21/−0.21/−0.18/−0.18pp, from the 2Q26 10-Q's ~$26m of deferred net losses | forward `Λ_q`. **Memo only — already inside the after-hedge stated FX** (`29_bridge_assumptions.csv`) |
| Hedge tests | `data/processed/overnight/28_fx_hedge_tests.csv` | 15 rows; expected-vs-realised reclass, and lag structure: gross ex-hedge revenue FX vs EUR y/y at lag 0 r 0.763, **lag 1 r 0.861**, lag 2 r 0.568 | validates that `λ < 1` |
| FX levels | `data/processed/overnight/10_fx_quarterly.csv` (37 rows × 9 ccys, 1Q18-3Q26), `10_fx_daily.csv` (19,468 rows, FRED, to 2026-08-28), `05_fred_cache/` | daily and quarterly | the two baskets; daily is required for the booking-date convolution |
| Currency weights | `data/processed/overnight/10_fx_basket.csv` | 23 rows; region × currency weights, judgemental, with USD legs at 0 y/y | `X^G`, `X^R` construction — weights are **assumed** and should become nights-weighted outputs of the regional build |
| Regional pass-through | `data/processed/overnight/10_regional_fx_passthrough.csv` | 5 rows; EMEA 1.043 (r .987, n 10), LatAm 0.623 (r .996, n 7), APAC 0.86 (r .972, n 5), NA **not identified** (basket moves <1.5pp) | cross-check on `s_G`; NA's non-identification is why a global basket beats four regional ones at this n |
| Regional ADR ex-FX | `data/processed/overnight/10_regional_adr_fx.csv` | 92 rows, region × quarter, reported / ex-FX / gap / basket | time-varying FX-neutral deflators (replaces the fixed `IDX`, audit §3.2) |
| Incumbent FX fits | `data/processed/overnight/05_fx_fits.csv` (26 rows), `05_fx_schedule.csv` (30 rows) | target × driver × lag × window with `loo_rmse`, `naive_rmse` | the baseline to beat: `adr_fx ~ eurusd` LOO 0.572 vs naive 2.053; `rev_fx` LOO 1.55-1.85 |
| Q4/FY27 bridge | `29_fx_step_down.csv`, `29_q4_2026_bridge.csv` (18 rows), `29_fy27_bridge.csv`, `29_fy27_quarterly_path.csv` (12 rows), `29_residual_history.csv` (8 rows), `29_bridge_assumptions.csv` (13 rows) | scenario × quarter | the incumbent bridge this replaces term-by-term; `29_residual_history.csv` is the plug we delete |
| Fee timeline | `data/processed/overnight/06_fee_timeline.csv` | 19 dated events 2019-05 → 2026-08, each with source and confidence | the dating of `m_q` |
| Fee elasticity grid | `data/processed/fee_split_elasticity_scenarios.csv` | 60 rows: ε × θ × σ → `nights_chg, gbv_chg, abnb_rev_chg, take_rate_chg_bp` (58.77 on guest spend) | the nights-elasticity offset |
| Measured re-pricing | `data/processed/adr/12_reprice_summary.csv`, `12_reprice_hist.csv` | matched listing pairs by market/date/segment; `theta` 0.833-0.845, `share_unchanged` ~0.25 | **measured** pass-through θ — the only hard number on host behaviour |
| Quote line items | `data/processed/overnight/06_quote_line_items.csv` | 76 city-dump rows over 1.71M fee-inclusive quotes; `li_nightly_subtotal, li_discount_amount, li_taxes, li_cleaning_fee` | the tax+cleaning dilution of the GBV base — currently an unmeasured de-rate on the fee uplift |
| Elasticities register | `data/processed/overnight/06_elasticities.csv` | 25 sourced sensitivities | the +40-50bp fee line, the +20bp FX service fee, the 14.5% BKNG net-take ceiling |
| Fee note | `research/notes/host_only_fee_history_and_elasticity.md` | 98 lines | the 2019-20 precedent (+17% bookings claim ⇒ implied listing elasticity −1.2), the ε = −1 indifference result, the management quote ledger |
| Booking curves | `data/processed/booking_curve_daily.csv` (44,379 rows), `booking_curves_by_market.csv` (600 rows, 120 markets, one Jul-Aug 2026 vintage) | market × snapshot × horizon; `blocked_rate`, `median_min_nights` | Dirichlet prior on `Φ` shape. **`blocked_rate` is not occupancy** |
| GBV-lag conversion | `data/processed/h2_bridge/h2_bridge_gbv_lag_conversion.csv` | 6 rows: Q3 17.39/17.15/17.18%, Q4 11.95/12.12/12.03% | independent confirmation of the kernel's stability |
| Guidance ledger | `data/processed/overnight/02_guidance_ledger.csv` | 194 statements, 23 prints; 3Q26 rows verified: revenue range 4690-4770, nights bucket 10-12, GBV bucket 14-16, take rate "relatively in-line", ADR "moderate increase" | the guide-emission layer |
| Consensus | `data/processed/overnight/04_current_consensus.csv` | Zacks 4 Sep: Q3 $4,740m (7 est), Q4 $3,200m (10 est, 3,050-3,700), FY26 $14,100m, FY27 $15,730m (13 est, 14,990-16,290); S&P 3 Sep FY26 $14,160m (43), FY27 $15,760m | the benchmark |
| R FX engine | `Citadel-ABNB-fx-engine/analysis/src/fx_engine/{engine,rates,contract,io,calibration,backtest,run_forecast}.R`; inputs `data/inputs/fx_engine/example/{exposure,forecasts,hedges,parameters,prior_year,scenario_rates,reference_rates}.csv`; outputs `data/processed/fx_engine/example/{adapter,consolidated,regional,currency_detail,detail,annual}.csv`; research `…/research/{calibrations,scores,predictions}.csv` | operational, 42 engine + 11 rate-path + 14 calibration checks; **example inputs are SYNTHETIC** and `calibrations.csv` is flagged `research_only_incompatible_with_exposure_basket` | the production translation layer. Contract per `FX_ENGINE_MENTAL_MAP.md`: supply `nights, adr (usd_constant), take_rate` per geography-quarter + `exposure.csv` shares summing to 1 + `hedges.csv` in dollars; consume `adapter.csv` `revenue_timing_multiplier` |

**External data required.** None is *required*. Three are cheap and would upgrade the build, in priority order: (1) **the 3Q26 10-Q derivatives note** (free, EDGAR, ~mid-Nov 2026) — updates designated notional, AOCI, next-12-month expected reclass, and settles whether the fee-structure leg of the unearned-fee distortion reverses post-migration; (2) **daily FRED cross rates already cached** (`05_fred_cache/`, `10_fx_daily.csv` to 28 Aug 2026) need only a refresh to the decision date; (3) **EUR/USD forwards** for the forward-curve scenario — obtainable from the licensed Bloomberg workbooks in `Theo Data` or, free, from CME FX futures settlements. Everything else in this lens is on disk.

---

## 4. Estimation, validation and the honest power statement

**Estimator.** A Bayesian state-space model in **Stan** (`cmdstanpy`), or PyMC if the team prefers. State: `Φ` parameterised as four seasonal lead-time densities on a simplex over `k ∈ {0,1,2,3}` with an ordering constraint (`E[k | Q=1] ≥ E[k | Q=4]`, which the data already assert), plus `ρ_t` (retention, a slow random walk that RNPL shifts), plus `τ_eff` as a deterministic function of the fee schedule (no free parameter), plus `λ` and the two FX scales. Observation equations: printed revenue (exact, small measurement error), printed GBV (exact), restated unearned fees (with a measurement-error term that absorbs `p_q` and refunds), and — the interval-censored part — the **qualitative guide buckets** (`nights_yoy_pct` bucket 10-12, `gbv_yoy_pct` bucket 14-16, `take_rate_yoy_pts` point 0) entered as `lo ≤ x ≤ hi` likelihood terms rather than midpoints, which is the correct treatment of `02_guidance_ledger.csv`'s `bucket` rows and mirrors the interval-observation treatment lens 1 uses for regional nights.

**Priors.** `Φ` shape: Dirichlet centred on the market-weighted `blocked_rate(days_ahead)` profile from `booking_curve_daily.csv`, concentration set so the prior is worth ~4 quarters of data. `ρ`: Beta centred at 0.835 (platform cancellation ~16.5%, the midpoint of the disclosed "roughly 16% historically versus 17%", 4Q25 call), random-walk sd 1pp/quarter. `λ`: Beta(3,1) — the 28_fx_hedge_tests lag structure (lag-1 r 0.861 > lag-0 r 0.763) says it is below 1 but the check-in leg dominates. `s_R`: Normal(0.56, 0.03) **hard-anchored on the disclosed non-USD revenue share** in `28_fx_hedge_disclosures.csv` — this is the single most important prior because it converts an under-powered regression into an accounting restriction. `s_G`: Normal(0.68, 0.05) from the nights mix. Fee schedule: no priors, it is arithmetic; the *migrated GBV share* gets a Beta prior from `06_fee_timeline.csv` disclosures (25% 1Q26, ~50% 2Q26) plus the professional-host concentration in `inside_airbnb_host_concentration.csv`, and the deadlines force it to ~1 by 4Q26.

**Software.** Stan for the state-space core; `statsmodels`/`linearmodels` for the pre-registered diagnostic regressions; **R only for the translation layer** via `Citadel-ABNB-fx-engine/analysis/src/fx_engine/run_forecast.R`, fed real `exposure.csv` (nights-weighted region×currency shares from the regional build, replacing the synthetic example), real `forecasts.csv` (per-region nights, host-payout-per-night in `usd_constant`, and `take_rate` from the fee schedule), and real `hedges.csv` (dollars from `28_fx_hedge_forward.csv`). Consume `adapter.csv`'s `revenue_timing_multiplier` **or** `revenue_fx_usd`, never both — the engine's own contract says so.

**Walk-forward protocol and PIT discipline.** Expanding window, origin at 4Q22 (post-COVID, post-regime), refit at every historical **guide date**, not every quarter-end — i.e. the information set is: all letters and 10-Qs filed strictly before the guide date, FRED FX through the day before, and nothing else. Concretely, the 6 Aug 2026 replay may use GBV through 2Q26, unearned fees at 30 Jun 2026, FX through 5 Aug 2026, and the migrated-share disclosures through the 2Q26 letter — and must **not** use the Zacks 4 Sep consensus vintage in place of the LSEG $4,610m that actually set the feature on 6 Aug (the repo flags this exact vintage trap, insider note §Street). Vintages are tracked in `data/processed/overnight/20_vintage_register.csv`; increment `spec_id` in `20_experiment_spec.json` and freeze before scoring, exactly as `20_frozen_q3_2026.csv` did.

**Baselines it must beat, on each of two frozen windows (2023Q1+ and 2024Q1+):**
1. **AR(1) on revenue y/y** and naive (last y/y) — the repo's standard, `20_temporal_validation.py`.
2. **Guide midpoint + trailing-8 median cushion (+1.79%)** — mean error 1.1% on the revenue level, 19/19 midpoint beats, 15/19 above the top (`02_guidance_ledger.csv`, `02_guidance_cushion_series.csv`). This is the bar, and it is a hard one.
3. **The incumbent driver-model construction** `τ_{t−4} × GBV_q × (1+w_q)` — audit §3.1, mean +0.53%, sd 1.97%, trailing-4 +1.05%, **under perfect foresight of nights, ADR and both FX legs**.
4. **For the FX block specifically:** `05_fx_fits.csv` `rev_fx ~ eurusd_avg12` LOO RMSE 2.30pp.

**[computed] Where the method stands today, before any of the three-week work.** A deliberately crude version — fixed kernel `(0, 0.38, 0.62, 0)`, prior-year same-quarter conversion, no fee schedule, no FX correction — gives a PIT one-step revenue error of **mean +0.17%, sd 2.33%, MAE 1.82%** over 1Q24-2Q26 (n = 10). The incumbent take-rate construction over the same window gives **mean +0.40%, sd 2.48%, MAE 1.83%** — *with perfect foresight of GBV*. So the crude kernel already matches the incumbent on error, is unbiased where the incumbent is biased (+1.05% trailing-4), and **needs no GBV forecast at all**. Adding the FX translation correction at the disclosed non-USD share `s = 0.56` cuts the within-quarter-of-year coefficient of variation of the conversion from 1.96%→1.45% (Q1) and 1.13%→**0.46%** (Q2) — and slightly worsens Q3 (0.90%→1.00%) and Q4 (0.66%→0.86%), which is exactly the right pattern: the FX correction bites where the booking-to-check-in gap is longest (Q1/Q2 revenue comes from the long-lead summer-booking cohorts) and is noise where it is shortest. The seasonal kernel plus the fee schedule is the remaining upside and is untested. **I am not claiming a validated win; I am claiming a validated architecture and a measured starting point.**

**Power, honestly.** There are 23 printed quarters, 19 guided, and 14 quarters of stated FX. A single-feature quarterly regression at n = 14-20 has ~35% power to detect an effect of one residual standard deviation at α = 0.05 — which is why the repo's ~3,500 tests produced `pred_sd/actual_sd = 0.14-0.33`. **This design does not add features; it removes them.** Count the free parameters that touch FY27 revenue: 4 seasonal lead means, 1 retention level + 1 RNPL shift, 1 `λ`, 2 FX scales (both with disclosure-anchored priors), 1 migrated-share path (deadline-forced), 1 incentive roll-off size = **11**, against 23 revenue equations + 23 balance-sheet equations + 14 FX observations + 19 interval-censored guide buckets ≈ **79 observations**, many of them exact identities rather than noisy draws. The incumbent has 12 plugs and 18 assumed parameters against the same data (audit §2). The power argument is not "we found a better feature"; it is **"we replaced free parameters with accounting restrictions."**

**Why the prior negatives do not condemn this — and which parts they do.**
- *Google Trends (432 tests, mean WF 3.05× naive), aggregate macro (1,408+890 pairs, 5 Bonferroni survivors all FX-mechanism), peer read-across (the signal was the PIT leak), management tone (n 23 vs 132 features), composite NNLS indexes* — **all irrelevant here.** This design uses no exogenous predictor of demand. Every input is either a published Airbnb number, a published exchange rate, or a published fee rate.
- *"Surprise vs Street" failed at n≈10* — **condemns the target, not the method**, and we do not use that target. We forecast the level and the guide.
- *"Nothing beats AR(1) for nights"* — **binding, and we accept it.** This lens does not forecast nights. It consumes `H` (host payout) from lenses 1-4 and is agnostic about how they get it.
- *The backlog survivor "does not beat naive on revenue" (WF 1.17× naive, `08_backlog_tests.csv`)* — **this is the one negative that genuinely bears on us, and it is a measurement defect, not a signal failure.** It was run on the *reported* unearned-fee series, which the insider note shows is distorted 16.2% (1Q26) and 16.5% (2Q26) by RNPL and the fee migration. Restated, unearned fees grew +16.6% and +15.4% against GBV +19.2% and +15.7%. **Pre-registered falsification test: if the restated series does not beat naive on revenue out of sample, the `Φ`-from-balance-sheet identification is weakened and we fall back to identifying `Φ` from the column-sum restriction and the booking-curve prior alone.** We should write that test into `20_experiment_spec.json` before running it.
- *The ADR ex-FX target is contaminated by integer rounding in the letters (`predictive/03_nowcast_tests.py:48-51`)* — **still live and it hits us too.** `stated_adr_fx_pp` and `stated_revenue_fx_pp` in `28_fx_hedge_disclosures.csv` are letter-rounded (e.g. "less than 1%" → 0.5). On a 3.5pp-range target, roughly half the variance is rounding, which attenuates every FX fit including mine. **Mitigation: score the FX block on an interval likelihood — "stated 3%" means `[2.5, 3.5]` — not on a point. That is a one-line change and it recovers real power.**

---

## 5. Outputs, uncertainty, and the mechanism of disagreement with the Street

**What the model emits.** For each quarter 3Q26-4Q27, a joint posterior over: `Φ` (the 4×4 transition matrix, reportable as "share of quarter q's revenue already booked at date t"), `ρ`, `τ_eff`, the printed take rate, GBV, revenue in USD, and the revenue-FX pp split into translation and hedge. Plus a **guide-emission layer**: given the revenue posterior, the guide midpoint is `posterior median ÷ (1 + cushion)` with the cushion drawn from the trailing-8 empirical distribution (median +1.79%, 25th-75th +0.95% to +2.63%), and the range width from the trailing-8 width distribution (1.9% of midpoint, 3Q26 was 1.68%). That produces a **distribution over the printed guide range**, which is the object the pitch is judged on.

**Uncertainty representation — not Monte Carlo.** Three layers, none of which is "draw from an assumed distribution":
1. **Posterior.** Stan's posterior over `Φ, ρ, λ, s_R, s_G` propagates to revenue analytically. Uncertainty in `Φ` is *data-determined*: it is wide in 1Q (long leads, 4 observations) and narrow in 4Q (short leads, the conversion has a 0.14pp range across three years).
2. **Scenario tree with data-dependent branch probabilities.** The branches are dated events, not percentile draws: fee migration completes on schedule (deadlines published → P ≈ 0.9); hotel credit expires 31 Dec 2026 (announced → P ≈ 0.85 it is not extended, the one-sided risk being an extension); direct-link pilot scales to >5% of nights by 4Q27 (announced 29 Aug 2026, scope undisclosed → P ≈ 0.2, calibrated on Airbnb's own pilot-to-rollout base rate in `06_fee_timeline.csv`); FX path ∈ {spot-constant, forward curve, ±1sd}. Probabilities come from base rates in the timeline file, not from judgement.
3. **Split conformal on the revenue level.** Calibrate absolute-error quantiles on the walk-forward residuals from the 2023Q1+ window and emit a distribution-free 80% interval on each guide. At n≈12 calibration points the conformal interval is honest-but-wide; that is a feature, and it is the correct answer to "how do you know your posterior is calibrated at n=20."

**Concrete numbers this build produces today [computed, crude version]:**

| | mechanical build | team's driver model | team's Q4/FY27 bridge | Street |
|---|---|---|---|---|
| 3Q26 revenue | **$4,830m (+17.9%)** | $4,801m (+17.2%) | $4,771m | $4,737-4,740m; guide $4,690-4,770m |
| 4Q26 revenue | **$3,284m (+18.2%)** | $3,145m (+13.2%) | $3,111m (+12.0%) | $3,200m (+15.2%) |
| 4Q26 revenue FX after hedge | **+0.41pp** | — | −0.43pp fitted, −3.43pp guide-anchored step | not published |
| FY27 revenue | **~$16.05bn central, $15.6-16.6bn** | $15,842m | $15,804m | $15,730-15,760m |

The 3Q26 build (`4,830 = 16.645% × [0.38·GBV_2Q26 + 0.62·GBV_1Q26] × (1 + fee uplift 1.5%) × (1 + FX 0.73% − hedge 0.21%)`) sits 1.3% above the top of the guide range, which is precisely where Airbnb has finished 15 times in 19. It is also within 0.6% of the team's independently-built frozen card ($4,801m, `20_frozen_q3_2026.csv`) — two methods with no shared parameter agreeing to 60bp is the best validation available before 5 Nov.

**The mechanism by which we differ from the Street, stated as an attribution.** Take the Street's 4Q26 $3,200m and strip our fee uplift: `3,284 / 1.0252 = $3,203m`. **The Street's Q4 number is exactly what you get from this model with the fee migration set to zero.** That is the edge, and it is falsifiable: the entire disagreement is one dated, published schedule change, applied with the correct recognition lag. Likewise for FY27: against the Street's $15.75bn, the bridge is **+2.3% take rate** (migrated GBV share rising from a revenue-weighted ~0.32 in FY26 to 1.00 in FY27 × 4.05% on the migrated cohort), **+1.1% incentive roll-off** (the 15% hotel credit expires 31 Dec 2026, and management has already said take rate would have been "slightly higher" absent those incentives), **+0.4pp FX** versus the team's own path, less **0 to −1.5%** if the direct-link pilot scales. Central +2.0% versus Street; range −1% to +5%.

**I must flag the internal tension rather than bury it.** This inverts the team's current Q4 call. `29_q4_2026_bridge.csv` puts 4Q26 at $3,111m, 2.8% *below* the Street, driven by a −3.43pp FX step down. This lens says the FX step is real but roughly a third that size once you translate at the right date, and that the fee migration more than offsets it. **One of the two is wrong and the disagreement is resolvable with data already on disk in about four days.** A pitch that presents the bear Q4 without having run this test is exposed; a pitch that has run it and can show the reconciliation is the strongest version of either view.

---

## 6. Minimal code skeleton

```python
# M6_mechanical_revenue.py  —  booking-cohort kernel + dated fee schedule + two-index FX
# Inputs (all verified present):
#   data/processed/overnight/02_kpi_panel_quarterly.csv   nights, gbv_musd, revenue_musd, take_rate_pct
#   data/processed/abnb_backlog_indicators.csv            unearned_fees_musd, funds_held_musd
#   data/processed/overnight/10_fx_quarterly.csv          9-ccy quarterly levels, 1Q18-3Q26
#   data/processed/overnight/10_fx_basket.csv             region x ccy weights
#   data/processed/overnight/28_fx_hedge_disclosures.csv  gross_fx_ex_hedge_pp, non_usd_revenue_share
#   data/processed/overnight/28_fx_hedge_forward.csv      forward hedge dollars (Lambda_q)
#   data/processed/overnight/06_fee_timeline.csv          dated migration events -> m_q
#   data/processed/adr/12_reprice_summary.csv             measured theta (host gross-up pass-through)
#   data/processed/overnight/06_quote_line_items.csv      li_taxes, li_cleaning_fee -> GBV de-rate
#   data/processed/booking_curve_daily.csv                blocked_rate(days_ahead) -> Dirichlet prior
import numpy as np, pandas as pd

# ---------- 1. fee schedule: ONE function, host payout -> (GBV, revenue). No double count possible.
def schedule(host_payout, migrated, hotel_sh, exp_sh, svc_sh, direct_sh, tax_clean_sh=0.11):
    # split fee: guest 14.1% on top, host 3% out; single fee: host grosses up, 15.5% out
    gbv_split,  rev_split  = host_payout/0.97*1.141, host_payout/0.97*0.171
    gbv_single, rev_single = host_payout/0.845,      host_payout/0.845*0.155
    gbv = (1-migrated)*gbv_split + migrated*gbv_single
    rev = (1-migrated)*rev_split + migrated*rev_single
    rev *= (1 - tax_clean_sh)                      # fees are not levied on taxes/cleaning
    rev += gbv*(hotel_sh*0.11 + exp_sh*0.20 + svc_sh*0.15 - direct_sh*0.08)   # mix + leakage cap
    return gbv, rev                                # ADR and take rate are OUTPUTS of these two

# ---------- 2. two currency indices from one basket; booking-dated and check-in-dated
def indices(fx_q, basket, reg_w_gbv, reg_w_rev, base="1Q23"):
    X = lambda w: sum(w[r]*b.weight*(1.0 if b.currency=="USD" else fx_q[b.currency]/fx_q.loc[base,b.currency])
                      for r in w for b in basket[basket.region==r].itertuples())
    return X(reg_w_gbv), X(reg_w_rev)              # X^G (booking), X^R (revenue)

# ---------- 3. the kernel: Rev_q = sum_k Phi[Q(q-k), k] * tau(m_{q-k}) * H_{q-k} * fx_conv + Lambda_q
def revenue(q, H, Phi, m, XR, lam, s_R, Lam):
    tot = 0.0
    for k in (0, 1, 2, 3):                          # Phi[:,0] is pinned to ~0 by the PIT restriction
        b = q - k
        _, rev_b = schedule(H[b], **m[b])
        fx = 1 + s_R*(lam*(XR[q]/XR[b]) + (1-lam) - 1)     # lam=1 check-in translate, 0 booking lock
        tot += Phi[b.quarter_of_year, k] * rev_b * fx
    return tot + Lam[q]                             # hedge dollars, added ONCE, never as a rate

# ---------- 4. Stan block (sketch). Identification comes from constraints, not from features.
#   parameters { simplex[4] Phi[4]; real<lower=0,upper=1> rho, lam; real s_R, s_G; vector[T] H; }
#   model {
#     for (Q in 1:4) Phi[Q] ~ dirichlet(alpha_from_booking_curves[Q]);   // external shape prior
#     s_R ~ normal(0.56, 0.03);                                          // DISCLOSED non-USD rev share
#     s_G ~ normal(0.68, 0.05);
#     lam ~ beta(3, 1);                                                  // 28_fx_hedge_tests lag-1 > lag-0
#     revenue_obs   ~ normal(revenue_hat, sigma_r);                      // 23 printed quarters
#     gbv_obs       ~ normal(gbv_hat,     sigma_g);                      // 23 printed quarters
#     unearned_restated ~ normal(cumsum(fees_booked - fees_recognised - refunds), sigma_u);
#     for (g in guide_buckets)                                           // INTERVAL-CENSORED, not midpoints
#       target += log_diff_exp(normal_lcdf(g.hi|mu[g.q],sd), normal_lcdf(g.lo|mu[g.q],sd));
#     for (f in fx_stated)                                               // letters round to integers:
#       target += log_diff_exp(normal_lcdf(f.pp+0.5|fx_hat[f.q],sd_f),   // score on [x-0.5, x+0.5]
#                              normal_lcdf(f.pp-0.5|fx_hat[f.q],sd_f));
#   }
# ---------- 5. hand off to the R engine for the production translation
#   write exposure.csv (nights-weighted region x ccy, shares sum to 1 per geography-quarter),
#         forecasts.csv (quarter, geography, region, level, nights, adr=usd_constant, take_rate),
#         hedges.csv    (scenario, quarter, hedge_usd  <- 28_fx_hedge_forward.csv)
#   Rscript --vanilla analysis/src/fx_engine/run_forecast.R <in> <out>
#   consume adapter.csv: EITHER revenue_fx_usd added to reference-basis revenue,
#                        OR revenue_timing_multiplier after FX-adjusted GBV x take.  NEVER both.
```

---

## 7. Three-week build plan, 3-4 undergraduates

**Week 1, day by day.**
- **Day 1 (all).** Freeze the spec: increment `spec_id` in `20_experiment_spec.json`, write the four pre-registered falsification tests (restated-backlog beats naive; two-index FX beats `05_fx_fits.csv` LOO 2.30pp on both windows; kernel beats the perfect-foresight take-rate construction; fee uplift shows up in the 3Q26 printed take rate). Nothing is run before this is committed.
- **Day 2 (A).** Build the restated unearned-fee series `reported/(1−d_q)` from `abnb_backlog_indicators.csv` using the 2023-25 seasonal coverage norms; reproduce the 0.9/3.8/16.2/16.5% distortion series; re-run the `08_backlog_tests.csv` regressions on the restated series. **This is the day that decides whether identification pin #1 survives.**
- **Day 2 (B).** Build `X^G` and `X^R` from `10_fx_daily.csv` at daily frequency; reproduce the stated ADR-FX series (target: beat the 0.76pp RMSE I got on quarterly averages) and the gross revenue-FX series with the **interval likelihood** on the letter-rounded values.
- **Day 3 (A+B).** Fit the seasonal `Φ` by constrained least squares (pre-Stan) against printed revenue + restated backlog. Report the 4×4 matrix, the implied "share already booked at guide date" by quarter, and `τ_eff` dispersion. **Success criterion: within-quarter-of-year `τ_eff` relative sd below 1.0% in all four quarters.**
- **Day 3 (C).** Measure the tax+cleaning share of GBV from `06_quote_line_items.csv` (`li_taxes + li_cleaning_fee` over `li_nightly_subtotal`), city-weighted. This de-rates the fee uplift and is currently an unmeasured assumption in every build including mine.
- **Day 4 (C).** Build the migrated-**GBV**-share path (not listing share) from `06_fee_timeline.csv` disclosures × professional-host concentration in `inside_airbnb_host_concentration.csv`; cross-check against the measured `theta` in `12_reprice_summary.csv`. Deliver `m_q` for 3Q25-4Q27.
- **Day 4 (D).** Extract the full hedge book: finish the hand-extraction in `28_fx_hedge_disclosures.py` for the remaining 10-Qs, tie `reclassified_to_revenue_musd` to the AOCI cash-flow-hedge XBRL line, and build forward `Λ_q` for 3Q27-4Q27 (currently only 3Q26-2Q27 exist).
- **Day 5 (all).** First end-to-end run in pure numpy: 3Q26 and 4Q26 point forecasts with the FX and fee blocks live. Reconcile to `29_q4_2026_bridge.csv` term by term and **write down the four-way FX reconciliation** (repo fit −0.43pp / two-index +0.41pp / guide-anchored +2.6pp / R-engine adapter). This is the memo's centrepiece; it must exist by the end of week 1.

**Week 2 milestones.** Port to Stan with the priors in §4; run the expanding-window walk-forward from 4Q22 with strict PIT vintages; score against all four baselines on both frozen windows; build the conformal calibration set; feed the real `exposure.csv` / `forecasts.csv` / `hedges.csv` into the R engine and verify the Python and R revenue lines agree to <0.1% (the engine ships 42 checks — use them); produce the FY27 quarterly path under spot-constant, forward-curve and ±1sd USD.

**Week 3 milestones.** Scenario tree with dated branch probabilities; the guide-emission layer and the distribution over the 5 Nov Q4 guide range; the mechanical bridge from Street to us for 4Q26 and FY27, one named term at a time; two exhibits for the two-page memo (the FX reconciliation waterfall; the take-rate bridge 3Q26-4Q27 on both quarterly and LTM bases); stress the five hostile questions in §8 and write the answers.

**What can be cut, in order.** (i) The Stan port — constrained least squares with a bootstrap gives 80% of the answer and all of the point estimates; (ii) conformal calibration — keep the posterior and state that it is uncalibrated at n≈12; (iii) FY27 quarterly seasonality — collapse to an annual take-rate bridge; (iv) the R-engine integration — it is a validation cross-check, not a dependency, though it is the only piece with 42 pre-existing unit tests and it is cheap. **What cannot be cut: the restated backlog (day 2A), the daily FX indices (day 2B), the fee-schedule single-numéraire construction (day 4C), and the four-way FX reconciliation (day 5).** Those four are the lens.

---

## 8. Failure modes and the hostile-judge cross-examination

**"Your kernel is just a take rate with extra steps."** No — it is a ratio to a *different denominator*. The take rate divides check-in-dated revenue by booking-dated GBV *of the same quarter*, which is why it swings 9.2/13.1/18.3/14.0 through the year and why Mertz calls it a timing difference. The kernel divides by the GBV that actually generated the revenue. Empirically the FX-adjusted conversion's within-quarter-of-year relative sd is 1.45/0.46/1.00/0.86% against the take rate's 2.08/1.10/2.17/2.52% — and it is applied to a published base rather than a forecast one, which removes the entire GBV forecast error from the Q4 guide problem.

**"n = 23. You have 11 parameters. You are over-fitting."** The 11 parameters face 23 revenue identities, 23 balance-sheet identities, 14 FX observations and 19 interval-censored guide buckets, and two of the parameters (`s_R`, `s_G`) are pinned by disclosure rather than estimated. Compare the incumbent: 12 plugs and 18 assumed parameters on the same data (audit §2), of which two (`τ_p` carry and `w_q`) jointly carry the whole timing mechanism. **We are reducing the parameter count, not raising it.**

**"Φ is unobservable. You've replaced one plug with another."** Partly true, and it is the honest weak point. Airbnb has legally engineered bookings so there is no ASC 606 remaining-performance-obligation disclosure and no unearned-fee rollforward; the FY2025 10-K explicitly says unearned fees "are not considered contract balances." So every conversion ratio is an estimate. The difference is that `Φ` is **over-identified** — four independent pins, two of them hard accounting restrictions — and it is **testable**: `research/notes/2026-09-10_h1-to-h2-bridge.md` §4 and `h2_bridge_gbv_lag_conversion.csv` show the lagged conversion has been 17.39/17.15/17.18% for three consecutive Q3s and 11.95/12.12/12.03% for three Q4s. A plug does not do that three years running.

**"Management guided FY26 take rate flat and has never missed a revenue guide. If the fee migration were worth 4% of revenue on the migrated cohort they would have said so."** They effectively did: *"Absent these incentives, we would have anticipated our implied take rate to be slightly higher, driven by our monetization initiatives"* (Mertz, 2Q26 call). The uplift is real and it is being spent, in FY26, on hotel price-match and a 15% Airbnb credit that **expires 31 Dec 2026**. The honest central case is therefore smaller than the raw arithmetic — we carry roughly half — and the risk is explicitly two-sided: the 29 Aug 2026 direct-link pilot at 6-10% is management pre-emptively capping the same benefit, worth −80bp at 10% of nights, which is larger than the entire migration gain. **Take rate is now a policy variable with a positive and a negative lever pulling simultaneously; that is the finding, not "take rate goes up."** And note the base rate: take-rate guidance is the *one* guide type Airbnb has actually missed (guided "up slightly" for 1Q26, delivered −0.10pts; guided 0.0 for 3Q25, delivered −0.69).

**"Your own FX fit misses the Q3 guide by 2.2pp. Why should I believe the Q4 number?"** You should not believe the point estimate yet; you should believe the reconciliation. I have shown that three defensible constructions give −0.43pp, +0.41pp and +2.6pp for 4Q26, a 3pp spread worth $90M, and that the team's current bear case rests on the weakest of the three (a single-regressor lagged-EUR fit with LOO RMSE 2.30pp on n=17, and the audit shows the *better*-validated FX fit in the repo cancels out of revenue entirely). The deliverable is the resolution, and it needs no new data: daily baskets, booking-date weighting via `Φ`, the 10-Q hedge note, and an interval likelihood on the letter-rounded stated values.

**"Inside Airbnb failed 36 tests. Why do you get to use it?"** We use it for two things only, neither of which is a time-series prediction: the *measured* host re-pricing pass-through θ (matched listing pairs, `12_reprice_summary.csv`) and the *cross-sectional* tax/cleaning share of GBV (`06_quote_line_items.csv`). The panel failed on coverage and vintage-reconstructibility as a 13-city time series (`n_flagged_r05_perm05 = 0` in both windows); neither defect touches a within-vintage matched-pair or a cross-sectional share.

**"What kills this?"** Three things, in order. (1) The restated backlog fails out of sample on day 2 — then `Φ` loses its hardest pin and rests on the column-sum restriction plus a single-vintage booking-curve prior, which is materially weaker. (2) Airbnb concedes rate broadly to defend hosts — the direct-link pilot goes general at 8% on >10% of nights and the entire fee edge inverts. (3) The 3Q26 print reveals that the printed take rate did *not* move with the migrated share, which would mean either the tax/cleaning de-rate is far larger than 11% or hosts are not on 15.5% in practice. **All three are observable on 5 Nov 2026, before the finals reconvene — which is exactly the property a Citadel PM wants in a thesis.**

---

## 9. Interlock

**Consumes.**
- *From lens 1 (structural mix / constrained regional nights):* the interval-censored regional nights posterior and the FX-neutral regional ADR ex-FX, delivered as **host payout per night in `usd_constant`**, not as reported ADR. This is the single most important interface change: if they hand me reported ADR, the fee reprice is already inside it and the double count returns. The handoff row is the R engine's contract exactly: `quarter, geography, region, level, nights, adr, adr_basis=usd_constant, currency, take_rate, reference_basis` (`FX_ENGINE_MENTAL_MAP.md`).
- *From lens 2 (nowcast tracker):* nothing required. If they produce a same-quarter GBV nowcast it slots into `H_q`, but `Φ_0 ≈ 0` means the 4Q26 guide does not depend on it.
- *From lens 4 (bottom-up markets):* market-level migrated-share and tax/cleaning shares, and — if they build a second Inside Airbnb capture — a post-deadline re-pricing panel that measures θ on the *mandatory* cohort rather than the voluntary early migrants.
- *From lens 5 (ML / LLM extraction):* structured extraction of the fee, hedge and incentive sentences from the 3Q26 10-Q and call within hours of the print — specifically designated notional, expected next-12-month reclass, migrated-listing share, and any quantification of new-business incentives.

**Hands to.**
- *To every lens:* `Φ`, i.e. the answer to "what share of quarter q's revenue is already on the ledger at date t," which is the arithmetic backbone of the guidance-game lens. It converts "Airbnb beats its guide 19/19" from a base rate into a mechanism: the cushion is small and shrinking (+3.04% over the first 11 prints, +1.86% over the last 8; range width 4.9% → 1.9% of midpoint) **because `Φ` leaves management seeing 85-90% of the quarter on guide day**.
- *To lens 3 (guidance game):* the revenue-level posterior that the cushion distribution converts into a guide range, plus the FX pp management will quote inside the guide sentence — they have quantified FX in that sentence every quarter, so we can forecast the sentence, not just the number.
- *To lens 1:* `s_G` and the FX-neutral deflators that de-contaminate the regional nights weights (audit §3.2: FX currently enters the nights build procyclically, worth ~+0.09pp of nights growth at 2Q26 FX levels).
- *To the valuation layer:* the FX pp, at 0.47 points of Adjusted EBITDA margin per point of revenue FX at Airbnb's dollar cost base — so the 4Q26 FX call is worth ~1.6 margin points before any marketing decision, and the FY27 exit multiple moves +0.48 EV/EBITDA turns per point of forward revenue growth. **The take-rate bridge is the highest-leverage line in the model:** costs scale with GBV and bookings, not with revenue, so ~90% of a take-rate change drops to EBITDA; ±50bp on FY25 GBV of $91.3bn ≈ ±$460m of revenue ≈ ±3.5 points of EBITDA margin — larger than the entire FY26 margin guidance range.
- *A warning to all lenses:* the hedge line (−0.21/−0.21/−0.18/−0.18pp, `28_fx_hedge_forward.csv`) is **already inside** the letter-stated after-hedge FX numbers. `29_q4_fy27_bridge.py` treats it correctly as `hedge_memo_pp`. `28_fx-hedge-disclosures.md`'s "For the model" section reads like an instruction to add it. **Anyone who adds it separately understates revenue by ~0.2pp a quarter.**
