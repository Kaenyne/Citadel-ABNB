# 01 — Method cards, one per adopted component

Head of research, 11 Sep 2026. Companion to `00_INTEGRATED_SYSTEM.md`. One card per adopted lens, in build
order. M4 is not a lens and gets a card for its three surviving artefacts. Every path below was opened.

Shared conventions for all cards:

- **Interface schema** on every file crossing a layer boundary:
  `quarter, region, line, variable, value, unit, basis, vintage, source_path, knowable_from`.
  `basis ∈ {filed, letter_bucket, letter_integer, back_out, derived, modelled, assumed}`.
  **`derived` rows are never used as observations.**
- **Windows:** W1 = 1Q23+ (n=14 guide dates), W2 = 1Q24+ (n=10). A result must survive both to be quoted.
- **Baselines:** naive/AR(1); trailing-4 mean; guide + trailing-8 cushion; **the free pre-guide Street
  consensus**.
- **Owners:** P1 core engine, P2 data/panel, P3 FX+take rate (Python and R), P4 challengers/consensus,
  W writing, X Excel. Four people; P4 and W can be the same person.

---

## Card 1 — M6 · The recognition kernel, the fee schedule and the FX date-stamp

**Role:** CORE ENGINE (Layer 2). Adjusted score 7.0. **Note: no adversarial review of M6 was ever written;
an independent red-team is a Week-1 deliverable (Fri 18 Sep).**

**Purpose.** Turn already-printed GBV into recognised revenue, so that the 4Q26 guide carries no GBV
forecast error and no take-rate forecast at all. This replaces `τ_{t−4} × (1 + w_q)` at
`13_driver_model.py:381-383`, whose perfect-foresight backtest error is **+0.53% mean, sd 1.97%,
trailing-four +1.05%** with 100% of the error in that one term.

**Equation.**

```
Revenue_q^USD = Σ_{k=0..3} Φ_{k | Q(q−k)} · fee(m_{q−k}) · GBV_{q−k}^USD  +  Λ_q
Φ_0 ≈ 0 (pre-registered test);  Φ_1 = 2/3, Φ_2 = 1/3 as the prior mean
λ_s ≡ Revenue_q / [⅔·GBV_{q−1} + ⅓·GBV_{q−2}]
    Q1 13.034 / 12.325 / 12.612  (mean 12.657, range 0.709)
    Q2 13.449 / 13.946 / 13.736  (mean 13.710, range 0.497)
    Q3 17.391 / 17.145 / 17.182  (mean 17.239, range 0.245)
    Q4 11.946 / 12.117 / 12.026  (mean 12.030, range 0.171)     [recomputed, 2023-2026]
fee(H, m): split → GBV = H/0.97 × 1.141, rev = H/0.97 × 0.171,  take 14.99%
           single → GBV = H/0.845,        rev = H/0.845 × 0.155, take 15.50%
           ⇒ +51bp of take, +4.05% of revenue on the migrated cohort at θ = 1;
             +3.4% of revenue given GBV at the measured θ = 0.833-0.845
TakeRate_q = Revenue_q / GBV_q   — an OUTPUT.  ADR_q = GBV_q/(N_q+S_q) — an OUTPUT.
```

**Inputs (paths).** `data/processed/overnight/02_kpi_panel_quarterly.csv` (24 quarters × 119 cols — the only
file the λ kernel needs); `data/processed/abnb_backlog_indicators.csv` (restated as `reported/(1−d_q)`,
`d_q` = 0.9 / 3.8 / 16.2 / 16.5% for 3Q25-2Q26); `data/processed/h2_bridge/h2_bridge_gbv_lag_conversion.csv`
(the same six ratios — a copy, **not** an independent estimator); `10_fx_daily.csv` (19,468 rows, FRED),
`10_fx_basket.csv`, `10_regional_fx_passthrough.csv` (EMEA 1.043 / LatAm 0.623 / APAC 0.86 / NA not
identified); `28_fx_hedge_disclosures.csv` (14 rows; `gross_fx_ex_hedge_pp`, `non_usd_revenue_share`
0.54→0.56), `28_fx_hedge_forward.csv` (−0.21/−0.21/−0.18/−0.18pp — **memo only**);
`06_fee_timeline.csv` (19 dated events); `data/processed/adr/12_reprice_summary.csv` (measured θ);
`data/processed/fee_split_elasticity_scenarios.csv`; `data/processed/booking_curve_daily.csv` (Dirichlet
shape prior only — `blocked_rate` is **not** occupancy); `Citadel-ABNB-fx-engine/analysis/src/fx_engine/*.R`.

