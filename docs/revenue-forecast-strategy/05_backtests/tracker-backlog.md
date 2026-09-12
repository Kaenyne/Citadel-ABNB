# tracker-backlog — backtest note

Package: `analysis/src/forecast_methods/tracker_backlog/`. Data outputs:
`data/processed/forecast_methods/tracker_backlog/`. Registry:
`data/processed/forecast_methods/registry/tracker-backlog__revenue_yoy_next_q.csv`,
`tracker-backlog__nights_yoy_next_q.csv`.

## Run command

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/tracker_backlog/run.py
```

**Exit code: 0.** All four steps ((a) rebuild, T1 circularity, (c) Gate G1, (d) booking
curve prior) completed. (e) is a written specification only, not code, per the
standing instruction "do not run the capture" — see §(e) below.

---

## T1 — the circularity test (run first, decides whether the rest of the package exists)

**Claim tested:** the architect's `unearned_fees_restated = reported / (1 − d_q)`, with
`d_q` the dated distortion series in `03_insider_mechanics.md` §1.5 (0.9% / 3.8% /
16.2% / 16.5% for 3Q25–2Q26), is — per the M6 critic — identically
`coverage_norm(season) × next_quarter_revenue`, because that is exactly how `d_q` was
derived (`d_q = gap / reported`, `gap = coverage_norm × next_quarter_revenue − reported`).

**Result — CONFIRMED, algebraically and numerically, to <0.001% on all 4 rows:**

| quarter-end | reported unearned ($M) | coverage norm | next-Q revenue used | basis | implied pro-forma ($M) | gap ($M) | d_q computed | d_q quoted | match |
|---|---|---|---|---|---|---|---|---|---|
| 3Q25 | 1,820.0 | 0.661 | 2,778.0 | actual (4Q25) | 1,836.26 | 16.26 | 0.893% | 0.9% | ✓ |
| 4Q25 | 1,743.0 | 0.676 | 2,678.0 | actual (1Q26) | 1,810.33 | 67.33 | 3.863% | 3.8% | ✓ |
| 1Q26 | 2,733.0 | 0.880 | 3,608.0 | actual (2Q26) | 3,175.04 | 442.04 | 16.174% | 16.2% | ✓ |
| 2Q26 | 2,831.0 | 0.697 | **4,730.0** | **GUIDE MIDPOINT (3Q26), not printed** | 3,296.81 | 465.81 | 16.454% | 16.5% | ✓ |

`n = 4`. `restated_multiply_form` reproduces `implied_pro_forma` to numerical rounding
on **4/4** rows (`multiply_vs_implied_pct_diff` max = 0.000%). The 3175 = 0.880 × 3608
and 3297 = 0.697 × 4730 checks named in the standing instruction both reproduce exactly.

**Formula-vs-number check** (`reported/(1−d_q)` as stated in the doc text vs.
`reported×(1+d_q)` as every quoted y/y number is actually computed), `n = 2`:

| quarter | reported | d_q | y/y multiply form | y/y divide form | quoted in doc | multiply matches | divide matches |
|---|---|---|---|---|---|---|---|
| 1Q26 | 2,733.0 | 16.174% | **+16.60%** | +19.73% | +16.6% | ✓ | ✗ |
| 2Q26 | 2,831.0 | 16.454% | **+15.39%** | +18.61% | +15.4% | ✓ | ✗ |

**Ruling (per the chief of staff's fiat, reproduced independently here): the multiply
form is what the document's own quoted numbers actually use; the divide form stated in
its prose does not reproduce them.** `basis=derived` everywhere this series appears.

**Verdict: CIRCULAR.** `restated_unearned_q ≡ coverage_norm_season(q) × revenue_{q+1}`.
The 2Q26 value is a function of the **3Q26 guide midpoint**, not a print — doubly
circular for any 3Q26 forecast. **The restated series is STRUCK as a pin, as a
feature, and from every window and likelihood in this and every other package.** It is
retained in `01_backlog_rebuild.csv` only as a labelled, non-consumed descriptive
column (`restatement_basis = "derived ... do not use as a forecast feature"`), never
as a registry object, never as a regression input.

Files: `02_circularity_test.csv`, `02b_formula_vs_number_check.csv`,
`02c_circularity_verdict.csv`.

---

## (a) Backlog rebuild since 4Q20

`01_backlog_rebuild.csv`, **n = 23 quarters** (4Q20–2Q26), from
`abnb_backlog_indicators.csv`. Columns: unearned fees, funds held, GBV, revenue,
nights, their y/y growth, the coverage ratio (recomputed and cross-checked against the
source file's own column — matches on **22/23** rows; the one non-match is the
expected 2Q26 row, whose next-quarter revenue is not yet printed, not a real
discrepancy), and the derived/circular restated series (labelled, unused).

**The identity, and what of it is actually testable:**

```
Nights_q       = GrossNights_q − Σ_{b≤q} CancelledNights(b,q) ± Alterations_q   [not disclosed]
GBV_q          = G_q − Σ_{b≤q} c(b,q)·G_b ± Alterations_q                       [not disclosed]
UnearnedFees_q = UnearnedFees_{q-1} + τ·p(q)·G_q − Revenue_q − RefundedFees_q
                 ± FX translation                                               [p(q), RefundedFees_q not disclosed]
