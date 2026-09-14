# M1 — MIXSTATE: a chain-linked conditional-index state space for ABNB revenue

**Proposal for the Citadel pitch modelling team.** Author: methodology proposer, lens M1 (structural
mix-aware decomposition as one state-space model). Date 11 Sep 2026. Repo `main @ a5d6dbb`.
Every repo path below was opened. Numbers marked **[recomputed]** were computed by me in this session
from the cited file and the script is reproducible in ten lines; they are not quoted from a note.

---

## 1. Thesis in five lines

1. **What it forecasts.** The joint posterior of the four *latent* regional home-night paths and the
   four *latent* regional ex-FX home-ADR paths, quarterly to 4Q27, from which printed Nights-and-Seats,
   printed blended ADR, GBV, take rate and revenue fall out as identities — emitting a posterior
   predictive **level** for 3Q26 revenue, for the 4Q26 guide midpoint management will set on ~5 Nov,
   and for FY27 revenue against the Street's $15.73-15.76bn (`data/processed/overnight/04_current_consensus.csv`).
2. **Why the level and not the surprise.** `docs/revenue-forecast-strategy/01_ground-truth/02_model_audit.md` §4.2(b)
   shows the ~3,500-test programme died by testing *surprise vs Street* (sd ≈1.3pp) with features that
   predict *level* (sd ≈5pp); `pred_sd/actual_sd` = 0.14-0.33 on 16 of 17 pairs. The 3-12 month window
   contains four **guides** and no decisive print, so level and guide are the right targets.
3. **Why it should beat what exists.** The current engine (`analysis/src/overnight/13_driver_model.py`
   L363-393) reduces algebraically to a product in which the FX-on-ADR term cancels exactly, the take
   rate is a prior-year carry, and 100% of an 8-quarter perfect-foresight backtest error (+0.53%, sd 1.97%)
   sits in one plug. MIXSTATE removes that plug and three others *by construction*, not by better judgement.
4. **The identifying asset nobody is using.** Quarterly regional revenue is disclosed **exactly** in the
   10-Q XBRL and Q4 is exactly recoverable from the 10-K. I rebuilt the full 1Q22-2Q26 panel and it
   reconciles to the printed total to the dollar-million in 4Q23 ($2,218M), 4Q24 ($2,480M) and 4Q25
   ($2,778M) **[recomputed]**. That is 72 exact regional observations sitting in the repo used only as
   the denominator of a share-plug.
5. **The differentiated call it produces.** Same nights as the Street, fewer dollars: geographic mix
   becomes an *output* of the nights build rather than a hand-set −1.7pp row, which pulls FY27 blended
   ADR toward the workbook's measured +1.37% and away from the model's assumed +2.50%, and the 4Q26
   revenue-FX step (−3.4pp, ~84% already observed) is a *measured state* rather than an assumption.

---

## 2. Formal specification

### 2.0 The ordering of the conditional indices, and why it is that ordering

Write reported blended ADR growth as a chain of Törnqvist indices over a sequence of partitions in
which each partition **refines** the one above it. With that nesting, every term at level *k* is by
construction the *within-cell* residual of level *k−1*, so no term can contain another. The ordering,
coarsest to finest:

| k | Partition | Index | Why here |
|---|---|---|---|
| 0 | currency of transaction | `F` (FX translation) | mechanical, fully observable daily, and it is a *translation* of every cell — it must sit outside every real term or it contaminates all of them |
| 1 | region (NA/EMEA/LatAm/APAC) | `M^geo` | the coarsest partition Airbnb discloses **exactly** (10-K annual regional table) |
| 2 | product line within region (homes / hotel rooms / experiences seats / services seats) | `M^prod` | a seat is a different good, not a cheap night; the KPI denominator changed definition 13 May 2025 |
| 3 | unit size within homes (capacity, bedrooms) | `M^size` | measured on 129 market-pairs, `data/processed/adr/08_size_mix_extended_summary.csv` |
| 4 | length-of-stay bucket within size | `M^los` | measured, `data/processed/adr/14b_los_adr_term.csv` |
| 5 | everything remaining within region × line × size × LOS | `P` (like-for-like price) and `M^sub` (sub-regional mix), **jointly unidentified** | the honest residual |

Ordering rule: *coarsest disclosure first*. Level 1 is pinned by exact annual data; level 2 by the
disclosed KPI-definition change; levels 3-4 by market panels; level 5 is what is left. Economically
the same order runs exogenous-to-endogenous: where Airbnb sells (geography, product line) is a
corporate decision; unit size and stay length are guest composition conditional on that; price is the
residual. Törnqvist is *superlative* (exact for a translog aggregator), so ordering matters only to
second order — and I will **report the reversal test**: re-run the chain in reverse order (5→1) and
publish the spread on each term as the ordering-sensitivity number. If the spread on the geo term
exceeds 0.2pp, the ordering claim is retracted, not defended.

### 2.1 States

Index quarters `t`, regions `r ∈ {na, emea, latam, apac}`, years `y`.

**Home nights.** Let `ℓ_{r,t} = ln n^home_{r,t}`. Parameterise the *level* through an exactly-adding-up
share: `n^home_{r,t} = N^home_t · s_{r,t}`, with `s_{·,t} = softmax(u_{·,t})`, `u_{na,t} ≡ 0` (identification
normalisation), `u_{r,t}` a random walk with drift. **Σ_r n_r = N holds by construction — there is no
residual to calibrate.** This single choice retires `CALIB = −0.41pp` (`10_regional_forecast.py:78,137`),
the +0.19pp index-number bias **[audit §3.3, recomputed there]**, and the 0.41pp gap between WS10 and
`13_driver_model.py` (which applies no calibration at all, L376).

Dynamics on the y/y log growth `g_{r,t} = Δ₄ℓ_{r,t}` (y/y is how *every* disclosure is phrased, so this
is the natural state):

```
g_{r,t} = c_{r,t} + φ_g (g_{r,t-1} − c_{r,t-1}) + λ_r' z_{r,t} + δ_r' d_t + η_{r,t},   η ~ N(0, σ_g²)
c_{r,t} = c_{r,t-1} + ν_{r,t}                       (slow trend, ν ~ N(0, σ_c²), σ_c small)
c_{r,0} ~ N(c̄, τ_c²)                                 (hierarchical across regions)
```

`φ_g` is **pooled across regions** (one parameter estimated on 4 × 24 = 96 growth cells, not 24).
`z_{r,t}` are vintage-lagged demand covariates (Eurostat EU27 platform nights for EMEA, JNTO/INE/ISTAT
for APAC/EMEA, the regulatory DiD treatment intensity). `d_t` are **dated product-lever dummies with
explicit lap structure**: RNPL-US from 3Q25 and its lap from 3Q26; RNPL-global from 1Q27; the
cancellation-policy redesign Oct 2025. This is where the audit's sharpest unstated assumption
(§3.9: "WS10's FY27 NA +6% implicitly requires a same-sized product lever every year, never lapped",
worth ~1.1pp of total nights ≈ $170M FY27) becomes an *estimated parameter with a posterior* instead of
a hidden property of a hard-coded dictionary.

**Seats and hotel rooms** get their own small states: `n^hotel_t`, `s^exp_t`, `s^svc_t`, each a log random
walk with drift, observed only through interval disclosures ("hotel nights growing ~3x homes",
"Experiences supply +80% y/y", "single-digit % of nights") entered as interval constraints. They are
**not** in the region partition at level 1; they enter at level 2.

