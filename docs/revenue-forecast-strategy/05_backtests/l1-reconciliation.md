# l1-reconciliation — Layer 1 constrained least-squares reconciliation

Overnight programme, 11 Sep 2026. Package `l1-reconciliation`.
Code `analysis/src/forecast_methods/l1_reconciliation/`.
Data `data/processed/forecast_methods/l1_reconciliation/`.
Registry `data/processed/forecast_methods/registry/l1-reconciliation__*.csv`.

## Header statements required by the addendum

**Numeraire.** This package hands **reported ADR** — GBV in reported USD divided by
Nights-and-Seats. It is **not** host payout per night and **not** `usd_constant`.
This package does **not** de-gross-up the fee migration; that equation lives in
`fee-takerate` and only there.

**Boundary.** Exactly one object crosses onward: **GBV in USD, booking-dated, one
number per quarter** (`l1_gbv_spine_quarterly.csv`). Nights, ADR, regional mix,
unit size, LOS, seats and regulation do not cross. The rule has been written into
`model/assumptions.md` under "L1 boundary rule".

**FY27 lines not rebuilt tonight.** The fee/take-rate step (+0.9pp at half weight),
new lines (+0.2pp), regulation (−0.3pp) and the hedge are carried as **assumed**
fixed inputs, labelled `assumed_not_rebuilt_tonight` in the decomposition file. No
build was fabricated to fill them.