**Estimator.** Constrained least squares first (four seasonal simplexes over k, ordering constraint
E[k|Q1] ≥ E[k|Q4], plus ρ and the two FX scales), with a block bootstrap. Stan is a **stretch goal gated at
end of Week 1**, not a deliverable. Interval likelihood on every letter-rounded FX integer:
`target += log_diff_exp(normal_lcdf(x+0.5), normal_lcdf(x−0.5))`. Priors that are disclosures, not
judgements: `s_R ~ N(0.56, 0.03)` from the disclosed non-USD revenue share; migrated-GBV share forced to ~1
by the 15 Sep / 13 Oct deadlines.

**Outputs.** `Φ` (the 4×4 transition matrix and hence "share of quarter q already on the ledger at date t");
quarterly revenue level 3Q26-4Q27 with intervals; the printed take rate as a derived series; the revenue-FX
contribution **as an output, not an input**; `Λ_q` in dollars.

**Owner / week.** P1 (kernel, Mon 14 Sep) + P3/R (FX and fee schedule, Tue-Thu 14-17 Sep). Red-team Fri 18 Sep.

**Interface contract.**
- **Consumes** exactly one object from Layer 1: `G_q` — GBV in USD, booking-dated, one number per quarter.
  Nights, ADR, mix and regulation must not cross the boundary. If Layer 1 hands over *reported* ADR instead
  of host payout in `usd_constant`, the fee reprice is already inside it and the double count returns.
- **Emits** to Layer 3: a revenue level posterior per quarter, plus the "already-booked share" scalar.
- **Guards:** the fee function is evaluated **once** and returns (GBV, revenue) jointly — the ADR workbook's
  `+0.50pp fee-migration reprice` row and `take_bps` are both deleted. The hedge is added **once**, in
  dollars, after pre-hedge revenue; it is already inside the letter-stated after-hedge FX, so anyone adding
  `28_fx_hedge_forward.csv` separately understates revenue by ~0.2pp a quarter. Consume the R engine's
  `adapter.csv` `revenue_fx_usd` **or** `revenue_timing_multiplier`, **never both**.
- **Rejected from the proposal:** all FX point estimates (3Q26 +1.04pp gross vs management's stated ~+3.2pp;
  4Q26 +0.41pp; 4Q26 $3,284M; FY27 ~$16.05bn). The architecture is adopted, the numbers are not.

**Pre-registered falsification.** (i) The restated backlog must beat naive on revenue growth on both windows
(Gate G1, 16 Sep) or Φ loses its hardest pin. (ii) λ's slope on the booking→check-in FX wedge must stay
\|t\| < 2 when 4Q26 is added (current: **+0.158, se 0.275, t = +0.57, r = 0.179, n = 12**). (iii) The
3Q26 printed take rate must clear 18.10% if the fee migration is flowing.

---

## Card 2 — M3 · The guidance policy function

**Role:** CORE ENGINE, terminal layer (Layer 3) and the pitch's clock. Critic average 4.83 → adjusted 6.0.

**Purpose.** Convert a revenue-level posterior into the **guide range management will print**, which is the
object the pitch is judged on: the 3-12 month window covers four guides and zero decisive prints. It also
supplies the surprise denominator on 5 Nov.

**Equation.**

```
guide_mid_q  = E[Revenue_q] / (1 + c),    c = trailing-8 A/g cushion
               c: mean +1.856%, median +1.79%, sd 1.006pp   [recomputed from 02_guidance_cushion_series.csv]
               last 8 values: 0.86, 2.69, 0.98, 2.52, 0.86, 3.27, 2.61, 1.06
range_width  = 1.7-2.2% of midpoint (trailing-8 mean 1.86%; 3Q26 was 1.68%)
S_q^at-print = guide_mid_q × (1 + κ),     κ = +0.52%, sd 28bp, LSEG-only pairs n ≈ 13
gap          = guide_mid_q / S_vendor − 1                     — derived, never parameterised
predictive sd = √(kernel PIT RMSE 2.44%² + cushion draw 1.006%²) ≈ 2.6pp
```

