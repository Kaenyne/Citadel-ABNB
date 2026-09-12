# Morning report — overnight revenue-forecast programme

**Written 11 Sep 2026, ~12:30 ET, for Theo. Everything below ran overnight while you were asleep.**
7 build packages + L0 spine + shared harness + scoreboard + optimal mix + adversarial red team.
Nothing committed to git. No file outside `analysis/src/forecast_methods/`, `data/processed/forecast_methods/`
and `docs/revenue-forecast-strategy/05_backtests/` was written.

---

## Orchestrator addendum (Claude, 12:55 ET) — read before the executive summary

- **Scoreboard re-scored after the red team.** `harness/score.py` was re-run at 12:50 ET: `scoreboard.csv` now has **273 rows (was 201)**; all 20 optimal-mix registry files are scored (72 rows); **70 of 272 rows survive both windows**. Red-team must-fix #5 is closed. The narrative in `05_backtests/SCOREBOARD.md` predates this re-run — for mix rows read the CSV.
- **The FX nuance to carry into the memo.** Full-sample, the free fit wins and a pure two-quarter lag is rejected (section 2). But on the three most recent *stated* quarters (4Q25–2Q26) the lagged Φ kernel at the fitted scale 0.851 tracks management's FX within **0.22pp** (2.71 / 4.25 / 2.88 vs stated 3.0 / 4.0 / 3.0) while the full-sample free fit misses by **1.21pp** (3.97 / 3.20 / 1.15). Either the effective lag lengthened in the RNPL / hedging era or n = 3 is noise — the stated 3Q26 FX on 5 Nov is the live test. Practical rule: forecast the *guide* with the lag-loaded spec (best PIT forecaster), describe the *history* with the free fit, and quote the effective-lag confidence set, never a point.
- **Run log.** Stage 1 (methodology: 5 ground-truth agents → 6 proposals → 6 critiques → architect; 18 agents, 89 min) and Stage 2 (this build: chief-of-staff → L0 spine + harness → 7 packages with verify/fix/re-verify → scoreboard → optimal mix → red team → this report; 33 agents, 2h35m, 5.8M tokens). Stage 2's first launch was killed by the Claude session usage limit at ~05:30 and resumed at 10:03 ET. Three Stage-1 agents lost only their JSON index (an apostrophe in the OneDrive path); every file was written. Full log: `00_OVERNIGHT_RUNBOOK.md`.
- **Shareable page:** https://claude.ai/code/artifact/253022ba-033a-43f8-a930-1d769a674a03 (private until you share it).
- **Nothing is committed.** Suggested: branch `theo/forecast-methods-overnight`; commit `analysis/src/forecast_methods/` (1.4 MB), `data/processed/forecast_methods/` (5.3 MB) and `docs/revenue-forecast-strategy/`. The venv is outside the repo at `~/.venvs/citadel-abnb`.

---

## Executive summary — 12 lines

1. **Your two-quarter FX proxy is not supported by the data.** Effective lag is **0.4-0.5 quarters**, 95% confidence set **0.03-0.92**; pure lag-2 × 0.56 is the *hardest-rejected* of four restrictions (LR 24.7, p < 0.0001 gross; p = 0.0005 on the stated series, independently re-tested by the red team). Weight on lag 2 is 0.00-0.04.
2. **But your instinct survives in the form that matters.** At a *guide date* only ~39% of the guided quarter's FX is observable, so the lag-loaded spec (H2) is the best point-in-time forecaster (RMSE 0.99pp, bias +0.10) while the free fit wins in-sample. FX hits *revenue* with a short lag and *the number management can see* with a long one.
3. **Once management has guided, nothing we built beats guide midpoint × (1 + trailing-8 cushion).** RMSE ratio to naive 0.377 (W1) / 0.319 (W2). The red team withdrew our claim that `print_from_guide` beats it — the baseline wins both windows. That is the honest headline and it must lead the memo.
4. **At the pitch date, when no 4Q26 guide exists, the kernel is the constructive object**: `revenue_q = λ_season × [⅔GBV_{q−1} + ⅓GBV_{q−2}]`, ex-COVID estimation window, ratio 0.555 / 0.484, PIT KS p = 0.63. It beats naive, AR(1), trailing-4 and the vintage-stamped pre-guide Street on both windows.
5. **The optimal mix does not beat the best single method on any of 18 target-pool cells.** It *does* beat the implementable choice (top-1 by trailing MSE) on 16 of 18. Combining beats the model you would have chosen, not the model that turned out best.
6. **3Q26 print: $4,816M**, mixture sd $48M, 80% conformal [$4,757, $4,876]. Frozen card says $4,805M. Zacks $4,740M (4 Sep). LSEG pre-guide $4,610M (6 Aug). We are above the top of the $4,690-4,770M guide, as a +1.86% cushion implies.
7. **4Q26 guide midpoint: $3,142M no fee step / $3,181M half step**, predictive sd 2.7-3.0% — **but the red team found this is anchored on a hand-set GBV_3Q26 of $26,300M while our own combined forecast is $26,550M.** Re-running with our own number gives **$3,161M** and P(guide < Zacks $3,200M) falls 0.730 → 0.657; P(< 36-analyst $3,158M) falls 0.568 → **0.486**. With a half fee step on top, the trade disappears. **This is the #1 must-fix.**
8. **FY27 $15,838M, +11.5%** vs Zacks $15.73-15.76bn — a +0.59% level edge and only **+0.09pp of growth**. The kernel weight moves FY26 as well as FY27, so across w = 0.33-0.667 growth spans **+9.18% to +11.52%** and the edge is **−2.25pp at the low end**. FY27 is exploratory, not a variant view on level.
9. **Forward-multiple implication, applied once:** +0.48 EV/EBITDA turns per growth point → **+0.043 turns** on our edge. Kernel-weight indeterminacy alone is **±1.12 turns**, ~25× larger. The pitch is about the guide and the composition, not the level.
10. **Three live 3Q26 objects are mutually inconsistent on take rate** — 18.14% (implied by mix revenue ÷ mix GBV, *clears* the frozen 18.10% pre-registration), 17.81% (published take-rate object, P(clear) = 0.254) and 18.40% (fee-takerate, P = 0.775). Our one pre-registered test has three answers. Must-fix #3.
11. **What is genuinely earned and defensible:** the scoring machinery reproduces exactly (200/200 rows, zero mismatches, independent pure-pandas recompute); the stacking is leakage-clean under attack; the FX lag fit reproduces independently to the digit; the λ conversion table reproduces to 2dp from the KPI panel alone; and **no take-rate object of any kind beats a plain seasonal naive** — take rate is an output, not a lever.
12. **Irreversible clocks start today:** Inside Airbnb daily capture (28 of 73 historical CDN probes already dead), consensus vintage stamps, fee-deadline listed-price panels 14/16 Sep and 12/14 Oct, spec freeze `ABNB-INT-v1` before 2 Oct.

---

## 1. Headline in three sentences

