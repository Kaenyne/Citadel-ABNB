# B3 — FY27 revenue-growth decomposition, rebuilt so it cannot double count

> # ⚠ EXPLORATORY
>
> **Nothing in this note is a scored object.** `l1-reconciliation` registers nothing at
> annual horizon; harness format v1.0 has no annual slot and its only LIVE target quarter
> is 2026Q3. The FY27 number is an **out-of-sample projection of a projection** — at FY27
> horizon *both* lagged GBV terms in the kernel are themselves forecasts.
>
> **Quote the band, never the point.** FY27 revenue **$15,720.3M to $15,837.6M**, growth
> **+9.18% to +11.52%**, across the mandated kernel-weight band w ∈ [0.33, ⅔]
> (00_IMPLEMENTATION_DECISIONS.md §11.1). The weight moves **FY26 as well as FY27**, which
> is why 0.74% of revenue becomes **2.34pp of growth**. The "+0.09pp edge over the Street"
> exists **only at w = ⅔**; at w = 0.33 the same build is **−2.25pp behind** the Street.
>
> Package `l1-reconciliation-v2`. Run date 2026-09-11. Method name `l1-reconciliation-v2`;
> objects `fy27_revenue_v2`, `fy27_growth_v2`. Nothing under `l1_reconciliation/`,
> `data/processed/forecast_methods/l1_reconciliation/` or any existing registry file was
> modified. `harness/score.py` was not run.

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/l1_reconciliation_v2/run.py
```

Outputs: `data/processed/forecast_methods/l1_reconciliation_v2/` —
`fy27_decomposition_v2.csv` (the object), `fy27_adr_attribution_v2.csv`,
`fy27_kernel_band_v2.csv`, `fy27_street_edges_v2.csv`, `fy27_identity_check_v2.csv`,
`fy27_annual_object_v2.csv`, `run_log.txt`.

---

## 0. What was wrong, and what the fix is

RED_TEAM **F1** refuted the published table (`l1_fy27_growth_decomposition.csv`, 14 additive
lines summing to +11.52pp). Four separate defects, all confirmed here by recomputation:

| # | defect | recomputed |
|---|---|---|
| 1 | geographic mix (−1.09pp) and unit-size/LOS (+0.38pp) listed as separate additive contributors | both already inside the two big lines; net double count **−0.71pp** |
| 2 | the volume × price cross term omitted | **+0.2479pp**, missing |
| 3 | "kernel timing +0.1674pp, an identity" | a **residual**. The computed value at w = ⅔ is **+0.0117pp** |
| 4 | GBV-side lines sum to 10.5554pp against the model's own GBV growth 11.5111pp | **0.96pp** unexplained |

**The mechanism, named.** GBV growth has *two* exact factorisations, and v1 took one line
from each:

* **Basis A** (index basis) — fixed-**price** quantity index **Q = +8.2632%** × fixed-**quantity**
  price index **P = +3.0000%**. `(1.082632)(1.03) − 1 = 11.5111%`, the model's GBV growth to
  seven decimals. **Q is a fixed-price index, so geographic mix is already inside it.**
* **Basis B** (the L1 spine's own identity) — total Nights-and-Seats **g_N = +9.4558%** ×
  blended reported ADR **g_ADR = +1.8777%**. `(1.094558)(1.018777) − 1 = 11.5111%`. Here
  **geographic mix is inside the ADR line**, as an output of `ADR_blend = Σ_r s_r ADR_r`.

v1 published the **basis-A volume and price lines** and then added the **basis-B geographic
mix** and a unit-size/LOS line on top. That is the double count. It also dropped basis A's
cross term, so the closing plug came out at +0.1674pp rather than the true kernel effect of
+0.0117pp — exactly as F1's accounting says (`0.1674 = 0.2479 + 0.0117 − 0.0922`).

**v2 never mixes bases.** It publishes basis B (the spine's own identity, in which mix is an
output of the ADR line and can therefore be *attributed* under it at zero weight), states the
cross term explicitly, computes the kernel effect instead of solving for it, and fences the
four assumed lines outside the computed dollar.

---

## 1. The algebra

Three exact factors, nothing else carries weight:

```
(1)  GBV_q        ≡  N_q × ADR_blend,q                                    identity, by construction
(2)  1 + g_GBV    =  (1 + g_N) × (1 + g_ADR)                              exact
(3)  1 + g_rev    =  (1 + g_GBV) × (1 + κ_w)                              exact, κ COMPUTED
     κ_w          =  (1 + g_rev) / (1 + g_GBV) − 1
     Revenue_q    =  λ_s(q) × [ w·GBV_{q−1} + (1 − w)·GBV_{q−2} ]         the kernel