**Inputs (paths).** `data/processed/overnight/02_guidance_ledger.csv` (194 statements, 159 scoreable);
`02_guidance_cushion_series.csv` (19 scoreable revenue guides); `02_guidance_accuracy.csv`;
`04_consensus_at_print.csv` + `16_consensus_at_print_merged.csv` (23 prints);
`04_current_consensus.csv` (Zacks 4 Sep: 3Q26 $4,740M/7; 4Q26 $3,200M/10, range $3,050-3,700; FY26 $14,100M/8;
FY27 $15,730M/13. S&P 3 Sep: FY26 $14,160M/43; FY27 $15,760M. NTM PT $178.96/46);
`20_executable_returns.csv` (`open_*` only); `20_frozen_q3_2026.csv`.

**Estimator.** Trailing-8 empirical cushion with a **block bootstrap**. No PyMC, no hierarchical pool.
Bucket-word guides (nights, GBV) mapped through the ledger's own vocabulary with the measured ~4pp
conservatism (4Q25 guided "mid-single digit" nights → +9.82%; 1Q26 guided "high-single digit" → +9.15%;
bucket guides beaten 5/5 above the range).

**Outputs.** `guide_mid` and range for 4Q26 (5 Nov), 1Q27 and FY27 (Feb 2027), 2Q27 (May 2027); the bucket
word for nights, GBV, ADR and take rate; `P(gap < 0)` against a **named vendor and timestamp**; the FY26
guide-raise probability (base rate: the FY guide has only ever been raised and the raise lands at the Q3
print, 2/2).

**Owner / week.** P1 (cushion + κ, Tue 15 Sep), W (bucket mapping and the guide-vs-print exhibit, Week 2).

**Interface contract.**
- **Consumes** one object: the revenue level posterior from Card 1. Nothing else.
- **Emits** the guide distribution and `κ` to Layer 4. The forward-growth delta is handed to valuation
  **once**.
- **Guards:** the cushion is measured as **A/g** (print ÷ guide midpoint — directly observed, kernel-free),
  never as g/M (which absorbs λ̂ bias; C-M3 §1.2 shows the two co-move one-for-one). `gap` is derived from
  `guide_mid` and `S`, so surprise-vs-Street is never separately estimated.
- **Deleted from the proposal:** the revision regression (it is the identity (1+rev) ≡ (1+κ)(1+gap), max
  residual 4.6e-6 on 18 rows); the hierarchical 159-statement pool (155 returned, 94 carry a cushion,
  `fillna(0.0)` fabricates 61); the −2.33% cushion; PyMC; and "guide below Street → 20-day drift" as an edge
  (all 9 events sit in 2022Q3-2025Q1, a window where 10 of 11 prints were negative regardless of gap sign;
  Fisher p = 0.27). The drift rule survives only as a caveated base rate.

**Pre-registered falsification.** Gate G4 (Fri 25 Sep): the guide-midpoint forecast must beat the **free
pre-guide Street consensus** on sign, target ≥8/14 on W1. On level it currently loses (MAE 1.93% vs 1.61%,
bias −1.23% vs −0.01%) and the memo must say so.

---

## Card 3 — M1 · The constrained reconciliation engine (nights, ADR, mix)

**Role:** MECHANICAL BRIDGE, Layer 1 + Layer 0. Critic average 4.00 → adjusted 5.5. **Demoted from state
space to constrained least squares.**

**Purpose.** Produce `G_q` (GBV in USD, booking-dated) for FY27 and beyond, with geographic mix, seats
dilution and the blended take rate as **outputs of identities** rather than rows. This closes three measured
inconsistencies in the current tree worth ~$175M (geo mix), ~$88M (seats treatment) and ~$110M (band-midpoint
bias) on FY27.

