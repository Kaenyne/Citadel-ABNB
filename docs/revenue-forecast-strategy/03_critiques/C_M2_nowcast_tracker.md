# Critique C-M2 — "The Ledger Filter" (M2 nowcast tracker)

**Reviewer:** adversarial IC seat / econometrics. **Date:** 11 Sep 2026. **Target:**
`docs/revenue-forecast-strategy/02_proposals/M2_nowcast_tracker.md` (403 lines, read in full).
**Method:** every number below was recomputed or re-opened from the file cited. Commands are inline
where the result is load-bearing. `[recomputed]` = I ran it.

**Verdict: ADOPT WITH FIXES — but only the bottom half of the proposal.** The accounting core is the
right architecture and it is the audit's own recommendation 1/2/7. The alt-data measurement layer as
specified has three identification failures, one of which (B3) is anchored on a number that does not
exist, and the headline trade it sells is already sitting in the repo in a 30-line script with a
*larger* edge. Cut the filter down or it will not be built, and if it is built it will not be defended.

---

## 0. The one-line summary a PM would keep

*"Q4-26 revenue is ~85% already booked and ~82% FX-determined at the 5 Nov guide date; reconstruct
the booked base from lagged GBV, subtract the historical cushion, and the guide midpoint prints
below Street — which has been a 9/9, −4.2% 20-day short."* That sentence is correct, tradeable, and
**it does not require any of M2's state-space machinery.** It is already computed in
`analysis/src/h1_to_h2_bridge.py:288-320` and written to `data/processed/h2_bridge/h2_bridge_revenue_dollars.csv`:

```
4Q26  lagged_gbv 26.315bn  conversion 0.12030  revenue 3,165.6M
      hist_actual_vs_guide_mid_pct 3.88   implied_guide_mid_if_cushion_holds 3,047.4M   consensus 3,200.0M
```
**−4.77% vs Street, already in the repo, dated, reproducible.** M2's headline output is
$3.12–3.15bn = −1% to −2%, i.e. *a smaller edge than the file it builds on*, and the entire
difference is the cushion (1.79% trailing-8 median vs 3.88% Q4-specific), a parameter M2 explicitly
disowns ("the cushion is M3's object", §2.3). **M2 must state, in one line, what the filter adds to
`h2_bridge_revenue_dollars.csv`.** As written it adds posterior intervals and a p/π decomposition.
That may be worth three weeks; it is not worth three weeks *and* a 100-state Stan model.

---

## 1. Identification — score 4/10

### 1.1 φ is not identified by the evidence offered. The likelihood is flat. [recomputed]

§2.1 claims the kernel is "likelihood-anchored on six measured conversions — Q3 .17391/.17145/.17182,
Q4 .11946/.12117/.12026 … A 0.25pp three-year range on ~17% is a *tight* likelihood."

Two things are wrong with this.

**(a) It is circular.** Those six numbers are produced by `analysis/src/h1_to_h2_bridge.py:292-297`:

```python
def lagged_gbv(q): ...        # 2/3 * GBV(q-1) + 1/3 * GBV(q-2)   <- hard-coded
conv = {q: pq.revenue_musd[q] / (1000 * lagged_gbv(q)) for q in [...]}
```
The "measured" conversions are computed **using the 2/3–1/3 weights that φ is supposed to estimate.**
Citing them as a likelihood anchor for φ is citing the prior back to itself.

**(b) The likelihood is genuinely flat in φ₁.** I recomputed the conversion under every weight
w₁∈[0,1] from `02_kpi_panel_quarterly.csv` and measured three-year stability:

| w₁ (weight on GBV_{q−1}) | Q3 3-yr CV | Q4 3-yr CV |
|---|---|---|
| 0.00 | 0.0111 | 0.0073 |
| 0.33 | 0.0077 | 0.0055 |
| 0.50 | 0.0066 | **0.0053** |
| **0.67 (the prior)** | **0.0063** | 0.0058 |
| 0.80 | 0.0067 | 0.0066 |
| 1.00 | 0.0083 | 0.0082 |

Q3 prefers 0.67 by a coefficient of variation of 0.0063 against 0.0066 at w₁=0.50 — on **three
observations**. Q4 prefers **0.50**, not 0.67. A likelihood that moves by 5% of its own value across
the entire admissible range of the parameter, on n=3, is not identification; it is a prior with a
citation. The posterior on φ will be the `Dirichlet(60·(0.66,0.32,0.02))` prior essentially unchanged,
and the proposal's "posterior sd on φ₁ of roughly 0.06 before data" is what you get *after* data too.

**Why this matters beyond pedantry:** the proposal's central selling point is that it "replaces the
plug with the thing it is a proxy for" (§1.3). But τ·Σφ is one number per quarter-of-year — four
seasonal constants — which is *informationally identical* to the seasonal take rate it replaces.
For comparison [recomputed]: the raw take rate's 3-year CV is 0.0176 (Q3) / 0.0205 (Q4); the
lagged-GBV conversion's is 0.0063 / 0.0058. **The conversion is genuinely ~3× more stable — that is a
real result and it is the reason to do this.** But it is a result that already exists, and it is a
better *reduced form*, not a *mechanism*. Do not sell a re-parameterised seasonal constant as
structural identification to a judge who will ask "what does φ₂ = 0.32 predict that φ₂ = 0.50 does not?"
On your own numbers: nothing detectable.

### 1.2 The hidden plug: p_q and π_q saturate the two equations they are supposed to over-identify

§2.1 sells (A4) and (A5) as "two observation equations, two unknown prepayment shares, one shared
latent G → **identified**", and §4.1 claims "≈12 free parameters". The proposal's own Stan block
(§6) declares:

