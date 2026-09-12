# M2 — The Ledger Filter: a point-in-time, mixed-frequency nowcast tracker for ABNB guidance

**Lens:** point-in-time mixed-frequency nowcast, engineered around the programme's negative results.
**Author:** M2 workstream, 11 Sep 2026. **Audience:** Citadel PM. **Horizon:** 3-12 months (guides of 5 Nov 2026 and ~Feb 2027).
**Conventions:** *measured* = computed from a disclosure or a dataset opened for this note; *assumed* = analyst input;
*unidentified* = not separable from public data. Every repo path below was opened (`head`/`wc`/`duckdb`) while writing.

---

## 1. Thesis in five lines

1. **What it forecasts.** Four pre-registered objects, in this order of tradability: (T1) the **Q4-26 revenue guide midpoint that management prints on ~5 Nov 2026, expressed as a % distance from the print-day Street number**; (T2) the 3Q26 **revenue and nights surprise** vs print-day consensus; (T3) the **FY26 guide raise**; (T4) the **FY27 consensus revision path** over the 60 sessions after 5 Nov, against today's $15.73-15.76bn.
2. **Why not the level.** The level is already solved: guide midpoint plus the trailing-8 cushion prices revenue to a 1.1% mean error over 19/19 beats (`research/notes/overnight/08_altdata-index-and-backtests.md`). Forecasting it better is worth nothing; the same note records it as *the worst* predictor of surprise. The stock trades on the guide, not the print — "guide below Street" produced 9/9 negative 20-day excess returns, mean −4.21%, on an executable next-open entry (`research/notes/overnight/09_stock-behaviour-and-alpha.md`, `data/processed/overnight/20_executable_returns.csv`).
3. **Why it should beat what the team has.** The driver model forecasts a *booking-dated* identity and then converts to revenue with a prior-year take-rate carry times an FX wedge — a construction whose perfect-foresight backtest still over-predicts revenue by +0.53% mean / +1.05pp trailing-4 with 100% of the error inside that one term (`docs/revenue-forecast-strategy/01_ground-truth/02_model_audit.md`). The Ledger Filter replaces the plug with the thing it is a proxy for: an estimated booking→check-in kernel, disciplined by four accounting observables (revenue, GBV, unearned fees, funds held) that are *over-identifying*.
4. **Where the edge is.** 85-90% of any quarter's revenue is already on the booking ledger when the guide is set (`docs/.../03_insider_mechanics.md` §1.4). So the guide is arithmetic plus a cushion. We can reconstruct the arithmetic — and the Street demonstrably does not: its 4Q26 range is $3,050-3,700m (10 estimates, Zacks 4 Sep) on a quarter that is 82% FX-determined and ~85% booking-determined.
5. **What is genuinely new.** A monthly state-space filter in which every alt-data series — reviews, Eurostat, arrivals, calendar pickup — is a **measurement of one latent state**, never an additive driver; disclosed regional bands enter as an **interval-censored likelihood**; and the 67.5m-row review store is corrected for **scrape-date censoring** and **listing survivorship** using a second listing vintage that the Phase-1 inventory says does not exist and that I verified does.

---

## 2. Formal specification

### 2.0 Notation

`m` = calendar month; `q` = quarter; `r ∈ {NA, EMEA, LatAm, APAC}`; `i` = Inside Airbnb market (120 current, 115 matched y/y); `ℓ` = months between booking and check-in; `D` = a decision date (guide date or print date).

### 2.1 Block A — the accounting core (the identification anchor)

Latent monthly **gross booked** quantities, before cancellations, translated at **booking-date** FX:

```
G_m   gross GBV booked in month m            (USD, booking-date FX)
N_m   gross nights-and-seats booked in m
```

Structural parameters:

```
φ_ℓ    share of month-m bookings checking in ℓ months later;  Σ_ℓ φ_ℓ = 1, φ_ℓ ≥ 0
κ_ℓ    share of month-m bookings cancelled ℓ months later (the cancellation hazard)
τ      economic take rate on fee-bearing GBV (LTM basis, slow-moving)
p_m    share of fees collected in CASH at booking (RNPL / fee-migration driven)
π_m    share of the booking AMOUNT collected in cash at booking (the funds-held analogue of p_m)
```

**Observation equations** (all four are printed or filed, so all four are likelihood terms):

```
(A1) GBV_q      = Σ_{m∈q} [ G_m − Σ_{b≤m} κ_{m−b} G_b ]                          (10-Q / letter, booking-dated, net of cancellations)
(A2) Nights_q   = Σ_{m∈q} [ N_m − Σ_{b≤m} κ^N_{m−b} N_b ]                         (letter)
(A3) Revenue_q  = τ · Σ_{m∈q} Σ_ℓ φ_ℓ · Ĝ_{m−ℓ} · (FX^chk_m / FX^bk_{m−ℓ}) + h_q  (income statement; Ĝ = surviving GBV; h_q = hedge reclass, filed)
(A4) UF_q       = UF_{q−1} + τ·p_q·G^gross_q − Revenue_q − τ·Refunds_q ± FXtr      (unearned fees, balance sheet)
(A5) FH_q       = FH_{q−1} + (1−τ)·π_q·G^gross_q − Payouts_q − GuestRefunds_q       (funds held for clients, balance sheet)
```

**How each term is identified.**

- **φ (the kernel).** Not free-estimated at n=23. Prior anchored on two measured objects: the non-negative fit of revenue on lagged GBV puts ~2/3 on `GBV(t−1)` and ~1/3 on `GBV(t−2)` (`research/airbnb_earnings_call_study.md` §8.4, n≈20); and the realised lagged-GBV conversion is astonishingly stable — **Q3: 0.17391 / 0.17145 / 0.17182 for 3Q23/3Q24/3Q25 and Q4: 0.11946 / 0.12117 / 0.12026** (verified in `data/processed/h2_bridge/h2_bridge_gbv_lag_conversion.csv`, 6 rows). A 0.25pp three-year range on a ~17% ratio is a *tight* likelihood. Prior: `φ ~ Dirichlet(60 · (0.66, 0.32, 0.02))`, giving a posterior sd on φ₁ of roughly 0.06 before data.
- **τ.** LTM take rate 13.26% at 2Q26 (`data/processed/overnight/02_kpi_panel_quarterly.csv`, col 82 `take_rate_pct`). Prior `τ ~ N(0.132, 0.003²)`, plus a *dated* mechanism shift from the fee migration (single 15.5% host fee: ~25% of listings at 1Q26, ~50% at 2Q26, deadlines 15 Sep 2026 ex-EEA and 13 Oct 2026 EEA+CH — `data/processed/overnight/06_fee_timeline.csv`) and the 29 Aug 2026 direct-link 6-10% pilot as a *negative* shift with an explicit scope prior.
- **p_m and π_m (the RNPL correction, done right).** The repo currently restates unearned fees with a hand-computed distortion `d_q` = 0.9 / 3.8 / 16.2 / 16.5% for 3Q25-2Q26 (`docs/.../03_insider_mechanics.md` §1.5). The filter does not take `d_q` as data; it **estimates `p_m` and `π_m` jointly** because (A4) and (A5) have *different denominators*: unearned fees are fee-denominated (~13-15% of GBV, $2,831m at 2Q26, −0.9% y/y against GBV +15.7%) while funds held is booking-amount-denominated (~87% of GBV, $12,224m, +10.5% y/y). Two observation equations, two unknown prepayment shares, one shared latent G → **identified**. The ratio `(1−π)/(1−p)` is the diagnostic that separates RNPL (hits both, proportionally) from the fee migration (hits fees only). That is the unidentified question §1.5 flags for the 3Q26 10-Q, converted into an estimable parameter with a posterior.
- **κ (cancellations).** Weakly identified; carried as an AR(1) around the disclosed platform rate step 16%→17% (4Q25 call). Sensitivity is pinned: 1m extra net lost nights = −0.75pp on Q3 growth, −0.82pp on Q4 (`research/notes/2026-09-10_rnpl-conversion-framework.md`).
- **FX.** Two objects only — a **booking-date** index and a **check-in-date** index from one basket, built from `data/processed/overnight/10_fx_daily.csv` (19,468 rows, DEXUSEU/DTWEXBGS and 8 crosses, last obs 2026-08-28) and `10_fx_quarterly.csv`. GBV and ADR translate at booking; revenue at the φ-convolution of booking. There is **no wedge**, so the FX-on-ADR term cannot cancel against a timing term — the defect at `analysis/src/overnight/13_driver_model.py:379` vs `:382` that makes the programme's best survivor (broad USD → ADR FX, walk-forward 0.44× naive) display-only. The hedge is an explicit overlay on a gross series (`data/processed/overnight/28_fx_hedge_disclosures.csv`, 15 rows).

