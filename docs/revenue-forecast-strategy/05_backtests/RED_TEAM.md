# RED_TEAM — adversarial audit of the overnight forecast programme

Run date 2026-09-11. Auditor: red-team agent, independent of every build package.
Scope: SCOREBOARD.md, OPTIMAL_MIX.md, 00_IMPLEMENTATION_DECISIONS.md, all 8 package notes,
all 11 VERIFY notes, the 57 registry files, `harness/scoreboard.csv`, and
`optimal_mix/combined_live_objects.json`.

**Method.** Nothing below is taken from a package note. Every number was recomputed from
source in two scratch scripts that import no package code:

- `rt_recompute.py` — rebuilds the entire scoreboard (actuals long-form from `targets.csv`,
  per-quarter naive matching, RMSE / MAE / bias / ratio) in pure pandas.
- `rt_fx.py` / `rt_fx2.py` — rebuilds the FX basket from `10_fx_daily.csv` (19,467 rows,
  9 FRED bilaterals), the judgement currency weights from `10_fx_basket.csv`, and
  trailing-4 filed regional revenue shares from `L0_exact_regional_revenue.csv`; then fits
  the lag-0/1/2 model by interval likelihood on the letter-rounded integers and runs the
  LR tests.

Both scripts live in `analysis/src/forecast_methods/red_team/`; commands in §11.

**Headline verdict: SOUND WITH FIXES.** The measurement machinery is genuinely good — the
harness, the PIT rules, the scorer and the FX estimation all reproduce independently and
exactly. The defects are concentrated in the *forward* objects the memo will actually
quote: the FY27 decomposition does not decompose the model it claims to decompose, the
4Q26 guide object is driven by a GBV input the programme's own forecast contradicts, the
three live 3Q26 objects are mutually inconsistent by 33bp of take rate, and the live FX
number is contradicted by management's own letter. All four are fixable before 2 Oct.

---

## 1. FATAL — must be fixed or struck before the memo

### F1. The FY27 growth decomposition double-counts, and its closing line is a residual mislabelled as an identity

`l1_fy27_growth_decomposition.csv` presents 14 additive lines summing to +11.52pp, with the
last line — "kernel timing (revenue is a convolution of LAGGED GBV), +0.1674pp" — described
as *"GBV growth minus revenue growth from the 2/3-1/3 lag; an identity, not a residual."*

Recomputed from the package's own `l1_fy27_revenue_grid.csv` (scenario `driver_base`,
kernel_w = 2/3):

| quantity | value |
|---|---|
| FY26 GBV (29,200 + 27,200 + 25,193.1 + 22,807.0) | 104,400.1 |
| FY27 GBV (32,751.6 + 30,204.0 + 27,932.7 + 25,529.4) | 116,417.7 |
| **GBV growth** | **+11.5111%** |
| **Revenue growth (grid)** | **+11.5228%** |
| **GBV growth − revenue growth** | **−0.0117pp** |

The claimed identity is **−0.012pp, not +0.167pp**. The line is a residual.

Worse, it is a residual that conceals a double count. Test:

```
(1 + volume 0.0826319) x (1 + ADR ex-FX 0.03) - 1 = 11.5111%
```

which is the model's FY27 GBV growth **to four decimals**. So the volume line and the
within-region ADR line, multiplied, *already are* the whole GBV growth. Therefore:

- **geographic mix −1.0896pp is already inside them** (it is an output of the same share
  identity applied to the same regional volumes);
- **unit size / LOS +0.3818pp is already inside the ADR line**;
- seats 0.00 and booking-date FX 0.00 are correctly zero.

Listing mix and LOS as separate additive contributors double-counts **−0.708pp**. The
decomposition only reaches the right total because the additive form *omits* the
volume x price cross term (+0.2479pp) and the +0.1674 plug absorbs the difference. The
exact accounting:

```
plug 0.1674 = cross term 0.2479 + true timing 0.0117 - the five narrative lines 0.0922
```

Independently: the GBV-side lines (rows 0-8) sum to **10.5554pp** against the model's own
GBV growth of **11.5111pp** — a **0.96pp unexplained gap in an 11.5pp number**.

And the three "assumed_not_rebuilt_tonight" revenue lines (fee +0.90, new lines +0.20,
regulation −0.30) are **not in the computed 15,837.6**: the grid revenue is
`lambda x lagged GBV` and nothing else. They are narrative, presented as arithmetic.