```stan
parameters { simplex[3] phi; real<lower=0> tau; vector[M] g;
             vector<lower=0,upper=1>[Q] p; vector<lower=0,upper=1>[Q] pi; real<lower=0> kap; ... }
```

`p` and `pi` are **free per quarter**. With Q=23 that is 46 free parameters, plus M≈78 monthly latent
states. Each of (A4) and (A5) has exactly one observation per quarter and exactly one free parameter
per quarter. **They are exactly identified — saturated — and contribute literally zero identifying
information about G, τ or φ.** p_q and π_q will absorb whatever residual the accounting identity
leaves, which is the definition of a plug. The audit's complaint about `13_driver_model.py:381-383`
("the residual of two regressions being used as the model's only timing term") applies verbatim to
M2's (A4)/(A5) as coded.

The over-identification the proposal is selling exists only if p and π are *restricted*. They must be
parameterised as low-dimensional functions of dated, observable events — RNPL rollout share and the
fee-migration share from `06_fee_timeline.csv` (20 rows, opened; carries the 15 Sep / 13 Oct 2026
dates) — with ≤3 free parameters each, plus a tight random walk. **This is the single most important
fix in this document.** Without it the "four over-identifying accounting observables" is two
observables and two plugs.

### 1.3 (A5) has an unobserved flow of the same order as the parameter

(A5) `FH_q = FH_{q−1} + (1−τ)·π_q·G^gross_q − Payouts_q − GuestRefunds_q`. **Payouts are not
disclosed.** Neither are guest refunds. Funds held for clients also contains lodging/occupancy taxes
Airbnb collects and remits on hosts' behalf, whose remittance calendar is jurisdictional and seasonal
and has nothing to do with π. So (A5) is one observation with three unknown flows. The only way to
close it is to assert Payouts_q = (1−τ)·Σφ·Ĝ (payout at check-in) — which re-uses φ and makes (A5) a
*restatement* of (A3), not an independent equation. Say so explicitly, or drop (A5) and estimate π
from nothing. Either is honest; "two equations, two unknowns" is not.

**Same for (A4):** verify against the 10-Q whether `unearned_fees` is pure deferred booking fees or
includes gift cards / Airbnb credits. `abnb_backlog_indicators.csv` (opened, 23 data rows) tags the
XBRL element as `DeferredRevenueCurrent`, which is broader than "fees". If it includes gift-card
liability the (A4) denominator argument ("fee-denominated, ~13-15% of GBV") is wrong at the margin
that p is estimated off.

### 1.4 A(d) is not cross-sectionally identified — it is the age-period-cohort problem [recomputed]

§2.2: "For a fixed calendar month … markets differ only in `d`. Regressing … on `d_{i,May}` across 120
markets recovers `A(d)` **cross-sectionally, with no time-series degrees of freedom consumed**."

By construction `d_{i,m} = scrape_i − monthend_m`. The model (B1) already contains a market effect
`α_i` (a function of `scrape_i` alone) and a platform-month effect `ω_m` (a function of `m` alone).
**`d` is exactly additively separable in the two fixed effects.** Any linear component of `log A(d)`
is absorbed by `α_i + ω_m` and is *not identified*. Only the **curvature** of A is identified, and
only through functional form. This is the textbook age = period − cohort collinearity and the
proposal does not mention it.

Worse, the variation is not what is claimed. The proposal states the spread is "2026-06-05 (Los
Angeles) through 2026-07-24 (Buenos Aires) — 50 days … verified in `booking_curves_by_market.csv`
(`snapshot_date` column, 601 rows)". I opened that file (601 rows confirmed):

```
snapshot range 2026-06-14 .. 2026-08-10     (not 2026-06-05 .. 2026-07-24)
```
and from `market_snapshot_panel.csv` (231 rows, opened) for `current_2026`, 115 markets:

```
88.7% of markets scraped on or before 2026-06-30;  IQR of scrape dates = 7 days
tail: 2026-07-12(1) 07-14(3) 07-15(1) 07-16(3) 07-20(1) 07-21(1) 07-24(1) 07-26(1) 08-10(1)
```

**The "50-day cross-sectional experiment" is a 7-day interquartile spread plus a 13-market tail.**
The accrual curve over the 0–60 day window — exactly the window where censoring runs from 95% to 5%
(1.81m May → 1.10m Jun → 0.10m Jul → 3.1k Aug in `abnb_party_size_reviews_v2_global_month.csv`,
165 rows, opened and confirmed) — is being fitted off ~13 markets that are not randomly selected.
The cited number contradicts the cited file. That is the kind of error that ends a hostile Q&A.

### 1.5 (B3) — the constraint that pins ω — is anchored on a number that is not disclosed, and its LatAm/APAC are transposed

§2.2 (B3): "annual Σ_m n̂_{r,m} = **the 10-K regional nights** (2025: NA 158m, EMEA 215m, LatAm 90m,
APAC 70m)". This is presented as the hard constraint that stops the review index free-floating and
is the *only* device pinning ω, the review-per-stay drift.

**Airbnb does not disclose regional nights.** The repo says so in its own ground truth:
`01_ground-truth/01_data_inventory.md:136` — *"No hard regional nights (only disclosed low/high/mid
bands since 3Q22 …) — Cannot be filled with new data in 3 weeks — Airbnb doesn't disclose it."*
`10_regional_panel_quarterly.csv` (23 data rows, opened) carries only `{r}_nights_share_est_pct`
— an **estimate** built from XBRL regional revenue divided by the fixed `IDX` deflator, i.e. precisely
the FX-contaminated plug that `02_model_audit.md` §3.2 condemns — plus
`na_share_of_nights_pct_disclosed = 30.0`, which goes NaN after 3Q25.