**Home ADR, local currency, ex-FX.** For each region, the level-5 decomposition *is* the state equation:

```
a_{r,t} ≡ Δ₄ ln ADR^home,local_{r,t} = p_t + q_{r,t} + m^size_{r,t} + m^los_{r,t} + m^sub_{r,t}
p_t   = p_{t-1} + ε_{p,t}                          global like-for-like price state (random walk)
q_{r,t} ~ N(0, σ_q²), σ_q ~ half-N(0, 0.01)        regional price deviation, heavily shrunk
```

The heavy shrinkage on `q` is not arbitrary: `research/notes/2026-09-07_adr-decomposition.md` concludes
"regional pricing is one number now, not four". Making that a prior with a posterior is how you test it
rather than assert it. `m^size` and `m^los` are **measured** with reported standard errors (§2.3).
`m^sub` is the sub-regional mix term and is where the honest unidentification lives (§2.5).

**Take rate and recognition timing.** Revenue is check-in dated; GBV is booking dated
(`01_ground-truth/03_insider_mechanics.md` §1.1, FY2025 10-K Revenue Recognition). So:

```
Rev_{r,t} = τ_{r,t} · Σ_{k=0..3} φ_k · GBV^local_{r,t-k} · X^C_{r,t}
τ_{r,t} = τ_{r,t-1} + ε_{τ,t}   (slow RW, σ_τ tiny)     φ ~ Dirichlet(α)
```

`φ` is the booking→check-in kernel, **not** a take-rate seasonal. There is no quarterly take-rate
assumption anywhere in this model; the printed 9.2 / 13.1 / 18.3 / 14.0 seasonality
(`02_kpi_panel_quarterly.csv`) falls out of `φ` convolved with GBV seasonality. This is the audit's
recommendation 1 implemented inside the mix model rather than beside it.

### 2.2 Observation equations, with the likelihood for each

**(A) Exact, zero-noise (enter as deterministic transforms or with σ = 1e-6):**

| Observation | Source | Count |
|---|---|---|
| total Nights-and-Seats, GBV, ADR, revenue, quarterly | `data/processed/overnight/02_kpi_panel_quarterly.csv` (cols `nights_m`, `gbv_musd`, `adr_usd`, `revenue_musd`) | 24 × 4 |
| **quarterly regional revenue, 1Q22-2Q26** | `data/processed/overnight/10_xbrl_revenue_geography.csv` (tags `srt:NorthAmericaMember`, `us-gaap:EMEAMember`, `srt:LatinAmericaMember`, `srt:AsiaPacificMember`), Q4 backed out against the 10-K annual | **72** |
| annual regional GBV and revenue | `data/processed/adr/01_regional_annual.csv` (from FY2021-FY2025 10-Ks) | 6 × 4 × 2 |

The Q4 back-out is exact, not approximate. 2025: NA 5196 − (1054+1377+1619) = 1146; EMEA 4729 − 3799 = 930;
LatAm 1160 − 809 = 351; APAC 1156 − 805 = 351; sum = **$2,778M = reported 4Q25 revenue, to the dollar-million**.
Same for 4Q24 ($2,480M) and 4Q23 ($2,218M) **[recomputed]**. Each row carries a `filed` date, which makes
point-in-time replay mechanical.

**(B) Interval-censored (the core of the method).** For an observation whose truth is only known to lie
in `[L, U]`, the log-likelihood contribution is
`log( Φ((U − μ)/σ) − Φ((L − μ)/σ) )` — in Stan, `log_diff_exp(normal_lcdf(U|μ,σ), normal_lcdf(L|μ,σ))`.
Four families:

1. **Regional nights-growth buckets.** `data/processed/overnight/10_regional_panel_quarterly.csv`,
   columns `{r}_nights_yoy_lo` / `_hi` where `{r}_basis == 'bucket'`. **28 genuine bucket observations**
   (4Q24-2Q26 × 4 regions) **[recomputed]**, each 2-3pp wide (e.g. 2Q26 NA [7,9], EMEA [7,9],
   LatAm [19,21], APAC [17,19]). *Critical hygiene point:* the same file carries **14 further rows with
   `basis = 'derived (residual to total …)'` for 1Q24-3Q24** — those are *outputs* of
   `10_regional_panel.py`'s residual solve, clipped to ±12, not disclosures. MIXSTATE **must not**
   condition on them; it re-derives them from the exact total and the exact regional revenue. Feeding a
   model its own prior output is the commonest way a state-space build fakes precision.
2. **Rounded percentage disclosures.** Every regional ADR y/y in `data/processed/overnight/10_regional_adr_fx.csv`
   is an integer (2Q26: NA +7, EMEA +7/+5 ex-FX, LatAm +9/+2, APAC +1) — 38 reported and 30 ex-FX
   observations **[recomputed]**. Global `adr_yoy_exfx_pct` in the KPI panel is likewise integer
   (1Q25-2Q26: 1, 1, 2, 3, 4, 4). The audit flags this as a **still-live measurement defect** (§4.2c:
   "on a target with a 3.5pp total range, roughly half the variance is rounding"). The fix is not a
   better regression — it is to stop pretending these are point observations. Enter each as
   `[x − 0.5, x + 0.5]`. That converts the repo's single worst measurement-error problem into a
   correctly-specified likelihood at zero data cost.
3. **Annual regional nights.** `01_regional_annual.csv` reports 2025 as NA 158 / EMEA 215 / LatAm 90 /
   APAC 70, rounded to 1M, summing to the disclosed 533M. Enter as `[x − 0.5, x + 0.5]` **and** impose
   the sum exactly. 24 interval observations across 2020-2025.
4. **Qualitative guides and seat disclosures.** "low double-digit" → [10,12]; "mid teens" → [14,16];
   "hotel nights ~3x homes" → `g^hotel ∈ [2.5, 3.5] × g^home`; "seats immaterial (2Q25)" → seat share
   ≤ 1.5%. Map from `data/processed/overnight/02_guidance_ledger.csv` (194 statements, dated at issuance).

**(C) Noisy measurements with reported standard errors:** `m^size` from
`data/processed/adr/08_size_mix_extended_summary.csv` (129 rows, market × 2Q26 window, with
`wedge_pp_market_min/median/max` giving a dispersion) and `data/processed/adr/05_size_mix_summary.csv`;
`m^los` from `data/processed/adr/14b_los_adr_term.csv` (`los_mix_pp` with `sens_lo`/`sens_hi`, e.g. 2023
`los_mix_pp` 0.330 in [0.323, 0.936]). These enter as `m̂ ~ N(m, se²)` — noisy readings of a state, not
inputs.

**(D) Covariates on the nights state, with shrinkage:** `data/processed/overnight/10_eurostat_platform_monthly_latest.csv`
(EU27 + 33 countries, Jan 2023-Mar 2026, 39 months, `eu27_nights_yoy_pct` 11.41 at the last print),
`10_bench_japan_arrivals_monthly.csv`, `10_bench_canada_travel_monthly.csv`. Prior `λ_r ~ N(0, ψ²)`,
`ψ ~ half-N(0, 0.15)`. **Pre-registered promise: publish the posterior of every `λ`.** If Eurostat
earns nothing, the posterior sits on zero, the model is unchanged, and we have reported it — which is a
categorically different outcome from the 64 failed Eurostat regressions in
`data/processed/overnight/08_eurostat_tests.csv`, where the series was asked to *be* the forecast.