**Fix:** present FY27 as `GBV growth (volume x ADR, multiplicative) + timing`, state the
cross term explicitly, move mix / LOS / seats / FX to a "already inside the lines above,
shown for attribution only" block with zero column, and put fee / new lines / regulation
in a clearly separated "not in the number" block — or add them to the number and restate it.

### F2. The 4Q26 guide object's central GBV input contradicts the programme's own 3Q26 GBV forecast, and the fix flips the trade

Every 4Q26 number in `guidance-policy`, `kernel-lambda`, `fee-takerate`, `fx-lag`,
`SCOREBOARD.md` and `OPTIMAL_MIX.md` is anchored on **GBV_3Q26 = 26,300 musd**, the
architect's hand-set central case. But `optimal_mix/combined_live_objects.json` publishes
its own combined **3Q26 GBV of 26,549.8 musd** (`stack_shrunk`, pool `all`, STATUS OK,
weight coverage 1.0). Nobody reconciled them. Recomputed with the same
lambda_Q4 = 12.0298% and the same mean cushion +1.857%:

| GBV_3Q26 input | print | guide mid | P(guide < Zacks 3,200) | P(guide < AV36 3,158) |
|---|---|---|---|---|
| 26,300 (architect, as published) | 3,199.9 | 3,141.6 | 0.730 | 0.568 |
| **26,549.8 (the programme's own forecast)** | **3,220.0** | **3,161.3** | **0.657** | **0.486** |

Using the programme's own GBV moves the guide midpoint **+19.7 musd**, drops
P(guide < Zacks) by **7.3pp** and drops P(guide < the 36-analyst panel) **below one half**.
Add the half-weight fee step on top of the mix GBV (print 3,260, guide ~3,201) and
P(guide < Zacks) is ~0.50 as well: **the guide-below-Street trade disappears entirely.**

The 4Q26 GBV grid is an *input*, not a forecast — OPTIMAL_MIX.md says so — but the memo's
headline probability is a deterministic function of that input, and the programme contains
a better-supported value for it that was never used.

**Fix:** either adopt 26,549.8 as the central case and restate every 4Q26 probability, or
state in the memo why the architect's 26,300 is preferred to the programme's own
combination. Do not publish 0.73 / 0.58 without the alternative alongside.

### F3. Three live 3Q26 objects are mutually inconsistent; the take-rate pre-registration is decided by which one you read

From the same `combined_live_objects.json`:

- revenue 4,816.1 musd
- GBV 26,549.76 musd
- take rate 17.8065%, with **P(clear the pre-registered 18.10) = 0.254**

But `4,816.1 / 26,549.76 = **18.140%**` — which **clears** the pre-registration. The gap is
**33.3bp**, or 88 musd of revenue on that GBV.

And `fee-takerate` (SCOREBOARD.md line 793) publishes a *third* answer: at GBV 26,300 and
central theta the printed take rate is **18.397%, P(>= 18.10) = 0.775**.

So the programme currently says P(the fee migration is visible in the 3Q26 print) is
**0.254, or implied-certain, or 0.775**, depending on which of its own three objects you
read. This is the single pre-registered test in the whole programme and it cannot be
reported until the three are reconciled.

Related identity failure in the same JSON: `(1 + nights_yoy 10.3423%)(1 + adr_yoy 5.2668%)
- 1 = 16.154%` against the published `gbv_yoy 15.938%` — the combination does not respect
`GBV = nights x ADR`, off by 0.22pp (~50 musd).

**Fix:** impose the identity on the live block. Publish one take rate, derived from the
revenue and GBV objects, and re-run the pre-registered probability from it.

### F4. The registered live FX number is contradicted by management's own letter

`fx-lag__live_fx_schedule.csv` registers 3Q26 `fx_pts_revenue` = **+1.2pp**, q10-q90
**[0.074, 2.326]**.

The 6 Aug 2026 shareholder letter (`02_guidance_ledger.csv`, guide_id
`ABNB-2Q26-revenue_yoy_pct-3Q26-183`, verified=True) guides 3Q26 revenue growth 15-17%
*"inclusive of an approximate **three percentage point** FX tailwind **after factoring in
our hedging program**"* — i.e. management's own estimate of exactly the series
`fx_pts_revenue` measures (1Q26 guided ~3pt / printed 3.0; 2Q26 guided ~3% / printed 4.0).

**+3.0 sits outside the package's own 80% interval.** Out-of-sample on the three quarters
that matter, using my independently rebuilt basket:

| spec | 1Q26 (act 3.0) | 2Q26 (act 4.0) | 3Q26 (mgmt ~3.0) | mean abs err |
|---|---|---|---|---|
| package Object A free fit | 3.97 (+0.97) | 3.20 (−0.80) | **1.15 (−1.85)** | **1.21** |
| architect Phi weights x fitted scale 0.851 | 2.71 (−0.29) | 4.25 (+0.25) | **2.88 (−0.12)** | **0.22** |
| Theo pure lag-2 x 0.56 | 1.15 (−1.85) | 2.10 (−1.90) | 3.14 (+0.14) | 1.30 |
| contemporaneous x 0.56 | 3.14 (+0.14) | 1.27 (−2.73) | 0.14 (−2.86) | 1.91 |

The scale required on the Phi weights to hit management's 3.0 on 3Q26 is **0.886**, against
the package's own fitted stated-series scale of **0.851**. The architect's kernel, at the
package's own fitted scale, is the best live predictor by a factor of five, while the
package's registered free-weight fit is the worst except for the two pure restrictions.

This does not overturn §2's in-sample verdict (see §5), but **+1.2pp must not reach the
memo**, and the memo must not imply the programme disagrees with management about 3Q26 FX
without saying so out loud.

---

## 2. Recomputation of the scoreboard — the machinery PASSES

I rebuilt **all 200 scoreboard rows** from the 57 registry CSVs plus `targets.csv`, with an
independent implementation of the actuals join, the per-quarter naive match and the metric
block.

```
registry rows: 4040   files: 57
merge status: {'both': 200, 'right_only': 72, 'left_only': 0}
MISMATCHES: 0        (tolerance 1e-6 on rmse and ratio, exact on n)
```

**Zero mismatches on n, MAE, RMSE, bias and `rmse_ratio_to_naive` across all 200 rows.**
That is a strong result and it should be said plainly: the harness is not fudging anything.
Spot values I confirm independently, PIT replay:

| object | W1 ratio | W2 ratio | confirmed |
|---|---|---|---|
| baselines guide_cushion (revenue) | 0.3771 | 0.3191 | yes |
| guidance-policy print_from_guide | 0.3788 | 0.3308 | yes |
| kernel last3_ex_covid | 0.5552 | 0.4721 | yes |
| kernel ex_covid | 0.5651 | 0.4843 | yes |
| kernel w = 2/3 published spec | 0.8309 | 0.7269 | yes (PIT KS p 0.00269 — rejected) |
| baselines street | 1.0731 | 0.8715 | yes |
| baselines ar1 | 1.1011 | 1.0094 | yes |
| kernel w033 | 1.5839 | 1.3113 | yes |
| l1 revenue_contemporaneous | 11.338 | 11.338 | yes |
| kernel revenue_level_h1 | 1.1689 | 0.8857 | yes |

**But the scoreboard file is STALE.** 72 registry groups — all 18 `optimal-mix` objects —
are in the registry and absent from `harness/scoreboard.csv`. The scorer was last run
before optimal-mix registered. Consequences:

- "objects_scored: 29" understates the registry by 18 objects.
- Several optimal-mix rows would change the leaderboard if scored:
  `mix_revenue_musd_parsimonious` PIT is **0.3604 on W1** (better than guide_cushion's
  0.3771) and 0.3324 on W2 (worse than 0.3191); `mix_revenue_musd_all` PIT is **0.3129 on
  W2**, the best revenue-level number in the whole registry, against 0.4318 on W1.
  Both split the windows, so the "no combination survives both windows" conclusion is
  unchanged — but it should be shown, not asserted.
- `mix_nights_m` and `mix_gbv_musd` LOSE to naive on both windows (1.549 / 1.105 and
  1.312 / 1.021 under PIT) and yet the mix's nights and GBV points are published as live
  objects with STATUS OK. That must be labelled.

**Fix:** re-run `harness/score.py` and repaste SCOREBOARD.md.

---

## 3. "Best method" is mislabelled on the target that matters

SCOREBOARD.md's `best_per_target` names **guidance-policy `print_from_guide`** as the best
revenue-level method and calls the comparison with the cushion baseline "a dead heat".

It is not a dead heat and it does not go that way. On both windows, both replays:

| | W1 RMSE | W2 RMSE |
|---|---|---|
| baselines `guide_cushion` (**baseline**, 1 param) | **35.457** | **34.596** |
| guidance-policy `print_from_guide` (1 param) | 35.617 | 35.865 |

The baseline wins **both** windows. The honest sentence is: *once a guide exists, nothing
in the programme beats guide midpoint x (1 + trailing-8 cushion)* — which is a good, clean
result, and it is the one the mix's own BMA weights independently discover (0.537 on
guide_cushion, 0.463 on print_from_guide, < 0.005 on the other twelve combined). Naming a
package object as the winner over its own baseline is the kind of thing a judge will find.