And the numbers do not match the repo. 158/215/90/70 sums to 533m (= FY25 nights, correct) but
implies LatAm 16.9% / APAC 13.1%. The repo's own 4Q25 panel row reads **LatAm 14.0 / APAC 16.1**.
**LatAm and APAC are transposed.**

Consequence: (B3) is a plug built on a plug, with two regions swapped. The proposal's four-device
anti-overlap architecture (§2.4) rests on device 2, and device 2 rests on this. Fix: replace (B3)
with the interval-censored band likelihood applied at annual frequency (which you already have as
device 3), and accept that ω is then weakly identified — and say so.

### 1.6 Concrete double count the "one latent" architecture does not prevent

The claim (§2.4.1): "Adding a fifth indicator **cannot** double count volume; it can only shrink the
posterior variance of `f`." **That is true if and only if the measurement-error covariance H is
diagonal and correctly specified.** It is not.

*The case.* Spain tightens its national STR registry; ~40k listings are deregistered in H2 2026.
(i) Inside Airbnb's Spanish market scrapes lose those listings → the review index for EMEA falls.
(ii) Eurostat's platform-nights series for Spain is collected *from the platforms under the same
registration regime* → EU27 platform nights fall. (iii) Spain INE arrivals are unaffected (hotel
substitution), but the proposal loads INE on f_EMEA too. Indicators (i) and (ii) share a common,
non-demand shock. With H diagonal the filter treats them as two independent draws, so the posterior
mean of f_EMEA is pulled twice by one shock and the posterior variance is understated by roughly a
factor (1+ρ) — with ρ plausibly 0.5–0.8 here, the effective precision is overstated ~1.5–1.8×.
**This is double counting, inside a "measurement-only" architecture, in the mean and the variance.**
The survivorship correction 1/S does *not* fix it: S is estimated from the same scrapes, so the
correction is itself a function of the shock.

The same structure applies to the pickup indicator and the review indicator, which come from the same
two scrapes of the same listing universe.

*Fix:* either (a) estimate a non-diagonal H with a single common "scrape/regime" factor loading on
every Inside-Airbnb-derived indicator, or (b) admit that Inside Airbnb reviews + Inside Airbnb pickup
are **one** indicator with two views and give them one shared error term. M4's ordinance treatment
flags ("down-weight treated markets", §9) are a band-aid, not a covariance.

### 1.7 Reviews count reservations, not nights — the loading β is not a constant

§2.2 defines the latent as `f^r_m ≡ log(Σ_ℓ φ_ℓ Ĝ^r_{m−ℓ} / ADR^r_m)` — **completed stay-nights** —
and measures it with review counts. A review is posted once per *reservation*, not once per night.
R measures reservations; f measures nights; the ratio is 1/ALOS. Airbnb's long-term-stay share fell
20.2% (2022) → 13.4% (2025), which the proposal itself cites in failure mode 8 — a mix shift that
mechanically **raises reviews per night** by roughly 1–2% a year with no change in demand.

The proposal's ω absorbs *review-rate* drift, not ALOS drift, and ω is pinned by (B3), which §1.5
above shows is a plug and which in any case **cannot be imposed on 2026 or 2027 — the forecast years
have no annual anchor.** So in exactly the window that matters, the review index carries an
unbounded, signed, ALOS-driven drift. The proposal's own sensitivity (±2pp/yr of drift = ±0.6pp of
nights growth at β≈0.3) is a third of the nights-surprise sd and this is a *second*, uncounted
source of the same drift. Fix: build the index as reviews **× measured ALOS** from the quote/LOS work
(`adr/14a-c`, `2026-09-09_los_synthesis.md`), or state that β is time-varying and put a random walk on it.

### 1.8 Survivorship: 1/S is the wrong correction

The survivorship point is correct and important — a current-vintage review series does manufacture
growth. But the fix is mis-specified. `S_i` as proposed is a **listing-count** survival
(`count(c.id)/count(*)` in the §6 skeleton, and the cross-checks quoted — Common Crawl 86–88%,
six-city retention 75.5%→73.4% in `11_supply_economics.csv`, 81 rows, opened — are all listing-count
survival). Delisting is concentrated in low-occupancy, low-review listings. **Review-weighted survival
is strictly higher than listing-count survival**, so dividing review counts by listing-count S
over-corrects history upward and *understates* recent growth — the opposite sign to the error being
fixed, and of the same order (several pp).

This is trivially fixable with the data on disk: the 2025 listings carry `number_of_reviews_ltm`
(col 58, verified by `gzcat` on `.../inside_airbnb_yoy_2025/austria/vienna/vienna/2025-09-14/listings.csv.gz`),
so review-weighted survival `Σ_{survivors} reviews_ltm / Σ_{all} reviews_ltm` is a one-line query.
**Use that, not 1/S_listings.** Also `rev["age_years"]` in the §6 skeleton is used and never defined.

---

## 2. Point-in-time safety and backtest validity — score 4/10

Credit where due: §4.4 states the main PIT hole before a reader finds it, names the optimism bound,
uses `02_metric_coverage.csv` (74 data rows, opened) and `02_disclosure_changes.csv` (23 rows,
opened) for truncation, forbids substituting the Zacks 4-Sep vintage into the 6-Aug LSEG feature
(`20_frozen_q3_2026.csv`, opened, carries exactly that warning), and insists on `open_*` returns.
That is better discipline than most of what the repo contains. But:

### 2.1 The "one genuinely point-in-time replay" does not exist as described

§4.4(a): "`listing_snapshots prior_2025` gives a real Sep-Nov 2025 vintage across 115 markets —
replay the 3Q25 guide date with it."

Two problems, both verified.

**(a) 21 of the 115 prior_2025 markets were scraped AFTER the 3Q25 print. [recomputed]** From
`market_snapshot_panel.csv`:
```
prior_2025 range: 2025-06-23 .. 2025-12-31       (proposal claims 2025-09-22 .. 2025-11-12)
by month: 2025-06: 1 | 2025-09: 91 | 2025-10: 1 | 2025-11: 9 | 2025-12: 13
scraped after 2025-11-06 (the 3Q25 print date): 21 of 115
```
An 18% look-ahead leak in the one date the proposal calls "genuinely point-in-time". Fixable by
dropping those markets — but then the replay is on 94 markets, not 115, and the proposal's stated
vintage range is simply wrong against the file it cites.

**(b) The 2025 vintage contains no review events.** I enumerated the raw store:
```
find .../inside_airbnb_yoy_2025/ -name '*.gz' | sed 's|.*/||' | sort | uniq -c
   115 listings.csv.gz
```
**115 listings files, zero reviews files.** The 2025 vintage supports `number_of_reviews`,
`number_of_reviews_ltm`, `number_of_reviews_l30d`, `number_of_reviews_ly`, `last_review` — i.e. two
or three *window aggregates* per listing at one date. It does **not** support the month-by-month
review-event panel (B1) is built on, and it cannot be run through A(d) at all because there is no
`date` field per review.

So the "one true out-of-sample vintage" replays a **different estimator** (an LTM/L30D aggregate)
from the one being scored live (accrual-corrected monthly event counts). That is not a point-in-time
replay of the model; it is a point-in-time replay of the *feature the repo already tested and which
already failed*. The honest sentence is: **zero true replays of this estimator, one true replay of a
coarser proxy on 94 markets, seven truncation replays, one live pre-registered call.** The proposal
should say that.

### 2.2 The consensus series splices vendors mid-sample [recomputed]

From `16_consensus_at_print_merged.csv` (23 data rows, opened), restricting to 2022Q3+ as the
proposal does: `cons_revenue_vendor` = Refinitiv ×4 (2022Q3–2023Q2), LSEG ×12 (2023Q3–2026Q2); same
for `next_q_cons_vendor`. The proposal's §4.4(2) rule — "Consensus = the vendor vintage dated before
D … Never mix vintages" — is satisfied *within* a date but violated *across* the sample: the target
T1 changes definition at 2023Q3. The Refinitiv→LSEG transition is also where the guide-vs-Street
series flips from a +2 to +6% regime to a −3 to +3% regime (see the printout in §3 below). At n=16,
four observations under a different vendor convention is 25% of the sample. Report T1 results with
and without the four Refinitiv rows.

### 2.3 The proposal's own stats check out — that part is clean [recomputed]

```
2022Q3+: revenue_surprise n=16 mean +1.714 sd 1.099 | nights n=13 mean +0.678 sd 1.527
         guide_vs_street n=16 mean +0.629 sd 2.485
```
Exactly as claimed. So do `h2_bridge_gbv_lag_conversion.csv` (6 rows, values exact),
`02_kpi_panel_quarterly.csv` (24 rows; `funds_held_for_clients_musd` col 31, `unearned_fees_musd`
col 32, `take_rate_pct` col 82 — note the §6 code comment reverses 31/32), `10_fx_daily.csv`
(19,467 data rows), `28_fx_hedge_disclosures.csv` (14 rows), `06_fee_timeline.csv` (19 rows),
`02_guidance_cushion_series.csv` (19 rows; trailing-8 median = 1.79% confirmed),
`coverage_summary.csv` (67,500,188 review rows / 588,120,594 calendar rows / prior_2025 1,458,929 vs
current_2026 1,494,056 — all confirmed). `10_eurostat_platform_monthly_latest.csv` is 39 data rows ×
**69** columns, not the "71 country columns"/"34 countries" the proposal gives in two places.

---

## 3. Statistical power and overfitting — score 5/10

### 3.1 The free-parameter count is understated by roughly 10×

§4.1 says "≈12 free parameters". The §6 skeleton declares: `simplex[3] phi` (2), `tau` (1),
`vector[M] g` (M≈78 monthly latent states), `vector[Q] p` (23), `vector[Q] pi` (23), `kap`, plus
per-market `α_i` (115), `s_{i,mo}` (115×12 shrunk), `β_i` (115), `ω_m` (~54), four observation-noise
scales, the cushion block. Even counting only the Stan block: **≈130 estimated quantities against 23
quarterly observations per accounting series.** Hierarchical shrinkage and informative priors make
this *estimable*; they do not make it 12 parameters, and a Citadel PM who reads the skeleton will
notice the gap between the prose and the code. Report the effective number of parameters (p_WAIC or
p_loo), not a hand count.

### 3.2 "~4,100 market-months" does not buy power for the decision-relevant parameters

§4.3 argues the n=16 problem is dodged because "the decision rule is the posterior of the accounting
core, whose parameters are identified off ~4,100 market-months and ~42 monthly state transitions per
region."