### 2.2 Block B — the monthly indicator block (where the nowcast content lives)

Latent **check-out-dated** regional stay-completion factor `f^r_m`, which is by construction the argument of (A3):

```
(B0)  f^r_m ≡ log( Σ_ℓ φ_ℓ Ĝ^r_{m−ℓ} / ADR^r_m )   — completed stay-nights in region r, month m
```

**Indicator 1 — reviews (the core).** From `/Users/theomachado/abnb_scratch/release/airbnb_quant_panel_v3/review_events.parquet` (**67,500,188 rows, 120 markets**, verified in `coverage_summary.csv`), count reviews by market × review-month:

```
(B1)  log R_{i,m} = α_i + s_{i,mo(m)} + β_i · f^{r(i)}_m + log A(d_{i,m}) − log S_i(m) + ω_m + ε_{i,m}
```

where `s` = market-specific month-of-year effect, `A(·)` = the review-accrual (right-censoring) curve, `d_{i,m}` = days from the end of month m to market i's scrape date, `S_i(m)` = the survival probability that a listing alive in month m is still listed at scrape, and `ω_m` = the platform-wide drift in the review-per-stay rate.

*Why reviews are the right indicator and not just another alt-data series:* reviews are posted after **check-out**. They are therefore a measurement of the **revenue-recognition numerator**, not of booked nights. Every other indicator the team tested (Trends, Eurostat, macro) was aimed at the booking-dated printed KPI, which is the wrong side of the wedge. This is the single most important design choice in the proposal.

**Identification of A(·) — the cross-sectional experiment that already exists.** The 120-market current vintage was **not scraped on one day**: snapshot dates run 2026-06-05 (Los Angeles) through 2026-07-24 (Buenos Aires) — 50 days of spread, verified in `data/processed/booking_curves_by_market.csv` (`snapshot_date` column, 601 rows) and `analysis/src/inside_airbnb_review_velocity.py` (CITIES block). For a fixed calendar month (say May 2026), markets differ only in `d`. Regressing `log R_{i,May} − α_i − s_{i,May}` on `d_{i,May}` across 120 markets recovers `A(d)` **cross-sectionally, with no time-series degrees of freedom consumed**, and the exercise repeats for each of the last ~6 months → ~700 market-month cells to fit a 3-parameter accrual curve. The censoring is visible and large: the global monthly review count runs 1,805,017 (May 2026) → 1,104,754 (Jun) → 100,706 (Jul) → 3,100 (Aug) in `data/processed/abnb_party_size_reviews_v2_global_month.csv` (165 rows, 2013-01 to 2026-08). Anyone who reads the raw tail as "demand collapsed in July" has made the error this term exists to prevent.

**Identification of S(·) — the second vintage the inventory says does not exist.** `coverage_summary.csv` in the same release directory records `listing_snapshots, prior_2025, 115 markets, 1,458,929 rows` alongside `current_2026, 115 markets, 1,494,056 rows`, and the raw files sit in `/Users/theomachado/abnb_scratch/raw_expansion/v3_2026-09-06/inside_airbnb_yoy_2025/` (115-row manifest, 33 countries, dumps dated 2025-09-22 to 2025-11-12) with a further 40 in `inside_airbnb_listings_backfill/`. The 2025 schema carries `id`, `number_of_reviews`, `number_of_reviews_ltm`, `number_of_reviews_ly`, `last_review`, `estimated_occupancy_l365d` (79 columns, verified by `gzcat` on `spain/pv/euskadi/2025-09-29/listings.csv.gz`). Matching on `id` across vintages gives a market-level survival hazard directly. External cross-checks already in the repo: Common Crawl listing survival 86-88% since 2023 and six-city ex-Austin year-ago retention 75.5% → 73.4% (`data/processed/overnight/11_supply_economics.csv`). **Consequence:** without `1/S_i(m)`, a review series built from a current vintage understates history by roughly 12-14% per year of lookback, which mechanically *manufactures* ~12-14pp of spurious "growth". This is very likely a live contaminant in the existing `ia_reviews_ltm_matched_yoy` feature.

**Identification of β and ω — the constraint that stops the index free-floating.** `β_i` is not free. Impose, as hard equality constraints in the filter:

```
(B2)  Σ_r w_{r,q} · n̂_{r,q} = Nights_q                                   (exact, every quarter)
(B3)  annual Σ_m n̂_{r,m} = the 10-K regional nights (2025: NA 158m, EMEA 215m, LatAm 90m, APAC 70m)
(B4)  β_i ~ N(β_r, σ_β²),  β_r ~ N(1, 0.25²),  σ_β ~ HalfNormal(0.3)     (hierarchical shrinkage)
```

(B3) is what pins `ω` (the review-per-stay drift). Inside Airbnb's own working assumption is ~50% of stays leave a review (documented in `analysis/src/count_reviews_duckdb.py` docstring); the *level* of 50% is irrelevant because it is absorbed into `α_i`. Only the **drift** matters, and (B3) forces the drift to be whatever reconciles regional review growth to disclosed regional nights annually.

**Indicator 2 — Eurostat, re-scoped as a lagged state observation.** EU27 platform nights monthly, 2018-Mar 2026, in `data/processed/overnight/10_eurostat_platform_monthly_latest.csv` (40 rows monthly, 71 country columns). The repo killed it as a *leading* feature because it publishes ~150 days late. But at lag 0 it is extraordinarily informative about EMEA: `eu_platform_yoy_lag0 → emea_nights_band` has r = 0.961 and a walk-forward RMSE ratio of **0.476× AR(1)** (n=9, wf_n=5, `data/processed/overnight/08_eurostat_tests.csv`). In a filter, a late-arriving high-precision observation of `f^EMEA_{m−5}` sharpens the *current* state through the persistence of the state — you do not need it to be contemporaneous to be useful. That is the standard ragged-edge argument and it is exactly what a single-feature regression cannot exploit.