Related: the two objects are near-collinear by construction (median cushion vs mean
cushion of the same trailing-8 ratios), so the "14-method mix" that produces the headline
3Q26 print of 4,816.1 is arithmetically **one method**: `4,730 x 1.0182`. Say so.

---

## 4. Leakage hunt — the stacking is CLEAN, with three residual exposures

I read `optimal_mix/combine.py` and `optimal_mix/run.py` line by line.

**Clean:**

1. The walk-forward loop filters the training block with
   `hist = [h for h in all_q if h in act and h in printdates and printdates[h] < dv]` —
   **strictly before**, from the harness calendar, expanding. Correct.
2. `combine.py` has no notion of time at all; the training block is assembled by the
   caller, so no scheme can leak on its own. Correct design.
3. The mix drops its own registry rows on every run, so it cannot eat its own output.
4. Both prior replays are published side by side everywhere.
5. The harness `baseline_street` raises `StreetVintageError` on any consensus row
   postdating the vintage — the kill-list rule about September vendors is enforced
   mechanically, not by discipline. Verified in the README and the registry
   (`street_as_of` = guide date on every row).
6. Conformal calibration for the live 3Q26 object uses 14 walk-forward residuals whose
   target quarters all printed before 2026-09-11. Not leakage.
7. `baseline_naive` at 2023Q1 = 1,509 x 1.2415 = 1,873.4, reproducing the registry exactly
   and using only 2022Q4-knowable growth. No revised-data contamination on revenue
   (revenue is not restated; GBV and nights are $0.1bn / 0.1M rounded current-vintage, which
   matters for the GBV and nights objects but not for the revenue spine).