## Exact commands

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/l1_reconciliation/run.py
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/score.py
```

Run time about 6 minutes (60 block-bootstrap refits plus 20 point-in-time refits).
Exit code 0.

## 1. Specification and parameter count

Free parameters, **60**:

| block | count | what |
|---|---|---|
| softmax logits | 3 × 18 = 54 | K−1 = 3 regional logits per quarter, 2022Q1–2026Q2, APAC is the reference |
| take-rate tilts | 3 | time-invariant regional multiplier `m_r`, APAC = 1 |
| take-rate drifts | 3 | one linear drift per region over the panel |

Everything else is **solved, not fitted**:

```
s_{r,q}   = softmax(a_{.,q})                     regions sum to 1 EXACTLY
n_{r,q}   = s_{r,q} * N_q                        nights identity EXACT
tr_q      = [sum_r Rev_{r,q}/m_{r,q}] / GBV_q    closed form
GBV_{r,q} = Rev_{r,q} / (tr_q * m_{r,q})         the 72 filed cells hold BY INVERSION
ADR_{r,q} = GBV_{r,q} / n_{r,q}                  OUTPUT
blend_q   = sum_r s_{r,q} * ADR_{r,q}            geographic mix is an OUTPUT
N_q       = n_home + n_hotel + s_exp + s_svc     seats/hotel dilution is an OUTPUT
```

Observations bounding those 60 parameters: **199** — 72 exact filed regional revenue
cells, 16 annual 10-K regional nights cells (FY2022–FY2025), 43 letter regional
nights-growth cells, 38 reported regional ADR y/y integers, 30 ex-FX regional ADR
y/y integers. Plus 18 exact total-nights identities and 18 exact total-GBV
identities that hold by construction.

Interval handling, as mandated: every band is a hinge on `[lo, hi]`, never a
midpoint; letter integers are scored on `[x−0.5, x+0.5]`; the **14 `basis ==
'derived'` rows (NA 8, EMEA 6, 4Q22–3Q24) are excluded from every likelihood**;
the 22 numeric LatAm/APAC stated integers enter as rounding intervals.

Regional shares are shares of **total Nights-and-Seats**, not of home nights,
because the 10-K regional table and the letters' regional ADR sentences are on that
basis (`research/notes/2026-09-09_seats-dilution.md`). The home/seat split is
applied only at the total level, which is where the dilution *output* lives. The
FY2025 cross-check: the four annual regional cells sum to 533.5M against a printed
FY2025 Nights-and-Seats of 533.0M.

Non-home volumes (hotels, experiences seats, services seats) are exogenous, dated
and **never fitted**, from the seats-dilution note's base case; 2021–2023 annual
values are back-extrapolated and carry `basis = assumed_backcast`. A ×0.60/×1.45
sensitivity case is coded (`NONHOME_CASES`) and changes no conclusion below,
because the dilution term nets out of GBV.

Regional FX pp on ADR is taken from the **letters themselves** wherever both the
reported and the ex-FX integer are disclosed for the same cell
(`fx_pp = mid(reported) − mid(exfx)`, `source = disclosed_pair`), and from a
GBV-weighted regional currency basket × the regional pass-through slope otherwise.
Unfitted basket-vs-disclosed agreement on 2026Q2: EMEA 1.77 vs 2.00, LatAm 6.89 vs
7.00. That is a free validation of the basket, not a fitted result.

## 2. Gate G2 — PASS, and where the disclosures stop cohering

### 2.1 The headline fit

`l1_residual_summary.csv`, n on every row:

| constraint class | n | inside its band | max overshoot beyond the band | mean abs |
|---|---|---|---|---|
| exact regional revenue (56 filed + 16 exact Q4 back-out) | 72 | **72** | 2.27e−13 $M | 2.9e−14 |
| annual 10-K regional nights | 16 | **16** | **0.0008 M nights** | 0.00019 |
| letter regional nights y/y | 43 | 14 strictly | **0.062 pp** | 0.011 |
| reported regional ADR y/y | 38 | 7 | **8.25 pp** | 1.26 |
| ex-FX regional ADR y/y | 30 | 5 | **4.57 pp** | 0.98 |

The 72 exact cells are 56 `basis == 'filed'` three-month regional revenue cells plus
16 `basis == 'back_out'` Q4 cells (FY 10-K minus the nine-month 10-Q). The back-outs
are an *exact arithmetic* derivation from two filed numbers — L0's own
`reconciliation_max_abs_diff_musd` is 0.0 — not a modelling assumption, so they are
constrained exactly like the filed cells. "72 filed" was loose shorthand inherited
from the L0 spine; the accurate phrase is **72 filed-or-exact-back-out cells**.

The 16 annual 10-K regional nights cells are not a *clean* subset of a dirtier 24.
All 24 annual cells in `L0_interval_observations.csv` are `basis == 'filed'` and
`included == True`. Only 16 (FY2022–FY2025) enter the fit because the reconciled
panel spans 2022Q1–2026Q2, so FY2020 and FY2021 fall outside the **panel window**.
That is a date-window boundary, not a data-quality filter.

Read the nights-y/y row correctly: 29 of the 43 cells sit outside their band by at
most 0.062pp, which is 8% of a rounding half-width. Treat the class as satisfied.
The ADR rows are not a near miss.

### 2.2 The feasibility ladder — the actual G2 answer

`l1_feasibility_ladder.csv`. Each stage refits with only the named classes active,
then scores **all** classes. Max overshoot beyond the band, in the class's own units:

| stage | exact rev ($M) | annual nights inside | annual nights (M) | nights y/y (pp) | ADR reported (pp) | ADR ex-FX (pp) |
|---|---|---|---|---|---|---|
| exact cells only | 1.1e−13 | 0/16 | 12.880 | 28.891 | 16.853 | 16.853 |
| + annual nights | 1.1e−13 | **16/16** | **0.000022** | 18.754 | 8.304 | 8.304 |
| + nights y/y | 1.1e−13 | **16/16** | **0.000029** | **0.00079** | 7.503 | 7.503 |
| + ADR reported | 2.3e−13 | 12/16 | 0.0042 | 0.705 | 6.891 | 4.340 |
| + ADR ex-FX (all) | 2.3e−13 | 12/16 | 0.0092 | 0.776 | 7.301 | 4.059 |

**Gate G2 passes.** The two things G2 names — reproduce all 72 filed cells, and put
every clean annual regional nights cell inside ±0.5M — hold *simultaneously and
exactly*, to 1e−13 $M and 2e−5 M nights, at 60 free parameters. Adding the 43
letter regional nights-growth cells costs nothing: all three classes hold together
to 8e−4 pp. That is a genuinely strong result — three independent disclosure
families, two of them interval-censored, are mutually consistent to numerical noise.

**And the disclosures are mutually inconsistent one class further on.** No
assignment of regional shares that respects the filed regional revenue, the 10-K
annual regional nights and the letter regional nights growth can also reproduce the
letters' regional **ADR** y/y integers under a regional take rate that is constant
or linearly drifting. The surviving gap is up to **7.3pp** on reported regional ADR
y/y and **4.1pp** ex-FX, mean about 1.0–1.3pp. Per the addendum this is reported as
a finding; the exact constraint was **not** relaxed to make it go away.

**Why the ladder's 7.3 / 4.1pp and §2.1's 8.25 / 4.57pp differ** (a reader could
confuse them, so state it): they are two different fits of the same data. The
ladder deliberately fits the ADR classes at **weight 1.0**, so each stage is a
genuine feasibility test — "can this class be satisfied at all, given the ones
below it". The headline fit in §2.1 uses `W_CONF` **adr = 0.25**, trading some ADR
fit for the lexicographic G2 priority on the exact cells and the annual nights.
Neither number corrects the other; both are printed with their weight, and they
must not be quoted interchangeably. `run.py` now prints this caveat above the
ladder and stamps `adr_constraint_weight` into `l1_feasibility_ladder.csv`.

Where the gap sits (`l1_residuals_by_constraint.csv`, cells missing by more than
1pp, n = 21): 18 of 21 are in 2025Q1–2026Q2; by region EMEA 6, LatAm 8, APAC 5, NA
2; worst single cell EMEA reported ADR y/y, 8.25pp. The concentration in 2025–26 and
in the non-USD regions is what you would expect if the **regional take rate moved**
in exactly the window in which the fee migration, RNPL and the cross-border mix were
moving — i.e. the identification failure is informative, not merely numerical. A
regional take rate free to move quarter by quarter would close the gap and identify
nothing, so it was not fitted.

### 2.3 What the reparameterisation retires

* Regions sum to printed Nights-and-Seats to **2.8e−14 M** over 18 quarters. The
  **−0.41pp calibration plug is retired**; it cannot exist under a softmax.
* Blended ADR equals the share-weighted sum of regional ADRs to **5.7e−14 USD**.
  The **+0.19pp current-weighting index bias is arithmetically impossible**.
* Regional GBV sums to printed GBV to **3.6e−12 $M**. The 1.13pp / ~$175M broken
  loop in the existing driver model is closed by construction.

## 3. Acceptance tests

`l1_acceptance_tests.csv`.

| # | test | result | numbers |
|---|---|---|---|
| A1 | reproduce all 72 exact regional revenue cells (filed or exact Q4 back-out) | **PASS** | 72/72, max abs 2.27e−13 $M; composition 56 filed + 16 exact back-out |
| A2 | every annual regional nights cell **inside the fitted panel window** inside ±0.5M | **PASS** | 16/16, max overshoot 0.0008 M; 16 of 24 L0 annual cells are in-window (FY2020/21 predate the 2022Q1 panel start; all 24 are `basis=filed, included=True`) |
| A3 | regional nights sum to printed Nights-and-Seats exactly | **PASS** | max 2.84e−14 M over n=18 |
| A4 | blended ADR = share-weighted regional ADR (mix is an OUTPUT) | **PASS** | max 5.68e−14 USD, n=18 |
| A5 | regional GBV sums to printed GBV | **PASS** | max 3.64e−12 $M, n=18 |
| A6a | seasonal λ **mean** within 0.35pp of the **most recent same-season observation** (the method cards' right-hand column) at w = 2/3 | **PASS** | Q1 12.694 vs 12.612 (+0.082, n=4); Q2 13.714 vs 13.736 (−0.022, n=4); Q3 17.239 vs 17.182 (+0.057, n=3); Q4 12.030 vs 12.026 (+0.004, n=3) |
| A6b | seasonal λ **mean** reproduces the architect's own headline **mean** where one is published (λ_Q3), i.e. mean-against-mean | **PASS** | Q3 17.2394 vs 17.239 (+0.0004pp, n=3); no headline mean is published for Q1/Q2/Q4, so only Q3 is testable like-for-like |
| A7 | reproduce the ADR note's geographic-mix drag 2023–25 | **PASS** | 2023 −1.22 vs −1.08; 2024 −1.13 vs −1.24; 2025 −1.48 vs −1.58; n=3 |
| A8 | reproduce the ADR note's within-region ex-FX ADR term 2023–25 | **FAIL** | 2023 +2.60 vs +3.10 (−0.50); 2024 +2.01 vs +3.44 (−1.43); 2025 +3.13 vs +3.41 (−0.28); n=3 |
| A9 | FY27 within 1% of the Street midpoint | **PASS** | 15,838 vs 15,745 (+0.59%), n=1 |

**A6 was reworded after verification.** The four values 12.612 / 13.736 / 17.182 /
12.026 are real and correctly sourced, but they are the **single most recent
same-season observation** (1Q26, 2Q26, 3Q25, 4Q25) — not a multi-year mean. What
this package computes is a multi-year **mean**. Comparing a mean to a single
observation is a weaker test than "reproduces the architect's table", so the row is
now split: A6a states plainly that it is mean-vs-single-observation, and A6b does
the one like-for-like mean-vs-mean comparison available — `00_INTEGRATED_SYSTEM.md`
publishes λ_Q3 as **17.239**, a 3-year mean, which this package's own mean matches
to 0.0004pp. No number changed; the framing did. Downstream the FY27 kernel build
already used the recomputed means (12.694 / 13.714 / 17.239 / 12.030), never the
target column, so nothing moved.

On A6 I report **all** available λ values, which settles the documentation
inconsistency the chief of staff flagged: Q1 and Q2 have **four** observations
(1Q23 12.803 and 2Q23 13.724 exist and are usable) while Q3 and Q4 have three. The
season means above use all available values; using only 2024–26 moves Q1 by
−0.082pp and Q2 by +0.022pp and changes nothing downstream.

## 4. (b) Validation against the ADR decomposition note

`l1_annual_adr_decomposition.csv`, n = 4 regions per year, built from this
reconciliation and nothing else.

| year | blended ADR y/y | within-region ex-FX (l1) | note | diff | geo mix (l1) | note | diff | FX (l1) |
|---|---|---|---|---|---|---|---|---|
| 2023 | +1.72% | +2.60pp | +3.10 | −0.50 | **−1.22pp** | −1.08 | −0.14 | +0.36 |
| 2024 | +1.77% | +2.01pp | +3.44 | −1.43 | **−1.13pp** | −1.24 | +0.11 | +1.00 |
| 2025 | +2.92% | +3.13pp | +3.41 | −0.28 | **−1.48pp** | −1.58 | +0.10 | +1.40 |
| 2026 (H1 annualised) | +8.13% | +5.99pp | — | — | **−0.34pp** | — | — | +2.44 |

**Geographic mix reproduces (A7).** Three independent constructions — the 10-K
regional panel in the ADR note, and this reconciliation which never sees that panel
— agree to ≤0.14pp on a −1.1 to −1.6pp drag. That is the strongest cross-validation
in this package and it is worth quoting.

**The within-region ex-FX term does not reproduce in 2024 (A8).** The 2023 and 2025
gaps (−0.50 and −0.28pp) are inside the reconciliation's own interval width; 2024's
−1.43pp is not. Reason, stated rather than plugged: the two constructions split the
same reported number differently at the FX line. My FX term for 2024 is +1.00pp,
built region by region from disclosed-pair FX where available and the weighted
basket elsewhere; the note takes FX from the letters at the consolidated level. The
difference is a **decomposition** difference, not a level difference — the blended
reported ADR y/y is the same number in both. I have not adjudicated it tonight; the
honest reading is that the within-region / FX split of the 2024 move is identified
to about ±1.4pp, and the pitch should not lean on it.

**A live finding, not in the plan.** The geographic-mix drag is **fading**, not
accelerating: −1.22, −1.13, −1.48, then **−0.34pp** in 2026 H1. The FY27
decomposition's assumed −1.5pp mix line is roughly four times the currently
observed drag. My own FY27 build produces −1.09pp, and even that may be too
negative. Someone should look at this before the memo is written.

## 5. Uncertainty — block bootstrap

`l1_bootstrap_intervals.csv`. 4-quarter block weighted bootstrap, 60/60 replicates
converged. No Stan, no PyMC, no state space, as instructed.

2026Q2 share p10–p90 (pp of Nights-and-Seats): NA 28.9–30.8, EMEA 39.1–41.9, LatAm
15.0–17.7, APAC 12.3–13.8. Regional reported ADR p10–p90: NA $224–292, EMEA
$184–223, LatAm $63–85, APAC $90–107.

Read that honestly: **regional shares are tight (±1pp) and regional ADR levels are
not (±15%)**. Shares are pinned by the annual 10-K cells and the letter growth
cells; the ADR level is the residual of a revenue cell divided by a nights number,
so it inherits the whole width. Any downstream use of a regional ADR *level* is
using a ±15% number. This is the reason the boundary rule exists.

## 6. FY27

`l1_fy27_revenue_grid.csv`. Two scenarios × the mandatory kernel-weight
sensitivity. Revenue is the convolution of already-printed / projected GBV,
`Revenue_q = λ_season × [w·GBV_{q−1} + (1−w)·GBV_{q−2}]`. **No FX pp is added to
revenue anywhere**; booking-date FX is inside the lagged USD GBV base.

| scenario | kernel w | FY26 $M | FY27 $M | FY27 growth | 4Q26 print $M |
|---|---|---|---|---|---|
| driver base | 0.33 | 14,398 | 15,720 | +9.2% | 3,192 |
| driver base | 0.50 | 14,299 | 15,780 | +10.4% | 3,151 |
| **driver base** | **0.667** | **14,201** | **15,838** | **+11.5%** | **3,111** |
| data-only continuation | 0.33 | 14,457 | 16,135 | +11.6% | 3,251 |
| data-only continuation | 0.50 | 14,387 | 16,158 | +12.3% | 3,240 |
| data-only continuation | 0.667 | 14,319 | 16,179 | +13.0% | 3,229 |

Against Street FY27 **$15,730–15,760M** and the driver model's **$15,842M**: the
headline is **$15,838M, +0.6% above the Street midpoint and $4M from the driver
model**, reached by a completely different route (regional reconciliation + kernel,
versus the driver model's contemporaneous build). Say in the first 200 words of the
memo that our FY27 is within 1% of consensus.

The kernel-weight sensitivity is worth **$117M on FY27** (w 0.33 → 0.667: $15,720.3M
→ $15,837.6M, spread $117.3M), i.e. 0.74% of revenue and 2.34pp of growth — materially larger than on the 4Q26 point object,
because at FY27 horizon both lagged GBV terms are themselves projections. Propagate
0.33–0.667 as instructed.

The data-only continuation runs $300–400M hotter than the driver base. Its ADR line
is the honest culprit: the reconstruction's trailing-4 regional reported ADR y/y is
running at +6.2% (1Q26 +9.0%, 2Q26 +5.3% printed), and carrying that into 2027
implies a price line roughly 2.5× the driver model's +3% ex-FX. Reported as a
result; not believed as a forecast.

### FY27 named, non-overlapping decomposition

`l1_fy27_growth_decomposition.csv`. Every line has exactly one owner and appears
once. The residual is **not** split.

| line | pp | owner | basis |
|---|---|---|---|
| volume: NA nights (+6.0% y/y) | +2.35 | l1-reconciliation | estimated |
| volume: EMEA nights (+7.0%) | +2.91 | l1-reconciliation | estimated |
| volume: LatAm nights (+16.0%) | +1.60 | l1-reconciliation | estimated |
| volume: APAC nights (+15.0%) | +1.41 | l1-reconciliation | estimated |
| price: within-region ADR ex-FX (l-f-l + sub-regional mix, **unsplit**) | +3.00 | l1-reconciliation | estimated |
| geographic mix (**OUTPUT** of the share identity) | −1.09 | l1-reconciliation | output |
| unit size and LOS (bedroom elasticity **0.23**) | +0.38 | l1-reconciliation | estimated |
| seats and hotel dilution (**OUTPUT** of N = home + hotel + seats) | 0.00 | l1-reconciliation | output |
| booking-date FX carried through Φ | 0.00 | l1-reconciliation | estimated |
| fee / take-rate mechanism (half weight) | +0.90 | fee-takerate | **assumed, not rebuilt tonight** |
| new lines | +0.20 | — | **assumed, not rebuilt tonight** |
| regulation | −0.30 | — | **assumed, not rebuilt tonight** |
| hedge (dollars, added ONCE by kernel-lambda) | 0.00 | kernel-lambda | **assumed, not rebuilt tonight** |
| kernel timing (revenue is a convolution of LAGGED GBV) | +0.17 | kernel-lambda | identity |
| **total FY27 revenue growth** | **+11.52** | | |

Notes that matter:

* **Volume totals +8.27pp**, against the plan's assumed +8.6pp — close, and it is
  built bottom-up from four regional nights lines rather than asserted.
* **The +2.9pp like-for-like/sub-regional split is NOT made.** Price is reported as
  the identified **sum** only. Separate price and sub-mix states are exactly
  collinear; the object is an unidentified 2-d ridge and it is left as one.
* **Unit size and LOS is +0.38pp, not +2pp.** Bedroom-nights wedge +1.66pp ×
  elasticity 0.23. n = 1 disclosed quarter — the bedroom-nights disclosure appears
  once in the KPI panel, which is a real weakness and is stated as such. The Street
  mapping of +2pp wedge → +2pp ADR is not used anywhere in this package.
* **Seats/hotel dilution is 0.00pp on revenue and that is correct, not a miss.**
  Dilution moves reported ADR and the unit count in opposite directions by
  construction; GBV, and therefore revenue, is unchanged. The output is the reported
  **ADR** drag, −3.52pp in 2026 on the base non-home case. Anyone carrying a seats
  line into a *revenue* build is double counting.
* **Booking-date FX is 0.00pp for FY27** because the FX inputs end at 2026Q3 and
  2027 is run on a **flat-spot carry** (zero y/y). That is an assumption, stated,
  not a measurement, and it is the single largest unmodelled risk in the FY27 line.
  It is also the one place where a second FX subtraction could sneak in; it has not.
* **Geographic mix −1.09pp is an output**, not a lever. See §4: the observed 2026
  drag is only −0.34pp, so even −1.09 may be too negative.

### Prior-to-posterior contraction and the 20% strike rule

| term | contraction | verdict |
|---|---|---|
| geographic mix | high — reproduces three independent constructions to ≤0.14pp | keep |
| regional nights shares | high — bootstrap p10–p90 ±1pp of share | keep |
| seats/hotel dilution on revenue | exact (identically zero) | keep as an identity |
| regional ADR **levels** | low — bootstrap ±15% | keep internal, do **not** cross the boundary |
| within-region price ex-FX split (l-f-l vs sub-mix) | **0%** — exactly collinear | **struck**; reported as one unsplit sum |
| unit size and LOS | low — n = 1 disclosed quarter | **flagged**; kept only because it is small (+0.38pp) and signed |
| fee step, new lines, regulation, hedge | **0%** — carried as fixed inputs | **struck from this package**; owned elsewhere |
| booking-date FX FY27 | **0%** — flat-spot carry assumption | **struck**; not a measurement |

## 7. Point-in-time backtest — and a large, useful negative

`registry/l1-reconciliation__revenue_contemporaneous.csv`, 44 rows. At each guide
date the reconciliation is refit on the information set at that date (filings with
`knowable_from <= d`, intervals likewise, no consensus), regional nights and ADR are
rolled one quarter forward on each region's own trailing-4 y/y, and revenue is
`sum_r GBV_{r,q} × take_rate_{r,last}`. Both replays are written.

Scoreboard (`harness/scoreboard.csv`):

| object | window | replay | n | MAE $M | RMSE $M | bias | **RMSE ratio to naive** | CRPS | 80% coverage |
|---|---|---|---|---|---|---|---|---|---|
| l1 revenue_contemporaneous | W1 | PIT | 10 | 1147 | 1229 | +127 | **11.34** | 836 | 0.70 |
| l1 revenue_contemporaneous | W1 | full-sample | 14 | 1004 | 1027 | −12 | **10.93** | 616 | 0.64 |
| l1 revenue_contemporaneous | W2 | PIT | 10 | 1147 | 1229 | +127 | **11.34** | 836 | 0.70 |
| l1 revenue_contemporaneous | W2 | full-sample | 10 | 1077 | 1094 | +23 | **10.09** | 721 | 0.70 |

For scale, on the same window: `baselines__guide_cushion` 0.377, `kernel-lambda`
best 0.555, `baselines__naive` 1.000, `baselines__street` 1.073.

**This object loses to naive by a factor of eleven and it survives neither window.
It is registered anyway, as a negative control, because of what it proves.** Bias is
near zero (−12 to +127 $M) while MAE is $1,000–1,150M: the errors are not a level
error, they are a *seasonal phase* error. Multiplying a quarter's own GBV by a take
rate mis-states revenue by roughly 30% every quarter, alternating sign, because
revenue is check-in-dated and GBV is booking-dated. This is the sharpest empirical
confirmation in the whole programme of the architect's identity — revenue is a
convolution of **lagged** GBV — and it is a direct, quantified strike against any
contemporaneous take-rate route to revenue, which is what the existing driver model
uses.

**The honest corollary: l1 adds no forecasting power at the total level.** The l1
GBV spine is numerically identical to printed GBV (A5: max difference 3.6e−12 $M) —
the reconciliation *redistributes* GBV regionally, it does not re-estimate it. So
running the spine through the kernel reproduces `kernel-lambda`'s objects exactly
and would be a duplicate registration, not an improvement. That was not done. What
l1 contributes is the regional decomposition, the G2 verdict, the mix and dilution
outputs, and the FY27 build — not a level edge.

Point-in-time coverage is 10 of 14 W1 dates. The four missing early dates are a real
PIT limitation, not a bug: XBRL regional revenue for a quarter only becomes public
with the following year's comparative filing, so at 2023-02-14 the y/y base for the
guided quarter does not yet exist in the information set. The `full_sample` replay
covers all 14 by construction, which is exactly the difference the two-replay rule
is designed to expose.

## 8. What failed, honestly

1. **A8 fails**: the within-region ex-FX ADR term does not reproduce the note in
   2024, off by −1.43pp. Cause identified (a different FX split), not adjudicated.
2. **The regional ADR y/y integers cannot be satisfied** alongside the filed revenue
   and nights disclosures under any smooth regional take rate. Gap up to 7.3pp.
   Reported, not relaxed.
3. **The registered PIT object loses to naive by 11×** and survives neither window.
   Registered as a negative control with the interpretation above.
4. **Regional ADR levels are weakly identified** (±15% at p10–p90) even though
   shares are tight. This is why only GBV crosses the boundary.
5. **FY27 booking-date FX is a flat-spot carry**, i.e. an assumption of zero. The
   largest unmodelled term in the FY27 line.
6. **Bedroom elasticity rests on n = 1 disclosed quarter** of the bedroom-nights
   wedge. The +0.38pp is directionally right and small; it is not measured well.
7. **Non-home unit volumes for 2021–2023 are back-extrapolated** and flagged
   `assumed_backcast`. They move reported-ADR dilution, not GBV, so nothing in the
   revenue build depends on them.
8. **Quarterly seats allocation is proportional to printed nights**, so the dilution
   output is constant within a year. The seats note itself says the true pattern is
   summer-heavy. Not correctable without a disclosure.

## 9. Not built, by instruction

The joint hedonic (the existing WTP coefficient file is richer, and the quote
line-items file is 76 aggregate rows with no price, capacity, bedroom or LOS
column); the 120-market panel; separate price and sub-mix states (exactly
collinear); a separate party-size driver (party size *is* the capacity index); the
1.67 regulation multiplier; any fix to new-business netting; any Stan or PyMC state
space; any Monte-Carlo-only or SARIMAX-only work.

## Harness change request

**HCR-1 — `window` has no legal value for a forecast quarter beyond 2026Q3.**
Harness v1.0 validates `window == "LIVE"` only for `quarter == 2026Q3`, so the FY27
objects this package is required to register (2026Q4, 2027Q1–2027Q4) are rejected
with `window=LIVE is inconsistent with quarter=2026Q4`. The rule is correct for
*backtested* windows but it makes every forward object beyond one quarter
unregisterable, and the FY27 object is named in the decisions document.

*Requested:* allow `window == "LIVE"` for any `quarter >= 2026Q3`, or add a
`window` value such as `FWD` for multi-quarter-ahead objects that score in nothing.

*Local workaround, applied:* the 2026Q3 rows are registered normally; the five
forward rows per object are written unchanged, in registry column format, to
`data/processed/forecast_methods/l1_reconciliation/l1_unregistered_fy27_revenue.csv`
and `..._fy27_growth.csv`, ready to be moved into the registry the moment the rule
changes. No second format was invented.

**HCR-2 (minor) — `calendar.csv` `guide_date` is an object/string column** while
`GUIDE_DATES_W1` is a list of `datetime.date`. `cal[cal.guide_date == pd.Timestamp(d)]`
silently returns an empty frame rather than raising, which cost a run. Suggest
parsing `guide_date` to `datetime64` in `load_calendar`, or documenting the dtype.

## Registered objects

| file | rows | what |
|---|---|---|
| `l1-reconciliation__revenue_contemporaneous.csv` | 44 | one-quarter-ahead revenue at each W1/W2 guide date, both replays. **Negative control** — see §7 |
| `l1-reconciliation__fy27_revenue.csv` | 1 | 2026Q3 revenue, LIVE at 2026-09-11 (the rest parked, HCR-1) |
| `l1-reconciliation__fy27_growth.csv` | 1 | the same on `revenue_yoy` |

## Fixes after verification (round 1)

Round-1 verification (`VERIFY_l1-reconciliation_r1.md`, verdict **PARTIAL**) found
no leakage and no fabricated number, but six items to tighten. All six are now
fixed. The package was re-run end to end:

```
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/l1_reconciliation/run.py
```

**Exit code 0, 150s.** All three registry files are **byte-identical** to the
pre-fix versions (`diff -q` clean on all three), which is itself the empirical
confirmation that fix 3 below was a hygiene fix and not a leakage fix.

| # | verifier item | what changed | effect on numbers |
|---|---|---|---|
| 1 | A6 framing compares a multi-year mean to a single most-recent observation | `run.py` A6 split into **A6a** (mean vs most-recent same-season observation, labelled as such) and **A6b** (mean vs the architect's own published **mean** λ_Q3 = 17.239, the only like-for-like comparison available). Note §3 rewritten. | none; A6a and A6b both PASS. A6b: 17.2394 vs 17.239, d = +0.0004pp |
| 2 | kernel-weight FY27 sensitivity quoted as $118M | now **computed in `run.py`** from `l1_fy27_revenue_grid.csv`, printed to the log, and written to the new `l1_kernel_weight_sensitivity.csv`, so the note can never drift from the grid again. Note corrected. | **$118M → $117M** (15,720.3 → 15,837.6, spread 117.3; 0.74% of revenue, 2.343pp of growth) |
| 3 | FX pp table inside the PIT refit built once from the full sample, not cut at `d−1` | `data.fx_pp_table()` gained an `as_of` argument implementing the harness FX rule: basket quarters contribute only if their **last calendar day is strictly before `as_of`**, and only intervals with `knowable_from <= as_of` contribute a disclosed pair. `pit_point()` now rebuilds the table at every guide date via `D.fx_pp_table(ivd, as_of=d)`. New helper `data.qend_date()`. | **none — all 44 registered PIT rows unchanged, file byte-identical.** That is the evidence for the verifier's reading: the ex-FX ADR constraint only ever fired on quarter pairs already inside the PIT quarter set, and the one-quarter-ahead projection never touched FX at all. The gap was real as code hygiene and is now closed before another package copies it. |
| 4 | "72 filed regional revenue cells" — 16 are exact back-outs | A1's own test string and note §2.1/§3 now say **"72 exact cells (56 filed + 16 exact Q4 back-out)"**, with the back-out derivation (FY 10-K minus nine-month 10-Q, L0 `reconciliation_max_abs_diff_musd` 0.0) stated. The composition is now printed in the acceptance-test detail and re-derived from the L0 file at run time, not hard-coded. | none |
| 5 | "16 **clean** annual nights cells" implies the other 8 are dirty | A2's test string and note §2.1/§3 now say the 16 are the cells **inside the fitted panel window**, and state explicitly that all 24 L0 annual cells are `basis=filed, included=True` and that FY2020/FY2021 are excluded only because they predate the 2022Q1 panel start. | none |
| 6 | ladder worst gap 7.3/4.1pp vs headline 8.25/4.57pp unreconciled | new paragraph in §2.2 explaining that the ladder fits ADR at **weight 1.0** (a genuine feasibility test) while the headline fit uses `W_CONF adr = 0.25` (lexicographic G2 priority). `run.py` now prints the caveat above the ladder and stamps an `adr_constraint_weight` column into `l1_feasibility_ladder.csv`. | none |

### Not fixed, and why

* **A8 still FAILS** and is reported as a failure, unchanged: the within-region
  ex-FX ADR term reproduces at +2.60 / +2.01 / +3.13pp against the ADR note's
  +3.10 / +3.44 / +3.41pp, worst gap −1.43pp in 2024. The cause is a different
  FX/within-region split between the two constructions, and that split is
  identified only to about ±1.4pp with the disclosures on disk. Closing it needs
  a regional FX decomposition the letters do not support. **Not papered over.**
* **The G2 fourth-class inconsistency stands** (no regional share assignment
  consistent with filed revenue + annual nights + nights growth reproduces the
  letters' regional ADR y/y integers under a constant or linearly drifting
  regional take rate). Per the addendum this is reported, not relaxed.
* **HCR-1 and HCR-2 remain open** — they are harness-level, and the verifier
  confirmed both by reading `windows.py` and `loaders.py` directly. The five
  forward FY27 rows per object stay parked in the `l1_unregistered_*` files in
  registry column format.
* **`include_same_day` (`knowable_from <= d`)** is left as-is. It is the
  harness's own ratified convention with a written rationale in `loaders.py`;
  changing it to the literal `<` reading is a harness-level decision, not an
  l1-reconciliation fix, and doing it unilaterally here would desynchronise this
  package from every other one.
* **Regional ADR levels remain weakly identified** (bootstrap ±15% against ±1pp
  on shares). Unchanged, and it is the reason only `gbv_musd` crosses the
  boundary.