The programme built and point-in-time backtested seven method families against five baselines on two expanding windows (W1: 14 guide dates from 1Q23; W2: 10 from 1Q24), registered 57 objects and scored 200 cells, and the single most useful finding is negative: **once Airbnb has guided, guide midpoint × (1 + trailing-8 cushion) is the forecast, and nothing we built beats it** — so the pitch's edge cannot be a level call on a guided quarter. **Your two-quarter FX proxy is rejected as a description of the revenue-FX series** (effective lag 0.4-0.5 quarters, 95% CS 0.03-0.92, zero weight on lag 2, pure lag-2 the hardest-rejected restriction of four) **but is vindicated as a statement about the guide date**, where only ~39% of the guided quarter's FX is observable and the lag-loaded spec out-forecasts the contemporaneous one on both windows. The red team confirmed the machinery (all 200 scoreboard cells reproduce exactly under an independent recompute; the stacking survived every leakage attack) and refuted four headline claims, of which the binding one is that **the 4Q26 guide probabilities rest on a hand-set GBV input our own forecast contradicts** — fix that before anything goes in the memo.

---

## 2. The FX answer to your question

### 2.1 Verdict: the two-quarter proxy is NOT supported

Rebuilt from the FRED dailies + judgement currency weights + trailing-4 filed regional shares, fitted by **interval likelihood on the letter-rounded integers** (scored on [x−0.5, x+0.5], never as points), n = 14 disclosed revenue-FX observations:

| quantity | gross ex-hedge | stated (after hedge) |
|---|---|---|
| a₀ / a₁ / a₂ (lags 0/1/2) | 0.538 / 0.4135 / 0.000 | 0.45 / 0.36 / 0.03 |
| normalised w₀ / w₁ | 0.565 / 0.435 | — |
| scale | 0.9515 | 0.8511 |
| **effective lag (quarters)** | **0.435** | **0.512** |
| 95% confidence set on effective lag | **[0.029, 0.923]** | [0.0, 1.2] |
| σ | 0.878pp | 1.034pp |

Red-team independent rebuild: a = 0.4526 / 0.3612 / 0.0373, scale 0.8511, effective lag 0.512, σ 1.034 — **matches the package to the digit**; all five LR p-values reproduce within 0.01.

**Restriction tests (× 0.56 disclosed non-USD revenue share), gross series:**

| restriction | LR | p | verdict |
|---|---|---|---|
| Theo pure lag-2 | 24.73 | **< 0.0001** | rejected hardest |
| Architect Φ = (0, ⅔, ⅓) | 16.76 | 0.0008 | rejected |
| pure lag-1 | 12.94 | 0.0048 | rejected |
| contemporaneous (lag 0) | 12.27 | 0.0065 | rejected |

On the **stated (after-hedge)** series contemporaneous survives at p = 0.060 and pure lag-1 at p = 0.075, while **lag-2 is still rejected at p = 0.0004**. Univariate correlations: lag-0 r = 0.800, lag-1 r = 0.797 (a dead heat — the M6 claim that lag-1 0.861 beats lag-0 0.763 is **withdrawn**), lag-2 r = 0.531. LOO RMSE: free 1.155/1.494, lag-1 1.428/1.507, lag-0 1.364/1.554, Φ 1.707/1.677, lag-2 **2.218** vs baselines zero 2.268-2.473 and last-value 2.109.

**One quarter of lag is not identified at n = 14.** Two quarters is.

### 2.2 Where your instinct *is* right — the reconciliation

At a guide date you have observed roughly **39%** of the guided quarter's FX. So the specification with **no lag-0 loading at all** (H2, Φ on ADR-FX, one free scale) is the best *point-in-time* forecaster: **RMSE 0.9936pp W1 / 0.9898 full-sample, bias +0.0975pp, interval RMSE 0.578** against 1.49-1.77pp for the contemporaneous and free-weight specs. The free fit describes the world better; the lagged fit forecasts better from the chair management sits in.

**The sentence that survives cross-examination:** *"FX reaches revenue with an effective lag of under one quarter, so by the time Airbnb guides, roughly two-thirds of the FX in the guided quarter is already fixed — and the part still moving is the part management least wants to guess, which is why the lagged proxy out-forecasts the contemporaneous one at the guide date."*

A second finding the round-1 bug had hidden: the **hindsight premium dominates the hypothesis race.** Knowing the weights is worth +0.88, +0.83, +0.51, +0.31, 0.00, −0.06pp of W2 RMSE across the six specs — **larger than every spec-versus-spec difference in the PIT table.** Any FX backtest in this family without a PIT replay is typically 0.3-0.9pp too good.

### 2.3 Already-determined share — the triple, never one number

`fx_lag/10_determined_share.csv`. Formula: determined = (1 − w₀) + w₀ × (days elapsed / days in quarter).

| date | what | target | w₀ = 0.15 (CS lo) | **w₀ = 0.57 (point)** | w₀ = 0.97 (CS hi) | w₀ = 0.75 (M6 λ) | **volume-determined** |
|---|---|---|---|---|---|---|---|
| 2026-08-06 | 3Q26 guide date | 3Q26 | 0.91 | **0.66** | 0.41 | 0.54 | 1.00 |
| 2026-09-11 | today (28 Aug FX) | 3Q26 | 0.97 | **0.88** | 0.79 | 0.84 | 1.00 |
| **2026-10-02** | **memo due** | **4Q26** | 0.85 | **0.44** | 0.04 | 0.26 | **0.333** |
| **2026-10-23** | **finals** | **4Q26** | 0.89 | **0.57** | 0.26 | 0.43 | **0.333** |
| 2026-11-05 | 4Q26 guide date | 4Q26 | 0.91 | **0.65** | 0.40 | 0.54 | **1.00** |
| 2027-02-11 | 1Q27 / FY27 guide | 1Q27 | 0.92 | **0.69** | 0.47 | 0.59 | 1.00 |

Three numbers to say together for 4Q26: FX-determined at 5 Nov **0.65 (band 0.40-0.91)**; volume-determined at 5 Nov **1.00** (3Q26 GBV prints that morning, so the kernel base is fully known); volume-determined at the **pitch date 0.333** — only 2Q26 GBV is printed and 3Q26 GBV carries two-thirds of the weight. **State that asymmetry in the pitch; do not gloss it.** The M6 λ = 0.75 gives 0.54, inside the band and the *pessimistic* end. The "82% determined" and "85-90% on the ledger" claims are used nowhere and should be retired.

### 2.4 The forward schedule (spot held from 2026-08-28)

| quarter | spot held | weak USD (+5%) | strong USD (−5%) | 80% band |
|---|---|---|---|---|
| 3Q26 | **+1.2** | +1.2 | +1.2 | 0.0 to +2.3 |
| 4Q26 | **+0.7** | +2.2 | −0.8 | −0.4 to +1.8 |
| 1Q27 | +0.5 | +3.1 | −2.2 | −0.7 to +1.6 |
| 2Q27 | +0.1 | +2.8 | −2.7 | −1.1 to +1.2 |

**FY27 FX is the revenue-weighted AVERAGE of the four quarterly contributions: +0.2pp.** Never their sum (0.5 + 0.1 + 0.2 + 0.1 = 0.9). The package parks the sum in a column literally named `sum_of_four_quarters_pp_DO_NOT_QUOTE`. Weak USD +2.3pp, strong USD −2.0pp on the same averaging. 2025 actual revenue shares (0.186/0.253/0.335/0.227) vs a simple mean differ by < 0.05pp.

