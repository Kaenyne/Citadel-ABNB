> Research survey by an autonomous Opus subagent on 22 Sep 2026 (ADR line v2, origin-destination and country price inputs), read-only; archived verbatim as provenance for docs/pitch-model-v2/lines/adr_v2_geomix_prereg.md. Its snapshot of the engine folder predates the full-panel price build (120 markets from the capture store) and the ECB/peg rates; the Hong Kong currency defect it found was fixed the same day. Model output, not a team decision.

# D — Origin / destination / sub-regional price inventory

Read-only survey, 22 Sep 2026, repo `/Users/theomachado/Citadel-ABNB` branch `theo/pitch-model-v2`.
Nothing in the repo or in `~/abnb_ia_capture/` was modified. No web fetches. No mix term computed here.

**Headline for the caller.** The sub-regional layer is not a greenfield: an in-flight, **untracked**
(uncommitted) build dated **today** already contains the exact inputs — `stays_yoy_by_country_vmatch.csv`,
`market_price_levels_usd.csv`, `market_currency_map.csv` — plus the estimator (`geomix.py`) and a
pre-registration (`docs/pitch-model-v2/lines/adr_v2_geomix_prereg.md`, §4 Results still empty). The binding
constraints are **price-level coverage (13 countries, 32 markets)** and the fact that the panel is a
**destination** object while every disclosed country statement (India, Brazil, Japan, Mexico) is an
**origin** statement.

---

## 0. The in-flight build (read this first)

`data/processed/pitch_model_v2/adr_engine/` — produced by `analysis/src/pitch_model_v2/adr_engine/`
(`00_summary.json` `run_at 2026-09-21T23:39:12`, `fx_last_obs 2026-09-18`).

`git status --porcelain` shows these as **untracked** (`??`), i.e. built but not committed:

```
?? analysis/src/pitch_model_v2/adr_engine/geomix.py
?? data/processed/pitch_model_v2/adr_engine/fx_daily_extra_2026-09-22.csv
?? data/processed/pitch_model_v2/adr_engine/market_currency_map.csv
?? data/processed/pitch_model_v2/adr_engine/market_price_levels_usd.csv
?? data/processed/pitch_model_v2/adr_engine/stays_yoy_by_country.csv
?? data/processed/pitch_model_v2/adr_engine/stays_yoy_by_country_vmatch.csv
?? data/processed/pitch_model_v2/adr_engine/stays_yoy_by_market.csv
?? data/processed/pitch_model_v2/adr_engine/stays_yoy_by_market_vmatch.csv
?? docs/pitch-model-v2/lines/adr_v2_geomix_prereg.md
```

`geomix.py` (75 lines) is **not yet imported by `run.py` or `assemble.py`** (grep for `geomix`,
`subregional_term`, `country_prices` over `adr_engine/*.py` returns only `geomix.py` itself). So the
term has been *specified and its inputs built*, but not run/scored/published.

The estimator, verbatim from `geomix.py` docstring:

```
within-region  mix_r(t) = [Σ_c s_c(t−4)(1+g_c(t)) P_c] / [(1+g_r(t)) Σ_c s_c(t−4) P_c] − 1
sub-regional geo term(t) = Σ_r w_r · mix_r(t),   w_r = 10-K regional GBV share
```

with `s_c(t−4)` = the country's share of its region's **vintage-matched prior-year** panel stays
(`n_prior`), `g_c` = country stays y/y, `P_c` = the country's USD price level. Countries without a price
level take the **region median** and therefore **contribute exactly zero within-region mix by
construction** (`build_term(..., impute_region_median=True)`). That is the single most important design
fact for interpreting coverage gaps below.

`country_prices()` collapses market → country by an `n_old`-weighted mean of USD levels, preferring the
`quote_per_night` basis and bridging `listed_nightly`-only markets by the **region-median quote/listed
ratio**.

Pre-registration: `docs/pitch-model-v2/lines/adr_v2_geomix_prereg.md` (dated 2026-09-22, written before
any score). H1 = the term is negative on average 1Q23–2Q26 with |mean| ≥ 0.25pp. H2 = walk-forward
`core2(t) = residual(t) − bundle(t) − subgeo(t)`, targets 1Q24–2Q26 (W1 n=10) and 1Q25–2Q26 (W2 n=6),
**pass line RMSE ratio to residual carry ≤ 0.75 on both windows**. H3 = forward scenario regardless.
§4 "Results (filed after the run)" is **empty**.

---

## 1. Destination-side stays panel (the E package)

### 1.1 Files and schemas — `data/processed/q3nowcast/E/`

| File | rows | columns |
|---|---|---|
| `market_geo.csv` | 123 | `market_key, country, region` |
| `market_vintage_monthly.csv` | ~4.8 MB | `market_key, cdn_path, dump_date, ymi, n_reviews, n_listings, n_reviews_mature12, n_reviews_mature24, n_new_listing_cohort, ym` |
| `market_monthly_yoy.csv` | 49,252 | `market_key, dump_date, ymi, n_reviews, n_mature12, n_mature24, n_lag12, n_mature12_lag12, yoy_all, yoy_mature, yoy_cohort, country, region, ym, vintage_late, vintage_old, n_vm_cur, n_vm_prior, yoy_vmatch` |
| `vintage_matched_nowcast_market.csv` | — | `market_key, region, period, vintage_late, vintage_old, win_start, win_end, n_cur, n_prior_oldvintage, n_prior_samevintage, yoy_vmatch, yoy_within, wedge_pp` |
| `vintage_matched_nowcast.csv` | — | `period, region, n_markets, vmatch_eq, vmatch_cw, within_eq, within_cw, wedge_eq_pp, regions_weight_covered` |
| `index_quarterly.csv` | — | `year, q, quarter, region, measure, n_markets, w_equal, w_reviews, w_median, reviews, reviews_lag12, regions_weight_covered` |
| `partial_window_yoy_market.csv` | — | `market_key, region, vintage, years_back, win_start, win_end, n_cur, n_prior, yoy` |
| `region_monthly_index.csv`, `global_monthly_index.csv`, `stable_listing_yoy_market.csv`, `survivorship_wedge.csv`, `posting_lag_curve.csv`, `coverage_monthly.csv` | — | supporting |

`data/processed/q3nowcast/E_aug/` is a parallel, **later-vintage** copy of the same 33 files (E_aug is
the one `adrq3/I3_geo_mix_3q26.csv` cites as "E_aug vintage-matched … 3Q26 to date").

**There is no `index_regional_vmatch_pct.csv` in E.** The file of that name lives at
`data/processed/forecast_methods/reviews_index_v2/index_regional_vmatch_pct.csv` (42 rows,
`qi, APAC, EMEA, LatAm, NAM`, in **percent**, `qi = year*4 + (q−1)`). Recent rows:

| quarter | qi | APAC | EMEA | LatAm | NAM |
|---|---|---|---|---|---|
| 3Q25 | 8102 | 4.95 | 2.18 | 18.44 | −0.38 |
| 4Q25 | 8103 | 6.24 | 5.52 | 24.82 | 0.06 |
| 1Q26 | 8104 | 8.86 | 4.73 | 18.22 | 5.41 |
| 2Q26 | 8105 | 2.30 | 1.48 | 20.40 | 6.90 |

Same directory also has `panel_country_month.csv` (1,782 rows; `code, ymi, nights, y_yoy, x_yoy_vmatch,
x_yoy_all, x_yoy_mature`) — **18 EU countries only**, ISO-2 codes, Eurostat nights as `y`; and
`mix_weights_stay_quarter.csv` (24 rows, `qi, NAM, EMEA, LatAm, APAC`).

### 1.2 Market list — 123 markets, 37 countries, 4 regions

`market_geo.csv` `region` = the **reporting region** (NAM/EMEA/LatAm/APAC).

