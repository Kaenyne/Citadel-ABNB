> Research survey by an autonomous Opus subagent on 21 Sep 2026 (overnight ADR session), read-only against the repo at HEAD 2a77a36; archived verbatim as provenance for docs/pitch-model-v2/lines/adr_v1_design.md. Model output, not a team decision.

# C — ex-FX ADR mechanism inventory

Repo `/Users/theomachado/Citadel-ABNB`, branch `theo/pitch-model-v2`. Read-only survey, 2026-09-21.
Purpose: every quarterly series and measured term the repo already holds for a mechanism-led,
identity-based decomposition of the disclosed constant-currency (ex-FX) ADR y/y, so the ADR line can
be built the way the nights line is — each component sourced, the like-for-like price residual the
one unobserved line, its causal drivers carried as cross-checks.

Already in hand (referenced, not reprinted here):
`data/processed/q3nowcast/H/adr_history_components.csv` (14 rows, 1Q23–2Q26, 22 cols — the residual
history), `data/processed/adrv3/K/K4_residual_nowcast.csv` (26 rows, 13 scenarios × quarter) and
`data/processed/adrv3/K/K4_fee_lap_schedule.csv` (48 rows: variant × quarter, `migrated_nights_share_pct`,
`yoy_change_pp`, `fee_contribution_central_pp`, `fee_contribution_high_pp`).

---

## 0. The identity as the repo implements it

`H1_adr_card.py` (`analysis/src/q3nowcast/H1_adr_card.py`, 429 lines) is the only place the full
decomposition is assembled. The identity:

```
adr_yoy_reported_pp = fx_effect_pp + adr_exfx_yoy_pp                       (identity_check_pp ≈ 0)
adr_exfx_yoy_pp     = geo_mix_pp + unit_size_pp + los_mix_pp
                    + new_business_pp + interaction_pp + residual_pricing_pp
```
i.e. `residual_pricing_pp = adr_exfx_yoy_pp − components_sum_pp`. The residual is defined as a
remainder, so it absorbs every measurement error in the other five terms *and* the regional
reconstruction gap. That is the reason the blended residual rule never pays the 0.39 pp gap that the
L regional route does (§5).

Card v3's 3Q26 print of the same identity, from `data/processed/adrv3/P/P1_card_v3_terms.csv`
(48 rows = quarter × variant × term, cols `quarter, variant, term, lo_pp, point_pp, hi_pp, in_point,
source, label`), variants `v3_without_K` / `v3_with_K`:

| term | lo | point | hi | source column says | label |
|---|---|---|---|---|---|
| like_for_like_pricing_residual | 2.398 | **4.849** | 4.849 | H residual history; v3 `last_q` rule = 2Q26 value; band = K4 scenario table (mean reversion 2023–25 mean → last_q) | assumed rule; **the one unobserved line** |
| geographic_mix | −1.571 | **−1.428** | −0.935 | I `I_mix_terms_3q26.csv` (E_aug regional split × 07/H method) | measured (unvalidated mapping) |
| unit_size_party | 0.530 | **0.797** | 0.998 | I `I_mix_terms_3q26.csv` (booked capacity, 119 markets, × 0.592) | measured (level term) |
| length_of_stay_mix | −0.081 | **0.056** | 0.289 | I `I_mix_terms_3q26.csv` (28+ share of blocked runs) | measured, unvalidated |
| new_business_seats | −0.750 | **−0.483** | −0.226 | H, `15_seats_dilution_quarterly` (bull/base/bear), as J3 | **assumed** |
| interaction | −0.150 | **−0.100** | −0.050 | H, `07_full_decomposition` interaction, as J3 | descriptive |
| fee_migration K line (with-K only) | 0.000 | **+0.17** | +0.93 | K2 mechanics coefficient 0.007 × Δ(y/y migrated share) | **imposed, not fitted** |

Other P files: `P1_card_v3_backtest.csv`, `P1_card_v3_backtest_paths.csv`, `P1_card_v3_pass_table.csv`,
`adr_card_v3.csv`, `P2_score_sheet_dry_run.txt`.

---

## 1. How the H decomposition computes each term

Source: `analysis/src/q3nowcast/H1_adr_card.py`. **Note the script reads from two absolute Windows
paths** (`MAIN = C:\Users\krish\citadel-abnb`, `ON2 = C:\Users\krish\citadel-abnb-overnight2`), so it
is not re-runnable as written on this machine; the inputs it names do exist in this repo under the
same relative paths.

### Inputs (all under `data/processed/adr/` unless noted)

| H term | input file | key columns | what H does |
|---|---|---|---|
| history / FX | `adr/02b_adr_history_extended.csv` | `quarter, nights_m, gbv_busd, adr_usd, adr_yoy_reported_pct, fx_pts_adr_final, adr_yoy_exfx_final, basis` | renamed straight through |
| `geo_mix_pp` | `adr/04_regional_quarterly_wide.csv` | `adr_{r}_usd_anchored`, `adr_yoy_exfx_{r}_pct`, `nights_share_{r}_pct`, `basis_adr_na` | see below |
| `unit_size_pp` | `adr/13_party_size_adr_quarterly.csv` (region=`global`) | `cap_yoy_pct` → `booked_capacity_yoy_pct`, `size_term_pp` | taken as-is |
| `los_mix_pp` | `adr/14b_los_adr_term.csv` (scope=`global_quarterly_yoy`) | `period, los_mix_pp, tier` | taken as-is |
| `new_business_pp` | `adr/15_seats_dilution_annual.csv` (case_business=`base`) | `year, dilution_drag_pp` | **annual, spread uniformly across the 4 quarters of that year** |
| `interaction_pp` | `adr/07_full_decomposition.csv` | `year, interaction_pp` | **annual, mapped to every quarter of that year** |

### geo_mix_pp — the "07/H method"
Regions `na, emea, latam, apac`. For quarter *q* with prior-year quarter *p*:
- `a0[r]` = year-ago **anchored regional ADR level** (`adr_{r}_usd_anchored` at *p*)
- `g[r]`  = disclosed regional **ex-FX** y/y at *q*
- `s1[r]`, `s0[r]` = current and year-ago **nights shares**

```
base   = Σ s0·a0
within = Σ s0·a0·(1+g/100) / base − 1          # within-region ex-FX
total  = Σ s1·a0·(1+g/100) / Σ s0·a0 − 1       # blended reconstruction
geo_mix_pp = 100·(total − within)
```
So it is **year-ago regional ADR levels grown at the disclosed regional ex-FX rates, reweighted on
current vs year-ago nights shares** — a pure share-shift term at constant-currency regional prices.
H also writes `within_region_exfx_pp`, `blended_exfx_reconstructed_pp` and
`geo_recon_gap_pp = blended_exfx_reconstructed_pp − adr_exfx_yoy_pp`.

### unit_size_pp — booked capacity × 0.592, and where 0.399 / 0.140 come from
Built in `analysis/src/adr/13_party_size_adr.py`. Chain, quoted from its docstring:

> the hedonic on 1.4m quote-basis listings gives `d ln(price) = 0.399 d ln(capacity) + 0.140 d bedrooms`,
> and in the 29-market size panel bedrooms move **1.27** per unit of log capacity (nights-weighted), so
> `eps = 0.399 + 0.140 × 1.27 = 0.58` (listed basis: `0.332 + 0.178 × 1.27 = 0.56`)
> `size term (pp) = 100 × eps × d ln(booked capacity)`

- **0.399** = capacity elasticity (coefficient on log `accommodates`), quote basis.
- **0.140** = coefficient on `bedrooms_f` holding capacity fixed, quote basis (elsewhere written
  0.1402 / 0.3991).
- Both come from `data/processed/overnight/06_wtp_hedonic_coefs.csv` (`price_basis`, `term`, `coef`),
  a **cross-sectional ASKING-price** hedonic — `analysis/src/adr/05_size_mix.py` line ~796 flags that
  caveat explicitly.
- **0.592** is the *I-workstream* refresh of the same formula with a bedrooms-per-log-capacity ratio of
  **1.374** rather than 1.27: `I_mix_terms_3q26.csv` basis text reads "× 0.592 (hedonic 0.399 + 0.140 × 1.374)".
  So 0.58 (H/13) and 0.592 (I) are the same construction at two different panel ratios.
- Booked capacity itself = capacity of the listing behind each review, from
  `data/processed/abnb_party_size_reviews_quarterly.csv`, 123 markets, **fixed 2019 market weights**
  so Inside Airbnb adding cities cannot masquerade as a trend. A review ≈ one booking.

Cross-references: `analysis/src/adr/06_measured_price.py` lines 444–457 prices the same bound with
`0.1402·beds_per_night·bed_growth + 0.399·ln(1+bed_growth)`.

### los_mix_pp — tiers A / B / C
Built in `analysis/src/adr/14b_los_bucket_shares.py`. Three nights buckets (<7, 7–27, 28+), shares
`s_b`, bucket means `m_b`, ALOS identity `1/ALOS = s1/m1 + s2/m2 + s3/m3`, `Σs=1`.

- **Tier A — DISCLOSED** (1Q21–2Q23 quarterly; annual 2021, 2022). Both the 28+ nights share and the
  7+ nights share were disclosed, so the three-bucket split is fully determined:
  `s1 = 1 − s7plus`, `s2 = s7plus − s28`, `s3 = s28`. No bucket mean needed for the shares. The ALOS
  identity is then run *backwards* to solve the short-bucket mean `m1 = s1/(1/ALOS − s2/m2 − s3/m3)`,
  giving 2.43 (2021) and 2.50 (2022) — stable to 0.07 nights; **calibrated m1 = mean of those**.
- **Tier B — SOLVED** (3Q23, 4Q23, 1Q24; annual 2023). `s28` disclosed, 7+ not. With
  `R = 1/ALOS − s3/m3`, `S = 1 − s3`: `s1 = (R − S/m2)/(1/m1 − 1/m2)`, `s2 = S − s1`. Feasibility needs
  `m1 ≤ S/R ≤ m2`.
- **Tier C — ALOS-ONLY CARRY** (2Q24–4Q25, and 2026 only if an ALOS is supplied). No stay-length
  disclosure at all after 1Q24. One extra assumption: `phi = s2/(s1+s2)` held at its last solved value;
  with `A = (1−phi)/m1 + phi/m2`, `B = 1/m3`, `s3 = (A − 1/ALOS)/(A − B)`. Validated on 1Q24 only
  (returns 17.4% vs disclosed 17%) — a **single-point test**; these rows carry `basis="alos_only"`.
- Disclosure coverage: 28+ share quarterly 1Q21–1Q24 then discontinued; 7+ share 1Q21–2Q23 then
  discontinued; ALOS annual only 2020–2025 (global 4.1, 4.1, 4.1, 3.9, 3.8, 3.7); one regional 28+
  figure ever (NA 23% in 3Q24), used as an out-of-sample test.
- Supporting files: `14a_los_bucket_price_ratios.csv`, `14a_los_discount_by_listing_summary.csv`,
  `14b_los_bucket_shares.csv`, `14b_los_disclosures.csv`, `14b_los_adr_term_sensitivity.csv`,
  `14c_los_runs_panel.csv`, `14c_calendar_manifest.csv`, `03_los_elasticity.csv`.

### new_business_pp — `15_seats_dilution_quarterly.csv`
Built in `analysis/src/adr/15_seats_dilution.py`. Since the 2Q25 letter the KPI denominator is
"Nights **and Seats** Booked", so ADR = GBV ÷ (home nights + hotel nights + experiences seats +
services seats). Exact unit-mix arithmetic:
```
dilution ratio_t = reported ADR / homes-only ADR = [1 + Σ s_i (ρ_i − 1)] / [1 − Σ s_i]
drag_t (pp)      = (ratio_t / ratio_{t−1} − 1) × 100
```
**Airbnb discloses none of the volumes — this is a scenario build, not a measurement** (the script
says so). Assumptions: take rates experiences 0.20 / services 0.15 / hotels 0.11; ticket per seat
experiences $75 (grid 50/75/100), services $120 (grid 80/120/180); hotel ADR FY25 $140; hotel nights
FY25 18.7m (3.5% of FY25 nights, inherited from `data/processed/overnight/11_new_business_scenarios.csv`);
home-nights growth FY26–28 bear/base/bull 6/8/10%. Note the case inversion: **the bull *business*
case is the bear *ADR* case**; both labels are carried (`case_business`, `case_adr`).

`data/processed/adr/15_seats_dilution_quarterly.csv` — 18 rows, 9 cols
(`case_business, case_adr, quarter, dilution_drag_pp, drag_hotels_pp, drag_seats_pp, share_seats,
share_hotels, seasonal_share_of_year`), quarters **3Q26–4Q27**:

| case_business/case_adr | 3Q26 | 4Q26 | 1Q27–4Q27 | share_seats | share_hotels |
|---|---|---|---|---|---|
| bear / bull | −0.2262 | −0.2262 | −0.2013 | 0.0155→0.0183 | 0.0394→0.0428 |
| base / base | −0.4826 | −0.4826 | −0.5651 | 0.0194→0.0283 | 0.0432→0.0510 |
| bull / bear | −0.7503 | −0.7503 | (−0.9 area) | 0.0235 | — |

Seasonality is nights seasonality (`seasonal_share_of_year` 0.2510 in Q3, 0.2250 in Q4, 0.2695 Q1,
0.2545 Q2). Annual companion `15_seats_dilution_annual.csv` (FY24–FY28) is what H actually uses for
history (base case, spread uniformly across the year). Sensitivity grid in
`15_seats_dilution_sensitivity.csv`. Note `research/notes/2026-09-09_seats-dilution.md`.

### interaction_pp
`data/processed/adr/07_full_decomposition.csv`, column `interaction_pp`, **annual only, to 2025**,
mapped to each quarter of its year. Card v3 carries −0.10 with a ±0.05 band and labels it
"descriptive".

### 2026 fills (important caveat, flagged in the file itself)
`14b` stops at 4Q25 (no 2026 stay-length disclosure, no 2026 ALOS) and `07` is annual to 2025. H fills
**1Q26 and 2Q26** with `los = +0.30` and `interaction = −0.10`, marked in the output column
`term_fill_2026`. Card v3 instead uses J3's H fills for 2026 (new business −0.48, interaction −0.10),
which is why the card's ex-FX (3.69) sits 0.30 below the rule's harness-convention value (3.99).

### H's other four outputs

