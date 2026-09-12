# 00 — Binding implementation decisions for the overnight build

Chief of staff, 11 Sep 2026, ~23:00 ET. Written after reading, in full:
`04_synthesis/00_INTEGRATED_SYSTEM.md`, `04_synthesis/01_METHOD_CARDS.md`,
`03_critiques/C_M6_fx_takerate_timing_mechanics.md`, `03_critiques/C_M5_ml_signal_extraction_and_challengers.md`,
`01_ground-truth/02_model_audit.md` §§4-5.

**Status of this document.** The architect's plan was written *before* the M6 and M5 critiques existed. Where
they conflict, this document rules, and the ruling is binding on every package tonight. Where I could not
resolve a conflict I say so in §11 and give a fiat so that nine implementers still make the same choice.
**§12 is a verification stamp:** before issuing this I re-ran, from the data, the λ acceptance table, the w₁
grid, the trailing-8 cushion, the W1/W2 guide-date lists and the 72-cell spine. All five reproduce; two of them
carry a trap that would have cost an implementer an hour, and those traps are now written into the addenda.

**Standing orders from Theo that override any card:** backtest point-in-time on an expanding window against
naive/AR(1), trailing-4, guide+cushion and the vintage-stamped Street; find the optimal mix of methods rather
than a single winner; the FX-hits-revenue-two-quarters-later hypothesis is to be **tested**, not assumed and
not assumed away; no Monte-Carlo-only and no SARIMAX-only work.

---

## 1. The one-paragraph reconciliation everything else hangs on

The architect and the M6 critic are **not** in conflict about FX; they are ruling on two different equations.

- The architect rules on the **revenue equation given GBV**: `Revenue_q = λ_s × [⅔·GBV_{q−1} + ⅓·GBV_{q−2}]`.
  Lagged GBV is already reported in USD at booking-date rates, so booking-date FX is *inside the base you
  multiply*. The only admissible extra FX term is the booking→check-in remeasurement inside `λ`, and that
  measures at slope **+0.158, se 0.275, t = +0.57, r = 0.179, n = 12**. Therefore the 4Q26 FX step-down is an
  **output** of the lagged-GBV arithmetic and must never be subtracted a second time.
- The critic rules on the **reduced-form stated-FX series**: the letter-stated gross revenue FX in pp. There,
  `0.56 × the 1Q26 basket (+5.60%) = +3.14pp` reproduces management's guided ~+3.2pp gross for 3Q26 to 0.06pp,
  while the contemporaneous basket (+0.32%) gives +0.18pp and cannot generate 2Q26's stated +4.61pp at all.
  Lag-1 r 0.861 > lag-0 0.763 > lag-2 0.582.

**These are the same arithmetic seen from inside and from outside.** A kernel that puts ⅔ weight on GBV(q−1)
and ⅓ on GBV(q−2) has an implied mean lag of **1.33 quarters**; a stated-FX series that loads on lag-1 and
lag-2 baskets is that same 1.33-quarter convolution measured on the reduced form. If the jointly estimated lag
weights on the stated-FX series are statistically consistent with `0.56 × (Φ₀, Φ₁, Φ₂) = 0.56 × (0, ⅔, ⅓)`,
then **Theo is right and the architect is right and they are the same claim** — and that sentence, with a
confidence set attached, is the single most valuable thing package `fx-lag` can produce tonight.

The thing that is *forbidden* is treating the lag as licence to add or subtract a pp of FX to revenue on top of
the lagged GBV. That is the double count the architect killed.

---

## 2. Decision 1 — FX: what `fx-lag` must estimate and report

### 2.1 Three objects, in this order. Write each to disk as it completes.