Both halves are wrong. The 4,100 market-months identify A(d), S and the *within-region* index shape —
none of which appear in `Base_D = τ̂ · Σ_ℓ φ̂_ℓ Ĝ_{D−ℓ} · FX`. τ, φ, and the level of Ĝ are identified
by quarterly observations only: n=23 (n=16 post-regime-change). And "42 monthly state transitions" is
not 42 observations — with only quarterly observations, the monthly states are **interpolations**;
the state equation contributes prior information, not likelihood. The effective sample for the
decision parameters is 16–23, exactly as the audit's §4.2(d) says it is ("**binding**, not fixable by
a better feature").

The proposal half-concedes this ("the pre-registered claim is a **calibration claim**") and that
concession is the right one. But then the interval coverage claim needs a power statement of its own:
with 8 backtest residuals, a split-conformal 80% band has coverage estimated to ±~14pp. You cannot
demonstrate calibration on n=8 either. Say the honest thing: **the model is defended on mechanism and
on one live pre-registered call, not on a backtest.**

### 3.3 Selective citation of the two numbers that carry the alt-data case

This is the most serious presentational problem and a judge with the CSVs will find it.

**(a) Inside Airbnb.** §4.6 says `ia_reviews_ltm_matched_yoy → nights_yoy` has
"`wf_ratio_vs_naive 0.947`, `wf_ratio_vs_ar1 0.964`, sign accuracy 0.714 … the nearest thing to a
survivor". From `08_ia_tests.csv` (opened), the *same feature/target pair* in the second evaluation
window (`2023Q1..2026Q2, WF from 2024Q1`):

```
wf_ratio_vs_naive 0.9467   wf_ratio_vs_ar1 1.2128   pearson_r 0.374  p 0.257  perm_p 0.266
```
**It loses to AR(1) by 21% in window 2.** The proposal itself endorses the repo's rule — "a rule that
fails either is dead" (§4.4) — and then quotes only the window-1 AR(1) ratio. By its own stated
standard this feature is dead. Quote both windows or drop the claim.

**(b) Eurostat.** §2.2 says lag-0 → `emea_nights_band` has "r = 0.961 and a walk-forward RMSE ratio of
**0.476× AR(1)** (n=9, wf_n=5)". From `08_eurostat_tests.csv` (opened), same row:

```
wf_rmse 3.083  wf_rmse_naive 3.286  wf_rmse_ar1 6.476
wf_ratio_vs_naive 0.938   wf_ratio_vs_ar1 0.476   wf_n 5   wf_sign_n 3
```
The 0.476 is an artefact of an AR(1) that is itself twice as bad as naive on this series. **Against
naive the ratio is 0.938 — parity — on five walk-forward points.** Citing the AR(1) ratio and not the
naive ratio is exactly the selection the audit's §4.2 was written to stop.

**(c) The frozen card.** §4.6 says the IA feature "carries the **lowest residual sd of any feature on
both targets** — 1.1714 (nights) and 1.1362 (revenue) … against the designated trailing-4 baseline's
1.2078 and 0.9169." Both numbers are in `20_frozen_q3_2026.csv` and are correct. But on **revenue the
baseline wins outright** (0.9169 < 1.1362), and the residual sds are in-sample on n_train 10–11.
The proposal prints the numbers and lets the framing do the work. A PM will read it as "the feature
beats the baseline on both." It does not.

### 3.4 The target choice is right, and the power argument for it is right

Credit: sd(guide-vs-Street) 2.485pp vs sd(revenue surprise) 1.099pp is verified, and choosing the
higher-variance target at fixed R² is the correct response to the repo's `pred_sd/actual_sd ≈ 0.2`
pathology. Forecasting a **level** (Base_D) and differencing against Street only at the end is the
correct structural fix for the "wrong target" failure the audit calls the programme's central error.
**Keep this regardless of what happens to the rest.**

One caveat the proposal misses: the cushion's own dispersion caps the achievable R² on T1.
[recomputed] The last eight `pct_distance_from_mid` values are 0.86 / 2.69 / 0.98 / 2.52 / 0.86 /
3.27 / 2.61 / 1.06 → mean 1.856, **sd 1.006pp**. Even with a perfect Base_D and a perfect Street
pull, the irreducible sd on T1 is ~1.0pp against a target sd of 2.485pp — max R² ≈ 0.84, and that
assumes the cushion is drawn from its own history. The proposal's prior is `μ_c ~ N(0.0179, 0.005²)`,
which puts sd 0.5pp on the *mean* and silently omits the 1.0pp draw variance. Fix the prior.

---

## 4. Tradeability — score 7/10

The strongest axis. The output maps to a trade: `Pr(guide_mid < Street × 0.99)` is an explicit
trigger for a rule with 9/9 sign, mean −4.21% on next-open entry over 20 days
(`09_stock-behaviour-and-alpha.md` convention preserved). The three-branch scenario tree with
probabilities read off the posterior is the right memo object. The mechanism for why the Street is
wrong is stated, dated and arithmetic (Q4 FX ~82% determined, −3.4pp step), and
`04_current_consensus.csv` (opened) confirms the Street evidence: **Q4-26 Zacks $3,200m, 10 estimates,
low $3,050m / high $3,700m** — a 20% spread on a quarter that is mostly already booked. That is a
real, checkable dispersion argument.

Four deductions:

1. **The edge already exists and is bigger without the model** (§0). M2's $3.12–3.15bn is *less*
   bearish than `h2_bridge_revenue_dollars.csv`'s $3,047m, and the gap is a cushion choice, not a
   filter output.
2. **M2 cannot produce its own primary target.** `guide_mid = Base_D × (1+g_new) × (1−c_D)`; c_D is
   M3's, g_new is unspecified. M2 standalone delivers Base_D. Present it that way.