### 2.3 The printed KPIs as outputs — this is where the seats problem dies

```
N^printed_t   = Σ_r n^home_{r,t} + n^hotel_t + s^exp_t + s^svc_t
GBV_t         = Σ_r n^home_{r,t}·ADR^home,USD_{r,t} + n^hotel_t·ADR^hotel_t + s^exp_t·p^exp + s^svc_t·p^svc
ADR^printed_t = GBV_t / N^printed_t
TakeRate_t    = Rev_t / GBV_t
```

Seats dilution is therefore **an identity, not a row**. That resolves by construction the audit's §3.6
triple treatment — `13_driver_model.py` applies no dilution, `14_revenue_by_line.py:152` reads `a_x` as
already-net and adds it back, `model/ADR_decomposition.xlsx` 5_Forecast carries −0.57pp as a separate
deductible — "two of which are mutually exclusive", worth 0.57pp of revenue growth ≈ $88M on FY27. It
also retires `adr/15_seats_dilution.py:55`'s `HOME_NIGHTS_GROWTH` (literally commented `# placeholder`),
because home nights now come from the same build everything else uses.

Likewise geographic mix is an identity: `ADR^printed` is a nights-weighted aggregate of regional ADRs,
so a bull nights case in LatAm *automatically* deepens the ADR mix drag. The audit's §3.4 "broken
feedback loop" (worth 1.13pp of ADR ≈ $175M on FY27) cannot exist in this specification.

### 2.4 FX enters exactly twice

Two objects only, both built from one currency basket per region (`data/processed/overnight/10_fx_daily.csv`,
19,468 rows; `10_fx_basket.csv`; pass-throughs in `10_regional_fx_passthrough.csv` — EMEA slope 1.043
(r 0.987, n 10), APAC 0.86 (r 0.972, n 5), LatAm 0.62, NA unidentified):

- `X^B_{r,t}` — booking-date index. Translates local-currency ADR and GBV.
- `X^C_{r,t}` — check-in-date index. Translates revenue, applied to the `φ`-convolution of local GBV.

There is no "FX timing wedge". The audit's §1.3 finding — that `f_A` cancels exactly and the best-validated
survivor of the whole programme (broad USD → ADR FX, walk-forward **0.44× naive**) is therefore wired to a
display-only line — is fixed structurally: `X^B` and `X^C` differ, so FX cannot cancel. The hedge becomes an
explicit overlay on a gross series (`28_fx_hedge_disclosures.csv`, 1Q23-2Q26), removing the double-subtraction
trap the audit flags at §3.7. And FX no longer enters the nights weights, because the weights are a softmax
over latent shares, not FX-translated revenue divided by a fixed 2025-calibrated `IDX` — killing the audit's
§3.2 procyclicality (~+0.09pp of nights growth at 2Q26 FX levels, correlated with the same dollar move that
inflates the FX terms).

### 2.5 GBV directly, or nights and ADR separately? — the identification argument

**Decision: model *nights and ADR separately at region level*; model *GBV only at total level*, as an
exact observation on the product.** The argument is purely about where the disclosure lives.

- At **total** level, GBV, nights and ADR are all disclosed exactly every quarter (`02_kpi_panel_quarterly.csv`:
  2Q26 nights 148.3, ADR 183.73, GBV $27,200M). Any two pin the third. Nothing is gained by choosing.
- At **region** level, GBV is disclosed only **annually** (`01_regional_annual.csv`), whereas *nights* carry
  two independent disaggregating disclosures — the quarterly buckets (28 intervals) and the annual exact
  counts (24 intervals) — and *ADR* carries 38 quarterly reported and 30 ex-FX integer readings plus exact
  annual levels (2025: NA $255.03, EMEA $158.89, LatAm $94.91, APAC $118.20 **[recomputed]** from
  `01_regional_annual.csv`). Modelling regional GBV directly would throw away the bands, which are the
  *only* quarterly regional signal there is.
- The residual degeneracy — within a region, quarterly data constrains mostly the *product* `n_r·ADR_r`
  through the exact revenue panel — is broken by exactly three things, and I state them as the
  identification claim: (i) the nights buckets constrain `n_r` alone; (ii) the annual 10-K constrains
  `n_r` and `ADR_r` separately and exactly; (iii) the regional ADR integers constrain `ADR_r` alone.
  Where a quarter has neither (ii) nor (iii) — NA ex-FX ADR is missing after 1Q25, APAC after 1Q26 — the
  posterior on the *split* widens while the posterior on the *product* stays tight. **That is the correct
  behaviour and it must be shown in the memo exhibit, not hidden.**

### 2.6 How the unidentified residual is handled honestly

`P` (like-for-like price) and `M^sub` (sub-regional mix) are jointly unidentified: no country-level ADR
is disclosed. `adr/07_assemble.py:103-104` gets it by subtraction (+3.6pp of 2025 within-region ex-FX;
+2.2pp carried into the forecast). MIXSTATE does three things instead of one:

1. **An informative prior on `P` from an independent hedonic quote index.** One log-additive regression
   on `data/processed/overnight/06_quote_line_items.csv` (77 aggregate rows over 1.71M fee-inclusive
   quotes, Mar-Aug 2026 by city) with capacity, bedrooms, stay-length bucket and market fixed effects
   estimated **jointly**, reusing `06_wtp_hedonic_coefs.csv` (extra bedroom +15.1%, capacity elasticity
   +0.49, 4.9★ premium +9.5%). Prior: `P_t ~ N(hedonic like-for-like index, 1.0pp²)`.
2. **A proxy for `M^sub`.** Expansion-market origin nights run ~2× core for six-plus consecutive quarters
   (`research/airbnb_earnings_call_study.md` §3.2; `10_regional_panel_quarterly.csv` col
   `expansion_market_growth_vs_core`) and expansion markets are lower-ADR. Enter as a signed prior:
   `M^sub_{r,t} ≤ 0` for LatAm/APAC with magnitude tied to the modelled share shift.
3. **Report the 2-d joint credible region, never a point.** The memo exhibit is a contour of
   `(P, M^sub)` with the identified sum drawn as a ridge. Any FY27 call that survives only at the
   top of that ridge is labelled as such.

**Prior-sensitivity commitment:** publish `∂(FY27 revenue)/∂(prior mean on P)`. If the call flips within
the prior's own 1σ, the call is withdrawn.

### 2.7 The eight overlaps, and the construction that kills each

| Audit finding | Size | Killed by |
|---|---|---|
| take carry × FX wedge plug (§3.1) | +1.05pp trailing-4, ±2.0pp 1σ; ~$165M FY27 | `φ`-kernel convolution; no take-rate forecast exists |
| FX in the nights weights (§3.2) | ~+0.09pp nights, procyclical | softmax shares; weights are latent, never FX-translated revenue |
| current-period growth weighting (§3.3) | +0.19pp stable bias; 0.41pp WS10-vs-13 gap | log levels + softmax → aggregation is an identity, no residual to calibrate |
| geo mix not fed back into ADR (§3.4) | 1.13pp ADR ≈ $175M FY27 | `ADR^printed = Σ w_r ADR_r`, mix is an output |
| size × party × LOS from one universe (§3.5) | bounded ~0.30pp; live trap | one joint hedonic; the party-size term **is** the capacity index, so it cannot be added twice |
| seats treated three ways (§3.6) | 0.57pp ≈ $88M FY27 | denominator identity `N = Σn^home + n^hotel + s^exp + s^svc` |
| FX four times, two inert (§3.7) | ~0.2pp/qtr hedge ambiguity | two FX objects, `X^B` and `X^C`; hedge is an explicit overlay |
| regulatory drag possibly double-counted (§3.8) | 0.28pp FY27 ≈ $44M; `reg_mult=1.67` | DiD treatment intensity as a *covariate on the state*, with dated pre-periods, not a post-hoc subtraction from a growth rate already set on realised (contaminated) data |