| region | markets | countries (markets each) |
|---|---|---|
| **EMEA** | 57 | italy 10, spain 9, france 4, greece 4, united-kingdom 4, belgium 3, switzerland 3, the-netherlands 3, germany 2, ireland 2, portugal 2, austria 1, czech-republic 1, denmark 1, hungary 1, kenya 1, latvia 1, malta 1, norway 1, south-africa 1, sweden 1, turkey 1 |
| **NAM** | 42 | united-states 34, canada 8 |
| **APAC** | 17 | australia 11, china 1 (hong-kong), japan 1 (tokyo), new-zealand 1, singapore 1, taiwan 1, thailand 1 |
| **LatAm** | 7 | brazil 2, argentina 1, belize 1, chile 1, colombia 1, mexico 1 |

**No India anywhere.** No Indonesia, Vietnam, Korea, Philippines, Poland, Croatia. The store is
Inside-Airbnb-shaped, i.e. rich-country / regulated-city biased.

`market_summary_2026.csv` is the same store at **120** markets / 35 countries (its `region` column is the
*sub-national* province, not the reporting region). The 3 E-only markets are `ireland` (1 of 2),
`malta`, `new-zealand`. `~/abnb_ia_capture/` holds 35 country directories (+`logs`) with 3 `.csv.gz` per
market = 120 markets, one vintage each, 9.5 GB.

**Contradiction to flag:** `M4_bottom_up_market_panel.md` §2.0 and §1.4 say "120 markets × 34 countries".
`market_geo.csv` says 123 / 37. `stays_yoy_by_country_vmatch.csv` says 119 / 34. All three are live in
the repo. The reconciliation is: store 120/35 → E adds ireland+malta+new-zealand = 123/37 → the vmatch
panel drops 4 markets that have fewer than 2 usable vintages = 119/34.

### 1.3 Per-country stays y/y — already built

`data/processed/pitch_model_v2/adr_engine/stays_yoy_by_country_vmatch.csv`
1,430 rows · `country, region, q, n_cur, n_prior, n_mkts, stays_yoy_pct, quarter` · 34 countries ·
2016Q1–2026Q3 · **all 34 countries have all 14 quarters 1Q23–2Q26** (119 markets each quarter).

Sibling files: `stays_yoy_by_market_vmatch.csv` (4,996 rows, adds `months`),
`stays_yoy_by_country.csv` / `stays_yoy_by_market.csv` (within-vintage variant, `rev`/`rev_prev`,
2022Q1 onward, survivorship-biased — the vmatch files are the ones to use).

Country stays y/y (%), vintage-matched, 1Q25–2Q26:

| region | country | 1Q25 | 2Q25 | 3Q25 | 4Q25 | 1Q26 | 2Q26 |
|---|---|---|---|---|---|---|---|
| APAC | australia | −0.3 | 3.7 | 4.2 | 6.0 | 5.1 | 0.7 |
| APAC | china (HK) | −4.4 | 7.4 | 9.4 | 8.8 | 5.8 | −10.4 |
| APAC | new-zealand | −4.4 | 8.0 | 9.2 | 6.5 | 13.2 | 3.0 |
| APAC | singapore | −1.0 | 26.9 | 47.2 | 32.9 | 39.1 | 13.6 |
| APAC | taiwan | 0.5 | 1.8 | 7.3 | 8.8 | 9.5 | 3.9 |
| APAC | thailand | 16.6 | −0.6 | −0.7 | 4.7 | 10.8 | 12.1 |
| EMEA | austria | −10.1 | −8.0 | −8.0 | 12.9 | 5.9 | −1.1 |
| EMEA | belgium | −1.5 | 4.5 | −1.4 | 1.7 | −4.4 | −7.5 |
| EMEA | czech-republic | 10.2 | 15.2 | 10.6 | 15.2 | 16.3 | 1.5 |
| EMEA | denmark | −6.6 | −7.0 | 2.3 | −3.8 | −9.7 | −0.9 |
| EMEA | france | 11.0 | 9.4 | 2.8 | −1.9 | −1.9 | −3.1 |
| EMEA | germany | 9.8 | 3.2 | −7.5 | 4.2 | −0.5 | −2.4 |
| EMEA | greece | 5.6 | 0.6 | −0.7 | 0.3 | 3.6 | 0.7 |
| EMEA | hungary | 1.4 | −2.5 | −4.2 | −0.8 | −4.7 | −10.6 |
| EMEA | ireland | −3.9 | −1.0 | 0.9 | 10.0 | 8.2 | 3.3 |
| EMEA | italy | 8.9 | 6.1 | 3.0 | 8.1 | 12.0 | 4.2 |
| EMEA | latvia | 11.8 | 18.8 | 14.4 | 5.7 | 4.9 | 3.3 |
| EMEA | malta | 10.5 | 3.9 | 0.3 | 11.4 | 7.1 | 8.4 |
| EMEA | norway | 7.3 | 14.8 | 14.6 | −4.3 | −8.4 | −4.0 |
| EMEA | portugal | −3.5 | 0.9 | −0.5 | −0.9 | −4.2 | −2.6 |
| EMEA | south-africa | 7.7 | 16.6 | 11.6 | 15.4 | 13.7 | 7.8 |
| EMEA | spain | 1.9 | −0.1 | 0.6 | 4.7 | 2.1 | 1.8 |
| EMEA | sweden | 1.3 | −14.7 | −3.9 | 6.8 | −14.3 | −2.0 |
| EMEA | switzerland | 2.3 | −0.9 | 5.5 | 3.4 | −3.3 | −12.5 |
| EMEA | the-netherlands | 3.2 | 3.7 | −1.6 | 7.4 | 3.7 | 4.9 |
| EMEA | turkey | −1.7 | 1.0 | 10.6 | 17.9 | 17.7 | 5.0 |
| EMEA | united-kingdom | 4.2 | −0.9 | 10.6 | 8.8 | 8.0 | 7.7 |
| LatAm | argentina | 4.9 | 33.8 | 25.4 | 23.7 | 26.2 | 24.6 |
| LatAm | belize | −7.3 | −22.1 | −9.3 | −5.7 | 1.0 | 4.9 |
| LatAm | brazil | 50.8 | 58.0 | 20.3 | 30.2 | 20.2 | 14.8 |
| LatAm | chile | 45.5 | 28.2 | 31.6 | 24.5 | 26.8 | 19.2 |
| LatAm | mexico | 21.2 | 23.3 | 11.9 | 23.2 | 7.8 | 24.0 |
| NAM | canada | −1.2 | 4.3 | 8.8 | −3.4 | 6.2 | 16.1 |
| NAM | united-states | −3.1 | −1.9 | −2.1 | 0.9 | 5.5 | 5.1 |

(Brazil here is `rio-de-janeiro` only — são-paulo is dropped, see §1.4.)

### 1.4 What is missing and why

| dropped | dumps held | consequence |
|---|---|---|
| `japan_kanto_tokyo` | 1 (`2026-06-30`) | **Japan has no stays y/y at all** — the most-quoted APAC country in the letters |
| `brazil_sp_são-paulo` | 2 (2026-06-14, 2026-08-18) | Brazil = Rio only; SP is the larger market (42,354 listings vs 48,713) |
| `colombia_dc_bogotá` | 2 | Colombia absent |
| `kenya_nairobi_nairobi` | 2 | Kenya absent |

The vintage-matched construction (latest dump vs a dump 300–430 days older) needs ≥ 2 well-separated
vintages; 1 market has 1 dump and 4 have 2.

**3Q26 QTD is effectively empty in this build**: `stays_yoy_by_market_vmatch.csv` `q = 2026Q3` has only
4 markets (`italy_puglia`, `italy_sicily`, `italy_trentino`, `turkey_istanbul`), 2 countries. The 3Q26
read has to come from the E_aug partial-window files (`partial_window_yoy_market.csv`,
`partial_vs_full_quarter_market.csv`, `monthly_nowcast_2026_market.csv`, `q3_2026_coverage.csv`), which
is what `adrq3/I3_geo_mix_3q26.csv` does at the region level.

### 1.5 If you must rebuild from raw

`market_vintage_monthly.csv` + `market_geo.csv` are sufficient: for market `m`, quarter `q`, take the
latest dump `v1` and the dump `v0` 300–430 days earlier, sum `n_reviews` over the three months of `q`
in `v1` and over the same three months a year earlier **in `v0`** (same listing age → survivorship
cancels), then aggregate to country by summing counts (not averaging y/y). Trim the last 2 months for
posting lag (`posting_lag_curve.csv`, `posting_completeness_curve.csv`). `yoy_vmatch` in
`market_monthly_yoy.csv` is the monthly version of exactly this.