**Indicator 3 — national arrivals for the expansion regions.** JNTO (Japan), INE (Spain), ISTAT (Italy), INE (Portugal), Embratur (Brazil), ABS (Australia) — all free, monthly, 20-30 day lag (`docs/.../05_altdata_landscape.md`). Enter as region-specific observations of `f^APAC` / `f^EMEA` / `f^LatAm` with their own loadings and noise. Repo already has two: `10_bench_japan_arrivals_monthly.csv`, `10_bench_canada_travel_monthly.csv`.

**Indicator 4 — calendar pickup (the only genuinely forward object).** For identical (listing, stay-date) cells present in two consecutive scrapes `t₀ < t₁`:

```
(B5)  P_i(t₀→t₁ ; stay-month M) = Σ_cells [ blocked_{t₁} − blocked_{t₀} ]  /  Σ_cells 1
```

This needs **no y/y and no price** — which matters, because the 2026 calendars carry a 5-column schema with **no price** (`docs/.../01_data_inventory.md`). It measures net new blocking on fixed inventory for a fixed stay month, i.e. gross bookings minus cancellations at a monthly frequency, ~4-10 weeks before those stays are recognised. Two disciplines: (a) **`blocked_rate` is not occupancy** and must never be called that (`data/processed/booking_curves_by_market.csv` carries this warning); (b) host blocks contaminate the level but are near-constant within a listing over a 30-day window, so the within-cell first difference removes most of them. Today the repo has a single vintage (`booking_curve_daily.csv`, 44,380 rows; `booking_curves_by_market.csv`, 601 rows, 120 markets) — **the second capture must start immediately** (see §7, Day 1).

### 2.3 Block C — the target equations

```
(C1)  Base_D   = τ̂ · Σ_ℓ φ̂_ℓ Ĝ_{D−ℓ} · FX ratio            — revenue already determined at guide date D
(C2)  guide_mid_{q+1} = Base_D · (1 + ĝ_new) · (1 − c_D)     — c_D = the cushion management leaves
(C3)  T1 = 100 · (guide_mid_{q+1} / Street_{q+1} − 1)
(C4)  T2 = 100 · (Revenue_q / Street_q − 1) and the nights analogue
```

`c_D ~ Student-t(ν=5, μ_c, σ_c)`, `μ_c ~ N(1.79%, 0.5²)` from the trailing-8 median (`data/processed/overnight/02_guidance_cushion_series.csv`, 19 rows; `wf_cushion_pct` runs 2.52, 2.565 at the last two prints; 25th-75th of the last 8 = +0.95% to +2.63%). **The cushion is M3's object, not mine** — see §9. M2 supplies `Base_D` with a posterior; M3 supplies `c_D`; `guide_mid` is their product.

### 2.4 How overlap is prevented BY CONSTRUCTION — four devices

1. **One latent per economic object; indicators are measurements, never drivers.** Reviews, Eurostat, arrivals and pickup all appear in *observation* equations for the same `f^r_m`. Adding a fifth indicator **cannot** double count volume; it can only shrink the posterior variance of `f`, with precision weights implied by each indicator's own estimated residual variance. This is the structural cure for the composite-index failure: all three NNLS indexes lost to AR(1) (`data/processed/overnight/08_index_backtests.csv`) because NNLS *adds* features into a conditional mean and spends parameters an n≤18 sample cannot afford. A measurement model spends none — the loadings are shrunk to 1 by (B4).
2. **Adding-up constraints in logs with base-period weights.** (B2)/(B3) make the aggregate an identity, which removes the +0.16 to +0.21pp index-number artefact (current-period weights on growth rates) documented in `analysis/src/overnight/10_regional_forecast.py:137` vs `13_driver_model.py:376`, and retires the `CALIB = −0.41pp` plug entirely.
3. **Disclosed bands as interval-censored likelihood, not midpoints.** Regional nights since 3Q22 are letter buckets ("high-single-digit"), held in `data/processed/overnight/10_regional_panel_quarterly.csv` as `{r}_nights_yoy_lo / _hi / _mid` (79 columns, 23 quarters). The filter uses `Pr(lo ≤ Δlog n̂_r ≤ hi)` — the correct likelihood — instead of regressing on `_mid`. Band-midpoint bias (worth −0.22pp mean, −0.72pp over the last two quarters) disappears and the band width becomes an honest posterior interval rather than a reconciliation error.
4. **Conditional (within-listing, within-market) indices.** Review growth is computed inside surviving listings and inside markets, so new-listing supply growth never enters the demand index, and market mix never enters the aggregate (the 13-city index chained a city set that ran 1→13 across the sample, so it was not comparable through time — `data/processed/overnight/08_ia_tests.csv` note). Market fixed effects `α_i` absorb everything cross-sectional.

---

## 3. Data map (every path verified)

**In-repo, quarterly / event grain**

| Path | Grain | Coverage | Use |
|---|---|---|---|
| `data/processed/overnight/02_kpi_panel_quarterly.csv` | company-quarter, 119 cols, 24 rows | 3Q20-2Q26 | (A1)-(A5) observables: `nights_m`, `gbv_musd`, `revenue_musd`, `take_rate_pct` (col 82), `unearned_fees_musd` (col 32), `funds_held_for_clients_musd` (col 31) |
| `data/processed/abnb_backlog_indicators.csv` | quarter-end, 23 rows | 4Q20-2Q26 | UF/FH levels and `unearned_to_next_q_revenue` (2Q26 = 0.599 vs Q2 norm 0.697) |
| `data/processed/h2_bridge/h2_bridge_gbv_lag_conversion.csv` | quarter, 6 rows | 3Q23-4Q25 | φ prior: Q3 0.17391/0.17145/0.17182; Q4 0.11946/0.12117/0.12026 |
| `data/processed/overnight/10_regional_panel_quarterly.csv` | region-quarter, 79 cols, 23 q | 3Q22-2Q26 | interval-censored band likelihood |
| `data/processed/overnight/02_guidance_ledger.csv` | statement, 194 rows | all 23 prints | guide objects, PIT dated at issuance |
| `data/processed/overnight/02_guidance_cushion_series.csv` | print, 19 rows | 3Q21-1Q26 | cushion prior |
| `data/processed/overnight/16_consensus_at_print_merged.csv` | print, 23 rows | 2020Q4-2026Q2 | targets. Computed here, 2022Q3+: revenue surprise n=16 mean +1.714 sd **1.099**; nights n=13 mean +0.678 sd **1.527**; guide-vs-Street n=16 mean +0.629 sd **2.485** |
| `data/processed/overnight/04_consensus_at_print.csv` | print, 24 rows | 23 prints | PIT consensus with vendor attribution |
| `data/processed/overnight/02_metric_coverage.csv` | metric, 75 rows | — | which series were knowable at each date; `stopped_before_2Q26` flag |
| `data/processed/overnight/05_fx_schedule.csv`, `10_fx_daily.csv`, `10_fx_quarterly.csv` | quarter / daily (19,468 rows to 2026-08-28) | — | booking-date and check-in-date FX indices |
| `data/processed/overnight/28_fx_hedge_disclosures.csv` | quarter, 15 rows | 1Q23-2Q26 | hedge overlay `h_q` |
| `data/processed/overnight/06_fee_timeline.csv` | event, ~19 rows | 2019-2026 | dated τ shifts (15 Sep / 13 Oct 2026) |
| `data/processed/overnight/20_experiment_spec.json`, `20_frozen_q3_2026.csv` | spec / card, 19 rows | — | pre-registration template to extend |
| `data/processed/overnight/08_ia_tests.csv`, `08_eurostat_tests.csv`, `08_backlog_tests.csv` | test | — | the priors on what does and does not work |