**Residual exposures, all disclosed by the packages but worth restating:**

- **The `full_sample` replay is leaky by construction and the gaps are large.** Not a bug —
  it is the diagnostic — but any number quoted without naming the replay is wrong by up to
  a factor of two. Worst offenders I measured: `fx-lag h3` W2 **0.824 full_sample vs 1.697
  PIT** (a 51% improvement from hindsight), `guidance-policy guide_mid_next_q` W1 **37.23
  vs 63.60** (41%), `fx-lag h3` W1 **1.000 vs 1.485** (33%), the no-guide kernel pool
  **35.97 vs 66.77** (46%, as OPTIMAL_MIX.md already says).
- **Specification search is not corrected anywhere.** `kernel-lambda` registered **7**
  revenue-level variants and the scoreboard quotes the best two (`ex_covid`,
  `last3_ex_covid`). `tracker-backlog` registered **8** specs and 3 survive. `optimal-mix`
  ran **7 schemes x 4 pools**. At n = 14 and n = 10 with ~37 objects, "survives both
  windows" is a weak filter and there is no multiplicity adjustment. The "ex_covid"
  exclusion is itself an ex-post judgement about which quarters were outliers.
- `vdate[q]` is taken from whichever candidate row sorts first within the quarter group.
  Harmless today (all candidates use the guide date) but it is an unguarded assumption.

**Conclusion: I could not construct a leakage attack that the programme has not already
disclosed.** This is the strongest part of the build.

---

## 5. FX — the verdict, rebuilt from scratch

### 5.1 The package's Object A reproduces independently

My rebuild (daily FRED -> quarterly average -> y/y -> judgement currency weights ->
trailing-4 filed regional revenue weights -> interval likelihood on `[x-0.5, x+0.5]`,
n = 14, 1Q23-2Q26, **stated / after-hedge series — the PIT-clean one**):

| | my rebuild | fx-lag note (stated) |
|---|---|---|
| a0 / a1 / a2 | 0.4526 / 0.3612 / 0.0373 | 0.45 / 0.36 / 0.03 |
| scale | **0.8511** | **0.84** |
| w0 / w1 / w2 | 0.532 / 0.424 / 0.044 | 0.53 / 0.43 / 0.04 |
| **effective lag** | **0.512 q** | **0.50 q** |
| sigma | 1.034 pp | 1.03 pp |

LR tests against the free fit, sigma profiled, df 3:

| restriction | my LR / p | note's LR / p |
|---|---|---|
| architect Phi x 0.56 | 10.00 / **0.0186** | 10.2 / 0.017 |
| **Theo pure lag-2 x 0.56** | **17.59 / 0.0005** | 18.0 / 0.0004 |
| contemporaneous x 0.56 | 7.41 / 0.0599 | 7.5 / 0.058 |
| pure lag-1 x 0.56 | 6.91 / 0.0748 | 7.1 / 0.069 |
| Phi weights, free scale (s = 0.665) | 9.57 / 0.0083 (df 2) | 9.9 / 0.0072 |

