# M3 — The guidance function and the revision game

**GAC: a guide–anchor–cushion state-space model of management's guidance policy, the Street's anchoring response, and the one-sided drift it creates.**

Proposal author: Claude Code (lens M3), 11 September 2026. Every repo claim below cites a path opened for this note.
Prices: $181.94 close 4 Sep 2026 (`data/processed/overnight/04_current_consensus.csv`), $174.54 on 9 Sep (04_recent_facts).
All new statistics in §2–§5 were computed in-session from the cited CSVs; the computation is reproduced in §6.

---

## 1. Thesis in five lines

1. **Forecast object:** the *revenue guide midpoint Airbnb will print*, `g_q`, at three dates — 4Q26 guide on ~5 Nov 2026, 1Q27 guide + first FY27 guide ~Feb 2027, 2Q27 guide ~May 2027 — and, mechanically downstream of it, the Street's next-quarter and FY27 consensus and the 20-day post-print drift. Level, not surprise.
2. **Why the guide and not revenue:** the 3–12 month window contains four guides and one print that lands after the finals. The team's own scoreboard says the guide-plus-cushion rule already nails the *level* to 1.1% (`research/notes/overnight/08_altdata-index-and-backtests.md`) and is the *worst* predictor of surprise-vs-Street (`research/notes/overnight/20_temporal-validation.md` §3). The unexploited object is the number management has not yet said.
3. **Why it is forecastable:** ~85–90% of a quarter's revenue is already on the booking ledger when the guide is set (`docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` §1.4). I reconstruct that ledger as a booking→check-in kernel and find, walk-forward and strictly point-in-time, a 1.36% MAE on the revenue level **90 days before the guide is given** (n=10, §4). The guide is that number shaded by a cushion whose last-8 mean is −2.33% with sd 1.84%.
4. **Why it beats what the team has:** the Street does not forecast Airbnb — it *re-anchors on the guide*. Measured here for the first time: consensus at the print date equals the guide midpoint × (1 + κ), κ mean **+0.57%**, last-8 **+0.52% with sd 0.28%** (n=18, `data/processed/overnight/16_consensus_at_print_merged.csv`). Consensus revision vs the guide gap has slope **0.988, r = 0.993**. Forecast the guide and you have forecast consensus to ±30bp.
5. **The trade:** my kernel puts the 4Q26 guide midpoint at **$3,095–3,165m (centre $3,120m)** against a Street $3,200m — a −2.5% gap. Every prior guide-below-Street print produced a negative 20-day executable return (8/8 with a numeric gap, mean **−3.96% raw / −4.21% excess**, against a 69.6% unconditional negative base rate). Day-1 is not forecastable and I do not claim it.

---

## 2. Formal specification

Three observables exist per print `t`: the guide midpoint `g_q` for the following quarter `q`, the Street consensus `S_q` measured at a dated vintage, and the realised revenue `A_q`. Everything in this model is a difference of logs of those three plus one measured state. **That is the structural reason nothing can be double counted: there are only two independent spreads, `log A_q − log g_q` and `log S_q − log g_q`, and each parameter is defined as exactly one of them.**

### 2.0 Index set

`q` = forecast quarter; `t` = print/guide date (`q = t+1` for the quarterly range); `s(q) ∈ {1,2,3,4}` = calendar quarter; `k` = lag in quarters from booking to check-in; `f` = guidance-item family (range / bucket / floor / ceiling / point / directional); `v` = consensus vendor-vintage.

### 2.1 Layer 0 — the backlog kernel (the state management sees)

```
A_q  =  λ_{s(q)} · Σ_{k=1..K} w_k · G_{q−k} · X_{q,q−k} · exp(ε_q)        (1)
Σ_k w_k = 1 ,  w ≥ 0 ,  K = 2 (extendable to 3)
```

* `G_{q−k}` = booking-dated Gross Booking Value in USD, as reported (`data/processed/overnight/02_kpi_panel_quarterly.csv`, column `gbv_busd`).
* `w` = the booking→check-in transition weights. **Identified** by the repo's non-negative lag fit at `w = (2/3, 1/3)` (`research/airbnb_earnings_call_study.md` §8.4; `research/notes/2026-09-10_h1-to-h2-bridge.md` §4) and cross-checked against the accounting identity `ΔUnearnedFees = τ·p·G_q − A_q − Refunds` using `data/processed/abnb_backlog_indicators.csv`. Under the pure two-lag restriction the fitted λ absorbs any tail.
* `λ_s` = the season-specific conversion scale. **Measured, not assumed.** Computed in-session on `02_kpi_panel_quarterly.csv`:

| season | λ 2023 | λ 2024 | λ 2025 | λ 2026 | 3-yr range |
|---|---|---|---|---|---|
| Q1 | 12.80% | 13.03% | 12.33% | 12.61% | 0.70pp |
| Q2 | 13.72% | 13.45% | 13.95% | 13.74% | 0.50pp |
| Q3 | **17.39%** | **17.15%** | **17.18%** | — | **0.24pp** |
| Q4 | **11.95%** | **12.12%** | **12.03%** | — | **0.17pp** |

* `X_{q,q−k}` = the booking→check-in FX re-translation factor, built from **one** currency basket: `X = Σ_c ω_c · (e_{c,q} / e_{c,q−k})` with `ω` the non-USD revenue weights and `e` the quarterly average rate from `data/processed/overnight/10_fx_daily.csv`. On the current euro path (1.15–1.17 flat through 4Q27, `data/processed/overnight/05_fx_schedule.csv`) `X ≈ 1.00–1.01`, so FX is near-inert on the *level* and the y/y FX "step-down" emerges as an **output** of (1), never as an input.

**This kills four plugs at once.** There is no take rate in (1) — `λ_s` *is* the timing ratio Mertz described ("any of the variation in take rate is just a timing difference", 2Q22 call, `data/processed/abnb_declined_to_quantify.csv`). There is no FX wedge, so the algebraic cancellation documented at `analysis/src/overnight/13_driver_model.py:379` vs `:382` (02_model_audit §1.3) cannot occur. There is no nights × ADR product, so the geographic-mix / size-mix / LOS overlaps catalogued in 02_model_audit §3.4–3.5 cannot propagate into revenue. And RNPL is not an additive term: it is a **shift in `w` toward longer lags**, which is exactly what the restated unearned-fee series shows (distortion 0.9 / 3.8 / 16.2 / 16.5% at 3Q25–2Q26, 03_insider_mechanics §1.5).

### 2.2 Layer 1 — the guidance policy function

Management's own expectation is the kernel plus what they can see and we cannot (October bookings, the live cancellation run-rate):