---

## 3. Data map — verified paths

**Exact observations (all in repo, all PIT-datable):**

| Path | Grain | Coverage | Role |
|---|---|---|---|
| `data/processed/overnight/02_kpi_panel_quarterly.csv` (119 cols) | company-quarter | 3Q20-2Q26 | exact totals: `nights_m`, `gbv_musd`, `adr_usd`, `revenue_musd`, `take_rate_pct`, `unearned_fees_musd`, `funds_held_for_clients_musd`, `fx_pts_adr`, `fx_pts_revenue` |
| `data/processed/overnight/10_xbrl_revenue_geography.csv` (258 rows) | filing × geo tag × period | 1Q20-2Q26 | **72 exact quarterly regional revenue cells**, `filed`-dated |
| `data/processed/adr/01_regional_annual.csv` (30 rows) | region-year | 2020-2025 | exact annual regional nights (±0.5M), GBV, revenue; from FY2021-FY2025 10-Ks |
| `data/processed/overnight/02_guidance_ledger.csv` (194 statements) | statement | all 23 prints | qualitative guides → interval constraints |
| `data/processed/overnight/04_consensus_at_print.csv`, `04_current_consensus.csv` | print / vendor | 23 prints / 3-4 Sep 2026 | the benchmark, never an input |

**Interval observations:**

| Path | Count | Note |
|---|---|---|
| `data/processed/overnight/10_regional_panel_quarterly.csv` cols `{r}_nights_yoy_lo/_hi`, `{r}_basis` | **28 genuine buckets**, 4Q24-2Q26 | exclude the **14** `basis='derived…'` rows — model output, not disclosure |
| `data/processed/overnight/10_regional_adr_fx.csv` (93 rows) | 38 reported + 30 ex-FX | integers → ±0.5pp intervals |
| `data/processed/adr/01_regional_annual.csv` `nights_m` | 24 | ±0.5M, with exact sum |
| `data/processed/overnight/27_nights_band.csv`, `27_regional_bucket_check.csv` | 3 / ~28 | existing crude version of this idea; keep as a cross-check, supersede as the estimator |

**Noisy measurements:** `data/processed/adr/08_size_mix_extended_summary.csv` (129 rows, market-level size
wedges with min/median/max), `05_size_mix_summary.csv` (72), `14b_los_adr_term.csv` (75, with
`sens_lo`/`sens_hi`), `13_party_size_adr_quarterly.csv`, `06_wtp_hedonic_coefs.csv`,
`data/processed/overnight/06_quote_line_items.csv` (77 aggregate rows / 1.71M quotes).

**FX and timing:** `data/processed/overnight/10_fx_daily.csv` (19,468), `10_fx_basket.csv`,
`10_fx_quarterly.csv`, `05_fx_schedule.csv` (31), `10_regional_fx_passthrough.csv`,
`28_fx_hedge_disclosures.csv`; kernel priors from `data/processed/h2_bridge/h2_bridge_gbv_lag_conversion.csv`
(3Q23 0.1739, 3Q24 0.1715, 3Q25 0.1718; 4Q 0.1195, 0.1207, 0.1200) and
`data/processed/abnb_backlog_indicators.csv` (24 rows, `unearned_to_next_q_revenue`, `rnpl_gap_pts`).
Sibling R engine: `…/Citadel-ABNB-fx-engine`, `…/FX-ADR-R-model`, map at `FX_ENGINE_MENTAL_MAP.md`.

**Covariates:** `data/processed/overnight/10_eurostat_platform_monthly_latest.csv` (39 months,
Jan 2023-Mar 2026), `10_bench_japan_arrivals_monthly.csv`, `10_bench_canada_travel_monthly.csv`,
`10_regional_benchmarks.csv`, `11_regulatory_overlay.csv` + the 32-factor register / SQLite.

**External data needed (all free, all inside three weeks per `01_ground-truth/05_altdata_landscape.md`):**

1. **Eurostat refresh Apr-Jun 2026** — the repo stops at Mar 2026; the ~150-day publication lag means
   2Q26 lands ~late Aug 2026 and is available now. Free API, ~2 hours.
2. **JNTO (Japan), INE (Spain), ISTAT (Italy), INE (Portugal), Embratur (Brazil), ABS (Australia)
   monthly arrivals with an accommodation-type split** — free portals, ~20 hours to backfill 2024-2026,
   0.5 h/month thereafter. These are the only non-US, non-EU covariates for the APAC and LatAm states.
3. **KPI-level Street consensus (nights, GBV, ADR), not just revenue** — Fiscal.ai Pro ($39/mo) or a
   Zacks/Yahoo key-metrics pull 2-3 days before 5 Nov. Required because M1's output is a *decomposition*
   and "vs Street" is only meaningful line by line. Current KPI consensus coverage is ADR 5/23 prints,
   GBV 12/23, nights 18/23.
4. *(Optional, week 3)* a second Inside Airbnb capture on the same 120-market list, to give the size-mix
   panel a genuine y/y instead of one vintage. Pipeline exists; ~1 day setup.

**Explicitly not used:** Google Trends (mean WF 3.05× naive, 432 tests), aggregate macro as a nights
predictor (1,408 pairs; 5 of 890 Bonferroni survivors, all the FX mechanism or the 2023 normalisation
trend), peer read-across (the "signal" was PIT leakage; the corrected version is worse), management tone.

---

## 4. Estimation and validation

**Engine.** Stan via `cmdstanpy` (NUTS), because interval censoring is native
(`log_diff_exp(normal_lcdf(U|·), normal_lcdf(L|·))`), the simplex is a built-in type, and the
non-centred parameterisation of hierarchical states is standard. PyMC 5 is an acceptable substitute.
A **MAP fallback** — penalised constrained least squares in `scipy.optimize.minimize` with hinge
penalties for the intervals and a softmax reparameterisation for the shares — is ~50 lines, runs in
seconds, and is the cut path if NUTS misbehaves (§7).

**Priors (all pre-registered in a spec file, in the discipline of `data/processed/overnight/20_experiment_spec.json`):**
`φ_g ~ Beta(4,4)` on (−1,1) scaled; `c̄ ~ N(0.08, 0.05²)` (platform nights growth); `τ_c ~ half-N(0, 0.03)`;
`σ_g ~ half-N(0, 0.03)`; `σ_q ~ half-N(0, 0.01)` (regional price convergence); `ψ ~ half-N(0, 0.15)`
(covariate shrinkage); `φ ~ Dirichlet(2·(0.05, 0.62, 0.30, 0.03))` centred on the repo's ⅔/⅓ non-negative
lag fit; `τ_{r,0} ~ N(10-K annual regional take, 0.3pp²)` — 2025 NA 12.89%, EMEA 13.84%, LatAm 13.58%,
APAC 13.97% **[recomputed]**.