Univariate correlations with the stated FX series, n = 14: **lag-0 r = 0.800, lag-1
r = 0.797, lag-2 r = 0.531**. LOO RMSE (OLS, with intercept): lag-0 1.554, lag-1 1.507,
lag-2 2.218, free 0-2 1.494, Phi-on-basket 1.677; baselines zero 2.268, last-value 2.188.

**I could not reproduce the M6 critic's "lag-1 r 0.861 beats lag-0 0.763".** On my basket
lag-0 and lag-1 are a dead heat (0.800 vs 0.797). The M6 ordering may hold on a different
basket construction; it does not hold on this one and should not be quoted as evidence.

### 5.2 The two-quarter proxy: NOT SUPPORTED in-sample; the "0.1pp match" is a coincidence

The M6 arithmetic does reproduce: `0.56 x the 1Q26 basket (+5.610) = +3.14pp` against
management's guided ~+3.2pp for 3Q26. **But it is a one-point coincidence.** The same rule
applied to the two quarters that actually printed:

- 1Q26: `0.56 x 3Q25 basket (2.057) = 1.15` against a printed **3.0** — miss −1.85pp
- 2Q26: `0.56 x 4Q25 basket (3.748) = 2.10` against a printed **4.0** — miss −1.90pp

A rule that misses by ~1.9pp on both of its last two realised observations and lands on the
third — which is itself a management forecast, not a print — has not been validated. Add the
formal test (LR 17.6, p 0.0005, the hardest-rejected of the four restrictions) and the
weight on lag 2 in the free fit (w2 = 0.044, and 0.000 on the gross series), and the answer
is unambiguous.

### 5.3 The verdict

> **Theo's two-quarter lead is NOT supported by the data and should not be asserted in the
> memo.** On 14 letter-rounded observations, scored as intervals, the effective lag of the
> stated revenue-FX contribution is **0.51 quarters** (95% CS roughly 0.0-1.2), the weight on
> lag 2 is **0.04**, and the pure two-quarter restriction is rejected at **p = 0.0005** — the
> worst-fitting of the four restrictions tested. Contemporaneous (p 0.060) and pure one-quarter
> (p 0.075) both survive; one quarter of lag is simply not identified at n = 14.
>
> **Three things must be said alongside it.** (i) The *mechanism* Theo describes is real and
> is not what the regression measures: bookings are made months ahead, and the
> booking-date basket is already inside the lagged GBV base, so the lag shows up as an
> *output* of the kernel arithmetic and must never be subtracted a second time. (ii) The
> fitted basket scale on the gross series is 0.95 with a 95% CS of [0.63, 1.33], which
> **excludes the disclosed 0.56 non-USD revenue share** — that is a finding about the
> judgement currency weights understating exposure by ~70%, not about the lag, and it puts a
> caveat on every basket-derived pp in the programme. (iii) On the live quarter the fitted
> model is **wrong in the direction of the architect**: it says +1.2pp for 3Q26 where
> management says ~+3.0pp, and the architect's Phi weights at the package's own fitted scale
> land at +2.88pp (§F4). The in-sample rejection of Phi at p = 0.019 and its out-of-sample
> superiority on the last three quarters are both true, and the memo should carry the
> tension rather than pick a side it cannot defend.
>
> **What is safe to say:** FX is forecastable (every specification beats zero and beats
> last-value by 2-4 standard errors); the lag is short and not separable from zero at this
> sample size; the 4Q26 FX step is an OUTPUT of the lagged-GBV arithmetic and is never
> added to revenue; nothing in the FX block survives the both-windows rule, because
> `fx_pts_revenue` has no naive baseline in the harness at all (see §6.3).

---

## 6. Every number that will reach the memo, graded

### 6.1 SAFE — survives both windows, PIT replay, on the harness scoreboard

| number | basis |
|---|---|
| 3Q26 print ~4,816 musd (= guide 4,730 x 1.0182) | guide_cushion 0.377 / 0.319, PIT KS p 0.39; print_from_guide 0.379 / 0.331 |
| "once guided, the guide plus the trailing-8 cushion IS the forecast" | the central, defensible result of the whole programme |
| The pre-guide Street is beatable but not reliably: Street 1.073 W1 / 0.871 W2 | fails the both-windows rule — say it as a split |
| Pitch-date (no-guide) revenue level: kernel ex_covid 0.565 / 0.484 | survives both, PIT KS p 0.63 |