```

with, on the driver-base GBV path (which is **w-invariant** — the kernel weight moves the
*recognition* of GBV into revenue, never GBV itself):

```
GBV   FY26 104,400.1 → FY27 116,417.7 $M            g_GBV  = +11.511084 %
N     FY26    584.08 → FY27    639.30 M             g_N    =  +9.455783 %
ADR   FY26  178.7444 → FY27  182.1007 $             g_ADR  =  +1.877745 %

(1 + 0.09455783)(1 + 0.01877745) − 1 = 0.11511084   ✓ = g_GBV, to 1e−14
additive: +9.4558 + 1.8777 + cross(g_N·g_ADR) +0.1776 = +11.5111 pp
```

λ (recomputed from the KPI panel, w = ⅔, as v1 does): **Q1 12.6938 / Q2 13.7136 /
Q3 17.2394 / Q4 12.0298 %**. FY26 revenue uses the **printed** 1Q26 $2,678M and 2Q26 $3,608M;
3Q26, 4Q26 and all of FY27 are kernel.

**κ_w is computed, not a residual.** Both sides of (3) are built from λ and the GBV path;
nothing is solved for. Two named channels sit inside it: the *lag* channel (a λ-weighted
**lagged**-GBV base grows at a different rate than the calendar year: −0.070 to −0.092pp) and
the *print* channel (FY26 1H is the printed number, not the kernel's own: +0.080 to −1.999pp,
and this is what makes κ so w-sensitive).

| w | κ_w | of which lag | of which print | as pp of growth |
|---|---|---|---|---|
| 0.33 | −2.0909 % | −0.0923 | −1.9986 | **−2.3316pp** |
| 0.50 | −1.0371 % | −0.0809 | −0.9562 | **−1.1564pp** |
| **⅔** | **+0.0105 %** | −0.0698 | +0.0803 | **+0.0117pp** |

**Reproduction test** (`fy27_identity_check_v2.csv`): the multiplicative form, the additive pp
column and the model's own growth agree at every w to **max 2.3e−14 pp**, against the required
0.01pp. The v2 build also reproduces v1's `driver_base` revenue grid to **1.8e−12 $M**, so
nothing here is a different model — only a different, non-overlapping accounting of the same one.

---

## 2. Table 1 — the decomposition (`fy27_decomposition_v2.csv`)

Only the `COMPUTED_*` rows carry weight. pp of FY27 revenue growth.

| block | line | w = 0.33 | w = 0.50 | w = ⅔ | weight | basis |
|---|---|---:|---:|---:|---|---|
| COMPUTED_GBV | volume: total Nights-and-Seats (N) | +9.4558 | +9.4558 | +9.4558 | **YES** | computed |
| COMPUTED_GBV | price: blended **reported** ADR | +1.8777 | +1.8777 | +1.8777 | **YES** | computed |
| COMPUTED_GBV | cross term: volume × price | +0.1776 | +0.1776 | +0.1776 | **YES** | computed |
| **= GBV growth** (w-invariant) | | **+11.5111** | **+11.5111** | **+11.5111** | subtotal | computed |
| COMPUTED_REVENUE | kernel recognition / timing (lagged-GBV conversion) | −2.3316 | −1.1564 | +0.0117 | **YES** | computed |
| **= FY27 REVENUE GROWTH, COMPUTED** | | **+9.1795** | **+10.3547** | **+11.5228** | **TOTAL** | computed |
| ASSUMED | fee / take-rate migration (half weight) | +0.90 | +0.90 | +0.90 | **NO** | assumed |
| ASSUMED | new lines outside GBV (ads, Services excess) | +0.20 | +0.20 | +0.20 | **NO** | assumed |
| ASSUMED | regulation (dated DiD on EMEA nights) | −0.30 | −0.30 | −0.30 | **NO** | assumed |
| ASSUMED | hedge (**dollars**, added ONCE by kernel-lambda) | 0.00 | 0.00 | 0.00 | **NO** | assumed |
| **= assumed block, total** | | **+0.80** | **+0.80** | **+0.80** | **NO** | assumed |
| ATTRIBUTION | 10 rows, see Table 2 | 0.00 | 0.00 | 0.00 | **ZERO** | attribution |

**The four assumed lines are not in the computed $15,837.6M.** The grid revenue is
`λ × lagged GBV` and nothing else. They are published separately and never added silently.

**COMPUTED vs COMPUTED + ASSUMED, both shown:**

| w | FY27 **computed** | growth | FY27 **incl. assumed as carried** (+0.80pp) | FY27 **incl. assumed at θ = 0.833** (+0.49pp) |
|---|---:|---:|---:|---:|
| 0.33 | $15,720.3M | +9.18 % | $15,835.4M (+9.98 %) | $15,790.8M (+9.67 %) |
| 0.50 | $15,779.5M | +10.35 % | $15,893.9M (+11.15 %) | $15,849.6M (+10.84 %) |
| **⅔** | **$15,837.6M** | **+11.52 %** | **$15,951.2M (+12.32 %)** | **$15,907.2M (+12.01 %)** |

**The fee line restated.** +0.90pp is carried from 00_IMPLEMENTATION_DECISIONS.md §8.1 and does
not state whether it embeds the pass-through correction (§11.6 says so explicitly).
`fee-takerate` recomputes it from primitives: at half weight it is **+0.36pp** (11.5pp-jump case)
to **+0.59pp** (central θ = 0.833) — i.e. the +0.90pp line is **0.31pp too generous**, and is
consistent either with a corrected step at ~77% weight or an uncorrected θ = 1 step at ~38%.

> **A warning that belongs on the exhibit.** `fee-takerate` also finds that at central θ the
> migration subtracts **−0.62pp from FY27 GBV growth**. The computed GBV build above does
> **not** carry that −0.62pp. So adding the fee line on top of this GBV build is itself a
> disguised double count unless the GBV side is restated. Stated here rather than netted.

---

## 3. Table 2 — the ADR attribution block (`fy27_adr_attribution_v2.csv`)

**ZERO WEIGHT IN THE TOTAL.** Every line below is already inside the ADR line of Table 1.
It exists to say *what the ADR line is made of*, not to add anything to anything.

| level | line | pp of the ADR line | basis | source |
|---|---|---:|---|---|
| L1 | geographic mix (OUTPUT of `ADR_blend = Σ_r s_r ADR_r`) | **−1.0896** | computed output | this build's own share identity; cross-validated in `l1-reconciliation` §4 against the 10-K Geographic Mix table and the ADR note to ≤0.14pp. Plan carries −1.5pp, ADR note −1.6pp (2025); **observed 2026 H1 is only −0.34pp**, so −1.09 may itself be too negative |
| L1 | within-region price (reported basis) | +3.0000 | computed output | driver-base sets every region's ADR y/y to +3.00% ex-FX, FX on a flat-spot carry |
| L1 | mix × price cross | −0.0327 | computed output | `g_ADR − mix − within` |
| **L1** | **= ADR LINE (blended reported ADR growth)** | **+1.8777** | computed | the three L1 rows sum to this, exactly |
| L2 | unit-size mix (bedroom elasticity **0.23**) | +0.63 | measured | `research/notes/2026-09-07_adr-decomposition.md` §0.3, direct measurement on **29 markets**; the Street's +2pp bedroom-nights → +2pp ADR mapping is **not** used |
| L2 | LOS mix | +0.04 | measured | same note §0, via `01_ground-truth/01_data_inventory.md` line 160. The ADR workbook's rival +0.30pp LOS term is a different construction (`02_model_audit.md` line 142) and is **not** mixed in |
| L2 | seats / hotel dilution (OUTPUT of `N = n_home + n_hotel + s_exp + s_svc`) | −0.50 | structure measured, ticket prices assumed | 00_IMPLEMENTATION_DECISIONS.md §8.1 / `research/notes/2026-09-09_seats-dilution.md`. **Nets to zero in GBV and in revenue** — it moves reported ADR and the unit count in opposite directions. The v2 FY27 build itself carries **0.00** here because non-home composition is held flat through 2027; −0.50 is the plan's y/y assumption. The measured 2026 *level* of dilution is −3.52pp |
| L2 | booking-date FX carried through Φ | 0.00 | flat-spot carry (assumption) | `l1-reconciliation` §6: FX inputs end 2026Q3, so 2027 runs on zero y/y. **Rival reading: `fx-lag` says +0.2pp** (OPTIMAL_MIX §4.4). Already inside the lagged USD GBV base; **never** added to revenue a second time |
| L2 | **like-for-like price + sub-regional mix (IDENTIFIED REMAINDER)** | **+2.83** | unidentified 2-d ridge | within-region price **minus** the four named L2 measurements. **NOT SPLIT** — separate price and sub-regional-mix states are exactly collinear (§8.2). It lands at +2.83pp against the plan's **+2.9pp**, which is corroboration, not a second estimate |
| **L2** | **= within-region price line** | **+3.0000** | computed | the five L2 rows sum to this, exactly |

Two closures hold by construction and are checked in code: the L1 rows sum to the ADR line,
and the L2 rows sum to the within-region price line. Nothing in this table is added to FY27
growth anywhere.

---

## 4. Table 3 — the kernel-weight band, the Street edge and the multiple

`fy27_kernel_band_v2.csv`, `fy27_street_edges_v2.csv`. Street-implied growth is each vendor's
**own** FY27 ÷ **own** FY26, so no vintage is mixed across the ratio.

| w | FY26 rev $M | FY27 rev $M | FY27 growth | GBV growth | κ_w |
|---|---:|---:|---:|---:|---:|
| 0.33 | 14,398.5 | 15,720.3 | **+9.18 %** | +11.51 % | −2.09 % |
| 0.50 | 14,298.9 | 15,779.5 | **+10.35 %** | +11.51 % | −1.04 % |
| **⅔ (published)** | **14,201.2** | **15,837.6** | **+11.52 %** | +11.51 % | +0.01 % |

Growth edge = our growth − vendor-implied growth. Turns at **+0.48 EV/EBITDA turns per point
of forward growth, applied ONCE** (OPTIMAL_MIX §4.5).

| vendor | as of | FY26 / FY27 $M | implied growth | edge at w = ⅔ | turns | edge at w = 0.50 | edge at w = 0.33 | turns at 0.33 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Zacks | 4 Sep 2026 | 14,130 / 15,745 (mids) | +11.430 % | **+0.093pp** | **+0.045** | −1.075pp | **−2.250pp** | −1.080 |
| Zacks | 11 Sep 2026 | 14,100 / 15,740 (n=13) | +11.631 % | −0.108pp | −0.052 | −1.277pp | −2.452pp | −1.177 |
| Alpha Vantage (LSEG) | 11 Sep 2026 | 14,155.1 / 15,757.8 (n=44) | +11.322 % | +0.200pp | +0.096 | −0.968pp | −2.143pp | −1.029 |
| Yahoo (LSEG) | 11 Sep 2026 | 14,160 / 15,790 (n=43) | +11.511 % | +0.012pp | +0.006 | −1.157pp | −2.332pp | −1.119 |
| S&P Global MI | 10 Sep 2026 | 14,160 / 15,770 | +11.370 % | +0.153pp | +0.073 | −1.015pp | −2.191pp | −1.051 |

Level edge runs **+0.30% to +0.62%** across the five anchors at w = ⅔ and **−0.44% to −0.13%**
at w = 0.33 — on the FY27 *level* we are the Street either way. Alpha Vantage and Yahoo are
**one LSEG-family panel surfaced twice** (A1 §2 caveat 1); count them once.

**The uncomfortable ratio, said out loud.** The kernel-weight indeterminacy is worth
**2.34pp of growth = ±1.12 turns**, against a level edge over the Street of **+0.09pp = +0.045
turns**. The indeterminacy is ~25× the edge. That is the single most important sentence in this
note and it is an argument for pitching the *composition*, not the level.

**Predictive interval** (`sd` on the registered objects), three components in quadrature:

| component | FY27 revenue | FY27 growth |
|---|---:|---:|
| kernel-weight band (q10 set to reach w = 0.33) | $91.5M | 1.828pp |
| L1 block-bootstrap, composition channel, 4,000 draws seed 20260911 | $6.0M | **0.042pp** |
| kernel strict-PIT walk-forward error (MAPE 2.313%, ×√(π/2)) | $459.1M | 3.19–3.23pp |
| **total** | **$468.2M** | **3.68–3.71pp** |

q10/q90 therefore **more than span** the w band at every weight. The bootstrap term is small
*because it is honest about its channel*: quarterly total GBV is pinned by the letters, so the
published block bootstrap prices **composition**, not level — FY27 GBV growth p10/p50/p90
+11.456 / +11.511 / +11.564%. The kernel's own out-of-sample error dominates, and the strict-PIT
2.313% is used rather than the widely-quoted 1.74%, which RED_TEAM §6 shows is the
full-sample-prior replay, not a walk-forward.

---

## 5. Registration

`data/processed/forecast_methods/registry/l1-reconciliation-v2__fy27_revenue_v2.csv` and
`...__fy27_growth_v2.csv`. Method **`l1-reconciliation-v2`** — new files under a new method
name; no existing registry file was read-modified-written. `window = LIVE`,
`vintage_date = 2026-09-11`, `prior_basis = full_sample`, `knowable_from = 2026-09-11`,
`n_params = 84`, `n_train = 24`, full `q05/q10/q25/q50/q75/q90/q95` ladder.

Six rows each, the forward quarterly path 2026Q3 → 2027Q4. **The FY27 annual object is the sum
of the four 2027 rows**; the two 2026 rows are the FY26 base and are labelled as such in
`notes`, precisely so that the RED_TEAM complaint against v1 (`fy27_revenue.csv` holding a
single 2026Q3 row of 4,804.0 under an object called `fy27_revenue`) cannot recur. The annual
object itself is parked at `fy27_annual_object_v2.csv`.

### Harness change request

**Add an annual / multi-quarter LIVE slot.** Format v1.0 derives `LIVE_TARGETS` from
`GUIDE_EVENTS_ALL`, so the only legal LIVE quarter is **2026Q3** and there is no representation
for an annual period at all. v2 therefore registers with `strict_windows=False` — a sanctioned
argument of `register()`, used deliberately and disclosed here — so that every row's `quarter`
means what it says. This is RED_TEAM harness change request 5, restated with a concrete object
behind it. Two secondary requests, both already on RED_TEAM's list and both biting here:
`fy27_*` can publish only one `prior_basis` (there is no PIT replay of a forward-only object),
and LIVE rows are scored in nothing, so `survives_both_windows = False` on them must never be
read as "tested and failed".

---

## 6. What the memo may say — and it is about composition, not level

> **On the FY27 level we are the Street, and the memo says so in its first 200 words.** Our
> FY27 is **$15,720–15,838M** against a Street of **$15,740–15,790M**; at the published kernel
> weight the growth edge over the 4 Sep Zacks vintage is **+0.09pp**, worth **0.045 EV/EBITDA
> turns**, and the kernel-weight indeterminacy alone is worth **2.34pp and ±1.12 turns** — 25
> times more. Anyone who claims a level edge here is claiming something they cannot defend.
> **The variant view is compositional.** Run the FY27 number through the identity
> `GBV ≡ nights × blended ADR` and the Street's +11.4% is made of things the Street reads as
> price strength and we read as arithmetic: blended ADR contributes only **+1.88pp** of the
> +11.51pp of GBV growth, and inside that ADR line **geographic mix is −1.09pp** — an *output*
> of the share identity, not a lever, and deepening as North America's share of
> Nights-and-Seats slides; the bedroom-nights disclosure the Street maps 1:1 into ADR is worth
> **+0.63pp at an elasticity of 0.23, not +2pp**; LOS adds **+0.04pp**; seats and hotel dilution
> move reported ADR and the unit count in opposite directions and **net to zero in revenue**, so
> anyone carrying a seats line into a revenue build is double counting. What is left —
> **+2.83pp of like-for-like price and sub-regional mix** — is a jointly unidentified 2-d ridge
> and we refuse to split it, because Airbnb discloses no country-level ADR. And the four lines
> the sell side would quote as drivers — fee migration **+0.9pp**, new lines **+0.2pp**,
> regulation **−0.3pp**, hedge **0.0** — are **assumed, and are not inside our computed
> $15,837.6M**; restated at the pass-through our own fee work supports (θ ≈ 0.83) the fee line
> is **+0.36 to +0.59pp**, not +0.9pp, and on the same arithmetic the migration also takes
> **−0.62pp off GBV growth**, which nobody has carried. **Same dollar, different derivative.**
> Composition is what moves the Feb-2027 guide and the multiple; the level is what a judge
> checks in ninety seconds and finds us agreeing with consensus.

### Caveats, all of them

1. **λ is estimated at w = ⅔ and then held fixed across the w grid.** That is v1's convention,
   reproduced here so the two grids are comparable. A self-consistent re-fit of λ at each w
   would shrink the band; the band as published is therefore an **upper bound** on the
   kernel-weight effect, not a calibrated interval.
2. **FY27 booking-date FX is a flat-spot carry, not a measurement**, and it is the single
   largest unmodelled risk in the line. `fx-lag` reads the same object at **+0.2pp**.
3. **Geographic mix −1.09pp may be too negative.** Observed 2026 H1 is −0.34pp. The plan's
   −1.5pp is roughly four times the currently observed drag.
4. **Unit size rests on n = 1 disclosed quarter** for the bedroom-nights wedge, and the +0.63pp
   L2 figure comes from the 29-market ADR panel, a *different* estimator from v1's
   wedge × elasticity +0.38pp. They are not averaged; the L2 block is attribution, so the
   remainder absorbs the difference and the total is untouched either way.
5. **The `data_only` continuation scenario is not carried here.** It runs $300–400M hotter on a
   trailing-4 ADR line ~2.5× the driver model's; reported in `l1-reconciliation` §6 as a result,
   not believed as a forecast, and excluded from the v2 object rather than blended into it.
6. **2027Q2 is the wide quarter.** Its w band alone is $3,578M → $4,037M, which is why its
   registered growth interval is much wider than its neighbours'. That is the lag structure
   biting on a seasonal turn, not an error.
7. **No consensus number enters any forecast.** The Street anchors appear only in the edge
   table, each vendor-stamped, and `street_as_of ≤ vintage_date` holds for all five.