FundsHeld_q    = FundsHeld_{q-1} + GuestCashReceived_q − HostPayouts_q − GuestRefunds_q  [components not disclosed]
```

Airbnb discloses none of gross bookings, cancellations, the prepaid share `p(q)`, or
host-payout timing numerically, at any frequency (confirmed by grep across the KPI
panel, the MD&A text folded into `03_insider_mechanics.md`, and the guidance ledger).
**Per the addendum's instruction, the prepaid share and payout-timing components are
NOT fitted in this package.** A structural model of `p(q)` and payout timing, capped at
≤3 parameters each (dated product/fee-migration shares + a tight random walk, never
free per quarter), is feasible in principle but out of tonight's scope — no payouts
equation is built here, so there is nothing to relabel or drop; only the directly
observable LEVELS (unearned fees, funds held, GBV, revenue, nights) are used, via
reduced-form regression, in Gate G1 below.

**Dated diagnostic for the 5 Nov filing** (addendum instruction, reproduced from the
2Q26 row exactly): fee-denominated unearned fees **−0.9% y/y** against funds held
**+10.5% y/y**, on GBV **+15.7% y/y**. The ~5–6x gap between the unearned-fee shortfall
and the funds-held shortfall against GBV growth is the mechanism named in
`03_insider_mechanics.md` §1.5: funds held is booking-amount-denominated (~87% of GBV,
only RNPL defers it) while unearned fees are fee-denominated (~13–15% of GBV) and are
hit by RNPL *and*, unidentified, by the single-fee migration moving fee collection from
guest-at-booking to host-payout-after-check-in. **This is the open question for the
3Q26 10-Q, not a modelling input.**

---

## (c) Gate G1, redefined — does the RAW series beat naive/AR(1)?

**Predictor:** OLS of `y_q` (target metric's y/y growth) on `x_{q-1}` (backlog item's
y/y growth at the *last printed* quarter — what a forecaster standing at the guide date
for `q` actually has, per the harness's `include_same_day=True` convention), refit
expanding-window at every guide date using only realised `(x,y)` pairs known at that
date. `n_params = 2` (intercept + slope) per row. Two features (`unearned_fees_yoy_pct`,
`funds_held_yoy_pct`), two targets (`revenue_yoy`, `nights_yoy`), both replays
(`PIT`: refit at each date; `full_sample`: parameters fixed to the final full-history
fit, inputs still point-in-time), both windows. **Independent validation, scoped to the
`unearned_fees` feature only** (this check was NOT run against the `funds_held`
feature — see the priority-1 reconciliation in "Fixes after verification" below for why
that distinction matters): the raw, uncorrected walk-forward for both
`unearned_fees_yoy_lag1` targets exactly reproduces the pre-existing
`data/processed/overnight/08_backlog_tests.csv` walk-forward (built by an earlier
pass) to 4 decimal places on RMSE and naive-ratio — same methodology, same numbers,
independently re-derived tonight. The `funds_held` feature was never put through this
same reproduction check; §(c)'s table below reports `gate_g1.py`'s own numbers for it,
which diverge materially from a legacy `funds`-feature number quoted elsewhere in the
repo (see "Fixes after verification").

**RMSE ratios, RAW series only, PIT replay** (`03c_gate_g1_ratios_by_spec.csv`):

| target | window | n | RMSE | ratio vs naive | ratio vs AR(1) | beats naive | beats AR(1) |
|---|---|---|---|---|---|---|---|
| revenue_yoy (unearned) | W1 | 14 | 4.479 | **1.171** | 1.029 | ✗ | ✗ |
| revenue_yoy (unearned) | W2 | 10 | 5.008 | **1.167** | 1.129 | ✗ | ✗ |
| revenue_yoy (funds) | W1 | 14 | 6.467 | 1.691 | 1.486 | ✗ | ✗ |
| revenue_yoy (funds) | W2 | 10 | 4.225 | 0.985 | 0.953 | ✓ (only, narrow — see reconciliation below) | ✓ (only) |
| nights_yoy (unearned) | W1 | 14 | 2.602 | **0.904** | 0.390 | ✓ | ✓ |
| nights_yoy (unearned) | W2 | 10 | 2.555 | **1.183** | 0.705 | ✗ | ✓ |
| nights_yoy (funds) | W1 | 14 | 5.269 | 1.832 | 0.790 | ✗ | ✓ |
| nights_yoy (funds) | W2 | 10 | 4.080 | 1.890 | 1.126 | ✗ | ✗ |

**Gate G1 verdict, as redefined (pass requires beating BOTH naive AND AR(1) on BOTH
windows): FAILS for revenue (both features, both windows) — confirms the pre-registered
expectation (1.17x naive / 1.03–1.49x AR(1)) almost exactly.** For nights, the
`unearned` feature beats AR(1) comfortably on both windows (0.390, 0.705) and beats
naive on W1 only (0.904); it does **not** clear naive on W2 (1.183). **The honest claim
survives only partially: the raw backlog predicts volume better than dollars, but does
not cleanly clear "beats naive on both windows" even for nights — only the AR(1) bar
is cleared on both windows.** (Note: the harness's own canonical `baseline_ar1` gives a
materially *weaker* AR(1) fit for `nights_yoy` — RMSE 6.67 vs. the legacy
`08_backlog_tests.csv`'s 3.97 — because the harness AR(1) is fit on the raw growth
series and over-extrapolates on the sharp 2022–2023 reopening deceleration; this makes
"beats AR(1)" an easier bar here than in the earlier exploratory pass, and is flagged,
not fixed, tonight.)

**RNPL correction (scenario, not fit):** `unearned_share × k`, `k ∈ {0.5, 1.0, 1.5}`,
added in points to the raw feature for RNPL-era quarters only. RNPL GBV share: only the
**floor** is management-disclosed (same-day letter, admissible under the PIT rule) —
"~20%" for 1Q26 and ">20%" for 2Q26 per `03_insider_mechanics.md`; the specific point
values used here, `{1Q26: 20%, 2Q26: 22%}`, are the **researcher's own point picks
within that disclosed floor**, not themselves disclosures (verification round 1 flagged
this — the 1Q26 figure happens to equal its floor, the 2Q26 figure does not).
`{3Q25: 5%, 4Q25: 12%}` is a **researcher scenario ramp with no disclosure of any kind
behind it** — flagged explicitly, since it feeds 2 of the 14 W1 dates and 2 of the 10 W2
dates. None of this affects PIT-safety (every value used is admissible as of its own
guide date either way); it affects only how confidently the point value can be cited.

| target (unearned feature) | window | k=0.5 ratio(naive/AR1) | k=1.0 ratio(naive/AR1) | k=1.5 ratio(naive/AR1) |
|---|---|---|---|---|
| revenue_yoy | W1 | 0.853 / 0.750 | **0.680 / 0.598** | 0.778 / 0.684 |
| revenue_yoy | W2 | 0.804 / 0.777 | **0.593 / 0.573** | 0.714 / 0.690 |
| nights_yoy | W1 | **0.750 / 0.323** | 0.797 / 0.344 | 1.025 / 0.442 |
| nights_yoy | W2 | **0.875 / 0.521** | 0.973 / 0.580 | 1.407 / 0.839 |

**Finding, heavily caveated: at k=0.5–1.0, the RNPL-corrected `unearned` feature clears
naive AND AR(1) on BOTH windows for BOTH targets simultaneously** (k=1.5 breaks nights
on naive). This is a genuinely interesting result — not the product of fitting k to
minimise error (k was fixed a priori at 3 round values before scoring) — but it rests
on two things that must be stated before it is used for anything: (1) 2 of 14/10 dates
per window use a **researcher-assumed** RNPL share, not a disclosure, and (2) choosing
"the best of 3 pre-registered k values after seeing both windows' scores" is itself a
mild multiple-comparison exposure — a true out-of-sample test would pre-commit to one k
before any scoring. **Treat as a promising, NOT gate-clearing, secondary finding pending
2H25 RNPL-share corroboration**, not as a cleared Gate G1. The `funds` feature gets
*worse* under the same correction at every k (e.g. revenue W1 ratio 1.69 → 2.18 → 2.69
naive-ratio as k rises 0→1.5) — consistent with `03_insider_mechanics.md`'s own finding
that funds held is distorted "by roughly a third as much" as unearned fees; a future
pass should test a funds-specific `k≈0.33`, not built tonight.

**Registered objects** (harness format, both replays, both windows, all spec_id
variants in one file each): `tracker-backlog__revenue_yoy_next_q.csv` (384 rows),
`tracker-backlog__nights_yoy_next_q.csv` (384 rows). `n_params = 2` per row
(OLS intercept + slope); the RNPL-scenario `k` is an externally fixed input, not a
fitted parameter, and is carried in `spec_id`/`notes`, not counted.

---

## (d) Booking-curve prior for kernel-lambda

`04_booking_curve_dirichlet_prior.csv`, from `booking_curves_by_market.csv` (**600 data
rows** — 601 lines including the header, corrected in this fixes round; 120 markets x 5
horizon bands, single Jul–Aug 2026 snapshot). **This is a proxy, not a measurement**, and
the mapping to Phi is directionally inverted from what Phi actually is (see full
caveat in the script docstring and `04c_booking_curve_prior_caveat.txt`):
`blocked_rate` is a forward-looking calendar-availability read (of dates that have not
happened yet, conflating real bookings with host-blocked dates), while the Phi kernel
weight is a backward-looking share of *already-arrived* stays by how far in advance
they were booked. A single cross-sectional snapshot cannot identify the latter from the
former; at most it bounds the plausibility of "meaningful mass books >1 quarter out."

Pseudo-Dirichlet shares (alpha = summed blocked listing-nights per bucket, `n` = 600
market×horizon rows):

| bucket | days | blocked nights | listing nights | pooled blocked rate | Dirichlet mean share |
|---|---|---|---|---|---|
| 0–1Q ahead | 0–90 | 65,347,332 | 142,961,146 | 0.457 | **0.251** |
| 1–2Q ahead | 91–180 | 54,064,487 | 145,016,100 | 0.373 | **0.208** |
| 2–4Q ahead (capped) | 181–372 | 140,884,979 | 299,795,884 | 0.470 | **0.541** |

**These weights must NOT be read as an estimate of Phi's (2/3, 1/3, 0).** They answer a
different question (how far out is currently-blocked calendar inventory) on a different
axis (forward availability, not backward booking lag) with a confound (host blocks) the
data cannot separate. Offered to kernel-lambda strictly as: "more than a token share of
inventory is blocked 6–12 months out, so a kernel with material 2Q+ mass is not
implausible on its face" — nothing quantitative should be read off the shares. Region
breakdown in `04b_booking_curve_prior_by_region.csv` (**267 data rows across 89
unique regions x 3 buckets**, corrected in this fixes round — an earlier draft of
this note said "120 rows" and separately, inconsistently, "~90 finer region rows"
in the same sentence) shows the shape is broadly stable across region codes (0–1Q
share range 0.169–0.365 across the 89 regions), for what that is worth given the
caveats above.

---

## (e) Inside Airbnb monthly capture — specification only, NOT run

Per the standing instruction, this is a specification, not code, and nothing here was
executed. It adapts `analysis/src/inside_airbnb_supply_panel.py` (currently 13 cities,
listings-only + a calendar/booking-curve side-pull; see `inside_airbnb_pair_eligibility`
audit note for the point-in-time coverage-classification machinery already built for it)
up to the full 120-market panel used by `booking_curves_by_market.csv`.

**What must start now, monthly, going forward (not retroactively — Inside Airbnb keeps
~12 months of CDN history per city, so a gap today is a permanent gap for that month):**

1. **Scope: 120 markets** (the same list as `booking_curves_by_market.csv`/
   `10_regional_panel_quarterly.csv`), not the current script's 13. Each market needs,
   per monthly snapshot: **listings.csv.gz** (host/room/price/availability fields, the
   existing `COLS` list in `inside_airbnb_supply_panel.py`), **calendar.csv.gz**
   (daily availability + price for the next 365 days — this is what
   `booking_curves_by_market.csv`/`booking_curve_daily.csv` were built from, one-off,
   for this package's step (d); it must become a recurring monthly pull to ever
   support a y/y or q/q booking-curve comparison, which the single Jul–Aug 2026
   vintage cannot), and **reviews.csv.gz** (review-level dates, for the
   `reviews_ltm`/`est_nights_ltm` occupancy proxy already defined in the script's
   docstring). Today's spec covers listings + calendar only; **reviews is new scope**
   for this monthly cadence and must be added to the download step.
2. **HEAD-poll approach** (per the addendum): Inside Airbnb does not publish a
   machine-readable index of available dump dates. The existing `discover` subcommand
   in `inside_airbnb_supply_panel.py` already does the right thing for its 13 cities —
   HEAD-request the CDN URL pattern
   `https://data.insideairbnb.com/{country/region/city}/data/{date}/data/{listings|
   calendar|reviews}.csv.gz` for a set of candidate dump dates (Inside Airbnb refreshes
   most cities roughly quarterly, a few monthly) and record which return 200 —
   **extend it to**: (i) probe on the **first business day of every month** going
   forward (a cron/scheduled task, not built tonight — a harness/ops concern outside
   this package), (ii) probe all three file types (`listings`, `calendar`, `reviews`)
   per city per candidate date independently, since they are not always refreshed
   together, (iii) widen `KNOWN_DATES`'s per-city URL-path table from 13 to the full
   120-market list (region/path strings for the other 107 need to be sourced from
   Inside Airbnb's `get-the-data` page structure, e.g.
   `country/region/market`, mirroring the 13 existing entries), (iv) write the
   discovered manifest with a `content_type` column (`listings`/`calendar`/`reviews`)
   alongside the existing `city`/`date`/`url` columns, and (v) record `probed_at`
   (today's date) as a vintage stamp on the manifest itself, so a later PIT replay can
   tell what was knowable when.
3. **Download and cache** exactly as `download` already does (gzip → parquet cache,
   `COLS` allow-list for listings), extended with a `reviews` parquet cache holding at
   minimum `listing_id`, `id`, `date` (the fields `est_nights_ltm` needs).
3. **Storage cost, sized from the existing 13-city, listings-only run**: 13 cities ≈
   several hundred MB of listings parquet. 120 markets × 3 file types (listings +
   calendar + reviews, where calendar and reviews are typically 5–20x the row count of
   listings) is a multi-GB-per-month acquisition — budget accordingly and gzip/parquet
   everything; do not keep raw `.csv.gz` beyond the acquisition step.
4. **`pair_eligible_pit` discipline carries over unchanged**: every new monthly
   snapshot must be classified with the same point-in-time-safe
   `partial_scope_pit`/`pair_eligible_pit` flags the script already computes (audit
   finding A04), so a later replay never uses a scope classification that depends on
   scrapes that had not happened yet.
5. **First deliverable once 2–3 monthly vintages exist**: a true y/y-comparable
   `blocked_rate`-by-horizon series (fixing the single-vintage limitation flagged
   throughout §(d) above), and a `reviews_ltm`-based occupancy proxy at the market
   grain — per `01_ground-truth/02_model_audit.md` recommendation #8, tested at
   market×month grain (n in the thousands), never re-aggregated to a 20-quarter
   national series.

**Not started tonight**: no download, no discover run, no new `KNOWN_DATES` entries,
no reviews cache. This section is the plan only.

---

## Parameter counts (this package)

| object | fitted params | external (non-fitted) inputs |
|---|---|---|
| circularity test | 0 (arithmetic identity) | 0 |
| backlog rebuild | 0 | 0 |
| Gate G1 OLS (per date, per spec) | 2 (intercept, slope) | RNPL scenario `k` (swept, not fit): 0 for raw, 1 constant for scenario variants |
| booking-curve Dirichlet prior | 0 | 0 (pure aggregation of raw counts) |

---

## Known issues / honest interpretation

1. **Gate G1 fails for revenue on the raw series, as pre-registered.** The RNPL-scenario
   correction flips it to a pass across a plausible k-range on both windows, but 2 of
   the RNPL-share inputs behind that correction are researcher assumptions, not
   disclosures — this is a lead for the 5 Nov call and the 3Q26 10-Q, not a validated
   signal.
2. **Nights only partially clears Gate G1** (AR(1) on both windows; naive on W1 only,
   raw). The RNPL-corrected version at k=0.5 clears all four cells.
3. **The harness's own canonical AR(1) baseline is materially weaker for `nights_yoy`
   than an earlier exploratory AR(1) in `08_backlog_tests.csv`** (RMSE 6.67 vs 3.97).
   Both are legitimate implementations of "AR(1) on y/y growth," refit differently
   (the harness fits directly on the raw growth series each expanding window and
   over-extrapolates through the 2022–2023 reopening deceleration). Not investigated
   further tonight; flagged for reconciliation.
4. **Two harness gaps found and worked around, not fixed** (detail in README.md):
   `score.py`'s scoreboard pools multiple `spec_id` variants registered under one
   object into a single blended row (no `spec_id` in `GROUP_KEYS`); `baselines.py`'s
   `BASELINE_SPECS` does not cover `nights_yoy`, so this package calls
   `baseline_naive`/`baseline_ar1` directly rather than reading the registry.
5. **The balance-sheet identity's cancellation, prepaid-share and payout-timing terms
   are not disclosed and not fitted**, per the addendum's instruction — no payouts
   equation exists in this package to drop or relabel.
6. **The booking-curve "prior" is explicitly not a Phi estimate** — it measures a
   different, inverted axis (forward calendar availability vs. backward booking lag)
   on a single vintage, and is handed to kernel-lambda as a plausibility check only.
7. **Coverage figures used throughout match the binding-decision numbers exactly**:
   Q1-end 0.880, Q2-end 0.697, Q3-end 0.661, Q4-end 0.676 (2023–25 full-sample means);
   the 85–90% "determined" claim and the 82% figure are both struck, per the chief of
   staff's ruling — not reproduced or used as inputs anywhere in this package.

---

## Fixes after verification (round 1)

An independent verifier scored this package **PARTIAL** (safe to score, with caveats).
Five issues were raised, in priority order; all five are addressed below. Re-run
confirmed: `run.py` exit code 0, 768 registry rows across the 2 objects (unchanged
count and unchanged values for every pre-existing row — the fixes below are additive
disclosure plus one new diagnostic output, not a change to any previously-registered
number).

### Priority 1 — `funds_raw` / `revenue_yoy` / W2 reconciled against `02_model_audit.md` line 438

**The gap.** `02_model_audit.md` line 438 quotes a "survivor": `bl_funds_yoy_lag1 ->
rev_yoy, ratio 0.600`, sourced from `data/processed/overnight/08_backlog_tests.csv`.
This package's own `funds_raw` / `revenue_yoy` / W2 / PIT row — the identical feature,
target and window — scores `ratio_vs_naive = 0.985` (a narrow pass, not a survivor).
The verifier correctly flagged that this package's note never surfaced or explained
that gap before using the funds feature (and its RNPL-scenario variants) as evidence.

**Diagnosis, not just disclosure.** A new function, `gate_g1.reconcile_funds_w2()`,
reproduces BOTH training conventions side by side and writes
`03d_funds_w2_legacy_reconciliation.csv`. Root cause, confirmed numerically by this
run: `08_backlog_tests.csv`'s own `window` column shows its W2 walk-forward for this
feature **trains only on `"2023Q1..2026Q2, WF from 2024Q1"`** — i.e. the legacy script
drops 2022 entirely from the OLS training sample for its W2 row. This package's
`walk_forward()` instead trains on full history from 2022Q1 for both W1 and W2,
differing only in which dates are *scored* — this is what the standing instruction
specifies ("expanding window ... W1 origin 1Q23 ... W2 origin 1Q24": the window origin
governs which dates are scored, not a second, shorter training cutoff).

Reproducing the legacy's own truncated-training convention exactly recovers its
number:

| convention | n scored | rmse | rmse_naive | ratio_vs_naive | ratio_vs_ar1 |
|---|---|---|---|---|---|
| this package (full history from 2022Q1) | 10 | 4.225 | 4.289 | **0.985** | 0.953 |
| legacy convention (training truncated to 2023Q1+) | 10 | 2.574 | 4.289 | **0.600** | 0.581 |
| legacy `08_backlog_tests.csv` quoted value (cross-check, read directly from the CSV) | — | — | — | 0.600143 | — |

The truncated-training reproduction (0.600200) matches the legacy quoted value
(0.600143) to 4 decimal places, closing the gap. `funds_held_yoy_pct` has a sharp 2022
reopening outlier (70.3% → 52.1% → 18.5% y/y in 4Q21–2Q22, from the KPI panel) that
swings the OLS fit for this feature far more than it swings `unearned_fees_yoy_pct`'s
comparable run — that is why dropping 2022 from training flips this one cell from a
narrow pass to what reads as a much stronger one, and why the effect is specific to
`funds` rather than also showing up for `unearned`.

**Ruling.** This package's own convention (full history from 2022Q1 for both windows)
is kept as the registered/headline number, because it is what the standing instruction
specifies. The legacy 0.600 is **not** a stronger, independently-corroborating result —
it is the same feature and window scored under a different, undisclosed training-sample
cutoff. **Anyone building on the `funds` feature, or its RNPL-scenario variants, should
treat the "funds gets worse under RNPL correction" finding as resting on the 0.985
convention, and should not cite the legacy 0.600 as a stronger prior without also citing
this reconciliation.** The `unearned` feature's reproduction against
`08_backlog_tests.csv` was already exact under either convention (both windows agree to
4 decimals — see §(c) above, now explicitly scoped to `unearned` only) and is
unaffected by this finding.

### Priority 2 — reproduction-check scope stated explicitly

§(c)'s "Independent validation" paragraph now states, up front, that the
`08_backlog_tests.csv` reproduction check was performed for the `unearned_fees`
feature only, and was never run against the `funds_held` feature — which is exactly
the feature the priority-1 gap above concerns. This was true in the original note's
underlying claim (it only ever cited `unearned_fees_yoy_lag1` targets) but the wording
made it easy to read as covering both features; it does not any more.

### Priority 3 — two row-count errors fixed

* `booking_curves_by_market.csv`: corrected from "601 rows" to **600 data rows**
  (601 was a `wc -l` header-inclusive miscount; 120 markets x 5 horizon bands = 600).
* `04b_booking_curve_prior_by_region.csv`: corrected from "120 rows" to **267 data
  rows across 89 unique regions x 3 buckets** (the original sentence was also
  internally inconsistent, separately saying "~90 finer region rows" a few words
  later — both numbers are now the verified 89/267). Neither correction changes any
  registered number or the Dirichlet shares themselves, which were already correct.

### Priority 4 — 2Q26 RNPL share rephrased

The 2Q26 RNPL GBV share used in the scenario correction (22%) was described as
"management-disclosed." Corrected: `03_insider_mechanics.md` discloses only a
**floor** of ">20%" for 2Q26; the specific point value 22% is this package's own
researcher pick within that floor, not itself a disclosure. `common.py`'s
`RNPL_GBV_SHARE_SCENARIO_PCT` comment and this note (§(c)) are both updated to say
so explicitly. This does not affect PIT-safety (both the floor and the point pick are
same-day-letter admissible as of their own guide dates) — it affects only how the
point value should be cited downstream.

### What could not be fixed, and why

Nothing here required re-running the package or invalidating any previously-registered
CSV — the verifier stated explicitly that the fix was disclosure, not re-computation,
and that is what was done, plus one additive diagnostic file
(`03d_funds_w2_legacy_reconciliation.csv`) that did not exist before. No acceptance
test result changed: Gate G1 still **fails for revenue on the raw series on both
windows**, and the `nights_yoy` raw feature still only **partially** clears Gate G1
(AR(1) both windows; naive W1 only) — these pre-registered-failure results are
unchanged and are not papered over by this fixes round. The known issue already listed
above (harness canonical AR(1) baseline vs. the legacy exploratory AR(1) for
`nights_yoy`, 6.67 vs 3.97) remains open and un-investigated, exactly as before — it is
a distinct reconciliation gap from the one fixed here and was correctly flagged, not
fixed, in the original pass.