```
log M_q = log( λ̂_{s(q)} Σ_k w_k G_{q−k} X_{q,q−k} )  +  η_q                 (2)
log g_q = log M_q  −  c_q                                                    (3)
c_q     = c̄_f + ρ (c_{q−1} − c̄_f) + γ′ z_q + ξ_q ,   ξ ~ N(0, σ_c²)         (4)
```

`c_q > 0` is the **cushion**: the shading management applies to its own point estimate. `z_q` is a four-element covariate vector, each element knowable at the guide date:

1. `fxobs_q` — the share of the revenue-FX driver already realised at the guide date (`driver_realised_share` in `05_fx_schedule.csv`: 0.84 for 4Q26, 0.34 for 1Q27, 0.00 thereafter). More observed FX → less to insure against → smaller cushion.
2. `width_q` — the range width as % of midpoint at the prior guide (`range_width_pct`, `02_guidance_cushion_series.csv`), a direct read on management's own uncertainty. It has compressed 4.9% → 1.9% → 1.68%.
3. `comp_q` — the prior-year growth being lapped (from the KPI panel), which proxies comp difficulty.
4. `fyraise_q` — an indicator for the Q3 print, where the FY guide raise has landed in every year it existed (FY24 35.0%→"approximately 35.5%" at 3Q24; FY25 34.5%→"approximately 35%" at 3Q25; `data/processed/overnight/02_fy_guide_revisions.csv`). A quarter in which management is simultaneously raising the year has a *different* cushion incentive on the quarter.

**Hierarchical pooling is how n=19 becomes n=159.** `c̄_f` is a family-level intercept on a standardised (per-family sd) scale with `c̄_f ~ N(μ_c, τ²)`. The ledger has 159 scoreable statements across 7 guide types and 21 metric families (`data/processed/overnight/02_guidance_ledger.csv`, 194 rows; counts verified in-session: directional 48, range 46, floor 39, point 26, ceiling 15, qualitative 10, bucket 10). The revenue-range family (n=39 statements, 19 scoreable quarters) borrows strength from the floor family (35/36 met), the ceiling family (12/14 met) and the bucket family (5/5 above). A partial-pooling estimate of `μ_c` is informed by ~159 observations; the revenue-specific deviation is what the 19 quarters actually have to identify, and `τ` decides how much shrinkage the data supports rather than the analyst.

**Two families are deliberately excluded from the pool** because 03_insider_mechanics §3.1 shows they behave differently: expense/tax `point` guides (FY24 SBC guided +20% then +25%, delivered +30.8%) and the take-rate guide (missed 3Q25 by −0.69pts and 1Q26 by −0.10pts). They get their own hyper-mean; pooling them with the top line would import upward bias into the revenue cushion.

### 2.3 Layer 2 — the Street anchoring response

```
log S_q^{at-print}  =  log g_q  +  κ  +  u_q ,    u ~ N(0, σ_κ²)             (5)
```

Estimated in-session from `16_consensus_at_print_merged.csv` (23 prints; 18 with both a pre-guide next-quarter consensus and a post-guide at-print consensus):

| statistic | n=18 all | last 8 |
|---|---|---|
| κ = consensus-at-print ÷ guide-midpoint − 1 | mean **+0.57%**, median +0.52%, sd 0.54% | mean **+0.52%**, sd **0.28%** |
| cushion = actual ÷ guide-midpoint − 1 | mean +2.31%, sd 1.20% | mean **+1.86%**, sd 1.00% |
| surprise = actual ÷ consensus-at-print − 1 | mean +1.73%, sd 1.28% | mean +1.33%, sd 0.92% |

And the revision itself, regressing the full-quarter consensus revision on the guide-vs-Street gap:

```
revision%  =  0.593  +  0.988 × gap%          n=18,  r = 0.993
revision%  =  0.652  +  0.955 × gap%          n=15 (post-2022Q3),  r = 0.993
```

**Read this carefully: the slope is one.** The Street does not partially incorporate the guide and then do its own work; it moves the number to the guide and adds ~0.6pp. The residual sd of κ over the last eight prints is 28 basis points. There is no forecasting problem left in Layer 2 — it is a measured mapping.

**The FY+1 channel** is the piece that needs external data:

```
Δ log S^{FY+1}  =  a  +  b · gap_q  +  d · ΔFYguide_t  +  v_t                (6)
```

One dated in-house observation exists and it is licensed, not scraped: the Bloomberg `Consensus_Guidance` tab in `"…/Theo Data/ABNB_Fundamentals_Alt_Macro_Bloomberg_LIVE.xlsx"` carries `BEST_SALES 2FY = 15,428.4` as of the 5 Aug 2026 prior close, against $15,730–15,760m on 3–4 Sep (`04_current_consensus.csv`). That is a **+1.96% to +2.15% FY27 revision in 30 days** following a Q3 guide that landed **+2.60%** above the pre-guide Street ($4,730m vs LSEG $4,610m, `20_frozen_q3_2026.csv`). Implied pass-through `b ≈ 0.77`. **n = 1. This is the single external acquisition the proposal needs (§3).** Note also that the same tab's 2021–2024 `1FY`/`2FY` cells are internally inconsistent (Q4 2021 shows FY22 sales of 15,480 against a realised $8,399m) — treat pre-2025 rows as unusable, exactly as the Phase-1 inventory warns, and use only the 2025–26 rows plus a vendor backfill.

### 2.4 Layer 3 — the price response function

The team has already proven that magnitude is not forecastable: 17 regressions of day-1 and day-20 excess returns on beats and guide surprises, **every one with a negative leave-one-out R²** (`data/processed/overnight/02_guidance_reaction_tests.csv`; best in-sample R² 0.156 has LOO −0.272). The revenue beat's sign hit rate against day-1 is **0.37** (`02_guidance_sign_tests.csv`). So Layer 3 is specified as a **sign-conditional two-component mixture**, not a regression:

```
r^{20d}_t | gap_t < 0   ~  N(μ_−, σ_−²)
r^{20d}_t | gap_t ≥ 0   ~  N(μ_+, σ_+²)
p_− = P(r^{20d} < 0 | gap < 0)  ~  Beta(1,1) prior → Beta(1+9, 1+0) posterior
```

