# C_M5 — Adversarial critique of `M5_ml_signal_extraction_and_challengers.md`

Reviewer: investment committee seat + econometrics. Posture: default scepticism; the proposal survives
only if I fail to break it. **I broke every one of its five modules on its own stated terms**, and three
of the five on facts I verified by opening the files it cites. Verdict at the bottom: **reject as a lens**,
salvage three components as a service layer inside M1/M3/M6.

All paths below are absolute-resolvable from the repo root
`/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB`.

---

## 0. Path spot-check (24 paths opened; 4 wrong or missing)

| Claim in M5 | What I found | Verdict |
|---|---|---|
| `data/processed/overnight/02_guidance_ledger.csv`, 195 rows incl. header, columns incl. `quote`, `cushion`, `verified` | 195 lines / 194 data rows; all 194 `verified=True`; all 194 `quote` non-null | **confirmed** |
| Code skeleton §6 filters `df.metric == "revenue_musd"` | **No such metric exists.** `metric` values are `revenue_usd_m` (22), `revenue_yoy_pct` (23), `revenue_yoy_exfx_pct` (4). The skeleton returns an **empty frame**; `pm.sample` on a zero-row `y` fails. | **broken as written** |
| `data/raw/transcripts/{ir,sa}/<q>.txt` "gitignored, already downloaded per script" | `data/raw/` contains only `bea/`, `fred/`, `regulatory/`. `transcript_analytics.py` sets `RAW = ROOT/data/raw/transcripts` where `ROOT = parents[2]` = the repo root. **The directory does not exist in this checkout.** Texts do exist elsewhere: `../Theo Data/raw_expansion_licensed/v2_2026-09-05/transcripts_factset/`, `../FX-ADR-R-model/refresh-2026-09-07/source_text/`, `theos-past-research/research/transcripts/` | **missing at the cited path** |
| `raw_expansion/` "315 files, ~9.9GB, sibling folder" | Not a sibling of the repo; it is a sibling of the repo's **parent** (`.../Citadel - ABNB/raw_expansion`), 9.2G on disk, 316 files, one top-level dir `v2_2026-09-05` | **exists, wrong location as cited** |
| `06_ia_dump_metrics.csv` / `08_ia_city_yoy.csv`, "169 rows", "168 dumps x 13 cities Dec 2022–Aug 2026" | File is `08_ia_dump_metrics.csv` (not `06_`), 168 data rows, 13 cities, 2022-12-13 to 2026-08-30 — dump count right. `08_ia_city_yoy.csv` is **103 data rows, not 169**. Neither file has any price column. | **path prefix and one row count wrong** |
| `06_quote_line_items.csv`, 77 rows / 1.71M underlying quotes | 76 data rows; `quotes` sums to **1,707,390**; **13 cities; dump dates 2026-03-16 to 2026-08-30 only** | **confirmed, but see §1.3 — six months, one year, thirteen cities** |
| `02_kpi_panel_quarterly.csv` 25 rows | 25 lines (24 quarters) | confirmed |
| `04_consensus_at_print.csv` 24 rows | 24 lines (23 prints) | confirmed |
| `20_prediction_ledger.csv` 392 rows, schema incl. `decision_time`, `consensus_point_in_time` | 391 data rows, 28 cols, schema confirmed | confirmed |
| `08_test_scoreboard.csv` 11 rows; `05_macro_sensitivities.csv`; `06_elasticities.csv`; `20_frozen_q3_2026.csv`; `04_current_consensus.csv`; `10_regional_panel_quarterly.csv`; `02_disclosure_changes.csv`; `booking_curves_by_market.csv` (601); `abnb_declined_to_quantify.csv`; the 6 party-size v2 shard families; `model/ABNB_driver_model.xlsx`; `13_driver_model.py`; `research/notes/2026-09-07_adr-decomposition.md`; `.../20_temporal-validation.md`; `.../08_altdata-index-and-backtests.md`; `.../29_q4-fy27-bridge.md`; `2026-09-04_management-timeline.md` | all present, contents as described | confirmed |
| `/Users/theomachado/abnb_scratch` | exists, 3.7G, contains `release/airbnb_quant_panel_v3` and `raw_expansion/v3_2026-09-06` | exists |

A proposal whose flagship code block filters on a metric name that is not in the file it says it
verified with `head -5` has not run its own skeleton. That is the first thing the committee notices.

---

## 1. AXIS 1 — IDENTIFICATION. Score 3/10

### 1.1 The cushion model is exactly unidentified. This is fatal and it is arithmetic, not opinion.

M5 §2a writes the model as

    cushion_c = alpha + sum_k beta_k * mean_{s in metric=revenue, c}(feature_k(s)) + u_c,  u_c ~ N(0, tau^2)

and claims "the effective n for beta_k is the ~194 statements ... shrunk through 23 groups, not 23
independent draws." Three separate facts kill this.