**Sample-size honesty.** There are 24 company-quarters. That is fatal for a single-feature quarterly
regression and the repo proved it 3,500 times. It is *not* fatal here, for three reasons I will defend
in the room: (i) the state equations are estimated on **region × quarter** cells — 96 growth cells and
~150 ADR cells — with a *pooled* `φ_g` and hierarchical `c_r`, giving ~16 effective parameters and
6-9 observations per parameter; (ii) the mix terms are estimated at **market × period** grain (129 market
pairs; 1.71M quotes), where n is in the hundreds-to-millions, exactly as the audit's recommendation 8
demands; (iii) **most of the information enters as constraints, not as degrees of freedom** — 72 exact
regional revenue cells, 24 exact totals, 24 exact annual regional cells and 28 intervals shrink the
feasible parameter set without being "fitted to". The genuinely underpowered objects are the covariate
loadings `λ_r`, which is precisely why they carry a shrinkage prior and why their posteriors are published.

**Point-in-time protocol.** Re-fit at each of the 19 guided quarters' guide dates. At guide date `T`:
- filings: only rows of `10_xbrl_revenue_geography.csv` with `filed ≤ T` (mechanical);
- letters/guides: only `02_guidance_ledger.csv` statements with `print_date ≤ T`;
- FX: `10_fx_daily.csv` truncated at `T`, with the forward path from forwards, never realised spot;
- Eurostat: only months whose publication date ≤ `T` (≈150-day lag), from `20_vintage_register.csv`;
- **market panels: excluded entirely from the historical replay.** `analysis/src/overnight/08_altdata_backtests.py:248`
  records that Inside Airbnb scope flags use *later* scrapes, so the panel is **not vintage-reconstructible**.
  In the backtest, `m^size` and `m^los` therefore enter as *time-invariant priors with no data*, which
  makes the historical scores a **lower bound** on the live model. Say that out loud; do not claim the
  backtest validates the mix terms. It validates the censoring machinery and the accounting structure.

**Baselines the model must beat**, on one-quarter-ahead revenue level, expanding window:
(a) seasonal naive; (b) AR(1) on nights × AR(1) on ADR × trailing-4 take; (c) **guide midpoint + trailing-8
median cushion +1.79%** — 1.1% mean error, the strongest level baseline in the repo; (d) the Street
consensus at print, where retrievable. Beating (c) on *level* is hard and I will not promise it; the
honest target is **match (c) on level and beat everything on the decomposition and on the 4Q-guide-direction
call**, because (c) is silent about *why* and is, per `20_temporal-validation.md` §3, the *worst* predictor
of anything relative.

**The free out-of-sample test nobody has run.** The quarterly buckets for year `y` are published quarterly
through `y`; the exact annual regional nights for `y` are published in the 10-K in February `y+1`. So:
fit the model on the buckets alone, form the 80% posterior interval for annual regional nights, and check
coverage against the 10-K. That is **24 clean out-of-sample checks (6 years × 4 regions) with zero
look-ahead**, testing exactly the machinery the method rests on. Target: 19-21 of 24 inside an 80%
interval. If coverage is 24/24 the intervals are too wide and I will say so; if it is 14/24 the method
is rejected. This test costs one afternoon and it is the single most persuasive exhibit available.

**Calibration.** PIT histogram of the 19 one-quarter-ahead predictive distributions; split-conformal
adjustment of the predictive interval using those 19 residuals, so the published FY27 interval has a
finite-sample coverage guarantee that does not depend on the Gaussian assumptions inside the model.

**Live test.** Score `data/processed/overnight/20_frozen_q3_2026.csv` (nights +10.2%, ADR +3.8%, GBV
$26,185M, revenue $4,801M) against MIXSTATE's frozen 3Q26 posterior on 6 Nov 2026 — after the finals, so
it is a calibration record, not a pitch input. Freeze the spec before 2 Oct and increment `spec_id`.

**Why the earlier negatives do not condemn this design — and what they do condemn.**

*Do not condemn:* (i) the failures were **single-feature regressions at n≈10-18 against surprise**;
MIXSTATE adds no aggregate regressors — its covariates are shrunk toward zero and its information is
constraints. (ii) The Inside Airbnb panel failed on **coverage and grain** (13 cities, city count moving
1→13, `n_flagged_r05_perm05 = 0` in both windows) — MIXSTATE uses market panels only for *mix coefficients*
estimated at market grain, never as an aggregate nights predictor. (iii) Eurostat failed as a *forecast*
(mean WF ratio 1.75× naive) and is used here as a *state covariate with a zero-centred prior*, which can
only help or be reported as useless. (iv) The macro failure (zero nights sensitivity) is *assumed true*
by this design: there is no macro term in the nights state.

*Do condemn, and I accept:* any claim that this model will forecast **surprise vs Street** better than a
trailing-4 mean; any claim that Google Trends, peer read-across or call tone adds anything; any backtest
entered at the pre-release close rather than the next open (`20_executable_returns.py`); and any use of
the derived/residual regional rows as data.

---

## 5. Outputs

The model emits a **joint posterior** over all latent states and hence over every derived quantity.
Four named deliverables:

**(a) 3Q26 print (~5 Nov).** Posterior predictive for revenue, Nights-and-Seats, printed ADR, GBV,
take rate. Headline statistics: `P(revenue > $4,770M)` (the top of the guide range, beaten 15/19 times
historically) and `P(nights > 146M)` against the reconstructed 144-146M implied bar
(`04_q3_2026_breakeven.csv`). Anchor: lagged-GBV conversion applied at the 6 Aug guide date gives
$4.78-4.85bn (`01_ground-truth/03_insider_mechanics.md` §1.4); the team's frozen card is $4,801M.
MIXSTATE's contribution is not a different number but a *distribution with an audit trail*.

**(b) The 4Q26 guide midpoint (the real 5 Nov event).** MIXSTATE produces a posterior for 4Q26 revenue;
the guidance-game lens (M3) maps it to a guide range via the cushion distribution (19/19 midpoint beats,
15/19 above the top, trailing-8 median cushion +1.79%). **The headline number of the whole pitch is
`P(guide midpoint < $3,200M Street)`.** The mechanism is arithmetic, not a demand view: 4Q26 revenue FX
is ~84% already determined at about **−0.4pp**, against **+3.0pp** guided for 3Q26 — a −3.4pp step that is
invariant across euro paths (`research/notes/overnight/29_q4-fy27-bridge.md`, `29_fx_step_down.csv`).
The team's FX-anchored bridge puts 4Q26 at $3,111M; the driver model at $3,145M; the Street at $3,200M.
On my read the posterior mass sits materially below the Street. That matters because **"guide below Street"
is the only executable survivor in the repo: 9/9 negative 20-day drift on next-open entry, mean −4.21%,
binomial p 0.0020** (`research/notes/overnight/09_stock-behaviour-and-alpha.md`).

**(c) The FY27 guide (~Feb 2027) and FY27 revenue vs Street $15.73-15.76bn.** Posterior for FY27 revenue
decomposed into **named, non-overlapping** contributions — home nights by region; hotel/seat volume;
like-for-like price; unit-size mix; LOS mix; geographic mix; sub-regional mix; FX translation; recognition
timing; take rate by region; new business outside GBV — each with its own credible interval and each
summing to the total by construction. `P(FY27 < $15,730M)` is the reportable. My prior expectation, to be
replaced by the posterior: the geo-mix-as-output change pulls blended ADR toward the workbook's measured
+1.37% from the model's assumed +2.50% (§3.4, ~$175M), and the take-rate plug removal removes ~+1.05pp of
systematic over-prediction (§3.1, ~$165M), so the central lands **at or below the low end of the Street's
range**, i.e. roughly $15.5-15.7bn, with the Street's $15.76bn sitting in the upper third of the posterior.