**In-repo, monthly / market grain**

| Path | Grain | Coverage | Use |
|---|---|---|---|
| `data/processed/abnb_party_size_reviews_v2_global_month.csv` | month, 165 rows | 2013-01 → 2026-08 | global review velocity; the censoring tail is visible here |
| `data/processed/abnb_party_size_reviews_v2_market_month_shard{0..5}.csv` | market × month, ~3,863 rows/shard | 2010 → 2026 | the market×month review panel — ≈115 markets × 36 usable months ≈ **4,100 cells** |
| `data/processed/abnb_party_size_reviews_v2_seasonal_index.csv` | month-of-year | — | seasonal prior for `s_{i,mo}` |
| `data/processed/overnight/10_eurostat_platform_monthly_latest.csv` | month × 34 countries, 40 rows | 2023-01 → 2026-03 | EMEA lagged observation |
| `data/processed/overnight/08_ia_dump_metrics.csv`, `08_ia_city_yoy.csv` | city-dump, 169 rows | Dec 2022 - Aug 2026, 13 cities | the *historical* dump series (the only true multi-vintage history) |
| `data/processed/booking_curves_by_market.csv` (601), `booking_curve_daily.csv` (44,380) | market × snapshot × horizon | Jun-Jul 2026, 120 markets | pickup vintage #1; snapshot dates 2026-06-05 → 2026-07-24 identify `A(d)` |
| `data/processed/overnight/11_supply_economics.csv` | — | — | survivorship cross-check (retention 75.5%→73.4%) |

**External volume — verified present at `/Users/theomachado/abnb_scratch/release/airbnb_quant_panel_v3/`** (3.7 GB total; DuckDB 1.5.5 confirmed installed):

| File | Size / rows | Use |
|---|---|---|
| `review_events.parquet` | 909 MB, **67,500,188 rows**, 120 markets | the review panel at day grain |
| `calendar_daily.parquet` | 70 MB, **588,120,594 rows**, 120 markets | pickup vintage #1 |
| `listing_snapshots.csv` | 1.45 GB; **prior_2025 1,458,929 rows / current_2026 1,494,056 rows over the same 115 markets** | the survivorship correction `S_i(m)` — a genuine second vintage |
| `market_snapshot_panel.csv` | 231 rows (115 markets × 2 vintages) | `reviews_ltm_total`, `reviews_l30d_total`, `estimated_occupancy_l365d_mean` by vintage |
| `/Users/theomachado/abnb_scratch/raw_expansion/v3_2026-09-06/inside_airbnb_yoy_2025/` | 115-file manifest, 33 countries, dumps 2025-09-22 → 2025-11-12 | raw 2025 listings for the id-level match |

**External to acquire (all obtainable inside three weeks, per Phase 1)**

1. **A second Inside Airbnb capture** — CC BY 4.0, free, pipeline exists (`analysis/src/build_booking_curves.py`, `download_us_listings.sh`, `data/manifests/inside_airbnb_download_log.csv`). **Start 12 Sep, repeat ~12 Oct.** Lead time: the data exists the day Inside Airbnb publishes; the constraint is elapsed time between captures, so this is the one item that cannot be compressed and must start on Day 1.
2. **National arrivals**: JNTO, Spain INE, Italy ISTAT, Portugal INE, Embratur, Australia ABS — free portals/APIs, ~20 hrs to backfill 2024-2026, 0.5 hr/month thereafter.
3. **Print-day consensus, 3 Nov 2026** — Zacks/Yahoo/Fiscal.ai key-metrics estimates for revenue *and* nights. Free or $39/mo. **Non-negotiable:** the 6 Aug feature was LSEG's $4,610m next-Q; Zacks' $4,740m (4 Sep) is a later vintage and must not be substituted into a historical feature (`data/processed/overnight/20_frozen_q3_2026.csv` carries this exact warning).
4. *Optional, if budget appears:* BofA SpendingPulse lodging (free monthly press release) as a fifth indicator with its own loading. Not load-bearing.

---

## 4. Estimation and validation

### 4.1 Estimator and software

Linear-Gaussian state space on log states, **Bayesian**, in **Stan (cmdstanpy)** with a `statsmodels.tsa.statespace.MLEModel` Gaussian twin for speed during development. Temporal aggregation (monthly state → quarterly observation) via the Mariano-Murasawa device: carry `Σ_{m∈q}` as a deterministic state augmentation so the quarterly observation is exact rather than an approximation. Interval observations (regional bands) via `target += log_diff_exp(normal_lcdf(hi|·), normal_lcdf(lo|·))`. The market-level review panel is fitted **once, offline**, as a hierarchical Poisson-lognormal GLM in `statsmodels`/`pymc` on ~4,100 market-months to produce (i) `Â(d)`, (ii) `Ŝ_i(m)`, (iii) the regional review index and **its estimated sampling variance**, which is then handed to the filter as a *known* observation-noise variance. This two-stage structure is deliberate: it keeps the Stan model small (≈12 free parameters) and it makes the alt-data precision an *input*, not something the 23-quarter sample is asked to learn.

### 4.2 Priors (all informative, all sourced)

| Parameter | Prior | Source |
|---|---|---|
| `φ` | `Dirichlet(60·(0.66,0.32,0.02))` | non-negative lagged-GBV fit (§8.4 of `research/airbnb_earnings_call_study.md`) + the six conversion constants |
| `τ_LTM` | `N(0.132, 0.003²)` | `02_kpi_panel_quarterly.csv` col 82 |
| `Δτ` fee migration | `N(+0.0045, 0.0010²)` on the migrated share | +40-50bps arithmetic, `06_elasticities.csv` |
| `Δτ` direct-link pilot | `N(−0.0010, 0.0020²)` FY27 | 10% of nights × 8pt = −0.8pt bound, `11_competition-supply-and-overlays.md` §8 |
| `β_r` | `N(1, 0.25²)` | reviews grow one-for-one with nights under the null |
| `σ_β` | `HalfNormal(0.3)` | hierarchical shrinkage across 115 markets |
| `κ` step | `N(+0.01, 0.005²)` | 16%→17% platform cancellation rate, 4Q25 call |
| `μ_c` (cushion) | `N(0.0179, 0.005²)` | trailing-8 median, `02_guidance_cushion_series.csv` |
| FX pass-through | EMEA 1.04, LatAm 0.62, APAC 0.86, NA 1.0 (fixed) | `10_regional_fx_passthrough.csv` |