**`data/processed/q3nowcast/H/adr_exfx_backtest.csv`** — 9 rows (2Q24–2Q26), 11 cols. Walk-forward of
the *component build* (every term a trailing-4q mean; new-business and interaction the prior calendar
year's annual value) against three benchmarks:

| quarter | actual ex-FX | component build | naive last q | prior-year q | AR(1) |
|---|---|---|---|---|---|
| 2Q24 | 3.0 | 1.26 | 2.0 | 2.0 | 2.08 |
| 3Q24 | 2.0 | 1.53 | 3.0 | 0.5 | 2.76 |
| 4Q24 | 2.0 | 1.92 | 2.0 | 0.5 | 2.08 |
| 1Q25 | 1.0 | 2.25 | 2.0 | 2.0 | 2.08 |
| 2Q25 | 1.0 | 2.04 | 1.0 | 3.0 | 1.39 |
| 3Q25 | 2.0 | 1.59 | 1.0 | 2.0 | 1.39 |
| 4Q25 | 3.0 | 1.63 | 2.0 | 2.0 | 2.08 |
| 1Q26 | 4.0 | 1.75 | 3.0 | 1.0 | 2.76 |
| 2Q26 | 4.0 | 2.57 | 4.0 | 1.0 | 3.45 |

RMSE pp: **component_build 1.292, naive_last_q 0.816, prior_year_q 1.810, ar1 0.804.**
**Ratio vs naive: component build 1.583 — the H component build LOSES to naive by 58%.** AR(1) 0.985.
The build is badly biased low in every acceleration (−1.4 to −2.25 pp in 1Q26/2Q26). This is the
single most important negative in the H workstream and it is the reason v3 abandoned the component
build for a residual *rule*.

**`data/processed/q3nowcast/H/adr_forecast_card.csv`** — 24 rows = 2 quarters × 4 routes × 3 FX
estimators. Routes: `a_component_build`, `b_h1_h2_transition` (disclosed 1H26 ex-FX +4.0 plus the
2023–25 H1→H2 transition, mean −0.5 for Q3 / −0.2 for Q4, n=3), `c_naive_last_disclosed` (+4.0, band =
the naive backtest RMSE), `headline_mean_of_routes`. At the midpoint FX estimator:

| quarter | route | FX pp | ex-FX pp | reported pp | ADR $ | central lo–hi $ | GBV $bn |
|---|---|---|---|---|---|---|---|
| 3Q26 | a component build | −0.43 | 3.36 | 2.93 | 176.31 | 174.31–178.31 | 25.88 |
| 3Q26 | b H1→H2 | −0.43 | 3.50 | 3.07 | 176.55 | 173.98–179.12 | 25.92 |
| 3Q26 | c naive | −0.43 | 4.00 | 3.57 | 177.41 | 176.01–178.80 | 26.04 |
| 3Q26 | **headline** | −0.43 | 3.62 | **3.19** | **176.76** | 173.98–179.12 | 25.95 |
| 4Q26 | a | +0.15 | 3.47 | 3.62 | 173.58 | 171.23–175.93 | 23.03 |
| 4Q26 | b | +0.15 | 3.80 | 3.95 | 174.14 | 171.12–177.82 | 23.11 |
| 4Q26 | c | +0.15 | 4.00 | 4.16 | 174.47 | 173.10–175.84 | 23.15 |
| 4Q26 | **headline** | +0.15 | 3.76 | **3.91** | **174.06** | 171.12–177.82 | 23.10 |

Bases: 3Q25 ADR $171.29, 4Q25 $167.51; nights 146.8m / 132.7m (comparison inputs only).
Central band = RSS of term half-ranges; wide band adds the full FX estimator spread.

**`data/processed/q3nowcast/H/adr_sensitivities.csv`** — 18 rows (9 terms × 2 quarters).
Per 1 pp of ADR: $1.71 of ADR and $259m GBV / $46m revenue in 3Q26; $1.68 and $231m / $31m in 4Q26
(same-quarter-prior-year take rates 17.88% and 13.62%). Variance contributions:

| 3Q26 | range pp | var % | | 4Q26 | range pp | var % |
|---|---|---|---|---|---|---|
| like_for_like_pricing | 1.52 | **31.3** | | fee_migration_increment | 1.92 | **35.2** |
| fx_estimator_choice | 1.38 | 25.8 | | fx_estimator_choice | 1.63 | 25.1 |
| fee_migration_increment | 1.15 | 18.3 | | like_for_like_pricing | 1.52 | 22.1 |
| unit_size_party | 0.98 | 13.0 | | unit_size_party | 0.98 | 9.2 |
| geographic_mix | 0.60 | 4.9 | | geographic_mix | 0.63 | 3.7 |
| new_business_seats | 0.52 | 3.7 | | new_business_seats | 0.52 | 2.6 |
| length_of_stay_mix | 0.45 | 2.9 | | length_of_stay_mix | 0.45 | 2.0 |
| interaction | 0.10 | 0.1 | | interaction | 0.10 | 0.1 |
| h1h2_vs_component_route_gap | 0.14 | n/a | | h1h2 gap | 0.33 | n/a |

**`data/processed/q3nowcast/H/adr_consensus_implied.csv`** — 4 rows. There is **no published ADR
consensus**; this backs one out of the Zacks revenue consensus at the same-quarter-prior-year take rate:

| quarter | vendor | cons. rev $m | take | nights basis | nights m | implied GBV $m | implied ADR $ | implied ADR y/y pp |
|---|---|---|---|---|---|---|---|---|
| 3Q26 | Zacks | 4740 | 0.1788 | team baseline | 146.8 | 26,510 | 180.59 | +5.43 |
| 3Q26 | Zacks | 4740 | 0.1788 | guide LDD 11% | 148.3 | 26,510 | 178.76 | +4.36 |
| 4Q26 | Zacks | 3200 | 0.1362 | team baseline | 132.7 | 23,495 | 177.05 | +5.70 |
| 4Q26 | Zacks | 3200 | 0.1362 | guide LDD 11% | 135.3 | 23,495 | 173.64 | +3.66 |

(Compare the real ADR consensus in §9: Bloomberg MODL 3Q26 $177.06, 4Q26 $171.33 — i.e. the
revenue-implied ADR runs $1.5–5.7 above the actual ADR consensus, because it forces the take rate.)

---

## 2. K — fee-migration mechanics

Note: `research/notes/adrv3/K_residual-decomposition-fee-migration.md` (31 KB).
Scripts: `analysis/src/adrv3/K2_expected_effect.py`, `K3_fit_and_score.py`, `K4_residual_nowcast.py`.

### Migrated-cohort share path and dates (`K1_migrated_cohort_share.csv`)
480 rows = quarter × region × basis × variant. `region ∈ {na, emea, latam, apac, blended}` (note:
**`blended`, not `global`**), `basis ∈ {listings, nights}`, `variant ∈ {central, low_migrant, high_migrant}`.
16 quarters, 1Q23–4Q26. Cols include `pre_existing_single_fee_share, migrated_tranche1_share,
migrated_tranche2_share, migrated_split_to_single_share, total_single_fee_share,
migrated_share_yoy_change, pre_existing_fee_step_in_yoy_window, step_label, label`.

**blended / central / nights** (the regressor basis):

| quarter | pre-existing | tranche 1 | tranche 2 | total single-fee | y/y Δ migrated (pp) |
|---|---|---|---|---|---|
| 1Q23–2Q25 | 0.154–0.163 | 0 | 0 | 0.154–0.163 | 0.0 |
| 3Q25 | 0.1545 | 0.0021 | 0 | 0.1566 | +0.21 |
| 4Q25 | 0.1584 | 0.1246 | 0 | 0.2830 | **+12.46** |
| 1Q26 | 0.1612 | 0.1660 | 0 | 0.3272 | **+16.60** |
| 2Q26 | 0.1617 | 0.1839 | 0.0312 | 0.3767 | **+21.51** |
| 3Q26 | 0.1545 | 0.2104 | 0.2517 | 0.6165 | **+46.00** |
| 4Q26 | 0.1257 | 0.2216 | 0.6687 | **1.0000** | **+74.97** |

(listings basis is the same path scaled: 4Q25 +9.58, 1Q26 +12.77, 2Q26 +17.26, 3Q26 +41.19, 4Q26 +74.33.
Nights basis multiplies the PMS cohorts by an **assumed 1.3 nights per listing**, range 1.0–1.6.)

Dates, from `step_label` (sourced dates, assumed levels):
- **25 Aug 2025** — new PMS-connected hosts default to single fee.
- **27 Oct 2025 — tranche 1** (PMS split-fee hosts); 4Q25 carries **66 of 92 days** because the fee
  applies by booking-confirmation date.
- **1 Dec 2025** — pre-existing cohort steps 15% → 15.5% (worth ≈ +0.1 pp blended at payout-neutral;
  inside the y/y from 4Q25 to 3Q26, **laps in 4Q26**).
- **7 May 2026 call** — "over a quarter" of listings (sourced level, D041). NA tranche-1 share (0.32 of
  NA listings) is **calibrated** so the blended total hits 0.26 in 1Q26.
- **22 Jun 2026** — UK-resident hosts transition; tranche 2 begins.
- **6 Aug 2026 call** — "about half" (sourced level, D047).
- **15 Sep 2026** — non-EEA deadline (inside 3Q26). **13 Oct 2026** — EEA/CH deadline (inside 4Q26).
  Complete by year-end. Quarter path within tranche 2 is **assumed** (monthly end-of-month ramp).
- Alternative paths: low-migrant (pre-existing 0.18; migrants 5.1, 6.7, 9.9, 29.2, 71.7 pp y/y across
  4Q25–4Q26), high-migrant (pre-existing 0.06; 23.4, 31.3, 41.8, 69.1, 76.6 pp). All three read "over a
  quarter" at the May call.
- `K1_assumptions.csv` — 18 rows (`parameter, central, low, high, label, source`). Pre-existing
  single-fee listing share by region: NA 0.03 (0.01–0.05), EMEA 0.20 (0.10–0.28), LatAm 0.08 (0.04–0.12),
  APAC 0.15 (0.08–0.22). Tranche-1 migrants: NA 0.30 (0.22–0.36, "assumed, calibrated"), EMEA 0.02,
  LatAm 0.10.

### The payout-neutral reprice arithmetic (`K2_expected_effect.csv`, 20 rows)
Cols: `cohort, guest_fee_assumption, guest_fee_pct_of_subtotal, case, listed_price_index,
guest_paid_old, cohort_adr_effect_pct, residual_pp_per_pp_of_yoy_cohort_share, label, recorded_at`.
Cohort "split → single 15.5%", guest fee 13.9 / 14.0 / 14.2% of subtotal (low/central/high):

| case | listed price index | guest paid old | cohort ADR effect % | residual pp per pp of y/y share |
|---|---|---|---|---|
| no reprice (listed unchanged) | 100.000 | 114.0 | **−12.28** | −0.1228 |
| half pass-through | 107.396 | 114.0 | −5.79 | −0.0579 |
| **payout neutral (+14.8% listed)** | 114.793 | 114.0 | **+0.696** | **+0.0070** |
| full over-reprice (+18.34%, host-forum advice) | 118.340 | 114.0 | +3.807 | +0.0381 |

So the payout-neutral reprice moves the migrated cohort's ADR by **+0.70% central (+0.78% at the low
fee, i.e. the 0.5–0.8% range)** and the full over-reprice by +3.8%.

### The pre-statement (`K2_expected_effect_prestated.csv`, 10 rows, recorded 2026-09-11 21:56:17, i.e. **before fitting**)
- Expected sign: **positive**.
- Expected coefficient central: **0.007** pp of residual per pp of y/y migrated nights share.
- Plausible range: **0.000 to 0.038**.
- "Outside the mechanics": above 0.05 or below −0.02.
- Implied 1H26 residual contribution, central: **+0.12 pp (1Q26), +0.15 pp (2Q26)**; at full
  over-reprice **+0.63 / +0.82**.
- Observed 1H26 step over the 2023–25 mean residual (2.40): **+1.98 pp (1Q26), +2.45 pp (2Q26)**.
- **Share of the step the fee reprice can explain: about 5% central, about 30% at full over-reprice.**

### Fitted 0.114 vs mechanics 0.007 (`K3_residual_fit.csv`, 24 rows)
Cols include `variant, basis, spec, n, coef_pp_per_pp_share, se, t, r2, rmse_pp, aic,
expected_central, expected_range, ratio_to_expected_central, ratio_to_expected_high, within_mechanics,
ci95_low, ci95_high, share_obs_nonzero`.

| variant/basis | spec | n | coef | se | t | R² | RMSE | × central | × top of range | within mechanics |
|---|---|---|---|---|---|---|---|---|---|---|
| central / nights | levels, with constant | 14 | 0.1210 | 0.0283 | 4.28 | 0.605 | 0.697 | 17.3× | 3.18× | **False** |
| central / nights | **levels, no constant, baseline = 2023–25 mean** | 14 | **0.1141** | 0.0245 | **4.66** | 0.626 | 0.705 | **16.3×** | 3.00× | **False** |
| central / nights | changes, with constant | 13 | 0.0885 | 0.0735 | 1.20 | 0.116 | 0.844 | 12.6× | 2.33× | False |
| central / listings | levels, with constant | 14 | 0.1536 | 0.0359 | 4.28 | 0.604 | 0.697 | 21.9× | 4.04× | False |

**Only 4 of the 14 observations have a non-zero share** (`share_obs_nonzero = 4`). The fitted 0.114 is
**16× the mechanics central and 3× the top of the pre-stated range**. The coefficient scales inversely
with the assumed cohort size (0.06 on the largest migrant path, 0.26 on the smallest), so the note
states the conclusion as a *ratio to the mechanics* rather than on the coefficient — on every path it
is at least 1.6× the top of the range.

**The confound (`K3_alternatives.csv`, 15 rows).** Correlations of the central share with:
2026 dummy **0.885**, RNPL nights-share path **0.974**, linear trend **0.717**.

| model | n | k | R² | RMSE | coef | t |
|---|---|---|---|---|---|---|
| constant only (2023–26 mean 2.715) | 14 | 1 | 0.857 | 1.108 | — | 8.84 |
| **cohort share d4 (central, nights)** | 14 | 2 | 0.605 | 0.697 | 0.121 | 4.28 |
| 2026 dummy | 14 | 2 | 0.490 | 0.791 | 2.217 | 3.40 |
| 4Q25-onward dummy | 14 | 2 | 0.565 | 0.731 | 2.03 | 3.9 |
| RNPL share alone (note §4) | 14 | — | 0.608 | 0.693 | — | — |

Put cohort share and RNPL share in together and **neither is distinguishable from zero (t 0.4 and 0.5)**.
AR(1) alone: rho 0.75, R² 0.41; add the share and R² → 0.70, share keeps its size (0.111, t 3.1) while
rho collapses to 0.19 → **a level shift dated to the migration window, not a continuation of drift**.
Geographic terms do nothing: `geo_mix_pp` R² 0.001, H's reconciliation gap 0.10, NA nights-share change
0.08, NA-minus-ex-NA ex-FX ADR 0.15.

### Scoring (`K3_k_criterion.csv` 22 rows, `K3_pass_table.csv` 176 rows, `K3_primary_rule_margin.csv` 30 rows)
Primary K rule = `last_q + 0.007 × (Δ4share_t − Δ4share_{t−1})`, **coefficient fixed at the K2 central
value and never fitted**.

| model | v3 prereg | checks | beats last_q ratio on all 4 | beats last_q jackknife on all 4 | K criterion met |
|---|---|---|---|---|---|
| last_q | PASS | 4 | False | False | False |
| persistence | FAIL | 2 | False | False | False |
| mean_pre_migration | FAIL | 0 | — | — | False |
| **K_mech_central__central** | **PASS** | **4** | **True** | **True** | **True** |
| K_mech_high__central | PASS | 4 | True | False | True |
| K_level_mech__central | FAIL | 0 | False | False | False |

