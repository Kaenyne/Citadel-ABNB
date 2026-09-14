# M4 — MOSAIC: a hierarchical, interval-censored market panel for nights and home ADR

**Market-Observed Stays And Intensity, Constrained.**
Proposal to the ABNB pitch team, 11 Sep 2026. Lens: bottom-up market-level microfoundation, reconciled to disclosed bands.
Every repo path below was opened (`head`/`wc`/`gzcat`) before it was cited. Numbers I computed in the course of writing are marked **[verified here]**.

---

## 1. Thesis in five lines

1. **What it forecasts.** The joint quarterly path of (a) *home* nights growth by region `Δln n_{r,q}`, `r ∈ {NA, EMEA, LatAm, APAC}`, and (b) *home* ADR ex-FX by region `Δln p_{r,q}`, for 3Q26 through 4Q27, as a **posterior distribution**, not a point. It does **not** forecast revenue directly; it hands regional nights and regional ex-FX ADR to the φ-kernel / FX lens (M6) and to the guidance-policy lens (M3).
2. **Level, not surprise.** The target is the *level* of the growth vector — the quantity the guidance-policy function takes as its state variable and the quantity the disclosed bands measure. The repo has already proved that "surprise vs Street" is unforecastable at n≈10 (`docs/revenue-forecast-strategy/01_ground-truth/02_model_audit.md` §4.2b; `data/processed/overnight/20_task_summary.csv` `pred_sd_over_actual_sd` 0.14–0.33 on 16 of 17 pairs). I do not re-fight that.
3. **What it replaces.** The 24 hand-written regional growth cells at `analysis/src/overnight/13_driver_model.py:253-259` (classified **assumed**, no estimator, no error bar, `02_model_audit.md` §2), the fixed ADR deflator `IDX = {1.42, 0.97, 0.68, 0.59}` in `10_regional_panel.py` (**plug**, calibrated on 2025 only), the `CALIB = −0.41pp` reconciliation fudge (`10_regional_forecast.py:78,137`, not applied in `13`), and the jointly-unidentified **+3.6pp "pricing + sub-regional mix"** residual of the ADR decomposition (`analysis/src/adr/07_assemble.py:103-104`).
4. **Why it should beat what exists.** The current regional build has an estimation sample of **zero** — it is prose. MOSAIC has 120 markets × 34 countries × ~180 monthly review observations ≈ 2.0 × 10⁴ market-months of demand, 258 matched-vintage city pairs for a repeat-listing price index, 48 Common Crawl survival crawls, and 32 dated regulatory treatments. The aggregate is then pinned by **exact** adding-up constraints (`Σ_r n_{r,q} = N_q` disclosed; `Σ_q n_{r,q} = A_{r,y}` from the 10-K geographic table) and **interval** constraints (the letters' buckets). The bottom-up panel supplies *within-band position*; the disclosures supply the level. Neither is asked to do the other's job.
5. **The differentiated call it produces.** On 15 Sep 2026 (ex-EEA) and 13 Oct 2026 (EEA+CH) the host-fee migration completes. Payout-neutral repricing lifts the *listed* nightly price of the migrating cohort ~+14.8% while leaving the *all-in guest price* — which is what GBV and ADR are built from — approximately unchanged. Inside Airbnb's 2026 schema carries **both** bases in the same file (`price` at column 47 and `price_quote_total_price` / `price_quote_price_per_night` at columns 50–51 **[verified here]** on `raw_expansion/v2_2026-09-05/inside_airbnb_current/spain/catalonia/barcelona/2026-06-24/listings.csv.gz`). A second capture across the deadlines therefore separates the accounting reclass from real repricing directly. Anyone reading listed prices — including the sell side and including this team's own pre-2026 series — will print a spurious ADR jump in 4Q26. That is a falsifiable, dated, mechanism-level edge no Street model has.

---

## 2. Formal specification

### 2.0 Indices and objects

| Symbol | Meaning |
|---|---|
| `i` | listing id (Airbnb's own, stable across vintages) |
| `m` | market (120 in the current store; 13 with deep history) |
| `c` | country (34 in the current store) |
| `r` | reporting region, `{NA, EMEA, LatAm, APAC}` |
| `ℓ` | reviewer language (origin proxy) |
| `t` | calendar month |
| `q` | fiscal quarter |
| `v` | **vintage** = dump date of an Inside Airbnb scrape |
| `k` | regulatory factor, `k = 1..32` (`research/regulatory/factors.json`, 32 records **[verified here]**) |

### 2.1 The intensive/extensive decomposition (no double count, by construction)

```
ln N_{m,q}  =  ln A_{m,q}      (extensive: bookable listings)
             + ln s_{m,q}      (intensive: stays per listing)
             + ln L_{m,q}      (length: nights per stay)
```
This is an **identity in logs**, so the three terms cannot double count: any effect assigned to one is mechanically absent from the others. This is the same discipline `02_model_audit.md` §3.3 recommends for the regional panel ("build in log levels with chain-linking, so the aggregate is an identity"). The supply/demand/price blocks below *measure* these three terms; they are never *added* to each other.

### 2.2 The demand block — review velocity with a survivorship correction

Reviews are the only demand observable with **full history inside a single current vintage**: `reviews.csv.gz` carries `listing_id, id, date, reviewer_id, reviewer_name, comments` **[verified here]**, i.e. a dated event per stay, back to 2010. That is why this lens works at all with a one-vintage 120-market store.

Let `R^v_{m,t}` = reviews in market `m`, month `t`, as counted **in vintage `v`**. The identity that killed the overnight test and that nobody wrote down is:

```
ln R^v_{m,t}  =  ln R*_{m,t}  +  ln Surv_m(t → v)  +  ε
```

`R*` is the true review flow; `Surv_m(t→v)` is the probability that a listing alive in month `t` is still present in the vintage-`v` file. A current-vintage review file is **survivorship-truncated**: every review belonging to a listing that has since been delisted is gone. Because the delisting hazard is ~3.6–4.1% per month post-fee-change (`research/notes/2026-09-07_fee-churn-recent-followup.md`) and Common Crawl puts 12-month listing survival at 86–88% since 2023 (`data/processed/cc_listing_survival.csv`, 48 crawls from `CC-MAIN-2021-17` onward **[verified here]**), a single vintage understates 2023 review flow by an order of 15–25% and 2021 flow by more. **Any y/y computed naively inside one vintage is biased toward showing acceleration.**

Identification of `Surv`: the 13-city stack observes the *same* `(m,t)` cell in up to **21 vintages** (`data/processed/overnight/08_ia_dump_metrics.csv`, 168 dumps, 13 Dec 2022 → 30 Aug 2026; per-city counts austin 15, barcelona 10, chicago 12, london 10, los-angeles 12, mexico-city 11, nashville 15, new-orleans 11, new-york-city 11, paris 17, rome 21, san-diego 13, sydney 10 **[verified here]**). Run

```
ln R^v_{m,t}  =  μ_{m,t}  +  f(age = v − t; m)  +  u_{m,t,v}
```

a two-way fixed-effects regression where `μ_{m,t}` is the cell fixed effect and `f(·)` is a flexible (spline or age-bin) survivorship curve. `f` is identified purely off *within-cell, across-vintage* variation — it needs no assumption about demand. Fit `f` on the 13 deep cities, shrink it hierarchically toward the Common Crawl platform-wide hazard, and apply it to all 120 markets. Output: `R̂*_{m,t}`, a survivorship-corrected monthly demand proxy for 120 markets, 2015–2026.

Stays: `s_{m,q} · A_{m,q} = S_{m,q} = R̂*_{m,q} / ρ_{m,q}`. The reviews-per-stay ratio `ρ` is a **level plus slow drift**, not a constant, and is calibrated — never assumed — by the aggregation constraints of §2.6: the disclosed global nights `N_q` and the 10-K regional annuals pin `ρ` up to the coverage wedge. Priors come from the repo's own review→party-size work (`data/processed/abnb_party_size_reviews_v2_market_month_shard{0..5}.csv`, 22,455 market-month rows **[verified here]**; `abnb_party_size_reviews_v2_seasonal_index.csv` supplies a monthly seasonal on the review-composition side).

**Do not use `estimated_occupancy_l365d` / `estimated_revenue_l365d` (columns 73–74 of the 2026 listings file) as truth.** They are Inside Airbnb's own "San Francisco model": reviews × a hard-coded review rate × a min-nights cap. `data/processed/market_summary_2026.csv` reports `est_occupancy_l365d_mean = 74.89` for Buenos Aires **[verified here]** — an implausible platform occupancy. They are a cross-check on `ρ`, nothing more. Same warning class as the repo's standing rule that `blocked_rate` is not occupancy (`data/processed/booking_curves_by_market.csv`).

### 2.3 The supply block — extensive margin, three independent observables

`A_{m,q}` (bookable listings) is measured from (i) listing counts per dump (`data/processed/overnight/08_ia_dump_metrics.csv`, `listings`, `n_avail`, `blocked_30`, `blocked_90`, `entire_share`, `partial_scope` **[verified here]**), (ii) matched-id retention and gross adds between vintages (`data/processed/inside_airbnb_like_for_like.csv`, 258 pairs with `matched`, `retention`, `new_share_b`, `gross_adds`, `exits`, plus PIT scope flags `scope_vs_peer_a_pit` **[verified here]**), and (iii) the review-implied active set — a listing is *active* in month `t` if it has a review within a market-specific window. Observable (iii) is the only one available for all 120 markets from one vintage; (i) and (ii) discipline it on 13 cities.

The `partial_scope` flag matters and is already in the data: Inside Airbnb's city definitions change (the failed overnight test chained a city set that grows from 1 to 13 across the sample — `research/notes/predictive/03_macro-altdata-nowcast.md` finding 7). MOSAIC's aggregation is a **balanced-panel log difference**: only `(m, t)` cells present in both endpoints enter the index, and market entry/exit is handled by chain-linking, never by level comparison.

### 2.4 The price block — a repeat-listing hedonic index (Case–Shiller for ADR)

The ADR decomposition's largest term, **+3.6pp of 2025 within-region ex-FX ADR**, is "pricing + sub-regional mix", jointly unidentified because Airbnb discloses no country ADR (`research/notes/2026-09-07_adr-decomposition.md` §3, §4.3). A repeat-listing index identifies it, because the *same listing* is its own control:

```
ln p_{i,v}  =  μ_{m,τ(v)}  +  α_i  +  x'_{i,v} β  +  e_{i,v}
Δ ln p_{i, v→v'}  =  (μ_{m,τ(v')} − μ_{m,τ(v)})  +  Δx'_{i} β  +  Δe
```

Listing fixed effects `α_i` difference out; `μ_{m,τ}` is the **like-for-like price level** of market `m` at time `τ`, estimated by weighted repeat-sales (Bailey–Muth–Nourse with a Case–Shiller three-stage variance weight on the interval length, because long gaps have fatter `Δe`). Then, by construction and with no residual left over:

```
Δ ln ADR^{home,exFX}_{r,q}  =  Σ_{m∈r} ω_{m,q-4} Δμ_{m,q}        ← like-for-like pricing (identified)
                             +  Σ_{m∈r} (ω_{m,q} − ω_{m,q-4}) μ_{m,q-4}   ← sub-regional (within-region) mix (identified)
                             +  Δ(composition | x)                         ← unit-size / LOS / quality, from β
```
with `ω_{m,q}` = nights weights **from the nights block of §2.2**, so the mix term is an *output of the same panel*, not a separate assumption. Three things follow:

- **The +3.6pp residual splits into two named, measured terms.** This is the single largest unidentified quantity in the team's ADR work.
- **Geographic mix stops being a row.** `02_model_audit.md` §3.4 prices the broken feedback loop at **1.13pp of ADR = ~$175M on FY27**; MOSAIC makes `ADR_blended = Σ_r ω_r ADR_r` an identity, exactly recommendation 3.
- **All composition terms come from one specification.** `β` carries capacity (`accommodates`), `bedrooms`, `beds`, `room_type`, `property_type`, rating and `license` presence, estimated jointly. That is `02_model_audit.md` recommendation 5: "terms estimated in one specification cannot double count; terms estimated in three separate scripts always can." It also resolves the live bedrooms-per-log-capacity mismatch (docstring 1.27 vs computed 1.37, `analysis/src/adr/13_party_size_adr.py:7` vs `:64`) by never needing that conversion.

**The price-basis splice (critical).** Pre-2026 dumps carry `price` = nightly rate for the first available night. 2026 dumps carry `price` **and** `price_quote_total_price` / `price_quote_price_per_night` / `price_quote_raw` — a fee-inclusive quote for a specific check-in/check-out **[verified here, columns 47–52]**. These are different objects and the repo already knows the historical listed-price series cannot be extended (`research/notes/predictive/03_macro-altdata-nowcast.md`; `inside_airbnb_like_for_like.csv` carries `price_basis_a`, `price_basis_b`, `price_comparable` flags **[verified here]**). MOSAIC runs **two parallel indices** — `μ^{listed}` and `μ^{allin}` — spliced at the basis change using the 1.71M-quote overlap in `data/processed/overnight/06_quote_line_items.csv` and `06_quote_discount_panel.csv`. This is not housekeeping; it is the whole fee-migration trade (§5).

### 2.5 Regulation and events — market-level difference-in-differences

`research/regulatory/factors.json` holds 32 dated factors (REG-01 NYC LL18 platform enforcement 2023-09-05; REG-02 Spain removal order 2025-05-19, 65,122 ads removed by Jul 2025, €64.06m fine Dec 2025; EU Reg 2024/1028 applying 2026-05-20; Barcelona licence non-renewal to Nov 2028 **[verified here from `factor_register.md`]**). Treatment `D_{m,t,k} = 1{t ≥ d_k, m ∈ M_k}`. Event study on the two log outcomes:

```
ln A_{m,t}  =  a_m + b_{c,t} + Σ_{h=−6}^{+12} θ^A_h · 1{t − d_{k(m)} = h}  +  u
ln R̂*_{m,t} =  ã_m + b̃_{c,t} + Σ_{h}      θ^R_h · 1{t − d_{k(m)} = h}  +  ũ
```

`b_{c,t}` (country × month) absorbs national demand and FX; identification is off *within-country, cross-market* timing. Use Callaway–Sant'Anna / Sun–Abraham to avoid the staggered-treatment negative-weight problem. Aggregate `θ^R` to EMEA by nights weight.

This replaces `REG_DRAG_PP` and the `reg_mult = 1.67` median→mean fudge (`13_driver_model.py:194,217,265-267`), and — decisively — **it removes the §3.8 double count**: the DiD counterfactual is the untreated-market growth path *inside the same panel that produces the forecast*, so regulation is no longer subtracted on top of a judgemental base growth rate that already contains it. It also adjudicates the open contradiction between the Monte Carlo and the restated six-city retention (75.5% → 73.4%, new-listing share flat; `research/notes/overnight/21_inside-airbnb-pair-eligibility.md`).

Events (World Cup ended 19 Jul 2026, Milan Olympics 1Q26) enter the same event-study frame from `data/processed/h2_bridge/h2_event_catalogue.csv`.

### 2.6 The reconciliation layer — where overlap is killed

The 120-market panel covers a fraction of a ~220-country platform. **Never use its level.** Use only its log growth, as a *noisy measurement of a latent state*:

```
STATE      Δln n_{r,q}   = latent regional home-nights growth               (4 × 24 states)
           δ_{r,q}       = coverage/representativeness wedge, random walk:  δ_{r,q} = δ_{r,q−1} + ν,  ν ~ N(0, σ_δ²)

MEASUREMENT
 (M1) covered panel:   Δln N̂^{cov}_{r,q}  =  Δln n_{r,q} − δ_{r,q} + η,     η ~ N(0, σ_η²)
 (M2) letters' bucket: lo_{r,q} ≤ Δln n_{r,q} ≤ hi_{r,q}        ← INTERVAL-CENSORED likelihood
 (M3) aggregation:     Σ_r exp(ln n_{r,q-4} + Δln n_{r,q})  =  N_q            ← EXACT (disclosed total)
 (M4) annual 10-K:     Σ_{q∈y} n_{r,q}  =  A_{r,y}                            ← EXACT (2025: NA 158m, EMEA 215m, LatAm 90m, APAC 70m)
 (M5) Eurostat:        Δln EU27_{c,t}  =  Δln n_{c,t} + ξ_{c,t}               ← EMEA subset, platform-share state ξ
 (M6) national stats:  JNTO / INE / ISTAT / ABS arrivals → cross-border leg only
```

Four properties that matter to a PM:

- **No residual exists to calibrate.** (M3) and (M4) are equality constraints, so the +0.19pp index-number bias documented in `02_model_audit.md` §3.3 **[their recomputation]** and the 0.41pp gap between WS10's `CALIB` and `13`'s zero cannot arise. The bands become an honest posterior interval rather than a midpoint plus a fudge.
- **FX never enters the nights weights.** The §3.2 defect — regional *revenue* in USD divided by a fixed ADR index producing FX-contaminated nights shares, worth ~+0.09pp of nights growth procyclically with dollar weakness — is structurally impossible here: the weights come from review-derived quantities, which are unit counts.
- **Every alternative dataset is a measurement, not a regressor.** The overnight programme added Eurostat, Inside Airbnb and macro as *features in a regression on 20 quarterly observations*. MOSAIC puts each in as an observation equation on a latent state it can actually see. That is why Eurostat's 150-day publication lag — fatal for a lead predictor (`08_test_scoreboard.csv`: `eu_platform_yoy_lag0 → rev_yoy` best ratio 0.932, never beats naive **[verified here]**) — is harmless here: a late observation still sharpens the *smoothed* estimate of `δ_r` and hence next quarter's forecast.
- **Home vs seats is explicit.** MOSAIC forecasts *home* nights only. Seats (Experiences/Services) and hotel room-nights are handed to M1/M5, which resolves the three-way contradiction in seats treatment worth **0.57pp of revenue growth = ~$88M on FY27** (`02_model_audit.md` §3.6).

### 2.7 Cross-border: a language-flow gravity model

Origin–destination is not observable in Inside Airbnb. Reviewer *language* is (`comments` free text; already parsed at `data/processed/abnb_party_size_reviews_v2_language_year_shard{0..5}.csv` and `abnb_party_size_reviews_v2_by_language_year.csv` **[verified here]**). Specify

```
ln R̂*_{ℓ,m,t}  =  λ_{ℓ,m}  +  γ_{m,t}  +  β_FX · ln FX_{ℓ→m,t}  +  β_S · ln Seats_{ℓ→m,t}  +  ε
```

`γ_{m,t}` (market × month) absorbs *all* destination-side demand, seasonality and local FX. The FX elasticity is identified purely from relative movement **across origin-language groups within the same market-month** — a clean, textbook gravity identification. Panel size ≈ 120 markets × ~10 usable languages × 60 months ≈ **7 × 10⁴ cells**. That is the answer to the n≈20 problem: the parameters are estimated at market grain, and only the *aggregate* is reconciled at quarterly grain.

This rebuilds the cross-border share (46% of gross nights, last disclosed 1Q24, `data/processed/overnight/05_crossborder_share.csv`) as a live series and prices the Middle East / inbound-US softness that BKNG and EXPE flagged in their 2Q26 calls.

---

## 3. Data map

### 3.1 In the repo (all verified by opening)

| Path | Grain | Size | Role |
|---|---|---|---|
| `raw_expansion/v2_2026-09-05/inside_airbnb_current/` (sibling OneDrive folder) | country/region/market/dump-date → `listings.csv.gz`, `calendar.csv.gz`, `reviews.csv.gz` | **9.2 GB**, 315 files, **120 markets, 34 countries**, dumps 14 Jun – 10 Aug 2026 | primary panel |
| `raw_expansion/v2_2026-09-05/inside_airbnb_current_manifest.csv` | file | 316 rows with sha256 + `verified` | integrity; also the market list for the capture script |
| …/`<market>/<date>/listings.csv.gz` | listing | schema includes `accommodates`, `bedrooms`, `beds`, **`price` (47)**, **`price_quote_checkin_date` (48)**, **`price_quote_total_price` (50)**, **`price_quote_price_per_night` (51)**, `availability_30/60/90/365`, `number_of_reviews_ltm/l30d/ly`, `estimated_occupancy_l365d`, `license`, `review_scores_*` | hedonic `x`, supply, licence flag for DiD |
| …/`<market>/<date>/calendar.csv.gz` | listing × date | **5 columns: `listing_id,date,available,minimum_nights,maximum_nights` — NO price** | forward availability only; min-nights for LOS floor |
| …/`<market>/<date>/reviews.csv.gz` | review | `listing_id,id,date,reviewer_id,reviewer_name,comments` | demand flow, language, repeat-guest |
| `data/processed/overnight/08_ia_dump_metrics.csv` | city × dump | 168 dumps, 13 cities, Dec 2022 – Aug 2026 | survivorship curve `f(age)`; seasonal factors |
| `data/processed/overnight/08_ia_city_yoy.csv` | city × dump | 103 rows incl. `reviews_l30d_matched_yoy`, `blocked_30_matched_yoy_pts` | the *matched* flow features — the seed signal |
| `data/processed/inside_airbnb_like_for_like.csv` | city × vintage pair | 258 pairs, `retention`, `lfl_price_chg_median`, `price_basis_a/b`, `price_comparable`, PIT scope flags | repeat-listing index prior; basis splice |
| `data/processed/cc_listing_survival.csv` / `cc_listing_survival_by_age.csv` / `cc_listing_panel.csv` | crawl | 48 crawls from 2021-04-26 | platform-wide survival prior |
| `data/processed/market_summary_2026.csv` | market | 120 rows, `listings`, `hosts`, `entire_home_share`, `multi_host_share`, `license_disclosed_share`, `reviews_ltm/l30d`, `avail365_mean` | market covariates, weights |
| `data/processed/booking_curves_by_market.csv` / `booking_curve_daily.csv` | market × horizon / day | 600 / 44,379 rows, single vintage | forward-availability shape; **not** occupancy, **not** y/y |
| `data/processed/abnb_party_size_reviews_v2_market_month_shard{0..5}.csv` | market × month | **22,455 rows** | review flow already parsed at the target grain |
| `data/processed/abnb_party_size_reviews_v2_language_year_shard{0..5}.csv`, `_by_language_year.csv` | language × year | — | gravity origin proxy |
| `data/processed/overnight/10_regional_panel_quarterly.csv` | region × quarter | 23 quarters, `{r}_nights_yoy_lo/hi/mid`, `_basis`, `_phrase`, `_adr_yoy_reported/exfx` | **the interval observations (M2)** |
| `data/processed/overnight/27_regional_bucket_check.csv` | quarter × region | `bucket_lo/hi`, `prior_share_pct`, `picked_sum_residual_pp` | existing bucket arithmetic to fold in |
| `data/processed/overnight/10_regional_adr_fx.csv` | region × quarter | reported and ex-FX regional ADR + `basket_fx_yoy_pct` | ADR level anchors, FX-neutral deflator |
| `data/processed/overnight/10_xbrl_revenue_geography.csv` | geo × period | 258 rows, XBRL-filed | cross-check only (FX-contaminated; never a nights source) |
| `data/processed/overnight/02_kpi_panel_quarterly.csv` / `02_kpi_panel_long.csv` | company-quarter | 119 cols / 1,050 quotes | disclosed totals `N_q`; regional phrase history from 3Q22 |
| `data/processed/eurostat_platform_nights_monthly.csv` / `_by_country.csv` / `_quarterly.csv` | month × 37 countries / country / quarter | 99 months from 2018-01 | measurement (M5) |
| `research/regulatory/factors.json` + `factor_register.md` + `data/raw/regulatory/` (171 MB) | factor | **32 factors**, dated | DiD treatment calendar |
| `data/processed/overnight/11_regulatory_overlay.csv`, `22_regulatory_delta.csv` | year | median/mean/p95 drags | the thing DiD replaces; keep as a prior-band cross-check |
| `data/processed/overnight/06_quote_line_items.csv`, `06_quote_discount_panel.csv` | quote, aggregated | 1.71M underlying quotes, Mar–Aug 2026 | price-basis splice; fee-inclusive hedonic |
| `data/processed/listing_churn_panel/`, `listing_churn_archive/`, `listing_platform_history/` | market/country rates | `market_rates.csv`, `pooled_rates.csv`, `snapshot_quality.csv` | churn priors |
| `analysis/src/inside_airbnb_supply_panel.py` | script | has `discover` / `download` / `build` modes and a CDN HEAD-probe | **reuse verbatim for the capture** |
| `analysis/src/inside_airbnb_review_velocity.py`, `build_market_summary.py`, `build_booking_curves.py`, `count_reviews_duckdb.py` | scripts | — | existing pipeline |

### 3.2 External, obtainable inside three weeks (all free)

| Source | Acquisition | Lead time | What it pins |
|---|---|---|---|
| **Inside Airbnb, second capture, 120 markets** | `python analysis/src/inside_airbnb_supply_panel.py discover` adapted to the 120-market list in the manifest; daily HEAD-poll of `https://data.insideairbnb.com/<country>/<region>/<market>/<date>/data/*.csv.gz`; CC BY 4.0 | start **14 Sep**; first new dumps land mid-Sep → late Oct | repeat-listing index across the fee deadlines; second point for `Surv` outside the 13 cities |
| JNTO monthly arrivals (Japan) | free portal/API, `jnto.go.jp/statistics` | ~20 days after month end | APAC cross-border leg |
| INE (Spain), ISTAT (Italy), INE (Portugal) | free portals | 20–30 days | EMEA; also Spain registry DiD |
| Embratur / IBGE (Brazil), DATATUR (Mexico) | free | 30 days | LatAm |
| ABS (Australia) short-term arrivals | free | 30 days | APAC |
| Municipal registries: Austin daily (`data.austintexas.gov`, already 527 dates in repo), NYC OSE, Barcelona, Paris | open data / FOIA | 0–30 days | DiD treatment intensity |
| Eurostat `tour_occ_nim` refresh | free API | publishes ~150 days late | (M5) smoothing only |

Explicitly **not** required: AirDNA, Facteus, Placer, Visible Alpha, OAG. MOSAIC is built entirely from free, CC BY 4.0 and government sources — a point worth making to a judge who assumes bottom-up means bought.

---

## 4. Estimation and validation

### 4.1 Estimator stack

- **Stage 1 — survivorship (`f(age)`).** Two-way FE with cell (`m,t`) and age-bin dummies on the 13-city stack; `pyfixest` or `linearmodels.PanelOLS`; hierarchical shrinkage of market-specific `f` toward the pooled curve and toward the Common Crawl hazard (empirical-Bayes; or a single PyMC hierarchical fit — it is a small model).
- **Stage 2 — repeat-listing index.** Weighted repeat-sales, three-stage Case–Shiller weighting (`statsmodels.WLS`), separately for `μ^{listed}` and `μ^{allin}`, with the hedonic `x` differences included so `β` is estimated jointly with `μ`. Winsorise at the 1st/99th market percentile (the convention already used in `inside_airbnb_supply_panel.py`).
- **Stage 3 — regulation.** Callaway–Sant'Anna (`differences` / `did` in Python, or R `did::att_gt`) on the market panel; report the event-study path, not a single ATT.
- **Stage 4 — gravity.** High-dimensional FE Poisson (PPML, `pyfixest.fepois`) on review counts, with market×month and language×market FE. PPML because counts are over-dispersed with zeros.
- **Stage 5 — reconciliation.** Bayesian state-space in **PyMC** (or Stan). Small by design: 4 regions × 24 quarters of `Δln n` + 4×24 `δ`. Interval likelihood via `pm.Censored(pm.Normal(...))`, or in Stan `target += log_diff_exp(normal_lcdf(hi|·), normal_lcdf(lo|·))`. Exact constraints (M3)/(M4) imposed by **reparameterisation** — model `K−1` free regional growths and solve the last from the total — so no soft penalty is needed and no constraint can be violated. NUTS, 4 chains, target_accept 0.95; check `r_hat < 1.01` and divergences.

**Priors (state them in the memo).** `σ_δ ~ HalfNormal(0.01)` — the coverage wedge drifts slowly; `σ_η ~ HalfNormal(0.02)` — the covered panel is a ±2pp measurement; `Δln n_{r,q}` gets an AR(1) prior with `ρ ~ Beta(6,2)` centred near 0.75 and `σ ~ HalfNormal(0.04)`. **The AR(1) prior is deliberate: the repo has shown nothing beats AR(1) for nights (`research/notes/overnight/20_temporal-validation.md`), so AR(1) is my prior mean and the data must move me off it.** That is how you use a negative result correctly.

### 4.2 Point-in-time discipline

The binding PIT fact, from the repo's own code: Inside Airbnb keeps only the latest dump on its page; older files persist on the CDN roughly 12 months (`analysis/src/inside_airbnb_supply_panel.py` docstring, **[verified here]**), and `08_altdata_backtests.py:248` already flags that the IA scope flag "uses LATER scrapes, so a frozen replay may only…" be partial. Therefore:

1. **True vintage replay exists only for the 13 cities, Dec 2022 → Aug 2026 = 15 quarters.** The dump date *is* the vintage. At each historical guide date `g`, admit only dumps with `dump_date ≤ g` and only reviews with `date ≤ g`.
2. For the 120-market store there is **one** vintage, so no historical replay is possible. Its historical contribution is limited to the survivorship-corrected review series, which is *reconstructible* but not *vintage-safe* — it must be labelled as such in the memo and excluded from any claim of out-of-sample performance.
3. The `_pit` scope columns already in `inside_airbnb_like_for_like.csv` (`scope_vs_peer_a_pit`, `scope_ref_n_a_pit`) are the correct convention and must be used.
4. Returns, if any lens uses MOSAIC output for a trade, must use `open_*` not `legacy_*` (`analysis/src/overnight/20_executable_returns.py`).

### 4.3 Baselines and the scoring rule

Baselines MOSAIC must beat, at the aggregate: **AR(1) on `Δln N`**, prior-year `Δln N`, the **band midpoint**, and the guide bucket. At market grain: market-level AR(1) and a seasonal-naive.

**Sample-size honesty and the power statement.** At the aggregate there are 23 disclosed quarters, 15 with usable vintages, and 4 regions ⇒ ~60 region-quarters of which ~46 carry a bucket. A single-feature quarterly regression against AR(1) at n=15 has, for a true incremental R² of 0.25, power ≈ 0.35 at α = 0.05 — i.e. **you cannot win that fight and must not pretend to.** `02_model_audit.md` §4.2d states this as binding and I accept it. MOSAIC therefore is **not scored as a quarterly regression**. It is scored three ways:

- **(i) Market grain, where the power is.** DiD: 120 markets × ~15 quarters = 1,800 cells; gravity PPML: ~7×10⁴ cells; repeat-sales: tens of thousands of matched pairs. These are ordinary, adequately-powered estimates with conventional standard errors and pre-trend tests.
- **(ii) Band-sharpening.** For each historical region-quarter with a disclosed bucket, does the posterior 80% interval sit **inside** the bucket and **contain** the eventual reconciliation-implied value? Score with interval score / CRPS against the "posterior = uniform on the bucket" null. This is the honest aggregate test at n=46 region-quarters and it is the one a judge will accept.
- **(iii) Conformal coverage.** Split-conformal intervals on the market-level nowcast (calibrate on the 13-city × 15-quarter holdout) give distribution-free coverage guarantees that do not depend on the Bayesian model being right.

### 4.4 Why the earlier negatives do not condemn this design — and which parts they do

**Condemned, and I do not use them:** Google Trends (432 tests, mean walk-forward RMSE **3.05× naive**, `08_test_scoreboard.csv` `tr_us_airbnb_yoy → rev_yoy` best ratio 1.880 in window 1 **[verified here]**); aggregate macro (5 of 890 Bonferroni survivors, all the FX mechanism or the 2023 normalisation trend); peer read-across (the signal *was* the PIT leak); management tone; composite NNLS indexes. None appear anywhere in MOSAIC.

**Not condemned — misdiagnosed.** The Inside Airbnb family scored `n_flagged_r05_perm05 = 0` in **both** windows (`data/processed/overnight/08_test_scoreboard.csv` **[verified here]**). That is the tell. An underpowered-but-real signal still throws spurious correlations at r>0.5 some of the time; **zero flags in 36 tests means the feature was broken, not weak.** Three named defects, each from the repo:

1. **Wrong statistic.** The headline feature is `ia_reviews_ltm_matched_yoy` — a *trailing-twelve-month stock*, differenced y/y, i.e. a 24-month window on a quarterly target. `data/processed/overnight/08_ia_tests.csv` gives it r = 0.374, p = 0.257, walk-forward ratio 0.947 vs naive at n = 11 **[verified here]**. The *flow* version, `ia_reviews_l30d_matched_yoy → nights_yoy`, is the best IA feature at **0.813× naive in both windows**. The flow works; the stock does not. Nobody built the monthly flow panel.
2. **Wrong coverage.** 13 cities against a 220-country platform, with the city set growing 1 → 13 through the sample. The 120-market store is **9× the markets and 34 countries**, and MOSAIC uses a balanced-panel chain-link so the set cannot grow mid-sample.
3. **No survivorship correction.** §2.2. This alone biases every single-vintage y/y toward showing acceleration, and it was never applied.

**Eurostat is not condemned either — it was given the wrong job.** Best ratio 0.932 as a *lead predictor* with a 150-day lag. As a *measurement equation in a filter* (M5) it never needs to lead; it sharpens the smoothed history of `δ_r`, which is where the forecast's information about coverage bias comes from. `eu_platform_yoy_lag1 → nights_surprise` did beat every baseline in the 2023Q1+ window (ratio 0.850, n = 11) before failing the frozen two-window rule at 1.209 — consistent with a real but noisy measurement, which is exactly how MOSAIC treats it.

---

## 5. Outputs

### 5.1 The four deliverables

**(a) 3Q26 print (5 Nov 2026).** A posterior over: printed Nights and Seats growth; **home** nights growth; the four regional growths with 80% intervals *inside* the "low double-digit" guide bucket; home ADR ex-FX decomposed into like-for-like (`Δμ`), within-region mix, unit-size/LOS composition, and — separately — the seats and hotel dilution handed in from M1. Calibration target: the frozen card `data/processed/overnight/20_frozen_q3_2026.csv` (nights +10.2%, ADR +3.8%, revenue $4,801M). **MOSAIC's prior expectation is that the disclosed regional buckets for 3Q26 land at or slightly below their midpoints in NA and EMEA**, because the 3Q26 quarter has no World Cup booking residual (the tournament ended 19 Jul 2026 and its stay-nights were booked in 4Q25–2Q26) and because the US RNPL anniversary begins in 3Q26.

**(b) Q4 26 guide (5 Nov 2026) — the number the pitch is judged on.** MOSAIC emits `P(nights bucket)` over {high-single-digit, low double-digit, low teens}. This is the sign-setting variable: `research/notes/catalyst_calendar.md` records that the earnings-move sign is set by the nights guide, not the beat, with a mean absolute move of **12.1%**. If the bottom-up panel shows Q4-relevant booking demand decelerating (which is what the RNPL US lap plus a −3.4pp FX step implies), the guide reverts to "high-single-digit" and the historical analogues are −13.4% (2 Nov 2022), −10.9% (10 May 2023), −8.0% (7 Aug 2025). Combined with the Q4 revenue guide landing near $3.05–3.10bn against Street $3.20bn, this triggers the repo's one executable rule — guide below Street → 20-day drift 9/9 negative, mean −4.21% on next-open entry.

**(c) FY27 guide (Feb 2027).** Regional nights path with the **lap** as an explicit axis. `02_model_audit.md` §3.9 shows a one-off 2026 product lever that laps takes NA 2027 to **+2.2%** versus WS10's **+6.0%** — 3.8pp of NA, ~1.1pp of total, ~$170M of FY27 revenue. MOSAIC adjudicates this with data rather than judgement: a level shift shows up in the market panel as a one-time step in `s_{m,q}` (stays per listing) that decays, while a recurring lever shows up as a sustained slope. Fifteen months of monthly market-level review flow can distinguish those two shapes; a 20-observation quarterly aggregate cannot.

**(d) FY27 revenue vs Street $15.73–15.76bn.** MOSAIC does not print revenue; it prints the two inputs. Pushed through the by-line build (`14_revenue_by_line.py`, hotels at 11% not the blended 13.4%) with the ADR-workbook geo-mix identity, the expected landing zone is **$15.5–15.7bn, i.e. at or modestly below Street**, versus the headline driver model's $15,842M. Two reasons, both measured rather than assumed: the geographic-mix feedback loop that `13` omits (1.13pp of ADR ≈ $175M, §3.4) and the hotel monetisation gap ($114M on FY27, compounding to $283M on FY28). **The uncomfortable, correct statement for the memo is that the team's own evidence puts FY27 below its headline number**, and the pitch is stronger for saying so — the Street already sits at the bottom of the team's range.

### 5.2 Uncertainty representation (not a Monte Carlo)

Three layers, none of which is "draw 10,000 paths from assumed distributions":

1. **Posterior.** The reconciliation layer returns a joint posterior over `{Δln n_{r,q}, δ_{r,q}}`. All aggregates (total nights, blended ADR via the mix identity, GBV) are *deterministic functions of the posterior draws*, so their intervals are coherent and the correlation structure between regions is preserved. Report the 10/50/90 of each.
2. **A data-dependent scenario tree.** Three binary nodes with probabilities **read off the model**, not assumed: (i) *fee-migration repricing* — measured from the second capture as the gap between `Δμ^{listed}` and `Δμ^{allin}` on migrating-country listings, `P(pass-through > 0)` from the repeat-sales posterior; (ii) *product-lever lap* — `P(step | shape of s_{m,q})` from the state-space; (iii) *EMEA regulation* — `P(θ^R < −1pp)` from the DiD posterior. Eight leaves, each with a probability that is a posterior quantity and a revenue consequence from the identity. That is a scenario tree with data-dependent probabilities, which is what a PM asks for and what a Monte Carlo of judgemental inputs is not.
3. **Split conformal** on the market-level nowcast, so the headline interval has distribution-free coverage even if the state-space is misspecified.

### 5.3 The mechanism by which the view differs from the Street

Four, ranked by conviction:

1. **The fee-migration listed-price artefact.** Deadlines 15 Sep (ex-EEA) and 13 Oct (EEA+CH) fall **inside 3Q26 and 4Q26**. Payout-neutral repricing is ~+14.8% on the migrating cohort's *listed* price with roughly **zero** effect on the all-in guest price, hence roughly zero on GBV and ADR. `research/notes/2026-09-07_adr-decomposition.md` §7 flags this as unmodelled anywhere. The 2026 dual-basis schema makes it measurable. Anyone — sell side, competitor, or this team's own pre-2026 series — reading Inside Airbnb listed prices will report a spurious ADR acceleration in 4Q26. MOSAIC prices the *real* pass-through residual (the workbook's +0.5pp row, bounded +0.7% / −12.3% / +3.8%) instead of the artefact.
2. **Bedroom Nights Booked.** 2Q26 introduced it at +12% against nights +10%, one observation, and the Street is mapping the 2pp wedge ~1:1 into ADR. The measured bedroom-count elasticity is **0.23** (0.2289 on 12 markets, 0.2312 on 29), so the wedge is worth **~+0.46pp**, not +2pp. MOSAIC's hedonic re-estimates this on 120 markets with capacity and bedrooms jointly, and the repeat-listing index says how much of the remainder is genuine repricing.
3. **Geographic mix is worsening and is not in the Street's ADR.** −0.5, −2.8, −1.1, −1.2, −1.6pp in 2021–25 and deteriorating as NA falls from 39.1% to 29.6% of nights. MOSAIC makes it an identity driven by the same nights forecast, so a bullish nights case automatically carries a deeper ADR drag — a constraint the Street's independent nights and ADR lines do not impose on themselves.
4. **Regulation, correctly signed and sized.** The DiD may well come in *smaller* than the Monte Carlo's EMEA −1.07% for 2027 (the supply panel's restated retention already cuts that way), which would be a *bullish* differentiator — the discipline is that the estimate is identified either way.

---

## 6. Minimal code skeleton

```python
# mosaic.py — bottom-up market panel, reconciled to disclosed bands.  ~80 lines.
# Inputs (all verified to exist):
#   RAW = .../raw_expansion/v2_2026-09-05/inside_airbnb_current/<country>/<region>/<market>/<date>/{listings,reviews}.csv.gz
#   data/processed/overnight/08_ia_dump_metrics.csv        (13 cities x 168 vintages -> survivorship)
#   data/processed/inside_airbnb_like_for_like.csv         (258 matched pairs -> repeat-sales prior, price_basis flags)
#   data/processed/cc_listing_survival.csv                 (48 crawls -> hazard prior)
#   data/processed/overnight/10_regional_panel_quarterly.csv (bands lo/hi  -> interval likelihood)
#   data/processed/overnight/02_kpi_panel_quarterly.csv    (disclosed total nights N_q -> exact constraint)
#   research/regulatory/factors.json                       (32 dated ordinances -> DiD)
import duckdb, numpy as np, pandas as pd, pymc as pm, pyfixest as pf

con = duckdb.connect()                                   # 588M calendar rows / 67.5M reviews: never load into pandas

# ---- 1. review flow at market x month, 120 markets, one vintage ------------------------------
rev = con.sql("""
  SELECT market, date_trunc('month', CAST(date AS DATE)) AS t, COUNT(*) AS R
  FROM read_csv_auto('RAW/**/reviews.csv.gz', filename=true, union_by_name=true)
  GROUP BY 1,2""").df()                                  # market parsed from filename path segments

# ---- 2. survivorship f(age): identified from 13 cities seen in up to 21 vintages --------------
stack = load_13city_review_counts_by_vintage()           # (market, t, vintage) from 08_ia_dump_metrics dump dates
stack["age"] = (stack.vintage - stack.t).dt.days // 30
surv = pf.feols("np.log(R) ~ C(age) | market^t", data=stack)   # cell FE absorb demand; age dummies ARE the curve
rev["R_star"] = rev.R / np.exp(surv.coef_at_age(rev.age))      # apply to all 120 markets; shrink toward cc_listing_survival

# ---- 3. repeat-listing hedonic price index (Case-Shiller), TWO bases -------------------------
# listed (col 47 'price') and all-in (col 50/51 'price_quote_*'); splice via 06_quote_line_items.csv
pairs = matched_listing_pairs(vintages)                  # requires the SECOND capture; before that, 13 cities only
d = pairs.assign(dlp=np.log(pairs.p_b/pairs.p_a), w=1/np.sqrt(pairs.gap_months))
mu = pf.feols("dlp ~ d_accommodates + d_bedrooms + d_rating | market^period", data=d, weights="w")

# ---- 4. regulation: staggered DiD on the 32-factor register ----------------------------------
panel = market_month_panel(rev, listings_counts, factors_json="research/regulatory/factors.json")
did = pf.feols("np.log(R_star) ~ i(rel_month, ref=-1) | market + country^t", data=panel, vcov={"CRV1":"market"})

# ---- 5. aggregate covered panel to regions, then RECONCILE ------------------------------------
cov = aggregate_to_region(rev, weights="nights_share_prior_year")   # balanced chain-link, never levels
bands = pd.read_csv("data/processed/overnight/10_regional_panel_quarterly.csv")  # {r}_nights_yoy_lo / _hi
Ntot  = pd.read_csv("data/processed/overnight/02_kpi_panel_quarterly.csv")["nights_yoy_pct"]

with pm.Model() as M:
    rho   = pm.Beta("rho", 6, 2)                              # AR(1) prior: the repo's unbeaten baseline
    sig_g = pm.HalfNormal("sig_g", 0.04); sig_d = pm.HalfNormal("sig_d", 0.01)
    sig_e = pm.HalfNormal("sig_e", 0.02)
    g  = pm.AR("g",  rho=rho, sigma=sig_g, shape=(4, NQ))     # latent regional dln n
    d  = pm.GaussianRandomWalk("delta", sigma=sig_d, shape=(4, NQ))   # coverage wedge
    pm.Normal("m_cov", mu=g - d, sigma=sig_e, observed=cov.values)             # (M1)
    pm.Censored("m_band", pm.Normal.dist(mu=g, sigma=0.005),                   # (M2) interval-censored
                lower=bands.lo.values, upper=bands.hi.values, observed=bands.mid.values)
    pm.Normal("m_agg", mu=pm.math.log((W0*pm.math.exp(g)).sum(0)),             # (M3) exact-ish aggregation
              sigma=0.001, observed=np.log1p(Ntot.values/100))
    # (M4) 10-K annual regional totals imposed the same way, one row per region-year
    idata = pm.sample(2000, tune=2000, target_accept=0.95, chains=4)

# ---- 6. emit ---------------------------------------------------------------------------------
post = summarise(idata, q=[0.1,0.5,0.9])                 # regional dln n + blended ADR = SUM_r w_r ADR_r (identity)
post.to_csv("data/processed/mosaic/regional_nights_posterior.csv")
```

---

## 7. Three-week build plan (3–4 undergraduates)

Roles: **A** = data engineering (DuckDB, 9.2 GB store), **B** = econometrics (FE/DiD/repeat-sales), **C** = Bayesian reconciliation, **D** (if four) = capture ops + regulatory calendar + memo exhibits.

**Week 1 — day level**

- **Fri 11 / Sat 12 Sep.** A: build a DuckDB catalogue over `raw_expansion/v2_2026-09-05/inside_airbnb_current/**` with market parsed from the path; validate against `inside_airbnb_current_manifest.csv` (316 rows, sha256 `verified` column). Confirm the calendar 5-column schema and the dual price basis. **Deliverable: row counts by market, one page.**
- **Sun 13 Sep. D: START THE CAPTURE — this is the highest-value irreversible action of the three weeks.** Adapt `analysis/src/inside_airbnb_supply_panel.py discover` to the 120-market list; cron a daily HEAD-poll of every market's `get-the-data` path; download on first sight. Missing a dump is unrecoverable — Inside Airbnb keeps only the latest file on the page.
- **Mon 14 Sep.** A: market × month review flow for all 120 markets (the query in §6 step 1). B: assemble the 13-city × vintage review stack from `08_ia_dump_metrics.csv` dump dates.
- **Tue 15 Sep.** B: estimate `f(age)` (survivorship); shrink toward `cc_listing_survival.csv`. **Checkpoint: does the corrected 13-city flow reproduce the known y/y in `08_ia_city_yoy.csv` better than the raw flow?** If not, stop and debug before anything else is built on it. C: read `10_regional_panel_quarterly.csv`, encode the 23 quarters × 4 regions of `lo/hi` bands.
- **Wed 16 Sep.** A: apply `f` to the 120-market flow; produce `R_star` market × month 2015–2026. B: hedonic `β` on the single 2026 vintage (cross-section: capacity, bedrooms, rating, room type, market FE) — this is the composition term and it needs no second vintage.
- **Thu 17 Sep.** C: PyMC reconciliation v1 with **bands + total-nights constraint only, no bottom-up panel**. This is the null model and it must run end-to-end today. Its posterior width is the benchmark MOSAIC has to beat.
- **Fri 18 Sep.** C: add (M1), the covered panel, with the `δ` wedge. Compare posterior widths. B: build the 32-factor treatment calendar from `factors.json` and map ordinances to markets.
- **Sat/Sun 19–20 Sep.** Buffer. First new dumps likely appearing — D verifies the capture is actually writing files.

**Week 2 — milestones**

- **M1 (Tue 22 Sep):** DiD event study on `ln A` and `ln R_star` with market + country×month FE; pre-trend plot. Replaces `REG_DRAG_PP` with an interval.
- **M2 (Wed 23 Sep):** language-flow gravity PPML; cross-border FX elasticity; rebuild of the cross-border share.
- **M3 (Thu 24 Sep):** repeat-listing index on the **13 cities** (258 pairs already in `inside_airbnb_like_for_like.csv` + the raw stack), both price bases, spliced. First identified estimate of like-for-like pricing vs sub-regional mix — i.e. the split of the +3.6pp residual.
- **M4 (Fri 25 Sep):** full reconciliation; regional posteriors for 3Q26–4Q27; blended ADR by the mix identity; hand-off CSVs to M6 (φ-kernel) and M3 (guidance).
- **M5 (Sun 27 Sep):** backtest — band-sharpening score and conformal coverage on the 13-city × 15-quarter history; comparison table vs AR(1), prior-year, band-midpoint.

**Week 3 — milestones**

- **M6 (Tue 29 Sep):** second-capture repeat-listing index across the 15 Sep deadline on whatever markets have re-dumped; the fee-artefact exhibit.
- **M7 (Wed 30 Sep):** sensitivity and the scenario tree with posterior-derived probabilities.
- **M8 (Thu 1 Oct):** two memo exhibits, one model tab, and a written statement of what is measured / assumed / unidentified.
- **Fri 2 Oct:** submit.

**What can be cut, in order:** (1) the gravity/cross-border block — interesting, not load-bearing; (2) the 120-market repeat-listing index (keep the 13-city one — it has real vintage depth); (3) the DiD (fall back to `11_regulatory_overlay.csv` as a prior band, stated as such); (4) the conformal layer. **What cannot be cut:** the daily capture (irreversible), the survivorship correction (without it every number is biased), and the reconciliation layer (without it the bottom-up panel has no discipline and repeats the overnight failure).

**What is estimable at each date — state this plainly in the memo.**

| Date | Newly available | Newly estimable |
|---|---|---|
| **2 Oct 2026** | one 120-market vintage; 13-city history; partial second vintage (fast-cycling markets) | survivorship-corrected review flow 2015–2026; cross-sectional hedonic; DiD on historical ordinances; reconciliation posterior; 13-city repeat-listing index |
| **5 Nov 2026** | second vintage for most of 120 markets, spanning the 15 Sep and 13 Oct fee deadlines | **sequential** repeat-listing index on both price bases → the fee-migration artefact, measured; first 120-market matched retention; 3Q26 print scored against the frozen card |
| **Feb 2027** | third vintage; Q4 print; FY27 guide | 6–8-month matched spans; migration fully lapped in listed prices; DiD on EU Affordable Housing Act announcement effects; FY27 guide scored |
| **May 2027** | fourth vintage | 9–11-month matched spans; supply response to the fee change identified |
| **Jun 2027** | fifth vintage | **first true market-level y/y from the 120-market store** |

**The honest constraint, stated first rather than last: no market-level y/y from the 120-market store exists before June 2027.** Everything before then is sequential and seasonally adjusted using the 13-city seasonal factors derived from 168 dumps over Dec 2022 – Aug 2026. Any proposal that claims 120-market y/y in October is lying about the data.

---

## 8. Failure modes and the hostile cross-examination

**"Your team already tested Inside Airbnb and got literally zero."** Correct — `n_flagged_r05_perm05 = 0` in both windows, and that is my argument, not yours. Zero spurious flags in 36 tests is a broken feature, not a weak signal; a real-but-underpowered signal produces false positives. The three defects are named and fixable (trailing-12-month stock instead of monthly flow; 13 cities on a growing set; no survivorship correction), and the *flow* feature that was tested, `ia_reviews_l30d_matched_yoy → nights_yoy`, did beat naive at **0.813×** in both windows.

**"Reviews are not stays."** Right. That is why `ρ` is calibrated by the disclosed totals rather than assumed, why the model uses review *growth* as a measurement of a latent state rather than as a level, and why the `δ_r` wedge exists and is allowed to drift. If review propensity shifts — Airbnb changes the review prompt, say — `δ` absorbs it and the posterior widens. That is a feature of a state-space model and a bug in a regression.

**"120 markets is still a small slice of a 220-country platform."** It is, and the model never uses the bottom-up *level*. It uses covered-panel *growth* as a noisy observation, with the coverage wedge as an explicit state. The level always comes from the 10-K and the letters.

**"One vintage means no y/y — your whole price index is a promise."** For 107 of 120 markets, yes, until the second capture. That is why the capture starts on day 3 and why the 13-city index (258 matched pairs, Dec 2022 – Aug 2026, price-basis flags already computed) is the deliverable that does not depend on it. I state the dependency rather than hide it.

**"Case–Shiller on Airbnb listings is asking prices, not transactions."** True and important: listed prices are asks, not realised ADR, and the 2026 calendars carry **no price column** so realised ADR is unobtainable. Two mitigations: the all-in quote basis (`price_quote_total_price`) is the guest-facing price actually offered for a dated stay, which is much closer to a transaction than a nightly ask; and the index is used as a *relative* series reconciled to disclosed regional ADR levels in `10_regional_adr_fx.csv`, never as a level.

**"Your DiD will be contaminated by anticipation and spillover."** Anticipation is why the event study runs from h = −6; spillover (displacement from Barcelona to Girona, NYC to Jersey City) is why the aggregation is by nights weight to the *region*, where displacement is internal and nets out, and why I would report a donut estimator excluding neighbouring markets as a robustness check.

**"n = 15 quarters. You cannot beat AR(1)."** Agreed, and I do not claim to at that grain — AR(1) is my *prior*. The estimation happens at market grain where n is 10³–10⁴; the aggregate is a constrained reconciliation whose test is interval sharpness and coverage, not RMSE against AR(1).

**"You're telling me your own model says FY27 is below the Street, and that's your pitch?"** Yes, and that is the point: the team's five internal FY27 estimates span $370M and the Street sits at the bottom of that range, essentially on top of the two best-evidenced builds. The pitch is not "our number is higher"; it is "the guide path and the Q4 nights bucket are what move the stock, the FX arithmetic is already 82% observed, and the ADR the Street is extrapolating from Bedroom Nights Booked is an elasticity error."

**Genuine residual risks I would flag unprompted:** Inside Airbnb may not re-dump some markets before 5 Nov (mitigated only by starting the poll now); the language-origin proxy is coarse and could mis-sign a cross-border call; the survivorship curve is estimated on 13 mostly-Western cities and shrunk, not measured, for APAC and LatAm; and `ρ` drift and `δ` drift are only separately identified because the annual 10-K constraints bind — if Airbnb stops disclosing the annual geographic table (it has form: cross-border, urban share and listings growth all stopped in 2023–24), the model loses its anchor.

---

## 9. Interlock

**Consumes from:**
- **M1 (structural mix):** seats and hotel volumes, so MOSAIC forecasts *home* nights and *home* ADR only and the printed Nights-and-Seats denominator is assembled downstream. Also the seats-dilution treatment convention — MOSAIC needs one stated answer to whether `a_x` is home or blended ADR (`02_model_audit.md` §3.6, worth 0.57pp ≈ $88M).
- **M6 (FX / take-rate / timing):** the booking-date and check-in-date currency indices. MOSAIC's price index is native-currency by construction (Inside Airbnb prices are local), so it is FX-clean; M6 translates. MOSAIC must **not** apply FX itself — that is how FX got into the nights weights in the current build (§3.2).
- **M3 (guidance game):** the bucket vocabulary and the historical mapping from operating state to guide language (`02_guidance_ledger.csv`, 194 statements).
- **M5 (ML signal extraction):** optional — a gradient-boosted challenger on market-month features to test whether the FE specification is leaving structure on the table. Challenger only; it never enters the identity.

**Hands to:**
- **M6:** regional home-nights posterior and regional home-ADR-ex-FX posterior, quarterly 3Q26–4Q27, as draws (so correlations survive), to be convolved with the φ kernel `Rev_q = Σ_k φ_k · fee · GBV_{q−k}`.
- **M1:** the nights weights `ω_{r,q}` that make `ADR_blended = Σ_r ω_r ADR_r` an identity, closing the 1.13pp / ~$175M geographic-mix loop.
- **M3:** `P(nights bucket)` for the Q4 26 and FY27 guides — the direct input to the guidance-policy function and to the "guide below Street" trade.
- **M2 (nowcast tracker):** the survivorship-corrected market × month review flow, refreshed monthly, as the live tracker series; plus the capture pipeline itself, which is the tracker's data feed.
- **All lenses:** the DiD regulatory event-study path, replacing `REG_DRAG_PP` and retiring `reg_mult = 1.67`.

**The one thing MOSAIC must never be allowed to do:** re-add a "party size" driver on top of unit-size mix. `analysis/src/adr/13_party_size_adr.py` shows the composition-implied party index moves *against* capacity (β = −0.36), and the repo has already re-based the pricing row twice to avoid exactly this double count. In MOSAIC both live inside the single hedonic `β`, and the shift-share is taken on fitted coefficients — which is the only construction under which they cannot be counted twice.