---

## 2. Guest-ORIGIN data

**Verdict: there is no measured Airbnb guest-origin object in the repo.** Four partial proxies exist,
each explicitly labelled a scenario or a proxy by its own author.

### 2.1 Disclosed origin statements — `data/processed/overnight/10_regional_panel_quarterly.csv`

23 rows (4Q20–2Q26), 78 columns. Built by `analysis/src/overnight/10_regional_panel.py` which reads
**only** `data/raw/letters/*.htm` = 23 shareholder letters, 8-K **Exhibit 99.1** → every value below is
**FILED**, not transcript-mirror. (`data/raw/letters/` is gitignored and empty in this checkout — see
`docs/pitch-model-v2/dossiers/ADR_A_disclosure_ledger.md` §0; the CSV is the durable artefact.)

The origin-side columns, all rows:

| quarter | latam_dom | brazil_origin | india_origin | japan_dom | china_outbound | first_time_booker | expansion_market_growth_vs_core | NA share disc. | ex-NA nights disc. |
|---|---|---|---|---|---|---|---|---|---|
| 3Q23 | | | | | 100 | | | | |
| 4Q23 | | | | | 90 | | | | |
| 1Q24 | | | | | 80 | | more than double core markets | | |
| 2Q24 | 24 | | | | | | significantly outperformed core | | |
| 3Q24 | 21 | | | | | | more than double core | | |
| 4Q24 | 30 | 21 | | | 25 | | more than twice core | | |
| 1Q25 | | 27 | | 21 | | | significantly outperformed core (5 quarters) | 30 | 11 |
| 2Q25 | | 18 | | | | | about twice core (6 quarters) | 30 | |
| 3Q25 | | 21 | | 27 | | | twice core, LTM | 30 | |
| 4Q25 | | 21 | 50 | | | | roughly twice core | | |
| 1Q26 | | 21 | 50 | | | 10 | roughly twice core, LTM | | |
| 2Q26 | | 31 | 60 | | | 11 | roughly twice core, LTM; core markets US, France, UK, Australia also accelerated | | |

Cross-border columns (same file), 1Q21–1Q24 then **disclosure stops**:

| quarter | cross_border_share_pct | cb_growth | cb→NA | cb→APAC | cb→EMEA | urban_share | urban_growth | LTS share |
|---|---|---|---|---|---|---|---|---|
| 1Q23 | 45 | 36 | 34 | 160 | — | 48 | 20 | 18 |
| 2Q23 | 45 | 16 | 20 | 80 | 15 | 48 | 13 | 18 |
| 3Q23 | 45 | 17 | 25 | — | 11 | 49 | 15 | 18 |
| 4Q23 | 44 | 13 | 15 | 29 | — | 51 | 11 | 19 |
| 1Q24 | 46 | 10 | — | 28 | — | — | — | 17 |
| 2Q24–4Q24 | — | — | — | 22 / 23 / 27 | — | — | — | — |
| 1Q25–2Q26 | **all NaN** | | | | | | | |

`data/processed/overnight/05_crossborder_share.csv` (15 rows, `quarter,
cross_border_share_of_gross_nights_pct, source`) carries the same series with the explicit provenance
string *"shareholder letters (Travel corridors section); 2019 values quoted as comparators in the 2022-23
letters; **not disclosed after 1Q24**"*: 2019Q1–Q4 = 51/50/48/47, 2021Q3 33 … 2024Q1 46.

### 2.2 Sentence ledger — `data/processed/overnight/10_regional_quotes.csv`

766 rows · `quarter, categories, sentence` · 4Q20–2Q26 · all from the filed letters. 167 sentences name
a country. `categories` is a pipe-joined tag set from the regex map at `10_regional_panel.py:50-62`
(`north_america | emea | latin_america | asia_pacific | cross_border | urban | long_term_stays |
expansion_markets | domestic | events`). The country-growth sentences that matter (all FILED, verbatim):

- **4Q24** — "Origin nights booked in Brazil grew over 20% for both Q4 and full-year 2024." · "the China
  outbound business with nights booked growing 25% year-over-year in Q4 2024."
- **1Q25** — "In Brazil, origin nights booked grew 27% in Q1 2025–an acceleration from Q4 2024." ·
  "domestic nights booked in Japan … domestic nights growing over 20% year-over-year." · "nights booked
  by Canadian guests to destinations in Mexico increased 27% year-over-year in March."
- **2Q25** — "sequential acceleration in growth of nights booked on an origin basis across several key
  countries, including Canada, Germany, and Japan." · "strong results in Germany, one of our expansion
  markets, with double-digit year-over-year growth of nights booked in Q2 2025." · Brazil origin
  "high-teens", first-time bookers ~20%.
- **3Q25** — "first-time bookers increasing over 20% in Japan and **nearly 50% in India**." · "In Japan,
  nights booked for domestic travel in Q3 2025 increased 27%." · Brazil origin "over 20%", FTB +17%.
- **4Q25** — "Q4 2025 nights booked on an origin basis in **India grew 50%** year-over-year and
  first-time bookers grew more than 60%." · "**India became one of our fastest-growing countries on an
  origin basis**." · "origin nights booked in **Mexico**–up high-teens." · Brazil "over 20%".
- **1Q26** — "In India, origin nights booked grew approximately 50% … and in Brazil, origin nights grew
  over 20% for the third consecutive quarter." · "continued double-digit nights growth in Mexico." ·
  FTB +10%, "highest since early 2022", strongest in Brazil, Japan, India.
- **2Q26** — "**origin net nights booked in India accelerate to 60%** year-over-year, and first-time
  bookers … more than doubled." · "Brazil … **accelerating to over 30%** year-over-year growth and …
  first-time bookers increasing 40%." · "in Japan … origin net nights booked grew in the **high-teens**."
  · "net origin nights booked in the **U.S., France, the UK, and Australia all accelerated** in Q2."
- **expansion markets**, every quarter 1Q24–2Q26: "more than double" → "roughly twice" core, on an
  **origin** basis, LTM from 1Q26.