**Equation.**

```
n_{r,q} = N_q · softmax(u_{r,q})                      ⇒  Σ_r n_r = N   EXACTLY
N_q     = Σ_r n_home,r + n_hotel + s_exp + s_svc      ⇒  seats dilution is an OUTPUT
ADR_blend,q = Σ_r w_{r,q} · ADR_{r,q}, w from the same nights build
                                                      ⇒  geographic mix is an OUTPUT
GBV_{r,q} = n_{r,q} · ADR^local_{r,q} · X^B_{r,q}
ln ADR^home,exFX = p_t (one global like-for-like price) + q_{r,t} (shrunk regional deviation)
                 + m_size + m_los     — all from ONE joint hedonic; party size IS the capacity index
Objective: minimise Σ (model − exact)² s.t. 72 filed revenue cells exact, 23 total-nights exact,
           hinge penalties on 28 bucket intervals, 68 ADR integers (±0.5pp), 24 annual nights cells (±0.5M)
```

**Inputs (paths).** `10_xbrl_revenue_geography.csv` (258 rows → the **72-cell exact panel**: 56 filed
three-month cells 1Q22-2Q26 + 16 Q4 back-outs; verified 4Q22 $1,902M / 4Q23 $2,218M / 4Q24 $2,480M / 4Q25
$2,778M to $1M); `10_regional_panel_quarterly.csv` (23 quarters × 79 cols, bands);
`10_regional_adr_fx.csv` (92 rows, reported / ex-FX / gap / basket); `data/processed/adr/*.csv` (46 files,
incl. `01_regional_annual.csv`, `05_size_mix_panel.csv` 29 markets, `07_full_decomposition.csv`);
`06_wtp_hedonic_coefs.csv` (extra bedroom +15.1%, capacity ε +0.49, 4.9+ rating +9.5%);
FY2025 10-K Geographic Mix table (2025: NA 158M nights / $40.3bn GBV / $5,196M revenue; EMEA 215M / $34.2bn /
$4,729M; LatAm 90M / $8.5bn / $1,160M; APAC 70M / $8.3bn / $1,156M);
`11_new_business_scenarios.csv`; `11_regulatory_overlay.csv` (to be replaced by a dated DiD).
**Not** `06_quote_line_items.csv` for the hedonic — it is 76 aggregate rows with no price, capacity, bedroom
or LOS column.

**Estimator.** `scipy.optimize` constrained penalised least squares, ~60 parameters. Softmax shares in log
levels with chain-linking so no reconciliation residual exists (`CALIB = −0.41pp` deleted; the +0.19pp
current-period-weighting index bias cannot arise). Interval likelihood, not midpoints. Regulation enters as
a dated DiD covariate **on the nights state**, never as a subtraction from a growth rate already fitted on
regulation-contaminated realised data (`reg_mult = 1.67` deleted).

**Outputs.** `G_q` per quarter, and as diagnostics: regional nights with posterior intervals; the geo-mix
term as an output (**measured −1.06pp in 2024, −1.48pp in 2025 — deepening**, against within-region ADR of
+2.71pp and +4.46pp; NA nights share 32.6 → 31.3 → 29.6%); the seats-dilution term; the FY25 take-rate
decomposition (**92-95% North American: NA 13.274 → 13.238 → 12.895%, blended −16.4bp**); and the
model-to-model reconciliation table.

**Owner / week.** P2 (L0 files Mon-Tue 14-15 Sep; hedonic Week 2), P1 (constrained LS Thu 17 Sep, Gate G2).

**Interface contract.**
- **Consumes** `X^B` from Card 1's FX block and the fee function's GBV leg.
- **Emits** to Card 1: `G_q` **only** — one number per quarter, plus the `w_r` weights internally. Writes
  the boundary rule into `model/assumptions.md` verbatim.
- **Guards:** one joint hedonic ⇒ size, LOS and party size cannot double count (a separate party-size driver
  is forbidden; annual β = −0.36 moves against capacity). `nb_incr` netting stays exactly as built at
  `13_driver_model.py:437` — adding the full WS11 incremental column creates a real double count.