**(d) The reconciliation artefact.** Every other FY27 number in the tree — `13` $15,842M, `29` $15,804M,
`14` $15,727.8M, WS10 ~$15,925M, ADR-workbook path ~$15,555M, choice driver ~$15,570M — is expressible as
a **restriction on MIXSTATE's parameters** (e.g. "`14` = MIXSTATE with hotel τ fixed at 11%"; "WS10 =
MIXSTATE with FX = 0 and the calibration applied to drifted rather than base shares"). That turns the
audit's §5 "$370M range with nothing reconciling it" into one table. It is the artefact the audit says
does not exist (recommendation 10) and it is the exhibit that answers "which of your four numbers is it?"

**Uncertainty representation — explicitly not a Monte Carlo.** Three layers:
1. the **posterior** itself, from a likelihood in which every disclosure enters with its true
   informativeness (exact, interval, or noisy). MCMC is the integration method for a posterior conditioned
   on data and falsifiable by held-out prints; a Monte-Carlo scenario model samples assumptions the analyst
   chose. Both draw random numbers; only one is testable. The PIT histogram and the 24-cell annual-coverage
   test are what make the difference operational;
2. a **scenario tree whose branch probabilities are posterior probabilities of latent states** — e.g.
   `P(NA home-nights trend c_na < 4%)`, `P(product lever laps)`, `P(P > hedonic prior + 1pp)` — so the
   bear/base/bull cases carry data-derived weights rather than the customary 25/50/25;
3. **split-conformal** intervals on the one-quarter-ahead revenue forecast calibrated on the 19 pseudo-OOS
   residuals, giving finite-sample coverage that survives model misspecification.

**How my view could differ from the Street, mechanically.** Not on demand. On three arithmetic channels
the sell-side does not model separately: (i) **geographic mix is accelerating** — Törnqvist on the exact
10-K regional table gives a geo drag of **−1.06pp in 2024 and −1.48pp in 2025** against within-region ADR
of +2.71pp and +4.46pp **[recomputed]**, and NA's nights share fell 32.6% → 31.3% → 29.6% while LatAm rose
14.3% → 15.4% → 16.9%; a Street model that forecasts one blended ADR cannot see this deepening;
(ii) **the FY25 take-rate decline is entirely North American** — NA 13.27% (2023) → 13.24% (2024) → **12.89%**
(2025) while EMEA/LatAm/APAC moved −6bps/−8bps/+5bps, so the −16bps blended fall is ~95% NA, coincident with
RNPL's US launch and hotels, and it decomposes as **within-region −1.36pp, regional GBV mix +0.15pp**
**[recomputed]** — a regional signature no one in the repo or, as far as the consensus commentary goes,
on the Street has isolated; (iii) **the 4Q26 FX step is already observed** and the Street's $3,200M
does not appear to carry it.

---

## 6. Minimal code skeleton

```stan
// M1 MIXSTATE — chain-linked conditional-index state space.  Stan (cmdstanpy).  Pseudo-code where noted.
data {
  int<lower=1> T; int<lower=1> R;                  // T quarters 3Q20..4Q27, R=4 {na,emea,latam,apac}
  // EXACT — data/processed/overnight/02_kpi_panel_quarterly.csv
  int To; vector[To] lnN_tot; vector[To] lnGBV_tot; vector[To] lnRev_tot; int obs_t[To];
  // EXACT — 10_xbrl_revenue_geography.csv (+ Q4 backed out vs adr/01_regional_annual.csv); filed-dated
  int Nr; int rv_t[Nr]; int rv_r[Nr]; vector[Nr] lnRev_reg;
  // INTERVAL — 10_regional_panel_quarterly.csv {r}_nights_yoy_lo/_hi, basis=='bucket' ONLY (28 rows;
  //            the 14 basis=='derived...' rows are model output, NOT data — excluded upstream)
  int Nb; int b_t[Nb]; int b_r[Nb]; vector[Nb] b_lo; vector[Nb] b_hi;
  // INTERVAL — 10_regional_adr_fx.csv, integers => +-0.5pp ; adr/01_regional_annual.csv nights +-0.5M
  int Na; int a_t[Na]; int a_r[Na]; vector[Na] a_lo; vector[Na] a_hi;
  int Ny; int y_yr[Ny]; int y_r[Ny]; vector[Ny] y_lo; vector[Ny] y_hi;
  // NOISY — adr/08_size_mix_extended_summary.csv, adr/14b_los_adr_term.csv
  matrix[T,R] size_hat; matrix[T,R] size_se; matrix[T,R] los_hat; matrix[T,R] los_se;
  matrix[T,R] lnXB; matrix[T,R] lnXC;              // 10_fx_daily.csv -> booking / check-in indices
  matrix[T,R] z;                                   // 10_eurostat_platform_monthly_latest.csv + JNTO/INE
  matrix[T,R] d;                                   // dated product-lever dummies w/ lap structure
}
parameters {
  vector[T] lnNhome;                               // total home nights (log level)
  matrix[T,R-1] u;                                 // softmax pre-shares  => sum_r n_r = N BY CONSTRUCTION
  matrix[T,R] g; real<lower=-1,upper=1> phi_g;     // Dlog4 home nights state; pooled AR(1)
  matrix[T,R] c; real cbar; real<lower=0> tau_c; real<lower=0> sig_g;
  vector[R] lam; real<lower=0> psi; vector[R] del;
  vector[T] p; matrix[T,R] q; real<lower=0> sig_p; real<lower=0> sig_q;   // price: global + shrunk dev
  matrix[T,R] msize; matrix[T,R] mlos; matrix[T,R] msub;                  // mix states
  vector[T] lnNhotel; vector[T] lnSexp; vector[T] lnSsvc;                 // seats / rooms states
  simplex[4] varphi; matrix[T,R] tau;                                     // book->checkin kernel; take
}
transformed parameters {
  matrix[T,R] s; matrix[T,R] lnn; matrix[T,R] lna; matrix[T,R] lnGBVr; vector[T] lnN_pr; vector[T] lnGBV;
  for (t in 1:T) s[t] = softmax(append_col(0.0, u[t]))';                  // exact adding-up
  lnn = rep_matrix(lnNhome,R) + log(s);
  for (t in 5:T) for (r in 1:R)                                            // ADR chain, level 5 -> 0
    lna[t,r] = lna[t-4,r] + p[t] + q[t,r] + msize[t,r] + mlos[t,r] + msub[t,r] + (lnXB[t,r]-lnXB[t-4,r]);
  for (t in 1:T) {
    lnGBVr[t] = lnn[t] + lna[t];                                           // regional GBV, USD @ booking
    lnN_pr[t] = log(sum(exp(lnn[t])) + exp(lnNhotel[t]) + exp(lnSexp[t]) + exp(lnSsvc[t]));
    lnGBV[t]  = log(sum(exp(lnGBVr[t])) + /* hotel + seats GBV, pseudo-code */ 0);
  }                                                                        // printed ADR = lnGBV - lnN_pr
}
model {
  phi_g ~ beta(4,4); cbar ~ normal(0.08,0.05); tau_c ~ normal(0,0.03);     // half-normals via <lower=0>
  sig_g ~ normal(0,0.03); sig_q ~ normal(0,0.01); psi ~ normal(0,0.15); lam ~ normal(0,psi);
  varphi ~ dirichlet(to_vector({0.10,1.24,0.60,0.06}));                    // centred on 2/3, 1/3 lag fit
  for (t in 5:T) for (r in 1:R) {
    g[t,r] ~ normal(c[t,r] + phi_g*(g[t-1,r]-c[t-1,r]) + lam[r]*z[t,r] + del[r]*d[t,r], sig_g);
    target += normal_lpdf(lnn[t,r] | lnn[t-4,r] + g[t,r], 1e-4);           // state <-> level link
    q[t,r] ~ normal(0,sig_q); msize[t,r] ~ normal(size_hat[t,r], size_se[t,r]);
    mlos[t,r] ~ normal(los_hat[t,r], los_se[t,r]); msub[t,r] ~ normal(0,0.01);
  }
  p[2:T] ~ normal(p[1:T-1], sig_p);  // prior mean from the 06_quote_line_items.csv hedonic (pseudo-code)
  for (i in 1:To) { target += normal_lpdf(lnN_tot[i] | lnN_pr[obs_t[i]], 1e-6);      // exact totals
                    target += normal_lpdf(lnGBV_tot[i] | lnGBV[obs_t[i]], 1e-6); }
  for (i in 1:Nr) {                                                         // exact regional revenue
    real mu = log(tau[rv_t[i],rv_r[i]]) + lnXC[rv_t[i],rv_r[i]] - lnXB[rv_t[i],rv_r[i]]
            + log(dot_product(varphi, exp(to_vector(lnGBVr[(rv_t[i]-3):rv_t[i], rv_r[i]]))));
    target += normal_lpdf(lnRev_reg[i] | mu, 1e-6); }
  for (i in 1:Nb) target += log_diff_exp(normal_lcdf(b_hi[i]|g[b_t[i],b_r[i]],0.004),   // nights buckets
                                         normal_lcdf(b_lo[i]|g[b_t[i],b_r[i]],0.004));
  for (i in 1:Na) target += log_diff_exp(normal_lcdf(a_hi[i]|lna[a_t[i],a_r[i]]-lna[a_t[i]-4,a_r[i]],0.004),
                                         normal_lcdf(a_lo[i]|lna[a_t[i],a_r[i]]-lna[a_t[i]-4,a_r[i]],0.004));
  for (i in 1:Ny) target += log_diff_exp(normal_lcdf(y_hi[i]|/*annual sum of lnn, pseudo*/0,0.01),
                                         normal_lcdf(y_lo[i]|0,0.01));      // 10-K annual, +-0.5M, 24 cells
}
generated quantities { /* posterior predictive 3Q26..4Q27 revenue; P(4Q26 guide mid < 3200);
                          P(FY27 < 15730); named contribution decomposition summing to the total */ }
```