### 4.3 Sample-size honesty and the power statement

Computed from `16_consensus_at_print_merged.csv`, restricting to the post-normalisation regime 2022Q3+:

- revenue surprise: **n = 16**, mean +1.714%, **sd 1.099pp**
- nights surprise: **n = 13**, mean +0.678%, **sd 1.527pp**
- guide-vs-Street: **n = 16**, mean +0.629%, **sd 2.485pp**

At n=16, the critical Pearson r for α=0.05 two-sided is **0.497 (R² = 0.247)**; 80% power requires **r = 0.651 (R² = 0.42)**. At n=13 (nights), 80% power requires **r = 0.709**. **Conclusion, stated up front so a judge does not have to extract it: no single quarterly regression in this design is permitted to be the decision rule.** The decision rule is the posterior of the accounting core, whose parameters are identified off ~4,100 market-months and ~42 monthly state transitions per region; the 16-quarter series is used only to calibrate two scalars under informative priors and to *score*. The pre-registered claim is therefore a **calibration claim** — that the 80% posterior interval covers ~80% of the time and that the point beats named baselines on RMSE — not a significance claim.

Note the target choice is itself a power decision: **sd(guide-vs-Street) = 2.485pp is 2.26× sd(revenue surprise) = 1.099pp.** At a fixed R², the recoverable signal in percentage points is 2.26× larger on T1 than on T2. That is why T1 is the primary target.

### 4.4 Walk-forward / PIT protocol

Expanding window over the **last eight guide dates** (the prints 3Q24 … 2Q26). At each date `D`:

1. Truncate every input at `D` using `02_metric_coverage.csv` for series availability and `02_disclosure_changes.csv` for series that *stopped* (cross-border 1Q24, urban 4Q23, regional exact-% 3Q24 → buckets).
2. Consensus = the vendor vintage dated before `D` from `04_consensus_at_print.csv`, with `cons_revenue_vendor` recorded on the row. Never mix vintages.
3. FX = `10_fx_daily.csv` truncated at `D`. Eurostat released on its actual ~150-day calendar. Arrivals at ~25 days.
4. **The one honest PIT hole, stated plainly.** The review store is a 2026 vintage. Reviews for historical months are visible *today* but with survivorship bias increasing with age, and they were not observable in that form at `D`. Treatment: (a) **one genuinely point-in-time replay** is possible, because `listing_snapshots prior_2025` gives a real Sep-Nov 2025 vintage across 115 markets — replay the 3Q25 guide date with it; (b) the other seven dates are replayed with the current store truncated at `D` and **reported as optimistic**, with the optimism bounded by the survivorship correction (≈12-14% of review mass per year of lookback, from `1/S` with S ≈ 0.86-0.88); (c) the 5 Nov 2026 observation is **genuinely prospective** and pre-registered. The correct sentence for the memo is: *one true out-of-sample vintage, seven flagged truncation replays, one live pre-registered call.* Do not claim more.
5. Emit at each `D`: `Base_D`, the implied guide midpoint, the implied `T1`, and a full posterior.

**Baselines the tracker must beat on the same eight dates:**

| Target | Baselines |
|---|---|
| T1 (guide vs Street) | zero; trailing-4 mean of `guide_vs_street_pct`; AR(1) |
| T2 revenue surprise | trailing-4 mean (the frozen designated primary, resid sd **0.9169**); trailing-8 (1.3339); AR(1); guide + cushion; zero |
| T2 nights surprise | trailing-4 mean (resid sd **1.2078**); AR(1); zero |
| revenue LEVEL | guide + trailing-8 cushion (1.1% mean error) — the level baseline it must at least match |

Two frozen evaluation windows (2023Q1+ and 2024Q1+), both reported; a rule that fails either is dead — the discipline set in `research/notes/overnight/20_temporal-validation.md`. All returns on the `open_*` convention, never `legacy_*` (`analysis/src/overnight/20_executable_returns.py`; the overnight gap is 73% of the variance of legacy day-1).

### 4.5 Pre-registration protocol

Extend `data/processed/overnight/20_experiment_spec.json` to `spec_id: "ABNB-M2-v1"`, `frozen_at: 2026-09-26`, freezing: the four targets and their exact definitions; the indicator list and each one's transformation; the priors table in §4.2; the aggregation constraints (B2)-(B4); the scrape dates admitted; the baselines; the two evaluation windows; and the decision thresholds. Write the card to `data/processed/overnight/M2_frozen_q3_2026.csv` with: Q3 revenue and nights point + 50/80/95 intervals; the Q4 guide low/mid/high; `Pr(guide_mid < Street)`; the FY26 raise call; and the FY27 posterior median. **Score it on 6 Nov 2026** in the same file, before anyone touches the spec. This mirrors the existing `20_frozen_q3_2026.csv` discipline and makes the tracker the only component of the pitch with a live, dated, falsifiable record by the finals.

### 4.6 Why the earlier negatives do not condemn this — and which parts they do

