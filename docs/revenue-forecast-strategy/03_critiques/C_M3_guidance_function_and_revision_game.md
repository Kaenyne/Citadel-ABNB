# C-M3 — Adversarial review of "GAC: the guidance function and the revision game"

Reviewer: adversarial lens (IC seat + econometrics). Date 11 Sep 2026.
Target: `docs/revenue-forecast-strategy/02_proposals/M3_guidance_function_and_revision_game.md`.
Everything below was recomputed in-session from the cited CSVs. Where I reproduce the author's number I say so;
where I do not, I give mine and the code path.

**Verdict: ADOPT WITH FIXES.** The λ_s kernel and the guide-vs-print separation are the best single idea
produced by any lens so far and they survive attack. The *revision game* — the part the proposal names
itself after and sells hardest — is an accounting identity, and Layer 3 is a time-period artefact.
Both must be demoted before this goes in front of a judge.

---

## 0. Scores

| axis | score | one-line |
|---|---|---|
| Identification | **4 / 10** | λ_s and κ reproduce exactly; the load-bearing cushion does not, and the revision slope is algebra |
| PIT safety / backtest validity | **6 / 10** | the discipline is genuine and best-in-repo, but the walk-forward is truncated and κ is measured below the data's rounding quantum |
| Statistical power / overfitting | **3 / 10** | all 8 below-Street events sit inside one 2.5-year window in which *every* print drifted down |
| Tradeability 3–12m | **5 / 10** | the direction is actionable and the FX-vs-Street mechanism is real; the drift rule is not the edge and the finals pre-date the catalyst |
| Buildability in 3 weeks | **7 / 10** | every file is on disk, the core reproduces in ~40 lines of pandas; PyMC is decoration and the skeleton has a data-fabricating bug |
| Defensibility in hostile Q&A | **4 / 10** | the flagship exhibit is the one a Citadel quant kills in 30 seconds |

---

## 1. Identification — 4/10

**What reproduces exactly.** I rebuilt λ_s from `02_kpi_panel_quarterly.csv` with w=(2/3,1/3):
Q3 17.391 / 17.145 / 17.182 %, Q4 11.946 / 12.117 / 12.026 %, and every cell of the §2.1 table to 2dp.
`data/processed/h2_bridge/h2_bridge_gbv_lag_conversion.csv` carries the same six numbers.
κ from `16_consensus_at_print_merged.csv` = mean +0.565 %, last-8 +0.516 %, sd 0.282 % — matches §2.3.
The n=10 walk-forward table in §4 reproduces to the third decimal. **The author did the arithmetic. That is not the problem.**

### 1.1 FATAL: the revision regression is an accounting identity, not a finding

The proposal's headline — "revision% = 0.593 + 0.988 × gap%, r = 0.993, **the slope is one**, the Street
adjusts *completely*" (§2.3, §5.4, §8, `novelty_vs_street`) — is definitionally true.

With `S_pre` = `next_q_cons_revenue_musd` at date t, `g` = `next_q_guide_mid_musd` at t, `S_post` = `cons_revenue_musd` at t+1:

```
gap      = g/S_pre − 1
κ        = S_post/g − 1
revision = S_post/S_pre − 1
⇒  (1 + revision)  ≡  (1 + κ)(1 + gap)     exactly, by construction
```

I verified this on all 18 rows: **max |residual| = 4.6 × 10⁻⁶**. Since sd(gap) = 4.54 % and sd(κ) = 0.54 %,
a slope of 1.00 and r of 0.99 are arithmetically guaranteed. Four of the 18 "revisions" are *exactly zero*
because the vendor printed the identical rounded number twice (2023Q1 2420→2420; 2024Q1 2740→2740;
2024Q3 2420→2420; 2025Q1 3040→3040).

This breaks the proposal on its own terms. §2.5 says "only two independent spreads exist… each parameter
is defined as exactly one of them." The revision slope is the *third* presentation of the *second* spread.
By the proposal's own anti-double-count rule it should never have been counted as separate evidence, and
`novelty_vs_street` lists it as one of "three quantities measured here for the first time." It is one
quantity, κ, shown twice. **Delete the revision regression or relabel it as the identity check it is.**

### 1.2 FATAL: the −2.33 % cushion is the hidden plug

Everything in §5.2 turns on one number: `guide = kernel × (1 − 2.33 %)`. That number appears in §1.3,
§5.2, §5.4 and is hard-coded in the §6 skeleton (`- 0.0233`). It is **never tabulated and does not
reproduce from any stated sample.** I computed log(g/M) with the author's own PIT λ̂ on all 14 quarters
where both exist:

| window | mean g/M − 1 | sd |
|---|---|---|
| all 14 | **−3.04 %** | 2.32 pp |
| last 8 | **−1.93 %** | **1.86 pp** |
| author's claim | −2.33 % | 1.84 pp |

The *sd* matches last-8 almost exactly (1.86 vs 1.84); the *mean* does not (−1.93 vs −2.33). Whatever
window produced the sd did not produce the mean. The 0.40 pp difference is 40 % of the entire headline gap:

| cushion used | 4Q26 guide | gap vs Street $3,200m |
|---|---|---|
| −2.33 % (proposal) | $3,118m | **−2.57 %** |
| −1.93 % (g/M last-8, recomputed) | $3,131m | **−2.17 %** |
| −1.86 % (= −[A/g − 1] last-8, the *tabulated* cushion) | $3,133m | **−2.10 %** |
| −3.04 % (g/M full history) | $3,095m | −3.28 % |

There is a second, deeper problem. The proposal uses the word "cushion" for two different objects and
switches between them without flagging it: §2.3 tabulates `A/g − 1` (+2.31 % all, +1.86 % last-8), which
is *directly observed and needs no kernel*; §2.2 eq. (3) defines `c = log M − log g`, which is
kernel-dependent. **`c` is a residual that absorbs every kernel misspecification.** My walk-forward shows the
kernel over-predicts revenue by a mean +0.99 pp (n=14, below), so ~1 pp of the "management shading" the
model attributes to policy is the author's own λ̂ bias. λ and c are not separately identified in the
forecast — only the product λ̂·e^c is. The proposal advertises λ_Q4's 0.17 pp three-year range as evidence
of tightness; the object that actually drives the trade, g/M, has an sd of 1.86 pp, eleven times wider.

**Concrete double-count case, as requested.** Take 3Q24→4Q24. Realised λ_Q4 came in at 12.117 %, above the
12.02 % PIT estimate, and the guide/kernel ratio that quarter was −0.78 %. In 4Q24→1Q25 λ_Q1 came in at
12.33 %, *below* the 13.03 % PIT estimate, and g/M was −5.52 %. The cushion series is therefore
co-moving one-for-one with λ error: `Corr` is mechanical because `g/M = g/(λ̂·lag)` and λ̂ is the *only*
free scale in M. Fit `c` on history, apply it forward with a *different* λ̂, and you have applied
the historical λ error twice — once inside c̄ and once inside the forward λ̂. That is the same class of
error as the `τ_{t−4} × (1+w_t)` plug the proposal is built to replace (02_model_audit §3.1). It is not
fixed by the log-additive chain; it is created by it.

### 1.3 FATAL: "n=19 becomes n=159" is false, and the code fabricates 61 observations

`02_guidance_ledger.csv` has 194 statements. The skeleton's own query returns **155**, not 159. Of those,
only **94 carry a non-null `cushion` value**. The `directional` (48), `point` (26) and `qualitative` (10)
families have *no* cushion by construction — a directional guide has no number to shade.

The §6 skeleton then writes:

```python
y = led.cushion.astype(float).fillna(0.0).values / 100.0
```

**This inserts 61 synthetic zero-cushion observations — 39 % of the pooled sample — and feeds them to the
hyper-mean likelihood.** It will drag μ_c toward zero and collapse τ. This is not a typo to be fixed in
review; it is the line that produces the number the whole Layer-1 pool rests on.

Worse, the surviving 94 are in **incommensurable units**. From the ledger:

| metric | n | mean cushion | unit |
|---|---|---|---|
| `revenue_usd_m` | 19 | 24.9 | **$m** |
| `revenue_yoy_pct` | 16 | 1.25 | pp |
| `adj_ebitda_margin_yoy_pts` | 18 | 3.13 | pts |
| `sm_growth_minus_rev_growth_pts` | 2 | 12.81 | pts |
| `take_rate_yoy_pts` | 9 | 0.20 | pts |

`pm.Normal(c_f[fam], …, observed=y)` pools $72m against 0.63 pts against 17.68 pts. The prose says
"standardised (per-family sd) scale" — but standardising *by each family's own sd* makes the pooled
hyper-mean unitless, and converting it back to a revenue cushion **in per cent requires the
revenue-range family's own sd, which has exactly 19 observations**. The pooling therefore contributes
zero information to the quantity the trade needs. 02_model_audit §4.2(d) already ruled: "with 23 prints
total and 19 guided quarters, no quarterly-frequency single-feature regression will ever clear a
trailing-mean baseline… re-openable only by changing the unit of observation." M3 does not change the
unit of observation for the cushion; it asserts it has.

Add that the two families that misbehave (expense/tax `point`, take-rate) are *dropped post hoc* after
their behaviour was inspected. Selecting 5 of 7 exchangeable groups on observed fit is a selection
decision on n=7, made with the answers visible.

### 1.4 What the overlap fix actually achieves

Credit where due: removing nights × ADR, the take-rate carry and the four-fold FX appearance is real and
correct. GBV as the state genuinely forecloses the geographic-mix / size-mix / LOS / regulatory-drag
double counts catalogued in 02_model_audit §3.4–3.8, **by construction, not in words.** That part survives.
But the fix relocates the overlap rather than eliminating it: everything the old model double-counted is
now inside a single unobserved scalar λ_s, and λ_s is confounded with c (§1.2 above) and with
booking→check-in FX (§2.4 below). One plug replaced four — an improvement, not a solution.

---

## 2. Point-in-time safety and backtest validity — 6/10

The PIT protocol in §4 is the most disciplined in the repo: strictly-prior consensus vintages, guide
statements with `print_date ≤ t`, `driver_realised_share` recomputed at t, and explicit awareness of the
LSEG-$4,610m-vs-Zacks-$4,740m trap that killed the peer read-across. Three real problems remain.

### 2.1 The walk-forward is truncated, and the stated reason is wrong