---

## 7. Three-week build plan (3-4 undergraduates)

Roles: **A** = state-space/Stan; **B** = data-construction and PIT; **C** = decomposition and validation;
**D** = FX, mix panels, exhibits.

**Week 1, day by day**

- **D1 (Fri 11 Sep).** *B*: build `01_exact_regional_revenue.csv` — quarterly regional revenue 1Q22-2Q26
  from `10_xbrl_revenue_geography.csv` (filter to 80-100 day periods), Q4 backed out against
  `adr/01_regional_annual.csv`; assert reproduction of 4Q23/4Q24/4Q25 totals to $1M (it does — verified).
  Carry the `filed` date on every row. *A*: repo/env setup, cmdstanpy + a 20-line censored-normal toy that
  recovers a known interval-censored mean.
- **D2.** *B*: build `02_interval_observations.csv` — one row per observation with
  `(t, region, quantity, lo, hi, source_path, knowable_from)`, covering the 28 genuine buckets, the 38+30
  regional ADR integers, the 24 annual nights cells, and the guidance-ledger qualitative guides.
  **Hard rule, written into the file's header: the 14 `basis='derived…'` rows are excluded.**
  *C*: reproduce the Törnqvist annual decomposition (2024→25: within +4.46pp, geo −1.48pp; take −1.21pp of
  which NA −35bps) and reconcile to `data/processed/adr/07_full_decomposition.csv`.
- **D3.** *D*: booking-date and check-in-date FX indices per region from `10_fx_daily.csv` +
  `10_fx_basket.csv`, cross-checked against `10_regional_fx_passthrough.csv` (EMEA 1.043, APAC 0.86,
  LatAm 0.62) and the sibling R engine. *A*: **MAP version** — penalised constrained least squares in
  `scipy`, softmax shares, hinge penalties for intervals, exact constraints as equalities.
  **Milestone: the MAP fit must place all 24 annual regional nights cells inside their ±0.5M intervals
  while reproducing every quarterly total exactly.** If it cannot, the disclosures are mutually
  inconsistent and that is itself a finding to report.
- **D4.** *A*: port MAP → Stan, non-centred, MAP as init, 4 chains × 2,000. *C*: build the PIT harness —
  a function `fit(as_of_date)` that filters every input by `knowable_from ≤ as_of_date`.
  *D*: joint hedonic on `06_quote_line_items.csv` + `08_size_mix_extended_summary.csv` for the `m^size`,
  `m^los` priors and the like-for-like price prior; reconcile the bedrooms-per-log-capacity discrepancy
  (docstring 1.27 vs computed 1.37, `adr/13_party_size_adr.py:7` vs `:64`).
- **D5.** *All*: **the free OOS test** — fit on buckets only, predict annual regional nights, score coverage
  over 24 cells. Publish the number whatever it is. *B*: pull the Eurostat Apr-Jun 2026 refresh; start the
  JNTO/INE/ISTAT backfill. **Week-1 gate: MAP + Stan both run, OOS coverage reported, exact constraints hold.**

**Week 2 — milestones**

M1. NUTS converged (R̂ < 1.01, ESS > 400 on all reported quantities), posterior-vs-prior contraction table.
M2. `φ` kernel and regional `τ` estimated off the 72-cell exact regional revenue panel; compare the implied
Q3/Q4 conversions to the measured 17.4/17.1/17.2% and 12.0/12.1/12.0%.
M3. Expanding-window PIT backtest at all 19 guide dates vs the four baselines; PIT histogram; conformal
calibration.
M4. First full FY26/FY27 posterior with the named-contribution decomposition; `P(4Q26 guide mid < $3,200M)`,
`P(FY27 < $15,730M)`.
M5. The model-to-model reconciliation table (§5d): each of the six existing FY27 estimates as a parameter
restriction.

**Week 3 — milestones**

M6. Freeze the spec file and `spec_id` before 2 Oct; register the 3Q26 / 4Q26-guide / FY27 posteriors.
M7. Ordering-reversal test on the Törnqvist chain; prior-sensitivity on the price residual.
M8. Memo exhibits: (i) the decomposition waterfall FY26→FY27 with credible intervals; (ii) the
`(P, M^sub)` joint credible region; (iii) `P(guide < Street)` with the 9/9 drift base rate; (iv) the
reconciliation table. M9. Dry-run Q&A against §8.