3. **n=9 on the drift rule, and the events are not independent of the mechanism.** The proposal's
   mechanism for the Q4 call is FX; several of the nine guide-below-Street events are FX-driven
   quarters. The proposal concedes the M6 overlap (risk 8) but not this one: the conditioning variable
   and the mechanism share a common driver, so the 9/9 record is not 9 independent draws on the
   hypothesis being traded. Size it as **one** bet with a wide prior on the drift magnitude.
4. **Nothing resolves before the finals.** Prelims 2 Oct, finals 22–24 Oct, print 5 Nov. The
   pre-registered card is a virtue (it is falsifiable and dated) but the judges see zero realised
   evidence. Lead the memo with the arithmetic, not with the card.

---

## 5. Buildability in three weeks by 3–4 undergraduates — score 4/10

**What is genuinely on disk and cheap:** `review_events.parquet` (909MB, 67.5m rows) is one DuckDB
query; the id-level 2025↔2026 survival match is one join; `listing_snapshots.csv` is 1.45GB and reads
fine; all repo CSVs opened without incident. `analysis/src/build_booking_curves.py` (79 lines) and
`data/manifests/inside_airbnb_download_log.csv` (258 rows) exist, so the second capture is a real
Day-1 action and should start regardless of what else is cut.

**What will not be built in three weeks:** the Stan model. It is not "linear-Gaussian" as §4.1 claims
— (A1) and (A3) sum *levels* of exponentiated log-states within a quarter, and (A3) multiplies τ × φ ×
G × an FX ratio. Mixed-frequency aggregation of a log-level state is the standard Mariano–Murasawa
*approximation* (geometric mean), not "exact"; the proposal claims exactness and then writes a
nonlinear model. With ~78 monthly latent states, 23 per-quarter p and π, a simplex, interval-censored
terms and a hierarchical 115-market block, HMC will be slow and divergence-prone, and the team has no
one who has debugged a non-identified Stan posterior before. The Day-5 gate is well designed and the
honest expectation is that it fails, at which point three weeks are gone.

**Minimum viable version that keeps the edge (my recommendation):**

1. Accounting core in `statsmodels`/`numpy`, quarterly only, ~6 parameters: four seasonal
   conversions (= τ·Σφ by quarter-of-year, already measured), a fee-migration τ step from
   `06_fee_timeline.csv`, one FX object from `10_fx_daily.csv`. **This reproduces the h2 bridge and
   the audit's recommendation 1 and is 200 lines.**
2. The regional nights panel as a small constrained state space with the **interval-censored band
   likelihood** (device 3). This is the audit's recommendation 2 and it is genuinely novel vs the
   repo's `_mid` regressions. ~150 lines, `scipy.optimize`.
3. Survivorship + accrual correction on the review panel, **review-weighted**, delivered as a
   descriptive exhibit and a *diagnostic*, not as a filter input.
4. The pre-registered card and the conformal band on whatever residuals exist.

That MVP keeps 100% of the tradeable edge and roughly 0% of the Stan risk. The Bayesian filter is a
week-4-if-it-exists item.

**Cut order disagreement:** §7 lists "the survivorship correction, the accrual correction, the
adding-up constraints, and the pre-registration" as uncuttable. Given §1.5, the adding-up constraint
as specified is a plug and should be *replaced*, not protected. And the accrual correction should be
cut before the accounting core, not after.

---

## 6. Defensibility in a 2-page memo and 10-minute Q&A — score 6/10

§8's ten pre-empted questions are the best part of the document and genuinely raise the floor. The
"one true vintage, seven flagged truncation replays, one live pre-registered call" formulation is the
right register.

**The first number a judge attacks:** *"Your Q4 guide midpoint is $3.12–3.15bn against Street
$3.16–3.20bn. That is a 1–2% gap. What is your standard error?"* The proposal's own T1 target sd is
2.485pp, the cushion alone contributes ~1.0pp, and the conformal band is built on eight residuals.
**The claimed edge is smaller than the stated uncertainty.** The proposal does not give the answer.

The answer it *should* give — and this is the strongest available defence — is that the **sign**, not
the magnitude, is what is robust: the base is $3.18–3.21bn, the cushion has been positive **19 of 19
times** with a minimum of 0.86% (`02_guidance_cushion_series.csv`, opened, verified), so
guide_mid < base always, and base is already at/below Street's $3,200m. Pr(guide below Street) is
therefore high *for a mechanical reason that does not depend on the filter at all*. Lead with that.

**The second attack:** *"Where does your regional nights constraint come from?"* — and §1.5 above is
what happens next. Fix (B3) before anyone reads it.

**Third:** §8.1's defence of the review index ("nights per average active listing has been
62.5/62.7/62.6/62.7 in 2022-25 — four years of listings exactly absorbing nights") is built on a
series whose own note in `11_supply_economics.csv` reads *"listing levels rounded as disclosed;
'over X million' treated as X"*, and whose 2025 row says *"listings growth 12% vs nights growth 8%"*
— which cannot produce a flat ratio. **The stability is a rounding artefact.** Drop that argument;
it is the weakest sentence in the document and it is in the Q&A section.

---

## 7. Refutation attempts