§4: "λ̂ from the two prior same quarters only (so 1Q24 is the first scoreable quarter)." **False.** 1Q23 has
two prior Q1 λ's available (1Q21 13.406 %, 1Q22 13.122 %) and is scoreable under the author's own rule, as
are 2Q23, 3Q23 and 4Q23. Running the rule as written:

| sample | n | mean err | MAE | RMSE |
|---|---|---|---|---|
| author's (1Q24–2Q26) | 10 | +0.30 % | **1.36 %** | 2.00 % |
| rule as stated (1Q23–2Q26) | 14 | **+0.99 %** | **1.74 %** | 2.44 % |

The four dropped quarters are the four worst (+3.60, +5.36, +0.59, +1.26). Dropping the first year of a
walk-forward improves MAE by 28 % and halves the apparent bias. There may be a *defensible* reason
(COVID-era λ's in the training set) but it is not the reason given, and the number quoted to the judge is
the truncated one.

### 2.2 κ is quoted to a precision finer than the data's rounding quantum

95 % of the consensus values in `16_consensus_at_print_merged.csv` are round to 3 significant figures
(2420, 3040, 4610, 4730). At a $3,000m level that is a ±0.167 % quantisation — uniform-rounding sd ≈ 0.10 pp.
The proposal quotes **"κ se = 0.10 %"** and **"forecast the guide and you have forecast consensus to ±30bp."**
The measurement error alone is the same size as the claimed standard error. Four of the 18 κ observations
are *forced* by the vendor printing the same rounded number twice.

Second: the series is **vendor-spliced** — CNBC-unattributed → StreetAccount → Refinitiv → LSEG. The three
largest |κ| deviations in the sample (2022Q1 +1.44 %, 2022Q2 −1.06 %, 2021Q4 +0.35 %) are *exactly* the three
cross-vendor pairs. On LSEG-only pairs κ is genuinely tight — which is good for the point estimate but
means the honest n is ~13, not 18, and the "n=18" in the memo is inflated by observations the author
should discard on his own logic.

### 2.3 The "frozen card" cross-check is not what it is cited as

§5.1 presents "frozen pre-registered card (`20_frozen_q3_2026.csv`) → $4,805m" as one of "three independent
constructions inside 0.25 %." I opened the file: it is a model × target registry for *surprise* targets,
columns `forecast / bl_guide / bl_guide_plus_cushion / consensus_vintage`. **It contains no revenue level and
no GBV of 26.19.** The $4,805m is `4,740 × (1 + 1.374 %)`, i.e. the **BASELINE trailing4_mean** surprise
applied to the Zacks 4-Sep vintage — and that file's own `consensus_vintage` note says the Zacks $4,740m
"is a LATER vintage and is not the feature." So the three "independent" constructions are: (i) the kernel,
(ii) guide × historical beat, (iii) consensus × historical beat. (ii) and (iii) are the same construction
on two anchors 0.2 % apart. **It is two constructions, and the third leans on a vintage the repo has
explicitly quarantined.** Fix the citation before a judge opens the CSV.

### 2.4 One un-tested PIT-adjacent assumption

The kernel sets K = 2 with lags k ∈ {1,2} and *no* k = 0 term. The cited source (`airbnb_earnings_call_study.md`
§8.4) says only "about two-thirds of the weight on the prior quarter's GBV and one-third on the quarter
before"; it does not state that a lag-0 term was tested and rejected. If w₀ > 0, then G_q — unobserved at
the guide date — enters the forecast quarter, and the whole "management can already see it" premise weakens.
`03_insider_mechanics` §1.4 labels the 120-market booking curve "**unusable** for y/y — single vintage," so
this cannot be settled from alt data; it must be settled by refitting the lag polynomial with k=0 included
and showing w₀ shrinks to zero. Until then K=2 is an assumption dressed as identification.

### 2.5 The "85–90 % already on the ledger" premise is the wrong season's number

§1.3 and the whole "why it is forecastable" argument rest on "~85–90 % of a quarter's revenue is already on
the booking ledger when the guide is set," cited to 03_insider_mechanics §1.4. That table says:
unearned-fee coverage of next-quarter revenue is **Q1-end 0.880, Q2-end 0.697, Q3-end 0.661, Q4-end 0.676**.
`abnb_backlog_indicators.csv` confirms Q3-end at 0.661 / 0.668 / 0.655 for 2023/24/25, and the RNPL era has
pushed the comparable metric to 0.599. **The guide that this entire pitch depends on — 4Q26, set at the Q3
print — is the one with the *lowest* coverage in the year, ~65 %, not 85–90 %.** The proposal quoted the
Q1-end figure. This is the single most consequential mis-citation in the document because it is the premise
sentence of §1.3.

---

## 3. Statistical power and overfitting — 3/10

### 3.1 FATAL: Layer 3's 8/8 is a calendar artefact

I pulled the below-Street set from `16_consensus_at_print_merged.csv` × `20_executable_returns.csv`:

> 2022Q3, 2023Q1, 2023Q3, 2024Q1, 2024Q2, 2024Q3, 2024Q4, 2025Q1 — mean `open_20d_pct` −3.96 %, 8/8 negative.

Reproduces the author's table. Now look at *when* they are. **Every one of the 8 falls inside 2022Q3–2025Q1.**
In that window, taking *all* prints regardless of gap sign:

| window | n | 20d mean | share negative |
|---|---|---|---|
| 2022Q3–2025Q1, **all** prints | 11 | **−3.51 %** | **10 / 11 = 90.9 %** |
| 2022Q3–2025Q1, below-Street | 8 | −3.96 % | 8 / 8 |
| 2022Q3–2025Q1, above-Street | 3 | −2.33 % | 2 / 3 |
| 2025Q2–2026Q2, all prints (all above-Street) | 5 | **+1.90 %** | 2 / 5 |

The conditional (8/8, −3.96 %) is indistinguishable from the *contemporaneous* unconditional (10/11, −3.51 %).
Fisher exact on the in-window 2×2 gives **p = 0.27**. A binomial 8/8 against the in-window base rate of
0.909 gives **p = 0.47**. The proposal's own concession — "the correct null is not a coin flip, it is ABNB's
69.6 % negative base rate, p = 0.038" — does not go far enough: the 69.6 % is itself a blend of a
90.9 %-negative de-rating regime and a 40 %-negative re-rating regime, and the below-Street indicator
selects the first regime almost perfectly. **The signal is a time dummy for 2022H2–2025Q1.** The
"9/9 negative, p = 0.0382" line in 02_model_audit §4.3 inherits the same defect and should be re-flagged there.

This also explains the proposal's own puzzle: "above-Street guides are 6/11 negative, indistinguishable from
the base rate." Of course they are — 8 of the 11 above-Street prints sit in the other regime.

The 8 events are also serially dependent: 2024Q1–2025Q1 is a run of *five consecutive* below-Street guides.
A block bootstrap at the regime level leaves ~2 independent episodes.

### 3.2 The uncertainty representation is not honest

§5.2 gives P(gap<0) = 0.87 with an 80 % interval of [−4.4 %, −0.5 %], which back-solves to a predictive
sd of **1.52 pp**. But the cushion alone has sd 1.86 pp (recomputed, §1.2), before adding kernel error
(RMSE 2.44 pp on the honest sample), GBV(3Q26) uncertainty (the author's own sweep moves the gap 2.2 pp
across a plausible GBV range), and estimation error in c̄ (se = 1.86/√8 = 0.66 pp). Compounding
conservatively:

```
sd_total = sqrt(1.86² + 1.74² + 1.2² + 0.66²) = 2.89 pp
gap mean (on the recomputed −1.93 % cushion) = −2.18 pp
P(gap < 0) = 0.775
```

**P ≈ 0.75–0.80, not 0.87.** The 80 % interval is roughly [−5.9 %, +1.5 %] and *includes zero*. That is still
a tradeable asymmetry, but it is a different sentence and the memo must say the honest one.

### 3.3 Free-parameter count vs observations

Declared: "~25 parameters against 159 pooled observations plus 22 quarterly kernel observations." Honest
count: λ_s (4, on 22 quarters ⇒ 5.5 obs each), w (1 free, K=2), c̄_range + ρ + σ_c + γ (4 covariates) = 7
parameters on **19** revenue quarters, κ (1) + σ_κ on **13** clean-vendor pairs, b on **n = 1**, p₋ on 8
non-independent events. The pooled 159 (really 94, really 61-fabricated) does not touch the 7 parameters
that matter. **The binding sample for the trade is 19, and the binding sample for the price claim is ~2
independent regimes.**

### 3.4 Does it repeat a failed design?

Partly no, partly yes. It genuinely avoids causes (a), (c) and (e) from 02_model_audit §4.2 — no Trends, no
macro demand proxies, no Inside Airbnb, no ADR_EXFX leak. Cause (b) — wrong target — is genuinely inverted:
forecasting the guide midpoint is a target with 4.5 pp of cross-sectional range, not 1.3 pp. That is the
proposal's strongest methodological claim and it survives. **Cause (d) is not escaped.** The cushion model
is a 4-regressor quarterly OLS on 19 observations dressed in a hierarchical prior whose pool contributes
nothing in the units required. The audit's own ruling applies verbatim.

### 3.5 The head-to-head the proposal did not run

§4 nominates the right baseline — "the Street's own next-quarter number as a guide proxy" — and then never
scores it. I did, with a strictly expanding PIT cushion (trailing-8 of prior g/M, ≥4 obs required):

| predictor of the **guide midpoint** | n | MAE | RMSE | bias |
|---|---|---|---|---|
| kernel + PIT cushion | 10 | **1.93 %** | 2.24 % | **−1.23 %** |
| pre-guide Street consensus (free, zero model) | 10 | **1.61 %** | 2.04 % | −0.01 % |

Robustness across cushion windows (trailing-3 / 4 / 8 / all, minimum-obs 3–6): the kernel MAE runs
1.62–2.12 % against the Street's 1.59–1.75 %, and the kernel's bias is **negative in every specification**
(−0.47 to −1.59 %). **On the level of the guide, the model loses to a number you can read off Bloomberg
for free, and its errors are one-sided in exactly the direction that generates the short.** That is the
most damaging single fact in this review and it must be resolved, not argued around.

One thing does survive: **sign of (ĝ − S) matches sign of (g − S) in 8 of 10** (7/8 to 8/11 across
specifications) against a ~50/50 in-sample split — binomial p ≈ 0.055 at n = 10. Marginal, but it is the
only place where the model beats the free baseline, and it is the only output the trade actually needs.

---

## 4. Tradeability over 3–12 months — 5/10

**What works.** The mechanism is stated crisply and is checkable: the Street has 4Q26 at $3,200m = **+15.2 %
y/y** on a 4Q25 base of $2,778m, essentially flat against the Q3 guided +15–17 %, while
`05_fx_schedule.csv` puts `revenue_fx_fit_pp` at **+2.19 for 3Q26 and −0.43 for 4Q26** (−3.4 pp against the
guided +3.0). **The Street has not taken Q4 down for the FX step.** That is a real, dated, falsifiable
disagreement with a mechanism, and it is the best sell-side-is-wrong argument in the repo. It survives.

**What does not.**

1. **The finals are 22–24 Oct 2026; the catalyst is 5 Nov.** The judged pitch must be *pre-positioned*. The
   drift rule in Layer 3 is a *post-event* rule — next-open entry after the gap is public — so it adds
   nothing to a pitch. Pre-positioning means eating the overnight gap, whose sd on `20_executable_returns.csv`
   is **8.7 pp** on below-Street events and **7.2 pp** unconditionally, against an admitted inability to
   forecast day-1 (17 regressions, all negative LOO R²). The proposal never states this. Run the honest EV
   at P(below) = 0.80: below branch −4.58 (gap) − 3.96 (20d) = −8.54 %; above branch +5.72 (gap) − 1.53 (20d)
   = +4.19 %; **EV ≈ −6.0 % over ~21 trading days.** That is a good trade — but it is carried entirely by the
   *gap forecast*, not by the drift conditioning, and the memo currently sells the reverse.
2. **The "Street bar" is a point estimate on a very wide distribution.** `04_current_consensus.csv` Q4 2026:
   Zacks $3,200m, **10 estimates, low $3,050m, high $3,700m** (the $3.70bn is almost certainly a data error
   and should be flagged). The model's $3,118–3,133m sits *above the Street low* and inside the range.
   "We are 2.5 % below the Street" is a statement about a mean with a 20 % spread. A judge will ask for the
   dispersion; the proposal has not looked at it.
3. **The 4Q26 gap-sign call is a regime flip that the model does not model.** The last four prints have all
   been guide-*above*-Street: +0.749, +3.162, +3.179, +2.603. M3 forecasts a sign flip on the fifth. The
   stated mechanism (FX) is credible, but there is no evidence in the specification that c_q responds to
   `fxobs` — γ is given an N(0, 0.01²) prior and never estimated in-session. The one covariate that must
   fire to produce the call is the one with zero reported evidence.
4. **The multiple bridge is circular at the margin.** "2.0 pp of forward growth × 0.48 turns = −5.8 % of EV,
   plus −1.9 % earnings, ≈ −7 to −8 %, against a measured 20-day drift of −4.0 %." The 0.48 turns/pt is
   itself a cross-sectional regression from `docs/2026-09-07_research-state-of-play.md` — the "two
   independent routes" both start from the same forward-growth delta. It is a consistency check, which the
   author says, but calling it "two independent routes" oversells it.

**Where it beats the alternative.** M3 is the only lens that produces a *dated, falsifiable, pre-registrable*
claim about a number management has not said yet, on a 5 Nov catalyst inside the horizon. Everything else
in the repo produces a better revenue number, which the judges cannot score.

---

## 5. Buildability in three weeks — 7/10

**All 21 cited repo paths exist** (verified with `ls`/`wc`). Row counts match the §3 data map within one
(ledger 194 statements + header = 195 ✓; cushion 19 + header ✓; consensus merged 23 + header ✓;
`10_fx_daily.csv` 19,467 rows + header ✓; `02_metric_coverage.csv`, `06_fee_timeline.csv`,
`29_fy27_bridge.csv` (base 4Q26 = $3,111m ✓), `20_prediction_ledger.csv` all present).
I reproduced λ_s, κ, the cushion series, the walk-forward and the drift panel **in about 40 lines of pandas
and under two minutes of compute.** Day-1's acceptance test will pass. Compute is a non-issue.

**Three build risks.**

1. **The §6 skeleton is not runnable as printed** and one of its lines fabricates data (`fillna(0.0)`, §1.3).
   Also: `led.cushion` is mixed-unit; `anchor = s.cons_revenue_musd.shift(-1)/s.next_q_guide_mid_musd - 1`
   silently includes the cross-vendor pairs; `mu_q` is built but `rho` is declared and never used; the
   forward block multiplies by `exp(gamma.mean()*0 - 0.0233)`, i.e. the posterior is discarded and the
   hard-coded cushion used. **Four undergraduates will copy this and inherit all four.**
2. **PyMC is decoration.** A 25-parameter NUTS model on 19 usable revenue quarters buys nothing over a
   trailing-8 mean with a bootstrap interval, and it buys a week of debugging plus divergences that
   nobody on the team will be able to diagnose under a hostile question. The proposal's own cut list ranks
   the Bayesian machinery as un-cuttable; it is the *most* cuttable thing here.
3. **Fiscal.ai is on the critical path for b, and b is n=1.** The proposal is honest about this. The
   fallback (press-quote reconstruction, ~2 analyst-days) collides with Day 1–5. Budget it or drop FY+1.

**Minimum viable version that keeps the edge (2–3 days, one person, pure pandas):**
λ_s from `02_kpi_panel_quarterly.csv` → PIT walk-forward on the *full* 14 quarters → trailing-8 g/M cushion
with a bootstrap interval → 4Q26 guide point + honest interval → gap vs $3,200m with its dispersion →
gap-sign call with the 8/10 hit rate and its p-value → the guide-vs-print reconciliation paragraph.
**That is the whole pitch.** Everything else — PyMC, conformal, the hierarchical pool, the FY+1 regression,
the revision regression — is removable without touching the edge, and removing the revision regression
*improves* the pitch.

---

## 6. Defensibility in a 2-page memo and 10-minute hostile Q&A — 4/10

**The one-sentence version (author's, §9), edited for what survives:**
> *Airbnb's Q4 revenue guide is set off a booking ledger we can reconstruct to ~1.7 % 90 days early, and
> management shades it ~2 % below their own point estimate; the Street's $3,200m carries no shading and
> no FX step, so on 5 Nov the range prints ~2 % light, and the Street's FY27 is an extrapolation of a
> quarter it has not seen.*

**The number the judge attacks first.** Not the kernel. A Citadel quant will go straight to the exhibit the
proposal is proudest of — *"revision% = 0.593 + 0.988 × gap%, r = 0.993"* — and say: **"That's an identity.
Your revision is (1+κ)(1+gap)−1 and your κ has sd 54 bp. You've regressed X on X and reported r-squared."**
The proposal has **no answer** to this; §8's prepared rebuttal ("it is a tautology only if you already knew
κ = +0.52 %") concedes the point without recognising it. That is a 30-second kill on the memo's centrepiece,
and it will contaminate everything else in the room.

**The second attack**, if the first is survived: *"Your eight below-Street events are all in 2022–2025, when
every ABNB print drifted down 10 times out of 11. Show me one below-Street guide in a good tape."* There
isn't one. The honest answer is "the conditioning adds nothing; the edge is the gap forecast," and the memo
must be rewritten to say that *first*.

**Third:** *"Your model loses to the Street's own next-quarter number at predicting the guide, and its errors
are biased low."* Answer available and honest: the level contest is a draw; the *sign* is 8/10; and the
bias is why we show the gap distribution rather than a point. But it must be pre-computed and in the appendix.

**What is defensible and should be the memo's spine:** the λ_s kernel (reproducible in one line, 0.17 pp
three-year range on Q4), the guide-vs-print separation ($3,120m guide vs ~$3,190m print — the cleanest
original thought in the repo), and the FX-step-vs-Street arithmetic with dated sources. The §4 "what I
refuse to claim" appendix is excellent practice and should be kept verbatim, extended to cover §3.1 above.

---

## 7. Refutation attempts

| # | Claim under attack | Attack | Outcome |
|---|---|---|---|
| 1 | "Revision slope 0.988, r 0.993 — the Street adjusts completely; measured for the first time" | (1+rev) ≡ (1+κ)(1+gap) by construction; verified on all 18 rows, max residual 4.6e-6; sd(gap)/sd(κ) = 8.4 makes slope 1 and r 0.99 mechanical; 4 of 18 revisions are exactly 0 from vendor rounding | **REFUTED** |
| 2 | "Guide below Street → 20-day drift, 8/8, p 0.038 vs the 69.6 % base rate" | all 8 events sit in 2022Q3–2025Q1, a window in which 10 of 11 prints were negative at 20d (mean −3.51 %); Fisher exact in-window p = 0.27; binomial vs in-window base rate p = 0.47; 2024Q1–2025Q1 is 5 consecutive events | **REFUTED** |
| 3 | "Hierarchical pooling turns n=19 into n=159 for the cushion" | the query returns 155, only 94 carry a cushion; 61 are `fillna(0.0)` fabrications in the skeleton; surviving values are $m / pp / pts pooled in one Normal; per-family standardisation makes the hyper-mean unconvertible to a revenue cushion in % | **REFUTED** |
| 4 | "Kernel PIT walk-forward MAE 1.36 %, n=10; the first scoreable quarter is 1Q24" | 1Q23–4Q23 are scoreable under the author's own two-prior-same-quarters rule; full sample n=14 gives MAE 1.74 %, RMSE 2.44 %, bias +0.99 % | **REFUTED** (arithmetic is right; the sample is truncated and the stated reason is false) |
| 5 | "Cushion −2.33 % ± 1.84 %" | not reproducible from any stated sample; recomputed g/M last-8 = −1.93 % (sd 1.86), full = −3.04 % (sd 2.32), tabulated A/g last-8 = +1.86 %; the 0.40 pp gap is 40 % of the headline call; c is also a residual that absorbs λ̂ bias, so λ and c are not separately identified | **REFUTED** |
| 6 | "P(gap<0) = 0.87, 80 % interval [−4.4 %, −0.5 %]" | implied sd 1.52 pp vs a cushion sd of 1.86 pp alone; compounding cushion + kernel + GBV + estimation error gives sd 2.89 pp and P ≈ 0.775, interval including zero | **PARTIALLY** (direction survives, confidence does not) |
| 7 | "The model forecasts the guide midpoint — a target nobody has scored" | true, and it is the right target (inverts audit cause (b)); but head-to-head PIT it loses on level to the free pre-guide Street number (MAE 1.93 vs 1.61; bias −1.23 vs −0.01; loses in all 5 cushion-window specifications) | **PARTIALLY** (target choice survives; level superiority refuted) |
| 8 | "Sign of gap is the tradeable output" | 8/10 correct against a 5/5 in-sample split, binomial p ≈ 0.055; robust 7/8 to 8/11 across cushion windows; this is the only place the model beats the free baseline | **SURVIVED** |
| 9 | "Nights × ADR / take rate / regulatory drag cannot double count because GBV is the state" | tried to construct a path back in: none exists so long as M1 hands over G only; the fix is structural, not verbal, and forecloses 02_model_audit §3.4–3.8 | **SURVIVED** (conditional on the §9 interface being enforced in `model/assumptions.md`) |
| 10 | "The Street's $3,200m Q4 carries no FX step" | checked: $3,200m = +15.2 % y/y on $2,778m, flat vs the Q3 guided +15–17 %, while `05_fx_schedule.csv` steps revenue FX from +2.19 to −0.43 pp; the Street has not taken it down | **SURVIVED** — this is the real edge |
| 11 | "~85–90 % of a quarter's revenue is on the booking ledger at the guide date" | 03_insider_mechanics §1.4 and `abnb_backlog_indicators.csv` give unearned-fee coverage of 0.661 / 0.668 / 0.655 at Q3-end — the exact vintage for the 4Q26 guide; 0.88 is the Q1-end figure; RNPL era ~0.599 | **REFUTED** (wrong season quoted for the one guide that matters) |
| 12 | "Three independent constructions of 3Q26 inside 0.25 %" | `20_frozen_q3_2026.csv` contains no revenue level; $4,805 = 4,740 × (1 + 1.374 % trailing-4 baseline) on a Zacks vintage the same file quarantines; constructions (ii) and (iii) are both "anchor × historical beat" | **REFUTED** |
| 13 | "λ_s independently confirmed by `h2_bridge_gbv_lag_conversion.csv`" | that file holds the identical six ratios from the identical two KPI-panel columns — a copy, not an independent estimator | **REFUTED** (harmless, but delete the word "independent") |

---

## 8. Fatal flaws

**F1.** The revision regression (slope 0.988, r 0.993) is an algebraic identity — the same object as κ,
counted twice — and it is the proposal's advertised centrepiece. It violates the proposal's own §2.5
no-double-count rule.

**F2.** Layer 3's 8/8 below-Street drift is a 2022Q3–2025Q1 calendar artefact. Against the contemporaneous
base rate (10/11 negative) the conditional edge is p = 0.27–0.47, i.e. none. The repo-level claim in
02_model_audit §4.3 inherits this and must be re-flagged.

**F3.** The −2.33 % cushion — the single number that generates the entire −2.5 % gap and hence the trade —
is not reproducible from any sample stated in the document, and the cushion is structurally confounded with
λ̂ bias so that λ and c are only jointly identified.

**F4.** "n=19 becomes n=159" is false. 94 statements carry a cushion; the §6 skeleton manufactures 61 zeros
via `fillna(0.0)`; the survivors are in incommensurable units; per-family standardisation makes the pool
uninformative about the revenue cushion in per cent.

**F5.** Head-to-head PIT, the kernel + cushion **loses to the free pre-guide Street consensus** at predicting
the guide midpoint (MAE 1.93 % vs 1.61 %) in every cushion-window specification, with a one-sided negative
bias of −0.47 to −1.59 pp that mechanically manufactures the short.

---

## 9. Must-fix (in priority order)

1. **Delete the revision regression from the memo**, or relabel it explicitly as the identity
   `(1+rev) ≡ (1+κ)(1+gap)` and use it only as a sanity check. Remove "revision slope" from the
   novelty list. Keep κ as the single Layer-2 parameter.
2. **Re-frame Layer 3.** Report the below-Street drift against the *contemporaneous* window base rate
   (10/11, −3.51 %), state Fisher p = 0.27, and demote it from "the trade" to "a consistency check."
   State plainly: **the edge is the gap forecast; the drift rule adds nothing a judge should pay for.**
3. **Publish the cushion table.** Show g/M for every quarter, name the window, and reconcile it to the
   tabulated A/g cushion. If the answer is −1.93 %, the gap is −2.17 % and the memo says −2.17 %.
4. **Rerun the walk-forward from 1Q23** and quote MAE 1.74 % / RMSE 2.44 % / bias +0.99 %. If COVID λ's are
   to be excluded, say so as a stated exclusion with the number both ways.
5. **Run and publish the head-to-head against the pre-guide Street consensus** (my table in §3.5). Lead the
   memo with the *sign* result (8/10, p ≈ 0.055), not the level result. If you cannot beat the free baseline
   on level, do not claim a level edge.
6. **Kill the `fillna(0.0)` line.** Either standardise properly and show what the pool changes (it will be
   ~nothing), or drop the hierarchical layer entirely and use a trailing-8 mean with a bootstrap CI.
   Recommend the latter.
7. **Fix the "85–90 %" premise** to the Q3-end coverage of ~0.66 (0.60 in the RNPL era), and adjust the
   "why it is forecastable" paragraph accordingly. This is the memo's first substantive sentence.
8. **Fix the `20_frozen_q3_2026.csv` citation.** Say "guide × trailing-4 beat on the Zacks 4-Sep vintage,"
   and note that the file's own vintage rule excludes that anchor as a feature. Say "two constructions," not three.
9. **Re-price the uncertainty:** predictive sd ≈ 2.9 pp, P(gap<0) ≈ 0.78, 80 % interval ≈ [−5.9 %, +1.5 %].
   Then state the pre-positioned EV honestly (−6 % over 21 days at P = 0.80) including the 8.7 pp-sd
   overnight gap you must eat because the finals are 22–24 Oct and the catalyst is 5 Nov.
10. **Add the Q4 consensus dispersion** ($3,050–3,700m, 10 estimates) to the "Street is wrong" exhibit, and
    flag the $3.70bn high as probable bad data.
11. **Test w₀.** Refit the lag polynomial with a k=0 term and show it shrinks to zero, or carry the
    contemporaneous-booking share as a stated assumption.
12. **Restrict κ to the LSEG-only pairs** (n ≈ 13) and stop quoting a standard error (0.10 %) finer than the
    consensus rounding quantum (±0.167 %). Quote κ as "+0.5 % ± the rounding of a 3-sig-fig vendor print."
13. **Drop PyMC** unless a day-4 sampling success is already in hand. Trailing means + block bootstrap
    deliver the same intervals with an answer a judge can follow.

---

## 10. What to keep even if the whole is rejected

1. **The λ_s booking→check-in kernel.** Reproducible in one line from `02_kpi_panel_quarterly.csv`;
   Q3 17.39/17.15/17.18 %, Q4 11.95/12.12/12.03 %. It is the direct, mechanism-grounded replacement for the
   `τ_{t−4} × (1+w_t)` plug at `13_driver_model.py:381-383` with its +1.05 pp perfect-foresight bias
   (02_model_audit §3.1). Hand it to M6 whatever happens to M3.
2. **The guide-vs-print separation.** "The bridge's $3,111m is the *guide*; the *print* is ~$3,190m."
   That is the single most original sentence in the repo and it resolves the $80m internal contradiction —
   but the reconciliation must be *demonstrated*, not asserted.
3. **Forecasting the guide midpoint rather than the surprise.** The correct response to 02_model_audit
   §4.2(b). It is the right target and no one else in the repo has scored it.
4. **GBV as the single state variable**, with nights/ADR/mix/take-rate barred from re-entering revenue.
   This is a structural fix and it should be written into `model/assumptions.md` verbatim.
5. **The FX-step-vs-Street arithmetic.** $3,200m = +15.2 % y/y against a revenue-FX step from +2.19 to
   −0.43 pp (`05_fx_schedule.csv`, `driver_realised_share` 0.84). Dated, sourced, falsifiable on 5 Nov.
6. **κ itself**, as a modest, rounding-limited fact: at-print consensus ≈ guide × 1.005. Useful for setting
   the surprise denominator on 5 Nov; not a discovery.
7. **The §4 power statement and the "what we refuse to claim" appendix.** Best analytical hygiene in the repo.
8. **The PIT protocol and the LSEG-$4,610m-not-Zacks-$4,740m vintage rule.** Adopt it project-wide.
9. **The gap-sign result: 8/10 PIT.** The only place the model beats a free baseline. Lead with it.

---

## 11. How this lens should interlock with the others

M3 should be demoted from "the model" to **the terminal layer of the stack, and the pitch's clock.** Its one
input is the GBV path: M1 (structural mix) and M4 (bottom-up markets) own nights × ADR × mix and must hand
M3 a single number, `G_{3Q26}` and forward, with nothing else crossing the boundary — that boundary is the
whole double-count fix and belongs in `model/assumptions.md` as a written rule, not a convention. M2 (nowcast)
gets its job description from M3 and it is a narrow one: because ~65 % (not 85–90 %) of 4Q26 is on the ledger
at the guide date, a within-quarter GBV nowcast is worth more than M3 assumes, and M2's target should be
`G_{3Q26}` measured against the "mid teens" bucket, since a $0.9bn GBV swing moves the guide $70m and the gap
2.2 pp — GBV uncertainty, not cushion uncertainty, may be the dominant term once the cushion is honestly
sized. M6 (FX / take-rate / timing) must own `X` and must settle the λ-vs-FX-regression conflict: the kernel
implies 4Q26 y/y of +14.9 % against a Q3 guide of +15.5 %, i.e. almost no FX step, while the repo's lagged-EUR
regression implies −2.6 to −3.4 pp. **M3 and the incumbent bridge cannot both be right, and the proposal
asserts the resolution rather than demonstrating it** — one of the two must be shown wrong on the data
before either number reaches the memo. M5 (ML) should be confined to what M3 says it should: candidate `z`
covariates describing management's *situation*, never their language. And the valuation lens takes the
forward-growth delta once — through M3's FY27 consensus path — never a second time through M1's own FY27
build, which would re-import the same 2 pp at the multiple. Run that way, M3 supplies the catalyst calendar,
the pre-registered 5 Nov card, and the one sentence a PM can act on; it should not supply the revenue number.