**(a) The dependent variable exists 19 times, once per call.** I ran the ledger:
`metric == "revenue_usd_m"` has 22 rows over 22 distinct calls, of which **19 have a non-null
`cushion`** (3Q21 through 1Q26 targets; 2Q26's 3Q26 guide is `pending`). There is **one revenue
guide per call**. So `y` is a length-19 vector indexed by call.

**(b) Averaging the features to the call destroys the within-call variation the whole design rests on.**
The specification itself takes `mean_{s in c}` of each feature. Any statement-level variance is
integrated out before it ever touches `beta_k`. The design matrix is 19 x 4. There is no sense in
which `beta_k` is "identified off ~194 independent text draws" — the estimator literally never sees
a statement, only a call mean. And the revenue-family statement count per call is **2.13**, not 8.4:
`revenue_usd_m` + `revenue_yoy_pct` + `revenue_yoy_exfx_pct` = 49 statements across 23 calls
(range 1 to 3 per call). The "194" is the count of **all metrics** — EBITDA margin, tax rate, S&M,
capex. M5 §2a forbids pooling across metrics ("never pools across metrics"), so by its own rule
the 194 is unavailable to it. The "159 scoreable" figure it borrows is from
`01_ground-truth/03_insider_mechanics.md:360`, where it counts **guide-type hit rates across all
metrics**, not revenue statements. The proposal has imported a number from a different population.

**(c) With one observation per group, the random intercept is not identified.** `u_c ~ N(0, tau^2)`
and `epsilon_c ~ N(0, sigma^2)` enter as `y_c = mu_c + u_c + epsilon_c` with exactly one `y` per
`c`. Only `tau^2 + sigma^2` is identified; `tau` and `sigma` are separately pinned **only by their
priors** (`HalfNormal(1.0)` for both in the §6 skeleton). PyMC will sample — Bayesian models with
proper priors always do — and will produce a posterior for `tau` that is a reparameterisation of the
prior. The skeleton's `calls, call_idx = np.unique(rev.print_quarter, return_inverse=True)` makes
`call_idx` a bijection onto rows, confirming it. **This is the hidden plug: the "hierarchical pooling
that fixes the n=23 problem" is a prior, not an estimator.** The proposal's own hostile-Q&A answer
("correct for the between-call variance component tau, which is why we report tau's credible interval
honestly") is worse than no answer — it promises to report a credible interval on a quantity the data
cannot speak to.

### 1.2 The target is in the wrong units, and the priors are mis-scaled by a factor of ~50.

`cushion` in the ledger is **US dollars millions above the top of the guided range**, not percent.
Verified values for the 19 scoreable revenue guides: 52, 29, 0, 4, 22, 0, 34, 0, 48, 72, 8, 2, 40, 2,
46, 0, 58, 48, 8. Mean **24.9**, sd **24.1**, min 0, max 72. The percentage object is a different
column, `pct_distance_from_mid` (mean 2.54, sd 1.55).

M5 sets `beta_k ~ N(0, 0.5^2)` on the stated reasoning that cushion is "measured in single-digit
percentage points" and "a coefficient near +/-1 already spans the observed range." Against a target
with sd 24, a N(0, 0.5) prior shrinks every slope to approximately zero **by construction**. The
skeleton compounds it: `alpha = pm.Normal("alpha", rev.cushion.mean(), 1.0)` puts an sd-1.0 prior on
an intercept whose own residual sd is ~24. The model will return `beta ~ 0` with tight intervals and
the team will report "no language signal" as a finding. **That is a manufactured null, and the memo
would be reporting a prior as a result.**

Worse, `cushion` in dollars is non-stationary by construction: guided revenue went from $1.435bn
(3Q21) to $4.730bn (3Q26). A fixed *proportional* beat produces a mechanically rising dollar cushion.
Any feature with a time trend loads on it.

### 1.3 A concrete double count, as requested: `fxquant` and the FX lens, counted twice.

Construct the case. Let the broad dollar weaken 5%.

1. **M6 (FX/take-rate/timing)** raises `f_R`. The repo's own fit is
   `05_macro_sensitivities.csv`: `usd_broad -> adr_fx_effect`, coefficient -0.5925 pp per unit,
   r = -0.9508, perm p = 0.0010, confidence `high`. Revenue FX moves. M6's `p_j` shifts right.
2. **M5 §2d.1** feeds broad-USD into the monotone GBM with an imposed sign. Its `p_j` shifts right,
   from the *same* macro series.
3. **M5 §2a** sets `fxquant_k(s) = 1` when management quantifies an FX effect in percentage points.
   Management quantifies FX **precisely when FX is large** — `03_insider_mechanics.md:509` shows the
   3Q26 construction ("inclusive of an approximate three percentage point FX tailwind after factoring
   in our hedging program"); this construction is a recent habit, concentrated in the quarters where
   FX was material, which are also the quarters with the largest revenue base. Regressing a
   dollar-denominated cushion on `fxquant` therefore produces a positive, apparently-significant
   `beta_fxquant` that is **the FX cycle plus the revenue-level trend**, not a language effect.
   M5 hands that as a "cushion-shift feature" to M3.
4. **M3 (guidance game)** applies the cushion shift to its guide-beat probability, moving *its* `p_j`
   right — on information already inside (1) and (2).
5. **M5 §2e** then mixes M6, M5 and M3 as if they were structurally distinct lenses.

The level is not over-counted (a mixture is a weighted average, not a sum), but the **dispersion
collapses exactly when the components are most correlated-wrong**: `p_ens = sum_j w_j p_j` is
narrow when the components agree, and they agree here because they are all reading one dollar. The
ensemble will be most confident in precisely the FX-shock scenario where the 1-2 quarter recognition
lag (`03_insider_mechanics.md:308-310`: EUR/USD y/y on revenue, r 0.76 at lag 0, **0.86 at lag 1**,
0.58 at lag 2, n=14) makes the mapping most fragile.

M5 §2a's stated overlap defence — "this model's only output is a scalar cushion-shift feature handed
downstream, never a revenue number itself" — **is contradicted by §2e**, which lists "ML challengers"
as its own lens `j` with its own `p_j` in the mixture. M5 is simultaneously an input to M3 and a
sibling of M3 in the same average. The overlap fix works in words only.

### 1.4 The hedonic residual is not "orthogonal by construction" in the sense that matters.

§2c writes `ln(price) = g0 + g1 ln(capacity) + g2 bedrooms + g3 LOS_bucket(t) + delta_m + theta_c(m) + eps`
and claims `eps` is "by construction orthogonal to size and LOS composition."

- **No time dummies.** A hedonic *price index* is the vector of time coefficients. This equation has
  no `t` except inside `LOS_bucket(t)`. You cannot recover an index from it. And OLS residuals are
  orthogonal to the included regressors **in sample, over the whole sample** — the within-market mean
  residual is exactly zero if `delta_m` is a market dummy. Aggregating `eps` to "a quarterly
  market-level index" recovers the part of the time variation the specification failed to model,
  which is not the same object as "pricing plus unmeasured mix."
- **Orthogonality to regressors is not orthogonality to composition.** Mix effects enter through
  shifts in the *distribution* of X, not through correlation with X in levels. With constant
  coefficients, a linear-in-logs hedonic removes composition only if you do the shift-share on the
  fitted coefficients explicitly — which `02_model_audit.md` §3.5 recommendation 5 says, and which
  §2c states but does not specify.
- **`theta_c(m)` is collinear with `delta_m`.** Countries contain markets, not the reverse; a
  country-within-market effect nested inside a market fixed effect is either empty or perfectly
  absorbed. This is a spec written from memory, not from the data.

### 1.5 Hidden plugs, enumerated

| Plug | Where | Why it is a plug |
|---|---|---|
| `tau` in the cushion model | §2a / §6 | one obs per group; `tau` is the prior |
| `beta_k` scale | §2a | N(0, 0.5) prior against an sd-24 target forces beta to 0 |
| Cross-border calibration `(a, b)` | §2b | §2b says "fit to the overlap window"; the same bullet says "a **single** calibration anchor" (46% at 1Q24). One anchor cannot identify two parameters. Internally inconsistent; in practice `b` gets set |
| Monotone constraint signs | §2d.1 | see §3.2 below — the sign on nights is imported from a different target |
| Ensemble weights `w_j` | §2e | unlearnable in three weeks (see §5.3); they will be hand-set, which is the scenario tree M5 says it replaces |
| `kappa` | §2e | a single order statistic of 6 residuals (see §3.4) |

---

## 2. AXIS 2 — POINT-IN-TIME SAFETY AND BACKTEST VALIDITY. Score 2/10

### 2.1 The review store is **not** point-in-time, and M5 claims the opposite.

M5 §4(d) asserts: "review-store text with a `review_date` <= t (reviews are naturally dated, so PIT
filtering on the store itself is trivial and this data source is *more* PIT-safe than most in the
repo, not less)."

This is exactly backwards, and the repo says so in its own inventory.
`../Theo Data/data_review_2026-09-07/DATA_MAP.md` describes V3 reviews as
**"67,500,188 rows; review dates 2008-06-22 to 2026-08-20 ... Public review event retained in a later
scrape; not all historical stays."** Finding 3 of the same document: the two listing vintages "do not
form a uniform annual panel," paired snapshot intervals range 170 to 370 days.

The review *date* is PIT-safe. The review's **presence in the sample is not**: it is the outcome of a
2026 scrape. Every review written in 2023 on a listing that was delisted, banned, or churned out
before September 2026 is **absent**. Survivorship selection is therefore a **monotone function of
distance from the snapshot**: the 2021 cross-section is far more selected than the 2025 one.

This destroys §2b's entire protocol. The design is: fit `y_disclosed = a + b*y_proxy` on the
pre-1Q24 overlap, freeze `(a, b)`, extend forward. But the pre-1Q24 overlap is drawn from a
*more-selected* sample than the post-1Q24 extension. The mapping is estimated under one selection
regime and applied under another, and the drift in selection is smooth and monotone — i.e. it will
look like a trend, which is exactly what the extension is supposed to measure. **The frozen
calibration is biased in the direction of the thing it is trying to estimate.** The proposal's
"stop-loss" (drop if `b`'s CI excludes a band around 1) does not catch it: the in-sample fit will be
excellent, because both series share the survivorship trend.

`02_model_audit.md` §4.2(c) already flagged this class of defect for Inside Airbnb:
*"the retrospective scope flag uses LATER scrapes, so a frozen replay may only... the IA panel is not
vintage-reconstructible and is labelled as such."* M5 re-opens it on a bigger store and calls the
bigger store the fix. It is the same defect with nine times the market coverage.

### 2.2 The transcript-paragraph feature is not reconstructible at the cited path.

§2a requires "the surrounding transcript paragraph pulled from `data/raw/transcripts/{ir,sa}/<q>.txt`."
That directory does not exist in this checkout (§0). The texts are recoverable from
`../Theo Data/raw_expansion_licensed/v2_2026-09-05/transcripts_factset/` and the sibling FX repos, but
those are **FactSet corrected transcripts**, which are published *after* the call, sometimes days
after, and are revised. For 8 of the 23 calls the source is `stockanalysis.com` paragraph text with
**no speaker tags** (`transcript_analytics.py` header: "speaker attribution inside Q&A is heuristic").
A hedge-density feature computed on a corrected, revised, speaker-heuristic transcript is not the text
that existed at the guide date. The §6 skeleton's PIT `assert` compares `extraction_asof` to
`print_date` — it checks that the **annotation** is not post-dated, not that the **source text vintage**
was available. That assert passes on leaked data.

### 2.3 Leakage in the walk-forward the skeleton actually implements.

`loo_expanding()` in §6 refits pooled OLS on `calls < i` and predicts call `i`. Good. But:
- The **LLM feature definitions** (which tokens count as hedges, which asks count as declines) are
  chosen once, by a human who has read all 23 transcripts and knows the cushion history. Feature
  *design* leakage is not controlled by any fold structure. With 4 features and 19 observations this
  is the dominant degree of freedom.
- `abnb_declined_to_quantify.csv` is described in `transcript_analytics.py` as a **hand-verified
  kept set**, curated from a rule-based candidate pass. It is a full-sample curated label. Using it
  as `decline_k` injects the curator's full-sample judgement into every early fold.
- The naive benchmark is `rev.groupby(...)["cushion"].mean().diff().abs().mean()` — a random-walk
  benchmark on a series whose best-known predictor is the **trailing-8 median** (+1.79%,
  `01_data_inventory.md:57`). `02_model_audit.md` §4.2(b) is explicit that trailing means are the
  hard baseline and that random-walk comparisons flatter models. The skeleton picks the flattering
  benchmark.

### 2.4 The ensemble backtest cannot be made PIT and M5 admits it.

§2e requires each of the six lenses to emit an as-of-date predictive distribution at every historical
guide date, which requires versioning `model/assumptions.md`, `REGIONAL_G`, the FX schedule and the
regulatory drag table by print date. §9 concedes this is "a repo-hygiene requirement this lens
surfaces but cannot itself enforce." A backtest whose precondition the proposal cannot deliver is not
a backtest.

---

## 3. AXIS 3 — STATISTICAL POWER AND OVERFITTING. Score 3/10

### 3.1 Free-parameter count against the real n

| Module | Real n | Free parameters | Comment |
|---|---|---|---|
| 2a cushion | **19** call-level obs | alpha, 4 betas, tau, sigma = **7** (tau not identified) + 5 feature *definitions* chosen ex post | ~2.7 obs per parameter |
| 2b cross-border | ~13 disclosed quarterly points (1Q21-1Q24, `02_disclosure_changes.csv` row 6: share 20% -> 46%) | a, b + proxy construction choices (language list, locale mapping, review-to-night weighting) | the disclosed series is a **COVID border-reopening ramp**; a 2-parameter linear fit on a monotone ramp is a level match, not identification of `b` |
| 2b LOS | 0 usable time-series points | — | see §3.3 |
| 2c hedonic | 1.71M quotes but **13 cities, Mar-Aug 2026 only** | 4 + market FE + listing FE | no y/y variation to index |
| 2d.1 GBM | 24 quarters, ~20 after burn-in | trees, depth, leaves, learning rate, 4 features, monotone signs — LightGBM defaults alone are >10 effective | |
| 2d.2 Chronos/TimesFM | 24 points | zero-shot, so 0 fitted — the only honest module in the stack | |
| 2d.3 BSTS | 24 quarters | level variance, seasonal variance, obs variance, 4 seasonal offsets | seasonal offsets pinned by "informative priors" near 9.2/13.1/18.3/14.0, i.e. at the values they are meant to estimate |
| 2e stack | <= 19 guide dates, in practice 6-10 with lens coverage | 6 weights (5 free) + kappa | |

M5's own §4 power paragraph is correct and then ignored: at n≈24 the detectable standardized effect
is ~0.9-1.0 sigma. Nothing in 2a, 2b or 2d.1 is anywhere near that. The proposal states the bound and
then proposes seven models beneath it.

### 3.2 The monotone constraint contradicts the repo's own evidence.

§2d.1 constrains `nights_yoy` **non-increasing in broad USD y/y**, sourcing the sign from "the two
validated survivors — funds-held slope 0.60/r 0.89, and broad-USD -> ADR-FX r 0.96-0.99."

I opened `05_macro_sensitivities.csv`. The USD survivor is on **`adr_fx_effect`**, not on nights:
r = -0.9508, perm p = 0.0010, confidence `high`. The row for **`usd_broad -> nights_yoy`** reads:
effect 0.2235 (positive), r = **0.3179**, spearman **-0.0637**, perm p = **0.2657**, LOO RMSE 3.5283
vs naive 2.954, confidence **`none`**, reason "|r| 0.32, perm p 0.27" — and `r_from2024` = **-0.3954**,
i.e. **the sign flips** between windows.

So the constraint imposes a **negative** sign on nights, while the full-window point estimate is
**positive**, the rank correlation is **-0.06**, and the relationship fails the team's own permutation
bar. M5 correctly quotes this row in §4 as something it "explicitly declines to build on" — and then
builds a hard monotone constraint on it in §2d.1. That is an internal contradiction, and it is the
precise mechanism by which the model would smuggle an untested macro view into the forecast.

Separately: **monotonicity is not a leakage control.** §2d.1 calls it "the leakage control." It is a
shape restriction on the fitted function. It constrains nothing about information timing. Category error,
and a judge with a stats background will say so.

### 3.3 `median_min_nights` is not an LOS proxy.

§2b builds the LOS proxy from "median reviewer-implied stay length from `booking_curves_by_market.csv`."
I opened it: 600 data rows, columns `country, region, market, snapshot_date, horizon, listing_nights,
listings, blocked_nights, blocked_rate, median_min_nights`. `median_min_nights` is the **host's
minimum-nights setting** — a supply-side restriction — with median 2 and a max of 31. It is not
reviewer-implied, not realized, and not stay length. And the snapshot dates run **2026-06-14 to
2026-08-10 only**: 24 snapshot dates inside one summer. There is **zero** time-series variation to
calibrate against the disclosed 28+ night share (which ran 24% -> 17% over 1Q21-1Q24,
`02_disclosure_changes.csv` row 8). M5 states both defects in its own data table ("single June-Jul
2026 vintage — NOT occupancy") and proceeds anyway.

### 3.4 Conformal at n_cal = 6 is not a finite-sample guarantee.

§2e: "split-conformal on the last 6 held-out quarters computes a single scalar inflation factor kappa
such that [q10 - kappa, q90 + kappa] achieves nominal 80% coverage empirically — a distribution-free,
finite-sample guarantee ... the single largest methodological upgrade this lens offers."

Two hard problems.

- **Exchangeability.** Split conformal's guarantee requires the calibration and test scores to be
  exchangeable. Quarterly revenue/guide data is trended, seasonal (the take rate alone runs
  9.2/13.1/18.3/14.0 by quarter, `03_insider_mechanics.md` §1.3), autocorrelated, and spans a COVID
  regime break. The expanding-window design M5 itself specifies **guarantees** non-exchangeability.
  There are time-series variants (weighted/adaptive conformal, EnbPI); the proposal names none of them.
- **n = 6.** The conformal quantile is the `ceil((n+1)(1-alpha))`-th order statistic. At n=6,
  alpha=0.2: `ceil(7 * 0.8) = 6`, i.e. **the maximum of the six calibration residuals**. The attainable
  coverage is 6/7 = 85.7%, not 80% — you cannot even target 80% at that n. And the interval width is
  a single order statistic: effective sample size one. Calling that a "guarantee" and the "largest
  methodological upgrade" is the single most attackable sentence in the document.

### 3.5 Does it repeat a failed design? Partly yes.

- **Repeats:** the call-level tone test. M5 claims to fix it by going statement-level; §1.1 shows the
  estimator never leaves the call level. It is the 2023 tone test with 4 features instead of 132 —
  better, but the same unit of observation and the same n.
- **Repeats:** composite NNLS. §2e reuses `scipy.optimize.nnls` and argues that pooling *distributions*
  is better-conditioned than pooling *point features*. That argument is real but not free: NNLS on 6
  non-negative weights summing to 1 over <=10 usable guide dates is 5 free parameters on 10 points,
  and the audit's verdict ("NNLS adds parameters a 20-observation sample cannot support") applies to
  the parameter count, not to the nature of the inputs.
- **Genuinely new and not condemned:** the repeat-listing panel design (never run), zero-shot
  foundation models for interval calibration (never run), PIT-histogram calibration diagnostics
  (never run — `20_temporal-validation.md` reports point RMSE only). Credit where due.

---

## 4. AXIS 4 — TRADEABILITY OVER 3-12 MONTHS. Score 4/10

The output format is right and is the proposal's strongest section. §5 asks for
`P(revenue >= Street mid)` and `P(4Q26 guide range < $3.10bn)` — decision-relevant probabilities,
benchmarked to the frozen card ($4,801M, +17.2%, `20_frozen_q3_2026.csv` is present and correctly
described) and to Street ($4,740M Zacks 4-Sep, 7 estimates, verified in `04_current_consensus.csv`).
It targets the **guide**, not the realised print, which is the correct target per
`02_model_audit.md` recommendation 7, and it is honest that the 5 Nov print lands after finals.

Where it fails the PM test:

1. **The mechanism for why the Street is wrong is asserted, not derived.** §5 says the differentiator
   is "mix-adjusted like-for-like pricing (2c) and the RNPL-lap language signal (2a)." 2c cannot be
   built (§5.2) and 2a is unidentified (§1.1). Strip those and the ensemble's disagreement with the
   Street is whatever the other five lenses already say, re-weighted by hand-set weights. There is no
   independent edge left.
2. **The only live, executable trade in the repo is not used.** `02_model_audit.md` §4.3: *guide below
   Street -> 20-day drift, 9/9 negative, mean -4.21% on the executable open-to-open convention,
   binomial p 0.0020.* That is the trade. M5 mentions the base rate 15/19 and 19/19 but never connects
   its `P(guide < Street)` output to the drift rule, never sizes it, never addresses that n = 9.
3. **No path to the multiple.** The pitch's P&L runs through the exit multiple (+0.48 EV/EBITDA turns
   per point of forward revenue growth). M5 produces revenue and guide distributions and stops. A PM
   asks "what is the stock worth in each branch"; the lens has no answer.

### FX lens note (the requested hypothesis test does not apply here)

The brief's FX-lag hypothesis — today's FX hits revenue ~2 quarters ahead via the booking lead — is
M6's burden, not M5's. For the record on the one place M5 touches it: M5 derives **no** lag weights.
It uses FX only as (i) a monotone sign on a GBM and (ii) a binary `fxquant` language dummy. Neither
uses the booking lead-time distribution nor the disclosed `fx_pts_revenue` series 2Q22-2Q26. The
relevant evidence is in `03_insider_mechanics.md` §2.4 (EUR/USD y/y on revenue ex-hedge: r 0.76 lag 0,
**0.86 lag 1**, 0.58 lag 2, n = 14) — which supports a **~1-quarter** modal lag, not 2 — and §1.4's
measured booking-to-check-in kernel (~2/3 on GBV(t-1), ~1/3 on GBV(t-2)), whose implied mean lag is
~1.33 quarters. M5 engages with none of it. `fx_lag_hypothesis_verdict: n/a` for this lens.

---

## 5. AXIS 5 — BUILDABILITY IN THREE WEEKS BY 3-4 UNDERGRADUATES. Score 2/10

### 5.1 Day-1 blockers the plan does not clear

- **Transcripts are not at the cited path** (§0). Day 2 assigns Person A to build the extraction
  prompt "against `02_guidance_ledger.csv`'s `quote` field". The `quote` field is present for all 194
  rows — but its **median length is 91 characters, max 150**. You cannot compute "hedging tokens per
  100 words of the statement's paragraph" from a 91-character quote. The paragraph requires the
  transcript, which requires finding and copying FactSet text from a sibling licensed folder, which
  reintroduces the vintage problem of §2.2. That is not a Day-2 task.
- **The review store is a 3.7G scratch volume with a V3 release panel**, not a DuckDB-ready table.
  `DATA_MAP.md` finding 1 notes V3 is a *partial* representation (five major markets present locally
  but absent from V3, 114,744 listing rows). Standing up 67.5M review rows, deriving reviewer locale,
  mapping locale to a host-country language table for 120 markets, and cutting to market-quarter is a
  multi-week data-engineering job, not "Day 3, Person B."
- **The §6 skeleton does not run.** `metric == "revenue_musd"` yields zero rows (§0).

### 5.2 2c cannot be built at all with the data on disk

The whole point of 2c is a **like-for-like y/y ADR benchmark**. The only fee-inclusive quote panel is
`06_quote_line_items.csv`: **13 cities, 2026-03-16 to 2026-08-30**. Six months, one year. There is no
prior-year quote panel to compare against, so there is no y/y like-for-like drift to measure — only
within-2026 seasonality.

The proposed fallback (chain to Inside Airbnb dumps) is closed twice over:
`08_ia_dump_metrics.csv` has **no price column**; `DATA_MAP.md` finding 4 states "the current calendar
has no price column"; and `02_model_audit.md` §4.2(e) records that Inside Airbnb **dropped listed
prices from late-2025 dumps**, so "the like-for-like price series cannot be extended." M5 quotes that
caveat in its own data table and then proposes the index anyway.

And the basis change is larger than the signal. `06_wtp_hedonic_coefs.csv` — which M5 does not cite —
**already contains the joint hedonic it proposes**, on 17 terms with dump fixed effects, fitted twice:

| Term | `listed_nightly` basis (n = 951,134, 47 dumps, R2 0.393) | `quote_per_night` basis (n = 1,375,944, 76 dumps, R2 0.459) |
|---|---|---|
| ln(capacity) | +0.332 (+39.4% per log unit) | 06_elasticities: +0.49% per 1% capacity vs +0.39% on the listed basis |
| bedrooms | +0.178 (+19.5%) | +15.1% |
| rating >= 4.9 | +13.5% | +9.5% |

The coefficients move 20-30% between the listed (2024-25) and quote (2026) bases. Any index that
chains 2024-25 listed prices to 2026 quotes is measuring the basis change, not price drift.
`DATA_MAP.md` finding 2 adds: "Quotes depend on requested stay length and may contain **inconsistent
currency representations**. The normalized price is not automatically realized ADR." An ex-FX
like-for-like index built on a panel with inconsistent currency handling is a contradiction in terms.

Finally: M5's §2c specification **drops** room_type, rating_band, host_band, instant_bookable,
licensed and reviewed_ltm, every one of which is large and correlated with capacity in the existing
fit. Its residual would be *more* contaminated by quality composition than the model the repo already
has. This module is a regression relative to existing work, presented as novelty.

### 5.3 The ensemble cannot be assembled on this timeline

§2e needs, at each historical guide date, an as-of-that-date predictive **distribution** from six
lenses that do not yet exist, plus date-versioned assumption files across the whole repo. §7's
"degrade gracefully — a 3-lens stack with correct weights beats a 6-lens stack rushed" concedes the
point without fixing it: a 3-lens NNLS on <=10 historical guide dates is 2 free parameters on 10
correlated points. The weights will be set by judgement. The proposal's headline differentiator
becomes the hand-set scenario tree it promises to replace.

### 5.4 What a minimum viable version actually is, and whether it carries edge

MVP that survives: (i) the **LLM annotation of the 194 `quote` fields** into a tidy
`m5_statement_features.csv` keyed on `guide_id` — cheap, one batched call, genuinely useful as a
**descriptive** artefact handed to M3; (ii) the **PIT-histogram / CRPS calibration harness** bolted
onto the existing `20_prediction_ledger.csv`, which already carries `decision_time`,
`last_training_label_quarter`, `consensus_point_in_time` (verified, 391 rows, 28 columns) — this is
a genuine gap in `20_temporal-validation.md`, it is a day of work, and it improves every other lens.
Everything else should be cut. Does the MVP carry edge? **(ii) yes, as infrastructure. (i) no** — a
descriptive language table is not a signal, and M5's own hostile-Q&A answer concedes the walk-forward
will probably be null.

---

## 6. AXIS 6 — DEFENSIBILITY IN A 2-PAGE MEMO AND 10-MINUTE HOSTILE Q&A. Score 3/10

**The one-sentence version M5 wants:** "We use ML not to forecast revenue but to extract what
management's language says about how much cushion they left themselves, to recover KPIs Airbnb stopped
disclosing, and to put honest, conformal-calibrated intervals on everyone else's numbers."

**The one-sentence version a judge hears:** "We ran a hierarchical Bayesian model on 19 observations
and a foundation model on 24 points."

**The first number a judge attacks: the n behind `beta_k`.** M5 has anticipated the question
("n=23 calls is still n=23 no matter how you slice the sentences") and its prepared answer —
"the within-call, sentence-level coefficients are identified off ~194 independent text draws" — is
**false for this specification** (§1.1). A judge who asks "how many revenue guides have a scored
cushion?" gets **19**. The follow-up — "and how many statements per call discuss revenue?" — gets
**2.1**. The prepared defence collapses in two questions, in public. That is worse than having no
module, because it costs credibility on the modules that are sound.

**Second attack: units.** "Your cushion variable has a standard deviation of 24. Your slope prior has
a standard deviation of 0.5. What can your betas possibly be?" There is no answer in the document.

**Third attack: PIT.** "Your review store was scraped in 2026. How do you see the reviews of listings
that were delisted in 2024?" M5's §4(d) claims this source is *more* PIT-safe than the rest of the
repo. It is the least.

**Memo economics.** §7 allocates M5 "<= 1 paragraph" of a two-page memo. Five modules, three of which
cannot be built, compressed into one paragraph, in support of a headline number produced by another
lens. The cost-benefit does not clear even before the identification problems.

---

## 7. Refutation attempts (claim -> attack -> outcome)

**R1. Claim (§2a):** hierarchical pooling raises effective n from 23 to ~194 and fixes the failed tone test.
**Attack:** ran the ledger. `y` = 19 call-level cushions; features are averaged to the call by the spec
itself; revenue-family statements are 2.13 per call; one obs per group leaves `tau` unidentified from
`sigma`. The "194" is an all-metric count the proposal's own no-cross-metric-pooling rule forbids.
**Outcome: REFUTED.**

**R2. Claim (§2a / §6):** the model is ready to run against the verified ledger.
**Attack:** `metric == "revenue_musd"` matches zero rows (actual: `revenue_usd_m`); `cushion` is $M
(sd 24.1) not percent, against a N(0, 0.5) slope prior and a N(mean, 1.0) intercept prior; 4 of 19
values are exactly 0 (censored at the top of the guided range) under a Gaussian likelihood.
**Outcome: REFUTED.**

**R3. Claim (§2b / §4d):** review-text KPI recovery is PIT-safe and is a grain fix, not a repeat of the
Trends/IA failures.
**Attack:** `DATA_MAP.md` — reviews are "retained in a later scrape; not all historical stays," from a
single 2026 V3 snapshot. Survivorship is monotone in distance from the snapshot, so a frozen
pre-1Q24 calibration is applied under a different selection regime; the disclosed cross-border series
is a 13-point COVID-reopening ramp (20% -> 46%); the LOS proxy is host `median_min_nights` from a
single summer-2026 vintage; §2b contradicts itself on one anchor vs an overlap-window fit.
**Outcome: REFUTED.**

**R4. Claim (§2c):** a repeat-listing hedonic gives the first true like-for-like ADR benchmark and kills
the double count by construction.
**Attack:** the quote panel is 13 cities x Mar-Aug 2026 — no y/y variation; IA dumps carry no price
(verified: no price column in `08_ia_dump_metrics.csv`; audit records prices dropped from late-2025
dumps); the joint hedonic already exists in `06_wtp_hedonic_coefs.csv` with a richer covariate set,
and its coefficients move 20-30% between the listed and quote bases, which is larger than the effect;
the spec has no time dummies, so no index is recoverable; `theta_c(m)` is collinear with `delta_m`.
**Outcome: REFUTED.**

**R5. Claim (§2d.1):** monotone constraints encode validated sign priors and control leakage.
**Attack:** `05_macro_sensitivities.csv` gives `usd_broad -> nights_yoy`: effect **+0.2235**, r 0.3179,
spearman -0.0637, perm p 0.2657, confidence **none**, `r_from2024` **-0.3954** (sign flips). The
constraint imposes a negative sign the data rejects, borrowed from the ADR-FX target. And monotonicity
is a shape restriction, not an information-timing control.
**Outcome: REFUTED.**

**R6. Claim (§2e):** conformal calibration gives a distribution-free finite-sample coverage guarantee —
the largest methodological upgrade on offer.
**Attack:** exchangeability fails by construction under an expanding-window time-series design (trend,
seasonality, COVID break), and at n_cal = 6 with alpha = 0.2 the conformal quantile is the **maximum**
of six residuals; attainable coverage is 6/7 = 85.7%, so 80% is not even targetable. No time-series
conformal variant is named.
**Outcome: REFUTED.**

**R7. Claim (§2a):** overlap with the other lenses is avoided because M5 emits only a scalar
cushion-shift feature, never a revenue number.
**Attack:** §2e lists "ML challengers" as its own lens with its own `p_j` in the same mixture that
contains M3, to which M5 feeds the cushion shift. A dollar shock moves M6, the GBM, `fxquant` and M3's
base rate together; the mixture's spread collapses exactly when the components are most
correlated-wrong.
**Outcome: REFUTED (contradicted by its own §2e).**

**R8. Claim (§2d.2, §4):** zero-shot foundation models for interval calibration are untested here and
therefore not condemned by the negative-test record.
**Attack:** tried and failed to break it. `20_temporal-validation.md` reports point RMSE only; nothing
in the ~3,500 tests measures PIT/coverage. The proposal pre-states that point accuracy will match
AR(1), which is the honest expectation, and asks only for the calibration comparison. It is cheap and
it is a real gap.
**Outcome: SURVIVED.**

**R9. Claim (§4, §7):** the plan is executable in three weeks with the files on disk.
**Attack:** transcripts absent from the cited path; the 91-character median `quote` cannot support a
per-100-word density feature; the review store is an unnormalised 3.7G scratch volume with a
documented-partial V3; 2c has no y/y price data; 2e's weights need date-versioned assumption files
across five lenses that do not exist. Three of five modules do not reach a defensible number.
**Outcome: REFUTED (partially survives as the two-piece MVP in §5.4).**

---

## 8. Scores

| Axis | Score | One-paragraph justification |
|---|---|---|
| 1. Identification | **3/10** | The flagship module is exactly unidentified: 19 call-level observations, features averaged to the call by the spec itself, one observation per random-effect group so `tau` is the prior. Slope priors are mis-scaled ~50x against a dollar-denominated, left-censored target. The hedonic residual is called orthogonal-by-construction when it is only orthogonal to included regressors in sample, and the equation has no time dummies so no index exists. The one real credit: §2c's instinct to co-estimate size and LOS in one regression is exactly the audit's recommendation 5 — but the repo already did it, better. |
| 2. PIT safety | **2/10** | The proposal's loudest PIT claim is its most wrong: the 67.5M review store is a single 2026 scrape, so review *presence* is survivorship-selected in a way that trends monotonically with distance from the snapshot — the exact defect the audit already recorded for Inside Airbnb. Transcript text is absent at the cited path and would be sourced from post-call corrected FactSet files. Feature-definition leakage and a full-sample hand-curated `declined_to_quantify` label enter every fold. The one genuinely PIT-clean input is the guidance ledger, which is dated at issuance. |
| 3. Power / overfitting | **3/10** | The document states the correct power bound (~0.9-1.0 sigma detectable at n=24) and then proposes seven models beneath it. 7 parameters on 19 points in 2a; 2 parameters on a 13-point COVID ramp in 2b; a GBM with double-digit effective parameters on ~20 quarters; 5 free weights on <=10 dates in 2e. The monotone constraint that is supposed to be the discipline imposes a sign the repo's own permutation test rejects and that flips between windows. Real credit for pre-registering the stop-loss on `b` and for proposing PIT/CRPS diagnostics nobody has run. |
| 4. Tradeability | **4/10** | The output *format* is right — `P(revenue >= Street mid)`, `P(4Q26 guide range < $3.10bn)`, a guide-bucket posterior — and it correctly targets the guide rather than the post-finals print. But the stated mechanism for disagreeing with the Street rests on two modules that cannot be built, it never connects its `P(guide < Street)` to the only executable rule in the repo (9/9, -4.21% open-to-open, p 0.0020), and it stops at revenue without touching the multiple that carries the P&L. |
| 5. Buildability (3 weeks) | **2/10** | The §6 skeleton does not run against the file it claims to have verified. Transcripts are not where it says. The 91-character `quote` field cannot support the density features. The review store is an unnormalised 3.7G scratch volume with a documented-partial V3. 2c has no prior-year price data anywhere on disk. 2e needs date-versioned assumptions across five lenses that do not exist. Two pieces are genuinely shippable in a day each; the other three are not shippable at all. |
| 6. Defensibility | **3/10** | The prepared answer to the first question a judge will ask ("n=23 is still n=23") is false for the specification actually written, and it falls in two follow-ups: 19 scoreable revenue guides, 2.1 revenue statements per call. The conformal sentence is the most attackable claim in the whole six-lens programme (n_cal = 6 cannot target 80%). Five modules compressed into one memo paragraph in support of another lens's headline number is poor use of scarce page space. |

---

## 9. FATAL flaws

1. **2a is unidentified.** 19 call-level observations, call-averaged features, one observation per
   random-effect group. `tau` and `sigma` are separately pinned only by priors. The headline "effective
   n = 194" is false under the proposal's own no-cross-metric rule.
2. **2a's target units are wrong by ~50x against its priors.** `cushion` is $M (mean 24.9, sd 24.1,
   left-censored at 0 for 4 of 19), not percentage points. `beta ~ N(0, 0.5)` and `alpha ~ N(mean, 1.0)`
   manufacture a null and a dollar-denominated target manufactures a spurious time trend.
3. **The review store is not point-in-time**, and M5 asserts the opposite as a strength. Single 2026
   scrape; presence is survivorship-selected; selection drifts monotonically with time-to-snapshot,
   which is the direction of the effect 2b is trying to measure.
4. **2c has no y/y like-for-like price data anywhere on disk.** Quote panel is 13 cities x six months
   of 2026; IA dumps carry no price (verified, and the audit records prices were dropped from
   late-2025 dumps); the listed-vs-quote basis change moves hedonic coefficients 20-30%.
5. **The §6 skeleton filters a metric name that does not exist** (`revenue_musd`), so the flagship code
   block has never been run.
6. **The overlap fix is verbal, not structural.** M5 is simultaneously an input to M3 and a sibling of
   M3 in the same mixture; one dollar shock moves four components together and the mixture is narrowest
   exactly where the components are most correlated-wrong.

## 10. MUST-FIX (if any part is carried forward)

1. Fix the metric name to `revenue_usd_m` and re-state the sample honestly as **n = 19 calls**.
2. Change the target to **`pct_distance_from_mid`** (mean 2.54, sd 1.55) or `cushion / value_mid`, and
   re-scale the priors to that target. Model the top-of-range censoring explicitly (Tobit / censored
   likelihood), since 4 of 19 realisations sit exactly at 0.
3. **Delete the call random intercept**, or make the model genuinely statement-level by defining a
   statement-level outcome (e.g. per-metric `pct_distance_from_mid`, which exists for 94 rows across
   13 metrics) and *then* pooling. One or the other, not the current hybrid.
4. Cap at **2 features**, not 5, at n=19, and pre-register them in `20_experiment_spec.json` with an
   incremented `spec_id` before any LLM pass is run.
5. Benchmark against the **trailing-8 median cushion**, not a random walk.
6. Move the transcript source to an explicit, dated path and record the transcript **vintage** (FactSet
   corrected transcripts post-date the call), not just the annotation date. Extend the §6 PIT assert to
   the source-text vintage.
7. Either **drop 2b** or add an explicit survivorship model: estimate the review-retention hazard by
   listing cohort from the paired V3 vintages and reweight, and show the recovered series with and
   without the correction. Fit `(a, b)` on the full 1Q21-1Q24 disclosed panel, state the n, and show the
   fit is not just a COVID-ramp level match (e.g. fit on differences, not levels).
8. **Drop the LOS proxy entirely.** `median_min_nights` is a host supply setting from one summer vintage.
   The repo's existing measured LOS work (`analysis/src/adr/14a-14c`) is better and already done.
9. **Drop 2c as specified.** If anything survives, it is: re-run `06_wtp_hedonic_coefs.csv` with a
   stay-length bucket added and **dump-date dummies**, on the quote basis only, and report the time
   dummies as a within-2026 seasonal price path with an explicit statement that no y/y index is possible.
   Do not chain the listed and quote bases.
10. **Remove the USD monotone constraint on nights.** Keep it on `adr_fx_effect` where the survivor
    actually lives, and stop calling monotonicity a leakage control.
11. **Restate the conformal claim.** Name a time-series conformal variant, state that exchangeability
    fails, report the attainable coverage grid at the actual `n_cal`, and stop calling it a guarantee.
12. **Resolve the M5-as-input vs M5-as-lens contradiction.** Pick one. If M5 feeds M3, it must not
    appear as a separate `p_j`; if it appears in the mixture, the cushion feature must not also be fed
    to M3.

## 11. WHAT TO KEEP even if the whole is rejected

1. **The calibration harness** — PIT histograms, CRPS, and coverage bolted onto the existing
   `20_prediction_ledger.csv` (391 rows, 28 columns, `decision_time` / `last_training_label_known_at` /
   `consensus_point_in_time` already present). `20_temporal-validation.md` reports point RMSE only.
   This is a genuine, cheap gap and it improves all five other lenses. **Highest-value item in the
   document.**
2. **The zero-shot foundation-model run as a calibration benchmark only**, with the null result
   pre-stated. One Colab session. It survived every attack I made.
3. **The LLM annotation of the 194 `quote` fields into `m5_statement_features.csv` keyed on `guide_id`** —
   as a *descriptive* artefact handed to M3's base-rate work, never as a fitted forecaster. It makes the
   guidance ledger conditionable on language and costs a day.
4. **The insistence that the target is the guide, not the realised print** (audit recommendation 7), and
   the discretisation of FY27 growth into the ledger's own historical bucket vocabulary. Correct framing,
   and it is the only part of the document a judge will find obviously right.
5. **The pre-registered stop-loss discipline** in §2b (state in advance what result kills the series).
   Apply it to every lens.
6. **The explicit separation of level accuracy from surprise accuracy** in §4, including the correct
   quotation of the audit's finding that guide+cushion is the *worst* surprise predictor.

---

## 12. Verdict: REJECT as a lens; salvage items 1-3 above as a service layer.

Three of five modules are unbuildable with data on disk (2b, 2c) or unidentified as specified (2a).
The two that survive (calibration diagnostics, zero-shot interval benchmark) are infrastructure, not a
view, and belong inside other lenses rather than as a sixth seat at the table. The ensemble (2e) is the
right *ambition* and is unreachable on this timeline; its weights would be hand-set, which is the
artefact it claims to replace.

## 13. Interlock with the other five lenses

M5 should stop being a lens and become a **service layer plus one referee**. Concretely: hand the
calibration harness (PIT/CRPS/coverage on `20_prediction_ledger.csv`) to **all five** lenses as the
common scoring contract, so that M1 (structural mix state-space), M2 (nowcast tracker), M3 (guidance
game), M4 (bottom-up markets) and M6 (FX/take-rate/timing) each report an interval whose honesty is
measured the same way — this is the single thing M5 offers that no other lens does, and it is worth
more as shared plumbing than as a private forecast. Hand the `guide_id`-keyed language annotation to
**M3** as a conditioning descriptor on its 19/19 and 15/19 base rates, with the explicit caveat that
n = 19 and no fitted coefficient is claimed. Give **M1** the existing `06_wtp_hedonic_coefs.csv` (not a
new hedonic) as the joint-estimation input that satisfies audit recommendation 5, and let M1 own the
+3.62pp unidentified ADR residual as a **bound**, since M1 already owns regional ADR and nights weights
and is the only lens that can make geographic mix an output rather than a row. Give **M6** the Bayesian
structural take-rate component (2d.3) only as a *diagnostic* on its seasonal offsets — M6 should be
replacing the take rate with the booking-to-check-in kernel `phi` (audit recommendation 1), not
estimating a better take-rate seasonal, and the FX double-count in §1.3 above is avoided only if the
dollar enters the programme **once**, inside M6. Give **M4** the survivorship problem: the market-grain
review/listing work M5 wants is genuinely M4's job, under a DiD design around dated ordinance effective
dates (audit recommendation 9), where the identification comes from treatment timing rather than from a
frozen calibration. And the aggregation across lenses should be, for this competition, an explicit and
*declared* judgemental weighting with a sensitivity table — not an NNLS stack dressed as learning, on
ten correlated points, whose weights the team cannot honestly say were estimated.