**The word that governs all of these is "origin".** They describe where the *guest* lives, not where the
night is spent. The E panel is a *destination* object. The prereg says so explicitly (§2 Coverage check:
"origin-side effects inside a destination (an Indian traveller booking a cheaper listing in Bangkok) are
outside this object's reach and are not claimed").

`expansion markets` is **never defined as a country list** in any filing or in the repo (grep over
`docs/` returns only descriptive references). It cannot be mapped to the panel.

### 2.3 The one O-D object built — `regional_kernel_v1`

Note: `docs/revenue-forecast-strategy/05_backtests/X_REGIONAL_KERNEL_OD_FX.md` (161 lines; briefs at
`docs/thesis-kernel-topdown/lane1/X_REGIONAL_KERNEL_OD_FX.md` and
`docs/revenue-forecast-strategy/lane1_briefs_v2/`). Verdict in the note's own first line:
**"underpowered"**.

Data: `data/processed/forecast_methods/regional_kernel_v1/` (38 files).

| file | rows | content |
|---|---|---|
| `od_nights_matrix.csv` | 384 | `quarter, origin, destination, nights_m, origin_share_of_destination, cross_border_country_assumption, print_date, basis` — **4×4 REGION margins only**, 2021Q1 onward, `basis = "current reconstruction; tourism proxies plus assumptions; not PIT history"`, `cross_border_country_assumption = 0.46` (the stale 1Q24 disclosure, used as a **scenario**) |
| `od_source_coverage.csv` | 2 | NA←NTTO 68.288M arrivals, classified-region 77.19%, currency-matched 74.90%, **`airbnb_od_measured_fraction = 0.0`**; APAC←JNTO 3.4421M, 95.12% / 43.73%, **0.0** |
| `exposure.csv` | 960 | `quarter, geography, region, level, currency, gbv_share, revenue_share, guest_fee_share, print_date, reference_basis, weight_basis`; `weight_basis = "assumed destination basket / partial public tourism origin proxy"` |
| `fx_basket_measured.csv` | 120 | `measured_airbnb_weight` = **all NaN**, `status = "not identified; scenario must not replace original basket"` |
| `fx_basket_scenario.csv`, `adr_passthrough_sensitivity.csv`, `mix_variance_decomposition.csv`, `regional_drift.csv`, `gross_scale_fits.csv`, `public_source_extracts.csv`, `registration_abstentions.csv` | | supporting |

Results relevant here: **measured Airbnb O-D currency cells = 0**; eligible PIT guide forecasts
**0/14 W1, 0/10 W2**; the registry objects were **abstained** from. The note's own memo sentence: *"no
measured Airbnb origin–destination currency matrix is identified."* The demand-channel reallocation it
does compute moves GBV by **$41.0M / $33.4M (+0.15pp / +0.14pp)** in 3Q26/4Q26 — i.e. geographic-mix
reallocation is second-order against translation in that framing.

### 2.4 Reviewer language — the only Airbnb-side origin proxy in the store

`data/processed/abnb_party_size_reviews_v2_language_year_shard{0..5}.csv` — 6 files, **13,350 rows**,
columns `market, year, lang, reviews, mention_any, headcount_n, headcount_mean, share_solo/couple/
family/group, cond_solo/couple/family/group`.

- `market` is `"<market_key>_<dump_date>"` → **123 markets**, 24 dump dates, **years 2008–2026**.
- `lang` has only **8 buckets**: `de, en, es, fr, it, other, pt, zh_ja_ko`. Not a country. `en` is 62%
  of 2025 reviews; `other` (1.44M in 2025) is the bucket that would contain Hindi, Korean, Thai, Polish,
  Dutch, Turkish…
- Granularity is **annual**, not monthly or quarterly.

Global reviews by language:

| lang | 2024 | 2025 | 2026 (partial) |
|---|---|---|---|
| en | 7,906,845 | 9,285,319 | 4,923,293 |
| es | 1,803,469 | 2,474,624 | 1,380,365 |
| other | 1,036,848 | 1,442,628 | 830,326 |
| de | 474,601 | 610,810 | 329,889 |
| fr | 543,492 | 660,623 | 341,553 |
| pt | 325,753 | 473,018 | 292,861 |
| zh_ja_ko | 314,765 | 410,477 | 237,367 |
| it | 134,437 | 170,693 | 88,670 |

Also `data/processed/abnb_party_size_reviews_v2_by_language_year.csv` (138 rows, global by year×lang).
The `X` brief lists "reviewer language / locale in the review store (flagged proxy)" as the Airbnb-side
origin proxy; the `X` note concludes *"Reviewer locale is unavailable, not measured zero."*
**Nobody has built an origin panel from these shards.** The raw store
(`~/abnb_ia_capture/*/…/reviews.csv.gz`) carries `reviewer_id, reviewer_name, comments` — no country,
no locale field.

### 2.5 Eurostat — destination only, one foreign/domestic split at EU27 level

| file | rows | origin content |
|---|---|---|
| `eurostat_platform_nights_monthly.csv` | 99 (2018-01→) | `eu27_domestic`, `eu27_foreign`, `foreign_share_pct` **at EU27 aggregate only**; the 34 `XX_nights` country columns are **totals, no residence split** |
| `overnight/10_eurostat_platform_monthly_latest.csv` | 39 (2023-01→) | same structure + y/y for every country |
| `eurostat_platform_nights_by_country.csv` | 32 | `geo, nights_2019/2023/2024/2025_m, growth_2024/2025_pct, growth_2025_vs_2019_pct, q1_2026_yoy_pct, share_of_eu27_2025_pct` — **destination only** |
| `eurostat_platform_vs_hotel_by_country_2019_2024.csv` | 32 | platform vs hotel nights/bedplaces/share by country |
| `eurostat_platform_nights_quarterly.csv` | 33 | EU27 nights + ABNB EMEA revenue comparison |
| `country_lodging_nights.csv` | 7 | France/Spain/Italy/… platform vs hotel guest nights, 2025 |

The `c_resid` (country-of-residence) dimension of Eurostat `tour_occ_nim` / `tour_ce_omr` is **not
pulled** into any processed file. The X note quotes the EU27 annual split (359.9M domestic / 591.7M
foreign = 62.18% foreign, 2025) from a live API call, not from a stored panel.

### 2.6 Tourism arrivals

`data/processed/ntto_us_inbound_monthly.csv` (19 rows, `month, metric_basis, arrivals_millions, yoy_pct,
source`, 2025-01→; **air_only, no origin breakdown**) · `overnight/10_bench_japan_arrivals_monthly.csv`
· `overnight/10_bench_canada_travel_monthly.csv` · `data/processed/q3nowcast/G/raw/ntto_arrivals_monthly.csv`
· `forecast_methods/macro_pulls/{ntto,istat}.csv` · `iata_rpk_yoy_by_region_monthly.csv` ·
`bts_us_airline_passengers_monthly.csv` · `tsa_checkpoint_monthly.csv`.
**None carries country-of-origin detail in the stored form.** The X note's 12 named NTTO origins and
JNTO nationality split were read live and survive only as the aggregate fractions in
`public_source_extracts.csv` / `od_source_coverage.csv`.

---

## 3. PRICE LEVELS by destination market

### 3.1 The USD-comparable table — `market_price_levels_usd.csv`

`data/processed/pitch_model_v2/adr_engine/market_price_levels_usd.csv`
**63 rows** · `market, market_key, country, region, currency, price_basis, usd_level, n_q, n_old`
**32 markets · 16 countries · 2 bases**. Source per the prereg: `median_old` from
`adrv3/M/M2_new_listing_premium.csv` (entire-home, `age_field = first_review`), converted at the
quarter-average FRED rate from `fx_daily_2026-09-21.csv` + `fx_daily_extra_2026-09-22.csv`.
`n_q` = quarters averaged; `n_old` = established-listing observations (used as the market weight).

| region | country | market | ccy | listed_nightly USD | quote_per_night USD |
|---|---|---|---|---|---|
| NAM | united-states | austin | USD | 161.58 | 251.65 |
| NAM | united-states | chicago | USD | 171.00 | 249.92 |
| NAM | united-states | los-angeles | USD | 174.33 | 249.43 |
| NAM | united-states | nashville | USD | 164.92 | 290.06 |
| NAM | united-states | new-orleans | USD | 133.50 | 220.08 |
| NAM | united-states | new-york-city | USD | 186.00 | 224.58 |
| NAM | united-states | san-diego | USD | 205.67 | 323.93 |
| EMEA | france | paris | EUR | 160.32 | 254.18 |
| EMEA | italy | rome | EUR | 145.30 | 215.04 |
| EMEA | spain | barcelona | EUR | 211.51 | 288.50 |
| EMEA | united-kingdom | london | GBP | 230.57 | 300.29 |
| LatAm | brazil | rio-de-janeiro | BRL | 59.41 | 102.40 |
| LatAm | mexico | mexico-city | MXN | 64.24 | 108.03 |
| LatAm | argentina | buenos-aires | ARS | **NaN** | **NaN** |
| LatAm | belize | belize | BZD | **NaN** | **NaN** |
| LatAm | chile | santiago | CLP | **NaN** | **NaN** |
| APAC | australia | ×11 markets | AUD | 114.50–241.12 | 194.63–381.01 |
| APAC | china | hong-kong | **CNY** | 116.61 | 158.50 |
| APAC | japan | tokyo | JPY | 127.60 | 135.39 |
| APAC | singapore | singapore | SGD | 206.76 | 182.35 |
| APAC | taiwan | taipei | TWD | 78.95 | 89.19 |
| APAC | thailand | bangkok | THB | 45.98 | 58.88 |

**These are the only USD-comparable cross-market price levels in the repo.** Everything else is native
currency or US-only.

Three defects to flag before use:

1. **Hong Kong is mapped to CNY, not HKD** (`market_currency_map.csv` row `china_hk_hong-kong → CNY`;
   `market_price_levels_usd.csv` carries `currency = CNY`). `fx_daily_extra_2026-09-22.csv` **does**
   contain HKD. CNY ≈ 0.14 USD/unit vs HKD ≈ 0.128 → the Hong Kong USD level is overstated by roughly
   9–10%. One-line fix in the currency map.
2. **Tokyo has a USD price level but no stays y/y** (1 dump, §1.4). Japan therefore enters the mix term
   as price-with-no-growth, i.e. not at all.
3. **Canada has no price level at all** — there is no Canadian market in `M2_new_listing_premium.csv`,
   although CAD FX exists. Canada is 17.07% of NAM base stays and grew +16.1% y/y in 2Q26 while the US
   grew +5.1%. Under `impute_region_median`, Canada contributes **zero** NAM within-region mix — which
   is almost certainly the wrong sign for the thesis (Canadian ADR is below US ADR).

`quote_per_night` is fee-inclusive (Inside Airbnb 2026 schema `price_quote_price_per_night`, derived from
`price_quote_total_price`); `listed_nightly` is the pre-2026 `price` field, host-listed, fee-exclusive,
first-available-night. They are **different objects** — the quote basis runs ~+35% to +55% above listed in
the same market. `geomix.py` bridges listed-only markets by the **region-median quote/listed ratio**; all
32 markets here have both bases except `sydney` (quote only) and a few with `n_q = 1`, so the bridge is
rarely binding but the region-median assumption is untested.

### 3.2 Currency availability — `market_currency_map.csv`

123 rows · `market_key, country, region, currency, fx_available` · **115 markets fx_available = True,
8 False.**

FRED coverage in the two fx files: `fx_daily_2026-09-21.csv` = AUD, BRL, CAD, EUR, GBP, INR, JPY, KRW,
MXN, USD_BROAD (2015-01-02→2026-09-18, 29,273 rows); `fx_daily_extra_2026-09-22.csv` = CHF, CNY, DKK,
HKD, NOK, NZD, SEK, SGD, THB, TWD, ZAR (2018-01-02→2026-09-18, 23,947 rows).

**No FRED series → no USD level (8 markets / 8 countries):** czech-republic **CZK**, hungary **HUF**,
kenya **KES**, turkey **TRY**, argentina **ARS**, belize **BZD**, chile **CLP**, colombia **COP**.
Argentina (+24.6% 2Q26) and Chile (+19.2%) are the two fastest-growing priced-out LatAm countries — they
are exactly the countries the thesis wants and exactly the ones that go to the region median.

### 3.3 The underlying market price source — `adrv3/M/M2_new_listing_premium.csv`

637 rows · `market, region, dump_date, quarter, price_basis, scope_flag, usable_for_premium, age_field,
variant, n_new, n_old, median_new, median_old, mean_new, mean_old, raw_median_premium_pct,
raw_mean_premium_pct, raw_logmean_premium_pct, hedonic_premium_logpts, hedonic_se,
hedonic_premium_l30d_weighted_logpts, hedonic_se_l30d_weighted, n_weighted_new, n_weighted_old`.

**34 markets · 16 quarters 4Q22–3Q26** (`1Q23…3Q26` + `4Q22`) · `price_basis` `listed_nightly` 327 rows /
`quote_per_night` 310 rows · `variant` ∈ {`all_rooms`, `entire_home`} · `age_field` ∈ {`first_review`,
`host_since`}. **Native currency** — the USD conversion happens only in `market_price_levels_usd.csv`.

Market coverage (quarters each): NAM 7 (austin 9, chicago 5, los-angeles 6, nashville 8, new-orleans 5,
new-york-city 4, san-diego 5) · EMEA **4 only** (rome 15, paris 10, barcelona 4, london 4) · LatAm 7
(belize 7, buenos-aires 5, mexico-city 5, rio-de-janeiro 5, santiago 5, bogota 2, sao-paulo 2) ·
APAC 16 (tokyo 7, bangkok 7, mid-north-coast 7, western-australia 7, barossa-valley 6, barwon 6,
mornington 6, northern-rivers 6, singapore 6, taipei 6, tasmania 6, brisbane 5, hong-kong 5,
sunshine-coast 5, melbourne 4, sydney 3).

**EMEA is the weak leg**: 4 priced markets out of 57 → 59.0% of EMEA base stays sit in a priced country,
and Germany, Portugal, Greece, Ireland, Netherlands, the Nordics, Turkey, Czechia, Hungary, Switzerland
are all unpriced. `M2_new_listing_premium_region.csv` (218 rows) aggregates to region but only for the
`markets` string it names (e.g. NAM 1Q25 = austin;chicago;los-angeles;nashville;san-diego).

### 3.4 Other price objects, and why none of them is cross-market USD

| file | rows | markets | period | basis | currency | verdict |
|---|---|---|---|---|---|---|
| `market_summary_2026.csv` | 120 | **120** | one 2026 snapshot per market (2026-06-14→2026-08-10) | listed/quote per dump | **native** (`price_median_native`) | The only 120-market price level. **Not USD**, and no FX for 8 currencies. **Data bug: geneva 0.14, vaud 0.15, zurich 0.16** — all three Swiss markets have a broken `price_median_native`; do not use CHF rows without re-deriving from raw. Single snapshot ⇒ no y/y, no quarterly path. |
| `overnight/06_price_per_unit_panel.csv` | 123 | **13** | 2022-12→2026-08 | `listed_nightly` 47 / `quote_per_night` 76 | native | `median_price, median_price_entire, median_price_per_bedroom_entire, median_price_per_person_entire, median_price_1br_entire, median_accommodates/bedrooms_entire, share_entire, share_superhost, median_min_nights, mean_est_nights_booked_l365d` |
| `overnight/06_quote_discount_panel.csv` | 76 | **13** | 2026-03-16→2026-08-30 | quote | native | **`quotes` sums to 1,707,390** — this is the "1.71M quote panel". `share_with_discount_pct, median/mean_discount_pct_of_subtotal, discount_drag_on_ppn_pct, share_line_{cleaning_fee,service_fee,taxes}_pct, median_quote_nights, median_quote_lead_days, median_ppn, median_ppn_entire, median_accommodates, median_price_per_person_night(_entire)`. **No currency column.** Fee-inclusive. |
| `overnight/06_quote_line_items.csv` | 76 | 13 | same | quote | native | line-item presence counts (`li_nightly_subtotal, li_discounted_subtotal, field_discount_amount, li_other, li_discount_amount, field_taxes, li_taxes, field_cleaning_fee, li_cleaning_fee`) |
| `overnight/06_price_gap_series.csv` | 22 | US only | 1Q21–2Q26 | mixed | USD | quarterly ABNB ADR vs CPI lodging, BEA hotels, STR US hotel ADR/RevPAR, MAR/HLT RevPAR, BKNG; `ia_us_median_entire_price`, `ia_us_median_price_per_bedroom/person`, `ia_us_price_basis`, `ia_us_cities`. **US leg only.** |
| `adr/06_price_benchmarks.csv` | 78 | — | 1Q21–2Q26 | — | `currency_basis` column present | benchmark ledger with `like_for_like_basis, availability_lag, status, used_in_price_series` |
| `adr/06_measured_price_quarterly.csv` | 22 | — | 1Q21–2Q26 | — | USD | US leg + RoW leg reconstruction, `price_measured_pp` with lo/hi, `confidence`, `residual_vs_adr_exfx_pp` |
| `inside_airbnb_city_snapshots.csv` | 168 | 13 | 2022-12→2026-08 | `price_basis` flagged | native | `median_price_entire, mean_price_entire, median_price_entire_active, median_price_private, median_price_entire_1br/2br, median_quote_total_entire`, plus PIT scope flags |
| `inside_airbnb_like_for_like.csv` | 258 | 13 | pairs | `price_basis_a/b`, `price_comparable` | native, but **y/y in %** | `lfl_price_chg_median(_clean), lfl_price_chg_mean, lfl_median_price_a/b, lfl_price_chg_annualized, price_pair_eligible` — **repeat-listing price change is currency-free**, so this IS cross-market comparable *as a growth rate*, just not as a level. 13 cities only. |
| `adrq3/J/calendar_price_yoy.csv` | 150 | ≤ few per cell | 1Q25–? | calendar price by lead bucket | % y/y | `snapshot1_quarter, group_type, group, regime, region, median_yoy_pct, trimmed_mean_yoy_pct, mean_ratio_yoy_pct, n_markets` — thin (n_markets 1–2 in most cells) |
| `adrq3/J/J1_price_coverage.csv` | 227 | **32** | 2024-03-16→2025-12-29 | calendar | — | `priced = True` on **98 of 227** market-snapshots; the 32 markets are the M2 set |
| `adrq3/J/J2_ia_quote_sequential.csv` | 44 | 13-ish | 2025-06→2026-08 | `basis_a/basis_b` | % | matched-listing sequential % change; splices listed↔quote |
| `adr/14c_los_runs_panel.csv` | 642 | — | snapshots 2025-09→ | calendar run lengths | — | **no price column**; LOS/occupancy only |
| `q3nowcast/F/F1_daily_levels.csv.gz` | large | 32 | 2024-05→2026 | calendar | — | `market, region, snapshot_date, stay_date, days_ahead, listing_nights, blocked_nights` — **no price**. The calendar work measures blocked share, not booked rate. |
| `overnight/10_regional_quotes.csv` | 766 | — | — | — | — | *sentences*, not prices (name is misleading) |

**Which price levels are USD-comparable across markets:** only
`data/processed/pitch_model_v2/adr_engine/market_price_levels_usd.csv` (32 markets, 13 countries with a
non-null level, fix HKD first). `inside_airbnb_like_for_like.csv` gives cross-market-comparable price
*changes* for 13 cities. Everything else is native currency, US-only, or region-aggregated.

---

## 4. Disclosed regional ADR levels, for validation

`data/processed/adr/01_regional_annual.csv` (30 rows; `year, region, nights_m, gbv_musd, revenue_musd,
nights_precision_m, source_10k, adr_computed, take_rate_pct, adr_stated, alos_nights, gbv_per_booking,
bookings_m, nights_share_pct, gbv_share_pct, revenue_share_pct, *_yoy_pct, adr_round_err_pct`).

`adr_computed` = GBV/nights from the 10-K geographic table (USD):

| year | NA | EMEA | LatAm | APAC | total |
|---|---|---|---|---|---|
| 2020 | 174.44 | 98.38 | 75.93 | 85.73 | 123.69 |
| 2021 | 221.98 | 123.68 | 95.52 | 109.72 | 155.92 |
| 2022 | 242.45 | 127.89 | 91.28 | 116.05 | 160.44 |
| 2023 | 239.32 | 140.33 | 94.59 | 117.96 | 163.51 |
| 2024 | 245.56 | 148.01 | 93.32 | 116.82 | 166.23 |
| 2025 | 255.03 | 158.89 | 94.91 | 118.20 | 171.24 |

Nights share (%): NA 39.08 → **29.64**; EMEA 35.04 → 40.34; LatAm 11.59 → **16.89**; APAC 14.29 → 13.13
(2020→2025). That falling NA share against a 2.7× NA/LatAm ADR ratio is the four-region geo-mix drag.

`data/processed/adr/04_regional_quarterly_wide.csv` (22 rows, 1Q21–2Q26; the file the caller already
has) — recent levels and disclosed y/y:

| quarter | ADR NA | EMEA | LatAm | APAC | nights share NA/EMEA/LatAm/APAC |
|---|---|---|---|---|---|
| 3Q25 | 249.16 | 164.62 | 94.95 | 116.58 | 31.39 / 36.78 / 16.96 / 14.86 |
| 4Q25 | 247.04 | 160.83 | 93.41 | 115.89 | 30.06 / 40.26 / 17.40 / 12.29 |
| 1Q26 | 279.01 | 183.24 | 99.93 | 128.32 | 27.73 / 39.64 / 17.94 / 14.69 |
| 2Q26 | 280.56 | 172.52 | 100.55 | 122.65 | 28.26 / 41.55 / 17.86 / 12.33 |

Disclosed ADR y/y reported / ex-FX (%), 2Q26: NA 7 / 6.75 · EMEA 7 / 5 · LatAm 9 / 2 · APAC 1 / −1.35.
`basis_adr_na = disclosed-chained` from 3Q23; earlier quarters are `modelled`.

---

## 5. What already exists on sub-regional mix

### 5.1 The unidentified residual — `data/processed/adr/07_full_decomposition.csv` (5 rows)

Columns: `year, adr_yoy_pct, geo_mix_pp, interaction_pp, of_which_los_pp, fx_pp, size_mix_pp,
size_n_pairs, size_n_markets, hotel_price_comparator_pp, worst_confidence, within_region_exfx_pp,
**pricing_and_subregional_mix_pp**, regional_exfx_independent_pp, reconciliation_gap_pp,
identity_check_pp, confidence`.

| year | ADR y/y | geo_mix | fx | size_mix | of_which_los | interaction | within_region_exfx | **pricing_and_subregional_mix** | regional_exfx_indep | recon gap |
|---|---|---|---|---|---|---|---|---|---|---|
| 2021 | 26.06 | −0.50 | 2.04 | 0.00 | 0.27 | −0.22 | 24.74 | **24.47** | 24.04 | 0.70 |
| 2022 | 2.68 | −2.75 | −5.17 | 0.00 | 0.26 | −0.39 | 10.99 | **10.73** | 9.76 | 1.23 |
| 2023 | 2.15 | −1.08 | 0.18 | 0.00 | 0.62 | −0.05 | 3.10 | **2.48** | 3.07 | 0.03 |
| 2024 | 1.64 | −1.24 | −0.45 | 0.44 | 0.21 | −0.11 | 3.44 | **2.80** | 3.15 | 0.30 |
| 2025 | 3.02 | −1.58 | 1.30 | −0.25 | 0.04 | −0.11 | 3.41 | **3.62** | 3.54 | −0.13 |

**Definition: a residual by subtraction.** `analysis/src/adr/07_assemble.py:103-104`,
`pricing_and_subregional_mix = within_region_exfx − size_mix − of_which_los`. Classified **"plug,
explicitly named as jointly unidentified"** in `docs/revenue-forecast-strategy/01_ground-truth/
02_model_audit.md` §145. `03_annual_decomposition.csv` is the 4-region parent
(`geo_mix_pp, within_region_pp, interaction_pp, of_which_{fx,los,size_and_price}_pp`, identity closes to
1e-14).

Why unidentified: *"Airbnb discloses no country-level ADR"* — `01_data_inventory.md` §143 and §160;
`03_insider_mechanics.md` §588; `M1_structural_mix_state_space.md` §5, §2.5, §243;
`B3_FY27_DECOMPOSITION.md` L2 row (**+2.83pp**, "NOT SPLIT — separate price and sub-regional-mix states
are exactly collinear"); `l1-reconciliation.md` §304 (+3.00pp, "**unsplit**").

**Contradiction to flag:** `C_M6_fx_takerate_timing_mechanics.md` §78 argues that *the host-fee migration
itself* is "plausibly +2 to +5pp of reported ADR in 1H26 — i.e. a large slice of the unidentified residual
*is* the migration." That competes for the same residual the sub-regional mix term wants to claim. The
prereg's H2 handles this by subtracting the bundle term first (`core2 = residual − bundle − subgeo`), but
the two are not orthogonal and the note should say so.

### 5.2 The plan that already exists — `M4_bottom_up_market_panel.md` §2.4

Writes the identity the caller is asking for, exactly:

```
Δ ln ADR^{home,exFX}_{r,q}  =  Σ_{m∈r} ω_{m,q-4} Δμ_{m,q}                 ← like-for-like pricing
                             +  Σ_{m∈r} (ω_{m,q} − ω_{m,q-4}) μ_{m,q-4}   ← sub-regional mix
                             +  Δ(composition | x)
```

with `μ` from a Bailey–Muth–Nourse repeat-listing index (Case–Shiller weights) on the 13 deep cities and
258 matched pairs, and `ω` from the nights block. Its §358 milestone "**M3 (Thu 24 Sep)**: repeat-listing
index on the 13 cities … first identified estimate of like-for-like pricing vs sub-regional mix" is two
days away and, as far as the repo shows, **not started**. `geomix.py` is the *level*-based shortcut to
the same decomposition (it uses a market price **level** `P_c`, not a repeat-listing index `μ`).

### 5.3 Four-region mix terms already computed (do not double count)

- `data/processed/pitch_model_v2/adr_engine/geo_mix_method_check.csv` (14 rows, 1Q23–2Q26):
  `geo_mix_buckets_pp` vs `geo_mix_H_pp` vs `diff_pp`. 2Q26 = −1.135 vs −1.267 (diff +0.132).
  The two methods converge from 4Q24 (|diff| ≤ 0.18pp) but diverge badly in 2023 (up to −1.69pp).
- `data/processed/pitch_model_v2/adr_engine/geo_mix_forward.csv` (6 rows): 3Q26 −1.293, 4Q26 −1.336,
  1Q27 −1.620, 2Q27 −1.081, 3Q27 −1.174, 4Q27 −1.109 (`geo_mix_nights_linked_pp`); `geo_mix_card_pp`
  flat at −1.428.
- `data/processed/adrq3/I/I3_geo_mix_history.csv` (10 rows) and `I3_geo_mix_3q26.csv` (14 rows,
  `growth_source ∈ {E_vmatch_cw, E_vmatch_eq, E_within_cw, …} × g_case ∈ {g_zero, g_2Q26_disclosed}`),
  `I_mix_terms_3q26.csv`, `I3_geo_mix_backtest.csv`.
- `adr_v2_geomix_prereg.md` §1: *"The four-region term stays the disclosed-bucket arithmetic of
  `adr_v1_design.md` §3.3. **The two layers add.**"* — i.e. the sub-regional term is *within*-region by
  construction and is additive to the bucket term, no double count.

---

## 6. Feasibility

### (a) Stays growth by country, vintage-matched — **YES, already done, with named holes**

File: `data/processed/pitch_model_v2/adr_engine/stays_yoy_by_country_vmatch.csv`
(`country, region, q, n_cur, n_prior, n_mkts, stays_yoy_pct, quarter`).
**34 of 37 countries · 119 of 123 markets · all 14 quarters 1Q23–2Q26 complete.**
Rebuildable from `E/market_vintage_monthly.csv` + `E/market_geo.csv` (§1.5).

Holes: **japan, colombia, kenya** (insufficient vintages) and **brazil = Rio only**.
**3Q26 QTD is not in this file** (4 markets, 2 countries). For 3Q26 use `E_aug/partial_window_yoy_market
.csv` + `E_aug/partial_vs_full_quarter_market.csv` + `E_aug/monthly_nowcast_2026_market.csv` and state the
partial-window basis, the way `adrq3/I3_geo_mix_3q26.csv` does at region level.

### (b) A USD price level per market/country — **PARTIAL: 13 countries of 34**

Best source, unambiguously: `market_price_levels_usd.csv`, `quote_per_night` basis preferred,
`listed_nightly` bridged by the region-median quote/listed ratio, weighted by `n_old`.

Priced countries (non-null USD level): **united-states, france, italy, spain, united-kingdom, brazil,
mexico, australia, china(HK), japan, singapore, taiwan, thailand** — 13.
Priced but NaN (no FRED series): argentina, belize, chile.
Not in M2 at all: canada, new-zealand, and every other EMEA country (18 of 22).

Share of each region's 2Q26 **base-quarter** panel stays (`n_prior`) sitting in a priced country:

| region | priced share of base stays | biggest unpriced countries (share of region base, 2Q26 y/y) |
|---|---|---|
| NAM | **82.9%** | canada 17.1% (+16.1%) |
| EMEA | **59.0%** | portugal 6.9% (−2.6), greece 6.5% (+0.7), ireland 6.3% (+3.3), hungary 2.8% (−10.6), czech 2.5% (+1.5), germany 2.2% (−2.4), turkey 1.9% (+5.0), belgium 1.9% (−7.5), austria 1.7%, south-africa 1.4% (+7.8), netherlands 1.4%, denmark 1.4%, malta 1.2%, norway 1.0%, switzerland 0.9% (−12.5), sweden 0.5%, latvia 0.5% |
| LatAm | **61.1%** | argentina 22.4% (+24.6), chile 15.1% (+19.2), belize 1.4% |
| APAC | **70.1%** | new-zealand 29.9% (+3.0) |

Every unpriced country is imputed at the region median and contributes **exactly zero** within-region
mix. So the term as currently specified can see: US vs nothing in NAM; Italy/Spain/France/UK against each
other in EMEA; Brazil vs Mexico in LatAm; Australia vs Thailand/Taiwan/HK/Singapore in APAC. The two
fastest-growing LatAm countries (Argentina +24.6%, Chile +19.2%, both low-ADR) are invisible. Canada
(+16.1%, lower ADR than US) is invisible. That biases the measured sub-regional term **toward zero**, and
plausibly toward the wrong sign in NAM and LatAm.

Cheapest fixes, in order of value per hour:
1. **HKD instead of CNY** for hong-kong — one cell in `market_currency_map.csv`, HKD already in the fx file.
2. **Add ARS/CLP/COP/TRY/HUF/CZK/KES** — the levels already exist in `M2_new_listing_premium.csv`
   (`median_old`, native); only the FX series is missing. Buenos Aires, Santiago, Bogotá, Istanbul,
   Budapest, Prague, Nairobi would move from imputed to measured. (Requires a new FX pull — out of scope
   for this read-only pass; note that `fx_daily_extra_2026-09-22.csv` shows exactly how the extra pull is
   staged.)
3. **Extend M2 beyond 34 markets.** The raw store has 120 markets with one vintage each; a *level* needs
   only one vintage (the premium/y/y needs two). `market_summary_2026.csv` already has
   `price_median_native` for all 120 — converting *that* at a snapshot-date FX rate would take coverage
   from 13 countries to 27 (all but the 8 no-FX ones), at the cost of a single-snapshot, all-room-types,
   listed-basis level. **Guard: the three Swiss markets in that file are corrupt (0.14 / 0.15 / 0.16).**
4. **Canada** — 8 markets in the store, CAD FX available, simply absent from M2.

### (c) A country-level geo-mix term = Σ share-shift × relative price — **YES, mechanically**

All three inputs exist and the estimator is written. The pieces:

| input | file | column |
|---|---|---|
| `s_c(t−4)` base shares | `stays_yoy_by_country_vmatch.csv` | `n_prior` (normalised within region) |
| `g_c(t)` country growth | `stays_yoy_by_country_vmatch.csv` | `stays_yoy_pct` |
| `g_r(t)` region growth | derived in `geomix.py` as `Σ s_c g_c` (panel-implied, **not** the disclosed regional band) |
| `P_c` price level | `market_price_levels_usd.csv` → `country_prices()` | `usd_level`, `n_old` weights |
| `w_r` region weight | 10-K GBV share via `fx_data.gbv_shares()` / `shares_at()` | `adr/01_regional_annual.csv` `gbv_share_pct` |
| within-region component | `build_term()` returns `(mix_by_region_quarter, per_country_contrib)` | `mix_pp`, `contrib_pp = (share_new − share_base) × rel_price × 100` |
| four-region parent | `geo_mix_method_check.csv`, `geo_mix_forward.csv`, `adrq3/I/I3_geo_mix_*.csv` | additive, per prereg §1 |
| validation target | `adr/04_regional_quarterly_wide.csv`, `adr/01_regional_annual.csv` | `adr_yoy_exfx_*_pct`, `adr_computed` |
| what it should explain | `adr/07_full_decomposition.csv` | `pricing_and_subregional_mix_pp` |

**The honest caveats the note must carry:**

1. **Destination ≠ origin.** The panel measures nights *spent in* a country. Every disclosed statement
   (India +50/60%, Brazil +21/31%, Japan high-teens, Mexico high-teens, expansion markets ~2× core) is
   *origin*. An Indian guest booking Bangkok raises Thailand's destination count and lowers blended ADR —
   the term catches that. An Indian guest booking Goa is invisible, because India is not a destination in
   the panel. The prereg already concedes this in writing.
2. **No India, at all.** Not in `market_geo.csv`, not in the store, not in `market_summary_2026.csv`.
   INR exists in the FX file; that is all. The single largest named growth country in the thesis cannot
   be measured from this panel, in either direction.
3. **Coverage bias is extreme and non-random**: 34 US markets, 11 Australian, 10 Italian, 9 Spanish vs 1
   each for Japan, Thailand, Mexico, Turkey, Singapore, Taiwan, Hong Kong. Countries are weighted by
   *panel* stays (`n_prior`), which is an Inside-Airbnb artefact, not Airbnb's true country mix — the US
   is 18.3% of global panel base stays; Airbnb's NA is ~29.6% of *nights*. The term is a **relative**
   within-region object, which mitigates but does not remove this.
4. **Price levels are asking/quoted prices, not booked ADR** — the prereg says "relative-level proxy";
   levels are what the mix term needs, but the mapping from listed → quote → booked ADR is assumed
   stable within region, untested.
5. **Two price bases in one series.** `listed_nightly` (pre-2026) vs `quote_per_night` (2026, fee
   inclusive). The host-fee migration completes **15 Sep 2026 (ex-EEA) / 13 Oct 2026 (EEA+CH)** and lifts
   the *listed* price of the migrating cohort ~+14.8% with the all-in guest price unchanged
   (`M4_bottom_up_market_panel.md` §1.5). Any price level spliced across that date without the bridge
   will print a spurious jump in 4Q26 — and the bridge itself (region-median quote/listed ratio) is the
   least-tested assumption in the chain. The 1.71M-quote overlap
   (`06_quote_discount_panel.csv`, 13 cities, 2026-03→2026-08) is the only overlap sample.
6. **The residual is contested.** §5.1: the fee migration claims +2 to +5pp of the same residual.
7. **Region growth `g_r` in `geomix.py` is panel-implied**, not the disclosed regional nights band. The
   within-region mix is therefore internally consistent with the panel but not pinned to disclosure;
   reconciliation to `10_regional_panel_quarterly.csv` `*_nights_yoy_mid` is a separate check that has
   not been run.

---

## 7. Exact path list

**Stays / destination**
- `data/processed/q3nowcast/E/{market_geo,market_vintage_monthly,market_monthly_yoy,vintage_matched_nowcast,vintage_matched_nowcast_market,index_quarterly,region_monthly_index,partial_window_yoy_market,partial_vs_full_quarter_market,monthly_nowcast_2026_market,q3_2026_coverage,posting_lag_curve,survivorship_wedge}.csv`
- `data/processed/q3nowcast/E_aug/` (same 33 files, later vintage — the 3Q26 source)
- `data/processed/pitch_model_v2/adr_engine/stays_yoy_by_{country,market}{,_vmatch}.csv` ← **use these**
- `data/processed/forecast_methods/reviews_index_v2/{index_regional_vmatch_pct,index_quarterly_v2,panel_country_month,mix_weights_stay_quarter}.csv`

**Origin**
- `data/processed/overnight/10_regional_panel_quarterly.csv` (78 cols; the origin columns in §2.1)
- `data/processed/overnight/10_regional_quotes.csv` (766 filed sentences)
- `data/processed/overnight/05_crossborder_share.csv`
- `data/processed/forecast_methods/regional_kernel_v1/{od_nights_matrix,od_source_coverage,exposure,fx_basket_measured,fx_basket_scenario,public_source_extracts,registration_abstentions}.csv`
- `docs/revenue-forecast-strategy/05_backtests/X_REGIONAL_KERNEL_OD_FX.md` · `docs/thesis-kernel-topdown/lane1/X_REGIONAL_KERNEL_OD_FX.md` · `docs/revenue-forecast-strategy/lane1_briefs_v2/X_REGIONAL_KERNEL_OD_FX.md`
- `data/processed/abnb_party_size_reviews_v2_language_year_shard{0..5}.csv` · `abnb_party_size_reviews_v2_by_language_year.csv`
- `data/processed/eurostat_platform_nights_monthly.csv` · `overnight/10_eurostat_platform_monthly_latest.csv` · `eurostat_platform_nights_by_country.csv` · `eurostat_platform_vs_hotel_by_country_2019_2024.csv` · `country_lodging_nights.csv`
- `data/processed/ntto_us_inbound_monthly.csv` · `overnight/10_bench_{japan_arrivals,canada_travel}_monthly.csv` · `q3nowcast/G/raw/ntto_arrivals_monthly.csv`

**Price**
- `data/processed/pitch_model_v2/adr_engine/{market_price_levels_usd,market_currency_map,fx_daily_2026-09-21,fx_daily_extra_2026-09-22}.csv` ← **use these**
- `data/processed/adrv3/M/{M2_new_listing_premium,M2_new_listing_premium_region,M1_dump_census,M3_new_listing_share}.csv`
- `data/processed/market_summary_2026.csv` (120 markets, native, **CHF rows corrupt**)
- `data/processed/overnight/{06_price_per_unit_panel,06_quote_discount_panel,06_quote_line_items,06_price_gap_series,06_price_gap_monthly}.csv`
- `data/processed/adr/{06_price_benchmarks,06_measured_price_quarterly,06_price_residual_annual}.csv`
- `data/processed/{inside_airbnb_city_snapshots,inside_airbnb_like_for_like,insideairbnb_price_by_accommodates}.csv`
- `data/processed/adrq3/J/{J1_price_coverage,calendar_price_yoy,J2_ia_quote_sequential,J2_proxy_quarterly_panel}.csv`

**Disclosed regional ADR / mix**
- `data/processed/adr/{01_regional_annual,04_regional_quarterly,04_regional_quarterly_wide,03_annual_decomposition,07_full_decomposition}.csv`
- `data/processed/adrq3/I/{I3_geo_mix_history,I3_geo_mix_3q26,I3_geo_mix_backtest,I_mix_terms_3q26}.csv`
- `data/processed/pitch_model_v2/adr_engine/{geo_mix_method_check,geo_mix_forward}.csv`
- `research/notes/2026-09-07_adr-decomposition.md` · `analysis/src/adr/07_assemble.py:103-104`
- `docs/revenue-forecast-strategy/02_proposals/M4_bottom_up_market_panel.md` §2.4, §358
- `docs/pitch-model-v2/lines/adr_v2_geomix_prereg.md` · `analysis/src/pitch_model_v2/adr_engine/geomix.py`

---

## 8. Contradictions and defects, collected

1. **123 vs 120 vs 119 markets; 37 vs 35 vs 34 countries** — E / store+`market_summary_2026` / vmatch
   panel. Reconciliation in §1.2. `M4` §2.0 says "120 markets × 34 countries", which is neither.
2. **Hong Kong mapped to CNY** in `market_currency_map.csv` and `market_price_levels_usd.csv`; HKD is
   available in `fx_daily_extra_2026-09-22.csv`. ~10% level error.
3. **`market_summary_2026.csv` Swiss prices are corrupt**: geneva 0.14, vaud 0.15, zurich 0.16
   `price_median_native`.
4. **Japan has a price level but no stays series**; **Canada has a stays series but no price level**.
5. **`market_geo.csv` `region` is the reporting region; `market_summary_2026.csv` `region` is the
   sub-national province.** Same column name, different object.
6. **`10_regional_quotes.csv` is not a price file** despite the name.
7. **The sub-regional mix and the fee-migration bundle both claim the same residual**
   (`07_full_decomposition.pricing_and_subregional_mix_pp` +3.62pp in 2025 vs
   `C_M6_fx_takerate_timing_mechanics.md` §78 "+2 to +5pp … *is* the migration").
8. **`geo_mix_method_check.csv` `diff_pp` runs −1.69pp in 1Q23 and +0.13pp in 2Q26** — the two four-region
   methods disagree materially in the early sample. Whichever is chosen must be fixed before the
   sub-regional layer is added to it.
9. **`index_regional_vmatch_pct.csv` is not in `q3nowcast/E/`** as the brief assumed; it is in
   `forecast_methods/reviews_index_v2/` and is in **percent** keyed by `qi`.
10. **`adr/07_full_decomposition.csv` 2022 row is self-flagged** `"low -- does not reconcile to the
    independent regional panel"` (`reconciliation_gap_pp` 1.23). Do not quote the 2022
    `pricing_and_subregional_mix_pp` of +10.73 without that caveat.