`last_q` baseline in `K3_pass_table.csv` (target `t2_reported_usd_yoy`):
eur 1Q24–2Q26 ratio **0.9163** (jk 0.871–0.969), eur 2Q24–2Q26 **0.9054** (jk 0.826–**0.9891**),
baskets **0.8764** (0.786–0.918) and **0.8714** (0.746–0.924); midpoint 0.8935 / 0.8817.
Target 1 (`t1_exfx_integer_fair`): **0.9847** and **1.0801** (jk to 1.1832, 0 of 9 below 1) — i.e. on the
letter's whole-point ex-FX figure the rule is **indistinguishable from naive and fails on the second
window**.
`K3_primary_rule_margin.csv`: the K line changes the error in only **4 quarters** (3Q25 +0.0015,
4Q25 +0.0858, 1Q26 +0.0290, 2Q26 +0.0343 pp) — a sign-test p of 0.0625. The margin over `last_q` is
**0.003 to 0.007 of ratio**. K's own note calls it "a nudge rather than evidence".

### K4 scenario definitions in words (`K4_residual_nowcast.csv`, 26 rows, 13 scenarios)
Scenario labels verbatim: `cohort model, fitted (central, b 0.114)`, `cohort model, fitted
(low_migrant, b 0.262)`, `cohort model, fitted (high_migrant, b 0.060)`, `cohort mechanics, central
(last_q + 0.007 × change in y/y share)`, `cohort mechanics, high (last_q + 0.038 × change in y/y share)`,
`lap only, residual steps`, `lap only, disclosed bundle ADR contribution`, `lap + tranche 2, central`,
`lap + tranche 2, high`, `persistence (v2 rule)`, `last_q (v3 rule)`, `mean reversion`, `AR(1) on the residual`.

In words:
- **lap only, residual steps** — treat *every* residual change since 2Q25 as a permanent level step
  dated to the products that launched in that quarter, and drop it from the y/y at its anniversary.
  3Q26 **3.9** (the 3Q25 US-RNPL step of 0.92 falls out), 4Q26 **3.06** (the 4Q25 step of 0.88 also falls out).
- **lap only, disclosed bundle** — same, but use management's 4Q25 GBV-minus-nights gap (≈1 pp bundle
  contribution) instead of the solved step. 4Q26 **3.85**.
- **lap + tranche 2, central / high** — lap-only plus the fee mechanics applied **only** to the cohort
  beyond what the 2Q26 residual already carries (avoids double counting): 3Q26 **4.10 / 4.86**,
  4Q26 **3.43 / 5.09**.
- **cohort mechanics, central** — the K rule, `last_q + 0.007 × Δ`: 3Q26 **5.02**, 4Q26 **5.22** (chained).
- **cohort model, fitted** — the reductio: at b 0.114 the 3Q26 residual is **7.6**, which is the argument
  that the 1H26 step is not the reprice. **Do not use the fitted coefficient anywhere** (the note's own
  instruction, repeated in the synthesis).
- **persistence** 4.6, **last_q (v3 rule)** 4.85, **mean reversion** 2.40 (the 2023–25 mean).
- 4Q26 is therefore reported as a **3.1 to 5.2 scenario band**, not a point. The harness has never
  scored a lap quarter, so it cannot rank these.

**When it laps — the key K finding.** The fee reprice does **not** lap in 4Q26, it **peaks** there. The
y/y migrated share runs +12.5 (4Q25), +16.6 (1Q26), +21.5 (2Q26), +46.0 (3Q26), +75.0 (4Q26), then
+70.8 (1Q27), +65.9 (2Q27), +41.2 (3Q27), **zero (4Q27)**. Contribution to the y/y residual rises from
+0.15 pp (2Q26) to +0.32 (3Q26) and +0.52 (4Q26) at the central coefficient; +0.82 → +1.75 → +2.85 at
the top. What *does* lap in 4Q26 is the bundle's ~1 pp 4Q25 contribution.

---

## 3. I — the measured mix terms

Directory `data/processed/adrq3/I/`; note `research/notes/adrq3/I_adr-mix-terms-3q26.md`;
scripts `analysis/src/adrq3/I3_geo_mix.py`, `I4_backtests.py`.

### `I1_party_size_quarterly.csv` — 85 rows, 14 cols, 2022Q3–2026Q3, 5 regions × 17 quarters
Cols: `q, region, n_markets, reviews, accommodates_mean, party_size_composition, headcount_mean,
accommodates_ge5, entire_share, mention_any, accommodates_mean_yoy_pct,
party_size_composition_yoy_pct, headcount_mean_yoy_pct, size_term_pp`.

**global (123 markets) — booked capacity y/y and the size term:**

| q | reviews | accommodates_mean | capacity y/y % | party-size comp y/y % | size_term_pp |
|---|---|---|---|---|---|
| 2022Q3 | 2,316,953 | 3.864 | — | — | — |
| 2022Q4 | 1,878,346 | 3.836 | — | — | — |
| 2023Q1 | 1,845,036 | 3.807 | — | — | — |
| 2023Q2 | 2,627,659 | 3.846 | — | — | — |
| 2023Q3 | 2,963,744 | 3.880 | 0.417 | 1.550 | 0.247 |
| 2023Q4 | 2,458,876 | 3.851 | 0.394 | 1.737 | 0.233 |
| 2024Q1 | 2,356,255 | 3.868 | 1.596 | 1.663 | 0.944 |
| 2024Q2 | 3,234,949 | 3.898 | 1.349 | 0.606 | 0.798 |
| 2024Q3 | 3,630,254 | 3.941 | 1.548 | 0.628 | 0.916 |
| 2024Q4 | 3,074,893 | 3.898 | 1.220 | 0.677 | 0.722 |
| 2025Q1 | 2,877,499 | 3.913 | 1.149 | 0.756 | 0.680 |
| 2025Q2 | 3,978,058 | 3.948 | 1.268 | 1.025 | 0.750 |
| 2025Q3 | 4,413,818 | 3.991 | 1.275 | 0.530 | 0.755 |
| 2025Q4 | 3,907,115 | 3.952 | 1.368 | 0.997 | 0.809 |
| 2026Q1 | 3,718,738 | 3.977 | 1.616 | 0.336 | 0.957 |
| 2026Q2 | 4,983,335 | 4.002 | 1.381 | 0.440 | 0.817 |
| 2026Q3 | 3,073,507 | 4.115 | **3.066** | 1.997 | **1.814** |

⚠ **2026Q3 is a partial quarter** (3.07m reviews vs 4.98m in 2026Q2) and its +3.07% is a
partial-quarter artifact. The window-matched construction used by the card is in
`I1_party_size_windows.csv` and gives **+1.346%** for 3Q26-to-date (2026-07-01..2026-08-16 vs the same
window 364 d earlier, 119 markets, 2,051,515 reviews) → term **+0.797 pp** (band 0.530–0.998). Use the
windows file, not the quarterly file, for 3Q26. Comparison columns in `I_mix_terms_3q26.csv`:
2Q26 +1.465% → 0.867 pp; 3Q25-to-date +1.362% → 0.806; 3Q25-full +1.330% → 0.787.
Other file: `I1_inventory.csv`, `I1_market_windows.csv`.