| # | Claim under test | Attack | Outcome |
|---|---|---|---|
| 1 | "φ is likelihood-anchored on six measured conversions; a 0.25pp range on 17% is a tight likelihood" | Recomputed conversion CV across w₁∈[0,1] from `02_kpi_panel_quarterly.csv`: 0.0063 at 2/3 vs 0.0066 at 0.5 vs 0.0077 at 1/3 (Q3); Q4 *prefers* 0.5. And the six numbers are generated by `h1_to_h2_bridge.py:292` using the 2/3–1/3 weights themselves. | **REFUTED** — φ is a prior, and the anchor is circular |
| 2 | "(A4) and (A5) are over-identifying: two equations, two unknowns → identified" | The §6 Stan block declares `vector[Q] p` and `vector[Q] pi` — one free parameter per quarter per equation. Both equations are saturated and contribute zero identifying information. Payouts and guest refunds in (A5) are undisclosed, adding a third unknown flow. | **REFUTED** as written; recoverable only by restricting p, π to ≤3 parameters each on dated event shares |
| 3 | "A(d) is identified cross-sectionally off a 50-day scrape spread, zero time-series dof consumed" | d = scrape_i − monthend_m is additively separable in the market and month effects the same equation already contains (age-period-cohort); only curvature is identified. And the spread is not 50 days: `booking_curves_by_market.csv` runs 2026-06-14..08-10 and `market_snapshot_panel.csv` shows 88.7% of markets scraped by 06-30, IQR 7 days, with 13 markets in the tail. | **REFUTED** — cited file contradicts cited number, and the design is collinear with the model's own FE |
| 4 | "(B3) pins ω against 10-K regional nights (NA 158 / EMEA 215 / LatAm 90 / APAC 70)" | Airbnb does not disclose regional nights (`01_data_inventory.md:136`); `10_regional_panel_quarterly.csv` carries only `{r}_nights_share_est_pct`, derived from XBRL revenue ÷ a fixed ADR index — the FX-contaminated plug `02_model_audit.md` §3.2 condemns. The quoted split implies LatAm 16.9% / APAC 13.1% against the repo's 14.0 / 16.1: transposed. | **REFUTED** — the anti-free-float device is a plug, with two regions swapped |
| 5 | "One genuinely point-in-time replay exists at the 3Q25 guide date from prior_2025" | `market_snapshot_panel.csv`: prior_2025 runs 2025-06-23..2025-12-31 (not 09-22..11-12), and **21 of 115 markets were scraped after the 2025-11-06 print**. `find` over the raw store returns **115 `listings.csv.gz` and zero `reviews` files** — so the 2025 vintage cannot produce a monthly review-event panel at all, only LTM/L30D aggregates. | **REFUTED** — the replay is of a different, coarser estimator, on 94 clean markets at best |
| 6 | "Adding a fifth indicator cannot double count; it can only shrink posterior variance" | True only under diagonal, correctly specified H. Reviews and Eurostat share a common registration/regulatory shock (Spain registry case); pickup and reviews come from the same two scrapes. Correlated measurement error pulls the state twice and understates posterior variance by ~(1+ρ). | **PARTIALLY** — the architecture is right, the covariance assumption defeats it; fixable with one common scrape factor in H |
| 7 | "Inside Airbnb reviews are the nearest thing to a survivor (0.947× naive, 0.964× AR(1))" | `08_ia_tests.csv` window 2 (WF from 2024Q1): `wf_ratio_vs_ar1 = 1.2128`, r 0.374, p 0.257, perm_p 0.266. Fails the proposal's own two-window rule. Frozen-card resid sd 1.1362 on revenue loses to the trailing-4 baseline's 0.9169. | **REFUTED as cited** — the concept may survive at the new grain, the evidence quoted does not |
| 8 | "Eurostat lag-0 is extraordinarily informative: 0.476× AR(1)" | Same row of `08_eurostat_tests.csv`: `wf_ratio_vs_naive 0.938`, wf_n 5, wf_sign_n 3. The 0.476 is relative to an AR(1) that is 1.97× worse than naive. Also, the company's own quarterly EMEA band at q−1 is fresher than a 5-month-lagged Eurostat print, so the incremental information is near zero. | **REFUTED** — ratio-shopping |
| 9 | "This forecasts the guide, which is what the stock trades on, and Street's $3,050–3,700m range proves the arithmetic isn't being done" | Verified in `04_current_consensus.csv` (Zacks 4 Sep, 10 estimates, low 3,050 high 3,700). The target choice and the dispersion argument both hold. | **SURVIVED** |
| 10 | "It replaces the take-rate plug with a mechanism, retiring the +1.05pp trailing-4 bias" | The bias fix is real — dividing out the prior-year wedge and using one FX object is correct and is the audit's §3.1 finding. But the replacement object (four seasonal τ·Σφ constants) carries the same degrees of freedom as a seasonal take rate; the gain is *stability* (CV 0.006 vs 0.019, recomputed), not *mechanism*. | **PARTIALLY** — real improvement, oversold as structural |
| 11 | "Reviews measure the revenue-recognition numerator because they are posted after check-out" | Timing is right; units are not. Reviews count reservations, not nights; the ALOS mix has moved (LTS 20.2%→13.4%) so reviews-per-night drifts, and ω is pinned by (B3), which cannot be imposed in the forecast years. | **PARTIALLY** — fix by multiplying the index by measured ALOS, or put a random walk on β |
| 12 | "≈12 free parameters" | The §6 Stan block declares ≈130 estimated quantities (78 monthly states + 46 p/π + simplex + 115 α_i + 115 β_i + ω_m + scales). | **REFUTED** — report p_loo, not a hand count |

---

## 8. Fatal flaws

1. **(B3) is anchored on a non-existent disclosure with LatAm and APAC transposed.** The device that
   prevents the alt-data index free-floating rests on a number the repo's own ground truth says does
   not exist, derived from the FX-contaminated share plug the audit condemns. Until this is replaced
   the "one latent, measurements only" architecture does not do what it claims.
