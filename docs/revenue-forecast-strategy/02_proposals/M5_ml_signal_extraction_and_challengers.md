# M5 — ML/AI as Signal Extraction, Challenger and Ensembler (Never the Primary Model)

**Lens owner:** ML/AI layer. **Target variable hierarchy:** (1) 3Q26 guide validation vs the frozen card (`data/processed/overnight/20_frozen_q3_2026.csv`); (2) the **4Q26 guide range Airbnb will set on ~5 Nov 2026** (guide_mid, guide_width); (3) the **FY27 guide Airbnb will set ~Feb 2027** (first FY27 revenue-growth statement, in the guidance-ledger's own qualitative buckets plus a quantitative posterior); (4) FY27 revenue vs Street $15.73–15.76bn. This is a stack of five extraction/challenger/ensembling modules that plug into — and never replace — the driver model (`model/ABNB_driver_model.xlsx`, `analysis/src/overnight/13_driver_model.py`).

---

## 1. Thesis of the method (five lines)

We do not build a seventh nights/ADR forecaster. We build (a) a point-in-time, item-level LLM extraction pipeline over the 194-statement guidance ledger and 23 transcripts that converts *how* management talks about a metric into a feature predicting *how much cushion* it will bank — a redesign of the team's failed call-level tone test (n 23, 132 features, no survivor) at the statement level (n≈194, one feature per statement, hierarchically pooled to the call); (b) three text-derived KPI proxies (party size — already built — cross-border share, LOS mix) mined from the 67.5M-review store to **recover series Airbnb stopped disclosing in 2023–24** and extend them through 2Q26 and beyond, calibrated on the overlap years so the extension is a measured, not assumed, series; (c) a repeat/matched-listing hedonic price index off the 1.71M fee-inclusive quotes as the first true like-for-like ADR benchmark, aimed straight at the +3.6pp "jointly unidentified" residual in `research/notes/2026-09-07_adr-decomposition.md`; (d) a monotone-constrained GBM and one zero-shot foundation time-series model run head-to-head against AR(1) and guide+cushion under nested expanding-window CV, reported honestly as calibration/interval tools at n≈24 quarters, not point-forecast winners; (e) a Bayesian model-averaging stack across this lens and the other five, with conformal intervals on the pinball loss for *surprise*, whose weights are learned only on pre-print information. It should beat the team's status quo not on point accuracy — nothing beats AR(1) at n=24 (`research/notes/overnight/20_temporal-validation.md`) — but on **what varies at the judged catalysts**: guide language, mix composition and calibrated interval width, which the current driver model has none of.

---

## 2. Formal specification

### 2a. Guidance-language extraction → cushion model

Unit of analysis: one **statement** `s` in one **call** `c` (call = print date), not one call. Base table: `data/processed/overnight/02_guidance_ledger.csv` (195 rows incl. header, columns `guide_id, print_quarter, print_date, target_period, horizon_quarters, metric, guide_type, value_low, value_high, value_mid, unit, direction, comparator_value, actual, outcome, distance_from_mid, cushion, pct_distance_from_mid, source, source_file, verified, quote, note, revised_later_by, revision_delta` — verified by `head -5`). For each statement extract, via a structured LLM pass over the `quote` field (already present verbatim, so this is a re-annotation not a re-scrape) and the surrounding transcript paragraph pulled from `data/raw/transcripts/{ir,sa}/<q>.txt` (paths documented, gitignored — verified in `analysis/src/transcript_analytics.py` header, 23 calls 4Q20–2Q26, 15 IR-sourced + 8 stockanalysis.com):

- `spec_k(s) ∈ {0,1}`: is the statement a **quantified range** (`value_low`/`value_high` populated) vs a **bucket word** ("low double-digit") vs pure **qualitative direction** — this is already encodable from `guide_type` in the CSV without new LLM calls for that one feature; the LLM pass is for the four below.
- `hedge_k(s) ∈ [0,1]`: density of hedging tokens ("approximately", "we expect", "should", "we currently anticipate") per 100 words of the statement's paragraph.
- `fxquant_k(s) ∈ {0,1}`: does the statement explicitly quantify an FX effect in percentage points (the recurring "inclusive of an approximate three percentage point FX tailwind" construction, confirmed present at the 3Q26 guide in `research/notes/overnight/29_q4-fy27-bridge.md` and the 2Q26 call).
- `decline_k(s) ∈ {0,1}`: was a specific follow-up analyst ask on this metric declined or answered qualitatively — this reuses the already-built `abnb_declined_to_quantify.csv` output of `analysis/src/transcript_analytics.py` (hand-verified excerpts checked verbatim against transcript) rather than re-deriving it.
- `comp_k(s) ∈ [0,1]`: forward/backward comp language density ("tougher comps in the back half", "anniversary") — the RNPL-lap language the model needs (`research/notes/2026-09-04_management-timeline.md`).

**Model, hierarchical pooling to fix the n=23 problem:**

cushion_c = α + Σ_k β_k · mean_{s∈metric=revenue,c}(feature_k(s)) + u_c, u_c ~ N(0, τ²)

estimated as a partial-pooling (random-intercept) Bayesian regression in PyMC with `c` (call) as the grouping factor and **statement**, not call, as the base unit feeding the group means — so the effective n for β_k is the ~194 statements (159 scoreable per the ground-truth digest) shrunk through 23 groups, not 23 independent draws. This is exactly the fix the ground-truth digest names as missing from the failed tone test: "item-level rather than call-level features, PIT, hierarchical pooling." Priors: β_k ~ N(0, 0.5²) (weakly informative on a cushion measured in single-digit percentage points; the trailing-8 median cushion is +1.79%, so a coefficient near ±1 already spans the observed range — a tight prior is doing real work at this n). Target `cushion_c` is `02_guidance_ledger.csv`'s own `cushion` field for the revenue-midpoint row of each call — no new label engineering.

**Identification:** the *only* thing that can identify β_k is genuine within-call, within-metric variation in how hedged/quantified/comp-laden each sentence is, which the ledger's `verified=True` quotes make auditable one row at a time — every β_k is traceable to specific quotes. This is not asking text to predict a number the text doesn't discuss; it is asking whether the *manner* of a guide correlates with how much room management left itself, which is a stated management habit ("relatively in-line year-over-year" for take rate almost always undershoots — FY24 SBC guided +20% then +25%, delivered +30.8%, ground-truth digest `guidance_policy`).

**Overlap avoidance:** each statement contributes to at most one metric-call cell; the hierarchical model shares only the *residual* variance structure across calls, never pools across metrics (revenue cushion and take-rate cushion are modeled as separate `y_c` vectors with a shared `c` grouping only through `τ`, not through `β`). No double counting with the Structural/Guidance-game lenses because this model's only output is a **scalar cushion-shift feature** handed downstream (Section 9), never a revenue number itself.

### 2b. Text-derived KPI recovery from the review store

Base method already built and validated in-repo: `analysis/src/abnb_party_size_reviews_v2.py` / `_aggregate.py`, outputs `data/processed/abnb_party_size_reviews_v2_decomposition.csv` (verified: columns `period0, period1, ips0, ips1, change, mix_effect, within_effect, fam0, fam1, fam_mix, fam_within` — an implied-party-size Oaxaca-style mix/within decomposition already exists for 2014-16 vs 2023-25) and the by-market/quarter/language shards (`abnb_party_size_reviews_v2_bucket_quarter_shard0-5.csv`, `_market_month_shard0-5.csv`, `_language_year_shard0-5.csv`, `_seasonal_index.csv`, `_global_month.csv`). We **extend, not re-derive**, this pipeline to two more series with the identical review-language-signal architecture:

- **Cross-border share proxy**: `crossborder_hat(m,q) = f(reviewer_locale_language(m,q) ≠ host_country_language(m))`, i.e. the share of reviews at market `m` in quarter `q` written in a language inconsistent with the local language, already partially computed in the `_language_year` shards (need only re-cut to quarterly and to a binary cross-border proxy instead of a party-size feature). Calibration target: the disclosed **cross-border share, 46% of gross nights at 1Q24** (last point, `02_disclosure_changes.csv` per ground-truth digest) — a single calibration anchor, so this is a **level-anchored proxy**, reported with an explicit calibration-uncertainty band, not a re-disclosure.
- **LOS mix proxy**: median reviewer-implied stay length from the `booking_curves_by_market.csv` (verified: `country, region, market, snapshot_date, horizon, listing_nights, listings, blocked_nights, blocked_rate, median_min_nights` — 601 rows, 120 markets, single June/July 2026 vintage) combined with the **existing measured LOS bucket work** in `analysis/src/adr/14a-14c` (bucket shares disclosed 2021-22, solved off ALOS 2023-25, ratios 1.00/0.966/0.852 — status "measured" per the model audit) — the review store adds only the *forward* extension past 2Q26 since Inside Airbnb's calendar files carry no price after the 2026 schema change (verified caveat: "2026 calendars carry NO price column").

**Identification and calibration protocol (mandatory, avoids the Google-Trends failure mode):** each recovered series is fit to the **overlap window only** (pre-1Q24 for cross-border, pre-1Q24 for LOS, pre-2Q26 for party size) via a single linear recalibration `y_disclosed = a + b·y_text_proxy`, with `(a,b)` frozen at the last disclosed point and **never re-fit** on later data — this is the walk-forward discipline the Google Trends test lacked (`research/notes/overnight/08_altdata-index-and-backtests.md`: 432 tests, mean WF RMSE 3.05x naive, "three times worse than last quarter's number is noise"). If `b`'s 90% credible interval (from a Bayesian errors-in-variables fit, since both series are noisy) excludes a wide band around 1, the series is **not used as a disclosure-replacement**, only as a *directional* corroborator inside the Structural lens's regional nights build. This is a strict pre-registration: we know two of three of these attempts may fail exactly as the 13-city Inside Airbnb panel failed on **grain**, not concept (`n_flagged_r05_perm05 = 0 in both windows` — the reopenable, grain-fixed version of that failure per model-audit recommendation 8).

### 2c. Repeat-listing hedonic price index (the like-for-like ADR benchmark)

This directly targets the +3.6pp jointly-unidentified 2025 ADR residual (`research/notes/2026-09-07_adr-decomposition.md §3, §4.3`) and the model-audit's overlap risk #5 (party size / unit size / LOS all drawn from one Inside Airbnb universe with a documented re-basing history, 3.25→2.5 for size, 2.5→2.2 for LOS).

Specification — **one log-additive hedonic, estimated jointly**, per model-audit recommendation 5:

ln(price_quote_itmc) = γ₀ + γ₁·ln(capacity_i) + γ₂·bedrooms_i + γ₃·LOS_bucket(t) + δ_m + θ_c(m) + ε_itmc

on `data/processed/overnight/06_quote_line_items.csv` (verified: 77 rows aggregated, but underlying 1.71M fee-inclusive quotes per the ground-truth digest) with `δ_m` a **market fixed effect** and `θ_c(m)` a **country-within-market fixed effect where the 120-market current Inside Airbnb store overlaps** (982k listings — this is where the "current 120-market store" gap-fill from Phase 1's own recommendation gets used: "extend the 29-market size-mix panel using the current 120-market Inside Airbnb store already on disk"). The **repeat-listing** refinement: restrict a second specification to `listing_id`s observed in ≥2 of the 168 Inside Airbnb dumps × 13 cities (Dec 2022–Aug 2026, `06_ia_dump_metrics.csv`/`08_ia_city_yoy.csv`, 169 rows) with a **listing fixed effect** replacing `δ_m·θ_c(m)`, which nets out *all* time-invariant listing quality and isolates pure like-for-like price drift — this is the closest thing to a country-level ADR series Airbnb will never disclose. Because both specifications share `γ₁, γ₂, γ₃`, size/LOS coefficients are estimated **once** and shift-shared into both the mix decomposition and the residual bound — killing the double-count risk the model audit flags (bedrooms-per-log-capacity mismatch 1.27 vs 1.37 docstring; fixed here by refitting jointly rather than reusing two prior point estimates).

**Overlap/orthogonality by construction:** because size (`γ₁,γ₂`) and LOS (`γ₃`) are co-estimated with market/listing fixed effects **in the same regression**, the residual (`ε`, aggregated to a quarterly market-level index) is *by construction orthogonal to size and LOS composition* — it is the pricing-plus-unmeasured-mix term, reported as a **bound**, not a point estimate, exactly as Phase 1's cheapest-fill recommendation specifies ("bounding sensitivity, not a point estimate").

### 2d. Challenger forecasters — calibration, not point accuracy

Panel: `data/processed/overnight/02_kpi_panel_quarterly.csv` (verified 25 rows incl. header, 119 columns, 3Q20–2Q26). At n≈24 quarterly observations minus burn-in, no model with >2-3 effective parameters can be expected to beat AR(1)/naive on point RMSE — this is exactly what `research/notes/overnight/20_temporal-validation.md` already found for every prior challenger. We therefore run three challengers **stated explicitly as calibration and interval instruments**, never as the point forecast:

1. **Monotone-constrained gradient boosting** (LightGBM, `monotone_constraints`) on nights_yoy and adr_exfx_yoy with ≤4 features (lagged KPI, the FX-broad-USD survivor, the funds-held-growth survivor, season dummy), constraint: nights_yoy non-decreasing in funds-held growth and non-increasing in USD broad y/y (sign priors from the two *validated* survivors — funds-held slope 0.60/r 0.89, and broad-USD→ADR-FX r 0.96-0.99 per `research/notes/overnight/08_altdata-index-and-backtests.md`). Monotonicity is the leakage control: it prevents the tree from fitting sign-unstable noise the way the failed composite NNLS indexes did (three indexes, all lost to AR(1), audit note: "combining features that individually lose to AR(1) at n≤18 cannot win").
2. **One zero-shot foundation time-series model** (Amazon Chronos-T5 or Google TimesFM, whichever has a working local/HF checkpoint — no fine-tuning, since n=24 cannot support it) run purely zero-shot on the univariate nights/ADR series, reported only for **predictive interval width and coverage**, not point RMSE — the honest expectation, stated up front, is that it roughly matches AR(1) point accuracy (these models are trained for exactly this regime: short series, no covariates) but may deliver **better-calibrated quantiles** than a naive normal-error band around AR(1), which is the actual product a Citadel PM needs for a scenario tree.
3. **Bayesian structural time series** (`statsmodels.tsa.UnobservedComponents` or PyMC state-space) with a local-level + explicit seasonal-take-rate component, encoding the seasonal identity directly: `take_rate_q = τ_LTM + seasonal_offset(quarter)` with offsets pinned near the disclosed 2023-25 means (9.2/13.1/18.3/14.0, LTM 13.2%) as informative priors — **this is the estimation of the take-rate mechanism the model audit says is missing** (recommendation 1), done as a Bayesian layer that reports a posterior over the seasonal-offset drift rather than a hard carry-forward.

**All three challengers are evaluated in nested nested expanding-window CV** (outer loop: origin quarter walks 1Q24→2Q26 i.e. ~10 origins after a minimum 12-quarter training burn-in; inner loop: hyperparameter selection on data strictly before the outer test origin) against three baselines: naive AR(1) on nights_yoy, `guide_mid + trailing cushion` (the survivor method, 1.1% mean error per ground-truth digest), and Street consensus at print (`04_consensus_at_print.csv`, verified 24 rows). Reported metrics: RMSE ratio to naive (the team's own convention, e.g. 0.44x for the FX/ADR survivor), CRPS for interval calibration, and PIT-histogram calibration checks (are the realized values uniformly distributed under the predicted CDF — the correct falsification test for "is this model's uncertainty honest", which point-RMSE alone cannot answer and which a Monte-Carlo-only proposal would never report).

### 2e. Bayesian model averaging / stacking across the six lenses

Let each lens `j ∈ {structural mix, nowcast tracker, guidance game, bottom-up markets, ML challengers, FX/take-rate/timing}` produce a predictive distribution `p_j(revenue_{q+1})` (or, pre-print, `p_j(guide_mid_{q+1})`). The ensemble is:

p_ens(y) = Σ_j w_j(x) · p_j(y), Σ_j w_j = 1, w_j ≥ 0

with weights **learned only on the pre-print information set** `x` available at each historical guide date (point-in-time discipline, Section 4) via a **stacked generalization** on the **pinball loss at five quantiles (10/25/50/75/90)** — chosen because the decision-relevant object is the *guide range*, a two-sided interval, not a point, and pinball loss is the proper scoring rule for quantiles the way CRPS is for full distributions. Weight-learning uses a **leave-one-quarter-out** cross-validated stacking regression (non-negative least squares on quantile losses, `scipy.optimize.nnls`, the same tool the team's own composite-index attempt used — but here disciplined by covering *distributions* pooled from six structurally different lenses rather than *point features* competing on one target, which is the actual reason NNLS failed before: "NNLS adds parameters a 20-observation sample cannot support" when the inputs are noisy point features; pooling well-specified *distributions* from mechanistically different models is a different, better-conditioned problem). **Conformal calibration** wraps the stack: split-conformal on the last 6 held-out quarters computes a single scalar inflation factor `κ` such that `[q_10 - κ, q_90 + κ]` achieves nominal 80% coverage empirically — this is what replaces "plain Monte Carlo" with a **distribution-free, finite-sample guarantee**, the single largest methodological upgrade this lens offers over a scenario-probability tree with hand-set weights.

**No leakage, checklist enforced at code level (Section 4):** weights `w_j(x)` and the conformal calibration set are both restricted to information dated strictly before each historical guide date; the six lenses' own internal parameters (e.g., the driver model's `REGIONAL_G` dictionary) must also be the **as-of-that-date** version, which requires versioning `model/assumptions.md` and the driver-model CSVs by print date — a new requirement this lens imposes on the other five, flagged explicitly in Section 9.

---

## 3. Data map (every path opened and verified this session)

| Input | Path | Grain | Verified | External? |
|---|---|---|---|---|
| Guidance ledger | `data/processed/overnight/02_guidance_ledger.csv` | statement | `head`/`wc -l`→195 rows, columns confirmed incl. `quote`, `cushion`, `verified` | No |
| Transcript raw text | `data/raw/transcripts/{ir,sa}/<q>.txt` (gitignored) | call | header of `analysis/src/transcript_analytics.py` documents 23 calls, 2 sources, exact IR CDN URLs | No (already downloaded per script; re-run `download_abnb_transcripts.py` if missing locally) |
| Declined-to-quantify table | `data/processed/abnb_declined_to_quantify.csv` (output of `transcript_analytics.py`) | analyst ask | script confirmed to hand-verify every excerpt against transcript | No |
| Party-size review decomposition | `data/processed/abnb_party_size_reviews_v2_decomposition.csv` + 6 shards each of `_bucket_quarter`, `_market_month`, `_language_year` | market-quarter / market-month / language-year | `head` confirmed columns `ips0, ips1, mix_effect, within_effect, fam_mix, fam_within` | No |
| Booking curves | `data/processed/booking_curves_by_market.csv` (601 rows) + `booking_curve_daily.csv` | market×snapshot×horizon | `head` confirmed `median_min_nights`, `blocked_rate`; single June–Jul 2026 vintage — NOT occupancy | No |
| Quote line items (hedonic base) | `data/processed/overnight/06_quote_line_items.csv` (77 aggregated rows / 1.71M underlying quotes) | quote, aggregated by city-dump | `head` confirmed `li_nightly_subtotal, li_discounted_subtotal, field_discount_amount` etc. | No |
| Inside Airbnb 120-market current store | `raw_expansion/` (315 files, ~9.9GB, sibling folder) | listing/calendar/review | per Phase 1 digest, 982k listings, 588M calendar rows; **calendars have no price in 2026 schema** | No (already acquired) |
| Consensus at print | `data/processed/overnight/04_consensus_at_print.csv` (24 rows) | print | `head` confirmed full column set incl. `guide_vs_street_pct`, `excess_1d/5d/20d_pct` | No |
| KPI panel | `data/processed/overnight/02_kpi_panel_quarterly.csv` (25 rows, 119 cols) | company-quarter | `wc -l` confirmed | No |
| Prediction ledger / test scoreboard | `data/processed/overnight/20_prediction_ledger.csv` (392 rows), `08_test_scoreboard.csv` (11 rows) | test | `head` confirmed columns incl. `bl_guide_plus_cushion`, `consensus_point_in_time` — this is the harness the challengers plug into | No |
| Macro sensitivities (survivor coefficients) | `data/processed/overnight/05_macro_sensitivities.csv` | macro×target | `head` confirmed `usd_broad → adr_fx_effect` r=−0.95, perm p=0.001, confidence=high; the sign prior for the monotone GBM | No |
| Elasticities (hedonic anchors) | `data/processed/overnight/06_elasticities.csv` | sourced sensitivity | `head` confirmed capacity +0.49%, bedroom +15.1%, rating 4.9+ +9.5% | No |
| Frozen 3Q26 card | `data/processed/overnight/20_frozen_q3_2026.csv` | pre-registered | per digest, nights +10.2%, ADR +3.8%, revenue $4,801M | No |
| 67.5M-row review store | documented in `Theo Data/data_review_2026-09-07/DATA_MAP.md`, **lives on external volume `/Users/theomachado/abnb_scratch`, NOT in the reviewed OneDrive workspace** | review | **not directly queryable from this repo checkout** — must be confirmed present before Week-1 planning | Possibly (verify volume mount) |

**External data needed:**
1. **Zacks/Yahoo/S&P KPI-level consensus (nights, ADR, EBITDA)** 2-3 days pre-5-Nov-print, free, per Phase 1's own plan — needed as the Street baseline for the ensemble's pinball-loss scoring at the one live catalyst inside the window.
2. **Confirm mount/copy of the 67.5M-review store** (`/Users/theomachado/abnb_scratch`) into a location this Python environment can DuckDB-query — if genuinely external-volume-only, budget Day 1 of Week 1 to resolve this before any review-text work starts; if unavailable, the smaller party-size CSVs already in `data/processed/` are a viable fallback for (2b) with reduced n.
3. Optional: Fiscal.ai free/$39 tier for KPI-level consensus depth (nights consensus at 15-20 analysts vs Zacks' 5-6) — 4hrs setup, per Phase 1 altdata landscape, improves the ensemble's Street-baseline precision but not required to ship.

---

## 4. Estimation and validation

**Software:** Python end-to-end for reproducibility by undergraduates — `pymc` (hierarchical cushion model, Bayesian structural time series), `lightgbm` (monotone GBM), `statsmodels` (UnobservedComponents fallback, and OLS diagnostics), `linearmodels` (fixed-effects hedonic — `PanelOLS` with market and listing FE, clustered SEs by market), `mapie` or hand-rolled split-conformal (`numpy`) for the conformal wrapper, `duckdb` for all review-store and Inside-Airbnb-scale queries (Section 6). A Chronos/TimesFM zero-shot call needs one GPU session (Colab T4 sufficient for a 24-point series; no fine-tuning, so no training compute budget) — this is explicitly the only GPU need in the entire lens.

**Point-in-time protocol (mandatory, and the team's own hard-won standard):** every historical "as of guide date `t`" feature must use only (a) transcript/letter text dated ≤ `t`, (b) KPI panel rows for quarters reported ≤ `t`, (c) consensus vintage dated ≤ `t` (the ground-truth digest flags exactly this trap: "the repo currently risks mixing the $4,610m LSEG figure that set the 6 Aug feature with the later $4,740m Zacks vintage" — this lens must not repeat it), (d) review-store text with a `review_date` ≤ `t` (reviews are naturally dated, so PIT filtering on the store itself is trivial and this data source is *more* PIT-safe than most in the repo, not less). The 20_prediction_ledger.csv schema (`decision_time`, `last_training_label_quarter`, `last_training_label_known_at`, `consensus_vintage_revenue`, `consensus_point_in_time`) already encodes this discipline — every new ledger row this lens produces must populate the same columns, which is a strong practical control since a malformed row is visually obvious next to 392 correctly-formed ones.

**Sample-size honesty and power at n≈20:** for the guidance-cushion hierarchical model, effective n is ~194 statements in 23 groups — a random-intercept model at this size can identify a **group-level variance** (τ²) and a **small number (≤5) of population-level slopes** with wide but usable credible intervals; it cannot support >5 predictors without the priors doing essentially all the work, which is why Section 2a caps at 5 features. For the KPI challengers, n≈24 quarters gives, at conventional 80% power and α=0.05, detectable standardized effect sizes no smaller than ~0.9–1.0σ in a simple regression — i.e., only a **large, mechanical** relationship (like the FX-on-ADR survivor, |r|≈0.95) is powered to be found; anything in the 0.3–0.5 correlation range that the team's macro sweep kept surfacing (`usd_broad → nights_yoy`, r=0.32, perm p=0.27, confidence "none" per `05_macro_sensitivities.csv`) is **not** powered to be distinguished from noise at this n, and this lens reports every such correlation with its permutation p-value and explicitly declines to build on anything below the team's own Bonferroni-clean bar.

**Baselines every model must beat, on the RMSE-ratio-to-naive convention the team already uses:** (1) AR(1)/naive-last on the KPI itself; (2) `guide_mid + trailing-8 cushion` (1.1% mean error, the best point predictor of *level* the team has found); (3) Street consensus at print. On *surprise* (not level), baseline (2) is explicitly the worst performer in the team's own tests (RMSE 2.0-2.4pp vs 1.33pp trailing-4) — so the challenger stack's real job is to beat baseline (2) specifically on surprise-relevant quantities (guide-vs-Street gap, cushion), where the team has *not yet* found anything that beats a trailing-4 mean, leaving this genuinely open ground rather than re-treading the closed "predict surprise from macro" ground that failed (Task A, `research/notes/predictive/`: pred_sd/actual_sd 0.14-0.33 on 16 of 17 pairs — every winner was an intercept-shift artifact).

**Why the team's negative results do NOT condemn this design — and which parts they DO condemn:**
- **Condemned, correctly, and not reopened here:** any attempt to forecast day-of-print stock *surprise* from macro, tone, or peer read-across at n≈20 with dozens of candidate features (management-tone: 1,677 turns × 132 features, n=23, no survivor — this lens uses ≤5 hierarchically-pooled features specifically because of that failure, not despite it). Composite NNLS indexes on point features are also condemned and not reused for KPI point-forecasting; NNLS is reused here *only* on stacking well-specified predictive distributions across six structurally different lenses, a different-conditioned problem, and is explicitly flagged as such.
- **Not condemned, because untested or tested at the wrong grain:** (i) item-level (not call-level) text features on the guidance ledger — never tried; (ii) review-text KPI recovery at market-month grain (thousands of observations) — the 13-city Inside Airbnb panel failure was a **coverage** failure (13 of ~220 markets, `n_flagged=0` in both windows) not a text-mining-concept failure, and the review store's 120-market, multi-year span is the fix Phase 1's own recommendation 8 names; (iii) a repeat-listing hedonic on 1.71M *quotes* — the team has only ever run city-dump-level aggregates, never a listing-fixed-effects panel; (iv) foundation time-series models for **interval calibration** — never attempted, and explicitly not claimed to beat AR(1) on point accuracy, so it cannot be "condemned" by a test that only ever measured point RMSE.

---

## 5. Outputs

For **3Q26** (already printing before the finals? No — 5 Nov, after finals, but scoreable as the pitch's first live falsification): posterior predictive distribution over `revenue_3Q26` from the ensemble, quoted as a 10/25/50/75/90 quantile fan, benchmarked against the frozen card ($4,801M, +17.2%) and Street ($4,740M/$4,737M consensus per `04_current_consensus.csv`/Alpha Vantage 11 Sep pull). The output is not "we think $X" but **P(revenue ≥ Street mid) and P(guide-implied 4Q26 range < $3.10bn)** — decision-relevant probabilities a PM can trade, computed from the conformal-calibrated stack, not a symmetric Monte Carlo cloud.

For the **4Q26 guide (5 Nov)**: a **scenario tree with data-dependent (not hand-set) branch probabilities** — branches defined by (i) whether the 3Q26 print beats/meets/misses the guide top, using the base rate 15/19 above-top as the branch prior, updated via the hierarchical cushion posterior's `c=24`(3Q26) draw; (ii) whether management's language on RNPL-lap/comp difficulty (measured live via the same LLM-extraction pipeline applied same-day to the new transcript) scores above or below the historical `comp_k` mean — this is the concrete mechanism (Section 2a) turned into a real-time signal. Output: posterior over `guide_mid_4Q26` and `guide_width_4Q26`, compared to the team's FX-anchored bridge ($3,111M base) and Street ($3,200M/$3,160M inferred).

For **FY27 guide (Feb 2027, after finals — a forward-looking deliverable for judges to score the team's process, not the print)**: the ensemble's posterior over the **first FY27 revenue-growth bucket word** Airbnb will use (discretized to the ledger's own historical vocabulary: "at least low double-digit" / "low-to-mid-teens" / "at least mid-teens" / "at least X%"), derived by mapping the continuous FY27 revenue posterior through the **empirical mapping table already implicit in `02_guidance_ledger.csv`** (which bucket word corresponds to which realized range, historically) — this operationalizes model-audit recommendation 7 ("model guide_mid_{q+1} = f(operating state, cushion history, FX already realised)") with an explicit categorical output a judge can check in Feb 2027.

For **FY27 revenue vs Street ($15.73–15.76bn)**: the ensemble posterior median and 80% interval, explicitly decomposed into **which of the six lenses is pulling the ensemble away from Street** — mechanically, since the FX-on-ADR survivor is display-only in the current driver model (Section on overlap risks, model audit) but *live* in this lens's hedonic residual and challenger nights model, **the mechanism by which this lens's view can differ from Street is precisely the channels Street's models (per the "worst predictor of surprise" finding on guide+cushion) under-weight: mix-adjusted like-for-like pricing (2c) and the RNPL-lap language signal (2a)**, not a different macro view — the team's own tests killed the macro channel for everyone, Street included.

**Uncertainty representation:** conformal-calibrated quantile fan (Section 2e) plus the discrete guide-bucket posterior (a genuine scenario tree with probabilities that update on realized text and KPI data) — explicitly *not* a Monte Carlo cloud built from independently sampled "bear/base/bull" assumptions, and explicitly not a SARIMAX confidence band.

---

## 6. Minimal code skeleton (≤80 lines, PyMC hierarchical cushion model — the highest-novelty piece)

```python
"""M5.2a — hierarchical guidance-cushion model. Input: 02_guidance_ledger.csv (verified 195 rows).
Run: python m5_cushion_model.py
"""
import pandas as pd, numpy as np, pymc as pm

LEDGER = "data/processed/overnight/02_guidance_ledger.csv"
FEATS  = "data/processed/m5_statement_features.csv"  # LLM-extraction output, Section 2a; one row per guide_id

df = pd.read_csv(LEDGER)
rev = df[(df.metric == "revenue_musd") & df.guide_type.notna() & df.cushion.notna()].copy()
feats = pd.read_csv(FEATS)  # cols: guide_id, hedge, fxquant, decline, comp   (0/1 or [0,1])
rev = rev.merge(feats, on="guide_id", how="left").fillna(0.0)

# PIT check (mandatory): drop any statement whose feature file post-dates its own print_date
assert (pd.to_datetime(feats.get("extraction_asof", rev.print_date)) <=
        pd.to_datetime(rev.print_date)).all(), "leakage: feature dated after its own print"

calls, call_idx = np.unique(rev.print_quarter, return_inverse=True)
X = rev[["hedge", "fxquant", "decline", "comp"]].to_numpy()
y = rev["cushion"].to_numpy()

with pm.Model() as cushion_model:
    beta   = pm.Normal("beta", 0, 0.5, shape=X.shape[1])
    alpha  = pm.Normal("alpha", rev.cushion.mean(), 1.0)
    tau    = pm.HalfNormal("tau", 1.0)
    u      = pm.Normal("u", 0, tau, shape=len(calls))          # call random intercept
    sigma  = pm.HalfNormal("sigma", 1.0)
    mu     = alpha + X @ beta + u[call_idx]
    pm.Normal("obs", mu, sigma, observed=y)
    trace = pm.sample(2000, tune=1000, target_accept=0.9, chains=4)

# Leave-one-call-out expanding-window check (Section 4): refit on calls < holdout, predict holdout
def loo_expanding(rev, min_calls=8):
    errors = []
    ordered = sorted(rev.print_quarter.unique())
    for i in range(min_calls, len(ordered)):
        train = rev[rev.print_quarter.isin(ordered[:i])]
        test  = rev[rev.print_quarter == ordered[i]]
        if train.empty or test.empty:
            continue
        # simple pooled-OLS refit per fold for speed; full PyMC refit for the final report
        Xtr, ytr = train[["hedge","fxquant","decline","comp"]].to_numpy(), train["cushion"].to_numpy()
        b, *_ = np.linalg.lstsq(np.c_[np.ones(len(Xtr)), Xtr], ytr, rcond=None)
        Xte = np.c_[np.ones(len(test)), test[["hedge","fxquant","decline","comp"]].to_numpy()]
        pred = Xte @ b
        errors.append(np.abs(pred.mean() - test["cushion"].mean()))
    naive_err = rev.groupby("print_quarter")["cushion"].mean().diff().abs().dropna().mean()
    return np.mean(errors), naive_err  # report as ratio-to-naive, team's convention

wf_err, naive_err = loo_expanding(rev)
print(f"walk-forward mean err {wf_err:.3f} vs naive {naive_err:.3f}  ratio={wf_err/naive_err:.2f}x")

summary = pm.summary(trace, var_names=["alpha", "beta", "tau"])
summary.to_csv("data/processed/m5_cushion_posterior_summary.csv")
```

The hedonic (2c), monotone-GBM (2d), and conformal stack (2e) follow the same shape (`linearmodels.PanelOLS` with `EntityEffects` for the fixed-effects hedonic; `lightgbm.LGBMRegressor(monotone_constraints=[...])` for the GBM; `numpy`-only split-conformal for the wrapper) and are omitted here for the 80-line budget — each is <40 lines given the data is already in `data/processed/`.

---

## 7. Three-week build plan (3-4 undergraduates)

**Week 1 (day-level):**
- **Day 1:** Confirm review-store mount (`/Users/theomachado/abnb_scratch` per DATA_MAP.md) is queryable via DuckDB; if not, fall back to `data/processed/abnb_party_size_reviews_v2_*` shards for a reduced-scope 2b. Pull Zacks/Yahoo KPI-level consensus (external data item #1). Assign owners: Person A = 2a (cushion model), Person B = 2b/2c (text KPI recovery + hedonic), Person C = 2d (challengers), Person D (if 4th) = 2e (stacking) + repo plumbing.
- **Day 2:** Person A builds the LLM-extraction prompt against `02_guidance_ledger.csv`'s `quote` field (194 statements — one batched call, est. <$5 at current API pricing, no fine-tune) producing `m5_statement_features.csv`; spot-check 20 statements by hand against source `.htm`/transcript text.
- **Day 3:** Person B stands up DuckDB queries over the review store (or fallback shards) for cross-border and LOS proxies; Person C pulls `02_kpi_panel_quarterly.csv` into the nested-CV harness skeleton, wires in the three baselines.
- **Day 4:** Person A runs the PyMC hierarchical model (skeleton above) + LOO-expanding check; Person B runs the calibration-window fit (`y_disclosed = a + b·y_proxy`) for both recovered series and reports the credible interval on `b`.
- **Day 5:** Person C fits monotone GBM + runs one Chronos/TimesFM zero-shot pass (Colab); Person D drafts the conformal wrapper on whatever lens outputs exist so far (even 2-3 lenses); **team sync — cut anything not producing a defensible number by EOD Friday.**

**Milestones after Week 1:**
- **End Week 2:** Hedonic (2c) estimated on `06_quote_line_items.csv` + repeat-listing subsample; cushion model's out-of-sample cushion forecast produced for the still-pending 3Q26 print as a genuine ex-ante test; ensemble stack assembled across whichever of the 6 lenses have delivered predictive distributions by then (degrade gracefully — a 3-lens stack with correct weights beats a 6-lens stack rushed).
- **End Week 3:** Freeze all four outputs (Section 5) in a single scored table alongside the frozen 3Q26 card; write the 2-page memo section (≤1 paragraph — this lens is a modifier to the Structural lens's headline number, not a competing headline); final gut-check: does every reported number trace to a path opened this document names.

**What to cut under time pressure, in order:** foundation time-series model (2d.2) first — genuinely nice-to-have for calibration, not decision-critical; the repeat-listing hedonic subsample (2c's second spec) second — the market-FE version alone still resolves most of the residual bound; the FY27 categorical-bucket mapping (Section 5's third output) third — it is a Feb-2027 deliverable anyway and can be described in prose without a fitted model if time runs out.

---

## 8. Failure modes and hostile-judge attack lines

- **"You're just fitting tone to itself — cushion IS the outcome of how confident they sound, tautological."** Response: the features are coded from *language structure* (hedge density, quantify/not, decline/not), not from a human tone-rating; the test is whether *ex-ante* structural features (available the moment the call transcript exists, before the next print) predict the *ex-post* cushion measured two-plus months later — a genuine forecasting claim, and the walk-forward ratio-to-naive (skeleton above) is reported precisely so a null result is visible, not hidden.
- **"n=23 calls is still n=23 no matter how you slice the sentences."** Response: correct for the *between-call* variance component (τ), which is why we report τ's credible interval honestly and do not claim to have "solved" the small-n problem — we claim only that the **within-call, sentence-level** coefficients (β_k) are identified off ~194 independent text draws, a materially different (and larger) information set than the team's prior call-level 132-feature sweep, which is the specific, falsifiable, narrower claim being made.
- **"The review-store KPI recovery is just Google Trends with extra steps — free text as a proxy for a hard number is exactly what already failed."** Response: Google Trends failed on a *demand-search* proxy for a *company-specific volume* number with no calibration anchor and admitted zero correlation (WF ratio 3.05x naive, best 0.836 only in one window). The review-text proxies here are calibrated **directly against the disclosed series they replace**, in the overlap window, with the fit reported and a stop-loss rule (if `b`'s CI excludes a wide band around 1, we say so and drop it) — the honesty mechanism is the pre-registration, not a claim that text-mining is inherently different from search-mining.
- **"Foundation models on 24 points is a stunt — of course it just reduces to AR(1)."** Response: agreed, and stated as the expected outcome in Section 2d before running it; the deliverable is the **coverage/calibration** comparison (PIT histogram), not a point-accuracy claim — if a judge presses "why run it at all then," the answer is that a hedge-fund PM cares about **interval honesty** for sizing a scenario-weighted position, and cheap zero-shot calibration checks are a due-diligence step the team's own 20_temporal-validation.md never ran.
- **"The ensemble stacking is just a fancier version of the composite indexes that already failed."** Response: the failed indexes combined *point features that individually lost to AR(1)*; this stack combines *predictive distributions from mechanistically distinct models* (a structural driver model, a nowcast tracker, an FX/take-rate model, this lens) each independently validated against baselines, and the stacking weights are scored on **pinball loss for quantiles**, not point RMSE — a different loss surface than NNLS ever optimized before in this repo.
- **"Every one of these modules depends on data (review store, transcript text) that may not even be accessible in this checkout."** Response: correctly flagged in Section 3 as the single largest execution risk; Day 1 of the build plan exists specifically to resolve it, and every module has a stated fallback that degrades gracefully to already-in-repo CSVs.

---

## 9. Interlock with the other five lenses

**Consumes:**
- From **Structural mix**: the regional nights build (`10_regional_panel_quarterly.csv`) and its interval-constraint outputs, as the target the cross-border/LOS recovered series (2b) corroborate, never override.
- From **FX/take-rate/timing**: the broad-USD→ADR-FX survivor coefficients (`05_macro_sensitivities.csv`) as the monotone-GBM's sign prior (2d.1), and the take-rate seasonal means as the Bayesian structural time series' informative prior (2d.3).
- From **Guidance game**: the guidance ledger itself (`02_guidance_ledger.csv`) is jointly owned — this lens adds the item-level text features: hands back an augmented `m5_statement_features.csv` keyed on `guide_id` so the Guidance-game lens's base-rate work (19/19 beats, 15/19 above-top) can be conditioned on language, not just outcome history.
- From **Nowcast tracker**: whatever pre-print operating-state features it produces (bookings-to-date proxies) as additional covariates in the challenger models (2d), subject to the same PIT filter.
- From **Bottom-up markets**: the market-level regulatory/DiD identification (model-audit recommendation 9) as a fixed-effect specification check on the hedonic (2c) — regulated markets should be excluded or dummy-flagged in the repeat-listing panel to avoid attributing a regulatory price effect to "pricing residual."

**Hands to:**
- **Structural mix**: the hedonic residual bound (2c) as the honest range around the +3.6pp unidentified ADR term, and the recovered cross-border/LOS series (2b) as an independent cross-check on the regional nights build (per model-audit recommendation 8's call for a market-grain re-test).
- **Guidance game**: the hierarchical cushion posterior (2a) as a **conditioning variable** — "cushion this quarter, given this call's language, is likely X±Y" — feeding directly into that lens's guide-vs-Street probability estimate.
- **FX/take-rate/timing**: the Bayesian structural take-rate model (2d.3) as a candidate replacement component for the flagged take-rate-carry plug (`13_driver_model.py:381`), specifically the posterior over the seasonal-offset drift term that lens needs to build its booking-to-check-in kernel (model-audit recommendation 1).
- **All lenses, via the ensemble (2e)**: a single conformal-calibrated quantile fan per catalyst date, and the explicit weight each lens received in the stack — which is itself a diagnostic the other lenses can use to see which of their claims are earning their keep out-of-sample.

**Critical dependency the other five must supply for this lens to function:** each lens must **version its own assumption files by print date** (the driver model's `REGIONAL_G`, the FX schedule, the regulatory drag table) so that a historical backtest of the ensemble is genuinely as-of-that-date and not contaminated by today's revised assumptions — this is a repo-hygiene requirement this lens surfaces but cannot itself enforce.