**What can be cut, in order:** (1) the covariates `z` — set `λ = 0`; the model is a constrained accounting
system and still works; (2) Stan → MAP only, with conformal intervals doing all the uncertainty work;
(3) separate seats/hotel states → fold hotel into homes at a fixed ADR ratio 0.81 and a fixed seat share;
(4) FY28 entirely (the horizon is 3-12 months); (5) the second Inside Airbnb capture; (6) the regulatory
DiD → keep `11_regulatory_overlay.csv` as an exogenous overlay with its interval published.
**What cannot be cut:** the exact regional revenue panel, the interval-observation file, the softmax
adding-up, and the 24-cell OOS coverage test. Those four *are* the method.

---

## 8. Failure modes and the hostile-judge script

**"This is a Kalman filter with thirty priors — you fit the answer."** The incumbent has **12 plugs and 18
assumed parameters** between inputs and FY27 revenue (`02_model_audit.md` §2), none with an error bar.
MIXSTATE has ~16 estimated parameters, every one with a published posterior, a pre-registered prior, and a
prior-to-posterior contraction statistic. And it passes a 24-cell out-of-sample test that the incumbent
cannot even be asked to take.

**"n = 24 quarters. You cannot fit a state-space model."** Correct for a model with 24 free parameters; this
one has ~16 and roughly 190 informative observations, 120 of which are *exact constraints* that reduce the
feasible set rather than consume degrees of freedom. The honest weak point is `λ_r`; it is shrunk and
published. And the model degrades gracefully: with `λ = 0` and `z` dropped it is a constrained accounting
identity that still beats the incumbent's take×wedge construction, whose perfect-foresight backtest error
is +0.53% with sd 1.97% against a `φ`-kernel whose Q3 conversion has a 0.3pp range over three years.

**"MCMC is Monte Carlo and you were told not to."** MCMC integrates a posterior defined by a likelihood
over *observed* data; a Monte-Carlo scenario model samples assumptions the analyst wrote down. The test is
whether the distribution is falsifiable: mine is, by the PIT histogram over 19 guide dates and by the
24-cell coverage test. Run the same test on a scenario Monte Carlo and there is nothing to score.

**"The bands are marketing language; you are over-reading them."** The interval likelihood is *strictly
weaker* than what the incumbent does, which is to take the midpoint. The evidence that midpoints are wrong
is in the repo: `27_regional_bucket_check.csv` shows midpoint sums leaving −0.51pp (4Q24) and −0.23pp (1Q25)
residuals, and `10_regional_panel_quarterly.csv` `residual_vs_total_pp` reaches **−1.06pp in 2Q26**, whereas
interval-feasible points close the total exactly. If a judge insists the bands are uninformative, I widen
them to ±3pp and show the posterior barely moves, because the exact regional revenue panel is doing most of
the work.

**"Your price residual is still unidentified, so your ADR forecast is a guess."** Yes, jointly with
sub-regional mix, and the memo says so in those words. It is reported as a 2-d credible region with an
independent hedonic prior, and I publish `∂FY27/∂(prior mean)`. The FY27 call is built to survive at the
prior mean, not at the top of the ridge.

**"Four regime breaks in five quarters — RNPL US, RNPL global, the seats denominator, the fee migration.
Your state equations are fitted on a different business."** That is the strongest attack. Answers: each
break is a dated, modelled level shift with an explicit lap (`d_t`); the seats break is handled by
*definition* because I model home nights and let the printed denominator be an identity; the fee migration's
deadlines (15 Sep 2026 ex-EEA, 13 Oct 2026 EEA) fall inside 3Q26/4Q26 and enter as a dated `M^prod`/price
shift with a wide prior, not as zero. I will not claim the posterior is tight through 1Q27; I will show it
widening there, which is the honest picture and is itself a differentiated statement.

**"The mix panels are a single vintage and not vintage-reconstructible, so your backtest is contaminated."**
Pre-empted: the historical replay runs with the mix terms as time-invariant priors and **no market data at
all** (`08_altdata_backtests.py:248`). The backtest therefore *understates* the live model and validates the
censoring and accounting structure only. Stated in the memo, not buried.

**"You are just going to land on the Street."** Possible, and if the posterior lands on $15.75bn the pitch
becomes a 4Q26-guide call rather than an FY27 call — which is the better trade anyway, given that "guide
below Street" is the only executable survivor in the repo and FY27 guidance does not arrive until after the
finals.

**Model risks I will flag unprompted:** disclosure discontinuation (regional buckets could stop, as
cross-border did in 1Q24 and urban in 4Q23 — Airbnb drops metrics that stop flattering); the direct-link
host-fee pilot (29 Aug 2026), at 10% of nights and an 8pt discount, is worth −0.8pt of blended take rate,
larger than the entire single-fee benefit, and is in no filing; and the `single_fee_pct` column in
`02_kpi_panel_quarterly.csv` carries **15.5 at 4Q25, which is the fee *rate*, not the migrated share** —
re-key it before anyone regresses on it.

---

## 9. Interlock with the other five lenses

**Consumes:**
- *M2 (nowcast tracker)* → the covariate matrix `z` at market × month, aggregated to region with the
  vintage lag attached. MIXSTATE shrinks whatever M2 delivers and reports its posterior loading, which is
  also the cleanest possible *evaluation* of M2: a coefficient with a credible interval instead of a
  walk-forward ratio at n = 12.
- *M4 (bottom-up markets)* → the joint hedonic coefficients (capacity, bedrooms, LOS bucket, market FE)
  that become the priors for `m^size`, `m^los`, and the regulatory DiD treatment intensity by market, which
  becomes the regulatory covariate on the nights state — replacing `REG_DRAG_PP` and the `reg_mult = 1.67`
  median-to-mean fudge.
- *M6 (FX / take rate / timing)* → `X^B`, `X^C`, the `φ` kernel prior, and the regional `τ` mechanism
  bridge (fee migration, FX service fee, RNPL share of GBV, hotel/Services mix). M6 owns the kernel;
  MIXSTATE owns the GBV that the kernel convolves.

**Hands over:**
- *M3 (guidance game)* ← the posterior for 4Q26 and FY27 revenue **and**, more usefully, the posterior for
  *what management can already see at guide date*: the `φ`-convolution of GBV already booked. That is the
  operating-state regressor in the guidance policy function `guide_mid_{q+1} = f(operating state, cushion
  history, FX already realised)`. MIXSTATE turns "85-90% determined" from a sentence into a distribution.
- *M5 (ML challenger)* ← the two objects the structural model deliberately leaves unexplained: the
  like-for-like **price residual** `P` and the **position of each realised regional growth inside its
  disclosed band**. Both are defined at market × month grain where n is in the thousands — the only grain
  at which the repo's own evidence says ML has a chance (`02_model_audit.md` rec. 8). ML predicting a
  structural residual is a legitimate challenger; ML predicting aggregate nights at n = 20 is the failure
  the repo already ran 3,500 times.
- *All lenses* ← the **reconciliation table**. Once every existing build is a parameter restriction on one
  model, the team can answer "which of your four numbers is it?" in one slide, which is the question the
  audit says a Citadel PM will find in ninety seconds.

**The division of labour in one line:** M1 owns the *identity and its posterior*; M6 owns *timing and
currency*; M4 owns *market-level coefficients*; M2 owns *high-frequency state covariates*; M5 owns
*residuals*; M3 owns the *map from the revenue posterior to the guide and to the trade*.