- **Deleted from the proposal:** the Stan state space; `τ_{r,t}` as 120 RW states (use 16 quarter-specific
  `fee_{r,q}` levels prior-centred on the measured Q3 17.4/17.1/17.2% and Q4 12.0/12.1/12.0%); the separate
  `q` and `m_sub` states (exactly collinear); the "24-cell free OOS test" (4 clean cells exist); the
  `06_quote_line_items.csv` hedonic.

**Pre-registered falsification.** Gate G2 (Thu 17 Sep): the fit must place every clean annual regional nights
cell inside ±0.5M while reproducing all 72 filed revenue cells exactly. Failure means the disclosures are
mutually inconsistent — publish that.

---

## Card 4 — M2 · The booked-base tracker

**Role:** TRACKER, accounting core only. Critic average 5.00 → adjusted 5.0. **Alt-data measurement layer cut
for the prelim.**

**Purpose.** Two things: (i) supply the target definition the whole system uses — forecast a **level** and
difference only at the last step, because guide-mid-vs-Street has sd **2.485pp** against revenue-surprise's
**1.099pp**, i.e. 2.26× more recoverable signal at fixed R²; (ii) hold the restated backlog identity that
pins Φ's tail.

**Equation.**

```
Base_D  = the revenue already on the booking ledger at guide date D
        = Σ_k Φ_k · fee · Ĝ_{D−k}   — the same object as Card 1, evaluated at the guide date
UF_q    = UF_{q−1} + τ·p_q·G_q − Revenue_q − τ·Refunds_q ± FXtr     (restated series only)
FH_q    = FH_{q−1} + (1−τ)·π_q·G_q − Payouts_q − GuestRefunds_q      (memo only — see guards)
unearned_restated = reported / (1 − d_q),  d_q = 0.9 / 3.8 / 16.2 / 16.5% (3Q25-2Q26)
```

**Inputs (paths).** `data/processed/abnb_backlog_indicators.csv` (24 rows; unearned fees $2,831M and funds
held $12,224M at 30 Jun 2026); `08_backlog_tests.csv`; `06_fee_timeline.csv`; 10-Q balance sheets via EDGAR.

**Estimator.** Restate first, then re-run the `08_backlog_tests.csv` regressions on the restated series.
`p` and `π` are restricted to ≤3 parameters each, driven by dated RNPL/fee-migration shares plus a tight
random walk — **not** free per quarter — and the (A4)/(A5) residuals must be shown to be non-zero before
either equation is claimed as over-identifying.

**Outputs.** `Base_D` with an interval at each historical guide date; the restated backlog series; the
`p` vs `π` diagnostic (fee-denominated unearned fees −0.9% y/y against amount-denominated funds held
+10.5%, on GBV +15.7%) as a sharp dated question for the 3Q26 10-Q.

**Owner / week.** P2, Wed 16 Sep (Gate G1).

**Interface contract.**
- **Emits** the restated backlog series to Card 1 as one of Φ's four pins.
- **Guards:** the reported unearned-fee series is **never** used — running on it is why the repo's own
  survivor fails on revenue (WF 1.17× naive, 1.28× AR(1)) while beating naive on **nights** (0.90×, AR(1)
  0.65×). The honest claim is *"the backlog predicts volume, not dollars, and only after restatement."*
  (A5) is either dropped or labelled as a restatement of (A3), since `Payouts_q` is imputed.
- **Deleted from the proposal:** the "10-K regional nights" anchor (Airbnb does not disclose it, and the
  quoted split is transposed); the review-index measurement layer (the 2025 store has zero reviews files);
  the claim that four accounting observables over-identify (it is two observables and two plugs).

**Pre-registered falsification.** Gate G1 (Wed 16 Sep): restated unearned fees must beat naive on revenue
growth on **both** windows. If not, say so and fall back to the column-sum restriction plus the booking-curve
prior — and state that Φ is weaker for it.

---

## Card 5 — M5 · The challenger and calibration rail

**Role:** CHALLENGER. No adversarial review was written; adjusted 4.0 after my own pass. **Scope cut to
calibration and same-day extraction.**