### 2.5 The four-way reconciliation — this is the memo exhibit

| construction | 4Q26 FX pp | status | named cause |
|---|---|---|---|
| repo `05_fx_schedule.csv` `revenue_fx_fit_pp` | **−0.4** | rejected as input | reduced-form level fit; re-applies a lag already inside the lagged GBV base |
| repo `29_q4_fy27_bridge.py` FX step | **−3.4** | rejected as input | **subtracts the FX step a second time** on a GBV base that already carries booking-date FX |
| M6 memo forward schedule | **+0.4** | rejected as input | rests on an FX fit that misses a nearly-observed quarter by ~2pp; the memo's own schedule carries +1.04pp against +0.73pp in its own 3Q26 build |
| guide-anchored (hold management's Q3 assumption flat) | **+2.6** | rejected as input | the basket itself rolls over; flat imports a tailwind spot has already removed |
| **kernel-implied (adopted, as an OUTPUT)** | **+0.6 to +0.7** | **adopted** | booking-date FX is already inside the lagged USD GBV base; the pp shown is what the arithmetic *produces*, never an adjustment applied to it |

Spread −3.4 to +2.6 = **6.0pp = $167M** of 4Q26 revenue. Excluding the double-subtraction, −0.4 to +2.6 = 3.0pp = **$84M**. **Our internal disagreement about FX alone is larger than the gap between our 4Q26 number and the Street's, and saying so first is a point in our favour.**

Two caveats that travel with every FX number:
- **The mechanism is real and is not what the regression measures.** Booking FX sits inside the lagged GBV base; the lag is an OUTPUT and is never subtracted twice.
- **The fitted gross scale 0.95 excludes the disclosed 0.56 non-USD revenue share** (CS 0.625-1.325). Our judgement currency weights understate exposure by roughly 70%. Anyone using this basket for a *level* rather than a *change* must rebuild weights from booking-currency data first.
- **On the live quarter the model is wrong in the architect's direction.** We register 3Q26 FX at **+1.2pp** (80% band 0.07-2.33) against management's **~+3.0pp after hedging** in the verified 6 Aug letter. Management sits outside our own interval. On 1Q26/2Q26/3Q26 the architect's Φ weights at our fitted scale give 2.71/4.25/2.88 vs stated 3.0/4.0/3.0 (mean abs error 0.22pp) against our free fit's 3.97/3.20/1.15 (MAE 1.21pp). **Strike the +1.2pp or publish it beside management's +3.0pp with the tension explained.**

Hedge accounting, for completeness: `gross_ex_hedge + hedge_effect = stated` holds on all 14 quarters to 1e-6. Hedges did nothing to revenue growth 1Q23-2Q25; from 3Q25 they subtract −1.13, −0.93, −0.66, −0.61pp as designated notional grew $2.6bn → $3.4bn (45-47% of LTM non-USD revenue). **The forward hedge file is never added on top of stated after-hedge FX.**

---

## 3. What was built tonight

| package | status | verify | key numbers | registry objects |
|---|---|---|---|---|
| **harness** (frozen, do not edit) | complete | n/a | target panel, PIT calendar, 5 baselines, scorer, registration format v1.0. 200 scoreboard cells. | 6 baseline objects |
| **L0-spine** | complete | pass | 72 exact regional revenue cells (56 filed + 16 back-out), 0 restated rows, basis flags | registers nothing (correct) |
| **kernel-lambda** | complete | **pass** | All 12 architect λ cells reproduce to 2dp (max diff 0.0005pp); Q4 range 0.171pp exact. Best PIT object `last3_ex_covid` 0.555/0.472, KS p 0.63. 3Q26 print $4,804M. 5 free params. | 10 |
| **fx-lag** | complete | **pass** | Object A eff. lag 0.435, CS [0.029, 0.923], H0 LR 16.762 p 0.0008, n 14. H2 PIT RMSE 0.9936. Determined-share triple. Four-way reconciliation. Deterministic, ~25s. | 3 |
| **guidance-policy** | complete | **pass** | `print_from_guide` 0.3788/0.3308 on **1 parameter**. Gate G4 **FAILS** both windows (7/14 p 0.605; 4/10 p 0.828). Drift rule dead: 8/9 executable, spread −1.50pp, Fisher p 0.141. | 5 |
| **fee-takerate** | complete | **pass** | **0 of 8 rows beat a plain seasonal naive** (lastyear 1.003/1.055, kernel 1.342/1.299). θ unidentified. Fee step +0.28 to +1.48pp at half weight, not +2.5%. A5 deliberate documented FAIL. 11 free params. | 3 |
| **l1-reconciliation** | complete | **pass** | G2 passes: 72/72 cells exact to 2.3e-13; 16/16 annual nights inside ±0.5M. FY27 $15,838M, +11.52%. A8 **still fails** (ex-FX ADR +2.60/+2.01/+3.13 vs note +3.10/+3.44/+3.41). 60 free params. | 3 |
| **calibration-rail** | complete | **partial** | Fixed a real bug: z-scores were passed as quantile *levels*; 128 of 284 PIT values were outside [0,1], now all 284 in range. Part (d) counts corrected to 12 biased / 21 calibrated / 1 overconfident. 4 note-level items open. | 5 |
| **tracker-backlog** | complete | **pass** | Gate G1 raw revenue **FAILS** both windows (1.171/1.168). RNPL-corrected `unearned_rnpl` k1.0 0.680/0.593, **caveated**. Legacy 0.600 reproduced as a truncated-training artefact, not corroboration. 768 registry rows, md5-stable. | 2 |
| **optimal-mix** | complete | n/a | 110 candidates, 4 pools, 7 schemes, both windows, both prior replays. 18 combined objects. 3 bugs found and fixed. | 18 |
| **red-team** | complete | n/a | 200/200 cells reproduce under independent pure-pandas recompute. 4 fatal, 12 must-fix, 12 confirmed, 11 withdrawn. | — |

**Every package registered. All 37 files parsed and validated; none needed a format fix; none excluded. Six verified pass; calibration-rail partial.**

---

## 4. The scoreboard, one table per target

Rules: RMSE ratio to the harness naive on the same series; PIT prior unless stated; survives-both means **both** W1 (n = 14) and W2 (n = 10).

### 4.1 Revenue level — the target that matters

| rank | object | W1 | W2 | vs guide+cushion | vs Street | survives both |
|---|---|---|---|---|---|---|
| **1** | **baselines `guide_cushion`** | **0.377** | **0.319** | *is* the benchmark | beats it | **yes** |
| 2 | guidance-policy `print_from_guide` (1 param) | 0.379 | 0.331 | **loses both** (35.617 vs 35.457 W1; 35.865 vs 34.596 W2) | beats it | yes |
| 3 | kernel-lambda `next_q_last3_ex_covid` | 0.555 | 0.472 | loses 0.555 vs 0.377 | beats pre-guide Street both | yes, KS p 0.63 |
| 4 | kernel-lambda `next_q_ex_covid` | 0.565 | 0.484 | loses | beats both | yes |
| 5 | `print_kernel_policy` / kernel `last3` | 0.766 | 0.647 | loses | beats | yes |
| 6 | kernel published w = ⅔ spec | 0.831 | 0.727 | loses | beats | **PIT rejected W1, KS p 0.0027** |
| — | baselines `street` (vintage-stamped) | 1.073 | 0.871 | — | — | **no** (fails W1) |
| — | baselines `ar1` | 1.101 | 1.009 | — | — | no |
| — | kernel `revenue_level_h1` (2q ahead) | 1.169 | 0.886 | — | — | no — published negative |
| — | kernel `w038` / `w033` | 1.433 / 1.584 | 1.196 / 1.311 | — | — | no — **COVID replay artefact, not evidence for ⅔** |
| — | baselines `trailing4` | 1.806 | 1.101 | — | — | no |
| — | baselines `naive_seasonal` | 3.754 | 3.115 | — | — | no |
| — | l1 `revenue_contemporaneous` | 11.338 | 10.093 | — | — | no — **deliberate negative control** |

**Best for a guided quarter: `guide_cushion`. Best at the pitch date, with no guide: kernel `ex_covid` (0.565/0.484).** These occupy different information sets and are not competitors.

### 4.2 Revenue y/y

| object | W1 | W2 | survives both |
|---|---|---|---|
| kernel-lambda `revenue_yoy_next_q` | 0.903 | 0.756 | yes, uncaveated |
| tracker-backlog `unearned_rnpl` k1.0 | 0.680 | 0.593 | yes but **heavily caveated** — read as corroboration, not a forecast |
| tracker `unearned_rnpl` k1.5 / k0.5 | 0.778 / 0.853 | 0.714 / 0.804 | yes, same caveat |
| tracker `unearned_raw` (Gate G1) | 1.171 | 1.168 | **no — G1 fails** |

Caveat that must travel with every tracker number: k is a researcher-**assumed swept** input; 2 of 14 (W1) / 10 (W2) dates use researcher-assumed RNPL shares; the raw feature fails; the surviving specs registered **no LIVE row**. No cushion or Street baseline exists for a growth target.

### 4.3 Guide midpoint

| object | metric | vs Street | survives |
|---|---|---|---|
| guidance-policy `guide_mid_next_q` (6 params, the only object) | 0.869 W1 / 1.049 W2 on its local naive | **LOSES both**: MAE 1.986 vs 1.966% W1; 1.762 vs 1.609% W2; bias +1.12 vs −0.51 | **no** |

**Gate G4 fails both windows: 7/14 (p 0.605) and 4/10 (p 0.828) on sign.** `rmse_ratio_to_naive` is NaN on all four rows — the harness has no naive baseline for this target. **We have no measured edge over the pre-guide Street on the level or the sign of the next guide midpoint.** Per the integrated system's own G4 rule: lead the memo with the FX/mix decomposition, not the gap forecast.

### 4.4 Nights, GBV, ADR, take rate, FX

| target | best | W1 | W2 | survives |
|---|---|---|---|---|
| nights y/y | tracker `unearned_rnpl` k0.5 vs the *local* calibration-rail `ref_naive` | 0.750 | 0.875 | yes, local ref only |
| nights y/y raw (Gate G1) | tracker `unearned_raw` | 0.904 | **1.183** | **no — partial only** |
| nights level | **baselines `naive` — nothing registered beats it** | 1.000 | 1.000 | — |
| gbv level | **baselines `naive`**; trailing4 1.668/1.136, ar1 1.662/1.225 both lose | 1.000 | 1.000 | — |
| gbv y/y | calibration-rail `ref_naive`, RMSE 3.662 / 3.423 | — | — | nothing else registered |
| adr y/y | calibration-rail `ref_ar1` — a statistical tie with `ref_naive` | 0.972 | 0.995 | local ref only |
| **take rate %** | fee-takerate `take_rate_lastyear`, which **still does not beat a plain seasonal naive** | 1.003 | 1.055 | **no — 0 of 8 rows beat it** |
| revenue FX pp | fx-lag **H3** free weights, all 14 W1 quarters, RMSE 1.485 / 1.697 | — | — | **no harness naive exists → ratio NaN → survives-both is False for every FX object** |

**Do not read fx-lag H2's "0.994" as a ratio. It is an RMSE in pp on 10 quarters.** Withdrawn as a surviving object.

### 4.5 Four scoreboard rows are VACUOUSLY "surviving"

`calibration-rail__gbm_surprise_guide` (0.339), `gbm_revenue` (0.927), `fx-lag__h2` (0.994) and `l1__revenue_contemporaneous` are scored on **2024Q1-2026Q2 in BOTH windows** — W1 is literally the same ten quarters as W2. **Read them as W2-only.**

---

## 5. The optimal mix

**Method.** 110 candidates from 36 non-own registry files. Four pools chosen on coverage or published attributes only, never on performance: `all` (full 14-quarter W1 coverage), `noguide` (drops guide/consensus consumers — the pitch-date information set), `parsimonious` (published n_params ≤ 2), `repaired` (take rate, minus three broken calibration-rail ref rows). Seven schemes: equal, inverse-MSE, constrained NNLS stacking on PIT errors, 50-50 shrinkage toward equal, BMA with log-predictive-score weights from the registered quantiles, top3-by-trailing-MSE, top1-trailing. Weights at guide date *d* fit only on pairs whose target quarter printed strictly before *d*, expanding, both windows, both prior replays. **Combined sd is the mixture sd, not the inverse-variance sd, so candidate disagreement widens the interval.**

**Does it beat the best single method? No — not on any of 18 target-pool cells.** Eighteen verdicts of *best single method is the mix*. Best single-window gains: revenue-parsimonious BMA **+4.43% on W1 but −4.16% on W2**; take-rate-repaired −0.38% W1 / +4.64% W2. Dead heats on n = 14 and 10 — exactly what the both-windows rule exists to catch.

**But that bar is an ex-post oracle.** Against the *implementable* choice (top-1 by trailing MSE, refit each guide date) **the mix wins on both windows in 16 of 18 cells**; the two losses are `adr_yoy`, where the pool is three near-identical references. Margins: revenue no-guide **−10.4% W1 / −14.8% W2**; revenue y/y **−28.5% / −52.6%**. *Combining does not beat the model that turned out best; it beats the model you would have chosen.*

**What the weights say — this is the substantive result.**

| pool | scheme | weights |
|---|---|---|
| Revenue level, 14 candidates | BMA at the last W1 vintage | `guide_cushion` **0.546**, `print_from_guide` **0.454**, all twelve others (incl. **all seven kernel objects**) under 0.005 combined |
| Revenue level, 6 parsimonious | constrained stack | `print_from_guide` 0.672, `guide_cushion` 0.182, **pre-guide Street 0.146**, exactly zero on naive, AR(1), trailing-4 |
| Revenue level, **NO-GUIDE** (the pitch-date set) | top3 | kernel `ex_covid` 0.397, kernel `last3_ex_covid` 0.397, `print_kernel_policy` 0.207 — **100% on the kernel family** |
| Take rate, repaired | inverse-MSE | `take_rate_lastyear` 0.641, `take_rate_kernel` 0.359 |

Once a guide exists, a leave-future-out optimiser puts essentially all weight on guide × (1 + trailing-8 cushion). The one thing it adds is a ~15% tilt toward the vintage-stamped Street in the parsimonious pool — a small, genuinely earned result.

Scheme ranking on revenue level W1: BMA 0.432 < stack_ls 0.456 < top3 0.466 < inverse-MSE 0.521 < stack_shrunk 0.540 < equal 0.637, **against the guide-cushion single at 0.377**. `equal` and `inverse-MSE` are **PIT-rejected** on revenue level W1 (KS p 0.018, 0.039) and biased +29.2 / +23.1 $M — a large pool in which most candidates over-forecast makes naive averaging actively harmful.

**The winning schemes (BMA, inverse-MSE, top3) add ZERO free parameters** — weights are deterministic functions of the training block. The schemes that spend parameters (stack, K−1) do not win.

**Leakage controls that survived attack:** weights filtered by `printdates[h] < vintage_date` from the harness calendar; scheme functions have no notion of time at all (the caller assembles the training block, so they cannot leak on their own); both prior replays published side by side; pool membership never chosen on performance; the 6 Aug 2026 guide is LIVE and enters no metric and no gate; the harness `baseline_street` **mechanically refuses any consensus row postdating the vintage**, so the kill-list rule about September vendors is enforced in code, not by discipline; optimal-mix drops its own rows on every run so it cannot eat its own output; live objects carry an explicit weight-coverage check.

**Prior-replay warning.** The no-guide kernel pool nearly **halves** its RMSE under full-sample priors (66.77 → 35.97 on W1, a 30.8 $M gap) while the guided and parsimonious pools are replay-invariant. **Any kernel walk-forward number quoted without naming the replay is off by about a factor of two.** The PIT-vs-full-sample gap reaches 51% on fx-lag H3 W2 (0.824 full-sample vs 1.697 PIT) and 41% on `guide_mid_next_q`.

**Three bugs found and reported:** SLSQP silently stalled at the equal-weight start for K = 14, making the stack look identical to equal (fixed with an NNLS simplex solve); `spec_id` embeds the `prior_basis` token in two packages, so a naive consumer sees two candidates where there is one; the harness take-rate classification bug is worth a **factor of 4.2** in RMSE (1.374 with the broken ref rows in the pool, 0.327 without).

---

## 6. The live calls, with vendor stamps

### 6.1 3Q26 print (prints ~5 Nov, after finals)

| source | value | stamp |
|---|---|---|
| **Our combined object** | **$4,816.1M**, mixture sd $48.0M | 11 Sep 2026 |
| 80% split-conformal | [$4,756.7, $4,875.6], half-width $59.5, n_cal = 8 | exchangeability **violated**; attainable band 88.9-100%; **no 80% guarantee** |
| Frozen card `20_frozen_q3_2026.csv` designated | $4,805.1M (+1.37% surprise on a $4,740M bar) | spec freeze 6 Sep 2026 |
| kernel-lambda live object | $4,804M, q10-q90 $4,707-4,903, sd $77M | ⅔×27,200 + ⅓×29,200 = 27,867 × 17.239% |
| guide + cushion | $4,730 × 1.0186 = **$4,818M** | 6 Aug 2026 letter |
| Zacks (7-estimate) | $4,740M | **4 Sep 2026** |
| LSEG pre-guide next-Q | $4,610M | **6 Aug 2026** |
| Management guide range | $4,690-4,770M | 6 Aug 2026 |

We are **+$76M vs Zacks, +$206M vs the LSEG pre-guide, and above the top of the guide** — as a +1.86% cushion implies. **Honest framing: the $4,816M is not a 14-method combination.** BMA weights are 0.537 `guide_cushion` / 0.463 `print_from_guide` — the same estimator with a median vs a mean cushion. It is arithmetically $4,730 × 1.0182. **One method. Say so.** The kernel's $4,804M and guide+cushion's $4,818M are **two constructions 0.3% apart, not three.**

Other 3Q26 live objects: nights **147.38M** (q10-q90 143.4-151.3; frozen card designated 147.6M), GBV **$26,549.8M** (25,456-27,643), ADR y/y **+5.27%**, GBV y/y **+15.94%**. **3Q26 nights y/y and revenue y/y are published as a labelled FAILURE** — the winning weights sit almost entirely on tracker-backlog specs that registered no LIVE row, surviving weight coverage is 2.4e-11, and the printed number is a renormalisation onto `ref_naive`.

**Take rate — three answers, one pre-registered test.** Mix revenue ÷ mix GBV = **18.140%**, which *clears* the frozen 18.10% pre-registration. The published take-rate object says **17.807%** with P(clear) = **0.254**. fee-takerate publishes **18.397%** with P = **0.775**. The same block breaks GBV = nights × ADR by 0.22pp. **This must be reconciled before the memo, and the single pre-registered probability re-run from the reconciled number.** And carry 17.81% as a *mechanism*, not a forecast: no take-rate object of any kind beats a plain seasonal naive on either window.

### 6.2 4Q26 guide midpoint, 5 Nov 2026

Central inputs: GBV_3Q26 $26,300M (hand-set, **contested**), λ_Q4 12.0298%, base $26,600M, mean trailing-8 cushion **+1.857%**, predictive sd **3.03pp measured** (not the 2.6pp the decision document assumed).

| fee-step case | print | **guide mid** | range | P(< Zacks $3,200M, 10 est., **4 Sep**) | P(< 36-analyst $3,158M, **11 Sep**) |
|---|---|---|---|---|---|
| **no step** | $3,199.9M | **$3,141.6M** | $3,115-3,168 | **0.730** (mix sd: 0.752) | **0.568** (mix: 0.576) |
| **half step** | $3,239.9M | **$3,180.9M** | $3,154-3,208 | **0.579** (mix: 0.587) | **0.406** (mix: 0.396) |
| full step (**EXCLUDED**) | $3,279.9M | $3,220.1M | — | 0.418 | 0.262 |
| fee-takerate primitives, no step | $3,200.0M | $3,141.4M | — | — | — |
| fee-takerate primitives, half step | $3,218.2M | $3,159.4M | — | — | — |

Across the GBV_3Q26 grid $25,900-27,000M the guide midpoint spans **$3,110-3,277M** and P(< Zacks) spans **0.220-0.830**.

**THE BINDING PROBLEM.** The object is anchored on a hand-set GBV_3Q26 of **$26,300M** while our own combined 3Q26 GBV forecast is **$26,549.8M**. Re-running with our own number: **guide mid $3,161.3M**, P(< Zacks $3,200M) **0.730 → 0.657**, P(< 36-analyst $3,158M) **0.568 → 0.486 — below one half.** With a half fee step on top, **the trade disappears.** Never publish 0.73 / 0.58 without 0.66 / 0.49 alongside.

**The trade flips on the vendor.** 58-75% against Zacks; a coin toss or worse against the 36-analyst panel. And say first that **consensus disagrees with itself by $126M** — Zacks's own quarterly sum is $14,226M against its own FY26 of $14,100M.

**The fee step, recomputed from primitives, is +0.28 to +1.48pp at half weight** against the +2.5% full step the architect arithmetic implies. The full-step central case is excluded because fee-takerate measures θ < 1, where migrated-cohort GBV falls. **And pick one predictive sd** — guidance-policy 3.03% gives P = 0.730; optimal-mix 2.73% gives P = 0.752 for the identical event.

### 6.3 FY27 — label it exploratory

**FY27 revenue $15,837.6M at kernel w = ⅔; $15,779.5M at 0.50; $15,720.3M at 0.33. Growth +11.52%.** Kernel-weight sensitivity $117.3M = 0.74% of revenue = **2.343pp of growth**.

Against **Zacks FY27 $15.73-15.76bn (4 Sep 2026, midpoint $15,745M)** we are **+0.59% on level** and **only +0.09pp on growth** vs the Street-implied +11.43%. **Say that in the first 200 words.**

**But the kernel weight moves FY26 as well as FY27.** Across w = 0.33-0.667 growth spans **+9.18% to +11.52%**, so the +0.09pp edge exists *only at w = ⅔*; at w = 0.33 the edge is **−2.25pp**. l1-reconciliation registers **nothing at annual horizon**, and its only registered revenue object is a declared negative control at ratio 11.34. **FY27 is exploratory.**

**Decomposition — must be rebuilt before the memo (fatal finding).**

| line | pp | owner | status |
|---|---|---|---|
| NA nights | +2.34 | volume | computed |
| EMEA nights | +2.90 | volume | computed |
| LatAm nights | +1.60 | volume | computed |
| APAC nights | +1.41 | volume | computed |
| **volume subtotal** | **+8.26** | | |
| within-region ADR ex-FX | +3.00 | price | deliberately unsplit |
| geographic mix | −1.09 | — | **ALREADY INSIDE volume × ADR — double-counts** |
| unit size & LOS (elasticity 0.23) | +0.38 | — | **ALREADY INSIDE — double-counts** |
| seats & hotel dilution | 0.00 | — | nets out of GBV |
| booking-date FX | 0.00 | — | already inside the lagged GBV base |
| fee | +0.90 | — | **ASSUMED, not rebuilt.** fee-takerate says this is **−0.31pp too generous** at half weight |
| new lines | +0.20 | — | **ASSUMED, not rebuilt** |
| regulation | −0.30 | — | **ASSUMED, not rebuilt** |
| hedge | 0.00 | — | **ASSUMED, not rebuilt** |
| kernel timing | +0.17 | — | **NOT an identity — a residual** |
| **total** | **+11.52** | | |

The arithmetic: **(1 + 8.2632%) × (1 + 3.00%) = 11.5111% exactly**, which *is* the model's GBV growth. So mix and LOS are already inside those two lines; listing them additively double-counts **−0.71pp**. GBV-side lines sum to 10.5554pp against the model's own 11.5111pp — a **0.96pp unexplained gap**. And GBV growth 11.5111% − revenue growth 11.5228% = **−0.0117pp, not the published +0.1674pp**; the "kernel timing identity" is a residual equal to the omitted cross term (+0.2479) + true timing (+0.0117) − the five narrative lines (+0.0922). **Also: fx-lag says FY27 FX is +0.2pp, not zero.**

**Do not let the memo imply management gives an FY27 revenue number in February.** ABNB guides a **1Q27 range plus qualitative colour**. The comparable object is the **1Q27 guide midpoint**.

### 6.4 Forward-multiple implication, applied once

Rule: **+0.48 EV/EBITDA turns per point of forward revenue growth, applied once.**
- Our growth edge +0.09pp → **+0.043 turns.**
- Kernel-weight indeterminacy (w 0.33 → 0.667, 2.34pp of growth) → **±1.12 turns.**

**Our own unidentified parameter is worth roughly 25× more multiple than our level edge over the Street.** This is an *implication*, not a price target, and it is exactly why the pitch must be about the guide and the composition.

---

## 7. Red-team verdict — `sound_with_fixes`

### Confirmed under independent attack

1. **All 200 harness scoreboard rows reproduce EXACTLY** from the 57 registry CSVs under a fully independent pure-pandas recomputation — zero mismatches on n, MAE, RMSE, bias, ratio. **The scoring machinery is not fudging anything.**
2. **The stacking is leakage-clean.** No leakage attack could be constructed that the programme had not already disclosed.
3. `baseline_street` **mechanically** refuses any consensus row postdating the vintage — enforced in code.
4. Conformal residuals for the live 3Q26 object do not overlap the test period; all 14 come from quarters that printed before 11 Sep 2026.
5. `baseline_naive` reproduces from point-in-time inputs (2023Q1 = 1,509 × 1.2415 = 1,873.4) with **no revised-data contamination** on the revenue spine.
6. The **fx-lag Object A fit reproduces independently** to the digit; all five LR p-values within 0.01.
7. The Q4-26 arithmetic is right **given its inputs**: λ_Q4 12.0297%, base 26,600.0, print 3,199.9, guide 3,141.6, half 3,180.9, full 3,220.1, P = 0.730 at sd 3.03%.
8. The kernel 3Q26 live print reproduces exactly: 17.2393% × (⅔×27,200 + ⅓×29,200) = 4,804.0.
9. The vacuous-survivor flag is real; the take-rate classification bug is real and large (3.14-4.61 RMSE vs 0.326).
10. 70 of 200 rows fall below the 85.7% attainable conformal floor, minimum 0.250.

### Withdrawn — do not quote these

- ~~`print_from_guide` is the best revenue-level method.~~ **The guide-cushion baseline wins both windows.**
- ~~The $4,816.1M 3Q26 print is a 14-method combination.~~ It is $4,730 × 1.0182 — **one method**.
- ~~fx-lag H2 at 0.994 is a surviving object.~~ That is an RMSE in pp; the ratio is NaN; no FX object survives either window.
- ~~Kernel timing +0.167pp is an identity.~~ It is a residual.
- ~~Geographic mix −1.09 and unit-size/LOS +0.38 are separate FY27 contributors.~~ Already inside volume and ADR.
- ~~M6's lag-1 r 0.861 beats lag-0 0.763.~~ On the rebuilt basket it is 0.800 vs 0.797 — a dead heat.
- ~~0.56 × the 1Q26 basket reproducing 3Q26 FX to 0.1pp is evidence for a two-quarter lead.~~ The same rule misses the two quarters that actually printed by **−1.85pp (1Q26) and −1.90pp (2Q26)**.
- ~~P(4Q26 guide < Zacks $3,200M) = 0.730 and < $3,158M = 0.568.~~ Both are functions of a contested GBV input.
- ~~FY27 growth +11.52% and the +0.09pp edge.~~ The band is +9.18% to +11.52%; the edge is −2.25pp at the low end.
- ~~29 objects scored, registry fully covered.~~ **18 optimal-mix objects / 72 scoreboard groups are unscored.**
- ~~tracker-backlog revenue y/y 0.680/0.593 as a forecast.~~ Corroboration only.

### Must-fix before the memo — in priority order

1. **Reconcile GBV_3Q26 $26,300M against our own $26,549.8M** and restate every 4Q26 probability, or justify the architect's input in the memo. Never publish 0.73/0.58 without 0.66/0.49.
2. **Rebuild the FY27 decomposition.** State GBV growth multiplicatively; publish the +0.248pp cross term; move mix and LOS to a zero-weight attribution block; separate the four assumed lines (they are **not** in the computed $15,837.6M); delete the kernel-timing identity claim.
3. **Reconcile the three take-rate numbers** (18.14 / 17.81 / 18.40) and re-run the single pre-registered probability from the reconciled one. Impose GBV = nights × ADR on the live block.
4. **Strike the registered live 3Q26 FX of +1.2pp** or publish it beside management's stated ~+3.0pp with the tension explained.
5. **Re-run `harness/score.py`** — 72 registry groups (all 18 optimal-mix objects) are missing from a stale `scoreboard.csv`. "29 objects scored" understates the registry by 18.
6. **Correct the best revenue-level method** to the guide-cushion baseline. It is not a dead heat and it does not go the published way.
7. **Pick one predictive sd** for the 4Q26 guide (3.03% vs 2.73%) and **one fee-step arithmetic** ($3,239.9 vs $3,218.2 half-weight print).
8. **Relabel the 72 scoreboard rows with an empty ratio.** `survives_both_windows = False` there means **no baseline exists**, not tested-and-failed. It currently hides that **no FX object survives either window** and that take rate, guide_mid, adr_yoy, gbv_yoy and nights_yoy are untested against a harness naive.
9. **Label FY27 exploratory.**
10. **Quote no p-value for the guide-below-Street drift rule.** Three incompatible values circulate: 0.27 (kill list), 0.038 (repo WS20 restatement, which supersedes WS16), 0.141 (tonight). The rule is dead either way: executable 8/9, spread −1.50pp.
11. **Do not present the 15 Sep / 13 Oct 2026 fee-migration deadlines as disclosure.** They have **no source in the repository** — they are a dated assumption.
12. **Name the prior replay on every kernel and FX number quoted.**

---

## 8. What is NOT proven — the honest caveats

- **n = 14 and n = 10.** A 4% RMSE difference is not a result. Both "dead heats" on revenue level are exactly that.
- **Exchangeability is violated** by expanding-window refits on a trending target with a 2022 regime change. Split conformal here is **descriptive, not a guarantee**. At n_cal = 6, α = 0.2 the attainable band is 85.7-100%; at n_cal = 8 it is 88.9-100%. **80% coverage is unattainable by construction.** 80% interval coverage is 100% on every combined object — the intervals are conservative, not calibrated.
- **The pre-registered same-quarter test FAILED.** φ₀ = 0.225 (n=21) / 0.405 (n=18) / 0.390 (n=14); bootstrap CIs exclude 0.02 in all three; the free fit beats the φ₀ = 0 restriction out-of-sample in all three. Implied mean lag 0.95-1.18 quarters, **shorter than the 1.33 a ⅔-⅓ kernel implies. The memo must say "most", not "all", of the quarter is visible.**
- **The kernel weight is not identified and its shape is window-dependent.** LOO argmin: 0.76 (n=22), 0.68 (n=18), 0.32 (n=14), 0.13 (12 cells). Block-bootstrap 95% CI on the argmin spans ~0 to 0.9 in every window. The critic's shape (min near 0.33, ⅔ worse) reproduces only on 2023Q1+ and the 12 cells; on n=18, **⅔ IS the minimiser to three decimals.** The w=0.38/0.33 backtest objects losing at 1.43/1.58 is a **COVID replay artefact, not evidence for ⅔.**
- **The kernel's quoted walk-forward MAE 1.74 / RMSE 2.44 / bias +0.99 is not reproducible** as a strict PIT replay. Strict PIT is **2.313 / 3.066 / +2.230**. The quoted triple brackets the full-sample-prior replays — it reads as full-sample, not walk-forward.
- **The FX wedge is not distinguishable from zero** (slope +0.233, se 0.252, t 0.93, p 0.35 on 12 cells; interval-likelihood slope set [+0.087, +0.373]). The falsification survives, but the architect's +0.158 could **not** be replicated to the digit because the wedge construction is written down nowhere — this is a **re-derivation**.
- **fx-lag could not reproduce** the repo `rev_fx` fit (repo n=13 where the window has 14 non-null points; slope −0.5348 vs −0.5023; the repo file does not record which observation it drops) or the architect's Object C slope (0.389 vs 0.158 on eight conventions; n, se and the |t| < 2 conclusion **do** reproduce).
- **l1 A8 still fails:** within-region ex-FX ADR reproduces at +2.60 / +2.01 / +3.13pp against the ADR note's +3.10 / +3.44 / +3.41, worst gap −1.43pp. The FX split is identified only to about ±1.4pp. **Not fixable with the disclosures on disk.**
- **The regional ADR y/y disclosure class is mutually inconsistent** with filed revenue + annual nights + nights growth under a constant or linearly drifting regional take rate. Regional ADR *levels* are weakly identified (bootstrap p10-p90 ≈ ±15%), which is why only GBV crosses the L1 boundary.
- **fee-takerate A5 fails on the full 420-row file:** more listings raised than cut by over 10% (mean 0.2149 vs 0.2025; only 178/420 rows with more cutters). The claim holds **only on the 20-row Austin sub-sample.**
- **The fiat de-gross-up equation** `payout = ADR/(1 + share×θ×0.1479)` is dimensionally wrong for a GBV-basis reported ADR. Both forms are implemented side by side; `gbv_consistent` is the default. **A ruling is needed before the memo.**
- **STALE SOURCES: FRED daily FX ends 2026-08-28.** Nothing downstream of fx-lag is genuinely "as of 11 Sep". Every such label in the repo is really as of 28 Aug.
- **8 of 37 objects are unscorable by design** — LIVE-only with no actual. The harness LIVE window admits 2026Q3 only and has no annual slot, so fx-lag parks 5 forward rows and l1 parks 5 FY27 quarters in unregistered files; two packages needed `strict_windows=False`.
- **MISLABELLED REGISTRY:** `l1__fy27_revenue` and `fy27_growth` each hold **one 2026Q3 row** ($4,804.0M and +17.31%). **Neither is FY27.** The annual totals live only in the package grid file.
- **TWO ESTIMATORS, ONE NAME:** the harness `guide_cushion` baseline uses the **median** trailing-8 cushion; every live object uses the **mean** +1.857%. The scoreboard row is not the object generating the 4Q26 guide midpoints.
- **SCORER POOLS `spec_id`:** tracker-backlog's eight specs collapse into one series (n 112 / 80) whose RMSE is not a method score. Re-scored per spec on a relabelled copy using the harness's own `score_registry`; **no harness file edited.** No other package duplicates a cell (checked across all 37 files).
- **Ex-FX acceleration is flat, not +0.4pp.** At GBV_3Q26 $26,300M the kernel base step is −1.8pp against a −1.9pp FX step, giving **+0.1pp**; at the frozen card's $26,185M it **decelerates 0.2pp**. Under readings B and C it decelerates 0.5-1.6pp. **The sign flips on a $115M move in the 3Q26 GBV estimate.** Never write "ex-FX accelerates" without naming the reading and the GBV.
- **Gates:** G1 fails (raw unearned 1.171/1.168; funds 1.691/0.985). G2 passes. G4 fails both windows. The drift rule is dead.
- FY27 **booking-date FX is a flat-spot carry of zero** — an assumption, not a measurement, and the largest unmodelled FY27 term.
- **Declared 4Q26 nights bucket probabilities (0.55 "low double digit") are above what the n−3 delta estimator supports (0.30-0.35).** Both published; labelled judgement.

---

## 9. Next actions — priority order, owners by skill, irreversible clocks

### Today / tomorrow — irreversible clocks (these cannot be recovered later)

| # | action | owner | clock |
|---|---|---|---|
| 1 | **Start the daily Inside Airbnb capture** on the identical 120-market list. HEAD-poll `data.insideairbnb.com` daily; download on first sight; **fetch `reviews.csv.gz` and `calendar.csv.gz`, not only `listings.csv.gz`** — that omission is why M4's vintage stack does not exist. | **P2 (data)** | **A missed dump is unrecoverable. 28 of 73 historical CDN probes are already dead.** |
| 2 | **Register consensus vintages now.** Pull and timestamp Zacks, Alpha Vantage/36-analyst and S&P Global for 3Q26, 4Q26, FY26, FY27. Re-pull 2-3 Nov when Zacks publishes nights/ADR/GBV consensus. | **P4 (market data)** | Vendors overwrite. The trade flips on which vendor we cite. |
| 3 | **Diarise the two fee deadlines** (15 Sep ex-EEA, 13 Oct EEA+CH) and capture listed-price panels **14/16 Sep** and **12/14 Oct** for the dual-basis exhibit (col 47 `price` vs col 51 `price_quote_price_per_night`). | **P2 (data)** | **14/16 Sep is in 3-5 days.** The only genuinely unowned exhibit in the deck. |
| 4 | **Freeze `spec_id = ABNB-INT-v1`** with the §4.3 card skeleton before any further model is run. | **W (writing/exhibits)** | Before 2 Oct; ideally before the 14 Sep build week. |

### This week — the must-fixes that change published numbers

| # | action | owner |
|---|---|---|
| 5 | Reconcile **GBV_3Q26 $26,300 vs $26,549.8** and restate every 4Q26 probability (fatal #2). | **P1 (core engine)** |
| 6 | Rebuild the **FY27 decomposition** multiplicatively; separate the four assumed lines; delete the timing identity (fatal #1). | **P1 + X (model plumbing)** |
| 7 | Reconcile the **three take-rate numbers** and impose GBV = nights × ADR on the live block; re-run the one pre-registered probability (fatal #3). | **P3/R (FX + take rate)** |
| 8 | Resolve the **live FX tension**: our +1.2pp vs management's ~+3.0pp (fatal #4). Decide whether we publish the architect's Φ reading as the live number. | **P3/R** |
| 9 | **Re-run `harness/score.py`** so the 72 missing groups are scored; relabel empty-ratio rows as "no baseline exists". | **X** |
| 10 | Rule on the **fiat de-gross-up equation** (dimensional error, both forms implemented). | **P3/R** |
| 11 | **Refresh FRED FX** past 28 Aug and re-run fx-lag so the "as of 11 Sep" labels are true. | **P2** |
| 12 | Write the memo around **the guide and the composition**, not a level call. Gate G4's own failure rule mandates it. | **W** |

---

## 10. Where everything lives, and how to re-run

### Folder map (all under the repo root `.../Citadel - ABNB/Citadel-ABNB`)

| what | path |
|---|---|
| Code, one folder per package | `analysis/src/forecast_methods/{harness,L0,kernel_lambda,fx_lag,guidance_policy,fee_takerate,l1_reconciliation,calibration_rail,tracker_backlog,optimal_mix,red_team}/` |
| Data outputs, one folder per package | `data/processed/forecast_methods/<package>/` |
| Registered forecast objects (57 files) | `data/processed/forecast_methods/registry/<package>__<object>.csv` |
| Scoreboard CSV | `data/processed/forecast_methods/harness/scoreboard.csv` |
| Backtest notes, one per package | `docs/revenue-forecast-strategy/05_backtests/<package>.md` |
| Verification notes (rounds 1 and 2) | `docs/revenue-forecast-strategy/05_backtests/VERIFY_<package>_r{1,2}.md` |
| Scoreboard / mix / red team / decisions | `docs/revenue-forecast-strategy/05_backtests/{SCOREBOARD,OPTIMAL_MIX,RED_TEAM,00_IMPLEMENTATION_DECISIONS}.md` |
| The plan and the binding critiques | `docs/revenue-forecast-strategy/04_synthesis/`, `03_critiques/` |
| Runbook | `docs/revenue-forecast-strategy/00_OVERNIGHT_RUNBOOK.md` |
| This report | `docs/revenue-forecast-strategy/07_MORNING_REPORT.md` |

### Re-run, in order, from the repo root

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
PY=/Users/theomachado/.venvs/citadel-abnb/bin/python

# 0. spine and harness (frozen — do not edit these files)
$PY analysis/src/forecast_methods/L0/run.py
$PY analysis/src/forecast_methods/harness/run.py
$PY -m pytest analysis/src/forecast_methods/harness/tests -q

# 1. the seven build packages (independent; any order)
$PY analysis/src/forecast_methods/kernel_lambda/run.py
$PY analysis/src/forecast_methods/fx_lag/run.py            # ~25s, deterministic
$PY analysis/src/forecast_methods/guidance_policy/run.py
$PY analysis/src/forecast_methods/fee_takerate/run.py
$PY analysis/src/forecast_methods/l1_reconciliation/run.py # ~150s
$PY analysis/src/forecast_methods/calibration_rail/run.py
$PY analysis/src/forecast_methods/tracker_backlog/run.py

# 2. score everything, then combine, then attack
$PY analysis/src/forecast_methods/harness/score.py
$PY analysis/src/forecast_methods/optimal_mix/run.py
$PY analysis/src/forecast_methods/red_team/run.py
```

All eleven exit 0. Every script resolves its paths relative to its own file, so they run from anywhere. Re-running `score.py` after `optimal_mix` is **required** — that is must-fix #5.

### Open harness change requests (worked around locally; the harness was never edited)

- **HCR-1:** no LIVE window past 2026Q3 and no annual target slot for FY27 → fx-lag parks 5 forward rows and l1 parks 5 FY27 quarters in unregistered files; two packages needed `strict_windows=False`.
- **HCR-2:** `guide_date` dtype.
- **HCR-3:** `score.py` `GROUP_KEYS` lacks `spec_id` → tracker-backlog's eight specs pool into one series.
- **HCR-4:** `baselines.py` `BASELINE_SPECS` omits `nights_yoy` and has **no baseline at all for `take_rate_pct`** → NaN ratios that read as failures.
- **HCR-5:** the metric classifier treats `take_rate_pct` as growth-like by name → seasonal naive returns 0.0 and calibration-rail ref rows compound a growth rate onto a level. Worth a factor of 4.2 in RMSE.