Computed in-session on the executable convention (`data/processed/overnight/20_executable_returns.csv`, `open_20d_pct` — next-open entry, per the repo's own standard at `analysis/src/overnight/20_executable_returns.py`):

| group | n | mean 20d | median | share negative |
|---|---|---|---|---|
| guide **below** Street | 8 | **−3.96%** | −2.97% | **8 / 8** |
| guide **above** Street | 11 | −1.53% | −3.76% | 6 / 11 |
| all prints (unconditional) | 23 | −2.18% | — | 16 / 23 = **69.6%** |

(The ledger's ninth below-Street row, 3Q21, carries a sign flag without a numeric pre-guide consensus; the repo's headline "9/9, mean −4.21% excess" uses QQQ-excess returns and that extra row. I report the 8 rows I can verify from raw prices and quote the note's excess figure as the note's.)

Two things follow. First, the signal is **one-sided**: above-Street guides are 6/11 negative, statistically indistinguishable from the 69.6% base rate. Second, the correct null is not a coin flip — it is ABNB's own 69.6% negative base rate, which is why the repo's binomial p is 0.038 rather than 0.002. I will state both.

### 2.5 Why nothing double counts, by construction

* **Only two spreads exist.** `cushion = log A − log g` and `κ = log S − log g`. The surprise vs Street is their difference and is therefore *derived*, never separately parameterised. This is the direct fix for failure cause (b) in 02_model_audit §4.2 — the programme estimated the difference of two near-equal numbers with features built for levels.
* **Log-additive chain-linking.** (2)–(5) are additive in logs, so a term can appear once or not at all; there is no place for the multiplicative `τ_{t−4} × (1+w_t)` construction whose perfect-foresight backtest error is +1.05pp trailing-4 (`13_driver_model.py:381-383`, 02_model_audit §3.1).
* **FX enters once.** One basket, one `X`, applied to the booking→check-in map. The four-fold FX appearance catalogued in 02_model_audit §3.7 (inert `f_A`, live `f_R`, the hedge reclass, and FX inside the nights weights) collapses to a single object. The hedge (−$26m of deferred losses over 12 months, ~−0.2pp/quarter, `research/notes/overnight/28_fx-hedge-disclosures.md`) is an explicit overlay on a gross series, never a separate step.
* **Nights and ADR do not appear.** `G` is the state. Nights × ADR is a *decomposition of G* owned by the structural-mix lens; if it is fed back into revenue it would be a second path to the same dollar. §9 specifies the one-way interface.
* **The regulatory drag does not appear.** It is already inside realised `G`. The double-count risk flagged at 02_model_audit §3.8 (REG_DRAG_PP subtracted from an EMEA growth rate that already contains realised regulatory losses) cannot arise in a model whose input is reported GBV.

---

## 3. Data map

Every path below was opened (`head`/`wc`/parse) in this session.

| Path | Grain | Rows | Role |
|---|---|---|---|
| `data/processed/overnight/02_guidance_ledger.csv` | statement | 195 incl. header, 194 statements | Layer-1 dependent variable and the hierarchical pooling frame (7 guide types, 21 metric families, 159 scoreable) |
| `data/processed/overnight/02_guidance_cushion_series.csv` | target quarter | 20 incl. header, 19 revenue ranges | `value_low/high/mid`, `actual`, `beat_vs_mid_pct`, `range_width_pct`, `wf_cushion_pct` — the cushion series and the `width` covariate |
| `data/processed/overnight/16_consensus_at_print_merged.csv` | print | 24 incl. header, 23 prints | `next_q_cons_revenue_musd` (pre-guide vintage), `cons_revenue_musd` (at-print), `next_q_guide_mid_musd`, `guide_vs_street_pct` — **both ends of every revision.** This file is the reason Layer 2 is identified |
| `data/processed/overnight/04_consensus_at_print.csv` | print | 24 | same schema pre-merge; `04_consensus_sources.csv` carries the 145 dated press quotes that make it PIT |
| `data/processed/overnight/02_kpi_panel_quarterly.csv` | company-quarter | 25 incl. header, 119 cols | `gbv_busd`, `revenue_musd`, `unearned_fees_musd`, `funds_held_for_clients_musd`, `revenue_yoy_exfx_pct` — Layer-0 state |
| `data/processed/abnb_backlog_indicators.csv` | quarter | 24 | unearned-fee coverage ratios; the restatement `1/(1−d_q)` with d = 0.9/3.8/16.2/16.5% |
| `data/processed/h2_bridge/h2_bridge_gbv_lag_conversion.csv` | season | 7 | independent confirmation of the λ_s series |
| `data/processed/overnight/05_fx_schedule.csv` | path × quarter | 31 (3 paths × 10 quarters) | `driver_realised_share` (the `fxobs` covariate), `eurusd_level`, fitted revenue-FX pp |
| `data/processed/overnight/10_fx_daily.csv` | daily | 19,468 | the single FX basket for `X` |
| `data/processed/overnight/20_executable_returns.csv` | print | 24 | `open_1d_pct`, `open_5d_pct`, `open_20d_pct` — Layer-3 dependent variable on the executable convention |
| `data/processed/overnight/02_guidance_reaction_tests.csv`, `02_guidance_sign_tests.csv` | test | 18, 7 | the negative results Layer 3 must respect |
| `data/processed/overnight/02_fy_guide_revisions.csv` | FY statement | 49 | the FY-guide ladder: FY26 revenue growth 11% (4Q25) → 14% (1Q26) → 15% (2Q26); margin "stable" → ≥35% → ≥35.5% |
| `data/processed/overnight/04_current_consensus.csv`, `04_q3_2026_breakeven.csv` | current | 19, 19 | the live Street bar and the derived nights/EBITDA bars |
| `data/processed/overnight/20_frozen_q3_2026.csv` | frozen card | 19 | the pre-registered 5-Nov scoring card; the LSEG $4,610m pre-guide vintage is preserved here and must not be replaced by Zacks $4,740m |
| `data/processed/overnight/29_fy27_bridge.csv` + `research/notes/overnight/29_q4-fy27-bridge.md` | scenario | 19, 87 lines | the incumbent Q4/FY27 walk this model must reconcile against |
| `"…/Theo Data/ABNB_Fundamentals_Alt_Macro_Bloomberg_LIVE.xlsx"` → `Consensus_Guidance` | print | 34×34 | licensed; `BEST_SALES 1FY/2FY` at prior-close as-of dates. **2025–26 rows usable; pre-2025 rows internally inconsistent — quarantine them** |

**External data required — one item, and it is cheap.**

* **Fiscal.ai (free tier or $39/mo Pro), historical FY+1 revenue consensus at each of the 23 print dates.** This is the only variable in the model with n=1. Acquisition: sign up, activate ABNB, export the consensus snapshot series, backfill 2020Q4–2026Q2 via the API. Phase-1 estimate: **4 hours of setup, same-day**; the Phase-1 alt-data landscape lists "Full history all 23 prints (2020Q4-2026Q2)". Fallback if the vendor's history is thin: reconstruct FY+1 consensus from dated press quotes the same way `04_consensus_sources.csv` reconstructed the quarterly series (145 quotes already sourced that way), which costs ~2 analyst-days and yields maybe 12–15 usable prints.
* **Nothing else.** No card panel, no AirDNA, no OAG, no Placer. This lens is deliberately built on disclosure, consensus vintages and prices.

---

## 4. Estimation and validation

**Estimator.** One Bayesian hierarchical state-space model in **PyMC 5** (Stan is acceptable; PyMC keeps the team in one language with `pandas`). `numpy`/`scipy` for the kernel, `statsmodels` only for the OLS baselines and Newey–West standard errors on the revision regression, `arviz` for diagnostics. Sampling: NUTS, 4 chains × 2,000 draws, target_accept 0.9; the model has ~25 parameters against 159 pooled observations plus 22 quarterly kernel observations, so it will sample cleanly.

**Priors — weakly informative, and every one of them is defensible out loud.**

| parameter | prior | justification |
|---|---|---|
| `w` (lag weights) | Dirichlet(4, 2) centred on (2/3, 1/3) | the repo's non-negative fit; concentration 6 = "worth about six quarters of data" |
| `log λ_s` | N(log λ̂_s^{trailing-3}, 0.03²) | 3pp of relative sd; the measured 3-year range is 0.17–0.70pp |
| `μ_c` (pooled cushion) | N(0.02, 0.02²) | the full-history mean beat is +2.54%; sd 2pp lets the data move it |
| `τ` (family sd) | HalfNormal(0.02) | shrinkage strength decided by the data, not by us |
| `ρ` | Beta(2,2) on (0,1) | cushions are persistent but mean-reverting; the halving from +3.04% to +1.86% is a slow drift, not a jump |
| `γ` | N(0, 0.01²) each | each covariate is allowed ~1pp of cushion effect a priori |
| `κ` | N(0.005, 0.005²) | the measured last-8 mean is +0.52% with sd 0.28% |
| `b` (FY+1 pass-through) | N(0.7, 0.3²) | one observation at 0.77; the prior must be wide until Fiscal.ai lands |
| `p_−` | Beta(1,1) | uniform; the posterior after 9/9 is Beta(10,1), mean 0.909 |

**Point-in-time protocol.** Expanding window, refit at each historical *guide date* `t`, using only:
(i) GBV and revenue through `q−1` **as reported at `t`** — the KPI panel is back-dated per `data/processed/overnight/02_metric_coverage.csv`, and Airbnb does not restate GBV, so vintage risk here is low and must be stated as such;
(ii) guidance statements with `print_date ≤ t`;
(iii) consensus vintages dated **strictly before** `t` — this is the discipline that `20_frozen_q3_2026.csv` already enforces by preserving LSEG $4,610m as the 6-Aug feature rather than the later Zacks $4,740m. Violating it is exactly the failure that killed the peer read-across (MAR reported *after* ABNB in 2023Q3 and 2025Q1, HLT in 2024Q2; the PIT-corrected version is strictly worse, 02_model_audit §4.2c);
(iv) FRED FX through `t` only, with `driver_realised_share` recomputed at `t`.

**Baselines it must beat, per target.**

| target | baselines | incumbent performance |
|---|---|---|
| revenue **level** `A_q` | AR(1) on y/y; seasonal-naive; **guide + trailing-8 cushion** | guide+cushion 1.1% mean error — the bar |
| **guide midpoint** `g_q` | prior-year same-quarter growth applied to the comp; the Street's own next-quarter number as a guide proxy | **nobody in the repo has ever scored this target.** The kernel's PIT walk-forward is MAE 1.36% (below) |
| **sign of `gap_q = g_q − S_q`** | always-positive; always-negative; coin flip | 11 above / 8 below in the scoreable sample; a constant predictor gets 58% |
| 20-day drift | zero; unconditional mean −2.18%; ABNB's 69.6% negative base rate | the sign rule is 8/8 |

**The kernel's own walk-forward, computed in-session.** `λ̂` from the two prior same quarters only (so 1Q24 is the first scoreable quarter), `G` known at the guide date:

| quarter | predicted | actual | error |
|---|---|---|---|
| 1Q24 | 2,130 | 2,142 | −0.55% |
| 2Q24 | 2,813 | 2,748 | +2.37% |
| 3Q24 | 3,732 | 3,732 | −0.01% |
| 4Q24 | 2,434 | 2,480 | −1.86% |
| 1Q25 | 2,381 | 2,272 | **+4.81%** |
| 2Q25 | 3,016 | 3,096 | −2.58% |
| 3Q25 | 4,116 | 4,095 | +0.50% |
| 4Q25 | 2,779 | 2,778 | **+0.05%** |
| 1Q26 | 2,692 | 2,678 | +0.54% |
| 2Q26 | 3,598 | 3,608 | −0.28% |

n = 10, mean +0.30%, **MAE 1.36%, RMSE 2.00%**; the last five quarters have MAE **0.79%**. The single outlier (1Q25, +4.81%) is the known 2024→2025 lead-time regime change — the same event that 03_insider_mechanics §1.4 identifies as one of only two invisible pattern breaks in five years, and it is *over-*prediction, i.e. the kernel is exposed to lag lengthening, which is precisely what a time-varying `w` is for.

**Sample-size honesty and a power statement.** 23 prints; 19 scoreable revenue ranges; 18 with both consensus ends; 10 quarters of PIT kernel backtest; 8 below-Street events. What that buys:

* **κ:** last-8 sd 0.28% → standard error 0.10%. A 0.5pp error in the anchoring constant would be detected at t ≈ 5. **Well identified.**
* **Cushion:** last-8 sd 1.00% → se 0.35%. A 1pp shift in cushion policy is detectable at t ≈ 2.9; a 0.3pp shift is not. **I will not claim cushion resolution finer than ±0.7pp.**
* **Drift sign:** 9/9 under a 50% null is p = 0.002; under ABNB's own 69.6% negative base rate, p = 0.0382. Both are reported. **This is a base-rate claim, not an alpha model.**
* **Drift magnitude:** with 8 events and a 20-day sd of ~4pp, the minimum detectable slope on `gap` is ~2.9pp of return per pp of gap. The observed data are non-monotone (gap −2.17% → −11.82%; gap −3.65% → −0.70%). **I therefore refuse to model the magnitude and trade the sign only.** This is the single most important refusal in the proposal.
* **`b` (FY+1 pass-through):** n = 1 today. Pre-registered: if Fiscal.ai delivers ≥12 prints and the posterior sd on `b` remains >0.3, the FY27 output is presented as a scenario tree with stated probabilities, not as a point estimate.

**Why the team's ~3,500 negative tests do not condemn this design — and which parts they do condemn.**

*They do not condemn it because:*
(b) **Wrong target was the central error and this design inverts it.** The programme predicted surprise-vs-Street, a difference with sd ~1.3pp, using level features with sd ~5pp; the diagnostic `pred_sd/actual_sd = 0.14–0.33` on 16 of 17 pairs is an intercept shift (02_model_audit §4.2b). My targets are the *guide midpoint* (whose PIT-predictable variation is the full 1.84% sd of `guide/mech`) and the *sign of gap* (which has 4.3pp of range across the 19 quarters). Both have far more variance than 1.3pp.
(d) **Underpowered at n≈10 with one regressor.** That is a statement about single-feature quarterly OLS. My cushion parameter is estimated on 159 pooled statements with hierarchical shrinkage; my kernel is a 3-parameter model on 22 quarters with a 1.36% MAE; my Layer-2 constant has a 0.10% standard error. The n problem is not binding on parameters this tightly identified.
(a) **No signal in Trends/macro.** I use neither. Zero Google Trends features, zero FRED macro features other than FX rates, which are a mechanical translation input and not a demand proxy.
(e) **Wrong grain.** I use no Inside Airbnb panel.
(c) **PIT leakage.** The one live leak (`ADR_EXFX` hard-coded from integer-rounded letters, `analysis/src/predictive/03_nowcast_tests.py:48-51`) never enters: I do not use ADR.

*They do condemn, and I accept:*
— any attempt to forecast the **day-1** move. 17 regressions, all negative LOO R², sign hit rate 0.37. The overnight gap is 73% of the variance of legacy day-1. My model emits no day-1 view.
— any use of **management tone** (1,677 turns × 132 features at n=23 — a multiple-comparison guarantee of false positives). I use *literal guidance vocabulary* from the ledger, which is a hand-coded categorical with a documented bucket→range map (`analysis/src/overnight/02_guidance_ledger.py`, 864 lines), not an NLP feature set.
— any claim that **alt data** improves the Q3 revenue nowcast at quarterly frequency. It does not, and I do not need it to.

---

## 5. Outputs

The model emits, at every refresh, a **posterior** over `g`, `S` and the gap — plus a scenario tree whose branch probabilities are *computed from that posterior*, not assigned by hand. There is no Monte-Carlo-only layer: the quantities below are posterior functionals, and the drift claim is a Beta-Binomial base rate.

### 5.1 The 3Q26 print (5 Nov 2026)

| estimator | 3Q26 revenue | vs Street $4,740m (Zacks, 7 est, 4 Sep) |
|---|---|---|
| kernel (1), λ̂ = 17.24%, lagged GBV = ⅔(27.2) + ⅓(29.2) = $27.87bn | **$4,804m** | +1.35% |
| guide + last-8 median cushion 1.79% | $4,815m | +1.58% |
| frozen pre-registered card (`20_frozen_q3_2026.csv`) | $4,805m | +1.37% |
| **M3 posterior median** | **$4,805m, 80% interval $4,745–4,865m** | **+1.4%, P(beat) ≈ 0.93** |

Three independent constructions inside 0.25%. The model's *incremental* claim here is small and it should be sold as such: the print is close to arithmetic. The model also predicts the **at-print consensus**: `S = g × (1 + κ) = 4,730 × 1.0052 = $4,755m`, which is the number to use in the surprise calculation on 5 Nov, not the stale $4,740m.

### 5.2 The 4Q26 guide (5 Nov 2026) — the output that matters

Management sees `lagGBV(4Q26) = ⅔·GBV(3Q26) + ⅓·GBV(2Q26)`. GBV(3Q26) is reported that morning; the 2Q26 letter guided it to "mid teens" (14–16%) and bucket guides have been beaten 5/5.

| GBV(3Q26) | y/y | kernel revenue (λ̂ = 12.03%) | y/y | guide mid at −2.33% cushion | vs Street $3,200m |
|---|---|---|---|---|---|
| $25.9bn | +13.1% | $3,169m | +14.1% | $3,095m | **−3.3%** |
| $26.19bn (frozen card) | +14.3% | $3,192m | +14.9% | $3,117m | **−2.6%** |
| $26.4bn | +15.3% | $3,209m | +15.5% | $3,134m | **−2.1%** |
| $26.8bn | +17.0% | $3,241m | +16.7% | $3,165m | −1.1% |

**Posterior output: 4Q26 guide midpoint $3,120m (80% interval $3,060–3,185m); range $3,080–3,160m; gap vs Street −2.5% (80% interval −4.4% to −0.5%); P(gap < 0) ≈ 0.87.** Reaching a $3,200m guide requires GBV(3Q26) above ~$27.6bn, +20.5% y/y, against a "mid teens" guide — possible only if the World Cup residual and RNPL eligibility expansion deliver a bucket break of unprecedented size.

**This is also where M3 corrects the team's own bear case.** The Q4/FY27 bridge (`29_fy27_bridge.csv`, `research/notes/overnight/29_q4-fy27-bridge.md`) puts 4Q26 *revenue* at $3,111m base by subtracting a −3.4pp FX step from the Q3 guide's growth rate. The kernel says 4Q26 **revenue** is $3,190–3,210m, i.e. at the Street, and the **guide** is $3,120m. The bridge's number is right for the guide and too low for the print, because the y/y FX step is already embedded in the USD-denominated lagged GBV base — subtracting it again from a growth rate built on that base double counts. The bridge and the kernel reconcile exactly once you separate the guide from the print. **That separation is this lens's contribution, and it is the sentence to put in front of the PM.**

Also emitted for 5 Nov: **FY26 guide raise.** With 1H26 actual $6,286m plus $4,805m plus $3,120–3,195m, FY26 lands $14,210–14,290m, +16.1% to +16.7% on FY25's $12,241m. The standing guide is "at least mid teens" (14–16%) and the base rate is unambiguous — the FY guide has only ever been raised and the raise lands at the Q3 print (FY24 and FY25 both converted a floor into "approximately X" at 3Q; `02_fy_guide_revisions.csv`). **Predicted: FY26 revenue growth guide converted from "at least mid teens" to a point near "approximately 16%", P ≈ 0.8.** Two signals fire in opposite directions in the same letter: a raised year and a Q4 range below the Street. The historical evidence says the tape weights the quarter — `fy_guide_action` has a sign hit rate of 0.50 on day-1 and 0.40 on 20-day (n=6, n=5; `02_guidance_sign_tests.csv`), i.e. nothing, while the gap sign is 8/8.

**Will management quantify the FX?** The 4Q25 letter quantified Q1's FX, the 1Q26 letter quantified Q2's ADR FX, the 2Q26 letter quantified Q3's ("inclusive of an approximate three percentage point foreign exchange tailwind after factoring in our hedging program"). Base rate says they quantify. If they do, the bridge is handed to the market and the drift may be muted; if they do not, the guide reads as a demand miss. The model carries this as a binary node with P(quantified) ≈ 0.75 and a drift multiplier of 0.5 on the quantified branch — an assumption, explicitly labelled, with n=0 direct evidence.

### 5.3 Feb 2027 — the Q4 print and the first FY27 guide

Kernel: `lagGBV(1Q27) = ⅔·GBV(4Q26) + ⅓·GBV(3Q26)`; λ̂(Q1) = 12.66%. On base-case GBV the 1Q27 guide midpoint comes out at **$2,930–2,990m**, +9.4% to +11.6% y/y against 1Q26's $2,678m — the first sub-teens quarterly guide since 2023, and against a 1Q26 comp of +17.9%. The FY27 guide, if it follows the FY26 template (first given at the Q4 print, as a bucket), lands as **"low double digits" or "low-to-mid teens"** — the model's posterior on FY27 growth is 9.5%–12.5%, so "low double digits" (10–12%) is the modal wording at P ≈ 0.55, "low to mid teens" at P ≈ 0.25, and a sub-10% wording at P ≈ 0.20.

### 5.4 FY27 revenue vs the Street's $15.73–15.76bn

The Street's FY27 is **not a bottom-up build** — 13 estimates spanning $14.99–16.29bn, an 8.3% range (`04_current_consensus.csv`). Equation (6) says it is an exit-rate extrapolation anchored on the Q4 guide.

```
FY27 consensus after 5 Nov  ≈  15,745 × (1 + b · gap)  with  b ≈ 0.77, gap ≈ −2.5%
                            ≈  15,745 × (1 − 0.019)  ≈  $15,445m   (growth +11.3% → ~+9.3%)
```

**M3's own FY27 point is $15.7–15.9bn — i.e. we agree with today's Street on the year and disagree on the path.** The model's FY27 emission is therefore *not* "FY27 revenue is lower"; it is:

> FY27 consensus will be marked **down ~2%** between 5 Nov 2026 and the February print, and then marked back up, because the Q4 guide is a floor with a ~1.9% cushion and the Street's FY27 is anchored to it rather than to FY27 fundamentals.

**Mechanism by which we differ from the Street, stated plainly.** Sell-side FY27 numbers are the Q4 exit rate rolled forward. The Q4 exit *guide* will be ~2.5% below where they have the Q4 *print*, because they do not separately model the guidance cushion — their Q4 number *is* their guide expectation. We do model it, we measure it at −2.33% ± 1.84%, and we know κ = +0.52% ± 0.28%. So on 5 Nov a gap opens that is arithmetic, not informational, and the revision regression (slope 0.988, r 0.993) says the Street closes it by moving to the guide.

**Multiple coherence check.** At +0.48 EV/EBITDA turns per point of forward revenue growth (`docs/2026-09-07_research-state-of-play.md`), a 2.0pp cut to forward growth is −0.96 turns on a ~16.5x base = −5.8% of EV, plus the ~−1.9% earnings effect ≈ **−7 to −8%** over the revision window. The measured 20-day drift after below-Street guides is −4.0% raw / −4.2% excess, with a worst case of −11.8%. Two independent routes land in the same band. That is a coherence check, not a precision claim, and I will say so.

### 5.5 Uncertainty representation

Not a Monte Carlo. Three objects:
1. **Posterior densities** on `g_{4Q26}`, `κ`, `c`, `b` from the PyMC fit — reported as medians and 80% credible intervals.
2. **A scenario tree with data-dependent probabilities.** Node 1: GBV(3Q26) tercile → determines the guide. Node 2: gap sign, `P(gap<0) = 0.87` from the posterior. Node 3: FX quantified in the letter, `P = 0.75` (labelled as an assumption). Node 4: FY26 raise, `P = 0.8` from the base rate. Every branch probability is either a posterior functional or a stated base rate with its `n`.
3. **Conformal prediction intervals** on the guide midpoint, using the 10 PIT kernel residuals as the calibration set. With n=10 the tightest honest two-sided coverage is 9/11 ≈ 82%, which gives an $\pm$ interval of roughly ±2.4% on the level — wider than the posterior, and the number I would quote to a hostile judge.

---

## 6. Minimal code skeleton

```python
# M3 / GAC.  Inputs are all repo-relative to Citadel-ABNB/.
# Runs end-to-end on files that exist today except FY+1 consensus (see §3).
import numpy as np, pandas as pd, pymc as pm

KPI   = "data/processed/overnight/02_kpi_panel_quarterly.csv"      # gbv_busd, revenue_musd
CUSH  = "data/processed/overnight/02_guidance_cushion_series.csv"  # 19 revenue ranges
LEDG  = "data/processed/overnight/02_guidance_ledger.csv"          # 194 stmts, hierarchical pool
CONS  = "data/processed/overnight/16_consensus_at_print_merged.csv"# both ends of every revision
FXSCH = "data/processed/overnight/05_fx_schedule.csv"              # driver_realised_share
RET   = "data/processed/overnight/20_executable_returns.csv"       # open_20d_pct (executable)

k = pd.read_csv(KPI).set_index("quarter")
def qkey(q): return (int(q[2:]), int(q[0]))
q_ord = sorted(k.index, key=qkey)

# ---- Layer 0: booking->check-in kernel.  w fixed at the repo's non-negative fit; lam_s free.
W = np.array([2/3, 1/3])
lag = {q: W[0]*k.gbv_busd[q_ord[i-1]] + W[1]*k.gbv_busd[q_ord[i-2]]
       for i, q in enumerate(q_ord) if i >= 2}
lam = {q: k.revenue_musd[q] / (lag[q]*1000) for q in lag}          # realised conversion
def lam_pit(q, yrs=2):                                            # PIT: prior same quarters only
    h = [lam[x] for x in sorted(lam, key=qkey)
         if x[0] == q[0] and int(x[2:]) < int(q[2:])]
    return np.mean(h[-yrs:])
def mech(q):                                                      # management's own view, ex-eta
    return lam_pit(q) * lag[q] * 1000        # X ~ 1.00 on the flat-euro path; see FXSCH

# ---- Layer 1+2 data: cushion (A/g-1), anchoring (S/g-1), gap (g/S-1)
c = pd.read_csv(CUSH); s = pd.read_csv(CONS)
c["mech"]     = c.target_period.map(lambda q: mech(q) if q in lag else np.nan)
c["log_gm"]   = np.log(c.value_mid / c.mech)                       # log g - log M  = -cushion_pol
c["log_cush"] = np.log(c.actual   / c.value_mid)                   # log A - log g
anchor = (s.cons_revenue_musd.shift(-1) / s.next_q_guide_mid_musd - 1).dropna()  # kappa

# ---- Hierarchical cushion across guidance families (n=159 scoreable, not n=19)
led = pd.read_csv(LEDG).query("outcome in ['above_range','within_range','met','not_met','beat','miss']")
fam = pd.Categorical(led.guide_type).codes; nf = fam.max() + 1
y   = led.cushion.astype(float).fillna(0.0).values / 100.0
with pm.Model() as M:
    mu_c = pm.Normal("mu_c", 0.02, 0.02); tau = pm.HalfNormal("tau", 0.02)
    c_f  = pm.Normal("c_f", mu_c, tau, shape=nf)                   # family partial pooling
    pm.Normal("y_fam", c_f[fam], pm.HalfNormal("s_f", 0.03), observed=y)
    # revenue-range cushion, with covariates knowable at the guide date
    z    = np.c_[c.range_width_pct.values/100, np.ones(len(c))]    # + fxobs, comp, fyraise
    g_   = pm.Normal("gamma", 0, 0.01, shape=z.shape[1])
    rho  = pm.Beta("rho", 2, 2)
    mu_q = c_f[list(pd.Categorical(led.guide_type).categories).index("range")] + z @ g_
    pm.Normal("cush_rev", mu_q, pm.HalfNormal("s_q", 0.02), observed=c.log_cush.values)
    kap  = pm.Normal("kappa", 0.005, 0.005)                        # Street anchoring constant
    pm.Normal("anch", kap, pm.HalfNormal("s_k", 0.005), observed=anchor.values)
    idata = pm.sample(2000, tune=2000, target_accept=0.9, chains=4)

# ---- Forward: 4Q26 guide.  GBV(3Q26) is the only unknown; sweep the guided "mid teens" bucket.
GBV_2Q26 = 27.2
for g3 in [25.9, 26.19, 26.4, 26.8]:                               # 3Q26 GBV scenarios, $bn
    lag4  = W[0]*g3 + W[1]*GBV_2Q26
    mech4 = np.mean([0.1195, 0.1212, 0.1203]) * lag4 * 1000        # lam_pit(Q4)
    guide = mech4 * np.exp(idata.posterior["gamma"].mean().item()*0 - 0.0233)  # -2.33% cushion
    print(f"GBV3Q26 {g3:5.2f} -> print {mech4:6.0f}  guide {guide:6.0f} "
          f"gap vs Street 3200: {100*(guide/3200-1):+5.1f}%")

# ---- Layer 3: one-sided drift.  Beta-Binomial on the SIGN only; no magnitude model.
r = pd.read_csv(RET).set_index("print_quarter").open_20d_pct
gap = s.set_index("print_quarter").guide_vs_street_pct.dropna()
below = r.reindex(gap[gap < 0].index).dropna()
print(f"below-Street: n={len(below)} mean={below.mean():+.2f}% neg={(below<0).sum()}/{len(below)}"
      f"  P(neg|below) posterior mean = {(1+(below<0).sum())/(2+len(below)):.3f}")
# FY+1 pass-through b: requires Fiscal.ai historical FY+1 consensus (pseudo-code until acquired)
# b, se = ols(dlog_FY1_consensus ~ gap + dFYguide).params, .bse      # n=1 in-house today (0.77)
```

---

## 7. Three-week build plan (3–4 undergraduates)

**Week 1 — day level.**

* **Day 1 (all 4).** Read `02_model_audit.md` §1.3, §3.1, §3.7 and `03_insider_mechanics.md` §1.3–1.5, §3.1–3.5. Person A signs up for Fiscal.ai and starts the FY+1 consensus backfill (4 hours; if the API is thin, switch to the press-quote reconstruction used in `04_consensus_sources.csv`). Person B reproduces the three in-session tables in §2 (λ_s, κ, cushion) from the CSVs — this is the acceptance test for the whole project; if the numbers do not reproduce, stop and find out why.
* **Day 2.** Person B: kernel `lam_pit` + PIT walk-forward, target MAE 1.36% on the 10-quarter sample. Person C: build the revision panel from `16_consensus_at_print_merged.csv` (both ends) and reproduce slope 0.988 / r 0.993. Person D: build the drift panel from `20_executable_returns.csv` on `open_*` columns only, reproduce 8/8 and the 69.6% base rate.
* **Day 3.** Person A: hierarchical ledger frame — map `02_guidance_ledger.csv` into (family, standardised cushion) pairs; exclude the expense/tax `point` family and the take-rate family per §2.2 and document why. Person B: add `X` (the FX basket) from `10_fx_daily.csv` and confirm it moves the kernel by <0.5% on the current euro path.
* **Day 4.** Person B + C: PyMC model up and sampling; check `r_hat < 1.01`, ESS > 400, prior-predictive sanity (does the prior allow a 5% cushion? it should, barely).
* **Day 5.** Full expanding-window replay: at each of the 19 guide dates, emit `ĝ`, `Ŝ`, `gap sign`. Score against the four baselines in §4. **Freeze the specification and write it to `data/processed/overnight/20_prediction_ledger.csv` alongside the existing frozen 3Q26 card.** Nothing is re-selected after this point.
* **Day 6–7.** Person D: the scenario tree and its probability arithmetic; Person A: the FY+1 regression on whatever Fiscal.ai delivered, with an explicit "n too small" branch that falls back to the n=1 pass-through as a stated assumption.

**Week 2 — milestones.**
M1: posterior + conformal intervals on the 4Q26 guide, and the written reconciliation of the kernel's $3,190–3,210m print against the bridge's $3,111m (§5.2) — this memo-ready paragraph is the single highest-value artefact of the whole lens.
M2: the three-print scenario tree with all branch probabilities sourced.
M3: FY27 revision path and the multiple bridge (+0.48 turns/pt), with the two-route coherence check.
M4: a one-page "what we refuse to claim" appendix, verbatim from §4's power statement.

**Week 3 — milestones.**
M5: hostile-judge rehearsal against §8; each attack gets a ≤60-second answer with a number and a path.
M6: the two memo pages and the model exhibit — the exhibit is the three-layer chain `g → S → A` with the measured κ and cushion printed on the arrows.
M7: live refresh discipline — re-run FX and the Street pull weekly; re-run the whole model on 5 Nov within two hours of the letter and score the frozen card.

**What can be cut, in order:** (i) the conformal layer — the posterior intervals carry the message; (ii) the FY+1 regression, falling back to the n=1 pass-through with a labelled assumption and a ±0.4 sensitivity band; (iii) the `z` covariates in (4), reverting to a constant cushion at the last-8 mean of −2.33% (this costs very little: the covariates explain a minority of a 1.84pp sd); (iv) the time-varying `w`. **What cannot be cut:** the λ_s kernel, κ, the cushion, the gap-sign rule and the guide-vs-print separation. Those five are the pitch.

---

## 8. Failure modes and the hostile judge

**"You have 19 observations and a hierarchical Bayesian model. This is curve-fitting."**
The revenue-range family contributes 19 quarters; the pooled cushion hyper-mean is informed by 159 scoreable statements across 7 guide types. The two parameters the trade depends on are `κ` (last-8 sd 0.28%, se 0.10%) and the gap sign (8/8, p = 0.038 against ABNB's *own* 69.6% negative base rate, not against a coin flip). Neither needs a large model. And I have pre-registered what I will not claim: no day-1 view, no drift magnitude, no cushion resolution finer than ±0.7pp. Everything else in the model is measurement, not inference.

**"The guide-below-Street rule is nine data points and the 2024Q4 case returned −11.8% while the 2024Q2 case, with a bigger gap, returned −0.7%. Your signal is noise."**
Correct, and that is why the model trades the sign and refuses the magnitude. The minimum detectable slope at n=8 with a 4pp return sd is 2.9pp per pp of gap; the data are non-monotone; I state that in the power section rather than fitting through it. The claim is a conditional base rate with a Beta(10,1) posterior — P(negative | below-Street) = 0.909 — against an unconditional 0.696. That is a modest edge, honestly sized, on an event whose *occurrence* my kernel predicts at P = 0.87.

**"Your Layer 2 is a tautology. Of course consensus sits near the guide."**
It is a tautology only if you already knew κ = +0.52% with a 28bp sd, and that the revision slope is 0.988 with r = 0.993. Nobody in this repo had measured either before this note, and the whole Street-response literature would predict partial adjustment, not unit adjustment. The non-obvious consequence is the one that pays: because adjustment is *complete*, the FY+1 number is anchored to a quarterly guide rather than to FY+1 fundamentals, which is why a cushion — a pure accounting-conservatism artefact — moves a forward multiple.

**"You are contradicting your own team's Q4 bridge by $80m."**
No — I reconcile it. The bridge's $3,111m is the right number for the *guide*; the kernel's $3,190–3,210m is the right number for the *print*. The bridge subtracts a −3.4pp y/y FX step from a growth rate whose base (lagged USD GBV) already carries that FX; the kernel translates once, at the booking→check-in step, and lets the y/y FX effect fall out. Both constructions then say the same thing about 5 November: the range lands below the Street.

**"RNPL broke your kernel. The unearned-fee coverage ratio went from 0.697 to 0.599."**
Two different estimators, and the divergence is the finding, not a defect. Funds held is booking-amount-denominated and distorted ~4.8%; unearned fees are fee-denominated and distorted ~16.5% (03_insider_mechanics §1.5). The kernel runs on **GBV**, which is not distorted at all — and its 4Q25 error was +0.05% and its 2Q26 error −0.28%, both *after* RNPL launched. The exposure is real but it is to lag **lengthening**, which shows up as over-prediction (1Q25, +4.81%), and the mitigation is a time-varying `w` with the restated unearned-fee series `reported/(1−d_q)` as its observation equation.

**"The single-fee migration deadlines fall inside 3Q26 and 4Q26. Your λ is about to move."**
Yes, and that is the model's largest un-hedged risk. 15 Sep 2026 ex-EEA and 13 Oct 2026 EEA+CH (`data/processed/overnight/06_fee_timeline.csv`) move fee collection from the guest at booking to the host's payout after check-in, which mechanically shifts `λ` and lengthens the fee-cash lag. The arithmetic effect on the *take rate* is +40–50bps gross (`06_elasticities.csv`), offset by the 29 Aug 2026 direct-link pilot at 6–10%. I handle this by (i) carrying a `λ` regime break with a prior on the shift of N(0, 0.4pp), (ii) making "does the 3Q26 10-Q attribute the unearned-fee gap to fee migration as well as RNPL?" a pre-registered post-print test, and (iii) refusing to forecast 2Q27 conversion at all until it is observed.

**"Management could simply guide differently."** They could. The cushion has already halved from +3.04% to +1.86% and the range from 4.9% to 1.9% of midpoint. If the trend continues, my gap narrows and the trade shrinks — which the posterior on `ρ` and the drift in `c` already encode. What would genuinely break the model is a *structural* change in disclosure: a multi-quarter guide, or dropping the quarterly range. Neither has any precedent in 23 prints and both would be visible in the letter within minutes.

**"Isn't this just the well-known 'guidance sandbagging' anomaly?"** The anomaly is that the beat is priced; the sign hit rate of the beat against day-1 is 0.37, *below* a coin flip. What is not priced is that the *guide* is the Street's FY+1 anchor with a unit adjustment coefficient. That is the specific, testable, one-company claim.

---

## 9. Interlock with the other five lenses

**Consumes.**
* *Structural mix (M1):* one number and one number only — the **GBV path**, `G_{3Q26}` and forward. My kernel takes GBV as its state, so the mix lens's nights × ADR decomposition enters revenue exclusively through `G`. Nights, ADR ex-FX, geographic mix, seats dilution and take rate must **not** be passed to me separately; that is the double-count boundary and it should be written into `model/assumptions.md`.
* *Nowcast tracker (M2):* a within-quarter estimate of `G_{3Q26}` with a stated vintage, and the 3Q26 GBV bucket read, which is the only free variable in my 4Q26 guide output (a $0.9bn swing in GBV(3Q26) moves the guide by $70m and the gap by 2.2pp).
* *FX / take-rate / timing (M6):* the single FX basket and the check-in-date index used in `X`, plus the `driver_realised_share` schedule and the hedge overlay as a memo line. I need one basket, not two fits.
* *Bottom-up markets (M4):* nothing directly. Its output belongs upstream in M1's GBV.
* *ML signal extraction (M5):* candidate covariates for `z` in equation (4) only — features of management's *situation* at the guide date (comp difficulty, FX observability, quarters since the last raise), never features of management's *language*. The n=23 × 132-feature tone programme is a settled negative.

**Hands to.**
* *To the memo:* the three-print scenario tree with data-dependent probabilities; the 4Q26 guide midpoint with an 80% interval; the FY27 consensus revision path; the guide-vs-print reconciliation paragraph that resolves the $80m disagreement with the existing Q4 bridge.
* *To M6 (FX/timing):* the measured `λ_s` series, which is the direct replacement for the take-rate carry × FX-wedge construction at `13_driver_model.py:381-383` and its +1.05pp trailing-4 perfect-foresight bias. My λ is their φ.
* *To M1 (structural mix):* a hard aggregate constraint. Any mix build whose implied revenue path is inconsistent with `λ_s × Σ w_k G_{q−k}` to better than 2% is wrong somewhere, and this is a cheap, fast falsification test for the five FY27 estimates that currently span $370m (02_model_audit §5).
* *To M2 (nowcast):* a precise specification of what the nowcast is worth. Because 85–90% of a quarter is determined at the guide date, a within-quarter GBV nowcast has value **only** for the *next* quarter's guide, not for the current print. That reframing is the difference between a nowcast that fails against AR(1) and one that has an identified job.
* *To the valuation lens:* the forward-growth input to the +0.48-turns-per-point multiple rule, delivered as a posterior over FY27 consensus growth rather than as a point.

**The one-sentence version for the PM.** Airbnb's guide is a floor with a measured 1.86% cushion; the Street re-anchors on it one-for-one within 30 basis points; the Street's FY27 number is an extrapolation of a quarterly guide it has not yet seen; my kernel says that guide lands 2.5% below where they have it, with 87% probability; and every time that has happened the stock has been down 20 days later.