### 6.2 EXPLORATORY — must carry the label

| number | why |
|---|---|
| **FY27 15,837.6 musd / +11.52%** | `l1-reconciliation` registers **nothing** at annual horizon; its only registered revenue object is `revenue_contemporaneous` at ratio **11.34** (a declared negative control). Growth spans **+9.18% to +11.52%** across the kernel-weight grid because the weight moves **FY26 as well as FY27** (FY26 = 14,398.5 at w = 0.33 vs 14,201.2 at w = 2/3). The "+0.09pp edge over the Street-implied +11.43%" exists **only at w = 2/3**; at w = 0.33 the edge is **−2.25pp**. |
| 3Q26 take rate 17.81% | 0 of 8 registered objects beats a plain seasonal naive on either window; and see F3 |
| 4Q26 guide midpoint 3,141.6 / 3,180.9 and the P(< Street) pair | arithmetic verified (below), input contested (F2), two published sds (§6.4) |
| All FX pp | no baseline exists for the target; nothing survives (§6.3) |
| tracker-backlog revenue y/y 0.680 / 0.593 | the package itself says to read the RNPL-corrected result as *corroboration, not a cleared Gate G1* — `k` is a researcher-assumed input swept over 3 values, the raw feature fails at 1.171 / 1.167, and the surviving specs registered **no LIVE row** |
| nights y/y and revenue y/y live points | already labelled NOT USABLE by optimal-mix — keep that label |

### 6.3 NOT TESTABLE — presented as failures, actually untested

72 of 200 scoreboard rows have an empty `rmse_ratio_to_naive` and therefore
`survives_both_windows = False`. That False means **"no baseline exists"**, not "lost".
Affected targets: `take_rate_pct`, `guide_mid`, `fx_pts_revenue`, `adr_yoy`, `gbv_yoy`,
`nights_yoy`. Confirmed by recomputation. Consequences the memo must respect:

- **No FX object survives either window**, because the harness has no naive for
  `fx_pts_revenue`. The summary's "fx-lag h2 0.994" is an **RMSE in pp, not a ratio** and
  must not be read as beating anything.
- `guide_mid_next_q` cannot fail the both-windows rule either; it fails Gate G4 on its own
  MAE comparison against the Street (1.986 vs 1.966 W1; 1.762 vs 1.609 W2), which is the
  correct and damning statement.
- The take-rate classification bug is real and large: `calibration-rail` ref rows score
  **3.14-4.61 RMSE on a 13-18% level series** against 0.326 for `fee-takerate
  take_rate_lastyear` — a factor of 10-14, caused by compounding a growth rate onto a level.
  Those three rows must be struck from any pool, as optimal-mix's `repaired` pool does.

### 6.4 Arithmetic I verified and it is RIGHT

- `lambda_Q4 = mean(11.946, 12.117, 12.026) = 12.0297%` ✓
- `2/3 x 26,300 + 1/3 x 27,200 = 26,600.0`; `x 12.0298% = 3,199.9` ✓
- `3,199.9 / 1.01857 = 3,141.6` ✓; half step `3,239.9 / 1.01857 = 3,180.9` ✓;
  full step `3,279.9 / 1.01857 = 3,220.1` ✓
- `P(guide < 3,200 | sd 3.03%) = Phi(58.4 / 95.19) = 0.730` ✓;
  `P(< 3,158) = 0.568` ✓
- kernel 3Q26 live: `0.172393 x [2/3(27,200) + 1/3(29,200)] = 4,803.9` ✓ (matches 4,804.0)
- FY27 decomposition lines sum to 11.5228 ✓ (but see F1 — summing is not reconciling)

**Two published sds for the same event.** `guidance-policy` uses **3.03%** and reports
P(guide < Zacks) = 0.730; `optimal-mix` uses **2.73%** and reports **0.752**. Both are
internally correct. The memo cannot carry both. Pick one, name its provenance, and delete
the other from every document.

**Two fee-step numbers for the same case.** The "half weight" 4Q26 print is **3,239.9**
(guidance-policy, +1.25% = +40 musd) in SCOREBOARD.md's table and in the registered
optimal-mix object, but SCOREBOARD.md's own narrative says the fee step recomputed from
primitives is **+0.28 to +1.48pp**, giving a central half-step print of **3,218.2**. The
+40 is at the very top of the recomputed range. Reconcile before quoting.

---

## 7. Against the repo's withdrawn-claims list and the kill list

Checked `research/notes/overnight/14_master-synthesis.md` §11 and the kill list.

