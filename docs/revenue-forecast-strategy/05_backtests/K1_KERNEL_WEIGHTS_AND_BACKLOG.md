# K1 — the recognition kernel: actual lag weights, the paid backlog, the RNPL adjustment, and the conditional 3Q26 range

Run 2026-09-11. Package `analysis/src/forecast_methods/kernel_phi_v2/` (a **copy**, seeded
from `kernel_lambda/kernel.py` and `tracker_backlog/{common,rebuild}.py`; nothing in those
packages was read-modified). Tables in `data/processed/forecast_methods/kernel_phi_v2/`
(31 files, `00_manifest.csv`). Figure `F1_phi_by_season.png`. **No registry writes, no
`harness/score.py`, no git.**

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/kernel_phi_v2/run.py   # exit 0, ~35s
```

---

## 0. One page, plain language

**What the weights are.** Fit `Revenue_q = c_s × Σ_{k=0..4} φ_k GBV_{q-k}` with φ on the
simplex and a separate conversion `c_s` for each fiscal quarter. On the ex-COVID sample
(n=16) the answer is **φ = (0.37, 0.12, 0.46, 0.00, 0.05)**: about a third of a quarter's
revenue comes from GBV booked *inside* that quarter, and roughly 58% from the two prior
quarters. On the full sample (n=20) it is (0.36, 0.50, 0.14, 0.00, 0.00); on 2023Q1+
(n=14) it is (0.39, 0.04, 0.57, 0.00, 0.00). **φ₀ is materially positive in every window**
— confirming kernel-lambda's KL-3 failure at k≤3 and extending it to k≤4 — and the
implied mean lag is 0.77–1.25 quarters, shorter than the 1.33 the published 2/3–1/3
kernel implies. An independent plausibility check agrees: the pooled ex-COVID φ implies
$27.2bn of 2Q26 GBV eventually converts at **14.1%**, against the 13.2% LTM take rate,
while the published kernel implies **15.5%**, which is too high (`A5b`).

**Whether the split is identified: no.** φ₁ and φ₂ are not separately identified from
this series. The 95% block-bootstrap interval on φ₁ is [0.00, 0.72] and on φ₂ [0.00,
0.64] (ex-COVID), and their bootstrap correlation is **−0.48 to −0.90** across windows.
The sum φ₁+φ₂ is better pinned (0.584, CI [0.15, 0.87]) but still not tight. Twelve-quarter
rolling windows put φ₁ anywhere from 0.000 to 0.502 and φ₂ from 0.034 to 0.602 (`A4`).
**Quote the identified sum, φ₁+φ₂ ≈ 0.58–0.64, and refuse to quote the split.**
Season-specific φ_{s,k} is worse than unidentified — it is *saturated* (20 parameters on
16–20 observations) and its leave-one-out error is 2.10% against the pooled 1.61% (`A3`).
There is no evidence the kernel differs by season; there is not enough data to look.

**But the split that *forecasts* is not the split that *fits*.** Once you drop φ₀ — which
you must, because GBV_q is not known when the forecast is made — the point-in-time optimal
weight on GBV_{q-1} is **w ≈ 0.65–0.70**, i.e. the published 2/3 (`D3`). In sample the
series prefers φ₂; out of sample it prefers φ₁. That reversal is the single most useful
finding here: **the 2/3–1/3 kernel is a bad description of the recognition process and a
good forecasting rule, and those are not in conflict.**

**What share of next quarter is on the ledger.** Paid backlog = unearned fees + funds
payable. Splitting next-quarter revenue three ways (`B5`, pre-RNPL 2022–1H25 norms):

| quarter-end | paid, on the ledger | booked but unpaid | not yet booked |
|---|---|---|---|
| Q1 | 36.5% | 21.4% | 42.1% |
| Q2 | 41.5% | 23.5% | 35.0% |
| Q3 | 35.0% | 32.4% | 32.6% |
| Q4 | 30.3% | 27.4% | 42.3% |

So "the backlog covers two thirds of next quarter" is wrong twice over: the *booked* share
is 58–67% and the *paid* share is only 30–42%. The wedge between them (21–32 points) is
prepayment, not RNPL — it is there in 2022 — and its **level is not identified**; only its
change is.

**How RNPL moves it.** The unpaid share of the model fee stock is flat to within ±3% of
its seasonal norm from 1Q24 through 3Q25 and then breaks: **−3.7% (4Q25), −12.8% (1Q26),
−15.2% (2Q26)**, i.e. an *excess* unpaid share of **+2.0pp, +8.1pp, +9.7pp** (`B3`). That
is an independent construction, and it lands inside Theo's u = 6–16% and below the
verification note's 13–15%. Unearned-fee coverage of next-quarter revenue falls 12.7%
(1Q26) and 13.8% (2Q26, against the guide) below norm, against 3.9% for funds payable.
**Correction to the brief's premise:** the 3.3–3.6× asymmetry is real, but the FY2025 10-K
puts *both* fees in unearned fees and routes guest cash to funds payable *net of service
fees*, so the single-fee migration cannot be the cause and moves the ratio the wrong way;
funds payable, not unearned fees, is the confounded line (±8.7pt annual FX translation).
See §2.4.

**RNPL leakage.** Writing `Revenue_q = c_s × [φ-weighted GBV] × (1 − L_q)`, L = (RNPL share
of the live backlog) × (incremental cancellation propensity) = **0.17% to 1.39%** across
16.7–23.1% share and +1 to +6pp propensity. That takes λ_Q3 from 17.239% to 17.00–17.21%
and λ_Q4 from 12.030% to 11.86–12.01%: **$8M to $67M off 3Q26 revenue**. 1H26 does not
show it — 1Q26 λ = 12.612 against a season mean of 12.721 (−0.85%) and 2Q26 λ = 13.736
against 13.706 (+0.22%), both comfortably inside their 80% bands.

**The 3Q26 conditional range, ledger only.** Conditioning on the printed GBV_2Q26 = $27,200M
and GBV_1Q26 = $29,200M, the expanding-window point-in-time model gives **$4,795M**, 50%
interval **$4,736–4,857M**, 80% interval **$4,683–4,914M** (`D6`), 1.4% above the $4,730M
guide midpoint. **GBV_3Q26 from the ledger alone: central $26.4–26.6bn, 80% band
$25.7–27.5bn** (`D9`). 4Q26 at GBV_3Q26 = $26,300M is **$3,181M** [q10 3,107, q90 3,260]
(`D7`). **The reviews/calendar alt-data nowcast (Krish's Q3 nowcast) is a separate route
and is not used anywhere in this note.**

---

## 1. (A) The actual weights

### 1.1 Specification and samples

`Revenue_q = c_{s(q)} × Σ_{k=0..4} φ_{g(q),k} × GBV_{q-k}`, φ ≥ 0, Σφ = 1 (softmax →
simplex), fitted on **relative** errors. `c_s` is always season-specific (4 parameters).
The φ group `g` is the treatment variable:

* **pooled** — one φ (4 free weights): 8 parameters
* **season** — one φ per fiscal quarter (16 free weights): 20 parameters
* **summer** — one φ for Q3, one for Q1/Q2/Q4 (8 free): 12 parameters

Requiring five lags costs four observations at the start: the usable panel is **3Q21–2Q26,
n = 20**. The ex-COVID rule (|nights y/y| > 25% dropped) removes **3Q21, 4Q21, 1Q22, 3Q22**,
leaving n = 16. The 2023Q1+ window has n = 14.

*Machinery validated:* at k ≤ 3 the pooled fit reproduces kernel-lambda's published
φ vectors to three decimals on all three of its windows (0.225/0.604/0.172/0.000;
0.405/0.179/0.360/0.056; 0.390/0.041/0.569/0.000). The extension to k = 4 and to grouped φ
is the only new code.

### 1.2 Point estimates (`A1_phi_estimates.csv`)

| sample | spec | n | params | φ₀ | φ₁ | φ₂ | φ₃ | φ₄ | φ₁+φ₂ | mean lag (q) | in-sample rel-RMSE | LOO rel-RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| full 2021Q3+ | pooled | 20 | 8 | 0.363 | 0.502 | 0.135 | 0.000 | 0.000 | 0.637 | 0.77 | 1.21% | 2.89% |
| full 2021Q3+ | **2/3–1/3 fixed** | 20 | 4 | 0 | 0.667 | 0.333 | 0 | 0 | 1.000 | 1.33 | 1.87% | **2.33%** |
| full 2021Q3+ | λ only (φ₁=1) | 20 | 4 | 0 | 1.000 | 0 | 0 | 0 | 1.000 | 1.00 | 2.17% | 2.71% |
| **ex-COVID** | **pooled** | 16 | 8 | **0.365** | **0.119** | **0.464** | 0.002 | 0.049 | **0.584** | **1.25** | **0.88%** | **1.61%** |
| ex-COVID | 2/3–1/3 fixed | 16 | 4 | 0 | 0.667 | 0.333 | 0 | 0 | 1.000 | 1.33 | 1.33% | 1.75% |
| ex-COVID | λ only | 16 | 4 | 0 | 1.000 | 0 | 0 | 0 | 1.000 | 1.00 | 1.68% | 2.21% |
| 2023Q1+ | pooled | 14 | 8 | 0.390 | 0.041 | 0.569 | 0.000 | 0.000 | 0.610 | 1.18 | 0.75% | 1.31% |
| 2023Q1+ | 2/3–1/3 fixed | 14 | 4 | 0 | 0.667 | 0.333 | 0 | 0 | 1.000 | 1.33 | 1.36% | 1.83% |

Season-specific and summer-vs-rest, ex-COVID (`A1`, and the right panel of `F1`):

| spec | Q1 φ | Q2 φ | Q3 φ | Q4 φ | LOO |
|---|---|---|---|---|---|
| season (20 params, n=16) | (.35,.00,.65,.00,.00) | (.33,.12,.51,.00,.04) | (.39,.00,.62,.00,.00) | (.01,.30,.24,.12,.33) | **2.10%** |
| summer vs rest (12 params) | rest (.39,.10,.40,.03,.08) | rest | Q3 (.39,.00,.62,.00,.00) | rest | 1.81% |
| pooled (8 params) | — one φ — | | | | **1.61%** |

**Reading.** Season-specific φ is saturated: 20 parameters on 16 observations gives the
best in-sample fit (0.68%) and the *worst* out-of-sample error of any spec (2.10%, and
2.18% on 2023Q1+). Its Q4 vector, with 0.33 on φ₄, is a boundary artefact of four Q4 cells
having to identify four free weights. **There is no usable evidence that the kernel differs
by season, and this sample cannot look for one.** The summer-vs-rest restriction is also
beaten by the pooled fit out of sample. **The pooled φ with season-specific `c_s` is the
only version of this model the data support**, which is exactly the programme's existing
architecture.

### 1.3 LOO horse race (`A3_loo_comparison.csv`)

Ratios of leave-one-quarter-out relative RMSE:

| sample | pooled φ | season φ | summer φ | λ-only |
|---|---|---|---|---|
| vs **fixed 2/3–1/3 kernel** | full 1.24 / **ex-COVID 0.92** / 2023+ **0.72** | 2.05 / 1.20 / 1.19 | 1.40 / 1.03 / 0.91 | 1.16 / 1.26 / 1.33 |
| vs **λ-only** | 1.07 / 0.73 / 0.54 | 1.77 / 0.95 / 0.90 | 1.20 / 0.82 / 0.69 | — |

The free φ beats the fixed kernel out of sample on the two post-COVID samples (0.92, 0.72)
and **loses on the full sample (1.24)**. This is a change from kernel-lambda's k ≤ 3 result
(free won all three windows there) and it is the extra lag doing it: with five weights and
20 collinear observations the free fit over-reaches on the COVID quarters. Both the fixed
kernel and λ-only have essentially zero LOO bias (+0.02 to +0.06%) while the free fits are
noisier. Report the free φ as a **description of recognition**, not as the forecasting
object.

### 1.4 Is φ₁ separable from φ₂? No. (`A6_identification.csv`, `A7`)

400 moving-block bootstrap draws, block 4, drawn samples rejected unless all four seasons
appear at least twice.

| sample | φ₁ point | φ₁ 95% CI | φ₂ point | φ₂ 95% CI | φ₁+φ₂ | sum 95% CI | **corr(φ₁,φ₂)** |
|---|---|---|---|---|---|---|---|
| full 2021Q3+ | 0.502 | [0.00, 0.58] | 0.135 | [0.03, 0.57] | 0.637 | [0.29, 0.75] | **−0.78** |
| ex-COVID | 0.119 | [0.00, 0.72] | 0.464 | [0.00, 0.64] | 0.584 | [0.15, 0.87] | **−0.48** |
| 2023Q1+ | 0.041 | [0.00, 0.65] | 0.569 | [0.00, 0.71] | 0.610 | [0.08, 0.89] | **−0.47** |
| ex-COVID, Q3-only φ (summer spec) | 0.000 | [0.00, 1.00] | 0.615 | [0.00, 0.84] | 0.615 | [0.57, 1.00] | **−0.90** |

The φ₁/φ₂ bootstrap correlation runs −0.47 to −0.90 and each individual CI covers most of
the unit interval. The sum's CI is narrower than the components' **only on the full sample**
(width 0.47 against φ₁'s 0.58); on ex-COVID it is the same width (0.72 against 0.72) and on
2023Q1+ it is *wider* (0.81 against 0.65). So even the identified sum is only loosely pinned,
and the honest summary is that the two-lag block as a whole is known to roughly ±0.2 and its
internal split not at all. Holding φ₀ and the
tail fixed and sweeping the split (`A7`), LOO runs from 1.176% at w = 0.20 to 1.788% at
w = 1.00 — a real but shallow gradient, on a criterion that (see §1.6) points the *opposite*
way from the forecasting criterion.

> **Verdict: the φ₁ : φ₂ split is unidentified from this series alone at n = 14–20.
> The identified quantity is φ₁ + φ₂ = 0.58–0.64, and φ₀ ≈ 0.36–0.39. Any statement of
> the form "x% of next quarter's revenue is already booked" should be made from the sum;
> any statement about *which* prior quarter it came from should not be made at all.**

### 1.5 Drift (`A4_rolling_windows.csv`)

Twelve-quarter rolling pooled fits:

| window ending | φ₀ | φ₁ | φ₂ | φ₁+φ₂ | c_Q3 | c_Q4 |
|---|---|---|---|---|---|---|
| 2Q24 | 0.530 | 0.370 | 0.034 | 0.404 | 18.30 | 13.47 |
| 4Q24 | 0.370 | 0.456 | 0.081 | 0.537 | 18.11 | 13.13 |
| 2Q25 | 0.548 | 0.125 | 0.247 | 0.372 | 18.09 | 13.28 |
| 4Q25 | 0.399 | 0.022 | 0.579 | 0.601 | 17.24 | 12.54 |
| 2Q26 | 0.398 | 0.000 | 0.602 | 0.602 | 17.22 | 12.53 |

φ₀ is the only stable feature (0.34–0.55). φ₁ and φ₂ trade places. Expanding windows are
tamer (φ₀ 0.36–0.55, φ₁ 0.35–0.50) but show the same swap after 3Q25. **What has genuinely
drifted is `c_s`, not φ**: c_Q3 falls from 18.30 to 17.22 and c_Q4 from 13.47 to 12.53 across the
rolling windows (not monotonically — the path is 18.30, 17.47, 18.11, 18.35, 18.09, 17.86,
17.24, 17.37, 17.22), which is the same downward conversion drift the λ table
shows and is the number that matters for dollars.

### 1.6 What "the weight of GBV from each quarter on later quarters" means, in dollars

Operationally: `revenue contribution of GBV_b to quarter b+k = c_{s(b+k)} × φ_k × GBV_b`.
For the printed **GBV_2Q26 = $27,200M** (`A5_dollar_map_2q26_gbv.csv`, 95% CI from the same
400 bootstrap draws, jointly on φ and c):

| lands in | k | pooled ex-COVID φ_k | c_s | **$M** | 80% band | 95% band |
|---|---|---|---|---|---|---|
| 2Q26 itself | 0 | 0.365 | 14.89% | **1,479** | 621 – 2,171 | 0 – 2,736 |
| **3Q26** | 1 | 0.119 | 17.48% | **568** | 0 – 1,643 | 0 – 3,512 |
| **4Q26** | 2 | 0.464 | 12.63% | **1,596** | 462 – 2,011 | 0 – 2,153 |
| 1Q27 | 3 | 0.002 | 10.67% | **6** | 0 – 52 | 0 – 443 |
| 2Q27 | 4 | 0.049 | 14.89% | **198** | 0 – 749 | 0 – 1,040 |
| **total lifetime** | | | | **3,847** | | (= 14.1% of GBV) |

The same map under the published 2/3–1/3 kernel: 3Q26 **$3,126M**, 4Q26 **$1,086M**,
everything else zero, lifetime $4,212M = 15.5% of GBV.

Two things must be said together. First, **the intervals swallow the point estimates**: the
95% band on 2Q26 GBV's contribution to 3Q26 runs from $0 to $3.5bn. That is the
identification failure in dollars, and it is why the estimated φ must never be used to make
a per-quarter carry-forward claim. Second, **the lifetime total is well behaved and is the
better plausibility check**: 14.1% against the 13.2% LTM take rate for the estimated φ,
15.5% for the published kernel. The published kernel loads all the weight on the two
highest-conversion quarters and therefore over-monetises a booking cohort by ~2.3 points
of GBV; the estimated φ, with its large φ₀ on the low-conversion booking quarter, does not.

**And the operationally useful version of the same question, at the guide date, is not this
map.** It is: given that GBV_{q-1} and GBV_{q-2} are printed and GBV_q is not, what mix of
the two printed quarters forecasts revenue_q best? That is §4.2, and the answer is w ≈ 2/3.

---

## 2. (B) Backlog conversion

### 2.1 Definitions (from the filings, as quoted in `03_insider_mechanics.md` §1.1/§1.3 and `docs/rnpl-short-audit/04_balance-sheet-verification.md` §C2)

* **Unearned fees** — "Service fees collected from customers prior to check-in are recorded
  as unearned fees on the consolidated balance sheets… not considered contract balances, as
  they are subject to refund in the event of a cancellation." FY2025 10-K Note 2: "**Host
  and guest fees are recorded as cash with a corresponding amount in unearned fees.**"
  Fee-denominated; it is the already-collected part of *future revenue*.
* **Funds payable** — "The Company records guest payments, **net of service fees**, as funds
  receivable and amounts held on behalf of customers with a corresponding amount in funds
  payable… when cash is received in advance of check-in." Booking-amount denominated, the
  host's share held. Funds receivable ≡ funds payable on the face of the balance sheet, so
  only the level informs.
* **PAID BACKLOG ≡ unearned fees + funds payable.**
* The circular `unearned_fees_restated = reported/(1−d_q)` series is **not built, read or
  used anywhere in this package** (struck by tracker-backlog T1; it is identically
  `coverage_norm × next-quarter revenue`, and its 2Q26 value is a function of the 3Q26
  guide).

### 2.2 Coverage and its pre-RNPL seasonal norms (`B1`, `B2`)

Coverage = balance at quarter-end ÷ next-quarter revenue. Norms are the **2022Q1–2025Q2**
(pre-RNPL) means.

| quarter-end | UF cover norm | FP cover norm | paid-backlog cover norm | n |
|---|---|---|---|---|
| Q1 | 0.868 | 3.042 | 3.910 | 4 |
| Q2 | 0.694 | 2.689 | 3.383 | 4 |
| Q3 | 0.657 | 2.625 | 3.282 | 3 |
| Q4 | 0.676 | 2.661 | 3.336 | 3 |

The UF norms reproduce the binding-decision numbers (Q1 0.880, Q2 0.697, Q3 0.661, Q4 0.676)
to within 0.013 — the difference is the 2022 quarters this window includes and the
2023–25 window does not.

Actuals against norm, RNPL era (`B3_coverage_deviations.csv`):

| quarter-end | UF cover | vs norm | FP cover | vs norm | paid backlog | vs norm |
|---|---|---|---|---|---|---|
| 3Q25 | 0.655 | −0.3% | 2.595 | −1.2% | 3.250 | −1.0% |
| 4Q25 | 0.651 | **−3.7%** | 2.599 | −2.3% | 3.249 | −2.6% |
| 1Q26 | 0.757 | **−12.7%** | 2.924 | −3.9% | 3.682 | −5.8% |
| 2Q26 † | 0.599 | **−13.8%** | 2.584 | −3.9% | 3.183 | −5.9% |

† against the **3Q26 guide midpoint $4,730M, not a print**. The 0.599 reproduces the insider
note's "59.9% pre-funded versus a 69.7% Q2-end norm".

So RNPL pushes coverage down from 4Q25, and it does so **3.3–3.6× harder on unearned fees than
on funds payable**, exactly as the asymmetry argument predicts: funds payable is
booking-amount denominated (~87% of GBV) and only RNPL defers it; unearned fees are
fee-denominated (~13–15% of GBV) and the same deferred dollar is a much larger fraction of
the smaller stock.

### 2.3 The share of next-quarter revenue that is on the ledger (`B5`)

Coverage is a stock-over-flow ratio, not a share: unearned fees at quarter-end also cover
check-ins in q+2 and beyond. To get the share, allocate the fee stock using the kernel's own
release schedule — of the fees standing at the end of q, the piece checking in during q+i is
`Σ_j φ_{j+i} GBV_{q-j}`, monetised at `c_{s(q+i)}`. That gives an allocation factor of
0.42–0.60 depending on season, and:

**P (paid, on the ledger) + W (booked but unpaid) + φ₀-piece (not yet booked) = 1**

| quarter-end | paid on ledger | booked but unpaid | not yet booked | booked total |
|---|---|---|---|---|
| Q1 (norm) | 0.365 | 0.214 | 0.421 | 0.579 |
| Q2 (norm) | 0.415 | 0.235 | 0.350 | 0.650 |
| Q3 (norm) | 0.350 | 0.324 | 0.326 | 0.674 |
| Q4 (norm) | 0.303 | 0.274 | 0.423 | 0.577 |
| **2Q26 (live, vs guide mid)** | **0.360** | **0.305** | **0.336** | **0.664** |

### 2.4 Reconciling with (A)'s φ₁+φ₂ — the wedge, and what it is

φ₁+φ₂ = 0.584 is a *φ-weighted* quantity; the booked share above is the same φ applied to
actual GBV levels, so it varies 0.577–0.674 by season while the weights do not. The two
objects are **not** the same thing, and the gap is the point:

* **φ₁+φ₂ (booked share, 58–67%)** counts revenue whose *booking* has happened. It is a
  volume statement.
* **UF coverage × allocation (paid share, 30–42%)** counts revenue whose *fee cash* has
  arrived. It is a cash statement.
* **The wedge W = 21–32 points** is bookings on the books whose fee has not been collected.

**The wedge's level is not identified and must not be read as RNPL.** It is 21–32 points in
2022, three years before RNPL existed. Two things are confounded inside it: genuine partial
prepayment (Pay Less Upfront, host-fee collection timing) and the fact that the kernel's φ
tail is a collinearity artefact that overstates the live backlog. The pooled ex-COVID φ
implies a fee stock of $5,230M at 30 June 2026 against reported unearned fees of $2,831M —
a 54% prepaid share — and neither the numerator's true prepayment rate nor the denominator's
true dwell time can be recovered separately from public data. **What is identified is the
change.** The unpaid share of the model fee stock, against its own pre-RNPL seasonal norm:

| quarter-end | unpaid share of fee stock | pre-RNPL norm | **excess** |
|---|---|---|---|
| 1Q24 – 2Q25 (six quarters) | — | — | **−1.5 to +0.1pp** |
| 3Q25 | 0.477 | 0.481 | **−0.3pp** |
| 4Q25 | 0.495 | 0.475 | **+2.0pp** |
| 1Q26 | 0.450 | 0.370 | **+8.1pp** |
| 2Q26 | 0.459 | 0.362 | **+9.7pp** |

The series is flat to within 1.5pp for six pre-RNPL quarters and then breaks in exactly the order
the rollout dates imply (US launch 3Q25, negligible; single fee + policy redesign 4Q25,
+2pp; global RNPL 17 Feb 2026, +8pp; full quarter of global RNPL, +10pp). **This is an
independent estimate of Theo's `u` built from the kernel rather than from the two-line
joint solve, and it lands inside his 6–16% range** and just below the verification note's
13.0%/15.1% medians at B = 1.00. It needs no `m` term, which is the term the verification
showed is not identified.

**Attribution of the 2Q26 wedge (30.5 points of 3Q26 revenue at the guide mid):**
~23.5 points is the pre-RNPL Q2 norm (prepayment structure and the φ-tail artefact) and
~7.0 points is the RNPL excess. The remaining 33.6 points of 3Q26 revenue is the φ₀ piece:
bookings that had not been made on 30 June.

### 2.5 The migration confound — the brief's premise is backwards

The brief asks to show "how the single-fee migration confounds unearned fees but not funds
payable." **That attribution is refuted by the filings and I will not reproduce it.**
`docs/rnpl-short-audit/04_balance-sheet-verification.md` §C2 establishes, verbatim from the
FY2025 10-K, that (i) *both* host and guest fees are recorded in unearned fees, so moving to
a host-only fee does not remove anything from that line — it moves the ratio UF/FP *up*
3–4%, the wrong sign, while the observed move is *down* 8–13%; (ii) guest payments always
entered funds payable *net* of service fees, under both fee structures; (iii) the 2Q26 10-Q
never mentions the fee structure and attributes the shortfall to "the increased guest
adoption of our flexible payment options"; and (iv) unearned fees reconciles to the
cash-flow statement within $3–8M for six quarters, while **funds payable carries a ±8.7-point
annual FX translation swing** (+$627M in FY25 on a $7.2bn base; 4Q25 funds payable is +17.3%
reported but +6.8% ex-FX, i.e. it lagged GBV by 9–14 points, *worse* than unearned fees).

**Corrected statement: unearned fees is the FX-clean, migration-neutral line; funds payable
is the confounded one.** My table 2.2 is consistent with this: the paid-backlog coverage
(dominated by funds payable) shows only a 5.9% break where unearned fees shows 13.8%, and
part of even that 5.9% is FX. Anyone scoring funds payable on 5 November must first subtract
(Δbalance − the financing-activities "Change in funds payable") to strip translation.

---

## 3. (C) The RNPL adjustment to the kernel

### 3.1 The form of the adjustment

`Revenue_q = c_s × [φ-weighted GBV]_q × (1 − L_q)`

Two disclosed facts fix the shape. GBV is booking-dated and "net of cancellations and
alterations **that occurred during that period**" (FY2025 10-K KPI definition), so a booking
made in q−1 and cancelled in q reduces **GBV_q**, not GBV_{q−1} — it is a pure leak out of
the kernel base in the recognition quarter, and it is only partly returned one quarter later
when the negative lands in GBV_q and is carried forward at φ₁. And RNPL payment falls due
"shortly before the end of the listing's free cancellation period" (ledger D002), i.e. days
before check-in, so essentially the whole excess-cancellation risk on a carried RNPL booking
is still ahead of it at the start of the recognition quarter. Hence `L_q ≈ s_backlog × Δc`.

### 3.2 The leakage grid (`C3_leakage_grid.csv`)

λ_Q3 = 17.239% and λ_Q4 = 12.030% are the 2023–2025 season means on the published
2/3–1/3 base (they reproduce kernel-lambda's table exactly: 17.391/17.145/17.182 and
11.946/12.117/12.026). 3Q26 base = ⅔(27,200) + ⅓(29,200) = 27,866.7.

| RNPL share of the live backlog | Δc = +1pt | +2pt | +4pt (D central) | +6pt (mgmt-implied) |
|---|---|---|---|---|
| **L**, at 16.7% (nights share) | 0.17% | 0.33% | 0.67% | 1.00% |
| **L**, at 21% (GBV share) | 0.21% | 0.42% | 0.84% | 1.26% |
| **L**, at 23.1% (backlog share, 1.5× dwell) | 0.23% | 0.46% | 0.92% | **1.39%** |
| λ_Q3 2026 at 21% share | 17.203 | 17.167 | 17.095 | 17.022 |
| λ_Q4 2026 at 21% share | 12.005 | 11.979 | 11.929 | 11.878 |
| 3Q26 revenue drop, $M, at 21% | −10 | −20 | −40 | −61 |

**Full range: L = 0.17% to 1.39%, λ_Q3 17.00–17.21% (−0.03 to −0.24pp), λ_Q4 11.86–12.01%
(−0.02 to −0.17pp), 3Q26 revenue −$8M to −$67M.** For scale, the D1 cohort engine's nights-side
answer over 2,025 cells is −0.10 to −1.37 growth points in 3Q26 and −0.08 to −1.36 in 4Q26,
central cell −0.62/−0.57 (`C6`). The dollar-side leakage here is the same order of magnitude
as the nights-side drag, which is the consistency check.

### 3.3 Does 1H26 already show it? (`C4_1h26_lambda_check.csv`) — No.

Bands are 4,000 draws: bootstrap the three-cell season mean, then add one draw of the pooled
relative dispersion (σ = 1.77%, 2023Q1–2025Q4).

| | λ actual | season mean 2023–25 | dev | 80% band | 95% band | inside 80%? | implied L | RNPL share of feeding GBV | implied Δc |
|---|---|---|---|---|---|---|---|---|---|
| **1Q26** | 12.612 | 12.721 | −0.109pp (−0.85%) | 12.35 – 13.08 | 12.15 – 13.27 | **yes** | +0.85% | 9.7% | +8.8pp |
| **2Q26** | 13.736 | 13.706 | +0.030pp (+0.22%) | 13.36 – 14.04 | 13.19 – 14.24 | **yes** | −0.22% | 17.3% | −1.3pp |

Both sit comfortably inside their 80% bands and they point in *opposite* directions. The
1Q26 shortfall would require Δc = +8.8pp — above management's own implied +6pp — and the
2Q26 print requires Δc < 0. **The lambda series does not yet contain a detectable RNPL
cancellation signal.** The most that can be said is an upper bound: if L were as large as
the +6pp/23.1% cell (1.39%), 2Q26's λ would have printed near 13.52 rather than 13.74.

Note that the "RNPL share of feeding GBV" column mixes provenance: 3Q25 (5%) and 4Q25 (12%)
are the **tracker-backlog researcher ramp with no disclosure of any kind behind them**; 1Q26
(20%) is management's own floor (D031); 2Q26 (22%) is a researcher point pick inside the
">20%" floor (D043). The 1Q26 row therefore rests on two undisclosed numbers.

### 3.4 The 5 November control-chart rule (`C5_control_chart_5nov.csv`)

At 5 November both GBV lags are printed, so `λ_Q3 = Revenue_3Q26 / 27,866.7` is an
**identity on the print**, not a forecast. Centre 17.239%.

| σ basis | rule | λ lower limit | revenue lower limit | implied L | implied Δc at 21% share |
|---|---|---|---|---|---|
| **Q3's own sd** (n=3, 0.132pp; one-draw se 0.153pp) | 1σ | 17.086 | **$4,761M** | 0.89% | **+4.2pp** |
| | 2σ | 16.934 | **$4,719M** | 1.77% | **+8.4pp** |
| pooled σ (all seasons, 1.77%; se 0.352pp) | 1σ | 16.888 | $4,706M | 2.04% | +9.7pp |
| | 2σ | 16.536 | $4,608M | 4.08% | +19.4pp |

**The rule.** Score the *print*, not the guide.

> **Primary:** compute λ_Q3 = printed 3Q26 revenue ÷ 27,866.7.
> * **λ ≥ 17.09% (revenue ≥ $4,761M)** — no leakage signal. Δc is below the D central cell.
> * **16.93% ≤ λ < 17.09% ($4,719–4,761M)** — a 1σ break on Q3's own dispersion, consistent
>   with the D central +4pp cell. **Warning, not confirmation** (n = 3 cells behind the σ).
> * **λ < 16.93% (revenue < $4,719M)** — a 2σ break implying L ≥ 1.77% and Δc ≥ +8.4pp,
>   above management's own implied +6pp. Escalate.

Three honesty conditions on that rule, all of which must be carried with it:

1. **The σ is built on three cells.** The Q3-own-sd chart is the tight one and the pooled-σ
   chart is 2.3× wider; a reading between $4,608M and $4,761M is a signal on one chart and
   noise on the other. Quote both.
2. **λ cannot separate cancellation from in-quarter booking weakness.** A λ miss is equally
   consistent with a weak φ₀ (fewer bookings made in July–September for July–September
   check-in) as with RNPL cancellations of carried bookings. It is a *composite* control
   chart.
3. **The discriminating cross-check is the unearned-fees line, conditioned on GBV.** Per the
   corrected rule in `04_balance-sheet-verification.md` §C4: score
   **(3Q26 unearned fees y/y) − (3Q26 GBV y/y)** — at or below −18pts the unpaid book is at
   or above the 1H26 run-rate; −12 to −18pts is in line with 1H26; wider than −8pts weakens
   the drag. A λ miss *with* the UF gap inside −12pts is a booking-flow story, not a
   cancellation story.

---

## 4. (D) The unknown part and the conditional range

### 4.1 Defining carried and R (`D0`, `D1`)

`carried_q = c_{s(q)} × [φ₁ GBV_{q-1} + φ₂ GBV_{q-2}]`, `R_q = revenue_q − carried_q`.
Because any positive rescaling of `carried` is absorbed one-for-one by the ratio
`k = R/carried`, **the only thing in this definition that affects a forecast is the split
w = φ₁/(φ₁+φ₂)**. Both scalings below use the pooled ex-COVID φ₁+φ₂ = 0.584 and its `c_s`.

R as a share of revenue, 2022Q1+ (`D1_residual_R_by_season.csv`):

| | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| **estimated split (w = 0.204)** | 48.4% ± 1.9 | 47.1% ± 0.9 | 39.1% ± 0.6 | 37.0% ± 1.2 |
| **published split (w = 2/3)** | 51.2% ± 1.2 | 36.7% ± 0.9 | 40.5% ± 0.7 | 38.5% ± 0.6 |
| R y/y growth, mean (sd), w=2/3 | +14.7 (9.5) | +14.3 (5.7) | +14.4 (6.9) | +14.9 (3.2) |
| revenue y/y, mean | +26.5 | +23.1 | +16.6 | +16.1 |

**The "unknown third" is really an unknown 37–51%, and it is extraordinarily stable.** Its
seasonal share has a standard deviation of 0.6–1.9 points over five years. It grows at
+14 to +15% a year in every season with a standard deviation of 3–10 points — i.e. R behaves
like a scaled copy of revenue, not like a residual.

### 4.2 What explains R point-in-time (`D2`, `D4`)

Season-demeaned in-sample correlation of `k` with each candidate (2022Q1+, n = 18), at the
w = 2/3 definition:

| regressor | PIT? | corr | t | R² |
|---|---|---|---|---|
| funds payable y/y at q−1 | yes | +0.51 | 2.39 | 0.26 |
| paid-backlog y/y at q−1 | yes | +0.49 | 2.25 | 0.24 |
| unearned fees y/y at q−1 | yes | +0.42 | 1.83 | 0.17 |
| prior-quarter GBV y/y | yes | +0.36 | 1.54 | 0.13 |
| prior-quarter GBV y/y acceleration | yes | +0.30 | 1.25 | 0.09 |
| nights y/y at q−1 | yes | +0.30 | 1.24 | 0.09 |
| summer (Q3) dummy | yes | 0.00 | — | 0.00 (absorbed by the season means) |
| **φ₀ in-quarter share** | **no** | +0.05 | 0.22 | **0.00** |

Everything that works is a momentum variable and they are all the same variable: the
quarter's own growth rate. The summer dummy is exactly zero because season means already
carry it. **The model-implied φ₀ in-quarter share explains nothing** (R² = 0.003) — which
is itself informative: the in-quarter piece is proportional to the rest, not an independent
driver, and it is in any case not point-in-time.

Expanding-window PIT replay (refit `c`/`k` at every guide date; scored on W1 targets 2023Q1+
and W2 targets 2024Q1+; n is 12 and 10 rather than 14 and 10 because five lags plus a
four-season training requirement cost the two 1H23 origins):

| training window | feature | W1 RMSE | W1 bias | ratio vs season mean | W2 RMSE | W2 bias | ratio |
|---|---|---|---|---|---|---|---|
| ex-COVID | season mean only | 1.898% | +0.605 | 1.000 | 2.032% | +0.541 | 1.000 |
| **ex-COVID** | **prior-quarter GBV y/y** | **1.813%** | **+0.173** | **0.955** | **1.964%** | **+0.261** | **0.966** |
| ex-COVID | unearned fees y/y | 1.807% | +0.150 | 0.952 | 1.964% | +0.211 | 0.966 |
| ex-COVID | paid-backlog y/y | 1.838% | −0.020 | 0.968 | 1.999% | −0.011 | 0.984 |
| ex-COVID | nights y/y | 1.815% | +0.207 | 0.956 | 1.970% | +0.280 | 0.969 |
| all history | season mean only | 2.014% | +0.945 | — | 2.162% | +0.949 | — |

**Honest reading: the observables buy 3–5% of RMSE and most of the bias.** No feature is a
signal; they are all the same momentum term and they mostly correct the upward drift that
comes from estimating a season mean on a growing series. The chosen object is
**ex-COVID training + prior-quarter GBV y/y**, on the grounds that GBV y/y is the cleanest
of the near-identical set and is the one variable with no balance-sheet confound.

### 4.3 The carried weight, point-in-time (`D3_carried_weight_pit_sweep.csv`)

Sweeping w with everything else refit at each guide date, ex-COVID training:

| w | 0.00 | 0.20 | 0.30 | 0.50 | 0.60 | **0.65** | **0.70** | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|---|
| W1 RMSE % | 6.42 | 4.54 | 3.70 | 2.37 | 1.99 | **1.906** | **1.909** | 2.14 | 2.58 | 3.12 |
| W2 RMSE % | 4.96 | 3.65 | 3.10 | 2.28 | 2.08 | **2.036** | 2.04 | 2.17 | 2.42 | 2.76 |
| W1 bias % | +2.96 | +2.11 | +1.74 | +1.08 | +0.79 | +0.65 | +0.52 | +0.27 | +0.04 | −0.17 |

**The point-in-time optimum is w = 0.65–0.70 on both windows, and 2/3 sits on it.** The +5%
flat band is roughly [0.58, 0.78]. Contrast this with §1.4, where the in-sample and LOO
criteria minimise at w ≈ 0.20. The two criteria disagree because the LOO criterion in (A)
uses GBV_q, which a forecaster does not have. **When φ₀ has to be replaced by a seasonal
constant — which is what any real forecast does — the weight on the most recent printed
quarter must rise, because that quarter is the best available proxy for the in-quarter
bookings you cannot see.** This is, as far as I can tell, the resolution of the whole
2/3-versus-0.33 argument in kernel-lambda: the 0.33 camp is reading an in-sample criterion,
the 2/3 camp a forecasting one, and both are right about their own objective.

### 4.4 The conditional 3Q26 distribution (`D6_live_3q26_conditional.csv`)

Conditioning on the printed **GBV_2Q26 = $27,200M** and **GBV_1Q26 = $29,200M**, at
w = 2/3, ex-COVID training, GBV-momentum feature, with the predictive distribution taken
from the 12 point-in-time replay errors (bias +0.173%, sd 1.885%):

| | $M |
|---|---|
| carried (c_Q3 × 0.584 × 27,866.7) | 2,844 |
| k (Q3 season mean + momentum) | 0.689 |
| **point (bias-corrected)** | **4,795** |
| 50% interval (q25–q75) | **4,736 – 4,857** |
| 80% interval (q10–q90) | **4,683 – 4,914** |
| memo: 3Q26 guide midpoint | 4,730 |
| memo: implied λ_Q3 at the point | 17.21% |

The point is 1.4% above the guide midpoint and 0.2% below kernel-lambda's independently
constructed $4,804M; the 80% band is 18% wider ($231M against $196M) because this object
carries the residual-model estimation error as well as the conversion dispersion.
**Two constructions, 0.2% apart on the point.**

Adding the §3 RNPL leakage as a multiplicative haircut: at the D central cell (21% share,
+4pp) the point falls to **$4,755M** and at the management-implied +6pp to **$4,735M** —
i.e. **the entire RNPL cancellation adjustment moves the 3Q26 point by less than the width
of the 50% interval.**

### 4.5 4Q26 on a GBV_3Q26 grid (`D7_live_4q26_grid.csv`)

Same object, `carried_4Q26 = c_Q4 × 0.584 × [⅔ GBV_3Q26 + ⅓ × 27,200]`:

| GBV_3Q26 ($M) | point ($M) | 50% interval | 80% interval |
|---|---|---|---|
| 25,500 | 3,117 | 3,078 – 3,158 | 3,044 – 3,195 |
| 26,000 | 3,157 | 3,118 – 3,198 | 3,083 – 3,236 |
| **26,300** | **3,181** | **3,142 – 3,222** | **3,107 – 3,260** |
| 26,500 | 3,197 | 3,157 – 3,239 | 3,122 – 3,277 |
| 27,000 | 3,238 | 3,197 – 3,279 | 3,161 – 3,318 |
| 27,500 | 3,278 | 3,236 – 3,320 | 3,200 – 3,359 |
| 28,000 | 3,318 | 3,276 – 3,360 | 3,239 – 3,400 |

At GBV_3Q26 = 26,300 this gives $3,181M against kernel-lambda's $3,200M — 0.6% lower,
because this object's `k` is estimated on the ex-COVID window rather than on all history.
**Whoever assembles the unconditional 4Q26 distribution must convolve this grid with the
GBV_3Q26 distribution below; the intervals here are conditional on GBV and exclude it.**

### 4.6 What predicts the next GBV print (`D8`, `D9`)

Target GBV_q; every predictor dated q−1 (printed in the letter carrying the guide for q);
expanding-window refit; naive = y/y persistence (GBV_q = GBV_{q−4} × (1 + y/y_{q−1})).

| feature | W1 n | W1 RMSE % | W1 ratio | W2 n | W2 RMSE % | W2 ratio | beats naive both? |
|---|---|---|---|---|---|---|---|
| naive y/y persistence | 14 | 3.258 | 1.000 | 10 | 3.075 | 1.000 | — |
| **unearned fees y/y, RNPL-corrected k = 1.0** | 12 | **2.655** | **0.815** | 10 | **2.674** | **0.870** | **yes** |
| unearned fees y/y, RNPL-corrected k = 0.5 | 12 | 3.236 | 0.993 | 10 | 3.356 | 1.091 | no |
| paid-backlog y/y | 12 | 3.626 | 1.113 | 10 | 3.854 | 1.253 | no |
| funds payable y/y | 12 | 4.019 | 1.234 | 10 | 4.163 | 1.354 | no |
| unearned fees y/y, raw | 12 | 4.051 | 1.244 | 10 | 4.288 | 1.395 | no |
| GBV y/y momentum (fitted slope) | 13 | 5.122 | 1.572 | 10 | 3.828 | 1.245 | no |
| nights y/y | 13 | 7.847 | 2.409 | 10 | 5.124 | 1.666 | no |

**Only one thing beats the naive on both windows: the RNPL-confound-corrected unearned-fees
series at k = 1.0.** The correction adds back the *year-over-year change* in the disclosed
RNPL GBV share, in points — a PIT-safe, non-circular adjustment that never touches
next-quarter revenue. This reproduces tracker-backlog's finding that the corrected unearned
series clears the bar the raw one fails, and inherits its caveats exactly: two of the share
inputs (3Q25 5%, 4Q25 12%) are **researcher ramp values with no disclosure behind them**,
and "best of the pre-registered k grid after seeing both windows" is a mild
multiple-comparison exposure. Note also that fitting a slope on GBV momentum is *worse* than
the naive, which imposes a slope of 1 — the fitted slope is estimated on too little data.

Live GBV_3Q26 (`D9_live_gbv_3q26.csv`), from a 3Q25 base of $22,900M:

| feature | implied GBV y/y | point $M | bias-corrected $M | 80% band $M |
|---|---|---|---|---|
| naive y/y persistence | +15.7% | 26,505 | 26,514 | 25,508 – 27,602 |
| **RNPL-corrected UF, k = 1.0** | **+15.2%** | **26,381** | **26,551** | **25,666 – 27,499** |
| RNPL-corrected UF, k = 0.5 | +11.6% | 25,561 | 25,891 | 24,810 – 27,070 |
| paid-backlog y/y | +12.4% | 25,736 | 26,463 | 25,184 – 27,879 |
| GBV momentum (fitted) | +18.9% | 27,231 | 26,707 | 25,480 – 28,057 |
| unearned fees y/y, raw | +8.4% | 24,821 | 25,299 | 23,957 – 26,800 |

> **What the ledger alone supports: GBV_3Q26 ≈ $26.4–26.6bn central (+15.2% to +15.7% y/y),
> 80% band $25.7–27.5bn.** The two objects that survive a walk-forward test — the naive and
> the corrected unearned-fees series — agree to within 0.5% ($26,381M against $26,505M raw,
> $26,551M against $26,514M bias-corrected). The raw unearned-fees series
> would say $24.8bn and is the one number in this table that must **not** be used: it is the
> RNPL deferral showing through, not a demand signal.
>
> **This is a separate route from the reviews/calendar alt-data nowcast (Krish's Q3 nowcast),
> which is not used, referenced or blended anywhere in this package.** If the two disagree,
> that disagreement is information and should be presented as two routes, not averaged.

---

## 5. Caveats

1. **n.** The panel has 24 quarters; requiring five GBV lags leaves 20, ex-COVID 16, 2023Q1+
   14. The PIT replays score 12 (W1) and 10 (W2) targets. Every interval in this note is
   built on samples where a single quarter moves the answer materially.
2. **COVID.** The ex-COVID rule drops 3Q21, 4Q21, 1Q22 and 3Q22 but keeps 2Q22 and 4Q22,
   whose nights y/y (24.8% and 20.2%) sit just inside the ±25% threshold. The threshold is
   the brief's, not a fitted choice, but the sample is sensitive to it.
3. **Identification.** φ₁ and φ₂ are not separately identified (bootstrap correlation −0.48
   to −0.90). Season-specific φ is saturated. The *level* of the paid-versus-booked wedge is
   not identified because the kernel's φ tail and the true prepayment rate are confounded;
   only the change against a pre-RNPL seasonal norm is.
4. **Softmax boundary.** φ_k = 0.000 means "driven to the boundary", not "estimated at zero".
5. **Block bootstrap.** Block length 4 on a series of 14–20 with a four-seasons-twice
   rejection rule. The intervals are optimistic if anything, and they are already wide.
6. **The 2Q26 coverage row uses the 3Q26 guide midpoint, not a print,** and is labelled as
   such everywhere it appears (`B4`). It is a forward-looking ratio and must not be scored
   as a realised one.
7. **RNPL share provenance.** The 3Q25 (5%) and 4Q25 (12%) shares carry no disclosure of any
   kind; 1Q26 (20%) is management's floor; 2Q26 (22%) is a researcher pick inside a ">20%"
   floor. Two of the eight quarters behind the corrected unearned-fees feature, and the 1Q26
   row of the λ check, rest on undisclosed values.
8. **The circular restated unearned-fees series is not used.** Nor is the harness, the
   registry, or `score.py`.
9. **This package produces no fee step and no FX step.** The λ and `c_s` conversions are
   outputs of printed revenue over printed GBV and already contain both; neither may be
   subtracted again downstream.
10. **The brief's premise on the migration confound is reversed here** (§2.5), on the
    strength of the FY2025 10-K language and the cash-flow reconciliation in
    `docs/rnpl-short-audit/04_balance-sheet-verification.md`. If that verification is itself
    wrong, §2.5 and the funds-payable caveats in §2.2 fall with it; nothing else in this note
    depends on it.

---

## 6. Files

`data/processed/forecast_methods/kernel_phi_v2/` — 30 CSVs plus `F1_phi_by_season.png`;
`00_manifest.csv` lists them all.

| group | files |
|---|---|
| A — weights | `A1_phi_estimates`, `A2_phi_bootstrap_ci`, `A3_loo_comparison`, `A4_rolling_windows`, `A5_dollar_map_2q26_gbv`, `A5b_lifetime_take_rate_check`, `A6_identification`, `A7_phi1_phi2_split_profile` |
| B — paid backlog | `B1_paid_backlog_panel`, `B2_coverage_norms`, `B3_coverage_deviations`, `B4_live_2q26_ledger`, `B5_three_way_decomposition` |
| C — RNPL | `C1_lambda_series`, `C2_lambda_season_norms`, `C3_leakage_grid`, `C4_1h26_lambda_check`, `C5_control_chart_5nov`, `C6_d1_nights_crosscheck` |
| D — residual and live | `D0_carried_and_residual_panel`, `D1_residual_R_by_season`, `D2_residual_R_explainers`, `D3_carried_weight_pit_sweep`, `D4_R_model_pit_race`, `D5_R_model_pit_replay`, `D6_live_3q26_conditional`, `D7_live_4q26_grid`, `D8_gbv_forecast_pit_race`, `D9_live_gbv_3q26` |

Code: `analysis/src/forecast_methods/kernel_phi_v2/{common,phi_fit,stage_a,stage_b,stage_c,stage_d,run}.py`,
plus the three untouched seed copies `kernel_seed.py`, `tracker_common_seed.py`,
`tracker_rebuild_seed.py` kept for provenance.
