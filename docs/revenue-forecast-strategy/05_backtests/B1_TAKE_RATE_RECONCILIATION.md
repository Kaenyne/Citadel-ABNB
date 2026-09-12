# B1 — the 3Q26 printed take rate, reconciled to ONE number and ONE probability

Run date 2026-09-11. Closes RED_TEAM.md **F3** ("three live 3Q26 objects are mutually
inconsistent; the take-rate pre-registration is decided by which one you read") and the
related identity failure `GBV ≠ nights × ADR` by 0.22 pp.

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/live_block_v2/run.py   # exit 0
```

Code: `analysis/src/forecast_methods/live_block_v2/` (copies of `optimal_mix/combine.py`
and of the kernel from `kernel_lambda/kernel.py`; nothing under `optimal_mix/`,
`fee_takerate/`, `kernel_lambda/` or the existing registry was read-modified).
Data: `data/processed/forecast_methods/live_block_v2/`.
Registry: `live-block-v2__{revenue,gbv,nights,adr,take_rate}.csv`, all `2026Q3`,
window `LIVE`, `vintage_date 2026-09-11`, both replays.
Card: `data/processed/forecast_methods/live_block_v2/LIVE_3Q26_CARD.csv`.

---

## THE ANSWER

> **3Q26 printed take rate = 18.14 %** (sd **0.46 pp**; q10 17.57 / q50 18.14 / q90 18.76)
> **P(printed take rate ≥ 18.10 %) = 0.53.** P(≤ 17.88 %, "fully offset") = 0.28.

+26 bp y/y against 3Q25's 17.88 %. Quote **one** number and **one** probability. The
programme's other three take-rate figures — 17.81 %, 18.40 % and the bare "18.14 %" with
no distribution — are superseded by this row and must not appear in the memo.

**The pre-registered test is a coin flip.** That is the finding, and it is not a failure
of the reconciliation — it is what the arithmetic says once the block is made consistent.

---

## 1. Where each of the three numbers came from, and why they differ

`data/processed/forecast_methods/live_block_v2/01_three_number_trace.csv`

| # | number | file / object | formula actually executed | numerator | denominator | sd | P(≥18.10) |
|---|---|---|---|---|---|---|---|
| 1 | **17.8065 %** | `optimal_mix/combined_live_objects.json` → `objects.live_3Q26_take_rate_pct` | `inv_mse` combination of **two take-rate MODELS**: 0.3401 × `fee-takerate\|take_rate_kernel` (18.2316) + 0.6599 × `fee-takerate\|take_rate_lastyear` (17.5875) | **none — the ratio is modelled directly and never divided** | none | 0.4424 | 0.254 |
| 2 | **18.1399 %** | the *same* JSON, never published as an object | `print_3Q26_revenue_musd.point_musd / live_3Q26_gbv_musd.point` = 4,816.1 / 26,549.76 | optimal-mix combined revenue 4,816.1 (`bma_logscore`, pool `all`) | optimal-mix combined GBV 26,549.76 (`stack_shrunk`, pool `all`) | — | — |
| 3 | **18.3971 %** | `fee_takerate/07a_live_3q26_take_rate.csv`, row `gbv 26,300 / theta central` | (λ_Q3 17.2394 % × lagged base 27,866.7 = **4,804.04**) × central-θ fee uplift = **4,838.45**, ÷ **26,300** | kernel revenue × fee step | **hand-set** GBV 26,300 (the architect's central case, *not* the programme's own GBV forecast) | 0.3941 | 0.775 |

### Why #1 differs from #2 — 33.3 bp

**#1 is a model *of* the ratio, not a ratio of the models.** Two thirds of its weight
(0.6599) sits on `tau_lag4_plus_drift` = 17.5875 %, a pure persistence object anchored on
3Q25's printed 17.88 % plus a trailing drift. It cannot see the 2026 revenue path (guide
+15–17 %, cushion +1.86 %) or the 2026 GBV path at all. Its predictive sd, 0.4424 pp, is
mostly *disagreement between the two models* (they are 0.64 pp apart), not information
about the print. The object never touches the live block's own revenue and GBV numbers,
so nothing forces it to agree with them, and it does not.

Arithmetic coincidence worth knowing before someone "discovers" it: the **guide midpoint**
4,730 ÷ the combined GBV = **17.816 %**, within 1 bp of the published 17.81 %. It is a
coincidence — #1 is not derived that way — but it is the right way to *read* 17.81 %: it
is roughly "the company prints its guide midpoint and earns no cushion."

### Why #3 differs from #2 — 25.7 bp, from two independent swaps

`01b_discrepancy_decomposition.csv`, one swap at a time:

| step | take rate | Δ |
|---|---|---|
| start: implied by the live block (4,816.1 / 26,549.8) | 18.1399 % | — |
| swap the **numerator** for kernel revenue × central-θ fee step (4,816.1 → 4,838.4, **+0.46 %**) | 18.2241 % | **+8.4 bp** |
| swap the **denominator** for the hand-set GBV (26,549.8 → 26,300, **−0.94 %**) | 18.3971 % | **+17.3 bp** |
| = `fee-takerate` 07a central θ | 18.3971 % | **+25.7 bp total** |

**Two thirds of the gap is the denominator, not the fee.** This is the same defect as
RED_TEAM F2: the whole 4Q26 block is anchored on a hand-set `GBV_3Q26 = 26,300` while the
programme publishes its own 26,549.8. `fee-takerate`'s own §6 already warned that the test
"discriminates on GBV, not on the fee"; the decomposition measures how much — at the
frozen-card GBV the *no-fee* counterfactual is already 18.35 %, i.e. the threshold clears
before any fee step is applied.

---

## 2. The reconciled block: identity imposed, distribution derived once

### 2.1 What is an input and what is an output

ABNB **defines** ADR as GBV ÷ Nights and Seats Booked, and the printed take rate as revenue
÷ **same-quarter** GBV. So:

* **inputs (carried unchanged from optimal-mix):** revenue 4,816.1 (sd 48.0), GBV
  26,549.76 (sd 853.21), nights and seats 147.376 (sd 3.077);
* **outputs (identities, computed inside every draw):** ADR = GBV / nights,
  take rate = 100 × revenue / GBV.

The published block's 0.22 pp break — `(1+nights_yoy 10.3423 %)(1+adr_yoy 5.2668 %) − 1 =
16.154 %` against `gbv_yoy 15.938 %` — is charged **entirely to ADR**, because ADR is the
definitional residual and because it is the only one of the three with no registered
baseline at all (RED_TEAM §6.3). Imposing the identity moves ADR y/y from **+5.27 % to
+5.17 %** (−10 bp); nights and GBV are untouched.

### 2.2 The joint draw

Each published marginal is already Gaussian on the level (`q10 = point − 1.2816·sd` exactly),
so the reconciliation changes only the **dependence**, which the published block never
specified. The correlation is the correlation of the **combined walk-forward percent
errors** `(point − actual)/actual`, taken from `optimal_mix/05_combined_walkforward.csv` at
the *same* pool and scheme each live object was built from
(`02_walkforward_error_correlation.csv`):

| pair | W1 / PIT (**n = 14**) | W2 / PIT (n = 10) | W1 / full_sample (n = 14) |
|---|---|---|---|
| **corr(revenue err, GBV err)** | **+0.7595** | +0.5347 | +0.5048 |
| corr(revenue err, nights err) | +0.6753 | +0.1808 | +0.3079 |
| corr(GBV err, nights err) | +0.8775 | +0.7104 | +0.8176 |

**Headline uses W1 / PIT, ρ(revenue, GBV) = +0.7595, n = 14.** 500,000 draws, seed
20260911. The point is the identity applied to the points (exact, reproducible); the sd and
quantiles come from the draws. The Monte-Carlo *mean* of the ratio is 18.155 % — 1.5 bp of
Jensen — and is not used.

### 2.3 The result

| object | point | sd | q10 | q50 | q90 | y/y |
|---|---|---|---|---|---|---|
| revenue (musd) | 4,816.1 | 48.0 | 4,754.6 | 4,816.1 | 4,877.6 | +17.61 % |
| GBV (musd) | 26,549.8 | 853.2 | 25,456.3 | 26,549.8 | 27,643.2 | +15.94 % |
| nights and seats (m) | 147.376 | 3.077 | 143.433 | 147.376 | 151.320 | +10.31 % |
| ADR (usd) — *identity* | 180.15 | 3.08 | 176.16 | 180.14 | 184.04 | +5.17 % |
| **take rate (%) — *identity*** | **18.1399** | **0.4628** | **17.5731** | **18.1396** | **18.7557** | **+26 bp** |

**P(take rate ≥ 18.10 %) = 0.5345. P(≤ 17.88 %) = 0.2833.**

The take rate's uncertainty is almost entirely GBV uncertainty: sd(revenue)/revenue is
1.00 % against sd(GBV)/GBV of 3.21 %.

### 2.4 The probability is robust; the *point* is not

`03_takerate_sensitivity.csv` — P moves by at most 1.4 pp across every dependence
assumption available, including the two degenerate ones:

| basis | ρ(rev,GBV) | sd (pp) | **P(≥18.10)** |
|---|---|---|---|
| **W1 / PIT (headline), n = 14** | **0.7595** | **0.463** | **0.534** |
| W1 / full_sample, n = 14 | 0.5048 | 0.518 | 0.531 |
| W2 / PIT, n = 10 | 0.5347 | 0.512 | 0.532 |
| W2 / full_sample, n = 10 | 0.4350 | 0.532 | 0.530 |
| all correlations forced to 0 | 0 | 0.613 | 0.526 |
| all correlations forced to 1 | 1 | 0.404 | 0.540 |
| marginals widened to the realised W1 walk-forward RMSE | 0.7595 | 0.627 | 0.526 |

But the **point** is a near-linear function of the GBV input, and the GBV input is contested
(`04_gbv_sensitivity.csv`):

| GBV assumed | take rate | P(≥18.10) |
|---|---|---|
| 25,900 (architect grid low) | 18.595 % | 0.853 |
| 26,185 (frozen card) | 18.393 % | 0.735 |
| 26,300 (architect central, the 4Q26 anchor) | 18.312 % | 0.676 |
| **26,549.8 (optimal-mix combined — used here)** | **18.140 %** | **0.534** |
| 26,800 | 17.971 % | 0.389 |
| 27,000 (architect grid top) | 17.837 % | 0.281 |

**The pre-registered test resolves on a 0.22 % move in GBV.** The GBV at which the
reconciled point is exactly 18.10 % is **26,608.3 musd**, 0.22 % above the combined point.
Equivalently, on the combined GBV the test requires a revenue print of **≥ 4,805.5 musd** —
**above the top of management's own 3Q26 guide range (4,770)** and +1.60 % on the midpoint
(4,730). It clears only because the trailing-8 cushion (+1.86 %) is bigger than the gap.
The choice of GBV here matches the sibling B2 object
(`guidance-policy-v2__gbv_musd_live.csv` = 26,549.7639), so the programme now uses one GBV.

---

## 3. Identity check

`05_identity_check.csv`. Tolerance 0.01 %.

| check | deviation | verdict |
|---|---|---|
| GBV vs nights × ADR, reconciled **point** | **0.00000 %** | PASS |
| GBV vs nights × ADR, worst of 500,000 **draws** | **0.00000 %** | PASS |
| take rate vs revenue ÷ GBV, worst of 500,000 draws | 0.00000 % | PASS |
| *published* block: (1+nights y/y)(1+ADR y/y)−1 vs GBV y/y | 0.216 pp | FAIL (the F3 break) |
| *published* block: revenue ÷ GBV vs published take rate | 0.333 pp | FAIL (the F3 break) |
| printed history 2023Q1–2026Q2: GBV vs nights × ADR, worst quarter | 0.270 % | PASS — the letter rounds GBV to $0.1 bn (±0.25 %) and nights to 0.1 M, so the identity is only checkable to ~0.32 %. It holds in the disclosures to the rounding. |

---

## 4. Seasonal sanity check, and the object nobody may confuse with a take rate

### 4.1 The printed same-quarter take rate, Q3 only

| quarter | revenue | GBV | **printed take rate** | λ_Q3 (kernel, **lagged** GBV) | lagged ÷ same-quarter base |
|---|---|---|---|---|---|
| 3Q21 | 2,237 | 11,900 | 18.798 % | 18.089 % | 1.0392 |
| 3Q22 | 2,884 | 15,600 | 18.487 % | 16.898 % | 1.0940 |
| 3Q23 | 3,397 | 18,300 | **18.563 %** | 17.391 % | 1.0674 |
| 3Q24 | 3,732 | 20,100 | **18.567 %** | 17.145 % | 1.0829 |
| 3Q25 | 4,095 | 22,900 | **17.882 %** | 17.182 % | 1.0408 |
| **3Q26 (reconciled)** | **4,816.1** | **26,549.8** | **18.140 %** | 17.283 % | 1.0496 |

Reading: 3Q25 broke a 3-year run at ~18.55 % by dropping **−68 bp**, because GBV grew
+13.9 % while revenue grew only +9.7 %. Our 18.140 % recovers **+26 bp** of that — a little
over a third of the fall — and still sits **42 bp below** 3Q23/3Q24. It is not a heroic
number. The flip line 18.10 % is **+22 bp y/y**, and it requires revenue growth to exceed
GBV growth by **1.23 %** multiplicatively — i.e. revenue y/y ≥ **+17.36 %** at the combined
GBV. Our revenue point is +17.61 %. **That 25 bp of revenue growth is the entire test.**

Seasonal contrast for anyone reading a single quarter in isolation: 2Q26 printed
**13.26 %** and 1Q26 **9.17 %**. GBV is booked at booking; revenue is recognised at
check-in. Q3 take rates are structurally the highest of the year and are not comparable
with any other quarter.

### 4.2 λ_Q3 ≈ 17.24 % is NOT "a take rate below 18.10 %"

`kernel-lambda` measures a **different ratio**:

```
lambda_s  =  Revenue_q / [ (2/3)·GBV_{q-1} + (1/3)·GBV_{q-2} ]      <- LAGGED GBV
printed   =  Revenue_q / GBV_q                                       <- SAME-QUARTER GBV
```

λ_Q3 = **17.2394 %** (2023–25: 17.391 / 17.145 / 17.182, sd 0.132) on a 3Q26 lagged base of
**27,866.7** musd. The same-quarter base is **26,549.8**. The base ratio is **1.0496**, so:

```
17.2394 %  ×  1.0496  =  18.0945 %
```

and identically `kernel revenue 4,804.04 / 26,549.8 = 18.0945 %`. **The entire structural
gap is the seasonal GBV base ratio** — Q3 bookings are seasonally *below* the Q1/Q2
bookings whose stays are recognised in Q3 — and it has run **+4.1 % to +8.3 %** since 2022.
Nothing about the two numbers is inconsistent; they are different objects with different
denominators.

Two consequences the memo must respect:

1. **Never write "λ is 17.24 %, so the take rate misses 18.10 %."** Converted properly, the
   kernel says **18.094 %** — 0.6 bp *below* the line, against the mix revenue's 18.140 %,
   which is 4.0 bp *above* it. **The pre-registered test is decided at the 5 bp level by
   which revenue object you use.** Say that out loud rather than letting a reader discover it.
2. The **16.77 %–17.06 %** figures in circulation (`M6_fx_takerate_timing_mechanics.md`
   §, `C_M6` §2, `00_IMPLEMENTATION_DECISIONS.md` L734: Q3 17.065 / 16.770 / 16.978) are
   **the same λ object at kernel weight w = 0.38**, not printed take rates. They are not
   "historical Q3 printed take rates" and must never be tabled next to 18.10 %. The printed
   Q3 history is **18.56 / 18.57 / 17.88**, above.

---

## 5. Caveats that survive the reconciliation

1. **The marginals are inherited, so their sins are inherited.** `mix_gbv_musd` loses to a
   seasonal naive on **both** windows (PIT ratio 1.312 / 1.021) and `mix_nights_m` loses on
   both (1.549 / 1.105) — RED_TEAM §2. This work fixes the block's **internal consistency**;
   it does not make the GBV object skilful, and the take rate is 90 % a GBV bet.
2. **Both legs over-forecast on the walk-forward, and GBV over-forecasts more.** W1 mean
   percent error: revenue **+0.80 %** (t = 2.14), GBV **+1.77 %** (t = 1.56), nights
   **+2.17 %** (t = 2.25). Removing both biases would move the take rate to **18.319 %** and
   **P to 0.680** (`03_takerate_sensitivity.csv`, last row). **It is not applied** — the
   published live objects are not de-biased either, the GBV bias is not significant on
   n = 14, and a 14-quarter bias estimate is itself noisy — but it is the single largest
   unexercised lever on the answer and it points **up**, so it must be disclosed rather than
   buried.
3. **`take_rate_pct` and `adr_usd` have no registered baseline**, so their
   `rmse_ratio_to_naive` is NaN and `survives_both_windows = False` is vacuous, not a defeat
   (RED_TEAM §6.3; harness change request in the package README).
4. **0.53 is a posterior from a Gaussian block, not a coverage guarantee.** Every conformal
   caveat on the underlying objects still binds: n_cal = 8, attainable band [0.889, 1.000],
   exchangeability violated.

---

## 6. What to say in the memo

> **"On the one line that decides the trade, our number is 18.14 % and our probability is
> 0.53 — a coin flip, and we are saying so."** The 3Q26 printed take rate is revenue
> divided by same-quarter GBV: $4,816 M ÷ $26,550 M = **18.14 %**, +26 bp on 3Q25's
> 17.88 %, with a standard deviation of 0.46 pp that is almost entirely GBV uncertainty.
> That puts **P(≥ 18.10 %) at 0.53**, stable between 0.53 and 0.54 under every dependence
> assumption we can estimate from fourteen walk-forward quarters. We previously carried
> three answers to this question — 17.81 %, 18.14 % and 18.40 %, implying probabilities of
> 0.25, unstated and 0.78 — and the differences were not about the fee: **two thirds of the
> spread was a hand-set GBV denominator of $26,300 M sitting next to our own forecast of
> $26,550 M**, and the rest was a take-rate model that never divides anything by anything.
> One number now, derived once, from a block in which GBV, nights and ADR satisfy
> Airbnb's own identities to machine precision.
>
> The honest framing of the pre-registration is this: **it is a GBV test wearing a fee
> test's clothes.** On our GBV, clearing 18.10 % requires a revenue print of **$4,805 M —
> above the top of management's own guide range of $4,770 M** — and it clears only because
> the trailing-8 guide cushion (+1.9 %) is larger than the gap. Move GBV by **0.22 %** and
> the test flips. That is why we pre-register the **pair** (take rate *and* GBV), not the
> take rate alone, and why the flip decision on 5 November should be read jointly with the
> Q4 nights bucket rather than off one ratio. Finally: **λ_Q3 = 17.24 % is not a take rate
> below our threshold.** It is revenue over *lagged* GBV; converted at the 3Q26 base ratio
> of 1.0496 it is **18.09 %**, and the figures of 16.8–17.1 % that appear in the earlier
> proposals are that same lagged object at a different kernel weight. If either number
> reaches a slide next to 18.10 %, the slide is wrong.

---

## 7. Registered objects

`data/processed/forecast_methods/registry/live-block-v2__*.csv`, format v1.0, both
`prior_basis` replays (the `full_sample` replay re-estimates the correlation on the
full-sample walk-forward: ρ(rev,GBV) = 0.5048, take rate sd 0.518 pp, P = 0.531).

| object | target | point | sd | n_params | n_train |
|---|---|---|---|---|---|
| `revenue` | `revenue_musd` | 4,816.1 | 48.0 | 0 | 13 |
| `gbv` | `gbv_musd` | 26,549.7639 | 853.209 | 0 | 13 |
| `nights` | `nights_m` | 147.3764 | 3.0774 | 0 | 13 |
| `adr` | `adr_usd` | 180.1494 | 3.0772 | 1 | 14 |
| `take_rate` | `take_rate_pct` | 18.1399 | 0.4628 | 1 | 14 |

`n_params` is 0 for the three carried objects (no new free parameter; the points are
optimal-mix's) and 1 for each identity output (the single walk-forward correlation that
sets its width). `n_train = 14` is the walk-forward sample the correlation is estimated on.
`knowable_from = 2026-08-06` (the shareholder letter) on every row.
`harness/score.py` was **not** run by this package.
