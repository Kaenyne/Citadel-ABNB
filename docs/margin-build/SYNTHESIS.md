# Margin build — SYNTHESIS

WS23 triangulation, 14 Sep 2026. Package `analysis/src/margin_build/23_final_model/`
(`py -3.13 .../run.py`, exit 0, ~4 min). Data `data/processed/margin_build/23_final_model/`.
Workbook `model/ABNB_margin_model.xlsx`. Registry objects `final-margin__combined` (1,152 rows)
and `final-margin__combined_dollar_from_margin` (576 rows).
Vintage **2026-09-11**; revenue path **bridge v3 / WS06 v2b**; consensus **LSEG 11 Sep** and
**Bloomberg BEST 5 Sep**.

> **Post-audit (WS31, 14 Sep).** The Codex/Astra audit
> (`docs/margin-build/audit/CODEX_ASTRA_AUDIT.md`, 18 findings) has been applied in full —
> every finding accepted, one (16) accepted in part with the deferred half named. The critical
> finding (a missing print-date gate on the h=1/h=2 calibration pools) **is fixed and replayed**;
> h=0 is unchanged and every pass/fail conclusion survives. The triage table, with what moved and
> what did not, is in `docs/margin-build/audit/AUDIT_RESPONSE.md`; every number that moved is in
> **§11 Post-audit changes** at the bottom of this file. The two headline restatements: the 3Q26
> dollar band is now **$2,337-2,462M** (from the adopted dollar object's own calibration, not the
> margin route's) and **P(beat) is 0.78, not 0.77** — the old pair took the band from one object
> and the sd from another. 3Q26 **S&M is $781M, +33.5% y/y** (was $790M / +35%) after the add-back
> schedule was unified.

---

## Bottom line, in ten lines

1. **3Q26 adjusted EBITDA margin 49.9%, adjusted EBITDA $2,399M**, against a Street of 49.78% / $2,361.5M (n 36, sd $20M). **The beat is $38-50M of dollars, not points of margin** — and it is a revenue call, not a cost call: at the Street's own revenue our margin is worth $8M.
2. The number comes from **`final-margin|combined|stack_clip`**, a six-member leave-future-out combination plus a zero-parameter management-sentence clip: **MAE 1.13pp (W1, n 14) / 0.79pp (W2, n 10)** — **0.50x / 0.40x** the seasonal naive (which *is* the guidance sentence as a level), **0.71x / 0.60x** the Street, sign test **p 0.0032 / p 0.011** against the naive and **p 0.029 / p 0.055** against the Street, on **2 wrapper parameters and 52 inherited (54 in the registry)**. In **dollars** the number we quote is that margin object multiplied by the revenue leg, registered and scored in its own right as **`final-margin|combined_dollar_from_margin`**: **MAE $30.7M (W1) / $25.8M (W2)**, **0.25x / 0.26x** the naive and **0.47x / 0.44x** the Street, better in **14 of 14 and 10 of 10** quarters than the Street (sign p 0.0001 / 0.0010) — the best dollar object in the build. The separately-built four-member dollar combination ($39.7M / $30.9M) is a **labelled cross-check**, not the quoted object (WS31 audit 04).
3. **The line that carries the quarter is sales & marketing: $781M, +33.5% y/y** on a $2,405M cash cost stack, against cost of revenue +12.5%, operations & support +6.4%, product development +14.4% and G&A +9.4%. $48M of S&M is 1.0pp of 3Q26 margin.
4. **Management's "down slightly vs Q3 2025" caps 3Q26 at 50.085%.** We land 0.15pp under it. Correcting the model for its own recent point-in-time bias (−0.27pp over the last five quarters) takes it to 50.21%, which the sentence then caps at 50.085%. **Both routes land in 49.9-50.1%** — the run's whole 47.9-51.7% spread has closed onto that.
5. **4Q26: we have no edge.** At h=1 the combination beats the naive (0.83x / 0.81x) but **loses to the raw Street by 20-28%**, so the Street carries the quarter: **28.90% / $918M** on bridge-v3 revenue, with the combination at 29.04% / $923M and M3's guide path at 29.90% / $950M.
6. **FY26 35.73% / $5,098M**, +0.23pp over the "at least 35.5%" floor and +$44M over Street's $5,054M. **That cushion is thin**: the floor breaks on a 2H26 revenue shortfall of only **0.63% if costs are held / 0.94% if they flex ($50-75M)**.
7. **The 5 Nov guide sentence we forecast is "approximately 36%"** (M3: the November sentence has been the numeric floor + 50bp, exact 2 of 2). **At our 3Q26 that sentence requires a 4Q26 margin of 30.1% against a Street 28.9%** — a 1.2pp, ~$39M gap, and the single most contestable number in the guide.
8. **FY27 is the trade: 34.64% / $5,483M against Street 36.45% / $5,766M, −$283M (−1.8pp).** **Incremental margin 24.7% against the Street's implied 43.7%.** This is a *spending scenario*, not a forecast — the combination fails its test at h≥2 — but it is arithmetic on the 2025-26 brand-marketing ramp continuing, and nothing in the build supports the Street's number.
9. **The biggest risk is S&M in both directions.** If the ramp pauses, the driver family's unclipped 51.4% is right and 3Q26 prints ~1.5pp higher. If it accelerates past +33% y/y, 4Q26 and FY27 break lower. And **we cannot measure a cost dial at Airbnb**: the peer regression of total opex on revenue gives **k 0.14 with t 0.47, n 18 — SE ≈ 0.30, a 95% interval of roughly −0.44 to +0.72**, which does not exclude flexibility as large as BKNG's 0.61, TRIP's 0.63 or EXPE's 0.44. It is an imprecise estimate, not a zero (WS31 audit 13). The model's own working assumption is M6's **cash-cost** elasticity of 0.364 (t 6.58, a different cost definition), and the honest range for a revenue miss is the held-to-flex band in §4.
10. **Nothing in this build forecasts the margin ratio better than the Street beyond h=0.** Everything from 4Q26 onward is the Street, a guide identity, or a labelled scenario. The pitch should say that out loud.

---

## 1. How the model is built (one page)

**The object.** `final-margin|combined`, primary spec `stack_clip`. At each guide date, for each
target quarter, it is a weighted average of six views of the adjusted EBITDA margin, then clipped
to the quarterly management sentence.

| member | what it is | own W1 / W2 h=0 MAE (pp) | own bias |
|---|---|---|---|
| `street-bias\|dispersion_conditioned\|rw_hl4_med` | Street + a fraction of its recency-weighted historical bias (M5) | 1.223 / 0.787 | +0.13 / +0.07 |
| `street-bias\|street_plus_flowthrough\|rw_hl4` | Street EBITDA + 0.464 x (our revenue − Street revenue) + $16M (M5) | 1.661 / 0.987 | +0.69 / +0.32 |
| `baselines-margin\|street` | the raw LSEG mean at the vintage | 1.592 / 1.311 | −1.22 / −1.13 |
| `guide-policy-margin\|actual_given_guide\|nov_sentence_pin` | the FY guide as a budget constraint, allocated `m[q−4] + delta` (M3) | 1.883 / 1.842 | −1.42 / −1.51 |
| `margin-ts\|q_sentence_direction\|k_fit_median` | `m[q−4] + k x direction of the management sentence` (M2) | 2.048 / 1.539 | −1.68 / −1.02 |
| `FAMILY_A` | equal mean of M1 `b_elastic_rw`, M6 `l0_rw`, M2 `sarima\|lines_aicc` — the cost-stack family | 2.128 / 1.670 | −0.06 / +0.43 |
| *reference* | `seasonal_naive` = y[q−4] = **the sentence level** | 2.237 / 1.959 | −0.47 / +0.19 |

Source: `data/processed/margin_build/23_final_model/23_diag_member_scores.csv`.

**The weights.** At target quarter *t*, the inverse of each member's mean absolute PIT error over
**quarters whose actual had already printed on or before this row's vintage date** — not merely
quarters earlier in the calendar. That gate is the fix for the audit's one critical finding: the
code used to select prior quarters by quarter order, so a 9 May vintage forecasting 2023Q3 at h=1
was weighted on 2023Q2 errors although 2023Q2 did not print until 3 August. The band's calibration
pool is gated the same way. h=0 is unaffected (at h=0 every earlier quarter has printed); h=1 and
h=2 points move by up to 0.18-0.25pp and are the numbers quoted in §2. Weights are then shrunk
halfway to equal weights
(λ = 0.5, fixed in `prereg.json` before any result, never tuned). Fewer than four prior quarters →
equal weights. The LIVE weights at 2026-09-11 use the whole W1 history, all of which printed
before the vintage. **The weights barely move: 0.146-0.201 at every vintage**, and the
equal-weight spec `stack_ew_clip` scores 1.123 / 0.802 against `stack_clip`'s 1.126 / 0.788.
**The result is a pool result, not a weighting result** — say so rather than dressing it up.

**The clip.** If a quarterly adjusted-EBITDA-margin sentence is in force at the vintage for the
quarter, the point is capped (a "down/lower" ceiling) or floored (an "up/exceeds" floor) at
`y[q−4] + value`. Zero estimated parameters; the sentence is inside the h=0 information set
(WS21 R17). It binds in **2 of 14** backtest quarters (2023Q1, 2023Q2) and helps both times:
W1 MAE 1.195 → **1.126** without / with the clip; W2 unchanged. At LIVE it does **not** bind —
the combination is already below the ceiling.

**The interval.** Split conformal on the combination's own point-in-time errors, k = ⌈(n+1)(1−α)⌉,
never the registry quantiles (which over-cover at 0.91-1.00 against a nominal 0.80 across every
method). Two calibrations are published: **all 14 W1 quarters (qhat80 2.20pp)** and **the last 10,
2024Q1+ (qhat80 2.08pp)**. Three different things must not be run together (WS31 audit 11):

- the **theoretical rank resolution** at this n — the grid a split-conformal interval's coverage can
  sit on, `[0.80, 0.87]` at n 14 and `[0.82, 0.91]` at n 10. This is arithmetic from n. It is *not*
  a coverage measurement, and the earlier phrase "attained coverage 82-91%" is **withdrawn**.
  The columns are now named `rank_grid_cov80_lo/hi`.
- the **observed backtest coverage** of the registered object: h=0 **13 of 14 (W1)** and **10 of 10
  (W2)**, on a different (expanding, PIT) calibration pool. Over-coverage, as everywhere in this build.
- **future** coverage, which neither of the above establishes: the pool was selected after seeing the
  scoreboard and split conformal assumes exchangeability that an expanding-window, regime-shifting
  time series does not give. **The live interval is descriptive until it is validated prospectively.**

The Gaussian-from-MAE cross-check on the recent window is 1.30pp — it disagrees with the conformal
number because the error distribution is fat-tailed (2023Q4 −3.91pp, 2024Q1 −2.60pp against a median
|error| of 0.60pp), and the conformal number is the honest one. `23_bands.csv`.

**Parameters.** The combination adds **2** (λ, fixed a priori, plus the fitted residual scale for
the band) and **inherits 52** from its members (M5-disp 5, M5-flow 6, street 1, M3 1, M2-sent 2,
FAMILY_A 10+12+15). **The registry now carries the honest total, `n_params = 54`**, with the split
in `notes`; it previously published the wrapper's 2 alone (WS31 audit 09). `n_train` now counts the
**prior quarters the weights were fitted on**, not the member count; the member count is
`n_members=<k>` in `notes` and a column of `23_combination_by_quarter.csv` — FORMAT 1.0 is frozen
and its validator rejects unknown registry columns, so a first-class `n_members` column is a harness
change request, not something this package could add. The reason to keep FAMILY_A's 37 is narrative
(it is the only member that says *why* the margin moves), not accuracy — dropping it *improves*
W1 MAE by 0.04pp.

**The revenue leg.** Backtest: the frozen harness guide-cushion / naive leg, untouched. LIVE:
**bridge v3 / WS06 v2b** (3Q26 $4,804M, 4Q26 $3,178M, FY26 $14,268M, FY27 $15,829M,
FY28 $17,137M), as WS22 group C endorsed. Margins are ratios and barely care; every dollar
number on this page uses bridge v3.

---

## 2. The backtest evidence

`data/processed/margin_build/10_harness_margin/scoreboard_margin.csv`, method `final-margin`,
object `combined`, spec `stack_clip`, `prior_basis = PIT`. Every ratio carries its paired
NW(1) p and its quarters-better count, per WS21's kill-list item 2.

### `adj_ebitda_margin_pct`

| window | h | n | MAE | rw MAE | bias | vs seasonal_naive (= the sentence) | vs drift | vs Street | NW(1) t / p vs naive | better in k of n | sign p vs naive | sign p vs Street | cov80 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| W1 | 0 | 14 | **1.126** | 0.823 | −0.67 | **0.504 / rw 0.430** | 0.472 | **0.708 / rw 0.659** | −3.60 / **0.0003** | **11 / 14** | **0.0032** | **0.029** | 0.93 |
| W2 | 0 | 10 | **0.788** | 0.662 | −0.47 | **0.402 / rw 0.377** | 0.390 | **0.601 / rw 0.593** | −3.84 / **0.0001** | **9 / 10** | **0.011** | 0.055 | 1.00 |
| W1 | 1 | 13 | 1.952 | 1.560 | −0.45 | 0.831 / rw 0.807 | 0.499 | **1.189** | −1.08 / 0.28 | 9 / 13 | 0.13 | 0.95 | 0.85 |
| W2 | 1 | 9 | 1.269 | 1.284 | +0.23 | 0.804 / rw 0.802 | 0.362 | **1.278** | −0.76 / 0.45 | 6 / 9 | 0.25 | 0.98 | 1.00 |
| W1 | 2 | 12 | 2.229 | 1.862 | −0.44 | 0.900 / rw 0.950 | 0.614 | — | −0.73 / 0.47 | 6 / 12 | 0.61 | — | 0.75 |
| W2 | 2 | 8 | 1.766 | 1.715 | +0.42 | **1.026** / rw 1.031 | 0.574 | — | +0.14 / 0.89 | 3 / 8 | 0.86 | — | 0.88 |

*(h=1 and h=2 are the post-audit, print-date-gated replay — WS31 audit 01. h=0 is unchanged.)*

### `adj_ebitda_musd` — the **adopted** dollar object, `combined_dollar_from_margin`

The margin combination × the revenue leg. This is the object the card quotes, and it is now
registered, scored and calibrated in its own right (WS31 audit 04).

| window | h | n | MAE $m | rw MAE | vs naive | vs Street | NW(1) t / p vs naive | better than naive, k of n | better than Street | sign p vs Street | cov80 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W1 | 0 | 14 | **30.7** | 24.3 | **0.248** | **0.470 / rw 0.389** | −3.55 / **0.0004** | **13 / 14** | **14 / 14** | **0.0001** | 0.86 |
| W2 | 0 | 10 | **25.8** | 21.4 | **0.264** | **0.445 / rw 0.360** | −3.56 / **0.0004** | **9 / 10** | **10 / 10** | **0.0010** | 0.80 |
| W1 | 1 | 13 | 78.3 | 73.4 | 0.601 | 1.195 | −1.67 / 0.094 | 8 / 13 | 6 / 13 | 0.71 | 0.62 |
| W2 | 1 | 9 | 75.1 | 71.5 | 0.828 | 1.607 | −0.73 / 0.46 | 5 / 9 | 3 / 9 | 0.91 | 0.89 |

### `adj_ebitda_musd` — the four-member dollar combination, **cross-check only**

| window | h | n | MAE $m | rw MAE | vs naive | vs Street | NW(1) t / p vs naive | better in k of n | sign p vs Street |
|---|---|---|---|---|---|---|---|---|---|---|
| W1 | 0 | 14 | 39.7 | 29.7 | 0.322 | 0.608 / rw 0.476 | −3.51 / 0.0004 | 12 / 14 | 0.090 |
| W2 | 0 | 10 | 30.9 | 25.5 | 0.316 | 0.531 / rw 0.429 | −3.56 / 0.0004 | 9 / 10 | 0.011 |
| W1 | 1 | 13 | 75.5 | 70.6 | 0.579 | 1.152 | −1.96 / 0.051 | 9 / 13 | 0.71 |
| W2 | 1 | 9 | 68.5 | 66.9 | 0.756 | 1.466 | −1.16 / 0.24 | 5 / 9 | 0.91 |

### Pass line (pre-registered in `prereg.json` before any result)

| test | result |
|---|---|
| **Primary** — beats `seasonal_naive` on the margin at h=0 **and** h=1, in **both** windows and **both** weightings | **PASS.** 0.504 / 0.402 at h=0; 0.831 / 0.804 at h=1; recency-weighted 0.430 / 0.377 and 0.807 / 0.802. |
| **Secondary** — not worse than the best single non-oracle object by more than 10%, at h=0 | **PASS on the margin** (W1 1.126 vs the best single 1.223 — better; W2 0.788 vs 0.743 — **5.9% worse**, inside the 10% tolerance). **PASS on dollars** (better than every single object in both windows). |
| **Secondary at h=1** | **FAIL.** 1.189x (W1) / 1.278x (W2) the raw Street. The pre-registered consequence applies: **quote the Street for 4Q26**, not the combination. |
| **h=2** | **FAIL** (W2 1.026x the naive). 2027 is a scenario. |
| Reporting rule — every ratio with p and quarters-better; never "survives both windows" alone | honoured throughout. |

Four tests planned, four run, two failures reported.

### Where the accuracy comes from (`23_diag_leave_one_out.csv`)

| variant | W1 MAE | Δ vs full | W2 MAE | Δ vs full |
|---|---|---|---|---|
| **all six + clip** | **1.126** | — | **0.788** | — |
| drop M5 `dispersion_conditioned` | 1.221 | +0.094 | 0.871 | +0.083 |
| drop M5 `street_plus_flowthrough` | 1.163 | +0.037 | 0.869 | +0.082 |
| drop the raw Street | 1.099 | **−0.028** | 0.753 | **−0.034** |
| drop M3 `nov_sentence_pin` | 1.107 | **−0.020** | 0.775 | **−0.012** |
| drop M2 sentence rule | 1.130 | +0.004 | 0.815 | +0.027 |
| drop FAMILY_A | 1.087 | **−0.040** | 0.814 | +0.026 |
| **Street-independent only (M3 + M2-sentence + FAMILY_A)** | **1.419** (0.635x naive) | +0.293 | **1.202** (0.614x naive) | +0.415 |
| no sentence clip | 1.195 | +0.068 | 0.788 | 0.000 |

Read plainly: **the two M5 objects are the accuracy; the Street, M3 and FAMILY_A are insurance**,
and they cost 0.02-0.04pp of MAE for it. The **Street-independent** version still runs at
**0.61-0.63x the seasonal naive** and prints **49.88%** for 3Q26 — within 0.06pp of the full
combination and 0.10pp of the Street. That is the version to quote if anyone objects that a pitch
"above consensus" cannot use consensus as an input. `23_diag_street_independent_live.csv`.

### Regime behaviour (`23_diag_shock_vs_calm.csv`)

| set | n | combination MAE | Street MAE | naive (sentence) MAE |
|---|---|---|---|---|
| all 14 | 14 | **1.126** | 1.592 | 2.237 |
| 1H23 regime break | 2 | **0.792** | 1.343 | 0.792 |
| 2H23 (incl. the $931M lodging-tax quarter) | 2 | 3.055 | 3.246 | 5.073 |
| 1H25 deceleration shock | 2 | **1.615** | 2.219 | 1.298 |
| last four quarters | 4 | **0.446** | 0.690 | 1.805 |

WS20's central worry — that M5's correction was catastrophic in 1H23 (4.68pp) — does not survive
the combination: carrying M3 and the sentence clip puts 1H23 at 0.79pp. The remaining weak set is
2H23, which was hard for everything.

### Hindsight — what this measures, and what it does not

`hindsight_share = (MAE_PIT − MAE_full_sample)/MAE_PIT` at h=0 on the margin: **W1 0.019, W2 −0.059**
(the full-sample replay is *worse* in W2). That says the *weights* contain essentially nothing fitted
on the future. **It says nothing about the selection of the member pool**, which is fixed by hand in
every replay, PIT and full-sample alike (WS31 audit 10).

### The caveat that is not in the p-values — read every number in §2 as retrospective

**The member pool was chosen after seeing the scoreboard**, and there is no historical selection step
and no untouched evaluation set anywhere in this build. It is WS20's and WS22's selection, not a
fresh one — M4 was excluded at 37 parameters, M2's ratio objects at weight 0, M5's
`street_plus_bias` at weight 0, M3's post-hoc pins at weight 0, every oracle spec, and M1's
`d_steps_rw`; and M3's included `nov_sentence_pin` is marked post-hoc in its own note. So:

- Every ratio, p-value and coverage figure above is **retrospective and conditional on the selected
  pool**. They price the combination against the baselines *given* the pool; they do not price the
  pool.
- The **hindsight share and the leave-one-out table are not evidence against selection bias.**
  Small PIT/full-sample differences and leave-one-member-out stability are consistent with a pool
  chosen on the same 14 quarters. They were previously offered that way; that reading is withdrawn.
- WS21's sign-flip null says a two-window survivor flag is ~30% free at this n. The sign tests here
  (p 0.003 / 0.011 against the naive) are well past that, which is a reason to take the h=0 result
  seriously — not a reason to treat the ratios as clean out-of-sample numbers.
- **The model is frozen at this vintage for prospective evaluation.** 5 Nov 2026 is the first
  out-of-sample quarter: one observation, scored against the pre-registered pass line, and the only
  evidence that will not be conditional on the selection.

---

## 3. The forecast set

All base case unless stated. Revenue from bridge v3 / WS06 v2b.
`23_forecast_quarterly.csv`, `23_forecast_annual.csv`, `23_path_rule.csv`.

### Which object supplies which quarter

| quarter | margin source | why |
|---|---|---|
| 3Q26 | `final-margin\|combined\|stack_clip` (h=0) | passes both windows and both weightings against the naive **and** the Street |
| 4Q26 | `baselines-margin\|street` (h=1) | the combination loses to the raw Street by 20-28% at h=1; pre-registered consequence |
| 1Q27-4Q27 | `final-margin\|combined\|stack_clip` (h≥2), **labelled SCENARIO** | h=2 fails in W2 (1.024x naive) |
| FY28 | FY27 margin rolled flat onto FY28 revenue | M6's R15 rule; **an extrapolation, not a forecast** |

### Quarterly

| USD m unless % | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| Revenue | 4,804 | 3,178 | 3,053 | 4,029 | 5,281 | 3,466 |
| Cost of revenue | 617 | 544 | 644 | 688 | 672 | 587 |
| Operations & support | 365 | 318 | 316 | 334 | 378 | 329 |
| Product development | 381 | 376 | 422 | 422 | 432 | 419 |
| Sales & marketing | **781** | **771** | 858 | 993 | 967 | 902 |
| G&A ex reserves | 281 | 272 | 239 | 241 | 302 | 282 |
| *sum of the five lines* | *2,426* | *2,280* | *2,479* | *2,678* | *2,751* | *2,520* |
| *less: D&A add-back* | *20.6* | *20.6* | *20.6* | *20.6* | *20.6* | *20.6* |
| Total cash costs | 2,405 | 2,260 | 2,459 | 2,658 | 2,730 | 2,499 |
| **Adj EBITDA** | **2,399** | **918** | 594 | 1,371 | 2,551 | 967 |
| **Adj EBITDA margin %** | **49.94** | **28.90** | 19.47 | 34.04 | 48.30 | 27.90 |
| 80% band, margin (pp) | 47.9-52.0 | 26.5-31.3 | 15.8-23.1 | 30.4-37.7 | 44.7-52.0 | 24.3-31.6 |
| 80% band, adj EBITDA | 2,337-2,462 | 800-1,037 | 445-744 | 1,222-1,521 | 2,401-2,700 | 817-1,116 |
| SBC | 452 | 465 | 464 | 551 | 511 | 526 |
| D&A | 20.6 | 20.6 | 20.6 | 20.6 | 20.6 | 20.6 |
| **GAAP operating income** | **1,927** | **433** | 110 | 799 | 2,019 | 420 |
| GAAP operating margin % | 40.11 | 13.61 | 3.60 | 19.84 | 38.23 | 12.11 |
| Interest income | 184 | 170 | 185 | 208 | 196 | 176 |
| Interest expense | 37 | 37 | 37 | 37 | 37 | 37 |
| Pretax income | 2,077 | 569 | 262 | 974 | 2,182 | 562 |
| Effective tax rate % | 18.0 | 18.0 | 17.5 | 17.5 | 17.5 | 17.5 |
| **Net income** | **1,703** | **467** | 216 | 804 | 1,800 | 464 |
| Diluted shares (m) | 591.7 | 586.4 | 581.0 | 575.7 | 570.4 | 565.1 |
| **EPS, diluted** | **2.88** | **0.80** | 0.37 | 1.40 | 3.16 | 0.82 |
| EPS 80% band (joint) | 2.70-3.05 | 0.64-0.95 | 0.18-0.56 | 1.16-1.63 | 2.86-3.45 | 0.61-1.03 |

The margin band is the combination's own conformal band; the **adj EBITDA band is the adopted
dollar object's own** (not the margin band re-multiplied by revenue), so the point, the band and
P(beat) are one object throughout (WS31 audit 04). The **EPS band is joint**: the EBITDA term and
M7's measured below-EBITDA bridge error (sd $0.083, W2 h=0 with EBITDA known) combined in
quadrature. The EBITDA-only version is kept in `23_forecast_quarterly.csv` as
`eps_q10/q90_ebitda_only` and is the number the pre-audit file published (WS31 audit 06).

**EPS is quoted one way only because GAAP diluted EPS *is* the Street definition for ABNB** (LSEG
`TR.EPSMean` is the GAAP diluted number; M7 confirmed the bridge reproduces the Street's own
$2.845 from the Street's own EBITDA to within $0.02). Where the two would differ is SBC treatment,
and no vendor in our panel runs an ex-SBC EPS for ABNB. The second "way" the discussion asked for
is therefore the **sensitivity**: `d(EPS)/d(adj EBITDA) = (1 − ETR)/shares = $0.001386 per $M`,
i.e. **$0.0666 of 3Q26 EPS per 1pp of margin**. Anyone with a different EBITDA can re-price EPS in
one multiplication.

**Quarterly free cash flow is not forecast.** M7's quarterly FCF object failed its pre-registered
line (1.018x the naive in W1, 0.927x in W2 equal-weighted; 1.090 / 1.054 recency-weighted) and
`fcf_margin_pct` is worse than the naive in both windows. The quarterly CFO/FCF columns exist in
`23_forecast_quarterly.csv` labelled `_diagnostic` and must not be quoted.

### Annual

| | FY26 | FY27 | FY28 |
|---|---|---|---|
| Revenue | 14,268 | 15,829 | 17,137 |
| **Adj EBITDA** | **5,098** | **5,483** | 5,937 |
| **Adj EBITDA margin %** | **35.73** | **34.64** | 34.64 *(flat roll-forward)* |
| bear / bull margin % | 35.42 / 36.10 | 32.15 / 36.53 | 32.15 / 36.53 |
| SBC | 1,814 | 2,053 | 2,323 |
| GAAP operating income | 3,204 | 3,348 | 3,531 |
| GAAP operating margin % | 22.45 | 21.15 | 20.60 |
| Net income | 3,146 | 3,284 | 3,459 |
| Diluted shares (m) | 595.8 | 573.0 | 551.7 |
| **EPS, diluted** | **5.28** | **5.73** | 6.27 |
| FY FCF, mid | 4,844 | 5,297 | 5,731 |
| FY FCF, bias-adjusted (−$399M) | **4,445** | **4,898** | 5,332 |
| FY FCF margin % | 34.0 | 33.5 | 33.4 |

FY26 and FY27 net income and tax are now the **sum of the quarters** (1H26 actual + our two
forecast quarters for FY26), with the annual ETR derived afterwards rather than an old annual rate
re-applied (WS31 audit 15; FY26 base NI 3,145.9 → 3,146.1). FY28, which has no quarterly build,
keeps the annual-rate route and says so in the `ni_basis` column. The FCF rows are rebuilt from the
updated **net income**, carrying M7's working-capital and other block across, instead of moving CFO
by the pretax EBITDA delta (WS31 audit 07: the omitted tax effect was $13.6-15.7M).
**The bear/bull rows are now the flex cost response** (M6 k = 0.364 on total cash costs), not the
base margin on a different revenue — which is why the FY27 spread widens from 34.51-34.71% to
32.15-36.53% (WS31 audit 05).

**FCF is annual only and is a range, not a point.** M7's annual FCF rule beat the prior-FY-actual
naive in 3 of 4 years with a **+$399M mean high bias**; the bias-adjusted row is the low end.
**FY26 FCF $4.4-4.8bn** against Street $4.92bn.

### Versus consensus, management and the prior team numbers (`23_vs_consensus.csv`)

| period | model adj EBITDA | LSEG (11 Sep) | gap $ | model margin | LSEG margin | gap pp | LSEG n / sd |
|---|---|---|---|---|---|---|---|
| **3Q26** | **2,399** | 2,361.5 | **+38** | **49.94** | 49.78 | **+0.16** | 36 / $20.0M |
| 4Q26 | 918 | 913.7 | +5 | 28.90 | 28.90 | 0.00 | 36 / $26.5M |
| 1Q27 | 594 | 610.7 | −16 | 19.47 | 20.29 | −0.82 | 19 / — |
| 2Q27 | 1,371 | 1,451.7 | −80 | 34.04 | 35.96 | −1.92 | 19 / — |
| 3Q27 | 2,551 | 2,695.6 | −145 | 48.30 | 51.15 | −2.85 | 17 / — |
| 4Q27 | 967 | 1,068.4 | −102 | 27.90 | 30.28 | −2.38 | 17 / — |
| **FY26** | **5,098** | 5,053.7 | **+44** | **35.73** | 35.62 | **+0.11** | 44 / $40.2M |
| **FY27** | **5,483** | 5,766.1 | **−283** | **34.64** | 36.45 | **−1.81** | 44 / $154.2M |
| FY28 | 5,937 | 6,602.7 | −666 | 34.64 | 37.65 | −3.01 | 26 / $271.9M |

Bloomberg BEST (5 Sep pull, not point-in-time): 3Q26 $2,359.9M, FY26 $5,046.8M — inside $7M of
LSEG on both. The **quoted** dollar number, $2,399M, is the adopted construction (margin × revenue,
`final-margin|combined_dollar_from_margin`, W1/W2 h=0 MAE $30.7M / $25.8M). The separately-built
four-member dollar combination (`final-margin|combined|stack_clip` on `adj_ebitda_musd`, MAE
$39.7M / $30.9M) reads **$2,411M** and is published as a **cross-check**; it is not the object the
band or the beat probability come from (WS31 audit 04).

The dispersion columns in `23_vs_consensus.csv` are now `lseg_revenue_sd_musd` and
`lseg_ebitda_sd_musd` — the old single `lseg_sd_musd` silently carried revenue sd on quarterly rows
and EBITDA sd on annual rows (WS31 audit 14). The EBITDA sds quoted in the table above (3Q26 $20.0M,
4Q26 $26.5M, FY26 $40.2M, FY27 $154.2M) were already the right quantity and are unchanged.

- **Management.** 3Q26 "margin down slightly vs Q3 2025" → ceiling 50.085%; we are 0.15pp under.
  FY26 "at least 35.5%" → we are +0.23pp over.
- **WS30 margin walk** (3Q26 50.80% / 4Q26 29.70%): 0.86pp high on Q3, 0.80pp high on Q4. Directionally
  the same view; not carried.
- **WS31b forward profiles** (3Q26 51.3-52.2% / **4Q26 24.7-25.9%**): the 4Q26 leg is **3-4pp below every
  method in this build and below the Street**, and is **not carried**. It is the incumbent repo margin
  model and it should not be cited anywhere until it is reconciled (WS20 open question 12 — still open).
- **WS07 lever model**: consistent on the per-night cost levels; nothing carried forward as a forecast.

### FY26 incremental margin, and why FY27 is the trade

| | FY26 | FY27 |
|---|---|---|
| model incremental margin | 39.5% | **24.7%** |
| Street's implied incremental margin | 38.8% | **43.7%** |

FY26 and the Street agree. **FY27 is a 19pp disagreement about incremental margin**, and it is
entirely a statement about sales & marketing: on our path FY27 S&M is $3,740M, **23.6% of revenue**,
against 21.5% in FY26 and 19.4% in FY25. The Street's FY27 requires the ramp to stop. That is a
spending decision, and the company has given no FY27 margin guidance — WS05 found no FY27 margin
hint in any letter or call.

---

## 4. Cyclicality

`23_seasonality.csv`, `23_macro_sensitivity.csv`, `23_fy26_floor_breakeven.csv`.

### Seasonal profile, and the mechanical / discretionary split

| quarter | revenue share (2022-26 avg) | our margin | historical mean margin 2022-26 (sd) | mechanical cost (CoR + Ops) % rev | discretionary (PD + S&M + G&A) % rev |
|---|---|---|---|---|---|
| Q1 | 19.4% | 19.47 (1Q27) | 17.42 (2.47) | 31.5 | 49.8 |
| Q2 | 26.1% | 34.04 (2Q27) | 33.59 (0.92) | 25.4 | 41.1 |
| Q3 | **32.8%** | 49.94 (3Q26) / 48.30 (3Q27) | **51.76 (1.81)** | 20.5 | 30.0 |
| Q4 | 21.8% | 28.90 (4Q26) / 27.90 (4Q27) | 29.75 (2.92) | 27.1 | 44.6 |

Two readings. **(a) The seasonality is a revenue phenomenon, not a cost one.** The mechanical cost
lines move 20.5% → 31.5% of revenue from Q3 to Q1 almost entirely because the denominator halves;
in dollars cost of revenue runs $544-688M and operations & support $316-378M across all six
forecast quarters — a 27% and 20% peak-to-trough range against revenue's 73%. **(b) The
discretionary block is the only thing that could smooth it and does not.** Product development,
S&M and G&A together run $1,418-1,701M *every quarter* regardless of season — the 1Q27 trough is a
19.5% margin because $1,519M of discretionary spend meets $3,053M of revenue. **3Q26 at 49.94% is
1.0 standard deviations below its own seasonal mean (51.76%)**, and that gap is the ramp.

### Macro sensitivity — margin change per 1pt of revenue shortfall

| period | costs held (k = 0) | costs flex at M6's k = 0.364 | costs flex one-for-one (never observed) |
|---|---|---|---|
| 2H26 | **0.59pp** | 0.38pp | 0.00pp |
| FY26 | **0.36pp** | 0.24pp | 0.03pp |
| FY27 | **0.66pp** | 0.42pp | 0.00pp |

The honest default is somewhere between "held" and "flex": M6's fitted elasticity of total cash
costs to revenue is 0.364 (t 6.58), but it is **asymmetric** — `k_down < k_up` for operations,
S&M and total cash costs at p < 0.02, i.e. Airbnb cuts less readily than it spends, and flexing
recovers only 30-40% of a revenue miss. **Use 0.35-0.6pp of FY27 margin per 1pt of revenue.**

### The FY26 floor break-even

| cost response | FY26 margin | cushion over 35.5% | 2H26 revenue shortfall that breaks the floor |
|---|---|---|---|
| held | 35.73% | **+0.23pp** | **0.63% ($50M)** |
| flex (k 0.364) | 35.73% | +0.23pp | **0.94% ($75M)** |
| one-for-one | 35.73% | +0.23pp | 6.68% ($533M) |

This is materially tighter than the 1.9-2.5% ($149-203M) M6 originally published, and it is the
version WS22 group A already restated. **The FY26 floor is a 4Q26 question**: at our 3Q26, holding
FY26 at exactly 35.5% requires 4Q26 of only 27.6%, and every path in the build is above that — but
there is less than one point of revenue between the guide and a miss.

---

## 5. The 5 November card

`23_card_5nov.csv`, `23_card_budget_identity.csv`.

| | number | band / comparison |
|---|---|---|
| **3Q26 adj EBITDA margin** | **49.94%** | 80% band 47.9-52.0, descriptive (see §1 on coverage); vs Street 49.78%, vs the 50.085% ceiling |
| **3Q26 adj EBITDA** | **$2,399M** | 80% band **$2,337-2,462M** (the adopted dollar object's own conformal qhat80 62.6); four-member dollar cross-check $2,411M; vs Street $2,361.5M |
| **Beat vs Street, dollars** | **+$38M** (dollar cross-check +$50M) | M5 flow-through arithmetic: 0.464 x (4,804 − 4,744) + 16 = **+$44M** |
| **P(3Q26 adj EBITDA beats Street)** | **0.78** | Gaussian, sd = qhat80 / 1.2816 = $48.8M, **on the same object as the band**. The previously published **0.77 is withdrawn** — it took the band from the margin route and the sd from the four-member dollar object. Descriptive, not validated: n 10 calibration, post-selection pool |
| P(3Q26 **margin** beats the Street's margin) | 0.54 | the margin call is a coin flip; **the dollar call is not** |
| **3Q26 EPS** | **$2.88** | 80% band **$2.70-3.05** (joint: EBITDA term + M7 bridge sd $0.083); vs Street $2.845 (n 34, sd $0.152) |
| **4Q26 margin** | **28.90%** (Street) | combination 29.04%; M3's guide path 29.90%; range to quote **28.9-29.9%** |
| **FY26 margin** | **35.73%** | floor 35.5%, Street 35.62%; cushion +0.23pp |
| **FY26 adj EBITDA** | **$5,098M** | vs Street $5,053.7M |
| **The margin sentence management gives on 5 Nov** | **"approximately 36%"** | M3: the November sentence has been the numeric floor + 50bp, **exact 2 of 2**; p ≈ 0.45-0.50 |
| **4Q26 implied by that sentence at our 3Q26** | **30.12%** | vs Street 28.90% — **the contestable number** |
| FY27 margin (scenario) | 34.64% | vs Street 36.45% |

**The budget identity, which is how to trade the guide.** With 1H26 actual ($6,286M revenue,
$1,780M adj EBITDA) and FY26 revenue $14,268M:

> **1pp of the FY26 margin sentence = 4.49pp of 4Q26 margin. 1pp of 3Q26 margin = −1.51pp of 4Q26.**

| FY26 sentence | 3Q26 = 49.4% | 3Q26 = 49.94% (us) | 3Q26 = 50.085% (the ceiling) |
|---|---|---|---|
| 35.50% (floor held) | 28.4% | **27.6%** | 27.4% |
| 35.75% | 29.5% | 28.7% | 28.5% |
| **36.00% (our sentence forecast)** | **30.9%** | **30.1%** | **29.9%** |
| 36.50% | 33.2% | 32.4% | 32.2% |

So the 5 Nov trade has two legs and they point the same way: **Q3 prints at or just under the
ceiling with a $38-50M dollar beat, and the FY sentence goes to "approximately 36%", which asks
the Street to raise 4Q26 by roughly 1.2pp / $39M.**

**The floor case is an inequality, and must be read as one (WS31 audit 12).** If management leaves
the sentence at "at least 35.5%", the arithmetic says only that **4Q26 ≥ ~27.6%** at our 3Q26 and
revenue. It does *not* say 4Q26 will be 27.6%: our own adopted 28.90% already satisfies it, as does
the Street's 28.90% and M3's 29.90%. An unchanged floor is therefore **the absence of a raise, not a
guide-down**, and whether the absence of a raise is a sell is a price-reaction question this build
has not tested — the reaction study is `research/notes/predictive/04_margin-and-reaction.md`, and
nothing in it was re-run here. Three separate objects: a **guide-floor calculation**, a **forecast
of the actual**, and a **tested price reaction**. Only the first is on this page.

### What 5 November settles

1. **The 10-Q sales-and-marketing split** — brand vs performance. Our 3Q26 S&M of $781M (+33.5% y/y)
   is the whole call; the split says whether the ramp is a fixed brand commitment or a variable
   performance spend that can be dialled down. Nothing else in the filing matters as much.
2. **Whether the "down slightly" sentence was a ceiling or a floor.** The quarterly sentence has
   been *missed* slightly more often than beaten (W2 mean −0.19pp, median −0.94pp, 4 of 10 above),
   which is why we clip rather than override — but the 60-140bp FY beat pattern is real and the
   quarter is the test.
3. **The FY26 sentence itself** (35.5% held vs "approximately 36%") — the 4.49x amplifier above.
4. **The SBC line.** Our FY26 EPS of $5.28 sits *below* Street's $5.31 on an EBITDA that is $44M
   *above* it. The difference is SBC and the share count, not operations. The 10-Q settles it.
5. **The G&A line.** Our reconciled 3Q26 G&A of $281M is +9.4% y/y, while 1H26 actually ran
   **−5.4% y/y**. That is the weakest number in our line stack (see §6).
6. **Interest income** at $184M — M7's one genuine below-the-line edge (MAE $17.9M W1 / $10.5M W2,
   0.81x / 0.68x the hardest baseline on one fitted parameter) — is the cleanest check that the
   bridge is calibrated.

### Three numbers the pitch should quote, with their bands

1. **3Q26 adjusted EBITDA $2,399M, 80% band $2,337-2,462M, against a Street $2,361.5M** — a
   $38-50M beat with P ≈ 0.78, driven by our revenue being $60M above the Street's, not by a margin view.
2. **FY26 adjusted EBITDA margin 35.73%, cushion over the floor +0.23pp, break-even on a
   0.6-0.9% 2H26 revenue miss** — the guide is tighter than it looks.
3. **FY27 adjusted EBITDA $5,483M / 34.6% margin against a Street $5,766M / 36.45%, an incremental
   margin of 24.7% against 43.7%** — labelled a spending scenario, and the reason is S&M at 23.6%
   of revenue.

---

## 6. What was tried and failed (one line each, with numbers)

**Inside WS23**

- The combination **loses to the raw Street at h=1** (1.189x W1 / 1.278x W2, post-audit replay) — the pre-registered secondary test failed and 4Q26 is quoted from the Street.
- The combination **fails outright at h=2 in W2** (1.026x the seasonal naive, post-audit replay) — 2027 is a scenario.
- The **weights do almost nothing**: inverse-MAE with λ = 0.5 produces 0.146-0.201 at every vintage and equal weights score 1.123 / 0.802 against 1.126 / 0.788. The λ grid (0.25 / 0.5 / 1.0) moves W1 MAE by 0.007pp.
- The **intervals still over-cover**: cov80 0.93 (W1) / 1.00 (W2) against a nominal 0.80 at h=0, even on a conformal band. At n 10-14 a split-conformal interval cannot be tuned finer than the rank grid; and observed backtest coverage is not a coverage guarantee for a selected model (§1).
- The **line residual allocation is mechanical and produces one uncomfortable number**: G&A at +9.4% y/y for 3Q26 against a 1H26 actual of −5.4% y/y. Allocating by PIT error variance puts 76.6% of the residual in S&M, 9.4% in product development and 14.0% in G&A; the economics argue for more in S&M still.

**From the method notes**

- **M1 (driver lines).** Both pre-registered pass lines failed. `b_elastic_rw` at h=0 is a **tie with y[q−4]** (1.010 W1 / 0.975 W2, t +0.07, p 0.95, better in 7 of 14) and the Street is 1.3-1.5x more accurate. "Every line but G&A beats the naive by 20-70%" and "total cash costs 0.27 / 0.22 — the cost stack is forecastable" are **withdrawn**: against a drift baseline total cash costs run **1.165x**. `d_steps_rw` was not point-in-time (WS21 R04) and is on the kill list. Its surviving claim is cost of revenue alone (b 0.81 on GBV, 0.753x drift, p 0.042, 9 of 14).
- **M2 (time series).** No object built from ABNB's own history beats last year's margin by a distinguishable amount. The best (the sentence rule, 2 parameters) is 0.92x the naive in W1 with **t −0.22, p 0.83, 7 of 14**, and 1.25-1.30x the Street. Its SARIMA LIVE 3Q26 of 51.50% is **disowned by its own author**; its `incremental_margin` FY27 path is disowned; its h=1 rows are **n = 1**.
- **M3 (guide policy).** The pre-registered main spec `rw_hl4` **failed P1** (3.83pp vs a naive 2.24pp). The FY cushion **over-predicts by 1.2-3.2pp point-in-time** (P2 failed; the literal guide beats every cushioned version, 1.22 vs 2.75pp) and **cannot be estimated on more than four fiscal years**. The registered LIVE 4Q26 of 34.51% / FY26 37.03% is **withdrawn and stamped NOT QUOTABLE**. The February floor is not mechanical (82bp MAE, wrong in both years that mattered). What survives is the **allocation result** (`m[q−4] + delta` beats the harness proration 0.546x W1 / 0.669x W2, p 0.028 / 0.030, 12 of 14 and 9 of 10) and the **budget identity**.
- **M4 (alt data).** **Fifty pre-registered point-in-time tests** under a strict `knowable_from` gate produced **one** survivor (G&A on computer-systems-design employment, lead 2, IV 0.895), which its own **1,000-draw random-series placebo** says fires on noise **5.5% of the time per G&A test and 22.5% under best-of-5**; across 50 tests the null expects 1.0 and we observed 1. Alt data moves margin MAE by 0.6% / 0.1% and 3Q26 by +0.13pp.
- **M5 (Street bias).** The **margin** claim is withdrawn (t −0.57 W1 / −1.46 W2, not significant). The dispersion conditioning adds **nothing** over a fixed "half the bias" constant (t −0.16, p 0.87, better in 6 of 14; t −1.16, p 0.25, better in **4 of 10**). Roughly **two-thirds of its LIVE beat was the 0.5 clip floor**, and the backtest prefers **no floor at all** (equal-or-better in all ten cells). The dispersion slope off the pre-registered pool is **+17.1, p 0.052**, not +28.3, p 0.005. Quantiles cov80 = cov90 = **1.00**. **Every h=1 correction is worse than doing nothing.**
- **M6 (cycle flex).** The forecaster is a tie (`l0_rw` t −0.10, **p 0.92**, 7 of 14) and fails at h≥1. **FY28 (31.3%) is withdrawn.** The FY26 floor-cushion claim was restated from "survives a 1.9-2.5% 2H26 shortfall" to **0.24-0.68%**. `k_pd` (−0.21) and `k_ga` (−0.11) are wrong-signed and insignificant. What survives is the **measurement**: `k_cor` 0.56 (0.652x / 0.677x drift, t −3.57 / −2.67, **p 0.0004 / 0.008**, 13 of 14 and 9 of 10) and the peer table.
- **M7 (below EBITDA).** **Quarterly FCF fails** (1.018 W1 / 0.927 W2 equal, 1.090 / 1.054 recency); `fcf_margin_pct` is worse than the naive in both windows; `cfo_musd` likewise. The self-reported "tax quantiles under-cover" is **withdrawn** — **0 of 128** h=0 cov80 cells sit below the exact binomial band and the mean is 0.941. Against the Street the EPS bridge is 0.94x / **1.04x** — **no alpha, by design**.
- **The harness.** `survives_both_windows` has a **~30% null pass rate** at this n (22.1 expected vs 25 observed, P 0.39); W2's ten quarters are a **subset** of W1's fourteen. Gating on significance cut margin h=0 survivors from 26 object-spec pairs to **7**, six of them M5.

---

## 7. The alt-data verdict

**There is no external dataset within our reach that improves the 3Q26 margin call.** M4 ran 50
pre-registered point-in-time tests across employment series, PPI, Google Trends, Play Store
ratings, careers-page postings, peer disclosures and event markers, under a `knowable_from` gate
and with 47 leakage placebos; the one survivor is indistinguishable from noise at the rate its own
placebo predicts. Two derived results are more valuable than any of the signals:

1. **A calibrated false-positive prior.** An unvalidated alt-data cost regressor costs **1-5% of
   margin accuracy**; a line-level pass line of the kind the scoreboard uses fires on pure noise
   **2.5-22.5%** of the time; and **18 of 50** real tests beat 1.0 in both windows — 36%, the
   coin-flip rate. Any future alt-data claim on this name needs a best-of-k placebo before it is
   believed.
2. **Good lines do not make a good margin.** The object with the best cash lines in the build
   (`lines_aug|best1_rw`, mean line ratio 0.549 to the naive) is one of the **worst on margin**
   (1.101x). The mechanism is specific and worth putting in the memo: S&M is the largest cash line
   and M1's S&M error is **negatively correlated** with the rest of the stack's, so "improving"
   S&M in isolation removes a hedge. **Select on `adj_ebitda_margin_pct`; report line ratios only
   against `seasonal_naive_drift`.**

The alt-data work that *does* feed the pitch is on the revenue side (the reviews-based nights
index, the calendar pace, the ADR card), not the margin side.

---

## 8. Open items

1. **WS31b's forward profiles put 4Q26 margin at 24.7-25.9%** — 3-4pp below every method in this build and below the Street. It is the incumbent repo margin model. Either reconcile it or retire it before anything cites it. (WS20 open question 12, unanswered.)
2. **The LIVE bridge-v3 revenue leg is applied by hand in WS23.** WS22 group C specified a `revenue_leg_live.csv` with a `leg` column (`baseline_pit` | `bridge_v3`) and ~30 lines in `baselines.py` / `build_live.py`. Until it exists, every other package's LIVE dollar rows still carry the harness naive leg (4Q26 $3,237M against bridge v3's $3,178M, FY27 $16,709M against $15,819M).
3. **There is no 4Q26 object with an edge.** The combination loses to the Street at h=1 in both windows. Before finals, the highest-value single piece of work is a genuine h=1 object — the obvious candidate is the November sentence itself, which does not exist until the 5 Nov letter, i.e. the trade into the print is structurally an h=1 position (WS21 R17).
4. **M7's FRED inputs have no re-pull fallback** (WS21 R13); the six-line patch is written into M7's note and was not applied because `run.py` shells out to `score.py`.
5. **The member pool selection is not priced** — see the caveat in §2.
6. **FY26 EPS is below Street on an above-Street EBITDA** ($5.28 vs $5.31 on +$44M). The gap is SBC and the share count. Worth a dedicated check before the memo.
7. **The G&A line in the reconciled stack (+9.4% y/y for 3Q26) contradicts the 1H26 actual (−5.4% y/y).** The residual allocation rule is mechanical; a judgement version would put more of the residual in S&M.
8. **FY28 has no model.** It is the FY27 margin rolled flat. M1's trend extrapolation gives 32.6%; M6's 31.3% is withdrawn; the Street is at 37.65%. Do not put an FY28 margin in the memo without the label.

---

## 9. For the pitch — quotable statements and their evidence

| statement | evidence |
|---|---|
| "3Q26 adjusted EBITDA $2,399M against a Street $2,361.5M, an 80% band of $2,337-2,462M and a 78% probability of a beat — band and probability both from `final-margin\|combined_dollar_from_margin`, which runs at 0.47x / 0.44x the Street's h=0 dollar error, better in 14 of 14 and 10 of 10 quarters." | `23_card_5nov.csv`, `23_forecast_quarterly.csv`, `23_bands.csv`, `scoreboard_margin.csv` |
| "The beat is dollars, not margin: our revenue is $60M above the Street's and the fitted flow-through is 0.464, so 0.464 x 60 + 16 = +$44M." | M5 `M5_discussion_summary.json`; `docs/margin-build/notes/M5_street_bias.md`; `23_card_5nov.csv` |
| "Our combined margin object beats the seasonal naive 2:1 and the Street 3:2 at h=0, in both windows and both weightings, better in 11 of 14 and 9 of 10 quarters, sign-test p 0.003 and 0.011 — retrospectively and conditional on a pool selected after seeing the scoreboard, on 2 wrapper parameters and 52 inherited." | `10_harness_margin/scoreboard_margin.csv` rows `final-margin|combined|stack_clip`; `23_combination_scores.csv` |
| "Without touching consensus at all, the same machinery prints 49.88% for 3Q26 and runs at 0.61-0.63x the naive." | `23_diag_street_independent_live.csv`, `23_diag_leave_one_out.csv` |
| "Management's quarterly margin sentence has been *missed* slightly more often than beaten — W2 mean −0.19pp, median −0.94pp, above in 4 of 10 — so we treat 'down slightly' as a real ceiling, not sandbagging." | `M1_driver_lines_live_guide_reconciled.csv`; `docs/margin-build/DISCUSSION.md` group A Q6 |
| "The FY26 'at least 35.5%' floor breaks on a 2H26 revenue shortfall of 0.6-0.9%, about $50-75M." | `23_fy26_floor_breakeven.csv` |
| "1pp of the FY26 margin sentence is 4.49pp of 4Q26 margin. At 'approximately 36%' and our Q3, 4Q26 has to be 30.1% against a Street 28.9%; at an unchanged 'at least 35.5%' the identity gives only 4Q26 ≥ ~27.6%, which our own 28.9% already clears." | `23_card_budget_identity.csv`; M3 note |
| "The November sentence rule — numeric floor plus 50bp — has been exact 2 of 2." | `docs/margin-build/notes/M3_guide_policy_margin.md`; `05_mgmt_statements_v2/05_nov2026_scenarios.csv` |
| "FY27 incremental margin 24.7% against the Street's implied 43.7%, and the whole gap is S&M at 23.6% of revenue." | `23_forecast_annual.csv`, `23_vs_consensus.csv`, `23_lines_quarterly.csv` |
| "We cannot measure a cost dial at Airbnb: total opex elasticity to revenue 0.14 with t 0.47, n 18 — SE 0.30, 95% interval roughly −0.44 to +0.72, which does not exclude BKNG's 0.61, TRIP's 0.63 or EXPE's 0.44. Imprecise, not zero; the model uses M6's cash-cost elasticity 0.364 on a different cost definition." | `M6_cycle_flex_peer_k.csv`; WS31 audit 13 |
| "Cost of revenue is the only cost line anywhere in this build that beats a drift baseline: k 0.56, 0.65x / 0.68x, t −3.57 / −2.67, p 0.0004 / 0.008, better in 13 of 14 and 9 of 10." | `M6_cycle_flex_k_table.csv`; `22_discussion_group_A/groupA_paired_vs_drift.csv` |
| "Flexing costs recovers only 30-40% of a revenue miss, and the response is asymmetric — k_down < k_up for operations, S&M and total cash costs at p < 0.02." | M6 note; `23_macro_sensitivity.csv` |
| "$0.0666 of 3Q26 EPS per 1pp of margin; interest income $184M, ETR 18.0%, 591.7m diluted shares." | `M7_parameter_sheet.csv`; `23_forecast_quarterly.csv` |
| "No external dataset we can reach improves the margin call; a line-level pass line of this kind fires on pure noise 2.5-22.5% of the time." | `docs/margin-build/notes/M4_alt_augmented.md` |

**Do not quote** (AGENT_BRIEF §6 + WS21's addendum + WS22's): M3's LIVE 4Q26 34.51% / FY26 37.03%;
M6's FY28 31.3%; M5's "+0.41pt beat" as a model output; M5's dispersion slope +28.3 / p 0.005;
M1's `d_steps_rw` numbers; any oracle spec (`*revknown*`, `*nightsknown*`, `*ebitda_known*`) as a
forecast; "survives both windows" as evidence of skill; any margin MAE ratio without its p-value
and quarters-better count; "the line model beats the naive" without re-scoring on
`adj_ebitda_margin_pct`; any quarterly FCF forecast; "M7's tax quantiles under-cover";
M6's "the FY26 floor survives a 1.9-2.5% 2H26 revenue shortfall"; **and, added by WS31:** the
**77% beat probability** and the old **$2,299-2,499M** 3Q26 dollar band (the two came from
different objects); **"attained coverage 82-91%"** as a coverage claim; **"Airbnb has no cost
dial"**; the hindsight share or the leave-one-out table as **evidence against selection bias**;
and any reading of an unchanged "at least 35.5%" as implying a 27.6% 4Q26 **point** or an
automatic sell.

---

## 10. File map

**Code** — `analysis/src/margin_build/23_final_model/`: `prereg.json`, `combine.py`,
`diagnostics.py`, `forecast.py`, `workbook.py`, `run.py`, `README.md`.

**Data** — `data/processed/margin_build/23_final_model/`:
`23_combination_by_quarter.csv`, `23_combination_weights.csv`, `23_combination_scores.csv`,
`23_combination_live.csv`, `23_conformal.csv`, `23_path_rule.csv`, `23_bands.csv`,
`23_lines_quarterly.csv`, `23_forecast_quarterly.csv`, `23_forecast_annual.csv`,
`23_vs_consensus.csv`, `23_scenarios.csv`, `23_seasonality.csv`, `23_macro_sensitivity.csv`,
`23_fy26_floor_breakeven.csv`, `23_card_5nov.csv`, `23_card_budget_identity.csv`,
`23_diag_leave_one_out.csv`, `23_diag_member_scores.csv`, `23_diag_shock_vs_calm.csv`,
`23_diag_street_independent_live.csv`, and (new, WS31) `23_dollar_from_margin_by_quarter.csv`,
`23_dollar_from_margin_live.csv`, `23_dollar_from_margin_scores.csv`. The pre-audit versions of
every file whose numbers moved are in `_pre_audit/`.

**Registry** — `data/processed/margin_build/registry/final-margin__combined.csv` (1,152 rows;
specs `stack_clip`, `stack`, `stack_lam25_clip`, `stack_ew_clip`; PIT and full_sample; W1 / W2 / LIVE)
and `final-margin__combined_dollar_from_margin.csv` (576 rows, the adopted dollar object).
Both scored into `data/processed/margin_build/10_harness_margin/scoreboard_margin.csv`.
Pre-audit backup: `final-margin__combined_pre_audit.csv.bak`.

**Workbook** — `model/ABNB_margin_model.xlsx` (README, Inputs, Lines, Bridge, Scenarios,
Consensus, Seasonality, Weights, Card).

**Audit** — `docs/margin-build/audit/CODEX_ASTRA_AUDIT.md` (the 18 findings) and
`docs/margin-build/audit/AUDIT_RESPONSE.md` (the triage table and what changed).

**Notes** — this file; `docs/margin-build/notes/23_triangulate.md`; the method notes
`M1_driver_lines.md` … `M7_below_ebitda.md`, `10_harness_margin.md`, `20_scoreboard.md`,
`21_red_team.md`, `01_input_census.md` … `06v_fy27_path_check.md`; `docs/margin-build/DISCUSSION.md`.

---

## 11. Post-audit changes (WS31, 14 Sep 2026)

Applied from `docs/margin-build/audit/CODEX_ASTRA_AUDIT.md`; triage in
`docs/margin-build/audit/AUDIT_RESPONSE.md`. Rebuild:
`py -3.13 analysis/src/margin_build/23_final_model/run.py` (exit 0, ends by calling `score.py`),
then `py -3.13 analysis/src/margin_build/20_scoreboard/run.py` (exit 0). Both were re-run in that
order, sequentially. A no-write audit mode now exists: `MARGIN_VERIFY_ONLY=1` recomputes into
`_verify/`, writes nothing, runs the same assertions and prints a per-file comparison.

### Every number that moved

| what | before | after | why |
|---|---|---|---|
| **h=1 margin MAE, W1 / W2** | 1.962 / 1.275 | **1.952 / 1.269** | 01 print-date gate |
| h=1 vs seasonal naive, W1 / W2 | 0.835 / 0.808 | **0.831 / 0.804** | 01 |
| h=1 vs Street, W1 / W2 | 1.196 / 1.285 | **1.189 / 1.278** | 01 (still a FAIL; 4Q26 stays the Street's) |
| **h=2 margin MAE, W1 / W2** | 2.255 / 1.762 | **2.229 / 1.766** | 01 |
| h=2 vs naive, W2 | 1.024 | **1.026** | 01 (still a FAIL; 2027 stays a scenario) |
| h=2 cov80, W1 | 0.83 (10/12) | **0.75 (9/12)** | 01 |
| h=1 dollar MAE (4-member), W1 / W2 | 75.3 / 69.0 | **75.5 / 68.5** | 01 |
| **3Q26 adj EBITDA 80% band** | $2,299-2,499M | **$2,337-2,462M** | 04 — the adopted object's own conformal qhat80 ($62.6M), not the margin band re-multiplied by revenue |
| **P(3Q26 adj EBITDA beats Street)** | 0.77 | **0.779** | 04 — same object as the band, sd $48.8M |
| 4Q26-4Q27 adj EBITDA bands | margin-implied | **adopted-object bands** (e.g. 4Q26 $800-1,037M) | 04 |
| **3Q26 EPS 80% band** | $2.74-3.02 | **$2.70-3.05** | 06 — M7 bridge sd $0.083 added in quadrature |
| 4Q26 / 1Q27 / 2Q27 / 3Q27 / 4Q27 EPS bands | 0.68-0.91 / 0.20-0.54 / 1.17-1.62 / 2.86-3.45 / 0.62-1.02 | **0.64-0.95 / 0.18-0.56 / 1.16-1.63 / 2.86-3.45 / 0.61-1.03** | 06 |
| **3Q26 sales & marketing** | $790.2M, +35.0% y/y | **$781.1M, +33.5% y/y** | 03 — the add-back schedule is D&A only, so $11.9M less residual to allocate |
| 3Q26 product development / G&A | $382.1M / $282.8M (+14.8% / +10.0%) | **$381.0M / $281.2M (+14.4% / +9.4%)** | 03 |
| 4Q26-4Q27 pd / S&M / G&A | — | each lower by the same mechanism (e.g. 2Q27 S&M $999M → **$993M**) | 03 |
| **FY26 net income, base** | $3,145.93M | **$3,146.12M** | 15 — sum of quarters, not an annual rate re-applied |
| FY26 net income, bear / bull | −$0.300M / −$0.065M off the quarters | **exact** | 15 |
| **FY26 / FY27 / FY28 FCF mid** | 4,830 / 5,283 / 5,716 | **4,844 / 5,297 / 5,731** | 07 — CFO rebuilt from after-tax net income |
| FY FCF bias-adjusted | 4,431 / 4,884 / 5,317 | **4,445 / 4,898 / 5,332** | 07 |
| 3Q26 quarterly CFO (diagnostic) | 1,001.2 | **1,016.9** | 07 |
| **FY26 bear / bull margin** | 35.70 / 35.78 | **35.42 / 36.10** | 05 — scenarios now carry M6's cost response |
| **FY27 bear / bull margin** | 34.512 / 34.707 | **32.146 / 36.528** | 05 |
| FY27 bear / bull EPS | 5.23 / 6.14 | **4.72 / 6.58** | 05 |
| Discretionary cost % of revenue, 3Q26 / 2Q27 / 3Q27 | 30.29 / 41.27 / 32.50 | **30.04 / 41.10 / 32.21** | 03 |
| Registry `n_params` | 2 | **54** (2 wrapper + 52 inherited, split in `notes`) | 09 |
| Registry `n_train` | member count (3/4/6) | **prior quarters the weights were fitted on** | 09 |
| Registry `street_vendor` / `street_as_of` / `knowable_from` | blank on all 1,152 rows | **populated** (768 consensus-anchored rows carry LSEG + its calc date; every row carries `knowable_from ≤ vintage`) | 08 |
| Registry `notes` | `<bound method NDFrame.clip ...>` on all 1,152 rows | **the clip status**, plus `n_members`, the member list and `consensus_anchored` | 17, 09, 08 |
| `23_vs_consensus.csv` dispersion | one `lseg_sd_musd` (revenue sd on quarters, EBITDA sd on years) | **`lseg_revenue_sd_musd` + `lseg_ebitda_sd_musd`** | 14 |
| `23_bands.csv` `attainable_cov80_lo/hi` | — | renamed **`rank_grid_cov80_lo/hi`**, plus `gaussian_sd_from_qhat80` | 11 |
| `23_combination_live.csv` `ebitda_musd_{base,bear,bull}` | silently never written (quarter-code mismatch) | **populated** | incidental repair found while fixing 04 |

### What did NOT move

- **Every h=0 result.** Margin MAE 1.126 / 0.788, the ratios, the sign tests, the leave-one-out
  table, the shock/calm table, the Street-independent LIVE 49.88% — all identical. The date gate
  cannot bite at h=0.
- **The adopted points.** 3Q26 49.94% / $2,399M, 4Q26 28.90% / $918M, FY26 35.73% / $5,098M,
  FY27 34.64% / $5,483M, FY26/FY27 EPS $5.28 / $5.73, the 30.12% sentence-implied 4Q26, the
  budget-identity multipliers (4.49 and −1.51), the floor break-evens (0.63% / 0.94%), the
  macro-sensitivity table, the revenue path.
- **Every pass/fail verdict**, in both directions: h=0 passes, h=1 fails against the Street, h=2
  fails in W2, quarterly FCF stays withdrawn.

### Rejected findings

**None.** All 18 reproduced or were accepted on their reasoning. Finding 16 is accepted in part:
the workbook is now **labelled a frozen report** on its README sheet, but wiring the Inputs sheet
into the forecast cells and saving formula caches is **deferred** — openpyxl cannot evaluate
formulas (only Excel writes caches) and converting the sheet set into a linked model is a rebuild,
not an audit fix. Findings 14, 16 and 18 were the minor items with a 20-minute test: 14 and 18 were
done, 16 was split as above.

### Assertions that now guard these identities

`run.py` step 4b fails the build (exit 2) unless: the five cash lines minus the D&A add-back equal
total cash costs and revenue minus total cash costs equals adj EBITDA; the GAAP bridge uses the
same add-back; CFO equals net income + D&A + SBC + working capital and other; annual tax and net
income equal the sum of the quarters; the card's dollar band and P(beat) come from the same object;
the bear and base scenario margins differ; and the EPS band is wider than the EBITDA-only band.

---

## RESUME

**WS31 (14 Sep) applied the Codex/Astra audit in full; §11 above lists every number that moved and
every identity now asserted in `run.py`. Nothing on the audit list is outstanding except the
deferred half of finding 16 (make the workbook input-driven and save formula caches).**

Everything WS23 was asked for is on disk and rebuilds with
`py -3.13 analysis/src/margin_build/23_final_model/run.py` (exit 0, ~4 min; it calls `score.py`
once at the end, so no other method package may be running; `MARGIN_VERIFY_ONLY=1` recomputes and
compares without writing). The next agent should do three
things, in this order. **First**, write the WS22 group C `revenue_leg_live.csv` patch into the
harness so every package's LIVE dollar rows sit on bridge v3 rather than the naive leg — WS23 did
it by hand for the final model only, and the 4Q26 wedge is $59M of revenue and $20-25M of EBITDA
on every other LIVE table. **Second**, reconcile or retire WS31b's 4Q26 margin profile (24.7-25.9%),
which contradicts this build, the Street and management, and is still the incumbent margin model in
the repo. **Third**, build a genuine h=1 object for 4Q26: the combination loses to the raw Street by
20-28% at h=1 in both windows, the trade into 5 Nov is structurally an h=1 position, and the
budget identity says 4Q26 is where the FY guide sentence actually lands (4.49pp of 4Q26 per 1pp of
FY26). If time allows after those, two smaller items: replace the mechanical residual allocation in
the line stack with one that respects the 1H26 G&A trend (−5.4% y/y, against our +10.0%), and check
why FY26 EPS is $0.03 below Street on an EBITDA $44M above it — the answer is SBC and the share
count, and the 5 Nov 10-Q settles it either way.