**Kill list — obeyed:**
- M3 revision regression: absent. ✓
- M5 hierarchical cushion model: absent. ✓
- M4 120-market panel as a nights measurement: not built. ✓
- Stan state space for the prelim: not built; constrained LS used. ✓
- Second subtraction of the FX step: the repo's −3.4pp appears only as a comparator in the
  four-way spread, never as an input. ✓
- `28_fx_hedge_forward.csv` added on top of the stated after-hedge FX: not done. ✓
- Zacks 4 Sep used as the 6 Aug pre-guide Street: mechanically impossible (harness raises). ✓

**Kill list — partially obeyed:**
- **The 9/9 guide-below-Street drift rule.** Correctly killed as a signal, but **three
  incompatible p-values are now in circulation for it**: 0.27 (the kill list), **0.038**
  (WS20's executable-entry restatement, n 23, mean −4.21%, which §11.1 says *supersedes* the
  WS16 figure), and **0.141** (calibration-rail tonight, executable 8 of 9, spread −1.50pp).
  The memo must quote **no p-value** for this and, if it quotes a base rate at all, must say
  which restatement and that it is not tradeable.

**Withdrawn claims correctly respected:** "0 / 23, no publisher quotes an ADR consensus" is
withdrawn (Zacks does, 5 prints) — nothing tonight relies on it. The AirROI 55.9% figure is
not used as evidence about hidden fees. The direct-booking −0.8pt is not used; 0-15bp is
the live range. The 2020Q4 "margin" attribution is not used.

**One repo claim tonight's build contradicts without saying so:** §11.1 records
*"approximately half of our active listings are now subject to the single service fee"* as
verbatim in the 2Q26 call (6 Aug 2026). SCOREBOARD.md's data-quality flags say the
**15 Sep and 13 Oct 2026 fee-migration deadlines have no source in the repository** and are
a dated assumption. Both can be true — the 50% figure is disclosed, the deadlines are not —
but the memo must not present the deadlines as disclosure. Flag stands.

---

## 8. Refutation attempts and outcomes

| # | claim attacked | attack | outcome |
|---|---|---|---|
| 1 | the 200 scoreboard cells are correctly scored | full independent recomputation, pure pandas, no harness import | **SURVIVED** — 0 mismatches |
| 2 | the registry is fully scored (29 objects) | count registry groups vs scoreboard rows | **REFUTED** — 72 groups / 18 optimal-mix objects missing; scoreboard.csv is stale |
| 3 | print_from_guide is the best revenue-level method | compare RMSE with the guide_cushion baseline on both windows | **REFUTED** — the baseline wins both (35.457 / 34.596 vs 35.617 / 35.865) |
| 4 | fx-lag Object A coefficients and LR tests | independent basket rebuild + interval likelihood | **SURVIVED** — a, scale, lag, sigma and all five p-values reproduce |
| 5 | Theo's two-quarter lead is rejected | independent LR, correlations, LOO, and a 2-quarter out-of-sample replay of the 0.56 x lag-2 rule | **SURVIVED** — p 0.0005, w2 = 0.04, and the rule misses 1Q26 and 2Q26 by ~1.9pp each |
| 6 | the registered live 3Q26 FX of +1.2pp | compare with the verified 6 Aug letter and backtest rival kernels on 1Q26/2Q26 | **REFUTED** — mgmt's ~+3.0 is outside the 80% interval; architect Phi at the fitted scale has 5x lower live error |
| 7 | "kernel timing +0.167pp is an identity" | compute GBV growth minus revenue growth from the package's own grid | **REFUTED** — it is −0.012pp; the line is a residual |
| 8 | the FY27 decomposition has one owner per line, no double count | test whether (1+volume)(1+ADR) already equals model GBV growth | **REFUTED** — it equals it exactly; mix and LOS are double-counted (−0.71pp) and the GBV-side lines miss by 0.96pp |
| 9 | the 4Q26 guide midpoint and P(guide < Street) | re-run with the programme's own 3Q26 GBV instead of the hand-set input | **REFUTED as quotable** — guide 3,161.3, P(< Zacks) 0.657, P(< AV36) 0.486 |
| 10 | 3Q26 take rate 17.81%, P(clear 18.10) = 0.254 | divide the mix's own revenue by its own GBV; compare with fee-takerate | **REFUTED** — implied 18.140%, which clears; fee-takerate says 18.397% / P = 0.775 |
| 11 | the stacking weights are leave-future-out | read the replay loop and the scheme functions | **SURVIVED** — `printdates[h] < dv` strictly; schemes are time-blind |
| 12 | conformal residuals do not overlap the test period | trace the live-object calibration set | **SURVIVED** — all 14 residuals from quarters printed before 2026-09-11 |
| 13 | baselines are not built with revised data | reproduce baseline_naive at 2023Q1 from PIT inputs | **SURVIVED** on revenue (1,509 x 1.2415 = 1,873.4); **PARTIAL** on GBV/nights, which are $0.1bn / 0.1M rounded current-vintage |
| 14 | "fx-lag h2 0.994 survives both windows" | check the scoreboard row | **REFUTED** — 0.994 is an RMSE in pp; `fx_pts_revenue` has no naive, ratio is NaN, survives_both is False |
| 15 | one predictive sd for the 4Q26 guide | compare guidance-policy and optimal-mix | **PARTIALLY** — both internally right, two published probabilities for one event (0.730 vs 0.752) |
| 16 | the drift rule is dead | compare tonight's p with the kill list and WS20 | **SURVIVED as a kill**, but three incompatible p-values (0.27 / 0.038 / 0.141) are in circulation |