### `I2_los_term.csv` — 60 rows, 23 cols
Cols: `year, kind, window, weighting, region, n_markets, los_mix_pp, share_lt7_late, share_n7_27_late,
share_ge28_late, share_lt7_old, share_n7_27_old, share_ge28_old, d_share_lt7_pp, d_share_n7_27_pp,
d_share_ge28_pp, mean_run_late, mean_run_old, n_runs_late, n_runs_old, los_mix_p25, los_mix_p75, los_mix_sd`.
This is the **calendar-blocked-runs** route (a different construction from H/14b's disclosure route):
`kind ∈ {jun, ...}`, `window ∈ {calendar_q3, lead_matched}`, `weighting ∈ {occupancy_weighted, unweighted}`,
regions EMEA / NA / `market_dispersion`, **only 2 markets per region** and only 4 in dispersion. Example
2025 jun / calendar_q3 / unweighted: EMEA +0.265, NA −0.947, market_dispersion +0.165 (p25 −0.210,
p75 +0.435, sd 0.528). The card's 3Q26 LOS term is **+0.056 pp (band −0.081 to +0.289)**.
Companions: `I2_los_market_windows.csv`, `I2_los_pairs.csv`.

### `I3_geo_mix_history.csv` — 10 rows (1Q24–2Q26), 13 cols (already reviewed; noted here for completeness)
Cols: `quarter, H_geo_mix_pp, rebuilt_from_disclosed_shares_pp, yoy_vmatch_w_reviews_pp,
yoy_vmatch_w_reviews_g0_pp, yoy_vmatch_w_equal_pp, yoy_vmatch_w_equal_g0_pp, yoy_all_w_reviews_pp,
yoy_all_w_reviews_g0_pp, yoy_all_w_equal_pp, yoy_all_w_equal_g0_pp, adr_exfx_yoy_pp, letter_buckets_pp`.
`rebuilt_from_disclosed_shares_pp` reproduces `H_geo_mix_pp` exactly. Companions:
`I3_geo_mix_3q26.csv`, `I3_geo_mix_backtest.csv`.

### `I4_backtest_scoreboard.csv` — 16 rows, 19 cols. **How each term did vs naive.**
Cols: `term, feature, target, n, r, perm_p, knowable_before_print, wf_start, wf_n, wf_rmse,
wf_rmse_naive, wf_rmse_prior, wf_rmse_ar1, wf_ratio_vs_naive, wf_ratio_vs_prior, wf_ratio_vs_ar1,
sign_acc, rmse_vs_H_pp, mean_diff_pp`.

| term | feature | target | n | r | perm p | wf n | **ratio vs naive** | vs AR1 | sign acc | RMSE vs H |
|---|---|---|---|---|---|---|---|---|---|---|
| unit_size | unit size term (13, global) lead 0 | ex-FX ADR y/y | 20 | −0.170 | 0.454 | 10 | **4.168** | 4.019 | 0.500 | — |
| unit_size | lead 1 | ex-FX ADR y/y | 19 | 0.169 | 0.510 | 9 | **5.471** | 5.284 | 0.556 | — |
| unit_size | unit size term | H residual pricing | 14 | 0.461 | 0.137 | 6 | **1.839** | 1.136 | 0.333 | — |
| los_mix | LOS mix (H/14b, disclosure-based) | ex-FX ADR y/y | 12 | −0.125 | 0.694 | 8 | **0.877** | 0.917 | 0.500 | — |
| geo_mix | yoy_vmatch_w_reviews | H geo_mix | 10 | 0.425 | 0.210 | 6 | 1.592 | 1.565 | 0.833 | 0.692 |
| geo_mix | yoy_vmatch_w_reviews | ex-FX ADR y/y | 10 | 0.680 | 0.042 | 6 | 1.338 | 1.055 | 0.167 | — |
| geo_mix | yoy_vmatch_w_equal | H geo_mix | 10 | 0.408 | 0.247 | 6 | 1.587 | 1.560 | 0.833 | 0.420 |
| geo_mix | yoy_vmatch_w_equal | ex-FX ADR y/y | 10 | 0.765 | 0.010 | 6 | 1.097 | 0.865 | 0.167 | — |
| geo_mix | yoy_all_w_reviews | H geo_mix | 10 | 0.429 | 0.211 | 6 | 1.686 | 1.657 | 0.833 | 0.597 |
| geo_mix | yoy_all_w_reviews | ex-FX ADR y/y | 10 | 0.777 | 0.011 | 6 | 1.153 | 0.909 | 0.167 | — |
| geo_mix | yoy_all_w_equal | H geo_mix | 10 | 0.441 | 0.215 | 6 | 1.572 | 1.545 | 0.667 | 0.408 |
| geo_mix | yoy_all_w_equal | ex-FX ADR y/y | 10 | 0.777 | 0.005 | 6 | 1.103 | 0.870 | 0.500 | — |
| **geo_mix** | **letter_buckets_pp** | **H geo_mix** | **7** | **0.994** | **0.002** | **3** | **0.221** | **0.226** | **1.000** | **0.078** |
| geo_mix | letter_buckets_pp | ex-FX ADR y/y | 7 | 0.891 | 0.006 | 3 | 1.021 | 0.734 | 0.333 | — |
| geo_mix | H geo_mix_pp (disclosed shares) | ex-FX ADR y/y | 10 | 0.725 | 0.020 | 6 | 1.199 | 0.945 | 0.333 | — |
| three_terms | geo + size + LOS (H columns) | ex-FX ADR y/y | 14 | 0.524 | 0.052 | 6 | 1.382 | 1.029 | 0.333 | — |

**Reading.** Only two features beat naive walk-forward: `letter_buckets_pp` as a *proxy for H's own
geo_mix* (ratio **0.221**, r 0.994, n only 7, wf n only 3 — this is a mapping check, not a forecast of
ADR), and the LOS mix term against ex-FX ADR y/y (**0.877**, n 12, wf n 8, but r is −0.125 with perm
p 0.694, so the ratio is not backed by any in-sample relation). **Every other term loses to naive**,
and the unit-size term loses catastrophically (4.2× and 5.5× naive) — it is a *level* term, not a
timing signal, and `I_mix_terms_3q26.csv` labels it exactly so: "measured; level term, not validated as
a timing signal (r −0.17 vs ex-FX ADR, walk-forward loses to naive)". The three measured terms taken
together lose at 1.382.
`I4_party_size_series_check.csv` is the companion series check.

### `I_mix_terms_3q26.csv` — 12 rows, 11 cols
Cols: `term, quarter, 3Q26_to_date_value, unit, adr_contribution_pp, point_pp, lo, hi, basis,
evidence_status, source_file`. This is the file card v3 (`P1_card_v3.py`) reads for the 3Q26 mix terms.

---

## 4. M — new-listing premium

Note `research/notes/adrv3/M_new-listing-price-premium.md` (32 KB). Scripts
`analysis/src/adrv3/M1_dump_census.py` … `M6_term_3q26.py`. Verdict: **FAIL** (RMSE lower on 2 of 4).

### Premium series (`M2_new_listing_premium.csv` 637 rows, 24 cols; `M2_premium_summary_by_period.csv` 34 rows)
Hedonic premium in **log points**, new listings vs incumbents, after room-type / capacity / bedroom
controls. Two bases are kept strictly separate (listed-nightly 2023–25 vs quote-per-night 2026).
GLOBAL rows:

| period | variant | n quarters | n markets | hedonic mean | min | max | l30d-weighted mean | n new | n old |
|---|---|---|---|---|---|---|---|---|---|
| listed 2023 (Rome only) | all_rooms | 5 | 2 | **+8.55** | 5.87 | 12.87 | 0.19 | 46,569 | 115,614 |
| listed 2023 (Rome only) | entire_home | 5 | 2 | +8.96 | 6.77 | 13.33 | −0.25 | 38,014 | 87,885 |
| listed 2024 | all_rooms | 4 | 11 | **−6.84** | −8.97 | −5.14 | −6.55 | 134,164 | 242,989 |
| listed 2024 | entire_home | 4 | 11 | −6.38 | −8.50 | −5.15 | −6.90 | 119,355 | 203,816 |
| **listed 2025 (1Q25–3Q25)** | all_rooms | 3 | **28** | **−5.58** | −5.77 | −5.29 | −4.02 | **261,480** | 625,300 |
| listed 2025 | entire_home | 3 | 28 | −5.48 | −6.03 | −5.03 | −4.30 | 221,687 | 516,371 |
| **quote 2026 (1Q26–3Q26)** | all_rooms | 3 | **33** | **−1.89** | −2.89 | −1.11 | −1.37 | **605,809** | 1,650,496 |
| quote 2026 | entire_home | 3 | 33 | −2.19 | −3.13 | −1.42 | −2.04 | 493,359 | 1,312,159 |

(This is the synthesis's "−5.6 log points listed 2025, 28 markets, 261k new listings; −1.9 quote 2026,
33 markets, 606k".) Standard errors 0.2–0.6 log points per region-quarter. Region splits in
`M2_new_listing_premium_region.csv` and `M4_premium_by_region_quarter.csv`.

### New-listing share of stays (`M3_new_listing_share.csv` 1,842 rows, 18 cols; `M3_new_listing_share_region.csv`)
Share of reviews from listings under 12 months old, 123 markets, three constructions
(`within_vintage_deep`, `mixed_lag`, `vintage_matched`). Level: **31–32% of all reviews in 2023 and
1H24; 29% in 2025 and 2026.** y/y change:
- +0.5 to +4.2 pp through 2Q24 (within-vintage deep lag, **biased upward by the attrition wedge**)
- −0.2 to −1.0 pp in 3Q24–2Q25 (mixed lag)
- **−2.3, −1.7, −0.9, −1.5 pp in 3Q25–2Q26** (vintage-matched)
- 3Q26 to date (July) **−1.8 pp**: EMEA −3.8, APAC −2.0, NA −0.7, LatAm +0.6.
Attrition wedge: **−1.8 to −2.3 pp per year of dump lag** (`M3_attrition_wedge.csv`), so the 2023–1H24
rise is overstated by 1–2 points; the direction since mid-2024 is robust. Lag-zero cross-check from
`number_of_reviews_l30d` agrees market by market (Paris 52→28%, Rome 36→21, Austin 36→29, Tokyo 45→39,
London 43→40; Sydney 37→41 and Mexico City 30→36 the other way). Also `M3_listings_dump_share.csv`.

### The term (`M4_term_quarterly.csv`, 490 rows, 12 cols; `M6_term_3q26.csv`, 7 rows)
`term_pp = premium_logpts × Δshare_pp`, 8 variants × 5 regions × 15 quarters (1Q23–3Q26).
**primary / GLOBAL_NW:**

| quarter | premium basis | premium source | Δshare pp | term_pp |
|---|---|---|---|---|
| 1Q23 | listed_nightly | carried_back;measured | 4.184 | 0.143 |
| 2Q23 | listed_nightly | carried_back;measured | 3.380 | 0.189 |
| 3Q23 | listed_nightly | carried_back;measured | 2.514 | 0.159 |
| 4Q23 | listed_nightly | carried_back;measured | 1.744 | 0.196 |
| 1Q24 | listed_nightly | carried_back;measured | 1.063 | 0.075 |
| 2Q24 | listed_nightly | carried_back;measured | 0.528 | 0.034 |
| 3Q24 | listed_nightly | carried_back;measured | −0.209 | −0.005 |
| 4Q24 | listed_nightly | measured | −0.381 | −0.019 |
| 1Q25 | listed_nightly | measured | −0.828 | 0.003 |
| 2Q25 | listed_nightly | measured | −0.973 | 0.056 |
| 3Q25 | listed_nightly | measured | −2.343 | 0.164 |
| 4Q25 | none | **carried** | −1.733 | 0.073 |
| 1Q26 | quote_per_night | measured | −0.855 | 0.031 |
| 2Q26 | quote_per_night | measured | −1.537 | 0.065 |
| 3Q26 | quote_per_night | measured | −1.806 | 0.054 |

Range **−0.02 to +0.20 pp per quarter**. 3Q26 **+0.054** (synthesis rounds to +0.05, band +0.02 to +0.07).
`M6_term_3q26.csv` by region (3Q26 to date, quote basis, vintage-matched): APAC premium +0.285
(se 0.195), Δshare −2.047 → term −0.0058; EMEA −4.692 (se 0.211), Δshare −3.772 → **+0.177**;
LatAm −1.996 (se 0.183); GLOBAL_NW Δshare −1.806 → **+0.054** (120 markets).

### Scoring (`M5_criterion.csv` 8 rows, `M5_scores.csv` 136 rows, `M5_paths.csv`)
Criterion: term history ≥ 8 quarters (met: **14**) *and* RMSE lower on both windows.

| variant | t2 RMSE lower on all 4 | count | eur 1Q24 (base) | eur 2Q24 (base) | baskets 1Q24 (base) | baskets 2Q24 (base) | M criterion |
|---|---|---|---|---|---|---|---|
| entire_home_premium | False | 2 | 1.113 (1.099) | 0.927 (0.935) | 0.833 (0.831) | 0.766 (0.783) | **False** |
| equal_weighted_share | False | 3 | 1.108 (1.099) | 0.926 (0.935) | 0.830 (0.831) | 0.767 (0.783) | **False** |
| full_scope_premium | False | 2 | 1.120 (1.099) | 0.933 (0.935) | 0.838 (0.831) | 0.769 (0.783) | **False** |

So the term **raises** RMSE under the eur estimator on the first window in every variant. The one
variant that clears the bar (stay-weighted premium, 0.003–0.009 pp of effect) is noise and was not the
pre-declared specification.

### The −10 coefficient supply lead
From the note (line 126): the walk-forward-coefficient sensitivity (baseline + β × term change, β fitted
on prior quarters) is **worse** than baseline for the primary term (ratios 1.05–1.22, **β −9 to −12**)
and **better** for the wedge-corrected term (ratios **0.70–0.81**, **β −10 to −15**). Line 170:

> A supply-growth term is the lead this note leaves. The share change (or E's same-listing decline, or
> the listing count itself) moving opposite to the residual with a coefficient near **−10** is a
> different mechanism from composition and would need its own pre-registered test on the S harness with
> a stated sign and size before fitting.

The mechanical (composition) coefficient is **+1**. A fitted −10 is therefore *not* the composition
mechanism; the synthesis records the share–residual correlation as **−0.68**. This is the single most
promising unexplored causal driver of the residual in the repo, and it is **untested** — no
pre-registration exists for it.

---

## 5. L — the regional route

Note `research/notes/adrv3/L_regional-residual-and-proxies.md` (34 KB). Verdict: **FAIL, 0 of 4.**

### Regional ex-FX ADR as reconstructed (`L1_regional_panel.csv`, 88 rows, 14 cols)
Cols: `quarter, region, exfx_pp, reported_yoy_pp, fx_pp, nights_share_pct, adr_anchored_usd, adr_usd,
exfx_basis, exfx_basis_raw, reported_basis_raw, basis_flag_04, usable, size_term_pp`. 1Q21–2Q26.

| quarter | NA | EMEA | LatAm | APAC |
|---|---|---|---|---|
| 1Q23 | −1.89 | 13.59 | −2.46 | 4.44 |
| 2Q23 | −0.87 | 6.43 | −2.22 | 4.09 |
| 3Q23 | −1.16 | 6.00 | −3.73 | 4.57 |
| 4Q23 | −0.22 | 6.00 | −2.80 | 1.85 |
| 1Q24 | 2.78 | 5.02 | −4.40 | 4.03 |
| 2Q24 | 4.09 | 4.61 | −0.18 | 2.32 |
| 3Q24 | 3.33 | 4.61 | 4.72 | −1.52 |
| 4Q24 | 3.47 | 6.00 | 4.00 | 2.00 |
| 1Q25 | 3.00 | 4.00 | 2.00 | 3.00 |
| 2Q25 | 3.33 | 3.00 | 2.00 | 1.00 |
| 3Q25 | 5.05 | 4.00 | 3.00 | 3.00 |
| 4Q25 | 4.78 | 4.00 | 3.00 | 2.00 |
| 1Q26 | 6.30 | 4.00 | 3.00 | 2.00 |
| 2Q26 | 6.75 | 5.00 | 2.00 | −1.35 |

`exfx_basis` by quarter — **this is the weak point**: NA is `solved` in 9 of 10 scored quarters (only
1Q25 disclosed); LatAm and APAC are `modelled` before 4Q24 and only `disclosed` from 4Q24; EMEA has 9
disclosed of 14 (3Q23, 4Q23, 4Q24–2Q26), 5 solved with a fitted pass-through of 1.04. Whole-point
integers throughout from 4Q24.

### The 0.39 pp reconstruction gap (`L1_identity_check.csv`, 18 rows, 19 cols)
Identity reproduced to 0.000000: `disclosed blended ex-FX = within-region ex-FX + geo mix − reconstruction gap`.
The gap (regional integer rounding, the blended integer, NA's assumed pass-through, modelled LatAm and
APAC before 4Q24) has **RMSE 0.39 pp on 1Q24–2Q26, range −0.35 to +0.72, lag-1 autocorrelation 0.30**,
and is **invisible to a regional forecast**. The blended residual rule never pays it because H defines
the residual to absorb it. `L_wf_gap_lastq` (subtract last quarter's gap) helps under eur (1.168 /
1.226) and hurts under baskets (1.088 / 1.092) — noise. Note's own summary: *"0.39 pp of RMSE that the
regional route pays and the blended residual rule does not. On a series whose naive RMSE is 0.9 to
1.2 pp, that is a third to a half of the error budget before any regional signal is counted."*
Dollar weights: NA 0.540, EMEA 0.312, LatAm 0.079, APAC 0.070 (1Q22 row).

### Proxies tried (`L2_proxy_tests.csv`, 52 rows, 36 cols — 32 proxy_ols + 20 own_rule)
Cols include `region, candidate, kind, in_selection_pool, wf_n, wf_rmse_model, wf_rmse_naive,
wf_ratio_vs_naive, wf_ratio_vs_ar1, jackknife_ratio_max, proxy, transform, lag, knowable_before_print,
n, first_q, last_q, pearson_r, p, spearman_r, perm_p, p_bonferroni, beats_naive, survivor`.

**EMEA — the one survivor:**

| candidate | n | window | r | p | wf n | **ratio vs naive** | vs AR1 | jk max | survivor |
|---|---|---|---|---|---|---|---|---|---|
| **hicp_ea_accommodation \| level \| lag0** | 14 | 1Q23–2Q26 | 0.742 | 0.002 | 10 | **0.914** | 0.923 | **1.173** | **True** |
| hicp_ea_accommodation \| level \| lag1 | 14 | | 0.783 | 0.001 | 10 | 1.829 | 1.846 | 2.355 | False |
| hicp_ea_accommodation \| diff \| lag0/lag1 | 14 | | −0.497 / −0.693 | 0.071 / 0.006 | 10 | 1.948 / 1.637 | | | False |
| ine_iph_spain \| level \| lag0 / lag1 | 14 | | 0.765 / 0.572 | 0.001 / 0.032 | 10 | 1.723 / 1.476 | | | False |

EMEA on HICP is real **per region** (0.914) but its jackknife max is **1.173** (it does not survive a
drop-one), and it **does not survive aggregation**.

**NA — all 24 candidates fail, and the good in-sample fits have the wrong sign:**

| candidate | n | r | p | wf n | ratio vs naive | vs AR1 | jk max |
|---|---|---|---|---|---|---|---|
| bea_hotels_price \| level \| lag1 | 13 | **−0.915** | 0.000 | 9 | **1.207** | 0.346 | 1.478 |
| cpi_lodging_sa \| level \| lag1 | 13 | **−0.898** | 0.000 | 9 | **1.319** | 0.378 | 1.601 |
| cpi_lodging_nsa \| level \| lag1 | 13 | −0.779 | 0.002 | 9 | 1.939 | 0.555 | 2.390 |
| mar_revpar \| level \| lag0 | 13 | −0.774 | 0.002 | 9 | 1.972 | 0.565 | 2.454 |
| hlt_revpar \| level \| lag1 | 13 | −0.733 | 0.004 | 9 | 2.060 | 0.590 | 2.469 |
| cpi_hotels_motels_nsa (4 forms) | 13 | −0.21 to +0.44 | 0.13–0.74 | 9 | 3.30–3.78 | | |

So the **US lodging CPI and BEA hotel prices are strongly *negatively* correlated with NA ex-FX ADR
(r −0.78 to −0.92, in-sample)** and therefore **read the 2026 price jump as a fall**; 2Q26 alone costs
2.19 pp. Marriott and Hilton RevPAR are in the same pool (`mar_revpar`, `hlt_revpar`) and also fail.
Windows: NA proxies n 13 (2Q23–2Q26), EMEA n 14 (1Q23–2Q26).

**Data files for the proxies, with date ranges (all in this repo):**

| proxy | file | rows | date range |
|---|---|---|---|
| US lodging CPI, SA (`cpi_lodging_sa`) | `data/raw/fred/CUSR0000SEHB.csv` (`observation_date, CUSR0000SEHB`) | 344 | 1997-12-01 → 2026-07-01, monthly |
| US hotels/motels CPI (`cpi_hotels_motels_nsa`) | `data/raw/fred/CUSR0000SETG01.csv` | 451 | 1989-01-01 → 2026-07-01, monthly |
| US headline CPI (deflator) | `data/raw/fred/CPIAUCSL.csv` | 955 | 1947-01-01 → 2026-07-01, monthly |
| BEA hotel prices (`bea_hotels_price`) | `data/raw/bea/bea_pce_travel_monthly_2015_2026.csv` (`date, series, measure, value, yoy_pct, bea_line, bea_label`; series `accommodations`, BEA line 249) | 4,170 | 2015-01-01 → 2026-07-01, monthly |
| Euro-area HICP accommodation (`hicp_ea_accommodation`) | `data/processed/govdata/P/raw/eurostat_hicp_cp112_family_monthly.csv`; also `data/processed/govdata/R/raw/eurostat_hicp_cp11203_monthly.csv` | — | monthly; Eurostat `prc_hicp_minr` |
| Spain INE IPH (`ine_iph_spain`) | (via the govdata workstream) | — | monthly |
| EUR/USD, broad dollar (FX estimators) | `data/raw/fred/DEXUSEU.csv` (7,220 rows, 1999-01-04 → 2026-09-04), `data/raw/fred/DTWEXBGS.csv` (5,395 rows, 2006-01-02 → 2026-09-04) | | daily |

3Q26 readings already captured in `data/processed/adrq3/J/J2_proxy_readings_3q26.csv`: **HICP July 4.6**
(Eurostat prc_hicp_minr), INE July 5.91, CPI lodging SA July–Aug 3.54, BEA hotels July 3.55.

### Selection and scoring (`L2_regional_selection.csv` 48 rows, `L3_scores.csv` 96 rows, `L3_pass.csv` 56 rows, `L3_walk_forward_paths.csv`, `L3_error_attribution.csv`, `L3_paired_jackknife.csv`, `L3_regional_paths.csv`, `L3_regional_scores.csv`)
Region-by-region pick chosen strictly before each quarter. NA uses `last_q` until 1Q25, then switches
to `cpi_lodging_sa|level|lag1` from 2Q25 — which is exactly when the NA proxies start inverting.

`L3_pass.csv`, primary `L_wf` on target `t2_reported_usd_yoy`:

| fx | window | n | RMSE | naive RMSE | ratio | jk min | jk max | last_q ratio | verdict |
|---|---|---|---|---|---|---|---|---|---|
| eur | 1Q24–2Q26 | 10 | 1.436 | 1.199 | **1.198** | 0.888 | 1.324 | 0.916 | FAIL |
| eur | 2Q24–2Q26 | 9 | 1.367 | 1.033 | **1.324** | 0.885 | 1.440 | 0.905 | FAIL |
| baskets | 1Q24–2Q26 | 10 | 0.980 | 0.949 | **1.033** | 0.794 | 1.137 | 0.876 | FAIL |
| baskets | 2Q24–2Q26 | 9 | — | — | **1.078** | — | — | 0.871 | FAIL |

0 of 4. Regional `last_q` carry 2 of 4; own-rules walk-forward 2 of 4 (0.922 / 0.936 eur, jk max 1.02).

### Nowcast (`L4_regional_nowcast.csv` 32 rows, `L4_aggregate_nowcast.csv` 12 rows)

| variant | region | quarter | pick | proxy input | forecast ex-FX pp | band | last disclosed | weight share % | weight ADR $ |
|---|---|---|---|---|---|---|---|---|---|
| L_wf | na | 3Q26 | bea_hotels_price\|level\|lag1 | 4.96 | **0.152** | 1.152 | 6.751 (solved) | 31.39 | 249.34 |
| L_wf | na | 4Q26 | same | 3.55 | **1.063** | 1.152 | 6.751 | 30.06 | 247.21 |
| L_wf | emea | 3Q26 | hicp_ea_accommodation\|level\|lag0 | 4.60 | **4.628** | 0.917 | 5.000 (disclosed) | 36.78 | 162.07 |
| L_wf | emea | 4Q26 | same (3Q26 reading held, assumed) | 4.60 | 4.628 | 0.917 | 5.000 | 37.8 | — |
| L_wf | latam | 3Q26/4Q26 | — | — | 2.0 | 0.965 | — | 9.6/9.8 | — |
| L_wf | apac | 3Q26/4Q26 | — | — | 1.412 / 1.015 | 1.693 | — | 10.0/8.4 | — |

Aggregate `L_wf`: 3Q26 within-region **+2.011**, geo_mix −1.428 (measured, I3 3Q26 split × 07/H method),
**blended ex-FX +0.582** (central band 0.816, −0.234 to +1.399; wide 1.813, −1.230 to +2.395);
4Q26 within-region +2.497, geo_mix −1.428 (assumed, carried), **blended +1.069** (band 0.811,
0.258–1.880). `gap_rmse_pp` 0.388, `geo_half_range_pp` 0.318. Central band = RSS(weighted regional OOS
RMSE, gap RMSE, geo half-range); wide = arithmetic sum.
**The synthesis says explicitly: do not use L's primary model's numbers (+0.6 / +1.1 ex-FX) for
anything.** The usable memo lines are the regional `last_q` carry (ex-FX +3.4 in 3Q26, +3.5 in 4Q26)
and the EMEA HICP read of **4.6**.

---

## 6. Hotel ADR / lodging comparators

### 6a. The L3 package — `analysis/src/forecast_methods/l3_adr_hotel_v1/`
`run.py` (25,334 B), `README.md`, `test_audit.py`. `AS_OF = 2026-09-13`; ADR snapshot 2026-09-11;
hotel observations through July 2026. 29 inputs SHA-256 hashed before and after.
README states outright: **"Hotels never enter ABNB ADR as measured pricing."**

**It contains exactly TWO hotel price series. There is no STR, CoStar, Marriott or Hilton series
anywhere in this package** (verified by grep over the source dir, both output dirs and both L3 docs):

| series (output column) | source file | freq | raw range | used range |
|---|---|---|---|---|
| `cpi_lodging_yoy_pct` — BLS CPI "Lodging away from home", SA | `data/raw/fred/CUSR0000SEHB.csv` (344 rows) | monthly | 1997-12-01 → 2026-07-01 | 2023-01 → 2026-07, 42 of 44 non-missing (2025-10 missing at source = shutdown gap) |
| `bea_hotels_price_yoy_pct` — BEA PCE price index, hotels & motels, 2017=100 | `data/raw/bea/bea_pce_travel_monthly_2015_2026.csv` filtered `series=="hotels_motels" & measure=="price_index_2017eq100"` (139 of 4,170 rows) | monthly | 2015-01-01 → 2026-07-01 | 2023-01 → 2026-07, 43 non-missing |

Reconciliation target `data/processed/hotel_price_monitor_monthly.csv` (43 rows, 2023-01→2026-07,
from `analysis/src/hotel_price_monitor.py`), tolerance 0.051 pp, actual max deltas 0.04926 / 0.04946.
⚠ That monitor's `abnb_adr_yoy_letter_pct` / `abnb_adr_exfx_yoy_pct` columns are a **hardcoded dict
manually transcribed from shareholder letters** (`ADR_EXFX = {"4Q25": (6,3), "1Q26": (9,4), "2Q26": (5,4)}`,
line 20); the CPI/BEA columns are computed.

Also ingested (supply, not price): 5 files from `data/processed/hotel_13_market_panel/`.

**`data/processed/forecast_methods/l3_adr_hotel_v1/` and `..._rebuild/` are byte-identical**
(`diff -rq` clean, 18 files each) — the rebuild is a determinism replication, not new content.

**`hotel_quarterly_comparators.csv`** — 15 rows, 7 cols, 2023Q1–2026Q3:

| quarter | CPI mths | CPI y/y % | BEA mths | BEA y/y % | ABNB ex-FX pp | ABNB reported pp |
|---|---|---|---|---|---|---|
| 2023Q1 | 3 | 7.114 | 3 | 7.938 | 3.0 | 0.214 |
| 2023Q2 | 3 | 3.794 | 3 | 4.000 | 2.0 | 1.386 |
| 2023Q3 | 3 | 5.568 | 3 | 5.959 | 0.5 | 3.158 |
| 2023Q4 | 3 | 0.613 | 3 | 0.214 | 0.5 | 2.565 |
| 2024Q1 | 3 | −0.581 | 3 | −0.878 | 2.0 | 2.642 |
| 2024Q2 | 3 | −1.168 | 3 | −1.711 | 3.0 | 2.120 |
| 2024Q3 | 3 | −0.912 | 3 | −1.436 | 2.0 | 1.400 |
| 2024Q4 | 3 | 1.809 | 3 | 1.759 | 2.0 | 0.893 |
| 2025Q1 | 3 | 0.491 | 3 | −0.048 | 1.0 | −0.891 |
| 2025Q2 | 3 | −1.559 | 3 | −2.585 | 1.0 | 2.920 |
| 2025Q3 | 3 | −1.922 | 3 | −3.136 | 2.0 | 4.675 |
| 2025Q4 | **2** | **NaN** | 3 | −3.184 | 3.0 | 5.932 |
| 2026Q1 | 3 | −0.148 | 3 | −2.190 | 4.0 | 9.035 |
| 2026Q2 | 3 | 4.722 | 3 | 4.960 | 4.0 | 5.301 |
| 2026Q3 | **1** | **NaN** | **1** | **NaN** | — | — |

`complete_quarters()` only emits a value when all 3 months are observed, hence the two blanks.
Other outputs: `hotel_monthly_comparators.csv` (43 rows), `hotel_coverage.json`,
`adr_scores.csv` (16 rows), `adr_independent_scores.csv` (16), `summary.json`,
`source_manifest.csv` (29 rows, all `audit_information_date = 2026-09-13`),
`adr_historical_identity.csv` (14 rows, 1Q23–2Q26 — reproduces H's residual identity),
`adr_card_identity.csv` (126 rows, all passed), `checks.csv` (14, all True),
`l4_adr_hotel_inputs.csv` (86 rows, 2026Q1–2026Q4 — **only 6 of 86 are hotel rows, all `descriptive`**),
`hotel_associations.csv` (24), `hotel_market_coverage.csv` (13), `adr_identification_audit.csv` (9),
`adr_interval_sensitivity.csv` (4), `adr_score_reproduction.csv` (16), `j3_reproduction.csv` (32).

`hotel_coverage.json`: markets 13; markets_with_page_captures 4; page observations 113; property
clusters 111; accepted registered room matches 26; registered rooms 1,060;
**markets_with_absolute_airbnb_hotel_nights 0; markets_with_absolute_airbnb_hotel_revenue 0;
markets_with_current_verified_independent_rooms 0**; capacity_total null.

### 6b. Pre-registration — `docs/revenue-forecast-strategy/05_backtests/L3_ADR_HOTEL_PREREG.md`
Registered **2026-09-13**, owner `adr_hotel`, branch `codex/lane3-full`, "Saved before executing the audit."
Hotel item (§5): rebuild monthly CPI-lodging and BEA hotel-price y/y from raw public series; match the
existing monitor within **0.051 pp**; aggregate **only complete three-month quarters**; then on
ADR-A (2024Q1–2026Q2), ADR-B (2024Q2–2026Q2) and full history 2023Q1–2026Q2 report **Pearson and
Spearman** against Airbnb **ex-FX** and **reported** ADR, with paired n, drop-one Pearson range, and
change-in-growth association.
**Pass/fail criterion: there is none.** Verbatim: *"This is a robustness/coverage diagnostic, with no
predictive promotion or causal pass line."* §6 adds that Airbnb hotel pricing, occupancy and
incremental demand "remain unidentified without outcomes." The only hard pass lines in the prereg are
for ADR itself (§2, dollar-ADR ratios and every drop-one ratio below 1 under both estimators in both
windows) and reproduction (§1, 16 P1 rows to 1e-9, 32 J3 rows to 0.001).

### 6c. Results — `docs/revenue-forecast-strategy/05_backtests/L3_ADR_HOTEL_RESULTS.md`
Dated 2026-09-13, commit `1c87628cedbc94ab8a0e8552743c94485ef353b8`, tests 12/12.
Verdict line: *"Implementation PASS; original descriptive ADR research PASS; **guide-date PIT evidence
NOT ESTABLISHED**; **hotel pricing transmission and hotel onboarding demand UNIDENTIFIED**; investment
adoption PENDING."* `summary.json` carries
`hotel_comparator_forecast_or_demand_edge: "NOT ESTABLISHED"`.

**The hotel correlations (the actual result):**

| comparator | full history r; n | ADR-A r; n | ADR-B r; n | change-in-growth r (ADR-A); n |
|---|---|---|---|---|
| US CPI lodging vs ex-FX ADR | 0.1321; 13 | 0.4745; 9 | 0.4674; 8 | 0.0095; 7 |
| BEA hotels/motels vs ex-FX ADR | 0.0106; 14 | 0.2716; 10 | 0.2733; 9 | −0.0103; 9 |
| US CPI lodging vs **reported** ADR | — | **0.0782**; 9 | — | **−0.6934**; 7 |
| BEA hotels/motels vs **reported** ADR | — | **−0.1856**; 10 | — | **−0.6042**; 9 |

Drop-one Pearson ranges on ADR-A: CPI **0.0123 to 0.6008** (Spearman 0.3162); BEA **−0.2955 to 0.4408**
(Spearman **0.0000**). All 24 specifications retained "including weak and negative results, without
choosing a winner." Illustrative divergence: 2026Q1 CPI −0.148% / BEA −2.190% against Airbnb ex-FX
**+4%**; 2026Q2 CPI +4.722% / BEA +4.960% against ex-FX **+4%**.
Hotel supply: **0 of 13 markets have actual Airbnb hotel nights, hotel revenue or verified independent
room totals; those missing values are not zeros.** No capacity sum is defensible.

The ADR ratios reported in the same document (these are **not** hotel models — hotels are not in them),
windows **ADR-A 2024Q1–2026Q2 n=10** and **ADR-B 2024Q2–2026Q2 n=9**, explicitly not the harness W1/W2:

| rule | FX | ADR-A ratio; jk max | ADR-B ratio; jk max |
|---|---|---|---|
| last-q residual + measured mix | euro | 0.916346; 0.968863 | 0.905369; 0.989084 |
| same | baskets | 0.876405; 0.918023 | 0.871375; 0.923653 |
| same | midpoint (comparison) | 0.893458; 0.944575 | 0.881744; 0.955239 |
| same + imposed K | euro | 0.911586; 0.965831 | 0.898148; 0.984108 |
| same + imposed K | baskets | 0.873500; 0.916276 | 0.867755; 0.921440 |

Both PASS 4/4; binding plain-rule jackknife margin **0.010916**. Rounded-ex-FX target
(`t1_exfx_integer_fair`): **0.984732 (n=10) / 1.080123 (n=9)**, jk max 1.080123 / 1.183216 — **fails on
ADR-B**. Ratios vs prior year 0.186–0.512, vs AR(1) 0.276–0.764. Integrity: P1 reproduction 16 rows to
2.22e-16, J3 32 rows to 8.88e-16, historical residual identity 14 rows to 8.88e-16 pp.

### 6d. Where STR / CoStar / Marriott / Hilton actually live (outside the L3 package)
**`data/processed/adrq3/J/J2_proxy_quarterly_panel.csv` — 18 rows, 10 cols, 1Q22–2Q26.** This is the
real hotel-proxy horse race. Cols: `quarter, cpi_lodging_sa, cpi_lodging_nsa, cpi_hotels_motels_nsa,
bea_hotels_price, hicp_ea_accommodation, ine_iph_spain, mar_revpar, hlt_revpar, mgmt_adr_guide`.
**Marriott and Hilton worldwide comparable constant-currency RevPAR y/y, quarterly 1Q22–2Q26:**

| quarter | MAR | HLT | cpi_lodging_sa | bea_hotels_price | hicp_ea_accom | mgmt_adr_guide |
|---|---|---|---|---|---|---|
| 1Q22 | 96.5 | 80.5 | 23.41 | 27.14 | 8.53 | — |
| 2Q22 | 70.6 | 54.3 | 16.38 | 18.71 | 14.03 | — |
| 3Q22 | 36.3 | 29.9 | 2.82 | 3.07 | 14.83 | 1.0 |
| 4Q22 | 28.8 | 24.8 | 3.93 | 4.34 | 11.40 | −1.0 |
| 1Q23 | 34.3 | 30.0 | 7.11 | 7.94 | 9.30 | −1.0 |
| 2Q23 | 13.5 | 12.1 | 3.79 | 4.00 | 9.77 | −1.0 |
| 3Q23 | 8.8 | 6.8 | 5.57 | 5.96 | 7.77 | 1.0 |
| 4Q23 | 7.2 | 5.7 | 0.61 | 0.21 | 6.83 | 0.5 |
| 1Q24 | 4.2 | 2.0 | −0.58 | −0.88 | 5.30 | 0.5 |
| 2Q24 | 4.9 | 3.5 | −1.17 | −1.71 | 5.47 | 1.0 |
| 3Q24 | 3.0 | 1.4 | −0.91 | −1.44 | 4.97 | 1.0 |
| 4Q24 | 5.0 | 3.5 | 1.81 | 1.76 | 5.07 | 1.0 |
| 1Q25 | 4.1 | 2.5 | 0.49 | −0.05 | 4.53 | −1.0 |
| 2Q25 | 1.5 | −0.5 | −1.56 | −2.59 | 3.97 | 0.0 |
| 3Q25 | 0.5 | −1.1 | −1.92 | −3.14 | 2.83 | 1.0 |
| 4Q25 | 1.9 | 0.5 | −1.93 | −3.18 | 3.33 | 1.0 |
| 1Q26 | 4.2 | 3.6 | −0.93 | −2.19 | 3.93 | 2.0 |
| 2Q26 | 3.4 | 3.9 | 4.16 | 4.96 | 4.27 | 2.0 |

(Note 2Q26 `cpi_lodging_sa` is 4.16 here vs 4.722 in L3's quarterly comparator — different month
aggregation; worth reconciling before either is quoted.)

**`data/processed/adrq3/J/proxy_tests.csv` — 164 rows.** Walk-forward from 2024Q1, wf_n 10.
**Every US hotel comparator FAILS vs naive.** Best ratios against consolidated ex-FX ADR:
`bea_hotels_price` diff lag0 **1.0326**; `cpi_lodging_sa` diff lag0 **1.0538**; `cpi_lodging_nsa` diff
lag0 **1.0603**; `hlt_revpar` best **1.1343** (level lag0, n 18, r 0.6921); `mar_revpar` best **1.1828**
(level lag0, n 18, r 0.6900). Against `residual_pricing_pp`: BEA diff lag0 **1.0261**, HLT 1.2029,
MAR 1.2178 — all above 1.
**Only 3 survivors of 164, and none is a US hotel series:** `hicp_ea_accommodation` level lag0 against
`adr_exfx_emea_pp` (ratios **0.9145** n 14 and **0.9645** n 18), and `mgmt_adr_guide` level lag0 against
`adr_reported_yoy_pp` (**0.9721**).

**STR / CoStar raw:**
- `data/processed/q3nowcast/G/str_weekly_us_3q26.csv` — 7 rows, 2026-07-01 (monthly July) → 2026-08-30;
  cols `week_start, week_end, occupancy_pct, occupancy_yoy_pct, adr_usd, adr_yoy_pct, revpar_usd,
  revpar_yoy_pct, publication_date, url, note`. **Manually transcribed** from CoStar/STR and Lodging
  Magazine press releases (per-row `url`). July 2026: ADR $171.74 (+5.7%), RevPAR $119.77 (+8.2%),
  occupancy 69.7%.
- `data/processed/forecast_methods/macro_pulls/costar_us_weekly.csv` — **header-only, 0 rows**;
  `manifest.json` records `http_status: 403`, `status: "failed"`, pulled 2026-09-13T17:24Z. Fallback is
  `analysis/src/forecast_methods/macro_pulls/public_web_extracts.csv` — 4 manually transcribed rows,
  week ended 2026-08-01, ADR $168.82 (+4.5%), RevPAR $120.45 (+7.3%).
- `data/processed/adrq3/J/J2_proxy_readings_3q26.csv` (15 rows): **`str_us_hotel_adr_july_month` 3Q26
  = 5.70%**, `str_us_hotel_adr_aug_weeks_mean` = 2.625%, flagged "yes; **no held history to test**".
  MAR/HLT 3Q26 blank ("reported 1–8 days before ABNB but not held today").

**MAR/HLT provenance (downloaded, not transcribed):** `data/processed/predictive/02_peer_sources.csv`
(256 rows; tickers BKNG/EXPE/HLT/MAR; 2020Q4–2026Q2; **46 revpar rows**, each with SEC EDGAR accession
and exhibit_url) → `analysis/src/adr/06_measured_price.py` →
`data/processed/adr/06_measured_price_quarterly.csv` (22 rows, 1Q21–2Q26, 34 cols incl.
`mar_revpar_yoy`, `hlt_revpar_yoy`, `global_revpar_yoy_pct`, `cpi_lodging_yoy_pct` n 22,
`bea_hotels_price_yoy_pct` n 22, `us_matched_item_price_yoy_pct` n 22, **`str_us_hotel_adr_yoy_pct`
n = 1** (1Q26 = 3.8), **`airdna_us_str_adr_yoy_pct` n = 3** (4Q24 3.1, 4Q25 3.3, 2Q26 4.6)).
There is **no** Marriott/Hilton/STR data in `data/raw/` (only `bea`, `fred`, `regulatory`).

⚠ `analysis/src/adrq3/J2_proxy_tests.py` reads `data/raw/external_prices/` and
`data/raw/inside_airbnb/` via the hardcoded Windows path `MAIN = r"C:\Users\krish\citadel-abnb"`;
**those directories do not exist in this repo copy**, so J2 is not re-runnable here.

---

## 7. Supply / demand balance

**`data/processed/overnight/02_kpi_panel_quarterly.csv`** — 24 rows (3Q20–2Q26), 120 cols.
The supply side is **very sparse** — this is the binding constraint on any supply-growth term:

| column | non-null of 24 | last value |
|---|---|---|
| `nights_m` | 24 | 148.3 (2Q26) |
| `nights_yoy_pct` | 20 | 10.34 (2Q26) |
| `active_listings_m` | **10** | 9.0 (4Q25) |
| `active_listings_yoy_pct` | **7** | 18.0 (3Q23) |
| `active_listings_yoy_ex_removals_pct` | **1** | 17.0 (1Q24) |
| `active_listings_ex_china_yoy_pct` | **1** | 26.0 (4Q22) |
| `removed_listings_cum_k` | **3** | 550 (3Q25) |
| `bedroom_nights_yoy_pct` | **1** | 12.0 (2Q26) |
| `na_share_of_nights_pct` | **1** | 30.0 (1Q25) |
| `active_listings_yoy_qual` | qualitative text | "active listings grew relatively in-line with the y/y…" (1Q26) |

Active listings: 6.0 (4Q21/1Q22), 6.6 (4Q22), 7.0 (2Q23/3Q23), 7.7 (4Q23), 8.0 (2Q24/3Q24/4Q24),
9.0 (4Q25) million. y/y: 15 (3Q22), 16 (4Q22), 18 (1Q23), 19 (2Q23/3Q23), 18 (4Q23), 15 (1Q24) — then
nothing but qualitative sentences ("approximately in-line with Nights and Seats", "slightly above",
"relatively in-line"). **There is no quarterly active-listings y/y series after 1Q24**, so a
nights-per-active-listing series cannot be built from disclosure past that point.

- **Nights per active listing:** not computed anywhere as a quarterly series. The only related object
  is `data/processed/beta_city_estimate.csv` / `analysis/src/beta_city_estimate.py` (city-level).
- **New-listing share (M3):** §4 above — this is the repo's *only* continuous quarterly supply-mix
  series (123 markets, 1Q23–3Q26, from review vintages), and it is a share of *stays*, not of listings.
- **Occupancy:** **there is no Airbnb occupancy series, disclosed or constructed.** The only occupancy
  objects are third-party city tax data (`data/processed/github_altdata/samples/
  sideye-boston-occupancy-tax-imputed-nights`, `.../texas-comptroller-hotel-occupancy-tax`) and the
  STR US hotel `occupancy_pct` / `occupancy_yoy_pct` columns in
  `data/processed/q3nowcast/G/str_weekly_us_3q26.csv` (7 rows, July–August 2026, US hotels only).
  `I2_los_term.csv` carries an `occupancy_weighted` weighting flag but those rows have `los_mix_pp = NaN`.

**Implication for the ADR build:** the M note's −10 supply-lead coefficient (§4) cannot currently be
tested on *disclosed* supply, because active-listings y/y stops at 1Q24. It would have to run on the
M3 new-listing share or E's same-listing review decline, both of which are Inside-Airbnb-derived.

---

## 8. RNPL-related ADR evidence, and the seats data

### 8a. The RNPL ADR premium is DERIVED, not measured
The identity used everywhere (`research/notes/2026-09-10_rnpl-conversion-framework.md` §3; coded at
`analysis/src/rnpl_balance_sheet_bridge.py` line 62):
```
p_nights = s / ( r(1−s) + s )      s = RNPL GBV share, r = RNPL / non-RNPL ADR ratio
```
`rnpl_balance_sheet_bridge.py:62` hard-codes `s=0.21; r=1.33` → "RNPL nights share … 16.7% (r=1.00:
21.0%, r=1.25: 17.7%)"; line 43 `nights = unpaid/(f(q,'adr_usd')*1.33)`.

**r does not come from an RNPL GBV-share ÷ RNPL nights-share pair. No RNPL nights share has ever been
disclosed.** r comes from the ratio of the **three-feature bundle's** GBV points to its nights points:
- **1Q26 (ledger D032, 2026-05-07 call):** "approximately three points of nights booked growth and
  approximately four points of GBV growth" → **4/3 = 1.33×**
- **4Q25 (ledger D014, 2026-02-12 call):** "over 200 basis points of growth in nights booked and
  roughly 300 basis points of growth in GBV" → **3/2 = 1.50×**

The audit downgrades both: `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` line 9 —
*"Bottom line 7 (marginal ADR 1.33x / 1.5x) — MODIFIED. 4/3 is an upper bound against prior-year ADR
(**1.22x against the 1Q26 ADR**); the 4Q25 '1.5x' rests on a '>200bp' denominator and is not supported."*

Two competing labels sit in the data files:
- `data/processed/rnpl_short_audit/rnpl_nights_module_params.csv` row 9 — "RNPL / non-RNPL ADR ratio |
  **1.33x** | **derived** | … Relabelled from ASSUMED by …2026-09-11_rnpl-balance-sheet-and-q3-bridge.md s1.7"
- `data/processed/overnight2/D/D1_rnpl_parameters.csv` row 6 — "RNPL to non-RNPL ADR ratio |
  **1.00, 1.15, 1.25** | **direction sourced, magnitude assumed** | ledger D016, D033, D045: mix shift to
  larger entire homes… **The ratio itself is undisclosed**"
- `docs/pitch-model-v2/dossiers/N2_backlog_identity.md` line 110 uses a {1.00, 1.33} grid at
  B ∈ {1.00, 1.05, 1.10} while D1's central cell uses 1.25.

**Live range: r = 1.00 / 1.15 / 1.22 / 1.25 / 1.33 / 1.50 — an ADR premium of 0% to +50%, central
+25% to +33%, with +22% the audit's tighter read.**

### 8b. The two share series
**(a) RNPL GBV share `s` — only 2 quarters disclosed** (`rnpl_nights_module_params.csv` rows 5–8):

| quarter | s | status |
|---|---|---|
| 3Q25 | 4% central (2.5–6%) | **assumed** |
| 4Q25 | 9% central (7–12%) | **assumed** |
| 1Q26 | ~20% | **measured** — 1Q26 shareholder letter, ledger D031: "roughly 20% of global GBV came from Reserve Now, Pay Later bookings" |
| 2Q26 | "over 20%", used at 21% | **measured lower bound** — 2Q26 call, ledger D043 (stockanalysis mirror; the official letter carries no share) |
| 3Q26 | 22% central (21–25) | **assumed** |
| 4Q26 | 23% central (21–27) | **assumed** |
| 1Q27–4Q27 | held at 4Q26 | **assumed** |

**(b) RNPL nights share — entirely constructed**
(`data/processed/rnpl_short_audit/rnpl_nights_module_state.csv`, 21 rows, 11 cols):

| scenario | quarter | GBV share % | nights share % | live unpaid backlog nights (mm) |
|---|---|---|---|---|
| bear | 2Q26 (cross-check) | 21.0 | 16.66 | 18.62 |
| bear | 3Q26 / 4Q26 / 1Q27–4Q27 | 25.0 / 27.0 / 27.0 | 20.04 / 21.76 / 21.76 | 22.29 / 23.10 / 26.0–28.0 |
| base | 2Q26 (cross-check) | 21.0 | 16.66 | 20.75 |
| base | 3Q26 / 4Q26 / 1Q27–4Q27 | 22.0 / 23.0 / 23.0 | 17.50 / 18.34 / 18.34 | 22.57 / 22.34 / 24.8–26.5 |
| bull | 2Q26–4Q27 | 21.0 flat | 16.66 flat | 25.10 → 27.77 |

(bear Δ 6.0 pp / lead 1.8 mo / rebook 0.00; base Δ 4.0 / 2.2 / 0.25; bull Δ 2.0 / 3.0 / 0.50.)
**⚠ Circular: 21.0 → 16.66 is exactly `s/(1.33(1−s)+s)`.** Dividing the GBV share by the nights share
here returns 1.33 by construction. **There is no independent RNPL-nights observation anywhere in the
repo, so the RNPL ADR premium cannot currently be used as a cross-check on the residual — it is an
input to itself.**

The explicit ask, in two places —
`docs/pitch-model-v2/dossiers/D4_d4_adr.md` line 229 and
`research/notes/adrv3/K_residual-decomposition-fee-migration.md` §5 item 1:
> "…the RNPL GBV share alongside the RNPL nights share for the same quarter, whose ratio is the RNPL
> ADR premium and would pin the mix leg and leave the fee leg as the remainder."

### 8c. The "larger homes" evidence
D016/D033/D045 are **statement IDs in a 60-row ledger**, not dossier files. Canonical location:
`data/processed/overnight2/D/rnpl_statement_ledger.csv` (60 rows × 22 cols: `statement_id, date,
period_referenced, event, speaker, role, theme, quote, quantity, quantity_num_low/high, unit, basis,
scope, night_weighted, official_or_mirror, quote_verified, source_key, source_file, source_url,
access_date, note`). Builder `analysis/src/overnight2/D0_rnpl_statement_ledger.py`; note
`research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md`.

**Only D016 carries the mechanism.** D016 | 2026-02-12 | 4Q25 | earnings call | Ellie Mertz (CFO) |
theme `adr_mix` | quantity "4+ bedrooms" | scope global | `night_weighted: NO` | **`official_or_mirror:
MIRROR`**:
> "Reserve Now, Pay Later saw significant adoption among eligible guests in Q4. It's also led to longer
> booking lead times and **a mix shift towards larger entire homes, especially those with four more
> bedrooms**, contributing to"

Ledger note (the analyst's own read): *"The mix shift is why RNPL ADR exceeds non-RNPL ADR, which is
why an RNPL GBV share overstates its nights share. **Direction is disclosed; the ratio is not.**"*
Source `data/raw/transcripts/web/4Q25.html`, stockanalysis.com mirror, accessed 2026-09-11.

D033 (1Q26 call) and D045 (2Q26 call) say only that RNPL "contributed to the increase in ADR" —
qualitative, no mix language. All three are **call mirrors, not official IR PDFs**. D045's note: *"2Q26
is the first print since 3Q25 with no quantified bundle growth contribution."*
`docs/pitch-model-v2/dossiers/X3_x3_bundle_sentences_provenance.md` (lines 85, 129, 173): the 2Q26 10-Q
carries "qualitative RNPL/ADR driver language only, no points", and the bundle sentences "cannot be
converted into growth points without an undisclosed RNPL-vs-non-RNPL ADR ratio".

**The attribution gap, stated in the repo's own words**
(`data/processed/rnpl_short_audit/rnpl_channel_ledger.csv`, 7 rows, channel `d` = "ADR line — RNPL
larger-home mix and the pricing residual; TWO-SIDED", lo −2.00 pp / central 0.00 / hi +1.78 pp, status
**ASSUMED**, `in_b3`: "ATTRIBUTION ONLY — zero weight"):
> "NEITHER ADR note names RNPL anywhere, while the residual stepped +1.15pp across exactly the two
> quarters management credits the bundle with ~3pts nights / ~4pts GBV. **The bedroom-count part of
> RNPL's larger-homes effect is inside the +0.63pp unit-size line; the trade-up-at-same-bedroom-count
> and lead-time-into-peak-dates parts are inside the +2.83pp remainder, UNATTRIBUTED.**"

This is the single cleanest statement of what the like-for-like residual actually contains, and it
says the H unit-size term (booked capacity from reviews) **partially** captures the RNPL mix — a
double-count risk if an RNPL mix term is ever added on top.

### 8d. `data/processed/rnpl_short_audit/` inventory
37 CSVs + `run_log.txt` + `verify_balance_sheet_output.txt`, all mtime 2026-09-18.
Scripts: `analysis/src/rnpl_short_audit/{rnpl_nights_module.py, verify_balance_sheet.py,
fy27_rnpl_channels.py, qog_cash_reality.py, qog_momentum_reversal.py}` and
`analysis/src/rnpl_balance_sheet_bridge.py`.
Quarters: forward module **3Q26–4Q27** (+2Q26 cross-check) plus FY27 rollup; balance-sheet verification
**1Q26 and 2Q26 only**; qog_momentum panels back to 2023.
ADR-relevant files: `rnpl_nights_module_state.csv` (21), `rnpl_nights_module.csv` (21),
`rnpl_nights_module_params.csv` (25), `rnpl_nights_module_cohort_matrix.csv` (36),
`rnpl_nights_module_audit_sensitivities.csv` (36), `rnpl_channel_ledger.csv` (7),
`verify_bs_unpaid_gbv_nights.csv` (48, 1Q26 and 2Q26 only),
`fy27_quarterly_phasing_rnpl_aware.csv` (8 rows, 2027Q1–2027Q4 × 2 lap cases — **the only quarterly ADR
column in the directory**: `adr_yoy_pct` = 2.617 / 1.527 / 1.229 / 2.088 for 1Q27–4Q27, identical in
both lap cases).
`verify_bs_unpaid_gbv_nights.csv` committed cell (2Q26, UF-only FX-clean, fee divisor 0.133, B 1.05):
u 19.4%, backlog GBV $26.4bn, unpaid GBV $5.13bn, **27.9mm nights at r = 1.00 vs 21.0mm at r = 1.33** —
i.e. the assumed ADR premium is exactly what turns $5.13bn into 21m rather than 28m nights.

### 8e. Cancellations and unpaid nights, as they touch ADR
- The one **audited** (non-mirror) disclosure, 2Q26 10-Q MD&A
  (`data/raw/regulatory/quantification/abnb_2026q2_10q.html`, quoted at
  `docs/rnpl-short-audit/04_balance-sheet-verification.md` line 24): *"To date, RNPL bookings … have
  experienced **higher cancellation rates** than historic bookings … the timing among GBV, revenue, and
  cash receipts may become less correlated."* That document (line 12) flags that this language is
  **absent from the 60-row ledger** — the strongest cancellation evidence is not in the structured data.
- Quantified platform rate (call mirror, hedged): D017 "approximately 1%" aggregate nominal increase;
  D018 "an average of maybe 16% cancellation rate historically going to 17%".
  `rnpl_nights_module_params.csv` row 8 labels it "sourced with an unstated unit of account — Not
  stated to be per night, per booking or per dollar, and no base period given."
- **Cancellations and ADR are carried in separate channels and nothing in the repo prices a
  cancellation → ADR (mix-of-survivors) effect.** Cancellations do hit ADR arithmetically through the
  denominator (ADR = GBV ÷ Nights-and-Seats, net of cancellations) — stated in
  `research/notes/2026-09-10_rnpl-conversion-framework.md` but **never converted into an ADR pp figure**.
- `docs/pitch-model-v2/dossiers/N2_backlog_identity.md`: 137m nights booked-not-stayed at 30 Jun 2026,
  of which 21m unpaid RNPL. Line 7: *"at an equal RNPL/non-RNPL ADR the backlog is exactly invariant to
  the unpaid share, and only lead-time lengthening B and the RNPL ADR premium r move it at all."*
  Line 116: *"RNPL bookings carry a higher ADR, so the same dollars hold fewer nights."* The term
  **fails its own validity test** — subtracting it makes reported nights *less* like measured stays
  (correlation 0.863 → 0.503) — so it is carried as a 5-Nov falsifier, not a forecast.
- `docs/pitch-model-v2/dossiers/D7_d7_take_rate.md` line 15 is the one place all three RNPL shares
  appear side by side (GBV 21%, backlog 23.1%, nights 16.7%) — and the 21/16.7 pair is again just the
  1.33× conversion.

### 8f. Seats — volumes are NOT measured
Covered in §1 above for the construction. The provenance point worth stating plainly:
- Script docstring, verbatim: *"Airbnb discloses none of the volumes, so this is a scenario build, not
  a measurement."* Code comment line 46: *"every number here is an assumption"*.
- Independent audit agrees — `docs/revenue-forecast-strategy/01_ground-truth/02_model_audit.md` line
  139: "Seats-dilution drag (−0.48 FY26, −0.57 FY27) … unit-mix arithmetic on undisclosed volumes;
  tickets $75/$120, hotel ADR $140, hotel nights 18.7M | **assumed** (structure measured, inputs assumed)".
- **FY25 hotel nights 18.7m provenance:** `analysis/src/overnight/11_competition_supply_overlays.py`
  line 395, verbatim — *"FY25: hotels 'single-digit % of nights' (Q4'25 call) → **assume 3.5%** of 533m
  nights = 18.7m nights × ~$140 hotel ADR × ~11% commission (undisclosed…)"*. So 18.7 = 3.5% × 533,
  where 3.5% is a point pick inside an unquantified "single-digit percentage".
  `research/notes/2026-09-07_hotel-absolute-disclosure-search.md` line 5 confirms **no verified absolute
  Airbnb hotel nights, hotel GBV or hotel fee revenue exists in the searched corpus**; its only hard
  bound (line 42) is hotel nights < 14.83m for 2Q26.
- Annual base-case path (`15_seats_dilution_annual.csv`, 15 rows = 3 cases × FY24–FY28, 24 cols):
  drag FY25 **−0.177**, FY26 **−0.483**, FY27 **−0.565**, FY28 **−0.617** pp;
  `dilution_ratio` 0.9882 / 0.9864 / 0.9817 / 0.9761 / 0.9701; `p_home_fy25` backed out at **$173.65**;
  `rho_hotels` 0.8062, `rho_exp` 0.4320, `rho_svc` 0.6910 held at FY25.
  FY25 hotel nights row = 18.7 exactly; FY24 = 18.7/1.30 = 14.385 (a second assumption: +30% into FY25).
  Case span FY27: bear(business)/bull(ADR) −0.201 to bull(business)/bear(ADR) −1.054.
- `15_seats_dilution_sensitivity.csv` — 81 rows (3 business cases × 3 exp tickets × 3 svc tickets ×
  3 FY24 exp-GBV bases). `drag_fy27_pp` range **−1.948 to −0.119**, median −0.565, mean −0.676.
  Base-business rows only: FY27 −0.30 to −1.01. The note's conclusion: *"The ticket assumption is the
  whole uncertainty."*
- ⚠ The quarterly file is **the annual drag repeated across all four quarters** — no quarterly
  variation. The note flags it: *"seats are probably summer-heavy (Experiences), so the uniform
  quarterly spread … understates 3Q and overstates 4Q. Not correctable without a disclosure."*

---

## 9. ADR laps, the FY27 build, and Street

### 9a. Lap dates (N memo 2 — `research/notes/adrv3/N_fx-estimator-and-q4-lap-decisions.md`)
The memo's subject is the **nights** lap, not the ADR lap, but it fixes the dates both use.
- The 4Q25 letter: *"In October, we announced new cancellation policies…"*; fee migration ran PMS hosts
  from October and most remaining single-fee hosts from December — **global, per the 3Q25 and 4Q25
  shareholder letters** (ledger D012, D013, D024, D060), not NA-only as PR #32 assumed.
- RNPL: **US from 3Q25, rest of world from 17 February 2026** (K note §4).
- Decision: **adopt Case B (WS-D global lap), 4Q26 nights +8.0 to +8.2%, point +8.1% (131.8mm)**, with
  the team's +8.9% (132.7mm) as the top of the band. The single free parameter — the ex-NA
  fee-and-cancellation share of the ex-NA bundle — is **pinned at 40–50%** by an out-of-sample check
  against the 4Q25 "over 200bps" disclosure.
- Revenue difference between the two cases: **~$21mm** ($3,115mm vs $3,137mm) at card v2's midpoint-FX
  4Q26 ADR of $173.55. "**The lap decision is a nights-growth-rate question, not a revenue-dollar
  question.**"
- `D1_prereg_thresholds.csv`: for the 4Q26 nights guide on 5 Nov, ≤7.5% supports the global lap, ≥9.5%
  weakens it, **7.6–9.4% inconclusive** — and both cases sit inside that band, so the guide alone will
  not settle it.
- **The one disclosure that settles it:** whether management repeats a quantified bundle contribution
  for 3Q26. ≤~1.5 points → Case B; ≥~2.5 points → Case A. Management gave "over 200bps nights, roughly
  300bps GBV" (4Q25, D014) and "about 3 points nights, 4 points GBV" (1Q26, D032), then **no figure for
  2Q26** (D045).
- **K's distinct point, which N does not make:** the fee reprice's ADR effect and the fee's nights
  effect run on *different clocks* — the nights lap is a 4Q25 anniversary, the ADR reprice **peaks** a
  year later (see §2).
- Files: `data/processed/adrv3/N/N1_fx_choice_card.csv`, `N1_fx_estimator_by_quarter.csv`,
  `N1_fx_estimator_window_summary.csv`, `N1_fx_estimator_reconciliation_check.csv`,
  `N2_q4_lap_cases.csv` (12 rows = 4 case variants × 3 FX estimators; 4Q26 ADR $172.20 on the eur fit,
  $174.93 on the baskets).
- FX estimator choice (N memo 1): **midpoint of the euro fit and the regional baskets.** RMSE 0.406 pp
  on 2Q22–2Q26 (euro 0.458, baskets 0.535) and 0.332 on 1Q24–2Q26 (0.455, 0.416). 3Q26 FX **−0.43 pp**
  (euro −1.12, baskets +0.26); 4Q26 **+0.15** (−0.66, +0.97). The 1.4 pp spread between the two single
  estimators is the largest controllable uncertainty on the ADR line.

### 9b. `data/processed/margin_build/06_fy27_path_v2/06_adr_build.csv`
**12 rows = 4 quarters (1Q27–4Q27) × 3 scenarios. FY27 only — there are no 3Q26/4Q26 rows and no
`adr_usd` column.** 15 cols: `quarter, scenario, residual_pp, k_line_pp, geo_mix_pp, party_size_pp,
los_pp, new_business_seats_pp, interaction_pp, adr_exfx_yoy_pct, eur_yoy_spot_held_pct, fx_eur_fit_pp,
fx_baskets_proxy_pp, fx_pts_adr, adr_reported_yoy_pct`.

| quarter | scenario | residual | k_line | geo_mix | party_size | los | seats | interaction | **ex-FX** | eur y/y spot | fx_eur_fit | fx_baskets | **fx_pts_adr** | **reported** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1Q27 | bear | 2.398 | 0.345 | −1.428 | 0.797 | 0.056 | −0.565 | −0.100 | 1.503 | −0.714 | −0.892 | 0.289 | **−2.378** | −0.875 |
| 2Q27 | bear | 2.398 | 0.311 | −1.428 | 0.797 | 0.056 | −0.565 | −0.100 | 1.469 | −0.119 | −0.623 | 0.237 | −2.267 | −0.798 |
| 3Q27 | bear | 2.398 | 0.138 | −1.428 | 0.797 | 0.056 | −0.565 | −0.100 | 1.296 | 0.647 | −0.278 | 0.347 | −1.494 | −0.198 |
| 4Q27 | bear | 2.398 | **−0.150** | −1.428 | 0.797 | 0.056 | −0.565 | −0.100 | 1.008 | 0.000 | −0.570 | 0.000 | −0.285 | 0.723 |
| 1Q27 | **base** | 4.372 | 0.345 | −1.428 | 0.797 | 0.056 | −0.565 | −0.100 | **3.478** | −0.714 | −0.892 | 0.289 | −0.301 | **3.176** |
| 2Q27 | base | 4.016 | 0.311 | −1.428 | 0.797 | 0.056 | −0.565 | −0.100 | 3.087 | −0.119 | −0.623 | 0.237 | −0.193 | 2.894 |
| 3Q27 | base | 3.750 | 0.138 | −1.428 | 0.797 | 0.056 | −0.565 | −0.100 | 2.648 | 0.647 | −0.278 | 0.347 | 0.034 | 2.682 |
| 4Q27 | base | 3.551 | **−0.150** | −1.428 | 0.797 | 0.056 | −0.565 | −0.100 | 2.161 | 0.000 | −0.570 | 0.000 | −0.285 | 1.876 |
| 1Q27 | bull | 4.849 | 0.345 | −1.428 | 0.797 | 0.056 | −0.565 | −0.100 | 3.954 | −0.714 | −0.892 | 0.289 | 1.775 | 5.730 |
| 2Q27 | bull | 4.849 | 0.311 | −1.428 | 0.797 | 0.056 | −0.565 | −0.100 | 3.920 | −0.119 | −0.623 | 0.237 | 1.881 | 5.801 |
| 3Q27 | bull | 4.849 | 0.138 | −1.428 | 0.797 | 0.056 | −0.565 | −0.100 | 3.747 | 0.647 | −0.278 | 0.347 | 1.521 | 5.268 |
| 4Q27 | bull | 4.849 | **−0.150** | −1.428 | 0.797 | 0.056 | −0.565 | −0.100 | 3.459 | 0.000 | −0.570 | 0.000 | −0.285 | 3.174 |

Notes: the **mix terms are frozen at the 3Q26 card values for all of FY27** (geo −1.428, party size
+0.797, LOS +0.056, interaction −0.100) and seats moves to the FY27 base drag −0.565. Only the
residual and the K line vary by quarter. **The K line turns negative in 4Q27 (−0.150)** — that is the
tranche-2 reprice falling out of the y/y, matching K's "does not fall out of the y/y until 4Q27".
Bull holds the residual flat at last_q 4.849; base decays 4.372 → 3.551; bear sits at the
mean-reversion value 2.398 throughout. `fx_pts_adr` differs from both single estimators (it is the
build's own FX line, not the midpoint of the two columns shown).

### 9c. Street ADR
`docs/pitch-model-v2/dossiers/V1_v1_street.md` (digger sonnet, 2026-09-18, commit e39d9e4).
**Bloomberg MODL, screenshot 12 Sep 2026 (Krish) is the ONLY source of a forward ADR consensus
anywhere** — A1 §3's exhaustive free-web check found no vendor page that carries ADR at all.

| period | object | point | low | high | unit | vintage | n |
|---|---|---|---|---|---|---|---|
| 3Q26 | **ADR** | **177.06** | **173.71** | **179.12** | usd | 2026-09-12 | **26** |
| 4Q26 | **ADR** | **171.33** | — | — | usd | 2026-09-12 | **25** |

**There is no FY26 or FY27 Street ADR row and no low/high for 4Q26.** The dossier states it directly
(lines 156–157): *"one source anywhere with a vendor-stamped forward nights and ADR — is
quarterly-only: it has no FY26 or FY27 nights or ADR row (A1 §3, exhaustive free-web check, confirms
the same absence)."* So 3Q26 and 4Q26 are the complete Street ADR set, and only 3Q26 has a range.

Companion Street rows that bear on the ADR line:
- 3Q26 nights **149.0m** per DEC-0005 (the memo prints 148.9m; the underlying 12-Sep MODL capture CSV
  records mean 149.0, low 147.0, high 151.0, n 28 — an unresolved conflict recorded in §4/§7).
  4Q26 nights **134.0m** (low 130.0, high 136.0, n 28).
- 3Q26 revenue **$4,744m** (LSEG-family, n 37); 4Q26 **$3,161m** LSEG-family vs **$3,200m** Zacks
  (n 10, flagged HIGH OUTLIER, +$40m above Yahoo/S&P).
- Implied take rates (DEC-0018): 3Q26 **17.98%** (4744 ÷ (149.0 × 177.06)), cross-checked against
  MODL's own published 18.0%; 4Q26 **13.77%** vs MODL's 13.76%.

**Card v3 against Street (midpoint FX, with K):** 3Q26 **$177.17** vs Street $177.06 — essentially on
top of consensus (+0.06%); 4Q26 **$174.57** vs Street $171.33 — **+1.9% above**. The variant view on
ADR is therefore a 4Q26 view, not a 3Q26 view. The H card's headline ($176.76 / $174.06) and card v2's
($176.47 / $173.55) sit in the same place. Note also that the mean-reversion downside (3Q26 ≈ $173.0)
is **$4.1 below Street**, well outside Street's own 3Q26 low of $173.71 only marginally.

---

## 10. Kill list items touching ADR
`docs/revenue-forecast-strategy/AGENT_BRIEF.md` §6, "Kill list — never quote these as ours".
Items that touch the ADR line:

1. **"The −3.4pp Q4 FX step (double subtraction)"** — an FX line, i.e. the ADR identity's other half.
2. **"'82% of Q4 FX already determined'"** — same.
3. **"'+4.05% fee uplift' as measured"** — directly the fee-migration / K term. K2's own arithmetic
   puts the payout-neutral reprice at **+0.70% on the migrated cohort** and the full over-reprice at
   **+3.81%**; 4.05% as *measured* is killed.
4. **"'half of ADR growth is bigger units' (it is +0.46–0.8pp)"** — directly the unit-size / party-size
   term. The card carries **+0.797 pp** for 3Q26, consistent with the stated correction.
5. **"the 1.71M quote panel as 'fee-inclusive' (it is not)"** — the quote-basis price panel that M2's
   2026 premium and the hedonic coefficients rest on.
6. **"the 120-market panel as a nights measurement"** — the same Inside-Airbnb review panel that
   supplies booked capacity (I1, 123 markets) and the new-listing share (M3); it is an ADR-mix input,
   and must not be re-used as a nights measurement.

Fuller lists: `docs/revenue-forecast-strategy/05_backtests/RED_TEAM.md`,
`research/notes/overnight/14_master-synthesis.md` §11.

Two more standing "do not use" instructions that are not in §6 but are equally binding, both from
`docs/adrv3/SYNTHESIS.md` §5:
- **"do not use K's fitted coefficient anywhere"** (0.114 — see §2).
- **"do not use L's primary model's numbers (+0.6 / +1.1 ex-FX) for anything"** (see §5).
- Plus: *"Do not build another price panel, scrape, or request calendar prices (J and the 8 September
  test closed those routes)."*

---

## 11. What is validated, what is not — the honest scoreboard

| term / route | status | walk-forward ratio vs naive | source |
|---|---|---|---|
| **residual `last_q` rule** (the v3 rule) on **dollar** ADR y/y | **PASS 4 of 4** | 0.916 / 0.905 (eur), 0.876 / 0.871 (baskets); jk max 0.969 / **0.989** / 0.918 / 0.924 | `K3_pass_table.csv`, L3 results |
| same rule on the **integer ex-FX** target | **FAILS on window 2** | **0.985 (n 10) / 1.080 (n 9)**, jk to 1.183, 0 of 9 below 1 | same |
| **K fee-mechanics line** (coefficient imposed at 0.007) | PASS by 0.003–0.007 of ratio | 0.912 / 0.898 / 0.873 / 0.868 | `K3_k_criterion.csv` |
| K fitted coefficient 0.114 | **do not use** — 16× mechanics, confounded with RNPL (r 0.974) and a 4Q25 dummy (0.885) at n 14 | — | `K3_residual_fit.csv`, `K3_alternatives.csv` |
| **H component build** (all five terms, trailing means) | **LOSES** | **1.583** (RMSE 1.292 vs naive 0.816) | `adr_exfx_backtest.csv` |
| **unit_size** term as a timing signal | **LOSES badly** | **4.168** (lead 0), **5.471** (lead 1); r −0.17, perm p 0.45 | `I4_backtest_scoreboard.csv` |
| unit_size vs the residual | LOSES | 1.839 | same |
| **geo_mix** (any review-based construction) vs ex-FX ADR | LOSES | 1.097 to 1.338 | same |
| geo_mix `letter_buckets_pp` as a proxy for H's own geo term | beats naive but n 7 / wf n 3 | **0.221** (r 0.994) | same |
| **los_mix** vs ex-FX ADR | marginally beats | **0.877** — but r −0.125, perm p 0.694 | same |
| three measured terms together | LOSES | 1.382 | same |
| **M new-listing premium term** | **FAIL** (RMSE lower on 2 of 4) | e.g. eur 1Q24 1.113 vs base 1.099 | `M5_criterion.csv` |
| M wedge-corrected term with a **fitted** β ≈ −10 to −15 | beats (0.70–0.81) but **β is −10 against a mechanical +1** — not the composition mechanism, not promoted | 0.70–0.81 | M note line 126 |
| **L regional route** (primary `L_wf`) | **FAIL 0 of 4** | 1.198 / 1.324 (eur), 1.033 / 1.078 (baskets) | `L3_pass.csv` |
| L EMEA on euro-area HICP accommodation | real per region, **does not survive the jackknife or aggregation** | 0.914, jk max **1.173** | `L2_proxy_tests.csv` |
| L NA on US lodging CPI / BEA hotel prices | FAIL, **wrong sign** (r −0.78 to −0.92) | 1.207 / 1.319 | same |
| **US hotel comparators** vs consolidated ex-FX ADR (J2) | **all FAIL** | best **1.0261** (BEA diff lag0 vs residual); MAR 1.1828, HLT 1.1343 | `data/processed/adrq3/J/proxy_tests.csv` |
| L3 hotel transmission test | **no pass criterion pre-registered**; verdict **"NOT ESTABLISHED"** | r 0.078 (CPI) / −0.186 (BEA) vs reported ADR | L3 results |
| `mgmt_adr_guide` (management's own ADR commentary, coded) | **survivor** | **0.9721** vs reported ADR y/y | `proxy_tests.csv`, `J2_mgmt_adr_guide_coded.csv` |
| **seats dilution** | not a measurement at all — scenario build on undisclosed volumes | — | `15_seats_dilution.py` |
| **RNPL ADR premium** | derived from bundle GBV-pts ÷ nights-pts, circular in the nights-share file | — | §8 |

**Three survivors in the whole repo, across all ~200 scored ADR features:** the blended residual
`last_q` rule (on the dollar target only), euro-area HICP accommodation against **EMEA** ex-FX ADR, and
management's own coded ADR guidance against reported ADR y/y.

## 12. Gaps a mechanism-led ADR build would still have to fill

1. **A within-region, like-for-like realised price series.** Nothing in the repo measures the price a
   given listing actually got, y/y. J and the 8 September test closed the calendar-price route; the
   quote panel is asking prices and is not fee-inclusive (kill-list item 5).
2. **RNPL nights share, independently observed.** Would pin the ADR premium and split the bundle's 1 pp
   into a mix leg and a fee leg. Currently circular (§8b).
3. **A supply term.** Active-listings y/y stops at 1Q24 (§7); the M −10 lead is untested and
   un-preregistered (§4).
4. **2026 LOS.** No stay-length disclosure since 1Q24 and no 2026 ALOS, so `los_mix_pp` for 1Q26 onward
   is a **fill (+0.30)**, and the I2 calendar-runs alternative rests on 2 markets per region.
5. **Occupancy.** No Airbnb occupancy series exists, disclosed or constructed (§7).
6. **Seat volumes and hotel nights.** Entirely assumed; 18.7m FY25 hotel nights is 3.5% × 533m, a point
   pick inside "single-digit percentage" (§8f).
7. **A lap-quarter observation.** The harness has never scored one, so it cannot rank the 4Q26
   residual scenarios (3.06 lap-only to 5.22 K rule) — a 2.2 pp spread worth $479m of 4Q26 GBV and
   $65m of revenue.

---

## 13. ⚠ LIVE, UNCOMMITTED WORK ON THIS EXACT LINE (found 2026-09-21 23:07–23:18)

Three **untracked** paths in the working tree, written tonight, are building precisely the
mechanism-led ADR line this inventory was commissioned for. They are not in git and were not
produced by this survey:

- `docs/pitch-model-v2/lines/adr_fx_prereg.md` (13,276 B, 23:10)
- `analysis/src/pitch_model_v2/adr_engine/` — `config.py, fx_data.py, fetch_fx.py, exfx.py,
  exposure.py, forecast.py, posterior.py, walkforward.py`, `tests/` (empty), 23:07–23:18
- `data/processed/pitch_model_v2/adr_engine/` — `fx_daily_2026-09-21.csv` (1.76 MB),
  `fx_design_full.csv`, `fx_pit_walkforward.csv`, `fx_scores.csv`, `fx_forecast_asof.csv`,
  `fx_currency_contributions.csv`, `fx_weights_posterior.csv`, `fx_beta_draws.npy`,
  `fx_sensitivity_revenue_shares.csv`, `fx_fetch_manifest_2026-09-21.csv`, `posterior_stdout.txt`

**The prereg** (registered *before* any fit; proposed **DEC-0034**, pending Theo's confirmation) states
the motivation in terms that match this brief exactly: card v3 carries two legs nobody built as a
mechanism — (a) the FX leg is the **midpoint of two in-sample fits ranked in-sample on the same 17
quarters they are scored on** (X1 §6: "cannot be quoted as out-of-sample skill"), and (b) the ex-FX leg
is "a persistence rule on an unobserved residual … which a lodging analyst will call a carry, not a
model." It rebuilds the ADR line the way the nights line was rebuilt on 18 Sep (DEC-0028).

Its FX identity (no lag — ADR FX is contemporaneous-at-booking, unlike revenue FX which carries the Φ
kernel):
```
FX_pp(t) = 100 · Σ_c ω_c(t) · [ ē_c(t)/ē_c(t−4) − 1 ]
ω_c(t)   = Σ_r g_r(t) · β_r · κ_{r,c}
```
with `ē_c` the business-day mean USD-per-unit rate (FRED H.10) and `ω` the GBV currency mix — **the
only unknown**. It notes the identity closes on disclosed data to **≤0.042 pp in every quarter**
(`adr_history_components.csv` `identity_check_pp`), and that the ex-FX leg is deliberately **not** given
a pass line "it cannot earn (the lap quarters have never been scored)".

**`fx_scores.csv`** (36 rows; `window, origin, variant, n, rmse_pp, rmse_naive_pp, ratio_vs_naive,
ratio_boot90_lo/hi, interval_rmse_pp, interval_ratio, bias_pp, mean_obs_frac, pass_line_0.75`) —
pre-registered pass line **ratio < 0.75**:

| window | origin | variant | n | RMSE | naive RMSE | ratio | boot90 lo–hi | pass |
|---|---|---|---|---|---|---|---|---|
| W1 | O1 | V0_translation | 13 | 1.313 | 3.002 | **0.437** | 0.189–0.728 | True |
| W1 | O1 | V1_passthrough | 13 | 1.492 | 3.002 | 0.497 | 0.293–0.781 | True |
| W1 | O1 | **V2_eur_ols** | 13 | 1.198 | 3.002 | **0.399** | 0.254–0.604 | True |
| W1 | O1 | V3_usd_broad_ols | 13 | 1.762 | 3.002 | 0.587 | 0.364–0.893 | True |
| W1 | O1 | zero | 13 | 2.226 | 3.002 | 0.742 | 0.487–1.023 | True |
| W1 | O2 | V0_translation | 14 | 0.724 | 2.106 | **0.344** | 0.271–0.438 | True |
| W1 | O2 | **V2_eur_ols** | 14 | 0.569 | 2.106 | **0.270** | 0.195–0.389 | True |
| W1 | O2 | V3_usd_broad_ols | 14 | 1.121 | 2.106 | 0.532 | 0.388–… | True |

i.e. **the FX leg passes its pre-registered bar comfortably, point-in-time, at two origins** — which is
more than the adrv3 midpoint estimator could ever claim.

**`fx_forecast_asof.csv`** (24 rows; `asof, asof_label, quarter, fx_pp_point_spot_held, p10, p50, p90,
sd, obs_frac_at_asof, shares_fy, last_fx_obs, usd_weak_+5pct, usd_strong_-5pct`), as-of 2026-09-21
(FRED through 18 Sep) and as-of the 2 Oct memo date:

| as-of | quarter | FX pp (spot held) | p10 | p50 | p90 | sd | obs frac | USD −5% | USD +5% |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-21 | **3Q26** | **+0.415** | 0.356 | 0.416 | 0.481 | 0.054 | **0.879** | +0.763 | +0.068 |
| 2026-09-21 | **4Q26** | **+0.514** | −1.056 | 0.582 | 2.260 | 1.305 | 0.000 | +3.390 | −2.363 |
| 2026-09-21 | 1Q27 | −0.369 | −3.200 | −0.236 | 2.778 | 2.314 | 0 | | |
| 2026-09-21 | 2Q27 | −0.427 | −3.902 | −0.227 | 3.680 | 2.944 | 0 | | |
| 2026-10-02 | 3Q26 | +0.415 | 0.383 | 0.416 | 0.450 | 0.029 | **0.955** | | |

**This matters to the number, not just the method.** The engine's 3Q26 FX is **+0.42 pp** against the
adrv3 card's **−0.43 pp** (N's midpoint) — a **0.85 pp** swing on the reported ADR line, ≈ **$1.45 of
3Q26 ADR** and ≈ **$220m of 3Q26 GBV** at the card's own sensitivities (§1). 87.9% of 3Q26's FX is
already observed at this build (95.5% by the memo date), so this is close to a measured quantity, where
the card's −0.43 is the midpoint of two in-sample fits. **Anyone using the adrv3 card's FX line should
reconcile against this engine before the 2 Oct freeze.**

Caveats: uncommitted, untracked, `tests/` is empty, DEC-0034 is *proposed* and unconfirmed, and the
currency-mix `ω` (via `β_r`, `κ_{r,c}`, `shares_fy = 2025`) is the fitted/assumed part. Not yet
reconciled against `data/processed/adrv3/N/N1_*` in any file I found.