2. **p_q and π_q saturate (A4) and (A5).** The over-identification that is the proposal's core
   identification argument does not exist in the model as coded.
3. **The "one true PIT replay" is not a replay of this estimator.** 115 listings files, zero reviews
   files in the 2025 store; 21/115 markets post-date the print. The backtest is weaker than the
   proposal's already-discounted description of it.

None of the three is fatal to the *programme*; all three are fatal to the *claims as written*, which
for a Citadel Q&A is the same thing.

## 9. Must-fix (in priority order)

1. Replace (B3) with an annual interval-censored band constraint; delete every reference to "10-K
   regional nights"; state that ω is weakly identified in the forecast years and carry it as a
   scenario axis with a stated ±2pp/yr bound.
2. Restrict p and π to ≤3 parameters each, driven by the dated RNPL/fee-migration shares in
   `06_fee_timeline.csv`, plus a tight random walk. Show the (A4)/(A5) residuals are non-zero
   afterwards, i.e. that the equations bind.
3. Either drop (A5) or state explicitly that Payouts_q is imputed as `(1−τ)·Σφ·Ĝ` and is therefore a
   restatement of (A3), not an independent observation. Verify the XBRL content of `unearned_fees`
   (gift cards?) against the 10-Q before using it as a fee-denominated series.
4. Benchmark **against `h2_bridge_revenue_dollars.csv`**, not against the take-rate carry. If the
   filter's Base_D does not beat the four seasonal conversion constants out of sample, say so and
   ship the conversion.
5. Correct the A(d) section: state the age-period-cohort collinearity, report the real scrape
   distribution (IQR 7 days, 13-market tail), and identify A only through curvature with a stated
   functional form and a region random effect.
6. Make survivorship **review-weighted** (`number_of_reviews_ltm` on the id-matched vintages), not
   listing-count. One query; the current 1/S has the wrong sign of bias.
7. Multiply the review index by measured ALOS, or put a random walk on β. Reviews are reservations.
8. Quote both evaluation windows for every alt-data statistic (IA window-2 AR(1) ratio 1.2128;
   Eurostat naive ratio 0.938, wf_n 5). Remove any ratio quoted only against the comparator it beats.
9. Put the cushion's **draw** sd (1.006pp, recomputed) into the T1 uncertainty, not just the 0.5pp
   prior sd on its mean. Then state Pr(guide < Street) honestly — it will be driven by the 19/19
   positive-cushion base rate, which is the defensible part.
10. Drop the `nights per active listing 62.5/62.7/62.6/62.7` defence (rounded denominator; the source
    note contradicts it).
11. Report effective parameters (p_loo/p_WAIC), not "≈12".
12. Fix the §6 skeleton: UF/FH column comment is reversed vs `02_kpi_panel_quarterly.csv` (31 = funds
    held, 32 = unearned fees); `age_years` is used and never defined; label the Mariano–Murasawa
    aggregation an approximation, not exact.

## 10. What to keep even if the whole is rejected

1. **The target.** Forecast the guide midpoint as a % distance from print-day Street (sd 2.485pp),
   built by forecasting a **level** and differencing at the last step. This is the correct structural
   answer to the programme's single largest documented failure, and it is verified.
2. **Base_D as an object.** "Revenue already on the booking ledger at the guide date" is the right
   unit of analysis, is defensible in one sentence, and is what makes the FY27 and Q4 calls mechanism-
   driven rather than extrapolative.
3. **Interval-censored likelihood on the disclosed regional bands** in place of `_mid` regressions.
   Cheap, correct, novel relative to the repo, and it turns band width into a posterior interval.
4. **Survivorship and censoring corrections on any current-vintage review series** — the diagnosis is
   right even though the estimator needs fixing, and it very likely contaminates the existing
   `ia_reviews_ltm_matched_yoy` feature that the frozen card is carrying live.
5. **Second Inside Airbnb capture on Day 1.** Free, irreversible clock, pipeline exists. Do it today
   regardless of which proposal wins.
6. **The p vs π separation as a research question** — fee-denominated unearned fees vs
   amount-denominated funds held is a genuinely sharp observation about the 3Q26 10-Q, even if the
   estimator that answers it has to be simpler than a state space.
7. **Pre-registration with a dated, scored card** (`ABNB-M2-v1`, scored 6 Nov). Worth more in a Q&A
   than any backtest this dataset can support.
8. **The §8 hostile-Q&A format.** Adopt it across all six proposals.

## 11. How this lens should interlock

M2 is not a standalone pitch and should not be presented as one. Its deliverable to the team is a
single number with a posterior — **Base_D, the revenue already determined at the guide date** — plus
the φ kernel and the monthly regional nights state. M3 owns the cushion c_D and therefore owns the
conversion from Base_D to a guide midpoint; M2 must stop quoting guide midpoints as its own output,
because every dollar of the difference between its $3.12–3.15bn and the repo's existing $3,047m is
M3's parameter. M6 owns the two FX objects, and the Q4 call is **one** trade shared with M6, not two
converging pieces of evidence — the memo must size it once. M1 should consume M2's nights weights and
return regional ADRs so geographic mix becomes an identity; that closes the 1.13pp / ~$175M gap the
audit documents and is the highest-value interlock in the set. M4 owns the ordinance treatment flags
that must enter the review index's *covariance*, not just as a down-weight. M5 competes on M2's
pre-registered card. The practical sequencing: build M2's accounting core first because M1, M3 and M6
all consume it; build the alt-data measurement layer last, because on the evidence recomputed above
it is the part most likely not to survive contact with its own backtest.