**Object A — joint lag regression on the stated revenue-FX series (the critic's must-fix 4).**
Regress `gross_fx_ex_hedge_pp` (from `28_fx_hedge_disclosures.csv`, 14 rows) jointly on the lag-0, lag-1 and
lag-2 revenue-weighted baskets built from `10_fx_daily.csv` / `10_fx_basket.csv`.

- The target is **integer-rounded** (values −4,−1,4,3,0,0,0,0,−2,0,0,1,3,4; sd 2.337pp; six exact zeros).
  Score it with the interval likelihood on `[x−0.5, x+0.5]`, **before** any comparison is quoted. A Gaussian
  point likelihood on this target is not admissible tonight.
- Report the **3-dimensional confidence set** for (w₀, w₁, w₂), not the point. At n=14 it will be wide. Say so.
- **Over-identification test:** under a booking-lock reading the fitted total scale must equal the disclosed
  non-USD revenue share **0.56** (`non_usd_revenue_share`, 0.54→0.56). A fitted scale materially away from 0.56
  means the judgemental basket weights in `10_fx_basket.csv` are wrong, not that the lag is wrong. Report the
  scale with its CI and say which reading the data prefers.
- **Reconciliation test (the deliverable):** test `H₀: (w₀,w₁,w₂) = 0.56 × (0, ⅔, ⅓)`. Report the p-value / the
  distance of the Φ-implied point from the confidence set. Whatever the answer, it is publishable.
- Benchmark against `05_fx_fits.csv` **`post22`** (best one-parameter LOO **1.2868**), never `ex21` (2.3038).
  Report your own LOO, never an in-sample fit against someone else's LOO.

**Object B — the wedge test (the critic's §7.4 item 3, the sharpest form of the hypothesis).**
ADR FX must be contemporaneous-at-booking by construction. Regress the wedge
`revenue_FX_pp − ADR_FX_pp` on the lag-0/1/2 baskets. If the revenue leg needs a lag the ADR leg does not, the
wedge **is** the recognition lag and it is directly measurable. Two-line test; run it.

**Object C — reproduce and extend the architect's λ-vs-wedge falsification.**
Regress season-demeaned λ (% relative) on `revenue_FX_pp − [⅔·ADR_FX_{q−1} + ⅓·ADR_FX_{q−2}]`. You must
reproduce **slope +0.158, se 0.275, t +0.57, r +0.179, n 12** as an acceptance check, then extend to all four
seasons **with the interval likelihood on the letter-rounded integers** (which currently attenuate it) and with
regional pass-through weighting (`10_regional_fx_passthrough.csv`: EMEA 1.043 / LatAm 0.623 / APAC 0.86, NA not
identified). Report the slope both ways. Pre-registered: adding 4Q26 must keep **|t| < 2**.

### 2.2 What `fx-lag` is forbidden to emit

- **No additive pp FX adjustment to revenue.** Ever. Not −3.4pp (`29_q4_fy27_bridge.py`), not +0.41pp (M6),
  not +2.6pp (guide-anchored). All three are rejected **as inputs**; all four constructions appear **only** in
  the four-way reconciliation exhibit, with a named cause per term and the honest statement that the spread is
  ~3pp ≈ $90M on 4Q26 and ~$430M on FY27.
- **Never add `28_fx_hedge_forward.csv`** (−0.21/−0.21/−0.18/−0.18pp) on top of letter-stated after-hedge FX.
  It is already inside it. Adding it separately understates revenue by ~0.2pp a quarter.
- **No FX pp quoted to two decimals.** One decimal, with a CI, or a range.

### 2.3 What `fx-lag` must emit

1. The lag-weight confidence set and the H₀ reconciliation result (§2.1).
2. The **booking-date FX carried through Φ**, as an *output* of the lagged-GBV arithmetic, for the memo exhibit:
   3Q26 = ⅔(+1.0) + ⅓(+5.0) = **+2.3pp**; 4Q26 = ⅔(≈0.0) + ⅓(+1.0) = **+0.3pp**; **step −2.0pp**, against a
   lagged-GBV growth step of −1.7pp, i.e. **ex-FX accelerates +0.4pp**. These inputs are basket y/y figures;
   recompute them from `10_fx_basket.csv` / `10_fx_quarterly.csv` and report your recomputation, not these.
3. The already-determined share, per §2.4.

### 2.4 The already-determined share at a guide date — binding definition

Report **all three** of the following, always together, never one alone:

```
determined_FX(d) = (1 − λ) + λ × (days elapsed in target quarter at d) / (days in target quarter)
  λ = 0.75 (M6's fitted check-in share), 5 Nov 2026, 4Q26 (92 days, 35 elapsed): 0.25 + 0.75 × 0.38 ≈ 0.54
  λ = 0    (booking lock, the lag hypothesis):                                            ≈ 1.00
  Report determined_FX as a function of λ across the Object-A confidence set, as a band.

determined_volume(5 Nov 2026, 4Q26) = 1.00
  "At the guide date, 100% of the GBV that will convert into Q4 revenue has printed." This is the
  defensible sentence and it is volume-based, not balance-sheet-based.

determined_volume(2 Oct / 22-24 Oct 2026, 4Q26) ≈ 1/3
  At the pitch date 3Q26 GBV has NOT printed. Only the ⅓ weight on 2Q26 GBV ($27,200M) is known.
  This asymmetry must be stated in the memo, not glossed.
```

- **The 82% figure is struck.** It is `q4_driver_realised_share` from `29_fx_step_down.csv` — the realised share
  of a *two-quarter-lagged driver*, imported into a contemporaneous model. Do not quote it.
- **"85-90% of the quarter is on the booking ledger at the guide date" is struck.** That is the Q1-end figure.
  Q3-end unearned-fee coverage is **0.661 / 0.668 / 0.655**, and **0.599** in the RNPL era — the exact vintage
  for the 4Q26 guide.

---

## 3. Decision 2 — the restated-backlog pin: the circularity test and the fallback

The critic's algebra: `d_q` is defined as the gap between reported unearned fees and *coverage_norm ×
next-quarter revenue*, and `d_q = gap / reported`. Therefore

```
restated_q = reported_q × (1 + d_q) = reported_q + gap_q ≡ coverage_norm_Q × Revenue_{q+1}
```

identically. For 2Q26 the value is literally `0.697 × the 3Q26 guide midpoint ($4,730M)`. Regressing
next-quarter revenue on it returns R² ≈ 1 by construction.

### 3.1 Test T1 — run this FIRST, before any modelling (owner: `tracker-backlog`, 20 minutes)

Numerically reconstruct, for 3Q25-2Q26 (`d_q` = 0.9 / 3.8 / 16.2 / 16.5%):

1. `reported_q × (1 + d_q)` and `coverage_norm_Q × Revenue_{q+1}`. Report the ratio per quarter.
2. **Pass condition:** the two agree to worse than 2% in at least half the quarters ⇒ the restatement carries
   independent balance-sheet content and may proceed as a pin (still subject to §3.2).
3. **Fail condition (expected):** they agree to better than 0.5% ⇒ **the restatement is circular. It is struck
   as a pin, struck as a feature, and struck from every window and every likelihood in every package.**

### 3.2 Two further defects that bind even if T1 somehow passes

- **`d_q`'s coverage norms are full-sample** ("2023-25 seasonal coverage norms") applied inside an expanding
  window whose origin is 2023. Any restated series used in a replay must recompute the coverage norm
  expanding-window through T−1, and the full-sample and PIT versions must be published side by side.
- **Formula-versus-number discrepancy.** The documents write `reported/(1 − d_q)`; the numbers quoted (+16.6%
  for 1Q26, +15.4% for 2Q26) come from `reported × (1 + d_q)`. A 3pp gap in the repo's own restatement.
  **Ruling: if a restatement is computed at all it is `reported × (1 + d_q)`**, matching the quoted numbers,
  and every row carries `basis = derived`.

### 3.3 Gate G1, redefined

G1 passes only if a **non-circular** backlog construction beats naive on revenue growth on **both** windows.
The circular construction is excluded by definition and cannot be used to pass the gate. **Expect G1 to fail.
Publish the negative result as an exhibit — it is worth more than a manufactured pass.**

### 3.4 The fallback, pre-declared so nobody waits for G1

Φ's tail is pinned by, in this order:

1. **The column-sum restriction** — `Σ_k Φ_k` implied by each season's λ_s. One equation per quarter.
2. **The raw reported unearned-fee / funds-held series used on a VOLUME target only.** This is the honest
   claim and it is supported: the survivor beats naive on **nights** (0.90×, AR(1) 0.65×) and **fails** on
   revenue (WF 1.17× naive, 1.28× AR(1)). Say: *"the backlog predicts volume, not dollars."*
3. **The booking-curve Dirichlet prior**, capped at a weight worth **≤4 quarters** of data and explicitly
   flagged: `booking_curves_by_market.csv` is a **single Jul-Aug 2026 vintage**, host blocks included,
   calendars carry no price, and `median_min_nights` is a host supply setting, not stay length. Using it at a
   2023 replay origin is **look-ahead**: the PIT replay runs **without** it, the full-sample replay **with**
   it, and both are published side by side (§6.3).

State plainly in the note that Φ is weaker for losing pin #1.

---

## 4. Decision 3 — the fee uplift, θ, and who owns the single de-gross-up

### 4.1 θ is declared UNIDENTIFIED. This is not a hedge; it is the finding.

`data/processed/adr/12_reprice_summary.csv`, all 420 rows: `mean_jump_pp` takes only **half-integer values**
(11.5 in 65 rows, 12.5 in 13, 14.5 in 7, 13.5 in 4, 17.5 in 4) — these are **histogram bin midpoints**, not
estimates. `theta = mean_jump_pp / 13.8` exactly, and ranges **0.833 to 1.407** over 402 non-blank rows and 34
markets; 0.833-0.845 is the **Austin sub-sample**. `excess_share_12_20` has median **0.0029** with 90% of rows
below 0.01 — the identified excess mass is ~0.3pp of listings, indistinguishable from zero. And
`share_lt_m10` ≈ 0.255 versus `share_gt_10` ≈ 0.178: **more listings cut price by >10% than raised it by >10%**
in the migration window.

**Binding language everywhere:** θ is *unidentified in Inside Airbnb*, not *measured*. Any package, note or
exhibit that calls θ "measured" is wrong and must be corrected.

### 4.2 The uplift is carried as a θ range, with the GBV sign carried correctly

Single host-only fee **15.5%** replacing the split fee (guest ~14.1%, host 3%). On the migrated cohort, per the
critic's verified arithmetic:

| θ | list-price jump | migrated-cohort GBV | migrated-cohort revenue | host net |
|---|---|---|---|---|
| 1.00 (full pass-through) | +14.79% | **+0.60%** | **+4.03%** | 0.0% |
| 0.833 (Austin citation) | +12.32% | **−1.56%** | **+1.81%** | −2.2% |
| 11.5pp modal jump | +11.50% | **−2.28%** | **+1.07%** | −2.9% |

- **Central case carried tonight: +1.1% to +1.8% of revenue on the migrated cohort.** The +4.05% figure is
  quoted **only** as the upper bound, always with the label "requires full pass-through, θ = 1".
- **At θ < 1 migrated-cohort GBV FALLS.** Any exhibit showing migration raising GBV is wrong. And because
  revenue *is* 15.5% of GBV under the single fee, anything that moves GBV moves revenue one-for-one — θ is not
  a GBV-channel-only effect.
- **The tax/cleaning de-rate row is DELETED.** `06_quote_line_items.csv` `li_*` columns are **counts of quotes
  containing the field** (cleaning fee: 88 of 1,707,390 quotes), not dollars; and as coded the de-rate
  multiplies the split-fee and single-fee legs identically, so it cancels out of the ratio anyway.

### 4.3 `m_q` is exogenous and dated. It is never fitted.

From `06_fee_timeline.csv` (19 dated events) plus the two deadlines: **0 / ~15 / ~25 / ~50%**, then
deadline-forced toward ~100% after **15 Sep 2026 (ex-EEA)** and **13 Oct 2026 (EEA + CH)**. Note in the package
README that the two deadlines are **not** in `06_fee_timeline.csv` (its 2026-07 row says only "to complete
during 2026"); they are sourced from `01_ground-truth/04_recent_facts.md` and must be dated there.

**Never estimate `m_q` against GBV.** The critic's positive-feedback path is real: a fitted `m_q` attributes
un-purged ADR gross-up to the migrated share, which then raises revenue through the take rate — a path from
"unexplained ADR strength" straight into "the fee edge", which is the number the pitch rests on.

Separately: the fee arithmetic is **GBV-weighted**, and professional hosts migrated first and are larger, so
the GBV-weighted migrated share runs **ahead of** the listing-weighted "~50% of listings". `fee-takerate` must
publish both and use the GBV-weighted one, Φ-weighted into the revenue quarter.

### 4.4 The single de-gross-up step — owner named

**Package `fee-takerate` owns it, exclusively, as an equation, not a request:**

```
H_{r,q} = ADR_reported_{r,q} / (1 + m_q · θ · 0.1479)        # de-gross-up, applied in exactly ONE file
fee(H, m): split  → GBV = H/0.97 × 1.141,  rev = H/0.97 × 0.171,  take 14.99%
           single → GBV = H/0.845,          rev = H/0.845 × 0.155, take 15.50%
schedule(H, m, θ) returns (GBV, revenue) JOINTLY, evaluated ONCE.
```

- `l1-reconciliation` must **not** de-gross-up ADR. It hands over either host payout per night in
  `usd_constant` **or** reported ADR — and says which, in the file header.
- The ADR workbook's `+0.50pp fee-migration reprice` row and the take-rate `take_bps` lever are the **same
  event**. Both are deleted.
- θ must appear as an explicit argument of `schedule()`. In M6 it appeared in the prose and nowhere in the
  specification; that is how it became an assumption dressed as arithmetic.

### 4.5 Pre-registered take-rate test (unchanged, but see the caveat in §11.7)

3Q26 printed take rate **≥ 18.10%** ⇒ the migration is flowing; **≤ 17.88%** ⇒ fully offset. Printed take rate
has not moved through 2Q26 (13.26% vs 13.17%, **+9bp**).

---

## 5. Decision 4 — the M6 numbers rejected versus the architecture adopted

### 5.1 REJECTED as inputs. None of these may appear in any forecast object, only in a reconciliation exhibit.

| # | Rejected | Why |
|---|---|---|
| 1 | 3Q26 gross revenue FX **+1.04pp** | Misses management's stated ~+3.2pp by 2.2pp on a quarter that is nearly observed |
| 2 | 4Q26 FX **+0.41pp**; repo bridge **−3.4pp**; guide-anchored **+2.6pp** | All are second subtractions of an effect already inside lagged USD GBV |
| 3 | 4Q26 revenue **$3,284M** and FY27 **~$16.05bn** | Rest on (1), (2) and the θ=1 uplift |
| 4 | **λ = 0.75** as a point estimate | Fitted on 14 integers; the three spec RMSEs (1.08 / 1.40 / 1.94) sit within ~1 SE (≈0.26pp) of each other |
| 5 | The **1.08 vs 2.30** RMSE comparison | In-sample 2-parameter vs LOO 1-parameter from the wrong window (`ex21`, n=17); matching-window LOO is 1.2868 |
| 6 | The **16.645%** 3Q26 conversion | Below every historical Q3 value at that kernel; an undocumented ~1.8% haircut that manufactures agreement with the frozen card |
| 7 | The **82%** determined-FX share | Realised share of a two-quarter-lagged driver imported into a contemporaneous model (§2.4) |
| 8 | **+4.05%** fee uplift as "measured" | Requires θ = 1 (§4.2) |
| 9 | The **restated-backlog pin** | Circular (§3) |
| 10 | "**11 free parameters against 79 observations**" | The Stan sketch declares `vector[T] H` as a parameter; 23 GBV observations are absorbed by 23 free `H`. True count ~35-40 against ~56 non-trivial observations |
| 11 | The tax/cleaning de-rate | `li_*` are counts (§4.2) |
| 12 | "Observable on 5 Nov, **before the finals reconvene**" | Finals are 22-24 Oct; 5 Nov is **after**. The pitch is pre-positioned and eats an overnight gap with sd 8.7pp on below-Street events |

### 5.2 ADOPTED whole

1. **The object:** revenue as a convolution of *already-printed* GBV, not a take rate on forecast GBV.
2. **One host-payout numéraire** fee algebra, evaluated once, returning `(GBV, revenue)` jointly.
3. **The hedge `Λ_q` in dollars, added once**, after pre-hedge revenue.
4. **Interval likelihoods everywhere** — letter integers on `[x−0.5, x+0.5]`, guide buckets as `lo ≤ x ≤ hi`,
   coded phrases carrying `phrase_kind` and never entered as a symmetric band around a fabricated integer.
   This is the cheapest power gain available and it binds on every package.
5. **The four-way FX reconciliation as an exhibit**, with a named cause per term.
6. **The two-sided take-rate framing** — single-fee uplift versus the 29 Aug 2026 direct-link pilot at 6-10%
   (**0-15bp** of FY27 take rate, never −0.8pt) versus the hotel credit expiring 31 Dec 2026.
7. **Φ as a communication device** — "what share of quarter q's revenue is already on the ledger at date t".
8. **RNPL is a Φ/ρ effect, not a take-rate lever.**
9. **The negative-test triage:** the Trends/macro/peer/tone negatives do not bind on a design with no
   exogenous demand predictor. Reuse that argument verbatim; it is correct.

### 5.3 The kernel: adopted with a mandatory sensitivity, not adopted blind

The architect publishes `w₁ = ⅔`. The critic's grid shows the pooled within-season relative sd is **flat**:
0.0127 (w₁=0), 0.0105 (0.20), **0.0099 (0.33)**, **0.0099 (0.38)**, 0.0102 (0.50), 0.0109 (0.62), 0.0114
(0.667), 0.0154 (1.00) — i.e. the optimum is near 0.33-0.38 and `w₁ = ⅔` is *not* the minimiser. Stability is a
property of smoothly-growing GBV, not evidence about Φ.

**Ruling.** `w₁ = ⅔` is the **published kernel** — the audit's kernel, the one the architect's Q4 object, the FX
decomposition and the 100%-determined claim are all built on, and the one that reproduces the acceptance table.
But `kernel-lambda` **must** publish the full grid, report the λ table at both `w₁ = ⅔` and `w₁ = 0.38`, report
a leave-one-quarter-out criterion with a CI (never the in-sample dispersion used as its own evidence), and
propagate `w₁ ∈ [0.33, 0.667]` as a sensitivity band on every downstream number.

**The expected result is the answer to the attack, so compute it explicitly:** at `w₁ = ⅔`,
`⅔(26,300) + ⅓(27,200) = 26,600 × 12.030% = $3,200M`; at `w₁ = 0.38`,
`0.38(26,300) + 0.62(27,200) = 26,858 × ~11.89% ≈ $3,193M`. If that holds, the honest sentence is *"the kernel
is not identified better than ±0.2 in w₁, and here is what that costs: about $7M on 4Q26, 0.2%"* — which is a
Citadel answer, where *"the conversion is stable to 0.14pp"* on n=3 is not. Verify it; do not assert it.

---

## 6. Decision 5 — M5 scope, and Decision 6 — windows, baselines, metrics, registry

### 6.1 M5 scope = calibration rail and challengers ONLY

**Built:** the challenger bank; PIT histograms; CRPS; split conformal; the coverage grid; the declared
judgemental ensemble with a sensitivity table; the same-day 5-Nov extraction tool; the 194-quote annotation as
a *descriptive* artefact keyed on `guide_id`.

**Not built, ever, tonight or later:** the hierarchical cushion model (19 call-level observations, features
averaged to the call by the spec itself, one observation per random-effect group so τ is the prior; the target
`cushion` is **$M** with mean 24.9 / sd 24.1 / 4 exact zeros, against a `N(0, 0.5)` slope prior — a ~50×
mis-scaling that manufactures a null); the cross-border and LOS text proxies; the 67.5M-review store (single
2026 scrape, presence is survivorship-selected monotonically in distance from the snapshot — the **least**
PIT-safe source in the repo, not the most); the repeat-listing hedonic (no y/y price data exists on disk: the
quote panel is 13 cities × Mar-Aug 2026, IA dumps carry no price column, and the listed-vs-quote basis change
moves hedonic coefficients 20-30%); NNLS ensemble weights presented as learned.

**Two corrections that bind:**
- **The monotone GBM keeps its sign prior ONLY on `adr_fx_effect`** (`usd_broad → adr_fx_effect`: r −0.95,
  perm p 0.001, confidence `high`). The **nights** constraint is REMOVED: `usd_broad → nights_yoy` has effect
  **+0.2235** (positive), r 0.3179, spearman **−0.0637**, perm p **0.2657**, confidence **`none`**, and
  `r_from2024` **−0.3954** — the sign flips between windows. And monotonicity is a shape restriction, not a
  leakage control; do not call it one.
- **Conformal is reported honestly.** State that exchangeability is violated by construction (trend,
  seasonality, autocorrelation, an expanding-window design). At `n_cal = 6`, α = 0.2, the conformal quantile is
  the `ceil(7 × 0.8) = 6`th order statistic — **the maximum of the six residuals** — so attainable coverage is
  **6/7 = 85.7%** and 80% is not targetable. Publish the attainable-coverage grid at the actual `n_cal`. Name a
  time-series variant (weighted/adaptive conformal, EnbPI) as the thing you are not doing and why.

### 6.2 Windows — exact, binding, no reinterpretation

Windows are indexed by **target quarter**. From `02_guidance_ledger.csv` (`metric == 'revenue_usd_m'`):

- **W1: target quarters 1Q23 … 2Q26 — n = 14 scoreable guide dates**, 2023-02-14, 2023-05-09, 2023-08-03,
  2023-11-01, 2024-02-13, 2024-05-08, 2024-08-06, 2024-11-07, 2025-02-13, 2025-05-01, 2025-08-06, 2025-11-06,
  2026-02-12, 2026-05-07.
- **W2: target quarters 1Q24 … 2Q26 — n = 10 scoreable guide dates**, 2024-02-13 … 2026-05-07.
- **LIVE:** the 2026-08-06 guide (target 3Q26, range $4,690-4,770M) has **no realised actual**. It is the
  pre-registered out-of-sample point. It is **never** counted in any metric, n, or gate.
- **A result must survive both W1 and W2 to be quoted.** Not "improve on both" — survive: beat every baseline
  in §6.3 on the headline metric in both.

### 6.3 Point-in-time rules, binding on every package

1. **Refit at guide dates, not quarter ends.** The information set at guide date `d` is: letters and 10-Qs
   filed **strictly before** `d`; FRED FX through `d − 1`; consensus values whose vintage timestamp is before
   `d`. Nothing else.
2. **Expanding window.** No rolling windows, no fixed training length.
3. **10-Q data post-dates the guide.** The guide is issued with the shareholder letter; the 10-Q follows days
   later. So `designated_notional`, `aoci_cash_flow_hedges_musd`, `reclassified_to_revenue_musd` and
   `expected_reclass_next_12m_musd` for the just-closed quarter are **not** in the guide-date information set —
   and `gross_fx_ex_hedge_pp` is constructed from `reclassified_to_revenue_musd`, so the **FX target itself is
   not PIT-available at the date the feature is formed**. `fx-lag` must either lag the target by one filing or
   run the estimation as an explicitly non-PIT structural fit and label it so. State which.
4. **Specification is filtered by date, not just data.** Every prior is elicited from trailing data through
   T−1. **Publish the full-sample-prior and the PIT-prior replays side by side.** A package that publishes only
   one has not met the bar.
5. **Letter-rounded integers are scored on `[x−0.5, x+0.5]`, never as points.**
6. **`basis == 'derived'` rows are excluded from every likelihood** — the 14 NA/EMEA nights cells 4Q22-3Q24 are
   residual-to-total constructions carrying XBRL FX contamination. The 22 numeric LatAm/APAC cells are
   **rounding intervals, not equalities**.
7. **Executable returns only.** `open_*` columns, never `legacy_*`. Next-session-open entry cut the
   guide-below-Street rule from −8.90% to −4.21%.
8. **Feature-definition leakage is real and uncontrolled by fold structure.** Any hand-curated, full-sample
   label (e.g. `abnb_declined_to_quantify.csv`) must be declared where used.

### 6.4 Baselines — every registered object must be scored against all five

| # | Baseline | Definition |
|---|---|---|
| B1 | naive | last observed value of the same series |
| B2 | AR(1) | fitted expanding-window on the same series |
| B3 | trailing-4 mean | of the same series |
| B4 | guide + cushion | `guide_mid × (1 + trailing-8 A/g cushion)`; trailing-8 as of that guide date |
| B5 | pre-guide Street | the **vintage-stamped** consensus whose timestamp precedes the guide date |

B4's cushion is measured as **A/g** (print ÷ guide midpoint — directly observed, kernel-free), never g/M. The
trailing-8 as of 6 Aug 2026 is `0.86, 2.69, 0.98, 2.52, 0.86, 3.27, 2.61, 1.06` ⇒ **mean +1.856%, median
+1.79%, sd 1.006pp**. All 19 scoreable guides were beaten at the midpoint (19/19); 15/19 above the top of the
range.

**B5 vintage discipline — the trap that killed the peer read-across.** The 6 Aug 2026 pre-guide Street for 3Q26
is **LSEG $4,610M**. It is **not** Zacks $4,740M (4 Sep 2026). Using a post-guide vintage as the pre-guide
Street is a disqualifying error. Every B5 row carries `street_vendor` and `street_as_of`.

**Honest prior:** B5 currently **beats** our guide-level forecast (MAE 1.61% vs 1.93%; bias −0.01% vs −1.23%).
Gate G4 is a **sign** test (target ≥8/14 on W1), not a level test. If your object loses to B5 on level, say so
in your note — that is the expected outcome and hiding it is worse than losing.

### 6.5 Metrics — every registered object reports all of these

RMSE ratio to naive (the repo convention); MAE; bias; CRPS from the quantiles; PIT histogram over the window's
guide dates; split-conformal 80% coverage on the last 6-8 residuals **with the exchangeability violation stated
in the same sentence**; and the **free-parameter count**, published, with the observation count it is measured
against. Any package that cannot state its parameter-to-observation ratio does not ship.

**Target parameter budget for the core:** 4 seasonal λ + 1 lag weight + 1 cushion + 1 κ = **7 free parameters**
against 23 revenue identities, 19 interval-censored guide buckets and 72 exact regional revenue cells.

**Contraction test:** for every term in the FY27 decomposition, publish prior-to-posterior contraction. **Strike
any term contracting < 20% from the exhibit.**

### 6.6 Registry conventions

Registered forecast objects go to
`data/processed/forecast_methods/registry/<package>__<object>.csv`, in the format defined by
`analysis/src/forecast_methods/harness/README.md`. **That README is authoritative; where it and this document
differ, the README wins and you record the difference in your note as a harness change request.**

At the time of writing, `analysis/src/forecast_methods/` **does not yet exist**. Until the harness lands, write
the registry file with at least these columns, one row per (object, origin guide date):

```
object_id, package, target_period, target_metric, origin_guide_date, window,
prior_basis, point, q10, q50, q90, sd,
n_free_params, n_obs,
b1_naive, b2_ar1, b3_trailing4, b4_guide_cushion, b5_street,
street_vendor, street_as_of, knowable_from, spec_id, notes
```

- `window ∈ {W1, W2, LIVE}`; `prior_basis ∈ {pit_prior, full_sample_prior}` — **both replays, both written.**
- `target_metric` names the series exactly (`revenue_usd_m`, `guide_mid_usd_m`, `take_rate_pct`, …).
- One file per object. Do not invent a second format. Do not edit `harness/` or `L0/` files.

### 6.7 Interface schema on every file crossing a layer boundary

`quarter, region, line, variable, value, unit, basis, vintage, source_path, knowable_from`
with `basis ∈ {filed, letter_bucket, letter_integer, back_out, derived, modelled, assumed}`; interval rows also
carry `lo, hi, phrase_kind`. `vintage` = the date the value was first publishable; `knowable_from` = the date a
backtest may use it.

**One object crosses L1 → L2: `G_q`, GBV in USD, booking-dated, one number per quarter.** Nights, ADR, geo mix,
size mix, LOS, seats and regulation cannot re-enter revenue because they are not in the interface. Write that
line into `model/assumptions.md` as a rule.

---

## 7. Decision 7 — the 4Q26 object

### 7.1 Definition

```
print_4Q26 = λ_Q4 × [ ⅔ · GBV_3Q26 + ⅓ · 27,200 ] × (1 + fee_step_4Q26) + Λ_Q4
             λ_Q4 = 12.030%  (11.946 / 12.117 / 12.026; within-season range 0.171pp)
             Λ_Q4 in dollars, added ONCE, and NOT re-added from 28_fx_hedge_forward.csv

guide_mid_4Q26 = print_4Q26 / (1 + c),   c = trailing-8 A/g cushion, mean +1.856%, sd 1.006pp
guide_range    = midpoint ± (1.7% to 2.2% of midpoint)   [trailing-8 mean width 1.86%; 3Q26 was 1.68%]
predictive sd  = sqrt(kernel PIT RMSE 2.44%² + cushion draw 1.006%²) ≈ 2.6pp
```

**GBV_3Q26 grid** (report the whole grid, headline the central case): 25,900 / 26,185 (frozen card) /
**26,300 (central, +14.8%)** / 26,600 / 27,000.

**Central, no fee step:** print **$3,200M** (+15.2%), guide mid **$3,141M**.
**Central, fee step at half weight:** print **$3,240M**, guide mid **$3,181M**, range ≈ **$3,145-3,215M**.

### 7.2 The fee step weight — defined, not inherited

`fee-takerate` computes, from primitives:

```
fee_step_4Q26 = uplift(θ) × migrated_GBV_share_Φweighted_4Q26
  uplift(θ) ∈ {+1.07% (11.5pp modal), +1.81% (θ=0.833), +4.03% (θ=1)}
  migrated_GBV_share is GBV-weighted (not listing-weighted) and Φ-weighted into 4Q26
```

**The Q4 object carries HALF of the central-θ value, and publishes the full range.** If the recomputed full step
at central θ comes out materially below the ~+2.5% implied by the architect's $3,240M, then the print moves
toward **$3,200-3,220M** and the guide toward **$3,141-3,160M**, and `P(guide < Zacks)` rises above 0.60.
**Report that honestly. Do not force the number back to $3,181M.**

### 7.3 Vendor-stamped anchors — name the vendor and the timestamp or do not state the trade

| Anchor | Value | Vintage |
|---|---|---|
| Zacks 4Q26 | **$3,200M**, 10 estimates, range $3,050-3,700 (the $3,700 is probable bad data; median ≈ $3,150M) | 4 Sep 2026 |
| Alpha Vantage, 36 analysts, 4Q26 | **$3,158M** | 11 Sep 2026 |
| LSEG 3Q26, **pre-guide** | **$4,610M** | at the 6 Aug 2026 guide |
| Zacks 3Q26 | $4,740M (7-10 est.) | 4 Sep 2026 — **never** usable as the 6 Aug pre-guide Street |
| Zacks FY26 / FY27 | $14.10-14.16bn / $15.73-15.76bn | 3-4 Sep 2026 |

`P(guide mid < Zacks $3,200M) ≈ **0.60**` [0.41 at the full fee step, 0.76 at no fee step].
`P(guide mid < Alpha Vantage $3,158M) ≈ **0.47**` [0.29, 0.65].
**Say it out loud: the guide-below-Street trade is a 60/40 and it flips on which vendor you quote.**

**Put the consensus's own inconsistency on the exhibit:** the quarterly Zacks consensus sums to
`2,678 + 3,608 + 4,740 + 3,200 = $14,226M` against an FY26 consensus of **$14,100M** — a **$126M**
self-disagreement, larger than our edge. That is a point in our favour if we say it first.

### 7.4 Print versus guide — never conflate

They differ by **+1.86%**. Every number in every note and exhibit is labelled **guide** or **print**. The team's
own `29_q4_fy27_bridge.py` $3,111M is a **guide** that additionally subtracts an FX step already inside the
lagged USD GBV — two errors, both corrected, and publishing the correction of our own work is the page-2
reconciliation table.

---

## 8. Decision 8 — the FY27 object and the named non-overlapping contributions

### 8.1 Definition

FY27 = the sum of four quarterly kernel objects, plus a decomposition whose lines are each an output of exactly
one owner and appear exactly once. They sum by construction.

| Contribution to FY27 revenue growth | pp | Owner | Class |
|---|---|---|---|
| Lagged-GBV **volume** ex-FX (home nights + hotel nights + seats) | **+8.6** | `l1-reconciliation` | measured/assumed |
| Lagged-GBV **within-region price** ex-FX | **+3.5** | `l1-reconciliation` | +0.6 measured (bedroom ε = 0.23), +0.0 LOS, **+2.9 UNIDENTIFIED** (price + sub-regional mix) |
| **Geographic mix** (output of `Σ_r w_r ADR_r`) | **−1.5** | identity | measured: −1.06pp (2024) → −1.48pp (2025), deepening as NA nights share goes 32.6 → 31.3 → 29.6% |
| **Seats / hotel dilution** (output of `N = Σn_home + n_hotel + s_exp + s_svc`) | **−0.5** | identity | structure measured, ticket prices assumed |
| **Booking-date FX** carried through Φ | **−0.4** | `fx-lag` | measured (spot-constant); ±1.5pp on a ±1sd euro path |
| **Fee / take-rate step** net of incentives and the direct-link pilot | **+0.9** | `fee-takerate` | +40-50bp gross migration, less **0-15bp** direct-link (never −0.8pt), plus the 15% hotel-credit expiry 31 Dec 2026; carried at **half weight** |
| **New lines outside GBV** (ads $0 FY26, Services excess) | **+0.2** | `l1-reconciliation` | assumed; `nb_incr` netting as built at `13_driver_model.py:437` — **do not "fix" it** |
| **Regulation** (dated DiD on EMEA nights) | **−0.3** | `l1-reconciliation` | model-based; replaces `REG_DRAG_PP × 1.67`, which is deleted |
| **FY27 revenue growth** | **+10.5** | | vs Street +11.3% |

`FY26 = 1H26 actual $6,286M + 3Q26 $4,815M + 4Q26 $3,240M = $14,341M (+17.2%)`;
`FY27 = $15,850M (+10.5%)`, 80% [$15,350M, $16,350M].

### 8.2 Two honesty requirements that are not optional

- **"Our FY27 is within 1% of consensus" must be said in the first 200 words.** $120M on $15.75bn is inside the
  kernel's own walk-forward MAE of **1.74%**. A judge finds it in ninety seconds and it is far better said by us.
  The variant view is compositional, not level: guide-versus-print separation, the FX/product lap, and the three
  ADR levers the Street reads as strength (bedroom nights at ε = 0.23 ⇒ **+0.46pp**, not +2pp; geo mix −1.48pp
  and deepening; seats dilution −0.5pp).
- **Do not split the +2.9pp price/sub-regional residual.** Airbnb discloses no country-level ADR. Report the
  identified **sum** as a 2-d ridge, flagged unidentified on the exhibit.

### 8.3 Tonight's FY27 object is explicitly a PLACEHOLDER

The L1 volume/price build is **not** constructed tonight (§9). Tonight's FY27 object is assembled from
`kernel-lambda` + `guidance-policy` + `fee-takerate`, with the four `l1-reconciliation` lines carried as **fixed
inputs from the table above, labelled `basis = assumed, not rebuilt tonight`**. No implementer may fabricate an
L1 build to fill the gap.

---

## 9. Decision 9 — what is explicitly NOT built tonight

1. The **Stan / PyMC state space** in any form. Constrained least squares with a block bootstrap gives every
   point estimate. (M1's 120-state `τ_{r,t}` random walk is dead regardless.)
2. The **120-market bottom-up panel** as a nights measurement (Gate G3; corr NA 0.14 / EMEA −0.07 /
   LatAm −0.36 / APAC 0.22; first-difference LatAm −0.71).
3. The **joint hedonic** rebuild. `06_wtp_hedonic_coefs.csv` already contains a richer version. `M1`'s
   `06_quote_line_items.csv` hedonic is impossible (76 aggregate rows, no price/capacity/bedroom/LOS column).
4. The **second Inside Airbnb capture** — it is an irreversible data-collection clock for P2, not tonight's code.
5. The **67.5M review store**, the cross-border proxy, the LOS proxy.
6. **M5's hierarchical cushion model**, in any form, at any n.
7. **M3's revision regression** — it is the identity `(1+rev) ≡ (1+κ)(1+gap)`, verified to 4.6e-6 on all 18 rows.
8. The **9/9 guide-below-Street 20-day drift rule as a tradeable signal**. All 9 events sit in 2022Q3-2025Q1, a
   window in which 10 of 11 prints were negative at 20 days regardless of gap sign (mean −3.51%); Fisher exact
   in-window p = 0.27. Report it **only** as a base rate with executable next-open returns and that caveat.
9. Any **second subtraction of the FX step**; any addition of `28_fx_hedge_forward.csv` on top of letter-stated
   after-hedge FX; any use of Zacks 4 Sep as the 6 Aug pre-guide Street.
10. The **R-engine cross-check**, **FY28**, the **regulatory DiD**, and the **NNLS ensemble**.
11. **Monte-Carlo-only** and **SARIMAX-only** work (Theo's standing order). A Monte Carlo may propagate an
    interval; it may not *be* the method.

---

## 10. Claims that may not be made, in any package note

The Inside Airbnb supply-exit figures (Paris 33%, Nashville 44%, Chicago 40% — 25 of 103 year-ago pairs had a
partial-scrape endpoint); any options-implied move for 5 Nov (withdrawn, not corrected; the 6 Nov weekly is not
listed); the nights-surprise 20-day drift; "−0.8pt of take rate from the direct-link pilot" (use 0-15bp);
"no publisher quotes an ADR consensus" (Zacks does, 5 prints, ABNB beat 5/5); AirROI's 55.9% as a measurement of
hidden fees (it is a model assuming the pre-migration 14% guest fee); that the 2020Q4 move was about margin
framing; that the WS08 guide reconciliation forecasts a beat; that the 0.988 revision slope is a finding; that
"three independent constructions of 3Q26" exist (it is **two** — the kernel and guide-plus-cushion, 0.3% apart);
that `h2_bridge_gbv_lag_conversion.csv` independently confirms λ_s (same six ratios, same two columns);
"85-90% of the quarter is on the ledger at the guide date".

---

## 11. Conflicts found between documents that I could NOT resolve (each carries a fiat so work proceeds)

1. **The lag weight `w₁`: ⅔ versus 0.38.** The architect, the audit and `h2_bridge` use ⅔; M6 uses 0.38; the
   critic's grid minimises at 0.33-0.38 and is flat over [0.20, 0.62]. The architect's acceptance test bakes in
   ⅔, so passing it proves only that the code implements ⅔. **Fiat: publish ⅔, report both, propagate
   [0.33, 0.667] as a sensitivity band on every downstream number (§5.3).**
2. **Three incompatible readings of the lag length in one repo.** Φ = (0, ⅔, ⅓) implies a mean lag of **1.33**
   quarters; `28_fx_hedge_tests.csv` lag-1 r 0.861 > lag-2 0.582 implies **~1**; `0.56 × the 1Q26 basket`
   reproducing 3Q26's guided FX to 0.06pp implies **2**. **Fiat: `fx-lag` adjudicates with a confidence set and
   reports all three readings side by side. Nobody else picks one.**
3. **The restatement formula.** `reported/(1 − d_q)` (integrated system §2.6, Cards 1 and 4) versus
   `reported × (1 + d_q)` (the numbers actually quoted; a 3pp gap). **Fiat: `reported × (1 + d_q)`, `basis =
   derived` — and struck entirely if test T1 shows circularity (§3.1).**
4. **`20_vintage_register.csv` cannot be what two documents ask of it.** The existing file is a *series-lineage*
   register (`series, file, native_freq, release_lag_days, vintage_reconstructible, how, lag_applied,
   approximation_label`). §4.1 and Card 0 both want it to carry `vendor, period, metric, value, n_estimates,
   as_of_timestamp, url` per consensus value. **Fiat: `L0-spine` creates a NEW `L0_vintage_register.csv`.
   `20_vintage_register.csv` is not overwritten and not extended.**
5. **The guide-date count.** "About 14" / "n=14" is reconcilable with `02_guidance_cushion_series.csv` only
   under target-quarter indexing. **Fiat: §6.2 — W1 targets 1Q23-2Q26 (n=14), W2 targets 1Q24-2Q26 (n=10), the
   6 Aug 2026 guide is LIVE and scores in no metric.**
6. **Whether the FY27 "+0.9pp fee step at half weight" already embeds the θ correction is never stated.** The
   critic's correction cuts the migrated-cohort uplift by 2-4×. **Fiat: `fee-takerate` recomputes from
   primitives and reports the delta against +0.9pp explicitly. Do not assume either way.**
7. **The 3Q26 take-rate pre-registration is nearly uninformative as written.** The threshold is ≥18.10% while
   the architect's own central printed take rate is **18.14%** — 4bp of separation — and the guide language is
   "relatively in-line" (17.88%). A test whose threshold sits 4bp below the central case discriminates almost
   nothing. **Fiat: keep the pre-registered threshold (it is already frozen), and additionally report the
   posterior `P(take rate ≥ 18.10%)` so the test's power is visible rather than implied.**
8. **The harness does not exist yet.** `analysis/src/forecast_methods/` is absent as of 23:00 on 11 Sep, so the
   registry format these addenda depend on is undefined at the moment they are written. **Fiat: §6.6's minimum
   column set, superseded by `harness/README.md` the instant it lands; every package records the difference as
   a harness change request in its own note.** This is the highest-risk coordination item tonight.
9. **M6 §5's own internal FX inconsistency** (+1.04pp gross in the schedule table versus +0.73% in the 3Q26
   build, a $15M difference) is never reconciled in any document. It does not matter tonight because both
   numbers are rejected (§5.1), but it should not be quoted from either place.

---

## 12. Verification stamp — what I re-ran from the data before issuing this document

Run with `/Users/theomachado/.venvs/citadel-abnb/bin/python` from the repo root, 11 Sep 2026. Four checks, all
passed; they are the numbers the most packages depend on, so nobody has to re-litigate them tonight.

| # | Check | Source | Result |
|---|---|---|---|
| V1 | λ_s acceptance table at w₁ = ⅔ | `data/processed/overnight/02_kpi_panel_quarterly.csv` (`revenue_musd`, `gbv_musd`) | **Reproduces exactly.** Q1 12.803 (1Q23) / 13.034 / 12.325 / 12.612; Q2 13.724 (2Q23) / 13.449 / 13.946 / 13.736; Q3 17.391 / 17.145 / 17.182; Q4 11.946 / 12.117 / 12.026. Note the 2023-2026 table in the cards **starts at 1Q24 for Q1/Q2** — 1Q23 (12.803) and 2Q23 (13.724) also exist and are usable; `kernel-lambda` should report all of them and say which it uses. |
| V2 | w₁ grid shape | same | Minimum at **w₁ = 0.33**, flat across [0.20, 0.50], ⅔ clearly worse. Levels differ from the critic's by pooling convention — see the `kernel-lambda` addendum. **The ruling in §5.3 stands on the shape, which replicates.** |
| V3 | Trailing-8 A/g cushion as of 6 Aug 2026 | `02_guidance_cushion_series.csv` (`beat_vs_mid_pct`) | **Reproduces exactly:** last 8 = 0.86, 2.69, 0.98, 2.52, 0.86, 3.27, 2.61, 1.06 ⇒ **mean 1.8562%, median 1.790%, sd 1.0064pp**. 19 scoreable guides, **19/19** positive at the midpoint, **15/19** above the top of the range. |
| V4 | W1 / W2 guide-date lists | `02_guidance_ledger.csv`, `metric == 'revenue_usd_m'` | **Confirmed.** 22 revenue guide rows; 19 with a realised actual; 2 pre-2021 rows carry no `value_mid`. W1 = the 14 dates in §6.2 (targets 1Q23-2Q26), W2 = the last 10 (targets 1Q24-2Q26), and **2026-08-06 (target 3Q26, mid $4,730M) has `actual = NaN` ⇒ LIVE, scores in nothing.** |
| V5 | The 72-cell spine | `10_xbrl_revenue_geography.csv` (258 rows) | **Structure confirmed and written into the `L0-spine` addendum.** 4 regions × 14 filed quarter-ends = 56 (no 4Q cell is ever filed), + 4 regions × 4 years of Q4 back-outs = 16 ⇒ **72**. Raw rows restate across filings: 95 three-month rows from 1Q22 collapse to **63** unique `(start, end, geo)`. 4Q22 back-out reproduces **$1,902M** to the dollar. The `country:US` / `NonUs` / `country:FR` tags are a separate axis — **do not mix them in.** |

Two things I could not verify because they do not exist yet, both already flagged as risks:
`analysis/src/forecast_methods/` (and therefore `harness/README.md`) is **still absent** at the time of writing
— §6.6's column set governs until it lands (§11.8); and `data/processed/forecast_methods/` does not exist, so
the first package to write creates it.

---

# PACKAGE ADDENDA

Each addendum below is handed verbatim to its implementer. §§1-12 above bind in addition.

---

## Addendum — `harness` (built first, blocks everyone)

You are the single point of coordination failure tonight. Ship a minimal, correct, documented format in the
first 30 minutes and announce it; do not gold-plate.

- Define and document `data/processed/forecast_methods/registry/<package>__<object>.csv` in
  `analysis/src/forecast_methods/harness/README.md`. **Start from §6.6's column set** and only add. If you
  change a column name, the README is authoritative and every package will re-read it — so freeze early.
- Provide one scoring function that, given a registry file, emits the §6.5 metric block: RMSE ratio to naive,
  MAE, bias, CRPS from `q10/q50/q90`, PIT histogram, split-conformal 80% coverage on the last 6-8 residuals,
  and the parameter-to-observation ratio. Coverage output must carry the exchangeability-violation string in
  the same row; at `n_cal = 6`, α = 0.2, emit the attainable-coverage grid (the quantile is the max of 6
  residuals; attainable = 6/7 = 85.7%), not a claimed 80% guarantee.
- Provide the five baselines B1-B5 (§6.4) as functions so no package re-implements them. B4's cushion is A/g,
  trailing-8, computed as of the guide date. B5 requires `street_vendor` + `street_as_of` and must **refuse**
  a consensus row whose vintage postdates the guide date.
- Provide the W1/W2/LIVE guide-date lists as data (§6.2), hard-coded from `02_guidance_ledger.csv`
  `metric == 'revenue_usd_m'`. Assert n = 14 and n = 10. The 2026-08-06 guide is LIVE and enters no metric.
- Enforce two replays per object: `prior_basis ∈ {pit_prior, full_sample_prior}`. A registry file carrying only
  one should warn loudly.
- Do not build a model. Do not edit `L0/`.

---

## Addendum — `L0-spine` (built first)

Build three files and nothing else. No model reads a disclosure except through them.

- **`L0_exact_regional_revenue.csv` — 72 cells.** 56 filed three-month regional revenue cells 1Q22-2Q26 from
  `10_xbrl_revenue_geography.csv` (80-100 day periods) plus 16 Q4 back-outs. `basis = filed`.
  **Acceptance assertion, must pass or you stop:** 4Q22 **$1,902M** / 4Q23 **$2,218M** / 4Q24 **$2,480M** /
  4Q25 **$2,778M** reproduce to $1M. These are currently unused anywhere in the repo.
  **I opened the file tonight; build it exactly this way and the 72 falls out (verified, §12):**
  - The four-region axis is `srt:NorthAmericaMember`, `us-gaap:EMEAMember`, `srt:LatinAmericaMember`,
    `srt:AsiaPacificMember` (45 rows each). **`country:US` (35), `us-gaap:NonUsMember` (35) and `country:FR` (8)
    are a DIFFERENT disclosure axis and must never be mixed into the same panel or summed with it.**
  - Filter to `80 ≤ (end − start + 1) ≤ 100` days, then **de-duplicate on `(start, end, geo)`** — the raw file
    restates the same cell across successive filings (95 three-month rows from 1Q22 collapse to **63** unique).
    Keep the **earliest `filed`** date as the row's `vintage`, and carry `accn`.
  - The result is **14 quarter-ends × 4 regions = 56**: Airbnb files regional revenue only in the three 10-Qs
    each year, so the filed set is Q1/Q2/Q3 of 2022-2025 plus 1Q26 and 2Q26. **There is no filed 4Q cell.**
  - The 16 back-outs are, per region and per year 2022-2025, `10-K annual − (Q1 + Q2 + Q3 filed)`.
  - **The four assertion figures are company TOTALS — the sum of that year's four regional back-outs — not
    single cells.** Worked check for 4Q22: NA 822+1,098+1,326 = 3,246; EMEA 373+732+1,263 = 2,368;
    LatAm 178+137+139 = 454; APAC 136+137+156 = 429 ⇒ 9M22 $6,497M; FY22 $8,399M − $6,497M = **$1,902M** ✓.
    Assert the total to $1M **and** assert each regional back-out is positive and within ±40% of its own Q3.
- **`L0_interval_observations.csv`.** 28 genuine bucket cells (4Q24-2Q26), 68 ADR integers (±0.5pp), 24 annual
  10-K nights cells (±0.5M at the table's own precision ⇒ ±0.45pp of annual growth), 19 guide ranges, 5 bucket
  words. Every row carries `lo, hi, phrase_kind`. **Hard rule in the file header: the 14 `basis == 'derived'`
  rows (NA 8, EMEA 6, spanning 4Q22-3Q24) are EXCLUDED from every likelihood**, and the 22 numeric LatAm/APAC
  cells are **rounding intervals, not equalities**. The 10-K Geographic Mix table is an interval, **not** an
  equality. Band-midpoint bias is −0.22pp on average and **−0.72pp over the last two quarters** — never enter a
  bucket as its midpoint.
- **`L0_vintage_register.csv` — a NEW file.** `vendor, period, metric, value, n_estimates, as_of_timestamp,
  url`. **Do not overwrite or extend `20_vintage_register.csv`** (it is a series-lineage register with an
  incompatible schema — see §11.4). Seed it with: LSEG 3Q26 $4,610M at the 6 Aug 2026 guide; Zacks 4 Sep 2026
  (3Q26 $4,740M; 4Q26 $3,200M, 10 est., range $3,050-3,700; FY26 $14.10-14.16bn; FY27 $15.73-15.76bn); Alpha
  Vantage 36-analyst 11 Sep 2026 4Q26 $3,158M; S&P 3 Sep 2026 FY26 $14,160M/43, FY27 $15,760M.
  **The 6 Aug pre-guide Street is LSEG $4,610M, never Zacks $4,740M.**
- Schema on every row: `quarter, region, line, variable, value, unit, basis, vintage, source_path,
  knowable_from` (+ `lo, hi, phrase_kind` on intervals). `vintage` = first publishable date;
  `knowable_from` = first date a backtest may use it.
- Write files progressively. A crash after file 1 must still leave file 1 on disk and asserted.

---

## Addendum — `kernel-lambda`

**Acceptance test first. If it does not reproduce, stop and write the note.** From
`02_kpi_panel_quarterly.csv` alone, with `λ_s = Revenue_q / [⅔·GBV_{q−1} + ⅓·GBV_{q−2}]`, 2023-2026:
Q1 **13.034 / 12.325 / 12.612** (mean 12.657, range 0.709); Q2 **13.449 / 13.946 / 13.736** (13.710, 0.497);
Q3 **17.391 / 17.145 / 17.182** (17.239, 0.245); Q4 **11.946 / 12.117 / 12.026** (12.030, **range 0.171pp**).

Then, and this is the part the critique makes mandatory:

- **Publish the w₁ grid**, pooled within-quarter-of-year relative sd, 1Q23-2Q26. Expect approximately:
  0.0127 (w₁=0), 0.0105 (0.20), 0.0099 (0.33), 0.0099 (0.38), 0.0102 (0.50), 0.0109 (0.62), 0.0114 (0.667),
  0.0154 (1.00). **The objective is flat over [0.20, 0.62] and ⅔ is not the minimiser.** Report the λ table at
  **both** w₁ = ⅔ and w₁ = 0.38 (expected Q3 17.065/16.770/16.978, Q4 11.80/11.93/11.94).
  **Do NOT stop if your grid levels differ from the critic's.** I re-ran it tonight (§12) and got
  0.0156 / 0.0130 / **0.0125** / 0.0126 / 0.0132 / 0.0144 / 0.0149 / 0.0199 at the same w₁ values — the *levels*
  move with the pooling convention (RMS versus mean of the four within-season relative sds, and whether 1Q23
  and 2Q23 are included). **Reproduce the SHAPE, which is the finding and which is convention-free: the minimum
  sits at w₁ ≈ 0.33, the objective is flat across [0.20, 0.50], and w₁ = ⅔ is materially worse than the
  minimiser.** State your pooling convention in one line in your note.
- **Report leave-one-quarter-out**, not the in-sample dispersion used as its own evidence, with a CI on w₁.
- **Compute the cost of the flatness explicitly.** 4Q26 at w₁=⅔: `⅔(26,300) + ⅓(27,200) = 26,600 × 12.030%
  = $3,200M`. At w₁=0.38: `0.38(26,300) + 0.62(27,200) = 26,858 × ~11.89% ≈ $3,193M`. Verify. If the gap is
  ~$7M / 0.2%, that sentence is the answer to the hardest attack on the kernel and belongs in your note.
- **Pre-registered test: Φ₀ ≈ 0.** Refit the non-negative lag polynomial over k ∈ {0,1,2,3} on 22 quarters and
  show w₀ shrinks to zero, or carry it as a stated assumption with a sensitivity. If w₀ > 0 the
  "management can already see it" premise weakens and the memo's first sentence must change.
- **Do not claim independent confirmation from `h2_bridge_gbv_lag_conversion.csv`.** It is the same six ratios
  from the same two columns at w₁ = 0.667. Say so.
- Register the 3Q26 and 4Q26 print objects and the W1/W2 expanding-window PIT replay of quarterly revenue
  level, scored against B1-B5. Honest headline figures to beat/match: **MAE 1.74%, RMSE 2.44%, bias +0.99%**
  from origin 1Q23. If you exclude COVID-era λs, give the number both ways.
- The λ_Q3 arithmetic for the 3Q26 card: lagged GBV `⅔(27,200) + ⅓(29,200) = $27,867M × 17.239% = $4,804M`.
  Kernel-only $4,804M versus guide+cushion $4,818M is **two** constructions 0.3% apart, not three.
- **Parameter count:** 4 seasonal λ + 1 lag weight = 5, against 23 revenue identities. Publish it.

---

## Addendum — `fx-lag`

Your job is to make the architect's ruling and Theo's hypothesis the **same statement**, with a confidence set.
Read §1 and §2 of this document before writing code.

- **Object A:** joint interval-likelihood regression of `gross_fx_ex_hedge_pp` (14 rows; values −4,−1,4,3,0,0,
  0,0,−2,0,0,1,3,4; sd 2.337pp) on lag-0/1/2 revenue-weighted baskets. Score on `[x−0.5, x+0.5]` **before** any
  comparison is quoted. Report the 3-d confidence set, not a point. Over-identify on the disclosed non-USD
  revenue share **0.56**. **Test H₀: (w₀,w₁,w₂) = 0.56 × (0, ⅔, ⅓)** and report the result either way — this is
  your headline deliverable.
- **Object B:** regress the wedge `revenue_FX_pp − ADR_FX_pp` on the basket lags. ADR FX is
  contemporaneous-at-booking by construction, so if the revenue leg needs a lag the ADR leg does not, the wedge
  **is** the recognition lag. Two lines; run it.
- **Object C:** reproduce the architect's falsification — season-demeaned λ on
  `revenue_FX_pp − [⅔·ADR_FX_{q−1} + ⅓·ADR_FX_{q−2}]`: **slope +0.158, se 0.275, t +0.57, r +0.179, n 12** —
  then extend to all four seasons with the interval likelihood and with regional pass-through weights
  (EMEA 1.043 / LatAm 0.623 / APAC 0.86; NA not identified). Pre-registered: |t| < 2 when 4Q26 is added.
- **Benchmark on `05_fx_fits.csv` `post22` (best one-parameter LOO 1.2868), never `ex21` (2.3038).** Report
  your own LOO. At n=14 the SE of an RMSE estimate is ≈ 0.26pp — so 1.08 / 1.40 / 1.94 are indistinguishable
  and you must say so.
- **PIT hazard, flagged in your note:** `gross_fx_ex_hedge_pp` is built from `reclassified_to_revenue_musd`,
  which is 10-Q data filed **after** the guide. Either lag the target by one filing or label the fit
  explicitly non-PIT-structural. State which you did.
- **Emit:** the lag confidence set; the H₀ result; booking-date FX carried through Φ (3Q26 +2.3pp, 4Q26 +0.3pp,
  **step −2.0pp**, against a lagged-GBV growth step of −1.7pp ⇒ **ex-FX accelerates +0.4pp**) recomputed from
  `10_fx_basket.csv`/`10_fx_quarterly.csv`; and the determined-share triple of §2.4 (FX ≈54% at λ=0.75 versus
  ≈100% at λ≈0; volume 100% at the 5 Nov guide date but only ~⅓ at the 2-24 Oct pitch date).
- **Emit NO additive pp adjustment to revenue.** The repo's −3.4pp, M6's +0.41pp and the guide-anchored +2.6pp
  appear only inside the four-way reconciliation exhibit with a named cause each and the honest spread
  (~3pp ≈ $90M on 4Q26, ~$430M on FY27). Never add `28_fx_hedge_forward.csv` on top of letter-stated
  after-hedge FX. Never quote an FX pp to two decimals. The 82% determined share is struck.

---

## Addendum — `guidance-policy`

- **Cushion is A/g** — print ÷ guide midpoint, directly observed, kernel-free. Never g/M (it absorbs λ̂ bias;
  the two co-move one-for-one). Trailing-8 as of 6 Aug 2026: `0.86, 2.69, 0.98, 2.52, 0.86, 3.27, 2.61, 1.06`
  ⇒ **mean +1.856%, median +1.79%, sd 1.006pp**. Reproduce from `02_guidance_cushion_series.csv`
  (19 scoreable revenue guides; 19/19 beaten at the midpoint, 15/19 above the top of the range).
  Estimator: trailing-8 empirical with a **block bootstrap**. No PyMC, no hierarchical pool.
- `guide_mid_q = E[Revenue_q] / (1 + c)`; `range_width = 1.7-2.2%` of midpoint (trailing-8 mean 1.86%, 3Q26
  1.68%); `S_at-print = guide_mid × (1 + κ)`, **κ = +0.52%, sd 28bp, LSEG-only pairs, n ≈ 13**;
  `gap = guide_mid / S_vendor − 1` is **derived, never parameterised**; predictive sd
  `√(2.44%² + 1.006%²) ≈ 2.6pp`.
- **Emit the 4Q26 object of §7** across the full GBV_3Q26 grid (25,900 / 26,185 / **26,300** / 26,600 / 27,000),
  with and without the fee step, and both `P(guide < Zacks $3,200M, 4 Sep)` ≈ **0.60** [0.41, 0.76] and
  `P(guide < Alpha Vantage $3,158M, 11 Sep)` ≈ **0.47** [0.29, 0.65]. **Label every number guide or print.**
  Put the Zacks internal inconsistency on the exhibit ($14,226M quarterly sum vs $14,100M FY26).
- **Bucket words** are mapped through the ledger's own vocabulary with the measured ~4pp conservatism
  (4Q25 guided "mid-single digit" nights → printed +9.82%; 1Q26 "high-single digit" → +9.15%; bucket guides
  beaten 5/5 above the range). Emit `P(4Q26 nights bucket)`: "low double-digit" 0.55 / "high single-digit" 0.40
  / other 0.05, and the FY26 guide-raise probability (base rate: the FY guide has only ever been raised and the
  raise lands at the Q3 print, 2/2 ⇒ P ≈ 0.75).
- **Gate G4 is a SIGN test** against B5, target **≥8/14 on W1**. On level we currently **lose** to the free
  pre-guide Street (MAE 1.93% vs 1.61%; bias −1.23% vs −0.01%). **Write that in your note.** Hiding it is worse
  than losing it.
- **Deleted:** the revision regression (identity, max residual 4.6e-6 on 18 rows); the hierarchical
  159-statement pool (155 returned, 94 carry a cushion, `fillna(0.0)` fabricates 61); the −2.33% g/M cushion;
  the drift rule as an edge (report it only as a base rate with executable next-open returns, Fisher
  in-window p = 0.27, mean −4.21%).
- **Parameter count:** 1 cushion + 1 κ = 2, against 19 scoreable guides and 19 interval-censored guide ranges.

---

## Addendum — `fee-takerate`

You own the single de-gross-up step, the fee function, and `m_q`. Nobody else touches any of the three.

- **θ is UNIDENTIFIED and you say so in the first line of your note.** `12_reprice_summary.csv`:
  `mean_jump_pp` takes only half-integer values (bin midpoints: 11.5 in 65 rows, 12.5 in 13, 14.5 in 7,
  13.5 in 4, 17.5 in 4); `theta = mean_jump_pp / 13.8` exactly, ranging **0.833-1.407** over 402 rows and 34
  markets (0.833-0.845 is the **Austin** sub-sample); `excess_share_12_20` median **0.0029**, 90% below 0.01;
  `share_lt_m10` ≈ 0.255 > `share_gt_10` ≈ 0.178.
- **Carry the uplift as a range with the GBV sign correct:** θ=1 ⇒ GBV **+0.60%**, revenue **+4.03%**;
  θ=0.833 ⇒ GBV **−1.56%**, revenue **+1.81%**; 11.5pp modal ⇒ GBV **−2.28%**, revenue **+1.07%**. Central
  carried: **+1.1% to +1.8%**. +4.05% is quoted only as the θ=1 upper bound, always labelled.
- **The de-gross-up, in exactly one file, as an equation:**
  `H_{r,q} = ADR_reported_{r,q} / (1 + m_q · θ · 0.1479)`. Then
  `schedule(H, m, θ)` returns `(GBV, revenue)` **jointly, evaluated once**: split → `GBV = H/0.97 × 1.141`,
  `rev = H/0.97 × 0.171` (take 14.99%); single → `GBV = H/0.845`, `rev = H/0.845 × 0.155` (take 15.50%).
  **θ must be an explicit argument.** The ADR workbook's `+0.50pp fee-migration reprice` row and `take_bps` are
  the same event; both are deleted.
- **`m_q` is exogenous and dated, never fitted against GBV:** 0 / ~15 / ~25 / ~50% from `06_fee_timeline.csv`,
  then deadline-forced toward ~100% after **15 Sep 2026 (ex-EEA)** and **13 Oct 2026 (EEA + CH)**. Note in your
  README that the two deadlines are **not** in `06_fee_timeline.csv`. Publish both the listing-weighted and the
  **GBV-weighted** migrated share (professionals migrated first and are larger) and use the GBV-weighted one,
  Φ-weighted into the revenue quarter.
- **Compute `fee_step_4Q26 = uplift(θ) × migrated_GBV_share_Φweighted` and hand HALF of the central-θ value to
  `guidance-policy`, with the full range.** If the recomputed full step comes out materially below the ~+2.5%
  implied by the architect's $3,240M, say so — the print moves to $3,200-3,220M, the guide to $3,141-3,160M,
  and `P(guide < Zacks)` rises. **Do not force the number back.** Also report the delta against the FY27
  exhibit's **+0.9pp** line, which does not state whether it embeds the θ correction (§11.6).
- **DELETE the tax/cleaning de-rate.** `li_*` are counts of quotes containing the field (cleaning fee: 88 of
  1,707,390); and as coded it multiplies both fee legs identically, cancelling out of the ratio.
- **Direct-link pilot: 0-15bp of FY27 take rate.** Never −0.8pt (that needs 8.4% of all GBV at the 6% tier or
  14.5% at 10%; reserve it for a "pilot becomes policy" tail). Add the 15% hotel-credit expiry 31 Dec 2026.
- **Pre-register:** 3Q26 printed take rate **≥ 18.10%** = flowing, **≤ 17.88%** = fully offset; also publish
  `P(take rate ≥ 18.10%)` so the test's power is visible (the threshold sits 4bp below our central 18.14%).
  Printed take rate has not moved through 2Q26 (13.26% vs 13.17%, +9bp), and this is the one guide family
  Airbnb has missed — twice, both to the downside (3Q25 −0.69 vs guided 0.0; 1Q26 −0.10 vs "up slightly").
- **Take rate is an OUTPUT** (`Revenue_q / GBV_q`), never an input. So is ADR.

---

## Addendum — `l1-reconciliation`

Scope tonight is the **accounting spine only**: the constrained least-squares reconciliation. No state space.

- **Gate G2:** the constrained LS must reproduce **all 72** exact filed regional revenue cells **and** place
  every clean annual regional nights cell inside **±0.5M**. If it cannot, the disclosures are mutually
  inconsistent — **that is itself a reportable finding**, and you report it rather than relaxing the exact
  constraint.
- Softmax regional shares so `Σ_r n_r = N` **exactly** (reparameterise: K−1 free, the Kth solved). This retires
  `CALIB = −0.41pp` and the +0.19pp current-weighting index bias. `N = Σn_home + n_hotel + s_exp + s_svc`, so
  **seats/hotel dilution is an OUTPUT**. `ADR_blend = Σ_r w_r ADR_r`, so **geographic mix is an OUTPUT** — this
  closes the 1.13pp / ~$175M broken loop at `13_driver_model.py:377-379`.
- **Exclude every `basis == 'derived'` row** (the 14 NA/EMEA nights cells 4Q22-3Q24). Treat the 22 numeric
  LatAm/APAC cells and the 10-K Geographic Mix table as **intervals**, and the 68 ADR integers as ±0.5pp.
  Block bootstrap for intervals; no Stan.
- **You hand exactly one object to L2: `G_q`** — GBV in USD, booking-dated, one number per quarter. Nights,
  ADR, mix, size, LOS, seats and regulation do not cross the boundary.
- **You do NOT de-gross-up the fee migration.** State in your output file header whether you are handing host
  payout per night in `usd_constant` or reported ADR. `fee-takerate` applies the single de-gross-up.
- **Do not build:** the joint hedonic (use `06_wtp_hedonic_coefs.csv`; `06_quote_line_items.csv` is 76
  aggregate rows with no price/capacity/bedroom/LOS column); the 120-market panel; separate `q` and `m_sub`
  states (exactly collinear); a separate party-size driver (**party size IS the capacity index**); `reg_mult
  = 1.67` (deleted — regulation enters as a dated covariate on the nights state, not a subtraction from a
  growth rate already fitted on regulation-contaminated data); any "fix" to the `nb_incr` netting at
  `13_driver_model.py:437`.
- Carry the bedroom elasticity **0.23** (0.2289 on 12 markets, 0.2312 on 29): the "+12% Bedroom Nights vs +10%
  nights" wedge is worth **+0.46pp of ADR, not +2pp**. Report the +2.9pp price/sub-regional residual as an
  **unidentified 2-d ridge** — do not split it.
- The FY27 decomposition lines you own (§8.1) are **not rebuilt tonight**; they are carried as
  `basis = assumed` at the stated values. Say so.

---

## Addendum — `calibration-rail`

You are infrastructure and a referee, not a lens. Your deliverable is the answer to *"is the interval honest at
n ≈ 20?"* — which no workstream in this repo has ever answered.

- **Challenger bank:** B1 naive, B2 AR(1), B3 trailing-4, B4 guide + trailing-8 cushion, B5 vintage-stamped
  pre-guide Street; plus a monotone LightGBM with **≤4 features**. Score all of them on **both** W1 and W2.
- **Sign priors: `adr_fx_effect` ONLY** (`usd_broad → adr_fx_effect`, r −0.95, perm p 0.001). **Remove the
  nights constraint**: `usd_broad → nights_yoy` is effect **+0.2235** (positive), r 0.3179, spearman −0.0637,
  perm p **0.2657**, confidence **`none`**, `r_from2024` **−0.3954** (sign flips). And monotonicity is a shape
  restriction, **not** a leakage control — do not call it one.
- **Calibration:** PIT histogram over the W1 guide dates; CRPS; split conformal on the last 6-8 walk-forward
  residuals. **State that exchangeability is violated by construction** (trend, seasonality, autocorrelation,
  expanding window). At `n_cal = 6`, α = 0.2, the conformal quantile is the `ceil(7 × 0.8) = 6`th order
  statistic — the **maximum** of six residuals — so attainable coverage is **6/7 = 85.7%** and 80% is not
  targetable. Publish the attainable-coverage grid at the actual `n_cal`. Name a time-series variant
  (weighted/adaptive conformal, EnbPI) as the thing you are not doing, and why.
- **Pre-registered falsification:** the conformal band must achieve **70-90%** empirical coverage on held-out
  quarters. If it does not, report the posterior and state plainly that it is uncalibrated at n ≈ 12.
- **Ensemble weights are DECLARED JUDGEMENTAL with a sensitivity table.** Not NNLS dressed as learning — 5 free
  weights on ≤10 correlated points is the artefact it claims to replace. NNLS is admissible **only** on
  well-specified predictive distributions from structurally different models, never on point features (the
  three composite indexes that lost to AR(1) combined point features that individually lost to AR(1)).
- **Theo's "optimal mix of methods" is your deliverable**, and it is answered by the scoreboard plus a declared
  weighting with sensitivities — not by a fitted stack. Report which lens earned its weight and on which window.
- **Not built:** the hierarchical cushion model; the review store; the cross-border and LOS proxies; the
  repeat-listing hedonic. The 194-quote LLM annotation is a **descriptive** artefact keyed on `guide_id`,
  handed to `guidance-policy`, with **no fitted coefficient claimed**. Zero-shot foundation models, if run at
  all, are reported for **interval coverage only**, with the null (point accuracy ≈ AR(1)) pre-stated.
- Every correlation is reported with its permutation p-value. Nothing below the team's own Bonferroni-clean bar
  is built on.

---

## Addendum — `tracker-backlog`

**Run test T1 first. It takes twenty minutes and it decides whether the rest of your package exists.**

- **T1 (§3.1):** reconstruct `reported_q × (1 + d_q)` and `coverage_norm_Q × Revenue_{q+1}` for 3Q25-2Q26
  (`d_q` = 0.9 / 3.8 / 16.2 / 16.5%). Check specifically that `3175 = 0.880 × 3608` (2Q26 actual) and
  `3297 = 0.697 × 4730` (the 3Q26 **guide midpoint**). **If they agree to better than 0.5%, the restatement is
  circular: strike it as a pin, as a feature, and from every window and likelihood in every package.** Write
  that conclusion to disk before doing anything else.
- Also record the formula-versus-number discrepancy: the documents say `reported/(1 − d_q)` while the quoted
  numbers (+16.6% for 1Q26, +15.4% for 2Q26) come from `reported × (1 + d_q)` — verify both
  (`2733 × 1.162 / 2723 = +16.6%` vs `2733 / 0.838 / 2723 = +19.8%`). **Ruling: use `× (1 + d_q)`,
  `basis = derived`.**
- **`d_q`'s coverage norms are full-sample.** Any restated series used in a replay recomputes the norm
  expanding-window through T−1, and both versions are published side by side.
- **Gate G1 redefined:** passes only if a **non-circular** construction beats naive on revenue growth on
  **both** windows. **Expect failure and publish the negative** — the reported series fails on revenue
  (WF **1.17×** naive, **1.28×** AR(1)) while beating naive on **nights** (**0.90×**, AR(1) **0.65×**).
  The honest claim is: **"the backlog predicts volume, not dollars."**
- **Fallback, already authorised (§3.4):** the column-sum restriction; the raw series on a **volume** target
  only; the booking-curve Dirichlet capped at ≤4 quarters of weight and flagged as a **single Jul-Aug 2026
  vintage** (host blocks included, calendars carry no price, `median_min_nights` is a host **supply setting**,
  not stay length) — so the PIT replay runs **without** it, the full-sample replay **with** it, both published.
  State plainly that Φ is weaker for losing pin #1.
- `p` and `π` are restricted to **≤3 parameters each**, driven by dated RNPL / fee-migration shares plus a
  tight random walk — **never free per quarter**, or (A4)/(A5) are saturated and prove nothing. Show the
  residuals are non-zero **before** claiming over-identification. (A5) is dropped or labelled a restatement of
  (A3), since `Payouts_q` is imputed as `(1−τ)·Σφ·Ĝ`.
- **Emit** the `p` vs `π` diagnostic as a dated question for the 3Q26 10-Q: fee-denominated unearned fees
  **−0.9% y/y** against amount-denominated funds held **+10.5%**, on GBV **+15.7%**. And regress `d_q`
  (0.9 / 3.8 / 16.2 / 16.5) on disclosed single-fee penetration (0 / 15 / ~25 / ~50) and RNPL GBV share — if
  the distortion is the fee migration rather than RNPL, the backlog indicator repairs itself in 1Q27.
- **Never** use the reported unearned-fee series on a dollar target. **Never** use a restated value at a guide
  date if T1 fails: the 2Q26 restated figure is `0.697 × the 3Q26 guide midpoint`, i.e. the thing being
  forecast.
- Coverage figures for the memo: Q3-end unearned-fee coverage **0.661 / 0.668 / 0.655**, **0.599** in the RNPL
  era. The "85-90% on the ledger" claim is **struck** (that is the Q1-end figure).

---

*Research, not investment advice. Prices as of 9 Sep 2026 ($174.54); consensus vintage-stamped at every use.*
