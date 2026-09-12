# B2 — the 5 Nov 2026 4Q26 guide midpoint, as a distribution

**The three independent consensus panels disagree by $42M on 4Q26.** Zacks says $3,200M on
ten estimates; the LSEG/Refinitiv-family panel says $3,158M on thirty-six (and $3,160M on
thirty-five when the same feed is surfaced through Yahoo Finance); S&P Global Market
Intelligence says $3,160M on thirty-five. The whole guide-below-Street trade lives inside
that $42M, so no single probability can be quoted without naming the vendor, the panel
size and the timestamp.

This note answers **RED_TEAM fatal finding F2**: every 4Q26 number in the programme was
anchored on `GBV_3Q26 = $26,300M`, the architect's hand-set central case, while the
programme's own combined 3Q26 GBV forecast is **$26,549.8M**. Rather than swap one point
input for another, the object is republished as a **distribution**: the 4Q26 guide
midpoint integrated over the programme's own GBV_3Q26 forecast, with three vendor-stamped
anchors and both cushion conventions shown side by side.

Package `guidance-policy-v2`. Code `analysis/src/forecast_methods/guidance_policy_v2/`
(copies of `guidance_policy/lib.py`, `kernel_lambda/kernel.py`, `tracker_backlog/common.py`
and `fee_takerate/fee_schedule.py`, modified). Data
`data/processed/forecast_methods/guidance_policy_v2/`. Registry
`guidance-policy-v2__gbv_musd_live.csv`, `__q4_2026_guide_mid_v2.csv`,
`__q4_2026_print_v2.csv`. **No existing file was modified. 16/16 acceptance tests pass.**

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/guidance_policy_v2/run.py
```

---

## 1. The anchors — vendor, panel size, timestamp

| anchor | value | n est. | as-of | register id |
|---|---|---|---|---|
| **LSEG-family** (Alpha Vantage; same panel via Yahoo Finance $3,160M, n=35) | **$3,158M** | 36 | **11 Sep 2026** | `CU-2026Q4-revenue-AlphaVantage` / `CU-2026Q4-revenue-Yahoo-20260911` |
| **S&P Global Market Intelligence** (via StockAnalysis) | **$3,160M** | 35 | **10 Sep 2026** | `CU-2026Q4-revenue-SPGlobal-20260910` |
| **Zacks** | **$3,200M** | 10 | **11 Sep 2026** (unchanged vs 4 Sep) | `CU-2026Q4-revenue-Zacks-20260911` |

Yahoo and Alpha Vantage are **one** panel, not two: their 4Q26 high/low agree to the
dollar and their revision counts are identical (A1_consensus_vintages.md §2). Counting
them separately would fake agreement. Zacks is simultaneously the **highest** print and
the **thinnest** panel, and it is the only one of the three above $3,160M.

Also on the exhibit, and said first: Zacks' own quarterly sum
(2,678 + 3,608 + 4,740 + 3,200 = **$14,226M**) disagrees with its own FY26 consensus of
**$14,100M** by **$126M** — three times the inter-vendor spread and larger than our edge.

## 2. The live 2026Q3 GBV base — now a registered object, not a hand-set input

`guidance-policy-v2__gbv_musd_live.csv` registers the combined 3Q26 GBV forecast as a LIVE
`gbv_musd` row so every downstream growth target has a live base:

| | value |
|---|---|
| point / q50 | **$26,549.8M** (y/y +15.94%) |
| q10 / q90 | $25,456.3M / $27,643.2M |
| fitted sd | **853.2** |
| source | `optimal_mix/combined_live_objects.json` → `live_3Q26_gbv_musd`, scheme `stack_shrunk`, pool `all`, STATUS OK, weight coverage 1.0 |

**Distribution fitted: NORMAL.** The published ladder is *exactly* symmetric —
q90 − q50 = q50 − q10 = 1,093.43 = 1.2816 × 853.21, asymmetry −4.6e−06pp. A skew-normal
has one more free parameter than there is evidence to identify it with; its fitted shape
parameter here is zero by construction, so the normal is the honest choice and the
skew-normal would be decoration.

> **The published $25,900–27,000M grid does not bracket the programme's own GBV forecast.**
> q10 = $25,456M sits **below** the grid floor and q90 = $27,643M sits **above** the ceiling;
> the twelve even grid steps carry only **47.8%** of the unconditional GBV mass. That is why
> the unconditional numbers in §5 integrate the continuous normal rather than re-weighting
> the twelve cells. The `gbv_weight_on_even_grid` column in the grid file is shown for
> transparency and is explicitly a **truncated** weight.

## 3. The two choices

### 3.1 Predictive sd — **3.03pp**, conditional on GBV

**I use 3.0305pp for the guide midpoint, because it is the walk-forward
decomposition of exactly the two error sources that survive once GBV_3Q26 is fixed: the
kernel object's own W1 point-in-time walk-forward RMSE of 2.8591% of level
(`guidance_policy/07_backtest_scores.csv`, `print_kernel_policy`, n = 14) combined in
quadrature with the trailing-8 cushion sd of 1.0048pp, which is the draw that turns a
print into a guide midpoint. The optimal-mix 2.73% is a *no-guide ensemble* revenue-level
RMSE that contains no cushion term at all and is carried by methods (naive, AR(1),
trailing-4) other than the one being published, so it is narrower for the wrong reason —
it is shown as a sensitivity row in §6 and it moves no conclusion.**

Two consequences worth stating. (i) The 3.03pp is **conditional**; the GBV uncertainty is
added by the integration in §5, not double-counted, because the kernel walk-forward is
measured at guide dates where the lagged GBV base had already printed. (ii) The **print**
object correctly carries 2.8591pp, not 3.03pp — the cushion is the print→guide step and
does not belong in the print's own interval. The v1 exhibit applied 3.03pp to both; that is
corrected here.

### 3.2 Fee-step arithmetic — **the primitives-based one**

| arithmetic | step | print at GBV 26,300 |
|---|---|---|
| primitives, theta=0.83, HALF step (CHOSEN) | +0.5543% | 3,217.7 |
| primitives, theta=0.83, FULL step (sensitivity) | +1.1086% | 3,235.4 |
| architect HALF weight (v1 exhibit, REJECTED) | +1.2500% | 3,239.9 |
| architect FULL weight (v1 exhibit, REJECTED) | +2.5000% | 3,279.9 |

**Chosen: primitives.** The architect's ±1.25% / ±2.50% is a flat multiplier with no θ and
no migrated share in it — it is an assumption wearing the clothes of arithmetic, and
`fee-takerate` A14 shows it is roughly double what the primitives produce. The primitives
route runs through the copied `fee_schedule.py`, at θ = 0.83 in **repo units**
(jump ÷ 13.8; = 0.774 in payout-neutral units), and is carried at half weight per
`00_IMPLEMENTATION_DECISIONS.md` §7.2; at fee-takerate's own θ = 0.8333 it reproduces that
package's `07b` print of **$3,218.2M** to $0.05M (acceptance test C1).

**The uplift used, stated explicitly.** At θ = 0.83 the listed price rises ×1.1228, the
migrated cohort's take rate goes 14.987% → 15.500%, its GBV **falls -1.597%** and its
host payout **falls -2.191%**, so its revenue rises **+1.773%**. Per $1 of
*pre-migration* migrated GBV that is **+26.6 bp of revenue** — not the +51 bp the naive
take-rate delta suggests, because the GBV denominator shrinks. Multiplied by the
Φ-weighted 4Q26 migrated **revenue** share of **0.6254** that is a full step of
**+1.1086%**, carried at half weight: **+0.5543%**.

Note what this does to the v1 framing: the primitives **full** step (+1.1086%) is
*smaller* than the architect's **half** step (+1.25%). The half-weight haircut was doing
more work than the entire fee mechanism.

## 4. The grid

`GBV_3Q26` $25,900–27,000M in $100M steps, plus the three named points. Mechanics:
`print = λ_Q4 × [⅔ GBV_3Q26 + ⅓ 27,200] × (1 + fee step)`, λ_Q4 = **12.0298%**
(4Q23 11.946 / 4Q24 12.117 / 4Q25 12.026, within-season range 0.171pp);
`guide mid = print ÷ (1 + c)` with **c = 1.8567% (mean, ÷1.0186)** and
**c = 1.7905% (median, ÷1.0179)**; guide range at the trailing-8 mean width
1.859% of the midpoint (the 1.7%–2.2% band is in the CSV as `*_w170_*` / `*_w220_*`).
`P(·)` are conditional on that GBV cell, at sd 3.03pp, on the **mean-cushion** midpoint.

Full file: `data/processed/forecast_methods/guidance_policy_v2/q4_2026_guide_grid.csv` (28 rows).

| GBV_3Q26 | wt. | base | **print** | **guide (÷1.0186)** | guide (÷1.0179) | range | P<LSEG 3,158 | P<S&P 3,160 | P<Zacks 3,200 | **print** | **guide (÷1.0186)** | guide (÷1.0179) | range | P<LSEG | P<S&P | P<Zacks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | *no fee step* | | | | | | | *θ = 0.83 fee step* | | | | | | |
| 25,900.0  | 0.068 | 26,333 | 3,167.8 | 3,110.1 | 3,112.1 | 3,081–3,139 | 0.694 | 0.702 | 0.830 | 3,185.4 | 3,127.3 | 3,129.4 | 3,098–3,156 | 0.627 | 0.635 | 0.778 |
| 26,000.0  | 0.074 | 26,400 | 3,175.9 | 3,118.0 | 3,120.0 | 3,089–3,147 | 0.664 | 0.672 | 0.807 | 3,193.5 | 3,135.3 | 3,137.3 | 3,106–3,164 | 0.595 | 0.603 | 0.752 |
| 26,100.0  | 0.079 | 26,467 | 3,183.9 | 3,125.8 | 3,127.9 | 3,097–3,155 | 0.633 | 0.641 | 0.783 | 3,201.5 | 3,143.2 | 3,145.2 | 3,114–3,172 | 0.562 | 0.570 | 0.725 |
| 26,185.0 *frozen card* |  | 26,523 | 3,190.7 | 3,132.5 | 3,134.6 | 3,103–3,162 | 0.606 | 0.614 | 0.761 | 3,208.4 | 3,149.9 | 3,152.0 | 3,121–3,179 | 0.534 | 0.542 | 0.700 |
| 26,200.0  | 0.083 | 26,533 | 3,191.9 | 3,133.7 | 3,135.8 | 3,105–3,163 | 0.601 | 0.609 | 0.757 | 3,209.6 | 3,151.1 | 3,153.1 | 3,122–3,180 | 0.529 | 0.537 | 0.696 |
| 26,300.0 **architect input** | 0.087 | 26,600 | 3,199.9 | 3,141.6 | 3,143.6 | 3,112–3,171 | 0.568 | 0.577 | 0.730 | 3,217.7 | 3,159.0 | 3,161.1 | 3,130–3,188 | 0.496 | 0.504 | 0.666 |
| 26,400.0  | 0.089 | 26,667 | 3,207.9 | 3,149.5 | 3,151.5 | 3,120–3,179 | 0.536 | 0.544 | 0.702 | 3,225.7 | 3,166.9 | 3,169.0 | 3,137–3,196 | 0.463 | 0.471 | 0.635 |
| 26,500.0  | 0.091 | 26,733 | 3,216.0 | 3,157.3 | 3,159.4 | 3,128–3,187 | 0.503 | 0.511 | 0.672 | 3,233.8 | 3,174.8 | 3,176.9 | 3,145–3,204 | 0.431 | 0.439 | 0.603 |
| 26,549.8 **own forecast** |  | 26,767 | 3,220.0 | 3,161.3 | 3,163.3 | 3,132–3,191 | 0.486 | 0.495 | 0.657 | 3,237.8 | 3,178.8 | 3,180.9 | 3,149–3,208 | 0.415 | 0.423 | 0.587 |
| 26,600.0  | 0.091 | 26,800 | 3,224.0 | 3,165.2 | 3,167.3 | 3,136–3,195 | 0.470 | 0.478 | 0.642 | 3,241.9 | 3,182.8 | 3,184.8 | 3,153–3,212 | 0.399 | 0.407 | 0.571 |
| 26,700.0  | 0.089 | 26,867 | 3,232.0 | 3,173.1 | 3,175.2 | 3,144–3,203 | 0.438 | 0.446 | 0.610 | 3,249.9 | 3,190.7 | 3,192.8 | 3,161–3,220 | 0.368 | 0.376 | 0.538 |
| 26,800.0  | 0.087 | 26,933 | 3,240.0 | 3,181.0 | 3,183.0 | 3,151–3,211 | 0.406 | 0.414 | 0.578 | 3,258.0 | 3,198.6 | 3,200.7 | 3,169–3,228 | 0.338 | 0.345 | 0.506 |
| 26,900.0  | 0.083 | 27,000 | 3,248.0 | 3,188.8 | 3,190.9 | 3,159–3,218 | 0.375 | 0.383 | 0.546 | 3,266.0 | 3,206.5 | 3,208.6 | 3,177–3,236 | 0.309 | 0.316 | 0.473 |
| 27,000.0  | 0.079 | 27,067 | 3,256.1 | 3,196.7 | 3,198.8 | 3,167–3,226 | 0.345 | 0.352 | 0.514 | 3,274.1 | 3,214.4 | 3,216.5 | 3,185–3,244 | 0.281 | 0.288 | 0.441 |

## 5. The unconditional distribution

GBV_3Q26 ~ N(26,549.8, 853.2) integrated out on a 4,001-point grid spanning ±8 sd;
the guide midpoint is a normal mixture, its quantiles inverted from the mixture CDF.

**Guide midpoint, 5 Nov 2026:**

| fee treatment | cushion | **mean** | median | **80% interval** | total sd | **P<LSEG $3,158** | **P<S&P $3,160** | **P<Zacks $3,200** |
|---|---|---|---|---|---|---|---|---|
| no fee step | ÷ 1.0186 (mean) | 3,161.3 | 3,160.3 | 3,011.9 – 3,311.8 | 117.0 (3.70%) | 0.492 | 0.499 | 0.632 |
| no fee step | ÷ 1.0179 (median) | 3,163.3 | 3,162.4 | 3,013.9 – 3,314.0 | 117.1 (3.70%) | 0.485 | 0.492 | 0.626 |
| fee step, θ = 0.83 (primitives, half) | ÷ 1.0186 (mean) | 3,178.8 | 3,177.8 | 3,028.6 – 3,330.2 | 117.7 (3.70%) | 0.433 | 0.440 | 0.575 |
| fee step, θ = 0.83 (primitives, half) | ÷ 1.0179 (median) | 3,180.9 | 3,179.9 | 3,030.6 – 3,332.4 | 117.8 (3.70%) | 0.426 | 0.433 | 0.568 |

**Print (4Q26 revenue), for completeness — never conflate it with the guide; they differ by 1.86%:**

| fee treatment | mean | 80% interval | sd | P<3,158 | P<3,160 | P<3,200 |
|---|---|---|---|---|---|---|
| no fee step | 3,220.0 | 3,073.5 – 3,367.6 | 114.7 | 0.297 | 0.303 | 0.434 |
| fee step, θ = 0.83 (primitives, half) | 3,237.8 | 3,090.6 – 3,386.2 | 115.4 | 0.246 | 0.251 | 0.374 |

Integrating the GBV forecast widens the guide-midpoint sd from **3.03% conditional to
3.70% unconditional** ($95.8M → $117.0M). That is the honest cost of not knowing
GBV_3Q26 at the pitch date, and it is the number the v1 exhibit never carried.

## 6. Sensitivities

**Predictive sd** (guide midpoint, mean cushion):

| fee treatment | sd | mean | 80% interval | P<LSEG | P<S&P | P<Zacks |
|---|---|---|---|---|---|---|
| no fee step | **3.03pp (chosen)** | 3,161.3 | 3,011.9 – 3,311.8 | 0.492 | 0.499 | 0.632 |
| no fee step | 2.73pp (sensitivity) | 3,161.3 | 3,021.7 – 3,302.0 | 0.491 | 0.499 | 0.641 |
| θ = 0.83 fee step | **3.03pp (chosen)** | 3,178.8 | 3,028.6 – 3,330.2 | 0.433 | 0.440 | 0.575 |
| θ = 0.83 fee step | 2.73pp (sensitivity) | 3,178.8 | 3,038.4 – 3,320.3 | 0.428 | 0.435 | 0.580 |

The 2.73pp alternative moves every unconditional probability by **less than 1pp** — because
at the unconditional level the GBV variance dominates the conditional variance. The
sd debate that occupied v1 and OPTIMAL_MIX turns out not to matter once GBV is integrated;
the fee-step choice and the vendor choice both matter far more.

**Fee-step arithmetic:** the primitives full step (+1.1086%) would add ~$17M to the
guide midpoint over the half step; the architect's half step (+1.25%) would add ~$22M and
its full step (+2.50%) ~$61M. Those are the rows to interrogate if anyone quotes a
probability below 0.45.

## 7. The two named points, side by side

Conditional on the GBV cell, mean cushion, sd 3.03pp. **print / guide mid** in $M.

| fee treatment | 26,300 (architect) | P<Zacks | P<S&P | P<LSEG | 26,549.8 (own forecast) | P<Zacks | P<S&P | P<LSEG | 26,185 (frozen card) | P<Zacks |
|---|---|---|---|---|---|---|---|---|---|---|
| no fee step | 3,199.9 / 3,141.6 | 0.730 | 0.577 | 0.568 | 3,220.0 / 3,161.3 | 0.657 | 0.495 | 0.486 | 3,190.7 / 3,132.5 | 0.761 |
| θ = 0.83 fee step | 3,217.7 / 3,159.0 | 0.666 | 0.504 | 0.496 | 3,237.8 / 3,178.8 | 0.587 | 0.423 | 0.415 | 3,208.4 / 3,149.9 | 0.700 |

**The headline pair is 0.73 versus 0.66.** Swapping the architect's hand-set GBV for the
programme's own forecast moves the guide midpoint **+$19.7M** and cuts P(guide < Zacks)
from **0.730 to 0.657**; against the two thirty-plus-analyst panels it falls from **0.57/0.58
to 0.49/0.50** — i.e. straight through a half. Add the primitives fee step and the pair
becomes **0.67 / 0.59** against Zacks and **0.50 / 0.42** against the broad panels. The
architect's input is not neutral: it is the single most favourable GBV in the named set
apart from the frozen card, and the frozen card is more favourable still (0.761).

## 8. What the memo may say

The 4Q26 guide is a **distribution, not a call**. On the programme's own 3Q26 GBV forecast
and its own recognition kernel, the 5 Nov guide midpoint centres on **$3,161M with no fee
step and $3,179M with the fee step measured from primitives at θ = 0.83**, with an 80%
interval of roughly **$3,012–3,312M** and **$3,029–3,330M** — an interval wide enough to
contain all three Street anchors and both fee treatments. Against that distribution the
guide lands below **Zacks' $3,200M (10 estimates, 11 Sep)** with probability **0.63 with no
fee step and 0.57 with it**, and below the two thirty-plus-analyst panels — **LSEG-family
$3,158M (36 est., 11 Sep)** and **S&P Global MI $3,160M (35 est., 10 Sep)** — with
probability **0.49/0.50 with no fee step and 0.43/0.44 with it**. In plain English: the guide
is *likely* to come in under the thin, high Zacks number and is a genuine **coin toss**
against the two broad panels, and the whole apparent edge is the $42M by which the panels
disagree with each other — which is itself smaller than the $126M by which Zacks disagrees
with its own FY26 line. Anyone who states a single number here is quoting the vendor, not
the forecast. The variant view that survives all of this is **compositional, not
directional**: at θ < 1 the migrated cohort's GBV and the host's payout both *fall*, the fee
step is roughly half what the programme assumed, and the print–guide separation of 1.86%
is worth more than the entire fee mechanism.

## 9. Caveats

1. **The fee step moves revenue only; the GBV grid is held fixed.** At θ = 0.83 the migrated
   cohort's GBV falls -1.60%, so a GBV_3Q26 that already embedded the 3Q26 migration ramp
   would sit *lower* than the grid point paired with it. The fee-step column is therefore, if
   anything, slightly generous, and the no-fee column is the conservative read.
2. **θ is unidentified, not measured.** 0.83 is a histogram bin midpoint from a *voluntary*
   Austin sub-sample (`fee-takerate.md` §0); the mandatory cohort forced across by the 15 Sep
   and 13 Oct deadlines has not repriced. The migrated-share path is judgemental and dated,
   never fitted.
3. **The GBV object's own carriers are baselines.** `live_3Q26_gbv_musd` is a shrunk stack of
   naive (0.667), AR(1) (0.167) and trailing-4 (0.167). It is a better-supported number than a
   hand-set point, but it is not a structural GBV forecast, and its sd of $853M is what drives
   the unconditional interval.
4. **Anchors are means, not medians.** No vendor publishes a revenue median (A1 §1). Zacks'
   $3,200M mean carries a $3,700M high that is probably bad data; its median is nearer $3,150M,
   which would put it *with* the other two panels and remove the trade.
5. **`street_as_of` discipline held**: every anchor's timestamp (10–11 Sep) precedes the
   `vintage_date` of 11 Sep, so the harness validator accepts all three.
6. `harness/score.py` was **not** run, per the task. These are LIVE rows and score in nothing.

### Harness observation (not a change request)

`window_of_target("2026Q4")` returns `[]` — `WINDOW_MEMBERSHIP` has LIVE = 2026Q3 only — so a
4Q26 LIVE row cannot pass `strict_windows=True`. The v1 `guidance-policy` package registered
its 4Q26 objects with `strict_windows=False` and this package does the same. The 2026Q3 GBV
row passes strict validation unchanged. Flagging it so nobody reads the bypass as a shortcut.

### Files

| file | contents |
|---|---|
| `guidance_policy_v2/00_acceptance_tests.csv` | 16 tests, all pass |
| `guidance_policy_v2/01_inputs.csv` | λ_Q4, GBV_2Q26, both cushions, all three sds |
| `guidance_policy_v2/02_gbv_3q26_live.csv` | the LIVE GBV base and its normal-fit diagnostics |
| `guidance_policy_v2/03_fee_step_arithmetic.csv` | the four fee-step arithmetics side by side |
| `guidance_policy_v2/04_fee_primitives.csv` | the θ = 0.83 uplift, per $ of migrated GBV |
| **`guidance_policy_v2/q4_2026_guide_grid.csv`** | **the 28-row exhibit grid** |
| `guidance_policy_v2/05_unconditional.csv` | 12 unconditional rows (object × fee × sd × cushion) |
| `guidance_policy_v2/06_named_points.csv` | the three named GBV points |
| `guidance_policy_v2/07_anchors.csv` | the three vendor-stamped anchors |
| `registry/guidance-policy-v2__gbv_musd_live.csv` | LIVE 2026Q3 `gbv_musd` |
| `registry/guidance-policy-v2__q4_2026_guide_mid_v2.csv` | LIVE 2026Q4 `guide_mid`, unconditional quantiles |
| `registry/guidance-policy-v2__q4_2026_print_v2.csv` | LIVE 2026Q4 `revenue_musd`, unconditional quantiles |