**Purpose.** Answer the one question no workstream in the repo has answered: *is the interval honest at
n ≈ 20?* Point accuracy is not the deliverable — nothing beats AR(1) for nights and we accept that as binding.

**Equation.**

```
Challengers: AR(1); trailing-4 mean; guide + trailing-8 cushion; pre-guide Street consensus;
             monotone-constrained LightGBM with ≤4 features and SIGN PRIORS from the two validated
             survivors (nights non-decreasing in funds-held growth; ADR-FX non-increasing in broad USD)
Calibration: split conformal on the last 6-8 walk-forward residuals →
             a single scalar κ_conf such that [q10 − κ_conf, q90 + κ_conf] achieves 80% empirical coverage
Scoring:     RMSE ratio to naive, CRPS, PIT histogram, coverage
```

**Inputs (paths).** `02_kpi_panel_quarterly.csv`; `20_prediction_ledger.csv` (391 rows — the existing
harness, and a malformed new row is visually obvious next to correctly-formed ones);
`08_test_scoreboard.csv`; `05_macro_sensitivities.csv` (`usd_broad → adr_fx_effect`, r −0.95, perm p 0.001 —
the monotone GBM's sign prior); `04_consensus_at_print.csv`.

**Estimator.** Nested expanding-window CV (outer: origin walks 1Q24→2Q26 after a 12-quarter burn-in; inner:
hyperparameters strictly before the outer test origin). Zero-shot Chronos/TimesFM is optional and is
reported **only** for interval coverage, with the expected outcome — that it matches AR(1) on point
accuracy — stated before it is run.

**Outputs.** The conformal inflation factor applied to Card 2's guide distribution; a PIT histogram over the
14 guide dates; the challenger scoreboard; and, separately, a same-day structured extraction of the fee,
hedge, incentive and migrated-share sentences from the 3Q26 10-Q and call within hours of the 5 Nov print.

**Owner / week.** P4, Week 2 (Mon-Wed 21-23 Sep).

**Interface contract.**
- **Consumes** predictive distributions from Cards 1-3 and the baselines.
- **Emits** a calibrated interval, and the explicit statement of which lens earned its weight.
- **Guards:** NNLS is used **only** on well-specified predictive distributions from structurally different
  models, never on point features — the three composite indexes that lost to AR(1) combined point features
  that individually lost to AR(1). Every correlation is reported with its permutation p-value and nothing
  below the team's own Bonferroni-clean bar is built on.
- **Deleted from the proposal:** the hierarchical item-level LLM cushion model (C-M3 §1.3 killed the
  identical construction: 94 usable rows, incommensurable units, 61 fabricated zeros, and per-family
  standardisation makes the hyper-mean unconvertible to a % revenue cushion); the cross-border and LOS text
  proxies (single calibration anchor at 1Q24, no scoreable window); the 67.5M-review store dependency (it
  lives on an external volume and is not queryable from this checkout).

**Pre-registered falsification.** The conformal band must achieve 70-90% empirical coverage on held-out
quarters. If it does not, report the posterior and state plainly that it is uncalibrated at n ≈ 12.

---

## Card 6 — M4 · Three artefacts and one irreversible data capture

**Role:** DISCARD as a lens. Critic average 3.67 → adjusted 3.0. Three deliverables survive.

**Purpose.** (a) Preserve optionality on a second Inside Airbnb vintage; (b) own the one exhibit the Street
cannot construct; (c) supply the bedroom-elasticity correction to Card 3's ADR build.

**Deliverable A — the capture. Start today.** Adapt `inside_airbnb_supply_panel.py discover` to the 120-market
list; HEAD-poll `data.insideairbnb.com` daily; download on first sight. **Critically: fetch `reviews.csv.gz`
and `calendar.csv.gz`, not only `listings.csv.gz`** — `inside_airbnb_supply_panel.py:51` downloads listings
only, which is exactly why M4's vintage stack does not exist and why 28 of 73 historical CDN probes are dead.
Owner P2. Cost: storage. A missed dump is unrecoverable.

**Deliverable B — the fee-migration dual-basis exhibit.** The 2026 Inside Airbnb schema carries both price
bases in one file: `price` (col 47, the listed nightly price) and `price_quote_price_per_night` (col 51, the
all-in quote). At payout-neutral repricing the migrating cohort's **listed** price rises ~14.8% (measured
pass-through θ = 0.833-0.845 on matched Austin panels, `data/processed/adr/12_reprice_summary.csv`) while the
all-in guest price — and therefore GBV and ADR — moves ~+0.7%. Deadlines **15 Sep 2026 (ex-EEA)** and
**13 Oct 2026 (EEA + CH)** fall inside 3Q26 and 4Q26. Capture matched panels on 14/16 Sep and 12/14 Oct.
**Conclusion for the memo: listed-price readers will print a spurious 4Q26 ADR acceleration.** Dated,
mechanical, falsifiable, unowned by the Street, and independent of every other block. Owner P2, Weeks 1 and 4.