**Permanently condemned, and absent from this design:** Google Trends (432 tests, mean walk-forward RMSE **3.05× naive**; three times worse than last quarter's number is noise, not an underpowered signal); aggregate macro (1,408 pairs, 5 of 890 Bonferroni survivors post-2022, all either the mechanical FX channel or the 2023 normalisation trend — proof being that new-vehicle CPI "nowcasts" nights as well as lodging spend does); peer read-across (the apparent signal *was* the PIT leak — MAR reported after ABNB in 2023Q3 and 2025Q1, and the corrected version is strictly worse, RMSE 3.16 vs 3.22); management tone (1,677 turns × 132 features against n=23); the three NNLS composite indexes; and any legacy-close-entry drift result. None appear here.

**Condemned in part — the TARGET, and this design fixes it.** Task A's central error was predicting *surprise* (sd ≈ 1.3pp) with features that predict *level* (sd ≈ 5pp): `pred_sd/actual_sd` was 0.14-0.33 on 16 of 17 pairs, so every "winner" was an intercept shift learning "expect +1.4%", which the trailing-4 mean supplies free. The Ledger Filter never regresses on a difference. It forecasts `Base_D` — a **level** with a level's dispersion — and then differences it against a separately sourced Street number at the last step. Whatever signal exists in the level is preserved, not cancelled.

**Condemned in part — Eurostat as a LEAD.** Correct: `eu_platform_yoy_lag1 → nights_surprise` beat everything in the 2023Q1+ window (0.850, n=11) and went to 1.209 in 2024Q1+, failing the two-window rule; and lag-0 is not available before a print. Re-scoped here as a lagged observation of a past state, which is a different and defensible use.

**NOT condemned — Inside Airbnb.** The repo's own diagnosis is *wrong grain*, not *no signal*: 13 cities against a ~220-country platform, with the city set running 1→13 across the sample so the series is not comparable through time, and `n_flagged_r05_perm05 = 0` in **both** windows — it did not even produce a spurious correlation, which is the signature of pure noise, not of a sign-flipping relationship. Meanwhile the nearest thing to a survivor is already sitting in the tree: `ia_reviews_ltm_matched_yoy → nights_yoy` has `wf_ratio_vs_naive 0.947`, `wf_ratio_vs_ar1 0.964`, sign accuracy **0.714** on 7 walk-forward points (`data/processed/overnight/08_ia_tests.csv`), and in the frozen card it carries the **lowest residual sd of any feature on both targets** — 1.1714 (nights) and 1.1362 (revenue) at n_train 10/11, against the designated trailing-4 baseline's 1.2078 and 0.9169 (`data/processed/overnight/20_frozen_q3_2026.csv`). A feature that reaches parity with naive while built from 13 non-comparable cities, on an LTM window that smears four quarters into one, and with **no survivorship correction at all**, is the textbook signature of attenuation.

*Attenuation arithmetic, stated as an assumption with its sensitivity.* If the index's sampling variance scales as `1/M` in the number of markets, moving 13 → 115 cuts measurement sd by `√(115/13) = 2.97×` and measurement variance by **8.8×**. With reliability `λ = σ²_true/(σ²_true + σ²_meas)`, an observed `r = 0.374` at `λ ≈ 0.30` implies `r_true ≈ 0.374/√0.30 = 0.68`; at `λ ≈ 0.79` the observed r rises to `0.68·√0.79 ≈ 0.61`. Against the n=16 thresholds (0.497 for p<0.05, 0.651 for 80% power), the redesign moves the concept from *undetectable* to *marginally detectable on the quarterly aggregate* — which is precisely why the quarterly aggregate is the scoring sample and not the estimation sample. If `λ` is instead 0.5 → 0.88, observed r goes 0.53 → 0.70: the conclusion is directionally robust but the exact number is not, and I will not claim it is.

---

## 5. Outputs

### 5.1 What the model emits

**For the 3Q26 print (5 Nov 2026)** — point plus 50/80/95 posterior intervals for: revenue; nights-and-seats; GBV; blended ADR (handed in from M1); the implied take rate as an *output*; and the surprise vs the **3 Nov** Street pull. Benchmarks it must be compared against in the memo: the existing frozen designated call of +1.37% revenue surprise on $4,740m → **$4,805m**, and +1.83% nights surprise on a 145m bar → **147.6m** (`20_frozen_q3_2026.csv`), and the driver model's $4,801m.

**For the Q4-26 guide (5 Nov)** — the object that pays. Mechanics at the guide date: lagged GBV = ⅔·GBV(3Q26) + ⅓·GBV(2Q26). At the team's 3Q26 GBV of $26.2bn and the actual 2Q26 $27.2bn, that is **$26.5bn**; at the measured Q4 conversion of 12.0-12.1% the arithmetic base is **$3.18-3.21bn**, before the check-in-vs-booking FX step. Applying a cushion of 1.79% (trailing-8 median) gives a **guide midpoint of $3.12-3.15bn against Street $3.16-3.20bn**, i.e. **−1% to −2%**. The team's FX-anchored bridge is lower at $3,111m and the driver model higher at $3,145m (`data/processed/overnight/13_model_quarterly.csv`, `29_fy27_bridge.csv`). **The filter's job is to resolve that $34m disagreement by forcing one φ, one FX object and one τ** — the two builds currently differ because one carries FX as a wedge on a take-rate carry and the other as an explicit residual. The emitted object is `Pr(guide_mid < Street × 0.99)`, which is the trigger for the 9/9 drift rule.

**For the FY26 raise (5 Nov)** — base rate is unambiguous: the FY guide has only ever been raised, and the raise lands at the Q3 print (FY24 margin 35.0% → ~35.5% at 3Q24; FY25 34.5% → ~35% at 3Q25). FY26 revenue growth already stands at "at least mid teens" after two raises. The filter emits `Pr(FY26 revenue-growth language is upgraded)` and the implied FY26 dollar range.

**For the FY27 guide (~Feb 2027)** and **FY27 revenue vs Street $15.73-15.76bn** — the FY27 number falls out of the φ-convolution of a monthly booked-GBV path, so it is a distribution. Expected posterior median **below** the team's $15,842m and at or below Street, with a materially fatter left tail than Street's $15.73-15.76bn dispersion implies.

### 5.2 Uncertainty representation (not a plain Monte Carlo)

Three layers, reported together:

1. **Posterior predictive** from the filter — the honest Bayesian object, but it inherits the likelihood's assumptions.
2. **Split conformal** on the eight backtest residuals for T1 and T2. With n=8 and residuals that are skewed by construction (19/19 beats), a distribution-free 80% interval is the number to put in front of a PM. Where the conformal band and the posterior disagree, **quote the conformal band** and say why.
3. **A scenario tree with data-dependent probabilities**: three branches for the Q4 guide — below Street (≤ −1%), in line (±1%), above (≥ +1%) — with probabilities read directly off the T1 posterior, and each branch carrying its own 20-day excess-return distribution estimated from the relevant executable sample (the 9-event "guide below Street" set, mean −4.21%, and ABNB's 69.6% unconditional positive-drift base rate for the other branches). The tree, not a simulation, is what goes in the memo.

### 5.3 The mechanism by which we differ from Street

1. **FX arithmetic the Street has not done.** 4Q26 revenue FX is ~82% determined by the two-prior-quarter EUR/USD mean and fits at **−0.4pp against +3.0pp guided for Q3** — a −3.4pp step that is invariant across strong-dollar, consensus and weak-dollar euro paths because the driver is already in the past (`research/notes/overnight/29_q4-fy27-bridge.md`, `data/processed/overnight/05_fx_schedule.csv`). Street's Q4 range of $3,050-3,700m on a quarter that is ~85% booking-determined and 82% FX-determined is itself the evidence that the arithmetic is not being done.
2. **The product lap.** The "+3 points of nights, +4 points of GBV" is the **bundle** (RNPL + cancellation redesign + simplified fees), not RNPL-alone or US-only. If the level shift laps rather than repeats, NA 2027 is +2.2% not +6.0% — ~1.1pp of total nights, ~$170m of FY27 revenue. The filter carries it as a year-keyed level shift in the state, so the lap is a scenario axis with a probability rather than an implicit property of a growth dictionary.
3. **The take-rate pincer.** The single-fee migration completes inside 3Q26/4Q26 (+40-50bps gross) while the 29 Aug 2026 direct-link pilot can subtract up to −0.8pt if it reaches 10% of nights — larger than the entire migration benefit. Street carries "flat".
4. **The backlog restatement.** Reported unearned fees are −0.9% y/y at 2Q26 against GBV +15.7%; restated for the prepayment shift they grew ~+15.4%. Anyone reading the reported series as demand deterioration is wrong, and anyone reading the pro-forma as clean is also wrong until `p` and `π` are separated. The filter separates them and emits the posterior.

---

## 6. Minimal code skeleton

```python
# M2_ledger_filter.py  — runnable structure; pseudo-code where a second capture is still pending.
import duckdb, pandas as pd, numpy as np, cmdstanpy
SCRATCH = "/Users/theomachado/abnb_scratch/release/airbnb_quant_panel_v3"
REPO    = ".../Citadel-ABNB/data/processed"

# ---------- STAGE 1: market x month review panel, censoring- and survivorship-corrected ----------
con = duckdb.connect()
# schema verified: source_file_id, geo_id, record_snapshot_date, listing_id, review_id, date, reviewer_id
rev = con.sql(f"""
  SELECT geo_id, date_trunc('month', date) AS m, any_value(record_snapshot_date) AS scrape,
         count(*) AS reviews
  FROM read_parquet('{SCRATCH}/review_events.parquet')          -- 67,500,188 rows, 120 markets
  WHERE date >= DATE '2022-01-01' GROUP BY 1,2""").df()
# d = days from month-end to that market's scrape date; the 50-day spread of scrape dates is the experiment
rev["d"] = (pd.to_datetime(rev.scrape) - (pd.to_datetime(rev.m) + pd.offsets.MonthEnd(0))).dt.days

# A(d): accrual curve identified CROSS-SECTIONALLY off the 50-day spread of scrape dates
#       (2026-06-05 .. 2026-07-24, see booking_curves_by_market.csv snapshot_date)
acc = fit_accrual(rev[rev.d.between(-5, 120)])                  # 3-param logistic on ~700 market-months
rev["reviews_adj"] = rev.reviews / acc.predict(rev.d).clip(0.05, 1.0)

# S_i(m): survivorship from the id-level match of the 2025 and 2026 listing vintages
#         prior_2025 1,458,929 rows vs current_2026 1,494,056 rows over the SAME 115 markets
# schema verified: geo_id, record_snapshot_date, vintage, id, ... (79 IA cols)
surv = con.sql(f"""
  WITH p AS (SELECT id, geo_id FROM read_csv_auto('{SCRATCH}/listing_snapshots.csv') WHERE vintage='prior_2025'),
       c AS (SELECT id         FROM read_csv_auto('{SCRATCH}/listing_snapshots.csv') WHERE vintage='current_2026')
  SELECT p.geo_id, count(c.id)::DOUBLE/count(*) AS s_yr FROM p LEFT JOIN c USING(id) GROUP BY 1""").df()
rev = rev.merge(surv, on="geo_id")
rev["reviews_adj"] /= rev.s_yr ** (rev.age_years)               # compounding hazard; cross-check 11_supply_economics.csv

# Hierarchical Poisson-lognormal: log R = a_i + s_i,mo + beta_i * f_r,m ; beta_i ~ N(beta_r, sig^2)
idx, idx_se = fit_review_index(rev, regions=f"{REPO}/overnight/10_regional_panel_quarterly.csv")

# ---------- STAGE 2: the state-space filter ----------
kpi  = pd.read_csv(f"{REPO}/overnight/02_kpi_panel_quarterly.csv")   # nights, gbv, revenue, take_rate, UF(31), FH(32)
bl   = pd.read_csv(f"{REPO}/abnb_backlog_indicators.csv")            # 23 quarter-ends
band = pd.read_csv(f"{REPO}/overnight/10_regional_panel_quarterly.csv")  # {r}_nights_yoy_lo/_hi  -> interval likelihood
eu   = pd.read_csv(f"{REPO}/overnight/10_eurostat_platform_monthly_latest.csv")  # ~150d lag: observes f_EMEA(m-5)
fx   = pd.read_csv(f"{REPO}/overnight/10_fx_daily.csv")              # ONE basket -> booking-date + check-in-date index
conv = pd.read_csv(f"{REPO}/h2_bridge/h2_bridge_gbv_lag_conversion.csv")  # phi prior anchor: .1739/.1715/.1718, .1195/.1212/.1203

stan = """
data { int Q; int M; vector[Q] gbv; vector[Q] rev; vector[Q] uf; vector[Q] fh;
        int NB; vector[NB] lo; vector[NB] hi; vector[M] review_idx; vector[M] review_se; ... }
parameters { simplex[3] phi; real<lower=0> tau; vector[M] g;          // log gross booked GBV, monthly
             vector<lower=0,upper=1>[Q] p; vector<lower=0,upper=1>[Q] pi; real<lower=0> kap; ... }
model {
  phi ~ dirichlet([39.6, 19.2, 1.2]');            tau ~ normal(0.132, 0.003);
  g[2:M] ~ normal(g[1:M-1] + drift + seas, sig_g);                     // state equation
  for (q in 1:Q) {
    gbv[q] ~ normal(agg_q(exp(g), kap, q), s_gbv);                     // (A1) booking-dated, net of cancellations
    rev[q] ~ normal(tau * conv_q(phi, exp(g), fxbk, fxchk, q) + hedge[q], s_rev);  // (A3) check-in dated
    uf[q]  ~ normal(uf[q-1] + tau*p[q]*gross[q] - rev[q] - refund[q], s_uf);       // (A4) fee-denominated
    fh[q]  ~ normal(fh[q-1] + (1-tau)*pi[q]*gross[q] - payout[q],      s_fh);      // (A5) amount-denominated
  }                                                                    //  -> p and pi SEPARATELY identified
  for (b in 1:NB)  target += log_diff_exp(normal_lcdf(hi[b]|mu_b[b],s_b), normal_lcdf(lo[b]|mu_b[b],s_b)); // bands
  review_idx ~ normal(beta_r .* f_from_state(g, phi), review_se);      // measurement, NOT a driver
  eu_obs     ~ normal(f_emea_lag5, eu_se);                             // ragged edge: observes a PAST state
}
generated quantities { real base_D; real guide_mid; real t1; ... }     // guide_mid = base_D * (1 - cushion_from_M3)
"""
fit = cmdstanpy.CmdStanModel(stan_file=write(stan)).sample(data=..., adapt_delta=0.95)
emit_card(fit, out=f"{REPO}/overnight/M2_frozen_q3_2026.csv")          # pre-registered; scored 6 Nov 2026
```

---

## 7. Three-week build plan (3-4 undergraduates)

**Week 1 — day level.**

- **Day 1 (Fri 12 Sep).** *Person A:* launch the second Inside Airbnb capture on the identical 120-market list (`analysis/src/build_booking_curves.py`, `data/manifests/inside_airbnb_download_log.csv`); this is the only irreversible clock in the plan. *Person B:* build the review panel from `review_events.parquet` in DuckDB (market × month, 2022-01 onward) — one query, ~20 minutes. *Person C:* pull the 6 national arrivals series. *Person D:* freeze the target definitions and open `M2_frozen_q3_2026.csv` as an empty schema.
- **Day 2.** Fit `A(d)` cross-sectionally off the 50-day scrape spread; plot the accrual curve; sanity-check that it reproduces the 1.81m → 1.10m → 0.10m May/Jun/Jul global collapse in `abnb_party_size_reviews_v2_global_month.csv` as censoring rather than demand.
- **Day 3.** Build `S_i(m)` from the id-level match of `listing_snapshots` prior_2025 vs current_2026; validate against Common Crawl 86-88% and the 75.5% → 73.4% six-city retention.
- **Day 4.** Hierarchical review index by region with sampling variance; check the (B3) annual constraint against 10-K regional nights (NA 158m / EMEA 215m / LatAm 90m / APAC 70m for 2025). If the constraint needs a >3pp/yr `ω` drift to hold, stop and diagnose before proceeding.
- **Day 5.** Accounting core in `statsmodels` (Gaussian, MLE) on quarterly data only: estimate `φ`, `τ`, `p`, `π` with no alt data. **Gate:** it must reproduce 2Q26 revenue to <1% and recover a `p` path whose implied distortion is near the documented 0.9 / 3.8 / 16.2 / 16.5%. If it does not, the specification is wrong and the alt data cannot rescue it.

**Week 2 — milestones.**
- M2.1: port to Stan; add the interval-censored band likelihood and the Eurostat lagged observation; posterior predictive checks on the eight held-out prints.
- M2.2: the PIT backtest harness — eight guide dates, vintage-correct consensus, the one true 2025-vintage replay flagged separately from the seven truncation replays.
- M2.3: beat-or-die scoring against trailing-4 / AR(1) / guide+cushion on both frozen windows.
- M2.4: second Inside Airbnb capture lands (~12 Oct) → compute pickup `P_i` and add it as a fifth measurement.

**Week 3 — milestones.**
- M3.1: freeze `ABNB-M2-v1` and write the 5-Nov card with all four targets, intervals and `Pr(guide < Street)`.
- M3.2: conformal bands and the three-branch scenario tree with data-dependent probabilities.
- M3.3: one-page exhibit for the memo — the Q4 guide bridge from lagged GBV to guide midpoint to Street, with the FX step named.
- M3.4: hand `φ̂` to M6 and the monthly regional nights state to M1; reconcile.

**What can be cut, in order:** (1) calendar pickup, if the second capture is late — the filter is complete without it and pickup is an enhancement, not a load-bearing term; (2) national arrivals beyond Japan and Spain; (3) the market-level hierarchical `β_i`, collapsing to four regional `β_r` (costs precision, not validity); (4) the conformal layer (keep the posterior). **What cannot be cut:** the survivorship correction, the accrual correction, the adding-up constraints, and the pre-registration.

---

## 8. Failure modes and the hostile-judge exchange

1. **"Your review index is a supply index."** Measured within surviving listings and within market, with `α_i` absorbing every cross-sectional level. And nights per average active listing has been 62.5 / 62.7 / 62.6 / 62.7 in 2022-25 (`data/processed/overnight/11_supply_economics.csv`) — four years of listings exactly absorbing nights — so supply and demand co-move one-for-one anyway; the index cannot be directionally wrong for that reason. What it *can* be is contaminated by regulatory delistings, which is why M4's market-level treatment flags enter as a down-weight.
2. **"One vintage. This is not point-in-time."** Correct for seven of the eight backtest dates, and I say so before you do. One true second vintage exists (115 markets, Sep-Nov 2025); one date is a genuine replay; the 5 Nov call is genuinely prospective and pre-registered with a spec hash. The seven truncation replays are reported as optimistic with the optimism bounded at ~12-14% of review mass per year of lookback.
3. **"n = 16."** Agreed, and here are the numbers unprompted: critical r 0.497, 80%-power r 0.651, sd of the three targets 1.099 / 1.527 / 2.485pp. That is exactly why the estimation sample is ~4,100 market-months and the quarterly series is the scoring sample, and why the pre-registered claim is interval coverage rather than statistical significance.
4. **"Reviews are ~50% of stays and the rate drifts."** The level is absorbed into `α_i`; only the drift matters, and constraint (B3) forces the drift to reconcile to disclosed annual regional nights. Sensitivity: a ±2pp/yr error in the drift is ±2pp on the index, which at `β ≈ 0.3` is ±0.6pp of nights growth — a third of the sd of the nights-surprise target. Reported, not hidden.
5. **"`blocked_rate` is not occupancy."** Never claimed. Pickup is a first difference within an identical (listing, stay-date) cell across two scrapes, which removes the time-invariant host-block component; the residual host-block variation is the term's main risk and is why pickup is the first item on the cut list.
6. **"The Street is not stupid about FX."** Partly right — but the Q4 range is $3,050-3,700m, a 21% spread, on a quarter ~85% determined by bookings already on the ledger and 82% determined by an FX driver already in the past. That dispersion *is* the evidence.
7. **"This is the same trade as your FX lens."** Yes, and that is corroboration rather than duplication: two independent constructions converge, and the filter is what resolves the $3,145m vs $3,111m disagreement between the team's own two builds by imposing one `φ`, one FX object and one `τ`.
8. **"Your kernel is non-stationary."** True and modelled. Long-term stays (28+ nights) recognise monthly, so a shrinking LTS share (20.2% of nights in 2022 → 13.4% in 2025, −2 to −2.5pp/yr) *shortens* the tail. `φ₁` carries a random walk with a tight innovation sd; the LTS share enters as a covariate on the tail mass.
9. **"You are fitting the accrual curve on six months."** Yes — ~700 market-month cells for three parameters. The failure mode is a systematically different posting culture by geography, which would bias `A` by region. Mitigation: fit `A` with region random effects and report the spread.
10. **"What if the 5 Nov call is simply wrong?"** Then it is wrong in public, on a pre-registered card, with a scored residual — which is worth more to a PM than an unfalsifiable model. The memo's recommendation is sized to the posterior, not to the point.

---

## 9. Interlock with the other five lenses

**Consumes:**
- **M1 (structural mix / ADR):** the four regional ADRs ex-FX and the "blended ADR as an output" construction. M2 forecasts *volume* and the recognition timing; M1 forecasts *price*. The filter never forecasts ADR, which removes the broken feedback loop where the driver model regionalises nights but applies one global ADR (worth 1.13pp of ADR, ~$175m on FY27).
- **M6 (FX / take rate / timing):** the single booking-date and check-in-date FX indices from one basket, the hedge overlay `h_q`, and the dated τ shifts. In exchange, M2 *returns* the estimated `φ̂` kernel, which retires the take-rate carry × wedge plug at `13_driver_model.py:381-383` and its +1.05pp trailing-4 revenue bias (~$50m on 3Q26, ~$165m on FY27).
- **M4 (bottom-up markets):** dated ordinance effective dates and DiD treatment flags at market level, so treated markets are down-weighted or given their own loading in the review index rather than being allowed to masquerade as demand.
- **M5 (ML challenger):** nothing structural. ML competes on the *same* pre-registered targets over the *same* eight dates with the *same* baselines. If it wins, it wins on the card.

**Hands to:**
- **M3 (guidance game):** the posterior of `Base_D` — revenue already determined on the booking ledger at the guide date. This is the missing half of the cushion model: M3 forecasts `c_D`, M2 forecasts `Base_D`, and `guide_mid = Base_D × (1 − c_D)`. Today the cushion model is applied to the *guide*, which is circular; applying it to `Base_D` makes it a real forecast.
- **M1:** the monthly regional nights state `n̂_{r,m}`, which is the `w_r` weight vector the blended-ADR identity `ADR = Σ_r w_r ADR_r` needs, with an honest posterior interval instead of a band midpoint.
- **M6:** the separated `p` and `π` paths, which answer the open question of whether the single-fee migration (not just RNPL) is depressing unearned fees and therefore whether the ~16% restatement reverses after the 15 Sep / 13 Oct deadlines.
- **The memo:** one exhibit — lagged GBV → conversion → FX step → cushion → guide midpoint → Street — with `Pr(guide < Street)` on it, and the three-branch drift tree beneath it.