---

## 9. Must-fix before the memo, in priority order

1. **Rebuild the FY27 decomposition** (F1). State GBV growth multiplicatively, publish the
   cross term, move mix / LOS / seats / FX to a zero-weight attribution block, separate the
   assumed revenue lines, and delete the "+0.167pp identity" claim.
2. **Reconcile GBV_3Q26 = 26,300 against the programme's own 26,549.8** (F2), and restate
   every 4Q26 probability, or justify the choice in the memo.
3. **Reconcile the three take-rate numbers** (F3: 17.81% / 18.14% implied / 18.397%) and
   re-run the single pre-registered test from the reconciled one.
4. **Strike the registered live FX of +1.2pp** or publish it alongside management's stated
   ~+3.0pp with the tension explained (F4).
5. **Re-run `harness/score.py`** so optimal-mix's 18 objects are scored, and repaste
   SCOREBOARD.md.
6. **Correct the "best revenue-level method"** to the guide-plus-cushion baseline (§3).
7. **Pick one predictive sd** for the 4Q26 guide and one fee-step arithmetic (§6.4).
8. **Relabel the 72 "not testable" rows** so `survives_both_windows = False` is never read
   as "tested and failed" (§6.3).
9. **Label FY27 exploratory** and, if the growth edge is quoted at all, quote the
   +9.18% to +11.52% band, not +11.52% alone (§6.2).
10. **Quote no p-value for the drift rule** (§7).
11. **Do not present the 15 Sep / 13 Oct fee deadlines as disclosure** — they have no source
    in the repository.
12. **Name the replay** on every kernel and FX number quoted; the PIT-vs-full-sample gap
    reaches 51%.

## 10. Harness change requests

1. Register naive / AR(1) / trailing-4 baselines for `take_rate_pct`, `guide_mid`,
   `fx_pts_revenue`, `adr_yoy`, `gbv_yoy`, `nights_yoy`, so 72 rows stop reporting an
   untested False.
2. Fix the growth-vs-level classification: `take_rate_pct` is a level whose name ends in
   `_pct`, and the seasonal naive returns 0.0 on it.
3. Add a `window_coverage` column so an object scored on 10 of 14 W1 dates cannot show
   `survives_both_windows = True` vacuously (`gbm_surprise_guide`, `gbm_revenue`,
   `l1 revenue_contemporaneous` all score the identical 2024Q1-2026Q2 set in both windows).
4. Score `spec_id` as part of the group key, or the 8-spec `tracker-backlog` objects pool
   into one meaningless series.
5. Add an annual / multi-quarter LIVE slot so FY27 and the 2027 quarters stop parking in
   unregistered files, and reject a LIVE row whose `quarter` contradicts its `object` name
   (`l1-reconciliation__fy27_revenue.csv` currently holds one **2026Q3** row of 4,804.0).
6. Warn when only one `prior_basis` is present — `l1 fy27_*` register `full_sample` only.

## 11. Commands

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
# all three audit scripts, exit code 0
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/red_team/run.py

# individually:
#  rt_recompute.py  rebuilds all 200 scoreboard cells from the registry (0 mismatches)
#  rt_fx.py         rebuilds the FX basket, fits lags 0/1/2 by interval likelihood, LR tests
#  rt_fx2.py        falsifies the live 3Q26 FX point against the 6 Aug letter
```

The audit scripts live in `analysis/src/forecast_methods/red_team/`. They import no package
code, write no data outputs and register nothing. No harness, L0, registry or other package
file was created or edited. No git operation was performed.