**Deliverable C — the bedroom-elasticity correction.** The Street maps the 2Q26 "Bedroom Nights Booked +12%
vs nights +10%" wedge ~1:1 into ADR. The measured bedroom-count elasticity is **0.23** (0.2289 on 12 markets,
0.2312 on 29), so the wedge is worth **+0.46pp of ADR, not +2pp**. Hand to Card 3. Owner P2, Week 2.

**Interface contract.**
- **Emits** θ and the tax/cleaning share of GBV to Card 1's fee function; the bedroom elasticity to Card 3.
- **Guards:** no Inside Airbnb **time series** enters any forecast. The panel is used cross-sectionally and
  within-vintage only. The 13-city panel's correlation with the four disclosed regional nights growths is
  **NA 0.14 / EMEA −0.07 / LatAm −0.36 / APAC 0.22** (first differences LatAm −0.71); Gate G3 (Thu 17 Sep)
  requires a ≥25% cut in mean 80% posterior width versus bands-plus-total alone, and is expected to fail —
  **publish the negative result as an exhibit.**
- **Deleted from the proposal:** the f(age) survivorship spline; the 120-market nights measurement; the
  gravity PPML; the DiD on `ln R*` as a causal estimand (delisting erases treated listings' pre-treatment
  reviews from the 2026 vintage, inverting the estimand); `P(nights bucket)` as a deliverable (3 precedents,
  2 of which printed above the range — hand the mapping to Card 2).

---

## Card 0 — Layer 0: the constraint spine (built once, owned by everyone)

**Purpose.** Every constraint the system uses lives in three files and nowhere else.

| File | Contents | Built |
|---|---|---|
| `L0_exact_regional_revenue.csv` | **72 cells.** 56 filed three-month regional revenue cells 1Q22-2Q26 from `10_xbrl_revenue_geography.csv` (80-100 day periods), plus 16 Q4 back-outs. Assertion: 4Q22 $1,902M / 4Q23 $2,218M / 4Q24 $2,480M / 4Q25 $2,778M reproduce to $1M. Carries `basis = filed`. **Unused anywhere in the repo today.** | Mon 14 Sep, P2 |
| `L0_interval_observations.csv` | One row per observation: 28 genuine bucket cells (4Q24-2Q26), 68 ADR integers (±0.5pp), 24 annual 10-K nights cells (±0.5M at the table's own precision), 19 guide ranges, 5 bucket words. Header carries the **hard rule**: the 14 `basis == 'derived'` rows (NA 8, EMEA 6, spanning 4Q22-3Q24) are **excluded**, and the 22 `basis == 'numeric'` LatAm/APAC cells are treated as rounding intervals, not equalities. `phrase_kind` distinguishes a coded qualitative phrase from a stated number. | Tue 15 Sep, P2 |
| `L0_vintage_register.csv` | Every consensus value with `vendor, period, metric, value, n_estimates, as_of_timestamp, url`. The 6 Aug 2026 guide-vs-Street feature is **LSEG $4,610M**, not Zacks $4,740M (4 Sep). Zacks publishes nights, ADR and GBV consensus 2-3 days before each print — diarise 2-3 Nov. | today, P4 |

**Guard.** No model reads a disclosure except through these three files. That is what makes the PIT harness
enforceable and what stops the FX-contaminated `derived` rows re-entering through a side door.

---

*Research, not investment advice.*
